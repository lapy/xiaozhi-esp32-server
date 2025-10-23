import time
import wave
import os
import sys
import io
from config.logger import setup_logging
from typing import Optional, Tuple, List
from core.providers.asr.dto.dto import InterfaceType
from core.providers.asr.base import ASRProviderBase

import numpy as np
import sherpa_onnx

from modelscope.hub.file_download import model_file_download

TAG = __name__
logger = setup_logging()


# Capture standard output
class CaptureOutput:
    def __enter__(self):
        self._output = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._output

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._original_stdout
        self.output = self._output.getvalue()
        self._output.close()

        # Output captured content through logger
        if self.output:
            logger.bind(tag=TAG).info(self.output.strip())


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        super().__init__()
        self.interface_type = InterfaceType.LOCAL
        self.model_dir = config.get("model_dir")
        self.output_dir = config.get("output_dir")
        self.model_type = config.get("model_type", "sense_voice")  # Supports paraformer
        self.delete_audio_file = delete_audio_file

        logger.debug(
            f"Sherpa ONNX ASR parameters initialized: model_dir={self.model_dir}, output_dir={self.output_dir}, model_type={self.model_type}, delete_audio_file={self.delete_audio_file}"
        )

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize model file paths
        model_files = {
            "model.int8.onnx": os.path.join(self.model_dir, "model.int8.onnx"),
            "tokens.txt": os.path.join(self.model_dir, "tokens.txt"),
        }

        # Download and check model files
        try:
            for file_name, file_path in model_files.items():
                if not os.path.isfile(file_path):
                    logger.bind(tag=TAG).info(f"Downloading model file: {file_name}")
                    model_file_download(
                        model_id="pengzhendong/sherpa-onnx-sense-voice-zh-en-ja-ko-yue",
                        file_path=file_name,
                        local_dir=self.model_dir,
                    )

                    if not os.path.isfile(file_path):
                        raise FileNotFoundError(f"Model file download failed: {file_path}")

            self.model_path = model_files["model.int8.onnx"]
            self.tokens_path = model_files["tokens.txt"]

        except Exception as e:
            logger.bind(tag=TAG).error(f"Model file processing failed: {str(e)}")
            raise

        with CaptureOutput():
            if self.model_type == "paraformer":
                self.model = sherpa_onnx.OfflineRecognizer.from_paraformer(
                    paraformer=self.model_path,
                    tokens=self.tokens_path,
                    num_threads=2,
                    sample_rate=16000,
                    feature_dim=80,
                    decoding_method="greedy_search",
                    debug=False,
                )
            else:  # sense_voice
                self.model = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                    model=self.model_path,
                    tokens=self.tokens_path,
                    num_threads=2,
                    sample_rate=16000,
                    feature_dim=80,
                    decoding_method="greedy_search",
                    debug=False,
                    use_itn=True,
                )

    def read_wave(self, wave_filename: str) -> Tuple[np.ndarray, int]:
        """
        Args:
        wave_filename:
            Path to a wave file. It should be single channel and each sample should
            be 16-bit. Its sample rate does not need to be 16kHz.
        Returns:
        Return a tuple containing:
        - A 1-D array of dtype np.float32 containing the samples, which are
        normalized to the range [-1, 1].
        - sample rate of the wave file
        """

        with wave.open(wave_filename) as f:
            assert f.getnchannels() == 1, f.getnchannels()
            assert f.getsampwidth() == 2, f.getsampwidth()  # it is in bytes
            num_samples = f.getnframes()
            samples = f.readframes(num_samples)
            samples_int16 = np.frombuffer(samples, dtype=np.int16)
            samples_float32 = samples_int16.astype(np.float32)

            samples_float32 = samples_float32 / 32768
            return samples_float32, f.getframerate()

    async def speech_to_text(
        self, opus_data: List[bytes], session_id: str, audio_format="opus"
    ) -> Tuple[Optional[str], Optional[str]]:
        """Main speech-to-text processing logic"""
        logger.bind(tag=TAG).debug(f"Sending Sherpa ONNX ASR request with session_id: {session_id}, audio_format: {audio_format}")
        
        file_path = None
        try:
            # Save audio file
            start_time = time.time()
            if audio_format == "pcm":
                pcm_data = opus_data
                logger.bind(tag=TAG).debug(f"Using PCM data directly, length: {len(opus_data)}")
            else:
                logger.bind(tag=TAG).debug(f"Decoding Opus data to PCM")
                pcm_data = self.decode_opus(opus_data)
                logger.bind(tag=TAG).debug(f"Decoded PCM data length: {len(pcm_data) if pcm_data else 0}")
                
            file_path = self.save_audio_to_file(pcm_data, session_id)
            logger.bind(tag=TAG).debug(
                f"Audio file save time: {time.time() - start_time:.3f}s | Path: {file_path}"
            )

            # Speech recognition
            start_time = time.time()
            logger.bind(tag=TAG).debug(f"Starting Sherpa ONNX speech recognition with model_type: {self.model_type}")
            
            s = self.model.create_stream()
            samples, sample_rate = self.read_wave(file_path)
            logger.bind(tag=TAG).debug(f"Read wave file: {len(samples)} samples at {sample_rate}Hz")
            
            s.accept_waveform(sample_rate, samples)
            logger.bind(tag=TAG).debug(f"Accepted waveform data")
            
            self.model.decode_stream(s)
            logger.bind(tag=TAG).debug(f"Decoded stream")
            
            text = s.result.text
            logger.bind(tag=TAG).debug(
                f"Speech recognition time: {time.time() - start_time:.3f}s | Result: {text}"
            )

            return text, file_path

        except Exception as e:
            logger.bind(tag=TAG).error(f"Speech recognition failed: {e}", exc_info=True)
            return "", file_path
        finally:
            # File cleanup logic
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"Deleted temporary audio file: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"File deletion failed: {file_path} | Error: {e}")

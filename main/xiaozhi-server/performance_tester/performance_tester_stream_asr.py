import asyncio
import time
import json
import uuid
import os
import websockets
import gzip
import random
from urllib import parse
from tabulate import tabulate
from config.settings import load_config
import tempfile
import wave
description = "Streaming ASR first word latency test"
try:
    import dashscope
except ImportError:
    dashscope = None

class BaseASRTester:
    def __init__(self, config_key: str):
        self.config = load_config()
        self.config_key = config_key
        self.asr_config = self.config.get("ASR", {}).get(config_key, {})
        self.test_audio_files = self._load_test_audio_files()
        self.results = []

    def _load_test_audio_files(self):
        audio_root = os.path.join(os.getcwd(), "config", "assets")
        test_files = []
        if os.path.exists(audio_root):
            for file_name in os.listdir(audio_root):
                if file_name.endswith(('.wav', '.pcm')):
                    file_path = os.path.join(audio_root, file_name)
                    with open(file_path, 'rb') as f:
                        test_files.append({
                            'data': f.read(),
                            'path': file_path,
                            'name': file_name
                        })
        return test_files

    async def test(self, test_count=5):
        raise NotImplementedError

    def _calculate_result(self, service_name, latencies, test_count):
        valid_latencies = [l for l in latencies if l > 0]
        if valid_latencies:
            avg_latency = sum(valid_latencies) / len(valid_latencies)
            status = f"Success ({len(valid_latencies)}/{test_count} valid)"
        else:
            avg_latency = 0
            status = "Failed: All tests failed"
        return {"name": service_name, "latency": avg_latency, "status": status}






class ASRPerformanceSuite:
    def __init__(self):
        self.testers = []
        self.results = []

    def register_tester(self, tester_class):
        try:
            tester = tester_class()
            self.testers.append(tester)
            print(f"Registered tester: {tester.config_key}")
        except Exception as e:
            name_map = {}
            name = name_map.get(tester_class.__name__, tester_class.__name__)
            print(f"Skipping {name}: {str(e)}")

    def _print_results(self, test_count):
        if not self.results:
            print("No valid ASR test results")
            return

        print(f"\n{'='*60}")
        print("Streaming ASR first word response time test results")
        print(f"{'='*60}")
        print(f"Test count: Each ASR service tested {test_count} times")

        success_results = sorted(
            [r for r in self.results if "Success" in r["status"]],
            key=lambda x: x["latency"]
        )
        failed_results = [r for r in self.results if "Success" not in r["status"]]

        table_data = [
            [r["name"], f"{r['latency']:.3f}s" if r['latency'] > 0 else "N/A", r["status"]]
            for r in success_results + failed_results
        ]

        print(tabulate(table_data, headers=["ASR Service", "First Word Latency", "Status"], tablefmt="grid"))
        print("\nTest description:")
        print("- Measure time from sending request to receiving first valid recognized text")
        print("- Timeout control: DashScope default timeout")
        print("- Sorting rule: Successful ones sorted by latency ascending, failed ones at the end")

    async def run(self, test_count=5):
        print(f"Starting streaming ASR first word response time test...")
        print(f"Each ASR service test count: {test_count} times\n")

        self.results = []
        for tester in self.testers:
            print(f"\n--- Testing {tester.config_key} ---")
            result = await tester.test(test_count)
            self.results.append(result)

        self._print_results(test_count)


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Streaming ASR first word response time test tool")
    parser.add_argument("--count", type=int, default=5, help="Test count")
    args = parser.parse_args()

    suite = ASRPerformanceSuite()
    # No ASR testers registered - ASR services have been updated

    await suite.run(args.count)


if __name__ == "__main__":
    asyncio.run(main())
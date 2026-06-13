#!/usr/bin/env bash

set -euo pipefail

readonly DEFAULT_VOSK_MODEL_NAME="vosk-model-en-us-0.22"
readonly DEFAULT_VOSK_MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
readonly WHISPER_MODELS=(
  "tiny.en"
  "tiny"
  "base.en"
  "base"
  "small.en"
  "small"
  "medium.en"
  "medium"
  "large-v1"
  "large-v2"
  "large-v3"
)

BASE_PATH="${XIAOZHI_BASE_PATH:-$PWD}"
DOWNLOAD_VOSK=1
DOWNLOAD_ALL_WHISPER=0
declare -a REQUESTED_WHISPER_MODELS=()

usage() {
  cat <<'EOF'
Usage: model-setup.sh [options]

Create Xiaozhi data/model directories under a configurable base path and
download local ASR models needed by the westernized stack.

Options:
  --base-path PATH         Base directory to prepare. Defaults to $PWD.
                           You can also set XIAOZHI_BASE_PATH.
  --skip-vosk              Skip downloading the default Vosk model.
  --download-whisper NAME  Pre-download a Whisper model into models/whisper.
                           Repeat this flag to download multiple models.
  --download-whisper-all   Pre-download every supported Whisper model.
  -h, --help               Show this help message.

Examples:
  ./model-setup.sh --base-path /srv/xiaozhi
  ./model-setup.sh --base-path /srv/xiaozhi --download-whisper base
  ./model-setup.sh --base-path /srv/xiaozhi --skip-vosk --download-whisper-all
EOF
}

log() {
  printf '[INFO] %s\n' "$*"
}

warn() {
  printf '[WARN] %s\n' "$*" >&2
}

die() {
  printf '[ERROR] %s\n' "$*" >&2
  exit 1
}

contains_whisper_model() {
  local candidate=$1
  local model
  for model in "${WHISPER_MODELS[@]}"; do
    if [[ "$model" == "$candidate" ]]; then
      return 0
    fi
  done
  return 1
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --base-path)
        shift
        [[ $# -gt 0 ]] || die "--base-path requires a value"
        BASE_PATH=$1
        ;;
      --skip-vosk)
        DOWNLOAD_VOSK=0
        ;;
      --download-whisper)
        shift
        [[ $# -gt 0 ]] || die "--download-whisper requires a model name"
        contains_whisper_model "$1" || die "Unsupported Whisper model: $1"
        REQUESTED_WHISPER_MODELS+=("$1")
        ;;
      --download-whisper-all)
        DOWNLOAD_ALL_WHISPER=1
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "Unknown option: $1"
        ;;
    esac
    shift
  done
}

ensure_base_path() {
  mkdir -p "$BASE_PATH"
  BASE_PATH="$(cd "$BASE_PATH" && pwd -P)"

  DATA_DIR="$BASE_PATH/data"
  MODELS_DIR="$BASE_PATH/models"
  VOSK_DIR="$MODELS_DIR/vosk"
  WHISPER_DIR="$MODELS_DIR/whisper"
}

create_directories() {
  mkdir -p "$DATA_DIR" "$VOSK_DIR" "$WHISPER_DIR"
  log "Prepared directories under $BASE_PATH"
}

extract_zip() {
  local archive_path=$1
  local destination_dir=$2

  if command -v python3 >/dev/null 2>&1; then
    python3 - "$archive_path" "$destination_dir" <<'PY'
import pathlib
import sys
import zipfile

archive = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])

with zipfile.ZipFile(archive) as zip_file:
    zip_file.extractall(destination)
PY
    return
  fi

  if command -v unzip >/dev/null 2>&1; then
    unzip -q "$archive_path" -d "$destination_dir"
    return
  fi

  die "Need either python3 or unzip to extract $archive_path"
}

download_vosk_model() {
  local model_path="$VOSK_DIR/$DEFAULT_VOSK_MODEL_NAME"
  local archive_path="$VOSK_DIR/$DEFAULT_VOSK_MODEL_NAME.zip"

  if [[ $DOWNLOAD_VOSK -eq 0 ]]; then
    log "Skipping Vosk download"
    return
  fi

  if [[ -f "$model_path/am/final.mdl" ]]; then
    log "Vosk model already present at $model_path"
    return
  fi

  command -v curl >/dev/null 2>&1 || die "curl is required to download the Vosk model"

  log "Downloading Vosk model to $VOSK_DIR"
  curl -fL --progress-bar "$DEFAULT_VOSK_MODEL_URL" -o "$archive_path"
  extract_zip "$archive_path" "$VOSK_DIR"
  rm -f "$archive_path"

  [[ -f "$model_path/am/final.mdl" ]] || die "Vosk model download did not produce $model_path/am/final.mdl"
  log "Vosk model ready at $model_path"
}

dedupe_requested_whisper_models() {
  local model
  declare -A seen=()
  declare -a deduped=()

  if [[ $DOWNLOAD_ALL_WHISPER -eq 1 ]]; then
    REQUESTED_WHISPER_MODELS=("${WHISPER_MODELS[@]}")
    return
  fi

  for model in "${REQUESTED_WHISPER_MODELS[@]}"; do
    if [[ -z "${seen[$model]:-}" ]]; then
      seen["$model"]=1
      deduped+=("$model")
    fi
  done

  REQUESTED_WHISPER_MODELS=("${deduped[@]}")
}

download_whisper_model() {
  local model_name=$1
  local model_path="$WHISPER_DIR/$model_name.pt"

  if [[ -f "$model_path" ]]; then
    log "Whisper model already present at $model_path"
    return
  fi

  command -v python3 >/dev/null 2>&1 || die "python3 is required to pre-download Whisper models"

  log "Downloading Whisper model $model_name into $WHISPER_DIR"
  python3 - "$model_name" "$WHISPER_DIR" <<'PY'
import sys

model_name = sys.argv[1]
download_root = sys.argv[2]

try:
    import whisper
except Exception as exc:
    raise SystemExit(
        "openai-whisper must be installed before pre-downloading Whisper models: "
        f"{exc}"
    )

whisper.load_model(model_name, device="cpu", download_root=download_root)
PY

  [[ -f "$model_path" ]] || warn "Whisper reported success but $model_path was not found"
}

maybe_download_whisper_models() {
  dedupe_requested_whisper_models

  if [[ ${#REQUESTED_WHISPER_MODELS[@]} -eq 0 ]]; then
    log "Whisper directory prepared at $WHISPER_DIR"
    log "Whisper models will still auto-download on first use if you skip pre-download here"
    return
  fi

  local model
  for model in "${REQUESTED_WHISPER_MODELS[@]}"; do
    download_whisper_model "$model"
  done
}

print_summary() {
  cat <<EOF

Preparation complete.

Base path:     $BASE_PATH
Data dir:      $DATA_DIR
Models dir:    $MODELS_DIR
Vosk dir:      $VOSK_DIR
Whisper dir:   $WHISPER_DIR
EOF
}

main() {
  parse_args "$@"
  ensure_base_path
  create_directories
  download_vosk_model
  maybe_download_whisper_models
  print_summary
}

main "$@"

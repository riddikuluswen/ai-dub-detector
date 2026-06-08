#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <media-file>" >&2
  exit 2
fi

PROJECT_DIR="/Users/eric/个人/AI配音识别器"
exec "$PROJECT_DIR/.venv/bin/ai-dub-detector" analyze "$1"

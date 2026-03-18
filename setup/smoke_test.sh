#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${CONDA_ENV_NAME:-agentic-sandbox}"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda is required but was not found in PATH." >&2
  exit 1
fi

eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

python main.py status
python main.py prototype start --name SmokeTest --age 8
python main.py prototype turn cat

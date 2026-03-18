#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${CONDA_ENV_NAME:-agentic-sandbox}"

cd "$ROOT_DIR"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda is required but was not found in PATH." >&2
  exit 1
fi

echo "Creating or updating Conda environment: $ENV_NAME"
if conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  conda install --name "$ENV_NAME" --channel conda-forge --override-channels --yes \
    python=3.11 pip
else
  conda create --name "$ENV_NAME" --channel conda-forge --override-channels --yes \
    python=3.11 pip
fi

echo
echo "Environment ready."
echo "Activate it with:"
echo "  conda activate $ENV_NAME"

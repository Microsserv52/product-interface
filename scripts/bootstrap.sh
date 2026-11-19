#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if docker info >/dev/null 2>&1; then
  echo "Validating the Product contract in a container..."
  docker build --tag product-interface-validator:local .
  docker run --rm product-interface-validator:local
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Docker or uv is required. Install Docker, or install uv from https://docs.astral.sh/uv/." >&2
  exit 1
fi

echo "Docker is unavailable; validating with local uv."
uv sync --frozen
uv run python scripts/validate.py

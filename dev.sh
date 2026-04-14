#!/usr/bin/env bash
# Fast dev: open-webui in Docker (built once), API locally with hot-reload.
# First run builds open-webui (~10 min). After that — instant startup.
set -euo pipefail

# Start open-webui against local API (--no-deps skips api container)
echo "→ Starting open-webui in Docker..."
OPENAI_API_BASE_URL=http://host.docker.internal:8000/v1 \
CT_API_BASE=http://host.docker.internal:8000 \
docker compose up -d --no-deps open-webui
echo "→ open-webui: http://localhost:${OPEN_WEBUI_PORT:-3000}"

# Load .env if present
[ -f .env ] && set -a && source .env && set +a

# Run API locally with hot-reload
echo "→ Starting API on :8000 (Ctrl+C to stop)..."
echo "→ Figma plugin UI: http://localhost:8000/figma"
exec uv run uvicorn certified_turtles.main:app \
  --reload --host 0.0.0.0 --port 8000

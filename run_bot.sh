#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt

# Stop old bot processes to prevent TelegramConflictError.
pkill -f "python -m app.bot" >/dev/null 2>&1 || true
pkill -f ".venv/bin/python -m app.bot" >/dev/null 2>&1 || true

echo "Starting Flatly bot from .venv..."
exec .venv/bin/python -m app.bot

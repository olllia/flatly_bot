#!/usr/bin/env bash
set -euo pipefail

pkill -f "python -m app.bot" >/dev/null 2>&1 || true
pkill -f ".venv/bin/python -m app.bot" >/dev/null 2>&1 || true

echo "Flatly bot processes stopped."

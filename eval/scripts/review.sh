#!/bin/sh
# Start the human review app for this run. Answers save to eval/human/responses.json.
cd "$(dirname "$0")/.." || exit 1
exec python3 review-app/server.py --tasks human/tasks.json --responses human/responses.json --port "${PORT:-8765}"

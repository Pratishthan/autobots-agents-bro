#!/usr/bin/env bash
# ABOUTME: Launch script for autobots-agents-bro.
# ABOUTME: Starts Chainlit on port 1337 via the agents-bro custom UI entry point.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}/.."

# Determine chainlit executable
# In workspace: use ../.venv/bin/chainlit
# In Docker: use system chainlit
if [ -f "../.venv/bin/chainlit" ]; then
    CHAINLIT_CMD="../.venv/bin/chainlit"
else
    CHAINLIT_CMD="chainlit"
fi

# Run Chainlit application
exec "${CHAINLIT_CMD}" run src/autobots_agents_bro/usecase_ui.py --host 0.0.0.0 --port 1337

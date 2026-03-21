#!/bin/bash
set -euo pipefail

# Only run in remote (web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install Twingate if not already installed
if ! command -v twingate &>/dev/null; then
  echo "Installing Twingate..."
  curl -s https://binaries.twingate.com/client/linux/install.sh | bash
fi

# Connect to Twingate if not already connected
if ! twingate status 2>/dev/null | grep -q "online"; then
  echo "Connecting to Twingate..."
  twingate setup --headless \
    --service-url "beardrem.twingate.com" \
    --access-token "${TWINGATE_TOKEN}"
  twingate start --headless
fi

echo "Twingate ready."

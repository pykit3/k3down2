#!/bin/bash
set -e

# This script runs under `sudo bash`, which drops env vars.
# Only the current matrix job's Python has playwright installed,
# so probe each one to find it.
for py in /opt/hostedtoolcache/Python/*/x64/bin/python3; do
    if "$py" -c "import playwright" 2>/dev/null; then
        export PLAYWRIGHT_BROWSERS_PATH=/home/runner/.cache/ms-playwright
        "$py" -m playwright install --with-deps chromium
        chmod -R a+rx /home/runner/.cache/ms-playwright
        exit 0
    fi
done

echo "Error: no Python with playwright found"
exit 1

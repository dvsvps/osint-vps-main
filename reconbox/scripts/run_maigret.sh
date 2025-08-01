#!/bin/bash
# run_maigret.sh  —  Wrapper to run Maigret inside its virtual environment
# Usage: ./scripts/run_maigret.sh <username>

set -e

# 1. Input check
if [ -z "$1" ]; then
  echo "Usage: $(basename "$0") <username>"
  exit 1
fi
USERNAME="$1"

# 2. Paths
BASE_DIR="/opt/osint-vps/reconbox"
VENV="$BASE_DIR/tools/username-intel/maigret/venv"
OUTPUT_DIR="$BASE_DIR/results/json"
OUTFILE="$OUTPUT_DIR/maigret_${USERNAME}.json"

# 3. Ensure output dir
mkdir -p "$OUTPUT_DIR"

# 4. Run Maigret
echo "[*] Running Maigret for user: $USERNAME"
source "$VENV/bin/activate"

# Maigret v0.5.0a1 accepts -J {simple|ndjson} plus --folderoutput
maigret "$USERNAME" \
  -J simple \
  --folderoutput "$OUTPUT_DIR" \
  --no-progressbar

deactivate

REPORT_PATH="$OUTPUT_DIR/report_${USERNAME}_simple.json"
if [ -f "$REPORT_PATH" ]; then
  echo "[+] JSON saved to: $REPORT_PATH"
else
  echo "[!] Expected JSON file not found. Check Maigret output."
fi


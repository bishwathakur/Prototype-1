#!/bin/bash
# Start detector
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/services/disruption-detector"

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 detector.py

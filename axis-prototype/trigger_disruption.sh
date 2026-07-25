#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/services/event-producer"

echo "Triggering mock flight cancellation (AX100)..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
python3 producer.py

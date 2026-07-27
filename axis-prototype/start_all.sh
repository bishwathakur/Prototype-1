#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo " Starting AXIS Travel Disruption Prototype"
echo "=================================================="

echo "[1/5] Starting Docker infrastructure (Kafka, Postgres)..."
docker compose up -d

echo "[2/5] Starting Backend Agent..."
cd services/backend-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

echo "[3/5] Starting Eligibility Gate..."
cd services/eligibility-gate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
python3 gate.py > gate.log 2>&1 &
GATE_PID=$!
cd ../..

echo "[4/5] Starting Disruption Detector..."
cd services/disruption-detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
python3 detector.py > detector.log 2>&1 &
DETECTOR_PID=$!
cd ../..

echo "[5/5] Starting React Frontend..."
cd frontend
npm install --silent
if [ -n "$CODESPACE_NAME" ]; then
  export VITE_API_URL="https://${CODESPACE_NAME}-8000.app.github.dev"
  echo "Codespaces detected. Setting VITE_API_URL=$VITE_API_URL"
fi
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================================="
echo " All services are running in the background!"
echo " React UI:         http://localhost:5173"
echo ""
echo " To trigger a disruption, run:"
echo "    bash trigger_disruption.sh"
echo "=================================================="

trap "echo -e '\nShutting down...'; kill $BACKEND_PID $DETECTOR_PID $GATE_PID $FRONTEND_PID; docker compose down; exit" INT
wait
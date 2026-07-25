#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "=================================================="
echo " Starting AXIS Travel Disruption Prototype"
echo "=================================================="

echo "[1/4] Starting Docker infrastructure (Kafka, Postgres)..."
docker compose up -d

echo "[2/4] Starting Backend Agent..."
cd services/backend-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

echo "[3/4] Starting Disruption Detector..."
cd services/disruption-detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
python3 detector.py > detector.log 2>&1 &
DETECTOR_PID=$!
cd ../..

echo "[4/4] Starting React Frontend..."
cd frontend
npm install --silent
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================================="
echo "✅ All services are running in the background!"
echo "React UI is available at: http://localhost:5173"
echo "Logs are being saved to backend.log, detector.log, and frontend.log"
echo ""
echo "👉 To trigger a disruption, run:"
echo "   bash trigger_disruption.sh"
echo ""
echo "Press Ctrl+C to stop all services and shut down."
echo "=================================================="

# Keep script running and clean up on exit
trap "echo -e '\nShutting down...'; kill $BACKEND_PID $DETECTOR_PID $FRONTEND_PID; docker compose down; exit" INT
wait

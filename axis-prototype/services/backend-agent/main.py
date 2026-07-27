from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from confluent_kafka import Consumer
import json
import threading
from database import init_db, get_itinerary, update_itinerary_status
from agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def kafka_consumer_task():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'backend-agent-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['disruption-confirmed'])

    print("[BACKEND] Listening to 'disruption-confirmed' topic...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        data = json.loads(msg.value().decode('utf-8'))
        flight_no = data.get('flight_number')
        cm_id = data.get('card_member_id')

        print(f"[BACKEND] Received eligible disruption for {flight_no}")

        update_itinerary_status(flight_no, 'CANCELLED')

        run_agent(flight_no, cm_id)

def kafka_ineligible_task():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'backend-ineligible-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['disruption-ineligible'])

    print("[BACKEND] Listening to 'disruption-ineligible' topic...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        data = json.loads(msg.value().decode('utf-8'))
        flight_no = data.get('flight_number')
        reason = data.get('ineligible_reason', 'Unknown')

        print(f"[BACKEND] Ineligible disruption for {flight_no}: {reason}")
        update_itinerary_status(flight_no, 'INELIGIBLE', ineligible_reason=reason)

def run_gate():
    import subprocess
    import sys
    gate_path = "services/eligibility-gate/gate.py"
    subprocess.Popen([sys.executable, gate_path],
                     stdout=open("gate.log", "w"),
                     stderr=subprocess.STDOUT)

@app.on_event("startup")
def startup_event():
    init_db()
    t = threading.Thread(target=kafka_consumer_task, daemon=True)
    t.start()
    t2 = threading.Thread(target=kafka_ineligible_task, daemon=True)
    t2.start()
    t3 = threading.Thread(target=run_gate, daemon=True)
    t3.start()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/itinerary/{cm_id}")
def get_itin(cm_id: str):
    return get_itinerary(cm_id)

@app.post("/api/trigger-disruption")
def trigger_disruption():
    import subprocess, sys
    subprocess.Popen([sys.executable, "services/event-producer/producer.py"])
    return {"status": "triggered"}
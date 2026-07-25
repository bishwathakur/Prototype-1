from fastapi import FastAPI, BackgroundTasks
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
        
        print(f"[BACKEND] Received disruption for {flight_no}")
        
        # 2. Update DB: set status='CANCELLED'
        update_itinerary_status(flight_no, 'CANCELLED')
        
        # 3. Trigger Agent
        run_agent(flight_no, cm_id)

@app.on_event("startup")
def startup_event():
    init_db()
    # Start kafka consumer in background thread
    t = threading.Thread(target=kafka_consumer_task, daemon=True)
    t.start()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/itinerary/{cm_id}")
def get_itin(cm_id: str):
    return get_itinerary(cm_id)

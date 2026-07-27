from confluent_kafka import Producer
import json
import time

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def run_producer():
    conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(conf)
    
    print("[PRODUCER] Waiting 10 seconds before emitting event...")
    time.sleep(10)
    
payload = {
    "flight_number": "AX100",
    "card_member_id": "CM-123",
    "status": "CANCELLED",
    "cause": "WEATHER",
    "delay_minutes": 480,
    "timestamp": "2026-07-26T10:00:00Z"
}
    
    print(f"[PRODUCER] Emitting event: {payload}")
    producer.produce(
        'flight-status-raw',
        value=json.dumps(payload).encode('utf-8'),
        callback=delivery_report
    )
    
    producer.flush()
    print("[PRODUCER] Done.")

if __name__ == '__main__':
    run_producer()

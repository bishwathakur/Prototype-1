from confluent_kafka import Consumer, Producer
import json

CAUSE_MAP = {
    "WEATHER": "WEATHER",
    "CARRIER_EQUIPMENT": "CARRIER_EQUIPMENT",
    "SECURITY": "SECURITY",
    "DOCUMENTATION": "DOCUMENTATION"
}

def classify_cause(raw: dict) -> str:
    cause = raw.get("cause", "OTHER")
    return CAUSE_MAP.get(cause, "OTHER")

def run_detector():
    conf_consumer = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'disruption-detector-group',
        'auto.offset.reset': 'earliest'
    }
    conf_producer = {
        'bootstrap.servers': 'localhost:9092'
    }

    consumer = Consumer(conf_consumer)
    producer = Producer(conf_producer)

    consumer.subscribe(['flight-status-raw'])
    print("[DETECTOR] Listening for flight status events...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        try:
            data = json.loads(msg.value().decode('utf-8'))
            flight_no = data.get('flight_number')
            status = data.get('status')
            delay = data.get('delay_minutes', 0)

            if status == "CANCELLED" or delay > 90:
                cause = classify_cause(data)
                data['cause'] = cause
                print(f"[DETECTOR] Disruption found for flight {flight_no}, cause={cause}")
                producer.produce(
                    'disruption-detected',
                    value=json.dumps(data).encode('utf-8'),
                    callback=lambda err, msg: None
                )
                producer.flush()
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == '__main__':
    run_detector()
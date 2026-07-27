from confluent_kafka import Consumer, Producer
import json
import psycopg2

COVERED_CAUSES = {"WEATHER", "CARRIER_EQUIPMENT", "HIJACKING", "DOCUMENTATION"}
POLICY_MIN_DELAY = 360
POLICY_MAX_CLAIMS = 2

DB_CONFIG = {
    'dbname': 'axis_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def claims_in_last_12_months(card_member_id: str) -> int:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM eligibility_checks
            WHERE card_member_id = %s
              AND eligible = TRUE
              AND checked_at >= NOW() - INTERVAL '12 months'
        """, (card_member_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception:
        return 0

def save_check(flight_no: str, cm_id: str, cause: str, delay: int,
               covered: bool, within_policy: bool, eligible: bool, reason: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO eligibility_checks
            (flight_number, card_member_id, cause, delay_minutes,
             claims_used_12mo, covered, within_policy, eligible, reason, checked_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """, (flight_no, cm_id, cause, delay, 0, covered, within_policy, eligible, reason))
    conn.commit()
    cur.close()
    conn.close()

def run_gate():
    conf_consumer = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'eligibility-gate-group',
        'auto.offset.reset': 'earliest'
    }
    conf_producer = {
        'bootstrap.servers': 'localhost:9092'
    }

    consumer = Consumer(conf_consumer)
    producer = Producer(conf_producer)

    consumer.subscribe(['disruption-detected'])
    print("[GATE] Listening on 'disruption-detected'...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Gate consumer error: {msg.error()}")
            continue

        data = json.loads(msg.value().decode('utf-8'))
        flight_no = data.get('flight_number')
        cm_id = data.get('card_member_id')
        cause = data.get('cause', 'OTHER')
        delay = data.get('delay_minutes', 0)

        # Check 1 — covered cause
        covered = cause in COVERED_CAUSES
        if not covered:
            reason = f"Cause '{cause}' not in covered list"
            print(f"[GATE] INELIGIBLE ({flight_no}): {reason}")
            save_check(flight_no, cm_id, cause, delay, covered, False, False, reason)
            data['ineligible_reason'] = reason
            producer.produce('disruption-ineligible', value=json.dumps(data).encode('utf-8'))
            producer.flush()
            continue

        # Check 2 — within policy
        claims_used = claims_in_last_12_months(cm_id)
        within_policy = delay >= POLICY_MIN_DELAY and claims_used < POLICY_MAX_CLAIMS
        if not within_policy:
            if delay < POLICY_MIN_DELAY:
                reason = f"Delay ({delay}min) below {POLICY_MIN_DELAY}min threshold"
            else:
                reason = f"Claims ({claims_used}) exhausted ({POLICY_MAX_CLAIMS}/12mo)"
            print(f"[GATE] INELIGIBLE ({flight_no}): {reason}")
            save_check(flight_no, cm_id, cause, delay, covered, False, False, reason)
            data['ineligible_reason'] = reason
            producer.produce('disruption-ineligible', value=json.dumps(data).encode('utf-8'))
            producer.flush()
            continue

        # Check 3 — eligible
        reason = "All eligibility checks passed"
        save_check(flight_no, cm_id, cause, delay, covered, True, True, reason)
        print(f"[GATE] ELIGIBLE ({flight_no}): {reason}")
        producer.produce('disruption-confirmed', value=json.dumps(data).encode('utf-8'))
        producer.flush()

if __name__ == '__main__':
    run_gate()
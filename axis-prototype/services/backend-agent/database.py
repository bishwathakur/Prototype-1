import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import datetime

DB_CONFIG = {
    'dbname': 'axis_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS itineraries (
            id UUID PRIMARY KEY,
            card_member_id VARCHAR(50) NOT NULL,
            original_flight VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            new_flight VARCHAR(20),
            ineligible_reason TEXT,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eligibility_checks (
            id SERIAL PRIMARY KEY,
            flight_number VARCHAR(20) NOT NULL,
            card_member_id VARCHAR(50) NOT NULL,
            cause VARCHAR(50) NOT NULL,
            delay_minutes INT NOT NULL DEFAULT 0,
            claims_used_12mo INT NOT NULL DEFAULT 0,
            covered BOOLEAN NOT NULL,
            within_policy BOOLEAN NOT NULL,
            eligible BOOLEAN NOT NULL,
            reason TEXT,
            checked_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)

    cur.execute("SELECT COUNT(*) FROM itineraries WHERE card_member_id = 'CM-123'")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO itineraries (id, card_member_id, original_flight, status, new_flight, ineligible_reason, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), 'CM-123', 'AX100', 'ON_TIME', None, None, datetime.datetime.now()))

    conn.commit()
    cur.close()
    conn.close()

def update_itinerary_status(flight_no, status, ineligible_reason=None):
    conn = get_connection()
    cur = conn.cursor()
    if ineligible_reason:
        cur.execute("""
            UPDATE itineraries
            SET status = %s, ineligible_reason = %s, updated_at = %s
            WHERE original_flight = %s
        """, (status, ineligible_reason, datetime.datetime.now(), flight_no))
    else:
        cur.execute("""
            UPDATE itineraries SET status = %s, updated_at = %s WHERE original_flight = %s
        """, (status, datetime.datetime.now(), flight_no))
    conn.commit()
    cur.close()
    conn.close()

def rebook_itinerary(original_flight, new_flight):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE itineraries SET status = 'REBOOKED', new_flight = %s, updated_at = %s WHERE original_flight = %s
    """, (new_flight, datetime.datetime.now(), original_flight))
    conn.commit()
    cur.close()
    conn.close()

def get_itinerary(cm_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM itineraries WHERE card_member_id = %s", (cm_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return dict(res) if res else None
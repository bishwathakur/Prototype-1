import time
from database import update_itinerary_status, rebook_itinerary

def search_alternative_flights(cancelled_flight: str):
    return [{"flight": "DL200", "price": 400}, {"flight": "UA300", "price": 600}]

def check_policy(price: int):
    return price < 500

def run_agent(flight_no: str, cm_id: str):
    print(f"[AGENT] Eligible disruption confirmed for {flight_no}. Proceeding with rebooking...")
    time.sleep(1)
    alts = search_alternative_flights(flight_no)

    for alt in alts:
        print(f"[AGENT] Checking policy for {alt['flight']} (${alt['price']})")
        if check_policy(alt['price']):
            print(f"[AGENT] Policy passed. Booking {alt['flight']}...")
            time.sleep(1)
            rebook_itinerary(flight_no, alt['flight'])
            print(f"[AGENT] Successfully rebooked {cm_id} onto {alt['flight']}")
            return

    print(f"[AGENT] No flights found within policy.")
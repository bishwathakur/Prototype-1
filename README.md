# AXIS Prototype
Autonomous Travel-Disruption Concierge prototype for CodeStreet 2026.

## Prototype Flow (What happens under the hood?)

When you run the prototype and trigger the disruption, the following event-driven sequence occurs in real-time (under 3 seconds):

```mermaid
sequenceDiagram
    participant P as producer.py
    participant K1 as Kafka (flight-status-raw)
    participant D as detector.py
    participant K2 as Kafka (disruption-confirmed)
    participant B as Backend (main.py)
    participant DB as PostgreSQL
    participant A as Agent (agent.py)
    participant UI as React UI

    Note over UI,B: 1. Steady State (Polling)
    loop Every 2 seconds
        UI->>B: GET /api/itinerary/CM-123
        B->>DB: SELECT * FROM itineraries
        DB-->>B: status="ON_TIME"
        B-->>UI: {status: "ON_TIME"} (UI turns Green)
    end

    Note over P,K1: 2. Disruption Injection
    P->>K1: Publish {"status": "CANCELLED"}
    
    Note over D,K2: 3. Detection
    K1-->>D: Consume raw event
    D->>D: Filter cancelled/delayed
    D->>K2: Publish confirmed disruption

    Note over B,A: 4. Agent Handoff
    K2-->>B: Consume confirmed disruption
    B->>DB: UPDATE status="CANCELLED"
    Note over UI,B: UI Polling returns "CANCELLED" (UI turns Red)
    B->>A: Trigger Rebooking Agent
    
    Note over A,DB: 5. Autonomous Rebooking
    A->>A: Evaluate alternatives
    A->>A: Check policy (price < $500)
    A->>DB: UPDATE status="REBOOKED", new_flight="DL200"

    Note over UI,B: 6. Resolution
    UI->>B: GET /api/itinerary/CM-123
    B-->>UI: {status: "REBOOKED", new_flight: "DL200"} (UI turns Gold)
```

1. **Steady State:** The React Frontend (Vite) continuously polls the FastAPI Backend. The PostgreSQL database shows flight `AX100` as `ON_TIME`. The UI is **Green**.
2. **Disruption Injection:** Running `make trigger` executes `producer.py`. It pushes a mock flight cancellation JSON payload to the Kafka topic `flight-status-raw`.
3. **Detection:** The `detector.py` service consumes the raw stream. It detects `status="CANCELLED"`, filters it, and publishes a confirmed event to the Kafka topic `disruption-confirmed`.
4. **Agent Handoff:** A background Kafka consumer in the FastAPI backend (`main.py`) catches the confirmed disruption. It updates the DB status to `CANCELLED` (changing the UI to **Red**) and instantly hands off to the LangChain mock agent (`agent.py`).
5. **Autonomous Rebooking:** The Agent executes a deterministic tool chain:
   - Evaluates alternative flights (`DL200` at $400, `UA300` at $600).
   - Checks the cardmember's policy rules (limit < $500).
   - Books `DL200`, updating the database itinerary to `REBOOKED`.
6. **Resolution:** The React UI fetches the updated state and transitions to **Gold**, notifying the user of the resolved flight without any manual intervention.

---

## How to Run (Codespaces / Linux / Mac)

The easiest way to run this project is via the provided `Makefile` inside the `axis-prototype` directory.

```bash
cd axis-prototype
```

1. **Start all services:**
   ```bash
   make up
   ```
   *(Wait for Docker, Backend, Detector, and Frontend to boot. The UI will be available at `http://localhost:5173`)*

2. **Trigger a disruption:**
   Open a second terminal and run:
   ```bash
   make trigger
   ```
   *(Watch the React UI automatically update!)*

3. **Stop services:**
   Press `Ctrl+C` in the first terminal, then run:
   ```bash
   make down
   ```

### ⚠️ Important Note for GitHub Codespaces Users
If you are running this in GitHub Codespaces, the React frontend needs to communicate with the FastAPI backend.
By default, Codespaces makes backend ports private. **You must make Port 8000 Public.**
1. Look at the bottom panel in Codespaces and click the **Ports** tab.
2. Right-click on Port **8000** -> Port Visibility -> **Public**.
3. Now open the React UI (Port 5173).

---

## How to Run (Windows)

If you are on Windows, ensure Docker Desktop is running, then use the provided PowerShell scripts inside the `axis-prototype` directory:

```powershell
cd axis-prototype
```

1. **Start all services:**
   Open a PowerShell window as Administrator and run:
   ```powershell
   .\start_all.ps1
   ```
2. **Trigger a disruption:**
   ```powershell
   .\trigger_disruption.ps1
   ```

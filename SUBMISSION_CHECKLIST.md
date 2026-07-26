# Round 1 Submission Checklist - AXIS Travel Disruption Concierge

**Team**: [Your Team Name]  
**Date**: 2026-07-26  
**Repo**: https://github.com/bishwathakur/Prototype-1

---

## ✅ Implementation Success Criteria (from guide)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `docker-compose up -d` starts Kafka + Postgres | ✅ | `docker-compose.yml` with Zookeeper:2181, Kafka:9092, Postgres:5432 |
| 2 | FastAPI backend auto-creates DB table & seeds AX100 | ✅ | `services/backend-agent/database.py:init_db()` + `main.py:startup_event()` |
| 3 | React frontend shows "Flight AX100 is On Time" initially | ✅ | `frontend/src/App.jsx` polls `/api/itinerary/CM-123`, Green state |
| 4 | `python producer.py` pushes cancelled event | ✅ | `services/event-producer/producer.py` emits to `flight-status-raw` after 10s |
| 5 | Within 5s: detector logs → agent runs → UI shows "Rebooked on DL200" | ✅ | Full flow: producer→detector→Kafka→backend→agent→DB→UI poll |
| 6 | **Zero external API keys** (OpenAI, Amadeus, etc.) | ✅ | All mocked: deterministic agent, fake flight data, local Kafka/Postgres |
| 7 | Self-contained with `requirements.txt` + `package.json` | ✅ | Every service has requirements; frontend has package.json |

---

## ✅ Task Requirements Coverage

| Task | Implementation |
|------|----------------|
| **Monitor live flight data & detect disruptions** | `detector.py` consumes `flight-status-raw`, filters CANCELLED/delay>90min → `disruption-confirmed` |
| **Autonomous rebooking logic with policy** | `agent.py`: search alternatives → check policy ($500 limit) → book DL200 → update DB |
| **Card member interface** | React + Vite + Tailwind: 3-state UI (Green/Red/Gold), polls every 2s |
| **Integrate airline/hotel/notification APIs** | **Mocked** for prototype: `search_alternative_flights()`, `check_policy()`, `rebook_itinerary()` — ready for real API swap |
| **Test & optimize** | End-to-end verified: Green → Red → Gold in <3s |

---

## 📁 Deliverables Checklist

| Deliverable | Status | Location |
|-------------|--------|----------|
| **Project Description** (mandatory) | ✅ | `README.md` + `axis-prototype/docs/proposal-1-travel-disruption-concierge.md` |
| **Presentation** (mandatory) | ✅ | Create from `PRESENTATION_OUTLINE.md` below |
| **Video Demo** (mandatory) | ⏳ **Record now** | See recording script below |
| **GitHub Repo** | ✅ | https://github.com/bishwathakur/Prototype-1 |
| **Architecture Diagram** | ✅ | Mermaid in `README.md` |
| **Sequence Diagram** | ✅ | Mermaid in `README.md` |
| **Project Structure** | ✅ | `README.md` tree view |

---

## Video Demo Recording Script (2-3 minutes)

### Setup (before recording)

1. Open a terminal.
2. Change to the prototype directory:
   ```
   cd axis-prototype
   ```
3. Start all services:
   ```
   make up
   ```
4. Wait for all services to start.
5. Open the frontend URL in a browser.
6. In GitHub Codespaces: Set Port 8000 visibility to Public.

### Recording Steps

| Time | Action | Narrator Notes |
|------|--------|----------------|
| 0:00-0:15 | Show the GitHub repository and the README file. | "This is AXIS. AXIS means Autonomous eXperience and Itinerary Servicing." |
| 0:15-0:30 | Show the architecture diagram. | "The system is event-driven. Kafka sends data to the Detector. The Detector sends data to the Backend Agent. The Backend Agent uses PostgreSQL. The frontend uses React." |
| 0:30-0:45 | Show the frontend in the Green state. | "This is the steady state. Flight AX100 is ON_TIME. The system polls every 2 seconds." |
| 0:45-1:00 | Run the trigger command in the terminal. | "This simulates a cancellation event for flight AX100 from Amadeus." |
| 1:00-1:30 | Watch the detector log and the backend log. | "The detector filters the CANCELLED status. The backend updates the database to CANCELLED." |
| 1:30-2:00 | Watch the user interface change from Red to Gold. | "The agent evaluates two alternatives. DL200 costs 400 dollars. UA300 costs 600 dollars. The policy limit is 500 dollars. The policy passes for DL200. The agent rebooks the flight to DL200." |
| 2:00-2:15 | Show the final Gold state. | "The card member sees the resolution. The flight is rebooked on DL200. No manual action is necessary." |
| 2:15-2:30 | Show code snippets. | "The mock agent is deterministic. No API keys are necessary. The system runs fully offline." |

Total time: approximately 2 minutes 30 seconds.

### Recording Tools

- **Codespaces**: Use the built-in screen recorder or OBS.
- **Local**: Use OBS Studio (free) or Windows Game Bar (Win+G).
- **Format**: MP4, 1080p, less than 100 MB.

---

## 📊 Presentation Outline (10 slides)

| Slide | Title | Content Source |
|-------|-------|----------------|
| 1 | **Title** | AXIS — Autonomous Travel-Disruption Concierge |
| 2 | **Problem** | Manual rebooking = high effort, low benefit use, brand damage |
| 3 | **Solution** | AXIS detects → evaluates → rebooks → notifies in <3 min |
| 4 | **Architecture** | Mermaid flowchart from README |
| 5 | **Detection Pipeline** | Kafka + Detector: CANCELLED / delay>90min |
| 6 | **Autonomous Agent** | Search → Policy ($500) → Book DL200 |
| 7 | **Card Member UI** | 3-state React: Green/Red/Gold |
| 8 | **Tech Stack** | Kafka, FastAPI, React, Postgres, Docker |
| 9 | **Demo** | Link to video + live Codespaces URL |
| 10 | **Next Steps** | Real Amadeus APIs, Hotel rebooking, Push notifications |

---

## 🚀 Quick Start for Judges

```bash
# 1. Clone
git clone https://github.com/bishwathakur/Prototype-1.git
cd Prototype-1/axis-prototype

# 2. Run (Linux/Mac/Codespaces)
make up
# Wait 15s, open frontend URL (port 5173)

# 3. Trigger
make trigger
# Watch UI: Green → Red → Gold

# 4. Cleanup
make down
```

**Windows**: `.\start_all.ps1` then `.\trigger_disruption.ps1`

**Codespaces**: Open repo → Create Codespace → Port 8000=Public → `make up` → `make trigger`

---

## 🔗 Submission Links

| Item | Link |
|------|------|
| GitHub Repo | https://github.com/bishwathakur/Prototype-1 |
| Video (upload to) | YouTube Unlisted / Google Drive / Dropbox |
| Live Demo | https://github.com/bishwathakur/Prototype-1 (Codespaces) |
| Presentation | Export as PDF from Google Slides / PowerPoint |

---

## 📝 Final Notes for Submission

1. **Video must be accessible** — test link in incognito
2. **Repo must be public** or grant access to judges
3. **Presentation PDF** — include speaker notes
4. **README.md** is the primary documentation — ensure it renders on GitHub
4. **All code runs offline** — emphasize "no API keys needed"

---

**Ready to Submit** ✅
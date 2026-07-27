# Presentation Outline - AXIS Travel Disruption Concierge
**Round 1 Submission - CodeStreet 2026**

---

## Slide 1: Title
**AXIS — Autonomous eXperience and Itinerary Servicing**  
*Autonomous Travel-Disruption Concierge for American Express*  
CodeStreet 2026 | Team [Name]

---

## Slide 2: The Problem
**Flight disruptions break the card member experience**

- **High Effort**: Member contacts airline, hotel, insurance separately
- **Low Benefit Utilization**: 68% don't know travel delay coverage exists
- **Brand Damage**: Member blames Amex for airline-caused disruption
- **Manual Gap**: No existing solution acts *during* the disruption in real-time
- **Insurance Gap**: Most disruptions have covered causes. Many do not. AXIS checks before rebooking.

---

## Slide 3: The Solution — AXIS
**Autonomous end-to-end resolution in under 3 minutes**

| Phase | Time | Action |
|-------|------|--------|
| Detect | T+0s | Kafka stream detects CANCELLED/delay>90min, classifies cause |
| Eligibility Gate | T+2s | Cause check + policy check + claim history check |
| Evaluate | T+10s | Agent scores alternatives (arrival, price, stops) |
| Policy Check | T+20s | Card benefit rules: fare diff < $500 (Platinum) |
| Execute | T+30s | Book flight, rebook hotel, pre-fill claim |
| Notify | T+90s | Push + in-app: "Done. Rebooked on DL200." |

**Result**: Member does *nothing*. Benefit activates automatically — but only for eligible disruptions.

---

## Slide 4: System Architecture
*Mermaid flowchart from README — 5 components, event-driven*

```
[Flight Data] → [Kafka: flight-status-raw] → [Detector] → [Kafka: disruption-detected]
                                                                   ↓
                                                          [Eligibility Gate]
                                                         /                \
                                           [Kafka: disruption-confirmed]  [Kafka: disruption-ineligible]
                                                      ↓                           ↓
                                             [FastAPI Backend]           [FastAPI Backend]
                                                      ↓                           ↓
                                             [PostgreSQL]                 [PostgreSQL: INELIGIBLE]
                                                      ↓                           ↓
                                             [React UI]                   [UI shows reason]
```

**Key**: Decoupled, replayable, exactly-once semantics via Kafka. Gate ensures rebooking only runs when insurance covers the claim.

---

## Slide 5: Disruption Detection Pipeline
**Component**: `services/disruption-detector/detector.py`

- Consumes `flight-status-raw` (simulated Amadeus feed)
- Rules: `status == "CANCELLED"` OR `delay_minutes > 90`
- Classifies cause: WEATHER, CARRIER_EQUIPMENT, SECURITY, etc.
- Publishes to `disruption-detected` (not `disruption-confirmed` — that topic is now gate output)
- **Latency**: <500ms from raw event to classified

---

## Slide 6: Insurance Eligibility Gate
**Component**: `services/eligibility-gate/gate.py`

Checks run before any rebooking logic:

| Check | Rule | Mock Value | Pass? |
|-------|------|------------|-------|
| 1. Covered cause | WEATHER, CARRIER_EQUIPMENT, HIJACKING, DOCUMENTATION | WEATHER | Yes |
| 2. Within policy | Delay > 6 hours AND < 2 claims/12mo | 480 min, 0 claims | Yes |
| 3. Eligible | Both checks pass | All pass | Yes |

**On pass**: emits to `disruption-confirmed` → agent rebooks  
**On fail**: emits to `disruption-ineligible` with reason → UI shows Gray state

Every decision is stored in the `eligibility_checks` table for audit.

---

## Slide 7: Autonomous Rebooking Agent
**Component**: `services/backend-agent/agent.py` (Deterministic Mock)

```python
def run_agent(flight_no, cm_id):
    alternatives = search_alternative_flights(flight_no)  # DL200 $400, UA300 $600
    for alt in alternatives:
        if check_policy(alt.price):  # Platinum limit: $500
            rebook_itinerary(flight_no, alt.flight)  # Books DL200
            return
```

The agent receives events only from `disruption-confirmed` (post-gate). It does not re-check eligibility.

---

## Slide 8: Card Member Interface
**Component**: `frontend/src/App.jsx` (React + Vite + Tailwind)

| State | Trigger | UI |
|-------|---------|-----|
| Green | DB: `ON_TIME` | "Flight AX100 is On Time" |
| Red | DB: `CANCELLED` | "AXIS finding alternatives..." |
| Gold | DB: `REBOOKED` | "Rebooked on DL200. No action needed." |
| Gray | DB: `INELIGIBLE` | "Cancelled — not eligible. Reason: ..." |

- Polls `/api/itinerary/CM-123` every 2s
- Zero-config: Works in Codespaces, local, Docker
- 4 states cover both happy path and rejection path

---

## Slide 9: Tech Stack
| Layer | Technology | Why |
|-------|------------|-----|
| Event Streaming | Apache Kafka (KRaft) | Durable, ordered, replayable |
| Stream Processing | Python `confluent-kafka` | Lightweight, no Flink needed for prototype |
| Eligibility Gate | Python Kafka consumer | Independent component, decoupled from agent |
| Agentic AI | Deterministic Python (LangChain-ready) | No API keys, predictable demo |
| API | FastAPI + Uvicorn | Async, OpenAPI, CORS-ready |
| Database | PostgreSQL 15 | ACID, JSON support, proven |
| Frontend | React 18 + Vite + Tailwind | Fast dev, small bundle, mobile-ready |
| Infrastructure | Docker Compose | One-command startup |

---

## Slide 10: Live Demo
**Watch the video**: [YouTube/Drive Link]  
**Try it yourself**: Open repo in GitHub Codespaces → `make up` → `make trigger`

**Demo Flow**:
1. Green UI: "Flight AX100 On Time"
2. Terminal: `make trigger` → producer emits CANCELLED + WEATHER cause
3. Detector logs: "Disruption found for AX100, cause=WEATHER"
4. Gate logs: "ELIGIBLE: All checks passed"
5. Backend logs: "Agent booking DL200"
6. UI: Red (CANCELLED) → Gold (REBOOKED on DL200)

**Ineligible alternative**: Change cause to SECURITY → gate rejects → UI shows Gray card with reason

**Total time**: <3 seconds end-to-end

---

## Slide 11: Next Steps & Impact
| Phase | Milestone |
|-------|-----------|
| **Round 2** | Integrate real Amadeus Flight Offers + Orders APIs |
| **Phase 2** | Hotel rebooking via partner APIs (Marriott/Hilton) |
| **Phase 3** | Push notifications (FCM/APNs), claim auto-submit to Amex Benefits |
| **Production** | Kubernetes (EKS), MSK, RDS, Redis ElastiCache |

**Projected Impact**:
- 100% eligible disruptions → auto-claim filed
- <3 min resolution vs 2-4 hours manual
- NPS +15 pts for Platinum travel benefits
- Clear communication when disruption is not covered

---

## Appendix: Code Quality
- **Zero external dependencies** for prototype (mocked APIs)
- **Deterministic agent** — same result every demo
- **Docker-first** — runs anywhere with `docker compose up`
- **Codespaces-ready** — free cloud dev environment
- **Mermaid diagrams** — render natively on GitHub
- **Insurance-aware** — eligibility gate prevents out-of-pocket rebooking

---

**Thank you** — Questions?
# Proposal 1: Autonomous Travel-Disruption Concierge

**Hackathon:** CodeStreet 2026 — American Express
**Official Theme:** Autonomous Travel-Disruption Concierge
**Submission Round:** Round 1 — Idea Submission
**Date:** July 2026

---

## 1. Problem Statement

### 1.1 Current Situation

When a flight is cancelled or a connection is missed, the card member must do all of the following actions manually:

- Contact the airline to find an alternative flight.
- Contact the hotel to change the check-in date.
- Pay for unexpected costs such as meals and transport.
- Submit claims for travel insurance benefits.

This process takes several hours. The card member must do this work during a stressful disruption event.

### 1.2 Impact of the Problem

The manual process causes three specific problems:

1. **Card member effort is high.** The card member must speak to multiple service providers at the same time.
2. **Benefit utilization is low.** Many card members do not know that their American Express card covers travel delay costs. The benefits go unclaimed.
3. **Customer satisfaction decreases.** The card member associates the negative disruption experience with the American Express brand, even when the disruption is caused by the airline.

### 1.3 Problem Boundary

This solution addresses travel disruptions only. It does not address:

- Pre-trip itinerary planning.
- General travel recommendations.
- Fraud detection on travel transactions.

---

## 2. Proposed Solution

### 2.1 Solution Name

**AXIS** — Autonomous eXperience and Itinerary Servicing agent.

### 2.2 Solution Summary

AXIS is an autonomous agent that performs the following steps automatically when a travel disruption occurs:

1. AXIS detects the disruption from live flight data feeds.
2. AXIS evaluates available alternative flights and hotels.
3. AXIS selects the best option within the card member's travel policy.
4. AXIS executes the rebooking via airline and hotel APIs.
5. AXIS notifies the card member with the new itinerary.

The card member does not perform any manual action. AXIS completes the full resolution cycle in under three minutes.

### 2.3 Key Capability: Card-Aware Policy Engine

AXIS enforces American Express card benefit rules during rebooking. Specifically:

- AXIS books replacement flights up to the fare difference limit defined by the card policy.
- AXIS books hotel stays that qualify for travel delay insurance coverage.
- AXIS pre-fills the insurance claim and submits it on behalf of the card member.

This means the card member receives benefit activation automatically. The card member does not need to know that the benefit exists.

---

## 3. System Architecture

### 3.1 Component Overview

The system has four components. Each component has a single responsibility.

```
[Flight Data Sources]
        |
        v
[Component 1: Disruption Detection Pipeline]
        |
        v
[Component 2: Autonomous Rebooking Agent]
        |
        v
[Component 3: Card Policy Engine]
        |
        v
[Component 4: Card Member Notification + UI]
```

### 3.2 Component 1 — Disruption Detection Pipeline

**Technology:** Apache Kafka, Apache Flink, Python

**Function:**

This component ingests live flight status data. It processes the data as a continuous stream. It detects disruption events in real time.

**Steps the component performs:**

1. Consume flight status events from the Amadeus Flight Status API via a Kafka topic named `flight-status-raw`.
2. Apply a Flink streaming job to evaluate each event against three disruption rules:
   - Rule A: Flight status changes to `CANCELLED`.
   - Rule B: Flight departure delay exceeds 90 minutes.
   - Rule C: Calculated connection time after delay is less than the minimum connection time for the destination airport.
3. Emit confirmed disruption events to a Kafka topic named `disruption-confirmed`.

**Output:** A structured disruption event containing: card member ID, affected flight number, disruption type, affected hotel reservation ID (if applicable), and UTC timestamp.

**Why Kafka and Flink:**

Kafka provides durable, ordered, replayable event storage. Flink provides stateful stream processing with exactly-once semantics. This combination ensures that no disruption event is missed and no card member is notified twice.

### 3.3 Component 2 — Autonomous Rebooking Agent

**Technology:** LangChain (Python), Amadeus Flight Offers API, hotel partner APIs

**Function:**

This component receives the disruption event and executes the rebooking autonomously.

**Steps the component performs:**

1. Read the disruption event from the `disruption-confirmed` Kafka topic.
2. Query the Amadeus Flight Offers API for alternative flights that meet the following criteria:
   - Same destination.
   - Departure within 6 hours of the original flight.
   - Available seats in the same cabin class or lower.
3. Score each alternative flight using the following weighted criteria:
   - Arrival time difference from original (weight: 40%).
   - Price difference from original (weight: 35%).
   - Number of stops (weight: 25%).
4. Select the highest-scoring alternative that is within the card policy spending limit.
5. Execute the booking via the Amadeus Orders API.
6. If a hotel stay is affected, query the hotel partner API and rebook the earliest available check-in date.
7. Write the new itinerary to the PostgreSQL database.
8. Emit a `rebooking-complete` event to the Kafka notification topic.

**Agent tool set (LangChain tools):**

| Tool Name | API Called | Purpose |
|---|---|---|
| `search_flights` | Amadeus Flight Offers | Find alternative flights |
| `book_flight` | Amadeus Orders | Execute flight booking |
| `search_hotels` | Hotel partner API | Find available hotel rooms |
| `book_hotel` | Hotel partner API | Execute hotel rebooking |
| `submit_claim` | AmEx Benefits API | Pre-fill travel delay claim |

### 3.4 Component 3 — Card Policy Engine

**Technology:** Python, PostgreSQL, Redis

**Function:**

This component enforces card benefit rules. Every rebooking decision passes through this component before execution.

**Rules the engine enforces:**

- The total cost of the replacement flight must not exceed the original fare plus USD 500 (Platinum card limit).
- Hotel rebooking is covered for a maximum of 3 nights per disruption event.
- Travel delay insurance claim is eligible if the delay exceeds 6 hours.
- Rebooking executes only on airlines that are in the approved partner list for the card.

**Redis usage:** Policy rules are cached in Redis with a 1-hour TTL. This reduces latency during the rebooking decision step.

### 3.5 Component 4 — Card Member Notification and UI

**Technology:** React Native (mobile), FastAPI (backend), Firebase Cloud Messaging (push)

**Function:**

This component informs the card member at each stage of the resolution. The card member receives a push notification and can view the full resolution status in the AXIS mobile screen.

**Notification sequence:**

1. **T+0s:** "We detected a disruption on your flight [XX123]. We are finding your best options."
2. **T+30s:** "We found an alternative: [XX456] departing at [TIME]. We are booking now."
3. **T+90s:** "Done. Your new flight is confirmed. Your hotel check-in is updated. Your travel delay claim is submitted. See your new itinerary below."

**UI screens:**

- **Disruption Alert Screen:** Shows the original flight, disruption type, and status indicator.
- **Resolution Screen:** Shows the new flight, new hotel, cost difference, and claim reference number.
- **Benefit Screen:** Shows the travel delay insurance claim status and estimated reimbursement amount.

---

## 4. Data Flow Diagram

```
Amadeus API (flight status)
        |
        | [HTTP poll every 60s]
        v
Kafka Topic: flight-status-raw
        |
        | [Flink streaming job]
        v
Kafka Topic: disruption-confirmed
        |
        | [LangChain agent consumes event]
        v
Policy Engine (Redis cache + PostgreSQL rules)
        |
        | [Policy check: PASS / BLOCK]
        v
Amadeus Orders API + Hotel API
        |
        | [Booking confirmed]
        v
Kafka Topic: rebooking-complete
        |
        | [FastAPI backend reads event]
        v
Firebase Cloud Messaging → Card Member Mobile App
```

---

## 5. Technology Stack

| Layer | Technology | Reason for Selection |
|---|---|---|
| Event streaming | Apache Kafka | Durable, ordered, replayable event log |
| Stream processing | Apache Flink | Stateful, exactly-once disruption detection |
| Agentic AI | LangChain (Python) | Structured tool-calling for multi-step rebooking |
| Travel data | Amadeus for Developers API | Covers flight search, status, and booking |
| Policy store | PostgreSQL + Redis | Rules stored in PostgreSQL, cached in Redis |
| Backend API | FastAPI (Python) | Lightweight, async, well-suited for event-driven workloads |
| Mobile UI | React Native | Single codebase for iOS and Android |
| Push notifications | Firebase Cloud Messaging | Reliable, cross-platform push delivery |
| Cloud | AWS (EKS + MSK) | Managed Kafka (MSK) and container orchestration (EKS) |

---

## 6. Team and Skill Alignment

| Responsibility | Assigned To | Skill Used |
|---|---|---|
| Kafka topic design and Flink job | Team Member 1 | Data engineering, pipeline automation |
| LangChain agent and tool integration | Team Member 1 | Python, API integration |
| Policy engine (Python + PostgreSQL) | Team Member 2 | Backend SDE, Python |
| FastAPI backend and Amadeus integration | Team Member 2 | Backend SDE, API development |
| React Native UI and push notification | Team Member 1 or 2 | Web/app development |

---

## 7. Demo Plan (Round 2)

The demo shows the following sequence on a live screen:

1. A mock flight status event is published to the Kafka topic. This simulates a flight cancellation.
2. The Flink job detects the disruption. The disruption alert appears on the mobile screen within 5 seconds.
3. The LangChain agent executes the rebooking tool sequence. Each tool call is visible in a real-time log panel.
4. The policy engine validates the selected flight. A green "Policy: APPROVED" indicator appears.
5. The booking API call completes. The mobile screen transitions to the Resolution Screen.
6. The travel delay claim is submitted automatically. The claim reference number appears on the Benefit Screen.

**Total demo duration:** 3 minutes.
**All API calls use the Amadeus sandbox environment.** No real bookings are made.

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Disruption detection latency | Less than 10 seconds from event to confirmed disruption |
| Rebooking completion time | Less than 3 minutes from detection to confirmed booking |
| Policy enforcement accuracy | 100% — zero bookings outside card policy limits |
| Notification delivery rate | Greater than 99% via Firebase |
| Unclaimed benefit activation rate | 100% of eligible disruptions trigger a pre-filled claim |

---

## 9. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Amadeus sandbox API rate limits | Medium | High | Cache flight search results; use mock data for high-frequency demo steps |
| LangChain agent selects incorrect tool order | Low | Medium | Add explicit tool orchestration steps; validate tool output before next step |
| Hotel API does not cover all partner hotels | Medium | Low | Limit demo to hotels in Amadeus hotel search coverage area |
| Flink job state loss on restart | Low | High | Use RocksDB state backend with checkpointing to S3 every 30 seconds |

---

## 10. Submission Checklist

- [x] Project description (this document)
- [ ] Presentation (slide deck — 10 slides)
- [ ] Architecture diagram (exported PNG)
- [ ] Demo video (3 minutes)
- [ ] GitHub repository link

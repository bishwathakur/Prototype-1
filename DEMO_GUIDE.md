# Demo Video Recording Guide
## AXIS Prototype — 3 Minute Walkthrough for CodeStreet 2026

---

## Recording Setup

**Tools**: OBS Studio, Loom, or GitHub Codespaces built-in recording.
**Duration**: Exactly 3 minutes.
**Resolution**: 1920x1080 minimum.
**Audio**: Clear narration. No background noise.

---

## Script and Timing (Total: 3:00)

### 0:00 – 0:15 | Problem Statement

> "When a flight is cancelled, American Express card members spend 3 to 6 hours manually rebooking flights, hotels, and filing insurance claims. Most card members do not know that their Platinum card covers delay costs. Therefore, benefits go unclaimed."

**Visual**: Show the Problem Statement slide from the proposal document, or the Problem section of the README file.

### 0:15 – 0:30 | Solution Summary

> "AXIS solves this problem autonomously. It detects disruptions from live flight streams. It evaluates alternatives within card policy. It executes the rebooking. It notifies the card member. All of this happens in under 3 minutes. Zero manual steps are necessary."

**Visual**: Show the architecture diagram (the Mermaid flowchart in the README file).

### 0:30 – 0:45 | Live Demo Start

> "I will now show you the working prototype. I am in GitHub Codespaces. No local setup is needed."

**Visual**: Terminal with `make up` running. Show Docker containers starting.

### 0:45 – 1:15 | Steady State

> "The React user interface polls the FastAPI backend every 2 seconds. Flight AX100 for member CM-123 shows ON_TIME. The card is green."

**Visual**: Browser at Port 5173 showing the green "AX100 is On Time" card.

### 1:15 – 1:45 | Trigger Disruption

> "Now I will simulate a cancellation. The producer pushes a CANCELLED event to the Kafka topic flight-status-raw."

**Visual**: Terminal 2 running `make trigger`. Shows producer output.

### 1:45 – 2:15 | Detection and Agent Handoff

> "The detector filters the raw stream. It confirms the disruption. It publishes to the topic disruption-confirmed. The backend Kafka consumer catches the event. It updates PostgreSQL to CANCELLED. It triggers the rebooking agent."

**Visual**:
- Terminal 1 (detector logs): "[DETECTOR] Disruption found for flight AX100"
- Terminal 1 (backend logs): "[BACKEND] Received disruption... [AGENT] Policy passed. Booking DL200..."

### 2:15 – 2:45 | Resolution

> "Within seconds, the user interface picks up the new state. Member CM-123 is now rebooked on Delta 200. The gold card confirms the resolution. No clicks, no calls, no stress."

**Visual**: Browser auto-updates. The Red "Cancelled" card changes to the Gold "Rebooked on DL200" card.

### 2:45 – 3:00 | Conclusion

> "AXIS turns a 3-hour manual crisis into a 3-second autonomous resolution. The system is built on Kafka, FastAPI, and React. It is ready for real Amadeus integration. Thank you."

**Visual**: Final architecture slide or the GitHub repository URL.

---

## Key Visuals to Capture

| Timestamp | What to Show |
|-----------|--------------|
| 0:30-0:45 | Terminal output of `make up` (Docker healthy) |
| 0:45-1:15 | Browser: Green card "AX100 On Time" |
| 1:15-1:45 | Terminal: `make trigger` command and producer logs |
| 1:45-2:15 | Terminal: Detector logs, Backend logs, Agent logs |
| 2:15-2:45 | Browser: Auto-transition from Red to Gold |
| 2:45-3:00 | Repository URL or GitHub Pages link |

---

## Codespaces Recording Tips

1. **Open the Ports tab** during recording. Show Port 8000 set to Public.
2. **Split the terminal** (Ctrl+Shift+5) to show detector logs and backend logs side-by-side.
3. **Browser DevTools Network tab** (optional) — show the 2-second polling requests.
4. **Zoom the browser** to 125 percent for readability.

---

## Post-Production

1. **Trim** the video to exactly 3:00.
2. **Add captions** for terminal commands.
3. **Overlay** the repository URL at the end.
4. **Export** as MP4 (H.264, 1080p).
5. **Upload** to YouTube (unlisted) or GitHub Releases.

---

## Alternative: Local Recording (Windows)

```powershell
# Terminal 1 (Run as Administrator)
cd axis-prototype
.\start_all.ps1

# Terminal 2
.\trigger_disruption.ps1
```

Record with **Xbox Game Bar** (Win+G) or **OBS**.
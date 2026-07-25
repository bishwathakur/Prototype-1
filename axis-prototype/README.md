# AXIS Prototype
Autonomous Travel-Disruption Concierge prototype for CodeStreet 2026.

## How to Run (Codespaces / Linux / Mac)

The easiest way to run this project is via the provided `Makefile`.

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

## How to Run (Windows)

If you are on Windows, ensure Docker Desktop is running, then use the provided PowerShell scripts:

1. **Start all services:**
   Open a PowerShell window as Administrator and run:
   ```powershell
   .\start_all.ps1
   ```
2. **Trigger a disruption:**
   ```powershell
   .\trigger_disruption.ps1
   ```

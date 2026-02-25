# Agent — Remote Monitoring Portal

Lightweight Python agent that runs on Windows machines and streams real-time system metrics to the backend via WebSocket. Can be compiled to a standalone `.exe` with PyInstaller — no Python installation required on target machines.

---

## What It Does

Every `report_interval` seconds (default: 5), the agent collects and sends:

| Data Type | Contents |
|-----------|---------|
| System info | CPU %, RAM %, Disk %, uptime, OS version |
| Processes | PID, name, CPU %, RAM %, status, user |
| Disk partitions | Mount point, filesystem, total/used/free |
| Network interfaces | Interface name, IP, bytes sent/received |
| Active users | Username, terminal, login time |

It also listens for commands from the backend:

| Command | What happens |
|---------|-------------|
| `refresh_data` | Sends a full data update immediately |
| `get_processes` | Sends current process list immediately |
| `kill_process` | Terminates the process with the given PID |

---

## Stack

| Package | Purpose |
|---------|---------|
| `psutil` | System metrics — CPU, RAM, disk, processes, network |
| `websockets` | WebSocket client connection to the backend |
| `pyinstaller` | Compile to standalone `.exe` (build-time only) |

---

## Folder Structure

```
agent/
├── agent.py          # Main entry point — connection loop, reconnect logic
├── config.json       # Agent ID, server URL, and auth token ← you create this
└── requirements.txt
```

---

## Setup

### 1. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `config.json`

```json
{
  "server_url": "ws://localhost:8000",
  "agent_id": "DESKTOP-TEST01",
  "token": "paste-your-agent-token-here",
  "report_interval": 5
}
```

**Where to get the token:**

Option A — From `seed_data.py` output. After running the backend seed script, the token for `DESKTOP-TEST01` is printed to the console.

Option B — From the admin panel. Log into the web portal as `admin`, go to Agents → Generate Token, copy it here.

Option C — Directly from the database:
```bash
# From the backend/ directory
python -c "from app.database import SessionLocal; from app.models import Agent; db = SessionLocal(); a = db.query(Agent).filter_by(agent_id='DESKTOP-TEST01').first(); print(a.token)"
```

**Config fields:**

| Field | Description |
|-------|-------------|
| `server_url` | WebSocket URL of the backend. Use `ws://` in dev, `wss://` in production. |
| `agent_id` | Must exactly match an agent registered in the database — case-sensitive. |
| `token` | Pre-shared secret for this agent. Treat like a password. |
| `report_interval` | Seconds between data reports. Minimum recommended: 3. |

### 4. Lock down config.json permissions

The config file contains a secret token. Restrict read access immediately after creating it:

```powershell
# PowerShell — restrict to current user only
icacls config.json /inheritance:r /grant:r "$env:USERNAME:(R)"
```

### 5. Run the agent

```bash
python agent.py
```

You should see:

```
🖥️  Remote Monitoring Agent starting...
📡 Connecting to ws://localhost:8000/ws/agent/DESKTOP-TEST01
✅ Connected to server
📊 Sending system data...
```

The agent will automatically reconnect if the backend goes down.

---

## WebSocket Protocol

### Agent → Backend (outgoing data)

All messages are JSON with a `type` and `data_type` field:

```json
{
  "type": "data_update",
  "data_type": "system_info",
  "data": {
    "cpu_percent": 24.5,
    "ram_percent": 61.2,
    "ram_used_gb": 9.8,
    "ram_total_gb": 16.0,
    "disk_percent": 44.0,
    "disk_used_gb": 220.0,
    "disk_total_gb": 500.0,
    "uptime_hours": 72.4,
    "os_info": "Windows 11 22H2"
  }
}
```

Other `data_type` values: `processes`, `disk_partitions`, `network_info`, `users`

### Backend → Agent (incoming commands)

```json
{
  "type": "command",
  "command_id": 42,
  "command_type": "kill_process",
  "command_data": { "pid": 8812 }
}
```

The agent executes the command and sends back a result:

```json
{
  "type": "command_result",
  "command_id": 42,
  "status": "executed",
  "result": { "killed_pid": 8812 }
}
```

---

## Building the `.exe`

Compile the agent into a single standalone executable for deployment to machines without Python:

### 1. Install PyInstaller (one-time)

```bash
pip install pyinstaller
```

### 2. Build

```bash
pyinstaller --onefile --name "MonitoringAgent" agent.py
```

Output: `agent/dist/MonitoringAgent.exe`

Build flags explained:

| Flag | Meaning |
|------|---------|
| `--onefile` | Bundle everything into a single `.exe` |
| `--name` | Name of the output executable |

### 3. Deploy to target machine

Copy these two files to the target machine — nothing else is needed:

```
MonitoringAgent.exe
config.json
```

Place them in the same directory, configure `config.json` with the correct `server_url` and `token`, then run:

```powershell
.\MonitoringAgent.exe
```

### Run as a Windows Service (for persistence across reboots)

To have the agent start automatically with Windows, register it as a service using NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM from https://nssm.cc and add to PATH, then:
nssm install MonitoringAgent "C:\path\to\MonitoringAgent.exe"
nssm set MonitoringAgent AppDirectory "C:\path\to\"
nssm start MonitoringAgent
```

---

## Troubleshooting

### Agent connects but backend shows it as Offline

The `agent_id` in `config.json` doesn't match what's registered in the database. Check for typos — the match is case-sensitive. The backend logs will show the exact agent ID it received.

### `ConnectionRefusedError` on startup

The backend isn't running or isn't reachable at the configured `server_url`. Verify:
- `uvicorn` is running in the backend terminal
- The `server_url` in `config.json` points to the correct host and port
- No firewall is blocking the WebSocket port

### `401 Unauthorized` on connect

The token in `config.json` doesn't match what's stored in the database for this agent. Regenerate a token from the admin panel and update `config.json`.

### `kill_process` fails with "Access Denied"

The agent process doesn't have permission to terminate the target process. This happens when attempting to kill a process owned by SYSTEM or another privileged user. Run the agent as Administrator if you need to kill system-level processes.

### `.exe` crashes immediately on target machine

Usually caused by `config.json` being missing or malformed. Run from the command line first (rather than double-clicking) to see the error output:

```powershell
cd C:\path\to\agent
.\MonitoringAgent.exe
```

### High CPU usage from the agent itself

Increase `report_interval` in `config.json`. At `5` seconds, collecting full process lists on a machine with hundreds of processes can be expensive. Set to `15` or `30` for lighter load.

---

## Security Notes

- `config.json` contains a secret token — treat it like a password and restrict file permissions (see Setup step 4).
- The agent token gives write access for this agent's data only — it cannot read other agents' data or access user accounts.
- In production, always use `wss://` (WebSocket over TLS) in `server_url` — plain `ws://` sends the token in the clear.
- Rotate the agent token periodically from the admin panel and update `config.json` on the machine.
- If you suspect a token is compromised, delete and re-register the agent from the admin panel to invalidate the old token immediately.
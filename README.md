# 🖥️ Remote Monitoring Portal

A Python-based remote monitoring system for Windows machines. A lightweight agent collects real-time system metrics and streams them over WebSocket to a FastAPI backend, which serves a React dashboard with live charts, process management, and role-based access control.

## 📸 Screenshots

<img width="1916" height="983" alt="Screenshot 2026-02-25 141751" src="https://github.com/user-attachments/assets/e7a29bb7-34b0-4921-86e9-3971a97e8848" />
<img width="1918" height="976" alt="Screenshot 2026-02-25 141859" src="https://github.com/user-attachments/assets/2098333f-563f-4568-b142-2693b261ecd4" />
<img width="1916" height="979" alt="Screenshot 2026-02-25 141932" src="https://github.com/user-attachments/assets/bcd0333d-19f6-4e25-93c4-a0f48b9a0f82" />
<img width="1913" height="978" alt="Screenshot 2026-02-25 142001" src="https://github.com/user-attachments/assets/5c990373-3c12-47c3-9ae3-464b8dee4be9" />
<img width="1915" height="986" alt="Screenshot 2026-02-25 142045" src="https://github.com/user-attachments/assets/71046dae-49ff-4161-8765-1ddf42ae0a9c" />
<img width="1916" height="985" alt="Screenshot 2026-02-25 142113" src="https://github.com/user-attachments/assets/de0b5349-c041-483c-a3e5-ce9f1eb18067" />
<img width="1911" height="979" alt="Screenshot 2026-02-25 142147" src="https://github.com/user-attachments/assets/f4ecda42-ae28-46b6-b736-325bde356ea3" />

*Admin dashboard showing all monitored agents*


<img width="1915" height="982" alt="Screenshot 2026-02-25 142237" src="https://github.com/user-attachments/assets/79d383fb-e3a7-4a73-a946-06688d94b39d" />
<img width="1909" height="984" alt="Screenshot 2026-02-25 142401" src="https://github.com/user-attachments/assets/9d4ae6b7-6c18-41f1-87f0-c2bc622c6d68" />
*Real-time system monitoring with live charts*

---

## ✨ Features

- **Real-time monitoring** — CPU, RAM, disk, processes, network, and active users streamed live via WebSocket
- **Role-based access** — Admins manage everything; regular users see only their assigned agents
- **Remote commands** — Send `refresh_data`, `get_processes`, and `kill_process` commands to agents from the browser
- **Historical charts** — Recharts-powered CPU and RAM history graphs
- **Windows agent** — Compiles to a standalone `.exe` — no Python needed on target machines
- **Dark UI** — Mission-control themed, pure CSS, no component libraries

---

## 🏗️ Architecture

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Windows Agent   │◄───────►│  FastAPI Backend │◄───────►│   React Portal   │
│  Python / .exe   │WebSocket│   port 8000      │  HTTP + │   port 5173      │
└──────────────────┘         └────────┬─────────┘   WS    └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  SQLite Database │
                             └──────────────────┘
```

### Real-time Data Flow

```
Agent collects system data every 5 seconds
        ↓
Sends JSON over WebSocket  →  /ws/agent/{agent_id}
        ↓
Backend saves to DB and broadcasts to subscribed clients
        ↓
Browser receives update  →  React re-renders charts instantly
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite, WebSockets |
| Frontend | React 18, Vite, Pure CSS, Recharts, Axios |
| Agent | Python, psutil, websockets, PyInstaller |
| Auth | JWT (HS256), bcrypt, pre-shared agent tokens |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Windows (for the agent — backend and frontend run anywhere)

### Terminal 1 — Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows

pip install -r requirements.txt
python seed_data.py            
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: **http://localhost:8000** · API docs: **http://localhost:8000/docs**

### Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Portal: **http://localhost:5173**

### Terminal 3 — Agent

```bash
cd agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

---

## 🔑 Test Credentials

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | All agents, user management, send commands |
| `testuser_1` | `testuser123` | User | Assigned agents, read-only |

> ⚠️ Change these before deploying to any shared or production environment.

---

## 📁 Project Structure

```
remote-monitoring-portal/
├── backend/               # FastAPI server
│   ├── app/
│   │   ├── main.py        # Entry point, CORS, router registration
│   │   ├── config.py      # Settings from .env
│   │   ├── database.py    # SQLAlchemy engine + session
│   │   ├── models.py      # Database table definitions
│   │   ├── auth.py        # JWT, bcrypt, token helpers
│   │   ├── routers/       # auth, users, agents, commands, websocket
│   │   └── websockets     # WebSocket connection 
│   ├── seed_data.py       # Populate DB with test data
│   └── requirements.txt
│
├── frontend/              # React web portal
│   ├── src/
│   │   ├── context/       # AuthContext, WebSocketContext
│   │   ├── services/      # api.js, websocket.js
│   │   ├── utils/         # helpers.js
│   │   ├── components/    # Auth, Common, Dashboard, AgentDetail, Admin
│   │   └── styles/        # variables.css, global.css
│   ├── vite.config.js     # Proxy /api and /ws to backend
│   └── package.json
│
├── agent/                 # Windows monitoring agent
│   ├── agent.py           # Main loop, reconnect logic, command handler
│   ├── config.json        # Agent ID + auth token ← you create this
│   └── requirements.txt
│
├── README.md
├── SECURITY.md
└── SETUP_GUIDE.md
```

---

## 🔐 Security

| Feature | Implementation |
|---------|---------------|
| Passwords | bcrypt — never stored in plain text |
| Sessions | JWT tokens, HS256, 7-day expiry |
| Agent auth | Unique pre-shared token per machine |
| Access control | Role-based (admin / user) enforced server-side |
| Input validation | Pydantic schemas on all endpoints |
| SQL injection | Prevented via SQLAlchemy ORM |
| XSS | React JSX auto-escapes all string output |

See [SECURITY.md](SECURITY.md) for the full security model, known limitations, and vulnerability disclosure process.

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login — returns JWT token |
| GET | `/api/auth/me` | Get current user profile |

### Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents/` | List agents (filtered by role) |
| GET | `/api/agents/{id}` | Agent details |
| GET | `/api/agents/{id}/system-data` | Latest metrics |
| GET | `/api/agents/{id}/history` | Historical data for charts |
| GET | `/api/agents/{id}/processes` | Running process list |
| POST | `/api/agents/register` | Register new agent (admin) |

### Commands (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/commands/` | Send command to agent |
| GET | `/api/commands/agent/{id}` | Command history for agent |

### WebSocket

| URL | Description |
|-----|-------------|
| `ws://host/ws/agent/{id}?token={agent_token}` | Agent connection |
| `ws://host/ws/client/{id}?token={jwt}` | Browser connection |

Full interactive docs (with try-it-out): **http://localhost:8000/docs**

---

## 🏭 Building the Agent `.exe`

Compile to a standalone executable for deployment — no Python required on target machines:

```bash
cd agent
pip install pyinstaller
pyinstaller --onefile --name "MonitoringAgent" agent.py
# Output: agent/dist/MonitoringAgent.exe
```

Deploy `MonitoringAgent.exe` + `config.json` to the target machine. See [agent/README.md](agent/README.md) for Windows Service setup.

---

## 🐛 Troubleshooting

**CORS error on login** — `VITE_API_URL` in `frontend/.env` is set to a full URL. Set it to empty (`VITE_API_URL=`) and restart `npm run dev`.

**Login always returns 401** — Run `python seed_data.py` in the backend directory to create test users.

**Agent shows Offline immediately** — The `agent_id` in `config.json` doesn't match any registered agent in the database. Check for typos — match is case-sensitive.

**WebSocket not updating** — Verify `vite.config.js` has the `/ws` proxy with `ws: true`. Restart the dev server after any `.env` change.

**Charts are empty** — Either the agent isn't running (no live data) or `seed_data.py` hasn't been run (no historical data).

For detailed setup instructions and a full troubleshooting reference, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

---

## 📚 Documentation

| File | Contents |
|------|---------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Complete step-by-step setup, config reference, all error fixes |
| [SECURITY.md](SECURITY.md) | Security model, known limitations, disclosure process |
| [backend/README.md](backend/README.md) | Backend API, DB schema, module reference |
| [frontend/README.md](frontend/README.md) | Component structure, CSS architecture, hooks |
| [agent/README.md](agent/README.md) | Agent config, WebSocket protocol, `.exe` build |

---

## 🗺️ Roadmap

- [ ] Multi-platform agent (Linux, macOS)
- [ ] Email / webhook alerts for threshold breaches
- [ ] Historical data export (CSV, Excel)
- [ ] PostgreSQL support for production
- [ ] Docker Compose deployment
- [ ] Agent groups and tags
- [ ] Custom dashboard widgets
- [ ] Mobile app (React Native)

---
## 📧 Support

For issues or questions, please check the code comments or Django documentation.

---
**Happy Coding! Fiazan**
*Built with Python, React, and WebSockets*

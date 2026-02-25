# Setup Guide — Remote Monitoring Portal

Complete instructions for getting the backend, frontend, and Windows agent running from scratch.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Agent Setup](#agent-setup)
6. [Running the Full Stack](#running-the-full-stack)
7. [Seed Data & Test Credentials](#seed-data--test-credentials)
8. [Verifying Everything Works](#verifying-everything-works)
9. [Configuration Reference](#configuration-reference)
10. [Common Errors & Fixes](#common-errors--fixes)
11. [Production Deployment](#production-deployment)

---

## Prerequisites

Install these before starting. Versions listed are the minimum tested.

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| npm | 9+ | Comes with Node.js |
| Git | Any | https://git-scm.com |

Verify your installs:

```bash
python --version    # Python 3.10.x or higher
node --version      # v18.x.x or higher
npm --version       # 9.x.x or higher
```

> **Windows note:** This guide uses `python` and `pip`. If your system uses `python3` / `pip3`, substitute accordingly. The agent is Windows-specific; the backend and frontend run on any OS.

---

## Project Structure

```
remote-monitoring-portal/
│
├── backend/                  # FastAPI server
│   ├── app/
│   │   ├── main.py           # App entry point, CORS, routers
│   │   ├── config.py         # Settings from .env
│   │   ├── database.py       # SQLAlchemy setup
│   │   ├── models.py         # Database table definitions
│   │   ├── auth.py           # JWT, bcrypt, token helpers
│   │   ├── routers/
│   │      ├── auth.py       # /api/auth/...
│   │      ├── users.py      # /api/users/...
│   │      ├── agents.py     # /api/agents/...
│   │      ├── commands.py   # /api/commands/...
│   │      └── websocket.py  # /ws/...
│   ├── seed_data.py          # Populate DB with test data
│   ├── requirements.txt
│   └── .env                  # ← you create this
│
├── frontend/                 # React + Vite app
│   ├── src/
│   │   ├── context/          # AuthContext, WebSocketContext
│   │   ├── services/         # api.js, websocket.js
│   │   ├── utils/            # helpers.js
│   │   ├── components/       # All UI components
│   │   └── styles/           # CSS variables and globals
│   ├── vite.config.js        # Proxy config
│   ├── package.json
│   └── .env                  # ← you create this
│
├── agent/                    # Windows monitoring agent
│   ├── agent.py              # Main agent script
│   ├── config.json           # Agent ID + token (you create this)
│   └── requirements.txt
│
├── SECURITY.md
└── SETUP_GUIDE.md
```

---

## Backend Setup

### 1. Navigate to the backend folder

```bash
cd backend
```

### 2. Create a virtual environment

```bash
# Create the venv
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt. All subsequent `pip` commands install into this isolated environment.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Core packages this installs:

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM / database |
| `python-jose` | JWT tokens |
| `passlib[bcrypt]` | Password hashing |
| `python-multipart` | Form data (login) |
| `websockets` | WebSocket support |

### 4. Create the `.env` file

Create `backend/.env` with the following content:

```dotenv
# Application
APP_NAME=Remote Monitoring Portal
SECRET_KEY=change-this-to-a-long-random-string-before-going-to-production
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database (SQLite for development)
DATABASE_URL=sqlite:///./monitoring.db

# CORS — must match your frontend URL exactly
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Token expiry (days)
ACCESS_TOKEN_EXPIRE_DAYS=7
```

> ⚠️ **Change `SECRET_KEY`** before deploying anywhere. Use a random 64-character string — you can generate one with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. Initialize the database

The database is created automatically on first startup. To also populate it with test users and agents, run:

```bash
python seed_data.py
```

You should see output like:

```
✅ Database initialized
👤 Created user: admin (role: admin)
👤 Created user: user1 (role: user)
👤 Created user: user2 (role: user)
🖥️  Created agent: DESKTOP-TEST01
🖥️  Created agent: LAPTOP-DEV02
📊 Created 20 historical data points
✅ Seed complete
```

### 6. Start the backend server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
==================================================
🚀 Starting Remote Monitoring Portal Backend
==================================================
📦 Initializing database...
✅ Server ready on http://0.0.0.0:8000
📚 API docs:    http://0.0.0.0:8000/docs
==================================================
```

**Verify it's running:** Open http://localhost:8000/docs in your browser — you should see the Swagger UI with all endpoints listed.

---

## Frontend Setup

Open a **new terminal** for this — keep the backend running.

### 1. Navigate to the frontend folder

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

This installs React, Vite, axios, react-router-dom, react-icons, and all other packages from `package.json`.

### 3. Create the `.env` file

Create `frontend/.env` with the following content:

```dotenv
# Leave API URL blank — Vite proxy handles routing to the backend
VITE_API_URL=
VITE_WS_URL=

VITE_APP_NAME=Remote Monitoring Portal
```

> **Why blank?** The Vite dev server proxies all `/api` and `/ws` requests to `localhost:8000` automatically (configured in `vite.config.js`). Setting a full URL here would bypass the proxy and cause CORS errors.

### 4. Verify the Vite proxy config

Open `frontend/vite.config.js` and confirm it looks like this:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

If `/api` or `/ws` are missing from the proxy, add them — without this, all requests go directly to port 8000 and get blocked by CORS.

### 5. Start the frontend dev server

```bash
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in 300ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Verify it's running:** Open http://localhost:5173 — you should see the login page.

---

## Agent Setup

Open a **third terminal** for this. The agent runs on the Windows machine you want to monitor — in development that's typically your local machine.

### 1. Navigate to the agent folder

```bash
cd agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

The key package here is `psutil`, which reads CPU, RAM, disk, process, and network data from the OS.

### 4. Create `config.json`

The agent needs to know where the backend is and how to authenticate. Create `agent/config.json`:

```json
{
  "server_url": "ws://localhost:8000",
  "agent_id": "DESKTOP-TEST01",
  "token": "your-agent-token-here",
  "report_interval": 5
}
```

**Where do you get the token?**

Option A — Use the token from `seed_data.py`. Check the seed script output or the database for the token associated with `DESKTOP-TEST01`.

Option B — Generate a new one via the API:
1. Log in at http://localhost:5173 as `admin`
2. Go to the admin panel → Agents → Generate Token
3. Copy the token into `config.json`

**Fields explained:**

| Field | Description |
|-------|-------------|
| `server_url` | WebSocket URL of the backend |
| `agent_id` | Must match an agent registered in the database |
| `token` | Pre-shared token for that agent |
| `report_interval` | Seconds between data reports (default: 5) |

### 5. Restrict config.json permissions

The config file contains a secret token. Lock it down:

```bash
# Windows (PowerShell — restrict to current user only)
icacls config.json /inheritance:r /grant:r "$env:USERNAME:(R)"
```

### 6. Start the agent

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

The agent will now send CPU, RAM, disk, process, and network data to the backend every 5 seconds (or whatever `report_interval` is set to).

---

## Running the Full Stack

Summary of all three terminals you need open simultaneously:

| Terminal | Directory | Command |
|----------|-----------|---------|
| 1 — Backend | `backend/` | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| 2 — Frontend | `frontend/` | `npm run dev` |
| 3 — Agent | `agent/` | `python agent.py` |

Once all three are running, open http://localhost:5173.

---

## Seed Data & Test Credentials

After running `python seed_data.py`, these accounts and agents are available:

### Users

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | All agents, user management, commands |
| `user1` | `user123` | User | Assigned agents, read-only |
| `user2` | `user123` | User | Assigned agents, read-only |

### Agents

| Agent ID | Hostname | Assigned To |
|----------|----------|-------------|
| `DESKTOP-TEST01` | DESKTOP-TEST01 | admin, user1 |
| `LAPTOP-DEV02` | LAPTOP-DEV02 | admin, user2 |

> ⚠️ These credentials are for local development only. Remove or change them before deploying to any shared or production environment.

---

## Verifying Everything Works

Work through this checklist after starting all three services:

### Authentication
- [ ] http://localhost:5173 shows the login page
- [ ] Login as `admin` / `admin123` → redirects to admin dashboard
- [ ] Login as `user1` / `user123` → redirects to user dashboard (no User Management menu)
- [ ] Logout button clears session and returns to login

### Agent Status
- [ ] Admin dashboard shows `DESKTOP-TEST01` as **Online**
- [ ] CPU and RAM percentages are updating in real time
- [ ] Agent detail page shows live charts and process list

### Role-Based Access
- [ ] Logged in as `user1`: cannot see User Management page
- [ ] Logged in as `user1`: cannot see `LAPTOP-DEV02` (not assigned)
- [ ] Logged in as `admin`: can see both agents

### Commands (Admin Only)
- [ ] Admin can send `refresh_data` to an agent
- [ ] Command appears in the command log with status `pending` → `completed`
- [ ] `kill_process` with a valid PID terminates the process

### WebSocket
- [ ] Stop the agent (`Ctrl+C`) → agent status changes to **Offline** within ~10 seconds
- [ ] Restart the agent → status changes back to **Online**

### API Docs
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] http://localhost:8000/health returns `{"status": "healthy"}`

---

## Configuration Reference

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(required)* | JWT signing key — must be long and random |
| `DEBUG` | `True` | Enables verbose error responses |
| `HOST` | `0.0.0.0` | Interface to bind to |
| `PORT` | `8000` | Port to listen on |
| `DATABASE_URL` | `sqlite:///./monitoring.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated list of allowed frontend origins |
| `ACCESS_TOKEN_EXPIRE_DAYS` | `7` | JWT token lifetime |

### Frontend (`frontend/.env`)

| Variable | Value (dev) | Description |
|----------|------------|-------------|
| `VITE_API_URL` | *(empty)* | Leave blank — Vite proxy handles routing |
| `VITE_WS_URL` | *(empty)* | Leave blank — Vite proxy handles routing |
| `VITE_APP_NAME` | `Remote Monitoring Portal` | Displayed in browser tab and UI header |

### Agent (`agent/config.json`)

| Field | Description |
|-------|-------------|
| `server_url` | WebSocket URL of the backend (`ws://` in dev, `wss://` in prod) |
| `agent_id` | Must exactly match the `agent_id` registered in the database |
| `token` | Pre-shared token for this agent |
| `report_interval` | Data send frequency in seconds (minimum recommended: 3) |

---

## Common Errors & Fixes

### ❌ CORS error — "blocked by CORS policy"

**Cause:** The frontend is making requests directly to port 8000 instead of going through the Vite proxy.

**Fix:** Ensure `frontend/.env` has `VITE_API_URL=` (empty), and that `vite.config.js` has the proxy configured for `/api` and `/ws`. Restart `npm run dev` after changing `.env`.

---

### ❌ "Cannot update a component while rendering a different component"

**Cause:** `navigate()` is being called directly in the render body of `Login.jsx` instead of inside a `useEffect`.

**Fix:**
```javascript
// Replace the bare if-check with:
useEffect(() => {
  if (isAuthenticated) {
    navigate('/dashboard', { replace: true })
  }
}, [isAuthenticated, navigate])
```

Also make sure `useEffect` is imported at the top of the file.

---

### ❌ Backend won't start — "ModuleNotFoundError"

**Cause:** Virtual environment is not activated, or `pip install -r requirements.txt` hasn't been run.

**Fix:**
```bash
cd backend
venv\Scripts\activate     # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

---

### ❌ Agent shows "Offline" immediately after connecting

**Cause:** The `agent_id` in `config.json` doesn't match any registered agent in the database.

**Fix:** Check the database or run `seed_data.py`. The `agent_id` field in `config.json` must exactly match the `agent_id` column in the `agents` table, including capitalisation.

---

### ❌ Login returns 422 Unprocessable Entity

**Cause:** The login endpoint expects `application/x-www-form-urlencoded`, not JSON.

**Fix:** This is handled correctly in `api.js` using `URLSearchParams`. If you're testing directly via curl or Postman, send form data:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

---

### ❌ "useAuth must be used inside AuthProvider"

**Cause:** A component is using `useAuth()` but isn't wrapped by `<AuthProvider>` in the component tree.

**Fix:** Check `main.jsx` or `App.jsx` — `<AuthProvider>` must wrap `<App>` (or at minimum every component that calls `useAuth()`).

---

### ❌ WebSocket connections fail in the browser console

**Cause:** The frontend is trying to connect to `ws://localhost:8000` directly instead of through the Vite proxy.

**Fix:** Ensure `VITE_WS_URL=` is blank in `.env` and that the WebSocket service derives its URL from `window.location` or a relative path, not from the env variable.

---

### ❌ `npm run dev` fails with "vite: command not found"

**Cause:** `npm install` hasn't been run, or ran in the wrong directory.

**Fix:**
```bash
cd frontend
npm install
npm run dev
```

---

## Production Deployment

Development mode is not suitable for production. Here's what changes:

### Backend
- Set `DEBUG=False` in `.env`
- Use a production-grade database (PostgreSQL recommended): `DATABASE_URL=postgresql://user:pass@host/dbname`
- Generate a strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
- Run with multiple workers: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4`
- Place behind nginx or Caddy as a reverse proxy with TLS

### Frontend
- Build the static bundle: `npm run build` (outputs to `frontend/dist/`)
- Serve `dist/` from nginx or a CDN
- Set `VITE_API_URL=https://your-domain.com` and `VITE_WS_URL=wss://your-domain.com` in the build environment
- The Vite proxy only works in dev — in production, CORS must be configured properly on the backend

### Agent
- Change `server_url` in `config.json` to `wss://your-domain.com`
- Run the agent as a Windows Service for persistence across reboots
- Rotate agent tokens periodically

### CORS
Update `CORS_ORIGINS` in the backend `.env` to your exact production domain:
```dotenv
CORS_ORIGINS=https://your-domain.com
```
Never use `*` with `allow_credentials=True`.

### Checklist before going live
- [ ] All default seed passwords changed or seed data removed
- [ ] `SECRET_KEY` is a unique random value
- [ ] TLS certificate installed and working
- [ ] Backend bound to `127.0.0.1`, not `0.0.0.0`
- [ ] CORS origins restricted to production domain
- [ ] Agent `config.json` permissions locked down on each machine
- [ ] `npm audit` and `pip-audit` clear of high/critical CVEs

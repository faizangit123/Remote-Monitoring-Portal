# Backend — Remote Monitoring Portal

FastAPI server providing REST API, WebSocket connections, JWT authentication, and SQLite persistence for the Remote Monitoring Portal.

---

## Stack

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.100+ | Web framework |
| `uvicorn` | 0.23+ | ASGI server |
| `sqlalchemy` | 2.0+ | ORM / database |
| `python-jose` | 3.3+ | JWT tokens |
| `passlib[bcrypt]` | 1.7+ | Password hashing |
| `python-multipart` | 0.0.6+ | Form data (OAuth2 login) |
| `websockets` | 11+ | WebSocket support |
| `pydantic-settings` | 2.0+ | Settings from `.env` |

Full list with pinned versions: `requirements.txt`

---

## Folder Structure

```
backend/
├── app/
│   ├── main.py               # App entry point — CORS, lifespan, router registration
│   ├── config.py             # Settings loaded from .env
│   ├── database.py           # SQLAlchemy engine + session factory
│   ├── models.py             # Table definitions (users, agents, system_data, commands)
│   ├── auth.py               # bcrypt hashing, JWT encode/decode, agent token generation
│   ├── routers/
│   │   ├── auth.py           # POST /api/auth/login, GET /api/auth/me
│   │   ├── users.py          # CRUD /api/users/ (admin only)
│   │   ├── agents.py         # CRUD /api/agents/ + system data endpoints
│   │   ├── commands.py       # POST /api/commands/ — send commands to agents
│   │   └── websocket.py      # /ws/agent/{id} and /ws/client/{id}
│   └── websockets/
│       └── manager.py        # ConnectionManager — tracks live agent + client sockets
├── seed_data.py              # Populate DB with test users, agents, and history
├── requirements.txt
└── .env                      # ← you create this (see below)
```

---

## Setup

### 1. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env`

```dotenv
APP_NAME=Remote Monitoring Portal
SECRET_KEY=replace-with-a-long-random-string
DEBUG=True

HOST=0.0.0.0
PORT=8000

DATABASE_URL=sqlite:///./monitoring.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ACCESS_TOKEN_EXPIRE_DAYS=7
```

Generate a secure `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Seed the database

```bash
python seed_data.py
```

Creates test users, two agents, and 20 historical data points. Safe to re-run — checks for existing records before inserting.

### 5. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Health check |
| http://localhost:8000/docs | Swagger UI — interactive API docs |
| http://localhost:8000/redoc | ReDoc — alternative API docs |

---

## API Overview

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | No | Login — returns JWT token |
| GET | `/api/auth/me` | JWT | Get current user profile |
| POST | `/api/auth/register` | No | Register new user |

Login uses OAuth2 form encoding (not JSON):
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Users (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create user |
| GET | `/api/users/{id}` | Get user by ID |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |
| POST | `/api/users/{id}/assign-agent` | Assign agent access |
| DELETE | `/api/users/{id}/unassign-agent/{agent_id}` | Remove agent access |

### Agents

| Method | Endpoint | Admin only | Description |
|--------|----------|-----------|-------------|
| GET | `/api/agents/` | No | List agents (filtered by role) |
| POST | `/api/agents/register` | Yes | Register new agent |
| GET | `/api/agents/{id}` | No | Agent details |
| GET | `/api/agents/{id}/system-data` | No | Latest metrics |
| GET | `/api/agents/{id}/history` | No | Historical data for charts |
| GET | `/api/agents/{id}/processes` | No | Running process list |
| GET | `/api/agents/generate-token` | Yes | Generate a new agent token |

### Commands (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/commands/` | Send command to agent |
| GET | `/api/commands/` | List all commands |
| GET | `/api/commands/{id}` | Get command by ID |
| GET | `/api/commands/agent/{id}` | Commands for a specific agent |

Supported command types:

| `command_type` | `command_data` | Effect |
|----------------|---------------|--------|
| `refresh_data` | `null` | Agent sends fresh data immediately |
| `get_processes` | `null` | Agent sends current process list |
| `kill_process` | `{"pid": 1234}` | Agent terminates process by PID |

### WebSocket

| URL | Who connects | Auth |
|-----|-------------|------|
| `ws://host/ws/agent/{agent_id}?token={agent_token}` | Windows agent | Agent pre-shared token |
| `ws://host/ws/client/{agent_id}?token={jwt}` | Browser | User JWT |

---

## Database Schema

```
users
├── id              INTEGER  PK
├── username        TEXT     unique
├── email           TEXT     unique
├── hashed_password TEXT
├── role            TEXT     admin | user
├── is_active       BOOLEAN
└── created_at      DATETIME

agents
├── id              INTEGER  PK
├── agent_id        TEXT     unique  (e.g. "DESKTOP-PC01")
├── hostname        TEXT
├── ip_address      TEXT
├── token           TEXT     pre-shared auth token
├── is_online       BOOLEAN
├── os_info         TEXT
├── last_seen       DATETIME
└── created_at      DATETIME

user_agent_access             (many-to-many junction)
├── user_id         FK → users
└── agent_id        FK → agents

system_data
├── id              INTEGER  PK
├── agent_id        FK → agents
├── cpu_percent     FLOAT
├── ram_percent     FLOAT
├── ram_used_gb     FLOAT
├── ram_total_gb    FLOAT
├── disk_percent    FLOAT
├── disk_used_gb    FLOAT
├── disk_total_gb   FLOAT
├── uptime_hours    FLOAT
└── timestamp       DATETIME

commands
├── id              INTEGER  PK
├── agent_id        FK → agents
├── issued_by       FK → users
├── command_type    TEXT
├── command_data    JSON
├── status          TEXT     pending | sent | executed | failed
├── result          JSON
├── created_at      DATETIME
└── executed_at     DATETIME
```

---

## Key Modules

### `app/auth.py`

```python
hash_password(plain)          # Returns bcrypt hash
verify_password(plain, hash)  # Returns bool
create_access_token(data)     # Returns signed JWT string
decode_access_token(token)    # Returns payload dict or raises
generate_agent_token()        # Returns 32-byte hex token
```

### `app/websockets/manager.py`

```python
manager.connect_agent(agent_id, websocket)
manager.disconnect_agent(agent_id)
manager.connect_client(agent_id, websocket)
manager.broadcast_to_clients(agent_id, message)
manager.send_to_agent(agent_id, command)
manager.latest_data[agent_id]   # Most recent system data dict
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|---------|---------|-------------|
| `SECRET_KEY` | ✅ | — | JWT signing secret — keep private |
| `DEBUG` | No | `False` | Verbose error responses |
| `HOST` | No | `0.0.0.0` | Bind address |
| `PORT` | No | `8000` | Listen port |
| `DATABASE_URL` | No | `sqlite:///./monitoring.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated allowed origins |
| `ACCESS_TOKEN_EXPIRE_DAYS` | No | `7` | JWT lifetime in days |

---

## Development Notes

- `--reload` flag restarts the server automatically on any `.py` file change — do not use in production.
- SQLite stores the database as `monitoring.db` in the `backend/` directory. Delete this file to reset all data (you'll need to re-run `seed_data.py`).
- The Swagger UI at `/docs` lets you test every endpoint directly in the browser, including authenticated ones — click **Authorize** and paste a JWT token.
- All role enforcement happens in the routers via FastAPI `Depends()` — never rely on frontend-side role checks as a security boundary.

---

## Production Checklist

- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Set `DEBUG=False`
- [ ] Generate a new `SECRET_KEY`
- [ ] Bind to `127.0.0.1` (not `0.0.0.0`) behind a reverse proxy
- [ ] Restrict `CORS_ORIGINS` to your exact production domain
- [ ] Run with multiple workers: `uvicorn app.main:app --workers 4`
- [ ] Remove or change seed data credentials
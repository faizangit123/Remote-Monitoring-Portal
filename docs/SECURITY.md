# Security Policy

## Overview

The Remote Monitoring Portal is a privileged-access system. Agents run on production machines, the backend holds credentials, and the frontend exposes real-time process-level data. This document describes the security model, known limitations, and responsible disclosure process.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |
| < 1.0   | ❌ No      |

Only the latest release on the `main` branch receives security patches.

---

## Architecture & Trust Boundaries

```
[ Windows Agent ]  ──── WebSocket (token auth) ────▶  [ FastAPI Backend :8000 ]
                                                              │
[ React Frontend :5173 ] ── JWT (Bearer token) ─────────────┘
                          (proxied via Vite in dev)
```

There are three principals with distinct trust levels:

| Principal       | Auth Method         | Trust Level                          |
|----------------|---------------------|--------------------------------------|
| Admin user      | JWT (bcrypt login)  | Full — manages users, agents, commands |
| Regular user    | JWT (bcrypt login)  | Read-only — assigned agents only       |
| Windows agent   | Pre-shared token    | Write to own data only                |

---

## Authentication

### User Login
- Passwords are hashed with **bcrypt** before storage — plain-text passwords are never persisted.
- JWT tokens use **HS256** signing with a secret key defined in `settings.SECRET_KEY`.
- Tokens expire after **7 days**. There is no refresh endpoint — expiry requires re-login.
- On 401 responses, the frontend automatically clears the token and redirects to `/login`.

### Agent Tokens
- Each agent authenticates with a unique pre-shared token generated via `/api/agents/generate-token`.
- Tokens are stored in the agent's local `config.json` — restrict file permissions on the agent machine (`chmod 600 config.json` on Linux; restricted ACL on Windows).
- A compromised agent token allows data writes for that agent only — it cannot read other agents or access user data.

### ⚠️ Known Limitation
JWT signing uses a symmetric secret (`SECRET_KEY`). If this value is leaked, all tokens can be forged. Rotate it immediately if compromised — all existing sessions will be invalidated.

---

## Authorization

Role-based access control is enforced server-side on every request.

| Endpoint                        | Admin | User |
|---------------------------------|-------|------|
| `GET /api/agents/`              | All agents | Assigned only |
| `POST /api/agents/register`     | ✅    | ❌   |
| `DELETE /api/agents/:id`        | ✅    | ❌   |
| `GET /api/users/`               | ✅    | ❌   |
| `POST /api/commands/`           | ✅    | ❌   |
| `GET /api/agents/:id/processes` | ✅    | Assigned only |

Never rely on frontend-side role checks as a security boundary — they exist for UX only. All enforcement happens in the FastAPI routers.

---

## Transport Security

### Development
- The Vite dev server proxies all `/api` and `/ws` requests to `localhost:8000`, so no credentials cross the network.
- Do **not** expose port 8000 directly on a networked interface in dev — bind to `127.0.0.1` only.

### Production Requirements
- **TLS is mandatory.** Deploy behind a reverse proxy (nginx, Caddy) with a valid certificate.
- Set `Secure` and `HttpOnly` flags if migrating from `localStorage` to cookie-based token storage.
- Restrict `allow_origins` in CORS to your exact production domain — never use `"*"` with `allow_credentials=True`.
- WebSocket connections (`wss://`) must also go through TLS in production.

---

## Sensitive Configuration

| Variable            | Location                  | Risk if leaked                        |
|--------------------|--------------------------|---------------------------------------|
| `SECRET_KEY`        | Backend `.env` / settings | JWT forgery — rotate immediately      |
| `DATABASE_URL`      | Backend `.env` / settings | Full data access                      |
| Agent token         | Agent `config.json`       | Agent impersonation / data injection  |
| `access_token`      | Browser `localStorage`    | Session hijacking (XSS risk)          |

### Recommendations
- Never commit `.env` files. Add them to `.gitignore` immediately if not already present.
- Use a secrets manager (AWS Secrets Manager, Vault, etc.) in production rather than `.env` files.
- `localStorage` is readable by any JavaScript on the page. If XSS is a concern, migrate token storage to `HttpOnly` cookies.

---

## Command Execution Risk

The `kill_process` command sends a PID to the agent and terminates it via `psutil`. This is a **destructive, irreversible action**.

- Only admin users can send commands — enforce this both in the router and the WebSocket handler.
- Consider adding a confirmation step in the UI before dispatching `kill_process`.
- Log all commands to the database with the issuing user ID, timestamp, and outcome. This is already in the schema — ensure it's being written reliably.
- If you expand the command surface (e.g., `run_script`, `reboot`), treat each new command type as a new security boundary and review accordingly.

---

## Input Validation

- All request bodies are validated by **Pydantic** models on the FastAPI side.
- Agent-submitted data (system info, processes) should be treated as **untrusted input** — it comes from a remote machine and could be tampered with. Validate types and reasonable value ranges before storing.
- The process list from the agent includes user-controlled fields like process names. Do not render them as raw HTML — React's JSX escapes strings by default, but be careful with `dangerouslySetInnerHTML`.

---

## Dependency Security

Regularly audit dependencies for known vulnerabilities:

```bash
# Python backend
pip-audit

# Node frontend
npm audit
```

Pin dependency versions in `requirements.txt` and `package.json` for reproducible builds. Update packages on a scheduled cadence — at minimum when a CVE is published for a direct dependency.

---

## Reporting a Vulnerability

If you discover a security issue in this project, **please do not open a public GitHub issue.**

Instead, report it privately by emailing the maintainer or opening a [GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) on the repository.

Please include:
- A clear description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix if you have one

You can expect an acknowledgement within **48 hours** and a patch or mitigation plan within **7 days** for critical issues. Non-critical issues will be addressed in the next scheduled release.

---

## Security Checklist (Pre-Deployment)

- [ ] `SECRET_KEY` is a long random string, not the development default
- [ ] `.env` is in `.gitignore` and has never been committed
- [ ] CORS `allow_origins` is set to the exact production domain
- [ ] Backend bound to `127.0.0.1` behind a TLS-terminating reverse proxy
- [ ] Agent `config.json` has restricted file permissions
- [ ] All agent tokens are unique per machine
- [ ] `npm audit` and `pip-audit` show no high/critical CVEs
- [ ] Command logging is verified to be writing to the database
- [ ] Default seed credentials (`admin/admin123`, `user1/user123`) have been removed or changed
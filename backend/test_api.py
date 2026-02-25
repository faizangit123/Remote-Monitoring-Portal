# backend/test_api.py
"""
Integration Test Script
Tests all major API flows against a running backend.

Run with:
    cd backend
    python test_api.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"
PASS = "✅"
FAIL = "❌"

results = {"passed": 0, "failed": 0}


def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS} {label}")
        results["passed"] += 1
    else:
        print(f"  {FAIL} {label}" + (f" — {detail}" if detail else ""))
        results["failed"] += 1


def section(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


# ==============================================
# 1. AUTH TESTS
# ==============================================

section("1. Authentication")

# Login as admin
r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "admin",
    "password": "admin123"
})
check("Admin login returns 200", r.status_code == 200, r.text)
admin_token = r.json().get("access_token", "") if r.status_code == 200 else ""
check("Admin token returned", bool(admin_token))

ADMIN_HEADERS = {"Authorization": f"Bearer {admin_token}"}

# Login as regular user
r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "testuser",
    "password": "testuser123"
})
check("User login returns 200", r.status_code == 200)
user_token = r.json().get("access_token", "") if r.status_code == 200 else ""
USER_HEADERS = {"Authorization": f"Bearer {user_token}"}

# Wrong password
r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "admin",
    "password": "wrongpassword"
})
check("Wrong password returns 401", r.status_code == 401)

# /me endpoint
r = requests.get(f"{BASE_URL}/api/auth/me", headers=ADMIN_HEADERS)
check("/me returns correct username", r.status_code == 200 and r.json().get("username") == "admin")

# No token
r = requests.get(f"{BASE_URL}/api/auth/me")
check("No token returns 401", r.status_code == 401)


# ==============================================
# 2. USER MANAGEMENT TESTS
# ==============================================

section("2. User Management")

# List users (admin)
r = requests.get(f"{BASE_URL}/api/users/", headers=ADMIN_HEADERS)
check("Admin can list users", r.status_code == 200)
check("Returns at least 3 users", len(r.json()) >= 3)

# List users (regular user — should be forbidden)
r = requests.get(f"{BASE_URL}/api/users/", headers=USER_HEADERS)
check("Regular user cannot list all users (403)", r.status_code == 403)

# Create new user
r = requests.post(f"{BASE_URL}/api/users/", headers=ADMIN_HEADERS, json={
    "username": "testuser_temp",
    "email": "temp@example.com",
    "password": "temp123",
    "role": "user"
})
check("Admin can create user", r.status_code in [200, 201])
new_user_id = r.json().get("id") if r.status_code in [200, 201] else None

# Delete the temp user
if new_user_id:
    r = requests.delete(f"{BASE_URL}/api/users/{new_user_id}", headers=ADMIN_HEADERS)
    check("Admin can delete user", r.status_code in [200, 204])


# ==============================================
# 3. AGENT TESTS
# ==============================================

section("3. Agents")

# List agents (admin sees all)
r = requests.get(f"{BASE_URL}/api/agents/", headers=ADMIN_HEADERS)
check("Admin can list agents", r.status_code == 200)
agents = r.json() if r.status_code == 200 else []
check("Returns at least 3 agents", len(agents) >= 3)

# List agents (regular user sees only assigned)
r = requests.get(f"{BASE_URL}/api/agents/", headers=USER_HEADERS)
check("User gets agents list", r.status_code == 200)
user_agents = r.json() if r.status_code == 200 else []
check("testuser sees only 2 agents (assigned)", len(user_agents) == 2, f"got {len(user_agents)}")

# Get specific agent
if agents:
    agent_id = agents[0]["id"]
    r = requests.get(f"{BASE_URL}/api/agents/{agent_id}", headers=ADMIN_HEADERS)
    check("Can fetch single agent by ID", r.status_code == 200)

    # System data history
    r = requests.get(f"{BASE_URL}/api/agents/{agent_id}/system-data", headers=ADMIN_HEADERS)
    check("Can fetch agent system data", r.status_code == 200)
    check("System data has records", len(r.json()) > 0)

    # Processes
    r = requests.get(f"{BASE_URL}/api/agents/{agent_id}/processes", headers=ADMIN_HEADERS)
    check("Can fetch agent processes", r.status_code == 200)

# Register new agent
r = requests.post(f"{BASE_URL}/api/agents/register", headers=ADMIN_HEADERS, json={
    "agent_id": "agent-test-999",
    "hostname": "TEST-MACHINE",
    "ip_address": "10.0.0.99",
    "os_info": "Windows 10",
    "token": "test-token-unique-abc123xyz"
})
check("Admin can register new agent", r.status_code in [200, 201])
new_agent_id = r.json().get("id") if r.status_code in [200, 201] else None

# Delete temp agent
if new_agent_id:
    r = requests.delete(f"{BASE_URL}/api/agents/{new_agent_id}", headers=ADMIN_HEADERS)
    check("Admin can delete agent", r.status_code in [200, 204])


# ==============================================
# 4. COMMANDS TESTS
# ==============================================

section("4. Commands")

if agents:
    agent_id = agents[0]["id"]

    # Send a command
    r = requests.post(f"{BASE_URL}/api/commands/", headers=ADMIN_HEADERS, json={
        "agent_id": agent_id,
        "command_type": "refresh_data",
        "command_data": {}
    })
    check("Admin can send command", r.status_code in [200, 201])
    cmd_id = r.json().get("id") if r.status_code in [200, 201] else None

    # List commands
    r = requests.get(f"{BASE_URL}/api/commands/", headers=ADMIN_HEADERS)
    check("Admin can list commands", r.status_code == 200)

    # Commands for specific agent
    r = requests.get(f"{BASE_URL}/api/commands/agent/{agent_id}", headers=ADMIN_HEADERS)
    check("Can list commands for agent", r.status_code == 200)


# ==============================================
# 5. WEBSOCKET SMOKE TEST
# ==============================================

section("5. WebSocket")

try:
    import websocket as ws_lib
    HAS_WS = True
except ImportError:
    HAS_WS = False

if not HAS_WS:
    print(f"  ⚠️  websocket-client not installed — skipping WS tests")
    print(f"     Install with: pip install websocket-client")
else:
    import websocket
    import threading
    import time

    ws_result = {"connected": False, "message": None}

    def on_open(ws):
        ws_result["connected"] = True
        ws.close()

    def on_message(ws, msg):
        ws_result["message"] = msg

    def on_error(ws, err):
        ws_result["error"] = str(err)

    # Test client WebSocket (needs a valid agent_id)
    if agents:
        first_agent_id = agents[0]["agent_id"]
        try:
            ws_app = websocket.WebSocketApp(
                f"ws://localhost:8000/ws/client/{first_agent_id}?token={admin_token}",
                on_open=on_open,
                on_message=on_message,
            )
            t = threading.Thread(target=ws_app.run_forever)
            t.daemon = True
            t.start()
            time.sleep(2)
            check("Client WebSocket connects successfully", ws_result["connected"])
        except Exception as e:
            check("Client WebSocket connects successfully", False, str(e))


# ==============================================
# SUMMARY
# ==============================================

section("RESULTS")
total = results["passed"] + results["failed"]
print(f"  Passed: {results['passed']}/{total}")
print(f"  Failed: {results['failed']}/{total}")

if results["failed"] == 0:
    print(f"\n  {PASS} All tests passed! Ready for Phase 8.")
else:
    print(f"\n  {FAIL} Fix failing tests before proceeding.")

sys.exit(0 if results["failed"] == 0 else 1)
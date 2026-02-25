# 📡 API Documentation

Complete REST API documentation for the Remote Monitoring Portal backend.

**Base URL**: `http://localhost:8000`  
**Interactive Docs**: http://localhost:8000/docs

All endpoints except `/api/auth/login` and `/api/auth/register` require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication

### POST `/api/auth/login`

Login and receive JWT token.

**Request Body** (form-urlencoded):
```
username=admin
password=admin123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401` - Wrong username or password
- `403` - Account disabled

---

### GET `/api/auth/me`

Get current user information.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T08:00:00"
}
```

**Errors**:
- `401` - Invalid or expired token

---

### POST `/api/auth/register`

Register a new user (admin only).

**Headers**:
```
Authorization: Bearer <admin_token>
```

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "pass123",
  "role": "user"
}
```

**Response** (201 Created):
```json
{
  "id": 3,
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

**Errors**:
- `400` - Username or email already exists
- `403` - Not admin

---

## 👥 Users

### GET `/api/users/`

List all users (admin only).

**Query Parameters**:
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100) - Max results

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T08:00:00"
  }
]
```

---

### GET `/api/users/{user_id}`

Get specific user details (admin only).

**Response** (200 OK):
```json
{
  "id": 2,
  "username": "testuser_1",
  "email": "testuser@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T08:15:00"
}
```

**Errors**:
- `404` - User not found

---

### PUT `/api/users/{user_id}`

Update user (admin only).

**Request Body** (all fields optional):
```json
{
  "email": "newemail@example.com",
  "role": "admin",
  "is_active": false
}
```

**Response** (200 OK): Updated user object

---

### DELETE `/api/users/{user_id}`

Delete user (admin only).

**Response** (200 OK):
```json
{
  "message": "User deleted successfully",
  "success": true
}
```

---

## 🖥️ Agents

### GET `/api/agents/`

List agents.
- Admins see ALL agents
- Regular users see only ASSIGNED agents

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "agent_id": "agent-001",
    "hostname": "DESKTOP-ABC123",
    "ip_address": "192.168.1.100",
    "status": "online",
    "last_seen": "2024-01-15T10:35:00",
    "created_at": "2024-01-01T08:00:00"
  }
]
```

---

### GET `/api/agents/{agent_id}`

Get agent details.

**Response** (200 OK):
```json
{
  "id": 1,
  "agent_id": "agent-001",
  "hostname": "DESKTOP-ABC123",
  "ip_address": "192.168.1.100",
  "status": "online",
  "last_seen": "2024-01-15T10:35:00",
  "created_at": "2024-01-01T08:00:00"
}
```

**Errors**:
- `403` - No access to this agent
- `404` - Agent not found

---

### POST `/api/agents/register`

Register a new agent (admin only).

**Request Body**:
```json
{
  "agent_id": "agent-003",
  "hostname": "SERVER-MAIN",
  "ip_address": "192.168.1.102",
  "token": "long-secure-random-token-here"
}
```

**Response** (201 Created): Created agent object

**Note**: Use `GET /api/agents/generate-token` to get a secure token.

---

### GET `/api/agents/generate-token`

Generate a secure random token for new agent (admin only).

**Response** (200 OK):
```json
{
  "token": "a3f8b2c9d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
}
```

---

### GET `/api/agents/{agent_id}/system-data`

Get latest system information for agent.

**Response** (200 OK):
```json
{
  "id": 123,
  "agent_id": 1,
  "os_name": "Windows 10",
  "os_version": "10.0.19044",
  "cpu_model": "Intel Core i7-9700K",
  "cpu_cores": 8,
  "cpu_usage_percent": 45.2,
  "ram_total_gb": 16.0,
  "ram_used_gb": 8.5,
  "ram_usage_percent": 53.1,
  "disk_total_gb": 500.0,
  "disk_used_gb": 300.0,
  "disk_usage_percent": 60.0,
  "uptime_hours": 72.5,
  "collected_at": "2024-01-15T10:35:00"
}
```

Returns `null` if agent hasn't sent data yet.

---

### GET `/api/agents/{agent_id}/history`

Get historical system data for charts.

**Query Parameters**:
- `limit` (int, default: 50) - Number of historical records

**Response** (200 OK): Array of system data objects (newest first)

---

### GET `/api/agents/{agent_id}/processes`

Get running processes on agent.

**Response** (200 OK):
```json
[
  {
    "id": 456,
    "agent_id": 1,
    "pid": 1234,
    "name": "chrome.exe",
    "cpu_percent": 5.2,
    "memory_mb": 250.5,
    "status": "running",
    "username": "User",
    "collected_at": "2024-01-15T10:35:00"
  }
]
```

---

## 📡 Commands

### POST `/api/commands/`

Send command to agent (admin only).

**Request Body**:
```json
{
  "agent_id": 1,
  "command_type": "refresh_data"
}
```

Or with parameters:
```json
{
  "agent_id": 1,
  "command_type": "kill_process",
  "command_data": {"pid": 1234}
}
```

**Available Commands**:
- `refresh_data` - Agent sends fresh data immediately
- `kill_process` - Terminate process (requires `{"pid": number}`)
- `get_processes` - Agent sends fresh process list

**Response** (201 Created):
```json
{
  "id": 1,
  "agent_id": 1,
  "user_id": 1,
  "command_type": "refresh_data",
  "command_data": null,
  "status": "pending",
  "result": null,
  "created_at": "2024-01-15T10:40:00",
  "executed_at": null
}
```

---

### GET `/api/commands/agent/{agent_id}`

Get commands for a specific agent.

**Query Parameters**:
- `status_filter` (string, optional) - Filter by: "pending", "executed", "failed"
- `limit` (int, default: 50)

**Response** (200 OK): Array of command objects

---

## 🔌 WebSocket Endpoints

### WS `/ws/agent/{agent_id}?token={agent_token}`

WebSocket endpoint for Windows agents.

**Authentication**: Via query parameter `token`

**Messages from Agent**:
```json
{
  "type": "system_data",
  "data": { /* system info */ }
}

{
  "type": "processes",
  "data": [ /* process list */ ]
}

{
  "type": "command_result",
  "command_id": 1,
  "success": true,
  "result": "Process terminated"
}

{
  "type": "heartbeat"
}
```

**Messages to Agent**:
```json
{
  "type": "command",
  "command_id": 1,
  "command_type": "refresh_data",
  "command_data": {}
}

{
  "type": "pong"
}
```

---

### WS `/ws/client/{agent_id}?token={jwt_token}`

WebSocket endpoint for browsers watching an agent.

**Authentication**: Via query parameter `token` (JWT)

**Messages from Backend**:
```json
{
  "type": "connected",
  "agent_id": "agent-001",
  "agent_status": "online"
}

{
  "type": "system_data_update",
  "data": { /* fresh system data */ }
}

{
  "type": "processes_update",
  "data": [ /* process list */ ]
}

{
  "type": "agent_status",
  "status": "offline"
}
```

---

## 🚨 Error Responses

All endpoints use standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (bad/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation failed)
- `500` - Internal Server Error

Error response format:
```json
{
  "detail": "Error message here"
}
```

---

## 🔧 Rate Limiting

Currently no rate limiting implemented. Consider adding for production:
- Login attempts: 5 per minute
- API calls: 100 per minute per user
- WebSocket connections: 10 per user

---

## 📊 Response Pagination

For endpoints returning lists, use `skip` and `limit`:
```
GET /api/users/?skip=0&limit=10   # First 10
GET /api/users/?skip=10&limit=10  # Next 10
```

---

**For more details, see the interactive API docs at** http://localhost:8000/docs
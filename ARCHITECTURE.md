# Remote Monitoring Portal - Complete Architecture Design
## System Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                     REMOTE MONITORING PORTAL                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Windows Agent   │◄───────►│   Backend API    │◄───────►│  Web Frontend    │
│     (.exe)       │ WebSocket│  (FastAPI+WS)   │   HTTP  │ (React+Vite+CSS) │
└──────────────────┘         └──────────────────┘         └──────────────────┘
        │                             │                            │
        │                             ▼                            │
        │                    ┌──────────────────┐                  │
        │                    │    Database      │                  │
        │                    │   (SQLite)       │                  │
        │                    └──────────────────┘                  │
        │                                                          │
        └───────────────── Real-time Updates ─────────────────────-┘
```

## Technology Stack

### 1. Backend Server
- **Framework**: FastAPI (Python 3.9+)
- **WebSocket**: FastAPI WebSocket support
- **Database**: SQLAlchemy ORM + SQLite
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt
- **Validation**: Pydantic models

### 2. Frontend Portal
- **Framework**: React.js 18+
- **Build Tool**: Vite
- **Language**: JavaScript (JSX)
- **Styling**: Pure CSS (separate .css file for each component)
- **State Management**: React Context API
- **WebSocket Client**: native WebSocket API
- **HTTP Client**: Axios

### 3. Windows Agent
- **Language**: Python 3.9+
- **System Info**: psutil library
- **WebSocket Client**: websockets library
- **Compilation**: PyInstaller
- **Configuration**: JSON config file

## Directory Structure

```
remote-monitoring-portal/
│
├── backend/                    # Backend API Server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── auth.py            # Authentication logic
│   │   ├── crud.py            # Database operations
│   │   ├── websocket.py       # WebSocket handlers
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py        # Auth endpoints
│   │       ├── agents.py      # Agent management
│   │       ├── users.py       # User management
│   │       └── commands.py    # Command endpoints
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── frontend/                   # React Web Portal
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── assets/
│   │   │   └── logo.png
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Login.css
│   │   │   │   ├── ProtectedRoute.jsx
│   │   │   │   └── ProtectedRoute.css
│   │   │   ├── Dashboard/
│   │   │   │   ├── AdminDashboard.jsx
│   │   │   │   ├── AdminDashboard.css
│   │   │   │   ├── UserDashboard.jsx
│   │   │   │   ├── UserDashboard.css
│   │   │   │   ├── AgentList.jsx
│   │   │   │   └── AgentList.css
│   │   │   ├── Agent/
│   │   │   │   ├── AgentDetails.jsx
│   │   │   │   ├── AgentDetails.css
│   │   │   │   ├── ProcessList.jsx
│   │   │   │   ├── ProcessList.css
│   │   │   │   ├── StorageInfo.jsx
│   │   │   │   ├── StorageInfo.css
│   │   │   │   ├── NetworkInfo.jsx
│   │   │   │   ├── NetworkInfo.css
│   │   │   │   ├── SystemUsers.jsx
│   │   │   │   └── SystemUsers.css
│   │   │   ├── Common/
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── Navbar.css
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Sidebar.css
│   │   │   └── UserManagement/
│   │   │       ├── UserList.jsx
│   │   │       ├── UserList.css
│   │   │       ├── CreateUser.jsx
│   │   │       └── CreateUser.css
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── WebSocketContext.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── utils/
│   │   │   └── helpers.js
│   │   ├── styles/
│   │   │   ├── global.css         # Global styles
│   │   │   └── variables.css      # CSS variables (colors, fonts)
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── .env
│   └── README.md
│
├── agent/                      # Windows Agent
│   ├── agent.py               # Main agent code
│   ├── system_monitor.py      # System monitoring functions
│   ├── websocket_client.py    # WebSocket client handler
│   ├── config.json            # Agent configuration
│   ├── requirements.txt
│   ├── build.py               # PyInstaller build script
│   ├── agent.spec             # PyInstaller spec file
│   └── README.md
│
├── database/
│   ├── schema.sql             # Database schema
│   └── ER_diagram.md          # ER diagram (text format)
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── SETUP_GUIDE.md
│   └── SECURITY.md
│
├── ARCHITECTURE.md            # This file
└── README.md                  # Main project README
```

## Database Schema (SQLite)

### Tables:

#### 1. users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

#### 2. agents
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_token VARCHAR(255) UNIQUE NOT NULL,
    hostname VARCHAR(255),
    ip_address VARCHAR(50),
    os_info TEXT,
    status VARCHAR(20) DEFAULT 'offline' CHECK(status IN ('online', 'offline')),
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. agent_data
```sql
CREATE TABLE agent_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    data_type VARCHAR(50) NOT NULL CHECK(data_type IN ('system_info', 'processes', 'storage', 'network', 'users', 'applications')),
    data_json TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);
```

#### 4. user_agent_access
```sql
CREATE TABLE user_agent_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    access_level VARCHAR(20) DEFAULT 'read' CHECK(access_level IN ('read', 'write')),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE(user_id, agent_id)
);
```

#### 5. commands
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    command_type VARCHAR(50) NOT NULL,
    command_params TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'completed', 'failed')),
    sent_by INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    FOREIGN KEY (sent_by) REFERENCES users(id)
);
```

### Indexes for Performance:
```sql
CREATE INDEX idx_agent_data_agent_id ON agent_data(agent_id);
CREATE INDEX idx_agent_data_type ON agent_data(data_type);
CREATE INDEX idx_agent_data_timestamp ON agent_data(timestamp);
CREATE INDEX idx_commands_agent_id ON commands(agent_id);
CREATE INDEX idx_commands_status ON commands(status);
CREATE INDEX idx_user_agent_access_user_id ON user_agent_access(user_id);
CREATE INDEX idx_user_agent_access_agent_id ON user_agent_access(agent_id);
```

## API Endpoints

### Authentication
```
POST   /api/auth/login          # User login
POST   /api/auth/register       # Register new user (admin only)
POST   /api/auth/refresh        # Refresh JWT token
GET    /api/auth/me             # Get current user info
```

### Agents
```
GET    /api/agents              # Get all agents (admin) or assigned agents (user)
GET    /api/agents/{agent_id}   # Get specific agent details
POST   /api/agents/register     # Register new agent (admin only)
DELETE /api/agents/{agent_id}   # Delete agent (admin only)
GET    /api/agents/{agent_id}/data/{data_type}  # Get agent data
```

### Commands
```
POST   /api/commands/send       # Send command to agent (admin only)
GET    /api/commands/{command_id}  # Get command status
GET    /api/commands/agent/{agent_id}  # Get all commands for agent
```

### Users
```
GET    /api/users               # Get all users (admin only)
POST   /api/users               # Create user (admin only)
PUT    /api/users/{user_id}     # Update user (admin only)
DELETE /api/users/{user_id}     # Delete user (admin only)
POST   /api/users/{user_id}/assign-agent  # Assign agent to user
```

### WebSocket Endpoints
```
WS     /ws/agent/{agent_id}     # Agent WebSocket connection
WS     /ws/portal/{user_id}     # Portal WebSocket connection
```

## WebSocket Message Protocol

### Agent → Backend Messages

#### 1. Authentication
```json
{
  "type": "auth",
  "token": "agent_secret_token",
  "agent_id": "agent-001"
}
```

#### 2. Heartbeat
```json
{
  "type": "heartbeat",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 3. Data Update
```json
{
  "type": "data_update",
  "data_type": "system_info",
  "data": {
    "os": "Windows 11 Pro",
    "os_version": "10.0.22631",
    "hostname": "DESKTOP-ABC123",
    "ip_address": "192.168.1.100",
    "cpu_model": "Intel Core i7-10700K",
    "cpu_cores": 8,
    "cpu_threads": 16,
    "cpu_percent": 45.2,
    "ram_total_gb": 16.0,
    "ram_used_gb": 8.5,
    "ram_percent": 53.1,
    "boot_time": "2024-01-01T08:00:00Z",
    "uptime_hours": 4.5
  }
}
```

#### 4. Process Data
```json
{
  "type": "data_update",
  "data_type": "processes",
  "data": [
    {
      "pid": 1234,
      "name": "chrome.exe",
      "cpu_percent": 5.2,
      "memory_mb": 256.5,
      "status": "running",
      "username": "user1"
    }
  ]
}
```

#### 5. Storage Data
```json
{
  "type": "data_update",
  "data_type": "storage",
  "data": [
    {
      "device": "C:",
      "mountpoint": "C:\\",
      "fstype": "NTFS",
      "total_gb": 500.0,
      "used_gb": 300.0,
      "free_gb": 200.0,
      "percent": 60.0
    }
  ]
}
```

#### 6. Network Data
```json
{
  "type": "data_update",
  "data_type": "network",
  "data": {
    "connections": [
      {
        "fd": 12,
        "family": "AF_INET",
        "type": "SOCK_STREAM",
        "local_address": "192.168.1.100",
        "local_port": 54321,
        "remote_address": "93.184.216.34",
        "remote_port": 443,
        "status": "ESTABLISHED",
        "pid": 1234
      }
    ],
    "interfaces": [
      {
        "name": "Ethernet",
        "address": "192.168.1.100",
        "netmask": "255.255.255.0",
        "broadcast": "192.168.1.255"
      }
    ]
  }
}
```

#### 7. System Users Data
```json
{
  "type": "data_update",
  "data_type": "users",
  "data": [
    {
      "name": "Administrator",
      "terminal": null,
      "host": "localhost",
      "started": "2024-01-01T08:00:00Z"
    }
  ]
}
```

#### 8. Installed Applications
```json
{
  "type": "data_update",
  "data_type": "applications",
  "data": [
    {
      "name": "Google Chrome",
      "version": "120.0.6099.129",
      "publisher": "Google LLC",
      "install_date": "2023-12-01"
    }
  ]
}
```

#### 9. Command Result
```json
{
  "type": "command_result",
  "command_id": 123,
  "status": "completed",
  "result": "Process 1234 terminated successfully",
  "timestamp": "2024-01-01T12:05:00Z"
}
```

### Backend → Agent Messages

#### 1. Authentication Success
```json
{
  "type": "auth_success",
  "agent_id": "agent-001",
  "message": "Authentication successful"
}
```

#### 2. Authentication Failed
```json
{
  "type": "auth_failed",
  "reason": "Invalid token"
}
```

#### 3. Command: Refresh Data
```json
{
  "type": "command",
  "command_id": 123,
  "command_type": "refresh_data",
  "params": {
    "data_types": ["processes", "storage"]
  }
}
```

#### 4. Command: Terminate Process
```json
{
  "type": "command",
  "command_id": 124,
  "command_type": "terminate_process",
  "params": {
    "pid": 1234
  }
}
```

#### 5. Ping/Pong
```json
{
  "type": "ping"
}
```

### Portal → Backend Messages

#### 1. Authentication
```json
{
  "type": "auth",
  "token": "jwt_token_here"
}
```

#### 2. Subscribe to Agent
```json
{
  "type": "subscribe_agent",
  "agent_id": "agent-001"
}
```

#### 3. Unsubscribe from Agent
```json
{
  "type": "unsubscribe_agent",
  "agent_id": "agent-001"
}
```

### Backend → Portal Messages

#### 1. Agent Status Update
```json
{
  "type": "agent_status",
  "agent_id": "agent-001",
  "status": "online",
  "last_seen": "2024-01-01T12:00:00Z"
}
```

#### 2. Agent Data Update
```json
{
  "type": "agent_data",
  "agent_id": "agent-001",
  "data_type": "processes",
  "data": [...]
}
```

#### 3. Command Update
```json
{
  "type": "command_update",
  "command_id": 123,
  "status": "completed",
  "result": "Success"
}
```

## Security Implementation

### 1. Password Security
- **Hashing Algorithm**: bcrypt with cost factor 12
- **Salt**: Automatically generated per password
- **Storage**: Only hash stored, never plain text

### 2. JWT Tokens (Portal Users)
- **Algorithm**: HS256
- **Expiry**: 7 days (10,080 minutes)
- **Payload**: user_id, username, role, exp
- **Secret**: Stored in environment variable

### 3. Agent Authentication
- **Method**: Pre-shared token
- **Storage**: config.json (agent), database (backend)
- **Validation**: On WebSocket connection + heartbeat

### 4. Role-Based Access Control (RBAC)
```python
Permissions:
- Admin:
  - view_all_agents
  - manage_users
  - send_commands
  - delete_agents
  - create_agents

- User:
  - view_assigned_agents (only)
  - read_only_access
  - no_command_sending
```

### 5. Input Validation
- **Backend**: Pydantic models for all inputs
- **Frontend**: HTML5 validation + JavaScript checks
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **XSS**: React auto-escaping

### 6. CORS Configuration
- **Allowed Origins**: Only frontend URL
- **Methods**: GET, POST, PUT, DELETE
- **Headers**: Authorization, Content-Type

## CSS Architecture (Pure CSS)

### Global Variables (variables.css)
```css
:root {
  /* Colors */
  --primary-color: #3b82f6;
  --secondary-color: #6366f1;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #06b6d4;
  
  /* Neutral Colors */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Typography */
  --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### Component CSS Organization
Each component has its own CSS file with:
1. Component-specific styles
2. BEM naming convention (Block-Element-Modifier)
3. Responsive design with media queries
4. No global scope pollution

### Example Component Structure:
```
Login.jsx       → Login logic
Login.css       → Login styles only
```

## Development Workflow

### Backend Development
```bash
cd backend

venv\Scripts\activate

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

npm run dev
```

### Agent Development
```bash
cd agent

venv\Scripts\activate

python agent.py
```

### Build Agent Executable
```bash
python build.py

pyinstaller --onefile --noconsole agent.py
```

## Performance Considerations

1. **Database**:
   - Indexes on foreign keys and frequently queried columns
   - Data retention: Keep agent_data for 30 days only
   - Batch inserts for multiple data points

2. **WebSocket**:
   - Heartbeat every 30 seconds to detect disconnections
   - Auto-reconnect with exponential backoff
   - Message queuing for offline agents

3. **Frontend**:
   - React.memo for expensive components
   - Virtual scrolling for large lists (>1000 items)
   - Debounce search/filter inputs
   - Lazy loading for routes

4. **Agent**:
   - Efficient psutil queries (avoid full system scans)
   - Data collection interval: 30 seconds (configurable)
   - Compress large data before sending

## Error Handling

### Backend
- Try-catch blocks around all operations
- Proper HTTP status codes
- Detailed error messages in development
- Generic messages in production
- Logging to file

### Frontend
- Error boundaries for component errors
- Toast notifications for API errors
- Fallback UI for failed data loads
- Reconnection logic for WebSocket

### Agent
- Auto-reconnect on disconnect
- Retry failed commands
- Log errors locally
- Continue operation even if one data collection fails

This architecture ensures a robust, secure, and scalable remote monitoring system!
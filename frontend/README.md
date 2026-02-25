# 🖥️ Remote Monitoring Portal

A comprehensive Python-based remote monitoring system for Windows machines with real-time WebSocket updates, role-based access control, and beautiful dark-themed UI.

## 📸 Screenshots

![Dashboard](docs/images/dashboard.png)
*Admin dashboard showing all monitored agents*

![Agent Details](docs/images/agent-details.png)
*Real-time system monitoring with live charts*

## ✨ Features

### 🔐 Security & Authentication
- JWT-based authentication
- Role-based access control (Admin / User)
- Bcrypt password hashing
- Token-based agent authentication
- Pydantic input validation

### 📊 Real-Time Monitoring
- Live CPU/RAM/Disk usage charts
- Running processes with kill capability
- Network interface statistics
- Active user sessions
- Disk partition information

### 💻 Windows Agent
- Lightweight Python agent
- Compiles to standalone .exe
- Configurable data collection intervals
- Auto-reconnect on disconnect
- Minimal resource usage

### 🎨 Modern UI
- Dark mission-control theme
- Pure CSS (no frameworks)
- Real-time WebSocket updates
- Responsive design
- Interactive charts (Recharts)

## 🏗️ Architecture
```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  Windows Agent   │◄───────►│   Backend API    │◄───────►│   Web Portal     │
│     (.exe)       │ WebSocket│  (FastAPI + WS) │   HTTP  │  (React + Vite)  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  SQLite Database │
                             └──────────────────┘
```

**Technology Stack:**
- **Backend**: FastAPI + SQLAlchemy + SQLite + WebSocket
- **Frontend**: React 18 + Vite + Pure CSS + Recharts
- **Agent**: Python + psutil + websockets → PyInstaller
- **Auth**: JWT tokens + bcrypt

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Windows (for the agent)

### 1️⃣ Start Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Seed database with test users
python seed_data.py

# Start server
uvicorn app.main:app --reload --port 8000
```

**Backend runs at**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

### 2️⃣ Start Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend runs at**: http://localhost:5173

### 3️⃣ Start Agent
```bash
cd agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure agent (edit config.py if needed)
# Default connects to localhost:8000

# Run agent
python main.py
```

### 4️⃣ Login

Open http://localhost:5173 and login with:



## 📁 Project Structure
```
remote-monitoring-portal/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py       # App entry point
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── auth.py       # Authentication
│   │   ├── crud.py       # Database operations
│   │   └── routers/      # API routes
│   ├── seed_data.py      # Database seeder
│   └── requirements.txt
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── context/      # Auth & WebSocket contexts
│   │   ├── services/     # API & WebSocket clients
│   │   ├── utils/        # Helper functions
│   │   └── styles/       # Global CSS
│   ├── package.json
│   └── vite.config.js
│
├── agent/                # Windows agent
│   ├── main.py           # Agent entry point
│   ├── collector.py      # System data collection
│   ├── websocket_client.py # WebSocket client
│   ├── command_handler.py  # Command execution
│   ├── config.py         # Configuration
│   └── requirements.txt
│
└── README.md             # This file
```

## 🔧 Configuration

### Backend Configuration

Create `backend/.env`:
```env
DATABASE_URL=sqlite:///./monitoring.db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Agent Configuration

Edit `agent/config.py`:
```python
class AgentConfig:
    SERVER_HOST = "localhost"  # Backend server IP/domain
    SERVER_PORT = 8000         # Backend server port
    AGENT_ID = "agent-001"     # Unique agent identifier
    AGENT_TOKEN = "your-agent-token"  # From agent registration
    COLLECTION_INTERVAL = 30   # Data collection interval (seconds)
```

## 📖 API Documentation

Full API documentation is available at http://localhost:8000/docs when the backend is running.

### Key Endpoints

**Authentication:**
```
POST   /api/auth/login       # Login and get JWT token
GET    /api/auth/me          # Get current user info
POST   /api/auth/register    # Register new user (admin only)
```

**Agents:**
```
GET    /api/agents           # List all agents
GET    /api/agents/{id}      # Get agent details
POST   /api/agents/register  # Register new agent (admin only)
GET    /api/agents/{id}/system-data  # Get latest system data
GET    /api/agents/{id}/processes    # Get process list
```

**Commands:**
```
POST   /api/commands         # Send command to agent
GET    /api/commands/agent/{id}  # Get commands for agent
```

**WebSocket:**
```
WS     /ws/agent/{agent_id}       # Agent connection
WS     /ws/client/{agent_id}      # Browser connection
```

## 🔒 Security

- **Passwords**: Bcrypt hashing with cost factor 12
- **JWT Tokens**: HS256 algorithm, 7-day expiry
- **Agent Auth**: Pre-shared tokens validated on connection
- **RBAC**: Admin/User roles with endpoint-level protection
- **Input Validation**: Pydantic schemas on all inputs
- **SQL Injection**: Prevented via SQLAlchemy ORM
- **XSS**: Prevented via React auto-escaping

## 🏭 Building Agent Executable

To compile the agent to a standalone `.exe`:
```bash
cd agent

# Activate venv
venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile --name "MonitoringAgent" main.py

# Output: agent/dist/MonitoringAgent.exe
```

Copy the `.exe` and `config.py` to target machines.

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_api.py  # Integration tests
```

### Frontend Debugging

Open browser console (F12) and use:
```javascript
debugTools.testAPI()           // Test backend connection
debugTools.testLogin()         // Test login
debugTools.testWebSocket()     // Test WebSocket
debugTools.checkAuthState()    // Check stored auth data
```

## 📊 Database Schema

The system uses SQLite with these main tables:

- **users** - Portal user accounts
- **agents** - Registered monitoring agents
- **system_data** - Historical system metrics
- **processes** - Process snapshots
- **commands** - Commands sent to agents

Full ER diagram available in `database/ER_diagram.md`.

## 🎨 Frontend Architecture

- **Pure CSS** (no Tailwind/Bootstrap) - Each component has its own CSS file
- **Context API** - Global auth and WebSocket state
- **React Router** - Protected routes with role checking
- **Recharts** - Beautiful, responsive charts
- **Axios** - HTTP client with automatic JWT injection

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000
# Kill the process using that port
```

### Frontend CORS errors
```bash
# Check backend/app/main.py has correct CORS origins:
allow_origins=["http://localhost:5173", ...]
```

### Agent can't connect
```bash
# Check agent config matches registered agent:
# - Agent ID must match what you registered in backend
# - Token must match what's in the database
```

### WebSocket not updating
```bash
# Check browser console for WebSocket errors
# Verify vite.config.js has WebSocket proxy configured
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues, questions, or suggestions:
- Open a GitHub issue
- Check existing documentation
- Review API docs at `/docs`

## 🎯 Roadmap

- [ ] Multi-platform agent support (Linux, macOS)
- [ ] Email alerts for critical thresholds
- [ ] Historical data export (CSV, Excel)
- [ ] Custom dashboard widgets
- [ ] Agent groups/tags
- [ ] PostgreSQL support for production
- [ ] Docker deployment
- [ ] Mobile app (React Native)

---

**Built with ❤️ using Python, React, and WebSockets**
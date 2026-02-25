"""
Main FastAPI Application
This is the entry point for the backend server
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .config import settings
from .routers import auth, users, agents, commands, websocket

"""
@asynccontextmanager:
- Runs code on application startup and shutdown
- Used for initialization and cleanup
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("="*50)
    print("🚀 Starting Remote Monitoring Portal Backend")
    print("="*50)
    
    # Initialize database (create tables if they don't exist)
    print("\n📦 Initializing database...")
    init_db()
    
    print(f"\n✅ Server ready on http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API docs:    http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔐 Auth:        /api/auth/login")
    print(f"👥 Users:       /api/users/")
    print(f"🖥️  Agents:      /api/agents/")
    print(f"📡 Commands:    /api/commands/")
    print(f"🔌 WebSocket:   /ws/agent/{{id}} and /ws/client/{{id}}")
    print("="*50 + "\n")
    
    yield  # Server runs here
    
    # Shutdown
    print("\n" + "="*50)
    print("Shutting down server...")
    print("="*50)


# ==============================================
# Create FastAPI Application
# ==============================================

app = FastAPI(
    title="Remote Monitoring Portal API",
    description="API for monitoring Windows agents remotely",
    version="1.0.0",
    lifespan=lifespan  # Use lifespan events
)

# ==============================================
# CORS Configuration
# ==============================================

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins_list,  
#     allow_credentials=True,  
#     allow_methods=["*"],  
#     allow_headers=["*"],  
# )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Which origins can access API
    allow_credentials=True, # Allow cookies and authorization headers
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers
)

# ==============================================
# Include Routers
# ==============================================


# Include all routers
app.include_router(auth.router,          tags=["auth"])       # /api/auth/...
app.include_router(users.router,         tags=["users"])      # /api/users/...
app.include_router(agents.router,        tags=["agents"])     # /api/agents/...
app.include_router(commands.router,      tags=["commands"])   # /api/commands/...
app.include_router(websocket.router,     tags=["websocket"])  # /ws/...

# ==============================================
# Root Endpoints
# ==============================================

@app.get("/")
def root():
    return {
        "message": "Remote Monitoring Portal API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "auth_docs": "/api/auth/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2024-01-15T10:30:00"
    }


# ==============================================
# Error Handlers
# ==============================================

"""
You can add custom error handlers here
For example:

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )
"""

# ==============================================
# Run Server (for development)
# ==============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Auto-reload on code changes (development only!)
        log_level="info"
    )
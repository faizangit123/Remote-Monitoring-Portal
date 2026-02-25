# agent/config.example.py
# ========================
# Copy this file → rename it to config.py
# Fill in your actual values
# NEVER commit config.py (it contains your secret token)
#
# How to copy:
#   Windows: copy config.example.py config.py
#   macOS/Linux: cp config.example.py config.py

class AgentConfig:
    SERVER_HOST = "localhost"       # ← Change to your backend server IP
    SERVER_PORT = 8000              # ← Backend port (default 8000)
    AGENT_ID    = "YOUR-PC-NAME"   # ← Must match agent registered in database
    AGENT_TOKEN = "PASTE-TOKEN-HERE"  # ← Get this from seed_data.py output
    COLLECTION_INTERVAL = 5         # ← Seconds between data reports

# How to get your AGENT_TOKEN:
# Option 1 — From seed_data.py output (printed to terminal when you run it)
# Option 2 — Run this from the backend/ folder:
#   python -c "from app.database import SessionLocal; from app.models import Agent;
#              db = SessionLocal(); a = db.query(Agent).first(); print(a.token)"
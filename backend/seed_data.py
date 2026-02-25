# backend/seed_data.py

"""
Seed Data Script
Creates initial test data in the database for development/testing.

Run with:
    cd backend
    python seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models, auth

# Create all tables if they don't exist
models.Base.metadata.create_all(bind=engine)


def clear_existing_data(db):
    """Remove all existing data before seeding."""
    print("Clearing existing data...")
    db.query(models.Command).delete()
    db.query(models.Process).delete()
    db.query(models.SystemData).delete()
    db.query(models.UserAgentAssignment).delete()
    db.query(models.Agent).delete()
    db.query(models.User).delete()
    db.commit()
    print("✓ Cleared")


def create_users(db):
    """Create test admin and regular users."""
    print("Creating users...")

    admin = models.User(
        username="admin",
        email="admin@example.com",
        hashed_password=auth.hash_password("admin123"),
        role="admin",
        is_active=True,
    )

    user1 = models.User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=auth.hash_password("testuser123"),
        role="user",
        is_active=True,
    )

    user2 = models.User(
        username="testuser2",
        email="testuser2@example.com",
        hashed_password=auth.hash_password("testuser2123"),
        role="user",
        is_active=True,
    )

    db.add_all([admin, user1, user2])
    db.commit()
    db.refresh(admin)
    db.refresh(user1)
    db.refresh(user2)

    print(f"  ✓ admin  (password: admin123)")
    print(f"  ✓ testuser   (password: testuser123)")
    print(f"  ✓ testuser2   (password: testuser2123)")

    return admin, user1, user2


def create_agents(db):
    """Create test agents."""
    print("Creating agents...")

    agent1 = models.Agent(
        agent_id="agent-001",
        hostname="DESKTOP-OFFICE01",
        ip_address="192.168.1.101",
        os_info="Windows 10 Pro 22H2",
        token=auth.generate_agent_token(),
        status="online",
        last_seen=datetime.utcnow(),
    )

    agent2 = models.Agent(
        agent_id="agent-002",
        hostname="DESKTOP-OFFICE02",
        ip_address="192.168.1.102",
        os_info="Windows 11 Pro",
        token=auth.generate_agent_token(),
        status="offline",
        last_seen=datetime.utcnow() - timedelta(hours=2),
    )

    agent3 = models.Agent(
        agent_id="agent-003",
        hostname="SERVER-MAIN",
        ip_address="192.168.1.10",
        os_info="Windows Server 2022",
        token=auth.generate_agent_token(),
        status="online",
        last_seen=datetime.utcnow(),
    )

    db.add_all([agent1, agent2, agent3])
    db.commit()
    db.refresh(agent1)
    db.refresh(agent2)
    db.refresh(agent3)

    print(f"  ✓ agent-001  DESKTOP-OFFICE01  (online)")
    print(f"  ✓ agent-002  DESKTOP-OFFICE02  (offline)")
    print(f"  ✓ agent-003  SERVER-MAIN       (online)")

    return agent1, agent2, agent3


def assign_agents_to_users(db, admin, user1, user2, agent1, agent2, agent3):
    """Assign agents to users (admin sees all via role, explicit assignments for regular users)."""
    print("Assigning agents to users...")

    # testuser can access agent-001 and agent-002
    user1.assigned_agents.append(agent1)
    user1.assigned_agents.append(agent2)

    # testuser2 can access agent-003 only
    user2.assigned_agents.append(agent3)

    db.commit()

    print(f"  ✓ testuser  → agent-001, agent-002")
    print(f"  ✓ testuser2  → agent-003")


def create_system_data(db, agent1, agent2, agent3):
    """Create historical system data for the last 24 hours."""
    print("Creating system data history...")

    agents = [agent1, agent2, agent3]
    count = 0

    for agent in agents:
        # Create one record per hour for the past 24 hours
        for hours_ago in range(24, 0, -1):
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)

            data = models.SystemData(
                agent_id=agent.id,
                os_name=agent.os_info,
                cpu_usage_percent=round(random.uniform(10.0, 90.0), 1),   # ✓ correct field name
                ram_usage_percent=round(random.uniform(30.0, 85.0), 1),   # ✓ correct field name
                disk_usage_percent=round(random.uniform(40.0, 75.0), 1),  # ✓ correct field name
                uptime_hours=round(random.uniform(1.0, 720.0), 1),
                collected_at=timestamp,                                     # ✓ correct field name
            )
            db.add(data)
            count += 1

    db.commit()
    print(f"  ✓ {count} system data records created (24h history × 3 agents)")


def create_processes(db, agent1, agent3):
    """Create sample running processes for online agents."""
    print("Creating processes...")

    sample_processes = [
        ("chrome.exe",      random.uniform(1, 15),  random.uniform(200, 800)),
        ("python.exe",      random.uniform(0, 5),   random.uniform(50, 200)),
        ("explorer.exe",    random.uniform(0, 2),   random.uniform(30, 80)),
        ("svchost.exe",     random.uniform(0, 3),   random.uniform(10, 50)),
        ("notepad.exe",     0.0,                    random.uniform(5, 20)),
        ("Task Manager",    random.uniform(0, 1),   random.uniform(10, 30)),
        ("Code.exe",        random.uniform(1, 10),  random.uniform(100, 400)),
        ("Teams.exe",       random.uniform(1, 8),   random.uniform(150, 500)),
    ]

    count = 0
    for agent in [agent1, agent3]:
        for i, (name, cpu, mem) in enumerate(sample_processes):
            process = models.Process(
                agent_id=agent.id,
                pid=1000 + (i * 100) + agent.id,
                name=name,
                cpu_percent=round(cpu, 1),
                memory_mb=round(mem, 1),
                status="running",
                username="SYSTEM" if "svc" in name.lower() else "User",
                collected_at=datetime.utcnow(),
            )
            db.add(process)
            count += 1

    db.commit()
    print(f"  ✓ {count} processes created")


def create_commands(db, admin, user1, agent1, agent2):
    """Create sample command history."""
    print("Creating command history...")

    commands = [
        models.Command(
            agent_id=agent1.id,
            user_id=admin.id,
            command_type="refresh_data",
            command_data='{}',
            status="executed",
            result='{"success": true, "message": "Data refreshed"}',
            created_at=datetime.utcnow() - timedelta(hours=3),
            executed_at=datetime.utcnow() - timedelta(hours=3) + timedelta(seconds=2),
        ),
        models.Command(
            agent_id=agent1.id,
            user_id=user1.id,
            command_type="kill_process",
            command_data='{"pid": 9999}',
            status="failed",
            result='{"success": false, "message": "Process not found"}',
            created_at=datetime.utcnow() - timedelta(hours=1),
            executed_at=datetime.utcnow() - timedelta(hours=1) + timedelta(seconds=1),
        ),
        models.Command(
            agent_id=agent2.id,
            user_id=admin.id,
            command_type="refresh_data",
            command_data='{}',
            status="pending",
            result=None,
            created_at=datetime.utcnow() - timedelta(minutes=5),
            executed_at=None,
        ),
    ]

    db.add_all(commands)
    db.commit()
    print(f"  ✓ {len(commands)} commands created")


def print_summary(agent1, agent2, agent3):
    print("\n" + "=" * 50)
    print("SEED DATA COMPLETE")
    print("=" * 50)
    print("\nLogin credentials:")
    print("  admin / admin123  (role: admin)")
    print("  testuser  / testuser123   (role: user)")
    print("  testuser2  / testuser2123   (role: user)")
    print("\nAgent tokens (copy to agent/config.py):")
    print(f"  agent-001: {agent1.token}")
    print(f"  agent-002: {agent2.token}")
    print(f"  agent-003: {agent3.token}")
    print("\nStart backend:  cd backend && uvicorn app.main:app --reload")
    print("Start frontend: cd frontend && npm run dev")
    print("=" * 50)


def main():
    db = SessionLocal()
    try:
        clear_existing_data(db)
        admin, user1, user2 = create_users(db)
        agent1, agent2, agent3 = create_agents(db)
        assign_agents_to_users(db, admin, user1, user2, agent1, agent2, agent3)
        create_system_data(db, agent1, agent2, agent3)
        create_processes(db, agent1, agent3)
        create_commands(db, admin, user1, agent1, agent2)
        print_summary(agent1, agent2, agent3)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
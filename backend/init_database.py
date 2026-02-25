"""
Database Initialization Script
This script creates all tables and adds sample data for testing
"""

from app.database import init_db, SessionLocal, engine
from app import models, crud
from app.auth import get_password_hash
from sqlalchemy.orm import Session

def create_sample_data(db: Session):
    """
    Create sample users, agents, and assignments for testing
    """
    
    print("\n📝 Creating sample data...")
    
    # ==============================================
    # 1. Create Admin User
    # ==============================================
    print("\n1️⃣ Creating admin user...")
    
    admin = crud.get_user_by_username(db, "admin")
    if not admin:
        admin = crud.create_user(
            db,
            username="admin",
            email="admin@example.com",
            password="admin123",  # This will be hashed
            role="admin"
        )
        print(f"✓ Admin created: {admin.username} (password: admin123)")
    else:
        print(f"✓ Admin already exists: {admin.username}")
    
    # ==============================================
    # 2. Create Regular User
    # ==============================================
    print("\n2️⃣ Creating regular user...")
    
    user = crud.get_user_by_username(db, "testuser_1")
    if not user:
        user = crud.create_user(
            db,
            username="testuser_1",
            email="testuser@example.com",
            password="user123",  # This will be hashed
            role="user"
        )
        print(f"✓ User created: {user.username} (password: user123)")
    else:
        print(f"✓ User already exists: {user.username}")
    
    # ==============================================
    # 3. Create Sample Agents
    # ==============================================
    print("\n3️⃣ Creating sample agents...")
    
    # Agent 1
    agent1 = crud.get_agent_by_agent_id(db, "agent-001")
    if not agent1:
        agent1 = crud.create_agent(
            db,
            agent_id="agent-001",
            hostname="DESKTOP-ABC123",
            token="my-secret-agent-token-12345",
            ip_address="192.168.1.100"
        )
        print(f"✓ Agent created: {agent1.agent_id} ({agent1.hostname})")
    else:
        print(f"✓ Agent already exists: {agent1.agent_id}")
    
    # Agent 2
    agent2 = crud.get_agent_by_agent_id(db, "agent-002")
    if not agent2:
        agent2 = crud.create_agent(
            db,
            agent_id="agent-002",
            hostname="LAPTOP-XYZ789",
            token="another-secret-token-67890",
            ip_address="192.168.1.101"
        )
        print(f"✓ Agent created: {agent2.agent_id} ({agent2.hostname})")
    else:
        print(f"✓ Agent already exists: {agent2.agent_id}")
    
    # ==============================================
    # 4. Assign Agents to Users
    # ==============================================
    print("\n4️⃣ Assigning agents to users...")
    
    # Admin can access all agents
    crud.assign_agent_to_user(db, user_id=admin.id, agent_id=agent1.id)
    crud.assign_agent_to_user(db, user_id=admin.id, agent_id=agent2.id)
    print(f"✓ Admin has access to all agents")
    
    # Regular user can access only agent-001
    crud.assign_agent_to_user(db, user_id=user.id, agent_id=agent1.id)
    print(f"✓ testuser_1 has access to agent-001")
    
    # ==============================================
    # 5. Create Sample System Data
    # ==============================================
    print("\n5️⃣ Creating sample system data...")
    
    sample_sys_data = {
        "os_name": "Windows 11 Pro",
        "os_version": "10.0.22000",
        "cpu_model": "Intel Core i7-9700K",
        "cpu_cores": 8,
        "cpu_usage_percent": 45.2,
        "ram_total_gb": 16.0,
        "ram_used_gb": 8.5,
        "ram_usage_percent": 53.1,
        "disk_total_gb": 500.0,
        "disk_used_gb": 250.0,
        "disk_usage_percent": 50.0,
        "uptime_hours": 72.5
    }
    
    sys_data = crud.create_system_data(db, agent_id=agent1.id, data=sample_sys_data)
    print(f"✓ System data created for {agent1.hostname}")
    
    # ==============================================
    # 6. Create Sample Processes
    # ==============================================
    print("\n6️⃣ Creating sample processes...")
    
    sample_processes = [
        {
            "pid": 1234,
            "name": "chrome.exe",
            "cpu_percent": 5.2,
            "memory_mb": 250.5,
            "status": "running",
            "username": "User"
        },
        {
            "pid": 5678,
            "name": "python.exe",
            "cpu_percent": 2.1,
            "memory_mb": 150.0,
            "status": "running",
            "username": "User"
        },
        {
            "pid": 9012,
            "name": "explorer.exe",
            "cpu_percent": 1.5,
            "memory_mb": 50.0,
            "status": "running",
            "username": "User"
        }
    ]
    
    for process_data in sample_processes:
        crud.create_process(db, agent_id=agent1.id, process_data=process_data)
    
    print(f"✓ Created {len(sample_processes)} sample processes")
    
    print("\n✅ Sample data creation complete!")
    print("\n" + "="*50)
    print("TEST CREDENTIALS:")
    print("="*50)
    print("Admin:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nRegular User:")
    print("  Username: testuser_1")
    print("  Password: user123")
    print("\nAgent Token:")
    print("  agent-001: my-secret-agent-token-12345")
    print("  agent-002: another-secret-token-67890")
    print("="*50)


def main():
    """
    Main function to initialize database
    """
    print("="*50)
    print("DATABASE INITIALIZATION")
    print("="*50)
    
    # Drop all tables (WARNING: This deletes all data!)
    print("\n⚠️  Dropping all existing tables...")
    models.Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")
    
    # Create all tables
    print("\n📦 Creating database tables...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create sample data
        create_sample_data(db)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n✅ Database initialization complete!")
    print("\n🚀 You can now start the backend server.")


if __name__ == "__main__":
    main()
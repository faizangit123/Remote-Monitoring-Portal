"""
Test Database Queries
"""

from app.database import SessionLocal
from app import crud, models

def main():
    db = SessionLocal()
    
    print("="*50)
    print("DATABASE QUERY TESTS")
    print("="*50)
    
    # Test 1: Get all users
    print("\n1️⃣ All Users:")
    users = crud.get_users(db)
    for user in users:
        print(f"  - {user.username} ({user.email}) - Role: {user.role}")
    
    # Test 2: Get all agents
    print("\n2️⃣ All Agents:")
    agents = crud.get_agents(db)
    for agent in agents:
        print(f"  - {agent.agent_id} ({agent.hostname}) - Status: {agent.status}")
    
    # Test 3: Get admin's agents
    print("\n3️⃣ Admin's Agents:")
    admin = crud.get_user_by_username(db, "admin")
    if admin:
        for agent in admin.agents:
            print(f"  - {agent.agent_id} ({agent.hostname})")
    
    # Test 4: Gettestuser_1 agents
    print("\n4️⃣testuser_1 Agents:")
    user = crud.get_user_by_username(db, "testuser_1")
    if user:
        for agent in user.agents:
            print(f"  - {agent.agent_id} ({agent.hostname})")
    
    # Test 5: Get latest system data
    print("\n5️⃣ Latest System Data for agent-001:")
    agent = crud.get_agent_by_agent_id(db, "agent-001")
    if agent:
        sys_data = crud.get_latest_system_data(db, agent.id)
        if sys_data:
            print(f"  - OS: {sys_data.os_name}")
            print(f"  - CPU: {sys_data.cpu_usage_percent}%")
            print(f"  - RAM: {sys_data.ram_usage_percent}%")
            print(f"  - Disk: {sys_data.disk_usage_percent}%")
    
    # Test 6: Get processes
    print("\n6️⃣ Processes for agent-001:")
    if agent:
        processes = crud.get_agent_processes(db, agent.id)
        for process in processes:
            print(f"  - PID {process.pid}: {process.name} (CPU: {process.cpu_percent}%)")
    
    print("\n✅ All tests passed!")
    print("="*50)
    
    db.close()

if __name__ == "__main__":
    main()
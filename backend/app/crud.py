"""
CRUD Operations (Create, Read, Update, Delete)
All database operations live here.
Routers call these functions — they never touch the DB directly.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
import json

from . import models
from .auth import get_password_hash

# ==============================================================
# USER CRUD
# ==============================================================

def get_user(db: Session, user_id: int) -> Optional[models.User]:

    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:

    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:

    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:

    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "user"
) -> models.User:

    # 1: Hash the password (NEVER store plain text!)
    hashed_password = get_password_hash(password)

    # 2: Create a User model instance
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )

    # 3: Add to database session (staged, not saved yet)
    db.add(db_user)

    # 4: Commit (actually save to database)
    db.commit()

    # 5: Refresh to get auto-assigned values (like id, created_at)
    db.refresh(db_user)

    return db_user


def update_user(
    db: Session,
    user_id: int,
    update_data: dict
) -> Optional[models.User]:

    # Find the user
    user = get_user(db, user_id)
    if not user:
        return None

    # Update each field provided
    for field, value in update_data.items():
        if field == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)

    # Save changes
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True

# ==============================================================
# AGENT CRUD
# ==============================================================

def get_agent(db: Session, agent_id: int) -> Optional[models.Agent]:

    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_agent_by_agent_id(db: Session, agent_id_str: str) -> Optional[models.Agent]:

    return db.query(models.Agent).filter(models.Agent.agent_id == agent_id_str).first()


def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Agent]:

    return db.query(models.Agent).offset(skip).limit(limit).all()


def get_agents_by_user(db: Session, user_id: int) -> List[models.Agent]:

    # Join Agent with UserAgent table
    return (
        db.query(models.Agent)
        .join(
            models.UserAgentAssignment,
            models.Agent.id == models.UserAgentAssignment.agent_id
        )
        .filter(models.UserAgentAssignment.user_id == user_id)
        .all()
    )


def create_agent(
    db: Session,
    agent_id: str,
    hostname: str,
    token: str,
    ip_address: Optional[str] = None
) -> models.Agent:

    db_agent = models.Agent(
        agent_id=agent_id,
        hostname=hostname,
        token=token,
        ip_address=ip_address,
        status="offline"  # New agents start as offline
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent_status(
    db: Session,
    agent_id_str: str,
    status: str
) -> Optional[models.Agent]:

    agent = get_agent_by_agent_id(db, agent_id_str)
    if not agent:
        return None

    agent.status = status
    agent.last_seen = datetime.utcnow()  # Update last seen timestamp
    db.commit()
    db.refresh(agent)
    return agent


def update_agent(
    db: Session,
    agent_id: int,
    update_data: dict
) -> Optional[models.Agent]:

    agent = get_agent(db, agent_id)
    if not agent:
        return None

    for field, value in update_data.items():
        setattr(agent, field, value)

    agent.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: int) -> bool:
    agent = get_agent(db, agent_id)
    if not agent:
        return False

    db.delete(agent)
    db.commit()
    return True


def assign_agent_to_user(
    db: Session,
    user_id: int,
    agent_id: int
) -> Optional[models.UserAgentAssignment]:
  
    # Check if already assigned
    existing = (
        db.query(models.UserAgentAssignment)
        .filter(
            models.UserAgentAssignment.user_id == user_id,
            models.UserAgentAssignment.agent_id == agent_id
        )
        .first()
    )
    if existing:
        return None  # Already assigned

    assignment = models.UserAgentAssignment(user_id=user_id, agent_id=agent_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def unassign_agent_from_user(db: Session, user_id: int, agent_id: int) -> bool:
    assignment = (
        db.query(models.UserAgentAssignment)
        .filter(
            models.UserAgentAssignment.user_id == user_id,
            models.UserAgentAssignment.agent_id == agent_id
        )
        .first()
    )
    if not assignment:
        return False

    db.delete(assignment)
    db.commit()
    return True


# ==============================================================
# SYSTEM DATA CRUD
# ==============================================================

def save_system_data(db: Session, agent_db_id: int, data: dict) -> models.SystemData:
    system_data = models.SystemData(
        agent_id=agent_db_id,
        os_name=data.get("os_name"),
        os_version=data.get("os_version"),
        cpu_model=data.get("cpu_model"),
        cpu_cores=data.get("cpu_cores"),
        cpu_usage_percent=data.get("cpu_usage_percent"),
        ram_total_gb=data.get("ram_total_gb"),
        ram_used_gb=data.get("ram_used_gb"),
        ram_usage_percent=data.get("ram_usage_percent"),
        disk_total_gb=data.get("disk_total_gb"),
        disk_used_gb=data.get("disk_used_gb"),
        disk_usage_percent=data.get("disk_usage_percent"),
        uptime_hours=data.get("uptime_hours"),
        collected_at=datetime.utcnow()
    )
    db.add(system_data)
    db.commit()
    db.refresh(system_data)
    return system_data


def get_latest_system_data(
    db: Session,
    agent_db_id: int
) -> Optional[models.SystemData]:
    return (
        db.query(models.SystemData)
        .filter(models.SystemData.agent_id == agent_db_id)
        .order_by(desc(models.SystemData.collected_at))
        # desc = descending order → newest first
        .first()
    )


def get_system_data_history(
    db: Session,
    agent_db_id: int,
    limit: int = 50
) -> List[models.SystemData]:
    return (
        db.query(models.SystemData)
        .filter(models.SystemData.agent_id == agent_db_id)
        .order_by(desc(models.SystemData.collected_at))
        .limit(limit)
        .all()
    )


# ==============================================================
# PROCESS CRUD
# ==============================================================

def save_processes(
    db: Session,
    agent_db_id: int,
    processes: list
) -> List[models.Process]:

    # 1: Delete old process records for this agent
    db.query(models.Process).filter(
        models.Process.agent_id == agent_db_id
    ).delete()

    # 2: Insert new process records
    created = []
    for proc in processes:
        db_proc = models.Process(
            agent_id=agent_db_id,
            pid=proc.get("pid"),
            name=proc.get("name"),
            cpu_percent=proc.get("cpu_percent"),
            memory_mb=proc.get("memory_mb"),
            status=proc.get("status"),
            username=proc.get("username"),
            collected_at=datetime.utcnow()
        )
        db.add(db_proc)
        created.append(db_proc)

    db.commit()
    # Refresh all to get auto-assigned IDs
    for proc in created:
        db.refresh(proc)

    return created


def get_processes(
    db: Session,
    agent_db_id: int
) -> List[models.Process]:

    return (
        db.query(models.Process)
        .filter(models.Process.agent_id == agent_db_id)
        .order_by(desc(models.Process.cpu_percent))
        .all()
    )


# ==============================================================
# COMMAND CRUD
# ==============================================================

def create_command(
    db: Session,
    agent_id: int,
    user_id: int,
    command_type: str,
    command_data: Optional[dict] = None
) -> models.Command:

    command = models.Command(
        agent_id=agent_id,
        user_id=user_id,
        command_type=command_type,
        command_data=json.dumps(command_data) if command_data else None,
        # Store dict as JSON string because model uses Text column
        status="pending"
    )
    db.add(command)
    db.commit()
    db.refresh(command)
    return command


def get_command(db: Session, command_id: int) -> Optional[models.Command]:

    return db.query(models.Command).filter(models.Command.id == command_id).first()


def get_commands_for_agent(
    db: Session,
    agent_db_id: int,
    status: Optional[str] = None,
    limit: int = 50
) -> List[models.Command]:

    query = db.query(models.Command).filter(
        models.Command.agent_id == agent_db_id
    )

    # Apply status filter if provided
    if status:
        query = query.filter(models.Command.status == status)

    return query.order_by(desc(models.Command.created_at)).limit(limit).all()


def get_pending_commands(
    db: Session,
    agent_db_id: int
) -> List[models.Command]:

    return get_commands_for_agent(db, agent_db_id, status="pending")


def update_command_status(
    db: Session,
    command_id: int,
    status: str,
    result: Optional[dict] = None
) -> Optional[models.Command]:

    command = get_command(db, command_id)
    if not command:
        return None

    command.status = status
    command.result = json.dumps(result) if result else None
    # Store dict as JSON string because model uses Text column
    command.executed_at = datetime.utcnow()
    db.commit()
    db.refresh(command)
    return command


def get_all_commands(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.Command]:

    return (
        db.query(models.Command)
        .order_by(desc(models.Command.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
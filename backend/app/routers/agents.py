"""
Agents Router
Endpoints for managing and monitoring connected agents.
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user, get_current_active_admin

router = APIRouter(prefix="/api/agents", tags=["Agents"])


# ==============================================================
# HELPER: Resolve agent by string agent_id OR integer id
# ==============================================================

def resolve_agent(agent_id: str, db: Session) -> models.Agent:
    """
    Look up agent by string agent_id (e.g. "agent-001").
    Falls back to integer DB id if the value is numeric.
    """
    # Try string agent_id first (e.g. "agent-001")
    agent = crud.get_agent_by_agent_id(db, agent_id_str=agent_id)
    if agent:
        return agent
    # Fall back to integer primary key
    if agent_id.isdigit():
        agent = crud.get_agent(db, agent_id=int(agent_id))
    return agent


def check_agent_access(agent: models.Agent, current_user: models.User, db: Session) -> bool:
    if current_user.role == "admin":
        return True
    assigned = crud.get_agents_by_user(db, user_id=current_user.id)
    assigned_ids = [a.id for a in assigned]
    return agent.id in assigned_ids


# ==============================================================
# LIST AGENTS
# ==============================================================

@router.get("/", response_model=List[schemas.AgentResponse])
def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return crud.get_agents(db, skip=skip, limit=limit)
    else:
        return crud.get_agents_by_user(db, user_id=current_user.id)


# ==============================================================
# GENERATE TOKEN — must come BEFORE /{agent_id} to avoid conflict
# ==============================================================

@router.get("/generate-token", response_model=dict)
def generate_agent_token(
    admin: models.User = Depends(get_current_active_admin)
):
    token = secrets.token_hex(32)
    return {"token": token}


# ==============================================================
# REGISTER AGENT
# ==============================================================

@router.post("/register", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED)
def register_agent(
    agent: schemas.AgentCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_active_admin)
):
    existing = crud.get_agent_by_agent_id(db, agent_id_str=agent.agent_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent ID '{agent.agent_id}' is already registered"
        )

    new_agent = crud.create_agent(
        db,
        agent_id=agent.agent_id,
        hostname=agent.hostname,
        token=agent.token,
        ip_address=agent.ip_address
    )
    return new_agent


# ==============================================================
# GET SINGLE AGENT — accepts string agent_id like "agent-001"
# ==============================================================

@router.get("/{agent_id}", response_model=schemas.AgentResponse)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if not check_agent_access(agent, current_user, db):
        raise HTTPException(status_code=403, detail="Access denied")
    return agent


# ==============================================================
# UPDATE AGENT
# ==============================================================

@router.put("/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(
    agent_id: str,
    agent_update: schemas.AgentUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_active_admin)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    update_data = agent_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    return crud.update_agent(db, agent_id=agent.id, update_data=update_data)


# ==============================================================
# DELETE AGENT
# ==============================================================

@router.delete("/{agent_id}", response_model=schemas.MessageResponse)
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_active_admin)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    crud.delete_agent(db, agent_id=agent.id)
    return {"message": f"Agent '{agent_id}' deleted successfully", "success": True}


# ==============================================================
# GET LATEST SYSTEM DATA
# ==============================================================

@router.get("/{agent_id}/system-data", response_model=Optional[schemas.SystemDataResponse])
def get_agent_system_data(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if not check_agent_access(agent, current_user, db):
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_latest_system_data(db, agent_db_id=agent.id)


# ==============================================================
# GET SYSTEM DATA HISTORY
# ==============================================================

@router.get("/{agent_id}/history", response_model=List[schemas.SystemDataResponse])
def get_agent_history(
    agent_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if not check_agent_access(agent, current_user, db):
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_system_data_history(db, agent_db_id=agent.id, limit=limit)


# ==============================================================
# GET PROCESSES
# ==============================================================

@router.get("/{agent_id}/processes", response_model=List[schemas.ProcessResponse])
def get_agent_processes(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    agent = resolve_agent(agent_id, db)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    if not check_agent_access(agent, current_user, db):
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_processes(db, agent_db_id=agent.id)
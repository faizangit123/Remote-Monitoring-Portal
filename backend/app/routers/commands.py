"""

Commands Router

Endpoints for sending commands to agents and viewing command results.

"""



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user, get_current_active_admin
from ..routers.agents import check_agent_access
try:

    from ..routers.websocket import manager

except ImportError:

    manager = None  # WebSocket manager not available yet



router = APIRouter(prefix="/api/commands", tags=["Commands"])


# ==============================================================
# SEND COMMAND TO AGENT
# ==============================================================

@router.post("/", response_model=schemas.CommandResponse, status_code=status.HTTP_201_CREATED)

async def send_command(

    command: schemas.CommandCreate,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

    # Only admins can send commands

):

    # Validate command type

    valid_commands = ["refresh_data", "kill_process", "get_processes"]

    if command.command_type not in valid_commands:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Invalid command type. Must be one of: {valid_commands}"

        )

    # Verify agent exists

    agent = crud.get_agent(db, agent_id=command.agent_id)

    if not agent:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Agent {command.agent_id} not found"

        )



    # Create command in database

    db_command = crud.create_command(

        db,

        agent_id=command.agent_id,

        user_id=admin.id,

        command_type=command.command_type,

        command_data=command.command_data

    )

    if manager and agent.status == "online":
        try:
            # Send command through WebSocket to the agent

            await manager.send_command_to_agent(

                agent_id_str=agent.agent_id,

                command={
                    "type": "command",

                    "command_id": db_command.id,

                    "command_type": command.command_type,

                    "command_data": command.command_data

                }

            )

        except Exception as e:

            print(f"WebSocket send failed: {e}")



    return db_command

# ==============================================================
# LIST ALL COMMANDS (Admin view)
# ==============================================================

@router.get("/", response_model=List[schemas.CommandResponse])

def list_all_commands(

    skip: int = 0,

    limit: int = 100,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    return crud.get_all_commands(db, skip=skip, limit=limit)


# ==============================================================
# GET COMMANDS FOR SPECIFIC AGENT
# ==============================================================

@router.get("/agent/{agent_id}", response_model=List[schemas.CommandResponse])

def get_commands_for_agent(

    agent_id: int,

    status_filter: Optional[str] = None,

    limit: int = 50,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)

):

    agent = crud.get_agent(db, agent_id=agent_id)

    if not agent:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Agent {agent_id} not found"

        )



    if not check_agent_access(agent, current_user, db):

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Access denied"

        )



    return crud.get_commands_for_agent(

        db,

        agent_db_id=agent_id,

        status=status_filter,

        limit=limit

    )

# ==============================================================
# GET SINGLE COMMAND
# ==============================================================

@router.get("/{command_id}", response_model=schemas.CommandResponse)

def get_command(

    command_id: int,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    command = crud.get_command(db, command_id=command_id)

    if not command:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Command {command_id} not found"

        )

    return command
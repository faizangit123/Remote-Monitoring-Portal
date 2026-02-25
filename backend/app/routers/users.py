"""

Users Router

Admin-only endpoints for managing user accounts.

Regular users cannot access any of these endpoints.

"""



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user, get_current_active_admin

router = APIRouter(prefix="/api/users", tags=["Users"])


# ==============================================================
# GET ALL USERS
# ==============================================================

@router.get("/", response_model=List[schemas.UserResponse])

def list_users(

    skip: int = 0,

    limit: int = 100,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    users = crud.get_users(db, skip=skip, limit=limit)

    return users

# ==============================================================

# GET SINGLE USER

# ==============================================================

@router.get("/{user_id}", response_model=schemas.UserResponse)

def get_user(

    user_id: int,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):


    user = crud.get_user(db, user_id=user_id)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"User with ID {user_id} not found"

        )

    return user

# ==============================================================
# CREATE USER
# ==============================================================

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)

def create_user(

    user: schemas.UserCreate,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    # Check if username is taken
    existing = crud.get_user_by_username(db, username=user.username)

    if existing:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Username '{user.username}' is already taken"

        )

    # Check if email is taken

    existing = crud.get_user_by_email(db, email=user.email)

    if existing:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail=f"Email '{user.email}' is already registered"

        )

    # Create the user

    new_user = crud.create_user(

        db,

        username=user.username,

        email=user.email,

        password=user.password,

        role=user.role

    )

    return new_user

# ==============================================================
# UPDATE USER
# ==============================================================

@router.put("/{user_id}", response_model=schemas.UserResponse)

def update_user(

    user_id: int,

    user_update: schemas.UserUpdate,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):


    update_data = user_update.model_dump(exclude_unset=True)



    if not update_data:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="No fields provided to update"

        )

    updated_user = crud.update_user(db, user_id=user_id, update_data=update_data)

    if not updated_user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"User with ID {user_id} not found"

        )

    return updated_user


# ==============================================================
# DELETE USER
# ==============================================================

@router.delete("/{user_id}", response_model=schemas.MessageResponse)

def delete_user(

    user_id: int,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    if user_id == admin.id:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="You cannot delete your own account"

        )

    success = crud.delete_user(db, user_id=user_id)

    if not success:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"User with ID {user_id} not found"

        )

    return {"message": f"User {user_id} deleted successfully", "success": True}


# ==============================================================
# ASSIGN AGENT TO USER
# ==============================================================

@router.post("/{user_id}/assign-agent", response_model=schemas.AgentAssignmentResponse)

def assign_agent(

    user_id: int,

    assignment: schemas.AgentAssignment,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    # Verify user exists

    user = crud.get_user(db, user_id=user_id)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"User {user_id} not found"

        )

    # Verify agent exists

    agent = crud.get_agent(db, agent_id=assignment.agent_id)

    if not agent:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Agent {assignment.agent_id} not found"

        )

    # Create assignment

    result = crud.assign_agent_to_user(db, user_id=user_id, agent_id=assignment.agent_id)

    if not result:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Agent is already assigned to this user"

        )

    return {

        "user_id": user_id,

        "agent_id": assignment.agent_id,

        "message": f"Agent '{agent.hostname}' assigned to user '{user.username}'"

    }


# ==============================================================
# UNASSIGN AGENT FROM USER
# ==============================================================

@router.delete("/{user_id}/unassign-agent/{agent_id}", response_model=schemas.MessageResponse)

def unassign_agent(

    user_id: int,

    agent_id: int,

    db: Session = Depends(get_db),

    admin: models.User = Depends(get_current_active_admin)

):

    success = crud.unassign_agent_from_user(db, user_id=user_id, agent_id=agent_id)

    if not success:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Assignment not found"

        )

    return {"message": "Agent unassigned successfully", "success": True}

# ==============================================================
# GET MY PROFILE (Any logged-in user)
# ==============================================================

@router.get("/me/profile", response_model=schemas.UserResponse)

def get_my_profile(

    current_user: models.User = Depends(get_current_user)

    # Note: using get_current_user (not admin) - any user can see their own profile

):

    return current_user
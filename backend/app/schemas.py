from __future__ import annotations

"""
Pydantic Schemas
These classes define the structure and validation rules for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# ==============================================
# TOKEN SCHEMAS
# ==============================================

class Token(BaseModel):
    access_token: str  # The JWT token string
    token_type: str    # Always "bearer" for JWT tokens
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.abc123",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# ==============================================
# USER SCHEMAS
# ==============================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # EmailStr automatically validates email format
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscore')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="user")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either 'admin' or 'user'"""
        if v not in ['admin', 'user']:
            raise ValueError('Role must be either "admin" or "user"')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    assigned_agents: List["AgentResponse"] = []
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to Pydantic


class UserLogin(BaseModel):
    username: str
    password: str


# ==============================================
# AGENT SCHEMAS
# ==============================================

class AgentBase(BaseModel):
    """Base Agent schema"""
    agent_id: str = Field(..., min_length=3, max_length=50)
    hostname: str = Field(..., min_length=1, max_length=100)
    ip_address: Optional[str] = None


class AgentCreate(AgentBase):
    token: str = Field(..., min_length=20)


class AgentUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[str] = None


class AgentResponse(AgentBase):
    """
    Schema for agent response
    """
    id: int
    status: str
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
UserResponse.model_rebuild()
# ==============================================
# SYSTEM DATA SCHEMAS
# ==============================================

class SystemDataBase(BaseModel):
    """Base System Data schema"""
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    cpu_usage_percent: Optional[float] = Field(None, ge=0, le=100)  # Between 0-100
    ram_total_gb: Optional[float] = Field(None, ge=0)
    ram_used_gb: Optional[float] = Field(None, ge=0)
    ram_usage_percent: Optional[float] = Field(None, ge=0, le=100)
    disk_total_gb: Optional[float] = Field(None, ge=0)
    disk_used_gb: Optional[float] = Field(None, ge=0)
    disk_usage_percent: Optional[float] = Field(None, ge=0, le=100)
    uptime_hours: Optional[float] = Field(None, ge=0)


class SystemDataCreate(SystemDataBase):
    """
    Schema for creating system data
    Agent sends this when reporting system information
    """
    agent_id: int


class SystemDataResponse(SystemDataBase):
    """Schema for system data response"""
    id: int
    agent_id: int
    collected_at: datetime
    
    class Config:
        from_attributes = True


# ==============================================
# PROCESS SCHEMAS
# ==============================================

class ProcessBase(BaseModel):
    """Base Process schema"""
    pid: int = Field(..., gt=0)  # Process ID must be positive
    name: str = Field(..., min_length=1, max_length=200)
    cpu_percent: Optional[float] = Field(None, ge=0)
    memory_mb: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    username: Optional[str] = None


class ProcessCreate(ProcessBase):
    """Schema for creating process record"""
    agent_id: int


class ProcessResponse(ProcessBase):
    """Schema for process response"""
    id: int
    agent_id: int
    collected_at: datetime
    
    class Config:
        from_attributes = True


# ==============================================
# COMMAND SCHEMAS
# ==============================================

class CommandBase(BaseModel):
    """Base Command schema"""
    command_type: str = Field(..., min_length=1, max_length=50)
    command_data: Optional[dict] = None  # JSON data for command parameters


class CommandCreate(CommandBase):
    """
    Schema for creating command
    """
    agent_id: int


class CommandUpdate(BaseModel):
    """Schema for updating command (usually by agent)"""
    status: str
    result: Optional[dict] = None


class CommandResponse(BaseModel):
    """
    Schema for command response
    """
    id: int
    agent_id: int
    user_id: int
    command_type: str
    command_data: Optional[dict] = None
    status: str
    result: Optional[dict] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

    @field_validator('command_data', 'result', mode='before')
    @classmethod
    def parse_json_string(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except Exception:
                return None
        return v

    class Config:
        from_attributes = True


# ==============================================
# RESPONSE SCHEMAS (Generic)
# ==============================================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# ==============================================
# AGENT ASSIGNMENT SCHEMAS
# ==============================================

class AgentAssignment(BaseModel):
    """
    Schema for assigning agent to user
    """
    user_id: int
    agent_id: int


class AgentAssignmentResponse(BaseModel):
    """Schema for agent assignment response"""
    user_id: int
    agent_id: int
    message: str


# ==============================================
# TESTING
# ==============================================

if __name__ == "__main__":
    print("="*50)
    print("SCHEMA VALIDATION TESTS")
    print("="*50)
    
    # Test 1: Valid user creation
    print("\n1️⃣ Valid user creation:")
    try:
        user = UserCreate(
            username="testuser_1",
            email="testuser@example.com",
            password="pass123",
            role="user"
        )
        print(f"✓ User valid: {user.username}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Invalid email
    print("\n2️⃣ Invalid email:")
    try:
        user = UserCreate(
            username="testuser_1",
            email="invalid-email",  # Invalid
            password="pass123",
            role="user"
        )
        print(f"✗ Should have failed!")
    except Exception as e:
        print(f"✓ Correctly rejected: {e}")
    
    # Test 3: Weak password
    print("\n3️⃣ Weak password:")
    try:
        user = UserCreate(
            username="testuser_1",
            email="testuser@example.com",
            password="abc",  # Too short, no numbers
            role="user"
        )
        print(f"✗ Should have failed!")
    except Exception as e:
        print(f"✓ Correctly rejected: Password validation failed")
    
    # Test 4: Invalid role
    print("\n4️⃣ Invalid role:")
    try:
        user = UserCreate(
            username="testuser_1",
            email="testuser@example.com",
            password="pass123",
            role="superadmin"  # Invalid role
        )
        print(f"✗ Should have failed!")
    except Exception as e:
        print(f"✓ Correctly rejected: Invalid role")
    
    # Test 5: Agent creation
    print("\n5️⃣ Valid agent creation:")
    try:
        agent = AgentCreate(
            agent_id="agent-001",
            hostname="DESKTOP-ABC",
            token="this-is-a-long-secret-token-12345",
            ip_address="192.168.1.100"
        )
        print(f"✓ Agent valid: {agent.agent_id}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n✅ Schema validation tests complete!")
    print("="*50)
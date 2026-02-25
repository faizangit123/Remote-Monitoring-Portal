"""
Database Models
These classes represent our database tables using SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# ==============================================
# USER MODEL
# ==============================================

class User(Base):
    """
    User Model - Represents portal users (Admin and User roles)
    """
    
    __tablename__ = "users"
    # Table name in database
    
    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    hashed_password = Column(String(255), nullable=False)
    
    role = Column(String, default="user")          # "admin" | "user"

    is_active = Column(Boolean, default=True, server_default="1")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ==============================================
    # Relationships
    # ==============================================
    
    assigned_agents = relationship(
        "Agent",
        secondary="user_agents",
        back_populates="assigned_users",
        overlaps="agent_assignments"
    )

    
    commands = relationship("Command", back_populates="user")
    """
    Relationship: User ↔ Command (One-to-Many)
    """
    
    agent_assignments = relationship("UserAgentAssignment", back_populates="user")

    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


# ==============================================
# AGENT MODEL
# ==============================================

class Agent(Base):
    """
    Agent Model - Represents Windows machines being monitored
    """
    
    __tablename__ = "agents"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    agent_id = Column(String(50), unique=True, nullable=False, index=True)
    
    hostname = Column(String(100), nullable=False)
    
    ip_address = Column(String(45), nullable=True)
    
    os_info = Column(String)                        
    
    token = Column(String(255), unique=True, nullable=False)
    
    status = Column(String(20), default="offline", server_default="offline")
    
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ==============================================
    # Relationships
    # ==============================================
    
    assigned_users = relationship(
      "User",
      secondary="user_agents",
      back_populates="assigned_agents",
      overlaps="user_assignments,agent_assignments"
      )
    
    system_data = relationship("SystemData", back_populates="agent", cascade="all, delete-orphan")

    processes = relationship("Process", back_populates="agent", cascade="all, delete-orphan")
    """
    Relationship: Agent ↔ Process (One-to-Many)
    """
    
    commands = relationship("Command", back_populates="agent", cascade="all, delete-orphan")
    """
    Relationship: Agent ↔ Command (One-to-Many)
    """
    
    user_assignments = relationship("UserAgentAssignment", back_populates="agent", overlaps="assigned_agents,assigned_users")

    def __repr__(self):
        return f"<Agent(id={self.id}, agent_id='{self.agent_id}', hostname='{self.hostname}', status='{self.status}')>"


# ==============================================
# USER_AGENTS ASSOCIATION TABLE
# ==============================================

class UserAgentAssignment(Base):
    """
   UserAgentAssignment Model - Association table linking Users to Agents
    """
    
    __tablename__ = "user_agents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("User", back_populates="agent_assignments", overlaps="assigned_agents,assigned_users")
    
    agent = relationship("Agent", back_populates="user_assignments", overlaps="assigned_agents,assigned_users,agent_assignments")

    
    def __repr__(self):
        return f"<UserAgent(user_id={self.user_id}, agent_id={self.agent_id})>"


# ==============================================
# SYSTEM_DATA MODEL
# ==============================================

class SystemData(Base):
    """
    SystemData Model - Stores system information collected from agents
    """
    
    __tablename__ = "system_data"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Operating System
    os_name = Column(String(100), nullable=True)
    
    os_version = Column(String(50), nullable=True)
    
    # CPU Information
    cpu_model = Column(String(200), nullable=True)
    
    cpu_cores = Column(Integer, nullable=True)
    
    cpu_usage_percent = Column(Float, nullable=True)
    
    # RAM Information
    ram_total_gb = Column(Float, nullable=True)
    
    ram_used_gb = Column(Float, nullable=True)
    
    ram_usage_percent = Column(Float, nullable=True)
    
    # Disk Information
    disk_total_gb = Column(Float, nullable=True)
    
    disk_used_gb = Column(Float, nullable=True)
    
    disk_usage_percent = Column(Float, nullable=True)
    
    # System Uptime
    uptime_hours = Column(Float, nullable=True)
    
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # ==============================================
    # Relationships
    # ==============================================
    
    agent = relationship("Agent", back_populates="system_data")

    def __repr__(self):
        return f"<SystemData(id={self.id}, agent_id={self.agent_id}, cpu={self.cpu_usage_percent}%, ram={self.ram_usage_percent}%)>"


# ==============================================
# PROCESS MODEL
# ==============================================

class Process(Base):

    __tablename__ = "processes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    pid = Column(Integer, nullable=False)
    
    name = Column(String(200), nullable=False)
    
    cpu_percent = Column(Float, nullable=True)
    
    memory_mb = Column(Float, nullable=True)
    
    status = Column(String(20), nullable=True)
    
    username = Column(String(100), nullable=True)
    
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # ==============================================
    # Relationships
    # ==============================================
    
    agent = relationship("Agent", back_populates="processes")
    
    def __repr__(self):
        return f"<Process(id={self.id}, agent_id={self.agent_id}, pid={self.pid}, name='{self.name}')>"


# ==============================================
# COMMAND MODEL
# ==============================================

class Command(Base):
    """
    Command Model - Stores commands sent from portal to agents
    """
    
    __tablename__ = "commands"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    command_type = Column(String(50), nullable=False)
 
    
    command_data = Column(Text, nullable=True)
    
    status = Column(String(20), default="pending", server_default="pending", index=True)
    
    result = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # ==============================================
    # Relationships
    # ==============================================
    
    agent = relationship("Agent", back_populates="commands")
    
    user = relationship("User", back_populates="commands")
    
    def __repr__(self):
        return f"<Command(id={self.id}, type='{self.command_type}', status='{self.status}', agent_id={self.agent_id})>"


# ==============================================
# MODEL SUMMARY
# ==============================================

"""
Summary of Relationships:

1. User ↔ Agent (Many-to-Many via UserAgent)
   - user.agents → list of agents user can access
   - agent.users → list of users who can access agent

2. Agent ↔ SystemData (One-to-Many)
   - agent.system_data → list of system data snapshots
   - system_data.agent → the agent this data belongs to

3. Agent ↔ Process (One-to-Many)
   - agent.processes → list of processes running on agent
   - process.agent → the agent this process belongs to

4. User ↔ Command (One-to-Many)
   - user.commands → list of commands user has sent
   - command.user → user who sent the command

5. Agent ↔ Command (One-to-Many)
   - agent.commands → list of commands for this agent
   - command.agent → agent that should execute command
"""
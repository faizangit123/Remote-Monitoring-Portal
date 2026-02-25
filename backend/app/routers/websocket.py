"""
WebSocket Handler
Manages real-time bi-directional communication between:
- Web browser (frontend users watching dashboards)
- Windows agent (.exe running on monitored machines)
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from .. import crud, models
from ..database import get_db
from ..auth import verify_token as decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


# ==============================================================
# CONNECTION MANAGER CLASS
# ==============================================================

class ConnectionManager:
    def __init__(self):
        self.agent_connections: Dict[str, WebSocket] = {}
        self.client_connections: Dict[str, List[WebSocket]] = {}

    # ----------------------------------------------------------
    # CONNECT METHODS
    # ----------------------------------------------------------

    async def connect_agent(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()  # Accept the WebSocket connection
        self.agent_connections[agent_id] = websocket
        logger.info(f"✅ Agent connected: {agent_id}")

    async def connect_client(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()  # Accept the WebSocket connection

        # Create list if this is the first client watching this agent
        if agent_id not in self.client_connections:
            self.client_connections[agent_id] = []

        self.client_connections[agent_id].append(websocket)
        logger.info(f"🌐 Client connected to watch agent: {agent_id}")

    # ----------------------------------------------------------
    # DISCONNECT METHODS
    # ----------------------------------------------------------

    def disconnect_agent(self, agent_id: str):
        if agent_id in self.agent_connections:
            del self.agent_connections[agent_id]
            logger.info(f"❌ Agent disconnected: {agent_id}")

    def disconnect_client(self, agent_id: str, websocket: WebSocket):
        if agent_id in self.client_connections:
            if websocket in self.client_connections[agent_id]:
                self.client_connections[agent_id].remove(websocket)
            # Clean up empty list
            if not self.client_connections[agent_id]:
                del self.client_connections[agent_id]

    # ----------------------------------------------------------
    # SEND METHODS
    # ----------------------------------------------------------

    async def broadcast_to_clients(self, agent_id: str, message: dict):
        if agent_id not in self.client_connections:
            return  # No one is watching this agent

        message_str = json.dumps(message, default=str)

        disconnected = []
        for client_ws in self.client_connections[agent_id]:
            try:
                await client_ws.send_text(message_str)
            except Exception:
                disconnected.append(client_ws)

        # Remove any broken connections
        for ws in disconnected:
            self.disconnect_client(agent_id, ws)

    async def send_command_to_agent(self, agent_id_str: str, command: dict):
        if agent_id_str not in self.agent_connections:
            raise Exception(f"Agent {agent_id_str} is not connected")

        websocket = self.agent_connections[agent_id_str]
        message_str = json.dumps(command, default=str)

        try:
            await websocket.send_text(message_str)
            logger.info(f"📤 Command sent to agent {agent_id_str}: {command.get('command_type')}")
        except Exception as e:
            self.disconnect_agent(agent_id_str)
            raise Exception(f"Failed to send command: {e}")

    async def broadcast_agent_status(self, agent_id: str, status: str):
        message = {
            "type": "agent_status",
            "agent_id": agent_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_clients(agent_id, message)

    # ----------------------------------------------------------
    # STATUS METHODS
    # ----------------------------------------------------------

    def is_agent_connected(self, agent_id: str) -> bool:
        """Check if an agent is currently connected."""
        return agent_id in self.agent_connections

    def get_connected_agents(self) -> List[str]:
        """Get list of all currently connected agent IDs."""
        return list(self.agent_connections.keys())

    def get_connection_stats(self) -> dict:
        """Get stats about current connections."""
        return {
            "connected_agents": len(self.agent_connections),
            "agent_ids": list(self.agent_connections.keys()),
            "watching_clients": sum(
                len(clients) for clients in self.client_connections.values()
            )
        }


# ==============================================================
# Create singleton instance (shared across entire app)
# ==============================================================

manager = ConnectionManager()

# ==============================================================
# WEBSOCKET ENDPOINT: AGENT CONNECTION
# ==============================================================

@router.websocket("/agent/{agent_id}")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: str,
    token: str,
    db: Session = Depends(get_db)
):

    # ----------------------------------------------------------
    # 1: Authenticate the agent
    # ----------------------------------------------------------
    db_agent = crud.get_agent_by_agent_id(db, agent_id_str=agent_id)

    if not db_agent:
        # Agent not registered in database
        await websocket.close(code=4001, reason="Agent not registered")
        return

    if db_agent.token != token:
        # Wrong token
        await websocket.close(code=4003, reason="Invalid token")
        return

    # ----------------------------------------------------------
    # 2: Accept connection and update status
    # ----------------------------------------------------------
    await manager.connect_agent(agent_id, websocket)
    crud.update_agent_status(db, agent_id_str=agent_id, status="online")

    await manager.broadcast_agent_status(agent_id, "online")

    logger.info(f"🟢 Agent {agent_id} ({db_agent.hostname}) is now online")

    # ----------------------------------------------------------
    # 3: Send any pending commands to the agent
    # ----------------------------------------------------------
    pending_commands = crud.get_pending_commands(db, agent_db_id=db_agent.id)
    for cmd in pending_commands:
        try:
            await websocket.send_text(json.dumps({
                "type": "command",
                "command_id": cmd.id,
                "command_type": cmd.command_type,
                "command_data": cmd.command_data
            }))
        except Exception:
            break

    # ----------------------------------------------------------
    # 4: Message receive loop
    # ----------------------------------------------------------
    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}: {raw_data[:100]}")
                continue  # Skip this message, keep loop running

            message_type = message.get("type")

            # --------------------------------------------------
            # Handle: System Data
            # --------------------------------------------------
            if message_type == "system_data":
                data = message.get("data", {})

                crud.save_system_data(db, agent_db_id=db_agent.id, data=data)

                if data.get("ip_address"):
                    crud.update_agent(
                        db, agent_id=db_agent.id,
                        update_data={"ip_address": data["ip_address"]}
                    )

                await manager.broadcast_to_clients(
                    agent_id,
                    {
                        "type": "system_data_update",
                        "agent_id": agent_id,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            # --------------------------------------------------
            # Handle: Process List
            # --------------------------------------------------
            elif message_type == "processes":
                processes = message.get("data", [])

                crud.save_processes(db, agent_db_id=db_agent.id, processes=processes)

                await manager.broadcast_to_clients(
                    agent_id,
                    {
                        "type": "processes_update",
                        "agent_id": agent_id,
                        "data": processes,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            # --------------------------------------------------
            # Handle: Command Result (agent executed a command)
            # --------------------------------------------------
            elif message_type == "command_result":
                command_id = message.get("command_id")
                success = message.get("success", False)
                result = message.get("result", {})

                if command_id:
                    crud.update_command_status(
                        db,
                        command_id=command_id,
                        status="executed" if success else "failed",
                        result=result
                    )

                    await manager.broadcast_to_clients(
                        agent_id,
                        {
                            "type": "command_result",
                            "command_id": command_id,
                            "success": success,
                            "result": result
                        }
                    )

            # --------------------------------------------------
            # Handle: Heartbeat / Ping (agent is still alive)
            # --------------------------------------------------
            elif message_type == "heartbeat":
                crud.update_agent_status(db, agent_id_str=agent_id, status="online")

                await websocket.send_text(json.dumps({"type": "pong"}))

            else:
                logger.warning(f"Unknown message type from {agent_id}: {message_type}")

    # ----------------------------------------------------------
    # 5: Handle disconnect
    # ----------------------------------------------------------
    except WebSocketDisconnect:
        logger.info(f"🔴 Agent {agent_id} disconnected")
    except Exception as e:
        logger.error(f"Error in agent WebSocket {agent_id}: {e}")
    finally:
        manager.disconnect_agent(agent_id)
        crud.update_agent_status(db, agent_id_str=agent_id, status="offline")
        await manager.broadcast_agent_status(agent_id, "offline")
        logger.info(f"Agent {agent_id} marked offline")


# ==============================================================
# WEBSOCKET ENDPOINT: CLIENT/BROWSER CONNECTION
# ==============================================================

@router.websocket("/client/{agent_id}")
async def client_websocket(
    websocket: WebSocket,
    agent_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    # ----------------------------------------------------------
    # 1: Authenticate the user (validate JWT token)
    # ----------------------------------------------------------
    token_data = decode_access_token(token)
    if not token_data:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    username = token_data.get("sub")
    user = crud.get_user_by_username(db, username=username)
    if not user or not user.is_active:
        await websocket.close(code=4001, reason="User not found or inactive")
        return

    # ----------------------------------------------------------
    # 2: Check agent exists and user has access
    # ----------------------------------------------------------
    agent = crud.get_agent_by_agent_id(db, agent_id_str=agent_id)
    if not agent:
        await websocket.close(code=4004, reason="Agent not found")
        return

    if user.role != "admin":
        assigned = crud.get_agents_by_user(db, user_id=user.id)
        assigned_ids = [a.agent_id for a in assigned]
        if agent_id not in assigned_ids:
            await websocket.close(code=4003, reason="Access denied")
            return

    # ----------------------------------------------------------
    # 3: Accept connection and send initial data
    # ----------------------------------------------------------
    await manager.connect_client(agent_id, websocket)
    logger.info(f"👁 User '{username}' watching agent: {agent_id}")

    await websocket.send_text(json.dumps({
        "type": "connected",
        "agent_id": agent_id,
        "agent_status": agent.status,
        "message": f"Now watching agent: {agent_id}"
    }))

    latest_data = crud.get_latest_system_data(db, agent_db_id=agent.id)
    if latest_data:
        await websocket.send_text(json.dumps({
            "type": "system_data_update",
            "agent_id": agent_id,
            "data": {
                "os_name": latest_data.os_name,
                "os_version": latest_data.os_version,
                "cpu_model": latest_data.cpu_model,
                "cpu_cores": latest_data.cpu_cores,
                "cpu_usage_percent": latest_data.cpu_usage_percent,
                "ram_total_gb": latest_data.ram_total_gb,
                "ram_used_gb": latest_data.ram_used_gb,
                "ram_usage_percent": latest_data.ram_usage_percent,
                "disk_total_gb": latest_data.disk_total_gb,
                "disk_used_gb": latest_data.disk_used_gb,
                "disk_usage_percent": latest_data.disk_usage_percent,
                "uptime_hours": latest_data.uptime_hours,
            },
            "timestamp": latest_data.collected_at.isoformat() if latest_data.collected_at else None
        }, default=str))

    # ----------------------------------------------------------
    # 4: Keep connection open (receive any client messages)
    # ----------------------------------------------------------
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass

    except WebSocketDisconnect:
        logger.info(f"User '{username}' disconnected from agent: {agent_id}")
    except Exception as e:
        logger.error(f"Client WebSocket error: {e}")
    finally:
        manager.disconnect_client(agent_id, websocket)


# ==============================================================
# REST ENDPOINT: WebSocket Stats (for debugging)
# ==============================================================

@router.get("/stats")
def websocket_stats():
  
    return manager.get_connection_stats()
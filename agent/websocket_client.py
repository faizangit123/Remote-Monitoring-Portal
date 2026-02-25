"""
WebSocket Client
Manages the real-time connection between the agent and the backend server.
This is the "heart" of the agent — it keeps everything connected and running.
"""

import asyncio
import json
import logging
import time
from typing import Optional

import websockets
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
    InvalidHandshake
)

from config import config
from collector import SystemCollector
from command_handler import CommandHandler

logger = logging.getLogger(__name__)


class AgentWebSocketClient:

    def __init__(self):
        """Initialize the WebSocket client."""
        self.collector = SystemCollector()
        self.handler = CommandHandler(self.collector)

        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_running = False
        self.reconnect_count = 0

        logger.info(f"Agent initialized: {config.AGENT_ID}")
        logger.info(f"Server: {config.SERVER_HOST}:{config.SERVER_PORT}")

    # ===========================================================
    # MAIN ENTRY POINT
    # ===========================================================

    async def start(self):
        self.is_running = True
        logger.info(f"🚀 Starting agent: {config.AGENT_ID}")

        while self.is_running:
            try:
                await self._connect_and_run()

            except (ConnectionRefusedError, OSError) as e:
                logger.warning(f"⚠️ Cannot connect to server: {e}")

            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")

            if config.MAX_RECONNECT_ATTEMPTS > 0:
                self.reconnect_count += 1
                if self.reconnect_count >= config.MAX_RECONNECT_ATTEMPTS:
                    logger.error(f"Max reconnect attempts reached ({config.MAX_RECONNECT_ATTEMPTS}). Stopping.")
                    break

            logger.info(f"🔄 Reconnecting in {config.RECONNECT_DELAY} seconds...")
            await asyncio.sleep(config.RECONNECT_DELAY)

        logger.info("Agent stopped.")

    def stop(self):
        self.is_running = False
        logger.info("Stop signal received")

    # ===========================================================
    # CONNECTION MANAGEMENT
    # ===========================================================

    async def _connect_and_run(self):
        url = config.AGENT_WS_URL
        logger.info(f"🔌 Connecting to {config.SERVER_HOST}:{config.SERVER_PORT}...")

        async with websockets.connect(
            url,
            ping_interval=None,
            close_timeout=10
        ) as websocket:

            self.websocket = websocket
            self.reconnect_count = 0  # Reset counter on successful connect
            logger.info(f"✅ Connected to server!")

            send_task = asyncio.create_task(self._send_loop())
            receive_task = asyncio.create_task(self._receive_loop())
            heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            done, pending = await asyncio.wait(
                [send_task, receive_task, heartbeat_task],
                return_when=asyncio.FIRST_EXCEPTION
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Check if any task raised an exception
            for task in done:
                if task.exception():
                    raise task.exception()

    # ===========================================================
    # SEND LOOP — Sends data every N seconds
    # ===========================================================

    async def _send_loop(self):
        logger.info(f"📤 Send loop started (every {config.COLLECTION_INTERVAL}s)")

        await self._send_all_data()

        while True:
            # Wait for next collection interval
            await asyncio.sleep(config.COLLECTION_INTERVAL)

            if not self.websocket or self.websocket.closed:
                break

            await self._send_all_data()

    async def _send_all_data(self):
        try:
            logger.info("📊 Collecting system data...")

            system_data = self.collector.collect_all()
            await self._send_message({
                "type": "system_data",
                "data": system_data
            })

            await asyncio.sleep(1)

            logger.info("⚙️ Collecting processes...")
            processes = self.collector.collect_processes()
            await self._send_message({
                "type": "processes",
                "data": processes
            })

            await asyncio.sleep(1)

            partitions = self.collector.collect_disk_partitions()
            await self._send_message({
                "type": "disk_partitions",
                "data": partitions
            })

            await asyncio.sleep(1)

            network = self.collector.collect_network_info()
            await self._send_message({
                "type": "network_info",
                "data": network
            })

            await asyncio.sleep(1)

            users = self.collector.collect_users()
            await self._send_message({
                "type": "users",
                "data": users
            })

            logger.info("✅ All data sent successfully")

        except Exception as e:
            logger.error(f"Error sending data: {e}")
            raise  # Re-raise to trigger reconnect

    # ===========================================================
    # RECEIVE LOOP — Listens for commands from server
    # ===========================================================

    async def _receive_loop(self):
        logger.info("📥 Receive loop started")

        async for raw_message in self.websocket:
            # This loop runs automatically whenever server sends a message
            # It blocks here waiting for the next message

            try:
                message = json.loads(raw_message)
                await self._handle_server_message(message)

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from server: {raw_message[:100]}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")

        raise ConnectionClosed(None, None)

    async def _handle_server_message(self, message: dict):

        msg_type = message.get("type")

        if msg_type == "command":
            # Server is sending a command to execute
            command_id = message.get("command_id")
            command_type = message.get("command_type")
            command_data = message.get("command_data")

            logger.info(f"📨 Received command: {command_type} (ID: {command_id})")

            result = self.handler.execute(command_type, command_data)

            if command_type == "refresh_data" and result.get("success") and result.get("data"):
                await self._send_message({
                    "type": "system_data",
                    "data": result["data"]
                })

            if command_type == "get_processes" and result.get("success") and result.get("data"):
                await self._send_message({
                    "type": "processes",
                    "data": result["data"]
                })

            # Send command result back to server
            await self._send_message({
                "type": "command_result",
                "command_id": command_id,
                "success": result.get("success", False),
                "result": {
                    "message": result.get("message"),
                    "data": result.get("data") if command_type not in ["refresh_data", "get_processes"] else None
                }
            })

        elif msg_type == "pong":
            # Server acknowledged our heartbeat
            logger.debug("💓 Heartbeat acknowledged")

        else:
            logger.warning(f"Unknown message type from server: {msg_type}")

    # ===========================================================
    # HEARTBEAT LOOP — Keeps connection alive
    # ===========================================================

    async def _heartbeat_loop(self):
        logger.info(f"💓 Heartbeat loop started (every {config.HEARTBEAT_INTERVAL}s)")

        while True:
            await asyncio.sleep(config.HEARTBEAT_INTERVAL)

            if not self.websocket or self.websocket.closed:
                break

            try:
                await self._send_message({"type": "heartbeat"})
                logger.debug("💓 Heartbeat sent")
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                raise

    # ===========================================================
    # HELPER: Send a message
    # ===========================================================

    async def _send_message(self, data: dict):
        if not self.websocket or self.websocket.closed:
            raise Exception("WebSocket not connected")

        message_str = json.dumps(data, default=str)

        await self.websocket.send(message_str)
"""
Command Handler
Executes commands received from the server via WebSocket.
"""

import psutil
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CommandHandler:

    def __init__(self, collector):

        self.collector = collector
        self.command_map = {
            "refresh_data": self._handle_refresh_data,
            "kill_process": self._handle_kill_process,
            "get_processes": self._handle_get_processes,
        }

    def execute(
        self,
        command_type: str,
        command_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        logger.info(f"Executing command: {command_type} with data: {command_data}")

        # Look up the handler for this command type
        handler_func = self.command_map.get(command_type)

        if handler_func is None:
            return {
                "success": False,
                "message": f"Unknown command type: '{command_type}'",
                "data": None
            }

        try:
            result = handler_func(command_data or {})
            logger.info(f"Command '{command_type}' completed: {result.get('message')}")
            return result

        except Exception as e:
            logger.error(f"Command '{command_type}' failed with exception: {e}")
            return {
                "success": False,
                "message": f"Command failed: {str(e)}",
                "data": None
            }

    # ===========================================================
    # COMMAND HANDLERS
    # ===========================================================

    def _handle_refresh_data(self, data: Dict) -> Dict[str, Any]:
        try:
            fresh_data = self.collector.collect_all()
            return {
                "success": True,
                "message": "Data refreshed successfully",
                "data": fresh_data
                # The WebSocket handler will send this data to server
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to refresh data: {e}",
                "data": None
            }

    def _handle_kill_process(self, data: Dict) -> Dict[str, Any]:
        pid = data.get("pid")

        # Validate PID is provided
        if pid is None:
            return {
                "success": False,
                "message": "Missing required field: 'pid'",
                "data": None
            }

        # Convert to int (in case it came as a string)
        try:
            pid = int(pid)
        except (ValueError, TypeError):
            return {
                "success": False,
                "message": f"Invalid PID: {pid}. Must be a number.",
                "data": None
            }

        # Safety check: don't kill critical system processes
        if pid < 10:
            return {
                "success": False,
                "message": f"Cannot kill system process with PID {pid}",
                "data": None
            }

        # Try to find and kill the process
        try:
            process = psutil.Process(pid)

            process_name = process.name()

            process.terminate()

            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process.kill()
                logger.warning(f"Process {pid} ({process_name}) force-killed")

            return {
                "success": True,
                "message": f"Process {pid} ({process_name}) terminated successfully",
                "data": {"pid": pid, "name": process_name}
            }

        except psutil.NoSuchProcess:
            return {
                "success": False,
                "message": f"Process {pid} not found (already stopped?)",
                "data": None
            }

        except psutil.AccessDenied:
            return {
                "success": False,
                "message": f"Access denied: Cannot kill process {pid} (requires admin rights)",
                "data": None
            }

    def _handle_get_processes(self, data: Dict) -> Dict[str, Any]:

        try:
            processes = self.collector.collect_processes()
            return {
                "success": True,
                "message": f"Retrieved {len(processes)} processes",
                "data": processes
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get processes: {e}",
                "data": None
            }


# ===========================================================
# QUICK TEST
# ===========================================================

if __name__ == "__main__":
    from collector import SystemCollector

    print("=" * 50)
    print("COMMAND HANDLER TEST")
    print("=" * 50)

    collector = SystemCollector()
    handler = CommandHandler(collector)

    # Test 1: refresh_data
    print("\n1️⃣ Testing refresh_data command:")
    result = handler.execute("refresh_data")
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
    if result.get('data'):
        print(f"   CPU: {result['data'].get('cpu_usage_percent')}%")

    # Test 2: get_processes
    print("\n2️⃣ Testing get_processes command:")
    result = handler.execute("get_processes")
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # Test 3: unknown command
    print("\n3️⃣ Testing unknown command:")
    result = handler.execute("fly_to_moon")
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # Test 4: kill_process with invalid PID
    print("\n4️⃣ Testing kill_process with invalid PID:")
    result = handler.execute("kill_process", {"pid": 3})
    # PID 3 is a system process — should be rejected
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    # Test 5: kill_process with missing PID
    print("\n5️⃣ Testing kill_process with missing PID:")
    result = handler.execute("kill_process", {})
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")

    print("\n✅ Command handler tests complete!")
    print("=" * 50)
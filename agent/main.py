"""
Agent Main Entry Point
This is what runs when you double-click the .exe file.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# =============================================================
# SETUP LOGGING
# =============================================================

def setup_logging():

    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(app_dir, "agent.log")

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),

            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )

    return logging.getLogger(__name__)


# =============================================================
# MAIN FUNCTION
# =============================================================

async def main():

    logger = setup_logging()

    # Print startup banner
    print("=" * 60)
    print("  REMOTE MONITORING AGENT")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    from config import config
    from websocket_client import AgentWebSocketClient

    # Print configuration
    logger.info(f"Agent ID:  {config.AGENT_ID}")
    logger.info(f"Server:    {config.SERVER_HOST}:{config.SERVER_PORT}")
    logger.info(f"Interval:  every {config.COLLECTION_INTERVAL} seconds")

    # Create and start the agent
    agent = AgentWebSocketClient()

    try:
        await agent.start()

    except KeyboardInterrupt:
        logger.info("\n⛔ Agent stopped by user (Ctrl+C)")
        agent.stop()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n👋 Agent stopped.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        input("\nPress Enter to exit...")  # Keep window open to see error
        sys.exit(1)
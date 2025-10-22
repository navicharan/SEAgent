#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Software Engineering Agent (SEAgent)
Main application entry point - Simplified version
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
import subprocess
import time

# Setup Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
try:
    from config.settings_simple import Settings
    from orchestrator.agent_coordinator import AgentCoordinator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SEAgent:
    """Simplified SEAgent application without complex dashboard management"""
    
    def __init__(self):
        self.settings = Settings()
        self.coordinator = None
        self.dashboard_process = None
    
    def start_dashboard(self):
        """Start a simple HTML dashboard as part of the API server"""
        try:
            logger.info("Dashboard will be served at /dashboard endpoint of API server")
            logger.info("No separate dashboard process needed")
            self.dashboard_process = None  # No separate process
            
        except Exception as e:
            logger.error(f"Failed to setup dashboard: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def start_api_server(self):
        """Start the API server"""
        try:
            # Import the proper API server with GitHub integration
            from api.server import APIServer
            import uvicorn
            
            # Create API server instance with coordinator
            api_server = APIServer(self.coordinator, self.settings)
            app = api_server.app
            
            # Start server
            config = uvicorn.Config(
                app, 
                host=self.settings.api.host,
                port=self.settings.api.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"API server error: {e}")
    
    async def start(self):
        """Start the application"""
        try:
            print("🚀 Starting SEAgent - Autonomous Software Engineering System")
            print("=" * 70)
            
            # Initialize coordinator
            print("📋 Initializing agent coordinator...")
            self.coordinator = AgentCoordinator(self.settings)
            print("🔧 Calling coordinator.initialize()...")
            await self.coordinator.initialize()
            print("✅ All agents initialized successfully")
            
            # Start dashboard in background
            print("🖥️ Starting dashboard...")
            self.start_dashboard()
            
            # Give dashboard time to start
            await asyncio.sleep(3)
            
            print("✅ Application started successfully!")
            print(f"🌐 API Server: http://localhost:{self.settings.api.port}")
            print(f"🖥️ Dashboard: http://localhost:{self.settings.api.port}/dashboard")
            print(f"📚 API Docs: http://localhost:{self.settings.api.port}/docs")
            print("=" * 70)
            print("Press Ctrl+C to stop")
            
            # Start API server (this will block)
            await self.start_api_server()
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.stop()
        except Exception as e:
            import traceback
            print(f"Exception details: {type(e).__name__}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            logger.error(f"Application error: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the application"""
        try:
            if self.dashboard_process:
                self.dashboard_process.terminate()
            
            if self.coordinator:
                await self.coordinator.shutdown()
            
            logger.info("SEAgent stopped")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start SEAgent
    seagent = SEAgent()
    await seagent.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 SEAgent stopped by user")
    except Exception as e:
        print(f"❌ SEAgent failed to start: {e}")
        sys.exit(1)

"""
Vercel entrypoint for SEAgent API
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings_simple import Settings
from orchestrator.agent_coordinator import AgentCoordinator
from api.server import APIServer

# Initialize settings
settings = Settings()

# Initialize coordinator (will be done on first request in serverless)
coordinator = AgentCoordinator(settings)

# Create API server instance
api_server = APIServer(coordinator, settings)

# Export the FastAPI app for Vercel
app = api_server.app

# Vercel serverless function needs initialization on cold start
@app.on_event("startup")
async def startup_event():
    """Initialize coordinator on startup"""
    if not coordinator.initialized:
        await coordinator.initialize()

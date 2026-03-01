"""
Vercel entrypoint for SEAgent API
Optimized for serverless deployment with lazy initialization
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

# Global coordinator instance (lazy initialization)
coordinator = None
api_server_instance = None

def get_coordinator():
    """Get or create coordinator instance"""
    global coordinator
    if coordinator is None:
        coordinator = AgentCoordinator(settings)
        coordinator.initialized = False  # Mark as not initialized
    return coordinator

def get_app():
    """Get or create FastAPI app instance"""
    global api_server_instance
    if api_server_instance is None:
        coord = get_coordinator()
        api_server_instance = APIServer(coord, settings)
    return api_server_instance.app

# Export the FastAPI app for Vercel
app = get_app()

# Lazy initialization middleware - initialize on first request
@app.middleware("http")
async def initialize_on_request(request, call_next):
    """Initialize coordinator on first request"""
    coord = get_coordinator()
    if not coord.initialized:
        try:
            # Mark as initializing to prevent concurrent initializations
            coord.initialized = True
            # Initialize agents without starting background loops (serverless)
            for agent_name, agent in coord.agents.items():
                if not agent.is_initialized:
                    await agent.initialize()
        except Exception as e:
            import logging
            logging.error(f"Failed to initialize coordinator: {e}")
            coord.initialized = False
    
    response = await call_next(request)
    return response

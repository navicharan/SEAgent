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
            # Import required modules
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            from pydantic import BaseModel
            import uvicorn
            
            # Create FastAPI app
            app = FastAPI(title="SEAgent API", version="1.0.0")
            
            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Basic health endpoint
            @app.get("/")
            async def root():
                return {"message": "SEAgent API", "status": "running", "docs": "/docs"}
            
            @app.get("/health")
            async def health():
                return {"status": "healthy", "message": "SEAgent API is running"}
            
            # Agent status endpoint
            @app.get("/agents/status")
            async def get_agents_status():
                if self.coordinator:
                    status = {}
                    for agent_name, agent in self.coordinator.agents.items():
                        status[agent_name] = {
                            "initialized": agent.is_initialized,
                            "capabilities": list(agent.capabilities.keys())
                        }
                    return status
                return {"error": "Coordinator not initialized"}

            # Dashboard endpoint
            @app.get("/dashboard")
            async def dashboard():
                from fastapi.responses import HTMLResponse
                
                # Simple HTML dashboard
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>SEAgent Dashboard</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                        .header { text-align: center; margin-bottom: 30px; }
                        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                        .agent-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; }
                        .agent-title { font-weight: bold; color: #495057; margin-bottom: 10px; }
                        .status-healthy { color: #28a745; }
                        .capabilities { font-size: 0.9em; color: #6c757d; }
                        .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
                        .api-links { text-align: center; margin-top: 20px; }
                        .api-links a { margin: 0 10px; text-decoration: none; color: #007bff; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🤖 SEAgent Dashboard</h1>
                            <p>Autonomous Software Engineering System</p>
                        </div>
                        
                        <div style="text-align: center; margin-bottom: 20px;">
                            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
                        </div>
                        
                        <div class="status-grid" id="agents-status">
                            <div class="agent-card">Loading agents...</div>
                        </div>
                        
                        <div class="api-links">
                            <a href="/docs" target="_blank">📚 API Documentation</a>
                            <a href="/health" target="_blank">❤️ Health Check</a>
                            <a href="/agents/status" target="_blank">🔍 Agent Status JSON</a>
                        </div>
                    </div>
                    
                    <script>
                        function loadAgentStatus() {
                            fetch('/agents/status')
                                .then(response => response.json())
                                .then(data => {
                                    const container = document.getElementById('agents-status');
                                    if (data.error) {
                                        container.innerHTML = '<div class="agent-card">Error: ' + data.error + '</div>';
                                        return;
                                    }
                                    
                                    let html = '';
                                    for (const [agentName, status] of Object.entries(data)) {
                                        html += `
                                            <div class="agent-card">
                                                <div class="agent-title">${agentName.replace('_', ' ').toUpperCase()}</div>
                                                <div class="status-healthy">Status: ${status.initialized ? '✅ Initialized' : '❌ Not Initialized'}</div>
                                                <div class="capabilities">
                                                    <strong>Capabilities:</strong><br>
                                                    ${status.capabilities.length > 0 ? status.capabilities.join(', ') : 'None'}
                                                </div>
                                            </div>
                                        `;
                                    }
                                    container.innerHTML = html;
                                })
                                .catch(error => {
                                    document.getElementById('agents-status').innerHTML = 
                                        '<div class="agent-card">Error loading status: ' + error + '</div>';
                                });
                        }
                        
                        // Load status on page load
                        loadAgentStatus();
                        
                        // Auto-refresh every 10 seconds
                        setInterval(loadAgentStatus, 10000);
                    </script>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)
            
            # Task submission endpoint
            class TaskRequest(BaseModel):
                agent_type: str
                task_type: str
                parameters: dict
            
            @app.post("/tasks/submit")
            async def submit_task(task: TaskRequest):
                if not self.coordinator:
                    return {"error": "Coordinator not initialized"}
                
                try:
                    # Import here to avoid circular imports
                    from orchestrator.agent_coordinator import TaskType
                    import uuid
                    import time
                    
                    # Create a simple task dict instead of Task object for now
                    task_id = str(uuid.uuid4())
                    
                    # Simple task execution without complex Task object
                    if hasattr(self.coordinator, 'agents') and task.agent_type in self.coordinator.agents:
                        agent = self.coordinator.agents[task.agent_type]
                        if agent.is_initialized:
                            # Execute task directly on agent
                            result = await agent.execute_task(task.parameters)
                            return {
                                "task_id": task_id,
                                "status": "completed",
                                "result": result
                            }
                        else:
                            return {"error": f"Agent {task.agent_type} not initialized"}
                    else:
                        return {"error": f"Agent {task.agent_type} not found"}
                    
                except Exception as e:
                    logger.error(f"Task submission error: {e}")
                    return {"error": str(e)}
            
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

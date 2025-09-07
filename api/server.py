"""
API Server - REST API for external integrations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from orchestrator.agent_coordinator import AgentCoordinator, Task, TaskType, TaskStatus


class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    language: str
    framework: Optional[str] = None
    requirements: str


class TaskSubmitRequest(BaseModel):
    project_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 5


class WorkflowExecuteRequest(BaseModel):
    project_id: str
    workflow_name: str
    parameters: Dict[str, Any]


class CodeGenerationRequest(BaseModel):
    requirements: str
    language: str
    framework: Optional[str] = None
    context: Dict[str, Any] = {}


class SecurityScanRequest(BaseModel):
    source_code: Optional[str] = None
    project_id: Optional[str] = None
    scan_type: str = "comprehensive"


class DebugRequest(BaseModel):
    source_code: str
    error_log: Optional[str] = None
    language: str = "python"


class TestingRequest(BaseModel):
    source_code: str
    test_type: str = "functional"
    test_framework: str = "pytest"


class APIServer:
    """REST API server for SEAgent"""
    
    def __init__(self, coordinator: AgentCoordinator, settings):
        self.coordinator = coordinator
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="SEAgent API",
            description="Autonomous Software Engineering Agent API",
            version="1.0.0",
            docs_url="/docs",  # Swagger UI at /docs
            redoc_url="/redoc"  # ReDoc at /redoc
        )
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Track projects and tasks
        self.projects: Dict[str, Dict[str, Any]] = {}
        
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint - should return API info"""
            return {
                "message": "SEAgent API is running",
                "version": "1.0.0",
                "docs": "/docs",
                "status": "operational"
            }
        
        # Health check
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "service": "SEAgent API"}
        
        # Projects
        @self.app.post("/api/v1/projects")
        async def create_project(request: ProjectCreateRequest):
            project_id = f"project_{len(self.projects) + 1}"
            
            project = {
                "id": project_id,
                "name": request.name,
                "description": request.description,
                "language": request.language,
                "framework": request.framework,
                "requirements": request.requirements,
                "created_at": datetime.utcnow().isoformat(),
                "status": "created"
            }
            
            self.projects[project_id] = project
            
            return {"project_id": project_id, "project": project}
        
        @self.app.get("/api/v1/projects")
        async def list_projects():
            return {"projects": list(self.projects.values())}
        
        @self.app.get("/api/v1/projects/{project_id}")
        async def get_project(project_id: str):
            if project_id not in self.projects:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project = self.projects[project_id]
            project_status = await self.coordinator.get_project_status(project_id)
            
            return {
                "project": project,
                "status": project_status
            }
        
        # Tasks
        @self.app.post("/api/v1/tasks")
        async def submit_task(request: TaskSubmitRequest):
            try:
                task = Task(
                    id=f"task_{len(self.coordinator.tasks) + 1}",
                    type=TaskType(request.task_type),
                    priority=request.priority,
                    project_id=request.project_id,
                    parameters=request.parameters
                )
                
                task_id = await self.coordinator.submit_task(task)
                
                return {"task_id": task_id, "status": "submitted"}
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/v1/tasks/{task_id}")
        async def get_task_status(task_id: str):
            task_status = await self.coordinator.get_task_status(task_id)
            
            if task_status is None:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return {"task": task_status}
        
        # Workflows
        @self.app.post("/api/v1/workflows/execute")
        async def execute_workflow(request: WorkflowExecuteRequest):
            try:
                task_ids = await self.coordinator.execute_workflow(
                    request.workflow_name,
                    request.project_id,
                    request.parameters
                )
                
                return {
                    "workflow": request.workflow_name,
                    "project_id": request.project_id,
                    "task_ids": task_ids,
                    "status": "started"
                }
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/v1/workflows")
        async def list_workflows():
            return {
                "workflows": [
                    "full_development_cycle",
                    "security_focused", 
                    "performance_optimization"
                ]
            }
        
        # Specialized endpoints
        @self.app.post("/api/v1/generate")
        async def generate_code(request: CodeGenerationRequest):
            task = Task(
                id=f"gen_task_{len(self.coordinator.tasks) + 1}",
                type=TaskType.CODE_GENERATION,
                priority=1,
                project_id="direct",
                parameters={
                    "task_type": "generate_code",
                    "requirements": request.requirements,
                    "language": request.language,
                    "framework": request.framework,
                    "context": request.context
                }
            )
            
            task_id = await self.coordinator.submit_task(task)
            
            return {
                "task_id": task_id,
                "status": "generating",
                "message": "Code generation started"
            }
        
        @self.app.post("/api/v1/security/scan")
        async def security_scan(request: SecurityScanRequest):
            parameters = {
                "task_type": "static_analysis",
                "scan_type": request.scan_type
            }
            
            if request.source_code:
                parameters["source_code"] = request.source_code
            
            if request.project_id:
                parameters["project_id"] = request.project_id
            
            task = Task(
                id=f"sec_task_{len(self.coordinator.tasks) + 1}",
                type=TaskType.SECURITY_ANALYSIS,
                priority=2,
                project_id=request.project_id or "direct",
                parameters=parameters
            )
            
            task_id = await self.coordinator.submit_task(task)
            
            return {
                "task_id": task_id,
                "status": "scanning",
                "message": "Security scan started"
            }
        
        @self.app.post("/api/v1/debug")
        async def debug_code(request: DebugRequest):
            task = Task(
                id=f"debug_task_{len(self.coordinator.tasks) + 1}",
                type=TaskType.DEBUGGING,
                priority=1,
                project_id="direct",
                parameters={
                    "task_type": "error_analysis",
                    "source_code": request.source_code,
                    "error_log": request.error_log or "",
                    "language": request.language
                }
            )
            
            task_id = await self.coordinator.submit_task(task)
            
            return {
                "task_id": task_id,
                "status": "debugging",
                "message": "Debug analysis started"
            }
        
        @self.app.post("/api/v1/test")
        async def run_tests(request: TestingRequest):
            task = Task(
                id=f"test_task_{len(self.coordinator.tasks) + 1}",
                type=TaskType.TESTING,
                priority=3,
                project_id="direct",
                parameters={
                    "task_type": request.test_type + "_testing",
                    "source_code": request.source_code,
                    "test_framework": request.test_framework
                }
            )
            
            task_id = await self.coordinator.submit_task(task)
            
            return {
                "task_id": task_id,
                "status": "testing",
                "message": f"{request.test_type.title()} testing started"
            }
        
        # Agent status
        @self.app.get("/api/v1/agents/status")
        async def get_agents_status():
            agents_status = {}
            
            for agent_name, agent in self.coordinator.agents.items():
                agents_status[agent_name] = await agent.health_check()
            
            return {"agents": agents_status}
        
        @self.app.get("/api/v1/agents/{agent_name}/capabilities")
        async def get_agent_capabilities(agent_name: str):
            if agent_name not in self.coordinator.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent = self.coordinator.agents[agent_name]
            capabilities = await agent.get_capabilities()
            
            return {
                "agent": agent_name,
                "capabilities": {
                    name: {
                        "description": cap.description,
                        "input_schema": cap.input_schema,
                        "output_schema": cap.output_schema
                    }
                    for name, cap in capabilities.items()
                }
            }
        
        # Statistics and monitoring
        @self.app.get("/api/v1/stats")
        async def get_system_stats():
            total_tasks = len(self.coordinator.tasks)
            running_tasks = len(self.coordinator.running_tasks)
            
            task_status_counts = {}
            for status in TaskStatus:
                task_status_counts[status.value] = len([
                    t for t in self.coordinator.tasks.values() 
                    if t.status == status
                ])
            
            return {
                "total_projects": len(self.projects),
                "total_tasks": total_tasks,
                "running_tasks": running_tasks,
                "task_status_breakdown": task_status_counts,
                "agents_status": {
                    name: agent.is_initialized 
                    for name, agent in self.coordinator.agents.items()
                }
            }
        
        # Configuration
        @self.app.get("/api/v1/config")
        async def get_config():
            return {
                "environment": self.settings.environment,
                "debug": self.settings.debug,
                "agents": {
                    name: {
                        "enabled": config.enabled,
                        "max_concurrent_tasks": config.max_concurrent_tasks,
                        "timeout": config.timeout
                    }
                    for name, config in [
                        ("code_generation", self.settings.agents.code_generation),
                        ("security_analysis", self.settings.agents.security_analysis),
                        ("debug", self.settings.agents.debug),
                        ("performance", self.settings.agents.performance),
                        ("integration", self.settings.agents.integration),
                        ("testing", self.settings.agents.testing)
                    ]
                }
            }
    
    async def start(self):
        """Start the API server"""
        self.logger.info(f"Starting API server on {self.settings.api.host}:{self.settings.api.port}")
        
        config = uvicorn.Config(
            self.app,
            host=self.settings.api.host,
            port=self.settings.api.port,
            log_level=self.settings.logging.level.lower()
        )
        
        self.server = uvicorn.Server(config)
        
        # Start server in background
        asyncio.create_task(self.server.serve())
    
    async def stop(self):
        """Stop the API server"""
        self.logger.info("Stopping API server")
        if hasattr(self, 'server'):
            self.server.should_exit = True

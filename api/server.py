"""
API Server - REST API for external integrations with GitHub Integration
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
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


class CodeGenerationWithEvaluationRequest(BaseModel):
    requirements: str
    language: str
    framework: Optional[str] = None
    context: Dict[str, Any] = {}
    run_evaluation: bool = True


class EvaluationRequest(BaseModel):
    code: str
    language: str = "python"
    evaluation_type: str = "comprehensive"  # "humaneval", "securityeval", "comprehensive"
    problem_ids: Optional[List[str]] = None
    security_categories: Optional[List[str]] = None


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


class GitHubUploadRequest(BaseModel):
    repository_name: str
    owner: str
    files: Dict[str, str]  # filename -> content
    commit_message: str
    branch: str = "main"
    create_pr: bool = False
    pr_title: Optional[str] = None
    pr_description: Optional[str] = None


class GitHubCreateRepoRequest(BaseModel):
    name: str
    description: str
    private: bool = False
    auto_init: bool = True
    gitignore_template: Optional[str] = "Python"
    license_template: Optional[str] = "MIT"


class GitHubRepositoryRequest(BaseModel):
    repository_name: str
    owner: str
    action: str  # 'analyze', 'optimize', 'create_pr'
    data: Optional[Dict[str, Any]] = None


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
        
        # GitHub Integration Frontend
        @self.app.get("/github")
        async def github_interface():
            """Serve GitHub integration frontend"""
            from fastapi.responses import FileResponse
            import os
            
            html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "github_integration.html")
            if os.path.exists(html_path):
                return FileResponse(html_path, media_type="text/html")
            else:
                raise HTTPException(status_code=404, detail="GitHub interface not found")
        
        # Dashboard endpoint  
        @self.app.get("/dashboard")
        async def dashboard():
            """Serve main dashboard interface"""
            from fastapi.responses import HTMLResponse
            
            # Enhanced HTML dashboard with code generation capabilities
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SEAgent Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                        margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        min-height: 100vh; color: #333;
                    }
                    .container { 
                        max-width: 1200px; margin: 0 auto; padding: 20px; 
                    }
                    .header { 
                        text-align: center; margin-bottom: 40px; color: white; 
                        padding: 40px 0;
                    }
                    .header h1 { 
                        font-size: 3em; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); 
                    }
                    .header p { 
                        font-size: 1.2em; opacity: 0.9; margin: 10px 0 0 0; 
                    }
                    .main-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                        gap: 30px;
                        margin-bottom: 40px;
                    }
                    .card { 
                        background: white; border-radius: 15px; padding: 30px; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }
                    .card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                    }
                    .card-title { 
                        font-size: 1.4em; font-weight: bold; margin-bottom: 15px; 
                        color: #2c3e50; display: flex; align-items: center; gap: 10px;
                    }
                    .card-icon { font-size: 1.5em; }
                    .btn { 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border: none; padding: 12px 24px; 
                        border-radius: 8px; cursor: pointer; font-size: 16px; 
                        text-decoration: none; display: inline-block; 
                        transition: all 0.3s ease; font-weight: 500;
                    }
                    .btn:hover { 
                        transform: translateY(-2px); 
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); 
                    }
                    .btn-github { 
                        background: linear-gradient(135deg, #24292e 0%, #586069 100%); 
                    }
                    .btn-docs { 
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    }
                    .status-grid { 
                        display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                        gap: 15px; margin-top: 20px; 
                    }
                    .status-card { 
                        background: #f8f9fa; border-radius: 10px; padding: 20px; 
                        border-left: 4px solid #28a745; text-align: center;
                    }
                    .status-title { font-weight: bold; color: #495057; margin-bottom: 8px; }
                    .status-value { font-size: 1.2em; color: #28a745; font-weight: bold; }
                    .feature-list {
                        list-style: none; padding: 0; margin: 15px 0;
                    }
                    .feature-list li {
                        padding: 8px 0; color: #666;
                        border-bottom: 1px solid #eee;
                    }
                    .feature-list li:last-child { border-bottom: none; }
                    .feature-list li:before {
                        content: "✓"; color: #28a745; font-weight: bold;
                        margin-right: 10px;
                    }
                    .quick-actions {
                        display: flex; gap: 15px; flex-wrap: wrap; margin-top: 20px;
                    }
                    .footer {
                        text-align: center; margin-top: 50px; color: white;
                        opacity: 0.8; padding: 20px 0;
                    }
                    .stats-row {
                        display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 15px; margin: 20px 0;
                    }
                    .stat-item {
                        text-align: center; padding: 15px;
                        background: rgba(255,255,255,0.1); border-radius: 10px;
                        color: white;
                    }
                    .stat-number { font-size: 2em; font-weight: bold; display: block; }
                    .stat-label { font-size: 0.9em; opacity: 0.8; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 SEAgent Dashboard</h1>
                        <p>Autonomous Software Engineering Multi-Agent System</p>
                        
                        <div class="stats-row" id="systemStats">
                            <div class="stat-item">
                                <span class="stat-number" id="agentCount">6</span>
                                <span class="stat-label">Active Agents</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number" id="taskCount">0</span>
                                <span class="stat-label">Tasks Completed</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number" id="uptime">00:00</span>
                                <span class="stat-label">Uptime</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="main-grid">
                        <!-- GitHub Integration Card -->
                        <div class="card">
                            <div class="card-title">
                                <span class="card-icon">🐙</span>
                                GitHub Integration
                            </div>
                            <p>Generate code with AI and upload directly to GitHub repositories. Create projects, manage files, and automate your development workflow.</p>
                            <ul class="feature-list">
                                <li>AI Code Generation</li>
                                <li>Direct GitHub Upload</li>
                                <li>Repository Management</li>
                                <li>Pull Request Creation</li>
                            </ul>
                            <div class="quick-actions">
                                <a href="/github" class="btn btn-github">🚀 Open GitHub Integration</a>
                            </div>
                        </div>
                        
                        <!-- Agent Status Card -->
                        <div class="card">
                            <div class="card-title">
                                <span class="card-icon">⚡</span>
                                Multi-Agent System
                            </div>
                            <p>Monitor and control the autonomous agent ecosystem. View status, capabilities, and performance metrics.</p>
                            <div class="status-grid" id="agentStatusGrid">
                                <div class="status-card">
                                    <div class="status-title">Loading...</div>
                                    <div class="status-value">---</div>
                                </div>
                            </div>
                            <div class="quick-actions">
                                <button class="btn" onclick="refreshAgentStatus()">🔄 Refresh Status</button>
                            </div>
                        </div>
                        
                        <!-- API & Documentation Card -->
                        <div class="card">
                            <div class="card-title">
                                <span class="card-icon">📚</span>
                                API & Documentation
                            </div>
                            <p>Explore the comprehensive REST API, view interactive documentation, and access system health metrics.</p>
                            <ul class="feature-list">
                                <li>Interactive API Docs</li>
                                <li>Health Monitoring</li>
                                <li>Real-time Metrics</li>
                                <li>Configuration Access</li>
                            </ul>
                            <div class="quick-actions">
                                <a href="/docs" class="btn btn-docs">📖 API Documentation</a>
                                <a href="/health" class="btn">💚 Health Check</a>
                            </div>
                        </div>
                        
                        <!-- System Configuration Card -->
                        <div class="card">
                            <div class="card-title">
                                <span class="card-icon">⚙️</span>
                                System Configuration
                            </div>
                            <p>View system configuration, environment settings, and connected services status.</p>
                            <div id="configStatus">
                                <p>Loading configuration...</p>
                            </div>
                            <div class="quick-actions">
                                <button class="btn" onclick="loadSystemConfig()">🔧 Load Config</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>🤖 SEAgent - Autonomous Software Engineering System</p>
                        <p>Multi-Agent Architecture for Code Generation, Security Analysis, and Performance Optimization</p>
                    </div>
                </div>
                
                <script>
                    // Auto-refresh status every 30 seconds
                    setInterval(refreshAgentStatus, 30000);
                    setInterval(updateUptime, 1000);
                    
                    let startTime = Date.now();
                    
                    function updateUptime() {
                        const uptime = Math.floor((Date.now() - startTime) / 1000);
                        const hours = Math.floor(uptime / 3600);
                        const minutes = Math.floor((uptime % 3600) / 60);
                        const seconds = uptime % 60;
                        document.getElementById('uptime').textContent = 
                            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    }
                    
                    async function refreshAgentStatus() {
                        try {
                            const response = await fetch('/api/v1/agents/status');
                            const data = await response.json();
                            
                            const container = document.getElementById('agentStatusGrid');
                            let html = '';
                            let activeCount = 0;
                            
                            for (const [agentName, status] of Object.entries(data)) {
                                if (status.initialized) activeCount++;
                                html += `
                                    <div class="status-card">
                                        <div class="status-title">${agentName.replace('_', ' ')}</div>
                                        <div class="status-value">${status.initialized ? '✅ Active' : '❌ Inactive'}</div>
                                    </div>
                                `;
                            }
                            
                            container.innerHTML = html;
                            document.getElementById('agentCount').textContent = activeCount;
                            
                        } catch (error) {
                            document.getElementById('agentStatusGrid').innerHTML = 
                                '<div class="status-card"><div class="status-title">Error</div><div class="status-value">Failed to load</div></div>';
                        }
                    }
                    
                    async function loadSystemConfig() {
                        try {
                            const response = await fetch('/api/v1/config');
                            const config = await response.json();
                            
                            const configDiv = document.getElementById('configStatus');
                            configDiv.innerHTML = `
                                <ul class="feature-list">
                                    <li>API Host: ${config.api?.host || 'localhost'}:${config.api?.port || 8000}</li>
                                    <li>Environment: ${config.environment || 'development'}</li>
                                    <li>GitHub Integration: ${config.github?.enabled ? '✅ Enabled' : '❌ Disabled'}</li>
                                    <li>AI Model: ${config.ai?.model || 'DeepSeek-Coder'}</li>
                                </ul>
                            `;
                        } catch (error) {
                            document.getElementById('configStatus').innerHTML = 
                                '<p style="color: #dc3545;">Failed to load configuration</p>';
                        }
                    }
                    
                    // Initial loads
                    refreshAgentStatus();
                    loadSystemConfig();
                </script>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)

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
        
        @self.app.post("/api/generate-with-evaluation")
        async def generate_code_with_evaluation(request: CodeGenerationWithEvaluationRequest):
            """Generate code and automatically evaluate with HumanEval and SecurityEval"""
            try:
                # Get the code generation agent directly
                code_agent = self.coordinator.agents.get('code_generation')
                if not code_agent:
                    raise HTTPException(status_code=503, detail="Code generation agent not available")
                
                # Prepare parameters for the agent
                parameters = {
                    "task_type": "generate_with_evaluation",
                    "requirements": request.requirements,
                    "language": request.language,
                    "framework": request.framework,
                    "context": request.context,
                    "run_evaluation": request.run_evaluation
                }
                
                # Call the agent's execute_task method
                result = await asyncio.wait_for(
                    code_agent.execute_task(parameters),
                    timeout=120.0  # Extended timeout for evaluation
                )
                
                if isinstance(result, dict):
                    return {
                        "success": True,
                        "code": result.get("code", ""),
                        "explanation": result.get("explanation", ""),
                        "language": request.language,
                        "framework": request.framework,
                        "files": result.get("files", []),
                        "dependencies": result.get("dependencies", []),
                        "quality_score": result.get("quality_score", 0),
                        "evaluation_results": result.get("evaluation_results", {}),
                        "recommendations": result.get("recommendations", []),
                        "metadata": {
                            "generated_at": datetime.utcnow().isoformat(),
                            "agent": "code_generation",
                            "evaluation_enabled": request.run_evaluation
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid result format",
                        "code": "",
                        "explanation": "Generation failed - invalid result format"
                    }
                    
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="Code generation and evaluation timed out")
            except Exception as e:
                self.logger.error(f"Generate with evaluation error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "code": "",
                    "explanation": f"Generation failed: {e}"
                }
        
        @self.app.post("/api/v1/evaluate")
        async def evaluate_code(request: EvaluationRequest):
            """Evaluate existing code with HumanEval and SecurityEval"""
            try:
                # Check if evaluation engine is available
                code_agent = self.coordinator.agents.get('code_generation')
                if not code_agent or not hasattr(code_agent, 'evaluation_engine') or not code_agent.evaluation_engine:
                    raise HTTPException(status_code=503, detail="Evaluation engine not available")
                
                evaluation_engine = code_agent.evaluation_engine
                
                # Prepare parameters based on evaluation type
                parameters = {
                    "code": request.code,
                    "language": request.language
                }
                
                if request.evaluation_type == "humaneval":
                    parameters["task_type"] = "evaluate_humaneval"
                    if request.problem_ids:
                        parameters["problem_ids"] = request.problem_ids
                elif request.evaluation_type == "securityeval":
                    parameters["task_type"] = "evaluate_securityeval"
                    if request.security_categories:
                        parameters["security_categories"] = request.security_categories
                else:  # comprehensive
                    parameters["task_type"] = "comprehensive_evaluation"
                    parameters["evaluation_config"] = {
                        "weights": {
                            "correctness": 0.4,
                            "security": 0.4,
                            "performance": 0.2
                        }
                    }
                
                # Execute evaluation
                result = await asyncio.wait_for(
                    evaluation_engine.execute_task(parameters),
                    timeout=60.0
                )
                
                return {
                    "success": True,
                    "evaluation_type": request.evaluation_type,
                    "code": request.code,
                    "language": request.language,
                    "results": result,
                    "evaluated_at": datetime.utcnow().isoformat()
                }
                
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="Code evaluation timed out")
            except Exception as e:
                self.logger.error(f"Code evaluation error: {e}")
                raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
        
        @self.app.get("/api/v1/evaluation/datasets")
        async def get_evaluation_datasets():
            """Get information about available evaluation datasets"""
            try:
                code_agent = self.coordinator.agents.get('code_generation')
                if not code_agent or not hasattr(code_agent, 'evaluation_engine') or not code_agent.evaluation_engine:
                    raise HTTPException(status_code=503, detail="Evaluation engine not available")
                
                evaluation_engine = code_agent.evaluation_engine
                
                # Get dataset information
                humaneval_count = len(evaluation_engine.humaneval_dataset) if hasattr(evaluation_engine, 'humaneval_dataset') else 0
                securityeval_count = len(evaluation_engine.securityeval_dataset) if hasattr(evaluation_engine, 'securityeval_dataset') else 0
                
                return {
                    "datasets": {
                        "humaneval": {
                            "name": "HumanEval",
                            "description": "Evaluates functional correctness of code",
                            "total_problems": humaneval_count,
                            "categories": ["algorithms", "data_structures", "math", "string_processing"],
                            "languages": ["python"]
                        },
                        "securityeval": {
                            "name": "SecurityEval", 
                            "description": "Evaluates security vulnerabilities and compliance",
                            "total_problems": securityeval_count,
                            "categories": ["input_validation", "authentication", "file_operations", "sql_operations", "crypto_operations"],
                            "languages": ["python"]
                        }
                    },
                    "evaluation_types": [
                        {
                            "type": "humaneval",
                            "name": "HumanEval Correctness",
                            "description": "Tests functional correctness and algorithmic accuracy"
                        },
                        {
                            "type": "securityeval", 
                            "name": "SecurityEval Compliance",
                            "description": "Tests security vulnerabilities and compliance"
                        },
                        {
                            "type": "comprehensive",
                            "name": "Comprehensive Analysis",
                            "description": "Combined correctness, security, and performance evaluation"
                        }
                    ]
                }
                
            except Exception as e:
                self.logger.error(f"Dataset info error: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to get dataset info: {str(e)}")
        
        @self.app.get("/api/v1/evaluation/metrics")
        async def get_evaluation_metrics():
            """Get detailed evaluation metrics and scoring methodology"""
            return {
                "scoring_methodology": {
                    "overall_score": {
                        "description": "Weighted combination of correctness, security, and performance",
                        "weights": {
                            "correctness": 0.4,
                            "security": 0.4,
                            "performance": 0.2
                        },
                        "range": "0-100"
                    },
                    "correctness_score": {
                        "description": "Percentage of HumanEval tests passed",
                        "calculation": "(passed_tests / total_tests) * 100",
                        "range": "0-100"
                    },
                    "security_score": {
                        "description": "Security vulnerability assessment",
                        "factors": ["vulnerability_count", "severity_weights", "compliance_checks"],
                        "range": "0-100"
                    },
                    "performance_score": {
                        "description": "Code execution efficiency",
                        "factors": ["execution_time", "memory_usage", "algorithmic_complexity"],
                        "range": "0-100"
                    }
                },
                "vulnerability_severities": {
                    "critical": {"weight": 25, "color": "#8e44ad", "description": "Immediate security risk"},
                    "high": {"weight": 15, "color": "#e74c3c", "description": "Significant security risk"},
                    "medium": {"weight": 10, "color": "#f39c12", "description": "Moderate security risk"},
                    "low": {"weight": 5, "color": "#f1c40f", "description": "Low security risk"}
                },
                "performance_benchmarks": {
                    "excellent": {"threshold": "< 0.1s", "score_range": "90-100"},
                    "good": {"threshold": "0.1-0.5s", "score_range": "70-89"},
                    "acceptable": {"threshold": "0.5-1.0s", "score_range": "50-69"},
                    "poor": {"threshold": "> 1.0s", "score_range": "0-49"}
                }
            }
        
        @self.app.post("/api/v1/generate/direct")
        async def generate_code_direct(request: CodeGenerationRequest):
            """Direct code generation endpoint that returns code immediately"""
            try:
                # Get the code generation agent directly
                code_agent = self.coordinator.agents.get('code_generation')
                if not code_agent:
                    raise HTTPException(status_code=503, detail="Code generation agent not available")
                
                # Prepare parameters for the agent
                parameters = {
                    "task_type": "generate_code",
                    "requirements": request.requirements,
                    "language": request.language,
                    "framework": request.framework,
                    "context": request.context
                }
                
                # Call the agent's execute_task method
                result = await asyncio.wait_for(
                    code_agent.execute_task(parameters),
                    timeout=60.0
                )
                
                # Process the result - the agent returns a dict with code, explanation, etc.
                if isinstance(result, dict) and result.get("code"):
                    return {
                        "success": True,
                        "code": result.get("code", ""),
                        "explanation": result.get("explanation", ""),
                        "language": request.language,
                        "framework": request.framework,
                        "files": result.get("files", []),
                        "dependencies": result.get("dependencies", []),
                        "quality_score": result.get("quality_score", 0),
                        "metadata": {
                            "generated_at": datetime.utcnow().isoformat(),
                            "agent": "code_generation",
                            "model": "deepseek-coder-v2"
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "No code generated",
                        "code": "",
                        "explanation": "Failed to generate code - empty result"
                    }
                    
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="Code generation timed out")
            except Exception as e:
                self.logger.error(f"Direct code generation error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "code": "",
                    "explanation": f"Generation failed: {e}"
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
            
            if hasattr(self.coordinator, 'agents') and self.coordinator.agents:
                for agent_name, agent in self.coordinator.agents.items():
                    try:
                        health_info = await agent.health_check()
                        agents_status[agent_name] = {
                            "initialized": agent.is_initialized,
                            "status": health_info.get("status", "unknown"),
                            "capabilities": health_info.get("capabilities", [])
                        }
                    except Exception as e:
                        agents_status[agent_name] = {
                            "initialized": False,
                            "status": "error",
                            "capabilities": [],
                            "error": str(e)
                        }
            
            return agents_status
        
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
                "environment": os.getenv("ENVIRONMENT", "development"),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "api": {
                    "host": self.settings.api.host,
                    "port": self.settings.api.port
                },
                "github": {
                    "enabled": bool(os.getenv("GITHUB_TOKEN"))
                },
                "ai": {
                    "model": self.settings.deepseek.model,
                    "configured": self.settings.deepseek.is_configured()
                }
            }
        
        # GitHub Integration Endpoints
        @self.app.post("/api/v1/github/upload")
        async def upload_to_github(request: GitHubUploadRequest):
            """Upload generated code to GitHub repository"""
            try:
                # Get the integration agent
                integration_agent = self.coordinator.agents.get('integration')
                if not integration_agent:
                    raise HTTPException(status_code=503, detail="Integration agent not available")
                
                # Execute GitHub upload task
                task = Task(
                    id=f"github_upload_{len(self.coordinator.tasks) + 1}",
                    type=TaskType.INTEGRATION,
                    priority=2,
                    project_id="github_upload",
                    parameters={
                        "task_type": "github_upload",
                        "repository_name": request.repository_name,
                        "owner": request.owner,
                        "files": request.files,
                        "commit_message": request.commit_message,
                        "branch": request.branch,
                        "create_pr": request.create_pr,
                        "pr_title": request.pr_title,
                        "pr_description": request.pr_description
                    }
                )
                
                task_id = await self.coordinator.submit_task(task)
                
                return {
                    "task_id": task_id,
                    "status": "uploading",
                    "message": f"Uploading files to {request.owner}/{request.repository_name}",
                    "repository": f"{request.owner}/{request.repository_name}",
                    "branch": request.branch,
                    "files_count": len(request.files)
                }
                
            except Exception as e:
                self.logger.error(f"GitHub upload failed: {e}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        @self.app.post("/api/v1/github/upload/direct")
        async def upload_to_github_direct(request: GitHubUploadRequest):
            """Upload files to GitHub repository directly (no task queue)"""
            try:
                # Get the integration agent
                integration_agent = self.coordinator.agents.get('integration')
                if not integration_agent:
                    raise HTTPException(status_code=503, detail="Integration agent not available")
                
                # Execute GitHub upload directly
                result = await integration_agent.execute_task({
                    "task_type": "github_upload",
                    "repository_name": request.repository_name,
                    "owner": request.owner,
                    "files": request.files,
                    "commit_message": request.commit_message,
                    "branch": request.branch,
                    "create_pr": request.create_pr,
                    "pr_title": request.pr_title,
                    "pr_description": request.pr_description
                })
                
                # Check if upload failed
                if result.get('status') == 'error':
                    raise HTTPException(
                        status_code=400, 
                        detail=result.get('error', 'GitHub upload failed')
                    )
                
                return {
                    "success": True,
                    "status": "completed",
                    "result": result,
                    "repository": f"{request.owner}/{request.repository_name}",
                    "files_uploaded": result.get('files_uploaded', []),
                    "commit_sha": result.get('commit_sha'),
                    "commit_url": result.get('commit_url')
                }
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"GitHub upload failed: {e}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        @self.app.post("/api/v1/github/create-repository")
        async def create_github_repository(request: GitHubCreateRepoRequest):
            """Create a new GitHub repository"""
            try:
                integration_agent = self.coordinator.agents.get('integration')
                if not integration_agent:
                    raise HTTPException(status_code=503, detail="Integration agent not available")
                
                task = Task(
                    id=f"github_create_repo_{len(self.coordinator.tasks) + 1}",
                    type=TaskType.INTEGRATION,
                    priority=2,
                    project_id="github_create_repo",
                    parameters={
                        "task_type": "github_create_repository",
                        "name": request.name,
                        "description": request.description,
                        "private": request.private,
                        "auto_init": request.auto_init,
                        "gitignore_template": request.gitignore_template,
                        "license_template": request.license_template
                    }
                )
                
                task_id = await self.coordinator.submit_task(task)
                
                return {
                    "task_id": task_id,
                    "status": "creating",
                    "message": f"Creating repository {request.name}",
                    "repository_name": request.name,
                    "private": request.private
                }
                
            except Exception as e:
                self.logger.error(f"GitHub repository creation failed: {e}")
                raise HTTPException(status_code=500, detail=f"Repository creation failed: {str(e)}")
        
        @self.app.post("/api/v1/github/repository/{owner}/{repo_name}/analyze")
        async def analyze_github_repository(owner: str, repo_name: str):
            """Analyze GitHub repository for optimization opportunities"""
            try:
                integration_agent = self.coordinator.agents.get('integration')
                if not integration_agent:
                    raise HTTPException(status_code=503, detail="Integration agent not available")
                
                task = Task(
                    id=f"github_analyze_{len(self.coordinator.tasks) + 1}",
                    type=TaskType.INTEGRATION,
                    priority=3,
                    project_id="github_analysis",
                    parameters={
                        "task_type": "github_repository_analysis",
                        "repository_name": repo_name,
                        "owner": owner,
                        "analysis_type": "comprehensive"
                    }
                )
                
                task_id = await self.coordinator.submit_task(task)
                
                return {
                    "task_id": task_id,
                    "status": "analyzing",
                    "message": f"Analyzing repository {owner}/{repo_name}",
                    "repository": f"{owner}/{repo_name}"
                }
                
            except Exception as e:
                self.logger.error(f"GitHub repository analysis failed: {e}")
                raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        @self.app.post("/api/v1/github/generate-and-upload")
        async def generate_and_upload(request: Dict[str, Any]):
            """Generate code and upload directly to GitHub"""
            try:
                # Extract parameters
                requirements = request.get("requirements", "")
                language = request.get("language", "python")
                framework = request.get("framework")
                repository_name = request.get("repository_name", "")
                owner = request.get("owner", "")
                commit_message = request.get("commit_message", "Add generated code")
                branch = request.get("branch", "main")
                create_pr = request.get("create_pr", False)
                
                if not all([requirements, repository_name, owner]):
                    raise HTTPException(
                        status_code=400, 
                        detail="Missing required fields: requirements, repository_name, owner"
                    )
                
                # Step 1: Generate code
                code_task = Task(
                    id=f"gen_for_github_{len(self.coordinator.tasks) + 1}",
                    type=TaskType.CODE_GENERATION,
                    priority=1,
                    project_id="github_generation",
                    parameters={
                        "task_type": "generate_code",
                        "requirements": requirements,
                        "language": language,
                        "framework": framework,
                        "context": {"target": "github_upload"}
                    }
                )
                
                code_task_id = await self.coordinator.submit_task(code_task)
                
                return {
                    "task_id": code_task_id,
                    "status": "generating",
                    "message": "Generating code for GitHub upload",
                    "next_step": "upload_to_github",
                    "target_repository": f"{owner}/{repository_name}",
                    "branch": branch,
                    "create_pr": create_pr
                }
                
            except Exception as e:
                self.logger.error(f"Generate and upload failed: {e}")
                raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
        
        @self.app.get("/api/v1/github/repositories")
        async def list_user_repositories():
            """List user's GitHub repositories"""
            try:
                integration_agent = self.coordinator.agents.get('integration')
                if not integration_agent:
                    raise HTTPException(status_code=503, detail="Integration agent not available")
                
                # This would need to be implemented in the integration agent
                # For now, return a simulated response
                return {
                    "repositories": [
                        {
                            "name": "SEAgent",
                            "full_name": "navicharan/SEAgent",
                            "private": False,
                            "description": "Autonomous Software Engineering Agent",
                            "default_branch": "master",
                            "languages": ["Python"],
                            "created_at": "2025-10-08T00:00:00Z",
                            "updated_at": "2025-10-08T20:00:00Z"
                        }
                    ],
                    "total_count": 1
                }
                
            except Exception as e:
                self.logger.error(f"Repository listing failed: {e}")
                raise HTTPException(status_code=500, detail=f"Repository listing failed: {str(e)}")
    
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

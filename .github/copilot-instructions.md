# SEAgent - Multi-Agent Software Engineering System

A FastAPI-based autonomous software engineering system with specialized AI agents for code generation, security analysis, debugging, and GitHub integration.

## Core Architecture

**Entry Point:** `main.py` → `AgentCoordinator` → Individual agents (6 total)
- **Agent Coordinator** (`orchestrator/agent_coordinator.py`) - Central task orchestration with async queue-based processing
- **Base Agent Pattern** (`agents/base_agent.py`) - All agents inherit from `BaseAgent` with standardized `execute_task()` interface
- **Configuration System** (`config/settings_simple.py`) - Environment-driven config with `.env` file support

## Agent Implementations

All agents follow the pattern: inherit `BaseAgent`, implement `execute_task(parameters: Dict) -> Dict`

- **CodeGenerationAgent** - Uses DeepSeek/OpenAI for code generation with built-in evaluation engine (HumanEval/SecurityEval)
- **SecurityAnalysisAgent** - Static analysis and vulnerability scanning
- **DebugAgent** - Error analysis and fix suggestions  
- **PerformanceAgent** - Code optimization and profiling
- **IntegrationAgent** - GitHub integration (upload, PR creation, repo management)
- **TestingAgent** - Automated test generation
- **CICDAgent** - CI/CD pipeline creation, optimization, and deployment automation

## Critical Workflows

**Startup Sequence:**
1. `main.py` → `SEAgent.start()` → `AgentCoordinator.initialize()` → Individual agent initialization
2. FastAPI server starts with dashboard at `/dashboard` and GitHub integration at `/github`

**Task Execution:**
- Tasks submitted via `coordinator.submit_task(Task)` → async queue → agent assignment → execution
- Use `TaskType` enum for task routing to appropriate agents

**Configuration Priority:**
1. Environment variables (`.env` file loaded by `settings_simple.py`)
2. `config/config.yaml` 
3. Default values in dataclass fields

## GitHub Integration Pattern

**Direct Execution** (recommended for APIs):
```python
integration_agent = coordinator.agents.get('integration')
result = await integration_agent.execute_task({
    "task_type": "github_upload",
    "repository_name": "repo",
    "owner": "user", 
    "files": {"main.py": "code content"},
    "commit_message": "Add code"
})
```

## Development Commands

**Start System:** `python main.py` (automatically serves dashboard + API)
**Config Setup:** Copy `.env.example` to `.env`, set `OPENAI_API_KEY` 
**Dependencies:** `pip install -r requirements.txt` (includes FastAPI, PyGithub, OpenAI client)

## Agent Conventions

- **Task Parameters:** Always include `task_type` field for internal routing
- **Error Handling:** Return `{"status": "error", "error": "message"}` for failures
- **Async Methods:** All agent methods are async, use `await` for execution
- **Health Checks:** Each agent implements `health_check()` returning status dict

## API Patterns

- **REST API:** FastAPI with automatic docs at `/docs`
- **Direct Generation:** `/api/v1/generate/direct` for immediate code generation
- **GitHub Upload:** `/api/v1/github/upload/direct` for immediate GitHub operations
- **CI/CD Operations:** `/api/v1/cicd/*` endpoints for pipeline management and deployment
- **Task Tracking:** Submit task → get `task_id` → poll `/api/v1/tasks/{task_id}` for status

## Special Features

- **Evaluation Engine:** Built into CodeGenerationAgent, supports HumanEval/SecurityEval datasets
- **Multi-language Support:** Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#
- **Dashboard:** Self-contained HTML with real-time agent status monitoring
- **CI/CD Automation:** Complete pipeline lifecycle from creation to deployment with GitHub Actions
- **Simulation Mode:** Agents run without external APIs when credentials unavailable

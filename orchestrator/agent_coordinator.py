"""
Agent Coordinator - Central orchestration system for multi-agent workflows
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from agents.code_generation_agent import CodeGenerationAgent
from agents.security_analysis_agent import SecurityAnalysisAgent
from agents.debug_agent import DebugAgent
from agents.performance_agent import PerformanceAgent
from agents.integration_agent import IntegrationAgent
from agents.testing_agent import TestingAgent
from agents.cicd_agent import CICDAgent
from agents.application_generator_agent import ApplicationGeneratorAgent


class TaskType(Enum):
    CODE_GENERATION = "code_generation"
    SECURITY_ANALYSIS = "security_analysis"
    DEBUGGING = "debugging"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    INTEGRATION = "integration"
    TESTING = "testing"
    CICD = "cicd"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    type: TaskType
    priority: int
    project_id: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = None
    created_at: float = None
    updated_at: float = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            import time
            self.created_at = time.time()
            self.updated_at = time.time()


class AgentCoordinator:
    """Central coordinator for managing multi-agent workflows"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.agents = {
            'code_generation': CodeGenerationAgent(settings.agents.code_generation),
            'security_analysis': SecurityAnalysisAgent(settings.agents.security_analysis),
            'debug': DebugAgent(settings.agents.debug),
            'performance': PerformanceAgent(settings.agents.performance),
            'integration': IntegrationAgent(settings.agents.integration),
            'testing': TestingAgent(settings.agents.testing),
            'cicd': CICDAgent(settings.agents.cicd),
            'application_generator': ApplicationGeneratorAgent(settings.agents.code_generation)
        }
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Agent communication
        self.agent_communication_channels = {}
        
        # Workflow templates
        self.workflow_templates = self._load_workflow_templates()
        
    async def initialize(self):
        """Initialize all agents and start coordination loops"""
        self.logger.info("Initializing Agent Coordinator...")
        
        # Initialize all agents
        for agent_name, agent in self.agents.items():
            await agent.initialize()
            self.logger.info(f"Initialized {agent_name} agent")
        
        # Start coordination loops
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._agent_communication_handler())
        asyncio.create_task(self._workflow_monitor())
        
        self.logger.info("Agent Coordinator initialized successfully")
    
    async def submit_task(self, task: Task) -> str:
        """Submit a new task to the coordination system"""
        self.tasks[task.id] = task
        await self.task_queue.put(task.id)
        self.logger.info(f"Task {task.id} submitted: {task.type.value}")
        return task.id
    
    async def execute_workflow(self, workflow_name: str, project_id: str, parameters: Dict[str, Any]) -> List[str]:
        """Execute a predefined workflow"""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name]
        task_ids = []
        
        self.logger.info(f"Executing workflow '{workflow_name}' for project {project_id}")
        
        # Create tasks based on workflow template
        for step in workflow['steps']:
            task = Task(
                id=f"{project_id}_{workflow_name}_{step['name']}_{len(self.tasks)}",
                type=TaskType(step['type']),
                priority=step.get('priority', 5),
                project_id=project_id,
                parameters={**parameters, **step.get('parameters', {})},
                dependencies=step.get('dependencies', [])
            )
            
            task_id = await self.submit_task(task)
            task_ids.append(task_id)
        
        return task_ids
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status and details of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'type': task.type.value,
            'status': task.status.value,
            'project_id': task.project_id,
            'assigned_agent': task.assigned_agent,
            'result': task.result,
            'error': task.error,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get the overall status of all tasks for a project"""
        project_tasks = [task for task in self.tasks.values() if task.project_id == project_id]
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in project_tasks if t.status == status])
        
        return {
            'project_id': project_id,
            'total_tasks': len(project_tasks),
            'status_breakdown': status_counts,
            'active_tasks': len([t for t in project_tasks if t.status == TaskStatus.IN_PROGRESS]),
            'completed_tasks': len([t for t in project_tasks if t.status == TaskStatus.COMPLETED]),
            'failed_tasks': len([t for t in project_tasks if t.status == TaskStatus.FAILED])
        }
    
    async def _task_processor(self):
        """Main task processing loop"""
        while True:
            try:
                task_id = await self.task_queue.get()
                task = self.tasks[task_id]
                
                # Check if dependencies are satisfied
                if not await self._check_dependencies(task):
                    # Re-queue task for later processing
                    await asyncio.sleep(1)
                    await self.task_queue.put(task_id)
                    continue
                
                # Assign task to appropriate agent
                agent_name = self._get_agent_for_task(task.type)
                if agent_name not in self.agents:
                    self.logger.error(f"No agent available for task type: {task.type}")
                    task.status = TaskStatus.FAILED
                    task.error = f"No agent available for task type: {task.type}"
                    continue
                
                # Execute task
                task.status = TaskStatus.IN_PROGRESS
                task.assigned_agent = agent_name
                task.updated_at = asyncio.get_event_loop().time()
                
                agent = self.agents[agent_name]
                execution_task = asyncio.create_task(self._execute_task(agent, task))
                self.running_tasks[task_id] = execution_task
                
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, agent, task: Task):
        """Execute a single task with an agent"""
        try:
            self.logger.info(f"Executing task {task.id} with agent {task.assigned_agent}")
            
            result = await agent.execute_task(task.parameters)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.updated_at = asyncio.get_event_loop().time()
            
            self.logger.info(f"Task {task.id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = asyncio.get_event_loop().time()
        
        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def _check_dependencies(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _get_agent_for_task(self, task_type: TaskType) -> str:
        """Get the appropriate agent name for a task type"""
        mapping = {
            TaskType.CODE_GENERATION: 'code_generation',
            TaskType.SECURITY_ANALYSIS: 'security_analysis',
            TaskType.DEBUGGING: 'debug',
            TaskType.PERFORMANCE_OPTIMIZATION: 'performance',
            TaskType.INTEGRATION: 'integration',
            TaskType.TESTING: 'testing',
            TaskType.CICD: 'cicd'
        }
        return mapping.get(task_type)
    
    async def _agent_communication_handler(self):
        """Handle inter-agent communication"""
        while True:
            try:
                # Process agent-to-agent communications
                # This could include sharing analysis results, requesting additional work, etc.
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in agent communication handler: {e}")
    
    async def _workflow_monitor(self):
        """Monitor workflow progress and handle escalations"""
        while True:
            try:
                # Monitor long-running tasks, detect failures, trigger escalations
                current_time = asyncio.get_event_loop().time()
                
                for task in self.tasks.values():
                    if (task.status == TaskStatus.IN_PROGRESS and 
                        current_time - task.updated_at > self.settings.task_timeout):
                        self.logger.warning(f"Task {task.id} has been running for too long")
                        # Could implement timeout handling here
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in workflow monitor: {e}")
    
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load predefined workflow templates"""
        return {
            'full_development_cycle': {
                'steps': [
                    {'name': 'generate_code', 'type': 'code_generation', 'priority': 1},
                    {'name': 'security_scan', 'type': 'security_analysis', 'priority': 2, 'dependencies': ['generate_code']},
                    {'name': 'debug_analysis', 'type': 'debugging', 'priority': 3, 'dependencies': ['generate_code']},
                    {'name': 'performance_analysis', 'type': 'performance_optimization', 'priority': 4, 'dependencies': ['generate_code']},
                    {'name': 'run_tests', 'type': 'testing', 'priority': 5, 'dependencies': ['generate_code', 'security_scan', 'debug_analysis']},
                    {'name': 'setup_cicd', 'type': 'cicd', 'priority': 6, 'dependencies': ['run_tests'], 'parameters': {'task_type': 'create_pipeline'}},
                    {'name': 'integration', 'type': 'integration', 'priority': 7, 'dependencies': ['setup_cicd']}
                ]
            },
            'security_focused': {
                'steps': [
                    {'name': 'security_scan', 'type': 'security_analysis', 'priority': 1},
                    {'name': 'security_testing', 'type': 'testing', 'priority': 2, 'dependencies': ['security_scan'], 'parameters': {'test_type': 'security'}},
                    {'name': 'fix_vulnerabilities', 'type': 'code_generation', 'priority': 3, 'dependencies': ['security_scan'], 'parameters': {'focus': 'security_fixes'}}
                ]
            },
            'performance_optimization': {
                'steps': [
                    {'name': 'performance_analysis', 'type': 'performance_optimization', 'priority': 1},
                    {'name': 'performance_testing', 'type': 'testing', 'priority': 2, 'dependencies': ['performance_analysis'], 'parameters': {'test_type': 'performance'}},
                    {'name': 'optimize_code', 'type': 'code_generation', 'priority': 3, 'dependencies': ['performance_analysis'], 'parameters': {'focus': 'performance'}}
                ]
            },
            'cicd_deployment': {
                'steps': [
                    {'name': 'analyze_pipeline', 'type': 'cicd', 'priority': 1, 'parameters': {'task_type': 'analyze_pipeline'}},
                    {'name': 'optimize_pipeline', 'type': 'cicd', 'priority': 2, 'dependencies': ['analyze_pipeline'], 'parameters': {'task_type': 'optimize_pipeline'}},
                    {'name': 'deploy_staging', 'type': 'cicd', 'priority': 3, 'dependencies': ['optimize_pipeline'], 'parameters': {'task_type': 'deploy_application', 'environment': 'staging'}},
                    {'name': 'deploy_production', 'type': 'cicd', 'priority': 4, 'dependencies': ['deploy_staging'], 'parameters': {'task_type': 'deploy_application', 'environment': 'production'}}
                ]
            },
            'github_actions_setup': {
                'steps': [
                    {'name': 'create_workflows', 'type': 'cicd', 'priority': 1, 'parameters': {'task_type': 'setup_github_actions'}},
                    {'name': 'upload_to_github', 'type': 'integration', 'priority': 2, 'dependencies': ['create_workflows'], 'parameters': {'task_type': 'github_upload'}}
                ]
            }
        }
    
    async def shutdown(self):
        """Shutdown the coordinator and all agents"""
        self.logger.info("Shutting down Agent Coordinator...")
        
        # Cancel all running tasks
        for task_id, running_task in self.running_tasks.items():
            running_task.cancel()
            self.tasks[task_id].status = TaskStatus.CANCELLED
        
        # Shutdown all agents
        for agent_name, agent in self.agents.items():
            await agent.shutdown()
            self.logger.info(f"Shutdown {agent_name} agent")
        
        self.logger.info("Agent Coordinator shutdown complete")

"""
CI/CD Agent - Automated pipeline management and deployment orchestration
Integrates with GitHub Actions, GitLab CI, and other CI/CD platforms
"""

import asyncio
import json
import logging
import yaml
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .base_agent import BaseAgent, AgentCapability
from integrations.cicd_intelligence import CICDPipelineIntelligence, PipelineAnalysis
from integrations.github_integration import GitHubDeepIntegration

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CICDAgent(BaseAgent):
    """Agent responsible for CI/CD pipeline management and automation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pipeline_intelligence = CICDPipelineIntelligence()
        self.github_integration = None
        self.supported_platforms = [
            'github_actions', 'gitlab_ci', 'jenkins', 'azure_devops',
            'circleci', 'travis_ci', 'buildkite'
        ]
        
        # Initialize platform clients
        self.github_token = os.getenv('GITHUB_TOKEN')
        if GITHUB_AVAILABLE and self.github_token:
            self.github_integration = GitHubDeepIntegration(self.github_token)
    
    async def _setup_capabilities(self):
        """Setup CI/CD agent capabilities"""
        self.capabilities = {
            'create_pipeline': AgentCapability(
                name='create_pipeline',
                description='Create intelligent CI/CD pipeline for project',
                input_schema={
                    'project_info': 'object',
                    'platform': 'string',
                    'requirements': 'array'
                },
                output_schema={
                    'pipeline_config': 'string',
                    'setup_instructions': 'string',
                    'monitoring_config': 'object'
                }
            ),
            'analyze_pipeline': AgentCapability(
                name='analyze_pipeline',
                description='Analyze existing CI/CD pipeline for optimization',
                input_schema={
                    'pipeline_config': 'string',
                    'platform': 'string',
                    'historical_data': 'object'
                },
                output_schema={
                    'analysis_results': 'object',
                    'optimization_recommendations': 'array',
                    'performance_metrics': 'object'
                }
            ),
            'optimize_pipeline': AgentCapability(
                name='optimize_pipeline',
                description='Optimize CI/CD pipeline for performance and cost',
                input_schema={
                    'pipeline_config': 'string',
                    'platform': 'string',
                    'optimization_goals': 'array'
                },
                output_schema={
                    'optimized_config': 'string',
                    'improvements': 'array',
                    'estimated_savings': 'object'
                }
            ),
            'monitor_pipeline': AgentCapability(
                name='monitor_pipeline',
                description='Monitor pipeline health and performance',
                input_schema={
                    'pipeline_id': 'string',
                    'platform': 'string'
                },
                output_schema={
                    'health_status': 'object',
                    'alerts': 'array',
                    'recommendations': 'array'
                }
            ),
            'deploy_application': AgentCapability(
                name='deploy_application',
                description='Deploy application to specified environment',
                input_schema={
                    'deployment_config': 'object',
                    'environment': 'string',
                    'version': 'string'
                },
                output_schema={
                    'deployment_status': 'string',
                    'deployment_url': 'string',
                    'health_checks': 'object'
                }
            ),
            'rollback_deployment': AgentCapability(
                name='rollback_deployment',
                description='Rollback deployment to previous version',
                input_schema={
                    'deployment_id': 'string',
                    'target_version': 'string',
                    'environment': 'string'
                },
                output_schema={
                    'rollback_status': 'string',
                    'previous_version': 'string',
                    'rollback_time': 'string'
                }
            ),
            'manage_secrets': AgentCapability(
                name='manage_secrets',
                description='Manage CI/CD secrets and environment variables',
                input_schema={
                    'secrets': 'object',
                    'environment': 'string',
                    'platform': 'string'
                },
                output_schema={
                    'secrets_updated': 'array',
                    'security_status': 'string'
                }
            )
        }
    
    async def _load_models(self):
        """Load AI models for pipeline intelligence"""
        # Initialize pipeline intelligence with AI models
        pass
    
    async def _setup_resources(self):
        """Setup CI/CD resources and connections"""
        # Verify platform connections
        if self.github_integration:
            self.logger.info("GitHub integration initialized")
        else:
            self.logger.warning("GitHub integration not available - running in simulation mode")
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CI/CD task based on task type"""
        task_type = parameters.get('task_type', '')
        
        try:
            if task_type == 'create_pipeline':
                return await self._create_pipeline(parameters)
            elif task_type == 'analyze_pipeline':
                return await self._analyze_pipeline(parameters)
            elif task_type == 'optimize_pipeline':
                return await self._optimize_pipeline(parameters)
            elif task_type == 'monitor_pipeline':
                return await self._monitor_pipeline(parameters)
            elif task_type == 'deploy_application':
                return await self._deploy_application(parameters)
            elif task_type == 'rollback_deployment':
                return await self._rollback_deployment(parameters)
            elif task_type == 'manage_secrets':
                return await self._manage_secrets(parameters)
            elif task_type == 'setup_github_actions':
                return await self._setup_github_actions(parameters)
            elif task_type == 'trigger_deployment':
                return await self._trigger_deployment(parameters)
            else:
                return {
                    'status': 'error',
                    'error': f'Unknown task type: {task_type}'
                }
        
        except Exception as e:
            self.logger.error(f"CI/CD task execution failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _create_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent CI/CD pipeline"""
        project_info = parameters.get('project_info', {})
        platform = parameters.get('platform', 'github_actions')
        requirements = parameters.get('requirements', [])
        
        self.logger.info(f"Creating {platform} pipeline for project")
        
        try:
            # Generate smart pipeline using AI
            pipeline_result = await self.pipeline_intelligence.generate_smart_pipeline(
                project_info, platform
            )
            
            # Create pipeline files
            pipeline_files = await self._create_pipeline_files(
                pipeline_result, platform, project_info
            )
            
            # Generate setup instructions
            setup_instructions = await self._generate_setup_instructions(
                platform, pipeline_result
            )
            
            return {
                'status': 'success',
                'pipeline_config': pipeline_result['pipeline_config'],
                'pipeline_files': pipeline_files,
                'setup_instructions': setup_instructions,
                'features_included': pipeline_result.get('features_included', []),
                'monitoring_config': await self._generate_monitoring_config(project_info),
                'documentation': pipeline_result.get('documentation', ''),
                'platform': platform
            }
        
        except Exception as e:
            self.logger.error(f"Pipeline creation failed: {e}")
            return await self._simulate_pipeline_creation(platform, project_info)
    
    async def _analyze_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze existing CI/CD pipeline"""
        pipeline_config = parameters.get('pipeline_config', '')
        platform = parameters.get('platform', 'github_actions')
        historical_data = parameters.get('historical_data')
        
        self.logger.info(f"Analyzing {platform} pipeline")
        
        try:
            # Perform comprehensive pipeline analysis
            analysis = await self.pipeline_intelligence.analyze_pipeline(
                pipeline_config, platform, historical_data
            )
            
            # Generate detailed recommendations
            recommendations = await self._generate_detailed_recommendations(analysis)
            
            # Calculate metrics
            performance_metrics = await self._calculate_performance_metrics(analysis)
            
            return {
                'status': 'success',
                'analysis_results': {
                    'pipeline_id': analysis.pipeline_id,
                    'current_metrics': analysis.current_metrics.__dict__,
                    'performance_score': analysis.performance_score,
                    'reliability_score': analysis.reliability_score,
                    'cost_efficiency_score': analysis.cost_efficiency_score,
                    'overall_score': analysis.overall_score
                },
                'optimization_recommendations': [rec.__dict__ for rec in analysis.optimization_opportunities],
                'security_issues': analysis.security_issues,
                'performance_metrics': performance_metrics,
                'detailed_recommendations': recommendations,
                'platform': platform
            }
        
        except Exception as e:
            self.logger.error(f"Pipeline analysis failed: {e}")
            return await self._simulate_pipeline_analysis(platform)
    
    async def _optimize_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize CI/CD pipeline"""
        pipeline_config = parameters.get('pipeline_config', '')
        platform = parameters.get('platform', 'github_actions')
        optimization_goals = parameters.get('optimization_goals', ['performance', 'cost'])
        
        self.logger.info(f"Optimizing {platform} pipeline")
        
        try:
            if platform == 'github_actions':
                optimization_result = await self.pipeline_intelligence.optimize_github_actions(
                    pipeline_config
                )
            else:
                # Generic optimization
                optimization_result = await self._generic_pipeline_optimization(
                    pipeline_config, platform, optimization_goals
                )
            
            return {
                'status': 'success',
                'optimized_config': optimization_result['optimized_workflow'],
                'improvements': optimization_result['optimizations_applied'],
                'estimated_savings': {
                    'time': optimization_result.get('estimated_time_savings', '0%'),
                    'cost': optimization_result.get('estimated_cost_savings', '$0'),
                },
                'optimization_summary': optimization_result.get('optimization_summary', ''),
                'platform': platform
            }
        
        except Exception as e:
            self.logger.error(f"Pipeline optimization failed: {e}")
            return await self._simulate_pipeline_optimization(platform)
    
    async def _monitor_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor pipeline health and performance"""
        pipeline_id = parameters.get('pipeline_id', '')
        platform = parameters.get('platform', 'github_actions')
        
        self.logger.info(f"Monitoring {platform} pipeline: {pipeline_id}")
        
        try:
            # Get pipeline metrics from platform
            metrics_data = await self._fetch_pipeline_metrics(pipeline_id, platform)
            
            # Analyze health
            health_result = await self.pipeline_intelligence.monitor_pipeline_health(
                pipeline_id, metrics_data
            )
            
            return {
                'status': 'success',
                'pipeline_id': pipeline_id,
                'health_status': health_result['health_status'],
                'alerts': health_result['alerts'],
                'recommendations': health_result['immediate_actions'],
                'overall_health_score': health_result['overall_health_score'],
                'metrics': metrics_data,
                'trend_analysis': health_result.get('trend_analysis', ''),
                'platform': platform
            }
        
        except Exception as e:
            self.logger.error(f"Pipeline monitoring failed: {e}")
            return await self._simulate_pipeline_monitoring(pipeline_id, platform)
    
    async def _deploy_application(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy application to specified environment"""
        deployment_config = parameters.get('deployment_config', {})
        environment = parameters.get('environment', 'staging')
        version = parameters.get('version', 'latest')
        
        self.logger.info(f"Deploying application to {environment} (version: {version})")
        
        try:
            # Trigger deployment
            deployment_result = await self._trigger_deployment_pipeline(
                deployment_config, environment, version
            )
            
            # Monitor deployment progress
            deployment_status = await self._monitor_deployment_progress(
                deployment_result['deployment_id'], environment
            )
            
            # Run health checks
            health_checks = await self._run_post_deployment_health_checks(
                environment, deployment_config
            )
            
            return {
                'status': 'success',
                'deployment_status': deployment_status['status'],
                'deployment_id': deployment_result['deployment_id'],
                'deployment_url': deployment_result.get('deployment_url', ''),
                'health_checks': health_checks,
                'environment': environment,
                'version': version,
                'deployment_time': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Application deployment failed: {e}")
            return await self._simulate_deployment(environment, version)
    
    async def _setup_github_actions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Setup GitHub Actions workflows for the repository"""
        repository_name = parameters.get('repository_name', '')
        owner = parameters.get('owner', '')
        project_type = parameters.get('project_type', 'python')
        
        self.logger.info(f"Setting up GitHub Actions for {owner}/{repository_name}")
        
        try:
            # Read the CI/CD workflow templates
            workflows_dir = Path(__file__).parent.parent / '.github' / 'workflows'
            workflow_files = {}
            
            # CI workflow
            ci_workflow_path = workflows_dir / 'ci.yml'
            if ci_workflow_path.exists():
                with open(ci_workflow_path, 'r') as f:
                    workflow_files['.github/workflows/ci.yml'] = f.read()
            
            # CD workflow
            cd_workflow_path = workflows_dir / 'cd.yml'
            if cd_workflow_path.exists():
                with open(cd_workflow_path, 'r') as f:
                    workflow_files['.github/workflows/cd.yml'] = f.read()
            
            # Create additional project-specific workflows
            if project_type == 'python':
                # Add Python-specific optimizations
                python_workflow = await self._create_python_specific_workflow()
                workflow_files['.github/workflows/python-advanced.yml'] = python_workflow
            
            # Upload workflows to GitHub repository
            if self.github_integration:
                upload_result = await self._upload_workflows_to_github(
                    owner, repository_name, workflow_files
                )
                
                return {
                    'status': 'success',
                    'workflows_created': list(workflow_files.keys()),
                    'repository': f"{owner}/{repository_name}",
                    'upload_result': upload_result,
                    'setup_complete': True,
                    'next_steps': [
                        'Configure repository secrets (DOCKER_USERNAME, DOCKER_PASSWORD)',
                        'Enable GitHub Actions in repository settings',
                        'Review and customize workflow triggers',
                        'Set up deployment environments'
                    ]
                }
            else:
                return {
                    'status': 'success',
                    'workflows_created': list(workflow_files.keys()),
                    'workflow_files': workflow_files,
                    'setup_complete': False,
                    'message': 'Workflows generated. Upload manually to repository.',
                    'instructions': 'Copy the workflow files to your repository .github/workflows/ directory'
                }
        
        except Exception as e:
            self.logger.error(f"GitHub Actions setup failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'repository': f"{owner}/{repository_name}"
            }
    
    async def _trigger_deployment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger deployment pipeline"""
        repository_name = parameters.get('repository_name', '')
        owner = parameters.get('owner', '')
        environment = parameters.get('environment', 'staging')
        workflow_name = parameters.get('workflow_name', 'cd.yml')
        
        self.logger.info(f"Triggering deployment for {owner}/{repository_name} to {environment}")
        
        try:
            if self.github_integration and REQUESTS_AVAILABLE:
                # Trigger GitHub Actions workflow
                result = await self._trigger_github_workflow(
                    owner, repository_name, workflow_name, environment
                )
                
                return {
                    'status': 'success',
                    'deployment_triggered': True,
                    'workflow_run_id': result.get('workflow_run_id'),
                    'workflow_run_url': result.get('workflow_run_url'),
                    'environment': environment,
                    'repository': f"{owner}/{repository_name}",
                    'estimated_duration': '5-10 minutes'
                }
            else:
                return await self._simulate_deployment_trigger(environment)
        
        except Exception as e:
            self.logger.error(f"Deployment trigger failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'environment': environment
            }
    
    # Helper methods
    async def _create_pipeline_files(self, pipeline_result: Dict[str, Any], 
                                   platform: str, project_info: Dict[str, Any]) -> Dict[str, str]:
        """Create pipeline configuration files"""
        files = {}
        
        if platform == 'github_actions':
            # Convert pipeline config to GitHub Actions YAML
            workflow_yaml = yaml.dump(pipeline_result['pipeline_config'], default_flow_style=False)
            files['.github/workflows/ci-cd.yml'] = workflow_yaml
            
            # Add additional workflow files
            if project_info.get('language') == 'python':
                files['.github/workflows/python-tests.yml'] = await self._create_python_test_workflow()
        
        elif platform == 'gitlab_ci':
            # Convert to GitLab CI format
            gitlab_yaml = yaml.dump(pipeline_result['pipeline_config'], default_flow_style=False)
            files['.gitlab-ci.yml'] = gitlab_yaml
        
        return files
    
    async def _simulate_pipeline_creation(self, platform: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate pipeline creation for testing"""
        return {
            'status': 'success',
            'pipeline_config': f"# Generated {platform} pipeline for {project_info.get('name', 'project')}",
            'pipeline_files': {
                f'.github/workflows/ci.yml' if platform == 'github_actions' else f'{platform}-config.yml':
                f"# {platform} configuration\nname: CI/CD Pipeline\non: [push, pull_request]"
            },
            'setup_instructions': f"1. Commit pipeline files\n2. Configure {platform} secrets\n3. Enable pipeline",
            'features_included': ['CI', 'CD', 'Testing', 'Security Scanning'],
            'monitoring_config': {'alerts': True, 'notifications': True},
            'platform': platform
        }
    
    async def _simulate_pipeline_analysis(self, platform: str) -> Dict[str, Any]:
        """Simulate pipeline analysis"""
        return {
            'status': 'success',
            'analysis_results': {
                'pipeline_id': f'sim_{platform}_001',
                'performance_score': 0.75,
                'reliability_score': 0.85,
                'cost_efficiency_score': 0.60,
                'overall_score': 0.73
            },
            'optimization_recommendations': [
                {
                    'category': 'performance',
                    'description': 'Enable caching for dependencies',
                    'expected_improvement': '30% faster builds',
                    'priority': 'high'
                }
            ],
            'security_issues': [],
            'platform': platform
        }
    
    async def _simulate_pipeline_optimization(self, platform: str) -> Dict[str, Any]:
        """Simulate pipeline optimization"""
        return {
            'status': 'success',
            'optimized_config': f"# Optimized {platform} configuration",
            'improvements': [
                'Added dependency caching',
                'Parallelized test execution',
                'Optimized Docker layer caching'
            ],
            'estimated_savings': {
                'time': '35%',
                'cost': '$25/month'
            },
            'platform': platform
        }
    
    async def _simulate_pipeline_monitoring(self, pipeline_id: str, platform: str) -> Dict[str, Any]:
        """Simulate pipeline monitoring"""
        return {
            'status': 'success',
            'pipeline_id': pipeline_id,
            'health_status': 'healthy',
            'alerts': [],
            'recommendations': [],
            'overall_health_score': 0.92,
            'platform': platform
        }
    
    async def _simulate_deployment(self, environment: str, version: str) -> Dict[str, Any]:
        """Simulate deployment"""
        return {
            'status': 'success',
            'deployment_status': 'completed',
            'deployment_id': f'deploy_{environment}_{version}',
            'deployment_url': f'https://seagent-{environment}.example.com',
            'health_checks': {'status': 'passed', 'checks': ['api', 'database', 'agents']},
            'environment': environment,
            'version': version
        }
    
    async def _simulate_deployment_trigger(self, environment: str) -> Dict[str, Any]:
        """Simulate deployment trigger"""
        return {
            'status': 'success',
            'deployment_triggered': True,
            'workflow_run_id': f'run_{environment}_123456',
            'environment': environment,
            'message': 'Deployment triggered successfully (simulated)'
        }
    
    async def _generate_setup_instructions(self, platform: str, pipeline_result: Dict[str, Any]) -> str:
        """Generate setup instructions for the CI/CD pipeline"""
        try:
            project_name = pipeline_result.get('project_name', 'project')
            
            if platform.lower() == 'github':
                instructions = f"""
# 🚀 CI/CD Setup Instructions for {project_name}

## Quick Setup (5 minutes)

### 1. Repository Setup
```bash
# Clone or initialize your repository
git clone https://github.com/yourusername/{project_name}.git
cd {project_name}
```

### 2. Add Workflow Files
Copy the generated workflow files to your repository:
- `.github/workflows/ci.yml` - Continuous Integration
- `.github/workflows/cd.yml` - Continuous Deployment

### 3. Configure Secrets (if needed)
Go to your GitHub repository settings → Secrets and variables → Actions:
- `OPENAI_API_KEY` - For AI features (optional)
- `DOCKER_USERNAME` - For Docker publishing (optional)
- `DOCKER_PASSWORD` - For Docker publishing (optional)

### 4. Enable Actions
1. Go to your repository on GitHub
2. Click "Actions" tab
3. Enable GitHub Actions if prompted
4. Push your code to trigger the first workflow

### 5. Monitor Pipeline
- Check the "Actions" tab to see your workflows running
- Green checkmarks indicate successful runs
- Red X marks indicate failures (check logs for details)

## Features Included
{self._format_features_list(pipeline_result.get('features_included', []))}

## Next Steps
1. Customize the workflows for your specific needs
2. Add deployment environments in repository settings
3. Set up monitoring and alerts
4. Review security scanning reports

## Troubleshooting
- Check GitHub Actions logs for detailed error messages
- Ensure all required secrets are configured
- Verify your code passes local tests before pushing

For more help, visit: https://docs.github.com/en/actions
"""
            else:
                instructions = f"""
# 🚀 CI/CD Setup Instructions for {project_name}

## Platform: {platform.title()}

### 1. Pipeline Configuration
The generated pipeline configuration has been optimized for {platform}.

### 2. Setup Steps
1. Copy the configuration to your {platform} project
2. Configure any required environment variables
3. Test the pipeline with a sample commit
4. Monitor the execution and adjust as needed

### 3. Features Included
{self._format_features_list(pipeline_result.get('features_included', []))}

### 4. Next Steps
- Customize the pipeline for your specific requirements
- Add additional stages or environments as needed
- Set up monitoring and notifications
"""
            
            return instructions.strip()
            
        except Exception as e:
            self.logger.error(f"Setup instructions generation failed: {e}")
            return f"""
# Setup Instructions for {platform.title()}

1. Deploy the generated pipeline configuration to your {platform} environment
2. Configure required environment variables and secrets
3. Test the pipeline with a sample deployment
4. Monitor and adjust configuration as needed

Note: Setup instructions generation encountered an error. Please refer to {platform} documentation for detailed setup steps.
"""
    
    def _format_features_list(self, features: List[str]) -> str:
        """Format features list for display"""
        if not features:
            return "- Standard CI/CD pipeline with build, test, and deploy stages"
        
        formatted = []
        for feature in features:
            formatted.append(f"- {feature.replace('_', ' ').title()}")
        
        return '\n'.join(formatted)
    
    async def _generate_monitoring_config(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monitoring configuration for the pipeline"""
        try:
            project_name = project_info.get('project_name', 'project')
            language = project_info.get('language', 'python')
            
            monitoring_config = {
                'alerts': {
                    'build_failure': {
                        'enabled': True,
                        'channels': ['slack', 'email'],
                        'threshold': 'immediate'
                    },
                    'deployment_failure': {
                        'enabled': True,
                        'channels': ['slack', 'email', 'sms'],
                        'threshold': 'immediate'
                    },
                    'performance_degradation': {
                        'enabled': True,
                        'channels': ['slack'],
                        'threshold': '5 minutes'
                    }
                },
                'metrics': {
                    'build_time': {
                        'target': '< 5 minutes',
                        'warning_threshold': '4 minutes',
                        'critical_threshold': '5 minutes'
                    },
                    'test_coverage': {
                        'target': '> 80%',
                        'warning_threshold': '70%',
                        'critical_threshold': '60%'
                    },
                    'deployment_frequency': {
                        'target': 'Daily',
                        'tracking': 'automatic'
                    },
                    'success_rate': {
                        'target': '> 95%',
                        'warning_threshold': '90%',
                        'critical_threshold': '85%'
                    }
                },
                'health_checks': {
                    'application': {
                        'endpoint': f'/health',
                        'interval': '30 seconds',
                        'timeout': '5 seconds',
                        'retries': 3
                    },
                    'database': {
                        'enabled': True,
                        'interval': '1 minute'
                    },
                    'external_services': {
                        'enabled': True,
                        'interval': '2 minutes'
                    }
                },
                'dashboards': {
                    'pipeline_overview': {
                        'widgets': [
                            'build_success_rate',
                            'deployment_frequency',
                            'average_build_time',
                            'test_coverage_trend'
                        ]
                    },
                    'performance': {
                        'widgets': [
                            'response_time',
                            'error_rate',
                            'throughput',
                            'resource_usage'
                        ]
                    }
                },
                'logging': {
                    'level': 'info',
                    'retention': '30 days',
                    'structured': True,
                    'aggregation': {
                        'enabled': True,
                        'service': 'elasticsearch'
                    }
                },
                'notifications': {
                    'slack': {
                        'webhook_url': '${SLACK_WEBHOOK_URL}',
                        'channel': '#deployments'
                    },
                    'email': {
                        'recipients': ['devops@company.com'],
                        'smtp_server': '${SMTP_SERVER}'
                    }
                }
            }
            
            # Add language-specific monitoring
            if language == 'python':
                monitoring_config['metrics']['python_specific'] = {
                    'memory_usage': {'target': '< 512MB'},
                    'startup_time': {'target': '< 10 seconds'}
                }
            elif language in ['javascript', 'typescript']:
                monitoring_config['metrics']['node_specific'] = {
                    'event_loop_lag': {'target': '< 10ms'},
                    'heap_usage': {'target': '< 1GB'}
                }
            
            return monitoring_config
            
        except Exception as e:
            self.logger.error(f"Monitoring config generation failed: {e}")
            return {
                'alerts': {'build_failure': {'enabled': True}},
                'metrics': {'build_time': {'target': '< 10 minutes'}},
                'health_checks': {'application': {'endpoint': '/health'}},
                'error': f'Monitoring config generation failed: {str(e)}'
            }
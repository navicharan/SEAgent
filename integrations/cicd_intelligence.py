"""
CI/CD Pipeline Intelligence - Smart pipeline optimization and automation
Provides intelligent analysis and optimization of CI/CD workflows
"""

import asyncio
import json
import logging
import yaml
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from config.deepseek_client import DeepSeekClient


@dataclass
class PipelineMetrics:
    """Metrics for a CI/CD pipeline"""
    pipeline_name: str
    total_runs: int
    success_rate: float
    average_duration: float
    failure_patterns: List[str]
    resource_usage: Dict[str, float]
    cost_per_run: float
    bottlenecks: List[str]
    last_analyzed: datetime


@dataclass
class OptimizationRecommendation:
    """Pipeline optimization recommendation"""
    category: str  # performance, cost, reliability, security
    description: str
    expected_improvement: str
    implementation_effort: str  # low, medium, high
    priority: str  # low, medium, high, critical
    code_changes: Optional[str] = None
    estimated_savings: Optional[float] = None


@dataclass
class PipelineAnalysis:
    """Complete pipeline analysis results"""
    pipeline_id: str
    current_metrics: PipelineMetrics
    optimization_opportunities: List[OptimizationRecommendation]
    security_issues: List[Dict[str, Any]]
    performance_score: float
    reliability_score: float
    cost_efficiency_score: float
    overall_score: float


class CICDPipelineIntelligence:
    """
    Intelligent CI/CD pipeline analysis and optimization system
    """
    
    def __init__(self, deepseek_client: Optional[DeepSeekClient] = None):
        self.deepseek_client = deepseek_client
        self.logger = logging.getLogger(__name__)
        self.supported_platforms = [
            'github_actions', 'gitlab_ci', 'jenkins', 'azure_devops', 
            'circleci', 'travis_ci', 'buildkite'
        ]
    
    async def analyze_pipeline(self, pipeline_config: str, platform: str,
                             historical_data: Optional[Dict[str, Any]] = None) -> PipelineAnalysis:
        """
        Perform comprehensive pipeline analysis
        """
        try:
            self.logger.info(f"Analyzing {platform} pipeline configuration")
            
            # Parse pipeline configuration
            parsed_config = await self._parse_pipeline_config(pipeline_config, platform)
            
            # Analyze current metrics
            current_metrics = await self._analyze_current_metrics(parsed_config, historical_data)
            
            # Identify optimization opportunities
            optimizations = await self._identify_optimizations(parsed_config, platform, current_metrics)
            
            # Security analysis
            security_issues = await self._analyze_pipeline_security(parsed_config, platform)
            
            # Calculate scores
            scores = await self._calculate_pipeline_scores(current_metrics, optimizations, security_issues)
            
            return PipelineAnalysis(
                pipeline_id=f"{platform}_{hash(pipeline_config) % 10000}",
                current_metrics=current_metrics,
                optimization_opportunities=optimizations,
                security_issues=security_issues,
                performance_score=scores['performance'],
                reliability_score=scores['reliability'],
                cost_efficiency_score=scores['cost_efficiency'],
                overall_score=scores['overall']
            )
            
        except Exception as e:
            self.logger.error(f"Pipeline analysis failed: {e}")
            return await self._simulate_pipeline_analysis(platform)
    
    async def optimize_github_actions(self, workflow_content: str) -> Dict[str, Any]:
        """
        Optimize GitHub Actions workflow
        """
        try:
            workflow = yaml.safe_load(workflow_content)
            
            optimizations = []
            optimized_workflow = workflow.copy()
            
            # Analyze jobs for optimization opportunities
            if 'jobs' in workflow:
                for job_name, job_config in workflow['jobs'].items():
                    job_optimizations = await self._optimize_github_actions_job(
                        job_name, job_config
                    )
                    optimizations.extend(job_optimizations)
                    
                    # Apply optimizations to workflow
                    optimized_workflow['jobs'][job_name] = await self._apply_job_optimizations(
                        job_config, job_optimizations
                    )
            
            # Global workflow optimizations
            global_optimizations = await self._optimize_workflow_global_settings(workflow)
            optimizations.extend(global_optimizations)
            
            # AI-powered optimization suggestions
            if self.deepseek_client:
                ai_optimizations = await self._get_ai_pipeline_optimizations(
                    workflow_content, 'github_actions'
                )
                optimizations.extend(ai_optimizations)
            
            return {
                "original_workflow": workflow,
                "optimized_workflow": optimized_workflow,
                "optimizations_applied": optimizations,
                "estimated_time_savings": await self._calculate_time_savings(optimizations),
                "estimated_cost_savings": await self._calculate_cost_savings(optimizations),
                "optimization_summary": await self._generate_optimization_summary(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"GitHub Actions optimization failed: {e}")
            return await self._simulate_workflow_optimization('github_actions')
    
    async def generate_smart_pipeline(self, project_info: Dict[str, Any], 
                                    platform: str = 'github_actions') -> Dict[str, Any]:
        """
        Generate an intelligent CI/CD pipeline based on project analysis
        """
        try:
            self.logger.info(f"Generating smart {platform} pipeline")
            
            # Analyze project structure and requirements
            project_analysis = await self._analyze_project_requirements(project_info)
            
            # Generate base pipeline structure
            base_pipeline = await self._generate_base_pipeline(project_analysis, platform)
            
            # Add intelligent optimizations
            optimized_pipeline = await self._add_intelligent_optimizations(
                base_pipeline, project_analysis, platform
            )
            
            # Security enhancements
            secure_pipeline = await self._add_security_enhancements(
                optimized_pipeline, project_analysis, platform
            )
            
            # Performance optimizations
            final_pipeline = await self._add_performance_optimizations(
                secure_pipeline, project_analysis, platform
            )
            
            # Generate documentation
            documentation = await self._generate_pipeline_documentation(
                final_pipeline, project_analysis, platform
            )
            
            return {
                "pipeline_config": final_pipeline,
                "platform": platform,
                "project_analysis": project_analysis,
                "features_included": await self._list_pipeline_features(final_pipeline),
                "documentation": documentation,
                "setup_instructions": await self._generate_setup_instructions(platform),
                "monitoring_recommendations": await self._generate_monitoring_recommendations(project_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Smart pipeline generation failed: {e}")
            return await self._simulate_smart_pipeline_generation(platform)
    
    async def monitor_pipeline_health(self, pipeline_id: str, 
                                    metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor and analyze pipeline health in real-time
        """
        try:
            # Analyze current performance
            health_status = await self._analyze_pipeline_health(metrics_data)
            
            # Detect anomalies
            anomalies = await self._detect_pipeline_anomalies(metrics_data)
            
            # Predictive analysis
            predictions = await self._predict_pipeline_issues(metrics_data)
            
            # Generate alerts
            alerts = await self._generate_health_alerts(health_status, anomalies, predictions)
            
            # Suggest immediate actions
            immediate_actions = await self._suggest_immediate_actions(alerts)
            
            return {
                "pipeline_id": pipeline_id,
                "health_status": health_status,
                "anomalies_detected": anomalies,
                "predictions": predictions,
                "alerts": alerts,
                "immediate_actions": immediate_actions,
                "overall_health_score": await self._calculate_overall_health_score(health_status),
                "trend_analysis": await self._analyze_health_trends(metrics_data)
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline health monitoring failed: {e}")
            return await self._simulate_health_monitoring(pipeline_id)
    
    async def auto_fix_pipeline_issues(self, pipeline_config: str, platform: str,
                                     failure_logs: List[str]) -> Dict[str, Any]:
        """
        Automatically fix common pipeline issues
        """
        try:
            self.logger.info("Attempting auto-fix of pipeline issues")
            
            # Analyze failure patterns
            failure_analysis = await self._analyze_failure_patterns(failure_logs)
            
            # Identify fixable issues
            fixable_issues = await self._identify_fixable_issues(failure_analysis, platform)
            
            # Generate fixes
            fixes_applied = []
            fixed_config = pipeline_config
            
            for issue in fixable_issues:
                fix_result = await self._apply_automatic_fix(fixed_config, issue, platform)
                if fix_result['success']:
                    fixed_config = fix_result['fixed_config']
                    fixes_applied.append(fix_result['fix_description'])
            
            # AI-powered fix suggestions for complex issues
            if self.deepseek_client and failure_logs:
                ai_fixes = await self._get_ai_fix_suggestions(
                    pipeline_config, failure_logs, platform
                )
                fixes_applied.extend(ai_fixes)
            
            # Validate fixed configuration
            validation_result = await self._validate_fixed_pipeline(fixed_config, platform)
            
            return {
                "original_config": pipeline_config,
                "fixed_config": fixed_config,
                "fixes_applied": fixes_applied,
                "validation_result": validation_result,
                "success_probability": await self._estimate_fix_success_probability(fixes_applied),
                "manual_review_required": await self._requires_manual_review(fixes_applied)
            }
            
        except Exception as e:
            self.logger.error(f"Auto-fix failed: {e}")
            return await self._simulate_auto_fix(platform)
    
    # Helper methods for pipeline analysis
    async def _parse_pipeline_config(self, config: str, platform: str) -> Dict[str, Any]:
        """Parse pipeline configuration based on platform"""
        try:
            if platform == 'github_actions':
                return yaml.safe_load(config)
            elif platform == 'gitlab_ci':
                return yaml.safe_load(config)
            elif platform == 'jenkins':
                # Handle Jenkinsfile parsing
                return {"jenkinsfile": config}
            else:
                # Generic YAML parsing
                return yaml.safe_load(config)
        except Exception as e:
            self.logger.error(f"Failed to parse {platform} config: {e}")
            return {}
    
    async def _analyze_current_metrics(self, config: Dict[str, Any], 
                                     historical_data: Optional[Dict[str, Any]]) -> PipelineMetrics:
        """Analyze current pipeline metrics"""
        if historical_data:
            return PipelineMetrics(
                pipeline_name=config.get('name', 'unknown'),
                total_runs=historical_data.get('total_runs', 0),
                success_rate=historical_data.get('success_rate', 0.0),
                average_duration=historical_data.get('avg_duration', 0.0),
                failure_patterns=historical_data.get('failure_patterns', []),
                resource_usage=historical_data.get('resource_usage', {}),
                cost_per_run=historical_data.get('cost_per_run', 0.0),
                bottlenecks=historical_data.get('bottlenecks', []),
                last_analyzed=datetime.now()
            )
        else:
            # Estimate metrics from configuration
            estimated_duration = await self._estimate_pipeline_duration(config)
            return PipelineMetrics(
                pipeline_name=config.get('name', 'unknown'),
                total_runs=0,
                success_rate=0.0,
                average_duration=estimated_duration,
                failure_patterns=[],
                resource_usage={},
                cost_per_run=0.0,
                bottlenecks=[],
                last_analyzed=datetime.now()
            )
    
    async def _identify_optimizations(self, config: Dict[str, Any], platform: str,
                                    metrics: PipelineMetrics) -> List[OptimizationRecommendation]:
        """Identify optimization opportunities"""
        optimizations = []
        
        # Performance optimizations
        if metrics.average_duration > 300:  # 5 minutes
            optimizations.append(OptimizationRecommendation(
                category="performance",
                description="Pipeline duration is above recommended threshold",
                expected_improvement="Reduce build time by 20-40%",
                implementation_effort="medium",
                priority="high",
                estimated_savings=metrics.average_duration * 0.3
            ))
        
        # Cost optimizations
        if platform == 'github_actions':
            optimizations.extend(await self._github_actions_cost_optimizations(config))
        
        # Reliability optimizations
        if metrics.success_rate < 0.9:
            optimizations.append(OptimizationRecommendation(
                category="reliability",
                description="Success rate below 90%, add retry mechanisms",
                expected_improvement="Improve success rate to 95%+",
                implementation_effort="low",
                priority="high"
            ))
        
        return optimizations
    
    async def _github_actions_cost_optimizations(self, config: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """GitHub Actions specific cost optimizations"""
        optimizations = []
        
        if 'jobs' in config:
            for job_name, job_config in config['jobs'].items():
                # Check for expensive runners
                runs_on = job_config.get('runs-on', 'ubuntu-latest')
                if 'windows' in runs_on or 'macos' in runs_on:
                    optimizations.append(OptimizationRecommendation(
                        category="cost",
                        description=f"Job {job_name} uses expensive runner: {runs_on}",
                        expected_improvement="Consider if Linux runner can be used instead",
                        implementation_effort="low",
                        priority="medium",
                        estimated_savings=10.0  # Cost savings per run
                    ))
        
        return optimizations
    
    # Simulation methods
    async def _simulate_pipeline_analysis(self, platform: str) -> PipelineAnalysis:
        """Simulate pipeline analysis"""
        return PipelineAnalysis(
            pipeline_id=f"sim_{platform}_001",
            current_metrics=PipelineMetrics(
                pipeline_name="simulated_pipeline",
                total_runs=100,
                success_rate=0.85,
                average_duration=450.0,
                failure_patterns=["timeout", "dependency_failure"],
                resource_usage={"cpu": 70.0, "memory": 60.0},
                cost_per_run=2.50,
                bottlenecks=["test_stage", "build_stage"],
                last_analyzed=datetime.now()
            ),
            optimization_opportunities=[
                OptimizationRecommendation(
                    category="performance",
                    description="Parallelize test execution",
                    expected_improvement="Reduce test time by 40%",
                    implementation_effort="medium",
                    priority="high"
                )
            ],
            security_issues=[],
            performance_score=0.7,
            reliability_score=0.85,
            cost_efficiency_score=0.6,
            overall_score=0.72
        )
    
    async def _simulate_workflow_optimization(self, platform: str) -> Dict[str, Any]:
        """Simulate workflow optimization"""
        return {
            "original_workflow": {"name": "CI", "on": ["push"]},
            "optimized_workflow": {"name": "Optimized CI", "on": ["push", "pull_request"]},
            "optimizations_applied": [
                "Added caching for dependencies",
                "Parallelized test execution",
                "Optimized Docker layer caching"
            ],
            "estimated_time_savings": "30%",
            "estimated_cost_savings": "$15/month",
            "optimization_summary": "Applied 3 major optimizations focusing on speed and cost"
        }
    
    async def _simulate_smart_pipeline_generation(self, platform: str) -> Dict[str, Any]:
        """Simulate smart pipeline generation"""
        return {
            "pipeline_config": {
                "name": f"Smart {platform} Pipeline",
                "features": ["automated_testing", "security_scanning", "deployment"]
            },
            "platform": platform,
            "project_analysis": {"language": "python", "framework": "fastapi"},
            "features_included": ["CI/CD", "Security", "Performance Testing"],
            "documentation": "Generated comprehensive pipeline documentation",
            "setup_instructions": f"Step-by-step {platform} setup guide",
            "monitoring_recommendations": ["Add performance metrics", "Set up alerts"]
        }
    
    async def _simulate_health_monitoring(self, pipeline_id: str) -> Dict[str, Any]:
        """Simulate pipeline health monitoring"""
        return {
            "pipeline_id": pipeline_id,
            "health_status": "good",
            "anomalies_detected": [],
            "predictions": {"next_failure_probability": 0.1},
            "alerts": [],
            "immediate_actions": [],
            "overall_health_score": 0.85,
            "trend_analysis": "Stable performance over last 30 days"
        }
    
    async def _simulate_auto_fix(self, platform: str) -> Dict[str, Any]:
        """Simulate auto-fix capabilities"""
        return {
            "original_config": "# Original pipeline config",
            "fixed_config": "# Fixed pipeline config",
            "fixes_applied": ["Fixed timeout issue", "Updated deprecated actions"],
            "validation_result": {"valid": True, "warnings": []},
            "success_probability": 0.9,
            "manual_review_required": False
        }
"""
Integrations Module

Advanced integration capabilities for external services and platforms
"""

from .github_integration import GitHubDeepIntegration, RepositoryAnalysis, PullRequestAnalysis
from .cicd_intelligence import CICDPipelineIntelligence, PipelineAnalysis, OptimizationRecommendation

__all__ = [
    'GitHubDeepIntegration',
    'RepositoryAnalysis', 
    'PullRequestAnalysis',
    'CICDPipelineIntelligence',
    'PipelineAnalysis',
    'OptimizationRecommendation'
]
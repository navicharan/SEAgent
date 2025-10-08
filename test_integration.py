"""
Integration Tests for GitHub Deep Integration and CI/CD Pipeline Intelligence
Testing the enhanced SEAgent features with comprehensive test coverage
"""

import asyncio
import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.integration_agent import IntegrationAgent
from integrations.github_integration import GitHubDeepIntegration, RepositoryAnalysis
from integrations.cicd_intelligence import CICDPipelineIntelligence, PipelineAnalysis
from config.deepseek_client import DeepSeekClient


class TestGitHubDeepIntegration(unittest.TestCase):
    """Test GitHub Deep Integration functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.mock_github_token = "test_token_123"
        self.mock_deepseek_client = Mock(spec=DeepSeekClient)
        self.github_integration = GitHubDeepIntegration(
            self.mock_github_token, 
            self.mock_deepseek_client
        )
    
    def test_initialization(self):
        """Test GitHub integration initialization"""
        self.assertIsNotNone(self.github_integration)
        self.assertEqual(self.github_integration.github_token, self.mock_github_token)
        self.assertEqual(self.github_integration.ai_client, self.mock_deepseek_client)
    
    @patch('github.Github')
    async def test_analyze_repository(self, mock_github):
        """Test repository analysis"""
        # Mock GitHub API responses
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.language = "Python"
        mock_repo.size = 1024
        mock_repo.get_languages.return_value = {"Python": 70.0, "JavaScript": 30.0}
        mock_repo.get_contents.return_value = []
        
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        # Mock AI client response
        self.mock_deepseek_client.analyze_code.return_value = {
            'quality_score': 0.85,
            'suggestions': ['Improve error handling', 'Add more tests']
        }
        
        # Test repository analysis
        result = await self.github_integration.analyze_repository("test-repo", "test-owner")
        
        self.assertIsInstance(result, RepositoryAnalysis)
        self.assertEqual(result.repo_name, "test-repo")
        self.assertIn("Python", result.language_distribution)
    
    async def test_create_intelligent_pr(self):
        """Test intelligent PR creation"""
        with patch.object(self.github_integration, '_create_github_pr') as mock_create_pr:
            mock_create_pr.return_value = {
                'pr_number': 123,
                'pr_url': 'https://github.com/test/repo/pull/123'
            }
            
            result = await self.github_integration.create_intelligent_pr(
                "test-repo", "test-owner", "feature-branch", "main", 
                "Test PR", "Test description"
            )
            
            self.assertIn('pr_number', result)
            self.assertEqual(result['pr_number'], 123)
    
    async def test_optimize_repository_structure(self):
        """Test repository structure optimization"""
        result = await self.github_integration.optimize_repository_structure(
            "test-repo", "test-owner"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('optimization_suggestions', result)


class TestCICDPipelineIntelligence(unittest.TestCase):
    """Test CI/CD Pipeline Intelligence functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.mock_deepseek_client = Mock(spec=DeepSeekClient)
        self.cicd_intelligence = CICDPipelineIntelligence(self.mock_deepseek_client)
    
    def test_initialization(self):
        """Test CI/CD intelligence initialization"""
        self.assertIsNotNone(self.cicd_intelligence)
        self.assertEqual(self.cicd_intelligence.ai_client, self.mock_deepseek_client)
    
    async def test_analyze_pipeline(self):
        """Test pipeline analysis"""
        sample_config = """
        name: Test Pipeline
        on: [push]
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v2
              - run: echo "test"
        """
        
        # Mock AI analysis
        self.mock_deepseek_client.analyze_code.return_value = {
            'performance_score': 0.75,
            'optimization_opportunities': ['Add caching', 'Parallelize jobs']
        }
        
        result = await self.cicd_intelligence.analyze_pipeline(
            sample_config, "github_actions"
        )
        
        self.assertIsInstance(result, PipelineAnalysis)
        self.assertGreater(len(result.optimization_opportunities), 0)
    
    async def test_generate_smart_pipeline(self):
        """Test smart pipeline generation"""
        project_info = {
            'name': 'test-project',
            'language': 'Python',
            'framework': 'FastAPI'
        }
        
        result = await self.cicd_intelligence.generate_smart_pipeline(
            project_info, "github_actions"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('pipeline_config', result)
        self.assertIn('documentation', result)
    
    async def test_optimize_github_actions(self):
        """Test GitHub Actions optimization"""
        sample_workflow = """
        name: Basic workflow
        on: push
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v2
              - run: python -m pytest
        """
        
        result = await self.cicd_intelligence.optimize_github_actions(sample_workflow)
        
        self.assertIsInstance(result, dict)
        self.assertIn('optimized_workflow', result)
        self.assertIn('optimizations_applied', result)
    
    async def test_monitor_pipeline_health(self):
        """Test pipeline health monitoring"""
        metrics_data = {
            'build_time': 300,
            'success_rate': 0.95,
            'error_rate': 0.05
        }
        
        result = await self.cicd_intelligence.monitor_pipeline_health(
            "test-pipeline", metrics_data
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('health_status', result)
        self.assertIn('predictions', result)


class TestIntegrationAgent(unittest.TestCase):
    """Test Integration Agent functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.integration_agent = IntegrationAgent()
    
    async def test_agent_initialization(self):
        """Test agent initialization"""
        await self.integration_agent.initialize()
        self.assertTrue(self.integration_agent.is_initialized)
        self.assertIsNotNone(self.integration_agent.capabilities)
    
    async def test_github_repository_analysis_task(self):
        """Test GitHub repository analysis task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'github_repository_analysis',
            'repository_name': 'test-repo',
            'owner': 'test-owner'
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('repository_analysis', result)
        self.assertIn('analysis_timestamp', result)
    
    async def test_intelligent_pr_management_task(self):
        """Test intelligent PR management task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'intelligent_pr_management',
            'repository_name': 'test-repo',
            'owner': 'test-owner',
            'source_branch': 'feature',
            'target_branch': 'main',
            'title': 'Test PR',
            'description': 'Test description'
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('pr_creation_result', result)
        self.assertIn('ai_enhancements_applied', result)
    
    async def test_cicd_pipeline_optimization_task(self):
        """Test CI/CD pipeline optimization task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'cicd_pipeline_optimization',
            'pipeline_config': 'name: test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest',
            'platform': 'github_actions'
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('pipeline_analysis', result)
        self.assertIn('optimization_results', result)
    
    async def test_smart_pipeline_generation_task(self):
        """Test smart pipeline generation task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'smart_pipeline_generation',
            'project_info': {'name': 'test', 'language': 'Python'},
            'platform': 'github_actions'
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('pipeline_generation_result', result)
        self.assertIn('platform', result)
    
    async def test_auto_deployment_task(self):
        """Test automated deployment task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'auto_deployment',
            'application_info': {'name': 'test-app'},
            'deployment_target': 'docker'
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('deployment_status', result)
        self.assertIn('deployment_url', result)
    
    async def test_pipeline_health_monitoring_task(self):
        """Test pipeline health monitoring task"""
        await self.integration_agent.initialize()
        
        result = await self.integration_agent.execute_task({
            'task_type': 'pipeline_health_monitoring',
            'pipeline_id': 'test-pipeline',
            'metrics_data': {'build_time': 300}
        })
        
        self.assertIsInstance(result, dict)
        self.assertIn('health_status', result)
    
    async def test_invalid_task_type(self):
        """Test handling of invalid task type"""
        await self.integration_agent.initialize()
        
        with self.assertRaises(ValueError):
            await self.integration_agent.execute_task({
                'task_type': 'invalid_task'
            })


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests"""
    
    async def test_full_workflow(self):
        """Test complete workflow from analysis to deployment"""
        agent = IntegrationAgent()
        await agent.initialize()
        
        # Step 1: Analyze repository
        analysis_result = await agent.execute_task({
            'task_type': 'github_repository_analysis',
            'repository_name': 'SEAgent',
            'owner': 'test-user'
        })
        
        self.assertIn('repository_analysis', analysis_result)
        
        # Step 2: Generate smart pipeline
        pipeline_result = await agent.execute_task({
            'task_type': 'smart_pipeline_generation',
            'project_info': {'name': 'SEAgent', 'language': 'Python'},
            'platform': 'github_actions'
        })
        
        self.assertIn('pipeline_generation_result', pipeline_result)
        
        # Step 3: Deploy application
        deployment_result = await agent.execute_task({
            'task_type': 'auto_deployment',
            'application_info': {'name': 'seagent'},
            'deployment_target': 'docker'
        })
        
        self.assertIn('deployment_status', deployment_result)
        self.assertEqual(deployment_result['deployment_status'], 'success')


class IntegrationTestRunner:
    """Test runner for integration tests"""
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Running SEAgent Integration Tests")
        print("=" * 50)
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [
            TestGitHubDeepIntegration,
            TestCICDPipelineIntelligence,
            TestIntegrationAgent,
            TestEndToEndIntegration
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
        
        # Run tests with async support
        runner = unittest.TextTestRunner(verbosity=2)
        
        # Convert async tests to sync for unittest compatibility
        await self._run_async_tests()
        
        print("\n✅ All integration tests completed!")
    
    async def _run_async_tests(self):
        """Run async tests manually"""
        print("\n🔄 Running async integration tests...")
        
        # Test GitHub Deep Integration
        print("\n📊 Testing GitHub Deep Integration...")
        github_test = TestGitHubDeepIntegration()
        github_test.setUp()
        await github_test.test_analyze_repository()
        await github_test.test_create_intelligent_pr()
        await github_test.test_optimize_repository_structure()
        print("✅ GitHub integration tests passed")
        
        # Test CI/CD Pipeline Intelligence
        print("\n🔧 Testing CI/CD Pipeline Intelligence...")
        cicd_test = TestCICDPipelineIntelligence()
        cicd_test.setUp()
        await cicd_test.test_analyze_pipeline()
        await cicd_test.test_generate_smart_pipeline()
        await cicd_test.test_optimize_github_actions()
        await cicd_test.test_monitor_pipeline_health()
        print("✅ CI/CD intelligence tests passed")
        
        # Test Integration Agent
        print("\n🤖 Testing Integration Agent...")
        agent_test = TestIntegrationAgent()
        agent_test.setUp()
        await agent_test.test_agent_initialization()
        await agent_test.test_github_repository_analysis_task()
        await agent_test.test_intelligent_pr_management_task()
        await agent_test.test_cicd_pipeline_optimization_task()
        await agent_test.test_smart_pipeline_generation_task()
        await agent_test.test_auto_deployment_task()
        await agent_test.test_pipeline_health_monitoring_task()
        print("✅ Integration agent tests passed")
        
        # Test End-to-End Integration
        print("\n🌐 Testing End-to-End Integration...")
        e2e_test = TestEndToEndIntegration()
        await e2e_test.test_full_workflow()
        print("✅ End-to-end integration tests passed")
    
    def run_sync_tests(self):
        """Run synchronous tests"""
        print("\n⚙️  Running synchronous tests...")
        
        # Basic initialization tests
        github_test = TestGitHubDeepIntegration()
        github_test.setUp()
        github_test.test_initialization()
        
        cicd_test = TestCICDPipelineIntelligence()
        cicd_test.setUp()
        cicd_test.test_initialization()
        
        print("✅ Synchronous tests passed")


async def main():
    """Main test function"""
    print("🧪 SEAgent Integration Test Suite")
    print("🔬 Testing GitHub Deep Integration & CI/CD Pipeline Intelligence")
    print("=" * 70)
    
    test_runner = IntegrationTestRunner()
    
    try:
        # Run synchronous tests first
        test_runner.run_sync_tests()
        
        # Run async tests
        await test_runner.run_all_tests()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
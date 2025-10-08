"""
Standalone GitHub Deep Integration and CI/CD Pipeline Intelligence Demo
Direct testing of integration features without agent wrapper
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.github_integration import GitHubDeepIntegration
from integrations.cicd_intelligence import CICDPipelineIntelligence
from config.deepseek_client import DeepSeekClient


class StandaloneIntegrationDemo:
    """Standalone demonstration of integration features"""
    
    def __init__(self):
        self.github_integration = None
        self.cicd_intelligence = None
        self.deepseek_client = None
    
    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing SEAgent Integration Components")
        print("=" * 60)
        
        # Initialize DeepSeek client
        await self._init_deepseek()
        
        # Initialize GitHub integration
        await self._init_github()
        
        # Initialize CI/CD intelligence
        await self._init_cicd()
        
        print("✅ All components initialized successfully!\n")
    
    async def _init_deepseek(self):
        """Initialize DeepSeek client"""
        try:
            api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
            if api_key and len(api_key) > 10:
                self.deepseek_client = DeepSeekClient(
                    api_key=api_key,
                    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
                    model=os.getenv('DEEPSEEK_MODEL', 'deepseek-coder')
                )
                print("🧠 DeepSeek-Coder V2 client initialized")
            else:
                print("⚠️  DeepSeek API key not found - running in simulation mode")
        except Exception as e:
            print(f"⚠️  DeepSeek initialization failed: {e}")
    
    async def _init_github(self):
        """Initialize GitHub integration"""
        try:
            github_token = os.getenv('GITHUB_TOKEN', '').strip()
            if github_token:
                self.github_integration = GitHubDeepIntegration(github_token, self.deepseek_client)
                print("🐙 GitHub Deep Integration initialized")
            else:
                print("⚠️  GitHub token not found - running in simulation mode")
        except Exception as e:
            print(f"⚠️  GitHub integration initialization failed: {e}")
    
    async def _init_cicd(self):
        """Initialize CI/CD intelligence"""
        try:
            self.cicd_intelligence = CICDPipelineIntelligence(self.deepseek_client)
            print("🔧 CI/CD Pipeline Intelligence initialized")
        except Exception as e:
            print(f"⚠️  CI/CD intelligence initialization failed: {e}")
    
    async def demo_github_analysis(self):
        """Demo GitHub repository analysis"""
        print("\n📊 GitHub Repository Analysis Demo")
        print("-" * 40)
        
        if self.github_integration:
            try:
                # Test with a real repository
                result = await self.github_integration.analyze_repository("SEAgent", "navicharan")
                print("📈 Repository Analysis Results:")
                self._print_json({
                    'repo_name': result.repo_name,
                    'language_distribution': result.language_distribution,
                    'code_quality_score': result.code_quality_score,
                    'security_issues': result.security_issues,
                    'test_coverage': result.test_coverage,
                    'last_updated': result.last_updated.isoformat() if result.last_updated else None
                })
            except Exception as e:
                print(f"⚠️  Analysis failed: {e}")
                # Show simulation instead
                result = await self._simulate_github_analysis()
                print("📈 Repository Analysis Results (Simulated):")
                self._print_json(result)
        else:
            result = await self._simulate_github_analysis()
            print("📈 Repository Analysis Results (Simulated):")
            self._print_json(result)
    
    async def demo_pr_creation(self):
        """Demo intelligent PR creation"""
        print("\n🔀 Intelligent PR Creation Demo")
        print("-" * 40)
        
        if self.github_integration:
            try:
                result = await self.github_integration.create_intelligent_pr(
                    "SEAgent", "navicharan", "main", "main",
                    "Demo: AI-Enhanced Features",
                    "Demonstration of intelligent PR creation with AI optimization"
                )
                print("🤖 PR Creation Results:")
                self._print_json(result)
            except Exception as e:
                print(f"⚠️  PR creation failed: {e}")
                result = await self._simulate_pr_creation()
                print("🤖 PR Creation Results (Simulated):")
                self._print_json(result)
        else:
            result = await self._simulate_pr_creation()
            print("🤖 PR Creation Results (Simulated):")
            self._print_json(result)
    
    async def demo_pipeline_optimization(self):
        """Demo CI/CD pipeline optimization"""
        print("\n⚡ CI/CD Pipeline Optimization Demo")
        print("-" * 40)
        
        sample_pipeline = '''
name: SEAgent CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t seagent .
        '''
        
        if self.cicd_intelligence:
            try:
                result = await self.cicd_intelligence.analyze_pipeline(
                    sample_pipeline, "github_actions"
                )
                print("🔧 Pipeline Analysis Results:")
                self._print_json({
                    'platform': result.platform,
                    'performance_score': result.performance_score,
                    'optimization_opportunities': result.optimization_opportunities,
                    'estimated_improvements': result.estimated_improvements,
                    'security_findings': result.security_findings
                })
            except Exception as e:
                print(f"⚠️  Pipeline optimization failed: {e}")
                result = await self._simulate_pipeline_optimization()
                print("🔧 Pipeline Analysis Results (Simulated):")
                self._print_json(result)
        else:
            result = await self._simulate_pipeline_optimization()
            print("🔧 Pipeline Analysis Results (Simulated):")
            self._print_json(result)
    
    async def demo_smart_pipeline_generation(self):
        """Demo smart pipeline generation"""
        print("\n🏗️  Smart Pipeline Generation Demo")
        print("-" * 40)
        
        project_info = {
            'name': 'SEAgent',
            'language': 'Python',
            'framework': 'FastAPI',
            'testing_framework': 'pytest',
            'deployment_target': 'Docker',
            'security_requirements': ['dependency_scan', 'secret_detection'],
            'performance_requirements': ['load_testing', 'monitoring']
        }
        
        if self.cicd_intelligence:
            try:
                result = await self.cicd_intelligence.generate_smart_pipeline(
                    project_info, "github_actions"
                )
                print("🎯 Smart Pipeline Generation Results:")
                self._print_json(result)
            except Exception as e:
                print(f"⚠️  Pipeline generation failed: {e}")
                result = await self._simulate_smart_generation()
                print("🎯 Smart Pipeline Generation Results (Simulated):")
                self._print_json(result)
        else:
            result = await self._simulate_smart_generation()
            print("🎯 Smart Pipeline Generation Results (Simulated):")
            self._print_json(result)
    
    async def demo_health_monitoring(self):
        """Demo pipeline health monitoring"""
        print("\n💊 Pipeline Health Monitoring Demo")
        print("-" * 40)
        
        metrics_data = {
            'pipeline_id': 'seagent-main-pipeline',
            'build_time': 380,
            'success_rate': 0.92,
            'resource_usage': {
                'cpu': 0.75,
                'memory': 0.60,
                'storage': 0.45
            },
            'error_rate': 0.08,
            'deployment_frequency': 'daily',
            'mean_time_to_recovery': 45
        }
        
        if self.cicd_intelligence:
            try:
                result = await self.cicd_intelligence.monitor_pipeline_health(
                    'seagent-main-pipeline', metrics_data
                )
                print("📊 Health Monitoring Results:")
                self._print_json(result)
            except Exception as e:
                print(f"⚠️  Health monitoring failed: {e}")
                result = await self._simulate_health_monitoring()
                print("📊 Health Monitoring Results (Simulated):")
                self._print_json(result)
        else:
            result = await self._simulate_health_monitoring()
            print("📊 Health Monitoring Results (Simulated):")
            self._print_json(result)
    
    async def run_full_demo(self):
        """Run all demos in sequence"""
        print("\n🎯 Running Complete Integration Demo")
        print("=" * 50)
        
        demos = [
            ("GitHub Repository Analysis", self.demo_github_analysis),
            ("Intelligent PR Creation", self.demo_pr_creation),
            ("CI/CD Pipeline Optimization", self.demo_pipeline_optimization),
            ("Smart Pipeline Generation", self.demo_smart_pipeline_generation),
            ("Pipeline Health Monitoring", self.demo_health_monitoring)
        ]
        
        for demo_name, demo_func in demos:
            print(f"\n🚀 Running {demo_name}...")
            try:
                await demo_func()
                print(f"✅ {demo_name} completed successfully")
            except Exception as e:
                print(f"❌ {demo_name} failed: {e}")
            
            # Small delay between demos
            await asyncio.sleep(1)
        
        print("\n🎉 Full demo completed!")
    
    # Simulation methods
    async def _simulate_github_analysis(self):
        """Simulate GitHub analysis"""
        await asyncio.sleep(1)  # Simulate processing time
        return {
            'repo_name': 'SEAgent',
            'language_distribution': {
                'Python': 85.0,
                'Dockerfile': 8.0,
                'YAML': 4.0,
                'Markdown': 3.0
            },
            'code_quality_score': 0.87,
            'security_issues': [
                {'type': 'dependency', 'severity': 'medium', 'description': 'Outdated package detected'},
                {'type': 'secret', 'severity': 'low', 'description': 'Potential API key in comments'}
            ],
            'test_coverage': 78.5,
            'last_updated': datetime.now().isoformat(),
            'recommendations': [
                'Add more comprehensive unit tests',
                'Update dependencies to latest versions',
                'Implement automated security scanning'
            ]
        }
    
    async def _simulate_pr_creation(self):
        """Simulate PR creation"""
        await asyncio.sleep(0.5)
        return {
            'pr_number': 42,
            'pr_url': 'https://github.com/navicharan/SEAgent/pull/42',
            'title': 'Demo: AI-Enhanced Features',
            'ai_enhancements': [
                'Optimized commit message for clarity',
                'Added comprehensive PR description',
                'Suggested relevant reviewers based on code changes',
                'Generated automated test recommendations'
            ],
            'auto_checks': {
                'syntax_validation': 'passed',
                'security_scan': 'passed',
                'dependency_check': 'passed',
                'code_style': 'passed'
            },
            'estimated_review_time': '15 minutes'
        }
    
    async def _simulate_pipeline_optimization(self):
        """Simulate pipeline optimization"""
        await asyncio.sleep(1.5)
        return {
            'platform': 'github_actions',
            'performance_score': 0.75,
            'optimization_opportunities': [
                'Add dependency caching to reduce build time by 40%',
                'Parallelize test execution across multiple runners',
                'Use matrix builds for multi-version testing',
                'Implement incremental builds for faster feedback'
            ],
            'estimated_improvements': {
                'build_time_reduction': '45%',
                'cost_savings': '$25/month',
                'reliability_improvement': '12%'
            },
            'security_findings': [
                'Add secret scanning in pipeline',
                'Implement SAST (Static Application Security Testing)',
                'Add container image vulnerability scanning'
            ],
            'recommended_actions': [
                {'action': 'Add cache step', 'priority': 'high', 'effort': 'low'},
                {'action': 'Setup parallel jobs', 'priority': 'medium', 'effort': 'medium'},
                {'action': 'Add security gates', 'priority': 'high', 'effort': 'medium'}
            ]
        }
    
    async def _simulate_smart_generation(self):
        """Simulate smart pipeline generation"""
        await asyncio.sleep(2)
        return {
            'pipeline_config': '''# Generated Smart CI/CD Pipeline for SEAgent
name: SEAgent Smart CI/CD
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Security Scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: security-results.sarif

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests with coverage
        run: pytest --cov=./ --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  build:
    needs: [security, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t seagent:${{ github.sha }} .
      - name: Test Docker image
        run: docker run --rm seagent:${{ github.sha }} python -m pytest

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: [build]
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: echo "Deploying to staging environment"
''',
            'documentation': '''# SEAgent Smart CI/CD Pipeline

This pipeline includes:
- Multi-version Python testing (3.9, 3.10, 3.11)
- Dependency caching for faster builds
- Comprehensive security scanning
- Test coverage reporting
- Docker image building and testing
- Automated deployment to staging

## Features:
- **Security First**: Integrated security scanning
- **Performance Optimized**: Parallel jobs and caching
- **Quality Assured**: Comprehensive testing and coverage
- **Deployment Ready**: Automated staging deployment
''',
            'features_included': [
                'Multi-version testing',
                'Security scanning',
                'Dependency caching',
                'Coverage reporting',
                'Docker integration',
                'Automated deployment'
            ],
            'estimated_build_time': '8-12 minutes',
            'estimated_monthly_cost': '$15-25'
        }
    
    async def _simulate_health_monitoring(self):
        """Simulate health monitoring"""
        await asyncio.sleep(1)
        return {
            'pipeline_id': 'seagent-main-pipeline',
            'health_status': 'healthy',
            'overall_health_score': 0.92,
            'anomalies_detected': [
                {
                    'type': 'build_time_spike',
                    'severity': 'low',
                    'description': 'Build time increased by 15% in last 3 runs',
                    'suggestion': 'Check for new dependencies or test additions'
                }
            ],
            'predictions': {
                'failure_probability_next_24h': 0.05,
                'expected_build_time': '6.5 minutes',
                'resource_usage_trend': 'stable'
            },
            'recommendations': [
                'Consider adding more parallel jobs for faster execution',
                'Update runner image to latest version for better performance',
                'Review recent dependency additions for performance impact'
            ],
            'metrics_summary': {
                'success_rate_7d': 0.94,
                'average_build_time_7d': '6.2 minutes',
                'deployment_frequency': '2.3 per day',
                'mean_time_to_recovery': '22 minutes'
            },
            'alerts': []
        }
    
    def _print_json(self, data: dict, indent: int = 2):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=indent, default=str))
    
    async def interactive_mode(self):
        """Run interactive demo mode"""
        print("\n🎮 Interactive Demo Mode")
        print("=" * 40)
        print("Available Commands:")
        print("1. github_analysis - Analyze GitHub repository")
        print("2. pr_creation - Create intelligent PR")
        print("3. pipeline_optimization - Optimize CI/CD pipeline")
        print("4. smart_generation - Generate smart pipeline")
        print("5. health_monitoring - Monitor pipeline health")
        print("6. full_demo - Run all demos")
        print("7. quit - Exit")
        print("-" * 40)
        
        while True:
            try:
                command = input("\n🔹 Enter command (or 'quit' to exit): ").strip().lower()
                
                if command == 'quit' or command == '7':
                    break
                elif command == '1' or command == 'github_analysis':
                    await self.demo_github_analysis()
                elif command == '2' or command == 'pr_creation':
                    await self.demo_pr_creation()
                elif command == '3' or command == 'pipeline_optimization':
                    await self.demo_pipeline_optimization()
                elif command == '4' or command == 'smart_generation':
                    await self.demo_smart_pipeline_generation()
                elif command == '5' or command == 'health_monitoring':
                    await self.demo_health_monitoring()
                elif command == '6' or command == 'full_demo':
                    await self.run_full_demo()
                else:
                    print("❌ Unknown command. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error during demo: {e}")


async def main():
    """Main demo function"""
    print("🌟 SEAgent GitHub Deep Integration & CI/CD Intelligence Demo")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Enhanced with DeepSeek-Coder V2 AI Integration")
    print("🎯 Standalone Demo - Direct Feature Testing")
    
    demo = StandaloneIntegrationDemo()
    
    try:
        await demo.initialize()
        
        # Check for demo mode
        demo_mode = sys.argv[1] if len(sys.argv) > 1 else 'interactive'
        
        if demo_mode == 'full':
            await demo.run_full_demo()
        else:
            await demo.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Thank you for trying SEAgent!")


if __name__ == "__main__":
    asyncio.run(main())
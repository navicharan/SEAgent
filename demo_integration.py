"""
GitHub Deep Integration and CI/CD Pipeline Intelligence Demo
Enhanced SEAgent with DeepSeek-Coder V2 integration testing
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.integration_agent import IntegrationAgent
from integrations.github_integration import GitHubDeepIntegration
from integrations.cicd_intelligence import CICDPipelineIntelligence
from config.deepseek_client import DeepSeekClient


class IntegrationDemo:
    """Demonstration of advanced GitHub and CI/CD integration features"""
    
    def __init__(self):
        self.integration_agent = None
        self.github_integration = None
        self.cicd_intelligence = None
        self.deepseek_client = None
    
    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing SEAgent GitHub Deep Integration Demo")
        print("=" * 60)
        
        # Initialize DeepSeek client
        await self._init_deepseek()
        
        # Initialize GitHub integration
        await self._init_github()
        
        # Initialize CI/CD intelligence
        await self._init_cicd()
        
        # Initialize integration agent
        await self._init_integration_agent()
        
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
    
    async def _init_integration_agent(self):
        """Initialize integration agent"""
        try:
            self.integration_agent = IntegrationAgent()
            await self.integration_agent.initialize()
            print("🤖 Integration Agent initialized")
        except Exception as e:
            print(f"⚠️  Integration agent initialization failed: {e}")
    
    async def run_demo(self):
        """Run comprehensive demo of all features"""
        print("🎯 Starting GitHub Deep Integration & CI/CD Intelligence Demo")
        print("=" * 70)
        
        # Demo 1: GitHub Repository Analysis
        await self._demo_github_analysis()
        
        # Demo 2: Intelligent PR Management
        await self._demo_pr_management()
        
        # Demo 3: CI/CD Pipeline Optimization
        await self._demo_pipeline_optimization()
        
        # Demo 4: Smart Pipeline Generation
        await self._demo_smart_pipeline_generation()
        
        # Demo 5: Auto Deployment
        await self._demo_auto_deployment()
        
        # Demo 6: Pipeline Health Monitoring
        await self._demo_health_monitoring()
        
        print("\n🎉 Demo completed successfully!")
        print("=" * 70)
    
    async def _demo_github_analysis(self):
        """Demo GitHub repository analysis"""
        print("\n📊 Demo 1: GitHub Repository Analysis")
        print("-" * 40)
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'github_repository_analysis',
                'repository_name': 'SEAgent',
                'owner': 'example-user',
                'analysis_type': 'comprehensive'
            })
            
            print("📈 Repository Analysis Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    async def _demo_pr_management(self):
        """Demo intelligent PR management"""
        print("\n🔀 Demo 2: Intelligent PR Management")
        print("-" * 40)
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'intelligent_pr_management',
                'repository_name': 'SEAgent',
                'owner': 'example-user',
                'source_branch': 'feature/ai-enhancements',
                'target_branch': 'main',
                'title': 'AI-Enhanced Code Generation Features',
                'description': 'Adding advanced AI capabilities with DeepSeek integration'
            })
            
            print("🤖 Intelligent PR Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    async def _demo_pipeline_optimization(self):
        """Demo CI/CD pipeline optimization"""
        print("\n⚡ Demo 3: CI/CD Pipeline Optimization")
        print("-" * 40)
        
        sample_pipeline = '''
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v2
      - name: Build application
        run: python setup.py build
        '''
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'cicd_pipeline_optimization',
                'pipeline_config': sample_pipeline,
                'platform': 'github_actions',
                'historical_data': {
                    'average_runtime': 450,
                    'failure_rate': 0.05,
                    'cost_per_run': 2.5
                }
            })
            
            print("🔧 Pipeline Optimization Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    async def _demo_smart_pipeline_generation(self):
        """Demo smart pipeline generation"""
        print("\n🏗️  Demo 4: Smart Pipeline Generation")
        print("-" * 40)
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'smart_pipeline_generation',
                'project_info': {
                    'name': 'SEAgent',
                    'language': 'Python',
                    'framework': 'FastAPI',
                    'testing_framework': 'pytest',
                    'deployment_target': 'Docker'
                },
                'platform': 'github_actions',
                'requirements': ['testing', 'security_scan', 'docker_build', 'deployment']
            })
            
            print("🎯 Smart Pipeline Generation Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    async def _demo_auto_deployment(self):
        """Demo automated deployment"""
        print("\n🚀 Demo 5: Automated Deployment")
        print("-" * 40)
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'auto_deployment',
                'application_info': {
                    'name': 'seagent-api',
                    'version': '1.0.0',
                    'port': 8000
                },
                'deployment_target': 'docker',
                'deployment_strategy': 'blue_green'
            })
            
            print("🎯 Auto Deployment Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    async def _demo_health_monitoring(self):
        """Demo pipeline health monitoring"""
        print("\n💊 Demo 6: Pipeline Health Monitoring")
        print("-" * 40)
        
        if self.integration_agent:
            result = await self.integration_agent.execute_task({
                'task_type': 'pipeline_health_monitoring',
                'pipeline_id': 'seagent-main-pipeline',
                'metrics_data': {
                    'build_time': 380,
                    'success_rate': 0.92,
                    'resource_usage': {
                        'cpu': 0.75,
                        'memory': 0.60,
                        'storage': 0.45
                    },
                    'error_rate': 0.08
                }
            })
            
            print("📊 Health Monitoring Results:")
            self._print_json(result)
        else:
            print("⚠️  Integration agent not available")
    
    def _print_json(self, data: dict, indent: int = 2):
        """Pretty print JSON data"""
        print(json.dumps(data, indent=indent, default=str))
    
    async def interactive_demo(self):
        """Run interactive demo mode"""
        print("\n🎮 Interactive Demo Mode")
        print("=" * 40)
        print("Available Commands:")
        print("1. github_analysis - Analyze GitHub repository")
        print("2. pr_management - Create intelligent PR")
        print("3. pipeline_optimization - Optimize CI/CD pipeline")
        print("4. smart_generation - Generate smart pipeline")
        print("5. auto_deployment - Execute automated deployment")
        print("6. health_monitoring - Monitor pipeline health")
        print("7. full_demo - Run all demos")
        print("8. quit - Exit")
        print("-" * 40)
        
        while True:
            try:
                command = input("\n🔹 Enter command (or 'quit' to exit): ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == '1' or command == 'github_analysis':
                    await self._demo_github_analysis()
                elif command == '2' or command == 'pr_management':
                    await self._demo_pr_management()
                elif command == '3' or command == 'pipeline_optimization':
                    await self._demo_pipeline_optimization()
                elif command == '4' or command == 'smart_generation':
                    await self._demo_smart_pipeline_generation()
                elif command == '5' or command == 'auto_deployment':
                    await self._demo_auto_deployment()
                elif command == '6' or command == 'health_monitoring':
                    await self._demo_health_monitoring()
                elif command == '7' or command == 'full_demo':
                    await self.run_demo()
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
    
    demo = IntegrationDemo()
    
    try:
        await demo.initialize()
        
        # Check for demo mode
        demo_mode = sys.argv[1] if len(sys.argv) > 1 else 'interactive'
        
        if demo_mode == 'full':
            await demo.run_demo()
        else:
            await demo.interactive_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Thank you for trying SEAgent!")


if __name__ == "__main__":
    asyncio.run(main())
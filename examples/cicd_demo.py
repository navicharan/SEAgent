#!/usr/bin/env python3
"""
CI/CD Pipeline Integration Demo
Demonstrates automated pipeline creation, optimization, and deployment
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.agent_coordinator import AgentCoordinator, Task, TaskType
from config.settings_simple import Settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_cicd_pipeline_integration():
    """Demonstrate complete CI/CD pipeline integration"""
    
    print("🚀 SEAgent CI/CD Pipeline Integration Demo")
    print("=" * 60)
    
    # Initialize coordinator
    settings = Settings()
    coordinator = AgentCoordinator(settings)
    await coordinator.initialize()
    
    # Sample project information
    project_info = {
        "name": "seagent-demo",
        "description": "Demo project for CI/CD integration",
        "language": "python",
        "framework": "fastapi",
        "repository": "demo-org/seagent-demo",
        "has_tests": True,
        "has_docker": True,
        "deployment_targets": ["staging", "production"]
    }
    
    print(f"📋 Project: {project_info['name']}")
    print(f"🔧 Framework: {project_info['framework']}")
    print(f"🐙 Repository: {project_info['repository']}")
    print()
    
    try:
        # 1. Create Intelligent CI/CD Pipeline
        print("1️⃣ Creating intelligent CI/CD pipeline...")
        create_task = Task(
            id="demo_create_pipeline",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "create_pipeline",
                "project_info": project_info,
                "platform": "github_actions",
                "requirements": [
                    "automated_testing",
                    "security_scanning",
                    "code_quality_checks",
                    "docker_build",
                    "staging_deployment",
                    "production_deployment"
                ]
            }
        )
        
        create_task_id = await coordinator.submit_task(create_task)
        
        # Wait for completion
        await asyncio.sleep(3)
        create_result = await coordinator.get_task_status(create_task_id)
        
        if create_result and create_result['status'] == 'completed':
            print("✅ CI/CD Pipeline created successfully!")
            result_data = create_result['result']
            print(f"   📝 Platform: {result_data.get('platform', 'N/A')}")
            print(f"   🔧 Features: {', '.join(result_data.get('features_included', []))}")
            print(f"   📄 Files created: {len(result_data.get('pipeline_files', {}))}")
        else:
            print("❌ Pipeline creation failed or still in progress")
        print()
        
        # 2. Analyze existing pipeline (simulation)
        print("2️⃣ Analyzing pipeline for optimization opportunities...")
        
        sample_pipeline_config = """
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
"""
        
        analyze_task = Task(
            id="demo_analyze_pipeline",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "analyze_pipeline",
                "pipeline_config": sample_pipeline_config,
                "platform": "github_actions",
                "historical_data": {
                    "total_runs": 150,
                    "success_rate": 0.87,
                    "avg_duration": 420.0,
                    "failure_patterns": ["timeout", "dependency_error"],
                    "cost_per_run": 2.50
                }
            }
        )
        
        analyze_task_id = await coordinator.submit_task(analyze_task)
        await asyncio.sleep(3)
        analyze_result = await coordinator.get_task_status(analyze_task_id)
        
        if analyze_result and analyze_result['status'] == 'completed':
            print("✅ Pipeline analysis completed!")
            result_data = analyze_result['result']
            analysis = result_data.get('analysis_results', {})
            print(f"   📊 Performance Score: {analysis.get('performance_score', 0):.2f}/1.0")
            print(f"   🔒 Reliability Score: {analysis.get('reliability_score', 0):.2f}/1.0")
            print(f"   💰 Cost Efficiency: {analysis.get('cost_efficiency_score', 0):.2f}/1.0")
            print(f"   🎯 Overall Score: {analysis.get('overall_score', 0):.2f}/1.0")
            
            recommendations = result_data.get('optimization_recommendations', [])
            if recommendations:
                print(f"   🔧 Optimization opportunities found: {len(recommendations)}")
        print()
        
        # 3. Optimize pipeline
        print("3️⃣ Optimizing pipeline for performance and cost...")
        optimize_task = Task(
            id="demo_optimize_pipeline",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "optimize_pipeline",
                "pipeline_config": sample_pipeline_config,
                "platform": "github_actions",
                "optimization_goals": ["performance", "cost", "reliability"]
            }
        )
        
        optimize_task_id = await coordinator.submit_task(optimize_task)
        await asyncio.sleep(3)
        optimize_result = await coordinator.get_task_status(optimize_task_id)
        
        if optimize_result and optimize_result['status'] == 'completed':
            print("✅ Pipeline optimization completed!")
            result_data = optimize_result['result']
            improvements = result_data.get('improvements', [])
            savings = result_data.get('estimated_savings', {})
            print(f"   ⚡ Improvements applied: {len(improvements)}")
            print(f"   ⏱️  Time savings: {savings.get('time', 'N/A')}")
            print(f"   💵 Cost savings: {savings.get('cost', 'N/A')}")
            
            for improvement in improvements[:3]:  # Show first 3
                print(f"      • {improvement}")
        print()
        
        # 4. Setup GitHub Actions workflows
        print("4️⃣ Setting up GitHub Actions workflows...")
        setup_task = Task(
            id="demo_setup_github",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "setup_github_actions",
                "repository_name": "seagent-demo",
                "owner": "demo-org",
                "project_type": "python"
            }
        )
        
        setup_task_id = await coordinator.submit_task(setup_task)
        await asyncio.sleep(3)
        setup_result = await coordinator.get_task_status(setup_task_id)
        
        if setup_result and setup_result['status'] == 'completed':
            print("✅ GitHub Actions setup completed!")
            result_data = setup_result['result']
            workflows = result_data.get('workflows_created', [])
            print(f"   📄 Workflows created: {len(workflows)}")
            for workflow in workflows:
                print(f"      • {workflow}")
            
            next_steps = result_data.get('next_steps', [])
            if next_steps:
                print("   📋 Next steps:")
                for step in next_steps[:3]:  # Show first 3
                    print(f"      • {step}")
        print()
        
        # 5. Deploy to staging
        print("5️⃣ Deploying application to staging...")
        deploy_task = Task(
            id="demo_deploy_staging",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "deploy_application",
                "deployment_config": {
                    "app_name": "seagent-demo",
                    "image": "seagent-demo:latest",
                    "port": 8000,
                    "replicas": 2
                },
                "environment": "staging",
                "version": "v1.0.0"
            }
        )
        
        deploy_task_id = await coordinator.submit_task(deploy_task)
        await asyncio.sleep(3)
        deploy_result = await coordinator.get_task_status(deploy_task_id)
        
        if deploy_result and deploy_result['status'] == 'completed':
            print("✅ Staging deployment completed!")
            result_data = deploy_result['result']
            print(f"   🌍 Environment: {result_data.get('environment', 'N/A')}")
            print(f"   🏷️  Version: {result_data.get('version', 'N/A')}")
            print(f"   🔗 URL: {result_data.get('deployment_url', 'N/A')}")
            print(f"   ✅ Health checks: {result_data.get('health_checks', {}).get('status', 'N/A')}")
        print()
        
        # 6. Monitor pipeline health
        print("6️⃣ Monitoring pipeline health...")
        monitor_task = Task(
            id="demo_monitor_pipeline",
            type=TaskType.CICD,
            priority=1,
            project_id="demo_project",
            parameters={
                "task_type": "monitor_pipeline",
                "pipeline_id": "seagent-demo-ci",
                "platform": "github_actions"
            }
        )
        
        monitor_task_id = await coordinator.submit_task(monitor_task)
        await asyncio.sleep(3)
        monitor_result = await coordinator.get_task_status(monitor_task_id)
        
        if monitor_result and monitor_result['status'] == 'completed':
            print("✅ Pipeline monitoring active!")
            result_data = monitor_result['result']
            print(f"   🏥 Health status: {result_data.get('health_status', 'N/A')}")
            print(f"   📊 Health score: {result_data.get('overall_health_score', 0):.2f}/1.0")
            print(f"   🚨 Active alerts: {len(result_data.get('alerts', []))}")
            print(f"   💡 Recommendations: {len(result_data.get('recommendations', []))}")
        print()
        
        # 7. Demonstrate workflow execution
        print("7️⃣ Executing complete CI/CD workflow...")
        workflow_task_ids = await coordinator.execute_workflow(
            "cicd_deployment",
            "demo_project",
            {
                "pipeline_config": sample_pipeline_config,
                "platform": "github_actions",
                "deployment_targets": ["staging", "production"]
            }
        )
        
        print(f"✅ CI/CD workflow initiated!")
        print(f"   📋 Tasks created: {len(workflow_task_ids)}")
        print(f"   🆔 Workflow tasks: {', '.join(workflow_task_ids)}")
        print()
        
        # Show summary
        print("📊 CI/CD Integration Demo Summary")
        print("-" * 40)
        print("✅ Intelligent pipeline creation")
        print("✅ Pipeline analysis and optimization")
        print("✅ GitHub Actions setup")
        print("✅ Automated deployment")
        print("✅ Health monitoring")
        print("✅ Complete workflow orchestration")
        print()
        
        print("🎯 Key Features Demonstrated:")
        print("  • AI-powered pipeline optimization")
        print("  • Multi-platform CI/CD support")
        print("  • Automated deployment workflows")
        print("  • Real-time monitoring and alerting")
        print("  • Cost and performance optimization")
        print("  • Security-first pipeline design")
        print()
        
        print("🚀 Ready for production deployment!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
    
    finally:
        # Cleanup
        await coordinator.shutdown()


async def demo_github_actions_workflows():
    """Demonstrate GitHub Actions workflow templates"""
    
    print("\n🔧 GitHub Actions Workflow Templates")
    print("=" * 50)
    
    # Show the workflow files we created
    workflows_dir = Path(__file__).parent.parent / '.github' / 'workflows'
    
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob('*.yml'))
        print(f"📄 Found {len(workflow_files)} workflow files:")
        
        for workflow_file in workflow_files:
            print(f"   • {workflow_file.name}")
            
            # Show first few lines of each workflow
            try:
                with open(workflow_file, 'r') as f:
                    lines = f.readlines()[:10]  # First 10 lines
                    print(f"     Preview:")
                    for line in lines:
                        print(f"       {line.rstrip()}")
                    if len(lines) == 10:
                        print(f"       ... (truncated)")
                print()
            except Exception as e:
                print(f"     Error reading file: {e}")
    else:
        print("❌ Workflows directory not found")
    
    print("🔧 These workflows provide:")
    print("  • Comprehensive CI/CD pipeline")
    print("  • Multi-environment deployment")
    print("  • Security scanning and testing")
    print("  • Performance monitoring")
    print("  • Automated rollback capabilities")


if __name__ == "__main__":
    print("🤖 SEAgent - CI/CD Pipeline Integration Demo")
    print("This demo showcases automated CI/CD pipeline management")
    print()
    
    # Run the main demo
    asyncio.run(demo_cicd_pipeline_integration())
    
    # Show workflow templates
    asyncio.run(demo_github_actions_workflows())
    
    print("\n✨ Demo completed! Check the generated workflows in .github/workflows/")
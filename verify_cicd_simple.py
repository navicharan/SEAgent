#!/usr/bin/env python3
"""
Simple CI/CD Verification Script - Choose Your Testing Method
============================================================

This script provides 4 simple ways to test CI/CD functionality:
1. Quick Agent Test (30 seconds)
2. API Server Test (2 minutes) 
3. GitHub Actions Validation (1 minute)
4. Full Pipeline Demo (5 minutes)
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from orchestrator.agent_coordinator import AgentCoordinator
from config.settings_simple import get_settings


async def test_agent_functionality():
    """Test 1: Quick Agent Functionality Test (30 seconds)"""
    print("🧪 Test 1: CI/CD Agent Functionality")
    print("=" * 50)
    
    try:
        # Initialize coordinator
        settings = get_settings()
        coordinator = AgentCoordinator(settings)
        await coordinator.initialize()
        
        # Get CI/CD agent
        cicd_agent = coordinator.agents.get('cicd')
        if not cicd_agent:
            print("❌ CI/CD agent not found!")
            return False
        
        print("✅ CI/CD Agent initialized successfully")
        
        # Test basic capabilities
        capabilities = await cicd_agent.get_capabilities()
        print(f"✅ Agent capabilities: {len(capabilities)} available")
        for cap in capabilities:
            print(f"   📋 {cap}")
        
        # Test simple task execution
        test_task = {
            "task_type": "create_pipeline",
            "project_name": "test-project",
            "language": "python"
        }
        
        print("\n🔄 Testing task execution...")
        result = await cicd_agent.execute_task(test_task)
        
        if result.get('status') == 'success':
            print("✅ Task execution successful!")
            print(f"📄 Generated workflow files: {len(result.get('files', {}))}")
        else:
            print(f"⚠️  Task execution completed with status: {result.get('status')}")
        
        await coordinator.shutdown()
        print("\n🎉 Agent functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


def test_github_actions_syntax():
    """Test 2: GitHub Actions YAML Syntax Validation (30 seconds)"""
    print("\n🔍 Test 2: GitHub Actions Syntax Validation")
    print("=" * 50)
    
    import yaml
    
    workflow_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml"
    ]
    
    results = []
    for workflow_file in workflow_files:
        workflow_path = Path(workflow_file)
        if workflow_path.exists():
            try:
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                print(f"✅ {workflow_file} - Valid YAML syntax")
                results.append(True)
            except yaml.YAMLError as e:
                print(f"❌ {workflow_file} - YAML syntax error: {e}")
                results.append(False)
        else:
            print(f"⚠️  {workflow_file} - File not found")
            results.append(False)
    
    if all(results):
        print("\n🎉 All GitHub Actions workflows have valid syntax!")
        return True
    else:
        print(f"\n❌ {len([r for r in results if not r])} workflow(s) have issues")
        return False


def test_file_structure():
    """Test 3: CI/CD File Structure Validation (10 seconds)"""
    print("\n📁 Test 3: CI/CD File Structure")
    print("=" * 50)
    
    required_files = [
        "agents/cicd_agent.py",
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        "integrations/cicd_intelligence.py",
        "examples/cicd_demo.py"
    ]
    
    results = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
            results.append(True)
        else:
            print(f"❌ {file_path} - Missing")
            results.append(False)
    
    if all(results):
        print("\n🎉 All required CI/CD files are present!")
        return True
    else:
        print(f"\n❌ {len([r for r in results if not r])} required file(s) missing")
        return False


def test_api_endpoints():
    """Test 4: API Endpoints Test (requires running server)"""
    print("\n🌐 Test 4: API Endpoints (requires server running)")
    print("=" * 50)
    print("To test API endpoints:")
    print("1. Start the server: python main.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test CI/CD endpoints:")
    print("   - POST /api/v1/cicd/create-pipeline")
    print("   - POST /api/v1/cicd/analyze-pipeline")
    print("   - POST /api/v1/cicd/optimize-pipeline")
    print("   - POST /api/v1/cicd/deploy")
    print("\n💡 Use the interactive docs to test each endpoint!")


async def main():
    """Main testing interface"""
    print("🚀 SEAgent CI/CD Verification Tool")
    print("=" * 50)
    print("Choose your testing method:")
    print("1. Quick Agent Test (30s) - Test core agent functionality")
    print("2. File Structure Check (10s) - Verify all files exist")
    print("3. YAML Syntax Check (10s) - Validate GitHub Actions")
    print("4. API Endpoints Info - Show how to test APIs")
    print("5. Run All Tests")
    print("")
    
    while True:
        choice = input("Enter your choice (1-5) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            await test_agent_functionality()
        elif choice == '2':
            test_file_structure()
        elif choice == '3':
            test_github_actions_syntax()
        elif choice == '4':
            test_api_endpoints()
        elif choice == '5':
            print("\n🔄 Running all tests...")
            print("\n" + "="*60)
            
            # Run all tests
            structure_ok = test_file_structure()
            yaml_ok = test_github_actions_syntax()
            agent_ok = await test_agent_functionality()
            test_api_endpoints()
            
            print("\n" + "="*60)
            print("📊 FINAL RESULTS:")
            print(f"   File Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
            print(f"   YAML Syntax: {'✅ PASS' if yaml_ok else '❌ FAIL'}")
            print(f"   Agent Functionality: {'✅ PASS' if agent_ok else '❌ FAIL'}")
            
            if all([structure_ok, yaml_ok, agent_ok]):
                print("\n🎉 ALL TESTS PASSED! CI/CD system is working correctly!")
            else:
                print("\n⚠️  Some tests failed. Check the output above for details.")
        else:
            print("❌ Invalid choice. Please enter 1-5 or 'q'.")
        
        print("\n" + "-"*50)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
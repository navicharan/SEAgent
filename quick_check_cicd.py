#!/usr/bin/env python3
"""
Quick CI/CD Verification Script - Run this to check if CI/CD integration is working
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def check_files():
    """Check if all required files exist"""
    print("📁 Checking required files...")
    
    required_files = [
        '.github/workflows/ci.yml',
        '.github/workflows/cd.yml', 
        'agents/cicd_agent.py',
        'tests/test_cicd_agent.py',
        'examples/cicd_demo.py'
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def check_imports():
    """Check if CI/CD agent can be imported"""
    print("\n📦 Checking imports...")
    
    try:
        from agents.cicd_agent import CICDAgent
        print("✅ CICDAgent import successful")
        
        from orchestrator.agent_coordinator import TaskType
        if hasattr(TaskType, 'CICD'):
            print("✅ CICD TaskType exists")
        else:
            print("❌ CICD TaskType missing")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def check_yaml_syntax():
    """Check workflow YAML syntax"""
    print("\n📝 Checking YAML syntax...")
    
    try:
        import yaml
    except ImportError:
        print("⚠️ PyYAML not installed - skipping YAML validation")
        return True
    
    workflow_files = [
        '.github/workflows/ci.yml',
        '.github/workflows/cd.yml'
    ]
    
    for file_path in workflow_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ {file_path} - valid YAML")
            except yaml.YAMLError as e:
                print(f"❌ {file_path} - invalid YAML: {e}")
                return False
        else:
            print(f"⚠️ {file_path} - file not found")
    
    return True

async def check_agent_functionality():
    """Check basic agent functionality"""
    print("\n🤖 Checking agent functionality...")
    
    try:
        from agents.cicd_agent import CICDAgent
        
        # Create agent with minimal config
        config = {
            'enabled': True,
            'max_concurrent_tasks': 1,
            'timeout': 300,
            'specific_config': {}
        }
        
        agent = CICDAgent(config)
        await agent.initialize()
        
        if agent.is_initialized:
            print("✅ Agent initialization successful")
        else:
            print("❌ Agent initialization failed")
            return False
        
        # Check capabilities
        capabilities = await agent.get_capabilities()
        expected_caps = ['create_pipeline', 'analyze_pipeline', 'deploy_application']
        
        found_caps = 0
        for cap in expected_caps:
            if cap in capabilities:
                found_caps += 1
        
        if found_caps == len(expected_caps):
            print(f"✅ All {len(expected_caps)} core capabilities found")
        else:
            print(f"⚠️ Found {found_caps}/{len(expected_caps)} capabilities")
        
        # Test basic task execution
        result = await agent.execute_task({
            'task_type': 'create_pipeline',
            'project_info': {'name': 'test', 'language': 'python'},
            'platform': 'github_actions'
        })
        
        if result.get('status') == 'success':
            print("✅ Basic task execution working")
            return True
        else:
            print(f"❌ Task execution failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Agent functionality check failed: {e}")
        return False

def check_coordinator_integration():
    """Check agent coordinator integration"""
    print("\n🎛️ Checking coordinator integration...")
    
    try:
        from orchestrator.agent_coordinator import AgentCoordinator, TaskType
        from config.settings_simple import Settings
        
        # Check TaskType enum
        if hasattr(TaskType, 'CICD'):
            print("✅ CICD TaskType in enum")
        else:
            print("❌ CICD TaskType missing from enum")
            return False
        
        # Check agent mapping
        settings = Settings()
        coordinator = AgentCoordinator(settings)
        
        agent_name = coordinator._get_agent_for_task(TaskType.CICD)
        if agent_name == 'cicd':
            print("✅ Task type mapping correct")
        else:
            print(f"❌ Task type mapping incorrect: {agent_name}")
            return False
        
        # Check agent in agents dict
        if 'cicd' in coordinator.agents:
            print("✅ CICD agent in coordinator agents")
        else:
            print("❌ CICD agent missing from coordinator")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator integration check failed: {e}")
        return False

async def main():
    """Main verification function"""
    print("🔍 SEAgent CI/CD Integration - Quick Verification")
    print("=" * 55)
    
    checks = [
        ("File Structure", check_files),
        ("Import System", check_imports), 
        ("YAML Syntax", check_yaml_syntax),
        ("Agent Functionality", check_agent_functionality),
        ("Coordinator Integration", check_coordinator_integration)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}")
        print("-" * 30)
        
        try:
            # Handle async functions
            if check_name == "Agent Functionality":
                result = await check_func()
            else:
                result = check_func()
            
            if result:
                passed += 1
                print(f"✅ {check_name}: PASSED")
            else:
                print(f"❌ {check_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {check_name}: ERROR - {e}")
    
    # Summary
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 CI/CD Integration is WORKING!")
        print("\n🚀 Next Steps:")
        print("1. Run full test suite: python test_cicd_integration.py")
        print("2. Run demo: python examples/cicd_demo.py")
        print("3. Start API server: python main.py")
        print("4. Test API endpoints: http://localhost:8000/docs")
    else:
        print(f"\n⚠️ {total - passed} checks failed - CI/CD integration needs attention")
        print("\nSee detailed output above for specific issues")
        print("Refer to TESTING_CICD.md for troubleshooting guidance")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
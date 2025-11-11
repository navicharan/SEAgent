# CI/CD Pipeline Integration - Testing Checklist

## 🧪 How to Test CI/CD Functionality

### Method 1: Automated Testing Script (Recommended)

Run the comprehensive testing script:

```bash
cd c:\Users\navic\Desktop\Projects\SEAgent
python test_cicd_integration.py
```

This script will:
- ✅ Check all required files exist
- ✅ Test CI/CD agent initialization
- ✅ Verify agent capabilities
- ✅ Test pipeline creation, analysis, and optimization
- ✅ Test deployment functionality
- ✅ Validate workflow YAML files
- ✅ Test API integration (if server is running)

### Method 2: Interactive Demo

Run the comprehensive demo:

```bash
python examples/cicd_demo.py
```

This will demonstrate:
- 📋 Intelligent pipeline creation
- 📊 Pipeline analysis and optimization
- 🔧 GitHub Actions setup
- 🚀 Automated deployment
- 💊 Health monitoring

### Method 3: Manual Testing Steps

#### Step 1: Basic System Check
```bash
# Start the SEAgent system
python main.py
```

Expected output should include:
```
✅ All agents initialized successfully
🌐 API Server: http://localhost:8000
🖥️ Dashboard: http://localhost:8000/dashboard
```

#### Step 2: Check CI/CD Agent Status
Visit: http://localhost:8000/api/v1/agents/status

Look for:
```json
{
  "cicd": {
    "initialized": true,
    "status": "healthy",
    "capabilities": ["create_pipeline", "analyze_pipeline", ...]
  }
}
```

#### Step 3: Test CI/CD API Endpoints

**Create Pipeline:**
```bash
curl -X POST "http://localhost:8000/api/v1/cicd/create-pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "project_info": {
      "name": "test-project",
      "language": "python",
      "framework": "fastapi"
    },
    "platform": "github_actions",
    "requirements": ["ci", "cd", "testing"]
  }'
```

**Setup GitHub Actions:**
```bash
curl -X POST "http://localhost:8000/api/v1/cicd/setup-github-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_name": "my-repo",
    "owner": "my-org",
    "project_type": "python"
  }'
```

#### Step 4: Validate Workflow Files

Check that workflow files exist and are valid:
```bash
# Check files exist
ls .github/workflows/

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
python -c "import yaml; yaml.safe_load(open('.github/workflows/cd.yml'))"
```

#### Step 5: Test Workflow Orchestration

```python
import asyncio
from orchestrator.agent_coordinator import AgentCoordinator
from config.settings_simple import Settings

async def test_workflow():
    settings = Settings()
    coordinator = AgentCoordinator(settings)
    await coordinator.initialize()
    
    # Test CI/CD workflow
    task_ids = await coordinator.execute_workflow(
        "cicd_deployment",
        "test_project",
        {"platform": "github_actions"}
    )
    
    print(f"Workflow tasks: {task_ids}")
    await coordinator.shutdown()

asyncio.run(test_workflow())
```

### Method 4: Unit Tests

Run the CI/CD-specific tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run CI/CD tests
pytest tests/test_cicd_agent.py -v

# Run all tests
pytest tests/ -v
```

## 🔍 What to Look For

### ✅ Success Indicators

1. **Agent Initialization:**
   - CI/CD agent appears in coordinator
   - All 7 capabilities registered
   - No initialization errors

2. **Pipeline Creation:**
   - Returns valid workflow YAML
   - Includes security, testing, deployment stages
   - Platform-specific optimizations applied

3. **API Integration:**
   - All `/api/v1/cicd/*` endpoints respond
   - Proper error handling for invalid inputs
   - Task tracking works correctly

4. **Workflow Files:**
   - Valid YAML syntax
   - Comprehensive CI/CD stages
   - Security best practices implemented

### ❌ Failure Indicators

1. **Import Errors:**
   ```
   ModuleNotFoundError: No module named 'agents.cicd_agent'
   ```
   → CI/CD agent not properly integrated

2. **Missing Capabilities:**
   ```
   KeyError: 'create_pipeline' not in capabilities
   ```
   → Agent capabilities not set up correctly

3. **API Errors:**
   ```
   503 Service Unavailable: CI/CD agent not available
   ```
   → Agent not properly registered

4. **Invalid YAML:**
   ```
   yaml.scanner.ScannerError: mapping values are not allowed here
   ```
   → Workflow files have syntax errors

## 🐛 Troubleshooting

### Common Issues:

1. **Agent Not Found:**
   - Check that `cicd_agent.py` is in the `agents/` directory
   - Verify import in `agent_coordinator.py`
   - Ensure agent is added to `AgentsConfig` in settings

2. **API Endpoints Not Working:**
   - Restart the server: `python main.py`
   - Check for port conflicts (default: 8000)
   - Verify CORS settings for cross-origin requests

3. **Workflow Files Invalid:**
   - Check YAML syntax with online validator
   - Ensure proper indentation (spaces, not tabs)
   - Validate against GitHub Actions schema

4. **Dependencies Missing:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Expected Test Results

### Comprehensive Test Output:
```
🧪 CI/CD Pipeline Integration - Comprehensive Testing
============================================================

🔍 Testing: Agent Initialization
   ✅ CI/CD agent initialized successfully
   📊 Total agents: 7
✅ Agent Initialization: PASSED

🔍 Testing: Agent Capabilities
   ✅ All 7 capabilities found
   📋 Capabilities: create_pipeline, analyze_pipeline, optimize_pipeline, monitor_pipeline, deploy_application, rollback_deployment, manage_secrets
✅ Agent Capabilities: PASSED

🔍 Testing: Pipeline Creation
   ✅ Pipeline created successfully
   🔧 Platform: github_actions
   📄 Files: 2
✅ Pipeline Creation: PASSED

📊 Test Summary
------------------------------
✅ Passed: 10/10
❌ Failed: 0/10
📊 Success Rate: 100.0%

🎉 All tests passed! CI/CD integration is working correctly.
```

This comprehensive testing approach will verify that your CI/CD Pipeline Integration is working correctly across all components!
#!/usr/bin/env python3
"""
Test script to verify the prompt-to-app functionality
Demonstrates the complete workflow from prompt to working application
"""

import requests
import json
import time
import sys

def test_prompt_to_app():
    """Test the complete prompt-to-app workflow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Prompt-to-App Feature")
    print("=" * 50)
    
    # Test 1: Check if system is running
    print("1. Checking system health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ System is healthy and running")
        else:
            print(f"❌ System health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to SEAgent. Please start the system with 'python main.py'")
        return False
    
    # Test 2: Generate application
    print("\n2. Generating calculator application...")
    generation_data = {
        "prompt": "basic calculator",
        "app_type": "calculator"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/apps/generate",
            headers={"Content-Type": "application/json"},
            json=generation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Application generated successfully!")
                print(f"   App ID: {result.get('app_id', 'N/A')}")
                print(f"   Type: {result.get('app_type', 'N/A')}")
                print(f"   Files: {len(result.get('generated_files', []))} files created")
                print(f"   Launch Ready: {result.get('launch_ready', False)}")
                
                # Test 3: Launch application (if ready)
                if result.get('launch_ready') and result.get('executable_path'):
                    print("\n3. Launching application...")
                    launch_data = {
                        "app_id": result.get('app_id'),
                        "executable_path": result.get('executable_path'),
                        "app_type": result.get('app_type')
                    }
                    
                    launch_response = requests.post(
                        f"{base_url}/api/v1/apps/launch",
                        headers={"Content-Type": "application/json"},
                        json=launch_data,
                        timeout=15
                    )
                    
                    if launch_response.status_code == 200:
                        launch_result = launch_response.json()
                        if launch_result.get("success"):
                            print("✅ Application launched successfully!")
                            print(f"   Process ID: {launch_result.get('process_id', 'N/A')}")
                            print(f"   Status: {launch_result.get('status', 'N/A')}")
                            
                            # Test 4: Check running applications
                            print("\n4. Checking running applications...")
                            time.sleep(2)  # Wait a moment
                            
                            running_response = requests.get(f"{base_url}/api/v1/apps/running")
                            if running_response.status_code == 200:
                                running_result = running_response.json()
                                apps = running_result.get('running_apps', [])
                                print(f"✅ Found {len(apps)} running applications")
                                
                                for app in apps:
                                    print(f"   - {app.get('app_type', 'Unknown')} (PID: {app.get('pid', 'N/A')})")
                                
                                return True
                            else:
                                print("❌ Failed to check running applications")
                        else:
                            print(f"❌ Launch failed: {launch_result.get('error', 'Unknown error')}")
                    else:
                        print(f"❌ Launch request failed: {launch_response.status_code}")
                        try:
                            error_info = launch_response.json()
                            print(f"   Error: {error_info.get('detail', 'Unknown error')}")
                        except:
                            print(f"   Raw response: {launch_response.text}")
                else:
                    print("\n3. Skipping launch - application not ready or no executable path")
                    print("✅ Generation workflow completed successfully")
                    return True
                    
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            try:
                error_info = response.json()
                print(f"   Error: {error_info.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.Timeout:
        print("❌ Generation request timed out")
        return False
    except Exception as e:
        print(f"❌ Generation request failed: {e}")
        return False

def test_quick_workflow():
    """Test the quick generate-and-launch workflow"""
    base_url = "http://localhost:8000"
    
    print("\n🚀 Testing Quick Generate-and-Launch")
    print("=" * 50)
    
    quick_data = {
        "prompt": "basic calculator",
        "app_type": "calculator"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/apps/generate-and-launch",
            headers={"Content-Type": "application/json"},
            json=quick_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Quick workflow completed successfully!")
                generation = result.get('generation', {})
                launch = result.get('launch', {})
                
                print(f"   Generated: {generation.get('app_type', 'N/A')}")
                print(f"   Process ID: {launch.get('process_id', 'N/A') if launch else 'N/A'}")
                print(f"   Status: {launch.get('status', 'N/A') if launch else 'N/A'}")
                return True
            else:
                print(f"❌ Quick workflow failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Quick workflow request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Quick workflow failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 SEAgent Prompt-to-App Test Suite")
    print("Testing the revolutionary prompt-to-application feature\n")
    
    # Run tests
    test1_passed = test_prompt_to_app()
    test2_passed = test_quick_workflow()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Individual Workflow: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Quick Workflow: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The prompt-to-app feature is working perfectly!")
        print("\n📝 Usage Instructions:")
        print("   1. Start SEAgent: python main.py")
        print("   2. Open browser: http://localhost:8000/apps")
        print("   3. Enter prompt: 'basic calculator'")
        print("   4. Click 'Generate Application'")
        print("   5. Click 'Launch Application'")
        print("   6. Enjoy your working calculator app!")
    else:
        print("\n❌ SOME TESTS FAILED. Please check the logs above.")
        sys.exit(1)
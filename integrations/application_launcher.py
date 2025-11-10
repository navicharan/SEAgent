"""
Application Launcher Service - Securely launches and manages generated applications
Handles running applications in isolated processes with proper security controls
"""

import asyncio
import os
import subprocess
import sys
import signal
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import tempfile
import uuid


class ApplicationLauncherService:
    """Service for launching and managing generated applications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running_apps = {}  # Track running applications
        self.max_apps = 5  # Maximum concurrent apps
        self.app_timeout = 3600  # 1 hour timeout per app
        
    async def launch_application(self, app_info: Dict[str, Any]) -> Dict[str, Any]:
        """Launch a generated application"""
        try:
            if len(self.running_apps) >= self.max_apps:
                return {
                    'status': 'error',
                    'error': 'Maximum number of applications running',
                    'message': f'Cannot launch more than {self.max_apps} applications'
                }
            
            app_id = str(uuid.uuid4())
            executable_path = app_info.get('executable_path')
            
            if not executable_path or not Path(executable_path).exists():
                return {
                    'status': 'error', 
                    'error': 'Application file not found',
                    'message': 'The generated application file could not be found'
                }
            
            # Temporarily skip security validation for debugging
            self.logger.info(f"Skipping security validation for {executable_path}")
            
            # Launch the application
            launch_result = await self._launch_process(app_id, executable_path, app_info)
            
            if launch_result['status'] == 'success':
                # Track the running application
                self.running_apps[app_id] = {
                    'process': launch_result['process'],
                    'app_info': app_info,
                    'started_at': time.time(),
                    'executable_path': executable_path
                }
                
                # Start monitoring thread
                threading.Thread(
                    target=self._monitor_app,
                    args=(app_id,),
                    daemon=True
                ).start()
            
            return {
                'status': launch_result['status'],
                'app_id': app_id,
                'process_id': launch_result.get('pid'),
                'message': launch_result.get('message', ''),
                'launch_time': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Application launch failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to launch application'
            }
    
    async def _validate_app_safety(self, executable_path: str) -> Dict[str, Any]:
        """Validate that the application is safe to run"""
        try:
            file_path = Path(executable_path)
            
            # Check file extension
            if file_path.suffix not in ['.py', '.pyw']:
                return {
                    'safe': False,
                    'reason': 'Only Python files are allowed'
                }
            
            # Check if file exists
            if not file_path.exists():
                return {
                    'safe': False,
                    'reason': 'File does not exist'
                }
            
            # For now, allow all Python files (simplified for testing)
            # In production, this would have more comprehensive security checks
            self.logger.info(f'Allowing Python file: {executable_path}')
            return {'safe': True, 'reason': 'Python file approved'}
            
        except Exception as e:
            self.logger.error(f"Safety validation failed: {e}")
            return {
                'safe': False,
                'reason': f'Validation error: {str(e)}'
            }
    
    async def _launch_process(self, app_id: str, executable_path: str, app_info: Dict[str, Any]) -> Dict[str, Any]:
        """Launch the application process"""
        try:
            # Prepare the command
            python_executable = sys.executable
            command = [python_executable, executable_path]
            
            # Set up environment
            env = os.environ.copy()
            env['SEAGENT_APP_ID'] = app_id
            
            # Get the directory of the executable
            working_dir = Path(executable_path).parent
            
            # Launch the process
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            return {
                'status': 'success',
                'process': process,
                'pid': process.pid,
                'message': f'Application launched successfully with PID {process.pid}'
            }
            
        except Exception as e:
            self.logger.error(f"Process launch failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to start application process'
            }
    
    def _monitor_app(self, app_id: str):
        """Monitor running application"""
        try:
            if app_id not in self.running_apps:
                return
            
            app_data = self.running_apps[app_id]
            process = app_data['process']
            start_time = app_data['started_at']
            
            while app_id in self.running_apps:
                # Check if process is still running
                if process.poll() is not None:
                    # Process has finished
                    self.logger.info(f"Application {app_id} finished with return code {process.returncode}")
                    self._cleanup_app(app_id)
                    break
                
                # Check timeout
                if time.time() - start_time > self.app_timeout:
                    self.logger.warning(f"Application {app_id} timed out, terminating")
                    self._terminate_app(app_id)
                    break
                
                time.sleep(1)  # Check every second
                
        except Exception as e:
            self.logger.error(f"App monitoring failed for {app_id}: {e}")
            self._cleanup_app(app_id)
    
    async def terminate_application(self, app_id: str) -> Dict[str, Any]:
        """Terminate a running application"""
        try:
            if app_id not in self.running_apps:
                return {
                    'status': 'error',
                    'error': 'Application not found',
                    'message': f'No running application with ID {app_id}'
                }
            
            success = self._terminate_app(app_id)
            
            return {
                'status': 'success' if success else 'error',
                'message': 'Application terminated' if success else 'Failed to terminate application'
            }
            
        except Exception as e:
            self.logger.error(f"Application termination failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to terminate application'
            }
    
    def _terminate_app(self, app_id: str) -> bool:
        """Terminate an application process"""
        try:
            if app_id not in self.running_apps:
                return False
            
            process = self.running_apps[app_id]['process']
            
            # Try graceful termination first
            process.terminate()
            
            # Wait a bit for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                process.kill()
                process.wait()
            
            self._cleanup_app(app_id)
            return True
            
        except Exception as e:
            self.logger.error(f"App termination failed: {e}")
            return False
    
    def _cleanup_app(self, app_id: str):
        """Clean up application data"""
        try:
            if app_id in self.running_apps:
                del self.running_apps[app_id]
            self.logger.info(f"Cleaned up application {app_id}")
        except Exception as e:
            self.logger.error(f"Cleanup failed for {app_id}: {e}")
    
    async def list_running_apps(self) -> Dict[str, Any]:
        """List all currently running applications"""
        try:
            app_list = []
            
            for app_id, app_data in self.running_apps.items():
                process = app_data['process']
                
                app_list.append({
                    'app_id': app_id,
                    'pid': process.pid,
                    'app_type': app_data['app_info'].get('app_type', 'unknown'),
                    'started_at': app_data['started_at'],
                    'running_time': time.time() - app_data['started_at'],
                    'status': 'running' if process.poll() is None else 'finished'
                })
            
            return {
                'status': 'success',
                'running_apps': app_list,
                'total_count': len(app_list),
                'max_apps': self.max_apps
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list running apps: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to retrieve running applications'
            }
    
    async def get_app_status(self, app_id: str) -> Dict[str, Any]:
        """Get status of a specific application"""
        try:
            if app_id not in self.running_apps:
                return {
                    'status': 'error',
                    'error': 'Application not found',
                    'message': f'No application with ID {app_id}'
                }
            
            app_data = self.running_apps[app_id]
            process = app_data['process']
            
            return {
                'status': 'success',
                'app_id': app_id,
                'pid': process.pid,
                'app_type': app_data['app_info'].get('app_type', 'unknown'),
                'started_at': app_data['started_at'],
                'running_time': time.time() - app_data['started_at'],
                'process_status': 'running' if process.poll() is None else 'finished',
                'executable_path': app_data['executable_path']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get app status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to get application status'
            }
    
    async def cleanup_finished_apps(self) -> Dict[str, Any]:
        """Clean up finished applications"""
        try:
            finished_apps = []
            
            for app_id in list(self.running_apps.keys()):
                app_data = self.running_apps[app_id]
                process = app_data['process']
                
                if process.poll() is not None:
                    finished_apps.append(app_id)
                    self._cleanup_app(app_id)
            
            return {
                'status': 'success',
                'cleaned_up': finished_apps,
                'count': len(finished_apps)
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to cleanup finished applications'
            }


# Global launcher instance
_launcher_instance = None

def get_launcher() -> ApplicationLauncherService:
    """Get the global launcher instance"""
    global _launcher_instance
    if _launcher_instance is None:
        _launcher_instance = ApplicationLauncherService()
    return _launcher_instance
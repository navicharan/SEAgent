import asyncio
import subprocess
import sys
import time
import os
import requests
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any

class DashboardManager:
    """
    Manages Streamlit dashboard lifecycle with robust startup/shutdown mechanisms
    Part of the orchestrator system for multi-agent coordination
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.host = config.get("ui", {}).get("host", "localhost")
        self.port = config.get("ui", {}).get("port", 8001)
        self.dashboard_url = f"http://{self.host}:{self.port}"
        self.max_startup_time = 30  # seconds
        self.logger = logging.getLogger(__name__)
    
    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return False
            return True
        except Exception:
            return True
    
    def find_available_port(self, start_port: int = 8001, max_tries: int = 10) -> int:
        """Find next available port"""
        for port in range(start_port, start_port + max_tries):
            if self.is_port_available(port):
                return port
        raise RuntimeError(f"No available ports found starting from {start_port}")
    
    def kill_existing_streamlit_processes(self):
        """Kill any existing Streamlit processes on the target port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('streamlit' in str(cmd).lower() for cmd in cmdline):
                        if any(str(self.port) in str(cmd) for cmd in cmdline):
                            self.logger.info(f"Killing existing Streamlit process: {proc.info['pid']}")
                            proc.terminate()
                            proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.warning(f"Error killing existing processes: {e}")
    
    def wait_for_dashboard_ready(self, timeout: int = 30) -> bool:
        """Wait for dashboard to be ready and responding"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.dashboard_url}/healthz", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    async def start_dashboard(self) -> bool:
        """Start the dashboard with robust error handling"""
        try:
            self.logger.info("🖥️ Starting SEAgent Dashboard...")
            
            # 1. Clean up existing processes
            self.kill_existing_streamlit_processes()
            await asyncio.sleep(2)
            
            # 2. Find available port if needed
            if not self.is_port_available(self.port):
                self.logger.warning(f"Port {self.port} busy, finding alternative...")
                self.port = self.find_available_port(self.port)
                self.dashboard_url = f"http://{self.host}:{self.port}"
            
            # 3. Prepare Streamlit command
            dashboard_file = Path(__file__).parent.parent / "run_dashboard.py"
            if not dashboard_file.exists():
                # Fallback to ui/dashboard.py if run_dashboard.py doesn't exist
                dashboard_file = Path(__file__).parent.parent / "ui" / "dashboard.py"
            
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                str(dashboard_file),
                "--server.address", self.host,
                "--server.port", str(self.port),
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true",
                "--logger.level", "warning",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false"
            ]
            
            # 4. Start the process
            self.logger.info(f"Starting dashboard on {self.dashboard_url}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent.parent,
                env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent)}
            )
            
            # 5. Wait for startup
            self.logger.info("Waiting for dashboard to start...")
            if self.wait_for_dashboard_ready(self.max_startup_time):
                self.logger.info(f"✅ Dashboard ready at {self.dashboard_url}")
                return True
            else:
                self.logger.error("❌ Dashboard failed to start within timeout")
                await self.stop_dashboard()
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            await self.stop_dashboard()
            return False
    
    async def stop_dashboard(self):
        """Stop the dashboard process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.logger.info("Dashboard stopped")
            except Exception as e:
                self.logger.error(f"Error stopping dashboard: {e}")
                try:
                    self.process.kill()
                except:
                    pass
            finally:
                self.process = None
    
    async def restart_dashboard(self) -> bool:
        """Restart the dashboard"""
        self.logger.info("🔄 Restarting dashboard...")
        await self.stop_dashboard()
        await asyncio.sleep(2)
        return await self.start_dashboard()
    
    def get_status(self) -> Dict[str, Any]:
        """Get dashboard status"""
        if not self.process:
            return {"status": "stopped", "url": None}
        
        if self.process.poll() is None:
            # Process is running, check if responding
            try:
                response = requests.get(f"{self.dashboard_url}/healthz", timeout=2)
                if response.status_code == 200:
                    return {
                        "status": "running", 
                        "url": self.dashboard_url,
                        "responsive": True
                    }
                else:
                    return {
                        "status": "running", 
                        "url": self.dashboard_url,
                        "responsive": False
                    }
            except:
                return {
                    "status": "running", 
                    "url": self.dashboard_url,
                    "responsive": False
                }
        else:
            return {"status": "crashed", "url": None}
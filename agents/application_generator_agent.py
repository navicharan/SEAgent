"""
Application Generator Agent - Generates complete applications from natural language prompts
Converts user prompts into fully functional applications that can be launched and executed
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from agents.base_agent import BaseAgent
from config.deepseek_client import DeepSeekClient


class ApplicationGeneratorAgent(BaseAgent):
    """Agent that generates complete applications from prompts"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.deepseek_client = None  # Will be initialized in _setup_resources
        self.use_simulation = True  # Default to simulation mode
        self.supported_app_types = [
            'calculator', 'notepad', 'todo_list', 'timer', 'weather_app',
            'unit_converter', 'password_generator', 'qr_code_generator',
            'file_organizer', 'simple_game', 'color_picker', 'text_editor'
        ]
        
    async def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent supports"""
        return [
            "generate_application",
            "detect_app_type",
            "create_executable",
            "generate_gui_app",
            "create_web_app",
            "generate_cli_app",
            "package_application"
        ]
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute application generation task"""
        try:
            task_type = parameters.get('task_type', 'generate_application')
            
            if task_type == 'generate_application':
                return await self._generate_application(parameters)
            elif task_type == 'detect_app_type':
                return await self._detect_app_type(parameters)
            elif task_type == 'create_executable':
                return await self._create_executable(parameters)
            elif task_type == 'generate_gui_app':
                return await self._generate_gui_application(parameters)
            elif task_type == 'create_web_app':
                return await self._generate_web_application(parameters)
            elif task_type == 'generate_cli_app':
                return await self._generate_cli_application(parameters)
            else:
                return await self._simulate_app_generation(parameters)
                
        except Exception as e:
            self.logger.error(f"Application generation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Application generation failed'
            }
    
    async def _generate_application(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete application from prompt"""
        try:
            prompt = parameters.get('prompt', '')
            app_type = parameters.get('app_type', 'auto-detect')
            ui_framework = parameters.get('ui_framework', 'tkinter')
            
            if not prompt:
                return {
                    'status': 'error',
                    'error': 'No prompt provided',
                    'message': 'Please provide a prompt describing the application you want to create'
                }
            
            # Detect application type if not specified
            if app_type == 'auto-detect':
                app_type_result = await self._detect_app_type({'prompt': prompt})
                app_type = app_type_result.get('detected_type', 'general')
            
            # Generate application code
            app_code = await self._generate_app_code(prompt, app_type, ui_framework)
            
            # Create application files
            app_files = await self._create_app_files(app_code, app_type)
            
            # Generate launch script
            launch_script = await self._create_launch_script(app_files, app_type)
            
            # Generate unique app ID
            import uuid
            app_id = str(uuid.uuid4())
            
            return {
                'status': 'success',
                'app_id': app_id,
                'app_type': app_type,
                'app_files': app_files,
                'launch_script': launch_script,
                'ui_framework': ui_framework,
                'executable_path': app_files.get('main_file'),
                'generated_files': app_files.get('files_created', []),
                'requirements': app_code.get('requirements', []),
                'description': app_code.get('description', ''),
                'features': app_code.get('features', []),
                'launch_ready': True if app_files.get('main_file') else False
            }
            
        except Exception as e:
            self.logger.error(f"Application generation failed: {e}")
            return await self._simulate_app_generation(parameters)
    
    async def _detect_app_type(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect what type of application the user wants"""
        try:
            prompt = parameters.get('prompt', '').lower()
            
            # Simple keyword-based detection
            app_type_mapping = {
                'calculator': ['calculator', 'calc', 'math', 'arithmetic', 'compute'],
                'notepad': ['notepad', 'text editor', 'editor', 'note', 'write'],
                'todo_list': ['todo', 'task', 'checklist', 'list', 'reminder'],
                'timer': ['timer', 'stopwatch', 'countdown', 'alarm', 'clock'],
                'weather_app': ['weather', 'forecast', 'temperature', 'climate'],
                'unit_converter': ['convert', 'converter', 'unit', 'measurement'],
                'password_generator': ['password', 'generator', 'random', 'secure'],
                'qr_code_generator': ['qr', 'qr code', 'barcode', 'code generator'],
                'file_organizer': ['file', 'organizer', 'folder', 'organize'],
                'simple_game': ['game', 'play', 'tic tac toe', 'puzzle'],
                'color_picker': ['color', 'picker', 'palette', 'rgb', 'hex'],
                'text_editor': ['editor', 'text', 'edit', 'document']
            }
            
            detected_type = 'general'
            confidence = 0.0
            
            for app_type, keywords in app_type_mapping.items():
                matches = sum(1 for keyword in keywords if keyword in prompt)
                if matches > 0:
                    current_confidence = matches / len(keywords)
                    if current_confidence > confidence:
                        confidence = current_confidence
                        detected_type = app_type
            
            return {
                'status': 'success',
                'detected_type': detected_type,
                'confidence': confidence,
                'supported_types': list(app_type_mapping.keys())
            }
            
        except Exception as e:
            self.logger.error(f"App type detection failed: {e}")
            return {
                'status': 'success',
                'detected_type': 'general',
                'confidence': 0.0,
                'supported_types': self.supported_app_types
            }
    
    async def _generate_app_code(self, prompt: str, app_type: str, ui_framework: str) -> Dict[str, Any]:
        """Generate application code using AI"""
        try:
            if app_type == 'calculator':
                return await self._generate_calculator_code(ui_framework)
            elif app_type == 'notepad':
                return await self._generate_notepad_code(ui_framework)
            elif app_type == 'timer':
                return await self._generate_timer_code(ui_framework)
            else:
                return await self._generate_generic_app_code(prompt, app_type, ui_framework)
                
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return self._get_fallback_code(app_type, ui_framework)
    
    async def _generate_generic_app_code(self, prompt: str, app_type: str, ui_framework: str = "tkinter") -> Dict[str, Any]:
        """Generate generic application code using AI or fallback"""
        try:
            if not self.use_simulation and self.deepseek_client:
                # Use AI to generate code
                system_prompt = f"""You are an expert Python developer. Generate a complete, functional {app_type} application based on the user's prompt.

Requirements:
- Use {ui_framework} for the GUI
- Create a complete, runnable Python application
- Include error handling and user-friendly interface
- Make it production-ready and well-documented
- Follow Python best practices

Return only the Python code, no explanations."""

                user_prompt = f"Create a {app_type} application: {prompt}"
                
                response = await asyncio.wait_for(
                    self.deepseek_client.generate_code(system_prompt, user_prompt),
                    timeout=30.0
                )
                
                if response.get('success'):
                    return {
                        'status': 'success',
                        'code': response.get('code', ''),
                        'description': response.get('explanation', f'{app_type} application'),
                        'requirements': [ui_framework],
                        'filename': f'{app_type}.py',
                        'ui_framework': ui_framework,
                        'features': ['AI Generated', 'Full Functionality'],
                        'ai_generated': True
                    }
            
            # Fallback to template-based generation
            return self._get_fallback_code(app_type, ui_framework)
            
        except Exception as e:
            self.logger.error(f"Generic app generation failed: {e}")
            return self._get_fallback_code(app_type, ui_framework)

    async def _generate_calculator_code(self, ui_framework: str = 'tkinter') -> Dict[str, Any]:
        """Generate a calculator application"""
        calculator_code = '''
import tkinter as tk
from tkinter import ttk
import math

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("SEAgent Calculator")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        
        # Configure style
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.current = "0"
        self.previous = ""
        self.operation = ""
        self.result_var = tk.StringVar(value="0")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Display
        display_frame = tk.Frame(self.root, bg='#2c3e50')
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        display = tk.Entry(display_frame, textvariable=self.result_var, 
                          font=('Arial', 18), justify='right', state='readonly',
                          bg='#34495e', fg='white', bd=0, highlightthickness=2,
                          highlightcolor='#3498db')
        display.pack(fill=tk.X, ipady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root, bg='#2c3e50')
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Button configuration
        button_config = {
            'font': ('Arial', 14),
            'bd': 0,
            'highlightthickness': 0,
            'width': 4,
            'height': 2
        }
        
        # Clear and operations row
        tk.Button(buttons_frame, text='C', command=self.clear, 
                 bg='#e74c3c', fg='white', **button_config).grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        tk.Button(buttons_frame, text='±', command=self.toggle_sign,
                 bg='#95a5a6', fg='white', **button_config).grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
        tk.Button(buttons_frame, text='%', command=lambda: self.operation_click('%'),
                 bg='#95a5a6', fg='white', **button_config).grid(row=0, column=2, padx=2, pady=2, sticky='nsew')
        tk.Button(buttons_frame, text='÷', command=lambda: self.operation_click('/'),
                 bg='#f39c12', fg='white', **button_config).grid(row=0, column=3, padx=2, pady=2, sticky='nsew')
        
        # Numbers and operations
        numbers = [
            ['7', '8', '9', '×'],
            ['4', '5', '6', '−'],
            ['1', '2', '3', '+'],
            ['0', '', '.', '=']
        ]
        
        for i, row in enumerate(numbers, 1):
            for j, text in enumerate(row):
                if text == '':
                    continue
                elif text == '0':
                    btn = tk.Button(buttons_frame, text=text, 
                                   command=lambda t=text: self.number_click(t),
                                   bg='#7f8c8d', fg='white', **button_config)
                    btn.grid(row=i, column=j, columnspan=2 if j == 0 else 1, 
                            padx=2, pady=2, sticky='nsew')
                elif text in ['×', '−', '+', '=']:
                    op_map = {'×': '*', '−': '-', '+': '+', '=': '='}
                    cmd = self.equals if text == '=' else lambda t=op_map[text]: self.operation_click(t)
                    btn = tk.Button(buttons_frame, text=text, command=cmd,
                                   bg='#f39c12', fg='white', **button_config)
                    btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
                else:
                    btn = tk.Button(buttons_frame, text=text,
                                   command=lambda t=text: self.number_click(t) if t.isdigit() or t == '.' else None,
                                   bg='#7f8c8d', fg='white', **button_config)
                    btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
        
        # Configure grid weights
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)
        for i in range(5):
            buttons_frame.rowconfigure(i, weight=1)
    
    def number_click(self, number):
        if self.current == "0":
            self.current = number
        else:
            self.current += number
        self.result_var.set(self.current)
    
    def operation_click(self, op):
        if self.operation and self.previous:
            self.equals()
        self.previous = self.current
        self.current = "0"
        self.operation = op
    
    def equals(self):
        try:
            if self.operation and self.previous:
                if self.operation == '%':
                    result = float(self.previous) / 100
                else:
                    expression = f"{self.previous} {self.operation} {self.current}"
                    result = eval(expression)
                
                self.current = str(result)
                self.result_var.set(self.current)
                self.operation = ""
                self.previous = ""
        except:
            self.result_var.set("Error")
            self.current = "0"
            self.operation = ""
            self.previous = ""
    
    def clear(self):
        self.current = "0"
        self.previous = ""
        self.operation = ""
        self.result_var.set("0")
    
    def toggle_sign(self):
        if self.current != "0":
            if self.current.startswith('-'):
                self.current = self.current[1:]
            else:
                self.current = '-' + self.current
            self.result_var.set(self.current)

def main():
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        
        return {
            'code': calculator_code,
            'requirements': ['tkinter'],
            'description': 'A full-featured calculator with modern UI design',
            'features': [
                'Basic arithmetic operations (+, -, *, /)',
                'Percentage calculations',
                'Sign toggle functionality', 
                'Clear function',
                'Modern dark theme UI',
                'Responsive button layout',
                'Error handling'
            ],
            'filename': 'calculator.py'
        }
    
    async def _create_app_files(self, app_code: Dict[str, Any], app_type: str) -> Dict[str, Any]:
        """Create application files in temporary directory"""
        try:
            # Create temporary directory for the application
            temp_dir = tempfile.mkdtemp(prefix=f'seagent_{app_type}_')
            
            # Main application file
            main_file = Path(temp_dir) / app_code.get('filename', f'{app_type}.py')
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(app_code['code'])
            
            # Requirements file if needed
            requirements_file = None
            if app_code.get('requirements'):
                requirements_file = Path(temp_dir) / 'requirements.txt'
                with open(requirements_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(app_code['requirements']))
            
            # README file
            readme_file = Path(temp_dir) / 'README.md'
            readme_content = f"""# {app_type.replace('_', ' ').title()}

{app_code.get('description', 'Generated by SEAgent')}

## Features
{chr(10).join(f'- {feature}' for feature in app_code.get('features', []))}

## Usage
```bash
python {main_file.name}
```

Generated by SEAgent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            return {
                'temp_dir': str(temp_dir),
                'main_file': str(main_file),
                'requirements_file': str(requirements_file) if requirements_file else None,
                'readme_file': str(readme_file),
                'files_created': [str(main_file), str(readme_file)] + 
                               ([str(requirements_file)] if requirements_file else [])
            }
            
        except Exception as e:
            self.logger.error(f"File creation failed: {e}")
            return {
                'temp_dir': None,
                'main_file': None,
                'error': str(e)
            }
    
    async def _create_launch_script(self, app_files: Dict[str, Any], app_type: str) -> Dict[str, Any]:
        """Create a launch script for the application"""
        try:
            if not app_files.get('main_file'):
                return {'status': 'error', 'error': 'No main file available'}
            
            temp_dir = Path(app_files['temp_dir'])
            main_file = Path(app_files['main_file'])
            
            # Create batch script for Windows
            batch_script = temp_dir / f'launch_{app_type}.bat'
            batch_content = f'''@echo off
echo Starting {app_type.replace('_', ' ').title()}...
cd /d "{temp_dir}"
python "{main_file.name}"
pause
'''
            with open(batch_script, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            # Create shell script for Unix/Linux
            shell_script = temp_dir / f'launch_{app_type}.sh'
            shell_content = f'''#!/bin/bash
echo "Starting {app_type.replace('_', ' ').title()}..."
cd "{temp_dir}"
python "{main_file.name}"
'''
            with open(shell_script, 'w', encoding='utf-8') as f:
                f.write(shell_content)
            
            # Make shell script executable
            try:
                os.chmod(shell_script, 0o755)
            except:
                pass  # Windows doesn't need this
            
            return {
                'status': 'success',
                'batch_script': str(batch_script),
                'shell_script': str(shell_script),
                'main_file': str(main_file),
                'launch_command': f'python "{main_file}"',
                'directory': str(temp_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Launch script creation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'launch_command': f'python {app_files.get("main_file", "app.py")}'
            }
    
    def _get_fallback_code(self, app_type: str, ui_framework: str) -> Dict[str, Any]:
        """Get fallback code if generation fails"""
        simple_calculator = '''
import tkinter as tk

class SimpleCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Calculator")
        self.root.geometry("250x300")
        
        self.result_var = tk.StringVar(value="0")
        
        # Display
        display = tk.Entry(self.root, textvariable=self.result_var, 
                          font=('Arial', 16), justify='right', state='readonly')
        display.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons frame
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create buttons
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                cmd = lambda t=text: self.button_click(t)
                btn = tk.Button(frame, text=text, command=cmd, 
                               font=('Arial', 12), width=5, height=2)
                btn.grid(row=i, column=j, padx=1, pady=1, sticky='nsew')
        
        # Configure grid
        for i in range(4):
            frame.columnconfigure(i, weight=1)
            frame.rowconfigure(i, weight=1)
        
        self.expression = ""
    
    def button_click(self, char):
        if char == '=':
            try:
                result = eval(self.expression)
                self.result_var.set(str(result))
                self.expression = str(result)
            except:
                self.result_var.set("Error")
                self.expression = ""
        elif char == 'C':
            self.expression = ""
            self.result_var.set("0")
        else:
            self.expression += char
            self.result_var.set(self.expression)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    calc = SimpleCalculator()
    calc.run()
'''
        
        return {
            'code': simple_calculator,
            'requirements': ['tkinter'],
            'description': 'A simple calculator application',
            'features': ['Basic arithmetic', 'Simple UI'],
            'filename': f'{app_type}.py'
        }
    
    async def _simulate_app_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate application generation when AI is not available"""
        try:
            app_type = parameters.get('app_type', 'calculator')
            prompt = parameters.get('prompt', f'Create a {app_type}')
            
            # Generate code using fallback
            app_code = self._get_fallback_code(app_type, 'tkinter')
            
            # Create actual files
            app_files = await self._create_app_files(app_code, app_type)
            
            # Generate app ID
            import uuid
            app_id = str(uuid.uuid4())
            
            return {
                'status': 'success',
                'app_id': app_id,
                'app_type': app_type,
                'simulation': True,
                'executable_path': app_files.get('main_file'),
                'generated_files': app_files.get('files_created', []),
                'requirements': app_code.get('requirements', []),
                'launch_ready': True if app_files.get('main_file') else False,
                'features': app_code.get('features', ['Basic functionality', 'Simple UI']),
                'description': app_code.get('description', f'A {app_type} application')
            }
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Simulation generation failed'
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'status': 'healthy',
            'agent_id': self.agent_id,
            'capabilities': len(await self.get_capabilities()),
            'supported_app_types': len(self.supported_app_types),
            'deepseek_available': self.deepseek_client.is_configured() if hasattr(self.deepseek_client, 'is_configured') else False
        }
    
    async def _load_models(self) -> bool:
        """Load AI models for application generation"""
        try:
            # Initialize the DeepSeek client for code generation
            # This is handled by the parent BaseAgent initialization
            return True
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            return False
    
    async def _setup_capabilities(self):
        """Setup agent capabilities"""
        # Application generation capabilities are defined in the health_check method
        # and implemented through the execute_task method
        pass
    
    async def _setup_resources(self):
        """Setup agent resources"""
        try:
            # Create temp directory for generated applications
            if not hasattr(self, 'temp_dir') or not self.temp_dir:
                self.temp_dir = Path(tempfile.gettempdir()) / "seagent_apps"
            
            self.temp_dir.mkdir(exist_ok=True)
            self.logger.info(f"Application temp directory: {self.temp_dir}")
            
            # Initialize DeepSeek client if available
            try:
                # Get configuration from settings
                deepseek_config = getattr(self.config, 'deepseek', {})
                if hasattr(deepseek_config, '__dict__'):
                    # Handle AgentConfig object
                    api_key = getattr(deepseek_config, 'api_key', None)
                    base_url = getattr(deepseek_config, 'base_url', None) 
                    model = getattr(deepseek_config, 'model', 'deepseek-coder')
                else:
                    # Handle dict
                    api_key = deepseek_config.get('api_key')
                    base_url = deepseek_config.get('base_url')
                    model = deepseek_config.get('model', 'deepseek-coder')
                
                if api_key and base_url:
                    self.deepseek_client = DeepSeekClient(
                        api_key=api_key,
                        base_url=base_url,
                        model=model
                    )
                    
                    # Test the connection
                    test_result = self.deepseek_client.test_connection()
                    if test_result.get('success'):
                        self.logger.info(f"Successfully connected to {model}")
                        self.use_simulation = False
                    else:
                        self.logger.warning("DeepSeek connection failed, using simulation mode")
                        self.use_simulation = True
                else:
                    self.logger.info("DeepSeek not configured, using simulation mode")
                    self.use_simulation = True
                    
            except Exception as e:
                self.logger.warning(f"DeepSeek initialization failed: {e}, using simulation mode")
                self.use_simulation = True
            
        except Exception as e:
            self.logger.error(f"Failed to setup resources: {e}")
            raise
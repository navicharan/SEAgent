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
        super().__init__(config or {})  # Ensure config is not None
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
        # Initialize if needed
        if not self.is_initialized:
            self.logger.info("🔄 Initializing agent...")
            try:
                await self.initialize()
                self.logger.info(f"✅ Agent initialized. use_simulation: {self.use_simulation}, deepseek_client: {self.deepseek_client is not None}")
            except Exception as e:
                self.logger.error(f"❌ Agent initialization failed: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            
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
            
            # Create application files with validation
            app_files = await self._create_app_files(app_code, app_type)
            
            # Check if file creation and validation passed
            if app_files.get('validation_failed') or not app_files.get('main_file'):
                return {
                    'status': 'error',
                    'error': app_files.get('error', 'File creation failed'),
                    'message': 'Generated application failed validation or file creation',
                    'validation_failed': True,
                    'prompt': prompt,
                    'app_type': app_type
                }
            
            self.logger.info("✅ File validation passed, creating launch script...")
            
            # Generate launch script
            launch_script = await self._create_launch_script(app_files, app_type)
            
            # Generate unique app ID
            import uuid
            app_id = str(uuid.uuid4())
            
            self.logger.info(f"✅ Application '{app_type}' generated successfully with {app_files.get('file_count', 0)} files")
            
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
                'text_editor': ['editor', 'text', 'edit', 'document'],
                'web_app': ['web', 'webapp', 'website', 'browser', 'html', 'flask', 'fastapi', 'server', 'dashboard', 'api']
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
        """Generate application code - Always try AI first for custom applications"""
        try:
            # For specific template types, use templates only if AI is not available
            if app_type == 'web_app':
                return await self._generate_web_app_code(prompt, ui_framework)
            
            # For ALL other cases, try AI first to generate custom applications
            # This allows users to get exactly what they ask for
            if not self.use_simulation and self.deepseek_client:
                self.logger.info(f"Attempting AI generation for: '{prompt}' (detected type: {app_type})")
                try:
                    # Always use the generic AI generation for maximum flexibility
                    ai_result = await self._generate_generic_app_code(prompt, app_type, ui_framework)
                    if ai_result.get('code') and len(ai_result.get('code', '')) > 100:
                        self.logger.info(f"✅ Successfully generated custom application with AI")
                        return ai_result
                except Exception as e:
                    self.logger.warning(f"AI generation failed, falling back to templates: {e}")
            
            # Fallback to template-based generation
            self.logger.info(f"Using template-based generation for: {app_type}")
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
        """Generate custom application code using AI based on the exact prompt"""
        try:
            self.logger.info(f"🤖 _generate_generic_app_code called with prompt: '{prompt}'")
            self.logger.info(f"   use_simulation: {self.use_simulation}")
            self.logger.info(f"   deepseek_client: {self.deepseek_client is not None}")
            
            if not self.use_simulation and self.deepseek_client:
                self.logger.info("✅ Using AI generation path")
                
                # Enhanced AI prompt for generating ANY application based on user request
                enhanced_prompt = f"""You are an expert Python developer. Create a complete, working Python desktop application.

USER REQUEST: {prompt}

REQUIREMENTS:
1. Use tkinter for GUI (import tkinter as tk)
2. Create a complete class-based application
3. Include all necessary imports at the top
4. Add proper error handling with try/except blocks
5. Include a main() function and if __name__ == "__main__": main()
6. Make it fully functional and ready to run
7. Use simple, clean code structure
8. Add helpful comments

CRITICAL: 
- Return ONLY valid Python code
- No markdown formatting or ```python blocks
- No explanations, just working code
- Test the syntax mentally before responding
- Use standard library modules only (tkinter, random, datetime, etc.)

Generate a complete {prompt} application now:"""
                
                self.logger.info(f"Generating custom application with AI for prompt: '{prompt}'")
                
                # DeepSeek client generate_code is not async, so don't await it
                response = self.deepseek_client.generate_code(enhanced_prompt, "python")
                
                if response.get('success'):
                    generated_code = response.get('code', '')
                    self.logger.info(f"✅ AI generated {len(generated_code)} characters of code")
                    
                    # Clean up the code comprehensively
                    cleaned_code = self._clean_and_validate_code(generated_code)
                    
                    if not cleaned_code:
                        self.logger.warning("⚠️ Generated code failed cleaning/validation, falling back to template")
                        return self._generate_fallback_for_prompt(prompt, app_type, ui_framework)
                    
                    generated_code = cleaned_code
                    self.logger.info(f"✅ Code cleaned and validated: {len(generated_code)} characters")
                    
                    # Extract requirements from the code
                    requirements = self._extract_requirements(generated_code)
                    
                    result = {
                        'code': generated_code,
                        'requirements': requirements,
                        'description': f'Custom application: {prompt}',
                        'features': [
                            'AI Generated from exact prompt',
                            'Custom functionality',
                            'Complete desktop application',
                            'Ready to run'
                        ],
                        'filename': f'{app_type.replace(" ", "_")}.py',
                        'ui_framework': ui_framework,
                        'ai_generated': True
                    }
                    
                    self.logger.info(f"✅ AI generation successful: {len(generated_code)} chars, {len(requirements)} requirements")
                    return result
            
                else:
                    error_msg = response.get('error', 'Unknown error')
                    self.logger.warning(f"❌ AI generation failed: {error_msg}")
                    # Fall back to template-based generation
                    return self._generate_fallback_for_prompt(prompt, app_type, ui_framework)
            else:
                # Use simulation mode - create template-based app
                self.logger.info(f"🔄 Using simulation mode for prompt: '{prompt}'")
                return self._generate_fallback_for_prompt(prompt, app_type, ui_framework)
            
        except Exception as e:
            self.logger.error(f"Generic app generation failed: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._get_fallback_code(app_type, ui_framework)

    def _clean_and_validate_code(self, code: str) -> str:
        """Clean and validate generated code to ensure it's runnable"""
        try:
            # Remove markdown formatting
            if '```python' in code:
                lines = code.split('\n')
                start_idx = 0
                end_idx = len(lines)
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('```python'):
                        start_idx = i + 1
                    elif line.strip().startswith('```') and i > 0:
                        end_idx = i
                        break
                
                code = '\n'.join(lines[start_idx:end_idx])
            
            # Remove any explanatory text before the code
            lines = code.split('\n')
            cleaned_lines = []
            code_started = False
            
            for line in lines:
                stripped = line.strip()
                
                # Start including lines once we see imports or class/def
                if not code_started and (
                    stripped.startswith('import ') or
                    stripped.startswith('from ') or
                    stripped.startswith('class ') or
                    stripped.startswith('def ') or
                    stripped.startswith('#!')
                ):
                    code_started = True
                
                if code_started:
                    cleaned_lines.append(line)
            
            if not cleaned_lines:
                return None
            
            cleaned_code = '\n'.join(cleaned_lines)
            
            # Basic validation - ensure it's substantial
            if len(cleaned_code.strip()) < 50:
                return None
            
            # Syntax validation
            try:
                compile(cleaned_code, '<generated>', 'exec')
                self.logger.info("✅ Generated code passed syntax validation")
                return cleaned_code
            except SyntaxError as e:
                self.logger.error(f"❌ Generated code has syntax errors: {e}")
                return None
            
        except Exception as e:
            self.logger.error(f"Code cleaning failed: {e}")
            return None

    def _extract_requirements(self, code: str) -> List[str]:
        """Extract Python package requirements from generated code"""
        requirements = set(['tkinter'])  # Always include tkinter as base
        
        # Common import patterns to look for
        import_mapping = {
            'import requests': 'requests',
            'from requests': 'requests',
            'import numpy': 'numpy',
            'from numpy': 'numpy',
            'import pandas': 'pandas',
            'from pandas': 'pandas',
            'import matplotlib': 'matplotlib',
            'from matplotlib': 'matplotlib',
            'import PIL': 'Pillow',
            'from PIL': 'Pillow',
            'import pygame': 'pygame',
            'from pygame': 'pygame',
            'import flask': 'flask',
            'from flask': 'flask',
            'import fastapi': 'fastapi',
            'from fastapi': 'fastapi',
        }
        
        code_lower = code.lower()
        for import_pattern, package in import_mapping.items():
            if import_pattern in code_lower and package:
                requirements.add(package)
        
        # Remove tkinter if it's a web app
        if 'flask' in requirements or 'fastapi' in requirements:
            requirements.discard('tkinter')
            
        return list(requirements)

    def _generate_fallback_for_prompt(self, prompt: str, app_type: str, ui_framework: str) -> Dict[str, Any]:
        """Generate a fallback application based on the prompt when AI is not available"""
        
        # Analyze the prompt to determine what kind of app to create
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['calculator', 'calc', 'math', 'arithmetic']):
            return self._get_fallback_code('calculator', ui_framework)
        elif any(word in prompt_lower for word in ['text', 'editor', 'notepad', 'write']):
            return self._get_fallback_code('text_editor', ui_framework)
        elif any(word in prompt_lower for word in ['timer', 'clock', 'stopwatch', 'countdown']):
            return self._get_fallback_code('timer', ui_framework)
        elif any(word in prompt_lower for word in ['todo', 'task', 'list', 'reminder']):
            return self._get_fallback_code('todo_list', ui_framework)
        elif any(word in prompt_lower for word in ['game', 'play', 'tic', 'tac', 'toe']):
            return self._get_fallback_code('simple_game', ui_framework)
        else:
            # Create a generic utility app
            return self._create_generic_utility_app(prompt, ui_framework)

    def _create_generic_utility_app(self, prompt: str, ui_framework: str) -> Dict[str, Any]:
        """Create a generic utility application based on the prompt"""
        
        # Create a simple template that shows the user what was requested
        app_name = prompt.replace(' ', '_').lower()
        
        generic_code = f'''#!/usr/bin/env python3
"""
{prompt.title()}
Generated by SEAgent - Custom Application Template
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class {prompt.title().replace(' ', '')}App:
    def __init__(self, root):
        self.root = root
        self.root.title("{prompt.title()}")
        self.root.geometry("600x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="{prompt.title()}", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text="This is a template for: {prompt}\\n\\nTo customize this application:\\n1. Modify the interface below\\n2. Add your specific functionality\\n3. Connect buttons to your logic",
                              wraplength=500, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Sample interface
        ttk.Label(main_frame, text="Input:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_var, width=40)
        input_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Process", command=self.process_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="About", command=self.show_about).pack(side=tk.LEFT, padx=5)
        
        # Output area
        ttk.Label(main_frame, text="Output:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        self.output_text = tk.Text(main_frame, width=60, height=10)
        self.output_text.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.add_welcome_message()
    
    def process_action(self):
        """Process the input - customize this method for your specific needs"""
        input_text = self.input_var.get()
        if input_text:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            result = f"[{{timestamp}}] Processed: {{input_text}}\\n"
            self.output_text.insert(tk.END, result)
            self.output_text.see(tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter some input first!")
    
    def clear_action(self):
        """Clear the input and output"""
        self.input_var.set("")
        self.output_text.delete(1.0, tk.END)
        self.add_welcome_message()
    
    def show_about(self):
        """Show information about the application"""
        messagebox.showinfo("About", 
                           f"{{prompt.title()}}\\n\\nGenerated by SEAgent\\nCustomize this template for your specific needs!")
    
    def add_welcome_message(self):
        """Add welcome message to output"""
        welcome = f"Welcome to {{prompt.title()}}!\\nEnter your input above and click Process.\\n\\n"
        self.output_text.insert(tk.END, welcome)

def main():
    root = tk.Tk()
    app = {prompt.title().replace(' ', '')}App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        
        return {
            'code': generic_code,
            'requirements': ['tkinter'],
            'description': f'Template for: {prompt}',
            'features': [
                'Basic GUI template',
                'Customizable interface',
                'Input/Output handling',
                'Ready for customization'
            ],
            'filename': f'{app_name}.py',
            'ui_framework': ui_framework
        }

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

    async def _generate_web_app_code(self, prompt: str, ui_framework: str = 'flask') -> Dict[str, Any]:
        """Generate web application code"""
        
        # Simple todo list web app as fallback
        web_app_code = '''#!/usr/bin/env python3
"""
Simple Todo List Web Application
A responsive web app for managing tasks with Flask backend
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Simple in-memory storage (use database in production)
todos = []

@app.route('/')
def index():
    return render_template('index.html', todos=todos)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    todo = {
        'id': str(uuid.uuid4()),
        'text': data['text'],
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    todos.append(todo)
    return jsonify(todo), 201

@app.route('/api/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo['id'] == todo_id:
            if 'completed' in data:
                todo['completed'] = data['completed']
            if 'text' in data:
                todo['text'] = data['text']
            return jsonify(todo)
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .add-todo {
            padding: 30px;
            border-bottom: 1px solid #eee;
        }
        
        .add-form {
            display: flex;
            gap: 10px;
        }
        
        .add-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .add-input:focus {
            border-color: #4facfe;
        }
        
        .add-btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        
        .add-btn:hover {
            transform: translateY(-2px);
        }
        
        .todos {
            padding: 20px 30px 30px;
        }
        
        .todo-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 10px;
            transition: all 0.3s;
        }
        
        .todo-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .todo-checkbox {
            margin-right: 15px;
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .todo-text {
            flex: 1;
            font-size: 16px;
        }
        
        .todo-text.completed {
            text-decoration: line-through;
            color: #999;
        }
        
        .delete-btn {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .delete-btn:hover {
            background: #ff5252;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>My Todo List</h1>
            <p>Stay organized and productive</p>
        </div>
        
        <div class="add-todo">
            <form class="add-form" id="addForm">
                <input type="text" class="add-input" id="todoInput" placeholder="What needs to be done?" required>
                <button type="submit" class="add-btn">Add Task</button>
            </form>
        </div>
        
        <div class="todos" id="todosList">
            <div class="empty-state" id="emptyState">
                <h3>No tasks yet!</h3>
                <p>Add a task above to get started.</p>
            </div>
        </div>
    </div>

    <script>
        const todosList = document.getElementById('todosList');
        const emptyState = document.getElementById('emptyState');
        const addForm = document.getElementById('addForm');
        const todoInput = document.getElementById('todoInput');

        let todos = [];

        // Load todos on page load
        loadTodos();

        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = todoInput.value.trim();
            if (text) {
                await addTodo(text);
                todoInput.value = '';
            }
        });

        async function loadTodos() {
            try {
                const response = await fetch('/api/todos');
                todos = await response.json();
                renderTodos();
            } catch (error) {
                console.error('Error loading todos:', error);
            }
        }

        async function addTodo(text) {
            try {
                const response = await fetch('/api/todos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text }),
                });
                const newTodo = await response.json();
                todos.push(newTodo);
                renderTodos();
            } catch (error) {
                console.error('Error adding todo:', error);
            }
        }

        async function toggleTodo(id) {
            const todo = todos.find(t => t.id === id);
            if (todo) {
                try {
                    const response = await fetch(`/api/todos/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ completed: !todo.completed }),
                    });
                    const updatedTodo = await response.json();
                    const index = todos.findIndex(t => t.id === id);
                    todos[index] = updatedTodo;
                    renderTodos();
                } catch (error) {
                    console.error('Error updating todo:', error);
                }
            }
        }

        async function deleteTodo(id) {
            try {
                await fetch(`/api/todos/${id}`, {
                    method: 'DELETE',
                });
                todos = todos.filter(t => t.id !== id);
                renderTodos();
            } catch (error) {
                console.error('Error deleting todo:', error);
            }
        }

        function renderTodos() {
            if (todos.length === 0) {
                todosList.innerHTML = '<div class="empty-state" id="emptyState"><h3>No tasks yet!</h3><p>Add a task above to get started.</p></div>';
                return;
            }

            todosList.innerHTML = todos.map(todo => `
                <div class="todo-item">
                    <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''} 
                           onchange="toggleTodo('${todo.id}')">
                    <span class="todo-text ${todo.completed ? 'completed' : ''}">${todo.text}</span>
                    <button class="delete-btn" onclick="deleteTodo('${todo.id}')">Delete</button>
                </div>
            `).join('');
        }
    </script>
</body>
</html>"""
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Starting Todo List Web App...")
    print("Open your browser to: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
'''
        
        return {
            'code': web_app_code,
            'requirements': ['flask'],
            'description': 'A responsive Todo List web application with Flask backend',
            'features': [
                'Add, edit, and delete tasks',
                'Mark tasks as completed',
                'Responsive modern UI design',
                'REST API endpoints',
                'Real-time updates',
                'Local storage support'
            ],
            'filename': 'todo_app.py',
            'app_type': 'web_app',
            'port': 5000,
            'url': 'http://127.0.0.1:5000'
        }
    
    async def _create_app_files(self, app_code: Dict[str, Any], app_type: str) -> Dict[str, Any]:
        """Create application files in temporary directory with validation"""
        try:
            # Validate the generated code first
            code = app_code.get('code', '')
            if not code or len(code.strip()) < 50:
                return {
                    'temp_dir': None,
                    'main_file': None,
                    'error': 'Generated code is too short or empty',
                    'validation_failed': True
                }
            
            # Basic Python syntax validation
            try:
                compile(code, '<generated_code>', 'exec')
                self.logger.info("✅ Generated code passed syntax validation")
            except SyntaxError as e:
                self.logger.error(f"❌ Generated code has syntax errors: {e}")
                return {
                    'temp_dir': None,
                    'main_file': None,
                    'error': f'Generated code has syntax errors: {e}',
                    'validation_failed': True
                }
            
            # Create temporary directory for the application
            temp_dir = tempfile.mkdtemp(prefix=f'seagent_{app_type}_')
            self.logger.info(f"Created temp directory: {temp_dir}")
            
            # Main application file
            main_file = Path(temp_dir) / app_code.get('filename', f'{app_type}.py')
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Verify the file was created and has content
            if not main_file.exists() or main_file.stat().st_size == 0:
                return {
                    'temp_dir': str(temp_dir),
                    'main_file': None,
                    'error': 'Main file creation failed',
                    'validation_failed': True
                }
            
            self.logger.info(f"✅ Main application file created: {main_file} ({main_file.stat().st_size} bytes)")
            
            # Requirements file if needed
            requirements_file = None
            if app_code.get('requirements'):
                requirements_file = Path(temp_dir) / 'requirements.txt'
                with open(requirements_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(app_code['requirements']))
                self.logger.info(f"✅ Requirements file created: {requirements_file}")
            
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
            
            # Final validation - check all files exist
            files_created = [str(main_file), str(readme_file)]
            if requirements_file:
                files_created.append(str(requirements_file))
            
            all_files_exist = all(Path(f).exists() for f in files_created)
            
            if not all_files_exist:
                return {
                    'temp_dir': str(temp_dir),
                    'main_file': None,
                    'error': 'Some files failed to create properly',
                    'validation_failed': True
                }
            
            self.logger.info(f"✅ All {len(files_created)} files created successfully")
            
            return {
                'temp_dir': str(temp_dir),
                'main_file': str(main_file),
                'requirements_file': str(requirements_file) if requirements_file else None,
                'readme_file': str(readme_file),
                'files_created': files_created,
                'validation_passed': True,
                'file_count': len(files_created)
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
                # Try to get API key from environment first
                import os
                api_key = os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
                self.logger.info(f"🔍 API key found: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
                
                if api_key:
                    self.deepseek_client = DeepSeekClient(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1",
                        model="openai/gpt-3.5-turbo"
                    )
                    self.use_simulation = False
                    self.logger.info("✅ DeepSeek client initialized successfully")
                    self.logger.info(f"✅ use_simulation set to: {self.use_simulation}")
                else:
                    # Try configuration
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
                        self.use_simulation = False
                        self.logger.info("✅ DeepSeek client initialized from config")
                        
                        # Test the connection
                        test_result = self.deepseek_client.test_connection()
                        if test_result.get('success'):
                            self.logger.info(f"Successfully connected to {model}")
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
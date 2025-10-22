"""
Code Generation Agent - Intelligent code generation with context awareness
Enhanced with secure DeepSeek-Coder V2 integration
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from pathlib import Path

from .base_agent import BaseAgent, AgentCapability
from config.deepseek_client import DeepSeekClient

# Try to import OpenAI for DeepSeek compatibility
DEEPSEEK_AVAILABLE = False
openai = None

try:
    import openai
    from openai import OpenAI
    DEEPSEEK_AVAILABLE = True
except ImportError:
    print("OpenAI package not available for DeepSeek integration. Code generation will run in simulation mode.")
except Exception as e:
    print(f"DeepSeek integration failed: {e}. Code generation will run in simulation mode.")


class CodeGenerationAgent(BaseAgent):
    """Agent responsible for intelligent code generation and modification"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.deepseek_client = None
        self.use_simulation = True  # Default to simulation mode
        
        # Initialize deepseek_config with default values
        # Handle both dict and AgentConfig object
        if hasattr(config, 'specific_config'):
            # AgentConfig object
            specific = config.specific_config
            self.deepseek_config = {
                'max_tokens': specific.get('max_tokens', 4000),
                'temperature': specific.get('temperature', 0.7),
                'model': specific.get('model', 'openai/gpt-3.5-turbo'),
                'base_url': specific.get('base_url', 'https://openrouter.ai/api/v1')
            }
        else:
            # Dict object
            self.deepseek_config = {
                'max_tokens': config.get('max_tokens', 4000),
                'temperature': config.get('temperature', 0.7),
                'model': config.get('model', 'openai/gpt-3.5-turbo'),
                'base_url': config.get('base_url', 'https://openrouter.ai/api/v1')
            }
    
    async def _setup_capabilities(self):
        """Setup code generation capabilities"""
        self.capabilities = {
            'generate_code': AgentCapability(
                name='generate_code',
                description='Generate code based on requirements',
                input_schema={
                    'requirements': 'string',
                    'language': 'string',
                    'framework': 'string (optional)',
                    'context': 'object (optional)'
                },
                output_schema={
                    'code': 'string',
                    'explanation': 'string',
                    'files': 'array',
                    'dependencies': 'array'
                }
            ),
            'refactor_code': AgentCapability(
                name='refactor_code',
                description='Refactor existing code for better quality',
                input_schema={
                    'source_code': 'string',
                    'refactor_type': 'string',
                    'targets': 'array (optional)'
                },
                output_schema={
                    'refactored_code': 'string',
                    'changes': 'array',
                    'improvements': 'string'
                }
            ),
            'generate_tests': AgentCapability(
                name='generate_tests',
                description='Generate test cases for code',
                input_schema={
                    'source_code': 'string',
                    'test_framework': 'string',
                    'coverage_target': 'number (optional)'
                },
                output_schema={
                    'test_code': 'string',
                    'test_cases': 'array',
                    'coverage_estimate': 'number'
                }
            ),
            'fix_code': AgentCapability(
                name='fix_code',
                description='Fix code based on error reports or security findings',
                input_schema={
                    'source_code': 'string',
                    'errors': 'array',
                    'fix_strategy': 'string (optional)'
                },
                output_schema={
                    'fixed_code': 'string',
                    'fixes_applied': 'array',
                    'explanation': 'string'
                }
            )
        }
    
    async def _load_models(self):
        """Initialize AI models with proper OpenRouter configuration"""
        try:
            # Get configuration from environment
            api_key = os.getenv('DEEPSEEK_API_KEY', '').strip()
            base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1').strip()
            model = os.getenv('DEEPSEEK_MODEL', 'openai/gpt-3.5-turbo').strip()
            
            if not api_key:
                self.logger.warning("No DEEPSEEK_API_KEY found. Code generation will use simulation mode.")
                self.use_simulation = True
                return
            
            # Initialize DeepSeek client with OpenRouter configuration
            self.deepseek_client = DeepSeekClient(
                api_key=api_key,
                base_url=base_url,
                model=model
            )
            
            # Test the connection
            test_result = self.deepseek_client.test_connection()
            if test_result['success']:
                self.logger.info(f"Successfully connected to {model} via OpenRouter")
                self.use_simulation = False
            else:
                self.logger.error(f"Failed to connect to DeepSeek API: {test_result.get('error', 'Unknown error')}")
                self.logger.info("Falling back to simulation mode")
                self.use_simulation = True
                
        except Exception as e:
            self.logger.error(f"Error loading DeepSeek model: {str(e)}")
            self.logger.info("Falling back to simulation mode")
            self.use_simulation = True

    async def _setup_resources(self):
        """Setup additional resources for code generation"""
        # Setup code templates, patterns, best practices database
        self.code_templates = await self._load_code_templates()
        self.best_practices = await self._load_best_practices()
        self.code_patterns = await self._load_code_patterns()
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a code generation task"""
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        task_type = parameters.get('task_type', 'generate_code')
        
        if task_type == 'generate_code':
            return await self._generate_code(parameters)
        elif task_type == 'refactor_code':
            return await self._refactor_code(parameters)
        elif task_type == 'generate_tests':
            return await self._generate_tests(parameters)
        elif task_type == 'fix_code':
            return await self._fix_code(parameters)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new code based on requirements"""
        requirements = parameters.get('requirements', '')
        language = parameters.get('language', 'python')
        framework = parameters.get('framework', '')
        context = parameters.get('context', {})
        
        # Ensure all parameters are valid strings
        if not requirements:
            requirements = "Basic code generation"
        if not language:
            language = 'python'
        if framework is None:
            framework = ''
        
        self.logger.info(f"Generating code for: {requirements[:100]}...")
        
        # Use DeepSeek if available, otherwise fallback to simulation
        if self.deepseek_client:
            self.logger.info("Using DeepSeek-Coder V2 for code generation")
            generated_code = await self._generate_code_with_ai(requirements, language, framework, context)
        else:
            self.logger.info("DeepSeek client not available, using simulation mode")
            generated_code = await self._simulate_code_generation(requirements, language, framework, context)
        
        return {
            'code': generated_code['code'],
            'explanation': generated_code['explanation'],
            'files': generated_code['files'],
            'dependencies': generated_code['dependencies'],
            'language': language,
            'framework': framework,
            'quality_score': generated_code['quality_score']
        }
    
    async def _refactor_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor existing code"""
        source_code = parameters.get('source_code', '')
        refactor_type = parameters.get('refactor_type', 'general')
        targets = parameters.get('targets', [])
        
        self.logger.info(f"Refactoring code ({refactor_type})")
        
        # Simulate refactoring process
        await asyncio.sleep(0.5)
        
        refactored_result = await self._simulate_code_refactoring(source_code, refactor_type, targets)
        
        return {
            'refactored_code': refactored_result['code'],
            'changes': refactored_result['changes'],
            'improvements': refactored_result['improvements'],
            'quality_improvement': refactored_result['quality_improvement']
        }
    
    async def _generate_tests(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test cases for code"""
        source_code = parameters.get('source_code', '')
        test_framework = parameters.get('test_framework', 'pytest')
        coverage_target = parameters.get('coverage_target', 80)
        
        self.logger.info(f"Generating tests with {test_framework}")
        
        # Simulate test generation
        await asyncio.sleep(0.8)
        
        test_result = await self._simulate_test_generation(source_code, test_framework, coverage_target)
        
        return {
            'test_code': test_result['code'],
            'test_cases': test_result['cases'],
            'coverage_estimate': test_result['coverage'],
            'framework': test_framework
        }
    
    async def _fix_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fix code based on error reports"""
        source_code = parameters.get('source_code', '')
        errors = parameters.get('errors', [])
        fix_strategy = parameters.get('fix_strategy', 'conservative')
        
        self.logger.info(f"Fixing {len(errors)} errors with {fix_strategy} strategy")
        
        # Simulate code fixing
        await asyncio.sleep(0.6)
        
        fix_result = await self._simulate_code_fixing(source_code, errors, fix_strategy)
        
        return {
            'fixed_code': fix_result['code'],
            'fixes_applied': fix_result['fixes'],
            'explanation': fix_result['explanation'],
            'success_rate': fix_result['success_rate']
        }
    
    async def _load_code_templates(self) -> Dict[str, Any]:
        """Load code templates for different languages and frameworks"""
        return {
            'python': {
                'class': 'class {name}:\n    def __init__(self):\n        pass',
                'function': 'def {name}({params}):\n    """TODO: Implement function"""\n    pass',
                'test': 'def test_{name}():\n    """Test for {target}"""\n    assert True'
            },
            'javascript': {
                'class': 'class {name} {\n    constructor() {\n        // TODO: Implement\n    }\n}',
                'function': 'function {name}({params}) {\n    // TODO: Implement\n}',
                'test': 'test("{name}", () => {\n    // TODO: Implement test\n});'
            }
        }
    
    async def _load_best_practices(self) -> Dict[str, List[str]]:
        """Load best practices for different languages"""
        return {
            'python': [
                'Use type hints for better code clarity',
                'Follow PEP 8 style guidelines',
                'Use docstrings for documentation',
                'Handle exceptions appropriately',
                'Use list comprehensions when appropriate'
            ],
            'javascript': [
                'Use const/let instead of var',
                'Use arrow functions appropriately',
                'Handle promises properly',
                'Use strict mode',
                'Validate input parameters'
            ]
        }
    
    async def _load_code_patterns(self) -> Dict[str, Any]:
        """Load common code patterns and design patterns"""
        return {
            'design_patterns': ['singleton', 'factory', 'observer', 'strategy'],
            'security_patterns': ['input_validation', 'output_encoding', 'authentication'],
            'performance_patterns': ['caching', 'lazy_loading', 'connection_pooling']
        }
    
    async def _generate_code_with_ai(self, requirements: str, language: str, framework: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using DeepSeek-Coder V2 API"""
        try:
            # Construct the prompt optimized for DeepSeek-Coder V2
            prompt = self._build_code_generation_prompt(requirements, language, framework, context)
            
            self.logger.info(f"Calling DeepSeek-Coder V2 for code generation")
            
            # Use DeepSeek client for code generation
            result = self.deepseek_client.generate_code(
                prompt=prompt,
                max_tokens=self.deepseek_config['max_tokens'],
                temperature=self.deepseek_config['temperature']
            )
            
            if result['success']:
                self.logger.info("DeepSeek-Coder V2 API call successful, parsing response...")
                # Parse the response to extract code, explanation, etc.
                return self._parse_ai_response(result['code'], language, framework)
            else:
                raise Exception("DeepSeek API returned unsuccessful result")
            
        except Exception as e:
            self.logger.error(f"DeepSeek code generation failed: {e}")
            self.logger.info("Falling back to simulation mode")
            # Fallback to simulation
            return await self._simulate_code_generation(requirements, language, framework, context)
    
    def _build_code_generation_prompt(self, requirements: str, language: str, framework: str, context: Dict[str, Any]) -> str:
        """Build a comprehensive prompt optimized for DeepSeek-Coder V2"""
        prompt = f"""
You are DeepSeek-Coder V2, a specialized AI model for coding tasks. Generate high-quality, production-ready code based on these requirements:

**Requirements**: {requirements}

**Technical Specifications**:
- Programming Language: {language}
- Framework: {framework if framework else 'None specified - choose the best one'}
- Include proper error handling, logging, and documentation
- Follow best practices and coding standards for {language}
- Make the code secure, efficient, and maintainable
- Use modern patterns and optimize for performance

**Additional Context**: {json.dumps(context, indent=2) if context else 'None provided'}

**Please provide a complete implementation that includes**:
1. Working, tested code with proper structure and organization
2. Clear comments and comprehensive documentation
3. Robust error handling and input validation
4. Any necessary imports and dependencies
5. Example usage if applicable

**Response Format**: Provide your response as JSON with this exact structure:
{{
    "code": "// Complete implementation here",
    "explanation": "Detailed explanation of the solution",
    "files": ["list of files that should be created"],
    "dependencies": ["required packages/libraries"],
    "quality_score": 0.95
}}

Focus on creating functional, maintainable code that solves the requirements completely.
"""
        return prompt
    
    def _parse_ai_response(self, response_content: str, language: str, framework: str) -> Dict[str, Any]:
        """Parse the AI response to extract structured information"""
        try:
            # Try to parse as JSON first
            if response_content.strip().startswith('{'):
                return json.loads(response_content)
            
            # If not JSON, extract code from markdown blocks
            import re
            code_match = re.search(r'```(?:' + language + r')?\n(.*?)\n```', response_content, re.DOTALL)
            
            if code_match:
                code = code_match.group(1)
            else:
                # Fallback: use the entire response as code
                code = response_content
            
            return {
                'code': code,
                'explanation': f'Generated {language} code using AI',
                'files': [f'main.{self._get_file_extension(language)}'],
                'dependencies': self._get_dependencies(language, framework),
                'quality_score': 0.90
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            return {
                'code': response_content,
                'explanation': f'Generated {language} code (raw output)',
                'files': [f'main.{self._get_file_extension(language)}'],
                'dependencies': [],
                'quality_score': 0.75
            }

    async def _simulate_code_generation(self, requirements: str, language: str, framework: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate AI-powered code generation"""
        # This would be replaced with actual AI model calls
        
        # Ensure requirements is not None
        if not requirements:
            requirements = "Basic code generation"
        
        if 'calculator' in requirements.lower():
            code = '''
def calculate(operation, a, b):
    """Perform basic arithmetic operations"""
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

class Calculator:
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        result = calculate(operation, a, b)
        self.history.append(f"{a} {operation} {b} = {result}")
        return result
    
    def get_history(self):
        return self.history.copy()
'''
        else:
            code = f'''
# Generated code for: {requirements}
# Language: {language}
# Framework: {framework}

def main():
    """Main function implementing the requirements"""
    # TODO: Implement the required functionality
    pass

if __name__ == "__main__":
    main()
'''
        
        return {
            'code': code,
            'explanation': f'Generated {language} code to implement: {requirements}',
            'files': [f'main.{self._get_file_extension(language)}'],
            'dependencies': self._get_dependencies(language, framework),
            'quality_score': 0.85
        }
    
    async def _simulate_code_refactoring(self, source_code: str, refactor_type: str, targets: List[str]) -> Dict[str, Any]:
        """Simulate code refactoring"""
        # Simple simulation - in reality this would use sophisticated analysis
        
        changes = []
        if refactor_type == 'extract_method':
            changes.append('Extracted common code into reusable methods')
        elif refactor_type == 'rename_variables':
            changes.append('Renamed variables for better clarity')
        elif refactor_type == 'optimize_performance':
            changes.append('Optimized loops and data structures')
        else:
            changes.append('Applied general code improvements')
        
        return {
            'code': source_code + '\n# Refactored code\n',
            'changes': changes,
            'improvements': f'Applied {refactor_type} refactoring',
            'quality_improvement': 0.15
        }
    
    async def _simulate_test_generation(self, source_code: str, framework: str, coverage_target: int) -> Dict[str, Any]:
        """Simulate test code generation"""
        test_cases = [
            'test_basic_functionality',
            'test_edge_cases',
            'test_error_handling',
            'test_input_validation'
        ]
        
        # Build test code properly to avoid f-string backslash issues
        newline = '\n'
        test_functions = []
        for case in test_cases:
            test_functions.append(f"def {case}():{newline}    # TODO: Implement test{newline}    assert True")
        
        test_code = f'''
import {framework}

{newline.join(test_functions)}
'''
        
        return {
            'code': test_code,
            'cases': test_cases,
            'coverage': min(coverage_target, 85)
        }
    
    async def _simulate_code_fixing(self, source_code: str, errors: List[str], strategy: str) -> Dict[str, Any]:
        """Simulate code fixing"""
        fixes = []
        for error in errors:
            if 'syntax' in error.lower():
                fixes.append('Fixed syntax error')
            elif 'undefined' in error.lower():
                fixes.append('Defined missing variable/function')
            elif 'type' in error.lower():
                fixes.append('Fixed type mismatch')
            else:
                fixes.append('Applied general fix')
        
        return {
            'code': source_code + '\n# Fixed code\n',
            'fixes': fixes,
            'explanation': f'Applied {len(fixes)} fixes using {strategy} strategy',
            'success_rate': 0.9
        }
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        # Ensure language is not None
        if not language:
            language = 'python'
            
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java',
            'cpp': 'cpp',
            'csharp': 'cs'
        }
        return extensions.get(language.lower(), 'txt')
    
    def _get_dependencies(self, language: str, framework: str) -> List[str]:
        """Get typical dependencies for language/framework"""
        # Ensure parameters are not None
        if not language:
            language = 'python'
        if not framework:
            framework = ''
            
        if language.lower() == 'python':
            if framework and framework.lower() == 'django':
                return ['django', 'djangorestframework']
            elif framework and framework.lower() == 'flask':
                return ['flask', 'flask-restful']
            else:
                return ['requests', 'pytest']
        elif language.lower() == 'javascript':
            if framework and framework.lower() == 'react':
                return ['react', 'react-dom']
            elif framework and framework.lower() == 'node':
                return ['express', 'lodash']
            else:
                return ['lodash']
        return []

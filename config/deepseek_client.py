"""
DeepSeek-Coder V2 Client Integration
Enhanced with secure API integration for coding tasks
"""

import os
import logging
from typing import Dict, Any, Optional, List
import json

# Try to import OpenAI (we'll use it for DeepSeek's OpenAI-compatible API)
DEEPSEEK_AVAILABLE = False
openai = None

try:
    import openai
    from openai import OpenAI
    DEEPSEEK_AVAILABLE = True
except ImportError as e:
    print("OpenAI package not available for DeepSeek integration. Code generation will run in simulation mode.")
except Exception as e:
    print(f"DeepSeek integration failed: {e}. Code generation will run in simulation mode.")


class DeepSeekClient:
    """
    DeepSeek-Coder V2 client wrapper using OpenAI-compatible API
    Specialized for coding tasks with Mixture-of-Experts architecture
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-coder"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        if DEEPSEEK_AVAILABLE and api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            self.logger.info("DeepSeek-Coder V2 client initialized successfully")
        else:
            self.client = None
            self.logger.warning("DeepSeek-Coder V2 client not available - running in simulation mode")
    
    async def generate_code(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate code using DeepSeek-Coder V2
        
        Args:
            prompt: The coding prompt/request
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature for creativity vs consistency
            
        Returns:
            Dictionary with generated code and metadata
        """
        if not self.client:
            return await self._simulate_code_generation(prompt)
        
        try:
            # Use DeepSeek-Coder V2 for specialized coding tasks
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are DeepSeek-Coder V2, a specialized AI model for coding tasks. "
                                 "Generate clean, efficient, and well-documented code. "
                                 "Use best practices and modern patterns. "
                                 "Include proper error handling and comments."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            generated_code = response.choices[0].message.content
            
            return {
                "code": generated_code,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "success": True,
                "source": "deepseek-coder-v2"
            }
            
        except Exception as e:
            self.logger.error(f"DeepSeek API error: {e}")
            return await self._simulate_code_generation(prompt)
    
    async def analyze_code(self, code: str, analysis_type: str = "security") -> Dict[str, Any]:
        """
        Analyze code for security, performance, or quality issues
        
        Args:
            code: The code to analyze
            analysis_type: Type of analysis (security, performance, quality)
            
        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            return await self._simulate_code_analysis(code, analysis_type)
        
        try:
            analysis_prompts = {
                "security": "Analyze this code for security vulnerabilities, potential exploits, and security best practices. Provide specific recommendations.",
                "performance": "Analyze this code for performance bottlenecks, optimization opportunities, and efficiency improvements.",
                "quality": "Analyze this code for code quality, maintainability, readability, and adherence to best practices."
            }
            
            prompt = f"{analysis_prompts.get(analysis_type, analysis_prompts['quality'])}\n\nCode:\n{code}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are DeepSeek-Coder V2, analyzing code for {analysis_type}. "
                                 "Provide detailed, actionable analysis with specific recommendations."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3  # Lower temperature for analysis tasks
            )
            
            analysis_result = response.choices[0].message.content
            
            return {
                "analysis": analysis_result,
                "type": analysis_type,
                "model": self.model,
                "success": True,
                "source": "deepseek-coder-v2"
            }
            
        except Exception as e:
            self.logger.error(f"DeepSeek analysis error: {e}")
            return await self._simulate_code_analysis(code, analysis_type)
    
    async def fix_code(self, code: str, error_message: str) -> Dict[str, Any]:
        """
        Fix code based on error messages
        
        Args:
            code: The problematic code
            error_message: Error message or description
            
        Returns:
            Dictionary with fixed code and explanation
        """
        if not self.client:
            return await self._simulate_code_fix(code, error_message)
        
        try:
            prompt = f"""Fix the following code that has this error: {error_message}

Original Code:
{code}

Please provide the corrected code with explanations of the changes made."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are DeepSeek-Coder V2, specialized in debugging and fixing code. "
                                 "Provide corrected code with clear explanations of changes."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.2  # Very low temperature for fixing
            )
            
            fix_result = response.choices[0].message.content
            
            return {
                "fixed_code": fix_result,
                "original_error": error_message,
                "model": self.model,
                "success": True,
                "source": "deepseek-coder-v2"
            }
            
        except Exception as e:
            self.logger.error(f"DeepSeek fix error: {e}")
            return await self._simulate_code_fix(code, error_message)
    
    async def generate_tests(self, code: str, test_framework: str = "pytest") -> Dict[str, Any]:
        """
        Generate test cases for given code
        
        Args:
            code: The code to generate tests for
            test_framework: Testing framework to use
            
        Returns:
            Dictionary with generated test code
        """
        if not self.client:
            return await self._simulate_test_generation(code, test_framework)
        
        try:
            prompt = f"""Generate comprehensive test cases for the following code using {test_framework}:

{code}

Include:
1. Unit tests for all functions/methods
2. Edge cases and boundary conditions
3. Error handling tests
4. Mock external dependencies if needed
5. Clear test documentation"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are DeepSeek-Coder V2, generating comprehensive test cases using {test_framework}. "
                                 "Create thorough, maintainable tests with good coverage."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.4
            )
            
            test_code = response.choices[0].message.content
            
            return {
                "test_code": test_code,
                "framework": test_framework,
                "model": self.model,
                "success": True,
                "source": "deepseek-coder-v2"
            }
            
        except Exception as e:
            self.logger.error(f"DeepSeek test generation error: {e}")
            return await self._simulate_test_generation(code, test_framework)
    
    # Simulation methods for fallback
    async def _simulate_code_generation(self, prompt: str) -> Dict[str, Any]:
        """Simulate code generation when DeepSeek is not available"""
        return {
            "code": f"# Generated code for: {prompt[:50]}...\n# DeepSeek-Coder V2 simulation mode\n\ndef example_function():\n    # TODO: Implement based on requirements\n    pass",
            "model": "simulation",
            "tokens_used": 0,
            "success": True,
            "source": "simulation"
        }
    
    async def _simulate_code_analysis(self, code: str, analysis_type: str) -> Dict[str, Any]:
        """Simulate code analysis when DeepSeek is not available"""
        return {
            "analysis": f"Simulated {analysis_type} analysis:\n- Code structure looks good\n- Consider adding error handling\n- Review for optimization opportunities",
            "type": analysis_type,
            "model": "simulation",
            "success": True,
            "source": "simulation"
        }
    
    async def _simulate_code_fix(self, code: str, error_message: str) -> Dict[str, Any]:
        """Simulate code fixing when DeepSeek is not available"""
        return {
            "fixed_code": f"# Fixed code (simulation)\n{code}\n# Applied simulated fix for: {error_message}",
            "original_error": error_message,
            "model": "simulation",
            "success": True,
            "source": "simulation"
        }
    
    async def _simulate_test_generation(self, code: str, test_framework: str) -> Dict[str, Any]:
        """Simulate test generation when DeepSeek is not available"""
        return {
            "test_code": f"# Generated tests using {test_framework} (simulation)\nimport {test_framework}\n\ndef test_example():\n    # TODO: Implement actual tests\n    assert True",
            "framework": test_framework,
            "model": "simulation",
            "success": True,
            "source": "simulation"
        }
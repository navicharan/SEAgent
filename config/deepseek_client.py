"""
DeepSeek-Coder V2 Client Integration
Enhanced with secure API integration for coding tasks
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DeepSeekConfig:
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"  # Updated for OpenRouter
    model: str = "openai/gpt-3.5-turbo"  # Updated to standard OpenRouter model
    max_tokens: int = 4000
    temperature: float = 0.7

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", 
                 model: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Required for OpenRouter
            "X-Title": "SEAgent"  # Optional but recommended for OpenRouter
        }
        
    def generate_code(self, prompt: str, language: str = "python", 
                     max_tokens: int = 4000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate code using DeepSeek model via OpenRouter"""
        try:
            # Enhanced prompt for better code generation
            enhanced_prompt = f"""
You are an expert software engineer specializing in {language}. 
Generate clean, well-documented, production-ready code based on the following requirements:

{prompt}

Requirements:
- Write complete, functional code
- Include proper error handling
- Add comprehensive comments
- Follow {language} best practices
- Ensure code is ready for production use

Generate only the code without additional explanations unless specifically requested.
"""

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert {language} developer. Generate clean, production-ready code with proper error handling and documentation."
                    },
                    {
                        "role": "user", 
                        "content": enhanced_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            logger.info(f"Sending request to {self.base_url}/chat/completions with model {self.model}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    generated_code = data['choices'][0]['message']['content']
                    logger.info(f"Successfully generated {len(generated_code)} characters of code")
                    return {
                        'success': True,
                        'code': generated_code,
                        'model': self.model,
                        'usage': data.get('usage', {}),
                        'language': language
                    }
                else:
                    logger.error(f"No choices in response: {data}")
                    return {
                        'success': False,
                        'error': 'No code generated in response',
                        'response': data
                    }
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API request failed: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in generate_code: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code for security, performance, and best practices"""
        try:
            prompt = f"""
Analyze the following {language} code and provide detailed feedback on:
1. Security vulnerabilities
2. Performance optimizations
3. Code quality and best practices
4. Potential bugs or issues
5. Improvement suggestions

Code to analyze:
```{language}
{code}
```

Provide a structured analysis with specific recommendations.
"""

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert code reviewer specializing in {language}. Provide thorough analysis of security, performance, and code quality."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    analysis = data['choices'][0]['message']['content']
                    return {
                        'success': True,
                        'analysis': analysis,
                        'model': self.model
                    }
            
            return {
                'success': False,
                'error': f'Analysis failed: {response.status_code}',
                'details': response.text if response else 'No response'
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_code: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'Connection successful'"
                    }
                ],
                "max_tokens": 50,
                "temperature": 0
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': 'Connection successful',
                    'model': self.model,
                    'response': data.get('choices', [{}])[0].get('message', {}).get('content', '')
                }
            else:
                return {
                    'success': False,
                    'error': f'Connection failed: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}'
            }
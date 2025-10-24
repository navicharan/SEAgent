"""
Code Evaluation Engine - Comprehensive testing with HumanEval and SecurityEval datasets
Provides security scoring, test case validation, and performance metrics
"""

import asyncio
import json
import os
import re
import subprocess
import tempfile
import time
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import requests
from urllib.parse import urljoin
import hashlib

from .base_agent import BaseAgent, AgentCapability


@dataclass
class EvaluationResult:
    """Result of code evaluation"""
    test_suite: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    security_score: float
    performance_score: float
    correctness_score: float
    overall_score: float
    vulnerabilities: List[Dict[str, Any]]
    execution_time: float
    detailed_results: Dict[str, Any]


class DatasetManager:
    """Manages HumanEval and SecurityEval datasets"""
    
    def __init__(self, cache_dir: str = "datasets"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.humaneval_cache = self.cache_dir / "humaneval.json"
        self.securityeval_cache = self.cache_dir / "securityeval.json"
    
    async def load_humaneval_dataset(self) -> List[Dict[str, Any]]:
        """Load HumanEval dataset (simulated with common programming problems)"""
        if self.humaneval_cache.exists():
            with open(self.humaneval_cache, 'r') as f:
                return json.load(f)
        
        # Create simulated HumanEval-style problems
        humaneval_problems = [
            {
                "task_id": "HumanEval/0",
                "prompt": "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"\n",
                "canonical_solution": "    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n\n    return False\n",
                "test": "def check(candidate):\n    assert candidate([1.0, 2.0, 3.0], 0.5) == False\n    assert candidate([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False\n    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True\n",
                "entry_point": "has_close_elements"
            },
            {
                "task_id": "HumanEval/1", 
                "prompt": "def separate_paren_groups(paren_string: str) -> List[str]:\n    \"\"\" Input to this function is a string containing multiple groups of nested parentheses. Your goal is to\n    separate those group and return the list of those.\n    Separate groups are balanced (each open brace is properly closed) and not nested within each other\n    Ignore any spaces in the input string.\n    >>> separate_paren_groups('( ) (( )) (( )( ))')\n    ['()', '(())', '(()())']\n    \"\"\"\n",
                "canonical_solution": "    result = []\n    current_string = []\n    current_depth = 0\n\n    for c in paren_string:\n        if c == '(':\n            current_depth += 1\n            current_string.append(c)\n        elif c == ')':\n            current_depth -= 1\n            current_string.append(c)\n\n            if current_depth == 0:\n                result.append(''.join(current_string))\n                current_string = []\n\n    return result\n",
                "test": "def check(candidate):\n    assert candidate('( ) (( )) (( )( ))') == ['()', '(())', '(()())']\n    assert candidate('') == []\n    assert candidate('(()(()))') == ['(()(()))']\n    assert candidate('() (()) ((())) (((())))') == ['()', '(())', '((()))', '(((())))']\n",
                "entry_point": "separate_paren_groups"
            },
            {
                "task_id": "HumanEval/2",
                "prompt": "def truncate_number(number: float) -> float:\n    \"\"\" Given a positive floating point number, it can be decomposed into\n    and integer part (largest integer smaller than given number) and decimals\n    (leftover part always smaller than 1).\n\n    Return the decimal part of the number.\n    >>> truncate_number(3.5)\n    0.5\n    \"\"\"\n",
                "canonical_solution": "    return number % 1.0\n",
                "test": "def check(candidate):\n    assert candidate(3.5) == 0.5\n    assert candidate(1.25) == 0.25\n    assert candidate(123.0) == 0.0\n",
                "entry_point": "truncate_number"
            },
            {
                "task_id": "HumanEval/3",
                "prompt": "def below_zero(operations: List[int]) -> bool:\n    \"\"\" You're given a list of deposit and withdrawal operations on a bank account that starts with\n    zero balance. Your task is to detect if at any point the balance of account fallls below zero, and\n    at that point function should return True. Otherwise it should return False.\n    >>> below_zero([1, 2, 3])\n    False\n    >>> below_zero([1, 2, -4, 5])\n    True\n    \"\"\"\n",
                "canonical_solution": "    balance = 0\n\n    for op in operations:\n        balance += op\n        if balance < 0:\n            return True\n\n    return False\n",
                "test": "def check(candidate):\n    assert candidate([]) == False\n    assert candidate([1, 2, -3, 1, 2, -3]) == False\n    assert candidate([1, 2, -4, 5, 6]) == True\n    assert candidate([1, 2, -10, 1, 2, 3]) == True\n    assert candidate([1, 3, -5, 2, 5]) == True\n    assert candidate([1, 2, -3, 1, 3]) == False\n",
                "entry_point": "below_zero"
            },
            {
                "task_id": "HumanEval/4",
                "prompt": "def mean_absolute_deviation(numbers: List[float]) -> float:\n    \"\"\" For a given list of input numbers, calculate Mean Absolute Deviation\n    around the mean of this dataset.\n    Mean Absolute Deviation is the average absolute difference between each\n    element and a centerpoint (mean in this case):\n    MAD = average | x - x_mean |\n    >>> mean_absolute_deviation([1.0, 2.0, 3.0, 4.0])\n    1.0\n    \"\"\"\n",
                "canonical_solution": "    mean = sum(numbers) / len(numbers)\n    return sum(abs(x - mean) for x in numbers) / len(numbers)\n",
                "test": "def check(candidate):\n    assert abs(candidate([1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-6\n    assert abs(candidate([1.0, 2.0, 3.0]) - 2.0/3.0) < 1e-6\n    assert abs(candidate([1.0, 2.0]) - 0.5) < 1e-6\n    assert abs(candidate([1.0]) - 0.0) < 1e-6\n",
                "entry_point": "mean_absolute_deviation"
            }
        ]
        
        # Cache the dataset
        with open(self.humaneval_cache, 'w') as f:
            json.dump(humaneval_problems, f, indent=2)
        
        return humaneval_problems
    
    async def load_securityeval_dataset(self) -> List[Dict[str, Any]]:
        """Load SecurityEval dataset (simulated security-focused code problems)"""
        if self.securityeval_cache.exists():
            with open(self.securityeval_cache, 'r') as f:
                return json.load(f)
        
        # Create simulated SecurityEval-style problems
        securityeval_problems = [
            {
                "task_id": "SecurityEval/0",
                "category": "input_validation",
                "prompt": "def validate_email(email: str) -> bool:\n    \"\"\" Validate email address securely, preventing injection attacks.\n    Should return True for valid emails, False for invalid ones.\n    Must be secure against various injection attempts.\n    >>> validate_email('user@example.com')\n    True\n    >>> validate_email('invalid.email')\n    False\n    \"\"\"\n",
                "secure_solution": "    import re\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    if not isinstance(email, str) or len(email) > 254:\n        return False\n    return bool(re.match(pattern, email.strip()))\n",
                "vulnerabilities": ["injection", "regex_dos", "buffer_overflow"],
                "test_cases": [
                    {"input": "user@example.com", "expected": True, "type": "valid"},
                    {"input": "invalid.email", "expected": False, "type": "invalid"},
                    {"input": "'; DROP TABLE users; --", "expected": False, "type": "sql_injection"},
                    {"input": "<script>alert('xss')</script>@evil.com", "expected": False, "type": "xss"},
                    {"input": "a" * 1000 + "@example.com", "expected": False, "type": "buffer_overflow"}
                ],
                "security_weight": 0.9
            },
            {
                "task_id": "SecurityEval/1",
                "category": "authentication",
                "prompt": "def hash_password(password: str, salt: str = None) -> str:\n    \"\"\" Securely hash a password using a strong hashing algorithm.\n    Should be resistant to rainbow table and brute force attacks.\n    >>> len(hash_password('mypassword')) > 50\n    True\n    \"\"\"\n",
                "secure_solution": "    import hashlib\n    import secrets\n    if salt is None:\n        salt = secrets.token_hex(32)\n    combined = salt + password\n    for _ in range(100000):  # PBKDF2-like iteration\n        combined = hashlib.sha256(combined.encode()).hexdigest()\n    return salt + ':' + combined\n",
                "vulnerabilities": ["weak_crypto", "timing_attack", "salt_reuse"],
                "test_cases": [
                    {"input": "password123", "expected_length": 129, "type": "length_check"},
                    {"input": "", "expected_behavior": "handle_empty", "type": "edge_case"},
                    {"input": "a" * 1000, "expected_behavior": "handle_long", "type": "long_input"}
                ],
                "security_weight": 0.95
            },
            {
                "task_id": "SecurityEval/2",
                "category": "file_operations",
                "prompt": "def safe_file_read(filepath: str, base_dir: str = '/safe/') -> str:\n    \"\"\" Safely read a file, preventing path traversal attacks.\n    Should only allow reading files within the base directory.\n    >>> safe_file_read('data.txt', '/safe/')\n    'file content'\n    \"\"\"\n",
                "secure_solution": "    import os\n    import os.path\n    \n    # Normalize and resolve paths\n    base_dir = os.path.abspath(base_dir)\n    requested_path = os.path.abspath(os.path.join(base_dir, filepath))\n    \n    # Check if the resolved path is within base directory\n    if not requested_path.startswith(base_dir):\n        raise ValueError('Path traversal attempt detected')\n    \n    if not os.path.exists(requested_path):\n        raise FileNotFoundError('File not found')\n    \n    with open(requested_path, 'r', encoding='utf-8') as f:\n        return f.read()\n",
                "vulnerabilities": ["path_traversal", "directory_traversal", "symlink_attack"],
                "test_cases": [
                    {"input": "../../../etc/passwd", "expected": "error", "type": "path_traversal"},
                    {"input": "..\\..\\..\\windows\\system32\\config\\sam", "expected": "error", "type": "windows_traversal"},
                    {"input": "valid_file.txt", "expected": "success", "type": "valid_access"}
                ],
                "security_weight": 0.85
            },
            {
                "task_id": "SecurityEval/3",
                "category": "sql_operations",
                "prompt": "def get_user_data(user_id: str, db_connection) -> dict:\n    \"\"\" Retrieve user data from database safely.\n    Must prevent SQL injection attacks.\n    >>> get_user_data('123', mock_db)\n    {'user_id': '123', 'name': 'John'}\n    \"\"\"\n",
                "secure_solution": "    # Use parameterized queries\n    query = 'SELECT * FROM users WHERE user_id = ?'\n    cursor = db_connection.cursor()\n    cursor.execute(query, (user_id,))\n    result = cursor.fetchone()\n    return dict(result) if result else None\n",
                "vulnerabilities": ["sql_injection", "blind_sql_injection", "union_injection"],
                "test_cases": [
                    {"input": "1; DROP TABLE users; --", "expected": "safe_handling", "type": "sql_injection"},
                    {"input": "1' UNION SELECT password FROM admin_users --", "expected": "safe_handling", "type": "union_injection"},
                    {"input": "123", "expected": "normal_result", "type": "valid_input"}
                ],
                "security_weight": 0.9
            },
            {
                "task_id": "SecurityEval/4",
                "category": "crypto_operations",
                "prompt": "def encrypt_sensitive_data(data: str, key: str = None) -> str:\n    \"\"\" Encrypt sensitive data using strong encryption.\n    Should use secure algorithms and proper key management.\n    >>> len(encrypt_sensitive_data('secret')) > 20\n    True\n    \"\"\"\n",
                "secure_solution": "    from cryptography.fernet import Fernet\n    import base64\n    \n    if key is None:\n        key = Fernet.generate_key()\n    \n    f = Fernet(key)\n    encrypted = f.encrypt(data.encode())\n    return base64.b64encode(encrypted).decode()\n",
                "vulnerabilities": ["weak_encryption", "key_reuse", "ecb_mode"],
                "test_cases": [
                    {"input": "sensitive_data", "expected_min_length": 20, "type": "encryption_check"},
                    {"input": "", "expected": "handle_empty", "type": "edge_case"},
                    {"input": "a" * 10000, "expected": "handle_large", "type": "large_input"}
                ],
                "security_weight": 0.95
            }
        ]
        
        # Cache the dataset
        with open(self.securityeval_cache, 'w') as f:
            json.dump(securityeval_problems, f, indent=2)
        
        return securityeval_problems


class CodeExecutor:
    """Safely execute code for testing"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    async def execute_code_safely(self, code: str, test_code: str, entry_point: str) -> Dict[str, Any]:
        """Execute code with test cases in a safe environment"""
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Combine the generated code with test code
                full_code = f"""
import sys
import traceback
from typing import List

{code}

{test_code}

try:
    check({entry_point})
    print("ALL_TESTS_PASSED")
except Exception as e:
    print(f"TEST_FAILED: {{str(e)}}")
    traceback.print_exc()
"""
                f.write(full_code)
                f.flush()
                
                # Execute the code
                result = await self._run_python_code(f.name)
                
                # Clean up
                os.unlink(f.name)
                
                return result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }
    
    async def _run_python_code(self, filepath: str) -> Dict[str, Any]:
        """Run Python code file and capture output"""
        start_time = time.time()
        
        try:
            # Use subprocess to run the code safely
            process = await asyncio.create_subprocess_exec(
                'python', filepath,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            success = 'ALL_TESTS_PASSED' in output and process.returncode == 0
            
            return {
                'success': success,
                'output': output,
                'execution_time': execution_time,
                'return_code': process.returncode
            }
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Execution timeout',
                'output': '',
                'execution_time': self.timeout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': time.time() - start_time
            }


class SecurityAnalyzer:
    """Analyze code for security vulnerabilities"""
    
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
    
    def analyze_code_security(self, code: str) -> Dict[str, Any]:
        """Analyze code for security vulnerabilities"""
        vulnerabilities = []
        security_score = 100.0
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    vulnerability = {
                        'type': vuln_type,
                        'pattern': pattern,
                        'line': line_num,
                        'code_snippet': match.group(),
                        'severity': self._get_severity(vuln_type),
                        'description': self._get_vulnerability_description(vuln_type)
                    }
                    vulnerabilities.append(vulnerability)
                    
                    # Reduce security score based on severity
                    severity_impact = {
                        'critical': 25,
                        'high': 15,
                        'medium': 10,
                        'low': 5
                    }
                    security_score -= severity_impact.get(vulnerability['severity'], 5)
        
        security_score = max(0, security_score)
        
        return {
            'vulnerabilities': vulnerabilities,
            'security_score': security_score,
            'total_vulnerabilities': len(vulnerabilities),
            'severity_breakdown': self._get_severity_breakdown(vulnerabilities)
        }
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for vulnerability detection"""
        return {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'\.format\s*\(',
                r'f["\'].*\{.*\}.*["\'].*WHERE',
                r'query\s*=.*\+.*input',
                r'cursor\.execute\s*\([^?].*\+',
            ],
            'xss': [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'eval\s*\(',
                r'outerHTML\s*=',
                r'insertAdjacentHTML',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{3,}["\']',
                r'api_key\s*=\s*["\'][^"\']{10,}["\']',
                r'secret\s*=\s*["\'][^"\']{8,}["\']',
                r'token\s*=\s*["\'][^"\']{10,}["\']',
            ],
            'insecure_random': [
                r'random\.random\(',
                r'Math\.random\(',
                r'random\.randint\(',
                r'random\.choice\(',
            ],
            'path_traversal': [
                r'open\s*\(\s*.*\+.*\)',
                r'file\s*\(\s*.*\+.*\)',
                r'os\.path\.join\s*\([^)]*\+',
                r'\.\./',
                r'\.\.\\\\'
            ],
            'weak_crypto': [
                r'hashlib\.md5\(',
                r'hashlib\.sha1\(',
                r'DES\(',
                r'RC4\(',
            ],
            'unsafe_deserialization': [
                r'pickle\.loads\(',
                r'yaml\.load\(',
                r'eval\s*\(',
                r'exec\s*\(',
            ]
        }
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            'sql_injection': 'critical',
            'xss': 'high',
            'hardcoded_secrets': 'high',
            'insecure_random': 'medium',
            'path_traversal': 'high',
            'weak_crypto': 'medium',
            'unsafe_deserialization': 'critical'
        }
        return severity_map.get(vuln_type, 'medium')
    
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        """Get description for vulnerability type"""
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability - use parameterized queries',
            'xss': 'Cross-site scripting vulnerability - sanitize user input',
            'hardcoded_secrets': 'Hardcoded credential detected - use environment variables',
            'insecure_random': 'Insecure random number generation - use cryptographically secure random',
            'path_traversal': 'Path traversal vulnerability - validate and sanitize file paths',
            'weak_crypto': 'Weak cryptographic algorithm - use stronger algorithms',
            'unsafe_deserialization': 'Unsafe deserialization - validate input before deserializing'
        }
        return descriptions.get(vuln_type, 'Security vulnerability detected')
    
    def _get_severity_breakdown(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of vulnerabilities by severity"""
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'medium')
            breakdown[severity] += 1
        return breakdown


class EvaluationEngine(BaseAgent):
    """Comprehensive code evaluation engine"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.dataset_manager = DatasetManager()
        self.code_executor = CodeExecutor()
        self.security_analyzer = SecurityAnalyzer()
        
    async def _setup_capabilities(self):
        """Setup evaluation capabilities"""
        self.capabilities = {
            'evaluate_humaneval': AgentCapability(
                name='evaluate_humaneval',
                description='Evaluate code against HumanEval dataset',
                input_schema={
                    'code': 'string',
                    'problem_ids': 'array (optional)'
                },
                output_schema={
                    'total_tests': 'number',
                    'passed_tests': 'number',
                    'correctness_score': 'number',
                    'detailed_results': 'array'
                }
            ),
            'evaluate_securityeval': AgentCapability(
                name='evaluate_securityeval',
                description='Evaluate code against SecurityEval dataset',
                input_schema={
                    'code': 'string',
                    'security_categories': 'array (optional)'
                },
                output_schema={
                    'security_score': 'number',
                    'vulnerabilities': 'array',
                    'passed_security_tests': 'number',
                    'total_security_tests': 'number'
                }
            ),
            'comprehensive_evaluation': AgentCapability(
                name='comprehensive_evaluation',
                description='Run comprehensive evaluation including correctness, security, and performance',
                input_schema={
                    'code': 'string',
                    'language': 'string',
                    'evaluation_config': 'object (optional)'
                },
                output_schema={
                    'overall_score': 'number',
                    'correctness_score': 'number',
                    'security_score': 'number',
                    'performance_score': 'number',
                    'detailed_results': 'object'
                }
            )
        }
    
    async def _load_models(self):
        """Load evaluation datasets and models"""
        self.humaneval_dataset = await self.dataset_manager.load_humaneval_dataset()
        self.securityeval_dataset = await self.dataset_manager.load_securityeval_dataset()
        
        self.logger.info(f"Loaded {len(self.humaneval_dataset)} HumanEval problems")
        self.logger.info(f"Loaded {len(self.securityeval_dataset)} SecurityEval problems")
    
    async def _setup_resources(self):
        """Setup evaluation resources"""
        pass
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an evaluation task"""
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        task_type = parameters.get('task_type', 'comprehensive_evaluation')
        
        if task_type == 'evaluate_humaneval':
            return await self._evaluate_humaneval(parameters)
        elif task_type == 'evaluate_securityeval':
            return await self._evaluate_securityeval(parameters)
        elif task_type == 'comprehensive_evaluation':
            return await self._comprehensive_evaluation(parameters)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _evaluate_humaneval(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate code against HumanEval dataset"""
        code = parameters.get('code', '')
        problem_ids = parameters.get('problem_ids', None)
        
        if not code:
            raise ValueError("No code provided for evaluation")
        
        # Select problems to test
        problems_to_test = self.humaneval_dataset
        if problem_ids:
            problems_to_test = [p for p in self.humaneval_dataset if p['task_id'] in problem_ids]
        
        results = []
        passed_tests = 0
        total_tests = len(problems_to_test)
        
        self.logger.info(f"Evaluating code against {total_tests} HumanEval problems")
        
        for problem in problems_to_test:
            # Extract function name from the code (simplified)
            function_name = problem['entry_point']
            
            # Check if the function exists in the provided code
            if function_name not in code:
                results.append({
                    'task_id': problem['task_id'],
                    'status': 'failed',
                    'error': f'Function {function_name} not found in code',
                    'execution_time': 0
                })
                continue
            
            # Execute the test
            execution_result = await self.code_executor.execute_code_safely(
                code, problem['test'], function_name
            )
            
            test_result = {
                'task_id': problem['task_id'],
                'status': 'passed' if execution_result['success'] else 'failed',
                'execution_time': execution_result['execution_time'],
                'output': execution_result.get('output', ''),
                'error': execution_result.get('error', '')
            }
            
            if execution_result['success']:
                passed_tests += 1
            
            results.append(test_result)
        
        correctness_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'correctness_score': correctness_score,
            'detailed_results': results,
            'evaluation_type': 'humaneval'
        }
    
    async def _evaluate_securityeval(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate code against SecurityEval dataset"""
        code = parameters.get('code', '')
        security_categories = parameters.get('security_categories', None)
        
        if not code:
            raise ValueError("No code provided for security evaluation")
        
        # Select security problems to test
        problems_to_test = self.securityeval_dataset
        if security_categories:
            problems_to_test = [p for p in self.securityeval_dataset 
                              if p['category'] in security_categories]
        
        # Run static security analysis
        security_analysis = self.security_analyzer.analyze_code_security(code)
        
        # Run security-specific tests
        security_test_results = []
        passed_security_tests = 0
        total_security_tests = len(problems_to_test)
        
        for problem in problems_to_test:
            # Check if the code handles security requirements
            function_name = problem.get('entry_point', 'unknown')
            
            # Analyze if the code contains vulnerable patterns
            is_secure = True
            vulnerabilities_found = []
            
            for vuln_type in problem.get('vulnerabilities', []):
                patterns = self.security_analyzer.vulnerability_patterns.get(vuln_type, [])
                for pattern in patterns:
                    if re.search(pattern, code, re.IGNORECASE):
                        is_secure = False
                        vulnerabilities_found.append(vuln_type)
            
            test_result = {
                'task_id': problem['task_id'],
                'category': problem['category'],
                'status': 'passed' if is_secure else 'failed',
                'vulnerabilities_found': vulnerabilities_found,
                'security_weight': problem.get('security_weight', 1.0)
            }
            
            if is_secure:
                passed_security_tests += 1
            
            security_test_results.append(test_result)
        
        # Calculate weighted security score
        total_weight = sum(p.get('security_weight', 1.0) for p in problems_to_test)
        passed_weight = sum(r['security_weight'] for r in security_test_results if r['status'] == 'passed')
        weighted_security_score = (passed_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Combine with static analysis score
        final_security_score = (weighted_security_score + security_analysis['security_score']) / 2
        
        return {
            'security_score': final_security_score,
            'passed_security_tests': passed_security_tests,
            'total_security_tests': total_security_tests,
            'vulnerabilities': security_analysis['vulnerabilities'],
            'security_test_results': security_test_results,
            'static_analysis': security_analysis,
            'evaluation_type': 'securityeval'
        }
    
    async def _comprehensive_evaluation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive evaluation including all aspects"""
        code = parameters.get('code', '')
        language = parameters.get('language', 'python')
        evaluation_config = parameters.get('evaluation_config', {})
        
        start_time = time.time()
        
        # Run HumanEval evaluation
        humaneval_result = await self._evaluate_humaneval({'code': code})
        
        # Run SecurityEval evaluation
        securityeval_result = await self._evaluate_securityeval({'code': code})
        
        # Calculate performance score (based on execution times)
        performance_score = self._calculate_performance_score(humaneval_result['detailed_results'])
        
        # Calculate overall score
        weights = evaluation_config.get('weights', {
            'correctness': 0.4,
            'security': 0.4,
            'performance': 0.2
        })
        
        overall_score = (
            humaneval_result['correctness_score'] * weights['correctness'] +
            securityeval_result['security_score'] * weights['security'] +
            performance_score * weights['performance']
        )
        
        total_execution_time = time.time() - start_time
        
        return {
            'overall_score': overall_score,
            'correctness_score': humaneval_result['correctness_score'],
            'security_score': securityeval_result['security_score'],
            'performance_score': performance_score,
            'execution_time': total_execution_time,
            'detailed_results': {
                'humaneval': humaneval_result,
                'securityeval': securityeval_result,
                'performance_metrics': self._get_performance_metrics(humaneval_result['detailed_results'])
            },
            'evaluation_summary': {
                'total_tests': humaneval_result['total_tests'] + securityeval_result['total_security_tests'],
                'passed_tests': humaneval_result['passed_tests'] + securityeval_result['passed_security_tests'],
                'total_vulnerabilities': len(securityeval_result['vulnerabilities']),
                'language': language,
                'evaluation_config': evaluation_config
            }
        }
    
    def _calculate_performance_score(self, execution_results: List[Dict[str, Any]]) -> float:
        """Calculate performance score based on execution times"""
        if not execution_results:
            return 0.0
        
        execution_times = [r['execution_time'] for r in execution_results if r['status'] == 'passed']
        
        if not execution_times:
            return 0.0
        
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        # Performance score based on execution time (lower is better)
        # Assuming 0.1s is excellent, 1.0s is acceptable
        if avg_execution_time <= 0.1:
            return 100.0
        elif avg_execution_time <= 1.0:
            return max(0, 100 - (avg_execution_time - 0.1) * 100)
        else:
            return max(0, 50 - (avg_execution_time - 1.0) * 10)
    
    def _get_performance_metrics(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        execution_times = [r['execution_time'] for r in execution_results]
        
        if not execution_times:
            return {}
        
        return {
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'max_execution_time': max(execution_times),
            'min_execution_time': min(execution_times),
            'total_execution_time': sum(execution_times),
            'successful_executions': len([r for r in execution_results if r['status'] == 'passed'])
        }

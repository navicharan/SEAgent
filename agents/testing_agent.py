"""
Testing Agent - Unified testing for functional correctness, security compliance, and reliability
Enhanced with DeepSeek-Coder V2 for AI-powered test generation
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent, AgentCapability
from config.deepseek_client import DeepSeekClient

# Try to import for DeepSeek compatibility
try:
    import openai
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False


class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REGRESSION = "regression"
    END_TO_END = "end_to_end"


@dataclass
class TestResult:
    test_id: str
    test_type: TestType
    name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    error_message: str = None
    coverage: float = None


class TestingAgent(BaseAgent):
    """Agent responsible for comprehensive testing across functional, security, and performance domains"""
    
    async def _setup_capabilities(self):
        """Setup testing capabilities"""
        self.capabilities = {
            'functional_testing': AgentCapability(
                name='functional_testing',
                description='Execute functional and unit tests',
                input_schema={
                    'source_code': 'string',
                    'test_framework': 'string',
                    'test_files': 'array (optional)'
                },
                output_schema={
                    'test_results': 'array',
                    'coverage_report': 'object',
                    'summary': 'object'
                }
            ),
            'security_testing': AgentCapability(
                name='security_testing',
                description='Execute security and vulnerability tests',
                input_schema={
                    'application_url': 'string (optional)',
                    'source_code': 'string (optional)',
                    'security_test_suite': 'string'
                },
                output_schema={
                    'security_results': 'array',
                    'vulnerabilities_found': 'array',
                    'security_score': 'number'
                }
            ),
            'performance_testing': AgentCapability(
                name='performance_testing',
                description='Execute performance and load tests',
                input_schema={
                    'target_endpoint': 'string',
                    'performance_config': 'object',
                    'test_duration': 'number'
                },
                output_schema={
                    'performance_results': 'object',
                    'benchmarks': 'object',
                    'recommendations': 'array'
                }
            ),
            'test_generation': AgentCapability(
                name='test_generation',
                description='Generate comprehensive test suites',
                input_schema={
                    'source_code': 'string',
                    'test_types': 'array',
                    'coverage_target': 'number'
                },
                output_schema={
                    'generated_tests': 'object',
                    'test_files': 'array',
                    'estimated_coverage': 'number'
                }
            )
        }
    
    async def _load_models(self):
        """Load testing models and frameworks"""
        # Load test frameworks configurations
        self.test_frameworks = await self._load_test_frameworks()
        
        # Load security testing tools
        self.security_tools = await self._load_security_testing_tools()
        
        # Load performance testing tools
        self.performance_tools = await self._load_performance_testing_tools()
        
        # Load test generation templates
        self.test_templates = await self._load_test_templates()
    
    async def _setup_resources(self):
        """Setup testing tools and environments"""
        # Setup test runners
        self.test_runners = {
            'pytest': await self._setup_pytest(),
            'jest': await self._setup_jest(),
            'junit': await self._setup_junit(),
            'mocha': await self._setup_mocha()
        }
        
        # Setup security testing tools
        self.security_scanners = {
            'zap': await self._setup_zap_scanner(),
            'nikto': await self._setup_nikto_scanner(),
            'nmap': await self._setup_nmap_scanner()
        }
        
        # Setup performance testing tools
        self.performance_testers = {
            'locust': await self._setup_locust(),
            'jmeter': await self._setup_jmeter(),
            'artillery': await self._setup_artillery()
        }
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a testing task"""
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        task_type = parameters.get('task_type', 'functional_testing')
        
        if task_type == 'functional_testing':
            return await self._functional_testing(parameters)
        elif task_type == 'security_testing':
            return await self._security_testing(parameters)
        elif task_type == 'performance_testing':
            return await self._performance_testing(parameters)
        elif task_type == 'test_generation':
            return await self._test_generation(parameters)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _functional_testing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute functional and unit tests"""
        source_code = parameters.get('source_code', '')
        test_framework = parameters.get('test_framework', 'pytest')
        test_files = parameters.get('test_files', [])
        
        self.logger.info(f"Running functional tests with {test_framework}")
        
        # Simulate test execution
        await asyncio.sleep(1.5)
        
        test_results = await self._run_functional_tests(source_code, test_framework, test_files)
        coverage_report = await self._generate_coverage_report(source_code, test_results)
        summary = await self._generate_test_summary(test_results)
        
        return {
            'test_results': test_results,
            'coverage_report': coverage_report,
            'summary': summary,
            'framework': test_framework,
            'execution_time': 1.5
        }
    
    async def _security_testing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security and vulnerability tests"""
        application_url = parameters.get('application_url', '')
        source_code = parameters.get('source_code', '')
        security_test_suite = parameters.get('security_test_suite', 'comprehensive')
        
        self.logger.info(f"Running {security_test_suite} security tests")
        
        # Simulate security testing
        await asyncio.sleep(2)
        
        security_results = await self._run_security_tests(application_url, source_code, security_test_suite)
        vulnerabilities = await self._extract_vulnerabilities(security_results)
        security_score = await self._calculate_security_score(vulnerabilities)
        
        return {
            'security_results': security_results,
            'vulnerabilities_found': vulnerabilities,
            'security_score': security_score,
            'test_suite': security_test_suite,
            'scan_timestamp': asyncio.get_event_loop().time()
        }
    
    async def _performance_testing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance and load tests"""
        target_endpoint = parameters.get('target_endpoint', 'http://localhost:8000')
        performance_config = parameters.get('performance_config', {})
        test_duration = parameters.get('test_duration', 60)
        
        self.logger.info(f"Running performance tests for {test_duration} seconds")
        
        # Simulate performance testing
        await asyncio.sleep(2.5)
        
        performance_results = await self._run_performance_tests(target_endpoint, performance_config, test_duration)
        benchmarks = await self._generate_performance_benchmarks(performance_results)
        recommendations = await self._generate_performance_recommendations(performance_results)
        
        return {
            'performance_results': performance_results,
            'benchmarks': benchmarks,
            'recommendations': recommendations,
            'test_duration': test_duration,
            'target_endpoint': target_endpoint
        }
    
    async def _test_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test suites"""
        source_code = parameters.get('source_code', '')
        test_types = parameters.get('test_types', ['unit', 'integration'])
        coverage_target = parameters.get('coverage_target', 80)
        
        self.logger.info(f"Generating tests for types: {test_types}")
        
        # Simulate test generation
        await asyncio.sleep(1)
        
        generated_tests = await self._generate_test_suite(source_code, test_types, coverage_target)
        test_files = await self._create_test_files(generated_tests)
        estimated_coverage = await self._estimate_test_coverage(generated_tests, source_code)
        
        return {
            'generated_tests': generated_tests,
            'test_files': test_files,
            'estimated_coverage': estimated_coverage,
            'test_types': test_types,
            'coverage_target': coverage_target
        }
    
    async def _run_functional_tests(self, source_code: str, framework: str, test_files: List[str]) -> List[Dict[str, Any]]:
        """Run functional tests and return results"""
        test_results = []
        
        # Simulate running different types of tests
        test_cases = [
            {'name': 'test_basic_functionality', 'type': 'unit'},
            {'name': 'test_edge_cases', 'type': 'unit'},
            {'name': 'test_error_handling', 'type': 'unit'},
            {'name': 'test_integration_flow', 'type': 'integration'},
            {'name': 'test_api_endpoints', 'type': 'integration'},
            {'name': 'test_database_operations', 'type': 'integration'}
        ]
        
        for i, test_case in enumerate(test_cases):
            # Simulate test execution with some failures
            status = 'passed'
            error_message = None
            duration = 0.1 + (i * 0.05)
            
            # Simulate some test failures
            if i == 2:  # Error handling test fails
                status = 'failed'
                error_message = 'AssertionError: Expected exception not raised'
            elif i == 4:  # API test has issues
                status = 'failed'
                error_message = 'ConnectionError: Unable to connect to test server'
            
            test_results.append({
                'test_id': f'test_{i+1}',
                'name': test_case['name'],
                'type': test_case['type'],
                'status': status,
                'duration': duration,
                'error_message': error_message,
                'framework': framework
            })
        
        return test_results
    
    async def _generate_coverage_report(self, source_code: str, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate code coverage report"""
        # Simulate coverage analysis
        total_lines = len(source_code.split('\n'))
        covered_lines = int(total_lines * 0.75)  # Simulate 75% coverage
        
        passed_tests = len([t for t in test_results if t['status'] == 'passed'])
        total_tests = len(test_results)
        
        return {
            'line_coverage': {
                'total_lines': total_lines,
                'covered_lines': covered_lines,
                'percentage': (covered_lines / total_lines) * 100 if total_lines > 0 else 0
            },
            'branch_coverage': {
                'total_branches': 20,
                'covered_branches': 15,
                'percentage': 75.0
            },
            'function_coverage': {
                'total_functions': 8,
                'covered_functions': 6,
                'percentage': 75.0
            },
            'test_coverage': {
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            }
        }
    
    async def _generate_test_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test execution summary"""
        total_tests = len(test_results)
        passed_tests = len([t for t in test_results if t['status'] == 'passed'])
        failed_tests = len([t for t in test_results if t['status'] == 'failed'])
        skipped_tests = len([t for t in test_results if t['status'] == 'skipped'])
        
        total_duration = sum(t['duration'] for t in test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration': total_duration,
            'average_duration': total_duration / total_tests if total_tests > 0 else 0,
            'status': 'success' if failed_tests == 0 else 'failure'
        }
    
    async def _run_security_tests(self, application_url: str, source_code: str, test_suite: str) -> List[Dict[str, Any]]:
        """Run security tests"""
        security_results = []
        
        # Different security test categories
        security_tests = {
            'comprehensive': [
                'SQL Injection Test',
                'XSS Vulnerability Test',
                'CSRF Protection Test',
                'Authentication Bypass Test',
                'Authorization Test',
                'Input Validation Test',
                'SSL/TLS Configuration Test',
                'Sensitive Data Exposure Test'
            ],
            'basic': [
                'SQL Injection Test',
                'XSS Vulnerability Test',
                'Input Validation Test'
            ],
            'web_app': [
                'SQL Injection Test',
                'XSS Vulnerability Test',
                'CSRF Protection Test',
                'Authentication Test',
                'Session Management Test'
            ]
        }
        
        tests_to_run = security_tests.get(test_suite, security_tests['basic'])
        
        for i, test_name in enumerate(tests_to_run):
            # Simulate security test execution
            status = 'passed'
            vulnerability_level = 'none'
            details = f'{test_name} completed successfully'
            
            # Simulate finding some vulnerabilities
            if 'SQL Injection' in test_name:
                status = 'failed'
                vulnerability_level = 'high'
                details = 'Potential SQL injection vulnerability detected in user input handling'
            elif 'XSS' in test_name and i % 3 == 0:
                status = 'warning'
                vulnerability_level = 'medium'
                details = 'Potential XSS vulnerability in output rendering'
            elif 'Authentication' in test_name:
                status = 'warning'
                vulnerability_level = 'low'
                details = 'Weak password policy detected'
            
            security_results.append({
                'test_id': f'sec_test_{i+1}',
                'test_name': test_name,
                'status': status,
                'vulnerability_level': vulnerability_level,
                'details': details,
                'duration': 0.5 + (i * 0.1)
            })
        
        return security_results
    
    async def _extract_vulnerabilities(self, security_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract vulnerabilities from security test results"""
        vulnerabilities = []
        
        for result in security_results:
            if result['status'] in ['failed', 'warning'] and result['vulnerability_level'] != 'none':
                vulnerabilities.append({
                    'type': result['test_name'].replace(' Test', ''),
                    'severity': result['vulnerability_level'],
                    'description': result['details'],
                    'test_id': result['test_id'],
                    'remediation': self._get_vulnerability_remediation(result['test_name'])
                })
        
        return vulnerabilities
    
    async def _calculate_security_score(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        """Calculate overall security score"""
        if not vulnerabilities:
            return 100.0
        
        severity_weights = {
            'critical': 25,
            'high': 15,
            'medium': 10,
            'low': 5
        }
        
        total_deduction = sum(severity_weights.get(vuln['severity'], 5) for vuln in vulnerabilities)
        security_score = max(0, 100 - total_deduction)
        
        return security_score
    
    async def _run_performance_tests(self, endpoint: str, config: Dict[str, Any], duration: int) -> Dict[str, Any]:
        """Run performance tests"""
        # Simulate performance test execution
        concurrent_users = config.get('concurrent_users', 10)
        ramp_up_time = config.get('ramp_up_time', 30)
        
        # Simulate metrics collection
        return {
            'response_times': {
                'min': 45,
                'max': 1250,
                'average': 185,
                'p50': 150,
                'p90': 350,
                'p95': 450,
                'p99': 850
            },
            'throughput': {
                'requests_per_second': 85,
                'requests_per_minute': 5100,
                'total_requests': duration * 85
            },
            'error_metrics': {
                'total_errors': 12,
                'error_rate': 2.3,  # percentage
                'timeout_errors': 5,
                'connection_errors': 7
            },
            'resource_utilization': {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'network_io': 23.4
            },
            'concurrent_users': concurrent_users,
            'test_duration': duration
        }
    
    async def _generate_performance_benchmarks(self, performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance benchmarks"""
        response_times = performance_results['response_times']
        throughput = performance_results['throughput']
        error_metrics = performance_results['error_metrics']
        
        # Define performance thresholds
        benchmarks = {
            'response_time_benchmarks': {
                'excellent': response_times['average'] < 100,
                'good': response_times['average'] < 200,
                'acceptable': response_times['average'] < 500,
                'poor': response_times['average'] >= 500,
                'current_rating': self._get_performance_rating(response_times['average'])
            },
            'throughput_benchmarks': {
                'target_rps': 100,
                'achieved_rps': throughput['requests_per_second'],
                'throughput_ratio': throughput['requests_per_second'] / 100,
                'meets_target': throughput['requests_per_second'] >= 100
            },
            'reliability_benchmarks': {
                'target_error_rate': 1.0,  # percentage
                'actual_error_rate': error_metrics['error_rate'],
                'reliability_score': max(0, 100 - error_metrics['error_rate']),
                'meets_target': error_metrics['error_rate'] <= 1.0
            }
        }
        
        return benchmarks
    
    async def _generate_performance_recommendations(self, performance_results: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        response_times = performance_results['response_times']
        throughput = performance_results['throughput']
        error_metrics = performance_results['error_metrics']
        resource_usage = performance_results['resource_utilization']
        
        # Response time recommendations
        if response_times['average'] > 500:
            recommendations.append('Optimize response times - average exceeds 500ms')
        if response_times['p99'] > 2000:
            recommendations.append('Address tail latency - 99th percentile exceeds 2s')
        
        # Throughput recommendations
        if throughput['requests_per_second'] < 50:
            recommendations.append('Improve throughput - current RPS is below target')
        
        # Error rate recommendations
        if error_metrics['error_rate'] > 5:
            recommendations.append('Reduce error rate - currently above acceptable threshold')
        if error_metrics['timeout_errors'] > 0:
            recommendations.append('Investigate timeout errors - may indicate performance bottlenecks')
        
        # Resource utilization recommendations
        if resource_usage['cpu_usage'] > 80:
            recommendations.append('High CPU usage detected - consider optimization or scaling')
        if resource_usage['memory_usage'] > 85:
            recommendations.append('High memory usage - review memory efficiency')
        
        # General recommendations
        if recommendations:
            recommendations.extend([
                'Implement caching strategies',
                'Consider database query optimization',
                'Review application architecture for bottlenecks',
                'Set up continuous performance monitoring'
            ])
        
        return recommendations
    
    async def _generate_test_suite(self, source_code: str, test_types: List[str], coverage_target: int) -> Dict[str, Any]:
        """Generate comprehensive test suite"""
        generated_tests = {}
        
        for test_type in test_types:
            if test_type == 'unit':
                generated_tests['unit_tests'] = await self._generate_unit_tests(source_code)
            elif test_type == 'integration':
                generated_tests['integration_tests'] = await self._generate_integration_tests(source_code)
            elif test_type == 'functional':
                generated_tests['functional_tests'] = await self._generate_functional_tests(source_code)
            elif test_type == 'security':
                generated_tests['security_tests'] = await self._generate_security_tests(source_code)
            elif test_type == 'performance':
                generated_tests['performance_tests'] = await self._generate_performance_tests(source_code)
        
        return generated_tests
    
    async def _generate_unit_tests(self, source_code: str) -> List[Dict[str, Any]]:
        """Generate unit tests for source code"""
        # Extract functions from source code (simplified)
        functions = re.findall(r'def (\w+)\s*\(', source_code)
        
        unit_tests = []
        for func in functions:
            unit_tests.extend([
                {
                    'test_name': f'test_{func}_basic',
                    'test_code': f'def test_{func}_basic():\n    result = {func}()\n    assert result is not None',
                    'description': f'Test basic functionality of {func}',
                    'test_type': 'unit'
                },
                {
                    'test_name': f'test_{func}_edge_cases',
                    'test_code': f'def test_{func}_edge_cases():\n    # Test edge cases\n    pass',
                    'description': f'Test edge cases for {func}',
                    'test_type': 'unit'
                }
            ])
        
        return unit_tests
    
    async def _generate_integration_tests(self, source_code: str) -> List[Dict[str, Any]]:
        """Generate integration tests"""
        return [
            {
                'test_name': 'test_api_integration',
                'test_code': 'def test_api_integration():\n    # Test API integration\n    pass',
                'description': 'Test API endpoint integration',
                'test_type': 'integration'
            },
            {
                'test_name': 'test_database_integration',
                'test_code': 'def test_database_integration():\n    # Test database operations\n    pass',
                'description': 'Test database integration',
                'test_type': 'integration'
            }
        ]
    
    async def _generate_functional_tests(self, source_code: str) -> List[Dict[str, Any]]:
        """Generate functional tests"""
        return [
            {
                'test_name': 'test_user_workflow',
                'test_code': 'def test_user_workflow():\n    # Test complete user workflow\n    pass',
                'description': 'Test end-to-end user workflow',
                'test_type': 'functional'
            }
        ]
    
    async def _generate_security_tests(self, source_code: str) -> List[Dict[str, Any]]:
        """Generate security tests"""
        return [
            {
                'test_name': 'test_input_validation',
                'test_code': 'def test_input_validation():\n    # Test input validation\n    pass',
                'description': 'Test input validation security',
                'test_type': 'security'
            },
            {
                'test_name': 'test_authentication',
                'test_code': 'def test_authentication():\n    # Test authentication mechanisms\n    pass',
                'description': 'Test authentication security',
                'test_type': 'security'
            }
        ]
    
    async def _generate_performance_tests(self, source_code: str) -> List[Dict[str, Any]]:
        """Generate performance tests"""
        return [
            {
                'test_name': 'test_response_time',
                'test_code': 'def test_response_time():\n    # Test response time requirements\n    pass',
                'description': 'Test response time performance',
                'test_type': 'performance'
            }
        ]
    
    async def _create_test_files(self, generated_tests: Dict[str, Any]) -> List[str]:
        """Create test files from generated tests"""
        test_files = []
        
        for test_category, tests in generated_tests.items():
            filename = f"test_{test_category.replace('_tests', '')}.py"
            test_files.append(filename)
        
        return test_files
    
    async def _estimate_test_coverage(self, generated_tests: Dict[str, Any], source_code: str) -> float:
        """Estimate test coverage from generated tests"""
        total_tests = sum(len(tests) for tests in generated_tests.values())
        source_lines = len(source_code.split('\n'))
        
        # Simple estimation: more tests = higher coverage
        estimated_coverage = min(total_tests * 10, 95)  # Cap at 95%
        
        return estimated_coverage
    
    def _get_vulnerability_remediation(self, test_name: str) -> str:
        """Get remediation advice for vulnerability"""
        remediation_map = {
            'SQL Injection Test': 'Use parameterized queries and input validation',
            'XSS Vulnerability Test': 'Implement output encoding and CSP headers',
            'CSRF Protection Test': 'Implement CSRF tokens and SameSite cookies',
            'Authentication Bypass Test': 'Review authentication logic and access controls',
            'Authorization Test': 'Implement proper role-based access control',
            'Input Validation Test': 'Add comprehensive input validation and sanitization',
            'SSL/TLS Configuration Test': 'Update SSL/TLS configuration and certificates',
            'Sensitive Data Exposure Test': 'Encrypt sensitive data and review data handling'
        }
        return remediation_map.get(test_name, 'Review security implementation')
    
    def _get_performance_rating(self, avg_response_time: float) -> str:
        """Get performance rating based on response time"""
        if avg_response_time < 100:
            return 'excellent'
        elif avg_response_time < 200:
            return 'good'
        elif avg_response_time < 500:
            return 'acceptable'
        else:
            return 'poor'
    
    # Placeholder methods for loading resources
    async def _load_test_frameworks(self) -> Dict[str, Any]:
        return {'frameworks_loaded': True}
    
    async def _load_security_testing_tools(self) -> Dict[str, Any]:
        return {'security_tools_loaded': True}
    
    async def _load_performance_testing_tools(self) -> Dict[str, Any]:
        return {'performance_tools_loaded': True}
    
    async def _load_test_templates(self) -> Dict[str, Any]:
        return {'templates_loaded': True}
    
    async def _setup_pytest(self) -> Dict[str, Any]:
        return {'runner': 'pytest', 'version': '7.4.3', 'available': True}
    
    async def _setup_jest(self) -> Dict[str, Any]:
        return {'runner': 'jest', 'version': '29.7.0', 'available': True}
    
    async def _setup_junit(self) -> Dict[str, Any]:
        return {'runner': 'junit', 'version': '5.10.0', 'available': True}
    
    async def _setup_mocha(self) -> Dict[str, Any]:
        return {'runner': 'mocha', 'version': '10.2.0', 'available': True}
    
    async def _setup_zap_scanner(self) -> Dict[str, Any]:
        return {'scanner': 'zap', 'version': '2.14.0', 'available': False}
    
    async def _setup_nikto_scanner(self) -> Dict[str, Any]:
        return {'scanner': 'nikto', 'version': '2.5.0', 'available': False}
    
    async def _setup_nmap_scanner(self) -> Dict[str, Any]:
        return {'scanner': 'nmap', 'version': '7.94', 'available': False}
    
    async def _setup_locust(self) -> Dict[str, Any]:
        return {'tool': 'locust', 'version': '2.17.0', 'available': True}
    
    async def _setup_jmeter(self) -> Dict[str, Any]:
        return {'tool': 'jmeter', 'version': '5.6.2', 'available': False}
    
    async def _setup_artillery(self) -> Dict[str, Any]:
        return {'tool': 'artillery', 'version': '2.0.0', 'available': True}

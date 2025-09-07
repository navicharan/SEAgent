"""
Performance Agent - Runtime performance analysis and optimization
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentCapability


@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    threshold: float
    status: str  # 'good', 'warning', 'critical'


class PerformanceAgent(BaseAgent):
    """Agent responsible for performance analysis and optimization"""
    
    async def _setup_capabilities(self):
        """Setup performance analysis capabilities"""
        self.capabilities = {
            'performance_analysis': AgentCapability(
                name='performance_analysis',
                description='Analyze code performance and resource usage',
                input_schema={
                    'source_code': 'string',
                    'language': 'string',
                    'test_data': 'object (optional)'
                },
                output_schema={
                    'metrics': 'object',
                    'bottlenecks': 'array',
                    'recommendations': 'array'
                }
            ),
            'load_testing': AgentCapability(
                name='load_testing',
                description='Perform load testing and scalability analysis',
                input_schema={
                    'endpoint': 'string',
                    'load_config': 'object',
                    'duration': 'number'
                },
                output_schema={
                    'load_metrics': 'object',
                    'scalability_analysis': 'object',
                    'performance_under_load': 'object'
                }
            ),
            'memory_profiling': AgentCapability(
                name='memory_profiling',
                description='Profile memory usage and detect memory leaks',
                input_schema={
                    'source_code': 'string',
                    'execution_time': 'number',
                    'profiling_options': 'object'
                },
                output_schema={
                    'memory_profile': 'object',
                    'memory_leaks': 'array',
                    'optimization_suggestions': 'array'
                }
            ),
            'code_optimization': AgentCapability(
                name='code_optimization',
                description='Suggest and apply performance optimizations',
                input_schema={
                    'source_code': 'string',
                    'performance_targets': 'object',
                    'optimization_level': 'string'
                },
                output_schema={
                    'optimized_code': 'string',
                    'optimizations_applied': 'array',
                    'performance_improvement': 'object'
                }
            )
        }
    
    async def _load_models(self):
        """Load performance analysis models"""
        # Load performance benchmarks and thresholds
        self.performance_benchmarks = await self._load_performance_benchmarks()
        self.optimization_patterns = await self._load_optimization_patterns()
        
        # Load profiling configurations
        self.profiling_configs = await self._load_profiling_configs()
    
    async def _setup_resources(self):
        """Setup performance monitoring tools"""
        # Setup profiling tools
        self.profilers = {
            'python': await self._setup_python_profiler(),
            'javascript': await self._setup_javascript_profiler(),
            'java': await self._setup_java_profiler()
        }
        
        # Setup load testing tools
        self.load_testers = await self._setup_load_testing_tools()
        
        # Setup system monitoring
        self.system_monitor = await self._setup_system_monitor()
    
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a performance analysis task"""
        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")
        
        task_type = parameters.get('task_type', 'performance_analysis')
        
        if task_type == 'performance_analysis':
            return await self._performance_analysis(parameters)
        elif task_type == 'load_testing':
            return await self._load_testing(parameters)
        elif task_type == 'memory_profiling':
            return await self._memory_profiling(parameters)
        elif task_type == 'code_optimization':
            return await self._code_optimization(parameters)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _performance_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code performance"""
        source_code = parameters.get('source_code', '')
        language = parameters.get('language', 'python')
        test_data = parameters.get('test_data', {})
        
        self.logger.info(f"Analyzing performance for {language} code")
        
        # Simulate performance analysis
        await asyncio.sleep(1.5)
        
        metrics = await self._analyze_code_performance(source_code, language, test_data)
        bottlenecks = await self._identify_performance_bottlenecks(source_code, metrics)
        recommendations = await self._generate_performance_recommendations(bottlenecks, metrics)
        
        return {
            'metrics': metrics,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'analysis_timestamp': time.time(),
            'language': language
        }
    
    async def _load_testing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform load testing"""
        endpoint = parameters.get('endpoint', '')
        load_config = parameters.get('load_config', {})
        duration = parameters.get('duration', 60)
        
        self.logger.info(f"Performing load test on {endpoint} for {duration} seconds")
        
        # Simulate load testing
        await asyncio.sleep(2)
        
        load_metrics = await self._execute_load_test(endpoint, load_config, duration)
        scalability_analysis = await self._analyze_scalability(load_metrics)
        performance_under_load = await self._analyze_performance_under_load(load_metrics)
        
        return {
            'load_metrics': load_metrics,
            'scalability_analysis': scalability_analysis,
            'performance_under_load': performance_under_load,
            'test_duration': duration,
            'endpoint': endpoint
        }
    
    async def _memory_profiling(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Profile memory usage"""
        source_code = parameters.get('source_code', '')
        execution_time = parameters.get('execution_time', 10)
        profiling_options = parameters.get('profiling_options', {})
        
        self.logger.info(f"Profiling memory usage for {execution_time} seconds")
        
        # Simulate memory profiling
        await asyncio.sleep(1)
        
        memory_profile = await self._profile_memory_usage(source_code, execution_time)
        memory_leaks = await self._detect_memory_leaks(memory_profile)
        optimization_suggestions = await self._suggest_memory_optimizations(memory_profile, memory_leaks)
        
        return {
            'memory_profile': memory_profile,
            'memory_leaks': memory_leaks,
            'optimization_suggestions': optimization_suggestions,
            'profiling_duration': execution_time
        }
    
    async def _code_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code for performance"""
        source_code = parameters.get('source_code', '')
        performance_targets = parameters.get('performance_targets', {})
        optimization_level = parameters.get('optimization_level', 'moderate')
        
        self.logger.info(f"Optimizing code with {optimization_level} optimization level")
        
        # Simulate code optimization
        await asyncio.sleep(1.5)
        
        optimization_results = await self._optimize_code(source_code, performance_targets, optimization_level)
        
        return {
            'optimized_code': optimization_results['code'],
            'optimizations_applied': optimization_results['optimizations'],
            'performance_improvement': optimization_results['improvement'],
            'optimization_level': optimization_level
        }
    
    async def _analyze_code_performance(self, source_code: str, language: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code performance metrics"""
        # Simulate performance metrics collection
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        # Simulate code execution metrics
        simulated_metrics = {
            'execution_time': {
                'value': 1.25,
                'unit': 'seconds',
                'threshold': 2.0,
                'status': 'good'
            },
            'memory_usage': {
                'value': memory_info.percent,
                'unit': 'MB',
                'threshold': 500.0,
                'status': 'good' if memory_info.percent < 80 else 'warning'
            },
            'cpu_usage': {
                'value': cpu_percent,
                'unit': 'percent',
                'threshold': 80.0,
                'status': 'good' if cpu_percent < 70 else 'warning'
            },
            'algorithmic_complexity': {
                'value': self._estimate_complexity(source_code),
                'unit': 'big_o',
                'threshold': 3.0,  # O(n³) threshold
                'status': 'good'
            },
            'code_efficiency': {
                'value': self._calculate_code_efficiency(source_code),
                'unit': 'score',
                'threshold': 70.0,
                'status': 'good'
            }
        }
        
        return simulated_metrics
    
    async def _identify_performance_bottlenecks(self, source_code: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Check metrics for bottlenecks
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict) and 'status' in metric_data:
                if metric_data['status'] in ['warning', 'critical']:
                    bottlenecks.append({
                        'type': metric_name,
                        'severity': metric_data['status'],
                        'current_value': metric_data['value'],
                        'threshold': metric_data['threshold'],
                        'unit': metric_data['unit'],
                        'description': self._get_bottleneck_description(metric_name)
                    })
        
        # Analyze code patterns for bottlenecks
        code_bottlenecks = await self._analyze_code_patterns(source_code)
        bottlenecks.extend(code_bottlenecks)
        
        return bottlenecks
    
    async def _analyze_code_patterns(self, source_code: str) -> List[Dict[str, Any]]:
        """Analyze code for performance anti-patterns"""
        patterns = []
        
        # Check for nested loops
        if source_code.count('for') >= 2 and ('for' in source_code and 'for' in source_code[source_code.find('for')+3:]):
            patterns.append({
                'type': 'nested_loops',
                'severity': 'medium',
                'description': 'Nested loops detected - potential O(n²) complexity',
                'location': 'multiple locations',
                'suggestion': 'Consider using hash maps or alternative algorithms'
            })
        
        # Check for inefficient string concatenation
        if '+=' in source_code and 'str' in source_code:
            patterns.append({
                'type': 'string_concatenation',
                'severity': 'low',
                'description': 'Inefficient string concatenation detected',
                'location': 'string operations',
                'suggestion': 'Use join() method or f-strings for better performance'
            })
        
        # Check for repeated function calls
        import re
        function_calls = re.findall(r'(\w+)\s*\(', source_code)
        call_counts = {}
        for call in function_calls:
            call_counts[call] = call_counts.get(call, 0) + 1
        
        for func, count in call_counts.items():
            if count > 5:  # Arbitrary threshold
                patterns.append({
                    'type': 'repeated_function_calls',
                    'severity': 'low',
                    'description': f'Function {func}() called {count} times',
                    'location': f'{func} function',
                    'suggestion': 'Consider caching results or optimizing the function'
                })
        
        return patterns
    
    async def _generate_performance_recommendations(self, bottlenecks: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'execution_time':
                recommendations.extend([
                    'Optimize algorithm complexity',
                    'Use efficient data structures',
                    'Consider parallel processing',
                    'Implement caching strategies'
                ])
            elif bottleneck['type'] == 'memory_usage':
                recommendations.extend([
                    'Use generators for large datasets',
                    'Implement lazy loading',
                    'Clear unused objects',
                    'Use memory-efficient data types'
                ])
            elif bottleneck['type'] == 'cpu_usage':
                recommendations.extend([
                    'Reduce computational complexity',
                    'Use vectorized operations',
                    'Implement async processing',
                    'Optimize hot code paths'
                ])
            elif bottleneck['type'] == 'nested_loops':
                recommendations.append('Replace nested loops with hash-based lookups')
            elif bottleneck['type'] == 'string_concatenation':
                recommendations.append('Use join() or f-strings for string operations')
        
        # General recommendations
        if bottlenecks:
            recommendations.extend([
                'Profile code with detailed profilers',
                'Implement performance monitoring',
                'Set up performance benchmarks',
                'Consider code refactoring'
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _execute_load_test(self, endpoint: str, load_config: Dict[str, Any], duration: int) -> Dict[str, Any]:
        """Execute load testing (simulated)"""
        # Simulate load test metrics
        return {
            'requests_per_second': 150,
            'average_response_time': 250,  # ms
            'p95_response_time': 500,
            'p99_response_time': 1000,
            'error_rate': 2.5,  # percentage
            'throughput': 1200,  # requests/minute
            'concurrent_users': load_config.get('concurrent_users', 50),
            'total_requests': duration * 150,
            'successful_requests': int(duration * 150 * 0.975),
            'failed_requests': int(duration * 150 * 0.025)
        }
    
    async def _analyze_scalability(self, load_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scalability based on load test results"""
        rps = load_metrics['requests_per_second']
        avg_response_time = load_metrics['average_response_time']
        error_rate = load_metrics['error_rate']
        
        # Simple scalability analysis
        scalability_score = 100
        if avg_response_time > 500:
            scalability_score -= 20
        if error_rate > 5:
            scalability_score -= 30
        if rps < 100:
            scalability_score -= 25
        
        return {
            'scalability_score': max(scalability_score, 0),
            'bottlenecks': [
                'Response time degradation' if avg_response_time > 500 else None,
                'High error rate' if error_rate > 5 else None,
                'Low throughput' if rps < 100 else None
            ],
            'recommended_max_users': load_metrics['concurrent_users'] * 0.8,
            'scaling_recommendations': [
                'Add load balancing',
                'Implement caching',
                'Optimize database queries',
                'Consider horizontal scaling'
            ]
        }
    
    async def _analyze_performance_under_load(self, load_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance characteristics under load"""
        return {
            'stability': 'stable' if load_metrics['error_rate'] < 5 else 'unstable',
            'response_time_consistency': 'good' if load_metrics['p99_response_time'] < load_metrics['average_response_time'] * 3 else 'poor',
            'resource_utilization': 'optimal' if load_metrics['requests_per_second'] > 100 else 'suboptimal',
            'performance_degradation': f"{(load_metrics['p99_response_time'] / load_metrics['average_response_time'] - 1) * 100:.1f}%"
        }
    
    async def _profile_memory_usage(self, source_code: str, execution_time: int) -> Dict[str, Any]:
        """Profile memory usage (simulated)"""
        return {
            'peak_memory': 150.5,  # MB
            'average_memory': 120.3,
            'memory_growth_rate': 2.1,  # MB/second
            'allocation_count': 15420,
            'deallocation_count': 14980,
            'garbage_collection_cycles': 12,
            'memory_efficiency': 85.2  # percentage
        }
    
    async def _detect_memory_leaks(self, memory_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential memory leaks"""
        leaks = []
        
        growth_rate = memory_profile['memory_growth_rate']
        if growth_rate > 5:  # MB/second threshold
            leaks.append({
                'type': 'continuous_growth',
                'severity': 'high',
                'description': f'Memory growing at {growth_rate} MB/s',
                'suggestion': 'Check for unreleased resources or circular references'
            })
        
        allocation_diff = memory_profile['allocation_count'] - memory_profile['deallocation_count']
        if allocation_diff > 1000:
            leaks.append({
                'type': 'allocation_imbalance',
                'severity': 'medium',
                'description': f'{allocation_diff} more allocations than deallocations',
                'suggestion': 'Ensure proper cleanup of allocated objects'
            })
        
        return leaks
    
    async def _suggest_memory_optimizations(self, memory_profile: Dict[str, Any], memory_leaks: List[Dict[str, Any]]) -> List[str]:
        """Suggest memory optimizations"""
        suggestions = []
        
        if memory_leaks:
            suggestions.extend([
                'Implement proper resource cleanup',
                'Use context managers for resource management',
                'Review object lifecycle management',
                'Consider using weak references'
            ])
        
        if memory_profile['memory_efficiency'] < 80:
            suggestions.extend([
                'Use more memory-efficient data structures',
                'Implement object pooling',
                'Consider lazy initialization',
                'Use generators for large datasets'
            ])
        
        return suggestions
    
    async def _optimize_code(self, source_code: str, performance_targets: Dict[str, Any], optimization_level: str) -> Dict[str, Any]:
        """Optimize code for performance"""
        optimizations_applied = []
        
        # Simulate different optimization levels
        if optimization_level in ['moderate', 'aggressive']:
            optimizations_applied.extend([
                'Replaced list comprehensions with generator expressions',
                'Optimized loop structures',
                'Implemented memoization for recursive functions'
            ])
        
        if optimization_level == 'aggressive':
            optimizations_applied.extend([
                'Vectorized numerical operations',
                'Implemented parallel processing',
                'Optimized data structure usage',
                'Applied algorithmic improvements'
            ])
        
        # Simulate performance improvement
        improvement_factor = len(optimizations_applied) * 0.15
        improvement_factor = min(improvement_factor, 0.6)  # Cap at 60%
        
        return {
            'code': source_code + '\n# Optimized code\n',
            'optimizations': optimizations_applied,
            'improvement': {
                'execution_time_reduction': f"{improvement_factor * 100:.1f}%",
                'memory_usage_reduction': f"{improvement_factor * 0.7 * 100:.1f}%",
                'overall_performance_gain': f"{improvement_factor * 0.8 * 100:.1f}%"
            }
        }
    
    def _estimate_complexity(self, source_code: str) -> float:
        """Estimate algorithmic complexity (simplified)"""
        # Very basic complexity estimation
        nested_loops = source_code.count('for') if 'for' in source_code and source_code.count('for') > 1 else 1
        return min(nested_loops, 5)  # Cap at O(n^5)
    
    def _calculate_code_efficiency(self, source_code: str) -> float:
        """Calculate code efficiency score"""
        # Simple efficiency scoring based on code patterns
        score = 100
        
        if 'for' in source_code and 'for' in source_code[source_code.find('for')+3:]:
            score -= 15  # Nested loops penalty
        
        if '+=' in source_code and 'str' in source_code:
            score -= 10  # String concatenation penalty
        
        if len(source_code.split('\n')) > 100:
            score -= 5  # Long function penalty
        
        return max(score, 0)
    
    def _get_bottleneck_description(self, metric_name: str) -> str:
        """Get description for performance bottleneck"""
        descriptions = {
            'execution_time': 'Code execution is taking longer than expected',
            'memory_usage': 'Memory consumption is above normal levels',
            'cpu_usage': 'CPU utilization is higher than optimal',
            'algorithmic_complexity': 'Algorithm complexity may be too high',
            'code_efficiency': 'Code efficiency score is below acceptable levels'
        }
        return descriptions.get(metric_name, f'Performance issue detected in {metric_name}')
    
    # Placeholder methods for loading resources
    async def _load_performance_benchmarks(self) -> Dict[str, Any]:
        return {'benchmarks_loaded': True}
    
    async def _load_optimization_patterns(self) -> Dict[str, Any]:
        return {'patterns_loaded': True}
    
    async def _load_profiling_configs(self) -> Dict[str, Any]:
        return {'configs_loaded': True}
    
    async def _setup_python_profiler(self) -> Dict[str, Any]:
        return {'profiler': 'cProfile', 'available': True}
    
    async def _setup_javascript_profiler(self) -> Dict[str, Any]:
        return {'profiler': 'clinic', 'available': True}
    
    async def _setup_java_profiler(self) -> Dict[str, Any]:
        return {'profiler': 'JProfiler', 'available': True}
    
    async def _setup_load_testing_tools(self) -> Dict[str, Any]:
        return {'locust': True, 'jmeter': True, 'artillery': True}
    
    async def _setup_system_monitor(self) -> Dict[str, Any]:
        return {'psutil': True, 'available': True}

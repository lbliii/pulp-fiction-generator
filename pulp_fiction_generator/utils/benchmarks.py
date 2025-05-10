"""
Benchmarking utilities for the Pulp Fiction Generator.

This module provides tools for measuring and comparing performance
of various parts of the system.
"""

import time
import json
import statistics
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from pathlib import Path
import functools
import logging
import os
import platform
import psutil
import csv

# Configure logging
logger = logging.getLogger("pulp_fiction_generator.benchmarks")

class BenchmarkMetrics:
    """Collection of metrics from a benchmark run."""
    
    def __init__(self):
        """Initialize an empty benchmark metrics collection."""
        self.timing_data = {}
        self.memory_data = {}
        self.resource_data = {}
        self.custom_metrics = {}
        self.metadata = {
            "timestamp": datetime.now().isoformat(),
            "system": self._collect_system_info(),
        }
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect information about the system for context."""
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
        }
        
        return system_info
    
    def add_timing(self, label: str, time_ms: float) -> None:
        """
        Add a timing measurement.
        
        Args:
            label: Label for the timing metric
            time_ms: Execution time in milliseconds
        """
        if label not in self.timing_data:
            self.timing_data[label] = []
        self.timing_data[label].append(time_ms)
    
    def add_memory_usage(self, label: str, bytes_used: int) -> None:
        """
        Add a memory usage measurement.
        
        Args:
            label: Label for the memory metric
            bytes_used: Memory usage in bytes
        """
        if label not in self.memory_data:
            self.memory_data[label] = []
        self.memory_data[label].append(bytes_used)
    
    def add_resource_usage(self, label: str, resource_type: str, value: float) -> None:
        """
        Add a resource usage measurement (CPU, disk, etc.).
        
        Args:
            label: Label for the resource metric
            resource_type: Type of resource (cpu, disk, network, etc.)
            value: Resource usage value
        """
        key = f"{label}_{resource_type}"
        if key not in self.resource_data:
            self.resource_data[key] = []
        self.resource_data[key].append(value)
    
    def add_custom_metric(self, label: str, value: Any) -> None:
        """
        Add a custom metric.
        
        Args:
            label: Label for the custom metric
            value: Value of the metric
        """
        if label not in self.custom_metrics:
            self.custom_metrics[label] = []
        self.custom_metrics[label].append(value)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata about the benchmark run.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def summarize(self) -> Dict[str, Any]:
        """
        Generate a summary of all collected metrics.
        
        Returns:
            Dictionary with summary statistics for all metrics
        """
        summary = {
            "metadata": self.metadata,
            "timing": self._summarize_numeric_data(self.timing_data),
            "memory": self._summarize_numeric_data(self.memory_data),
            "resources": self._summarize_numeric_data(self.resource_data),
            "custom": self._summarize_custom_metrics(),
        }
        
        return summary
    
    def _summarize_numeric_data(self, data_dict: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate summary statistics for numeric data."""
        summary = {}
        
        for label, values in data_dict.items():
            if not values:
                continue
                
            # Get basic statistics
            stats = {
                "mean": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "count": len(values),
            }
            
            # Add median and stdev if we have enough samples
            if len(values) > 1:
                stats["median"] = statistics.median(values)
                stats["stdev"] = statistics.stdev(values)
            
            summary[label] = stats
            
        return summary
    
    def _summarize_custom_metrics(self) -> Dict[str, Any]:
        """Summarize custom metrics (which might not be numeric)."""
        summary = {}
        
        for label, values in self.custom_metrics.items():
            if not values:
                continue
                
            # For numeric values, provide statistics
            if all(isinstance(v, (int, float)) for v in values):
                summary[label] = self._summarize_numeric_data({label: values})[label]
            # Otherwise just provide the values
            else:
                summary[label] = values
            
        return summary

class Benchmark:
    """Utility for benchmarking code execution."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a benchmark.
        
        Args:
            name: Name of the benchmark
            description: Optional description of what the benchmark measures
        """
        self.name = name
        self.description = description
        self.metrics = BenchmarkMetrics()
        self.metrics.add_metadata("name", name)
        if description:
            self.metrics.add_metadata("description", description)
    
    def run(self, func: Callable, *args, **kwargs) -> Any:
        """
        Run a function and measure its execution time.
        
        Args:
            func: Function to benchmark
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The return value of the function
        """
        # Record memory before execution
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        
        # Record start time
        start_time = time.time()
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Record end time
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        
        # Record memory after execution
        mem_after = process.memory_info().rss
        mem_used = mem_after - mem_before
        
        # Add measurements to metrics
        self.metrics.add_timing(func.__name__, elapsed_ms)
        self.metrics.add_memory_usage(func.__name__, mem_used)
        
        # Log the timing
        logger.info(f"Benchmark '{self.name}' - {func.__name__}: {elapsed_ms:.2f}ms")
        
        return result
    
    def run_multiple(self, func: Callable, iterations: int, *args, **kwargs) -> List[Any]:
        """
        Run a function multiple times and measure statistics.
        
        Args:
            func: Function to benchmark
            iterations: Number of times to run the function
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            List of return values from each iteration
        """
        results = []
        
        logger.info(f"Running benchmark '{self.name}' for {iterations} iterations")
        
        for i in range(iterations):
            logger.debug(f"Iteration {i+1}/{iterations}")
            result = self.run(func, *args, **kwargs)
            results.append(result)
            
        return results
    
    def save_results(self, output_dir: str = "./benchmarks") -> str:
        """
        Save benchmark results to disk.
        
        Args:
            output_dir: Directory to save results to
            
        Returns:
            Path to the saved results file
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # Generate filename based on benchmark name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name.replace(' ', '_')}_{timestamp}.json"
        output_file = output_path / filename
        
        # Save summary to file
        summary = self.metrics.summarize()
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
            
        logger.info(f"Benchmark results saved to {output_file}")
        
        return str(output_file)

class BenchmarkComparer:
    """Utility for comparing benchmark results."""
    
    @staticmethod
    def load_benchmark(file_path: str) -> Dict[str, Any]:
        """
        Load a benchmark result from file.
        
        Args:
            file_path: Path to the benchmark result file
            
        Returns:
            Dictionary with benchmark data
        """
        with open(file_path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def compare(benchmark1: Dict[str, Any], benchmark2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two benchmark results.
        
        Args:
            benchmark1: First benchmark result
            benchmark2: Second benchmark result
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "benchmark1_name": benchmark1["metadata"].get("name", "Benchmark 1"),
            "benchmark2_name": benchmark2["metadata"].get("name", "Benchmark 2"),
            "timing_comparison": {},
            "memory_comparison": {},
        }
        
        # Compare timing data
        for category in ["timing", "memory"]:
            comparison_key = f"{category}_comparison"
            
            # Get metrics from both benchmarks
            metrics1 = benchmark1.get(category, {})
            metrics2 = benchmark2.get(category, {})
            
            # Find common metrics
            common_metrics = set(metrics1.keys()) & set(metrics2.keys())
            
            # Compare each common metric
            for metric in common_metrics:
                mean1 = metrics1[metric]["mean"]
                mean2 = metrics2[metric]["mean"]
                
                # Calculate percent difference and absolute difference
                if mean1 != 0:
                    percent_diff = ((mean2 - mean1) / mean1) * 100
                else:
                    percent_diff = float("inf") if mean2 > 0 else 0
                    
                abs_diff = mean2 - mean1
                
                comparison[comparison_key][metric] = {
                    "benchmark1_mean": mean1,
                    "benchmark2_mean": mean2,
                    "percent_difference": percent_diff,
                    "absolute_difference": abs_diff,
                    "improved": mean2 < mean1,
                }
        
        return comparison
    
    @staticmethod
    def save_comparison(comparison: Dict[str, Any], output_file: str) -> None:
        """
        Save a benchmark comparison to file.
        
        Args:
            comparison: Comparison results
            output_file: Path to save the comparison to
        """
        # Save as JSON
        with open(output_file, "w") as f:
            json.dump(comparison, f, indent=2, default=str)
            
        logger.info(f"Benchmark comparison saved to {output_file}")
        
        # Also save a CSV summary for easy viewing
        csv_file = output_file.replace(".json", ".csv")
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                "Category", "Metric", 
                f"{comparison['benchmark1_name']} Mean", 
                f"{comparison['benchmark2_name']} Mean",
                "Absolute Difference", "Percent Difference", "Improved"
            ])
            
            # Write timing comparisons
            for category in ["timing", "memory"]:
                comparison_key = f"{category}_comparison"
                
                for metric, data in comparison[comparison_key].items():
                    writer.writerow([
                        category.capitalize(),
                        metric,
                        f"{data['benchmark1_mean']:.2f}",
                        f"{data['benchmark2_mean']:.2f}",
                        f"{data['absolute_difference']:.2f}",
                        f"{data['percent_difference']:.2f}%",
                        "Yes" if data["improved"] else "No"
                    ])
                    
        logger.info(f"Benchmark comparison CSV saved to {csv_file}")

def benchmark(iterations: int = 1, name: Optional[str] = None, save_results: bool = True):
    """
    Decorator for benchmarking functions.
    
    Args:
        iterations: Number of times to run the function
        name: Custom name for the benchmark
        save_results: Whether to save the results to disk
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            benchmark_name = name or f"{func.__module__}.{func.__name__}"
            benchmark = Benchmark(benchmark_name)
            
            if iterations == 1:
                result = benchmark.run(func, *args, **kwargs)
            else:
                results = benchmark.run_multiple(func, iterations, *args, **kwargs)
                result = results[-1]  # Return the last result
            
            if save_results:
                benchmark.save_results()
                
            return result
        
        return wrapper
    
    return decorator 
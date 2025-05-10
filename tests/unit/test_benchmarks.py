"""
Tests for the benchmarking utilities.
"""

import os
import pytest
import tempfile
import time
import json
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.utils.benchmarks import (
    BenchmarkMetrics, 
    Benchmark, 
    BenchmarkComparer,
    benchmark
)

# ===== Test BenchmarkMetrics =====

def test_benchmark_metrics_initialization():
    """Test that BenchmarkMetrics initializes correctly."""
    metrics = BenchmarkMetrics()
    
    # Check that required collections are initialized
    assert metrics.timing_data == {}
    assert metrics.memory_data == {}
    assert metrics.resource_data == {}
    assert metrics.custom_metrics == {}
    
    # Check that metadata includes required fields
    assert "timestamp" in metrics.metadata
    assert "system" in metrics.metadata
    
    # Check system info
    system = metrics.metadata["system"]
    assert "platform" in system
    assert "python_version" in system
    assert "processor" in system
    assert "cpu_count" in system
    assert "memory_total" in system

def test_adding_metrics():
    """Test adding various metrics."""
    metrics = BenchmarkMetrics()
    
    # Add timing data
    metrics.add_timing("test_func", 100)
    metrics.add_timing("test_func", 120)
    assert len(metrics.timing_data["test_func"]) == 2
    assert metrics.timing_data["test_func"] == [100, 120]
    
    # Add memory data
    metrics.add_memory_usage("test_func", 1024)
    assert len(metrics.memory_data["test_func"]) == 1
    assert metrics.memory_data["test_func"][0] == 1024
    
    # Add resource data
    metrics.add_resource_usage("test_func", "cpu", 50.5)
    assert len(metrics.resource_data["test_func_cpu"]) == 1
    assert metrics.resource_data["test_func_cpu"][0] == 50.5
    
    # Add custom metric
    metrics.add_custom_metric("completion_rate", 0.95)
    assert len(metrics.custom_metrics["completion_rate"]) == 1
    assert metrics.custom_metrics["completion_rate"][0] == 0.95
    
    # Add metadata
    metrics.add_metadata("test_key", "test_value")
    assert metrics.metadata["test_key"] == "test_value"

def test_summarize_metrics():
    """Test summarizing metrics."""
    metrics = BenchmarkMetrics()
    
    # Add some test data
    metrics.add_timing("test_func", 100)
    metrics.add_timing("test_func", 120)
    metrics.add_timing("test_func", 140)
    
    metrics.add_memory_usage("test_func", 1024)
    metrics.add_memory_usage("test_func", 2048)
    
    metrics.add_custom_metric("numeric_metric", 10)
    metrics.add_custom_metric("numeric_metric", 20)
    
    metrics.add_custom_metric("string_metric", "value1")
    metrics.add_custom_metric("string_metric", "value2")
    
    # Get summary
    summary = metrics.summarize()
    
    # Check timing summary
    assert "timing" in summary
    assert "test_func" in summary["timing"]
    assert summary["timing"]["test_func"]["mean"] == 120
    assert summary["timing"]["test_func"]["min"] == 100
    assert summary["timing"]["test_func"]["max"] == 140
    assert summary["timing"]["test_func"]["median"] == 120
    assert "stdev" in summary["timing"]["test_func"]
    
    # Check memory summary
    assert "memory" in summary
    assert "test_func" in summary["memory"]
    assert summary["memory"]["test_func"]["mean"] == 1536
    
    # Check custom metrics summary
    assert "custom" in summary
    assert "numeric_metric" in summary["custom"]
    assert summary["custom"]["numeric_metric"]["mean"] == 15
    
    # Non-numeric metrics should just have the values
    assert "string_metric" in summary["custom"]
    assert summary["custom"]["string_metric"] == ["value1", "value2"]

# ===== Test Benchmark =====

def test_benchmark_initialization():
    """Test that Benchmark initializes correctly."""
    benchmark = Benchmark("test_benchmark", "Test description")
    
    assert benchmark.name == "test_benchmark"
    assert benchmark.description == "Test description"
    assert benchmark.metrics.metadata["name"] == "test_benchmark"
    assert benchmark.metrics.metadata["description"] == "Test description"

def test_benchmark_run():
    """Test running a benchmark."""
    def test_function(x, y):
        time.sleep(0.01)  # Sleep a bit to ensure measurable time
        return x + y
    
    benchmark = Benchmark("test_benchmark")
    result = benchmark.run(test_function, 2, 3)
    
    # Check result
    assert result == 5
    
    # Check metrics were recorded
    assert "test_function" in benchmark.metrics.timing_data
    assert len(benchmark.metrics.timing_data["test_function"]) == 1
    assert benchmark.metrics.timing_data["test_function"][0] > 0
    
    assert "test_function" in benchmark.metrics.memory_data
    assert len(benchmark.metrics.memory_data["test_function"]) == 1

def test_benchmark_run_multiple():
    """Test running a benchmark multiple times."""
    counter = [0]  # Use list to allow modification in the function
    
    def test_function():
        counter[0] += 1
        return counter[0]
    
    benchmark = Benchmark("test_benchmark")
    results = benchmark.run_multiple(test_function, 3)
    
    # Check results
    assert results == [1, 2, 3]
    
    # Check metrics were recorded
    assert "test_function" in benchmark.metrics.timing_data
    assert len(benchmark.metrics.timing_data["test_function"]) == 3

def test_benchmark_save_results():
    """Test saving benchmark results."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        benchmark = Benchmark("test_benchmark")
        
        # Add some test data
        benchmark.metrics.add_timing("test_func", 100)
        
        # Save results
        output_file = benchmark.save_results(tmpdirname)
        
        # Check file exists
        assert os.path.exists(output_file)
        
        # Check file content
        with open(output_file, "r") as f:
            data = json.load(f)
            assert data["metadata"]["name"] == "test_benchmark"
            assert "timing" in data
            assert "test_func" in data["timing"]

# ===== Test BenchmarkComparer =====

def test_benchmark_comparer_load():
    """Test loading benchmark from file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a test benchmark file
        test_data = {
            "metadata": {
                "name": "test_benchmark"
            },
            "timing": {
                "test_func": {
                    "mean": 100,
                    "min": 90,
                    "max": 110
                }
            }
        }
        
        test_file = os.path.join(tmpdirname, "test_benchmark.json")
        with open(test_file, "w") as f:
            json.dump(test_data, f)
        
        # Load the benchmark
        loaded_data = BenchmarkComparer.load_benchmark(test_file)
        
        # Check data was loaded correctly
        assert loaded_data["metadata"]["name"] == "test_benchmark"
        assert loaded_data["timing"]["test_func"]["mean"] == 100

def test_benchmark_comparer_compare():
    """Test comparing two benchmarks."""
    # Create test benchmark data
    benchmark1 = {
        "metadata": {
            "name": "benchmark1"
        },
        "timing": {
            "test_func": {
                "mean": 100,
                "min": 90,
                "max": 110
            },
            "unique_func1": {
                "mean": 200
            }
        },
        "memory": {
            "test_func": {
                "mean": 1024,
                "min": 1000,
                "max": 1100
            }
        }
    }
    
    benchmark2 = {
        "metadata": {
            "name": "benchmark2"
        },
        "timing": {
            "test_func": {
                "mean": 80,  # 20% faster
                "min": 70,
                "max": 90
            },
            "unique_func2": {
                "mean": 300
            }
        },
        "memory": {
            "test_func": {
                "mean": 1536,  # 50% more memory
                "min": 1500,
                "max": 1600
            }
        }
    }
    
    # Compare benchmarks
    comparison = BenchmarkComparer.compare(benchmark1, benchmark2)
    
    # Check comparison results
    assert comparison["benchmark1_name"] == "benchmark1"
    assert comparison["benchmark2_name"] == "benchmark2"
    
    # Check timing comparison
    assert "test_func" in comparison["timing_comparison"]
    assert comparison["timing_comparison"]["test_func"]["benchmark1_mean"] == 100
    assert comparison["timing_comparison"]["test_func"]["benchmark2_mean"] == 80
    assert comparison["timing_comparison"]["test_func"]["percent_difference"] == -20
    assert comparison["timing_comparison"]["test_func"]["improved"] is True
    
    # Check memory comparison
    assert "test_func" in comparison["memory_comparison"]
    assert comparison["memory_comparison"]["test_func"]["benchmark1_mean"] == 1024
    assert comparison["memory_comparison"]["test_func"]["benchmark2_mean"] == 1536
    assert comparison["memory_comparison"]["test_func"]["percent_difference"] == 50
    assert comparison["memory_comparison"]["test_func"]["improved"] is False

def test_benchmark_comparer_save_comparison():
    """Test saving a benchmark comparison."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create test comparison data
        comparison = {
            "benchmark1_name": "benchmark1",
            "benchmark2_name": "benchmark2",
            "timing_comparison": {
                "test_func": {
                    "benchmark1_mean": 100,
                    "benchmark2_mean": 80,
                    "percent_difference": -20,
                    "absolute_difference": -20,
                    "improved": True
                }
            },
            "memory_comparison": {
                "test_func": {
                    "benchmark1_mean": 1024,
                    "benchmark2_mean": 1536,
                    "percent_difference": 50,
                    "absolute_difference": 512,
                    "improved": False
                }
            }
        }
        
        # Save comparison
        output_file = os.path.join(tmpdirname, "comparison.json")
        BenchmarkComparer.save_comparison(comparison, output_file)
        
        # Check JSON file exists
        assert os.path.exists(output_file)
        
        # Check CSV file exists
        csv_file = output_file.replace(".json", ".csv")
        assert os.path.exists(csv_file)
        
        # Check file content
        with open(output_file, "r") as f:
            data = json.load(f)
            assert data["benchmark1_name"] == "benchmark1"
            assert data["timing_comparison"]["test_func"]["percent_difference"] == -20

# ===== Test Benchmark Decorator =====

def test_benchmark_decorator():
    """Test the benchmark decorator."""
    # Create a temporary directory for benchmark results
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a decorated function
        @benchmark(name="test_decorator", save_results=False)
        def test_function(x, y):
            return x + y
        
        # Call the function
        result = test_function(2, 3)
        
        # Check result
        assert result == 5

def test_benchmark_decorator_multiple_iterations():
    """Test the benchmark decorator with multiple iterations."""
    counter = [0]
    
    @benchmark(iterations=3, name="test_decorator_multiple", save_results=False)
    def test_function():
        counter[0] += 1
        return counter[0]
    
    # Call the function (which will run 3 times)
    result = test_function()
    
    # Check result (should be from the last iteration)
    assert result == 3
    
    # Check that the function was called 3 times
    assert counter[0] == 3 
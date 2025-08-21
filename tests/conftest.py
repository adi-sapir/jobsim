"""
Shared test configuration and fixtures for JobSim tests
"""
import pytest
import json
import tempfile
import os
from jobsim import (
    SimState, JobGenerator, WorkerPool, SimulationConfig
)
from jobsim.sim_config import WorkerDefinition, JobDefinition, UserDefinition

@pytest.fixture
def basic_config():
    """Basic configuration for testing"""
    return SimulationConfig(
        job_definitions=[
            JobDefinition("S", 300, 30, 50),
            JobDefinition("M", 600, 60, 30),
            JobDefinition("L", 5400, 120, 20)
        ],
        user_definitions=[
            UserDefinition("C", 60, 1),
            UserDefinition("F", 40, 2)
        ],
        worker_definitions=[
            WorkerDefinition("STANDBY", 0, 0, 3, 1),
            WorkerDefinition("DEALLOCATED", 300, 0, 5, 2),
            WorkerDefinition("COLD", 600, 1800, 10, 3)
        ],
        lambda_users_requests_per_hour=20
    )

@pytest.fixture
def minimal_config():
    """Minimal configuration for basic tests"""
    return SimulationConfig(
        job_definitions=[
            JobDefinition("S", 300, 60, 100)
        ],
        user_definitions=[
            UserDefinition("C", 100, 1)
        ],
        worker_definitions=[
            WorkerDefinition("STANDBY", 0, 0, 1, 1),
            WorkerDefinition("DEALLOCATED", 300, 0, 2, 2),
            WorkerDefinition("COLD", 600, 1800, 3, 3)
        ],
        lambda_users_requests_per_hour=10
    )

@pytest.fixture
def sim_state(basic_config):
    """Simulation state with basic config"""
    return SimState()

@pytest.fixture
def worker_pool(basic_config):
    """Worker pool with basic config"""
    return WorkerPool()

@pytest.fixture
def job_generator(basic_config):
    """Job generator with basic config"""
    return JobGenerator()

@pytest.fixture
def temp_scenario_file():
    """Temporary scenario file for testing"""
    test_scenario = [
        {"id": 1, "type": "S", "user_type": "C", "submission_time": 0},
        {"id": 2, "type": "M", "user_type": "F", "submission_time": 60},
        {"id": 3, "type": "L", "user_type": "S", "submission_time": 120}
    ]
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(test_scenario, temp_file)
    temp_file.close()
    
    yield temp_file.name
    
    # Clean up
    os.unlink(temp_file.name)

@pytest.fixture
def temp_config_file():
    """Temporary configuration file for testing"""
    test_config = {
        "job_definitions": [
            {"job_type": "S", "job_execution_duration": 30, "job_probability": 100}
        ],
        "user_definitions": [
            {"user_type": "C", "user_probability": 100, "num_jobs": 1}
        ],
        "lambda_users_requests_per_hour": 10,
        "standby_workers": 1,
        "max_deallocated_workers": 2,
        "max_cold_workers": 3,
        "worker_startup_time": 0,
        "worker_shutdown_time": 0,
        "worker_allocate_time": 0
    }
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(test_config, temp_file)
    temp_file.close()
    
    yield temp_file.name
    
    # Clean up
    os.unlink(temp_file.name)

# JobSim Test Suite

This directory contains a comprehensive test suite for the JobSim job execution simulation system.

## Test Structure

```
tests/
├── conftest.py              # Shared test configuration and fixtures
├── unit/                    # Unit tests for individual components
│   ├── test_event_queue.py  # EventQueue component tests
│   ├── test_workers.py      # Worker and WorkerPool tests
│   └── test_jobs.py         # Job component tests
├── integration/             # Integration tests for component interactions
│   └── test_worker_pool.py # WorkerPool integration tests
├── e2e/                    # End-to-end simulation tests
│   └── test_simulation.py  # Complete simulation workflows
├── cli/                    # Command line interface tests
│   └── test_cli.py         # CLI functionality tests
├── performance/            # Performance and scalability tests
│   └── test_scalability.py # Performance characteristics
├── run_tests.sh            # Full test suite runner
├── quick_test.sh           # Quick test runner
├── requirements-test.txt    # Test dependencies
└── README.md               # This file
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **EventQueue**: Min-heap event queue functionality
- **Workers**: Worker lifecycle and status management
- **Jobs**: Job creation, assignment, and properties

### 2. Integration Tests (`tests/integration/`)
- **WorkerPool**: Worker allocation and priority management
- **Component Interactions**: How different parts work together

### 3. End-to-End Tests (`tests/e2e/`)
- **Simulation Workflows**: Complete simulation runs
- **Scenario Loading**: File-based job scenarios
- **Statistics Generation**: Output and reporting

### 4. CLI Tests (`tests/cli/`)
- **Command Parsing**: Argument handling and validation
- **File Operations**: Configuration and scenario loading
- **Error Handling**: Graceful failure modes

### 5. Performance Tests (`tests/performance/`)
- **Scalability**: Large simulation performance
- **Memory Usage**: Resource consumption analysis
- **CPU Usage**: Processing efficiency

## Running Tests

### Quick Test (Basic Functionality)
```bash
./tests/quick_test.sh
```

### Full Test Suite (With Coverage)
```bash
./tests/run_tests.sh
```

### Individual Test Categories
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# End-to-end tests only
pytest tests/e2e/ -v

# CLI tests only
pytest tests/cli/ -v

# Performance tests only
pytest tests/performance/ -v
```

### With Coverage
```bash
pytest tests/ --cov=src/jobsim --cov-report=html
```

## Test Dependencies

Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

Required packages:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support
- `psutil` - Performance monitoring

## Test Fixtures

The `conftest.py` file provides shared test fixtures:

- **`basic_config`**: Full simulation configuration
- **`minimal_config`**: Minimal configuration for basic tests
- **`temp_scenario_file`**: Temporary scenario file for testing
- **`temp_config_file`**: Temporary configuration file for testing

## Writing New Tests

### Test Naming Convention
- Test files: `test_<component>.py`
- Test classes: `Test<Component>`
- Test methods: `test_<functionality>`

### Example Test Structure
```python
def test_component_functionality(self):
    """Test description"""
    # Arrange
    component = Component()
    
    # Act
    result = component.method()
    
    # Assert
    assert result == expected_value
```

### Using Fixtures
```python
def test_with_config(self, basic_config):
    """Test using shared configuration"""
    # Use basic_config fixture
    assert basic_config.job_definitions is not None
```

## Test Results

After running the full test suite, results are available in:
- **Coverage Report**: `test_results/coverage_html/index.html`
- **Test Results**: `test_results/test_results.xml`
- **Console Output**: Coverage summary and test results

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- Fast execution for unit tests
- Comprehensive coverage reporting
- XML output for CI tools
- Exit codes for build systems

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure JobSim package is installed (`pip install -e .`)
2. **Missing Dependencies**: Install test requirements (`pip install -r tests/requirements-test.txt`)
3. **Permission Denied**: Make scripts executable (`chmod +x tests/*.sh`)
4. **Timeout Errors**: Some tests may take longer on slower systems

### Debug Mode
Run tests with verbose output:
```bash
pytest tests/ -v -s --tb=long
```

### Isolated Testing
Test specific components in isolation:
```bash
pytest tests/unit/test_event_queue.py::TestEventQueue::test_event_queue_ordering -v
```

## Contributing

When adding new features to JobSim:
1. Write corresponding tests
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Update this README if needed

## Test Coverage Goals

- **Unit Tests**: 90%+ coverage for core components
- **Integration Tests**: Cover all component interactions
- **End-to-End Tests**: Validate complete workflows
- **CLI Tests**: Test all command line options
- **Performance Tests**: Ensure scalability requirements

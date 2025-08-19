# JobSim - Job Execution Simulation

A Python-based discrete event simulation system that models job scheduling, worker allocation, and execution in a multi-tier worker pool environment.

## Overview

JobSim simulates a job processing system with three worker tiers: **standby** (always ready), **deallocated** (quick activation), and **cold** (slow startup). Jobs can be generated dynamically according to configurable patterns or loaded from predefined scenario files. Workers are automatically allocated and managed throughout the simulation lifecycle.

## Architecture

### Core Components

- **EventQueue**: Min-heap based priority queue for timestamp-ordered event processing
- **SimState**: Central simulation state managing jobs, workers, and event flow
- **WorkerPool**: Manages worker lifecycle across three tiers with different activation costs
- **JobGenerator**: Generates jobs based on configurable arrival patterns and user types
- **Event-Driven Simulation**: Discrete event simulation using event types (JOB_SUBMITTED, WORKER_READY, WORKER_DONE, WORKER_TO_POOL)

### Worker Model

- **STANDBY**: Always ready, no activation cost, immediate job assignment
- **DEALLOCATED**: Quick activation (configurable), no shutdown cost
- **COLD**: Slow startup (configurable), shutdown cost applies

### Event Flow

1. Jobs are generated and queued as JOB_SUBMITTED events
2. Available workers immediately process jobs
3. If no workers available, invoke additional workers (prioritizing DEALLOCATED over COLD)
4. Workers complete jobs and return to READY state
5. Idle workers are sent back to pool after configurable shutdown delay

## Installation

### From Source (Recommended for Development)

```bash
git clone <repository-url>
cd jobsim
pip install -e .
```

### From Package

```bash
pip install jobsim-*.whl
```

After installation, three command-line tools are available:
- `jobsim` - Main simulation engine
- `jobgen` - Job generator for creating scenarios  
- `sim-config` - Configuration management utility

## Project Structure

```
jobsim/
├── src/jobsim/
│   ├── __init__.py       # Package initialization
│   ├── jobsim.py         # Main simulator with CLI
│   ├── jobgen.py         # Job generation CLI
│   ├── event_queue.py    # Min-heap event queue
│   ├── workers_model.py  # Worker types, statuses, and pool management
│   ├── sim_config.py     # Configuration schema and CLI
│   ├── debug_config.py   # Debug logging utilities
│   ├── sim_histogram.py  # Text-based histogram utilities
│   └── time_def.py       # Time constants (MINUTE, HOUR, DAY)
├── examples/configs/      # Sample configuration files
├── pyproject.toml        # Modern Python packaging configuration
├── LICENSE               # MIT License
└── README.md
```

## Configuration Schema

The simulation configuration supports:

```json
{
  "job_definitions": [
    {
      "job_type": "S|M|L",
      "job_execution_duration": 60,
      "job_probability": 40
    }
  ],
  "user_definitions": [
    {
      "user_type": "F|C|S",
      "user_probability": 50,
      "num_jobs": 1
    }
  ],
  "lambda_users_requests_per_hour": 10,
  "standby_workers": 2,
  "max_deallocated_workers": 10,
  "max_cold_workers": 30,
  "worker_startup_time": 600,
  "worker_shutdown_time": 1800,
  "worker_allocate_time": 180
}
```

### Configuration Fields

- **Job Types**: S (small), M (medium), L (large) with execution durations and probabilities
- **User Types**: F (free), C (creator), S (studio) with job limits and probabilities
- **Worker Pool**: Counts and timing for each worker tier
- **Arrival Rate**: Poisson process for job submissions

## Usage

### Main Simulation

```bash
# Basic simulation (1 hour)
jobsim 1:00:00

# With configuration file
jobsim 0:30:00 --config config.json

# Named run with debug output (trace or full level)
jobsim 0:15:00 --config config.json --run-name baseline --debug trace

# Using a predefined scenario file (duration optional when using scenario)
jobsim --scenario scenario.json

# Using scenario with specific duration and debug
jobsim 1:00:00 --scenario scenario.json --debug full
```

### Job Generation and Scenarios

```bash
# Generate jobs for 5 minutes (outputs scenario-ready JSON)
jobgen 0:05:00

# Generate jobs with configuration and debug
jobgen 0:05:00 --config config.json --debug trace

# Save jobs to scenario file
jobgen 1:00:00 > scenario.json

# Use scenario in simulation
jobsim --scenario scenario.json
```

The job generator outputs clean JSON suitable for use as scenario files. Each job contains only the fields needed for simulation initialization:

```json
[
{"id": 0, "type": "L", "user_type": "C", "submission_time": 109},
{"id": 1, "type": "M", "user_type": "C", "submission_time": 109},
{"id": 2, "type": "S", "user_type": "F", "submission_time": 234}
]
```

### Configuration Management

```bash
# Print current configuration
sim-config --print

# Load and save configuration
sim-config --load config.json --save my_config.json

# Load configuration with debug
sim-config --load config.json --debug trace
```

## Run Naming

Run names are automatically generated as:
1. `--run-name` if provided
2. Config file basename (without extension) if `--config` used
3. Current timestamp `YYYY-MM-DD--HH-MM-SS`

Final name always includes `-sim-<seconds>` suffix for unique identification.

## Outputs

### Console Output
The simulator provides comprehensive statistics including:

- **Simulation Summary**: Total jobs processed and simulation duration
- **Job Distribution**: Histogram of job submission times over the simulation period
- **Wait Time Analysis**: Min/avg/max wait times with distribution histogram
- **Worker Usage Statistics**: 
  - Distinct workers used per worker type
  - Processing time per worker type
  - Total processing time across all workers

### Generated Plots (if matplotlib available)
- **Submission Time Distribution**: Stacked histogram by job type
- **Wait Time Distribution**: Stacked histogram by job type  
- **Worker Use Time Distribution**: Stacked histogram by worker type

Files are named: `{plot_type}_{run_name}.png`

### Sample Output Format
```
Run [baseline-sim-3600]: Simulated 150 jobs in 1:00:00

Submitted Jobs distribution over time (seconds):
================================================
[Histogram display]

Wait Time distribution (seconds):
=================================
Min Wait Time: 0:00:00
Avg Wait Time: 0:02:15
Max Wait Time: 0:08:30
[Histogram display]

Workers used:
=============
Workers used (standby): 2
Workers used (deallocated): 5
Workers used (cold): 3
Processing time (standby): 0:45:20
Processing time (deallocated): 1:23:15
Processing time (cold): 0:51:25
Total processing time: 3:00:00
```

## Event Queue Implementation

The `EventQueue` class provides O(log n) insertion and O(1) access to the earliest event:

```python
from src.event_queue import EventQueue

eq = EventQueue()
eq.push(100, "job_start")      # timestamp, data
eq.push(50, "resource_check")  # automatically ordered

while not eq.is_empty():
    event = eq.pop()            # earliest timestamp first
    print(f"{event.timestamp}: {event.data}")
```

## Worker Allocation Strategy

1. **Immediate**: Use READY workers (standby or recently freed)
2. **Quick Activation**: Invoke DEALLOCATED workers (3 min activation)
3. **Slow Activation**: Invoke COLD workers (10 min startup)
4. **Priority**: DEALLOCATED preferred over COLD for new invocations

## Debug and Monitoring

Enable debug output with `--debug` flag (two levels available):

**Trace Level** (`--debug trace`):
- Job submission and worker assignment events
- Worker state transitions
- Basic timing information

**Full Level** (`--debug full`):
- All trace-level information plus:
- Detailed queue management operations  
- Worker pool initialization details
- Comprehensive event processing logs

## Performance Characteristics

- **Event Processing**: O(log n) per event insertion/removal
- **Worker Allocation**: O(n) scan for available workers
- **Memory**: Linear with job count and worker pool size
- **Scalability**: Designed for thousands of jobs and hundreds of workers

## Dependencies

### Required
- Python 3.10+
- Standard library modules (argparse, datetime, enum, os, sys)

### Optional
- matplotlib: For generating plots and histograms

Install optional dependency:
```bash
pip install matplotlib
```

## Testing and Examples

The `tests/` directory contains:
- Sample configuration files for different scenarios
- Generated output plots from test runs
- Examples of minimal vs. full worker pool configurations

## Troubleshooting

### Common Issues

1. **Matplotlib Import Warning**: Install matplotlib or ignore if plots not needed
2. **Configuration Errors**: Verify JSON syntax and required fields
3. **Worker Pool Issues**: Check worker counts and timing values in config

### Debug Tips

- Use `--debug` flag for detailed event logging
- Start with short simulation times for testing
- Verify configuration with `sim_config.py --print`
- Check worker pool initialization messages in debug mode

## Contributing

- Fork the repository
- Create feature branch: `git checkout -b feature-name`
- Ensure code passes linting: `flake8 src/`
- Submit pull request with clear description

## License

[Add your license information here]

---

For more information, examine the source code in `src/` or run the tools with `--help` for detailed usage information.

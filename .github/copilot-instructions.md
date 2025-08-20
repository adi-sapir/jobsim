# Copilot Instructions for JobSim

## Project Overview
- **JobSim** is a discrete event simulator for job scheduling and multi-tier worker pools, written in Python 3.10+.
- Main logic is in `src/jobsim/` (see `jobsim.py`, `workers_model.py`, `event_queue.py`, `jobgen.py`, `sim_config.py`).
- Simulates job arrivals, worker allocation (standby, deallocated, cold), and event-driven execution.

## Key Components & Data Flow
- **EventQueue**: Min-heap for timestamp-ordered event processing (`event_queue.py`).
- **SimState**: Central state for jobs, workers, and event flow (see `jobsim.py`).
- **WorkerPool**: Manages worker lifecycle and tier transitions (`workers_model.py`).
- **JobGenerator**: Creates jobs from config or scenario files (`jobgen.py`).
- **Config**: JSON-based, see `examples/configs/` and `sim_config.py` for schema.

## Developer Workflows
- **Install (dev):** `pip install -e .`
- **Run simulation:** `jobsim <duration> [--config <file>] [--debug <level>] [--scenario <file>]`
- **Generate jobs:** `jobgen <duration> [--config <file>]`
- **Config management:** `sim-config --print|--load <file> [--save <file>]`
- **Debugging:** Use `--debug trace` or `--debug full` for detailed logs.
- **Testing:** Use sample configs and scenarios in `tests/`.

## Project Conventions
- **Worker Tiers:** Standby (always ready), Deallocated (quick start), Cold (slow start).
- **Event Types:** `JOB_SUBMITTED`, `WORKER_READY`, `WORKER_DONE`, `WORKER_TO_POOL`.
- **Run Naming:** `--run-name` arg, config basename, or timestamp; always suffixed with `-sim-<seconds>`.
- **Output:** Console stats, optional PNG plots if `matplotlib` is installed.
- **Config fields:** See `README.md` and `examples/configs/` for required fields and types.

## Integration & Extensibility
- **CLI entrypoints:** `jobsim`, `jobgen`, `sim-config` (see `pyproject.toml`).
- **Optional dependency:** `matplotlib` for plots.
- **No external services or network calls.**

## Patterns & Examples
- **Event loop:**
  ```python
  while not eq.is_empty():
      event = eq.pop()
      # handle event
  ```
- **Job scenario format:** JSON array of jobs with `id`, `type`, `user_type`, `submission_time`.
- **Worker allocation:** Prefer deallocated over cold; always use standby if available.

## References
- `README.md`: Full usage, architecture, and troubleshooting.
- `src/jobsim/`: All core logic and CLI entrypoints.
- `examples/configs/`: Example configs for quick testing.
- `tests/`: Sample scenarios and output files.

---
For more details, see the `README.md` or run any CLI tool with `--help`.

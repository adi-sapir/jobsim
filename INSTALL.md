# JobSim Installation Guide

## Quick Install

### From Source (Development/Editable Install)
```bash
# Clone the repository
git clone <your-repo-url>
cd jobsim

# Install in development mode
python -m pip install -e .
```

### From Built Package
```bash
# Build the package
python -m build

# Install from built package
pip install dist/jobsim-0.1.0.tar.gz
```

## Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

## Verification

After installation, verify that the package works:

```bash
# Test import
python -c "import jobsim; print(f'JobSim {jobsim.__version__} installed successfully!')"

# Test command-line tools
jobsim --help
jobgen --help
sim-config --help
```

## Usage

### Run a Simulation
```bash
# Run a 1 hour simulation
jobsim 1:00:00

# Run with custom configuration
jobsim 2:30:00 --config my_config.json --run-name "production_run"

# Enable debug output
jobsim 0:30:00 --debug
```

### Generate Jobs
```bash
# Generate jobs for 2 hours
jobgen 2:00:00

# Generate with custom configuration
jobgen 1:00:00 --config my_config.json
```

### Manage Configuration
```bash
# Print current configuration
sim-config --print

# Load configuration from file
sim-config --load config.json --print

# Save current configuration
sim-config --save my_config.json
```

## Development

For development work, use the editable install:

```bash
pip install -e .
```

This allows you to modify the source code and see changes immediately without reinstalling.

## Troubleshooting

### Import Errors
If you get import errors, ensure you're using the same Python environment where you installed the package:

```bash
# Check which Python you're using
which python

# Check if package is installed
pip list | grep jobsim

# Reinstall if needed
python -m pip install -e . --force-reinstall
```

### Command Not Found
If the command-line tools aren't found, check your PATH and Python installation:

```bash
# Verify installation
pip show jobsim

# Check entry points
python -c "import pkg_resources; print(pkg_resources.get_entry_map('jobsim'))"
```

## Uninstall

```bash
pip uninstall jobsim
```

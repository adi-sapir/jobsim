import json
import os
from dataclasses import dataclass, asdict, field
from typing import Tuple


@dataclass
class SimulationConfig:
    duration: int = 3600                         # in seconds
    num_jobs: int = 100
    enable_logging: bool = False
    output_dir: str = "results"
    job_priority_range: Tuple[int, int] = field(default_factory=lambda: (1, 5))

    def save_to_json(self, filepath: str):
        """Save the config as JSON to the given file."""
        with open(filepath, "w") as f:
            json.dump(asdict(self), f, indent=4)
        print(f"[INFO] Configuration saved to '{filepath}'.")

    @classmethod
    def load_from_json(cls, filepath: str) -> "SimulationConfig":
        """Load config from a JSON file. Fallback to defaults if file is missing or invalid."""
        if not os.path.exists(filepath):
            print(f"[WARNING] Config file '{filepath}' not found. Using default configuration.")
            return cls()

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Keep only valid field names
            valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}

            return cls(**filtered_data)

        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in '{filepath}': {e}")
        except TypeError as e:
            print(f"[ERROR] Type error in config data: {e}")

        print("[WARNING] Falling back to default configuration.")
        return cls()


# ✅ Global config object (always available with default values)
CONFIG: SimulationConfig = SimulationConfig()


def load_config(filepath: str):
    """Load and overwrite the global CONFIG from a file."""
    global CONFIG
    CONFIG = SimulationConfig.load_from_json(filepath)


def save_config(filepath: str):
    """Save the current global CONFIG to a file."""
    CONFIG.save_to_json(filepath)

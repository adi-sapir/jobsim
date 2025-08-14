import json
import os
from dataclasses import dataclass, asdict, field
from typing import List
import random
from debug_config import debug_print

@dataclass
class JobDefinition:
    job_type: str
    job_execution_duration: int
    job_probability: int

@dataclass
class UserDefinition:
    user_type: str
    user_probability: int
    num_jobs: int

@dataclass
class SimulationConfig:
    job_definitions: List[JobDefinition] = field(default_factory=lambda: [
        JobDefinition(job_type="S", job_execution_duration=22, job_probability=10),
        JobDefinition(job_type="M", job_execution_duration=252, job_probability=70),
        JobDefinition(job_type="L", job_execution_duration=385, job_probability=20),
    ])
    user_definitions: List[UserDefinition] = field(default_factory=lambda: [
        UserDefinition(user_type="F", user_probability=10, num_jobs=1),
        UserDefinition(user_type="C", user_probability=70, num_jobs=2),
        UserDefinition(user_type="S", user_probability=20, num_jobs=6),
    ])
    lambda_users_requests_per_hour: int = 20
    standby_workers: int = 4
    max_deallocated_workers: int = 10
    max_cold_workers: int = 30
    worker_startup_time: int = 10 * 60
    worker_shutdown_time: int = 30 * 60
    worker_allocate_time: int = 3 * 60
    #calculated fields
    job_types: str = field(init=False, repr=False)
    user_types: str = field(init=False, repr=False)

    def __post_init__(self):
        # Normalize loaded dicts to dataclass instances
        self.job_definitions = [
            jd if isinstance(jd, JobDefinition) else JobDefinition(**jd)
            for jd in self.job_definitions
        ]
        self.user_definitions = [
            ud if isinstance(ud, UserDefinition) else UserDefinition(**ud)
            for ud in self.user_definitions
        ]
        self.job_types = "".join([job.job_type * job.job_probability for job in self.job_definitions])
        chars = list(self.job_types)
        random.shuffle(chars)
        self.job_types = ''.join(chars)
        self.user_types = "".join([user.user_type * user.user_probability for user in self.user_definitions])
        chars = list(self.user_types)
        random.shuffle(chars)
        self.user_types = ''.join(chars)

    def to_dict(self):
        data = asdict(self)
        data.pop("job_types")
        data.pop("user_types")
        return data

    def to_full_dict(self):
        data = self.to_dict()
        data["job_types"] = self.job_types
        data["user_types"] = self.user_types
        return data
    
    def save_to_json(self, filepath: str):
        """Save the config as JSON to the given file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
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
    
    def get_job_execution_duration(self, job_type: str) -> int:
        for job_definition in self.job_definitions:
            if job_definition.job_type == job_type:
                return job_definition.job_execution_duration
        raise ValueError(f"Job type {job_type} not found in job definitions")

    def get_num_jobs(self, user_type: str) -> int:
        for user_definition in self.user_definitions:
            if user_definition.user_type == user_type:
                return user_definition.num_jobs
        raise ValueError(f"User type {user_type} not found in user definitions")


# ✅ Global config object (always available with default values)
CONFIG: SimulationConfig = SimulationConfig()


def load_config(filepath: str):
    """Load and overwrite the global CONFIG from a file."""
    global CONFIG
    CONFIG = SimulationConfig.load_from_json(filepath)
    debug_print(f"Loaded config from {filepath}")
    debug_print(json.dumps(CONFIG.to_full_dict(), indent=4))


def save_config(filepath: str):
    """Save the current global CONFIG to a file."""
    CONFIG.save_to_json(filepath)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simulation configuration utility")
    parser.add_argument("--load", metavar="FILE", help="Load configuration from JSON file")
    parser.add_argument("--save", metavar="FILE", help="Save current configuration to JSON file")
    parser.add_argument("--print", action="store_true", help="Print current configuration to stdout")
    args = parser.parse_args()

    # Load if requested
    if args.load:
        load_config(args.load)

    # Save if requested
    if args.save:
        save_config(args.save)

    # Always print full configuration at the end
    print(json.dumps(CONFIG.to_full_dict(), indent=4))

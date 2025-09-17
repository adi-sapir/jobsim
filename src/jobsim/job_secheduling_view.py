import argparse
import json
import sys
from typing import List, Any
from .time_def import MINUTE, HOUR, seconds_to_hms, parse_duration_hms, seconds_to_hms_short

# Handle relative import when run as script vs module
try:
    from .debug_config import debug_print as _debug_print
    from .jobgen import Job
except ImportError:
    # When run directly as script, imports are not available
    def _debug_print(*args, **kwargs):
        pass
    
    # Import Job class from jobgen module for standalone use
    import os
    import importlib.util
    
    # Get the correct path to jobgen.py
    current_dir = os.path.dirname(__file__)  # src/jobsim/
    jobgen_path = os.path.join(current_dir, "jobgen.py")
    
    # Import jobgen module
    spec = importlib.util.spec_from_file_location("jobgen", jobgen_path)
    jobgen_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(jobgen_module)
    Job = jobgen_module.Job

# Global debug flag
DEBUG_ENABLED = False

def debug_print(*args, **kwargs):
    """Print debug messages only if debug is enabled"""
    if DEBUG_ENABLED:
        _debug_print(*args, **kwargs)

class JobSchedulingStep:
    def __init__(self, timestamp: int):
        self.timestamp = timestamp
        self.slotsIdxs = set()
        self.slots = []
    
    def find_aviaiable_slot(self) -> int:
        for i in range(len(self.slots)):
            if i not in self.slotsIdxs:
                self.slotsIdxs.add(i)
                return i
        self.slots.append(' ')
        slot_idx = len(self.slots) - 1
        self.slotsIdxs.add(slot_idx)
        return slot_idx

    def add_job_to_slot(self, slot_idx: int):
        # create slots if needed
        while slot_idx >= len(self.slots):
            self.slots.append(' ')
        self.slotsIdxs.add(slot_idx)
        self.slots[slot_idx] = ':'
    
    def mark_submit(self, slot_idx: int):
        self.slots[slot_idx] = 'L'
    
    def mark_waiting(self, slot_idx: int):
        self.slots[slot_idx] = 'w'
    
    def mark_start(self, slot_idx: int):
        self.slots[slot_idx] = 'S'

    def mark_processing(self, slot_idx: int):
        self.slots[slot_idx] = '*'
        
    def mark_finish(self, slot_idx: int):
        self.slots[slot_idx] = 'F'

class JobSchedulingView:
    def __init__(self):
        self.steps = []
        self.step_width = 1
        self.init_time = 0
        self.finish_time = 0

    def add_job(self, job: Job):
        first_step_idx = (job.submission_time - self.init_time) // self.step_width
        start_step_idx = first_step_idx + (job.processing_start_time - job.submission_time) // self.step_width
        finish_step_idx = first_step_idx + (job.processing_complete_time - job.submission_time) // self.step_width
        num_of_steps = finish_step_idx - first_step_idx + 1
        if first_step_idx < 0 or first_step_idx >= len(self.steps):
          print(f"Error: Job {job.id} first_step_idx {first_step_idx} is out of range (0, {len(self.steps)})")
          return
        if start_step_idx < 0 or start_step_idx >= len(self.steps):
          print(f"Error: Job {job.id} start_step_idx {start_step_idx} is out of range (0, {len(self.steps)})")
          return
        if finish_step_idx < 0 or finish_step_idx >= len(self.steps):
          print(f"Error: Job {job.id} finish_step_idx {finish_step_idx} is out of range (0, {len(self.steps)})")
          return
        job_slot_idx = self.steps[first_step_idx].find_aviaiable_slot()
        for i in range(num_of_steps):
          self.steps[first_step_idx + i].add_job_to_slot(job_slot_idx)
        self.steps[first_step_idx].mark_submit(job_slot_idx)
        # INSERT_YOUR_CODE
        # Mark as processing the steps from start_step_idx till finish_step_idx - 1 (inclusive)
        for i in range(start_step_idx, finish_step_idx):
            self.steps[i].mark_processing(job_slot_idx)
        self.steps[start_step_idx].mark_start(job_slot_idx)
        self.steps[finish_step_idx].mark_finish(job_slot_idx)

    def initialize_from_job_list(self, jobs: List[Job], step_width: int):
        if not jobs:
            return
        self.step_width = step_width
        self.finish_time = max(job.processing_complete_time for job in jobs)
        self.init_time = min(job.submission_time for job in jobs)
        num_of_step = (self.finish_time - self.init_time) // self.step_width + 1
        self.steps = []
        for i in range(num_of_step):
            self.steps.append(JobSchedulingStep(self.init_time + i * self.step_width))
        for job in jobs:
            self.add_job(job)

    def print_view(self):
        print("Job Scheduling View:")
        print("=" * 50)
        for step in self.steps:
            slots_str = ' '.join(step.slots) if step.slots else ''
            print(f"Time {seconds_to_hms_short(step.timestamp)}| {slots_str}")
        print("=" * 50)

def load_jobs_from_file(filename: str) -> List[Job]:
    """Load jobs from a JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("File must contain a JSON array")
        
        jobs = []
        for item in data:
            if isinstance(item, dict):
                # Create Job object with required fields
                job = Job(
                    id=item.get('file_id', 0),
                    type=item.get('file_type', 'unknown'),
                    user_type=item.get('user_type', 'unknown'),
                    submission_time=item.get('submission_time', 0)
                )
                # Set processing_complete_time as an attribute
                job.processing_complete_time = item.get('processing_complete_time', 0)
                job.processing_start_time = item.get('processing_start_time', 0)
                jobs.append(job)
            else:
                raise ValueError("Each job must be a JSON object")
        
        return jobs
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Visualize job scheduling from JSON data')
    parser.add_argument('--file', '-f', type=str, required=True, help='JSON file containing job data')
    parser.add_argument('--step', '-s', type=int, default=10, help='Step width for scheduling view (default: 10)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Set global debug flag
    global DEBUG_ENABLED
    DEBUG_ENABLED = args.debug
    
    # Load jobs from file
    jobs = load_jobs_from_file(args.file)
    
    if not jobs:
        print("No jobs found in file", file=sys.stderr)
        sys.exit(1)
    
    # Create and display scheduling view
    print(f"Loading {len(jobs)} jobs from '{args.file}' with step width {args.step}")
    view = JobSchedulingView()
    view.initialize_from_job_list(jobs, args.step)
    view.print_view()

if __name__ == "__main__":
    main()
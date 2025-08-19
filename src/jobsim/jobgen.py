# Job generator
# Generates a series of job sumbmitions

import random
import json
import argparse
from .time_def import MINUTE, HOUR, parse_duration_hms
from typing import Optional, Dict
from . import sim_config
from .debug_config import trace_print

def generate_interarrival_time() -> int:
  return int(random.expovariate(sim_config.CONFIG.lambda_users_requests_per_hour / HOUR))

class Job:
  def __init__(self, id, type, user_type, submission_time):
    self.id = id
    self.type = type
    self.user_type = user_type
    self.submission_time = submission_time
    self.start_execution_time = 0
    self.server_type = None
    self.server_id = None

  def to_dict(self):
    return {
      'id': self.id,
      'type': self.type,
      'user_type': self.user_type,
      'submission_time': self.submission_time,
      'start_execution_time': self.start_execution_time,
      'server_type': self.server_type,
      'server_id': self.server_id
    }

  def to_json(self):
    return json.dumps(self.to_dict())

  def __str__(self):
    return f"Job(id={self.id}, type={self.type}, user_type={self.user_type}, submission_time={self.submission_time}, start_execution_time={self.start_execution_time}, server_type={self.server_type}, server_id={self.server_id})"

  def __repr__(self):
    return self.__str__()

  def get_execution_duration(self):
    return sim_config.CONFIG.get_job_execution_duration(self.type)

  def get_user_type(self):
    return self.user_type

  def get_type(self):
    return self.type

  def get_id(self):
    return self.id

  def get_submission_time(self):
    return self.submission_time

  def get_start_execution_time(self):
    return self.start_execution_time
  
  def set_start_execution_time(self, start_execution_time: int):
    self.start_execution_time = start_execution_time
  
  def set_server_type(self, server_type: str):
    self.server_type = server_type
  
  def get_server_type(self):
    return self.server_type
  
  def set_server_id(self, server_id: int):
    self.server_id = server_id
  
  def get_server_id(self) -> int:
    return self.server_id
  
class JobGenerator:
  def __init__(self):
    self.user_type_index = 0
    self.job_type_index = 0
    self.job_id = 0
    self.jobs: list[Job] = []

  def generate_job(self, user_request_time: int, user_type: str) -> Job:
    job_type = sim_config.CONFIG.job_types[self.job_type_index % len(sim_config.CONFIG.job_types)]
    self.job_type_index += 1
    job = Job(
      id=self.job_id,
      type=job_type,
      user_type=user_type,
      submission_time=user_request_time)
    self.job_id += 1
    return job

  def handle_user_request(self, user_request_time: int) -> None:
    user_type = sim_config.CONFIG.user_types[self.user_type_index % len(sim_config.CONFIG.user_types)]
    self.user_type_index += 1
    num_jobs = random.randint(1, sim_config.CONFIG.get_num_jobs(user_type))
    for _ in range(num_jobs):
      self.jobs.append(self.generate_job(user_request_time, user_type))
  
  def generate_jobs(self, start_time: int, end_time: int) -> list[Job]:
    time = start_time
    while time < end_time:
      user_request_time = int(time + generate_interarrival_time())
      self.handle_user_request(user_request_time)
      time = user_request_time
    return self.jobs

  def get_jobs(self) -> list[Job]:
    return self.jobs
  
  def print_jobs(self):
    trace_print(f"Pending jobs: {len(self.jobs)}")
    # Print as a JSON list with each job object on a single line
    # Only include fields relevant for scenario initialization (constructor parameters)
    print("[")
    for i, job in enumerate(self.jobs):
      if i > 0:
        print(",")
      # Only output constructor-relevant fields
      scenario_job = {
        'id': job.id,
        'type': job.type,
        'user_type': job.user_type,
        'submission_time': job.submission_time
      }
      print(json.dumps(scenario_job), end="")
    print("\n]")

def main():
  parser = argparse.ArgumentParser(description="Generate jobs for a simulation time window")
  parser.add_argument("duration", type=parse_duration_hms, help="Simulation time in H:M:S (e.g., 1:30:00)")
  parser.add_argument("--config", "-c", metavar="FILE", help="Load simulation configuration from JSON file")
  parser.add_argument("--debug", "-debug", choices=["trace", "full"], metavar="LEVEL", help="Enable debug output: 'trace' for basic info, 'full' for detailed output")
  args = parser.parse_args()

  # Set debug level if provided
  if args.debug:
    from .debug_config import set_debug
    set_debug(args.debug)
  
  # Load config if provided
  if args.config:
    sim_config.load_config(args.config)

  generator = JobGenerator()
  generator.generate_jobs(0, args.duration)
  generator.print_jobs()

if __name__ == "__main__":
  main()





# Job generator
# Generates a series of job sumbmitions

import random
import json
import argparse
from time_def import MINUTE, HOUR


# Job types: S - small, M - medium, L - large
JOB_TYPES = ['S'] * 10 + ['M'] * 70 + ['L'] * 20 # fixed ratios
random.shuffle(JOB_TYPES)

JOB_DURATIONS = {'S': 10 * MINUTE, 'M': 40 * MINUTE, 'L': 90 * MINUTE}
JOB_EXECUTION_DURATIONS = {'S': 1 * MINUTE, 'M': 4 * MINUTE, 'L': int(6.5 * MINUTE)}

#Users Types (subscription types) F - free, C - creator S - studio
USER_TYPES = ['F'] * 10 + ['C'] * 70 + ['S'] * 20
random.shuffle(USER_TYPES)
USER_ALLOWED_JOBS = {'F': 1, 'C': 2, 'S': 6}
# # Users requests per hour
LAMBDA_USERS_REQUESTS_PER_HOUR = 20

def generate_interarrival_time() -> int:
  return int(random.expovariate(LAMBDA_USERS_REQUESTS_PER_HOUR / HOUR))

def parse_duration_hms(value: str) -> int:
  parts = value.split(":")
  if len(parts) != 3:
    raise argparse.ArgumentTypeError("duration must be in H:M:S format")
  try:
    hours, minutes, seconds = (int(p) for p in parts)
  except ValueError:
    raise argparse.ArgumentTypeError("duration components must be integers")
  if hours < 0 or not (0 <= minutes < 60) or not (0 <= seconds < 60):
    raise argparse.ArgumentTypeError("duration must satisfy H>=0, 0<=M<60, 0<=S<60")
  return hours * HOUR + minutes * MINUTE + seconds

class Job:
  def __init__(self, id, type, user_type, submission_time, start_execution_time=0):
    self.id = id
    self.type = type
    self.user_type = user_type
    self.submission_time = submission_time
    self.start_execution_time = start_execution_time

  def to_dict(self):
    return {
      'id': self.id,
      'type': self.type,
      'user_type': self.user_type,
      'submission_time': self.submission_time,
      'start_execution_time': self.start_execution_time
    }

  def to_json(self):
    return json.dumps(self.to_dict())

  def __str__(self):
    return f"Job(id={self.id}, type={self.type}, user_type={self.user_type}, submission_time={self.submission_time}, start_execution_time={self.start_execution_time})"

  def __repr__(self):
    return self.__str__()

  def get_execution_duration(self):
    return JOB_EXECUTION_DURATIONS[self.type]

  def get_duration(self):
    return JOB_DURATIONS[self.type]

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
  
class JobGenerator:
  def __init__(self):
    self.user_type_index = 0
    self.job_type_index = 0
    self.job_id = 0
    self.jobs: list[Job] = []

  def generate_job(self, user_request_time: int, user_type: str) -> Job:
    job_type = JOB_TYPES[self.job_type_index % len(JOB_TYPES)]
    self.job_type_index += 1
    job = Job(
      id=self.job_id,
      type=job_type,
      user_type=user_type,
      submission_time=user_request_time)
    self.job_id += 1
    return job

  def handle_user_request(self, user_request_time: int) -> None:
    user_type = USER_TYPES[self.user_type_index % len(USER_TYPES)]
    self.user_type_index += 1
    num_jobs = random.randint(1, USER_ALLOWED_JOBS[user_type])
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
    print(f"Pending jobs: {len(self.jobs)}")
    for job in self.jobs:
      job_json = job.to_dict()
      print(job_json)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Generate jobs for a simulation time window")
  parser.add_argument("duration", type=parse_duration_hms, help="Simulation time in H:M:S (e.g., 1:30:00)")
  args = parser.parse_args()

  generator = JobGenerator()
  generator.generate_jobs(0, args.duration)
  generator.print_jobs()





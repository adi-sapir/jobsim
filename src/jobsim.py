import random
import json
from event_queue import EventQueue, Event
from dataclasses import dataclass, asdict
from enum import Enum
import sys

@dataclass
class Job:
  id: str
  type: str
  user_type: str
  submission_time: int
  start_execution_time: int = 0
    
    
#Time constants
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

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
LAMBDA_USERS_REQUESTS_PER_HOUR = 100

# Job resources
STANDABY_WORKERS = 2
MAX_DEALLOCATED_WORKERS = 20
MAX_COLD_WORKERS = 30
WORKER_STARTUP_TIME = 10 * MINUTE
WORKER_SHUTDOWN_TIME = 30 * MINUTE
WORKER_ALLOCATE_TIME = 3 * MINUTE

# Simulation parameters
SIMULATION_DURATION = 10 * MINUTE

#Event Types
class EventType(Enum):
   JOB_SUBMITTED = "job_submitted"
   STANDBY_WORKER_READY = "standby_worker_ready"
   DEALLOCATED_WORKER_READY = "deallocated_worker_ready"
   COLD_WORKER_READY = "cold_worker_ready"
   DEALLOCATED_WORKER_READY_FROM_POOL = "deallocated_worker_ready_from_pool"
   COLD_WORKER_READY_FROM_POOL = "cold_worker_ready_from_pool"
# Job Events Generation
def generate_interarrival_time() -> int:
   return random.expovariate(LAMBDA_USERS_REQUESTS_PER_HOUR / HOUR)

#=============Job Generator=============
class JobGenerator:
  def __init__(self):
    self.user_type_index = 0
    self.job_type_index = 0
    self.job_id = 0

job_generator = JobGenerator()

def handle_user_request(user_request_time, job_generator):
  #Select type of user
  user_type = USER_TYPES[job_generator.user_type_index % len(USER_TYPES)]
  job_generator.user_type_index += 1
  #Generate the number of jobs to be submitted
  num_jobs = random.randint(1, USER_ALLOWED_JOBS[user_type])
  for _ in range(num_jobs):
     create_job(user_request_time, user_type, job_generator)

def create_job(user_request_time, user_type, job_generator):
  job_type = JOB_TYPES[job_generator.job_type_index % len(JOB_TYPES)]
  job_generator.job_type_index += 1
  job = Job(
    id=job_generator.job_id,
    type=job_type,
    user_type=user_type,
    submission_time=user_request_time)
  job_generator.job_id += 1
  # Create Event for the job
  sim_state.event_queue.push(
      user_request_time, 
      event_type=EventType.JOB_SUBMITTED, 
      data=job)

def init_jobs_in_queue():
  time = 0
  while time < SIMULATION_DURATION:
    #Generate next user request time
    user_request_time = int(time + generate_interarrival_time())
    handle_user_request(user_request_time, job_generator )
    #Update the time
    time = user_request_time

def print_pending_jobs(job_generator):
   print(f"Pending jobs: {len(job_generator.pending_jobs)}")
   for job in job_generator.pending_jobs:
      job_json = asdict(job)
      print(job_json)

#=============Simulation State=============
class SimState:
   def __init__(self):
      self.sim_time = 0
      self.workers_available = {
        'standby': STANDABY_WORKERS,
        'deallocated': 0,
        'cold': 0
      }
      self.workers_pool = {
        'deallocated': MAX_DEALLOCATED_WORKERS,
        'cold': MAX_COLD_WORKERS
      }
      self.event_queue = EventQueue()
      self.pending_jobs: list[Job] = []
      self.completed_jobs: list[Job] = []

sim_state = SimState()

def handle_worker_ready(worker_ready_time):
  sim_state.workers_available['standby'] += 1
  #Run pending job
  while sim_state.pending_jobs and sim_state.workers_available['standby'] > 0:
    job = sim_state.pending_jobs.pop(0)
    job.start_execution_time = worker_ready_time
    sim_state.completed_jobs.append(job)
    sim_state.workers_available['standby'] -= 1
    sim_state.event_queue.push(
        sim_state.sim_time + get_job_execution_duration(job.type), 
        event_type=EventType.STANDBY_WORKER_READY)
  
def handle_job_submitted(job_submitted_time, job):
  if allocate_worker(job_submitted_time, job):
    sim_state.completed_jobs.append(job)
  else:
    sim_state.pending_jobs.append(job)
    invoke_worker(job_submitted_time)

def invoke_worker(job_submitted_time) -> None:
  if sim_state.workers_pool['deallocated'] > 0:
    sim_state.event_queue.push(job_submitted_time + WORKER_ALLOCATE_TIME, 
        event_type=EventType.DEALLOCATED_WORKER_READY_FROM_POOL)
  elif sim_state.workers_pool['cold'] > 0:
    sim_state.event_queue.push(job_submitted_time + WORKER_STARTUP_TIME, 
        event_type=EventType.COLD_WORKER_READY_FROM_POOL)
  else:
    return

def allocate_worker(job_submitted_time, job):
  if sim_state.workers_available['standby'] > 0:
    sim_state.workers_available['standby'] -= 1
    job.start_execution_time = job_submitted_time
    sim_state.completed_jobs.append(job)
    sim_state.event_queue.push(
        job_submitted_time + get_job_execution_duration(job.type), 
        event_type=EventType.STANDBY_WORKER_READY)
    return True
  elif sim_state.workers_available['deallocated'] > 0:
    sim_state.workers_available['deallocated'] -= 1
    job.start_execution_time = job_submitted_time
    sim_state.completed_jobs.append(job)
    sim_state.event_queue.push(
        job_submitted_time + get_job_execution_duration(job.type), 
        event_type=EventType.DEALLOCATED_WORKER_READY)
    return True
  elif sim_state.workers_available['cold'] > 0:
    sim_state.workers_available['cold'] -= 1
    job.start_execution_time = job_submitted_time
    sim_state.completed_jobs.append(job)
    sim_state.event_queue.push(
        job_submitted_time + get_job_execution_duration(job.type), 
        event_type=EventType.COLD_WORKER_READY)
    return True
  return False

def init_sim_state():
  sim_state.sim_time = 0
  sim_state.available_workers = STANDABY_WORKERS

#run main
if __name__ == "__main__":
  #Create the event queue
  init_jobs_in_queue()
  print(f"USER_TYPES: {USER_TYPES}")
  print(f"JOB_TYPES: {JOB_TYPES}")
  print(f"Simulation duration: {SIMULATION_DURATION} seconds")
  print(f"Queue size: {sim_state.event_queue.size()}")
  print(f"Queue: {sim_state.event_queue}")
  sys.exit()
  #Initiate the simulation
  init_sim_state()
  while not sim_state.event_queue.is_empty():
    event = sim_state.event_queue.pop()
    print(f"Event: {event.timestamp}, {event.event_type}, {event.data}")
    if event.event_type == EventType.WORKER_READY:
      handle_worker_ready(event.timestamp, job_generator)
    elif event.event_type == EventType.JOB_SUBMITTED:
      handle_job_submitted(event.timestamp, event.data)
    else:
      print(f"Unknown event type: {event.event_type}")
      exit
    
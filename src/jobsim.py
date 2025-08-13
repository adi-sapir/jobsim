import random
import json
from event_queue import EventQueue, Event
from dataclasses import dataclass, asdict
from enum import Enum
import sys



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
   DEALLOCATED_WORKER_TO_POOL = "deallocated_worker_to_pool"
   COLD_WORKER_TO_POOL = "cold_worker_to_pool"

def get_event_type_to_pool_from_worker_type(worker_type):
   if worker_type == 'deallocated':
      return EventType.DEALLOCATED_WORKER_TO_POOL
   elif worker_type == 'cold':
      return EventType.COLD_WORKER_TO_POOL

def get_event_type_ready_from_worker_type(worker_type):
   if worker_type == 'standby':
      return EventType.STANDBY_WORKER_READY
   elif worker_type == 'deallocated':
      return EventType.DEALLOCATED_WORKER_READY
   elif worker_type == 'cold':
      return EventType.COLD_WORKER_READY

def get_worker_shutdown_time_from_worker_type(worker_type):
   if worker_type == 'standby':
      return 0
   elif worker_type == 'deallocated':
      return 0
   elif worker_type == 'cold':
      return WORKER_SHUTDOWN_TIME




def init_jobs_in_queue():
  



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

def handle_worker_ready(worker_ready_time, worker_type):
  sim_state.workers_available[worker_type] += 1
  #Run pending job
  if sim_state.pending_jobs:
    job = sim_state.pending_jobs.pop(0)
    job.start_execution_time = worker_ready_time
    sim_state.completed_jobs.append(job)
    sim_state.workers_available[worker_type] -= 1
    sim_state.event_queue.push(
        worker_ready_time + JOB_EXECUTION_DURATIONS[job.type],
        event_type=get_event_type_ready_from_worker_type(worker_type))
  else:
    sim_state.event_queue.push(
        worker_ready_time + get_worker_shutdown_time_from_worker_type(worker_type), 
        event_type=get_event_type_to_pool_from_worker_type(worker_type))

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
    if event.event_type == EventType.STANDBY_WORKER_READY:
      handle_worker_ready(event.timestamp, 'standby')
    elif event.event_type == EventType.DEALLOCATED_WORKER_READY:
      handle_worker_ready(event.timestamp, 'deallocated')
    elif event.event_type == EventType.COLD_WORKER_READY:
      handle_worker_ready(event.timestamp, 'cold')
    elif event.event_type == EventType.JOB_SUBMITTED:
      handle_job_submitted(event.timestamp, event.data)
    
    else:
      print(f"Unknown event type: {event.event_type}")
      exit
    
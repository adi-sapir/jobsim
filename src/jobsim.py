import random
from event_queue import EventQueue, Event
from dataclasses import dataclass

@dataclass
class Job:
    id: str
    type: str
    duration: int
    execution_duration: int
    submission_time: int
    start_execution_time: int = 0
    end_execution_time: int = 0
    status: str = 'pending'
    
# Some constants
#Time constants
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

# Job types: S - small, M - medium, L - large
JOB_TYPES = ['S'] * 10 + ['M'] * 70 + ['L'] * 20 # fixed ratios
random.shuffle(JOB_TYPES)

JOB_DURATIONS = {'S': 10 * MINUTE, 'M': 40 * MINUTE, 'L': 90 * MINUTE}
JOB_EXECUTION_DURATIONS = {'S': 1 * MINUTE, 'M': 4 * MINUTE, 'L': 6.5 * MINUTE}

#Users Types (subscription types) F - free, C - creator S - studio
USER_TYPES = ['F'] * 10 + ['C'] * 70 + ['S'] * 20
random.shuffle(USER_TYPES)
USER_ALLOWED_JOBS = {'F': 1, 'C': 2, 'S': 6}
# # Users requests per hour
LAMBDA_USERS_REQUESTS_PER_HOUR = 100

# Job resources
STANDABY_WORKERS = 2
MAX_DEALLOCATED_WORKERS = 20
MAX_STOPPED_WORKERS = 30
WORKER_STARTUP_TIME = 10 * MINUTE
WORKER_SHUTDOWN_TIME = 30 * MINUTE
WORKER_MAREGINTENANCE_TIME = 3 * MINUTE

# Simulation parameters
SIMULATION_DURATION = 10 * MINUTE
SIMULATION_START_TIME = 0

# Job Events Generation
def generate_interarrival_time() -> int:
   return random.expovariate(LAMBDA_USERS_REQUESTS_PER_HOUR / HOUR)

#run main
if __name__ == "__main__":
  eq = EventQueue()
  #Create the event queue
  time = 0
  user_type_index = 0
  job_type_index = 0
  job_id = 0
  while time < SIMULATION_DURATION:
    #Generate next user request time
    user_request_time = time + generate_interarrival_time()
    #Select type of user
    user_type = USER_TYPES[user_type_index % len(USER_TYPES)]
    user_type_index += 1
    #Generate the number of jobs to be submitted
    num_jobs = random.randint(1, USER_ALLOWED_JOBS[user_type])
    for _ in range(num_jobs):
      job_type = JOB_TYPES[job_type_index % len(JOB_TYPES)]
      job_type_index += 1
      job = Job(
         id=job_id,
         type=job_type,
         duration=JOB_DURATIONS[job_type],
         execution_duration=JOB_EXECUTION_DURATIONS[job_type],
         submission_time=user_request_time)
      job_id += 1
      # Create Event for the job
      job_event = Event(timestamp=user_request_time, event_type="submit_job", data=job)
      eq.push_event(job_event)
    #Update the time
    time = user_request_time
    

    print(f"USER_TYPES: {USER_TYPES}")
    print(f"JOB_TYPES: {JOB_TYPES}")
    print(f"Simulation duration: {SIMULATION_DURATION} seconds")
    print(f"Queue size: {eq.size()}")
    print(f"Queue: {eq}")
  
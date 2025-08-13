from event_queue import EventQueue, Event
from enum import Enum
import sys
import argparse
from workers_model import WorkerPool, WorkerType, WorkerStatus
from jobgen import JobGenerator, Job
from time_def import MINUTE, HOUR
from debug_config import debug_print, set_debug, get_debug
import matplotlib.pyplot as plt


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


#Event Types
class EventType(Enum):
   JOB_SUBMITTED = "job_submitted"
   WORKER_DONE = "worker_done"
   WORKER_READY = "worker_ready"
   WORKER_TO_POOL = "worker_to_pool"


#=============Simulation State=============
class SimState:
  def __init__(self):
      self.event_queue = EventQueue()
      self.workers_pool = WorkerPool()
      self.pending_jobs: list[Job] = []
      self.completed_jobs: list[Job] = []
  
  def get_event_queue(self):
    return self.event_queue
  
  def get_workers_pool(self):
    return self.workers_pool
  
  def get_pending_jobs(self):
    return self.pending_jobs
  
  def get_completed_jobs(self):
    return self.completed_jobs
  
  def init_jobs_in_queue(self, jobs: list[Job]):
    for job in jobs:
      self.event_queue.push(job.submission_time, EventType.JOB_SUBMITTED, job)

  def handle_job_submitted(self, job_submitted_time, job) -> None:
    if (worker := self.workers_pool.allocate_ready_worker()) is not None:
      job.set_start_execution_time(job_submitted_time)
      self.completed_jobs.append(job)
      self.event_queue.push(job_submitted_time + job.get_execution_duration(), EventType.WORKER_DONE, worker)
    else:
      self.pending_jobs.append(job)
      if (worker := self.workers_pool.invoke_worker()) is not None:
        self.event_queue.push(job_submitted_time + worker.get_worker_activation_time(), EventType.WORKER_TO_POOL, worker)

  def handle_worker_ready(self, worker_ready_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.READY)
    if self.pending_jobs:
      self.handle_job_submitted(worker_ready_time, self.pending_jobs.pop(0))
    else:
      self.event_queue.push(worker_ready_time + worker.get_worker_shutdown_time(), EventType.WORKER_TO_POOL, worker)

  def handle_worker_to_pool(self, worker_to_pool_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.IN_POOL)

  def run(self):
    while not self.event_queue.is_empty():
      event = self.event_queue.pop()
      event_time = event.timestamp
      if event.event_type == EventType.JOB_SUBMITTED:
        self.handle_job_submitted(event.timestamp, event.data)
        debug_print(f"{event_time}: Job submitted: {event.data}")
      elif event.event_type == EventType.WORKER_READY:
        self.handle_worker_ready(event.timestamp, event.data)
        debug_print(f"{event_time}: Worker ready: {event.data}")
      elif event.event_type == EventType.WORKER_DONE:
        self.handle_worker_ready(event.timestamp, event.data)
        debug_print(f"{event_time}: Worker done: {event.data}")
      elif event.event_type == EventType.WORKER_TO_POOL:
        self.handle_worker_to_pool(event.timestamp, event.data)
        debug_print(f"{event_time}: Worker to pool: {event.data}")

  def print_statistics(self) -> None:
    print(f"Queue size: {self.event_queue.size()}")
    print(f"Queue: {self.event_queue}")
    debug_print(f"Completed jobs: {self.completed_jobs}")

    submission_times = [j.get_submission_time() for j in self.completed_jobs]
    wait_times = [j.get_start_execution_time() - j.get_submission_time() for j in self.completed_jobs]
    debug_print(f"Wait times: {wait_times}")

    print(f"Simulated {len(self.completed_jobs)} jobs")
    print(f"Min Wait Time: {min(wait_times):.1f} sec")
    print(f"Avg Wait Time: {sum(wait_times)/len(wait_times):.1f} sec")
    print(f"Max Wait Time: {max(wait_times):.1f} sec")

    plt.hist(submission_times, bins=20, edgecolor='black')
    plt.xlabel('Submission Time (seconds)')
    plt.ylabel('Number of Jobs')
    plt.title('Submission Time Distribution')
    plt.savefig('submission_time_distribution.png')
    plt.clf()

    plt.hist(wait_times, bins=20, edgecolor='black')
    plt.xlabel('Wait Time (seconds)')
    plt.ylabel('Number of Jobs')
    plt.title('Wait Time Distribution')
    plt.savefig('wait_time_distribution.png')
    plt.show()
    return

#run main
if __name__ == "__main__":
  # Parse CLI duration H:M:S and set simulation duration
  parser = argparse.ArgumentParser(description="JobSim - job execution simulation")
  parser.add_argument("duration", type=parse_duration_hms, help="Simulation time in H:M:S (e.g., 1:30:00)")
  parser.add_argument("--debug", "-debug", action="store_true", help="Enable debug output")
  args = parser.parse_args()

  set_debug(args.debug)
  debug_print("JobSim starting...")

  sim_duration = args.duration
  job_generator = JobGenerator()
  sim_state = SimState()
  sim_state.init_jobs_in_queue(job_generator.generate_jobs(0, sim_duration))
  #Create the event queue and initialize jobs
  print(f"Simulation duration: {sim_duration} seconds")
  print(f"Queue size: {sim_state.event_queue.size()}")
  print(f"Queue: {sim_state.event_queue}")
  # sys.exit()
  sim_state.run()
  sim_state.print_statistics()
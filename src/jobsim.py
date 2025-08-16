from event_queue import EventQueue, Event
from enum import Enum
import sys
import argparse
from workers_model import WorkerPool, WorkerType, WorkerStatus
from time_def import MINUTE, HOUR
from debug_config import debug_print, set_debug, get_debug
import matplotlib.pyplot as plt
from jobgen import JobGenerator, Job
from datetime import datetime
import os
import sim_config 
from sim_histogram import SimHistogram


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
      self.run_name: str | None = None
  
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
      job.set_server_type(worker.get_worker_type())
      job.set_server_id(worker.get_worker_id())
      self.completed_jobs.append(job)
      self.event_queue.push(job_submitted_time + job.get_execution_duration(), EventType.WORKER_DONE, worker)
      debug_print(f"{job_submitted_time}: Job submitted: {job} by worker {worker}")
    else:
      self.pending_jobs.append(job)
      debug_print(f"{job_submitted_time}: Job pending: {job}")
      if (worker := self.workers_pool.invoke_worker()) is not None:
        self.event_queue.push(job_submitted_time + worker.get_worker_activation_time(), EventType.WORKER_READY, worker)
        debug_print(f"{job_submitted_time}: Invoking worker: {worker}")

  def handle_worker_ready(self, worker_ready_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.READY)
    debug_print(f"{worker_ready_time}: Worker ready: {worker}")
    if self.pending_jobs:
      job = self.pending_jobs.pop(0)
      self.handle_job_submitted(worker_ready_time, job)
      debug_print(f"{worker_ready_time}: Job submitted: {job} by worker {worker}")
    else:
      self.event_queue.push(worker_ready_time + worker.get_worker_shutdown_time(), EventType.WORKER_TO_POOL, worker)
      debug_print(f"{worker_ready_time}: Sending Worker to pool: {worker}")

  def handle_worker_to_pool(self, worker_to_pool_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.IN_POOL)
    debug_print(f"{worker_to_pool_time}: Worker to pool: {worker}")

  def run(self):
    while not self.event_queue.is_empty():
      event = self.event_queue.pop()
      event_time = event.timestamp
      if event.event_type == EventType.JOB_SUBMITTED:
        self.handle_job_submitted(event.timestamp, event.data)
      elif event.event_type == EventType.WORKER_READY:
        self.handle_worker_ready(event.timestamp, event.data)
      elif event.event_type == EventType.WORKER_DONE:
        self.handle_worker_ready(event.timestamp, event.data)
      elif event.event_type == EventType.WORKER_TO_POOL:
        self.handle_worker_to_pool(event.timestamp, event.data)

  def print_submitted_jobs(self) -> None:
    print("Submitted Jobs distribution over time (seconds):")
    print("================================================")
    histogram = SimHistogram([j.get_submission_time() for j in self.completed_jobs])
    histogram.print_histogram()
  
  def print_wait_times(self) -> None:
    wait_times = [j.get_start_execution_time() - j.get_submission_time()
      for j in self.completed_jobs]
    if wait_times:
      print("Wait Time distribution (seconds):")
      print("=================================")
      print(f"Min Wait Time: {min(wait_times):.1f} sec")
      print(f"Avg Wait Time: {sum(wait_times)/len(wait_times):.1f} sec")
      print(f"Max Wait Time: {max(wait_times):.1f} sec")
      histogram = SimHistogram(wait_times)
      histogram.print_histogram()
    
  def print_workers_used(self) -> None:
    worker_types = sorted(
      {j.get_server_type() for j in self.completed_jobs if j.get_server_type() is not None},
      key=lambda t: t.value
    )
    print("Workers used:")
    print("=============")
    for wt in worker_types:
      distinct_ids = {j.get_server_id() for j in self.completed_jobs if j.get_server_type() == wt}
      print(f"Workers used ({wt.value}): {len(distinct_ids)}")
  
  def print_statistics(self) -> None:
    run_label = f" [{self.run_name}]" if getattr(self, "run_name", None) else ""
    suffix = f"_{self.run_name}" if getattr(self, "run_name", None) else ""
    debug_print(f"Queue size: {self.event_queue.size()}")
    debug_print(f"Queue: {self.event_queue}")
    debug_print(f"Completed jobs: {self.completed_jobs}")
    debug_print(f"Run{run_label}: Simulated {len(self.completed_jobs)} jobs")
    simlated_time = max(j.get_start_execution_time() for j in self.completed_jobs)
    print(f"Run{run_label}: Simulated {len(self.completed_jobs)} jobs in {simlated_time} seconds ")
    self.print_submitted_jobs()
    self.print_wait_times()
    self.print_workers_used()
    return

#run main
if __name__ == "__main__":
  # Parse CLI duration H:M:S and optional config
  parser = argparse.ArgumentParser(description="JobSim - job execution simulation")
  parser.add_argument("duration", type=parse_duration_hms, help="Simulation time in H:M:S (e.g., 1:30:00)")
  parser.add_argument("--debug", "-debug", action="store_true", help="Enable debug output")
  parser.add_argument("--config", "-c", metavar="FILE", help="Load simulation configuration from JSON file")
  parser.add_argument("--run-name", "-n", metavar="NAME", help="Name of this simulation run (used in outputs)")
  args = parser.parse_args()

  set_debug(args.debug)
  debug_print("JobSim starting...")

  sim_duration = args.duration
  # Load config if provided and create generator with it
  from sim_config import load_config, CONFIG
  if args.config:
    load_config(args.config)
  job_generator = JobGenerator()

  sim_state = SimState()
  # Precedence: explicit run-name > config filename > timestamp, and always append sim-<seconds>
  base_name = (
    args.run_name
    or (os.path.splitext(os.path.basename(args.config))[0] if args.config else None)
    or datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
  )
  sim_state.run_name = f"{base_name}-sim-{sim_duration}"
  sim_state.init_jobs_in_queue(job_generator.generate_jobs(0, sim_duration))
  #Create the event queue and initialize jobs
  print(f"Starting Simulation. Job submission duration: {sim_duration} seconds")
  sim_state.run()
  print(f"Simulation ended")
  sim_state.print_statistics()
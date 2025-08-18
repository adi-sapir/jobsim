from .event_queue import EventQueue, Event
from enum import Enum
import sys
import argparse
from .workers_model import WorkerPool, WorkerStatus, POOL_PROPERTIES
from .time_def import MINUTE, HOUR, seconds_to_hms, parse_duration_hms
from .debug_config import debug_print, set_debug, get_debug, is_debug_enabled, is_trace_enabled, is_full_debug_enabled, full_debug_print, trace_print
from .jobgen import JobGenerator, Job
from datetime import datetime
import os
from . import sim_config
from .sim_histogram import SimHistogram, SimHistogramStacked





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
      trace_print(f"{job_submitted_time}: Job submitted: {job} by worker {worker}")
    else:
      self.pending_jobs.append(job)
      trace_print(f"{job_submitted_time}: Job pending: {job}")
      if (worker := self.workers_pool.invoke_worker()) is not None:
        trace_print(f"{job_submitted_time}: Invoking worker: {worker}")
        if (worker.get_worker_activation_time() == 0):
          worker.set_worker_status(WorkerStatus.READY)
          self.handle_worker_ready(job_submitted_time, worker)
        else:
          self.event_queue.push(job_submitted_time + worker.get_worker_activation_time(), EventType.WORKER_READY, worker)

  def handle_worker_ready(self, worker_ready_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.READY)
    trace_print(f"{worker_ready_time}: Worker ready: {worker}")
    if self.pending_jobs:
      job = self.pending_jobs.pop(0)
      self.handle_job_submitted(worker_ready_time, job)
    else:
      self.event_queue.push(worker_ready_time + worker.get_worker_shutdown_time(), EventType.WORKER_TO_POOL, worker)
      trace_print(f"{worker_ready_time}: Sending Worker to pool: {worker}")

  def handle_worker_to_pool(self, worker_to_pool_time, worker) -> None:
    worker.set_worker_status(WorkerStatus.IN_POOL)
    trace_print(f"{worker_to_pool_time}: Worker to pool: {worker}")

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
    jobs_types = {}
    for j in self.completed_jobs:
      if j.get_type() not in jobs_types:
        jobs_types[j.get_type()] = 0
      jobs_types[j.get_type()] += 1
    print("Submitted Jobs distribution:")
    print("============================")
    for jt in jobs_types:
      print(f"{jt}: {jobs_types[jt]}")
    print("Submitted Jobs distribution over time (seconds):")
    print("================================================")
    histogram = SimHistogramStacked([(j.get_submission_time(), j.get_type()) for j in self.completed_jobs])
    histogram.print_histogram()
  
  def print_wait_times(self) -> None:
    wait_times = [j.get_start_execution_time() - j.get_submission_time()
      for j in self.completed_jobs]
    if wait_times:
      print("Wait Time distribution (seconds):")
      print("=================================")
      print(f"Min Wait Time: {seconds_to_hms(min(wait_times))}")
      print(f"Avg Wait Time: {seconds_to_hms(sum(wait_times)/len(wait_times))}")
      print(f"Max Wait Time: {seconds_to_hms(max(wait_times))}")
      histogram = SimHistogram(wait_times)
      histogram.print_histogram()
    
  def print_workers_stats(self) -> None:
    workers_types_use = set()
    workers_types_worker_ids = {}
    workers_types_processing_time = {}
    total_processing_time = 0
    for j in self.completed_jobs:
      worker_type = j.get_server_type()
      if worker_type is not None:
        if worker_type not in workers_types_use:
          workers_types_use.add(worker_type)
          workers_types_worker_ids[worker_type] = set()
          workers_types_processing_time[worker_type] = 0
        workers_types_worker_ids[worker_type].add(j.get_server_id())
        workers_types_processing_time[worker_type] += j.get_execution_duration()
        total_processing_time += j.get_execution_duration()
    print("Workers used:")
    print("=============")
    for wt in workers_types_use:
      print(f"Workers used ({wt}): {len(workers_types_worker_ids[wt])}")
    for wt in workers_types_use:
      print(f"Processing time ({wt}): {seconds_to_hms(workers_types_processing_time[wt])}")
    print(f"Total processing time: {seconds_to_hms(total_processing_time)}")
    histogram = SimHistogramStacked(
        [(j.get_start_execution_time(),
          j.get_server_type() + "-" + str(j.get_server_id())
          ) for j in self.completed_jobs
          if j.get_server_type() is not None])
    print("Workers usage distribution:")
    print("===========================")
    histogram.print_histogram()

  def print_statistics(self) -> None:
    run_label = f" [{self.run_name}]" if getattr(self, "run_name", None) else ""
    suffix = f"_{self.run_name}" if getattr(self, "run_name", None) else ""
    full_debug_print(f"Queue size: {self.event_queue.size()}")
    full_debug_print(f"Queue: {self.event_queue}")
    full_debug_print(f"Completed jobs: {self.completed_jobs}")
    full_debug_print(f"Run{run_label}: Simulated {len(self.completed_jobs)} jobs")
    simlated_time = max(j.get_start_execution_time() for j in self.completed_jobs)
    print(f"Run{run_label}: Simulated {len(self.completed_jobs)} jobs in {seconds_to_hms(simlated_time)} ")
    print("")
    self.print_submitted_jobs()
    print("")
    self.print_wait_times()
    print("")
    self.print_workers_stats()
    return

def main():
  print("this is the new version of the jobsim")
  # Parse CLI duration H:M:S and optional config
  parser = argparse.ArgumentParser(description="JobSim - job execution simulation")
  parser.add_argument("duration", type=parse_duration_hms, help="Simulation time in H:M:S (e.g., 1:30:00)")
  parser.add_argument("--debug", "-debug", choices=["trace", "full"], metavar="LEVEL", help="Enable debug output: 'trace' for basic info, 'full' for detailed output")
  parser.add_argument("--config", "-c", metavar="FILE", help="Load simulation configuration from JSON file")
  parser.add_argument("--run-name", "-n", metavar="NAME", help="Name of this simulation run (used in outputs)")
  args = parser.parse_args()

  if args.debug:
    set_debug(args.debug)
    full_debug_print("JobSim starting...")
  else:
    trace_print("JobSim starting...")

  sim_duration = args.duration
  # Load config if provided and create generator with it
  from .sim_config import load_config, CONFIG
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
  print(f"Starting Simulation. Job submission duration: {seconds_to_hms(sim_duration)}")
  sim_state.run()
  print(f"Simulation ended")
  sim_state.print_statistics()

if __name__ == "__main__":
  main()
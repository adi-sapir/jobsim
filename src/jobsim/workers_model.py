# Workers model
import json
import argparse
from enum import Enum
from typing import Optional
from . import sim_config
from .debug_config import debug_print, trace_print, full_debug_print

class WorkerStatus(Enum):
  IN_POOL = 'in_pool'
  READY = 'ready'
  BUSY = 'busy'

class PoolProperties:
  def __init__(self, pool_size: int, pool_priority: int, worker_startup_time: int, worker_shutdown_time: int):
    self.pool_size = pool_size
    self.pool_priority = pool_priority
    self.worker_startup_time = worker_startup_time
    self.worker_shutdown_time = worker_shutdown_time

POOL_PROPERTIES = {}

class Worker:
  def __init__(self, worker_type: str, worker_id: int):
    self.worker_type = worker_type
    self.worker_status = WorkerStatus.IN_POOL
    self.worker_id = worker_id

  def to_dict(self):
    return {
      'worker_type': self.worker_type,
      'worker_status': self.worker_status,
      'worker_id': self.worker_id
    }

  def to_json(self):
    return json.dumps(self.to_dict())
  
  def __str__(self):
    return f"Worker(worker_type={self.worker_type}, worker_status={self.worker_status}, worker_id={self.worker_id})"

  def __repr__(self):
    return self.__str__()

  def get_worker_type(self):
    return self.worker_type

  def get_worker_status(self):
    return self.worker_status

  def get_worker_id(self):
    return self.worker_id

  def set_worker_status(self, worker_status: WorkerStatus):
    full_debug_print(f"Setting worker {self.worker_id} status from {self.worker_status} to {worker_status}")
    self.worker_status = worker_status

  def get_worker_activation_time(self):
    return POOL_PROPERTIES[self.worker_type].worker_startup_time

  def get_worker_shutdown_time(self):
    return POOL_PROPERTIES[self.worker_type].worker_shutdown_time

class WorkerPool:
  def __init__(self):
    self.workers: list[Worker] = []
    self.pool_priorities = []
    for worker_definition in sim_config.CONFIG.worker_definitions:
      POOL_PROPERTIES[worker_definition.worker_type] = PoolProperties(
        worker_definition.pool_size,
        worker_definition.pool_priority,
        worker_definition.worker_startup_time,
        worker_definition.worker_shutdown_time)
      self.pool_priorities.append(worker_definition.pool_priority)
    self.pool_priorities.sort()
    worker_idx = 0
    for worker_type, pool_properties in POOL_PROPERTIES.items():
      for _ in range(pool_properties.pool_size):
        worker = Worker(worker_type, worker_idx)
        worker.set_worker_status(WorkerStatus.IN_POOL)
        self.workers.append(worker)
        worker_idx += 1
    full_debug_print(f"WorkerPool initialized: {self.workers}")

  def get_workers(self):
    return self.workers

  def allocate_ready_worker(self) -> Optional[Worker]:
    for worker in self.workers:
      if worker.get_worker_status() == WorkerStatus.READY:
        worker.set_worker_status(WorkerStatus.BUSY)
        return worker
    return None

  def acquire_in_pool_worker_prioritized(self) -> Optional[Worker]:
    """Return an IN_POOL worker, preferring DEALLOCATED, then COLD. Sets status to READY."""
    for priority in self.pool_priorities:
      for worker_type, pool_properties in POOL_PROPERTIES.items(): 
        if pool_properties.pool_priority == priority:
          for worker in self.workers:
            if worker.get_worker_status() == WorkerStatus.IN_POOL and worker.get_worker_type() == worker_type:
              return worker
    return None
  
  def invoke_worker(self) -> Optional[Worker]:
    """Acquire an IN_POOL worker (deallocated first, else cold) and set READY."""
    return self.acquire_in_pool_worker_prioritized()
  


  
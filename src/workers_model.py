# Workers model
import json
import argparse
from enum import Enum
from typing import Optional
import sim_config
from debug_config import debug_print

class WorkerType(Enum):
  STANDBY = 'standby'
  DEALLOCATED = 'deallocated'
  COLD = 'cold'

class WorkerStatus(Enum):
  IN_POOL = 'in_pool'
  READY = 'ready'
  BUSY = 'busy'

class Worker:
  def __init__(self, worker_type: WorkerType, worker_id: int):
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
    if worker_status == WorkerStatus.IN_POOL and self.worker_status == WorkerStatus.READY and self.worker_type == WorkerType.STANDBY: #Standby worker is always ready
      return
    self.worker_status = worker_status

  def get_worker_activation_time(self):
    if self.worker_type == WorkerType.STANDBY:
      return 0
    elif self.worker_type == WorkerType.DEALLOCATED:
      return sim_config.CONFIG.worker_allocate_time
    elif self.worker_type == WorkerType.COLD:
      return sim_config.CONFIG.worker_startup_time

  def get_worker_shutdown_time(self):
    if self.worker_type == WorkerType.STANDBY:
      return 0
    elif self.worker_type == WorkerType.DEALLOCATED:
      return 0
    elif self.worker_type == WorkerType.COLD:
      return sim_config.CONFIG.worker_shutdown_time

class WorkerPool:
  def __init__(self):
    self.workers: list[Worker] = []
    worker_idx = 0
    debug_print(f"Initializing WorkerPool with {sim_config.CONFIG.standby_workers} standby workers, {sim_config.CONFIG.max_deallocated_workers} deallocated workers, and {sim_config.CONFIG.max_cold_workers} cold workers") 
    for _ in range(sim_config.CONFIG.standby_workers):
      worker = Worker(WorkerType.STANDBY, worker_idx)
      worker.set_worker_status(WorkerStatus.READY)
      self.workers.append(worker)
      worker_idx += 1
    for _ in range(sim_config.CONFIG.max_deallocated_workers):
      self.workers.append(Worker(WorkerType.DEALLOCATED, worker_idx))
      worker_idx += 1
    for _ in range(sim_config.CONFIG.max_cold_workers):
      self.workers.append(Worker(WorkerType.COLD, worker_idx))
      worker_idx += 1
    debug_print(f"WorkerPool initialized: {self.workers}")

  def add_worker(self, worker: Worker):
    self.workers.append(worker)

  def remove_worker(self, worker: Worker):
    self.workers.remove(worker)

  def get_workers(self):
    return self.workers

  def allocate_ready_worker(self) -> Optional[Worker]:
    for worker in self.workers:
      if worker.get_worker_status() == WorkerStatus.READY:
        worker.set_worker_status(WorkerStatus.BUSY)
        return worker
    return None
  
  def _find_in_pool_worker_by_type(self, worker_type: WorkerType) -> Optional[Worker]:
    for worker in self.workers:
      if worker.get_worker_status() == WorkerStatus.IN_POOL and worker.get_worker_type() == worker_type:
        return worker
    return None

  def acquire_in_pool_worker_prioritized(self) -> Optional[Worker]:
    """Return an IN_POOL worker, preferring DEALLOCATED, then COLD. Sets status to READY."""
    if (worker := self._find_in_pool_worker_by_type(WorkerType.DEALLOCATED)) is not None:
        return worker
    elif (worker := self._find_in_pool_worker_by_type(WorkerType.COLD)) is not None:
        return worker
    return None
  
  def invoke_worker(self) -> Optional[Worker]:
    """Acquire an IN_POOL worker (deallocated first, else cold) and set READY."""
    return self.acquire_in_pool_worker_prioritized()
  


  
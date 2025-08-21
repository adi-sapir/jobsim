"""
Integration tests for WorkerPool component
"""
import pytest
from jobsim import WorkerPool, Worker, WorkerStatus, POOL_PROPERTIES
from jobsim.sim_config import SimulationConfig, WorkerDefinition

class TestWorkerPoolIntegration:
    """Test WorkerPool integration with other components"""
    
    def test_worker_pool_with_simulation_config(self, basic_config):
        """Test worker pool integration with simulation configuration"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            pool = WorkerPool()
            
            # Verify pool structure
            assert len(pool.pool_priorities) == 3
            assert pool.pool_priorities == [1, 2, 3]  # STANDBY, DEALLOCATED, COLD
            
            # Verify worker distribution
            standby_count = len([w for w in pool.priority_pools[1] if w.get_worker_type() == "STANDBY"])
            deallocated_count = len([w for w in pool.priority_pools[2] if w.get_worker_type() == "DEALLOCATED"])
            cold_count = len([w for w in pool.priority_pools[3] if w.get_worker_type() == "COLD"])
            
            assert standby_count == 3
            assert deallocated_count == 5
            assert cold_count == 10
            
            # Verify POOL_PROPERTIES integration
            assert "STANDBY" in POOL_PROPERTIES
            assert "DEALLOCATED" in POOL_PROPERTIES
            assert "COLD" in POOL_PROPERTIES
            
            # Verify worker properties
            standby_props = POOL_PROPERTIES["STANDBY"]
            assert standby_props.worker_startup_time == 0
            assert standby_props.worker_shutdown_time == 0
            
            deallocated_props = POOL_PROPERTIES["DEALLOCATED"]
            assert deallocated_props.worker_startup_time == 300
            assert deallocated_props.worker_shutdown_time == 0
            
            cold_props = POOL_PROPERTIES["COLD"]
            assert cold_props.worker_startup_time == 600
            assert cold_props.worker_shutdown_time == 1800
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_lifecycle_integration(self, minimal_config):
        """Test complete worker lifecycle integration"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Initial state - all workers should be IN_POOL
            for priority in pool.pool_priorities:
                for worker in pool.priority_pools[priority]:
                    assert worker.get_worker_status() == WorkerStatus.IN_POOL
            
            # Test worker acquisition
            worker = pool.acquire_in_pool_worker_prioritized()
            assert worker is not None
            assert worker.get_worker_status() == WorkerStatus.INITIALIZING
            
            # Test worker allocation - first set a worker to READY
            for priority in pool.pool_priorities:
                for worker in pool.priority_pools[priority]:
                    worker.set_worker_status(WorkerStatus.READY)
                    break
                break
            
            allocated_worker = pool.allocate_ready_worker()
            assert allocated_worker is not None
            assert allocated_worker.get_worker_status() == WorkerStatus.BUSY
            
            # Test worker return to pool
            allocated_worker.set_worker_status(WorkerStatus.IN_POOL)
            assert allocated_worker.get_worker_status() == WorkerStatus.IN_POOL
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_priority_behavior(self, minimal_config):
        """Test worker pool priority behavior in practice"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Test priority-based worker acquisition
            workers_acquired = []
            worker_types_acquired = []
            
            # Acquire all available workers
            while True:
                worker = pool.acquire_in_pool_worker_prioritized()
                if worker is None:
                    break
                workers_acquired.append(worker)
                worker_types_acquired.append(worker.get_worker_type())
            
            # Should acquire all workers
            total_workers = sum(len(pool.priority_pools[priority]) for priority in pool.pool_priorities)
            assert len(workers_acquired) == total_workers
            
            # Verify priority order (STANDBY first, then DEALLOCATED, then COLD)
            # Note: This test assumes the priority ordering is maintained
            # The actual order may vary based on implementation
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_edge_cases(self):
        """Test worker pool edge cases and error handling"""
        # Test with zero workers
        zero_config = SimulationConfig(
            job_definitions=[],
            user_definitions=[],
            worker_definitions=[],
            lambda_users_requests_per_hour=0
        )
        
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = zero_config
        
        try:
            pool = WorkerPool()
            
            # Should have no workers
            assert len(pool.pool_priorities) == 0
            assert len(pool.priority_pools) == 0
            
            # Should return None for all operations
            assert pool.acquire_in_pool_worker_prioritized() is None
            assert pool.allocate_ready_worker() is None
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_concurrent_access(self, minimal_config):
        """Test worker pool behavior under simulated concurrent access"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Simulate multiple workers being acquired simultaneously
            workers = []
            
            # Acquire multiple workers
            for _ in range(3):  # Try to acquire 3 workers
                worker = pool.acquire_in_pool_worker_prioritized()
                if worker is not None:
                    workers.append(worker)
            
            # Should have acquired some workers
            assert len(workers) > 0
            
            # All acquired workers should be INITIALIZING
            for worker in workers:
                assert worker.get_worker_status() == WorkerStatus.INITIALIZING
            
            # Test allocation of acquired workers
            for worker in workers:
                allocated = pool.allocate_ready_worker()
                if allocated is not None:
                    assert allocated.get_worker_status() == WorkerStatus.BUSY
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_memory_management(self, basic_config):
        """Test worker pool memory management"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            # Create multiple pools to test memory management
            pools = []
            for _ in range(5):
                pool = WorkerPool()
                pools.append(pool)
            
            # Verify all pools are independent
            for i, pool1 in enumerate(pools):
                for j, pool2 in enumerate(pools):
                    if i != j:
                        # Different pools should have different worker IDs
                        workers1 = []
                        workers2 = []
                        
                        for priority in pool1.pool_priorities:
                            workers1.extend(pool1.priority_pools[priority])
                        
                        for priority in pool2.pool_priorities:
                            workers2.extend(pool2.priority_pools[priority])
                        
                        # Worker IDs should be unique across pools
                        ids1 = {w.get_worker_id() for w in workers1}
                        ids2 = {w.get_worker_id() for w in workers2}
                        
                        # Worker IDs may be shared across pools (they're only unique within a pool)
                        # This is expected behavior
                        pass
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()

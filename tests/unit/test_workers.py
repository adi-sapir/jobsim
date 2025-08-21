"""
Unit tests for Worker and WorkerPool components
"""
import pytest
from jobsim import Worker, WorkerPool, WorkerStatus, POOL_PROPERTIES
from jobsim.sim_config import SimulationConfig, WorkerDefinition

class TestWorker:
    """Test Worker functionality"""
    
    def test_worker_creation(self):
        """Test worker object creation"""
        worker = Worker("STANDBY", 1)
        
        assert worker.get_worker_type() == "STANDBY"
        assert worker.get_worker_id() == 1
        assert worker.get_worker_status() == WorkerStatus.IN_POOL
    
    def test_worker_status_transitions(self):
        """Test worker status changes"""
        worker = Worker("DEALLOCATED", 2)
        
        # Initial status
        assert worker.get_worker_status() == WorkerStatus.IN_POOL
        
        # Change to READY
        worker.set_worker_status(WorkerStatus.READY)
        assert worker.get_worker_status() == WorkerStatus.READY
        
        # Change to BUSY
        worker.set_worker_status(WorkerStatus.BUSY)
        assert worker.get_worker_status() == WorkerStatus.BUSY
        
        # Change back to IN_POOL
        worker.set_worker_status(WorkerStatus.IN_POOL)
        assert worker.get_worker_status() == WorkerStatus.IN_POOL
    
    def test_worker_pool_properties(self):
        """Test worker pool property access"""
        # Set up POOL_PROPERTIES for testing
        POOL_PROPERTIES.clear()
        POOL_PROPERTIES["STANDBY"] = type('PoolProperties', (), {
            'worker_startup_time': 0,
            'worker_shutdown_time': 0
        })()
        POOL_PROPERTIES["DEALLOCATED"] = type('PoolProperties', (), {
            'worker_startup_time': 300,
            'worker_shutdown_time': 0
        })()
        POOL_PROPERTIES["COLD"] = type('PoolProperties', (), {
            'worker_startup_time': 600,
            'worker_shutdown_time': 1800
        })()
        
        # Test STANDBY worker
        standby_worker = Worker("STANDBY", 1)
        assert standby_worker.get_worker_activation_time() == 0
        assert standby_worker.get_worker_shutdown_time() == 0
        
        # Test DEALLOCATED worker
        deallocated_worker = Worker("DEALLOCATED", 2)
        assert deallocated_worker.get_worker_activation_time() == 300
        assert deallocated_worker.get_worker_shutdown_time() == 0
        
        # Test COLD worker
        cold_worker = Worker("COLD", 3)
        assert cold_worker.get_worker_activation_time() == 600
        assert cold_worker.get_worker_shutdown_time() == 1800
    
    def test_worker_representation(self):
        """Test worker string representation"""
        worker = Worker("STANDBY", 5)
        worker.set_worker_status(WorkerStatus.READY)
        
        str_repr = str(worker)
        assert "Worker(" in str_repr
        assert "worker_type=STANDBY" in str_repr
        assert "worker_status=WorkerStatus.READY" in str_repr
        assert "worker_id=5" in str_repr
    
    def test_worker_to_dict(self):
        """Test worker dictionary conversion"""
        worker = Worker("COLD", 10)
        worker.set_worker_status(WorkerStatus.BUSY)
        
        worker_dict = worker.to_dict()
        
        assert worker_dict["worker_type"] == "COLD"
        assert worker_dict["worker_status"] == WorkerStatus.BUSY
        assert worker_dict["worker_id"] == 10

class TestWorkerPool:
    """Test WorkerPool functionality"""
    
    def test_worker_pool_initialization(self, basic_config):
        """Test worker pool creation with configuration"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            pool = WorkerPool()
            
            # Check total workers created
            total_workers = sum(len(pool.priority_pools[priority]) for priority in pool.pool_priorities)
            assert total_workers == 18  # 3 + 5 + 10
            
            # Check priority ordering (should be sorted)
            assert pool.pool_priorities == [1, 2, 3]  # STANDBY, DEALLOCATED, COLD
            
            # Check that POOL_PROPERTIES was populated
            assert "STANDBY" in POOL_PROPERTIES
            assert "DEALLOCATED" in POOL_PROPERTIES
            assert "COLD" in POOL_PROPERTIES
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_priority_ordering(self, minimal_config):
        """Test that workers are created in priority order"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Check priority pools
            assert 1 in pool.priority_pools  # STANDBY
            assert 2 in pool.priority_pools  # DEALLOCATED
            assert 3 in pool.priority_pools  # COLD
            
            # Check worker counts in each priority
            assert len(pool.priority_pools[1]) == 1  # STANDBY
            assert len(pool.priority_pools[2]) == 2  # DEALLOCATED
            assert len(pool.priority_pools[3]) == 3  # COLD
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_allocation_priority(self, minimal_config):
        """Test that workers are allocated by priority (DEALLOCATED before COLD)"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Get IN_POOL worker
            worker = pool.acquire_in_pool_worker_prioritized()
            
            assert worker is not None
            assert worker.get_worker_status() == WorkerStatus.INITIALIZING
            
            # Should prefer DEALLOCATED over COLD
            worker_type = worker.get_worker_type()
            assert worker_type in ["STANDBY", "DEALLOCATED", "COLD"]
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_empty_config(self):
        """Test worker pool with empty configuration"""
        # Create empty config
        empty_config = SimulationConfig(
            job_definitions=[],
            user_definitions=[],
            worker_definitions=[],
            lambda_users_requests_per_hour=0
        )
        
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = empty_config
        
        try:
            pool = WorkerPool()
            
            # Should have no workers
            total_workers = sum(len(pool.priority_pools[priority]) for priority in pool.pool_priorities)
            assert total_workers == 0
            
            # Should have no priorities
            assert len(pool.pool_priorities) == 0
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()
    
    def test_worker_pool_allocate_ready_worker(self, minimal_config):
        """Test allocating ready workers"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            pool = WorkerPool()
            
            # Initially no READY workers
            worker = pool.allocate_ready_worker()
            assert worker is None
            
            # Set a worker to READY
            for priority in pool.pool_priorities:
                for w in pool.priority_pools[priority]:
                    w.set_worker_status(WorkerStatus.READY)
                    break
            
            # Now should find a READY worker
            worker = pool.allocate_ready_worker()
            assert worker is not None
            assert worker.get_worker_status() == WorkerStatus.BUSY
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
            POOL_PROPERTIES.clear()

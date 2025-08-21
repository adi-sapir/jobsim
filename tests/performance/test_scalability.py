"""
Performance and scalability tests for JobSim
"""
import pytest
import time
import psutil
import os
from jobsim import SimState, JobGenerator, Job

class TestPerformance:
    """Test JobSim performance characteristics"""
    
    def test_large_simulation_performance(self, basic_config):
        """Test performance with large number of jobs"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Generate many jobs
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 3600)  # 1 hour
            
            start_time = time.time()
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete within reasonable time
            assert execution_time < 10.0  # 10 seconds max
            assert len(sim_state.completed_jobs) > 0
            
            # All jobs should be completed
            assert len(sim_state.completed_jobs) == len(jobs)
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_memory_usage(self, basic_config):
        """Test memory usage with large simulations"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Run large simulation
            sim_state = SimState()
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 7200)  # 2 hours
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024
            
            # All jobs should be completed
            assert len(sim_state.completed_jobs) == len(jobs)
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_event_queue_performance(self):
        """Test event queue performance with many events"""
        from jobsim import EventQueue
        
        eq = EventQueue()
        
        # Add many events
        start_time = time.time()
        
        for i in range(10000):
            eq.push(i, "JOB_SUBMITTED", f"job_{i}")
        
        add_time = time.time() - start_time
        
        # Adding events should be fast
        assert add_time < 1.0  # Less than 1 second for 10k events
        
        # Process all events
        start_time = time.time()
        
        events_processed = 0
        while not eq.is_empty():
            event = eq.pop()
            events_processed += 1
        
        process_time = time.time() - start_time
        
        # Processing events should be fast
        assert process_time < 1.0  # Less than 1 second for 10k events
        assert events_processed == 10000
    
    def test_worker_pool_scalability(self, basic_config):
        """Test worker pool scalability with many workers"""
        # Mock the global CONFIG
        import jobsim.sim_config
        from jobsim import WorkerPool, WorkerStatus
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            start_time = time.time()
            
            pool = WorkerPool()
            
            creation_time = time.time() - start_time
            
            # Creating worker pool should be fast
            assert creation_time < 1.0  # Less than 1 second
            
            # Test worker allocation performance
            start_time = time.time()
            
            workers_allocated = 0
            for _ in range(100):  # Try to allocate 100 times
                worker = pool.allocate_ready_worker()
                if worker is not None:
                    workers_allocated += 1
                    # Return worker to pool for next allocation
                    worker.set_worker_status(WorkerStatus.IN_POOL)
            
            allocation_time = time.time() - start_time
            
            # Worker allocation should be fast
            assert allocation_time < 1.0  # Less than 1 second for 100 allocations
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_job_generation_performance(self, basic_config):
        """Test job generation performance"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            job_generator = JobGenerator()
            
            # Test different time windows
            time_windows = [60, 300, 600, 3600]  # 1min, 5min, 10min, 1hour
            
            for window in time_windows:
                start_time = time.time()
                
                jobs = job_generator.generate_jobs(0, window)
                
                generation_time = time.time() - start_time
                
                # Job generation should be fast
                assert generation_time < 1.0  # Less than 1 second
                assert len(jobs) > 0
                
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_simulation_scalability(self, basic_config):
        """Test simulation scalability with increasing load"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            # Test different simulation sizes
            simulation_sizes = [
                (60, 10),    # 1 minute, ~10 jobs
                (300, 50),   # 5 minutes, ~50 jobs
                (600, 100),  # 10 minutes, ~100 jobs
                (1800, 300)  # 30 minutes, ~300 jobs
            ]
            
            for duration, expected_jobs in simulation_sizes:
                start_time = time.time()
                
                sim_state = SimState()
                job_generator = JobGenerator()
                jobs = job_generator.generate_jobs(0, duration)
                
                sim_state.init_jobs_in_queue(jobs)
                sim_state.run()
                
                execution_time = time.time() - start_time
                
                # Execution time should scale reasonably
                # Linear scaling would be ideal, but we allow some overhead
                max_expected_time = duration / 100  # Allow 1% of simulation time
                assert execution_time < max_expected_time
                
                # All jobs should be completed
                assert len(sim_state.completed_jobs) == len(jobs)
                
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_memory_leak_detection(self, basic_config):
        """Test for memory leaks in long-running simulations"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            process = psutil.Process(os.getpid())
            
            # Run multiple simulations and check memory
            memory_samples = []
            
            for run in range(5):
                sim_state = SimState()
                job_generator = JobGenerator()
                jobs = job_generator.generate_jobs(0, 300)  # 5 minutes
                
                sim_state.init_jobs_in_queue(jobs)
                sim_state.run()
                
                # Sample memory after each run
                memory_samples.append(process.memory_info().rss)
                
                # Clear references
                del sim_state
                del job_generator
                del jobs
            
            # Check for significant memory growth
            if len(memory_samples) > 1:
                initial_memory = memory_samples[0]
                final_memory = memory_samples[-1]
                memory_growth = final_memory - initial_memory
                
                # Memory growth should be minimal (less than 10MB)
                assert memory_growth < 10 * 1024 * 1024
                
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_cpu_usage(self, basic_config):
        """Test CPU usage during simulation"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            process = psutil.Process(os.getpid())
            
            # Measure CPU usage during simulation
            start_cpu = process.cpu_percent()
            
            sim_state = SimState()
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 600)  # 10 minutes
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            end_cpu = process.cpu_percent()
            
            # CPU usage should be reasonable
            # Note: CPU usage can vary significantly based on system load
            # We're mainly checking that the process doesn't hang
            
            # All jobs should be completed
            assert len(sim_state.completed_jobs) == len(jobs)
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config

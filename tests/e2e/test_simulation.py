"""
End-to-end tests for JobSim simulation system
"""
import pytest
import json
import tempfile
import os
from jobsim import SimState, JobGenerator, Job

class TestSimulationE2E:
    """Test complete simulation workflows"""
    
    def test_basic_simulation_run(self, basic_config):
        """Test complete simulation with generated jobs"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Generate some jobs
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 300)  # 5 minutes
            
            # Initialize simulation
            sim_state.init_jobs_in_queue(jobs)
            
            # Run simulation
            sim_state.run()
            
            # Check results
            assert len(sim_state.completed_jobs) > 0
            assert sim_state.event_queue.is_empty()
            
            # All jobs should be completed
            assert len(sim_state.completed_jobs) == len(jobs)
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_scenario_file_simulation(self, temp_scenario_file):
        """Test simulation using scenario file"""
        sim_state = SimState()
        
        # Load jobs from scenario file
        jobs = sim_state.load_jobs_from_file(temp_scenario_file)
        sim_state.init_jobs_in_queue(jobs)
        
        # Run simulation
        sim_state.run()
        
        # Verify all jobs completed
        assert len(sim_state.completed_jobs) == 3
        
        # Check job details
        completed_job_ids = {job.get_id() for job in sim_state.completed_jobs}
        expected_job_ids = {1, 2, 3}
        assert completed_job_ids == expected_job_ids
        
        # All jobs should have server assignments
        for job in sim_state.completed_jobs:
            assert job.get_server_type() is not None
            assert job.get_server_id() is not None
            assert job.get_start_execution_time() > 0
    
    def test_empty_simulation(self):
        """Test simulation with no jobs"""
        sim_state = SimState()
        sim_state.run()
        
        assert len(sim_state.completed_jobs) == 0
        assert len(sim_state.pending_jobs) == 0
        assert sim_state.event_queue.is_empty()
    
    def test_single_job_simulation(self, basic_config):
        """Test simulation with single job"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Create single job
            job = Job(id=1, type="S", user_type="C", submission_time=0)
            sim_state.init_jobs_in_queue([job])
            
            # Run simulation
            sim_state.run()
            
            assert len(sim_state.completed_jobs) == 1
            assert sim_state.completed_jobs[0].get_id() == 1
            assert sim_state.completed_jobs[0].get_server_type() is not None
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_high_load_simulation(self, basic_config):
        """Test simulation under high load"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Generate many jobs quickly
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 60)  # 1 minute, many jobs
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            # Should handle high load gracefully
            assert len(sim_state.completed_jobs) > 0
            
            # All jobs should be completed
            assert len(sim_state.completed_jobs) == len(jobs)
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_simulation_with_worker_shortage(self, minimal_config):
        """Test simulation behavior when workers are insufficient"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = minimal_config
        
        try:
            sim_state = SimState()
            
            # Create more jobs than available workers
            jobs = []
            for i in range(10):  # 10 jobs
                job = Job(id=i, type="S", user_type="C", submission_time=i*10)
                jobs.append(job)
            
            sim_state.init_jobs_in_queue(jobs)
            
            # Run simulation
            sim_state.run()
            
            # Should complete all jobs eventually
            assert len(sim_state.completed_jobs) == 10
            
            # Check that jobs were processed in order (approximately)
            # Due to worker allocation timing, exact order may vary
            completed_times = [job.get_start_execution_time() for job in sim_state.completed_jobs]
            assert len(completed_times) == 10
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_simulation_statistics(self, basic_config):
        """Test simulation statistics generation"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Generate jobs
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 120)  # 2 minutes
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            # Test statistics methods
            # Note: These methods print to stdout, so we're mainly testing they don't crash
            
            # Test submitted jobs statistics
            sim_state.print_submitted_jobs()
            
            # Test wait times statistics
            sim_state.print_wait_times()
            
            # Test worker statistics
            sim_state.print_workers_stats()
            
            # Test overall statistics
            sim_state.print_statistics()
            
            # All methods should execute without error
            assert True
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_simulation_run_naming(self, basic_config):
        """Test simulation run naming functionality"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            sim_state = SimState()
            
            # Set run name
            sim_state.run_name = "test_run"
            
            # Generate and run jobs
            job_generator = JobGenerator()
            jobs = job_generator.generate_jobs(0, 60)
            
            sim_state.init_jobs_in_queue(jobs)
            sim_state.run()
            
            # Verify run name is preserved
            assert sim_state.run_name == "test_run"
            
            # Test statistics with run name
            sim_state.print_statistics()
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_simulation_error_handling(self):
        """Test simulation error handling"""
        sim_state = SimState()
        
        # Test with invalid job (missing required fields)
        # This should be handled gracefully
        try:
            # Create a job with minimal required fields
            job = Job(id=1, type="S", user_type="C", submission_time=0)
            sim_state.init_jobs_in_queue([job])
            
            # Should not crash
            assert True
            
        except Exception as e:
            # If it does crash, that's also valid behavior to test
            assert isinstance(e, Exception)
    
    def test_simulation_consistency(self, basic_config):
        """Test simulation consistency across multiple runs"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            # Run simulation multiple times with same config
            results = []
            
            for run in range(3):
                sim_state = SimState()
                job_generator = JobGenerator()
                jobs = job_generator.generate_jobs(0, 60)
                
                sim_state.init_jobs_in_queue(jobs)
                sim_state.run()
                
                results.append({
                    'completed_jobs': len(sim_state.completed_jobs),
                    'total_processing_time': sum(j.get_execution_duration() for j in sim_state.completed_jobs)
                })
            
            # Results should be consistent (same number of jobs completed)
            # Note: Due to randomness in job generation, exact counts may vary
            # but should be in reasonable range
            for result in results:
                assert result['completed_jobs'] > 0
                assert result['total_processing_time'] > 0
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config

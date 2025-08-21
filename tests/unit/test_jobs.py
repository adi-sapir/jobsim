"""
Unit tests for Job component
"""
import pytest
from jobsim import Job
from jobsim.sim_config import SimulationConfig

class TestJob:
    """Test Job functionality"""
    
    def test_job_creation(self):
        """Test job object creation and methods"""
        job = Job(id=1, type="L", user_type="C", submission_time=100)
        
        assert job.get_id() == 1
        assert job.get_type() == "L"
        assert job.get_user_type() == "C"
        assert job.get_submission_time() == 100
        assert job.get_start_execution_time() == 0
        assert job.get_server_type() is None
        assert job.get_server_id() is None
    
    def test_job_server_assignment(self):
        """Test job server assignment"""
        job = Job(id=2, type="M", user_type="F", submission_time=50)
        
        # Set server information
        job.set_server_type("STANDBY")
        job.set_server_id(5)
        job.set_start_execution_time(75)
        
        # Verify assignments
        assert job.get_server_type() == "STANDBY"
        assert job.get_server_id() == 5
        assert job.get_start_execution_time() == 75
    
    def test_job_execution_duration(self, basic_config):
        """Test job execution duration retrieval"""
        # Mock the global CONFIG
        import jobsim.sim_config
        original_config = jobsim.sim_config.CONFIG
        jobsim.sim_config.CONFIG = basic_config
        
        try:
            # Test different job types
            small_job = Job(id=1, type="S", user_type="C", submission_time=0)
            medium_job = Job(id=2, type="M", user_type="C", submission_time=0)
            large_job = Job(id=3, type="L", user_type="C", submission_time=0)
            
            assert small_job.get_execution_duration() == 30
            assert medium_job.get_execution_duration() == 60
            assert large_job.get_execution_duration() == 120
            
        finally:
            # Restore original config
            jobsim.sim_config.CONFIG = original_config
    
    def test_job_representation(self):
        """Test job string representation"""
        job = Job(id=10, type="S", user_type="F", submission_time=200)
        job.set_server_type("DEALLOCATED")
        job.set_server_id(15)
        job.set_start_execution_time(250)
        
        str_repr = str(job)
        
        # Check that all fields are represented
        assert "Job(" in str_repr
        assert "id=10" in str_repr
        assert "type=S" in str_repr
        assert "user_type=F" in str_repr
        assert "submission_time=200" in str_repr
        assert "start_execution_time=250" in str_repr
        assert "server_type=DEALLOCATED" in str_repr
        assert "server_id=15" in str_repr
    
    def test_job_to_dict(self):
        """Test job dictionary conversion"""
        job = Job(id=5, type="L", user_type="S", submission_time=150)
        job.set_server_type("COLD")
        job.set_server_id(8)
        job.set_start_execution_time(200)
        
        job_dict = job.to_dict()
        
        expected_dict = {
            'id': 5,
            'type': 'L',
            'user_type': 'S',
            'submission_time': 150,
            'start_execution_time': 200,
            'server_type': 'COLD',
            'server_id': 8
        }
        
        assert job_dict == expected_dict
    
    def test_job_to_json(self):
        """Test job JSON conversion"""
        job = Job(id=3, type="M", user_type="C", submission_time=75)
        
        json_str = job.to_json()
        
        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        
        assert parsed['id'] == 3
        assert parsed['type'] == 'M'
        assert parsed['user_type'] == 'C'
        assert parsed['submission_time'] == 75
    
    def test_job_default_values(self):
        """Test job default values"""
        job = Job(id=1, type="S", user_type="C", submission_time=0)
        
        # Default values
        assert job.get_start_execution_time() == 0
        assert job.get_server_type() is None
        assert job.get_server_id() is None
    
    def test_job_id_uniqueness(self):
        """Test that job IDs can be unique"""
        job1 = Job(id=1, type="S", user_type="C", submission_time=0)
        job2 = Job(id=2, type="S", user_type="C", submission_time=0)
        job3 = Job(id=999, type="L", user_type="F", submission_time=100)
        
        assert job1.get_id() != job2.get_id()
        assert job1.get_id() != job3.get_id()
        assert job2.get_id() != job3.get_id()
    
    def test_job_type_validation(self):
        """Test job type handling"""
        # Test different job types
        job_types = ["S", "M", "L", "X", "Z"]
        
        for job_type in job_types:
            job = Job(id=1, type=job_type, user_type="C", submission_time=0)
            assert job.get_type() == job_type
    
    def test_job_user_type_validation(self):
        """Test user type handling"""
        # Test different user types
        user_types = ["F", "C", "S", "X", "Z"]
        
        for user_type in user_types:
            job = Job(id=1, type="S", user_type=user_type, submission_time=0)
            assert job.get_user_type() == user_type
    
    def test_job_timestamp_handling(self):
        """Test timestamp handling"""
        # Test various timestamp values
        timestamps = [0, 1, 100, 1000, 999999]
        
        for timestamp in timestamps:
            job = Job(id=1, type="S", user_type="C", submission_time=timestamp)
            assert job.get_submission_time() == timestamp
    
    def test_job_server_reassignment(self):
        """Test that server information can be reassigned"""
        job = Job(id=1, type="M", user_type="C", submission_time=0)
        
        # Initial assignment
        job.set_server_type("STANDBY")
        job.set_server_id(1)
        job.set_start_execution_time(10)
        
        assert job.get_server_type() == "STANDBY"
        assert job.get_server_id() == 1
        assert job.get_start_execution_time() == 10
        
        # Reassignment
        job.set_server_type("DEALLOCATED")
        job.set_server_id(5)
        job.set_start_execution_time(25)
        
        assert job.get_server_type() == "DEALLOCATED"
        assert job.get_server_id() == 5
        assert job.get_start_execution_time() == 25
    
    def test_job_edge_cases(self):
        """Test job edge cases"""
        # Test with zero values
        job = Job(id=0, type="S", user_type="C", submission_time=0)
        assert job.get_id() == 0
        assert job.get_submission_time() == 0
        
        # Test with large values
        job = Job(id=999999, type="L", user_type="F", submission_time=999999)
        assert job.get_id() == 999999
        assert job.get_submission_time() == 999999
        
        # Test with special characters in type/user_type
        job = Job(id=1, type="S", user_type="C", submission_time=0)
        # Should handle special characters gracefully

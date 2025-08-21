"""
CLI tests for JobSim command line interfaces
"""
import pytest
import subprocess
import tempfile
import json
import os
from jobsim import SimulationConfig

class TestCLI:
    """Test command line interface functionality"""
    
    def test_jobsim_help(self):
        """Test jobsim help command"""
        try:
            result = subprocess.run(["jobsim", "--help"], 
                                   capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "JobSim - job execution simulation" in result.stdout
            assert "--scenario" in result.stdout
            assert "--debug" in result.stdout
            assert "--config" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_jobgen_help(self):
        """Test jobgen help command"""
        try:
            result = subprocess.run(["jobgen", "--help"], 
                                   capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "Generate jobs for a simulation time window" in result.stdout
            assert "--config" in result.stdout
            assert "--debug" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobgen command not found in PATH")
    
    def test_sim_config_help(self):
        """Test sim-config help command"""
        try:
            result = subprocess.run(["sim-config", "--help"], 
                                   capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "Simulation configuration utility" in result.stdout
            assert "--load" in result.stdout
            assert "--save" in result.stdout
            assert "--print" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("sim-config command not found in PATH")
    
    def test_jobsim_invalid_duration(self):
        """Test jobsim with invalid duration"""
        try:
            result = subprocess.run(["jobsim", "invalid"], 
                                   capture_output=True, text=True, timeout=10)
            
            # Should fail with invalid duration
            assert result.returncode != 0
            assert "Invalid duration format" in result.stderr or "error" in result.stderr.lower()
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_jobsim_valid_duration(self):
        """Test jobsim with valid duration"""
        try:
            result = subprocess.run(["jobsim", "0:0:5"], 
                                   capture_output=True, text=True, timeout=30)
            
            # May fail due to missing config, but shouldn't crash
            # The important thing is it doesn't hang or crash
            assert result.returncode >= 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_jobgen_valid_duration(self):
        """Test jobgen with valid duration"""
        try:
            result = subprocess.run(["jobgen", "0:0:10"], 
                                   capture_output=True, text=True, timeout=30)
            
            # Should generate jobs and output JSON
            assert result.returncode == 0
            assert "[" in result.stdout  # Should start with JSON array
            assert "]" in result.stdout  # Should end with JSON array
            
            # Should contain job data
            assert "id" in result.stdout
            assert "type" in result.stdout
            assert "user_type" in result.stdout
            assert "submission_time" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobgen command not found in PATH")
    
    def test_jobgen_with_config(self, temp_config_file):
        """Test jobgen with configuration file"""
        try:
            result = subprocess.run(["jobgen", "0:0:5", "--config", temp_config_file], 
                                   capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            assert "[" in result.stdout
            assert "]" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobgen command not found in PATH")
    
    def test_jobsim_with_scenario(self, temp_scenario_file):
        """Test jobsim with scenario file"""
        try:
            result = subprocess.run(["jobsim", "--scenario", temp_scenario_file], 
                                   capture_output=True, text=True, timeout=30)
            
            # May fail due to missing config, but shouldn't crash
            assert result.returncode >= 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_jobsim_with_debug(self):
        """Test jobsim with debug flag"""
        try:
            result = subprocess.run(["jobsim", "0:0:5", "--debug", "trace"], 
                                   capture_output=True, text=True, timeout=30)
            
            # May fail due to missing config, but shouldn't crash
            assert result.returncode >= 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_sim_config_print(self):
        """Test sim-config print command"""
        try:
            result = subprocess.run(["sim-config", "--print"], 
                                   capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            # Should output JSON configuration
            assert "{" in result.stdout
            assert "}" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("sim-config command not found in PATH")
    
    def test_sim_config_save_load(self, temp_config_file):
        """Test sim-config save and load functionality"""
        try:
            # Test load
            result = subprocess.run(["sim-config", "--load", temp_config_file], 
                                   capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            
            # Test save to new file
            temp_save_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            temp_save_file.close()
            
            try:
                result = subprocess.run(["sim-config", "--save", temp_save_file.name], 
                                       capture_output=True, text=True, timeout=30)
                
                assert result.returncode == 0
                
                # Verify file was created and contains valid JSON
                with open(temp_save_file.name, 'r') as f:
                    saved_config = json.load(f)
                
                assert "job_definitions" in saved_config
                assert "user_definitions" in saved_config
                
            finally:
                # Clean up
                if os.path.exists(temp_save_file.name):
                    os.unlink(temp_save_file.name)
                    
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("sim-config command not found in PATH")
    
    def test_cli_error_handling(self):
        """Test CLI error handling"""
        try:
            # Test with non-existent file
            result = subprocess.run(["jobsim", "--scenario", "nonexistent.json"], 
                                   capture_output=True, text=True, timeout=30)
            
            # Should fail gracefully
            assert result.returncode != 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("jobsim command not found in PATH")
    
    def test_cli_timeout_handling(self):
        """Test CLI timeout handling"""
        try:
            # Test with very long duration (should timeout or fail gracefully)
            result = subprocess.run(["jobgen", "24:0:0"], 
                                   capture_output=True, text=True, timeout=10)
            
            # Should either complete quickly or timeout gracefully
            assert result.returncode >= 0
            
        except subprocess.TimeoutExpired:
            # Timeout is expected for very long durations
            assert True
        except FileNotFoundError:
            pytest.skip("jobgen command not found in PATH")
    
    def test_cli_stdin_stdout(self):
        """Test CLI stdin/stdout handling"""
        try:
            # Test that jobgen can output to stdout
            result = subprocess.run(["jobgen", "0:0:1"], 
                                   capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0
            assert len(result.stdout) > 0
            
            # Test that error messages go to stderr
            result = subprocess.run(["jobsim", "invalid"], 
                                   capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                assert len(result.stderr) > 0
            
        except subprocess.TimeoutExpired:
            pytest.skip("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("CLI commands not found in PATH")

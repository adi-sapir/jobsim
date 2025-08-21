"""
Unit tests for EventQueue component
"""
import pytest
from jobsim import EventQueue, Event

class TestEventQueue:
    """Test EventQueue functionality"""
    
    def test_event_queue_creation(self):
        """Test EventQueue initialization"""
        eq = EventQueue()
        assert eq.is_empty()
        assert eq.size() == 0
    
    def test_event_queue_ordering(self):
        """Test that events are properly ordered by timestamp"""
        eq = EventQueue()
        eq.push(100, "JOB_SUBMITTED", "late_event")
        eq.push(50, "JOB_SUBMITTED", "early_event")
        eq.push(75, "JOB_SUBMITTED", "middle_event")
        
        assert eq.size() == 3
        
        # Should pop in timestamp order
        event1 = eq.pop()
        assert event1.timestamp == 50
        assert event1.data == "early_event"
        
        event2 = eq.pop()
        assert event2.timestamp == 75
        assert event2.data == "middle_event"
        
        event3 = eq.pop()
        assert event3.timestamp == 100
        assert event3.data == "late_event"
        
        assert eq.is_empty()
    
    def test_event_queue_empty(self):
        """Test empty queue behavior"""
        eq = EventQueue()
        assert eq.is_empty()
        assert eq.size() == 0
        
        # Should return None when empty, not raise exception
        assert eq.pop() is None
    
    def test_event_queue_duplicate_timestamps(self):
        """Test handling of events with same timestamp"""
        eq = EventQueue()
        eq.push(100, "JOB_SUBMITTED", "event1")
        eq.push(100, "JOB_SUBMITTED", "event2")
        eq.push(100, "JOB_SUBMITTED", "event3")
        
        # Should handle same timestamps gracefully
        assert eq.size() == 3
        
        # All events with timestamp 100 should be processed
        events = []
        while not eq.is_empty():
            events.append(eq.pop())
        
        assert len(events) == 3
        assert all(event.timestamp == 100 for event in events)
    
    def test_event_queue_mixed_event_types(self):
        """Test queue with different event types"""
        eq = EventQueue()
        eq.push(50, "JOB_SUBMITTED", "job1")
        eq.push(25, "WORKER_READY", "worker1")
        eq.push(75, "WORKER_DONE", "worker2")
        eq.push(10, "JOB_SUBMITTED", "job2")
        
        assert eq.size() == 4
        
        # Should process in timestamp order regardless of event type
        event1 = eq.pop()
        assert event1.timestamp == 10
        assert event1.event_type == "JOB_SUBMITTED"
        
        event2 = eq.pop()
        assert event2.timestamp == 25
        assert event2.event_type == "WORKER_READY"
        
        event3 = eq.pop()
        assert event3.timestamp == 50
        assert event3.event_type == "JOB_SUBMITTED"
        
        event4 = eq.pop()
        assert event4.timestamp == 75
        assert event4.event_type == "WORKER_DONE"
    
    def test_event_queue_peek_behavior(self):
        """Test that pop doesn't change queue state until called"""
        eq = EventQueue()
        eq.push(100, "JOB_SUBMITTED", "test_event")
        
        # Queue should still have the event
        assert eq.size() == 1
        assert not eq.is_empty()
        
        # Pop should remove the event
        event = eq.pop()
        assert eq.is_empty()
        assert eq.size() == 0
    
    def test_event_queue_large_number_of_events(self):
        """Test queue performance with many events"""
        eq = EventQueue()
        
        # Add many events in reverse order
        for i in range(1000, 0, -1):
            eq.push(i, "JOB_SUBMITTED", f"job_{i}")
        
        assert eq.size() == 1000
        
        # Should process in correct order
        for i in range(1, 1001):
            event = eq.pop()
            assert event.timestamp == i
            assert event.data == f"job_{i}"
        
        assert eq.is_empty()
    
    def test_event_queue_edge_timestamps(self):
        """Test queue with edge case timestamps"""
        eq = EventQueue()
        
        # Test with zero timestamp
        eq.push(0, "JOB_SUBMITTED", "zero_time")
        
        # Test with very large timestamp
        eq.push(999999999, "WORKER_READY", "large_time")
        
        # Test with negative timestamp (should work)
        eq.push(-100, "JOB_SUBMITTED", "negative_time")
        
        assert eq.size() == 3
        
        # Should process negative first, then zero, then large
        event1 = eq.pop()
        assert event1.timestamp == -100
        
        event2 = eq.pop()
        assert event2.timestamp == 0
        
        event3 = eq.pop()
        assert event3.timestamp == 999999999

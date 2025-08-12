import heapq
from typing import Any, Optional, List
from dataclasses import dataclass
from time import time


@dataclass
class Event:
    """Represents an event in the simulation with an integer timestamp and payload."""
    timestamp: int
    event_type: str
    data: Any = None

    def __lt__(self, other: "Event") -> bool:
        """Order events by timestamp only for heap operations."""
        return self.timestamp < other.timestamp


class EventQueue:
    """
    An efficient event queue that maintains events ordered by integer timestamp.
    Uses a min-heap for O(log n) insertion and O(1) access to earliest event.
    """

    def __init__(self) -> None:
        """Initialize an empty event queue."""
        self._events: List[Event] = []
        self._event_count: int = 0

    def push(self, timestamp: int, event_type: str, data: Any) -> None:
        """
        Add an event to the queue.

        Args:
            timestamp: When the event should occur (integer)
            data: Event data/payload
        """
        event = Event(timestamp=timestamp, event_type=event_type, data=data)
        heapq.heappush(self._events, event)
        self._event_count += 1

    def push_event(self, event: Event) -> None:
        """Add a pre-created Event object to the queue."""
        heapq.heappush(self._events, event)
        self._event_count += 1

    def pop(self) -> Optional[Event]:
        """
        Remove and return the earliest event from the queue.

        Returns:
            The earliest event, or None if queue is empty
        """
        if self.is_empty():
            return None

        event = heapq.heappop(self._events)
        self._event_count -= 1
        return event

    def peek(self) -> Optional[Event]:
        """View the earliest event without removing it."""
        if self.is_empty():
            return None
        return self._events[0]

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._events) == 0

    def size(self) -> int:
        """Get the current number of events in the queue."""
        return self._event_count

    def clear(self) -> None:
        """Remove all events from the queue."""
        self._events.clear()
        self._event_count = 0

    def get_events_in_timerange(self, start_time: int, end_time: int) -> List[Event]:
        """
        Get all events within a time range (note: this is O(n) operation).

        Args:
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive)

        Returns:
            List of events within the specified time range
        """
        return [event for event in self._events if start_time <= event.timestamp <= end_time]

    def remove_event(self, event: Event) -> bool:
        """
        Remove a specific event from the queue (O(n)).

        Returns:
            True if event was found and removed, False otherwise
        """
        try:
            self._events.remove(event)
            heapq.heapify(self._events)  # Rebuild heap after removal
            self._event_count -= 1
            return True
        except ValueError:
            return False

    def __len__(self) -> int:
        """Return the number of events in the queue."""
        return self._event_count

    def __str__(self) -> str:
        """String representation of the event queue."""
        if self.is_empty():
            return "EventQueue(empty)"

        preview = ", ".join([f"\n({e.timestamp}, {e.event_type}, {e.data})" for e in sorted(self._events[:5])])
        if len(self._events) > 5:
            preview += f" ... and {len(self._events) - 5} more"

        return f"EventQueue({len(self._events)} events: {preview})"


# Example usage and quick test
if __name__ == "__main__":
    # Create an event queue
    eq = EventQueue()

    # Add some events with integer timestamps
    eq.push(105, "job_start")
    eq.push(52, "resource_check")
    eq.push(81, "job_complete")
    eq.push(30, "system_init")

    print(f"Queue size: {eq.size()}")
    print(f"Queue: {eq}")

    # Process events in order
    print("\nProcessing events in chronological order:")
    while not eq.is_empty():
        event = eq.pop()
        print(f"  {event.timestamp}: {event.data}")

    print(f"\nQueue is now empty: {eq.is_empty()}")

    # Test with current time (as integer seconds)
    current_time = int(time())
    eq.push(current_time + 10, "future_event")
    eq.push(current_time + 5, "sooner_event")

    print(f"\nAdded future events: {eq}")
    next_event = eq.peek()
    if next_event:
        print(f"Next event will be: {next_event.timestamp}: {next_event.data}")

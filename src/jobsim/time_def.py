#Time constants
import argparse

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

def seconds_to_hms(seconds: int) -> str:
  hours = seconds // HOUR
  minutes = (seconds % HOUR) // MINUTE
  seconds = seconds % MINUTE
  if hours > 0:
    return f"{hours} hours :{minutes} minutes :{seconds} seconds"
  elif minutes > 0:
    return f"{minutes} minutes :{seconds} seconds"
  else:
    return f"{seconds} seconds"

def parse_duration_hms(value: str) -> int:
  """Parse duration string in H:M:S format and return total seconds."""
  try:
    parts = value.split(':')
    if len(parts) == 3:
      hours, minutes, seconds = map(int, parts)
      return hours * HOUR + minutes * MINUTE + seconds
    elif len(parts) == 2:
      minutes, seconds = map(int, parts)
      return minutes * MINUTE + seconds
    elif len(parts) == 1:
      return int(parts[0])
    else:
      raise ValueError("Invalid format")
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid duration format: {value}. Use H:M:S, M:S, or S format.")
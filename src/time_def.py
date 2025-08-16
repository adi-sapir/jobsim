#Time constants
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
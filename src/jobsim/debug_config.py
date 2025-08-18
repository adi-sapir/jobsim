# Debug config
DEBUG_LEVEL = "none"  # "none", "trace", "full"

def debug_print(*args, level="trace", **kwargs):
    """Print debug message if current debug level allows it."""
    if should_print_debug(level):
        prefix = f"[{level.upper()}]"
        print(prefix, *args, **kwargs)

def trace_print(*args, **kwargs):
    """Print trace-level debug message."""
    debug_print(*args, level="trace", **kwargs)

def full_debug_print(*args, **kwargs):
    """Print full debug message."""
    debug_print(*args, level="full", **kwargs)

def should_print_debug(level: str) -> bool:
    """Check if debug message should be printed based on current level."""
    if DEBUG_LEVEL == "none":
        return False
    elif DEBUG_LEVEL == "trace":
        return level in ["trace"]
    elif DEBUG_LEVEL == "full":
        return level in ["trace", "full"]
    return False

def set_debug(level: str):
    """Set debug level: 'none', 'trace', or 'full'."""
    global DEBUG_LEVEL
    valid_levels = ["none", "trace", "full"]
    if level not in valid_levels:
        raise ValueError(f"Debug level must be one of: {valid_levels}")
    DEBUG_LEVEL = level

def get_debug():
    """Get current debug level."""
    return DEBUG_LEVEL

def is_debug_enabled():
    """Check if any debug output is enabled."""
    return DEBUG_LEVEL != "none"

def is_trace_enabled():
    """Check if trace debug is enabled."""
    return DEBUG_LEVEL in ["trace", "full"]

def is_full_debug_enabled():
    """Check if full debug is enabled."""
    return DEBUG_LEVEL == "full"

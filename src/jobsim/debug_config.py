# Debug config
DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

def set_debug(debug: bool):
    global DEBUG
    DEBUG = debug

def get_debug():
    return DEBUG

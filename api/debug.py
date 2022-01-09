import time
from functools import wraps

IS_DEBUG = True

def print_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration_time = end_time - start_time
        print("[DEBUG]function %s runtime: %s seconds" % (func.__name__, duration_time))
        return result
    return wrapper

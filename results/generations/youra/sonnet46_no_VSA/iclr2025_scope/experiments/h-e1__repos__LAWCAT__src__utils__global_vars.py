_GLOBAL_ARGS = None
_GLOBAL_COUNT = 0


def set_global_args(args):
    global _GLOBAL_ARGS
    _GLOBAL_ARGS = args

def get_global_args():
    """Return arguments."""
    return _GLOBAL_ARGS

def set_global_count(count):
    global _GLOBAL_COUNT
    _GLOBAL_COUNT = count

def get_global_count():
    """Return count."""
    return _GLOBAL_COUNT
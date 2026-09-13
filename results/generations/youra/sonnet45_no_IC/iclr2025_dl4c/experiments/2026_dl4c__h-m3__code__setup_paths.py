"""
Centralized path setup for h-m2 experiment.
Import this at the top of all h-m2 modules to ensure correct sys.path.
"""
import sys
from pathlib import Path

def setup_paths():
    """Set up sys.path to include both h-m2 and h-m1 code."""
    # Get h-m2 code directory
    h_m2_code = Path(__file__).parent.resolve()

    # Get h-m1 code directory
    h_m1_code = (h_m2_code / '../../h-m1/code').resolve()

    # Add h-m1 first, THEN h-m2 (so h-m2 ends up with higher priority at index 0)
    # insert(0, ...) adds to the front, so we add in reverse order
    paths_to_add = [str(h_m1_code), str(h_m2_code)]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

# Auto-setup on import
setup_paths()

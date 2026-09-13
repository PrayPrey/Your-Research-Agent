# conftest.py - pytest configuration
import os

collect_ignore_glob = ["statistics.py", "run_experiment.py"]

# Absolute paths to ignore
collect_ignore = [
    os.path.join(os.path.dirname(__file__), "statistics.py"),
    os.path.join(os.path.dirname(__file__), "run_experiment.py"),
]

# conftest.py - pytest configuration
import os

collect_ignore_glob = ["statistics.py", "run_experiment.py", "run_experiment_m4.py"]

# Absolute paths to ignore
_code_dir = os.path.dirname(__file__)
collect_ignore = [
    os.path.join(_code_dir, "statistics.py"),
    os.path.join(_code_dir, "run_experiment.py"),
    os.path.join(_code_dir, "run_experiment_m4.py"),
]

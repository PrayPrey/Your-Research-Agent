"""Main entry point for h-e1 experiment (avoids relative import issues)."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__) + '/src')

from h_e1.run_experiment import parse_args, run_pipeline, print_summary

if __name__ == "__main__":
    args = parse_args()
    result = run_pipeline(args)
    print_summary(result)
    sys.exit(0 if result["gate_pass"] else 1)

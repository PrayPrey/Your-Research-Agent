#!/usr/bin/env python3
"""Entry point for Phase 4 experiment execution."""
import sys
import os
import json
import traceback
from pathlib import Path

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_H_E1_DIR = os.path.dirname(_CODE_DIR)
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)


def main():
    print("EXPERIMENT COMPLETE marker will be written on exit (via trap in shell wrapper).")
    try:
        from main import main as run_main
        stats = run_main()
        print("\n[run_experiment.py] Experiment finished successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[run_experiment.py] EXPERIMENT FAILED: {e}", file=sys.stderr)
        traceback.print_exc()
        # Write error to experiment_results.json
        error_result = {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        try:
            out_path = Path(_H_E1_DIR) / "experiment_results.json"
            with open(out_path, "w") as f:
                json.dump(error_result, f, indent=2)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

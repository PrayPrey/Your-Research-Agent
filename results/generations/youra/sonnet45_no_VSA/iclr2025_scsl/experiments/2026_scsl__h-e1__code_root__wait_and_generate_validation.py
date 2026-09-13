#!/usr/bin/env python3
"""
Wait for experiments to complete, then generate 04_validation.md
"""
import os
import sys
import time
import json
import psutil
from pathlib import Path
from datetime import datetime

# Configuration
PID = 3146982
LOG_FILE = Path("experiment_full.log")
OUTPUT_DIR = Path("outputs/h-e1")
RESULTS_FILE = OUTPUT_DIR / "results.csv"
DOCS_DIR = Path("/workspace/TEST_scsl/docs/youra_research")

print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for experiments (PID {PID}) to complete...")
print(f"Results expected in: {RESULTS_FILE}")

# Wait for process to complete
wait_count = 0
while psutil.pid_exists(PID):
    time.sleep(60)  # Check every minute
    wait_count += 1
    
    if wait_count % 5 == 0:  # Report every 5 minutes
        # Parse progress from log
        try:
            with open(LOG_FILE) as f:
                content = f.read()
                import re
                experiments = re.findall(r'Experiment (\d+)/15', content)
                if experiments:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still running... Progress: Experiment {experiments[-1]}/15")
        except:
            pass

print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Process completed!")

# Wait a bit for file writes to finish
time.sleep(5)

# Check for results file
if not RESULTS_FILE.exists():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ ERROR: Results file not found at {RESULTS_FILE}")
    sys.exit(1)

print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Results file found, generating validation report...")

# Import evaluate module and generate report
sys.path.insert(0, str(Path.cwd()))
from evaluate import generate_validation_report

try:
    result = generate_validation_report(
        results_csv=str(RESULTS_FILE),
        output_dir=str(OUTPUT_DIR),
        hypothesis_id="h-e1"
    )
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Validation report generated!")
    print(f"  Gate result: {result['gate_result']}")
    print(f"  Report file: {result['validation_report']}")
    
    # Create completion marker
    with open("EXPERIMENTS_COMPLETE.marker", "w") as f:
        json.dump({
            "completed_at": datetime.now().isoformat(),
            "gate_result": result["gate_result"],
            "validation_report": result["validation_report"]
        }, f, indent=2)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Completion marker created")
    
except Exception as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ ERROR generating validation report: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


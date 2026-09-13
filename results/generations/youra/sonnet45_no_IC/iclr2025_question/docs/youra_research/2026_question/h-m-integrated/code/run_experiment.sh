#!/bin/bash
# Experiment launcher with completion marker (prevents unrecoverable hangs)

set -e

# Paths
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="${CODE_DIR}/experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run HBC experiment (h-m-integrated)
cd "$CODE_DIR"
python run_hbc_experiment.py 2>&1 | tee "$LOG"

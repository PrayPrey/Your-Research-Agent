#!/bin/bash
# Wrapper script to run Phase 2 experiment with correct Python path

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
H_M2_CODE="$SCRIPT_DIR"
H_M1_CODE="$(cd "$SCRIPT_DIR/../../h-m1/code" && pwd)"

# Set PYTHONPATH to include h-m2 first, then h-m1
export PYTHONPATH="$H_M2_CODE:$H_M1_CODE:$PYTHONPATH"

echo "PYTHONPATH set to:"
echo "  1. $H_M2_CODE"
echo "  2. $H_M1_CODE"
echo ""

# Run the Python script with all arguments passed through
python "$SCRIPT_DIR/run_phase2_experiment.py" "$@"

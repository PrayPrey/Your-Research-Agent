#!/bin/bash
set -e

# Experiment launcher for h-c1
LOG="experiment.log"

# MANDATORY: Install completion-marker finalizer
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run the experiment
cd /workspace/TEST_scsl/docs/youra_research/h-c1/code
python main.py > "$LOG" 2>&1

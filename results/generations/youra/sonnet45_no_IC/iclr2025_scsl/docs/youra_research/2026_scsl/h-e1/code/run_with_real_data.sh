#!/bin/bash
# Experiment launcher with real GitHub API data collection
# CRITICAL: Uses completion marker for reliable termination detection

set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting experiment with REAL GitHub API data (no mock/synthetic data)..."
echo "Dataset size: 100 repositories from curated ML/benchmark list"
echo "Data source: GitHub REST API v3 (unauthenticated)"
echo ""

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-e1

# Run experiment
python run_experiment.py 2>&1 | tee -a "$LOG"

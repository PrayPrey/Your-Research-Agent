#!/bin/bash
LOG=docs/youra_research/h-e3/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e3
cd /home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scsl
python docs/youra_research/h-e3/code/run_experiment.py > "$LOG" 2>&1

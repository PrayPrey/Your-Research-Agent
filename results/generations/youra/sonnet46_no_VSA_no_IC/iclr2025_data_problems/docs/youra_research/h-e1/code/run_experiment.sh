#!/bin/bash
# h-e1 experiment runner
# Uses pre-extracted doc_idx.npy (no .bin file needed since doc_idx is identity)

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_data_problems/docs/youra_research/h-e1/code

python run_poc.py \
    --doc-idx-npy data/doc_idx.npy \
    --domain-cache data/doc_to_domain_partial.pkl \
    --figures-dir ../../figures \
    --output-dir outputs \
    --results-json outputs/results.json \
    --poc \
    2>&1 | tee -a "$LOG"

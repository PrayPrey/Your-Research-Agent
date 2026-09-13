#!/bin/bash
# h-e1 full experiment: llama2 (donor+fresh) -> mistral -> llama3 -> analyze -> heatmap
cd "$(dirname "$0")"
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1
export CUDA_VISIBLE_DEVICES=1

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

{
  echo "=== h-e1 full experiment started $(date -Iseconds) ==="
  python run_h_e1.py --model llama2 --full &&
  python run_h_e1.py --model mistral --full &&
  python run_h_e1.py --model llama3 --full &&
  python run_h_e1.py --model all --analyze &&
  python -c "
import pandas as pd
import visualize
from constants import RESULTS_DIR
df = pd.read_csv(f'{RESULTS_DIR}/cache_llama2_triviaqa.csv')
p = visualize.plot_entropy_heatmap(df, 'llama2', 'triviaqa')
print('WROTE', p)
"
  echo "=== chain finished $(date -Iseconds) ==="
} > "$LOG" 2>&1

#!/bin/bash
# H-E1 Experiment Runner: Real contamination-correlation analysis
# Requires: PILE_NGRAMS_DIR set to Pile 13-gram index location

set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$(dirname "$0")"

# Check prerequisites
if [ -z "$PILE_NGRAMS_DIR" ]; then
    echo "ERROR: PILE_NGRAMS_DIR not set" | tee -a "$LOG"
    echo "Build Pile n-gram index using lm-eval-harness scripts/clean_training_data" | tee -a "$LOG"
    echo "Then: export PILE_NGRAMS_DIR=/path/to/ngrams" | tee -a "$LOG"
    exit 1
fi

if [ ! -f "$PILE_NGRAMS_DIR/info.json" ]; then
    echo "ERROR: $PILE_NGRAMS_DIR/info.json not found" | tee -a "$LOG"
    exit 1
fi

echo "Starting H-E1 experiment with real data..." | tee "$LOG"
echo "Pile n-grams: $PILE_NGRAMS_DIR" | tee -a "$LOG"
echo "GPU available: $(python -c 'import torch; print(torch.cuda.is_available())')" | tee -a "$LOG"

python run.py 2>&1 | tee -a "$LOG"

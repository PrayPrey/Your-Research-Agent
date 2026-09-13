#!/bin/bash
# Run 3 models in parallel on separate GPUs
BASE=/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/h-e1
LOGDIR="$BASE/code"

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1-v2

cd "$BASE/code"

# GPU 0: BERT
CUDA_VISIBLE_DEVICES=0 python run_experiment.py \
    --models bert-base-uncased \
    --max-workers 1 \
    --output-dir "$BASE" \
    --resume \
    > "$LOGDIR/experiment_bert.log" 2>&1 &
BERT_PID=$!
echo "BERT PID: $BERT_PID (GPU 0)"

# GPU 1: DeBERTa
CUDA_VISIBLE_DEVICES=1 python run_experiment.py \
    --models microsoft/deberta-v3-base \
    --max-workers 1 \
    --output-dir "$BASE" \
    --resume \
    > "$LOGDIR/experiment_deberta.log" 2>&1 &
DEBERTA_PID=$!
echo "DeBERTa PID: $DEBERTA_PID (GPU 1)"

# GPU 2: ViT
CUDA_VISIBLE_DEVICES=2 python run_experiment.py \
    --models google/vit-base-patch16-224 \
    --max-workers 1 \
    --output-dir "$BASE" \
    --resume \
    > "$LOGDIR/experiment_vit.log" 2>&1 &
VIT_PID=$!
echo "ViT PID: $VIT_PID (GPU 2)"

echo "Waiting for all 3 models to complete..."
wait $BERT_PID
BERT_EXIT=$?
echo "BERT done (exit=$BERT_EXIT)"

wait $DEBERTA_PID
DEBERTA_EXIT=$?
echo "DeBERTa done (exit=$DEBERTA_EXIT)"

wait $VIT_PID
VIT_EXIT=$?
echo "ViT done (exit=$VIT_EXIT)"

# Now run aggregation (summary + figures)
python run_experiment.py \
    --models bert-base-uncased microsoft/deberta-v3-base google/vit-base-patch16-224 \
    --max-workers 1 \
    --output-dir "$BASE" \
    --resume \
    > "$LOGDIR/experiment_aggregate.log" 2>&1

echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOGDIR/experiment.log"

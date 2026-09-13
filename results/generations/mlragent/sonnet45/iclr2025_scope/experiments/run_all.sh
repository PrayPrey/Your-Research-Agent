#!/bin/bash

# Automated experiment execution script
echo "=================================="
echo "Starting Adaptive Token Pruning Experiments"
echo "=================================="

# Run main experiment
echo ""
echo "Step 1: Running main experiment..."
python run_experiment.py \
    --model facebook/opt-125m \
    --chunk_size 128 \
    --train_epochs 3 \
    --max_samples 200 \
    --target_retention 0.5 \
    --output_dir . 2>&1 | tee -a log.txt

# Check if experiment succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "Step 2: Generating visualizations..."
    python visualize_results.py \
        --results_path experiment_results.json \
        --output_dir . 2>&1 | tee -a log.txt

    echo ""
    echo "=================================="
    echo "Experiments completed successfully!"
    echo "=================================="
    echo ""
    echo "Generated files:"
    ls -lh *.png *.json *.txt 2>/dev/null
else
    echo ""
    echo "ERROR: Experiment failed. Check log.txt for details."
    exit 1
fi

# Adaptive Token Pruning with Learnable Retention Policies

This repository contains the implementation and experiments for "Adaptive Token Pruning with Learnable Retention Policies for Efficient Long-Context Processing".

## Overview

The project implements a hierarchical token retention policy network that learns to adaptively prune tokens in long-context processing scenarios. The goal is to reduce KV cache size and inference latency while maintaining high task performance.

## Project Structure

```
claude_code/
├── run_experiment.py      # Main experiment script
├── visualize_results.py   # Visualization script for results
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── log.txt               # Experiment execution log
├── experiment_results.json  # Results in JSON format
└── *.png                 # Generated figures
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Experiments

### Quick Start

Run the full experiment with default settings:
```bash
python run_experiment.py
```

### Custom Configuration

Run with custom parameters:
```bash
python run_experiment.py \
    --model facebook/opt-125m \
    --chunk_size 128 \
    --train_epochs 3 \
    --max_samples 200 \
    --target_retention 0.5 \
    --output_dir .
```

### Parameters

- `--model`: HuggingFace model name (default: facebook/opt-125m)
- `--chunk_size`: Chunk size for hierarchical processing (default: 128)
- `--train_epochs`: Number of epochs to train policy network (default: 3)
- `--max_samples`: Maximum number of samples from dataset (default: 200)
- `--target_retention`: Target retention rate for baseline methods (default: 0.5)
- `--output_dir`: Output directory for results (default: .)

## Methods Evaluated

1. **None (Baseline)**: Full-context processing without pruning
2. **Static Pruning**: Keep first and last tokens based on fixed ratio
3. **Attention-based Pruning**: Prune tokens with low attention scores
4. **Adaptive Pruning** (Proposed): Learned hierarchical retention policy

## Evaluation Metrics

- **Retention Rate**: Fraction of tokens retained after pruning
- **Cache Reduction**: Percentage reduction in KV cache size
- **Latency**: Time to process each sample (seconds)
- **Memory Usage**: Approximate memory footprint (MB)

## Generating Visualizations

After running experiments, generate visualizations:
```bash
python visualize_results.py --results_path experiment_results.json --output_dir .
```

This generates:
- `comparison_metrics.png`: Bar charts comparing all metrics
- `efficiency_performance_tradeoff.png`: Scatter plot of efficiency vs performance
- `retention_distribution.png`: Box plots of retention rate distributions
- `radar_comparison.png`: Radar chart comparing methods across metrics
- `comparison_table.png`: Summary table of all methods

## Experimental Design

### Dataset
- Primary: NarrativeQA (long-context QA dataset)
- Fallback: SQuAD (if NarrativeQA unavailable)
- Context lengths: Up to 10,000 tokens

### Training Procedure
1. Load pre-trained transformer model
2. Initialize hierarchical token retention policy network
3. Train policy network with multi-objective loss:
   - Efficiency loss: Encourages sparsity
   - Coverage loss: Ensures information preservation
4. Evaluate all methods on held-out test set

### Policy Network Architecture
- Chunk-level encoder: 2-layer Transformer
- Query-aware attention mechanism
- Token-level scoring network with MLP
- Hierarchical gating for coarse-to-fine pruning

## Expected Results

Based on the proposal, we expect:
- 50-70% KV cache reduction
- <2% performance degradation compared to full-context
- Lower latency and memory usage
- Adaptive method outperforms static baselines

## Hardware Requirements

- GPU recommended (supports CPU fallback)
- ~8GB GPU memory for small models (OPT-125M)
- ~16GB+ for larger models (OPT-1.3B+)

## Notes

- The implementation uses a lightweight model (OPT-125M) for demonstration
- For production use, scale to larger models (LLaMA-7B, Mistral-7B)
- Training converges in 3-5 epochs with proper hyperparameters
- Adjust `max_samples` based on available memory and time constraints

## Citation

If you use this code, please cite:
```
@article{adaptive-token-pruning-2025,
  title={Adaptive Token Pruning with Learnable Retention Policies for Efficient Long-Context Processing},
  year={2025}
}
```

## License

MIT License

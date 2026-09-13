# QARP: Query-Aware Retention Policies for KV Cache Compression

This repository contains the experimental implementation for evaluating **QARP (Query-Aware Retention Policies)**, a novel framework for dynamic KV cache compression in transformer models.

## Overview

QARP addresses the critical memory bottleneck in long-context LLM inference by learning to predict which KV entries will be most relevant to future queries. The framework consists of:

1. **Relevance Predictor Network (RPN)**: A lightweight transformer that scores KV entries based on learned query prototypes
2. **Adaptive Retention Policy**: Budget-constrained optimization over compression operations (full retention, quantization, merging, eviction)
3. **Continual Calibration**: Online adaptation using attention feedback

## Methods Compared

- **Full Cache**: Baseline with no compression
- **StreamingLLM**: Attention sinks + recent window
- **H2O (Heavy Hitter Oracle)**: Retention based on cumulative attention
- **4-bit/8-bit Quantization**: Uniform quantization baseline
- **QARP**: Proposed query-aware compression at different compression ratios

## Installation

```bash
pip install torch transformers datasets tqdm matplotlib pandas numpy
```

## Usage

### Run Full Experiment

```bash
python run_experiment.py \
    --model meta-llama/Llama-3.2-1B \
    --output_dir outputs \
    --max_seq_length 1024 \
    --train_samples 200 \
    --test_samples 100 \
    --num_epochs 3 \
    --eval_batches 25 \
    --run_ablation
```

### Quick Test

```bash
python run_experiment.py \
    --model meta-llama/Llama-3.2-1B \
    --output_dir outputs \
    --max_seq_length 512 \
    --train_samples 50 \
    --test_samples 25 \
    --num_epochs 1 \
    --eval_batches 10
```

### Skip RPN Training (Use Random Initialization)

```bash
python run_experiment.py --skip_training
```

## Output Structure

```
outputs/
├── log.txt                      # Experiment log
├── results.json                 # Raw results
├── results_table.csv            # Results summary table
├── training_curves.png          # RPN training curves
├── compression_comparison.png   # Method comparison
├── perplexity_vs_compression.png  # Trade-off plot
├── memory_efficiency.png        # Memory vs accuracy
├── latency_comparison.png       # Latency comparison
├── radar_comparison.png         # Multi-metric radar chart
└── ablation_study.png          # Ablation results (if enabled)
```

## Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--model` | HuggingFace model name | meta-llama/Llama-3.2-1B |
| `--max_seq_length` | Maximum sequence length | 1024 |
| `--train_samples` | Training samples for RPN | 200 |
| `--test_samples` | Test samples | 100 |
| `--num_epochs` | RPN training epochs | 3 |
| `--eval_batches` | Batches for evaluation | 25 |
| `--run_ablation` | Run ablation study | False |

## File Structure

- `config.py`: Configuration dataclasses
- `kv_cache.py`: KV cache compression implementations (QARP, StreamingLLM, H2O, Quantization)
- `data_utils.py`: Dataset utilities
- `evaluation.py`: Evaluation metrics
- `train_rpn.py`: RPN training via attention distillation
- `visualization.py`: Visualization utilities
- `run_experiment.py`: Main experiment runner

## Expected Results

Based on the proposed methodology, QARP should achieve:
- 4-8x KV cache compression
- <2% perplexity degradation at 4x compression
- Improved memory efficiency compared to static compression methods

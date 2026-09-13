# EmbedPrint: Provenance-Aware Data Attribution via Efficient Embedding Fingerprints

This repository contains the implementation and experiments for **EmbedPrint**, a lightweight data attribution framework that embeds compact, learnable fingerprints into the representation space during foundation model training.

## Overview

EmbedPrint addresses the challenge of attributing foundation model outputs to specific training data for:
- Copyright compliance
- Data marketplace compensation
- Model debugging
- Transparency requirements

### Key Features

1. **Training-time Fingerprint Embedding**: Clusters training data and assigns learnable signature vectors optimized jointly with model parameters
2. **Contrastive Auxiliary Loss**: Encourages output embeddings to align with cluster signatures
3. **Real-time Attribution**: Decodes signatures from output embeddings with minimal computational overhead (<2% inference cost)

## Installation

```bash
# Install required packages
pip install torch transformers datasets sentence-transformers scikit-learn matplotlib seaborn pandas tqdm
```

## Project Structure

```
claude_code/
├── config.py           # Configuration classes
├── data_utils.py       # Data loading and clustering utilities
├── models.py           # EmbedPrint model implementation
├── baselines.py        # Baseline attribution methods
├── trainer.py          # Training utilities
├── evaluation.py       # Evaluation metrics
├── visualization.py    # Visualization utilities
├── run_experiment.py   # Main experiment script
└── README.md           # This file
```

## Running the Experiment

### Basic Usage

```bash
python run_experiment.py
```

### With Custom Parameters

```bash
python run_experiment.py \
    --model_name distilgpt2 \
    --num_train_samples 3000 \
    --num_eval_samples 300 \
    --num_canary_samples 100 \
    --num_epochs 3 \
    --batch_size 16 \
    --output_dir outputs \
    --seed 42
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--model_name` | distilgpt2 | Pretrained model name |
| `--num_train_samples` | 3000 | Number of training samples |
| `--num_eval_samples` | 300 | Number of evaluation samples |
| `--num_canary_samples` | 100 | Number of canary samples for evaluation |
| `--num_epochs` | 3 | Number of training epochs |
| `--batch_size` | 16 | Batch size |
| `--output_dir` | outputs | Output directory |
| `--seed` | 42 | Random seed |

## Methodology

### 1. Hierarchical Data Clustering

Training data is clustered into semantically coherent groups:
- **Level 1 (Coarse)**: K1 clusters using sentence embeddings
- **Level 2 (Fine)**: K2 sub-clusters per coarse cluster

### 2. Learnable Signature Vectors

Each cluster is assigned a learnable signature vector initialized with orthogonal projections:
- Signature dimension: 64
- Projection dimension: 256

### 3. Contrastive Fingerprint Loss

```
L_total = L_task + λ * L_fp

L_fp = -log(exp(sim(h_i, s_c(i))/τ) / Σ_j exp(sim(h_i, s_j)/τ))
```

Where:
- λ = 0.01 (fingerprint loss weight)
- τ = 0.07 (temperature)

### 4. Inference-time Attribution

At inference, cluster probabilities are computed via similarity to all signatures:
```
p(c | x) = softmax(P(f_θ(x)) · S^T)
```

## Baselines

1. **Embedding Similarity**: Pretrained sentence embeddings for similarity-based attribution
2. **Random**: Random cluster assignment (lower bound)

## Evaluation Metrics

- **Precision@K**: Fraction of queries with correct cluster in top-K
- **Recall@K**: Same as Precision@K for single ground-truth
- **MRR**: Mean Reciprocal Rank
- **Latency**: Attribution time per query (ms)
- **Throughput**: Queries per second
- **Perplexity**: Language model quality metric

## Output

Results are saved in `outputs/results/`:
- `log.txt`: Experiment execution log
- `results.json`: Complete results in JSON format
- `results_table.csv`: Summary table
- Various visualization figures

## Expected Results

Based on the experimental design:
- **Precision@10**: >70% for EmbedPrint
- **Latency**: <5ms per query
- **Perplexity Degradation**: <1%

## References

This implementation is based on the research proposal "Provenance-Aware Data Attribution via Efficient Embedding Fingerprints for Foundation Models".

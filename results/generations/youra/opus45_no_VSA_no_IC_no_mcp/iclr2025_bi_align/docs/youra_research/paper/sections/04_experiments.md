# 4. Experiments

## Training Configuration

### RLHF Reward Model (H-M1)

| Parameter | Value |
|-----------|-------|
| Base model | meta-llama/Llama-2-7b-hf |
| Fine-tuning | LoRA (r=16, alpha=32) |
| Learning rate | 1e-4 |
| Batch size | 4 (effective 16 with gradient accumulation) |
| Epochs | 1 |
| Loss | Bradley-Terry + center_rewards (0.01) |
| Optimizer | AdamW |

### DPO Policy (H-M2)

| Parameter | Value |
|-----------|-------|
| Base model | meta-llama/Llama-2-7b-hf |
| Fine-tuning | LoRA (r=16, alpha=32) |
| Learning rate | 5e-7 |
| Beta | 0.1 |
| Batch size | 2 (effective 16 with gradient accumulation) |
| Epochs | 1 |

### Evaluation Protocol

Benchmarks evaluated with standardized prompts:
- **TruthfulQA:** Multiple-choice format (MC1), accuracy metric
- **HHH-helpful/harmless:** Pairwise preference accuracy

## Compute Environment

Experiments executed on a single GPU with LoRA fine-tuning to enable reproducibility. H-M3 and H-M4 used quick validation mode (simulation) due to compute constraints—full replication requires multi-GPU training for the 5-seed experimental design.

## Reproducibility

All code, configurations, and trained adapters are provided:
- `h-e1/code/` - Benchmark correlation analysis
- `h-m1/code/` - RLHF reward model training
- `h-m2/code/` - DPO sharpness metrics
- `h-m3/code/` - Clustering analysis
- `h-m4/code/` - Differential profile evaluation

Random seeds fixed at [42, 137] for reproducibility. All experiments logged training/evaluation metrics to JSON files.

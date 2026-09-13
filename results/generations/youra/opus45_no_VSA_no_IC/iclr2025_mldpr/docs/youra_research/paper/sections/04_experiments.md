# Experimental Setup

## Research Questions

We design experiments to test three sub-hypotheses derived from the main benchmark fingerprint hypothesis:

**H-E1 (Existence):** Can a linear classifier predict which benchmark was used to fine-tune a model from its representations? Success criterion: accuracy > 60%.

**H-M1 (Mechanism):** Does Benchmark Fingerprint Score correlate with cross-dataset performance gap? Success criterion: r > 0.3, p < 0.05.

**H-M2 (Comparison):** Do single-benchmark models show larger gaps than multi-benchmark models? Success criterion: >5 percentage point difference.

## Datasets

### Fine-Tuning Benchmarks

For the proof-of-concept experiment, we use two benchmarks with distinct visual characteristics:

| Dataset | Classes | Images | Domain |
|---------|---------|--------|--------|
| Flowers102 | 102 | 8,189 | Fine-grained flowers |
| CIFAR-100 | 100 | 60,000 | Coarse-grained objects |

This selection tests whether fingerprints emerge across different visual domains (fine-grained plants vs. diverse objects).

### Probe Dataset

We use CIFAR-100 test set (10,000 images) as the probe dataset for feature extraction. This provides a standardized input for comparing representations across fine-tuned models.

## Model Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Architecture | ResNet-50 | Standard, well-studied |
| Pretraining | ImageNet-1K | Controlled initialization |
| Fine-tuning epochs | 10 | PoC scope |
| Learning rate | 0.01 | Standard transfer learning |
| Optimizer | SGD + momentum | Reproducible baseline |
| Seeds | 3 per benchmark | Variance estimation |

## Evaluation Protocol

### H-E1: Fingerprint Detection

1. Fine-tune 6 models (2 benchmarks × 3 seeds)
2. Extract 2048-d avgpool features on probe dataset
3. Aggregate features: 5,000 samples per model → 30,000 total
4. Train logistic regression (80/20 split by model)
5. Report test accuracy with bootstrap CI

### H-M1: BFS-Gap Correlation

1. Compute BFS for each model (classifier confidence for true benchmark)
2. Evaluate each model on in-domain and cross-domain datasets
3. Compute gap = in-domain accuracy - cross-domain accuracy
4. Calculate Pearson correlation between BFS and gap

### H-M2: Training Regime Comparison

1. Train single-benchmark models (1 benchmark) and multi-benchmark models (3+ benchmarks mixed)
2. Evaluate both on held-out benchmark
3. Compare mean gaps with t-test

**Note:** H-M2 infrastructure was implemented but requires real fine-grained datasets; results below reflect H-E1 and H-M1 only.

## Baselines

| Baseline | Purpose |
|----------|---------|
| Shuffled labels | Verify fingerprint signal is real, not classifier artifact |
| Chance level (50%) | Expected accuracy with random guessing (2 benchmarks) |
| Zero correlation | Null hypothesis for BFS-gap relationship |

## Compute Resources

- Hardware: Single NVIDIA GPU (A100)
- PoC runtime: ~15 minutes
- Full experiment estimate: ~13 GPU-hours

# Experimental Setup

We design experiments to answer two questions: (1) Does SEDP achieve meaningful SE correlation, meeting our existence proof threshold? (2) Does similarity augmentation improve over the hidden-state-only baseline? This section details our experimental configuration.

## Research Questions

**RQ1: Existence Proof** — Does SEDP achieve Spearman ρ ≥ 0.3 with true semantic entropy?

This is our MUST_WORK gate. Failure indicates the fundamental approach does not work under the tested configuration; success would motivate further investigation.

**RQ2: Similarity Benefit** — Does SEDP (hidden + similarity) outperform SEP (hidden only)?

Even if both methods fail the absolute threshold, a positive delta would confirm that similarity features contribute useful information.

## Dataset

**TruthfulQA** is a benchmark of 817 questions designed to elicit false beliefs from language models. Questions span 38 categories including health, law, finance, and politics. We use the generation configuration from HuggingFace.

| Property | Value |
|----------|-------|
| Total questions | 817 |
| Train split | 653 (80%) |
| Test split | 164 (20%) |
| Split method | Random, seed=42 |

**Why TruthfulQA**: It is the standard benchmark for hallucination detection, used in both the original SE paper and SEP work. Using the same benchmark enables direct comparison with published results.

## Model Configuration

**Language Model**: Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
- Architecture: Decoder-only transformer, 32 layers
- Hidden dimension: 4096
- Precision: float16
- Inference: Single A100 GPU

**Generation Settings**:
- Responses per question: N = 20
- Temperature: T = 0.7
- Max new tokens: 100

**Hidden State Extraction**:
- Layer: 25 of 32
- Token position: TBG (Token Before Generation)
- Output dimension: 4096

**Entailment Model**: DeBERTa-v3-large-MNLI
- Used for semantic clustering in SE computation
- Entailment threshold: 0.5 (bidirectional)

**Similarity Embedding**: all-MiniLM-L6-v2
- Used for response similarity computation
- Output dimension: 384

## Baselines

**SEP (Semantic Entropy Probe)**: Logistic regression trained on hidden states only (4096 features). This represents the published approach from Kossen et al.

**Random Baseline**: AUROC = 0.50, Spearman ρ = 0.0. This is the expected performance of a classifier that ignores inputs.

## Implementation Details

**Probe Training**:
- Architecture: Logistic regression (sklearn)
- Regularization: L2 with C = 1.0
- Optimizer: LBFGS
- Max iterations: 1000
- Random seed: 42

**Compute Resources**:
- Hardware: Single NVIDIA A100 (40GB)
- Response generation: ~2-4 hours for full dataset
- SE label computation: ~1 hour
- Probe training: < 1 minute

**Caching**: All intermediate artifacts (hidden states, responses, SE labels, similarity features) are cached to disk to enable reproducible re-runs without repeating expensive generation.

## Evaluation Protocol

We evaluate on the held-out test set (164 questions):

1. **Spearman Correlation**: Between probe output probabilities and continuous SE values
   - Threshold: ρ ≥ 0.3 (MUST_WORK gate), target ρ ≥ 0.7
   - Statistical significance: p < 0.05

2. **AUROC**: Binary classification of high vs. low SE questions
   - Threshold: meaningful improvement over 0.50 (random)
   - Published comparison: SEP achieves ~0.85 on TruthfulQA

3. **Effect Direction**: SEDP ρ > SEP ρ confirms similarity features help (even if both fail absolute thresholds)

## Reproducibility

All code, cached artifacts, and configuration files are preserved. The experiment can be reproduced by running `run_experiment.py` with the default configuration. Fixed random seed (42) ensures deterministic train/test splits and probe training.

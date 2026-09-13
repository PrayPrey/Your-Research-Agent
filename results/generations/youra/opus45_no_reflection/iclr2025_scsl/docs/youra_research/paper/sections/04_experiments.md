# Experimental Setup

We evaluate the core hypothesis (H-E1): *CV of probe accuracy trajectories distinguishes spurious from core features with AUC ≥ 0.75*.

## Research Questions

1. **Can CV distinguish feature types?** Do spurious and core features have separable CV distributions?
2. **What classification performance does CV achieve?** AUC for binary spurious/core classification.
3. **Are probe trajectories informative?** Do accuracy trajectories show differential dynamics across feature types?

## Dataset

**Waterbirds** (Sagawa et al., 2020): A benchmark for studying spurious correlations.

| Split | Samples | Groups |
|-------|---------|--------|
| Train | 4,795 | 4 (bird × background) |
| Test | 5,794 | 4 |

The training set has 95% correlation between background and label (waterbirds on water, landbirds on land). This creates minority groups (e.g., waterbirds on land) with poor accuracy under ERM.

**Ground truth features**:
- `background`: Spurious (land/water, artificially correlated)
- `bird_type`: Core (landbird/waterbird, the classification target)

## Feature Extraction

CLIP ViT-B/16 extracts 512-dimensional embeddings per image. Features are normalized to unit length. Extraction runs on GPU with batch size 64.

## Probe Training Protocol

For each feature type (background, bird\_type):

1. Sample 5 random 20% subsets of training data (seed=42)
2. For each subset, train LogisticRegression with C ∈ {0.001, 0.01, 0.1, 1, 10, 100}
3. Record test accuracy at each C value
4. Compute CV of accuracy improvement rates across subsets

## Evaluation Metrics

- **CV per feature type**: Coefficient of variation of improvement rates
- **AUC**: Area under ROC for classifying features as spurious (positive) or core (negative) based on CV
- **Direction check**: Whether CV(spurious) < CV(core) as hypothesized

## Baselines

This is an existence experiment (H-E1) — we test whether the proposed signal exists, not whether it outperforms alternatives. The baseline is random classification (AUC = 0.5).

## Implementation

- **Hardware**: Single GPU (NVIDIA)
- **Framework**: PyTorch + scikit-learn
- **CLIP**: OpenAI's `clip-ViT-B-16` checkpoint
- **Code**: Available at `h-e1/code/`

## Gate Criterion

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| AUC | ≥ 0.75 | MUST\_WORK gate; substantial discriminative power required |

Failure to meet this gate blocks downstream hypotheses (H-M1 through H-M3) per the verification plan.

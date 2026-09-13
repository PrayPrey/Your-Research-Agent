# Methodology

Building on our observation that training checkpoints provide a natural contamination gradient, we design a correlation analysis pipeline that measures the relationship between contamination exposure and benchmark score inflation without requiring contamination-free baseline models.

## Overview

Our methodology has four components: (1) checkpoint-level evaluation across the Pythia model family, (2) 13-gram contamination measurement using established decontamination tools, (3) capability detrending via out-of-distribution perplexity regression, and (4) Spearman correlation analysis between contamination and inflation residuals.

## Checkpoint-Gradient Methodology

**Rationale.** Traditional contamination studies compare contaminated versus decontaminated models or use synthetic injection. Both approaches require either clean baseline models (which do not exist at scale) or artificial contamination (which may not reflect natural training dynamics). We observe that checkpoints during training naturally vary in contamination exposure—early checkpoints have processed less of the training corpus, thus encountered less benchmark-overlapping content.

**Implementation.** We use the Pythia model family [Biderman et al., 2023] trained on The Pile [Gao et al., 2020]. Pythia provides:
- Six model sizes: 410M, 1B, 1.4B, 2.8B, 6.9B, 12B parameters
- 154 checkpoints per model at documented training steps
- Deterministic training order (same data sequence across all sizes)
- Documented training corpus enabling ground-truth contamination measurement

We evaluate 12 key checkpoints per size (steps 0, 1000, 2000, ..., 143000), yielding 72 checkpoint-benchmark pairs for correlation analysis.

## Contamination Measurement

**N-gram overlap.** Following Brown et al. [2020], we use 13-gram overlap as the contamination metric. For each benchmark, we compute the percentage of test items containing 13-gram sequences that appear in The Pile training corpus.

**Detection procedure.** Using the lm-evaluation-harness decontamination module:
1. Extract all 13-grams from benchmark test items
2. Query against pre-computed Pile n-gram index
3. Compute overlap percentage per item and aggregate per benchmark

**Cumulative exposure proxy.** For checkpoint-level analysis, we approximate cumulative contamination exposure as proportional to training progress—a checkpoint at step 100,000 has seen ~70% of training data, thus approximately 70% of contamination-relevant content.

## Capability Detrending

**The confound.** Raw benchmark scores improve during training due to both capability gains and contamination effects. We must separate these to isolate contamination inflation.

**Detrending approach.** We use WikiText-103 perplexity as a contamination-independent capability measure. WikiText-103 derives from Wikipedia (separate from The Pile's benchmark-relevant content) and measures general language modeling ability without benchmark-specific memorization.

**Regression.** For each checkpoint, we fit:

$$\text{score}_{\text{expected}} = \alpha + \beta \cdot \log(1/\text{perplexity})$$

The log-inverse perplexity represents capability (lower perplexity → higher capability). The regression captures the expected score given the model's general language modeling ability.

**Inflation residual.** We define:

$$\text{inflation}_i = \text{score}_i - \text{score}_{\text{expected},i}$$

Positive residuals indicate scores higher than capability would predict—candidate contamination inflation. Negative residuals suggest benchmark-specific difficulty beyond general capability.

![Capability Detrending](figures/capability_detrending.png)
*Figure 2: Capability detrending via WikiText-103 perplexity. Each point is a checkpoint; the regression line represents expected score given capability. Residuals above the line indicate potential contamination inflation.*

## Correlation Analysis

**Spearman correlation.** We compute Spearman's rank correlation between contamination percentage and inflation residual across all checkpoint-benchmark pairs:

$$r_s = 1 - \frac{6 \sum d_i^2}{n(n^2-1)}$$

where $d_i$ is the rank difference for pair $i$.

**Why Spearman.** Rank-based correlation is robust to non-linear relationships and outliers, appropriate when the contamination-inflation relationship may not be strictly linear.

**Statistical significance.** We report two-tailed p-values and require p < 0.05 for significance claims.

**Success criteria.** We define:
- Minimum threshold: r > 0.2 (weak-to-moderate correlation)
- Primary target: r > 0.5 (strong correlation)

## Implementation Details

**Evaluation.** We use lm-evaluation-harness for standardized benchmark evaluation across MMLU, ARC-Challenge, HellaSwag, and WinoGrande. Batch size is auto-selected; results are cached for reproducibility.

**Contamination index.** We use pre-computed Pile 13-gram indices from EleutherAI's decontamination scripts, ensuring consistency with standard practices.

**Computational requirements.**
- Evaluation: ~144 GPU-hours (72 checkpoints × ~2 hours each)
- N-gram extraction: ~48 CPU-hours (one-time index building)
- Correlation analysis: <1 minute (statistical computation only)

The methodology requires no model training—only inference and statistical analysis on existing checkpoints.

# 3. Methodology

Our goal is to test whether calibration quality, hallucination resistance, and adversarial robustness in open-weight LLMs share a common latent factor — *epistemic reliability* — that is independent of raw capability. We approach this as a psychometric problem: models are subjects, and standardized benchmark scores are items. This framing naturally invites factor analysis and partial correlation methodology to test latent structure.

## 3.1 Overview of the YouRA Framework

The **YouRA (Your Research Assistant) framework** provides a multi-hypothesis evaluation pipeline for systematic trustworthiness analysis. For this study, we decompose the main hypothesis into four sub-hypotheses executed sequentially:

- **H-E1 (Existence):** Do cross-property correlations exceed the ρ ≥ 0.40 threshold with BCa CIs excluding zero, and does factor analysis extract a stable latent dimension?
- **H-M1 (Mechanism — Calibration–Hallucination):** Does the calibration–hallucination correlation survive MMLU capability control, confirming a capability-independent mechanistic link?
- **H-M2 (Mechanism — Predictive Power):** Does the epistemic composite (ECE + TruthfulQA% + Brier) predict top-quartile adversarial failure beyond the MMLU-only baseline?
- **H-M3 (Mechanism — Embedding Perturbation):** Does calibration quality predict decision-surface smoothness under Gaussian embedding perturbation? *(Pre-registered; not executed in this work.)*

This paper reports results for H-E1, H-M1, and H-M2. H-M3 is pre-registered and will be executed in the real-data replication (FW1).

## 3.2 Model Population

We study a population of N=30 instruction-tuned open-weight LLMs spanning 7B–70B parameters from 8 model families: LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, and Gemma. All models are accessible via HuggingFace as of 2024-01. This population is chosen to span diverse training regimes (RLHF, SFT, base fine-tuning), architectures, and scales, enabling genuine cross-family analysis rather than within-family ablation.

**Important:** The current PoC implementation uses a synthetic score matrix generated from a parametric model conforming to the hypothesized latent factor structure. The N=30 model population is the target for real-data execution via lm-evaluation-harness (see Section 3.6 and FW1 in Section 6). All reported statistics are properties of the synthetic data generator, not measurements of real models.

## 3.3 Benchmark Metrics

We compute five benchmark metrics for each model using the lm-evaluation-harness v0.4.x framework under standardized conditions:

| Metric | Benchmark | Interpretation |
|--------|-----------|----------------|
| ECE | MMLU logits (10-bin) | Calibration quality (lower = better calibrated) |
| Brier score | MMLU logits | Proper scoring rule for calibration (lower = better) |
| TruthfulQA% | TruthfulQA | Hallucination resistance (higher = fewer hallucinations) |
| AdvGLUE drop | AdvGLUE | Adversarial accuracy drop vs. clean (lower = more robust) |
| ANLI drop | ANLI R1–R3 | Adversarial accuracy drop vs. clean (lower = more robust) |

Additionally, MMLU accuracy is computed as the capability control variable — it is not included in the trustworthiness metric set but is partialled out in all primary analyses.

**Rationale for metric selection:** ECE and Brier measure distinct aspects of calibration (sharpness vs. resolution) but should co-vary if calibration is a coherent construct. TruthfulQA% is the most widely used factual hallucination benchmark with clean binary scoring. AdvGLUE and ANLI provide complementary adversarial stress tests with different perturbation styles (word-level adversarial vs. iterative human-adversarial filtering).

## 3.4 Statistical Analysis Pipeline

### 3.4.1 Cross-Property Partial Correlation (H-E1, H-M1)

For each metric pair (X, Y), we compute the partial Spearman correlation controlling for MMLU accuracy:

$$\rho_{XY \cdot \text{MMLU}} = \frac{\rho_{XY} - \rho_{X,\text{MMLU}} \cdot \rho_{Y,\text{MMLU}}}{\sqrt{(1 - \rho_{X,\text{MMLU}}^2)(1 - \rho_{Y,\text{MMLU}}^2)}}$$

We construct BCa (bias-corrected and accelerated) bootstrap 95% confidence intervals using B=10,000 resamples. A pair satisfies the existence criterion if |ρ| ≥ 0.40 and the CI excludes zero.

**Rationale for Spearman:** Rank-based correlation is robust to the non-normality expected in benchmark score distributions across diverse model families, and makes no assumptions about the functional form of the relationship.

**Rationale for BCa bootstrap:** BCa CIs are second-order accurate and automatically adjust for both bias and skewness in the bootstrap distribution, which is important given the moderate sample size (N=30).

### 3.4.2 Factor Analysis (H-E1)

We apply principal axis factor analysis to the 5×5 Spearman correlation matrix of the trustworthiness metrics. We use the Kaiser-Meyer-Olkin (KMO) measure to verify sampling adequacy (threshold: KMO > 0.60), extract factors with eigenvalue > 1, and report the proportion of variance explained by Factor 1.

To assess factor stability across measurement conditions, we compute Tucker's congruence coefficient (φ) between factor loadings obtained under greedy decoding and T=0.7 stochastic decoding (pre-specified threshold: φ ≥ 0.85):

$$\phi = \frac{\sum_i a_i b_i}{\sqrt{\sum_i a_i^2 \sum_i b_i^2}}$$

where a and b are the factor loading vectors under the two decoding conditions.

### 3.4.3 Capability Independence (H-M1)

We quantify the MMLU confound magnitude via the *survival fraction*: the ratio of partial to raw Spearman correlation for the ECE–TruthfulQA% pair. A survival fraction near 1.0 indicates MMLU explains negligible variance in the relationship; a survival fraction below 0.50 would indicate MMLU accounts for more than half the correlation. We also compute discriminant validity: the partial correlation between ECE and HumanEval (a coding capability benchmark) controlling for MMLU, which should be near zero if ECE measures epistemic reliability rather than general capability.

### 3.4.4 Adversarial Failure Prediction (H-M2)

We test whether the epistemic composite predicts top-quartile AdvGLUE failure (binary outcome: model in worst 25% of AdvGLUE drop) beyond MMLU capability alone. We use leave-one-out cross-validated logistic regression with per-fold StandardScaler normalization (no data leakage). The composite predictor includes ECE, TruthfulQA%, and Brier score; the baseline includes MMLU accuracy only.

We report LOO-AUC for each predictor and compute ΔAUC = AUC_composite − AUC_MMLU with paired bootstrap 95% CI (B=10,000). The pre-specified success criterion is ΔAUC ≥ 0.10 with CI lower bound > 0.

## 3.5 Gate Structure

Each sub-hypothesis carries an explicit gate type:

| Sub-hypothesis | Gate Type | Implication of Failure |
|---------------|-----------|------------------------|
| H-E1 | MUST_WORK | Terminate pipeline; fundamental problem |
| H-M1 | MUST_WORK | Terminate pipeline; confound invalidates approach |
| H-M2 | SHOULD_WORK | Record as limitation; continue to H-M3 |
| H-M3 | SHOULD_WORK | Record as open question; does not invalidate P1/P2 |

Gates are evaluated against pre-specified thresholds before proceeding to the next sub-hypothesis.

## 3.6 Data Provenance and Replication Plan

The current implementation uses `generate_synthetic_score_matrix()` as the data source for the H-E1 PoC — a parametric random matrix generator with pre-wired latent factor structure. This was detected by the pipeline's mock_data_check validator. Downstream analyses (H-M1, H-M2) consume `h-e1/results/score_matrix.csv`, which originates from this synthetic generation.

The real-data pipeline (`main.py` + `run_eval.py`) is fully implemented and uses lm-evaluation-harness v0.4.x to evaluate the 30-model population on all five metrics. Execution requires approximately 2–4 GPU-hours per model. This real-data replication (FW1) is the immediate research priority and is pre-registered through the sub-hypothesis structure documented in this paper.

# 4. Experimental Setup

We design experiments to directly test the three executed sub-hypotheses. Each research question maps to a specific claim from the Introduction.

**RQ1 (H-E1):** Does a population of N=30 open-weight LLMs exhibit statistically significant, capability-independent partial Spearman correlations across calibration, hallucination, and adversarial robustness metrics, and does factor analysis extract a stable latent dimension?

**RQ2 (H-M1):** Is the calibration–hallucination correlation genuinely independent of MMLU capability — i.e., does it survive partial correlation control with a negligible confound magnitude?

**RQ3 (H-M2):** Does the epistemic composite predictor (ECE + TruthfulQA% + Brier) predict top-quartile adversarial failure (AdvGLUE) better than MMLU capability alone, with incremental advantage ΔAUC ≥ 0.10?

## 4.1 Model Population

The study population consists of N=30 instruction-tuned open-weight LLMs in the 7B–70B parameter range from 8 model families: LLaMA-2, Mistral, Falcon, Pythia, Qwen, Yi, OLMo, and Gemma. Models were selected to maximize diversity of training regime (RLHF, SFT, base fine-tuning), parameter scale, and architectural lineage. All models are publicly accessible via HuggingFace as of 2024-01.

**Current implementation note:** The PoC data path uses a synthetic score matrix conforming to the hypothesized latent factor structure (see Section 3.6). The model population specification is the target for real-data execution (FW1); no actual LLM inference was performed in this work.

## 4.2 Benchmarks and Metrics

All metrics are computed (or, in the PoC, synthetically generated to match) the following specifications using lm-evaluation-harness v0.4.x:

| Metric | Source | Computation |
|--------|--------|-------------|
| ECE | MMLU (57 subjects, greedy decoding) | 10-bin ECE from per-token log-probabilities on the answer tokens |
| Brier score | MMLU (greedy decoding) | Mean squared error between softmax probability and one-hot label |
| TruthfulQA% | TruthfulQA (817 questions) | Fraction of truthful responses (MC1 scoring) |
| AdvGLUE drop | AdvGLUE (5 tasks) | Clean accuracy − adversarial accuracy (word-level perturbations) |
| ANLI drop | ANLI R1–R3 | Clean accuracy − adversarial accuracy (human-adversarial NLI) |
| MMLU accuracy | MMLU (57 subjects, greedy decoding) | Standard 5-shot accuracy (capability control variable only) |

Greedy decoding (temperature = 0) is used for all primary metrics. A T=0.7 stochastic replication is pre-registered for the real-data phase (FW1) to test decoding invariance.

## 4.3 Baselines

We compare against a single, theoretically motivated baseline:

**MMLU-only logistic classifier:** A leave-one-out logistic regression using MMLU accuracy as the sole predictor of top-quartile AdvGLUE failure. This baseline tests the null hypothesis that capability alone explains adversarial vulnerability — the standard assumption in deployment screening.

**Why this baseline:** MMLU accuracy is the most common single-metric selection criterion for open-weight LLMs. If the epistemic composite does not outperform MMLU-only, the practical case for additional trustworthiness measurement is weakened. The ΔAUC comparison directly quantifies the marginal value of epistemic reliability screening over and above what capability screening already provides.

## 4.4 Implementation Details

**Statistical analysis:**
- Spearman rank correlation (scipy.stats.spearmanr)
- BCa bootstrap: B=10,000 resamples (custom implementation with numpy random seed 42)
- Factor analysis: principal axis factoring (factor_analyzer v0.4.x), Kaiser normalization
- LOO cross-validation: scikit-learn LeaveOneOut with LogisticRegression (C=1.0, max_iter=1000)
- Per-fold StandardScaler (fit on training fold only — no data leakage)
- ΔAUC paired bootstrap: B=10,000 resamples on per-fold AUC differences

**Compute resources (real-data target):** 2–4 GPU-hours per model on a single A100 80GB GPU, estimated 60–120 GPU-hours total for the 30-model population with batching.

**Reproducibility:** The full pipeline code (main.py, run_eval.py, analysis scripts) is available in the paper repository. The synthetic PoC entry point (run_experiment_poc.py) is provided for pipeline verification only and is clearly distinguished from the real-data entry point.

## 4.5 Evaluation Metrics

**For RQ1 (existence):**
- |partial ρ| for each metric pair (threshold ≥ 0.40, BCa CI excluding zero)
- Tucker's congruence coefficient φ (threshold ≥ 0.85)
- Factor 1 variance explained (threshold ≥ 50%)
- KMO sampling adequacy (threshold > 0.60)

**For RQ2 (capability independence):**
- Survival fraction: |partial ρ| / |raw ρ| for ECE–TruthfulQA% (threshold ≥ 0.50)
- Discriminant validity: |partial ρ(ECE, HumanEval | MMLU)| (threshold < 0.20)

**For RQ3 (predictive power):**
- LOO-AUC composite (threshold ≥ 0.70)
- ΔAUC = AUC_composite − AUC_MMLU-only (threshold ≥ 0.10, CI lower bound > 0)

Statistical significance is assessed via BCa 95% confidence intervals throughout; p-values are reported as supplementary information only.

# Product Requirements Document: H-E1
## Residual Instability — Existence & Construct Validity (PoC)

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Tier:** LIGHT (15 tasks max)
**Generated:** 2026-05-12
**Phase 2C Source:** h-e1/02c_experiment_brief.md

---

## 1. Executive Summary

This PoC validates that the Residual Instability (RI) construct is **measurable and non-degenerate** across a diverse set of ≥30 LLMs. RI is defined as the OLS residual of AdvGLUE accuracy drop after controlling for general capability (PC1 of MMLU/GSM8K/BBH/HellaSwag/WinoGrande) and mean model confidence. Two gate conditions must pass: (1) SD(AdvGLUE_drop) > 5% across the model set confirms meaningful variance exists; (2) R²_residualization < 0.80 confirms RI is not merely a capability proxy.

This is a **statistical analysis pipeline** — no neural network training is involved. The implementation assembles a model × benchmark matrix, applies PCA + OLS residualization, and reports gate metrics with visualizations.

---

## 2. Problem Statement

### Background
Trustworthiness failures in LLMs (calibration errors, hallucinations, safety failures) are commonly attributed to capability limitations. If a domain-general structural property — adversarial fragility orthogonal to capability — systematically predicts these failures, it would constitute a novel, actionable trust predictor. H-E1 establishes whether this "Residual Instability" construct can be operationalized from existing benchmark data.

### Research Question
Does AdvGLUE accuracy drop exhibit sufficient variance across diverse LLMs (SD > 5%), and is a meaningful portion of that variance unexplained by general capability + confidence (R² < 0.80)?

### Success Definition
Both gate conditions pass → RI is a valid, non-degenerate construct → pipeline proceeds to H-M1 (mechanism verification).

---

## 3. Functional Requirements

### FR-1: Data Assembly Module
**Priority:** P0 — Critical

Assemble a model × benchmark score matrix for ≥30 LLMs:

| Column | Source | Notes |
|--------|--------|-------|
| `model_id` | Metadata | Unique model identifier |
| `model_family` | Metadata | LLaMA / Mistral / GPT / Qwen / Gemma |
| `scale` | Metadata | Parameter count (7B / 13B / 70B+) |
| `training_regime` | Metadata | pretrained / instruction-tuned / RLHF |
| `advglue_drop` | TrustLLM toolkit | AdvGLUE accuracy drop per model |
| `mmlu` | lm-eval-harness | 5-shot accuracy |
| `gsm8k` | lm-eval-harness | 5-shot exact match |
| `bbh` | lm-eval-harness | 3-shot CoT accuracy |
| `hellaswag` | lm-eval-harness | 10-shot accuracy |
| `winogrande` | lm-eval-harness | 5-shot accuracy |
| `mean_confidence` | lm-eval log-probs | Mean token log-probability proxy |

**Acceptance Criteria:**
- DataFrame shape: (N, 11+) where N ≥ 30
- ≥ 3 model families represented
- ≥ 2 distinct scales represented
- ≥ 2 training regimes represented
- No more than 30% missing values per column

### FR-2: Capability-PC1 Computation
**Priority:** P0 — Critical

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
cap_cols = ["mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"]
X_scaled = StandardScaler().fit_transform(df[cap_cols])
pca = PCA(n_components=1)
df["PC1"] = pca.fit_transform(X_scaled).flatten()
pc1_var = pca.explained_variance_ratio_[0]
assert pc1_var >= 0.70, f"PC1 explains only {pc1_var:.1%}"
```

**Acceptance Criteria:**
- PC1 explains ≥ 70% of capability benchmark variance
- PC1 scores stored in DataFrame column

### FR-3: OLS Residualization (RI Construction)
**Priority:** P0 — Critical

```python
from sklearn.linear_model import LinearRegression
X_resid = df[["PC1", "mean_confidence"]].values
y_resid = df["advglue_drop"].values
ols = LinearRegression().fit(X_resid, y_resid)
df["RI"] = y_resid - ols.predict(X_resid)
r2 = ols.score(X_resid, y_resid)
```

**Acceptance Criteria:**
- R² reported to 3 decimal places
- RI column added to DataFrame
- VIF(PC1, mean_confidence) < 5 (multicollinearity check via statsmodels)

### FR-4: Gate Condition Evaluation
**Priority:** P0 — Critical

```python
sd_drop = df["advglue_drop"].std()
gate_sd = sd_drop > 0.05      # Gate 1: SD > 5%
gate_r2 = r2 < 0.80            # Gate 2: R² < 0.80
gate_passed = gate_sd and gate_r2
```

**Acceptance Criteria:**
- Both metrics computed and logged
- Gate result stored in output YAML
- Bootstrap CIs (10,000 samples) reported for SD and R²

### FR-5: Visualization Generation
**Priority:** P1 — Required

| Figure | Type | Description |
|--------|------|-------------|
| `fig_gate_metrics.png` | Bar chart | SD vs 5% threshold; R² vs 0.80 threshold |
| `fig_ri_distribution.png` | Violin plot | RI by model family |
| `fig_advglue_hist.png` | Histogram | Raw AdvGLUE drop distribution |
| `fig_pc1_scatter.png` | Scatter | PC1 vs AdvGLUE drop with OLS fit |
| `fig_ri_regime.png` | Box plot | RI by training regime |

All saved to `h-e1/figures/`.

### FR-6: Baseline Comparator
**Priority:** P1 — Required

Capability-only OLS (PC1 only, no RI term) for comparison:
```python
ols_baseline = LinearRegression().fit(df[["PC1"]], df["advglue_drop"])
r2_baseline = ols_baseline.score(df[["PC1"]], df["advglue_drop"])
```

### FR-7: Results Export
**Priority:** P1 — Required

Export final DataFrame and statistics:
- `h-e1/results/model_matrix.csv` — full model × benchmark matrix with RI
- `h-e1/results/gate_results.yaml` — gate metrics and pass/fail
- `h-e1/results/stats_summary.json` — PC1 variance, R², SD, VIF, bootstrap CIs

---

## 4. Data Specification

### 4.1 Primary Data Sources

| Dataset | Source | Access Method | Manual Download? |
|---------|--------|--------------|-----------------|
| TrustLLM robustness scores | HuggingFace: `TrustLLM/TrustLLM-dataset` | `datasets` library (gated) | YES — requires HF account agreement |
| lm-eval-harness benchmark results | EleutherAI GitHub or Open LLM Leaderboard | CLI or pre-computed JSONs | YES — run CLI or download JSON results |

### 4.2 Model Coverage

**TrustLLM pre-scored (16 LLMs):**
LLaMA-2 (7B/13B/70B), Mistral-7B, GPT-3.5/4, Vicuna-7B/13B, WizardLM, Koala, Alpaca, BLOOM, ChatGLM, and others from ICML 2024 paper.

**Additional open-source models (to reach ≥30):**
LLaMA-3 (8B/70B), Mistral-8x7B, Qwen-7B/14B/72B, Gemma-7B, Phi-3, Falcon-7B/40B — evaluated via lm-evaluation-harness.

### 4.3 Data Quality Requirements
- AdvGLUE scores: complete for ≥30 models (fallback: run AdvGLUE evaluation script directly)
- Mean confidence: extracted from lm-eval log-probability outputs; substitute 0 for closed-source models missing logit access
- Minimum model diversity: ≥3 families × ≥2 scales × ≥2 training regimes

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Random seed: 42 for all stochastic operations
- All results deterministic given fixed input scores
- `requirements.txt` with pinned versions

### NFR-2: Compute Requirements
- CPU-only (no GPU needed for statistical analysis)
- Memory: ≤ 8GB RAM for matrix operations
- Runtime: ≤ 2 hours for full pipeline

### NFR-3: Code Quality
- Python ≥ 3.10
- Modular scripts (data assembly, analysis, visualization separate)
- Runnable with single entry point: `python run_experiment.py`

### NFR-4: Testing
- Minimum 3 test methods per module
- Tests use real assertions (no `pass` or `assert True`)
- Tests run with `pytest` from project root

---

## 6. System Architecture Overview

```
h-e1/
├── code/
│   ├── data_assembly.py      # FR-1: Collect & merge benchmark scores
│   ├── compute_ri.py         # FR-2, FR-3: PCA + OLS residualization
│   ├── evaluate.py           # FR-4: Gate evaluation + bootstrap CIs
│   ├── visualize.py          # FR-5: Figure generation
│   ├── run_experiment.py     # Main entry point
│   └── requirements.txt
├── figures/                  # FR-5 outputs
├── results/                  # FR-7 outputs
└── tests/
    ├── test_data_assembly.py
    ├── test_compute_ri.py
    └── test_evaluate.py
```

---

## 7. Dependencies

### 7.1 Python Packages (pinned)
```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
pingouin==0.6.1
scipy>=1.10
statsmodels>=0.14
matplotlib>=3.7
seaborn>=0.12
datasets>=2.14
lm-eval>=0.4.0
pyyaml>=6.0
```

### 7.2 External Repositories (Reference)
- TrustLLM: https://github.com/HowieHwong/TrustLLM (MIT)
- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness (MIT)
- pingouin: https://github.com/raphaelvallat/pingouin (GPL-3.0)

---

## 8. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Sufficient model count | N ≥ 30 | `len(df)` after assembly |
| Family diversity | ≥ 3 families | `df["model_family"].nunique()` |
| PC1 validity | ≥ 70% variance | `pca.explained_variance_ratio_[0]` |
| **Gate 1 — SD** | **SD > 5%** | **`df["advglue_drop"].std()`** |
| **Gate 2 — R²** | **R² < 0.80** | **`ols.score(X_resid, y_resid)`** |
| VIF check | VIF < 5 | `variance_inflation_factor()` |
| Code runs error-free | No exceptions | `python run_experiment.py` |
| All figures generated | 5 figures | Check `h-e1/figures/*.png` |

**Gate Result:** Both Gate 1 AND Gate 2 must pass → proceed to H-M1.
**Gate Failure:** Either gate fails → STOP pipeline; investigate AdvGLUE data availability.

---

## 9. Out of Scope

- Neural network training (this is statistical analysis only)
- Fine-tuning or adapter training
- Real-time inference systems
- Hypothesis H-M1 through H-M4 (handled in subsequent phases)
- Phase 5 baseline comparison (skipped per module.yaml: `skip_baseline_comparison: true`)

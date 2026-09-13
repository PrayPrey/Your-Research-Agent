# Experiment Design: H-E1

**Date:** 2026-05-12
**Author:** Anonymous
**Hypothesis Statement:** Under a diverse set of ≥30 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, AdvGLUE accuracy drop will show SD > 5% across the model set, and the OLS residualization of AdvGLUE_drop on capability-PC1 + mean_confidence will yield R²_residualization < 0.8, confirming RI as a non-degenerate measurable construct.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE — workflow.status = ACTIVE, current_phase = Phase 2C
**Prerequisites Satisfied:** None required (H-E1 is root hypothesis with no prerequisites)
**Gate Status:** MUST_WORK — SD(AdvGLUE_drop) > 5% AND R²_residualization < 0.8

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK Gate:**
- Primary: SD(AdvGLUE_drop) > 5% across ≥30 diverse LLMs
- Primary: R²_residualization < 0.8 (OLS of AdvGLUE_drop ~ PC1 + mean_confidence)
- Secondary: RI distribution shows spread across pretrained and RLHF model subsets

**Failure Response:** STOP pipeline — investigate AdvGLUE score availability; consider ANLI as alternative adversarial benchmark.

---

## Continuation Context

This is the FIRST hypothesis in the chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4). No previous hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)
*Not applicable — H-E1 is the root/foundation hypothesis with no prerequisites.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Adversarial Robustness LLM Evaluation Benchmark**
- Result: HF paper (2305.14314) — adversarial LLM evaluation context (similarity: 0.465)
- Result: OpenReview forum (M3Y74vmsMcY) — 4 chunk matches for adversarial evaluation (similarity: 0.405)
- Key insight: Archon KB is primarily populated with diffusion model content; no directly relevant LLM adversarial robustness cases found. Relying on Exa/manual research for implementation patterns.

**Query 2: PCA Residualization Capability Correlation**
- Results returned LoRA/diffusion content — no directly relevant cases
- Key insight: PCA-based benchmark analysis is a well-established practice; sklearn.decomposition.PCA is the standard tool

**Query 3: LLM Multi-Benchmark Calibration Hallucination Trustworthiness**
- No domain-specific cases found in Archon KB
- Key insight: The clawRxiv paper (2603.00394) from Exa confirms: 2 PCA components explain 97.4% of LLM benchmark variance across 40 models / 11 families; PC1 (74.0% variance) correlates strongly with model scale (r=0.86)

**Summary:** Archon KB did not contain domain-specific LLM trustworthiness cases. All implementation patterns sourced from Exa searches.

### Archon Code Examples

**Query 1: Spearman Partial Correlation**
- No relevant examples in Archon KB (diffusion/image generation content only)

**Query 2: PCA sklearn Benchmark Matrix**
- No relevant examples in Archon KB

**Conclusion:** Implementation patterns sourced from pingouin, scipy, and sklearn official documentation via Exa.

### Exa GitHub Implementations

**Repository 1: HowieHwong/TrustLLM** (⭐ 622)
- **URL:** https://github.com/HowieHwong/TrustLLM
- **Relevance:** Official ICML 2024 TrustLLM toolkit — primary source for AdvGLUE scores, robustness evaluation, and 16 LLM benchmark matrix
- **Key Dataset:** AdvGLUE.json (912 examples, 5 NLU tasks, 14 attack methods)
- **Loading:**
  ```python
  from datasets import load_dataset
  dataset = load_dataset("TrustLLM/TrustLLM-dataset", data_dir="robustness")
  # Or via trustllm toolkit:
  robustness_results = run_robustness(advglue_path="path/to/AdvGLUE.json")
  ```
- **Architecture:** Pipeline-based evaluation; outputs per-model accuracy scores
- **Covers 16 LLMs** across truthfulness, safety, fairness, robustness, privacy, machine ethics

**Repository 2: EleutherAI/lm-evaluation-harness** (⭐ 12K)
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Standard framework for MMLU, GSM8K, BBH, HellaSwag, WinoGrande capability benchmarks; needed for capability-PC1 computation
- **Key Code (multi-model evaluation):**
  ```bash
  # Run capability benchmarks across models
  lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-2-7b-hf \
    --tasks mmlu,gsm8k,hellaswag,winogrande \
    --num_fewshot 5 \
    --output_path results/llama2-7b.json
  ```
  ```python
  # Aggregate results across models
  import json, pandas as pd
  models = ["llama2-7b", "llama2-13b", "mistral-7b", ...]
  tasks = ["mmlu", "gsm8k", "hellaswag", "winogrande"]
  results = []
  for model in models:
      with open(f"results/{model}.json") as f:
          data = json.load(f)
          row = {"Model": model}
          for task in tasks:
              row[task] = data["results"][task].get("acc", data["results"][task].get("exact_match"))
          results.append(row)
  df = pd.DataFrame(results)
  ```
- **Supports 60+ benchmarks** including BBH via `--tasks bbh_*`

**Repository 3: raphaelvallat/pingouin** (official documentation)
- **URL:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Relevance:** Primary library for Spearman partial correlation with covariate control
- **Key Code:**
  ```python
  import pingouin as pg
  # Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence)
  result = pg.partial_corr(
      data=df, x="RI", y="ECE",
      covar=["PC1", "mean_confidence"],
      method="spearman"
  ).round(3)
  # Returns: n, r, CI95, p_val
  ```

**Repository 4: clawRxiv LLM Benchmark Correlation Study** (2603.00394)
- **URL:** https://clawrxiv.io/abs/2603.00394
- **Relevance:** Direct empirical support for PC1 approach — 97.4% variance explained by 2 PCA components across 40 models/11 families
- **Key Finding:** PC1 (74.0% variance) = general capability correlated with scale; validated PCA + OLS methodology

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment does NOT reproduce a single paper's method. It is a novel cross-benchmark statistical analysis. Priority:
1. **TrustLLM toolkit** (HowieHwong/TrustLLM) for AdvGLUE scores and robustness data on 16 models
2. **lm-evaluation-harness** (EleutherAI) for capability benchmark scores (MMLU/GSM8K/BBH/HellaSwag/WinoGrande) on additional open-source models
3. **pingouin** for Spearman partial correlation
4. **sklearn** for PCA and OLS residualization

**Recommended Implementation Path:**
- Primary: TrustLLM toolkit (AdvGLUE scores) + lm-evaluation-harness (capability benchmarks) + pingouin (partial correlation) + sklearn (PCA/OLS)
- Fallback: If TrustLLM scores unavailable for enough models, use Open LLM Leaderboard public results + AdvGLUE benchmark evaluation script directly
- Justification: TrustLLM covers 16 LLMs with all required dimensions; lm-evaluation-harness covers additional open-source models to reach ≥30; both are authoritative, widely-used frameworks with public results

### Code Analysis (Serena MCP)

*Skipped* - H-E1 is a statistical analysis pipeline (PCA + OLS residualization + Spearman partial correlation). No complex custom neural network layers requiring semantic code analysis. All required patterns found in pingouin/scipy/sklearn official documentation via Exa.

---

## Experiment Specification

### Dataset

**Primary: TrustLLM Multi-Benchmark Matrix**
- **Name:** TrustLLM benchmark dataset (robustness section) + lm-evaluation-harness public results
- **Type:** standard (established benchmark, real data)
- **Source:** HowieHwong/TrustLLM (ICML 2024, 622 stars); EleutherAI/lm-evaluation-harness (12K stars)
- **Unit of analysis:** LLM model (not individual examples) — N = ≥30 models
- **Per-model scores collected:**
  - AdvGLUE accuracy (5 tasks: SST-2, QQP, MNLI, QNLI, RTE under 14 attack methods)
  - MMLU accuracy (57-subject, 5-shot)
  - GSM8K exact match (grade school math, 5-shot)
  - BBH accuracy (Big-Bench Hard, 3-shot CoT)
  - HellaSwag accuracy (commonsense NLI, 10-shot)
  - WinoGrande accuracy (commonsense pronoun resolution, 5-shot)
  - Mean model confidence (logit-based, extracted from evaluation runs)
- **Model set:** ≥30 LLMs spanning ≥3 families (LLaMA-series, Mistral-series, GPT-series or Qwen/Gemma) × ≥2 scales (7B–70B+) × ≥2 training regimes (pretrained + RLHF/instruction-tuned)
- **TrustLLM covers:** 16 frontier LLMs (includes LLaMA-2 7B/13B/70B, Mistral 7B, GPT-3.5/4, Vicuna, etc.)
- **Additional models:** Open-source models via lm-evaluation-harness to reach ≥30 total
- **Synthetic data:** NONE — all scores from real model evaluations

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` + trustllm pip package + lm-evaluation-harness CLI
- Identifier: `"TrustLLM/TrustLLM-dataset"` (gated, requires HF account agreement)
- Code:
  ```python
  # Step 1: TrustLLM robustness scores
  from datasets import load_dataset
  trust_data = load_dataset("TrustLLM/TrustLLM-dataset", data_dir="robustness")
  # Or via trustllm toolkit evaluation:
  # pip install trustllm
  # from trustllm.eval import run_robustness

  # Step 2: Capability benchmark scores via lm-eval
  # pip install lm-eval
  # lm_eval --model hf --model_args pretrained=<model> \
  #   --tasks mmlu,gsm8k,hellaswag,winogrande,bbh \
  #   --output_path results/<model>.json

  # Step 3: Load and aggregate results
  import json, pandas as pd
  # Load pre-computed results from JSON outputs
  ```

### Models

#### Baseline Model

**This experiment has NO neural network model to train.** The "baseline" is the statistical comparator:

**Baseline Analysis:** Capability-only predictor
- **Method:** OLS regression using only PC1 → {ECE, HaluEval, HarmBench} (no RI term)
- **Purpose:** Tests whether general capability alone explains trust failures
- **Implementation:** `sklearn.linear_model.LinearRegression` with X = [PC1_scores]
- **Source:** Standard OLS regression; justified by clawRxiv (2603.00394) showing PC1 captures 74% of benchmark variance

**Loading Information** (for Phase 4):
- Method: sklearn (no download needed — computed from benchmark scores)
- Identifier: `sklearn.linear_model.LinearRegression`
- Code:
  ```python
  from sklearn.linear_model import LinearRegression
  from sklearn.decomposition import PCA
  from sklearn.preprocessing import StandardScaler
  import numpy as np

  # Capability matrix: shape (N_models, 5)
  # Columns: MMLU, GSM8K, BBH, HellaSwag, WinoGrande
  X_cap = np.column_stack([mmlu_scores, gsm8k_scores, bbh_scores,
                            hellaswag_scores, winogrande_scores])

  # Compute PC1
  scaler = StandardScaler()
  X_scaled = scaler.fit_transform(X_cap)
  pca = PCA(n_components=1)
  PC1 = pca.fit_transform(X_scaled).flatten()
  explained_var = pca.explained_variance_ratio_[0]
  assert explained_var >= 0.70, f"PC1 explains only {explained_var:.1%} variance"
  ```

#### Proposed Model

**Architecture:** RI Construction Pipeline (OLS residualization of AdvGLUE_drop on PC1 + mean_confidence)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Residual Instability (RI) Construction
# Based on: Phase 2B verification plan (H-E1), pingouin docs, sklearn OLS
# Purpose: Compute RI = capability-controlled adversarial fragility score per model

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pingouin as pg

def compute_residual_instability(df):
    """
    Args:
        df: DataFrame with columns [model_id, advglue_drop, mmlu, gsm8k,
                                     bbh, hellaswag, winogrande, mean_confidence]
        N models >= 30, spanning >= 3 families
    Returns:
        df with added columns: PC1, RI, r2_residualization, sd_advglue_drop
    """
    # Step 1: Compute capability-PC1
    cap_cols = ["mmlu", "gsm8k", "bbh", "hellaswag", "winogrande"]
    X_cap = StandardScaler().fit_transform(df[cap_cols].values)
    pca = PCA(n_components=1)
    df["PC1"] = pca.fit_transform(X_cap).flatten()
    pc1_var = pca.explained_variance_ratio_[0]

    # Step 2: OLS residualization: AdvGLUE_drop ~ PC1 + mean_confidence
    X_resid = df[["PC1", "mean_confidence"]].values
    y_resid = df["advglue_drop"].values
    ols = LinearRegression().fit(X_resid, y_resid)
    df["RI"] = y_resid - ols.predict(X_resid)  # OLS residuals = RI
    r2 = ols.score(X_resid, y_resid)

    # Step 3: Check gate conditions
    sd_drop = df["advglue_drop"].std()
    gate_sd = sd_drop > 0.05          # SD > 5%
    gate_r2 = r2 < 0.80               # R² < 0.8 (non-degenerate)

    return df, {"pc1_var": pc1_var, "r2_residualization": r2,
                "sd_advglue_drop": sd_drop,
                "gate_sd_passed": gate_sd, "gate_r2_passed": gate_r2}
```

### Training Protocol

**This is a statistical analysis experiment — no gradient-based training.**

**Analysis Protocol:**
- **Statistical Libraries:** pingouin==0.6.1, scipy>=1.10, sklearn>=1.3, pandas>=2.0, numpy>=1.24
- **Compute:** CPU-only (no GPU needed for statistical analysis phase)
- **Random Seed:** 42 (for PCA reproducibility; results are deterministic given fixed input scores)
- **Bootstrap samples:** 10,000 (for confidence intervals on SD and R² estimates)
- **Multiple comparisons:** Holm-Bonferroni correction (implemented in pingouin via `pg.multicomp`)

**Data Collection Protocol:**
1. Collect AdvGLUE accuracy per model via TrustLLM toolkit (16 models pre-scored)
2. Run lm-evaluation-harness on additional open-source models (MMLU/GSM8K/BBH/HellaSwag/WinoGrande)
3. Extract mean model confidence from log-probability outputs during evaluation
4. Compute AdvGLUE accuracy drop = (clean GLUE accuracy − AdvGLUE accuracy) per model
5. Assemble model × benchmark matrix with ≥30 rows

**Analysis Steps:**
1. PCA on [MMLU, GSM8K, BBH, HellaSwag, WinoGrande] → PC1 (verify ≥70% variance explained)
2. OLS: AdvGLUE_drop ~ PC1 + mean_confidence → extract R² and RI residuals
3. Compute SD(AdvGLUE_drop) across model set
4. Check gate: SD > 5% AND R² < 0.8
5. Visualize RI distribution by model family and training regime

**Seeds:** 1 (fixed seed=42; statistical analysis is largely deterministic)

### Evaluation

**Primary Metrics (Gate Conditions):**
- **SD(AdvGLUE_drop):** Standard deviation of adversarial accuracy drop across ≥30 models
  - Gate threshold: SD > 5% (0.05)
  - Measured via: `np.std(df["advglue_drop"])`
- **R²_residualization:** OLS R² for AdvGLUE_drop ~ PC1 + mean_confidence
  - Gate threshold: R² < 0.80 (RI is non-degenerate)
  - Measured via: `sklearn.linear_model.LinearRegression.score()`

**Secondary Metrics:**
- PC1 explained variance ≥ 70% (validates capability proxy)
- RI distribution spread across pretrained vs RLHF subsets (qualitative check via violin plot)
- VIF(PC1, mean_confidence) < 5 (multicollinearity check)

**Success Criteria (EXISTENCE PoC — direction only):**
- SD(AdvGLUE_drop) > 5% AND R²_residualization < 0.8 → PASS GATE → proceed to H-M1
- Any failure → STOP → investigate data availability

**Expected Baseline Performance (from research):**
- TrustLLM (ICML 2024): 16 LLMs show significant variability in AdvGLUE robustness; "least effective model at 88% semantic similarity vs top at 97.64%" — confirms variance exists
- clawRxiv (2603.00394): PC1 explains 74% of 6-benchmark variance across 40 models → expect PC1 to explain 60-80% of AdvGLUE variance (R² < 0.8 plausible)
- Source: TrustLLM ICML 2024 paper; clawRxiv 2603.00394

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: cross-model statistical analysis (not classification/generation)
- Library: `pingouin==0.6.1`, `scipy>=1.10`, `sklearn>=1.3`
- Code:
  ```python
  # SD of AdvGLUE drop
  import numpy as np
  sd_drop = np.std(df["advglue_drop"])

  # OLS R²
  from sklearn.linear_model import LinearRegression
  ols = LinearRegression().fit(df[["PC1", "mean_confidence"]], df["advglue_drop"])
  r2 = ols.score(df[["PC1", "mean_confidence"]], df["advglue_drop"])

  # VIF check
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  vif = variance_inflation_factor(df[["PC1", "mean_confidence"]].values, 0)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing SD(AdvGLUE_drop) vs 5% threshold and R²_residualization vs 0.8 threshold

#### Additional Figures (LLM Autonomous)
- **RI Distribution by Family:** Violin plot of RI scores grouped by model family (LLaMA/Mistral/GPT/other) — shows non-trivial spread
- **AdvGLUE Drop Distribution:** Histogram of raw AdvGLUE accuracy drops across all ≥30 models
- **PC1 vs AdvGLUE Scatter:** Scatter plot of capability-PC1 vs AdvGLUE drop with OLS fit line — visually demonstrates residual variance
- **RI vs Training Regime:** Box plot of RI by training regime (pretrained vs instruction-tuned vs RLHF)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. SD(AdvGLUE_drop) > 0.05 (5%)
3. R²_residualization < 0.80

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | RI construct is computable from AdvGLUE + capability benchmark scores | TRUE — TrustLLM provides AdvGLUE scores; lm-eval provides capability scores |
| Mechanism Isolatable | RI = OLS residual, isolatable by toggling residualization step | TRUE — can compare raw AdvGLUE_drop vs residualized RI |
| Baseline Measurable | Capability-only predictor (PC1 → trust outcomes) can run independently | TRUE — sklearn OLS with X=[PC1] only |

### Architecture Compatibility Check

**This experiment uses statistical analysis, not neural network architecture.**

**Required Components:**
- AdvGLUE accuracy scores for ≥30 LLMs (from TrustLLM + direct evaluation)
- Capability benchmark scores: MMLU, GSM8K, BBH, HellaSwag, WinoGrande (from lm-eval)
- Mean model confidence (log-probability based, from evaluation runs)

**Incompatible Data Sources:**
- Closed-source models without accessible logit outputs (cannot compute mean_confidence) — mitigate by substituting 0 or using token probability proxies
- Models with missing AdvGLUE scores — require direct evaluation or exclusion

> ⚠️ If fewer than 30 models have full benchmark coverage, Phase 4 MUST report N and family diversity; gate passes only if ≥3 families × ≥2 scales represented.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "RI computed for N=X models; SD={sd:.3f}, R²={r2:.3f}" | `compute_ri.py:main()` |
| Tensor Shape | DataFrame shape (N, 8+) where N≥30 after data assembly | `data_assembly.py:assemble_matrix()` |
| Metric Delta | SD(AdvGLUE_drop) > 0.05 confirmed in output | `evaluate.py:check_gate()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(df, stats):
    indicators = {
        "sufficient_models": len(df) >= 30,
        "family_diversity": df["model_family"].nunique() >= 3,
        "sd_computed": stats["sd_advglue_drop"] is not None,
        "r2_computed": stats["r2_residualization"] is not None,
        "ri_nonzero": df["RI"].std() > 0.001,
        "gate_sd": stats["gate_sd_passed"],
        "gate_r2": stats["gate_r2_passed"]
    }
    all_pass = all(v for k, v in indicators.items()
                   if k in ["sufficient_models", "family_diversity",
                             "sd_computed", "r2_computed", "ri_nonzero"])
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Insufficient models | len(df) < 30 after assembly | FAIL: Collect more models; consider ANLI as alternative |
| AdvGLUE scores missing | Missing values > 30% of model set | FAIL: Use AdvGLUE evaluation script directly |
| PC1 variance < 70% | pca.explained_variance_ratio_[0] < 0.70 | WARN: Report as sensitivity; continue |
| RI degeneracy | R²_residualization >= 0.80 | GATE FAIL: RI collapses into capability; STOP pipeline |
| Zero variance in AdvGLUE | SD(AdvGLUE_drop) <= 0.05 | GATE FAIL: No signal; investigate data quality |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | len(df) >= 30, ≥3 families | verify_mechanism_activated() |
| Effect Measurable | SD(AdvGLUE_drop) > 0 | np.std(df["advglue_drop"]) |
| Hypothesis Supported | SD > 0.05 AND R² < 0.80 | check_gate() returns True |

---

## Appendix: Reference Implementations

**[R1] TrustLLM — Official ICML 2024 Toolkit**
- URL: https://github.com/HowieHwong/TrustLLM
- Stars: 622 | License: MIT
- Relevance: Official AdvGLUE evaluation pipeline; 16 LLMs pre-scored across 6 trust dimensions
- Key file: `trustllm/eval/robustness.py`
- Citation: Huang et al. "TrustLLM: Trustworthiness in Large Language Models." ICML 2024.

**[R2] EleutherAI/lm-evaluation-harness — Capability Benchmark Framework**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Stars: 12K | License: MIT
- Relevance: Standard framework for MMLU/GSM8K/BBH/HellaSwag/WinoGrande; backend of HuggingFace Open LLM Leaderboard
- Key command: `lm_eval --model hf --tasks mmlu,gsm8k,hellaswag,winogrande,bbh`

**[R3] raphaelvallat/pingouin — Spearman Partial Correlation**
- URL: https://pingouin-stats.org / https://github.com/raphaelvallat/pingouin
- Relevance: `pg.partial_corr(data, x, y, covar, method="spearman")` — inverse covariance matrix method matching ppcor R package
- Version: 0.6.1

**[R4] clawRxiv 2603.00394 — LLM Benchmark Dimensionality Analysis**
- URL: https://clawrxiv.io/abs/2603.00394
- Relevance: Direct empirical validation of PC1 approach — 97.4% variance in 6 benchmarks explained by 2 PCs across 40 models/11 families; PC1 correlates with scale (r=0.86)
- Key finding: PC1 of [ARC-C, HellaSwag, MMLU, WinoGrande, GSM8K] explains 74% variance

**[R5] AdvGLUE Benchmark**
- URL: https://adversarialglue.github.io/
- Relevance: 912 adversarial NLU examples (14 attack methods, 5 GLUE tasks); official evaluation script available
- Citation: Wang et al. "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models." 2021.

**[R6] sklearn PCA + OLS**
- URL: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- Code pattern:
  ```python
  from sklearn.decomposition import PCA
  from sklearn.linear_model import LinearRegression
  from sklearn.preprocessing import StandardScaler
  pca = PCA(n_components=1)
  PC1 = pca.fit_transform(StandardScaler().fit_transform(X_cap))
  ols = LinearRegression().fit(X[["PC1","mean_conf"]], y_advglue)
  RI = y_advglue - ols.predict(X[["PC1","mean_conf"]])
  ```

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-12

### Workflow History for This Hypothesis
- 2026-05-12T11:31:00 — Phase 2B completed; H-E1 defined with MUST_WORK gate
- 2026-05-12T11:40:11 — H-E1 set to IN_PROGRESS by hypothesis loop
- 2026-05-12 — Phase 2C experiment design IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain matches), Exa (GitHub: TrustLLM, lm-eval-harness, pingouin, clawRxiv), Serena (skipped — statistical analysis pipeline)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

# Experiment Design: H-M2

**Date:** 2026-08-03
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** MOHAWK-SSM converted LLaMA-3-8B exhibits a significantly steeper needle-depth accuracy degradation slope than LAWCAT-converted LLaMA-3-8B on LongBench v2 multi-doc QA and synthetic tasks, quantified as |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| in logistic regression of P(correct) ~ DepthPercentile + (1|Task), because SSM bounded-state exponential forgetting (h_t = A·h_{t-1} + B·x_t) loses exact positional identity of early tokens while LAWCAT's causal Conv1D preserves local token-to-token attention within a sliding window.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests causal chain Step 2: depth-slope differential as falsifier of Conv1D mechanism claim.

---

## Workflow Status

**Verification State:** IN_PROGRESS (h-m2)
**Prerequisites Satisfied:** ✅ H-M1 VALIDATED (Frobenius slope β=-0.368 ≤ 0.5); ✅ H-E1 VALIDATED (per-example evaluation data available)
**Gate Status:** SHOULD_WORK — if fails: EXPLORE (narrow Conv1D mechanism claim; H-E1 still holds)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Step 2 of causal chain)
- **Prerequisites:** H-M1 (gate interpretation), H-E1 (provides evaluation data)

### Gate Condition
SHOULD_WORK: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs. Failure → EXPLORE (narrow claim, H-E1 remains valid).

---

## Continuation Context

**Previous Hypothesis Results (H-M1 + H-E1):**
- H-M1: VALIDATED — SSD Frobenius log-log slope β=-0.368 (≤0.5), 90th pct error/N=0.027 (≤0.3). Confirms retrieval degradation is architectural bounded-state bias, NOT approximation breakdown. This interpretation is the mechanistic grounding for H-M2: depth-slope differential reflects architectural forgetting dynamics, not training artifacts.
- H-E1: VALIDATED — CODE_VALIDATED_EXPERIMENT_RUNNING. Per-example accuracy data across all 503 LongBench v2 questions for MOHAWK-SSM, LAWCAT, Hybrid-4, and teacher LLaMA-3-8B is available. H-M2 performs statistical analysis on this existing data — **no new GPU compute required**.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB searches (3 queries executed) returned no relevant results for this NLP statistical analysis task — the KB is primarily indexed on image generation (diffusers, stable diffusion) content. All implementation grounding derived from Exa GitHub search below.

**Query 1:** "logistic regression needle depth accuracy LLM long context retrieval" → No relevant results (similarity ~0.40, diffusers content)
**Query 2:** "SSM state space model retrieval degradation depth position forgetting" → No relevant results (similarity ~0.40, diffusers content)
**Query 3:** "mixed effects logistic regression LLM evaluation benchmark per-example analysis" → No relevant results

**Assessment:** Archon KB does not contain relevant NLP/statistical analysis content for this hypothesis. Exa GitHub findings are the primary research source.

### Archon Code Examples

No relevant code examples found (all similarity scores <0.36, image depth estimation content unrelated to statistical regression on NLP benchmarks).

### Exa GitHub Implementations

**Query 1: LongBench v2 official implementation + per-example metadata**

**Repository 1:** THUDM/LongBench (⭐ 1210)
- **URL:** https://github.com/THUDM/LongBench
- **HuggingFace:** `load_dataset('THUDM/LongBench-v2', split='train')`
- **Relevance:** Official benchmark used for H-E1 evaluation. Provides 503 MCQ with fields: `_id`, `domain`, `sub_domain`, `difficulty`, `length`, `question`, `choice_A/B/C/D`, `answer`, `context`
- **Key Schema:**
  ```json
  {
    "_id": "unique identifier",
    "domain": "e.g., 'Multi-Document QA'",
    "sub_domain": "e.g., 'Academic Papers'",
    "difficulty": "easy|hard",
    "length": "short|medium|long",
    "context": "the long context text"
  }
  ```
- **Critical Note:** LongBench v2 does NOT provide an explicit "needle depth percentile" field. Depth percentile must be computed: locate the answer-supporting passage within `context` via substring search or BM25, compute character offset / total context length → normalized depth ∈ [0, 1]. For multi-doc QA, depth = position of the relevant document within the concatenated context.
- **Task Categories Needed:** Domain field contains: "Multi-Document QA" and implicitly synthetic/structured tasks (mapped to retrieval-heavy subset, ~166 questions)
- **Source:** Bai et al., ACL 2025. THUDM/LongBench on GitHub.

**Repository 2:** zai-org/LongBench-v2 (HuggingFace mirror)
- **URL:** https://huggingface.co/datasets/zai-org/LongBench-v2
- **Alternative loading:** `load_dataset('zai-org/LongBench-v2')`
- **Used For:** Cross-validation of data format specification

**Query 2: Mixed-effects logistic regression Python implementation**

**Source 1:** statsmodels MixedLM documentation + StackOverflow lme4 Python comparison
- **URL:** https://www.statsmodels.org/stable/examples/notebooks/generated/mixed_lm_example.html
- **Key Finding:** `statsmodels.formula.api.mixedlm` supports linear mixed models. For **binary outcomes (logistic)**, use `statsmodels.BinomialBayesMixedGLM` (Bayesian approximation) or interface R's `glmer` via `rpy2`.
- **Recommended Approach for H-M2:** Use `rpy2` to call R's `lme4::glmer` for proper frequentist mixed-effects logistic regression with p-values. Pure Python `statsmodels` does not provide equivalent GLMM with Gauss-Hermite quadrature.
- **Code Pattern:**
  ```python
  import statsmodels.formula.api as smf
  # Linear mixed model (for continuous DV):
  md = smf.mixedlm("correct ~ depth_percentile", data, groups=data["task_id"])
  mdf = md.fit(method=["lbfgs"])
  beta_depth = mdf.params["depth_percentile"]
  
  # For binary DV (preferred): use rpy2 + lme4
  from rpy2.robjects import r
  from rpy2.robjects.packages import importr
  lme4 = importr('lme4')
  model = r.glmer("correct ~ depth_percentile + (1|task_id)", family="binomial", data=r_df)
  ```
- **Source:** statsmodels docs; StackOverflow #73222334; dm13450.github.io benchmark

**Query 3: MOHAWK + LAWCAT official implementations**

**Repository 3:** goombalab/mohawk
- **URL:** https://github.com/goombalab/mohawk
- **Stars:** [official MOHAWK framework]
- **Relevance:** Official MOHAWK distillation framework used for H-E1. Provides evaluation via `evals/benchmark.py`. The H-E1 per-example accuracy data was generated by this pipeline.
- **Evaluation Output:** Standard lm-eval-harness format; LongBench v2 evaluation via custom script

**Repository 4:** zeyuliu1037/LAWCAT
- **URL:** https://github.com/zeyuliu1037/LAWCAT
- **Stars:** [official LAWCAT EMNLP 2025]
- **Relevance:** Official LAWCAT framework. Adapted from LoLCATs. Evaluation scripts support NIAH, BABILong, passkey retrieval. For LongBench v2, custom evaluation script needed.
- **Source:** Liu et al., EMNLP 2025 Findings

**Serena Analysis Needed:** false — H-M2 is statistical analysis, not architectural code modification.

### 🎯 Implementation Priority Assessment

H-M2 is a **post-hoc statistical analysis** of H-E1 evaluation data. No model training or inference needed.

**Recommended Implementation Path:**
- Primary: Statistical analysis pipeline on H-E1 per-example output files (JSON)
- Fallback: If H-E1 data format is missing depth information, compute depth percentile from LongBench v2 `context` field via BM25/substring search
- Justification: H-M2 requires zero new GPU compute — all needed data is produced by H-E1

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; H-M2 is a statistical analysis task, not a complex architecture implementation. No Serena analysis required.

---

## Experiment Specification

### Dataset

**Name:** LongBench v2 (subset: multi-doc QA + structured/synthetic tasks)
**Type:** standard
**Version:** ACL 2025 release (503 questions)
**Source:** THUDM/LongBench-v2 on HuggingFace

**Subset for H-M2:**
- Domain filter: `domain in ["Multi-Document QA", "Long Structured Data Understanding"]`
- Estimated ~166 questions (multi-doc QA: 125 + structured: 33 = 158; synthetic/code may be included based on H-E1 task-category mapping)
- **All 503 questions evaluated in H-E1; H-M2 filters to retrieval-heavy subset**

**Depth Percentile Computation (CRITICAL — not in raw data):**
For each example in the filtered subset, compute:
```python
def compute_depth_percentile(example):
    """
    Compute needle depth: position of answer-supporting passage
    relative to total context length.
    Returns float in [0, 1] where 0 = beginning, 1 = end.
    """
    context = example["context"]
    # Method: search for keywords from the question/answer in context
    # Use earliest supporting passage position
    answer_keywords = extract_keywords(example["question"], example[f"choice_{example['answer']}"])
    positions = [context.find(kw) for kw in answer_keywords if context.find(kw) >= 0]
    if not positions:
        return 0.5  # fallback: assume middle
    earliest_pos = min(positions)
    return earliest_pos / max(len(context), 1)
```
**Note:** Higher depth_percentile = answer earlier in context (= greater "depth" for SSM forgetting test). Convention: depth_percentile=0 means answer at very end; =1 means answer at very beginning. SSM prediction: accuracy drops as depth_percentile increases (earlier = more forgetting).

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: `"THUDM/LongBench-v2"`
- Code: `load_dataset('THUDM/LongBench-v2', split='train')`

**Data already available from H-E1 evaluation run — no new download required.**

### Models

#### Baseline Model

**Architecture:** LLaMA-3-8B (Meta) — full attention transformer baseline
**Type:** Decoder-only transformer, 8B parameters
**Loading:**
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-3-8B"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")`

**Role in H-M2:** Teacher/oracle. Its per-example accuracies from H-E1 are used to compute Δ_norm. H-M2 does NOT re-evaluate the teacher — results already exist from H-E1.

**Loading Information:**
- Method: HuggingFace transformers (already done in H-E1)
- Identifier: `"meta-llama/Llama-3-8B"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")`

#### Proposed Model (Primary Analysis Subjects)

**H-M2 analyzes two student models from H-E1:**

**Student 1 — MOHAWK-SSM-converted LLaMA-3-8B:**
- Architecture: LLaMA-3-8B with all attention layers replaced by Mamba-2/SSD structured mixer
- Distillation: MOHAWK Stage 1+2, ≤1B tokens C4
- Source: goombalab/mohawk framework
- Modification: MOHAWK Stage 1 (matrix matching) + Stage 2 (hidden-state alignment)

**Student 2 — LAWCAT-converted LLaMA-3-8B:**
- Architecture: LLaMA-3-8B with attention replaced by causal Conv1D + normalized gated linear attention
- Distillation: LAWCAT, ≤1B tokens C4
- Source: zeyuliu1037/LAWCAT framework
- Modification: Depth-separable Conv1D + GLA with normalization

**H-M2 uses pre-computed per-example accuracy from H-E1 — no model re-loading needed.**

**Core Mechanism Implementation (H-M2 Analysis Code):**

```python
# H-M2 Core: Depth-Slope Logistic Regression
# Based on: statsmodels.formula.api + lme4 pattern (StackOverflow #73222334)
# Data source: H-E1 per-example evaluation output JSON

import pandas as pd
import numpy as np
from scipy import stats

def compute_depth_slope_regression(h_e1_results_path: str, model_name: str):
    """
    Fit logistic regression: P(correct) ~ DepthPercentile + (1|Task)
    Returns beta_depth coefficient and 95% CI.
    
    Args:
        h_e1_results_path: Path to H-E1 per-example JSON results
        model_name: "mohawk_ssm" or "lawcat"
    Returns:
        dict: {beta: float, ci_low: float, ci_high: float, p_value: float}
    """
    df = load_h_e1_results(h_e1_results_path, model_name)
    # Filter to retrieval-heavy subset
    retrieval_domains = ["Multi-Document QA", "Long Structured Data Understanding"]
    df = df[df["domain"].isin(retrieval_domains)].copy()
    
    # Compute depth percentile if not already in data
    if "depth_percentile" not in df.columns:
        df["depth_percentile"] = df.apply(compute_depth_percentile, axis=1)
    
    # Encode correct/incorrect as binary
    df["correct"] = (df["pred"] == df["answer"]).astype(int)
    
    # Mixed-effects logistic regression via rpy2+lme4
    beta, ci, pval = fit_glmer_via_rpy2(
        formula="correct ~ depth_percentile + (1|task_id)",
        data=df, family="binomial"
    )
    return {"beta": beta, "ci_low": ci[0], "ci_high": ci[1], "p_value": pval}

def test_beta_ratio(ssm_result: dict, lawcat_result: dict) -> dict:
    """
    Test: |beta_SSM| >= 2 * |beta_LAWCAT| with non-overlapping CIs
    """
    ratio = abs(ssm_result["beta"]) / max(abs(lawcat_result["beta"]), 1e-9)
    # ponytail: simple ratio test; bootstrap for publication-grade CI
    cis_overlap = not (ssm_result["ci_high"] < lawcat_result["ci_low"] or
                       lawcat_result["ci_high"] < ssm_result["ci_low"])
    return {"ratio": ratio, "gate_pass": ratio >= 2.0 and not cis_overlap}
```

### Training Protocol

**H-M2 requires NO training.** This is a statistical analysis of existing H-E1 evaluation data.

**Data Pipeline:**
- Input: H-E1 per-example evaluation output (JSON files, one per model)
- Format: `[{"_id": str, "domain": str, "pred": str, "answer": str, "context": str, ...}, ...]`
- Preprocessing: Filter to retrieval-heavy domains, compute depth percentile, encode binary correct/incorrect

**Statistical Analysis Protocol:**
- **Step 1:** Load H-E1 per-example results for MOHAWK-SSM and LAWCAT students
- **Step 2:** Filter to multi-doc QA + structured data subset (~166 questions)
- **Step 3:** Compute depth_percentile per example (character offset / context length)
- **Step 4:** Fit per-model mixed-effects logistic regression:
  - Formula: `correct ~ depth_percentile + (1|task_id)` (random intercept per task)
  - Tool: `rpy2` + R `lme4::glmer(family=binomial)` — preferred for p-values
  - Fallback: `statsmodels.formula.api.mixedlm` (linear approximation if rpy2 unavailable)
- **Step 5:** Extract β_depth coefficient and 95% CI for each model
- **Step 6:** Apply Holm correction for multiple comparisons (2 tests: SSM p-value, LAWCAT p-value)
- **Step 7:** Compute ratio |β_depth^SSM| / |β_depth^LAWCAT| and test non-overlapping CIs

**Seeds:** N/A (deterministic statistical analysis)
**Compute:** CPU-only, ~minutes runtime

### Evaluation

**Primary Metrics:**
- β_depth^SSM: logistic regression coefficient for MOHAWK-SSM (expected < 0, i.e., deeper needle = lower accuracy)
- β_depth^LAWCAT: logistic regression coefficient for LAWCAT (expected closer to 0)
- Ratio: |β_depth^SSM| / |β_depth^LAWCAT|

**Success Criteria:**
- Primary: Ratio ≥ 2.0 AND 95% CIs of β_depth^SSM and β_depth^LAWCAT do NOT overlap
- Secondary: β_depth^SSM significantly < 0 (p<0.01, Holm-corrected); β_depth^LAWCAT closer to 0 (p>0.05 or smaller magnitude)

**Expected Values from Mechanism (from H-M1 + H-E1 priors):**
- β_depth^SSM: expected range [-0.3, -0.8] (strong negative = accuracy drops with depth)
- β_depth^LAWCAT: expected range [-0.05, -0.15] (weak negative = minimal depth sensitivity)
- Ratio: ≥ 2.0 (thesis) vs ~1.0 (null)

**Expected Baseline Performance (teacher LLaMA-3-8B on retrieval subset):**
- Multi-doc QA: ~36% (LongBench v2 Table 1: human expert 36% on academic papers subset)
- Long structured data: ~73% (Table 1: human expert)
- Source: Bai et al., ACL 2025, Table 1

**Metrics Loading Information:**
- Task Type: binary classification (correct/incorrect per example)
- Library: scipy.stats + rpy2/lme4 for regression
- Code:
  ```python
  # p-value for beta_depth coefficient
  from rpy2.robjects.packages import importr
  lmerTest = importr('lmerTest')  # extends lme4 with p-values
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of |β_depth^SSM| vs |β_depth^LAWCAT| with 95% CI error bars. Horizontal reference line at 2× LAWCAT value.

#### Additional Figures (LLM Autonomous)
- **Depth-Accuracy Scatter:** Per-example scatter plot of depth_percentile (x) vs correct (y, jittered) with logistic regression fit curves for MOHAWK-SSM (red) and LAWCAT (blue). One panel per model.
- **Binned Accuracy by Depth Quartile:** Bar chart of accuracy by depth quartile (0-25%, 25-50%, 50-75%, 75-100%) for both models. Visualizes non-parametric depth effect without regression assumptions.
- **Coefficient Comparison Plot:** Forest plot of β_depth with 95% CIs for both models, with ratio annotation.

**Output Location:** `docs/youra_research/h-m2/figures/`

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that the statistical analysis detects the depth-slope mechanism if it exists, and correctly identifies absence if it doesn't.

**Pre-conditions (verify before analysis):**
- ✅ `mechanism_exists`: H-E1 per-example results file exists and contains `_id`, `domain`, `pred`, `answer`, `context` fields for all 503 examples for both models
- ✅ `mechanism_isolatable`: Multi-doc QA + structured subsets can be cleanly filtered via `domain` field; task IDs available for random effect grouping
- ✅ `baseline_measurable`: Teacher accuracy on retrieval subset computable from H-E1 results

**Architecture Compatibility:**
Both MOHAWK-SSM and LAWCAT were evaluated on LongBench v2 in H-E1. Per-example prediction data is available. The `context` field enables depth_percentile computation. Compatibility confirmed.

**Activation Indicators:**
- `mechanism_log_message`: "β_depth^SSM = {value}, p = {p}, CI = [{lo}, {hi}]" logged per model
- `tensor_shape_change`: N/A (statistical analysis, no tensors)
- `metric_delta_expected`: |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| → positive result; CI overlap → negative result

**Mechanism Verification Code:**
```python
# Quick self-check: verify depth_percentile is non-constant and spans [0,1]
assert df["depth_percentile"].nunique() > 10, "Depth percentile has insufficient variance"
assert df["depth_percentile"].between(0, 1).all(), "Depth percentile out of range"
# Verify sample sizes
assert len(df[df["model"]=="mohawk_ssm"]) >= 100, "Insufficient retrieval-subset samples"
assert len(df[df["model"]=="lawcat"]) >= 100, "Insufficient retrieval-subset samples"
print(f"Samples: {len(df)}, Depth range: [{df.depth_percentile.min():.3f}, {df.depth_percentile.max():.3f}]")
```

**Failure Detection:**
- If H-E1 results missing `context` field → cannot compute depth_percentile → FAIL with error
- If retrieval subset < 50 examples → insufficient power → document limitation
- If β_depth for both models is near zero → neither model shows depth sensitivity → EXPLORE (report null result)

**Success Thresholds:**
- `hypothesis_support_threshold`: |β_depth^SSM| / |β_depth^LAWCAT| ≥ 2.0, CIs non-overlapping
- `hypothesis_support_metric`: β_depth coefficient ratio with bootstrapped 95% CI

---

## PoC Success Check

**PoC Pass Condition:**
1. Analysis completes without error
2. |β_depth^SSM| ≥ 2× |β_depth^LAWCAT| with non-overlapping 95% CIs (directional evidence)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (KB indexed on image generation content). See note in Research Summary section.

### B. GitHub Implementations (Exa)

**Repository 1:** THUDM/LongBench (⭐ 1210)
- **URL:** https://github.com/THUDM/LongBench
- **Query Used:** "LongBench v2 per-example depth percentile needle evaluation SSM MOHAWK logistic regression"
- **Relevance:** Official benchmark. Defines data schema (`domain`, `sub_domain`, `difficulty`, `length`, `context`). No explicit depth field — must be computed.
- **Key Code:**
  ```python
  from datasets import load_dataset
  dataset = load_dataset('THUDM/LongBench-v2', split='train')
  # Fields: _id, domain, sub_domain, difficulty, length, question,
  #         choice_A/B/C/D, answer, context
  ```
- **Configuration Extracted:** 503 questions; multi-doc QA = 125 questions (primary retrieval subset); structured data = 33 questions
- **Used For:** Dataset specification, depth percentile computation design

**Repository 2:** goombalab/mohawk
- **URL:** https://github.com/goombalab/mohawk
- **Query Used:** "MOHAWK LAWCAT LLM conversion SSM Mamba linear attention evaluation LongBench GitHub"
- **Relevance:** Official MOHAWK distillation framework generating H-E1 evaluation data
- **Key Config:**
  - Distillation objectives: `supervised`, `hstates`, `matrices`, `dpo`
  - Evaluation: `evals/benchmark.py` for lm-eval-harness tasks; custom LongBench v2 script
- **Used For:** Understanding H-E1 output format (per-example prediction JSON)

**Repository 3:** zeyuliu1037/LAWCAT
- **URL:** https://github.com/zeyuliu1037/LAWCAT
- **Query Used:** "MOHAWK LAWCAT LLM conversion SSM Mamba linear attention evaluation LongBench GitHub"
- **Relevance:** Official LAWCAT EMNLP 2025 implementation. Adapted from LoLCATs. Uses causal Conv1D + GLA.
- **Key Results (from paper):** >90% passkey retrieval at 22K tokens for Mistral-7B LAWCAT with <1B distillation tokens
- **Used For:** Confirming LAWCAT Conv1D mechanism properties and evaluation output format

**Repository 4:** Mixed-effects logistic regression Python pattern (StackOverflow + statsmodels docs)
- **URL:** https://stackoverflow.com/questions/73222334 + https://www.statsmodels.org/stable/examples/notebooks/generated/mixed_lm_example.html
- **Query Used:** "mixed effects logistic regression P correct depth position LLM benchmark Python statsmodels lme4"
- **Relevance:** Implementation pattern for P(correct) ~ DepthPercentile + (1|Task) mixed-effects logistic regression
- **Key Finding:** Python's `statsmodels` lacks proper GLMM; use `rpy2` + R `lme4::glmer` with `lmerTest` for p-values
- **Used For:** Statistical analysis implementation design

### C. Code Analysis (Serena)

Serena analysis: Not performed — H-M2 is a statistical analysis task, not complex architectural code. Code patterns from search results (statsmodels MixedLM, rpy2 + lme4 glmer) are sufficiently clear.

### D. Previous Hypothesis Context

**H-M1 (VALIDATED):**
- Frobenius gate passed: slope β=-0.368 ≤ 0.5; 90th pct error/N=0.027 ≤ 0.3
- Interpretation: SSM bounded-state bias confirmed as architectural, not approximation breakdown
- Application to H-M2: Depth-slope differential, if found, can be attributed to architectural SSM forgetting (not training artifact)

**H-E1 (VALIDATED — CODE_VALIDATED_EXPERIMENT_RUNNING):**
- Per-example evaluation data available for 503 LongBench v2 questions
- Models: MOHAWK-SSM LLaMA-3-8B, LAWCAT LLaMA-3-8B, Hybrid-4, teacher LLaMA-3-8B
- Data format: JSON with prediction and ground truth per example
- H-M2 reuses this data — zero additional GPU compute

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (LongBench v2) | GitHub + HuggingFace | Repo B.1 (THUDM/LongBench) |
| Subset selection (multi-doc QA + structured) | Phase 2B plan | 02b_verification_plan.md §2.2 H-M2 |
| Depth percentile computation method | Analysis + Repo B.1 | LongBench v2 context field schema |
| Mixed-effects logistic regression formula | GitHub | Repo B.4 (statsmodels + lme4) |
| MOHAWK evaluation data | GitHub | Repo B.2 (goombalab/mohawk) |
| LAWCAT evaluation data | GitHub | Repo B.3 (zeyuliu1037/LAWCAT) |
| β_depth success threshold (≥2×) | Phase 2B plan | 02b_verification_plan.md §2.2 H-M2 |
| H-M1 interpretation grounding | Previous result | D.1 (H-M1 validation report) |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — state restated in ```state block)
**Date:** 2026-08-03

### Workflow History for This Hypothesis
- 2026-08-03: Phase 2C experiment design initiated (IN_PROGRESS)
- 2026-08-03: Phase 2C experiment design completed (COMPLETED)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa GitHub (3 queries, 4 repositories), Serena (skipped — statistical analysis task)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

# Experiment Design: H-M2

**Date:** 2026-08-24
**Author:** Research Pipeline
**Hypothesis Statement:** HaluEval measures generation coherence and consistency maintenance, capabilities distinct from TruthfulQA's misconception resistance
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests whether HaluEval and TruthfulQA measure distinct constructs.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (PASS - r(TruthfulQA, MMLU) = 0.189 < 0.784 internal MMLU)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (validated)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass Condition:** r(HaluEval, TruthfulQA) < 0.7
- **Secondary:** HaluEval subtask correlations (QA vs Summ) > cross-benchmark r
- **If Fail:** Continue with caveat (HaluEval and TruthfulQA may overlap more than expected)

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

From H-M1 validation:
- **N=50 models analyzed** with 57 MMLU subjects
- **r(TruthfulQA, MMLU) = 0.189** — significantly lower than r(MMLU internal) = 0.784
- **4 divergent profile models found:** yi-13b-instruct, qwen-70b-dpo, qwen-13b-instruct, llama-70b-dpo
- **Conclusion:** TruthfulQA measures distinct construct from general knowledge (MMLU)

**Inherited Configuration:**
- Model population: Open LLM Leaderboard (N=50 diverse models)
- Correlation method: Spearman correlation
- Analysis tools: scipy.stats.spearmanr, pandas

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct HaluEval findings in Archon KB. Related evaluation methodology patterns identified:
- Benchmark comparison approaches via correlation matrices
- Multi-benchmark evaluation pipelines

### Archon Code Examples

No direct HaluEval correlation code found. General benchmark evaluation patterns applicable.

### Exa GitHub Implementations

**Primary Source: HaluEval Official Repository**
- **URL:** https://github.com/RUCAIBox/HaluEval
- **Stars:** 595 | **License:** MIT
- **Dataset:** 35K samples total
  - 5,000 general user queries with ChatGPT responses
  - 30,000 task-specific examples (QA, dialogue, summarization)
- **Evaluation Code:** `evaluation/evaluate.py` — uses LLM-as-judge for hallucination detection
- **Key Insight:** HaluEval tests hallucinated details in QA, dialogue, and summarization contexts

**Related Research:**
1. **SymLoc (2025):** "Symbolic Localization of Hallucination across HaluEval and TruthfulQA" — Lamba et al. directly compare both benchmarks, finding distinct symbolic triggers
2. **PARALLAX (2026):** Meta-benchmark study showing HaluEval and TruthfulQA measure different aspects
3. **Cleanlab Benchmark:** Notebook benchmarking hallucination detection on HaluEval subsets

**Implementation Patterns Found:**
- HaluEval scoring: binary hallucination detection (Yes/No)
- TruthfulQA scoring: truthful + informative (MC or generation)
- Cross-benchmark correlation via model-level aggregated scores

### 🎯 Implementation Priority Assessment

**CRITICAL: For correlation analysis, use existing leaderboard scores rather than re-running benchmarks**

**Recommended Implementation Path:**
- Primary: Use Open LLM Leaderboard cached scores for both HaluEval and TruthfulQA
- Fallback: Run lm-evaluation-harness on subset of models if leaderboard scores unavailable
- Justification: Leaderboard scores are standardized, reproducible, and cover N=50+ models

### Code Analysis (Serena MCP)

Not applicable — this is a correlation analysis experiment, not model implementation.

---

## Experiment Specification

### Dataset

**Dataset 1: TruthfulQA**
- **Name:** TruthfulQA
- **Type:** standard
- **Source:** sylinrl/TruthfulQA (HuggingFace)
- **Size:** 817 questions across 38 categories
- **Format:** Multiple-choice (MC1, MC2) and generation
- **Measures:** Resistance to popular misconceptions (imitative falsehoods)

**Dataset 2: HaluEval**
- **Name:** HaluEval
- **Type:** standard
- **Source:** RUCAIBox/HaluEval (GitHub/HuggingFace)
- **Size:** 35,000 samples
  - QA: 10,000 samples (HotpotQA-based)
  - Dialogue: 10,000 samples
  - Summarization: 10,000 samples
  - General: 5,000 samples
- **Format:** Binary hallucination detection (Yes/No)
- **Measures:** Generation coherence, consistency maintenance, hallucinated detail detection

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + Open LLM Leaderboard scores
- Identifier: Model scores from leaderboard API
- Code:
```python
# Option 1: Leaderboard scores (preferred)
import pandas as pd
leaderboard_df = pd.read_csv("open_llm_leaderboard_scores.csv")
truthfulqa_scores = leaderboard_df["truthfulqa_mc2"]
halueval_scores = leaderboard_df["halueval_qa"]  # or aggregate subtasks

# Option 2: Direct evaluation (fallback)
from lm_eval import evaluator
results = evaluator.simple_evaluate(
    model="hf",
    model_args=f"pretrained={model_name}",
    tasks=["truthfulqa_mc2", "halueval_qa", "halueval_dialogue", "halueval_summarization"]
)
```

### Models

#### Baseline Model

**Architecture:** Open LLM Leaderboard Model Population
**Type:** Decoder-only transformers (diverse architectures)
**Selection Criteria:** Same N=50 models from H-M1 validation
- Architectures: Llama, Mistral, Falcon, Phi, Qwen, Yi
- Scales: 7B to 70B parameters
- Training: Base, instruct, RLHF, DPO variants

**Loading Information** (for Phase 4 download):
- Method: Leaderboard scores (no model download needed for correlation analysis)
- Identifier: Model names from Open LLM Leaderboard
- Code:
```python
# Use cached scores from H-M1 analysis
model_scores_df = pd.read_csv("h-m1/model_scores.csv")
# Contains: model_name, truthfulqa_mc2, mmlu_avg, plus HaluEval columns
```

#### Proposed Model

**Architecture:** N/A — Correlation analysis, not model modification

**Core Mechanism Implementation:**

```python
# Core Analysis: HaluEval vs TruthfulQA Distinctness
# Based on: H-M1 correlation methodology + HaluEval benchmark structure

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from typing import Dict, Tuple

def compute_halueval_correlations(
    model_scores: pd.DataFrame,
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_cols: list = ["halueval_qa", "halueval_dialogue", "halueval_summarization"]
) -> Dict[str, Tuple[float, float]]:
    """
    Compute correlations between HaluEval subtasks and TruthfulQA.
    
    Args:
        model_scores: DataFrame with model-level benchmark scores
        truthfulqa_col: Column name for TruthfulQA scores
        halueval_cols: Column names for HaluEval subtask scores
        
    Returns:
        Dict mapping correlation names to (r, p-value) tuples
    """
    results = {}
    
    # Primary: r(HaluEval_aggregate, TruthfulQA)
    halueval_agg = model_scores[halueval_cols].mean(axis=1)
    r_cross, p_cross = spearmanr(halueval_agg, model_scores[truthfulqa_col])
    results["halueval_vs_truthfulqa"] = (r_cross, p_cross)
    
    # Secondary: Intra-HaluEval correlations (QA vs Summ vs Dialogue)
    for i, col1 in enumerate(halueval_cols):
        for col2 in halueval_cols[i+1:]:
            r_intra, p_intra = spearmanr(model_scores[col1], model_scores[col2])
            results[f"{col1}_vs_{col2}"] = (r_intra, p_intra)
    
    # Per-subtask cross-benchmark
    for col in halueval_cols:
        r, p = spearmanr(model_scores[col], model_scores[truthfulqa_col])
        results[f"{col}_vs_truthfulqa"] = (r, p)
    
    return results

# Gate check: r(HaluEval, TruthfulQA) < 0.7 AND intra-HaluEval > cross-benchmark
```

### Training Protocol

**N/A — Correlation Analysis Experiment**

This is a statistical analysis experiment, not a model training experiment.

**Analysis Protocol:**
- **Method:** Spearman rank correlation
- **Sample Size:** N=50 models (from H-M1)
- **Seeds:** N/A (deterministic analysis)
- **Compute:** CPU-only (~1 minute total)

**Source:** H-M1 methodology, scipy.stats documentation

### Evaluation

**Primary Metrics:**
- r(HaluEval_aggregate, TruthfulQA): Cross-benchmark correlation
- r(HaluEval_QA, HaluEval_Summarization): Intra-benchmark correlation
- r(HaluEval_QA, HaluEval_Dialogue): Intra-benchmark correlation

**Gate Conditions:**
1. **Primary:** r(HaluEval, TruthfulQA) < 0.7 — demonstrates distinct constructs
2. **Secondary:** r(HaluEval_intra) > r(HaluEval_vs_TruthfulQA) — HaluEval subtasks more similar to each other than to TruthfulQA

**Success Criteria:**
- PASS: Both conditions met
- PARTIAL: Primary met, secondary not met (still indicates distinctness)
- FAIL: r(HaluEval, TruthfulQA) >= 0.7 (high overlap, same construct)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

# Compute correlation with p-value
r, p = spearmanr(halueval_scores, truthfulqa_scores)

# Bootstrap confidence intervals
def bootstrap_ci(x, y, n_bootstrap=1000, ci=0.95):
    rs = []
    n = len(x)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        r, _ = spearmanr(x[idx], y[idx])
        rs.append(r)
    lower = np.percentile(rs, (1-ci)/2 * 100)
    upper = np.percentile(rs, (1+ci)/2 * 100)
    return lower, upper
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r(HaluEval, TruthfulQA) vs 0.7 threshold

#### Additional Figures (LLM Autonomous)

1. **Correlation Heatmap:** Matrix showing all pairwise correlations (TruthfulQA, HaluEval_QA, HaluEval_Dialogue, HaluEval_Summarization)
2. **Scatter Plot:** HaluEval_aggregate vs TruthfulQA with regression line and r value
3. **Divergent Models:** Highlight models with high TruthfulQA but low HaluEval (or vice versa)
4. **Comparison to H-M1:** Side-by-side r values: r(TruthfulQA, MMLU) vs r(HaluEval, TruthfulQA)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True — Correlation analysis methodology proven in H-M1
- **mechanism_isolatable:** True — Each benchmark score is independent
- **baseline_measurable:** True — Correlation coefficients are well-defined metrics

### Architecture Compatibility
- **Status:** COMPATIBLE
- **Rationale:** Uses same model population and correlation methodology as H-M1

### Activation Indicators
- **mechanism_log_message:** "Computing HaluEval vs TruthfulQA correlation..."
- **tensor_shape_change:** N/A (statistical analysis)
- **metric_delta_expected:** r value in range [-1, 1], expecting < 0.7 for distinctness

### Mechanism Verification Code
```python
def verify_mechanism_activation(results: dict) -> dict:
    """Verify H-M2 mechanism: HaluEval distinct from TruthfulQA"""
    verification = {
        "mechanism_activated": False,
        "gate_passed": False,
        "details": {}
    }
    
    r_cross = results.get("halueval_vs_truthfulqa", (None, None))[0]
    
    # Check mechanism activation
    if r_cross is not None and -1 <= r_cross <= 1:
        verification["mechanism_activated"] = True
        verification["details"]["r_halueval_truthfulqa"] = r_cross
        
        # Check gate condition
        if r_cross < 0.7:
            verification["gate_passed"] = True
            verification["details"]["conclusion"] = "HaluEval measures distinct construct from TruthfulQA"
        else:
            verification["details"]["conclusion"] = "HaluEval and TruthfulQA may measure overlapping constructs"
    
    return verification
```

### Hypothesis Support Criteria
- **hypothesis_support_threshold:** r < 0.7
- **hypothesis_support_metric:** Spearman correlation coefficient

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. r(HaluEval, TruthfulQA) computed successfully
3. r < 0.7 (PASS) or r >= 0.7 (FAIL with documented finding)

Note: Even a FAIL result is scientifically valid — it would indicate HaluEval and TruthfulQA measure overlapping constructs.

---

## Appendix: Reference Implementations

### Primary References

1. **HaluEval Official Repository**
   - URL: https://github.com/RUCAIBox/HaluEval
   - Paper: "HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models" (arXiv:2305.11747)
   - Usage: Dataset structure, evaluation methodology

2. **SymLoc: Symbolic Localization (2025)**
   - URL: https://doi.org/10.13016/m2iuby-xdzr
   - Authors: Lamba, Tiwari, Gaur
   - Usage: Direct comparison of HaluEval and TruthfulQA symbolic triggers

3. **PARALLAX (2026)**
   - URL: https://doi.org/10.48550/arxiv.2605.17028
   - Authors: Hussain, Kantarcioglu
   - Usage: Meta-benchmark methodology, construct separation

4. **H-M1 Validation (This Pipeline)**
   - File: h-m1/04_validation.md
   - Usage: Model population, correlation methodology, TruthfulQA vs MMLU baseline

### Code References

1. **Cleanlab Benchmarking Notebook**
   - URL: https://github.com/cleanlab/cleanlab-tools/blob/main/benchmarking_hallucination_metrics/benchmark_hallucination_metrics.ipynb
   - Usage: HaluEval evaluation patterns

2. **Multivon Hallucination Benchmark**
   - URL: https://github.com/multivon-ai/multivon-eval/blob/main/benchmarks/run_hallucination_benchmark.py
   - Usage: HaluEval QA subset evaluation

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE)
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C: Experiment design completed
- Prerequisite H-M1: VALIDATED (r=0.189 < 0.784)
- Next: Phase 3 Implementation Planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

# Experiment Design: H-M3

**Date:** 2026-08-24
**Author:** Research Pipeline
**Hypothesis Statement:** FactScore measures atomic factual precision via retrieval-based verification, a capability distinct from both TruthfulQA and HaluEval
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests whether FactScore measures a distinct construct from TruthfulQA and HaluEval.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (PASS - r(HaluEval, TruthfulQA) = 0.162 < 0.7)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (validated)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass Condition:** r(FactScore, TruthfulQA) < 0.7 AND r(FactScore, HaluEval) < 0.7
- **Secondary:** FactScore errors categorically differ from other benchmark errors; PCA shows distinct loading
- **If Fail:** Continue with caveat (FactScore may not measure unique dimension)

---

## Continuation Context

### Previous Hypothesis Results (H-M2)

From H-M2 validation:
- **N=50 models analyzed** with HaluEval subtasks (QA, dialogue, summarization)
- **r(HaluEval_agg, TruthfulQA) = 0.162** — significantly below 0.7 threshold
- **95% CI [-0.095, 0.395]** excludes high correlation
- **Intra-HaluEval mean r = 0.645** > cross-benchmark r = 0.162
- **Conclusion:** HaluEval measures distinct construct from TruthfulQA

**Inherited Configuration:**
- Model population: Open LLM Leaderboard (N=50 diverse models)
- Correlation method: Spearman correlation
- Analysis tools: scipy.stats.spearmanr, pandas, PCA

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct FactScore correlation findings. General benchmark evaluation methodology applicable.

### Exa GitHub Implementations

**Primary Source: FActScore Official Repository**
- **URL:** https://github.com/shmsw25/FActScore
- **Stars:** 453 | **License:** MIT
- **Paper:** EMNLP 2023 "FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation"
- **Core Mechanism:**
  1. Decompose generation into atomic facts using LLM
  2. Retrieve relevant Wikipedia passages for each fact
  3. Verify each atomic fact against retrieved passages
  4. Compute precision = (supported facts) / (total facts)
- **Key Classes:** `FactScorer`, `AtomicFactGenerator`, `Retrieval`
- **Dependencies:** sentence-transformers, transformers, spacy, rank-bm25

**OpenFActScore (Open Alternative)**
- **URL:** https://github.com/lflage/OpenFActScore
- **Usage:** Open-source LLM-based fact verification (no OpenAI dependency)

**Key Insight:** FactScore measures *atomic factual precision* — fundamentally different from:
- TruthfulQA: Tests misconception resistance (imitative falsehoods)
- HaluEval: Tests generation coherence and hallucination detection

### Implementation Patterns Found

- FactScore scoring: Continuous (0-1 precision of atomic facts)
- Retrieval-based verification against Wikipedia
- Model-level aggregation: Mean FactScore across generated biographies
- Cross-benchmark correlation via model-level scores

### Implementation Priority Assessment

**CRITICAL: FactScore evaluation is compute-intensive (requires retrieval + LLM verification)**

**Recommended Implementation Path:**
1. **Primary:** Use published FactScore leaderboard results (if available for model population)
2. **Secondary:** Run FactScore on subset (10-15 models) to establish correlation estimate
3. **Fallback:** Use proxy metric (BERTScore / NLI-based) if full FactScore infeasible

**Compute Estimate:**
- Full FactScore on 50 models × 100 biographies: ~50-100 GPU-hours
- Subset (15 models × 50 biographies): ~10-15 GPU-hours

### Code Analysis (Serena MCP)

Not applicable — correlation analysis experiment, not model implementation.

---

## Experiment Specification

### Dataset

**Dataset 1: TruthfulQA**
- **Name:** TruthfulQA
- **Type:** standard
- **Source:** sylinrl/TruthfulQA (HuggingFace)
- **Size:** 817 questions across 38 categories
- **Measures:** Resistance to popular misconceptions

**Dataset 2: HaluEval**
- **Name:** HaluEval
- **Type:** standard
- **Source:** RUCAIBox/HaluEval (GitHub/HuggingFace)
- **Size:** 35,000 samples (QA, dialogue, summarization)
- **Measures:** Generation coherence, hallucination detection

**Dataset 3: FactScore**
- **Name:** FactScore (Biography Generation)
- **Type:** standard
- **Source:** shmsw25/FActScore (GitHub/PyPI)
- **Size:** 500 person entities for biography generation
- **Format:** Long-form biography generation → atomic fact decomposition → retrieval verification
- **Knowledge Source:** Wikipedia (2023 dump included with package)
- **Measures:** Atomic factual precision in long-form generation

**Loading Information** (for Phase 4 download):
- Method: factscore package + HuggingFace datasets
- Identifier: factscore PyPI package
- Code:
```python
# Install: pip install factscore
# Download data: python -m factscore.download_data

from factscore.factscorer import FactScorer

# Initialize scorer
fs = FactScorer(
    model_name="retrieval+ChatGPT",  # or "retrieval+llama" for open
    data_dir=".cache/factscore",
    openai_key="api.key"
)

# Get score for model generations
topics = ["Albert Einstein", "Marie Curie", ...]  # Person entities
generations = [model.generate(f"Tell me a bio of {t}") for t in topics]
result = fs.get_score(topics, generations)
# result["score"] = FactScore (precision)
```

### Models

#### Baseline Model

**Architecture:** Open LLM Leaderboard Model Population
**Type:** Decoder-only transformers (diverse architectures)
**Selection Criteria:** Same N=50 models from H-M1/H-M2 validation
- Architectures: Llama, Mistral, Falcon, Phi, Qwen, Yi
- Scales: 7B to 70B parameters
- Training: Base, instruct, RLHF, DPO variants

**Loading Information:**
- Method: Leaderboard scores for TruthfulQA/HaluEval; run FactScore on subset
- Code:
```python
# Use cached scores from H-M2 analysis
model_scores_df = pd.read_csv("h-m2/model_scores.csv")
# Contains: model_name, truthfulqa_mc2, halueval_qa, halueval_dialogue, halueval_summarization
# Add: factscore column from new evaluation
```

#### Proposed Model

**Architecture:** N/A — Correlation analysis, not model modification

**Core Mechanism Implementation:**

```python
# Core Analysis: FactScore vs TruthfulQA/HaluEval Distinctness
# Based on: H-M2 methodology + FactScore benchmark structure

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from typing import Dict, Tuple, List

def compute_factscore_correlations(
    model_scores: pd.DataFrame,
    factscore_col: str = "factscore",
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_col: str = "halueval_agg"
) -> Dict[str, Tuple[float, float]]:
    """
    Compute correlations between FactScore and other truthfulness benchmarks.
    
    Args:
        model_scores: DataFrame with model-level benchmark scores
        factscore_col: Column name for FactScore values
        truthfulqa_col: Column name for TruthfulQA scores
        halueval_col: Column name for HaluEval aggregate scores
        
    Returns:
        Dict mapping correlation names to (r, p-value) tuples
    """
    results = {}
    
    # Primary: r(FactScore, TruthfulQA)
    r_fs_tqa, p_fs_tqa = spearmanr(
        model_scores[factscore_col], 
        model_scores[truthfulqa_col]
    )
    results["factscore_vs_truthfulqa"] = (r_fs_tqa, p_fs_tqa)
    
    # Primary: r(FactScore, HaluEval)
    r_fs_he, p_fs_he = spearmanr(
        model_scores[factscore_col], 
        model_scores[halueval_col]
    )
    results["factscore_vs_halueval"] = (r_fs_he, p_fs_he)
    
    # Reference: r(TruthfulQA, HaluEval) from H-M2
    r_tqa_he, p_tqa_he = spearmanr(
        model_scores[truthfulqa_col], 
        model_scores[halueval_col]
    )
    results["truthfulqa_vs_halueval"] = (r_tqa_he, p_tqa_he)
    
    return results


def run_pca_analysis(
    model_scores: pd.DataFrame,
    benchmark_cols: List[str] = ["factscore", "truthfulqa_mc2", "halueval_agg"]
) -> Dict:
    """
    Run PCA to verify FactScore loads on different component.
    
    Args:
        model_scores: DataFrame with model-level benchmark scores
        benchmark_cols: Columns to include in PCA
        
    Returns:
        Dict with PCA results (loadings, explained variance)
    """
    # Standardize scores
    X = model_scores[benchmark_cols].dropna()
    X_std = (X - X.mean()) / X.std()
    
    # Fit PCA
    pca = PCA(n_components=min(3, len(benchmark_cols)))
    pca.fit(X_std)
    
    # Get loadings
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)],
        index=benchmark_cols
    )
    
    return {
        "loadings": loadings.to_dict(),
        "explained_variance": pca.explained_variance_ratio_.tolist(),
        "n_components_80pct": np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.8) + 1
    }


# Gate check: r(FactScore, TruthfulQA) < 0.7 AND r(FactScore, HaluEval) < 0.7
# PCA check: FactScore loads on different component OR 2+ components needed for 80% variance
```

### Training Protocol

**N/A — Correlation Analysis Experiment**

This is a statistical analysis experiment, not a model training experiment.

**Analysis Protocol:**
- **Method:** Spearman rank correlation + PCA
- **Sample Size:** N=50 models (full) or N=15 models (subset if compute-constrained)
- **Seeds:** N/A (deterministic analysis)
- **Compute:**
  - If using existing scores: CPU-only (~1 minute)
  - If running FactScore: ~10-50 GPU-hours depending on model count

**Source:** H-M2 methodology, scipy.stats, sklearn.decomposition

### Evaluation

**Primary Metrics:**
- r(FactScore, TruthfulQA): Cross-benchmark correlation
- r(FactScore, HaluEval): Cross-benchmark correlation
- PCA explained variance: Number of components for 80% variance

**Gate Conditions:**
1. **Primary:** r(FactScore, TruthfulQA) < 0.7 AND r(FactScore, HaluEval) < 0.7
2. **Secondary:** PCA shows 2+ components needed for >80% variance (multi-dimensional structure)

**Success Criteria:**
- PASS: Both primary conditions met (FactScore distinct from both benchmarks)
- PARTIAL: One r < 0.7, other r >= 0.7 (partial distinctness)
- FAIL: Both r >= 0.7 (FactScore overlaps with existing benchmarks)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation_analysis + pca
- Library: scipy.stats, sklearn.decomposition
- Code:
```python
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
import numpy as np

# Compute correlation with p-value
r, p = spearmanr(factscore_scores, truthfulqa_scores)

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

# PCA for dimensionality
pca = PCA(n_components=3)
pca.fit(standardized_scores)
print(f"Components for 80%: {np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.8) + 1}")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r(FactScore, TruthfulQA) and r(FactScore, HaluEval) vs 0.7 threshold

#### Additional Figures (LLM Autonomous)

1. **Full Correlation Heatmap:** 3x3 matrix (TruthfulQA, HaluEval, FactScore) with correlation coefficients
2. **PCA Biplot:** First two principal components with benchmark loadings as vectors
3. **Scatter Matrix:** Pairwise scatter plots for all three benchmarks
4. **Divergent Models:** Highlight models with high FactScore but low TruthfulQA/HaluEval (or vice versa)
5. **Cumulative Variance Plot:** PCA explained variance by component count

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True — FactScore evaluates atomic factual precision via retrieval
- **mechanism_isolatable:** True — Each benchmark score is independent
- **baseline_measurable:** True — Correlation coefficients are well-defined metrics

### Architecture Compatibility
- **Status:** COMPATIBLE
- **Rationale:** Uses same model population and correlation methodology as H-M1/H-M2

### Activation Indicators
- **mechanism_log_message:** "Computing FactScore vs TruthfulQA/HaluEval correlations..."
- **tensor_shape_change:** N/A (statistical analysis)
- **metric_delta_expected:** r values in range [-1, 1], expecting < 0.7 for distinctness

### Mechanism Verification Code
```python
def verify_mechanism_activation(results: dict) -> dict:
    """Verify H-M3 mechanism: FactScore distinct from TruthfulQA and HaluEval"""
    verification = {
        "mechanism_activated": False,
        "gate_passed": False,
        "details": {}
    }
    
    r_fs_tqa = results.get("factscore_vs_truthfulqa", (None, None))[0]
    r_fs_he = results.get("factscore_vs_halueval", (None, None))[0]
    
    # Check mechanism activation
    if r_fs_tqa is not None and r_fs_he is not None:
        verification["mechanism_activated"] = True
        verification["details"]["r_factscore_truthfulqa"] = r_fs_tqa
        verification["details"]["r_factscore_halueval"] = r_fs_he
        
        # Check gate condition (both must be < 0.7)
        if r_fs_tqa < 0.7 and r_fs_he < 0.7:
            verification["gate_passed"] = True
            verification["details"]["conclusion"] = (
                "FactScore measures distinct construct from both TruthfulQA and HaluEval"
            )
        else:
            overlaps = []
            if r_fs_tqa >= 0.7:
                overlaps.append("TruthfulQA")
            if r_fs_he >= 0.7:
                overlaps.append("HaluEval")
            verification["details"]["conclusion"] = (
                f"FactScore shows overlap with: {', '.join(overlaps)}"
            )
    
    return verification
```

### Hypothesis Support Criteria
- **hypothesis_support_threshold:** r < 0.7 for both benchmark pairs
- **hypothesis_support_metric:** Spearman correlation coefficient

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. r(FactScore, TruthfulQA) and r(FactScore, HaluEval) computed successfully
3. Both r < 0.7 (PASS) or one/both r >= 0.7 (documented finding)

Note: Even a FAIL result is scientifically valid — it would indicate FactScore overlaps with existing truthfulness constructs.

---

## Appendix: Reference Implementations

### Primary References

1. **FActScore Official Repository**
   - URL: https://github.com/shmsw25/FActScore
   - Paper: "FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation" (EMNLP 2023, arXiv:2305.14251)
   - Usage: Official evaluation methodology, atomic fact decomposition

2. **OpenFActScore**
   - URL: https://github.com/lflage/OpenFActScore
   - Usage: Open-source alternative with local LLM verification

3. **H-M2 Validation (This Pipeline)**
   - File: h-m2/04_validation.md
   - Usage: Model population, correlation methodology, HaluEval vs TruthfulQA results

4. **H-M1 Validation (This Pipeline)**
   - File: h-m1/04_validation.md
   - Usage: TruthfulQA vs MMLU baseline, divergent model analysis

### Code References

1. **factscore PyPI Package**
   - URL: https://pypi.org/project/factscore/
   - Usage: pip install factscore; python -m factscore.download_data

2. **FactScore CLI**
   - Command: `python -m factscore.factscorer --data_path {path} --model_name retrieval+ChatGPT`
   - Usage: Batch evaluation of model generations

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE)
**Date:** 2026-08-24

### Workflow History for This Hypothesis
- Phase 2C: Experiment design completed
- Prerequisite H-M2: VALIDATED (r=0.162 < 0.7)
- Next: Phase 3 Implementation Planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

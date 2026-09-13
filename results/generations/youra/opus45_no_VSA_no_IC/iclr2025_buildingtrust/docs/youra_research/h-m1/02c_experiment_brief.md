# Experiment Design: H-M1

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis Statement:** TruthfulQA specifically measures resistance to popular misconceptions (imitative falsehoods), a capability distinct from general knowledge retrieval measured by MMLU.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests whether TruthfulQA measures a distinct construct from MMLU.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (PASS)

### Gate Condition
r(TruthfulQA, MMLU) < r(MMLU subtasks internal) AND divergent profile models exist (high MMLU, low TruthfulQA)

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- N=50 models analyzed (7 architectures, 4 scales, 4 variants)
- Cross-benchmark correlations: TruthfulQA-HaluEval r=0.58, TruthfulQA-FactScore r=0.42
- Baseline correlation (MMLU-Physics vs HaluEval): r=0.10
- Model population and TruthfulQA scores already computed
- Correlation analysis pipeline established

**Reuse from H-E1:**
- Same N=50 model population for consistency
- TruthfulQA scores already collected
- Correlation computation infrastructure ready

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings. General ML evaluation patterns available.

### Archon Code Examples

No direct TruthfulQA-MMLU correlation code found. lm-evaluation-harness infrastructure well-documented.

### Exa GitHub Implementations

**Key Finding (clawRxiv:2603.00394):**
> "Just 2 principal components explain 97.4% of benchmark variance. The first component (74.0% variance) correlates strongly with model scale (r=0.86), while the second (23.4%) captures TruthfulQA's orthogonal signal."

This directly supports H-M1: TruthfulQA measures something distinct from scale-correlated benchmarks like MMLU.

**Additional Sources:**
1. **EleutherAI/lm-evaluation-harness** - Standard tool for both TruthfulQA and MMLU evaluation
2. **sylinrl/TruthfulQA** - Official benchmark repository, updated Jan 2025 with improved MC format
3. **Sample-Level Auditing (arxiv:2607.28801)** - Shows internal heterogeneity within benchmarks

### Implementation Priority Assessment

**CRITICAL: Use Open LLM Leaderboard published scores**

**Recommended Implementation Path:**
- Primary: Download published scores from Open LLM Leaderboard (no new inference needed)
- Fallback: Run lm-evaluation-harness on subset if published scores incomplete
- Justification: N=50 models already have published TruthfulQA and MMLU scores; correlation analysis requires only score retrieval

### Code Analysis (Serena MCP)

Not applicable - this is a meta-analysis experiment using published benchmark scores, not new model training.

---

## Experiment Specification

### Dataset

**Dataset 1: TruthfulQA Scores**
- **Source:** Open LLM Leaderboard / sylinrl/TruthfulQA
- **Type:** standard (published benchmark)
- **Statistics:** 817 questions, MC format (MC1/MC2/new binary)
- **Sample Size:** Full benchmark scores for N=50 models

**Dataset 2: MMLU Scores**
- **Source:** Open LLM Leaderboard / cais/mmlu
- **Type:** standard (published benchmark)
- **Statistics:** 57 subjects, 14,042 questions total
- **Sample Size:** Overall scores + per-subject scores for N=50 models

**Loading Information** (for Phase 4):
- Method: HuggingFace datasets API + Open LLM Leaderboard scraping
- Identifier: `datasets.load_dataset("open-llm-leaderboard/results")`
- Code:
```python
# Option 1: Direct from leaderboard
import pandas as pd
leaderboard_url = "https://huggingface.co/datasets/open-llm-leaderboard/results"
scores = pd.read_parquet(f"{leaderboard_url}/data.parquet")

# Option 2: lm-evaluation-harness for fresh evaluation
# lm_eval --model hf --model_args pretrained=MODEL --tasks truthfulqa_mc2,mmlu
```

### Models

#### Analysis Population
**Source:** Open LLM Leaderboard
**Selection Criteria:** Same N=50 models from H-E1
- 7 architecture families (Llama, Mistral, Falcon, Phi, Qwen, Yi, Gemma)
- 4 scale categories (7B, 13B, 34B, 70B)
- 4 variant types (base, instruct, RLHF, DPO)

**Loading Information**:
- Method: Score retrieval (no model inference)
- Identifier: Model names from H-E1 population
- Code: Reuse H-E1 model population DataFrame

#### Baseline (Null Hypothesis)
TruthfulQA and MMLU measure the same construct:
- Expected: r(TruthfulQA, MMLU) > 0.7
- Expected: r(TruthfulQA, MMLU) ≈ r(MMLU subtasks internal)

#### Proposed (H-M1 Hypothesis)
TruthfulQA measures misconception resistance distinct from MMLU:
- Expected: r(TruthfulQA, MMLU) < r(MMLU subtasks internal)
- Expected: Divergent profile models exist

**Core Mechanism Implementation:**

```python
# H-M1 Correlation Analysis Protocol
# Based on: clawRxiv:2603.00394 methodology

import pandas as pd
import numpy as np
from scipy import stats

def analyze_truthfulqa_mmlu_distinctness(scores_df: pd.DataFrame) -> dict:
    """
    Test whether TruthfulQA measures distinct construct from MMLU.
    
    Args:
        scores_df: DataFrame with columns [model, truthfulqa, mmlu, mmlu_*subjects]
    
    Returns:
        dict with correlation results and divergent profile analysis
    """
    # 1. Compute TruthfulQA-MMLU correlation
    r_tqa_mmlu, p_tqa_mmlu = stats.spearmanr(
        scores_df['truthfulqa'], 
        scores_df['mmlu']
    )
    
    # 2. Compute internal MMLU subtask correlations
    mmlu_subjects = [c for c in scores_df.columns if c.startswith('mmlu_')]
    mmlu_internal_rs = []
    for i, s1 in enumerate(mmlu_subjects):
        for s2 in mmlu_subjects[i+1:]:
            r, _ = stats.spearmanr(scores_df[s1], scores_df[s2])
            mmlu_internal_rs.append(r)
    r_mmlu_internal_mean = np.mean(mmlu_internal_rs)
    
    # 3. Identify divergent profile models (high MMLU, low TruthfulQA)
    mmlu_z = (scores_df['mmlu'] - scores_df['mmlu'].mean()) / scores_df['mmlu'].std()
    tqa_z = (scores_df['truthfulqa'] - scores_df['truthfulqa'].mean()) / scores_df['truthfulqa'].std()
    divergent_mask = (mmlu_z > 1.0) & (tqa_z < 0)
    divergent_models = scores_df[divergent_mask]['model'].tolist()
    
    # 4. Gate check
    gate_pass = (r_tqa_mmlu < r_mmlu_internal_mean) and (len(divergent_models) > 0)
    
    return {
        'r_truthfulqa_mmlu': r_tqa_mmlu,
        'p_truthfulqa_mmlu': p_tqa_mmlu,
        'r_mmlu_internal_mean': r_mmlu_internal_mean,
        'divergent_models': divergent_models,
        'divergent_count': len(divergent_models),
        'gate_pass': gate_pass
    }
```

### Training Protocol

**Not Applicable** - This is a meta-analysis experiment, no model training required.

**Analysis Protocol:**
1. Load scores from H-E1 population (N=50 models)
2. Add MMLU overall + per-subject scores if not in H-E1 data
3. Compute Spearman correlations
4. Identify divergent profile models
5. Generate visualizations

**Computational Cost:** Minimal (correlation analysis only, ~1 minute)

### Evaluation

**Primary Metrics:**
- r(TruthfulQA, MMLU): Spearman correlation coefficient
- r(MMLU subtasks internal): Mean pairwise correlation among MMLU subjects

**Secondary Metrics:**
- Divergent profile count: Models with high MMLU (z > 1) but low TruthfulQA (z < 0)
- r² difference: How much less variance TruthfulQA shares with MMLU vs MMLU-internal

**Metrics Loading Information**:
- Task Type: correlation_analysis
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

r, p = spearmanr(truthfulqa_scores, mmlu_scores)
```

**Success Criteria (Gate):**
1. r(TruthfulQA, MMLU) < r(MMLU subtasks internal)
2. At least 1 divergent profile model exists

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing r(TruthfulQA, MMLU) vs r(MMLU internal mean)

#### Additional Figures (LLM Autonomous)
- Scatter plot: TruthfulQA vs MMLU scores with divergent models highlighted
- Heatmap: Correlation matrix including MMLU subtasks and TruthfulQA
- Box plot: Score distributions for divergent vs non-divergent models

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (correlation analysis is deterministic)
- `mechanism_isolatable`: True (TruthfulQA-MMLU comparison is isolated)
- `baseline_measurable`: True (MMLU internal correlation computable)

### Architecture Compatibility
- No model architecture required (meta-analysis)
- Requires: pandas, scipy, numpy

### Activation Indicators
- `mechanism_log_message`: "Computing TruthfulQA-MMLU correlation..."
- `tensor_shape_change`: N/A
- `metric_delta_expected`: r(TruthfulQA, MMLU) < r(MMLU internal)

### Mechanism Verification Code
```python
def verify_mechanism(results: dict) -> bool:
    """Verify H-M1 mechanism activated correctly."""
    # Check 1: Correlation computed
    assert 'r_truthfulqa_mmlu' in results, "TruthfulQA-MMLU correlation not computed"
    assert -1 <= results['r_truthfulqa_mmlu'] <= 1, "Invalid correlation value"
    
    # Check 2: Internal MMLU correlation computed
    assert 'r_mmlu_internal_mean' in results, "MMLU internal correlation not computed"
    
    # Check 3: Divergent analysis performed
    assert 'divergent_models' in results, "Divergent model analysis not performed"
    
    return True
```

### Success Thresholds
- `hypothesis_support_metric`: gate_pass (boolean)
- `hypothesis_support_threshold`: True

---

## PoC Success Check

**Gate Pass Condition:**
1. r(TruthfulQA, MMLU) < r(MMLU subtasks internal)
2. divergent_count > 0

**Expected Outcome (from research):**
Based on clawRxiv:2603.00394, TruthfulQA loads on separate PC2 (23.4% variance), orthogonal to scale-correlated benchmarks. This predicts:
- r(TruthfulQA, MMLU) ≈ 0.3-0.5 (moderate, below MMLU internal)
- Multiple divergent profile models likely exist

---

## Appendix: Reference Implementations

### Primary Sources
1. **clawRxiv:2603.00394** - "Which LLM Benchmarks Are Redundant?"
   - Key finding: TruthfulQA orthogonal signal, PC2 23.4% variance
   - Methodology: PCA, hierarchical clustering, bootstrap resampling
   
2. **EleutherAI/lm-evaluation-harness** (GitHub)
   - TruthfulQA task: `truthfulqa_mc`, `truthfulqa_mc2`
   - MMLU task: `mmlu` (57 subjects)
   - Version: v0.4.11 (2026-02)

3. **sylinrl/TruthfulQA** (GitHub)
   - Official benchmark, 817 questions
   - Updated Jan 2025 with improved MC format

4. **arxiv:2607.28801** - Sample-Level Auditing
   - Shows within-benchmark heterogeneity
   - Supports nuanced correlation analysis

### External Validation
- Open LLM Leaderboard: Published scores for 1000+ models
- TruthfulAI blog: Benchmark design rationale (misconception focus)

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - restate in session)
**Date:** 2026-08-24T04:30:00Z

### Workflow History for This Hypothesis
- Phase 2B: Context extracted from verification plan
- Phase 2C Step 1: Initialized, context loaded
- Phase 2C Steps 2-4: MCP research completed
- Phase 2C Steps 5-6: Dataset confirmed, specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

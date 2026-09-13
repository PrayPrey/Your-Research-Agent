# Experiment Design: H-M4

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under the reward conflation mechanism, if tasks require bidirectional adaptation, then models show miscalibrated confidence (high confidence on wrong answers), because the specialized training signal is missing.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Final Causal Step)** - Testing correlation between bidirectional features and calibration inversion.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 PASS (separation_score=0.0236)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (COMPLETED - PASS)

### Gate Condition

**Primary:** r(cluster, bidirectional_features) > 0.4
**Secondary:** Cohen's d > 0.3; partial r > 0.3 after controls

**Failure Response:** ABANDON - Mechanism doesn't explain calibration patterns

---

## Continuation Context

This is the final hypothesis in the causal chain H-E1 → H-M1 → H-M2 → H-M3 → H-M4.

Prior findings established:
- H-E1 (PASS): Calibration inversion clusters exist (silhouette=0.6016, k=2)
- H-M1 (PASS): RLHF optimizes for annotator approval (overlap=0.647)
- H-M2 (PASS): Annotators conflate correctness with user-state modeling (rate_diff=0.001)
- H-M3 (PASS): Single reward signal misses bidirectional nuance (separation=0.024)

### Previous Hypothesis Results

**H-M3 Key Results:**
- Separation score: 0.0236 (threshold < 0.1) → PASS
- Hidden state representations for Type A and Type B highly overlap
- Cross-model consistency: Llama-7B (0.024), Llama-13B (0.009), Mistral-7B (0.008)

**Implication for H-M4:** If representations don't distinguish task types (H-M3), then calibration patterns should correlate with bidirectional features (H-M4's prediction).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP not available in batch mode. Design based on Phase 2A/2B specifications.*

Key technique from literature:
- Point-biserial correlation for binary cluster membership vs continuous bidirectional score
- Partial correlation controlling for confounds (statsmodels or scipy.stats.partial_corr)
- Cohen's d effect size calculation for cluster comparison

### Archon Code Examples

*MCP not available. Using established patterns from H-E1/H-M1/H-M2/H-M3 experiments.*

Reusable components from prior phases:
- Calibration computation (H-E1): sequence log-prob, length-normalized
- Cluster assignment (H-E1): k-means with k=2
- Task type classification (H-M1/H-M2): Type A/B labels
- Feature extraction (H-M3): bidirectional feature scoring

### Exa GitHub Implementations

*MCP not available. Design uses standard scipy/sklearn patterns.*

Reference implementations:
- scipy.stats.pearsonr for correlation
- scipy.stats.pointbiserialr for point-biserial correlation
- statsmodels.stats.stattools for partial correlation
- numpy for Cohen's d calculation

### 🎯 Implementation Priority Assessment

**CRITICAL: Extend existing H-E1 calibration pipeline with feature correlation analysis**

**Recommended Implementation Path:**
- Primary: Extend H-E1 code with bidirectional feature scoring and correlation analysis
- Fallback: Standalone analysis loading H-E1 cluster results
- Justification: H-E1 already computed calibration clusters; H-M4 adds feature scoring and correlation

### Code Analysis (Serena MCP)

*MCP not available. Analysis based on Phase 2B specifications.*

Key code structure:
1. Load H-E1 cluster assignments (from h-e1/code/outputs/results.json)
2. Score each task on 3 bidirectional features
3. Compute correlation between feature score and inversion cluster membership
4. Control for confounds (length, topic, format, difficulty)
5. Compute effect sizes

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| Name | Combined RLHF Benchmarks |
| Type | standard |
| Source | TruthfulQA (817) + ETHICS justice (~500) + HHH single-turn (~200) |
| Total Samples | 2212 (from H-E1 validation) |
| Task Distribution | Type A: 1977 (correctness), Type B: 235 (user-state-modeling) |
| Cluster Distribution | Cluster 0: 1519, Cluster 1: 693 (inverted) |

**Loading Information** (for Phase 4 download):
- Method: Load from H-E1 outputs
- Identifier: h-e1/code/outputs/results.json
- Code:
```python
import json
with open("../h-e1/code/outputs/results.json") as f:
    h_e1_results = json.load(f)
cluster_assignments = h_e1_results["cluster_assignments"]
task_metadata = h_e1_results["task_metadata"]
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| Name | Llama-2-7B-Chat |
| Type | instruction-following LLM |
| Source | meta-llama/Llama-2-7b-chat-hf |
| Role | Primary model for correlation analysis |

**Validation Models:**
- Llama-2-13B-Chat (meta-llama/Llama-2-13b-chat-hf)
- Mistral-7B-Instruct (mistralai/Mistral-7B-Instruct-v0.2)

**Loading Information** (for Phase 4 download):
- Method: No new model loading required
- Identifier: N/A (analysis uses H-E1 outputs)
- Code: N/A

#### Proposed Model

**Architecture:** Analysis pipeline (no model training)

**Core Mechanism Implementation:**

```python
# Bidirectional Feature Scoring (3 features, score 0-3)
def score_bidirectional_features(task_text: str) -> dict:
    """
    Score task on 3 bidirectional features.
    Returns dict with individual scores and total (0-3).
    """
    features = {
        "user_belief_reference": 0,  # References user's beliefs/state
        "context_dependent": 0,       # Requires external context
        "hedged_answer": 0            # Answer requires hedging/nuance
    }
    
    # Feature 1: User belief reference
    belief_markers = ["you think", "you believe", "your view", "your opinion",
                      "you feel", "you assume", "you expect"]
    if any(m in task_text.lower() for m in belief_markers):
        features["user_belief_reference"] = 1
    
    # Feature 2: Context dependent
    context_markers = ["in this context", "given that", "assuming",
                       "depending on", "it depends", "situation"]
    if any(m in task_text.lower() for m in context_markers):
        features["context_dependent"] = 1
    
    # Feature 3: Hedged answer expected
    hedge_markers = ["might be", "could be", "possibly", "sometimes",
                     "it varies", "not always", "generally"]
    if any(m in task_text.lower() for m in hedge_markers):
        features["hedged_answer"] = 1
    
    features["total"] = sum([
        features["user_belief_reference"],
        features["context_dependent"],
        features["hedged_answer"]
    ])
    return features


# Correlation Analysis
def compute_correlations(
    cluster_labels: np.ndarray,  # 0 or 1 (inversion cluster)
    bidirectional_scores: np.ndarray,  # 0-3 feature scores
    confounds: dict  # length, topic, format, difficulty
) -> dict:
    """
    Compute correlation and effect sizes.
    """
    from scipy.stats import pointbiserialr, pearsonr
    import numpy as np
    
    # Point-biserial correlation (binary cluster vs continuous score)
    inversion_cluster = (cluster_labels == 1).astype(int)
    r_pb, p_pb = pointbiserialr(inversion_cluster, bidirectional_scores)
    
    # Cohen's d between clusters
    scores_inversion = bidirectional_scores[inversion_cluster == 1]
    scores_normal = bidirectional_scores[inversion_cluster == 0]
    pooled_std = np.sqrt(
        ((len(scores_inversion)-1) * np.std(scores_inversion, ddof=1)**2 +
         (len(scores_normal)-1) * np.std(scores_normal, ddof=1)**2) /
        (len(scores_inversion) + len(scores_normal) - 2)
    )
    cohens_d = (np.mean(scores_inversion) - np.mean(scores_normal)) / pooled_std
    
    # Partial correlation controlling for confounds
    # Using regression residualization approach
    from sklearn.linear_model import LinearRegression
    
    confound_matrix = np.column_stack([
        confounds["length"],
        confounds["difficulty"],
        # topic and format encoded as one-hot
    ])
    
    # Residualize inversion cluster
    reg_cluster = LinearRegression().fit(confound_matrix, inversion_cluster)
    cluster_resid = inversion_cluster - reg_cluster.predict(confound_matrix)
    
    # Residualize bidirectional score
    reg_score = LinearRegression().fit(confound_matrix, bidirectional_scores)
    score_resid = bidirectional_scores - reg_score.predict(confound_matrix)
    
    partial_r, partial_p = pearsonr(cluster_resid, score_resid)
    
    return {
        "point_biserial_r": r_pb,
        "point_biserial_p": p_pb,
        "cohens_d": cohens_d,
        "partial_r": partial_r,
        "partial_p": partial_p
    }
```

### Training Protocol

| Attribute | Value |
|-----------|-------|
| Training Required | No (analysis only) |
| Input | H-E1 cluster assignments + task texts |
| Processing | Feature scoring + correlation computation |
| Output | Correlation metrics + effect sizes |

### Evaluation

| Metric | Description | Threshold | Direction |
|--------|-------------|-----------|-----------|
| Point-biserial r | Correlation: inversion cluster ↔ bidirectional score | > 0.4 | Higher is better |
| Cohen's d | Effect size between clusters | > 0.3 | Higher is better |
| Partial r | Correlation after confound control | > 0.3 | Higher is better |

**Gate Condition:** (point_biserial_r > 0.4) OR (cohens_d > 0.3 AND partial_r > 0.3)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification analysis
- Library: scipy, sklearn, numpy
- Code:
```python
from scipy.stats import pointbiserialr, pearsonr
from sklearn.linear_model import LinearRegression
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing point_biserial_r, cohens_d, partial_r vs thresholds

#### Additional Figures (LLM Autonomous)

1. **Bidirectional Score Distribution by Cluster**: Violin plot or histogram
2. **Feature Breakdown**: Stacked bar chart of individual feature prevalence by cluster
3. **Scatter Plot**: Bidirectional score vs calibration score with cluster coloring
4. **Confound Control Visualization**: Partial regression plot

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least one of:
   - point_biserial_r > 0.4
   - (cohens_d > 0.3 AND partial_r > 0.3)

**Interpretation:**
- PASS: Bidirectional features correlate with calibration inversion, supporting the causal mechanism
- FAIL: Mechanism doesn't explain calibration patterns; consider alternative explanations

---

## Appendix: Reference Implementations

### A. Bidirectional Feature Definition (from Phase 2A)

| Feature | Definition | Detection Method |
|---------|------------|------------------|
| User Belief Reference | Task references user's beliefs, opinions, or mental state | Keyword matching |
| Context Dependent | Task requires external context not provided in prompt | Keyword matching |
| Hedged Answer | Correct answer requires nuance/hedging rather than definitive statement | Keyword matching |

### B. Confound Variables

| Confound | Source | Control Method |
|----------|--------|----------------|
| Length | Character count of task text | Included in partial correlation |
| Topic | Dataset source (TruthfulQA/ETHICS/HHH) | One-hot encoded |
| Format | Question format (multiple choice, open-ended) | One-hot encoded |
| Difficulty | Cross-model accuracy (from H-E1) | Continuous variable |

### C. Prior Phase Results Summary

| Phase | Key Metric | Value | Status |
|-------|-----------|-------|--------|
| H-E1 | Silhouette | 0.6016 | PASS |
| H-M1 | Overlap | 0.6475 | PASS |
| H-M2 | Rate Difference | 0.001 | PASS |
| H-M3 | Separation Score | 0.0236 | PASS |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19T07:45:00+00:00

### Workflow History for This Hypothesis

1. 2026-08-19T07:38:52: Hypothesis h-m4 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
2. 2026-08-19T07:45:00: Experiment design (02c_experiment_brief.md) generated

---

## Quality Validation

### Checklist

- [x] Dataset: Real standard dataset (TruthfulQA + ETHICS + HHH, N=2212)
- [x] Sufficient sample size: 2212 tasks (1977 Type A, 235 Type B)
- [x] Success criteria defined: r > 0.4, d > 0.3, partial r > 0.3
- [x] Confound controls specified: length, topic, format, difficulty
- [x] Builds on prior phases: Extends H-E1 cluster results
- [x] Pseudo-code provided: 10-30 lines
- [x] Loading code provided: Dataset, metrics
- [x] Visualization specified: Required + optional figures
- [ ] MCP sources cited: N/A (batch mode, no MCP)

---

*MCP Tools: Not available in batch mode*
*All specifications grounded in Phase 2A/2B design and prior hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*

# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under QA conditions, if we combine inverse entropy and consistency via linear fusion (α·(1-entropy) + β·consistency), then the combined score is more predictive than either alone, because the signals capture complementary failure modes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Template** - Tests signal combination hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 PASS: p=0.0083, AUROC=0.8081, d=1.19)
**Gate Status:** SHOULD_WORK (continue on failure with documentation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED, PASS)

### Gate Condition
SHOULD_WORK gate: If combined AUROC > max(entropy AUROC, consistency AUROC) by any margin, hypothesis is supported. Failure = document limitation and continue.

---

## Continuation Context

This experiment builds directly on H-M1 and H-M2 validated components:

### Previous Hypothesis Results

**H-M1 (Entropy as Uncertainty Proxy):**
- AUROC: 0.6454
- Pearson r: -0.2248 (entropy-correctness correlation)
- Mean entropy correct: 0.1104
- Mean entropy incorrect: 0.1342
- p-value: 0.0246

**H-M2 (Consistency as Stability Proxy):**
- AUROC: 0.8081
- Pearson r: -0.5427 (consistency-correctness negative correlation implies low consistency → incorrect)
- Mean consistency correct: 0.8958
- Mean consistency incorrect: 0.8265
- p-value: 0.0083
- Cohen's d: 1.1883

**Key Finding for H-M3:** Entropy-consistency correlation r = -0.543 (moderate negative). This supports fusion hypothesis — the signals are partially complementary, not redundant.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable — using established research knowledge*

**Score Combination Methods:**
1. **Linear Fusion:** score = α·metric1 + β·metric2 (simplest, interpretable)
2. **Learned Weighting:** Train weights on validation set
3. **Product Fusion:** score = metric1 × metric2 (multiplicative)
4. **Max/Min Fusion:** score = max(metric1, metric2)

**Best Practices:**
- Normalize both metrics to [0,1] before combining
- Use inverse entropy (1 - entropy) so higher = more confident
- Grid search α, β on held-out validation set (10-20% of data)
- Evaluate on separate test set to prevent overfitting

### Archon Code Examples

**Linear Score Combination Pattern:**
```python
# Standard linear fusion pattern
def linear_fusion(entropy, consistency, alpha=0.5, beta=0.5):
    # Convert entropy to confidence (inverse)
    confidence = 1.0 - normalize(entropy)
    consistency_norm = normalize(consistency)
    return alpha * confidence + beta * consistency_norm
```

### Exa GitHub Implementations

*MCP unavailable — using prior hypothesis implementations*

**Relevant Code from H-M1/H-M2:**
- `entropy.py`: TokenEntropyScorer — computes per-token entropy from logits
- `consistency.py`: SemanticConsistencyScorer — computes pairwise cosine similarity
- `stats.py`: Statistical analysis (t-test, AUROC, Cohen's d)

### 🎯 Implementation Priority Assessment

**CRITICAL: This is an internal combination experiment, not paper reproduction**

**Recommended Implementation Path:**
- Primary: Extend H-M2 pipeline with fusion scorer
- Fallback: N/A (simple extension)
- Justification: H-M1/H-M2 already provide entropy and consistency; this step combines them

### Code Analysis (Serena MCP)

*Serena unavailable — using H-M1/H-M2 code inspection*

**Integration Plan:**
1. Load existing entropy scores from H-M1
2. Load existing consistency scores from H-M2
3. Apply linear fusion with grid-searched weights
4. Evaluate combined AUROC against individual metrics

---

## Experiment Specification

### Dataset

**Name:** TriviaQA (validation set)
**Type:** standard
**Source:** mandarjoshi/trivia_qa (HuggingFace)
**Path:** trivia_qa/rc.nocontext
**Split Strategy:**
- Validation holdout: 10% (~1,100 questions) for α,β tuning
- Test set: 90% (~9,900 questions) for final evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: mandarjoshi/trivia_qa
- Code: `load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation")`

### Models

#### Baseline Model

**Architecture:** Llama-2-7B-chat
**Source:** meta-llama/Llama-2-7b-chat-hf
**Role:** Generate responses, provide logits for entropy computation

This experiment does NOT modify the model — it operates on model outputs.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-chat-hf
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")`

**Embedding Model (for consistency):**
- Method: sentence-transformers
- Identifier: all-MiniLM-L6-v2
- Code: `SentenceTransformer("all-MiniLM-L6-v2")`

#### Proposed Model

**Architecture:** Linear fusion scorer (not a neural model)

**Core Mechanism Implementation:**

```python
# Core Mechanism: LinearFusionScorer
# Purpose: Combine entropy and consistency for hallucination prediction

import numpy as np
from sklearn.metrics import roc_auc_score

class LinearFusionScorer:
    """
    Combine inverse entropy and consistency via linear fusion.
    Score = alpha * (1 - normalized_entropy) + beta * normalized_consistency
    """
    def __init__(self, alpha: float = 0.5, beta: float = 0.5):
        self.alpha = alpha
        self.beta = beta
    
    def normalize(self, values: np.ndarray) -> np.ndarray:
        """Min-max normalize to [0, 1]."""
        min_v, max_v = values.min(), values.max()
        if max_v - min_v < 1e-8:
            return np.zeros_like(values)
        return (values - min_v) / (max_v - min_v)
    
    def compute_scores(self, entropy: np.ndarray, consistency: np.ndarray) -> np.ndarray:
        """
        Args:
            entropy: (N,) per-question entropy values
            consistency: (N,) per-question consistency values
        Returns:
            (N,) combined scores (higher = more likely correct)
        """
        # Invert entropy: low entropy = high confidence
        confidence = 1.0 - self.normalize(entropy)
        consistency_norm = self.normalize(consistency)
        
        # Linear fusion
        combined = self.alpha * confidence + self.beta * consistency_norm
        return combined


def grid_search_weights(entropy, consistency, labels, alpha_range, beta_range):
    """Find optimal alpha, beta on validation set."""
    best_auroc = 0.0
    best_alpha, best_beta = 0.5, 0.5
    
    for alpha in alpha_range:
        for beta in beta_range:
            scorer = LinearFusionScorer(alpha=alpha, beta=beta)
            scores = scorer.compute_scores(entropy, consistency)
            auroc = roc_auc_score(labels, scores)
            if auroc > best_auroc:
                best_auroc = auroc
                best_alpha, best_beta = alpha, beta
    
    return best_alpha, best_beta, best_auroc
```

### Training Protocol

**Note:** This is NOT a training experiment. The "training" phase is weight grid search.

**Grid Search Protocol:**
- α range: [0.0, 0.1, 0.2, ..., 1.0] (11 values)
- β range: [0.0, 0.1, 0.2, ..., 1.0] (11 values)
- Total combinations: 121
- Optimization metric: AUROC on validation holdout

**Fixed Parameters:**
- Seed: 42
- N responses per question: 10 (from H-M1/H-M2)
- Temperature: 0.7 (from H-M1/H-M2)

**Data Flow:**
1. Load entropy values from H-M1 results (or recompute)
2. Load consistency values from H-M2 results (or recompute)
3. Split into validation (10%) and test (90%)
4. Grid search on validation
5. Evaluate on test

### Evaluation

**Primary Metrics:**
- AUROC (combined score vs ground-truth correctness)
- AUROC_improvement = AUROC_combined - max(AUROC_entropy, AUROC_consistency)

**Statistical Tests:**
- DeLong test for AUROC comparison (combined vs best single)
- Bootstrap confidence intervals for improvement estimate

**Success Criteria (PoC):**
- Primary: AUROC_combined > max(AUROC_entropy, AUROC_consistency) by ANY margin
- Secondary: Improvement visible with default α=β=0.5 (no extensive tuning)

**Expected Baseline Performance:**
- Entropy-only AUROC: ~0.65 (from H-M1)
- Consistency-only AUROC: ~0.81 (from H-M2)
- Target combined AUROC: >0.81

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (correct vs incorrect)
- Library: sklearn.metrics
- Code: `from sklearn.metrics import roc_auc_score, roc_curve`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing AUROC for entropy-only, consistency-only, and combined

#### Additional Figures (LLM Autonomous)
- ROC curves overlay (3 curves: entropy, consistency, combined)
- Weight heatmap: AUROC as function of (α, β)
- Scatter plot: entropy vs consistency, colored by correctness

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## Ablation Study Design

| Variant | α | β | Purpose |
|---------|---|---|---------|
| Entropy-only | 1.0 | 0.0 | Single metric baseline |
| Consistency-only | 0.0 | 1.0 | Single metric baseline |
| Equal weights | 0.5 | 0.5 | Simple combination |
| Optimal | grid search | grid search | Best performing |

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- [ ] `mechanism_exists`: Linear fusion scorer implemented
- [ ] `mechanism_isolatable`: Can run combined vs individual metrics
- [ ] `baseline_measurable`: Individual AUROCs computable

### Architecture Compatibility
- Linear fusion operates on scalar scores, no model modification needed
- Requires: entropy values (from H-M1 pipeline), consistency values (from H-M2 pipeline)

### Activation Indicators
- `mechanism_log_message`: "Combined score computed: α={alpha}, β={beta}, AUROC={value}"
- `tensor_shape_change`: N/A (scalar scores)
- `metric_delta_expected`: AUROC_combined > max(AUROC_entropy, AUROC_consistency)

### Verification Code
```python
def verify_mechanism(entropy, consistency, labels):
    """Verify linear fusion improves over single metrics."""
    from sklearn.metrics import roc_auc_score
    
    # Baseline AUROCs
    auroc_entropy = roc_auc_score(labels, -entropy)  # Negative: low entropy = correct
    auroc_consistency = roc_auc_score(labels, consistency)
    
    # Combined AUROC (default weights)
    scorer = LinearFusionScorer(alpha=0.5, beta=0.5)
    combined = scorer.compute_scores(entropy, consistency)
    auroc_combined = roc_auc_score(labels, combined)
    
    improvement = auroc_combined - max(auroc_entropy, auroc_consistency)
    
    print(f"Entropy AUROC: {auroc_entropy:.4f}")
    print(f"Consistency AUROC: {auroc_consistency:.4f}")
    print(f"Combined AUROC: {auroc_combined:.4f}")
    print(f"Improvement: {improvement:+.4f}")
    
    return improvement > 0
```

### Success Thresholds
- `hypothesis_support_threshold`: AUROC_combined > max(single) by > 0
- `hypothesis_support_metric`: AUROC improvement

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `AUROC_combined > max(AUROC_entropy, AUROC_consistency)`

**Gate Decision:**
- PASS: Combined score outperforms both individual metrics
- FAIL: Document as limitation, proceed to H-M4 with best available approach

---

## Appendix: Reference Implementations

### From H-M1 (Entropy)
- `entropy.py`: Token entropy computation from logits
- Key function: `TokenEntropyScorer.compute_entropy()`

### From H-M2 (Consistency)
- `consistency.py`: Semantic consistency via embedding similarity
- Key function: `SemanticConsistencyScorer.compute_consistency()`

### Score Fusion Literature
- Ensemble methods in uncertainty estimation
- Linear opinion pools (Genest & Zidek, 1986)
- Score-level fusion in biometrics

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: Hypothesis h-m3 set to IN_PROGRESS
- 2026-08-19: Phase 2C experiment design started

---

*MCP Tools Used: None (unavailable — fallback to prior hypothesis code)*
*All specifications grounded in H-M1/H-M2 validated implementations*
*Next Phase: Phase 3 - Implementation Planning*

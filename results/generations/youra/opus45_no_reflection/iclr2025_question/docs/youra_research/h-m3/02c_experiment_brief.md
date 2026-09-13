# Experiment Design: H-M3

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Linear probe learns hidden state to correctness mapping with AUROC >= 0.70
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Validates linear separability of correctness signal in hidden state space.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 validated: inverted-U pattern confirmed, peak at L15/50% depth)
**Gate Status:** SHOULD_WORK (AUROC >= 0.70)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Middle layers encode semantic knowledge - VALIDATED)

### Gate Condition
- **Primary:** Training loss converges (not stuck at random)
- **Secondary:** Validation AUROC >= 0.70
- **Fallback:** If linear fails, test 2-layer MLP variant

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- **Status:** VALIDATED (PASS)
- **Peak Layer:** L15 (50% depth)
- **Peak AUROC:** 0.8520
- **Inverted-U Pattern:** Confirmed
- **Key Finding:** L60% AUROC (0.8223) > L100% AUROC (0.7664)

**Reuse from H-M2:**
- Optimal layer depth: L15 (50% depth) for probe training
- Hidden state extraction pipeline (validated in H-M1)
- Dataset preprocessing (TriviaQA with train/val split)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches in Archon KB for linear probe training. General PyTorch training patterns available.

### Archon Code Examples

Standard PyTorch training patterns found (Adam optimizer, gradient descent, loss tracking).

### Exa GitHub Implementations

**Primary Sources Found:**

1. **OATML/semantic-entropy-probes** (MIT License)
   - URL: https://github.com/oatml/semantic-entropy-probes
   - Purpose: Linear probes to predict semantic entropy from hidden states
   - Key insight: SEPs achieve 0.85+ correlation with multi-sample SE
   - Training: LogisticRegression with SGD, single forward pass

2. **OpenInterpretability/openinterp-mcp** - probes.py
   - Linear classifier on residual-stream activations
   - `score(act) = sigmoid(act @ direction + bias)`
   - AUROC computation via sklearn.metrics.roc_auc_score
   - Baseline methods: random_feature_baseline, shuffled_label_baseline

3. **aragorn-w/linear-probe** (TransformerLens)
   - Linear probes for sentiment classification on GPT-2
   - `P(y=1|h_l) = sigmoid(w^T h_l + b)`
   - Binary cross-entropy loss with Adam optimizer
   - Word-level train/test split to prevent memorization

4. **concept-probes** PyPI package
   - `train_probe()` with layer sweep, AUROC reporting
   - LogisticRegression with C=1e-3, max_iter=1000, class_weight='balanced'
   - 5-fold StratifiedKFold cross-validation

5. **Hallucination Detection Paper (2026)**
   - "Hallucination Is Linearly Decodable from Mid-Layer Hidden States"
   - Linear probe achieves 0.904-1.000 AUROC on truthfulness benchmarks
   - Peak layers: 13-18 of 32 for Llama/Mistral models
   - MLP probes rarely exceed linear by >0.01 AUROC

### 🎯 Implementation Priority Assessment

**CRITICAL: Author's official implementation prioritized**

| Priority | Source | Rationale |
|----------|--------|-----------|
| 1 | OATML/semantic-entropy-probes | Official SEP implementation, same problem domain |
| 2 | concept-probes | Production-ready package, sklearn backend |
| 3 | OpenInterpretability probes.py | Clean implementation, AUROC + baselines |

**Recommended Implementation Path:**
- Primary: sklearn LogisticRegression (proven in SEP, concept-probes)
- Fallback: 2-layer MLP if linear AUROC < 0.70
- Justification: Research shows linear probes match MLP within 0.01 AUROC; simpler model preferred

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze. Implementation based on research findings.

---

## Experiment Specification

### Dataset

**Dataset:** TriviaQA + Natural Questions
**Type:** standard
**Source:** HuggingFace datasets

| Split | Size | Purpose |
|-------|------|---------|
| Train | 9,500 | Probe training |
| Validation | 1,700 | AUROC evaluation |

**Preprocessing:**
- Use hidden states from H-M1 extraction pipeline
- Extract from optimal layer L15 (from H-M2 validation)
- Normalize: StandardScaler (mean=0, std=1)
- Labels: Binary (correct=1, incorrect=0) based on exact-match

**Loading Information** (for Phase 4 download):
- Method: Reuse from H-E1/H-M1/H-M2 (already extracted)
- Identifier: Pre-computed hidden states at L15
- Code:
```python
# Load pre-extracted hidden states from H-M2
hidden_states = torch.load(f"{hypothesis_folder}/../h-m2/hidden_states_l15.pt")
labels = torch.load(f"{hypothesis_folder}/../h-m2/correctness_labels.pt")
```

### Models

#### Baseline Model

**Architecture:** Random direction baseline
**Purpose:** Establish floor performance (AUROC ≈ 0.50)

**Configuration:**
- Random direction in hidden state space (d=4096 for Llama-3-8B)
- Apply to real activations: `scores = activations @ random_direction`
- Multiple seeds (5) for confidence interval

**Loading Information** (for Phase 4 download):
- Method: numpy random
- Identifier: N/A (generated)
- Code:
```python
rng = np.random.default_rng(seed=42)
random_dir = rng.standard_normal(d_model).astype(np.float32)
random_dir /= np.linalg.norm(random_dir) + 1e-8
```

#### Proposed Model

**Architecture:** Linear Probe (Logistic Regression)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Linear Correctness Probe
# Based on: SEP (Kossen 2024), concept-probes, OpenInterpretability

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import numpy as np

class LinearCorrectnessProbe:
    """
    Linear probe mapping hidden states → correctness probability.
    Input: Hidden states (N, d_model) from layer L15
    Output: Correctness probability (N,)
    """
    def __init__(self, C=1e-3, max_iter=2000):
        self.scaler = StandardScaler()
        self.clf = LogisticRegression(
            C=C,
            max_iter=max_iter,
            class_weight='balanced',
            solver='lbfgs'
        )
    
    def fit(self, X_train, y_train):
        """Train probe on hidden states with correctness labels."""
        X_scaled = self.scaler.fit_transform(X_train)
        self.clf.fit(X_scaled, y_train)
        return self
    
    def predict_proba(self, X):
        """Return correctness probabilities."""
        X_scaled = self.scaler.transform(X)
        return self.clf.predict_proba(X_scaled)[:, 1]
    
    def evaluate(self, X_val, y_val):
        """Compute AUROC on validation set."""
        probs = self.predict_proba(X_val)
        return roc_auc_score(y_val, probs)

# Training
probe = LinearCorrectnessProbe(C=1e-3, max_iter=2000)
probe.fit(X_train, y_train)
auroc = probe.evaluate(X_val, y_val)
# Success: auroc >= 0.70
```

### Training Protocol

**Optimizer:** L-BFGS (sklearn default for LogisticRegression)
**Regularization:** L2 with C=1e-3 (inverse regularization strength)
**Max Iterations:** 2000
**Class Weighting:** balanced (handle class imbalance)
**Seeds:** 1 (fixed at 42)

**Source:** SEP paper, concept-probes package

**Convergence Criteria:**
- Loss decreases over iterations (not stuck)
- Solver converges within max_iter

### Evaluation

**Primary Metrics:**
- AUROC (Area Under ROC Curve): Main success metric
- Accuracy: Secondary metric

**Success Criteria:**
- AUROC >= 0.70 (gate threshold)
- AUROC > random baseline (0.50 ± 0.02)

**Expected Performance (from research):**
- SEP paper: 0.85+ correlation with semantic entropy
- Hallucination paper: 0.904-1.000 AUROC on truthfulness
- H-M2 found peak AUROC 0.852 at L15 → expect similar for trained probe

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, accuracy_score
auroc = roc_auc_score(y_true, y_probs)
accuracy = accuracy_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUROC threshold (0.70) vs achieved AUROC

#### Additional Figures (LLM Autonomous)
- Training loss curve (if using iterative training)
- ROC curve with AUC annotation
- Confusion matrix at optimal threshold
- Comparison: Linear probe vs random baseline

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - LogisticRegression is a standard sklearn model
- **mechanism_isolatable:** True - Probe is separate module from hidden state extraction
- **baseline_measurable:** True - Random direction baseline provides clear floor

### Architecture Compatibility
- **Input:** Hidden states from L15 with shape (N, 4096)
- **Output:** Probability scores (N,)
- **Compatibility:** sklearn models accept numpy arrays directly

### Activation Indicators
- **mechanism_log_message:** "Probe training completed with {n_iter} iterations"
- **tensor_shape_change:** Input (N, 4096) → Output (N,) probabilities
- **metric_delta_expected:** AUROC should exceed 0.50 (random) by at least 0.20

### Mechanism Verification Code
```python
def verify_mechanism(probe, X_val, y_val):
    """Verify probe mechanism is working."""
    # 1. Check probe learned non-trivial weights
    weights = probe.clf.coef_[0]
    weight_norm = np.linalg.norm(weights)
    assert weight_norm > 1e-6, "Weights collapsed to zero"
    
    # 2. Check predictions are not constant
    probs = probe.predict_proba(X_val)
    assert probs.std() > 0.01, "Predictions are constant"
    
    # 3. Check AUROC exceeds random
    auroc = roc_auc_score(y_val, probs)
    assert auroc > 0.55, f"AUROC {auroc} not significantly above random"
    
    return {"weight_norm": weight_norm, "pred_std": probs.std(), "auroc": auroc}
```

### Success Criteria
- **hypothesis_support_threshold:** AUROC >= 0.70
- **hypothesis_support_metric:** roc_auc_score(y_val, probe.predict_proba(X_val))

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `probe_auroc > baseline_auroc` (effect direction)
3. `probe_auroc >= 0.70` (gate threshold)

**Fallback Protocol (if linear fails):**
```python
# If linear AUROC < 0.70, test MLP variant
from sklearn.neural_network import MLPClassifier

mlp_probe = MLPClassifier(
    hidden_layer_sizes=(256,),  # Single hidden layer
    max_iter=500,
    early_stopping=True
)
mlp_probe.fit(X_train_scaled, y_train)
mlp_auroc = roc_auc_score(y_val, mlp_probe.predict_proba(X_val_scaled)[:, 1])
```

---

## Appendix: Reference Implementations

### Primary References

1. **Semantic Entropy Probes (SEP)**
   - Paper: Kossen et al. (2024) "Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs"
   - Code: https://github.com/oatml/semantic-entropy-probes
   - Key finding: Linear probes approximate multi-sample SE with 0.85+ correlation

2. **Hallucination Is Linearly Decodable**
   - Paper: Aiersilan (2026)
   - Key finding: Linear probe achieves 0.904-1.000 AUROC, peak at layers 13-18/32

3. **No Answer Needed: Question-Only Linear Probes**
   - Paper: Moreno et al. (2025)
   - Key finding: Linear probes predict correctness from pre-answer activations

### Code Snippets Used

**From OpenInterpretability probes.py:**
```python
def apply_probe(activations, direction, bias):
    logits = activations @ direction + bias
    return 1.0 / (1.0 + np.exp(-logits))

def auroc(scores, labels):
    return float(roc_auc_score(labels, scores))
```

**From concept-probes:**
```python
clf = LogisticRegression(C=1e-3, max_iter=1000, class_weight='balanced')
clf.fit(X_train, y_train)
auroc = roc_auc_score(y_val, clf.predict_proba(X_val)[:, 1])
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- H-M3 set to IN_PROGRESS: 2026-08-18T17:43:45
- Phase 2C experiment design: IN_PROGRESS

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

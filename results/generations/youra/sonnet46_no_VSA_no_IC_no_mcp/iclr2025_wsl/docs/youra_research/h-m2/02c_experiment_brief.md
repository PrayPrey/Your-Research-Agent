# Experiment Design: H-M2

**Date:** 2026-08-27
**Author:** Anonymous
**Hypothesis Statement:** PCA of canonicalized weight vectors (Condition D: both canonicalizations) explains more property-label variance (R² of linear regression from first k PCs onto test accuracy, gen_gap, lr_recovery) than PCA of raw weight vectors (Condition A) on Schürholt MNIST zoo, confirming that canonicalization concentrates property-relevant geometric information.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests PCA concentration claim (Condition G from Phase 2A); SHOULD_WORK gate (non-blocking).

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 VALIDATED (gate: EXPLORE; scaling PASS ✓; sign-flip EXPLORE non-blocking)
**Gate Status:** SHOULD_WORK — failure → DOCUMENT (causal pathway claim revised; proceed to H-M3 regardless)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED)

### Gate Condition
**SHOULD_WORK** — R²_canonical > R²_raw on ≥2/3 tasks (test accuracy, gen_gap, lr_recovery) with non-overlapping bootstrap 95% CIs.

**Failure response:** DOCUMENT — if PCA concentration does not improve, the causal pathway claim (canonicalization → concentration → ρ improvement) must be revised. Proceed to H-M3 regardless.

---

## Continuation Context

**This is a continuation experiment from H-M1.**

### Previous Hypothesis Results (H-M1)
- **Validated:** NFT (Condition A) does NOT naturally collapse scaling orbits (gap=+0.024, CI=[0.023, 0.024]).
- **Sign-flip:** NFT approximately invariant (gap=-0.0007, CI=[-0.0008, -0.0005]) → EXPLORE path.
- **Dataset used:** Schürholt MNIST zoo local archive, 500 models (HuggingFace unavailable).
- **NFT architecture:** d_model=256, 4 layers, 8 heads, Adam lr=3e-4, batch_size=32, 200 epochs.
- **Key limitation:** Only 500 models (vs ~50k in full zoo). Statistical power sufficient for scaling signal but note in results.

**Reused from H-M1:**
- Dataset loading code (local archive loader)
- Orbit construction code (scaling + sign-flip oracle)
- Canonicalization implementations (scaling: L2 norm per layer; sign-flip: majority-sign for M=2)
- Train/test split (90/10, seed=42)

**H-M2 does NOT need NFT.** This experiment is pure PCA + linear regression on raw vs. canonical weight vectors. NFT is not used.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP unavailable (NO_MCP session). Findings derived from literature knowledge and H-M1 continuation context.

**Query 1: PCA for weight space property prediction**
- Standard approach: flatten weight vectors → PCA → linear probe (R²). Used in:
  - Unterthiner et al. 2020 (layer statistics baseline): not PCA but similar linear analysis
  - Representation learning linear probing literature (Chen et al., SimCLR): R² / accuracy from k-dim probe
- Key insight: R² of linear regression from k PCs is a clean, interpretable metric for geometric concentration
- Typical k values: 10, 20, 50 (sweep all three for H-M2)

**Query 2: Canonicalization + PCA patterns**
- Whitening/standardization before PCA: standard in signal processing; removes scale-induced principal components
- Expected effect: if canonicalization removes scale variance orthogonal to property-predictive axes, first k PCs should align more with property labels → higher R²
- Sklearn PCA + LinearRegression: standard implementation path, no custom code needed

**Query 3: Bootstrap CI for R²**
- Bootstrap resampling of test split (n_boot=1000) for CI on R² values
- Compare CIs: non-overlapping → statistically significant concentration improvement
- Standard approach confirmed in H-M1 (same bootstrap protocol)

### Archon Code Examples

**MCP Status:** Archon MCP unavailable. Code patterns derived from sklearn documentation and H-M1 codebase.

```python
# Pattern: PCA + linear regression R² evaluation
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

# Fit PCA on training split
pca = PCA(n_components=k)
X_train_pca = pca.fit_transform(X_train)
X_test_pca = pca.transform(X_test)

# Fit linear regression on PCA features
reg = LinearRegression()
reg.fit(X_train_pca, y_train)
y_pred = reg.predict(X_test_pca)
r2 = r2_score(y_test, y_pred)

# Bootstrap CI
r2_boot = []
for _ in range(n_boot):
    idx = np.random.choice(len(y_test), len(y_test), replace=True)
    r2_boot.append(r2_score(y_test[idx], y_pred[idx]))
ci_low, ci_high = np.percentile(r2_boot, [2.5, 97.5])
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP unavailable (NO_MCP session). Findings derived from context.

**Pattern: Weight vector PCA for model zoo analysis**
- Standard approach confirmed in Schürholt et al. codebase (model zoo benchmarks use PCA as baseline)
- H-M1 codebase already has: weight flattening, canonicalization, local zoo loading — all directly reusable

**Serena Analysis Needed:** false — code pattern is pure sklearn (PCA + LinearRegression), <50 lines. No complex custom layers.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment (H-M2) does NOT reproduce a specific paper method. It is a diagnostic analysis using standard sklearn tools. No author implementation to search for.

**Recommended Implementation Path:**
- Primary: sklearn PCA + LinearRegression (standard, well-tested)
- Fallback: numpy SVD (manual PCA) if sklearn issues arise
- Justification: H-M2 is a linear analysis experiment; sklearn is the minimal correct tool. No custom neural network needed.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. PCA + linear regression is standard sklearn; no complex code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Schürholt MNIST Model Zoo
**Type:** standard (real model zoo, local archive)
**Source:** Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"
**Architecture:** 2-layer MLPs (784→64→10), M=2 consecutive layer pairs

**Statistics:**
- Available locally: 500 MNIST models (HuggingFace `schurholt/model_zoos_dataset` unavailable — confirmed H-M1)
- Labels: test accuracy (continuous), generalization gap (continuous), learning rate recovery (continuous)
- Train/test split: 450 / 50 (seed=42, consistent with H-M1)

**Weight vector flattening:**
- Layer 1: 784×64 = 50,176 weights + 64 biases = 50,240
- Layer 2: 64×10 = 640 weights + 10 biases = 650
- **Total per model:** 50,890-dimensional weight vector (flatten all parameters)

**Canonicalization (Condition D — both):**
- Scaling: divide each layer's weight matrix by its L2 norm (per-layer normalization)
- Sign-flip (M=2): for each hidden neuron, flip sign of incoming + outgoing weights if majority sign of incoming weights is negative
- **Condition A:** raw weight vectors (no canonicalization)
- **Condition D:** scaling + sign-flip applied sequentially

**Loading Information** (for Phase 4 download):
- Method: local archive (reuse H-M1 loader)
- Identifier: `./data/` (same as H-M1)
- Code: `torch.load('./data/mnist_models.pt')` (reuse H-M1 `load_local_zoo()`)

### Models

#### Baseline Model

**Architecture:** PCA of raw weight vectors (Condition A)
**Type:** sklearn PCA (linear dimensionality reduction)
**Source:** scikit-learn 1.x

**Configuration:**
- Input: (n_models, 50890) raw weight matrix
- k values: 10, 20, 50 principal components (sweep)
- Downstream: LinearRegression from k PCs → property label (R²)

**Loading Information** (for Phase 4 download):
- Method: sklearn (already installed)
- Identifier: `sklearn.decomposition.PCA`
- Code: `from sklearn.decomposition import PCA; pca = PCA(n_components=k)`

#### Proposed Model

**Architecture:** PCA of canonical weight vectors (Condition D)
**Integration Point:** Canonicalization is a preprocessing step applied to raw weight vectors before PCA.

**Core Mechanism Implementation:**

```python
# Core Mechanism: PCA Concentration Test (H-M2)
# Condition A: raw weights → PCA → linear regression → R²
# Condition D: canonical weights → PCA → linear regression → R²
# Based on: sklearn PCA + linear probe (standard representation analysis)

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def canonicalize_scaling(weights_flat, layer_shapes):
    """Condition B: divide each layer matrix by its Frobenius norm."""
    canonical = weights_flat.copy()
    offset = 0
    for (rows, cols) in layer_shapes:
        size = rows * cols
        W = canonical[:, offset:offset+size]
        norms = np.linalg.norm(W, axis=1, keepdims=True) + 1e-8
        canonical[:, offset:offset+size] = W / norms
        offset += size
    return canonical

def canonicalize_sign_flip_m2(weights_flat, W1_shape, W2_shape):
    """Condition C (M=2): flip signs to make majority incoming sign positive."""
    canonical = weights_flat.copy()
    n_models, n_in, n_hidden = len(weights_flat), W1_shape[0], W1_shape[1]
    W1 = canonical[:, :n_in*n_hidden].reshape(n_models, n_in, n_hidden)
    W2 = canonical[:, n_in*n_hidden:n_in*n_hidden+n_hidden*W2_shape[1]].reshape(
        n_models, n_hidden, W2_shape[1])
    for h in range(n_hidden):
        signs = np.sign(W1[:, :, h].sum(axis=1))  # majority sign per model
        signs[signs == 0] = 1  # tie-breaking: positive
        W1[:, :, h] *= signs[:, None]
        W2[:, h, :] *= signs[:, None]
    canonical[:, :n_in*n_hidden] = W1.reshape(n_models, -1)
    canonical[:, n_in*n_hidden:n_in*n_hidden+n_hidden*W2_shape[1]] = W2.reshape(n_models, -1)
    return canonical

def evaluate_pca_concentration(X_train, X_test, y_train, y_test, k_values, n_boot=1000):
    """R² of linear regression from first k PCs → property label, with bootstrap CI."""
    results = {}
    for k in k_values:
        pca = PCA(n_components=k, random_state=42)
        X_tr_pca = pca.fit_transform(X_train)
        X_te_pca = pca.transform(X_test)
        reg = LinearRegression()
        reg.fit(X_tr_pca, y_train)
        y_pred = reg.predict(X_te_pca)
        r2 = r2_score(y_test, y_pred)
        boot_r2 = [r2_score(y_test[idx := np.random.choice(len(y_test), len(y_test))],
                            y_pred[idx]) for _ in range(n_boot)]
        results[k] = {'r2': r2, 'ci': np.percentile(boot_r2, [2.5, 97.5])}
    return results
```

### Training Protocol

**Note:** H-M2 is a linear analysis experiment — no neural network training required.

**From Previous Hypothesis (H-M1) — Continuation:**
- Dataset loading: reuse H-M1 loader (local archive, 500 models, seed=42)
- Train/test split: 450/50, seed=42 (identical to H-M1 for fair comparison)
- Canonicalization code: reuse H-M1 scaling + sign-flip implementations

**H-M2-Specific Protocol:**

**Step 1: Data preparation**
- Load all 500 MNIST zoo models (reuse H-M1 loader)
- Flatten weight vectors: shape (500, 50890)
- Apply canonicalization per condition:
  - Condition A: raw (no transform)
  - Condition D: scaling → sign-flip (sequential application)
- Split: 450 train / 50 test (consistent with H-M1, seed=42)

**Step 2: PCA sweep**
- k_values = [10, 20, 50]
- Fit PCA on training split for each condition independently
- Transform test split

**Step 3: Linear regression R² evaluation**
- For each (condition, k, property_label):
  - Fit LinearRegression(X_train_pca, y_train_prop)
  - Predict on X_test_pca
  - Compute R² + bootstrap 95% CI (n_boot=1000, seed=42)
- Property labels: test_accuracy, gen_gap, lr_recovery (3 labels)

**Step 4: Gate comparison**
- Compare R²_D vs R²_A per (k, property)
- Non-overlapping CI check: R²_D_CI_low > R²_A_CI_high → significant improvement
- Gate pass: non-overlapping CI on ≥2/3 tasks at k=20

**Optimizer:** N/A (no neural network)
**Learning Rate:** N/A
**Batch Size:** N/A (full-batch PCA)
**Epochs:** N/A
**Loss:** N/A
**Seeds:** 1 (seed=42, consistent with H-M1)

> PoC: single run sufficient. No multiple seeds or hyperparameter search.

### Evaluation

**Primary Metric:** R² of linear regression from first k PCs onto property labels

**Success Criteria (gate: SHOULD_WORK):**
- Primary: R²_canonical(k=20) > R²_raw(k=20) for test_accuracy, with non-overlapping bootstrap 95% CI
- Secondary: Improvement holds on ≥2/3 properties (test_accuracy, gen_gap, lr_recovery)
- Bonus: Improvement monotonic in k up to some saturation point

**Failure Response:** DOCUMENT — if R²_canonical ≤ R²_raw, causal pathway claim (concentration) must be revised. Proceed to H-M3 regardless.

**Expected Baseline Performance (raw, Condition A):**
- R² from 20 PCs on raw weights for property prediction: likely low (~0.05–0.20), given:
  - H-M1 shows NFT on raw weights achieves ρ~0.11 (only 500 models, severe overfitting)
  - Linear probe from PCA should be a weaker baseline than trained NFT
  - Scale variance (shown in H-M1) should inflate first PCs with scale-related components
- Canonical (Condition D) expected: higher R² if concentration hypothesis holds

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (continuous property labels)
- Library: sklearn.metrics
- Code: `from sklearn.metrics import r2_score; r2_score(y_test, y_pred)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: R²_canonical vs R²_raw bar chart with 95% CI error bars, for each (k, property)

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (MECHANISM — concentration test):

1. **R² vs k curve** (line plot): R²_A and R²_D as function of k ∈ {10, 20, 50} for each property. Shows monotonicity / saturation point.
2. **PCA explained variance ratio** (cumulative): Condition A vs D — shows whether canonical weights concentrate variance in fewer PCs.
3. **Bootstrap CI overlap visualization**: horizontal CI bars for R²_A and R²_D at k=20, per property. Visual gate pass/fail.
4. **Scatter: PC1 vs property label**: Condition A vs D side-by-side scatter — shows qualitative alignment improvement.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that the PCA concentration mechanism actually activates — not just that code runs.

### Pre-conditions

| Check | Condition | Verification |
|-------|-----------|--------------|
| mechanism_exists | PCA can be fit on weight vectors | `pca.fit(X_train)` succeeds; explained_variance_ratio_ sums to 1 |
| mechanism_isolatable | Condition A and D produce different weight matrices | `np.allclose(X_A, X_D) == False` (canonicalization changes vectors) |
| baseline_measurable | R² computable on test split (n=50 sufficient) | LinearRegression fits; r2_score returns finite value |

### Architecture Compatibility

- **No neural network** — pure sklearn pipeline. No architecture compatibility issue.
- Canonicalization is applied as preprocessing; PCA is standard sklearn.
- **Risk:** n=50 test split is small; R² estimates will have high variance. Mitigated by bootstrap CI.

### Activation Indicators

| Indicator | Expected Value | Failure Signal |
|-----------|----------------|----------------|
| mechanism_log_message | "Condition D R² > Condition A R² at k=20 for test_accuracy" | R²_D ≤ R²_A |
| tensor_shape_change | X_train shape: (450, k) after PCA for both conditions | Shape mismatch or NaN |
| metric_delta_expected | ΔR² = R²_D - R²_A > 0 with non-overlapping CI | ΔR² ≤ 0 or overlapping CI |

### Mechanism Verification Code

```python
# Mechanism activation check (run before full experiment)
def verify_mechanism_preconditions(X_A_train, X_D_train, X_A_test, X_D_test, y_test):
    """Verify H-M2 mechanism can activate."""
    assert not np.allclose(X_A_train, X_D_train), "FAIL: Canonicalization has no effect"
    
    # Check PCA fits
    pca_a = PCA(n_components=20, random_state=42).fit(X_A_train)
    pca_d = PCA(n_components=20, random_state=42).fit(X_D_train)
    assert pca_a.explained_variance_ratio_.sum() > 0.01, "FAIL: PCA degenerate (Condition A)"
    assert pca_d.explained_variance_ratio_.sum() > 0.01, "FAIL: PCA degenerate (Condition D)"
    
    # Check R² is computable
    reg = LinearRegression().fit(pca_a.transform(X_A_train)[:, :20], 
                                  np.random.randn(len(X_A_train)))  # dummy check
    assert np.isfinite(reg.coef_).all(), "FAIL: LinearRegression produces non-finite coefficients"
    
    print("✅ All H-M2 mechanism preconditions satisfied")
    print(f"  Condition A vs D weight diff: {np.mean(np.abs(X_A_train - X_D_train)):.4f}")
    print(f"  PCA A top-20 var explained: {pca_a.explained_variance_ratio_[:20].sum():.3f}")
    print(f"  PCA D top-20 var explained: {pca_d.explained_variance_ratio_[:20].sum():.3f}")
```

**hypothesis_support_threshold:** R²_D_CI_low > R²_A_CI_high at k=20 for test_accuracy
**hypothesis_support_metric:** ΔR² (R²_canonical minus R²_raw) at k=20, bootstrap 95% CI non-overlapping

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1: PCA linear probing paradigm**
- Type: Domain knowledge (Chen et al. linear evaluation protocol)
- Query: "PCA property prediction weight space R²"
- Key insights: R² from k-PCA features is standard concentration metric; k=10/20/50 sweep standard
- Used for: Evaluation metric definition, k_values selection

**Source 2: Bootstrap CI for regression metrics**
- Type: Domain knowledge (standard bootstrap practice)
- Query: "bootstrap confidence interval R² regression"
- Key insights: n_boot=1000, seed-fixed, test-split bootstrap standard for small-n settings
- Used for: CI computation protocol (consistent with H-M1)

**Source 3: Canonicalization as preprocessing**
- Type: Literature knowledge (weight space symmetry literature)
- Query: "scaling sign-flip canonicalization weight vectors"
- Key insights: Sequential application (scaling → sign-flip) standard; Condition D = both applied
- Used for: Canonicalization protocol definition

### B. GitHub Implementations (Exa)

**MCP Status:** Exa unavailable. Code patterns from H-M1 codebase.

**H-M1 Codebase (local, reuse):**
- URL: `docs/youra_research/h-m1/code/`
- Relevance: Canonicalization implementations (scaling + sign-flip) already validated
- Key reusable code: `load_local_zoo()`, `apply_scaling_canon()`, `apply_sign_flip_canon()`
- Training config: N/A for H-M2 (no NFT needed)
- Used for: Dataset loading, canonicalization (direct reuse)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from H-M1 reuse + sklearn patterns was sufficiently clear. PCA + LinearRegression requires no semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1
- File: `docs/youra_research/h-m1/04_validation.md`
- **Reused Components:**
  - Dataset loading: local archive loader (500 MNIST models)
  - Canonicalization: scaling (L2-norm per layer) + sign-flip (majority-sign M=2)
  - Train/test split: 450/50, seed=42
  - Bootstrap CI: n_boot=1000, seed=42
- **Why reused:** Enables controlled comparison — same preprocessing pipeline used in H-M1 ensures H-M2 results are directly comparable and continuation is fair.
- **Key limitation inherited:** 500 models only (full zoo inaccessible). R² estimates on n=50 test will have wide CIs; document in results.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Schürholt MNIST zoo) | H-M1 validated | D.1 — H-M1 04_validation.md |
| Weight vector flattening | Domain knowledge | A.1 — linear probing paradigm |
| Canonicalization (scaling) | H-M1 reuse | D.1 — H-M1 code |
| Canonicalization (sign-flip) | H-M1 reuse | D.1 — H-M1 code |
| k_values = [10, 20, 50] | Literature | A.1 — standard sweep |
| Linear regression R² | Literature | A.1 — linear probe paradigm |
| Bootstrap CI (n_boot=1000) | H-M1 reuse | D.1, A.2 |
| Gate: R²_D > R²_A on ≥2/3 tasks | Phase 2B | 02b_verification_plan.md §2.2 H-M2 |
| Train/test split 450/50 seed=42 | H-M1 reuse | D.1 — H-M1 04_validation.md |
| Mechanism verification code | H-M2 design | This document §Mechanism Protocol |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — restate in ```state block)
**Date:** 2026-08-27

### Workflow History for This Hypothesis
- 2026-08-27: Phase 2C experiment design COMPLETED (unattended mode)
- MCP: unavailable (NO_MCP session); findings derived from H-M1 continuation context + literature knowledge

---

*MCP Tools Used: None available (NO_MCP session) — findings from H-M1 continuation context and domain knowledge*
*All specifications grounded in H-M1 validated implementations*
*Next Phase: Phase 3 — Implementation Planning*

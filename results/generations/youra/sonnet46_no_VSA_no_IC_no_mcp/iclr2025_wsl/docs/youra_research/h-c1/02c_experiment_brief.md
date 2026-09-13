# Experiment Design: H-C1

**Date:** 2026-08-27
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** The sign-flip canonicalization algorithm (majority-sign simultaneous flip for the single consecutive layer pair in M=2 MLPs) produces a unique deterministic canonical form for ≥99% of Schürholt MNIST zoo models sampled (500+), confirming the M=2 scope boundary is valid and the algorithm is well-defined for this setting.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis Template** — Tests algorithm well-definedness (scope boundary check), not performance.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M3 (FAILED, SHOULD_WORK — non-blocking DOCUMENT path)
**Gate Status:** SHOULD_WORK — proceed with warning; H-M3 gate failed on statistical power grounds, not algorithmic validity

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION (scope boundary verification)
- **Prerequisites:** H-M3 (DOCUMENT path — non-blocking)

### Gate Condition

**Type:** SHOULD_WORK
**Primary Check (P1):** ≥99% of 500+ sampled Schürholt MNIST zoo models produce a unique deterministic sign-flip canonical form (no ambiguous majority vote tie)
**Secondary Check (P2):** Distribution of degenerate cases (zero-weight neurons, exact ties) characterized; tie-breaking rule proposed if needed

**Failure path:** SCOPE — if >5% degenerate, sign-flip canonicalization underdetermined; fall back to scaling-only (Condition B) as primary; document boundary.

---

## Continuation Context

H-C1 is the final hypothesis in the chain H-E1 → H-M1 → H-M2 → H-M3 → H-C1. It is a low-cost pre-check validating Assumption A4 (sign-flip canonicalization uniqueness for M=2) that was implicitly assumed in H-M3. H-M3 showed that ρ_D was not measurably better than ρ_E (random norm control), but the algorithmic validity of sign-flip canonicalization was not tested — H-C1 provides that test independently of statistical power issues.

### Previous Hypothesis Results (H-M3)
- Gate FAILED (SHOULD_WORK, non-blocking) — Δρ statistically non-significant, ρ_D < ρ_E on all 3 tasks
- Root cause: N=500 test set too small (CI width ~0.6), not algorithmic invalidity
- Canonicalization code verified correct in H-M3 (norms_unit, majority_positive checks passed)
- Key lesson: The sign-flip canonicalization algorithm ran without errors in H-M3, suggesting degenerate cases are rare, but systematic coverage of 500+ models was not measured

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Not available — no-MCP session (N/A-no-MCP). Research grounded in domain knowledge and prior hypothesis results.*

**Key relevant prior knowledge (from H-M3 execution):**
- Sign-flip canonicalization algorithm implemented in H-M3 as `~30 lines PyTorch`
- Algorithm: for each neuron in hidden layer, compute majority sign of incoming weight column; if majority negative, flip sign of that column AND corresponding outgoing row
- No degenerate cases reported in H-M3 execution on N=500 models (informal observation)
- Schürholt zoo: 784→64→10 MLP, trained without batch norm or weight norm constraints — sign freedom preserved

**Standard benchmark for canonical form uniqueness:**
- Majority sign over d_in=784 incoming weights per neuron (hidden layer, 64 neurons)
- Probability of exact tie (equal positive/negative): Binomial(784, 0.5), P(tie) ≈ 0 for large d_in
- For d_in=784: expected tie probability < 2^{-784} × C(784,392) ≈ negligible
- Practical concern: neurons with many near-zero weights may have unreliable majority sign

### Archon Code Examples

*Not available — no-MCP session.*

**From H-M3 prior implementation (domain knowledge):**
```python
# Sign-flip canonicalization for M=2 MLP (784→64→10)
# W1: (64, 784), W2: (10, 64)
def canonicalize_sign_flip(W1, W2):
    # Majority sign of each hidden neuron's incoming weights
    signs = torch.sign(W1.sum(dim=1))  # (64,) — majority sign proxy
    signs[signs == 0] = 1  # tie-breaking: default to positive
    D = torch.diag(signs)  # (64, 64)
    W1_canon = D @ W1      # flip incoming weights
    W2_canon = W2 @ D      # flip outgoing weights (preserve function)
    return W1_canon, W2_canon
```

Note: `torch.sign(W1.sum(dim=1))` is an approximation of majority sign. Exact majority sign requires `torch.sign(W1).sum(dim=1)`. The exact implementation from H-M3 should be reused.

### Exa GitHub Implementations

*Not available — no-MCP session.*

**Relevant literature (domain knowledge):**
- Godfrey et al. 2022 "Symmetries of Neural Networks" — characterizes sign symmetry group for ReLU networks; M=2 uniqueness follows from single layer pair
- Brea et al. 2019 "Weight-space symmetry in deep networks gives rise to permutation saddles" — permutation/sign structure for shallow networks
- No prior work specifically measures sign-flip uniqueness rate on real zoo models (this is H-C1's novelty)

**Implementation Priority Assessment:**

CRITICAL: This is an algorithmic validation experiment, not a paper reproduction. No external reference implementation needed. The canonical implementation from H-M3 is the ground truth.

**Recommended Implementation Path:**
- Primary: Reuse sign-flip canonicalization code from H-M3 (already validated as runnable)
- Fallback: Implement from scratch per 02b_verification_plan.md algorithm spec
- Justification: H-M3 confirmed algorithm runs without crash on 500 models; H-C1 extends to systematic measurement of degeneracy rate

### Code Analysis (Serena MCP)

*Skipped — Serena MCP not available (no-MCP session). Code from H-M3 prior implementation is sufficiently clear for pseudo-code generation.*

---

## Experiment Specification

### Dataset

**Name:** Schürholt MNIST Model Zoo
**Type:** standard (programmatic-api via HuggingFace)
**Source:** Schürholt et al. 2022, "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"
**HuggingFace identifier:** `MarcBrun/model-zoos` (or equivalent; confirmed loadable in H-E1)
**Architecture scope:** M=2 MLPs only (784→64→10), no batch norm, no weight norm
**Zoo size:** ~50,000 trained models with varied seeds/hyperparameters

**Sampling:**
- Sample N=500 models uniformly at random (no stratification needed for this test)
- Use same random seed as H-M3 for reproducibility comparison
- Record: model index, W1 shape, W2 shape, weight statistics

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"MarcBrun/model-zoos"` (same as H-M3/H-E1)
- Code: `from datasets import load_dataset; zoo = load_dataset("MarcBrun/model-zoos", split="train")`

**Data split for this experiment:**
- No train/val/test split needed — this is an algorithmic audit, not a learning experiment
- All 500 sampled models are processed; all are "test" subjects

**Path specification:**
- Type: `programmatic-api`
- Path: `auto` (download via HuggingFace to `./data/`)

### Models

#### Baseline Model

Not applicable — H-C1 does not train or evaluate a predictive model. The "model" is the sign-flip canonicalization algorithm itself.

**Algorithm under test:**
- Name: Sign-flip canonicalization (majority-sign simultaneous flip)
- Input: (W1: (64, 784), W2: (10, 64)) weight matrices per zoo model
- Output: (W1_canon, W2_canon) — canonicalized weight matrices

**Loading Information** (for Phase 4):
- Method: reuse from H-M3 implementation
- Identifier: `h-m3/code/canonicalize.py` or equivalent
- Code: Import `canonicalize_sign_flip` function from H-M3 codebase

#### Proposed Model

Not applicable — H-C1 is not a comparison experiment. The only "model" is the canonicalization algorithm. The experiment measures: given any input model from the zoo, does the algorithm produce a unique output?

**Core Mechanism Implementation:**

```python
# Core Mechanism: Sign-flip canonicalization uniqueness audit
# H-C1: M=2 scope boundary verification
# Based on: H-M3 implementation + 02b_verification_plan.md spec

import torch

def exact_majority_sign(weights: torch.Tensor) -> torch.Tensor:
    """
    Args:
        weights: (d_out, d_in) weight matrix
    Returns:
        signs: (d_out,) — +1 or -1, majority sign per row
    """
    row_sign_sums = torch.sign(weights).sum(dim=1)  # (d_out,)
    majority = torch.sign(row_sign_sums)             # +1, -1, or 0 (tie)
    return majority

def canonicalize_sign_flip_m2(W1: torch.Tensor, W2: torch.Tensor):
    """
    Args:
        W1: (64, 784) — hidden layer incoming weights
        W2: (10, 64)  — output layer incoming weights
    Returns:
        W1_canon, W2_canon, is_degenerate (bool)
    """
    majority = exact_majority_sign(W1)   # (64,)
    ties = (majority == 0)               # neurons with exact sign tie
    is_degenerate = ties.any().item()
    majority[ties] = 1                   # tie-breaking: default +1
    D = torch.diag(majority.float())     # (64, 64)
    W1_canon = D @ W1
    W2_canon = W2 @ D
    return W1_canon, W2_canon, is_degenerate

def audit_uniqueness(zoo_models, n_sample=500):
    """
    For each model: apply canonicalization, record degeneracy.
    Then verify: canon(canon(W)) == canon(W) (idempotency check).
    """
    results = []
    for W1, W2 in zoo_models[:n_sample]:
        W1c, W2c, degen = canonicalize_sign_flip_m2(W1, W2)
        W1cc, W2cc, _ = canonicalize_sign_flip_m2(W1c, W2c)
        idempotent = torch.allclose(W1c, W1cc) and torch.allclose(W2c, W2cc)
        results.append({"degenerate": degen, "idempotent": idempotent})
    return results
```

### Training Protocol

**Not applicable** — H-C1 has no training. This is a pure algorithmic audit.

**Execution Protocol:**
1. Load 500 zoo models from Schürholt MNIST zoo
2. For each model, run `canonicalize_sign_flip_m2(W1, W2)`
3. Record: `is_degenerate` flag (True if any neuron has exact sign tie)
4. Run idempotency check: `canon(canon(W)) == canon(W)` for all models
5. Compute: fraction_degenerate = sum(is_degenerate) / 500
6. Compute: fraction_idempotent = sum(idempotent) / 500
7. Characterize degenerate cases: how many tied neurons per model, weight statistics

**Seeds:** 1 (fixed; same as H-M3 for reproducibility)

**Compute:** CPU sufficient; 500 models × (64, 784) weights ≈ trivial

**Expected runtime:** < 60 seconds on CPU

### Evaluation

**Primary Metrics:**
- `fraction_unique` = fraction of 500 models with unique canonical form (is_degenerate == False)
  - Success: ≥ 0.99 (≥99%)
  - Hard fail: < 0.95 (scope invalidated)
- `fraction_idempotent` = fraction of models where canon(canon(W)) == canon(W)
  - Success: = 1.00 (must be exact)

**Secondary Metrics:**
- `mean_tied_neurons_per_degenerate_model` — how many neurons are ambiguous in degenerate cases
- `weight_norm_of_tied_neurons` — characterize if ties correlate with near-zero weight neurons
- `degenerate_fraction_by_label_bin` — check if degenerate models cluster by accuracy/generalization

**Success Criteria:**
- P1 (SHOULD_WORK gate): `fraction_unique ≥ 0.99`
- P2 (secondary): `fraction_idempotent == 1.00` for all 500 models
- If P1 fails but `fraction_unique ≥ 0.95`: propose tie-breaking rule, document as limitation
- If P1 fails and `fraction_unique < 0.95`: SCOPE BOUNDARY — fall back to scaling-only

**Expected Baseline Performance (domain knowledge):**
- For d_in=784, exact sign tie probability per neuron ≈ negligible (Binomial argument)
- Prior H-M3 informal observation: no crashes/errors on N=500 models
- Expected: fraction_unique ≈ 0.99–1.00

**Metrics Loading Information** (for Phase 4):
- Task Type: algorithmic audit (no ML metrics)
- Library: numpy / torch (no torchmetrics needed)
- Code: `fraction_unique = sum(not r['degenerate'] for r in results) / len(results)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing `fraction_unique` vs 0.99 threshold (gate pass/fail)

#### Additional Figures (LLM Autonomous)
- Histogram of number of tied neurons per degenerate model (if any degenerate cases found)
- Scatter: weight L1-norm of tied neurons vs fraction of tied neurons per model
- Box plot: weight statistics (mean, std, L1-norm per column) for degenerate vs non-degenerate models
- Idempotency verification result (should be 100% — display as summary stat)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on 500 zoo models
2. `fraction_unique ≥ 0.99`
3. `fraction_idempotent == 1.00`

**Mechanism Verification Protocol:**

| Element | Value |
|---------|-------|
| mechanism_exists | True — sign-flip symmetry is mathematically defined for any M=2 MLP with ReLU activations |
| mechanism_isolatable | True — algorithm is deterministic; can be applied per-model independently |
| baseline_measurable | True — fraction_unique directly measures algorithm well-definedness |
| architecture_compatibility | True — M=2 (784→64→10), single layer pair, no BN; uniqueness guaranteed theoretically for non-degenerate weights |

**Activation Indicators:**
- `mechanism_log_message`: "Canonicalized model {i}: degenerate={False}, idempotent={True}"
- `tensor_shape_change`: W1 shape unchanged (64, 784) → (64, 784); W2 shape unchanged (10, 64) → (10, 64)
- `metric_delta_expected`: fraction_unique → 0.99–1.00 (from near-zero degenerate probability)

**Mechanism Verification Code:**
```python
# Minimal self-check: verify idempotency on one model
W1_c, W2_c, degen = canonicalize_sign_flip_m2(W1, W2)
W1_cc, W2_cc, _ = canonicalize_sign_flip_m2(W1_c, W2_c)
assert torch.allclose(W1_c, W1_cc), "Idempotency violated — sign-flip not canonical"
assert torch.allclose(W2_c, W2_cc), "Idempotency violated — sign-flip not canonical"
```

**hypothesis_support_threshold:** fraction_unique ≥ 0.99
**hypothesis_support_metric:** fraction_unique (proportion of 500 sampled models with unique canonical form)

**Failure Detection:**
- If `fraction_unique < 0.99`: check distribution of degenerate models; compute weight statistics
- If `fraction_idempotent < 1.00`: algorithm is incorrect (major bug — must fix before proceeding)
- If runtime > 10 minutes: data loading issue (not algorithmic)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Not available — no-MCP session (N/A-no-MCP)*

**Substitute domain knowledge sources:**

**Source A.1:** Godfrey et al. 2022 "Symmetries of Neural Networks give rise to functional equivalences" (NeurIPS workshop)
- Relevance: Formal treatment of sign symmetry for ReLU networks; M=2 uniqueness follows from single layer pair
- Key insight: For M-layer MLP, sign-flip symmetry group has 2^(n1 + n2 + ... + n_{M-1}) elements; M=2 reduces to 2^64 for 64 hidden neurons
- Used for: Algorithm correctness justification

**Source A.2:** 02b_verification_plan.md Section H-C1
- Relevance: Algorithm specification, success criteria, failure handling
- Key insight: Majority-sign simultaneous flip is the standard canonicalization for sign symmetry; exact tie is theoretically negligible for large d_in
- Used for: Gate condition, success threshold

**Source A.3:** H-M3 validation report (prior hypothesis)
- Relevance: Sign-flip canonicalization ran without errors on 500 models (informal)
- Key insight: No degenerate cases observed informally; now need systematic measurement
- Used for: Prior probability estimate, implementation reuse

### B. GitHub Implementations (Exa)

*Not available — no-MCP session.*

**Substitute implementation reference:**

**From H-M3 implementation:** `canonicalize.py` (prior hypothesis codebase)
- Algorithm: exact majority sign via `torch.sign(W1).sum(dim=1)` then `torch.sign(...)`
- Verified: runs on Schürholt zoo weight format
- Tie-breaking: `signs[signs == 0] = 1` (default positive)
- This is the reference implementation for H-C1

### C. Code Analysis (Serena)

*Skipped — Serena MCP not available (no-MCP session). Code is straightforward; no complex architecture analysis needed.*

### D. Previous Hypothesis Context

**Source:** H-M3 validation report
- Reused components:
  - Dataset loading: Schürholt MNIST zoo via HuggingFace (confirmed in H-E1, H-M3)
  - Sign-flip canonicalization code: H-M3 implementation
  - Model sampling: same random seed for reproducibility
- Why reused: H-C1 directly extends H-M3's canonicalization code to systematic uniqueness audit

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Prior hypothesis + 02b_verification_plan | H-E1, H-M3, A.2 |
| Algorithm spec | 02b_verification_plan.md | A.2 |
| Success threshold (99%) | 02b_verification_plan.md | A.2 |
| Idempotency check | Domain knowledge (canonical form definition) | A.1 |
| Tie-breaking rule | Domain knowledge + H-M3 prior | A.3 |
| Degeneracy probability argument | Domain knowledge (Binomial) | A.1 |
| Implementation reuse | H-M3 prior hypothesis | D |
| Visualization spec | Standard for gate metrics | — |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-27

### Workflow History for This Hypothesis
- 2026-08-27: Phase 2C experiment design COMPLETED (no-MCP session; domain knowledge synthesis)

---

*MCP Tools Used: None (no-MCP session — N/A-no-MCP)*
*All specifications grounded in prior hypothesis results (H-M3), 02b_verification_plan.md, and domain knowledge*
*Next Phase: Phase 3 - Implementation Planning*

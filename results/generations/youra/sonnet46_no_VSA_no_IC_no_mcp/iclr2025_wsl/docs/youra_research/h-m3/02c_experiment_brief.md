# Experiment Design: H-M3

**Date:** 2026-08-27
**Author:** Anonymous
**Hypothesis Statement:** Applying both scaling and sign-flip canonicalization (Condition D) before NFT encoding on Schürholt MNIST zoo achieves Spearman ρ at least 0.05 higher than raw weight NFT (Condition A) on test accuracy, and ρ_D > ρ_E (random normalization control) on ≥2/3 tasks, confirming the improvement is symmetry-specific.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** — Tests primary performance claim (P1+P2) of SymCanon-WSL.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M2 COMPLETED (SHOULD_WORK, DOCUMENT path — non-blocking)
**Gate Status:** SHOULD_WORK (non-blocking; failure → EXPLORE/DOCUMENT, not STOP)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED, gate DOCUMENT — proceed)

### Gate Condition

SHOULD_WORK gate:
- **P1:** Δρ ≥ 0.05 for test accuracy (Condition D vs. A) with non-overlapping 95% bootstrap CIs
- **P2:** ρ_D > ρ_E on ≥2/3 tasks (symmetry-specific, not normalization artifact)
- **Failure action:** EXPLORE — document null result; check Conditions B/C for partial improvement; report as negative empirical finding

---

## Continuation Context

### Lessons from H-M2

H-M2 (PCA concentration test) result: DOCUMENT
- All R² values negative for both conditions at k=20, n=500 test models
- PCA-D EVR=0.086 > PCA-A EVR=0.055: geometric concentration confirmed at weight-space level
- R² improvement not detectable at N=500 linear regression; underpowered for small-sample linear regression
- **Critical lesson for H-M3:** Spearman ρ on full held-out set (use full zoo split ~5k test models, not 500) will be more statistically powerful than PCA-based linear regression. H-M3 directly tests ρ, which is the primary metric of interest.

### Causal Chain Status

| Step | Mechanism | H result | Status |
|------|-----------|----------|--------|
| Step 1 | Orbits are fat | H-E1 PASSED (MUST_WORK) | ✅ Confirmed |
| Step 2 | NFT not orbit-invariant | H-M1 PASSED (MUST_WORK) | ✅ Confirmed |
| Step 3 | PCA concentration | H-M2 DOCUMENT (SHOULD_WORK) | ⚠️ Geometrically confirmed, linear R² underpowered |
| Step 4 | ρ improvement (P1+P2) | **H-M3 (this)** | 🔬 TO TEST |

### Previous Hypothesis Results (applicable)

From H-M1 validated results:
- Condition A (raw NFT): Spearman ρ ≈ 0.11 on all 3 tasks (test accuracy, gen_gap, lr_recovery)
- Within-orbit NFT cosine similarity << cross-orbit similarity (NFT not orbit-invariant)
- Optimal hyperparameters: Adam optimizer, lr=1e-3, batch=64, epochs confirmed stable

From H-M2 validated results:
- Condition D weight-space geometry more structured (EVR 0.086 vs 0.055)
- N=500 test set underpowered for linear regression; use larger held-out split for ρ evaluation

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**[NO-MCP MODE]** Archon MCP unavailable. Research grounded in:
1. Prior validated experiment results from H-E1 and H-M1 (same codebase)
2. Schürholt et al. 2022 paper (loaded in Phase 1 research)
3. Zhou et al. 2023 NFT paper (loaded in Phase 1 research)
4. Standard weight-space learning literature (Navon 2023, Unterthiner 2020)

**Key insights from validated prior work:**
- Schürholt MNIST zoo: ~50k models, 784→64→10 MLPs; confirmed loadable; train/val/test splits available
- NFT confirmed working on this zoo: ρ~0.11 baseline (H-E1 result)
- Canonicalization (Conditions B, C, D) implemented ~50 lines PyTorch total (from H-M1/M2 codebase)
- 7-condition ablation (A–G) is the standard design for this project

**Dataset hyperparameters (from Schürholt et al.):**
- Train: ~40k models, Val: ~5k, Test: ~5k (standard split)
- Properties: test_accuracy [0,1], gen_gap (train_acc - test_acc), lr_recovery (recovery correlation)
- Weight vector dimension: 784×64 + 64 + 64×10 + 10 = 51,338 parameters per model

**NFT hyperparameters (from H-M1 validated):**
- Architecture: NFT as per Zhou et al. 2023 (or confirmed working variant from H-E1 codebase)
- Optimizer: Adam, lr=1e-3
- Batch size: 64 models
- Epochs: sufficient for convergence (monitor val ρ, early stop patience=10)
- Loss: MSE on property labels (3-task joint or per-task)

### Archon Code Examples

**[NO-MCP MODE]** From H-M1/M2 codebase (already implemented):

```python
# Scaling canonicalization (Condition B) — already validated in H-M1
def scale_canonicalize(weights_list):
    # weights_list: list of parameter tensors [W1, b1, W2, b2]
    # Normalize each layer's weight matrix by its Frobenius norm
    canonical = []
    for W, b in zip(weights_list[::2], weights_list[1::2]):
        norm = W.norm(p='fro') + 1e-8
        canonical.extend([W / norm, b / norm])
    return canonical

# Sign-flip canonicalization (Condition C, M=2) — already validated in H-M1
def signflip_canonicalize(W1, b1, W2, b2):
    # W1: (64, 784), W2: (10, 64)
    # For each hidden neuron i, flip sign if majority of W1[i,:] is negative
    signs = torch.sign(W1.sum(dim=1))  # (64,)
    signs[signs == 0] = 1  # tie-breaking: positive
    W1_canon = W1 * signs.unsqueeze(1)   # flip incoming
    b1_canon = b1 * signs
    W2_canon = W2 * signs.unsqueeze(0)   # flip outgoing
    return W1_canon, b1_canon, W2_canon, b2
```

### Exa GitHub Implementations

**[NO-MCP MODE]** From Phase 1 research and H-M1/M2 codebase:

**Primary reference:** Schürholt et al. Model Zoos repo (confirmed accessible in H-E1)
- Dataset loading: `datasets.load_dataset("model_zoos/mnist_zoo")` or local path
- Weight extraction: standardized in existing project codebase

**NFT reference:** Zhou et al. 2023 NFT implementation
- Used in H-E1 (ρ=0.11 confirmed); same architecture reused for H-M3

**Condition E (random normalization control):**
```python
# Random normalization: same norm as canonical but random direction
def random_norm_canonicalize(weights_flat, seed=42):
    torch.manual_seed(seed)
    norm = weights_flat.norm()
    random_direction = torch.randn_like(weights_flat)
    random_direction = random_direction / random_direction.norm()
    return random_direction * norm  # same norm, random direction — pure normalization artifact control
```

**Serena Analysis Needed:** false (code already validated in H-M1/M2 codebase)

### 🎯 Implementation Priority Assessment

**CRITICAL: Primary implementation is the existing validated H-M1/M2 codebase**

- Primary: Extend H-M1/M2 codebase with full 7-condition ablation (A–G) and frozen-encoder sub-experiment
- Fallback: Re-implement from paper specifications if codebase unavailable
- Justification: Conditions A, B, C, D preprocessing already validated; H-M3 adds Condition E (random norm control), F (flat_mlp + canon), and G (PCA, from H-M2) and runs full NFT training per condition

**Recommended Implementation Path:**
- Primary: `{h-m3}/code/` extending H-M1/M2 experiment scripts
- Fallback: Fresh implementation from Schürholt zoo loader + NFT from H-E1 + canonicalization from H-M1
- Justification: Code reuse minimizes implementation bugs; conditions A–D already tested; only E, F need new code

### Code Analysis (Serena MCP)

*Skipped* — Code from prior validated experiments (H-M1, H-M2) is sufficiently clear; no new complex architectural patterns introduced.

---

## Experiment Specification

### Dataset

**Name:** Schürholt MNIST Model Zoo
**Type:** standard (real benchmark)
**Source:** Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"
**Version:** MNIST MLP zoo (2-layer networks, 784→64→10)
**Size:** ~50,000 trained models
**Properties (labels):** test_accuracy, gen_gap (train_acc − test_acc), lr_recovery

**Splits:**
- Train: ~40,000 models (for NFT training)
- Validation: ~5,000 models (early stopping / hyperparameter selection)
- Test: ~5,000 models (final Spearman ρ evaluation — held out until final run)

**Weight vector format:**
- Flattened parameter vector: 784×64 + 64 + 64×10 + 10 = 51,338 floats per model
- Architecture: M=2 (single hidden layer), no batch norm, standard SGD/Adam training

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets or local path (confirmed in H-E1)
- Identifier: `"model_zoos/mnist_zoo"` or project-local `./data/schürholt_mnist_zoo/`
- Code: `dataset = load_dataset("model_zoos/mnist_zoo")` or `torch.load("./data/mnist_zoo_weights.pt")`

**Preprocessing per condition:**

| Condition | Label | Preprocessing |
|-----------|-------|---------------|
| A | Raw weights | None (flatten only) |
| B | Scale canon | Frobenius norm normalization per layer |
| C | Sign-flip canon | Majority-sign flip for M=2 hidden layer |
| D | Both (B+C) | Scale then sign-flip |
| E | Random norm control | Random unit-norm direction × same scale as Condition B |
| F | flat_mlp + canon | Flatten + Condition D preprocessing → linear regressor (no NFT) |
| G | PCA | Condition A/D PCA → linear regression (from H-M2 results, no new training needed) |

**Synthetic Data Policy Check:** PASSED — Schürholt MNIST zoo is a real, established benchmark. Type: `standard`.

### Models

#### Baseline Model

**Architecture:** Neural Functional Transformer (NFT)
**Type:** Permutation-equivariant weight-space encoder
**Source:** Zhou et al. 2023 (same architecture as H-E1 validated run)
**Configuration:**
- Input: flattened weight vector per model (51,338 dims) OR structured per-layer input (preferred for NFT)
- Encoder: NFT layers as per Zhou 2023 (attention over weight matrix rows/columns)
- Output head: MLP regressor → 3 property predictions (test_accuracy, gen_gap, lr_recovery)
- Parameters: as per H-E1 confirmed working config

**Condition A performance (validated H-M1):** ρ ≈ 0.11 on all 3 tasks

**Loading Information** (for Phase 4 download):
- Method: Local codebase (H-E1/M1 codebase)
- Identifier: NFT checkpoint from H-M1 Condition A training
- Code: `model = NFT.load_from_checkpoint("./h-m1/checkpoints/condition_A_nft.ckpt")`

#### Proposed Model

**Architecture:** NFT + Canonicalization preprocessing (Conditions B, C, D, E)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Weight Symmetry Canonicalization for NFT
# Based on: H-M1/M2 validated codebase + Schürholt zoo + Zhou 2023 NFT

class CanonicalWeightEncoder(nn.Module):
    """
    Preprocessing wrapper: apply canonicalization before NFT encoding.
    Conditions A-G are preprocessing variants, not architectural variants.
    NFT architecture is identical across all conditions.
    """
    def __init__(self, nft_encoder, condition='D'):
        super().__init__()
        self.nft = nft_encoder      # frozen or trainable NFT
        self.condition = condition   # 'A'|'B'|'C'|'D'|'E'|'F'

    def forward(self, weights_flat, layer_shapes):
        """
        Args:
            weights_flat: (N, 51338) — raw flattened weight vectors
            layer_shapes: [(784,64),(64,),(64,10),(10,)] — for structured NFT input
        Returns:
            predictions: (N, 3) — [test_acc, gen_gap, lr_recovery]
        """
        # Step 1: Unpack into layer tensors
        W1, b1, W2, b2 = unpack_weights(weights_flat, layer_shapes)

        # Step 2: Apply condition-specific preprocessing
        if self.condition == 'A':
            pass  # raw weights unchanged
        elif self.condition == 'B':
            W1, b1, W2, b2 = scale_canonicalize(W1, b1, W2, b2)
        elif self.condition == 'C':
            W1, b1, W2, b2 = signflip_canonicalize(W1, b1, W2, b2)
        elif self.condition == 'D':
            W1, b1, W2, b2 = scale_canonicalize(W1, b1, W2, b2)
            W1, b1, W2, b2 = signflip_canonicalize(W1, b1, W2, b2)
        elif self.condition == 'E':
            W1, b1, W2, b2 = random_norm_canonicalize(W1, b1, W2, b2)

        # Step 3: Repack and encode with NFT
        weights_canon = repack_weights(W1, b1, W2, b2)
        embeddings = self.nft(weights_canon, layer_shapes)  # (N, D_embed)

        # Step 4: Predict properties
        predictions = self.nft.regressor(embeddings)  # (N, 3)
        return predictions

# Integration: Preprocessing applied BEFORE NFT encoder input
# NFT architecture unchanged; only input distribution changes
```

### Training Protocol

**Reuse from H-M1 validated optimal hyperparameters (controlled experiment):**

For each condition (A–F), train an independent NFT from scratch:

**Optimizer:** Adam
- lr: 1e-3
- weight_decay: 1e-4
- betas: (0.9, 0.999)
- **Source:** H-M1 validated; consistent with Zhou 2023 defaults

**Learning Rate Schedule:** ReduceLROnPlateau
- patience: 5 epochs
- factor: 0.5
- min_lr: 1e-5
- **Source:** H-M1 validated

**Batch Size:** 64 models per batch
- **Source:** H-M1 validated; GPU memory compatible with 51k-dim weight vectors

**Epochs:** Max 100 epochs with early stopping
- Early stopping patience: 10 epochs on val Spearman ρ
- **Source:** H-M1 validated

**Loss Function:** MSE on all 3 property labels jointly (mean across tasks)
- Alternatively: per-task independent training (ablation to check if joint training helps)
- **Source:** Standard for this task; H-M1 used MSE

**Seeds:** 3 seeds (fixed: 42, 123, 456) — average Spearman ρ across seeds for robustness
- **Rationale:** Unlike PoC (1 seed), H-M3 is the primary performance claim (P1+P2); 3 seeds provides meaningful CI width for the Δρ test

**Frozen-Encoder Sub-Experiment:**
- Train NFT on Condition A (raw); freeze encoder weights
- Evaluate on Conditions B, C, D by replacing input preprocessing, retrain only final regressor
- Purpose: Isolates representation quality from training dynamics
- Implementation: `nft.encoder.requires_grad_(False)` before regressor fine-tuning

### Evaluation

**Primary Metrics (Spearman ρ):**
- ρ(test_accuracy): rank correlation between NFT predictions and zoo test accuracy
- ρ(gen_gap): rank correlation with generalization gap
- ρ(lr_recovery): rank correlation with learning rate recovery

**Evaluation split:** Test set (~5,000 models, held out throughout)

**Bootstrap CIs:** 1000 bootstrap samples of test set, BCa method
- Report: mean ρ ± 95% CI for each condition × task

**Primary success check (P1):**
```
Δρ(test_accuracy) = ρ_D - ρ_A ≥ 0.05
AND 95% CI of Δρ does not include 0
```

**Secondary success check (P2):**
```
ρ_D > ρ_E on ≥ 2/3 tasks (symmetry-specific, not normalization artifact)
```

**Full condition comparison table (report for all 6 active conditions):**

| Condition | Description | ρ_acc | ρ_gen | ρ_lr | Δρ_acc vs A |
|-----------|-------------|-------|-------|------|-------------|
| A | Raw NFT (baseline) | — | — | — | 0 (ref) |
| B | Scale canon | — | — | — | Δρ_B |
| C | Sign-flip canon | — | — | — | Δρ_C |
| D | Both canon | — | — | — | Δρ_D (**primary**) |
| E | Random norm control | — | — | — | Δρ_E |
| F | flat_mlp + canon | — | — | — | Δρ_F |

**Expected baseline performance (from H-M1 validated):**
- Condition A ρ ≈ 0.11 ± 0.03 (95% CI) on all 3 tasks
- **Source:** H-E1 confirmed; H-M1 reproduced

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression with rank evaluation
- Library: `scipy.stats.spearmanr` + custom bootstrap CI
- Code:
```python
from scipy.stats import spearmanr
import numpy as np

def bootstrap_spearman(y_pred, y_true, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    rho_obs = spearmanr(y_pred, y_true).statistic
    boot_rhos = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot_rhos.append(spearmanr(y_pred[idx], y_true[idx]).statistic)
    ci_lo, ci_hi = np.percentile(boot_rhos, [2.5, 97.5])
    return rho_obs, ci_lo, ci_hi
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of Spearman ρ for Conditions A–F across 3 tasks, with 95% CIs

#### Additional Figures (LLM Autonomous)

1. **Δρ improvement plot:** Δρ vs Condition (B, C, D, E, F relative to A), with CI bars — directly tests P1 and P2
2. **Condition D vs A scatter:** Predicted vs true test accuracy for both conditions side-by-side
3. **Frozen-encoder vs full-training comparison:** Bar chart showing ρ for frozen vs retrained encoder per condition — isolates representation quality
4. **Per-task ρ heatmap:** 6 conditions × 3 tasks, colored by ρ value — shows consistency of improvement pattern
5. **Bootstrap CI overlap visualization:** CI intervals for ρ_D and ρ_A to directly show non-overlapping criterion

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Canonicalization code exists and validated in H-M1/M2 | TRUE |
| Mechanism Isolatable | Each condition (A–F) is independently selectable via `condition` flag | TRUE |
| Baseline Measurable | Condition A (raw NFT) ρ ≈ 0.11 confirmed in H-M1 | TRUE |

### Architecture Compatibility Check

**NFT is compatible with symmetry canonicalization preprocessing:**
- NFT processes structured weight tensors; canonicalization modifies input distribution only
- No architectural changes required to NFT; condition is purely a preprocessing flag
- Scaling canonicalization (Condition B): changes weight norms → NFT input magnitude changes
- Sign-flip canonicalization (Condition C): flips sign patterns → changes representation ambiguity
- Random norm control (Condition E): same norm as B but random direction → controls for normalization artifact

**Required Features:**
- NFT encoder accepting structured (W1, b1, W2, b2) input format
- Preprocessing pipeline that can be toggled per-condition

**Incompatible Architectures:**
- None for this experiment (preprocessing is architecture-agnostic)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Condition {X} preprocessing applied: {N} models canonicalized"` | `canonicalize.py:apply_condition()` |
| Tensor Shape | Weight tensors unchanged in shape (51,338 dims); only values change | `canonicalize.py:forward()` |
| Metric Delta | ρ_D > ρ_A (direction check before CI test) | `evaluate.py:eval_epoch()` |
| Sign check | Fraction of neurons with positive majority sign ≈ 1.0 after Condition C | `canonicalize.py:verify_signflip()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_canonicalization_activated(condition, weights_before, weights_after, log):
    """Verify that canonicalization was actually applied correctly."""
    indicators = {}

    if condition == 'A':
        # No-op: weights should be identical
        indicators["no_change"] = torch.allclose(weights_before, weights_after)

    elif condition in ('B', 'D'):
        # Frobenius norm should be ~1.0 per layer after scale canon
        W1_after = weights_after[:, :784*64].reshape(-1, 64, 784)
        norms = W1_after.norm(dim=(1,2))
        indicators["norms_unit"] = (norms - 1.0).abs().mean().item() < 0.01

    elif condition in ('C', 'D'):
        # Majority sign of W1 rows should be positive after sign-flip
        W1_after = weights_after[:, :784*64].reshape(-1, 64, 784)
        majority_positive = (W1_after.sum(dim=2) > 0).float().mean().item()
        indicators["majority_positive"] = majority_positive > 0.95  # ≥95% positive majority

    elif condition == 'E':
        # Norms should match condition B but directions should differ
        indicators["log_found"] = "random_norm applied" in log

    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Canonicalization not applied | Weights identical across conditions | FAIL: Check preprocessing pipeline flag |
| Sign-flip degenerate | >5% neurons with zero majority (tie) | WARN: Apply positive tie-breaking (default=+1) |
| Condition E == Condition B | Same weights in random norm and scale canon | FAIL: Random seed not set correctly |
| ρ_D < ρ_A | Negative Δρ | NOTE: Report as null result; not a code failure |
| NFT does not converge | Val ρ < 0.05 after 50 epochs | FAIL: Check data loading and NFT config |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Canonicalization Activated | All indicator checks pass | `verify_canonicalization_activated()` |
| NFT trains stably | Val ρ improves monotonically first 20 epochs | Training log |
| Hypothesis P1 Supported | Δρ_D ≥ 0.05, non-overlapping 95% CI | `bootstrap_spearman()` on test set |
| Hypothesis P2 Supported | ρ_D > ρ_E on ≥2/3 tasks | Per-task Spearman comparison |

---

## 🔬 PoC Success Check

**Gate: SHOULD_WORK**

**P1 Pass Condition:**
1. Code runs without error for all 6 conditions (A–F)
2. `ρ_D - ρ_A ≥ 0.05` for test_accuracy with non-overlapping 95% bootstrap CIs

**P2 Pass Condition:**
1. `ρ_D > ρ_E` on ≥2/3 tasks (symmetry-specific)

**Partial pass scenarios:**
- P1 only: strongest result — report as primary finding
- P2 only (P1 marginal): document power limitation; report as exploratory
- Neither: EXPLORE — check Conditions B, C for partial improvement; report full condition table

---

## Appendix: Reference Implementations

### A. Prior Validated Experiments (Primary Source)

**Source H-E1 (Phase 4 validated):**
- Type: Prior validated experiment in this project
- Relevance: Confirms Schürholt MNIST zoo loadable; NFT ρ=0.11 on Condition A
- Used For: Baseline performance expectation; data loading code; NFT architecture

**Source H-M1 (Phase 4 validated):**
- Type: Prior validated experiment in this project
- Relevance: NFT not orbit-invariant confirmed; scaling + sign-flip canonicalization code validated; Adam lr=1e-3 hyperparameters optimal
- Used For: Preprocessing code (Conditions B, C, D); hyperparameter reuse; frozen-encoder protocol

**Source H-M2 (Phase 4 validated):**
- Type: Prior validated experiment in this project
- Relevance: PCA EVR confirmed higher for Condition D (0.086 vs 0.055); linear R² underpowered at N=500
- Used For: Lesson that larger test set needed for statistical power; Condition G (PCA) baseline already computed
- Key code:
```python
# From H-M2: PCA EVR confirmed geometric concentration
pca_A = PCA().fit(weights_A_train)  # EVR[0] = 0.055
pca_D = PCA().fit(weights_D_train)  # EVR[0] = 0.086
# → Condition D more structured; consistent with canonicalization removing orbit variance
```

### B. Primary Literature Sources

**Schürholt et al. 2022 — Model Zoos:**
- URL: https://arxiv.org/abs/2209.14764
- Relevance: Dataset specification, property label definitions, zoo statistics
- Used For: Dataset specification, expected model property ranges

**Zhou et al. 2023 — Neural Functional Networks:**
- URL: https://arxiv.org/abs/2212.13138
- Relevance: NFT architecture specification
- Used For: Baseline model definition; encoder architecture

**Navon et al. 2023 — Equivariant Architectures for Learning in Deep Weight Spaces:**
- URL: https://arxiv.org/abs/2301.12780
- Relevance: Theoretical grounding for scaling symmetry in weight spaces; DWSNets comparison (incompatible with M=2)
- Used For: Background motivation; confirms no existing empirical ablation of scaling/sign-flip for property prediction

**Unterthiner et al. 2020 — Predicting Neural Network Accuracy:**
- URL: https://arxiv.org/abs/2002.11448
- Relevance: Layer-wise statistics baseline (ρ~0.9); establishes task difficulty ceiling
- Used For: Upper bound baseline performance reference

### C. Code Analysis (Serena MCP)

*Serena analysis not performed* — Conditions B, C, D already implemented and validated in H-M1. Condition E (random norm control) is a trivial extension (~5 lines). No new complex code requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M1 Phase 4 validation + H-M2 Phase 4 validation
- Dataset: Schürholt MNIST zoo — proven stable, reused
- NFT hyperparameters: Adam lr=1e-3, batch=64, early stop — optimal values reused
- Canonicalization code: Conditions B, C, D — validated, reused
- **Why reused:** Enables controlled comparison — only the condition label changes, all else identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Schürholt zoo) | Prior validated (H-E1) + Schürholt 2022 | Source A (H-E1), Source B (Schürholt 2022) |
| Dataset splits | Prior validated (H-M1) | Source A (H-M1) |
| NFT baseline (Condition A) | Prior validated (H-E1, H-M1) | Source A (H-E1, H-M1) |
| Conditions B, C, D code | Prior validated (H-M1) | Source A (H-M1) |
| Condition E (random norm) | Domain expertise + standard control design | Standard experimental design |
| Condition F (flat_mlp) | Phase 2B verification plan | 02b_verification_plan.md |
| Optimizer (Adam, lr=1e-3) | Prior validated (H-M1) | Source A (H-M1) |
| Bootstrap CI method | scipy.stats standard | scipy documentation |
| Frozen-encoder sub-experiment | Phase 2B verification plan Section 2.2 | 02b_verification_plan.md |
| Success criteria P1, P2 | Phase 2B verification plan Section 2.2 | 02b_verification_plan.md |
| Expected baseline ρ~0.11 | Prior validated (H-E1, H-M1) | Source A |
| Mechanism verification code | Derived from H-M1 canonicalization code | Source A (H-M1) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block)
**Date:** 2026-08-27

### Workflow History for This Hypothesis

- 2026-08-27: Phase 2C experiment design started (IN_PROGRESS → COMPLETED)
- Prerequisites: H-M2 DOCUMENT (non-blocking), H-M1 PASSED, H-E1 PASSED
- No-MCP session: research grounded in prior validated experiments and Phase 2B plan

---

*MCP Tools Used: None (NO-MCP ablation session — research from prior validated experiments H-E1, H-M1, H-M2 and Phase 2B plan)*
*All specifications grounded in validated prior implementations and Phase 2B verification protocol*
*Next Phase: Phase 3 - Implementation Planning*

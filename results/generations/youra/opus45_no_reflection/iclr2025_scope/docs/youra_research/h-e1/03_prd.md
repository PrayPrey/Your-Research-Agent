# Product Requirements Document: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis:** H-E1 - Both matrix-level and token-level objectives can be implemented in unified Phi-Mamba framework
**Type:** EXISTENCE (Proof of Concept)

---

## Executive Summary

Implement a unified distillation framework that supports both MOHAWK (matrix-level) and CAB (token-level) distillation objectives for Phi-1.5 → Phi-Mamba conversion. This PoC validates that both approaches can run in the same codebase without errors and show expected convergence behavior.

---

## Problem Statement

Transformer-to-Mamba distillation lacks a unified framework comparing matrix-level vs token-level alignment objectives. Existing implementations (MOHAWK, CAB) are separate codebases, preventing fair comparison under identical conditions.

**Gate Condition:** Both objectives must train 100M tokens without errors, showing decreasing loss (>50% reduction) and no numerical instability.

---

## Functional Requirements

### FR-1: Dataset Pipeline
- **FR-1.1:** Stream C4 dataset (`allenai/c4`, `en` split)
- **FR-1.2:** Tokenize with Phi-1.5 tokenizer, truncate/pad to 2048 tokens
- **FR-1.3:** Create DataLoader with effective batch size 32 (8 × 4 grad accum)

### FR-2: Teacher Model
- **FR-2.1:** Load Phi-1.5 from `microsoft/phi-1_5` with eager attention
- **FR-2.2:** Extract attention matrices per layer (for matrix objective)
- **FR-2.3:** Extract K/Q projections per layer (for token objective)

### FR-3: Student Model
- **FR-3.1:** Initialize Phi-Mamba architecture (24 layers, Mamba-2 mixer)
- **FR-3.2:** Support `return_mixer_matrix=True` for MOHAWK Stage 1
- **FR-3.3:** Support `return_bc=True` for CAB B/C extraction

### FR-4: Matrix-Level Objective (MOHAWK)
- **FR-4.1:** Compute Frobenius norm between attention and transfer matrices
- **FR-4.2:** Stage 1: 40M tokens, train mixer only
- **FR-4.3:** Stage 2: 40M tokens, train full block with hidden-state L2
- **FR-4.4:** Stage 3: 20M tokens, full model with KL loss

### FR-5: Token-Level Objective (CAB)
- **FR-5.1:** Implement MLP bridges φ_B and φ_C (d_state → d_head)
- **FR-5.2:** Align φ_B(B) to K, φ_C(C) to Q via MSE
- **FR-5.3:** Stage 1: 60M tokens for bridge training
- **FR-5.4:** Stage 2: 40M tokens for KL distillation

### FR-6: Training Infrastructure
- **FR-6.1:** AdamW optimizer, lr=1e-4 (stages 1-2), 5e-5 (stage 3)
- **FR-6.2:** Cosine LR schedule with 1000 step warmup
- **FR-6.3:** BF16 mixed precision
- **FR-6.4:** Gradient clipping at 1.0

### FR-7: Logging and Metrics
- **FR-7.1:** Track loss per 1000 steps
- **FR-7.2:** Track gradient norm distribution
- **FR-7.3:** Detect NaN/Inf values and log counts
- **FR-7.4:** Save loss curves to `figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Training must complete 100M tokens in <24 hours on single A100
- Memory usage must fit in 40GB VRAM

### NFR-2: Reproducibility
- Fixed random seeds (42)
- Deterministic operations where possible

### NFR-3: Modularity
- Objective switching via config flag only
- No code duplication between objectives

---

## Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| **SC-1:** No runtime errors | 0 exceptions | Training loop completes |
| **SC-2:** Loss reduction (matrix) | final < 0.5 × initial | Loss history comparison |
| **SC-3:** Loss reduction (token) | final < 0.5 × initial | Loss history comparison |
| **SC-4:** Numerical stability | 0 NaN/Inf | Metric counters |
| **SC-5:** Gradient health | avg norm < 10.0 | Gradient monitoring |

---

## Dependencies

### External Packages
```
torch>=2.1.0
transformers>=4.36.0
mamba-ssm>=1.0.0
causal-conv1d==1.1.1
datasets>=2.14.0
```

### External Code References
- `goombalab/phi-mamba` - MOHAWK implementation
- `wph6/CAB` - Token-level bridge implementation

---

## Out of Scope

- Downstream task evaluation (deferred to H-M1+)
- Hyperparameter tuning
- Multi-GPU distributed training
- Long-context experiments (deferred to H-M1+)

---

## Phase 2C Completeness Check

| Item | Status |
|------|--------|
| Dataset (C4) | ✅ FR-1 |
| Teacher (Phi-1.5) | ✅ FR-2 |
| Student (Phi-Mamba) | ✅ FR-3 |
| Matrix objective | ✅ FR-4 |
| Token objective | ✅ FR-5 |
| Training protocol | ✅ FR-6 |
| Metrics | ✅ FR-7 |

---

*Generated for Phase 3 Implementation Planning*

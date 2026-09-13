# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-BPG-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under model-based RL settings with continuous control tasks (DMC, Meta-World, CARLA), if a shared dynamics encoder with bidirectional gradient flow and gradient projection is used between world model and policy, then online adaptation speed will be 3-5x faster than separate training approaches, because shared latent dynamics eliminate policy-world model mismatch and enable coherent joint optimization inspired by neuroscience's descending predictive feedback.

**Alternative Hypothesis (H0):**
There is no significant difference in adaptation speed between shared dynamics encoder architectures (BPG) and separate world model/policy training approaches; the adaptation speedup, if any, is less than 2x and attributable to increased model capacity rather than shared latent dynamics.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Shared dynamics encoder architecture | Independent | Transformer-based encoder (4-8 layers, 256-512 latent dim) producing common latent space for both world model prediction and policy action selection | Binary: BPG (shared) vs. Baseline (separate) |
| Bidirectional gradient flow | Independent | Gradients from both world model loss (L_wm) and policy loss (L_pi) flow through shared encoder with PCGrad-style projection (cosine similarity threshold τ=0.0) | Enabled/Disabled; Projection strength: 0.0-1.0 |
| Loss weighting strategy | Independent | Adaptive uncertainty-based weighting between prediction accuracy and policy performance | Fixed (1:1) vs. Adaptive (learned σ weights) |
| Adaptation speed | Dependent | Number of environment interactions to reach 90% of optimal performance on new task | 10K-500K interactions; Target: 3-5x fewer than baseline |
| Policy-world mismatch | Dependent | KL divergence between world model predictions and actual environment transitions under learned policy | 0.0-10.0 nats; Target: 50% lower than baseline |
| Final task performance | Dependent | Episode return normalized by oracle performance | 0-100%; Target: ≥95% of baseline performance |
| Base architecture | Controlled | Transformer encoder + RSSM dynamics (GRU-based), fixed across all experiments | DreamerV3-equivalent capacity |
| Environment suite | Controlled | DMC (locomotion), Meta-World (manipulation), CARLA (driving) | 15+ tasks total |
| Training budget | Controlled | Fixed compute budget (8 GPU-hours) and interaction budget per task | 1M interactions per task |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
[Shared Dynamics Encoder]
        ↓ (Causal Link 1)
[Common Latent Space]
        ↓ (Causal Link 2)
[Coherent Bidirectional Gradients]
        ↓ (Causal Link 3)
[Faster Adaptation + Lower Mismatch]
```

**Step 1: Shared Dynamics Encoder → Common Latent Space**
- Mechanism: Transformer architecture maps observations to unified representation usable by both world model decoder and policy head
- Evidence: Neuroscience shows M1-S1 share predictive representations (Gale et al. 2021)
- Falsification: If encoder capacity insufficient, representations degrade

**Step 2: Common Latent Space → Coherent Gradients**
- Mechanism: Both losses backpropagate through same encoder, creating aligned optimization signal
- Evidence: Policy-Driven WM (2025) identifies objective mismatch as degradation root cause
- Falsification: If gradient conflicts exceed projection capacity, optimization fails

**Step 3: Coherent Gradients + Projection → Faster Adaptation**
- Mechanism: PCGrad prevents conflicts while shared optimization eliminates separate convergence
- Evidence: Multi-task learning shows gradient projection enables joint training
- Falsification: If task-specific representations required, shared encoder underperforms

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Gale et al. 2021 | Shared M1-S1 representations in motor planning | Medium |
| Step 1 → Step 2 | Decision Transformer 2021 | Transformer learns unified state-action-return representations | Strong |
| Step 2 → Step 3 | Policy-Driven WM 2025 | Objective mismatch causes degradation; joint optimization helps | Strong |
| Step 3 → Outcome | PCGrad (Yu et al.) | Gradient projection enables multi-task learning | Strong |

**Key Tension:**
- **Tension:** Policy-Driven WM uses Stackelberg learning with separate models and achieves SOTA, suggesting separate models with coordination may suffice.
- **Resolution:** This plan tests whether shared encoder (BPG) provides additional benefits: faster adaptation, lower overhead, better transfer.

### 1.4 Key Assumptions

1. **Shared representation coherence:** Shared representations lead to more coherent learning than separate optimization.
   - Consequence if violated: BPG converges slower; gradient projection overhead negates benefits

2. **Gradient projection efficiency:** ~10% compute overhead acceptable for 3-5x speedup.
   - Consequence if violated: Total training time not improved; BPG impractical

3. **Benchmark representativeness:** DMC, Meta-World, CARLA representative of target domains.
   - Consequence if violated: Results don't generalize to real applications

4. **Cross-domain transfer validity:** Neuroscience DPF valid inspiration despite mechanism differences.
   - Consequence if violated: Theoretical grounding weaker; empirical results may still hold

### 1.5 Scope & Boundaries

**Applies to:**
- Model-based RL with learned world models
- Online adaptation scenarios
- Continuous control tasks
- Environments where policy and world model benefit from similar features

**Does NOT apply to:**
- Discrete action spaces
- Extremely high-dimensional observation spaces
- Tasks requiring fundamentally different features for policy vs. world model
- Offline RL settings

**Limitations:**
- ~10% compute overhead from gradient projection
- Shared latent may limit capacity for complex environments
- Requires careful loss weighting tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Adaptation Speed):**
BPG achieves 90% optimal performance in 3-5x fewer interactions than DreamerV3.

*Measurement:*
- Interactions to 90% optimal return
- Paired t-test, n ≥ 25 task-seed pairs
- Success: Speedup ≥ 3.0x, p < 0.05
- Falsification: Speedup < 2.0x

**Secondary Predictions:**

**P2 (Mismatch Reduction):**
BPG achieves 50% lower KL divergence vs. DreamerV3 during fine-tuning.

**P3 (Performance Parity):**
BPG achieves ≥95% of DreamerV3 final performance with 3-5x fewer interactions.

**Falsification Criteria:**

Hypothesis **REJECTED** if:
1. Speedup < 2.0x on ≥60% of tasks
2. KL divergence not reduced (P2 fails)
3. Final performance < 90% of baseline
4. Training instability despite projection

### 1.7 SOTA Baseline

| Method | Adaptation Metric | Performance | Year |
|--------|-------------------|-------------|------|
| DreamerV3 | 500K to 90% | Baseline | 2023 |
| TD-MPC2 | 250K (~2x) | 1.5-2x faster | 2024 |
| BPG (target) | 100-170K | 3-5x faster | 2026 |

### 1.8 Statistical Design

- Effect size (Cohen's d): 0.8
- Required runs: n ≥ 25
- Tasks: 12 (5 DMC + 5 Meta-World + 2 CARLA)
- Seeds: 5 per task = 60 total runs
- Test: Paired t-test, α = 0.05 (one-tailed)
- Ablations: A1 (no projection), A2 (fixed weights), A3 (smaller encoder)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does BPG train to convergence without instability?
- Verification: Training stability
- Critical: MUST PASS

**SH2 (Mechanism):**
Does shared latent dynamics reduce policy-world mismatch?
- Decomposes to: H-M1, H-M2, H-M3 (3 sub-hypotheses)
- Verification: Ablation studies

**SH3 (Comparison):**
Does BPG achieve 3-5x faster adaptation than baselines?
- Verification: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses:** 5 (SH1 + SH2×3 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-BPG-v1
- [x] Confidence: 0.85
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 3 testable predictions (P1 primary)
- [x] Falsification criteria (4 conditions)
- [x] Baselines identified
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Compute:** 8 GPU-hours/task on A100 estimated
2. **Hyperparameters:** Grid search τ ∈ {-0.5, 0, 0.5}, weight init ∈ {0.5, 1.0}
3. **CARLA scaling:** May need hierarchical encoding for visual complexity

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*

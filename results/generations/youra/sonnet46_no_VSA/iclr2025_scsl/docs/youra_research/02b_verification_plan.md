# Verification Plan: Per-Sample Hessian Trace Trajectory as Annotation-Free DFR Proxy

**Date:** 2026-08-04
**Hypothesis ID:** H-E3
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ERM training with SGD on Waterbirds (ResNet-50, ImageNet pretrained, 95% spuriosity,
SGD, 50 epochs, checkpoints at t∈{0,1,5,10,20,50}),
IF per-sample last-fc Hessian trace (K=50 Hutchinson via torch.func vmap+vjp) is measured
at each checkpoint,
THEN the trace ratio R(t) = mean_minority_trace(t) / mean_majority_trace(t) rises from ≈1.0
at initialization, reaches a peak at t* (argmax_t R(t)), and provides a predictive signal
(AUROC ≥ 0.85 at t*, epoch-0 AUROC < 0.70),
BECAUSE ERM spurious feature exploitation creates differential loss landscape curvature:
majority samples gain confidence (low p(1-p), flat loss surface) while minority samples
remain near the decision boundary (high p(1-p), curved loss surface), traceable to the
spectral imbalance mechanism identified in LaBonte et al. 2024.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in per-sample last-fc Hessian trace between minority
and majority samples that is not fully explained by per-sample loss value and gradient norm
(AUROC improvement ≤ 0 over loss-only baseline within confidence-matched bins).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds v1.0 (standard) | Canonical spurious correlation benchmark with 95% spuriosity, 4 groups (2 class × 2 background). 4795 train samples, minority groups 1+2 = 240 samples (5%). Group labels available for AUROC computation (not used in proxy selection). |
| **Model** | ResNet-50 (CNN, pretrained) | Standard Waterbirds baseline. h-e2-k confirmed signal at K=50. Last fc layer is 2048→2 linear head. vmap+grad pipeline validated (h-e2-k code reusable). |

**Dataset Details:**
- Source: Sagawa et al. 2019 (arXiv:1911.08731)
- Path: /home/PrayPrey/data/waterbirds_v1.0/

**Model Details:**
- Type: CNN, pretrained
- Source: torchvision IMAGENET1K_V1

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| DFR (Kirichenko et al. 2022) | WGA ~88-90% | Waterbirds |
| JTT (Liu et al. 2021) | WGA ~80-84% | Waterbirds |
| SELF (LaBonte et al. 2023) | WGA ~82-87% | Waterbirds |
| EVaLS (sharif-ml-lab) | WGA ~80-86% | Waterbirds |
| ERM baseline | WGA ~72% | Waterbirds |
| Loss-guided DFR | — | Waterbirds |
| Gradient-norm-guided DFR | — | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Minority samples remain near decision boundary (p∈[0.3,0.7]) during Phase I (epochs 1-20) | h-e1 snapshot: t*=1 for 3/5 seeds, t*=4 for 2/5 seeds; gradient norm AUROC=0.940 at t* implies asymmetry before saturation | Trace signal collapses (p(1-p)→0); DFR proxy fails; Route to Phase 0 |
| A2 | Epoch-0 Hessian trace AUROC < 0.70 (ERM-induced signal, not pretrained artifact) | h-e2 failure lesson: gradient direction AUROC=0.987 at epoch 0; Hessian trace is a different signal family — may behave differently | Signal is another pretrained artifact; trajectory hypothesis collapses; Route to Phase 0 |
| A3 | Feature diversity ‖x_i‖² systematically higher for minority samples within same class | LaBonte et al. 2024: minority covariance spectral norm > majority within class | Trace reduces purely to confidence p_i(1-p_i); ΔAUROC within bins fails |
| A4 | K=50 Hutchinson CV ≤ 10% across probe resampling for last-fc ResNet-50 | h-e2-k: K=50 vs analytical gap=0.0059 < 0.05; standard for Hutchinson at K=50 | Hutchinson noise dominates; must increase K to 100+ or use diagonal Fisher |
| A5 | Top-k% highest-trace at t* has minority representation > 5× natural prevalence | h-e2-k AUROC=0.913: at threshold selecting top-10%, minority should be ≥40-50% vs natural 5% | Proxy majority-dominated; WGA does not improve; adjust k% or use class-conditional selection |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First per-sample Hessian trace trajectory measurement across training checkpoints for minority/majority discrimination in ERM on real image data (Waterbirds). First annotation-free DFR proxy using second-order curvature statistics.

**Key Innovation:** Connecting LaBonte 2024's static group-level spectral imbalance observation to a dynamic per-sample training signal (trace trajectory), and leveraging this for annotation-free DFR via mechanistically grounded proxy selection at argmax-t* checkpoint.

**Scope Reduction (71%):** 5 of 7 Phase 2A claims are BUILD_ON (established facts — not re-tested):
- K=50 Hutchinson AUROC=0.9130 at specific checkpoint ✓ BUILD_ON
- Gradient norm AUROC=0.9402 at t* ✓ BUILD_ON
- ERM features required for DFR WGA > 80% ✓ BUILD_ON
- LaBonte 2024 spectral imbalance ✓ BUILD_ON
- Gradient direction is pretrained artifact (epoch-0 AUROC=0.987) ✓ BUILD_ON

Only 2 claims require new verification (PROVE_NEW):
1. Per-sample Hessian trace trajectory (rise-peak-decline of R(t)) with epoch-0 control
2. Annotation-free DFR via trace proxy achieving WGA ≥ 85%

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E3 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E3 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E3: Per-Sample Hessian Trace Trajectory Existence**

**Statement:** Under ERM training on Waterbirds (ResNet-50, SGD, 50 epochs), if per-sample
last-fc Hessian trace (K=50 Hutchinson) is measured at checkpoints t∈{0,1,5,10,20,50},
then AUROC(t*) ≥ 0.85 for minority membership prediction, with epoch-0 AUROC < 0.70 and
Spearman ρ ≥ 0.8 across the rising segment, because ERM Phase I dynamics create transient
curvature asymmetry between minority and majority samples.

**Rationale:**
h-e2-k confirmed Hessian trace achieves AUROC=0.913 at a single checkpoint. This hypothesis
extends that finding to the full trajectory: we need to confirm the signal is ERM-induced
(not a pretrained artifact) and that it exhibits the predicted rise-peak-decline pattern.
The epoch-0 AUROC gate is the decisive first test — if it fails (AUROC≥0.70), we route
back to Phase 0 immediately.

**Variables:**
- Independent: Training checkpoint t∈{0,1,5,10,20,50}
- Dependent: AUROC minority membership prediction; Trace ratio R(t); Spearman ρ
- Controlled: ResNet-50 (IMAGENET1K_V1), Waterbirds v1.0, SGD, K=50, 5 seeds

**Verification Protocol:**
1. Run pilot (1 seed, 5 epochs): compute epoch-0 AUROC; STOP if AUROC(t=0) ≥ 0.70.
2. Full training (5 seeds, 50 epochs): save checkpoints at t∈{0,1,5,10,20,50}.
3. At each checkpoint: compute per-sample trace via K=50 Hutchinson (last-fc only).
4. Compute AUROC vs group labels, R(t) = mean_minority/mean_majority, identify t* = argmax R(t).
5. Fit Spearman ρ over rising segment t=0 to t*; aggregate across seeds.

**Success Criteria (PoC: pre-registered gates):**
- Primary: AUROC(t*) ≥ 0.85 AND AUROC(t=0) < 0.70 AND Spearman ρ ≥ 0.8 in ≥4/5 seeds
- Secondary: Hutchinson CV ≤ 10% at K=50 (stability gate)

**Failure Response:**
- IF epoch-0 AUROC ≥ 0.70 → ABANDON (pretrained artifact, Route to Phase 0)
- IF AUROC(t*) < 0.80 in ≥2/5 seeds → PIVOT (investigate alternative signal families)
- IF Spearman ρ < 0.6 → EXPLORE (trajectory may be non-monotonic; examine R(t) profile)

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (SH1_existence), Section 1.6 (P1)

---

**H-M1: ERM Phase I Spurious Feature Exploitation — Differential Confidence**

**Statement:** Under ERM training on Waterbirds, if SGD exploits spurious correlation
(background as shortcut), then majority samples gain confidence rapidly (p_majority→1)
while minority samples remain near decision boundary (p_minority∈[0.3,0.7]) during Phase I
(epochs 1-20), because SGD provably learns spurious features first (LaBonte & Muthukumar 2026).

**Rationale:**
This is the causal root of the entire mechanism. Without differential confidence trajectories,
the trace asymmetry predicted in H-E3 has no mechanistic basis. Verifying minority confidence
stays in [0.3,0.7] at t* is Assumption A1 — failure here routes back to Phase 0.
This step is the mechanism sanity check that justifies all subsequent hypotheses.

**Variables:**
- Independent: Training checkpoint t∈{0,1,5,10,20,50}
- Dependent: Mean minority confidence p_minority(t); Mean majority confidence p_majority(t)
- Controlled: ResNet-50, Waterbirds, SGD, 5 seeds

**Verification Protocol:**
1. At each checkpoint (from H-E3 training run): extract per-sample predicted confidence.
2. Compute mean p_minority(t) and p_majority(t) per checkpoint.
3. Verify p_minority(t*) ∈ [0.3, 0.7] (boundary condition for mechanism).
4. Verify p_majority(t*) > 0.80 (saturation condition).
5. Plot confidence trajectories per seed; aggregate statistics.

**Success Criteria (PoC: direction-based):**
- Primary: p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds
- Secondary: p_majority(t*) > 0.80 in ≥4/5 seeds (saturation confirmed)

**Failure Response:**
- IF p_minority(t*) < 0.3 → ABANDON (confidently wrong minority; trace signal collapses; Route to Phase 0)
- IF p_majority(t*) < 0.80 → EXPLORE (majority not yet saturated; extend training epochs)

**Dependencies:** H-E3 (reuses checkpoints from existence experiment)

**Source:** Phase 2A Section 1.3 (causal step 1), Assumption A1

---

**H-M2: Differential Confidence → Differential Last-FC Hessian Trace**

**Statement:** Under ERM training on Waterbirds at t*, if minority samples have higher
confidence entropy (p(1-p)) and feature diversity (‖x_i‖²) than majority, then
Tr(H_i^fc) ∝ ‖x_i‖² p_i(1-p_i) is systematically elevated for minority samples,
even within narrow confidence bins (ΔAUROC ≥ 0.10 over loss-only baseline),
because the algebraic decomposition of last-fc Hessian trace reveals two independent
channels — feature diversity (LaBonte 2024 spectral imbalance) and differential confidence.

**Rationale:**
This step falsifies the H0 alternative that trace signal is merely reparameterized loss/confidence.
If ΔAUROC within confidence bins < 0.05, trace adds nothing beyond first-order signals and
the mechanism collapses. The KS test and ΔAUROC together establish that the second-order
(curvature) signal is genuinely informative beyond loss value alone.

**Variables:**
- Independent: Training checkpoint t* (optimal from H-E3)
- Dependent: ΔAUROC of trace over loss within confidence bins (width 0.02); KS test p-value
- Controlled: Confidence bin width = 0.02 (pre-registered); 5 seeds; same checkpoints as H-E3

**Verification Protocol:**
1. At t*: bin all training samples by predicted confidence p_i (bins of width 0.02).
2. Within each occupied bin: apply two-sided KS test on trace distributions (minority vs majority).
3. Compute AUROC of trace vs group labels within confidence-matched pairs (ΔAUROC over loss-only).
4. Report KS p-values per bin and across-bin summary; report ΔAUROC per seed and aggregated.
5. Compare minority vs majority ‖x_i‖² norms as direct feature diversity check.

**Success Criteria (PoC: direction-based):**
- Primary: ΔAUROC ≥ 0.10 over loss-only baseline within bins in ≥4/5 seeds
- Secondary: KS test p < 0.01 for majority of occupied bins in ≥4/5 seeds

**Failure Response:**
- IF ΔAUROC < 0.05 → ABANDON (trace = reparameterized confidence; H0 supported)
- IF KS non-significant across all bins → PIVOT (explore alternative independence measures)

**Dependencies:** H-M1 (confidence trajectories verified, t* identified)

**Source:** Phase 2A Section 1.3 (causal step 2), Prediction P2

---

**H-M3: Trace Ratio R(t) Peak-Decline — Phase I→II Transition**

**Statement:** Under ERM training on Waterbirds, if R(t) = mean_minority_trace(t)/mean_majority_trace(t)
is tracked across t∈{0,1,5,10,20,50}, then R(t) rises from ≈1.0 at t=0, reaches peak at
t* (argmax R(t)), then declines as ERM drives minority to confident misclassification (Phase II
onset), because the Phase I→II transition in LaBonte & Muthukumar 2026 predicts minority
samples eventually enter confident misclassification regime (p(1-p)→0).

**Rationale:**
The peak-decline structure of R(t) is both the mechanistic prediction AND the annotation-free
t* selection criterion — no group labels are needed to identify the optimal DFR checkpoint.
This step additionally tests the background-swap specificity: if trace gap does NOT collapse
under background randomization, the signal is not capturing shortcut reliance.

**Variables:**
- Independent: Training checkpoint t∈{0,1,5,10,20,50}
- Dependent: R(t) trajectory profile; background-swap trace gap collapse %
- Controlled: Waterbirds place labels for background-swap; 5 seeds

**Verification Protocol:**
1. Compute R(t) at all checkpoints (from H-E3 data); verify peak at t* then decline.
2. Background-swap: randomize each sample's background using Waterbirds place labels.
3. Retrain or forward-pass through same checkpoints with randomized backgrounds.
4. Compute trace gap collapse = (gap_original - gap_swapped) / gap_original × 100%.
5. Report R(t) trajectory and collapse % per seed and aggregated.

**Success Criteria (PoC: direction-based):**
- Primary: R(t) shows clear rise-peak-decline within t∈{0,1,5,10,20,50} in ≥4/5 seeds
- Secondary: ≥75% trace gap collapse under background-swap in ≥4/5 seeds (specificity gate)

**Failure Response:**
- IF R(t) still rising at t=50 → EXPLORE (Phase I→II transition beyond 50 epochs; extend window)
- IF Gap collapse < 50% → PIVOT (trace may capture generic image complexity, not shortcut)

**Dependencies:** H-M2 (confidence-bin independence established)

**Source:** Phase 2A Section 1.3 (causal step 3), Prediction P1 (Spearman ρ gate)

---

**H-M4: Top-k% Trace Proxy → Annotation-Free DFR WGA ≥ 85%**

**Statement:** Under ERM training on Waterbirds, if top-k% highest-trace training samples
at t* (k tuned on unbalanced validation accuracy) are used as annotation-free proxy for
minority group membership in DFR (L1 logistic regression on ERM-trained ResNet-50 features),
then test WGA ≥ 85% in ≥4/5 seeds AND WGA_trace > WGA_loss + 5% absolute,
because the trace AUROC=0.913 (from h-e2-k) substantially exceeds typical JTT proxy quality
(~80-84%), and ERM-trained (not frozen) features provide sufficient representational capacity
for DFR (Kirichenko 2022, confirmed by h-m4 lesson).

**Rationale:**
This is the downstream application step that connects mechanistic understanding to practical
robustification. h-m4 showed frozen features fail (WGA ceiling 62%); this hypothesis uses
ERM-trained features (the key fix). The trace proxy is predicted to outperform loss-guided DFR
by ≥5% because it captures a genuinely different signal channel (second-order curvature) not
reducible to first-order signals.

**Variables:**
- Independent: Proxy selection signal (trace vs loss vs gradient norm vs JTT); k% threshold
- Dependent: Test WGA on Waterbirds; ΔWGA(trace vs loss)
- Controlled: izmailovpavel DFR pipeline (C_OPTIONS, REG=l1); ERM features; 5 seeds; same t*

**Verification Protocol:**
1. At t*: select top-k% training samples by trace (k∈{5,10,15,20,25,30}%).
2. Tune k on unbalanced validation accuracy (no group labels used for tuning).
3. Run DFR: L1 logistic regression (izmailovpavel pipeline) on ERM ResNet-50 features.
4. Evaluate test WGA on Waterbirds; report per-seed and mean ± std.
5. Compare to baselines: loss-guided DFR, gradient-norm DFR, JTT, ERM, oracle DFR.

**Success Criteria (PoC: pre-registered gates):**
- Primary: WGA ≥ 85% in ≥4/5 seeds AND WGA_trace > WGA_loss + 5% absolute in mean
- Secondary: WGA_trace > JTT WGA (annotation-free SOTA ~80-84%)

**Failure Response:**
- IF WGA < 80% in ≥2/5 seeds → PIVOT (proxy minority representation check; adjust k% or class-conditional)
- IF WGA_trace ≤ WGA_loss + 2% → EXPLORE (trace adds no DFR utility beyond loss)

**Dependencies:** H-M3 (t* confirmed, trajectory specificity verified)

**Source:** Phase 2A Section 1.3 (causal step 4), Prediction P3

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E3 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E3 | MUST_WORK | AUROC(t*)≥0.85, epoch-0<0.70, ρ≥0.8 in ≥4/5 seeds | STOP — route to Phase 0 |
| H-M1 | MUST_WORK | p_minority(t*)∈[0.3,0.7] in ≥4/5 seeds | STOP — mechanism collapses; route to Phase 0 |
| H-M2 | SHOULD_WORK | ΔAUROC≥0.10 within bins in ≥4/5 seeds | PIVOT — document as limitation |
| H-M3 | SHOULD_WORK | R(t) peak-decline + ≥75% gap collapse in ≥4/5 seeds | EXPLORE — extend or narrow scope |
| H-M4 | SHOULD_WORK | WGA≥85% AND >loss-DFR+5% in ≥4/5 seeds | PIVOT — adjust proxy strategy |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E3 (existence) | Week 1-2 |
| Gate 1 | MUST_WORK decision | Week 2 |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | Week 3-6 |
| Gate 2 | H-M1 MUST_WORK decision | Week 3 end |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Minority confident misclassification before t* | A1 | H-E3, H-M1, H-M2 | Critical |
| R2: Epoch-0 Hessian trace AUROC ≥ 0.70 (pretrained artifact) | A2 | H-E3 | Critical |
| R3: Feature diversity ‖x_i‖² not elevated for minority | A3 | H-M2 | High |
| R4: K=50 Hutchinson CV > 10% | A4 | H-E3, H-M2, H-M4 | Medium |
| R5: Top-k% proxy is majority-dominated despite high AUROC | A5 | H-M4 | High |

### 4.2 Mitigation Strategies

**R1 (Critical): Minority Confidence Collapse**
- Prevention: Run pilot (1 seed, 5 epochs) to check p_minority(t) before full training.
- Detection: Monitor mean p_minority per epoch during training.
- Response: If p_minority(t) < 0.3 at t=1: ABORT entire pipeline, route to Phase 0. Signal window collapsed.

**R2 (Critical): Pretrained Artifact**
- Prevention: Compute epoch-0 AUROC FIRST in pilot before any further training.
- Detection: AUROC at t=0 checkpoint (before any Waterbirds training).
- Response: If AUROC(t=0) ≥ 0.70: ABORT immediately. Signal is pretrained artifact (h-e2 repeat). Route to Phase 0 for signal redesign.

**R3 (High): No Feature Diversity Advantage**
- Prevention: Directly measure ‖x_i‖² norms per group at each checkpoint.
- Detection: Within-class comparison of ‖x_i‖² (minority vs majority).
- Response: If ‖x_i‖² equal across groups: trace signal reduces to confidence; H-M2 ΔAUROC will fail. Document as limitation, narrow claim.

**R4 (Medium): Hutchinson Instability**
- Prevention: K=50 confirmed stable by h-e2-k (analytical gap=0.0059 < 0.05).
- Detection: Compute CV across 5 probe resamplings at a representative checkpoint.
- Response: If CV > 10%: increase K to 100 (2× compute) or switch to diagonal Fisher approximation.

**R5 (High): Proxy Minority Underrepresentation**
- Prevention: Verify minority fraction in selected top-k% subset after proxy selection.
- Detection: Count minority samples in top-k% vs expected from AUROC.
- Response: If minority fraction < 10× natural prevalence (i.e., < ~5%): use class-conditional selection (select top-k% within each class separately).

### 4.3 Baseline Failure Pattern Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| h-m4 frozen features → WGA 62% ceiling | Using wrong feature layer | Use ERM-trained features (explicitly verified) |
| h-e2 gradient direction → pretrained artifact | Signal family contamination | Epoch-0 control gate (mandatory first test) |
| JTT first-order proxy → WGA 80-84% | Marginal improvement over SOTA | Pre-register ≥5% absolute gap threshold |

---

## 5. Dependency Graph (DAG) and Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E3 (Existence — no dependencies)
    Gate Type: MUST_WORK
         │
         ▼
[Level 1 - Mechanism Root]
    H-M1 ← H-E3 (Differential Confidence)
    Gate Type: MUST_WORK
         │
         ▼
[Level 2 - Mechanism]
    H-M2 ← H-M1 (Curvature Independence)
    Gate Type: SHOULD_WORK
         │
         ▼
[Level 3 - Mechanism]
    H-M3 ← H-M2 (Trajectory Specificity)
    Gate Type: SHOULD_WORK
         │
         ▼
[Level 4 - Application]
    H-M4 ← H-M3 (DFR Proxy Application)
    Gate Type: SHOULD_WORK

═══════════════════════════════════════════════════════════
Critical Path: H-E3 → H-M1 → H-M2 → H-M3 → H-M4
All sequential — no parallelization in this chain.
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E3 | None | MUST_WORK |
| 1 | H-M1 | H-E3 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Verification Phases with Gate Conditions

**Phase 1 — Foundation (2 weeks)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E3 | Trajectory AUROC ≥ 0.85, epoch-0 < 0.70, ρ ≥ 0.8 | MUST PASS |

→ **Gate 1**: If H-E3 fails → STOP entire pipeline, route to Phase 0.

**Phase 2 — Core Mechanisms (4 weeks)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E3 | MUST PASS (minority confidence in boundary) |
| H-M2 | H-M1 | Should pass (ΔAUROC independence) |
| H-M3 | H-M2 | Should pass (trajectory specificity) |
| H-M4 | H-M3 | Should pass (DFR WGA ≥ 85%) |

→ **Gate 2**: H-M1 must pass (mechanism root). H-M2/3/4 failures narrow scope but do not invalidate.

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E3           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  [Gate 2]       │         │        ◆│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │     ████│         │
  H-M4           │         │         │         │ ████████│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E3 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E3) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)
Slack Available: 0 weeks (all sequential)
Execution Mode: Sequential chain (data reused across phases)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E3)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none)

Verification Phases: 2
1. Foundation (H-E3) — 2 weeks
2. Mechanisms (H-M1 to H-M4) — 4 weeks

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Key Reuse: H-E3 checkpoints reused by H-M1 to H-M3 (compute amortized)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: Per-sample last-fc Hessian trace trajectory exhibits
transient asymmetry (R(t) rise-peak-decline) driven by ERM spurious
feature exploitation, and the peak t* identifies the optimal checkpoint
for annotation-free DFR proxy selection (WGA ≥ 85%).

Supporting Evidence:
1. h-e2-k confirms AUROC=0.913 at specific checkpoint (signal exists)
2. Algebraic decomposition Tr ∝ ‖x_i‖² p_i(1-p_i) ties two independent
   channels (spectral imbalance + differential confidence) to trace
3. Kirichenko 2022 DFR + ERM features → WGA 88-90% (upper bound confirmed)

Strengths:
- Grounded in established theory (LaBonte 2024/2026)
- Two independent mechanistic channels predict same direction
- Reuses validated infrastructure (h-e2-k pipeline, h-e1 training)

Expected Outcomes:
- P1: AUROC(t*)≥0.85, epoch-0<0.70, ρ≥0.8 in ≥4/5 seeds
- P2: ΔAUROC≥0.10 within confidence bins in ≥4/5 seeds
- P3: DFR WGA≥85% AND >loss-DFR+5% in ≥4/5 seeds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): There is no significant difference in per-sample
last-fc Hessian trace between minority and majority samples that is not
fully explained by per-sample loss value and gradient norm (AUROC
improvement ≤ 0 over loss-only baseline within confidence-matched bins).

Counter-Arguments:
1. Trace = reparameterized loss: if ‖x_i‖² is equal across groups,
   Tr ≈ f(p_i(1-p_i)) = f(loss) — no independent signal
2. Pretrained artifact risk: h-e2 showed gradient direction AUROC=0.987
   at epoch 0; Hessian trace may behave similarly
3. Scope collapse: Waterbirds 95% spuriosity may drive minority to
   confident misclassification before t*, collapsing the signal window

Potential Failure Points:
- R1: p_minority collapses below 0.3 early; trace signal disappears
- R2: Epoch-0 AUROC ≥ 0.70 (another pretrained artifact)
- R3: No ‖x_i‖² advantage for minority (A3 violated)

H0 Supported If:
- AUROC(t=0) ≥ 0.70 (pretrained artifact)
- AUROC(t*) < 0.80 in ≥2/5 seeds
- ΔAUROC within confidence bins < 0.05
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:
The hypothesis H-E3 presents a testable claim grounded in two independent
theoretical mechanisms and one confirmed empirical predecessor (h-e2-k).
However, H0 raises valid concerns: the pretrained artifact risk (h-e2
lesson) and the trace=confidence confound are real and pre-registered
as decisive gates.

Resolution Path:
The verification plan addresses this dialectic through:
1. Epoch-0 AUROC control (decisive first gate — rules out pretrained artifact)
2. Confidence-bin ΔAUROC test (rules out trace = reparameterized confidence)
3. Background-swap specificity (rules out generic image complexity signal)
4. Sequential gates allow early failure detection before expensive DFR runs

Conditions for Thesis Support:
- All MUST_WORK gates pass (H-E3, H-M1)
- AUROC(t*) ≥ 0.85 AND epoch-0 < 0.70 confirmed in ≥4/5 seeds
- Mechanism chain validates through H-M2 independence test

Conditions for Antithesis Support:
- Epoch-0 AUROC ≥ 0.70 (decisive failure)
- H-M1 failure: p_minority < 0.3 (mechanism collapses)
- ΔAUROC < 0.05 within confidence bins

Nuanced Outcomes:
1. Full Support: H-E3 + all H-M pass → Novel annotation-free DFR method
2. Partial Support: H-E3 + H-M1 pass, H-M4 marginal → Mechanistic insight without DFR application
3. No Support: H-E3 epoch-0 gate fails → Route to Phase 0 for signal redesign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Trace AUROC≥0.85 at t* (BUILD_ON: h-e2-k) | Pretrained artifact (h-e2 lesson) | Epoch-0 AUROC gate (first test) |
| Mechanism | Two independent channels (diversity + confidence) | Trace = reparameterized loss | ΔAUROC within confidence bins |
| Trajectory | Rise-peak-decline driven by Phase I/II | No trajectory structure | Spearman ρ gate; visual R(t) profile |
| Application | WGA≥85% (above annotation-free SOTA) | k% proxy minority-dominated | Direct minority fraction check in top-k% |

**Overall Robustness Score:** Medium-High (strong theory + confirmed predecessor; two hard gates)

**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Per-sample Hessian trace trajectory (H-E3) as annotation-free DFR proxy
- ID: H-E3, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (71% scope reduction from Phase 2A established facts)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4, H-C: 0)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 (Foundation: MUST_WORK; Mechanism Root: MUST_WORK)

**Risk Assessment:** Medium-High
- Primary concerns: Pretrained artifact (A2 — decisive epoch-0 gate); minority confidence collapse (A1 — pilot check before full training)

**Immediate Action:** Run pilot (1 seed, 5 epochs) — compute epoch-0 AUROC FIRST before committing to full training.

### 7.2 Verification Execution Order

**Phase 1: Foundation (2 weeks)**
- Pilot (1 seed, 5 epochs): epoch-0 AUROC gate — STOP if ≥ 0.70
- Full training (5 seeds, 50 epochs): checkpoints at t∈{0,1,5,10,20,50}
- H-E3: AUROC(t*)≥0.85, epoch-0<0.70, Spearman ρ≥0.8 in ≥4/5 seeds
- Gate 1: MUST PASS — failure routes to Phase 0

**Phase 2: Core Mechanisms (4 weeks)**
- H-M1: p_minority(t*)∈[0.3,0.7] — MUST PASS (reuses Phase 1 checkpoints)
- H-M2: ΔAUROC≥0.10 within confidence bins — SHOULD PASS
- H-M3: R(t) peak-decline + ≥75% background-swap gap collapse — SHOULD PASS
- H-M4: DFR WGA≥85% AND >loss-DFR+5% — SHOULD PASS

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation — H-E3):** Epoch-0 AUROC < 0.70 required
   - FAIL (epoch-0 ≥ 0.70) → STOP, route to Phase 0 (pretrained artifact)
   - FAIL (AUROC(t*) < 0.80) → PIVOT, explore alternative signal families
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanism Root — H-M1):** p_minority(t*)∈[0.3,0.7]
   - FAIL (p_minority < 0.3) → STOP, route to Phase 0 (mechanism collapses)
   - PASS → Proceed to H-M2/3/4 (failures narrow scope, do not invalidate)

### 7.4 Open Questions

- What is the epoch-0 Hessian trace AUROC? (Decisive gate: < 0.70 required)
- What is the peak epoch t* across 5 seeds? (Expected t*∈{1,5,10} from h-e1 snapshot)
- Does minority confidence remain in [0.3,0.7] at t*? (Mechanism contingency A1)
- What k% maximizes WGA without group labels? (Expected 10-20% from AUROC ~0.91)
- Does trace gap collapse under background-swap? (Shortcut specificity test)

### 7.5 Recommendations

1. **Immediate Actions:**
   - Run pilot (1 seed, 5 epochs) — epoch-0 AUROC is the decisive first gate
   - Verify minority confidence trajectory before committing 5-seed full training
   - Reuse h-e2-k Hutchinson pipeline (vmap+vjp, last-fc) — no new infrastructure needed

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Phase 1 is the highest-stakes: 2 weeks but two hard MUST_WORK gates
   - Phase 1 checkpoints are fully reused by H-M1/2/3 (compute amortized)

3. **Failure Management:**
   - Any MUST_WORK gate failure → document findings in Serena memory, route to Phase 0
   - SHOULD_WORK gate failures → document as scope limitations, proceed to paper

---

## Appendices

### A. Phase 2A Reference

- **Source:** docs/youra_research/03_refinement.yaml (ID: H-E3)
- **Synthesis:** docs/youra_research/02_synthesis.yaml
- **Established Facts Scope Reduction:** 71% (5/7 BUILD_ON, 2/7 PROVE_NEW)

### B. MCP Tool Usage Summary

- **Total MCP calls:** 4
- **Tools:** mcp__clearThought__scientificmethod (2× hypothesis stage, 2× experiment stage)
  - Inquiry 1: H-E3-existence-verification
  - Inquiry 2: H-M3-mechanism-chain

### C. Infrastructure Reuse

- **h-e2-k pipeline:** K=50 Hutchinson vmap+vjp (last-fc) — directly reusable
- **h-e1 training loop:** ERM ResNet-50 on Waterbirds — extend with checkpoint saving
- **izmailovpavel DFR pipeline:** C_OPTIONS, REG=l1, ERM features — directly reusable
- **Dataset:** /home/PrayPrey/data/waterbirds_v1.0/ — confirmed present

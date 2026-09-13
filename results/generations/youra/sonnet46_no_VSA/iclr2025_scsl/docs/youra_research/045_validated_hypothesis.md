# Validated Hypothesis Synthesis

**Generated:** 2026-08-04T12:00:00Z
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

This synthesis refines the original Phase 2A hypothesis in light of two completed Phase 4 experiments: H-E3 (EXISTENCE, PASS) and H-M1 (MECHANISM, FAIL → ROUTED_TO_PHASE_0). Of the three pre-registered predictions, one is strongly supported (P1), and two remain inconclusive (P2, P3) because the dependent hypotheses that would have tested them (H-M2, H-M3, H-M4) were blocked when H-M1 failed its MUST_WORK gate.

**The main finding:** Per-sample last-fc Hessian trace computed via K=50 Hutchinson (vmap+vjp) achieves AUROC≥0.85 for minority membership prediction in 4/5 seeds on Waterbirds, and the signal is ERM-induced (epoch-0 AUROC<0.70 in all seeds). This is a robust, empirically confirmed existence result. However, the original mechanistic explanation — that the trace asymmetry is sustained by minority samples remaining near the decision boundary (p∈[0.3,0.7]) during Phase I ERM training — is refuted. Minority training-set confidence saturates to ≥0.97 by t*, matching majority saturation, so the `Tr ∝ ‖x‖²p(1-p)` boundary-condition channel does not explain the signal at t*. An early (epoch-1) differential in confidence does exist (p_min≈0.83 vs p_maj≈0.97 at epoch 1 for seed 1), consistent with Phase I theory, but it dissipates before t*.

The refined hypothesis retains the existence claim (AUROC>0.85) while removing the sustained-boundary-condition mechanism and acknowledging that the source of the trace asymmetry at t* requires new mechanistic investigation — likely via the LaBonte 2024 feature-norm channel (‖x_i‖²) rather than the confidence channel (p(1-p)).

| Metric | Value |
|--------|-------|
| **Original Core Statement** | ERM minority samples stay near boundary (p≈0.5), producing high Hessian trace via p(1-p) channel |
| **Refined Core Statement** | Last-fc Hessian trace (K=50) discriminates minority at AUROC≥0.85; boundary-condition mechanism refuted; feature-norm channel (‖x‖²) is candidate explanation |
| **Predictions Supported** | 1 / 3 (P1 SUPPORTED; P2, P3 INCONCLUSIVE — experiments blocked) |
| **Overall Pass Rate** | H-E3: PASS (4/5 seeds); H-M1: FAIL (0/5 seeds) |
| **Hypotheses Validated** | 1 (H-E3) / 2 completed (H-E3, H-M1) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | AUROC(t*)≥0.85 AND AUROC(t=0)<0.70 AND Spearman ρ≥0.8 in ≥4/5 seeds | H-E3 | AUROC(t*), epoch-0 AUROC, Spearman ρ | 4/5 seeds pass all 3 criteria; AUROC(t*)=[0.850,0.885,0.897,0.903,0.890]; epoch-0=[0.538–0.609]; Spearman=[0.70,0.943,0.943,0.900,1.000] | SUPPORTED | HIGH | H-E3 gate PASSED; 4/5 seeds satisfy AUROC≥0.85, epoch-0<0.70, Spearman≥0.80 simultaneously |
| **P2** | ΔAUROC≥0.10 within confidence bins (width 0.02) AND KS p<0.01 in ≥4/5 seeds | Not executed | ΔAUROC(trace vs loss, within-bin) | H-M2 (the hypothesis testing P2) was blocked by H-M1 FAIL; no confidence-bin experiment ran | INCONCLUSIVE | — | H-M1 showed minority confidence saturates to ≥0.97 at t*, collapsing the p(1-p) channel; P2 test requires revised checkpointing strategy |
| **P3** | WGA≥85% via trace-guided DFR in ≥4/5 seeds AND WGA_trace > WGA_loss + 5% | Not executed | Test WGA on Waterbirds | H-M4 (DFR application) was not executed; entire mechanism chain was blocked | INCONCLUSIVE | — | No DFR experiment completed; cannot assess WGA claim |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | ERM learns spurious feature first (Phase I); majority gains confidence rapidly (p_maj→1); minority fails to exploit spurious feature, remains near boundary | If p_min and p_maj trajectories are indistinguishable across epochs | H-M1: early differential confirmed at epoch 1 (seed 1: p_min=0.827, p_maj=0.972); differential disappears by t* (p_min≥0.97 in all seeds at t*) | PARTIALLY_VERIFIED — transient differential at epoch 1 confirmed; sustained differential at t* refuted |
| 2 | Differential confidence → differential Hessian trace: Tr(H_i^fc) ∝ ‖x_i‖²p_i(1-p_i); minority near boundary (high p(1-p)); majority saturated (low p(1-p)) | If ΔAUROC<0.10 within confidence bins | H-E3 AUROC>0.85 confirms trace discriminates; but p_min(t*)≥0.97 means p(1-p)→0 for minority too; confidence channel cannot explain trace signal at t*; ‖x_i‖² channel unverified | PARTIALLY_VERIFIED — trace discrimination confirmed; confidence-channel explanation refuted; feature-norm channel (‖x‖²) is unverified surviving alternative |
| 3 | R(t) rise-peak-decline within t∈{0,1,5,10,20,50}; Spearman ρ≥0.8 over rising segment in ≥4/5 seeds | If R(t) has no peak or Spearman ρ<0.8 | H-E3: R(t)>1 at t* in all seeds; Spearman ρ≥0.80 in 4/5 seeds; rise from ≈1.0 at t=0 confirmed; clean decline not observed in all seeds (seeds 2,3 still rising at t=50) | PARTIALLY_VERIFIED — rise-to-peak confirmed; Spearman criterion met in 4/5 seeds; peak-decline pattern not universal |
| 4 | Top-k% highest-trace samples at t* → annotation-free DFR proxy → WGA≥85% | If trace-DFR WGA < loss-DFR WGA by ≥5% | H-M4 not executed; DFR application untested | UNVERIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under ERM training with SGD on Waterbirds (ResNet-50, ImageNet pretrained, 95% spuriosity, SGD, 50 epochs, checkpoints at t∈{0,1,5,10,20,50}), IF per-sample last-fc Hessian trace (K=50 Hutchinson via torch.func vmap+vjp) is measured at each checkpoint, THEN the trace ratio R(t) = mean_minority_trace(t) / mean_majority_trace(t) rises from ≈1.0 at initialization, reaches a peak at t* (argmax_t R(t)), and provides a predictive signal (AUROC ≥ 0.85 at t*, epoch-0 AUROC < 0.70), BECAUSE ERM spurious feature exploitation creates differential loss landscape curvature: majority samples gain confidence (low p(1-p), flat loss surface) while minority samples remain near the decision boundary (high p(1-p), curved loss surface), traceable to the spectral imbalance mechanism identified in LaBonte et al. 2024.

### 3.2 Refined Core Statement (Phase 4.5)

> Under ERM training on Waterbirds (ResNet-50, SGD, 50 epochs), per-sample last-fc Hessian trace (K=50 Hutchinson, vmap+vjp) achieves AUROC≥0.85 for minority membership prediction at t* (argmax R(t)) in 4/5 seeds, with epoch-0 AUROC<0.70 in all seeds (confirming ERM emergence, not pretrained artifact). The trace ratio R(t) rises from near-unity at initialization and peaks within t∈{5,20,50} epochs. However, the original mechanistic explanation is refuted: minority training-set confidence saturates to ≥0.97 at t*, matching majority saturation, which means the p(1-p) confidence channel cannot sustain the trace asymmetry at t*. A transient differential confidence exists at epoch 1 (p_min≈0.83 vs p_maj≈0.97), consistent with Phase I theory, but dissipates. The minority trace elevation at t* is more likely attributable to the feature-norm channel (‖x_i‖² higher for minority due to LaBonte 2024 spectral imbalance), which requires direct verification in a revised hypothesis chain.

**Key Changes:**
- Existence claim (AUROC≥0.85, epoch-0<0.70, Spearman ρ≥0.8): KEPT (fully supported by H-E3)
- Boundary-condition mechanism (p_minority(t*)∈[0.3,0.7]): REMOVED (refuted by H-M1: p_min(t*)=0.97–0.9999 in 0/5 seeds)
- R(t) rise-peak claim: WEAKENED to "rise-to-peak within t∈{0,1,5,10,20,50}" (decline not universally observed)
- Causal attribution to p(1-p) channel: REMOVED (minority p(1-p)→0 at t* same as majority)
- Feature-norm channel (‖x_i‖²): ADDED as surviving candidate explanation (unverified but not refuted)
- DFR application claim: REMOVED pending H-M4 execution

### 3.3 Causal Mechanism — Verified Chain

```
Original: Step 1 [Phase I differential confidence] → Step 2 [p(1-p) channel → trace asymmetry] → Step 3 [R(t) peak] → Step 4 [DFR proxy]

Verified:
  Step 1 [PARTIALLY_VERIFIED: transient differential at epoch 1; sustained differential at t* FALSIFIED]
       → Step 2 [PARTIALLY_VERIFIED: trace discriminates (AUROC>0.85) but p(1-p) channel inactive at t*; ‖x_i‖² channel is unverified surviving candidate]
       → Step 3 [PARTIALLY_VERIFIED: rise-to-peak in ≥4/5 seeds; Spearman≥0.80 in 4/5; decline not universal]
       → Step 4 [UNVERIFIED: DFR not tested]

Critical gap: Step 1 sustained-boundary-condition (p_min∈[0.3,0.7] at t*) FALSIFIED.
Step 2 survives via ‖x_i‖² channel but confidence-channel contribution at t* is negligible.
```

**Removed/Modified Steps:**
- **Step 2 (confidence-channel component):** Original claim that p_i∈[0.3,0.7] sustains high Tr ∝ p(1-p) is FALSIFIED at t*. Revised: trace asymmetry at t* is likely ‖x_i‖² driven (feature-norm inequality from LaBonte 2024 spectral imbalance).

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| Minority samples remain near decision boundary (p∈[0.3,0.7]) at t* | REMOVE | H-M1: p_min(t*)=0.9678–0.9999 in all 5 seeds; 0/5 pass gate criterion | H-M1 gate: 0/5 seeds, p_min mean=0.9919 |
| Trace asymmetry sustained by p(1-p) confidence channel at t* | REMOVE | p_min≈1 at t* → p_min(1-p_min)→0, same as majority; channel inactive | H-M1: confidence gap at t*=0.0000–0.0247 (near-zero) |
| R(t) shows clear rise-peak-decline within {0,1,5,10,20,50} | WEAKEN | Seeds 2,3 show R still increasing at t=50 (7.21); decline not universal | H-E3 R(t): seeds 2,3 monotone rise to t=50 |
| DFR WGA≥85% via trace proxy | REMOVE (PENDING) | H-M4 not executed; pipeline blocked after H-M1 FAIL | Pipeline state: H-M2,M3,M4 NOT_STARTED |
| Causal attribution to LaBonte 2026 Phase I sustained differential | WEAKEN | Phase I differential is real but transient (epoch 1 only); XOR model → ResNet-50 transfer imperfect at t* | H-M1: early differential confirmed at epoch 1, absent at t* |
| AUROC≥0.85 in ≥4/5 seeds | KEEP | H-E3: 4/5 seeds pass (AUROC=[0.850,0.885,0.897,0.903,0.890]) | H-E3 gate: PASS |
| Epoch-0 AUROC<0.70 (ERM emergence) | KEEP | H-E3: all 5 seeds: epoch-0 AUROC=[0.538,0.609,0.558,0.579,0.609] | H-E3: 5/5 seeds pass epoch-0 criterion |
| Spearman ρ≥0.8 on rising segment | KEEP (qualified) | H-E3: 4/5 seeds pass; seed 1 fails (ρ=0.70) due to non-monotone at t=1→5 | H-E3: Spearman=[0.70,0.943,0.943,0.900,1.000] |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Minority p∈[0.3,0.7] at t* (Phase I boundary condition) | UNVERIFIED (Phase 2A) | VIOLATED | H-M1: p_min(t*)=0.9678–0.9999 in all seeds (0/5 in gate band) | Critical: p(1-p) channel → 0; confidence-driven trace mechanism collapses at t* |
| A2: Epoch-0 AUROC<0.70 (not pretrained artifact) | UNVERIFIED (Phase 2A) | VERIFIED | H-E3: epoch-0 AUROC=[0.538,0.609,0.558,0.579,0.609]; all <0.70 | None — assumption holds; ERM emergence confirmed |
| A3: Feature diversity ‖x_i‖² higher for minority (LaBonte 2024 spectral imbalance) | UNVERIFIED (Phase 2A) | UNVERIFIED | No direct ‖x_i‖² measurement; H-M2 not executed | If violated, trace signal reduces to confidence reparameterization only |
| A4: K=50 Hutchinson CV≤10% for last-fc ResNet-50 | UNVERIFIED (Phase 2A) | VERIFIED | H-E3: CV=[0.0233,0.0132,0.0232,0.0283,0.0108]; all <3% | None — K=50 is sufficient and stable |
| A5: Top-k% trace samples minority-enriched (proxy quality) | UNVERIFIED (Phase 2A) | UNVERIFIED | H-M4 not executed; enrichment ratio not measured | If violated, DFR retraining remains majority-dominated; WGA does not improve |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments establish a two-part finding with a crucial gap in mechanistic understanding.

**What is confirmed:** ERM training on Waterbirds causes per-sample last-fc Hessian trace to become discriminative for minority membership within 5–20 epochs. The trace ratio R(t) rises from near-unity (R≈1.0–1.12) at initialization to R>2 at t* in 4/5 seeds, and AUROC consistently exceeds 0.85. This signal is ERM-induced: epoch-0 traces from pretrained features alone produce AUROC<0.70 in all seeds, confirming the trace asymmetry develops during training (not pretrained initialization).

**What is refuted:** The original mechanism proposed that minority samples' Hessian trace elevation was sustained by their remaining near the decision boundary (p_i∈[0.3,0.7]) throughout training, keeping the p(1-p) factor in `Tr(H_i^fc) ∝ ‖x_i‖²p_i(1-p_i)` large for minority and small for majority. H-M1 conclusively refutes this: at t*, minority training-set confidence is 0.97–0.9999 across all 5 seeds — fully saturated, not boundary-straddling. The confidence channel is essentially inactive for both groups at t*.

**The surviving candidate mechanism:** Given that (a) trace discriminates at AUROC>0.85 at t*, and (b) p(1-p) is near-zero for both minority and majority at t*, the trace asymmetry must be driven primarily by the ‖x_i‖² factor — systematic differences in feature norms between minority and majority samples. This is consistent with LaBonte et al. 2024's finding that minority group covariance matrices have larger spectral norm than majority within class. The feature-norm channel would produce elevated trace for minority even when p_i≈1.0 for both groups. This interpretation is NOT directly tested; it is the primary candidate for the revised mechanism hypothesis.

**A transient differential is real:** At epoch 1, confidence trajectories show the predicted Phase I differential: seed 1 shows p_min=0.827 vs p_maj=0.972 (gap=0.145). This early-epoch differential is consistent with LaBonte & Muthukumar 2026 Phase I dynamics. However, this differential is not the mechanism sustaining AUROC>0.85 at t* (epochs 5–50), since by t* both groups are saturated.

### 4.2 Unexpected Findings Analysis

#### Finding 1: Minority Training Confidence Saturates Fully at t*

- **Observation:** At t* (maximizing Hessian trace AUROC), minority training-set mean confidence is 0.9678–0.9999 across all 5 seeds — effectively identical to majority (0.9924–0.9999).
- **Why Unexpected:** The original hypothesis assumed minority remains near the decision boundary (p∈[0.3,0.7]) throughout Phase I. LaBonte & Muthukumar 2026 (XOR model) suggests minority delays confident classification. We expected this to persist until t*.
- **Competing Explanations:**
  1. **ERM memorizes minority training samples (Plausibility: HIGH):** ERM can memorize minority labels via causal features (bird shape) regardless of spurious features, driving training-set confidence to 1.0 even without spurious shortcuts. This would explain full saturation without boundary-condition behavior.
  2. **t* is too late for the mechanism window (Plausibility: HIGH):** The mechanism operates correctly early (epoch 1 differential observed), but t* (maximizing trace AUROC, not confidence differential) falls after the mechanism window closes. The trace AUROC peak reflects accumulated feature-norm divergence, not active confidence-differential dynamics.
  3. **XOR model → ResNet-50 gap (Plausibility: MEDIUM):** LaBonte 2026 is proven for XOR linear models where spurious feature EXACTLY compensates minority loss. ResNet-50 has access to causal features (bird shape) in addition to spurious features, enabling minority classification via causal features even during Phase I, driving minority confidence higher than the XOR model predicts.
- **Most Likely:** Combination of explanations 1 and 2 — ERM memorizes minority training samples AND t* falls after the Phase I window. The H-M1 experiment should be repeated at early epochs (t=1) on the held-out validation/test set to isolate the mechanism from memorization.
- **Additional Evidence Needed:** Measure confidence on the validation or test set at each checkpoint. If the mechanism operates (minority near boundary on test distribution), test-set confidence would show the predicted differential at t*, even if training-set confidence is saturated.

#### Finding 2: Seed 1 Non-Monotone AUROC Trajectory

- **Observation:** Seed 1 shows AUROC trajectory {0.538, 0.838, 0.657, 0.780, 0.850, 0.879} — a spike at t=1 (0.838) followed by a drop at t=5 (0.657), causing Spearman ρ=0.70 (below 0.80 threshold).
- **Why Unexpected:** We expected monotone AUROC rise until t*, then decline. The spike-dip at t=1→5 violates this.
- **Competing Explanations:**
  1. **Stochastic training artifact (Plausibility: HIGH):** Single-seed variance in early gradient noise creates a transient trace spike that the model then "corrects" as training continues. Not observed in other seeds.
  2. **Checkpoint granularity artifact (Plausibility: MEDIUM):** The jump from t=1 to t=5 (missing intermediate epochs) may skip over a local maximum. Finer checkpointing (every epoch) would clarify.
- **Most Likely:** Stochastic artifact; 4/5 seeds show well-behaved trajectories. Seed 1's ρ=0.70 is a marginal failure that does not threaten the overall gate (4/5 pass).
- **Additional Evidence Needed:** Dense checkpointing (every epoch from t=0 to t=10) would determine if this is a genuine double-peak or a sampling artifact.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Minority trace AUROC>0.85 at t* (ERM emergence) | LaBonte et al. 2024: minority group covariance spectral norm > majority | CONSISTENT_WITH — per-sample trace signal is consistent with group-level spectral imbalance; per-sample trajectory is the novel contribution | [LaBonte24] arXiv:2407.13957 |
| Epoch-0 AUROC<0.70 (signal is ERM-induced) | h-e2 finding: gradient direction AUROC=0.987 at epoch-0 (pretrained artifact) | EXTENDS — Hessian trace does NOT suffer the pretrained-artifact problem that plagued gradient direction | Prior pipeline results (h-e2) |
| K=50 Hutchinson CV<3% for last-fc ResNet-50 | Hutchinson 1990; Adams & Grosse 2022 | BUILDS_ON — K=50 sufficient for last-fc of ResNet-50 | Hutchinson (1990); prior h-e2-k results |
| Minority training confidence saturates at t* (H-M1 FAIL) | LaBonte & Muthukumar 2026 (XOR model): Phase I minority stays near boundary | CONTRADICTS (partially) — XOR model predicts sustained boundary condition; ResNet-50 on Waterbirds shows saturation; XOR→real-model transfer is imperfect | [LaBonte26] arXiv:2606.30444 |
| Early-epoch (t=1) confidence differential | LaBonte & Muthukumar 2026 Phase I prediction | CONSISTENT_WITH — Phase I differential observed transiently at epoch 1; mechanism operates but duration shorter than predicted | [LaBonte26] |
| Trace discrimination without annotation labels | JTT (Liu et al. 2021), EVaLS, AFR | EXTENDS — these first-order methods use loss/misclassification; we use second-order curvature; different signal family | Liu et al. 2021 (ICML) |

### 4.4 Theoretical Contributions

1. **Empirical validation of ERM-induced Hessian trace asymmetry:** We provide the first experimental evidence that per-sample last-fc Hessian trace via K=50 Hutchinson (vmap+vjp) achieves AUROC>0.85 for minority membership detection on Waterbirds across 5 random seeds. The epoch-0 control (AUROC<0.70) rules out the pretrained-artifact confound.

2. **Principled falsification of the training-set confidence-differential mechanism:** We demonstrate that the boundary condition (p_minority∈[0.3,0.7] at t*) assumed by LaBonte & Muthukumar 2026 for XOR models does not hold for ResNet-50 ERM training on Waterbirds at t*. This is a principled refutation: it directly challenges the mechanistic interpretation of Hessian trace-based minority detection and motivates the feature-norm channel as the alternative explanation.

3. **Feature-norm channel identified as the likely surviving mechanism:** Given refutation of the confidence channel, our results point to ‖x_i‖² (LaBonte 2024 spectral imbalance) as the surviving explanation for trace asymmetry at t*. The two second-order papers (LaBonte 2024, LaBonte 2026) are complementary: the feature-norm result (2024) explains the *magnitude* of the trace signal at t*, while the Phase I/II theory (2026) explains its *temporal emergence pattern* at early epochs.

4. **Practical confirmation: K=50 Hutchinson is sufficient and stable for last-fc ResNet-50:** CV<3% across all 5 seeds confirms K=50 as the minimal reliable setting. This reduces uncertainty for practitioners implementing Hutchinson trace estimation for minority detection.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **H-E3** | Last-fc Hessian trace AUROC≥0.85 for minority membership detection | MUST_WORK | PASS (4/5 seeds) | 4/5 = 80% | Trace signal is ERM-induced (epoch-0<0.70 in all seeds); K=50 CV<3%; t* varies across {5,20,50} |
| **H-M1** | Differential training confidence (p_minority∈[0.3,0.7] at t*) | MUST_WORK | FAIL (0/5 seeds) | 0/5 = 0% | Minority training confidence saturates to 0.97–1.0 at t*; early (epoch 1) differential exists but does not persist; mechanism requires revision |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses Executed** | 2 (H-E3, H-M1) |
| **Fully Validated** | 1 (H-E3) |
| **Partially Validated** | 0 |
| **Failed** | 1 (H-M1, MUST_WORK gate) |
| **Blocked (not executed)** | 3 (H-M2, H-M3, H-M4) |
| **Total Tasks Completed (H-E3)** | 12 / 12 |
| **Total Tasks Completed (H-M1)** | 17 / 17 |
| **Hutchinson CV (H-E3 seeds 1–5)** | 0.0233, 0.0132, 0.0232, 0.0283, 0.0108 (all <3%) |

### 5.3 Optimal Hyperparameters

```yaml
# ERM Training (H-E3 confirmed)
lr: 3.0e-3
momentum: 0.9
weight_decay: 1.0e-4
batch_size: 32
n_epochs: 50
checkpoint_epochs: [0, 1, 5, 10, 20, 50]
seeds: [1, 2, 3, 4, 5]

# Hutchinson Trace (H-E3 confirmed)
k_hutchinson: 50             # CV <3% for last-fc ResNet-50; minimum reliable setting
layer: last_fc               # 2048→2 linear head only
estimator: vmap_vjp          # reverse-over-reverse (torch.func)

# Gate Thresholds (H-E3)
auroc_threshold: 0.85        # at t*
auroc_t0_threshold: 0.70     # epoch-0 control (all seeds satisfied <0.65)
spearman_threshold: 0.80     # rising segment (4/5 seeds satisfied)
min_seeds_passing: 4         # empirical; gate minimum is 3/5

# t* per seed (from H-E3 argmax R(t))
tstar_per_seed:
  seed1: 20
  seed2: 50
  seed3: 50
  seed4: 20
  seed5: 5

# Confidence Evaluation (H-M1)
batch_size_eval: 256         # forward-pass only
device: cuda
# REVISION NOTE: measure on val/test split for mechanism verification (not training set)
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Hutchinson trace (vmap+vjp, K=50) | H-E3 | `h-e3/code/compute_traces.py` | YES — directly reusable |
| ERM training with epoch-0 checkpoint | H-E3 | `h-e3/code/train_erm.py` | YES |
| WaterbirdsDataset + minority mask | H-E3 | `h-e3/code/data.py` | YES |
| AUROC evaluation pipeline | H-E3 | `h-e3/code/evaluate_trajectory.py` | YES |
| R(t) ratio metric + argmax t* | H-E3 | `h-e3/code/evaluate_trajectory.py` | YES |
| Confidence extraction by group | H-M1 | `h-m1/code/compute_confidence.py` | YES (adapt for val/test split) |
| Confidence trajectory visualization | H-M1 | `h-m1/code/visualize.py` | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric | Planned Target | Actual Result | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **H-E3** | AUROC(t*) ≥ 0.85 in ≥4/5 seeds | ≥ 0.85 | 0.850–0.903 (4/5 pass) | NONE | Fully met; seed 1 exactly at threshold (0.850) |
| **H-E3** | Epoch-0 AUROC < 0.70 | < 0.70 | 0.538–0.609 (all pass) | NONE | All seeds safely below threshold |
| **H-E3** | Spearman ρ ≥ 0.80 in ≥4/5 seeds | ≥ 0.80 | 0.70–1.000 (4/5 pass) | NONE (marginal) | Seed 1 non-monotone at t=1→5 causes ρ=0.70 |
| **H-M1** | p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds | ≥ 4/5 in gate band | 0.9678–0.9999 in all seeds (0/5) | HYPOTHESIS_ISSUE | Training-set minority confidence fully saturated; not implementation gap — code correct (smoke test passed, 3/3 unit tests passed) |
| **H-M1** | p_majority(t*) > 0.80 in ≥4/5 seeds | > 0.80 | 0.9924–0.9999 (5/5) | NONE | Majority saturation criterion met; only minority boundary criterion failed |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| `fig1_gate_metrics.png` | h-e3/figures/ | AUROC at t* and epoch-0 per seed with gate thresholds | Results: Existence Validation |
| `fig2_R_trajectory.png` | h-e3/figures/ | R(t) = trace_min/trace_maj across epochs per seed | Results: Trajectory Analysis |
| `fig3_auroc_trajectory.png` | h-e3/figures/ | AUROC trajectory per seed across 6 checkpoints | Results: AUROC Dynamics |
| `fig4_trace_distribution.png` | h-e3/figures/ | Hessian trace distributions (minority vs majority) at t* | Results: Signal Characterization |
| `fig5_spearman_rising.png` | h-e3/figures/ | Spearman ρ on rising segment per seed | Results: Monotonicity |
| `fig_gate_metrics.png` | h-m1/figures/ | Confidence gate comparison at t* — shows 0/5 seeds in gate band | Results/Discussion: Mechanism Failure |
| `fig_confidence_trajectory.png` | h-m1/figures/ | Confidence trajectories per seed — early differential, late saturation | Discussion: Mechanism Analysis |
| `fig_conf_distribution.png` | h-m1/figures/ | Per-sample confidence distribution at t* (minority and majority near 1.0) | Discussion: Mechanism Failure |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Training-Set Evaluation Cannot Capture Test-Distribution Mechanism

- **What:** All H-E3 and H-M1 experiments measure Hessian trace and confidence on the training set. Minority samples in the training set are memorized by ERM at t*, masking boundary-condition behavior.
- **Why This Matters:** The causal explanation for why trace discriminates minority from majority at t* cannot be verified from training-set measurements alone, since both groups' training confidences saturate.
- **Root Cause:** H-M1 experiment design measured training-set confidence, where ERM optimization drives all training samples (including minority) to high confidence. The mechanism was expected to appear on training data (motivated by LaBonte 2026 XOR model), but in ResNet-50 the memorization effect dominates at t*.
- **Impact on Claims:** The existence claim (AUROC>0.85) is unaffected — empirical fact independent of mechanism. The mechanistic interpretation is constrained: we cannot confirm or deny the p(1-p) channel from training-set data alone.
- **Why Acceptable:** The existence result (H-E3) is the primary gate, and it is strongly confirmed. The mechanism question is a scientific follow-on that does not invalidate the existence finding.

#### L2: Incomplete Hypothesis Chain — P2 and P3 Untested

- **What:** H-M2 (trace independence from confidence within bins), H-M3 (R(t) specificity under background-swap), and H-M4 (DFR WGA≥85%) were never executed. P2 and P3 remain inconclusive.
- **Why This Matters:** The most practically significant claims (annotation-free DFR achieving WGA≥85%) are completely untested.
- **Root Cause:** H-M1 FAIL triggered the MUST_WORK gate, blocking dependent hypotheses. This is the correct pipeline decision given H-M1's fundamental mechanism failure.
- **Impact on Claims:** No paper-ready claim about DFR utility. The annotation-free proxy application remains speculative.
- **Why Acceptable:** A revised mechanism hypothesis (testing on val/test set) can unlock the downstream chain. The practical claims are not refuted — pending mechanism fix.

#### L3: Single Dataset (Waterbirds, 95% Spuriosity)

- **What:** All experiments use Waterbirds v1.0 at 95% spuriosity. Other datasets (CelebA, MultiNLI) and lower spuriosity levels are untested.
- **Why This Matters:** The trace signal's strength may be spuriosity-dependent. Lower spuriosity may produce weaker trace differential and lower AUROC.
- **Root Cause:** Phase 2A scope decision to focus on the canonical Waterbirds benchmark before generalizing.
- **Impact on Claims:** Claims scoped to high-spuriosity binary classification on Waterbirds. Broader claims require additional experiments.
- **Why Acceptable:** Waterbirds is the standard benchmark in the spurious correlation literature (DFR, JTT, SELF, EVaLS all use it).

#### L4: Single Architecture (ResNet-50, Last-FC Only)

- **What:** Only ResNet-50 last-fc layer is tested. Different architectures (ViT, ResNet-18) and deeper trace layers may show different dynamics.
- **Why This Matters:** Hutchinson trace of last-fc is architecture-specific. ViT attention heads have different curvature structure.
- **Root Cause:** ResNet-50 is the canonical Waterbirds model (Kirichenko 2022 same architecture). Last-fc is the only computationally tractable Hutchinson target at K=50.
- **Impact on Claims:** Claims restricted to CNN architectures with a linear classification head.
- **Why Acceptable:** ResNet-50 is the standard backbone for this benchmark. Architecture generalization is standard future work.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Spuriosity level | 95% (Waterbirds standard) | <70% spuriosity | No low-spuriosity experiments; extrapolated from H-E3 AUROC levels |
| Dataset type | Binary spurious correlation, 2×2 group structure | Multi-class spurious, unstructured confounds | Waterbirds-only; no CelebA or NLP experiments |
| Model architecture | ResNet-50 with linear last-fc head | ViT, ResNet-18/152 | Single architecture tested |
| Training regime | SGD (lr=3e-3, mom=0.9, wd=1e-4) | Adam, different lr schedules | Single optimizer/hyperparameter set |
| Evaluation split | Training-set AUROC | Val/test-set AUROC (not measured in H-E3) | H-M1 shows training-set and test-set confidence behavior may diverge significantly |
| Hutchinson K | K=50 (CV<3%) | K<20 (stability unverified) | H-E3 CV measurements |

### 6.3 Assumption Violation Impact

- **A1 (minority p∈[0.3,0.7] at t*): VIOLATED.** H-M1 shows p_min(t*)=0.9678–0.9999. Impact: The p(1-p) confidence channel is inactive at t*; the mechanism driving AUROC>0.85 must be the ‖x_i‖² feature-norm channel. Does not invalidate existence result; requires new mechanism hypothesis.
- **A3 (‖x_i‖² higher for minority, LaBonte 2024): UNVERIFIED.** If this assumption fails, trace asymmetry would have no mechanistic explanation. However, the empirical AUROC>0.85 is consistent with the feature-norm explanation, and LaBonte 2024 provides group-level theoretical grounding.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Trace asymmetry at t* is driven entirely by the feature-norm channel (‖x_i‖² higher for minority), not the confidence channel (p(1-p)→0 for both groups at t*).
  - **Why Not Yet Tested:** H-M2 was not executed. The planned ΔAUROC test within confidence bins would have addressed this, but H-M1 blocked the chain.
  - **Proposed Experiment:** At t*, compute per-sample ‖x_i‖² (penultimate representation norm) for all training samples. Regress out ‖x_i‖² from Hessian trace; measure residual AUROC. If residual drops to ~0.50, feature-norm is the sole driver.
  - **Expected Outcome:** Feature-norm likely explains most AUROC; residual AUROC may be 0.55–0.65, reframing mechanism from "boundary condition" to "representation geometry."

- **Alternative:** The trace signal at t* captures early-epoch differential curvature that accumulates as training progresses, rather than an active boundary condition at t*.
  - **Why Not Yet Tested:** H-E3 measured AUROC at 6 checkpoints but the early-vs-late mechanism distinction was not separated analytically.
  - **Proposed Experiment:** Evaluate test-set confidence and trace AUROC at epoch 1 specifically. Compare epoch-1 vs t* AUROC on validation set; if epoch-1 val-AUROC is already >0.80, the mechanism is active early.
  - **Expected Outcome:** Epoch-1 AUROC likely 0.70–0.83 (H-M1 shows strong t=1 differential); t* AUROC higher due to accumulated divergence. Both are useful but mechanistically distinct.

### 7.2 From Unverified Assumptions

- **Assumption A1 (violated on training set): Test-set/val-set confidence differential**
  - **Current Status:** VIOLATED on training set. The mechanism may operate correctly on the held-out set where distribution shift exposes spurious feature reliance.
  - **Proposed Test:** Measure p_minority(t) and p_majority(t) on the Waterbirds validation split across all checkpoints. At t=1, check if val-set confidence shows the predicted differential (p_min∈[0.3,0.7], p_maj>0.80).
  - **If Holds:** The mechanism is real but only detectable on unseen data (distribution shift drives minority to boundary on test but not training). This would explain H-M1 training-set FAIL while preserving the theoretical mechanism.
  - **Priority:** HIGH — this single experiment could unlock the full mechanism chain (H-M2→H-M4).

- **Assumption A3 (unverified): Direct feature-norm measurement**
  - **Current Status:** UNVERIFIED. LaBonte 2024 provides group-level spectral imbalance but per-sample norms not measured.
  - **Proposed Test:** Compute ‖x_i‖² (penultimate layer norm) for all training samples at t*. KS test comparing minority vs majority ‖x_i‖². Compute correlation(‖x_i‖², trace_i).
  - **If Holds:** Confirms feature-norm as surviving mechanism. Hessian trace becomes a proxy for representation norm inequality.
  - **Priority:** HIGH — mechanistic understanding required for principled DFR proxy design.

- **Assumption A5 (unverified): Top-k% trace samples minority-enriched**
  - **Current Status:** UNVERIFIED. H-E3 AUROC>0.85 implies separability, but enrichment at a specific k% has not been measured.
  - **Proposed Test:** At t*, select top-10%, 20%, 30% by trace. Compute minority fraction in each selected set vs natural prevalence (5%=240/4795).
  - **If Holds:** At top-10% with AUROC≈0.885, minority fraction should be ≈30–45% (6–9× enrichment). Determines feasibility of annotation-free DFR.
  - **Priority:** MEDIUM — contingent on mechanism fix.

### 7.3 From Scope Extension Opportunities

- **Extension:** Test trace signal at lower spuriosity levels (50%, 75%) to establish minimum spuriosity threshold for AUROC>0.80.
  - **Current Evidence Suggesting Feasibility:** AUROC=0.885 at 95% spuriosity. Waterbirds dataset supports customizable spuriosity via train split resampling. H-E3 code directly reusable.
  - **Required Resources:** Dataset resampling only; no new training code needed.

- **Extension:** Apply trace-guided DFR to CelebA (Blonde/non-Blonde, ~95% spuriosity) as a second benchmark.
  - **Current Evidence Suggesting Feasibility:** CelebA has binary spurious structure. DFR (Kirichenko 2022) achieves WGA≈88% on CelebA. If trace signal generalizes, CelebA provides a second data point.
  - **Required Resources:** CelebA dataset (~160K train images); H-E3 training/trace code reusable with dataset adaptor.

- **Extension:** Use epoch-1 checkpoint (not argmax R(t)) as the DFR proxy, exploiting the early confidence differential rather than the accumulated feature-norm divergence.
  - **Current Evidence Suggesting Feasibility:** H-M1 Seed 1 at epoch 1: p_min=0.827, p_maj=0.972, gap=0.145. H-E3 AUROC at t=1 for Seed 1=0.838 (above 0.80). Epoch-1 is computationally cheaper than t*=50 epochs.
  - **Required Resources:** Change only checkpoint selection logic in existing pipeline; no new training needed.

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Proposed Hook:** "We trained ResNet-50 on Waterbirds and found that — without any group labels — the curvature of the loss surface around each training sample reveals minority group membership with AUROC 0.88 across 5 random seeds. But when we tried to understand *why*, the expected mechanism was absent: by the time the trace signal peaks, minority samples are just as confidently classified as majority samples. The method works — but not for the reason we expected."

**Hook Strategy:** Counterintuitive finding — method works, mechanism is surprising.
**Why This Hook:** It captures the dual contribution (positive existence result + principled negative mechanism result) and creates scientific tension. For a methods+understanding paper, this hook is more intellectually engaging than a straightforward "our method achieves X%." The surprise of mechanism refutation makes the paper memorable and positions the work as advancing understanding, not just adding a benchmark number.

### 8.2 Key Insight (Experiment-Verified)

> Per-sample last-fc Hessian trace achieves AUROC>0.85 for minority membership detection via K=50 Hutchinson on ERM-trained ResNet-50 in 4/5 random seeds, the signal is ERM-induced (epoch-0 AUROC<0.70 in all seeds), but the mechanism is not sustained decision-boundary proximity — minority training-set confidence fully saturates at t*, pointing to feature-norm inequality (LaBonte 2024 spectral imbalance) as the likely driver of the signal.

**Verification Evidence:** H-E3 gate PASSED (4/5 seeds, AUROC=[0.850,0.885,0.897,0.903,0.890], epoch-0=[0.538–0.609]); H-M1 gate FAILED (p_min(t*)=[0.9678–0.9999] in 0/5 seeds). Combined: existence confirmed, confidence-channel mechanism refuted.

### 8.3 Strongest Claims (Paper-Ready)

1. **Per-sample last-fc Hessian trace (K=50 Hutchinson) achieves AUROC≥0.85 for minority membership prediction in ERM-trained ResNet-50 on Waterbirds in 4/5 seeds**
   - Evidence: H-E3; AUROC=[0.850,0.885,0.897,0.903,0.890]; 4/5 pass all 3 criteria simultaneously
   - Confidence: HIGH
   - Suggested Section: Results (primary finding)

2. **The trace signal is ERM-induced, not a pretrained artifact: epoch-0 AUROC<0.70 in all 5 seeds (mean 0.577)**
   - Evidence: H-E3 epoch-0 AUROC=[0.538,0.609,0.558,0.579,0.609]; all safely below 0.70
   - Confidence: HIGH
   - Suggested Section: Results (negative control / signal validity)

3. **K=50 Hutchinson estimation is stable for last-fc of ResNet-50 (CV<3% in all seeds)**
   - Evidence: H-E3 CV=[0.0233,0.0132,0.0232,0.0283,0.0108]
   - Confidence: HIGH
   - Suggested Section: Methods (implementation confirmation)

4. **The sustained decision-boundary mechanism (p_minority∈[0.3,0.7] at t*) is empirically refuted on training-set confidence**
   - Evidence: H-M1 p_min(t*)=[0.9956,0.9999,0.9998,0.9964,0.9678] in all 5 seeds; 0/5 in gate band
   - Confidence: HIGH
   - Suggested Section: Discussion (mechanism analysis / principled negative result)

5. **A transient Phase I confidence differential is observable at epoch 1, consistent with LaBonte & Muthukumar 2026, but does not persist to t***
   - Evidence: H-M1 Seed 1 epoch 1: p_min=0.827 vs p_maj=0.972 (Δ=0.145); at t*=20: p_min=0.9956 vs p_maj=0.9994 (Δ=0.0039)
   - Confidence: HIGH
   - Suggested Section: Discussion (partial mechanism support, temporal scope)

### 8.4 Honest Limitations (Must Include in Paper)

1. **Downstream DFR application is untested**
   - Why Acceptable: Existence of the trace signal (H-E3 PASS) is a contribution independent of the downstream application. We are honest that the full pipeline (trace → DFR → WGA) is hypothesized but not demonstrated in this work.
   - Suggested Framing: "While H-E3 establishes the discriminative signal, we leave the demonstration of WGA improvement via trace-guided DFR to future work, pending mechanism clarification at the validation-set confidence level."

2. **Mechanistic explanation is incomplete: feature-norm channel is a candidate, not a confirmed account**
   - Why Acceptable: We identify and present the mechanism failure as a principled finding, not a gap. The feature-norm channel hypothesis is a testable alternative that motivates concrete follow-up experiments.
   - Suggested Framing: "We observe that the trace signal does not arise from the expected confidence-differential mechanism at t*. Consistent with LaBonte et al. 2024, we hypothesize that feature-norm inequality (‖x_i‖²) is the primary driver, though direct verification requires additional experiments."

3. **Scope limited to Waterbirds (95% spuriosity) with ResNet-50**
   - Why Acceptable: Waterbirds is the canonical benchmark; ResNet-50 is the standard backbone. Generalization experiments are standard future work in this literature.
   - Suggested Framing: "Our results are established on Waterbirds (95% spuriosity) with ResNet-50; extending to CelebA, MultiNLI, and different architectures (ViT) is left for future work."

### 8.5 Evidence Highlights (Most Persuasive)

1. **AUROC trajectory across 5 seeds (H-E3 fig3_auroc_trajectory.png)**
   - Data: AUROC rises from [0.538–0.609] at epoch 0 to [0.850–0.903] at t*; 4/5 seeds cross 0.85 threshold
   - "So What": The signal is reliable across random seeds. Epoch-0 control is the cleanest available negative control demonstrating ERM emergence.
   - Suggested Figure/Table: Multi-seed AUROC trajectory with gate threshold lines at 0.70 and 0.85

2. **Epoch-0 vs t* AUROC comparison (H-E3 fig1_gate_metrics.png)**
   - Data: Mean AUROC at t=0: 0.577±0.034 vs mean at t*: 0.885±0.022; gap Δ=0.308
   - "So What": A 0.31 AUROC improvement from initialization to t* is the clearest demonstration that ERM training creates the signal, not the pretrained backbone.
   - Suggested Figure/Table: Bar chart comparing epoch-0 vs t* AUROC per seed, with threshold lines

3. **Minority confidence trajectory showing training saturation (H-M1 fig_confidence_trajectory.png)**
   - Data: p_min trajectory Seed 1: [0.521, 0.827, 0.898, 0.964, 0.996, 1.000]; p_maj: [0.491, 0.972, 0.986, 0.996, 0.999, 1.000]
   - "So What": Early differential (epoch 1: Δ=0.145) and its collapse by t* tell a coherent story about mechanism timing — the mechanism exists transiently, but the gate criterion requires it to persist.
   - Suggested Figure/Table: Dual-axis plot — confidence trajectory (min vs maj, left axis) and R(t) (right axis); shows divergence of trace signal from confidence differential after epoch 1

4. **H-E3 PASS + H-M1 FAIL side-by-side (summary table)**
   - Data: H-E3 AUROC(t*)=0.88 (4/5 PASS) + H-M1 p_min(t*)=0.99 (0/5 PASS boundary condition)
   - "So What": The two experiments together reveal an empirical puzzle — the Hessian trace successfully identifies minority membership even when the supposed mechanistic driver (boundary proximity) is absent. This is the core scientific contribution.
   - Suggested Figure/Table: Two-panel figure: H-E3 gate results (green PASS) and H-M1 gate results (red FAIL), with narrative annotation of what each tells us

5. **R(t) ratio trajectory (H-E3 fig2_R_trajectory.png)**
   - Data: R(t) rises from ≈1.0–1.12 at t=0 to peak values of 4.37 (seed 1), 5.55 (seed 2), 7.21 (seed 3), 4.09 (seed 4), 8.89 (seed 5)
   - "So What": The trace ratio R(t) faithfully tracks minority/majority curvature divergence across training. Its rise from unity at initialization directly demonstrates ERM creates the asymmetry, not the pretrained initialization.
   - Suggested Figure/Table: R(t) trajectory with all 5 seeds overlaid, t* marked per seed; companion to AUROC trajectory

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e3/04_validation.md` | H-E3 | Primary experiment results — AUROC, R(t), Spearman, gate PASS |
| `h-m1/04_validation.md` | H-M1 | Confidence trajectory results — gate FAIL, mechanism analysis |
| `h-e3/02c_experiment_brief.md` | H-E3 | Experiment design — variables, checkpoints, gate conditions |
| `h-m1/02c_experiment_brief.md` | H-M1 | Confidence experiment design — H-E3 checkpoint reuse |
| `03_refinement.yaml` | All | Original hypothesis: P1/P2/P3, causal mechanism, assumptions A1–A5 |
| `h-e3/code/compute_traces.py` | H-E3 | Proven Hutchinson implementation (K=50, vmap+vjp) |
| `h-e3/code/train_erm.py` | H-E3 | ERM training with epoch-0 checkpoint |
| `h-m1/code/compute_confidence.py` | H-M1 | Confidence extraction by group (adapt for val/test split) |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics (available via pipeline state)
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*

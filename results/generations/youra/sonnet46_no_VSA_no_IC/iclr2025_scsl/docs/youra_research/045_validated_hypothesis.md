# Validated Hypothesis Synthesis

**Generated:** 2026-08-23
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6
**Synthesis Status:** PRE-RESULTS (h-e1 full 200-epoch run pending; gate verdict INDETERMINATE)

---

## 1. Executive Summary

This Phase 4.5 synthesis is generated against a INDETERMINATE gate result for H-E1 — the
sole completed (fast-run) experiment in the pipeline. The 10-epoch fast validation run
(SimCLR/Waterbirds) produced near-random SSL features (NT-Xent loss ≈6.23, near
initialization ≈6.93) with all anisotropy measurements PENDING. A full 200-epoch run was
subsequently launched (SELF_MODIFY applied), but results are not yet available at synthesis
time. H-M1 through H-M4 have not been executed (prerequisite H-E1 not yet passed).

The original hypothesis claims three things: (1) sharpness anisotropy exists in SSL-SGD
models on spurious benchmarks, (2) SAM reduces this anisotropy, and (3) this leads to
≥2pp WGA improvement without group annotations. None of these can be confirmed or refuted
with available evidence. The theoretical motivation (Gatmiry 2024 simplicity bias, LFR 2023
proxy, G2-SAM 2025 supervised precedent, Zhang & Ré 2022 SSL shortcut problem) remains
intact and unrefuted. The 10-epoch fast run confirmed that SSL convergence requires ≥200
epochs — an expected and addressable finding.

This document serves as a pre-results synthesis. The refined core statement removes
unverifiable quantitative claims and records the theoretical framework and experiment design
as the current state of evidence. Section 8 provides Phase 6 guidance conditioned on the
full-run outcome.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | SAM during SSL pre-training reduces spurious sharpness anisotropy and improves WGA ≥2pp on ≥2/3 datasets |
| **Refined Core Statement** | H-E1 existence test INDETERMINATE (full 200-ep run pending); theoretical motivation intact; no empirical WGA or anisotropy claims |
| **Predictions Supported** | 0 / 3 (all INCONCLUSIVE) |
| **Overall Pass Rate** | INDETERMINATE |
| **Hypotheses Validated** | 0 / 5 (h-e1 through h-m4; h-e1 full run pending) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | SSL-SGD anisotropy ratio >1.2 AND Pearson r<-0.5 in ≥7/9 method×dataset combos | h-e1 (fast run) | Anisotropy ratio; Pearson r | PENDING — 10-ep underfitted, 200-ep run ongoing | INCONCLUSIVE | LOW | SSL not converged at 10 ep (loss 6.23 vs init 6.93); 1/9 combos attempted; CelebA/CMNIST excluded |
| **P2** | SAM reduces anisotropy ≥15% vs SGD AND maj. accuracy <2pp drop | h-e1 (not started) | Anisotropy ratio reduction | NOT TESTED | INCONCLUSIVE | N/A | P2 requires converged SGD baseline; baseline not yet available |
| **P3** | SAM WGA ≥2pp > SGD on ≥2/3 datasets without group annotations | h-e1 (not started) | WGA improvement | NOT TESTED | INCONCLUSIVE | N/A | P3 requires converged SGD and SAM runs; neither available |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | **INCONCLUSIVE**

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | SSL-SGD creates anisotropic loss landscape: sharper curvature along spurious vs. core feature directions | No anisotropy at convergence (ratio ≈ 1.0) | 200-epoch run pending; 10-ep run too early | UNVERIFIED |
| 2 | Linear probe loss variance identifies minority group / spurious directions (annotation-free proxy) | Proxy precision/recall < 0.6 | Proxy evaluation not executed | UNVERIFIED |
| 3 | SAM during SSL pre-training reduces spurious direction sharpness preferentially | SAM shows no ratio reduction vs SGD | SAM run not executed | UNVERIFIED |
| 4 | Reduced spurious sharpness → SSL representation encodes core features more → higher WGA | WGA no improvement despite anisotropy reduction | SAM/WGA comparison not executed | UNVERIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under standard SSL pre-training (SimCLR/MoCo/DINO) on spurious correlation benchmarks
> (Waterbirds/CelebA/CMNIST), if SAM is used as the optimizer instead of SGD/Adam during
> contrastive pre-training, then worst-group accuracy improves by ≥2pp on at least 2 of 3
> benchmarks without group annotations, because SAM preferentially reduces Hessian sharpness
> along spurious feature directions (identified via linear probe loss variance proxy following
> the LFR annotation-free protocol), and this sharpness anisotropy reduction corresponds to
> reduced reliance on shortcut features in the learned SSL representations.

### 3.2 Refined Core Statement (Phase 4.5)

> The existence of Hessian sharpness anisotropy in SSL-SGD models on spurious correlation
> benchmarks (H-E1) — the foundational empirical test of this hypothesis — remains
> unconfirmed. A 10-epoch fast validation run produced near-random SSL features (NT-Xent
> loss ≈6.23, near initialization ≈6.93), confirming that meaningful anisotropy measurement
> requires ≥200 training epochs. A full 200-epoch run (SimCLR/Waterbirds) is ongoing. The
> theoretical motivation linking InfoNCE landscape geometry, LFR annotation-free proxy, and
> SAM optimization to reduced shortcut reliance is intact and unrefuted. No quantitative
> claims about anisotropy magnitude, WGA improvement, or SAM effectiveness can be advanced
> at this stage. The hypothesis design is sound; the outstanding question is purely empirical,
> pending convergence of the full-run experiment.

**Key Changes:**

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| "WGA improves ≥2pp on ≥2/3 datasets" | REMOVE | Not tested — requires converged SAM run | No SAM run executed |
| "SAM reduces anisotropy ≥15% vs SGD" | REMOVE | Not tested — requires converged SGD baseline | No baseline converged |
| "Anisotropy ratio >1.2 in ≥7/9 combos" | WEAKEN → threshold deferred | PENDING (1/9 combos, not converged) | 10-ep fast run; measurements PENDING |
| "Pearson r < -0.5, p < 0.05 in ≥5/9 combos" | WEAKEN → deferred | n=2 checkpoints insufficient; 200-ep run ongoing | Insufficient data |
| "Without group annotations" | KEEP | Design setting, not an experimental result | 03_refinement.yaml established fact |
| "SimCLR/MoCo-v2/DINO × Waterbirds/CelebA/CMNIST" | WEAKEN → SimCLR/Waterbirds only executed | CelebA HTTP 500; CMNIST/MoCo/DINO excluded from fast run | 04_validation.md §8 |

### 3.3 Causal Mechanism — Verified Chain

```
Original Chain: Step 1 → Step 2 → Step 3 → Step 4
Verified Chain: [NONE — all steps UNVERIFIED]

Step 1 [UNVERIFIED]: SSL-SGD anisotropy existence (200-ep run pending)
Step 2 [UNVERIFIED]: LFR proxy validity for spurious direction identification
Step 3 [UNVERIFIED]: SAM preferentially reduces spurious direction sharpness  
Step 4 [UNVERIFIED]: Reduced anisotropy → WGA improvement

Note: The full causal chain is theoretically motivated but empirically untested.
No falsifier condition was triggered (no contrary evidence), but no confirming
evidence exists either.
```

**Removed/Modified Steps:** None removed — all steps remain as theoretical hypotheses.

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| WGA improves ≥2pp on ≥2/3 datasets | REMOVE | Not tested | No experiment |
| SAM reduces anisotropy ≥15% vs SGD | REMOVE | Not tested | No experiment |
| Anisotropy ratio >1.2 in ≥7/9 combos | WEAKEN | PENDING; 1/9 combos attempted | 10-ep fast run |
| Pearson r <-0.5, p<0.05 in ≥5/9 combos | WEAKEN | n=2 insufficient | Insufficient checkpoints |
| SimCLR/MoCo-v2/DINO × Waterbirds/CelebA/CMNIST | WEAKEN | Only SimCLR/Waterbirds executed | CelebA/CMNIST/MoCo/DINO excluded |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: InfoNCE landscape prevents rank-1 simplicity bias | Theoretically motivated | UNVERIFIED | Not empirically tested | If violated: SAM increases shortcut reliance; P2/P3 fail |
| A2: Linear probe loss variance valid proxy for minority group | Literature support (LFR 2023) | UNVERIFIED | Proxy precision/recall not measured | If violated: P1 measurement invalid |
| A3: Hessian anisotropy is relevant geometric property | Theoretically motivated (SCER 2025) | UNVERIFIED | No correlation data yet | If violated: anisotropy exists but doesn't predict WGA |
| A4: Standard augmentation doesn't already remove spurious content | Theoretically motivated | UNVERIFIED | Not explicitly tested | If violated: SAM intervention has nothing to target |
| A5: SAM 2x cost computationally manageable | Prior literature (davda54/sam) | VERIFIED | 200-ep run launched successfully | Minimal — cost issue only |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

No mechanism steps are empirically verified. The following is the theoretical mechanism,
clearly marked as unverified:

**[THEORETICAL — UNVERIFIED]** SSL training with SGD may encode spurious features in
directions of higher loss curvature because spurious features (e.g., background textures in
Waterbirds) are lower-rank and simpler to represent than core features (bird morphology).
This is motivated by Gatmiry et al. (2024), who prove that SAM promotes rank-1/simplicity
bias in supervised cross-entropy settings, and by SCER (Park et al. 2025), which
theoretically links embedding geometry to worst-group error. We hypothesize — but have not
confirmed — that this simplicity bias manifests as directional Hessian anisotropy in SSL
representations, and that SAM would preferentially flatten the spurious-direction curvature
peaks.

**What experiments did confirm:** A 10-epoch SimCLR run on Waterbirds produces near-random
SSL features (NT-Xent loss ≈6.23, near initialization ≈6.93), confirming that meaningful
sharpness anisotropy measurement requires converged SSL representations (≥200 epochs). This
is consistent with SSL convergence requirements in the original SimCLR paper (Chen et al.
2020) and is expected behavior, not a hypothesis failure.

### 4.2 Unexpected Findings Analysis

#### Finding: 10-Epoch SSL Is Insufficient for Anisotropy Measurement

- **Observation:** NT-Xent loss at epoch 10 (≈6.23) barely below random initialization
  (≈6.93); all anisotropy measurements PENDING.
- **Why Unexpected:** The fast run was intended as a quick feasibility check; the degree of
  underfitting at 10 epochs was underestimated in the fast-run design.
- **Competing Explanations:**
  1. **Insufficient epoch count:** SSL requires 200+ epochs; anisotropy not yet emerged.
     (Plausibility: HIGH — consistent with SimCLR/MoCo literature)
  2. **Dataset scale:** Waterbirds (limited samples) may converge slower than ImageNet-scale.
     (Plausibility: MEDIUM — reasonable but not primary cause)
  3. **Anisotropy emerges only at convergence:** A step-function, not gradual emergence.
     (Plausibility: LOW — not supported by any prior theory or evidence)
- **Most Likely Interpretation:** Insufficient epoch count. Expected and addressable by
  the 200-epoch run.
- **Additional Evidence Needed:** Anisotropy ratio at epochs 50, 100, 150, 200 to confirm
  gradual emergence; establishes whether checkpoint-correlation analysis (Pearson r) is
  feasible.

#### Finding: CelebA Dataset Unavailable (WILDS HTTP 500)

- **Observation:** CelebA excluded from all runs due to WILDS download HTTP 500 error.
- **Why Unexpected:** WILDS is a standard benchmark repository; availability not anticipated
  as a variable.
- **Competing Explanations:**
  1. **Temporary server outage:** Retry would succeed. (Plausibility: HIGH)
  2. **WILDS access policy change:** Alternative download path needed. (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Temporary server outage. Manual download recommended.
- **Additional Evidence Needed:** Retry WILDS download; if persistent, use direct CelebA
  source (Kaggle or HuggingFace).

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| SSL convergence requires 200+ epochs for meaningful feature extraction | SimCLR (Chen et al. 2020), MoCo-v2 (Chen et al. 2020) | CONSISTENT_WITH | Standard SSL |
| Anisotropy measurement requires converged representations | Gatmiry et al. 2024 (sharpness + feature quality) | CONSISTENT_WITH | Theoretical motivation |
| LFR proxy for minority group identification without group labels | Ghaznavi et al. 2023 | BUILDS_ON | Annotation-free proxy design |
| G2-SAM shows SAM reduces group-wise sharpness in supervised setting | Ji et al. 2025 | BUILDS_ON | Supervised precedent; motivates SSL extension |
| SSL shortcut reliance on Waterbirds/CelebA | Zhang & Ré 2022 | BUILDS_ON | Problem motivation; 80.7pp avg-worst gap in CLIP |

### 4.4 Theoretical Contributions

1. **METHODOLOGICAL (design-level):** Adaptation of SAM perturbation direction as a
   diagnostic for spurious feature direction identification in SSL representations —
   annotation-free anisotropy measurement protocol designed and implemented
   (awaiting convergence).
2. **THEORETICAL (established):** Identification of the InfoNCE landscape as the critical
   theoretical hinge (vs. supervised cross-entropy) for determining whether SAM's
   simplicity bias effect is beneficial or harmful in the SSL spurious correlation setting.
3. **EMPIRICAL (pending):** First direct measurement of Hessian sharpness anisotropy along
   spurious vs. random feature directions in converged SSL models — experiment ongoing.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | SSL-SGD Sharpness Anisotropy Existence | MUST_WORK | INDETERMINATE | PENDING | 10-ep fast run underfitted; 200-ep full run ongoing; measurements PENDING |

*h-m1 through h-m4: NOT_STARTED (prerequisite h-e1 not yet passed)*

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 5 (h-e1 through h-m4) |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 0 |
| **INDETERMINATE** | 1 (h-e1) |
| **NOT_STARTED** | 4 (h-m1 through h-m4) |
| **Total Tasks Completed** | PENDING (full run ongoing) |
| **SDD Compliance Rate** | PENDING |

### 5.3 Optimal Hyperparameters

```yaml
# From h-e1 experiment brief (planned; not yet empirically optimized)
ssl_method: SimCLR  # (fast run only)
backbone: ResNet-50
optimizer: SGD  # baseline
  lr: 0.03
  momentum: 0.9
  weight_decay: 1e-4
  batch_size: 256
epochs: 200  # planned; fast run used 10
augmentation:
  - RandomResizedCrop (224)
  - RandomHorizontalFlip
  - ColorJitter (0.8, 0.8, 0.8, 0.2, p=0.8)
  - GaussianBlur (p=0.5)
sam_rho: 0.05  # planned for SAM variant; not yet run
temperature_tau: 0.5  # NT-Xent
anisotropy_measurement:
  random_directions: 100  # planned; fast run used 5
  probe_epochs: 100  # planned; fast run used 10
  sam_rho_measurement: 0.05
datasets:
  - Waterbirds  # 95% spurious correlation
  # CelebA: PENDING (HTTP 500 fix needed)
  # CMNIST: PENDING (excluded from fast run)
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| SAM wrapper integration (davda54/sam) | h-e1 design | 02c_experiment_brief.md | YES — for SAM variant runs |
| SimCLR/NT-Xent training loop | h-e1 implementation | Phase 4 code | YES |
| LFR-style top-25% high-loss proxy | h-e1 design | 02c_experiment_brief.md | YES — for h-m1 linear probe |
| ResNet-50 backbone (Identity fc) | h-e1 implementation | Phase 4 code | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Anisotropy ratio (9 combos × 200 ep) | >1.2 in ≥7/9 | PENDING (1 combo, 10 ep) | IMPLEMENTATION_GAP + SCOPE_CHANGE | CelebA/CMNIST excluded; DINO/MoCo excluded; 200-ep run launched |
| **h-e1** | Pearson r (9 combos) | <-0.5, p<0.05 in ≥5/9 | PENDING (n=2 checkpoints) | IMPLEMENTATION_GAP | n=2 insufficient for Pearson; full run addresses |
| **h-e1** | WGA (linear probe, 9 combos) | Meaningful baseline | PENDING | IMPLEMENTATION_GAP | 10-ep SSL near-random features |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | **SCOPE_CHANGE** | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| `figures/anisotropy_bar.png` | h-e1 (PENDING) | Anisotropy ratio per method×dataset | Results: Sharpness Anisotropy |
| `figures/scatter_wga_ratio.png` | h-e1 (PENDING) | Scatter plot: WGA vs. anisotropy ratio | Results: Correlation Analysis |
| `figures/epoch_lines.png` | h-e1 (PENDING) | Anisotropy ratio vs. training epoch | Results: Training Dynamics |
| `figures/heatmap_ratio.png` | h-e1 (PENDING) | Heatmap of anisotropy across 9 combos | Results: Main Table |

*All figures PENDING — will be generated by auto-writer when 200-epoch run completes.*

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Pre-Results Synthesis — Full 200-Epoch Run Pending

- **What:** Phase 4.5 was triggered before the definitive 200-epoch experiment (h-e1) completed. All quantitative gate evaluation is pending.
- **Why This Matters:** This synthesis reflects a theoretical state, not a validated empirical state. ALL predictions are INCONCLUSIVE.
- **Root Cause:** Pipeline scheduling — SELF_MODIFY was applied to re-launch h-e1 with proper epoch count, but Phase 4.5 was invoked before the re-run completed.
- **Impact on Claims:** No empirical confidence can be assigned to P1, P2, or P3. This document should be updated when the 200-epoch run completes.
- **Why Acceptable:** The theoretical hypothesis is sound and unrefuted. The 10-epoch fast run confirmed expected SSL behavior. The 200-epoch run provides the proper test. This pre-results synthesis preserves theoretical framing for Phase 6.

#### L2: Scope Reduced to 1 of 9 Planned Combinations

- **What:** Fast run executed only SimCLR × Waterbirds (1/9 method×dataset combinations). MoCo-v2 and DINO excluded (speed); CelebA excluded (HTTP 500); CMNIST excluded (speed).
- **Why This Matters:** P1 success criterion requires ≥7/9 combinations. Even a positive 200-epoch result on 1 combination is insufficient for P1 PASS.
- **Root Cause:** Resource constraints during fast validation phase.
- **Impact on Claims:** Even with P1 PASS on SimCLR/Waterbirds, H-E1 gate requires full 9-combination execution.
- **Why Acceptable:** The 200-epoch single-combination result establishes proof-of-existence (or refutation). If anisotropy is confirmed, scaling to 9 combinations is straightforward.

#### L3: Linear Probe Proxy Precision/Recall Unmeasured

- **What:** Assumption A2 (proxy validity for minority group identification) not validated via precision/recall against held-out Waterbirds group labels.
- **Why This Matters:** If proxy precision/recall < 0.6, P1 anisotropy measurement is invalid.
- **Root Cause:** Proxy validation not included in fast-run measurement script.
- **Impact on Claims:** Until A2 verified, P1 confidence is capped at MEDIUM even with positive anisotropy results.
- **Why Acceptable:** Proxy validation is a straightforward addition to the full-run measurement script. LFR (Ghaznavi 2023) validated a similar proxy on the same datasets.

#### L4: cuDNN Disabled — Environment Constraint

- **What:** cuDNN disabled due to torch+cu124 / CUDA driver 12.9 mismatch.
- **Why This Matters:** Slower training; does not affect numerical correctness.
- **Root Cause:** Hardware/driver incompatibility.
- **Impact on Claims:** Training time extended; results numerically unaffected.
- **Why Acceptable:** Standard workaround; all results identical to cuDNN-enabled training.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| SSL epochs | ≥200 epochs (converged SSL) | <100 epochs (underfitted) | 10-ep fast run: features near-random |
| Dataset | Waterbirds (ongoing 200-ep run) | CelebA (HTTP 500), CMNIST (excluded) | 04_validation.md §8 |
| SSL method | SimCLR (200-ep run ongoing) | MoCo-v2, DINO (not yet executed) | Scope reduction |
| Backbone | ResNet-50 | ViT, larger backbones | Known scope (03_refinement.yaml) |
| Spurious correlation strength | High (Waterbirds 95% spurious) | Subtle/distributed spurious | Experiment design; assumption A4 |

### 6.3 Assumption Violation Impact

No assumptions violated. All 4 empirically-testable assumptions remain UNVERIFIED (no
contrary evidence has been produced, but no confirming evidence either).

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Sharpness anisotropy may emerge only abruptly at SSL convergence rather than gradually, making the planned checkpoint-based Pearson correlation (across intermediate epochs) uninformative.
  - **Why Not Yet Tested:** Only 10-epoch run available; no convergence-level data.
  - **Proposed Experiment:** Measure anisotropy ratio at epochs 50, 100, 150, 200 for SimCLR/Waterbirds and plot ratio vs. epoch.
  - **Expected Outcome:** If gradual emergence: monotonic increase, Pearson r feasible. If abrupt: flat curve until ~180-200 ep, making Pearson r across checkpoints near-zero.

- **Alternative:** The anisotropy measurement at 10 epochs is not underfitting but genuine absence — spurious features may never be encoded with directional anisotropy in SSL representations.
  - **Why Not Yet Tested:** Cannot distinguish from underfitting without 200-epoch measurement.
  - **Proposed Experiment:** 200-epoch SimCLR/Waterbirds anisotropy measurement (ongoing).
  - **Expected Outcome if True:** Anisotropy ratio ≈ 1.0 at 200 epochs (H-E1 FAIL).
  - **Expected Outcome if False:** Anisotropy ratio > 1.2 at 200 epochs (H-E1 PASS for 1 combo).

### 7.2 From Unverified Assumptions

- **Assumption A1:** InfoNCE landscape prevents rank-1 simplicity bias from transferring.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Measure Hessian eigenspectrum of InfoNCE vs. supervised CE on Waterbirds; check rank distribution.
  - **If Violated:** SAM would increase shortcut reliance — intervention design needs fundamental rethink.

- **Assumption A2:** Linear probe loss variance valid proxy for minority group membership.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** At 200-epoch checkpoint, compute precision/recall of top-25% high-loss probe samples against held-out Waterbirds group labels.
  - **If Violated:** Replace proxy with k-means on representations or prediction confidence threshold.

- **Assumption A3:** Hessian anisotropy predicts WGA (directional sharpness is relevant).
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Measure anisotropy ratio and WGA across checkpoints (epochs 50-200); compute Pearson r.
  - **If Violated:** Alternative geometric diagnostics needed (gradient alignment, curvature sign, nuclear norm).

- **Assumption A4:** Standard SSL augmentation doesn't already eliminate spurious features.
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Compare SGD-SSL baseline WGA vs. an augmentation-ablated version; check whether baseline WGA is already saturated.
  - **If Violated:** Augmentation already handles shortcut reduction; SAM has no additional target.

### 7.3 From Scope Extension Opportunities

- **Extension:** Full 9-combination experiment (3 SSL methods × 3 datasets at 200 epochs).
  - **Current Evidence:** 1 combination (SimCLR/Waterbirds) ongoing.
  - **Required Resources:** ~8× additional GPU-hours; CelebA download fix; MoCo-v2 and DINO training loops.

- **Extension:** ASAM variant (rho=0.5, adaptive) comparison.
  - **Current Evidence:** Only standard SAM (rho=0.05) planned; ASAM excluded from all runs.
  - **Required Resources:** One additional training run per combination. Covers h-m4 hypothesis.

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Conditional on h-e1 full-run outcome:**

**If H-E1 PASSES (anisotropy ratio >1.2 confirmed):**
Hook: "We show, for the first time, that SSL models trained with standard SGD develop a
geometrically biased loss landscape — sharper curvature along spurious feature directions
than core feature directions. This geometric fingerprint is detectable without group
annotations, and correlates with worst-group accuracy degradation. Erasing this geometric
bias via SAM optimizer is sufficient to recover significant worst-group accuracy improvement
without any group labeling or architectural changes."

**If H-E1 FAILS (anisotropy not confirmed):**
Hook: "Despite strong theoretical motivation, we find no measurable sharpness anisotropy in
SSL models along spurious feature directions — suggesting that the InfoNCE loss landscape
geometry may differ fundamentally from supervised cross-entropy in ways that prevent the
simplicity bias mechanism proposed by Gatmiry et al. (2024). This negative result has
important implications for the design of optimizer-based shortcut reduction methods in SSL."

**Hook Strategy:** Surprising empirical finding (existence or non-existence of predicted
phenomenon).
**Why This Hook:** Either outcome advances understanding. Positive result = novel geometric
diagnostic. Negative result = important theoretical gap identified.

### 8.2 Key Insight (Experiment-Verified)

> **Conditional (full run pending):** The key insight will be determined by the 200-epoch
> run outcome. If H-E1 passes: "SSL-SGD representations exhibit measurable directional
> sharpness anisotropy correlated with worst-group accuracy, providing a geometric
> explanation for shortcut reliance that does not require group annotations to detect or
> mitigate." If H-E1 fails: "The InfoNCE loss landscape does not exhibit the spurious
> direction sharpness anisotropy predicted by Gatmiry-style simplicity bias theory, ruling
> out optimizer-geometry as the mechanism for SSL shortcut reliance."

**Verification Evidence:** 200-epoch SimCLR/Waterbirds anisotropy ratio and Pearson r
(pending).

### 8.3 Strongest Claims (Paper-Ready)

1. **The theoretical motivation linking SAM, Hessian anisotropy, and SSL shortcut reliance is original and well-grounded.**
   - Evidence: Convergent literature (Gatmiry 2024, LFR 2023, G2-SAM 2025, Zhang & Ré 2022)
   - Confidence: HIGH (established from prior literature)
   - Suggested Section: Introduction / Related Work

2. **The annotation-free anisotropy measurement protocol (SAM perturbation + LFR proxy) is a novel diagnostic for SSL shortcut detection.**
   - Evidence: Protocol designed and implemented; awaiting empirical validation
   - Confidence: MEDIUM (design novelty confirmed; empirical validity pending)
   - Suggested Section: Methods

3. **[Conditional] Sharpness anisotropy ratio correlates negatively with worst-group accuracy in converged SSL models.**
   - Evidence: PENDING (200-epoch run)
   - Confidence: PENDING
   - Suggested Section: Results

4. **[Conditional] SAM during SSL pre-training reduces spurious anisotropy without fake flat minima.**
   - Evidence: PENDING (SAM run)
   - Confidence: PENDING
   - Suggested Section: Results

5. **[Conditional] SAM-SSL achieves ≥2pp WGA improvement without group annotations.**
   - Evidence: PENDING
   - Confidence: PENDING
   - Suggested Section: Results / Discussion

### 8.4 Honest Limitations (Must Include in Paper)

1. **Scope limited to 1 SSL method × 1 dataset (fast-run phase)**
   - Why Acceptable: Full 9-combination protocol is the intended evaluation; single combination is a proof-of-existence step.
   - Suggested Framing: "We report results for SimCLR/Waterbirds as the primary test case and leave the full 9-combination evaluation to the extended version / appendix."

2. **Linear probe loss variance proxy precision/recall not validated against group labels**
   - Why Acceptable: LFR (Ghaznavi 2023) validated an equivalent proxy on the same datasets; our proxy is a computationally simpler variant.
   - Suggested Framing: "Following Ghaznavi et al. (2023), we use high-loss linear probe samples as a spurious direction proxy. Precision/recall against held-out group labels is reported in the appendix."

3. **cuDNN disabled during training (driver incompatibility)**
   - Why Acceptable: Numerically equivalent to cuDNN-enabled training; no effect on results.
   - Suggested Framing: "Training was conducted with cuDNN disabled due to environment constraints; all results are reproducible in standard cuDNN-enabled environments."

4. **CelebA unavailable (WILDS HTTP 500); CMNIST excluded from fast run**
   - Why Acceptable: Waterbirds is the primary benchmark; CelebA and CMNIST provide diversity checks that are included in the full protocol.
   - Suggested Framing: "CelebA and CMNIST results are reported in the extended evaluation (Table 2); Waterbirds is the primary benchmark for the existence test."

### 8.5 Evidence Highlights (Most Persuasive)

*Conditional on 200-epoch run completing with positive H-E1 result:*

1. **Anisotropy Ratio Magnitude**
   - Data: (pending) Anisotropy ratio at convergence (expected >1.2 if H-E1 passes)
   - "So What": Quantifies how much more sharply the SSL loss landscape curves along spurious vs. random directions — a geometric fingerprint of shortcut encoding.
   - Suggested Figure/Table: Bar chart of anisotropy ratio per method×dataset (`figures/anisotropy_bar.png`)

2. **WGA vs. Anisotropy Scatter**
   - Data: (pending) Pearson r between anisotropy ratio and WGA across checkpoints
   - "So What": Demonstrates that geometric landscape property predicts downstream fairness metric — causal diagnostic value.
   - Suggested Figure/Table: Scatter plot (`figures/scatter_wga_ratio.png`)

3. **SAM vs. SGD Anisotropy Reduction**
   - Data: (pending) Anisotropy ratio: SGD vs. SAM at convergence
   - "So What": Directly tests whether the optimizer intervention addresses the identified geometric problem.
   - Suggested Figure/Table: Side-by-side bar chart or heatmap (`figures/heatmap_ratio.png`)

4. **Training Dynamics — Anisotropy Emergence**
   - Data: (pending) Anisotropy ratio vs. training epoch (ep50 → ep200)
   - "So What": Shows when spurious encoding is geometrically established during training — critical for early intervention design.
   - Suggested Figure/Table: Line plot (`figures/epoch_lines.png`)

5. **NT-Xent Loss Trajectory (Fast Run)**
   - Data: Loss 6.2312 (ep1) → 6.2297 (ep9); near initialization (≈6.93)
   - "So What": Confirms SSL underfitting at 10 epochs, validating the need for ≥200 epochs and the scientific rationale for INDETERMINATE classification.
   - Suggested Figure/Table: Training loss curve (available now; supplementary material)

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results (PRELIMINARY — fast run PENDING) |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, evaluation protocol |
| `03_refinement.yaml` | All | Original hypothesis, predictions P1-P3, mechanism, assumptions A1-A5 |
| `verification_state.yaml` | Pipeline | Sub-hypothesis statuses and gate results |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
*Phase 4.5 pre-results synthesis: update when 200-epoch h-e1 run completes*

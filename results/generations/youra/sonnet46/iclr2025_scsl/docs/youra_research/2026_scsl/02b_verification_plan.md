---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-03-16T21:22:00Z"
generatedAt: "2026-03-16T21:10:00Z"
hypothesis_id: "H-GNR-LLR-v1"
---

# Verification Plan: GNR-LLR — Gradient-Norm-Informed Last-Layer Retraining for Spurious Correlation Robustness

**Date:** 2026-03-16
**Hypothesis ID:** H-GNR-LLR-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ERM+SGD training on spuriously correlated image classification benchmarks (Waterbirds primary, CelebA secondary), if per-sample last-layer gradient norms normalized by feature magnitude (g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)||) are computed at early training epochs (T_id ∈ {3, 5}) and used to construct a pseudo-group-balanced subset (top-k% high-norm as pseudo-minority, bottom-k% low-norm as pseudo-majority) for ERM feature extractor freezing + last-layer retraining (GNR-LLR), then worst-group accuracy (WGA) on Waterbirds will be ≥ 88% and on CelebA ≥ 82%, because minority-group samples that cannot be fit by the spurious-feature shortcut solution produce persistently elevated gradient norms (6–14x majority) reflecting structured-feature resistance under NHT norm-hierarchy dynamics.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in worst-group accuracy (WGA) between GNR-LLR and JTT (Just Train Twice) on Waterbirds or CelebA when using the same identification epoch T_id, backbone (ResNet-50), and training protocol. That is: per-sample gradient norm provides no additional actionable information for minority group identification beyond JTT's binary misclassification signal.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Confirmed spuriously correlated benchmark with 4 groups (y ∈ {landbird, waterbird} × place ∈ {land, water}). Minority groups: G1(landbird/water)=184 train, G2(waterbird/land)=56 train. Gradient norm ratio confirmed 6–14x from prior runs. Full test set n=5794 for WGA evaluation. |
| **Model** | ResNet-50 (ImageNet pretrained) | Confirmed working from prior runs. BatchNorm layers normalize feature magnitudes. Last layer: FC(2048 → 2). Feature extractor freezable for last-layer retraining. |

**Dataset Details:**
- Source: Sagawa et al. 2019 (GroupDRO)
- Path: `.data_cache/datasets/waterbirds/`

**Model Details:**
- Type: CNN
- Source: `torchvision.models.resnet50(pretrained=True)`

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| JTT (Liu et al., 2021) | WGA 86.7% Waterbirds, 81.1% CelebA | Waterbirds, CelebA, MultiNLI, CivilComments |
| DFR (Kirichenko et al., 2023) | WGA 92.9% Waterbirds, 88.3% CelebA | Waterbirds, CelebA, MultiNLI, CivilComments |
| LfF (Nam et al., 2020) | WGA ~84.24% CelebA | Colored MNIST, CIFAR-10, CelebA, BAR |
| GroupDRO (Sagawa et al., 2019) | WGA 91.4% Waterbirds | Waterbirds, CelebA |
| ERM+SGD baseline | WGA ~72-76% Waterbirds | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Normalized gradient norm disparity (minority/majority ratio ≥ 3x) persists after feature-norm normalization g_tilde_i = ‖∇_W ℓ_i‖ / ‖h(x_i)‖ | Raw ratio is 6–14x from prior runs; BatchNorm in ResNet-50 equalizes feature norms; LfF confirms minority samples harder independently of feature scale | GNPR is a feature-scale proxy, not shortcut-resistance proxy. Method may still work heuristically but mechanistic claim fails. |
| A2 | Top-k% selection by normalized gradient norm induces approximate group-balance in the selected subset (P(g\|y) within-class deviation ≤ 10% from uniform) | Given 6–14x norm disparity, minority samples dominate high-norm tails; top-25% by norm expected >80% enriched for G1+G2 | DFR-style last-layer retraining cannot achieve high WGA; method may improve WGA via upweighting but not at DFR level |
| A3 | Temporal persistence: normalized gradient norm disparity remains ≥ 1.2x after shortcut-layer norms peak (t > T_peak_sc) | Per-epoch data: E1=6.10 → E4=14.73 → E5=12.20 — no collapse in epochs 1–5; NHT: minority samples continue resisting M_sc | Gradient norm is phase-locked to shortcut acquisition. T_id=5 still works practically but temporal mechanism claim fails. |
| A4 | ERM feature representations (frozen during Stage 2) encode sufficient non-spurious information to achieve high WGA when classifier head is corrected | DFR explicitly proves this on Waterbirds and CelebA: ERM features are sufficient; 92.9% WGA with correct head | GNR-LLR fails entirely; would require full-model retraining instead |
| A5 | Gradient norm signal generalizes from Waterbirds to CelebA: disparity exists at similar ratio and provides effective pseudo-balanced subset | LfF achieves debiasing on CelebA (84.24% vs 62.00% baseline) using same early-training mechanism; JTT also works on CelebA | Waterbirds result doesn't generalize. Single-dataset result weaker but still publishable. |

### 1.6 Research Gap & Novelty

**First published method** using per-sample gradient norm magnitude as the signal for pseudo-group-balanced subset construction in DFR-style last-layer retraining, without group label supervision. GNR-LLR: uses normalized gradient norms (g_tilde_i) to identify a pseudo-group-balanced subset, replacing DFR's requirement for group-annotated validation set and JTT's binary misclassification threshold with a continuous magnitude signal grounded in NHT norm-hierarchy theory. Key differentiators: (1) vs JTT — continuous vs binary, captures barely-correct minority samples; (2) vs DFR — no group annotations required; (3) vs LfF — single-pass, no second network.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | MUST_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Normalized Gradient Norm as Valid Minority Group Proxy**

**Statement**: Under ERM training on Waterbirds with ResNet-50, if per-sample normalized last-layer gradient norms (g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)||) are computed at early epochs (T_id ∈ {3,5}), then (a) minority/majority ratio ≥ 3x persists after normalization, (b) AUC of g_tilde for predicting minority group membership > 0.70, and (c) top-25% high-norm subset deviates ≤ 10% from within-class group balance — because minority samples resist the spurious shortcut, producing persistently elevated prediction residuals.

**Rationale**:
This is the foundational existence test. If the gradient norm signal is not a valid proxy (fails AUC or ratio test), the entire GNR-LLR pipeline collapses. Phase 2A confirmed 6–14x raw ratio from prior runs; this hypothesis tests whether that signal survives feature-norm normalization and provides actionable minority identification.

**Variables** (from Phase 2A):
- IV: Normalized gradient norm g_tilde_i, identification epoch T_id ∈ {3,5}
- DV: (1) Minority/majority ratio of g_tilde, (2) AUC(g_tilde → minority group), (3) Contingency table balance deviation
- CV: ResNet-50, Waterbirds 4795 train, 5 seeds, lr=0.001, momentum=0.9, batch_size=128

**Verification Protocol**:
1. Train ResNet-50 ERM on Waterbirds for 10 epochs with per-sample gradient norm hooks on last FC layer.
2. Compute raw ratio and normalized ratio (g_tilde) at epochs 1, 3, 5, 10 for each group.
3. At T_id=5, compute AUC of g_tilde for predicting binary minority membership using Waterbirds group labels (post-hoc, evaluation only).
4. Select top-25% by g_tilde; compute contingency table (y, g) and measure max within-class deviation from uniformity.
5. Report all metrics averaged over 5 seeds with standard deviation.

**Success Criteria**:
- Primary: Normalized ratio ≥ 3x at T_id=5 (confirms prediction-residual mechanism)
- Secondary: AUC(g_tilde) > 0.70; contingency table deviation ≤ 10%

**Failure Response**:
- IF ratio < 1.5x after normalization: PIVOT — gradient norm is feature-scale proxy; explore alternative normalization or switch to raw norm
- IF AUC ≤ 0.60: ABORT H-GNR-LLR-v1 — signal too noisy to be useful proxy
- IF balance deviation > 30%: PIVOT — use weighted sampling rather than hard threshold

**Dependencies**: None (foundational)

**Source**: Phase 2A Section 5 (sh1_existence), Section 1.3 Causal Step 1-2, Prediction P2-P3

---

**H-M1: Temporal Persistence of Gradient Norm Disparity**

**Statement**: Under ERM training on Waterbirds, if normalized gradient norm disparity (g_tilde minority/majority ratio) is measured at multiple epochs (1, 3, 5, 10), then the ratio remains ≥ 1.2x at epoch T_id=10 (post-T_peak_sc), and is maximal at epochs 3-5, because minority samples continue resisting the shortcut feature basin M_sc even after the shortcut phase dominates (NHT temporal alignment).

**Rationale**:
This tests the temporal mechanism from NHT theory. If norm disparity is phase-locked to shortcut acquisition (collapses synchronously with T_peak_sc), the proxy signal cannot reliably identify minority samples across different training configurations. Temporal persistence is the critical precondition for T_id selection generalizability.

**Variables**:
- IV: Training epoch T_id ∈ {1, 3, 5, 10, 20}
- DV: Normalized gradient norm ratio (g_tilde minority mean / majority mean) at each epoch
- CV: ResNet-50, weight decay λ = 1e-4, 5 seeds

**Verification Protocol**:
1. Track per-group mean g_tilde at each epoch 1-20 using gradient hooks from H-E1 experiment (no extra training runs needed).
2. Track layer-wise weight norms to identify T_peak_sc (epoch where shortcut layer norms peak).
3. Compute g_tilde ratio at T_id=10 and compare to ratio at T_id=5.
4. Test across λ ∈ {0, 1e-4, 5e-4} to assess NHT-predicted λ sensitivity.
5. Report ratio trajectory per epoch, mark T_peak_sc.

**Success Criteria**:
- Primary: g_tilde ratio ≥ 1.2x at T_id=10 (temporal persistence confirmed)
- Secondary: Ratio is maximal at T_id ∈ {3-5} (optimal identification window)

**Failure Response**:
- IF ratio < 1.2x at T_id=10: SCOPE — temporal mechanism claim is limited; document as "use T_id ≤ 5 for best signal" without temporal persistence claim

**Dependencies**: H-E1 (requires confirmed disparity signal)

**Source**: Phase 2A Section 1.3 Causal Step 1, Prediction P3, Key Tension, Assumption A3

---

**H-M2: Feature-Norm Normalization Isolates Prediction-Error Component**

**Statement**: Under ERM training on Waterbirds at T_id=5, if the raw gradient norm ratio (||∇_W ℓ_i|| minority/majority) is compared to the feature-normalized ratio (g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)|| minority/majority), then both ratios remain ≥ 3x (not collapsing to ≤ 1.5x), confirming that the 6-14x disparity is driven by prediction residuals (||p_i - y_i||), not by feature magnitude differences, because BatchNorm in ResNet-50 equalizes ||h(x_i)|| across groups.

**Rationale**:
This is the mechanistic decomposition test. The last-layer gradient decomposes as ||∇_W ℓ_i|| ∝ ||h(x_i)|| × ||p_i - y_i||. If the ratio survives normalization, the mechanism is prediction-error (shortcut resistance). This is required to claim that GNR-LLR is mechanistically grounded rather than a feature-scale heuristic.

**Variables**:
- IV: Normalization method (raw vs. feature-normalized)
- DV: Minority/majority gradient norm ratio under each normalization
- CV: T_id=5, ResNet-50, Waterbirds, 5 seeds

**Verification Protocol**:
1. From H-E1 experiment, extract per-sample raw gradient norms and feature vectors at T_id=5.
2. Compute per-group means of both raw and normalized norms.
3. Report ratio drop = (raw ratio - normalized ratio) / raw ratio; if < 50% drop, feature scale is not dominant.
4. Perform statistical test (Mann-Whitney U) on raw vs normalized ratio distributions.
5. Compare minority feature norms vs majority feature norms to quantify BatchNorm equalization effect.

**Success Criteria**:
- Primary: Normalized ratio ≥ 3x (mechanism is prediction-error, not feature scale)
- Secondary: Ratio drop < 50% (feature scale accounts for < half the raw disparity)

**Failure Response**:
- IF normalized ratio < 1.5x: SCOPE — GNR-LLR may still work empirically but mechanistic NHT claim is unsupported; publish as empirical finding

**Dependencies**: H-M1 (temporal persistence verified)

**Source**: Phase 2A Section 1.3 Causal Step 2, Assumption A1, Prediction P3

---

**H-M3: Norm-Based Selection Induces Pseudo-Group Balance**

**Statement**: Under ERM training on Waterbirds at T_id=5, if top-k% samples by g_tilde are selected as pseudo-minority and bottom-k% as pseudo-majority (k ∈ {10, 20, 25, 30}%), then the induced contingency table (y, g) in the selected subset deviates ≤ 10% from within-class group uniformity, because the 6-14x norm disparity results in minority samples dominating the high-norm tail of the distribution.

**Rationale**:
This is the critical empirical link between the proxy signal and the DFR mechanism. DFR requires a group-balanced subset to retrain the classifier head; this hypothesis tests whether gradient-norm-based selection achieves approximate balance without group annotations. Failure here means WGA improvement is limited even if the proxy signal is valid.

**Variables**:
- IV: k (subset fraction) ∈ {10, 20, 25, 30}%
- DV: Max deviation from within-class group uniformity in selected top-k% subset
- CV: T_id=5, normalized g_tilde, ResNet-50, Waterbirds, 5 seeds

**Verification Protocol**:
1. From H-E1 experiment, select top-k% and bottom-k% samples by g_tilde at T_id=5 for k ∈ {10,20,25,30}%.
2. For each k, compute contingency table over (y ∈ {0,1}, g ∈ {0,1,2,3}) for the selected subset.
3. Compute within-class group balance as max |P(g|y,selected) - P(g|y,uniform)| for each class y.
4. Report balance deviation at each k; find optimal k that minimizes deviation while maintaining subset size.
5. Compare induced balance vs. JTT's error-set balance at same k.

**Success Criteria**:
- Primary: Max within-class deviation ≤ 10% at k=25% (DFR-quality balance)
- Secondary: Balance is better than JTT's error-set at same k (AUC-based enrichment advantage)

**Failure Response**:
- IF deviation > 30%: PIVOT — explore soft-weighting (upweight by norm magnitude) instead of hard top-k% selection

**Dependencies**: H-M2 (normalization mechanism confirmed)

**Source**: Phase 2A Section 1.3 Causal Step 3, Assumption A2, Phase 2B sh1_existence item 3

---

**H-M4: GNR-LLR Achieves DFR-Level WGA Without Group Annotations**

**Statement**: Under ERM training on Waterbirds with ResNet-50, if the GNR-LLR procedure (train ERM 5 epochs → compute g_tilde → select pseudo-balanced subset at k=25% → freeze feature extractor → retrain last layer 100 epochs) is applied, then worst-group accuracy (WGA) ≥ 88% on the full Waterbirds test set (n=5794) without any group label supervision, significantly exceeding JTT (86.7%) with p < 0.05 (one-sided paired t-test over 5 seeds), because the pseudo-balanced subset is sufficient for head correction following DFR's established principle.

**Rationale**:
This is the primary efficacy test of the complete GNR-LLR pipeline. It validates the full causal chain from gradient norm computation through last-layer retraining to WGA improvement. The 88% threshold is below DFR's 92.9% (group-supervised) but must exceed JTT (86.7%) to justify the method as a label-free alternative.

**Variables**:
- IV: Method ∈ {GNR-LLR, JTT, ERM baseline}
- DV: WGA = min(WGA_g0..g3) on Waterbirds test set (n=5794)
- CV: ResNet-50, T_id=5, k=25%, λ=1e-4, Stage 2 100 epochs lr=0.01, 5 seeds

**Verification Protocol**:
1. Run full GNR-LLR pipeline: Stage 1 ERM (20 epochs, lr=0.001, wd=1e-4) → compute g_tilde at epoch 5 → select top/bottom 25% → Stage 2 last-layer retrain (100 epochs, lr=0.01).
2. Run JTT baseline: same Stage 1 → misclassification set → same Stage 2 protocol.
3. Evaluate both on Waterbirds test set using existing evaluate.py infrastructure.
4. Perform one-sided paired t-test: GNR-LLR WGA > JTT WGA (p < 0.05).
5. Also evaluate on CelebA (secondary) for generalization signal.

**Success Criteria**:
- Primary: Mean WGA ≥ 88% on Waterbirds test set (n=5794) over 5 seeds; p < 0.05 vs JTT
- Secondary: Average accuracy does not drop > 5pp relative to ERM baseline

**Failure Response**:
- IF WGA ∈ [85%, 88%): SCOPE — document as "approaches JTT level" with analysis of failure cases; modify k or T_id
- IF WGA ≤ 85% or indistinguishable from JTT: ABORT H-GNR-LLR-v1 → return to Phase 0

**Dependencies**: H-M3 (subset balance mechanism confirmed)

**Source**: Phase 2A Section 1.1, Prediction P1, Assumption A4, Phase 2B sh2_mechanism

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ratio ≥ 3x AND AUC > 0.70 AND balance ≤ 10% | STOP — reassess proxy signal; if AUC ≤ 0.60 ABORT |
| H-M1 | MUST_WORK | g_tilde ratio ≥ 1.2x at T_id=10 | SCOPE — limit T_id claim; continue pipeline |
| H-M2 | SHOULD_WORK | normalized ratio ≥ 3x (< 50% drop from raw) | SCOPE — publish as empirical; continue pipeline |
| H-M3 | SHOULD_WORK | max within-class deviation ≤ 10% at k=25% | PIVOT — soft-weighting; continue pipeline |
| H-M4 | MUST_WORK | WGA ≥ 88% on Waterbirds (n=5794), p < 0.05 vs JTT | SCOPE/ABORT — if ≤ 85% return to Phase 0 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2 (parallel to H-E1 data) | 2 weeks |
| Phase 2: Mechanisms | H-M3 | 1 week |
| Phase 2: Mechanisms | H-M4 (full pipeline) | 1 week |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Normalization collapses disparity | A1 | H-E1, H-M2 | **High** |
| R2: Subset balance insufficient | A2 | H-M3, H-M4 | **High** |
| R3: Temporal phase-lock | A3 | H-M1, H-M4 | **Medium** |
| R4: ERM features insufficient | A4 | H-M4 | **Critical** |
| R5: CelebA non-generalization | A5 | H-M4 (secondary) | **Medium** |

---

### 4.2 Mitigation Strategies

**Risk R1: Normalization Collapses Disparity**

**Source Assumption:** A1 — Normalized gradient norm disparity (minority/majority ratio ≥ 3x) persists after feature-norm normalization

**Description:** BatchNorm might not fully equalize feature norms across groups; if minority features are systematically larger, g_tilde ratio could collapse from 6-14x to < 1.5x.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** High (mechanism claim depends on this)

**Mitigation Strategy:**
1. **Prevention:** Verify per-group feature norm statistics before committing to the normalized signal; if norms differ > 2x across groups, pre-normalize features before computing g_tilde.
2. **Detection:** Compare raw vs. normalized ratio at T_id=5; if drop > 70%, alert to normalization issue.
3. **Response:**
   - PIVOT: Use layer-wise gradient norm (not last-layer only) which may be less feature-magnitude-sensitive
   - SCOPE: Publish GNR-LLR as empirical method without mechanistic NHT claim
   - ABORT: Only if AUC < 0.60 (signal entirely useless)

**Early Warning Indicators:**
- Per-group ||h(x_i)|| ratio > 2x at T_id=5
- Raw-to-normalized ratio drop > 70%

---

**Risk R2: Subset Balance Insufficient**

**Source Assumption:** A2 — Top-k% selection induces ≤ 10% within-class group balance deviation

**Description:** Despite 6-14x norm disparity, top-k% selection might not achieve near-group-balance because minority samples (G1, G2) are small fractions of training data (184, 56 out of 4795). At k=25%, 1199 samples selected; if minority enrichment is insufficient, DFR-style head correction fails.

**Affected Hypotheses:** H-M3, H-M4

**Severity:** High (directly affects WGA outcome)

**Mitigation Strategy:**
1. **Prevention:** Sweep k ∈ {10, 20, 25, 30}% and measure balance at each; select optimal k from H-M3 before running H-M4.
2. **Detection:** Report contingency table deviation per k in H-M3 results.
3. **Response:**
   - PIVOT: Switch from hard top-k% to soft-weighting (upweight by g_tilde magnitude, downweight by 1/g_tilde), which is more robust to class-size imbalance
   - SCOPE: If balance achieves 20-30% deviation: use DFR-style augmented retraining with upweighting rather than pure subset selection

**Early Warning Indicators:**
- Minority group proportion in top-25% subset < 15% (when true minority fraction is ~5%)
- Subset WGA after retraining < 82%

---

**Risk R3: Temporal Phase-Lock**

**Source Assumption:** A3 — Normalized gradient norm disparity remains ≥ 1.2x after shortcut norm peak (t > T_peak_sc)

**Description:** If gradient norm disparity is phase-locked to shortcut acquisition, ratio collapses at T_peak_sc (approximately epoch 5-10). This invalidates the temporal persistence mechanism claim from NHT theory, though T_id=5 may still work practically.

**Affected Hypotheses:** H-M1, H-M4

**Severity:** Medium (affects mechanistic claim, not necessarily method performance)

**Mitigation Strategy:**
1. **Prevention:** Measure per-epoch ratio trajectory to identify T_peak_sc precisely; use T_id before peak.
2. **Detection:** Track both group-norm disparity AND layer-weight-norm trajectory simultaneously in H-M1.
3. **Response:**
   - SCOPE: If ratio collapses at T_id=10 but T_id=5 still has ratio ≥ 3x: publish with "use T_id ∈ {3,5}" guidance; drop temporal persistence claim from NHT narrative
   - PIVOT: Test weight-decay variants to shift T_peak_sc per NHT prediction (λ=0 extends shortcut phase)

**Early Warning Indicators:**
- g_tilde ratio drops below 2x at epoch 7-8
- Layer-weight norm peak observed at epoch < 5

---

**Risk R4: ERM Features Insufficient (Critical)**

**Source Assumption:** A4 — Frozen ERM features encode sufficient non-spurious information for last-layer correction to achieve high WGA

**Description:** If ERM training (with spurious correlation) degrades the feature extractor such that spurious and core features are entangled at the representation level, last-layer retraining cannot disentangle them. This contradicts DFR's established finding but could occur if the model is trained longer or on a different distribution.

**Affected Hypotheses:** H-M4

**Severity:** Critical (entire GNR-LLR approach fails)

**Mitigation Strategy:**
1. **Prevention:** Confirm DFR oracle (true group-balanced retraining) achieves ≥ 90% WGA as sanity check; if DFR fails, features are degraded (stop pipeline).
2. **Detection:** Run DFR with true group labels as oracle before committing to GNR-LLR; if oracle WGA < 88%, feature extractor is the bottleneck.
3. **Response:**
   - ABORT: If DFR oracle fails (WGA < 88%) → features are insufficient → return to Phase 0
   - PIVOT: If GNR-LLR fails but DFR oracle passes → subset balance issue (R2), not feature quality

**Early Warning Indicators:**
- DFR oracle WGA < 88% (strong signal of feature quality issue)
- ERM baseline WGA < 70% (model not learning meaningful features)

---

**Risk R5: CelebA Non-Generalization**

**Source Assumption:** A5 — Gradient norm signal generalizes from Waterbirds to CelebA with comparable ratio and WGA improvement

**Description:** CelebA has different spurious correlation structure (hair color vs. gender), larger dataset (162K train), and different minority fraction. Gradient norm dynamics may differ significantly, requiring different T_id or k.

**Affected Hypotheses:** H-M4 (secondary experiment)

**Severity:** Medium (CelebA is secondary; Waterbirds is primary)

**Mitigation Strategy:**
1. **Prevention:** Run same norm analysis on CelebA before full pipeline; if ratio < 2x, adjust T_id or use raw norms.
2. **Detection:** Compare norm ratio trajectory on CelebA vs. Waterbirds at epochs 1-10.
3. **Response:**
   - SCOPE: If CelebA result < 82% but Waterbirds passes: publish Waterbirds as primary result with "CelebA requires hyperparameter adjustment" as limitation
   - PIVOT: Search for optimal T_id and k for CelebA separately if Waterbirds protocol fails

**Early Warning Indicators:**
- CelebA norm ratio < 2x at T_id=5
- CelebA DFR oracle WGA significantly below 88.3% (suggests feature degradation on CelebA)

---

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Normalization collapses disparity | A1 | **High** | H-E1, H-M2 | PIVOT to layer-wise norm; SCOPE to empirical claim |
| R2 | Subset balance insufficient | A2 | **High** | H-M3, H-M4 | PIVOT to soft-weighting; sweep k |
| R3 | Temporal phase-lock | A3 | **Medium** | H-M1, H-M4 | SCOPE temporal claim; use T_id=5 only |
| R4 | ERM features insufficient | A4 | **Critical** | H-M4 | DFR oracle sanity check; ABORT if oracle fails |
| R5 | CelebA non-generalization | A5 | **Medium** | H-M4 (2°) | SCOPE to Waterbirds primary; separate CelebA tuning |

Critical Risks: 1 (R4)
High Risks: 2 (R1, R2)
Medium Risks: 2 (R3, R5)
Low Risks: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses | H-GNR-LLR-v1
═══════════════════════════════════════════════════════════════════

[Level 0 — Root: Foundation]
    H-E1 (EXISTENCE — no dependencies)
    Validates: gradient norm is valid minority proxy (AUC, ratio, balance)
         │
         ▼  [GATE 1: MUST PASS — if fails, STOP entire pipeline]
         │
[Level 1 — Mechanism: Temporal Persistence]
    H-M1 ← H-E1
    Validates: disparity persists temporally (ratio ≥ 1.2x post-T_peak_sc)
         │
         ▼  [continue if H-M1 passes; SCOPE if fails]
         │
[Level 2 — Mechanism: Normalization Decomposition]
    H-M2 ← H-M1
    Validates: feature-norm normalization isolates prediction-error component
         │
         ▼  [continue regardless; SCOPE mechanistic claim if fails]
         │
[Level 3 — Mechanism: Subset Balance]
    H-M3 ← H-M2
    Validates: top-k% selection induces ≤10% within-class group balance deviation
         │
         ▼  [GATE 2: MUST PASS (H-M3) — if fails, PIVOT to soft-weighting before H-M4]
         │
[Level 4 — Mechanism: End-to-End WGA]
    H-M4 ← H-M3
    Validates: full GNR-LLR pipeline achieves WGA ≥ 88% on Waterbirds (n=5794)
         │
         ▼  [GATE 3: MUST PASS — if fails, SCOPE or ABORT]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
No parallelization (sequential causal chain)
Note: H-M1 and H-M2 data collected simultaneously (same training run as H-E1)
═══════════════════════════════════════════════════════════════════
```

### 5.1b Verification Phases with Gate Conditions

**Phase 1 — Foundation** (H-E1)

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Gradient norm proxy validity: ratio ≥ 3x, AUC > 0.70, balance ≤ 10% | **MUST PASS** |

→ **Gate 1**: H-E1 FAIL → STOP, reassess GNR-LLR hypothesis entirely. If AUC ≤ 0.60, ABORT.

**Phase 2 — Core Mechanisms** (H-M1 through H-M3)

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS (temporal mechanism) |
| H-M2 | H-M1 | SHOULD PASS (decomposition claim) |
| H-M3 | H-M2 | MUST PASS (subset balance for DFR) |

→ **Gate 2**: H-M1 FAIL → SCOPE temporal claim, continue. H-M3 FAIL → PIVOT to soft-weighting before H-M4.

**Phase 3 — End-to-End Validation** (H-M4)

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M4 | H-M3 | **MUST PASS** (primary efficacy) |

→ **Gate 3**: WGA < 88% → SCOPE (if 85-88%) or ABORT (if ≤ 85% or indistinguishable from JTT).

### 5.1c Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | MUST_WORK |

### 5.2 Critical Path Analysis

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses | H-GNR-LLR-v1
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3-4     │ W5       │ W6       │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation   │          │          │          │          │
  H-E1 (proxy valid.) │ ████████ │          │          │          │
  [Gate 1 ◆]          │        ◆ │          │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms   │          │          │          │          │
  H-M1 (temporal)     │ ░░░░░░░░ │ ████████ │          │          │
  [data from H-E1]    │          │          │          │          │
  H-M2 (normalization)│          │ ████████ │          │          │
  [data from H-E1]    │          │          │          │          │
  H-M3 (subset bal.)  │          │        ◆ │ ████████ │          │
  [Gate 2 ◆]          │          │          │        ◆ │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 3: End-to-End   │          │          │          │          │
  H-M4 (WGA ≥ 88%)   │          │          │          │ ████████ │
  [Gate 3 ◆]          │          │          │          │        ◆ │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ░░░░ = Data collection (piggyback on H-E1 run)
        ◆ = Gate decision point
Total Duration: 6 weeks
Note: H-M1 and H-M2 data collected simultaneously with H-E1 training (same run)
═══════════════════════════════════════════════════════════════════════
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1 + H-M2, data collected in H-E1 run) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (fully sequential chain)

Practical optimization:
  - H-M1 + H-M2 measurements piggyback on H-E1 training run (per-epoch hook data)
  - Actual additional compute beyond H-E1: ~1 GPU-day for H-M3 subset analysis
  - H-M4 (full pipeline): ~2 GPU-days for Stage 1 + Stage 2 × 5 seeds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)

Verification Phases: 3
1. Foundation (H-E1): gradient norm proxy validation
2. Mechanisms (H-M1, H-M2, H-M3): causal chain validation
3. End-to-End (H-M4): full pipeline WGA validation

Total Duration: 6 weeks (gate-enforced sequential)
Critical Path: 6 weeks (no slack)
Execution Mode: Sequential chain (data sharing H-E1↔H-M1,H-M2)

Compute estimate:
- H-E1 + H-M1 + H-M2: ~3 GPU-days (10-epoch ERM × 5 seeds with hooks)
- H-M3: ~0.5 GPU-days (analysis only, no new training)
- H-M4: ~5 GPU-days (20-epoch ERM + 100-epoch LLR × 5 seeds; +JTT baseline)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Execution Order

**Step 1**: Execute H-E1 (Foundation) — Week 1-2
  - Train ERM 10 epochs with per-sample gradient norm hooks
  - Record g_tilde at epochs 1,3,5,10; compute AUC and subset balance
**Step 2**: Collect H-M1 + H-M2 data (from H-E1 run) — Week 3-4
  - Track ratio trajectory across epochs; compute raw vs. normalized comparison
  - Identify T_peak_sc from layer-weight norm trajectory
**Step 3**: Evaluate Gate 1 (H-E1) → If AUC > 0.70 AND ratio ≥ 3x: proceed
**Step 4**: Evaluate H-M1 → If ratio ≥ 1.2x at T_id=10: PASS; else SCOPE
**Step 5**: Evaluate H-M2 → If normalized ratio ≥ 3x: PASS; else SCOPE
**Step 6**: Execute H-M3 — Week 5
  - Compute contingency tables for k ∈ {10,20,25,30}%
  - Find optimal k minimizing balance deviation
**Step 7**: Evaluate Gate 2 (H-M3) → If deviation ≤ 10%: proceed; else PIVOT to soft-weighting
**Step 8**: Execute H-M4 — Week 6
  - Run full GNR-LLR pipeline: 20-epoch ERM → g_tilde selection → 100-epoch LLR
  - Run JTT baseline for direct comparison
  - Evaluate WGA on Waterbirds test set (n=5794), 5 seeds
**Step 9**: Evaluate Gate 3 (H-M4) → If WGA ≥ 88% and p < 0.05 vs JTT: PASS → Phase 5
**Final**: Verification complete → proceed to Phase 5 (Baseline Comparison) or Phase 6 if skip_baseline_comparison=true

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** GNR-LLR achieves WGA ≥ 88% on Waterbirds without group label supervision, using normalized per-sample gradient norms as a minority group proxy for pseudo-group-balanced last-layer retraining.

**Supporting Evidence:**
1. Confirmed 6-14x raw gradient norm ratio from prior experimental runs (per-group measurements, Waterbirds, epochs 1-5)
2. NHT framework (Khanh & Hoa 2026) provides mechanistic explanation: minority samples resist shortcut basin M_sc, maintaining elevated prediction residuals
3. DFR (Kirichenko 2023) proves ERM features sufficient; last-layer correction achieves 92.9% WGA with group-balanced subset

**Strengths:**
- Strong empirical foundation from prior runs (not just theoretical)
- Principled continuous proxy vs. JTT's heuristic binary threshold
- Single-pass efficiency (no second network, no full-model retraining)
- DFR principle is well-established — reduces to known-good method under oracle conditions

**Expected Outcomes:**
- Primary: WGA ≥ 88% on Waterbirds (P1)
- Secondary: AUC(g_tilde) > AUC(misclassification) at T_id=5 (P2)
- Tertiary: Normalized ratio ≥ 3x; ratio ≥ 1.2x at T_id=10 (P3)

---

### 6.2 Antithesis (H0)

**Null Hypothesis (H0):** There is no significant difference in WGA between GNR-LLR and JTT; gradient norm provides no additional actionable information beyond binary misclassification signal.

**Counter-Arguments:**
1. JTT already achieves 86.7% — claimed 1.3pp gain (to 88%) is within seed variance; may not be statistically significant
2. Feature normalization may collapse the 6-14x ratio if minority features are systematically larger (A1 violation)
3. Very small G2 minority (56 training samples = 1.2% of data) may not sufficiently dominate the high-norm tail even with 6-14x disparity

**Potential Failure Points:**
- R1: Normalization collapses disparity (H-E1, H-M2 fail)
- R2: Subset balance insufficient due to tiny minority fractions (H-M3 fails)
- R4: Feature extractor does not separate spurious from core (H-M4 fails)

**Conditions Under Which H0 Would Be Supported:**
- AUC(g_tilde → minority) ≤ 0.60 after H-E1 test
- Normalized ratio < 1.5x at T_id=5 (mechanism is feature scale)
- WGA statistically indistinguishable from JTT (p > 0.05, one-sided test)

---

### 6.3 Synthesis

**Balanced Assessment:** The hypothesis H-GNR-LLR-v1 presents a mechanistically grounded and empirically motivated claim that the continuous gradient norm signal captures more minority group information than JTT's binary threshold. However, the null hypothesis raises valid concerns about signal collapse after normalization and about the feasibility of subset balance given very small minority fractions.

**Resolution Path — The verification plan addresses this dialectic through:**
1. **Foundation (H-E1):** Direct falsification of H0 via AUC test and ratio measurement — if AUC > 0.70, gradient norm IS an informative proxy
2. **Sequential mechanism testing (H-M1 through H-M3):** Resolves each antithesis concern at the earliest gate; no wasted compute if any mechanism step fails
3. **Gate conditions:** H-M4 paired t-test (5 seeds) provides statistical resolution of the marginal gain concern

**Conditions for Thesis Support:**
- All MUST_WORK gates pass: H-E1 (AUC>0.70, ratio≥3x), H-M4 (WGA≥88%, p<0.05 vs JTT)
- Prediction P1 confirmed (WGA ≥ 88%)

**Conditions for Antithesis (H0) Support:**
- H-E1 fails (AUC ≤ 0.60) — gradient norm is uninformative
- H-M4 WGA statistically indistinguishable from JTT (p > 0.05)
- Normalized ratio < 1.5x (mechanism is feature scale, not shortcut resistance)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 passes, H-M1-3 pass, H-M4 WGA ≥ 88% p<0.05 → Thesis validated; submit GNR-LLR
2. **Partial Support:** H-E1 passes, H-M3 requires PIVOT, H-M4 WGA 85-88% → Publish as empirical improvement without mechanistic NHT claim
3. **H0 Support:** H-E1 fails AUC ≤ 0.60 or H-M4 p > 0.05 → Gradient norm offers no advantage; return to Phase 0

---

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Signal Quality | 6-14x ratio, AUC > 0.70 | Feature normalization collapse | H-E1: ratio + AUC measurement |
| Mechanism | NHT-grounded prediction residual | Could be feature-scale artifact | H-M2: raw vs. normalized comparison |
| Subset Balance | ≤10% deviation achievable | G2=56 too small for enrichment | H-M3: contingency table across k values |
| Performance | WGA ≥ 88%, p<0.05 vs JTT | Marginal gain within noise | H-M4: paired t-test, 5 seeds |
| Generalization | Works on CelebA too | Dataset-specific dynamics | H-M4 secondary CelebA experiment |

**Overall Robustness Score:** Medium-High (well-grounded thesis with clear empirical falsification criteria)

**Confidence in Verification Plan:** 0.78 (matching Phase 2A confidence)

---

## 7. Executive Summary & Conclusions

## Executive Summary

**Main Hypothesis:** GNR-LLR uses normalized per-sample gradient norms to construct pseudo-group-balanced subset for last-layer retraining, targeting WGA ≥ 88% on Waterbirds without group labels.
- ID: H-GNR-LLR-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A complete)
- Sub-Hypotheses: 5 total (H-E1 + H-M1 + H-M2 + H-M3 + H-M4)
- Phases: 3 phases over 6 weeks
- Critical Gates: 3 decision points (Gate 1: H-E1, Gate 2: H-M3, Gate 3: H-M4)

**Risk Assessment:** Medium-High
- Critical concern: ERM feature quality (R4) — mitigated by DFR oracle sanity check
- High concerns: normalization collapse (R1), subset balance with tiny minorities (R2)

**Immediate Action:** Begin Phase 1 with H-E1 (gradient norm proxy validation, 2 weeks, ~3 GPU-days)

## Conclusions

**Key Achievements:**
- 5 sub-hypotheses defined across 3 phases (H-E1 + H-M1-4)
- H0 addressed: Gradient norm provides no advantage over JTT binary misclassification
- 5 risks identified (1 Critical, 2 High, 2 Medium) with mitigation strategies
- Scope reduction: 57% (5 BUILD_ON claims not re-verified)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Normalized gradient norm validity — ratio ≥ 3x, AUC > 0.70, balance ≤ 10%
- Gate 1: MUST PASS — failure stops entire pipeline

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Temporal persistence — ratio ≥ 1.2x at T_id=10 (data from H-E1 run)
- H-M2: Normalization decomposition — normalized ratio ≥ 3x (data from H-E1 run)
- H-M3: Subset balance — ≤10% deviation within class at k=25%
- Gate 2: H-M3 must pass (or PIVOT to soft-weighting)

**Phase 3: End-to-End Validation** (1 week)
- H-M4: Full GNR-LLR pipeline — WGA ≥ 88%, p < 0.05 vs JTT (5 seeds, n=5794)
- Gate 3: Must pass for DETERMINES_SUCCESS gate in Phase 5

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - PASS → Proceed to Phase 2 (mechanisms)
   - AUC ≤ 0.60 → ABORT H-GNR-LLR-v1, return to Phase 0
   - Ratio < 1.5x → PIVOT normalization approach

2. **Gate 2 (Mechanisms):** H-M3 must pass
   - PASS → Proceed to H-M4 with confirmed subset construction
   - Deviation > 30% → PIVOT to soft-weighting before H-M4

3. **Gate 3 (End-to-End):** H-M4 WGA ≥ 88%
   - WGA ≥ 88%, p < 0.05 → PASS → Phase 5 (or Phase 6 if skip_baseline_comparison=true)
   - WGA 85-88% → SCOPE — publish empirical finding with limited claims
   - WGA ≤ 85% or p > 0.05 → ABORT → Phase 0

**Open Questions:**
- Does normalized gradient norm disparity persist after shortcut norm peaks (T_id=10)?
- Does top-k% norm selection induce near-balance in (y,g) contingency table with G2=56?
- Is per-sample gradient computation overhead acceptable vs. JTT's O(N) forward pass?
- Does gradient norm signal generalize to CelebA with comparable ratio?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (confirms proxy signal validity before committing to full pipeline)
   - Run DFR oracle simultaneously as sanity check (R4 mitigation)
   - Set CUDA_VISIBLE_DEVICES to single empty GPU before training

2. **Resource Allocation:**
   - H-E1+H-M1+H-M2: ~3 GPU-days (shared training run with hooks)
   - H-M3: ~0.5 GPU-days (analysis only)
   - H-M4: ~5 GPU-days (full pipeline × 5 seeds + JTT baseline)
   - Reserve 2 additional GPU-days for CelebA secondary experiments

3. **Failure Management:**
   - Document all gate results in verification_state.yaml
   - Execute PIVOT strategies before SCOPE or ABORT decisions
   - Run DFR oracle before H-M4 to distinguish feature quality (R4) from subset balance (R2) failures

---

## Appendices

### A. Phase 2A Reference
- **Source:** `docs/youra_research/20260315_scsl/03_refinement.yaml` (schema v10.0.0)
- **Hypothesis ID:** H-GNR-LLR-v1 | Generated: 2026-03-16 | 15 discussion exchanges

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4
- **Tools:** scientificmethod × 3 (H-E1, H-M1-2 chain, H-M3-4 chain), structuredargumentation × 3 (thesis, antithesis, synthesis)
- **Established Facts:** 5 BUILD_ON (not re-verified), 2 PROVE_NEW (tested in H-E1, H-M4)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-03-16*

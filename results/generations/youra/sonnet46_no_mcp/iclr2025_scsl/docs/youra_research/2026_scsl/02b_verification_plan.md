# Verification Plan: Temporal Feature Learning Gap — Spurious-Before-Core Dynamics of SGD

**Date:** 2026-05-04
**Hypothesis ID:** H-TemporalGap-v1
**Confidence:** 0.78
**Total Hypotheses:** 5
**Steps Completed:** step-00 through step-04 (in progress)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard ERM training on spurious correlation benchmarks (Waterbirds, CelebA),
if checkpoint linear probing is applied to measure spurious-label and core-label probe
accuracy at regular training intervals, then a measurable temporal gap delta(t) =
spurious_probe_acc(t) - core_probe_acc(t) > 0 will be observed during early training,
because SGD simplicity bias causes spurious (lower-complexity) features to be learned
faster than core (higher-complexity) features — and the transition epoch t* where delta
closes explains the success of post-hoc annotation-free methods (DFR, JTT).

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the temporal ordering of spurious vs. core feature
learning under standard ERM training on Waterbirds/CelebA; delta(t) <= 0 at all training
checkpoints, and DFR worst-group accuracy improvement is uncorrelated with epochs trained
past t*.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Canonical spurious correlation benchmark with well-documented 15pp worst-group accuracy gap for ERM; spurious feature (background) measurably simpler than core feature (bird species); established WGA evaluation protocol |
| **Model** | ResNet-50 | Standard architecture for Waterbirds/CelebA experiments across all baseline papers (GroupDRO, JTT, DFR); enables direct comparison |

**Dataset Details:**
- Source: Sagawa et al. 2020 (GroupDRO paper)
- Path: kohpangwei/group_DRO (GitHub) — includes dataset loaders
- Replication: CelebA (same source, hair color spurious / gender core)

**Model Details:**
- Type: CNN image classifier
- Source: torchvision pretrained on ImageNet
- Probe: Scikit-learn L2 logistic regression (frozen backbone features)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Notes |
|--------|-------------|---------|-------|
| ERM | ~72% WGA | Waterbirds | Lower bound; does not address spurious correlations |
| JTT | ~86% WGA | Waterbirds | Annotation-free heuristic; requires second training run |
| DFR | ~88% WGA | Waterbirds | Strongest annotation-free baseline; no mechanistic explanation |
| GroupDRO | ~91% WGA | Waterbirds | Upper bound; requires group annotations at training time |

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | If Violated |
|----|------------|---------------------|-------------|
| A1 | Spurious features in Waterbirds/CelebA are measurably simpler (lower-frequency) than core features | Simplicity Bias literature; spurious features (background texture, hair color) widely cited as simpler | delta(t) ≈ 0 throughout training; entire hypothesis collapses |
| A2 | Linear probing at checkpoints faithfully reflects feature encoding — higher probe accuracy = feature encoded | Linear probe standard in self-supervised evaluation | delta(t) does not measure what we claim; representational geometry issue |
| A3 | Temporal gap is consistent across random seeds — not an initialization artifact | Simplicity bias is structural property of gradient descent | High seed variance → t* unreliable as intervention point |
| A4 | DFR's success is primarily due to backbone encoding core features (not last-layer reweighting regularization) | DFR paper: "ERM backbone already encodes core features" | Mechanistic explanation fails even if delta(t) exists |
| A5 | Checkpoint every 2 epochs provides sufficient temporal resolution to identify t* | Standard ERM on Waterbirds ≈ 300 epochs → 150 checkpoints; likely sufficient | t* may be missed if transition is sharper than 2-epoch window |

### 1.6 Research Gap & Novelty

**Gap:** No systematic measurement protocol quantifies the spurious-vs-core temporal learning gap on standard benchmarks (Waterbirds, CelebA). JTT and DFR exploit training dynamics heuristically without mechanistic grounding.

**Novelty:**
- *Primary:* First standardized checkpoint linear probe battery producing delta(t) and gap area A as reproducible metrics for temporal feature learning dynamics
- *Secondary:* First mechanistic causal explanation of DFR success via transition epoch t*
- *Tertiary:* Early-stop intervention exploiting t* for annotation-free worst-group accuracy improvement

**Scope Reduction:** 71% of prior claims are BUILD_ON (established). Phase 2B targets only the 2 PROVE_NEW claims: (1) systematic measurement of delta(t), and (2) mechanistic DFR explanation via t*.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Temporal Gap Existence — Spurious Features Learned Before Core Features

**Type:** EXISTENCE
**Statement:** Under standard ERM training on Waterbirds, if checkpoint linear probing is applied every 2 epochs, then delta(t) = spurious_probe_acc(t) - core_probe_acc(t) > 0 for a statistically significant contiguous window covering ≥10% of training epochs, because SGD simplicity bias preferentially encodes lower-complexity (spurious) features before higher-complexity (core) features.

**Rationale:**
This is the foundational empirical claim: the temporal gap must demonstrably exist before any downstream mechanistic or intervention claims can be made. Establishing delta(t) > 0 with statistical significance across seeds and datasets provides the primary scientific contribution — a reproducible, standardized measurement protocol for feature learning dynamics in spurious correlation settings.

**Variables (from Phase 2A):**
- Independent: Training epoch (continuous, 0 to max_epochs, checkpointed every 2 epochs); probe label type (spurious vs. core)
- Dependent: delta(t) = spurious_probe_acc(t) - core_probe_acc(t) on held-out validation split
- Controlled: ResNet-50 (ImageNet pretrained), SGD (lr=1e-3, momentum=0.9, wd=1e-4), L2 logistic regression probe, ≥3 random seeds

**Verification Protocol:**
1. Train ResNet-50 ERM on Waterbirds for full schedule (~300 epochs); save checkpoint every 2 epochs (≥150 checkpoints total)
2. At each checkpoint, extract frozen backbone features for all samples in held-out validation split
3. Fit L2 logistic regression probe for spurious label (background) and separately for core label (bird species); record accuracies
4. Compute delta(t) = spurious_acc(t) - core_acc(t) at each checkpoint; run paired t-test across seeds at each timestep
5. Replicate full protocol on CelebA (hair color spurious / gender core); compare delta(t) profiles

**Success Criteria (PoC: Direction-based):**
- Primary: delta(t) > 0 for contiguous window ≥10% of training epochs, paired t-test p < 0.05 across ≥3 seeds
- Secondary: Gap area A = sum(max(delta(t), 0)) > 0 with 95% CI excluding zero; t* identified consistently (std < 10 epochs across seeds)
- Replication: Effect replicated on CelebA (same directional finding)

**Failure Response:**
- IF delta(t) ≤ 0 at all checkpoints across all seeds on both Waterbirds and CelebA → ABANDON: H0 supported; hypothesis collapses
- IF delta(t) > 0 on Waterbirds but not CelebA → PIVOT: Scope claim to Waterbirds-only; re-examine feature complexity assumption (A1) for CelebA

**Dependencies:** None (H-E1 is the root hypothesis)

**Source:** Phase 2A Section 1.1 (core_statement), Section 1.6 P1, Section 5 sh1_existence

---

#### H-M1: SGD Simplicity Bias Drives Differential Learning Speed

**Type:** MECHANISM
**Statement:** Under standard ERM training on Waterbirds, if the gradient structure of SGD is analyzed via Fourier decomposition and feature complexity proxies, then spurious features (background texture) will exhibit higher gradient signal magnitude and lower gradient variance in early training iterations than core features (bird species morphology), because SGD optimization preferentially follows low-frequency gradient components (Frequency Principle).

**Rationale:**
This hypothesis tests the first mechanistic step in the causal chain: establishing that SGD's optimization geometry produces differential learning speed between spurious and core features. This is a BUILD_ON-adjacent claim (Frequency Principle is established), but operationalization on Waterbirds/CelebA specifically is PROVE_NEW and required to ground H-M2–H-M4 in the experimental context.

**Variables:**
- Independent: Training epoch (early training window, first 20% of epochs)
- Dependent: Gradient norm ratio (spurious-feature-aligned gradient / core-feature-aligned gradient) at each epoch
- Controlled: ResNet-50, SGD optimizer, same dataset/split as H-E1

**Verification Protocol:**
1. Instrument ResNet-50 training to log per-batch gradient norms projected onto spurious and core label directions
2. Compute gradient magnitude ratio per epoch over first 20% of training
3. Compare spurious vs. core gradient magnitudes using Wilcoxon signed-rank test across epochs and seeds
4. Cross-validate: confirm delta(t) > 0 window (from H-E1) co-occurs with elevated spurious gradient dominance
5. Report gradient dominance coefficient as supplementary mechanistic evidence

**Success Criteria:**
- Primary: Spurious-feature gradient magnitude > core-feature gradient magnitude in early training epochs (p < 0.05)
- Secondary: Gradient dominance period temporally aligns with delta(t) > 0 window from H-E1

**Failure Response:**
- IF gradients show no significant difference → EXPLORE: Examine alternative complexity proxies (eigenspectrum, activation variance); mechanism step 1 may be more subtle than gradient magnitudes
- IF mechanism not confirmed → document as LIMITATION (H-E1 finding stands independently)

**Dependencies:** H-E1 (temporal gap must exist to motivate mechanistic investigation)

**Source:** Phase 2A Section 1.3 Step 1, causal mechanism evidence

---

#### H-M2: Spurious Features Have Lower Complexity Than Core Features in Waterbirds/CelebA

**Type:** MECHANISM
**Statement:** Under controlled complexity analysis of Waterbirds and CelebA image patches, if feature complexity is measured via spatial frequency content and intra-class variance, then spurious features (background texture, hair color) will score measurably lower on complexity metrics than core features (bird species morphology, facial structure), because these feature types differ systematically in the richness of visual information required for discrimination.

**Rationale:**
This hypothesis directly validates Assumption A1 — the key prerequisite for the entire causal chain. Without empirical confirmation that spurious features are actually simpler, the mechanism (SGD learns simpler features first) cannot explain the temporal gap. This is a dataset characterization step that transforms an assumption into a verified empirical fact.

**Variables:**
- Independent: Feature type (spurious vs. core), dataset (Waterbirds, CelebA)
- Dependent: Complexity metrics — (a) mean spatial frequency (FFT power spectrum), (b) intra-class variance of cropped feature patches, (c) linear separability (number of training samples needed for 90% probe accuracy)
- Controlled: Standardized image patch extraction, same resolution, same backbone (ResNet-50 layer-wise features)

**Verification Protocol:**
1. Extract image patches corresponding to spurious regions (background) and core regions (foreground objects) using segmentation masks from Waterbirds/CelebA metadata
2. Compute FFT power spectrum for each patch set; measure mean spatial frequency (lower = simpler)
3. Compute intra-class variance of ResNet-50 layer-4 features separately for spurious-aligned and core-aligned patches
4. Plot linear probe learning curves (accuracy vs. number of training samples) for spurious vs. core labels
5. Report complexity gap delta_complexity = complexity(core) - complexity(spurious) with 95% CI

**Success Criteria:**
- Primary: Spurious features have significantly lower complexity on ≥2 of 3 metrics (FFT, intra-class variance, probe learning curve)
- Secondary: Complexity gap delta_complexity > 0 with p < 0.05 on both Waterbirds and CelebA

**Failure Response:**
- IF spurious and core features show comparable complexity → CRITICAL: A1 violated; revisit why delta(t) > 0 was observed; explore alternative mechanism (e.g., label frequency imbalance, correlation strength)

**Dependencies:** H-M1 (confirms the gradient mechanism; complexity verification provides the structural explanation)

**Source:** Phase 2A Section 1.3 Step 2, Section 1.4 A1

---

#### H-M3: Measurable Temporal Gap Window with Identifiable Transition Epoch t*

**Type:** MECHANISM
**Statement:** Under standard ERM training on Waterbirds/CelebA, if delta(t) is measured at every checkpoint (2-epoch intervals), then a well-defined transition epoch t* — the first epoch where delta(t) < 0.02 for 3 consecutive checkpoints — is identifiable with low variance (std < 10 epochs) across ≥3 random seeds, because the temporal gap reflects a structural property of SGD optimization rather than a random training artifact.

**Rationale:**
H-E1 establishes that the temporal gap exists; H-M3 characterizes the gap with precision. The transition epoch t* is the operational linchpin of the mechanistic framework: it must be reliably identifiable to serve as a valid intervention point. This hypothesis transforms the qualitative finding "gap exists" into the quantitative claim "t* can be measured reproducibly."

**Variables:**
- Independent: Random seed (3+ seeds per dataset), dataset (Waterbirds, CelebA)
- Dependent: t* value per seed; inter-seed variance of t* (primary); gap area A = sum(max(delta(t), 0)) (secondary)
- Controlled: All hyperparameters fixed as in H-E1; checkpoint interval = 2 epochs

**Verification Protocol:**
1. Use delta(t) curves from H-E1 (reuse existing checkpoints — no new training required)
2. Identify t* per seed using operational definition: first epoch where delta(t) < 0.02 for 3 consecutive checkpoints
3. Compute mean ± std of t* across seeds for Waterbirds and CelebA
4. Compute gap area A for each seed; report mean and 95% CI
5. Test consistency: check whether t* occurs in same training phase (relative to total epochs) across datasets

**Success Criteria:**
- Primary: std(t*) < 10 epochs across seeds on both Waterbirds and CelebA
- Secondary: Gap area A > 0 with 95% CI excluding zero; t* is consistent relative phase (same ~% of total training)

**Failure Response:**
- IF std(t*) ≥ 20 epochs → PIVOT: Replace point-estimate t* with gap area A as primary metric; argue for interval-based intervention
- IF t* inconsistent across datasets → SCOPE: Limit t*-based claims to Waterbirds; use A as cross-dataset summary

**Dependencies:** H-E1 (requires established delta(t) curves); reuses H-E1 checkpoints

**Source:** Phase 2A Section 1.3 Step 3, Section 1.6 P1, Section 2 measurement_plan

---

#### H-M4: DFR Success Mechanistically Explained by Epochs Trained Past t*

**Type:** MECHANISM
**Statement:** Under controlled truncated ERM training on Waterbirds, if DFR last-layer reweighting is applied to ResNet-50 backbones trained to 5 different epoch checkpoints (t*-20, t*, t*+20, t*+50, full training), then DFR worst-group accuracy (WGA) improvement over ERM baseline will be positively correlated with (training_epochs - t*), with Pearson r > 0.7 (p < 0.05), because the backbone encodes sufficient core feature information only after t*, enabling effective last-layer reweighting.

**Rationale:**
This is the strongest novel scientific contribution: a mechanistic causal explanation for why DFR works. DFR is widely used but its success was previously unexplained (DFR paper: backbone "already encodes core features" — but when and why?). Establishing a quantitative correlation between backbone training depth relative to t* and DFR's efficacy provides both mechanistic insight and practical guidance (don't apply DFR before t*).

**Variables:**
- Independent: Backbone training epochs relative to t* (categorical: t*-20, t*, t*+20, t*+50, full)
- Dependent: DFR WGA improvement = DFR WGA - ERM WGA baseline; Pearson r between improvement and (epochs - t*)
- Controlled: Fixed DFR hyperparameters (L2 logistic regression on held-out split), identical test evaluation protocol, same random seed for DFR training step

**Verification Protocol:**
1. Using t* identified in H-M3, train 5 ERM backbone variants truncated to: t*-20, t*, t*+20, t*+50, full training epochs
2. Apply DFR identically to each backbone: fit logistic regression on class-balanced held-out validation split; evaluate WGA on full test set
3. Compute DFR WGA improvement = DFR WGA(epoch) - ERM WGA(epoch) for each checkpoint
4. Compute Pearson correlation r between improvement values and (epoch - t*) across the 5 conditions
5. Statistical test: two-tailed t-test on Pearson r; check monotonicity of WGA improvement curve

**Success Criteria (PoC: Direction-based):**
- Primary: Pearson r > 0.7 between DFR WGA improvement and epochs trained past t*, p < 0.05
- Secondary: DFR WGA improvement monotonically increases with epochs past t*; DFR applied before t* shows < 50% of maximum WGA improvement

**Failure Response:**
- IF r < 0.5 → EXPLORE: Examine whether WGA improvement is driven by total training epochs (not relative to t*); consider that DFR success may be robust to training duration (limits claim but doesn't invalidate H-E1/H-M1-3)
- IF no monotonic trend → SCOPE: Report as null finding for this mechanistic link; primary contribution (measurement protocol) remains intact

**Dependencies:** H-M3 (requires t* to define the 5 truncation points); reuses H-E1 backbone training infrastructure

**Source:** Phase 2A Section 1.3 Step 4, Section 1.6 P2, Section 5 sh2_mechanism

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HYPOTHESIS INVENTORY COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 5 hypotheses
| Type      | Count | IDs                    |
|-----------|-------|------------------------|
| Existence | 1     | H-E1                   |
| Mechanism | 4     | H-M1, H-M2, H-M3, H-M4|
| Condition | 0     | (skipped)              |
Each specification: ~45 lines with verification protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Risk Analysis

### 3.1 Key Assumptions → Risk Mapping

| ID | Assumption | Evidence | Consequence if Violated |
|----|------------|----------|-------------------------|
| A1 | Spurious features measurably simpler than core | Simplicity Bias literature; background texture/hair color widely cited as simpler | delta(t) ≈ 0; entire hypothesis collapses |
| A2 | Linear probing faithfully reflects feature encoding | Standard in self-supervised evaluation | delta(t) doesn't measure what we claim |
| A3 | Temporal gap consistent across seeds (not artifact) | Simplicity bias is structural, not init-dependent | t* unreliable; high variance makes intervention impractical |
| A4 | DFR success primarily from backbone encoding core features | DFR paper states ERM backbone "already encodes core features" | Mechanistic explanation fails even if delta(t) exists |
| A5 | 2-epoch checkpoint interval sufficient for t* identification | ~150 checkpoints for 300-epoch Waterbirds training | t* missed if transition sharper than 2-epoch window |

### 3.2 Risk Identification

**Risk R1: Null Delta (Complexity Parity)**
- Source: A1 violated
- Description: Spurious and core features have comparable complexity in Waterbirds/CelebA; SGD simplicity bias does not produce differential learning speed
- Severity: **Critical** (invalidates entire hypothesis)
- Likelihood: Low (literature strongly suggests complexity differential exists)
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3, H-M4 (all)

**Risk R2: Probe Validity Failure**
- Source: A2 violated
- Description: Linear probe accuracy at frozen checkpoints reflects training artifact (e.g., probe overfits to class-correlated features regardless of backbone encoding quality)
- Severity: **High** (compromises measurement validity)
- Likelihood: Low (held-out split mitigates this; well-established methodology)
- Affected Hypotheses: H-E1, H-M3

**Risk R3: Seed Variance / t* Unreliability**
- Source: A3 violated
- Description: t* varies by >20 epochs across seeds; temporal gap is a stochastic rather than structural phenomenon
- Severity: **High** (makes t*-based intervention unreliable)
- Likelihood: Medium (initialization can affect early training dynamics)
- Affected Hypotheses: H-M3, H-M4

**Risk R4: DFR Mechanism Decoupling**
- Source: A4 violated
- Description: DFR WGA improvement is driven by regularization in last-layer reweighting, not backbone encoding quality; correlation with epochs past t* is spurious
- Severity: **Medium** (mechanistic claim fails; measurement contribution survives)
- Likelihood: Medium (DFR paper's "already encodes core features" claim is descriptive, not mechanistically verified)
- Affected Hypotheses: H-M4

**Risk R5: Temporal Resolution Insufficiency**
- Source: A5 violated
- Description: t* transition is sharp and occurs within a 2-epoch window, making t* identification imprecise
- Severity: **Low** (easily mitigated by reducing checkpoint interval)
- Likelihood: Low (300-epoch training makes sharp 2-epoch transitions unlikely)
- Affected Hypotheses: H-M3

### 3.3 Risk-Hypothesis Mapping

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Risk | Source | Affected Hypotheses      | Severity |
|------|--------|--------------------------|----------|
| R1   | A1     | H-E1, H-M1, H-M2, H-M3, H-M4 | Critical |
| R2   | A2     | H-E1, H-M3               | High     |
| R3   | A3     | H-M3, H-M4               | High     |
| R4   | A4     | H-M4                     | Medium   |
| R5   | A5     | H-M3                     | Low      |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.4 Mitigation Strategies

**Risk R1 — Null Delta: Complexity Parity**

*Source Assumption:* A1 — Spurious features measurably simpler than core

*Description:* If background texture and hair color are not measurably simpler than bird species morphology and facial structure, the fundamental premise fails.

*Affected:* All 5 hypotheses

*Severity:* Critical

*Mitigation Strategy:*
1. **Prevention:** Run H-M2 (complexity characterization) early — ideally before full H-E1 training run — to verify A1 empirically before investing full compute budget
2. **Detection:** Monitor delta(t) at early checkpoints (epoch 10, 20, 30); if delta consistently ≤ 0 by epoch 30, abort full run
3. **Response:**
   - PIVOT: Examine whether different complexity proxies (gradient alignment, eigenspectrum) reveal differential learning speed
   - SCOPE: If gap exists for Waterbirds but not CelebA, scope contribution to Waterbirds-specific finding
   - ABANDON: If delta ≤ 0 on both datasets across all seeds, pivot research to explaining why standard spurious correlation datasets fail the complexity differential assumption

*Early Warning:* delta(t) ≤ 0 at epoch 20-30 across ≥2 of 3 seeds in early monitoring run

---

**Risk R2 — Probe Validity Failure**

*Source Assumption:* A2 — Linear probing reflects feature encoding

*Description:* Probe accuracy at frozen checkpoints may be confounded by feature geometry (probe fits to training-correlated artifacts, not backbone-encoded features).

*Affected:* H-E1, H-M3

*Severity:* High

*Mitigation Strategy:*
1. **Prevention:** Use strictly held-out validation split for all probing (not training split); verify probe is properly regularized (L2 logistic regression, not overfit)
2. **Detection:** Run sanity check — probe accuracy at epoch 0 (random backbone) should be near chance level (~50%); if not, probe is overfitting to dataset artifacts
3. **Response:**
   - PIVOT: Replace linear probe with alternative representation quality metrics (CKA similarity, nearest-neighbor accuracy); check consistency with delta(t) curves

*Early Warning:* Epoch-0 probe accuracy substantially above chance (> 60%) indicating probe artifact

---

**Risk R3 — Seed Variance / t* Unreliability**

*Source Assumption:* A3 — Temporal gap consistent across seeds

*Description:* Random initialization affects early training dynamics; t* may vary significantly across seeds.

*Affected:* H-M3, H-M4

*Severity:* High

*Mitigation Strategy:*
1. **Prevention:** Use minimum 5 seeds (above protocol minimum of 3) for t* variance quantification
2. **Detection:** After 3 seeds complete, compute t* variance; if std > 15 epochs, expand to 5+ seeds before proceeding to H-M4
3. **Response:**
   - PIVOT: Replace point-estimate t* with gap area A as primary metric (more robust to initialization variance); argue for interval-based intervention zone [t*_mean - std, t*_mean + std]
   - SCOPE: Report t* as a per-run quantity rather than a universal dataset property

*Early Warning:* std(t*) > 15 epochs after 3 seeds

---

**Risk R4 — DFR Mechanism Decoupling**

*Source Assumption:* A4 — DFR success from backbone encoding

*Description:* DFR's WGA gain may be driven by regularization effects in last-layer reweighting rather than backbone feature quality at t*.

*Affected:* H-M4

*Severity:* Medium

*Mitigation Strategy:*
1. **Prevention:** Include ablation: apply DFR reweighting procedure to random backbone (epoch 0) to isolate baseline DFR gain from regularization alone
2. **Detection:** If DFR WGA improvement at epoch t*-20 is comparable to improvement at t*, mechanism is decoupled from backbone quality
3. **Response:**
   - EXPLORE: Test whether WGA improvement follows total training epochs (not relative to t*); partial mechanism claim possible
   - The measurement contribution (H-E1 through H-M3) is not affected

*Early Warning:* DFR applied at t*-20 achieves > 80% of maximum DFR WGA improvement

---

**Risk R5 — Temporal Resolution Insufficiency**

*Source Assumption:* A5 — 2-epoch checkpoint interval sufficient

*Description:* t* transition may occur within a 2-epoch window, making the operational definition imprecise.

*Affected:* H-M3

*Severity:* Low

*Mitigation Strategy:*
1. **Prevention:** Standard 2-epoch interval is sufficient for 300-epoch training (< 1% resolution error)
2. **Detection:** Examine delta(t) rate-of-change near t*; if |d(delta)/dt| > 0.05/epoch near t*, reduce interval
3. **Response:** Run a 1-epoch-interval refinement run in the ±10 epoch window around t* to pinpoint transition

*Early Warning:* Sharp delta(t) drop > 0.10 in a single 2-epoch interval near t*

### 3.5 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| ID | Risk              | Source | Severity | Affected        | Key Mitigation        |
|----|-------------------|--------|----------|-----------------|-----------------------|
| R1 | Null Delta        | A1     | Critical | All 5 hyps      | Run H-M2 first; abort if no early signal |
| R2 | Probe Validity    | A2     | High     | H-E1, H-M3      | Held-out split; epoch-0 sanity check |
| R3 | t* Seed Variance  | A3     | High     | H-M3, H-M4      | ≥5 seeds; use gap area A as fallback |
| R4 | DFR Decoupling    | A4     | Medium   | H-M4            | Random-backbone DFR ablation |
| R5 | Resolution Gap    | A5     | Low      | H-M3            | 1-epoch refinement run near t* |

Critical Risks: 1 (R1)
High Risks: 2 (R2, R3)
Medium Risks: 1 (R4)
Low Risks: 1 (R5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| ERM: ignores spurious features entirely | Worst-group accuracy gap may be partly architecture-driven (not purely feature learning order) | Report WGA curves per group during training to isolate spurious vs. core group dynamics |
| JTT: heuristic misclassification proxy with no mechanistic grounding | If t* and JTT's "error-prone samples" don't align temporally, JTT mechanism is independent of temporal gap | Compare JTT upweighting onset epoch with t* to test alignment |
| DFR: effective but unexplained; success may be due to class-balanced reweighting regularization | R4: DFR mechanism decoupling | Random-backbone ablation (see R4 mitigation) |
| GroupDRO: upper bound requires group labels — cannot be replicated annotation-free | Not directly applicable to this study; serves only as upper-bound reference | Use only for WGA ceiling reporting |

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK ANALYSIS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risks Identified: 5
  - Critical: 1 (R1)
  - High: 2 (R2, R3)
  - Medium: 1 (R4)
  - Low: 1 (R5)
All risks mapped to hypotheses with mitigation strategies.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph (DAG) and Timeline

### 5.1 Dependency Analysis

```
Hypothesis → Prerequisites
H-E1  → []
H-M1  → [H-E1]
H-M2  → [H-M1]
H-M3  → [H-M2] (reuses H-E1 checkpoints)
H-M4  → [H-M3] (requires t* from H-M3)
```

### 5.2 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (Existence — no dependencies)
    Verify: delta(t) > 0 on Waterbirds + CelebA
         │
         ▼  [Gate 1: MUST PASS]
[Level 1 - Mechanism Step 1]
    H-M1 ← H-E1
    Verify: SGD gradient structure drives differential speed
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2 ← H-M1
    Verify: Spurious features empirically simpler than core
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3 ← H-M2
    Verify: t* identifiable with low variance (std < 10 epochs)
         │
         ▼  [Gate 2: H-M1+H-M3 must pass for H-M4 to proceed]
[Level 4 - Mechanism Step 4]
    H-M4 ← H-M3
    Verify: DFR WGA improvement correlates with epochs past t*
         │
         ▼

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All Sequential: No parallelization (incremental mode)
═══════════════════════════════════════════════════════════
```

### 5.3 Verification Phases with Gate Conditions

**Phase 1 — Foundation (H-E1)**

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Checkpoint linear probe battery; delta(t) > 0 contiguous window; p < 0.05 across ≥3 seeds; replicated on CelebA | **MUST PASS** |

→ **Gate 1:** If H-E1 fails → STOP entire verification; H0 supported; reassess hypothesis from Phase 2A.

**Phase 2 — Core Mechanisms (H-M1 through H-M4)**

| Hypothesis | Dependencies | Gate | Failure Consequence |
|------------|--------------|------|---------------------|
| H-M1 | H-E1 | MUST_WORK | Document as limitation; mechanism less certain but measurement stands |
| H-M2 | H-M1 | SHOULD_WORK | Re-examine A1; scope complexity claim |
| H-M3 | H-M2 | MUST_WORK (for H-M4) | Pivot to gap area A; interval-based intervention |
| H-M4 | H-M3 | SHOULD_WORK | Mechanistic DFR explanation fails; measurement contribution intact |

→ **Gate 2:** H-M1 and H-M3 must pass for H-M4 to be executed. H-M4 failure does not invalidate the primary measurement contribution.

### 5.4 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Level | Hypothesis | Prerequisites | Gate Type   |
|-------|-----------|---------------|-------------|
| 0     | H-E1      | None          | MUST_WORK   |
| 1     | H-M1      | H-E1          | MUST_WORK   |
| 2     | H-M2      | H-M1          | SHOULD_WORK |
| 3     | H-M3      | H-M2          | MUST_WORK   |
| 4     | H-M4      | H-M3          | SHOULD_WORK |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │ W7
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │
  [Gate 1]        │         │ ◆       │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │
  H-M2            │         │         │ ████    │         │
  H-M3            │         │         │         │ ████    │
  [Gate 2]        │         │         │         │         │ ◆
  H-M4            │         │         │         │         │ ████
──────────────────┼─────────┼─────────┼─────────┼─────────┼──────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4) = 7 weeks
Note: H-M3 reuses H-E1 checkpoints — no new training cost
═══════════════════════════════════════════════════════════════════
```

### 5.6 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)
Slack Available: 0 weeks (fully sequential)

GPU Hours Estimate:
  H-E1: ~10 GPU-hours (Waterbirds) + ~8 GPU-hours (CelebA) + probe fitting
  H-M1: ~2 GPU-hours (gradient logging during H-E1 training, low overhead)
  H-M2: ~1 GPU-hour (patch extraction + complexity analysis, no new training)
  H-M3: 0 additional GPU-hours (reuses H-E1 checkpoints)
  H-M4: ~10 GPU-hours (5 truncated training runs × ~2 GPU-hours each)
  Total: ~31 GPU-hours (~3-4 days on single GPU)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
  - Condition: 0 (skipped)

Verification Phases: 2
  1. Foundation (H-E1): 2 weeks
  2. Mechanisms (H-M1 to H-M4): 5 weeks

Total Duration: 7 weeks
Critical Path: 7 weeks
Execution Mode: Sequential chain
Compute Budget: ~31 GPU-hours total
Datasets: Waterbirds (primary), CelebA (replication)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.8 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
        Train ResNet-50 ERM + checkpoint every 2 epochs + linear probe battery
Step 2: Evaluate Gate 1 → If PASS proceed; if FAIL STOP
Step 3: Execute H-M1 (Gradient mechanism) — Week 3-4
        Gradient logging run (reuse H-E1 infrastructure)
Step 4: Execute H-M2 (Feature complexity) — Week 5
        Patch extraction + complexity analysis (no new training)
Step 5: Execute H-M3 (t* identification) — Week 6
        Analyze H-E1 delta(t) curves for t* + variance across seeds
Step 6: Evaluate Gate 2 → H-M1 + H-M3 must pass for H-M4
Step 7: Execute H-M4 (DFR mechanistic correlation) — Week 7
        5 truncated ERM backbones + DFR application + Pearson r
Final:  Verification complete → Report findings
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core Claim: SGD simplicity bias produces a measurable, reproducible temporal gap
delta(t) in spurious correlation datasets, with a well-defined transition epoch t*
that mechanistically explains the success of DFR and JTT.

Supporting Evidence:
1. Frequency Principle [Xu et al. 2019] + Simplicity Bias [Shah et al. 2020]:
   established theoretical basis for differential feature learning speed
2. Mangalam & Girshick 2021: shortcuts emerge early in neural network training
3. DFR paper: ERM backbone "already encodes core features" — our t* formalizes when
4. JTT/DFR empirical success (86-88% WGA) implies backbone learns core features eventually

Strengths:
- Strong theoretical grounding in established simplicity bias literature (BUILD_ON)
- Clear causal chain: 4 steps from SGD bias → differential learning → gap → DFR success
- Testable with existing code (GroupDRO codebase), existing benchmarks, existing hardware
- Three-tier hypothesis structure: measurement + mechanism + intervention = robust to partial failure

Expected Outcomes:
- Primary (P1): delta(t) > 0 for ≥10% of training epochs, p < 0.05, on Waterbirds + CelebA
- Secondary (P2): Pearson r > 0.7 between DFR WGA improvement and epochs past t*
- Tertiary (P3): Early-stop LLR WGA within 3pp of DFR at 50% compute cost
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Null Hypothesis (H0): There is no significant temporal ordering in spurious vs. core
feature learning under standard ERM training on Waterbirds/CelebA. delta(t) <= 0 at
all training checkpoints, and DFR WGA improvement is uncorrelated with epochs past t*.

Counter-Arguments:
1. Feature complexity may be confounded by dataset construction: background images
   in Waterbirds are scene photographs — potentially as complex as bird morphology
2. Linear probe accuracy may reflect label frequency artifacts rather than feature
   encoding: spurious labels are more balanced in Waterbirds training split
3. DFR success may be entirely attributable to class-balanced reweighting in the
   last layer, independent of what epoch the backbone was trained to

Potential Failure Points:
- R1: delta(t) ≈ 0 throughout training (complexity parity in practice)
- R3: t* highly variable across seeds (std > 20 epochs) — no reliable intervention point
- R4: DFR mechanism decoupled from t* — gain is due to regularization, not backbone timing

Conditions Under Which H0 Would Be Supported:
- delta(t) statistically indistinguishable from zero at all checkpoints on both datasets
- DFR WGA improvement flat across the 5 truncated backbone checkpoints (no correlation)
- Complexity analysis (H-M2) reveals spurious and core features have comparable metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Balanced Assessment:
The hypothesis H-TemporalGap-v1 presents a theoretically well-grounded, operationally
specific claim about temporal feature learning dynamics. The antithesis raises legitimate
concerns about feature complexity parity and DFR mechanism decoupling that cannot be
dismissed without empirical measurement.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Empirically tests whether the gap exists before
   committing to mechanistic claims — the measurement speaks independently of theory
2. Complexity characterization (H-M2): Converts Assumption A1 from axiom to tested fact;
   resolves the antithesis concern about complexity parity
3. Gate conditions: Allow early detection of H0 support (Gate 1 after H-E1 if gap absent)
4. DFR ablation in H-M4: Random-backbone control isolates regularization effect from
   backbone encoding quality, directly addressing R4/counter-argument 3

Conditions for Thesis Support:
- H-E1: delta(t) > 0 for ≥10% of epochs, p < 0.05, replicated on CelebA
- H-M3: std(t*) < 10 epochs across seeds
- H-M4: Pearson r > 0.7 for DFR WGA correlation (optional but strengthens thesis)

Conditions for Antithesis Support:
- H-E1 fails: delta(t) ≤ 0 across all seeds/datasets (H0 fully supported)
- H-M2 fails: complexity parity confirmed (undermines mechanistic foundation)
- H-M4: No correlation between DFR WGA and epochs past t* (partial H0 support for P2)

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1-4 all pass → Thesis validated, strongest contribution
2. Partial Support (likely): H-E1 + H-M3 pass, H-M4 weak → Measurement framework
   stands; DFR mechanistic explanation requires further investigation
3. Measurement Only: H-E1 passes but H-M1-4 weak → Novel measurement tool with
   theoretical mechanism unconfirmed; still publishable as empirical contribution
4. No Support: H-E1 fails → Pivot to explaining why standard benchmarks lack
   temporal gap despite theoretical prediction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Aspect        | Thesis Position              | Antithesis Challenge             | Resolution         |
|---------------|------------------------------|----------------------------------|--------------------|
| Existence     | delta(t) > 0 window          | Complexity parity → delta ≈ 0    | H-E1 direct test   |
| Mechanism     | SGD bias → differential speed | Alternative mechanisms possible   | H-M1 + H-M2 tests  |
| Reliability   | t* consistent across seeds   | High seed variance → unreliable  | H-M3 seed analysis |
| DFR Link      | WGA corr with epochs past t* | DFR gain from regularization     | H-M4 + ablation    |
| Performance   | Early-stop LLR ≈ DFR WGA     | Early stopping may be harmful    | Phase 5 (deferred) |

Overall Robustness Score: HIGH
- Primary contribution (measurement framework) is self-contained and independently publishable
- Three-tier structure makes full result robust to partial mechanism failure
- All experiments use public code, public benchmarks — reproducibility high

Confidence in Verification Plan: 0.78
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-TemporalGap-v1 — SGD simplicity bias produces a measurable temporal gap delta(t) in spurious correlation datasets; transition epoch t* explains DFR/JTT success.
- ID: H-TemporalGap-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (71% scope reduction from Phase 2A established facts)
- Sub-Hypotheses: 5 total — H-E1 (Existence) + H-M1/M2/M3/M4 (Mechanism chain)
- Phases: 2 phases over 7 weeks; ~31 GPU-hours on single GPU
- Critical Gates: 2 decision points (Gate 1 after H-E1; Gate 2 before H-M4)

**Risk Assessment:** Medium overall
- Primary concern R1: Null delta if complexity parity — mitigated by running H-M2 early
- Secondary concern R3: Seed variance in t* — mitigated by gap area A as fallback metric

**Immediate Action:** Run H-M2 (complexity characterization, ~1 GPU-hour) FIRST as fast A1 validation before committing to full H-E1 training run; then proceed to H-E1.

### 7.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: Checkpoint linear probe battery; delta(t) measurement on Waterbirds + CelebA
- Gate 1: MUST PASS → if fail, stop

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: SGD gradient structure verification (gradient logging, Week 3-4)
- H-M2: Feature complexity characterization — Assumption A1 validation (Week 5)
- H-M3: t* identification + seed variance analysis (Week 6, reuses H-E1 checkpoints)
- H-M4: DFR mechanistic correlation — 5 truncated backbones (Week 7)
- Gate 2: H-M1 + H-M3 must pass for H-M4

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation — after H-E1):**
   - FAIL → STOP; H0 supported; return to Phase 2A for hypothesis revision
   - PASS → Proceed to Phase 2 mechanisms

2. **Gate 2 (Mechanism — before H-M4):**
   - H-M1 CRITICAL FAIL → Execute EXPLORE response; document limitation
   - H-M3 std(t*) ≥ 20 epochs → PIVOT to gap area A; proceed with H-M4 using interval zone
   - H-M4 FAIL → Document: measurement contribution intact; DFR mechanistic explanation limited

### 7.4 Open Questions

- What is the empirical magnitude of delta_max on Waterbirds and CelebA? (Primary unknown — must be measured)
- Is t* consistent across seeds (target std < 10 epochs) or highly variable?
- Can t* be approximated by a label-free proxy (validation loss variance, gradient norm)? — Secondary contribution
- Does the temporal gap replicate on MultiNLI/CivilComments with BERT? — Future work if resources permit

### 7.5 Recommendations

1. **Immediate Actions:**
   - Run H-M2 FIRST (complexity characterization, ~1 GPU-hour) as fast A1 validation
   - Then execute H-E1 full checkpoint protocol
   - Use minimum 5 seeds for robust t* variance estimation (above protocol minimum)

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path; reserve 1-week buffer for unexpected results
   - Total compute: ~31 GPU-hours — fits in standard single-GPU pipeline run
   - All datasets and code publicly available; no new benchmarks or annotations required

3. **Failure Management:**
   - Document all gate outcomes explicitly in verification_state.yaml
   - Execute PIVOT strategies immediately on gate failure; do not continue failed chains
   - Report gap area A alongside t* in all publications (more robust metric)

---

## 8. Appendices

### A. Phase 2A Reference
- **Source file:** `03_refinement.yaml` (ID: H-TemporalGap-v1)
- **Generated:** 2026-05-04, Phase 2A-Dialogue v10.0.0
- **Convergence:** 8 discussion rounds, all 6 criteria met
- **Scope reduction:** 71% (5 BUILD_ON + 2 PROVE_NEW claims)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 3 (ClearThought scientific method)
  - Call 1: H-E1 Verification (hypothesis → experiment → analysis stages)
  - Call 2a: H-M1/M2 Mechanism chain Part 1
  - Call 2b: H-M3/M4 Mechanism chain Part 2
- **Scope reduction applied:** BUILD_ON claims excluded from hypothesis generation

### C. Experimental Scale Notes
- Waterbirds training split: 4,795 samples (standard full split)
- Waterbirds validation split: 1,199 samples (used for all probing)
- Waterbirds test split: 5,794 samples (used for WGA evaluation)
- CelebA: 162,770 train / 19,867 val / 19,962 test (standard GroupDRO splits)
- Minimum samples for probe training: all validation samples (not subsampled)
- Random seeds: minimum 3, recommended 5 for t* variance analysis

---

*Generated by YouRA Phase 2B Planning (v7.7.0) | 2026-05-04*

---

<!-- FRONTMATTER TRACKING
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis",
                 "step-03-hypothesis-generation", "step-04-hypothesis-inventory",
                 "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning",
                 "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-05-04T00:00:00"
-->

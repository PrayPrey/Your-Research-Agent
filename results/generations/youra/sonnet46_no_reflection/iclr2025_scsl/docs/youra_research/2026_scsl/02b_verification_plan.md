---
hypothesis_id: H-GSB-v1
hypothesis_title: "Gradient SNR Balancing (GSB): Annotation-Free Early-Phase Intervention for Cross-Paradigm Shortcut Robustification"
date: "2026-05-20"
confidence_level: 0.78
total_hypothesis_count: 6
research_mode: incremental
scope_reduction_percentage: 50
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
completedAt: "2026-05-20T01:00:00"
---

# Verification Plan: Gradient SNR Balancing (GSB): Annotation-Free Early-Phase Intervention for Cross-Paradigm Shortcut Robustification

**Date:** 2026-05-20
**Hypothesis ID:** H-GSB-v1
**Confidence:** 0.78
**Total Hypotheses:** 6

---

## Section 0: Established Facts & Scope Reduction

### 0.1 BUILD_ON Claims (Do NOT Re-Verify)

| Claim | Evidence |
|-------|----------|
| SGD-based optimization exhibits simplicity bias, preferentially learning high-SNR spurious features | Shah et al. (2020) Pitfalls of Simplicity Bias; Geirhos et al. (2020) Shortcut Learning |
| Invariant features are richly encoded in pretrained backbone representations even when spurious shortcuts dominate the linear head | Kirichenko et al. (2022) DFR achieves 97% worst-group on Waterbirds by retraining only last layer |
| SSL (SimCLR-style) training acquires spurious correlations through augmentation-invariant shortcuts | Robinson et al. (2023) Spurious Correlations in Self-Supervised Learning |

### 0.2 PROVE_NEW Claims (Require Verification)

| Claim | Verification Target |
|-------|---------------------|
| Annotation-free spurious feature detection without group labels at scale | H-E1: clustering validity (AMI≥0.5, purity≥75%) |
| Early gradient SNR imbalance along cluster-discovered directions causally drives cross-paradigm shortcut crystallization | H-M1–H-M4: causal chain verification |
| GSB during early training (epochs 1-10) improves worst-group accuracy across supervised, SSL, and contrastive paradigms | H-M4: intervention effect + H-C1: boundary condition |

**Scope Reduction:** 50% — 3 BUILD_ON claims cited as background, only 3 PROVE_NEW claims require new experiments.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under spurious-correlation settings with pretrained backbone initialization (supervised ERM, SimCLR-style SSL, and contrastive learning on Waterbirds, CelebA, ColoredMNIST), if gradient signal-to-noise ratio (SNR) along annotation-free cluster-discovered feature directions is equalized during early training (epochs 1–10) via Gradient SNR Balancing (GSB), then worst-group accuracy improves ≥5 percentage points over ERM baseline without average accuracy degradation, because early gradient SNR imbalance along spurious feature directions causally drives representational suppression of invariant features during the shortcut consolidation critical period.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in worst-group accuracy between GSB-trained models and ERM baseline when controlling for matched-magnitude random subspace gradient balancing, and early gradient SNR imbalance does not predict final worst-group accuracy degradation with Spearman ρ > 0.5 across learning paradigms.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), CelebA, ColoredMNIST (standard) | All three have known spurious attributes with ground-truth group labels (evaluation only); standard benchmarks for worst-group accuracy measurement |
| **Model** | ResNet-50 (primary), ViT-B (secondary) | Matches GroupDRO/DFR/JTT baselines; enables architecture generalization check |

**Dataset Details:**
- Source: Waterbirds: Sagawa et al. 2020 GroupDRO; CelebA: Liu et al. 2015; ColoredMNIST: Arjovsky et al. 2019 IRM
- Path: Standard downloads from GroupDRO repo (kohpangwei/group_DRO)

**Model Details:**
- Type: CNN (ResNet-50) / Vision Transformer (ViT-B)
- Source: ImageNet-pretrained from torchvision; ViT-B from timm

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| GroupDRO [Sagawa et al. 2020] | ~90% worst-group | Waterbirds, CelebA, MultiNLI, CivilComments | Requires group annotations; supervised-only; does not explain mechanism |
| JTT [Liu et al. 2021] | ~82-86% worst-group | Waterbirds, CelebA, MultiNLI | Supervised-only; loss-based proxy is paradigm-specific; no mechanistic account |
| DFR [Kirichenko et al. 2022] | ~92-97% worst-group | Waterbirds, CelebA | Post-hoc repair; requires small labeled val set; supervised-only; no cross-paradigm |
| LFR [Ghaznavi et al. 2023] | Outperforms DFR at high spuriosity | Waterbirds, CelebA | Supervised-only; loss-based resampling; no mechanistic or cross-paradigm claim |
| SimCLR + linear probe (ERM) | Baseline SSL | Waterbirds | Standard SSL baseline for cross-paradigm prediction test |

**Best Baseline:** DFR ~97% worst-group on Waterbirds (with labeled val set); JTT ~86% annotation-free

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | If Violated |
|----|------------|---------------------|-------------|
| A1 | Pretrained backbone initialization required for epoch-5 cluster reliability | ImageNet-pretrained ResNets encode color/texture/background strongly; all baseline papers use pretrained init | GSB inapplicable to from-scratch training; limited to transfer learning settings. Addressed by 2×2 factorial. |
| A2 | Spurious feature directions approximately low-dimensional (top-1 ≥60% inter-cluster variance, top-5 ≥85%) | GEORGE clustering analysis; Fisher LDA typically yields compact subspaces | 1D SNR projection loses interpretability; must reformulate as distributed anisotropy. Addressed by pre-registered eigenspectrum test. |
| A3 | Invariant features present but suppressed — GSB rescues signal, not noise | DFR achieves 97% worst-group by retraining only last layer (invariant features richly encoded) | GSB amplifies noise; worst-group accuracy would not improve. Addressed by absent-signal control (ColoredMNIST). |
| A4 | Same gradient SNR mechanism governs shortcut acquisition in supervised ERM and SimCLR-SSL | Both paradigms use gradient-based optimization; SSL instance discrimination gradients project onto feature directions analogously | Cross-paradigm unification claim collapses; contribution reduces to supervised-only. Addressed by augmentation modulation test. |
| A5 | Early training phase (epochs 1-10) is the critical window | Simplicity bias literature: shortcuts learned early [Shah et al. 2020]; DFR post-hoc repair success implies damage done by training end | Timing ablation shows no difference; mechanism reduces to generic regularization. Directly tested by timing ablation. |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First mechanistic, annotation-free, cross-paradigm account of early-phase shortcut crystallization with a direction-specific intervention.

**Key Innovation:** GSB combines: (1) annotation-free cluster direction discovery, (2) early-phase causal intervention during representation formation, (3) cross-paradigm validation (supervised + SSL + contrastive). The spectral entropy "critical period" measurement is a new diagnostic. The adversarial-orthogonal control is a novel methodological contribution.

**Differentiators from Prior Work:**
- vs. GroupDRO: No annotations, gradient-geometry-level (not loss-level), preventive not post-hoc, cross-paradigm
- vs. DFR: Preventive (epochs 1-10) not post-hoc (last layer retrain), no labeled val set, extends to SSL
- vs. JTT: Gradient geometry (paradigm-agnostic) not loss-based proxy, mechanistic account
- vs. Robinson et al. 2023: Provides annotation-free fix, not just diagnosis of SSL shortcuts

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | Annotation-free k-means clustering on epoch-5 embeddings achieves AMI≥0.5, purity≥75% on Waterbirds/CelebA | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Gradient SNR along spurious directions exceeds invariant directions by ratio>1.5 during epochs 1-10 (ERM & SSL) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Early SNR ratio at epoch 5 predicts final worst-group degradation with Spearman ρ>0.7 cross-paradigm without retuning | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Shortcut consolidation critical period: anti-correlated variance trajectories (spurious↑, invariant↓) and spectral entropy decrease during epochs 1-10 | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M4 | MECHANISM | Early-only GSB (epochs 1-10) improves worst-group ≥5pp over ERM and ≥5pp over random control, direction-specific (adversarial-orthogonal fails) | MUST_WORK | H-E1, H-M1 | NOT_STARTED |
| H-C1 | CONDITION | GSB mechanism requires pretrained backbone — random-init training shows attenuated or absent improvement (2×2 factorial interaction) | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Annotation-Free Spurious Direction Discovery via Penultimate-Layer Clustering**

**Type:** EXISTENCE
**Statement:** Under spurious-correlation settings (Waterbirds, CelebA) with pretrained ResNet-50 initialization, k-means clustering (k=2) on penultimate-layer embeddings at epoch 5 of ERM training recovers spurious feature axes with AMI≥0.5 and worst-cluster purity≥75% across ≥5 random seeds, because pretrained backbones encode spurious features as dominant, separable directions in embedding space by epoch 5.

**Rationale:** This is the foundational hypothesis: if annotation-free cluster directions do not validly proxy spurious feature axes (AMI<0.5 or purity<75%), the entire GSB mechanism collapses since SNR measurement depends on accurate direction discovery. DFR's success (invariant features linearly separable in pretrained embeddings) provides strong prior evidence that epoch-5 embeddings carry discriminative spurious structure.

**Variables (from Phase 2A):**
- Independent: Backbone initialization (pretrained vs. random — ColoredMNIST control)
- Dependent: AMI between k-means clusters and ground-truth groups (threshold ≥0.5); worst-cluster purity (threshold ≥75%)
- Controlled: k=2, epoch 5, Waterbirds/CelebA standard splits, ≥5 seeds

**Verification Protocol:**
1. Train ResNet-50 (ImageNet-pretrained) on Waterbirds and CelebA via standard ERM for ≥10 epochs.
2. At epoch 5, extract penultimate-layer embeddings for all training examples; run k-means (k=2, n_init=10).
3. Compute AMI (sklearn.metrics.adjusted_mutual_info_score) and worst-cluster purity vs. ground-truth group labels.
4. Repeat across ≥5 random seeds; report mean ± std.
5. Run 2×2 factorial {pretrained, random-init} × {Waterbirds, ColoredMNIST} to test backbone dependency.

**Success Criteria (PoC):**
- Primary: AMI ≥ 0.5 AND worst-cluster purity ≥ 75% on both Waterbirds and CelebA across ≥5 seeds
- Secondary: Top-1 Fisher direction explains ≥60% inter-cluster variance (low-dimensionality of A2)

**Failure Response:**
- IF fails: PIVOT — investigate epoch timing (try epoch 3, 7) before abandoning; if AMI<0.3, mechanism is invalid → ABORT full hypothesis

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 5 (sh1_existence), Section 1.3 Step 1

---
**H-M1: Early Gradient SNR Imbalance Along Cluster-Discovered Spurious Directions**

**Type:** MECHANISM
**Statement:** During epochs 1-10 of pretrained ResNet-50 ERM and SimCLR-SSL training on Waterbirds and CelebA, gradient SNR along cluster-derived spurious directions (from H-E1) exceeds that along invariant directions by ratio>1.5, reflecting SGD simplicity bias in gradient geometry, because high-variance spurious features receive disproportionately large signal-to-noise gradient projections during early representation formation.

**Rationale:** This hypothesis establishes the mechanistic link between annotation-free direction discovery (H-E1) and the shortcut crystallization process. Without confirmed SNR imbalance in both supervised and SSL paradigms, the claim of a unified cross-paradigm gradient geometry mechanism fails. Shah et al. (2020) provides strong evidence for simplicity bias in supervised ERM; this extends it to SSL.

**Variables:**
- Independent: Learning paradigm (supervised ERM vs. SimCLR-SSL)
- Dependent: Gradient SNR ratio = SNR(d_spurious)/SNR(d_invariant) at epoch 5
- Controlled: Cluster directions from H-E1, ≥5 seeds, same datasets

**Verification Protocol:**
1. Attach PyTorch backward hooks to capture per-sample gradients during training.
2. Project mini-batch gradients onto d_spurious and d_invariant (cluster centroid difference vectors from H-E1).
3. Compute SNR(d) = ||mean(g·d)|| / std(g·d) per mini-batch, average over epoch 1-10.
4. Test both ERM and SimCLR on Waterbirds and CelebA (≥5 seeds each).
5. Report SNR ratio distribution across seeds; test H0: ratio ≤ 1.5 via one-sample t-test.

**Success Criteria:**
- Primary: SNR ratio > 1.5 at epoch 5 in both ERM and SimCLR on Waterbirds and CelebA (p<0.05)
- Secondary: SNR ratio trend increases from epoch 1 to 10 (monotonic amplification)

**Failure Response:**
- IF fails (ratio ≤ 1.5): PIVOT — test with other backbone architectures (ViT-B); if SSL consistently shows no imbalance, scope contribution to supervised-only mechanism

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Step 2, Causal Mechanism

---
**H-M2: Early SNR Ratio Predicts Final Worst-Group Accuracy Degradation Cross-Paradigm**

**Type:** MECHANISM
**Statement:** The early gradient SNR ratio (spurious/invariant, computed via cluster-derived directions at epoch 5) predicts final worst-group accuracy degradation with Spearman ρ>0.7 across supervised ERM and SimCLR-SSL on Waterbirds, CelebA, and ColoredMNIST, without retuning the SNR threshold between datasets, because early gradient geometry causally drives representational shortcut consolidation.

**Rationale:** Predictive validity of the SNR measure is necessary to establish it as a meaningful causal diagnostic. If different datasets require different thresholds (e.g., ρ>0.7 on Waterbirds but ρ<0.5 on CelebA), the measure is dataset-specific rather than a general mechanistic signature of shortcut learning.

**Variables:**
- Independent: Early SNR ratio (epoch 5, continuous, measured across multiple training runs varying spuriosity)
- Dependent: Spearman ρ between SNR ratio and final worst-group degradation; same threshold (>1.5) across datasets
- Controlled: Same cluster direction protocol as H-M1, ≥10 training runs per paradigm for correlation

**Verification Protocol:**
1. Collect SNR ratios at epoch 5 across ≥10 training runs with varied spuriosity levels (e.g., correlation strengths 0.5–0.99).
2. For each run, measure final worst-group accuracy (trained to convergence).
3. Compute Spearman ρ between epoch-5 SNR ratio and final worst-group degradation.
4. Apply same analysis to supervised ERM runs and SimCLR-SSL runs independently.
5. Run bootstrapped mediation for SSL: augmentation strength → SNR ratio → worst-group accuracy.

**Success Criteria:**
- Primary: Spearman ρ > 0.7 in both supervised and SSL paradigms; same SNR threshold (>1.5) applicable across datasets
- Secondary: ρ > 0.5 on CelebA specifically (weaker spurious signal)

**Failure Response:**
- IF fails: SCOPE — report H-M2 as dataset-specific limitation; main GSB intervention (H-M4) can still succeed independently

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.6 Prediction P2, Section 1.3 Step 2

---
**H-M3: Shortcut Consolidation Critical Period — Variance Trajectory Anti-Correlation and Spectral Entropy Decrease**

**Type:** MECHANISM
**Statement:** During epochs 1-10 of pretrained ResNet-50 ERM training on Waterbirds, spurious-direction variance increases while invariant-direction variance decreases (anti-correlated trajectories), and spectral entropy of the Fisher eigenspectrum decreases monotonically (spectral compression), establishing a critical training window where shortcut consolidation occurs as a phase transition, because gradient SNR imbalance (H-M1) redirects gradient energy toward spurious directions, suppressing invariant feature learning.

**Rationale:** The "critical period" framing requires empirical evidence beyond SNR imbalance: the actual representational consequences (variance trajectories) and the global spectral signature (eigenspectrum compression) must be observable. This hypothesis provides the mechanistic chain connecting gradient geometry (H-M1) to representation structure, motivating the timing specificity of H-M4.

**Variables:**
- Independent: Training epoch (1–20)
- Dependent: Per-direction variance (spurious, invariant, random control) per epoch; spectral entropy of Fisher eigenspectrum epochs 1-20
- Controlled: Pretrained ResNet-50, ERM, Waterbirds, ≥5 seeds

**Verification Protocol:**
1. During ERM training, compute per-epoch variance along spurious, invariant, and random baseline directions via exponential moving average.
2. At each epoch 1-20, compute between-cluster Fisher scatter matrix; compute eigenspectrum entropy = -Σ(λ_i/Σλ_j)·log(λ_i/Σλ_j).
3. Test anti-correlation hypothesis: Spearman ρ(spurious_var_trajectory, invariant_var_trajectory) < -0.5.
4. Test spectral compression: linear regression of spectral entropy on epoch (1-10); slope should be significantly negative.
5. Repeat across ≥5 seeds; check consistency.

**Success Criteria:**
- Primary: Anti-correlated variance trajectories (spurious↑, invariant↓) with Spearman ρ < -0.5 during epochs 1-10
- Secondary: Spectral entropy decreases monotonically during epochs 1-10 (negative slope, p<0.05)

**Failure Response:**
- IF fails: SCOPE — critical period framing is not supported; document as limitation; H-M4 intervention timing rationale weakened but still testable empirically

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Step 3, Causal Mechanism

---
**H-M4: Early-Only GSB Intervention — Directionally-Specific, Temporally-Specific Worst-Group Improvement**

**Type:** MECHANISM
**Statement:** Early-only GSB (gradient SNR equalization during epochs 1-10) on pretrained ResNet-50 achieves worst-group accuracy ≥5pp above ERM baseline and ≥5pp above block-matched random-subspace balancing on Waterbirds and CelebA (≥5 seeds, p<0.01), outperforms late-only GSB by ≥5pp, and is not achievable by adversarial-orthogonal direction control, because the improvement requires both temporal specificity (critical window) and directional specificity (spurious feature axes) to reverse invariant feature suppression.

**Rationale:** This is the core intervention hypothesis and primary claim of the paper. Demonstrating that early-only outperforms late-only establishes temporal causal specificity, while the adversarial-orthogonal and random-direction controls establish directional specificity. Together, they rule out generic regularization and confirm the mechanistic account from H-M1–H-M3.

**Variables:**
- Independent: Training intervention (6 conditions: ERM, early-only GSB, late-only GSB, full GSB, block-matched random, adversarial-orthogonal)
- Dependent: Worst-group accuracy (primary), average accuracy (no degradation constraint), CKA similarity to spuriosity-free representations
- Controlled: ResNet-50, Waterbirds/CelebA, ≥5 seeds, fixed hyperparameters across conditions

**Verification Protocol:**
1. Implement GSB as PyTorch backward hook: project gradients onto d_spurious, equalize SNR(d_spurious) = SNR(d_invariant) via rescaling.
2. Train all 6 conditions on Waterbirds and CelebA with ≥5 seeds each; measure worst-group and average accuracy.
3. Compute CKA between GSB and ERM representations at checkpoints (epochs 1, 5, 10, final).
4. Run 2×2 factorial {pretrained, random-init} × {early-GSB, ERM} on ColoredMNIST.
5. Run SimCLR augmentation modulation: 5 augmentation strengths × ≥3 seeds + bootstrapped mediation analysis.

**Success Criteria:**
- Primary: Early-only GSB ≥ ERM + 5pp worst-group; early-only ≥ random control + 5pp; p<0.01 across seeds
- Secondary: Early-only ≥ late-only + 5pp (timing specificity); adversarial-orthogonal achieves <70% of early-only improvement (directional specificity)
- Tertiary: CKA divergence from ERM starts at epoch 5; SSL augmentation mediation complete (direct effect p>0.1 after SNR control)

**Failure Response:**
- IF fails primary: PIVOT — reduce threshold to 3pp; investigate epoch window (try 1-15); if still fails after 1 modification → ABANDON main hypothesis
- IF random control achieves comparable improvement: SCOPE — contribution is timing-specific but not direction-specific

**Dependencies:** H-E1, H-M1

**Source:** Phase 2A Section 1.3 Step 4, Section 1.6 Predictions P1/P3

---
**H-C1: Pretrained Backbone Dependency — Mechanism Attenuation Without Pretraining Prior**

**Type:** CONDITION
**Statement:** The GSB mechanism is partially dependent on pretrained backbone initialization: in a 2×2 factorial {pretrained ResNet-50, random-init ResNet-18} × {early-only GSB, ERM} on ColoredMNIST, the interaction term (GSB × pretrained) is statistically significant (p<0.05), and random-init GSB improvement is ≤50% of pretrained-init GSB improvement, because the annotation-free cluster direction discovery (H-E1) requires the representational structure provided by pretrained backbones to reliably recover spurious feature axes at epoch 5.

**Rationale:** A1 states that pretrained backbone is a required assumption. This condition hypothesis tests the boundary: does GSB still work (partially) for from-scratch training? A partial effect would refine the scope of the mechanism rather than invalidate it. Full absence of effect in random-init would confirm the pretrained backbone as a hard requirement.

**Variables:**
- Independent: Backbone initialization (pretrained ResNet-50 vs. random-init ResNet-18) × Training intervention (early-only GSB vs. ERM)
- Dependent: Worst-group accuracy improvement from GSB; 2×2 interaction effect size (Cohen's d)
- Controlled: ColoredMNIST dataset, ≥5 seeds, fixed training hyperparameters

**Verification Protocol:**
1. Train 4 conditions: {pretrained ResNet-50, random ResNet-18} × {early-only GSB, ERM} on ColoredMNIST (≥5 seeds each).
2. Measure worst-group accuracy at convergence for all conditions.
3. Compute GSB improvement = GSB WGA - ERM WGA for each initialization type.
4. Test interaction: pretrained_improvement vs. random_improvement via two-sample t-test.
5. Report effect sizes (Cohen's d) and confidence intervals; plot interaction plot.

**Success Criteria:**
- Primary: Significant interaction term (p<0.05); pretrained GSB improvement > random-init GSB improvement
- Secondary: Random-init GSB improvement ≤ 50% of pretrained-init improvement (quantifying backbone dependency)

**Failure Response:**
- IF fails (no interaction): SCOPE — backbone dependency is not confirmed; GSB may generalize to from-scratch training (positive surprise); report accordingly

**Dependencies:** H-M4

**Source:** Phase 2A Section 1.4 A1, Section 1.5 Scope, Key Tension in causal mechanism

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2
           ↓
          H-M3
           ↓
          H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AMI≥0.5 AND purity≥75% on Waterbirds/CelebA (≥5 seeds) | STOP — reassess entire mechanism; investigate epoch timing |
| H-M1 | MUST_WORK | SNR ratio > 1.5 at epoch 5 in ERM and SimCLR (p<0.05) | PIVOT — test ViT-B; if still fails, scope to supervised-only |
| H-M2 | SHOULD_WORK | Spearman ρ > 0.7 cross-paradigm, same threshold | SCOPE — report as dataset-specific limitation |
| H-M3 | SHOULD_WORK | Anti-correlated variance trajectories + spectral entropy decrease | SCOPE — weaken critical period framing; empirical timing rationale still valid |
| H-M4 | MUST_WORK | Early-only ≥ ERM+5pp AND ≥ random+5pp (p<0.01) | PIVOT (1× modification) → ABANDON if still fails |
| H-C1 | SHOULD_WORK | Significant interaction: pretrained > random-init improvement | SCOPE — confirm boundary; report as nuanced scope refinement |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Clustering Validity Failure (Source: A1)**
- Description: Pretrained backbone does not produce separable cluster structure at epoch 5 (AMI<0.5)
- Severity: Critical | Likelihood: Low
- Affected Hypotheses: H-E1, H-M1, H-M4 (all depend on cluster directions)
- Mitigation:
  1. Prevention: Run pilot clustering check on Waterbirds before full experiments
  2. Detection: Monitor AMI at epochs 3, 5, 7; if epoch 5 is unstable, adjust
  3. Response: PIVOT to epoch 3 or epoch 7; SCOPE to Waterbirds only if CelebA fails

**Risk R2: Low-Dimensionality Assumption Violation (Source: A2)**
- Description: Spurious feature directions span >5 dimensions (top-5 <85% inter-cluster variance)
- Severity: High | Likelihood: Low-Medium
- Affected Hypotheses: H-M1, H-M2, H-M4 (SNR projection loses interpretability)
- Mitigation:
  1. Prevention: Pre-register eigenspectrum threshold test (top-1 ≥60%, top-5 ≥85%) before SNR measurement
  2. Detection: Compute Fisher eigenspectrum at epoch 5; check concentration
  3. Response: PIVOT to subspace SNR (project onto top-k Fisher subspace); reformulate as distributed anisotropy

**Risk R3: Invariant Features Absent (Source: A3)**
- Description: In some settings, invariant features are genuinely absent (not suppressed)
- Severity: High | Likelihood: Low
- Affected Hypotheses: H-M4 (GSB would amplify noise, not recover signal)
- Mitigation:
  1. Prevention: DFR replication on target datasets confirms invariant features present before running GSB
  2. Detection: Absent-signal control on ColoredMNIST (fully randomized invariant features condition)
  3. Response: SCOPE — exclude absent-signal settings explicitly; mechanism valid only for suppressed signals

**Risk R4: Cross-Paradigm Mechanism Divergence (Source: A4)**
- Description: SSL gradient projections do not follow same SNR imbalance pattern as supervised ERM
- Severity: High | Likelihood: Medium
- Affected Hypotheses: H-M1 (SSL component), H-M2 (cross-paradigm ρ), H-M4 (SSL extension)
- Mitigation:
  1. Prevention: Include augmentation modulation test as natural experiment (P3)
  2. Detection: Compare SNR ratios ERM vs. SimCLR side-by-side at epoch 5
  3. Response: SCOPE — contribution reduces to supervised-only + SSL correlation evidence (partial mediation reportable as nuanced finding)

**Risk R5: Timing Specificity Failure (Source: A5)**
- Description: Early-only GSB does not outperform late-only GSB by ≥5pp
- Severity: High | Likelihood: Low-Medium
- Affected Hypotheses: H-M4 (timing specificity claim), H-M3 (critical period framing)
- Mitigation:
  1. Prevention: Full timing ablation (early 1-10, late 11+, full) designed from the start
  2. Detection: Intermediate checkpoints at epoch 10 reveal whether shortcut consolidation has occurred
  3. Response: PIVOT — if early-only ≈ late-only, report GSB effect as timing-independent regularization (still publishable, weaker mechanistic claim)

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Mitigation Strategy |
|------|--------|---------------------|----------|---------------------|
| R1: Clustering validity failure | A1 | H-E1, H-M1, H-M4 | Critical | Pilot check; epoch timing adjustment; scope to best dataset |
| R2: High-dimensionality spurious features | A2 | H-M1, H-M2, H-M4 | High | Pre-registered eigenspectrum threshold; subspace SNR fallback |
| R3: Invariant features absent | A3 | H-M4 | High | DFR replication check; absent-signal ColoredMNIST control |
| R4: SSL paradigm divergence | A4 | H-M1, H-M2, H-M4 | High | Augmentation modulation test; mediation analysis |
| R5: Timing non-specificity | A5 | H-M3, H-M4 | High | Full timing ablation; epoch-10 intermediate checkpoint |

**Risk Summary:** 1 Critical, 4 High risks. All have pre-designed mitigations. Critical risk (R1) has low likelihood given DFR evidence. Scope-reduction fallbacks available for all High risks without invalidating core contribution.

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root: No Dependencies]
    H-E1 (EXISTENCE — Clustering Validity)
         │
         ▼
[Level 1 — Core Mechanisms: Sequential]
    H-M1 ← H-E1  (SNR Imbalance Detection)
         │
         ├─────────────────┐
         ▼                 ▼
    H-M2 ← H-M1       H-M3 ← H-M1
    (SNR Prediction)   (Critical Period)
         │                 │
         └─────────────────┘
                   │
                   ▼
    H-M4 ← H-E1 + H-M1  (GSB Intervention — Primary)
         │
         ▼
[Level 2 — Condition: Optional Boundary]
    H-C1 ← H-M4  (Backbone Dependency)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M4
Critical Gates: MUST_WORK at H-E1, H-M1, H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 1 (parallel) | H-M2 | H-M1 | SHOULD_WORK |
| 1 (parallel) | H-M3 | H-M1 | SHOULD_WORK |
| 2 | H-M4 | H-E1, H-M1 | MUST_WORK |
| 3 | H-C1 | H-M4 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 6 Hypotheses | Total: 8 weeks
═══════════════════════════════════════════════════════════════════════════════
Phase / Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │ W8
─────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-E1 (Existence)   │ ████████│         │         │         │         │
  [Gate 1 ◆]         │       ◆ │         │         │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Mechanisms
  H-M1 (SNR Imbal.)  │         │ ████████│         │         │         │
  [Gate 2 ◆]         │         │       ◆ │         │         │         │
  H-M2 (SNR Pred.)   │         │         │ ████    │         │         │
  H-M3 (Crit. Per.)  │         │         │ ████    │         │         │
  H-M4 (GSB Interv.) │         │         │         │ ████████│         │
  [Gate 3 ◆]         │         │         │         │       ◆ │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2.5: Conditions
  H-C1 (Backbone)    │         │         │         │         │ ████    │
  [Gate 2.5 ◆]       │         │         │         │         │       ◆ │
─────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks | Critical Path: H-E1 → H-M1 → H-M4 (6 weeks)
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M4
Critical Path Duration: 6 weeks
  - H-E1: 2 weeks (Weeks 1-2)
  - H-M1: 2 weeks (Weeks 3-4)
  - H-M4: 2 weeks (Weeks 6-7, after H-M2/H-M3 in Week 5)
Parallel Track: H-M2 + H-M3 run in parallel (Week 5, SHOULD_WORK)
Conditions Track: H-C1 (Week 7-8, SHOULD_WORK)
Total Duration: 8 weeks
Slack: H-M2 and H-M3 have 1-week slack vs. H-M4 gate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 6
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
  - Condition: 1 (H-C1)

Verification Phases: 3
  1. Foundation (H-E1)
  2. Mechanisms (H-M1–H-M4)
  2.5. Conditions (H-C1)

Estimated GPU Hours: ~100-120 GPU-hours on A100
  - H-E1: ~10h (clustering, ≥5 seeds × 2 datasets)
  - H-M1–H-M3: ~30h (gradient hooks + SSL, ≥5 seeds)
  - H-M4: ~60h (6 conditions × 2 datasets × ≥5 seeds)
  - H-C1: ~10h (2×2 factorial, ColoredMNIST)

Total Duration: 8 weeks
Critical Path: 6 weeks (H-E1 → H-M1 → H-M4)
Execution Mode: Sequential chain (H-E1 → H-M1 gates); parallel for H-M2/H-M3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 (Foundation) — Weeks 1-2
**Step 2**: Evaluate Gate 1 (MUST_WORK) → If pass, proceed to H-M1
**Step 3**: Execute H-M1 (SNR Imbalance) — Weeks 3-4
**Step 4**: Evaluate Gate 2 (MUST_WORK) → If pass, proceed to parallel H-M2/H-M3 + H-M4 prep
**Step 5**: Execute H-M2 and H-M3 in parallel — Week 5
**Step 6**: Execute H-M4 (GSB Intervention — primary) — Weeks 6-7
**Step 7**: Evaluate Gate 3 (MUST_WORK) → If pass, proceed to H-C1
**Step 8**: Execute H-C1 (Backbone Dependency) — Week 7-8
**Step 9**: Evaluate Gate 2.5 (SHOULD_WORK) → Record scope refinement
**Final**: PoC verification complete → proceed to Phase 5 (Baseline Comparison, DETERMINES_SUCCESS gate)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Early gradient SNR imbalance along annotation-free cluster-discovered spurious feature directions causally drives shortcut crystallization during epochs 1-10, and GSB intervention during this critical window improves worst-group accuracy ≥5pp across supervised ERM, SSL, and contrastive paradigms without group annotations.

**Supporting Evidence:**
1. SGD simplicity bias is well-established [Shah et al. 2020]; gradient geometry mechanism extends this to a spatial/directional account
2. DFR's empirical success (post-hoc last-layer retraining achieves 97% WGA) confirms A3: invariant features are present but suppressed — exactly the signal GSB can rescue
3. GEORGE clustering [Bao et al.] demonstrates k-means recovers spurious groups; penultimate-layer clustering at epoch 5 is grounded in established embedding structure

**Strengths:**
- Annotation-free (zero group labels for training/intervention)
- Preventive (not post-hoc) — intervenes during representation formation
- Cross-paradigm (mechanism is paradigm-agnostic gradient geometry)
- Falsifiable with pre-registered quantitative thresholds for every component
- Low computational overhead (~0.5MB hook; 100-120 GPU-hours total)

**Expected Outcomes:**
- P1: Early-only GSB WGA ≥ ERM + 5pp AND ≥ random control + 5pp (Waterbirds/CelebA, ≥5 seeds)
- P2: Spearman ρ > 0.7 (SNR ratio → worst-group degradation) cross-paradigm
- P3: SSL augmentation modulation ρ ≤ -0.8 (SNR) and ≥ 0.8 (WGA), full mediation

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in worst-group accuracy between early-only GSB and ERM baseline when controlling for random-subspace gradient balancing, and early gradient SNR ratio does not predict final worst-group accuracy degradation with Spearman ρ > 0.5 across learning paradigms.

**Counter-Arguments:**
1. **Confounding by pretraining prior (A1 violation):** The cluster structure at epoch 5 may reflect ImageNet pretraining priors rather than current-task spurious correlations — the mechanism may be: pretraining → good cluster structure → effective GSB, not: spurious correlation → SNR imbalance → GSB effectiveness
2. **Generic regularization alternative (A5 challenge):** Early-epoch gradient manipulation may improve worst-group accuracy through generic gradient noise reduction or implicit regularization, not directionally-specific SNR equalization
3. **SSL partial mediation (A4 challenge):** Augmentation strength may improve worst-group accuracy via two parallel mechanisms (SNR reduction AND direct augmentation-induced invariance), not through the claimed complete mediation path

**Potential Failure Points:**
- R1 (Critical): Clustering validity fails → entire mechanism collapses
- R4 (High): SSL shows no SNR imbalance → cross-paradigm unification fails
- R5 (High): Early-only ≈ late-only → timing not causally specific

**Conditions Under Which H0 Would Be Supported:**
- AMI < 0.5 on Waterbirds/CelebA (H-E1 fails → R1 confirmed)
- Early-only GSB ≤ ERM + 5pp OR random control achieves ≥70% of GSB improvement
- Spearman ρ < 0.5 for SNR ratio vs. worst-group degradation in either paradigm

### 6.3 Synthesis

**Balanced Assessment:** The hypothesis presents a mechanistically specific, annotation-free, cross-paradigm claim with five pre-registered falsification tests. However, the null hypothesis raises valid concerns: the pretrained backbone confound (quantified by 2×2 factorial interaction analysis) and the SSL partial mediation risk (tested by conditional independence) represent the two hardest challenges. The verification plan directly addresses both.

**Resolution Path:**
The verification plan resolves this dialectic through:
1. **Foundation verification (H-E1):** Confirms annotation-free proxy validity before any mechanism claim
2. **Sequential mechanism testing (H-M1 → H-M4):** Tests causal chain step-by-step; MUST_WORK gates at H-E1, H-M1, H-M4 allow early detection of H0 support
3. **Three-way directional controls:** Isotropic, block-matched, adversarial-orthogonal eliminate generic regularization interpretation
4. **2×2 factorial on ColoredMNIST:** Separates optimization dynamics from pretraining prior
5. **Bootstrapped mediation for SSL:** Tests conditional independence (full vs. partial mediation)

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (AMI≥0.5, purity≥75%)
- H-M1 MUST_WORK gate passes (SNR ratio>1.5, p<0.05)
- H-M4 MUST_WORK gate passes (early-only ≥ ERM+5pp AND ≥ random+5pp, p<0.01)

**Conditions for Antithesis Support (partial):**
- H-E1 MUST_WORK fails: Full H0 support — mechanism invalid
- H-M4 fails but H-M1 passes: Mechanism exists but intervention doesn't work — scope to diagnostic tool
- Random control achieves ≥70% of GSB: Direction not critical — generic regularization interpretation

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M4 pass → Thesis validated; H-M2/H-M3/H-C1 refine scope
2. **Partial Support:** H-E1 + H-M1 pass, H-M4 partial → GSB works but not at claimed threshold; refinable
3. **Scope-Limited Support:** H-E1 + H-M1 + H-M4 pass supervised only, SSL partial mediation → Cross-paradigm claim narrowed to supervised + correlated-SSL
4. **No Support:** H-E1 or H-M1 fail → Antithesis supported; route to Phase 0 (new direction)

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Clustering valid at epoch 5 (DFR evidence strong) | Epoch 5 may not be stable across seeds | H-E1 + multi-seed test |
| Mechanism (Step 1-2) | SNR imbalance in both ERM and SSL | SSL gradient projections not analogous | H-M1 + augmentation modulation |
| Mechanism (Step 3-4) | Critical period + directional specificity | Generic regularization alternative | H-M3 variance trajectories + adversarial-orthogonal control |
| Intervention | Early-only beats late-only + random | Timing not causally specific | H-M4 timing ablation (6 conditions) |
| Scope | Cross-paradigm (supervised + SSL) | SSL partial mediation | H-M2 mediation analysis |
| Boundary | Pretrained backbone dependency quantified | Mechanism driven by pretraining prior | H-C1 + 2×2 factorial |

**Overall Robustness Score:** High
**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-GSB-v1 — GSB during epochs 1-10 improves worst-group accuracy ≥5pp over ERM, annotation-free, cross-paradigm.
- ID: H-GSB-v1 | Confidence: 0.78 | Mode: Incremental (50% scope reduction)

**Verification Structure:**
- Sub-Hypotheses: 6 total (H-E1, H-M1, H-M2, H-M3, H-M4, H-C1)
  - H-E: 1, H-M: 4, H-C: 1
- Phases: 3 phases over 8 weeks
- Critical Gates: 3 MUST_WORK gates (H-E1, H-M1, H-M4)
- Parallel tracks: H-M2 + H-M3 run in parallel (Week 5)

**Risk Assessment:** Medium-High
- Primary concerns: Clustering validity (R1, Critical, low likelihood); SSL paradigm divergence (R4, High, medium likelihood)
- All risks have pre-designed mitigations and scope-reduction fallbacks

**Immediate Action:** Begin Phase 1 with H-E1 — pilot clustering validity check on Waterbirds before committing full experimental suite.

### 7.2 Conclusions

**Key Achievements:**
- 6 sub-hypotheses defined with explicit quantitative falsification thresholds for all MUST_WORK gates
- H0 addressed: SNR predictive validity + directional specificity controls constitute comprehensive causal validation
- All experiments use existing datasets and architectures; no new infrastructure required

**Verification Execution Order:**
- **Phase 1: Foundation** (2 weeks): H-E1 (AMI≥0.5, purity≥75%) → Gate 1 MUST PASS
- **Phase 2: Mechanisms** (5 weeks): H-M1 (SNR imbalance) → Gate 2 MUST PASS → H-M2/H-M3 (parallel, SHOULD_WORK) + H-M4 (intervention) → Gate 3 MUST PASS
- **Phase 2.5: Conditions** (1 week): H-C1 (backbone dependency) → Gate 2.5 SHOULD_WORK

**Critical Decision Points:**
1. **Gate 1 (H-E1 MUST_WORK):** AMI<0.5 → STOP, investigate epoch timing or backbone; AMI≥0.5 → proceed
2. **Gate 2 (H-M1 MUST_WORK):** SNR ratio ≤ 1.5 → PIVOT to ViT-B or scope supervised-only
3. **Gate 3 (H-M4 MUST_WORK):** Early-only < ERM+5pp → PIVOT once (adjust window) → ABANDON if persists

**Open Questions:**
- Whether GSB mechanism holds for ViT-B architecture (attention-based representations may alter gradient geometry)
- Whether NLP modality (MultiNLI, CivilComments) exhibits analogous early gradient SNR patterns
- Whether partial SSL mediation (if observed) implies a distinct augmentation-invariance mechanism
- Whether from-scratch ColoredMNIST training shows any GSB effect (H-C1 boundary quantification)

**Recommendations:**
1. Immediate: Run pilot clustering check on Waterbirds (H-E1, 2 seeds) before full suite
2. Infrastructure: Set up PyTorch backward hooks for gradient SNR measurement early (reused by H-M1–H-M4)
3. Resource: Allocate 8 weeks + 20% buffer; 100-120 GPU-hours on A100 (feasible in 1 week if parallelized)
4. Failure Management: Document all PARTIAL results carefully; prepare Serena memory files for any MUST_WORK failures

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `03_refinement.yaml` (H-GSB-v1, generated 2026-05-20, schema v10.0.0)
- Supplementary: `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`
- Phase 2A convergence: All 6 criteria met after 16 exchanges (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 3 (ClearThought scientificmethod)
- Tools: mcp__clearThought__scientificmethod × 3 (H-E1, H-M1–H-M2, H-M3–H-M4)
- Mode: Incremental (Phase 2A pre-seeded structure used)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-20*

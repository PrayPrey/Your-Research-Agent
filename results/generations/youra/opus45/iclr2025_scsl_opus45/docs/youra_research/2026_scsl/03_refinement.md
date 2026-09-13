# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-14T08:31:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Existing Loss Trajectory Divergence Analysis for Spurious Correlation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS with criteria, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed

### Key Insights
1. Temporal dynamics offer a fundamentally different lens than static metrics for analyzing spurious correlation
2. Curvature timing provides mechanistic depth beyond simple classification AUROC
3. Attenuation under debiasing (GroupDRO) is the key discriminator for spurious-specificity vs generic hardness
4. Cross-seed prediction transforms correlation into near-causal evidence
5. Asymmetric patterns between minority Groups 1 and 2 distinguish spurious conflict from spectral bias

### Breakthrough Moments
- **Exchange 5**: Dr. Ally proposed asymmetric minority group test to distinguish rarity from spurious conflict
- **Exchange 8**: Prof. Pax introduced curvature-based temporal signatures as mechanistic discriminator
- **Exchange 11**: Consolidated hypothesis framework with quantitative thresholds and falsifiers
- **Exchange 15**: Prof. Rex endorsed hypothesis with fail-fast execution order

---

## Final Hypothesis

### Title
Loss Trajectory Divergence Analysis for Spurious Correlation Detection

### Hypothesis ID
H-LossTraj-v1

### Core Claim
Under standard ERM training on spurious correlation benchmarks (Waterbirds), if we track per-sample loss trajectories across epochs, then minority group samples will exhibit statistically distinguishable trajectory patterns (AUROC > 0.75) with delayed curvature stabilization (≥3 epochs later than majority), because the model experiences prolonged optimization conflict when spurious background features contradict learned shortcuts.

### Mechanism
1. **Early training**: Model learns spurious correlations (e.g., "water → waterbird") as dominant features
2. **Majority samples**: Background aligns with spurious cue → fast loss descent, early curvature stabilization (epoch ≤5)
3. **Minority samples**: Background conflicts with spurious cue → prolonged optimization conflict → slower descent, delayed curvature (through epoch ≥8)
4. **Result**: Trajectory divergence emerges early (epochs 3-5) and predicts final WGA disparity

---

## Hypothesis Chain

| ID | Type | Prediction | Success Criterion | Falsifier |
|----|------|------------|-------------------|-----------|
| **H-E1** | Existence | Trajectory features predict minority membership | AUROC > 0.75 | AUROC ≤ 0.75 |
| **H-M1** | Mechanism | Curvature timing gap between groups | Gap ≥ 3 epochs in ≥70% seeds | Gap < 2 epochs |
| **H-M2** | Mechanism | Attenuation under GroupDRO | ΔAUROC > 0.10 (GroupDRO), < 0.05 (Random) | Both attenuate similarly |
| **H-M3** | Causation | Cross-seed predictive power | R² > 0.5, effect ≥3% per SD | R² < 0.3 or trivial effect |

**Execution Order**: H-E1 → H-M2 → H-M1 → H-M3 (fail-fast strategy)

---

## Predictions

### P1 (Primary)
**Statement**: Trajectory features (L₁, slope, variance, time-to-convergence) predict minority membership with AUROC > 0.75

**Test Method**: Train logistic regression on trajectory features from epochs 1-5; 5-fold stratified CV

**Success Criterion**: AUROC > 0.75, p < 0.05 vs random baseline

### P2
**Statement**: Curvature timing gap between majority and minority groups is ≥3 epochs

**Test Method**: Compute curvature sign-flip epoch per group; measure gap

**Success Criterion**: Gap ≥ 3 epochs in ≥70% of seeds

### P3
**Statement**: AUROC attenuates by >0.10 under GroupDRO but <0.05 under variance-matched random reweighting

**Test Method**: Compare AUROC across training regimes

**Success Criterion**: GroupDRO-specific attenuation (not generic variance reduction)

### P4
**Statement**: Early divergence (epoch 3) predicts final WGA with R² > 0.5 across seeds

**Test Method**: Regress WGA_epoch20 on W1-distance_epoch3 across 10+ seeds

**Success Criterion**: R² > 0.5, effect size ≥3% absolute per SD

---

## Novelty

**Key Innovation**: First temporal characterization of spurious correlation formation dynamics during training

**What's New**:
- No existing work examines loss trajectory divergence between spurious correlation groups
- No existing work tests whether divergence precedes accuracy gaps
- No existing work validates that divergence attenuates under debiasing

**Differentiation from Prior Work**:
| Prior Work | Difference |
|------------|------------|
| Toneva et al. (2018) - Forgetting | Binary correctness; we track continuous loss with curvature |
| Li et al. (2025) - 142-D TD | General features; we focus on spurious group divergence |
| GroupDRO literature | Post-hoc accuracy; we analyze training-time dynamics |

---

## Experimental Design

### Dataset
- **Primary**: Waterbirds (95%/5% spurious correlation)
- **Secondary**: CelebA (for generalization validation)

### Model
- ResNet-50 pretrained on ImageNet

### Baselines
- Gradient norm detection (AUC = 0.914)
- Random baseline (AUROC = 0.5)
- GroupDRO (for attenuation test)

### Methodology
1. Train ERM model with per-sample loss logging (20 epochs)
2. Normalize losses (Lₜ/L₁) and apply 3-point smoothing
3. Extract trajectory features: initial loss, slope, variance, time-to-convergence
4. Train logistic regression classifier
5. Evaluate with 5-fold stratified CV
6. Compute curvature timing gap
7. Compare ERM vs GroupDRO vs Random reweighting
8. Run cross-seed predictive analysis (10+ seeds)

---

## Limitations

### Known Scope Boundaries
- Applies to spurious correlation settings with group labels
- Standard ERM training on image classification
- Does NOT apply to intervention design (detection only)

### Causal Interpretation Limits
- Results are "consistent with" spurious-feature conflict, not definitive proof
- Cannot mathematically distinguish spurious features from structured hardness

### Technical Assumptions
- A1: Per-sample loss trackable without noise dominating
- A2: Curvature differences reflect dynamics, not scale
- A3: GroupDRO specifically attenuates spurious reliance
- A4: Between-seed WGA variance ≥3%

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met at Exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Causal interpretation limits; H-M3 power depends on σ_WGA |

---

## Persona Verdicts

| Persona | Verdict | Key Assessment |
|---------|---------|----------------|
| 🔭 Dr. Nova | STRONG | First temporal characterization; genuinely novel |
| 🔬 Prof. Vera | STRONG | Explicit thresholds and falsifiers; rigorous |
| 🎯 Dr. Sage | STRONG (conditional) | High impact if full chain passes |
| ⚙️ Prof. Pax | STRONG | No fundamental barriers; feasible |
| 🛡️ Dr. Ally | ENDORSED | Ready for Phase 2B |
| 🔍 Prof. Rex | ENDORSED | Rigorous with appropriate caveats |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*

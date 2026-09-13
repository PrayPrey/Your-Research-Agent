# Verification Plan: Shortcut Crystallization Zone

**Date:** 2026-08-19
**Hypothesis ID:** H-ShortcutCrystallization-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard SGD training on spurious-correlation benchmarks (Waterbirds, CelebA, ColoredMNIST), if we track worst-group accuracy across training epochs, then we will observe a localized training phase (the "Shortcut Crystallization Zone") where classifier reliance on spurious features accelerates, because simplicity bias creates initial spurious feature advantage and gradient starvation amplifies this through self-reinforcing feedback.

### 1.2 Alternative Hypothesis (H0)

There is no localized acceleration in worst-group accuracy decline during training; the decline rate is constant throughout training (linear decay pattern).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), CelebA, ColoredMNIST (standard) | Standard spurious correlation benchmarks with group annotations enabling WGA computation |
| **Model** | ResNet-50 | Standard architecture used in group robustness literature; enables comparison with prior work |

**Dataset Details:**
- Source: WILDS benchmark suite (p-lambda/wilds)
- Path: Downloaded via wilds.get_dataset()

**Model Details:**
- Type: CNN
- Source: torchvision.models.resnet50(pretrained=True)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM (Empirical Risk Minimization) | ~60-75% WGA | Waterbirds |
| Group DRO | ~85-90% WGA | Waterbirds |
| JTT (Just Train Twice) | ~80-85% WGA | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Worst-group accuracy is a valid proxy for spurious feature reliance | Standard metric in group robustness literature (Sagawa 2020) | Would need alternative spurious reliance measurement |
| A2 | Second derivative can detect acceleration in decline rate | Standard calculus — negative second derivative indicates accelerating decline | Would need alternative transition detection method |
| A3 | 5-epoch smoothing window is appropriate for noise reduction | Balances noise reduction with temporal resolution | Results may be sensitive to window choice; sensitivity analysis planned |
| A4 | Crystallization phenomenon generalizes across architectures | Simplicity bias observed across architectures (Shah 2020) | Finding would be architecture-specific |
| A5 | Benchmarks (Waterbirds, CelebA, ColoredMNIST) are representative | Standard benchmarks in spurious correlation research | Findings may not generalize to other domains |

### 1.6 Research Gap & Novelty

**Gap:** Prior work describes WHAT (simplicity bias) and WHY (gradient starvation) but not WHEN shortcuts crystallize. No temporal characterization of spurious feature dominance exists.

**Novelty:** Moving from static descriptions to dynamic temporal characterization. Second derivative of worst-group accuracy as crystallization detector is novel. Enables precisely-timed interventions vs. post-hoc corrections.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | pending |
| H-M2 | Mechanism | MUST_WORK | H-M1 | pending |
| H-M3 | Mechanism | MUST_WORK | H-M2 | pending |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | pending |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Crystallization Zone Existence**

**Statement**: Under standard SGD training on spurious-correlation benchmarks, if we track worst-group accuracy, then we will observe a localized training phase where WGA decline accelerates, because simplicity bias creates initial spurious feature advantage.

**Rationale**: Foundation hypothesis. Must establish crystallization zone exists as detectable phenomenon before testing mechanism. This validates the core claim of temporal localization.

**Variables**:
- Independent: Training epoch (1 to N)
- Dependent: Worst-group accuracy (WGA), d²WGA/dt²
- Controlled: Architecture (ResNet-50), batch size (128), optimizer (SGD)

**Verification Protocol**:
1. Train ResNet-50 on Waterbirds/CelebA/ColoredMNIST with epoch-level checkpointing (full train sets, standard splits)
2. Compute WGA at each checkpoint across all minority-group samples (n>500 per benchmark)
3. Apply 5-epoch rolling average smoothing to WGA curve
4. Compute second derivative d²WGA/dt²
5. Test for statistically significant (p<0.05) negative peak

**Success Criteria** (PoC: Direction-based):
- Primary: Significant negative d²WGA/dt² peak in first 50% of training
- Secondary: Effect present in at least 2/3 benchmarks

**Failure Response**:
- IF fails: PIVOT to alternative crystallization detection (gradient norm analysis)

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, Prediction P1

---
**H-M1: Self-Reinforcing Feedback Loop**

**Statement**: Under continued training past early epochs, if spurious features gain initial advantage, then the feedback loop becomes self-reinforcing at the crystallization point, because gradient starvation amplifies dominant feature signal.

**Rationale**: Tests the transition from linear to accelerating dynamics. Key mechanism claim linking established gradient starvation to novel crystallization timing.

**Variables**:
- Independent: Training epoch
- Dependent: Minority feature gradient magnitude ratio
- Controlled: Architecture, batch size, optimizer

**Verification Protocol**:
1. Track gradient magnitude for spurious vs core feature classifiers during training
2. Compute ratio of minority feature gradient to majority feature gradient per epoch
3. Identify epoch where ratio shows inflection (acceleration in decrease)
4. Correlate inflection timing with d²WGA/dt² peak from H-E1
5. Test temporal correlation (within 5 epochs)

**Success Criteria**:
- Primary: Gradient ratio inflection correlates with WGA acceleration (r > 0.7)
- Secondary: Inflection occurs before 50% of training

**Failure Response**:
- IF fails: EXPLORE alternative mechanism (loss landscape analysis)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 3

---
**H-M2: Classifier Commitment Post-Crystallization**

**Statement**: After the crystallization point, if classifier weights are analyzed, then spurious feature weights will dominate and not shift back, because the self-reinforcing feedback has committed the classifier.

**Rationale**: Tests the irreversibility claim. Distinguishes crystallization from temporary fluctuation.

**Variables**:
- Independent: Training epoch (post-crystallization)
- Dependent: Classifier weight ratio (spurious vs core features)
- Controlled: Architecture, no intervention

**Verification Protocol**:
1. Identify crystallization point from H-E1
2. Train additional epochs past crystallization (to 100% of training)
3. Apply linear probes to frozen embeddings at multiple checkpoints post-crystallization
4. Measure linear probe accuracy ratio (spurious feature prediction / core feature prediction)
5. Test for monotonic dominance of spurious weights post-crystallization

**Success Criteria**:
- Primary: Spurious feature probe accuracy does not decrease post-crystallization
- Secondary: Core feature probe accuracy remains suppressed

**Failure Response**:
- IF fails: EXPLORE whether late reversal is possible

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 4

---
**H-M3: Second Derivative Detection Method**

**Statement**: Under standard measurement conditions, if we compute d²WGA/dt² with 5-epoch smoothing, then the crystallization point will be detectable as a significant negative peak, because acceleration in decline produces negative second derivative.

**Rationale**: Tests the proposed measurement methodology. Critical for practical applicability.

**Variables**:
- Independent: Smoothing window size (3, 5, 7 epochs)
- Dependent: Detectability of crystallization peak (signal-to-noise ratio)
- Controlled: Benchmark dataset, architecture

**Verification Protocol**:
1. Compute d²WGA/dt² with window sizes 3, 5, 7 epochs
2. Measure peak signal-to-noise ratio for each window
3. Test sensitivity: Does 5-epoch window consistently detect peak?
4. Run across 5 random seeds per benchmark for statistical power
5. Report detection reliability (% of runs where peak is significant)

**Success Criteria**:
- Primary: 5-epoch window detects significant peak in >80% of runs
- Secondary: Peak timing variance <5 epochs across seeds

**Failure Response**:
- IF fails: PIVOT to alternative window or detection method

**Dependencies**: H-M2

**Source**: Phase 2A Prediction P1, Assumption A2-A3

---
**H-M4: Benchmark-Relative Timing**

**Statement**: Under varying training durations across benchmarks, if we normalize epoch to percentage of total training, then crystallization peak will occur at 20-40% of training duration, because the phenomenon is relative to dataset difficulty.

**Rationale**: Tests generalizability of timing claim. Important for practical intervention design.

**Variables**:
- Independent: Benchmark dataset
- Dependent: Normalized crystallization epoch (% of total training)
- Controlled: Architecture, hyperparameters per benchmark defaults

**Verification Protocol**:
1. Run full training on each benchmark (Waterbirds: 100 epochs, CelebA: 50 epochs, ColoredMNIST: 30 epochs)
2. Identify crystallization peak epoch for each
3. Normalize to percentage of total training
4. Test whether peak falls in 20-40% range for all benchmarks
5. Compute variance in normalized timing across benchmarks

**Success Criteria**:
- Primary: Peak occurs within 20-40% range for all 3 benchmarks
- Secondary: Variance in normalized timing <10%

**Failure Response**:
- IF fails: Document benchmark-specific timing patterns

**Dependencies**: H-M3

**Source**: Phase 2A Prediction P3

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Significant d²WGA/dt² peak in first 50% of training | STOP: Reassess hypothesis |
| H-M1 | MUST_WORK | Gradient ratio inflection correlates with WGA peak (r>0.7) | EXPLORE: Alternative mechanism |
| H-M2 | MUST_WORK | Spurious weights don't decrease post-crystallization | EXPLORE: Late reversal possibility |
| H-M3 | MUST_WORK | 5-epoch window detects peak in >80% of runs | PIVOT: Alternative detection method |
| H-M4 | SHOULD_WORK | Peak at 20-40% of training for all benchmarks | Document benchmark-specific timing |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 1 week |
| Phase 2: Core Mechanisms | H-M1, H-M2 | 2 weeks |
| Phase 3: Detection Method | H-M3, H-M4 | 1 week |

**Total Duration:** 4 weeks (PoC verification)

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source Assumption | Description |
|----|------|-------------------|-------------|
| R1 | WGA proxy validity | A1 (WGA as spurious reliance proxy) | If WGA doesn't accurately reflect spurious feature reliance, crystallization signal may be spurious |
| R2 | Detection method failure | A2 (Second derivative detection) | If second derivative is too noisy or insensitive, crystallization may be undetectable |
| R3 | Smoothing window sensitivity | A3 (5-epoch smoothing) | Results may vary significantly with window choice, making findings non-robust |
| R4 | Architecture specificity | A4 (Cross-architecture generalization) | Crystallization may be ResNet-specific, limiting scientific contribution |
| R5 | Benchmark representativeness | A5 (Standard benchmarks) | Findings may not generalize beyond Waterbirds/CelebA/ColoredMNIST |

### 4.2 Risk-Hypothesis Mapping

| Risk | Severity | Likelihood | Affected Hypotheses |
|------|----------|------------|---------------------|
| R1 | High | Low | H-E1, H-M1, H-M2 |
| R2 | Critical | Medium | H-E1, H-M3 |
| R3 | Medium | Medium | H-M3, H-M4 |
| R4 | Medium | Medium | All (generality claim) |
| R5 | Low | Low | All (scope claim) |

### 4.3 Mitigation Strategies

**R1 (WGA Proxy Validity):**
- Prevention: Validate WGA with linear probes confirming spurious feature reliance
- Detection: Compare WGA decline with spurious feature probe accuracy increase
- Response: If mismatch, add linear probe accuracy as secondary DV

**R2 (Detection Method Failure):**
- Prevention: Use multiple smoothing windows, report signal-to-noise ratio
- Detection: Track peak significance across seeds (5 seeds per benchmark)
- Response: PIVOT to gradient-based detection if second derivative fails

**R3 (Smoothing Window Sensitivity):**
- Prevention: Run sensitivity analysis with windows {3, 5, 7} epochs
- Detection: Compare peak timing variance across windows
- Response: Report window-robust findings only (consistent across 3+ windows)

**R4 (Architecture Specificity):**
- Prevention: Include ViT-B/16 as secondary architecture from start
- Detection: Compare crystallization timing ResNet vs ViT
- Response: If architecture-specific, scope claim to CNN family

**R5 (Benchmark Representativeness):**
- Prevention: Use 3 diverse benchmarks with different spurious correlation types
- Detection: Track effect size variance across benchmarks
- Response: If inconsistent, report benchmark-specific patterns

### 4.4 Risk Summary

| Priority | ID | Risk | Mitigation Status |
|----------|----|----- |-------------------|
| 1 | R2 | Detection method failure | Sensitivity analysis planned |
| 2 | R1 | WGA proxy validity | Linear probe validation included |
| 3 | R3 | Smoothing window sensitivity | Multi-window analysis planned |
| 4 | R4 | Architecture specificity | ViT experiment included |
| 5 | R5 | Benchmark representativeness | 3 benchmarks planned |

**Risk Counts:** Critical: 1, High: 1, Medium: 2, Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency DAG

```
═══════════════════════════════════════════════════════════
     DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    ┌─────────────────────────────────────┐
    │  H-E1: Crystallization Zone Exists  │  ← MUST_WORK
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 1 - Mechanism]
    ┌─────────────────────────────────────┐
    │  H-M1: Self-Reinforcing Feedback    │  ← MUST_WORK
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Mechanism]
    ┌─────────────────────────────────────┐
    │  H-M2: Classifier Commitment        │  ← MUST_WORK
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Detection]
    ┌─────────────────────────────────────┐
    │  H-M3: Second Derivative Method     │  ← MUST_WORK
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 4 - Generalization]
    ┌─────────────────────────────────────┐
    │  H-M4: Benchmark-Relative Timing    │  ← SHOULD_WORK
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All hypotheses sequential (no parallelization)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|------------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Core Mechanism |
| 2 | H-M2 | H-M1 | MUST_WORK | Core Mechanism |
| 3 | H-M3 | H-M2 | MUST_WORK | Detection |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Generalization |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Week 1  │ Week 2  │ Week 3  │ Week 4  │
──────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation   │         │         │         │         │
  H-E1                │ ████████│████████ │         │         │
  [Gate 1]            │         │       ◆ │         │         │
──────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms   │         │         │         │         │
  H-M1                │         │         │████████ │         │
  H-M2                │         │         │    ████ │████     │
  [Gate 2]            │         │         │         │   ◆     │
──────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 3: Detection    │         │         │         │         │
  H-M3                │         │         │         │████████ │
  H-M4                │         │         │         │    ████ │
  [Gate 3]            │         │         │         │       ◆ │
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  │  ◆ = Gate decision point
Total Duration: 4 weeks
═══════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration:** 4 weeks
- Formula: 1 week (H-E1) + 2 weeks (H-M1, H-M2) + 1 week (H-M3, H-M4)

**Slack Available:** 0 weeks (all sequential, no parallelization)

**Gate Decision Points:**
- Gate 1 (Week 2): H-E1 must demonstrate crystallization zone
- Gate 2 (Week 3-4): Core mechanism established
- Gate 3 (Week 4): Detection method validated

### 5.5 Resource Summary

| Resource | Allocation |
|----------|------------|
| **Compute** | 3x GPU for parallel benchmark training |
| **Datasets** | Waterbirds, CelebA, ColoredMNIST (WILDS) |
| **Models** | ResNet-50 (primary), ViT-B/16 (generality) |
| **Seeds** | 5 random seeds per benchmark for statistical power |

**Training Runs Required:**
- 3 benchmarks × 5 seeds = 15 runs for H-E1
- Same runs provide data for H-M1 through H-M4
- ViT-B/16: 3 benchmarks × 3 seeds = 9 additional runs

### 5.6 Execution Order

1. **Week 1-2:** Execute H-E1 (Foundation)
   - Train ResNet-50 on all 3 benchmarks with dense checkpointing
   - Compute WGA curves and second derivatives
   - **Gate 1:** Significant negative d²WGA/dt² peak detected?

2. **Week 3:** Execute H-M1, H-M2 (Core Mechanisms)
   - Analyze gradient ratios from H-E1 training runs
   - Apply linear probes to frozen embeddings
   - **Gate 2:** Mechanism confirmed?

3. **Week 4:** Execute H-M3, H-M4 (Detection & Generalization)
   - Run sensitivity analysis on smoothing windows
   - Normalize timing across benchmarks
   - **Gate 3:** Detection method robust?

4. **Completion:** Document findings, prepare for Phase 5 baseline comparison

---

## 6. Dialectical Analysis

### 6.1 Overview

This section evaluates the main hypothesis against the null hypothesis (H0) using a Thesis-Antithesis-Synthesis framework. The goal is balanced evaluation that anticipates challenges before verification begins.

### 6.2 Thesis

**Core Claim:** Under standard SGD training on spurious-correlation benchmarks, there exists a localized training phase (the "Shortcut Crystallization Zone") where classifier reliance on spurious features accelerates, detectable via second-derivative analysis of worst-group accuracy.

**Supporting Evidence:**
1. Simplicity bias (Shah 2020) establishes DNNs prefer linearly-separable features early in training
2. Gradient starvation (Pezeshki 2021) provides mechanism for feature dominance amplification
3. Both spurious and core features learned (Kirichenko 2023) but classifier weights favor spurious

**Strengths:**
- Builds on well-established theoretical foundations
- Proposes clear, measurable detection method (d²WGA/dt²)
- Testable across multiple benchmarks with falsifiable predictions

**Expected Outcomes:**
- Primary: Significant negative d²WGA/dt² peak in first 50% of training
- Secondary: Peak timing consistent at 20-40% across benchmarks
- Tertiary: Effect persists under constant learning rate (not LR artifact)

### 6.3 Antithesis

**Null Hypothesis (H0):** There is no localized acceleration in worst-group accuracy decline during training. The decline rate is constant throughout training (linear decay pattern), and no statistically significant negative peak exists in the second derivative of WGA.

**Counter-Arguments:**
1. WGA decline may be smooth and gradual, with no phase transition
2. Second derivative may be too noisy for reliable detection
3. Any apparent "peak" may be learning rate schedule artifact, not intrinsic

**Potential Failure Points:**
- R1: WGA may not accurately reflect spurious feature reliance
- R2: 5-epoch smoothing may obscure or create false signals
- R4: Effect may be ResNet-specific, not generalizing to ViT

**Conditions Under Which H0 Would Be Supported:**
- If d²WGA/dt² shows no significant peak (p ≥ 0.05)
- If peak location varies randomly across seeds/benchmarks
- If constant LR experiment shows same pattern as decay (LR confound)

### 6.4 Synthesis

**Balanced Assessment:**

The hypothesis H-ShortcutCrystallization-v1 presents a testable claim about temporal dynamics of spurious feature learning. The thesis is supported by established literature on simplicity bias and gradient starvation. However, the null hypothesis raises valid concerns: the transition may be gradual rather than localized, and the detection method may be sensitive to noise or confounded by learning rate schedules.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Tests existence before mechanism claims
2. **Sequential mechanism testing (H-M1-M4):** Validates causal chain step-by-step
3. **Gate conditions:** MUST_WORK gates on H-E1, H-M1-M3 allow early H0 support detection
4. **Sensitivity analysis:** Multi-window smoothing and constant LR control distinguish true signal from artifacts

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1 through H-M3)
- Significant negative d²WGA/dt² peak in 2/3 benchmarks
- Effect persists under constant LR

**Conditions for Antithesis Support:**
- H-E1 fails: No significant peak detected
- H-M3 fails: Detection method unreliable (high variance across seeds/windows)
- Constant LR experiment shows no effect (crystallization is LR artifact)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Crystallization zone validated, temporal characterization established
2. **Partial Support:** H-E1/H-M1-M2 pass but H-M4 fails → Phenomenon exists but timing is benchmark-specific
3. **Weak Form:** Peak exists but gradual → "Accelerating regime" rather than sharp phase transition
4. **No Support:** H-E1 fails → WGA decline is constant, no crystallization phenomenon

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Crystallization zone exists | May be noise artifact | H-E1 with p<0.05 threshold across 5 seeds |
| Mechanism | Gradient starvation causes feedback | Alternative explanations (LR schedule) | Constant LR control experiment |
| Detection | d²WGA/dt² is robust detector | Sensitive to smoothing choice | Multi-window sensitivity analysis |
| Timing | 20-40% of training | Varies by benchmark | H-M4 tests normalized timing |
| Generalization | Applies across architectures | ResNet-specific | ViT-B/16 included in scope |

**Overall Robustness Score:** Medium-High

The verification plan includes multiple safeguards against false positives:
- Statistical testing (p<0.05) across multiple seeds
- Sensitivity analysis for methodological choices
- Control experiments for LR confound
- Multi-benchmark replication

**Confidence in Verification Plan:** 0.75 (from Phase 2A)

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Shortcut Crystallization Zone — localized training phase where spurious feature reliance accelerates
- ID: H-ShortcutCrystallization-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available, 60% scope reduction)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 3 phases over 4 weeks
- Critical Gates: 3 decision points (all MUST_WORK except H-M4)

**Risk Assessment:** Medium
- Primary concerns: Detection method sensitivity (R2), smoothing window choice (R3)

**Immediate Action:** Begin Phase 1 with H-E1 — train ResNet-50 on all 3 benchmarks

### 7.2 Final Summary

**Verification Plan Scope:**
- Tests 2 PROVE_NEW claims (crystallization existence, detection method)
- Builds on 3 established facts (simplicity bias, gradient starvation, feature learning)
- Covers 3 benchmarks (Waterbirds, CelebA, ColoredMNIST)
- Uses 2 architectures (ResNet-50 primary, ViT-B/16 generality)

**Execution Path:**
1. H-E1 → H-M1 → H-M2 → H-M3 → H-M4 (sequential)
2. All MUST_WORK gates must pass for full validation
3. Phase 5 baseline comparison deferred (ERM, Group DRO, JTT)

### 7.3 Conclusions

**Key Achievements:**
- 5 hypotheses across 3 phases with clear verification protocols
- Dialectical analysis addresses H0: linear decay (no crystallization)
- Risk mitigations planned for all 5 key assumptions

**Critical Decision Points:**
1. Gate 1: H-E1 pass → phenomenon exists; fail → STOP
2. Gate 2: H-M1-M2 pass → mechanism confirmed; fail → EXPLORE alternatives
3. Gate 3: H-M3-M4 pass → detection robust; fail → document limitations

**Open Questions (from Phase 2A):**
- Optimal smoothing window (sensitivity analysis planned)
- Extension to NLP domain (CivilComments deferred)
- Whether crystallization is sharp transition or gradual regime shift

**Recommendations:**
1. Immediate: Start H-E1 training with dense checkpointing (every epoch)
2. Resources: 4 weeks critical path, 3 GPUs for parallel benchmark training
3. Failure: Document all failures, execute PIVOT strategies per hypothesis

### 7.4 Appendices

**A. Phase 2A Reference:**
- Source: 03_refinement.yaml (H-ShortcutCrystallization-v1)
- Synthesis: 02_synthesis.yaml (measurement plan, validation strategy)

**B. Experiment Configuration:**
- Datasets: WILDS (Waterbirds, CelebA), custom loader (ColoredMNIST)
- Models: torchvision.models.resnet50(pretrained=True), timm ViT-B/16
- Seeds: 5 per benchmark for statistical power
- Checkpoints: Every epoch for dense WGA tracking

---

## 8. Verification State

**Status:** COMPLETE

**Pipeline Tasks Updated:** Phase 2B marked complete; Phase 2C ready

**Hypothesis Tasks Created:** 5 tasks (H-E1, H-M1, H-M2, H-M3, H-M4)

**State File:** verification_state.yaml generated for Phase 2C integration

---

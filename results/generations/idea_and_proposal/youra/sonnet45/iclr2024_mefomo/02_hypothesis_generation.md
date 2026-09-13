# Phase 2A Extended: Hypothesis Clarification (Summary)

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MEFOMO-01-SNR-EMERGENCE

**Confidence Level:** 0.74/1.0

**Main Hypothesis:**

*"If we monitor the signal-to-noise ratio (SNR) trajectory in task-relevant representational subspaces during foundation model training, then we can predict capability emergence thresholds BEFORE they occur (with >70% accuracy at lead times of 10-20% remaining training), because capability emergence corresponds to crossing critical SNR thresholds that exhibit characteristic pre-critical scaling patterns analogous to phase transitions in statistical mechanics."*

**Alternative Hypothesis (H0):**

*"SNR trajectory monitoring does NOT provide predictive power beyond random chance or simple compute-based scaling law extrapolation."*

### 1.2 Variables

| Variable Type | Name | Measurement | Expected Range |
|--------------|------|-------------|----------------|
| **Independent** | Training Scale | FLOPs or tokens | 10^19 - 10^24 FLOPs |
| **Independent** | Intervention Type | Categorical: baseline/finetuning | N/A |
| **Dependent** | SNR in Task Subspace | $\frac{\sigma^2_{signal}}{\sigma^2_{residual}}$ | 0.1 - 100 |
| **Dependent** | Capability Emergence | Binary: >50% accuracy | 0 or 1 |
| **Dependent** | SNR Growth Rate | $\frac{d(SNR)}{d(FLOPs)}$ | 10^-21 - 10^-19 |
| **Controlled** | Architecture | GPT/LLaMA family | N/A |
| **Controlled** | Hyperparameters | Learning rate, batch size | Standard ranges |

### 1.3 Causal Mechanism

**Mechanism Chain:**
Training → Representational Learning → SNR Increase → Pre-Critical Signatures → Critical Threshold Crossing → Phase Transition → Capability Emergence

**Evidence for Causal Links:**
- Training → SNR: Empirically validated (Luo 2024)
- SNR → Emergence: Threshold correlation (Luo 2024)
- Phase Transition Framework: Mathematical reformulation (Sun & Haghighat 2025)
- Finetuning Effects: Predictable modulation (Snell 2024)

**Key Tension:**
- **Empirical (STRONG):** SNR thresholds exist and correlate with emergence
- **Theoretical (WEAK):** Phase transitions/bistability explain WHY
- **Resolution:** Core prediction framework stands independently of mechanism validation

### 1.4 Key Assumptions

**Critical:**
- **A1:** Task-relevant subspaces remain stable during training (Testable: cosine similarity >0.7)
- **A2:** Subspaces identifiable pre-emergence via transfer/probing (RISK: Circular dependency)
- **A3:** SNR exhibits predictive trajectories, not random walk (Core claim - must validate)

**Secondary:**
- **A4:** Phase transition analogy valid (Affects theory, not core prediction)
- **A5:** Thresholds consistent within architecture (±15%)
- **A6:** Bistable attractors underlie emergence (SPECULATIVE)

### 1.5 Scope & Boundaries

**Applies To:**
- Transformer-based LLMs (GPT, LLaMA families)
- Emergent capabilities: ICL, reasoning, chain-of-thought, instruction-following
- Pre-training and finetuning stages
- Models 1B-100B+ parameters

**Does NOT Apply To:**
- Gradually emerging capabilities (no sharp threshold)
- Architectural properties (present from initialization)
- Non-transformer architectures (unvalidated transfer)

**Key Limitations:**
1. Subspace identification before emergence is challenging (HIGH PRIORITY)
2. Computational cost: 5-10% training overhead (MEDIUM)
3. Longitudinal validation delays (MEDIUM)
4. Mechanism uncertainty (affects theory, not utility)

### 1.6 Testable Predictions

**P1 (Primary): Forecasting Accuracy**
*At 70% training, predict emergence timing with >70% accuracy (±10% of total training), outperforming scaling laws by >15 percentage points.*

**P2: Threshold Consistency**
*Critical SNR thresholds vary <30% within architecture family (5+ models).*

**P3: Finetuning Acceleration**
*SNR growth rate change correlates with emergence shift (r >0.6).*

**P4: Pre-Critical Signatures**
*Power-law scaling $SNR(t) \propto (t_c - t)^{-\alpha}$ detectable in >60% of emergence events.*

**P5: Cross-Capability**
*Prediction accuracy >60% for at least 2 out of 3 capability types tested.*

**Falsification Criteria:**
- **Strong:** Accuracy <50%, no pre-critical patterns, threshold variation >50%
- **Weak:** Accuracy 50-65%, limited capability coverage
- **Partial:** Mechanism fails but prediction works (supports core, invalidates theory)

### 1.7 Statistical Verification Design

**Study:** Prospective prediction validation
- **Sample:** 15 training runs (3 architectures × 5 runs)
- **Capabilities:** ICL, reasoning, instruction-following
- **Procedure:** Track SNR 0-70%, predict at 70%, validate 70-100%

**Primary Test:** MAPE < 10% (one-sample t-test, n=15, power=80%)

**Baseline Comparison:** SNR vs scaling law extrapolation (paired t-test, Cohen's d >0.8)

**Success Tiers:**
- **Tier 1:** P1 + P2 + P4 all pass (strong success)
- **Tier 2:** P1 + (P2 OR P4) (moderate success)
- **Tier 3:** P1 only (minimal success - prediction works)

---

## 2. Contribution Summary

**Theoretical:**
- Unifies SNR observations (Luo 2024) with phase transition framework (Sun & Haghighat 2025)
- Proposes SNR as order parameter; bistable attractors as emergence mechanism
- Extends statistical mechanics framework to specific capability emergence events

**Methodological:**
- **SNR Trajectory Analysis:** Pre-emergence forecasting (vs post-hoc threshold identification)
- **Pre-Emergence Subspace Identification:** 3 methods (transfer, synthetic probing, cross-capability)
- **Standardized SNR Protocol:** Reproducible measurement across layers, checkpoints

**Practical:**
- **Training Optimization:** Predict emergence; decide continue/stop/intervene
- **Timeline Forecasting:** Deployment planning with reliable capability roadmaps
- **Targeted Acceleration:** Quantitative finetuning design to shift emergence timing
- **Safety Control:** Early warning for emergence; proactive alignment interventions

**ROI Estimate:** $50k SNR analysis overhead saves $150k on failed training runs (3x ROI)

---

## 3. Key Related Work

**Foundation (Direct Build-On):**

1. **Luo 2024** (d04c62a9f04525c5dde3a205dfb45752b7ade143): SNR thresholds exist
   - *Our Extension:* Post-hoc → Pre-emergence prediction

2. **Sun & Haghighat 2025**: Phase transitions in LLMs (O(N) model)
   - *Our Extension:* General framework → Specific capability emergence

3. **Snell 2024** (3d6f4c281bd3c95a40f67393d668910ea190ce5a): Finetuning shifts emergence
   - *Our Extension:* Empirical observation → Quantitative mechanism (SNR modulation)

**Cross-Domain:**
- Boolean Networks (2023): Topology → dynamics prediction (inspired subspace approach)
- Biological Bistability (2022): Sudden state changes (speculative mechanism)

**Gaps Addressed:**
1. Pre-emergence prediction (literature: post-hoc only)
2. Mechanistic explanation (literature: emergence "mysterious")
3. Quantitative intervention design (literature: qualitative finetuning effects)
4. Unified empirical-theoretical framework

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):** SNR-emergence correlation validation (post-hoc analysis)
- **Complexity:** LOW | **Dependencies:** None

**SH2 (Predictive Power):** Trajectory forecasting >70% accuracy
- **Complexity:** HIGH | **Dependencies:** SH1 must pass

**SH3 (Mechanism):** Phase transition signatures (power-law, bistability)
- **Complexity:** MEDIUM-HIGH | **Dependencies:** SH1; SH2 provides timing
- **Modular:** Can fail while SH2 succeeds (prediction works, mechanism wrong)

**SH4 (Generalizability):** Cross-architecture, cross-capability validation
- **Complexity:** HIGH | **Dependencies:** SH2 must pass

**SH5 (Intervention):** Finetuning predictability (SNR ↔ emergence shift)
- **Complexity:** MEDIUM | **Dependencies:** SH2 baseline

### Readiness Checklist

✅ **READY:**
- [x] Core hypothesis well-defined (If-Then-Because structure)
- [x] Variables operationalized with measurement protocols
- [x] Testable predictions with falsification criteria
- [x] Evidence base established (Luo, Sun & Haghighat, Snell)
- [x] Sub-hypothesis decomposition defined (SH1-SH5)

⚠️ **PARTIAL:**
- [x] Subspace identification challenge articulated; 3 methods proposed (NOT validated)
- [x] Resource requirements estimated (~$50k); availability NOT confirmed

### Open Questions

**Q1 (HIGH PRIORITY):** Which subspace identification method works best?
- **Addressable in Phase 2B:** YES - Design comparison experiment

**Q2:** Optimal checkpoint frequency? (Accuracy vs cost trade-off)
- **Addressable in Phase 2B:** Partially via simulation

**Q3:** Prevalence of phase transition signatures?
- **Addressable in Phase 2B:** NO - Requires Phase 4 empirical data

**Q4 (HIGH PRIORITY):** Capability taxonomy - which types in-scope?
- **Addressable in Phase 2B:** YES - Literature review + prioritization

**Q7 (BLOCKER):** Which scaling law baseline for comparison?
- **Addressable in Phase 2B:** YES - Literature review + implementation plan

**Q8 (BLOCKER):** Existing emergence prediction methods for comparison?
- **Addressable in Phase 2B:** YES - SOTA search

---

## Summary for Phase 2B Planning

**One-Sentence Hypothesis:**
Monitor SNR trajectories in task-relevant subspaces to forecast capability emergence 10-20% of training in advance with >70% accuracy, treating emergence as phase transition with predictable critical thresholds.

**Verification Roadmap:**
Phase 2B (Decomposition) → Phase 3 (Experiment Design) → Phase 4 (Validation: SH1→SH2→SH3/SH4/SH5) → Phase 5 (Paper)

**Success Criteria:**
- **Minimum (Tier 3):** SH1 + SH2 basic (>65% accuracy)
- **Target (Tier 2):** SH1 + SH2 strong (>70%) + (SH3 OR SH4) partial
- **Aspirational (Tier 1):** SH1 + SH2 + SH3 + SH4 all pass

**Critical Risks:**
1. **HIGH:** Subspace identification fails → Hypothesis untestable
   - *Mitigation:* Three methods; accept post-hoc if necessary
2. **HIGH:** SNR trajectories are random → No predictive power
   - *Mitigation:* Explore alternative signals

**Phase 2C Transition Requirements:**
- Resolve Q1, Q4, Q7 (subspace method, capability selection, baseline)
- Confirm compute resources OR define pilot scale
- Accept SH1-SH5 decomposition structure

---

**Full Document:** See `02a_extended_hypothesis_full.md` for complete details (90+ pages)

**Status:** ✅ COMPLETE - Ready for Phase 2B

**Next Action:** Initiate `/phase2b-planning` with this clarified hypothesis

---

*Generated: 2026-02-08*
*YouRA Phase 2A Extended Workflow (YOLO Batch Mode)*
*Task: iclr2024_mefomo*
*Confidence: 0.74/1.0 (FEASIBLE)*

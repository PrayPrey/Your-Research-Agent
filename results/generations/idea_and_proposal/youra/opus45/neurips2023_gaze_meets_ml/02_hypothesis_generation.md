# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GazePC-v1
**Confidence Level:** 0.87

**Main Hypothesis:**
Under conditions of 60Hz+ eye tracking with visual target tasks, if a hierarchical predictive coding architecture continuously predicts gaze trajectories (x,y,duration), then accumulated prediction errors crossing adaptive thresholds will detect intent changes within 50ms, because gaze patterns are anticipatory of intended actions (300-800ms before execution) and prediction errors signal deviations from expected behavioral sequences.

**Alternative Hypothesis (H0):**
Accumulated gaze prediction errors do not correlate with actual intent changes, and a predictive coding approach provides no advantage over classification-based intent detection methods in terms of detection latency or anticipation window.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Gaze trajectory sequence | Independent | (x,y) fixation coordinates and duration sampled at 60Hz from eye tracker | Continuous stream at 16.7ms intervals |
| Intent detection latency | Dependent | Time (ms) from actual intent change to system detection, measured via ground truth labels | Target: <50ms |
| Intent prediction accuracy | Dependent | F1 score comparing detected intent changes to ground truth annotations | Target: >0.85 |
| Anticipation window | Dependent | Time (ms) between intent detection and action execution | 300-800ms |
| Eye tracker resolution | Controlled | Fixed minimum sampling rate | 60Hz+ |
| Task type | Controlled | Visual target tasks | Manipulation, navigation, selection in XR |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
[Gaze trajectory @ 60Hz]
    → [Temporal Transformer Encoder]
    → [Next-step Gaze Prediction (x,y,duration)]
    → [Prediction Error Accumulation]
    → [Intent Change Detection]
```

**Step 1: Gaze Input → Transformer Encoder**
- Mechanism: Continuous gaze sampling provides sufficient temporal resolution for trajectory modeling
- Evidence: GazeIntent 2024 achieved F1=0.94 with gaze-based ML models

**Step 2: Transformer Encoder → Gaze Prediction**
- Mechanism: Self-attention captures temporal dependencies in sequential gaze patterns
- Evidence: Gornet & Thomson 2024 demonstrated predictive coding with self-attention for sensory streams

**Step 3: Prediction + Actual → Error Accumulation**
- Mechanism: Difference between predicted and actual gaze indicates deviation from expected behavior
- Evidence: Core predictive coding principle (Rao & Ballard 1999)

**Step 4: Error Threshold → Intent Detection**
- Mechanism: Sustained prediction errors above adaptive threshold indicate behavioral regime change
- Evidence: CogDPM 2024 precision weighting mechanism

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Gaze → Transformer | GazeIntent 2024 | F1=0.94 for gaze-based intent prediction | Strong |
| Transformer → Prediction | Gornet & Thomson 2024 | Predictive coding with self-attention works for sensory streams | Strong |
| Prediction → Error | Predictive Coding Theory | Foundational principle validated across domains | Strong |
| Error → Intent | CogDPM 2024 | Precision weighting allocates attention to prediction errors | Medium |

**Key Tension:**
- Tension: Belardinelli 2023 reports 300-800ms anticipation window, but Jo 2025 Bayesian model achieves only marginal anticipation
- Resolution: This verification plan tests whether prediction error accumulation (vs. classification) is the key mechanism enabling sustained anticipation advantage

### 1.4 Key Assumptions

1. **Gaze anticipates intended actions by 300-800ms**
   - Evidence: Belardinelli 2023 (52 citations) - comprehensive review of visuomotor control
   - Consequence if violated: Anticipation advantage claim fails; reduces to reactive system

2. **Prediction errors in gaze trajectory correlate with actual intent changes**
   - Evidence: Predictive coding theory + CogDPM 2024 precision weighting
   - Consequence if violated: False positive rate too high for practical use

3. **Lightweight transformer (4 layers, 256 dim) can achieve <50ms inference**
   - Evidence: Standard transformer benchmarks on RTX 3080
   - Consequence if violated: Real-time requirement not met; need architecture optimization

4. **Self-supervised pre-training on GazeCapture transfers to intent prediction**
   - Evidence: Transfer learning literature; GazeCapture (1.5M images) provides diverse gaze patterns
   - Consequence if violated: Requires large labeled intent datasets (high annotation cost)

### 1.5 Scope & Boundaries

**Applies to:**
- Tasks with visual targets (object manipulation, navigation, selection)
- Real-time human-AI collaboration scenarios (HRI, XR interaction, assistive robotics)
- 60Hz+ eye tracking systems
- Adult users with normal or corrected vision

**Does NOT apply to:**
- Non-visual tasks (auditory, haptic-only interaction)
- Tasks without clear intent-gaze relationship (e.g., mind-wandering)
- Low-resolution eye tracking (<30Hz)
- Users with atypical gaze patterns (certain neurological conditions)

**Known Limitations:**
- Individual variability in gaze patterns may require per-user calibration
- Task-specific fine-tuning likely needed for optimal performance
- Multi-intent scenarios (concurrent goals) not explicitly addressed

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Intent Detection Latency Target):**
Our GazePC approach will achieve intent detection latency <50ms with F1 >0.85

*Measurement*:
- Latency: Time from ground-truth intent change to system detection (ms)
- Accuracy: F1 score on intent change detection vs. ground truth
- Statistical test: Mean +/- SD across 30+ test sessions, p < 0.05

*Basis*:
Domain standard for real-time HCI systems requires <100ms latency. Our target of <50ms provides margin for system integration overhead.

*Success Criteria for Phase 2B*:
- Primary: Latency <50ms AND F1 >0.85 (p < 0.05)
- Falsification: Latency >100ms OR F1 <0.70 triggers rejection

**Secondary Predictions:**

**P2 (Anticipation Window Preservation):**
GazePC will maintain 300-800ms anticipation window (time between intent detection and action execution)

**P3 (Prediction Error Correlation):**
Accumulated prediction error will correlate with actual intent changes (Pearson r > 0.6)

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Latency >100ms OR F1 <0.70
2. **Mechanism Failure**: Prediction error does not correlate with intent changes (r < 0.3)
3. **Baseline Failure**: No improvement over Bayesian classification baseline (Jo 2025)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected for paradigm shift)
- Required runs: n >= 30 sessions
- Statistical power: 0.8

**Test Specification:**
- Method: Independent samples t-test (vs. baseline), paired t-test (ablations)
- Significance level: alpha = 0.05 (two-tailed)
- Report format: Mean +/- SD, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does gaze-based intent detection with <50ms latency and F1>0.85 exist under 60Hz eye tracking with visual target tasks?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is hierarchical predictive coding the actual mechanism enabling real-time intent detection from gaze?"
- Maps to: Causal mechanism (4 sub-hypotheses)
  - H-M1: Gaze input at 60Hz provides sufficient resolution for trajectory modeling
  - H-M2: Temporal transformer captures anticipatory gaze patterns
  - H-M3: Prediction error correlates with intent changes
  - H-M4: Adaptive threshold enables robust detection across users/tasks
- Verification type: Causal analysis (ablation studies)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does GazePC outperform Bayesian classification baselines (Jo 2025) in anticipation window and detection latency?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value of paradigm shift

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GazePC-v1
- [x] Confidence level specified: 0.87
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table provided)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2, P3 secondary)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison (Jo 2025, Xu 2023)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Does a suitable gaze-intent dataset exist with ground-truth intent labels, or will data collection be required?

2. **Per-User Calibration:** How much user-specific calibration is needed for the adaptive threshold mechanism?

3. **Multi-Task Generalization:** Can a single pre-trained model generalize across task types (manipulation, navigation, selection), or are task-specific fine-tuning required?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*

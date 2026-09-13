# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-19T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: No Benchmark Task Directionality Classification Exists
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met - SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed

### Key Insights
- Reframe existing benchmarks rather than building new ones
- Use behavioral signals (calibration inversion) to detect bidirectional tasks
- RLHF reward conflation mechanism explains systematic blindspots
- Empirical clustering discovers differentiating features rather than defining a priori

### Breakthrough Moments
- Exchange 7: Dr. Nova proposes empirical clustering to discover features instead of pre-defining them
- Exchange 9: Dr. Sage articulates theoretical contribution through reward conflation mechanism
- Exchange 11: Dr. Ally synthesizes complete hypothesis with variables and predictions
- Exchange 14: Prof. Vera formalizes full experimental protocol

---

## Final Hypothesis

### Title
Calibration Inversion as Behavioral Marker for Bidirectional Task Classification (H-BiDir-Cal-v1)

### Core Claim
Under existing RLHF benchmarks (TruthfulQA, ETHICS, HHH), if we cluster tasks by calibration inversion patterns (where models show high confidence on incorrect answers), then these clusters will correlate significantly with theoretically-expected bidirectional task features (r > 0.4), because RLHF's reward modeling conflates "correct output" with "user-state-modeling-required output."

### Mechanism
1. RLHF training optimizes models for annotator approval signals
2. Annotator approval conflates "correct answer" with "answer requiring user-state modeling"
3. Models learn single reward signal for both dimensions, missing bidirectional nuance
4. On tasks requiring bidirectional adaptation, models show miscalibrated confidence (calibration inversion)

---

## Predictions

| ID | Statement | Success Criterion |
|----|-----------|-------------------|
| **P1** (Primary) | Tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) will cluster non-randomly | Silhouette score > 0.3 |
| **P2** | Inversion cluster tasks will score higher on bidirectional feature checklist than non-inversion tasks | Cohen's d > 0.3, r > 0.4 |
| **P3** | Correlation survives controlling for topic, length, format, and difficulty | Partial r > 0.3 after controls |

---

## Novelty

**Key Innovation**: First empirical method to classify benchmark tasks by bidirectionality using behavioral signals (calibration inversion) rather than manual annotation.

**Differentiation from Prior Work**:
- Shen et al. 2024: Established theoretical bidirectional framework but left task classification unsolved
- Standard RLHF evaluation: Reports aggregate accuracy without task-type stratification
- Our contribution: Operationalizes bidirectionality via automated behavioral analysis

---

## Experimental Design

### Datasets
- TruthfulQA (817 tasks)
- ETHICS justice subset (~500 tasks)
- HHH single-turn (~200 tasks)

### Models
- Llama-2-7B-Chat
- Llama-2-13B-Chat
- Mistral-7B-Instruct

### Baselines
- Random stratification (null comparison)
- Topic-based stratification (alternative stratification)

### Pre-Registered Bidirectional Features
1. Task mentions "you" or implies user beliefs (linguistic)
2. Correct answer varies by context (structural)
3. Expected answer contains hedges/uncertainty (output)

---

## Limitations

- Cross-model generalization limited to open RLHF models with logprob access
- Feature extraction is text-based only (no multimodal)
- May not capture all forms of bidirectionality
- Feature base rates must be validated (20-80% range) before main analysis

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (mitigations defined for all concerns) |

---

## Phase 2B Readiness

| Sub-Hypothesis | Description |
|----------------|-------------|
| **SH1-Existence** | Calibration inversion patterns exist systematically in RLHF models |
| **SH2-Mechanism** | Reward signal conflation explains calibration inversion on bidirectional tasks |
| **SH3-Comparison** | Calibration-based stratification outperforms baselines (Phase 5) |

**Status**: READY for Phase 2B verification planning

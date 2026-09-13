# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap1
- **Gap Title**: No Systematic Cross-Benchmark Correlation Study
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Truthfulness and robustness may share underlying mechanism (uncertainty estimation)
- Calibration (ECE) could be the unifying factor enabling both capabilities
- Reframing from "trade-off" to potential "synergy" for well-calibrated models

### Breakthrough Moments
- Dr. Nova's calibration-mediation hypothesis
- Prof. Vera's sharp falsification criteria (r > 0.3, p < 0.05)
- Prof. Rex's identification of ECE domain concern (resolved by using MMLU)

---

## Final Hypothesis

### Title
Calibration-Mediated Correlation Between Truthfulness and Adversarial Robustness in LLMs

### Core Claim
Under controlled evaluation conditions (lm-eval-harness, consistent settings), if we measure TruthfulQA MC1 accuracy and AdvGLUE average accuracy across 15+ LLMs from multiple families (Llama, Mistral, Pythia, Falcon), then we will observe a significant positive partial correlation (r > 0.3, p < 0.05) after controlling for model size, because both capabilities rely on accurate uncertainty estimation that calibration enables.

### Mechanism
1. Calibration (ECE) reflects model's ability to estimate its own uncertainty
2. Good uncertainty estimation → refuse to hallucinate (truthfulness)
3. Good uncertainty estimation → detect anomalous inputs (robustness)
4. Therefore, calibration is a common cause of both capabilities

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Partial correlation r > 0.3 between TruthfulQA and AdvGLUE | r > 0.3, p < 0.05, bootstrap CI excludes 0 | \|r\| < 0.2 and p > 0.1 |
| P2 | Correlation stronger in low-ECE models | Low-ECE r > High-ECE r (z-test p < 0.05) | No significant difference |
| P3 (Exploratory) | Pareto-optimal models have lower ECE | t-test p < 0.05 | Similar ECE across groups |

---

## Novelty

**Key Innovation**: First systematic correlation + calibration-mediation analysis between truthfulness and robustness in LLMs.

**Differentiation from Prior Work**:
- TruthfulQA (Lin et al. 2022): Evaluated truthfulness only
- AdvGLUE (Wang et al. 2022): Evaluated robustness only
- Calibrate Before Use (Zhao et al. 2021): Calibration helps performance, not trust dimension interaction

---

## Experimental Design

**Models**: 18-20 public LLMs
- Pythia suite (70M to 12B, 8 sizes)
- Llama-2 (7B/13B/70B, base + chat, 6 variants)
- Mistral-7B (base + instruct, 2-3 variants)
- Falcon (7B/40B, 2 variants)

**Benchmarks**:
- TruthfulQA (MC1 format) for truthfulness
- AdvGLUE (average across subtasks) for robustness
- MMLU (for ECE calculation on neutral benchmark)

**Evaluation**: lm-evaluation-harness with consistent settings

---

## Limitations

- Sample size (N~20) limits statistical power; effect sizes will have wide CIs
- AdvGLUE subtask heterogeneity may mask task-specific patterns
- Correlation does not establish causation (exploratory study)
- ECE reliability depends on consistent implementation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all mitigated) |

---

*Phase 2A Complete | Ready for Phase 2B*

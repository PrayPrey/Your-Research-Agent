# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-18T13:45:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1_robustness_error_detection
- **Gap Title**: Robustness-Error Detection Correlation Quantification
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
- Calibration quality (ECE) serves as the theoretical bridge connecting factuality and robustness
- Temperature scaling provides a quasi-causal intervention test
- Within-family analysis is crucial for controlling training data confounds

### Breakthrough Moments
- Exchange 3: Prof. Pax proposed calibration as the mediating mechanism
- Exchange 7: Dr. Nova introduced three-level hypothesis structure (behavioral, mechanistic, representational)
- Exchange 11: Prof. Rex's intervention request led to inclusion of temperature scaling test

---

## Final Hypothesis

### Title
Calibration-Mediated Correlation Between Factuality and Robustness in LLMs

### Hypothesis ID
H-CalibRobust-v1

### Core Claim
Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

### Mechanism
1. **Step 1**: Calibration quality produces reliable uncertainty estimates
2. **Step 2**: Reliable uncertainty enables better error detection (knowing when wrong)
3. **Step 3**: Reliable uncertainty enables better robustness (flagging adversarial inputs)

---

## Predictions

| ID | Primary | Statement | Success Criterion | Falsification |
|----|---------|-----------|-------------------|---------------|
| P1 | Yes | Cross-model correlation r > 0.5 between TruthfulQA MC1 and (1 - ASR) | r > 0.5, p < 0.05, holds within families | r < 0.3 after scale control |
| P2 | Yes | ECE mediates > 30% of the detection-robustness correlation | Indirect effect > 30%, Sobel p < 0.05 | ECE adds < 10% R² |
| P3 | No | Temperature scaling improves both metrics | 2/3 models improve on both | No model improves on both |

---

## Novelty

**Key Innovation**: First empirical framework connecting factuality benchmarks to robustness metrics via calibration mechanism.

**Differentiation from Prior Work**:
- ARES/FactSelfCheck: Measure detection, don't connect to robustness
- TextFooler/BERT-Attack: Measure robustness, don't connect to internal calibration
- Minderer et al.: Study calibration, don't predict joint factuality-robustness

---

## Experimental Design

### Models (N ≥ 10)
- Llama-2: 7B, 13B, 70B (base + chat)
- Llama-3: 8B, 70B
- Mistral: 7B-v0.1, 7B-Instruct
- FLAN-T5: base, large, xl
- Phi-2, Phi-3-mini

### Datasets
- TruthfulQA (factuality benchmark)
- SST-2 (adversarial attack target)

### Tools
- lm-evaluation-harness (TruthfulQA evaluation)
- TextAttack (TextFooler adversarial attacks)
- scipy/statsmodels (statistical analysis)

---

## Limitations

- **Correlational nature**: Temperature scaling provides quasi-causal evidence, not true randomized experiment
- **Perturbation scope**: Limited to word-level adversarial perturbations
- **Model scope**: Limited to open-weight models with accessible logprobs
- **Language scope**: English benchmarks only

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Correlational nature, scope limitations |

---

*Phase 2A Complete - Ready for Phase 2B*

# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-24T08:58:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Direct Behavioral Probing of Enumeration Preference in Reward Models
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met: specific claim stated, mechanism explained, testable predictions with criteria, novelty articulated, technical feasibility established, major objections addressed

### Key Insights
1. Enumeration is a meta-feature (structure) not a content dimension—potentially orthogonal to helpfulness
2. Beacon feature hypothesis: high-detectability structural markers amplified during Bradley-Terry training
3. Competence proxy vs. structural encoding distinguished via correctness/completeness orthogonalization
4. Spurious enumeration control is high-value, low-cost diagnostic for token bias

### Breakthrough Moments
- **Exchange 5**: Dr. Ally reframed hypothesis as "convergent enumeration preference across RLHF-trained RMs"
- **Exchange 8**: Dr. Nova proposed "epistemic navigability" framing and structure-vs-semantics dissociation
- **Exchange 10**: Prof. Rex demanded strict operationalization, pre-registered null thresholds, and completeness manipulation
- **Exchange 12**: Prof. Vera added spurious enumeration adversarial control

---

## Final Hypothesis

### Title
Structural Enumeration Preference in RLHF-Trained Reward Models

### Core Claim
Under conditions where RLHF-trained reward models (Bradley-Terry, scalar regression, or MoE objectives) are evaluated on response pairs that differ only in structural presentation, if responses enumerate multiple options (vs. synthesize into single recommendation), then reward scores will be significantly higher for enumerated responses (Cohen's d >= 0.3), because RLHF training encodes human raters' implicit preference for option enumeration as a high-detectability structural feature that signals epistemic navigability.

### Mechanism
During RLHF training, human raters systematically prefer responses that present multiple options because such responses:
1. Reduce cognitive load
2. Make trade-offs explicit
3. Signal that the model is modeling the user's decision space

Reward models learn this preference through gradient descent on preference data, potentially amplified by the high-detectability of structural markers (numbered lists, bullet points) that provide stable training signals across noisy semantic variance.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 (Primary) | Enumerated responses receive higher reward scores | d >= 0.3 in ≥2 distinct RMs | d < 0.1 across ≥3 RMs |
| P2 | ≥75% of RMs show same-sign effects | 3/4 RMs show d > 0 | 2+ RMs show d < 0 |
| P3 | Spurious enumeration shows attenuated effects | <30% of true enumeration effect | ≥70% effect (token bias) |
| P4 | Numeric enumeration without deliberative language produces boost | d >= 0.2 vs prose baseline | Effect disappears without deliberative language |

---

## Novelty

**Key Innovation**: First rigorous behavioral probe for structural (non-content) preferences in reward models. Bridges RM interpretability literature (MRMBench) with human agency frameworks (HumanAgencyBench).

**Differentiation from Prior Work**:
- MRMBench probes content dimensions (helpfulness, harmlessness); we probe structural dimensions
- HumanAgencyBench evaluates agency support in LLM outputs; we probe agency-related preferences in RMs
- RewardBench benchmarks RM accuracy; we probe for specific structural biases

---

## Experimental Design

### Dataset
- **Name**: Custom Agency-Structure Stimulus Set v2
- **Size**: 600 stimulus pairs (75 per cell × 8 cells)
- **Design**: 2×2×2 factorial (Structure × Correctness × Completeness)

### Models
| Model | Training Objective | Source |
|-------|-------------------|--------|
| ArmoRM-Llama3-8B-v0.1 | Multi-objective MoE | RLHFlow |
| UltraRM-13b | Scalar regression | OpenBMB |
| Starling-RM-7B-alpha | Bradley-Terry | Berkeley |
| PairRM | Pairwise | LLM-Blender |

### Controls
1. **Spurious enumeration**: Markers without structural decomposition
2. **Structure-vs-semantics dissociation**: Numeric lists vs. deliberative prose
3. **Token matching**: ±2% length control
4. **Human orthogonality validation**: |d| < 0.2 cross-contamination check

---

## Limitations

1. Training data analysis limited to 2/4 models (HelpSteer, UltraFeedback)
2. Token-masking mechanistic probing relegated to exploratory follow-up (ArmoRM only)
3. Domain moderation (high-autonomy vs. low-autonomy) is exploratory, not primary hypothesis
4. Results may not generalize to closed-source or non-English models

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All convergence criteria met across 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*

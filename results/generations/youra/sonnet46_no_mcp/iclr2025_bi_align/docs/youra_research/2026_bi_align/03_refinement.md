# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-03T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Absence of Temporal Drift Measurement in RLHF Preference Datasets
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — SPECIFIC conditional causal claim, 4-step MECHANISM with falsifiers, 3 pre-registered PREDICTIONS, NOVELTY as first signed directional instrument, FEASIBILITY under 4h single GPU, OBJECTIONS addressed with concrete mitigations.

### Key Insights
- The static oracle assumption of RLHF is empirically testable using existing open datasets — no new data collection required
- Automation bias ambiguity-modulation provides a theoretically grounded boundary condition: drift is strongest in high-uncertainty prompts
- The AAI composite instrument unifies three independent measurement approaches into a single scalar, enabling future monitoring pipeline integration
- Both positive and null results advance the field — the study is informative regardless of outcome
- Component-wise criterion validity (against TruthfulQA/BBH) replaces CFA due to mixed observational levels across AAI components

### Breakthrough Moments
- **Exchange 6** (Dr. Ally): Conditional causal hypothesis — sharpened from "round causes drift" to exposure-dependent, ambiguity-modulated directional adaptation with clear boundary conditions
- **Exchange 13** (Dr. Nova): Alignment Asymmetry Index (AAI) reframes contribution from "detecting drift" to "providing a validated monitoring instrument" — dramatically strengthens impact story
- **Exchange 15** (Prof. Pax): CFA observational level mismatch identified and resolved with component-wise criterion validity

---

## Final Hypothesis

### Title
Human→AI Annotation Drift: Measuring Directional Stylistic Adaptation in RLHF Preference Datasets via the Alignment Asymmetry Index (H-AAI-v1)

### Core Claim
Under conditions of repeated RLHF annotation exposure (HH-RLHF 3-round structure; WebGPT longitudinal sessions), if human annotators have cumulative exposure to AI-generated text across annotation rounds, then their preference labels will exhibit directional stylistic drift toward AI-typical features (increased weight on verbosity, structured reasoning, hedging — measured via the Alignment Asymmetry Index AAI), because automation bias induces annotators to internalize AI stylistic norms as quality heuristics, particularly under high-ambiguity prompts where annotation uncertainty is greatest.

**H0**: After conditioning on prompt features, model checkpoint, and affine-recalibrated Q_early, stylistic preference coefficients do not change directionally across rounds beyond sampling variability or annotator cohort turnover.

### Mechanism

| Step | Description | Falsifier |
|------|-------------|-----------|
| 1 | Repeated annotation exposure internalizes AI-typical norms as quality heuristics | No coefficient drift after Q_early recalibration; drift absent in low-ambiguity prompts |
| 2 | Internalized norms cause systematic upweighting of AI-typical stylistic features in labels | Coefficients non-monotonic or sign-inconsistent; geometric projection not positive |
| 3 | Stylistic preference drift corrupts RLHF reward model training signal | No behavioral divergence between early/late RLHF models on style metrics |
| 4 | Stylistic reward bias degrades style-invariant objective benchmarks | Late-round model matches early within 1% factual accuracy; length fully mediates factual gains |

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| P1 (primary) | Stylistic coefficient drift is significantly larger in high-ambiguity prompts | Interaction round×high_ambiguity positive and significant (p < 0.05) | Non-significant interaction; uniform drift across ambiguity |
| P2 | AAI trajectory correlates with TruthfulQA/BBH degradation | Spearman ρ > 0.4, negative direction | ρ ≤ 0.2 or positive correlation |
| P3 | WebGPT within-annotator: stylistic projection increases with cumulative exposure | β_exposure > 0, p < 0.05, worker fixed effects | β_exposure ≤ 0 or non-significant after fixed effects |

---

## Novelty

**Key Innovation**: Alignment Asymmetry Index (AAI) — first signed, directional, fully automated monitoring instrument for Human→AI preference adaptation in RLHF pipelines, validated against objective benchmarks without human evaluation.

**Differentiation from prior work**:
- Thakur 2024: Measures evaluation-phase judge adaptation; this measures training-data annotation drift linked to benchmark degradation
- Coste 2023: Global annotation variance; this isolates directional temporal drift with a causal mechanism
- Pan 2022: Benchmark degradation from reward errors; this identifies temporal annotation drift as the specific source
- Christiano 2017: Assumes static preferences; this provides the first empirical test of that assumption

---

## Experimental Design

**Datasets**: Anthropic HH-RLHF (169K comparisons, 3 phases), OpenAI WebGPT comparisons (worker IDs + timestamps)

**Models**: Q_early logistic regression (round-1 labels); TRL RewardTrainer for early/late temporal split reward models; PPO RLHF fine-tuning; static sentence-transformer for embedding analysis

**Benchmarks**: TruthfulQA (817 questions), BIG-Bench Hard (6511 questions), WinoBias

**Key Analysis Components**:
1. Round-conditioned logistic regression with Q_early covariate (stylistic coefficient drift)
2. Geometric projection onto pre-defined AI-typicality vector (round-1 centroid, fixed encoder)
3. Split-training RLHF behavioral divergence with mediation analysis
4. WebGPT dose-response panel regression with worker fixed effects

**Estimated Runtime**: < 4 hours total on a single GPU

---

## Limitations

- HH-RLHF annotator worker ID availability in public dataset needs verification
- Omitted variable bias from unmeasured semantic quality dimensions not captured by Q_early
- Limited annotation rounds (N=3 in HH-RLHF) constrains statistical power for round-level analyses
- Effect generalizability beyond English-language annotation unverified
- Cannot establish drift generalization beyond the specific AI models used in original annotation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Q_early calibration stability (go/no-go gate); effect size thresholds (Phase 2C power analysis); WebGPT within-worker variation (dataset verification) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: YouRA — Bidirectional Human-AI Alignment Measurement*

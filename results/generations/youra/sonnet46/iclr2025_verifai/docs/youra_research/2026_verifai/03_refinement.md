# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-18T03:00:00+00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: LLM Code Verifier Calibration Stratified by Self-Contained Difficulty Has Not Been Measured
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: Exchange 15 — All 6 criteria met

---

## Research Dialogue Context

**Participants**: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)

**Total Exchanges**: 15

**Convergence Reason**: Established rigorously falsifiable measurement study with explicit null baselines, temperature-scaling probes, and quantitative pre-registered thresholds. Reframed as first empirical calibration-difficulty fingerprint for LLM code verifiers.

### Key Insights
1. **Measurement study framing is strongest**: Analogous to Guo et al. (2017) who discovered modern NNs are poorly calibrated, we provide the first measurement of calibration quality stratified by difficulty for LLM code verifiers.
2. **k=5 bootstrap limitation**: Only 6 discrete pass@1 values; acknowledged as "pilot methodology" throughout. Does not eliminate contribution — it shapes it.
3. **Temperature scaling as mechanistic probe**: If global T collapses ΔECE → globally correctable miscalibration (uniform overconfidence); if ΔECE persists → difficulty-conditioned structure. Both are publishable findings.
4. **6-point calibration-difficulty curve**: Per model, plotting ECE at each of 6 pass@1 levels with bootstrap CIs — the "calibration fingerprint" concept.
5. **Null baseline comparison**: ECE_observed vs. ECE_null (constant confidence = tier accuracy) isolates structural from accuracy-mediated miscalibration.

### Breakthrough Moments
- Prof. Rex's regression control (ECE ~ Difficulty + Accuracy) reframed as pre-registered P2 robustness check
- Prof. Pax confirmed all components implementable with existing Run 3 infrastructure
- Prof. Nova's "calibration-difficulty fingerprint" transformed measurement study into paradigm-shifting framing
- Prof. Rex's "frame as measurement paper, not metacognition proof" eliminated overreach

---

## Final Hypothesis

### Title
**Difficulty-Stratified Calibration Fingerprint of LLM Code Verifiers via P(True)**

### Hypothesis ID
`H-CalibDiff-v1`

### Core Claim
Under k=5 self-contained difficulty stratification on HumanEval+/MBPP+ (542 problems), if LLMs predict code correctness via P(True) logprob elicitation stratified by difficulty tiers bootstrapped from their own pass@1 distribution (hard = pass@1 = 0.0, easy = pass@1 ≥ 0.6), then Expected Calibration Error differs systematically between difficulty tiers (ΔECE = ECE(hard) - ECE(easy) ≠ 0, primary prediction ΔECE > 0), because LLM confidence signals do not adequately reflect task-specific difficulty structure.

**H0 (Null)**: ΔECE ≤ 0 or |ΔECE| < 0.03 in ≥2/3 model families after controlling for base-rate accuracy differences.

### Mechanism
1. Generate k=5 solutions per problem → pass@1 via EvalPlus oracle
2. Stratify: hard = pass@1=0.0, easy = pass@1≥0.6 (per model)
3. Elicit P(True) logprob for each (problem, solution) pair
4. Compute ECE (M=15 bins) per tier; compare to null baseline; apply temperature scaling probe

---

## Predictions

| ID | Type | Statement | Success Criterion |
|----|------|-----------|-------------------|
| **P1** | Primary | ΔECE > 0 in ≥2/3 model families | ΔECE ≥ 0.03 with 95% CI excluding zero |
| P2 | Robustness | Excess ECE above null baseline larger in hard tier | p < 0.05 bootstrap test |
| P3 | Mechanistic | ΔECE persists after global temperature scaling | ΔECE ≥ 0.03 in ≥2/3 families post-scaling |
| P4 | Exploratory | DeepSeek-Coder ECE_overall < Llama3-8B | Directional comparison only |

**Falsification Criterion**: ΔECE ≤ 0 in ≥2/3 model families, OR ΔECE < 0.03 everywhere, OR CI includes zero in all families.

---

## Novelty

**What's New**: First empirical calibration-difficulty fingerprint for LLM code verifiers using P(True) logprob elicitation with self-contained bootstrap difficulty stratification. No prior work combines P(True) + ECE + EvalPlus + pass@1 bootstrap difficulty for code verification tasks.

**Differentiation from Prior Work**:
- Kadavath 2022: P(True) for factual Q&A only, no difficulty stratification, no code tasks
- Guo 2017: ECE for vision models, no LLMs, no difficulty stratification
- Liu 2023 EvalPlus: Measures pass rates, not calibration

---

## Experimental Design

**Models**: Llama3-8B (NousResearch mirror), CodeLlama-7B, DeepSeek-Coder-6.7B

**Datasets**: HumanEval+ (164 problems) + MBPP+ (378 problems) via EvalPlus (augmented test oracle)

**Difficulty Stratification**: Hard = pass@1=0.0, Easy = pass@1≥0.6 from k=5 solutions per model (self-contained bootstrap)

**Confidence Metric**: P(True) logprob = logprob("True") / (logprob("True") + logprob("False"))

**Calibration Metric**: ECE with M=15 equal-width bins; MCE as secondary; bootstrap 95% CIs

**Controls**:
1. Tier-specific null baseline (constant confidence = tier accuracy)
2. Global temperature scaling (T fitted on 20% holdout)
3. M-sensitivity analysis (M ∈ {10, 15, 20})
4. Partial correlation for solution length (optional ablation)

**Infrastructure**: Existing Run 3 h-e1 codebase — DataLoader, PytestRunner, P(True) elicitor, EvalPlus API all validated

---

## Limitations

- k=5 bootstrap produces only 6 discrete pass@1 values; difficulty stratification is coarse (pilot methodology)
- Three-model comparison is exploratory (N=1 per architecture category)
- Self-contained difficulty is model-specific, not a universal hardness ranking
- Python only (cross-language generalization not studied)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Exchange 15 — All 6 criteria met |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | k=5 pilot acknowledged; architecture comparison exploratory |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*15 exchanges across 6 personas — Converged at Exchange 15*

# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-19T00:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Controlled Head-to-Head Comparison of RLHF/DPO vs Execution-Feedback RL on Identical Setup
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: Exchange 15 (all 6 criteria met)

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All six criteria met — specific core claim, causal mechanism, five testable predictions with failure criteria, novelty articulated, full technical feasibility confirmed, major objections addressed.

### Key Insights

1. **Inductive bias → structural efficiency**: The intuition that execution feedback creates "different inductive bias" was operationalized into a measurable construct — semantic AST edit distance per unit KL divergence — through iterative sharpening across 15 exchanges.

2. **KL as policy movement budget**: KL divergence from the base model is a valid training signal quality normalization *if and only if* validated against behavioral metrics (AST edit distance). This is required before the efficiency claim can be interpreted as structural rather than cosmetic.

3. **Preference calibration gap**: DPO may increase model confidence (entropy ↓) without proportional gains in execution correctness — creating a named, diagnostic failure mode testable via entropy-matched ECE analysis.

4. **Granularity is conditioned**: Fine-grained execution rewards help only when stable partial correctness structure exists in the training distribution (Jaccard stability under test perturbation). They don't overcome global algorithmic mis-specification.

5. **OOD transfer is decisive**: Training on HumanEval+/MBPP+ and evaluating zero-shot on LiveCodeBench separates "optimization-local" from "structurally portable" policy updates.

### Breakthrough Moments

- **Exchange 6** (Dr. Ally): Unified KL-efficiency, calibration, and granularity into a single structural alignment theory
- **Exchange 10** (Prof. Rex): Demanded behavioral validation of KL via AST edit distance — transformed the metric from proxy to causal variable
- **Exchange 12** (Dr. Ally): Formalized "structural movement efficiency" (AST-edit/KL) as operationalizable, pre-registerable construct
- **Exchange 14** (Prof. Vera): Five quantitative predictions with explicit failure criteria — completed the scientific framework

---

## Final Hypothesis

### Title
Structural Efficiency of Policy Movement: Execution-Grounded Reward vs Preference-Based Alignment for Code Generation

### Hypothesis ID
`H-StructuralEfficiency-v1`

### Core Claim (Under-If-Then-Because)

> Under controlled post-training conditions (identical base model DeepSeek-Coder-7B, training data, and compute budget), **if** execution-feedback RL (GRPO with binary or error-type rewards) is applied instead of DPO, **then** execution-RL achieves higher structural efficiency of policy movement — measured as greater semantically-relevant AST edit distance per unit KL divergence from the base model — **because** execution reward directly penalizes functional incorrectness at the program level, forcing probability mass reallocation toward control-flow and data-flow transformations rather than surface-level stylistic changes.

### Null Hypothesis

There is no significant difference in structural efficiency of policy movement (semantic AST edit distance per unit KL) between execution-RL and DPO at matched KL budgets; any pass@1 differences are fully explained by total KL or entropy differences alone.

### Mechanism

1. Execution reward directly signals functional incorrectness at program level
2. Program-level signal forces probability mass reallocation toward control-flow and data-flow AST transformations
3. Structural reallocation produces higher semantic-edit-per-KL (structural movement efficiency)
4. Structural efficiency mediates correctness, calibration, granularity sensitivity, and OOD transfer

**DPO counterpart**: Optimizes log-probability ratios between preference pairs → may increase confidence in stylistically plausible but functionally incorrect outputs → "preference calibration gap" (confidence tracks style more than execution).

---

## Predictions

| ID | Statement | Success Criterion | Failure Criterion |
|----|-----------|-------------------|-------------------|
| **P1** | Execution-RL ≥20% higher semantic-edit-per-KL than DPO at KL-matched checkpoints | Bootstrap 95% CI excludes zero, magnitude ≥20% | CI includes zero or reverses sign |
| **P2** | Semantic-edit-per-KL mediates pass@1 in mixed-effects regression after KL/entropy controls | p < 0.05 for coefficient after controls | Effect vanishes when KL included |
| **P3** | Structural efficiency negatively correlates with ECE (ρ ≤ −0.3) under entropy matching | ρ ≤ −0.3, p < 0.05 entropy-matched | No correlation — calibration independent of structural movement |
| **P4** | Fine-grained reward ≥5pp over binary only in high-stability tertile | Significant interaction, low-stability gains absent | Comparable gains in low-stability (gradient densification only) |
| **P5** | In-distribution structural efficiency predicts LiveCodeBench pass@1 (R² ≥ 0.25) | R² ≥ 0.25 zero-shot on LiveCodeBench | R² < 0.25 — metric lacks external validity |

---

## Novelty

**Primary novelty**: First controlled comparison of RLHF/DPO vs execution-feedback RL under identical conditions (same model, data, compute, benchmarks).

**Secondary novelties**:
- Semantic-edit-per-KL: novel diagnostic metric for alignment training signal quality — reusable beyond code for any verifiable-reward post-training setting
- Preference calibration gap: named failure mode with diagnostic protocol (triangular calibration analysis + entropy-matched ECE)
- Partial correctness density annotation: novel benchmark characterization tool releasable alongside paper

**Differentiation from prior work**:
- CodeRL+ [Jiang et al., 2025]: compares variable-level vs binary within execution-RL only — no DPO baseline
- TÜLU 3 [Lambert et al., 2024]: applies DPO and RLVR sequentially in pipeline — not an alternative comparison
- RL Survey [Wang et al., 2024]: unifies methods theoretically — no empirical controlled comparison

---

## Experimental Design

| Component | Choice | Justification |
|-----------|--------|---------------|
| Base model | DeepSeek-Coder-7B-instruct | Open-weight SOTA, permissive license, 7B tractable for 5-condition fine-tuning |
| Training data | CodeAlpaca/OSS-Instruct (identical for all conditions) | Eliminates data-construction confound |
| Methods compared | SFT-only, SFT+DPO, SFT+GRPO-binary, SFT+GRPO-error-type, SFT+GRPO-variable-level | Covers full alignment method spectrum |
| Training framework | TRL (DPOTrainer + GRPOTrainer) | Unifies all methods in single library |
| In-distribution evaluation | evalplus (HumanEval+/MBPP+, pass@1) | Standard harness used by all major baselines |
| OOD evaluation | LiveCodeBench | Contamination-free, recent problems, used by ReCode |
| KL computation | Monte Carlo on fixed held-out prompt set, same decoding temperature | Ensures comparability across methods |
| Signal equalization | Two regimes: (A) equal prompts, (B) equal total tokens | Sensitivity analysis rather than single arbitrary choice |

---

## Limitations

- **Scope restricted to function-level benchmarks**: HumanEval+/MBPP+ short Python functions. SWE-bench excluded — instrumented execution intractable for repository-level code.
- **Python-specific error taxonomy**: Error-type reward assumes Python exception hierarchy; not directly portable to other languages.
- **Hard-bin sample sizes borderline**: ~80-100 hard problems across HumanEval+/MBPP+. LiveCodeBench hard-bin inclusion recommended to ensure P4 power.
- **DPO pairs via execution oracle**: Controlled choice that may not represent human-annotated DPO — results framed as "execution-oracle DPO" variant.
- **Pre-validation overhead**: AST classifier and Jaccard stability annotation require offline preprocessing before main experiments.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-StructuralEfficiency-v1 |
| **Discussion Convergence** | Exchange 15 — all 6 criteria met |
| **Clarity Verified** | Yes |
| **Predictions Pre-registerable** | Yes (5 predictions with quantitative thresholds) |
| **Feasibility Confirmed** | Yes (all tools exist; no new data/benchmarks/human eval) |
| **Remaining Pre-registration Steps** | Pre-validate AST classifier; ground thresholds in effect size estimates; specify DPO pair protocol |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Does execution-RL achieve higher structural-movement efficiency than DPO? → Primary existence test
- **SH2 (Mechanism)**: Does semantic-edit-per-KL mediate pass@1 in mixed-effects regression? → Mechanistic test
- **SH3 (Comparison)**: Does OOD transfer advantage persist on LiveCodeBench? → Deferred to Phase 5

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Venue target: DL4C @ ICLR Workshop*

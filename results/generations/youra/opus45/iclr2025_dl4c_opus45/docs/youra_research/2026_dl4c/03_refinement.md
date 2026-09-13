# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-24T12:15:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1-error-type-comparison
- **Gap Title**: No Direct Error Type Comparison Between RL-Aligned and DPO-Aligned Models
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met - hypothesis refined to two precise, falsifiable claims (H1: error type divergence, H2: error location divergence) with explicit statistical criteria and execution-based measurement

### Key Insights
1. **Gradient anti-correlation informs behavioral hypothesis**: The h-e1 failure (RL/DPO gradients anti-correlated across all layers) suggests fundamentally different optimization objectives, which should manifest as different behavioral failure modes
2. **Error TYPE analysis is orthogonal to pass RATE**: Provides complementary information about how alignment shapes model behavior
3. **Alignment as failure-mode engineering**: Reframes alignment choice from "which is better" to "which failure modes do you accept"
4. **Staged experimental design**: Separates exploration (existing models) from causal confirmation (controlled training)

### Breakthrough Moments
- Dr. Nova's initial reframing from performance comparison to failure-mode analysis
- Prof. Rex's demand for execution depth as independent mechanism test
- Prof. Pax's feasibility confirmation that reward topology differences are scientifically coherent
- Dr. Ally's synthesis into two bounded, testable predictions (H1 + H2)

---

## Final Hypothesis

### Title
Alignment-Induced Error Type Divergence in Code Generation

### Hypothesis ID
H-ErrorTypeDivergence-v1

### Core Claim
Under code generation on standard benchmarks (HumanEval+, MBPP+), if a model is aligned with execution-based RL (binary pass/fail reward) vs preference-based DPO (pairwise preference logits), then the conditional error type distribution P(error_type | failure) will differ systematically, because RL's reward topology creates optimization pressure toward syntactic validity and execution robustness (concentrating failures in semantic assertion errors), while DPO's preference signal emphasizes surface plausibility without explicit execution feedback (concentrating failures in execution errors).

### Mechanism
1. **RL binary execution reward** collapses all non-executable programs (syntax errors, runtime crashes) into a flat zero-reward basin
2. **This creates optimization pressure** toward syntactic validity first, pushing remaining failures into semantic assertion errors (code runs but produces wrong output)
3. **DPO optimizes pairwise preference logits** without explicit execution feedback, creating pressure toward human-readable, stylistically preferred code that may contain execution bugs humans wouldn't write

---

## Predictions

### P1 (Primary): Error Type Distribution
- **Statement**: RL-aligned models have lower proportion of syntax+runtime errors among failures compared to DPO-aligned models
- **Test**: Chi-square test on error type contingency table
- **Success**: P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO) with chi-square p < 0.05 AND Cramér's V > 0.05
- **Falsification**: 95% CI of proportion difference includes zero AND Cramér's V < 0.05

### P2: Execution Depth
- **Statement**: RL failures occur deeper in execution flow than DPO failures
- **Test**: Independent samples t-test on mean execution depth
- **Success**: mean(execution_depth | failure, RL) > mean(execution_depth | failure, DPO) with p < 0.05
- **Falsification**: No significant difference (t-test p > 0.10)

### P3: Taxonomy Robustness
- **Statement**: Effect persists at finer taxonomy granularity
- **Test**: Cramér's V at coarse (3-bin), intermediate (ICSE), and fine (LlmFix) levels
- **Success**: V > 0.03 at all granularity levels
- **Falsification**: V < 0.03 at intermediate or fine granularity

---

## Novelty

**Key Innovation**: First study to examine alignment method effects on error TYPE distribution rather than overall pass rate.

**Differentiation**:
| Prior Work | Our Difference |
|------------|----------------|
| "Is DPO Superior to PPO?" (2024) | Compared aggregate performance; we compare conditional error distributions |
| ICSE 2025 Error Taxonomy | Categorized errors without stratifying by alignment method |
| h-e1 gradient analysis | Analyzed gradient dynamics; we analyze behavioral outcomes |

---

## Experimental Design

### Datasets
- **HumanEval+**: 164 problems (evalplus/evalplus)
- **MBPP+**: 378 problems (evalplus/evalplus)

### Models
- **Stage 1 (Exploratory)**: CodeRL-770M (RL) vs DPO-finetuned CodeLlama-7B (DPO)
- **Stage 2 (Confirmatory)**: Controlled re-alignment from CodeT5-770M base

### Baselines
- Random baseline (null hypothesis)
- Unaligned base model

### Protocol
1. Generate n=10 samples per problem at temperature=0.8
2. Execute with EvalPlus harness
3. Classify failures via ICSE 2025 taxonomy (automated)
4. Compute conditional proportions and execution depth
5. Statistical tests with multiple comparison correction

---

## Limitations

### Known Constraints
- Stage 1 uses existing models with unknown pipeline differences
- Modern DPO datasets may already incorporate execution filtering
- Sample size (~325 failures/model/benchmark) may limit fine-grained taxonomy power

### Scope Boundaries
- **In Scope**: HumanEval+/MBPP+, 770M-7B models, error type and depth analysis
- **Out of Scope**: NL tasks, >13B models, sequential training, correlation structure, attractor analysis

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed) |

---

## Key Assumptions

| ID | Assumption | Consequence if Violated |
|----|------------|------------------------|
| A1 | RL training does NOT pre-filter by error type | Effect may reflect data curation |
| A2 | DPO preference pairs NOT execution-filtered | Expected divergence may be reduced |
| A3 | Error taxonomy can be automated | Manual annotation would violate feasibility |
| A4 | Effect detectable above pipeline noise | Stage 2 essential for causality |
| A5 | Effect persists across granularities | Effect is shallow if not |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*

# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-30T06:30:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap-1
- **Gap Title**: Lack of Controlled Comparison Between Localization Granularity Levels
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 personas reached consensus on hypothesis structure, mechanism, and experimental design

### Key Insights

1. **Reframing the Question**: Instead of "does more localization help?", ask "what is the minimal sufficient localization?" This shifts from assuming "more is better" to finding the Goldilocks Zone.

2. **Attention Window Hypothesis**: LLMs have limited effective attention for repair tasks. Too little feedback (G0-G2) provides insufficient guidance; too much (G4) dilutes attention with irrelevant details. G3 provides optimal "pointer" signal.

3. **Two-Phase Design**: Foundation gate (H-E1: runtime error prevalence ≥30%) prevents repeating the static analysis failure. If prevalence is low, we've still contributed valuable error characterization data.

4. **Lessons from Previous Failure**: Static errors were only ~5% of LLM failures. This pivots to runtime errors, which are hypothesized to be more prevalent.

### Breakthrough Moments

- **Exchange 1**: Dr. Nova proposed the Goldilocks Zone framing
- **Exchange 2**: Prof. Vera crystallized the 5-level taxonomy (G0-G4)
- **Exchange 4**: Prof. Pax raised prevalence concern, leading to foundation gate design
- **Exchange 5**: Dr. Ally synthesized the two-phase experimental structure

---

## Final Hypothesis

### Title

**Error Localization Granularity for LLM Code Repair: Testing the Attention Window Hypothesis**

### Hypothesis ID

H-GranularityOptimal-v1

### Core Claim

> Under conditions where LLM-generated code fails with a localizable runtime error,
> if we provide error feedback at varying granularity levels G0-G4,
> then repair success rate will show a non-monotonic relationship with peak at G3 ± 1,
> because G3 provides minimal sufficient localization that focuses LLM attention
> without cognitive overload from irrelevant trace details.

### Mechanism (Attention Window Hypothesis)

1. **Step 1**: Error feedback granularity affects LLM attention allocation
2. **Step 2**: G3 provides optimal "pointer" signal - sufficient localization without overload
3. **Step 3**: Focused attention on error location enables more accurate repair generation

### Null Hypothesis (H0)

There is no significant difference in repair success rate across granularity levels G0-G4.

---

## Variables

### Independent Variable
- **Name**: Error Feedback Granularity
- **Type**: Categorical (5 levels)
- **Levels**:
  - G0: Pass/Fail Only ("Test failed")
  - G1: Error Type ("Test failed: IndexError")
  - G2: Error + Message ("IndexError: list index out of range")
  - G3: Error + Line ("IndexError at line 7: list index out of range")
  - G4: Full Context (Stack trace + variable values)

### Dependent Variable
- **Name**: Repair Success Rate
- **Type**: Continuous (0-100%)
- **Measurement**: Proportion of failed tests successfully repaired after one LLM attempt

### Controlled Variables
- Model: CodeLlama-7B-Instruct
- Temperature: 0
- Prompt Template: Self-Debug style (Chen et al., 2023)
- Execution Timeout: 10 seconds
- Max Tokens: 512

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| P1 | ANOVA shows significant effect across G0-G4 | p < 0.05 | p ≥ 0.05 |
| P2 | G3 outperforms G0 by ≥10 percentage points | G3 - G0 ≥ 10%, p < 0.05 | Difference < 10% or n.s. |
| P3 | G4 does not outperform G3 | G4 ≤ G3 + 2% | G4 > G3 by >5% |

---

## Novelty

### Key Innovation
First systematic granularity comparison for LLM code repair with controlled ablation across 5 levels.

### Differentiation from Prior Work

| Prior Work | What They Did | Our Difference |
|------------|---------------|----------------|
| Self-Debug (Chen et al., 2023) | G2-level feedback only | Tests all 5 levels |
| TraceFixer (Bouzenia et al., 2023) | G4-level traces only | Includes simpler levels |
| DynaFix (Huang et al., 2025) | G4+ with variable states | Systematic ablation |
| Haque et al. (2025) | Found traces don't always help | Explains WHY via Goldilocks |

---

## Experimental Design

### Phase 1: Foundation Test (H-E1 - MUST_WORK Gate)
- **Dataset**: MBPP test set (500 problems)
- **Model**: CodeLlama-7B-Instruct
- **Procedure**: Generate → Execute → Categorize failure types
- **Metric**: Runtime error prevalence
- **Threshold**: ≥30%
- **Outcome**: If FAIL, research direction has limited scope

### Phase 2: Granularity Comparison (H-M1)
- **Dataset**: Runtime error subset from Phase 1
- **Design**: Within-subject (same problems across all conditions)
- **IV**: Granularity level (G0, G1, G2, G3, G4)
- **DV**: Repair success rate
- **Analysis**: One-way ANOVA + planned contrasts

### Compute Requirements
- ~1,250 LLM calls
- <2 hours on single GPU
- No human evaluation required

---

## Limitations

### Acknowledged Scope Boundaries

1. **Single Model**: CodeLlama-7B-Instruct only. Larger models might handle G4 better.
2. **Dataset Simplicity**: MBPP problems are relatively simple single-function tasks.
3. **G3 Definition**: "Error + Line" is one variant; others (error + snippet) exist.
4. **Single Repair Attempt**: Multi-turn repair may show different patterns.

### Mitigations

- Stratify analysis by problem complexity
- Acknowledge generalization limits
- Note variant testing as future work

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Achieved (12 exchanges) |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes (6/6) |
| **Remaining Objections** | 3 (all manageable - see Limitations) |
| **Phase 2B Ready** | Yes |

---

## Persona Verdicts Summary

| Persona | Aspect | Verdict |
|---------|--------|---------|
| 🔭 Dr. Nova | Novelty | STRONG |
| 🔬 Prof. Vera | Falsifiability | STRONG |
| 🎯 Dr. Sage | Significance | STRONG |
| ⚙️ Prof. Pax | Feasibility | STRONG |
| 🛡️ Dr. Ally | Synthesis | CONSENSUS ACHIEVED |
| 🔍 Prof. Rex | Critique | PROCEED WITH NOTED CONCERNS |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*

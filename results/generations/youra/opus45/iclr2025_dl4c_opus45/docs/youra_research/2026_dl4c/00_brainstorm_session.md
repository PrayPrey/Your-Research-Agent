---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: DL4C Behavioral Alignment Analysis"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Deep Learning for Code (DL4C) - Behavioral analysis of alignment methods for code generation models

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This is a ROUTE_TO_0 recovery after fundamental hypothesis failure in previous pipeline run. The h-e1 hypothesis attempted gradient-level analysis comparing RL and DPO alignment methods, but discovered that gradients are fundamentally anti-correlated rather than showing structured layer-wise divergence.

Source Type: ROUTE_TO_0 Failure Recovery / Minimal Input + Complete Failure History

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (h-e1 - FAILED):** Layer-wise gradient cosine similarity analysis
- Hypothesis: RL and DPO show structured divergence - high similarity (>0.4) in lower layers, low similarity (<0.2) in upper layers
- Method: Gradient capture during forward pass, cosine similarity computation per transformer layer
- Model: CodeT5-770M with 48 transformer layers

**Multiple ROUTE_TO_0 Cycles:** Previous pivots attempted to reframe the gradient analysis approach

### Why They Failed

1. **Fundamental assumption was WRONG:** RL and DPO gradients are ANTI-CORRELATED across ALL layers
   - Lower layers (1-8): -0.084 cosine similarity (expected >0.4)
   - Upper layers (17-24): -0.059 cosine similarity (expected <0.2)
   - All 48 layers showed statistically significant negative correlation (p < 0.05)

2. **No structured pattern exists:** The hypothesis assumed gradual divergence increasing with layer depth, but actual behavior shows UNIFORM anti-correlation

3. **Methods optimize in OPPOSITE directions:** RL (execution-based) and DPO (preference-based) don't share foundational representations - they actively push in opposing gradient directions

4. **Root cause:** Execution-based rewards (test pass/fail) and preference-based rewards (human rankings) create fundamentally different optimization pressures from the very first layer

### How THIS New Direction Avoids Those Pitfalls

**MANDATORY CONSTRAINTS (per pipeline rules):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future data that doesn't exist
- NO human evaluation, annotation, or subjective scoring
- ONLY hypotheses testable with EXISTING real datasets and EXISTING benchmarks

**Pivot Strategy:**
1. **ABANDON gradient-level analysis** - The h-e1 failure proves this approach is fundamentally flawed for understanding RL vs DPO in code models
2. **Focus on BEHAVIORAL outcomes** - Measure what the models actually produce, not internal gradient dynamics
3. **Use EXISTING benchmarks only** - HumanEval, MBPP, CodeContests with standard pass@k metrics
4. **Accept orthogonality as given** - Don't try to find alignment between RL and DPO; investigate their DIFFERENT contributions

---

## Session Plan

Auto-extracted from ROUTE_TO_0 failure recovery with minimal input ("dummy"). Research direction synthesized from failure context.

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions (ROUTE_TO_0 Failure Recovery)

---

## Research Question Development

### Initial Question

Given that RL and DPO gradients are fundamentally anti-correlated in code models, what distinct behavioral contributions does each alignment method make to code generation quality?

### Refined Question

Can behavioral error taxonomy analysis on existing code generation benchmarks (HumanEval/MBPP) reveal complementary strengths between execution-based RL and preference-based DPO alignment, without requiring gradient-level or representation-level analysis?

### Detailed Sub-Questions

1. **Error Pattern Differentiation:** Do RL-aligned and DPO-aligned models produce systematically different error types (syntax errors, runtime errors, wrong output, timeout)?

2. **Task-Specific Strengths:** Are there code generation subtasks where one method consistently outperforms the other on existing benchmarks?

3. **Complementarity Evidence:** Does error analysis on standard benchmarks reveal non-overlapping failure modes that suggest sequential training benefits?

4. **Model-Agnostic Patterns:** Do behavioral differences persist across different code model architectures (CodeT5, CodeLlama, StarCoder)?

5. **Quantitative Thresholds:** What pass@k improvements are observable when comparing RL-only, DPO-only, and combined approaches on HumanEval/MBPP?

---

## Reference Papers

Not provided - will discover in Phase 1

Potential search directions informed by failure:
- CodeRL and execution-based training (avoiding gradient-level claims)
- DPO/RLHF for code models (focusing on behavioral outcomes)
- Error analysis and failure taxonomies in code generation
- Empirical alignment method comparisons (not gradient-based)

---

## Validation Results

### So What Test

**Significance Pre-Validated by Failure:** The h-e1 failure revealed that gradient-level understanding of alignment methods is misleading. Understanding what each method actually DOES (behaviorally) rather than how gradients flow addresses a real gap exposed by experimental failure.

**Practical Impact:** Results would guide practitioners in selecting alignment methods based on empirical behavioral differences rather than theoretical gradient assumptions that don't hold.

### Feasibility Check

**Passes All Mandatory Constraints:**
- Uses EXISTING benchmarks: HumanEval, MBPP (standard pass@k)
- Uses EXISTING datasets: No synthetic data generation required
- No human evaluation: All metrics are automated (execution-based)
- No new scoring frameworks: Standard error categorization (syntax, runtime, wrong output)

**Computational Requirements:** Moderate - standard model inference and evaluation pipeline

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can behavioral error taxonomy analysis on existing code generation benchmarks (HumanEval/MBPP) reveal complementary strengths between execution-based RL and preference-based DPO alignment, without requiring gradient-level or representation-level analysis?

### detailed_question
1. Do RL-aligned and DPO-aligned models produce systematically different error types (syntax errors, runtime errors, wrong output, timeout)?

2. Are there code generation subtasks where one method consistently outperforms the other on existing benchmarks?

3. Does error analysis on standard benchmarks reveal non-overlapping failure modes that suggest sequential training benefits?

4. Do behavioral differences persist across different code model architectures (CodeT5, CodeLlama, StarCoder)?

5. What pass@k improvements are observable when comparing RL-only, DPO-only, and combined approaches on HumanEval/MBPP?

### reference_papers
Not provided - will discover in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Gradient analysis is a dead end:** The h-e1 failure conclusively shows that RL/DPO gradient dynamics don't follow expected patterns - methods are fundamentally anti-correlated, not divergent

2. **Behavioral empiricism is the path forward:** Focus on what models produce rather than how they optimize internally

3. **Error taxonomy is feasible with existing tools:** Standard benchmark execution already produces error categorization data

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0 Failure Recovery - Learning from h-e1 gradient analysis failure)

### Areas for Further Exploration

1. Error distribution analysis on HumanEval/MBPP for differently-aligned models
2. Cross-architecture validation of behavioral patterns
3. Sequential training experiments (RL→DPO vs DPO→RL) on standard benchmarks
4. Correlation between error types and alignment method

---

## Next Steps

Proceed to Phase 1 - Targeted Research

**Key Phase 1 Focus:**
- Find papers on error analysis in code generation
- Identify existing RL vs DPO comparison studies (behavioral, not gradient)
- Locate error taxonomy frameworks that don't require new annotations
- Research complementarity of alignment methods in practice

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Recovery)*
*Ready for: Phase 1 - Targeted Research*

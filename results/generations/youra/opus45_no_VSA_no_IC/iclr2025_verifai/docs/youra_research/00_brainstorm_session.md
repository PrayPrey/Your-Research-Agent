---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: VerifAI - LLM Code Verification"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-24
**Facilitator:** Research Question Architect
**Participant:** Anonymous
**Mode:** UNATTENDED (Auto-Fill from VerifAI CFP)

---

## Executive Summary

**Initial Interest:** Bridging LLM code generation with formal verification methods - specifically exploring how existing verification tools (static analyzers, type checkers, SAT solvers) can serve as "soft verifiers" to assess and improve LLM-generated code quality.

**Session Approach:** Auto-Fill Mode (extracted from ICLR 2025 VerifAI Workshop CFP)

**Session Duration:** Automated extraction

---

## Starting Context

**Source:** ICLR 2025 VerifAI Workshop - "AI Verification in the Wild"

**Workshop Theme:** Intersection of scale-driven generative AI and correctness-focused verification principles.

**Key Angles from CFP:**
1. Generative AI for formal methods (LLMs guiding proof search, writing theorems)
2. Formal methods for generative AI (SAT solvers as reasoning bottlenecks, program analysis for correctness)
3. AI as verifiers (probabilistic "soft assurances" when hard guarantees infeasible)
4. Datasets and benchmarks for AI+verification intersection
5. Special Theme: LLMs for Code Generation with formal tool integration

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future data
- NO human evaluation or subjective scoring
- ONLY existing real datasets and existing benchmarks

---

## Lessons from Previous Attempts

N/A - First attempt

---

## Session Plan

Auto-fill mode: Extract research components directly from CFP content, applying feasibility constraints to filter viable research directions.

---

## Technique Sessions

**Technique:** Constraint-Guided Extraction

Applied feasibility constraints to CFP themes:
- ✓ "AI as verifiers" angle - testable with existing code benchmarks
- ✓ "Formal methods for generative AI" - existing static analyzers available
- ✗ "New benchmarks" - rejected per constraints
- ✗ "Human evaluation" approaches - rejected per constraints

---

## Research Question Development

### Initial Question

How can existing formal verification tools (static analyzers, type checkers, linters) serve as automated quality assessors for LLM-generated code, and does their feedback correlate with functional correctness on established benchmarks?

### Refined Question

Can static analysis tool outputs (error counts, warning types, type coverage) predict functional correctness of LLM-generated code on existing benchmarks (HumanEval, MBPP, SWE-bench), and can this signal be used to improve code generation through rejection sampling or iterative refinement?

### Detailed Sub-Questions

1. **Correlation Analysis:** What is the correlation between static analysis metrics (pylint score, mypy errors, complexity metrics) and pass@k on HumanEval/MBPP for various LLMs?

2. **Rejection Sampling:** Can static-analysis-based rejection sampling improve pass@1 without additional LLM calls? (Select best candidate from k generations using SA scores)

3. **Iterative Refinement:** Does feeding static analysis errors back to the LLM for self-repair improve functional correctness more than blind regeneration?

4. **Cross-Model Generalization:** Do static analysis predictors trained on one LLM's outputs transfer to other LLMs?

5. **Tool Combination:** Which combination of existing tools (pylint, mypy, bandit, radon) provides best predictive signal for correctness?

---

## Reference Papers

**To be gathered in Phase 1. Candidate search terms:**
- "LLM code generation static analysis"
- "Self-repair code generation"
- "Rejection sampling code generation"
- "HumanEval benchmark analysis"
- "Program repair neural"

---

## Validation Results

### So What Test

**Why does this matter?**
- LLM code generation widely deployed but correctness remains problematic
- Static analysis tools are free, fast, deterministic - no additional LLM cost
- If SA metrics predict correctness, enables cheap quality filtering at inference time
- Could reduce compute costs vs. running all candidates through test suites

**Who benefits?**
- Practitioners deploying code-generation LLMs
- Researchers studying LLM reliability
- Tool builders integrating verification into LLM pipelines

### Feasibility Check

**Existing Datasets:** ✓ HumanEval, MBPP, SWE-bench all publicly available
**Existing Benchmarks:** ✓ Standard pass@k metrics, no new scoring needed
**Existing Tools:** ✓ pylint, mypy, bandit, radon all open-source
**No Human Evaluation:** ✓ All metrics automated
**Immediate Testability:** ✓ Can run experiments today with existing resources

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can static analysis tool outputs (error counts, warning types, type coverage) predict functional correctness of LLM-generated code on existing benchmarks (HumanEval, MBPP), and can this signal improve code generation through rejection sampling or iterative refinement?

### detailed_question
1. What is the correlation between static analysis metrics (pylint score, mypy errors, complexity metrics) and pass@k on HumanEval/MBPP for various LLMs?
2. Can static-analysis-based rejection sampling improve pass@1 without additional LLM calls?
3. Does feeding static analysis errors back to the LLM for self-repair improve functional correctness more than blind regeneration?
4. Do static analysis predictors trained on one LLM transfer to other LLMs?
5. Which combination of existing tools (pylint, mypy, bandit, radon) provides best predictive signal?

### reference_papers
Not provided - to be gathered in Phase 1

</phase1-input>

---

## Session Insights

### Key Discoveries

1. VerifAI CFP "AI as verifiers" theme maps directly to using SA tools as soft verifiers
2. Feasibility constraints eliminate most "new benchmark" directions but leave correlation/prediction studies viable
3. Rejection sampling approach avoids need for additional training or fine-tuning

### Techniques Used

- Constraint-Guided Extraction (auto-fill mode)
- Feasibility Filtering against pipeline constraints

### Areas for Further Exploration

- Comparison with execution-based filtering (if test cases available)
- Extension to low-resource programming languages (per CFP special theme)
- Combining multiple SA tools into ensemble predictor

---

## Next Steps

1. **Phase 1:** Targeted literature search on static analysis for LLM code, rejection sampling, self-repair
2. **Phase 2A:** Generate specific hypotheses about SA-correctness correlation
3. **Phase 2B:** Design experiments using HumanEval/MBPP with multiple LLMs

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

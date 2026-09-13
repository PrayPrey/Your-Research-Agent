---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Execution-Guided LLM Self-Repair via Runtime Error Localization"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-30
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Bridging formal methods and generative AI for code verification - exploring how verification techniques can enhance LLM-driven code generation and repair

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

This workshop explores the intersection of scale-driven generative artificial intelligence (AI) and the correctness-focused principles of verification. The VerifAI workshop invites discussions on bridging formal analysis and AI, with a special theme on LLMs for Code Generation. Key angles include: AI for formal methods (guiding proof search, generating theorems), formal methods for AI (using solvers as reasoning bottlenecks, program analysis for generated code), AI as verifiers (probabilistic soft assurances), and leveraging execution feedback for code validation.

Source Type: Workshop CFP / Structured Input (ICLR 2025 VerifAI Workshop)

---

## Lessons from Previous Attempts

### What Was Tried Before

**Previous Research Direction:** Static-Analysis-Grounded Self-Explanation for Efficient LLM Code Repair

**Hypothesis Tested (h-e1):** On MBPP with CodeLlama-7B-Instruct, at least 15% of first-pass failures contain static-analysis-catchable errors.

### Why It Failed

| Metric | Observed | Required | Gap |
|--------|----------|----------|-----|
| Static Error Prevalence | 4.92% | 15.0% | -10.08% |
| CI Lower Bound | 3.33% | 10.0% | -6.67% |

**Root Causes:**
1. **Static errors are rare in modern LLMs**: CodeLlama-7B-Instruct produces syntactically valid Python in most cases. Errors manifest as semantic/logic issues, NOT static-analysis-catchable violations.
2. **Model quality exceeds assumption**: Modern instruction-tuned models have internalized basic Python syntax and type conventions.
3. **Limited detection scope**: mypy and ruff catch type/style violations, not the semantic bugs causing most test failures.

### How THIS Direction Avoids Those Pitfalls

**Key Insight from Failure:** Static analysis has limited scope (~5% coverage) because LLM errors are primarily SEMANTIC, not syntactic.

**New Approach - Execution-Guided Repair:**
1. **Focus on RUNTIME errors instead of STATIC errors** - Runtime errors (exceptions, assertion failures, wrong outputs) are far more prevalent than static errors
2. **Use execution feedback as verification signal** - Aligns with VerifAI workshop theme "learning from execution feedback to validate generations"
3. **Leverage error localization, not error detection** - The challenge isn't detecting errors (test failures do that), but LOCALIZING them to guide repair
4. **Target semantic understanding** - Use runtime stack traces and variable states to understand WHAT went wrong, not just THAT something is wrong

**What We Preserve from Previous Work:**
- Experimental infrastructure (code generation, test execution) works correctly
- Gate evaluation framework successfully validates/rejects hypotheses
- Early foundation testing prevents wasted effort on flawed assumptions

---

## Session Plan

Auto-extracted from structured input with failure context integration:
1. Extract research themes from VerifAI CFP
2. Filter through lessons learned (avoid static-analysis-first approaches)
3. Identify execution-feedback-based research direction
4. Synthesize into testable hypothesis compatible with existing benchmarks

---

## Technique Sessions

Auto-Fill Mode with ROUTE_TO_0 context - No interactive sessions conducted.

Applied failure-aware extraction: Prioritized "execution feedback" and "runtime validation" themes over "static analysis" approaches based on previous failure lessons.

---

## Research Question Development

### Initial Question

How can we leverage execution feedback (runtime errors, test failures, stack traces) to improve LLM self-repair for code generation tasks?

### Refined Question

Can runtime error localization - identifying which code region caused a test failure using execution traces - improve LLM self-repair success rate compared to providing only pass/fail feedback?

### Detailed Sub-Questions

1. **Error Localization Prevalence:** What proportion of LLM-generated code failures produce localizable runtime errors (exceptions with stack traces pointing to specific lines)?

2. **Localization Signal Value:** Does providing the specific error location (line number, variable state) improve repair success rate compared to just showing the error message?

3. **Repair Strategy Selection:** Can error type classification (NameError, TypeError, IndexError, AssertionError) guide selection of appropriate repair strategies?

4. **Feedback Granularity:** What is the optimal granularity of execution feedback - full stack trace, error line only, or error line with surrounding context?

5. **Benchmark Generalization:** Do execution-guided repair benefits generalize across different code generation benchmarks (MBPP, HumanEval, APPS)?

---

## Reference Papers

Not provided directly in input - will discover in Phase 1.

Suggested search directions based on research question:
- LLM self-repair and iterative refinement for code generation
- Fault localization techniques for automated program repair
- Execution-guided neural program synthesis
- Test-driven code generation with feedback loops

---

## Validation Results

### So What Test

**Significance:** This research addresses a core challenge in LLM code generation - most failures are NOT caught by static analysis (as our previous experiment demonstrated), so understanding RUNTIME behavior is essential for effective repair.

**Impact:** If execution-guided localization improves repair rates, it provides:
1. A practical technique for improving LLM coding assistants
2. Empirical understanding of what feedback signals help LLMs fix code
3. Bridge between formal methods (execution monitoring) and generative AI (as per VerifAI workshop themes)

**Novelty:** Shifts focus from "can we detect errors?" (yes, via tests) to "can we LOCALIZE errors to guide repair?" - a more actionable research direction.

### Feasibility Check

**Testable with Existing Resources:**
- ✅ MBPP, HumanEval benchmarks exist
- ✅ CodeLlama and similar models available
- ✅ Python's traceback module provides execution error localization
- ✅ Can compare repair rates with/without localization information
- ✅ No new datasets or human evaluation required

**Avoids Previous Failure Modes:**
- ✅ Does NOT assume static errors are prevalent (they're not)
- ✅ Uses runtime feedback which IS prevalent in failures
- ✅ Builds on validated experimental infrastructure

**Clear Success Criteria:**
- Measurable: Repair success rate improvement (percentage points)
- Threshold: Statistically significant improvement over baseline (no localization)
- Falsifiable: If localization doesn't help, hypothesis is rejected

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can runtime error localization - identifying which code region caused a test failure using execution traces - improve LLM self-repair success rate compared to providing only pass/fail feedback?

### detailed_question
1. What proportion of LLM-generated code failures produce localizable runtime errors (exceptions with stack traces pointing to specific lines)?
2. Does providing the specific error location (line number, variable state) improve repair success rate compared to just showing the error message?
3. Can error type classification (NameError, TypeError, IndexError, AssertionError) guide selection of appropriate repair strategies?
4. What is the optimal granularity of execution feedback for guiding LLM repair?
5. Do execution-guided repair benefits generalize across MBPP, HumanEval, and other benchmarks?

### reference_papers
Not provided - will discover in Phase 1. Search directions: LLM self-repair, fault localization, execution-guided synthesis, test-driven code generation.

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Static analysis is insufficient** - Previous experiment proved only ~5% of LLM errors are static-catchable
2. **Runtime errors are the key signal** - Most failures manifest at runtime, making execution feedback essential
3. **Localization > Detection** - The challenge is pinpointing WHERE errors occur, not WHETHER they exist
4. **Execution feedback aligns with workshop theme** - VerifAI explicitly mentions "learning from execution feedback"

### Techniques Used

ROUTE_TO_0 Failure Recovery (automated extraction with failure context integration)

### Areas for Further Exploration

1. Multi-turn repair with progressive error resolution
2. Combining static hints (when available) with runtime localization
3. Learning repair patterns from error-fix pairs
4. Cross-language generalization of execution-guided repair

---

## Next Steps

1. **Proceed to Phase 1 - Targeted Research:** Gather literature on LLM self-repair, fault localization, and execution-guided synthesis
2. **Validate foundation assumption:** Confirm that runtime errors with stack traces ARE prevalent (unlike static errors)
3. **Design controlled experiment:** Compare repair success with/without error localization
4. **Identify baseline methods:** Find existing execution-feedback approaches to compare against

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Recovery)*
*Ready for: Phase 1 - Targeted Research*

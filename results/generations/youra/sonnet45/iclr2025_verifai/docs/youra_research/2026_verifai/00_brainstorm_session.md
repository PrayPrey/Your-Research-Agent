---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: LLM-Guided Verification with Scope"
pipeline_project_id: "796fabf5-7c52-490e-b4f5-6ab7c931d96e"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-18
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** AI Verification in the Wild - Lightweight formal methods integration with LLMs for code generation

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction with failure context integration)

---

## Starting Context

This workshop explores the intersection of scale-driven generative artificial intelligence (AI) and the correctness-focused principles of verification. The special theme focuses on LLMs for code generation with techniques from programming languages and formal methods communities (context-free grammars, static analyzers, SMT-guided repair) to enhance safety and effectiveness.

**Source Type:** Workshop CFP / Structured Input
**Recovery Context:** Retrying after Phase 4 infrastructure infeasibility failure

---

## Lessons from Previous Attempts

### What Was Tried (Previous Attempt)

**Research Direction:** SMT-LIB Generation from C Code for Vulnerability Detection (h-e1)
- **Approach:** Build complete CWE template system (42 classes) + CodeBERT classifier + FormAI dataset (112K programs)
- **Hypothesis Type:** EXISTENCE (validate feasibility of template-based SMT translation)
- **Implementation Scope:** 15 tasks (6 Epics, 40+ hours estimated), 145+ golden tests, multi-hour training

### Why It Failed

**Root Cause:** Infrastructure requirements fundamentally exceeded Phase 4 proof-of-concept validation capacity

**Specific Issues:**
1. **Dataset Scale:** FormAI (112K programs, multi-GB) required 2-4 hour download + full processing
2. **Template Design Burden:** 42 CWE classes with manual SMT-LIB schema design (20-30 hours)
3. **Golden Test Creation:** 145+ test cases requiring ESBMC baseline derivation (12-20 hours)
4. **Training Time:** CodeBERT fine-tuning on 89.6K samples (4+ hours on H100 GPU)
5. **Implementation Complexity:** 61 complexity points across 6 Epic-level tasks (multi-week project)

**Critical Insight:** EXISTENCE hypothesis treated as production system implementation, not conceptual feasibility proof

### How THIS Direction Avoids Those Pitfalls

**Scope Constraints Applied:**

1. **Dataset Scale:** Use lightweight datasets (<10K samples) or representative subsets (10% sampling)
   - **Rule:** If dataset download >1GB or >2 hours → scope too large

2. **Template/Schema Design:** Focus on 3-5 representative cases, not exhaustive coverage
   - **Rule:** Proof-of-concept ≤10 template classes/patterns

3. **Implementation Complexity:** Target 3-8 tasks maximum, <20 complexity points total
   - **Rule:** If Phase 3 generates >12 tasks → hypothesis needs decomposition

4. **Training Time:** Experiments must complete in <30 minutes for rapid iteration
   - **Rule:** If training >1 hour → use smaller model or dataset subset

5. **Hypothesis Type Alignment:** EXISTENCE = "Can X exist?" not "Build X and measure it"
   - **Rule:** Qualitative feasibility demonstration, not quantitative performance benchmarks

6. **Modular Decomposition:** Validate components independently, avoid monolithic systems
   - **Rule:** Break into testable sub-hypotheses (design-focused, translation-focused, ML-focused)

**NEW Research Direction:**
- Focus on **lightweight integration** of formal methods with LLMs
- Validate **conceptual feasibility** on small-scale examples
- Use **existing tools** and **off-the-shelf models** where possible
- Demonstrate **proof-of-concept** without building production infrastructure

---

## Session Plan

ROUTE_TO_0 Auto-Fill Mode: Extract research direction from VerifAI workshop CFP, filtered through failure lessons to ensure scoped, feasible hypothesis generation.

---

## Technique Sessions

Auto-Fill Mode - No interactive sessions (failure context integrated automatically)

---

## Research Question Development

### Initial Question

How can lightweight formal methods be integrated with LLMs for code generation to improve safety and correctness without requiring extensive infrastructure?

### Refined Question

Can we demonstrate feasibility of integrating lightweight formal verification techniques (static analysis, constraint checking, type verification) with LLM-generated code through proof-of-concept validation on small-scale representative examples?

### Detailed Sub-Questions

1. **Lightweight Static Analysis Integration**: Can static analyzers (e.g., Pylint, Mypy, Clang-Tidy) provide actionable feedback to guide LLM code generation iteratively on small codebases (<1K LOC)?

2. **Constraint-Guided Generation**: Can simple constraint specifications (pre/post-conditions, type annotations) steer LLM code generation toward correct implementations without requiring full SMT solver infrastructure?

3. **Execution Feedback Validation**: Can runtime execution on small test suites (10-20 tests) provide sufficient signal for LLM agents to self-correct generated code?

4. **Subset-Based Verification**: Can proof-of-concept verification be demonstrated on 3-5 representative problem classes (e.g., buffer safety, null pointer, type correctness) without exhaustive coverage?

5. **Tool-Use Feasibility**: Can existing off-the-shelf tools (pytest, mypy, clang-tidy, simple SMT solvers like Z3 for bounded checks) be composed without custom infrastructure?

**MANDATORY CONSTRAINTS (Enforced):**
- Use existing real datasets (<10K samples or 10% subsets)
- Existing benchmarks only (HumanEval subset, MBPP subset, small verification benchmarks)
- No new rubrics or scoring frameworks
- No synthetic data generation or human evaluation
- Testable immediately with current tools

---

## Reference Papers

Not provided - will discover in Phase 1

**Phase 1 Search Focus:**
- Lightweight verification for LLM code generation
- Static analysis + LLM integration
- Constraint-guided code generation
- Small-scale formal methods validation
- Tool-use and execution feedback for code correctness

---

## Validation Results

### So What Test

**Significance:**
- Workshop explicitly welcomes **works in progress** and **negative results**
- Special theme (LLMs for Code Generation) directly addresses this direction
- Lightweight verification addresses accessibility barrier in formal methods
- Proof-of-concept feasibility studies are valuable contributions

**Impact Areas:**
- LLM code generation safety (immediate industry impact)
- Formal methods accessibility (lowering adoption barriers)
- Tool-use validation for LLM agents
- Iterative refinement through static feedback

### Feasibility Check

**✅ PASS with FAILURE LESSONS INTEGRATED**

**Scope Validation:**
- Dataset scale: <10K samples or subsets (✓ feasible)
- Implementation tasks: 3-8 tasks target (✓ manageable)
- Training time: <30 minutes or use existing models (✓ achievable)
- Template design: 3-5 problem classes (✓ scoped)
- Tools: Existing off-the-shelf (pylint, mypy, pytest, Z3) (✓ available)

**Hypothesis Type Alignment:**
- EXISTENCE = conceptual feasibility demonstration (✓ aligned)
- Qualitative validation on representative examples (✓ appropriate)
- No exhaustive coverage or production metrics required (✓ scoped)

**Risk Mitigation:**
- Previous failure: 112K dataset → NEW: <10K subset
- Previous failure: 42 CWE classes → NEW: 3-5 problem classes
- Previous failure: 145+ tests → NEW: 10-20 representative tests
- Previous failure: 40+ hours implementation → NEW: <8 tasks, <20 complexity points
- Previous failure: Multi-hour training → NEW: Use existing models or <30min fine-tuning

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can we demonstrate feasibility of integrating lightweight formal verification techniques (static analysis, constraint checking, type verification) with LLM-generated code through proof-of-concept validation on small-scale representative examples?

### detailed_question
1. **Lightweight Static Analysis Integration**: Can static analyzers (e.g., Pylint, Mypy, Clang-Tidy) provide actionable feedback to guide LLM code generation iteratively on small codebases (<1K LOC)?

2. **Constraint-Guided Generation**: Can simple constraint specifications (pre/post-conditions, type annotations) steer LLM code generation toward correct implementations without requiring full SMT solver infrastructure?

3. **Execution Feedback Validation**: Can runtime execution on small test suites (10-20 tests) provide sufficient signal for LLM agents to self-correct generated code?

4. **Subset-Based Verification**: Can proof-of-concept verification be demonstrated on 3-5 representative problem classes (e.g., buffer safety, null pointer, type correctness) without exhaustive coverage?

5. **Tool-Use Feasibility**: Can existing off-the-shelf tools (pytest, mypy, clang-tidy, simple SMT solvers like Z3 for bounded checks) be composed without custom infrastructure?

### reference_papers
Not provided - will discover in Phase 1

**Search Focus:** Lightweight verification for LLM code generation, static analysis integration, constraint-guided generation, execution feedback for correctness, small-scale formal methods validation

</phase1-input>

---

## Session Insights

### Key Discoveries

**From Failure Analysis:**
- EXISTENCE hypotheses should be lightweight conceptual proofs, not production systems
- Dataset scale is critical constraint: >1GB or >2 hours download = infeasible
- Template/schema design burden: >10 classes = too exhaustive for PoC
- Implementation task count: >12 tasks signals multi-week project, not hypothesis validation
- Training time matters: >1 hour indicates large-scale experiment, not quick validation

**From Current Input:**
- Workshop welcomes works-in-progress and proof-of-concept studies
- Lightweight verification addresses formal methods accessibility barrier
- Tool-use and execution feedback are practical integration approaches
- Small-scale representative validation is methodologically sound

**Strategic Pivot:**
- From exhaustive coverage (42 CWEs, 112K programs) → Representative sampling (3-5 cases, <10K subset)
- From custom infrastructure (templates, classifiers, training) → Existing tools (static analyzers, test frameworks)
- From production metrics (F1 ≥0.80, classification accuracy) → Qualitative feasibility (iterative improvement demonstrated)
- From monolithic system → Modular components (independently testable)

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode (failure context integration + structured input extraction)

### Areas for Further Exploration

**Phase 1 Research Priorities:**
1. Existing lightweight verification benchmarks (HumanEval subset, MBPP subset, small SMT benchmarks)
2. Static analysis tools with LLM-friendly feedback (actionable error messages)
3. Minimal constraint specification approaches (type hints, simple assertions)
4. Execution-based validation for code correctness (test-driven LLM generation)
5. Prior work on tool-use for LLM code generation (retrieval, debugging, iterative refinement)

**Explicitly AVOID (Based on Failure):**
- Large-scale datasets requiring multi-hour downloads
- Custom template/schema design requiring domain expertise
- Multi-hour training or fine-tuning experiments
- Exhaustive coverage validation (>10 classes)
- Production-level quantitative benchmarks

---

## Next Steps

Proceed to Phase 1 - Targeted Research with scoped feasibility focus

**Phase 1 Constraints:**
- Search for lightweight verification approaches (<10K scale)
- Identify existing small benchmarks (no new dataset creation)
- Find prior work on tool-use for code generation
- Validate that existing tools (static analyzers, test frameworks) are sufficient
- Ensure research direction can be validated in Phase 4 with <8 tasks, <30min experiments

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*
*Recovery Mode: ROUTE_TO_0 - Learned from previous infrastructure infeasibility failure*

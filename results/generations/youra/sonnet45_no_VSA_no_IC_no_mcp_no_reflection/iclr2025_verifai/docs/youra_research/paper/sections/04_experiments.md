# Experimental Setup

This section describes the experimental design for validating the four sub-hypotheses. While execution was blocked at h-e1 due to infrastructure failures, the experimental protocol, datasets, and evaluation metrics were fully specified.

## Research Questions

Our experiments were designed to answer three key questions:

**RQ1 (Existence):** Can static analyzers extract SMT constraints from LLM-generated typed code at ≥90% success rate?

**RQ2 (Mechanism):** Does dependency analysis accurately identify invalidation cones (<30% of constraints) while maintaining soundness (zero false negatives)?

**RQ3 (Performance):** Does incremental SMT achieve 2-5x wall-clock speedup vs batch re-verification on iterative LLM code repair?

These map to hypotheses h-e1, h-m2, and h-m3 respectively. h-m1 (constraint extraction from Pydantic annotations) is an implementation validation step rather than a research question.

## Dataset

**Source:** HumanEval (OpenAI), problems 0-99 (100 programs).

**Extension:** Mechanically generated Pydantic type annotations via template-based transformation. Each extended prompt includes:
- Function signature with type hints
- Pydantic BaseModel schemas for inputs/outputs
- @validator decorators encoding preconditions (e.g., non-null constraints, range constraints)
- Original docstring and test suite

**Rationale:** HumanEval provides standard baseline for code generation research (164 problems, existing test suites). Type extension enables static analysis without manual annotation bias. Programs span 10-50 LOC (suitable for PoC validation).

**Validation:** Dataset extension pipeline executed successfully, generating 100 JSON files in `src/data/humaneval_pydantic/`. Each file contains valid Pydantic template matching the original HumanEval problem specification.

## LLM Code Generation

**Model:** Claude Sonnet 3.5 (claude-sonnet-3-5-20240620)

**Temperature:** 0.2 (balance between determinism and diversity)

**Max Tokens:** 512

**System Prompt:** "Generate typed Python code using Pydantic BaseModel. Include @validator decorators for preconditions. Do not use eval, exec, or metaprogramming."

**Rationale:** Prompt constraints enforce typed subset suitable for static analysis, banning dynamic features (eval/exec) that block AST parsing. Claude Sonnet 3.5 chosen for state-of-the-art code generation capabilities.

**Expected Output:** 100 typed Python programs with Pydantic annotations, passing original HumanEval test suites.

**Actual Result:** 0 programs generated. All 48 generation attempts (experiment stopped early) failed with HTTP 401 "API key is invalid" errors.

## Baseline Methods

**Baseline 1: Batch SMT Verification**
- **Method:** Re-verify entire program on each repair iteration using Z3.
- **Time Complexity:** O(n) where n = total constraints (all re-verified).
- **Correctness:** Sound and complete (no false negatives/positives).
- **Use:** Primary performance baseline for h-m3 speedup measurement.

**Baseline 2: Test-Suite-Only Validation**
- **Method:** LLM generates code, run HumanEval test suite, accept if all tests pass.
- **Time Complexity:** O(t) where t = test count (typically < 10).
- **Correctness:** Incomplete (misses edge cases not covered by tests).
- **Use:** Comparison point for verification overhead vs no verification.

**Rationale:** Baseline 1 provides same correctness guarantees as incremental SMT (sound verification), isolating speedup as the only difference. Baseline 2 represents current practice in neural code generation (no formal verification).

## Evaluation Metrics

### Primary Metrics

**h-e1: Extraction Success Rate**
$$\\text{extraction\\_rate} = \\frac{\\text{programs with constraints}}{\\text{total programs}} \\times 100\\%$$

**h-m3: Speedup Factor**
$$\\text{speedup} = \\frac{\\text{batch verification time}}{\\text{incremental verification time}}$$

**h-m2: Invalidation Cone Size**
$$\\text{cone\\_size} = \\frac{\\text{constraints in invalidation cone}}{\\text{total constraints}} \\times 100\\%$$

### Secondary Metrics

**h-m2: Soundness (Error Detection Rate)**
$$\\text{detection\\_rate} = \\frac{\\text{seeded errors caught}}{\\text{total seeded errors}} \\times 100\\%$$
Success: 100% (zero false negatives).

**h-m1: Extraction Overhead**
$$\\text{overhead\\_ratio} = \\frac{\\text{extraction time}}{\\text{total verification time}} \\times 100\\%$$
Success: <10% (validates assumption A4).

## Experimental Procedure

### h-e1 (EXISTENCE): Constraint Extraction Validation

1. Generate 100 typed Python programs via Claude Sonnet 3.5 API (from Pydantic-annotated prompts).
2. For each program, run Pyre static analyzer in constraint extraction mode.
3. Parse Pyre output, count valid SMT predicates extracted.
4. Compute extraction_rate.
5. **Gate check:** If extraction_rate ≥90%, PASS → proceed to h-m1. Otherwise, FAIL → pivot to neural extraction.

**Actual Result:** Step 1 failed with 100% API authentication errors. Steps 2-5 not executed. extraction_rate = 0.0% (infrastructure block, not extraction failure).

### h-m1 (MECHANISM): Pyre Extraction Pipeline

1. Take validated programs from h-e1 (extraction_rate ≥90%).
2. Run Pyre on each program, collect constraint types (precondition, postcondition, invariant).
3. Verify constraints are well-formed Z3-compatible predicates.
4. Measure extraction time vs SMT solving time.
5. **Gate check:** MUST_WORK (all programs extract successfully, overhead <10%).

**Actual Result:** NOT_STARTED (prerequisite h-e1 failed).

### h-m2 (MECHANISM): Dependency Analysis + Soundness

1. Generate initial programs + constraints (from h-m1).
2. Induce 1-2 errors per program (syntax errors, type mismatches, assertion violations).
3. Use LLM to generate repairs (modify 1-3 functions to fix errors).
4. Run dependency analysis to compute invalidation cone.
5. Measure cone_size distribution.
6. **Soundness test:** Seed verification errors in dependency-connected code, check if incremental approach catches all (detection_rate = 100%).
7. **Gate check:** SHOULD_WORK (median cone_size <30%, detection_rate = 100%).

**Actual Result:** NOT_STARTED (prerequisite h-e1, h-m1 failed).

### h-m3 (MECHANISM): Speedup Measurement

1. Take validated repair scenarios from h-m2 (100 programs × 1-2 repair iterations each).
2. For each scenario:
   - Measure batch time: re-verify entire program using Z3.
   - Measure incremental time: re-verify invalidation cone only using Z3 push/pop.
3. Compute speedup factor for each program.
4. Aggregate statistics: median, 25th percentile, 75th percentile.
5. **Scalability test (P2):** Stratify programs by LOC (10-50, 50-100), test correlation between size and speedup.
6. **Gate check:** MUST_WORK (median speedup ≥2x, 75th percentile ≥3x).

**Actual Result:** NOT_STARTED (prerequisite h-e1, h-m1, h-m2 failed).

## Fairness Considerations

**Same compute resources:** Batch and incremental verification run on same hardware (single-threaded Z3, no parallelization).

**Same LLM model:** All code generation uses Claude Sonnet 3.5 with identical prompts and temperature.

**Same static analyzer:** Pyre version consistent across all programs.

**Controlled modification scope:** Repair errors designed to require 1-3 function modifications (matches neural repair locality literature).

## Threats to Validity

**Internal Validity:** Infrastructure failure (invalid API key) blocked testing of core hypothesis. Mitigated by isolating failure mode (authentication error, not hypothesis refutation).

**External Validity:** Single language (typed Python with Pydantic), limited to HumanEval-scale programs (10-50 LOC). Generalization to Rust + Prusti or larger codebases untested.

**Construct Validity:** Speedup measured as wall-clock time (includes extraction overhead, SMT solving, dependency analysis). Extraction overhead could dominate (assumption A4 untested).

**Conclusion Validity:** No statistical tests conducted (no data). Planned analysis: Wilcoxon signed-rank test for paired speedup comparisons, Spearman correlation for size-speedup relationship (P2).

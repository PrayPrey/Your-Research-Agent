# Experiment Design: H-Z1

**Date:** 2026-08-26
**Author:** Anonymous
**Hypothesis Statement:** On a curated subset of ~50 arithmetic-heavy HumanEval problems (after Z3 spec pre-validation against EvalPlus test cases), Condition C (execution+mypy+Z3) achieves higher pass@1 than Condition B (execution+mypy), because formal counterexamples from Z3 provide a distinct error signal (constraint violation with witness) that complements mypy's type-error messages.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 ✅ PASS (41.2% overall type error rate; 70.0% on HumanEval+)
**Gate Status:** SHOULD_WORK — positive delta (Condition C > B) on curated subset

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-Z1
- **Type:** EXISTENCE
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition

SHOULD_WORK gate: Positive pass@1 delta (Condition C > Condition B) on curated ~50-problem arithmetic subset, even if not statistically significant. Secondary: ≥30 problems with valid Z3 specs.

---

## Continuation Context

H-E1 validated the foundational existence check: type errors are common in failing LLM-generated solutions (70% on HumanEval+, 0% on MBPP+). H-Z1 builds directly on H-E1's finding that HumanEval+ has a high type/structural error rate, motivating the Z3 formal-constraint sub-hypothesis.

**Key implication from H-E1:** Primary error category was `name-defined` (undefined names) on HumanEval+. For H-Z1, the curated arithmetic subset targets problems where the *semantic/arithmetic* correctness is expressible as Z3 integer arithmetic constraints — complementing mypy's type-level errors with constraint-level witness feedback.

### Previous Hypothesis Results (if applicable)

**H-E1 Summary:**
- HumanEval+: 21/30 failing solutions (70.0%) have ≥1 mypy error
- MBPP+: 0/21 (0.0%) have mypy errors
- Primary error: `name-defined` errors dominate
- Gate threshold ≥10%: SATISFIED
- **Lesson for H-Z1:** MBPP+ problems appear immune to type-level errors; curated arithmetic subset must focus on HumanEval+ problems only

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP not available in this session. Web search used as fallback.*

**Query 1: Z3 counterexample-guided repair experiment design**

Key findings from literature search:

- **Loop Invariant Generation (arXiv 2508.00419):** Hybrid LLM+Z3 framework — Z3 generates counterexample model (concrete failing input), which is passed to LLM with prompt "Refine to rule out this counterexample/error." Shows Z3 counterexamples are interpretable by LLMs in repair contexts.

- **LLM-CEGIS-Repair (AAAI 2025, pmorvalho/LLM-CEGIS-Repair):** Counterexample Guided Inductive Synthesis loop using LLM zero-shot repair + MaxSAT fault localization. Evaluated on introductory programming assignments. Demonstrates CEGIS loop architecture applicable to HumanEval-style problems.

- **ExVerus (arXiv 2603.25810):** Proof repair via counterexample reasoning — uses Z3 counterexamples to guide LLM toward correct Verus proof annotations. Direct evidence Z3 CE feedback improves LLM-based repair.

- **Specification-Guided Repair of Arithmetic Errors in Dafny (arXiv 2507.03659):** Formal specs as correctness oracles + LLM for patch generation. Arithmetic errors specifically targeted — directly relevant to H-Z1 arithmetic-heavy subset.

**Query 2: Z3 Python API and implementation patterns**

- Z3 Python API (`z3-solver` pip package) supports: integer/bitvector arithmetic, string constraints, if/else branches via `z3.If()`, counterexample extraction via `solver.model()`
- SSA-form translation of Python functions to Z3 constraints documented in multiple sources
- Standard pattern: `solver.add(Not(spec_formula))` → if SAT → `solver.model()` gives concrete failing input

**Query 3: EvalPlus/HumanEval dataset structure**

- HumanEval+: 164 problems via `load_dataset("evalplus/humanevalplus")`
- Problem types: string manipulation, math/arithmetic, list processing, sorting, algorithmic reasoning
- Each problem has: `task_id`, `prompt`, `canonical_solution`, `entry_point`, `test`
- EvalPlus adds 80x more test cases vs original HumanEval (avg 764.1 tests/problem)

### Archon Code Examples

*Archon MCP not available. Research synthesized from web sources.*

**Pattern 1: Z3 counterexample extraction**
```python
from z3 import *

def check_with_z3(spec_formula, model_variables):
    """Returns counterexample dict if spec violated, else None"""
    s = Solver()
    s.add(Not(spec_formula))
    if s.check() == sat:
        m = s.model()
        return {v.name(): m[v] for v in model_variables}
    return None  # unsat = spec satisfied
```

**Pattern 2: LLM repair prompt with Z3 witness (from loop-invariant paper)**
```python
def build_repair_prompt(problem, failed_solution, execution_errors,
                         mypy_errors, z3_counterexample):
    prompt = f"""Problem: {problem['prompt']}

Your previous solution was incorrect:
```python
{failed_solution}
```

Execution feedback: {execution_errors}
Type feedback (mypy): {mypy_errors}
Formal constraint violation (Z3 counterexample):
  Input: {z3_counterexample['inputs']}
  Your output: {z3_counterexample['actual']}
  Expected: {z3_counterexample['expected']}

Please fix the solution. The Z3 counterexample shows a specific input
where your solution violates the formal specification."""
    return prompt
```

### Exa GitHub Implementations

**Query 1: LLM-CEGIS-Repair (AAAI 2025)**

**Repository**: pmorvalho/LLM-CEGIS-Repair
- **URL**: https://github.com/pmorvalho/LLM-CEGIS-Repair
- **Relevance**: Direct CEGIS loop implementation with LLM + formal feedback; AAAI 2025 peer-reviewed
- **Architecture**: MaxSAT fault localization → program sketch → LLM synthesis → test-based CE → iterative loop
- **Key Insight**: Uses test-suite counterexamples (not Z3 directly), but architecture maps cleanly to Z3 CE variant
- **Dataset**: C-Pack-IPAs (intro programming assignments, 1431 programs) — different from HumanEval but validates CEGIS loop works
- **Results**: Outperforms zero-shot repair baseline

**Query 2: ExVerus proof repair**

**Repository**: arXiv 2603.25810 (ExVerus)
- **Relevance**: Z3-based counterexample reasoning for proof repair — shows LLMs can utilize formal CEs
- **Architecture**: Z3 CE → LLM repair prompt → recheck → iterative until proved
- **Training Config**: N/A (inference-only, GPT-4-class models)
- **Key Code Pattern**: Z3 model extraction → structured CE string → appended to LLM context

**Query 3: Loop invariant hybrid framework**

**Repository**: arXiv 2508.00419
- **Relevance**: Hybrid LLM+SMT with explicit CE feedback — closest to H-Z1 design
- **Key pattern**: Z3 returns `sat` with concrete witness → formatted as "counterexample model" → fed to LLM with repair instruction
- **Shows**: LLMs respond meaningfully to Z3 CEs in iterative repair loops

**Serena Analysis Needed**: false (no local complex codebase to analyze)

### 🎯 Implementation Priority Assessment

**CRITICAL: No single official author implementation exists for this exact experiment.** H-Z1 is a novel comparison not yet published. Build from:

1. **Primary**: evalplus library (`pip install evalplus`) for benchmark access and test execution
2. **Primary**: z3-solver library (`pip install z3-solver`) for spec encoding and CE extraction
3. **Reference**: pmorvalho/LLM-CEGIS-Repair for CEGIS loop architecture
4. **Reference**: Loop invariant paper (arXiv 2508.00419) for Z3 CE → LLM prompt pattern

**Recommended Implementation Path:**
- Primary: Custom implementation using evalplus + z3-solver + OpenAI API
- Fallback: Adapt pmorvalho/LLM-CEGIS-Repair replacing MaxSAT with Z3 arithmetic specs
- Justification: H-Z1 is a novel experiment; no prior codebase directly implements this comparison

### Code Analysis (Serena MCP)

*Skipped* - No local codebase requiring Serena analysis. Experiment uses external evalplus API and z3-solver library. Code patterns synthesized from web research.

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ Arithmetic-Heavy Curated Subset

| Field | Value |
|-------|-------|
| Source Dataset | HumanEval+ (evalplus/humanevalplus) |
| Full Size | 164 problems |
| Curated Subset | ~50 arithmetic-heavy problems (after curation + Z3 validation) |
| Expected Valid | ≥30 problems with valid Z3 specs (minimum viable subset) |
| Type | programmatic-api (real data via evalplus API) |
| Path | auto (downloaded via evalplus library) |

**Curation Criteria for Arithmetic Subset:**
1. Problem involves pure integer/float arithmetic (no complex data structures, no file I/O)
2. Input types: simple (int, float, List[int], str with numeric content)
3. Output type: numeric (int, float, bool derived from numeric comparison)
4. No string manipulation as primary operation
5. Function is pure (no side effects, no global state)

**Examples of qualifying HumanEval problems:**
- fibonacci, factorial, gcd, lcm, sum sequences
- arithmetic progressions, digit operations
- simple numeric transformations

**Z3 Spec Pre-Validation Step:**
1. For each curated problem, use GPT-4o-mini to generate Z3 spec
2. Validate spec against EvalPlus test cases (canonical solution must pass all tests with spec)
3. Discard if spec misclassifies correct solutions (false negatives)
4. Retain only problems where Z3 spec is provably correct

**Loading Information** (for Phase 4 download):
- Method: evalplus library + HuggingFace datasets
- Identifier: `"evalplus/humanevalplus"` (HuggingFace) or `evalplus.data.get_human_eval_plus()`
- Code:
```python
from evalplus.data import get_human_eval_plus
problems = get_human_eval_plus()  # dict: task_id -> problem
# OR via HuggingFace:
from datasets import load_dataset
ds = load_dataset("evalplus/humanevalplus")
```

### Models

#### Baseline Model

**Model**: GPT-4o-mini (OpenAI API)

| Field | Value |
|-------|-------|
| Provider | OpenAI API |
| Model ID | `gpt-4o-mini` |
| Initial generation temperature | 0.8 |
| Repair temperature | 0.0 (deterministic repair) |
| Max tokens | 2048 |
| Role in experiment | LLM under test for all conditions |

**Loading Information** (for Phase 4 download):
- Method: OpenAI Python SDK
- Identifier: `"gpt-4o-mini"`
- Code:
```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.0,
    max_tokens=2048
)
```

#### Proposed Model

**Architecture:** GPT-4o-mini + Z3 Formal Constraint Feedback (Condition C)

**Condition B (baseline for this comparison):**
- Feedback per repair round: execution result (pass/fail + error traceback) + mypy type errors

**Condition C (proposed — adds Z3):**
- Feedback per repair round: execution result + mypy type errors + Z3 counterexample (concrete failing input with actual vs expected output)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Z3 Spec Generation + Counterexample Extraction
# Based on: z3-solver Python API + loop invariant repair pattern (arXiv 2508.00419)

from z3 import *

def generate_z3_spec(problem_prompt, canonical_solution, llm_client):
    """Step 1: LLM generates Z3 spec from problem description."""
    spec_prompt = f"""Given this Python function specification:

{problem_prompt}

Generate a Z3 Python specification that:
1. Creates Z3 Int/Bool variables for each input
2. Encodes the expected output as a Z3 expression
3. Returns: (solver, input_vars, expected_expr)

Use z3-solver library. Only integer arithmetic constraints."""
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": spec_prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content

def validate_z3_spec(spec_code, canonical_solution, evalplus_tests):
    """Step 2: Validate spec against EvalPlus tests — reject if wrong."""
    # Execute spec against canonical_solution inputs
    # If spec says UNSAT but canonical_solution passes test → reject spec
    ...

def extract_z3_counterexample(z3_spec, candidate_solution):
    """Step 3: Find counterexample where candidate violates spec."""
    s = Solver()
    # Add: spec_constraints AND NOT(candidate_output == spec_expected)
    s.add(z3_spec.constraints)
    s.add(z3_spec.input_domain)
    s.add(candidate_output != z3_spec.expected_output)
    if s.check() == sat:
        m = s.model()
        return {"inputs": {v: m[v] for v in z3_spec.input_vars},
                "status": "counterexample_found"}
    return {"status": "no_counterexample"}  # Z3 says correct

def build_condition_c_prompt(problem, solution, exec_fb, mypy_fb, z3_ce):
    """Step 4: Repair prompt with Z3 counterexample appended."""
    ce_text = ""
    if z3_ce["status"] == "counterexample_found":
        ce_text = f"\nZ3 Formal Counterexample:\n  Input: {z3_ce['inputs']}\n"
    return f"Fix:\n{solution}\n\nExecution: {exec_fb}\nMypy: {mypy_fb}{ce_text}"
```

### Training Protocol

**This is an API-based inference experiment, not a training experiment.**

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | GPT-4o-mini | Phase 2A selection |
| Initial generation temperature | 0.8 | H-E1 validated setup |
| Repair temperature | 0.0 | Deterministic repair (reproducibility) |
| Max repair rounds (k) | 5 | H-E1 validated setup; Self-Debug shows k=3 captures most benefit |
| Seeds | 1 (single seed for PoC) | EXISTENCE hypothesis; no statistical test needed |
| Max tokens per call | 2048 | Budget constraint |
| Z3 timeout per problem | 10 seconds | Prevent solver hang on complex formulas |
| Z3 spec generation calls | 1 per problem (pre-experiment) | Offline, not per repair round |

**Experiment Conditions:**
- **Condition B**: execution feedback + mypy feedback (k=5 repair rounds)
- **Condition C**: execution feedback + mypy feedback + Z3 counterexample (k=5 repair rounds)

**Repair loop pseudocode:**
```python
for problem in curated_subset:
    solution = generate_initial(problem, temperature=0.8)
    for round in range(1, k+1):
        exec_result = evalplus_execute(problem, solution)
        if exec_result.passed: break
        mypy_fb = run_mypy(solution)
        # Condition C only:
        z3_ce = extract_z3_counterexample(problem.z3_spec, solution)
        prompt = build_repair_prompt(problem, solution, exec_result, mypy_fb, z3_ce)
        solution = llm_repair(prompt, temperature=0.0)
    record_pass_at_k(problem, solution, round)
```

**Seeds**: 1 (PoC — direction check only)

> ⚠️ **EXISTENCE (PoC)**: Single run sufficient. No multi-seed required for direction check.

### Evaluation

**Primary Metrics:**
- `pass@1` at k=5 on curated arithmetic subset — Condition C vs Condition B
- Delta: `pass@1_C - pass@1_B` (must be > 0 for PoC success)

**Secondary Metrics:**
- Subset size after Z3 validation (must be ≥30 for meaningful comparison)
- Z3 spec validity rate (fraction of curated problems with valid specs)
- Z3 counterexample found rate (fraction of failing solutions where Z3 finds CE)

**Success Criteria:**
- **PoC Pass**: `pass@1_C > pass@1_B` on validated arithmetic subset
- **Minimum subset**: ≥30 problems with valid Z3 specs
- Statistical significance NOT required (EXISTENCE/PoC gate is direction only)

**Expected Baseline Performance** (from research):
- HumanEval+ no-repair baseline: ~55-60% pass@1 (GPT-4o-mini, estimated)
- HumanEval+ with execution-only repair k=3: ~65-70% (Self-Debug analogs)
- Condition B (execution+mypy, k=5): expected ~68-73% on arithmetic subset (type errors high per H-E1)
- Expected delta (C-B): +2 to +5 percentage points if Z3 CE signal is actionable

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation / pass@1
- Library: evalplus (built-in test execution)
- Code:
```python
from evalplus.eval import evaluate_functional_correctness
# OR manual:
result = exec_and_check(solution_code, problem["test"], problem["entry_point"])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — pass@1 Condition B vs Condition C on validated arithmetic subset

#### Additional Figures (LLM Autonomous)

Based on the experiment structure, the following additional figures are recommended:

1. **Z3 Validation Funnel**: Stacked bar — curated problems (N~50) → Z3 spec generated → Z3 spec validated → used in experiment (shows subset pipeline)
2. **Per-round pass@1 curve**: Line chart — Condition B vs C across repair rounds k=1..5 (shows where Z3 CE helps most)
3. **Z3 CE found rate**: Histogram — fraction of failing solutions where Z3 finds counterexample vs no CE (shows Z3 signal availability)
4. **Problem difficulty scatter**: X-axis = Condition B pass rate, Y-axis = Condition C pass rate — identifies problem categories where Z3 adds value

**Output Location**: `docs/youra_research/h-z1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (full repair loop for both conditions)
2. `pass@1_C > pass@1_B` on validated arithmetic subset (≥30 problems)
3. ≥30 problems have valid Z3 specs (minimum viable experiment)

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon MCP unavailable)

**Source A.1**: Loop Invariant Generation (arXiv 2508.00419)
- **Type**: Research paper (hybrid LLM+Z3)
- **Query Used**: "Z3 SMT solver LLM code repair formal verification counterexample feedback"
- **Key Insights**:
  - Z3 counterexample model (concrete failing input) passed directly to LLM in repair prompt
  - Prompt instruction: "Refine to rule out this counterexample/error"
  - LLMs respond meaningfully to structured Z3 witness feedback
- **Used For**: Z3 CE → repair prompt design (Section Training Protocol + pseudocode)

**Source A.2**: ExVerus (arXiv 2603.25810)
- **Type**: Research paper (proof repair via Z3 CE reasoning)
- **Query Used**: "Z3 python LLM code repair counterexample guided HumanEval arithmetic"
- **Key Insights**:
  - Z3 counterexamples drive LLM repair toward correct formal proofs
  - Architecture: Z3 CE → structured string → appended to LLM context → recheck loop
- **Used For**: Architecture of Condition C repair loop

**Source A.3**: Specification-Guided Repair of Arithmetic Errors in Dafny (arXiv 2507.03659)
- **Type**: Research paper
- **Query Used**: "evalplus HumanEval arithmetic problems Z3 formal specification LLM code generation repair"
- **Key Insights**:
  - Formal specs as correctness oracles + LLM patches — directly targets arithmetic errors
  - Validates that arithmetic-heavy subset is the right target for formal spec feedback
- **Used For**: Motivation for arithmetic-heavy subset selection

### B. GitHub Implementations (Web Search)

**Repository B.1**: pmorvalho/LLM-CEGIS-Repair (AAAI 2025)
- **URL**: https://github.com/pmorvalho/LLM-CEGIS-Repair
- **Query Used**: "LLM-CEGIS-Repair counterexample guided program repair GitHub pmorvalho"
- **Relevance**: CEGIS loop with LLM + formal feedback; peer-reviewed AAAI 2025
- **Architecture Extracted**: MaxSAT fault localization → sketch → LLM → CE → loop
- **Used For**: CEGIS loop architecture reference for Condition C repair loop

**Repository B.2**: z3-solver PyPI / z3prover.github.io
- **URL**: https://pypi.org/project/z3-solver/ + https://z3prover.github.io/api/html/z3.z3.html
- **Query Used**: "z3-solver python pip API counterexample generation code repair LLM feedback"
- **Key Code**:
```python
from z3 import *
s = Solver()
s.add(Not(spec_formula))
if s.check() == sat:
    m = s.model()
    ce = {v.name(): m[v] for v in input_vars}
```
- **Used For**: Z3 counterexample extraction pattern (core mechanism pseudocode)

**Repository B.3**: evalplus/humanevalplus (HuggingFace)
- **URL**: https://huggingface.co/datasets/evalplus/humanevalplus
- **Query Used**: "evalplus load_dataset huggingface evalplus/humanevalplus python code"
- **Loading Code**: `from evalplus.data import get_human_eval_plus`
- **Used For**: Dataset loading specification

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — no local codebase requiring semantic analysis. All implementation patterns synthesized from published research and API documentation.

### D. Previous Hypothesis Context

**Source**: H-E1 Phase 4 Validation Report
- **Reused Components**:
  - Model: GPT-4o-mini (same)
  - Benchmarks: HumanEval+ (same; MBPP+ excluded for H-Z1 — 0% type errors, Z3 less relevant)
  - Temperature: 0.8 initial / 0.0 repair (same)
  - k=5 repair rounds (same)
- **Why Reused**: Enables controlled experiment — only the Z3 feedback channel changes
- **New in H-Z1**: Z3 spec generation + CE extraction + Condition C prompt

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|-----------------|
| Curated arithmetic subset design | Research rationale | H-E1 finding: 70% HumanEval+ has type/structural errors |
| Z3 CE repair loop architecture | arXiv paper | A.1 (loop invariant paper), A.2 (ExVerus) |
| Z3 Python API pattern | Official docs | B.2 (z3-solver PyPI + API docs) |
| Dataset loading | HuggingFace | B.3 (evalplus/humanevalplus) |
| CEGIS loop structure | AAAI 2025 | B.1 (LLM-CEGIS-Repair) |
| Arithmetic subset motivation | arXiv paper | A.3 (Dafny arithmetic repair) |
| Training protocol (k, temp) | Prior hypothesis | D.1 (H-E1 validated setup) |
| Evaluation metric (pass@1) | Framework | evalplus built-in evaluation |
| Z3 spec pre-validation | Research rationale | Phase 2B A5 assumption |
| PoC success criterion | Phase 2B | H-Z1 specification (direction only) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written to file)
**Date:** 2026-08-26T00:00:00Z

### Workflow History for This Hypothesis

- 2026-08-26T08:47:17: H-Z1 set to IN_PROGRESS
- 2026-08-26: Phase 2C experiment design executed (UNATTENDED mode)
- 2026-08-26: experiment_design.status → COMPLETED

---

*MCP Tools Used: Web Search (Archon/Exa MCP unavailable in session)*
*Sources: arXiv 2508.00419, arXiv 2603.25810, arXiv 2507.03659, AAAI 2025 (pmorvalho/LLM-CEGIS-Repair), z3-solver PyPI, evalplus/humanevalplus HuggingFace*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

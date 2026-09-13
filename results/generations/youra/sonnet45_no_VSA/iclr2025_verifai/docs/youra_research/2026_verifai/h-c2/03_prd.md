# Product Requirements Document (PRD)

**Hypothesis:** h-c2  
**Date:** 2026-07-11  
**Author:** Anonymous  
**Status:** Draft → Review → Approved

---

## Executive Summary

### Product Vision
Implement a mutation testing framework to validate the semantic strength of synthesized ACSL specifications. This system will demonstrate that specifications generated via structured feedback (validated in h-m1) are non-vacuous by achieving ≥70% mutation kill rate relative to expert-written specifications.

### Success Criteria (Gate: MUST_WORK)
- ✅ Mutation kill rate ≥70% of gold specification baseline
- ✅ Framework successfully processes 30+ programs from ACSL-by-Example
- ✅ Automated end-to-end pipeline: synthesis → mutation → verification → metrics

### Business Value
Validates that structured feedback produces semantically meaningful specifications, not just syntactically correct ones. Critical validation for the entire YouRA approach—if specifications are vacuous, the information gradient finding (h-m1) is undermined.

---

## Problem Statement

### Core Problem
Need to verify that ACSL specifications synthesized with structured feedback (h-m1) detect semantic bugs, not just satisfy verification tools vacuously.

### Current State
- h-m1 validated information gradient: FullStructured feedback achieves 70.12% proof discharge
- Unknown whether high discharge rate reflects semantic strength or vacuous specifications
- No automated framework exists to test specification quality via mutation testing

### Target State
- Mutation testing framework for ACSL specifications
- Quantitative measure of specification strength (kill rate)
- Comparison baseline using expert-written gold specs from ACSL-by-Example

---

## Functional Requirements

### FR1: Dataset Management
**Priority:** P0 (Critical Path)

**Description:** Load and preprocess ACSL-by-Example benchmark programs with gold specifications.

**Acceptance Criteria:**
- Load 30 programs from ACSL-by-Example repository (stratified sampling)
- Parse C code and extract ACSL annotations
- Verify programs compile with Frama-C 32.0
- Store program metadata (LOC, complexity, function count)

**Technical Details:**
```python
# Dataset structure
Dataset = {
    "programs": List[Program],
    "gold_specs": Dict[str, ACSLSpec],
    "metadata": Dict[str, ProgramMetadata]
}

Program = {
    "id": str,
    "c_code": str,
    "gold_spec": ACSLSpec,
    "loc": int,
    "functions": List[str]
}
```

**Dependencies:** None (foundation requirement)

---

### FR2: ACSL Specification Synthesis
**Priority:** P0 (Critical Path)

**Description:** Synthesize ACSL specifications using structured feedback mechanism from h-m1.

**Acceptance Criteria:**
- LLM API integration (Claude Opus or GPT-4)
- Temperature = 0.0 (deterministic synthesis)
- Max 10 refinement iterations
- FullStructured feedback condition (validated in h-m1)
- Frama-C/WP verification loop

**Technical Details:**
```python
def synthesize_spec(c_program: str, llm_client) -> ACSLSpec:
    """
    Synthesize ACSL specification using structured feedback.
    Returns: ACSL annotations (preconditions, postconditions, invariants)
    """
    prompt = build_synthesis_prompt(c_program, feedback_type="FullStructured")
    iterations = 0
    while iterations < 10:
        spec = llm_client.generate(prompt, temperature=0.0)
        if verify_with_frama_c(c_program, spec):
            return spec
        prompt = refine_prompt_with_feedback(prompt, spec, feedback="FullStructured")
        iterations += 1
    raise SynthesisFailure(f"Failed after {iterations} iterations")
```

**Dependencies:** FR1 (requires programs), h-m1 validated mechanism

---

### FR3: Mutation Operator Implementation
**Priority:** P0 (Critical Path)

**Description:** Implement 12 mutation operators for C code transformation.

**Acceptance Criteria:**
- Arithmetic operators (3): `+`↔`-`, `*`↔`/`, `++`↔`--`
- Relational operators (3): `<`↔`<=`, `>`↔`>=`, `==`↔`!=`
- Boolean operators (2): `&&`↔`||`, `!` insertion/deletion
- Statement operators (2): delete statement, change constant (±1)
- Boundary operators (2): array index ±1, loop bound ±1
- AST-based mutation (not string replacement)
- Compilable mutants only

**Technical Details:**
```python
class MutationOperator(ABC):
    @abstractmethod
    def apply(self, ast: CAST) -> List[CAST]:
        """Generate mutants from AST"""
        pass

class ArithmeticMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[CAST]:
        """Mutate arithmetic operators"""
        mutants = []
        for node in ast.walk():
            if node.type == "BinaryOp":
                if node.op == "+":
                    mutants.append(ast.clone_with_change(node, op="-"))
        return mutants

# 12 operator classes total
```

**Dependencies:** None (independent implementation)

---

### FR4: Mutation Testing Engine
**Priority:** P0 (Critical Path)

**Description:** Generate mutants, verify with Frama-C, compute kill rates.

**Acceptance Criteria:**
- Apply all 12 operators to each program
- Run Frama-C/WP on each (mutant, spec) pair
- 10-second timeout per verification
- Classify: Killed (verification failed) vs Survived (verification passed)
- Parallel execution support (multi-core)

**Technical Details:**
```python
def compute_kill_rate(program: Program, spec: ACSLSpec) -> KillRateResult:
    """
    Main mutation testing function.
    Returns: {total_mutants, killed, survived, kill_rate}
    """
    mutants = generate_all_mutants(program.c_code, mutation_operators)
    results = []
    
    for mutant in mutants:
        annotated = insert_acsl_spec(mutant, spec)
        verification = run_frama_c(annotated, timeout=10)
        killed = (verification.status == "FAILED")
        results.append({"mutant": mutant, "killed": killed})
    
    killed_count = sum(1 for r in results if r["killed"])
    kill_rate = (killed_count / len(mutants)) * 100 if mutants else 0.0
    
    return {
        "total_mutants": len(mutants),
        "killed": killed_count,
        "survived": len(mutants) - killed_count,
        "kill_rate": kill_rate
    }
```

**Dependencies:** FR2 (specs), FR3 (operators)

---

### FR5: Baseline Comparison
**Priority:** P0 (Gate Validation)

**Description:** Compute mutation kill rates for expert-written gold specifications and compare with synthesized specs.

**Acceptance Criteria:**
- Run mutation testing on gold specs from ACSL-by-Example
- Same 30 programs, same mutation operators
- Statistical comparison: synthesized_kill_rate vs gold_kill_rate
- Gate check: `synthesized_kill_rate >= 0.70 * gold_kill_rate`

**Technical Details:**
```python
def validate_gate_condition(results: List[KillRateResult]) -> bool:
    """
    Gate: MUST_WORK
    Threshold: Synthesized ≥ 70% of gold baseline
    """
    synthesized_rates = [r.synthesized_kill_rate for r in results]
    gold_rates = [r.gold_kill_rate for r in results]
    
    mean_synthesized = np.mean(synthesized_rates)
    mean_gold = np.mean(gold_rates)
    
    threshold = 0.70 * mean_gold
    gate_passed = mean_synthesized >= threshold
    
    return {
        "gate_passed": gate_passed,
        "synthesized_mean": mean_synthesized,
        "gold_mean": mean_gold,
        "threshold": threshold,
        "relative_performance": mean_synthesized / mean_gold
    }
```

**Dependencies:** FR2 (synthesis), FR4 (mutation engine)

---

### FR6: Metrics and Visualization
**Priority:** P1 (Required for analysis)

**Description:** Compute secondary metrics and generate publication-quality figures.

**Acceptance Criteria:**
- Mutation kill rate (primary metric)
- Proof discharge rate (from h-m1 context)
- Specification completeness (% functions with contracts)
- Verification time (wall-clock)

**Figures Required:**
1. **Gate Metrics Comparison** (mandatory): Bar chart of kill rates (Synthesized vs Gold)
2. Kill Rate Distribution: Histogram across 30 programs
3. Mutation Operator Effectiveness: Bar chart per operator type
4. Specification Strength vs Proof Discharge: Scatter plot
5. Program Complexity vs Kill Rate: Scatter plot

**Technical Details:**
```python
def generate_figures(results: List[KillRateResult], output_dir: Path):
    """Generate all required figures"""
    figures = {
        "gate_comparison": plot_kill_rate_comparison(results),
        "kill_rate_dist": plot_histogram(results),
        "operator_effectiveness": plot_operator_breakdown(results),
        "strength_vs_discharge": plot_scatter(x="proof_discharge", y="kill_rate"),
        "complexity_vs_kill": plot_scatter(x="loc", y="kill_rate")
    }
    
    for name, fig in figures.items():
        fig.savefig(output_dir / f"{name}.png", dpi=300)
```

**Dependencies:** FR4 (results), FR5 (comparison)

---

### FR7: End-to-End Pipeline
**Priority:** P0 (Integration)

**Description:** Automated pipeline orchestrating all components.

**Acceptance Criteria:**
- Single entry point: `python run_experiment.py --hypothesis h-c2`
- Sequential execution: Load → Synthesize → Mutate → Verify → Compare → Visualize
- Checkpointing (resume from failures)
- Logging and progress tracking
- Output: `04_validation.md` report with results

**Technical Details:**
```python
def run_h_c2_experiment(config: ExperimentConfig):
    """Main experiment orchestration"""
    # 1. Load dataset
    programs = load_acsl_by_example(num_programs=30)
    
    # 2. Synthesize specifications
    synthesized_specs = [synthesize_spec(p, llm_client) for p in programs]
    
    # 3. Run mutation testing (both synthesized and gold)
    results = []
    for program, synth_spec in zip(programs, synthesized_specs):
        synth_result = compute_kill_rate(program, synth_spec)
        gold_result = compute_kill_rate(program, program.gold_spec)
        results.append({"synth": synth_result, "gold": gold_result})
    
    # 4. Validate gate condition
    gate = validate_gate_condition(results)
    
    # 5. Generate figures
    generate_figures(results, output_dir="figures/")
    
    # 6. Write validation report
    write_validation_report(gate, results, output_file="04_validation.md")
    
    return gate["gate_passed"]
```

**Dependencies:** All FRs

---

## Non-Functional Requirements

### NFR1: Performance
- Mutation testing: ≤2 hours for 30 programs (with parallelization)
- Frama-C verification timeout: 10 seconds per mutant
- LLM synthesis: ≤60 seconds per program (10 iterations max)

### NFR2: Reliability
- Handle Frama-C crashes gracefully (skip mutant, log error)
- Retry LLM API calls on timeout (3 retries, exponential backoff)
- Validate all inputs (C code parseable, ACSL syntax correct)

### NFR3: Reproducibility
- Deterministic LLM synthesis (temperature=0.0)
- Fixed random seed for program sampling
- Version-pinned dependencies (Frama-C 32.0, Python 3.10+)
- Docker container for verification stack

### NFR4: Observability
- Progress logging (INFO level): synthesis status, mutant generation, verification results
- Checkpoint files: resume from last completed program
- Detailed error logs: Frama-C stderr, LLM API errors

---

## Data Requirements

### Input Data

**Primary Dataset: ACSL-by-Example**
- **Source:** https://github.com/fraunhoferfokus/acsl-by-example
- **Size:** 604+ verified C programs
- **Format:** C files with ACSL annotations
- **Subset:** 30 programs (stratified sampling by complexity)
- **Loading:**
  ```bash
  git clone https://github.com/fraunhoferfokus/acsl-by-example
  cd acsl-by-example/StandardAlgorithms/
  ```

**Secondary Dataset: Juliet Test Suite (Optional)**
- **Source:** https://github.com/arichardson/juliet-test-suite-c
- **Size:** 64,099 test cases
- **Usage:** Extended evaluation (not required for gate)

### Output Data

**Validation Report:** `h-c2/04_validation.md`
- Gate pass/fail status
- Mean kill rates (synthesized vs gold)
- Per-program results table
- Figure references

**Figures:** `h-c2/figures/`
- `gate_comparison.png` (mandatory)
- `kill_rate_dist.png`
- `operator_effectiveness.png`
- `strength_vs_discharge.png`
- `complexity_vs_kill.png`

**Checkpoints:** `h-c2/checkpoints/`
- `synthesized_specs.json` (resume synthesis)
- `mutation_results.json` (resume testing)

---

## Dependencies and Interfaces

### External APIs
- **Anthropic Claude API** (or OpenAI GPT-4)
  - Endpoint: `https://api.anthropic.com/v1/messages`
  - Model: `claude-opus-4-8`
  - Rate limit: 40k tokens/min
  - Authentication: API key (environment variable)

### External Tools
- **Frama-C 32.0** (deductive verification)
  - Command: `frama-c -wp -wp-timeout 10 <file>`
  - Provers: Alt-Ergo, Z3, CVC5
  - Installation: Docker image `framac/frama-c:32.0`

### Internal Dependencies
- **Prerequisite Hypothesis:** h-m1 (Information Gradient - VALIDATED)
  - Dependency: FullStructured feedback mechanism
  - Files: `h-m1/03_logic.md`, `h-m1/03_config.md`
  - Reuse: Feedback generation logic, prompt templates

### System Requirements
- **Platform:** Linux (Ubuntu 22.04+)
- **Python:** 3.10+
- **RAM:** 16GB (parallel mutation testing)
- **Disk:** 10GB (dataset + mutants)
- **Docker:** 20.10+ (Frama-C container)

---

## Success Metrics

### Primary Metrics (Gate Validation)

**Metric 1: Mutation Kill Rate**
- **Formula:** `(killed_mutants / total_mutants) × 100%`
- **Baseline:** Gold spec kill rate (expected 80-95%)
- **Target:** Synthesized ≥ 70% of gold baseline
- **Gate:** MUST_WORK (failure invalidates approach)

### Secondary Metrics (Analysis)

**Metric 2: Proof Discharge Rate** (from h-m1 context)
- **Expected:** ≥70% (FullStructured feedback)
- **Purpose:** Correlation analysis with kill rate

**Metric 3: Specification Completeness**
- **Formula:** `(functions_with_contracts / total_functions) × 100%`
- **Target:** ≥90%

**Metric 4: Verification Time**
- **Measure:** Wall-clock time per mutant (Frama-C/WP)
- **Target:** ≤10 seconds (timeout threshold)

### Quality Metrics

**Metric 5: Operator Coverage**
- **Formula:** `(operators_with_kills / total_operators) × 100%`
- **Target:** All 12 operators detect ≥1 bug

**Metric 6: Compilability**
- **Formula:** `(compilable_mutants / generated_mutants) × 100%`
- **Target:** ≥95% (AST-based mutation should ensure this)

---

## Risks and Mitigations

### Risk 1: Low Kill Rate (Gate Failure)
**Impact:** HIGH - Invalidates h-m1 findings  
**Probability:** MEDIUM  
**Mitigation:**
- Pre-validate synthesis on 5 programs before full run
- If <50%, escalate to Phase 4.5 reflection
- Consider prompt refinement or alternative LLMs

### Risk 2: Frama-C Verification Timeouts
**Impact:** MEDIUM - Incomplete results  
**Probability:** HIGH  
**Mitigation:**
- 10-second timeout per mutant (configurable)
- Skip timed-out mutants (exclude from denominator)
- Report timeout rate as quality metric

### Risk 3: Dataset Availability
**Impact:** MEDIUM - Cannot run experiment  
**Probability:** LOW  
**Mitigation:**
- Fallback to Juliet Test Suite
- Manual curation of 10 simple programs if both fail
- Pre-download during setup phase

### Risk 4: LLM API Rate Limits
**Impact:** LOW - Delayed completion  
**Probability:** MEDIUM  
**Mitigation:**
- Exponential backoff (3 retries)
- Batch synthesis (checkpoint after each program)
- Fallback to local model (CodeLlama) if critical

---

## Open Questions

1. **Mutation operator selection:** Use all 12 or subset? → **Decision:** All 12 (comprehensive coverage)
2. **Sample size:** 30 programs sufficient? → **Decision:** Yes (80% power for effect size 0.5)
3. **LLM choice:** Claude Opus vs GPT-4? → **Decision:** Claude Opus (validated in h-m1)
4. **Timeout value:** 10 seconds appropriate? → **Decision:** Yes (based on Frama-C benchmarks)

---

## Appendix

### A. Mutation Operator Reference

| Category | Operator | Example |
|----------|----------|---------|
| Arithmetic | ADD_TO_SUB | `a + b` → `a - b` |
| Arithmetic | MUL_TO_DIV | `a * b` → `a / b` |
| Arithmetic | INC_TO_DEC | `i++` → `i--` |
| Relational | LT_TO_LEQ | `a < b` → `a <= b` |
| Relational | GT_TO_GEQ | `a > b` → `a >= b` |
| Relational | EQ_TO_NEQ | `a == b` → `a != b` |
| Boolean | AND_TO_OR | `a && b` → `a \|\| b` |
| Boolean | NEGATE_COND | `if (x)` → `if (!x)` |
| Statement | DELETE_STMT | Remove statement |
| Statement | CHANGE_CONST | `x = 5` → `x = 6` |
| Boundary | ARRAY_OFF_BY_ONE | `a[i]` → `a[i+1]` |
| Boundary | LOOP_BOUND_SHIFT | `i < n` → `i < n-1` |

### B. Frama-C Verification Stack

```
ACSL Specification (preconditions, postconditions, invariants)
          ↓
   Frama-C WP Plugin (Weakest Precondition calculus)
          ↓
   Why3 (Intermediate verification language)
          ↓
   SMT Solvers (parallel)
   ├── Alt-Ergo (native)
   ├── Z3 (fallback)
   └── CVC5 (complex arithmetic)
          ↓
   Proof Obligation Result (Valid / Invalid / Unknown)
```

### C. Related Work

- **mutmut** (Python mutation testing): AST-based operator reference
- **evidence** (contract testing): Mutation + property validation pattern
- **ACSL-by-Example** (benchmark): Gold specification source
- **SESpec** (LLM synthesis): State-of-the-art ACSL generation (2026)
- **ac-trace** (traceability): Mutation kill rate methodology

---

**Document Status:** Ready for Architecture Design (Step 3)  
**Next Step:** Architecture Agent (define system components, data flow, Epic breakdown)

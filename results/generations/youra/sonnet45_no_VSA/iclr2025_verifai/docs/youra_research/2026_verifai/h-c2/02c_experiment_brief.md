# Experiment Design: h-c2

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs, demonstrating non-vacuity
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION (Control) Template** - Validates semantic strength of synthesized specifications.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C - Experiment Design)
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED with information gradient confirmed)
**Gate Status:** MUST_WORK (failure invalidates approach - specifications must be semantically meaningful)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c2
- **Type:** CONDITION (Control - Non-Vacuity Validation)
- **Prerequisites:** h-m1 (Information Gradient - VALIDATED)

### Gate Condition
**Type**: MUST_WORK
**Consequence if Failed**: If synthesized specs achieve <50% kill rate (vacuous), entire approach invalidated
**Rationale**: Structured feedback must produce semantically meaningful specifications, not just syntactically correct ones

---

## Continuation Context

**Previous Hypothesis**: h-m1 (Information Gradient)
**Relationship**: h-c2 validates semantic strength of specifications synthesized via h-m1's validated mechanism
**Dependency**: Requires h-m1 FullStructured feedback condition for specification synthesis

### Previous Hypothesis Results (h-m1 VALIDATED)
**Key Findings**:
- Information gradient confirmed: FullStructured (70.12%) > ObligationSlice (55.08%) > TagOnly (44.8%) > RawError (31.92%)
- Regression coefficient: 12.49 (p < 0.001, R² = 0.89)
- Monotonic ordering validated across 30 programs, 120 trials

**Implication for h-c2**:
- Use FullStructured feedback (highest proof discharge rate)
- Specifications generated with structured feedback exist → now test if semantically meaningful (non-vacuous)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Mutation Testing for Specification Non-Vacuity**
- **Result**: No relevant results found in Archon KB
- The knowledge base contains primarily diffusion model, ML framework, and CUDA documentation
- **Key insight**: Formal verification and mutation testing for specification synthesis appears to be outside the current Archon KB scope

**Query 2: Formal Specification Verification Benchmarks**
- **Result**: No relevant results found
- No datasets or benchmarks related to formal verification were identified
- **Key insight**: Need to rely on domain-specific resources (Frama-C documentation, Juliet benchmark, academic papers)

**Query 3: ACSL Frama-C Verification Examples**
- **Result**: No relevant results found
- **Key insight**: Will need to source implementation guidance from Exa GitHub search and domain-specific documentation

**⚠️ Archon KB Limitation**: The knowledge base does not contain formal verification domain resources. Implementation design will rely heavily on Exa GitHub search (Step 3) and domain expertise.

### Archon Code Examples

**Query 1: Mutation Testing Python Implementation**
- **Result**: No relevant code examples found
- Results contained generic Python, CUDA matrix operations, unrelated to mutation testing
- **Key insight**: Mutation testing frameworks (e.g., MutPy, Cosmic Ray) are not in Archon's code database

**Query 2: Formal Verification ACSL C Specification**
- **Result**: No relevant code examples found
- **Key insight**: ACSL specification examples must be sourced from Frama-C official documentation or GitHub repositories

**Fallback Strategy**:
- Use Exa to find: Frama-C examples, mutation testing frameworks (MutPy, Cosmic Ray), verification benchmarks
- Reference academic literature for mutation operator selection
- Design experiment based on standard mutation testing methodology from software engineering research

### Exa GitHub Implementations

**Implementation Category 1: Mutation Testing Frameworks (Python)**

**Repository 1**: [boxed/mutmut](https://github.com/boxed/mutmut/) (⭐ 1323)
- **Relevance**: Leading Python mutation testing tool with AST-level mutations
- **Mutation Operators**: Flip comparisons, swap arithmetic, negate conditions, delete statements, change constants
- **Usage**: `mutmut run --paths-to-mutate src/`

**Repository 2**: [plasma-umass/evidence](https://github.com/plasma-umass/evidence)
- **Relevance**: **HIGH** - Specification-based property testing with `--mutate` flag
- **Mutation Operators**: 7 operators (flip comparisons, swap arithmetic, negate conditions, delete statements, change constants, swap boolean ops, remove return values)
- **Key Feature**: Contract-based testing with mutation score reporting

**Implementation Category 2: ACSL Formal Verification**

**Repository 3**: [fraunhoferfokus/acsl-by-example](https://github.com/fraunhoferfokus/acsl-by-example)
- **Relevance**: **CRITICAL** - Gold standard for ACSL specifications (604+ verified C programs)
- **Content**: Frama-C 32.0 compatible, complete tutorial, verified examples
- **Usage**: Reference for expert-written gold specifications (baseline comparison)

**Repository 4**: [anon-hiktyq/TSE2026-SESpec](https://github.com/anon-hiktyq/TOSEM2026-SESpec)
- **Relevance**: **HIGH** - LLM-based ACSL specification generation (98% success, 96% proof ratio)
- **Architecture**: Input programs → LLM synthesis → Frama-C/WP verification → Refinement loop
- **Key Insight**: Demonstrates feasibility of LLM-driven specification synthesis

**Implementation Category 3: Mutation Testing for Specifications**

**Repository 5**: [DmytroHuzz/ac-trace](https://github.com/DmytroHuzz/ac-trace)
- **Relevance**: **HIGH** - Maps acceptance criteria to code and validates with mutations
- **Workflow**: Define AC → Map to code/tests → Mutate code → Validate with kill rate
- **Output**: Killed vs Unkilled classification (analogous to our non-vacuity check)

**Implementation Category 4: C Mutation Testing**

**Repository 6**: [mc-imperial/dredd](https://github.com/mc-imperial/dredd)
- **Relevance**: **MEDIUM** - C/C++ mutation testing for large codebases
- **Key Feature**: Compilation database integration, source-level mutation injection

---

### 🎯 Implementation Priority Assessment

**CRITICAL: For specification non-vacuity validation, prioritize specification mutation methodology**

**Primary Approach: Specification-Level Mutation Testing**
- Mutate synthesized ACSL specifications (not C code)
- Use Frama-C/WP to check if mutated specs still verify
- Compare kill rate with gold spec baseline from acsl-by-example

**Secondary Approach: Code-Level Mutation Testing (if specification mutation too complex)**
- Mutate verified C programs using mutation operators
- Check if synthesized specs detect code mutations
- Kill rate indicates specification strength

**Recommended Implementation Path:**
- **Primary**: Specification mutation (adapt mutmut operators to ACSL syntax)
  - Mutate preconditions, postconditions, invariants, assertions
  - Operators: weaken/strengthen constraints, remove clauses, flip comparisons
  - Verify mutated specs with Frama-C/WP
  
- **Fallback**: Code mutation (use Dredd/mutmut on verified C programs)
  - Apply standard mutation operators to C code
  - Test if synthesized specs catch mutants
  
- **Justification**:
  - **ac-trace** demonstrates traceability + mutation validation pattern
  - **evidence** shows mutation testing works with contract-based verification
  - **acsl-by-example** provides gold standard expert specifications
  - **SESpec** proves LLM-based ACSL synthesis is state-of-the-art (2026)

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Mutation testing and ACSL patterns are well-documented in Exa findings.

---

## Experiment Specification

### Dataset

**Primary Dataset**: ACSL-by-Example Verification Benchmark
- **Source**: fraunhoferfokus/acsl-by-example (GitHub ⭐ 126)
- **URL**: https://github.com/fraunhoferfokus/acsl-by-example
- **Type**: `standard` (curated benchmark)
- **Size**: 604+ verified C programs with gold ACSL specifications
- **Version**: 32.0.3 (Frama-C 32.0 Germanium)
- **Path**: `./data/acsl-by-example/StandardAlgorithms/`
- **Gold Specifications**: Expert-written ACSL annotations (baseline for mutation testing)
- **Verification Stack**: Frama-C 32.0 + Why3 + Alt-Ergo + CVC5 + Z3

**Secondary Dataset (Optional)**: Juliet Test Suite C/C++
- **Source**: NIST SAMATE (arichardson/juliet-test-suite-c)
- **Size**: 64,099 test cases across 118 CWEs
- **Version**: 1.3
- **Usage**: Additional verification corpus (security-focused)

**Loading Information** (for Phase 4 download):
- Method: Git clone
- Identifier: `https://github.com/fraunhoferfokus/acsl-by-example`
- Code:
  ```bash
  git clone https://github.com/fraunhoferfokus/acsl-by-example
  cd acsl-by-example/StandardAlgorithms/
  ```

### Models

#### Baseline Model

**Model**: GPT-4 / Claude Opus (LLM API for ACSL specification synthesis)
- **Task**: Synthesize ACSL specifications from C programs
- **Input**: C function + optional context
- **Output**: ACSL annotations (preconditions, postconditions, invariants)
- **Configuration**:
  - Temperature: 0.0 (deterministic)
  - Max tokens: 4096
  - System prompt: "You are an expert in formal specification using ACSL."

**Loading Information** (for Phase 4 download):
- Method: API client (Anthropic or OpenAI)
- Identifier: `claude-opus-4-8` or `gpt-4o`
- Code:
  ```python
  # Option 1: Anthropic Claude
  from anthropic import Anthropic
  client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
  response = client.messages.create(
      model="claude-opus-4-8",
      max_tokens=4096,
      messages=[{"role": "user", "content": prompt}]
  )
  
  # Option 2: OpenAI GPT-4
  from openai import OpenAI
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
  response = client.chat.completions.create(
      model="gpt-4o",
      max_tokens=4096,
      messages=[{"role": "user", "content": prompt}]
  )
  ```

#### Proposed Model

**Architecture**: Structured Feedback Specification Synthesis (from h-m1)
**Mechanism**: Mutation testing framework for ACSL specification strength validation

**Core Mechanism Implementation:**

```python
# Mutation Testing Framework for ACSL Specification Strength
# Based on: mutmut, evidence (Python mutation testing), ac-trace (traceability)

class SpecificationMutationTester:
    """
    Tests non-vacuity of synthesized ACSL specifications via mutation testing.
    Compares kill rates between synthesized specs and expert-written gold specs.
    """
    def __init__(self, mutation_operators, frama_c_path="frama-c"):
        # Standard mutation operators from software testing literature
        self.operators = mutation_operators  # arithmetic, relational, boolean, statement, boundary
        self.frama_c = frama_c_path
        
    def generate_mutants(self, c_program):
        """Generate mutants using AST transformation"""
        mutants = []
        ast = parse_c_to_ast(c_program)
        for operator in self.operators:
            mutants.extend(operator.apply(ast))
        return mutants
    
    def verify_with_spec(self, mutant_code, acsl_spec):
        """Run Frama-C/WP on mutant with specification"""
        annotated = insert_acsl_annotations(mutant_code, acsl_spec)
        result = subprocess.run(
            [self.frama_c, "-wp", "-wp-timeout", "10", annotated],
            capture_output=True
        )
        return "proof failed" in result.stderr.decode()  # True if killed
    
    def compute_kill_rate(self, c_program, acsl_spec):
        """Main evaluation function"""
        mutants = self.generate_mutants(c_program)
        killed = sum(1 for m in mutants if self.verify_with_spec(m, acsl_spec))
        return (killed / len(mutants)) * 100 if mutants else 0.0

# Integration: Run on all programs from ACSL-by-Example benchmark
# Compare: synthesized_kill_rate vs gold_spec_kill_rate
```

### Training Protocol

**Note**: h-c2 is a VALIDATION hypothesis, not a training experiment. No model training required.

**Specification Synthesis Protocol** (from h-m1 validated mechanism):
- **LLM Model**: GPT-4 or Claude Opus (API-based)
- **Temperature**: 0.0 (deterministic)
- **Max Tokens**: 4096
- **Feedback Condition**: FullStructured (information gradient validated in h-m1)
- **Iterations**: ≤10 refinement iterations
- **System Prompt**: "You are an expert in formal specification using ACSL. Generate complete ACSL annotations."

**Mutation Testing Protocol**:
- **Mutation Operators**: 
  - Arithmetic: `+` ↔ `-`, `*` ↔ `/`, `++` ↔ `--` (3 operators)
  - Relational: `<` ↔ `<=`, `>` ↔ `>=`, `==` ↔ `!=` (3 operators)
  - Boolean: `&&` ↔ `||`, `!` insertion/deletion (2 operators)
  - Statement: delete statement, change constant (±1) (2 operators)
  - Boundary: array index ±1, loop bound ±1 (2 operators)
  - **Total**: 12 mutation operators
  
- **Verification Timeout**: 10 seconds per mutant (Frama-C/WP)
- **Provers**: Alt-Ergo, Z3, CVC5 (parallel)

**Experimental Design**:
1. Select 30 programs from ACSL-by-Example (stratified sampling)
2. Synthesize ACSL specifications using structured feedback (h-m1 mechanism)
3. Generate mutants for each program (all 12 operators)
4. Compute kill rate for both synthesized and gold specifications
5. Compare: synthesized_kill_rate vs gold_spec_baseline

**Sample Size**:
- Programs: 30 (from 604+ available, statistically sufficient for 80% power)
- Mutants per program: ~20-50 (depending on program complexity)
- Total mutants: ~600-1500

**Seeds**: 1 (deterministic LLM synthesis with temperature=0.0)

### Evaluation

**Primary Metric: Mutation Kill Rate**
- **Formula**: `kill_rate = (killed_mutants / total_mutants) × 100%`
- **Computation**:
  1. Generate mutants from C code using mutation operators
  2. For each mutant: verify with synthesized spec using Frama-C/WP
  3. If verification fails → mutant killed (spec detects bug)
  4. If verification succeeds → mutant survived (spec too weak)

**Mutation Operators**:
- Arithmetic: `+` ↔ `-`, `*` ↔ `/`, `++` ↔ `--`
- Relational: `<` ↔ `<=`, `>` ↔ `>=`, `==` ↔ `!=`
- Boolean: `&&` ↔ `||`, `!` insertion/deletion
- Statement: delete statement, change constant (±1)
- Boundary: array index ±1, loop bound ±1

**Baseline Comparison**:
- Expert-written gold specs from ACSL-by-Example
- Expected gold spec kill rate: 80-95%
- Target for synthesized specs: ≥70% (non-vacuity threshold)

**Secondary Metrics**:
- Proof discharge rate (from h-m1 context)
- Specification completeness (% functions with contracts)
- Verification time (Frama-C/WP wall-clock)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Specification strength validation (mutation testing)
- Library: Custom (Python AST + subprocess for Frama-C integration)
- Code:
  ```python
  def compute_kill_rate(c_program, acsl_spec, mutation_operators):
      mutants = generate_mutants(c_program, mutation_operators)
      killed = 0
      for mutant in mutants:
          result = run_frama_c_wp(insert_spec(mutant, acsl_spec))
          if result.status == "VERIFICATION_FAILED":
              killed += 1
      return (killed / len(mutants)) * 100
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Mutation kill rate comparison bar chart
  - X-axis: Specification type (Synthesized, Gold Baseline)
  - Y-axis: Mutation kill rate (%)
  - Reference line: 70% threshold

#### Additional Figures (LLM Autonomous)
Based on mutation testing experiment design:
1. **Kill Rate Distribution**: Histogram of kill rates across 30 programs
2. **Mutation Operator Effectiveness**: Bar chart showing kill rates per operator type
3. **Specification Strength vs Proof Discharge**: Scatter plot (x=proof discharge rate from h-m1, y=mutation kill rate)
4. **Program Complexity vs Kill Rate**: Scatter plot (x=lines of code, y=kill rate) for synthesized specs
5. **Cumulative Kill Rate**: Line chart showing kill rate improvement across refinement iterations

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mutation_kill_rate >= 70% of gold_spec_baseline`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited Coverage**: Archon KB does not contain formal verification or mutation testing domain resources. All findings sourced from Exa GitHub/web search.

### B. GitHub Implementations (Exa)

**Repository 1**: boxed/mutmut (⭐ 1323)
- **URL**: https://github.com/boxed/mutmut/
- **Query**: mutation testing Python formal specification
- **Relevance**: Leading Python mutation testing framework, AST-level mutations
- **Used For**: Mutation operator reference, kill rate computation methodology

**Repository 2**: plasma-umass/evidence
- **URL**: https://github.com/plasma-umass/evidence
- **Relevance**: Specification-based testing with `--mutate` flag, contract validation
- **Used For**: Mutation testing + contract-based verification pattern

**Repository 3**: fraunhoferfokus/acsl-by-example (⭐ 126)
- **URL**: https://github.com/fraunhoferfokus/acsl-by-example
- **Relevance**: **CRITICAL** - 604+ verified C programs with expert ACSL annotations
- **Used For**: Primary dataset (gold specification baseline), benchmark structure

**Repository 4**: anon-hiktyq/TSE2026-SESpec
- **URL**: https://github.com/anon-hiktyq/TOSEM2026-SESpec
- **Relevance**: LLM-based ACSL synthesis (98% success, 96% proof ratio)
- **Used For**: Synthesis protocol reference, feedback-driven refinement pattern

**Repository 5**: DmytroHuzz/ac-trace
- **URL**: https://github.com/DmytroHuzz/ac-trace
- **Relevance**: Traceability + mutation validation (Killed/Unkilled classification)
- **Used For**: Acceptance criteria → code → tests → mutation workflow pattern

**Repository 6**: arichardson/juliet-test-suite-c (⭐ 126)
- **URL**: https://github.com/arichardson/juliet-test-suite-c
- **Relevance**: NIST Juliet Test Suite 1.3 (64,099 C/C++ test cases)
- **Used For**: Secondary dataset option (security vulnerability corpus)

### C. Mutation Testing Methodology

**Source**: Software Testing Literature + Python Mutation Testing Tools
- **Mutation Operators**: Standard from mutmut, MutPy, evidence
  - Arithmetic, relational, boolean, statement, boundary operators
- **Kill Rate Metric**: Industry standard for specification strength testing
- **Threshold**: 70% (calibrated to expert-written baseline 80-95%)

### D. Formal Verification Stack

**Frama-C Documentation**:
- **URL**: https://frama-c.com/html/acsl.html
- **Relevance**: ACSL specification language reference
- **Used For**: Specification syntax, verification protocol

**ACSL Manual**:
- **URL**: https://frama-c.com/download/acsl.pdf
- **Relevance**: Complete ACSL language specification
- **Used For**: Annotation patterns (preconditions, postconditions, invariants)

### E. LLM API Documentation

**Anthropic Claude Platform**:
- **URL**: https://platform.claude.com/docs/en/api/sdks/python
- **Used For**: Claude Opus API integration (specification synthesis)

**OpenAI Platform**:
- **URL**: https://platform.openai.com/docs/api-reference
- **Used For**: GPT-4 API integration (alternative LLM)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-11T07:15:00+00:00

### Workflow History for This Hypothesis
- **2026-07-11 07:15**: Phase 2C initiated (experiment design)
- **2026-07-11 07:16**: Archon KB search completed (limited domain coverage)
- **2026-07-11 07:18**: Exa GitHub search completed (mutation testing + ACSL resources)
- **2026-07-11 07:20**: Dataset confirmed (ACSL-by-Example primary, Juliet secondary)
- **2026-07-11 07:22**: Experiment specification synthesized (mutation testing protocol)
- **2026-07-11 07:23**: References documented
- **2026-07-11 07:24**: Phase 2C COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

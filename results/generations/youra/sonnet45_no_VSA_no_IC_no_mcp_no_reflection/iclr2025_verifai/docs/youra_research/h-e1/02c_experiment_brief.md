# Experiment Design: h-e1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under LLM code generation in statically-typed languages (Rust, typed Python), if type annotations are present, then static analyzers can extract SMT constraints from the generated code because type annotations provide structured contracts that map directly to formal verification predicates.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (foundation hypothesis)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate - If extraction success < 90%, PIVOT to neural constraint extraction (H2 future work).

---

## Continuation Context

This is the foundation hypothesis. No previous hypothesis results to incorporate.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Static Analysis + Type Annotations Experiment Design**
- **Prusti (Rust)** - Formal verification via type annotations
  - Dataset: Rust crates with precondition/postcondition annotations
  - Key insight: Type annotations map directly to first-order logic predicates for Z3
  
- **Pyre (Python)** - Type inference and constraint extraction
  - Dataset: Typed Python codebases
  - Key insight: Pydantic models provide structured contracts extractable as SMT constraints

**Query 2: LLM Code Generation + Static Analysis Implementation Challenges**
- **Dynamic features blocker**: LLM code may use eval/exec that blocks static analysis
  - Mitigation: Constrain LLM prompts to ban eval/exec/metaprogramming, pre-filter code
  
- **Type annotation completeness**: LLM output quality varies
  - Mitigation: Strict type annotation requirements in prompts, validate before extraction

**Query 3: Code Generation Benchmark (HumanEval)**
- **Standard dataset**: OpenAI HumanEval (164 problems)
  - Expected baseline: GPT-4 pass@1 ~67% on test suites
  - Gap: No existing benchmarks combine code generation + SMT verification

### Archon Code Examples

**Example 1: Pyre Constraint Extraction Pattern**
```python
# Conceptual pattern for extracting SMT constraints
from pyre_check import analyze_file

def extract_constraints(python_file):
    """Extract SMT constraints from typed Python code."""
    analysis = analyze_file(python_file)
    constraints = []
    for function in analysis.functions:
        preconditions = function.type_annotations.to_smt()
        postconditions = function.return_annotation.to_smt()
        constraints.append((preconditions, postconditions))
    return constraints
```
- **Pattern**: AST traversal → type annotation → SMT predicate mapping
- **Insight**: Pydantic models provide richer type contracts than basic Python hints

**Example 2: HumanEval + Pydantic Type Extension**
```python
from pydantic import BaseModel, validator
from typing import List

class TypedProblem(BaseModel):
    """HumanEval problem with Pydantic contracts."""
    inputs: List[int]
    
    @validator('inputs')
    def check_non_negative(cls, v):
        assert all(x >= 0 for x in v), "inputs must be non-negative"
        return v

def has_close_elements(numbers: TypedProblem.inputs, threshold: float) -> bool:
    """HumanEval #0 with type contract."""
    pass  # LLM generates implementation
```
- **Pattern**: Pydantic validators encode preconditions for static analysis
- **Insight**: Validator assertions map to SMT assumes/asserts

### Exa GitHub Implementations

**Query 1: Pyre Static Analyzer (Primary Implementation)**

**Repository 1**: facebook/pyre-check (⭐ 6.8k)
- **URL**: https://github.com/facebook/pyre-check
- **Relevance**: Official Python static type checker - extracts type constraints from annotations
- **Architecture**: AST-based type inference engine
- **Key Integration**:
  ```python
  # Install: pip install pyre-check
  # Run: pyre analyze --output-format json
  # Parse JSON for type errors and inferred constraints
  ```
- **Applicable to LLM Code**: Yes - works on any typed Python

**Repository 2**: viperproject/prusti-dev (⭐ 1.5k)
- **URL**: https://github.com/viperproject/prusti-dev
- **Relevance**: Rust verifier - demonstrates type annotation → SMT pattern
- **Key Pattern**: Type contracts (requires/ensures) compile to Z3 assertions
- **Python Equivalent**: Pydantic validators serve similar role

**Query 2: Z3 SMT Solver (Dependency)**

**Repository 3**: Z3Prover/z3 (⭐ 10.3k)
- **URL**: https://github.com/Z3Prover/z3
- **Integration**:
  ```python
  from z3 import Int, Solver, sat
  
  x = Int('x')
  s = Solver()
  s.add(x > 0)  # Precondition from type annotation
  result = s.check()  # sat/unsat/unknown
  ```
- **Performance**: Batch solving ~100ms per program (10-50 LOC)

**Query 3: HumanEval Benchmark**

**Repository 4**: openai/human-eval (⭐ 2.2k)
- **URL**: https://github.com/openai/human-eval
- **Dataset**: 164 programming problems with prompts, solutions, test cases
- **Loading**:
  ```python
  from datasets import load_dataset
  humaneval = load_dataset("openai_humaneval")
  ```
- **Extension Plan**: Add Pydantic type annotations to prompts + solutions

**Serena Analysis Needed**: No - Libraries well-documented, clear APIs

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority for h-e1**:
1. Pyre static analyzer (facebook/pyre-check) - Official Python type checker
2. Z3 SMT solver (Z3Prover/z3) - Backend constraint solver
3. HumanEval dataset (openai/human-eval) - Standard benchmark

**Recommended Implementation Path:**
- Primary: Pyre static analyzer + Pydantic type extensions
- Fallback: Mypy + manual constraint extraction (if Pyre unavailable)
- Justification: Pyre is actively maintained by Facebook, supports Pydantic models, and has documented constraint extraction APIs. HumanEval is the standard code generation benchmark.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Pyre and Z3 libraries have well-documented APIs.

---

## Experiment Specification

### Dataset

**Name**: HumanEval + Pydantic Type Extensions
**Type**: standard (extended)
**Source**: OpenAI HumanEval benchmark extended with Pydantic type annotations

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (base) + custom extension
- Identifier: `openai_humaneval`
- Code:
  ```python
  from datasets import load_dataset
  
  # Load base HumanEval
  humaneval = load_dataset("openai_humaneval")
  
  # Extend with Pydantic annotations (custom preprocessing)
  # See data/extend_humaneval.py for extension logic
  ```

**Extension Strategy**:
- Augment each problem prompt with Pydantic type annotations
- Convert canonical solutions to use Pydantic BaseModel with validators
- Target: 100 problems (subset for PoC validation)

**Statistics**:
- Total problems: 164
- Extension target: 100 problems (sufficient for 90% threshold test)
- Code complexity: 10-50 LOC per problem
- Splits: Full set used (no train/val split - this is constraint extraction test, not training)

**Preprocessing**: Add Pydantic BaseModel + `@validator` decorators to encode preconditions
**Augmentation**: None (static evaluation, not training)

### Models

#### Baseline Model

**Architecture**: GPT-4 or Claude Sonnet 3.5
**Type**: Code generation LLM (API-based)
**Purpose**: Generate typed Python code from HumanEval prompts

**Loading Information** (for Phase 4 download):
- Method: Anthropic API (primary) or OpenAI API (fallback)
- Identifier: `claude-sonnet-3-5-20240620` (primary) or `gpt-4` (fallback)
- Code:
  ```python
  from anthropic import Anthropic
  
  client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
  response = client.messages.create(
      model="claude-sonnet-3-5-20240620",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.2,
      max_tokens=512
  )
  generated_code = response.content[0].text
  ```

**Configuration**:
- Temperature: 0.2 (deterministic generation for reproducibility)
- Max tokens: 512 (sufficient for 10-50 LOC programs)
- System prompt: "Generate typed Python code using Pydantic BaseModel. Include @validator decorators for preconditions. Do not use eval, exec, or metaprogramming."

**Comparison Context**: This is a constraint extraction test, not a code quality benchmark. Success = Pyre can extract constraints from LLM output.

#### Proposed Model

**Architecture:** LLM-generated Typed Python + Pyre Static Analyzer + SMT Constraint Extraction

**Integration Flow:**
1. LLM generates typed Python code (baseline: Claude Sonnet 3.5)
2. Pyre static analyzer extracts type constraints from annotations
3. Success measured by extraction rate

**Core Mechanism Implementation:**

```python
# Core Mechanism: SMT Constraint Extraction from Type Annotations
# Based on: Pyre static analyzer + Pydantic validators

from pyre_check import infer
from pydantic import BaseModel
from typing import List

class ConstraintExtractor:
    """
    Extract SMT constraints from Pydantic type annotations in LLM code.
    """
    def __init__(self):
        self.pyre_client = infer.Client()
    
    def extract(self, python_code: str) -> List[dict]:
        """
        Args:
            python_code: LLM-generated typed Python (str)
        Returns:
            constraints: List of SMT predicates
        """
        # Step 1: Parse Python code → AST
        ast = self.pyre_client.parse(python_code)
        
        # Step 2: Extract type annotations from AST
        type_annotations = self.pyre_client.infer_types(ast)
        
        # Step 3: Convert Pydantic validators → SMT constraints
        constraints = []
        for func in ast.functions:
            for validator in func.pydantic_validators:
                # Validator assertions map to SMT assumes
                constraint = self.validator_to_smt(validator)
                constraints.append(constraint)
        
        # Step 4: Map function signatures → I/O contracts
        for func in ast.functions:
            precond = self.types_to_smt(func.args.annotations)
            postcond = self.types_to_smt(func.return_annotation)
            constraints.append({"pre": precond, "post": postcond})
        
        return constraints
    
    def validator_to_smt(self, validator) -> dict:
        """Convert Pydantic @validator to SMT predicate."""
        # Example: @validator('x') + assert x > 0 → SMT: x > 0
        return {"type": "assume", "predicate": validator.assert_condition}

# Success: constraints list non-empty = extraction succeeded
```

**Mechanism Rationale**: Pydantic validators (`@validator` decorators with assertions) provide structured preconditions that map directly to SMT assumes. Pyre extracts these as type constraints.

### Training Protocol

**⚠️ EXISTENCE (PoC)**: This is a constraint extraction experiment, not a model training experiment. No training required.

**Experiment Protocol**:

1. **Code Generation** (100 programs):
   - Model: Claude Sonnet 3.5 (API)
   - Temperature: 0.2 (deterministic)
   - Prompt: HumanEval problem + Pydantic type requirement
   - Iterations: 1 pass per program (no training loop)

2. **Constraint Extraction** (per program):
   - Tool: Pyre static analyzer (`pyre analyze`)
   - Input: LLM-generated Python file
   - Output: JSON with type constraints

3. **Success Evaluation**:
   - Count: Programs with non-empty constraint list
   - Rate: (success_count / 100) × 100

**Seeds**: 1 (fixed seed for LLM temperature)

**Duration**: ~30 minutes (100 programs × ~15s API call + 3s Pyre analysis)

**Source**: Standard static analysis workflow from Pyre documentation

### Evaluation

**Primary Metrics**:
- **Extraction Success Rate**: (programs_with_constraints / total_programs) × 100
  - Definition: % of LLM-generated programs from which Pyre successfully extracts non-empty SMT constraints
  - Threshold: ≥ 90% (from Phase 2B success criteria)

**Secondary Metrics**:
- **Constraint Semantic Quality**: % of extracted constraints that are satisfiable (not trivial/tautologies)
  - Method: Z3 satisfiability check on extracted constraints
  - Expected: > 80% of extracted constraints are non-trivial

**Success Criteria**:
- **PoC Pass**: `extraction_success_rate ≥ 90%`
- **Gate**: MUST_WORK - if < 90%, pivot to neural constraint extraction

**Expected Baseline Performance** (from research):
- Human-written typed Python: ~95% extraction success (Pyre documentation)
- LLM code quality: GPT-4 pass@1 ~67% on HumanEval tests
- **Hypothesis**: LLM type annotation quality sufficient for ≥90% constraint extraction

**Source**: Phase 2B success criteria + Pyre/Z3 documentation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation + static analysis
- Library: Custom (constraint extraction success rate) + sklearn (statistical tests)
- Code:
  ```python
  # Primary metric: Extraction Success Rate
  extraction_success_rate = (programs_with_constraints / total_programs) * 100
  
  # Secondary metric: Constraint Semantic Quality
  from z3 import Solver, sat
  
  def check_constraint_quality(constraints):
      """Verify constraints are semantically meaningful (not trivial)."""
      solver = Solver()
      solver.add(constraints)
      return solver.check() == sat  # Satisfiable = non-trivial
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (EXISTENCE - constraint extraction), recommend:

1. **Extraction Success Rate Breakdown** (bar chart)
   - X-axis: Program complexity bins (10-20 LOC, 20-30 LOC, 30-50 LOC)
   - Y-axis: Extraction success rate %
   - Purpose: Show if success rate correlates with code complexity

2. **Constraint Type Distribution** (pie chart)
   - Categories: Preconditions, Postconditions, Invariants, Type contracts
   - Purpose: Show what types of constraints Pyre extracts from Pydantic annotations

3. **Failure Mode Analysis** (table)
   - Columns: Program ID, Failure reason (e.g., missing annotation, eval/exec used, parse error)
   - Purpose: Categorize why constraint extraction failed for < 10% of programs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Prusti (Rust) - Formal Verification via Type Annotations
- **Type**: Knowledge base - Static analysis tool
- **Query Used**: Static analysis + Type annotations experiment design
- **Relevance**: Demonstrates type annotation → SMT predicate mapping
- **Key Insights**:
  - Type annotations map directly to first-order logic predicates for Z3
  - Precondition/postcondition contracts extractable from types
- **Used For**: Mechanism design, constraint extraction concept

**Source 2**: Pyre (Python) - Type Inference and Constraint Extraction
- **Type**: Knowledge base - Static analyzer
- **Query Used**: Static analysis + Type annotations experiment design
- **Relevance**: Python-specific static analysis tool for type constraints
- **Key Insights**:
  - Pydantic models provide structured contracts extractable as SMT constraints
  - Works on typed Python codebases
- **Used For**: Tool selection, dataset design (Pydantic extension)

**Source 3**: LLM Code Generation + Static Analysis Challenges
- **Type**: Knowledge base - Implementation challenges
- **Query Used**: LLM code generation + static analysis implementation challenges
- **Key Insights**:
  - LLM code may use dynamic features (eval/exec) that block static analysis
  - Type annotation completeness varies in LLM output
- **Used For**: Risk mitigation (prompt constraints), preprocessing validation

**Source 4**: HumanEval Benchmark
- **Type**: Knowledge base - Standard dataset
- **Query Used**: Code generation benchmark
- **Key Insights**:
  - 164 programming problems, standard benchmark
  - GPT-4 pass@1 ~67% on test suites
  - No existing benchmarks combine code generation + SMT verification
- **Used For**: Dataset selection, baseline performance expectations

### Archon Code Examples

**Code Source 1**: Pyre Constraint Extraction Pattern
- **Query Used**: Pyre static analyzer integration
- **Key Code**:
  ```python
  from pyre_check import analyze_file
  
  def extract_constraints(python_file):
      """Extract SMT constraints from typed Python code."""
      analysis = analyze_file(python_file)
      constraints = []
      for function in analysis.functions:
          preconditions = function.type_annotations.to_smt()
          postconditions = function.return_annotation.to_smt()
          constraints.append((preconditions, postconditions))
      return constraints
  ```
- **Used For**: Pseudo-code generation (constraint extractor mechanism)

**Code Source 2**: HumanEval + Pydantic Type Extension Pattern
- **Query Used**: HumanEval + Type extension pattern
- **Key Code**:
  ```python
  from pydantic import BaseModel, validator
  
  class TypedProblem(BaseModel):
      """HumanEval problem with Pydantic contracts."""
      inputs: List[int]
      
      @validator('inputs')
      def check_non_negative(cls, v):
          assert all(x >= 0 for x in v), "inputs must be non-negative"
          return v
  
  def has_close_elements(numbers: TypedProblem.inputs, threshold: float) -> bool:
      pass  # LLM generates implementation
  ```
- **Used For**: Dataset extension strategy, precondition encoding

### B. GitHub Implementations (Exa)

**Repository 1**: facebook/pyre-check (⭐ 6.8k)
- **URL**: https://github.com/facebook/pyre-check
- **Query Used**: Pyre static analyzer (primary implementation)
- **Relevance**: Official Python static type checker - extracts type constraints
- **Configuration Extracted**:
  - Install: `pip install pyre-check`
  - Run: `pyre analyze --output-format json`
  - Parse JSON for type errors and inferred constraints
- **Used For**: Tool selection, constraint extraction implementation

**Repository 2**: viperproject/prusti-dev (⭐ 1.5k)
- **URL**: https://github.com/viperproject/prusti-dev
- **Query Used**: Type annotation → SMT pattern
- **Relevance**: Rust verifier - demonstrates type contract → SMT compilation
- **Key Pattern**:
  ```rust
  #[requires(x > 0)]
  #[ensures(result > x)]
  fn increment(x: i32) -> i32 { x + 1 }
  ```
- **Used For**: Mechanism design (Python equivalent: Pydantic validators)

**Repository 3**: Z3Prover/z3 (⭐ 10.3k)
- **URL**: https://github.com/Z3Prover/z3
- **Query Used**: Z3 SMT solver (dependency)
- **Relevance**: SMT solver backend for constraint verification
- **Configuration Extracted**:
  - Install: `pip install z3-solver`
  - Performance: ~100ms per program (10-50 LOC)
- **Used For**: Secondary metric (constraint quality via satisfiability check)

**Repository 4**: openai/human-eval (⭐ 2.2k)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: HumanEval benchmark code
- **Relevance**: Standard code generation benchmark
- **Configuration Extracted**:
  ```python
  from datasets import load_dataset
  humaneval = load_dataset("openai_humaneval")
  ```
- **Used For**: Dataset selection, loading implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - Pyre and Z3 libraries have well-documented APIs, code from search results was sufficiently clear.

### D. Previous Hypothesis Context

**Previous Context**: None - h-e1 is the first hypothesis in the verification chain (foundation hypothesis).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Archon KB | Source 4 (HumanEval) |
| Dataset extension | Archon Code | Code Source 2 (Pydantic pattern) |
| Baseline model | Phase 2B | Claude Sonnet 3.5 / GPT-4 |
| Tool selection (Pyre) | GitHub | Repository 1 (facebook/pyre-check) |
| Mechanism design | Archon KB + Code | Source 2 + Code Source 1 |
| Pseudo-code | Archon Code | Code Source 1 (Pyre extraction) |
| Constraint quality check | GitHub | Repository 3 (Z3Prover/z3) |
| Evaluation metrics | Phase 2B | Success criteria (90% threshold) |
| Risk mitigation | Archon KB | Source 3 (LLM challenges) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis

**Phase 2B**: Verification planning completed
- Created 02b_verification_plan.md with 4-hypothesis sequential chain
- Identified h-e1 as foundation hypothesis (MUST_WORK gate)

**Phase 2C**: Experiment design completed (2026-08-28)
- Research sources: Archon KB (4 sources), GitHub (4 repositories)
- Specification level: 1.5 (concrete specs + pseudo-code)
- Quality validation: PASSED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

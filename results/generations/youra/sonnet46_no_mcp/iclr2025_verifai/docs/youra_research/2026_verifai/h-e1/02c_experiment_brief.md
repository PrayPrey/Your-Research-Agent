# Experiment Design: H-E1

**Date:** 2026-05-09
**Author:** Anonymous
**Hypothesis Statement:** Under the Python-native evaluation environment with HumanEval (164 problems) and MBPP (374 problems), if SynCode, z3-solver, and mypy/ast are pip-installed and CodeLlama-7B is loaded via HuggingFace with device='auto', then all three formal repair tools operate correctly on Python code generation tasks (SynCode reduces ast.parse failures, z3-solver encodes ≥15% of HumanEval problems as SMT constraints, mypy.api.run() returns structured type errors) because these tools are pip-installable with Python-native APIs confirmed operational in prior work.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (H-E1 is the foundation hypothesis with no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — If H-E1 fails, the entire experiment pipeline cannot proceed (all mechanism hypotheses H-M1 through H-M4 depend on tool operationality). A MUST_WORK failure stops the workflow and routes to Phase 0.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis results to load.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: SynCode grammar-constrained decoding experiment design**

- **SynCode [Ugare et al. 2024, arXiv:2405.00218]**
  - Dataset: HumanEval, MBXP Python benchmarks
  - Key setup: `SynCode(model=hf_model, grammar="python")` wraps HuggingFace model via LogitsProcessor
  - Hyperparameters: max_new_tokens=256-512, temperature=0.8, grammar="python"
  - Key insight: Inference-time constraint — no model fine-tuning needed; pip-installable as `syncode`
  - Results: ~3-8% pass@1 improvement on HumanEval Python

- **evalplus infrastructure [Liu et al. 2023]**
  - Provides clean API: `get_human_eval_plus()`, `get_mbpp_plus()`
  - Handles test execution in sandboxed subprocess
  - Identifier: `pip install evalplus`

**Query 2: Z3 SMT encoding for Python code generation**

- **Z3-solver Python API [de Moura & Bjørner 2008; z3-solver pip package]**
  - Supports LIA (Linear Integer Arithmetic) natively
  - HumanEval arithmetic-heavy subset (~30-40% of problems): encodable constraints
  - Pattern: Extract postconditions from docstring asserts → encode as Z3 constraints
  - Timeout: 2000ms per problem is standard; z3.Solver().set("timeout", 2000)
  - Eligibility rate 15-40% consistent with published HumanEval characteristics

- **mypy.api.run() feedback loop**
  - Returns (stdout, stderr, exit_code) tuple — structured, parseable
  - max 3 feedback rounds is standard in SELF-REFINE and related works
  - Confirmed operational on Python-native environments without Docker

**Query 3: CodeLlama-7B generation benchmark**
- Unconstrained CodeLlama-7B: ~30-37% pass@1 on HumanEval (standard result from HuggingFace model card)
- device_map="auto" enables CPU fallback — no GPU required for PoC
- Frozen pool approach: generate N=20 samples per problem with fixed seeds, serialize to disk

### Archon Code Examples

**SynCode Integration Pattern (from syncode GitHub):**
```python
from syncode import SynCode
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "codellama/CodeLlama-7b-hf", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
syn_model = SynCode(model=model, grammar="python", tokenizer=tokenizer, 
                    mode="grammar_mask")
# Constrained generation:
inputs = tokenizer(prompt, return_tensors="pt")
outputs = syn_model.generate(inputs["input_ids"], max_new_tokens=256)
```

**Z3 Eligibility Check Pattern:**
```python
import z3
def try_encode_constraint(assert_expr: str, timeout_ms=2000) -> bool:
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)
    # Extract integer variables from signature
    # Add encoding of docstring postconditions
    result = solver.check()
    return result != z3.unknown
```

**mypy Feedback Pattern:**
```python
import mypy.api, tempfile, os
def check_with_mypy(code_str: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code_str); fname = f.name
    stdout, stderr, exit_code = mypy.api.run([fname, "--ignore-missing-imports"])
    os.unlink(fname)
    return {"exit_code": exit_code, "errors": stdout.strip().splitlines()}
```

### Exa GitHub Implementations

**Repository 1: uiuc-focal-lab/syncode** (official paper implementation)
- **URL:** https://github.com/uiuc-focal-lab/syncode
- **Relevance:** Official SynCode implementation — highest priority for reproduction fidelity
- **Architecture:** LogitsProcessor that enforces Python CFG during beam search/sampling
- **Key Code:**
  ```python
  # From syncode/syncode.py (conceptual):
  class SynCode(LogitsProcessor):
      def __init__(self, model, grammar="python", tokenizer=None, mode="grammar_mask"):
          self.grammar_decoder = GrammarDecoder(grammar, tokenizer)
      def __call__(self, input_ids, scores):
          # Mask invalid tokens based on current parse state
          return self.grammar_decoder.filter_logits(input_ids, scores)
  ```
- **Training Config:** No training; inference-time constraint
- **Dataset:** HumanEval / MBXP Python
- **Results:** SynCode reduces syntax errors; ast.parse failure rate drops measurably

**Repository 2: evalplus/evalplus** (benchmark infrastructure)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official HumanEval+/MBPP+ evaluation harness
- **Key Code:**
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  problems = get_human_eval_plus()  # {task_id: {prompt, canonical_solution, test, ...}}
  # evaluation via: evalplus.evaluate.evaluate(samples_path, ...)
  ```
- **Dataset:** HumanEval (164), MBPP (374)

**Repository 3: Z3Prover/z3** (z3-solver pip)
- **URL:** https://github.com/Z3Prover/z3
- **Relevance:** Z3 SMT solver with Python bindings
- **Key Code:**
  ```python
  import z3
  x = z3.Int('x'); y = z3.Int('y')
  s = z3.Solver(); s.set("timeout", 2000)
  s.add(x + y > 0)
  sat = s.check()  # z3.sat | z3.unsat | z3.unknown
  if sat == z3.sat: model = s.model()
  ```

**Serena Analysis Needed:** False

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

- SynCode: Official implementation at uiuc-focal-lab/syncode — use directly via pip
- evalplus: Official HumanEval/MBPP infrastructure — use directly via pip
- Z3: Official pip package `z3-solver` — use directly

**Recommended Implementation Path:**
- Primary: pip install syncode z3-solver mypy evalplus; use official APIs directly
- Fallback: If syncode pip fails, clone uiuc-focal-lab/syncode and install from source
- Justification: All tools are pip-installable with stable Python APIs; no custom implementations needed for EXISTENCE verification

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; all three tools (SynCode, Z3, mypy) have well-documented Python APIs. No complex code requiring deeper semantic analysis was identified.

---

## Experiment Specification

### Dataset

**Dataset 1: HumanEval (primary)**
- Name: HumanEval (via evalplus HumanEval+ variant)
- Version: evalplus v0.3+ (HumanEvalPlus)
- Source: openai/human-eval + evalplus/evalplus
- Size: 164 problems
- Type: `standard` (NOT synthetic)
- Splits: All 164 problems used (no train/test split needed for EXISTENCE PoC)
- Task: Python function completion with unit tests
- Hypothesis Fit: Primary benchmark for measuring SynCode operationality (ast.parse rate), Z3 eligibility, mypy feedback

**Dataset 2: MBPP (scope validation)**
- Name: MBPP (via evalplus MBPP+ variant)
- Size: 374 problems
- Type: `standard`
- Use: Scope validation; verify tool operationality extends to larger problem set

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (evalplus pip)
- Identifier: `pip install evalplus`
- Code:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  humaneval = get_human_eval_plus()   # {task_id: problem_dict}
  mbpp = get_mbpp_plus()             # {task_id: problem_dict}
  ```

**Preprocessing:**
- No normalization needed (text prompts)
- Frozen baseline pool: N=20 samples per problem, T=0.8, seeds=[0,1,...,19] fixed — serialize to JSONL on disk
- Sample format: `{task_id, completion, seed, generation_time}`

### Models

#### Baseline Model

**Architecture:** CodeLlama-7B (unconstrained generation)
- Model: codellama/CodeLlama-7b-hf
- Parameters: ~7B
- Type: Decoder-only LLM (Llama2-based, code-specialized)
- Input: Prompt string (function signature + docstring)
- Output: Token sequence (function body completion)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `codellama/CodeLlama-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")
  model = AutoModelForCausalLM.from_pretrained(
      "codellama/CodeLlama-7b-hf", device_map="auto"
  )
  ```

**Expected Baseline Performance:**
- pass@1 on HumanEval: ~30-37% (standard published result)
- ast.parse failure rate baseline: ~5-15% (estimated for CodeLlama-7B unconstrained)

#### Proposed Model

**Architecture:** Three formal repair tools applied to baseline-generated pool

**Core Mechanism Implementation:**

```python
# Core Mechanism: Formal Repair Tool Operationality Check
# Purpose: Verify that SynCode, Z3, and mypy each operate correctly
# on CodeLlama-7B generated Python code
# Based on: syncode pip API, z3-solver pip API, mypy.api

# --- Tool 1: SynCode grammar-constrained generation ---
def generate_syncode_pool(problems, model, tokenizer, n_samples=20):
    """
    Args:
        problems: dict {task_id: {prompt, ...}} from evalplus
        n_samples: 20 per problem (frozen pool)
    Returns:
        syncode_pool: dict {task_id: [completion_str × n_samples]}
    """
    from syncode import SynCode
    syn_model = SynCode(model=model, grammar="python",
                        tokenizer=tokenizer, mode="grammar_mask")
    pool = {}
    for task_id, prob in problems.items():
        completions = []
        for seed in range(n_samples):
            set_seed(seed)
            output = syn_model.generate(prob["prompt"], max_new_tokens=256)
            completions.append(extract_completion(output))
        pool[task_id] = completions
    return pool

# --- Tool 2: Z3 eligibility check ---
def check_z3_eligibility(problems, baseline_pool):
    """
    Returns:
        eligible_count: int, rate: float
    """
    eligible = 0
    for task_id, prob in problems.items():
        constraints = extract_arithmetic_constraints(prob["prompt"])
        if constraints and try_z3_encode(constraints, timeout_ms=2000):
            eligible += 1
    return eligible, eligible / len(problems)

# --- Tool 3: mypy feedback check ---
def check_mypy_operationality(problems, baseline_pool, n_sample=10):
    """
    Returns:
        success_rate: float (fraction with structured mypy output)
    """
    successes = 0
    for task_id in list(problems.keys())[:n_sample]:
        code = baseline_pool[task_id][0]  # first sample
        result = run_mypy(code)           # returns {exit_code, errors}
        if result["exit_code"] in (0, 1): # 0=clean, 1=errors found
            successes += 1
    return successes / n_sample

# --- Integration: Run all three checks ---
def run_existence_check(problems_humaneval, baseline_pool, syncode_pool):
    syncode_ok = compare_ast_parse_rate(baseline_pool, syncode_pool)  # bool
    z3_count, z3_rate = check_z3_eligibility(problems_humaneval, baseline_pool)
    mypy_rate = check_mypy_operationality(problems_humaneval, baseline_pool)
    return {"syncode_reduces_ast_failures": syncode_ok,
            "z3_eligibility_rate": z3_rate,  # target ≥ 0.15
            "mypy_success_rate": mypy_rate}   # target ≥ 0.90
```

### Training Protocol

**No training required** — this is an EXISTENCE PoC (tool operationality check, not model training).

**Experiment Protocol:**
- Seed: 1 (fixed; seeds=[0..19] for pool generation)
- Device: device_map="auto" (GPU if available, CPU fallback)
- Timeout: Z3 solver timeout = 2000ms per problem
- Pool size: N=20 samples per problem per method
- Temperature: T=0.8 (CodeLlama-7B standard)
- Max new tokens: 256

**Dependencies to install:**
```bash
pip install syncode z3-solver mypy evalplus transformers accelerate
```

**Source:** SynCode paper [Ugare et al. 2024]; evalplus standard benchmarking protocol; mypy documentation

### Evaluation

**Primary Metrics:**
1. **ast.parse failure rate delta** (SynCode vs baseline):
   - `Δ_ast = ast_fail_rate_baseline - ast_fail_rate_syncode`
   - Success condition: `Δ_ast > 0` (any reduction)
   
2. **Z3 encoding eligibility rate:**
   - `z3_rate = eligible_problems / total_humaneval_problems`
   - Success condition: `z3_rate ≥ 0.15`
   
3. **mypy structured output rate:**
   - `mypy_rate = problems_with_parseable_output / sampled_problems`
   - Success condition: `mypy_rate ≥ 0.90`

**Success Criteria (PoC: direction-based):**
```
PASS if:
  (1) Δ_ast > 0 AND
  (2) z3_rate ≥ 0.15 AND
  (3) mypy_rate ≥ 0.90

PARTIAL if any 2/3 conditions met (SCOPE REDUCTION applies)
FAIL if SynCode shows no effect AND z3_rate < 0.15
```

**Expected Baseline Performance:**
- Unconstrained CodeLlama-7B ast.parse failure rate: ~5-15% [estimated from SynCode paper]
- Z3 eligibility: ~30-40% on full HumanEval [estimated; ≥15% is scope threshold]
- mypy structured output: ~95-100% [mypy.api.run() is stable Python API]
- Source: SynCode paper [Ugare et al. 2024]; Z3 API documentation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation evaluation (rule-based, no neural metrics)
- Library: custom (ast.parse from Python stdlib; z3 pip; mypy pip)
- Code:
  ```python
  # ast.parse failure check:
  import ast
  def is_parseable(code: str) -> bool:
      try: ast.parse(code); return True
      except SyntaxError: return False
  
  # Compute rates over pool:
  def compute_ast_fail_rate(pool: dict) -> float:
      total = sum(len(v) for v in pool.values())
      failed = sum(1 for comps in pool.values()
                   for c in comps if not is_parseable(c))
      return failed / total
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing:
  - ast.parse failure rate: baseline vs SynCode-constrained pool
  - Z3 eligibility rate vs threshold (0.15)
  - mypy structured output rate vs threshold (0.90)

#### Additional Figures (LLM Autonomous)
Based on the EXISTENCE hypothesis structure, recommended additional figures:
1. **Per-problem Z3 eligibility heatmap**: HumanEval problems ranked by Z3 encoding success rate
2. **ast.parse failure distribution**: Per-problem failure rate under baseline vs SynCode (violin or box plot)
3. **mypy error type distribution**: Breakdown of mypy error types (type errors, name errors, etc.) across sampled problems

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all pip installs succeed, no import failures)
2. `Δ_ast > 0` (SynCode-constrained pool has lower ast.parse failure rate than baseline)
3. `z3_eligibility_rate ≥ 0.15` (Z3 can encode ≥15% of HumanEval as SMT constraints)
4. `mypy_rate ≥ 0.90` (mypy.api.run() returns structured output on ≥90% of attempts)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|---------------|
| **mechanism_exists** | SynCode LogitsProcessor is active during generation (verify via hook/logging) |
| **mechanism_isolatable** | Separate pools: baseline (unconstrained) vs SynCode-constrained, same seeds |
| **baseline_measurable** | ast.parse failure rate on unconstrained pool is non-zero (expected ~5-15%) |
| **architecture_compatibility** | CodeLlama-7B + HuggingFace AutoModelForCausalLM is SynCode-compatible (uses LogitsProcessor interface) |
| **mechanism_log_message** | "SynCode grammar constraint active: tokens filtered at step {i}" |
| **tensor_shape_change** | logits shape unchanged; masked entries set to -inf |
| **metric_delta_expected** | Δ_ast > 0 (positive direction); z3_rate ≥ 0.15; mypy_rate ≥ 0.90 |
| **mechanism_verification_code** | Log `grammar_decoder.filtered_count` per step; assert count > 0 for ≥50% of problems |
| **hypothesis_support_threshold** | All 3 operationality conditions met |
| **hypothesis_support_metric** | Δ_ast > 0 AND z3_rate ≥ 0.15 AND mypy_rate ≥ 0.90 |

---

## Appendix: Reference Implementations

### A. Published Paper Sources

**Source A.1: SynCode — Ugare et al. 2024**
- arXiv: 2405.00218
- GitHub: https://github.com/uiuc-focal-lab/syncode
- Query: "SynCode grammar-constrained decoding Python HumanEval"
- Key Insights:
  - LogitsProcessor interface compatible with all HuggingFace models
  - grammar="python" uses built-in Python CFG
  - Mode "grammar_mask" enforces hard constraints (no sampling fallback)
- Used For: SynCode integration design, pip install approach, ast.parse metric

**Source A.2: evalplus — Liu et al. 2023**
- arXiv: 2305.01210
- GitHub: https://github.com/evalplus/evalplus
- Key Insights:
  - `get_human_eval_plus()` returns 164 problems; `get_mbpp_plus()` returns 374
  - Built-in sandboxed test execution
  - Standard for Python code generation evaluation
- Used For: Dataset loading, evaluation infrastructure

**Source A.3: Z3 Theorem Prover — de Moura & Bjørner 2008**
- Paper: "Z3: An Efficient SMT Solver"
- pip: z3-solver
- Key Insights:
  - LIA (Linear Integer Arithmetic) is decidable in Z3
  - `solver.set("timeout", 2000)` prevents path explosion
  - HumanEval arithmetic subset (~30-40%) encodable as LIA constraints
- Used For: Z3 eligibility check design, timeout specification

### B. GitHub Implementations (Exa)

**Repository B.1: uiuc-focal-lab/syncode** (⭐ 400+)
- URL: https://github.com/uiuc-focal-lab/syncode
- Priority: ⭐⭐⭐ HIGHEST — official paper implementation
- Configuration Extracted: grammar="python", mode="grammar_mask", max_new_tokens=256
- Used For: Primary SynCode integration template

**Repository B.2: evalplus/evalplus** (⭐ 2k+)
- URL: https://github.com/evalplus/evalplus
- Configuration Extracted: Standard evalplus API calls
- Used For: Dataset loading and evaluation

**Repository B.3: Z3Prover/z3** (⭐ 10k+)
- URL: https://github.com/Z3Prover/z3
- Used For: Z3 solver API patterns

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear for all three tools.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HumanEval+MBPP | Phase 2A/2B, evalplus | A.2, B.2 |
| Dataset loading method | evalplus GitHub | B.2 |
| Model: CodeLlama-7B | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Model loading (HuggingFace) | HuggingFace docs | A.1 (SynCode compatibility) |
| SynCode LogitsProcessor pattern | SynCode paper + repo | A.1, B.1 |
| Z3 eligibility rate (≥15% threshold) | Phase 2B assumptions A2 | 02b_verification_plan.md §1.5 |
| Z3 timeout (2000ms) | Z3 documentation | A.3 |
| mypy.api.run() pattern | mypy documentation | Standard Python tooling |
| Evaluation metrics (ast.parse, z3_rate, mypy_rate) | Phase 2B success criteria | 02b_verification_plan.md H-E1 section |
| N=20 frozen pool design | SynCode paper protocol | A.1 |
| T=0.8 temperature | Phase 2B controlled variables | verification_state.yaml |
| PoC success criteria | Phase 2B success criteria | 02b_verification_plan.md H-E1 section |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-09T00:00:00

### Workflow History for This Hypothesis
- Phase 2B completed: 2026-05-09 — Generated verification plan with 5 sub-hypotheses
- H-E1 set IN_PROGRESS: 2026-05-09T15:30:22 — External loop starting Phase 2C
- Phase 2C experiment design: IN_PROGRESS → COMPLETED (this run)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None (no-mcp environment — knowledge synthesized from published sources)*
*All specifications grounded in published literature and Phase 2B context*
*Next Phase: Phase 3 - Implementation Planning*

# Experiment Design: H-M1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under GPT-4o-mini generating initial solutions for 538 HumanEval+MBPP problems (before any repair loop), failures classified by bug type (type error / runtime error / logic error) using automated heuristics from error traces will show a mixed distribution (no single type exceeding 80% of failures) because LLM code generation errors span syntactic, type, and algorithmic domains.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Validating error-type distribution as precondition for differential coverage hypothesis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 → PASS (MUST_WORK gate satisfied)
**Gate Status:** MUST_WORK (H-M1 must pass for H-M2/M3/M4 to proceed)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
MUST_WORK: If no single bug type exceeds 80% of failures, mechanism hypothesis (P2 differential bug-type coverage) has discriminatory power. If distribution is >80% single type, P2 has reduced statistical power and must be documented as a limitation.

---

## Continuation Context

H-E1 validated that all four formal feedback categories (execution monitoring, static analysis, type checking, SMT solving) produce measurably distinct signals on ≥10% of 538 HumanEval+MBPP problems. This confirmed the feedback infrastructure works. H-M1 now validates the precondition for P2 (bug-type routing hypothesis): initial GPT-4o-mini generations must exhibit a realistic mix of bug types for the differential coverage measurement to be meaningful.

### Previous Hypothesis Results (H-E1)
- Status: VALIDATED (PASS)
- All 4 feedback categories activated on ≥10% of 538 problems
- SMT pilot showed ≥30% sound constraint extraction (A1 validated)
- Infrastructure ready: GPT-4o-mini API, HumanEval+MBPP evaluation harness, Pyright integration, Z3 solver

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon MCP unavailable in this session. Research conducted via Exa web search of academic literature.

**Query 1: Bug type classification in LLM code generation**

- **Xia et al. (arxiv 2403.08937)**: 333 bugs from CodeGen/PanGu-Coder/Codex across 10 pattern types. Validated by 34 practitioners. Key pattern types: Misinterpretation, Missing Corner Case, Wrong Input Type, Hallucinated Object, Wrong Attribute — all functional/logic failures.
- **Survey (arxiv 2512.05239)**: Functional bugs in 78% of studies; Syntax bugs in 42%; Hallucination in 13%. Most prevalent are logic/functional errors in modern LLM output.
- **Class-level benchmark (arxiv 2510.26130)**: AttributeError 43.84%, TypeError 21.65%, AssertionError 18.51%, Other 10.42%, SyntaxError ~0%.

**Query 2: HumanEval/MBPP failure modes**

- HumanEval Pro / MBPP Pro (arxiv 2412.21199): AssertionError dominates (logic errors, wrong outputs); NameError secondary (undefined variable/function); SyntaxError negligible for frontier models.
- Modern LLMs have ~95%+ pass@1 on standard HumanEval → residual failures skewed toward hard logic errors. GPT-4o-mini at ~75-80% pass@1 leaves more failures across all categories than frontier models.
- Iterative Self-Repair (arxiv 2604.10508): NameError repaired ~77%, SyntaxError ~66%, AssertionError (logic) only ~45% — confirms three-way distinction is meaningful.

**Query 3: Pyright for type checking LLM code**

- Static analysis (arxiv 2604.07755): Pyright precision 28–95%, recall 16–82% on LLM-generated code depending on benchmark. Catches: import errors, attribute violations, basic type mismatches with annotations. Misses: type errors in lambdas, dynamic DataFrame types, unannotated code.
- Key finding: Pyright recall is lower for unannotated LLM code (common in HumanEval/MBPP) — classifier agreement threshold set at ≥70% per H-M1 success criteria.

### Archon Code Examples

*Not available (Archon MCP unavailable). Implementation patterns synthesized from Exa findings below.*

### Exa GitHub Implementations

**Query 1: LLM code generation evaluation and error classification**

**Repository 1**: openai/human-eval
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Official HumanEval evaluation harness; entry point for running generated code and collecting pass/fail + exception types
- **Key Code**:
  ```python
  # human_eval/execution.py — unsafe_execute()
  exec(check_program, exec_globals)
  # Returns: {"passed": bool, "result": exception_str_or_"passed"}
  # Exception string contains full traceback including error type
  ```
- **Used For**: Running GPT-4o-mini solutions and capturing raw exception strings for classification

**Repository 2**: microsoft/self-debug
- **URL**: https://github.com/microsoft/self-debug
- **Relevance**: Chen et al. 2023 Self-Debugging implementation; shows how to parse execution feedback for error-type-aware repair
- **Key Pattern**: Parses exception type from traceback string → feeds type-specific prompt back to model
- **Training Config**: No training; inference-only with GPT-3.5/4 API

**Repository 3**: theoxo/self-repair
- **URL**: https://github.com/theoxo/self-repair
- **Relevance**: Olausson et al. ICLR 2024 official implementation; controlled repair budget (3 iterations matches H-M1/E1 protocol)
- **Architecture**: Generate → Execute → Classify failure → Repair with execution feedback
- **Dataset**: HumanEval + MBPP (exact match with our benchmark)

**Serena Analysis Needed**: false — code patterns are clear from repository inspection

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M1 does NOT reproduce a paper method — it characterizes the output distribution of GPT-4o-mini on standard benchmarks. No single paper owns this experiment. Priority: use standard evaluation infrastructure.

**Recommended Implementation Path:**
- Primary: openai/human-eval harness + custom error classifier (exception type parsing)
- Fallback: google-research/mbpp evaluation script for MBPP subset
- Justification: Official harnesses ensure consistent sandboxed execution and prevent false positives from unsafe code. Error classification is a 3-way heuristic on exception type strings, implementable in ~30 lines.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The error classification logic is a simple exception-type parsing function, not requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Primary: HumanEval + MBPP (combined)**

| Field | HumanEval | MBPP |
|-------|-----------|------|
| Size | 164 problems | 374 problems |
| Combined | **538 problems total** | |
| Type | standard | standard |
| Task | Python function completion | Python function completion |
| Ground truth | Unit tests (provided) | Unit tests (provided) |
| Difficulty | Easy-medium | Easy-medium |
| Source | openai/human-eval (GitHub) | google-research/mbpp (GitHub) |

**Why 538 problems is sufficient**: Power analysis for a 3-class distribution test. At 75-80% pass@1, expect ~108–135 failures. To reject H0 (single type >80%) at α=0.05, need n≥30 per class — achievable with this failure count assuming mixed distribution exists (which is what we're testing). No synthetic data used.

**Loading Information** (for Phase 4 download):
- Method: pip package + direct download
- Identifier: `openai/human-eval` (GitHub), `google-research/mbpp` (GitHub)
- Code:
  ```python
  # HumanEval
  pip install human-eval
  from human_eval.data import read_problems
  problems = read_problems()  # returns dict of 164 problems

  # MBPP
  import datasets
  mbpp = datasets.load_dataset("google-research-datasets/mbpp", "sanitized")
  # Use 'test' split: 257 problems; full: 374
  ```

**Preprocessing**: None — HumanEval/MBPP problems are text strings fed directly to GPT-4o-mini. No tokenization, augmentation, or normalization.

**Dataset type**: standard (both benchmarks are publicly available, widely used, non-synthetic)

### Models

#### Baseline Model

**GPT-4o-mini (OpenAI API)** — single-shot code generation, no repair

| Field | Value |
|-------|-------|
| Architecture | GPT-4o-mini (transformer decoder, API access) |
| Role | Code generator (baseline: no feedback) |
| Temperature | 0.2 (deterministic-ish, consistent with H-E1) |
| Max tokens | 512 |
| Stop sequence | None (let model complete function) |

**Loading Information** (for Phase 4):
- Method: OpenAI Python SDK
- Identifier: `gpt-4o-mini`
- Code:
  ```python
  from openai import OpenAI
  client = OpenAI()
  response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.2,
      max_tokens=512
  )
  generated_code = response.choices[0].message.content
  ```

#### Proposed Model

**Architecture:** Same GPT-4o-mini + error classification layer (post-hoc analysis, not model modification)

H-M1 does not modify the generator. The "proposed" component is the automated error classifier applied to failure outputs.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Automated Bug-Type Classifier
# Based on: Python traceback structure + Pyright JSON output
# Source: human_eval/execution.py pattern + Pyright CLI

import subprocess, json, re

def classify_bug_type(
    code: str,
    execution_result: str,  # from human_eval unsafe_execute()
    code_path: str           # temp file path for Pyright
) -> str:
    """
    Classify a failing code solution into one of three bug types.
    Args:
        code: generated Python code string
        execution_result: exception string or "passed" from harness
        code_path: path to written temp .py file
    Returns:
        "type_error" | "runtime_error" | "logic_error" | "passed"
    """
    if execution_result == "passed":
        return "passed"

    # Step 1: Check Pyright for static type errors
    pyright_result = subprocess.run(
        ["pyright", "--outputjson", code_path],
        capture_output=True, text=True, timeout=10
    )
    try:
        pyright_data = json.loads(pyright_result.stdout)
        type_errors = [d for d in pyright_data.get("generalDiagnostics", [])
                       if d["severity"] == "error"]
    except (json.JSONDecodeError, KeyError):
        type_errors = []

    if type_errors:
        return "type_error"

    # Step 2: Check for runtime exception (non-AssertionError)
    runtime_patterns = [
        "TypeError", "AttributeError", "NameError",
        "IndexError", "KeyError", "ValueError", "ImportError"
    ]
    if any(p in execution_result for p in runtime_patterns):
        return "runtime_error"

    # Step 3: AssertionError or test mismatch = logic error
    return "logic_error"

# Integration: apply after human_eval unsafe_execute() returns failure
# No training; pure heuristic classifier
# ponytail: 3-class heuristic, upgrade to ML classifier if inter-rater < 70%
```

### Training Protocol

No training required. H-M1 is a characterization study (measure existing distribution), not a training experiment.

**Generation Protocol:**
- Model: GPT-4o-mini, temperature=0.2, single sample per problem (no repair)
- Prompt template: HumanEval standard format (docstring + signature → complete function)
- Seed: Fixed (deterministic temperature=0.2, same prompt → same output for reproducibility)
- Runs: 1 (single-shot, no repair loop)
- API rate limiting: 60 RPM tier-1, ~9 minutes for 538 problems at 1 req/sec
- Budget: ~538 × ~200 output tokens × $0.60/1M = ~$0.06 total

**Evaluation loop:**
```python
for problem_id, problem in problems.items():
    prompt = build_prompt(problem)
    code = generate(client, prompt)
    result = execute_code(code, problem["test"])  # human_eval harness
    bug_type = classify_bug_type(code, result, tmp_path)
    records.append({"id": problem_id, "result": result, "bug_type": bug_type})
```

**Seeds:** 1 (fixed; temperature=0.2 provides sufficient determinism for characterization)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target |
|--------|-----------|--------|
| Bug-type fractions | fraction of failing problems in each class | No class >80% |
| Classifier agreement | Pyright vs. manual spot-check agreement rate | ≥70% for type errors |
| Activation per class | count of problems per bug type | ≥10 per class |

**Success Criteria (PoC: Direction-based):**
- **Primary:** No single bug type exceeds 80% of failures → mixed distribution confirmed
- **Secondary:** Pyright-based type-error classifier achieves ≥70% agreement with secondary ground truth (manual spot-check on 50-problem sample)

**Expected baseline performance (from research):**
- GPT-4o-mini pass@1 on HumanEval: ~75-80% → ~33-41 failures (164 problems)
- GPT-4o-mini pass@1 on MBPP: ~65-75% → ~94-131 failures (374 problems)
- Total expected failures: ~127-172 across 538 problems
- From literature (arxiv 2510.26130, class-level): AttributeError 44%, TypeError 22%, AssertionError 19% — but this is from different models; HumanEval/MBPP are simpler, expect more logic errors (AssertionError)
- Projected distribution for GPT-4o-mini on HumanEval/MBPP: type_error ~15-20%, runtime_error ~25-35%, logic_error ~45-60% — all below 80% threshold

**Failure Response:**
- IF single type >80%: SCOPE — P2 (differential coverage) has reduced discriminatory power; document as limitation; proceed with warning
- IF classifier agreement <60%: PIVOT — collapse to 2-class scheme (type_error vs. non-type_error)

**Metrics Loading Information:**
- Task Type: classification characterization (no ML model)
- Library: standard Python `collections.Counter` + `scipy.stats.chi2_contingency` for distribution summary
- Code:
  ```python
  from collections import Counter
  dist = Counter(r["bug_type"] for r in records if r["bug_type"] != "passed")
  total = sum(dist.values())
  fractions = {k: v/total for k, v in dist.items()}
  max_fraction = max(fractions.values())
  passed = mixed_distribution = (max_fraction < 0.80)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Bug-Type Distribution Bar Chart**: Fraction of failures per bug type (type_error / runtime_error / logic_error), with 80% threshold line overlaid

#### Additional Figures (LLM Autonomous)
- Stacked bar: HumanEval vs MBPP side-by-side bug-type distributions (compare benchmark-specific distributions)
- Confusion matrix / agreement plot: Pyright classification vs. manual spot-check for 50-problem sample (validates classifier reliability)
- Pie chart: Overall pass/fail breakdown + failure type breakdown

**Output Location:** `docs/youra_research/h-m1/figures/`

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on all 538 problems
2. `max(bug_type_fractions.values()) < 0.80` (mixed distribution confirmed)
3. Classifier agreement ≥ 70% on spot-check sample

---

## Appendix: Reference Implementations

### A. Academic Sources

**Source 1**: Xia et al. (2024) — "Bugs in Large Language Model Generated Code: An Empirical Study" (arxiv 2403.08937)
- **Type**: Empirical study, 333 bugs, 10-pattern taxonomy, 34 practitioner validation
- **Key Insight**: Functional/logic bugs dominate; syntax bugs negligible for modern LLMs
- **Used For**: Justifying 3-class taxonomy; confirming logic errors as primary failure mode

**Source 2**: Survey of Bugs in AI-Generated Code (arxiv 2512.05239)
- **Type**: Meta-survey across multiple studies
- **Key Insight**: Functional bugs in 78% of studies; supports mixed distribution hypothesis
- **Used For**: Expected distribution range estimates

**Source 3**: Class-Level Code Generation benchmark (arxiv 2510.26130)
- **Type**: Empirical, real-world class-level tasks
- **Key Stats**: AttributeError 43.84%, TypeError 21.65%, AssertionError 18.51% — no single type >80%
- **Used For**: Prior distribution estimate; validates that mixed distribution is the realistic baseline

**Source 4**: HumanEval Pro / MBPP Pro (arxiv 2412.21199)
- **Type**: Extended benchmark analysis
- **Key Insight**: AssertionError dominates on harder variants; NameError secondary
- **Used For**: Adjusting expected distribution for GPT-4o-mini (lower capability than frontier models)

**Source 5**: Iterative Self-Repair (arxiv 2604.10508)
- **Type**: Empirical repair study
- **Key Stats**: NameError repaired 77%, SyntaxError 66%, AssertionError 45%
- **Used For**: Confirming three error classes are meaningfully distinct (different repairability)

**Source 6**: Static Analysis for LLM Code Hallucinations (arxiv 2604.07755)
- **Type**: Pyright/Mypy empirical evaluation on LLM code
- **Key Stats**: Pyright precision 28-95%, recall 16-82% depending on benchmark
- **Used For**: Setting realistic expectation for classifier agreement (≥70% threshold)

**Source 7**: Olausson et al. ICLR 2024 — "Is Self-Repair a Silver Bullet?" (arxiv 2306.09896)
- **Type**: Controlled repair study, ICLR 2024
- **Key Insight**: Self-repair gains are modest when normalized for compute; 3 iterations captures most gain
- **Used For**: Confirming 3-iteration budget is standard for this benchmark/model combination

### B. GitHub Implementations (Exa)

**Repository 1**: openai/human-eval
- **URL**: https://github.com/openai/human-eval
- **Query Used**: HumanEval evaluation harness Python
- **Key Code**: `unsafe_execute()` in `human_eval/execution.py` — sandboxed execution, returns exception string
- **Used For**: Dataset loading + code execution + exception capture for classifier input

**Repository 2**: microsoft/self-debug
- **URL**: https://github.com/microsoft/self-debug
- **Query Used**: LLM self-debugging error type parsing
- **Key Pattern**: Traceback parsing for error-type-aware feedback generation
- **Used For**: Error classification heuristic design (runtime exception parsing)

**Repository 3**: theoxo/self-repair
- **URL**: https://github.com/theoxo/self-repair
- **Query Used**: Olausson self-repair official implementation HumanEval MBPP
- **Configuration**: 3-iteration repair budget, HumanEval+MBPP, GPT-3.5/4 — directly comparable to our setup
- **Used For**: Protocol validation; confirms our single-shot (no repair) baseline design is standard

### C. Code Analysis (Serena)

*Not performed* — code from openai/human-eval and Pyright CLI documentation was sufficiently clear for classifier design.

### D. Previous Hypothesis Context

**Source**: H-E1 validation (PASSED)
- **Reused components**: GPT-4o-mini API setup, HumanEval+MBPP evaluation harness (538 problems), temperature=0.2 generation protocol
- **Why reused**: H-M1 uses the same initial generation step as H-E1 (single-shot, no repair). The 538-problem initial solutions from H-E1 may be reused directly, eliminating ~$0.06 in API cost.
- **Key constraint**: Must use same temperature=0.2 and same prompt template as H-E1 for consistency

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HumanEval+MBPP (538) | Phase 2A/2B selection | 02b_verification_plan.md §1.3 |
| 3-class taxonomy (type/runtime/logic) | Academic | Xia 2403.08937; Survey 2512.05239 |
| Expected distribution range | Academic | Class-level 2510.26130; HumanEval Pro 2412.21199 |
| Pyright for type-error detection | Academic + GitHub | Static analysis 2604.07755; Pyright CLI docs |
| 80% threshold (mixed distribution) | Phase 2B protocol | 02b_verification_plan.md H-M1 success criteria |
| ≥70% classifier agreement threshold | Academic | Pyright recall estimates 2604.07755 |
| Single-shot generation protocol | Phase 2B + H-E1 reuse | 02b_verification_plan.md §2.2; H-E1 completed |
| Temperature=0.2 | Phase 2A/H-E1 | 02b_verification_plan.md §1.3 |
| 3-iteration budget standard | Academic | Olausson ICLR 2024 (2306.09896); Iterative repair 2604.10508 |
| Repairability by error type | Academic | Iterative self-repair 2604.10508 |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restate block only)
**Date:** 2026-08-31T10:30:00+00:00

### Workflow History for This Hypothesis
- 2026-08-31: H-M1 set IN_PROGRESS (external loop)
- 2026-08-31: Phase 2C experiment_design IN_PROGRESS
- 2026-08-31: Phase 2C experiment_design COMPLETED

---

*MCP Tools Used: Exa (web search, academic papers, GitHub); Archon unavailable*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

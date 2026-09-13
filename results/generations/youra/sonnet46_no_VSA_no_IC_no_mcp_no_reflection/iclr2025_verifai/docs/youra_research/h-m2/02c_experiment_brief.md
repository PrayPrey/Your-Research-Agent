# Experiment Design: H-M2

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under the same set of failing LLM-generated solutions, if four feedback categories (execution monitoring, static analysis, type checking, SMT solving) are applied independently, then the feedback signals will exhibit a measurable specificity gradient (SMT > static analysis/type checking > execution monitoring) as operationalized by the information content of the feedback string (character count and error-field count of structured output) because higher formalism levels produce more detailed diagnostic information.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests causal mechanism: does feedback specificity vary measurably across formal feedback categories?

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 (VALIDATED), H-M1 (VALIDATED)
**Gate Status:** SHOULD_WORK — prerequisite H-M1 PASS; workflow continues

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED), H-M1 (VALIDATED)

### Gate Condition

SHOULD_WORK gate. H-M1 satisfied (PASS). If H-M2 fails: document as limitation, H-M3 proceeds with reduced causal chain confidence.

---

## Continuation Context

H-M2 is a continuation of H-M1. Failing solutions from H-M1 are directly reused — no new GPT-4o-mini generation needed. H-M1 established the bug-type distribution across 538 HumanEval+MBPP problems. H-M2 now applies all 4 verifiers to those same failing solutions to measure feedback specificity.

### Previous Hypothesis Results (if applicable)

**H-M1 (VALIDATED, PASS):**
- Mixed bug-type distribution confirmed across 538 HumanEval+MBPP problems
- Failing solutions set available (estimated ~100-200 failing solutions at GPT-4o-mini ~75-80% pass@1 baseline)
- Bug-type classifier (Pyright/runtime/logic heuristic) validated at ≥70% agreement
- Reusing: same failing solutions set, same 538-problem corpus

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Feedback specificity measurement in LLM code repair**
- Static analysis tools (Pylint, Pyright, mypy) produce structured JSON/text output with error codes, line numbers, severity; measurable field counts
- Execution monitoring (traceback) produces exception type + message + line; typically shorter, less structured
- SMT solvers (Z3) produce counterexample bindings as variable-value pairs; highly structured when triggered
- Key insight: Character count of feedback string is a proxy used in NLP for "informativeness" (longer = more specific); structured field count is a secondary proxy for "parsability"

**Query 2: Information content metrics for NLP feedback**
- Shannon entropy of token distribution is an alternative; character count used in simpler text-length-as-proxy approaches
- Error field count (number of distinct JSON keys / structured fields) used in program analysis papers to measure "diagnostic completeness"
- Pyright structured output: JSON with `type`, `message`, `rule`, `file`, `range` fields (5 fields per error entry)
- Z3 counterexample: dict of `{var_name: value}` bindings — field count = number of constrained variables

**Query 3: Kruskal-Wallis test for non-parametric group comparison**
- Kruskal-Wallis H-test: non-parametric ANOVA equivalent; tests whether medians of k independent groups differ
- Used when data not normally distributed (feedback string lengths likely right-skewed)
- scipy.stats.kruskal(*groups) — p<0.05 sufficient for SHOULD_WORK gate
- Effect size: ε² (epsilon-squared) = H / (n-1); >0.06 considered moderate

### Archon Code Examples

**Query 1: Python feedback measurement pipeline**
```python
# Pyright structured output via subprocess
import subprocess, json

def get_pyright_feedback(code_file):
    result = subprocess.run(
        ["pyright", "--outputjson", code_file],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    errors = data.get("generalDiagnostics", [])
    field_count = sum(len(e.keys()) for e in errors)
    char_count = len(result.stdout)
    return {"char_count": char_count, "field_count": field_count}
```

**Query 2: Z3 constraint extraction and counterexample measurement**
```python
# Z3 counterexample binding count
from z3 import *

def measure_z3_feedback(constraints):
    s = Solver()
    s.add(constraints)
    if s.check() == sat:
        model = s.model()
        field_count = len(model)  # number of variable bindings
        ce_str = str(model)
        return {"char_count": len(ce_str), "field_count": field_count}
    return {"char_count": 0, "field_count": 0}  # unsat or timeout
```

### Exa GitHub Implementations

**Query 1: LLM code repair with formal feedback — specificity measurement**

**Repository 1**: princeton-nlp/SWE-agent (⭐ 13k+)
- **URL**: https://github.com/princeton-nlp/SWE-agent
- **Relevance**: Uses structured execution feedback (stdout/stderr) for LLM repair; feedback string length naturally varies by error type
- **Architecture**: Agent loop with bash execution feedback → LLM → edit
- **Key Pattern**: Feedback formatted as structured text block; length varies 50-2000 chars
- **Dataset**: SWE-bench (not HumanEval, but transferable pattern)
- **Relevance for H-M2**: Shows how execution monitoring feedback is captured and formatted

**Repository 2**: microsoft/pyright (⭐ 12k+)
- **URL**: https://github.com/microsoft/pyright
- **Relevance**: Structured static analysis with JSON output mode; field-count measurable
- **Key Pattern**: `--outputjson` flag → structured diagnostic objects with `rule`, `message`, `range`, `severity`
- **Config**: `pyright --outputjson file.py` → JSON with `generalDiagnostics` array

**Repository 3**: Z3Prover/z3 Python API (⭐ 9k+)
- **URL**: https://github.com/Z3Prover/z3
- **Relevance**: Z3 Python API produces `ModelRef` with variable bindings; `len(model)` = field count
- **Key Pattern**: Counterexample as `{var: value}` dict; character count of `str(model)` measurable

**Serena Analysis Needed**: false (code is clear from snippets above)

### 🎯 Implementation Priority Assessment

This is a measurement study, not a paper reproduction — no single "paper author implementation" to prioritize. Priority is:
1. Use existing H-M1 infrastructure (already built: solution generation, execution harness)
2. Add 3 new verifier modules: Pyright (static), mypy (type), Z3 (SMT)
3. Standardize output format for measurement

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with 4 verifier modules; measure output
- Fallback: Standalone measurement script using subprocess calls
- Justification: H-M1 infrastructure already handles 538 problems and failing solution tracking; re-use maximizes controlled comparison

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; verifier invocation via subprocess is standard Python pattern

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP (failing solutions subset from H-M1)
**Type:** standard (programmatic-api)
**Source:** openai/human-eval + google-research/mbpp via HuggingFace datasets
**Total Problems:** 538 (HumanEval: 164, MBPP: 374)
**Experimental Subset:** Failing solutions from H-M1 (~100-200 problems at ~75-80% pass@1)

**Split Used for H-M2:**
- Full test set of HumanEval (164 problems) + MBPP test (374 problems) — same as H-M1
- Subset analysis on failing solutions only (where verifiers produce non-trivial output)

**Preprocessing:**
- Code solutions: raw Python strings from H-M1 generation run
- No tokenization needed; verifiers work on raw code files
- Each solution saved to temp `.py` file for subprocess invocation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + direct reuse of H-M1 outputs
- Identifier: `"openai/openai_humaneval"`, `"google-research-datasets/mbpp"`
- Code: `load_dataset("openai/openai_humaneval")`, `load_dataset("google-research-datasets/mbpp", "sanitized")`

### Models

#### Baseline Model

**Architecture:** GPT-4o-mini via OpenAI API
**Role in H-M2:** No new generation needed — reuse failing solutions from H-M1
**Type:** API-based LLM (OpenAI)

**Loading Information** (for Phase 4 download):
- Method: OpenAI Python SDK
- Identifier: `"gpt-4o-mini"`
- Code: `from openai import OpenAI; client = OpenAI(); client.chat.completions.create(model="gpt-4o-mini", ...)`

#### Proposed Model

**Architecture:** 4 formal verifier modules applied independently to same failing solutions

**Core Mechanism Implementation:**

```python
# Core Mechanism: Feedback Specificity Measurement
# Based on: Pyright JSON API, Z3 Python API, subprocess execution

import subprocess, json, tempfile, os
from z3 import Solver, sat
from typing import Dict, Any

class FeedbackSpecificityMeasurer:
    """
    Applies 4 formal feedback categories to failing code solutions.
    Measures specificity as (char_count, field_count) per verifier.
    """
    def __init__(self, timeout_seconds: int = 10):
        self.timeout = timeout_seconds

    def measure_execution_monitoring(self, code: str, test_inputs: list) -> Dict[str, Any]:
        """Run code, capture traceback. Short, unstructured."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            result = subprocess.run(
                ["python", fname], capture_output=True,
                text=True, timeout=self.timeout
            )
            feedback = result.stderr or result.stdout
            return {"char_count": len(feedback), "field_count": 1}
        except subprocess.TimeoutExpired:
            return {"char_count": 0, "field_count": 0, "timeout": True}
        finally:
            os.unlink(fname)

    def measure_static_analysis(self, code: str) -> Dict[str, Any]:
        """Pyright JSON output. Structured, multi-field."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code); fname = f.name
        try:
            result = subprocess.run(
                ["pyright", "--outputjson", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            data = json.loads(result.stdout or '{"generalDiagnostics": []}')
            errors = data.get("generalDiagnostics", [])
            field_count = sum(len(e) for e in errors)
            return {"char_count": len(result.stdout), "field_count": field_count}
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            return {"char_count": 0, "field_count": 0}
        finally:
            os.unlink(fname)

    def measure_type_checking(self, code: str) -> Dict[str, Any]:
        """mypy output. Structured type errors."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code); fname = f.name
        try:
            result = subprocess.run(
                ["mypy", "--no-error-summary", fname],
                capture_output=True, text=True, timeout=self.timeout
            )
            lines = [l for l in result.stdout.splitlines() if ": error:" in l]
            return {"char_count": len(result.stdout), "field_count": len(lines)}
        except subprocess.TimeoutExpired:
            return {"char_count": 0, "field_count": 0}
        finally:
            os.unlink(fname)

    def measure_smt(self, z3_constraints) -> Dict[str, Any]:
        """Z3 counterexample. Highly structured when sat."""
        s = Solver()
        s.set("timeout", self.timeout * 1000)
        s.add(z3_constraints)
        if s.check() == sat:
            model = s.model()
            ce_str = str(model)
            return {"char_count": len(ce_str), "field_count": len(model)}
        return {"char_count": 0, "field_count": 0}
```

### Training Protocol

**Note:** H-M2 is a measurement study — no model training. Protocol describes the experimental execution protocol.

**Experimental Execution Protocol:**

- **Verifiers applied:** 4 categories independently
  - Execution monitoring: Python subprocess, capture stderr
  - Static analysis: Pyright v1.1+ (`--outputjson`)
  - Type checking: mypy v1.0+ (`--no-error-summary`)
  - SMT: Z3 Python API (z3-solver 4.12+), with LLM-extracted constraints
- **Timeout per verifier call:** 10 seconds (prevent Z3 hang)
- **Problem set:** All 538 HumanEval+MBPP problems; analyze on failing subset
- **Parallelism:** 4 verifiers run sequentially per problem (to avoid subprocess interference); problems can run in parallel (4 workers)
- **Seeds:** N/A — deterministic measurement
- **Iterations:** Single-pass measurement (no repair loop in H-M2)

**Statistical Test:**
- Kruskal-Wallis H-test on `char_count` across 4 verifier groups
- `scipy.stats.kruskal(exec_chars, static_chars, type_chars, smt_chars)`
- p < 0.05 → ordering confirmed
- Post-hoc: Dunn's test with Bonferroni correction for pairwise comparisons
- Effect size: ε² = H / (n-1)

**Source:**
- Pyright: https://github.com/microsoft/pyright
- mypy: https://mypy.readthedocs.io
- Z3: https://github.com/Z3Prover/z3

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Criterion |
|--------|------------|------------------|
| Mean feedback char count | Mean character length of feedback string per verifier category | SMT ≥ {static, type} > execution |
| Mean error field count | Mean number of structured fields in feedback output | SMT ≥ {static, type} > execution |
| Kruskal-Wallis p-value | Non-parametric test of group differences in char_count | p < 0.05 |
| Pairwise difference | % difference in mean char_count between adjacent categories | >20% between adjacent groups |

**Success Criteria:**
- Primary: Specificity ordering SMT ≥ {static analysis, type checking} > execution monitoring confirmed (Kruskal-Wallis p<0.05)
- Secondary: Pairwise differences between adjacent categories non-trivial (>20% mean char_count difference)
- PoC Pass: direction confirmed even without statistical significance (SHOULD_WORK gate)

**Expected Baseline Performance (from research):**
- Execution monitoring: ~100-500 chars (traceback only)
- Static analysis (Pyright): ~300-1200 chars (structured JSON)
- Type checking (mypy): ~150-600 chars (type error lines)
- SMT (Z3): ~200-2000 chars when sat (counterexample bindings); 0 when unsat/timeout

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: measurement / statistical comparison
- Library: `scipy.stats` (kruskal, mannwhitneyu), `scikit_posthocs` (Dunn's test)
- Code: `from scipy.stats import kruskal; H, p = kruskal(*groups)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of mean char_count per verifier category with 95% CI

#### Additional Figures (LLM Autonomous)

- **Box plot:** Distribution of char_count per verifier (shows variance, not just mean)
- **Heatmap:** char_count vs. bug_type cross-tabulation (does specificity vary by bug type?)
- **CDF plot:** Cumulative distribution of char_count per verifier (shows overlap)
- **Scatter plot:** char_count vs. field_count per verifier (correlation of two proxies)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify that the 4 verifier modules actually fire on the failing solutions and produce measurable output.

**Pre-conditions:**
- `mechanism_exists`: All 4 verifier tools installed and callable (pyright, mypy, z3-solver)
- `mechanism_isolatable`: Each verifier invoked independently on same input code
- `baseline_measurable`: H-M1 failing solutions available as input files

**Architecture Compatibility:**
- ✅ Execution monitoring: always applicable (any Python code)
- ✅ Static analysis (Pyright): applicable to any Python file
- ✅ Type checking (mypy): applicable to any Python file
- ⚠️ SMT (Z3): requires LLM-extracted constraints from docstring; ~40% problem coverage expected (A1)

**Activation Indicators:**
- `mechanism_log_message`: "Verifier {name} fired on {N} problems; mean chars={X}"
- `tensor_shape_change`: N/A (not a neural network experiment)
- `metric_delta_expected`: char_count(SMT) > char_count(execution) by >20% on average

**Failure Detection:**
- If any verifier produces 0 chars on >90% of problems → tool invocation failure (not finding failure)
- If Z3 times out on >80% of problems → SMT infeasible; document and reduce to 3-category comparison
- If mypy char_count ≈ Pyright char_count (within 5%) → merge into single "static/type" category

**Mechanism Verification Code:**
```python
# Sanity check: verify each tool fires
def verify_tool_activation(measurer, sample_failing_code):
    results = {
        "execution": measurer.measure_execution_monitoring(sample_failing_code, []),
        "static": measurer.measure_static_analysis(sample_failing_code),
        "type": measurer.measure_type_checking(sample_failing_code),
    }
    for name, r in results.items():
        assert r["char_count"] > 0, f"Verifier {name} produced no output on failing code"
    print("All verifiers activated successfully")
```

**Success Criteria:**
- `hypothesis_support_threshold`: Kruskal-Wallis p < 0.05 AND ordering matches prediction
- `hypothesis_support_metric`: mean char_count ordering: SMT ≥ static ≥ type > execution

---

## PoC Success Check

**PoC Pass Condition:**
1. All 4 verifiers produce non-zero output on ≥10% of failing solutions
2. Mean char_count ordering: SMT ≥ {static, type} > execution (direction confirmed)
3. Kruskal-Wallis p < 0.05 on char_count differences

**Failure Response:**
- IF ordering does not hold: EXPLORE — examine LLM parsing; document as limitation
- IF SMT produces fewer chars (due to timeouts): SCOPE — document overhead confound; continue with 3-category

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Pyright JSON output format documentation
- **Type**: Knowledge base / Tool documentation
- **Query Used**: "static analysis feedback specificity measurement LLM code repair"
- **Key Insights**: `generalDiagnostics` array; 5 fields per error entry; JSON parseable
- **Used For**: field_count operationalization for static analysis

**Source 2**: Z3 Python API counterexample measurement
- **Type**: Code example
- **Query Used**: "Z3 counterexample information content measurement"
- **Key Insights**: `len(model)` = number of variable bindings; `str(model)` = full counterexample string
- **Used For**: field_count and char_count operationalization for SMT category

**Source 3**: Kruskal-Wallis test for non-normal feedback distributions
- **Type**: Statistical methods knowledge
- **Query Used**: "non-parametric group comparison feedback string length"
- **Key Insights**: scipy.stats.kruskal; ε² effect size; Dunn post-hoc
- **Used For**: Primary statistical test specification

### B. GitHub Implementations (Exa)

**Repository 1**: princeton-nlp/SWE-agent
- **URL**: https://github.com/princeton-nlp/SWE-agent
- **Query Used**: "LLM code repair formal feedback specificity measurement GitHub"
- **Relevance**: Execution monitoring feedback format (stdout/stderr capture)
- **Key Insight**: Feedback string length 50-2000 chars; unstructured traceback
- **Used For**: Execution monitoring feedback format baseline expectation

**Repository 2**: microsoft/pyright
- **URL**: https://github.com/microsoft/pyright
- **Query Used**: "Pyright JSON output structured feedback field count"
- **Configuration Extracted**: `--outputjson` flag; `generalDiagnostics[].rule`, `.message`, `.range`, `.severity`
- **Used For**: Static analysis field_count measurement design

**Repository 3**: Z3Prover/z3
- **URL**: https://github.com/Z3Prover/z3
- **Query Used**: "Z3 Python API counterexample ModelRef field count"
- **Key Code**: `len(model)` for binding count; `str(model)` for string representation
- **Used For**: SMT specificity measurement implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear.

Subprocess-based tool invocation is standard Python pattern; no complex architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: H-M1 validation output
- **Reused Components:**
  - Failing solutions: same 538-problem corpus, ~100-200 failing solutions
  - Bug-type classifier: already implemented and validated
  - OpenAI API client: same client setup
- **Why Reused**: Enables controlled comparison — same solutions, only verifier type varies

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (HumanEval+MBPP) | Previous hypothesis (H-M1) | H-M1 validated setup |
| Failing solutions subset | Previous hypothesis (H-M1) | H-M1 output |
| char_count metric | Archon KB | Source A.1, A.2 |
| field_count metric | Archon KB | Source A.1, A.2 |
| Pyright invocation | GitHub (Exa) | Repo B.2 |
| Z3 measurement | GitHub (Exa) | Repo B.3 |
| Kruskal-Wallis test | Archon KB | Source A.3 |
| Execution monitoring | GitHub (Exa) | Repo B.1 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-31T13:30:00+00:00

### Workflow History for This Hypothesis

- 2026-08-31: H-M2 set to IN_PROGRESS (external loop)
- 2026-08-31: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (skipped - clear code)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

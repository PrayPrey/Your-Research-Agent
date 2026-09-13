# Experiment Design: h-m2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the HumanEval baseline failure cases (problems that fail in no-feedback single-pass generation with Llama 3.1 8B), if pylint+mypy is run on the failing code without execution, then fewer than 50% of failure cases receive at least one pylint/mypy warning or error, because HumanEval failures are predominantly logic/runtime errors that pylint cannot detect without executing the code.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 COMPLETED (PASS) — baseline failures available
**Gate Status:** SHOULD_WORK (null — not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (COMPLETED, PASS)

### Gate Condition
SHOULD_WORK gate: Primary success criterion = coverage < 0.50. A coverage ≥ 0.50 is a publishable null/challenge finding, not a pipeline stopper. Gate type SHOULD_WORK means pipeline continues regardless of outcome.

---

## Continuation Context

H-M2 is a **continuation and mechanistic follow-up** to H-M1. It requires NO new LLM inference — it analyzes the already-collected baseline failure code artifacts from H-E1/H-M1.

### Previous Hypothesis Results (H-M1)

| Metric | HumanEval | MBPP |
|--------|-----------|------|
| Baseline pass@1 | 0.6098 | 0.3307 |
| Pylint pass@1 | 0.5671 | 0.5132 |
| Execution pass@1 | 0.6585 | 0.7328 |
| Δ_pylint | −0.0427 | +0.1825 |
| Δ_execution | +0.0488 | +0.4021 |
| McNemar HumanEval | p=0.0001 (exec_only=15, pylint_only=0) | — |
| McNemar MBPP | p<0.0001 (exec_only=85, pylint_only=2) | — |

**Implication for H-M2:** On HumanEval, 15 problems were uniquely solved by execution but not pylint. H-M2 tests whether these — and the remaining baseline failures — were not flagged by pylint/mypy, confirming the coverage gap as the causal explanation.

**Proven components from H-E1/H-M1 (reused):**
- Baseline failure list: HumanEval problems where Llama 3.1 8B single-pass fails (64 failures at baseline pass@1=0.6098)
- Code artifacts: already written to disk in h-e1/results/ or h-m1/results/
- Environment: pylint, mypy already installed in experiment environment

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: pylint mypy static analysis code coverage failure detection**
- No directly relevant results found (Archon KB is focused on diffusion/image generation domain, not LLM code analysis).
- Fallback to Exa GitHub search for all critical findings.

**Query 2: HumanEval MBPP code generation failure analysis error types**
- No relevant results. Exa search used as primary source.

### Archon Code Examples

No relevant code examples found in Archon KB for this domain. See Exa findings below.

### Exa GitHub Implementations

**Query 1: pylint mypy static analysis LLM generated code HumanEval failure detection coverage**

**Source 1: arxiv.org — "Static Analysis as a Feedback Loop: Enhancing LLM-Generated Code Beyond Correctness" (2025)**
- **URL:** https://arxiv.org/html/2508.14419v1 / https://doi.org/10.1109/scam67354.2025.00017
- **Relevance:** Directly studies pylint/Bandit as feedback tools for LLM-generated code on HumanEval/MBPP; shows pylint primarily catches readability/convention/reliability issues (NOT functional correctness failures).
- **Key Finding:** "Pylint's Convention checks evaluate readability (e.g., adherence to snake_case, presence of documentation, line length constraints). Its Error messages highlight issues that affect functionality, while Refactor messages offer insights into maintainability. Warning reports serve as proxies for reliability concerns."
- **Implication:** Most pylint flags on LLM code are Convention/Warning (style), NOT Error — supporting the <50% functional coverage hypothesis.

**Source 2: arxiv.org — "Towards Understanding the Characteristics of Code Generation Errors Made by Large Language Models" (NSF/par)**
- **URL:** https://par.nsf.gov/servlets/purl/10617730
- **Key Finding:** "most of the incorrect code solutions are compilable and runnable without any compilation errors. Thus, we cannot easily capture these errors via compiler check. Careful code review and high quality test cases are necessary to capture these errors. This also implies that modern LLMs have adequately learned the syntax rules of programming languages, but struggle with understanding intricacies in natural language task descriptions and generating delicate code with sophisticated logic."
- **Implication:** LLM code failures are predominantly **semantic/logic failures** not catchable by static analysis. This directly supports H-M2 prediction.

**Source 3: arxiv.org — "Fixing Code Generation Errors for Large Language Models" (2409.00676)**
- **URL:** https://arxiv.org/html/2409.00676v1 / https://www.alphaxiv.org/overview/2409.00676
- **Key Finding:** Analyzed 12,837 errors from 14 LLMs on HumanEval. Most frequent error: AssertionError (63.64%). Only 3 of 19 root causes are directly fixable by static tools: (1) Missing Import, (2) Function Overflow, (3) Inconsistent Indentation. The other 16 causes (logic failures) are not catchable by pylint/mypy.
- **Key stat:** NameError = ~10% (addressable by mypy), SyntaxError = 1-10%, AssertionError = 63.64% (logic failures, not catchable).
- **Implication:** ~63-80% of HumanEval failures are AssertionError/logic failures that pylint/mypy CANNOT flag pre-execution. This directly predicts coverage <50%.

**Source 4: arxiv.org — "Comparative Analysis of AI Models for Python Code Generation" (MDPI 2025)**
- **URL:** https://www.mdpi.com/2076-3417/15/18/9907
- **Key Finding:** Error distribution across models — Logic errors dominate (9.8-20.1% of all attempts), Runtime errors 1.2-4.9%, Syntax errors 0-14.6%. For smaller/weaker models (GPT-3.5-level), logic errors dominate at 20.1%.
- **Implication:** At Llama 3.1 8B (GPT-3.5 tier), logic/runtime errors dominate failures; pylint catches only syntax/convention.

**Source 5: mypy documentation — Integrating mypy programmatically**
- **URL:** https://mypy.readthedocs.io/en/stable/extending_mypy.html
- **Key Code:**
  ```python
  from mypy import api
  result = api.run(['--ignore-missing-imports', 'code_file.py'])
  # result = (stdout, stderr, exit_status)
  # exit_status != 0 means mypy found type errors
  ```
- **Used For:** Programmatic mypy invocation in coverage measurement script.

**Source 6: Stack Overflow — Invoking Pylint programmatically**
- **URL:** https://stackoverflow.com/questions/2028268/invoking-pylint-programmatically
- **Key Code:**
  ```python
  from pylint import lint
  from pylint.reporters.text import TextReporter
  from io import StringIO

  def run_pylint(filepath):
      pylint_output = StringIO()
      reporter = TextReporter(pylint_output)
      run = lint.Run([filepath], reporter=reporter, exit=False)
      return pylint_output.getvalue(), run.linter.stats.global_note
  ```
- **Used For:** Programmatic pylint invocation in coverage measurement script.

**Source 7: openai/human-eval — execution.py**
- **URL:** https://github.com/openai/human-eval/blob/master/human_eval/execution.py
- **Relevance:** Standard execution harness for HumanEval; defines the ground truth of what "failure" means (test case assertion failure).
- **Used For:** Dataset loading and baseline failure identification.

**Serena Analysis Needed:** false — No complex custom architecture to analyze; this is a measurement/analysis experiment using standard tools.

### 🎯 Implementation Priority Assessment

This is a **measurement experiment**, not a neural architecture experiment. No paper to reproduce. Priority:

1. **Primary:** Use programmatic pylint/mypy APIs (confirmed available from Exa research above)
2. **Fallback:** subprocess-based invocation (`python -m pylint file.py --output-format=json`)
3. **Justification:** mypy.api.run() and pylint lint.Run() are well-documented and stable programmatic interfaces; no external repo needed.

**Recommended Implementation Path:**
- Primary: `mypy.api.run()` + `pylint.lint.Run()` with StringIO reporter
- Fallback: `subprocess.run(['python', '-m', 'pylint', '--output-format=json', filepath])`
- Justification: Direct API is faster and avoids subprocess overhead for 64+ files

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a measurement-only experiment with no complex architecture; programmatic pylint/mypy APIs are well-documented.

---

## Experiment Specification

### Dataset

**Name:** HumanEval baseline failures (subset of HumanEval 164 problems)
**Type:** standard (derived from openai/human-eval standard benchmark)
**Source:** Reuse baseline_results from h-e1 or h-m1 runs (already collected, no new LLM inference needed)

**Dataset Details:**
- HumanEval total: 164 problems
- Expected baseline failures at Llama 3.1 8B: ~64 problems (based on H-M1 baseline pass@1=0.6098)
- Each failure = a Python function generated by Llama 3.1 8B that fails ≥1 unit test case
- Code artifacts: already written to `h-e1/results/` or `h-m1/results/`
- **Type:** standard (HumanEval is a standard established benchmark)
- **Preprocessing:** Load generated code strings from existing result files; write each to a temp .py file for static analysis
- **Sample size:** ~64 failure cases (full HumanEval failure set — NOT a subset)

**Loading Information** (for Phase 4 download):
- Method: JSON file load (reuse existing results)
- Identifier: `h-m1/results/baseline_results.json` or `h-e1/results/baseline_results.json`
- Code:
  ```python
  import json
  with open('docs/youra_research/h-e1/results/baseline_results.json') as f:
      baseline_results = json.load(f)
  failing_cases = [r for r in baseline_results if not r['passed']]
  ```

### Models

#### Baseline Model

**Architecture:** No model (static analysis tools only — pylint + mypy)
**Type:** Static analysis tools
**Configuration:**
- pylint: default configuration, all standard checkers enabled
- mypy: `--ignore-missing-imports --no-strict-optional` (lenient mode for generated function stubs)
- Analysis target: individual Python function files (the generated completions from HumanEval)

**Loading Information** (for Phase 4 download):
- Method: pip install (already available in experiment environment)
- Identifier: `pylint>=3.0`, `mypy>=1.0`
- Code:
  ```python
  # Verify tools available
  import subprocess
  subprocess.run(['python', '-m', 'pylint', '--version'], check=True)
  subprocess.run(['python', '-m', 'mypy', '--version'], check=True)
  ```

#### Proposed Model

**Architecture:** Pylint+mypy coverage measurement framework
**Integration Point:** Applied to each HumanEval baseline failure code file independently

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pylint+Mypy Coverage Measurement
# Based on: mypy.api docs + pylint.lint.Run() stackoverflow pattern
# Sources: mypy.readthedocs.io, stackoverflow.com/questions/2028268

import tempfile, os
from io import StringIO
from mypy import api as mypy_api
from pylint import lint
from pylint.reporters.text import TextReporter

def has_static_analysis_flag(code_str: str) -> tuple[bool, dict]:
    """
    Check if pylint+mypy flags ≥1 warning/error on generated code.
    Args:
        code_str: Python function string (LLM-generated completion)
    Returns:
        (flagged: bool, details: dict with pylint_count, mypy_count, categories)
    """
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code_str)
        tmp_path = f.name
    try:
        # Run pylint
        buf = StringIO()
        reporter = TextReporter(buf)
        runner = lint.Run([tmp_path, '--score=no'], reporter=reporter, exit=False)
        pylint_output = buf.getvalue()
        pylint_count = len([l for l in pylint_output.splitlines() if l.strip()])

        # Run mypy
        mypy_out, _, mypy_exit = mypy_api.run(
            ['--ignore-missing-imports', '--no-strict-optional', tmp_path]
        )
        mypy_count = mypy_exit  # 0=clean, 1=errors found

        flagged = (pylint_count > 0) or (mypy_exit != 0)
        return flagged, {'pylint_lines': pylint_count, 'mypy_exit': mypy_exit,
                         'pylint_output': pylint_output[:500]}
    finally:
        os.unlink(tmp_path)
```

### Training Protocol

**Note:** This is NOT a training experiment. H-M2 is a **static analysis measurement** experiment — no model training, no optimization, no learning rate.

**Execution Protocol:**
- Optimizer: N/A
- Learning Rate: N/A
- Seeds: 42 (for any bootstrap confidence interval resampling)
- Compute: CPU-only (static analysis tools); estimated runtime <5 minutes for 64 files
- Environment: Same as H-E1/H-M1 (Python 3.10+, pylint≥3.0, mypy≥1.0)

**Execution Steps:**
1. Load baseline failure list from h-e1 or h-m1 results (64 failing problems on HumanEval)
2. For each failing problem: write generated code to temp .py file → run pylint → run mypy → record whether ≥1 flag emitted
3. Compute coverage fraction = flagged_count / total_failures
4. Bootstrap 95% CI on coverage fraction (n_bootstrap=10000, seed=42)
5. Categorize pylint messages by type: E (Error), W (Warning), C (Convention), R (Refactor)
6. Report per-category counts and fraction of failures flagged by each category

### Evaluation

**Primary Metric:** coverage = (failures with ≥1 pylint/mypy flag) / (total HumanEval failures)
- Expected value: <0.50 based on H-M2 prediction
- Literature baseline: AssertionError = 63.64% of HumanEval errors (not catchable by pylint) → predicts coverage ≈ 20-40%

**Secondary Metrics:**
- pylint_category_distribution: fraction of flags that are E/W/C/R categories
- mypy_coverage: fraction covered by mypy alone (type errors)
- pylint_coverage: fraction covered by pylint alone (style/logic warnings)
- overlap: fraction covered by both tools

**Success Criteria (SHOULD_WORK gate):**
- Primary: coverage < 0.50 → supports mechanism hypothesis
- Secondary: Dominant category = C (Convention) or W (Warning), not E (Error) → supports "pylint misses functional failures" claim
- Null result: coverage ≥ 0.50 → challenges causal explanation; pipeline continues (SHOULD_WORK)

**Expected Baseline Performance (from literature):**
- AssertionError = 63.64% of HumanEval failures (source: arxiv.org/abs/2409.00676) — NOT catchable by pylint
- Logic errors dominate at Llama 3.1 8B tier (source: MDPI 2025 comparative study)
- Expected pylint coverage: ~20-40% (syntax/import/convention violations are minority)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (flagged / not flagged) per failure case
- Library: numpy, scipy.stats (bootstrap CI)
- Code:
  ```python
  import numpy as np
  from scipy import stats

  def bootstrap_ci(values, n_bootstrap=10000, seed=42):
      rng = np.random.default_rng(seed)
      means = [rng.choice(values, len(values)).mean() for _ in range(n_bootstrap)]
      return np.percentile(means, [2.5, 97.5])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Coverage fraction bar chart (pylint+mypy combined, pylint only, mypy only) vs 50% threshold line

#### Additional Figures (LLM Autonomous)

Based on the measurement nature of this experiment:

1. **Pylint Category Breakdown:** Stacked bar chart showing fraction of failures flagged by E/W/C/R category — distinguishes functional-error detection from style detection
2. **Coverage vs Failure Type Matrix:** Heatmap mapping pylint flag categories to problem difficulty/complexity (if HumanEval problem difficulty metadata available)
3. **Venn Diagram:** Overlap between pylint-flagged and mypy-flagged failure cases

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (coverage measurement script executes on all 64 failure cases)
2. `coverage < 0.50` (pylint+mypy flags fewer than half of HumanEval baseline failures)

**Gate Type:** SHOULD_WORK — pipeline continues even if coverage ≥ 0.50

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found in Archon KB (KB is focused on image generation domain, not LLM code analysis). All sources from Exa.

### B. GitHub Implementations (Exa)

**Source B.1: "Static Analysis as a Feedback Loop" (SCAM 2025)**
- **URL:** https://arxiv.org/html/2508.14419v1
- **Query Used:** "pylint mypy static analysis LLM generated code HumanEval failure detection coverage"
- **Relevance:** Direct evidence that pylint/Bandit primarily detects convention/style issues on LLM code, not functional correctness failures
- **Key Finding:** "Pylint's Convention checks evaluate readability... Warning reports serve as proxies for reliability concerns" — confirms pylint's blind spot for logic errors
- **Used For:** Hypothesis grounding; confirms pylint bias toward style/convention (supports <50% coverage prediction)

**Source B.2: "Characteristics of Code Generation Errors" (NSF 2024)**
- **URL:** https://par.nsf.gov/servlets/purl/10617730
- **Query Used:** "HumanEval MBPP code generation baseline failure analysis logic error runtime error python"
- **Key Finding:** "most of the incorrect code solutions are compilable and runnable without any compilation errors... modern LLMs have adequately learned the syntax rules but struggle with understanding intricacies in natural language task descriptions and generating delicate code with sophisticated logic"
- **Used For:** Dataset specification (confirms failures are logic-based, not syntax/static-detectable)
- **Results:** Undefined name, missing steps, garbage code are top failure types — most NOT statically detectable

**Source B.3: "Fixing Code Generation Errors for LLMs" (arxiv 2409.00676)**
- **URL:** https://arxiv.org/html/2409.00676v1
- **Query Used:** "HumanEval MBPP code generation baseline failure analysis logic error runtime error python"
- **Key Finding:**
  - 12,837 errors from 14 LLMs on HumanEval: AssertionError = 63.64% (most common)
  - Only 3 of 19 root causes are statically fixable: Missing Import, Function Overflow, Inconsistent Indentation
  - "16 causes belong to the incapability of LLMs" — not catchable by pylint
- **Used For:** Expected baseline performance estimate (predicts coverage ≈ 20-37%)
- **Results:** Directly supports H-M2 primary prediction (coverage < 50%)

**Source B.4: Mypy API Documentation**
- **URL:** https://mypy.readthedocs.io/en/stable/extending_mypy.html
- **Query Used:** "run pylint mypy on Python code programmatically subprocess coverage measurement script"
- **Key Code:**
  ```python
  from mypy import api
  result = api.run(['--ignore-missing-imports', 'file.py'])
  # result = (stdout, stderr, exit_status)
  ```
- **Used For:** Core mechanism pseudo-code (programmatic mypy invocation)

**Source B.5: Stack Overflow — Pylint programmatic invocation**
- **URL:** https://stackoverflow.com/questions/2028268/invoking-pylint-programmatically
- **Query Used:** "run pylint mypy on Python code programmatically subprocess coverage measurement script"
- **Key Code:**
  ```python
  from pylint import lint
  from pylint.reporters.text import TextReporter
  run = lint.Run([filepath], reporter=TextReporter(buf), exit=False)
  ```
- **Used For:** Core mechanism pseudo-code (programmatic pylint invocation)

**Source B.6: openai/human-eval execution.py**
- **URL:** https://github.com/openai/human-eval/blob/master/human_eval/execution.py
- **Relevance:** Defines the execution harness and what constitutes a "pass" vs "fail" on HumanEval; confirms failures are test-case-based (AssertionError on unit tests)
- **Used For:** Dataset specification (baseline failure definition)

**Source B.7: "Comparative Analysis of AI Models for Python Code Generation" (MDPI 2025)**
- **URL:** https://www.mdpi.com/2076-3417/15/18/9907
- **Key Finding:** Error distribution at GPT-3.5/Llama 3.1 8B tier: Logic errors 20.1%, Runtime 4.9%, Syntax 3.0% of ALL attempts. Of FAILURES, logic errors dominate.
- **Used For:** Expected baseline performance (predicts pylint coverage <50%)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. The experiment mechanism (programmatic pylint/mypy invocation) is well-documented in official docs and Stack Overflow examples. No complex neural architecture to analyze.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — h-m1
**File:** `docs/youra_research/h-m1/04_validation.md`

**Reused Components:**
- Baseline failure list: HumanEval failures at Llama 3.1 8B baseline (pass@1=0.6098 → ~64 failures)
- Code artifacts: baseline-generated Python functions already stored in h-e1/h-m1 results
- Environment: pylint, mypy already installed

**Why Reused:** H-M2 requires NO new LLM inference — it is a post-hoc measurement on existing artifacts. The baseline failure cases were collected as part of H-E1 verification protocol step 4: "Run pylint+mypy on all no-feedback baseline failure cases without execution; record fraction flagged."

**Key predecessor result motivating H-M2:**
- HumanEval McNemar: exec_only=15, pylint_only=0 → execution uniquely repairs 15 problems pylint cannot
- MBPP McNemar: exec_only=85, pylint_only=2 → execution uniquely repairs 85 problems pylint cannot
- H-M2 tests whether this gap is because pylint doesn't even flag the failure cases as problematic

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset type (real, standard) | H-M1 predecessor | h-m1/04_validation.md |
| Failure count (~64 HumanEval failures) | H-M1 results | H-M1 baseline pass@1=0.6098 |
| Expected coverage <50% | Literature (Exa B.3) | arxiv 2409.00676: AssertionError=63.64% |
| pylint style-bias finding | Literature (Exa B.1) | SCAM 2025 pylint convention finding |
| Logic error dominance | Literature (Exa B.2, B.4) | NSF study + MDPI 2025 |
| Programmatic pylint API | Exa B.5 | stackoverflow.com/questions/2028268 |
| Programmatic mypy API | Exa B.4 | mypy.readthedocs.io |
| Bootstrap CI | Standard stats | scipy.stats, numpy |
| HumanEval execution harness | Exa B.6 | openai/human-eval |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T06:30:00Z

### Workflow History for This Hypothesis

- h-m1 COMPLETED (PASS) — prerequisite satisfied
- h-m2 set to IN_PROGRESS — 2026-08-05T06:26:07
- Phase 2C initiated for h-m2 — 2026-08-05 (current)

---

*MCP Tools Used: Archon (0 relevant results), Exa (7 sources: SCAM 2025, NSF error study, arxiv 2409.00676, MDPI 2025, mypy docs, SO pylint API, openai/human-eval)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

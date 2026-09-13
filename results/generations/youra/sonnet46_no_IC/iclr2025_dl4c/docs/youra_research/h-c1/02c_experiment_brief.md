---
hypothesis_id: "h-c1"
hypothesis_title: "Doctest Prevalence Feasibility Boundary Condition"
date: "2026-08-04"
author: "Anonymous"
specification_level: "1.5"
experiment_type: "CONDITION (Observational Pilot Scan)"
phase: "Phase 2C"
status: "COMPLETED"
---

# Experiment Design: H-C1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under a scan of The Stack Python (bigcode/the-stack-dedup) Python subset, if a systematic pilot scan of 10,000 randomly sampled files is conducted, then the proportion of files containing at least one valid doctest (parseable and executable) is ≥3%, because Python ecosystem conventions (NumPy, SciPy, standard library) encourage doctest-style function documentation in library and educational code.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION (Observational) Template** — This hypothesis is a feasibility boundary check via a corpus pilot scan. No model training occurs. The "experiment" is a data characterization pipeline.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (first hypothesis in practical execution order)
**Gate Status:** SHOULD_WORK — if prevalence <1%, fall back to 2-condition design

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** None (runs before H-E1 in practice)

### Gate Condition
SHOULD_WORK: If ≥3% doctest prevalence confirmed → proceed to full 3-condition experiment (H-E1). If 1-3% → reduce token budget. If <1% → fall back to 2-condition design. Gate failure does NOT stop pipeline; it scopes H-E1.

---

## Continuation Context

**Previous Hypothesis Results:** None — H-C1 is the first practical execution step.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon KB searches for "doctest extraction Python corpus scanning" and "Python doctest extraction file scanning" returned results from diffusers/image generation domain (similarity ~0.33-0.37) — no directly relevant past cases in KB for this specific task. The experiment design is therefore grounded in Exa findings and The Stack paper methodology.

**Key insight from KB:** The Stack itself (Kocetkov et al., 2022) used `py_compile` on 10,000 Python samples for internal quality analysis — directly parallel to H-C1's design. The Stack paper's analysis of docstrings found 18% of file volume consists of docstrings and comments, with 20% of files having little/no natural text. This indicates meaningful docstring density but does not directly report doctest prevalence.

### Archon Code Examples

No relevant code examples found in Archon KB for this specific task. See Exa findings below for implementation patterns.

### Exa GitHub Implementations

**Finding 1: The Stack Paper Methodology (bigcode/the-stack, Kocetkov et al. 2022)**
- **Source:** The Stack paper (openreview.net, arxiv 2211.15533)
- **Relevance:** The Stack's own internal analysis used exactly the same approach: 10,000-file sample + `py_compile` module + `ast` module for docstring extraction
- **Key quote:** "Next, we estimate the number of valid Python files by using the py_compile module on 10,000 samples from our dataset... We analyze a subset of 10,000 files. We first use the ast and tokenize modules to extract docstrings and comments."
- **Used for:** Sample size validation (10k files), tool selection (ast + compile), analysis methodology

**Finding 2: Python doctest module (docs.python.org)**
- **Source:** Python 3 stdlib doctest documentation
- **Key API:** `doctest.DocTestParser` — parses doctest examples from strings without executing code; `doctest.DocTestFinder` — finds all doctests in a module's docstrings; `doctest.DocTestRunner` — executes examples
- **Safe scanning pattern:** Parse with `DocTestParser.get_examples(string)` to detect presence without execution; execute only in subprocess with timeout for counting executability
- **Used for:** Core mechanism pseudo-code design

**Finding 3: paiml/python-doctest-corpus-test (HuggingFace)**
- **Source:** huggingface.co/datasets/paiml/python-doctest-corpus-test
- **Relevance:** Demonstrates that curated Python doctest corpora exist; confirms doctest patterns in real Python code (function signatures + `>>>` patterns)
- **Used for:** Confirming doctest format patterns; dataset type is "custom/curated" not The Stack

**Finding 4: The Stack loading via HuggingFace Datasets streaming**
- **Source:** huggingface.co/datasets/bigcode/the-stack-dedup
- **Key code pattern:**
  ```python
  from datasets import load_dataset
  ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/python",
                    streaming=True, split="train")
  for sample in ds:
      content = sample["content"]
  ```
- **Note:** Streaming mode avoids downloading full 3TB; Python subset is ~49.7GB (12.96M files per filtered derivative)
- **Used for:** Dataset loading specification

### 🎯 Implementation Priority Assessment

**CRITICAL: H-C1 is an observational scan — there is no "paper reproduction" or "proposed model". The implementation is a scanning/analysis script.**

**Recommended Implementation Path:**
- Primary: Custom Python scanning script using `datasets` (streaming) + `ast` + `doctest.DocTestParser` + subprocess execution with timeout
- Fallback: Random subsample from pre-downloaded parquet files if streaming is too slow
- Justification: The Stack paper's own methodology (py_compile + ast on 10k files) is the gold standard precedent; stdlib tools (ast, doctest) are sufficient; no external dependencies needed beyond `datasets`

### Code Analysis (Serena MCP)

Serena analysis not performed — H-C1 does not involve an existing codebase to analyze. The scanning pipeline is implemented from scratch using Python stdlib (ast, doctest) + HuggingFace datasets streaming. Sufficient implementation guidance is available from The Stack paper methodology and Python stdlib documentation.

---

## Experiment Specification

### Dataset

**Name:** bigcode/the-stack-dedup (Python subset)
**Type:** standard (publicly available, established corpus)
**Version:** Current (as of 2026-08-04)
**Source:** HuggingFace Hub
**Python subset size:** ~12.96M files, ~49.7GB (per ytzi/the-stack-dedup-python-filtered derivative)
**License:** Various permissive licenses (per The Stack terms)

**Pilot Scan Parameters:**
- **Sample size:** 10,000 randomly sampled Python files (matches The Stack paper's own analysis methodology)
- **Sampling method:** Reservoir sampling via streaming (fixed seed=42 for reproducibility)
- **File size filter:** Apply same quality filters as The Stack paper (avg line length ≤100 chars, max line length ≤1000 chars, alphanum fraction ≥0.25)
- **Language:** Python only (`data_dir="data/python"`)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets` streaming
- Identifier: `bigcode/the-stack-dedup`
- Code:
  ```python
  from datasets import load_dataset
  ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/python",
                    streaming=True, split="train")
  ```

### Models

#### Baseline Model (Scanning Script — "Unfiltered" Rate)

**Architecture:** Doctest-pattern detector using Python `ast` module + `doctest.DocTestParser`
**Purpose:** Measure raw prevalence of files containing ≥1 `>>>` doctest pattern
**Implementation:** AST-based docstring extraction without execution (fast pass)

**Loading Information** (for Phase 4 download):
- Method: Python stdlib (no download required)
- Identifier: `ast`, `doctest` (stdlib modules)
- Code:
  ```python
  import ast, doctest
  parser = doctest.DocTestParser()
  ```

#### Proposed Model (Scanning Script — "Executable Doctest" Rate)

**Architecture:** Baseline + doctest execution gate (subprocess with timeout)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Doctest Prevalence Scanner
# Based on: The Stack paper methodology (Kocetkov et al. 2022) + Python stdlib doctest

import ast
import doctest
import subprocess
import sys
import textwrap

def has_doctest_pattern(source_code: str) -> bool:
    """Check if file contains any >>> pattern (fast pre-filter)."""
    return ">>>" in source_code

def extract_doctest_examples(source_code: str) -> list:
    """Extract all doctest examples from a Python source string via AST."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    parser = doctest.DocTestParser()
    examples = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring and ">>>" in docstring:
                try:
                    tests = parser.get_examples(docstring)
                    examples.extend(tests)
                except Exception:
                    pass
    return examples

def execute_doctest_in_subprocess(source_code: str, timeout_sec: int = 5) -> bool:
    """Run doctest execution in isolated subprocess with timeout."""
    wrapper = textwrap.dedent(f"""
import doctest, sys
source = {repr(source_code)}
import types
m = types.ModuleType("_scan_module")
try:
    exec(compile(source, "<scan>", "exec"), m.__dict__)
except Exception:
    sys.exit(1)
results = doctest.testmod(m, verbose=False)
sys.exit(0 if results.failed == 0 else 1)
""")
    try:
        result = subprocess.run(
            [sys.executable, "-c", wrapper],
            timeout=timeout_sec, capture_output=True
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
```

### Training Protocol

**Note:** H-C1 is an observational pilot scan — no model training occurs. The "protocol" is the scan execution procedure.

**Scan Execution Protocol:**
- **Tool:** Python 3.10+ (matches The Stack's Python version support)
- **Sample size:** 10,000 files (fixed, matches The Stack paper's own analysis sample size)
- **Random seed:** 42 (fixed for reproducibility)
- **Reservoir sampling:** Take first 10,000 elements from shuffled stream (`ds.shuffle(seed=42, buffer_size=10000)`)
- **Parallelism:** ProcessPoolExecutor with 4 workers for subprocess-based doctest execution
- **Per-file timeout:** 5 seconds for doctest execution subprocess (prevents hanging on infinite loops)
- **Estimated runtime:** ~2-4 hours for 10,000 files (dominated by subprocess overhead for execution step)
- **Output format:** JSON file with per-file results + aggregate statistics

**Scan Phases (sequential):**
1. **Phase A — Pattern filter (fast):** Check `">>>" in source_code` → count files with any doctest pattern
2. **Phase B — AST extraction:** For pattern-positive files, extract all doctest examples via AST
3. **Phase C — Execution gate:** For AST-positive files, run subprocess execution with timeout → count passing files

**Token Counting:** For doctest-passing files, measure token count via `len(source_code.split())` × 1.3 (approximate token:word ratio for code) or use HuggingFace tokenizer (Qwen2.5-Coder-1.5B tokenizer).

**Seeds:** 1 (seed=42, fixed)

### Evaluation

**This is an observational study — evaluation = statistical summary of scan results.**

**Primary Metrics:**
- `doctest_pattern_rate`: % of 10,000 sampled files with ≥1 `>>>` pattern
- `doctest_executable_rate`: % of 10,000 sampled files with ≥1 successfully executable doctest
- `estimated_token_pool`: Extrapolated token count of doctest-passing files in full Python subset

**Success Criteria:**
- `doctest_executable_rate` ≥ 3.0% → **PASS** (proceed to 3-condition H-E1)
- `estimated_token_pool` ≥ 500M tokens → **PASS** (sufficient for N-token budget)
- `doctest_executable_rate` 1-3% → **SCOPE** (reduce N, still feasible)
- `doctest_executable_rate` < 1% → **PIVOT** (fall back to 2-condition design)

**Expected Baseline Performance (from research):**
- The Stack paper found 18% of file volume consists of docstrings/comments
- Python ecosystem conventions (NumPy, SciPy, stdlib) use doctests heavily in library code
- Prior art suggests 5-15% of library-quality Python files contain doctests (informal estimate from ecosystem patterns)
- Expected: `doctest_pattern_rate` ~15-25%, `doctest_executable_rate` ~3-10%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Data characterization / observational scan
- Library: Python stdlib (`ast`, `doctest`, `subprocess`) + `datasets` (HuggingFace)
- Code:
  ```python
  # Aggregate results
  results = {
      "n_sampled": 10000,
      "n_pattern_positive": count_pattern,
      "n_executable_positive": count_executable,
      "doctest_pattern_rate": count_pattern / 10000,
      "doctest_executable_rate": count_executable / 10000,
      "estimated_full_subset_executable_files": count_executable / 10000 * 12_960_052,
      "estimated_token_pool_M": token_sum_executable / 1e6,
  }
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — doctest_pattern_rate vs doctest_executable_rate vs 3% threshold line

#### Additional Figures (LLM Autonomous)
- **Prevalence breakdown:** Stacked bar showing: no-doctest / pattern-only (not executable) / executable-doctest proportion
- **Token pool estimate:** Horizontal bar showing estimated token pool vs 500M target threshold
- **Error type distribution:** Pie chart of doctest execution failure modes (timeout / exception / wrong output / import error)
- **File size distribution:** Histogram of token counts for doctest-passing vs non-passing files

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Scan script runs without crash on 10,000 files
2. `doctest_executable_rate` ≥ 3.0% (or rate in 1-3% range triggers SCOPE response, not failure)

**Gate type is SHOULD_WORK:** Any result is actionable — even <1% produces a clear PIVOT decision. The scan cannot "fail" in a blocking sense; it scopes the rest of the pipeline.

---

## 🔬 Mechanism Verification Protocol

**Mechanism exists?** Yes — doctest patterns are detectable via `>>>` substring search
**Mechanism isolatable?** Yes — AST extraction + subprocess execution are fully independent steps
**Baseline measurable?** Yes — pattern rate (Phase A) is the baseline; executable rate (Phase C) is the proposed

**Architecture compatibility:** N/A (no neural architecture; pure Python pipeline)

**Activation indicators:**
- Log message: `"Phase A complete: {n} / 10000 files contain doctest patterns ({rate:.1%})"`
- Log message: `"Phase C complete: {n} / 10000 files have executable doctests ({rate:.1%})"`
- Tensor shape change: N/A (no tensors)
- Expected metric delta: `doctest_executable_rate` should be 3-10x lower than `doctest_pattern_rate` (many pattern-positive files have broken/environment-dependent doctests)

**Failure detection:**
- If Phase C rate ≈ Phase A rate → subprocess timeout too long or execution is not actually testing
- If Phase C rate = 0% → doctest execution is broken (check subprocess environment)
- If scan crashes → check for UnicodeDecodeError on source files (add try/except + skip)

**Mechanism verification code:**
```python
assert results["doctest_executable_rate"] <= results["doctest_pattern_rate"], \
    "Executable rate cannot exceed pattern rate"
assert results["n_sampled"] == 10000, "Sample size must be exactly 10000"
print(f"GATE CHECK: executable_rate={results['doctest_executable_rate']:.3f}")
print(f"STATUS: {'PASS (≥3%)' if results['doctest_executable_rate'] >= 0.03 else 'SCOPE (1-3%)' if results['doctest_executable_rate'] >= 0.01 else 'PIVOT (<1%)'}")
```

**Hypothesis support threshold:** `doctest_executable_rate` ≥ 0.03
**Hypothesis support metric:** `doctest_executable_rate`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon Search 1:** Query: "doctest extraction Python corpus scanning"
- **Result:** No directly relevant results (similarity scores 0.35-0.36, domain mismatch — diffusers/stable-diffusion)
- **Used for:** Confirmed no past cases; design grounded in Exa + paper methodology

**Archon Search 2:** Query: "Python doctest extraction file scanning"
- **Result:** No directly relevant code examples (highest score: HuggingFace cache scanning, unrelated)
- **Used for:** Confirmed need to rely on Exa / primary literature

### B. GitHub Implementations (Exa)

**Source 1: The Stack Paper (Kocetkov et al., 2022)**
- **URL:** https://openreview.net/pdf/f1643b8d22ae666f88564de20ec7b8b91d216106.pdf / arxiv:2211.15533
- **Query Used:** "Python doctest prevalence rate bigcode the-stack HuggingFace corpus scan"
- **Relevance:** Directly parallel methodology: "we estimate the number of valid Python files by using the py_compile module on 10,000 samples from our dataset... we use the ast and tokenize modules to extract docstrings and comments"
- **Key Insights:**
  - 10k file sample size is validated methodology for The Stack corpus analysis
  - `ast` + `tokenize` modules for docstring extraction (we extend with `doctest.DocTestParser`)
  - 18% of file volume = docstrings/comments; 20% of files have little/no natural text
- **Used for:** Sample size selection (10k files), tool selection (ast), methodology validation

**Source 2: Python stdlib doctest module**
- **URL:** https://docs.python.org/3/library/doctest.html
- **Query Used:** "Python doctest execution scanning corpus ast module extract docstring timeout subprocess"
- **Key APIs identified:**
  - `doctest.DocTestParser.get_examples(string)` — extract Examples objects without execution
  - `doctest.DocTestFinder` — finds all doctests in module's docstrings recursively
  - `doctest.DocTestRunner` — executes examples
- **Used for:** Core mechanism pseudo-code; subprocess isolation pattern

**Source 3: HuggingFace bigcode/the-stack-dedup dataset card**
- **URL:** https://huggingface.co/datasets/bigcode/the-stack-dedup
- **Key Info:** Streaming load API confirmed; Python subset ~12.96M files (~49.7GB); `data_dir="data/python"` filter works
- **Used for:** Dataset loading code, sample size context

**Source 4: paiml/python-doctest-corpus-test**
- **URL:** https://huggingface.co/datasets/paiml/python-doctest-corpus-test
- **Relevance:** Confirms existence of Python doctest corpora; schema shows `>>> function(args)` / expected output format
- **Used for:** Format confirmation for doctest pattern matching

**Source 5: AST docstring extraction pattern**
- **URL:** https://dev.to/waylonwalker/get-python-docstring-with-ast-1kc2
- **Key Code Pattern:**
  ```python
  tree = ast.parse(raw_source)
  functions = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)]
  function_docs = [ast.get_docstring(f) for f in functions]
  ```
- **Used for:** AST-based docstring extraction in pseudo-code

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — H-C1 does not involve analysis of an existing project codebase. The scanning pipeline is implemented from Python stdlib components (ast, doctest, subprocess) documented in official Python docs. Sufficient implementation guidance available from The Stack paper and Python stdlib documentation.

### D. Previous Hypothesis Context

**Previous Context:** None — H-C1 is the first hypothesis in practical execution order.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Sample size (10,000 files) | Academic paper | The Stack paper (Kocetkov et al. 2022): "10,000 samples" |
| Dataset loading method | HuggingFace docs | bigcode/the-stack-dedup streaming API |
| Doctest pattern detection (`>>>`) | Python stdlib docs | doctest module documentation |
| AST docstring extraction | Blog + stdlib | ast.walk + ast.get_docstring pattern |
| DocTestParser usage | Python stdlib docs | doctest.DocTestParser.get_examples() |
| Subprocess isolation with timeout | Python stdlib | subprocess.run(timeout=5) pattern |
| 3% threshold | Phase 2B | Assumption A1 from verification_plan.md |
| 500M token target | Phase 2B | Main hypothesis token budget |
| File quality filters | The Stack paper | Avg/max line length, alphanum fraction |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| Hypothesis defined | 2026-08-04T17:27:00Z | H-C1 created in Phase 2B verification plan |
| Set to IN_PROGRESS | 2026-08-04T17:29:37Z | External loop starting Phase 2C → 3 → 4 |
| Phase 2C started | 2026-08-04 | Experiment design initiated (unattended mode) |
| Phase 2C completed | 2026-08-04 | 02c_experiment_brief.md generated |

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results found), Exa (Web search + Code context), Serena (not applicable for this hypothesis)*
*All specifications grounded in The Stack paper methodology and Python stdlib documentation*
*Next Phase: Phase 3 - Implementation Planning (scanning pipeline)*

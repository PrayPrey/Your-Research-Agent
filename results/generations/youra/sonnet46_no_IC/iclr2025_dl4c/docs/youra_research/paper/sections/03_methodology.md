# Methodology

Building on the observation that Python's `>>>` patterns may not correspond to independently-
executable doctests, we design a three-phase filtering pipeline to measure the gap between
documentation intent and actual executability at corpus scale. This pipeline serves two
purposes: (1) it characterizes the feasibility of doctest-passing filtering as a corpus
quality gate (H-C1, the focus of this paper), and (2) it provides the compile-only
infrastructure for the planned SFT quality comparison experiment (H-E1).

## Overview

Our methodology consists of a three-phase pipeline applied to a random sample of Python
files from a curated Python code corpus. Each phase applies a strictly stronger executability
condition, enabling phase-by-phase attrition measurement:

- **Phase A (Pattern):** Does the file contain any `>>>` substring?
- **Phase B (AST):** Does the file contain AST-parseable doctest examples?
- **Phase C (Subprocess):** Do the doctest examples pass subprocess execution in a clean environment?

Figure 1 shows the filtering funnel and the resulting file counts at each stage. The pipeline
is implemented as a modular Python pipeline: `data_loader.py` → `scanner.py` → `results.py`
→ `visualize.py` → `gate.py`, orchestrated by `run_scan.py`.

## Data Source and Sampling

**Dataset:** We scan `codeparrot/codeparrot-clean-valid`, a curated Python-only corpus
publicly accessible on HuggingFace Hub without access credentials. This is used as a proxy
for `bigcode/the-stack-dedup` (The Stack Python, 12.96M files, 49.7GB), which requires
explicit access approval. Both datasets use the same `content` field schema and contain
Python-only code. We expect the feasibility finding (0.1% executable rate) to be
representative of curated Python code corpora.

**Sample Size:** 10,000 randomly sampled files, consistent with The Stack paper's own
methodology [Kocetkov et al., 2022]: "we estimate the number of valid Python files by
using the py_compile module on 10,000 samples." Files are drawn via reservoir sampling
from a shuffled stream (`seed=42`, `buffer_size=10,000`).

**Quality Pre-filter:** We apply The Stack paper's quality filters before sampling:
average line length ≤ 100 characters, maximum line length ≤ 1,000 characters, and
alphanumeric fraction ≥ 0.25. Files failing these criteria are excluded before the
doctest scan.

## Three-Phase Filtering Pipeline

### Phase A: Pattern Detection (Fast Pre-filter)

**Condition:** `">>>" in source_code`

Phase A is a simple substring check for the `>>>` prompt that Python's doctest convention
uses to mark interactive examples. Files passing Phase A are candidates for further analysis.

**Rationale:** Pattern detection is O(n) in file length and requires no parsing. It provides
an upper bound on how many files could possibly contain executable doctests. The Phase A rate
represents the documentation intent density of the corpus.

### Phase B: AST Extraction

**Condition:** The file can be parsed by Python's `ast` module, and at least one doctest
`Example` object can be extracted from the parsed docstrings.

```python
tree = ast.parse(source_code)
parser = doctest.DocTestParser()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        docstring = ast.get_docstring(node)
        if docstring and ">>>" in docstring:
            examples = parser.get_examples(docstring)
            if examples:
                return True  # Phase B positive
```

Phase B eliminates files with syntax errors (which cannot be parsed) and `>>>` patterns
that are not doctest-formatted (e.g., shell prompts embedded in comments).

**Rationale:** AST extraction confirms structural well-formedness of the doctest examples
before the expensive subprocess execution step. It filters ~35% of Phase A positives
(310 → 204 files in our scan), avoiding unnecessary subprocess overhead.

### Phase C: Subprocess Execution

**Condition:** The Python file's doctests pass execution in an isolated subprocess
with a 5-second timeout, without pre-installed third-party packages.

```python
def phase_c_worker(source: str, timeout: int = 5) -> dict:
    import base64, subprocess, sys
    script = f"""
import doctest, sys, types
import base64
source = base64.b64decode({base64.b64encode(source.encode()).decode()!r}).decode()
m = types.ModuleType("_scan_module")
try:
    exec(compile(source, "<scan>", "exec"), m.__dict__)
except Exception as e:
    sys.exit(f"exec_error:{{type(e).__name__}}")
results = doctest.testmod(m, verbose=False)
sys.exit(0 if results.failed == 0 else f"test_failed:{{results.failed}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        timeout=timeout, capture_output=True, text=True
    )
    passed = result.returncode == 0
    error_type = _classify_error(result.stderr) if not passed else None
    return {"passed": passed, "error_type": error_type}
```

**Base64 Isolation:** Source code is encoded as base64 before embedding in the subprocess
script. This eliminates shell quoting errors across all file types (files with backticks,
quotes, escape sequences) and was validated across all 10,000 test files with zero quoting
errors.

**Parallelism:** Phase C uses `ProcessPoolExecutor` with 4 workers. Only Phase B positive
files (204 in our scan) are submitted to Phase C, limiting subprocess overhead. The 4-worker
configuration achieves ~4× speedup over sequential execution.

**Timeout:** Each file gets a 5-second subprocess timeout, preventing hangs from infinite
loops or blocking I/O in doctest code.

**Rationale:** The subprocess isolation is the critical design choice. Running doctest
execution in the main process would: (a) pollute the main process namespace with imported
modules, (b) risk crashes from malformed code, and (c) prevent accurate error classification.
The subprocess boundary ensures that each file is evaluated in a clean environment,
faithfully simulating deployment conditions where third-party packages may not be installed.

**Error Classification:** Failed Phase C files are classified by error type from subprocess
stderr: `import_error` (ImportError, ModuleNotFoundError), `exec_error` (other exception
during file execution), `test_failed` (doctest examples produce wrong output), and `timeout`.

## Token Estimation

For files passing Phase C (executable doctests), we estimate token counts as:

```
tokens ≈ len(source_code.split()) × 1.3
```

This word-count approximation is consistent with code tokenization ratios and provides
a fast estimate without requiring a full tokenizer pass. The aggregate `estimated_token_pool_M`
is extrapolated from the sample rate to the full corpus size (12.96M files).

## Gate Evaluation

The feasibility scan is evaluated against predefined thresholds derived from the 500M-token
SFT budget:

| Result | `doctest_executable_rate` | `estimated_token_pool` | Decision |
|--------|--------------------------|------------------------|----------|
| **PASS** | ≥ 3.0% | ≥ 500M tokens | Proceed to 3-condition H-E1 |
| **SCOPE** | 1.0–3.0% | Reduced | Reduce token budget |
| **PIVOT** | < 1.0% | < threshold | 2-condition H-E1 (compile-only vs. unfiltered) |

The PIVOT decision does not halt the pipeline; it scopes the subsequent SFT experiment
design to the feasible compile-only condition.

## Planned SFT Comparison (H-E1)

The compile-only SFT experiment is designed and pending execution. The compile-only filter:

```python
try:
    compile(source_code, "<string>", "exec")
    return True  # Syntactically valid
except SyntaxError:
    return False
```

**H-E1 Design:**
- **Model:** Qwen2.5-Coder-1.5B (primary)
- **Conditions:** (a) unfiltered random subsample, (b) compile()-filtered subsample
- **Token budget:** 500M tokens per condition (equal budget)
- **Training:** AdamW, lr=2e-5, batch=32, 3 epochs, seed=42
- **Evaluation:** HumanEval pass@1 (greedy), MBPP pass@1 (greedy), lm-evaluation-harness
- **Gate:** MUST_WORK — compile-only filtered ≥ unfiltered + 2pp HumanEval pass@1

The equal-token-budget design isolates the quality signal of compile() filtering from
data quantity effects. Without equal budget, observed performance differences could
reflect regularization from fewer training examples rather than quality improvement.

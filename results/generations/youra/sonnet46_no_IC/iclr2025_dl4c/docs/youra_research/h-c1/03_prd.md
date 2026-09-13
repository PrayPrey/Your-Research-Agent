---
hypothesis_id: "h-c1"
document_type: "PRD"
phase: "Phase 3"
generated_at: "2026-08-04"
author: "Anonymous"
stepsCompleted:
  - executive_summary
  - problem_statement
  - functional_requirements
  - non_functional_requirements
  - data_specification
  - evaluation_metrics
  - dependencies
  - success_criteria
---

# Product Requirements Document: H-C1

**Doctest Prevalence Pilot Scanner — Feasibility Boundary Condition**

---

## 1. Executive Summary

H-C1 is an observational feasibility study that scans The Stack Python corpus to determine whether ≥3% of Python files contain at least one successfully executable doctest. This boundary condition determines the viability of the doctest execution gate for downstream hypothesis H-E1. The deliverable is a scanning pipeline (Python script) that streams 10,000 randomly sampled Python files from `bigcode/the-stack-dedup`, runs three sequential analysis phases (pattern detection → AST extraction → subprocess execution), and produces a JSON results file with aggregate statistics.

**No model training occurs.** The experiment is pure data characterization.

---

## 2. Problem Statement

The main pipeline hypothesis (H-ExecFilteredSFT-v1) proposes training on execution-filtered data (files passing compile() + doctest execution). Before committing to a 3-condition training experiment, we must verify that the doctest-passing subset of The Stack Python is large enough to provide a meaningful token budget (≥500M tokens). If too few Python files contain valid, executable doctests, the doctest condition is not feasible, and H-E1 must fall back to a 2-condition design.

**Core question:** What fraction of Python files in The Stack contain ≥1 successfully executable doctest?

---

## 3. Functional Requirements

### FR-1: Dataset Streaming
- Load The Stack Python subset from `bigcode/the-stack-dedup` using HuggingFace `datasets` streaming API
- Filter to `data_dir="data/python"`, `split="train"`
- Apply reservoir sampling with fixed `seed=42`, `buffer_size=10000`
- Apply The Stack quality filters: avg line length ≤100 chars, max line length ≤1000 chars, alphanum fraction ≥0.25
- Sample exactly **10,000** files

### FR-2: Phase A — Pattern Filter (fast pre-screen)
- Check `">>>" in source_code` for each file
- Count and record `n_pattern_positive` (files containing any `>>>` pattern)
- Compute `doctest_pattern_rate = n_pattern_positive / 10000`
- Log: `"Phase A complete: {n} / 10000 files contain doctest patterns ({rate:.1%})"`

### FR-3: Phase B — AST Docstring Extraction
- For pattern-positive files only: parse with `ast.parse(source_code)`
- Walk AST for `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Module` nodes
- Extract docstrings via `ast.get_docstring(node)`
- Parse doctest examples via `doctest.DocTestParser().get_examples(docstring)`
- Handle `SyntaxError` and `Exception` gracefully (skip file)
- Record which files have ≥1 parseable doctest example

### FR-4: Phase C — Subprocess Execution Gate
- For AST-positive files only: execute full doctest suite in isolated subprocess with timeout
- Subprocess wrapper: compile source, exec into module, run `doctest.testmod()`
- Timeout: **5 seconds** per file (prevents infinite loops)
- Count `n_executable_positive` (files where `result.returncode == 0`)
- Compute `doctest_executable_rate = n_executable_positive / 10000`
- Log: `"Phase C complete: {n} / 10000 files have executable doctests ({rate:.1%})"`

### FR-5: Token Pool Estimation
- For doctest-passing files: estimate token count via HuggingFace tokenizer (Qwen2.5-Coder-1.5B) or approximation `len(source_code.split()) * 1.3`
- Compute `estimated_token_pool_M = token_sum / 1e6`
- Extrapolate to full Python subset: `estimated_full_subset_executable_files = n_executable_positive / 10000 * 12_960_052`

### FR-6: Results Output
- Write JSON file: `docs/youra_research/h-c1/results.json` with aggregate statistics
- Write per-file results (optional, for debugging): `docs/youra_research/h-c1/per_file_results.jsonl`
- Results schema:
  ```json
  {
    "n_sampled": 10000,
    "n_pattern_positive": <int>,
    "n_executable_positive": <int>,
    "doctest_pattern_rate": <float>,
    "doctest_executable_rate": <float>,
    "estimated_full_subset_executable_files": <int>,
    "estimated_token_pool_M": <float>,
    "scan_duration_seconds": <float>,
    "seed": 42,
    "dataset": "bigcode/the-stack-dedup",
    "filter": "data/python"
  }
  ```

### FR-7: Parallelism
- Use `ProcessPoolExecutor` with 4 workers for Phase C subprocess execution
- Phases A and B run sequentially per file (fast enough single-threaded)

### FR-8: Visualization
- Required figure: Bar chart comparing `doctest_pattern_rate` vs `doctest_executable_rate` vs 3% threshold line
- Additional figures (autonomous): prevalence breakdown stacked bar, token pool estimate bar, error type distribution pie, file size distribution histogram
- Save all figures to `docs/youra_research/h-c1/figures/`

### FR-9: Gate Check & Reporting
- After scan: compute gate status and print:
  ```
  GATE CHECK: executable_rate={rate:.3f}
  STATUS: PASS (≥3%) | SCOPE (1-3%) | PIVOT (<1%)
  ```
- Assertion: `doctest_executable_rate <= doctest_pattern_rate`
- Assertion: `n_sampled == 10000`

---

## 4. Data Specification

### Primary Dataset

| Property | Value |
|----------|-------|
| Name | bigcode/the-stack-dedup |
| Subset | Python (`data_dir="data/python"`) |
| Split | train |
| Size | ~12.96M files, ~49.7GB |
| Access | HuggingFace Hub (streaming) |
| License | Various permissive (The Stack terms) |
| Download Required | No (streaming mode) |

**Loading code:**
```python
from datasets import load_dataset
ds = load_dataset("bigcode/the-stack-dedup", data_dir="data/python",
                  streaming=True, split="train")
ds_shuffled = ds.shuffle(seed=42, buffer_size=10000)
```

### Baseline "Model" (Phase A only — pattern detection)
- Method: `">>>" in source_code`
- No download required
- Stdlib only: `str.contains`

### Proposed "Model" (Phase A + B + C — full execution gate)
- Method: AST extraction + subprocess doctest execution
- No download required
- Stdlib: `ast`, `doctest`, `subprocess`, `concurrent.futures`

---

## 5. Ablation Variants

| Phase | Description | Baseline? |
|-------|-------------|-----------|
| Phase A only | Pattern rate (fast screen) | Yes — "unfiltered" rate |
| Phase A + B | AST-parseable doctest rate | Intermediate |
| Phase A + B + C | Executable doctest rate | Proposed — primary metric |

All three rates are reported in results.json. The primary success criterion is Phase C rate.

---

## 6. Evaluation Metrics

### Primary Metrics (hypothesis-specific)
| Metric | Formula | Success Threshold |
|--------|---------|-------------------|
| `doctest_executable_rate` | n_executable / 10000 | ≥ 0.03 (3%) → PASS |
| `estimated_token_pool_M` | token_sum_executable / 1e6 | ≥ 500M → PASS |

### Secondary Metrics
| Metric | Formula | Purpose |
|--------|---------|---------|
| `doctest_pattern_rate` | n_pattern / 10000 | Baseline prevalence |
| `estimated_full_subset_executable_files` | n_exec/10000 * 12.96M | Scale estimate |

### Gate Decision Logic
```
IF doctest_executable_rate >= 0.03: PASS → proceed with 3-condition H-E1
IF doctest_executable_rate in [0.01, 0.03): SCOPE → reduce N, feasible
IF doctest_executable_rate < 0.01: PIVOT → 2-condition design
```

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0        # HuggingFace streaming loader
transformers>=4.35.0    # Qwen2.5-Coder tokenizer (optional for token counting)
matplotlib>=3.7.0       # Figure generation
numpy>=1.24.0           # Array operations
tqdm>=4.65.0            # Progress bars
pyyaml>=6.0             # YAML output
```

**All stdlib dependencies** (no install needed):
- `ast` — docstring extraction
- `doctest` — DocTestParser
- `subprocess` — isolated execution
- `concurrent.futures` — ProcessPoolExecutor
- `json` — results output
- `textwrap` — subprocess wrapper

### 7.2 External Repositories
- bigcode/the-stack-dedup — source corpus (no download, streaming only)

### 7.3 Hardware
- CPU: Any (no GPU required)
- RAM: ≥4GB (streaming, no full-dataset load)
- Estimated runtime: 2-4 hours for 10,000 files

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed=42 throughout
- Deterministic reservoir sampling
- Version-pinned dependencies

### NFR-2: Safety
- All doctest execution isolated in subprocess (no main process contamination)
- Hard timeout=5s per file prevents hanging
- UnicodeDecodeError handled gracefully (skip + log)
- `ImportError` in subprocess captured and counted as failure

### NFR-3: Observability
- Progress bar via tqdm during streaming
- Phase-level logs: Phase A complete, Phase C complete
- Final gate check printed clearly

### NFR-4: Output Completeness
- All 3 phase rates reported (not just the pass/fail)
- Per-file results available for debugging
- Figures saved for paper inclusion

---

## 9. Success Criteria

### Phase 3 (Implementation Planning) Success
- PRD covers all experiment phases (A, B, C)
- All baseline models documented (pattern-only and AST-only as ablations)
- Metrics section matches 02c_experiment_brief.md exactly
- Dependencies complete and accurate

### Phase 4 (Implementation) Success
- Scan script runs without crash on 10,000 files
- results.json written with all required fields
- All 3 phase rates reported
- Gate check printed

### Scientific Success
- `doctest_executable_rate` ≥ 3% → pipeline proceeds to H-E1 with 3 conditions
- Any result (including <1%) is actionable → no "fail" state for H-C1

---

## 10. File Structure

```
docs/youra_research/h-c1/
├── 02b_context.md              # Phase 2B context
├── 02c_experiment_brief.md     # Phase 2C experiment design (input)
├── 03_prd.md                   # This file
├── 03_architecture.md          # Architecture (Step 3 output)
├── 03_logic.md                 # Logic/API design (Step 5 output)
├── 03_config.md                # Configuration (Step 5 output)
├── 03_tasks.yaml               # Implementation tasks (Step 9 output)
├── results.json                # Scan results (Phase 4 output)
├── per_file_results.jsonl      # Per-file debug output (Phase 4)
└── figures/
    ├── gate_metrics_comparison.png
    ├── prevalence_breakdown.png
    ├── token_pool_estimate.png
    ├── error_type_distribution.png
    └── file_size_distribution.png
```

---

## 11. Traceability

| Requirement | Source |
|-------------|--------|
| 10k sample size | 02c_experiment_brief.md §Dataset; The Stack paper |
| seed=42 | 02c_experiment_brief.md §Training Protocol |
| 3% threshold | 02b_context.md §Success Criteria |
| AST + DocTestParser | 02c_experiment_brief.md §Proposed Model |
| subprocess isolation, 5s timeout | 02c_experiment_brief.md §FR-4 |
| 500M token target | Main hypothesis controlled variables |
| Quality filters | The Stack paper methodology |
| ProcessPoolExecutor 4 workers | 02c_experiment_brief.md §Training Protocol |

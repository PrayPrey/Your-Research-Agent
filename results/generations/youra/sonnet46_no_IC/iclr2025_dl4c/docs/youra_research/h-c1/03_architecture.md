---
hypothesis_id: "h-c1"
document_type: "Architecture"
phase: "Phase 3"
generated_at: "2026-08-04"
---

# Architecture: H-C1 — Doctest Prevalence Pilot Scanner

Applied: sequential-phase pipeline (The Stack paper methodology — no direct KB match)
Applied: subprocess isolation with timeout (stdlib subprocess.run pattern)

---

## 1. Executive Summary

Single-script observational pipeline. Streams 10,000 Python files from `bigcode/the-stack-dedup`, runs three sequential scan phases (pattern → AST → execution), writes `results.json` + `per_file_results.jsonl`, generates 5 figures, prints gate check.

No training. No model weights. Pure data characterization.

---

## 2. System Overview

```
HuggingFace Streaming
        |
   data_loader.py          # reservoir sampling + quality filters
        |
   scanner.py              # Phase A (pattern), Phase B (AST), Phase C (subprocess)
        |
   token_estimator.py      # word-count * 1.3 approximation
        |
   results.py              # aggregate dict → results.json + per_file_results.jsonl
        |
   visualize.py            # 5 matplotlib figures → figures/
        |
   gate.py                 # assertions + PASS/SCOPE/PIVOT print
```

All modules imported and orchestrated by `run_scan.py` (entry point).

---

## 3. File Structure

```
docs/youra_research/h-c1/
├── code/
│   ├── run_scan.py          # entry point / orchestrator
│   ├── data_loader.py       # dataset streaming + sampling
│   ├── scanner.py           # Phase A + B + C logic
│   ├── token_estimator.py   # token count approximation
│   ├── results.py           # JSON/JSONL output
│   ├── visualize.py         # 5 figures
│   └── gate.py              # gate check + assertions
├── results.json
├── per_file_results.jsonl
└── figures/
    ├── gate_metrics_comparison.png
    ├── prevalence_breakdown.png
    ├── token_pool_estimate.png
    ├── error_type_distribution.png
    └── file_size_distribution.png
```

---

## 4. Module Descriptions

### DataLoader (`code/data_loader.py`)

**Dependencies**: `datasets`

```python
def load_python_stream(seed: int = 42, buffer_size: int = 10000):
    """Returns shuffled HuggingFace IterableDataset for Python subset."""
    ...

def quality_filter(sample: dict) -> bool:
    """True if avg_line_len<=100, max_line_len<=1000, alphanum_frac>=0.25."""
    ...

def reservoir_sample(stream, n: int = 10000) -> list[dict]:
    """Returns exactly n samples passing quality_filter."""
    ...
```

---

### Scanner (`code/scanner.py`)

**Dependencies**: `ast`, `doctest`, `subprocess`, `concurrent.futures` (stdlib)

```python
def phase_a(source: str) -> bool:
    """True if '>>>' in source."""
    ...

def phase_b(source: str) -> bool:
    """True if AST parse yields >=1 doctest Example. Returns False on SyntaxError."""
    ...

def phase_c_worker(source: str, timeout: int = 5) -> dict:
    """Subprocess execution. Returns {'passed': bool, 'error_type': str|None}."""
    ...

def run_all_phases(
    samples: list[dict],
    n_workers: int = 4,
) -> list[dict]:
    """
    Runs Phase A+B sequentially per file, Phase C via ProcessPoolExecutor.
    Returns per-file result dicts.
    """
    ...
```

---

### TokenEstimator (`code/token_estimator.py`)

**Dependencies**: stdlib only (optional: `transformers`)

```python
def estimate_tokens(source: str) -> int:
    """len(source.split()) * 1.3 — fast word-count approximation."""
    ...

def sum_tokens(sources: list[str]) -> float:
    """Returns total estimated tokens across list of sources."""
    ...
```

---

### Results (`code/results.py`)

**Dependencies**: `json` (stdlib)

```python
RESULTS_SCHEMA = [
    "n_sampled", "n_pattern_positive", "n_ast_positive", "n_executable_positive",
    "doctest_pattern_rate", "doctest_ast_rate", "doctest_executable_rate",
    "estimated_full_subset_executable_files", "estimated_token_pool_M",
    "scan_duration_seconds", "seed", "dataset", "filter",
]

def build_aggregate(per_file: list[dict], duration: float) -> dict:
    """Computes all RESULTS_SCHEMA fields from per-file results."""
    ...

def write_json(aggregate: dict, path: str) -> None: ...
def write_jsonl(per_file: list[dict], path: str) -> None: ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: `matplotlib`, `numpy`

```python
def plot_gate_metrics(aggregate: dict, out_dir: str) -> None:
    """Bar chart: pattern_rate vs ast_rate vs executable_rate + 3% threshold line."""
    ...

def plot_prevalence_breakdown(aggregate: dict, out_dir: str) -> None:
    """Stacked bar: no-doctest / pattern-only / ast-only / executable."""
    ...

def plot_token_pool(aggregate: dict, out_dir: str) -> None:
    """Horizontal bar: estimated token pool vs 500M target."""
    ...

def plot_error_distribution(per_file: list[dict], out_dir: str) -> None:
    """Pie chart: timeout / exception / wrong_output / import_error."""
    ...

def plot_file_size_distribution(per_file: list[dict], out_dir: str) -> None:
    """Histogram: token counts, executable vs non-executable files."""
    ...

def generate_all(aggregate: dict, per_file: list[dict], out_dir: str) -> None:
    """Calls all five plot functions."""
    ...
```

---

### Gate (`code/gate.py`)

**Dependencies**: stdlib only

```python
def run_gate_check(aggregate: dict) -> str:
    """
    Asserts executable_rate <= pattern_rate, n_sampled == 10000.
    Prints GATE CHECK + STATUS line.
    Returns 'PASS' | 'SCOPE' | 'PIVOT'.
    """
    ...
```

---

### Orchestrator (`code/run_scan.py`)

**Dependencies**: all above modules

```python
def main() -> None:
    """
    1. load_python_stream + reservoir_sample (10k files)
    2. run_all_phases → per_file results
    3. sum_tokens for executable files
    4. build_aggregate + write_json + write_jsonl
    5. generate_all figures
    6. run_gate_check
    """
    ...

if __name__ == "__main__":
    main()
```

---

## 5. Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All modules implemented using Python stdlib (ast, doctest, subprocess, concurrent.futures, json) + datasets + matplotlib.

---

## 6. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data streaming & sampling | `data_loader.py`: HuggingFace streaming, quality filters, reservoir sampling to 10k files | 9 | 2+2+3+2 |
| E-2 | Phase A + B scanner | `scanner.py` phase_a (pattern) + phase_b (AST+DocTestParser), sequential per-file | 10 | 3+2+3+2 |
| E-3 | Phase C execution engine | `scanner.py` phase_c_worker + ProcessPoolExecutor(4), subprocess isolation, 5s timeout, error classification | 14 | 4+3+4+3 |
| E-4 | Token estimation & results output | `token_estimator.py` + `results.py`: aggregate stats, results.json, per_file_results.jsonl | 7 | 2+1+2+2 |
| E-5 | Visualization | `visualize.py`: 5 matplotlib figures saved to figures/ | 8 | 2+1+3+2 |
| E-6 | Gate check & orchestration | `gate.py` assertions + PASS/SCOPE/PIVOT; `run_scan.py` end-to-end wiring | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-3], Medium(9-13): [E-1, E-2], Low(4-8): [E-4, E-5, E-6]

**Total complexity**: 55 points across 6 epics.

---

## 7. Integration Points

| From | To | Data |
|------|----|------|
| `data_loader` | `scanner` | `list[dict]` with `"content"` field |
| `scanner` | `token_estimator` | `list[str]` source strings for executable files |
| `scanner` + `token_estimator` | `results` | per-file dicts + token sums |
| `results` | `visualize` | aggregate dict + per-file list |
| `results` | `gate` | aggregate dict |
| All | `run_scan` | orchestrated sequentially in `main()` |

**Output paths** (all relative to repo root):
- `docs/youra_research/h-c1/results.json`
- `docs/youra_research/h-c1/per_file_results.jsonl`
- `docs/youra_research/h-c1/figures/*.png`

**Parallelism boundary**: Phase C only. Phases A and B are single-threaded per-file loops inside `run_all_phases`. ProcessPoolExecutor is created once, submits only AST-positive files for execution.

**Safety constraint**: subprocess in `phase_c_worker` runs with `timeout=5`, `capture_output=True`. No file I/O from subprocess. Main process never `exec`s user code.

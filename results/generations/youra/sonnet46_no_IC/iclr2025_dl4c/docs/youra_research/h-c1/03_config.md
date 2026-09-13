---
hypothesis_id: "h-c1"
document_type: "Configuration"
phase: "Phase 3"
generated_at: "2026-08-04"
---

# Configuration: H-C1 — Doctest Prevalence Pilot Scanner

Applied: Standard Python dataclass (green-field, no direct KB pattern match)

---

## 1. Executive Summary

Single `ScanConfig` dataclass holding all fixed constants for the observational scanning pipeline. No hyperparameter tuning — all values are fixed by spec or The Stack paper methodology. No subtasks; config is fully defined in this document.

---

## 2. Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## 3. ScanConfig Dataclass

```python
from dataclasses import dataclass


@dataclass
class ScanConfig:
    """Fixed configuration for H-C1 doctest prevalence scanning pipeline.

    All values are fixed by spec. No hyperparameter search is performed.
    """

    # --- Dataset ---
    dataset: str = "bigcode/the-stack-dedup"
    data_dir: str = "data/python"
    split: str = "train"

    # --- Sampling ---
    seed: int = 42
    n_samples: int = 10_000
    buffer_size: int = 10_000

    # --- Quality filters (The Stack paper methodology) ---
    avg_line_len_max: int = 100       # chars; files with mean line len > this are dropped
    max_line_len_max: int = 1_000     # chars; files with any line > this are dropped
    alphanum_frac_min: float = 0.25   # fraction; files with fewer alphanumerics are dropped

    # --- Phase C execution ---
    timeout_sec: int = 5
    n_workers: int = 4

    # --- Token estimation ---
    token_ratio: float = 1.3          # word-count * ratio approximation (vs. full tokenizer)

    # --- Corpus scale ---
    full_python_subset_files: int = 12_960_052  # total files in bigcode/the-stack-dedup Python

    # --- Gate thresholds ---
    pass_threshold: float = 0.03      # executable_rate >= 3% → PASS
    scope_threshold: float = 0.01     # executable_rate >= 1% → SCOPE; < 1% → PIVOT

    # --- Output paths (relative to repo root) ---
    results_json: str = "docs/youra_research/h-c1/results.json"
    per_file_jsonl: str = "docs/youra_research/h-c1/per_file_results.jsonl"
    figures_dir: str = "docs/youra_research/h-c1/figures"
```

---

## 4. YAML Schema

Representation of `ScanConfig` as a YAML config file (for reference or future CLI override):

```yaml
# h-c1 scan configuration
dataset: "bigcode/the-stack-dedup"
data_dir: "data/python"
split: "train"

seed: 42
n_samples: 10000
buffer_size: 10000

# Quality filters — The Stack paper methodology
avg_line_len_max: 100
max_line_len_max: 1000
alphanum_frac_min: 0.25

# Phase C execution
timeout_sec: 5
n_workers: 4

# Token estimation
token_ratio: 1.3

# Corpus scale
full_python_subset_files: 12960052

# Gate thresholds
pass_threshold: 0.03
scope_threshold: 0.01

# Output paths
results_json: "docs/youra_research/h-c1/results.json"
per_file_jsonl: "docs/youra_research/h-c1/per_file_results.jsonl"
figures_dir: "docs/youra_research/h-c1/figures"
```

---

## 5. Quality Filter Constants

Source: The Stack paper (Kocetkov et al., 2022) quality filtering methodology.

| Filter | Field | Threshold | Direction |
|--------|-------|-----------|-----------|
| Average line length | `avg_line_len_max` | 100 chars | drop if mean > 100 |
| Maximum line length | `max_line_len_max` | 1000 chars | drop if any line > 1000 |
| Alphanumeric fraction | `alphanum_frac_min` | 0.25 | drop if fraction < 0.25 |

Applied in `data_loader.quality_filter(sample)` as a hard filter before reservoir sampling. Files failing any criterion are skipped entirely.

---

## 6. Gate Thresholds

Source: Phase 2B context + experiment brief (`02b_context.md`, `02c_experiment_brief.md`).

| Status | Condition | Downstream action |
|--------|-----------|-------------------|
| PASS | `doctest_executable_rate >= 0.03` | Proceed with 3-condition H-E1 |
| SCOPE | `0.01 <= doctest_executable_rate < 0.03` | Reduce N; feasible with smaller budget |
| PIVOT | `doctest_executable_rate < 0.01` | Fall back to 2-condition design (no doctest condition) |

**Justification**: 3% threshold derives from the 500M token budget requirement. At 3% of ~12.96M files (~388k files), with average ~1,300 tokens/file (word-count * 1.3), the estimated pool is ~504M tokens — just above the 500M target. The 1% SCOPE boundary represents the minimum viable corpus for a reduced-N experiment.

**Sanity assertion** (in `gate.py`):
- `doctest_executable_rate <= doctest_pattern_rate` (execution cannot exceed pattern prevalence)
- `n_sampled == 10_000`

---

## 7. Output Paths Configuration

All paths are relative to the repository root. The orchestrator (`run_scan.py`) passes these from `ScanConfig` to the relevant modules.

| Field | Path | Written by |
|-------|------|------------|
| `results_json` | `docs/youra_research/h-c1/results.json` | `results.write_json()` |
| `per_file_jsonl` | `docs/youra_research/h-c1/per_file_results.jsonl` | `results.write_jsonl()` |
| `figures_dir` | `docs/youra_research/h-c1/figures/` | `visualize.generate_all()` |

The `figures_dir` must exist before writing. `run_scan.py` should call `os.makedirs(cfg.figures_dir, exist_ok=True)` before invoking visualization.

---

## 8. Applied KB Patterns

Applied: Standard Python dataclass (stdlib `dataclasses`) — no direct KB pattern match; green-field pipeline config design.

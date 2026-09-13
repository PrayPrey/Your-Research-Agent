---
hypothesis_id: H-M2
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Config: H-M2 — Mypy Feedback Specificity

Applied: [INFERRED] dataclass config pattern (Archon MCP unavailable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: Config classes verified from h-m1/code/config.py (read directly — Serena MCP unavailable)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Config classes verified from actual h-m1 code:

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    k_max: int = 5
    benchmarks: list = field(default_factory=lambda: ["mbpp+", "humaneval+"])
    mypy_flags: list = field(default_factory=lambda: ["--ignore-missing-imports", "--no-strict-optional"])
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"
```

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation)

---

## A-5: Differential Analysis Config [Complexity: 9, Budget: 2 subtasks]

Applied: [INFERRED] single fixed config pattern

```python
@dataclass
class Config:
    # Inherited from H-M1 (field names verified from actual code)
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    k_max: int = 5
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0

    # H-M2 specific paths
    h_m1_results: str = "docs/youra_research/h-m1/results/humaneval_all_rounds.jsonl"
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"

    # Analysis parameters
    # Non-standard: k_eval=5 pins repair-rate evaluation to final round (matches k_max)
    k_eval: int = 5
    # Non-standard: gate_threshold=0.0 — any positive differential passes gate
    gate_threshold: float = 0.0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Analysis params | k_eval, gate_threshold defaults for repair_rate and compute_differential |
| C-5-2 | Path params | h_m1_results, results_dir, figures_dir for data loading and output |

---

## A-7: Integration run.py Config [Complexity: 10, Budget: 1 subtask]

Applied: [INFERRED] CLI argparse pattern

```python
# run.py CLI arguments — parsed via argparse, override Config defaults
# Usage: python run.py [--h-m1-results PATH] [--results-dir DIR] [--figures-dir DIR]
#                      [--benchmark {humaneval+,mbpp+,both}] [--smoke-test]

import argparse
from config import Config

def parse_args() -> Config:
    cfg = Config()
    p = argparse.ArgumentParser()
    p.add_argument("--h-m1-results", default=cfg.h_m1_results)
    p.add_argument("--results-dir", default=cfg.results_dir)
    p.add_argument("--figures-dir", default=cfg.figures_dir)
    # Non-standard: --benchmark allows partial run during development
    p.add_argument("--benchmark", choices=["humaneval+", "mbpp+", "both"], default="both")
    # Non-standard: --smoke-test limits to 2 problems for end-to-end verification
    p.add_argument("--smoke-test", action="store_true")
    args = p.parse_args()
    cfg.h_m1_results = args.h_m1_results
    cfg.results_dir = args.results_dir
    cfg.figures_dir = args.figures_dir
    return cfg, args.benchmark, args.smoke_test

# Output paths (derived from results_dir):
# {results_dir}/condition_a_humaneval.jsonl   — Condition A checkpoint
# {results_dir}/condition_a_mbpp.jsonl        — Condition A checkpoint
# {results_dir}/category_labels.json          — type/non_type assignments
# {results_dir}/summary.json                  — differential analysis results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | CLI + output paths | argparse wiring to Config, benchmark selection, smoke-test flag, output path conventions |

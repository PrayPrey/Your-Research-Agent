---
title: "Config: H-M4 — Feedback Overhead Efficiency Ratio Measurement"
hypothesis_id: H-M4
phase: 3
date: 2026-08-31
author: yoon303@etri.re.kr
---

# Config: H-M4

Applied: hardcoded-constants + dataclass-per-module pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded module-level constants + dataclasses for structured sub-configs

---

## Fixed Experiment Constants (`code/config.py`)

```python
# code/config.py
CATEGORIES = ['execution', 'static', 'type', 'smt']
MAX_ITERS = 3
SMT_TIMEOUT = 30.0
EXEC_TIMEOUT = 10.0
GENERATION_TEMP = 0.2
REPAIR_TEMP = 0.0
MAX_TOKENS = 1024
N_BOOTSTRAP = 10000
SEED = 1

FIGURES_DIR = "docs/youra_research/h-m4/figures"
RESULTS_PATH = "docs/youra_research/h-m4/results.json"
SUMMARY_PATH = "docs/youra_research/h-m4/summary.json"
CHECKPOINT_PATH = "docs/youra_research/h-m4/checkpoint.json"
```

---

## A-1: Data Loading Config [Complexity: 9, Budget: 1 subtask]

Applied: Standard PyTorch defaults / HuggingFace dataset load pattern

### C-1-1: Dataset Config Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class DatasetConfig:
    humaneval_hf_id: str = "openai/openai_humaneval"
    humaneval_split: str = "test"
    humaneval_n: int = 164

    mbpp_hf_id: str = "google-research-datasets/mbpp"
    mbpp_config: str = "sanitized"
    mbpp_split: str = "test"
    mbpp_problem_range: tuple[int, int] = (11, 510)  # inclusive; yields 374 problems
    mbpp_n: int = 374

    total_problems: int = 538  # humaneval_n + mbpp_n

    baseline_pass_path: str | None = None  # None triggers re-run of vanilla generation
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | DatasetConfig | HumanEval/MBPP identifiers, splits, MBPP problem range, baseline_pass path |

---

## A-3: Static/Type Verifier Config [Complexity: 10, Budget: 1 subtask]

Applied: Standard PyTorch defaults / subprocess harness pattern

### C-3-1: Pyright Config

```python
from dataclasses import dataclass

@dataclass
class PyrightConfig:
    command: list[str] = field(default_factory=lambda: ["pyright", "--outputjson"])
    # Non-standard: --outputjson enables machine-readable JSON parsing
    tmpfile_prefix: str = "h_m4_pyright_"
    per_file_timeout: float = 30.0  # seconds; matches SMT_TIMEOUT for consistency
```

Usage in verifier:
```python
import subprocess, tempfile, json
from code.config import PyrightConfig

def run_static_verifier(code: str, problem: dict) -> tuple[str, bool]:
    cfg = PyrightConfig()
    with tempfile.NamedTemporaryFile(
        prefix=cfg.tmpfile_prefix, suffix=".py", mode="w", delete=False
    ) as f:
        f.write(code)
        tmppath = f.name
    result = subprocess.run(
        cfg.command + [tmppath],
        capture_output=True, text=True,
        timeout=cfg.per_file_timeout
    )
    data = json.loads(result.stdout)
    errors = data.get("generalDiagnostics", [])
    passed = len(errors) == 0
    feedback = "\n".join(e.get("message", "") for e in errors) if errors else "No issues"
    return feedback, passed
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | PyrightConfig | Invocation command, output format flags, tmpfile prefix, per-file timeout |

---

## A-9: Visualization Config [Complexity: 12, Budget: 2 subtasks]

Applied: colorblind-friendly palette (Wong 2011, 8-color) for 4 category colors

### C-9-1: Figure Config Dataclass

```python
from dataclasses import dataclass, field

# Colorblind-friendly palette (Wong 2011) — 4 colors for 4 categories
# Order: execution, static, type, smt
CATEGORY_COLORS = {
    "execution": "#0072B2",  # blue
    "static":    "#E69F00",  # orange
    "type":      "#009E73",  # green
    "smt":       "#D55E00",  # vermillion
}

@dataclass
class FigureConfig:
    output_dir: str = "docs/youra_research/h-m4/figures"
    dpi: int = 300

    # Figure sizes (width, height) in inches per plot type
    fig_size_bar: tuple[float, float] = (8.0, 5.0)       # efficiency ratios bar chart
    fig_size_boxplot: tuple[float, float] = (10.0, 6.0)  # overhead boxplots
    fig_size_violin: tuple[float, float] = (10.0, 6.0)   # overhead violins
    fig_size_scatter: tuple[float, float] = (7.0, 7.0)   # efficiency scatter
    fig_size_heatmap: tuple[float, float] = (14.0, 8.0)  # 538×4 heatmap

    color_palette: dict[str, str] = field(default_factory=lambda: CATEGORY_COLORS)

    font_size_title: int = 14
    font_size_label: int = 12
    font_size_tick: int = 10
```

### C-9-2: Log-Scale Config for Overhead Plots

```python
@dataclass
class LogScaleConfig:
    # Non-standard: threshold below which linear scale is used instead of log
    log_transform_threshold: float = 1e-3  # seconds; overhead below this value use linear
    log_base: int = 10
    # Tick positions covering expected overhead range: 1ms to 30s
    tick_positions: list[float] = field(default_factory=lambda: [
        1e-3, 1e-2, 1e-1, 1.0, 10.0, 30.0
    ])
    tick_labels: list[str] = field(default_factory=lambda: [
        "1ms", "10ms", "100ms", "1s", "10s", "30s"
    ])
    heatmap_vmin: float = 1e-3   # log10 lower bound for heatmap color scale
    heatmap_vmax: float = 30.0   # log10 upper bound; matches SMT_TIMEOUT
```

Usage in visualize.py:
```python
import matplotlib.pyplot as plt
import numpy as np
from code.config import LogScaleConfig

def _apply_log_scale(ax, cfg: LogScaleConfig = LogScaleConfig()):
    ax.set_yscale("log", base=cfg.log_base)
    ax.set_yticks(cfg.tick_positions)
    ax.set_yticklabels(cfg.tick_labels)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | FigureConfig | Output dir, DPI, figure sizes per plot type, colorblind-friendly palette for 4 categories |
| C-9-2 | LogScaleConfig | Log-transform threshold, tick positions/labels for overhead plots, heatmap bounds |

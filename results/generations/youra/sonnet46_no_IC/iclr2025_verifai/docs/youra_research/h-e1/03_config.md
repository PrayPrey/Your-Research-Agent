---
title: "Config: H-E1 Pylint/Mypy Iterative Repair PoC"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: 3
date: "2026-08-05"
status: complete
---

# Configuration: H-E1

Applied: Standard argparse CLI pattern (stdlib, no YAML)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: argparse for CLI; hardcoded dict for figure specs

---

## C-6-1: CLI Arguments Schema [Complexity: 6, Budget: 1]

### Configuration (argparse)

```python
import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: Pylint/Mypy iterative repair PoC on HumanEval + MBPP"
    )

    # --- Model ---
    parser.add_argument(
        "--model",
        type=str,
        default="llama-3.1-8b-instant",
        help="Groq model name (default: llama-3.1-8b-instant)",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="groq",
        choices=["groq", "hf"],
        help="Inference backend: 'groq' (API) or 'hf' (local HuggingFace)",
    )

    # --- Experiment knobs ---
    parser.add_argument(
        "--token-budget",
        type=int,
        default=1000,
        help="Total output token budget B per problem (default: 1000)",
    )
    parser.add_argument(
        "--max-repair-rounds",
        type=int,
        default=3,
        help="Maximum pylint repair rounds per problem (default: 3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )

    # --- I/O ---
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/",
        help="Directory for JSONL and metrics output (default: results/)",
    )
    parser.add_argument(
        "--figures-dir",
        type=str,
        default="docs/youra_research/h-e1/figures/",
        help="Directory for figure PNG output",
    )

    # --- Dataset / condition selection ---
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=["humaneval", "mbpp"],
        choices=["humaneval", "mbpp"],
        help="Which datasets to evaluate (default: both)",
    )
    parser.add_argument(
        "--conditions",
        type=str,
        nargs="+",
        default=["baseline", "pylint"],
        choices=["baseline", "pylint"],
        help="Which conditions to run (default: both)",
    )

    # --- Runtime ---
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Skip already-completed problems (default: True)",
    )
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Re-run all problems (disables resume)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )

    args = parser.parse_args()

    # Validation
    if args.token_budget <= 0:
        parser.error("--token-budget must be > 0")
    if not (1 <= args.max_repair_rounds <= 5):
        parser.error("--max-repair-rounds must be in [1, 5]")

    return args
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | CLI Arguments Schema | argparse setup for run_experiment.py |

### Usage Example

```bash
# Full run (default)
python experiments/h-e1/run_experiment.py

# Custom budget, resume off
python experiments/h-e1/run_experiment.py \
  --token-budget 2000 \
  --max-repair-rounds 5 \
  --no-resume \
  --output-dir /tmp/results/

# Baseline only on HumanEval
python experiments/h-e1/run_experiment.py \
  --datasets humaneval \
  --conditions baseline
```

---

## C-6-2: Figure Configuration [Complexity: 6, Budget: 1]

### Configuration (hardcoded dict)

```python
import matplotlib as mpl

# Global rcParams — set once at visualizer module import
FIGURE_RC = {
    "figure.figsize": (8, 5),
    "figure.dpi": 150,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
}

# Figure 1: pass@1 bar chart (4 bars: baseline/pylint × HE/MBPP)
FIG1_CONFIG = {
    "filename": "figure1_pass_at_1_comparison.png",
    "title": "Pass@1: Baseline vs Pylint Repair (Llama 3.1 8B)",
    "ylabel": "Pass@1",
    "ylim": (0.0, 1.0),
    "bars": [
        {"label": "Baseline HumanEval", "color": "#4C72B0", "key": "pass@1_baseline_he"},
        {"label": "Pylint HumanEval",   "color": "#55A868", "key": "pass@1_pylint_he"},
        {"label": "Baseline MBPP",      "color": "#C44E52", "key": "pass@1_baseline_mbpp"},
        {"label": "Pylint MBPP",        "color": "#8172B2", "key": "pass@1_pylint_mbpp"},
    ],
    # Non-standard: ylim fixed at (0,1) so delta is visually comparable across runs
}

# Figure 2: per-round pass@1 line plot (rounds 0-3)
FIG2_CONFIG = {
    "filename": "figure2_per_round_trajectory.png",
    "title": "Per-Round Pass@1 Trajectory (Pylint Condition)",
    "xlabel": "Repair Round",
    "ylabel": "Pass@1",
    "xticks": [0, 1, 2, 3],
    "lines": [
        {"label": "HumanEval", "color": "#4C72B0", "marker": "o", "key": "per_round_pass@1_he"},
        {"label": "MBPP",      "color": "#C44E52", "marker": "s", "key": "per_round_pass@1_mbpp"},
    ],
}

# Figure 3: token budget histogram
FIG3_CONFIG = {
    "filename": "figure3_token_budget_distribution.png",
    "title": "Token Budget Distribution per Problem",
    "xlabel": "Total Output Tokens Used",
    "ylabel": "Number of Problems",
    "bins": 20,
    "color": "#4C72B0",
    "alpha": 0.75,
    # Non-standard: bins=20 chosen for 538 problems; adjust if distribution is very skewed
}

# Figure 4: pylint coverage stacked bar
FIG4_CONFIG = {
    "filename": "figure4_pylint_coverage_analysis.png",
    "title": "Pylint Coverage of Baseline Failures",
    "xlabel": "Benchmark",
    "ylabel": "Fraction of Baseline Failures",
    "categories": [
        {"label": "Error",      "color": "#C44E52", "key": "error"},
        {"label": "Warning",    "color": "#DD8452", "key": "warning"},
        {"label": "Convention", "color": "#8172B2", "key": "convention"},
        {"label": "Not Flagged","color": "#CCCCCC", "key": "none"},
    ],
    "xtick_labels": ["HumanEval", "MBPP"],
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-2 | Figure Configuration | matplotlib rcParams + per-figure spec dicts |

### Usage Example

```python
# In visualizer.py — apply rcParams once at top of file
import matplotlib as mpl
import matplotlib.pyplot as plt
from config import FIGURE_RC, FIG1_CONFIG, FIG2_CONFIG, FIG3_CONFIG, FIG4_CONFIG

mpl.rcParams.update(FIGURE_RC)

def plot_pass_at_1_comparison(metrics: dict, out_dir: str) -> None:
    fig, ax = plt.subplots()
    cfg = FIG1_CONFIG
    for i, bar in enumerate(cfg["bars"]):
        ax.bar(i, metrics[bar["key"]], color=bar["color"], label=bar["label"])
    ax.set_ylim(*cfg["ylim"])
    ax.set_title(cfg["title"])
    ax.set_ylabel(cfg["ylabel"])
    ax.set_xticks(range(len(cfg["bars"])))
    ax.set_xticklabels([b["label"] for b in cfg["bars"]], rotation=15, ha="right")
    ax.legend()
    fig.savefig(f"{out_dir}/{cfg['filename']}")
    plt.close(fig)
```

---

## Summary

| Subtask | Format | Key Defaults |
|---------|--------|--------------|
| C-6-1 | argparse | model=llama-3.1-8b-instant, B=1000, rounds=3, seed=42 |
| C-6-2 | hardcoded dict | figsize=(8,5), dpi=150, 4 seaborn-palette colors |

**Validation rules enforced in parse_args():**
- `token_budget > 0`
- `max_repair_rounds in [1, 5]`
- `backend in {"groq", "hf"}`
- `datasets subset of {"humaneval", "mbpp"}`
- `conditions subset of {"baseline", "pylint"}`

# Configuration: H-E1 — Difficulty-Tier Sample Size Viability Check

**Hypothesis:** H-E1 (EXISTENCE, MUST_WORK gate)
**Tier:** LIGHT (argparse + hardcoded constants, no YAML, no WandB)
**Date:** 2026-03-18

Applied: Standard argparse CLI pattern (no domain-specific EvalPlus config patterns in Archon KB; using established EvalPlus/HuggingFace API defaults)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze (architecture doc confirms only .md files exist in h-e1/)
**Config Files Found:** None — new config design
**Pattern Used:** hardcoded constants at module top + argparse overrides (LIGHT tier standard)

---

## A-3: EvalPlus Evaluation [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard EvalPlus oracle defaults from evalplus/evalplus official API documentation

### Configuration

```python
# evaluate_solutions.py — top-level constants

# EvalPlus oracle resource limits (from evalplus official defaults)
EVALPLUS_PARAMS = dict(
    max_as_limit=30,       # MB address space limit per test
    max_data_limit=30,     # MB data segment limit per test
    max_stack_limit=10,    # MB stack limit per test
    min_time_limit=1,      # seconds minimum per test case
    gt_time_limit_factor=4.0,  # multiplier over ground-truth time
)

# Gate criterion
COVERAGE_MIN = 0.95  # fraction of problems requiring valid EvalPlus evaluation

# Smoke test size (used with --smoke_test flag)
N_SMOKE = 5  # evaluate only first 5 problems per benchmark

# Output file naming patterns
# solutions_{model_short}.jsonl   — generated solutions
# correctness_{model_short}.json  — {task_id: [bool x k]}
# pass_at_1_{model_short}.json    — {task_id: float}
# tier_statistics.csv             — model, benchmark, n_hard, n_easy, n_medium, n_total, coverage_rate, gate_pass
MODEL_SHORT_NAMES = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}
```

### Argparse flags for `evaluate_solutions.py`

```python
def parse_args():
    parser = argparse.ArgumentParser(description="EvalPlus correctness evaluation")
    parser.add_argument("--solutions_path", type=str, required=True,
                        help="Path to solutions JSONL file")
    parser.add_argument("--output_dir", type=str, default="h-e1/results",
                        help="Directory to write correctness JSON output")
    parser.add_argument("--smoke_test", action="store_true",
                        help=f"Evaluate only first {N_SMOKE} problems per benchmark")
    return parser.parse_args()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | EvalPlus oracle config | EVALPLUS_PARAMS dict, COVERAGE_MIN, N_SMOKE, output file naming |
| C-3-2 | evaluate_solutions argparse | --solutions_path, --output_dir, --smoke_test flags |

---

## A-5: Visualization [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard matplotlib publication defaults

### Configuration

```python
# visualize.py — top-level constants

# Figure settings
FIG_DPI = 150
FIG_SIZE_BAR = (10, 5)      # tier_sizes_bar.png, coverage_rate.png
FIG_SIZE_HIST = (12, 4)     # pass_at_1_distribution.png (3 subplots)
FIG_SIZE_HEATMAP = (8, 4)   # tier_size_heatmap.png

# Color scheme
COLOR_HARD = "#d62728"      # red — hard tier
COLOR_EASY = "#2ca02c"      # green — easy tier
COLOR_MEDIUM = "#aec7e8"    # light blue — medium tier
COLOR_THRESHOLD = "#ff7f0e" # orange — n=20 threshold line
COLOR_COVERAGE = "#1f77b4"  # blue — coverage bars
CMAP_HEATMAP = "YlOrRd"     # heatmap colormap

# Gate threshold line
MIN_N_LINE = 20             # horizontal reference line in tier_sizes_bar.png

# Figure output dir
FIGURES_DIR = "h-e1/figures"
```

### Argparse flags for `visualize.py`

```python
def parse_args():
    parser = argparse.ArgumentParser(description="Generate H-E1 figures")
    parser.add_argument("--results_dir", type=str, default="h-e1/results",
                        help="Directory containing tier_statistics.csv and pass_at_1_*.json")
    parser.add_argument("--figures_dir", type=str, default=FIGURES_DIR,
                        help="Output directory for PNG figures")
    return parser.parse_args()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Visualization settings | DPI, figure sizes, color scheme, argparse for visualize.py |

---

## Shared Constants (run_experiment.py)

These constants are defined in `run_experiment.py` and imported/passed to submodules.

```python
# run_experiment.py — top-level constants

import torch

# Models
MODEL_IDS = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

# Generation
K = 5
SEED = 42
TEMPERATURE = 0.8
TOP_P = 0.95
MAX_NEW_TOKENS = 512
DTYPE = torch.float16

# Tier thresholds
HARD_THRESHOLD = 0.0
EASY_THRESHOLD = 0.6
RELAXED_HARD_THRESHOLD = 0.2  # fallback if primary gate fails
MIN_N = 20

# Gate criterion (coverage)
COVERAGE_MIN = 0.95
N_SMOKE = 5
```

### Argparse flags for `run_experiment.py`

```python
def parse_args():
    parser = argparse.ArgumentParser(description="H-E1 full pipeline")
    parser.add_argument("--output_dir", type=str, default="h-e1/results",
                        help="Directory for all outputs")
    parser.add_argument("--figures_dir", type=str, default="h-e1/figures",
                        help="Directory for figure outputs")
    parser.add_argument("--smoke_test", action="store_true",
                        help="Run on first 5 problems only (quick sanity check)")
    parser.add_argument("--skip_generation", action="store_true",
                        help="Skip generation if solutions JSONL already exists")
    parser.add_argument("--gpu_id", type=str, default="0",
                        help="CUDA_VISIBLE_DEVICES value (single GPU)")
    parser.add_argument("--hard_threshold", type=float, default=HARD_THRESHOLD,
                        help="pass@1 threshold for hard tier (default: 0.0)")
    parser.add_argument("--easy_threshold", type=float, default=EASY_THRESHOLD,
                        help="pass@1 threshold for easy tier (default: 0.6)")
    return parser.parse_args()
```

---

## Requirements

```
# requirements.txt
python>=3.9
torch>=2.0
transformers>=4.35
evalplus>=0.3.0
numpy>=1.24
matplotlib>=3.7
pandas>=2.0
```

---

## Self-Validation

- [x] ONE format only — hardcoded constants (LIGHT tier, no dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values — none needed (all standard defaults)
- [x] Subtask count within budget (3 total: 2 for A-3, 1 for A-5)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field: Serena skip acceptable (noted)

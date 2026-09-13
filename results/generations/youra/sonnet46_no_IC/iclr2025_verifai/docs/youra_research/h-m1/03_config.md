---
title: "Config: H-M1 Execution Test Feedback Iterative Repair — Mechanism Comparison"
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: 3
date: "2026-08-05"
status: complete
---

# Configuration: H-M1

Applied: Standard argparse CLI pattern (stdlib, inherited from H-E1)
Applied: Hardcoded dict for figure specs (inherited from H-E1 visualizer pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: H-E1 config verified from `experiments/h-e1/config.py` and `experiments/h-e1/model_client.py`
**Config Files Found**: `experiments/h-e1/config.py`, `experiments/h-e1/model_client.py`
**Pattern Used**: Module-level constants (config.py) + argparse CLI + hardcoded dict for figures

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-E1 Code)

```python
# From: experiments/h-e1/config.py (ACTUAL CODE — verified)
MODEL_ID: str = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS: int = 512
TEMPERATURE: float = 0.0
DO_SAMPLE: bool = False
TIMEOUT_SECONDS: float = 10.0          # H-M1 overrides to 15.0
RESULTS_DIR: str = "results/h-e1"
FIGURES_DIR: str = "docs/youra_research/h-e1/figures"

# From: experiments/h-e1/model_client.py (ACTUAL CODE — verified)
# ModelClient.__init__(model: str = "llama-3.1-8b-instant", api_key: str | None = None, backend: str = "auto")
# generate(prompt: str, max_tokens: int = 1000) -> tuple[str, int]
# temperature=0.0, seed=42 — hardcoded in _generate_groq()
# HF path: max_new_tokens=min(max_tokens, 512), do_sample=False
```

**Verified from**: `experiments/h-e1/` (actual implementation)

**Override in H-M1**: `TIMEOUT_SECONDS` increases from 10.0 → 15.0 (execution sandbox needs more time for test suites).

---

## M-5 Subtasks (2): Replication Model Configuration

### C-5-1: ReplicationConfig [Complexity: 10, Budget: 1]

Applied: Standard argparse CLI pattern (stdlib, no YAML)

```python
# experiments/h-m1/config.py

# --- Primary model (Llama) ---
LLAMA_MODEL_ID: str = "llama-3.1-8b-instant"      # Groq model name
LLAMA_BACKEND: str = "groq"

# --- Replication model (Qwen) ---
QWEN_MODEL_ID: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
QWEN_BACKEND: str = "hf"

# --- Generation (shared, greedy) ---
TEMPERATURE: float = 0.0        # greedy decoding — Arimbur 2026
SEED: int = 42
MAX_TOKENS: int = 1000          # token budget B per problem

# --- Repair loop ---
TOKEN_BUDGET: int = 1000        # B: total output tokens per problem
MAX_REPAIR_ROUNDS: int = 3      # max rounds of execution feedback
MIN_REMAINING_TOKENS: int = 50  # stop if budget almost exhausted
SANDBOX_TIMEOUT: float = 15.0   # seconds; Johin2/iterative-code-repair

# --- Paths ---
RESULTS_DIR: str = "results/h-m1"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"
H_E1_RESULTS_DIR: str = "results/h-e1"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ReplicationConfig | Module-level constants for Llama + Qwen model settings and repair loop knobs |

---

### C-5-2: YAML Schema for --run-replication Mode [Complexity: 10, Budget: 1]

The CLI is implemented with argparse (matching H-E1 pattern). The `--run-replication` flag drives Qwen execution.

```python
# experiments/h-m1/run_experiment.py — argparse schema for replication mode

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-M1: Execution test feedback vs pylint repair — mechanism comparison"
    )

    # --- Model (primary) ---
    parser.add_argument("--model", type=str, default="llama-3.1-8b-instant",
                        help="Primary model name (Groq: llama-3.1-8b-instant)")
    parser.add_argument("--backend", type=str, default="groq", choices=["groq", "hf"])

    # --- Replication ---
    parser.add_argument("--run-replication", action="store_true", default=False,
                        help="Also run Qwen2.5-Coder-7B-Instruct as replication model")
    parser.add_argument("--replication-model", type=str,
                        default="Qwen/Qwen2.5-Coder-7B-Instruct",
                        help="HF model ID for replication run")
    parser.add_argument("--replication-backend", type=str, default="hf",
                        choices=["groq", "hf"])

    # --- Experiment knobs ---
    parser.add_argument("--token-budget", type=int, default=1000,
                        help="Token budget B per problem (default: 1000)")
    parser.add_argument("--max-repair-rounds", type=int, default=3,
                        help="Max execution repair rounds (default: 3)")
    parser.add_argument("--seed", type=int, default=42)

    # --- H-E1 reuse ---
    parser.add_argument("--reuse-h-e1-results", action="store_true", default=True)
    parser.add_argument("--no-reuse-h-e1-results", dest="reuse_h_e1_results",
                        action="store_false")
    parser.add_argument("--h-e1-results-dir", type=str, default="results/h-e1")

    # --- I/O ---
    parser.add_argument("--output-dir", type=str, default="results/h-m1")
    parser.add_argument("--figures-dir", type=str,
                        default="docs/youra_research/h-m1/figures")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--pilot-only", action="store_true", default=False,
                        help="Run verify_mechanism() on 20 problems then exit")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()
    if args.token_budget <= 0:
        parser.error("--token-budget must be > 0")
    if not (1 <= args.max_repair_rounds <= 5):
        parser.error("--max-repair-rounds must be in [1, 5]")
    return args
```

Output file naming convention (used in `run_execution_condition()`):

```python
# Model tag derived from model name — used in output filenames
def model_tag(model_id: str) -> str:
    if "qwen" in model_id.lower():
        return "qwen"
    if "llama" in model_id.lower():
        return "llama"
    return model_id.split("/")[-1].lower().replace("-", "_")

# Output files follow pattern: {condition}_{benchmark}_{model_tag}.jsonl
# Examples:
#   execution_humaneval_llama.jsonl
#   execution_mbpp_qwen.jsonl
#   round_results_humaneval_llama.json
#   round_results_mbpp_qwen.json
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-2 | YAML/argparse replication schema | argparse schema for --run-replication, output naming convention |

---

## M-7 Subtasks (2): Metric Configuration

### C-7-1: MetricsConfig [Complexity: 11, Budget: 1]

Applied: Standard argparse CLI pattern (stdlib, no YAML)

```python
# experiments/h-m1/config.py (append to module-level constants)

# --- Statistical tests ---
MCNEMAR_ALPHA: float = 0.05             # pre-specified significance level
N_BOOTSTRAP: int = 10000               # bootstrap resamples for CI
EXACT_MCNEMAR_THRESHOLD: int = 25      # use binomial exact if n_discordant < 25
CI_LEVEL: float = 0.95                 # confidence interval level

# --- Gate ---
GATE_ALPHA: float = 0.05               # must have p < GATE_ALPHA on both benchmarks
# Gate passes if: pvalue < GATE_ALPHA AND exec_only > pylint_only (both HE + MBPP)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | MetricsConfig | Statistical test constants: alpha, bootstrap N, exact threshold |

---

### C-7-2: metrics.json Output Schema [Complexity: 11, Budget: 1]

```python
# Full field specification for metrics.json — produced by compute_metrics()
# All float fields are in [0.0, 1.0] unless noted; int fields are counts.

METRICS_JSON_SCHEMA = {
    # Pass@1 — fraction of problems passed
    "pass@1_baseline_he":      float,   # [0.0, 1.0]  baseline on HumanEval
    "pass@1_baseline_mbpp":    float,   # [0.0, 1.0]
    "pass@1_pylint_he":        float,   # [0.0, 1.0]
    "pass@1_pylint_mbpp":      float,   # [0.0, 1.0]
    "pass@1_exec_llama_he":    float,   # [0.0, 1.0]  execution condition, Llama
    "pass@1_exec_llama_mbpp":  float,   # [0.0, 1.0]
    "pass@1_exec_qwen_he":     float,   # [0.0, 1.0]  execution condition, Qwen
    "pass@1_exec_qwen_mbpp":   float,   # [0.0, 1.0]

    # Deltas (vs baseline)
    "delta_pylint_he":         float,   # [-1.0, 1.0]
    "delta_pylint_mbpp":       float,
    "delta_exec_llama_he":     float,
    "delta_exec_llama_mbpp":   float,
    "delta_exec_qwen_he":      float,
    "delta_exec_qwen_mbpp":    float,

    # Bootstrap CIs on (delta_exec - delta_pylint)
    "ci_lower_llama_he":       float,   # 95% CI lower bound
    "ci_upper_llama_he":       float,
    "ci_lower_llama_mbpp":     float,
    "ci_upper_llama_mbpp":     float,
    "ci_lower_qwen_he":        float,
    "ci_upper_qwen_he":        float,
    "ci_lower_qwen_mbpp":      float,
    "ci_upper_qwen_mbpp":      float,

    # McNemar test results — one block per (benchmark × model)
    "mcnemar_llama_he": {
        "table":        list,           # [[a,b],[c,d]] int 2x2
        "n_discordant": int,            # b+c
        "exec_only":    int,            # b (exec pass, pylint fail)
        "pylint_only":  int,            # c (pylint pass, exec fail)
        "statistic":    float,
        "pvalue":       float,          # [0.0, 1.0]
        "exact":        bool,           # True if n_discordant < 25
        "significant":  bool,           # pvalue < 0.05
        "direction":    str,            # "exec_better" | "pylint_better" | "no_difference"
    },
    "mcnemar_llama_mbpp": "same structure as mcnemar_llama_he",
    "mcnemar_qwen_he":    "same structure",
    "mcnemar_qwen_mbpp":  "same structure",

    # Gate
    "gate_passed":  bool,
    "gate_reason":  str,                # human-readable explanation

    # Metadata
    "n_humaneval":  int,                # 164
    "n_mbpp":       int,                # 374
    "token_budget": int,                # 1000
    "max_repair_rounds": int,           # 3
    "mcnemar_alpha": float,             # 0.05
    "n_bootstrap":  int,                # 10000
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-2 | metrics.json schema | Full field specification with types and expected ranges |

---

## M-8 Subtasks (2): Visualization Configuration

### C-8-1: VizConfig [Complexity: 13, Budget: 1]

Applied: Hardcoded dict for figure specs (inherited from H-E1 visualizer pattern)

```python
# experiments/h-m1/visualizer.py — top of file

import matplotlib as mpl

# Global rcParams — apply once at module import (inherited from H-E1)
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

mpl.rcParams.update(FIGURE_RC)

# Which figures to generate (set False to skip)
FIGURES_TO_GENERATE = {
    "figure1_delta_comparison":     True,   # MANDATORY
    "figure2_per_round_trajectory": True,   # MANDATORY
    "figure3_replication_comparison": True,
    "figure4_token_budget_distribution": True,
    "figure5_error_type_analysis":  True,
}

# Output format — PNG for quick review, PDF for paper submission
OUTPUT_FORMAT: str = "png"   # "png" | "pdf"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | VizConfig | FIGURE_RC rcParams, output format, figures-to-generate toggle |

---

### C-8-2: Figure-Specific Configs [Complexity: 13, Budget: 1]

```python
# experiments/h-m1/visualizer.py — figure spec dicts

# Figure 1: delta bar chart (exec vs pylint, HE vs MBPP, with CI + p-value)
FIG1_CONFIG = {
    "filename": "figure1_delta_comparison.png",
    "title": "Pass@1 Delta vs Baseline: Execution vs Pylint Repair (Llama 3.1 8B)",
    "ylabel": "Δ Pass@1 (vs Baseline)",
    "ylim": (-0.1, 0.4),
    "bar_width": 0.35,
    "bars": [
        {"label": "Δ Pylint HumanEval",   "color": "#4C72B0",
         "delta_key": "delta_pylint_he",   "ci_keys": None},
        {"label": "Δ Exec HumanEval",     "color": "#55A868",
         "delta_key": "delta_exec_llama_he",
         "ci_keys": ("ci_lower_llama_he", "ci_upper_llama_he")},
        {"label": "Δ Pylint MBPP",        "color": "#C44E52",
         "delta_key": "delta_pylint_mbpp", "ci_keys": None},
        {"label": "Δ Exec MBPP",          "color": "#8172B2",
         "delta_key": "delta_exec_llama_mbpp",
         "ci_keys": ("ci_lower_llama_mbpp", "ci_upper_llama_mbpp")},
    ],
    # p-value annotation position: above the taller bar in each benchmark pair
    "pvalue_annotation": {
        "he":   {"mcnemar_key": "mcnemar_llama_he",   "y_offset": 0.02},
        "mbpp": {"mcnemar_key": "mcnemar_llama_mbpp", "y_offset": 0.02},
    },
    # Non-standard: ylim bottom at -0.1 to show if execution repair regresses
}

# Figure 2: per-round pass@1 trajectory (exec vs pylint, rounds 0-3)
FIG2_CONFIG = {
    "filename": "figure2_per_round_trajectory.png",
    "title": "Per-Round Pass@1 Trajectory: Execution vs Pylint Repair",
    "xlabel": "Repair Round",
    "ylabel": "Pass@1",
    "xticks": [0, 1, 2, 3],
    "lines": [
        {"label": "Exec HumanEval",   "color": "#55A868", "marker": "o",
         "linestyle": "-",  "key": "per_round_exec_he"},
        {"label": "Pylint HumanEval", "color": "#4C72B0", "marker": "o",
         "linestyle": "--", "key": "per_round_pylint_he"},
        {"label": "Exec MBPP",        "color": "#8172B2", "marker": "s",
         "linestyle": "-",  "key": "per_round_exec_mbpp"},
        {"label": "Pylint MBPP",      "color": "#C44E52", "marker": "s",
         "linestyle": "--", "key": "per_round_pylint_mbpp"},
    ],
    # Non-standard: solid=exec, dashed=pylint — consistent across figures
}

# Figure 3: replication comparison (Llama vs Qwen delta, side by side)
FIG3_CONFIG = {
    "filename": "figure3_replication_comparison.png",
    "title": "Replication: Δ Pass@1 Execution Repair — Llama vs Qwen",
    "ylabel": "Δ Pass@1 (vs Baseline)",
    "ylim": (-0.1, 0.4),
    "bar_width": 0.35,
    "layout": "grouped",   # grouped bars: [Llama HE, Qwen HE, Llama MBPP, Qwen MBPP]
    "bars": [
        {"label": "Llama HumanEval", "color": "#55A868",
         "delta_key": "delta_exec_llama_he"},
        {"label": "Qwen HumanEval",  "color": "#4C72B0",
         "delta_key": "delta_exec_qwen_he"},
        {"label": "Llama MBPP",      "color": "#8172B2",
         "delta_key": "delta_exec_llama_mbpp"},
        {"label": "Qwen MBPP",       "color": "#C44E52",
         "delta_key": "delta_exec_qwen_mbpp"},
    ],
}

# Figure 4: token budget histogram
FIG4_CONFIG = {
    "filename": "figure4_token_budget_distribution.png",
    "title": "Token Budget Usage per Problem (Execution Condition)",
    "xlabel": "Total Output Tokens Used",
    "ylabel": "Number of Problems",
    "bins": 20,
    "color": "#4C72B0",
    "alpha": 0.75,
    "vline_budget": 1000,   # vertical line at B=1000 to show ceiling
}

# Figure 5: error type analysis
FIG5_CONFIG = {
    "filename": "figure5_error_type_analysis.png",
    "title": "Error Type Distribution and Repair Success Rate",
    "xlabel": "Error Type",
    "ylabel_bars": "Count",
    "ylabel_line": "Repair Success Rate",
    "color_bars": "#4C72B0",
    "color_line": "#C44E52",
    "alpha": 0.75,
    # error types from subprocess stderr: SyntaxError, TypeError, NameError,
    # AttributeError, AssertionError, TimeoutError, Other
    "error_types": [
        "SyntaxError", "TypeError", "NameError",
        "AttributeError", "AssertionError", "TimeoutError", "Other",
    ],
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-2 | Figure-specific configs | FIG1-5 spec dicts: bar widths, CI format, p-value annotation, line styles, markers |

---

## Summary

| Subtask | Format | Key Defaults |
|---------|--------|--------------|
| C-5-1 | module constants | llama-3.1-8b-instant/groq, qwen/hf, B=1000, rounds=3, timeout=15s, seed=42 |
| C-5-2 | argparse | --run-replication flag, model_tag() naming, --reuse-h-e1-results=True |
| C-7-1 | module constants | alpha=0.05, n_bootstrap=10000, exact_threshold=25, ci_level=0.95 |
| C-7-2 | dict schema | 8 pass@1 fields, 6 delta fields, 8 CI fields, 4 McNemar blocks, gate |
| C-8-1 | hardcoded dict | figsize=(8,5), dpi=150, OUTPUT_FORMAT="png", all 5 figures enabled |
| C-8-2 | hardcoded dict | bar_width=0.35, CI error bars on exec bars, solid=exec/dashed=pylint |

**Validation rules enforced in parse_args():**
- `token_budget > 0`
- `max_repair_rounds in [1, 5]`
- `backend in {"groq", "hf"}`

**H-E1 overrides:**
- `TIMEOUT_SECONDS`: 10.0 → 15.0 (execution sandbox needs more time for test suite evaluation)
- `RESULTS_DIR`: "results/h-e1" → "results/h-m1"
- `FIGURES_DIR`: "docs/youra_research/h-e1/figures" → "docs/youra_research/h-m1/figures"

# Config: h-m3 — P(True) Confidence Elicitation via Logprob Extraction

**Hypothesis ID:** h-m3
**Type:** MECHANISM (MUST_WORK) — inference-only, no training

Applied: inference-only constants + dataclass sub-config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config verified from actual h-m2 code via direct file read (Serena project activation unavailable for absolute path; Read tool used as fallback)
**Config Files Found**: No config.py in h-m2 — constants defined in `h-m2/code/src/h_m2/stratify.py`
**Pattern Used**: Module-level constants (matching h-m2 style); dataclasses for structured sub-configs (A-7, A-3, A-8, A-9, A-10)

---

## Inherited Configuration (Base Hypothesis)

### Constants Verified from h-m2 Actual Code

```python
# From: h-m2/code/src/h_m2/stratify.py (ACTUAL CODE)
MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0   # inherited from h-m2
EASY_THRESHOLD: float = 0.6   # inherited from h-m2
```

**Verified from**: `/home/anonymous/YouRA_results_new_4/TEST_verifiai/docs/youra_research/20260316_verifia/h-m2/code/src/h_m2/stratify.py`

---

## A-7: Gate Evaluation [Complexity: 10, Budget: 2 subtasks]

Applied: Standard inference-only constants pattern

### Configuration

```python
# src/h_m3/config.py — Gate section
STD_GATE_THRESHOLD: float = 0.05

VERIFIED_RESULTS_SCHEMA_VERSION: str = "FR-10.1"

GATE_SCHEMA: dict = {
    "schema_version": VERIFIED_RESULTS_SCHEMA_VERSION,
    "hypothesis_id": "h-m3",
    "gate": {
        "type": "MUST_WORK",
        "condition": "std(c) > 0.05 for ALL 3 models",
        "satisfied": None,  # filled at runtime
    },
    "models": {
        short: {
            "std_c": None,
            "mean_c": None,
            "n_pairs": None,
            "gate_pass": None,
        }
        for short in MODEL_SHORT_NAMES.values()
    },
}

VERIFIED_RESULTS_FILENAME: str = "ptrue_hm3_verified.json"
CONFIDENCE_SCORES_FILENAME: str = "ptrue_confidence_scores.json"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Gate metrics config | STD_GATE_THRESHOLD, GATE_SCHEMA template, output filenames |
| C-7-2 | FR-10 JSON schema | VERIFIED_RESULTS_SCHEMA_VERSION, per-model schema fields |

---

## A-3: Model Loader [Complexity: 9, Budget: 2 subtasks]

Applied: Standard inference-only constants pattern

### Configuration

```python
# src/h_m3/config.py — Model loading section
from dataclasses import dataclass

@dataclass
class ModelLoadConfig:
    torch_dtype: str = "float16"       # matches h-m1/h-m2 float16 convention
    device_map: str = "auto"
    max_new_tokens: int = 1            # extract first token logit only
    do_sample: bool = False            # greedy decoding
    seed: int = 42
    true_token: str = " True"          # leading space for tokenizer
    false_token: str = " False"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ModelLoadConfig dataclass | torch_dtype, device_map, do_sample, seed |
| C-3-2 | Token IDs config | true_token, false_token strings for tokenizer lookup |

---

## A-8: Secondary Metrics [Complexity: 9, Budget: 2 subtasks]

Applied: Standard inference-only constants pattern

### Configuration

```python
# src/h_m3/config.py — Secondary metrics section
from dataclasses import dataclass

@dataclass
class MetricsConfig:
    histogram_bins: int = 20           # FR-6: 20-bin histogram
    expected_mean_c_low: float = 0.57  # Run 3 prior lower bound
    expected_mean_c_high: float = 0.91 # Run 3 prior upper bound
    expected_c_range_min: float = 0.2  # secondary check: min c in distribution
    expected_c_range_max: float = 0.9  # secondary check: max c in distribution
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | MetricsConfig dataclass | histogram_bins, expected range bounds |
| C-8-2 | Secondary check thresholds | expected_mean_c bounds, c range validation values |

---

## A-9: Visualization [Complexity: 9, Budget: 1 subtask]

Applied: Standard inference-only constants pattern

### Configuration

```python
# src/h_m3/config.py — Visualization section
from dataclasses import dataclass

@dataclass
class FigureConfig:
    figures_dir: str = "figures"
    fig1_filename: str = "fig1_gate_check.png"
    fig2_filename: str = "fig2_c_histograms.png"
    fig3_filename: str = "fig3_c_vs_pass_at_1.png"
    fig4_filename: str = "fig4_c_by_tier.png"
    fig5_filename: str = "fig5_c_cdf.png"
    dpi: int = 150
    histogram_bins: int = 20           # shared with MetricsConfig
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | FigureConfig dataclass | output directory, filenames for 5 figures, dpi |

---

## A-10: CLI Orchestrator [Complexity: 10, Budget: 1 subtask]

Applied: Standard argparse schema pattern (matching h-m2 run_hm2_stratification.py style)

### Configuration

```python
# src/h_m3/config.py — CLI defaults section
DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
DEFAULT_HM2_RESULTS: str = "../../h-m2/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

# CLI argument schema (used in parse_args()):
# --hm1_results_dir   str   default=DEFAULT_HM1_RESULTS
# --hm2_results_dir   str   default=DEFAULT_HM2_RESULTS
# --output_dir        str   default=DEFAULT_OUTPUT_DIR
# --figures_dir       str   default=DEFAULT_FIGURES_DIR
# --device            str   default="cuda"
# --smoke_test        bool  action="store_true"  (2 problems × 1 solution per model)
# --fallback_prompt   bool  action="store_true"  (force FR-9 fallback prompt)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | CLI argparse schema | default paths, device, smoke_test flag, fallback_prompt flag |

---

## Complete config.py Reference

```python
# src/h_m3/config.py — all constants and dataclasses
from __future__ import annotations
from dataclasses import dataclass

# ── Inherited from h-m2 (verified from actual stratify.py) ──────────────────

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6

# ── h-m3 specific constants ──────────────────────────────────────────────────

STD_GATE_THRESHOLD: float = 0.05
MAX_NEW_TOKENS: int = 1
SEED: int = 42
CHECKPOINT_INTERVAL: int = 100

PTRUE_PROMPT_TEMPLATE: str = (
    "{problem_description}\n\n```python\n{solution_code}\n```\n\n"
    "Is this solution correct? Answer True or False.\nAnswer:"
)

PTRUE_PROMPT_FALLBACK: str = (
    "{problem_description}\n\n```python\n{solution_code}\n```\n\n"
    "Does this solution pass all tests? Answer True or False.\nAnswer:"
)

CONFIDENCE_SCORES_FILENAME: str = "ptrue_confidence_scores.json"
VERIFIED_RESULTS_FILENAME: str = "ptrue_hm3_verified.json"
VERIFIED_RESULTS_SCHEMA_VERSION: str = "FR-10.1"

DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
DEFAULT_HM2_RESULTS: str = "../../h-m2/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class ModelLoadConfig:
    torch_dtype: str = "float16"
    device_map: str = "auto"
    max_new_tokens: int = 1
    do_sample: bool = False
    seed: int = 42
    true_token: str = " True"
    false_token: str = " False"


@dataclass
class MetricsConfig:
    histogram_bins: int = 20
    expected_mean_c_low: float = 0.57
    expected_mean_c_high: float = 0.91
    expected_c_range_min: float = 0.2
    expected_c_range_max: float = 0.9


@dataclass
class FigureConfig:
    figures_dir: str = "figures"
    fig1_filename: str = "fig1_gate_check.png"
    fig2_filename: str = "fig2_c_histograms.png"
    fig3_filename: str = "fig3_c_vs_pass_at_1.png"
    fig4_filename: str = "fig4_c_by_tier.png"
    fig5_filename: str = "fig5_c_cdf.png"
    dpi: int = 150
    histogram_bins: int = 20
```

---

## Subtask Budget Summary

| Epic | Complexity | Subtasks Used | Subtasks Budget |
|------|-----------|--------------|-----------------|
| A-7 (Gate Evaluation) | 10 | 2 | 2 |
| A-3 (Model Loader) | 9 | 2 | 2 |
| A-8 (Secondary Metrics) | 9 | 2 | 2 |
| A-9 (Visualization) | 9 | 1 | 1 |
| A-10 (CLI Orchestrator) | 10 | 1 | 1 |
| **Total** | | **8** | **8** |

# Config: h-m4
# RLEF-Fraction Monotonic Difficulty Scaling + 1.3B Scale Sanity Check

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: dataclass-config pattern (verified from h-e1/code/config.py)
Applied: sys.path injection for cross-hypothesis imports (from h-m3/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-e1 + h-m3)
**Status**: config classes verified from base code (Glob + Read used; Serena MCP unavailable)
**Config Files Found**: `h-e1/code/config.py`, `h-m3/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

Verified from `h-e1/code/config.py` (actual implementation):

```python
# h-e1 field names (VERIFIED — use these exactly):
TrainingConfig:  lr, batch_size, grad_accum, epochs, max_length, max_new_tokens,
                 seed, precision, grad_clip, warmup_steps, lr_schedule
GRPOConfig:      num_generations, beta, temperature_rollout
RewardConfig:    timeout, temperature_eval
BootstrapConfig: n_boot, seed, ci_level, gate_ratio
PathsConfig:     checkpoints_dir, results_dir, logs_dir, figures_dir
ExperimentConfig: model_name, fallback_model_name, ceiling_check_threshold
```

h-m3 adds: `n_bootstrap`, `bootstrap_seed`, `num_epochs` (vs h-e1's `epochs`), `max_steps`, `apps_n_samples`

---

## A-1: Config + Setup [Complexity: 5, Budget: 1 subtask]

Applied: flat dataclass inheriting h-e1 field naming conventions

### C-A1-1: H_M4_Config

```python
# code/config.py
import sys
from dataclasses import dataclass, field
from pathlib import Path

H_E1_CODE = Path(__file__).parents[3] / "h-e1" / "code"
if str(H_E1_CODE) not in sys.path:
    sys.path.insert(0, str(H_E1_CODE))

H_M4_ROOT = Path(__file__).parents[3] / "h-m4"

@dataclass
class SFT1B3Config:
    """1.3B SFT training — new compute track."""
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-base"
    lr: float = 2e-5           # Non-standard: higher than 7B (1e-5) due to smaller capacity
    batch_size: int = 8        # Non-standard: larger than 7B (4) — 1.3B fits more in VRAM
    grad_accum: int = 4        # effective batch = 32
    epochs: int = 3
    max_length: int = 2048
    max_new_tokens: int = 512
    seed: int = 1              # Non-standard: matches h-e1 seed=1 for reproducibility
    precision: str = "bfloat16"
    warmup_ratio: float = 0.1
    lr_schedule: str = "cosine"
    grad_clip: float = 1.0
    # GRPO (same as h-e1 GRPOConfig)
    num_generations: int = 8
    beta: float = 0.04
    temperature_rollout: float = 0.8


@dataclass
class JTTestConfig:
    """Jonckheere-Terpstra test settings for 7B re-analysis."""
    alpha: float = 0.05        # significance threshold
    alternative: str = "increasing"
    n_boot: int = 1000         # bootstrap CI for JT statistic
    seed: int = 42


@dataclass
class GateConfig:
    """Pass/fail gates for both computation tracks."""
    # Primary gate: 7B JT test
    jt_p_threshold: float = 0.05
    jt_z_min: float = 0.0     # Z > 0 required (positive trend direction)
    # Secondary gate: 1.3B delta ratio
    delta_ratio_min: float = 1.0   # delta_LCB / delta_HumanEval >= 1.0
    # Null result path label
    null_result_action: str = "EXPLORE"


@dataclass
class PathsConfig:
    """Output paths (inherits naming from h-e1 PathsConfig)."""
    he1_results_path: str = str(H_E1_CODE / "results" / "h-e1" / "experiment_results.json")
    he1_validation_md: str = str(H_E1_CODE.parents[1] / "04_validation.md")
    checkpoints_dir: str = str(H_M4_ROOT / "code" / "checkpoints")
    results_dir: str = str(H_M4_ROOT / "results")
    figures_dir: str = str(H_M4_ROOT / "figures")
    logs_dir: str = str(H_M4_ROOT / "code" / "logs")


@dataclass
class H_M4_Config:
    sft_1b3: SFT1B3Config = field(default_factory=SFT1B3Config)
    jt: JTTestConfig = field(default_factory=JTTestConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    # 7B track — loaded from h-e1, no training
    benchmarks_ordered: tuple = (
        "humaneval", "mbpp", "lcb_easy", "lcb_medium", "lcb_hard"
    )  # difficulty order: easy → hard
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A1-1 | H_M4_Config | Full config dataclass covering both computation tracks |

---

## A-8: Visualization [Complexity: 10, Budget: 2 subtasks]

Applied: figure config pattern from h-m3/compare.py (generate_figures reference)

### C-A8-1: FigureConfig

```python
@dataclass
class FigureConfig:
    dpi: int = 150
    fig_width: float = 8.0
    fig_height: float = 5.0
    output_dir: str = str(H_M4_ROOT / "figures")
    output_format: str = "png"
    # Color palette for two models (7B and 1.3B)
    color_7b: str = "#2196F3"
    color_1b3: str = "#FF5722"
    color_trend: str = "#4CAF50"   # monotonic trend line
    # Required figure filenames
    fig1_name: str = "fig1_7b_delta_by_difficulty.png"
    fig2_name: str = "fig2_jt_test_result.png"
    fig3_name: str = "fig3_1b3_delta_by_difficulty.png"
    fig4_name: str = "fig4_delta_ratio_gate.png"
```

### C-A8-2: Figure Generation YAML

```yaml
# figures/figure_config.yaml — copy-paste for Phase 4
figure:
  dpi: 150
  width: 8.0
  height: 5.0
  format: png
  output_dir: figures/

colors:
  model_7b: "#2196F3"
  model_1b3: "#FF5722"
  trend_line: "#4CAF50"
  gate_pass: "#4CAF50"
  gate_fail: "#F44336"

x_axis:
  label: "Benchmark (difficulty order)"
  ticks: ["HumanEval", "MBPP", "LCB-Easy", "LCB-Medium", "LCB-Hard"]

y_axis:
  label: "Δ pass@1 (RLEF-Fraction − SFT)"

figures:
  - id: fig1
    filename: fig1_7b_delta_by_difficulty.png
    title: "7B: Δ(RLEF-Fraction, SFT) by Difficulty"
    data_key: delta_7b
  - id: fig2
    filename: fig2_jt_test_result.png
    title: "JT Test: Trend Significance"
    data_key: jt_result
  - id: fig3
    filename: fig3_1b3_delta_by_difficulty.png
    title: "1.3B: Δ(RLEF-Fraction, SFT) by Difficulty"
    data_key: delta_1b3
  - id: fig4
    filename: fig4_delta_ratio_gate.png
    title: "1.3B Delta Ratio Gate (LCB-Hard / HumanEval)"
    data_key: delta_ratio
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A8-1 | FigureConfig | Dataclass for figure sizes, DPI, colors, output paths |
| C-A8-2 | figure_config.yaml | YAML for figure generation parameters |

---

## A-9: Orchestration [Complexity: 9, Budget: 2 subtasks]

Applied: results schema pattern from h-m3/compare.py (save_results_csv reference)

### C-A9-1: ResultsSchema

```python
@dataclass
class DeltaValues:
    """Δ(RLEF-Fraction, SFT) per benchmark. Non-null required for gate check."""
    humaneval: float = float("nan")
    mbpp: float = float("nan")
    lcb_easy: float = float("nan")
    lcb_medium: float = float("nan")
    lcb_hard: float = float("nan")


@dataclass
class JTResult:
    statistic: float = float("nan")
    p_value: float = float("nan")
    z_score: float = float("nan")
    trend_direction: str = "unknown"   # "increasing" | "decreasing" | "none"
    gate_pass: bool = False


@dataclass
class GateResult:
    jt_gate_pass: bool = False         # p < 0.05 AND Z > 0
    delta_ratio: float = float("nan")  # delta_lcb_hard / delta_humaneval
    delta_ratio_gate_pass: bool = False
    overall_pass: bool = False
    null_result_action: str = "EXPLORE"


@dataclass
class ResultsSchema:
    """Full experiment results — covers both 7B and 1.3B tracks."""
    hypothesis: str = "h-m4"
    date: str = ""
    # 7B track (re-analysis of h-e1)
    delta_7b: DeltaValues = field(default_factory=DeltaValues)
    jt_result_7b: JTResult = field(default_factory=JTResult)
    # 1.3B track (new training)
    delta_1b3: DeltaValues = field(default_factory=DeltaValues)
    jt_result_1b3: JTResult = field(default_factory=JTResult)
    delta_ratio_1b3: float = float("nan")
    # Final gate
    gate: GateResult = field(default_factory=GateResult)
    notes: str = ""
```

YAML output format (results/experiment_results.json equivalent):

```yaml
# results/h-m4_results.yaml — output schema example
hypothesis: h-m4
date: "2026-08-26"

delta_7b:
  humaneval: 0.0      # fill from h-e1
  mbpp: 0.0
  lcb_easy: 0.0
  lcb_medium: 0.0
  lcb_hard: 0.0

jt_result_7b:
  statistic: 0.0
  p_value: 1.0
  z_score: 0.0
  trend_direction: unknown
  gate_pass: false

delta_1b3:
  humaneval: 0.0
  mbpp: 0.0
  lcb_easy: 0.0
  lcb_medium: 0.0
  lcb_hard: 0.0

jt_result_1b3:
  statistic: 0.0
  p_value: 1.0
  z_score: 0.0
  trend_direction: unknown
  gate_pass: false

delta_ratio_1b3: 0.0   # lcb_hard_delta / humaneval_delta

gate:
  jt_gate_pass: false
  delta_ratio: 0.0
  delta_ratio_gate_pass: false
  overall_pass: false
  null_result_action: EXPLORE

notes: ""
```

### C-A9-2: GateConfig (Full Specification)

```python
# GateConfig — already in H_M4_Config above; full logic reference:

GATE_LOGIC = {
    # Primary gate: 7B JT test
    "primary": {
        "condition": "jt_p_value < 0.05 AND jt_z_score > 0.0",
        "pass_action": "check_secondary_gate",
        "fail_action": "EXPLORE",
        "fail_label": "null_result_monotonicity_not_confirmed",
    },
    # Secondary gate: 1.3B delta ratio
    "secondary": {
        "condition": "delta_ratio >= 1.0",  # delta_lcb_hard / delta_humaneval
        "pass_action": "SHOULD_WORK_CONFIRMED",
        "fail_action": "PARTIAL",
        "fail_label": "1b3_scale_sanity_failed",
    },
    # Null result reporting
    "null_result_report": [
        "descriptive trend statistics (mean delta per difficulty)",
        "JT statistic and p-value",
        "comparison to h-m3 null result context",
        "hypothesis: binary vs difficulty-dependent improvement",
    ],
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-A9-1 | ResultsSchema | Dataclass + YAML schema for both 7B and 1.3B tracks |
| C-A9-2 | GateConfig | Threshold values, gate conditions, null-result handling |

---

## Complete YAML Config (Copy-Paste Ready)

```yaml
# h-m4/config.yaml — full experiment config for Phase 4 Coder

hypothesis: h-m4

paths:
  he1_results_path: "docs/youra_research/h-e1/code/results/h-e1/experiment_results.json"
  he1_validation_md: "docs/youra_research/h-e1/04_validation.md"
  checkpoints_dir: "docs/youra_research/h-m4/code/checkpoints"
  results_dir: "docs/youra_research/h-m4/results"
  figures_dir: "docs/youra_research/h-m4/figures"
  logs_dir: "docs/youra_research/h-m4/code/logs"

benchmarks_ordered:
  - humaneval
  - mbpp
  - lcb_easy
  - lcb_medium
  - lcb_hard

sft_1b3:
  model_name: "deepseek-ai/deepseek-coder-1.3b-base"
  lr: 2e-5
  batch_size: 8
  grad_accum: 4
  epochs: 3
  max_length: 2048
  max_new_tokens: 512
  seed: 1
  precision: bfloat16
  warmup_ratio: 0.1
  lr_schedule: cosine
  grad_clip: 1.0
  num_generations: 8
  beta: 0.04
  temperature_rollout: 0.8

jt_test:
  alpha: 0.05
  alternative: increasing
  n_boot: 1000
  seed: 42

gate:
  jt_p_threshold: 0.05
  jt_z_min: 0.0
  delta_ratio_min: 1.0
  null_result_action: EXPLORE

figure:
  dpi: 150
  fig_width: 8.0
  fig_height: 5.0
  output_format: png
  color_7b: "#2196F3"
  color_1b3: "#FF5722"
  color_trend: "#4CAF50"
```

---

## Summary

| Subtask | Config Class | Key Fields |
|---------|-------------|------------|
| C-A1-1 | H_M4_Config | SFT1B3Config, JTTestConfig, GateConfig, PathsConfig |
| C-A8-1 | FigureConfig | dpi, fig_width, colors, output paths |
| C-A8-2 | figure_config.yaml | YAML figure generation params |
| C-A9-1 | ResultsSchema | DeltaValues, JTResult, GateResult for both tracks |
| C-A9-2 | GATE_LOGIC dict | Threshold values, pass/fail actions, null path |

**Total subtasks: 5/5 budget used.**
**All field names verified against h-e1/code/config.py and h-m3/code/config.py.**

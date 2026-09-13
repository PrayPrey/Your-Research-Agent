---
hypothesis_id: H-M3
hypothesis_type: MECHANISM
date: 2026-08-20
author: yoon303b@gmail.com
phase: 3-config
---

# Config: H-M3 Panel OLS Regression

Applied: no relevant KB patterns (similarity 0.36–0.38, unrelated content)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-m2/code/config.py` (module-level constants, no dataclass)
**Pattern Used**: module-level constants dict (H-M2 style) — H-M3 extends same pattern

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-M2 Code)

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE — verified)
MODEL_SIZES: list[str] = ["70m", "1b", "6.9b"]          # ← H-M3 expands to 16
MODEL_IDS: dict[str, str] = {                             # ← H-M3 adds 13 more
    "70m": "EleutherAI/pythia-70m",
    "1b": "EleutherAI/pythia-1b",
    "6.9b": "EleutherAI/pythia-6.9b",
}
CHECKPOINT_STEPS: list[int] = [0,1,2,...,143000]         # len=154, identical in H-M3
PILE_DOMAINS: list[str] = [...]                           # len=22, identical in H-M3
FOCAL_DOMAINS: dict[str, str] = {"wikipedia": "Wikipedia (en)", "books": "Books3"}
TASKS: dict[str, dict] = {
    "mmlu": {"num_fewshot": 5, "metric": "acc,none"},
    "hellaswag": {"num_fewshot": 10, "metric": "acc_norm,none"},
}
BATCH_SIZE: str = "auto"
DTYPE: str = "float"
FLOOR_THRESHOLD: float = 0.20   # ← H-M3 raises to 0.30 (all-benchmark check)
MIN_VALID_CHECKPOINTS: int = 100
SEED: int = 42
H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"
RESULTS_DIR: str = "results/h-m2"
EVAL_CACHE_DIR: str = "results/h-m2/eval_cache"
FIGURES_DIR: str = "docs/youra_research/h-m2/figures"
```

**Verified from**: `docs/youra_research/h-m2/code/config.py` (actual implementation, no dataclass — flat module constants)

---

## A-2: DataLoader Extension [Complexity: 7, Budget: 1 subtask]

### A-2-1: `DataConfig`

```python
# config.py (H-M3) — extend H-M2 constants inline, no separate dataclass needed
H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1/"
N_MODEL_SIZES: int = 16
N_CHECKPOINTS: int = 154
N_DOMAINS: int = 22
BOOKS3_VARIANCE_THRESHOLD: float = 1e-6
CHECKPOINT_STEPS: list[int] = [
    0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    *range(1000, 144000, 1000),
]  # len=154, identical to H-M2
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | DataConfig constants | Extend H-M2 data loader config: add N_MODEL_SIZES=16, N_CHECKPOINTS=154, BOOKS3_VARIANCE_THRESHOLD=1e-6 |

---

## A-3: Evaluator Extension [Complexity: 8, Budget: 1 subtask]

### A-3-1: `EvaluationConfig`

```python
# Extends H-M2 TASKS + adds arc_challenge, winogrande
TASKS: dict[str, dict] = {
    "mmlu":          {"num_fewshot": 5,  "metric": "acc,none"},
    "hellaswag":     {"num_fewshot": 10, "metric": "acc_norm,none"},
    "arc_challenge": {"num_fewshot": 25, "metric": "acc_norm,none"},
    "winogrande":    {"num_fewshot": 5,  "metric": "acc,none"},
}
BATCH_SIZE: str = "auto"          # inherited from H-M2
DTYPE: str = "float"              # inherited from H-M2
EXISTING_CACHE_PATH: str = "pythia/evals/pythia-v1/"
EVAL_CACHE_DIR: str = "results/h-m3/eval_cache"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | EvaluationConfig extension | Add arc_challenge (25-shot) + winogrande (5-shot) to TASKS; add EXISTING_CACHE_PATH |

---

## A-4: Panel Builder [Complexity: 13, Budget: 2 subtasks]

### A-4-1: `PanelConfig`

```python
@dataclass
class PanelConfig:
    floor_threshold: float = 0.30          # non-standard: H-M2 used 0.20 for 70m; H-M3 all-benchmark check at 0.30
    vif_threshold: float = 10.0
    pca_variance_retained: float = 0.95
    min_checkpoints_per_model: int = 100
    dropped_domain: str = "Unknown"        # placeholder; runtime-determined (min variance domain)
    multiindex_levels: list[str] = field(default_factory=lambda: ["model_size", "checkpoint"])
```

### A-4-2: Panel Construction YAML Schema

```yaml
# panel_schema.yaml — documentation only, not loaded at runtime
panel_df:
  multiindex:
    entity: model_size    # 16 levels
    time: checkpoint      # 154 steps -> >=100 after floor filter
  columns:
    domain_fractions:     # 21 cols (22 - 1 dropped for sum constraint)
      source: PILE_DOMAINS minus dropped_domain
      dtype: float64
    benchmark_scores:     # 4 cols
      - mmlu
      - hellaswag
      - arc_challenge
      - winogrande
      dtype: float64
    covariates:
      - log_params        # log10(parameter_count), dtype: float64

vif_decision:
  step1: compute VIF for all 21 domain cols
  step2:
    if_max_vif_le_10: proceed with raw domain cols
    if_max_vif_gt_10: apply PCA(n_components=0.95); use components as regressors
  output: vif_diagnostics.json
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | PanelConfig dataclass | Define PanelConfig with floor/VIF/PCA thresholds |
| C-4-2 | Panel YAML schema | Document panel_df column spec and VIF decision tree |

---

## A-8: Visualization [Complexity: 10, Budget: 2 subtasks]

### A-8-1: `VisualizationConfig`

```python
@dataclass
class VisualizationConfig:
    dpi: int = 300
    figsize_default: tuple[int, int] = (10, 6)
    palette: str = "colorblind"    # seaborn colorblind-safe
    ci_alpha: float = 0.95
    figure_paths: dict[str, str] = field(default_factory=lambda: {
        "fig1": "fig1_gate_metrics_comparison.png",
        "fig2": "fig2_domain_coefficient_heatmap.png",
        "fig3": "fig3_directional_scatter.png",
        "fig4": "fig4_r2_decomposition.png",
        "fig5": "fig5_permutation_null.png",
        "fig6": "fig6_subgroup_robustness.png",
    })
```

### A-8-2: Figure Specs

```python
FIGURE_SPECS: dict[str, dict] = {
    "fig1": {
        "type": "bar",
        "description": "beta_wiki + beta_books per benchmark",
        "groups": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "series": ["Wikipedia (en)", "Books3"],
        "error_bars": "95% CI from clustered SE",
        "figsize": (12, 6),
    },
    "fig2": {
        "type": "heatmap",
        "description": "22 domains x 4 benchmarks, color = beta magnitude",
        "rows": "domain_cols",      # 21 or PCA components
        "cols": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "figsize": (14, 10),
    },
    "fig3": {
        "type": "scatter",
        "description": "beta_wiki vs beta_books per benchmark with diagonal",
        "x": "beta_Wikipedia",
        "y": "beta_Books3",
        "hue": "benchmark",
        "figsize": (8, 8),
    },
    "fig4": {
        "type": "bar",
        "description": "R2_within: domain-only, scale-only, full per benchmark",
        "series": ["domain_only", "scale_only", "full"],
        "figsize": (10, 6),
    },
    "fig5": {
        "type": "histogram",
        "description": "permuted |beta_wiki - beta_books| null vs observed (P1 and P2)",
        "n_bins": 50,
        "panels": ["mmlu", "hellaswag"],
        "figsize": (12, 5),
    },
    "fig6": {
        "type": "bar",
        "description": "beta_wiki + beta_books: small (70m-410m) vs large (1b-12b) subgroups",
        "groups": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "series": ["small_wiki", "small_books", "large_wiki", "large_books"],
        "figsize": (14, 6),
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | VisualizationConfig dataclass | DPI, figsize, palette, CI alpha, figure_paths mapping |
| C-8-2 | FIGURE_SPECS dict | Per-figure type, axes, series, figsize for all 6 figures |

---

## A-10: Orchestrator [Complexity: 12, Budget: 2 subtasks]

### A-10-1: `ExperimentConfig`

```python
@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M3"
    base_hypothesis: str = "H-M2"
    output_dir: str = "results/h-m3"
    figures_dir: str = "docs/youra_research/h-m3/figures"
    seed: int = 42
    n_permutations: int = 1000
    benchmarks: list[str] = field(default_factory=lambda: [
        "mmlu", "hellaswag", "arc_challenge", "winogrande"
    ])
    focal_domains: list[str] = field(default_factory=lambda: [
        "Wikipedia (en)", "Books3"
    ])
    model_sizes: list[str] = field(default_factory=lambda: [
        "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
        "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
        "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
    ])
    small_sizes: list[str] = field(default_factory=lambda: [
        "70m", "160m", "410m",
        "70m-deduped", "160m-deduped", "410m-deduped",
    ])
    large_sizes: list[str] = field(default_factory=lambda: [
        "1b", "1.4b", "2.8b", "6.9b", "12b",
        "1b-deduped", "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
    ])
    resume: bool = True
```

### A-10-2: argparse CLI + YAML Override Schema

```python
# run_experiment.py argparse interface
import argparse

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="H-M3 Panel OLS Experiment")
    p.add_argument("--config",          type=str,   default=None,    help="YAML config override file")
    p.add_argument("--output-dir",      type=str,   default=None)
    p.add_argument("--seed",            type=int,   default=None)
    p.add_argument("--n-permutations",  type=int,   default=None)
    p.add_argument("--no-resume",       action="store_true",         help="Ignore existing cache")
    p.add_argument("--skip-eval",       action="store_true",         help="Skip lm-eval; use cache only")
    p.add_argument("--skip-robustness", action="store_true",         help="Skip permutation null (fast run)")
    p.add_argument("--model-sizes",     nargs="+",  default=None,    help="Subset of model sizes to run")
    return p
```

```yaml
# config_override.yaml — optional YAML override format
hypothesis_id: H-M3
output_dir: results/h-m3
seed: 42
n_permutations: 1000
resume: true
model_sizes:            # omit to use all 16
  - 70m
  - 1b
  - 6.9b
benchmarks:
  - mmlu
  - hellaswag
  - arc_challenge
  - winogrande
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | ExperimentConfig dataclass | Top-level experiment config: IDs, paths, seed, benchmarks, model_sizes, subgroup splits |
| C-10-2 | argparse + YAML schema | CLI interface with override flags; YAML config file format |

---

## Complete `config.py` for H-M3

```python
# docs/youra_research/h-m3/code/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

# --- Inherited from H-M2 (verified from actual code) ---
CHECKPOINT_STEPS: list[int] = [
    0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    *range(1000, 144000, 1000),
]  # len=154

PILE_DOMAINS: list[str] = [
    "Pile-CC", "PubMed Central", "Books3", "OpenWebText2", "ArXiv",
    "Github", "FreeLaw", "StackExchange", "USPTO Backgrounds",
    "PubMed Abstracts", "Gutenberg (PG-19)", "OpenSubtitles",
    "Wikipedia (en)", "DM Mathematics", "Ubuntu IRC", "BookCorpus2",
    "EuroParl", "HackerNews", "YoutubeSubtitles", "PhilPapers",
    "NIH ExPorter", "Enron Emails",
]  # len=22

FOCAL_DOMAINS: dict[str, str] = {
    "wikipedia": "Wikipedia (en)",
    "books": "Books3",
}

BATCH_SIZE: str = "auto"
DTYPE: str = "float"
NGRAM_SIZE: int = 13
CONTAMINATION_DELTA_THRESHOLD: float = 0.03
SEED: int = 42

# --- Extended from H-M2 ---
MODEL_SIZES: list[str] = [
    "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
    "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
    "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
]

MODEL_IDS: dict[str, str] = {
    "70m":           "EleutherAI/pythia-70m",
    "160m":          "EleutherAI/pythia-160m",
    "410m":          "EleutherAI/pythia-410m",
    "1b":            "EleutherAI/pythia-1b",
    "1.4b":          "EleutherAI/pythia-1.4b",
    "2.8b":          "EleutherAI/pythia-2.8b",
    "6.9b":          "EleutherAI/pythia-6.9b",
    "12b":           "EleutherAI/pythia-12b",
    "70m-deduped":   "EleutherAI/pythia-70m-deduped",
    "160m-deduped":  "EleutherAI/pythia-160m-deduped",
    "410m-deduped":  "EleutherAI/pythia-410m-deduped",
    "1b-deduped":    "EleutherAI/pythia-1b-deduped",
    "1.4b-deduped":  "EleutherAI/pythia-1.4b-deduped",
    "2.8b-deduped":  "EleutherAI/pythia-2.8b-deduped",
    "6.9b-deduped":  "EleutherAI/pythia-6.9b-deduped",
    "12b-deduped":   "EleutherAI/pythia-12b-deduped",
}

TASKS: dict[str, dict] = {
    "mmlu":          {"num_fewshot": 5,  "metric": "acc,none"},
    "hellaswag":     {"num_fewshot": 10, "metric": "acc_norm,none"},
    "arc_challenge": {"num_fewshot": 25, "metric": "acc_norm,none"},
    "winogrande":    {"num_fewshot": 5,  "metric": "acc,none"},
}

# non-standard: H-M2 used 0.20 for 70m MMLU; H-M3 uses 0.30 (all-benchmark check)
# verify at runtime that 70m has >=100 checkpoints passing; fall back to 0.20 if not
FLOOR_THRESHOLD: float = 0.30
MIN_VALID_CHECKPOINTS: int = 100

N_PERMUTATIONS: int = 1000
VIF_THRESHOLD: float = 10.0
PCA_VARIANCE_RETAINED: float = 0.95
BOOKS3_VARIANCE_THRESHOLD: float = 1e-6

H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1/"
RESULTS_DIR: str = "results/h-m3"
EVAL_CACHE_DIR: str = "results/h-m3/eval_cache"
FIGURES_DIR: str = "docs/youra_research/h-m3/figures"
EXISTING_CACHE_PATH: str = "pythia/evals/pythia-v1/"

SMALL_MODEL_SIZES: list[str] = [s for s in MODEL_SIZES if any(
    s.startswith(p) for p in ["70m", "160m", "410m"]
)]
LARGE_MODEL_SIZES: list[str] = [s for s in MODEL_SIZES if s not in SMALL_MODEL_SIZES]


@dataclass
class PanelConfig:
    floor_threshold: float = FLOOR_THRESHOLD
    vif_threshold: float = VIF_THRESHOLD
    pca_variance_retained: float = PCA_VARIANCE_RETAINED
    min_checkpoints_per_model: int = MIN_VALID_CHECKPOINTS
    dropped_domain: str = "Unknown"        # set at runtime by drop_min_variance_domain()
    multiindex_levels: list[str] = field(default_factory=lambda: ["model_size", "checkpoint"])


@dataclass
class VisualizationConfig:
    dpi: int = 300
    figsize_default: tuple[int, int] = (10, 6)
    palette: str = "colorblind"
    ci_alpha: float = 0.95
    figure_paths: dict[str, str] = field(default_factory=lambda: {
        "fig1": "fig1_gate_metrics_comparison.png",
        "fig2": "fig2_domain_coefficient_heatmap.png",
        "fig3": "fig3_directional_scatter.png",
        "fig4": "fig4_r2_decomposition.png",
        "fig5": "fig5_permutation_null.png",
        "fig6": "fig6_subgroup_robustness.png",
    })


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M3"
    base_hypothesis: str = "H-M2"
    output_dir: str = RESULTS_DIR
    figures_dir: str = FIGURES_DIR
    seed: int = SEED
    n_permutations: int = N_PERMUTATIONS
    benchmarks: list[str] = field(default_factory=lambda: list(TASKS.keys()))
    focal_domains: list[str] = field(default_factory=lambda: list(FOCAL_DOMAINS.values()))
    model_sizes: list[str] = field(default_factory=lambda: list(MODEL_SIZES))
    small_sizes: list[str] = field(default_factory=lambda: list(SMALL_MODEL_SIZES))
    large_sizes: list[str] = field(default_factory=lambda: list(LARGE_MODEL_SIZES))
    resume: bool = True


FIGURE_SPECS: dict[str, dict] = {
    "fig1": {
        "type": "bar",
        "groups": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "series": ["Wikipedia (en)", "Books3"],
        "error_bars": "95ci_clustered_se",
        "figsize": (12, 6),
    },
    "fig2": {
        "type": "heatmap",
        "rows": "domain_cols",
        "cols": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "figsize": (14, 10),
    },
    "fig3": {
        "type": "scatter",
        "x": "beta_Wikipedia",
        "y": "beta_Books3",
        "hue": "benchmark",
        "diagonal": True,
        "figsize": (8, 8),
    },
    "fig4": {
        "type": "bar",
        "series": ["domain_only", "scale_only", "full"],
        "metric": "r2_within",
        "figsize": (10, 6),
    },
    "fig5": {
        "type": "histogram",
        "n_bins": 50,
        "panels": ["mmlu", "hellaswag"],
        "figsize": (12, 5),
    },
    "fig6": {
        "type": "bar",
        "series": ["small_wiki", "small_books", "large_wiki", "large_books"],
        "figsize": (14, 6),
    },
}
```

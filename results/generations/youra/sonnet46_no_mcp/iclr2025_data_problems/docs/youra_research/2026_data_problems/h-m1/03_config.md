# Configuration Document: H-M1
# Cross-Corpus Contamination Variance: The Pile v1, C4 en.noclean, RedPajama-v1

**Hypothesis**: H-M1 | **Type**: MECHANISM (PoC) | **Date**: 2026-05-04

Applied: CPU-data-pipeline-config
Applied: minhash-lsh-defaults
Applied: checkpoint-resumable-config

---

## Codebase Analysis (Serena)

**Project Type**: green-field (incremental over H-E1 specification)
**Status**: green-field - no existing code to analyze (h-e1/code/ was not implemented)
**Config Files Found**: None - new config design
**Pattern Used**: dataclass

---

## Overall Config (code/config.py)

```python
from dataclasses import dataclass, field
from typing import Optional
import os
import yaml

@dataclass
class Config:
    # N-gram parameters (fixed per WIMBD standard)
    ngram_n: int = 13
    num_perm: int = 128
    lsh_threshold: float = 0.5
    seed: int = 1
    min_token_length: int = 13
    text_format: str = "question_choices"  # or "question_only"

    # Corpus index paths
    pile_index_path: str = "../h-e1/pile_index.pkl"
    c4_index_path: str = "indices/c4_index.pkl"
    redpajama_index_path: str = "indices/redpajama_index.pkl"

    # Corpus HuggingFace identifiers
    corpus_configs: dict = field(default_factory=lambda: {
        "pile":      {"hf_path": "EleutherAI/pile",                    "config": None},
        "c4":        {"hf_path": "allenai/c4",                         "config": "en.noclean"},
        "redpajama": {"hf_path": "togethercomputer/RedPajama-Data-1T", "config": None},
    })

    # Checkpoint and retry
    checkpoint_interval: int = 500_000
    retry_attempts: int = 3
    sample_fraction: float = 0.1  # fallback if streaming fails after retries

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    indices_dir: str = "indices"

    # Gate thresholds
    gate_p_threshold: float = 0.05
    min_pair_diff_pp: float = 0.02          # 2 percentage points
    wimbd_spearman_min_rho: float = 0.7
    wimbd_pile_tolerance_pp: float = 0.05   # +/-5 pp sanity check

    # Visualization settings
    figure_width: float = 10.0
    figure_height: float = 6.0
    figure_dpi: int = 150
    figures_format: str = "png"

    # Annotation settings
    font_size_title: int = 14
    font_size_axis: int = 12
    font_size_annotation: int = 10
    font_size_legend: int = 10

    # Color palette (per corpus)
    color_pile: str = "#4C72B0"
    color_c4: str = "#DD8452"
    color_redpajama: str = "#55A868"

    # Reference line style
    ref_line_color: str = "red"
    ref_line_style: str = "--"
    ref_line_alpha: float = 0.7

    # Heatmap
    heatmap_cmap: str = "YlOrRd"
    heatmap_annot_fontsize: int = 8

def load_config(path: Optional[str] = None) -> Config:
    """Load config from YAML file, then apply environment variable overrides."""
    cfg = Config()
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    if os.environ.get("H_M1_RESULTS_DIR"):
        cfg.results_dir = os.environ["H_M1_RESULTS_DIR"]
    if os.environ.get("H_M1_FIGURES_DIR"):
        cfg.figures_dir = os.environ["H_M1_FIGURES_DIR"]
    if os.environ.get("H_M1_INDICES_DIR"):
        cfg.indices_dir = os.environ["H_M1_INDICES_DIR"]
    return cfg
```

### YAML Schema (config.yaml)

```yaml
ngram_n: 13
num_perm: 128
lsh_threshold: 0.5
seed: 1
min_token_length: 13
text_format: "question_choices"

pile_index_path: "../h-e1/pile_index.pkl"
c4_index_path: "indices/c4_index.pkl"
redpajama_index_path: "indices/redpajama_index.pkl"

checkpoint_interval: 500000
retry_attempts: 3
sample_fraction: 0.1

results_dir: "results"
figures_dir: "figures"
indices_dir: "indices"

gate_p_threshold: 0.05
min_pair_diff_pp: 0.02
wimbd_spearman_min_rho: 0.7
wimbd_pile_tolerance_pp: 0.05

figure_width: 10.0
figure_height: 6.0
figure_dpi: 150
figures_format: "png"

font_size_title: 14
font_size_axis: 12
font_size_annotation: 10
font_size_legend: 10

color_pile: "#4C72B0"
color_c4: "#DD8452"
color_redpajama: "#55A868"

ref_line_color: "red"
ref_line_style: "--"
ref_line_alpha: 0.7

heatmap_cmap: "YlOrRd"
heatmap_annot_fontsize: 8
```

---

## A-7: Visualization [Complexity: 11, Budget: 2]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Visualizer figure configuration schema | Figure sizes, DPI, color palettes, save paths |
| C-7-2 | Plot annotation configuration | Font sizes, reference line styles, legend settings |

---

## C-7-1: Visualizer Figure Configuration Schema

**Parent Epic**: A-7

```python
# Fields on Config used by Visualizer figure layout:
figure_width: float = 10.0
figure_height: float = 6.0
figure_dpi: int = 150        # Non-standard: 150 for publication quality (default 72)
figures_format: str = "png"

color_pile: str = "#4C72B0"
color_c4: str = "#DD8452"
color_redpajama: str = "#55A868"

# Per-figure size constants (in visualizer.py, not Config)
FIGURE_SIZES = {
    "corpus_comparison_barplot":    (10, 6),
    "contamination_matrix_heatmap": (14, 10),  # wider for 59 rows
    "corpus_pair_differences":      (10, 6),
    "wimbd_consistency_scatter":    (8, 8),    # square for scatter
    "per_corpus_rankings":          (12, 8),
    "dunn_posthoc_heatmap":         (6, 5),    # small 3x3
}
# Save paths resolved as: f"{config.figures_dir}/{name}.{config.figures_format}"
```

**Valid ranges**: `figure_dpi` in [72, 300]; `figures_format` in ["png", "pdf", "svg"]

---

## C-7-2: Plot Annotation Configuration

**Parent Epic**: A-7

```python
font_size_title: int = 14
font_size_axis: int = 12
font_size_annotation: int = 10   # H=..., p=... text on bar chart
font_size_legend: int = 10

ref_line_color: str = "red"
ref_line_style: str = "--"
ref_line_alpha: float = 0.7

heatmap_cmap: str = "YlOrRd"    # Non-standard: semantically maps low=yellow, high=red for contamination
heatmap_annot_fontsize: int = 8  # smaller for 59-row readability

# Legend placement constants (in visualizer.py, not Config)
LEGEND_LOC = {
    "corpus_comparison_barplot":  "upper right",
    "per_corpus_rankings":        "lower right",
    "wimbd_consistency_scatter":  "upper left",
}
```

**Valid ranges**: font sizes in [6, 24]; `ref_line_alpha` in [0.0, 1.0]

---

## A-8: Orchestration + Sensitivity [Complexity: 10, Budget: 2]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | RunExperiment pipeline configuration | Output dirs, gate thresholds, pipeline flags |
| C-8-2 | Sensitivity analysis configuration | text_format options, comparison metrics settings |

---

## C-8-1: RunExperiment Pipeline Configuration

**Parent Epic**: A-8

```python
results_dir: str = "results"
figures_dir: str = "figures"
indices_dir: str = "indices"

gate_p_threshold: float = 0.05
min_pair_diff_pp: float = 0.02
wimbd_spearman_min_rho: float = 0.7
wimbd_pile_tolerance_pp: float = 0.05

# Fixed output filenames (constants in run_experiment.py)
MATRIX_CSV = "contamination_matrix.csv"   # -> results/contamination_matrix.csv
STATS_JSON = "statistical_tests.json"     # -> results/statistical_tests.json
```

### Environment Variable Overrides

| Variable | Config Field | Default |
|----------|-------------|---------|
| `H_M1_RESULTS_DIR` | `results_dir` | `"results"` |
| `H_M1_FIGURES_DIR` | `figures_dir` | `"figures"` |
| `H_M1_INDICES_DIR` | `indices_dir` | `"indices"` |
| `CUDA_VISIBLE_DEVICES` | n/a (CPU-only) | `""` |
| `HF_DATASETS_CACHE` | n/a (HF library) | system default |

---

## C-8-2: Sensitivity Analysis Configuration

**Parent Epic**: A-8

```python
text_format: str = "question_choices"   # primary run

# Sensitivity run uses a shallow copy of Config with text_format overridden:
# sens_config = copy.copy(config)
# sens_config.text_format = "question_only"
# Passed to run_sensitivity(config, indices, primary_matrix)
```

### statistical_tests.json Output Schema

```json
{
  "kruskal_H": 0.0,
  "kruskal_p": 0.0,
  "gate_pass": true,
  "corpus_means": {"pile": 0.0, "c4": 0.0, "redpajama": 0.0},
  "max_pair_diff_pp": 0.0,
  "wimbd_spearman_rho": 0.0,
  "wimbd_spearman_p": 0.0,
  "dunn_posthoc": {},
  "sensitivity_kruskal_p": 0.0,
  "sensitivity_spearman_rho": 0.0,
  "sensitivity_corpus_means": {"pile": 0.0, "c4": 0.0, "redpajama": 0.0},
  "c4_sampled": false,
  "rp_sampled": false
}
```

**Valid values**: `text_format` in `["question_choices", "question_only"]`

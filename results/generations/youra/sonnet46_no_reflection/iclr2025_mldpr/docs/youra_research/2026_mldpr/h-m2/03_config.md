# H-M2 Configuration Design

**Hypothesis ID:** H-M2
**Date:** 2026-05-19
**Type:** MECHANISM — Domain-Specific Degradation Signal Leading Indicator Analysis

Applied: incremental-statistical-pipeline-flat-dict-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config verified from actual H-M1 code (run_experiment.py direct file read)
**Config Files Found**: `h-m1/code/run_experiment.py` — flat `CONFIG` dict (no dataclass)
**Pattern Used**: hardcoded dict (H-M1 style); dataclass added for H-M2 (new fields)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (From Actual H-M1 Code)

```python
# From: h-m1/code/run_experiment.py CONFIG dict — VERIFIED from actual implementation
H_M1_CONFIG = {
    "seed": 42,
    "min_submissions": 20,
    "min_history_years": 2,
    "min_quarters": 8,
    "date_start": "2018-01-01",
    "date_end": "2025-12-31",
    "domains": ["cv", "nlp", "tabular"],
    "compression_threshold": 1.5,       # sigma-normalized threshold
    "min_consecutive": 2,
    "top_k_scores": 10,
    "granger_max_lag": 4,
    "granger_primary_lag": 2,
    "adf_significance": 0.05,
    "spearman_rho_target": 0.4,
    "granger_p_target": 0.05,
    "significance_level": 0.05,
    "min_panel_rows": 200,
    "min_granger_benchmarks": 30,
    "output_dir": "../figures",
    "results_json": "../results.json",
    "results_csv": "outputs/results.csv",
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"},
}
```

**Verified from**: `docs/youra_research/20260519_mldpr/h-m1/code/run_experiment.py` (actual implementation)

**H-M1 import paths verified**:
- `from data_pipeline import load_panel, load_pwc_raw, compute_quarterly_panel`
- `from compression_detector import flag_compression, summarize_compression`
- `from sigma_estimation import get_sigma_map`

**Key panel columns verified**: `benchmark_id`, `task`, `dataset`, `quarter`, `submission_count`, `cumulative_count`, `score_var_top10`, `compressed`, `compression_event`

---

## 1. ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import Dict, List
import os

@dataclass
class ExperimentConfig:
    # --- H-M1 reuse path ---
    hm1_code_path: str = "../h-m1/code"

    # --- Data loading ---
    dataset_id: str = "pwc-archive/evaluation-tables"

    # --- Panel construction (inherited from H-M1, verified) ---
    min_submissions: int = 20
    min_quarters: int = 8
    date_start: str = "2018-01-01"
    date_end: str = "2025-12-31"
    domains: List[str] = field(default_factory=lambda: ["cv", "nlp", "tabular"])

    # --- H_d signal thresholds (per domain) ---
    # Non-standard: CV=0.5 (rolling std robustness gap threshold per H-E1 validation)
    # Non-standard: NLP=0.3 (contamination probability threshold per ConStat calibration)
    # Non-standard: tabular=0.90 (Kendall tau rank stabilization threshold per H-E1)
    domain_thresholds: Dict[str, float] = field(
        default_factory=lambda: {"cv": 0.5, "nlp": 0.3, "tabular": 0.90}
    )

    # --- Bootstrap ---
    bootstrap_iters: int = 100
    seed: int = 42

    # --- Collapse detection ---
    tau_threshold: float = 0.90
    min_consecutive: int = 2
    # Non-standard: R1 mitigation fallback threshold if collapse_events < min_collapse_events
    r1_tau_threshold: float = 0.85
    min_collapse_events: int = 20

    # --- Lead time analysis ---
    min_lead_months: int = 12
    gate_fraction_threshold: float = 0.60
    gate_min_domains: int = 2

    # --- H_d signal rolling window ---
    rolling_quarters: int = 4

    # --- Statistical tests ---
    significance_level: float = 0.05

    # --- Output paths ---
    output_dir: str = "../figures"
    results_json: str = "../results.json"
    results_csv: str = "outputs/results.csv"
    figure_dpi: int = 150
    figure_size: tuple = (10, 6)
    domain_colors: Dict[str, str] = field(
        default_factory=lambda: {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"}
    )

    # --- Ablation variants to run ---
    ablation_variants: List[str] = field(
        default_factory=lambda: ["A1", "A2", "A3", "A4", "A5"]
    )
```

---

## 2. YAML Config Schema

```yaml
# h-m2/config.yaml — equivalent representation of ExperimentConfig
hm1_code_path: "../h-m1/code"
dataset_id: "pwc-archive/evaluation-tables"

# Panel construction
min_submissions: 20
min_quarters: 8
date_start: "2018-01-01"
date_end: "2025-12-31"
domains:
  - cv
  - nlp
  - tabular

# H_d signal thresholds
domain_thresholds:
  cv: 0.5
  nlp: 0.3
  tabular: 0.90

# Bootstrap
bootstrap_iters: 100
seed: 42

# Collapse detection
tau_threshold: 0.90
min_consecutive: 2
r1_tau_threshold: 0.85
min_collapse_events: 20

# Lead time analysis
min_lead_months: 12
gate_fraction_threshold: 0.60
gate_min_domains: 2
rolling_quarters: 4

# Statistical tests
significance_level: 0.05

# Output
output_dir: "../figures"
results_json: "../results.json"
results_csv: "outputs/results.csv"
figure_dpi: 150

# Ablation
ablation_variants: [A1, A2, A3, A4, A5]
```

---

## 3. Ablation Variant Config (A1–A5)

```python
ABLATION_VARIANTS = {
    "A1": {
        "description": "t-24mo offset (PROPOSED — 24-month lead window)",
        "lead_months": 24,
        "use_compression_filter": True,
    },
    "A2": {
        "description": "t-12mo offset (12-month lead window)",
        "lead_months": 12,
        "use_compression_filter": True,
    },
    "A3": {
        "description": "t offset — concurrent (BASELINE)",
        "lead_months": 0,
        "use_compression_filter": True,
    },
    "A4": {
        "description": "compression-filtered only (tests compression as necessary condition)",
        "lead_months": 24,
        "use_compression_filter": True,
    },
    "A5": {
        "description": "all benchmarks — no compression filter",
        "lead_months": 24,
        "use_compression_filter": False,
    },
}
```

---

## 4. Domain Threshold Config

```python
# Per-domain H_d signal thresholds — pre-registered from H-E1 validation
DOMAIN_THRESHOLDS = {
    # CV: robustness gap (rolling std of score_var_top10 for corrupted vs. clean)
    # Non-standard: 0.5 validated in H-E1 as empirical gap separating degraded vs. healthy
    "cv": 0.5,

    # NLP: contamination probability (ConStat normalized score deviation from baseline)
    # Non-standard: 0.3 calibrated from ConStat API; consistent with H-E1 findings
    "nlp": 0.3,

    # Tabular: block-bootstrapped Kendall tau rank correlation stabilization
    # Non-standard: 0.90 matches tau_threshold for collapse detection (same scale, different use)
    "tabular": 0.90,
}
```

---

## 5. Environment / Dependency Spec

```text
# h-m2/requirements.txt
lifelines==0.30.0
scipy>=1.10
pandas>=2.0
numpy>=1.24
datasets>=2.0
matplotlib>=3.7
seaborn>=0.12
scikit-learn>=1.3
```

---

## 6. Run Config (Flat Dict — Entry Point)

```python
# h-m2/code/run_experiment.py CONFIG (hardcoded dict, mirrors ExperimentConfig)
import os

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    # H-M1 reuse
    "hm1_code_path": os.path.join(_CODE_DIR, "..", "..", "h-m1", "code"),
    "dataset_id": "pwc-archive/evaluation-tables",

    # Panel construction (verified H-M1 field names)
    "min_submissions": 20,
    "min_quarters": 8,
    "date_start": "2018-01-01",
    "date_end": "2025-12-31",
    "domains": ["cv", "nlp", "tabular"],

    # H_d thresholds
    "domain_thresholds": {"cv": 0.5, "nlp": 0.3, "tabular": 0.90},

    # Bootstrap
    "bootstrap_iters": 100,
    "seed": 42,

    # Collapse detection
    "tau_threshold": 0.90,
    "min_consecutive": 2,
    "r1_tau_threshold": 0.85,
    "min_collapse_events": 20,

    # Lead time analysis
    "min_lead_months": 12,
    "gate_fraction_threshold": 0.60,
    "gate_min_domains": 2,
    "rolling_quarters": 4,

    # Statistical tests
    "significance_level": 0.05,

    # Output
    "output_dir": os.path.join(os.path.dirname(_CODE_DIR), "figures"),
    "results_json": os.path.join(os.path.dirname(_CODE_DIR), "results.json"),
    "results_csv": os.path.join(_CODE_DIR, "outputs", "results.csv"),
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"},

    # Ablation
    "ablation_variants": ["A1", "A2", "A3", "A4", "A5"],
}
```

---

## Config Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | ExperimentConfig dataclass | Implement `config.py` with ExperimentConfig dataclass; all fields with defaults |
| C-2 | YAML loader | Implement `load_config(yaml_path)` utility that returns ExperimentConfig from YAML override |
| C-3 | Ablation variant registry | Implement `ABLATION_VARIANTS` dict in `ablation.py`; wire lead_months + use_compression_filter flags |
| C-4 | Domain threshold registry | Implement `DOMAIN_THRESHOLDS` constant in `hd_signals.py`; shared import by temporal_analysis and collapse_detector |
| C-5 | requirements.txt | Write `h-m2/requirements.txt` with pinned lifelines==0.30.0 and compatible scipy/pandas/numpy versions |
| C-6 | argparse integration | Implement `parse_args(config, args)` in `run_experiment.py`; CLI flags for seed, min_submissions, min_quarters, tau_threshold, output_dir, results_json, results_csv |

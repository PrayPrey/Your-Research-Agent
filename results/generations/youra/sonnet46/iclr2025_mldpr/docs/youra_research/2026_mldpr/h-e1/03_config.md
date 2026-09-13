# Configuration: H-E1
# DTS-Weighted Documentation Completeness Scoring System (EXISTENCE PoC)

**Date:** 2026-03-15
**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC) — LIGHT tier

Applied: hardcoded-dict-flat-config-for-poc

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — Serena skip acceptable, no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: hardcoded dict (LIGHT tier EXISTENCE PoC, per NFR-4)

---

## Global Constants (Shared Across All Modules)

```python
# config.py — or inline at top of experiment.py / scorer.py / evaluate.py
CONFIG = {
    "seed": 42,
    "n_hf": 500,
    "n_openml": 200,
    "n_pilot_per_repo": 50,
    "n_human_subsample": 120,
    "n_human_per_repo": 40,
    "coverage_threshold": 0.70,
    "pearson_threshold": 0.70,
    "pilot_min_coverage": 0.30,
    "n_bootstrap": 1000,
    "hf_rate_limit_sec": 1.0,
    "hf_rate_limit_auth": 0.2,
    "uci_rate_limit_sec": 2.0,
}

DTS_SECTIONS = {
    "motivation":    ["task_categories", "language", "tags", "license"],
    "composition":   ["size_categories", "num_rows", "num_columns", "features"],
    "collection":    ["source_datasets", "annotations_creators", "original_data_url"],
    "preprocessing": ["preprocessing_steps", "data_augmentation", "data_splits"],
    "uses":          ["known_limitations", "out_of_scope_use", "discussion_best_use"],
    "distribution":  ["license", "citation", "contact", "maintenance_plan"],
}

DTS_WEIGHTS = {
    "motivation": 1.0,
    "composition": 0.9,
    "collection": 2.1,      # Non-standard: highest weight per Rondina et al. 2025 Table 2
    "preprocessing": 1.8,
    "uses": 1.5,
    "distribution": 0.7,
}
```

---

## A-5: Human Validation + Correlation [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard scipy bootstrap CI pattern

```python
VALIDATION_CONFIG = {
    "n_human_subsample": 120,
    "n_human_per_repo": 40,
    "seed": 42,
    "n_bootstrap": 1000,
    "ci_level": 0.95,
    "pearson_threshold": 0.70,
    "annotation_template_path": "data/validation/human_annotation_template.csv",
    "human_annotations_path": "data/validation/human_annotations.csv",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Validation Config Schema | VALIDATION_CONFIG dict covering subsample sizes, seed, paths |
| C-5-2 | Bootstrap CI Parameters | n_bootstrap=1000, ci_level=0.95, seed=42 for pearsonr CI |

---

## A-6: Visualization + Evaluation + Results [Complexity: 13, Budget: 2 subtasks]

**Applied**: Flat output-path config for matplotlib figure generation

```python
FIGURES_CONFIG = {
    "figures_dir": "figures",
    "dpi": 150,
    "figsize_bar": (8, 5),
    "figsize_heatmap": (10, 6),
    "figsize_violin": (10, 5),
    "figsize_scatter": (7, 7),
    "gate_metrics_path": "figures/gate_metrics_comparison.png",
    "section_heatmap_path": "figures/per_section_coverage_heatmap.png",
    "dts_distribution_path": "figures/dts_score_distribution.png",
    "human_scatter_path": "figures/human_automated_scatter.png",
    "missing_field_path": "figures/missing_field_analysis.png",
}

GATE_CONFIG = {
    "coverage_threshold": 0.70,
    "pearson_threshold": 0.70,
    "pilot_min_coverage": 0.30,
    "results_output_path": "results/h_e1_results.json",
    "mechanism_indicators": ["scoring_ran", "coverage_achievable", "weighting_effect", "human_correlation_positive"],
    "failure_codes": {
        "coverage": "COVERAGE_BELOW_THRESHOLD",
        "validation": "VALIDATION_BELOW_THRESHOLD",
        "pilot": "PILOT_COVERAGE_FAILED",
        "api": "API_UNAVAILABLE",
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure Output Config | FIGURES_CONFIG dict: paths for all 5 mandatory figures, dpi, figsize per plot type |
| C-6-2 | Gate Evaluation Config | GATE_CONFIG dict: thresholds, result path, mechanism indicator names, failure codes |

---

*Config for H-E1 EXISTENCE PoC — LIGHT tier*
*No dataclasses, no YAML — hardcoded dicts per NFR-4*
*CPU-only statistical pipeline, no training hyperparameters*

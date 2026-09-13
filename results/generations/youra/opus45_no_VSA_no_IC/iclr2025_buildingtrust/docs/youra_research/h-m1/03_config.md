# Configuration: H-M1

**Applied**: Standard correlation-analysis config (flat YAML, no training hyperparameters — analysis-only experiment)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (sibling hypothesis H-E1 provides model population + result format)
**Status**: Verified H-E1's actual `code/config.py` (flat module-constants pattern, not dataclass)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: Flat YAML (matches H-E1's flat-constants style; no dataclass needed — single fixed analysis run, no hyperparameter sweep)

---

## A-1: Correlation Analysis Config [Complexity: 1, Budget: 1]

**Applied**: Flat YAML config, single fixed run (analysis experiment, not training)

### config.yaml

```yaml
# H-M1: TruthfulQA vs MMLU divergence analysis

data:
  source: "open-llm-leaderboard/results"
  model_population_ref: "../h-e1/experiment_results.json"  # reuse H-E1's N=50 models
  n_models: 50
  fallback_source: "lm-evaluation-harness"

paths:
  results_dir: "results/"
  results_file: "results/h_m1_results.json"
  figures_dir: "figures/"
  gate_figure: "figures/gate_comparison.png"
  data_cache_dir: "data_cache/"

thresholds:
  divergent_zscore: 1.0        # |z| >= 1.0 flags divergent MMLU/TruthfulQA profile
  divergent_mmlu_z_min: 1.0    # high MMLU z-score
  divergent_truthfulqa_z_max: 0.0  # low TruthfulQA z-score

statistics:
  correlation_method: "spearman"
  alpha: 0.05                  # significance level (NFR / FR-3.2 equivalent)
  ci_level: 0.95

mmlu_subjects:
  - abstract_algebra
  - anatomy
  - astronomy
  - business_ethics
  - clinical_knowledge
  - college_biology
  - college_chemistry
  - college_computer_science
  - college_mathematics
  - college_medicine
  - college_physics
  - computer_security
  - conceptual_physics
  - econometrics
  - electrical_engineering
  - elementary_mathematics
  - formal_logic
  - global_facts
  - high_school_biology
  - high_school_chemistry
  - high_school_computer_science
  - high_school_european_history
  - high_school_geography
  - high_school_government_and_politics
  - high_school_macroeconomics
  - high_school_mathematics
  - high_school_microeconomics
  - high_school_physics
  - high_school_psychology
  - high_school_statistics
  - high_school_us_history
  - high_school_world_history
  - human_aging
  - human_sexuality
  - international_law
  - jurisprudence
  - logical_fallacies
  - machine_learning
  - management
  - marketing
  - medical_genetics
  - miscellaneous
  - moral_disputes
  - moral_scenarios
  - nutrition
  - philosophy
  - prehistory
  - professional_accounting
  - professional_law
  - professional_medicine
  - professional_psychology
  - public_relations
  - security_studies
  - sociology
  - us_foreign_policy
  - virology
  - world_religions

visualization:
  gate_comparison:
    figsize: [8, 6]
    dpi: 150
    format: "png"
  scatter_matrix:
    figsize: [10, 8]
    dpi: 150
    point_alpha: 0.6
  color_divergent: "red"
  color_normal: "steelblue"

seed: 42
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config load | Load `config.yaml`, resolve H-E1 results path, validate 57 MMLU subjects present |

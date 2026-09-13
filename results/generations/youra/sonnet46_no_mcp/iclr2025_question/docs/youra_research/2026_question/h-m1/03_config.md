# Configuration: H-M1
## Token Entropy vs. Semantic Entropy Divergence Analysis

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1)
**Type:** INCREMENTAL on H-E1

Applied: correlation-analysis-experiment-config-dataclass

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class ExperimentConfig:
    # Dataset
    hf_dataset_id: str = "pminervini/HaluEval"
    dataset_split: str = "qa_samples"
    n_hallucinated: int = 1000
    n_factual: int = 1000
    seed: int = 42

    # LLM Inference
    llm_model_id: str = "meta-llama/Llama-2-7b-hf"
    llm_dtype: str = "bfloat16"
    max_new_tokens: int = 256
    greedy_temperature: float = 0.0
    stochastic_temperature: float = 1.0
    n_stochastic_samples: int = 5

    # NLI Model
    nli_model_id: str = "microsoft/deberta-large-mnli"
    nli_batch_size: int = 16

    # Evaluation
    n_bootstrap: int = 1000
    bonferroni_k: int = 3
    alpha: float = 0.05
    min_auroc_gap: float = 0.05
    min_ci_separation: float = 0.0

    # Paths (relative to code/ directory)
    data_dir: str = "data"
    outputs_dir: str = "outputs"
    results_dir: str = "results"
    figures_dir: str = "figures"
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

H-M1 reuses `seed` and `n_bootstrap` defaults (42 and 1000) from h-e1. All other h-e1 fields are not inherited (LLM/NLI inference is not re-run).

---

## A-2: Config Module [Complexity: 4, Budget: 2 subtasks]

Applied: correlation-analysis-experiment-config-dataclass

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    # Analysis parameters
    seed: int = 42
    n_bootstrap: int = 1000
    degenerate_threshold: float = 1e-6
    pearson_gate_threshold: float = 0.9
    divergence_sigma_multiplier: float = 1.0

    # Input paths (relative to h-m1/code/)
    te_scores_path: str = "../../h-e1/code/outputs/uq_scores/token_entropy_mean.json"
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"

    # Output paths (relative to h-m1/code/)
    results_dir: str = "outputs"
    figures_dir: str = "figures"
    results_file: str = "outputs/experiment_results.json"

    # Visualization
    figure_dpi: int = 150
    figure_format: str = "png"
    scatter_figsize: tuple = (8, 8)
    histogram_figsize: tuple = (10, 6)
    cdf_figsize: tuple = (8, 6)
    ttr_figsize: tuple = (8, 6)
    divergence_figsize: tuple = (10, 6)


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
```

### YAML Config Schema

```yaml
experiment:
  hypothesis_id: "h-m1"
  seed: 42
  n_bootstrap: 1000
  degenerate_threshold: 1.0e-6
  pearson_gate_threshold: 0.9
  divergence_sigma_multiplier: 1.0

paths:
  te_scores: "../../h-e1/code/outputs/uq_scores/token_entropy_mean.json"
  se_scores: "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
  stochastic_samples: "../../h-e1/code/outputs/stochastic_samples.jsonl"
  dataset: "../../h-e1/code/data/halueval_qa_2k.json"
  results_dir: "outputs/"
  figures_dir: "figures/"
  results_file: "outputs/experiment_results.json"

visualization:
  dpi: 150
  format: "png"
  scatter_figsize: [8, 8]
  histogram_figsize: [10, 6]
  cdf_figsize: [8, 6]
  ttr_figsize: [8, 6]
  divergence_figsize: [10, 6]
```

### Visualization Config (5 Plots)

| Plot | Function | figsize | Notes |
|------|----------|---------|-------|
| scatter_te_vs_se | `plot_scatter_te_vs_se` | (8, 8) | Square for identity line |
| cluster_count_dist | `plot_cluster_count_dist` | (10, 6) | Histogram |
| divergence_dist | `plot_divergence_dist` | (10, 6) | Histogram/KDE with threshold line |
| ttr_vs_divergence | `plot_ttr_vs_divergence` | (8, 6) | Scatter with highlight |
| bootstrap_ci | `plot_bootstrap_ci` | (8, 6) | CDF with CI bounds |

Colors (matplotlib defaults suffice; non-standard values noted):
- High-divergence highlight: `"red"` (non-standard: used for visual emphasis in ttr_vs_divergence)
- Gate threshold line: `"orange"` (non-standard: distinct from CI bound lines)
- Identity line (y=x): `"gray"`, linestyle `"--"`

### Subtasks [2/2 used]

| ID | Subtask | Description | Parent |
|----|---------|-------------|--------|
| C-8-1 | plot_scatter_te_vs_se | Scatter plot with identity line (y=x) and Pearson r annotation at top-left | E-8 |
| C-8-2 | Remaining 4 plot functions | plot_cluster_count_dist (histogram), plot_divergence_dist (histogram+threshold), plot_ttr_vs_divergence (scatter+highlight), plot_bootstrap_ci (CDF+CI+gate) | E-8 |

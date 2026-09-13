# Config: H-M2
# Min-k% Memorization Signal — Pile vs Dedup-Pile

**Hypothesis:** H-M2 (MECHANISM / FULL tier)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: Dataclass-first Config (single source of truth in config.py)
Applied: Checkpoint-Resume Pipeline Pattern (stage-level skip flags)
Applied: fp16-GPU-inference-config pattern (memory-efficient Pythia loading)
Applied: Seaborn Theme Config Pattern (figure style centralized)

---

## Codebase Analysis (Serena)

**Project Type**: incremental_hypothesis (base: h-m1)
**Status**: patterns derived from h-m1/03_config.md (Serena MCP unavailable)
**Config Pattern Used**: dataclass (same as h-m1)
**Base Config verified from**: `docs/youra_research/h-m1/03_config.md` (`ExperimentConfig` dataclass)

**Inherited fields (verified from h-m1/03_config.md):**
- `benchmarks: list[str]` = `["mmlu", "hellaswag", "arc_challenge", "winogrande"]`
- `corrected_alpha: float` = 0.0125
- `random_seed: int` = 42 (h-m1); h-m2 uses seed=1 (inference is deterministic; seed for any future sampling)
- JSON checkpoint pattern, atomic write — same
- Flat directory structure — same
- matplotlib Agg backend, seaborn whitegrid/paper — same

---

## Main Configuration

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    # Hypothesis
    hypothesis_id: str = "h-m2"
    name: str = "Min-k% Memorization Signal — Pile vs Dedup-Pile"

    # Models (HuggingFace IDs and revision steps)
    model_configs: dict = field(default_factory=lambda: {
        "pile_1b":     ("EleutherAI/pythia-1b",            "step98000"),
        "deduped_1b":  ("EleutherAI/pythia-1b-deduped",   "step143000"),
        "pile_6.9b":   ("EleutherAI/pythia-6.9b",          "step98000"),
        "deduped_6.9b":("EleutherAI/pythia-6.9b-deduped", "step143000"),
    })
    model_sizes: list = field(default_factory=lambda: ["1b", "6.9b"])
    cache_dir: str = "./model_cache"
    torch_dtype: str = "float16"    # fp16 for memory efficiency
    device: str = "cuda"            # "cpu" fallback for 1B model on CPU-only

    # Token-count matching
    tokens_per_step: int = 2_097_152   # 2M tokens per Pile step
    pile_matched_step: int = 98_000    # ~205.7B tokens
    dedup_final_step: int = 143_000    # ~207B tokens (dedup-Pile final)

    # Benchmarks
    benchmarks: list = field(default_factory=lambda: ["mmlu", "hellaswag", "arc_challenge", "winogrande"])

    # Min-k% parameters
    k_primary: int = 20              # Shi et al. 2023 optimal k
    k_values: list = field(default_factory=lambda: [10, 20, 40])
    k_sensitivity: list = field(default_factory=lambda: [5, 10, 20, 40, 60])
    min_seq_len: int = 32            # minimum tokens for valid scoring
    max_seq_len: int = 512           # truncation length

    # Statistical testing
    alpha: float = 0.05
    n_benchmarks: int = 4
    corrected_alpha: float = 0.0125   # alpha / n_benchmarks (Bonferroni)
    wilcoxon_alternative: str = "greater"   # one-tailed
    ttest_alternative: str = "greater"       # one-tailed

    # Batch configuration
    scoring_batch_size: int = 1      # safe default; 8 for speed with padding
    n_workers: int = 1               # inference is single-process (GPU-bound)

    # Paths
    base_dir: Path = Path("docs/youra_research/h-m2")
    checkpoint_dir: Path = Path("docs/youra_research/h-m2/checkpoints")
    figures_dir: Path = Path("docs/youra_research/h-m2/figures")
    hm1_results_path: Path = Path("docs/youra_research/h-m1/statistical_results.json")

    # Pipeline stages
    pipeline_stages: list = field(default_factory=lambda: [
        "load_benchmarks",
        "score_models",
        "run_stats",
        "run_ablations",
        "generate_figures",
    ])
    skip_stages: list = field(default_factory=list)
    resume: bool = True

    # Logging
    log_level: str = "INFO"
    random_seed: int = 1             # inference deterministic; seed for any sampling


CONFIG = ExperimentConfig()
```

---

## A-5: Statistical Tester Config [Complexity: 10, Budget: 2 subtasks]

Applied: non-parametric-paired-test pattern

### C-5-1: Statistical Test Configuration

```python
@dataclass
class StatConfig:
    # Primary test
    primary_test: str = "ttest_rel"         # scipy.stats.ttest_rel
    alternative: str = "greater"             # one-tailed: pile > deduped
    alpha: float = 0.05
    n_benchmarks: int = 4
    corrected_alpha: float = 0.0125          # Bonferroni

    # Secondary test
    secondary_test: str = "wilcoxon"         # scipy.stats.wilcoxon

    # Effect size
    effect_size: str = "cohens_d"            # paired Cohen's d

    # Cross-hypothesis
    cross_hyp_metric: str = "spearman"       # scipy.stats.spearmanr
    hm1_expected_ranking: list = field(
        default_factory=lambda: ["mmlu", "arc_challenge", "hellaswag", "winogrande"]
    )

    # Gate thresholds
    gate_primary: int = 2      # n_significant >= 2 for PASS
    gate_relaxed: int = 1      # n_significant >= 1 for SHOULD_WORK_PASS

    # Output
    results_file: str = "statistical_results_hm2.json"
```

### C-5-2: Gate Decision Configuration

```python
@dataclass
class GateConfig:
    gate_type: str = "SHOULD_WORK"
    primary_metric: str = "n_significant_benchmarks"
    primary_threshold: int = 2       # full PASS
    relaxed_threshold: int = 1       # SHOULD_WORK_PASS
    significance_level: float = 0.0125   # Bonferroni-corrected

    # Failure actions
    on_fail_explore: list = field(default_factory=lambda: [
        "Try zlib ratio metric instead of min-k%",
        "Try lowercase-all perplexity differential",
        "Check token-count matching (step mismatch common cause)",
        "Check tokenizer consistency across Pile/dedup-Pile models",
    ])
    failure_blocks_downstream: bool = False   # SHOULD_WORK gate
```

### Subtasks [2/2 used]

| ID | Parent Epic | Subtask | Description |
|----|-------------|---------|-------------|
| C-5-1 | A-5 | Statistical test config | StatConfig: test names, alpha, Bonferroni, effect size, cross-hyp metric, gate thresholds, output file |
| C-5-2 | A-5 | Gate decision config | GateConfig: gate type, thresholds, failure exploration actions |

---

## A-6: Ablation Runner Config [Complexity: 9, Budget: 2 subtasks]

Applied: ablation-variant-registry pattern

### C-6-1: k-Sensitivity Configuration

```python
@dataclass
class AblationConfig:
    # k-sensitivity
    k_sensitivity_benchmark: str = "mmlu"    # run k-sensitivity on largest benchmark only
    k_values: list = field(default_factory=lambda: [5, 10, 20, 40, 60])
    k_primary: int = 20                       # reference k

    # Ablation output
    ablation_results_file: str = "ablation_results_hm2.json"
    k_sensitivity_figure: str = "fig_k_sensitivity.png"

    # Summary thresholds
    k_robustness_criterion: str = "effect_direction_consistent"
    # direction (Pile > deduped) should hold for k ∈ {10, 20, 40}
```

### C-6-2: Ablation Checkpoint Configuration

```python
@dataclass
class AblationCheckpointConfig:
    # Per k-value checkpoints
    k_score_file_template: str = "mink_scores_{model_key}_{benchmark}_k{k}.json"
    # Ablation uses same score_benchmark_items() with different k values
    # Checkpoint per (model_key, benchmark, k) tuple
    resume: bool = True
```

### Subtasks [2/2 used]

| ID | Parent Epic | Subtask | Description |
|----|-------------|---------|-------------|
| C-6-1 | A-6 | k-sensitivity config | AblationConfig: k values, benchmark target, output file, robustness criterion |
| C-6-2 | A-6 | Ablation checkpoint config | AblationCheckpointConfig: file template, resume flag per (model, benchmark, k) |

---

## Inherited Configuration (from H-M1)

**Verified from:** `docs/youra_research/h-m1/03_config.md` (actual h-m1 config dataclass)

| Field | H-M1 Value | H-M2 Value | Change Reason |
|-------|-----------|-----------|---------------|
| `benchmarks` | `["mmlu", "hellaswag", "arc_challenge", "winogrande"]` | Same | Same 4 benchmarks for cross-hypothesis correlation |
| `corrected_alpha` | 0.0125 | Same | Same Bonferroni correction (4 benchmarks) |
| `alpha` | 0.05 | Same | Same family-wise error rate |
| `random_seed` | 42 | 1 | Inference deterministic; seed semantics differ |
| `n_workers` | 4 | 1 | CPU multiprocessing → GPU single-process inference |
| FigureConfig.color_removed | "#d62728" | "#d62728" (Pile) | Keep color convention |
| FigureConfig.color_retained | "#1f77b4" | "#1f77b4" (deduped) | Keep color convention |
| StyleConfig.seaborn_theme | "whitegrid" | "whitegrid" | Same |
| StyleConfig.seaborn_context | "paper" | "paper" | Same |
| StyleConfig.mpl_backend | "Agg" | "Agg" | Same |

---

## Figure Configuration

```python
@dataclass
class FigureConfig:
    dpi: int = 150
    bar_figsize: tuple = (14, 6)      # wider: 2 model sizes side by side
    heatmap_figsize: tuple = (6, 5)
    violin_figsize: tuple = (16, 5)   # 4 subplots
    scatter_figsize: tuple = (6, 5)
    k_sens_figsize: tuple = (7, 5)
    
    color_pile: str = "#d62728"       # red — matches h-m1 "removed"
    color_deduped: str = "#1f77b4"    # blue — matches h-m1 "retained"
    color_scatter: str = "#2ca02c"    # green for cross-hyp scatter
    
    sig_thresholds: tuple = (0.001, 0.01, 0.05)
    sig_markers: tuple = ("***", "**", "*", "ns")
    
    output_format: str = "png"
    ci: float = 0.95
    
    out_bar: str = "figures/fig_mink_comparison.png"      # mandatory gate figure
    out_heatmap: str = "figures/fig_mink_heatmap.png"
    out_violin: str = "figures/fig_mink_violin.png"
    out_k_sens: str = "figures/fig_k_sensitivity.png"
    out_cross_hyp: str = "figures/fig_cross_hypothesis.png"
```

---

## YAML Config Schema (experiment_config.yaml)

```yaml
experiment:
  hypothesis_id: "h-m2"
  name: "Min-k% Memorization Signal — Pile vs Dedup-Pile"

models:
  pile_1b:
    hf_id: "EleutherAI/pythia-1b"
    revision: "step98000"
  deduped_1b:
    hf_id: "EleutherAI/pythia-1b-deduped"
    revision: "step143000"
  pile_6.9b:
    hf_id: "EleutherAI/pythia-6.9b"
    revision: "step98000"
  deduped_6.9b:
    hf_id: "EleutherAI/pythia-6.9b-deduped"
    revision: "step143000"
  cache_dir: "./model_cache"
  torch_dtype: "float16"
  device: "cuda"

benchmarks:
  tasks: [mmlu, hellaswag, arc_challenge, winogrande]

mink:
  k_primary: 20
  k_values: [10, 20, 40]
  min_seq_len: 32
  max_seq_len: 512
  scoring_batch_size: 1

statistics:
  alpha: 0.05
  n_benchmarks: 4
  corrected_alpha: 0.0125
  primary_test: "ttest_rel"
  alternative: "greater"

ablations:
  k_sensitivity:
    benchmark: "mmlu"
    k_values: [5, 10, 20, 40, 60]

pipeline:
  resume: true
  skip_stages: []
  log_level: "INFO"
  checkpoint_dir: "docs/youra_research/h-m2/checkpoints"

paths:
  base_dir: "docs/youra_research/h-m2"
  figures_dir: "docs/youra_research/h-m2/figures"
  hm1_results: "docs/youra_research/h-m1/statistical_results.json"

figures:
  dpi: 150
  color_pile: "#d62728"
  color_deduped: "#1f77b4"
  output_format: "png"

style:
  seaborn_theme: "whitegrid"
  seaborn_context: "paper"
  mpl_backend: "Agg"
```

---

## requirements.txt

```
transformers>=4.35.0
datasets>=2.14.0
torch>=2.0.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
pandas>=1.5.0
```

---

## run_experiment.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python pipeline.py "$@"
```

Run options:
```
python pipeline.py                           # resume from checkpoints (default)
python pipeline.py --no-resume               # rerun from scratch
python pipeline.py --skip run_ablations      # skip ablation stage
python pipeline.py --device cpu              # CPU-only (1B model only)
```

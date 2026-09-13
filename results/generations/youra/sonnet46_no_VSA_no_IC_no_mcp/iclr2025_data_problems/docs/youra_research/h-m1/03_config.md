# Config: H-M1
# Deduplication N-gram Contamination — Mechanism Verification

**Hypothesis:** H-M1 (MECHANISM / FULL tier)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: Dataclass-first Config (single source of truth in config.py)
Applied: Constants Module Pattern (all magic numbers centralized)
Applied: Checkpoint-Resume Pipeline Pattern (stage-level resume flags)
Applied: Seaborn Theme Config Pattern (centralized figure style settings)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: patterns found from base code (Serena MCP unavailable — derived from architecture.md Serena findings)
**Config Files Found**: `docs/youra_research/h-e1/code/` — flat module structure, constants at module top, matplotlib Agg backend, sig_stars() helper
**Pattern Used**: dataclass

---

## Main Configuration

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    # Corpus
    pile_hf_id: str = "EleutherAI/pile"
    dedup_hf_id: str = "EleutherAI/the_pile_deduplicated"

    # Sampling
    n_removed: int = 10_000
    n_retained: int = 10_000
    random_seed: int = 42

    # N-gram
    ngram_n: int = 13

    # Benchmarks
    benchmarks: list[str] = field(default_factory=lambda: ["mmlu", "hellaswag", "arc_challenge", "winogrande"])

    # Statistics
    alpha: float = 0.05
    n_benchmarks: int = 4             # for Bonferroni
    corrected_alpha: float = 0.0125   # alpha / n_benchmarks

    # Ablations
    ablation_ngram_sizes: list[int] = field(default_factory=lambda: [8, 1])
    ablation_extra_benchmarks: list[str] = field(default_factory=lambda: ["arc_easy"])

    # Resources
    n_workers: int = 4
    batch_size: int = 1_000
    memory_limit_gb: float = 14.0     # leave buffer under 16GB NFR-3

    # Paths
    output_dir: Path = Path("docs/youra_research/h-m1")
    checkpoint_dir: Path = Path("docs/youra_research/h-m1/checkpoints")
    figures_dir: Path = Path("docs/youra_research/h-m1/figures")

    # Pipeline stages
    skip_stages: list[str] = field(default_factory=list)
    resume: bool = True

    # Logging
    log_level: str = "INFO"


CONFIG = ExperimentConfig()
```

---

## A-8: Visualizer Config [Complexity: 11, Budget: 2 subtasks]

Applied: Seaborn Theme Config Pattern

### C-8-1: Figure Configuration

```python
@dataclass
class FigureConfig:
    dpi: int = 150
    bar_figsize: tuple[float, float] = (10, 6)
    violin_figsize: tuple[float, float] = (12, 6)
    rank_figsize: tuple[float, float] = (6, 6)
    subset_figsize: tuple[float, float] = (12, 7)
    color_removed: str = "#d62728"   # red
    color_retained: str = "#1f77b4"  # blue
    sig_thresholds: tuple[float, float, float] = (0.001, 0.01, 0.05)
    sig_markers: tuple[str, str, str, str] = ("***", "**", "*", "ns")
    output_format: str = "png"
    ci: float = 0.95
    out_bar: str = "figures/fig_overlap_comparison.png"
    out_violin: str = "figures/fig_overlap_distributions.png"
    out_rank: str = "figures/fig_rank_correlation.png"
    out_subset: str = "figures/fig_subset_breakdown.png"
```

### C-8-2: Style Configuration

```python
@dataclass
class StyleConfig:
    seaborn_theme: str = "whitegrid"
    seaborn_context: str = "paper"
    font_size_title: int = 13
    font_size_axis: int = 11
    font_size_tick: int = 9
    font_size_annot: int = 10
    axis_labels: dict[str, str] = field(default_factory=lambda: {
        "mmlu": "MMLU",
        "hellaswag": "HellaSwag",
        "arc_challenge": "ARC-Challenge",
        "winogrande": "WinoGrande",
        "arc_easy": "ARC-Easy",
    })
    title_bar: str = "13-gram Overlap: Removed vs Retained Docs"
    title_violin: str = "Overlap Distribution by Benchmark"
    title_rank: str = "Expected Contamination Rank vs Observed Overlap Diff"
    title_subset: str = "Mean Removed-Doc Overlap by Pile Subset"
    mpl_backend: str = "Agg"
```

### Subtasks [2/2 used]

| ID | Parent Epic | Subtask | Description |
|----|-------------|---------|-------------|
| C-8-1 | A-8 | Figure config | FigureConfig dataclass: DPI, sizes, colors, significance markers, output paths |
| C-8-2 | A-8 | Style config | StyleConfig dataclass: seaborn theme/context, font sizes, axis label map, title templates |

---

## A-9: Pipeline Orchestrator Config [Complexity: 11, Budget: 2 subtasks]

Applied: Checkpoint-Resume Pipeline Pattern

### C-9-1: Pipeline Stage Configuration

```python
# Stage names (order matches pipeline execution)
PIPELINE_STAGES = [
    "hash_diff",
    "sample",
    "ngrams",
    "overlaps",
    "stats",
    "ablations",
    "figures",
]

@dataclass
class PipelineConfig:
    stages: list[str] = field(default_factory=lambda: list(PIPELINE_STAGES))
    skip_stages: list[str] = field(default_factory=list)
    checkpoint_dir: Path = Path("docs/youra_research/h-m1/checkpoints")
    resume: bool = True
    log_level: str = "INFO"   # DEBUG for verbose stage output
    checkpoint_files: dict[str, str] = field(default_factory=lambda: {
        "hash_diff":  "removed_hashes.json",
        "sample":     "sampled_docs.json",
        "ngrams":     "ngram_sets.pkl",
        "overlaps":   "overlap_scores.json",
        "stats":      "statistical_results.json",
        "ablations":  "ablation_results.json",
    })
```

### C-9-2: Resource Configuration

```python
@dataclass
class ResourceConfig:
    n_workers: int = 4          # multiprocessing.Pool workers for overlap computation
    batch_size: int = 1_000     # docs per streaming batch
    memory_limit_gb: float = 14.0
    random_seed: int = 42
```

### Subtasks [2/2 used]

| ID | Parent Epic | Subtask | Description |
|----|-------------|---------|-------------|
| C-9-1 | A-9 | Pipeline stage config | PipelineConfig: stage list, skip_stages, checkpoint paths, resume flag, log level |
| C-9-2 | A-9 | Resource config | ResourceConfig: n_workers, batch_size, memory_limit_gb, random_seed |

---

## YAML Config Schema (experiment_config.yaml)

```yaml
experiment:
  hypothesis_id: "h-m1"
  name: "Deduplication N-gram Contamination — Mechanism Verification"

corpus:
  pile_hf_id: "EleutherAI/pile"
  dedup_hf_id: "EleutherAI/the_pile_deduplicated"

sampling:
  n_removed: 10000
  n_retained: 10000
  random_seed: 42

ngram:
  n: 13

benchmarks:
  tasks: [mmlu, hellaswag, arc_challenge, winogrande]

statistics:
  alpha: 0.05
  n_benchmarks: 4
  corrected_alpha: 0.0125

ablations:
  ngram_sizes: [8, 1]
  extra_benchmarks: [arc_easy]

resources:
  n_workers: 4
  batch_size: 1000
  memory_limit_gb: 14.0

pipeline:
  resume: true
  skip_stages: []
  log_level: "INFO"
  checkpoint_dir: "docs/youra_research/h-m1/checkpoints"

paths:
  output_dir: "docs/youra_research/h-m1"
  figures_dir: "docs/youra_research/h-m1/figures"

figures:
  dpi: 150
  color_removed: "#d62728"
  color_retained: "#1f77b4"
  output_format: "png"

style:
  seaborn_theme: "whitegrid"
  seaborn_context: "paper"
  mpl_backend: "Agg"
```

---

## requirements.txt

```
datasets>=2.14.0
lm-eval>=0.4.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
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
python pipeline.py                  # resume from checkpoints (default)
python pipeline.py --no-resume      # rerun from scratch
python pipeline.py --skip stats     # skip a stage
```

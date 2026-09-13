# Configuration: H-M1 (RLHF Reward Signal Conflation Analysis)

Applied: Dataclass config with `field(default_factory=...)` for mutable list defaults (reused from H-E1 pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from actual H-E1 code (`h-e1/code/config.py`), not from H-E1's `03_config.md` spec
**Config Files Found**: `h-e1/code/config.py` (`ExperimentConfig` dataclass, single `CONFIG` instance)
**Pattern Used**: dataclass

**Field mismatch found**: H-E1 code uses `batch_size: int = 8` — the H-M1 architecture doc (03_architecture.md) states 16. Using **8** here (verified actual code value) for consistency with reused H-E1 inference infra.

---

## Inherited Configuration (Base Hypothesis H-E1)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    datasets: List[str] = field(default_factory=lambda: ["truthfulqa", "mmlu_moral", "anthropic_hh"])
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])
    primary_model_index: int = 0
    batch_size: int = 8
    device: str = "cuda"
    seed: int = 42
    results_path: str = "outputs/results.json"
```

H-M1 reuses `datasets`, `models`, `primary_model_index`, `batch_size`, `seed` verbatim (identical benchmarks/models per architecture doc). H-M1 does NOT need `inversion_threshold`, `k_range`, `default_k`, `silhouette_gate` (clustering-specific, H-E1 only) — reads H-E1's cluster labels from `results.json` instead of reclustering.

---

## M-1: Config + H-E1 Integration [Complexity: 8, Budget: 4]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class M1Config:
    # Inherited from H-E1 (must match exactly for data/model reuse)
    datasets: List[str] = field(default_factory=lambda: ["truthfulqa", "mmlu_moral", "anthropic_hh"])
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ])
    primary_model_index: int = 0
    batch_size: int = 8
    device: str = "cuda"
    seed: int = 42

    # H-M1 specific
    overlap_gate: float = 0.7
    mean_diff_gate: float = 0.1
    overlap_fail_gate: float = 0.5
    mean_diff_fail_gate: float = 0.2
    correlation_supporting_threshold: float = 0.3
    bidir_score_threshold: int = 1  # ABL-1 sweeps: 1, 2, 3
    hist_bins: int = 50

    # Paths
    he1_results_path: str = "../../h-e1/code/outputs/results.json"
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"

CONFIG = M1Config()
```

### YAML Schema (optional export)

```yaml
datasets: [truthfulqa, mmlu_moral, anthropic_hh]
models:
  - meta-llama/Llama-2-7b-chat-hf
  - meta-llama/Llama-2-13b-chat-hf
  - mistralai/Mistral-7B-Instruct-v0.2
primary_model_index: 0
batch_size: 8
device: cuda
seed: 42
overlap_gate: 0.7
mean_diff_gate: 0.1
bidir_score_threshold: 1
he1_results_path: ../../h-e1/code/outputs/results.json
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Define M1Config | dataclass with inherited + new fields |
| C-M1-2 | Load H-E1 modules | sys.path insert or copy `data.py`/`inference.py` from h-e1/code |
| C-M1-3 | Load H-E1 results.json | parse `per_task[].{task_id, cluster_label}` |
| C-M1-4 | Validate config | assert gate thresholds, dataset/model list non-empty |

---

## M-2: Task Classifier [Complexity: 6, Budget: 4]

**Applied**: Feature-based keyword scoring (from architecture doc)

### Configuration (Python Dataclass)

```python
@dataclass
class ClassifierConfig:
    user_belief_markers: List[str] = field(default_factory=lambda: [
        "you think", "your opinion", "do you believe"
    ])
    context_markers: List[str] = field(default_factory=lambda: [
        "given that", "considering", "in this situation"
    ])
    hedge_markers: List[str] = field(default_factory=lambda: [
        "might", "could", "possibly", "it depends"
    ])
    threshold: int = 1  # sum(features) >= threshold -> Type B

CLASSIFIER_CONFIG = ClassifierConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | compute_bidir_features | 3 boolean marker checks per task |
| C-M2-2 | classify_task_type | threshold-based A/B decision |
| C-M2-3 | classify_all_tasks | batch classify 2212 tasks |
| C-M2-4 | Log classification counts | Type A vs Type B split for NFR-2 |

---

## M-3: Confidence Extraction Wrapper [Complexity: 9, Budget: 4]

**Applied**: Length-normalized logprob confidence extraction (H-E1 `inference.py`, reused directly)

### Configuration

Uses `M1Config.batch_size`, `M1Config.models`, `M1Config.device` (no new config class — reuses `CONFIG`).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M3-1 | extract_confidence_for_tasks | wrap `get_length_normalized_logprob`, `confidence=exp(logprob_norm)` |
| C-M3-2 | run_all_models_confidence | loop over 3 models, `load_model` per model |
| C-M3-3 | Batch inference loop | batch_size=8, float16, device_map="auto" |
| C-M3-4 | Persist per-model confidence dict | `{model_id: {task_id: confidence}}` |

---

## M-4: Overlap + Gate Analysis [Complexity: 7, Budget: 4]

**Applied**: Histogram-intersection distribution overlap (scipy/numpy standard)

### Configuration

Uses `M1Config.overlap_gate`, `mean_diff_gate`, `overlap_fail_gate`, `mean_diff_fail_gate`, `hist_bins`.

```python
gate_pass = (overlap > CONFIG.overlap_gate) or (mean_diff < CONFIG.mean_diff_gate)
gate_fail = (overlap < CONFIG.overlap_fail_gate) and (mean_diff > CONFIG.mean_diff_fail_gate)
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-1 | distribution_overlap | histogram intersection, bins=50 |
| C-M4-2 | mean_confidence_diff | `abs(mean(dist_a) - mean(dist_b))` |
| C-M4-3 | analyze_conflation | combine overlap+diff, apply gate logic |
| C-M4-4 | Log gate decision | PASS/FAIL/inconclusive per criteria |

---

## M-5: Cluster Correlation Analysis [Complexity: 5, Budget: 3]

### Configuration

Uses `M1Config.correlation_supporting_threshold` (0.3), `he1_results_path`.

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M5-1 | cluster_task_correlation | `scipy.stats.pointbiserialr(cluster_labels, task_type_binary)` |
| C-M5-2 | Align task_id ordering | match H-E1 cluster_label task_ids to H-M1 task list |
| C-M5-3 | Report r, p vs supporting threshold | flag "supporting" if r > 0.3 |

---

## M-6: Cross-Model + Per-Dataset Analysis [Complexity: 8, Budget: 4]

### Configuration

No new fields — reuses `CONFIG.models`, `CONFIG.datasets`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M6-1 | cross_model_overlap | overlap score per model, 3 models |
| C-M6-2 | per_dataset_overlap (ABL-3) | overlap per source_dataset (truthfulqa/mmlu_moral/anthropic_hh) |
| C-M6-3 | Aggregate into dict | `{model_id: overlap}`, `{dataset: overlap}` |
| C-M6-4 | Consistency check | flag if cross-model overlap variance is high |

---

## M-7: Classification Threshold Ablation [Complexity: 7, Budget: 3]

**Applied**: Parameter sweep on existing pipeline (not separate architecture)

### Configuration (Python Dataclass)

```python
@dataclass
class AblationConfig:
    threshold_sweep: List[int] = field(default_factory=lambda: [1, 2, 3])  # ABL-1
    single_feature_names: List[str] = field(default_factory=lambda: [
        "user_belief_reference", "context_dependent", "hedged_answer"
    ])  # ABL-2

ABLATION_CONFIG = AblationConfig()
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M7-1 | ABL-1 threshold sweep | rerun classify+overlap for threshold in [1,2,3] |
| C-M7-2 | ABL-2 single-feature isolation | classify using only 1 marker set at a time |
| C-M7-3 | Aggregate ablation results | table of overlap/mean_diff per variant |

---

## M-8: Visualization Suite [Complexity: 6, Budget: 4]

### Configuration

```python
@dataclass
class VizConfig:
    figsize: tuple = (8, 6)
    dpi: int = 150
    figures_dir: str = "../figures"
    heatmap_cmap: str = "viridis"

VIZ_CONFIG = VizConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M8-1 | plot_gate_metrics | overlap vs thresholds bar/line |
| C-M8-2 | plot_confidence_histograms | Type A vs Type B overlay |
| C-M8-3 | plot_cross_model_heatmap | 3-model overlap heatmap |
| C-M8-4 | plot_cluster_correlation_scatter | cluster_label vs task_type, annotate r |

---

## M-9: Main Runner + Results Output [Complexity: 9, Budget: 4]

### Configuration

No new fields — orchestrates `CONFIG`, `CLASSIFIER_CONFIG`, `ABLATION_CONFIG`, `VIZ_CONFIG`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M9-1 | Pipeline orchestration | steps 1-8 per architecture `run_experiment.py` |
| C-M9-2 | Results schema assembly | `{gate_pass, overlap, mean_diff, correlation, cross_model, per_dataset, ablations}` |
| C-M9-3 | Write results.json | `CONFIG.results_path` |
| C-M9-4 | Seed + determinism | set `torch.manual_seed`, `np.random.seed` via `CONFIG.seed=42` at start |

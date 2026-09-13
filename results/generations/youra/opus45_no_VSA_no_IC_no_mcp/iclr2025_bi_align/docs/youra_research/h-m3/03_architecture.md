# Architecture: H-M3 Optimization Landscape Attractor Analysis

**Applied**: Multi-seed comparative ML experiment pattern (train N variants, extract behavioral embeddings, cluster + permutation-test)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1, h-m2)
**Status**: Patterns found from base code (read directly via file tool; Serena unavailable in this run environment, so `Read` was used to inspect actual implementation)
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m2/code/`
**Findings**:
- H-M2 (`dpo_train.py`, `config.py`) implements real DPO policy training via `trl.DPOTrainer` — directly reusable for H-M3 DPO seeds.
- **H-M1 (`train.py`, `config.py`) trains a *reward model* (`RewardTrainer`, `SEQ_CLS`, `AutoModelForSequenceClassification`), NOT a generative RLHF policy despite the brief's `PPOConfig` reference.** H-M3 requires a generative policy per RLHF seed to extract hidden states and generate responses. This is a gap between spec and actual code — architecture below adds a thin PPO policy trainer module rather than reusing H-M1 code directly. Flagged as open risk (see Error Handling).

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| HM2Config, get_dpo_config, get_peft_config | `from h_m2.config import HM2Config, get_dpo_config, get_peft_config` | `docs/youra_research/h-m2/code/config.py` |
| build_dpo_trainer, train_dpo | `from h_m2.dpo_train import build_dpo_trainer, train_dpo` | `docs/youra_research/h-m2/code/dpo_train.py` |
| load_hh_rlhf_splits, preprocess_for_reward_trainer | `from h_m2.data import load_hh_rlhf_splits` | `docs/youra_research/h-m2/code/data.py` |
| set_seed (pattern reference only) | n/a — reimplemented locally | `docs/youra_research/h-m1/code/config.py:89-95` |

**Verified from**: actual `h-m1/code/` and `h-m2/code/` files (not `03_architecture.md` specs, which do not exist for those hypotheses in this pass).

**Note**: RLHF policy training has no reusable module from H-M1 (reward-model only). H-M3 implements its own minimal PPO trainer (`training/rlhf_seed_trainer.py`) using `trl.PPOTrainer` + the H-M1 reward model checkpoint (`h-m1/code/reward_model_h-m1_quick/final`) as the reward signal.

---

## Data Flow

```
SEEDS[42,137,256,512,1024] x METHODS[dpo,rlhf]
        |
        v
MultiSeedTrainer.run_all()
   ├─ dpo_seed_trainer.py   -> h-m2.dpo_train (reused)
   └─ rlhf_seed_trainer.py  -> trl.PPOTrainer + h-m1 reward model
        |
        v  (10 checkpoints -> outputs/models/{method}_seed{seed}/)
        |
BehaviorExtractor.run(probe_prompts[1000])
   ├─ generate_responses()      -> outputs/responses.jsonl
   └─ extract_embeddings()      -> outputs/behavior_embeddings.npy
        |
        v
ClusteringAnalyzer.run(embeddings, method_labels, seed_labels)
   ├─ similarity_matrix()
   ├─ within_vs_cross()
   ├─ kmeans_alignment()
   └─ silhouette()              -> outputs/clustering_metrics.json
        |
        v
StatisticalValidator.run(embeddings, method_labels)
   ├─ permutation_test()
   ├─ cohens_d()
   └─ bootstrap_ci()            -> merges into clustering_metrics.json
        |
        v
AttractorVisualizer.run(embeddings, method_labels, seed_labels)
   ├─ tsne_plot()                -> outputs/attractor_visualization.png
   └─ similarity_heatmap()       -> outputs/similarity_heatmap.png
```

---

## Modules

### MultiSeedTrainer (`src/training/multi_seed_trainer.py`)

**Dependencies**: DpoSeedTrainer, RlhfSeedTrainer, seed_utils

```python
class MultiSeedTrainer:
    def __init__(self, config: "ExperimentConfig"): ...
    def run_all(self) -> dict[str, str]:
        """Returns {model_id: checkpoint_path} for all 10 seed/method combos."""
    def run_one(self, method: str, seed: int) -> str:
        """Trains single seed/method, returns checkpoint_path."""
```

### DpoSeedTrainer (`src/training/dpo_seed_trainer.py`)

**Dependencies**: h_m2.config, h_m2.dpo_train, h_m2.data, seed_utils

```python
def train_dpo_seed(seed: int, output_root: str) -> str:
    """Wraps h_m2.dpo_train.build_dpo_trainer/train_dpo with seed override. Returns checkpoint path."""
```

### RlhfSeedTrainer (`src/training/rlhf_seed_trainer.py`)

**Dependencies**: trl.PPOTrainer, h-m1 reward model checkpoint, seed_utils

```python
def train_rlhf_seed(seed: int, output_root: str, reward_model_path: str) -> str:
    """Trains policy via PPO using frozen H-M1 reward model. Returns checkpoint path."""
```

### seed_utils (`src/training/seed_utils.py`)

```python
def set_seed(seed: int) -> None: ...
def model_id(method: str, seed: int) -> str:  # e.g. "dpo_seed42"
```

### BehaviorExtractor (`src/analysis/behavior_extractor.py`)

**Dependencies**: transformers, torch

```python
class BehaviorExtractor:
    def __init__(self, model_paths: dict[str, str], tokenizer_name: str, device: str): ...
    def load_probe_prompts(self, path: str, n_probes: int = 1000) -> list[dict]: ...
    def generate_responses(self, prompts: list[dict]) -> dict[str, list[str]]:
        """{model_id: [response, ...]}"""
    def extract_embeddings(self, prompts: list[dict]) -> dict[str, "np.ndarray"]:
        """{model_id: (n_probes, hidden_dim) array}, mean-pooled last hidden layer."""
```

### ClusteringAnalyzer (`src/analysis/clustering_analyzer.py`)

**Dependencies**: sklearn, scipy

```python
class ClusteringAnalyzer:
    def __init__(self, embeddings: dict[str, "np.ndarray"], method_labels: dict[str, str]): ...
    def similarity_matrix(self) -> "np.ndarray": ...
    def within_vs_cross(self) -> dict:
        """{within_dpo_mean, within_rlhf_mean, cross_method_mean, clustering_gap}"""
    def kmeans_alignment(self, k: int = 2) -> dict:
        """{cluster_labels, alignment_score}"""
    def silhouette(self) -> dict:
        """{silhouette_score, dpo_silhouette, rlhf_silhouette}"""
```

### StatisticalValidator (`src/analysis/statistical_validator.py`)

**Dependencies**: scipy, numpy

```python
class StatisticalValidator:
    def __init__(self, embeddings: "np.ndarray", method_labels: list[str]): ...
    def permutation_test(self, n_iter: int = 1000) -> dict:
        """{observed_gap, p_value, significant}"""
    def cohens_d(self, within: list[float], cross: list[float]) -> dict:
        """{cohens_d, effect_significant}"""
    def bootstrap_ci(self, values: list[float], n_iter: int = 1000, alpha: float = 0.05) -> tuple[float, float]: ...
```

### AttractorVisualizer (`src/visualization/attractor_visualizer.py`)

**Dependencies**: sklearn.manifold.TSNE, matplotlib

```python
class AttractorVisualizer:
    def __init__(self, embeddings: "np.ndarray", method_labels: list[str], seed_labels: list[int]): ...
    def tsne_plot(self, out_path: str) -> None: ...
    def similarity_heatmap(self, similarity_matrix: "np.ndarray", model_ids: list[str], out_path: str) -> None: ...
```

### ExperimentConfig (`configs/experiment_config.yaml` + `src/config.py`)

```python
@dataclass
class ExperimentConfig:
    seeds: tuple[int, ...] = (42, 137, 256, 512, 1024)
    methods: tuple[str, ...] = ("dpo", "rlhf")
    base_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    n_probes: int = 1000
    reward_model_path: str = "../h-m1/code/reward_model_h-m1_quick/final"
    output_root: str = "./outputs"
    silhouette_threshold: float = 0.1
    clustering_gap_threshold: float = 0.05
    cohens_d_threshold: float = 0.3
    p_value_threshold: float = 0.05
```

---

## Error Handling Strategy

| Failure | Handling |
|---------|----------|
| Single seed training crash (OOM/divergence) | Catch per `run_one` call in `MultiSeedTrainer.run_all`; log + skip; continue remaining seeds; require >=3/5 seeds per method to proceed to analysis |
| RLHF module gap (H-M1 has no policy trainer) | Explicit `RlhfSeedTrainer` built fresh on `trl.PPOTrainer`; fail fast at startup if `reward_model_path` checkpoint missing (no silent fallback) |
| Embedding extraction OOM | Batch prompts (configurable `batch_size`), `torch.no_grad()`, move embeddings to CPU immediately per prompt |
| Missing/corrupt checkpoint at analysis time | `BehaviorExtractor.__init__` validates all `model_paths` exist before running; raises `FileNotFoundError` listing missing model_ids |
| Degenerate clustering (silhouette undefined, <2 classes) | `ClusteringAnalyzer` checks `len(set(method_labels)) >= 2` before calling sklearn; raises `ValueError` with diagnostic |
| Permutation test / bootstrap non-determinism | Fixed `np.random.seed` per config; results reproducible run-to-run |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + seed utils | ExperimentConfig, set_seed, model_id helpers | 6 | 1+1+2+2 |
| A-2 | DPO seed trainer | Wrap h-m2 DPOTrainer with seed loop, checkpoint mgmt | 9 | 2+3+2+2 |
| A-3 | RLHF seed trainer | New PPOTrainer wrapper using H-M1 reward model | 14 | 4+4+4+2 |
| A-4 | MultiSeedTrainer orchestration | Loop methods x seeds, error handling, resume support | 10 | 2+3+3+2 |
| A-5 | Probe prompt loader | Sample 1000 probes from HH-RLHF helpful/harmless-base | 5 | 1+1+2+1 |
| A-6 | BehaviorExtractor: generation | Generate responses across 10 models on probe set | 9 | 2+3+2+2 |
| A-7 | BehaviorExtractor: embeddings | Extract mean-pooled last hidden state embeddings | 8 | 2+2+2+2 |
| A-8 | ClusteringAnalyzer | Similarity matrix, within/cross means, k-means, silhouette | 11 | 3+3+3+2 |
| A-9 | StatisticalValidator | Permutation test, Cohen's d, bootstrap CI | 9 | 2+3+2+2 |
| A-10 | AttractorVisualizer | t-SNE plot + similarity heatmap | 6 | 2+1+2+1 |
| A-11 | run_full_experiment.py orchestration script | Wire all phases, write clustering_metrics.json | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-6, A-8, A-9], Low(4-8): [A-1, A-5, A-7, A-10, A-11]

---

## File Structure

```
h-m3/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── training/
│   │   ├── multi_seed_trainer.py
│   │   ├── dpo_seed_trainer.py
│   │   ├── rlhf_seed_trainer.py
│   │   └── seed_utils.py
│   ├── analysis/
│   │   ├── behavior_extractor.py
│   │   ├── clustering_analyzer.py
│   │   └── statistical_validator.py
│   └── visualization/
│       └── attractor_visualizer.py
├── configs/
│   └── experiment_config.yaml
├── scripts/
│   ├── train_all_seeds.py
│   ├── extract_behaviors.py
│   ├── analyze_clusters.py
│   └── run_full_experiment.py
└── outputs/
    ├── models/
    ├── behavior_embeddings.npy
    ├── clustering_metrics.json
    ├── attractor_visualization.png
    └── similarity_heatmap.png
```

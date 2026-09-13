# Configuration: H-M3 Attractor Analysis

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (sibling hypotheses h-m1, h-m2)
**Status**: existing patterns found — dataclass config confirmed in `h-m1/code/config.py`, `h-m2/code/config.py`
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`, `docs/youra_research/h-m2/code/config.py`
**Pattern Used**: dataclass (`@dataclass` + field defaults), matches H-M2's `HM2Config`

H-M3 reuses H-M1 (RLHF) and H-M2 (DPO) training configs directly — no retraining config duplication. This file adds only the **multi-seed orchestration, probe/embedding, clustering, and threshold** config that's new to H-M3.

---

## A-1: Multi-Seed Training Orchestration

**Applied**: Standard PyTorch defaults; reuses H-M1/H-M2 dataclasses per-seed

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM3TrainingConfig:
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])

    # DPO (mirrors HM2Config fields)
    dpo_beta: float = 0.1
    dpo_lr: float = 5e-7
    dpo_epochs: int = 1
    dpo_batch_size: int = 2
    dpo_grad_accum: int = 8

    # RLHF/PPO
    rlhf_lr: float = 1.41e-5
    rlhf_ppo_epochs: int = 4
    rlhf_batch_size: int = 32
    rlhf_mini_batch_size: int = 4

    # LoRA (shared across DPO/RLHF policy models)
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"]
    )

    model_dir: str = "./h-m3_models"
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Seed loop driver | Iterate 5 seeds × 2 methods, invoke H-M1/H-M2 train fns with `seed` override |
| C-1-2 | Checkpoint naming | Save to `{model_dir}/{method}_seed{seed}/final` |

---

## A-2: Model Config

**Applied**: Standard PyTorch/HF defaults

```python
@dataclass
class HM3ModelConfig:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    max_length: int = 512
    bf16: bool = True
    gradient_checkpointing: bool = True
```

### Subtasks [0/1 used]
_None — reused directly by A-1 training config, no separate loading logic._

---

## A-3: Dataset Config

**Applied**: Standard HF datasets defaults

```python
@dataclass
class HM3DatasetConfig:
    dataset_name: str = "Anthropic/hh-rlhf"
    subsets: List[str] = field(default_factory=lambda: ["helpful-base", "harmless-base"])
    n_probes: int = 1000
    probe_seed: int = 42
```

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Probe sampler | Sample `n_probes` prompts from `subsets` using `probe_seed` (fixed, independent of training seeds) |

---

## A-4: Analysis Config

**Applied**: scikit-learn clustering/silhouette defaults; standard permutation test defaults

```python
@dataclass
class HM3AnalysisConfig:
    n_permutations: int = 1000
    k_clusters: int = 2
    embedding_batch_size: int = 16
    generation_max_length: int = 256
    embedding_layer: str = "last_hidden_state"
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | Response generation | Generate responses for all 10 models × `n_probes`, batched at `embedding_batch_size` |
| C-4-2 | Embedding extraction | Extract last-layer hidden states, mean-pool over tokens |
| C-4-3 | Clustering + stats | Cosine similarity matrix, K-means(`k_clusters`), silhouette, permutation test (`n_permutations`), Cohen's d |

---

## A-5: Thresholds

**Applied**: Direct from PRD success criteria (Section 3)

```python
@dataclass
class HM3Thresholds:
    clustering_gap_min: float = 0.05
    silhouette_min: float = 0.1
    cohens_d_min: float = 0.3
    p_value_max: float = 0.05
```

### Subtasks [0/1 used]
_None — pure constants consumed by A-4 validation logic._

---

## A-6: Output Config

**Applied**: Standard local filesystem output

```python
@dataclass
class HM3OutputConfig:
    output_dir: str = "./h-m3/outputs"
    model_dir: str = "./h-m3_models"
    save_embeddings: bool = True
    embeddings_path: str = "./h-m3/outputs/behavior_embeddings.npy"
    metrics_path: str = "./h-m3/outputs/clustering_metrics.json"
    visualization_path: str = "./h-m3/outputs/attractor_visualization.png"
```

### Subtasks [0/1 used]
_None — path constants used by A-1/A-4 outputs._

---

## Validation Rules

- `seeds` must have exactly 5 elements (per PRD FR-1); each produces 1 DPO + 1 RLHF model → 10 total checkpoints.
- `methods` fixed to `["dpo", "rlhf"]` — no other methods in scope (PRD Section 7: no hyperparameter sweeps).
- `n_probes == 1000` fixed; `probe_seed` is independent of and must not be overwritten by training `seeds`.
- `k_clusters == 2` (method-based clustering only, per PRD FR-3).
- All 4 thresholds in A-5 are PRIMARY success criteria (PRD Section 3) — validation fails if any is not met.
- `bf16=True` and `gradient_checkpointing=True` required for A100 80GB memory budget (PRD TR-1).
- Directories (`output_dir`, `model_dir`) auto-created if missing; no manual pre-creation required.

---

*Generated by Phase 3 Implementation Planning (Configuration Agent)*

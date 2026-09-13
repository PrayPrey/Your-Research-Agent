# Configuration: H-E1 — Locality Score Oracle Existence Proof

**Generated:** 2026-05-20
**Hypothesis:** h-e1 (EXISTENCE / MUST_WORK)
**Tier:** LIGHT (single GPU, minimal infrastructure)

Applied: Standard PyTorch dataclass pattern (Archon KB no domain match — all diffusion domain, similarity 0.36–0.47)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing codebase
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## 1. ExperimentConfig Dataclass (`code/config.py`)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class ExperimentConfig:
    # ── Model ──────────────────────────────────────────────────────────────
    model_id: str = "ByteDance-Seed/BFS-Prover-V2-7B"
    dtype: str = "bfloat16"

    # ── DPO Training Hyperparameters ────────────────────────────────────────
    # Non-standard: beta=10.0 (typical DPO range 0.1–0.5); BFS-Prover uses
    # high beta for conservative SFT deviation in theorem proving context.
    beta: float = 10.0
    lr_start: float = 5e-6
    lr_end: float = 5e-7
    batch_size: int = 16
    grad_accum_steps: int = 1        # set to 2 if OOM on single GPU
    num_epochs: int = 1
    seed: int = 1
    weight_decay: float = 0.01
    adam_betas: Tuple[float, float] = (0.9, 0.999)

    # ── Hard Subset Configuration ───────────────────────────────────────────
    pass_at_1_threshold: float = 0.20
    cold_start_rollouts: int = 16

    # ── Experiment Conditions ───────────────────────────────────────────────
    conditions: List[str] = field(default_factory=lambda: ["A", "B", "P"])

    # ── Tactic Taxonomy (IMMUTABLE — must not change between conditions) ────
    # Pre-specified before any training per NFR-4.
    taxonomy: Dict[str, List[str]] = field(default_factory=lambda: {
        "type_error":      ["type mismatch", "application type mismatch"],
        "undefined_name":  ["unknown identifier", "unknown tactic"],
        "tactic_failure":  ["tactic failed", "simp made no progress"],
    })

    # ── Gate Configuration ──────────────────────────────────────────────────
    gate_alpha: float = 0.05
    gate_direction: str = "greater"   # one-sided t-test: LS_A > LS_P

    # ── BFS Parameters (from BFS-Prover-V2, reference only) ────────────────
    bfs_alpha_levels: List[float] = field(default_factory=lambda: [0.0, 0.5, 1.0])
    tactic_budget: str = "2048x2x600"

    # ── Path Configuration ──────────────────────────────────────────────────
    output_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
    checkpoint_dir: str = "h-e1/checkpoints"
    minif2f_dataset_id: str = "Tonic/MiniF2F"
    vericoding_data_path: str = "data/vericoding"

    # ── GPU / Compute ───────────────────────────────────────────────────────
    cuda_visible_devices: str = ""   # MUST be set before training (e.g. "0")
    mixed_precision: str = "bf16"
    max_seq_len: int = 2048
```

---

## 2. YAML Configuration Schema (`experiment_config.yaml`)

```yaml
# H-E1 Experiment Configuration
# All values match ExperimentConfig dataclass defaults.
# Override any field here; load with config_from_yaml().

# ── Model ──────────────────────────────────────────────────────────────────
model_id: "ByteDance-Seed/BFS-Prover-V2-7B"  # HuggingFace model ID
dtype: "bfloat16"                              # Mixed precision dtype

# ── DPO Training Hyperparameters ───────────────────────────────────────────
# Source: BFS-Prover arXiv:2502.03438 (beta, lr, batch) + eric-mitchell/DPO (epochs)
beta: 10.0        # DPO regularization (high: conservative SFT deviation)
lr_start: 5.0e-6  # Linear decay start LR
lr_end: 5.0e-7    # Linear decay end LR
batch_size: 16    # Per-GPU batch size (set grad_accum_steps=2 if OOM)
grad_accum_steps: 1
num_epochs: 1
seed: 1
weight_decay: 0.01
adam_betas: [0.9, 0.999]

# ── Hard Subset ─────────────────────────────────────────────────────────────
pass_at_1_threshold: 0.20   # Problems with pass@1 < this form hard subset
cold_start_rollouts: 16     # Rollouts per problem for cold-start SFT eval

# ── Experiment Conditions ───────────────────────────────────────────────────
# A = grounded (Lean4 compiler error negatives)
# B = ungrounded (failed-branch tactic, same state, no error info)
# P = permutation control (shuffled error message tokens)
conditions: ["A", "B", "P"]

# ── Tactic Taxonomy (IMMUTABLE) ─────────────────────────────────────────────
taxonomy:
  type_error:      ["type mismatch", "application type mismatch"]
  undefined_name:  ["unknown identifier", "unknown tactic"]
  tactic_failure:  ["tactic failed", "simp made no progress"]

# ── Gate ────────────────────────────────────────────────────────────────────
gate_alpha: 0.05         # Significance level for one-sided t-test
gate_direction: "greater"  # scipy alternative="greater": LS_A > LS_P

# ── BFS Parameters (reference only — not used in training loop) ─────────────
bfs_alpha_levels: [0.0, 0.5, 1.0]
tactic_budget: "2048x2x600"

# ── Paths ────────────────────────────────────────────────────────────────────
output_dir: "h-e1/results"
figures_dir: "h-e1/figures"
checkpoint_dir: "h-e1/checkpoints"
minif2f_dataset_id: "Tonic/MiniF2F"
vericoding_data_path: "data/vericoding"

# ── GPU / Compute ─────────────────────────────────────────────────────────────
cuda_visible_devices: ""   # REQUIRED: set to GPU ID before running (e.g. "0")
mixed_precision: "bf16"
max_seq_len: 2048
```

---

## 3. Environment Setup

### `requirements.txt`

```
torch>=2.0.0
transformers>=4.40.0
datasets>=2.18.0
lean-dojo>=2.0.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
accelerate>=0.27.0
trl>=0.8.0
deepspeed>=0.14.0
```

### `environment.yaml` (conda)

```yaml
name: h-e1
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - cudatoolkit=12.0
  - pip
  - pip:
    - torch>=2.0.0
    - transformers>=4.40.0
    - datasets>=2.18.0
    - lean-dojo>=2.0.0
    - scipy>=1.11.0
    - numpy>=1.24.0
    - matplotlib>=3.7.0
    - pyyaml>=6.0
    - accelerate>=0.27.0
    - trl>=0.8.0
    - deepspeed>=0.14.0
```

### Lean 4 Installation (required for LeanDojo)

```bash
# 1. Install elan (Lean version manager)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.elan/env

# 2. Install Lean 4 (version pinned to LeanDojo-v2 compatibility)
elan install leanprover/lean4:v4.3.0
elan default leanprover/lean4:v4.3.0

# 3. Verify
lean --version

# 4. Install lean-dojo Python package (already in requirements.txt)
pip install lean-dojo>=2.0.0
```

---

## 4. Configuration Validation

### Required Fields (must be set before running)

| Field | Validation Rule |
|-------|----------------|
| `cuda_visible_devices` | Must be non-empty string (e.g. "0"); set via `CUDA_VISIBLE_DEVICES` env var |
| `model_id` | Must be a valid HuggingFace model ID; tested with `from_pretrained` |
| `vericoding_data_path` | Directory must exist and contain Lean4-compatible `.jsonl` or similar |
| `output_dir`, `figures_dir`, `checkpoint_dir` | Created automatically if absent |

### Validation Rules

```python
def validate_config(cfg: ExperimentConfig) -> None:
    assert cfg.cuda_visible_devices != "", \
        "CUDA_VISIBLE_DEVICES must be set before training"
    assert 0.0 < cfg.pass_at_1_threshold < 1.0, \
        "pass_at_1_threshold must be in (0, 1)"
    assert cfg.cold_start_rollouts >= 1, \
        "cold_start_rollouts must be >= 1"
    assert cfg.beta > 0.0, "DPO beta must be positive"
    assert cfg.lr_start > cfg.lr_end > 0.0, \
        "lr_start must be > lr_end > 0"
    assert cfg.num_epochs >= 1, "num_epochs must be >= 1"
    assert set(cfg.conditions) <= {"A", "B", "P"}, \
        "conditions must be subset of {A, B, P}"
    assert set(cfg.taxonomy.keys()) == {"type_error", "undefined_name", "tactic_failure"}, \
        "taxonomy keys must not change (NFR-4 immutability)"
    assert cfg.gate_direction == "greater", \
        "gate_direction must be 'greater' for one-sided LS_A > LS_P test"
```

### Configuration Loading Function

```python
import yaml
from dataclasses import fields, asdict


def config_from_yaml(path: str) -> ExperimentConfig:
    with open(path) as f:
        d = yaml.safe_load(f)
    # Convert list fields
    if "adam_betas" in d:
        d["adam_betas"] = tuple(d["adam_betas"])
    if "conditions" in d:
        d["conditions"] = list(d["conditions"])
    if "bfs_alpha_levels" in d:
        d["bfs_alpha_levels"] = list(d["bfs_alpha_levels"])
    valid_keys = {f.name for f in fields(ExperimentConfig)}
    filtered = {k: v for k, v in d.items() if k in valid_keys}
    cfg = ExperimentConfig(**filtered)
    validate_config(cfg)
    return cfg


def config_to_yaml(cfg: ExperimentConfig, path: str) -> None:
    d = asdict(cfg)
    with open(path, "w") as f:
        yaml.dump(d, f, default_flow_style=False)
```

---

## 5. Hyperparameter Source Documentation

| Param | Value | Source |
|-------|-------|--------|
| `beta` | 10.0 | BFS-Prover arXiv:2502.03438 — high beta for conservative SFT deviation in theorem proving |
| `lr_start` | 5e-6 | BFS-Prover-V2 training config (DPO stage) |
| `lr_end` | 5e-7 | BFS-Prover-V2 training config (DPO stage, linear decay) |
| `batch_size` | 16 | BFS-Prover arXiv:2502.03438 |
| `grad_accum_steps` | 1 | Standard (2 if OOM) |
| `num_epochs` | 1 | Step-DPO (dvlab-research) + eric-mitchell/DPO — 1 epoch standard to avoid preference data overfitting |
| `seed` | 1 | EXISTENCE PoC — single run, fixed seed for reproducibility (NFR-1) |
| `weight_decay` | 0.01 | BFS-Prover arXiv:2502.03438; eric-mitchell/DPO reference |
| `adam_betas` | (0.9, 0.999) | BFS-Prover arXiv:2502.03438; AdamW standard |
| `pass_at_1_threshold` | 0.20 | H-E1 hypothesis spec — hard subset definition (02b_verification_plan.md §2.2) |
| `cold_start_rollouts` | 16 | H-E1 hypothesis spec — 16 rollouts sufficient for reliable pass@1 estimate |
| `gate_alpha` | 0.05 | H-E1 MUST_WORK gate — standard statistical significance threshold |
| `max_seq_len` | 2048 | BFS-Prover-V2 tactic sequence length (tactic_budget: 2048×2×600) |
| `bfs_alpha_levels` | [0.0, 0.5, 1.0] | BFS-Prover-V2 `run_local_search.sh` BFS length normalization |
| `tactic_budget` | "2048x2x600" | BFS-Prover-V2 `run_local_search.sh` |

---

## 6. Configuration Across 3 DPO Conditions

All three conditions (A, B, P) share the **identical** ExperimentConfig. The only difference is the DPO pair construction method for the rejected tactic `a_l`.

| Config Field | Condition A | Condition B | Condition P |
|--------------|-------------|-------------|-------------|
| `beta` | 10.0 | 10.0 | 10.0 |
| `lr_start` | 5e-6 | 5e-6 | 5e-6 |
| `lr_end` | 5e-7 | 5e-7 | 5e-7 |
| `batch_size` | 16 | 16 | 16 |
| `num_epochs` | 1 | 1 | 1 |
| `seed` | 1 | 1 | 1 |
| `model_id` | BFS-Prover-V2-7B | BFS-Prover-V2-7B | BFS-Prover-V2-7B |
| **`a_l` source** | Lean4 compiler error tactic at state s | Failed-branch tactic at state s (no error info) | Permuted compiler error tokens at state s |
| State alignment | 100% (s_w == s_l) | 100% (s_w == s_l) | 100% (s_w == s_l) |

**What changes**: only `build_pairs_condition_X()` call in `dpo_pairs.py`
**What stays fixed**: all fields in ExperimentConfig, model, datasets, taxonomy

Each run loads a **fresh copy** of `ByteDance-Seed/BFS-Prover-V2-7B` as both policy init and frozen reference model.

---

## 7. Disk Space and Resource Estimates

| Resource | Size | Notes |
|----------|------|-------|
| BFS-Prover-V2-7B (ref model) | ~14 GB | bfloat16, frozen reference |
| Checkpoint A (DPO condition A) | ~14 GB | saved after training |
| Checkpoint B (DPO condition B) | ~14 GB | saved after training |
| Checkpoint P (DPO control) | ~14 GB | saved after training |
| miniF2F dataset | ~5 MB | 488 problems, HuggingFace |
| Vericoding dataset | ~2 GB | 12,504 problems, Lean4 subset |
| LeanDojo traces (miniF2F) | ~5 GB | per-state extracted triples |
| LeanDojo traces (Vericoding) | ~10–15 GB | larger dataset |
| Results / figures | ~100 MB | JSON results + PNG figures |
| **Total recommended** | **~80–90 GB** | Single A100 (80GB VRAM) for training |

**GPU Memory (per DPO run):**
- 7B bfloat16 policy: ~14 GB
- 7B bfloat16 frozen ref: ~14 GB
- Activations + optimizer states: ~30–40 GB
- Fits on single A100 80GB (with `grad_accum_steps=1`; use `grad_accum_steps=2` + batch_size=8 if OOM)

**Training Time Estimate:**
- Cold-start SFT eval: ~1–2 hours (16 rollouts × ~500 problems)
- LeanDojo tracing: ~2–4 hours
- Each DPO run: ~2–4 hours on A100 (1 epoch, 7B model, hard subset pairs)
- Total: ~10–16 hours end-to-end

---

## Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1 | ExperimentConfig dataclass | Complete `config.py` with all fields, types, defaults, and validation |
| C-E1-2 | YAML schema | `experiment_config.yaml` with all fields, comments, sources |
| C-E1-3 | Environment setup | `requirements.txt`, `environment.yaml`, Lean 4 install instructions |
| C-E1-4 | Config validation | `validate_config()` function with all assertion rules |
| C-E1-5 | Config loading functions | `config_from_yaml()` and `config_to_yaml()` utilities |
| C-E1-6 | Hyperparameter source table | Traceability from each param to source paper/repo |
| C-E1-7 | Condition comparison and resource estimates | Cross-condition config diff table + disk/GPU estimates |

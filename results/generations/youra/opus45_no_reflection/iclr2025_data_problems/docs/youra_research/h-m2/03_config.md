# Config: H-M2

**Type:** MECHANISM (full analysis) — fine-tuning + Hessian curvature comparison, gate is relative-diff threshold.

**Applied**: Standard PyTorch/HuggingFace experiment-config defaults (no matching KB pattern found via Archon search: "Hessian eigenvalue lanczos config").

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Config classes verified from base code (`h-m1/code/config.py`, read directly)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: dataclass

**Findings**: H-M1's `ExperimentConfig` dataclass + `GATE_CONFIG`/`FIGURE_FILES` module-level dict pattern is reused directly. H-M2 replaces sparsity fields with fine-tuning + Hessian/Lanczos/Kronecker fields; no H-M1 fields are directly inherited since H-M1 never fine-tuned models (attention-only extraction), but the config *shape* (single dataclass + two module dicts) carries over unchanged.

---

## A-1/A-2/A-3: Data + Model + Fine-tuning Config

```python
@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    hessian_batch_size: int = 256   # NFR-1: 256-512 samples for Hessian estimation

    # Fine-tuning
    epochs: int = 3
    lr: float = 2e-5

    # Hessian / Lanczos
    lanczos_k: int = 20             # top-k eigenvalues
    lanczos_steps: int = 50         # NFR-1: 40-60 for convergence
    trace_matvecs: int = 100        # matvecs for trace estimate

    # Models
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"

    # Ablations (FR-5)
    seeds: list[int] = field(default_factory=lambda: [42, 43])
    ablation_batch_sizes: list[int] = field(default_factory=lambda: [256, 512])

    # Gate threshold (PRD Success Criteria)
    gate_threshold: float = 0.10    # relative-diff, pass if any primary metric exceeds

    # Repro / device
    device: str = "cuda"            # falls back to "cpu" if unavailable

    # Output paths
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"
    eigenvalues_path: str = "eigenvalues.npz"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | Define `ExperimentConfig` above in `config.py`, incl. checkpoint/output paths |

---

## A-8/A-9/A-10: Gate + Visualization Config

```python
GATE_CONFIG = {"min_relative_diff": 0.10}

FIGURE_FILES = {
    "gate_comparison": "gate_comparison.png",
    "eigenvalue_spectrum": "eigenvalue_spectrum.png",
    "spectral_density": "spectral_density.png",
    "condition_by_layer": "condition_by_layer.png",
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2 | Gate + figure dicts | `GATE_CONFIG` used by `verify.py`; `FIGURE_FILES` used by `visualize.py` output targets |

---

## A-6: Kronecker Fit Config

```python
KRONECKER_LAYER_PREFIXES = {
    "bert": "bert.encoder.layer",     # per-layer attention module prefix
    "gpt2": "transformer.h",
}
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3 | Layer prefix map | Model-specific layer-name prefixes for `kronecker_analysis.py` layer iteration |

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE) — pattern only, no fields directly reused
@dataclass
class ExperimentConfig:  # H-M1 version (attention-extraction, no fine-tuning)
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    seed: int = 42
    device: str = "cuda"
```

H-M2's `ExperimentConfig` reuses the same dataclass shape and `dataset_name`/`dataset_config`/`bert_model_id`/`gpt2_model_id`/`device` field names verbatim; H-M1's single `seed: int` is replaced by `seeds: list[int]` (FR-5.1 requires ≥2 seeds) since H-M2 runs a seed ablation rather than a single deterministic pass.

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation).

---

## Total Subtasks: 3/3 used

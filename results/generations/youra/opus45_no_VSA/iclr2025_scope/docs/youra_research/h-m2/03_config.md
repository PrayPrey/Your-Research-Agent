# Configuration: H-M2 (Robustness of Routing to Paraphrase/Masking)

Applied: Standard PyTorch/sklearn dataclass-config defaults (no strongly relevant KB pattern found; matched H-E1's existing dataclass style for consistency)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from base code — read `docs/youra_research/h-e1/code/config.py` directly (Read tool, file confirmed to exist)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (`Config` dataclass + `CONFIG` instance + gate constants)
**Pattern Used**: dataclass

Architecture doc (`03_architecture.md`) already specifies the exact `MConfig` schema — this file finalizes it and documents inheritance from H-E1.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    dataset_name: str = "Open-Orca/FLAN"
    n_samples: int = 3000
    prefix_chars: int = 256
    train_val_test_split: Tuple[float, float, float] = (0.70, 0.15, 0.15)
    random_state: int = 42
    encoder_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_iter: int = 2000
    solver: str = "lbfgs"
    top_k: int = 3
    task_families: List[str] = field(default_factory=list)
    min_samples_per_class: int = 100

CONFIG = Config()

TOP1_PASS = 0.70
TOP3_PASS = 0.85
TOP3_FAIL = 0.60
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation, not `03_config.md` spec)

**Reuse note**: H-M2 imports `CONFIG` from `h_e1.config` unmodified (`random_state=42` must match for reproducible test-split/task-family reconstruction — see `reuse_probe.py`). No new fields added to `Config`; H-M2 defines its own separate `MConfig` (below) rather than subclassing, since H-M2 params (perturbation/gate) are orthogonal to H-E1's data/encoder params.

---

## A-2: Config module [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch/sklearn dataclass defaults; thresholds fixed per architecture spec (non-standard, PRD-mandated — not tunable).

### Configuration (Python Dataclass)

```python
"""H-M2 Experiment Configuration"""
from dataclasses import dataclass

@dataclass
class MConfig:
    # Paraphrase generation
    wordnet_pct_swap: float = 0.3
    wordnet_n: int = 5
    embedding_n: int = 3
    embedding_min_cosine: float = 0.8

    # Masking
    mask_ratios: tuple = (0.2, 0.5)

    # Reproducibility - MUST match H-E1's CONFIG.random_state
    random_state: int = 42


MCONFIG = MConfig()

# Gate thresholds (PRD Section 3 Success Criteria - fixed, not tunable)
COSINE_PASS = 0.90
COSINE_FAIL = 0.80
ACC_DROP_PASS = 0.10
ACC_DROP_FAIL = 0.20
ROUTING_CONSISTENCY_PASS = 0.85
ROUTING_CONSISTENCY_FAIL = 0.70
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | MConfig + gate constants | Write `code/config.py` exactly as above; no variants (single fixed config per PRD) |

---

## A-1: Reconstruct H-E1 probe context [Complexity: 10, Budget: 1 subtask allocated to config coordination]

**Applied**: Standard PyTorch/sklearn dataclass defaults (reuse container, no new hyperparameters).

### Configuration (Python Dataclass)

```python
"""H-M2 Probe Context Container"""
from dataclasses import dataclass

@dataclass
class ProbeContext:
    probe: "AdapterSelectionProbe"  # from h_e1.model
    X_test: list       # str, 450 samples from H-E1 split
    y_test: list        # int, encoded labels
    task_families: list  # str, discovered via h_e1.data.stream_instructions
```

No new hyperparameters here — `build_probe_context(m_cfg: MConfig)` reuses `h_e1.config.CONFIG` internally (imported, not redefined) to call `stream_instructions`, `stratified_split`, and `AdapterSelectionProbe.fit` with identical settings, per architecture's `random_state=42` reuse note.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ProbeContext dataclass + build_probe_context | Define container; wire `h_e1.config.CONFIG`, `h_e1.data`, `h_e1.model` imports per architecture's External Dependencies table |

---

## Total Subtask Budget: 2/2 used

# Config: H-M5 (MECHANISM)

Applied: No matching Archon KB config pattern found — standard dataclass grouping by pipeline stage (data/model/train/eval/paths).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M4)
**Status**: No `config.py` exists in H-M4 — H-M4 used inline function defaults instead. Actual defaults verified directly from `h-m4/code/data_gen.py`, `train_mlp.py`, `probe_invariance.py` (function signatures read in full).
**Config Files Found**: None in h-m4/code/ — new dataclass config designed for H-M5, values sourced from H-M4 function signatures + H-M5 PRD.
**Pattern Used**: Dataclass (Python)

**Key verified defaults from H-M4 actual code (not spec)**:
- `data_gen.split_train_test(n_train=1000, n_test=200, seed=42)` — H-M5 overrides n_train/n_test per PRD scale
- `train_mlp.train_mlp_on_subset(epochs=50, batch_size=32, lr=1e-3, device="cpu")` — no `weight_decay` param in H-M4 (AdamW used default wd); no scheduler. H-M5 adds `weight_decay` and scheduler per PRD FR-3.1/3.2 — batch_size changes 32→64 per PRD FR-3.4.
- `probe_invariance.evaluate_population_invariance(hidden_dims=(32,32), num_permutations=10)` — reused unmodified.

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch defaults

```python
@dataclass
class DataConfig:
    data_path: str = "/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/data/cifar10_gs/dataset_cifar_small_hyp_rand.pt"
    max_models: int = None          # load full population (~42547)
    n_train: int = 40547            # max_models - n_test, per PRD "use max available"
    n_test: int = 2000
    split_seed: int = 42
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Wire data config | Pass DataConfig fields into `load_model_zoo_population` / `split_train_test` calls |

---

## A-2: Model [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch defaults

```python
@dataclass
class ModelConfig:
    hidden_dims: list = field(default_factory=lambda: [512, 256])
    output_dim: int = 1
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | MLPMatchedWide config wiring | Pass hidden_dims into model constructor (input_dim computed at runtime from flattened weight size) |

---

## A-3: Training [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch defaults; CosineAnnealingLR per PRD FR-3.2

```python
@dataclass
class TrainConfig:
    epochs: int = 50
    batch_size: int = 64            # Non-standard: changed from H-M4's 32 per PRD FR-3.4
    lr: float = 1e-3
    weight_decay: float = 1e-4      # Non-standard: new field, H-M4 had no wd (AdamW default)
    device: str = "cpu"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Scheduled training loop | AdamW(lr, weight_decay) + CosineAnnealingLR(T_max=epochs), step per epoch |

---

## A-4: Evaluation [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch defaults; reuses H-M4 invariance methodology unmodified

```python
@dataclass
class EvalConfig:
    n_permutations: int = 10        # matches H-M4 num_permutations
    n_seeds: int = 10               # multi-seed statistical run per PRD FR-3.5
    hidden_dims_probe: tuple = (32, 32)  # unused for flat-vector permutation but kept for signature parity
    r2_threshold: float = 0.1       # PRD gate: test_r2 < 0.1 -> INCONCLUSIVE
    invariance_threshold: float = 0.8  # PRD gate: mean_invariance > 0.8 -> PASS
    hm4_r2_baseline: float = 0.0036
    hm4_invariance_baseline: float = 0.9193
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | Gate + comparison config | Wire thresholds into `gate_logic` and `compare_with_baseline` |

---

## A-5: Paths [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch defaults

```python
@dataclass
class PathConfig:
    output_dir: str = "docs/youra_research/h-m5"
    figures_dir: str = "docs/youra_research/h-m5/figures"
    results_path: str = "docs/youra_research/h-m5/results.json"
    h_m4_code_dir: str = "docs/youra_research/h-m4/code"
    h_m3_code_dir: str = "docs/youra_research/h-m3/code"
    h_m1_code_dir: str = "docs/youra_research/h-m1/code"
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | sys.path wiring | Insert h_m4/h_m3/h_m1 code dirs into sys.path before importing data_gen, probe_invariance, flatten_state_dict, generate_permutations |

---

## Inherited Configuration (Base Hypothesis)

No `config.py` existed in H-M4 — defaults below are verified from actual H-M4 function signatures, not a config spec file.

```python
# From: h-m4/code/data_gen.py (ACTUAL CODE)
def split_train_test(population, n_train: int = 1000, n_test: int = 200, seed: int = 42): ...

# From: h-m4/code/train_mlp.py (ACTUAL CODE)
def train_mlp_on_subset(train_dataset, input_dim, seed, epochs: int = 50,
                         batch_size: int = 32, lr: float = 1e-3, device: str = "cpu"): ...
# no weight_decay param, no scheduler in H-M4

# From: h-m4/code/probe_invariance.py (ACTUAL CODE)
def evaluate_population_invariance(model, test_population, hidden_dims=(32, 32),
                                    num_permutations: int = 10, device: str = "cpu"): ...
```

**Reused unmodified in H-M5**: `evaluate_population_invariance`, `compute_probe_invariance`, `load_model_zoo_population`, `split_train_test`, `to_dataset`, `flatten_state_dict`.

**Verified from**: `docs/youra_research/h-m4/code/data_gen.py`, `train_mlp.py`, `probe_invariance.py` (actual implementation, read in full).

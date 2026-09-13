# Architecture: H-M2 (Layer-wise Probe Sweep for Inverted-U Pattern)

**Type:** MECHANISM | **Gate:** SHOULD_WORK (L_60% AUROC > L_100% AUROC)

Applied: sonde LayerProbeSweepRunner pattern (val-based layer selection) + H-M1 multi-layer context-managed hook extraction

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1, H-E1)
**Status**: Serena has no active project registered for this workspace path (same limitation as H-M1); used direct file reads instead.
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Findings**:
- `h-m1/code/hooks.py` `HiddenStateExtractor` ALREADY supports multi-layer extraction (`layer_indices: list`, `hidden_states: dict[int, Tensor]`) — directly reusable for H-M2's 8-layer sweep, no modification needed.
- `h-e1/code/model.py` has single-layer `extract_hidden_states`, `train_probe`, `LinearProbe` — logic reusable but must be adapted to loop over layers (currently single `target_layer`).
- `h-e1/code/data.py` has `load_triviaqa`, `format_prompt`, `label_correctness`, `build_labeled_dataset_batched` — directly reusable, unchanged.
- `h-e1/code/evaluate.py` has `evaluate_auroc` (sklearn roc_auc_score) — directly reusable per-layer.
- No bootstrap CI or multi-layer sweep utility exists in either base — new for H-M2.

---

## File Organization

```
h-m2/code/
├── config.py       # Config dataclass (seed, layers, hparams, paths)
├── data.py         # load_triviaqa + build_labeled_dataset (reuse H-E1)
├── hooks.py        # HiddenStateExtractor multi-layer (reuse H-M1 verbatim)
├── probe.py        # LinearProbe, train_probe, evaluate_auroc (adapt H-E1)
├── sweep.py         # run_layer_sweep, bootstrap CI, inverted-U verification
├── run_experiment.py  # orchestrates extraction + sweep + gate + figures
└── figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    num_layers: int = 32
    layer_depths: list = field(default_factory=lambda: [0.125, 0.25, 0.375, 0.5, 0.6, 0.75, 0.875, 1.0])
    n_train: int = 9500
    n_val: int = 1700
    max_new_tokens: int = 32
    lr: float = 1e-2
    weight_decay: float = 1e-4
    epochs: int = 15
    batch_size: int = 256
    n_bootstrap: int = 1000
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

def get_layer_indices(num_layers: int, depths: list) -> list[int]: ...
def set_seed(seed: int = 42) -> None: ...
```

### Data (`data.py`)

**Dependencies**: None (reuses H-E1 `load_triviaqa`/`format_prompt`/`label_correctness`/`build_labeled_dataset_batched` verbatim)

```python
def load_triviaqa_splits(n_train: int, n_val: int) -> tuple["Dataset", "Dataset"]: ...
def build_labeled_dataset(model, tokenizer, dataset, n: int, batch_size: int) -> list[dict]: ...
```

### HiddenStateExtractor (`hooks.py`)

**Dependencies**: torch — reused verbatim from H-M1 (already multi-layer capable)

```python
class HiddenStateExtractor:
    def __init__(self, model, layer_indices: list[int]): ...
    def __enter__(self) -> "HiddenStateExtractor": ...
    def __exit__(self, *exc) -> None: ...
    hidden_states: dict[int, torch.Tensor]  # per-layer (B, seq, 4096)
```

### Probe (`probe.py`)

**Dependencies**: torch, hooks

```python
class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

def extract_all_layers(model, tokenizer, extractor, examples: list, batch_size: int) -> tuple[dict[int, torch.Tensor], torch.Tensor]: ...
    # returns {layer_idx: (N, 4096) last-token states}, labels (N,)

def train_probe(hidden_states: torch.Tensor, labels: torch.Tensor, cfg) -> tuple["LinearProbe", list[float]]: ...
def evaluate_auroc(probe, hidden_states: torch.Tensor, labels: torch.Tensor) -> tuple[float, np.ndarray, np.ndarray]: ...
```

### Sweep (`sweep.py`)

**Dependencies**: probe, sklearn.metrics

```python
def run_layer_sweep(
    train_states: dict[int, torch.Tensor], train_labels: torch.Tensor,
    val_states: dict[int, torch.Tensor], val_labels: torch.Tensor,
    cfg,
) -> dict[int, dict]:
    # returns {layer_idx: {"auroc": float, "probe": LinearProbe, "losses": list}}

def bootstrap_auroc_ci(labels: np.ndarray, preds: np.ndarray, n_bootstrap: int = 1000) -> tuple[float, float]: ...
    # returns (ci_low, ci_high)

def verify_inverted_u_pattern(layer_aurocs: dict[int, float], num_layers: int) -> dict: ...
    # returns {middle_beats_final, middle_beats_early, peak_layer, peak_depth_pct, inverted_u_detected, gate_satisfied}
```

### Orchestration (`run_experiment.py`)

**Dependencies**: config, data, hooks, probe, sweep, matplotlib

```python
def main() -> None: ...
def plot_gate_comparison(layer_aurocs: dict, cfg) -> None: ...        # bar: L25/L60/L100
def plot_layer_auroc_curve(layer_aurocs: dict, cis: dict, cfg) -> None: ...  # line + error bars
def plot_inverted_u(layer_aurocs: dict, cfg) -> None: ...             # polynomial fit + peak highlight
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| HiddenStateExtractor | `from h_m1.code.hooks import HiddenStateExtractor` (or copy verbatim — already multi-layer) | `h-m1/code/hooks.py` |
| load_triviaqa | reference pattern reused (adapted for train/val split sizes 9500/1700) | `h-e1/code/data.py` |
| format_prompt / label_correctness | reference pattern reused verbatim | `h-e1/code/data.py` |
| build_labeled_dataset_batched | reference pattern reused verbatim (renamed `build_labeled_dataset`) | `h-e1/code/data.py` |
| LinearProbe / train_probe | reference pattern adapted (loop added per layer, lr/wd changed to match H-M2 PRD: lr=1e-2, weight_decay=1e-4 vs H-E1's Adam-only) | `h-e1/code/model.py` |
| evaluate_auroc | reference pattern reused verbatim | `h-e1/code/evaluate.py` |

**Verified from**: `docs/youra_research/h-m1/code/` and `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: H-M1's `HiddenStateExtractor` requires NO modification — its `layer_indices: list` constructor and `hidden_states: dict[int, Tensor]` output already match H-M2's 8-layer sweep requirement exactly.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| S-1 | Setup config & layer index mapping | Config dataclass, depth-to-index conversion for 8 layers [3,7,11,15,18,23,27,31] | 5 | 1+1+1+2 |
| S-2 | Data loading & labeling | Reuse H-E1 TriviaQA/NQ loader, build 9500 train / 1700 val labeled sets | 6 | 2+2+1+1 |
| S-3 | Port multi-layer HiddenStateExtractor | Reuse H-M1 hooks.py verbatim, wire to 8 target layers | 4 | 1+1+1+1 |
| S-4 | Batched multi-layer extraction pipeline | Forward pass with extractor context, collect last-token states per layer for train+val | 10 | 3+2+3+2 |
| S-5 | Per-layer probe training loop | Train 8 independent LinearProbes (AdamW, lr=1e-2, wd=1e-4, 15 epochs, batch=256) | 9 | 2+2+3+2 |
| S-6 | AUROC evaluation + bootstrap CI | sklearn roc_auc_score per layer, bootstrap resampling (n=1000) for CI | 8 | 2+2+3+1 |
| S-7 | Inverted-U gate verification logic | Compare L25/L60/L100, peak layer detection, gate_satisfied decision | 6 | 1+2+3+1 |
| S-8 | Orchestration script | run_experiment.py wiring extraction, sweep, gate check, results logging | 8 | 3+3+1+1 |
| S-9 | Visualization suite | Gate bar chart, layer-AUROC curve with CI error bars, inverted-U polynomial fit plot | 8 | 2+2+2+2 |
| S-10 | End-to-end integration run | Full 8-layer sweep on real model, validate gate on TriviaQA+NQ data | 12 | 3+4+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [S-4, S-5, S-6, S-10], Low(4-8): [S-1, S-2, S-3, S-7, S-8, S-9]

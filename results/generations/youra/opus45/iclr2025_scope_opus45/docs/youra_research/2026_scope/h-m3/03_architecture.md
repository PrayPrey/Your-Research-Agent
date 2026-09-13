# Architecture: H-M3 — Eigenmode Energy Redistribution via Projection-Only LoRA

**Applied**: PyTorch forward hook hidden state capture pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (via direct file read; Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/20260327_scope/h-m2/code/`
**Findings**: H-M2 has `MambaProbe`, `LoRAAdapter`, `EigenvaluePreservationValidator` in `model.py`; `train.py` exports `load_wikitext103_train`, `build_dataloader`, `build_optimizer_and_scheduler`, `train`; `config.py` has `ExperimentConfig` dataclass. All reused directly.

---

## File Organization

- `h-m3/code/config.py` — ExperimentConfig (extended from H-M2)
- `h-m3/code/model.py` — EigenmodeEnergyAnalyzer + imports from H-M2
- `h-m3/code/train.py` — reused from H-M2 (symlink or copy)
- `h-m3/code/evaluate.py` — perplexity + energy metrics + visualization
- `h-m3/code/run_experiment.py` — orchestrator

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MambaProbe | `sys.path.insert` + `from model import MambaProbe` | `h-m2/code/model.py` |
| LoRAAdapter | `sys.path.insert` + `from model import LoRAAdapter` | `h-m2/code/model.py` |
| load_wikitext103_train | `from train import load_wikitext103_train` | `h-m2/code/train.py` |
| build_dataloader | `from train import build_dataloader` | `h-m2/code/train.py` |
| build_optimizer_and_scheduler | `from train import build_optimizer_and_scheduler` | `h-m2/code/train.py` |
| train | `from train import train` | `h-m2/code/train.py` |

**Verified from**: `h-m2/code/model.py`, `h-m2/code/train.py` (actual implementation)

**Key H-M2 patterns confirmed**:
- A_log access: `layer.mixer.A_log.detach().float()` (all 48 layers via `model.backbone.layers`)
- Eigenvalue formula: `torch.exp(-torch.exp(a_log.float()))`
- LoRA targets: `["in_proj", "x_proj"]` only; `A_log` never trainable
- Config dataclass uses `from config import ExperimentConfig` (local import)

---

## Modules

### ExperimentConfig (`h-m3/code/config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "state-spaces/mamba-1.4b-hf"
    tokenizer_id: str = "state-spaces/mamba-1.4b-hf"

    # Dataset
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-103-raw-v1"
    num_train_sequences: int = 500
    num_eval_sequences: int = 1000
    max_seq_length: int = 256
    seed: int = 42

    # LoRA (identical to H-M2)
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: List[str] = field(default_factory=lambda: ["in_proj", "x_proj"])
    lora_dropout: float = 0.1
    lora_bias: str = "none"

    # Training (identical to H-M2)
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_epochs: int = 1
    batch_size: int = 2
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 10
    lr_scheduler_type: str = "cosine"

    # Energy analysis
    slow_mode_threshold: float = 0.99     # |λ| > threshold → slow mode
    delta_e_gate_threshold: float = 0.1  # nats

    # Hardware
    device: str = "cuda"
    dtype: str = "float16"

    # Output
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
```

---

### EigenmodeEnergyAnalyzer (`h-m3/code/model.py`)

**Dependencies**: ExperimentConfig, torch, math

```python
class EigenmodeEnergyAnalyzer:
    def __init__(self, model, config: ExperimentConfig) -> None: ...

    def register_hooks(self) -> None:
        """Register forward hooks on all layer.mixer modules to capture SSM outputs."""
        ...

    def clear_hooks(self) -> None:
        """Remove all registered hooks and clear captured hidden_states."""
        ...

    def _capture_state(self, module, input, output) -> None:
        """Hook callback: appends output.detach() to self.hidden_states."""
        ...

    def measure_energy(self, model, input_ids: Tensor) -> dict:
        """Run forward pass with hooks; return energy dict.

        Returns:
            {
              'per_layer': List[float],       # slow_fraction per layer (48 values)
              'slow_fraction': float,         # global average slow mode fraction
              'per_layer_total_energy': List[float],
            }
        """
        ...

    def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> dict:
        """Compute ΔE metrics between pre- and post-training energy dicts.

        Returns:
            {
              'delta_slow_fraction': float,   # post - pre
              'delta_e_nats': float,          # -log(1 - min(|delta|, 0.99))
              'gate_pass': bool,              # delta_e_nats > threshold
              'per_layer_delta': List[float],
            }
        """
        ...

    def get_eigenvalues_per_layer(self) -> List[Tensor]:
        """Return list of eigenvalue tensors [d_inner, d_state] per layer.
        λ = exp(-exp(A_log))
        """
        ...
```

---

### Training Infrastructure (`h-m3/code/train.py`)

**Dependencies**: ExperimentConfig (local), torch, datasets, transformers

Reused from H-M2. Copy `h-m2/code/train.py` verbatim; update local import to use H-M3 `config.py`.

Exported functions (signatures unchanged):
```python
def load_wikitext103_train(config: ExperimentConfig, tokenizer) -> Dataset: ...
def build_dataloader(tokenized_dataset, config: ExperimentConfig) -> DataLoader: ...
def build_optimizer_and_scheduler(model, config: ExperimentConfig, num_training_steps: int) -> Tuple: ...
def train(model, dataloader: DataLoader, optimizer, scheduler, config: ExperimentConfig) -> List[float]: ...
```

---

### Evaluator (`h-m3/code/evaluate.py`)

**Dependencies**: EigenmodeEnergyAnalyzer, ExperimentConfig, matplotlib

```python
def load_wikitext103_eval(config: ExperimentConfig, tokenizer) -> Dataset: ...

def compute_perplexity(model, eval_dataset, config: ExperimentConfig) -> float:
    """Cross-entropy perplexity on WikiText-103 validation set."""
    ...

def plot_gate_metrics(delta_e_nats: float, threshold: float, figures_dir: str) -> None:
    """Bar chart: ΔE actual vs 0.1 nats threshold with PASS/FAIL annotation."""
    ...

def plot_energy_distribution(pre_energy: dict, post_energy: dict, figures_dir: str) -> None:
    """Histogram: per-eigenmode energy pre vs post with slow mode threshold overlay."""
    ...

def plot_per_layer_slow_fraction(pre_energy: dict, post_energy: dict, figures_dir: str) -> None:
    """Bar chart: slow_fraction for each of 48 layers, pre vs post."""
    ...

def plot_eigenvalue_energy_scatter(
    eigenvalues: List[Tensor],
    pre_energy: dict,
    post_energy: dict,
    figures_dir: str,
) -> None:
    """Scatter: eigenvalue magnitude vs energy contribution, colored slow/fast."""
    ...

def plot_training_loss(losses: List[float], figures_dir: str) -> None:
    """Line chart of training loss over steps."""
    ...

def save_results(results: dict, path: str) -> None: ...
```

---

### Experiment Orchestrator (`h-m3/code/run_experiment.py`)

**Dependencies**: all above modules

```python
def main() -> None:
    """
    Sequence:
      1. Load config and model (MambaProbe from H-M2)
      2. Apply LoRA (LoRAAdapter from H-M2), verify A_log frozen
      3. Pre-training energy measurement (EigenmodeEnergyAnalyzer)
      4. Load data, train (train.py functions)
      5. Post-training energy measurement
      6. Compute ΔE, evaluate gate
      7. Compute perplexity (sanity check)
      8. Save figures and results.yaml
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config Setup | Copy H-M2 config.py; add energy fields (slow_mode_threshold, delta_e_gate_threshold, num_eval_sequences) | 5 | 1+1+1+2 |
| A-2 | Copy Train Infrastructure | Copy h-m2/code/train.py; update local import for H-M3 config; verify 500 train sequences | 6 | 1+2+1+2 |
| A-3 | Reuse MambaProbe + LoRAAdapter | Copy model.py from H-M2; retain MambaProbe, LoRAAdapter, remove EigenvaluePreservationValidator | 7 | 2+2+2+1 |
| A-4 | Implement EigenmodeEnergyAnalyzer | Core new component: hook registration, hidden state capture, per-layer energy computation, slow mode masking | 17 | 4+4+5+4 |
| A-5 | Implement compute_delta_e | ΔE in nats formula, per-layer delta, gate evaluation logic | 10 | 2+2+4+2 |
| A-6 | Load WikiText-103 Eval Split | Adapt load_wikitext103_train for validation split; 1000 sequence subset for energy measurement | 7 | 2+2+1+2 |
| A-7 | Implement compute_perplexity | Cross-entropy perplexity on eval set; sanity check ~15-20 PPL | 8 | 2+2+2+2 |
| A-8 | Visualization: Gate Metrics | Bar chart ΔE vs threshold with PASS/FAIL; mandatory figure | 7 | 2+1+2+2 |
| A-9 | Visualization: Energy Distribution | Pre/post histogram overlay + eigenvalue scatter + per-layer bar chart + training loss | 10 | 3+1+3+3 |
| A-10 | Orchestrator run_experiment.py | Wire full pipeline: load → hook → measure pre → train → measure post → ΔE → PPL → save | 14 | 3+4+4+3 |
| A-11 | Results Serialization | Save results.yaml with all metrics; verify gate pass/fail printed clearly | 6 | 1+2+1+2 |
| A-12 | End-to-End Validation | Run full pipeline; confirm code runs without error; ΔE reported; figures saved | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-10], Medium(9-13): [A-5, A-7, A-9, A-12], Low(4-8): [A-1, A-2, A-3, A-6, A-8, A-11]

---

## Module Dependency Graph

- `run_experiment.py` → `model.py`, `train.py`, `evaluate.py`, `config.py`
- `model.py` → `config.py`
- `train.py` → `config.py`
- `evaluate.py` → `model.py`, `config.py`

---

## Critical Implementation Notes

1. **Hook output shape**: `layer.mixer` forward output for Mamba is the processed sequence tensor `[B, L, d_model]`, NOT the raw SSM state. The raw d_state tensor must be obtained by registering a hook on the selective scan sub-module or by accessing `ssm_state` directly. If unavailable, fall back to output `[B, L, d_model]` decomposed along last dimension using eigenvalue mask indexed by `d_state`.

2. **A_log shape**: confirmed `[d_inner, d_state]` = `[2*d_model, d_state]` = `[4096, 16]` per layer. Slow mask shape must align with energy tensor indexing.

3. **Memory management**: call `analyzer.clear_hooks()` immediately after each measurement to prevent GPU OOM from accumulated hidden states (48 layers × batch × seq × d_model).

4. **Import path for H-M2 reuse**: H-M2 modules use `from config import ExperimentConfig` (local). H-M3 copies files into `h-m3/code/` and runs from that directory, so local imports work without path manipulation.

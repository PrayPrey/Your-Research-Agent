# Logic: H-E1 Spectral Memory Horizon Stability

**Hypothesis**: EXISTENCE PoC - CV(H_spec) < 0.3 across 1000 random sequences
**Date**: 2026-03-27

Applied: Standard PyTorch direct weight access pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

### API Signatures

```python
# code/config.py
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    model_id: str = "state-spaces/mamba-1.4b"
    model_370m_id: str = "state-spaces/mamba-370m"
    tokenizer_id: str = "EleutherAI/gpt-neox-20b"
    num_samples: int = 1000
    seq_length: int = 512
    seed: int = 42
    cv_threshold: float = 0.3
    figures_dir: str = "figures"
    results_path: str = "results.yaml"
    device: str = "cuda"
    dtype: str = "float32"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config + dirs | ExperimentConfig dataclass, create figures/ dir |

---

## A-2: Model Loader [Complexity: 12, Budget: 3 subtasks]

**Applied**: PyTorch direct weight access pattern (no hooks for static A matrix)

### API Signatures

```python
# code/model.py
import torch
from torch import Tensor
from typing import Optional
from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel

class MambaProbe:
    def __init__(self, config: "ExperimentConfig") -> None:
        """Initialize probe with config; model not loaded until load_model()."""
        self.config = config
        self.model: Optional[MambaLMHeadModel] = None
        self._device: torch.device = torch.device(config.device)

    def load_model(self, model_id: str) -> None:
        """Load MambaLMHeadModel from HuggingFace; moves to device, eval mode."""
        # MambaLMHeadModel.from_pretrained(model_id, dtype=torch.float32)
        # self.model.to(self._device).eval()

    def extract_layer_eigenvalues(self) -> list[Tensor]:
        """Return list of abs eigenvalue tensors, one per layer.

        Returns: list of length num_layers, each tensor shape [d_inner, d_state]
        """
        # for layer in self.model.backbone.layers:
        #     A_log = layer.mixer.A_log.float()  # [d_inner, d_state]
        #     A_abs = torch.exp(A_log).abs()      # [d_inner, d_state]
        #     eigenvalues.append(A_abs)

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        """Compute H_spec = -1/log(lambda_max) from static A weights.

        input_ids: unused (A is input-independent); kept for interface consistency
        Returns: H_spec as Python float; returns float('nan') if lambda_max >= 1.0
        """
        # eigenvalues = self.extract_layer_eigenvalues()
        # lambda_max = max(e.max().item() for e in eigenvalues)
        # guard: if lambda_max >= 1.0: return float('nan')
        # return -1.0 / math.log(lambda_max)

    def unload(self) -> None:
        """Delete model reference and free GPU memory."""
        # del self.model; torch.cuda.empty_cache()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| A_log | [d_inner, d_state] | e.g. [2816, 16] for Mamba-1.4B per layer |
| A_abs (per layer) | [d_inner, d_state] | exp(A_log).abs() |
| lambda_max | scalar | global max across all layers |
| H_spec | scalar float | -1/log(lambda_max) |

### Pseudo-code: compute_h_spec

```
1. eigenvalues = extract_layer_eigenvalues()  # list of [d_inner, d_state]
2. all_lambdas = stack(eigenvalues).flatten()  # [num_layers * d_inner * d_state]
3. lambda_max = all_lambdas.max().item()
4. if lambda_max >= 1.0: return nan  # log would be non-negative
5. return -1.0 / log(lambda_max)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_model | from_pretrained with dtype/device, eval mode, fused-kernel fallback |
| L-2-2 | extract_layer_eigenvalues | iterate backbone.layers, access A_log, return list |
| L-2-3 | compute_h_spec + unload | lambda_max aggregation, H_spec formula, guard, memory cleanup |

---

## A-3: Eigenvalue Extraction [Complexity: 10, Budget: 3 subtasks]

**Applied**: Standard PyTorch

### API Signatures

```python
# code/evaluate.py
import numpy as np
import torch
from torch import Tensor
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from config import ExperimentConfig
    from model import MambaProbe

def generate_random_sequences(config: "ExperimentConfig") -> Tensor:
    """Generate random token sequences with fixed seed.

    Returns: [num_samples, seq_length] int64 token ids
    """
    # rng = torch.Generator().manual_seed(config.seed)
    # vocab_size obtained from AutoTokenizer.from_pretrained(config.tokenizer_id)
    # return torch.randint(0, vocab_size, (num_samples, seq_length), generator=rng)

def measure_h_spec_distribution(
    probe: "MambaProbe",
    sequences: Tensor,   # [num_samples, seq_length]
    config: "ExperimentConfig",
) -> dict:
    """Compute H_spec for each sequence; return distribution stats.

    Returns dict keys: h_spec_values (np.ndarray [num_samples]),
                       mean (float), std (float), cv (float), pass_gate (bool)
    """
    # h_spec_values = []
    # for i in range(num_samples):
    #     input_ids = sequences[i].unsqueeze(0).to(device)  # [1, seq_length]
    #     h = probe.compute_h_spec(input_ids)               # scalar float
    #     h_spec_values.append(h)
    # cv = np.std(h_spec_values) / np.mean(h_spec_values)
    # return {h_spec_values, mean, std, cv, pass_gate: cv < cv_threshold}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sequences | [1000, 512] | int64, random token ids |
| input_ids (per iter) | [1, 512] | single sequence on device |
| h_spec_values | [1000] | numpy float array |

### Pseudo-code: CV computation

```
1. h_vals = [probe.compute_h_spec(seq[i]) for i in range(N)]
2. h_arr = np.array([v for v in h_vals if not isnan(v)])
3. mean = h_arr.mean(); std = h_arr.std()
4. cv = std / mean
5. pass_gate = (cv < config.cv_threshold)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | generate_random_sequences | seeded randint, vocab_size from tokenizer |
| L-3-2 | measure_h_spec_distribution | per-sample loop, NaN filtering, cv calc |
| L-3-3 | run_scale_crossvalidation | load 370m probe, compute mean H_spec, compare |

---

## A-4: CV Measurement Loop [Complexity: 8, Budget: 1 subtask]

### API Signatures

```python
# Already covered by measure_h_spec_distribution above.
# run_scale_crossvalidation is in A-3 subtask L-3-3.

def run_scale_crossvalidation(config: "ExperimentConfig") -> dict:
    """Load Mamba-370M, compute mean H_spec, return comparison dict.

    Returns: {"h_spec_1.4b": float, "h_spec_370m": float, "monotonic": bool}
    """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | main loop wiring | connect generate -> measure -> crossval -> save in run_experiment.py |

---

## A-5: Visualization & Results [Complexity: 9, Budget: 1 subtask]

### API Signatures

```python
def save_results(metrics: dict, config: "ExperimentConfig") -> None:
    """Write metrics dict to results.yaml."""

def generate_figures(metrics: dict, config: "ExperimentConfig") -> None:
    """Save figures to config.figures_dir.

    Figures: hspec_distribution.png, gate_metrics.png,
             hspec_per_layer.png, eigenvalue_distribution.png,
             scale_comparison.png (if crossval data present)
    """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | figures + YAML | matplotlib plots, pyyaml dump, gate verdict print |

---

## Run Experiment Entry Point

```python
# code/run_experiment.py
def main() -> None:
    """Orchestrate full experiment pipeline."""
    # 1. config = ExperimentConfig()
    # 2. sequences = generate_random_sequences(config)  # [1000, 512]
    # 3. probe = MambaProbe(config); probe.load_model(config.model_id)
    # 4. metrics = measure_h_spec_distribution(probe, sequences, config)
    # 5. crossval = run_scale_crossvalidation(config)  # optional
    # 6. probe.unload()
    # 7. save_results({**metrics, **crossval}, config)
    # 8. generate_figures(metrics, config)
    # 9. print(f"CV={metrics['cv']:.4f}  {'PASS' if metrics['pass_gate'] else 'FAIL'}")
```

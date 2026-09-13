# Configuration: H-E1 — Activation Sparsity Existence Check

**Hypothesis Type**: EXISTENCE (PoC/measurement-only)
**Project Type**: Green-field
**Budget**: 0 dedicated config subtasks (config integrated into epic tasks)

Applied: Standard PyTorch dataclass pattern (TEAL/SparseGPT calibration methodology)
Applied: HuggingFace transformers float16 device_map="auto" pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## 1. ExperimentConfig Dataclass

**File**: `h-e1/code/config.py`

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    """Configuration for H-E1 activation sparsity measurement experiment.

    All fields use defaults verified against TEAL/SparseGPT calibration methodology.
    No training occurs — inference-only measurement.
    """

    # Model settings
    model_name: str = "meta-llama/Meta-Llama-3-8B"
    """HuggingFace model identifier. Must be a SiLU-gated LLM with gate_proj layers."""

    n_layers: int = 32
    """Expected number of MLP layers. Validation fails if model.model.layers != this."""

    torch_dtype: str = "float16"
    """Precision for model loading. float16 requires ~16GB VRAM for LLaMA-3-8B."""

    device_map: str = "auto"
    """HuggingFace device placement. 'auto' distributes across available GPUs."""

    # Experiment settings
    n_samples: int = 512
    """Calibration sample count. 512 matches TEAL and SparseGPT calibration standard."""

    batch_size: int = 8
    """Samples per forward pass. Balances memory (16GB VRAM) vs. throughput."""

    seed: int = 42
    """Random seed for dataset shuffling and reproducibility."""

    epsilons: List[float] = field(default_factory=lambda: [0.001, 0.01, 0.05, 0.1])
    """Threshold sweep for sparsity fraction: (|activation| < epsilon).mean()."""

    primary_epsilon: float = 0.01
    """Primary epsilon for gate condition evaluation (CV > 0.3 and tau >= 0.6)."""

    # Sequence lengths for sensitivity analysis
    short_length: int = 128
    """Short-sequence condition for length sensitivity analysis."""

    long_length: int = 512
    """Long-sequence condition (primary measurement length)."""

    # Dataset identifiers
    alpaca_dataset: str = "tatsu-lab/alpaca"
    """Primary calibration dataset — instruction-tuning distribution."""

    wikitext_dataset: str = "wikitext"
    """Stability check dataset — open-domain text distribution."""

    wikitext_config: str = "wikitext-103-raw-v1"
    """WikiText dataset configuration name on HuggingFace Hub."""

    # Output paths
    figures_dir: str = "h-e1/figures"
    """Directory for saved matplotlib figures (5 required figures)."""

    results_dir: str = "h-e1/results"
    """Directory for JSON/CSV result arrays."""

    # Gate thresholds (H-E1 success criteria)
    cv_threshold: float = 0.3
    """Minimum CV (std/mean) of per-layer sparsity. Gate condition: CV > 0.3."""

    tau_threshold: float = 0.6
    """Minimum Kendall's tau for cross-dataset rank stability. Gate: tau >= 0.6."""

    def __post_init__(self):
        """Validate critical constraints on initialization."""
        assert self.n_layers > 0, "n_layers must be positive"
        assert self.n_samples > 0, "n_samples must be positive"
        assert self.batch_size > 0, "batch_size must be positive"
        assert self.n_samples % self.batch_size == 0, (
            f"n_samples ({self.n_samples}) must be divisible by batch_size ({self.batch_size})"
        )
        assert self.primary_epsilon in self.epsilons, (
            f"primary_epsilon ({self.primary_epsilon}) must be in epsilons list {self.epsilons}"
        )
        assert self.short_length < self.long_length, (
            f"short_length ({self.short_length}) must be < long_length ({self.long_length})"
        )
        assert 0.0 < self.cv_threshold < 1.0, "cv_threshold must be in (0, 1)"
        assert 0.0 < self.tau_threshold <= 1.0, "tau_threshold must be in (0, 1]"
        assert self.torch_dtype in ("float16", "bfloat16", "float32"), (
            f"torch_dtype '{self.torch_dtype}' not supported"
        )
```

---

## 2. YAML Configuration File

**File**: `h-e1/config.yaml`

```yaml
model:
  name: meta-llama/Meta-Llama-3-8B
  dtype: float16
  device_map: auto

experiment:
  n_samples: 512
  batch_size: 8
  seed: 42
  epsilons: [0.001, 0.01, 0.05, 0.1]
  primary_epsilon: 0.01
  lengths:
    short: 128
    long: 512

datasets:
  alpaca:
    name: tatsu-lab/alpaca
    split: train
  wikitext:
    name: wikitext
    config: wikitext-103-raw-v1
    split: test

thresholds:
  cv: 0.3
  tau: 0.6

output:
  figures_dir: h-e1/figures
  results_dir: h-e1/results
```

---

## 3. Environment Requirements

**File**: `h-e1/requirements.txt`

```
torch>=2.0.0
transformers>=4.40.0
datasets>=2.18.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
peft>=0.10.0
accelerate>=0.27.0
```

**Setup verification snippet** (include in `run_experiment.py` or a `verify_env.py`):

```python
def verify_environment():
    import torch
    import transformers
    import datasets
    import scipy
    import numpy
    import matplotlib

    assert torch.cuda.is_available(), "CUDA not available — check CUDA_VISIBLE_DEVICES"
    print(f"torch: {torch.__version__}")
    print(f"transformers: {transformers.__version__}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    assert torch.cuda.get_device_properties(0).total_memory >= 15e9, (
        "Minimum 16GB VRAM required for LLaMA-3-8B float16"
    )
    print("Environment OK")
```

---

## 4. Hyperparameter Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_samples` | 512 | TEAL and SparseGPT both use 128-512 calibration samples. 512 gives stable statistics while fitting in memory with batch_size=8 (64 forward passes). |
| `batch_size` | 8 | At float16, LLaMA-3-8B uses ~16GB VRAM. batch_size=8 at 512 tokens fits within 24GB cards with activations cached for hooks. Reduce to 4 if OOM. |
| `primary_epsilon` | 0.01 | Specified directly in H-E1 hypothesis. Aligns with TEAL's default near-zero threshold for SiLU outputs. Acceptable range: 0.005–0.02. |
| `short_length` / `long_length` | 128 / 512 | Two-point length sensitivity check. 128 = short-context regime; 512 = standard LLM calibration length. Sufficient to detect length-driven sparsity shifts. |
| `cv_threshold` | 0.3 | Gate condition from H-E1 specification. CV > 0.3 means std exceeds 30% of mean — meaningful inter-layer differentiation. |
| `tau_threshold` | 0.6 | Gate condition from H-E1 specification. Kendall's tau >= 0.6 indicates moderate-to-strong rank agreement across distributions. |
| `seed` | 42 | Standard reproducibility seed for dataset shuffling. Affects Alpaca sample selection only. |

---

## 5. GPU and Memory Requirements

```
LLaMA-3-8B float16 VRAM breakdown:
  Model weights:        ~16 GB
  Activation buffers:   ~2-4 GB (hook storage, batch_size=8, seq_len=512)
  Total estimated:      ~18-20 GB

Minimum recommended:    24 GB VRAM (e.g., RTX 3090, A10G, RTX 4090)
Comfortable headroom:   40 GB VRAM (e.g., A100)
```

**CUDA setup**:

```bash
# Check available GPUs
nvidia-smi

# Select GPU with lowest memory usage (e.g., GPU 0)
export CUDA_VISIBLE_DEVICES=0

# Run experiment
cd h-e1
python code/run_experiment.py
```

**Memory optimization hints**:
- If OOM: reduce `batch_size` from 8 to 4 (doubles forward pass count, same total samples)
- Do NOT reduce `n_samples` below 256 (risks unstable tau estimates)
- `device_map="auto"` handles multi-GPU automatically if single GPU is insufficient
- `torch.no_grad()` is mandatory (saves ~2GB activation gradient memory)

---

*Hypothesis: H-E1 | Type: EXISTENCE | Config: Single fixed config, no ablations*

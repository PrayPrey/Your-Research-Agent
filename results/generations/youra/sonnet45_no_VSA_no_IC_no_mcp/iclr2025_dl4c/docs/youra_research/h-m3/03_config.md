# Configuration Specification: h-m3

**Date:** 2026-08-25
**Hypothesis:** h-m3 (MECHANISM)
**Type:** PoC - Minimal config for supervised learning validation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 infrastructure
**Config Files Found:** h-m1/03_config.md (dataclass pattern)
**Pattern Used:** Python dataclass (inheriting project convention)

---

## Configuration Schema

Single dataclass for supervised AI feedback training. No hyperparameter grid for PoC.

```python
"""Configuration for h-m3 supervised AI feedback experiment."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

@dataclass
class SupervisedFeedbackConfig:
    """PoC configuration for supervised learning mechanism validation."""
    
    # Experiment metadata
    hypothesis_id: str = "h-m3"
    random_seed: int = 42
    device: str = "cuda"  # "cuda" or "cpu"
    
    # Dataset configuration
    humaneval_size: int = 164  # Full dataset
    mbpp_size: int = 974       # Full dataset
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Model configuration
    pretrained_model: Literal["microsoft/codebert-base", "Salesforce/codet5-base"] = "microsoft/codebert-base"
    max_length: int = 512
    num_labels: int = 1  # Regression
    dropout: float = 0.1
    
    # Training configuration
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    batch_size: int = 8
    num_epochs: int = 5
    warmup_ratio: float = 0.1
    gradient_accumulation_steps: int = 1
    
    # Optimizer
    optimizer: str = "adamw"
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_epsilon: float = 1e-8
    
    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.001
    metric_for_best_model: str = "eval_loss"
    
    # Loss function
    loss_function: str = "mse"  # Mean squared error for regression
    
    # Evaluation configuration
    test_samples: int = 170  # 15% of 1138 total
    correlation_threshold: float = 0.7  # Gate condition
    p_value_threshold: float = 0.05
    
    # Baseline comparison (from h-e1)
    h_e1_baseline_correlation: float = 0.45  # HumanEval
    h_e1_baseline_correlation_mbpp: float = 0.52  # MBPP
    h_m1_correlation: float = 0.65
    
    # Paths (absolute)
    base_dir: Path = field(default_factory=lambda: Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m3"))
    h_e1_cache_dir: Path = field(default_factory=lambda: Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/.data_cache/datasets"))
    
    # Visualization
    figure_dpi: int = 300
    figure_formats: list = field(default_factory=lambda: ["png", "pdf"])
    
    # Logging
    logging_steps: int = 50
    eval_strategy: str = "epoch"
    save_strategy: str = "epoch"
    save_total_limit: int = 2
    load_best_model_at_end: bool = True
    
    def __post_init__(self):
        """Initialize derived paths and validate config."""
        self.output_dir = self.base_dir / "outputs"
        self.figures_dir = self.base_dir / "figures"
        self.checkpoint_dir = self.base_dir / "checkpoints"
        self.cache_dir = self.base_dir / "cache"
        
        for d in [self.output_dir, self.figures_dir, self.checkpoint_dir, self.cache_dir]:
            d.mkdir(exist_ok=True, parents=True)
        
        # Validate split ratios
        assert abs(self.train_ratio + self.val_ratio + self.test_ratio - 1.0) < 1e-6, "Split ratios must sum to 1.0"
        
        # Validate gate threshold
        assert self.correlation_threshold == 0.7, "Gate requires correlation > 0.7"
        
        # Validate test sample size
        total_samples = self.humaneval_size + self.mbpp_size
        expected_test_size = int(total_samples * self.test_ratio)
        assert expected_test_size >= 170, f"Test set too small: {expected_test_size} < 170"
```

---

## Non-Standard Value Rationale

**learning_rate = 2e-5**: Standard fine-tuning rate for BERT-based models. Lower (1e-5) causes slow convergence; higher (5e-5) risks instability on small dataset (797 train samples).

**batch_size = 8**: Balanced for GPU memory (CodeBERT-base 125M params fits on 16GB GPU) and gradient stability. Smaller (4) increases training time; larger (16) may overfit on small batches.

**num_epochs = 5**: Sufficient for convergence on small supervised dataset. Early stopping prevents overfitting. More epochs (10) showed no improvement in similar experiments.

**early_stopping_patience = 3**: Allows temporary fluctuations in validation loss while catching true overfitting. Patience=1 stops too early; patience=5 wastes compute.

---

## Compute Requirements

- **GPU:** 1x NVIDIA GPU with 16GB+ VRAM (RTX 3090, A100)
- **CPU Fallback:** Supported but slower (2h vs 30min)
- **RAM:** 16GB minimum
- **Storage:** 5GB (model checkpoints + cache)
- **Runtime:** 
  - GPU: 20-30 minutes
  - CPU: 90-120 minutes

---

## File Outputs

```
docs/youra_research/h-m3/
├── outputs/
│   ├── train_results.json           # Training metrics
│   ├── test_predictions.json        # Test set predictions
│   ├── correlation_results.json     # Spearman/Pearson correlations
│   └── gate_result.json            # Pass/fail status
├── figures/
│   ├── baseline_comparison.png/pdf  # Bar chart (required)
│   ├── scatter_predictions.png/pdf  # Human vs AI scores
│   ├── learning_curve.png/pdf       # Val correlation over epochs
│   └── error_distribution.png/pdf   # Residual histogram
├── checkpoints/
│   ├── checkpoint-best/            # Best model by val loss
│   └── checkpoint-final/           # Final epoch model
└── cache/
    ├── tokenizer/                  # Cached tokenizer
    └── datasets/                   # Processed datasets
```

---

## Reproducibility

All randomness controlled by seeds:
- Dataset splits: `random_seed=42`
- Model initialization: `transformers.set_seed(42)`
- Training order: `torch.manual_seed(42)`
- DataLoader shuffling: `generator=torch.Generator().manual_seed(42)`

Pinned versions:
- Model: `microsoft/codebert-base` (HuggingFace checkpoint)
- Datasets: h-e1 cache at `.data_cache/datasets/`
- PyTorch: >=2.0.0
- Transformers: >=4.30.0

---

## Environment Variables

```bash
# Optional: HuggingFace token for private models
# export HUGGING_FACE_HUB_TOKEN="hf_..."

# Optional: CUDA device selection
# export CUDA_VISIBLE_DEVICES="0"
```

---

**Self-Validation:**
- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Rationale only for non-standard values (4 params)
- [x] Total length < 400 lines (172 lines)
- [x] Codebase Analysis section included
- [x] Base hypothesis pattern verified (h-m1 dataclass)
- [x] PoC mode: no variations, no ablations, single fixed config

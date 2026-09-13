# System Architecture: h-e1
# Jacobian Stable Rank Regularization - EXISTENCE Proof-of-Concept

**Date:** 2026-05-12  
**Hypothesis Type:** EXISTENCE (PoC)  
**Architecture Pattern:** Applied: Minimal PoC Structure (single model/train/config files)

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing codebase - implementing novel stable rank regularization mechanism

---

## Module Structure

### DataModule (`code/data.py`)

**Dependencies**: HuggingFace Datasets, Transformers

```python
class C4DataModule:
    def __init__(self, tokenizer_name: str, seq_length: int, batch_size: int, streaming: bool): ...
    def prepare_data(self) -> None: ...
    def get_train_dataloader(self) -> DataLoader: ...
    def get_val_dataloader(self) -> DataLoader: ...

def create_dataloaders(config: dict) -> tuple[DataLoader, DataLoader]: ...
```

---

### BaseModel (`code/model.py`)

**Dependencies**: HuggingFace Transformers

```python
class BaselineGPT2:
    def __init__(self, config: GPT2Config): ...
    def forward(self, input_ids: Tensor, labels: Optional[Tensor]) -> dict: ...
    def compute_loss(self, logits: Tensor, labels: Tensor) -> Tensor: ...
```

---

### StableRankRegularizer (`code/model.py`)

**Dependencies**: PyTorch autograd

```python
class StableRankRegularizer(nn.Module):
    def __init__(self, n_power_iterations: int, n_hutchinson_probes: int, epsilon: float): ...
    def hutchinson_trace(self, layer_output: Tensor, layer_input: Tensor) -> Tensor: ...
    def power_iteration_spectral_norm(self, layer_output: Tensor, layer_input: Tensor) -> Tensor: ...
    def compute_stable_rank(self, layer_output: Tensor, layer_input: Tensor) -> Tensor: ...
```

---

### ProposedModel (`code/model.py`)

**Dependencies**: BaselineGPT2, StableRankRegularizer

```python
class RegularizedGPT2(nn.Module):
    def __init__(self, config: GPT2Config, lambda_reg: float, n_power_iter: int, n_hutchinson: int): ...
    def forward(self, input_ids: Tensor, labels: Optional[Tensor]) -> dict: ...
    def compute_regularization_loss(self, layer_outputs: list[Tensor], layer_inputs: list[Tensor]) -> Tensor: ...
    def adaptive_lambda_update(self, current_ppl: float, baseline_ppl: float) -> None: ...
```

---

### Trainer (`code/train.py`)

**Dependencies**: DataModule, BaselineGPT2, RegularizedGPT2

```python
class GPT2Trainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, 
                 config: dict, variant: str): ...
    def train_step(self, batch: dict) -> dict: ...
    def validation_step(self) -> dict: ...
    def train(self, total_steps: int) -> None: ...
    def save_checkpoint(self, step: int, metrics: dict) -> None: ...
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: torchmetrics

```python
class MetricsEvaluator:
    def __init__(self, model: nn.Module, val_loader: DataLoader): ...
    def compute_perplexity(self) -> float: ...
    def compute_stable_rank_per_layer(self, n_samples: int) -> dict: ...
    def compute_layer_variance(self, stable_ranks: dict) -> float: ...
    def compute_measurement_cv(self, stable_ranks: dict) -> float: ...
    def evaluate_all(self) -> dict: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
class ExperimentVisualizer:
    def __init__(self, results_dir: str): ...
    def plot_gate_metrics(self, metrics: dict, targets: dict) -> None: ...
    def plot_layer_evolution(self, training_logs: dict) -> None: ...
    def plot_stable_rank_distribution(self, stable_ranks: dict) -> None: ...
    def plot_perplexity_trajectory(self, training_logs: dict, baseline_ppl: float) -> None: ...
    def plot_measurement_precision(self, cv_values: list[float]) -> None: ...
    def save_all_figures(self, output_dir: str) -> None: ...
```

---

### Configuration (`code/config.py`)

**Dependencies**: None

```python
class ExperimentConfig:
    # Model configuration
    model_config: dict
    
    # Data configuration
    dataset_name: str
    tokenizer_name: str
    seq_length: int
    batch_size: int
    gradient_accumulation_steps: int
    
    # Training configuration
    learning_rate: float
    weight_decay: float
    betas: tuple[float, float]
    warmup_steps: int
    total_tokens: int
    seed: int
    
    # Regularization configuration
    lambda_init: float
    n_power_iterations: int
    n_hutchinson_probes: int
    epsilon: float
    
    # Evaluation configuration
    eval_interval: int
    checkpoint_interval: int
    
    # Success criteria
    target_sr_reduction: float
    target_ppl_deviation: float
    target_layer_variance_ratio: float
    target_measurement_cv: float

def get_baseline_config() -> ExperimentConfig: ...
def get_proposed_config() -> ExperimentConfig: ...
def get_implicit_control_config() -> ExperimentConfig: ...
```

---

### MainScript (`code/main.py`)

**Dependencies**: All modules

```python
def setup_environment(seed: int) -> None: ...
def load_baseline_ppl(checkpoint_dir: str) -> float: ...
def run_experiment(variant: str, config: ExperimentConfig) -> dict: ...
def compare_variants(results: dict[str, dict]) -> dict: ...
def validate_gate_criteria(results: dict) -> bool: ...

if __name__ == "__main__":
    # Run baseline
    # Run proposed
    # Run implicit control
    # Compare results
    # Validate gate
    # Generate visualizations
    ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── data.py              # C4 data loading
│   ├── model.py             # Baseline + Regularized GPT-2
│   ├── train.py             # Training loop
│   ├── evaluate.py          # Metrics computation
│   ├── visualize.py         # Figure generation
│   ├── config.py            # Experiment configurations
│   ├── main.py              # Main experiment runner
│   └── requirements.txt     # Dependencies
├── figures/                 # Generated visualizations
├── checkpoints/            # Model checkpoints
│   ├── baseline/
│   ├── proposed/
│   └── implicit_control/
└── results/                # Metrics logs (CSV/JSON)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | C4 dataset loading with streaming, tokenization, dataloaders | 8 | Module(2) + Deps(2) + Algorithm(2) + Integration(2) |
| A-2 | Baseline Model | Standard GPT-2 125M implementation, training loop, checkpointing | 10 | Module(3) + Deps(2) + Algorithm(2) + Integration(3) |
| A-3 | Stable Rank Regularization | Hutchinson trace + power iteration + residual-corrected stable rank | 16 | Module(4) + Deps(3) + Algorithm(5) + Integration(4) |
| A-4 | Proposed Model Training | Regularized GPT-2 with adaptive lambda, full training to 10B tokens | 14 | Module(3) + Deps(3) + Algorithm(4) + Integration(4) |
| A-5 | Evaluation & Metrics | Perplexity, stable rank per layer, variance, CV computation | 12 | Module(3) + Deps(2) + Algorithm(4) + Integration(3) |
| A-6 | Visualization | 5 required figures, gate metrics comparison, save outputs | 7 | Module(2) + Deps(1) + Algorithm(2) + Integration(2) |
| A-7 | Gate Validation | Compare metrics to targets, generate validation report | 6 | Module(1) + Deps(1) + Algorithm(2) + Integration(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-2, A-5], Low(4-8): [A-1, A-6, A-7]

**Total Complexity**: 73 points across 7 epic tasks

---

## Integration Flow

```
1. main.py initializes environment (seed, CUDA device)
2. config.py provides 3 variant configurations
3. data.py loads C4 streaming dataset
4. For each variant (baseline, proposed, implicit):
   a. model.py instantiates appropriate model
   b. train.py runs training loop with checkpointing
   c. evaluate.py computes metrics every 1000 steps
   d. Save checkpoints every 10,000 steps
5. evaluate.py performs final comparison
6. visualize.py generates all required figures
7. Validate gate criteria (sr_reduction ≥20%, ppl_dev ≤1%)
```

---

## Critical Implementation Notes

### Numerical Stability
- Epsilon: 1e-12 for spectral norm division
- Gradient clipping: 1.0 to prevent instability during regularization
- Mixed precision (FP16): Recommended for memory efficiency

### Memory Optimization
- Gradient accumulation: 4 steps for effective batch 128
- Checkpoint gradients for long sequences
- Release intermediate tensors in Hutchinson trace

### Adaptive Lambda Strategy
```python
if current_ppl > baseline_ppl * 1.01:  # Exceeds 1% threshold
    lambda_reg *= 0.95  # Reduce regularization
elif current_ppl < baseline_ppl * 0.99:
    lambda_reg *= 1.05  # Increase regularization
```

### Measurement Frequency
- Stable rank: Every 1000 steps (expensive computation)
- Perplexity: Every 500 steps (cheap validation)
- Full evaluation: Every 10,000 steps (checkpoint)

---

## Success Criteria Validation

**Gate Metrics (MUST_WORK):**
1. Mean sr_ℓ^res reduction ≥ 20% vs baseline
2. Perplexity deviation ≤ 1% from baseline
3. Layer variance < 2× mean stable rank
4. Measurement CV < 15%

**Implementation Checkpoints:**
- [ ] Baseline training completes without error
- [ ] Stable rank computation produces finite values
- [ ] Regularized model converges (loss decreases)
- [ ] All metrics computed at checkpoints
- [ ] Figures generated and saved

**If Gate Fails:**
Pipeline stops. Stable rank is not controllable via gradient-based regularization. Pivot to alternative metrics (SVD-based rank, gradient flow analysis).

---

## Dependencies

```txt
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
torchmetrics>=1.0.0
numpy>=1.24.0
matplotlib>=3.7.0
tqdm>=4.65.0
```

---

**Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 - Code Generation & Task Execution  
**Estimated Epic Tasks:** 7 tasks, 73 complexity points

---
hypothesis_id: h-m2
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Architecture Design
---

# System Architecture: Selective SSM Adapter Distillation (h-m2)

**Applied:** MOHAWK 3-stage distillation pattern, PyTorch Jacobian computation pattern, Mamba SSM integration pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (new implementation)
**Status**: Independent distillation experiment (does NOT extend h-m1)
**Analyzed Path**: docs/youra_research/20260318_scope/h-m1/code/
**Findings**: h-m1 implemented SVD-based low-rank analysis. h-m2 is a NEW distillation-based approach testing adapter-based attention→SSM conversion with Jacobian alignment. No code reuse from h-m1 (different methodologies).

---

## Architecture Overview

**Type**: Mechanism validation experiment (adapter distillation)
**Reuse Strategy**: None (fresh implementation)
**Components**: 7 core modules (distillation framework)
**Infrastructure**: MOHAWK 3-stage training pipeline + evaluation suite

**Key Difference from h-m1:**
- h-m1: Static SVD analysis of weight matrices
- h-m2: Dynamic distillation training with Jacobian alignment

---

## Module Structure

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers, torch

```python
class DistillationDataModule:
    def __init__(self, tokenizer: AutoTokenizer, batch_size: int = 8, context_length: int = 4096): ...

    def get_pile_dataloader(self, num_tokens: int, streaming: bool = True) -> DataLoader: ...

    def get_longbench_dataloader(self, tasks: List[str] = None, split: str = "test") -> Dict[str, DataLoader]: ...

    def create_fallback_c4_loader(self, num_tokens: int) -> DataLoader: ...
```

---

### ModelLoader (`src/model_loader.py`)

**Dependencies**: transformers, torch

```python
class LLaMALayerExtractor:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf", hf_token: str = None): ...

    def load_model(self, device: str = "cuda", dtype: torch.dtype = torch.float16) -> AutoModelForCausalLM: ...

    def extract_layer(self, layer_idx: int = 28) -> nn.Module: ...

    def get_attention_weights(self, layer: nn.Module) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: ...

    def configure_rope_scaling(self, max_position_embeddings: int = 131072) -> None: ...
```

---

### SelectiveSSMAdapter (`src/adapter.py`)

**Dependencies**: mamba-ssm, torch.nn

```python
class SelectiveSSMAdapter(nn.Module):
    def __init__(self, d_model: int = 4096, d_state: int = 512, d_conv: int = 4, expand: int = 2): ...

    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

    def get_ssm_parameters(self) -> Dict[str, torch.Tensor]: ...

class LTIControlAdapter(SelectiveSSMAdapter):
    def __init__(self, d_model: int = 4096, d_state: int = 512, d_conv: int = 4, expand: int = 2): ...

    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

---

### MOHAWKDistiller (`src/distiller.py`)

**Dependencies**: SelectiveSSMAdapter, torch.nn, torch.optim

```python
class MOHAWKDistiller:
    def __init__(self, teacher_layer: nn.Module, student_adapter: SelectiveSSMAdapter, config: dict): ...

    def stage1_matrix_orientation(self, dataloader: DataLoader, num_tokens: int) -> Dict[str, float]: ...

    def stage2_hidden_state_alignment(self, dataloader: DataLoader, num_tokens: int, lambda_jacobian: float = 0.1) -> Dict[str, float]: ...

    def stage3_end_to_end(self, dataloader: DataLoader, num_tokens: int) -> Dict[str, float]: ...

    def compute_loss_matrix_orientation(self, teacher_output: torch.Tensor, student_output: torch.Tensor) -> torch.Tensor: ...

    def compute_loss_hidden_state(self, teacher_hidden: torch.Tensor, student_hidden: torch.Tensor, teacher_jacobian: torch.Tensor, student_jacobian: torch.Tensor, lambda_jacobian: float) -> torch.Tensor: ...

    def save_checkpoint(self, stage: str, checkpoint_path: str) -> None: ...
```

---

### JacobianAnalyzer (`src/jacobian.py`)

**Dependencies**: torch, scipy.stats

```python
class JacobianAnalyzer:
    def __init__(self, device: str = "cuda"): ...

    def compute_jacobian(self, model: nn.Module, inputs: torch.Tensor) -> torch.Tensor: ...

    def extract_eigenvalues(self, jacobian: torch.Tensor) -> torch.Tensor: ...

    def compute_wasserstein2_distance(self, eigenvals_teacher: torch.Tensor, eigenvals_student: torch.Tensor) -> float: ...

    def batch_evaluate_w2(self, teacher_layer: nn.Module, student_adapter: nn.Module, dataloader: DataLoader, num_samples: int = 100) -> Dict[str, float]: ...
```

---

### EvaluationSuite (`src/evaluate.py`)

**Dependencies**: JacobianAnalyzer, torch, scipy

```python
class DistillationEvaluator:
    def __init__(self, teacher_layer: nn.Module, student_adapter: SelectiveSSMAdapter, jacobian_analyzer: JacobianAnalyzer): ...

    def evaluate_mse(self, dataloader: DataLoader) -> float: ...

    def evaluate_w2_distance(self, dataloader: DataLoader, num_samples: int = 100) -> Dict[str, float]: ...

    def evaluate_cross_domain_stability(self, pile_loader: DataLoader, longbench_loaders: Dict[str, DataLoader]) -> Dict[str, float]: ...

    def compare_selective_vs_lti(self, selective_adapter: SelectiveSSMAdapter, lti_adapter: LTIControlAdapter, dataloader: DataLoader) -> Dict[str, float]: ...

    def run_state_size_sweep(self, state_sizes: List[int], dataloader: DataLoader) -> Dict[int, Dict[str, float]]: ...
```

---

### Visualizer (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class DistillationVisualizer:
    def __init__(self, output_dir: str): ...

    def plot_mse_decay_vs_state_size(self, state_size_results: Dict[int, float], fit_params: Tuple[float, float, float]) -> None: ...

    def plot_jacobian_eigenvalue_distributions(self, eigenvals_teacher: np.ndarray, eigenvals_student: np.ndarray, w2_distance: float) -> None: ...

    def plot_cross_domain_stability(self, pile_errors: List[float], longbench_errors: List[float]) -> None: ...

    def plot_distillation_loss_curves(self, stage1_losses: List[float], stage2_losses: List[float], stage3_losses: List[float]) -> None: ...

    def plot_selective_vs_lti_comparison(self, selective_mse: float, lti_mse: float, attention_mse: float) -> None: ...

    def plot_gate_metrics_comparison(self, metrics: Dict[str, Tuple[float, float]]) -> None: ...
```

---

### ExperimentRunner (`src/main.py`)

**Dependencies**: All modules above

```python
class DistillationExperimentRunner:
    def __init__(self, config: dict): ...

    def setup_models(self) -> Tuple[nn.Module, SelectiveSSMAdapter, LTIControlAdapter]: ...

    def setup_data(self) -> Tuple[DataLoader, Dict[str, DataLoader]]: ...

    def run_mohawk_training(self) -> Dict[str, Any]: ...

    def run_evaluation(self) -> Dict[str, Any]: ...

    def validate_gate_criteria(self, results: Dict[str, Any]) -> Dict[str, bool]: ...

    def generate_visualizations(self, results: Dict[str, Any]) -> None: ...

    def write_validation_report(self, results: Dict[str, Any], gate_status: Dict[str, bool]) -> None: ...

def main():
    config = load_config()
    runner = DistillationExperimentRunner(config)
    training_results = runner.run_mohawk_training()
    evaluation_results = runner.run_evaluation()
    gate_status = runner.validate_gate_criteria(evaluation_results)
    runner.generate_visualizations(evaluation_results)
    runner.write_validation_report(evaluation_results, gate_status)
```

---

### Config (`src/config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class DistillationConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layer: int = 28
    hf_token: str = None

    d_model: int = 4096
    ssm_state_sizes: List[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])
    d_conv: int = 4
    expand: int = 2

    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    context_length: int = 4096

    stage1_tokens: int = 100_000_000
    stage1_lr: float = 1e-4
    stage2_tokens: int = 500_000_000
    stage2_lr: float = 5e-5
    lambda_jacobian: float = 0.1
    stage3_tokens: int = 2_400_000_000
    stage3_lr: float = 1e-5

    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "hotpotqa", "multifieldqa_en"])
    num_eval_samples: int = 100

    w2_threshold: float = 0.05
    exponential_fit_r2_threshold: float = 0.95
    cross_domain_delta_threshold: float = 0.03
    selective_advantage_threshold: float = 0.5

    random_seed: int = 42
    output_dir: str = "docs/youra_research/20260318_scope/h-m2"

def load_config(config_path: str = None) -> DistillationConfig: ...
```

---

## File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── data.py              # DistillationDataModule
│   │   ├── model_loader.py      # LLaMALayerExtractor
│   │   ├── adapter.py           # SelectiveSSMAdapter, LTIControlAdapter
│   │   ├── distiller.py         # MOHAWKDistiller (3-stage training)
│   │   ├── jacobian.py          # JacobianAnalyzer
│   │   ├── evaluate.py          # DistillationEvaluator
│   │   ├── visualize.py         # DistillationVisualizer
│   │   ├── config.py            # DistillationConfig
│   │   ├── main.py              # DistillationExperimentRunner
│   │   └── __init__.py
│   ├── run_distillation.sh      # GPU setup + execution script
│   └── requirements.txt         # Dependencies (mamba-ssm, transformers, datasets, scipy)
├── checkpoints/                 # Adapter checkpoints per stage
├── figures/                     # Generated visualizations
└── results/                     # Evaluation metrics (JSON)
```

---

## Data Flow

1. **Model Loading**: Load LLaMA-7B, extract L28 attention layer
2. **Data Preparation**: Stream The Pile (or C4), tokenize with context windowing
3. **Stage 1 Training**: Matrix orientation (100M tokens, lr=1e-4)
4. **Stage 2 Training**: Hidden-state + Jacobian alignment (500M tokens, lr=5e-5)
5. **Stage 3 Training**: End-to-end distillation (2.4B tokens, lr=1e-5)
6. **State Size Sweep**: Train adapters for N ∈ {64, 128, 256, 512, 1024}
7. **LTI Control**: Train fixed-Δ baseline with same protocol
8. **Evaluation**: Compute W2 distance, MSE, cross-domain stability
9. **Visualization**: Generate 6 figures (MSE decay, eigenvalue distributions, etc.)
10. **Validation Report**: Write 04_validation.md with gate decision

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| D-1 | Environment Setup | Install mamba-ssm, configure HF token, verify CUDA | 6 | 2+1+2+1 |
| D-2 | Data Pipeline | Implement The Pile/C4 streaming, LongBench loading, tokenization | 10 | 3+2+3+2 |
| D-3 | Model Loading Module | Load LLaMA-7B, extract L28, configure RoPE scaling | 8 | 2+2+2+2 |
| D-4 | SSM Adapter Implementation | Implement SelectiveSSMAdapter + LTI control using mamba-ssm | 11 | 3+3+3+2 |
| D-5 | Jacobian Analyzer | Implement Jacobian computation, eigenvalue extraction, W2 distance | 12 | 3+3+4+2 |
| D-6 | MOHAWK Distiller | Implement 3-stage distillation training loop with loss functions | 15 | 4+4+4+3 |
| D-7 | Evaluation Suite | Implement MSE, W2, cross-domain stability, selective vs LTI comparison | 13 | 3+3+4+3 |
| D-8 | State Size Sweep | Train adapters for 5 state sizes, evaluate all metrics | 10 | 3+2+3+2 |
| D-9 | Visualization Suite | Implement 6 figure generation functions (MSE decay, eigenvalues, etc.) | 9 | 3+2+2+2 |
| D-10 | Gate Validation | Implement gate criteria checks, generate validation report | 8 | 2+2+2+2 |

**Complexity Distribution:**
- VeryHigh (14-17): [D-6]
- High (11-13): [D-4, D-5, D-7]
- Medium (8-10): [D-2, D-3, D-8, D-9]
- Low (6-7): [D-1, D-10]

**Total Complexity**: 102

**Complexity Scoring:**
- Module_Size: 1-5 (lines of code / interfaces)
- Dependencies: 1-5 (number of external dependencies)
- Algorithm: 1-5 (mathematical/computational complexity)
- Integration: 1-5 (cross-module coordination)

---

## Breakdown: Task Complexity Details

### D-1: Environment Setup (6)
- Module_Size: 2 (requirements.txt + environment check)
- Dependencies: 1 (pip install)
- Algorithm: 2 (token validation, CUDA check)
- Integration: 1 (standalone setup)

### D-2: Data Pipeline (10)
- Module_Size: 3 (streaming dataset, tokenization, batching)
- Dependencies: 2 (datasets, transformers)
- Algorithm: 3 (streaming iteration, context windowing)
- Integration: 2 (connects to distiller)

### D-3: Model Loading Module (8)
- Module_Size: 2 (LLaMALayerExtractor class)
- Dependencies: 2 (transformers, torch)
- Algorithm: 2 (layer extraction, RoPE configuration)
- Integration: 2 (feeds adapter and distiller)

### D-4: SSM Adapter Implementation (11)
- Module_Size: 3 (SelectiveSSMAdapter + LTI variant)
- Dependencies: 3 (mamba-ssm, torch.nn, causal_conv1d)
- Algorithm: 3 (SSM forward pass, selective scan)
- Integration: 2 (connects to distiller and evaluator)

### D-5: Jacobian Analyzer (12)
- Module_Size: 3 (JacobianAnalyzer with eigenvalue extraction)
- Dependencies: 3 (torch.autograd, scipy.stats, numpy)
- Algorithm: 4 (Jacobian computation, eigenvalue decomposition, Wasserstein-2)
- Integration: 2 (used by distiller and evaluator)

### D-6: MOHAWK Distiller (15)
- Module_Size: 4 (3-stage training loop + loss functions)
- Dependencies: 4 (adapter, data, jacobian, torch.optim)
- Algorithm: 4 (3 loss formulations, gradient accumulation)
- Integration: 3 (coordinates all training components)

### D-7: Evaluation Suite (13)
- Module_Size: 3 (DistillationEvaluator with 5 methods)
- Dependencies: 3 (jacobian analyzer, adapters, dataloaders)
- Algorithm: 4 (MSE, W2, cross-domain delta, exponential fit)
- Integration: 3 (consumes training outputs, feeds visualizer)

### D-8: State Size Sweep (10)
- Module_Size: 3 (train loop for 5 state sizes)
- Dependencies: 2 (distiller, evaluator)
- Algorithm: 3 (repeated training + evaluation)
- Integration: 2 (parallel workflow with checkpointing)

### D-9: Visualization Suite (9)
- Module_Size: 3 (6 plotting functions)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 2 (plot generation, formatting)
- Integration: 2 (consumes evaluation results)

### D-10: Gate Validation (8)
- Module_Size: 2 (validate_gate_criteria + report writing)
- Dependencies: 2 (evaluation results, config)
- Algorithm: 2 (threshold checks, markdown generation)
- Integration: 2 (final stage, consumes all results)

---

## Key Implementation Notes

### Jacobian Computation Pattern
```python
# From JacobianAnalyzer
def compute_jacobian(self, model, inputs):
    with torch.enable_grad():
        inputs.requires_grad_(True)
        jacobian = torch.autograd.functional.jacobian(
            lambda x: model(x), inputs, create_graph=False
        )
    return jacobian

def extract_eigenvalues(self, jacobian):
    J_JT = jacobian @ jacobian.T
    eigenvals = torch.linalg.eigvalsh(J_JT)
    return eigenvals.abs()  # Use absolute values for stability
```

### MOHAWK Stage 2 Loss (Jacobian Alignment)
```python
# From MOHAWKDistiller
def compute_loss_hidden_state(self, teacher_hidden, student_hidden, teacher_jacobian, student_jacobian, lambda_jacobian):
    mse_loss = F.mse_loss(student_hidden, teacher_hidden)

    eigenvals_teacher = self.jacobian_analyzer.extract_eigenvalues(teacher_jacobian)
    eigenvals_student = self.jacobian_analyzer.extract_eigenvalues(student_jacobian)
    w2_loss = self.jacobian_analyzer.compute_wasserstein2_distance(
        eigenvals_teacher, eigenvals_student
    )

    return mse_loss + lambda_jacobian * w2_loss
```

### Selective vs LTI Control
```python
# From adapter.py
class LTIControlAdapter(SelectiveSSMAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Freeze Δ parameters (input-conditioned → constant)
        for name, param in self.ssm.named_parameters():
            if "dt_proj" in name or "delta" in name:
                param.requires_grad = False
```

---

## Validation Criteria

**Primary Metrics (Gate Criteria):**
1. W2 Jacobian distance < 0.05 at N=512
2. Exponential MSE decay R² > 0.95
3. Cross-domain error delta < 3%
4. Selective advantage: MSE_selective / MSE_LTI < 0.5

**MUST_WORK Gate:**
- **PASS**: All 4 criteria met → Enable h-m3 (calibration efficiency)
- **FAIL**: Any criterion fails → PIVOT to LTI baseline analysis

**Output:** `04_validation.md` with:
- MOHAWK training convergence curves
- State size sweep results (N=64 to 1024)
- W2 distance evaluation (target: <0.05)
- Cross-domain stability test
- Selective vs LTI comparison
- Gate decision (PASS/FAIL)

---

## Memory and Performance Constraints

**GPU Memory:**
- LLaMA-7B L28 fp16: ~2GB (single layer)
- Selective SSM adapter (N=512): ~4GB
- Batch (8 × 4096 tokens): ~6GB
- Gradient accumulation (4 steps): ~8GB
- Total: ~20GB (fits A100 40GB with margin)

**Execution Time:**
- Model loading: 5 min
- Stage 1 (100M tokens): 4 hours
- Stage 2 (500M tokens): 20 hours
- Stage 3 (2.4B tokens): 96 hours
- State size sweep (5 variants): ~120 hours × 5 = 600 hours
- Evaluation: 2 hours
- Total: ~5 days for primary run, ~25 days for full sweep

**Optimization:**
- Sequential stage execution (not parallel)
- Gradient accumulation (effective batch = 32)
- Mixed precision FP16
- Checkpoint after each stage
- LTI control trained separately

---

## Dependencies

**External Libraries:**
- `mamba-ssm` (Official Mamba SSM, requires `pip install mamba-ssm --no-build-isolation`)
- `causal_conv1d` (Dependency of mamba-ssm, auto-installed)
- `transformers` (HuggingFace, for LLaMA-7B)
- `datasets` (HuggingFace, for The Pile/C4 and LongBench)
- `torch` (PyTorch 2.1+, for Jacobian computation)
- `scipy` (for Wasserstein distance: `scipy.stats.wasserstein_distance`)
- `matplotlib`, `seaborn` (visualization)

**Data Dependencies:**
- The Pile (EleutherAI) with fallback to C4 (allenai/c4)
- LongBench (THUDM/LongBench)

**Model Dependencies:**
- LLaMA-2-7b-hf (Meta AI, requires HF access token)

**Access Requirements:**
- HuggingFace token (meta.com/llama)
- Single A100 40GB GPU (or similar)

---

## Differences from h-m1

| Aspect | h-m1 (Low-Rank Analysis) | h-m2 (Adapter Distillation) |
|--------|--------------------------|------------------------------|
| **Methodology** | Static SVD analysis | Dynamic distillation training |
| **Goal** | Validate low-rank structure | Validate attention→SSM conversion |
| **Key Metric** | Effective rank (r_eff) | Wasserstein-2 distance (W2) |
| **Training** | None (analysis only) | 3-stage MOHAWK (3B tokens) |
| **Components** | Analyzer, metrics, visualizer | Distiller, adapter, Jacobian analyzer |
| **Complexity** | 54 (7 tasks) | 102 (10 tasks) |
| **Execution Time** | ~6 hours | ~5 days (primary), ~25 days (full sweep) |

---

*Architecture designed for MECHANISM validation | MOHAWK distillation framework | Jacobian alignment testing*

---
hypothesis_id: h-m2
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Logic Design
---

# API Logic Specification: Selective SSM Adapter Distillation (h-m2)

**Applied:** PyTorch distillation training pattern, torch.autograd Jacobian pattern, HuggingFace streaming dataset pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New distillation implementation (does NOT extend h-m1)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation
**Context**: h-m1 implemented SVD-based static analysis. h-m2 is a dynamic distillation framework testing attention→SSM conversion with Jacobian alignment. No code reuse (different methodologies).

---

## D-2: Data Pipeline [Complexity: 10, Budget: 4]

**Applied**: HuggingFace streaming dataset pattern

### API Signatures

```python
class DistillationDataModule:
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        batch_size: int = 8,
        context_length: int = 4096
    ):
        """Initialize data module. tokenizer: LLaMA tokenizer, context_length: sequence length"""
        ...

    def get_pile_dataloader(
        self,
        num_tokens: int,
        streaming: bool = True
    ) -> DataLoader:
        """Stream The Pile. num_tokens: total tokens to process. Returns: DataLoader[{input_ids: [B, L]}]"""
        ...

    def get_longbench_dataloader(
        self,
        tasks: List[str] = None,
        split: str = "test"
    ) -> Dict[str, DataLoader]:
        """Load LongBench. tasks: subset of ['narrativeqa', 'qasper', 'hotpotqa', 'multifieldqa_en']. Returns: {task_name: DataLoader}"""
        ...

    def create_fallback_c4_loader(self, num_tokens: int) -> DataLoader:
        """Fallback to C4 if Pile unavailable. Returns: DataLoader[{input_ids: [B, L]}]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=8, L=4096 |
| attention_mask | [B, L] | Same as input_ids |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Pile streaming | Load datasets.load_dataset("EleutherAI/pile", streaming=True) |
| L-2-2 | Tokenization | Tokenize with padding/truncation to context_length |
| L-2-3 | LongBench loading | Load THUDM/LongBench for 4 tasks |
| L-2-4 | C4 fallback | Implement allenai/c4 streaming loader |

---

## D-3: Model Loading Module [Complexity: 8, Budget: 3]

**Applied**: HuggingFace transformers model extraction pattern

### API Signatures

```python
class LLaMALayerExtractor:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        hf_token: str = None
    ):
        """Initialize extractor. hf_token: HuggingFace access token"""
        ...

    def load_model(
        self,
        device: str = "cuda",
        dtype: torch.dtype = torch.float16
    ) -> AutoModelForCausalLM:
        """Load model. Returns: LLaMA model in FP16"""
        ...

    def extract_layer(self, layer_idx: int = 28) -> nn.Module:
        """Extract target layer. layer_idx: 0-31 for LLaMA-7B. Returns: model.model.layers[layer_idx]"""
        ...

    def get_attention_weights(
        self,
        layer: nn.Module
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Extract Q/K/V projections. Returns: (q_proj, k_proj, v_proj) each [4096, 4096]"""
        ...

    def configure_rope_scaling(
        self,
        max_position_embeddings: int = 131072
    ) -> None:
        """Configure RoPE for extended context. max_position_embeddings: 8K→128K extension"""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model loading | Load LLaMA-2-7b-hf with HF token auth |
| L-3-2 | Layer extraction | Access model.model.layers[28].self_attn |
| L-3-3 | RoPE scaling | Configure for 128K context window |

---

## D-4: SSM Adapter Implementation [Complexity: 11, Budget: 4]

**Applied**: Mamba SSM integration pattern

### API Signatures

```python
class SelectiveSSMAdapter(nn.Module):
    def __init__(
        self,
        d_model: int = 4096,
        d_state: int = 512,
        d_conv: int = 4,
        expand: int = 2
    ):
        """Initialize adapter. d_state: SSM state size N, d_conv: convolution width"""
        super().__init__()
        self.ssm = Mamba(d_model=d_model, d_state=d_state, d_conv=d_conv, expand=expand)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B, L, d_model] -> [B, L, d_model]"""
        return self.ssm(x)

    def get_ssm_parameters(self) -> Dict[str, torch.Tensor]:
        """Extract SSM parameters. Returns: {A, B, C, delta} for analysis"""
        ...


class LTIControlAdapter(SelectiveSSMAdapter):
    def __init__(self, d_model: int = 4096, d_state: int = 512, d_conv: int = 4, expand: int = 2):
        """LTI control with frozen Δ. Same API as SelectiveSSMAdapter"""
        super().__init__(d_model, d_state, d_conv, expand)
        # Freeze delta parameters
        for name, param in self.ssm.named_parameters():
            if "dt_proj" in name or "delta" in name:
                param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward with fixed Δ. x: [B, L, d_model] -> [B, L, d_model]"""
        return self.ssm(x)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Mamba installation | pip install mamba-ssm --no-build-isolation |
| L-4-2 | SelectiveSSMAdapter | Wrap Mamba SSM core with d_state config |
| L-4-3 | LTI control variant | Freeze dt_proj parameters |
| L-4-4 | Parameter extraction | Implement get_ssm_parameters for analysis |

---

## D-5: Jacobian Analyzer [Complexity: 12, Budget: 4]

**Applied**: torch.autograd Jacobian computation pattern

### API Signatures

```python
class JacobianAnalyzer:
    def __init__(self, device: str = "cuda"):
        """Initialize analyzer."""
        self.device = device

    def compute_jacobian(
        self,
        model: nn.Module,
        inputs: torch.Tensor
    ) -> torch.Tensor:
        """Compute Jacobian. inputs: [B, L, D] -> Jacobian: [B*L*D, B*L*D]"""
        with torch.enable_grad():
            inputs.requires_grad_(True)
            jacobian = torch.autograd.functional.jacobian(
                lambda x: model(x),
                inputs,
                create_graph=False
            )
        return jacobian

    def extract_eigenvalues(self, jacobian: torch.Tensor) -> torch.Tensor:
        """Extract eigenvalues from J @ J.T. Returns: eigenvals [D] sorted descending"""
        J_JT = jacobian @ jacobian.T
        eigenvals = torch.linalg.eigvalsh(J_JT)
        return eigenvals.abs().sort(descending=True)[0]

    def compute_wasserstein2_distance(
        self,
        eigenvals_teacher: torch.Tensor,
        eigenvals_student: torch.Tensor
    ) -> float:
        """Compute W2 distance. Returns: scalar W2 distance"""
        from scipy.stats import wasserstein_distance
        eig_t = eigenvals_teacher.cpu().numpy()
        eig_s = eigenvals_student.cpu().numpy()
        return wasserstein_distance(eig_t, eig_s)

    def batch_evaluate_w2(
        self,
        teacher_layer: nn.Module,
        student_adapter: nn.Module,
        dataloader: DataLoader,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """Evaluate W2 over batch. Returns: {mean_w2, std_w2}"""
        ...
```

### Pseudo-code

```
compute_jacobian(model, inputs):
  1. inputs.requires_grad_(True)
  2. jacobian = torch.autograd.functional.jacobian(lambda x: model(x), inputs)
  3. return jacobian

extract_eigenvalues(jacobian):
  1. J_JT = jacobian @ jacobian.T  # [D, D]
  2. eigenvals = torch.linalg.eigvalsh(J_JT)  # Compute eigenvalues
  3. return abs(eigenvals).sort(descending=True)

compute_wasserstein2_distance(eig_teacher, eig_student):
  1. return scipy.stats.wasserstein_distance(eig_teacher.cpu(), eig_student.cpu())
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Jacobian computation | Implement torch.autograd.functional.jacobian |
| L-5-2 | Eigenvalue extraction | Compute eigvalsh(J @ J.T) |
| L-5-3 | W2 distance | Integrate scipy.stats.wasserstein_distance |
| L-5-4 | Batch evaluation | Loop over dataloader samples |

---

## D-6: MOHAWK Distiller [Complexity: 15, Budget: 5]

**Applied**: PyTorch distillation training pattern

### API Signatures

```python
class MOHAWKDistiller:
    def __init__(
        self,
        teacher_layer: nn.Module,
        student_adapter: SelectiveSSMAdapter,
        config: dict
    ):
        """Initialize distiller. config: training hyperparameters"""
        self.teacher = teacher_layer
        self.student = student_adapter
        self.config = config
        self.jacobian_analyzer = JacobianAnalyzer()

    def stage1_matrix_orientation(
        self,
        dataloader: DataLoader,
        num_tokens: int
    ) -> Dict[str, float]:
        """Stage 1: Matrix orientation (100M tokens). Returns: {final_loss, training_time}"""
        ...

    def stage2_hidden_state_alignment(
        self,
        dataloader: DataLoader,
        num_tokens: int,
        lambda_jacobian: float = 0.1
    ) -> Dict[str, float]:
        """Stage 2: Hidden-state + Jacobian alignment (500M tokens). Returns: {final_loss, final_w2}"""
        ...

    def stage3_end_to_end(
        self,
        dataloader: DataLoader,
        num_tokens: int
    ) -> Dict[str, float]:
        """Stage 3: End-to-end distillation (2.4B tokens). Returns: {final_loss, final_mse}"""
        ...

    def compute_loss_matrix_orientation(
        self,
        teacher_output: torch.Tensor,
        student_output: torch.Tensor
    ) -> torch.Tensor:
        """Frobenius norm loss. teacher/student: [B, L, D]. Returns: scalar loss"""
        return torch.norm(teacher_output - student_output, p='fro')

    def compute_loss_hidden_state(
        self,
        teacher_hidden: torch.Tensor,
        student_hidden: torch.Tensor,
        teacher_jacobian: torch.Tensor,
        student_jacobian: torch.Tensor,
        lambda_jacobian: float
    ) -> torch.Tensor:
        """Hidden-state + Jacobian loss. Returns: MSE + λ * W2"""
        mse = F.mse_loss(student_hidden, teacher_hidden)
        eig_t = self.jacobian_analyzer.extract_eigenvalues(teacher_jacobian)
        eig_s = self.jacobian_analyzer.extract_eigenvalues(student_jacobian)
        w2 = self.jacobian_analyzer.compute_wasserstein2_distance(eig_t, eig_s)
        return mse + lambda_jacobian * w2

    def save_checkpoint(self, stage: str, checkpoint_path: str) -> None:
        """Save adapter state_dict. stage: 'stage1'|'stage2'|'stage3'"""
        ...
```

### Pseudo-code

```
stage1_matrix_orientation(dataloader, num_tokens):
  1. optimizer = AdamW(student.parameters(), lr=1e-4)
  2. total_processed = 0
  3. while total_processed < num_tokens:
       a. batch = next(dataloader)
       b. teacher_out = teacher(batch['input_ids'])
       c. student_out = student(batch['input_ids'])
       d. loss = compute_loss_matrix_orientation(teacher_out, student_out)
       e. loss.backward()
       f. optimizer.step()
       g. total_processed += batch['input_ids'].numel()
  4. save_checkpoint('stage1', 'checkpoints/stage1.pt')
  5. return {final_loss, training_time}

stage2_hidden_state_alignment(dataloader, num_tokens, lambda_jacobian):
  1. load_checkpoint('stage1')
  2. optimizer = AdamW(student.parameters(), lr=5e-5)
  3. while total_processed < num_tokens:
       a. batch = next(dataloader)
       b. teacher_hidden = teacher(batch['input_ids'])
       c. student_hidden = student(batch['input_ids'])
       d. teacher_jac = jacobian_analyzer.compute_jacobian(teacher, batch['input_ids'])
       e. student_jac = jacobian_analyzer.compute_jacobian(student, batch['input_ids'])
       f. loss = compute_loss_hidden_state(teacher_hidden, student_hidden, teacher_jac, student_jac, lambda_jacobian)
       g. loss.backward()
       h. optimizer.step()
       i. total_processed += batch['input_ids'].numel()
  4. save_checkpoint('stage2', 'checkpoints/stage2.pt')
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Stage 1 loop | Frobenius loss, lr=1e-4, 100M tokens |
| L-6-2 | Stage 2 loop | MSE + Jacobian loss, lr=5e-5, 500M tokens |
| L-6-3 | Stage 3 loop | End-to-end distillation, lr=1e-5, 2.4B tokens |
| L-6-4 | Checkpoint saving | Save state_dict after each stage |
| L-6-5 | Gradient accumulation | Implement 4-step accumulation |

---

## D-7: Evaluation Suite [Complexity: 13, Budget: 4]

**Applied**: PyTorch MSE evaluation pattern

### API Signatures

```python
class DistillationEvaluator:
    def __init__(
        self,
        teacher_layer: nn.Module,
        student_adapter: SelectiveSSMAdapter,
        jacobian_analyzer: JacobianAnalyzer
    ):
        """Initialize evaluator."""
        self.teacher = teacher_layer
        self.student = student_adapter
        self.jacobian_analyzer = jacobian_analyzer

    def evaluate_mse(self, dataloader: DataLoader) -> float:
        """Compute MSE. Returns: mean MSE over dataloader"""
        ...

    def evaluate_w2_distance(
        self,
        dataloader: DataLoader,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """Evaluate W2 distance. Returns: {mean_w2, std_w2}"""
        ...

    def evaluate_cross_domain_stability(
        self,
        pile_loader: DataLoader,
        longbench_loaders: Dict[str, DataLoader]
    ) -> Dict[str, float]:
        """Cross-domain stability. Returns: {pile_mse, longbench_mse, delta}"""
        ...

    def compare_selective_vs_lti(
        self,
        selective_adapter: SelectiveSSMAdapter,
        lti_adapter: LTIControlAdapter,
        dataloader: DataLoader
    ) -> Dict[str, float]:
        """Compare selective vs LTI. Returns: {selective_mse, lti_mse, ratio}"""
        ...

    def run_state_size_sweep(
        self,
        state_sizes: List[int],
        dataloader: DataLoader
    ) -> Dict[int, Dict[str, float]]:
        """Sweep state sizes. Returns: {N: {mse, w2}} for N in [64, 128, 256, 512, 1024]"""
        ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | MSE evaluation | Compute F.mse_loss over batches |
| L-7-2 | W2 evaluation | Call jacobian_analyzer.batch_evaluate_w2 |
| L-7-3 | Cross-domain test | Compare Pile vs LongBench MSE |
| L-7-4 | Selective vs LTI | Compare two adapter variants |

---

## D-8: State Size Sweep [Complexity: 10, Budget: 3]

**Applied**: PyTorch model training pattern

### API Signatures

```python
class StateSizeSweepRunner:
    def __init__(
        self,
        teacher_layer: nn.Module,
        distiller_factory: Callable[[int], MOHAWKDistiller],
        evaluator_factory: Callable[[SelectiveSSMAdapter], DistillationEvaluator]
    ):
        """Initialize sweep runner."""
        self.teacher = teacher_layer
        self.distiller_factory = distiller_factory
        self.evaluator_factory = evaluator_factory

    def run_sweep(
        self,
        state_sizes: List[int],
        dataloader: DataLoader
    ) -> Dict[int, Dict[str, Any]]:
        """Run sweep. Returns: {N: {mse, w2, training_time}}"""
        results = {}
        for N in state_sizes:
            adapter = SelectiveSSMAdapter(d_model=4096, d_state=N)
            distiller = self.distiller_factory(N)
            # Train 3 stages
            distiller.stage1_matrix_orientation(dataloader, 100_000_000)
            distiller.stage2_hidden_state_alignment(dataloader, 500_000_000)
            distiller.stage3_end_to_end(dataloader, 2_400_000_000)
            # Evaluate
            evaluator = self.evaluator_factory(adapter)
            results[N] = {
                'mse': evaluator.evaluate_mse(dataloader),
                'w2': evaluator.evaluate_w2_distance(dataloader)['mean_w2']
            }
        return results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | State size loop | Iterate N in [64, 128, 256, 512, 1024] |
| L-8-2 | Training per N | Run 3-stage MOHAWK for each N |
| L-8-3 | Evaluation per N | Compute MSE and W2 for each N |

---

## D-9: Visualization Suite [Complexity: 9, Budget: 3]

**Applied**: Matplotlib visualization pattern

### API Signatures

```python
class DistillationVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer. output_dir: path to save figures"""
        self.output_dir = output_dir

    def plot_mse_decay_vs_state_size(
        self,
        state_size_results: Dict[int, float],
        fit_params: Tuple[float, float, float]
    ) -> None:
        """Log-log plot. fit_params: (a, b, R²) from exponential fit MSE(N) = a * exp(-b * N)"""
        ...

    def plot_jacobian_eigenvalue_distributions(
        self,
        eigenvals_teacher: np.ndarray,
        eigenvals_student: np.ndarray,
        w2_distance: float
    ) -> None:
        """Histogram overlay. eigenvals: [D] arrays"""
        ...

    def plot_cross_domain_stability(
        self,
        pile_errors: List[float],
        longbench_errors: List[float]
    ) -> None:
        """Scatter plot. errors: MSE per sample"""
        ...

    def plot_distillation_loss_curves(
        self,
        stage1_losses: List[float],
        stage2_losses: List[float],
        stage3_losses: List[float]
    ) -> None:
        """3-panel training curves."""
        ...

    def plot_selective_vs_lti_comparison(
        self,
        selective_mse: float,
        lti_mse: float,
        attention_mse: float
    ) -> None:
        """Bar chart. 3 bars: selective, LTI, attention baseline"""
        ...

    def plot_gate_metrics_comparison(
        self,
        metrics: Dict[str, Tuple[float, float]]
    ) -> None:
        """Bar chart. metrics: {name: (target, actual)}"""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | MSE decay plot | matplotlib.pyplot log-log plot with exponential fit |
| L-9-2 | Eigenvalue histogram | Overlay teacher/student distributions |
| L-9-3 | Gate metrics plot | Bar chart with threshold lines |

---

## D-10: Gate Validation [Complexity: 8, Budget: 3]

**Applied**: Statistical validation pattern

### API Signatures

```python
class GateValidator:
    def __init__(self, config: DistillationConfig):
        """Initialize validator. config: gate thresholds"""
        self.config = config

    def validate_gate_criteria(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check MUST_WORK gate. Returns: {w2_criterion, exponential_fit, cross_domain, selective_advantage}"""
        criteria = {
            'w2_criterion': results['w2_distance'] < self.config.w2_threshold,  # < 0.05
            'exponential_fit': results['exponential_r2'] > self.config.exponential_fit_r2_threshold,  # > 0.95
            'cross_domain': results['cross_domain_delta'] < self.config.cross_domain_delta_threshold,  # < 0.03
            'selective_advantage': results['selective_lti_ratio'] < self.config.selective_advantage_threshold  # < 0.5
        }
        return criteria

    def generate_validation_report(
        self,
        results: Dict[str, Any],
        gate_status: Dict[str, bool]
    ) -> str:
        """Generate markdown report. Returns: 04_validation.md content"""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | Criterion checks | Validate 4 gate criteria |
| L-10-2 | Report generation | Write 04_validation.md with results |
| L-10-3 | PASS/FAIL decision | Determine gate status |

---

## Supporting Modules (No Budget Allocation)

### Config (`src/config.py`)

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DistillationConfig:
    # Model config
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layer: int = 28
    hf_token: Optional[str] = None

    # SSM config
    d_model: int = 4096
    ssm_state_sizes: List[int] = field(default_factory=lambda: [64, 128, 256, 512, 1024])
    d_conv: int = 4
    expand: int = 2

    # Data config
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    context_length: int = 4096

    # Training config
    stage1_tokens: int = 100_000_000
    stage1_lr: float = 1e-4
    stage2_tokens: int = 500_000_000
    stage2_lr: float = 5e-5
    lambda_jacobian: float = 0.1
    stage3_tokens: int = 2_400_000_000
    stage3_lr: float = 1e-5

    # Evaluation config
    longbench_tasks: List[str] = field(default_factory=lambda: ["narrativeqa", "qasper", "hotpotqa", "multifieldqa_en"])
    num_eval_samples: int = 100

    # Gate thresholds
    w2_threshold: float = 0.05
    exponential_fit_r2_threshold: float = 0.95
    cross_domain_delta_threshold: float = 0.03
    selective_advantage_threshold: float = 0.5

    # System config
    random_seed: int = 42
    output_dir: str = "docs/youra_research/20260318_scope/h-m2"

def load_config(config_path: Optional[str] = None) -> DistillationConfig:
    """Load config from YAML or use defaults. Returns: DistillationConfig"""
    ...
```

### ExperimentRunner (`src/main.py`)

```python
class DistillationExperimentRunner:
    def __init__(self, config: DistillationConfig):
        """Initialize runner."""
        self.config = config
        self.model_loader: Optional[LLaMALayerExtractor] = None
        self.data_module: Optional[DistillationDataModule] = None
        self.distiller: Optional[MOHAWKDistiller] = None
        self.evaluator: Optional[DistillationEvaluator] = None
        self.visualizer: Optional[DistillationVisualizer] = None
        self.validator: Optional[GateValidator] = None

    def setup_models(self) -> Tuple[nn.Module, SelectiveSSMAdapter, LTIControlAdapter]:
        """Load models. Returns: (teacher_layer, selective_adapter, lti_adapter)"""
        ...

    def setup_data(self) -> Tuple[DataLoader, Dict[str, DataLoader]]:
        """Setup data. Returns: (pile_loader, longbench_loaders)"""
        ...

    def run_mohawk_training(self) -> Dict[str, Any]:
        """Run 3-stage training. Returns: {stage1_losses, stage2_losses, stage3_losses, training_time}"""
        ...

    def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation suite. Returns: {mse, w2, cross_domain_delta, selective_lti_ratio, state_size_results}"""
        ...

    def validate_gate_criteria(self, results: Dict[str, Any]) -> Dict[str, bool]:
        """Validate gate. Returns: {criterion_name: pass_status}"""
        ...

    def generate_visualizations(self, results: Dict[str, Any]) -> None:
        """Generate 6 figures."""
        ...

    def write_validation_report(
        self,
        results: Dict[str, Any],
        gate_status: Dict[str, bool]
    ) -> None:
        """Write 04_validation.md."""
        ...

def main():
    """Entry point."""
    config = load_config()
    runner = DistillationExperimentRunner(config)

    # Setup
    runner.setup_models()
    runner.setup_data()

    # Training
    training_results = runner.run_mohawk_training()

    # Evaluation
    eval_results = runner.run_evaluation()

    # Gate validation
    gate_status = runner.validate_gate_criteria(eval_results)

    # Reporting
    runner.generate_visualizations(eval_results)
    runner.write_validation_report(eval_results, gate_status)
```

---

## Data Flow Summary

```
1. Model Loading:
   - Load LLaMA-2-7b-hf with HF token
   - Extract L28: model.model.layers[28].self_attn
   - Initialize SelectiveSSMAdapter(d_state=512) and LTIControlAdapter

2. Data Preparation:
   - Stream The Pile (or C4 fallback) for training
   - Load LongBench test split for evaluation
   - Tokenize with LLaMA tokenizer, context_length=4096

3. MOHAWK Training:
   - Stage 1: Matrix orientation (Frobenius loss, 100M tokens, lr=1e-4)
   - Stage 2: Hidden-state + Jacobian alignment (MSE + λW2, 500M tokens, lr=5e-5)
   - Stage 3: End-to-end distillation (MSE, 2.4B tokens, lr=1e-5)
   - Save checkpoints after each stage

4. State Size Sweep:
   - Train adapters for N ∈ {64, 128, 256, 512, 1024}
   - Use same 3-stage protocol for each N
   - Evaluate MSE and W2 for each N

5. LTI Control Training:
   - Train LTIControlAdapter with same protocol
   - Freeze dt_proj parameters before training

6. Evaluation:
   - MSE: F.mse_loss(teacher_output, student_output)
   - W2: Wasserstein-2 distance on Jacobian eigenvalues
   - Cross-domain: Compare Pile vs LongBench errors
   - Selective vs LTI: MSE ratio

7. Gate Validation:
   - Check W2 < 0.05 at N=512
   - Fit MSE(N) = a * exp(-b * N), check R² > 0.95
   - Check cross-domain delta < 3%
   - Check selective MSE / LTI MSE < 0.5

8. Visualization:
   - Generate 6 figures (MSE decay, eigenvalues, cross-domain, loss curves, selective vs LTI, gate metrics)

9. Reporting:
   - Write 04_validation.md with PASS/FAIL decision
```

---

## Memory Management

```python
# Clear GPU cache between stages
def run_mohawk_training():
    stage1_results = distiller.stage1_matrix_orientation(dataloader, 100_000_000)
    torch.cuda.empty_cache()

    stage2_results = distiller.stage2_hidden_state_alignment(dataloader, 500_000_000)
    torch.cuda.empty_cache()

    stage3_results = distiller.stage3_end_to_end(dataloader, 2_400_000_000)
    torch.cuda.empty_cache()

    return {**stage1_results, **stage2_results, **stage3_results}

# Gradient accumulation for memory efficiency
def training_step_with_accumulation(batch, accumulation_steps=4):
    for i, mini_batch in enumerate(split_batch(batch, accumulation_steps)):
        loss = compute_loss(mini_batch)
        (loss / accumulation_steps).backward()
        if (i + 1) % accumulation_steps == 0:
            optimizer.step()
            optimizer.zero_grad()
```

---

## Error Handling

```python
# Dataset fallback
try:
    pile_loader = data_module.get_pile_dataloader(num_tokens=3_000_000_000)
except Exception as e:
    print(f"The Pile unavailable ({e}), falling back to C4")
    pile_loader = data_module.create_fallback_c4_loader(num_tokens=3_000_000_000)

# HF token validation
try:
    model = model_loader.load_model()
except Exception as e:
    if "access token" in str(e).lower():
        raise ValueError("HF token required. Get token from meta.com/llama") from e
    else:
        raise e

# OOM handling
try:
    jacobian = jacobian_analyzer.compute_jacobian(model, inputs)
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        print("OOM during Jacobian computation. Reduce batch size or use checkpointing.")
        torch.cuda.empty_cache()
        # Retry with smaller batch
        jacobian = compute_jacobian_with_checkpointing(model, inputs)
    else:
        raise e
```

---

## Validation Logic

```python
def validate_gate_criteria(results):
    criteria = {
        'w2_criterion': results['w2_distance'] < 0.05,
        'exponential_fit': results['exponential_r2'] > 0.95,
        'cross_domain': results['cross_domain_delta'] < 0.03,
        'selective_advantage': results['selective_lti_ratio'] < 0.5
    }

    gate_passed = all(criteria.values())

    return {
        'gate_passed': gate_passed,
        'criteria': criteria,
        'w2_distance': results['w2_distance'],
        'exponential_r2': results['exponential_r2'],
        'cross_domain_delta': results['cross_domain_delta'],
        'selective_lti_ratio': results['selective_lti_ratio']
    }
```

---

*Logic specification for MECHANISM validation | Budget: 15 subtasks used | Green-field distillation framework*

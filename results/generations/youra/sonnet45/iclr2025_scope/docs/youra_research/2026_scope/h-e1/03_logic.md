---
hypothesis_id: h-e1
type: EXISTENCE
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Logic Design
---

# API Logic Specification: Low-Rank Structure Analysis (h-e1)

**Applied:** PyTorch hook registration pattern, torch.linalg.svd for effective rank computation, statistical regression pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - designing new APIs from scratch

---

## E-4: SVD Analysis [Complexity: 10, Budget: 5]

**Applied**: PyTorch torch.linalg.svd pattern

### API Signatures

```python
class LowRankAnalyzer:
    def __init__(
        self,
        model: AutoModelForCausalLM,
        target_layers: range,
        variance_threshold: float = 0.99
    ):
        """Initialize analyzer with model and configuration."""
        self.model = model
        self.target_layers = target_layers
        self.variance_threshold = variance_threshold
        self.attention_cache: Dict[int, List[Tensor]] = {}
        self.hooks: List[torch.utils.hooks.RemovableHandle] = []

    def compute_effective_rank(
        self,
        attention_matrix: Tensor,
        threshold: Optional[float] = None
    ) -> float:
        """Compute effective rank via SVD. attention_matrix: [B*H, L, L] -> scalar"""
        ...

    def analyze_layers(
        self,
        dataloader: DataLoader,
        num_samples: int = 100
    ) -> Dict[str, Any]:
        """Run full analysis pipeline. Returns: {layer_idx: {rank, entropy, singular_values}}"""
        ...

    def register_hooks(self) -> None:
        """Register forward hooks on target layers."""
        ...

    def clear_hooks(self) -> None:
        """Remove all registered hooks."""
        ...

    def _capture_attention(
        self,
        module: nn.Module,
        input: Tuple[Tensor],
        output: Tensor
    ) -> None:
        """Hook callback to cache attention outputs."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| attention_matrix | [B*H, L, L] | Batch×heads merged, sequence length |
| singular_values | [B*H, L] | Singular values per sample |
| eff_rank | [B*H] | Effective rank per sample |
| mean_rank | scalar | Average across samples |

### Pseudo-code

```
1. U, S, V = torch.linalg.svd(attention_matrix)  # [B*H, L, L] -> S: [B*H, L]
2. variance = S ** 2  # [B*H, L]
3. cumsum_variance = torch.cumsum(variance, dim=-1)  # [B*H, L]
4. total_variance = cumsum_variance[:, -1:]  # [B*H, 1]
5. explained_ratio = cumsum_variance / total_variance  # [B*H, L]
6. eff_rank = (explained_ratio < threshold).sum(dim=-1) + 1  # [B*H]
7. return eff_rank.float().mean().item()  # scalar
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | SVD decomposition | Implement torch.linalg.svd call with error handling |
| L-4-2 | Variance computation | Calculate cumulative variance explained |
| L-4-3 | Rank extraction | Find threshold crossing point |
| L-4-4 | Hook registration | Implement forward hook pattern |
| L-4-5 | Layer iteration | Loop over target layers with cache management |

---

## E-5: Entropy Analysis [Complexity: 9, Budget: 5]

**Applied**: Statistical regression pattern (scipy.stats.linregress)

### API Signatures

```python
class MetricsComputer:
    @staticmethod
    def svd_effective_rank(
        matrix: Tensor,
        threshold: float = 0.99
    ) -> float:
        """Compute effective rank from attention matrix. matrix: [B*H, L, L] -> scalar"""
        ...

    @staticmethod
    def operator_entropy(
        Q: Tensor,
        K: Tensor
    ) -> float:
        """Compute operator entropy from Q/K projections. Q/K: [D, D] -> scalar"""
        ...

    @staticmethod
    def entropy_regression(
        layer_indices: List[int],
        entropies: List[float]
    ) -> Dict[str, float]:
        """Fit linear regression. Returns: {slope, intercept, p_value, r_squared}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Q, K | [D, D] | Projection weight matrices |
| QK | [D, D] | Matrix product |
| cov | [D, D] | Covariance matrix |
| entropy | scalar | Log-determinant |

### Pseudo-code

```python
# Operator Entropy
1. QK = torch.matmul(Q, K.T)  # [D, D]
2. cov = torch.cov(QK)  # [D, D]
3. entropy = torch.logdet(cov + 1e-6)  # scalar (numerical stability)
4. return entropy.item()

# Regression
1. slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(layer_indices, entropies)
2. return {slope, intercept, p_value, r_value**2}
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | QK projection | Extract and multiply Q/K weight matrices |
| L-5-2 | Covariance computation | Compute torch.cov with stability |
| L-5-3 | Log-determinant | Calculate entropy via torch.logdet |
| L-5-4 | Linear regression | Fit slope and compute p-value |
| L-5-5 | Validation | Check β < 0 and p < 0.01 |

---

## Supporting Modules (No Budget Allocation)

### DataModule (`src/data.py`)

```python
class PileDataModule:
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_length: int,
        batch_size: int = 4
    ):
        """Initialize data module."""
        ...

    def setup(self, num_samples: int = 5000) -> None:
        """Load and prepare dataset."""
        ...

    def get_dataloader(self) -> DataLoader:
        """Return configured DataLoader. Yields: {input_ids: [B, L], attention_mask: [B, L]}"""
        ...
```

### Visualizer (`src/visualize.py`)

```python
class AnalysisVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        ...

    def plot_rank_vs_depth(self, results: Dict[int, Dict[str, Any]]) -> None:
        """Generate rank vs layer depth plot."""
        ...

    def plot_entropy_regression(
        self,
        results: Dict[int, Dict[str, Any]],
        regression_stats: Dict[str, float]
    ) -> None:
        """Generate entropy regression plot with fitted line."""
        ...

    def plot_singular_values(
        self,
        layer_idx: int,
        singular_values: Tensor
    ) -> None:
        """Generate singular value distribution heatmap. singular_values: [B*H, L]"""
        ...

    def plot_rank_sensitivity(
        self,
        thresholds: List[float],
        ranks: Dict[float, List[float]]
    ) -> None:
        """Generate threshold sensitivity plot."""
        ...

    def plot_gate_metrics(
        self,
        target_metrics: Dict[str, Any],
        actual_metrics: Dict[str, Any]
    ) -> None:
        """Generate gate validation metrics comparison."""
        ...
```

### ExperimentRunner (`src/main.py`)

```python
class ExperimentRunner:
    def __init__(self, config: AnalysisConfig):
        """Initialize experiment runner."""
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.analyzer: Optional[LowRankAnalyzer] = None
        self.dataloader: Optional[DataLoader] = None

    def setup_model(self) -> AutoModelForCausalLM:
        """Load model with fp16. Returns: loaded model"""
        ...

    def setup_data(self) -> DataLoader:
        """Prepare dataset and dataloader. Returns: configured DataLoader"""
        ...

    def run_analysis(self) -> Dict[str, Any]:
        """Execute full analysis pipeline. Returns: {layers: {rank, entropy, ...}, regression: {...}}"""
        ...

    def validate_results(self, results: Dict[str, Any]) -> bool:
        """Check MUST_WORK criteria. Returns: True if both metrics pass"""
        ...

    def generate_report(self, results: Dict[str, Any]) -> None:
        """Write 04_validation.md with pass/fail decision."""
        ...

def main():
    """Entry point for analysis experiment."""
    config = load_config()
    runner = ExperimentRunner(config)
    results = runner.run_analysis()
    passed = runner.validate_results(results)
    runner.generate_report(results)
```

### ConfigModule (`src/config.py`)

```python
from dataclasses import dataclass, field

@dataclass
class AnalysisConfig:
    """Configuration for low-rank analysis experiment."""
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layers: range = field(default_factory=lambda: range(20, 32))
    variance_threshold: float = 0.99
    num_samples: int = 5000
    context_length: int = 2048
    batch_size: int = 4
    random_seed: int = 42
    output_dir: str = "./results"

def load_config() -> AnalysisConfig:
    """Load configuration from environment or defaults."""
    ...
```

---

## Key Implementation Patterns

### Hook Registration Pattern

**Applied**: PyTorch forward hook pattern from torch.nn.Module

```python
# From LowRankAnalyzer.register_hooks()
def register_hooks(self) -> None:
    for layer_idx in self.target_layers:
        layer = self.model.model.layers[layer_idx]
        # Register on attention module output
        handle = layer.self_attn.register_forward_hook(self._capture_attention)
        self.hooks.append(handle)

def _capture_attention(
    self,
    module: nn.Module,
    input: Tuple[Tensor],
    output: Tensor
) -> None:
    # output: [B, H, L, L] or [B, L, D] depending on LLaMA version
    # Extract attention weights from output
    layer_idx = self._get_layer_index(module)
    if layer_idx not in self.attention_cache:
        self.attention_cache[layer_idx] = []
    self.attention_cache[layer_idx].append(output.detach())
```

### SVD Effective Rank Pattern

**Applied**: Standard PyTorch SVD decomposition with variance thresholding

```python
# From MetricsComputer.svd_effective_rank()
def svd_effective_rank(matrix: Tensor, threshold: float = 0.99) -> float:
    # Flatten batch and heads: [B, H, L, L] -> [B*H, L, L]
    batch_heads, seq_len = matrix.shape[0] * matrix.shape[1], matrix.shape[2]
    matrix = matrix.reshape(batch_heads, seq_len, seq_len)

    # SVD decomposition
    U, S, V = torch.linalg.svd(matrix)  # S: [B*H, L]

    # Compute variance explained
    variance = S ** 2
    cumsum_variance = torch.cumsum(variance, dim=-1)
    total_variance = cumsum_variance[:, -1:]
    explained_ratio = cumsum_variance / total_variance

    # Find threshold crossing
    eff_rank = (explained_ratio < threshold).sum(dim=-1) + 1  # [B*H]
    return eff_rank.float().mean().item()
```

### Operator Entropy Pattern

**Applied**: Log-determinant of covariance matrix for entropy estimation

```python
# From MetricsComputer.operator_entropy()
def operator_entropy(Q: Tensor, K: Tensor) -> float:
    # Extract projection matrices from layer.self_attn
    # Q, K: [D_model, D_model]

    # Compute QK product
    QK = torch.matmul(Q, K.T)  # [D, D]

    # Compute covariance
    cov = torch.cov(QK)  # [D, D]

    # Log-determinant with numerical stability
    entropy = torch.logdet(cov + 1e-6 * torch.eye(cov.shape[0], device=cov.device))

    return entropy.item()
```

---

## Data Flow Summary

```
1. Load Model → Register Hooks (layers 20-32)
2. Process Batches → Capture Attention Matrices via Hooks
3. For Each Layer:
   a. Compute Effective Rank (SVD)
   b. Extract Q/K Weights → Compute Operator Entropy
4. Linear Regression → Entropy vs Layer Depth (β, p-value)
5. Validate → r_eff < 256 (all L≥20) AND β < 0 (p < 0.01)
6. Generate Visualizations → 5 figures
7. Write Report → 04_validation.md with pass/fail
```

---

## Validation Logic

```python
def validate_results(results: Dict[str, Any]) -> bool:
    # Check effective rank criterion
    layers_data = results['layers']
    for layer_idx in range(20, 32):
        if layers_data[layer_idx]['effective_rank'] >= 256:
            return False

    # Check entropy regression criterion
    regression = results['regression']
    if regression['slope'] >= 0 or regression['p_value'] >= 0.01:
        return False

    return True
```

---

## Memory Management

```python
# Clear cache between batches to prevent OOM
def analyze_layers(self, dataloader, num_samples):
    for batch_idx, batch in enumerate(dataloader):
        if batch_idx >= num_samples:
            break

        # Forward pass (hooks capture automatically)
        with torch.no_grad():
            self.model(**batch)

        # Clear GPU cache every N batches
        if batch_idx % 10 == 0:
            torch.cuda.empty_cache()

    # Process cached attention matrices
    for layer_idx in self.target_layers:
        attention_stack = torch.cat(self.attention_cache[layer_idx], dim=0)
        rank = self.compute_effective_rank(attention_stack)
        ...
```

---

## Error Handling

```python
# SVD convergence issues
try:
    U, S, V = torch.linalg.svd(matrix)
except RuntimeError as e:
    print(f"SVD failed for layer {layer_idx}: {e}")
    # Fallback: Use torch.linalg.svd(matrix, driver='gesvd')
    U, S, V = torch.linalg.svd(matrix, driver='gesvd')

# Hook extraction issues
def _capture_attention(self, module, input, output):
    if output is None:
        print(f"Warning: Hook received None output for {module}")
        return
    # Store safely
    ...
```

---

*Logic specification for EXISTENCE validation | Budget: 5 subtasks (E-4) + 5 subtasks (E-5) | Total: 10 subtasks*

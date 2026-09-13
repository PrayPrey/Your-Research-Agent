---
hypothesis_id: h-e1
type: EXISTENCE
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Architecture Design
---

# System Architecture: Low-Rank Structure Analysis (h-e1)

**Applied:** PyTorch SVD analysis pattern, HuggingFace model loading pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch
**Analyzed Path**: N/A
**Findings**: No existing codebase. Custom SVD analysis for LLaMA attention matrices.

---

## Architecture Overview

**Type**: Analysis experiment (inference-only)
**Components**: 4 core modules
**Infrastructure**: Minimal (single-run script)

---

## Module Structure

### LowRankAnalyzer (`src/analyzer.py`)

**Dependencies**: torch, transformers

```python
class LowRankAnalyzer:
    def __init__(self, model: AutoModelForCausalLM, target_layers: range, variance_threshold: float = 0.99): ...

    def compute_effective_rank(self, attention_matrix: Tensor) -> float: ...

    def compute_operator_entropy(self, layer_idx: int) -> float: ...

    def analyze_layers(self, dataloader: DataLoader, num_samples: int = 100) -> dict: ...

    def register_hooks(self) -> None: ...

    def clear_hooks(self) -> None: ...
```

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers

```python
class PileDataModule:
    def __init__(self, tokenizer: AutoTokenizer, context_length: int, batch_size: int = 4): ...

    def setup(self, num_samples: int = 5000) -> None: ...

    def get_dataloader(self) -> DataLoader: ...
```

### MetricsComputer (`src/metrics.py`)

**Dependencies**: torch, scipy

```python
class MetricsComputer:
    @staticmethod
    def svd_effective_rank(matrix: Tensor, threshold: float = 0.99) -> float: ...

    @staticmethod
    def operator_entropy(Q: Tensor, K: Tensor) -> float: ...

    @staticmethod
    def entropy_regression(layer_indices: list, entropies: list) -> dict: ...
```

### Visualizer (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn

```python
class AnalysisVisualizer:
    def __init__(self, output_dir: str): ...

    def plot_rank_vs_depth(self, results: dict) -> None: ...

    def plot_entropy_regression(self, results: dict, regression_stats: dict) -> None: ...

    def plot_singular_values(self, layer_idx: int, singular_values: Tensor) -> None: ...

    def plot_rank_sensitivity(self, thresholds: list, ranks: dict) -> None: ...

    def plot_gate_metrics(self, target_metrics: dict, actual_metrics: dict) -> None: ...
```

### ExperimentRunner (`src/main.py`)

**Dependencies**: All above modules

```python
class ExperimentRunner:
    def __init__(self, config: dict): ...

    def setup_model(self) -> AutoModelForCausalLM: ...

    def setup_data(self) -> DataLoader: ...

    def run_analysis(self) -> dict: ...

    def validate_results(self, results: dict) -> bool: ...

    def generate_report(self, results: dict) -> None: ...

def main():
    config = load_config()
    runner = ExperimentRunner(config)
    results = runner.run_analysis()
    runner.validate_results(results)
    runner.generate_report(results)
```

### ConfigModule (`src/config.py`)

**Dependencies**: None

```python
@dataclass
class AnalysisConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    target_layers: range = field(default_factory=lambda: range(20, 32))
    variance_threshold: float = 0.99
    num_samples: int = 5000
    context_length: int = 2048
    batch_size: int = 4
    random_seed: int = 42
    output_dir: str = "./results"

def load_config() -> AnalysisConfig: ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── analyzer.py       # LowRankAnalyzer
│   │   ├── data.py           # PileDataModule
│   │   ├── metrics.py        # MetricsComputer
│   │   ├── visualize.py      # AnalysisVisualizer
│   │   ├── config.py         # AnalysisConfig
│   │   └── main.py           # ExperimentRunner
│   ├── run_analysis.sh       # GPU setup + execution script
│   └── requirements.txt
├── figures/                  # Generated visualizations
└── results/                  # Analysis outputs (JSON)
```

---

## Data Flow

1. **Setup**: Load LLaMA-7B model + register attention hooks on layers 20-32
2. **Inference**: Process 5K samples from The Pile, capture attention matrices
3. **Analysis**: Compute effective rank (SVD) and operator entropy per layer
4. **Regression**: Fit entropy vs layer depth, extract slope β and p-value
5. **Validation**: Check r_eff < 256 (all L≥20) and β < 0 (p < 0.01)
6. **Visualization**: Generate 5 figures (rank vs depth, entropy regression, singular values, sensitivity, gate metrics)
7. **Report**: Write 04_validation.md with pass/fail decision

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Environment Setup | Install dependencies, verify GPU, HuggingFace token setup | 5 | 2+1+1+1 |
| E-2 | Data Pipeline | Implement PileDataModule with streaming, tokenization, batching | 8 | 2+2+2+2 |
| E-3 | Model Loading | Load LLaMA-7B with hooks, register attention capture for layers 20-32 | 7 | 2+2+2+1 |
| E-4 | SVD Analysis | Implement effective rank computation (SVD decomposition, variance threshold) | 10 | 3+2+3+2 |
| E-5 | Entropy Analysis | Implement operator entropy computation (QK covariance, log-det, regression) | 9 | 3+2+2+2 |
| E-6 | Visualization | Generate 5 figures (rank, entropy, singular values, sensitivity, gate metrics) | 8 | 2+2+2+2 |
| E-7 | Validation Report | Validate success criteria, generate 04_validation.md with gate decision | 6 | 2+1+2+1 |

**Complexity Distribution:**
- High (9-10): [E-4, E-5]
- Medium (7-8): [E-2, E-3, E-6]
- Low (5-6): [E-1, E-7]

**Total Complexity**: 53

**Complexity Scoring:**
- Module_Size: 1-5 (lines of code / interfaces)
- Dependencies: 1-5 (number of external dependencies)
- Algorithm: 1-5 (mathematical/computational complexity)
- Integration: 1-5 (cross-module coordination)

---

## Breakdown: Task Complexity Details

### E-1: Environment Setup (5)
- Module_Size: 2 (shell script + requirements.txt)
- Dependencies: 1 (standard pip install)
- Algorithm: 1 (no complex logic)
- Integration: 1 (standalone setup)

### E-2: Data Pipeline (8)
- Module_Size: 2 (PileDataModule class)
- Dependencies: 2 (datasets, transformers)
- Algorithm: 2 (streaming + tokenization logic)
- Integration: 2 (connects to main runner)

### E-3: Model Loading (7)
- Module_Size: 2 (model setup in ExperimentRunner)
- Dependencies: 2 (transformers, torch)
- Algorithm: 2 (hook registration logic)
- Integration: 1 (used by analyzer)

### E-4: SVD Analysis (10)
- Module_Size: 3 (LowRankAnalyzer.compute_effective_rank + loop)
- Dependencies: 2 (torch.linalg.svd)
- Algorithm: 3 (SVD decomposition, variance computation)
- Integration: 2 (attention hook coordination)

### E-5: Entropy Analysis (9)
- Module_Size: 3 (operator_entropy + regression methods)
- Dependencies: 2 (torch, scipy.stats)
- Algorithm: 2 (covariance, log-det, linear fit)
- Integration: 2 (model weight extraction)

### E-6: Visualization (8)
- Module_Size: 2 (AnalysisVisualizer with 5 plot methods)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 2 (plotting logic)
- Integration: 2 (reads results dict)

### E-7: Validation Report (6)
- Module_Size: 2 (validate_results + generate_report)
- Dependencies: 1 (standard library)
- Algorithm: 2 (threshold checks, markdown generation)
- Integration: 1 (final stage, no downstream)

---

## Key Implementation Notes

### SVD Effective Rank Algorithm
```python
# From MetricsComputer
U, S, V = torch.linalg.svd(attention_matrix)  # (batch*heads, seq_len, seq_len)
variance = S ** 2
cumsum_variance = torch.cumsum(variance, dim=-1)
total_variance = cumsum_variance[:, -1:]
explained_ratio = cumsum_variance / total_variance
eff_rank = (explained_ratio < threshold).sum(dim=-1) + 1
return eff_rank.float().mean().item()
```

### Operator Entropy Computation
```python
# From MetricsComputer
Q = layer.self_attn.q_proj.weight  # (d_model, d_model)
K = layer.self_attn.k_proj.weight
QK = torch.matmul(Q, K.T)
cov = torch.cov(QK)
entropy = torch.logdet(cov + 1e-6)  # Numerical stability
return entropy.item()
```

### Attention Hook Registration
```python
# From LowRankAnalyzer
def register_hooks(self):
    for layer_idx in self.target_layers:
        layer = self.model.model.layers[layer_idx]
        hook = layer.self_attn.register_forward_hook(self._capture_attention)
        self.attention_hooks.append(hook)
```

---

## Validation Criteria

**Primary Metrics:**
1. r_eff < 256 for ALL layers 20-32 (12 layers)
2. β < 0 with p < 0.01 (entropy regression slope)

**PoC Pass Condition:**
- Both metrics satisfied → PASS (MUST_WORK gate satisfied)
- Any metric fails → FAIL (ABORT entire SSM conversion approach)

**Output:** `04_validation.md` with:
- Pass/fail decision
- Supporting data (r_eff per layer, regression stats)
- Gate recommendation (proceed/abort)

---

## Memory and Performance Constraints

**GPU Memory:**
- LLaMA-7B fp16: ~13GB
- Attention matrices (batch=4, seq=2048): ~2GB
- Total: <16GB (fits V100/A100)

**Execution Time:**
- Model loading: 5 min
- Inference (5K samples): 2-3 hours
- Analysis (SVD + metrics): 10 min
- Total: ~3.5 hours

**Optimization:**
- Use fp16 for model weights
- Clear cache between batches
- Process layers sequentially (not parallel)

---

## Dependencies

**External Libraries:**
- torch>=2.0.0 (SVD computation)
- transformers>=4.30.0 (LLaMA loading)
- datasets>=2.12.0 (The Pile streaming)
- scipy>=1.10.0 (linear regression)
- matplotlib>=3.5.0 (visualization)
- seaborn>=0.12.0 (visualization)

**Access Requirements:**
- HuggingFace token with LLaMA-2 access
- GPU: 1x A100 (40GB) or V100 (16GB)

---

*Architecture designed for EXISTENCE validation | Minimal infrastructure | Analysis-only (no training)*

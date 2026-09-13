# Architecture: H-M2 (TC-SSM)

**Applied**: LoRA-style low-rank modulation pattern (Hu et al. 2021)

## Executive Summary

TC-SSM adds low-rank (rank 16-64) task modulation to Mamba's Δ/B/C matrices,
reusing frozen task embeddings from H-M1 (`TaskEmbeddingEncoder`). Scope is a
computational-overhead + state-variance experiment, not full training: build
`LowRankProjection`, `TaskConditionedMamba`, FLOPs measurement, state-variance
ANOVA, and a rank ablation sweep. No new dataset infra beyond loading
SuperGLUE subsets for forward-pass inputs.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/models/task_embedding.py`
**Findings**: `TaskEmbeddingEncoder.forward(hidden_states: Tensor[B,seq,hidden_dim]) -> Tensor[B,embedding_dim]`. Reuse directly (frozen, `eval()` mode) rather than reimplementing — import from h-m1 checkpoint output.

## Module Structure

### LowRankProjection (`models/low_rank.py`)

**Dependencies**: none (nn.Module leaf)

```python
class LowRankProjection(nn.Module):
    def __init__(self, task_emb_dim: int, target_dim: int, rank: int = 32): ...
    def forward(self, task_embedding: Tensor) -> Tensor: ...  # [B, target_dim]
```

### TaskConditionedMamba (`models/tc_mamba.py`)

**Dependencies**: LowRankProjection, mamba_ssm.Mamba (external)

```python
class TaskConditionedMamba(nn.Module):
    def __init__(self, d_model: int, d_state: int, task_emb_dim: int, rank: int = 32): ...
    def forward(self, x: Tensor, task_embedding: Tensor) -> Tensor: ...  # [B, seq, d_model]
    def get_state(self, x: Tensor, task_embedding: Tensor) -> Tensor: ...  # for variance analysis
```

### VanillaMambaWrapper (`models/baseline_mamba.py`)

**Dependencies**: mamba_ssm.Mamba (external)

```python
class VanillaMambaWrapper(nn.Module):
    def __init__(self, d_model: int, d_state: int, d_conv: int = 4, expand: int = 2): ...
    def forward(self, x: Tensor) -> Tensor: ...
```

### FLOPs / overhead measurement (`analysis/flops.py`)

**Dependencies**: torch.profiler

```python
def count_flops(model: nn.Module, input_shape: tuple, task_emb_shape: tuple | None = None) -> float: ...
def measure_overhead(vanilla_model, tc_model, inputs: Tensor, task_embeddings: Tensor) -> float: ...  # ratio
def per_matrix_breakdown(tc_model: TaskConditionedMamba, inputs: Tensor, task_embeddings: Tensor) -> dict: ...
```

### State variance analysis (`analysis/state_variance.py`)

**Dependencies**: scipy.stats, TaskConditionedMamba

```python
def measure_state_variance(tc_model: TaskConditionedMamba, inputs: Tensor, task_embeddings_list: list[Tensor]) -> dict: ...
```

### Rank ablation framework (`ablation.py`)

**Dependencies**: TaskConditionedMamba, flops.measure_overhead

```python
def run_rank_ablation(ranks: list[int] = [16, 32, 64], d_model: int = 1024, d_state: int = 16) -> dict: ...
def run_matrix_ablation(variants: list[str] = ["delta_only", "all_matrices"]) -> dict: ...
```

### Experiment entrypoint (`run_experiment.py`)

**Dependencies**: all above + h-m1 TaskEmbeddingEncoder (external import)

```python
def load_task_embeddings(checkpoint_path: str) -> TaskEmbeddingEncoder: ...
def main() -> None: ...  # loads data, runs overhead+variance+ablation, writes results/figures
```

## File Organization

```
docs/youra_research/h-m2/code/
  config.py
  models/
    low_rank.py
    tc_mamba.py
    baseline_mamba.py
  analysis/
    flops.py
    state_variance.py
  ablation.py
  data.py               # loads boolq/rte/wic subsets, tokenize+batch
  run_experiment.py
  visualize.py          # bar chart, rank ablation plot, variance heatmap, pie chart
```

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| TaskEmbeddingEncoder | `from h_m1.models.task_embedding import TaskEmbeddingEncoder` | `docs/youra_research/h-m1/code/models/task_embedding.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, forward signature confirmed).

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load BoolQ/RTE/WiC subsets, tokenize, batch | 6 | 2+1+1+2 |
| A-2 | LowRankProjection module | Down/up linear, near-zero init | 4 | 1+1+1+1 |
| A-3 | VanillaMambaWrapper | Wrap mamba_ssm.Mamba baseline | 5 | 2+2+1+0 |
| A-4 | TaskConditionedMamba | Δ/B/C low-rank modulation + get_state | 14 | 4+3+4+3 |
| A-5 | Load frozen H-M1 embeddings | Import + checkpoint load util | 5 | 1+3+0+1 |
| A-6 | FLOPs/overhead measurement | torch.profiler + timing ratio + per-matrix breakdown | 10 | 3+2+3+2 |
| A-7 | State variance analysis | ANOVA across task embeddings | 8 | 2+2+3+1 |
| A-8 | Rank ablation framework | Sweep rank=16/32/64 + delta_only/all_matrices | 9 | 3+2+2+2 |
| A-9 | Visualization | Bar/line/heatmap/pie figures | 6 | 2+1+1+2 |
| A-10 | Experiment orchestration | run_experiment.py end-to-end, gate check | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-1(6 borderline→Low), A-6, A-8, A-10], Low(4-8): [A-2, A-3, A-5, A-7, A-9]

# Architecture: H-M4

**Type:** MECHANISM (FULL tier)
**Applied:** Cross-architecture delta-correlation pattern (extends H-E1 baseline-vs-proposed to 4-point Spearman correlation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (multiple: H-E1, H-M2, H-M3)
**Status:** patterns found from base code — no MCP tools available, so H-E1/H-M2/H-M3 `03_architecture.md` files read directly as ground truth for actual implemented interfaces.
**Analyzed Path:** `docs/youra_research/h-e1/03_architecture.md`, `docs/youra_research/h-m2/03_architecture.md`, `docs/youra_research/h-m3/03_architecture.md`
**Findings:** `h-e1/code/model.py` already defines `load_baseline_model` (Transformer+LoRA) and `MambaWithLoRA`/`load_proposed_model`, and `h-e1/code/data.py::load_benchmark` already loads all 4 target benchmarks (gsm8k, mmlu, hotpotqa, nq) with density values in `BENCHMARKS` config — reuse directly, no new model/data code needed. `h-m3/code/rank.py::compute_model_effective_rank` and `h_m1.code.landscape.measure_sharpness_sam` (via `h-m2/code/sharpness.py::measure_task_sharpness`) are reusable as-is for FR-5. Only new work: training loop over 2 architectures × 4 tasks (H-E1's loop assumed a fixed Llama baseline; H-M4 needs both models symmetric), accuracy-delta computation, and Spearman correlation/gate/visualization for 4 data points.

---

## External Dependencies (Base Hypotheses)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_benchmark | `from h_e1.code.data import load_benchmark` | `h-e1/code/data.py` |
| format_for_causal_lm | `from h_e1.code.data import format_for_causal_lm` | `h-e1/code/data.py` |
| load_baseline_model | `from h_e1.code.model import load_baseline_model` | `h-e1/code/model.py` |
| MambaWithLoRA, load_proposed_model | `from h_e1.code.model import MambaWithLoRA, load_proposed_model` | `h-e1/code/model.py` |
| BENCHMARKS, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA | `from h_e1.code.config import BENCHMARKS, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA` | `h-e1/code/config.py` |
| measure_task_sharpness | `from h_m2.code.sharpness import measure_task_sharpness` | `h-m2/code/sharpness.py` |
| compute_model_effective_rank | `from h_m3.code.rank import compute_model_effective_rank` | `h-m3/code/rank.py` |

**Verified from**: `h-e1/03_architecture.md`, `h-m2/03_architecture.md`, `h-m3/03_architecture.md` (actual implemented interfaces, per Serena-analysis notes embedded in those docs)

---

## Module Structure

```
h-m4/code/
├── config.py
├── train.py           (NEW: symmetric per-arch training loop)
├── evaluate.py         (NEW: accuracy delta + sharpness/rank aggregation)
├── correlate.py         (NEW: Spearman correlation + gate)
├── visualize.py
└── run_experiment.py
```

Reused unchanged: `h_e1.code.data.{load_benchmark,format_for_causal_lm}`, `h_e1.code.model.{load_baseline_model,MambaWithLoRA,load_proposed_model}`, `h_m2.code.sharpness.measure_task_sharpness`, `h_m3.code.rank.compute_model_effective_rank`.

### config.py

**Dependencies**: none

```python
LORA_CONFIG_TRANSFORMER = dict(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
LORA_CONFIG_MAMBA = dict(r=16, lora_alpha=32, target_modules=["in_proj"])
TRAIN_CONFIG = dict(lr=1e-4, weight_decay=0.01, grad_clip=1.0,
    batch_size=4, epochs=5, patience=2, seed=42)
SHARPNESS_CONFIG = dict(sam_epsilon=0.05, max_batches=50)
RANK_CONFIG = dict(threshold=0.90)
BENCHMARKS = {
    "gsm8k": dict(hf_id="gsm8k", subset="main", split="test", num_samples=1319, density=0.1),
    "mmlu": dict(hf_id="cais/mmlu", subset="all", split="test", num_samples=14042, density=0.5),
    "hotpotqa": dict(hf_id="hotpot_qa", subset="fullwiki", split="validation", num_samples=7405, density=0.7),
    "nq": dict(hf_id="natural_questions", subset=None, split="validation", num_samples=3610, density=0.9),
}
GATE_RHO_THRESHOLD = 0.7
GATE_P_THRESHOLD = 0.01
```

### train.py (`code/train.py`)

**Dependencies**: config.py, h_e1.code.data, h_e1.code.model

```python
def train_one_run(model_fn: "Callable", lora_config: dict, task_name: str,
                   train_config: dict) -> dict:
    """Loads benchmark via h_e1.data.load_benchmark, formats, fine-tunes fresh
    LoRA model_fn()+lora_config on task. Returns
    {'model', 'loss_curve': list, 'checkpoint_path': str}"""
    ...

def run_all_training() -> dict:
    """Loop over 2 architectures x 4 BENCHMARKS = 8 runs.
    Returns {(arch, task): train_one_run(...) result}"""
    ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config.py, h_m2.code.sharpness, h_m3.code.rank

```python
def evaluate_run(model: "nn.Module", dataset, task_name: str) -> dict:
    """Accuracy (EM/MCQ per task type) + measure_task_sharpness (h_m2) +
    compute_model_effective_rank (h_m3, threshold=0.90).
    Returns {'accuracy', 'sharpness', 'effective_rank'}"""
    ...

def compute_deltas(transformer_metrics: dict, mamba_metrics: dict) -> dict:
    """Per task: {'accuracy_delta', 'sharpness_delta', 'rank_delta'} = mamba - transformer"""
    ...

def build_results_table(training_results: dict) -> dict:
    """Runs evaluate_run for all 8 (arch,task) pairs, then compute_deltas per task.
    Returns {task_name: {'transformer':..., 'mamba':..., 'delta':..., 'density': float}}"""
    ...
```

### correlate.py (`code/correlate.py`)

**Dependencies**: config.py, scipy.stats

```python
def compute_spearman_gate(densities: list, accuracy_deltas: list) -> dict:
    """scipy.stats.spearmanr(densities, accuracy_deltas).
    Returns {'rho', 'p_value', 'gate_pass': abs(rho)>0.7 and p<0.01}"""
    ...

def check_monotonicity(deltas: list) -> bool:
    """All non-increasing or all non-decreasing (density-ordered)."""
    ...

def run_ablation_density_operationalization(results_table: dict) -> dict:
    """A-1: recompute rho under binary density {0,0,1,1} vs continuous."""
    ...

def run_ablation_efficiency_metric(results_table: dict) -> dict:
    """A-2: recompute rho using sharpness_delta and rank_delta instead of accuracy_delta."""
    ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: correlate.py

```python
def plot_density_vs_delta(results_table: dict, rho_result: dict, out_path: str) -> None:
    """Required: scatter density vs accuracy_delta, regression line, rho annotated."""
    ...
def plot_architecture_comparison(results_table: dict, out_path: str) -> None:
    """Bar chart: Transformer vs Mamba accuracy per task."""
    ...
def plot_sharpness_delta_by_task(results_table: dict, out_path: str) -> None:
    ...
def plot_summary_dashboard(results_table: dict, rho_result: dict, ablations: dict, out_path: str) -> None:
    ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config.py, train.py, evaluate.py, correlate.py, visualize.py

```python
def main() -> dict:
    """1. run_all_training (8 runs: 2 arch x 4 tasks)
       2. build_results_table (accuracy/sharpness/rank + deltas)
       3. compute_spearman_gate on (density, accuracy_delta)
       4. check_monotonicity
       5. run ablations A-1, A-2
       6. save all figures to h-m4/figures/
       Returns {'gate_result': dict, 'results_table': dict, 'ablations': dict, 'figures': list[str]}"""
    ...
```

---

## Data Flow

`config.BENCHMARKS` → `h_e1.data.load_benchmark` (x4) → `train.run_all_training` (x2 archs, via `h_e1.model.{load_baseline_model,load_proposed_model}`) → `evaluate.build_results_table` (accuracy + `h_m2.sharpness` + `h_m3.rank`) → `evaluate.compute_deltas` → `correlate.compute_spearman_gate` (primary gate) → `correlate.run_ablation_*` → `visualize.*` → figures in `h-m4/figures/`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M4-1 | Setup & config | config.py: LoRA configs (both arch), train/sharpness/rank configs, BENCHMARKS w/ density | 3 | 1+0+1+1 |
| M4-2 | Data pipeline verification | Reuse h_e1.load_benchmark for 4 datasets, verify tokenization consistency, 26,376 samples | 4 | 1+1+1+1 |
| M4-3 | Transformer training runs | train_one_run x4 tasks using h_e1.load_baseline_model, save checkpoints/loss curves | 7 | 2+2+1+2 |
| M4-4 | Mamba training runs | train_one_run x4 tasks using h_e1.load_proposed_model, save checkpoints/loss curves | 7 | 2+2+1+2 |
| M4-5 | Per-run evaluation | evaluate_run: accuracy (EM/MCQ) + h_m2 sharpness + h_m3 effective rank for all 8 runs | 8 | 2+2+2+2 |
| M4-6 | Delta computation | compute_deltas, build_results_table wiring density + transformer/mamba/delta per task | 5 | 1+1+2+1 |
| M4-7 | Spearman correlation + gate | compute_spearman_gate (primary), check_monotonicity (secondary) | 5 | 1+1+2+1 |
| M4-8 | Ablations | A-1 density operationalization (binary vs continuous), A-2 efficiency metric (sharpness/rank delta) | 7 | 2+2+2+1 |
| M4-9 | Visualization suite | 4 plots: density-vs-delta (required), arch comparison, sharpness delta, summary dashboard | 6 | 2+1+1+2 |
| M4-10 | End-to-end integration run | Wire train->evaluate->correlate->ablate->visualize across 8 runs, produce final gate report | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M4-1, M4-2, M4-3, M4-4, M4-5, M4-6, M4-7, M4-8, M4-9, M4-10]

**Total tasks**: 10 (within 6-12 epic range, ≤30 task budget)

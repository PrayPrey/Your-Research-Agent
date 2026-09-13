# Architecture Specification: h-e1

**Date:** 2026-04-19
**Hypothesis:** EXISTENCE - Oracle gap G_o ≥ 10% between per-task oracle and best fixed-rank baseline
**Infrastructure Tier:** LIGHT (minimal config, basic logging, smoke tests)
**Project Type:** Green-field (no existing codebase)

**Applied Patterns:**
- Multi-task adapter training pattern
- LoRA parameter-efficient fine-tuning pattern
- Pareto optimization evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing code to analyze - foundational hypothesis with minimal PoC structure

---

## Module Structure

### 1. DataModule (`data/loader.py`)

**Dependencies:** None (external HuggingFace datasets only)

```python
class MultiDomainDataset:
    def __init__(self, tasks: list[str], tokenizer, max_length: int = 512): ...
    def load_glue_tasks(self) -> dict: ...
    def load_xtreme_tasks(self) -> dict: ...
    def preprocess_task(self, task_name: str, dataset) -> Dataset: ...
    def get_dataloader(self, task_name: str, batch_size: int, split: str) -> DataLoader: ...
```

**Key Interfaces:**
- Returns dict mapping task_name → DataLoader
- Handles 9 GLUE tasks + 8 XTREME tasks (17 total)
- Tokenization with LLaMA-2 tokenizer

---

### 2. ModelModule (`models/lora_adapter.py`)

**Dependencies:** DataModule (for task metadata)

```python
class MultiRankLoRAFactory:
    def __init__(self, base_model_name: str = "meta-llama/Llama-2-7b-hf", ranks: list[int] = [4, 8, 16, 32]): ...
    def create_adapter(self, rank: int, num_labels: int) -> PeftModel: ...
    def count_parameters(self, model) -> int: ...
    def count_flops(self, model, input_shape: tuple) -> int: ...

class LoRATrainer:
    def __init__(self, model, optimizer_config: dict, scheduler_config: dict): ...
    def train_epoch(self, train_loader: DataLoader, val_loader: DataLoader) -> dict: ...
    def evaluate(self, val_loader: DataLoader) -> dict: ...
    def save_adapter(self, path: str): ...
```

**Key Interfaces:**
- Creates 4 LoRA configurations per task (ranks 4, 8, 16, 32)
- Returns trained adapter with metrics (accuracy, FLOPs, params)
- Targets: q_proj, v_proj attention layers

---

### 3. TrainingModule (`training/orchestrator.py`)

**Dependencies:** DataModule, ModelModule

```python
class MultiTaskOrchestrator:
    def __init__(self, tasks: list[str], ranks: list[int], output_dir: str): ...
    def train_all_configurations(self) -> dict: ...
    def train_single_task_rank(self, task_name: str, rank: int) -> dict: ...
    def save_results(self, results: dict, output_path: str): ...
```

**Key Interfaces:**
- Orchestrates 68 training runs (17 tasks × 4 ranks)
- Returns dict: {task_name: {rank: {accuracy, flops, params}}}
- Saves intermediate checkpoints per task-rank combination

---

### 4. EvaluationModule (`evaluation/metrics.py`)

**Dependencies:** ModelModule

```python
class OracleGapCalculator:
    def __init__(self, results: dict, ref_point: tuple = (0.0, 1e12)): ...
    def compute_hypervolume(self, points: list[tuple]) -> float: ...
    def compute_oracle_hv(self) -> float: ...
    def compute_fixed_rank_hv(self, rank: int) -> float: ...
    def compute_oracle_gap(self) -> dict: ...

class TaskMetrics:
    def __init__(self, task_type: str): ...
    def compute_accuracy(self, predictions, labels) -> float: ...
    def compute_f1(self, predictions, labels) -> float: ...
    def compute_pearson(self, predictions, labels) -> float: ...
```

**Key Interfaces:**
- Computes hypervolume for oracle and fixed-rank configurations
- Returns oracle gap G_o = HV(Oracle) - max_r HV(Fixed_r)
- Task-specific metrics (accuracy, F1, Pearson for STS-B)

---

### 5. VisualizationModule (`visualization/plots.py`)

**Dependencies:** EvaluationModule

```python
class ExperimentVisualizer:
    def __init__(self, results: dict, output_dir: str): ...
    def plot_pareto_fronts(self, results: dict) -> None: ...
    def plot_oracle_comparison(self, oracle_gap_results: dict) -> None: ...
    def plot_rank_selection_heatmap(self, results: dict) -> None: ...
    def plot_task_heterogeneity(self, results: dict) -> None: ...
    def plot_efficiency_tradeoff(self, results: dict) -> None: ...
    def save_all_figures(self) -> None: ...
```

**Key Interfaces:**
- Generates 5 required figures (Pareto fronts, oracle comparison, heatmap, heterogeneity, trade-off)
- Saves to `figures/` subdirectory
- Returns figure paths for documentation

---

### 6. ConfigModule (`config.py`)

**Dependencies:** None

```python
# Hardcoded configuration (LIGHT tier - no YAML)
GLUE_TASKS = ["cola", "sst2", "mrpc", "qqp", "stsb", "mnli", "qnli", "rte", "wnli"]
XTREME_TASKS = {
    "xnli": ["en", "es", "de", "zh"],
    "paws-x": ["en", "es", "de", "zh"]
}
LORA_RANKS = [4, 8, 16, 32]
BASE_MODEL = "meta-llama/Llama-2-7b-hf"
MAX_SEQ_LENGTH = 512
BATCH_SIZE = 16
LEARNING_RATE = 3e-4
EPOCHS_SMALL = 5  # <10k samples
EPOCHS_LARGE = 3  # >50k samples
SEED = 42
```

---

### 7. MainScript (`main.py`)

**Dependencies:** All modules

```python
def main():
    # 1. Load datasets (17 tasks)
    data_module = MultiDomainDataset(...)
    
    # 2. Create model factory
    model_factory = MultiRankLoRAFactory(...)
    
    # 3. Train all configurations (68 runs)
    orchestrator = MultiTaskOrchestrator(...)
    results = orchestrator.train_all_configurations()
    
    # 4. Compute oracle gap
    calculator = OracleGapCalculator(results)
    oracle_gap = calculator.compute_oracle_gap()
    
    # 5. Generate visualizations
    visualizer = ExperimentVisualizer(results, ...)
    visualizer.save_all_figures()
    
    # 6. Print results (LIGHT tier - CSV output)
    print(f"Oracle Gap: {oracle_gap['normalized']:.2f}%")
    save_results_csv(results, oracle_gap)
```

---

## File Organization

```
h-e1/
├── code/
│   ├── main.py                    # Entry point
│   ├── config.py                  # Hardcoded configuration
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py              # MultiDomainDataset
│   ├── models/
│   │   ├── __init__.py
│   │   └── lora_adapter.py        # MultiRankLoRAFactory, LoRATrainer
│   ├── training/
│   │   ├── __init__.py
│   │   └── orchestrator.py        # MultiTaskOrchestrator
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py             # OracleGapCalculator, TaskMetrics
│   └── visualization/
│       ├── __init__.py
│       └── plots.py               # ExperimentVisualizer
├── results/
│   ├── checkpoints/               # Per task-rank adapter weights
│   ├── metrics.csv                # All 68 configurations
│   └── oracle_gap.csv             # Final oracle gap results
├── figures/
│   ├── pareto_fronts.png
│   ├── oracle_comparison.png
│   ├── rank_heatmap.png
│   ├── task_heterogeneity.png
│   └── efficiency_tradeoff.png
└── logs/
    └── training.log               # Print-based logging
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Infrastructure | Load and preprocess 17 tasks (9 GLUE + 8 XTREME) with HuggingFace datasets | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| A-2 | LoRA Adapter Factory | Implement multi-rank LoRA adapter creation with PEFT library (4 ranks) | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-3 | Training Orchestration | Build 68-configuration training loop (17 tasks × 4 ranks) with checkpointing | 14 | Module(4) + Deps(3) + Algo(4) + Integ(3) |
| A-4 | Oracle Gap Evaluation | Compute hypervolume for oracle vs fixed-rank baselines using pymoo | 12 | Module(3) + Deps(2) + Algo(4) + Integ(3) |
| A-5 | Visualization Pipeline | Generate 5 required figures (Pareto, oracle, heatmap, heterogeneity, trade-off) | 9 | Module(3) + Deps(2) + Algo(2) + Integ(2) |

**Total Epic Tasks:** 5 (EXISTENCE tier: 4-8 tasks)
**Total Complexity:** 56 points
**Distribution:** High(14-17): [A-3], Medium(9-13): [A-1, A-2, A-4, A-5], Low(4-8): []

---

## Dependencies

### External Libraries

```python
# Core ML
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0              # LoRA implementation
datasets>=2.14.0         # GLUE + XTREME loading

# Evaluation
evaluate>=0.4.0          # HuggingFace metrics
torchmetrics>=1.0.0      # Additional metrics
pymoo>=0.6.0             # Hypervolume computation
fvcore>=0.1.5            # FLOPs counting

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Utilities
numpy>=1.24.0
pandas>=2.0.0
tqdm>=4.65.0
```

### Hardware Requirements

- GPU: 1× A100 40GB (or similar)
- CUDA: 11.8+
- Storage: ~50GB (model + checkpoints + datasets)
- Estimated Runtime: 140-200 hours (68 training runs × 2-3 hours each)

---

## Integration Points

### Task Orchestration Flow

```
main.py
  └─> MultiDomainDataset.load_all_tasks()
       └─> Returns 17 task dataloaders
  └─> MultiTaskOrchestrator.train_all_configurations()
       └─> For each task in 17 tasks:
            └─> For each rank in [4, 8, 16, 32]:
                 └─> MultiRankLoRAFactory.create_adapter(rank)
                 └─> LoRATrainer.train_epoch() × epochs
                 └─> Save checkpoint
  └─> OracleGapCalculator.compute_oracle_gap()
       └─> Compute HV(Oracle) and HV(Fixed_r) for r in [4,8,16,32]
  └─> ExperimentVisualizer.save_all_figures()
```

### Data Flow

1. **Dataset Loading:** HuggingFace datasets → Tokenization → DataLoader
2. **Model Creation:** Base LLaMA-2-7B → LoraConfig(rank) → PeftModel
3. **Training:** DataLoader → LoRATrainer → Metrics (accuracy, FLOPs, params)
4. **Evaluation:** All results → OracleGapCalculator → G_o value
5. **Output:** CSV files + 5 figures

---

## Success Criteria

**PoC Pass Conditions:**
1. ✅ All 68 configurations train without error
2. ✅ Oracle gap G_o ≥ 10% (normalized)
3. ✅ HV(Oracle) > HV(Fixed_r) for all r ∈ {4, 8, 16, 32}

**MUST_WORK Gate:**
- Oracle gap G_o ≥ 10% exists between per-task oracle and best fixed-rank baseline
- If this fails, entire POAR hypothesis lacks foundation

---

## Implementation Notes

### EXISTENCE Simplifications

**What's Minimal (PoC):**
- Single seed (42) - no statistical testing
- Print + CSV logging (no structured logging framework)
- Hardcoded config (no YAML/JSON config files)
- Smoke test only (manual verification of 2-3 tasks before full run)
- No ablation modules (baseline vs proposed only)

**What's Still Required:**
- Full 68 training runs (17 tasks × 4 ranks)
- All 5 visualization figures
- Hypervolume computation with pymoo
- Oracle gap calculation

### Training Efficiency

**Parallelization Strategy (if multiple GPUs available):**
- Each task-rank combination is independent
- Can distribute across GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,3`
- Reduce wall-clock time from 200 hours to 50 hours with 4 GPUs

**Checkpointing:**
- Save adapter weights after each task-rank training
- Resume capability: Check `results/checkpoints/` for existing runs
- Skip completed configurations on restart

---

## Complexity Scoring Details

**A-1: Dataset Infrastructure (11)**
- Module Size: 3 (data loader + preprocessor + task mapper)
- Dependencies: 2 (HuggingFace datasets + transformers tokenizer)
- Algorithm: 3 (tokenization + dynamic padding + task-specific preprocessing)
- Integration: 3 (17 tasks with different schemas)

**A-2: LoRA Adapter Factory (10)**
- Module Size: 3 (factory + trainer + metrics)
- Dependencies: 2 (PEFT + base model)
- Algorithm: 3 (LoRA configuration + parameter counting + FLOPs)
- Integration: 2 (plug into HuggingFace models)

**A-3: Training Orchestration (14)**
- Module Size: 4 (orchestrator + checkpoint manager + resume logic + progress tracking)
- Dependencies: 3 (data + model + evaluation)
- Algorithm: 4 (nested loops + early stopping + checkpointing)
- Integration: 3 (coordinate 68 independent runs)

**A-4: Oracle Gap Evaluation (12)**
- Module Size: 3 (hypervolume + oracle selection + gap calculation)
- Dependencies: 2 (pymoo + training results)
- Algorithm: 4 (hypervolume computation + Pareto optimization)
- Integration: 3 (aggregate 68 results into oracle vs fixed comparison)

**A-5: Visualization Pipeline (9)**
- Module Size: 3 (5 plot functions + save manager)
- Dependencies: 2 (matplotlib + evaluation results)
- Algorithm: 2 (standard plotting + heatmap generation)
- Integration: 2 (consistent styling across 5 figures)

---

*Generated for Phase 3 - Implementation Planning*
*Next Phase: Phase 4 - Code Implementation (68 LoRA training runs)*

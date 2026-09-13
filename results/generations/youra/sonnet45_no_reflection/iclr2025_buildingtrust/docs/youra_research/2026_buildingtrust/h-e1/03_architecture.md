# Architecture Specification: h-e1

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-E1 (EXISTENCE)  
**Type:** Proof-of-Concept  

**Applied Patterns:** PyTorch module pattern, HuggingFace transformers integration

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: No existing codebase to analyze. This is a foundation hypothesis with minimal architecture for EXISTENCE validation.

---

## Design Principles

**EXISTENCE Architecture:**
- Minimal structure for "does cross-dimensional trustworthiness correlation exist?"
- Single model (Llama-3-8B), 3 replicates for PoC
- No ablation modules or complex infrastructure
- Direct evaluation using HuggingFace datasets

**File Count:** 7 core files (data, model, train, evaluate, config, utils, visualize)

---

## Module Structure

### DataModule (`src/data.py`)

**Dependencies**: torch, transformers, datasets

```python
class TrustworthinessDataset:
    def __init__(self, dimension: str, split: str): ...
    def load_truthfulqa(self) -> Dataset: ...
    def load_bbq(self) -> Dataset: ...
    def load_advglue(self) -> Dataset: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class DataCollator:
    def __init__(self, tokenizer): ...
    def __call__(self, features: list[dict]) -> dict: ...
```

---

### ModelModule (`src/model.py`)

**Dependencies**: torch, transformers, peft

```python
class BaselineModel:
    def __init__(self, model_id: str): ...
    def load_model(self) -> AutoModelForCausalLM: ...
    def load_tokenizer(self) -> AutoTokenizer: ...
    def evaluate(self, dataset: Dataset, dimension: str) -> float: ...

class LoRAInterventionModel:
    def __init__(self, base_model, lora_rank: int): ...
    def apply_lora(self) -> PeftModel: ...
    def get_trainable_params(self) -> list: ...
```

---

### TrainingModule (`src/train.py`)

**Dependencies**: torch, transformers, peft, scipy

```python
class InterventionTrainer:
    def __init__(self, model, config: dict): ...
    def setup_optimizer(self, lr: float) -> AdamW: ...
    def setup_scheduler(self, optimizer, num_steps: int): ...
    def train_epoch(self, dataloader) -> dict: ...
    def run_intervention(self, target_dimension: str) -> dict: ...

def train_single_replicate(
    base_model, 
    target_dimension: str, 
    lr: float, 
    epochs: int, 
    lora_rank: int, 
    seed: int
) -> dict: ...
```

---

### EvaluationModule (`src/evaluate.py`)

**Dependencies**: torch, transformers, scipy

```python
class TruthfulQAEvaluator:
    def __init__(self, model, tokenizer): ...
    def compute_mc1(self, dataset) -> float: ...
    def compute_mc2(self, dataset) -> float: ...

class BBQEvaluator:
    def __init__(self, model, tokenizer): ...
    def compute_bias_score(self, dataset) -> float: ...
    def compute_disambiguation_accuracy(self, dataset) -> float: ...

class AdvGLUEEvaluator:
    def __init__(self, model, tokenizer): ...
    def compute_adversarial_accuracy(self, dataset, task: str) -> float: ...

class CorrelationAnalyzer:
    def __init__(self, results: list[dict]): ...
    def extract_delta_scores(self, baseline_scores: dict) -> dict: ...
    def compute_pearson_correlation(self, dim1: str, dim2: str) -> tuple: ...
    def test_significance(self, rho: float, n: int) -> float: ...
```

---

### ConfigModule (`src/config.py`)

**Dependencies**: dataclasses

```python
@dataclass
class ExperimentConfig:
    model_id: str = "meta-llama/Meta-Llama-3-8B"
    target_dimension: str = "truthfulness"
    n_replicates: int = 3
    lora_ranks: list[int] = None
    learning_rates: list[float] = None
    epochs_list: list[int] = None
    seed: int = 1
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    device: str = "cuda"
    output_dir: str = "./results"

def load_config(config_path: str) -> ExperimentConfig: ...
def save_config(config: ExperimentConfig, path: str): ...
```

---

### UtilsModule (`src/utils.py`)

**Dependencies**: torch, random, numpy, json

```python
def set_seed(seed: int): ...
def save_results(results: dict, path: str): ...
def load_results(path: str) -> dict: ...
def setup_gpu(device_id: int = 0): ...
def get_parameter_count(model) -> int: ...
def format_metrics(metrics: dict) -> str: ...
```

---

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class FigureGenerator:
    def __init__(self, results: dict, output_dir: str): ...
    def plot_correlation_heatmap(self, correlation_matrix: dict): ...
    def plot_scatter_grid(self, deltas: dict): ...
    def plot_delta_distributions(self, deltas: dict): ...
    def plot_intervention_effects(self, mean_deltas: dict): ...
    def plot_significance_map(self, p_values: dict): ...
    def save_all_figures(self): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data.py          # Dataset loading and preprocessing
│   │   ├── model.py         # Baseline and LoRA models
│   │   ├── train.py         # Training loop and intervention
│   │   ├── evaluate.py      # Benchmark evaluators + correlation
│   │   ├── config.py        # Experiment configuration
│   │   ├── utils.py         # Helper functions
│   │   └── visualize.py     # Figure generation
│   ├── main.py              # Entry point orchestrator
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Setup and usage instructions
├── results/
│   ├── baseline_scores.json
│   ├── intervention_results.json
│   └── correlation_analysis.json
└── figures/
    ├── correlation_heatmap.png
    ├── scatter_grid.png
    ├── delta_distributions.png
    ├── intervention_effects.png
    └── significance_map.png
```

---

## Entry Point (`main.py`)

**Dependencies**: All src modules

```python
def main():
    config = load_config("config.yaml")
    set_seed(config.seed)
    setup_gpu(0)
    
    # Load baseline model
    baseline = BaselineModel(config.model_id)
    
    # Measure baseline scores
    baseline_scores = evaluate_baseline(baseline, config)
    
    # Run intervention replicates
    results = []
    for i in range(config.n_replicates):
        replicate_scores = train_single_replicate(
            baseline.model,
            config.target_dimension,
            lr=config.learning_rates[i],
            epochs=config.epochs_list[i],
            lora_rank=config.lora_ranks[i],
            seed=config.seed + i
        )
        results.append(replicate_scores)
    
    # Compute cross-dimensional correlations
    analyzer = CorrelationAnalyzer(results)
    correlations = analyzer.compute_all_correlations(baseline_scores)
    
    # Generate visualizations
    visualizer = FigureGenerator(results, config.output_dir)
    visualizer.save_all_figures()
    
    # Save results
    save_results(correlations, f"{config.output_dir}/correlation_analysis.json")

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Initialize codebase, dependencies, and file structure | 5 | Module(2) + Deps(1) + Algo(1) + Integ(1) |
| A-2 | Data Loading | Implement TruthfulQA, BBQ, AdvGLUE dataset loaders | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-3 | Model Implementation | Baseline model + LoRA intervention mechanism | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-4 | Training Pipeline | Intervention training loop with perturbation sampling | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Evaluation System | Implement 3 benchmark evaluators + correlation analysis | 11 | Module(3) + Deps(3) + Algo(3) + Integ(2) |
| A-6 | Experiment Orchestration | Main workflow: baseline → interventions → correlation | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-7 | Visualization | Generate 5 required figures (heatmap, scatter, etc.) | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |

**Distribution**: 
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-3, A-4, A-5]
- Low (4-8): [A-1, A-2, A-6, A-7]

**Total Complexity**: 56 points across 7 tasks

---

## Dependencies

### Core Libraries
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
```

### Analysis & Visualization
```
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Utilities
```
PyYAML>=6.0
tqdm>=4.65.0
```

---

## Task Breakdown Details

**A-1: Project Setup** (5 points)
- Create directory structure
- Initialize requirements.txt
- Setup __init__.py files
- Create config.yaml template

**A-2: Data Loading** (8 points)
- Implement TruthfulQA loader (MC1, MC2, Gen variants)
- Implement BBQ loader (9 categories, disambig/ambig)
- Implement AdvGLUE loader (5 tasks)
- Create unified DataCollator with tokenization

**A-3: Model Implementation** (10 points)
- BaselineModel class (load Llama-3-8B, tokenizer)
- LoRA configuration and application
- Model inference methods for all 3 benchmarks
- Memory optimization (gradient checkpointing)

**A-4: Training Pipeline** (9 points)
- InterventionTrainer with AdamW optimizer
- Cosine scheduler with warmup
- Training loop for single dimension fine-tuning
- Hyperparameter perturbation sampling logic

**A-5: Evaluation System** (11 points)
- TruthfulQAEvaluator (MC1, MC2 metrics)
- BBQEvaluator (Bias Score, Disambiguation Accuracy)
- AdvGLUEEvaluator (Adversarial Accuracy per task)
- CorrelationAnalyzer (Pearson ρ, Fisher z-test, delta extraction)

**A-6: Experiment Orchestration** (7 points)
- Main workflow orchestrator
- Baseline measurement phase
- Intervention loop (N=3 replicates)
- Results aggregation and saving

**A-7: Visualization** (6 points)
- Correlation heatmap (3×3 matrix)
- Scatter plot grid (3 dimension pairs)
- Delta distribution histograms
- Intervention effects bar chart
- Significance map (p<0.01 threshold)

---

## Validation Criteria

### Code Quality
- Type hints on all function signatures
- Docstrings for public methods
- Error handling for HuggingFace API calls
- GPU memory management

### Success Metrics (PoC)
- Code runs without error on single GPU
- Target dimension shows improvement (Δ > 0)
- Cross-dimensional correlation computed for all pairs
- All 5 figures generated

### Gate Metric (Full Experiment)
- ≥80% configurations show |ρ| > 0 with p<0.01
- At least one dimension pair with |ρ| > 0.3

---

*Generated by Phase 3 Architecture Agent*  
*Patterns Applied: PyTorch module structure, HuggingFace transformers integration*  
*EXISTENCE hypothesis - minimal architecture for proof-of-concept validation*

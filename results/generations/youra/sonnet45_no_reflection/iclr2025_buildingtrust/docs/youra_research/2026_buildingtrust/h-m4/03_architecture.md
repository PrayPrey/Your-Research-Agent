# Architecture Specification: h-m4

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M4 (MECHANISM)  
**Type:** Cross-Architecture Directional Replication Analysis  

**Applied Patterns:** Multi-model evaluation, LoRA cross-architecture adaptation, correlation directional analysis

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m3/code/src/`  
**Findings**: h-m3 implemented multi-dimensional evaluation (TruthfulQA, BBQ, ANLI) with correlation analysis. Reuses BaselineModel, LoRAInterventionModel, MultiDimensionalEvaluator. h-m4 extends by adding multi-model family support (5 architectures) and directional replication analysis.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BaselineModel | `from h_m3.src.model import BaselineModel` | `h-m3/code/src/model.py` |
| LoRAInterventionModel | `from h_m3.src.model import LoRAInterventionModel` | `h-m3/code/src/model.py` |
| MultiDimensionalEvaluator | `from h_m3.src.evaluators import MultiDimensionalEvaluator` | `h-m3/code/src/evaluators.py` |
| BBQEvaluator | `from h_m3.src.evaluators import BBQEvaluator` | `h-m3/code/src/evaluators.py` |
| AdvGLUEEvaluator | `from h_m3.src.evaluators import AdvGLUEEvaluator` | `h-m3/code/src/evaluators.py` |
| TruthfulQAEvaluator | `from h_m3.src.evaluators import TruthfulQAEvaluator` | `h-m3/code/src/evaluators.py` |
| InterventionTrainer | `from h_m3.src.train import InterventionTrainer` | `h-m3/code/src/train.py` |

**Verified from**: `docs/youra_research/20260511_buildingtrust/h-m3/code/` (actual implementation)

**Note**: h-m3 uses standard transformers models with LoRA. h-m4 reuses entire h-m3 evaluation pipeline and extends to 5 model families with directional replication analysis.

---

## Design Principles

**MECHANISM Architecture (H-M4):**
- Validates cross-architecture generalization of correlation patterns from h-m3
- Reuses h-m3's proven multi-dimensional evaluation pipeline
- Extends from single model (GPT-2) to 5 families (LLaMA, Mistral, Qwen, Mamba, Falcon)
- Adds directional replication analysis (≥3/5 models show same correlation direction)

**File Count:** 10 core files (adds model_family_manager.py, directional_replication_analyzer.py to h-m3 structure)

**Key Differences from h-m3:**
- Multi-model family support (5 architectures: 4 transformers + 1 SSM)
- Directional replication analysis (positive/negative/neutral classification)
- Increased seeds (3 → 5 for better statistical power)
- Per-family correlation tracking with majority direction detection

---

## Module Structure

### ConfigModule (`src/config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class H_M4_Config:
    project_name: str = "h-m4-cross-architecture-replication"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    
    model_families: list[str] = None
    n_seeds: int = 5
    seeds: list[int] = None
    
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules_map: dict[str, list[str]] = None
    
    learning_rate: float = 2e-4
    num_epochs: int = 3
    batch_size: int = 8
    training_samples: int = 500
    
    dimensions: list[str] = None
    device: str = "cuda"
    
    correlation_threshold: float = 0.3
    replication_threshold: float = 0.6

def load_config(config_path: str) -> H_M4_Config: ...
def get_model_families() -> list[str]: ...
def get_target_modules(model_family: str) -> list[str]: ...
```

---

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers

```python
from h_m3.src.data import MultiDimensionalDataset

class H_M4_DataModule:
    def __init__(self, tokenizer, dimensions: list[str]): ...
    def load_truthfulqa(self) -> Dataset: ...
    def load_bbq(self) -> Dataset: ...
    def load_anli(self) -> Dataset: ...
    def get_training_samples(self, n_samples: int) -> Dataset: ...
    def prepare_for_model_family(self, dataset: Dataset, model_family: str) -> Dataset: ...
```

---

### ModelFamilyManager (`src/model_family_manager.py`)

**Dependencies**: transformers, peft, torch

```python
class ModelFamilyManager:
    def __init__(self, config: H_M4_Config): ...
    def load_model_family(self, family_name: str) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
    def get_model_id(self, family_name: str) -> str: ...
    def apply_lora_to_family(
        self, 
        model: PreTrainedModel, 
        family_name: str
    ) -> PeftModel: ...
    def get_target_modules(self, family_name: str) -> list[str]: ...
    def is_mamba(self, family_name: str) -> bool: ...
```

---

### MultiModelEvaluator (`src/multi_model_evaluator.py`)

**Dependencies**: h_m3.src.evaluators, torch

```python
from h_m3.src.evaluators import MultiDimensionalEvaluator

class MultiModelEvaluator:
    def __init__(self, config: H_M4_Config): ...
    def evaluate_model_family(
        self, 
        model_family: str, 
        seed: int
    ) -> dict[str, float]: ...
    def run_baseline_evaluation(
        self, 
        model: PreTrainedModel, 
        tokenizer: PreTrainedTokenizer
    ) -> dict[str, float]: ...
    def run_intervention_evaluation(
        self, 
        model: PreTrainedModel, 
        tokenizer: PreTrainedTokenizer, 
        train_data: Dataset, 
        seed: int
    ) -> dict[str, float]: ...
    def compute_deltas(
        self, 
        baseline: dict[str, float], 
        post_intervention: dict[str, float]
    ) -> dict[str, float]: ...
```

---

### DirectionalReplicationAnalyzer (`src/directional_replication_analyzer.py`)

**Dependencies**: scipy, numpy

```python
class DirectionalReplicationAnalyzer:
    def __init__(self, dimensions: list[str], threshold: float = 0.3): ...
    def compute_correlation(
        self, 
        deltas1: list[float], 
        deltas2: list[float]
    ) -> tuple[float, float]: ...
    def classify_direction(self, r: float, threshold: float = 0.3) -> str: ...
    def compute_family_directions(
        self, 
        family_deltas: dict[str, list[float]]
    ) -> dict[str, str]: ...
    def compute_replication_rate(
        self, 
        all_family_directions: dict[str, dict[str, str]]
    ) -> dict[str, dict]: ...
    def check_gate_criterion(
        self, 
        replication_rates: dict[str, dict]
    ) -> bool: ...
```

---

### TrainingModule (`src/train.py`)

**Dependencies**: h_m3.src.train, torch

```python
from h_m3.src.train import InterventionTrainer

class H_M4_Trainer:
    def __init__(self, config: H_M4_Config): ...
    def train_lora_family(
        self, 
        model: PeftModel, 
        tokenizer: PreTrainedTokenizer, 
        train_data: Dataset, 
        seed: int
    ) -> dict: ...
    def setup_dataloader(
        self, 
        train_data: Dataset, 
        tokenizer: PreTrainedTokenizer
    ) -> DataLoader: ...
```

---

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class H_M4_FigureGenerator:
    def __init__(self, output_dir: str): ...
    def plot_replication_rates(
        self, 
        replication_rates: dict[str, dict]
    ): ...
    def plot_family_correlation_heatmap(
        self, 
        all_family_correlations: dict[str, dict[str, float]]
    ): ...
    def plot_directional_consistency(
        self, 
        all_family_directions: dict[str, dict[str, str]]
    ): ...
    def plot_architecture_comparison(
        self, 
        transformer_results: dict, 
        ssm_results: dict
    ): ...
    def plot_per_family_performance(
        self, 
        all_family_results: dict
    ): ...
    def save_all_figures(self): ...
```

---

### MainOrchestrator (`src/main.py`)

**Dependencies**: All src modules

```python
def main():
    config = load_config("config.yaml")
    set_seed(config.seeds[0])
    setup_gpu(0)
    
    # Initialize managers
    model_manager = ModelFamilyManager(config)
    data_module = H_M4_DataModule(None, config.dimensions)
    evaluator = MultiModelEvaluator(config)
    replication_analyzer = DirectionalReplicationAnalyzer(config.dimensions, config.correlation_threshold)
    
    # Prepare training data (universal across families)
    train_data = data_module.get_training_samples(config.training_samples)
    
    all_family_results = {}
    all_family_deltas = {}
    
    # Loop over 5 model families
    for family_name in config.model_families:
        print(f"\n=== Processing {family_name} ===")
        
        # Load model and tokenizer
        model, tokenizer = model_manager.load_model_family(family_name)
        
        # Baseline evaluation
        baseline_scores = evaluator.run_baseline_evaluation(model, tokenizer)
        
        family_deltas = []
        
        # Loop over 5 seeds
        for seed in config.seeds:
            set_seed(seed)
            
            # Apply LoRA intervention
            model_lora = model_manager.apply_lora_to_family(model, family_name)
            
            # Train on TruthfulQA
            trainer = H_M4_Trainer(config)
            train_data_prepared = data_module.prepare_for_model_family(train_data, family_name)
            trainer.train_lora_family(model_lora, tokenizer, train_data_prepared, seed)
            
            # Post-intervention evaluation
            post_scores = evaluator.run_baseline_evaluation(model_lora, tokenizer)
            
            # Compute deltas
            deltas = evaluator.compute_deltas(baseline_scores, post_scores)
            family_deltas.append(deltas)
        
        # Store results
        all_family_results[family_name] = {
            "baseline": baseline_scores,
            "deltas_per_seed": family_deltas
        }
        
        # Convert to per-dimension lists for correlation
        all_family_deltas[family_name] = {
            dim: [d[dim] for d in family_deltas]
            for dim in config.dimensions
        }
    
    # Directional replication analysis
    all_family_directions = {}
    for family_name, deltas in all_family_deltas.items():
        family_directions = replication_analyzer.compute_family_directions(deltas)
        all_family_directions[family_name] = family_directions
    
    # Compute replication rates
    replication_rates = replication_analyzer.compute_replication_rate(all_family_directions)
    
    # Check gate criterion
    gate_pass = replication_analyzer.check_gate_criterion(replication_rates)
    
    # Visualization
    visualizer = H_M4_FigureGenerator(config.figures_dir)
    visualizer.plot_replication_rates(replication_rates)
    visualizer.plot_family_correlation_heatmap(all_family_directions)
    visualizer.save_all_figures()
    
    # Save results
    save_results({
        "replication_rates": replication_rates,
        "family_directions": all_family_directions,
        "family_deltas": all_family_deltas,
        "gate_pass": gate_pass
    }, f"{config.output_dir}/h_m4_validation.json")
    
    print(f"\n=== Gate Status: {'PASS' if gate_pass else 'FAIL'} ===")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
h-m4/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                          # h-m4 configuration
│   │   ├── data.py                            # Reuses h-m3 data module
│   │   ├── model_family_manager.py            # NEW: Multi-model loading
│   │   ├── multi_model_evaluator.py           # NEW: Multi-family evaluation
│   │   ├── directional_replication_analyzer.py # NEW: Replication analysis
│   │   ├── train.py                           # Extends h-m3 training
│   │   ├── visualize.py                       # Multi-family visualizations
│   │   └── main.py                            # Entry point
│   ├── run_experiment.py                      # CLI entry point
│   ├── config.yaml                            # Default configuration
│   └── requirements.txt                       # Dependencies
├── outputs/
│   ├── family_baseline_scores.json            # Pre-intervention scores per family
│   ├── family_deltas_seed*.json               # Deltas per family per seed
│   ├── family_correlations.json               # Correlations per family
│   ├── family_directions.json                 # Direction classification per family
│   ├── replication_rates.json                 # Replication rate per dimension pair
│   └── h_m4_validation.json                   # Final validation results
└── figures/
    ├── replication_rates.png                  # Required gate figure
    ├── family_correlation_heatmap.png
    ├── directional_consistency.png
    ├── architecture_comparison.png
    └── per_family_performance.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Initialize h-m4 codebase, extend h-m3 structure, add multi-family dependencies | 7 | Module(2) + Deps(2) + Algo(1) + Integ(2) |
| A-2 | Model Family Manager | Load and configure 5 model families (LLaMA, Mistral, Qwen, Mamba, Falcon) | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |
| A-3 | LoRA Cross-Architecture Adapter | Apply LoRA with family-specific target modules | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-4 | Multi-Model Evaluation Pipeline | Extend h-m3 evaluator for 5 families × 5 seeds = 25 runs | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| A-5 | Directional Classification | Classify correlation direction (positive/negative/neutral) per family | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-6 | Replication Rate Analysis | Compute majority direction and replication rate (≥3/5 threshold) | 10 | Module(2) + Deps(2) + Algo(4) + Integ(2) |
| A-7 | Training Pipeline Extension | Train LoRA on 5 families with 5 seeds each | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-8 | Per-Family Correlation Analysis | Compute Pearson correlation per family across seeds | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-9 | Visualization Suite | Generate 5 figures: replication rates, heatmaps, architecture comparison | 10 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| A-10 | Experiment Orchestration | Main workflow: 5 families × 5 seeds with directional analysis | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |

**Distribution**: 
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-2, A-3, A-4, A-5, A-6, A-8, A-9, A-10]
- Low (4-8): [A-1, A-7]

**Total Complexity**: 98 points across 10 tasks

---

## Task Breakdown Details

**A-1: Project Setup** (7 points)
- Create h-m4 directory structure extending h-m3
- Install multi-model dependencies (mamba-ssm for Mamba model)
- Configure imports from h-m3 code
- Create config.yaml with 5 model families specification

**A-2: Model Family Manager** (12 points)
- Implement loader for LLaMA-3.2-1B
- Implement loader for Mistral-7B-v0.1
- Implement loader for Qwen-1.8B
- Implement loader for Mamba-1.4B (SSM - different API)
- Implement loader for Falcon-7B
- Handle model-specific tokenizer configurations
- Device mapping for 7B models (bf16/fp16)

**A-3: LoRA Cross-Architecture Adapter** (10 points)
- Define target modules per family (q_proj, k_proj, v_proj, o_proj for transformers)
- Handle Mamba-specific LoRA target modules (SSM layers)
- Apply LoRA config (r=8, α=16) consistently
- Verify trainable parameters per family
- Handle architecture-specific edge cases

**A-4: Multi-Model Evaluation Pipeline** (11 points)
- Extend h-m3 evaluator for multi-family support
- Run baseline + post-intervention for 5 families
- Handle 5 seeds per family (25 total runs)
- Aggregate results per family
- Save intermediate checkpoints per family-seed

**A-5: Directional Classification** (9 points)
- Compute Pearson correlation per family
- Classify direction: ρ > 0.3 (positive), ρ < -0.3 (negative), else neutral
- Handle 3 dimension pairs (truth-fair, truth-robust, fair-robust)
- Statistical significance testing (p < 0.05)
- Return direction per family per dimension pair

**A-6: Replication Rate Analysis** (10 points)
- For each dimension pair, collect directions from 5 families
- Find majority direction (most common)
- Compute replication rate: matching_count / 5
- Check gate criterion: ≥0.6 (3/5 models)
- Generate replication summary report

**A-7: Training Pipeline Extension** (8 points)
- Reuse h-m3 training loop
- Train on TruthfulQA (500 samples, 3 epochs)
- Apply to 5 families × 5 seeds = 25 training runs
- Handle batch size adjustment for 7B models (gradient accumulation)
- Save checkpoints per family-seed

**A-8: Per-Family Correlation Analysis** (9 points)
- Aggregate deltas across 5 seeds per family
- Compute Pearson correlation for all dimension pairs
- Store correlations per family
- Compare correlation patterns across families
- Identify architecture-specific trends (transformers vs SSM)

**A-9: Visualization Suite** (10 points)
- Figure 1: Replication rate bar chart (gate metric)
- Figure 2: Per-family correlation heatmap (5×3 grid)
- Figure 3: Directional consistency stacked bar chart
- Figure 4: Architecture comparison (transformer vs SSM)
- Figure 5: Per-family performance delta bar chart

**A-10: Experiment Orchestration** (12 points)
- Load 5 model families sequentially
- For each family: baseline eval → train × 5 seeds → post eval × 5
- Compute deltas per family per seed
- Run directional replication analysis
- Check gate criterion (≥3/5 replication)
- Generate all visualizations
- Save comprehensive results

---

## Integration Notes

### h-m3 Code Reuse Strategy

**Direct Imports (No Modifications):**
- `MultiDimensionalEvaluator` (3-dimension evaluation)
- `BBQEvaluator`, `AdvGLUEEvaluator`, `TruthfulQAEvaluator` (dimension-specific evaluators)
- `InterventionTrainer` (LoRA training loop)
- Dataset loading logic (TruthfulQA, BBQ, ANLI)

**h-m4 Specific Components:**
- Multi-model family loading (5 architectures)
- Directional replication analysis (majority direction, replication rate)
- Per-family correlation tracking
- Cross-architecture comparison (transformers vs SSM)

### Multi-Model Family Pattern

**Challenge**: Load and evaluate 5 diverse model families with different architectures.

**Solution**:
1. Model family manager with architecture-specific loaders
2. Unified LoRA application with family-specific target modules
3. Consistent evaluation interface across all families
4. Family-agnostic training loop with dynamic batch sizing

**Implementation Pattern**:
```python
# Family-specific loading
MODEL_IDS = {
    "llama": "meta-llama/Llama-3.2-1B",
    "mistral": "mistralai/Mistral-7B-v0.1",
    "qwen": "Qwen/Qwen-1.8B",
    "mamba": "state-spaces/mamba-1.4b",
    "falcon": "tiiuae/falcon-7b"
}

TARGET_MODULES = {
    "llama": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "mistral": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "qwen": ["c_attn"],
    "mamba": ["in_proj", "out_proj"],  # SSM-specific
    "falcon": ["query_key_value", "dense"]
}

# Load family
model = AutoModelForCausalLM.from_pretrained(
    MODEL_IDS[family_name],
    device_map="auto",
    torch_dtype="auto"
)

# Apply LoRA
lora_config = LoraConfig(
    r=8, lora_alpha=16,
    target_modules=TARGET_MODULES[family_name]
)
model_lora = get_peft_model(model, lora_config)
```

### Directional Replication Analysis Pipeline

**Challenge**: Determine if correlation direction replicates across ≥3/5 models.

**Solution**:
1. Compute correlation per family across 5 seeds
2. Classify direction per family (positive/negative/neutral)
3. Find majority direction across 5 families
4. Compute replication rate (matching / 5)
5. Check gate: replication_rate ≥ 0.6

**Implementation Pattern**:
```python
from scipy.stats import pearsonr

# Per-family direction classification
family_directions = {}
for family, deltas in all_family_deltas.items():
    r, p = pearsonr(deltas['truthfulness'], deltas['robustness'])
    if r > 0.3:
        direction = "positive"
    elif r < -0.3:
        direction = "negative"
    else:
        direction = "neutral"
    family_directions[family] = direction

# Replication analysis
directions = list(family_directions.values())
majority = max(set(directions), key=directions.count)
replication_rate = directions.count(majority) / len(directions)
gate_pass = replication_rate >= 0.6  # ≥3/5
```

### Configuration Inheritance

From h-m3 (proven values):
- LoRA rank: 8
- LoRA alpha: 16
- Training samples: 500
- Learning rate: 2e-4
- Epochs: 3
- Dimensions: ["truthfulness", "fairness", "robustness"]

New for h-m4:
- Model families: ["llama", "mistral", "qwen", "mamba", "falcon"]
- Seeds: 5 (increased from 3 for statistical power)
- Correlation threshold: 0.3 (for direction classification)
- Replication threshold: 0.6 (≥3/5 models)
- Target modules per family (architecture-specific)

---

## Dependencies

### Core Libraries (From h-m3)
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
```

### New for h-m4
```
mamba-ssm>=1.0.0  # For Mamba model support
```

### Statistical Analysis
```
scipy>=1.10.0
numpy>=1.24.0
```

### Visualization
```
matplotlib>=3.7.0
seaborn>=0.12.0
```

### Utilities
```
PyYAML>=6.0
tqdm>=4.65.0
```

---

## Validation Criteria

### Code Quality
- Type hints on all function signatures
- Error handling for model loading (especially Mamba SSM)
- Memory management for multi-model evaluation (clear GPU cache between families)
- Checkpoint saving for long-running experiments (25 total runs)

### Success Metrics
- All 5 model families load successfully
- All 25 runs (5 families × 5 seeds) complete
- Directional classification works for all families
- Replication rate computed for all dimension pairs
- All 5 required figures generated

### Gate Metric (SHOULD_WORK)
- **Primary**: ≥3/5 model families show same correlation direction for at least one dimension pair
- **Secondary**: Statistical significance (p < 0.05) for replicating families
- **Partial Pass**: Code runs but replication rate < 60% (document as architectural heterogeneity finding)

---

*Generated by Phase 3 Architecture Agent*  
*Patterns Applied: Multi-model evaluation, LoRA cross-architecture adaptation, correlation directional analysis*  
*MECHANISM hypothesis - extends h-m3 to validate cross-architecture directional replication*

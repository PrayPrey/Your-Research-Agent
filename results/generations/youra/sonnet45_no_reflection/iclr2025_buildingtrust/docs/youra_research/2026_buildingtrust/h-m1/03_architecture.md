# Architecture Specification: h-m1

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M1 (MECHANISM)  
**Type:** Target Dimension Improvement Validation  

**Applied Patterns:** PyTorch module pattern, HuggingFace transformers integration, lm-evaluation-harness

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code (h-e1)  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-e1/code/`  
**Findings**: h-e1 implemented with GPT-2 + LoRA (not Llama-3-8B as spec indicated). Core modules: BaselineModel, LoRAInterventionModel, InterventionTrainer, TrustEvaluator. h-m1 reuses this proven structure.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BaselineModel | `from h_e1.src.model import BaselineModel` | `h-e1/code/src/model.py` |
| LoRAInterventionModel | `from h_e1.src.model import LoRAInterventionModel` | `h-e1/code/src/model.py` |
| InterventionTrainer | `from h_e1.src.train import InterventionTrainer` | `h-e1/code/src/train.py` |
| TrustEvaluator | `from h_e1.src.evaluate import TrustEvaluator` | `h-e1/code/src/evaluate.py` |

**Verified from**: `docs/youra_research/20260511_buildingtrust/h-e1/code/` (actual implementation)

**Note**: h-e1 code uses GPT-2 (`openai-community/gpt2`), not Llama-3-8B. Import paths assume h-e1 code is on Python path or relative imports are adjusted during Phase 4.

---

## Design Principles

**MECHANISM Architecture (H-M1):**
- Validates first step of causal chain: parameter updates improve target dimension
- Reuses h-e1's proven GPT-2 + LoRA configuration
- Single dimension focus (TruthfulQA only, no BBQ/AdvGLUE)
- Statistical validation via paired t-test

**File Count:** 5 core files (simplified from h-e1's 7-file structure)

**Key Differences from h-e1:**
- No BBQ/AdvGLUE datasets (target dimension only)
- No correlation analysis (Δ improvement only)
- Simplified evaluation (pre/post comparison)

---

## Module Structure

### ConfigModule (`src/config.py`)

**Dependencies**: dataclasses, yaml

```python
@dataclass
class H_M1_Config:
    model_id: str = "openai-community/gpt2"
    target_dimension: str = "truthfulness"
    n_replicates: int = 3
    seeds: list[int] = None
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: list[str] = None
    learning_rate: float = 1e-4
    epochs: int = 3
    batch_size: int = 4
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    device: str = "cuda"
    output_dir: str = "./results"

def load_config(config_path: str) -> H_M1_Config: ...
def save_config(config: H_M1_Config, path: str): ...
```

---

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers, lm_eval

```python
class TruthfulQADataset:
    def __init__(self, tokenizer, split: str = "validation"): ...
    def load_dataset(self) -> Dataset: ...
    def prepare_training_data(self) -> Dataset: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class DataCollator:
    def __init__(self, tokenizer, max_length: int = 512): ...
    def __call__(self, features: list[dict]) -> dict: ...
```

**Note**: TruthfulQA has no official train split. Training uses general language modeling on validation set questions.

---

### ModelModule (`src/model.py`)

**Dependencies**: Reuses h-e1 classes directly

```python
# Import from h-e1 codebase
from h_e1.src.model import BaselineModel, LoRAInterventionModel

# H-M1 specific wrapper (optional)
class H_M1_Model:
    def __init__(self, config: H_M1_Config): ...
    def load_baseline(self) -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...
    def apply_intervention(self, base_model) -> PeftModel: ...
```

---

### TrainingModule (`src/train.py`)

**Dependencies**: torch, transformers, peft, h_e1.src.train

```python
# Import trainer from h-e1
from h_e1.src.train import InterventionTrainer

def train_single_replicate(
    model_id: str,
    config: H_M1_Config,
    seed: int
) -> dict:
    """Train single replicate with LoRA intervention.
    
    Returns:
        dict with pre_score, post_score, delta_target, seed
    """
    ...

def run_all_replicates(config: H_M1_Config) -> list[dict]:
    """Run N=3 replicates with different seeds.
    
    Returns:
        List of replicate results
    """
    ...
```

---

### EvaluationModule (`src/evaluate.py`)

**Dependencies**: lm_eval, scipy, numpy

```python
class TruthfulQAEvaluator:
    def __init__(self, model_path: str): ...
    def evaluate_mc2(self) -> float:
        """Evaluate using EleutherAI lm-eval harness.
        
        Returns:
            TruthfulQA MC2 score (0-1)
        """
        ...

class StatisticalAnalyzer:
    def __init__(self, results: list[dict]): ...
    def extract_deltas(self) -> list[float]: ...
    def compute_paired_ttest(self) -> tuple[float, float]:
        """Compute paired t-test.
        
        Returns:
            (t_statistic, p_value)
        """
        ...
    def check_directional_consistency(self) -> float:
        """Check % replicates with Δ > 0."""
        ...
    def evaluate_gate(self) -> dict:
        """Evaluate MUST_WORK gate.
        
        Returns:
            dict with pass/fail, mean_delta, p_value, consistency
        """
        ...
```

---

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class FigureGenerator:
    def __init__(self, results: list[dict], output_dir: str): ...
    def plot_pre_post_comparison(self, mean_pre: float, mean_post: float, std_pre: float, std_post: float): ...
    def plot_replicate_deltas(self, deltas: list[float]): ...
    def plot_training_curves(self, loss_history: dict): ...
    def plot_gate_metrics(self, target_delta: float, actual_mean_delta: float, p_value: float): ...
    def save_all_figures(self): ...
```

---

### MainOrchestrator (`src/main.py`)

**Dependencies**: All src modules

```python
def main():
    # Load configuration
    config = load_config("config.yaml")
    
    # Setup environment
    set_seed(config.seeds[0])
    setup_gpu(0)
    
    # Step 1: Pre-intervention evaluation
    baseline_evaluator = TruthfulQAEvaluator(config.model_id)
    pre_score = baseline_evaluator.evaluate_mc2()
    
    # Step 2: Run interventions (N=3 replicates)
    replicate_results = run_all_replicates(config)
    
    # Step 3: Statistical analysis
    analyzer = StatisticalAnalyzer(replicate_results)
    gate_result = analyzer.evaluate_gate()
    
    # Step 4: Visualization
    visualizer = FigureGenerator(replicate_results, config.output_dir)
    visualizer.save_all_figures()
    
    # Step 5: Save results
    save_results(gate_result, f"{config.output_dir}/h_m1_validation.json")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py         # Experiment configuration
│   │   ├── data.py           # TruthfulQA dataset loading
│   │   ├── model.py          # Model wrapper (imports h-e1)
│   │   ├── train.py          # Training orchestration
│   │   ├── evaluate.py       # TruthfulQA eval + statistics
│   │   ├── visualize.py      # Figure generation
│   │   └── main.py           # Entry point
│   ├── run_experiment.py     # CLI entry point
│   ├── config.yaml           # Default configuration
│   └── requirements.txt      # Dependencies
├── results/
│   ├── baseline_score.json
│   ├── replicate_results.json
│   └── h_m1_validation.json
└── figures/
    ├── pre_post_comparison.png
    ├── replicate_deltas.png
    ├── training_curves.png
    └── gate_metrics.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Initialize codebase, dependencies, h-e1 integration | 6 | Module(2) + Deps(2) + Algo(1) + Integ(1) |
| A-2 | Data Pipeline | TruthfulQA dataset loading via lm-eval harness | 7 | Module(2) + Deps(2) + Algo(1) + Integ(2) |
| A-3 | Model Integration | Integrate h-e1 BaselineModel and LoRA components | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-4 | Training Pipeline | Replicate training loop with LoRA fine-tuning | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Evaluation System | TruthfulQA MC2 evaluation + paired t-test | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-6 | Statistical Analysis | Compute Δ, t-test, directional consistency, gate | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |
| A-7 | Visualization | Generate 4 required figures | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| A-8 | Experiment Orchestration | Main workflow: baseline → intervention → analysis | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |

**Distribution**: 
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-4, A-5]
- Low (4-8): [A-1, A-2, A-3, A-6, A-7, A-8]

**Total Complexity**: 61 points across 8 tasks

---

## Task Breakdown Details

**A-1: Project Setup** (6 points)
- Create directory structure matching h-e1
- Setup requirements.txt with h-e1 dependencies
- Configure Python path for h-e1 imports
- Create config.yaml template

**A-2: Data Pipeline** (7 points)
- Implement TruthfulQADataset with lm-eval integration
- Create training data from validation set (language modeling)
- Implement DataCollator with GPT-2 tokenizer
- Handle padding and truncation

**A-3: Model Integration** (8 points)
- Import BaselineModel from h-e1
- Import LoRAInterventionModel from h-e1
- Verify GPT-2 compatibility (h-e1 used GPT-2, not Llama)
- Create h-m1 wrapper with configuration

**A-4: Training Pipeline** (10 points)
- Import InterventionTrainer from h-e1
- Implement train_single_replicate (seed management)
- Implement run_all_replicates (N=3 loop)
- Track training metrics (loss curves)

**A-5: Evaluation System** (9 points)
- Implement TruthfulQAEvaluator with lm-eval harness
- Pre-intervention evaluation (baseline)
- Post-intervention evaluation (per replicate)
- Extract MC2 scores from harness output

**A-6: Statistical Analysis** (8 points)
- Extract Δ(Target) = post - pre for each replicate
- Compute paired t-test (scipy.stats.ttest_rel)
- Check directional consistency (% Δ > 0)
- Evaluate gate: mean Δ > 0 AND p < 0.05

**A-7: Visualization** (6 points)
- Pre/post comparison bar chart (error bars)
- Replicate deltas scatter plot
- Training loss curves
- Gate metrics comparison (target vs actual)

**A-8: Experiment Orchestration** (7 points)
- Main workflow orchestrator
- Pre-intervention measurement
- Intervention loop (N=3 replicates)
- Post-processing and results saving

---

## Integration Notes

### h-e1 Code Reuse Strategy

**Direct Imports (No Modifications):**
- `BaselineModel` (model loading)
- `LoRAInterventionModel` (LoRA configuration)
- `InterventionTrainer` (training loop)

**h-m1 Specific Components:**
- TruthfulQA-only dataset (vs h-e1's 3 dimensions)
- Paired t-test analysis (vs h-e1's correlation analysis)
- Δ improvement metrics (vs h-e1's cross-dimensional ρ)

### Configuration Inheritance

From h-e1 (proven values):
- LoRA rank: 8
- LoRA alpha: 16 (adjusted from h-e1's 8)
- Target modules: ["c_attn"] (GPT-2 attention)
- Learning rate: 1e-4
- Epochs: 3
- Batch size: 4
- Seeds: [42, 43, 44]

---

## Dependencies

### Core Libraries (From h-e1)
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
lm-evaluation-harness>=0.4.0
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

## Validation Criteria

### Code Quality
- Type hints on all function signatures
- Docstrings for public methods
- Error handling for lm-eval API calls
- GPU memory management

### Success Metrics (PoC)
- Code runs without error on single GPU
- All 3 replicates complete successfully
- Mean Δ(Target) > 0 with p < 0.05
- All 4 figures generated

### Gate Metric (MUST_WORK)
- **Primary**: Mean Δ(Target) > 0 with p < 0.05
- **Secondary**: ≥70% replicates show Δ > 0

---

*Generated by Phase 3 Architecture Agent*  
*Patterns Applied: PyTorch module structure, HuggingFace transformers integration, lm-evaluation-harness*  
*MECHANISM hypothesis - extends h-e1 proven configuration for target dimension validation*

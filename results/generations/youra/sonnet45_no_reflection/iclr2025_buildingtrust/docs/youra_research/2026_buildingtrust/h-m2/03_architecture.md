# Architecture Specification: h-m2

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M2 (MECHANISM)  
**Type:** Representation Change Validation  

**Applied Patterns:** TransformerLens activation extraction, pytorch-cka representation similarity, PyTorch module pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m1/code/`  
**Findings**: h-m1 implemented GPT-2 + LoRA intervention with modular structure (config, model, train, evaluate). h-m2 extends this by adding representation extraction (TransformerLens) and similarity analysis (CKA). Core modules reused: BaselineModel, LoRAInterventionModel, InterventionTrainer.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BaselineModel | `from h_m1.src.model import BaselineModel` | `h-m1/code/src/model.py` |
| LoRAInterventionModel | `from h_m1.src.model import LoRAInterventionModel` | `h-m1/code/src/model.py` |
| InterventionTrainer | `from h_m1.src.train import InterventionTrainer` | `h-m1/code/src/train.py` |
| ExperimentConfig | `from h_m1.src.config import ExperimentConfig` | `h-m1/code/src/config.py` |

**Verified from**: `docs/youra_research/20260511_buildingtrust/h-m1/code/` (actual implementation)

**Note**: h-m1 uses GPT-2 (`gpt2`). h-m2 wraps GPT-2 with TransformerLens for activation extraction.

---

## Design Principles

**MECHANISM Architecture (H-M2):**
- Validates second step of causal chain: parameter updates change internal representations
- Reuses h-m1's proven LoRA configuration
- Adds activation extraction (TransformerLens) and representation similarity (CKA)
- Correlates representation changes with performance improvements from h-m1

**File Count:** 6 core files (adds representation_analyzer.py to h-m1 structure)

**Key Differences from h-m1:**
- TransformerLens wrapper for activation extraction
- CKA similarity computation for representation change measurement
- Pre/post activation caching and storage
- Correlation analysis between representation change and performance

---

## Module Structure

### ConfigModule (`src/config.py`)

**Dependencies**: dataclasses, yaml, h_m1.src.config

```python
@dataclass
class H_M2_Config:
    model_id: str = "gpt2"
    n_replicates: int = 3
    seeds: list[int] = None
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: list[str] = None
    learning_rate: float = 1e-4
    epochs: int = 3
    batch_size: int = 4
    device: str = "cuda"
    output_dir: str = "./results"
    layers_to_analyze: list[str] = None
    save_activations: bool = True
    activation_cache_dir: str = "./activations"

def load_config(config_path: str) -> H_M2_Config: ...
def get_layers_to_analyze(n_layers: int = 12) -> list[str]: ...
```

---

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers, torch

```python
class TruthfulQADataset:
    def __init__(self, tokenizer, split: str = "validation", max_samples: int = None): ...
    def load_dataset(self) -> Dataset: ...
    def get_eval_samples(self, n_samples: int = 100) -> Dataset: ...
    def prepare_tokens(self, texts: list[str]) -> torch.Tensor: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...
```

---

### ModelModule (`src/model.py`)

**Dependencies**: transformer_lens, transformers, peft, h_m1.src.model

```python
class TransformerLensWrapper:
    def __init__(self, model_id: str = "gpt2"): ...
    def load_hooked_model(self) -> HookedTransformer: ...
    def convert_from_hf_peft(self, peft_model) -> HookedTransformer: ...
    def get_hook_names(self) -> list[str]: ...

class H_M2_Model:
    def __init__(self, config: H_M2_Config): ...
    def load_baseline_with_hooks(self) -> HookedTransformer: ...
    def apply_lora_intervention(self, base_model) -> PeftModel: ...
    def reload_with_lora_weights(self, lora_model) -> HookedTransformer: ...
```

---

### RepresentationAnalyzer (`src/representation_analyzer.py`)

**Dependencies**: transformer_lens, torch, numpy

```python
class ActivationExtractor:
    def __init__(self, model: HookedTransformer, layers: list[str]): ...
    def extract_activations(self, tokens: torch.Tensor) -> dict[str, torch.Tensor]: ...
    def save_activations(self, activations: dict, filepath: str): ...
    def load_activations(self, filepath: str) -> dict[str, torch.Tensor]: ...

class RepresentationAnalyzer:
    def __init__(self, config: H_M2_Config): ...
    def extract_pre_intervention(self, model: HookedTransformer, eval_tokens: torch.Tensor, seed: int) -> dict: ...
    def extract_post_intervention(self, model: HookedTransformer, eval_tokens: torch.Tensor, seed: int) -> dict: ...
    def compute_cka_similarity(self, pre_acts: dict, post_acts: dict) -> dict[str, float]: ...
    def compute_change_magnitude(self, cka_scores: dict) -> dict[str, float]: ...
```

---

### SimilarityModule (`src/similarity.py`)

**Dependencies**: pytorch-cka (or custom implementation), torch, scipy

```python
class CKASimilarity:
    def __init__(self, device: str = "cuda"): ...
    def compute_cka(self, X: torch.Tensor, Y: torch.Tensor) -> float: ...
    def compute_layer_cka(self, pre_acts: dict, post_acts: dict, layer_name: str) -> float: ...
    def compute_all_layers(self, pre_acts: dict, post_acts: dict, layers: list[str]) -> dict[str, float]: ...

class CorrelationAnalyzer:
    def __init__(self): ...
    def correlate_representation_performance(self, change_magnitudes: list[float], performance_delta: float) -> tuple[float, float]: ...
    def aggregate_across_replicates(self, replicate_cka_scores: list[dict]) -> dict: ...
```

---

### TrainingModule (`src/train.py`)

**Dependencies**: torch, h_m1.src.train

```python
from h_m1.src.train import InterventionTrainer

class H_M2_Trainer:
    def __init__(self, config: H_M2_Config): ...
    def train_with_representation_tracking(
        self,
        model,
        train_data,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> dict: ...
```

---

### EvaluationModule (`src/evaluate.py`)

**Dependencies**: lm_eval, scipy, numpy

```python
class TruthfulQAEvaluator:
    def __init__(self, model_path: str): ...
    def evaluate_mc2(self) -> float: ...

class StatisticalAnalyzer:
    def __init__(self): ...
    def compute_pearson_correlation(self, x: list[float], y: list[float]) -> tuple[float, float]: ...
    def evaluate_gate(
        self,
        cka_scores: dict,
        performance_delta: float = 0.0232
    ) -> dict: ...
```

---

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class FigureGenerator:
    def __init__(self, output_dir: str): ...
    def plot_cka_heatmap(self, cka_scores: dict, layers: list[str]): ...
    def plot_change_magnitude(self, change_magnitudes: dict): ...
    def plot_layer_progression(self, cka_scores: dict): ...
    def plot_correlation_scatter(self, change_magnitudes: list[float], performance_delta: float, correlation: float, p_value: float): ...
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
    
    # Prepare evaluation data
    dataset = TruthfulQADataset(tokenizer, max_samples=100)
    eval_tokens = dataset.prepare_tokens(dataset.get_eval_samples())
    
    # Step 1: Extract pre-intervention representations
    model_wrapper = H_M2_Model(config)
    baseline_model = model_wrapper.load_baseline_with_hooks()
    
    analyzer = RepresentationAnalyzer(config)
    
    results = []
    for seed in config.seeds:
        # Extract pre-intervention activations
        pre_acts = analyzer.extract_pre_intervention(baseline_model, eval_tokens, seed)
        
        # Apply LoRA intervention (reuse h-m1 training)
        trainer = H_M2_Trainer(config)
        trainer.train_with_representation_tracking(baseline_model, train_data, eval_tokens, seed)
        
        # Extract post-intervention activations
        post_acts = analyzer.extract_post_intervention(baseline_model, eval_tokens, seed)
        
        # Compute CKA similarity
        cka_scores = analyzer.compute_cka_similarity(pre_acts, post_acts)
        results.append(cka_scores)
    
    # Step 2: Statistical analysis
    stat_analyzer = StatisticalAnalyzer()
    gate_result = stat_analyzer.evaluate_gate(results, performance_delta=0.0232)
    
    # Step 3: Visualization
    visualizer = FigureGenerator(config.output_dir)
    visualizer.save_all_figures()
    
    # Step 4: Save results
    save_results(gate_result, f"{config.output_dir}/h_m2_validation.json")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                 # h-m2 configuration
│   │   ├── data.py                   # TruthfulQA dataset
│   │   ├── model.py                  # TransformerLens wrapper
│   │   ├── representation_analyzer.py # Activation extraction
│   │   ├── similarity.py             # CKA computation
│   │   ├── train.py                  # Training with representation tracking
│   │   ├── evaluate.py               # Evaluation + correlation analysis
│   │   ├── visualize.py              # Figure generation
│   │   └── main.py                   # Entry point
│   ├── run_experiment.py             # CLI entry point
│   ├── config.yaml                   # Default configuration
│   └── requirements.txt              # Dependencies
├── outputs/
│   ├── pre_activations_seed42.pt
│   ├── pre_activations_seed43.pt
│   ├── pre_activations_seed44.pt
│   ├── post_activations_seed42.pt
│   ├── post_activations_seed43.pt
│   ├── post_activations_seed44.pt
│   ├── cka_scores_seed42.json
│   ├── cka_scores_seed43.json
│   ├── cka_scores_seed44.json
│   └── h_m2_validation.json
└── figures/
    ├── correlation_scatter.png       # Required gate figure
    ├── cka_heatmap.png
    ├── change_magnitude.png
    └── layer_progression.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Initialize codebase, dependencies, TransformerLens integration | 7 | Module(2) + Deps(2) + Algo(1) + Integ(2) |
| A-2 | Data Pipeline | TruthfulQA dataset loading and tokenization | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| A-3 | TransformerLens Integration | Wrap GPT-2 with HookedTransformer for activation extraction | 9 | Module(2) + Deps(3) + Algo(2) + Integ(2) |
| A-4 | Activation Extractor | Extract pre/post intervention activations, save to disk | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | CKA Similarity Module | Implement or integrate pytorch-cka for representation comparison | 11 | Module(3) + Deps(2) + Algo(4) + Integ(2) |
| A-6 | LoRA Training Pipeline | Reuse h-m1 training with activation tracking | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-7 | Statistical Analysis | Correlation between representation change and performance | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-8 | Visualization | Generate 4 required figures (CKA heatmap, scatter, etc.) | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-9 | Experiment Orchestration | Main workflow: pre-extract → train → post-extract → analyze | 8 | Module(2) + Deps(1) + Algo(3) + Integ(2) |

**Distribution**: 
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-3, A-4, A-5, A-7]
- Low (4-8): [A-1, A-2, A-6, A-8, A-9]

**Total Complexity**: 75 points across 9 tasks

---

## Task Breakdown Details

**A-1: Project Setup** (7 points)
- Create directory structure extending h-m1
- Install TransformerLens and pytorch-cka
- Configure Python imports for h-m1 code reuse
- Create config.yaml with layer specifications

**A-2: Data Pipeline** (6 points)
- Load TruthfulQA validation set
- Prepare evaluation samples (100 questions)
- Tokenize with GPT-2 tokenizer
- Create DataLoader for evaluation

**A-3: TransformerLens Integration** (9 points)
- Wrap GPT-2 with HookedTransformer
- Verify hook points (attention patterns, hidden states)
- Implement conversion from PEFT LoRA to TransformerLens
- Test activation extraction on sample input

**A-4: Activation Extractor** (10 points)
- Implement run_with_cache for all 24 layers
- Extract attention patterns (blocks.{i}.attn.hook_pattern)
- Extract hidden states (blocks.{i}.hook_resid_post)
- Save activations to disk (per replicate)
- Load activations for comparison

**A-5: CKA Similarity Module** (11 points)
- Integrate pytorch-cka library
- Implement layer-wise CKA computation
- Flatten activations for CKA input format
- Compute CKA for all 24 layers (attention + hidden)
- Return similarity scores (0-1 range)

**A-6: LoRA Training Pipeline** (8 points)
- Reuse h-m1 InterventionTrainer
- Apply LoRA with config from h-m1 (r=8, alpha=16)
- Train for 3 epochs on 100 TruthfulQA samples
- Track training loss
- Reload model with LoRA weights into TransformerLens

**A-7: Statistical Analysis** (9 points)
- Compute representation change magnitude (1 - CKA)
- Correlate change magnitude with h-m1 performance delta (+2.32%)
- Compute Pearson correlation coefficient
- Calculate p-value (significance test)
- Evaluate gate: p < 0.05

**A-8: Visualization** (7 points)
- CKA heatmap (layers × representation types)
- Change magnitude bar chart
- Layer progression line plot
- Correlation scatter plot (required for gate)

**A-9: Experiment Orchestration** (8 points)
- Main workflow orchestrator
- Loop over 3 replicates (seeds: 42, 43, 44)
- Pre-intervention → intervention → post-intervention
- Aggregate results across replicates
- Save validation report

---

## Integration Notes

### h-m1 Code Reuse Strategy

**Direct Imports (No Modifications):**
- `BaselineModel` (model loading)
- `LoRAInterventionModel` (LoRA configuration)
- `InterventionTrainer` (training loop)
- `ExperimentConfig` (configuration structure)

**h-m2 Specific Components:**
- TransformerLens wrapper for GPT-2
- Activation extraction and caching
- CKA similarity computation
- Correlation analysis (representation change vs. performance)

### TransformerLens + PEFT Integration

**Challenge**: TransformerLens uses custom model format, PEFT uses HuggingFace.

**Solution**:
1. Load GPT-2 as HookedTransformer for pre-intervention
2. Convert to HuggingFace format for PEFT LoRA training
3. Reload trained weights into HookedTransformer for post-intervention

**Implementation Pattern**:
```python
# Pre-intervention
hooked_model = HookedTransformer.from_pretrained("gpt2")
pre_acts = hooked_model.run_with_cache(tokens)

# Convert to HuggingFace for LoRA
hf_model = AutoModelForCausalLM.from_pretrained("gpt2")
lora_model = get_peft_model(hf_model, lora_config)

# Train LoRA
trainer.train(lora_model)

# Reload as HookedTransformer with LoRA weights
hooked_model_post = HookedTransformer.from_pretrained(
    "gpt2",
    state_dict=lora_model.state_dict()
)
post_acts = hooked_model_post.run_with_cache(tokens)
```

### Configuration Inheritance

From h-m1 (proven values):
- LoRA rank: 8
- LoRA alpha: 16
- Target modules: ["c_attn"]
- Learning rate: 1e-4
- Epochs: 3
- Batch size: 4
- Seeds: [42, 43, 44]

New for h-m2:
- Layers to analyze: 24 (12 attention + 12 hidden)
- Activation cache directory
- CKA computation settings

---

## Dependencies

### Core Libraries (From h-m1)
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
lm-evaluation-harness>=0.4.0
```

### New for h-m2
```
transformer-lens>=1.0.0
pytorch-cka>=0.1.0
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
- Error handling for TransformerLens/PEFT conversion
- GPU memory management (activations can be large)
- Activation caching to disk (avoid OOM)

### Success Metrics (PoC)
- Code runs without error on single GPU
- All 3 replicates complete successfully
- Pre/post activations extracted for 24 layers
- CKA similarity computed for all layers
- Correlation analysis completed

### Gate Metric (SHOULD_WORK)
- **Primary**: Significant correlation (p < 0.05) between representation change magnitude and performance improvement
- **Secondary**: Representation changes detectable in >50% of layers (CKA < 1.0)

---

*Generated by Phase 3 Architecture Agent*  
*Patterns Applied: TransformerLens activation extraction, pytorch-cka representation similarity, PyTorch module pattern*  
*MECHANISM hypothesis - extends h-m1 to validate representation change mechanism*

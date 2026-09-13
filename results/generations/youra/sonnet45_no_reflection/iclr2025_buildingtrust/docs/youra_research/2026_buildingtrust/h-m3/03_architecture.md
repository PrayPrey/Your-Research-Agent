# Architecture Specification: h-m3

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M3 (MECHANISM)  
**Type:** Cross-Dimensional Correlation Analysis  

**Applied Patterns:** Multi-task evaluation structure, TransformerLens activation extraction, CKA representation similarity, Pearson correlation analysis

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m2/code/`  
**Findings**: h-m2 implemented GPT-2 + LoRA + TransformerLens pipeline with CKA analysis. Modular structure includes representation_analyzer.py (activation extraction), similarity.py (CKA computation), evaluate.py (TruthfulQA evaluation). h-m3 extends this by adding multi-dimensional evaluation (BBQ, AdvGLUE) and cross-dimensional correlation analysis.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BaselineModel | `from h_m2.src.model import BaselineModel` | `h-m2/code/src/model.py` |
| LoRAInterventionModel | `from h_m2.src.model import LoRAInterventionModel` | `h-m2/code/src/model.py` |
| ActivationExtractor | `from h_m2.src.representation_analyzer import ActivationExtractor` | `h-m2/code/src/representation_analyzer.py` |
| RepresentationAnalyzer | `from h_m2.src.representation_analyzer import RepresentationAnalyzer` | `h-m2/code/src/representation_analyzer.py` |
| CKASimilarity | `from h_m2.src.similarity import CKASimilarity` | `h-m2/code/src/similarity.py` |
| TrustEvaluator | `from h_m2.src.evaluate import TrustEvaluator` | `h-m2/code/src/evaluate.py` |

**Verified from**: `docs/youra_research/20260511_buildingtrust/h-m2/code/` (actual implementation)

**Note**: h-m2 uses GPT-2 wrapped in TransformerLens. h-m3 reuses entire h-m2 pipeline and extends evaluation to 3 dimensions.

---

## Design Principles

**MECHANISM Architecture (H-M3):**
- Validates third step of causal chain: representation changes cause correlated performance shifts across dimensions
- Reuses h-m2's proven TransformerLens + CKA pipeline
- Extends evaluation from single dimension (TruthfulQA only) to multi-dimensional (TruthfulQA + BBQ + AdvGLUE)
- Adds cross-dimensional correlation analysis with permutation testing

**File Count:** 8 core files (adds multi_dimensional_evaluator.py, correlation_analyzer.py to h-m2 structure)

**Key Differences from h-m2:**
- Multi-dimensional evaluation (3 trustworthiness benchmarks)
- Cross-dimensional correlation analysis (Pearson + permutation test)
- Per-dimension performance tracking across replicates
- Increased training samples (100 → 500 for better coverage)

---

## Module Structure

### ConfigModule (`src/config.py`)

**Dependencies**: dataclasses, yaml, h_m2.src.config

```python
@dataclass
class H_M3_Config:
    model_id: str = "gpt2"
    n_replicates: int = 3
    seeds: list[int] = None
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: list[str] = None
    learning_rate: float = 5e-5
    epochs: int = 3
    batch_size: int = 4
    training_samples: int = 500
    device: str = "cuda"
    output_dir: str = "./results"
    layers_to_analyze: list[str] = None
    save_activations: bool = True
    activation_cache_dir: str = "./activations"
    dimensions: list[str] = None
    eval_limit: dict[str, int] = None

def load_config(config_path: str) -> H_M3_Config: ...
def get_default_dimensions() -> list[str]: ...
```

---

### DataModule (`src/data.py`)

**Dependencies**: datasets, transformers, torch

```python
class MultiDimensionalDataset:
    def __init__(self, tokenizer, dimensions: list[str]): ...
    def load_truthfulqa(self, split: str = "validation") -> Dataset: ...
    def load_bbq(self, split: str = "test") -> Dataset: ...
    def load_advglue(self) -> Dataset: ...
    def get_training_samples(self, n_samples: int = 500) -> Dataset: ...
    def get_eval_samples_per_dimension(self, dimension: str) -> Dataset: ...
    def prepare_tokens(self, texts: list[str]) -> torch.Tensor: ...
```

---

### ModelModule (`src/model.py`)

**Dependencies**: h_m2.src.model

```python
from h_m2.src.model import BaselineModel, LoRAInterventionModel

class H_M3_Model:
    def __init__(self, config: H_M3_Config): ...
    def load_baseline(self) -> BaselineModel: ...
    def apply_lora_intervention(self, base_model) -> LoRAInterventionModel: ...
    def get_hooked_model(self) -> HookedTransformer: ...
```

---

### MultiDimensionalEvaluator (`src/multi_dimensional_evaluator.py`)

**Dependencies**: transformers, datasets, lm_eval, torch

```python
class BBQEvaluator:
    def __init__(self, model, tokenizer): ...
    def evaluate(self) -> float: ...
    def load_dataset(self) -> Dataset: ...

class AdvGLUEEvaluator:
    def __init__(self, model, tokenizer): ...
    def evaluate(self) -> float: ...
    def load_dataset(self) -> Dataset: ...

class TruthfulQAEvaluator:
    def __init__(self, model, tokenizer): ...
    def evaluate(self) -> float: ...

class MultiDimensionalEvaluator:
    def __init__(self, model, tokenizer, dimensions: list[str]): ...
    def evaluate_all_dimensions(self) -> dict[str, float]: ...
    def evaluate_dimension(self, dimension: str) -> float: ...
```

---

### CorrelationAnalyzer (`src/correlation_analyzer.py`)

**Dependencies**: scipy, numpy, torch

```python
class CrossDimensionalCorrelationAnalyzer:
    def __init__(self, dimensions: list[str]): ...
    def compute_deltas(
        self, 
        pre_scores: dict[str, float], 
        post_scores: dict[str, float]
    ) -> dict[str, float]: ...
    def compute_pearson_correlation(
        self, 
        deltas1: list[float], 
        deltas2: list[float]
    ) -> tuple[float, float]: ...
    def compute_all_pairs(
        self, 
        deltas_per_seed: dict[str, dict[str, float]]
    ) -> dict[str, tuple[float, float]]: ...
    def permutation_test(
        self, 
        deltas1: list[float], 
        deltas2: list[float], 
        n_permutations: int = 1000
    ) -> float: ...
    def correlate_layer_with_dimensions(
        self, 
        rep_changes: dict[str, float], 
        perf_deltas: dict[str, list[float]]
    ) -> dict[str, dict[str, tuple[float, float]]]: ...
```

---

### RepresentationAnalyzer (`src/representation_analyzer.py`)

**Dependencies**: h_m2.src.representation_analyzer

```python
from h_m2.src.representation_analyzer import RepresentationAnalyzer as H_M2_Analyzer

class H_M3_RepresentationAnalyzer(H_M2_Analyzer):
    def __init__(self, config: H_M3_Config): ...
    def extract_with_multi_eval(
        self, 
        model: HookedTransformer, 
        eval_tokens: dict[str, torch.Tensor], 
        seed: int
    ) -> dict[str, dict[str, torch.Tensor]]: ...
```

---

### SimilarityModule (`src/similarity.py`)

**Dependencies**: h_m2.src.similarity

```python
from h_m2.src.similarity import CKASimilarity

class H_M3_SimilarityAnalyzer:
    def __init__(self, device: str = "cuda"): ...
    def compute_all_layers_cka(
        self, 
        pre_acts: dict, 
        post_acts: dict, 
        layers: list[str]
    ) -> dict[str, float]: ...
```

---

### TrainingModule (`src/train.py`)

**Dependencies**: torch, transformers, peft

```python
class H_M3_Trainer:
    def __init__(self, config: H_M3_Config): ...
    def train_lora(
        self, 
        model, 
        train_dataset, 
        tokenizer, 
        seed: int
    ) -> dict: ...
    def setup_optimizer(self) -> torch.optim.Optimizer: ...
```

---

### VisualizationModule (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class H_M3_FigureGenerator:
    def __init__(self, output_dir: str): ...
    def plot_correlation_scatter(
        self, 
        deltas1: list[float], 
        deltas2: list[float], 
        dim1: str, 
        dim2: str, 
        r: float, 
        p: float
    ): ...
    def plot_correlation_matrix(
        self, 
        correlations: dict[str, tuple[float, float]]
    ): ...
    def plot_layer_dimension_heatmap(
        self, 
        layer_corrs: dict[str, dict[str, tuple[float, float]]]
    ): ...
    def plot_dimension_performance(
        self, 
        pre_scores: dict[str, float], 
        post_scores: dict[str, float]
    ): ...
    def plot_permutation_test(
        self, 
        observed: float, 
        null_dist: list[float]
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
    
    # Load multi-dimensional datasets
    dataset_loader = MultiDimensionalDataset(tokenizer, config.dimensions)
    train_data = dataset_loader.get_training_samples(config.training_samples)
    eval_data = {
        dim: dataset_loader.get_eval_samples_per_dimension(dim)
        for dim in config.dimensions
    }
    
    # Prepare evaluation tokens
    eval_tokens = {
        dim: dataset_loader.prepare_tokens(eval_data[dim])
        for dim in config.dimensions
    }
    
    all_results = []
    
    for seed in config.seeds:
        # Load baseline model
        model_wrapper = H_M3_Model(config)
        baseline_model = model_wrapper.load_baseline()
        hooked_model = model_wrapper.get_hooked_model()
        
        # Pre-intervention evaluation (all 3 dimensions)
        evaluator = MultiDimensionalEvaluator(hooked_model, tokenizer, config.dimensions)
        pre_scores = evaluator.evaluate_all_dimensions()
        
        # Extract pre-intervention activations
        rep_analyzer = H_M3_RepresentationAnalyzer(config)
        pre_acts = rep_analyzer.extract_with_multi_eval(hooked_model, eval_tokens, seed)
        
        # Apply LoRA intervention
        trainer = H_M3_Trainer(config)
        trainer.train_lora(baseline_model, train_data, tokenizer, seed)
        
        # Post-intervention evaluation (all 3 dimensions)
        post_scores = evaluator.evaluate_all_dimensions()
        
        # Extract post-intervention activations
        post_acts = rep_analyzer.extract_with_multi_eval(hooked_model, eval_tokens, seed)
        
        # Compute CKA similarity
        similarity_analyzer = H_M3_SimilarityAnalyzer()
        cka_scores = similarity_analyzer.compute_all_layers_cka(
            pre_acts, post_acts, config.layers_to_analyze
        )
        
        all_results.append({
            "seed": seed,
            "pre_scores": pre_scores,
            "post_scores": post_scores,
            "cka_scores": cka_scores
        })
    
    # Cross-dimensional correlation analysis
    corr_analyzer = CrossDimensionalCorrelationAnalyzer(config.dimensions)
    
    # Compute deltas per seed
    deltas_per_seed = {}
    for result in all_results:
        deltas = corr_analyzer.compute_deltas(result["pre_scores"], result["post_scores"])
        deltas_per_seed[result["seed"]] = deltas
    
    # Correlate all dimension pairs
    correlations = corr_analyzer.compute_all_pairs(deltas_per_seed)
    
    # Permutation tests
    permutation_results = {}
    for pair, (r, p) in correlations.items():
        dim1, dim2 = pair.split("_vs_")
        deltas1 = [deltas_per_seed[seed][dim1] for seed in config.seeds]
        deltas2 = [deltas_per_seed[seed][dim2] for seed in config.seeds]
        p_perm = corr_analyzer.permutation_test(deltas1, deltas2)
        permutation_results[pair] = p_perm
    
    # Layer-wise correlation
    rep_changes = {layer: 1.0 - cka for layer, cka in all_results[0]["cka_scores"].items()}
    perf_deltas = {
        dim: [deltas_per_seed[seed][dim] for seed in config.seeds]
        for dim in config.dimensions
    }
    layer_correlations = corr_analyzer.correlate_layer_with_dimensions(rep_changes, perf_deltas)
    
    # Visualization
    visualizer = H_M3_FigureGenerator(config.output_dir)
    visualizer.save_all_figures()
    
    # Save results
    save_results({
        "correlations": correlations,
        "permutation_tests": permutation_results,
        "layer_correlations": layer_correlations,
        "deltas_per_seed": deltas_per_seed
    }, f"{config.output_dir}/h_m3_validation.json")

if __name__ == "__main__":
    main()
```

---

## File Organization

```
h-m3/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                          # h-m3 configuration
│   │   ├── data.py                            # Multi-dimensional dataset loader
│   │   ├── model.py                           # Model wrapper (reuses h-m2)
│   │   ├── multi_dimensional_evaluator.py     # NEW: 3-dimension evaluation
│   │   ├── correlation_analyzer.py            # NEW: Cross-dimensional correlation
│   │   ├── representation_analyzer.py         # Extends h-m2 analyzer
│   │   ├── similarity.py                      # Reuses h-m2 CKA
│   │   ├── train.py                           # Training with increased samples
│   │   ├── visualize.py                       # Correlation visualizations
│   │   └── main.py                            # Entry point
│   ├── run_experiment.py                      # CLI entry point
│   ├── config.yaml                            # Default configuration
│   └── requirements.txt                       # Dependencies
├── outputs/
│   ├── pre_scores_seed*.json                  # Pre-intervention dimension scores
│   ├── post_scores_seed*.json                 # Post-intervention dimension scores
│   ├── deltas_seed*.json                      # Performance deltas per seed
│   ├── cka_scores_seed*.json                  # CKA scores per seed
│   ├── correlations.json                      # Cross-dimensional correlations
│   ├── permutation_tests.json                 # Permutation test p-values
│   ├── layer_correlations.json                # Layer-wise correlations
│   └── h_m3_validation.json                   # Final validation results
└── figures/
    ├── dimension_correlations.png             # Required gate figure (scatter plots)
    ├── correlation_matrix.png
    ├── layer_dimension_heatmap.png
    ├── dimension_performance.png
    └── permutation_test.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Initialize h-m3 codebase, extend h-m2 structure, add multi-dimensional dependencies | 7 | Module(2) + Deps(2) + Algo(1) + Integ(2) |
| A-2 | Multi-Dimensional Data Pipeline | Load TruthfulQA, BBQ, AdvGLUE datasets with unified interface | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-3 | BBQ Evaluator | Implement BBQ (fairness) evaluation wrapper | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-4 | AdvGLUE Evaluator | Implement AdvGLUE (robustness) evaluation wrapper | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-5 | Multi-Dimensional Orchestrator | Unified evaluator for all 3 dimensions with consistent output format | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-6 | Cross-Dimensional Correlation Analyzer | Compute Pearson correlation between all dimension pairs | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-7 | Permutation Test | Random baseline comparison for observed correlations | 10 | Module(2) + Deps(2) + Algo(4) + Integ(2) |
| A-8 | Layer-Wise Correlation | Correlate per-layer representation changes with dimension-specific deltas | 11 | Module(3) + Deps(2) + Algo(4) + Integ(2) |
| A-9 | Training Pipeline Extension | Increase training samples (100→500), reuse h-m2 LoRA training | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-10 | Visualization Suite | Generate 5 figures: correlation scatter, matrix heatmap, layer heatmap, performance bars, permutation | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-11 | Experiment Orchestration | Main workflow: pre-eval (3D) → train → post-eval (3D) → correlation analysis | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |

**Distribution**: 
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [A-2, A-3, A-4, A-6, A-8, A-10, A-11]
- Low (4-8): [A-1, A-5, A-9]

**Total Complexity**: 100 points across 11 tasks

---

## Task Breakdown Details

**A-1: Project Setup** (7 points)
- Create h-m3 directory structure extending h-m2
- Install multi-dimensional evaluation dependencies (datasets for BBQ, AdvGLUE)
- Configure imports from h-m2 code
- Create config.yaml with 3 dimensions specification

**A-2: Multi-Dimensional Data Pipeline** (10 points)
- Load TruthfulQA (HuggingFace datasets)
- Load BBQ (lighteval/bbq_helm)
- Load AdvGLUE (custom loader from official benchmark)
- Unified interface returning consistent format
- Tokenization handling per dataset format

**A-3: BBQ Evaluator** (9 points)
- Implement bias detection evaluation
- Load BBQ test split
- Multiple-choice accuracy computation
- Handle ambiguous vs unambiguous contexts
- Return fairness score (0-1)

**A-4: AdvGLUE Evaluator** (10 points)
- Download AdvGLUE benchmark from official website
- Implement custom evaluation wrapper
- Support 5 GLUE tasks with adversarial examples
- Compute robustness score
- Handle word-level and sentence-level attacks

**A-5: Multi-Dimensional Orchestrator** (8 points)
- Unified evaluator class for all 3 dimensions
- Consistent output format: {dimension: score}
- Parallel evaluation where possible
- Error handling per dimension
- Logging per-dimension evaluation progress

**A-6: Cross-Dimensional Correlation Analyzer** (9 points)
- Compute deltas: post_score - pre_score per dimension
- Pearson correlation for all dimension pairs (3 pairs)
- Statistical significance testing (p-value < 0.05)
- Return correlation matrix with p-values
- Handle 3 replicates (seeds)

**A-7: Permutation Test** (10 points)
- Implement permutation testing (1000 iterations)
- Randomly shuffle dimension deltas
- Generate null distribution of correlations
- Compare observed correlation to null
- Compute permutation p-value

**A-8: Layer-Wise Correlation** (11 points)
- For each of 24 layers, compute representation change (1 - CKA)
- Correlate layer-specific change with each dimension delta
- Generate 24×3 correlation matrix
- Identify which layers correlate with which dimensions
- Statistical testing per layer-dimension pair

**A-9: Training Pipeline Extension** (7 points)
- Increase training samples from 100 to 500
- Reuse h-m2 LoRA training code
- Same hyperparameters: r=8, α=16, lr=5e-5
- Train for 3 epochs
- Apply to TruthfulQA (target dimension only)

**A-10: Visualization Suite** (9 points)
- Figure 1: Correlation scatter plots (3 panels for dimension pairs)
- Figure 2: Correlation matrix heatmap
- Figure 3: Layer-dimension correlation heatmap (24×3)
- Figure 4: Pre/post performance bar chart (3 dimensions)
- Figure 5: Permutation test visualization (observed vs null distribution)

**A-11: Experiment Orchestration** (10 points)
- Pre-intervention: evaluate all 3 dimensions, extract activations
- Apply LoRA intervention on TruthfulQA (500 samples)
- Post-intervention: re-evaluate all 3 dimensions, extract activations
- Compute CKA for representation changes
- Perform cross-dimensional correlation analysis
- Run permutation tests
- Generate all visualizations
- Loop over 3 seeds for statistical robustness

---

## Integration Notes

### h-m2 Code Reuse Strategy

**Direct Imports (No Modifications):**
- `BaselineModel` (model loading)
- `LoRAInterventionModel` (LoRA configuration)
- `ActivationExtractor` (activation extraction)
- `RepresentationAnalyzer` (pre/post activation extraction)
- `CKASimilarity` (representation similarity computation)

**h-m3 Specific Components:**
- Multi-dimensional evaluation (TruthfulQA + BBQ + AdvGLUE)
- Cross-dimensional correlation analysis (Pearson + permutation)
- Layer-wise dimension-specific correlation
- Extended training samples (500 instead of 100)

### Multi-Dimensional Evaluation Pattern

**Challenge**: Evaluate 3 independent benchmarks with different formats.

**Solution**:
1. Unified evaluator interface returning {dimension: score}
2. Dimension-specific evaluator classes (BBQEvaluator, AdvGLUEEvaluator, TruthfulQAEvaluator)
3. Consistent pre/post evaluation protocol
4. Per-seed evaluation for statistical robustness

**Implementation Pattern**:
```python
# Pre-intervention
pre_scores = {
    'truthfulness': evaluate_truthfulqa(model),
    'fairness': evaluate_bbq(model),
    'robustness': evaluate_advglue(model)
}

# Post-intervention (after LoRA fine-tuning on TruthfulQA)
post_scores = {
    'truthfulness': evaluate_truthfulqa(finetuned_model),
    'fairness': evaluate_bbq(finetuned_model),
    'robustness': evaluate_advglue(finetuned_model)
}

# Compute deltas
deltas = {dim: post_scores[dim] - pre_scores[dim] for dim in dimensions}
```

### Correlation Analysis Pipeline

**Challenge**: Correlate dimension-specific deltas with representation changes.

**Solution**:
1. Aggregate deltas across 3 seeds
2. Compute Pearson correlation for all dimension pairs
3. Permutation test for non-random baseline comparison
4. Layer-wise correlation to identify dimension-specific patterns

**Implementation Pattern**:
```python
# Dimension pair correlation
from scipy.stats import pearsonr
r, p = pearsonr(deltas['truthfulness'], deltas['fairness'])

# Permutation test
null_dist = []
for _ in range(1000):
    permuted = np.random.permutation(deltas['fairness'])
    r_null, _ = pearsonr(deltas['truthfulness'], permuted)
    null_dist.append(r_null)
p_perm = np.mean(np.abs(null_dist) >= np.abs(r))

# Layer-wise correlation
for layer_name, rep_change in representation_changes.items():
    for dim, perf_deltas in dimension_deltas.items():
        r_layer, p_layer = pearsonr([rep_change] * 3, perf_deltas)
```

### Configuration Inheritance

From h-m2 (proven values):
- LoRA rank: 8
- LoRA alpha: 16
- Target modules: ["c_attn"]
- Learning rate: 5e-5
- Epochs: 3
- Batch size: 4
- Seeds: [42, 43, 44]
- Layers to analyze: 24 (12 attention + 12 residual)

New for h-m3:
- Dimensions: ["truthfulness", "fairness", "robustness"]
- Training samples: 500 (increased from 100)
- Evaluation limits per dimension
- Permutation test iterations: 1000

---

## Dependencies

### Core Libraries (From h-m2)
```
torch>=2.0.0
transformers>=4.30.0
peft>=0.4.0
datasets>=2.12.0
transformer-lens>=1.0.0
```

### New for h-m3
```
scipy>=1.10.0
lm-evaluation-harness>=0.4.0
```

### Dataset-Specific
```
datasets>=2.12.0  # TruthfulQA, BBQ via HuggingFace
# AdvGLUE: Custom download from https://adversarialglue.github.io/
```

### Visualization
```
matplotlib>=3.7.0
seaborn>=0.12.0
numpy>=1.24.0
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
- Error handling for dataset loading (especially AdvGLUE custom loader)
- Memory management for multi-dimensional evaluation (clear cache between dimensions)
- Activation caching consistent with h-m2

### Success Metrics
- All 3 dimensions evaluate successfully
- Correlation analysis completes for all dimension pairs
- Permutation tests run for 1000 iterations
- Layer-wise correlation computed for 24 layers × 3 dimensions
- All 5 required figures generated

### Gate Metric (SHOULD_WORK)
- **Primary**: At least one dimension pair shows non-random correlation (p < 0.05)
- **Secondary**: |ρ| > 0.2 for at least one dimension pair (small-to-medium effect)
- **Permutation**: Observed correlation differs from null distribution (p_perm < 0.05)
- **Partial Pass**: Code runs but correlations are random (document as scientific finding)

---

*Generated by Phase 3 Architecture Agent*  
*Patterns Applied: Multi-task evaluation structure, TransformerLens activation extraction, CKA representation similarity, Pearson correlation analysis*  
*MECHANISM hypothesis - extends h-m2 to validate cross-dimensional correlation propagation*

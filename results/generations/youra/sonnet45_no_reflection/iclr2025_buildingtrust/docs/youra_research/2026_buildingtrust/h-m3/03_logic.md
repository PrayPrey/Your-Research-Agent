# Logic Specification: h-m3

**Document Version:** 1.0  
**Date:** 2026-05-11  
**Hypothesis:** H-M3 (MECHANISM)  
**Type:** Cross-Dimensional Correlation Analysis  
**Budget:** 0 subtasks (11 Epic tasks defined in architecture)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m2 actual code  
**Analyzed Path**: `docs/youra_research/20260511_buildingtrust/h-m2/code/src/`  
**Relevant Symbols**: BaselineModel, LoRAInterventionModel, ActivationExtractor, RepresentationAnalyzer, CKASimilarity, CorrelationAnalyzer, TransformerLensWrapper, TrustEvaluator

**Key Findings**:
- h-m2 implements GPT-2 + TransformerLens + CKA pipeline
- Proven activation extraction: ActivationExtractor.extract_activations(tokens) returns Dict[str, Tensor]
- CKASimilarity.compute_all_layers() computes similarity for 24 layers
- CorrelationAnalyzer exists but only handles single-dimension correlation
- h-m3 extends with multi-dimensional evaluation (3 benchmarks) and cross-dimensional correlation

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are imported from h-m2. Signatures verified from actual implementation:

```python
# From: h-m2/code/src/model.py (ACTUAL CODE)
class BaselineModel:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B"):
        """Initialize baseline model. Args: model_id (HuggingFace model ID)"""
        ...
    
    def load_model(self) -> AutoModelForCausalLM:
        """Load pretrained model with bfloat16."""
        ...
    
    def load_tokenizer(self) -> AutoTokenizer:
        """Load tokenizer with padding setup."""
        ...

class LoRAInterventionModel:
    def __init__(
        self,
        base_model: AutoModelForCausalLM,
        lora_rank: int = 8,
        lora_alpha: int = 8,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None
    ):
        """Initialize LoRA wrapper. target_modules default: ["q_proj", "v_proj"]"""
        ...
    
    def apply_lora(self) -> PeftModel:
        """Apply LoRA adapter to base model."""
        ...

# From: h-m2/code/src/representation_analyzer.py (ACTUAL CODE)
class ActivationExtractor:
    def __init__(self, model: HookedTransformer, layers: List[str], cache_dir: str):
        """Initialize activation extractor."""
        ...
    
    def extract_activations(self, tokens: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Extract activations. tokens: [N, L] -> Dict[layer_name: Tensor]"""
        ...
    
    def save_activations(self, activations: Dict[str, torch.Tensor], filepath: str):
        """Save activations to cache_dir/filepath."""
        ...
    
    def load_activations(self, filepath: str) -> Dict[str, torch.Tensor]:
        """Load activations from cache_dir/filepath."""
        ...

class RepresentationAnalyzer:
    def __init__(self, config):
        """Initialize representation analyzer."""
        ...
    
    def extract_pre_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """Extract pre-intervention activations. Returns: 24 layers × activations"""
        ...
    
    def extract_post_intervention(
        self,
        model: HookedTransformer,
        eval_tokens: torch.Tensor,
        seed: int
    ) -> Dict[str, torch.Tensor]:
        """Extract post-intervention activations. Returns: 24 layers × activations"""
        ...

# From: h-m2/code/src/similarity.py (ACTUAL CODE)
class CKASimilarity:
    def __init__(self, device: str = "cuda"):
        """Initialize CKA similarity computation."""
        ...
    
    def compute_cka(self, X: torch.Tensor, Y: torch.Tensor) -> float:
        """Compute CKA. X: [N, F], Y: [N, F] -> float (0-1)"""
        ...
    
    def compute_all_layers(
        self,
        pre_acts: Dict[str, torch.Tensor],
        post_acts: Dict[str, torch.Tensor],
        layers: List[str]
    ) -> Dict[str, float]:
        """Compute CKA for all layers. Returns: {layer_name: cka_score}"""
        ...

# From: h-m2/code/src/transformer_lens_wrapper.py (ACTUAL CODE)
class TransformerLensWrapper:
    def __init__(self, model_id: str = "gpt2", device: str = "cuda"):
        """Initialize TransformerLens wrapper."""
        ...
    
    def load_baseline_hooked(self) -> HookedTransformer:
        """Load GPT-2 as HookedTransformer. Returns: model with hook points"""
        ...
    
    def convert_peft_to_hooked(self, peft_model: PeftModel) -> HookedTransformer:
        """Convert PEFT to HookedTransformer. Merges LoRA weights."""
        ...

# From: h-m2/code/src/evaluate.py (ACTUAL CODE)
class TrustEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize evaluator."""
        ...
    
    def evaluate(self, dimension: str, model_path: str = None) -> float:
        """Evaluate model. dimension: "truthfulness" | "fairness" | "robustness". Returns: accuracy"""
        ...
```

**Verified from**: `h-m2/code/` (actual implementation, NOT spec)

**Note**: h-m2 uses model_id="gpt2" and target_modules=["c_attn"] (GPT-2 specific). h-m3 will use identical configuration.

---

## A-1: Project Setup [Complexity: 7, Budget: 0]

**Applied**: Standard PyTorch project structure + h-m2 imports

### API Signatures

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import yaml

@dataclass
class H_M3_Config:
    """Configuration for h-m3 multi-dimensional evaluation."""
    
    # Model (inherited from h-m2)
    model_id: str = "gpt2"
    
    # Replication
    n_replicates: int = 3
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    
    # LoRA (inherited from h-m2)
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: ["c_attn"])
    
    # Training (h-m3: increased samples)
    learning_rate: float = 5e-5
    epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    training_samples: int = 500  # Increased from h-m2's 100
    
    # Multi-dimensional evaluation (NEW)
    dimensions: List[str] = field(default_factory=lambda: ["truthfulness", "fairness", "robustness"])
    eval_limit: Dict[str, int] = field(default_factory=lambda: {"truthfulness": 817, "fairness": 500, "robustness": 500})
    
    # Representation extraction (inherited from h-m2)
    layers_to_analyze: List[str] = field(default_factory=list)
    save_activations: bool = True
    activation_cache_dir: str = "./outputs/activations"
    
    # Environment
    device: str = "cuda"
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    
    def __post_init__(self):
        """Generate layer names for GPT-2 (24 layers: 12 attn + 12 hidden)."""
        if not self.layers_to_analyze:
            self.layers_to_analyze = []
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.attn.hook_pattern")
            for i in range(12):
                self.layers_to_analyze.append(f"blocks.{i}.hook_resid_post")

def load_config(config_path: str) -> H_M3_Config:
    """Load configuration from YAML."""
    ...

def save_config(config: H_M3_Config, output_path: str):
    """Save configuration to YAML."""
    ...
```

---

## A-2: Multi-Dimensional Data Pipeline [Complexity: 10, Budget: 0]

**Applied**: HuggingFace datasets + lm-eval harness for 3 benchmarks

### API Signatures

```python
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer
import torch
from typing import Dict, List, Optional

class MultiDimensionalDataset:
    def __init__(self, tokenizer: PreTrainedTokenizer, dimensions: List[str]):
        """Initialize multi-dimensional dataset loader. dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.tokenizer = tokenizer
        self.dimensions = dimensions
        self.datasets: Dict[str, Dataset] = {}
    
    def load_truthfulqa(self, split: str = "validation") -> Dataset:
        """Load TruthfulQA. Returns: Dataset with 817 questions"""
        ...
    
    def load_bbq(self, split: str = "test") -> Dataset:
        """Load BBQ bias benchmark. Returns: Dataset with 500+ samples"""
        ...
    
    def load_advglue(self) -> Dataset:
        """Load AdvGLUE robustness benchmark. Returns: Dataset"""
        ...
    
    def get_training_samples(self, n_samples: int = 500) -> Dataset:
        """Get training subset from TruthfulQA. Returns: tokenized Dataset [n_samples]"""
        ...
    
    def get_eval_samples_per_dimension(self, dimension: str) -> Dataset:
        """Get evaluation samples for dimension. Returns: Dataset"""
        ...
    
    def prepare_tokens(self, dataset: Dataset) -> torch.Tensor:
        """Tokenize dataset for activation extraction. Returns: [N, L]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_tokens | [500, L] | Training samples (L≤512) |
| eval_tokens_truthfulness | [817, L] | TruthfulQA full set |
| eval_tokens_fairness | [500, L] | BBQ test set |
| eval_tokens_robustness | [500, L] | AdvGLUE samples |

---

## A-3: BBQ Evaluator [Complexity: 9, Budget: 0]

**Applied**: lm-eval harness integration pattern

### API Signatures

```python
from transformers import PreTrainedModel, PreTrainedTokenizer
from datasets import Dataset
import torch

class BBQEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize BBQ fairness evaluator."""
        self.model = model
        self.tokenizer = tokenizer
    
    def load_dataset(self) -> Dataset:
        """Load BBQ test split. Returns: Dataset"""
        ...
    
    def evaluate(self) -> float:
        """Evaluate fairness. Returns: accuracy (0-1)"""
        ...
    
    def _compute_bias_score(self, predictions: List[int], labels: List[int]) -> float:
        """Compute bias metric. Returns: fairness score"""
        ...
```

---

## A-4: AdvGLUE Evaluator [Complexity: 10, Budget: 0]

**Applied**: Custom evaluation wrapper for AdvGLUE benchmark

### API Signatures

```python
from transformers import PreTrainedModel, PreTrainedTokenizer
import torch
from typing import List, Dict

class AdvGLUEEvaluator:
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """Initialize AdvGLUE robustness evaluator."""
        self.model = model
        self.tokenizer = tokenizer
    
    def load_dataset(self) -> Dict[str, Dataset]:
        """Load AdvGLUE tasks. Returns: {task_name: Dataset}"""
        ...
    
    def evaluate(self) -> float:
        """Evaluate robustness across tasks. Returns: average accuracy (0-1)"""
        ...
    
    def evaluate_task(self, task_name: str, dataset: Dataset) -> float:
        """Evaluate single task. Returns: task accuracy"""
        ...
```

### Pseudo-code

```
1. Load AdvGLUE benchmark (5 GLUE tasks with adversarial examples)
2. For each task:
   - Tokenize adversarial examples
   - Run model inference
   - Compute task accuracy
3. Return average accuracy across tasks
```

---

## A-5: Multi-Dimensional Orchestrator [Complexity: 8, Budget: 0]

**Applied**: Unified evaluation interface

### API Signatures

```python
from typing import Dict

class MultiDimensionalEvaluator:
    def __init__(self, model, tokenizer, dimensions: List[str]):
        """Initialize multi-dimensional evaluator. dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.model = model
        self.tokenizer = tokenizer
        self.dimensions = dimensions
        self.evaluators: Dict[str, any] = {}
        self._setup_evaluators()
    
    def _setup_evaluators(self):
        """Setup dimension-specific evaluators."""
        ...
    
    def evaluate_dimension(self, dimension: str) -> float:
        """Evaluate single dimension. Returns: score (0-1)"""
        ...
    
    def evaluate_all_dimensions(self) -> Dict[str, float]:
        """Evaluate all dimensions. Returns: {dimension: score}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | {dim: float} | Per-dimension scores (0-1) |

---

## A-6: Cross-Dimensional Correlation Analyzer [Complexity: 9, Budget: 0]

**Applied**: scipy.stats.pearsonr for correlation analysis

### API Signatures

```python
from scipy.stats import pearsonr
import numpy as np
from typing import Dict, List, Tuple

class CrossDimensionalCorrelationAnalyzer:
    def __init__(self, dimensions: List[str]):
        """Initialize correlation analyzer. dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.dimensions = dimensions
    
    def compute_deltas(
        self,
        pre_scores: Dict[str, float],
        post_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute performance deltas. Returns: {dimension: delta}"""
        ...
    
    def compute_pearson_correlation(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> Tuple[float, float]:
        """Compute Pearson correlation. Returns: (r, p_value)"""
        ...
    
    def compute_all_pairs(
        self,
        deltas_per_seed: Dict[int, Dict[str, float]]
    ) -> Dict[str, Tuple[float, float]]:
        """Compute correlations for all dimension pairs. Returns: {pair: (r, p)}"""
        ...
```

### Pseudo-code

```
1. Compute deltas per seed:
   deltas[seed][dim] = post_scores[seed][dim] - pre_scores[seed][dim]

2. For each dimension pair (dim1, dim2):
   deltas1 = [deltas[seed][dim1] for seed in seeds]
   deltas2 = [deltas[seed][dim2] for seed in seeds]
   r, p = pearsonr(deltas1, deltas2)

3. Return correlation matrix: {f"{dim1}_vs_{dim2}": (r, p)}
```

---

## A-7: Permutation Test [Complexity: 10, Budget: 0]

**Applied**: Permutation testing for random baseline comparison

### API Signatures

```python
import numpy as np
from scipy.stats import pearsonr
from typing import List

class PermutationTester:
    def __init__(self, n_permutations: int = 1000):
        """Initialize permutation tester. n_permutations: 1000 (default)"""
        self.n_permutations = n_permutations
    
    def permutation_test(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> float:
        """Run permutation test. Returns: p_value"""
        ...
    
    def _generate_null_distribution(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> List[float]:
        """Generate null distribution of correlations. Returns: [r_null_1, r_null_2, ...]"""
        ...
```

### Pseudo-code

```
1. Compute observed correlation:
   r_obs, _ = pearsonr(deltas1, deltas2)

2. Generate null distribution (1000 permutations):
   null_dist = []
   for i in range(1000):
       permuted = np.random.permutation(deltas2)
       r_null, _ = pearsonr(deltas1, permuted)
       null_dist.append(r_null)

3. Compare observed to null:
   p_perm = np.mean(np.abs(null_dist) >= np.abs(r_obs))

4. Return p_perm
```

---

## A-8: Layer-Wise Correlation [Complexity: 11, Budget: 0]

**Applied**: Per-layer representation change correlated with dimension-specific deltas

### API Signatures

```python
from scipy.stats import pearsonr
from typing import Dict, List, Tuple

class LayerWiseCorrelationAnalyzer:
    def __init__(self, layers: List[str], dimensions: List[str]):
        """Initialize layer-wise analyzer. layers: 24 layers, dimensions: 3"""
        self.layers = layers
        self.dimensions = dimensions
    
    def correlate_layer_with_dimensions(
        self,
        rep_changes: Dict[str, float],
        perf_deltas: Dict[str, List[float]]
    ) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Correlate layer changes with dimension deltas.
        
        Args:
            rep_changes: {layer: change_magnitude} (24 layers)
            perf_deltas: {dimension: [delta_seed1, delta_seed2, delta_seed3]} (3 dimensions)
        
        Returns:
            {layer: {dimension: (r, p)}}
        """
        ...
    
    def identify_dimension_specific_layers(
        self,
        layer_correlations: Dict[str, Dict[str, Tuple[float, float]]],
        threshold: float = 0.05
    ) -> Dict[str, List[str]]:
        """Identify which layers correlate with which dimensions. Returns: {dimension: [layers]}"""
        ...
```

### Pseudo-code

```
1. For each layer (24 layers):
   rep_change = 1.0 - cka_scores[layer]
   
   For each dimension (3 dimensions):
       perf_deltas_dim = [deltas[seed][dim] for seed in seeds]  # 3 values
       # Correlate single layer change with 3 seed deltas
       r, p = pearsonr([rep_change] * 3, perf_deltas_dim)
       layer_correlations[layer][dim] = (r, p)

2. Generate 24×3 correlation matrix
3. Identify significant layer-dimension pairs (p < 0.05)
```

---

## A-9: Training Pipeline Extension [Complexity: 7, Budget: 0]

**Applied**: Reuse h-m2 LoRA training with increased samples

### API Signatures

```python
from h_m2.src.model import LoRAInterventionModel
from torch.utils.data import DataLoader
import torch

class H_M3_Trainer:
    def __init__(self, config: H_M3_Config):
        """Initialize h-m3 trainer with 500 training samples."""
        self.config = config
    
    def train_lora(
        self,
        model,
        train_dataset,
        tokenizer,
        seed: int
    ) -> Dict:
        """Train LoRA on 500 TruthfulQA samples. Returns: training history"""
        ...
    
    def setup_optimizer(self) -> torch.optim.Optimizer:
        """Setup AdamW optimizer. lr=5e-5"""
        ...
```

---

## A-10: Visualization Suite [Complexity: 9, Budget: 0]

**Applied**: matplotlib + seaborn plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple

class H_M3_FigureGenerator:
    def __init__(self, output_dir: str):
        """Initialize figure generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_correlation_scatter(
        self,
        deltas1: List[float],
        deltas2: List[float],
        dim1: str,
        dim2: str,
        r: float,
        p: float
    ):
        """Plot correlation scatter. 3 points per panel (seeds). Save to dimension_correlations.png"""
        ...
    
    def plot_correlation_matrix(
        self,
        correlations: Dict[str, Tuple[float, float]]
    ):
        """Plot correlation matrix heatmap. 3×3 matrix (dimension pairs)"""
        ...
    
    def plot_layer_dimension_heatmap(
        self,
        layer_corrs: Dict[str, Dict[str, Tuple[float, float]]]
    ):
        """Plot layer-dimension correlation heatmap. 24 layers × 3 dimensions"""
        ...
    
    def plot_dimension_performance(
        self,
        pre_scores: Dict[str, float],
        post_scores: Dict[str, float]
    ):
        """Plot pre/post performance bars. 3 dimensions"""
        ...
    
    def plot_permutation_test(
        self,
        observed: float,
        null_dist: List[float]
    ):
        """Plot permutation test distribution. Observed vs null"""
        ...
    
    def save_all_figures(self, results: Dict):
        """Generate and save all 5 figures."""
        ...
```

---

## A-11: Experiment Orchestration [Complexity: 10, Budget: 0]

**Applied**: Standard experiment workflow with multi-dimensional evaluation

### API Signatures

```python
import torch
import random
import numpy as np
from typing import Dict, List

def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def setup_gpu(gpu_id: int):
    """Setup GPU environment. export CUDA_VISIBLE_DEVICES={gpu_id}"""
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

def run_single_replicate(
    config: H_M3_Config,
    seed: int,
    eval_tokens: Dict[str, torch.Tensor]
) -> Dict:
    """Run single replicate with multi-dimensional evaluation.
    
    Returns:
        {
            "seed": int,
            "pre_scores": {dimension: score},
            "post_scores": {dimension: score},
            "cka_scores": {layer: cka},
            "deltas": {dimension: delta}
        }
    """
    ...

def main():
    """Main experiment orchestrator.
    
    Workflow:
        1. Load config and setup environment
        2. Load 3 datasets (TruthfulQA, BBQ, AdvGLUE)
        3. Prepare evaluation tokens per dimension
        4. For each seed (3 replicates):
           a. Load baseline model with TransformerLens
           b. Pre-intervention: evaluate all 3 dimensions
           c. Extract pre-intervention activations
           d. Apply LoRA intervention (500 TruthfulQA samples)
           e. Post-intervention: evaluate all 3 dimensions
           f. Extract post-intervention activations
           g. Compute CKA similarity (24 layers)
        5. Cross-dimensional correlation analysis:
           a. Compute deltas per seed per dimension
           b. Correlate all dimension pairs (3 pairs)
           c. Permutation tests (1000 iterations)
           d. Layer-wise correlation (24×3 matrix)
        6. Generate visualizations (5 figures)
        7. Save validation results
    """
    ...
```

### Pseudo-code

```
1. Setup:
   config = load_config("config.yaml")
   set_seed(config.seeds[0])
   setup_gpu(0)

2. Load datasets:
   dataset_loader = MultiDimensionalDataset(tokenizer, config.dimensions)
   train_data = dataset_loader.get_training_samples(500)
   eval_data = {
       "truthfulness": dataset_loader.load_truthfulqa(),
       "fairness": dataset_loader.load_bbq(),
       "robustness": dataset_loader.load_advglue()
   }
   eval_tokens = {dim: dataset_loader.prepare_tokens(eval_data[dim]) for dim in config.dimensions}

3. Replicate loop (N=3):
   all_results = []
   for seed in config.seeds:
       set_seed(seed)
       
       # Load baseline with hooks
       wrapper = TransformerLensWrapper(config.model_id)
       hooked_model = wrapper.load_baseline_hooked()
       
       # Pre-intervention multi-dimensional evaluation
       evaluator = MultiDimensionalEvaluator(hooked_model, tokenizer, config.dimensions)
       pre_scores = evaluator.evaluate_all_dimensions()
       
       # Extract pre-intervention activations
       analyzer = RepresentationAnalyzer(config)
       pre_acts = analyzer.extract_pre_intervention(hooked_model, eval_tokens, seed)
       
       # Apply LoRA intervention
       hf_model = BaselineModel(config.model_id).load_model()
       lora_wrapper = LoRAInterventionModel(
           base_model=hf_model,
           lora_rank=config.lora_rank,
           lora_alpha=config.lora_alpha,
           target_modules=config.target_modules
       )
       peft_model = lora_wrapper.apply_lora()
       
       trainer = H_M3_Trainer(config)
       trainer.train_lora(peft_model, train_data, tokenizer, seed)
       
       # Post-intervention multi-dimensional evaluation
       peft_model_merged = peft_model.merge_and_unload()
       hooked_post = wrapper.convert_peft_to_hooked(peft_model_merged)
       post_scores = evaluator.evaluate_all_dimensions()
       
       # Extract post-intervention activations
       post_acts = analyzer.extract_post_intervention(hooked_post, eval_tokens, seed)
       
       # Compute CKA similarity
       cka_module = CKASimilarity(device=config.device)
       cka_scores = cka_module.compute_all_layers(pre_acts, post_acts, config.layers_to_analyze)
       
       all_results.append({
           "seed": seed,
           "pre_scores": pre_scores,
           "post_scores": post_scores,
           "cka_scores": cka_scores
       })

4. Cross-dimensional correlation analysis:
   corr_analyzer = CrossDimensionalCorrelationAnalyzer(config.dimensions)
   
   # Compute deltas per seed
   deltas_per_seed = {}
   for result in all_results:
       deltas = corr_analyzer.compute_deltas(result["pre_scores"], result["post_scores"])
       deltas_per_seed[result["seed"]] = deltas
   
   # Correlate dimension pairs
   correlations = corr_analyzer.compute_all_pairs(deltas_per_seed)
   
   # Permutation tests
   perm_tester = PermutationTester(n_permutations=1000)
   permutation_results = {}
   for pair, (r, p) in correlations.items():
       dim1, dim2 = pair.split("_vs_")
       deltas1 = [deltas_per_seed[seed][dim1] for seed in config.seeds]
       deltas2 = [deltas_per_seed[seed][dim2] for seed in config.seeds]
       p_perm = perm_tester.permutation_test(deltas1, deltas2)
       permutation_results[pair] = p_perm
   
   # Layer-wise correlation
   rep_changes = {layer: 1.0 - cka for layer, cka in all_results[0]["cka_scores"].items()}
   perf_deltas = {
       dim: [deltas_per_seed[seed][dim] for seed in config.seeds]
       for dim in config.dimensions
   }
   layer_analyzer = LayerWiseCorrelationAnalyzer(config.layers_to_analyze, config.dimensions)
   layer_correlations = layer_analyzer.correlate_layer_with_dimensions(rep_changes, perf_deltas)

5. Visualization:
   visualizer = H_M3_FigureGenerator(config.figures_dir)
   visualizer.save_all_figures({
       "correlations": correlations,
       "permutation_results": permutation_results,
       "layer_correlations": layer_correlations,
       "deltas_per_seed": deltas_per_seed
   })

6. Save results:
   save_json({
       "correlations": correlations,
       "permutation_tests": permutation_results,
       "layer_correlations": layer_correlations,
       "deltas_per_seed": deltas_per_seed,
       "replicates": all_results
   }, f"{config.output_dir}/h_m3_validation.json")
```

---

## Implementation Notes

### h-m2 Code Reuse Strategy

**Direct Imports (No Modifications)**:
- `BaselineModel` (model loading)
- `LoRAInterventionModel` (LoRA configuration)
- `ActivationExtractor` (activation extraction)
- `RepresentationAnalyzer` (pre/post activation extraction)
- `CKASimilarity` (representation similarity computation)
- `TransformerLensWrapper` (HookedTransformer conversion)

**h-m3 Specific Components**:
- `MultiDimensionalDataset` (load 3 benchmarks)
- `BBQEvaluator` (fairness evaluation)
- `AdvGLUEEvaluator` (robustness evaluation)
- `MultiDimensionalEvaluator` (unified evaluation interface)
- `CrossDimensionalCorrelationAnalyzer` (dimension pair correlation)
- `PermutationTester` (random baseline comparison)
- `LayerWiseCorrelationAnalyzer` (layer-dimension correlation)

### Multi-Dimensional Evaluation Pattern

**Challenge**: Evaluate 3 independent benchmarks with different formats.

**Solution**:
1. Unified evaluator interface returning {dimension: score}
2. Dimension-specific evaluator classes (BBQEvaluator, AdvGLUEEvaluator, TrustEvaluator)
3. Consistent pre/post evaluation protocol
4. Per-seed evaluation for statistical robustness

### Correlation Analysis Pipeline

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

---

## Validation Checklist

### Self-Validation

- [x] No ASCII diagrams
- [x] KB patterns applied (scipy.stats, permutation testing, multi-dimensional evaluation)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis code verified
- [x] API signatures match actual h-m2 code
- [x] External Dependencies API section included

### Base Hypothesis Verification

- [x] Read actual code from h-m2/code/
- [x] API signatures verified from actual implementation
- [x] Parameter names exactly match (model_id, lora_rank, lora_alpha, target_modules, device)
- [x] External Dependencies API section included
- [x] Configuration inheritance documented

---

*Generated by Phase 3 Logic Agent*  
*Patterns Applied: scipy.stats correlation analysis, permutation testing, multi-dimensional evaluation architecture, TransformerLens activation extraction, CKA representation similarity*  
*MECHANISM hypothesis - extends h-m2 to validate cross-dimensional correlation propagation*

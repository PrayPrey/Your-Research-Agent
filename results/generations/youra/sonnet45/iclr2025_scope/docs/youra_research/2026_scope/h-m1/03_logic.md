---
hypothesis_id: h-m1
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Logic Design
---

# API Logic Specification: Low-Rank Compression Mechanism (h-m1)

**Applied:** PyTorch variance computation pattern, Statistical validation pattern, DataLoader factory pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from h-e1 actual code
**Analyzed Path**: docs/youra_research/20260318_scope/h-e1/code/src/
**Relevant Symbols**: LowRankAnalyzer, MetricsComputer, PileDataModule, AnalysisConfig
**Verification**: Parameter names and types confirmed from implementation files

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-e1 Actual Code)

The following APIs are called from h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/code/src/analyzer.py (ACTUAL CODE)
class LowRankAnalyzer:
    def __init__(
        self,
        model: AutoModelForCausalLM,
        target_layers: range,
        variance_threshold: float = 0.99
    ):
        """Initialize analyzer with model and configuration."""
        ...

    def analyze_layers(
        self,
        dataloader: DataLoader,
        num_samples: int = 100
    ) -> Dict[str, Any]:
        """Run full analysis. Returns: {layer_idx: {effective_rank, operator_entropy, singular_values}}"""
        ...

    def compute_effective_rank(
        self,
        attention_matrix: Tensor,
        threshold: Optional[float] = None
    ) -> float:
        """Compute effective rank. attention_matrix: [B, H, L, L] -> scalar"""
        ...

    def compute_operator_entropy(self, layer_idx: int) -> float:
        """Compute entropy from Q/K weights. Returns: scalar"""
        ...

# From: h-e1/code/src/metrics.py
class MetricsComputer:
    @staticmethod
    def entropy_regression(
        layer_indices: List[int],
        entropies: List[float]
    ) -> Dict[str, float]:
        """Fit linear regression. Returns: {slope, intercept, p_value, r_squared, std_err}"""
        ...

# From: h-e1/code/src/data.py
class PileDataModule:
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_length: int,
        batch_size: int = 4
    ):
        """Initialize data module."""
        ...

    def setup(self, num_samples: int = 5000) -> None:
        """Load and prepare dataset."""
        ...

    def get_dataloader(self) -> DataLoader:
        """Return configured DataLoader. Yields: {input_ids: [B, L], attention_mask: [B, L]}"""
        ...

# From: h-e1/code/src/config.py
@dataclass
class AnalysisConfig:
    model_name: str = "mistralai/Mistral-7B-v0.1"
    target_layers: range = field(default_factory=lambda: range(20, 32))
    variance_threshold: float = 0.99
    num_samples: int = 50
    context_length: int = 512
    batch_size: int = 1
    random_seed: int = 42
    output_dir: str = "../figures"
    device: str = "cuda"
    use_fp16: bool = True
    hf_token: Optional[str] = None
```

**Verified from**: h-e1/code/src/ (actual implementation)

---

## M-2: Context Length Data Pipeline [Complexity: 9, Budget: 4]

**Applied**: DataLoader factory pattern

### API Signatures

```python
class MultiContextDataModule:
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        context_lengths: List[int],
        batch_size: int = 1
    ):
        """Initialize multi-context data module."""
        self.tokenizer = tokenizer
        self.context_lengths = context_lengths
        self.batch_size = batch_size

    def get_dataloader_factory(self) -> Callable[[int], DataLoader]:
        """Return factory function. Returns: context_length -> DataLoader"""
        def factory(context_length: int) -> DataLoader:
            data_module = PileDataModule(
                tokenizer=self.tokenizer,
                context_length=context_length,
                batch_size=self.batch_size
            )
            data_module.setup(num_samples=10)
            return data_module.get_dataloader()
        return factory
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | L varies: 8192, 16384, 32768, 65536, 131072 |
| attention_mask | [B, L] | Same as input_ids |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Factory function | Implement context_length -> DataLoader factory |
| L-2-2 | PileDataModule reuse | Instantiate h-e1 data module per context |
| L-2-3 | Memory management | Clear cache between context lengths |
| L-2-4 | Validation | Test all 5 context lengths load correctly |

---

## M-3: Stability Testing Module [Complexity: 10, Budget: 4]

**Applied**: PyTorch variance computation pattern

### API Signatures

```python
class ContextStabilityTester:
    def __init__(
        self,
        analyzer: LowRankAnalyzer,
        context_lengths: List[int] = [8192, 16384, 32768, 65536, 131072]
    ):
        """Initialize stability tester."""
        self.analyzer = analyzer
        self.context_lengths = context_lengths

    def test_context_stability(
        self,
        dataloader_factory: Callable[[int], DataLoader],
        num_samples_per_length: int = 10
    ) -> Dict[int, Dict[int, float]]:
        """Test stability. Returns: {context_length: {layer_idx: entropy}}"""
        ...

    def compute_variance_metrics(
        self,
        stability_results: Dict[int, Dict[int, float]]
    ) -> Dict[int, float]:
        """Compute variance per layer. Returns: {layer_idx: variance}"""
        ...

    def validate_stability(
        self,
        variance_metrics: Dict[int, float],
        baseline_variance: float,
        threshold: float = 1.2
    ) -> bool:
        """Check stability criterion. Returns: True if all variances ≤ threshold*baseline"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropies | List[float] × 5 | One per context length |
| variance | scalar | Per-layer variance |

### Pseudo-code

```
test_context_stability():
  1. results = {}
  2. for context_length in [8K, 16K, 32K, 64K, 128K]:
       a. dataloader = dataloader_factory(context_length)
       b. layer_results = analyzer.analyze_layers(dataloader, num_samples=10)
       c. results[context_length] = {layer: data['operator_entropy'] for layer, data in layer_results.items()}
  3. return results

compute_variance_metrics():
  1. variance_per_layer = {}
  2. for layer_idx in analyzer.target_layers:
       a. entropies = [stability_results[ctx][layer_idx] for ctx in context_lengths]
       b. variance_per_layer[layer_idx] = np.var(entropies)
  3. return variance_per_layer

validate_stability():
  1. for layer_idx, variance in variance_metrics.items():
       a. if variance > threshold * baseline_variance:
            return False
  2. return True
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Multi-context loop | Iterate over 5 context lengths |
| L-3-2 | Analyzer integration | Call analyze_layers per context |
| L-3-3 | Variance computation | Compute np.var across contexts |
| L-3-4 | Threshold validation | Check variance ≤ 1.2× baseline |

---

## M-4: Mechanism Verification Logic [Complexity: 8, Budget: 3]

**Applied**: Statistical validation pattern

### API Signatures

```python
class MechanismValidator:
    def __init__(
        self,
        analyzer: LowRankAnalyzer,
        stability_tester: ContextStabilityTester
    ):
        """Initialize mechanism validator."""
        self.analyzer = analyzer
        self.stability_tester = stability_tester

    def verify_mechanism_activated(
        self,
        results: Dict[int, Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, bool]]:
        """Check activation indicators. Returns: (all_passed, {indicator: status})"""
        ...

    def verify_compression_mechanism(
        self,
        results: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify rank decreases with depth. Returns: {trend_confirmed, rank_early, rank_deep}"""
        ...

    def validate_gate_criteria(
        self,
        results: Dict[int, Dict[str, Any]],
        stability_results: Dict[int, Dict[int, float]],
        regression_stats: Dict[str, float]
    ) -> Dict[str, bool]:
        """Check MUST_WORK gate. Returns: {rank_criterion, entropy_criterion, stability_criterion}"""
        ...
```

### Pseudo-code

```
verify_mechanism_activated():
  1. indicators = {
       "svd_computed": len(results) == len(analyzer.target_layers),
       "rank_measured": all('effective_rank' in r for r in results.values()),
       "entropy_measured": all('operator_entropy' in r for r in results.values()),
       "regression_valid": regression_stats is not None and 'slope' in regression_stats
     }
  2. return all(indicators.values()), indicators

verify_compression_mechanism():
  1. early_layers = [20, 21, 22]
  2. deep_layers = [29, 30, 31]
  3. rank_early = mean([results[i]['effective_rank'] for i in early_layers])
  4. rank_deep = mean([results[i]['effective_rank'] for i in deep_layers])
  5. return {'trend_confirmed': rank_deep < rank_early, 'rank_early': rank_early, 'rank_deep': rank_deep}

validate_gate_criteria():
  1. rank_criterion = all(results[i]['effective_rank'] < 256 for i in range(20, 32))
  2. entropy_criterion = regression_stats['slope'] < 0 and regression_stats['p_value'] < 0.01
  3. variance_metrics = stability_tester.compute_variance_metrics(stability_results)
  4. baseline_variance = mean(variance_metrics.values())
  5. stability_criterion = stability_tester.validate_stability(variance_metrics, baseline_variance, threshold=1.2)
  6. return {rank_criterion, entropy_criterion, stability_criterion}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Activation checks | Verify SVD/entropy computed for all layers |
| L-4-2 | Compression trend | Compare early vs deep layer ranks |
| L-4-3 | Gate validation | Check all 3 MUST_WORK criteria |

---

## Supporting Modules (No Budget Allocation)

### ExtendedConfig (`src/config.py`)

```python
from h_e1.src.config import AnalysisConfig
from dataclasses import dataclass, field

@dataclass
class MechanismConfig(AnalysisConfig):
    """Extended configuration for mechanism validation."""
    context_lengths: List[int] = field(default_factory=lambda: [8192, 16384, 32768, 65536, 131072])
    samples_per_context: int = 10
    stability_threshold: float = 1.2
    baseline_context_length: int = 8192

def load_config() -> MechanismConfig:
    """Load configuration. Returns: MechanismConfig with defaults"""
    ...
```

### MechanismExperimentRunner (`src/main.py`)

```python
class MechanismExperimentRunner:
    def __init__(self, config: MechanismConfig):
        """Initialize experiment runner."""
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.analyzer: Optional[LowRankAnalyzer] = None
        self.stability_tester: Optional[ContextStabilityTester] = None
        self.validator: Optional[MechanismValidator] = None

    def setup_base_analyzer(self) -> LowRankAnalyzer:
        """Load model and create analyzer. Returns: configured LowRankAnalyzer"""
        ...

    def run_base_analysis(self) -> Dict[int, Dict[str, Any]]:
        """Run h-e1 baseline analysis. Returns: layer results"""
        ...

    def run_stability_tests(self) -> Dict[int, Dict[int, float]]:
        """Run multi-context stability tests. Returns: {context: {layer: entropy}}"""
        ...

    def validate_mechanism(
        self,
        base_results: Dict[int, Dict[str, Any]],
        stability_results: Dict[int, Dict[int, float]]
    ) -> Dict[str, Any]:
        """Run all validation checks. Returns: {gate_passed, activation, compression, criteria}"""
        ...

    def generate_report(self, validation_results: Dict[str, Any]) -> None:
        """Write 04_validation.md with MECHANISM gate decision."""
        ...

def main():
    """Entry point for mechanism validation experiment."""
    config = load_config()
    runner = MechanismExperimentRunner(config)
    base_results = runner.run_base_analysis()
    stability_results = runner.run_stability_tests()
    validation = runner.validate_mechanism(base_results, stability_results)
    runner.generate_report(validation)
```

### ExtendedVisualizer (`src/visualize.py`)

```python
from h_e1.src.visualize import AnalysisVisualizer

class MechanismVisualizer(AnalysisVisualizer):
    def plot_entropy_stability_heatmap(
        self,
        stability_results: Dict[int, Dict[int, float]]
    ) -> None:
        """Generate stability heatmap. context_lengths × layers"""
        ...
```

---

## Data Flow Summary

```
1. Load Model → Create LowRankAnalyzer (reuse h-e1)
2. Base Analysis:
   a. Run analyze_layers with baseline context (8K)
   b. Extract ranks and entropies
3. Stability Testing:
   a. For each context (8K, 16K, 32K, 64K, 128K):
      - Create dataloader
      - Run analyze_layers (10 samples)
      - Extract entropies
   b. Compute variance per layer
4. Mechanism Verification:
   a. Check activation indicators
   b. Verify compression trend (early > deep)
   c. Validate gate criteria (rank, entropy, stability)
5. Generate Report:
   a. Write 04_validation.md with MECHANISM pass/fail
   b. Generate extended visualizations
```

---

## Validation Logic

```python
def validate_mechanism(base_results, stability_results):
    # 1. Mechanism activated
    activated, indicators = validator.verify_mechanism_activated(base_results)
    if not activated:
        return {'gate_passed': False, 'reason': 'Mechanism not activated'}

    # 2. Compression trend
    compression = validator.verify_compression_mechanism(base_results)
    if not compression['trend_confirmed']:
        return {'gate_passed': False, 'reason': 'No compression trend'}

    # 3. Gate criteria
    regression_stats = MetricsComputer.entropy_regression(
        layer_indices=list(base_results.keys()),
        entropies=[r['operator_entropy'] for r in base_results.values()]
    )
    criteria = validator.validate_gate_criteria(base_results, stability_results, regression_stats)

    gate_passed = all(criteria.values())
    return {
        'gate_passed': gate_passed,
        'activation': indicators,
        'compression': compression,
        'criteria': criteria,
        'regression': regression_stats
    }
```

---

## Memory Management

```python
# Clear cache between context lengths
def run_stability_tests():
    results = {}
    for context_length in config.context_lengths:
        dataloader = dataloader_factory(context_length)
        layer_results = analyzer.analyze_layers(dataloader, num_samples=10)
        results[context_length] = {
            layer: data['operator_entropy']
            for layer, data in layer_results.items()
        }
        # Critical: clear GPU cache
        torch.cuda.empty_cache()
    return results
```

---

## Error Handling

```python
# Stability test failure handling
try:
    stability_results = run_stability_tests()
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        # Reduce context lengths or batch size
        config.context_lengths = [8192, 16384, 32768]
        stability_results = run_stability_tests()
    else:
        raise e

# Missing layer data
if layer_idx not in base_results:
    print(f"Warning: Layer {layer_idx} missing from base results")
    continue
```

---

*Logic specification for MECHANISM validation | Budget: 11 subtasks (M-2: 4, M-3: 4, M-4: 3) | Total: 11 subtasks*

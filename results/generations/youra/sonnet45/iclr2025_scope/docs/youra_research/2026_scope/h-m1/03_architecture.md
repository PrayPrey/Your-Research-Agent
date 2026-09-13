---
hypothesis_id: h-m1
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Architecture Design
---

# System Architecture: Low-Rank Compression Mechanism (h-m1)

**Applied:** PyTorch SVD analysis pattern, HuggingFace model loading pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Reuses h-e1 analysis framework
**Analyzed Path**: docs/youra_research/20260318_scope/h-e1/code/
**Findings**: h-e1 implements SVD-based effective rank and operator entropy analysis. h-m1 extends this with context-length stability testing and deeper mechanism validation.

---

## Architecture Overview

**Type**: Mechanism validation experiment (extends h-e1)
**Reuse Strategy**: Import h-e1 analyzer, add stability testing module
**Components**: 2 new modules + reuse 5 from h-e1
**Infrastructure**: Minimal (extends h-e1 single-run script)

---

## Module Structure

### External Dependencies (Base Hypothesis)

**Module Paths (From h-e1 Actual Code):**

| Module | Import Path | File Location |
|--------|-------------|---------------|
| LowRankAnalyzer | `from h_e1.src.analyzer import LowRankAnalyzer` | `h-e1/code/src/analyzer.py` |
| MetricsComputer | `from h_e1.src.metrics import MetricsComputer` | `h-e1/code/src/metrics.py` |
| AnalysisVisualizer | `from h_e1.src.visualize import AnalysisVisualizer` | `h-e1/code/src/visualize.py` |
| PileDataModule | `from h_e1.src.data import PileDataModule` | `h-e1/code/src/data.py` |
| AnalysisConfig | `from h_e1.src.config import AnalysisConfig` | `h-e1/code/src/config.py` |

**Verified from**: h-e1/code/ (actual implementation)

---

### StabilityTester (`src/stability.py`)

**Dependencies**: LowRankAnalyzer (h-e1), torch, scipy

```python
class ContextStabilityTester:
    def __init__(self, analyzer: LowRankAnalyzer, context_lengths: List[int] = [8192, 16384, 32768, 65536, 131072]): ...

    def test_context_stability(self, dataloader_factory: Callable, num_samples_per_length: int = 10) -> dict: ...

    def compute_variance_metrics(self, stability_results: dict) -> dict: ...

    def validate_stability(self, variance_metrics: dict, baseline_variance: float, threshold: float = 1.2) -> bool: ...
```

---

### MechanismValidator (`src/validator.py`)

**Dependencies**: LowRankAnalyzer (h-e1), StabilityTester, MetricsComputer (h-e1)

```python
class MechanismValidator:
    def __init__(self, analyzer: LowRankAnalyzer, stability_tester: StabilityTester): ...

    def verify_mechanism_activated(self, results: dict) -> Tuple[bool, dict]: ...

    def verify_compression_mechanism(self, results: dict) -> dict: ...

    def validate_gate_criteria(self, results: dict, stability_results: dict) -> dict: ...

    def generate_validation_report(self, validation_results: dict) -> None: ...
```

---

### ExtendedExperimentRunner (`src/main.py`)

**Dependencies**: ExperimentRunner (h-e1), StabilityTester, MechanismValidator

```python
class MechanismExperimentRunner:
    def __init__(self, config: dict): ...

    def setup_base_analyzer(self) -> LowRankAnalyzer: ...

    def run_base_analysis(self) -> dict: ...

    def run_stability_tests(self) -> dict: ...

    def validate_mechanism(self, base_results: dict, stability_results: dict) -> dict: ...

    def generate_report(self, validation_results: dict) -> None: ...

def main():
    config = load_config()
    runner = MechanismExperimentRunner(config)
    base_results = runner.run_base_analysis()
    stability_results = runner.run_stability_tests()
    validation = runner.validate_mechanism(base_results, stability_results)
    runner.generate_report(validation)
```

---

### ExtendedConfig (`src/config.py`)

**Dependencies**: AnalysisConfig (h-e1)

```python
@dataclass
class MechanismConfig(AnalysisConfig):
    context_lengths: List[int] = field(default_factory=lambda: [8192, 16384, 32768, 65536, 131072])
    samples_per_context: int = 10
    stability_threshold: float = 1.2
    baseline_context_length: int = 8192

def load_config() -> MechanismConfig: ...
```

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── stability.py       # ContextStabilityTester
│   │   ├── validator.py       # MechanismValidator
│   │   ├── config.py          # MechanismConfig (extends h-e1)
│   │   └── main.py            # MechanismExperimentRunner
│   ├── run_mechanism.sh       # GPU setup + execution script
│   └── requirements.txt       # Adds h-e1 as dependency
├── figures/                   # Generated visualizations
└── results/                   # Mechanism validation outputs (JSON)
```

---

## Data Flow

1. **Base Analysis** (reuse h-e1): Run SVD/entropy analysis on layers 20-32 with baseline context (8K)
2. **Context Stability Testing**: Repeat analysis at 5 context lengths (8K, 16K, 32K, 64K, 128K) with 10 samples each
3. **Variance Computation**: Calculate entropy variance across context lengths per layer
4. **Mechanism Verification**: Check activation indicators (SVD computed, entropy measured, regression valid)
5. **Gate Validation**: Verify r_eff < 256 (L≥20), β < 0 (p<0.01), variance ≤ 1.2× baseline
6. **Visualization**: Extend h-e1 figures with entropy stability heatmap (context × layer)
7. **Report**: Write 04_validation.md with MECHANISM pass/fail decision

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup h-e1 Integration | Install h-e1 as dependency, configure import paths, verify base analyzer works | 6 | 2+1+2+1 |
| M-2 | Context Length Data Pipeline | Extend PileDataModule to generate samples at 5 context lengths (8K-128K) | 9 | 3+2+2+2 |
| M-3 | Stability Testing Module | Implement ContextStabilityTester with variance computation across context lengths | 10 | 3+3+2+2 |
| M-4 | Mechanism Verification Logic | Implement activation checks, compression trend validation, regression verification | 8 | 2+2+2+2 |
| M-5 | Extended Visualization | Add entropy stability heatmap (context × layer) to h-e1 visualizations | 7 | 2+2+2+1 |
| M-6 | Gate Validation Pipeline | Implement gate criteria checks (r_eff<256, β<0, variance≤1.2×), generate pass/fail | 8 | 2+2+2+2 |
| M-7 | Mechanism Validation Report | Generate 04_validation.md with mechanism-level analysis and gate decision | 6 | 2+1+2+1 |

**Complexity Distribution:**
- High (9-10): [M-2, M-3]
- Medium (7-8): [M-4, M-5, M-6]
- Low (6): [M-1, M-7]

**Total Complexity**: 54

**Complexity Scoring:**
- Module_Size: 1-5 (lines of code / interfaces)
- Dependencies: 1-5 (number of external dependencies)
- Algorithm: 1-5 (mathematical/computational complexity)
- Integration: 1-5 (cross-module coordination)

---

## Breakdown: Task Complexity Details

### M-1: Setup h-e1 Integration (6)
- Module_Size: 2 (requirements.txt + import paths)
- Dependencies: 1 (h-e1 dependency)
- Algorithm: 2 (path resolution, import validation)
- Integration: 1 (standalone setup)

### M-2: Context Length Data Pipeline (9)
- Module_Size: 3 (extend PileDataModule with multi-context support)
- Dependencies: 2 (datasets, transformers)
- Algorithm: 2 (context windowing, tokenization)
- Integration: 2 (connects to stability tester)

### M-3: Stability Testing Module (10)
- Module_Size: 3 (ContextStabilityTester with variance computation)
- Dependencies: 3 (LowRankAnalyzer, torch, scipy)
- Algorithm: 2 (variance computation, stability checks)
- Integration: 2 (coordinates with base analyzer)

### M-4: Mechanism Verification Logic (8)
- Module_Size: 2 (MechanismValidator with activation checks)
- Dependencies: 2 (h-e1 modules)
- Algorithm: 2 (indicator checks, trend validation)
- Integration: 2 (reads base results, stability results)

### M-5: Extended Visualization (7)
- Module_Size: 2 (add heatmap to AnalysisVisualizer)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 2 (heatmap generation)
- Integration: 1 (extends h-e1 visualizer)

### M-6: Gate Validation Pipeline (8)
- Module_Size: 2 (validate_gate_criteria method)
- Dependencies: 2 (h-e1 metrics)
- Algorithm: 2 (threshold checks, boolean logic)
- Integration: 2 (consumes base + stability results)

### M-7: Mechanism Validation Report (6)
- Module_Size: 2 (generate_validation_report)
- Dependencies: 1 (standard library)
- Algorithm: 2 (markdown generation, formatting)
- Integration: 1 (final stage)

---

## Key Implementation Notes

### Context Stability Algorithm
```python
# From ContextStabilityTester
def test_context_stability(self, dataloader_factory, num_samples_per_length=10):
    results = {}
    for context_length in self.context_lengths:
        dataloader = dataloader_factory(context_length)
        layer_results = self.analyzer.analyze_layers(dataloader, num_samples_per_length)
        results[context_length] = {
            layer_idx: data['operator_entropy']
            for layer_idx, data in layer_results.items()
        }
    return results
```

### Variance Computation
```python
# From ContextStabilityTester
def compute_variance_metrics(self, stability_results):
    variance_per_layer = {}
    for layer_idx in self.analyzer.target_layers:
        entropies = [stability_results[ctx][layer_idx] for ctx in self.context_lengths]
        variance_per_layer[layer_idx] = np.var(entropies)
    return variance_per_layer
```

### Mechanism Activation Verification
```python
# From MechanismValidator
def verify_mechanism_activated(self, results):
    indicators = {
        "svd_computed": len(results) == len(self.analyzer.target_layers),
        "rank_measured": all('effective_rank' in r for r in results.values()),
        "entropy_measured": all('operator_entropy' in r for r in results.values()),
        "regression_valid": 'entropy_slope_beta' in results.get('regression', {})
    }
    return all(indicators.values()), indicators
```

---

## Validation Criteria

**Primary Metrics:**
1. Effective rank decreases with depth (deep layers < early layers)
2. Entropy slope β < 0 with p < 0.01 (monotonic decrease)
3. Entropy variance ≤ 1.2× baseline across context lengths (stability)

**MECHANISM Pass Condition:**
- Mechanism activated (all indicators TRUE)
- Compression trend confirmed (rank decreases L20→L32)
- Regression significant (β < 0, p < 0.01)
- Context stability verified (variance ≤ 1.2× baseline)

**Output:** `04_validation.md` with:
- Mechanism activation status
- Compression mechanism validation
- Context stability results
- Gate decision (PASS/FAIL)

---

## Memory and Performance Constraints

**GPU Memory:**
- LLaMA-7B fp16: ~13GB (same as h-e1)
- Attention matrices (5 context lengths × 10 samples): ~5GB
- Total: <20GB (fits A100 40GB)

**Execution Time:**
- Model loading: 5 min (same as h-e1)
- Base analysis (8K context, 100 samples): 3.5 hours (reuse h-e1)
- Stability tests (5 contexts × 10 samples): 2 hours
- Analysis: 15 min
- Total: ~6 hours

**Optimization:**
- Sequential context processing (not parallel)
- Clear cache between contexts
- Reuse h-e1 base analysis if available

---

## Dependencies

**External Libraries:**
- All h-e1 dependencies (torch, transformers, datasets, scipy, matplotlib, seaborn)
- h-e1 codebase (via relative import or install)

**Access Requirements:**
- Same as h-e1: HuggingFace token, GPU (A100 40GB recommended)

---

## Differences from h-e1 (EXISTENCE)

| Aspect | h-e1 (EXISTENCE) | h-m1 (MECHANISM) |
|--------|------------------|------------------|
| **Goal** | Validate structure exists | Validate mechanism operates as theorized |
| **Analysis** | Single context (baseline) | Multi-context stability test |
| **Validation** | r_eff < 256, β < 0 | + Context stability, mechanism activation |
| **Gate** | Structure exists | Mechanism validated |
| **Code** | Standalone analyzer | Extends h-e1 with stability testing |

---

*Architecture designed for MECHANISM validation | Extends h-e1 | Adds context stability testing*

# System Architecture: h-m1

**Date:** 2026-07-12
**Hypothesis:** h-m1 (MECHANISM - Reliability-Robustness Correlation via Memorization)
**Type:** MECHANISM
**Author:** Architecture Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Statistical correlation analysis pattern (scipy.stats)
- Applied: Multi-dimensional evaluation framework (from h-e1)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Reusing code structure from h-e1 EXISTENCE validation
**Analyzed Path:** `/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code/`
**Findings:** Single-file implementation with integrated scoring functions. Reuse dataset loading, model management, and reliability/robustness scoring. Add correlation analysis module.

---

## System Overview

This MECHANISM hypothesis tests whether factual memorization creates positive correlation (r>0.3, p<0.05) between reliability and robustness metrics. The architecture extends h-e1 evaluation pipeline with stratified analysis (factual vs. misinformation) and statistical correlation testing.

**Core Validation:** Pearson r > 0.3 on factual stratum with 95% CI lower bound > 0.2.

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** datasets, h-e1 base code

```python
class StratifiedTruthfulQALoader:
    def __init__(self): ...
    def load_full_dataset(self) -> list[dict]: ...
    def stratify_by_factuality(self, dataset: list[dict]) -> tuple[list[dict], list[dict]]: ...
    def get_factual_stratum(self) -> list[dict]: ...
    def get_misinformation_stratum(self) -> list[dict]: ...
    def validate_stratification(self, factual: list, misinfo: list) -> bool: ...
```

### ResponseGenerator (`src/response_generator.py`)

**Dependencies:** transformers, torch

```python
class LlamaResponseGenerator:
    def __init__(self, model_size: str): ...
    def load_model(self) -> tuple: ...
    def generate_response(self, prompt: str, seed: int) -> str: ...
    def generate_batch(self, prompts: list[str]) -> list[dict]: ...
    def cleanup(self) -> None: ...
```

### ReliabilityScorer (`src/scorers/reliability_scorer.py`)

**Dependencies:** openai (reuse from h-e1)

```python
class GPT4ReliabilityScorer:
    def __init__(self, api_key: str): ...
    def score_response(self, question: str, answer: str) -> float: ...
    def score_batch(self, qa_pairs: list[tuple]) -> np.ndarray: ...
```

### RobustnessScorer (`src/scorers/robustness_scorer.py`)

**Dependencies:** sentence_transformers (reuse from h-e1)

```python
class ParaphraseRobustnessScorer:
    def __init__(self, sbert_model_name: str): ...
    def generate_paraphrase(self, text: str) -> str: ...
    def compute_consistency(self, original: str, paraphrased: str) -> float: ...
    def score_batch(self, response_pairs: list[tuple]) -> np.ndarray: ...
```

### CorrelationAnalyzer (`src/correlation_analyzer.py`)

**Dependencies:** scipy, numpy

```python
class PearsonCorrelationAnalyzer:
    def __init__(self, alpha: float = 0.05): ...
    def compute_correlation(self, reliability: np.ndarray, robustness: np.ndarray) -> dict: ...
    def fisher_z_confidence_interval(self, r: float, n: int, confidence: float = 0.95) -> tuple[float, float]: ...
    def permutation_test(self, reliability: np.ndarray, robustness: np.ndarray, n_permutations: int = 1000) -> dict: ...
    def validate_gate(self, correlation_result: dict, threshold: float = 0.3, ci_threshold: float = 0.2) -> bool: ...
```

### StratificationAnalyzer (`src/stratification_analyzer.py`)

**Dependencies:** CorrelationAnalyzer, pandas

```python
class StratificationAnalyzer:
    def __init__(self, correlation_analyzer: PearsonCorrelationAnalyzer): ...
    def analyze_factual_stratum(self, results_df: pd.DataFrame) -> dict: ...
    def analyze_misinformation_stratum(self, results_df: pd.DataFrame) -> dict: ...
    def compare_strata(self, factual_result: dict, misinfo_result: dict) -> dict: ...
    def validate_mechanism_hypothesis(self, factual_result: dict) -> bool: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class CorrelationVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics_comparison(self, observed_r: float, threshold: float = 0.3) -> None: ...
    def plot_scatter_with_regression(self, reliability: np.ndarray, robustness: np.ndarray, r: float, p_value: float, ci: tuple) -> None: ...
    def plot_model_comparison(self, correlations_by_model: dict) -> None: ...
    def plot_permutation_test(self, observed_r: float, null_distribution: np.ndarray) -> None: ...
    def plot_confidence_intervals(self, correlations_by_model: dict) -> None: ...
    def plot_stratification_comparison(self, factual_r: float, misinfo_r: float) -> None: ...
    def generate_all_figures(self, results: dict) -> None: ...
```

### Configuration (`src/config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class CorrelationConfig:
    alpha: float = 0.05
    correlation_threshold: float = 0.3
    ci_lower_threshold: float = 0.2
    n_permutations: int = 1000
    confidence_level: float = 0.95

@dataclass
class ExperimentConfig:
    model_sizes: list[str]
    generation_params: dict
    stratification_enabled: bool = True
    output_dir: str
    figures_dir: str
    correlation: CorrelationConfig

def load_config() -> ExperimentConfig: ...
```

### Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    config = load_config()
    
    # Load and stratify dataset
    loader = StratifiedTruthfulQALoader()
    factual_prompts = loader.get_factual_stratum()
    misinfo_prompts = loader.get_misinformation_stratum()
    
    all_results = []
    
    # Process each model size
    for model_size in config.model_sizes:
        # Generate responses
        generator = LlamaResponseGenerator(model_size)
        factual_responses = generator.generate_batch(factual_prompts)
        misinfo_responses = generator.generate_batch(misinfo_prompts)
        
        # Score dimensions
        rel_scorer = GPT4ReliabilityScorer(os.getenv("OPENAI_API_KEY"))
        rob_scorer = ParaphraseRobustnessScorer("all-MiniLM-L6-v2")
        
        factual_reliability = rel_scorer.score_batch(factual_responses)
        factual_robustness = rob_scorer.score_batch(factual_responses)
        
        misinfo_reliability = rel_scorer.score_batch(misinfo_responses)
        misinfo_robustness = rob_scorer.score_batch(misinfo_responses)
        
        # Analyze correlations
        corr_analyzer = PearsonCorrelationAnalyzer(alpha=0.05)
        strat_analyzer = StratificationAnalyzer(corr_analyzer)
        
        factual_result = strat_analyzer.analyze_factual_stratum(
            pd.DataFrame({"reliability": factual_reliability, "robustness": factual_robustness})
        )
        misinfo_result = strat_analyzer.analyze_misinformation_stratum(
            pd.DataFrame({"reliability": misinfo_reliability, "robustness": misinfo_robustness})
        )
        
        comparison = strat_analyzer.compare_strata(factual_result, misinfo_result)
        
        all_results.append({
            "model_size": model_size,
            "factual": factual_result,
            "misinformation": misinfo_result,
            "comparison": comparison
        })
        
        generator.cleanup()
    
    # Validate MECHANISM gate
    gate_passed = all(
        strat_analyzer.validate_mechanism_hypothesis(r["factual"]) 
        for r in all_results
    )
    
    # Visualize results
    visualizer = CorrelationVisualizer(config.figures_dir)
    visualizer.generate_all_figures({
        "results_by_model": all_results,
        "gate_passed": gate_passed
    })
    
    # Save results
    save_results(all_results, config.output_dir)
    
    return 0 if gate_passed else 1
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataLoader | Direct implementation (h-e1 inlined) | `h-e1/code/run_experiment.py:28-35` |
| ModelManager | Direct implementation (h-e1 inlined) | `h-e1/code/run_experiment.py:37-54` |
| ReliabilityScorer | Direct implementation (h-e1 inlined) | `h-e1/code/run_experiment.py:97-154` |
| RobustnessScorer | Direct implementation (h-e1 inlined) | `h-e1/code/run_experiment.py:189-237` |

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code/run_experiment.py` (actual implementation)

**Note:** h-e1 uses single-file architecture. h-m1 will modularize and extend with correlation analysis.

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── response_generator.py
│   │   ├── scorers/
│   │   │   ├── __init__.py
│   │   │   ├── reliability_scorer.py
│   │   │   └── robustness_scorer.py
│   │   ├── correlation_analyzer.py
│   │   ├── stratification_analyzer.py
│   │   ├── visualizer.py
│   │   └── config.py
│   ├── run_experiment.py
│   ├── requirements.txt
│   └── README.md
├── outputs/
│   ├── responses_factual.json
│   ├── responses_misinfo.json
│   ├── results_factual.csv
│   ├── results_misinfo.csv
│   └── correlation_results.json
└── figures/
    ├── gate_metrics_comparison.png (MANDATORY)
    ├── scatter_with_regression.png
    ├── model_comparison.png
    ├── permutation_test.png
    ├── confidence_intervals.png
    └── stratification_comparison.png
```

---

## Data Flow

1. **DataLoader** loads TruthfulQA and stratifies into factual (~400) and misinformation (~400)
2. **ResponseGenerator** generates responses for both strata using Llama-2-chat (7B/13B/70B)
3. **Scorers** compute reliability (GPT-4) and robustness (paraphrase consistency)
4. **CorrelationAnalyzer** computes Pearson r with Fisher z-transform CI and permutation test
5. **StratificationAnalyzer** validates r>0.3 on factual stratum, compares with misinformation
6. **Visualizer** generates 6 figures including mandatory gate metrics comparison
7. **Main Orchestrator** validates MECHANISM gate and saves results

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Stratified Dataset Preparation | Load TruthfulQA, stratify into factual/misinformation strata, validate ~400 each | 9 | Module(2) + Dependencies(2) + Algorithm(3) + Integration(2) |
| B-2 | Response Generation Pipeline | Generate responses for 3 models × 2 strata × ~400 prompts = ~2,400 samples | 11 | Module(3) + Dependencies(2) + Algorithm(3) + Integration(3) |
| B-3 | Reliability and Robustness Scoring | Reuse h-e1 scorers, integrate with stratified dataset | 13 | Module(3) + Dependencies(3) + Algorithm(3) + Integration(4) |
| B-4 | Correlation Analysis Module | Implement Pearson r, Fisher z-transform CI, permutation test | 15 | Module(3) + Dependencies(3) + Algorithm(5) + Integration(4) |
| B-5 | Stratification Analysis | Per-stratum correlation, compare factual vs. misinformation | 12 | Module(3) + Dependencies(2) + Algorithm(4) + Integration(3) |
| B-6 | Statistical Validation | MECHANISM gate validation (r>0.3, p<0.05, CI>0.2) | 10 | Module(2) + Dependencies(2) + Algorithm(3) + Integration(3) |
| B-7 | Visualization Suite | Generate 6 figures including mandatory gate metrics comparison | 14 | Module(3) + Dependencies(3) + Algorithm(4) + Integration(4) |
| B-8 | Results Management | Save correlation results, statistics, generate validation report | 8 | Module(2) + Dependencies(2) + Algorithm(2) + Integration(2) |

**Total Complexity:** 92 (distributed across 8 tasks)

**Distribution:**
- Very High (18-20): []
- High (14-17): [B-4, B-7]
- Medium (9-13): [B-1, B-2, B-3, B-5, B-6]
- Low (4-8): [B-8]

---

## Complexity Analysis

### High-Complexity Components

**B-4: Correlation Analysis (15)**
- Module complexity: Pearson r, Fisher z-transform, permutation test
- Dependencies: scipy.stats (pearsonr), numpy for permutation sampling
- Algorithm: Fisher z-transform confidence intervals, null distribution generation
- Integration: Per-model and per-stratum correlation computation

**B-7: Visualization Suite (14)**
- Module complexity: 6 distinct figure types with statistical annotations
- Dependencies: matplotlib, seaborn, numpy
- Algorithm: Scatter with regression line, permutation distribution overlay, forest plot CI
- Integration: Coordinate with correlation results, gate validation status

### Moderate-Complexity Components

**B-3: Reliability and Robustness Scoring (13)**
- Adapt h-e1 scorers for stratified dataset
- Handle 2x sample size (factual + misinformation)
- API rate limiting for GPT-4

**B-5: Stratification Analysis (12)**
- Per-stratum correlation computation
- Statistical comparison between strata
- Mechanism hypothesis validation logic

**B-2: Response Generation (11)**
- Batch generation for 2 strata
- Checkpoint/resume for fault tolerance
- Memory management for 70B model

**B-6: Statistical Validation (10)**
- Gate validation (r>0.3, p<0.05, CI>0.2)
- Permutation test significance check
- Aggregate results across 3 models

**B-1: Stratified Dataset Preparation (9)**
- TruthfulQA category-based stratification
- Validate stratum sizes (~400 each)
- Handle edge cases (ambiguous categories)

### Low-Complexity Components

**B-8: Results Management (8)**
- Save correlation results as JSON/CSV
- Generate validation report
- Export figures

---

## Critical Dependencies

### External APIs
- **OpenAI GPT-4:** ~2,400 API calls for reliability scoring (2 strata × ~400 prompts × 3 models)

### Compute Resources
- **GPU:** NVIDIA A100 40GB for Llama-2-70B inference
- **Storage:** 200GB+ for model weights, responses, checkpoints
- **Memory:** 128GB+ RAM

### External Libraries
- `scipy >= 1.10.0` (Pearson correlation, Fisher z-transform)
- `transformers >= 4.30.0` (Llama-2)
- `datasets >= 2.14.0` (TruthfulQA)
- `sentence-transformers >= 2.2.0` (semantic similarity)
- `openai >= 1.0.0` (GPT-4 API)
- `pandas >= 2.0.0` (data manipulation)
- `matplotlib >= 3.7.0`, `seaborn >= 0.12.0` (visualization)

---

## Validation Strategy

### MECHANISM Gate Validation
```python
def validate_mechanism_gate(factual_result: dict) -> bool:
    """
    Validate MECHANISM gate on factual stratum:
    - Pearson r > 0.3
    - p-value < 0.05
    - 95% CI lower bound > 0.2
    """
    r = factual_result["correlation"]
    p = factual_result["p_value"]
    ci_lower = factual_result["ci_95"][0]
    
    gate_passed = (r > 0.3) and (p < 0.05) and (ci_lower > 0.2)
    
    return gate_passed
```

### Secondary Validation
- **Permutation Test:** Observed r exceeds 95th percentile of null distribution
- **Model Size Effect:** Correlation increases with model size (7B < 13B < 70B)
- **Stratification Effect:** Factual r > Misinformation r (mechanism specificity)

---

## Risk Mitigation

### Low Correlation (Hypothesis Failure)
- **Strategy:** Analyze per-model results, check for model size effects
- **Fallback:** Gate allows exploration of alternative mechanisms (retrieval quality, model calibration)

### API Rate Limits
- **Strategy:** Exponential backoff, batch requests, checkpoint/resume
- **Fallback:** Prioritize one model (13B) for full analysis if quota limited

### Insufficient Factual Samples
- **Strategy:** Validate TruthfulQA category labeling, manual review if needed
- **Fallback:** Adjust stratification method (use multiple categories)

### Memory Constraints (70B Model)
- **Strategy:** Int8 quantization, sequential model loading
- **Fallback:** Skip 70B if OOM, validate gate on 7B+13B only

---

## Expected Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Stratified Dataset Prep (B-1) | 0.5 days | TruthfulQA access |
| Response Generation (B-2) | 1 day | B-1, GPU access |
| Scoring (B-3) | 2 days | B-2, OpenAI API |
| Correlation Analysis (B-4) | 0.5 days | B-3 |
| Stratification Analysis (B-5) | 0.5 days | B-4 |
| Statistical Validation (B-6) | 0.5 days | B-5 |
| Visualization (B-7) | 0.5 days | B-6 |
| Results Management (B-8) | 0.5 days | B-7 |

**Total:** 4 days (sequential execution)

**Critical Path:** B-1 → B-2 → B-3 → B-4 → B-5 → B-6 → B-7 → B-8

---

## Success Criteria

### Primary (MECHANISM Gate)
- **Pearson r > 0.3** on factual stratum for at least one model
- **p-value < 0.05** (two-tailed test)
- **95% CI lower bound > 0.2**

### Secondary
- At least one model shows r > 0.4 (strong coupling)
- Factual r > Misinformation r (mechanism specificity)
- Permutation test p < 0.05 (null hypothesis rejection)

### Deliverables
- `correlation_results.json` with per-model and per-stratum results
- 6 publication-quality figures including mandatory gate metrics comparison
- Validation report with gate evaluation (PASS/FAIL)

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)

# System Architecture: h-m2

**Date:** 2026-07-12
**Hypothesis:** h-m2 (MECHANISM - Fairness-Reliability Negative Correlation via Alignment Tax)
**Type:** MECHANISM
**Author:** Architecture Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Correlation analysis pattern (scipy.stats.pearsonr)
- Applied: Multi-dimensional evaluation framework

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extending h-m1 correlation analysis pipeline
**Analyzed Path:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/`
**Findings:** Single-file implementation (run_experiment.py) with integrated scoring. Reuse dataset loading, model inference, reliability scoring, and correlation analysis. Add HONEST fairness scoring module.

---

## System Overview

This MECHANISM hypothesis tests whether RLHF alignment creates a negative correlation (r<-0.2, p<0.05) between fairness and reliability metrics. The architecture extends h-m1's validated correlation pipeline by adding a fairness dimension (HONEST bias metric with demographic augmentation).

**Core Validation:** Pearson r < -0.2 with p < 0.05 and 95% CI upper bound < -0.1.

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** datasets, h-m1 base code

```python
class TruthfulQALoader:
    def __init__(self): ...
    def load_full_dataset(self) -> list[dict]: ...
    def get_prompts(self) -> list[str]: ...
    def get_ground_truth(self) -> list[str]: ...
```

### ResponseGenerator (`src/response_generator.py`)

**Dependencies:** transformers, torch

```python
class LlamaResponseGenerator:
    def __init__(self, model_name: str): ...
    def load_model(self) -> tuple: ...
    def generate_response(self, prompt: str, seed: int) -> str: ...
    def generate_batch(self, prompts: list[str]) -> list[str]: ...
    def cleanup(self) -> None: ...
```

### ReliabilityScorer (`src/scorers/reliability_scorer.py`)

**Dependencies:** openai (reuse from h-m1)

```python
class GPT4ReliabilityScorer:
    def __init__(self, api_key: str): ...
    def score_response(self, question: str, answer: str, ground_truth: str) -> float: ...
    def score_batch(self, qa_pairs: list[tuple]) -> np.ndarray: ...
```

### FairnessScorer (`src/scorers/fairness_scorer.py`)

**Dependencies:** transformers, sentence_transformers (NEW for h-m2)

```python
class HONESTFairnessScorer:
    def __init__(self, model, tokenizer, sbert_model_name: str = "all-MiniLM-L6-v2"): ...
    def generate_demographic_variants(self, question: str) -> dict[str, str]: ...
    def generate_variant_responses(self, variants: dict[str, str]) -> dict[str, str]: ...
    def compute_consistency_score(self, responses: dict[str, str]) -> float: ...
    def score_batch(self, questions: list[str]) -> np.ndarray: ...
```

### CorrelationAnalyzer (`src/correlation_analyzer.py`)

**Dependencies:** scipy, numpy (reuse from h-m1)

```python
class PearsonCorrelationAnalyzer:
    def __init__(self, alpha: float = 0.05): ...
    def compute_correlation(self, fairness: np.ndarray, reliability: np.ndarray) -> dict: ...
    def fisher_z_confidence_interval(self, r: float, n: int, confidence: float = 0.95) -> tuple[float, float]: ...
    def validate_gate(self, correlation_result: dict, threshold: float = -0.2, ci_threshold: float = -0.1) -> bool: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class CorrelationVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics_comparison(self, observed_r: float, threshold: float = -0.2) -> None: ...
    def plot_scatter_with_regression(self, fairness: np.ndarray, reliability: np.ndarray, r: float, p_value: float) -> None: ...
    def plot_dimension_distributions(self, fairness: np.ndarray, reliability: np.ndarray) -> None: ...
    def plot_quadrant_analysis(self, fairness: np.ndarray, reliability: np.ndarray) -> None: ...
    def generate_all_figures(self, results: dict) -> None: ...
```

### Configuration (`src/config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class DemographicConfig:
    demographics: list[str] = field(default_factory=lambda: ["Black", "Asian", "White", "Hispanic"])
    prompt_template: str = "A {demographic} person asks: {question}"

@dataclass
class CorrelationConfig:
    alpha: float = 0.05
    correlation_threshold: float = -0.2
    ci_upper_threshold: float = -0.1
    confidence_level: float = 0.95

@dataclass
class ExperimentConfig:
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    generation_params: dict
    output_dir: str
    figures_dir: str
    demographic: DemographicConfig
    correlation: CorrelationConfig

def load_config() -> ExperimentConfig: ...
```

### Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    config = load_config()
    
    # Load dataset (reuse h-m1)
    loader = TruthfulQALoader()
    questions = loader.get_prompts()
    ground_truth = loader.get_ground_truth()
    
    # Generate responses (reuse h-m1)
    generator = LlamaResponseGenerator(config.model_name)
    responses = generator.generate_batch(questions)
    
    # Score reliability (reuse h-m1)
    rel_scorer = GPT4ReliabilityScorer(os.getenv("OPENAI_API_KEY"))
    reliability_scores = rel_scorer.score_batch(zip(questions, responses, ground_truth))
    
    # Score fairness (NEW for h-m2)
    fair_scorer = HONESTFairnessScorer(
        generator.model, 
        generator.tokenizer,
        config.demographic.sbert_model
    )
    fairness_scores = fair_scorer.score_batch(questions)
    
    # Analyze correlation (adapt h-m1)
    corr_analyzer = PearsonCorrelationAnalyzer(alpha=0.05)
    result = corr_analyzer.compute_correlation(fairness_scores, reliability_scores)
    
    # Validate gate
    gate_passed = corr_analyzer.validate_gate(result)
    
    # Visualize (adapt h-m1)
    visualizer = CorrelationVisualizer(config.figures_dir)
    visualizer.generate_all_figures({
        "fairness": fairness_scores,
        "reliability": reliability_scores,
        "correlation_result": result,
        "gate_passed": gate_passed
    })
    
    # Save results
    save_results(result, gate_passed, config.output_dir)
    
    generator.cleanup()
    
    return 0 if gate_passed else 1
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataLoader | Inlined in run_experiment.py | `h-m1/code/run_experiment.py:33-88` |
| ModelManager | Inlined in run_experiment.py | `h-m1/code/run_experiment.py:90-120` |
| ReliabilityScorer | Inlined in run_experiment.py | `h-m1/code/run_experiment.py` (GPT-4 scoring) |
| CorrelationAnalyzer | Inlined in run_experiment.py | `h-m1/code/run_experiment.py` (scipy.stats) |
| Config Module | `from src.config import load_config` | `h-m1/code/src/config.py` |

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/run_experiment.py` (actual implementation)

**Note:** h-m1 uses mostly inlined implementation in run_experiment.py. h-m2 will maintain similar structure with added fairness scoring module.

---

## File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── scorers/
│   │   │   ├── __init__.py
│   │   │   ├── reliability_scorer.py  (reuse h-m1)
│   │   │   └── fairness_scorer.py     (NEW)
│   │   └── config.py
│   ├── run_experiment.py
│   ├── requirements.txt
│   └── README.md
├── outputs/
│   ├── responses.jsonl
│   ├── scores.csv
│   └── correlation_results.json
└── figures/
    ├── gate_metrics_comparison.png     (MANDATORY)
    ├── scatter_plot.png
    ├── distributions.png
    └── quadrant_analysis.png
```

---

## Data Flow

1. **DataLoader** loads TruthfulQA (817 prompts)
2. **ResponseGenerator** generates responses using Llama-2-7b-chat
3. **ReliabilityScorer** scores factual correctness (GPT-4 or heuristic)
4. **FairnessScorer** generates demographic variants, computes HONEST bias score
5. **CorrelationAnalyzer** computes Pearson r with Fisher z-transform CI
6. **Visualizer** generates 4 figures including mandatory gate comparison
7. **Main Orchestrator** validates gate (r<-0.2, p<0.05, CI<-0.1) and saves results

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Dataset Loading | Load TruthfulQA (817 prompts), validate structure | 6 | Module(2) + Dependencies(1) + Algorithm(1) + Integration(2) |
| C-2 | Response Generation | Generate responses for all prompts using Llama-2-7b-chat | 8 | Module(2) + Dependencies(2) + Algorithm(2) + Integration(2) |
| C-3 | Reliability Scoring | Reuse h-m1 GPT-4 scoring or heuristic fallback | 10 | Module(2) + Dependencies(3) + Algorithm(2) + Integration(3) |
| C-4 | Fairness Scoring Module (NEW) | HONEST metric with demographic augmentation (4 demographics × 817 prompts) | 16 | Module(4) + Dependencies(3) + Algorithm(5) + Integration(4) |
| C-5 | Correlation Analysis | Compute Pearson r, Fisher z-transform CI, p-value | 12 | Module(3) + Dependencies(2) + Algorithm(4) + Integration(3) |
| C-6 | Gate Validation | Check r<-0.2, p<0.05, CI<-0.1 criteria | 7 | Module(2) + Dependencies(1) + Algorithm(2) + Integration(2) |
| C-7 | Visualization Suite | Generate 4 figures (gate comparison, scatter, distributions, quadrants) | 11 | Module(3) + Dependencies(2) + Algorithm(3) + Integration(3) |
| C-8 | Results Management | Save correlation results, generate validation report | 6 | Module(2) + Dependencies(1) + Algorithm(1) + Integration(2) |

**Total Complexity:** 76 (distributed across 8 tasks)

**Distribution:**
- Very High (18-20): []
- High (14-17): [C-4]
- Medium (9-13): [C-3, C-5, C-7]
- Low (4-8): [C-1, C-2, C-6, C-8]

---

## Complexity Analysis

### High-Complexity Components

**C-4: Fairness Scoring Module (16)**
- Module complexity: Demographic variant generation, semantic similarity computation
- Dependencies: sentence_transformers (SBERT), transformers (model inference)
- Algorithm: HONEST bias metric (consistency scoring across demographic variants)
- Integration: 5× inference load (817 × 5 = 4085 generations total)

### Moderate-Complexity Components

**C-5: Correlation Analysis (12)**
- Reuse h-m1 statistical framework
- Fisher z-transform confidence intervals
- Two-tailed significance test

**C-7: Visualization Suite (11)**
- 4 publication-quality figures
- Quadrant analysis (high-fairness-low-reliability region)
- Statistical annotations (r, p-value, CI)

**C-3: Reliability Scoring (10)**
- Reuse h-m1 GPT-4 scorer
- Fallback to heuristic if API unavailable
- 817 API calls with rate limiting

### Low-Complexity Components

**C-2: Response Generation (8)**
- Reuse h-m1 inference pipeline
- Fixed parameters (temp=0.7, top_p=0.9, max_tokens=256)

**C-6: Gate Validation (7)**
- Simple threshold checks
- SHOULD_WORK gate allows pivots

**C-1: Dataset Loading (6)**
- Direct HuggingFace load
- Minimal preprocessing

**C-8: Results Management (6)**
- Save JSON/CSV outputs
- Generate markdown report

---

## Critical Dependencies

### External APIs
- **OpenAI GPT-4:** ~817 API calls for reliability scoring (with fallback to heuristic)

### Compute Resources
- **GPU:** NVIDIA GPU with 16GB+ VRAM for Llama-2-7b FP16
- **Storage:** 30GB+ for model weights, responses
- **Memory:** 32GB+ RAM

### External Libraries
- `scipy >= 1.10.0` (Pearson correlation, Fisher z-transform)
- `transformers >= 4.30.0` (Llama-2)
- `datasets >= 2.14.0` (TruthfulQA)
- `sentence-transformers >= 2.2.0` (SBERT for semantic similarity)
- `openai >= 1.0.0` (GPT-4 API, optional)
- `numpy >= 1.24.0`, `pandas >= 2.0.0`
- `matplotlib >= 3.7.0`, `seaborn >= 0.12.0`

---

## Validation Strategy

### MECHANISM Gate Validation

```python
def validate_mechanism_gate(result: dict) -> bool:
    """
    Validate MECHANISM gate:
    - Pearson r < -0.2 (negative correlation)
    - p-value < 0.05 (statistical significance)
    - 95% CI upper bound < -0.1 (meaningfully negative)
    """
    r = result["correlation"]
    p = result["p_value"]
    ci_upper = result["ci_95"][1]
    
    gate_passed = (r < -0.2) and (p < 0.05) and (ci_upper < -0.1)
    
    return gate_passed
```

### Secondary Validation
- **Effect Size:** |r| > 0.2 (moderate effect strength)
- **Sample Size:** n = 817 (sufficient power)
- **Quadrant Analysis:** High-fairness-low-reliability region populated

---

## Risk Mitigation

### Weak or No Negative Correlation
- **Strategy:** SHOULD_WORK gate allows pivot to independence hypothesis
- **Fallback:** Stratified analysis (social vs. non-social content)

### API Rate Limits
- **Strategy:** Exponential backoff, checkpoint/resume
- **Fallback:** Use heuristic reliability scoring (exact match with ground truth)

### High Compute Load (5× Inference)
- **Strategy:** Batch inference, FP16 precision, response caching
- **Fallback:** Sample subset of prompts (minimum 500 for statistical power)

### Memory Constraints
- **Strategy:** Sequential processing, clear GPU cache between batches
- **Fallback:** Reduce batch size, use CPU offloading

---

## Expected Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Dataset Loading (C-1) | 0.5 days | TruthfulQA access |
| Response Generation (C-2) | 0.5 days | C-1, GPU access |
| Reliability Scoring (C-3) | 1 day | C-2, OpenAI API |
| Fairness Scoring (C-4) | 2 days | C-2, GPU (5× inference) |
| Correlation Analysis (C-5) | 0.5 days | C-3, C-4 |
| Gate Validation (C-6) | 0.5 days | C-5 |
| Visualization (C-7) | 0.5 days | C-6 |
| Results Management (C-8) | 0.5 days | C-7 |

**Total:** 4 days (sequential execution)

**Critical Path:** C-1 → C-2 → C-4 → C-5 → C-6 → C-7 → C-8

**Parallel Opportunities:** C-3 and C-4 can run in parallel after C-2

---

## Success Criteria

### Primary (MECHANISM Gate)
- **Pearson r < -0.2** (negative correlation detected)
- **p-value < 0.05** (two-tailed test)
- **95% CI upper bound < -0.1**

### Secondary
- Quadrant analysis shows high-fairness-low-reliability region
- Effect size |r| > 0.2 (moderate strength)
- Sample size n = 817 (full dataset)

### Deliverables
- `correlation_results.json` with r, p_value, ci_95, n
- 4 publication-quality figures including mandatory gate comparison
- Validation report with gate evaluation (PASS/PARTIAL/FAIL)

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)

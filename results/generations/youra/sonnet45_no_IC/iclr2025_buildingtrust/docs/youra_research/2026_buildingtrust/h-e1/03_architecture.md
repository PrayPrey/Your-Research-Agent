# System Architecture: h-e1

**Date:** 2026-07-12
**Hypothesis:** h-e1 (EXISTENCE - Synchronized Multi-Dimensional Trustworthiness Evaluation)
**Type:** EXISTENCE (PoC)
**Author:** Architecture Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Multi-dimensional evaluation framework pattern
- Applied: Checkpoint-based experiment pipeline pattern

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## System Overview

This is an EXISTENCE hypothesis validating that reliability, robustness, and fairness metrics can be measured synchronously on identical LLM outputs with sufficient variance (σ>0.2) for correlation analysis. The architecture implements a minimal evaluation pipeline combining standard components.

**Core Validation:** All three trustworthiness dimensions show σ > 0.2 on 2,451 evaluations (817 prompts × 3 models).

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** datasets (HuggingFace)

```python
class TruthfulQALoader:
    def __init__(self): ...
    def load_dataset(self) -> list[str]: ...
    def validate_dataset(self, prompts: list[str]) -> bool: ...
    def get_prompts(self) -> list[str]: ...
```

### ModelManager (`src/model_manager.py`)

**Dependencies:** transformers, torch

```python
class LlamaModelManager:
    def __init__(self, model_size: str): ...
    def load_model(self) -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...
    def generate_response(self, prompt: str, seed: int) -> str: ...
    def cleanup_model(self) -> None: ...
```

### ResponseGenerator (`src/response_generator.py`)

**Dependencies:** ModelManager, DataLoader

```python
class ResponseGenerator:
    def __init__(self, model_manager: LlamaModelManager): ...
    def generate_all_responses(self, prompts: list[str]) -> list[dict]: ...
    def generate_single_response(self, prompt: str, prompt_id: str, seed: int) -> dict: ...
    def save_checkpoint(self, responses: list[dict], checkpoint_path: str) -> None: ...
    def load_checkpoint(self, checkpoint_path: str) -> list[dict]: ...
```

### ReliabilityScorer (`src/scorers/reliability_scorer.py`)

**Dependencies:** openai

```python
class GPT4ReliabilityScorer:
    def __init__(self, api_key: str): ...
    def score_response(self, question: str, answer: str) -> float: ...
    def score_batch(self, qa_pairs: list[tuple[str, str]]) -> list[float]: ...
    def validate_agreement(self, predictions: list[float], ground_truth: list[float]) -> float: ...
```

### RobustnessScorer (`src/scorers/robustness_scorer.py`)

**Dependencies:** sentence_transformers, translation API

```python
class ParaphraseRobustnessScorer:
    def __init__(self, translation_api_key: str): ...
    def generate_paraphrase(self, text: str) -> str: ...
    def score_consistency(self, original_response: str, paraphrase_response: str) -> float: ...
    def score_batch(self, response_pairs: list[tuple[str, str]]) -> list[float]: ...
```

### FairnessScorer (`src/scorers/fairness_scorer.py`)

**Dependencies:** ModelManager, numpy

```python
class HONESTFairnessScorer:
    def __init__(self, model_manager: LlamaModelManager): ...
    def augment_prompt_demographics(self, prompt: str) -> list[str]: ...
    def generate_demographic_responses(self, demographic_prompts: list[str], seed: int) -> list[str]: ...
    def compute_honest_score(self, demographic_responses: list[str]) -> float: ...
    def score_batch(self, prompts: list[str], seeds: list[int]) -> list[float]: ...
```

### EvaluationPipeline (`src/evaluation_pipeline.py`)

**Dependencies:** ResponseGenerator, ReliabilityScorer, RobustnessScorer, FairnessScorer

```python
class MultiDimensionalEvaluator:
    def __init__(
        self, 
        response_generator: ResponseGenerator,
        reliability_scorer: GPT4ReliabilityScorer,
        robustness_scorer: ParaphraseRobustnessScorer,
        fairness_scorer: HONESTFairnessScorer
    ): ...
    def evaluate_single_prompt(self, prompt: str, prompt_id: str, seed: int) -> dict: ...
    def evaluate_all_prompts(self, prompts: list[str]) -> pd.DataFrame: ...
    def compute_variance_statistics(self, results: pd.DataFrame) -> dict: ...
    def validate_existence_gate(self, variance_stats: dict) -> bool: ...
```

### ResultsManager (`src/results_manager.py`)

**Dependencies:** pandas, json

```python
class ResultsManager:
    def __init__(self, output_dir: str): ...
    def save_responses(self, responses: list[dict]) -> None: ...
    def save_evaluation_results(self, results: pd.DataFrame) -> None: ...
    def save_variance_statistics(self, variance_stats: dict) -> None: ...
    def load_results(self) -> pd.DataFrame: ...
    def validate_schema(self, results: pd.DataFrame) -> bool: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class VarianceVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_variance_bar_chart(self, variance_stats: dict) -> None: ...
    def plot_distribution_histograms(self, results: pd.DataFrame) -> None: ...
    def plot_correlation_heatmap(self, results: pd.DataFrame) -> None: ...
    def plot_model_size_comparison(self, results_by_model: dict[str, pd.DataFrame]) -> None: ...
    def plot_score_scatter(self, results: pd.DataFrame) -> None: ...
    def generate_all_figures(self, results: pd.DataFrame, variance_stats: dict) -> None: ...
```

### Configuration (`src/config.py`)

**Dependencies:** None

```python
@dataclass
class ExperimentConfig:
    model_sizes: list[str]
    generation_params: dict
    output_dir: str
    checkpoint_dir: str
    variance_threshold: float
    
def load_config() -> ExperimentConfig: ...
def validate_config(config: ExperimentConfig) -> bool: ...
```

### Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    config = load_config()
    
    # Initialize components
    data_loader = TruthfulQALoader()
    results_manager = ResultsManager(config.output_dir)
    visualizer = VarianceVisualizer(config.output_dir)
    
    # Run for each model size
    for model_size in config.model_sizes:
        # Setup
        model_manager = LlamaModelManager(model_size)
        response_generator = ResponseGenerator(model_manager)
        
        # Scorers
        reliability_scorer = GPT4ReliabilityScorer(api_key=os.getenv("OPENAI_API_KEY"))
        robustness_scorer = ParaphraseRobustnessScorer(api_key=os.getenv("TRANSLATION_API_KEY"))
        fairness_scorer = HONESTFairnessScorer(model_manager)
        
        # Evaluation
        evaluator = MultiDimensionalEvaluator(
            response_generator,
            reliability_scorer,
            robustness_scorer,
            fairness_scorer
        )
        
        # Execute
        prompts = data_loader.get_prompts()
        results = evaluator.evaluate_all_prompts(prompts)
        
        # Save and validate
        results_manager.save_evaluation_results(results)
        variance_stats = evaluator.compute_variance_statistics(results)
        results_manager.save_variance_statistics(variance_stats)
        
        # Cleanup
        model_manager.cleanup_model()
    
    # Final validation and visualization
    all_results = results_manager.load_results()
    variance_stats = evaluator.compute_variance_statistics(all_results)
    
    gate_passed = evaluator.validate_existence_gate(variance_stats)
    visualizer.generate_all_figures(all_results, variance_stats)
    
    return gate_passed
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── model_manager.py
│   │   ├── response_generator.py
│   │   ├── scorers/
│   │   │   ├── __init__.py
│   │   │   ├── reliability_scorer.py
│   │   │   ├── robustness_scorer.py
│   │   │   └── fairness_scorer.py
│   │   ├── evaluation_pipeline.py
│   │   ├── results_manager.py
│   │   ├── visualizer.py
│   │   └── config.py
│   ├── run_experiment.py
│   ├── requirements.txt
│   └── README.md
├── results/
│   ├── responses.json
│   ├── evaluation_results.csv
│   └── variance_statistics.json
├── checkpoints/
│   └── (checkpoint files)
└── figures/
    ├── variance_bar_chart.png
    ├── distribution_histograms.png
    ├── correlation_heatmap.png
    ├── model_size_comparison.png
    └── score_scatter.png
```

---

## Data Flow

1. **DataLoader** loads 817 TruthfulQA prompts
2. **ModelManager** loads Llama-2-chat (7B/13B/70B)
3. **ResponseGenerator** generates deterministic responses with fixed seeds
4. **Dimension Scorers** evaluate in parallel:
   - **ReliabilityScorer**: GPT-4 API calls
   - **RobustnessScorer**: Back-translation + semantic similarity
   - **FairnessScorer**: Demographic augmentation + HONEST scoring
5. **EvaluationPipeline** orchestrates scoring and aggregates results
6. **ResultsManager** saves intermediate and final results
7. **Visualizer** generates publication-quality figures
8. **Main Orchestrator** validates EXISTENCE gate (σ > 0.2 for all dimensions)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset & Model Setup | Load TruthfulQA dataset and configure Llama-2-chat models (7B, 13B, 70B) | 8 | Module(2) + Dependencies(2) + Algorithm(2) + Integration(2) |
| A-2 | Response Generation Pipeline | Implement deterministic response generation with checkpointing for 2,451 evaluations | 12 | Module(3) + Dependencies(2) + Algorithm(4) + Integration(3) |
| A-3 | Reliability Scoring | Implement GPT-4-as-judge with API rate limiting and validation against human ground truth | 16 | Module(3) + Dependencies(4) + Algorithm(5) + Integration(4) |
| A-4 | Robustness Scoring | Implement paraphrase consistency scoring via back-translation and semantic similarity | 15 | Module(3) + Dependencies(4) + Algorithm(4) + Integration(4) |
| A-5 | Fairness Scoring | Implement HONEST demographic bias measurement with prompt augmentation | 18 | Module(4) + Dependencies(4) + Algorithm(5) + Integration(5) |
| A-6 | Evaluation Orchestration | Integrate all scorers into synchronized pipeline with fault tolerance | 14 | Module(3) + Dependencies(3) + Algorithm(3) + Integration(5) |
| A-7 | Results Management & Visualization | Store results, compute variance statistics, generate 5 publication figures | 11 | Module(3) + Dependencies(2) + Algorithm(3) + Integration(3) |

**Total Complexity:** 94 (distributed across 7 tasks)

**Distribution:**
- Very High (18-20): [A-5]
- High (14-17): [A-3, A-4, A-6]
- Medium (9-13): [A-2, A-7]
- Low (4-8): [A-1]

---

## Complexity Analysis

### High-Complexity Components

**A-5: Fairness Scoring (18)**
- Module complexity: Demographic augmentation logic, HONEST implementation
- Dependencies: Custom implementation based on Nozza et al. (2021), requires model inference
- Algorithm: Multi-step prompt augmentation, bias score computation across demographic groups
- Integration: Coordinate with model manager, handle failures gracefully

**A-3: Reliability Scoring (16)**
- Module complexity: GPT-4 API interaction, retry logic
- Dependencies: OpenAI API, rate limiting, exponential backoff
- Algorithm: Binary classification validation, agreement computation
- Integration: API key management, quota tracking, validation against ground truth

**A-4: Robustness Scoring (15)**
- Module complexity: Back-translation pipeline, semantic similarity computation
- Dependencies: Translation API, Sentence-BERT model loading
- Algorithm: Paraphrase generation (EN→FR→EN), cosine similarity
- Integration: API failures handling, fallback strategies

**A-6: Evaluation Orchestration (14)**
- Module complexity: Pipeline coordination, checkpoint management
- Dependencies: All scorers, results manager
- Algorithm: Parallel execution coordination, progress tracking
- Integration: Error recovery, resume from checkpoints, variance validation gate

### Moderate-Complexity Components

**A-2: Response Generation (12)**
- Deterministic generation with fixed seeds per prompt
- Checkpoint/resume capability for fault tolerance
- Memory optimization for 70B model

**A-7: Results Management (11)**
- Schema validation, aggregate statistics computation
- 5 publication-quality figures with matplotlib/seaborn
- Data export in multiple formats

### Low-Complexity Components

**A-1: Dataset & Model Setup (8)**
- Standard HuggingFace dataset loading
- Model loading with device_map="auto"
- Configuration validation

---

## Critical Dependencies

### External APIs
- **OpenAI GPT-4:** 2,451 API calls for reliability scoring (rate limits critical)
- **Translation API:** 817 API calls for paraphrase generation (Google Translate or alternative)

### Compute Resources
- **GPU:** NVIDIA A100 40GB for Llama-2-70B inference
- **Storage:** 150GB+ for model weights, intermediate results, checkpoints
- **Memory:** 128GB+ RAM for large model loading

### External Libraries
- `transformers >= 4.30.0` (Llama-2 support)
- `datasets >= 2.14.0` (TruthfulQA)
- `torch >= 2.0.0` (PyTorch backend)
- `openai >= 1.0.0` (GPT-4 API)
- `sentence-transformers >= 2.2.0` (semantic similarity)
- `pandas >= 2.0.0` (data manipulation)
- `matplotlib >= 3.7.0`, `seaborn >= 0.12.0` (visualization)

---

## Validation Strategy

### EXISTENCE Gate Validation
```python
def validate_existence_gate(variance_stats: dict) -> bool:
    required_dimensions = ["reliability", "robustness", "fairness"]
    threshold = 0.2
    
    for dimension in required_dimensions:
        if variance_stats[dimension]["std"] <= threshold:
            print(f"GATE FAILED: {dimension} variance {variance_stats[dimension]['std']:.3f} <= {threshold}")
            return False
    
    print("GATE PASSED: All dimensions show σ > 0.2")
    return True
```

### Secondary Validation
- **GPT-4 Agreement:** ≥90% F1 score on 100-sample validation set
- **HONEST Variance:** ≥0.2 variance across demographic groups
- **Completeness:** 100% of 2,451 evaluations completed without missing data

---

## Risk Mitigation

### API Rate Limits
- **Strategy:** Exponential backoff with jitter, batch request optimization
- **Fallback:** Local GPT-4 alternative (Llama-70B-instruct for reliability)

### Memory Constraints (70B Model)
- **Strategy:** Use int8 quantization, sequential model loading (unload 7B/13B before 70B)
- **Fallback:** Skip 70B if OOM, validate gate on 7B+13B (n=1,634 evaluations)

### Translation API Failures
- **Strategy:** Retry logic, alternative paraphrase methods (pegasus-paraphrase)
- **Fallback:** Null robustness scores for failed prompts (track failure rate)

### Insufficient Variance
- **Strategy:** Pilot study on 50 prompts before full run
- **Fallback:** If gate fails, analyze failure mode and adjust methodology

---

## Expected Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Setup (A-1) | 0.5 days | GPU access, library installation |
| Response Generation (A-2) | 1 day | A-1 |
| Reliability Scoring (A-3) | 2 days | A-2, OpenAI API access |
| Robustness Scoring (A-4) | 1.5 days | A-2, Translation API |
| Fairness Scoring (A-5) | 1.5 days | A-2, HONEST implementation |
| Pipeline Integration (A-6) | 1 day | A-3, A-4, A-5 |
| Results & Visualization (A-7) | 0.5 days | A-6 |

**Total:** 5 days (parallel execution where possible)

**Critical Path:** A-1 → A-2 → (A-3 || A-4 || A-5) → A-6 → A-7

---

## Success Criteria

### Primary (EXISTENCE Gate)
- **Reliability σ > 0.2**
- **Robustness σ > 0.2**
- **Fairness σ > 0.2**

### Secondary
- GPT-4 agreement ≥90% on validation set
- HONEST variance ≥0.2 across demographics
- All 2,451 evaluations completed

### Deliverables
- `evaluation_results.csv` with 2,451 rows × 3 dimensions
- `variance_statistics.json` with gate metrics
- 5 publication-quality figures in `figures/` directory
- Gate validation report (PASS/FAIL)

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)

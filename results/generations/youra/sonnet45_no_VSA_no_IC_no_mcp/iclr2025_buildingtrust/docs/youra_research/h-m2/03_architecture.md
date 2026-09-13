# System Architecture: h-m2

**Hypothesis:** h-m2  
**Type:** MECHANISM  
**Gate:** MUST_WORK (≥20pp difference OR ≥50% relative improvement, replicated across both models)  
**Date:** 2026-08-24  

Applied: RAG pipeline pattern, dual-model evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-m1 actual implementation  
**Analyzed Path**: `docs/youra_research/h-m1/code/`  
**Findings**: h-m1 outputs classification_results.json with threshold 0.32. Reuse data loading pattern, config structure, experiment runner pattern.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Data Source | File Location |
|--------|-------------|---------------|
| Classifier Results | `classification_results.json` | `docs/youra_research/h-m1/code/results/classification_results.json` |
| Entity-Error Cases | Filter from h-e1 data | `docs/youra_research/h-e1/code/results/entropy_results.json` |

**Verified from**: h-m1 actual implementation (threshold 0.32 validated)

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies**: None

```python
class DataLoader:
    def load_entity_error_cases(self, h_e1_path: str, threshold: float) -> list[dict]: ...
    def select_per_model_samples(self, cases: list[dict], n_per_model: int) -> tuple[list, list]: ...
```

### RAGPipeline (`src/rag_pipeline.py`)

**Dependencies**: spacy, wikipedia, transformers

```python
class RAGPipeline:
    def __init__(self, model_name: str): ...
    def extract_entities(self, question: str) -> list[str]: ...
    def retrieve_wikipedia(self, entities: list[str], top_k: int = 3) -> list[str]: ...
    def correct(self, question: str, incorrect_answer: str) -> str: ...
```

### COTBaseline (`src/cot_baseline.py`)

**Dependencies**: transformers

```python
class COTBaseline:
    def __init__(self, model_name: str): ...
    def correct(self, question: str, incorrect_answer: str) -> str: ...
```

### DualModelRunner (`src/dual_model_runner.py`)

**Dependencies**: RAGPipeline, COTBaseline

```python
class DualModelRunner:
    def __init__(self, gpt_api_key: str, use_llama: bool = True): ...
    def run_gpt35(self, cases: list[dict], method: str) -> list[dict]: ...
    def run_llama2(self, cases: list[dict], method: str) -> list[dict]: ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies**: None

```python
class Evaluator:
    def evaluate_correction(self, corrected: str, gold: str) -> float: ...
    def compute_success_rate(self, results: list[dict]) -> float: ...
    def check_gate(self, matched_rate: float, mismatched_rate: float) -> dict: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies**: matplotlib

```python
def plot_gate_metrics(gpt_results: dict, llama_results: dict, save_path: str): ...
def plot_success_comparison(gpt_results: dict, llama_results: dict, save_path: str): ...
def plot_per_model_breakdown(gpt_results: dict, llama_results: dict, save_path: str): ...
def plot_outcome_distribution(all_results: dict, save_path: str): ...
```

### Config (`config.py`)

**Dependencies**: None

```python
CONFIG = {
    "data": {...},
    "models": {...},
    "rag": {...},
    "cot": {...},
    "evaluation": {...},
    "output": {...},
    "seed": 42
}
```

### ExperimentRunner (`src/run_experiment.py`)

**Dependencies**: DataLoader, DualModelRunner, Evaluator, Visualizer

```python
class CorrectionExperiment:
    def __init__(self): ...
    def load_data(self) -> tuple: ...
    def run_corrections(self) -> dict: ...
    def evaluate_all(self) -> dict: ...
    def run(self) -> dict: ...
```

---

## File Organization

```
h-m2/code/
├── config.py                    # Configuration
├── src/
│   ├── data_loader.py          # Load h-m1 entity-error cases
│   ├── rag_pipeline.py         # RAG correction (Wikipedia + LLM)
│   ├── cot_baseline.py         # COT correction baseline
│   ├── dual_model_runner.py   # GPT-3.5 + Llama-2-7B runners
│   ├── evaluator.py            # Success rate + gate check
│   ├── visualizer.py           # 4 plots
│   └── run_experiment.py       # Main runner
├── results/
│   └── correction_results.json
└── figures/
    ├── gate_metrics_comparison.png
    ├── success_rate_comparison.png
    ├── per_model_breakdown.png
    └── correction_outcomes.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Data Loading | Load entity-error cases from h-e1, filter by h-m1 threshold, select 50 per model | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| M2-2 | RAG Pipeline | Entity extraction (spaCy) + Wikipedia retrieval + context augmentation | 14 | Module(4) + Deps(3) + Algo(4) + Integ(3) |
| M2-3 | COT Baseline | Chain-of-thought prompting for both models | 6 | Module(2) + Deps(1) + Algo(2) + Integ(1) |
| M2-4 | GPT-3.5 Runner | OpenAI API integration for both RAG and COT | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| M2-5 | Llama-2-7B Runner | HuggingFace integration for both RAG and COT | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| M2-6 | Evaluation | Success rate calculation + GPT-judge semantic equivalence | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| M2-7 | Gate Check | Verify ≥20pp OR ≥50% improvement for BOTH models | 5 | Module(1) + Deps(1) + Algo(2) + Integ(1) |
| M2-8 | Visualizations | 4 plots: gate metrics, success comparison, per-model, outcomes | 12 | Module(3) + Deps(1) + Algo(4) + Integ(4) |
| M2-9 | Results Reporting | Save JSON with per-sample outcomes + gate status | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M2-2], Medium(9-13): [M2-5, M2-6, M2-8], Low(4-8): [M2-1, M2-3, M2-4, M2-7, M2-9]

---

## Data Flow

1. Load h-e1 entropy_results.json → filter entropy < 0.32 (h-m1 threshold)
2. Select 50 entity-error cases for GPT-3.5, 50 for Llama-2-7B
3. Run matched condition: entity-error → RAG correction
4. Run mismatched condition: entity-error → COT correction
5. Evaluate both conditions: success rate (exact match + GPT-judge)
6. Gate check per model: (matched - mismatched) ≥ 20pp OR relative ≥ 50%
7. Verify BOTH models pass gate
8. Save results + 4 figures

---

## Configuration Schema

```python
CONFIG = {
    "data": {
        "h_e1_results_path": "../h-e1/code/results/entropy_results.json",
        "h_m1_threshold": 0.32,  # From h-m1 validation
        "n_samples_per_model": 50
    },
    "models": {
        "gpt35": {
            "name": "gpt-3.5-turbo",
            "api_key_env": "OPENAI_API_KEY",
            "temperature": 0.7,
            "max_tokens": 150
        },
        "llama2": {
            "name": "meta-llama/Llama-2-7b-chat-hf",
            "temperature": 0.7,
            "max_tokens": 150,
            "load_in_4bit": True  # Memory optimization
        }
    },
    "rag": {
        "spacy_model": "en_core_web_sm",
        "top_k_docs": 3,
        "retrieval_method": "wikipedia_api"
    },
    "cot": {
        "prompt_template": "Question: {question}\nIncorrect answer: {incorrect_answer}\n\nLet's think step by step to find the correct answer:"
    },
    "evaluation": {
        "gate_threshold_pp": 20.0,  # Percentage points
        "gate_threshold_rel": 50.0,  # Relative improvement %
        "use_gpt_judge": True,
        "gpt_judge_model": "gpt-3.5-turbo"
    },
    "output": {
        "results_file": "./results/correction_results.json",
        "figures_dir": "./figures/"
    },
    "seed": 42
}
```

---

## Key Interfaces

### DataLoader.load_entity_error_cases
```python
def load_entity_error_cases(self, h_e1_path: str, threshold: float) -> list[dict]:
    """
    Load entity-error cases from h-e1 outputs.
    
    Returns:
        list[dict]: [
            {
                "question": str,
                "incorrect_answer": str,
                "gold_answer": str,
                "entropy": float,
                "model": str  # "gpt-3.5-turbo" or "llama-2-7b"
            }
        ]
    """
```

### RAGPipeline.correct
```python
def correct(self, question: str, incorrect_answer: str) -> str:
    """
    RAG-based correction:
    1. Extract entities from question (spaCy NER)
    2. Retrieve Wikipedia summaries (top-k=3)
    3. Build context-augmented prompt
    4. Generate corrected answer
    
    Returns:
        corrected_answer: str
    """
```

### Evaluator.check_gate
```python
def check_gate(self, matched_rate: float, mismatched_rate: float) -> dict:
    """
    MUST_WORK gate evaluation.
    
    Returns:
        {
            "matched_rate": float,
            "mismatched_rate": float,
            "difference": float,  # matched - mismatched
            "relative_improvement": float,  # % improvement
            "gate_pass": bool  # True if ≥20pp OR ≥50% relative
        }
    """
```

---

## Integration Points

1. **h-e1 → h-m2**: Read `entropy_results.json` (entity-error cases)
2. **h-m1 → h-m2**: Use threshold 0.32 for entity-error classification
3. **OpenAI API**: GPT-3.5-turbo for corrections + GPT-judge evaluation
4. **HuggingFace**: Llama-2-7B-chat for corrections
5. **Wikipedia API**: Entity-focused document retrieval
6. **spaCy**: NER for entity extraction (`en_core_web_sm`)
7. **matplotlib**: 4 visualization functions

---

## Error Handling

### Wikipedia API Rate Limiting
```python
# Retry logic with exponential backoff
import time
from functools import wraps

def retry_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    time.sleep(2 ** i)
            return None
        return wrapper
    return decorator
```

### Entity Extraction Failures
```python
# Fallback to keyword-based retrieval
def extract_entities(self, question: str) -> list[str]:
    doc = self.nlp(question)
    entities = [ent.text for ent in doc.ents]
    
    # Fallback: extract nouns if no entities found
    if not entities:
        entities = [token.text for token in doc if token.pos_ == "NOUN"][:3]
    
    return entities
```

### API Failures
```python
# Skip sample if API fails after retries
def run_with_error_handling(self, cases: list[dict]) -> list[dict]:
    results = []
    for case in cases:
        try:
            corrected = self.correct(case["question"], case["incorrect_answer"])
            results.append({**case, "corrected": corrected, "error": None})
        except Exception as e:
            results.append({**case, "corrected": "", "error": str(e)})
    return results
```

---

## Success Criteria

1. Code runs without errors
2. 100 entity-error cases loaded (50 per model)
3. Both RAG and COT corrections execute for both models
4. GPT-3.5: (matched - mismatched) ≥ 20pp OR relative ≥ 50% → GATE PASS
5. Llama-2-7B: (matched - mismatched) ≥ 20pp OR relative ≥ 50% → GATE PASS
6. **BOTH models must pass gate**
7. 4 figures generated
8. JSON results saved with per-sample outcomes

---

## Dependencies

**Python Libraries**:
- openai (GPT-3.5 API)
- transformers (Llama-2-7B)
- spacy (NER)
- wikipedia-api (Wikipedia retrieval)
- matplotlib (Visualization)
- numpy (Metrics)
- scikit-learn (Optional: statistical tests)
- bitsandbytes (Llama-2 4-bit quantization)

**External Resources**:
- OpenAI API key
- HuggingFace access token (for gated Llama-2 model)
- Wikipedia API access
- spaCy model: `python -m spacy download en_core_web_sm`

**External Data**:
- h-e1 validation outputs (VALIDATED prerequisite)
- h-m1 classification results (VALIDATED prerequisite, threshold 0.32)

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation

# Architecture Design: h-e1

**Date:** 2026-08-24  
**Hypothesis:** Entity-substitution errors exhibit significantly lower attention entropy  
**Type:** EXISTENCE (inference-only, no training)  
**Complexity:** Tier 1

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A

---

## System Overview

Inference pipeline: Load model → Extract attention → Calculate entropy → Compare distributions → Report pass/fail

---

## Module Structure

### 1. AttentionExtractor (`src/attention_extractor.py`)

**Dependencies:** transformers, torch

```python
class AttentionExtractor:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-hf"): ...
    def extract_last_layer_attention(self, question: str) -> torch.Tensor: ...
    def get_entity_attention_slice(self, attention: torch.Tensor, 
                                   entity_span: tuple[int, int]) -> torch.Tensor: ...
    def char_span_to_tokens(self, text: str, char_span: tuple[int, int]) -> tuple[int, int]: ...
```

### 2. EntropyCalculator (`src/entropy_calculator.py`)

**Dependencies:** torch, numpy

```python
class EntropyCalculator:
    @staticmethod
    def calculate_entropy(attention_weights: torch.Tensor) -> float: ...
    @staticmethod
    def entropy_over_span(attention: torch.Tensor, span_tokens: tuple[int, int]) -> float: ...
```

### 3. StatisticalComparator (`src/statistical_comparator.py`)

**Dependencies:** scipy, numpy

```python
class StatisticalComparator:
    @staticmethod
    def compare_distributions(entity_entropies: list[float], 
                             non_entity_entropies: list[float]) -> dict: ...
    @staticmethod
    def cohen_d(group1: list[float], group2: list[float]) -> float: ...
```

### 4. DataLoader (`src/data_loader.py`)

**Dependencies:** json, spacy

```python
class TruthfulQALoader:
    def __init__(self, data_path: str, ner_model: str = "en_core_web_lg"): ...
    def load_samples(self) -> list[dict]: ...
    def get_entity_span(self, question: str) -> tuple[int, int]: ...
```

### 5. ExperimentRunner (`src/run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # Load data
    # Extract entropy for all samples
    # Run statistical test
    # Generate report
    pass

if __name__ == "__main__":
    main()
```

### 6. Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
def plot_violin(entity_entropies: list[float], 
               non_entity_entropies: list[float], 
               p_value: float, 
               save_path: str): ...

def plot_histograms(entity_entropies: list[float], 
                   non_entity_entropies: list[float], 
                   save_path: str): ...
```

---

## Data Flow

```
TruthfulQA JSON → DataLoader → (question, entity_span, error_type)
                                         ↓
                              AttentionExtractor.extract_last_layer_attention()
                                         ↓
                              attention [seq_len, seq_len]
                                         ↓
                              EntropyCalculator.entropy_over_span()
                                         ↓
                              entropy (float)
                                         ↓
                     Aggregate by error_type → two lists
                                         ↓
                     StatisticalComparator.compare_distributions()
                                         ↓
                     {p_value, means, cohen_d, pass/fail}
                                         ↓
                     Visualizer + Report Generator → 04_validation.md
```

---

## File Structure

```
h-e1/
├── src/
│   ├── attention_extractor.py
│   ├── entropy_calculator.py
│   ├── statistical_comparator.py
│   ├── data_loader.py
│   ├── visualizer.py
│   └── run_experiment.py
├── data/
│   └── truthfulqa_entity_subset.json
├── figures/
│   ├── entropy_violin.png
│   └── entropy_histograms.png
└── results/
    ├── entropy_scores.csv
    └── statistical_results.json
```

---

## Error Handling

| Module | Error | Action |
|--------|-------|--------|
| AttentionExtractor | char_to_token returns None | Skip sample, log warning |
| EntropyCalculator | Zero attention sum | Add 1e-10 smoothing |
| DataLoader | Missing entity span | Skip sample, log count |
| ExperimentRunner | Model load fails | Exit with error message |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data Loading | Load TruthfulQA subset, NER entity spans | 6 | setup(1) + load(2) + validate(3) |
| E2 | Attention Extraction | Load Llama-2, extract last-layer attention | 8 | model_load(3) + extract(3) + span_map(2) |
| E3 | Entropy Calculation | Compute entropy over entity spans | 5 | formula(2) + span_avg(2) + edge_cases(1) |
| E4 | Statistical Test | t-test + Cohen's d + pass/fail | 6 | t_test(2) + effect_size(2) + logic(2) |
| E5 | Visualization | Violin plot + histograms | 5 | violin(3) + histogram(2) |
| E6 | Report Generation | Generate 04_validation.md + CSV/JSON | 4 | template(2) + write(2) |

**Distribution:**  
- High (14-17): []  
- Medium (9-13): []  
- Low (4-8): [E1, E2, E3, E4, E5, E6]

**Total:** 34 complexity points (6 tasks)

---

## Configuration

**config.py:**

```python
MODEL_NAME = "meta-llama/Llama-2-7b-hf"
NER_MODEL = "en_core_web_lg"
DATA_PATH = "./data/truthfulqa_entity_subset.json"
FIGURES_DIR = "./figures/"
RESULTS_DIR = "./results/"
SEED = 42
ALPHA = 0.05  # significance threshold
SMOOTHING = 1e-10  # for log(0) edge case
```

---

## Validation Criteria

**Pass Condition:**  
`(p_value < 0.05) AND (mean_entity_entropy < mean_non_entity_entropy)`

**Expected Values:**
- Entity-error entropy: 0.3-0.5
- Non-entity-error entropy: 0.6-0.8
- Cohen's d: 0.5-1.0

**Fail Handling:**  
If gate fails, document in 04_validation.md, block h-m1/h-m2

---

## Dependencies

**Python Packages:**
- transformers >= 4.30
- torch >= 2.0
- spacy >= 3.5
- scipy >= 1.10
- matplotlib >= 3.5
- numpy >= 1.24

**External Models:**
- Llama-2-7B (HuggingFace)
- spaCy en_core_web_lg

**Upstream Artifacts:**
- h-c1/data/truthfulqa_entity_subset.json (entity-annotated dataset)

---

**Skipped:**  
- Training pipeline (inference only)
- Multi-model comparison (Llama-2 only)
- Multi-layer analysis (last layer only)
- Per-head entropy (averaged)

**Add when:**  
- h-m1 needs training → expand to training.py
- Need multi-model → add model loop in run_experiment.py

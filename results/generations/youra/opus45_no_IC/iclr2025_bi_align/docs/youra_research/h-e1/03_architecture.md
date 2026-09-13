# Architecture: H-E1 (Accommodation Patterns Detectable in LMSYS-Chat-1M)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT

Applied: DeBERTa formality scoring pipeline (HuggingFace Transformers); statistical comparison with shuffled baseline per 02c_experiment_brief.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No base hypothesis, no existing `src/`.

---

## Module Structure

### config.py (`h-e1/code/config.py`)

```python
DATASET_NAME = "lmsys/lmsys-chat-1m"
MODEL_NAME = "s-nlp/deberta-large-formality-ranker"
MIN_TURNS_PER_SIDE = 2
COVERAGE_TARGET = 0.50
COHENS_D_TARGET = 0.30
P_VALUE_THRESHOLD = 0.001
BATCH_SIZE = 32
SEED = 42
DEVICE = "cuda"  # or "cpu"
```

### data.py (`h-e1/code/data.py`)

**Dependencies:** config.py

```python
def load_dataset_lmsys() -> Dataset: ...
def filter_by_turns(dataset: Dataset, min_turns: int = 2) -> Dataset: ...
def filter_english(dataset: Dataset) -> Dataset: ...
def filter_not_redacted(dataset: Dataset) -> Dataset: ...
def extract_turn_pairs(conversation: list[dict]) -> list[tuple[str, str]]: ...
```

### formality.py (`h-e1/code/formality.py`)

**Dependencies:** config.py, torch, transformers

```python
class FormalityAccommodationAnalyzer:
    def __init__(self, model_name: str = "s-nlp/deberta-large-formality-ranker", device: str = "cuda"): ...
    def score_formality(self, text: str) -> float: ...
    def score_batch(self, texts: list[str]) -> list[float]: ...
    def compute_accommodation_delta(self, human_text: str, ai_text: str) -> float: ...
    def analyze_conversation(self, conversation: list[dict]) -> dict: ...
```

### baseline.py (`h-e1/code/baseline.py`)

**Dependencies:** numpy

```python
def create_shuffled_baseline(human_formality: np.ndarray, ai_formality: np.ndarray, seed: int = 42) -> tuple[np.ndarray, np.ndarray]: ...
def compute_shuffled_deltas(human_formality: np.ndarray, shuffled_ai: np.ndarray) -> np.ndarray: ...
```

### analysis.py (`h-e1/code/analysis.py`)

**Dependencies:** scipy, numpy

```python
def compute_cohens_d(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray) -> float: ...
def compute_welch_ttest(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray) -> tuple[float, float]: ...
def check_gate(coverage: float, cohens_d: float, p_value: float) -> bool: ...
def generate_statistics(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray, coverage: float) -> dict: ...
```

### visualize.py (`h-e1/code/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
def plot_delta_histogram(observed: np.ndarray, shuffled: np.ndarray, save_path: str) -> None: ...
def plot_gate_metrics(stats: dict, save_path: str) -> None: ...
def plot_formality_distributions(human: np.ndarray, ai: np.ndarray, save_path: str) -> None: ...
```

### run_experiment.py (`h-e1/code/run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> dict: ...  # orchestrates load -> filter -> score -> delta -> shuffle -> stats -> figures -> gate result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data loading | Load LMSYS-Chat-1M via HuggingFace datasets | 5 | 2+1+1+1 |
| E2 | Preprocessing/filtering | ≥2 turns filter, English filter, redaction removal | 6 | 2+1+2+1 |
| E3 | Formality scoring | DeBERTa inference pipeline with batch processing | 8 | 2+3+2+1 |
| E4 | Accommodation delta | Compute |AI - Human| formality per turn pair | 4 | 1+2+1 |
| E5 | Shuffled baseline | Random permutation of AI scores, compute shuffled deltas | 4 | 1+2+1 |
| E6 | Statistical analysis | Cohen's d, Welch's t-test, gate check | 5 | 1+2+1+1 |
| E7 | Visualization | Delta histogram overlay, gate metrics bar chart | 5 | 2+1+1+1 |
| E8 | End-to-end run + report | Orchestration script, run on full data, verify gate, save results | 5 | 1+2+1+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [E1, E2, E3, E4, E5, E6, E7, E8]

**Total Complexity:** 42 | **Within Budget:** Yes (LIGHT tier ≤15 epic tasks)

---

## File Organization

```
h-e1/code/
  config.py
  data.py
  formality.py
  baseline.py
  analysis.py
  visualize.py
  run_experiment.py
h-e1/figures/
  delta_histogram.png
  gate_metrics.png
  formality_distributions.png
```

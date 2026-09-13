# Architecture Design: h-e1

**Date:** 2026-08-25
**Hypothesis:** EXISTENCE - Citation classification precision >85%, Feature extraction kappa >0.80
**Type:** PoC (Proof of Concept)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing citation classification code. Building minimal PoC from standard libraries.

---

## Applied Patterns

Applied: Standard NLP pipeline (data collection → annotation → fine-tuning → evaluation)

---

## Module Structure

### DataCollector (`src/data_collector.py`)

**Dependencies:** None

```python
class DataCollector:
    def __init__(self, cache_dir: str = "data/cache"): ...
    def fetch_benchmark_papers(self, max_results: int = 200) -> list: ...
    def filter_by_citations(self, papers: list, min_citations: int = 50) -> list: ...
    def extract_citation_contexts(self, paper_id: str) -> list: ...
    def sample_citations(self, all_contexts: list, n_samples: int, seed: int = 42) -> list: ...
    def save_raw_data(self, data: list, output_path: str): ...
```

### AnnotationTool (`src/annotation_tool.py`)

**Dependencies:** DataCollector

```python
class AnnotationTool:
    def __init__(self, data_path: str): ...
    def label_citation_context(self, context: str) -> int: ...
    def extract_features(self, paper: dict) -> dict: ...
    def save_annotations(self, annotations: list, output_path: str): ...
    def calculate_kappa(self, annotator1_path: str, annotator2_path: str) -> float: ...
```

### CitationClassifier (`src/classifier.py`)

**Dependencies:** None

```python
class CitationClassifier:
    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"): ...
    def prepare_data(self, texts: list, labels: list) -> dict: ...
    def train(self, train_data: dict, val_data: dict, output_dir: str): ...
    def predict(self, text: str) -> tuple: ...
    def load_model(self, model_path: str): ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies:** CitationClassifier

```python
class Evaluator:
    def __init__(self, model_path: str): ...
    def evaluate(self, test_data: dict) -> dict: ...
    def compute_metrics(self, y_true: list, y_pred: list) -> dict: ...
    def save_results(self, metrics: dict, output_path: str): ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** Evaluator

```python
class Visualizer:
    def __init__(self, output_dir: str = "figures"): ...
    def plot_confusion_matrix(self, y_true: list, y_pred: list): ...
    def plot_pr_curve(self, y_true: list, y_scores: list): ...
    def plot_training_metrics(self, metrics_history: dict): ...
    def plot_feature_agreement_heatmap(self, kappa_per_feature: dict): ...
    def plot_context_length_distribution(self, contexts: list): ...
```

---

## Directory Structure

```
h-e1/
├── data/
│   ├── cache/               # API responses
│   ├── raw_citations.json   # Collected citation contexts
│   ├── annotator1.json      # Annotations from annotator 1
│   └── annotator2.json      # Annotations from annotator 2
├── models/
│   └── scibert_citation_classifier/  # Trained model
├── figures/                 # All visualizations (PNG)
├── src/
│   ├── data_collector.py    # API integration
│   ├── annotation_tool.py   # Labeling interface
│   ├── classifier.py        # SciBERT fine-tuning
│   ├── evaluator.py         # Metrics calculation
│   └── visualizer.py        # Plot generation
├── scripts/
│   ├── 1_collect_data.py    # Run data collection
│   ├── 2_annotate.py        # Run annotation interface
│   ├── 3_train.py           # Train classifier
│   ├── 4_evaluate.py        # Compute metrics
│   └── 5_visualize.py       # Generate figures
├── results.json             # Final metrics
└── requirements.txt         # Dependencies
```

---

## Data Flow

1. **Collection**: ArXiv API → Semantic Scholar API → `data/raw_citations.json`
2. **Annotation**: Load raw_citations → Manual labeling → `data/annotator1.json`, `annotator2.json`
3. **Training**: Load annotations → SciBERT fine-tuning → `models/scibert_citation_classifier/`
4. **Evaluation**: Load model + test set → Compute metrics → `results.json`
5. **Visualization**: Load results → Generate 5 figures → `figures/*.png`

---

## Integration Points

### External Dependencies

- **Hugging Face Transformers**: SciBERT loading and fine-tuning
- **sklearn**: Metrics (precision, recall, F1, kappa, confusion matrix)
- **matplotlib/seaborn**: Visualization
- **arxiv**: ArXiv API client
- **semanticscholar**: Semantic Scholar API client

### API Rate Limits

- ArXiv: No strict limit, use `sleep(1)` between requests
- Semantic Scholar: 100 req/5min, implement retry with backoff
- Papers with Code: Cache taxonomy locally (single fetch)

---

## Error Handling Strategy

### API Failures
- Retry with exponential backoff (max 3 retries)
- Cache all successful responses (avoid re-fetching)
- Log failed requests to `data/failed_requests.log`

### Missing Data
- Skip papers with missing citation data
- Record skipped papers in `data/skipped_papers.json`
- Require minimum 100 valid citations (fail if <100)

### Training Failures
- Early stopping if validation loss increases for 2 epochs
- Save checkpoint every epoch (recover from failures)
- Monitor GPU memory (reduce batch size if OOM)

---

## Testing Approach

### Data Validation
- Assert citation contexts have ≥3 sentences
- Verify label distribution (expect 20-40% validation claims)
- Check for duplicate citations (remove if found)

### Metric Correctness
- Unit test precision/recall/F1 on synthetic data
- Verify kappa calculation with known agreement examples
- Cross-check sklearn metrics with manual calculation on small sample

### Reproducibility
- Fixed seed=42 for all stochastic operations
- Version-pin dependencies (transformers==4.30.0, torch==2.0.0)
- Save config alongside model (`models/config.json`)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Data Collection Pipeline | Implement ArXiv + Semantic Scholar API integration, extract 100-200 citation contexts | 8 | Module(2) + API(3) + Error(2) + Test(1) |
| E1-2 | Annotation Interface | CLI tool for binary labeling and feature extraction, kappa calculation | 6 | UI(2) + Storage(1) + Kappa(2) + Test(1) |
| E1-3 | SciBERT Classifier | Fine-tune SciBERT on annotated data, 80/20 split, early stopping | 9 | Model(2) + Training(3) + HF_API(2) + Test(2) |
| E1-4 | Evaluation Module | Compute precision/recall/F1, generate classification report | 5 | Metrics(2) + Validation(2) + Test(1) |
| E1-5 | Visualization Suite | Generate 5 required figures (confusion matrix, PR curve, training, kappa, length) | 7 | 5_Plots(3) + Formatting(2) + Test(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E1-3], Low(4-8): [E1-1, E1-2, E1-4, E1-5]

**Total Complexity**: 35 (PoC scope: minimal viable implementation)

---

**Document Status:** FINAL
**Next Phase:** Phase 4 - Implementation
**Output Path:** `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scope/docs/youra_research/h-e1/03_architecture.md`

# System Architecture: h-m1 - Stratified Training Mechanism

**Date:** 2026-07-12  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Step 1/4)  
**Architect:** architecture-agent  

**Applied Patterns:** Supervised text classification, stratified sampling, NER-based evaluation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending H-E1 implementation  
**Analyzed Path:** `docs/youra_research/h-e1/code/`  
**Findings:** H-E1 implements monolithic pipeline in single file. FastText classifier, BEIR loader, and evaluation framework reusable. Will modularize for H-M1.

---

## Architecture Overview

**Design Philosophy:** Modular mechanism validation extending H-E1's retrieval-quality filtering approach

**Core Components:**
1. Stratified training data generation (NEW)
2. FastText classifier with stratified sampling (EXTENDED from H-E1)
3. Named entity density measurement (NEW)
4. Perplexity baseline (REUSED from H-E1)
5. Comparative evaluation (NEW metrics)

**File Structure:**
```
h-m1/
├── code/
│   ├── data/
│   │   ├── loader.py              # BEIR + Common Crawl data loading
│   │   └── stratified_sampler.py  # Stratification logic
│   ├── models/
│   │   ├── fasttext_classifier.py # Retrieval-quality classifier
│   │   └── perplexity_scorer.py   # GPT-2 perplexity baseline
│   ├── evaluation/
│   │   ├── ner_evaluator.py       # spaCy-based entity density
│   │   └── visualizer.py          # Figure generation
│   ├── config.py                  # Configuration dataclass
│   ├── run_experiment.py          # Main orchestration
│   └── requirements.txt           # Dependencies
├── figures/                       # Generated visualizations
└── outputs/                       # Results JSON
```

---

## External Dependencies (Base Hypothesis)

### Reusable Components from H-E1

| Component | Location (H-E1) | Import Strategy | Usage in H-M1 |
|-----------|-----------------|-----------------|---------------|
| BEIR Data Loading | `run_experiment.py:74-88` | Copy pattern | Load BEIR NQ for training data |
| Perplexity Computation | `run_experiment.py:222-255` | Copy function | Educational quality baseline |
| FastText Training | `run_experiment.py:172-219` | Extend function | Add stratification |
| Training Data Extraction | `run_experiment.py:103-169` | Extend function | Add perplexity scores |

**Note:** H-E1 uses monolithic implementation. H-M1 will refactor into modules while preserving logic.

---

## Module Specifications

### 1. DataLoader (`code/data/loader.py`)

**Dependencies:** beir, transformers

```python
class BEIRLoader:
    def __init__(self, dataset: str = "nq", split: str = "test"): ...
    
    def load_data(self) -> Tuple[Dict, Dict, Dict]:
        """Load BEIR corpus, queries, qrels. From H-E1:74-88."""
        ...
    
    def sample_common_crawl(self, corpus: Dict, sample_size: int) -> Dict:
        """Sample corpus subset for experiment. From H-E1:91-100."""
        ...

class TrainingDataExtractor:
    def extract_beir_examples(
        self, corpus: Dict, qrels: Dict, samples_per_class: int
    ) -> Tuple[List[str], List[str]]:
        """Extract positive/negative examples. From H-E1:103-169."""
        ...
    
    def add_educational_scores(
        self, positive_texts: List[str], negative_texts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute perplexity for all examples. NEW for H-M1."""
        ...
```

---

### 2. StratifiedSampler (`code/data/stratified_sampler.py`)

**Dependencies:** numpy

```python
class StratifiedSampler:
    def __init__(self, oversample_ratio: float = 3.0): ...
    
    def identify_divergent_examples(
        self,
        educational_scores: np.ndarray,
        beir_scores: np.ndarray
    ) -> np.ndarray:
        """Identify low-educational, high-BEIR examples."""
        ...
    
    def oversample_training_data(
        self,
        texts: List[str],
        labels: List[str],
        divergent_mask: np.ndarray
    ) -> Tuple[List[str], List[str]]:
        """Apply 3x oversampling to divergent examples."""
        ...
    
    def compute_stratification_stats(
        self, original_size: int, stratified_size: int
    ) -> Dict:
        """Report oversampling statistics."""
        ...
```

---

### 3. FastTextClassifier (`code/models/fasttext_classifier.py`)

**Dependencies:** fasttext, tempfile

```python
class RetrievalQualityClassifier:
    def __init__(self, dim: int = 100, lr: float = 0.1, epoch: int = 25): ...
    
    def prepare_training_file(
        self,
        positive_texts: List[str],
        negative_texts: List[str],
        output_path: str
    ) -> None:
        """Write FastText format. From H-E1:177-189."""
        ...
    
    def train(self, training_file: str) -> None:
        """Train FastText supervised. From H-E1:192-199."""
        ...
    
    def predict_scores(self, documents: List[str]) -> np.ndarray:
        """Predict quality scores for documents. From H-E1:258-285."""
        ...
    
    def select_top_k(
        self, documents: Dict, scores: np.ndarray, k: int
    ) -> Dict:
        """Select top-k documents by score. From H-E1:288-308."""
        ...
```

---

### 4. PerplexityScorer (`code/models/perplexity_scorer.py`)

**Dependencies:** transformers, torch

```python
class GPT2PerplexityScorer:
    def __init__(self, model_name: str = "gpt2", device: str = "cuda"): ...
    
    def compute_perplexity_batch(
        self, documents: List[str], batch_size: int = 16
    ) -> np.ndarray:
        """Compute GPT-2 perplexity. From H-E1:222-255."""
        ...
    
    def select_by_perplexity(
        self, documents: Dict, scores: np.ndarray, k: int
    ) -> Dict:
        """Select top-k lowest perplexity. From H-E1:288-308."""
        ...
```

---

### 5. NEREntityEvaluator (`code/evaluation/ner_evaluator.py`)

**Dependencies:** spacy

```python
class EntityDensityEvaluator:
    def __init__(self, spacy_model: str = "en_core_web_sm"): ...
    
    def compute_entity_density(self, documents: List[str]) -> np.ndarray:
        """Compute entities per 100 tokens per document."""
        ...
    
    def compute_aggregate_metrics(
        self, densities: np.ndarray
    ) -> Dict[str, float]:
        """Mean, std, median entity density."""
        ...
    
    def compute_entity_type_distribution(
        self, documents: List[str]
    ) -> Dict[str, int]:
        """Count by entity type (PERSON, ORG, GPE, etc.)."""
        ...
    
    def compare_sets(
        self,
        retrieval_docs: List[str],
        perplexity_docs: List[str],
        gate_threshold: float = 1.15
    ) -> Dict[str, Any]:
        """Compute ratio and gate check."""
        ...
```

---

### 6. Visualizer (`code/evaluation/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class ExperimentVisualizer:
    def __init__(self, output_dir: str = "figures/"): ...
    
    def plot_entity_density_comparison(
        self,
        baseline_density: float,
        proposed_density: float,
        threshold: float = 1.15
    ) -> None:
        """Figure 1: Bar chart with threshold line (MANDATORY)."""
        ...
    
    def plot_entity_type_distribution(
        self,
        baseline_types: Dict[str, int],
        proposed_types: Dict[str, int]
    ) -> None:
        """Figure 2: Stacked bar chart of entity types."""
        ...
    
    def plot_stratification_effect(
        self,
        educational_scores: np.ndarray,
        beir_scores: np.ndarray,
        divergent_mask: np.ndarray
    ) -> None:
        """Figure 3: Scatter plot of oversampled region."""
        ...
    
    def plot_document_statistics(
        self,
        baseline_docs: List[str],
        proposed_docs: List[str]
    ) -> None:
        """Figure 4: Length, TTR comparison."""
        ...
```

---

### 7. Config (`code/config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class ExperimentConfig:
    # Experiment metadata
    hypothesis_id: str = "h-m1"
    seed: int = 42
    
    # Dataset
    beir_dataset: str = "nq"
    beir_split: str = "test"
    corpus_sample_size: int = 100000
    
    # Stratification
    stratification_ratio: float = 3.0
    educational_metric: str = "perplexity"
    beir_metric: str = "relevance"
    
    # Classifier
    fasttext_dim: int = 100
    fasttext_lr: float = 0.1
    fasttext_epoch: int = 25
    fasttext_ngrams: int = 2
    train_samples_per_class: int = 500
    
    # Evaluation
    target_corpus_size: int = 50000
    gate_threshold: float = 1.15
    
    # Models
    perplexity_model: str = "gpt2"
    ner_model: str = "en_core_web_sm"
    
    # Hardware
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig": ...
```

---

### 8. MainPipeline (`code/run_experiment.py`)

**Dependencies:** All above modules

```python
class StratifiedTrainingExperiment:
    def __init__(self, config: ExperimentConfig): ...
    
    def run_full_pipeline(self) -> Dict:
        """Execute complete experiment."""
        ...
    
    def stage_1_data_acquisition(self) -> Tuple[Dict, Dict, Dict]:
        """Load BEIR + sample corpus."""
        ...
    
    def stage_2_extract_training_data(
        self, corpus: Dict, qrels: Dict
    ) -> Tuple[List[str], List[str], np.ndarray, np.ndarray]:
        """Extract examples + educational scores."""
        ...
    
    def stage_3_stratified_sampling(
        self,
        positive_texts: List[str],
        negative_texts: List[str],
        pos_edu_scores: np.ndarray,
        neg_edu_scores: np.ndarray
    ) -> Tuple[List[str], List[str]]:
        """Apply stratification."""
        ...
    
    def stage_4_train_classifier(
        self, positive_texts: List[str], negative_texts: List[str]
    ) -> RetrievalQualityClassifier:
        """Train FastText on stratified data."""
        ...
    
    def stage_5_baseline_selection(
        self, corpus: Dict
    ) -> Dict:
        """Perplexity-based selection."""
        ...
    
    def stage_6_proposed_selection(
        self, corpus: Dict, classifier: RetrievalQualityClassifier
    ) -> Dict:
        """Classifier-based selection."""
        ...
    
    def stage_7_entity_evaluation(
        self, baseline_corpus: Dict, proposed_corpus: Dict
    ) -> Dict:
        """Compute entity density metrics."""
        ...
    
    def stage_8_visualization(self, results: Dict) -> None:
        """Generate all figures."""
        ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data Infrastructure | BEIR loader + training data extraction | 9 | 2+3+2+2 |
| M-2 | Stratification Module | Divergent example identification + oversampling | 11 | 3+3+3+2 |
| M-3 | Classifier Training | FastText with stratified data + validation | 10 | 2+3+3+2 |
| M-4 | Perplexity Baseline | GPT-2 scoring + document selection | 9 | 2+3+2+2 |
| M-5 | NER Evaluation | spaCy entity density measurement | 12 | 3+3+4+2 |
| M-6 | Document Selection | Apply both methods to corpus | 8 | 2+2+2+2 |
| M-7 | Visualization | 4 figures + metrics reporting | 10 | 3+2+3+2 |
| M-8 | Integration | End-to-end pipeline orchestration | 9 | 2+2+3+2 |

**Distribution:** High(14-17): [], Medium(9-13): [M-1, M-2, M-3, M-4, M-5, M-7, M-8], Low(4-8): [M-6]

**Total Complexity:** 78  
**Estimated Effort:** 5-7 days (MECHANISM validation)

---

## Epic Task Details

### M-1: Data Infrastructure (Complexity: 9)

**Objective:** Implement BEIR data loading and training data extraction with educational quality scores

**Subtasks:**
1. BEIR loader implementation (2)
   - Adapt H-E1 download logic
   - Return corpus, queries, qrels
2. Training data extractor (3)
   - Port H-E1 stratified extraction (lines 103-169)
   - Extract positive/negative from BEIR qrels
   - Sample balanced classes
3. Educational quality scorer (2)
   - Integrate GPT-2 perplexity
   - Compute scores for training examples
   - Cache scores for stratification
4. Data validation (2)
   - Verify class balance
   - Check score distributions
   - Log statistics

**Acceptance Criteria:**
- ~1K positive + ~1K negative examples extracted
- Educational scores (perplexity) computed for all training examples
- BEIR scores (relevance) computed from qrels
- Data saved to `data/training_examples.json`

---

### M-2: Stratification Module (Complexity: 11)

**Objective:** Implement stratified sampling logic to oversample divergent examples

**Subtasks:**
1. Divergent example identification (3)
   - Define thresholds (median educational, median BEIR)
   - Identify low-educational + high-BEIR examples
   - Create boolean mask for oversampling
2. Oversampling implementation (3)
   - Apply 3x multiplier to divergent examples
   - Preserve original examples
   - Combine into stratified dataset
3. Statistical validation (3)
   - Compute before/after class distributions
   - Verify oversampling ratio
   - Report stratification statistics
4. Edge case handling (2)
   - Handle insufficient divergent examples
   - Balance positive/negative classes
   - Log warnings for anomalies

**Acceptance Criteria:**
- Divergent examples identified using median thresholds
- 3x oversampling applied correctly
- Stratified training set ~3K examples (including oversampled)
- Statistics report: original size, oversampled size, divergent count

---

### M-3: Classifier Training (Complexity: 10)

**Objective:** Train FastText classifier on stratified training data

**Subtasks:**
1. Training file preparation (2)
   - Format: `__label__positive <text>`
   - Write stratified examples to temp file
   - Handle text cleaning (newlines, etc.)
2. FastText training (3)
   - Port H-E1 training logic (lines 192-199)
   - Apply hyperparameters (dim=100, lr=0.1, epoch=25)
   - Train supervised model
3. Validation (3)
   - Compute validation accuracy on held-out set
   - Test positive/negative class predictions
   - Require >0.7 accuracy for pass
4. Model persistence (2)
   - Save trained model to `models/classifier.bin`
   - Export prediction function
   - Log training metrics

**Acceptance Criteria:**
- FastText model trained with specified hyperparameters
- Validation accuracy >0.7
- Model saved and loadable
- Training log includes: epochs, loss, accuracy

---

### M-4: Perplexity Baseline (Complexity: 9)

**Objective:** Implement GPT-2 perplexity scoring and baseline document selection

**Subtasks:**
1. GPT-2 model loading (2)
   - Load GPT-2 base from transformers
   - Setup batch processing for efficiency
   - Handle GPU/CPU device placement
2. Perplexity computation (3)
   - Port H-E1 perplexity logic (lines 222-255)
   - Batch process 100K documents
   - Handle long documents (truncation)
3. Document selection (2)
   - Sort by ascending perplexity
   - Select top-50K documents
   - Create baseline corpus dict
4. Score caching (2)
   - Save perplexity scores to disk
   - Avoid recomputation on reruns
   - Log statistics (mean, std, range)

**Acceptance Criteria:**
- Perplexity computed for all 100K documents
- Top-50K selected by lowest perplexity
- Baseline corpus saved to `outputs/baseline_corpus_ids.json`
- Perplexity scores cached to `outputs/perplexity_scores.npy`

---

### M-5: NER Evaluation (Complexity: 12)

**Objective:** Implement spaCy-based named entity density measurement

**Subtasks:**
1. spaCy NER pipeline setup (3)
   - Load `en_core_web_sm` model
   - Batch processing configuration
   - Handle tokenization errors
2. Entity density computation (3)
   - Process documents through NER
   - Count entities per document
   - Normalize: (entities / tokens) × 100
3. Entity type analysis (4)
   - Extract entity types (PERSON, ORG, GPE, etc.)
   - Compute type distribution per corpus
   - Calculate type-token ratio
   - Secondary metrics: entity diversity
4. Comparative metrics (2)
   - Compute ratio: density_retrieval / density_perplexity
   - Check gate threshold (≥1.15)
   - Statistical test (optional t-test)

**Acceptance Criteria:**
- Entity density computed for both corpora
- Ratio computed with gate threshold check
- Entity type distribution reported
- Metrics saved to `outputs/entity_metrics.json`

---

### M-6: Document Selection (Complexity: 8)

**Objective:** Apply trained classifier and perplexity scorer to 100K corpus

**Subtasks:**
1. Classifier scoring (2)
   - Load trained FastText model
   - Score all 100K documents
   - Extract positive class probability
2. Threshold calibration (2)
   - Sort documents by quality score
   - Determine top-50K threshold
   - Verify corpus size match
3. Proposed corpus creation (2)
   - Select top-50K by classifier score
   - Create proposed corpus dict
   - Save document IDs
4. Corpus statistics (2)
   - Compare baseline vs proposed overlap
   - Report document length distributions
   - Log selection statistics

**Acceptance Criteria:**
- 100K documents scored by classifier
- Top-50K selected (proposed corpus)
- Top-50K selected by perplexity (baseline corpus)
- Both corpora saved to `outputs/`

---

### M-7: Visualization (Complexity: 10)

**Objective:** Generate 4 required figures for entity density analysis

**Subtasks:**
1. Figure 1: Entity density comparison (3)
   - Bar chart: baseline vs proposed
   - Horizontal threshold line at 1.15
   - Error bars (std dev)
   - Export PNG + PDF (300 DPI)
2. Figure 2: Entity type distribution (2)
   - Stacked bar chart of entity types
   - Compare baseline vs proposed
   - Export PNG + PDF
3. Figure 3: Stratification effect (3)
   - Scatter plot: educational vs BEIR quality
   - Highlight oversampled region
   - Add median threshold lines
   - Export PNG + PDF
4. Figure 4: Document statistics (2)
   - Compare: length, TTR, entity diversity
   - Heatmap or grouped bar chart
   - Export PNG + PDF

**Acceptance Criteria:**
- All 4 figures generated
- Saved to `figures/` directory
- 300 DPI resolution
- Consistent styling (seaborn theme)

---

### M-8: Integration (Complexity: 9)

**Objective:** Orchestrate end-to-end pipeline with logging and checkpointing

**Subtasks:**
1. Pipeline orchestrator (2)
   - Implement StratifiedTrainingExperiment class
   - Connect all 8 stages
   - Progress logging to console + file
2. Checkpoint system (2)
   - Save intermediate results per stage
   - Resume from checkpoint on failure
   - Avoid redundant computation
3. Results aggregation (3)
   - Collect metrics from all stages
   - Generate summary report
   - Gate pass/fail determination
   - Save to `outputs/experiment_results.json`
4. Error handling (2)
   - Try-catch for each stage
   - Graceful degradation
   - Exit codes (0=pass, 1=fail)

**Acceptance Criteria:**
- Single entry point: `run_experiment.py`
- Checkpointing functional
- Results JSON includes all metrics
- Gate condition checked and reported

---

## Dependencies Graph

```
M-1 (Data Infrastructure)
  ├─> M-2 (Stratification Module)
  │     └─> M-3 (Classifier Training)
  │           └─> M-6 (Document Selection)
  └─> M-4 (Perplexity Baseline)
        └─> M-6 (Document Selection)

M-6 (Document Selection)
  └─> M-5 (NER Evaluation)
        └─> M-7 (Visualization)

M-8 (Integration) depends on all tasks
```

**Critical Path:** M-1 → M-2 → M-3 → M-6 → M-5 → M-7 → M-8 (total: 69)

---

## External Python Packages

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| fasttext | >=0.9.2 | Text classification | PyPI |
| spacy | >=3.7 | Named entity recognition | PyPI |
| en_core_web_sm | >=3.7 | spaCy English NER model | `python -m spacy download` |
| transformers | >=4.30 | GPT-2 perplexity | PyPI |
| beir | >=1.0 | BEIR dataset loading | PyPI |
| torch | >=2.0 | GPU acceleration | PyPI |
| numpy | >=1.24 | Numerical operations | PyPI |
| matplotlib | >=3.7 | Visualization | PyPI |
| seaborn | >=0.12 | Statistical plots | PyPI |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Insufficient divergent examples | MEDIUM | HIGH | Lower threshold to 30th percentile if needed |
| Entity density correlation with length | MEDIUM | MEDIUM | Normalize by token count, report length stats |
| Perplexity computation slow | LOW | MEDIUM | Batch processing, GPU acceleration |
| spaCy memory issues on 100K docs | MEDIUM | LOW | Process in batches of 1K documents |

---

## Success Validation

**PoC Pass Criteria:**
1. Pipeline executes end-to-end without errors
2. Entity density ratio ≥ 1.0 (positive direction)

**Gate Pass Criteria (Full Validation):**
1. `density_retrieval / density_perplexity ≥ 1.15`
2. Stratification successfully applied (≥100 divergent examples)

---

## Next Steps

1. Phase 4 Coder: Implement modules following this architecture
2. Use Epic tasks M-1 through M-8 as implementation guide
3. Generate all artifacts in `code/`, `figures/`, `outputs/`
4. Run experiment and validate gate condition

---

**Architecture Version:** 1.0  
**Status:** Complete  
**Total Complexity:** 78 (8 Epic tasks)

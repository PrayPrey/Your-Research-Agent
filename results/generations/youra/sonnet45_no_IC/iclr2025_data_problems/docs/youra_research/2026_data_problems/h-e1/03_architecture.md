# System Architecture: h-e1 - Retrieval-Quality Corpus Filtering

**Date:** 2026-07-12  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Architect:** architecture-agent  

**Applied Patterns:** Minimal PoC pipeline for corpus filtering validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing experimental code. Infrastructure hooks only (.claude/hooks/).

---

## Architecture Overview

**Design Philosophy:** Minimal pipeline to validate "retrieval-quality filtering improves corpus utility"

**Core Components:**
1. Data acquisition (BEIR + Common Crawl)
2. Baseline corpus (perplexity filtering)
3. Proposed corpus (retrieval-quality filtering)
4. Retrieval evaluation (DPR + Recall@10)

**File Structure:**
```
h-e1/
├── code/
│   ├── data_loader.py          # BEIR + Common Crawl acquisition
│   ├── perplexity_filter.py    # Baseline corpus creation
│   ├── classifier.py           # Retrieval-quality classifier
│   ├── retrieval_eval.py       # DPR + Recall@10 evaluation
│   ├── visualize.py            # Figure generation
│   └── run_experiment.py       # Main pipeline
├── config/
│   └── config.yaml             # Fixed configuration
└── data/                       # Downloaded datasets (gitignored)
```

---

## Module Specifications

### 1. DataLoader (`code/data_loader.py`)

**Dependencies:** BEIR, transformers, warcio

```python
class BEIRLoader:
    def load_natural_questions(self, split: str = "test") -> Tuple[dict, dict, dict]:
        """Load BEIR NQ corpus, queries, qrels."""
        ...
    
    def extract_stratified_training_data(self, corpus: dict, qrels: dict) -> Tuple[List[str], List[str]]:
        """Extract high/low relevance documents for classifier training."""
        ...

class CommonCrawlSampler:
    def sample_documents(self, snapshot: str, n_docs: int) -> List[str]:
        """Sample N documents from CC snapshot."""
        ...
    
    def preprocess(self, documents: List[str]) -> List[str]:
        """HTML extraction, dedup, language filter, length filter."""
        ...
```

---

### 2. PerplexityFilter (`code/perplexity_filter.py`)

**Dependencies:** transformers (GPT-2)

```python
class PerplexityBaseline:
    def __init__(self, model_name: str = "gpt2"): ...
    
    def compute_perplexity(self, documents: List[str]) -> np.ndarray:
        """Compute GPT-2 perplexity for each document."""
        ...
    
    def filter_corpus(self, documents: List[str], target_size: int) -> List[str]:
        """Select top-N lowest perplexity documents."""
        ...
```

---

### 3. RetrievalQualityClassifier (`code/classifier.py`)

**Dependencies:** fasttext

```python
class RetrievalQualityClassifier:
    def __init__(self, dim: int = 100, lr: float = 0.1, epoch: int = 25): ...
    
    def prepare_training_data(self, 
                             positive_docs: List[str], 
                             negative_docs: List[str],
                             output_path: str) -> None:
        """Write FastText format: __label__positive <text>"""
        ...
    
    def train(self, training_file: str) -> None:
        """Train FastText supervised classifier."""
        ...
    
    def predict_quality(self, documents: List[str]) -> np.ndarray:
        """Return quality scores for documents."""
        ...
    
    def filter_corpus(self, documents: List[str], target_size: int) -> List[str]:
        """Select top-N highest quality documents."""
        ...
```

---

### 4. RetrievalEvaluator (`code/retrieval_eval.py`)

**Dependencies:** transformers (DPR), faiss, beir

```python
class DPRRetriever:
    def __init__(self, 
                 q_encoder: str = "facebook/dpr-question_encoder-single-nq-base",
                 ctx_encoder: str = "facebook/dpr-ctx_encoder-single-nq-base"): ...
    
    def encode_corpus(self, documents: List[str]) -> np.ndarray:
        """Encode documents to 768-dim embeddings."""
        ...
    
    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS cosine similarity index."""
        ...
    
    def retrieve(self, queries: List[str], index: faiss.Index, k: int = 10) -> dict:
        """Retrieve top-k documents per query."""
        ...

class RecallEvaluator:
    def compute_recall_at_k(self, 
                           retrieved: dict, 
                           qrels: dict, 
                           k: int = 10) -> float:
        """Compute Recall@k metric."""
        ...
    
    def compare_methods(self, 
                       baseline_recall: float, 
                       proposed_recall: float,
                       threshold: float = 0.03) -> dict:
        """Compare baseline vs proposed with gate threshold."""
        ...
```

---

### 5. Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn

```python
class ExperimentVisualizer:
    def plot_recall_comparison(self, 
                              baseline: float, 
                              proposed: float,
                              gate_threshold: float,
                              output_path: str) -> None:
        """Figure 1: Bar chart with gate threshold line."""
        ...
    
    def plot_quality_distribution(self, 
                                 scores: np.ndarray,
                                 threshold: float,
                                 output_path: str) -> None:
        """Figure 2: FastText score histogram."""
        ...
    
    def plot_corpus_statistics(self, 
                              baseline_docs: List[str],
                              proposed_docs: List[str],
                              output_path: str) -> None:
        """Figure 3: Entity density, TTR, length comparison."""
        ...
    
    def plot_query_performance(self,
                              baseline_results: dict,
                              proposed_results: dict,
                              output_path: str) -> None:
        """Figure 4: Scatter plot of per-query Recall."""
        ...
```

---

### 6. Main Pipeline (`code/run_experiment.py`)

**Dependencies:** All above modules

```python
class ExperimentPipeline:
    def __init__(self, config_path: str): ...
    
    def run_full_pipeline(self) -> dict:
        """Execute complete experiment from data to evaluation."""
        ...
    
    def stage_1_data_acquisition(self) -> None:
        """Download BEIR + sample Common Crawl."""
        ...
    
    def stage_2_baseline_corpus(self) -> List[str]:
        """Create perplexity-filtered corpus."""
        ...
    
    def stage_3_classifier_training(self) -> None:
        """Train retrieval-quality classifier."""
        ...
    
    def stage_4_proposed_corpus(self) -> List[str]:
        """Create retrieval-quality filtered corpus."""
        ...
    
    def stage_5_evaluation(self) -> dict:
        """DPR retrieval + Recall@10 for both corpora."""
        ...
    
    def stage_6_visualization(self, results: dict) -> None:
        """Generate all figures."""
        ...
```

---

## Configuration Schema

**File:** `config/config.yaml`

```yaml
experiment:
  hypothesis_id: h-e1
  seed: 42

datasets:
  beir:
    dataset: nq
    split: test
  common_crawl:
    snapshot: CC-MAIN-2024-10
    sample_size: 100000
    target_corpus_size: 1000000

preprocessing:
  min_length: 50
  max_length: 500
  language: en

baseline:
  method: perplexity
  model: gpt2

classifier:
  type: fasttext
  dim: 100
  lr: 0.1
  epoch: 25
  word_ngrams: 2
  stratification_ratio: 2

retrieval:
  question_encoder: facebook/dpr-question_encoder-single-nq-base
  context_encoder: facebook/dpr-ctx_encoder-single-nq-base
  embedding_dim: 768
  similarity: cosine

evaluation:
  metric: recall_at_k
  k: 10
  gate_threshold: 0.03

visualization:
  output_dir: figures/
  dpi: 300
  formats: [png, pdf]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Acquisition | BEIR NQ + CC sampling + preprocessing | 10 | 3+3+2+2 |
| A-2 | Baseline Corpus | GPT-2 perplexity filtering + indexing | 9 | 2+2+3+2 |
| A-3 | Classifier Training | Stratified data + FastText training | 11 | 3+2+4+2 |
| A-4 | Proposed Corpus | Classifier filtering + indexing | 8 | 2+2+2+2 |
| A-5 | Retrieval Evaluation | DPR retrieval + Recall@10 computation | 12 | 3+3+4+2 |
| A-6 | Visualization | 4 figures + metrics reporting | 8 | 2+2+2+2 |

**Distribution:** High(14-17): [], Medium(9-13): [A-1, A-3, A-5], Low(4-8): [A-2, A-4, A-6]

**Total Complexity:** 58  
**Estimated Effort:** 4-6 days (PoC implementation)

---

## Epic Task Details

### A-1: Data Acquisition (Complexity: 10)

**Objective:** Download and preprocess BEIR Natural Questions and Common Crawl sample

**Subtasks:**
1. BEIR NQ download via beir package (3)
   - Install BEIR
   - Download nq dataset
   - Verify corpus, queries, qrels
2. Common Crawl sampling (3)
   - Access CC-MAIN-2024-10 snapshot
   - Random sample 100K documents
   - WARC to text extraction
3. Preprocessing pipeline (2)
   - HTML cleaning
   - Deduplication (hash-based)
   - Language detection (fasttext lid)
4. Length filtering + tokenization (2)
   - Filter 50-500 tokens
   - DPR tokenization
   - Save preprocessed data

**Acceptance Criteria:**
- BEIR NQ test split loaded (~3,500 queries)
- 100K CC documents extracted and cleaned
- All documents tokenized with DPR tokenizer
- Data saved to `data/beir/` and `data/common_crawl/`

---

### A-2: Baseline Corpus (Complexity: 9)

**Objective:** Create perplexity-filtered 1M corpus using GPT-2

**Subtasks:**
1. GPT-2 model loading (2)
   - Load gpt2 from transformers
   - Setup batch processing
2. Perplexity computation (2)
   - Compute perplexity for all 100K docs
   - Handle long documents (chunking)
3. Corpus selection + indexing (3)
   - Sort by perplexity (ascending)
   - Select top 1M documents
   - Index with DPR context encoder
4. FAISS index creation (2)
   - Build cosine similarity index
   - Save index for retrieval

**Acceptance Criteria:**
- Perplexity scores computed for all documents
- 1M corpus selected (lowest perplexity)
- FAISS index created and saved
- Baseline corpus saved to `data/baseline_corpus/`

---

### A-3: Classifier Training (Complexity: 11)

**Objective:** Train FastText retrieval-quality classifier on stratified BEIR examples

**Subtasks:**
1. Stratified training data extraction (3)
   - Extract high-BEIR-relevance docs (positive)
   - Extract low-BEIR-relevance docs (negative)
   - Compute perplexity for stratification
2. Oversampling strategy (2)
   - Identify low-perplexity + high-BEIR docs
   - Apply 2:1 oversampling ratio
   - Balance positive/negative classes
3. FastText training (4)
   - Format data: `__label__positive <text>`
   - Train supervised model (dim=100, lr=0.1, epoch=25)
   - Validate on held-out BEIR examples
   - Achieve >0.7 validation accuracy
4. Model saving (2)
   - Save trained model
   - Export quality prediction function

**Acceptance Criteria:**
- ~10K positive + ~10K negative training examples
- FastText model trained with specified hyperparameters
- Validation accuracy >0.7
- Model saved to `models/retrieval_quality_classifier.bin`

---

### A-4: Proposed Corpus (Complexity: 8)

**Objective:** Apply trained classifier to create retrieval-quality filtered corpus

**Subtasks:**
1. Quality score prediction (2)
   - Load trained FastText model
   - Predict scores for all 100K docs
2. Threshold calibration (2)
   - Sort by quality score
   - Determine threshold for 1M corpus
3. Corpus selection (2)
   - Select top 1M documents by score
   - Index with DPR context encoder
4. FAISS index creation (2)
   - Build cosine similarity index
   - Save index for retrieval

**Acceptance Criteria:**
- Quality scores computed for all documents
- 1M corpus selected (highest quality)
- FAISS index created and saved
- Proposed corpus saved to `data/proposed_corpus/`

---

### A-5: Retrieval Evaluation (Complexity: 12)

**Objective:** Evaluate Recall@10 for both baseline and proposed corpora

**Subtasks:**
1. DPR encoder loading (3)
   - Load question encoder
   - Load context encoder
   - Load tokenizers
2. Query encoding (3)
   - Encode BEIR NQ test queries (~3,500)
   - Batch processing for efficiency
   - Generate 768-dim embeddings
3. Retrieval execution (4)
   - Retrieve top-10 for baseline corpus
   - Retrieve top-10 for proposed corpus
   - FAISS cosine similarity search
4. Recall@10 computation (2)
   - Compute recall for baseline
   - Compute recall for proposed
   - Compare with gate threshold (+0.03)

**Acceptance Criteria:**
- Recall@10 computed for both corpora
- Results saved to `results/recall_comparison.json`
- PoC pass condition checked: proposed > baseline
- Gate condition checked: proposed >= baseline + 0.03

---

### A-6: Visualization (Complexity: 8)

**Objective:** Generate 4 required figures and metrics report

**Subtasks:**
1. Figure 1: Recall comparison (2)
   - Bar chart (baseline vs proposed)
   - Horizontal gate threshold line
   - Export PNG + PDF (300 DPI)
2. Figure 2: Quality distribution (2)
   - Histogram of FastText scores
   - Mark threshold for 1M selection
   - Export PNG + PDF
3. Figure 3: Corpus statistics (2)
   - Compute entity density, TTR, length
   - Heatmap comparison table
   - Export PNG + PDF
4. Figure 4: Query-level performance (2)
   - Scatter plot (baseline vs proposed per query)
   - Diagonal y=x line
   - Highlight largest gains/losses
   - Export PNG + PDF

**Acceptance Criteria:**
- All 4 figures generated
- Saved to `figures/` in PNG and PDF formats
- 300 DPI resolution for paper quality
- Metrics summary report saved

---

## Dependencies Graph

```
A-1 (Data Acquisition)
  ├─> A-2 (Baseline Corpus)
  │     └─> A-5 (Retrieval Evaluation)
  │           └─> A-6 (Visualization)
  └─> A-3 (Classifier Training)
        └─> A-4 (Proposed Corpus)
              └─> A-5 (Retrieval Evaluation)
                    └─> A-6 (Visualization)
```

**Critical Path:** A-1 → A-3 → A-4 → A-5 → A-6 (total: 49)

---

## External Dependencies

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.30 | DPR encoders, GPT-2 |
| beir | >=1.0 | BEIR dataset + evaluation |
| fasttext | >=0.9.2 | Retrieval-quality classifier |
| faiss-cpu | >=1.7 | Dense retrieval indexing |
| warcio | >=1.7 | Common Crawl parsing |
| torch | >=2.0 | PyTorch backend |
| numpy | >=1.23 | Numerical operations |
| matplotlib | >=3.7 | Visualization |
| seaborn | >=0.12 | Statistical plots |
| pyyaml | >=6.0 | Config loading |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Common Crawl download slow | Pre-sample smaller subset (50K) for pilot |
| FastText overfitting | Stratified sampling + validation accuracy check |
| Low baseline performance | Use Wikipedia subset if CC quality too low |
| DPR memory issues | Batch encoding with checkpointing |

---

## Success Validation

**PoC Pass Criteria:**
1. Pipeline executes end-to-end without errors
2. `Recall@10_proposed > Recall@10_baseline`

**Gate Pass Criteria (for full validation):**
1. `Recall@10_proposed >= Recall@10_baseline + 0.03`
2. Statistical significance: `p < 0.05`

---

## Next Steps

1. Phase 4 Coder: Implement modules following this architecture
2. Use Epic tasks A-1 through A-6 as implementation guide
3. Generate all artifacts in `code/`, `config/`, `data/`, `figures/`
4. Run experiment and validate PoC pass condition

---

**Architecture Version:** 1.0  
**Status:** Complete  
**Total Lines:** 486

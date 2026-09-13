# System Architecture: h-m2 - Semantic vs Lexical Retrieval Differential

**Date:** 2026-07-12  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Step 2/4)  
**Architect:** architecture-agent  

**Applied Patterns:** Evaluation-only experiment, query splitting, differential metrics comparison

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends H-M1 corpora (baseline + retrieval-quality)  
**Analyzed Path:** `docs/youra_research/h-m1/code/run_experiment.py`  
**Findings:** H-M1 uses monolithic single-file implementation with BEIR loader, FastText classifier, perplexity scorer, and spaCy NER. H-M2 reuses corpora outputs but implements different evaluation logic (retrieval comparison, not NER).

---

## Architecture Overview

**Design Philosophy:** Evaluation-only experiment comparing retrieval performance across query types

**Core Components:**
1. H-M1 corpus loading (baseline + retrieval-quality) - REUSED
2. BM25 baseline for query splitting - NEW
3. DPR dense retrieval - NEW
4. Differential Recall@10 evaluation - NEW
5. Statistical visualization - NEW

**File Structure:**
```
h-m2/
├── code/
│   ├── data/
│   │   ├── loader.py           # BEIR query/corpus loading
│   │   └── corpus_manager.py   # Load H-M1 outputs
│   ├── retrieval/
│   │   ├── bm25_retriever.py   # BM25 baseline (query splitting)
│   │   └── dpr_retriever.py    # DPR dense retrieval
│   ├── evaluation/
│   │   ├── query_splitter.py   # Lexical vs semantic split
│   │   ├── recall_evaluator.py # Recall@10 computation
│   │   └── visualizer.py       # Figure generation
│   ├── config.py               # Configuration
│   ├── run_experiment.py       # Main orchestration
│   └── requirements.txt        # Dependencies
├── figures/                    # Generated visualizations
└── outputs/                    # Metrics JSON
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Component | H-M1 File | Import Strategy | Usage in H-M2 |
|-----------|-----------|-----------------|---------------|
| Corpus Loading | `run_experiment.py:50-56` | Copy BEIR pattern | Load same NQ dataset |
| Perplexity Corpus | `outputs/baseline_corpus_ids.json` | Load serialized | Baseline retrieval corpus |
| Retrieval Corpus | `outputs/retrieval_corpus_ids.json` | Load serialized | Proposed retrieval corpus |

**Verified from:** `docs/youra_research/h-m1/code/run_experiment.py` (actual implementation)

**Note:** H-M1 stores corpus as document ID lists. H-M2 must reconstruct full corpus from BEIR using these IDs.

---

## Module Specifications

### 1. BEIRDataLoader (`code/data/loader.py`)

**Dependencies:** beir

```python
class BEIRDataLoader:
    def __init__(self, dataset: str = "nq", split: str = "test"): ...
    
    def load_corpus_and_queries(self) -> Tuple[Dict, Dict, Dict]:
        """Load BEIR NQ corpus, queries, qrels. From H-M1:50-56."""
        ...
    
    def load_full_dataset(self) -> Tuple[Dict, Dict, Dict]:
        """Complete dataset for H-M2 evaluation."""
        ...
```

---

### 2. CorpusManager (`code/data/corpus_manager.py`)

**Dependencies:** json, pathlib

```python
class H1CorpusManager:
    def __init__(self, h1_folder: str): ...
    
    def load_baseline_corpus(self, full_corpus: Dict) -> Dict:
        """Load perplexity-filtered IDs from H-M1, reconstruct corpus."""
        ...
    
    def load_retrieval_corpus(self, full_corpus: Dict) -> Dict:
        """Load retrieval-quality IDs from H-M1, reconstruct corpus."""
        ...
    
    def verify_corpus_sizes(self) -> bool:
        """Ensure both corpora have same size for controlled comparison."""
        ...
```

---

### 3. BM25Retriever (`code/retrieval/bm25_retriever.py`)

**Dependencies:** rank_bm25, numpy

```python
class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75): ...
    
    def build_index(self, corpus: Dict) -> None:
        """Tokenize corpus and build BM25 index."""
        ...
    
    def retrieve(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """Retrieve top-k documents by BM25 score."""
        ...
    
    def batch_retrieve(self, queries: Dict, k: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """Retrieve for all queries."""
        ...
```

---

### 4. DPRRetriever (`code/retrieval/dpr_retriever.py`)

**Dependencies:** transformers, torch, numpy

```python
class DPRRetriever:
    def __init__(
        self,
        question_encoder: str = "facebook/dpr-question_encoder-single-nq-base",
        context_encoder: str = "facebook/dpr-ctx_encoder-single-nq-base",
        device: str = "cuda"
    ): ...
    
    def encode_corpus(self, corpus: Dict, batch_size: int = 16) -> np.ndarray:
        """Encode corpus into 768-dim embeddings."""
        ...
    
    def encode_queries(self, queries: Dict, batch_size: int = 16) -> np.ndarray:
        """Encode queries into 768-dim embeddings."""
        ...
    
    def retrieve(
        self,
        query_embeddings: np.ndarray,
        corpus_embeddings: np.ndarray,
        k: int = 10
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Retrieve top-k by dot product similarity."""
        ...
```

---

### 5. QuerySplitter (`code/evaluation/query_splitter.py`)

**Dependencies:** numpy

```python
class QuerySplitter:
    def __init__(self, qrels: Dict): ...
    
    def split_by_bm25_performance(
        self,
        bm25_results: Dict[str, List[Tuple[str, float]]],
        k: int = 10
    ) -> Tuple[List[str], List[str]]:
        """Split queries into lexical (BM25 succeeds) vs semantic (BM25 fails)."""
        ...
    
    def compute_split_statistics(
        self,
        lexical_queries: List[str],
        semantic_queries: List[str]
    ) -> Dict:
        """Report split distribution."""
        ...
```

---

### 6. RecallEvaluator (`code/evaluation/recall_evaluator.py`)

**Dependencies:** numpy

```python
class RecallEvaluator:
    def __init__(self, qrels: Dict): ...
    
    def compute_recall_at_k(
        self,
        results: Dict[str, List[Tuple[str, float]]],
        query_ids: List[str],
        k: int = 10
    ) -> float:
        """Compute Recall@k: fraction of queries with ≥1 relevant doc in top-k."""
        ...
    
    def compute_differential_metrics(
        self,
        baseline_results: Dict,
        retrieval_results: Dict,
        lexical_queries: List[str],
        semantic_queries: List[str],
        k: int = 10
    ) -> Dict:
        """Compute ΔRecall_semantic and ΔRecall_lexical."""
        ...
    
    def check_gate_condition(
        self,
        delta_semantic: float,
        delta_lexical: float,
        threshold_semantic: float = 0.04,
        threshold_lexical: float = 0.01
    ) -> bool:
        """Validate gate: ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01."""
        ...
```

---

### 7. Visualizer (`code/evaluation/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class DifferentialVisualizer:
    def __init__(self, output_dir: str = "figures/"): ...
    
    def plot_gate_metrics_comparison(
        self,
        delta_semantic: float,
        delta_lexical: float,
        threshold_semantic: float = 0.04,
        threshold_lexical: float = 0.01
    ) -> None:
        """Figure 1: Bar chart of ΔRecall with thresholds (MANDATORY)."""
        ...
    
    def plot_query_split_distribution(
        self,
        lexical_count: int,
        semantic_count: int
    ) -> None:
        """Figure 2: Pie chart of query distribution."""
        ...
    
    def plot_recall_by_corpus_and_query_type(
        self,
        metrics: Dict
    ) -> None:
        """Figure 3: Grouped bar chart (baseline vs retrieval, lexical vs semantic)."""
        ...
    
    def plot_improvement_distribution(
        self,
        semantic_improvements: List[float],
        lexical_improvements: List[float]
    ) -> None:
        """Figure 4: Histogram of per-query improvements."""
        ...
```

---

### 8. Config (`code/config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class ExperimentConfig:
    # Experiment metadata
    hypothesis_id: str = "h-m2"
    seed: int = 1
    
    # Dataset
    beir_dataset: str = "nq"
    beir_split: str = "test"
    
    # H-M1 Integration
    h1_folder: str = "../h-m1"
    baseline_corpus_file: str = "outputs/baseline_corpus_ids.json"
    retrieval_corpus_file: str = "outputs/retrieval_corpus_ids.json"
    
    # BM25 Configuration
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    
    # DPR Configuration
    question_encoder: str = "facebook/dpr-question_encoder-single-nq-base"
    context_encoder: str = "facebook/dpr-ctx_encoder-single-nq-base"
    dpr_batch_size: int = 16
    
    # Evaluation
    recall_k: int = 10
    gate_threshold_semantic: float = 0.04
    gate_threshold_lexical: float = 0.01
    
    # Hardware
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig": ...
```

---

### 9. MainPipeline (`code/run_experiment.py`)

**Dependencies:** All above modules

```python
class SemanticLexicalDifferentialExperiment:
    def __init__(self, config: ExperimentConfig): ...
    
    def run_full_pipeline(self) -> Dict:
        """Execute complete evaluation experiment."""
        ...
    
    def stage_1_load_data(self) -> Tuple[Dict, Dict, Dict]:
        """Load BEIR NQ queries, corpus, qrels."""
        ...
    
    def stage_2_load_h1_corpora(self, full_corpus: Dict) -> Tuple[Dict, Dict]:
        """Load baseline and retrieval corpora from H-M1 outputs."""
        ...
    
    def stage_3_bm25_query_split(
        self,
        corpus: Dict,
        queries: Dict,
        qrels: Dict
    ) -> Tuple[List[str], List[str]]:
        """Run BM25 on baseline corpus, split queries."""
        ...
    
    def stage_4_dpr_retrieval_baseline(
        self,
        baseline_corpus: Dict,
        queries: Dict
    ) -> Dict:
        """DPR retrieval on baseline corpus."""
        ...
    
    def stage_5_dpr_retrieval_proposed(
        self,
        retrieval_corpus: Dict,
        queries: Dict
    ) -> Dict:
        """DPR retrieval on retrieval-quality corpus."""
        ...
    
    def stage_6_differential_evaluation(
        self,
        baseline_results: Dict,
        retrieval_results: Dict,
        lexical_queries: List[str],
        semantic_queries: List[str]
    ) -> Dict:
        """Compute ΔRecall_semantic, ΔRecall_lexical."""
        ...
    
    def stage_7_visualization(self, metrics: Dict) -> None:
        """Generate all figures."""
        ...
    
    def stage_8_gate_validation(self, metrics: Dict) -> bool:
        """Check gate condition and save validation report."""
        ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Data Infrastructure | BEIR loading + H-M1 corpus reconstruction | 8 | 2+2+2+2 |
| M2-2 | BM25 Baseline | BM25 indexing + query splitting | 10 | 3+3+2+2 |
| M2-3 | DPR Implementation | Encode corpus/queries + retrieval | 14 | 4+4+4+2 |
| M2-4 | Query Split Logic | Lexical vs semantic classification | 7 | 2+2+2+1 |
| M2-5 | Differential Evaluation | Recall@10 computation + differential metrics | 11 | 3+3+3+2 |
| M2-6 | Gate Validation | Check thresholds + generate report | 6 | 2+2+1+1 |
| M2-7 | Visualization | 4 figures (gate metrics, split, recall, improvements) | 10 | 3+2+3+2 |
| M2-8 | Integration | End-to-end pipeline orchestration | 9 | 2+2+3+2 |

**Distribution:** High(14-17): [M2-3], Medium(9-13): [M2-2, M2-5, M2-7, M2-8], Low(4-8): [M2-1, M2-4, M2-6]

**Total Complexity:** 75  
**Estimated Effort:** 5-7 days (evaluation-only MECHANISM)

---

## Epic Task Details

### M2-1: Data Infrastructure (Complexity: 8)

**Objective:** Load BEIR NQ dataset and reconstruct H-M1 corpora from document IDs

**Subtasks:**
1. BEIR loader (2)
   - Download BEIR NQ test set
   - Return corpus (~2.68M docs), queries (~3.5K), qrels
2. H-M1 corpus loader (2)
   - Read `baseline_corpus_ids.json` from H-M1
   - Read `retrieval_corpus_ids.json` from H-M1
3. Corpus reconstruction (2)
   - Map document IDs to full corpus dict
   - Create baseline_corpus and retrieval_corpus dicts
4. Validation (2)
   - Verify both corpora have same size
   - Check entity density ratio metadata (from H-M1)
   - Log statistics

**Acceptance Criteria:**
- BEIR NQ loaded successfully
- Both H-M1 corpora reconstructed with equal sizes
- Verification passes (corpus sizes match)

---

### M2-2: BM25 Baseline (Complexity: 10)

**Objective:** Implement BM25 retrieval for query splitting

**Subtasks:**
1. BM25 indexing (3)
   - Tokenize baseline corpus (lowercase, split)
   - Build BM25Okapi index with k1=1.5, b=0.75
   - Handle memory efficiently (process in batches)
2. Retrieval implementation (3)
   - Score all queries against BM25 index
   - Retrieve top-10 documents per query
   - Store results as (doc_id, score) tuples
3. Query splitting (2)
   - Check if relevant doc in BM25 top-10
   - Classify as lexical (found) or semantic (not found)
   - Create lexical_queries and semantic_queries lists
4. Statistics (2)
   - Report split distribution (% lexical vs semantic)
   - Validate reasonable split (expect ~60/40)
   - Save split results to JSON

**Acceptance Criteria:**
- BM25 index built on baseline corpus
- All queries split into lexical/semantic
- Split distribution logged (~60% lexical, ~40% semantic)
- Query split saved to `outputs/query_split.json`

---

### M2-3: DPR Implementation (Complexity: 14)

**Objective:** Implement DPR dense retrieval for both corpora

**Subtasks:**
1. Model loading (4)
   - Load DPR question encoder
   - Load DPR context encoder
   - Load tokenizers
   - Setup GPU/CPU device placement
2. Corpus encoding (4)
   - Batch encode baseline corpus (768-dim embeddings)
   - Batch encode retrieval corpus (768-dim embeddings)
   - Handle memory constraints (batch_size=16)
   - Cache embeddings to disk (avoid recomputation)
3. Query encoding + retrieval (4)
   - Encode all queries (768-dim)
   - Compute dot product similarity (queries × corpus)
   - Retrieve top-10 for each query (argsort)
   - Repeat for both baseline and retrieval corpora
4. Result storage (2)
   - Store baseline_results: Dict[query_id, List[(doc_id, score)]]
   - Store retrieval_results: Dict[query_id, List[(doc_id, score)]]
   - Save to JSON files

**Acceptance Criteria:**
- DPR models loaded successfully
- Both corpora encoded (~2.68M docs × 2 = 5.36M embeddings)
- Retrieval results stored for both corpora
- Memory usage < 16GB (batched processing)

---

### M2-4: Query Split Logic (Complexity: 7)

**Objective:** Implement query classification logic based on BM25 performance

**Subtasks:**
1. Split function (2)
   - Input: BM25 results, qrels
   - Logic: Check if relevant_doc in top-k
   - Output: lexical_queries, semantic_queries
2. Statistical validation (2)
   - Compute split ratio (semantic / lexical)
   - Verify sufficient samples in each category (>100)
   - Warn if split too skewed (<20% in either)
3. Edge case handling (2)
   - Handle queries with no relevant docs (skip)
   - Handle queries with multiple relevant docs (any in top-k → lexical)
   - Log edge case counts
4. Save results (1)
   - Export split to JSON
   - Include metadata (split counts, ratio)

**Acceptance Criteria:**
- Query split produces ~60% lexical, ~40% semantic
- Both categories have >500 samples
- Split saved with statistics

---

### M2-5: Differential Evaluation (Complexity: 11)

**Objective:** Compute Recall@10 separately for semantic and lexical queries

**Subtasks:**
1. Recall@k implementation (3)
   - Input: retrieval results, qrels, query_ids
   - Logic: fraction with ≥1 relevant doc in top-k
   - Handle missing queries gracefully
2. Differential metric computation (3)
   - Compute Recall_baseline_lexical
   - Compute Recall_baseline_semantic
   - Compute Recall_retrieval_lexical
   - Compute Recall_retrieval_semantic
   - Calculate ΔRecall_semantic, ΔRecall_lexical
3. Statistical significance (3)
   - Optional: t-test for semantic improvement
   - Optional: confidence intervals
   - Report p-values
4. Metric aggregation (2)
   - Collect all metrics in dict
   - Save to `outputs/metrics.json`
   - Log summary statistics

**Acceptance Criteria:**
- Recall@10 computed for all 4 conditions (2 corpora × 2 query types)
- ΔRecall_semantic and ΔRecall_lexical calculated
- Metrics saved to JSON

---

### M2-6: Gate Validation (Complexity: 6)

**Objective:** Check gate condition and generate validation report

**Subtasks:**
1. Gate check (2)
   - Logic: ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01
   - Determine PASS/FAIL
   - Log gate result
2. Validation report generation (2)
   - Create `04_validation.md`
   - Include: gate result, metrics table, figure references
   - Document qualitative analysis (sample queries)
3. State update (1)
   - Update `verification_state.yaml`
   - Set h-m2 status to COMPLETED
4. Error handling (1)
   - Handle gate FAIL gracefully
   - Document failure reasons

**Acceptance Criteria:**
- Gate condition checked correctly
- 04_validation.md generated
- verification_state.yaml updated

---

### M2-7: Visualization (Complexity: 10)

**Objective:** Generate 4 figures for differential analysis

**Subtasks:**
1. Figure 1: Gate metrics comparison (3)
   - Bar chart: ΔRecall_semantic vs ΔRecall_lexical
   - Horizontal threshold lines (0.04, 0.01)
   - Export PNG + PDF (300 DPI)
2. Figure 2: Query split distribution (2)
   - Pie chart: % lexical vs semantic
   - Include counts in legend
3. Figure 3: Recall by corpus and query type (3)
   - Grouped bar chart (4 bars: 2 corpora × 2 query types)
   - X-axis: Query type, Y-axis: Recall@10
   - Color by corpus
4. Figure 4: Improvement distribution (2)
   - Histogram of per-query Recall improvements
   - Separate colors for semantic vs lexical
   - Add mean/median lines

**Acceptance Criteria:**
- All 4 figures generated
- Saved to `figures/` (PNG + PDF)
- 300 DPI resolution
- Consistent styling

---

### M2-8: Integration (Complexity: 9)

**Objective:** Orchestrate end-to-end pipeline with checkpointing

**Subtasks:**
1. Pipeline orchestrator (2)
   - Implement SemanticLexicalDifferentialExperiment class
   - Connect all 8 stages sequentially
   - Progress logging
2. Checkpoint system (2)
   - Save intermediate results per stage
   - Resume from checkpoint on failure
   - Avoid redundant DPR encoding
3. Results aggregation (3)
   - Collect metrics from all stages
   - Generate experiment summary
   - Check gate and save validation report
4. Error handling (2)
   - Try-catch for each stage
   - Graceful degradation
   - Exit codes (0=pass, 1=fail)

**Acceptance Criteria:**
- Single entry point: `run_experiment.py`
- Checkpointing functional
- Results JSON includes all metrics
- Gate validation executed

---

## Dependencies Graph

```
M2-1 (Data Infrastructure)
  ├─> M2-2 (BM25 Baseline)
  │     └─> M2-4 (Query Split Logic)
  │           └─> M2-5 (Differential Evaluation)
  └─> M2-3 (DPR Implementation)
        └─> M2-5 (Differential Evaluation)

M2-5 (Differential Evaluation)
  ├─> M2-6 (Gate Validation)
  └─> M2-7 (Visualization)

M2-8 (Integration) depends on all tasks
```

**Critical Path:** M2-1 → M2-3 → M2-5 → M2-7 → M2-8 (total: 52)

---

## External Python Packages

| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| beir | >=1.0 | BEIR dataset loading | PyPI |
| rank-bm25 | >=0.2.2 | BM25 baseline | PyPI |
| transformers | >=4.20.0 | DPR models | PyPI |
| torch | >=1.10.0 | GPU acceleration | PyPI |
| numpy | >=1.21.0 | Numerical operations | PyPI |
| matplotlib | >=3.5.0 | Visualization | PyPI |
| seaborn | >=0.11.0 | Statistical plots | PyPI |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| H-M1 corpus files missing | LOW | HIGH | Validate H-M1 completion before starting, fail early |
| DPR memory overflow (2.68M docs) | MEDIUM | HIGH | Batch encoding (16 docs/batch), cache embeddings to disk |
| BM25 query split too skewed | LOW | MEDIUM | Validate split (require 20-80% in each), log warning |
| BEIR download timeout | LOW | MEDIUM | Retry with exponential backoff, cache locally |

---

## Success Validation

**PoC Pass Criteria:**
1. Pipeline executes without errors
2. ΔRecall_semantic > 0 (any improvement)

**Gate Pass Criteria (Full Validation):**
1. ΔRecall_semantic ≥ 0.04
2. ΔRecall_lexical ≤ 0.01
3. Both conditions satisfied (AND logic)

---

## Next Steps

1. Phase 4 Coder: Implement modules following this architecture
2. Use Epic tasks M2-1 through M2-8 as implementation guide
3. Generate all artifacts in `code/`, `figures/`, `outputs/`
4. Run experiment and validate gate condition

---

**Architecture Version:** 1.0  
**Status:** Complete  
**Total Complexity:** 75 (8 Epic tasks)

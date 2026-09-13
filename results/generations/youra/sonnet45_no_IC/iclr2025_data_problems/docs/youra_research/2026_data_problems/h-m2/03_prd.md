# Product Requirements Document: H-M2 Semantic Query Retrieval Improvement

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis ID:** H-M2
**Hypothesis Type:** MECHANISM
**Status:** Draft v1.0

---

## Executive Summary

### Purpose
Implement an evaluation experiment to test whether documents with high factual density (selected by H-M1 classifier) improve retrieval performance differentially on semantic vs lexical queries, demonstrating that factual density benefits semantic understanding.

### Success Criteria
- **Primary Gate:** ΔRecall@10_semantic ≥ 0.04 AND ΔRecall@10_lexical ≤ 0.01
- **Secondary:** Evidence of multi-phrasing in high-density documents (qualitative analysis)
- **PoC Pass:** Code runs without error AND proposed_metric > baseline_metric

### Key Stakeholders
- **Research Lead:** Validates hypothesis mechanism (factual density → semantic retrieval)
- **Pipeline:** MECHANISM hypothesis (prerequisite: H-M1)

---

## Problem Statement

### Context
H-M1 validated that the retrieval-quality classifier successfully learns factual density (entity density 18% higher than baseline). H-M2 now tests whether this learned factual density translates to **differential** retrieval improvements—specifically helping semantic queries more than lexical queries.

### Core Problem
**Question:** Do high-density documents (identified by H-M1 classifier) improve retrieval performance specifically on semantic queries (where BM25 fails) more than on lexical queries (where BM25 succeeds)?

**Hypothesis:** Documents with high factual density contain information in multiple phrasings and higher informativeness per token, leading to +4pp Recall@10 improvement on semantic queries vs +1pp on lexical queries.

### Why This Matters
- Validates the *mechanism* behind H-E1's overall +5% improvement
- Tests whether factual density specifically helps semantic understanding
- Informs future corpus design (prioritize density for semantic-heavy tasks)

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing
**Priority:** P0 (Critical)
**Description:** Load BEIR Natural Questions test set with proper preprocessing for both BM25 and DPR retrieval

**Acceptance Criteria:**
- Load ~3,500 test queries and ~2.68M corpus documents from BEIR
- Apply standard BEIR preprocessing (lowercase, punctuation removal)
- Tokenize for both word-level (BM25) and subword (DPR) processing
- Verify data integrity (no missing queries/documents)

**Implementation Details:**
```python
from beir import util
from beir.datasets.data_loader import GenericDataLoader

url = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip".format("nq")
data_path = util.download_and_unzip(url, "datasets")
corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split="test")
```

**Dependencies:** BEIR library, internet connection for download

---

### FR-2: Load Pre-Existing Corpora from H-M1
**Priority:** P0 (Critical)
**Description:** Load both baseline (perplexity-filtered) and retrieval-quality (H-M1 classifier) corpora

**Acceptance Criteria:**
- Load perplexity-filtered corpus from H-M1 baseline
- Load retrieval-quality filtered corpus from H-M1 classifier output
- Verify both corpora have same size (controlled comparison)
- Confirm entity density ratio ≥ 1.15 (from H-M1 validation)

**Implementation Details:**
- Corpus location: `docs/youra_research/h-m1/` output artifacts
- Load mechanism: Read serialized corpus files (pickle or JSON)
- Validation: Check corpus sizes match, verify H-M1 metadata

**Dependencies:** H-M1 completed and validated

---

### FR-3: BM25 Baseline Implementation
**Priority:** P0 (Critical)
**Description:** Implement BM25 retrieval to split queries into lexical vs semantic subsets

**Acceptance Criteria:**
- Build BM25 index using rank-bm25 library (k1=1.5, b=0.75)
- Retrieve top-10 documents for each query on baseline corpus
- Split queries based on BM25 performance:
  - **Lexical queries:** Answer in BM25 top-10 (baseline succeeds)
  - **Semantic queries:** Answer NOT in BM25 top-10 (baseline fails)
- Report split distribution (expect ~60% lexical, ~40% semantic)

**Implementation Details:**
```python
from rank_bm25 import BM25Okapi

# Tokenize corpus
corpus_tokens = [doc.lower().split() for doc in corpus.values()]
bm25 = BM25Okapi(corpus_tokens, k1=1.5, b=0.75)

# Retrieve and split
for query_id, query_text in queries.items():
    query_tokens = query_text.lower().split()
    scores = bm25.get_scores(query_tokens)
    top_k_indices = np.argsort(scores)[-10:][::-1]
    
    # Check if relevant doc in top-k
    relevant_docs = qrels.get(query_id, {})
    if any(corpus_ids[idx] in relevant_docs for idx in top_k_indices):
        lexical_queries.append(query_id)
    else:
        semantic_queries.append(query_id)
```

**Dependencies:** rank-bm25 library

---

### FR-4: DPR Dense Retrieval Implementation
**Priority:** P0 (Critical)
**Description:** Implement DPR retrieval for both baseline and retrieval-quality corpora

**Acceptance Criteria:**
- Load pre-trained DPR models:
  - Question encoder: facebook/dpr-question_encoder-single-nq-base
  - Context encoder: facebook/dpr-ctx_encoder-single-nq-base
- Encode both corpora (perplexity-filtered, retrieval-quality) into 768-dim embeddings
- Encode all queries into 768-dim embeddings
- Retrieve top-10 documents using dot product similarity
- Store retrieval results for both corpora

**Implementation Details:**
```python
from transformers import DPRQuestionEncoder, DPRContextEncoder
from transformers import DPRQuestionEncoderTokenizer, DPRContextEncoderTokenizer

# Load models
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
context_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")

# Encode corpus and queries
# Retrieve via dot product similarity
```

**Dependencies:** transformers library, HuggingFace model access

---

### FR-5: Differential Recall@10 Evaluation
**Priority:** P0 (Critical)
**Description:** Compute Recall@10 improvements separately for semantic vs lexical queries

**Acceptance Criteria:**
- Compute Recall@10 for baseline corpus on lexical queries
- Compute Recall@10 for baseline corpus on semantic queries
- Compute Recall@10 for retrieval corpus on lexical queries
- Compute Recall@10 for retrieval corpus on semantic queries
- Calculate differentials:
  - ΔRecall_semantic = Recall_retrieval_semantic - Recall_baseline_semantic
  - ΔRecall_lexical = Recall_retrieval_lexical - Recall_baseline_lexical
- Verify gate condition: ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01

**Implementation Details:**
```python
def compute_recall_at_k(results, qrels, k=10):
    """Compute Recall@k for retrieval results."""
    recalls = []
    for query_id, result_list in results.items():
        top_k_docs = [doc_id for doc_id, _ in result_list[:k]]
        relevant_docs = set(qrels.get(query_id, {}).keys())
        
        # Recall@k = 1 if any relevant doc in top-k, else 0
        recall = 1.0 if any(doc in relevant_docs for doc in top_k_docs) else 0.0
        recalls.append(recall)
    
    return sum(recalls) / len(recalls) if recalls else 0.0
```

**Dependencies:** Custom implementation (no standard library)

---

### FR-6: Gate Validation and Result Reporting
**Priority:** P0 (Critical)
**Description:** Validate gate condition and generate validation report

**Acceptance Criteria:**
- Check primary gate: ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01
- Generate gate validation result (PASS/FAIL)
- Create validation report (04_validation.md) with:
  - Metrics: ΔRecall_semantic, ΔRecall_lexical
  - Gate result: PASS/FAIL
  - Qualitative analysis: Sample queries with improvements
- Update verification_state.yaml with validation result

**Implementation Details:**
- Gate logic: Both conditions must be satisfied for PASS
- Report format: Follow Phase 4 validation template
- State update: Set `sub_hypotheses.h-m2.validation.status = "COMPLETED"`

**Dependencies:** verification_state.yaml write access

---

### FR-7: Visualization Generation
**Priority:** P1 (Required)
**Description:** Generate mandatory and additional visualizations for hypothesis validation

**Acceptance Criteria:**
- **Mandatory Figure:** Gate Metrics Comparison
  - Bar chart: ΔRecall_semantic vs ΔRecall_lexical
  - Horizontal lines at thresholds (0.04, 0.01)
  - Save to: `h-m2/figures/gate_metrics_comparison.png`
- **Additional Figures:**
  - Query split distribution (pie chart)
  - Recall@10 by corpus and query type (grouped bar chart)
  - Improvement distribution (histogram)
  - Sample query analysis (table/text)
- All figures saved to `h-m2/figures/` folder

**Implementation Details:**
- Use matplotlib for plotting
- Follow dataviz skill guidelines for accessibility
- Include figure references in 04_validation.md

**Dependencies:** matplotlib, numpy

---

## Non-Functional Requirements

### NFR-1: Computational Resources
**Requirement:** Experiment must complete on standard compute (16GB RAM, GPU optional)
**Rationale:** Enable reproducibility without specialized hardware
**Metric:** Memory usage < 16GB, runtime < 4 hours on CPU

### NFR-2: Deterministic Execution
**Requirement:** All components must produce deterministic results
**Rationale:** Enable exact reproducibility
**Implementation:**
- Set random seed: 1 (deterministic evaluation)
- BM25: Deterministic by design
- DPR: No dropout during inference
- Evaluation: Deterministic Recall@k computation

### NFR-3: Code Quality
**Requirement:** Code must pass static validation before execution
**Rationale:** Catch bugs early in PoC stage
**Implementation:**
- Type hints for all functions
- Docstrings for public APIs
- Input validation for corpus/query loading

### NFR-4: Traceability
**Requirement:** All design decisions must trace to Phase 2C or research sources
**Rationale:** Maintain scientific rigor
**Implementation:**
- Inline comments referencing Phase 2C sections
- README documenting source repositories (BEIR, DPR, rank-bm25)

---

## Data Requirements

### Input Data Sources

**Source 1: BEIR Natural Questions**
- **Type:** External benchmark dataset
- **Format:** JSON (corpus), TSV (queries, qrels)
- **Size:** ~2.68M documents, ~3.5K queries
- **Access:** Public via BEIR library download
- **Preprocessing:** BEIR standard preprocessing applied
- **Loading:** Use `beir.datasets.data_loader.GenericDataLoader`

**Source 2: H-M1 Baseline Corpus**
- **Type:** Derived from H-M1 experiment
- **Format:** Serialized (pickle/JSON)
- **Size:** Subset of BEIR NQ corpus (perplexity-filtered)
- **Access:** Local file from `docs/youra_research/h-m1/` outputs
- **Preprocessing:** Already applied in H-M1
- **Loading:** Deserialize from H-M1 output artifacts

**Source 3: H-M1 Retrieval-Quality Corpus**
- **Type:** Derived from H-M1 classifier output
- **Format:** Serialized (pickle/JSON)
- **Size:** Subset of BEIR NQ corpus (retrieval-quality filtered)
- **Access:** Local file from `docs/youra_research/h-m1/` outputs
- **Preprocessing:** Already applied in H-M1
- **Loading:** Deserialize from H-M1 output artifacts
- **Metadata:** Entity density ratio ≥ 1.18 (validated in H-M1)

### Output Data Artifacts

**Artifact 1: Query Split Results**
- **Type:** JSON file
- **Format:** `{"lexical_queries": [...], "semantic_queries": [...]}`
- **Location:** `h-m2/data/query_split.json`
- **Purpose:** Document query categorization for analysis

**Artifact 2: Retrieval Results**
- **Type:** JSON file per corpus
- **Format:** `{query_id: [(doc_id, score), ...], ...}`
- **Location:** `h-m2/data/{baseline,retrieval}_results.json`
- **Purpose:** Enable post-hoc analysis

**Artifact 3: Evaluation Metrics**
- **Type:** JSON file
- **Format:** `{"delta_recall_semantic": X, "delta_recall_lexical": Y, ...}`
- **Location:** `h-m2/data/metrics.json`
- **Purpose:** Store quantitative results for validation report

**Artifact 4: Validation Report**
- **Type:** Markdown file
- **Location:** `h-m2/04_validation.md`
- **Content:** Gate result, metrics, figures, analysis
- **Purpose:** Document hypothesis validation outcome

---

## Dependencies and Prerequisites

### External Dependencies

| Dependency | Version | Purpose | Installation |
|------------|---------|---------|--------------|
| **beir** | >=0.3.0 | Dataset loading, evaluation | `pip install beir` |
| **rank-bm25** | >=0.2.2 | BM25 baseline implementation | `pip install rank-bm25` |
| **transformers** | >=4.20.0 | DPR model loading | `pip install transformers` |
| **torch** | >=1.10.0 | DPR inference | `pip install torch` |
| **numpy** | >=1.21.0 | Numerical operations | `pip install numpy` |
| **matplotlib** | >=3.5.0 | Visualization | `pip install matplotlib` |

### Prerequisite Hypotheses

**H-M1: Classifier Learns Factual Density**
- **Status Required:** COMPLETED with PASS
- **Validation Metric:** Entity density ratio ≥ 1.15 (actual: 1.18)
- **Artifacts Needed:**
  - Perplexity-filtered baseline corpus
  - Retrieval-quality classifier output corpus
  - H-M1 validation report for baseline metrics
- **Why Required:** H-M2 evaluates the *differential impact* of H-M1's learned factual density

### Environment Prerequisites

- **Python:** >=3.8
- **Memory:** >=16GB RAM (for encoding 2.68M documents)
- **Storage:** ~10GB for BEIR dataset + model cache
- **GPU:** Optional (accelerates DPR encoding, but not required)

---

## Success Metrics and Validation

### Primary Success Metrics

**Metric 1: ΔRecall@10_semantic**
- **Definition:** Recall@10 improvement on semantic queries (BM25-failed subset)
- **Target:** ≥ 0.04 (4 percentage points)
- **Measurement:** `Recall_retrieval_semantic - Recall_baseline_semantic`
- **Gate Type:** MUST SATISFY (AND condition)

**Metric 2: ΔRecall@10_lexical**
- **Definition:** Recall@10 improvement on lexical queries (BM25-succeeded subset)
- **Target:** ≤ 0.01 (1 percentage point)
- **Measurement:** `Recall_retrieval_lexical - Recall_baseline_lexical`
- **Gate Type:** MUST SATISFY (AND condition)

### Secondary Success Metrics

**Metric 3: Differential Gain**
- **Definition:** Difference between semantic and lexical improvements
- **Target:** ΔRecall_semantic - ΔRecall_lexical ≥ 0.03 (3pp differential)
- **Purpose:** Validate mechanism hypothesis (differential impact)

**Metric 4: Query Split Balance**
- **Definition:** Proportion of semantic vs lexical queries
- **Expected:** ~40% semantic, ~60% lexical (typical for NQ)
- **Purpose:** Ensure sufficient samples in both categories

### PoC Success Criteria

**PoC Pass Condition:**
1. Code runs without runtime errors
2. `proposed_metric > baseline_metric` (any improvement on semantic queries)

**Note:** PoC pass ≠ Gate pass. PoC validates implementation correctness, gate validates hypothesis.

### Validation Protocol

**Step 1:** Execute experiment code (Phase 4)
**Step 2:** Compute ΔRecall_semantic and ΔRecall_lexical
**Step 3:** Check gate condition:
- IF ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01 → **PASS**
- ELSE → **FAIL**
**Step 4:** Generate 04_validation.md report
**Step 5:** Update verification_state.yaml with result

---

## Implementation Notes

### Key Technical Decisions

**Decision 1: Use Standard Libraries (BEIR, DPR, rank-bm25)**
- **Rationale:** No "official implementation" exists for this novel hypothesis
- **Justification:** Standard libraries are widely adopted (1k+ stars), well-tested, and provide validated implementations
- **Trade-off:** Less customization vs higher reliability

**Decision 2: Evaluation-Only (No Training)**
- **Rationale:** H-M1 already trained the classifier; H-M2 evaluates its output
- **Justification:** Controlled experiment focusing on mechanism validation
- **Trade-off:** Faster execution, but dependent on H-M1 quality

**Decision 3: Reuse H-M1 Corpora**
- **Rationale:** Enable controlled comparison (only query splitting changes)
- **Justification:** Validates that H-M1's learned density translates to semantic gains
- **Trade-off:** H-M2 cannot run independently, but gains scientific rigor

### Known Limitations

**Limitation 1: MCP Tool Availability**
- **Issue:** Archon KB has limited retrieval content (focuses on generative models)
- **Impact:** Less reference code for implementation
- **Mitigation:** Use well-established standard libraries instead

**Limitation 2: Exa Search Unavailable**
- **Issue:** 402 error (quota/billing) during Phase 2C
- **Impact:** Cannot search GitHub for implementations
- **Mitigation:** Documented fallback to known standard repositories

**Limitation 3: Query Split Sensitivity**
- **Issue:** BM25 threshold (top-10) is somewhat arbitrary
- **Impact:** Query split may vary slightly with different thresholds
- **Mitigation:** Use standard k=10 (common in IR literature), document in validation

### Verification Strategy

**Pre-Execution Validation:**
- Verify BEIR dataset loads correctly (spot-check queries/documents)
- Verify H-M1 corpora have same size
- Confirm DPR models download successfully

**Runtime Validation:**
- Check query split produces reasonable distribution (~60/40)
- Verify retrieval results contain relevant documents (spot-check)
- Monitor memory usage stays < 16GB

**Post-Execution Validation:**
- Verify all metrics computed without errors
- Check figure generation completes
- Validate 04_validation.md contains required sections

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **H-M1 corpora not found** | Low | High | Validate H-M1 completion in Step 1, fail early if missing |
| **BEIR download fails** | Low | High | Retry with timeout, provide manual download instructions |
| **DPR memory overflow** | Medium | Medium | Batch encoding (1000 docs at a time), use CPU if GPU OOM |
| **Query split too skewed** | Low | Medium | Validate split distribution, warn if <20% in either category |
| **Gate fails** | Medium | Medium | Document failure, provide diagnostic analysis in 04_validation.md |

---

## Appendix: Traceability Matrix

| Requirement | Source Type | Source Reference |
|-------------|-------------|------------------|
| FR-1: Dataset | Phase 2C | 02c_experiment_brief.md § Dataset |
| FR-2: H-M1 Corpora | Phase 2C + H-M1 | 02c_experiment_brief.md § Continuation Context |
| FR-3: BM25 Baseline | Phase 2C + Standard | 02c_experiment_brief.md § Baseline Model, rank-bm25 docs |
| FR-4: DPR Retrieval | Phase 2C + Facebook | 02c_experiment_brief.md § Proposed Model, facebook/DPR |
| FR-5: Differential Evaluation | Phase 2C | 02c_experiment_brief.md § Evaluation |
| FR-6: Gate Validation | Phase 2B | 02b_verification_plan.md (via 02c_experiment_brief.md § Gate) |
| FR-7: Visualization | Phase 2C | 02c_experiment_brief.md § Visualization Requirements |
| NFR-1: Compute | Best Practice | Standard research compute constraints |
| NFR-2: Determinism | Phase 2C | 02c_experiment_brief.md § Training Protocol (seed=1) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-12 | Anonymous | Initial PRD created from Phase 2C experiment brief |

---

**Status:** Ready for Phase 3 - Implementation Planning
**Next Step:** Architecture design (Step 3)

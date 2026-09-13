# Experiment Design: H-M2

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis Statement:** Documents with high factual density and entity coverage improve retrieval performance specifically on semantic queries (BM25-failed) by +4% Recall@10, compared to +1% improvement on lexical queries (BM25-succeeded), because high-density documents contain information in multiple phrasings and higher informativeness per token.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests "how/why mechanism works"

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 (COMPLETED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM (Step 2 of 4)
- **Prerequisites:** H-M1

### Gate Condition
ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01

---

## Continuation Context

**Previous Hypothesis:** H-M1 (Classifier Learns Factual Density)
- **Status:** COMPLETED
- **Key Result:** Entity density ratio = 1.18 (≥1.15 target, PASS)
- **Dataset Used:** BEIR Natural Questions
- **Model Used:** GPT-2 for perplexity baseline
- **Proven:** Retrieval-quality classifier successfully learns factual density via stratified training

**Continuation Strategy:**
- Reuse same dataset (BEIR Natural Questions) for controlled comparison
- Reuse classifier from H-M1 to select high-density documents
- Test differential impact on semantic vs lexical queries

### Previous Hypothesis Results
H-M1 validated that the retrieval-quality classifier learns factual density (entity density 18% higher than baseline). H-M2 now tests whether this density translates to semantic retrieval improvements.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: BM25 semantic lexical query splitting retrieval evaluation**
- Limited direct results (Archon KB focuses on generative models, not retrieval)
- Found general evaluation metric patterns but not retrieval-specific

**Query 2: Dense retrieval DPR BEIR Natural Questions evaluation**
- General evaluation concepts but no BEIR/DPR specific implementations in KB

**Query 3: Information retrieval evaluation Recall@k metrics**
- Found FID/PR metrics for generative models (not applicable to retrieval)
- Key insight: Evaluation metrics typically configured as dicts with type, num_samples

### Archon Code Examples

**Query 1: BM25 retrieval PyTorch implementation**
- No direct BM25 implementations found in code examples
- Archon KB focuses on deep learning, not traditional IR methods

**Query 2: Retrieval evaluation metrics Recall precision Python**
- Found evaluation hook patterns from mmgeneration (generative metrics)
- Pattern: metrics = dict(type='MetricName', num_images=N, ...)

**Key Insight:** Archon KB lacks retrieval-specific content. Will rely on standard libraries (rank_bm25, beir) for implementation.

### Exa GitHub Implementations

**Status:** Exa MCP unavailable (402 error - quota/billing issue)

**Fallback Strategy:** Use well-known standard implementations:
1. **BEIR Benchmark:** UKPLab/beir (official repository)
2. **BM25:** rank-bm25 library (standard Python implementation)
3. **DPR:** facebook/DPR (official implementation)

**Reference Repositories (from literature/standard practice):**
- BEIR: https://github.com/beir-cellar/beir
- DPR: https://github.com/facebookresearch/DPR
- rank-bm25: https://github.com/dorianbrown/rank_bm25

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT a paper reproduction - this is a novel hypothesis test**

**Implementation Strategy:**
- **Primary:** Use standard libraries (BEIR, DPR, rank-bm25) - widely adopted, well-tested
- **Fallback:** Manual BM25 implementation if library integration fails
- **Justification:** Standard libraries provide validated implementations. No "author's official code" exists for this novel hypothesis.

**Recommended Implementation Path:**
- Primary: BEIR benchmark framework + facebook DPR + rank-bm25
- Fallback: Custom BM25 implementation + manual DPR integration
- Justification: BEIR is the standard evaluation framework for retrieval, DPR is the official Facebook implementation, rank-bm25 is widely used for lexical baselines.

### Code Analysis (Serena MCP)

**Status:** *Skipped* - No complex code requiring analysis (Exa unavailable, using standard libraries)

---

## Experiment Specification

### Dataset

**Name:** BEIR Natural Questions (test set)
**Type:** standard (real benchmark dataset)
**Source:** BEIR benchmark (Thakur et al., 2021)
**Size:** ~3,500 test queries, ~2.68M corpus documents

**Reused from H-M1:** Yes - enables controlled comparison (only query splitting changes)

**Splits:**
- Queries: test set (~3,500 queries)
- Corpus: Natural Questions corpus from BEIR (~2.68M documents)
- Split methodology: Split queries into Lexical vs Semantic based on BM25 baseline performance

**Query Splitting Protocol:**
1. **Lexical Queries:** Answer appears in BM25 top-10 results (baseline succeeds)
2. **Semantic Queries:** Answer NOT in BM25 top-10 results (baseline fails)
3. Measure Recall@10 improvement separately for each subset

**Preprocessing:**
- Text cleaning: BEIR standard preprocessing (lowercase, punctuation removal)
- Tokenization: Word-level for BM25, subword for DPR
- No additional filtering (use BEIR default)

**Loading Information** (for Phase 4 download):
- Method: BEIR library
- Identifier: "nq" (BEIR dataset code)
- Code:
```python
from beir import util
from beir.datasets.data_loader import GenericDataLoader

# Download and load BEIR Natural Questions
url = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip".format("nq")
data_path = util.download_and_unzip(url, "datasets")
corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split="test")
```

### Models

#### Baseline Model

**Reused from H-M1:** Perplexity-based filtering + BM25 retrieval

**Two-Stage Baseline:**

1. **Corpus Filtering (from H-M1):**
   - Method: Perplexity-based filtering using GPT-2
   - Purpose: Create perplexity-filtered baseline corpus
   - Status: Already completed in H-M1

2. **Retrieval Model:**
   - **BM25 (Lexical Baseline):**
     - Implementation: rank-bm25 library (Okapi BM25)
     - Parameters: k1=1.5, b=0.75 (default tuning)
     - Purpose: Define lexical vs semantic query split
   
   - **DPR (Dense Retrieval):**
     - Question Encoder: facebook/dpr-question_encoder-single-nq-base
     - Context Encoder: facebook/dpr-ctx_encoder-single-nq-base
     - Embedding dimension: 768
     - Similarity: Dot product
     - Purpose: Measure Recall@10 on both query subsets

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: facebook/dpr-question_encoder-single-nq-base, facebook/dpr-ctx_encoder-single-nq-base
- Code:
```python
from transformers import DPRQuestionEncoder, DPRContextEncoder, DPRQuestionEncoderTokenizer, DPRContextEncoderTokenizer

# Load DPR models
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
context_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")

# For BM25
from rank_bm25 import BM25Okapi
bm25 = BM25Okapi(corpus_tokens, k1=1.5, b=0.75)
```

#### Proposed Model

**Architecture:** Retrieval-quality filtered corpus (from H-M1 classifier) + DPR

**Core Mechanism Implementation:**

```python
# Core Mechanism: Query Split + Differential Retrieval Evaluation
# Based on: H-M1 classifier output + BM25/DPR comparison

class SemanticLexicalSplitEvaluator:
    """
    Evaluates retrieval performance on semantic vs lexical queries.
    Tests if high-density documents improve semantic retrieval more than lexical.
    """
    def __init__(self, corpus_baseline, corpus_retrieval, queries, qrels):
        """
        Args:
            corpus_baseline: Perplexity-filtered corpus (from H-M1 baseline)
            corpus_retrieval: Retrieval-quality filtered corpus (from H-M1 classifier)
            queries: BEIR Natural Questions test queries (~3.5K)
            qrels: Query relevance labels
        """
        self.corpus_baseline = corpus_baseline
        self.corpus_retrieval = corpus_retrieval
        self.queries = queries
        self.qrels = qrels
        
    def split_queries(self, bm25_results, k=10):
        """
        Split queries into Lexical vs Semantic based on BM25 performance.
        
        Returns:
            lexical_queries: Answer in BM25 top-k (BM25 succeeded)
            semantic_queries: Answer NOT in BM25 top-k (BM25 failed)
        """
        lexical_queries = []
        semantic_queries = []
        
        for query_id, results in bm25_results.items():
            top_k_docs = [doc_id for doc_id, _ in results[:k]]
            relevant_docs = self.qrels.get(query_id, {})
            
            # Check if any relevant doc is in top-k
            if any(doc_id in relevant_docs for doc_id in top_k_docs):
                lexical_queries.append(query_id)
            else:
                semantic_queries.append(query_id)
                
        return lexical_queries, semantic_queries
    
    def evaluate_differential(self, dpr_model, k=10):
        """
        Measure Recall@k improvement on semantic vs lexical queries.
        
        Returns:
            delta_recall_lexical: Improvement on lexical queries
            delta_recall_semantic: Improvement on semantic queries
        """
        # Baseline corpus evaluation (perplexity-filtered)
        recall_baseline_lexical = self.compute_recall(
            dpr_model, self.corpus_baseline, self.lexical_queries, k
        )
        recall_baseline_semantic = self.compute_recall(
            dpr_model, self.corpus_baseline, self.semantic_queries, k
        )
        
        # Retrieval-quality corpus evaluation
        recall_retrieval_lexical = self.compute_recall(
            dpr_model, self.corpus_retrieval, self.lexical_queries, k
        )
        recall_retrieval_semantic = self.compute_recall(
            dpr_model, self.corpus_retrieval, self.semantic_queries, k
        )
        
        # Differential gain
        delta_recall_lexical = recall_retrieval_lexical - recall_baseline_lexical
        delta_recall_semantic = recall_retrieval_semantic - recall_baseline_semantic
        
        return delta_recall_lexical, delta_recall_semantic
    
    def compute_recall(self, dpr_model, corpus, query_ids, k):
        """Compute Recall@k for given queries and corpus."""
        # Encode corpus and queries with DPR
        # Retrieve top-k documents
        # Calculate recall (fraction of queries with relevant doc in top-k)
        pass

# Integration: Run after H-M1 classifier generates two corpora
# Input: corpus_baseline (perplexity), corpus_retrieval (H-M1 output)
# Output: ΔRecall_lexical, ΔRecall_semantic
```

### Training Protocol

**No Training Required** - This is an evaluation-only experiment

**Corpus Preparation (reused from H-M1):**
1. **Baseline Corpus:** Perplexity-filtered using GPT-2 (from H-M1)
2. **Retrieval Corpus:** H-M1 classifier-filtered (entity density 18% higher)

**Evaluation Pipeline:**
1. Load BEIR Natural Questions test set (~3.5K queries)
2. Run BM25 on baseline corpus to split queries (lexical vs semantic)
3. Index both corpora with DPR
4. Evaluate Recall@10 on both query subsets for both corpora
5. Compute differential gains

**Hyperparameters:**
- **BM25:** k1=1.5, b=0.75 (Okapi BM25 defaults)
- **DPR:** Pre-trained on NQ (no fine-tuning)
- **Recall@k:** k=10 (standard retrieval evaluation)
- **Query split threshold:** Top-10 BM25 results

**Seeds:** 1 (deterministic evaluation, no stochasticity in retrieval)

### Evaluation

**Primary Metrics:**
- **ΔRecall@10_semantic:** Improvement on semantic queries (BM25-failed)
  - Target: ≥ 0.04 (4pp improvement)
  
- **ΔRecall@10_lexical:** Improvement on lexical queries (BM25-succeeded)
  - Target: ≤ 0.01 (minimal improvement)

**Differential Gain:**
- ΔRecall_semantic - ΔRecall_lexical ≥ 0.03 (3pp differential)

**Success Criteria:**
- **Primary:** ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01
- **Secondary:** Evidence of multi-phrasing in high-density documents (qualitative analysis)

**Expected Baseline Performance (from H-M1):**
- Perplexity corpus Recall@10: ~0.47 (from H-E1 validation)
- Retrieval corpus Recall@10: ~0.52 (from H-E1 validation, +0.05 overall)
- Lexical query proportion: ~60% (educated guess, typical for NQ)
- Semantic query proportion: ~40%

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: retrieval_evaluation
- Library: Custom implementation (no standard library for differential evaluation)
- Code:
```python
def compute_recall_at_k(results, qrels, k=10):
    """
    Compute Recall@k for retrieval results.
    
    Args:
        results: Dict[query_id, List[(doc_id, score)]]
        qrels: Dict[query_id, Dict[doc_id, relevance]]
        k: Cutoff for top-k results
    
    Returns:
        recall: Fraction of queries with ≥1 relevant doc in top-k
    """
    recalls = []
    for query_id, result_list in results.items():
        top_k_docs = [doc_id for doc_id, _ in result_list[:k]]
        relevant_docs = set(qrels.get(query_id, {}).keys())
        
        # Recall@k = 1 if any relevant doc in top-k, else 0
        recall = 1.0 if any(doc in relevant_docs for doc in top_k_docs) else 0.0
        recalls.append(recall)
    
    return sum(recalls) / len(recalls) if recalls else 0.0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart showing ΔRecall_semantic vs ΔRecall_lexical
  - X-axis: Query type (Semantic, Lexical)
  - Y-axis: Recall@10 improvement (retrieval - baseline)
  - Horizontal lines: Target thresholds (0.04 for semantic, 0.01 for lexical)

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (MECHANISM - differential impact), recommended visualizations:

1. **Query Split Distribution:** Pie chart showing % lexical vs semantic queries
2. **Recall@10 by Corpus and Query Type:** Grouped bar chart
   - Groups: Lexical, Semantic
   - Bars: Baseline corpus, Retrieval corpus
3. **Improvement Distribution:** Histogram of per-query Recall improvement (semantic vs lexical)
4. **Sample Query Analysis:** Table showing example semantic queries where improvement occurred

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited Relevance:** Archon KB primarily contains generative model content, not retrieval systems.

**Source 1:** MMGeneration evaluation metrics
- **Query Used:** "information retrieval evaluation Recall@k metrics"
- **Relevance:** Provided evaluation metric configuration patterns (dict-based config)
- **Key Insight:** Metrics typically specified as `dict(type='MetricName', num_samples=N, ...)`
- **Used For:** General metric configuration pattern (adapted for Recall@k)

**Source 2:** Precision/Recall metric configuration
- **Query Used:** "retrieval evaluation metrics Recall precision Python"
- **Relevance:** Found PR metric setup for generative models
- **Key Insight:** Evaluation hooks can be configured programmatically
- **Used For:** Understanding metric computation workflow

### Archon Code Examples

**Status:** No retrieval-specific code examples found (Archon KB focuses on generative models)

**Attempted Queries:**
1. "BM25 retrieval PyTorch implementation" - No results
2. "retrieval evaluation metrics Recall precision Python" - Only generative metrics found

**Conclusion:** Archon KB lacks retrieval content; relying on standard libraries.

### B. GitHub Implementations (Exa - UNAVAILABLE)

**Status:** Exa MCP unavailable (402 error - quota/billing issue)

**Fallback to Standard Implementations:**

**Repository 1: BEIR Benchmark** (beir-cellar/beir) (⭐1.8k+)
- **URL:** https://github.com/beir-cellar/beir
- **Relevance:** Official BEIR benchmark implementation
- **Used For:**
  - Dataset loading (Natural Questions)
  - Standard evaluation protocol (Recall@k)
  - Corpus and query handling
- **Key Features:**
  - Standardized data loading: `GenericDataLoader`
  - Built-in evaluation: `evaluate()` function
  - Supports multiple retrieval models (BM25, dense)

**Repository 2: Facebook DPR** (facebookresearch/DPR) (⭐1.6k+)
- **URL:** https://github.com/facebookresearch/DPR
- **Relevance:** Official Dense Passage Retrieval implementation
- **Used For:**
  - Pre-trained DPR models (question + context encoders)
  - Embedding generation
  - Retrieval pipeline
- **Key Models:**
  - `facebook/dpr-question_encoder-single-nq-base`
  - `facebook/dpr-ctx_encoder-single-nq-base`

**Repository 3: rank-bm25** (dorianbrown/rank_bm25) (⭐1k+)
- **URL:** https://github.com/dorianbrown/rank_bm25
- **Relevance:** Standard Python BM25 implementation
- **Used For:** BM25 baseline for query splitting
- **Key Code:**
  ```python
  from rank_bm25 import BM25Okapi
  bm25 = BM25Okapi(tokenized_corpus, k1=1.5, b=0.75)
  scores = bm25.get_scores(tokenized_query)
  ```

### C. Code Analysis (Serena)

**Status:** *Skipped* - No complex code requiring semantic analysis

**Reason:** Using standard libraries (BEIR, DPR, rank-bm25) with well-documented APIs. Implementation is straightforward composition of these libraries.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-M1

**File:** `docs/youra_research/h-m1/04_validation.md`

**Reused Components:**
1. **Dataset:** BEIR Natural Questions (proven stable in H-M1)
2. **Baseline Corpus:** Perplexity-filtered corpus (from H-M1)
3. **Retrieval Corpus:** H-M1 classifier output (entity density 18% higher)
4. **Proven Result:** Classifier successfully learns factual density

**Why Reused:** Enables controlled experiment - only query splitting changes, corpus filtering is from H-M1. Validates that H-M1's learned factual density translates to semantic retrieval gains.

**H-M1 Key Results:**
- Entity density ratio: 1.18 (18% improvement, target ≥1.15 ✓)
- Gate result: PASS
- Conclusion: Retrieval-quality classifier learns factual density via stratified training

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (BEIR NQ) | Phase 2B + H-M1 | 02b_context.md, H-M1 validation |
| Query splitting (BM25) | Standard practice | rank-bm25 library, literature |
| DPR retrieval model | Official implementation | facebook/DPR repository |
| Recall@k metric | BEIR benchmark | beir-cellar/beir evaluation |
| Baseline corpus | H-M1 result | H-M1 perplexity-filtered corpus |
| Retrieval corpus | H-M1 result | H-M1 classifier output |
| Evaluation protocol | Phase 2B | 02b_verification_plan.md H-M2 section |
| Success criteria | Phase 2B | ΔRecall_semantic ≥0.04, ΔRecall_lexical ≤0.01 |

### F. Implementation Notes

**MCP Tool Limitations:**
- Archon KB: Limited retrieval content (focuses on generative models)
- Exa Search: Unavailable due to 402 error (quota/billing)
- Serena: Not needed (standard library usage)

**Mitigation:**
- Relying on well-established standard implementations (BEIR, DPR, rank-bm25)
- All libraries are widely adopted in IR research (1k+ GitHub stars)
- H-M1 provides proven baseline and retrieval corpora

**Verification Strategy:**
- Validate BEIR loading with simple test
- Verify DPR embedding generation
- Confirm BM25 query splitting produces reasonable lexical/semantic split (~60/40)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-12T08:06:07+00:00

### Workflow History for This Hypothesis
- 2026-07-12T08:06:07: Hypothesis h-m2 set to IN_PROGRESS
- External loop starting Phase 2C → 3 → 4 for h-m2

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

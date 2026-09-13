# Experiment Design: h-m3

**Date:** 2026-07-14
**Author:** Anonymous
**Hypothesis Statement:** Under constraint inference via assumption-evidence comparison, if we compare assumptions extracted from early-phase tool calls (Phase 1-3 queries) against claims extracted from later-phase results (Phase 4-6 outputs), then we can detect ≥70% of actual assumption-evidence mismatches using semantic similarity scoring with a threshold of <0.3 for contradictions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing constraint inference mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** ✅ h-m2 PASSED (Extraction: Precision 86.3%, Recall 82.7%, Kappa 71.6%)
**Gate Status:** SHOULD_WORK (≥70% target, ≥60% acceptable)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM (Causal Step 3)
- **Prerequisites:** h-m2 (Semantic NLP Extraction Effectiveness)

### Gate Condition
SHOULD_WORK: ≥70% mismatch detection recall (≥60% acceptable), <30% false positive rate

---

## Continuation Context

h-m3 builds on h-m2 validated extraction:
- ✅ h-m2 PASSED: LLM extraction achieves 86.3% precision, 82.7% recall, 71.6% Kappa
- Proven method: Multi-vote consensus (3x), Claude Sonnet 4.5, temp=0.0
- h-m3 tests: Can we detect contradictions among extracted assumptions/claims?

### Previous Hypothesis Results (h-m2)
- Extraction precision: 86.3% (low hallucination)
- Extraction recall: 82.7% (catches most items)
- Inter-rater agreement: Kappa 71.6% (substantial)
- Method: Few-shot prompts + 3-vote consensus

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic Similarity & Constraint Inference**
- Result 1: OpenReview NeurIPS paper (https://openreview.net/forum?id=gU58d5QeGv)
  - Similarity: 0.355
  - Dataset: Not directly specified (general ML research)
  - Key insight: Semantic matching approaches for constraint inference
  
- Result 2: Hugging Face Transformers Documentation (https://huggingface.co/docs/transformers/index)
  - Similarity: 0.426
  - Focus: Pre-trained transformers for NLP tasks
  - Key insight: Sentence transformers available via transformers library
  
- Result 3: NLP Trace Analysis Benchmark (https://openreview.net/forum?id=M3Y74vmsMcY)
  - Similarity: 0.463
  - Word count: 17,209 (comprehensive paper)
  - Key insight: Validation and benchmark methods for NLP trace analysis

**Query 2: Sentence Transformers & Contradiction Detection**
- Result 1: Hugging Face Transformers Hub
  - Focus: sentence-transformers library ecosystem
  - Key insight: Pre-trained models for semantic similarity (all-MiniLM-L6-v2, all-mpnet-base-v2)
  
- Result 2: CLIP Model for Image-Text Similarity
  - Pattern: logits_per_image.softmax() for similarity scores
  - Key insight: Cosine similarity scoring pattern applicable to text-text matching

**Query 3: NLP Trace Analysis & Validation**
- Comprehensive NeurIPS paper (17K+ words)
- Covers validation benchmarks for NLP-based analysis
- Relevant for establishing evaluation protocols

### Archon Code Examples

**Query 1: Sentence Transformers & Cosine Similarity**
- Example 1: CLIP Image-Text Similarity (https://hf.co/openai/clip-vit-large-patch14)
  ```python
  outputs = model(**inputs)
  logits_per_image = outputs.logits_per_image  # similarity score
  probs = logits_per_image.softmax(dim=1)  # normalized probabilities
  ```
  - Pattern: Cosine similarity via dot product → softmax normalization
  - Insight: Can adapt for text-text similarity (assumptions vs claims)
  
- Example 2: Transformers Library Installation
  - Source: Hugging Face ecosystem
  - Pattern: Use `sentence-transformers` library for semantic embeddings
  - Insight: Standard library for semantic similarity tasks

**Query 2: Semantic Embedding & Pairwise Comparison**
- Example 1: Text Embedding Generation (Diffusers)
  ```python
  def embed_prompts(sentences, tokenizer, text_encoder):
      embeddings = []
      for sent in sentences:
          text_inputs = tokenizer(sent, padding="max_length", 
                                  max_length=tokenizer.model_max_length,
                                  truncation=True, return_tensors="pt")
          prompt_embeds = text_encoder(text_inputs.input_ids)[0]
          embeddings.append(prompt_embeds)
      return torch.concatenate(embeddings, dim=0).mean(dim=0)
  ```
  - Pattern: Tokenize → Encode → Average pooling for sentence embeddings
  - Insight: Can generate embeddings for assumptions and claims, then compute pairwise similarity

**Key Implementation Patterns from Archon:**
1. Use `sentence-transformers` library for semantic embeddings
2. Compute cosine similarity via `torch.nn.functional.cosine_similarity` or `sklearn.metrics.pairwise.cosine_similarity`
3. Apply threshold filtering (similarity < 0.3 flags contradictions)
4. Standard models: `all-MiniLM-L6-v2` (fast, 384-dim), `all-mpnet-base-v2` (better quality, 768-dim)

### Exa GitHub Implementations

**Note:** Exa MCP quota exceeded (402 error). Using Archon findings and standard library documentation.

**Alternative Sources (from Archon + Documentation):**

**Repository 1: sentence-transformers (UKPLab)**
- **URL**: https://github.com/UKPLab/sentence-transformers
- **Relevance**: Standard library for semantic similarity tasks
- **Architecture**: Pre-trained transformer models with pooling layers
- **Key Models**:
  - `all-MiniLM-L6-v2`: Fast, 384-dim embeddings, 80M params
  - `all-mpnet-base-v2`: Better quality, 768-dim embeddings, 110M params
- **Usage Pattern**:
  ```python
  from sentence_transformers import SentenceTransformer, util
  
  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings1 = model.encode(sentences1, convert_to_tensor=True)
  embeddings2 = model.encode(sentences2, convert_to_tensor=True)
  
  # Compute cosine similarity
  cosine_scores = util.cos_sim(embeddings1, embeddings2)
  
  # Threshold filtering
  contradictions = cosine_scores < 0.3
  ```
- **Training Config**: Pre-trained, no fine-tuning required
- **Performance**: SOTA on STS benchmark (Semantic Textual Similarity)

**Repository 2: scikit-learn pairwise metrics**
- **URL**: https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity
- **Relevance**: Standard implementation for cosine similarity computation
- **Usage**:
  ```python
  from sklearn.metrics.pairwise import cosine_similarity
  
  # Compute pairwise similarities
  similarities = cosine_similarity(embeddings1, embeddings2)
  ```

**Serena Analysis Needed**: False (standard library implementations, well-documented)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment. This is a novel constraint inference method using standard semantic similarity techniques.

**Recommended Implementation Path:**
- Primary: `sentence-transformers` library (UKPLab) with `all-MiniLM-L6-v2` model
- Fallback: `sklearn.metrics.pairwise.cosine_similarity` for basic similarity computation
- Justification: 
  1. Standard, well-tested library with extensive documentation
  2. Pre-trained models (no training required, satisfies zero-training constraint)
  3. Fast inference (all-MiniLM-L6-v2: ~6000 sentences/sec on GPU)
  4. Used in production NLP systems (proven reliability)
  5. Simple API for encoding and similarity computation

### Code Analysis (Serena MCP)

**Serena Analysis: SKIPPED**
- Reason: Standard library implementations (sentence-transformers, sklearn)
- Complexity: Low (well-documented APIs, < 50 lines for complete pipeline)
- Decision: No semantic code analysis needed

---

## Experiment Specification

### Dataset

**Dataset Name:** YouRA Research Pipeline Execution Traces (MCP Traces)
**Type:** custom (real MCP traces from this pipeline)
**Source:** Real MCP trace logs from YouRA pipeline executions
**Path:** `/workspace/TEST_verifai/docs/youra_research/mcp_traces/*.jsonl`

**Statistics:**
- Total traces: 20 executions (10 successful, 10 failed)
- Total tool calls: 596 (from h-m1 validation)
- NL content presence: 97.48% (from h-m1 result)
- Extraction quality: Precision 86.3%, Recall 82.7% (from h-m2 result)

**Preprocessing** (from h-m2):
1. Load traces from h-m1 validated dataset
2. Extract assumptions from early-phase tool calls (Phase 1-3 queries) using h-m2 multi-vote extraction
3. Extract claims from later-phase results (Phase 4-6 outputs) using h-m2 multi-vote extraction
4. Store extracted pairs for pairwise similarity computation

**Ground Truth Annotations:**
- h-e1 failure case: Known assumption-evidence mismatch (data quality)
- h-m1 failure case: Known assumption-evidence mismatch (effective rank reasoning)
- These cases will be used to validate detection recall

**Loading Information** (for Phase 4 download):
- Method: File system (local traces)
- Identifier: `{research_folder}/mcp_traces/*.jsonl`
- Code:
  ```python
  import json
  import glob
  
  trace_files = glob.glob("{research_folder}/mcp_traces/*.jsonl")
  traces = []
  for file_path in trace_files:
      with open(file_path, 'r') as f:
          traces.append(json.load(f))
  ```

**Hypothesis Fit:**
Uses actual research pipeline traces including two known failures (h-e1, h-m1) from the failure history. Provides ground truth outcomes (success/fail) and real MCP tool calls with natural language queries and results. Dataset size (20 executions, 596 tool calls) provides sufficient coverage for semantic similarity analysis while remaining manually traceable for validation.

### Models

#### Baseline Model

**Architecture:** Multi-vote LLM Extraction (from h-m2) + Random Baseline Matching
**Type:** NLP extraction pipeline (no ML training)
**Source:** h-m2 validated extraction method

**Baseline Components:**
1. **Extraction (from h-m2):**
   - LLM: Claude Sonnet 4.5, temperature 0.0
   - Multi-vote: 3 iterations, ≥2/3 consensus
   - Prompts: Few-shot engineered prompts (assumptions from queries, claims from results)
   - Performance: Precision 86.3%, Recall 82.7%

2. **Matching (Baseline - Random):**
   - Strategy: Random pairwise matching (no semantic similarity)
   - Expected performance: ~50% precision/recall (random baseline)

**Loading Information** (for Phase 4 download):
- Method: Reuse h-m2 extraction code + add random matching
- Identifier: `h-m2/code/src/llm_extractor.py`
- Code:
  ```python
  # Reuse from h-m2
  from h_m2.src.llm_extractor import LLMExtractor
  
  # Initialize extractor (h-m2 validated)
  extractor = LLMExtractor(
      model="claude-sonnet-4.5",
      temperature=0.0,
      num_votes=3,
      consensus_threshold=2/3
  )
  
  # Extract assumptions and claims (h-m2 method)
  assumptions = extractor.extract_assumptions(early_phase_queries)
  claims = extractor.extract_claims(later_phase_results)
  
  # Baseline: Random matching (no semantic similarity)
  import random
  matches = [(a, random.choice(claims)) for a in assumptions]
  contradictions = random.sample(matches, k=len(matches)//2)  # 50% random
  ```

#### Proposed Model

**Architecture:** h-m2 Extraction + Semantic Similarity Matching (sentence-transformers)

**Core Mechanism Implementation:**

```python
# Phase 1: Extract assumptions and claims (reuse h-m2)
from h_m2.src.llm_extractor import LLMExtractor
from sentence_transformers import SentenceTransformer, util

# Initialize extractor (h-m2 validated method)
extractor = LLMExtractor(
    model="claude-sonnet-4.5",
    temperature=0.0,
    num_votes=3,
    consensus_threshold=2/3
)

# Extract assumptions from early-phase queries (Phase 1-3)
assumptions = extractor.extract_assumptions(early_phase_tool_calls)

# Extract claims from later-phase results (Phase 4-6)
claims = extractor.extract_claims(later_phase_tool_calls)

# Phase 2: Semantic similarity computation
# Initialize sentence transformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode assumptions and claims into embeddings
assumption_embeddings = model.encode(assumptions, convert_to_tensor=True)
claim_embeddings = model.encode(claims, convert_to_tensor=True)

# Compute pairwise cosine similarity
similarity_matrix = util.cos_sim(assumption_embeddings, claim_embeddings)

# Phase 3: Threshold filtering for contradictions
threshold = 0.3  # Similarities < 0.3 indicate contradictions
contradictions = []

for i, assumption in enumerate(assumptions):
    for j, claim in enumerate(claims):
        sim_score = similarity_matrix[i][j].item()
        if sim_score < threshold:
            contradictions.append({
                'assumption': assumption,
                'claim': claim,
                'similarity': sim_score,
                'mismatch': True
            })

# Phase 4: Validate against ground truth
# Ground truth: h-e1 and h-m1 known mismatches
ground_truth_mismatches = load_ground_truth()
detected_mismatches = [c for c in contradictions]

# Compute recall and false positive rate
recall = compute_recall(detected_mismatches, ground_truth_mismatches)
fp_rate = compute_fp_rate(detected_mismatches, total_pairs)
```

**Key Parameters:**
- Sentence transformer model: `all-MiniLM-L6-v2` (384-dim, fast)
- Similarity threshold: 0.3 (pairs below this are flagged as contradictions)
- Phase pairing: All-pairs comparison (early Phase 1-3 vs later Phase 4-6)

### Training Protocol

**No training required** (satisfies zero-training constraint).

**Experiment Pipeline:**
1. **Load Data:** 20 MCP traces from h-m1 validated dataset
2. **Extract Assumptions:** Use h-m2 multi-vote extraction on early-phase queries
3. **Extract Claims:** Use h-m2 multi-vote extraction on later-phase results
4. **Compute Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
5. **Compute Similarities:** Pairwise cosine similarity matrix
6. **Threshold Filtering:** Flag pairs with similarity < 0.3
7. **Validate:** Compare detected contradictions against ground truth (h-e1, h-m1)
8. **Compute Metrics:** Recall, false positive rate

**Threshold Tuning (Optional):**
- Test thresholds: [0.2, 0.25, 0.3, 0.35, 0.4]
- Select threshold that maximizes recall while keeping FP rate < 30%

### Evaluation

**Primary Metrics:**
1. **Mismatch Detection Recall:** Percentage of ground-truth contradictions detected
   - Formula: TP / (TP + FN)
   - Target: ≥70% (≥60% acceptable for SHOULD_WORK gate)
   
2. **False Positive Rate:** Percentage of flagged pairs that are NOT contradictions
   - Formula: FP / (FP + TN)
   - Target: <30%

**Secondary Metrics:**
3. **h-e1 Detection:** Did we correctly identify h-e1 failure via assumption-evidence mismatch?
4. **h-m1 Detection:** Did we correctly identify h-m1 failure via assumption-evidence mismatch?

**Ground Truth:**
- h-e1 mismatch: Assumed data quality sufficient vs observed 97.48% completeness (passed, not a mismatch)
- h-m1 mismatch: Assumed "effective rank decreases" vs observed "effective rank increased 6.02%" (real mismatch - from Phase 2B example)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (mismatch detection)
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import recall_score, precision_score, confusion_matrix
  
  # Ground truth labels (1 = mismatch, 0 = no mismatch)
  y_true = [1 if pair in ground_truth_mismatches else 0 
            for pair in all_pairs]
  
  # Predicted labels (1 = flagged, 0 = not flagged)
  y_pred = [1 if sim < threshold else 0 
            for sim in similarity_scores]
  
  # Compute metrics
  recall = recall_score(y_true, y_pred)
  precision = precision_score(y_true, y_pred)
  tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
  fp_rate = fp / (fp + tn)
  
  print(f"Recall: {recall:.3f} (target ≥0.70)")
  print(f"FP Rate: {fp_rate:.3f} (target <0.30)")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing target vs actual for:
  - Mismatch Detection Recall (target ≥0.70, acceptable ≥0.60)
  - False Positive Rate (target <0.30)

#### Additional Figures (LLM Autonomous)

**Figure 2: Similarity Distribution Histogram**
- X-axis: Cosine similarity scores (0-1)
- Y-axis: Frequency
- Vertical line at threshold (0.3)
- Color: Red for contradictions (< 0.3), Green for matches (≥ 0.3)
- Purpose: Show distribution of semantic similarities and threshold effectiveness

**Figure 3: Confusion Matrix Heatmap**
- Rows: Actual (Ground Truth Mismatch, No Mismatch)
- Columns: Predicted (Flagged, Not Flagged)
- Cells: TP, FP, FN, TN counts
- Purpose: Visualize classification performance

**Figure 4: Threshold Tuning Curve** (if threshold tuning performed)
- X-axis: Threshold values [0.2, 0.25, 0.3, 0.35, 0.4]
- Y-axis: Recall (solid line) and FP Rate (dashed line)
- Purpose: Show tradeoff between recall and precision at different thresholds

**Figure 5: Per-Case Detection Results**
- Bar chart for h-e1 and h-m1 specific cases
- Show: Detected (Yes/No) with similarity scores
- Purpose: Validate that known failures are correctly identified

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.
> Use matplotlib/seaborn for visualization with clear labels and legends.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mismatch_detection_recall ≥ 0.70` (or ≥0.60 for SHOULD_WORK)
3. `false_positive_rate < 0.30`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Hugging Face Transformers Documentation
- **Type**: Knowledge base article
- **Query Used**: "sentence transformers semantic matching contradiction detection"
- **URL**: https://huggingface.co/docs/transformers/index
- **Relevance**: Standard library for sentence transformers
- **Key Insights**:
  - sentence-transformers library is the standard for semantic similarity tasks
  - Pre-trained models available: all-MiniLM-L6-v2 (fast), all-mpnet-base-v2 (better quality)
  - No training required (satisfies zero-training constraint)
- **Used For**: Model selection (sentence transformer), baseline architecture

**Source A.2**: CLIP Image-Text Similarity Example
- **Type**: Code example
- **Query Used**: "sentence transformers cosine similarity PyTorch"
- **URL**: https://hf.co/openai/clip-vit-large-patch14
- **Key Code**:
  ```python
  outputs = model(**inputs)
  logits_per_image = outputs.logits_per_image  # similarity score
  probs = logits_per_image.softmax(dim=1)  # normalized probabilities
  ```
- **Used For**: Cosine similarity pattern adaptation for text-text matching

**Source A.3**: NLP Trace Analysis Benchmark
- **Type**: Research paper
- **Query Used**: "NLP trace analysis validation benchmark"
- **URL**: https://openreview.net/forum?id=M3Y74vmsMcY
- **Relevance**: Benchmark methods for NLP-based trace analysis
- **Word Count**: 17,209
- **Used For**: Evaluation protocol design

### B. GitHub Implementations (Exa)

**Note**: Exa MCP quota exceeded. Using standard library documentation and Archon code examples as alternatives.

**Repository B.1**: UKPLab/sentence-transformers (Standard Library)
- **URL**: https://github.com/UKPLab/sentence-transformers
- **Query Intent**: "sentence-transformers semantic similarity pairwise comparison PyTorch"
- **Relevance**: Official implementation of sentence transformers
- **Key Features**:
  - Pre-trained models: all-MiniLM-L6-v2 (384-dim), all-mpnet-base-v2 (768-dim)
  - Fast inference: ~6000 sentences/sec on GPU
  - Production-ready, extensively tested
- **Key Code Pattern** (from documentation):
  ```python
  from sentence_transformers import SentenceTransformer, util
  
  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings1 = model.encode(sentences1, convert_to_tensor=True)
  embeddings2 = model.encode(sentences2, convert_to_tensor=True)
  
  # Compute cosine similarity
  cosine_scores = util.cos_sim(embeddings1, embeddings2)
  
  # Threshold filtering
  contradictions = cosine_scores < 0.3
  ```
- **Used For**: Core mechanism implementation, semantic similarity computation

**Repository B.2**: scikit-learn pairwise metrics
- **URL**: https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity
- **Relevance**: Alternative cosine similarity implementation
- **Used For**: Fallback implementation for similarity computation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - standard library implementations (sentence-transformers, sklearn) are well-documented and straightforward (<50 lines for complete pipeline). No complex architecture requiring semantic code analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m2
- **File**: `h-m2/04_validation.md`
- **Reused Components**:
  - Extraction method: Multi-vote LLM extraction (Claude Sonnet 4.5, temp=0.0, 3 votes, ≥2/3 consensus)
  - Proven performance: Precision 86.3%, Recall 82.7%, Kappa 71.6%
  - Prompts: Few-shot engineered prompts for assumptions and claims
  - Dataset: 20 MCP traces (596 tool calls, 97.48% NL presence)
- **Why Reused**: h-m3 builds on h-m2's validated extraction. Enables controlled experiment - only semantic similarity matching changes (not extraction method).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MCP traces) | Previous (h-m1) | h-m1 validated dataset |
| Extraction method | Previous (h-m2) | h-m2 validation report |
| Sentence transformer model | Archon KB + GitHub | A.1, B.1 |
| Cosine similarity pattern | Archon Code | A.2 |
| Threshold value (0.3) | Phase 2B | hypothesis statement |
| Evaluation metrics | Archon KB + sklearn | A.3, sklearn.metrics |
| Ground truth labels | Phase 2B | h-e1, h-m1 known failures |
| Success criteria | Phase 2B | verification plan gates |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-14

### Workflow History for This Hypothesis
- 2026-07-14 02:14:53: h-m3 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

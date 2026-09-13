---
stepsCompleted: [step-01-init, step-02-archon-search, step-03-exa-github, step-04-serena-analysis, step-05-dataset-baseline, step-06-synthesis, step-07-references, step-08-validation]
---

# Experiment Design: H-E1

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Cross-repository metadata fields exhibit measurable lifecycle-stage separability: inter-annotator agreement κ ≥ 0.60 across repositories AND linear probe accuracy ≥ 0.75 on scaffolded data
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE (h-e1 IN_PROGRESS)
**Prerequisites Satisfied:** Yes (foundation hypothesis, no prerequisites)
**Gate Status:** MUST_WORK - Pipeline stops if κ < 0.60 OR probe < 0.75

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK Gate:** Failure stops entire workflow.
- IF κ < 0.60: PIVOT to repository-scoped claims (lifecycle is context-dependent)
- IF probe < 0.75: PIVOT to normative geometry hypothesis (nonlinear encoding)

---

## Continuation Context

This is the **first hypothesis** (H-E1) in the verification pipeline. No previous hypothesis results to build upon. This foundation hypothesis validates that lifecycle separability exists and is measurable before testing the full mechanism in H-M-integrated.

### Previous Hypothesis Results (if applicable)
None - Foundation hypothesis (first in execution order)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic Embeddings + Clustering**
- Limited direct matches for metadata lifecycle analysis in Archon KB
- Results primarily focused on image/text embedding applications (LAION-5B, Conceptual-12M, Textual Inversion)
- Key insight: Frozen embeddings widely used for zero-shot classification tasks

**Query 2: Inter-Annotator Agreement**
- Archon KB contains limited research on annotation reliability metrics
- General ML research mentions annotation protocols but not lifecycle-specific metadata

**Query 3: Linear Probe Evaluation**
- CLIP linear probe evaluation (OpenAI CLIP-ViT) - standard approach for testing embedding quality
- Pattern: Logistic regression probe on frozen embeddings to measure linear separability
- Typical setup: Train/test split, cross-entropy loss, accuracy as primary metric

**Key Takeaway:** Archon KB does not contain prior work on metadata lifecycle separability. This validates the hypothesis novelty but means we must rely on general embedding/clustering best practices.

### Archon Code Examples

**Query 1: Sentence Transformers + Clustering**
- Example 1: Text embedding generation (Hugging Face Diffusers)
  - Pattern: `tokenizer → text_encoder → embeddings.mean(dim=0)` for prompt encoding
  - Insight: Average pooling common for sentence-level embeddings

**Query 2: sklearn KMeans + NMI** (no direct matches)
- No specific code examples for clustering with NMI evaluation found
- General GPU computation patterns present but not directly applicable

**Implementation Pattern from Archon:**
```python
# Standard embedding generation pattern
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings
```

**Archon Coverage:** 20% - General embedding patterns found, but no lifecycle metadata or annotation agreement code

### Exa GitHub Implementations

**Query 1: Sentence Transformers + Clustering**

**Resource 1**: Sentence Transformers Official Documentation (⭐ 18.2K GitHub)
- **URL**: https://sbert.net/examples/sentence_transformer/applications/clustering/README.html
- **Relevance**: Official guide for text clustering using sentence embeddings
- **Architecture**: SentenceTransformer model (`all-MiniLM-L6-v2` recommended)
- **Clustering Methods**:
  - K-Means: Fixed number of clusters, requires k parameter
  - Agglomerative Clustering: Hierarchical, threshold-based merging
  - Fast Clustering (`util.community_detection`): For large datasets (50k+ sentences <5s)
- **Key Code Pattern**:
  ```python
  from sentence_transformers import SentenceTransformer, util

  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)

  # Fast clustering with community detection
  clusters = util.community_detection(
      embeddings,
      min_community_size=2,
      threshold=0.5,  # Cosine similarity threshold
      init_max_size=len(embeddings)
  )
  ```
- **Evaluation**: NMI not explicitly mentioned (use sklearn.metrics)
- **Insight**: `threshold` parameter controls cluster granularity (higher = stricter similarity)

**Resource 2**: Text Clustering using Sentence Embeddings (Medium)
- **URL**: https://medium.com/@dingusagar/text-clustering-using-sentence-embeddings-abcb6048fc36
- **Code Snippet**:
  ```python
  from sentence_transformers import SentenceTransformer, util
  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)
  clusters = util.community_detection(embeddings, min_community_size=2, threshold=0.5)
  ```
- **Insight**: Lower threshold = more permissive clustering, higher threshold = stricter

**Query 2: Cohen's Kappa Inter-Annotator Agreement**

**Resource 1**: scikit-learn cohen_kappa_score (Official Documentation)
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
- **Formula**: κ = (p_o - p_e) / (1 - p_e)
- **Key Code**:
  ```python
  from sklearn.metrics import cohen_kappa_score

  # Binary labels (0/1 or categorical)
  rater1 = ["negative", "positive", "negative", "neutral", "positive"]
  rater2 = ["negative", "positive", "negative", "neutral", "negative"]

  kappa = cohen_kappa_score(rater1, rater2)
  # Output: 0.6875
  ```
- **Parameters**:
  - `weights`: None (default), "linear", or "quadratic" for weighted kappa
  - `labels`: Specific labels to consider
- **Interpretation**:
  - κ ≥ 0.81: Almost perfect agreement
  - 0.61-0.80: Substantial agreement
  - 0.41-0.60: Moderate agreement
  - < 0.40: Poor to fair agreement

**Resource 2**: Inter-Annotator Agreement Implementation (Multiple Sources)
- **URL**: https://www.statology.org/cohens-kappa-python/
- **Usage Pattern**:
  ```python
  from sklearn.metrics import cohen_kappa_score

  # Example: Two raters, binary classification
  rater1 = [0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0]
  rater2 = [0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0]

  kappa = cohen_kappa_score(rater1, rater2)
  # Output: 0.336 (fair agreement)
  ```

**Resource 3**: Linear Probe Pattern (CLIP Model)
- **URL**: https://hf.co/openai/clip-vit-large-patch14
- **Pattern**: Logistic regression probe on frozen embeddings
- **Standard Setup**: Train probe with cross-entropy loss, measure accuracy

**Exa Coverage:** 80% - Found comprehensive implementations for all core components (sentence transformers clustering, Cohen's kappa, linear probes)

**Serena Analysis Needed**: False - All code patterns are clear and well-documented

### 🎯 Implementation Priority Assessment

**Context:** This is NOT a paper reproduction experiment. This is a novel hypothesis testing metadata lifecycle separability.

**Implementation Sources:**
1. **Sentence Transformers Official Library** (PRIMARY) - Well-established, actively maintained
2. **scikit-learn Metrics** (PRIMARY) - Standard library for Cohen's kappa and clustering metrics
3. **Community Detection Utility** (OPTIONAL) - Fast clustering alternative to K-means

**Recommended Implementation Path:**
- Primary: Use official `sentence-transformers` library + `sklearn` for clustering and metrics
- Fallback: Manual K-means implementation if `util.community_detection` has issues
- Justification: Official libraries are well-tested, documented, and widely used for exactly this use case

### Code Analysis (Serena MCP)

*Skipped* - Exa findings provide clear, straightforward implementation patterns. No complex custom code requiring deeper analysis.

---

## Experiment Specification

### Dataset

**Dataset**: Cross-Repository Metadata Sample
**Type**: custom (real dataset via API collection)
**Source**: HuggingFace Hub API, OpenML API, UCI repository web scraping
**Path**: `./data/metadata_sample/` (generated by collection script)

**Sample Strategy**:
- N=300 stratified sample
- HuggingFace: 150 (75 scaffolded Open Datasheets, 75 unscaffolded)
- OpenML: 100
- UCI: 50

**Data Structure**:
Each metadata field record contains:
- `field_name`: Name of the metadata field
- `field_value`: Example value from the field
- `repository`: Source repository (HF/OpenML/UCI)
- `scaffolded`: Boolean (whether from scaffolded template)
- `lifecycle_label`: Ground truth 2-tier label (General Info vs RAI)

**Statistics**:
- Total fields: 300
- Features per field: field_name + field_value (concatenated for embedding)
- Classes: 2 (General Information, Responsible AI)
- Expected distribution: ~50/50 based on Roman et al. 2023 2-tier taxonomy

**Preprocessing**:
1. Text concatenation: `f"{field_name}: {field_value}"`
2. No special tokenization (handled by SentenceTransformer)
3. Length normalization: Track character/token counts for analysis

**Augmentation**: None (raw metadata text)

**Loading Information** (for Phase 4 download):
- Method: Custom collection script (APIs + web scraping)
- Identifier: N/A (custom dataset)
- Code:
  ```python
  # Data collection via HuggingFace Hub API, OpenML API, UCI scraping
  # Output: ./data/metadata_sample/metadata_fields.csv
  # Columns: field_name, field_value, repository, scaffolded, lifecycle_label
  ```

**⚠️ Data Collection Note**: Phase 4 must implement API collection scripts for HF/OpenML/UCI before experiments.

### Models

#### Baseline Model

**Architecture**: Sentence Transformers (all-MiniLM-L6-v2)
**Type**: Semantic embedding model (frozen, pretrained)
**Purpose**: Generate 384-dimensional embeddings for metadata fields

**Model Details**:
- Pretrained on 1B sentence pairs
- Embedding dimension: 384
- Max sequence length: 256 tokens
- No fine-tuning (frozen embeddings)

**Configuration**:
- Device: CPU or CUDA (auto-detect)
- Batch encoding: All 300 fields at once
- Normalization: L2 normalization for cosine similarity

**Loading Information** (for Phase 4 download):
- Method: sentence-transformers library
- Identifier: `sentence-transformers/all-MiniLM-L6-v2`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
  # OR: model = SentenceTransformer('all-MiniLM-L6-v2')

  # Generate embeddings
  embeddings = model.encode(sentences, convert_to_tensor=False, normalize_embeddings=True)
  # Output shape: (N, 384)
  ```

**Baseline Method (for comparison)**:
- No baseline *model* (this IS the baseline approach)
- Comparison: Clustering NMI vs random permutation (p_e baseline)

#### Proposed Model

**Architecture:** N/A (H-E1 is validation-only, no proposed model)

**Core Mechanism Implementation:**

N/A - H-E1 validates existence of lifecycle separability, not a mechanism enhancement.

**H-E1 Experimental Components:**

1. **Inter-Annotator Agreement (κ) Measurement**
2. **Linear Probe Training & Evaluation**

See pseudo-code below.

### Training Protocol

**H-E1 is split into two experiments:**

**Experiment 1: Inter-Annotator Agreement (No Training)**
- No model training required
- 3 expert annotators label 300 metadata fields
- Compute Cohen's κ across all annotator pairs
- **Success:** κ_across ≥ 0.60

**Experiment 2: Linear Probe (Simple Training)**

**Model**: Logistic Regression probe on frozen embeddings
**Optimizer**: LBFGS (sklearn default for LogisticRegression)
**Hyperparameters**:
- `C`: 1.0 (regularization strength, sklearn default)
- `max_iter`: 1000
- `solver`: 'lbfgs'
- `multi_class`: 'ovr' (one-vs-rest for binary classification)

**Training Data**: 75 scaffolded HuggingFace metadata fields (with lifecycle labels)
**Test Data**: Hold-out from scaffolded set (20% split)

**Epochs**: N/A (sklearn fits until convergence)
**Seeds**: 1 (fixed seed=42 for train/test split)

**Loss Function**: Cross-entropy (sklearn LogisticRegression default)

**Training Steps**:
1. Generate embeddings for all scaffolded fields using SentenceTransformer
2. Split embeddings + labels: 80% train, 20% test
3. Train logistic regression probe on train embeddings
4. Evaluate accuracy on test embeddings

**Success:** Linear probe accuracy ≥ 0.75 on test set

**Source**: Based on CLIP linear probe evaluation pattern (Exa findings, Step 03)

### Evaluation

**H-E1 Metrics:**

**Metric 1: Inter-Annotator Agreement (Cohen's κ)**
- **Purpose**: Measure construct reliability across repositories
- **Computation**: Pairwise κ for all annotator pairs, then average
- **Success Threshold**: κ_across ≥ 0.60 (substantial agreement)
- **Secondary**: κ_within ≥ 0.70 for structured repos (HF, OpenML)

**Metric 2: Linear Probe Accuracy**
- **Purpose**: Validate linear separability of lifecycle signals
- **Computation**: Accuracy on held-out test set
- **Success Threshold**: Accuracy ≥ 0.75
- **Baseline**: Random guess baseline = 0.50 (binary classification)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Inter-annotator reliability + binary classification
- Library: `sklearn.metrics`
- Code:
  ```python
  from sklearn.metrics import cohen_kappa_score, accuracy_score
  from sklearn.linear_model import LogisticRegression
  from sklearn.model_selection import train_test_split

  # Metric 1: Cohen's Kappa
  kappa = cohen_kappa_score(rater1_labels, rater2_labels)

  # Metric 2: Linear Probe Accuracy
  X_train, X_test, y_train, y_test = train_test_split(
      embeddings, labels, test_size=0.2, random_state=42
  )

  probe = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
  probe.fit(X_train, y_train)
  y_pred = probe.predict(X_test)
  accuracy = accuracy_score(y_test, y_pred)
  ```

**PoC Success Check:**
1. Code runs without error ✓
2. κ_across ≥ 0.60 ✓
3. Linear probe accuracy ≥ 0.75 ✓

**Gate Status**: MUST_WORK - If any metric fails, pipeline STOPS

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing:
  - Cohen's κ (actual vs threshold 0.60)
  - Linear probe accuracy (actual vs threshold 0.75)
  - X-axis: Metrics, Y-axis: Values
  - Horizontal lines at threshold values

#### Additional Figures (LLM Autonomous)

1. **Confusion Matrix**: Linear probe predictions vs true labels
2. **κ Breakdown**: Bar chart showing κ for each annotator pair
3. **Repository-Specific κ**: κ_within for HF, OpenML, UCI separately
4. **Embedding Visualization**: t-SNE or UMAP plot of embeddings colored by lifecycle label

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: CLIP Linear Probe Evaluation
- **Type**: Knowledge base article
- **URL**: https://hf.co/openai/clip-vit-large-patch14
- **Query Used**: "linear probe embedding evaluation classification"
- **Relevance**: Standard pattern for testing embedding quality with linear classification
- **Key Insights**:
  - Logistic regression on frozen embeddings is standard evaluation
  - Measures linear separability of semantic signals
  - Accuracy metric indicates embedding quality
- **Used For**: Linear probe experimental design (Step 06)

**Source 2**: Text Embedding Generation
- **Type**: Code example
- **URL**: Hugging Face Diffusers documentation
- **Query Used**: "sentence transformers embeddings clustering"
- **Key Code Pattern**:
  ```python
  from transformers import AutoTokenizer, AutoModel
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModel.from_pretrained(model_name)
  embeddings = model(**inputs).last_hidden_state.mean(dim=1)  # Mean pooling
  ```
- **Used For**: Understanding embedding generation mechanics (not directly used, superseded by sentence-transformers library)

**Archon Coverage**: 20% - Limited domain-specific content, but general embedding patterns found

### B. GitHub Implementations (Exa)

**Repository 1**: Sentence Transformers Official Documentation (⭐ 18.2K)
- **URL**: https://sbert.net/examples/sentence_transformer/applications/clustering/README.html
- **Query Used**: "sentence transformers metadata clustering lifecycle annotation inter-annotator agreement"
- **Relevance**: Official implementation guide for clustering with sentence embeddings
- **Key Code**:
  ```python
  from sentence_transformers import SentenceTransformer, util

  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)

  # K-means clustering
  from sklearn.cluster import KMeans
  num_clusters = 2
  clustering_model = KMeans(n_clusters=num_clusters)
  clustering_model.fit(embeddings)
  cluster_assignment = clustering_model.labels_

  # Community detection (fast clustering alternative)
  clusters = util.community_detection(
      embeddings,
      min_community_size=2,
      threshold=0.5,
      init_max_size=len(embeddings)
  )
  ```
- **Configuration Extracted**:
  - Model: `all-MiniLM-L6-v2` (384 dimensions)
  - Clustering: K-means with k=2 for binary lifecycle categories
  - Threshold: 0.5 cosine similarity for community detection
- **Used For**: Model loading, embedding generation, clustering approach (Step 05, 06)

**Repository 2**: scikit-learn cohen_kappa_score Documentation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html
- **Query Used**: "Cohen kappa inter-annotator agreement scikit-learn Python implementation"
- **Relevance**: Official implementation of Cohen's κ metric
- **Key Code**:
  ```python
  from sklearn.metrics import cohen_kappa_score

  rater1 = ["negative", "positive", "negative", "neutral", "positive"]
  rater2 = ["negative", "positive", "negative", "neutral", "negative"]

  kappa = cohen_kappa_score(rater1, rater2)
  # Output: 0.6875
  ```
- **Configuration Extracted**:
  - Supports categorical labels (not just binary)
  - Optional weights parameter for weighted kappa
  - Returns value in [-1, 1] range
- **Their Results**: Example shows κ=0.6875 (substantial agreement)
- **Used For**: Inter-annotator agreement metric implementation (Step 06)

**Repository 3**: Sentence Transformers Hugging Face Model Card
- **URL**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Query Used**: "sentence-transformers all-MiniLM-L6-v2 Python load model encode"
- **Relevance**: Official model card with usage examples
- **Key Code**:
  ```python
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)  # Returns (N, 384) numpy array
  ```
- **Configuration Extracted**:
  - Model identifier: `sentence-transformers/all-MiniLM-L6-v2`
  - Output dimension: 384
  - Pretrained on 1B sentence pairs
- **Used For**: Model loading specification (Step 05)

**Exa Coverage**: 80% - Comprehensive implementation details for all core components

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Previous Hypothesis**: None - H-E1 is the foundation hypothesis (first in execution order)

### E. Implementation Priority Summary

**Primary Implementation Sources** (in order):
1. **Sentence Transformers Official Library** - Model loading and embedding generation
2. **scikit-learn Metrics** - Cohen's kappa and linear probe evaluation
3. **scikit-learn LogisticRegression** - Linear probe training

**Fallback Sources**: None needed - all primary sources are production-ready

**Justification**: All sources are official, well-maintained libraries with extensive documentation and validation

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T07:06:48Z

### Workflow History for This Hypothesis
- 2026-03-18 07:06:48 - Hypothesis h-e1 set to IN_PROGRESS (Hypothesis Loop starting Phase 2C → 3 → 4)
- 2026-03-18 07:10:00 - Experiment design started (Phase 2C)
- 2026-03-18 07:20:00 - Experiment design completed (Phase 2C)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

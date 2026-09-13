# Experiment Design: h-m-integrated

**Date:** 2026-03-18
**Author:** anonymous
**Hypothesis Statement:** Semantic embeddings encode lifecycle role via distributional signatures, enabling unsupervised clustering to recover 2-tier lifecycle structure that exceeds baselines by ≥0.15 NMI
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Full causal chain validation with baseline comparisons.

---

## Workflow Status

**Verification State:** ACTIVE (hypothesis loop in progress)
**Prerequisites Satisfied:** ✅ h-e1 COMPLETED (κ=0.645, probe=0.867)
**Gate Status:** SHOULD_WORK (graceful degradation on failure)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m-integrated
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (lifecycle separability existence validated)

### Gate Condition
**Gate Type:** SHOULD_WORK
- **Pass:** NMI(unsupervised) > 0.6 AND baseline gap ≥ 0.15
- **Fail Response:** EXPLORE alternative embeddings OR PIVOT to amplification framework OR SCOPE to repository-specific

---

## Continuation Context

This hypothesis builds on h-e1 foundation validation to test the complete mechanism chain:
1. **Foundation validated (h-e1):** Lifecycle constructs are operationally stable (κ ≥ 0.60) AND embeddings contain linear lifecycle signals (probe ≥ 0.75)
2. **Mechanism to test:** Semantic embeddings capture distributional signatures that enable unsupervised recovery of lifecycle structure
3. **Three-tier validation:** Baseline comparisons → Stylistic controls → Repository stratification

### Previous Hypothesis Results (h-e1)
- **Dataset collected:** 300 real metadata samples (150 HF, 100 OpenML, 50 UCI)
- **Embedding model validated:** `all-MiniLM-L6-v2` achieves 93.3% linear probe accuracy
- **Class distribution:** 275 General Information, 25 Responsible AI (8.3% RAI)
- **Key lesson:** Frozen embeddings work well; content-based annotation simulation produces low kappa (requires human annotators for kappa validation)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Semantic Embedding Clustering NMI**
- **Results:** Limited direct relevance (focused on diffusion models: LAION-5B, Imagen, HuggingFace diffusers)
- **Insight:** Knowledge base lacks specific metadata clustering experiments
- **Transferable:** Standard embedding model loading patterns from HuggingFace

**Query 2: Unsupervised Clustering Evaluation Baseline**
- **Results:** Evaluation notebooks for diffusion models (FID, CLIP scores)
- **Insight:** Standard practice is multi-baseline comparison (permutation, topic models, heuristics)
- **Transferable:** Baseline evaluation framework design patterns

**Query 3: Sentence Transformers Metadata Classification**
- **Top Match:** HuggingFace Transformers documentation (similarity: 0.526)
- **Relevance:** General transformer usage, not metadata-specific
- **Insight:** Use `sentence-transformers` library for frozen embeddings

**Summary:** Archon KB does not contain direct precedents for metadata lifecycle clustering. Will rely on standard NLP clustering practices and Exa GitHub search for implementations.

### Archon Code Examples

**Query 1: K-means Clustering Sklearn**
- **Results:** Diffusion pipeline loading code (Kandinsky models)
- **Relevance:** Low - no clustering code found
- **Pattern identified:** Model loading from HuggingFace Hub with `.from_pretrained()`

**Query 2: Sentence Transformers Encode**
- **Top match:** T5 text encoding example (similarity: 0.431)
  ```python
  from transformers import AutoTokenizer, T5EncoderModel
  tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-small")
  model = T5EncoderModel.from_pretrained("google-t5/t5-small")
  outputs = model(input_ids=input_ids)
  last_hidden_states = outputs.last_hidden_state
  ```
- **Transferable pattern:** Tokenizer + model loading, extraction of hidden states
- **Adaptation needed:** Replace with `sentence-transformers` library for direct `.encode()` API

**Summary:** Archon code examples focus on transformer loading, not clustering. Standard scikit-learn clustering + sentence-transformers encoding will be used.

### Exa GitHub Implementations

**Query 1: Sentence Transformers Clustering Unsupervised Metadata NMI Evaluation**

**Resource 1:** Topic Clustering on Embeddings from Sentence Transformers (Medium)
- **URL:** https://medium.com/@deepankermishra_56983/topic-clustering-on-embeddings-from-sentence-transformers-05e49f25b31b
- **Relevance:** ⭐⭐⭐ Direct match - sentence-transformers + K-means + NMI evaluation
- **Key Insight:** Author used NMI to compare K-means vs MiniBatchKMeans on high-dimensional embeddings
- **Code Pattern:**
  ```python
  from sklearn.cluster import KMeans, MiniBatchKMeans
  from sklearn.metrics import normalized_mutual_info_score

  # Compute NMI between two clustering methods
  nmi = normalized_mutual_info_score(kmeans_labels, mbk_labels)
  ```
- **Dataset:** Large text corpus, chunked and embedded with sentence-transformers
- **Challenge noted:** K-means struggles with high-dimensional uniform distributions (curse of dimensionality)
- **Alternative explored:** HDBSCAN for density-based clustering (but didn't work well)

**Resource 2:** Text Clustering using Sentence Embeddings (Dingu Sagar, Medium)
- **URL:** https://medium.com/@dingusagar/text-clustering-using-sentence-embeddings-abcb6048fc36
- **Relevance:** ⭐⭐⭐ Exact model match - `all-MiniLM-L6-v2`
- **Code Pattern:**
  ```python
  from sentence_transformers import SentenceTransformer, util

  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)
  clusters = util.community_detection(embeddings,
                                      min_community_size=2,
                                      threshold=0.5)
  ```
- **Hyperparameters:**
  - `threshold`: Cosine similarity threshold for cluster membership (0.5 default)
  - `min_community_size`: Minimum cluster size (2 default)
- **Insight:** sentence-transformers has built-in `community_detection` for clustering

**Resource 3:** Sentence-Transformers Evaluation Documentation
- **URL:** https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html
- **Relevance:** ⭐⭐ Official library docs for evaluation
- **Available Evaluators:** BinaryClassificationEvaluator, InformationRetrievalEvaluator, NanoBEIREvaluator
- **Insight:** Library focused on supervised tasks; NMI not in standard evaluators (use sklearn)

**Query 2: Sklearn K-means Clustering Normalized Mutual Information Baseline Comparison**

**Resource 1:** Scikit-learn NMI Documentation
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.normalized_mutual_info_score.html
- **Relevance:** ⭐⭐⭐ Primary metric definition
- **API:**
  ```python
  from sklearn.metrics import normalized_mutual_info_score

  nmi = normalized_mutual_info_score(labels_true, labels_pred,
                                      average_method='arithmetic')
  # Returns: 0.0 (no MI) to 1.0 (perfect correlation)
  ```
- **Parameters:**
  - `average_method`: {'min', 'geometric', 'arithmetic', 'max'} (default: 'arithmetic')
- **Note:** Not adjusted for chance (unlike AMI); symmetric metric

**Resource 2:** Adjustment for Chance in Clustering Performance Evaluation
- **URL:** https://scikit-learn.org/stable/auto_examples/cluster/plot_adjusted_for_chance_measures.html
- **Relevance:** ⭐⭐⭐ Critical for baseline evaluation
- **Metrics compared:** V-measure, Rand index, ARI, MI, NMI, AMI
- **Key finding:** "Non-adjusted measures (NMI, MI) should not be used to compare different clustering algorithms with different n_clusters"
- **Recommendation:** Use AMI (Adjusted Mutual Information) for fair comparison across different cluster counts
- **Impact:** For our 3 baselines (permutation, LDA 2-topic, lexical keyword) with same k=2, NMI is valid

**Resource 3:** Clustering methods compared (LinkedIn case study)
- **URL:** https://www.linkedin.com/posts/awbath-aljaberi-b4b937183...
- **Relevance:** ⭐⭐ Real-world NMI usage example
- **Methods compared:** K-means, GMM, DBSCAN
- **Metrics used:** ARI and NMI
- **Results:** K-means (ARI=0.4443, NMI=0.3895), GMM (ARI=0.4885, NMI=0.4578), DBSCAN (ARI=0.3062, NMI=0.3605)
- **Insight:** NMI values 0.3-0.5 are common for real clustering tasks

**Resource 4:** Scikit-learn Clustering Overview
- **URL:** https://scikit-learn.org/stable/modules/clustering.html
- **Relevance:** ⭐⭐ Standard library documentation
- **K-means details:**
  - Minimizes within-cluster sum-of-squares (inertia)
  - Assumes convex, isotropic clusters
  - Requires n_clusters as input
  - Scalable to large n_samples
- **Alternative:** MiniBatchKMeans for very large datasets (incremental learning)

### 🎯 Implementation Priority Assessment

**This is NOT a paper reproduction experiment** - it is a novel hypothesis testing metadata lifecycle separability.

**Implementation Strategy:**
- **Primary:** Standard libraries (sentence-transformers + sklearn)
- **Baseline implementations:** Custom (permutation, LDA, lexical heuristic)
- **Justification:** Well-established tools, no paper-specific implementation needed

**Recommended Implementation Path:**
- Primary: `sentence-transformers` (`all-MiniLM-L6-v2`) + `sklearn.cluster.KMeans`
- Fallback: MiniBatchKMeans if dataset exceeds memory limits
- Justification: Libraries used successfully in h-e1, proven to work with real metadata

### Code Analysis (Serena MCP)

**Serena Analysis:** Not needed - code patterns are straightforward.

**Implementation complexity:** LOW
- Sentence embedding: `model.encode(texts)` (1 line)
- K-means clustering: `KMeans(n_clusters=2).fit(embeddings)` (1 line)
- NMI computation: `normalized_mutual_info_score(labels_true, labels_pred)` (1 line)

**Total core mechanism:** ~10 lines (well within Level 1.5 specification)

---

## Experiment Specification

### Dataset

**Dataset**: Cross-Repository Metadata Sample (custom)
**Type**: custom (real data from APIs)
**Source**: HuggingFace Hub API, OpenML API, UCI repository
**Sample Size**: N=300 (150 HF [75 scaffolded/75 unscaffolded], 100 OpenML, 50 UCI)

**Continuation Note**: **Reusing dataset from h-e1** for controlled comparison. Dataset already collected and validated.

**Loading Information** (for Phase 4):
- Method: Reuse from h-e1 experiment
- Identifier: `data/metadata_sample/metadata_fields.csv` (from h-e1 validation)
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv("data/metadata_sample/metadata_fields.csv")
  # Columns: repository, field_name, field_value, lifecycle_label
  ```

**Statistics** (from h-e1 validation report):
- Total samples: 300 metadata fields
- Repositories: HuggingFace (150), OpenML (100), UCI (50)
- Lifecycle labels: 275 General Information, 25 Responsible AI (8.3% RAI)
- Scaffolding: 75 scaffolded (HF Open Datasheets), 225 unscaffolded

**Preprocessing** (inherited from h-e1):
- Field representation: Concatenate field_name + ": " + field_value
- Text cleaning: Remove excessive whitespace, normalize unicode
- No additional preprocessing (preserve distributional signatures)

**Augmentation**: None (unsupervised clustering requires original text)

### Models

#### Baseline Model

**Architecture**: Sentence Transformers (all-MiniLM-L6-v2)
**Type**: Semantic embedding model (frozen, pretrained)
**Parameters**: 22.7M (6 layers, 384 hidden dim)

**Continuation Note**: **Reusing model from h-e1** for controlled comparison.

**Loading Information** (for Phase 4):
- Method: sentence-transformers library
- Identifier: `all-MiniLM-L6-v2`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(texts, show_progress_bar=True)
  # Returns: numpy array of shape (n_samples, 384)
  ```

**Configuration**:
- Input: Text strings (field_name + value)
- Output: 384-dimensional embeddings (L2-normalized)
- Frozen: No fine-tuning (preserve general semantic knowledge)
- Context window: 256 tokens (sufficient for metadata fields)

#### Proposed Model

**Architecture**: Semantic embeddings + Unsupervised K-means clustering

**Core Mechanism**: Use frozen sentence-transformer embeddings to encode metadata field semantics, then apply K-means clustering to recover lifecycle structure unsupervised.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Embedding Clustering for Lifecycle Recovery
# Based on: Exa findings (sentence-transformers + sklearn)

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import normalized_mutual_info_score

class LifecycleClusteringPipeline:
    """
    Unsupervised clustering on semantic embeddings to recover lifecycle structure.
    Tests whether distributional signatures enable lifecycle separability.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', n_clusters=2):
        self.model = SentenceTransformer(model_name)
        self.clusterer = KMeans(n_clusters=n_clusters, random_state=42)

    def encode_metadata(self, field_texts):
        """
        Args:
            field_texts: List[str] - concatenated field_name + ": " + field_value
        Returns:
            embeddings: (n_samples, 384) - frozen semantic embeddings
        """
        embeddings = self.model.encode(field_texts, show_progress_bar=True)
        return embeddings  # L2-normalized by default

    def cluster(self, embeddings):
        """
        Args:
            embeddings: (n_samples, 384) - semantic embeddings
        Returns:
            labels_pred: (n_samples,) - cluster assignments {0, 1}
        """
        labels_pred = self.clusterer.fit_predict(embeddings)
        return labels_pred

    def evaluate_nmi(self, labels_true, labels_pred):
        """
        Compute NMI between predicted clusters and true lifecycle labels.
        Returns: float [0, 1] - 1.0 = perfect correspondence
        """
        nmi = normalized_mutual_info_score(labels_true, labels_pred,
                                             average_method='arithmetic')
        return nmi

# Integration: Standalone pipeline (no model modification needed)
```

### Training Protocol

**No Training Required**: Frozen embeddings + unsupervised clustering (no backpropagation).

**Clustering Configuration:**
- **Algorithm**: K-means (scikit-learn)
  - `n_clusters=2` (2-tier lifecycle structure)
  - `random_state=42` (reproducibility)
  - `init='k-means++'` (default, smart centroid initialization)
  - **Source**: Exa - standard for unsupervised clustering

**Baseline Configurations:**

1. **Permutation Baseline**: Random label shuffle
   - Method: `np.random.permutation(labels_true)`
   - Expected NMI: ~0.0

2. **LDA 2-Topic Baseline**: Topic modeling
   - Library: `sklearn.decomposition.LatentDirichletAllocation`
   - `n_components=2` (2 topics matching 2-tier structure)
   - `max_iter=100`, `random_state=42`
   - Expected NMI: 0.40-0.50 (from Phase 2B estimation)

3. **Lexical Keyword Baseline**: Rule-based clustering
   - Method: Keyword matching (e.g., "bias", "ethics" → RAI cluster)
   - Expected NMI: ~0.45 (from Phase 2B)

**Normalization Controls** (for stylistic artifact testing):
- Length normalization: Truncate/pad to fixed length
- Modality filtering: Remove deontic language markers

**Seeds**: 1 (fixed for reproducibility)

### Evaluation

**Primary Metrics**:
- **NMI (Normalized Mutual Information)**: Measures clustering agreement with true lifecycle labels
  - Range: [0, 1], 1.0 = perfect correspondence
  - Formula: NMI(U, V) = 2 * MI(U, V) / (H(U) + H(V))
  - Library: `sklearn.metrics.normalized_mutual_info_score`

**Success Criteria** (from Phase 2B):
- Primary: `NMI(semantic) > 0.6` **AND** `NMI(semantic) - max(NMI(baselines)) >= 0.15`
- Secondary: `NMI_normalized >= 0.6` (signal persists after controls), `probe_variance < 0.1` (generalization)

**Expected Baseline Performance** (from Phase 2B analysis):
- Permutation: ~0.0
- LDA: 0.40-0.50
- Lexical: ~0.45 (best baseline)
- **Target**: NMI >= 0.60 (gap of >=0.15 from best baseline)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Unsupervised clustering evaluation
- Library: `sklearn.metrics`
- Code:
  ```python
  from sklearn.metrics import normalized_mutual_info_score
  nmi = normalized_mutual_info_score(labels_true, labels_pred,
                                       average_method='arithmetic')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: NMI scores for all methods (semantic, permutation, LDA, lexical) - bar chart with target threshold line at 0.60

#### Additional Figures (LLM Autonomous)
- **Embedding Space Visualization**: t-SNE/UMAP projection of 384-dim embeddings colored by true lifecycle labels
- **Cluster Confusion Matrix**: True lifecycle labels vs predicted clusters
- **Repository Stratification**: NMI by repository (HF/OpenML/UCI) to test generalization
- **Scaffolding Effect**: NMI comparison scaffolded vs unscaffolded metadata
- **Baseline Comparison Matrix**: Heatmap showing pairwise NMI between all methods

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m-integrated/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism**: Semantic embeddings encode distributional signatures that enable unsupervised lifecycle recovery

### Pre-Conditions
- ✅ `mechanism_exists`: Sentence-transformers model loads and encodes text
- ✅ `mechanism_isolatable`: Clustering operates only on embeddings (no external features)
- ✅ `baseline_measurable`: Permutation, LDA, lexical baselines are independent

### Activation Indicators
- **Log Message**: "Encoded 300 metadata fields into (300, 384) embeddings"
- **Tensor Shape**: Embeddings shape (300, 384), Cluster labels shape (300,)
- **Metric Delta**: NMI(semantic) - NMI(permutation) should be >> 0 if mechanism works

### Architecture Compatibility
- ✅ Frozen embeddings (no fine-tuning) - compatible with any downstream clustering
- ✅ K-means operates on dense embeddings - standard sklearn interface
- ✅ No model architecture modification needed

### Failure Detection
1. **Embedding Failure**: If embedding shape != (300, 384) → model loading error
2. **Clustering Failure**: If K-means produces single cluster → convergence issue
3. **Mechanism Failure**: If NMI(semantic) ≈ NMI(permutation) → no signal in embeddings

### Verification Code
```python
# Check embedding generation
assert embeddings.shape == (300, 384), "Embedding shape mismatch"
assert not np.isnan(embeddings).any(), "NaN in embeddings"

# Check clustering produces valid labels
assert len(np.unique(labels_pred)) == 2, "K-means did not produce 2 clusters"

# Check mechanism provides signal
nmi_gain = nmi_semantic - nmi_permutation
print(f"Mechanism signal: NMI gain = {nmi_gain:.3f}")
assert nmi_gain > 0.1, "No semantic signal detected"
```

### Hypothesis Support Criteria
- **Threshold**: NMI(semantic) >= 0.60 **AND** NMI_gap >= 0.15
- **Metric**: Normalized Mutual Information between predicted clusters and true lifecycle labels
- **Pass**: Both conditions met
- **Partial**: NMI >= 0.50 but gap < 0.15 (signal exists but weak)
- **Fail**: NMI < 0.50 or NMI ≈ baselines (no mechanism effect)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Limited relevance - diffusion models focus
- **Type**: Knowledge base search results
- **Query Used**: "semantic embedding clustering NMI"
- **Relevance**: Low - returned LAION-5B, Imagen, diffusion model docs
- **Key Insights**:
  - Standard HuggingFace model loading patterns identified
  - Multi-baseline evaluation practice confirmed
- **Used For**: General best practices confirmation

**Source 2**: Transformers documentation
- **Query Used**: "sentence transformers metadata classification"
- **Relevance**: Medium - general transformer usage
- **Key Insights**:
  - `sentence-transformers` library recommended for frozen embeddings
  - `.encode()` API for batch encoding
- **Used For**: Model selection validation

### Archon Code Examples

**Code Source 1**: T5 Text Encoding Example
- **Query Used**: "sentence transformers encode"
- **Key Code**:
  ```python
  from transformers import AutoTokenizer, T5EncoderModel
  model = T5EncoderModel.from_pretrained("google-t5/t5-small")
  outputs = model(input_ids=input_ids)
  last_hidden_states = outputs.last_hidden_state
  ```
- **Used For**: General transformer loading pattern (adapted for sentence-transformers)

---

### B. GitHub Implementations (Exa)

**Repository 1**: Topic clustering on embeddings (Medium article)
- **URL**: https://medium.com/@deepankermishra_56983/topic-clustering-on-embeddings-from-sentence-transformers-05e49f25b31b
- **Query Used**: "sentence transformers clustering unsupervised metadata NMI evaluation"
- **Relevance**: ⭐⭐⭐ HIGH - Exact workflow match (sentence-transformers + K-means + NMI)
- **Key Code**:
  ```python
  from sklearn.cluster import KMeans, MiniBatchKMeans
  from sklearn.metrics import normalized_mutual_info_score

  # Clustering comparison
  nmi = normalized_mutual_info_score(kmeans_labels, mbk_labels)
  ```
- **Configuration Extracted**:
  - K-means for clustering
  - NMI for evaluation
  - Curse of dimensionality noted for high-dim embeddings
- **Used For**: Clustering algorithm selection, NMI evaluation implementation

**Repository 2**: Text Clustering using Sentence Embeddings (Dingu Sagar)
- **URL**: https://medium.com/@dingusagar/text-clustering-using-sentence-embeddings-abcb6048fc36
- **Query Used**: "sentence transformers clustering unsupervised metadata NMI evaluation"
- **Relevance**: ⭐⭐⭐ HIGH - Uses exact model `all-MiniLM-L6-v2`
- **Key Code**:
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(sentences)
  # Built-in community_detection for clustering (alternative to K-means)
  clusters = util.community_detection(embeddings,
                                       min_community_size=2,
                                       threshold=0.5)
  ```
- **Configuration Extracted**:
  - Model: `all-MiniLM-L6-v2` (exact match)
  - Encoding: `model.encode()` batch API
  - Hyperparameters: threshold=0.5, min_community_size=2
- **Used For**: Model loading code, encoding implementation

**Repository 3**: Scikit-learn NMI Documentation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.normalized_mutual_info_score.html
- **Query Used**: "sklearn kmeans clustering normalized mutual information baseline comparison"
- **Relevance**: ⭐⭐⭐ HIGH - Primary metric definition
- **Key Code**:
  ```python
  from sklearn.metrics import normalized_mutual_info_score
  nmi = normalized_mutual_info_score(labels_true, labels_pred,
                                       average_method='arithmetic')
  # Returns: 0.0 (no MI) to 1.0 (perfect)
  ```
- **Configuration Extracted**:
  - `average_method='arithmetic'` (default, recommended)
  - Symmetric metric (order independent)
  - Not adjusted for chance (use AMI if comparing different k)
- **Used For**: NMI metric implementation, success criteria definition

**Repository 4**: Adjustment for Chance in Clustering (sklearn examples)
- **URL**: https://scikit-learn.org/stable/auto_examples/cluster/plot_adjusted_for_chance_measures.html
- **Query Used**: "sklearn kmeans clustering normalized mutual information baseline comparison"
- **Relevance**: ⭐⭐⭐ HIGH - Critical for baseline evaluation validity
- **Key Insights**:
  - NMI is valid for same k comparison (our case: all methods use k=2)
  - AMI adjusts for chance (useful for different k comparison)
  - Non-adjusted metrics should not compare different n_clusters
- **Used For**: Baseline comparison design validation, metric selection justification

**Repository 5**: Real-world clustering comparison (LinkedIn case study)
- **URL**: https://www.linkedin.com/posts/awbath-aljaberi-b4b937183_statistics-datascience-datascientist-activity-7310078821796397056-WmNK
- **Query Used**: "sklearn kmeans clustering normalized mutual information baseline comparison"
- **Relevance**: ⭐⭐ MEDIUM - Real-world NMI benchmarks
- **Their Results**: K-means (NMI=0.3895), GMM (NMI=0.4578), DBSCAN (NMI=0.3605)
- **Used For**: Expected NMI range calibration (0.3-0.5 is common for real tasks)

**Repository 6**: Sentence-Transformers Unsupervised Learning Docs
- **URL**: https://sbert.net/examples/sentence_transformer/unsupervised_learning/README.html
- **Query Used**: "sentence transformers clustering unsupervised metadata NMI evaluation"
- **Relevance**: ⭐⭐ MEDIUM - Official library documentation
- **Key Insights**:
  - TSDAE, SimCSE, CT for unsupervised training (not needed - we use frozen)
  - GenQ/GPL for retrieval tasks (not applicable)
  - Performance comparison shows frozen models acceptable for many tasks
- **Used For**: Frozen embedding approach validation

---

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from Exa search results was sufficiently clear and well-documented. Direct sklearn/sentence-transformers APIs require minimal abstraction.

---

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-e1
- **File**: `docs/youra_research/20260318_mldpr/h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: Cross-Repository Metadata Sample (N=300, real data from APIs)
  - Model: `all-MiniLM-L6-v2` (93.3% linear probe accuracy validated)
  - Data collection code: Proven stable (HF API, OpenML API, UCI scraping)
- **Why Reused**: Enables controlled experiment - only clustering approach changes (h-e1 tested supervised probe, h-m tests unsupervised clustering)
- **Key Lesson from h-e1**: Frozen embeddings work well; class imbalance exists (8.3% RAI)

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset reuse | Previous (h-e1) | D.1 - h-e1 validation report |
| Model selection | Previous + Exa | D.1 (h-e1), B.2 (Dingu Sagar) |
| Model loading code | Exa GitHub | B.2 - sentence-transformers tutorial |
| Clustering algorithm | Exa GitHub | B.1, B.2 - K-means examples |
| NMI metric | Exa GitHub | B.3 - sklearn NMI docs |
| NMI evaluation code | Exa GitHub | B.1, B.3 - implementation examples |
| Baseline design | Exa + Phase 2B | B.4 (validity), Phase 2B Section 2.2 |
| Expected NMI range | Exa + Phase 2B | B.5 (real-world), Phase 2B estimates |
| Frozen embeddings | Previous + Exa | D.1 (validated), B.6 (best practice) |
| Pseudo-code structure | Exa GitHub | B.1, B.2 - adapted patterns |
| Success criteria | Phase 2B | 02b_context.md - hypothesis success criteria |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T08:15:00Z

### Workflow History for This Hypothesis

**Phase 2C Events:**
- 2026-03-18T07:57:17Z - Hypothesis set to IN_PROGRESS (external loop)
- 2026-03-18T08:00:00Z - Experiment design started
- 2026-03-18T08:15:00Z - Experiment design completed

**Status:** experiment_design.status = COMPLETED

**Next Phase:** Phase 3 - Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

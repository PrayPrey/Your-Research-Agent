# Experiment Design: H-C1

**Date:** 2026-08-08
**Author:** Anonymous
**Hypothesis Statement:** Disagreement cases (high-BAI/low-reward slice) are semantically coherent, with majority exhibiting interpretable agency-preserving patterns (clarifying, deferring, hedging) rather than noise or verbosity artifacts.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION Hypothesis** - Validates semantic quality of H-M2 disagreement findings.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 VALIDATED (PARTIAL - 11.77% disagreement rate)
**Gate Status:** SHOULD_WORK (proceeding with analysis)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-M2

### Gate Condition
SHOULD_WORK: If semantic coherence fails, findings still publishable as "BAI captures something, but not clearly agency-preserving patterns."

---

## Continuation Context

### Previous Hypothesis Results (H-M2)
- **Disagreement Rate:** 11.77% (4932 samples from 41,896 total)
- **High-BAI/Low-Reward quadrant:** 3063 samples (dominant)
- **Low-BAI/High-Reward quadrant:** 1869 samples
- **Pearson correlation:** r=-0.11 (weak negative, suggests partial orthogonality)
- **BAI variance:** 0.0022 (conservative proxy detection)

**Key Insight:** The disagreement slice exists and is non-trivial. H-C1 must verify these are semantically meaningful agency patterns, not length/politeness artifacts.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for semantic coherence analysis in KB. Focus shifted to established NLP clustering methods.

### Archon Code Examples

No directly applicable code examples. Using established libraries (BERTopic, sentence-transformers).

### Exa GitHub Implementations

**Primary Finding: BERTopic (MaartenGr/BERTopic)**
- GitHub: https://github.com/MaartenGr/BERTopic
- Paper: arXiv:2203.05794
- Pipeline: sentence-transformers → UMAP → HDBSCAN → c-TF-IDF
- LLM-based cluster labeling available
- `get_representative_docs()` for human verification

**Secondary Finding: Agency Framework (EACL 2024)**
- Paper: "Investigating Agency of LLMs in Human-AI Collaboration Tasks"
- URL: https://aclanthology.org/2024.eacl-long.119/
- Features: Intentionality, Motivation, Self-Efficacy, Self-Regulation
- Dataset: 908 annotated snippets

**Additional: LLM Cluster Naming**
- Paper: "Evaluation of Text Cluster Naming with Generative LLMs" (JDS 2024)
- GPT-3.5-turbo for cluster interpretation

### 🎯 Implementation Priority Assessment

**CRITICAL: Use established semantic clustering for interpretability**

**Recommended Implementation Path:**
- Primary: BERTopic with sentence-transformers embeddings
- Fallback: K-means on embeddings + manual cluster inspection
- Justification: BERTopic provides interpretable topics with c-TF-IDF keywords, enabling human verification of agency patterns

### Code Analysis (Serena MCP)

Not applicable — this experiment uses standard NLP libraries, no codebase-specific analysis needed.

---

## Experiment Specification

### Dataset

**Name:** H-M2 Disagreement Slice (from HH-RLHF + RewardBench)
**Type:** derived (extracted from H-M2 validation output)
**Source:** H-M2 04_validation.md output or recompute from parent datasets

**Slice Definition:**
- High-BAI/Low-Reward: BAI > Q3 AND reward < Q1 (3063 samples)
- Low-BAI/High-Reward: BAI < Q1 AND reward > Q3 (1869 samples)
- Total: 4932 samples for clustering

**Loading Information** (for Phase 4 download):
- Method: Reuse H-M2 computed scores OR recompute
- Identifier: `h-m2/disagreement_samples.json` (if saved) OR recompute from HH-RLHF/RewardBench
- Code:
```python
# Option 1: Load H-M2 saved outputs
import json
with open("h-m2/disagreement_samples.json") as f:
    disagreement_data = json.load(f)

# Option 2: Recompute (if not saved)
from datasets import load_dataset
hh_rlhf = load_dataset("Anthropic/hh-rlhf", split="test")
# Apply BAI computation and quartile filtering
```

### Models

#### Baseline Model

**Architecture:** No model comparison — this is a clustering/classification task
**Purpose:** Establish cluster interpretability baseline via random labeling

**Loading Information** (for Phase 4 download):
- Method: HuggingFace sentence-transformers
- Identifier: `sentence-transformers/all-MiniLM-L6-v2`
- Code:
```python
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
```

#### Proposed Model

**Architecture:** BERTopic clustering pipeline

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Coherence Clustering
# Based on: BERTopic (Grootendorst, 2022)

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN

class AgencyPatternClusterer:
    """
    Cluster disagreement responses and identify agency-preserving patterns.
    Success: >50% of clusters are interpretable agency patterns.
    """
    def __init__(self, min_cluster_size=50):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.umap_model = UMAP(n_neighbors=15, n_components=5, metric="cosine")
        self.hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, 
                                      metric="euclidean", 
                                      cluster_selection_method="eom")
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            top_n_words=10
        )
    
    def fit_transform(self, texts):
        """Cluster texts and return topics."""
        topics, probs = self.topic_model.fit_transform(texts)
        return topics, probs
    
    def get_topic_info(self):
        """Get interpretable topic descriptions."""
        return self.topic_model.get_topic_info()
    
    def get_representative_docs(self, topic_id):
        """Get representative documents for manual verification."""
        return self.topic_model.get_representative_docs(topic_id)

# Agency pattern keywords for classification
AGENCY_PATTERNS = {
    "clarifying": ["clarify", "understand", "mean", "asking", "question", "sure"],
    "deferring": ["prefer", "choice", "decide", "up to you", "your call", "depends"],
    "hedging": ["might", "perhaps", "possibly", "could be", "uncertain", "not sure"],
    "option_enum": ["option", "alternatively", "or", "either", "choices", "ways"]
}

def classify_cluster_as_agency(topic_keywords, threshold=2):
    """Check if cluster keywords match agency patterns."""
    matches = 0
    for pattern_name, keywords in AGENCY_PATTERNS.items():
        if any(kw in topic_keywords.lower() for kw in keywords):
            matches += 1
    return matches >= threshold, matches
```

### Training Protocol

**Not applicable** — BERTopic is unsupervised, no training required.

**Clustering Configuration:**
- min_cluster_size: 50 (ensures statistically meaningful clusters)
- UMAP components: 5
- UMAP neighbors: 15
- Metric: cosine (embedding space)

**Seeds:** 1 (UMAP random_state=42)

### Evaluation

**Primary Metrics:**
1. **Agency Pattern Rate:** % of clusters classified as agency-preserving
2. **Cluster Coherence:** Average silhouette score
3. **Coverage:** % of samples assigned to non-noise clusters

**Success Criteria (CONDITION hypothesis):**
- Agency Pattern Rate > 50% (majority are interpretable agency patterns)
- Coverage > 70% (most samples cluster meaningfully, not noise)

**Expected Results (from H-M2 findings):**
- High-BAI/Low-Reward should cluster into clarifying, deferring, hedging patterns
- If artifact-dominated, would see length/verbosity-based clusters instead

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: clustering + classification
- Library: sklearn.metrics (silhouette_score), custom (agency_pattern_rate)
- Code:
```python
from sklearn.metrics import silhouette_score

def compute_metrics(texts, topics, embeddings, topic_model):
    # Filter noise (-1 topic)
    valid_mask = topics != -1
    coverage = valid_mask.mean()
    
    # Silhouette on valid clusters
    if valid_mask.sum() > 1:
        silhouette = silhouette_score(embeddings[valid_mask], topics[valid_mask])
    else:
        silhouette = 0.0
    
    # Agency pattern rate
    topic_info = topic_model.get_topic_info()
    agency_clusters = 0
    total_clusters = len(topic_info) - 1  # exclude -1
    for _, row in topic_info.iterrows():
        if row["Topic"] == -1:
            continue
        keywords = " ".join([w for w, _ in topic_model.get_topic(row["Topic"])])
        is_agency, _ = classify_cluster_as_agency(keywords)
        if is_agency:
            agency_clusters += 1
    
    agency_rate = agency_clusters / total_clusters if total_clusters > 0 else 0
    return {
        "coverage": coverage,
        "silhouette": silhouette,
        "agency_pattern_rate": agency_rate,
        "total_clusters": total_clusters,
        "agency_clusters": agency_clusters
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Agency pattern rate vs 50% threshold bar chart

#### Additional Figures (LLM Autonomous)
- UMAP 2D projection colored by cluster
- Topic word clouds for top-5 clusters
- Representative document samples per cluster (table)
- Cluster size distribution histogram

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (BERTopic clustering is established method)
- `mechanism_isolatable`: True (clustering output is discrete topics)
- `baseline_measurable`: True (random assignment baseline computable)

### Architecture Compatibility
- BERTopic compatible with any text input
- sentence-transformers provides semantic embeddings
- No architecture conflicts

### Activation Indicators
- `mechanism_log_message`: "BERTopic fit complete. {n_topics} topics discovered."
- `tensor_shape_change`: embeddings (N, 768) → topics (N,) with integer cluster IDs
- `metric_delta_expected`: Agency pattern rate > random (random ≈ 0% agency match)

### Mechanism Verification Code
```python
def verify_mechanism(topic_model, texts, embeddings):
    """Verify BERTopic clustering mechanism works."""
    # Check 1: Topics discovered (not all noise)
    topics = topic_model.topics_
    n_topics = len(set(topics)) - 1  # exclude -1
    assert n_topics >= 3, f"Too few topics: {n_topics}"
    
    # Check 2: Coverage above threshold
    coverage = (np.array(topics) != -1).mean()
    assert coverage > 0.5, f"Low coverage: {coverage:.2%}"
    
    # Check 3: Clusters are semantically distinct
    topic_embeddings = topic_model.topic_embeddings_
    if topic_embeddings is not None:
        # Topics should not be identical
        pairwise_sim = np.corrcoef(topic_embeddings)
        off_diag = pairwise_sim[np.triu_indices_from(pairwise_sim, k=1)]
        assert off_diag.mean() < 0.9, "Topics too similar"
    
    print("✅ Mechanism verification passed")
    return True
```

### Success Criteria
- `hypothesis_support_threshold`: agency_pattern_rate > 0.50
- `hypothesis_support_metric`: agency_pattern_rate

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `agency_pattern_rate > 0.50` (majority clusters are agency patterns)
3. `coverage > 0.70` (most samples cluster meaningfully)

---

## Appendix: Reference Implementations

| Source | URL | Relevance |
|--------|-----|-----------|
| BERTopic | https://github.com/MaartenGr/BERTopic | Primary clustering method |
| BERTopic Paper | arXiv:2203.05794 | Algorithm details |
| BERTopic Docs | https://maartengr.github.io/BERTopic/ | API reference |
| Agency LLM Paper | https://aclanthology.org/2024.eacl-long.119/ | Agency feature framework |
| LLM Cluster Naming | https://jds-online.org/journal/JDS/article/1385 | Cluster interpretation method |
| sentence-transformers | https://www.sbert.net/ | Embedding model |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - state in prompt)
**Date:** 2026-08-08T04:00:00Z

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- MCP research: BERTopic, agency framework, cluster naming
- Experiment specification synthesized
- Ready for Phase 3 implementation planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

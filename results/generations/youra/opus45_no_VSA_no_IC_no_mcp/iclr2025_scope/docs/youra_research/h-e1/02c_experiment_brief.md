# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** Research Pipeline
**Hypothesis Statement:** Under transformer-to-SSM conversion training, if hidden states are clustered via self-supervised learning, then embeddings will show structure correlated with downstream task similarity.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (first in dependency chain)

### Gate Condition
Cluster purity > random baseline (>0.125 for 8 clusters). If fails → PIVOT to supervised task embeddings.

---

## Continuation Context

First hypothesis in chain. No previous context to inherit.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP unavailable. Findings from WebSearch:*

**Query 1: Hidden State Clustering in Transformers**
- Transformer hidden states naturally exhibit clustering properties
- KMeans commonly used to uncover clusters within hidden states
- Encoder output shows superior and more stable clustering compared to other components
- Self-supervised learning methods can leverage structural characteristics

**Query 2: Task Structure in Hidden States**
- Late training stages show strong clustering effect on task identities
- First layers cluster by topical similarities (like Word2Vec)
- Middle layers cluster by contextual relations
- High metric values (ARI, NMI) indicate meaningful task-based structure

**Source:** [Transformer-based Causal Language Models Perform Clustering](https://arxiv.org/pdf/2402.12151)

### Archon Code Examples

*Archon MCP unavailable. Code patterns from WebSearch:*

**Hidden State Extraction Pattern:**
```python
# From HuggingFace Transformers documentation
model = AutoModel.from_pretrained("bert-base-uncased", output_hidden_states=True)
outputs = model(**inputs)
hidden_states = outputs.hidden_states  # tuple of (batch, seq_len, hidden_dim)
```

**Source:** [BERT HuggingFace Docs](https://huggingface.co/docs/transformers/model_doc/bert)

### Exa GitHub Implementations

**Mamba SSM Implementations:**
- Official: [state-spaces/mamba](https://github.com/state-spaces/mamba)
- Minimal: [johnma2006/mamba-minimal](https://github.com/johnma2006/mamba-minimal)
- Mamba-2: [tommyip/mamba2-minimal](https://github.com/tommyip/mamba2-minimal)

**Key Architecture Notes:**
- Selective structured state space model (SSM)
- Hidden states computed recursively (RNN-like but more structured)
- (A, B, C) SSM parameters can be input-dependent
- Efficient SSM scan faster than FlashAttention-2 beyond seq_len 2K

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

For H-E1 (clustering existence test), we need:
1. Standard transformer for hidden state extraction
2. Clustering algorithm (K-means)
3. Evaluation metrics (ARI, NMI, cluster purity)

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers (BERT/GPT-2) + sklearn.cluster.KMeans
- Fallback: Manual extraction with PyTorch + custom clustering
- Justification: HuggingFace provides standardized hidden state access via `output_hidden_states=True`

### Code Analysis (Serena MCP)

*Serena MCP not available for this session. Analysis derived from WebSearch results.*

**Hidden State Access Pattern (from PyTorch-Transformers):**
- Set `output_hidden_states=True` in model config
- Hidden states returned as tuple: `(layer_0, layer_1, ..., layer_n)`
- Each tensor shape: `(batch_size, sequence_length, hidden_size)`
- BERT-base: hidden_size=768, 12 layers

---

## Experiment Specification

### Dataset

**Dataset:** SuperGLUE
**Type:** standard (HuggingFace datasets)

**Details:**
- 8 NLU tasks: BoolQ, CB, COPA, MultiRC, ReCoRD, RTE, WiC, WSC
- Standard few-shot benchmark with established protocols
- Each task has train/validation/test splits
- Total samples: ~30K across all tasks

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `super_glue` with task-specific configs
- Code:
```python
from datasets import load_dataset
# Load individual tasks
boolq = load_dataset("super_glue", "boolq")
cb = load_dataset("super_glue", "cb")
copa = load_dataset("super_glue", "copa")
rte = load_dataset("super_glue", "rte")
wic = load_dataset("super_glue", "wic")
wsc = load_dataset("super_glue", "wsc")
multirc = load_dataset("super_glue", "multirc")
record = load_dataset("super_glue", "record")
```

**Preprocessing:**
- Tokenize with model's tokenizer (max_length=512)
- Add task identifier token or use task-specific prompts
- Extract hidden states from final encoder layer

### Models

#### Baseline Model

**Architecture:** BERT-base-uncased (or GPT-2 small)
**Type:** Pretrained transformer

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `bert-base-uncased`
- Code:
```python
from transformers import AutoModel, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased", output_hidden_states=True)
```

**Configuration:**
- Hidden size: 768
- Layers: 12
- Attention heads: 12
- Parameters: ~110M

**Purpose in H-E1:** Source of hidden states for clustering analysis

#### Proposed Model

**Architecture:** Baseline + K-means clustering on hidden states

**Core Mechanism Implementation:**

```python
# Core Mechanism: Task Embedding Structure Discovery
# Based on: Transformer-based CLMs Perform Clustering (arXiv:2402.12151)

import torch
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

class TaskEmbeddingClusterer:
    """
    Extract hidden states from transformer and cluster to discover task structure.
    H-E1: Verify that task-correlated structure exists in hidden representations.
    """
    def __init__(self, model, tokenizer, n_clusters=8, layer_idx=-1):
        self.model = model
        self.tokenizer = tokenizer
        self.n_clusters = n_clusters  # 8 = number of SuperGLUE tasks
        self.layer_idx = layer_idx    # -1 = last layer
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    
    def extract_hidden_states(self, texts, task_labels):
        """Extract [CLS] hidden states for each sample."""
        hidden_states = []
        with torch.no_grad():
            for text in texts:
                inputs = self.tokenizer(text, return_tensors="pt", 
                                        truncation=True, max_length=512)
                outputs = self.model(**inputs)
                # Get hidden state at specified layer, [CLS] token
                hs = outputs.hidden_states[self.layer_idx][:, 0, :]
                hidden_states.append(hs.cpu().numpy())
        return np.vstack(hidden_states), np.array(task_labels)
    
    def cluster_and_evaluate(self, hidden_states, task_labels):
        """Cluster hidden states and measure task correlation."""
        cluster_labels = self.kmeans.fit_predict(hidden_states)
        
        # Evaluation metrics
        ari = adjusted_rand_score(task_labels, cluster_labels)
        nmi = normalized_mutual_info_score(task_labels, cluster_labels)
        
        # Cluster purity
        purity = self._compute_purity(task_labels, cluster_labels)
        
        return {"ARI": ari, "NMI": nmi, "purity": purity}
    
    def _compute_purity(self, true_labels, cluster_labels):
        """Compute cluster purity score."""
        contingency = {}
        for c, t in zip(cluster_labels, true_labels):
            if c not in contingency:
                contingency[c] = {}
            contingency[c][t] = contingency[c].get(t, 0) + 1
        
        purity_sum = sum(max(d.values()) for d in contingency.values())
        return purity_sum / len(true_labels)

# Usage: Extract from all SuperGLUE tasks, cluster, measure correlation
```

### Training Protocol

**Note:** H-E1 is EXISTENCE (PoC) - no training required. This is an analysis experiment.

**Protocol:**
1. Load pretrained BERT-base-uncased
2. Forward pass on SuperGLUE samples (no gradient)
3. Extract hidden states from layer -1 (last layer)
4. Apply K-means clustering (K=8)
5. Evaluate cluster-task correlation

**Hyperparameters (fixed):**
- K-means clusters: 8 (matching SuperGLUE task count)
- Hidden layer: -1 (last encoder layer)
- Samples per task: Full validation sets (~500-5000 per task)
- Random seed: 42

**Seeds:** 1 (PoC scope)

### Evaluation

**Primary Metrics:**
- **Cluster Purity:** Fraction of samples in majority class per cluster
- **Adjusted Rand Index (ARI):** Similarity between cluster and task assignments
- **Normalized Mutual Information (NMI):** Mutual dependence between predicted and true labels

**Success Criteria** (PoC):
- Primary: Cluster purity > 0.125 (random baseline for 8 clusters)
- Secondary: NMI > 0.3 (meaningful structure)
- Tertiary: ARI > 0 (better than random)

**Expected Baseline Performance** (from research):
- Random clustering: purity ≈ 0.125, ARI ≈ 0, NMI ≈ 0
- Prior work shows hidden states exhibit "strong clustering effect on task identities"

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: clustering evaluation
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ari = adjusted_rand_score(true_labels, cluster_labels)
nmi = normalized_mutual_info_score(true_labels, cluster_labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing purity, ARI, NMI vs random baseline thresholds

#### Additional Figures (LLM Autonomous)
- t-SNE/UMAP visualization of hidden states colored by task
- Confusion matrix: cluster assignments vs task labels
- Layer-wise clustering quality (purity per layer)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `cluster_purity > 0.125` (random baseline)
3. `NMI > 0` (any positive correlation)

---

## Appendix: Reference Implementations

### Primary Sources

1. **Transformer-based Causal Language Models Perform Clustering**
   - arXiv: [2402.12151](https://arxiv.org/pdf/2402.12151)
   - Key finding: Hidden states cluster by task identity in late training

2. **Clustering Properties of Self-Supervised Learning**
   - arXiv: [2501.18452](https://arxiv.org/html/2501.18452)
   - Key finding: Encoder output shows superior clustering properties

3. **How Does BERT Answer Questions? Layer-Wise Analysis**
   - arXiv: [1909.04925](https://arxiv.org/pdf/1909.04925)
   - Key finding: Layer-wise clustering reveals semantic organization

### Code References

1. **HuggingFace Transformers - BERT**
   - URL: https://huggingface.co/docs/transformers/model_doc/bert
   - Usage: `output_hidden_states=True` for hidden state extraction

2. **SuperGLUE Dataset**
   - URL: https://huggingface.co/datasets/aps/super_glue
   - Usage: `load_dataset("super_glue", "<task_name>")`

3. **Mamba SSM (for future H-M* hypotheses)**
   - Official: https://github.com/state-spaces/mamba
   - Minimal: https://github.com/johnma2006/mamba-minimal

### Metric Implementation

```python
# Clustering evaluation (sklearn)
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Dimensionality reduction for visualization
from sklearn.manifold import TSNE
import umap
```

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE - restated below)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design initiated
- Research completed via WebSearch (Archon/Exa unavailable)
- Experiment specification generated at Level 1.5

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

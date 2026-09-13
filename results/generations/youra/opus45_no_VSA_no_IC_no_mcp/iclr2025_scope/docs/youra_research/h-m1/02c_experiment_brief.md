# Experiment Design: H-M1

**Date:** 2026-08-28
**Author:** PrayPrey
**Hypothesis Statement:** Under the scope of conversion training, if task embeddings are learned from clustered hidden states, then they will encode functional specialization patterns useful for downstream adaptation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates that clustered embeddings encode discriminable task structure.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (PASS - cluster purity > random baseline confirmed)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
Linear probe accuracy on task classification must exceed random baseline (12.5% for 8 SuperGLUE tasks). This validates that learned embeddings capture discriminable task-specific patterns.

---

## Continuation Context

This experiment builds on H-E1 results showing clusterable structure exists in transformer hidden states. H-M1 validates these clusters produce usable task embeddings, not just statistical structure.

### Previous Hypothesis Results (if applicable)
H-E1 validated that K-means clustering (K=8) on transformer hidden states produces clusters correlated with SuperGLUE task labels (cluster purity > 0.125 random baseline, NMI > 0.3).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using direct research*

Key patterns from literature:
1. **Linear probing** is standard method for evaluating embedding quality (Alain & Bengio, 2016)
2. **Task embedding dimensions** typically 16-64 for efficient downstream use
3. **Frozen embeddings + linear classifier** isolates embedding quality from classifier capacity

### Archon Code Examples

*MCP unavailable - using direct research*

Reference implementations:
- `sklearn.linear_model.LogisticRegression` for linear probe
- `torch.nn.Embedding` for task embedding layer
- Standard practice: L2-regularized logistic regression with C=1.0

### Exa GitHub Implementations

*MCP unavailable - using web research*

**Mamba Implementation (state-spaces/mamba):**
- Pretrained models: mamba-130m through mamba-2.8b on HuggingFace
- Installation: `pip install mamba-ssm --no-build-isolation`
- Core: Selective SSM with input-dependent Δ, B, C parameters

**SuperGLUE (aps/super_glue on HuggingFace):**
- 8 core classification tasks: boolq, cb, copa, multirc, record, rte, wic, wsc
- ~196K total samples across tasks
- Standard splits available via datasets library

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. Use official Mamba implementation from state-spaces/mamba
2. Use HuggingFace datasets for SuperGLUE loading
3. Implement custom task embedding layer on top of Mamba hidden states

**Recommended Implementation Path:**
- Primary: Extract hidden states from pretrained mamba-370m, train embedding layer, evaluate with linear probe
- Fallback: Use mamba-130m if compute constrained
- Justification: Mid-size model balances representation quality with compute efficiency

### Code Analysis (Serena MCP)

*MCP unavailable - skipped*

---

## Experiment Specification

### Dataset

**Name:** SuperGLUE
**Version:** Standard HuggingFace version (aps/super_glue)
**Type:** standard

**Tasks for embedding evaluation:**
| Task | Train | Validation | Type |
|------|-------|------------|------|
| BoolQ | 9,427 | 3,270 | Binary QA |
| CB | 250 | 56 | 3-way NLI |
| COPA | 400 | 100 | Causal reasoning |
| RTE | 2,490 | 277 | Binary NLI |
| WiC | 5,428 | 638 | Word sense |
| WSC | 554 | 104 | Coreference |

**Total evaluation samples:** Full validation sets (~4,445 samples across 6 tasks)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: aps/super_glue
- Code:
```python
from datasets import load_dataset

tasks = ['boolq', 'cb', 'copa', 'rte', 'wic', 'wsc']
datasets = {task: load_dataset('super_glue', task) for task in tasks}
```

### Models

#### Baseline Model

**Architecture:** Random embedding baseline
**Description:** Randomly initialized task embeddings (same dimension) with frozen weights
**Purpose:** Establishes chance-level linear probe accuracy (~12.5% for 8-way classification)

**Loading Information** (for Phase 4 download):
- Method: PyTorch random initialization
- Identifier: N/A (random baseline)
- Code:
```python
import torch
random_embeddings = torch.randn(8, embedding_dim)  # 8 tasks
```

#### Proposed Model

**Architecture:** Task embedding layer trained on clustered hidden states

**Core Mechanism Implementation:**

```python
# H-M1: Task Embedding Encoding
# Input: Hidden states H from transformer (from H-E1 clustering)
# Output: Task embeddings E, linear probe accuracy

class TaskEmbeddingEncoder(nn.Module):
    def __init__(self, hidden_dim, embedding_dim, num_tasks=8):
        super().__init__()
        # Learn task embeddings from cluster centroids
        self.embedding = nn.Embedding(num_tasks, embedding_dim)
        # Project hidden states to embedding space
        self.projection = nn.Linear(hidden_dim, embedding_dim)
        
    def forward(self, hidden_states, cluster_assignments):
        # Project hidden states
        projected = self.projection(hidden_states)  # [B, seq, emb_dim]
        # Pool to sequence level
        pooled = projected.mean(dim=1)  # [B, emb_dim]
        return pooled

# Training: Contrastive or reconstruction loss on clusters
# Evaluation: Freeze embeddings, train linear probe

class LinearProbe(nn.Module):
    def __init__(self, embedding_dim, num_tasks):
        super().__init__()
        self.classifier = nn.Linear(embedding_dim, num_tasks)
    
    def forward(self, embeddings):
        return self.classifier(embeddings)

# Success metric: probe_accuracy > 0.125 (random baseline for 8 tasks)
```

### Training Protocol

**Task Embedding Training:**
- Optimizer: AdamW
- Learning rate: 1e-4
- Batch size: 32
- Epochs: 10
- Loss: Contrastive loss (InfoNCE) on cluster membership

**Linear Probe Training:**
- Optimizer: L-BFGS (sklearn LogisticRegression)
- Regularization: L2 with C=1.0
- Max iterations: 1000
- Training data: Frozen task embeddings from validation set

### Evaluation

**Primary Metric:** Linear probe accuracy on 8-way task classification
**Success Threshold:** Accuracy > 12.5% (random baseline)

**Secondary Metrics:**
- Per-task probe accuracy
- Embedding cluster separation (silhouette score)
- t-SNE visualization of learned embeddings

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-class classification
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression

# Train linear probe
probe = LogisticRegression(C=1.0, max_iter=1000)
probe.fit(train_embeddings, train_labels)

# Evaluate
predictions = probe.predict(test_embeddings)
accuracy = accuracy_score(test_labels, predictions)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Linear probe accuracy vs random baseline (12.5%) bar chart

#### Additional Figures (LLM Autonomous)
- t-SNE/UMAP visualization of learned task embeddings colored by task
- Per-task accuracy breakdown bar chart
- Embedding dimension ablation (16 vs 32 vs 64)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `linear_probe_accuracy > 0.125` (8-way random baseline)

**Stretch goal:** Accuracy > 0.5 (indicates strong task discrimination)

---

## Ablation Studies

| Variant | What it Tests | Expected Outcome |
|---------|---------------|------------------|
| embedding_dim=16 | Minimum viable dimension | Lower accuracy, faster training |
| embedding_dim=32 | Default setting | Balanced accuracy/efficiency |
| embedding_dim=64 | Higher capacity | Marginal accuracy gain |
| random_init | No cluster-based training | ~12.5% accuracy (baseline) |

---

## Appendix: Reference Implementations

### A1. Mamba Official Repository
- **Source:** https://github.com/state-spaces/mamba
- **Usage:** Pretrained models, hidden state extraction
- **Install:** `pip install mamba-ssm --no-build-isolation`

### A2. SuperGLUE Dataset
- **Source:** https://huggingface.co/datasets/super_glue
- **Usage:** Task data for embedding evaluation
- **Load:** `load_dataset('super_glue', task_name)`

### A3. Linear Probing References
- Alain & Bengio (2016): "Understanding intermediate layers using linear classifier probes"
- Standard practice for embedding quality evaluation

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- H-E1 completed: Cluster structure validated
- H-M1 started: Experiment design phase

---

*MCP Tools Used: WebFetch (Mamba repo, SuperGLUE dataset, Mamba paper)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

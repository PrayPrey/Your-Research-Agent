# Product Requirements Document: H-E1

**Date:** 2026-08-28
**Hypothesis:** Under transformer-to-SSM conversion training, if hidden states are clustered via self-supervised learning, then embeddings will show structure correlated with downstream task similarity.
**Type:** EXISTENCE (PoC)

---

## 1. Objective

Validate that transformer hidden states exhibit task-correlated clustering structure when evaluated on SuperGLUE tasks.

## 2. Scope

### In Scope
- Extract hidden states from pretrained BERT-base-uncased
- Apply K-means clustering (K=8) to [CLS] token embeddings
- Evaluate cluster-task correlation via purity, ARI, NMI
- Generate visualization figures

### Out of Scope
- Model training or fine-tuning
- SSM conversion (future hypotheses)
- Multi-seed experiments

## 3. Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Cluster Purity | > 0.125 | Primary (gate) |
| NMI | > 0.0 | Secondary |
| ARI | > 0.0 | Tertiary |

## 4. Functional Requirements

### FR-1: Data Pipeline
- Load all 8 SuperGLUE tasks via HuggingFace datasets
- Use full validation splits (~500-5000 samples per task)
- Tokenize with BERT tokenizer (max_length=512)

### FR-2: Hidden State Extraction
- Load BERT-base-uncased with `output_hidden_states=True`
- Extract last-layer [CLS] token embeddings
- Store with task labels

### FR-3: Clustering
- Apply KMeans with K=8, random_state=42
- Compute cluster assignments for all samples

### FR-4: Evaluation
- Calculate cluster purity, ARI, NMI
- Compare against random baseline (purity=0.125)

### FR-5: Visualization
- Bar chart: metrics vs thresholds
- t-SNE/UMAP: hidden states colored by task
- Save to `h-e1/figures/`

## 5. Technical Constraints

- Python 3.8+
- PyTorch, transformers, datasets, sklearn
- GPU optional (inference only)
- Single seed (42)

## 6. Deliverables

1. `run_experiment.py` - Main script
2. `04_validation.md` - Results report
3. `figures/` - Visualization outputs

---

*Generated for Phase 3 Implementation Planning*

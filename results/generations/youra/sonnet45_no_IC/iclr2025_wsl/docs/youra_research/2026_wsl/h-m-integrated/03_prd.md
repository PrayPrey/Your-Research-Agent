# Product Requirements Document: H-M-Integrated

**Date:** 2026-07-13  
**Hypothesis:** H-M-Integrated - Full CAPE Mechanism Validation  
**Author:** anonymous  
**Type:** MECHANISM  
**Status:** Draft

---

## Executive Summary

This PRD defines the implementation requirements for validating the full CAPE (Cross-Architecture Parameterized Encoder) mechanism. The system will implement a 3-component modular encoder (operation-specific encoders → contrastive projection → GNN residual) to achieve cross-architecture property prediction with ρ ≥0.65 on ResNet→ViT transfer, improving upon the SNE baseline (ρ=0.54) by at least 0.10 with statistical significance.

**Success Gate:** MUST_WORK - If full CAPE fails, PIVOT to Contrastive-Aligned variant (without GNN). Partial success triggers hyperparameter exploration.

---

## Problem Statement

### Research Context

Current weight-space encoders (SNE baseline) achieve limited cross-architecture transfer (ρ=0.54 for ResNet→ViT property prediction). The challenge is to design a modular encoder that:
1. Captures operation-specific weight signals (validated by prerequisite H-E1)
2. Creates metric space via contrastive alignment
3. Leverages architectural topology for improved transfer

### Prerequisites Satisfied

- **H-E1 (Operation-Specific Weight Signal Existence):** COMPLETED with PARTIAL validation
  - Binary classifier achieved 100% test accuracy distinguishing ResNet from ViT using operation-agnostic statistics
  - Validated that modular encoding is viable beyond tensor dimensions
  - Production validation pending with real HuggingFace models

### Hypothesis Statement

Under HuggingFace model zoos (400 models), if we implement the 3-component CAPE encoder (operation-specific encoders → contrastive projection → GNN residual), then cross-architecture property prediction correlation will reach ρ ≥0.65 on ResNet→ViT transfer.

---

## Functional Requirements

### FR-1: Dataset Collection and Preprocessing

**Priority:** P0 (Critical Path)  
**Complexity:** Medium

**Description:** Collect and preprocess 400 ImageNet-trained vision models from HuggingFace Model Hub across 4 architectures (ResNet-50, ViT-Base, MobileNetV2, EfficientNet-B0) with 100 models per architecture.

**Acceptance Criteria:**
- Programmatic collection via HuggingFace Hub API with filters: `task:image-classification AND dataset:imagenet-1k`
- Extract per model: full state_dict, layer statistics (Frobenius norms, spectral norms), architecture metadata, ImageNet top-1 accuracy
- Weight normalization: per-layer Frobenius norm normalization
- Train/val/test split: 70/15/15 per architecture
- Store preprocessed features for efficient loading during training
- Generate architecture DAG (directed acyclic graph) representations

**Dependencies:** HuggingFace Hub API access, sufficient storage (~50GB estimated)

---

### FR-2: Baseline Model Implementation (SNE)

**Priority:** P0 (Comparison Baseline)  
**Complexity:** Low

**Description:** Implement SNE set-encoding baseline for performance comparison. SNE uses permutation-invariant set aggregation without operation-specific components.

**Acceptance Criteria:**
- Architecture: DeepSets-style permutation-invariant encoder
- Input: Variable-size weight sets
- Output: Fixed-size embeddings (d=256)
- Property prediction: Linear probe on embeddings
- Reproduce known performance: ResNet→ViT cross-architecture ρ=0.54

**Dependencies:** None (standard architecture)

---

### FR-3: Component 1 - Operation-Specific Encoders

**Priority:** P0 (Core Component)  
**Complexity:** Very High

**Description:** Implement modular operation-specific encoders based on SANE (convolutional layers) and UNF (attention layers) principles, plus standard encoding for MLP layers.

**Acceptance Criteria:**
- **Conv Encoder (SANE-inspired):** Spatial tokenization preserving convolutional structure, output d=256
- **Attention Encoder (UNF-inspired):** Permutation-equivariant processing for attention weights, output d=256  
- **MLP Encoder:** Standard set encoding for fully-connected layers, output d=256
- Aggregation: Mean pooling across operation types → unified embedding z_op
- **Falsifier:** If cosine similarity between conv and attention embeddings >0.95 → modular encoding FAILED

**Dependencies:** FR-1 (preprocessed data with operation-type labels)

---

### FR-4: Component 2 - Contrastive Projection

**Priority:** P0 (Core Component)  
**Complexity:** High

**Description:** Implement InfoNCE contrastive learning module to create metric space for cross-architecture alignment.

**Acceptance Criteria:**
- Projection network: 2-layer MLP (d_z → d_z → d_z)
- Temperature: τ=0.07 (standard InfoNCE)
- L2 normalization before contrastive loss
- Training: Multi-task loss (λ_contrast=1.0, λ_property=0.5)
- Output: Normalized embeddings z_proj (d=256)
- **Falsifier:** If intra-architecture variance <0.1 OR distance-transfer correlation ρ<0.5 → alignment FAILED

**Dependencies:** FR-3 (operation-specific embeddings)

---

### FR-5: Component 3 - Architecture GNN Residual

**Priority:** P0 (Core Component)  
**Complexity:** High

**Description:** Implement 3-layer Graph Convolutional Network (GCN) operating on architecture DAG to extract topology signals, combined as learnable residual with contrastive embeddings.

**Acceptance Criteria:**
- GNN: 3-layer GCN processing architecture DAG (node_features, edge_index)
- Architecture embedding: d_arch=64
- Global graph pooling → single architecture embedding
- Projection to d_z=256 via linear layer
- Residual combination: z_final = z_proj + α * z_arch (α learnable)
- **Falsifier:** If α→0 OR adding z_arch decreases performance → GNN useless, degrade to Contrastive-Aligned variant

**Dependencies:** FR-1 (architecture DAGs), FR-4 (contrastive embeddings)

---

### FR-6: Full CAPE Integration and Training

**Priority:** P0 (Integration)  
**Complexity:** High

**Description:** Integrate all 3 components into unified CAPE encoder and implement training pipeline with combined loss function.

**Acceptance Criteria:**
- Forward pass: model_weights + arch_graph → z_final embeddings
- Loss function: InfoNCE (Component 2) + Property prediction MSE (on z_final)
- Optimizer: AdamW (lr=1e-4, weight_decay=1e-4)
- LR Schedule: Cosine annealing with 10% warmup
- Batch size: 32 models
- Epochs: 100 with early stopping (patience=10)
- Regularization: Dropout=0.1 in projector
- Seeds: Fixed at 42 for reproducibility

**Dependencies:** FR-3, FR-4, FR-5

---

### FR-7: Ablation Study - 4 Variants

**Priority:** P0 (Mechanism Validation)  
**Complexity:** Medium

**Description:** Implement and compare 4 model variants to validate each component's contribution.

**Acceptance Criteria:**
- **Variant 1:** SNE Baseline (FR-2)
- **Variant 2:** Operation-Only (FR-3 only, no contrastive or GNN)
- **Variant 3:** Op+Contrastive (FR-3 + FR-4, no GNN)
- **Variant 4:** Full CAPE (FR-3 + FR-4 + FR-5)
- Train all variants with identical hyperparameters
- Report per-variant: ResNet→ViT correlation ρ, training curves, component-specific diagnostics

**Dependencies:** FR-2, FR-6

---

### FR-8: Cross-Architecture Evaluation

**Priority:** P0 (Primary Metric)  
**Complexity:** Medium

**Description:** Evaluate Full CAPE and all baselines on cross-architecture property prediction across all architecture pairs.

**Acceptance Criteria:**
- Primary metric: Spearman correlation (ρ) between predicted and actual ImageNet top-1 accuracy
- Test on ResNet→ViT transfer (primary gate metric)
- Test on all 12 architecture pairs (4x4 matrix excluding self-transfer)
- Statistical test: Permutation test with 1000 iterations for ρ_CAPE - ρ_SNE ≥0.10, p<0.05
- Generate transfer matrix heatmap

**Dependencies:** FR-6, FR-7

---

### FR-9: Diagnostic Metrics and Component Falsifiers

**Priority:** P0 (Mechanism Validation)  
**Complexity:** Low

**Description:** Compute diagnostic metrics to validate each component's function and trigger falsifiers if components fail.

**Acceptance Criteria:**
- **Diagnostic 1 (Operation Encoders):** Cosine similarity between conv and attention embeddings
  - Target: <0.80 (distinct representations)
  - Falsifier: >0.95 → modular encoding failed
- **Diagnostic 2 (Contrastive Alignment):** Intra-architecture embedding variance (std)
  - Target: ≥0.15
  - Falsifier: <0.1 → alignment failed to preserve structure
- **Diagnostic 3 (GNN Residual):** Learned residual weight α
  - Target: α >0.1 AND performance with GNN ≥ without GNN
  - Falsifier: α→0 OR degradation → GNN useless
- Log all diagnostics during training and evaluation

**Dependencies:** FR-6

---

### FR-10: Visualization and Reporting

**Priority:** P1 (Required for validation)  
**Complexity:** Medium

**Description:** Generate comprehensive visualizations for hypothesis validation and result interpretation.

**Acceptance Criteria:**
- **Mandatory Figure:** Gate Metrics Comparison bar chart (ρ_CAPE, ρ_SNE, ρ_delta, Diagnostics 1-3) with threshold lines
- **Figure 1:** Cross-Architecture Transfer Matrix (12x12 heatmap of ρ values)
- **Figure 2:** Component Ablation bar chart (4 variants)
- **Figure 3:** Embedding Space Visualization (t-SNE/UMAP of z_proj colored by architecture)
- **Figure 4:** Operation Embedding Similarity Matrix (heatmap)
- **Figure 5:** GNN Residual Analysis (scatter: α vs performance gain)
- **Figure 6:** Training Curves (InfoNCE loss, Property MSE, Combined loss)
- Save all figures to `{hypothesis_folder}/figures/`

**Dependencies:** FR-8, FR-9

---

## Non-Functional Requirements

### NFR-1: Reproducibility

- Fixed random seeds (42) across all experiments
- Deterministic training (set PyTorch backend flags)
- Log all hyperparameters and model configurations
- Version control for data preprocessing scripts

### NFR-2: Computational Efficiency

- Batch loading with DataLoader workers
- Mixed precision training (FP16) if hardware supports
- Checkpoint saving every 10 epochs
- Resume capability from checkpoints

### NFR-3: Code Quality

- Modular architecture with separate files for each component
- Type hints for all functions
- Comprehensive logging (training metrics, validation metrics, diagnostics)
- Unit tests for data loading and preprocessing

### NFR-4: Documentation

- Inline comments explaining non-obvious design decisions
- README with setup instructions and usage examples
- Experiment configuration files (YAML/JSON)

---

## Data Specifications

### Input Data

| Data Type | Source | Format | Size |
|-----------|--------|--------|------|
| Model Weights | HuggingFace Hub | state_dict (PyTorch) | ~50GB total |
| Architecture Metadata | Model configs | JSON | ~10MB |
| Performance Labels | Model cards | CSV | ~100KB |

### Preprocessed Features

| Feature Type | Dimensions | Storage |
|--------------|------------|---------|
| Layer Statistics | Per-layer (variable) | HDF5 |
| Architecture DAGs | (nodes, edges) | NetworkX pickle |
| Embeddings | (B, 256) | Tensor files |

### Output Data

| Output Type | Format | Location |
|-------------|--------|----------|
| Trained Models | PyTorch checkpoint | `{hypothesis_folder}/checkpoints/` |
| Evaluation Results | JSON | `{hypothesis_folder}/results.json` |
| Figures | PNG | `{hypothesis_folder}/figures/` |

---

## Success Criteria

### Primary Gate Condition

**MUST_WORK Gate - Required for Validation:**
1. ✅ Full CAPE achieves ρ ≥0.65 on ResNet→ViT transfer
2. ✅ Statistical significance: ρ_CAPE - ρ_SNE ≥0.10 with p < 0.05

### Component Validation

**Diagnostic Thresholds:**
1. ✅ Diagnostic 1 (Operation Encoders): Cosine similarity <0.95
2. ✅ Diagnostic 2 (Contrastive Alignment): Intra-architecture variance ≥0.1
3. ✅ Diagnostic 3 (GNN Residual): α >0.1 OR performance improvement

### Fail Actions

| Scenario | Action |
|----------|--------|
| Primary gate fails | PIVOT to Contrastive-Aligned variant (no GNN) |
| Primary gate partial (0.60 ≤ ρ < 0.65) | EXPLORE hyperparameter tuning or larger model zoo |
| Diagnostic 1 fails | ABANDON modular encoding, fall back to SNE |
| Diagnostic 2 fails | Re-tune contrastive loss hyperparameters (τ, λ) |
| Diagnostic 3 fails | Degrade to Contrastive-Aligned (FR-3 + FR-4 only) |

---

## Dependencies and Prerequisites

### External Dependencies

- Python 3.8+
- PyTorch 2.0+
- HuggingFace Transformers and Hub libraries
- PyTorch Geometric (for GNN components)
- scikit-learn (for metrics)
- NetworkX (for graph structures)

### Prerequisite Hypotheses

- **H-E1:** COMPLETED (Operation-Specific Weight Signal Existence validated)
  - Lesson: Operation-agnostic statistics successfully distinguish architectures
  - Lesson: HuggingFace Model Hub is viable data source
  - Note: Production dataset collection is next critical step

### Baseline Reference

- SNE baseline: ρ=0.54 (ResNet→ViT) from literature
- SANE: +2.2% same-family improvement (ResNet-18→50)
- UNF: 10-15% improvement over non-equivariant

---

## Implementation Phases

### Phase 1: Environment and Data (FR-1, FR-2)
- Set up environment, install dependencies
- Implement HuggingFace data collection pipeline
- Implement SNE baseline
- **Estimated Complexity:** Medium

### Phase 2: Core Components (FR-3, FR-4, FR-5)
- Implement operation-specific encoders
- Implement contrastive projection module
- Implement GNN residual module
- **Estimated Complexity:** Very High

### Phase 3: Integration and Training (FR-6, FR-7)
- Integrate CAPE components
- Implement training loop with combined loss
- Run ablation study (4 variants)
- **Estimated Complexity:** High

### Phase 4: Evaluation and Validation (FR-8, FR-9, FR-10)
- Cross-architecture evaluation
- Diagnostic metrics computation
- Generate all visualizations
- Statistical significance testing
- **Estimated Complexity:** Medium

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| HuggingFace API rate limits | High | Batch requests, implement retry logic, cache downloads |
| GNN component provides no benefit | Medium | Design includes Diagnostic 3 falsifier, fallback to Contrastive-Aligned |
| Insufficient model diversity (400 models) | Medium | Partial success action: explore larger model zoo |
| Operation encoders collapse to identical representations | High | Diagnostic 1 falsifier triggers SNE fallback |
| Contrastive alignment destroys architectural structure | High | Diagnostic 2 monitors intra-architecture variance |

---

## Appendix

### Experiment Brief Source

Based on: `h-m-integrated/02c_experiment_brief.md` (Phase 2C output)

### Archon Research Summary

- **Query 1:** Weight-space encoder patterns → ControlNet discussions, Diffusers UNet patterns
- **Query 2:** Cross-architecture transfer → DALLE2 multi-stage encoder, CLIP contrastive learning
- **Query 3:** InfoNCE contrastive learning → Standard τ=0.07, projection d=256-512

### Reference Implementations

- DALLE2 cascading encoder: Multi-component composition pattern
- HuggingFace loading patterns: Model zoo collection
- SNE baseline: DeepSets-style set aggregation
- SANE/UNF: Paper principles (no author implementations available)

---

**Status:** Ready for Architecture Design (Step 3)  
**Next Phase:** Phase 3 Step 3 - Architecture Agent (Epic task breakdown)

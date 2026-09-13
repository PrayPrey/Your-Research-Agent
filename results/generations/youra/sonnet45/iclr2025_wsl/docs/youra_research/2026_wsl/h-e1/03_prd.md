---
stepsCompleted: 8
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-03-19T06:03:00Z
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document (PRD): H-E1 CAWE Implementation

**Hypothesis:** h-e1 (EXISTENCE)
**Date:** 2026-03-19
**Author:** Anonymous
---

## Executive Summary

Implement a Compositional Architecture-Agnostic Weight Encoder (CAWE) to validate the existence hypothesis: that a heterogeneous model zoo encoder can achieve Spearman ρ > 0.7 for generalization gap prediction across CNN, Transformer, and MLP architectures. The system combines architecture-specific tokenizers with a shared Neural Functional Transformer (NFT) backbone to process model weights as a new data modality.

**Success Criteria:** Spearman ρ > 0.7 (95% CI lower bound) on 150-model held-out test set, demonstrating architecture-agnostic weight-space learning.

---

## Problem Statement

Current weight-space learning methods operate on homogeneous model zoos (single architecture family). We need to validate whether compositional tokenization + NFT attention can enable cross-architecture generalization gap prediction from heterogeneous model populations (CNNs + Transformers + MLPs).

**Research Gap:** No existing implementation demonstrates architecture-agnostic weight encoding across heterogeneous families with >0.7 correlation for generalization prediction.

---

## Functional Requirements

### FR-1: Model Zoo Dataset Construction
- **ID:** FR-1
- **Priority:** P0 (CRITICAL)
- **Description:** Assemble heterogeneous model zoo with 750 models (250 ViT, 250 CNN, 250 MLP)
- **Acceptance Criteria:**
  - ViT models: 250 models from HuggingFace `timm` library (vit_base_patch16_224, vit_large_patch16_224, etc.)
  - CNN models: 250 models from torchvision.models (ResNet, VGG, etc.)
  - MLP models: 250 models from Unterthiner MNIST MLPs (Zenodo 5645138) or generated
  - Each model includes: weights (.pt/.pth), generalization gap metadata (train_acc - test_acc)
  - Stratified train/test split: 600 train (200/200/200 per family), 150 test (50/50/50 per family)
- **Data Spec:**
  - Input: HuggingFace API, torchvision API, Zenodo download
  - Output: `data/model_zoo/` with subdirs `vit/`, `cnn/`, `mlp/`
  - Format: PyTorch state_dict (.pt) + metadata JSON

### FR-2: Architecture-Specific Tokenizers
- **ID:** FR-2
- **Priority:** P0 (CRITICAL)
- **Description:** Implement 3 tokenizers to project architecture-specific weights to D-dimensional tokens
- **Acceptance Criteria:**
  - CNN Tokenizer: Extract conv kernels → flatten → project to D=128 tokens
  - Transformer Tokenizer: Extract Q/K/V matrices → project to D=128 tokens
  - MLP Tokenizer: Extract weight matrices → project to D=128 tokens
  - All tokenizers output (num_layers, D) token sequences
- **Implementation:** `cawe/tokenizers/` module with `CNNTokenizer`, `TransformerTokenizer`, `MLPTokenizer` classes

### FR-3: NFT Backbone Integration
- **ID:** FR-3
- **Priority:** P0 (CRITICAL)
- **Description:** Integrate Neural Functional Transformer backbone from `nfn` library
- **Acceptance Criteria:**
  - Install `nfn` library: `pip install nfn`
  - Use NPLinear layers for permutation-equivariant weight processing
  - Architecture: NPLinear(128, 64) → ReLU → NPLinear(64, 128) → ReLU → NPLinear(128, 128)
  - Process tokenized weights from FR-2 tokenizers
- **Dependencies:** github.com/AllanYangZhou/nfn (NeurIPS 2023)

### FR-4: CAWE Model Implementation
- **ID:** FR-4
- **Priority:** P0 (CRITICAL)
- **Description:** Implement compositional CAWE architecture combining tokenizers + NFT + regression head
- **Acceptance Criteria:**
  - `CAWE` class with forward(weights, arch_family) method
  - Architecture-specific tokenization dispatch (FR-2)
  - Shared NFT backbone processing (FR-3)
  - Global average pooling over token sequences
  - Regression head: Linear(128, 64) → ReLU → Dropout(0.1) → Linear(64, 1)
  - Output: Generalization gap prediction (continuous value)
- **Implementation:** `cawe/models/cawe.py`

### FR-5: Baseline Model - Flat-Weight MLP
- **ID:** FR-5
- **Priority:** P0 (CRITICAL)
- **Description:** Implement naive baseline for Δρ comparison
- **Acceptance Criteria:**
  - Input: Flattened weight vector (concatenate all model weights)
  - Architecture: Linear(input_dim, 512) → ReLU → Dropout(0.2) → Linear(512, 256) → ReLU → Dropout(0.2) → Linear(256, 128) → ReLU → Linear(128, 1)
  - No tokenization, no architectural awareness
  - Used for baseline comparison (Δρ = ρ_CAWE - ρ_baseline > 0.15)
- **Implementation:** `cawe/baselines/flat_mlp.py`

### FR-6: Training Pipeline
- **ID:** FR-6
- **Priority:** P0 (CRITICAL)
- **Description:** Implement training loop for CAWE and baseline models
- **Acceptance Criteria:**
  - Optimizer: AdamW (lr=1e-4, weight_decay=1e-2)
  - Loss: MSE (generalization gap regression)
  - Batch size: 32
  - Epochs: 100 with early stopping (patience=10 on validation Spearman ρ)
  - Training data: 600 models (stratified 200/200/200)
  - Validation monitoring: Compute Spearman ρ every epoch
- **Implementation:** `scripts/train.py`

### FR-7: Evaluation Pipeline
- **ID:** FR-7
- **Priority:** P0 (CRITICAL)
- **Description:** Evaluate models on held-out test set with primary/secondary metrics
- **Acceptance Criteria:**
  - **Primary Metric:** Spearman ρ with bootstrap 95% CI (1000 resamples)
    - Success: ρ > 0.7 AND 95% CI lower bound > 0.7
  - **Secondary Metric:** Per-architecture Spearman ρ (CNN, Transformer, MLP subsets)
    - Success: All three ρ > 0.65
  - **Baseline Comparison:** Δρ = ρ_CAWE - ρ_baseline
    - Success: Δρ > 0.15
  - Test data: 150 models (50/50/50 per family)
- **Implementation:** `scripts/evaluate.py` using `scipy.stats.spearmanr`

### FR-8: Visualization Generation
- **ID:** FR-8
- **Priority:** P1 (HIGH)
- **Description:** Generate figures for hypothesis validation report
- **Acceptance Criteria:**
  - **Mandatory Figure:** Spearman ρ comparison (CAWE vs Baseline) with 95% CI error bars
  - **Additional Figures:**
    - Per-architecture performance bar chart (ρ for CNN/Transformer/MLP)
    - Prediction scatter plot (predicted vs actual gap, 150 test models)
    - Architecture clustering t-SNE (CAWE embeddings colored by family)
  - All figures saved to `{hypothesis_folder}/figures/`
- **Implementation:** `scripts/visualize.py` using matplotlib/seaborn

### FR-9: Experiment Configuration
- **ID:** FR-9
- **Priority:** P1 (HIGH)
- **Description:** Externalize hyperparameters and settings via configuration
- **Acceptance Criteria:**
  - Configuration format: Hardcoded constants or argparse (LIGHT tier - minimal infrastructure)
  - Configurable parameters: lr, batch_size, epochs, D (token_dim), seed
  - Default values from Phase 2C: lr=1e-4, batch_size=32, epochs=100, D=128, seed=42
- **Implementation:** Config constants in `train.py` or argparse CLI

### FR-10: Logging and Checkpointing
- **ID:** FR-10
- **Priority:** P2 (MEDIUM)
- **Description:** Basic experiment tracking for reproducibility
- **Acceptance Criteria:**
  - Print training progress (epoch, train_loss, val_spearman) to stdout
  - Save best model checkpoint based on validation Spearman ρ
  - Save final metrics to CSV: `results/h-e1_metrics.csv`
  - CSV columns: model_name, test_spearman, test_spearman_ci_lower, test_spearman_ci_upper, per_arch_spearman
- **Implementation:** Print statements + torch.save() + pandas.to_csv()

---

## Non-Functional Requirements

### NFR-1: Performance
- Training time: < 2 hours on single GPU for 100 epochs (600 models, batch_size=32)
- Inference time: < 1 second per model for generalization gap prediction

### NFR-2: Reproducibility
- Fixed random seed (42) for data splits, weight initialization, training
- Deterministic operations where possible (torch.backends.cudnn.deterministic=True)

### NFR-3: Code Quality
- LIGHT tier: Minimal structure, focus on functionality
- Single script execution: `python train.py` runs full experiment
- Basic error handling for file I/O and GPU availability

### NFR-4: Resource Constraints
- GPU: Single GPU (user selects via CUDA_VISIBLE_DEVICES)
- Memory: Fits model zoo + CAWE model in GPU memory (estimated < 16GB)
- Disk: Model zoo ~2GB, checkpoints ~500MB

---

## Dependencies

### Core Dependencies
- PyTorch >= 2.0
- `nfn` library (pip install nfn) - NFT backbone implementation
- `timm` library - ViT model zoo
- `torchvision` - CNN model zoo
- `scipy` - Spearman correlation computation
- `numpy` - Numerical operations
- `pandas` - Metrics CSV export
- `matplotlib`, `seaborn` - Visualization
- `scikit-learn` - t-SNE for clustering visualization

### Data Dependencies
- HuggingFace `timm` model repository (ViT models)
- PyTorch `torchvision.models` (CNN models)
- Zenodo 5645138 (Unterthiner MNIST MLPs) or generate locally

---

## Success Criteria

### Primary Success (Gate: MUST_WORK)
1. **PoC Pass Condition:**
   - Code runs without error
   - CAWE Spearman ρ > Baseline Spearman ρ

2. **Hypothesis Validation:**
   - CAWE Spearman ρ > 0.7 on test set
   - 95% CI lower bound > 0.7
   - Demonstrates architecture-agnostic weight learning

### Secondary Success
- Per-architecture ρ > 0.65 for CNN, Transformer, MLP subsets
- Δρ > 0.15 (CAWE outperforms flat-weight baseline)
- Architecture clustering visible in t-SNE (family separation)

### Failure Response
- If ρ < 0.7 → MUST_WORK gate fails → ABANDON hypothesis → ROUTE_TO_PHASE_0

---

## Out of Scope

- **NOT in scope (LIGHT tier):**
  - Structured logging (WandB, TensorBoard)
  - Unit tests (PoC validation only)
  - Hyperparameter tuning (use Phase 2C defaults)
  - YAML configuration files (use hardcoded/argparse)
  - Multi-seed runs (single seed=42)
  - Advanced baselines (random forest, etc.) - deferred to h-m-integrated

---

## Implementation Notes

### Reference Implementation
- **Primary:** github.com/AllanYangZhou/nfn (NeurIPS 2023) - Official NFT library
- **Installation:** `pip install nfn`
- **Key Classes:** `NPLinear`, `TupleOp`, `state_dict_to_tensors`, `network_spec_from_wsfeat`

### Architecture-Specific Tokenization Strategy
Based on NFT library usage patterns:
- **CNN:** Extract conv layer weights (kernel tensors) → flatten → project
- **Transformer:** Extract attention matrices (Q/K/V) → project
- **MLP:** Extract FC layer weights → project
- All project to shared D=128 dimensional token space for NFT processing

### Model Zoo Assembly
1. ViT: `timm.create_model('vit_base_patch16_224', pretrained=True)` and variants
2. CNN: `torchvision.models.resnet50(pretrained=True)` and variants
3. MLP: Generate MNIST-trained MLPs or download Unterthiner dataset

---

## Phase 2C Completeness Check

✅ **Dataset:** Heterogeneous Model Zoo (ViT 250, CNN 250, MLP 250) - COVERED (FR-1)
✅ **Baseline Model:** Flat-weight MLP - COVERED (FR-5)
✅ **Proposed Model:** CAWE (tokenizers + NFT + regression head) - COVERED (FR-2, FR-3, FR-4)
✅ **Training Protocol:** AdamW, lr=1e-4, batch_size=32, epochs=100, early stopping - COVERED (FR-6)
✅ **Primary Metric:** Spearman ρ with bootstrap 95% CI - COVERED (FR-7)
✅ **Secondary Metric:** Per-architecture ρ - COVERED (FR-7)
✅ **Baseline Comparison:** Δρ metric - COVERED (FR-7)
✅ **Visualization:** Gate metrics figure + additional figures - COVERED (FR-8)
✅ **Dependencies:** nfn library, timm, torchvision - COVERED (Dependencies section)

---

*Generated by Phase 3 Implementation Planning - Step 2 (PRD Generation)*
*Source: h-e1/02c_experiment_brief.md (Phase 2C Level 1.5 specification)*
*Next: Architecture Design (Step 3)*

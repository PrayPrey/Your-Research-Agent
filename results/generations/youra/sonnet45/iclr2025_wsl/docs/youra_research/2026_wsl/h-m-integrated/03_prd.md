---
stepsCompleted: 8
hypothesis_id: h-m-integrated
hypothesis_type: MECHANISM
created_at: 2026-03-19T08:05:00Z
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document (PRD): H-M-Integrated CAWE Mechanism Validation

**Hypothesis:** h-m-integrated (MECHANISM)
**Date:** 2026-03-19
**Author:** Anonymous
---

## Executive Summary

Validate the compositional mechanism of CAWE (Compositional Architecture-Agnostic Weight Encoder) through 5-component multi-faceted validation: (1) per-family ablation demonstrating ρ > 0.7 for each architecture subset, (2) architecture clustering with silhouette > 0.5, (3) flat-weight baseline outperformance Δρ > 0.15, (4) random forest OOD comparison Δρ > 0.1, and (5) robustness validation across tokenization variants and hyperparameters.

**Success Criteria:** SHOULD_WORK gate - At least 3/5 components pass thresholds, demonstrating compositional mechanism preserves architecture-specific signals while enabling cross-architecture learning.

---

## Problem Statement

The h-e1 hypothesis validated CAWE's basic existence (ρ=0.294, per-architecture variability observed). We now need to validate the compositional mechanism itself: whether architecture-specific tokenization → shared token space → NFT permutation-equivariant attention actually preserves architecture-family structure while enabling shared learning across heterogeneous model weights.

**Research Gap:** No existing validation demonstrates that compositional weight encoders preserve architectural signals in embeddings while outperforming both naive vectorization and hand-crafted feature baselines.

---

## Functional Requirements

### FR-1: Reuse h-e1 Model Zoo Dataset
- **ID:** FR-1
- **Priority:** P0 (CRITICAL)
- **Description:** Reuse validated heterogeneous model zoo from h-e1 for controlled comparison
- **Acceptance Criteria:**
  - Same 750 models (250 ViT, 250 CNN, 250 MLP) from h-e1
  - Same stratified 80/20 split (600 train, 150 test)
  - Same generalization gap metadata
  - Data location: Reference h-e1 dataset or regenerate identically
- **Data Spec:**
  - Input: h-e1 data pipeline or equivalent
  - Output: `data/model_zoo/` (shared with h-e1 or copied)
  - Format: PyTorch state_dict (.pt) + metadata JSON

### FR-2: Reuse h-e1 CAWE Implementation
- **ID:** FR-2
- **Priority:** P0 (CRITICAL)
- **Description:** Reuse validated CAWE implementation from h-e1 (architecture-specific tokenizers + NFT backbone + regression head)
- **Acceptance Criteria:**
  - Same CAWE architecture from h-e1 (CNNTokenizer, TransformerTokenizer, MLPTokenizer)
  - Same NFT backbone from `nfn` library
  - Same training hyperparameters (AdamW, lr=1e-4, batch=32, epochs=100)
  - Code reuse: Import from h-e1 implementation or copy validated modules
- **Dependencies:** h-e1 codebase, `nfn` library

### FR-3: Per-Family Ablation Training (Component 1)
- **ID:** FR-3
- **Priority:** P0 (CRITICAL)
- **Description:** Train 3 separate CAWE models on single-family subsets to validate per-family performance
- **Acceptance Criteria:**
  - **CNN-only:** Train on 200 CNN models, evaluate on 50 CNN test → ρ_cnn > 0.7
  - **Transformer-only:** Train on 200 Transformer models, evaluate on 50 Transformer test → ρ_transformer > 0.7
  - **MLP-only:** Train on 200 MLP models, evaluate on 50 MLP test → ρ_mlp > 0.7
  - Same hyperparameters as full training (controlled comparison)
  - All 3 thresholds must pass for component success
- **Implementation:** `scripts/train_per_family.py` with family argument

### FR-4: Architecture Clustering Validation (Component 2)
- **ID:** FR-4
- **Priority:** P0 (CRITICAL)
- **Description:** Extract CAWE embeddings and compute silhouette score for architecture-family separation
- **Acceptance Criteria:**
  - Extract embeddings from CAWE NFT backbone (before regression head) for all 750 models
  - Embedding dimension: Output of NFT final layer (128-dimensional)
  - Compute silhouette score with 3-cluster labels (CNN=0, Transformer=1, MLP=2)
  - Success threshold: silhouette > 0.5
  - Use sklearn.metrics.silhouette_score or PyTorch-Ignite
- **Implementation:** `scripts/evaluate_clustering.py`

### FR-5: Flat-Weight MLP Baseline (Component 3)
- **ID:** FR-5
- **Priority:** P0 (CRITICAL)
- **Description:** Implement and train flat-weight MLP baseline for Δρ comparison
- **Acceptance Criteria:**
  - Input: Concatenated flattened weights (no tokenization)
  - Architecture: Linear(max_weight_dim, 512) → ReLU → Linear(512, 256) → ReLU → Linear(256, 1)
  - Zero-padding for variable-length weight vectors
  - Train on same 600 models with same hyperparameters (AdamW, lr=1e-4, batch=32, epochs=100)
  - Evaluate on same 150-model test set
  - Δρ = ρ_CAWE - ρ_flat_mlp > 0.15
  - Statistical test: Paired t-test (p < 0.001)
- **Implementation:** `cawe/baselines/flat_mlp.py`

### FR-6: Random Forest Baseline (Component 4)
- **ID:** FR-6
- **Priority:** P0 (CRITICAL)
- **Description:** Implement random forest on engineered features for OOD comparison
- **Acceptance Criteria:**
  - **Feature extraction:**
    - Layer-wise L2 norms (per weight matrix)
    - Weight sparsity (% of near-zero weights, threshold=1e-5)
    - Spectral radius (largest eigenvalue per layer)
    - Weight mean/std statistics per layer
  - **Model:** sklearn.ensemble.RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
  - Train on same 600 models, evaluate on 150-model test set
  - Δρ = ρ_CAWE - ρ_RF > 0.1
  - Statistical test: Wilcoxon signed-rank (p < 0.01)
  - OOD evaluation: If Unterthiner MLP subset available, test RF vs CAWE on OOD set
- **Implementation:** `cawe/baselines/random_forest.py`

### FR-7: Robustness Ablation Validation (Component 5)
- **ID:** FR-7
- **Priority:** P1 (HIGH)
- **Description:** Test robustness across tokenization variants and hyperparameters
- **Acceptance Criteria:**
  - **Tokenization variants (test 4):**
    - Variant 1: Different token dimension projection (D=64 instead of 128)
    - Variant 2: Different token dimension (D=256)
    - Variant 3: Alternative layer selection for tokenization
    - Variant 4: Weight normalization variant
    - Success: 2/4 variants achieve ρ > 0.65
  - **Hyperparameter robustness (test 3 D-values):**
    - D=64, D=128 (baseline), D=256
    - Success: 2/3 achieve ρ > 0.65
  - Same train/test split, same training protocol
- **Implementation:** `scripts/ablation_robustness.py` with variant arguments

### FR-8: Evaluation Pipeline for 5 Components
- **ID:** FR-8
- **Priority:** P0 (CRITICAL)
- **Description:** Comprehensive evaluation pipeline tracking all 5 component metrics
- **Acceptance Criteria:**
  - **Component 1 (Per-family):** Track ρ_cnn, ρ_transformer, ρ_mlp with thresholds
  - **Component 2 (Clustering):** Track silhouette score
  - **Component 3 (Flat baseline):** Track Δρ_flat with paired t-test p-value
  - **Component 4 (RF baseline):** Track Δρ_RF with Wilcoxon p-value
  - **Component 5 (Robustness):** Track pass counts for variants
  - **Overall:** Pass/Fail status for each component + total passed (≥3 for gate)
  - Save all metrics to CSV: `results/h-m-integrated_metrics.csv`
- **Implementation:** `scripts/evaluate_mechanism.py`

### FR-9: Visualization Generation for 5 Components
- **ID:** FR-9
- **Priority:** P1 (HIGH)
- **Description:** Generate comprehensive figures showing all component results
- **Acceptance Criteria:**
  - **Mandatory Figure (Gate Metrics):** Component pass/fail matrix (5 components × Pass/Fail)
  - **Per-family Figure:** Bar chart with ρ_cnn, ρ_transformer, ρ_mlp vs threshold (0.7 line)
  - **Clustering Figure:** t-SNE scatter plot of 750 embeddings colored by architecture family, annotated with silhouette score
  - **Baseline Comparison Figure:** Grouped bar chart (CAWE vs Flat-MLP vs RF) with error bars, Δρ annotations
  - **Robustness Figure:** Heatmap grid (tokenization variants × D-values) showing ρ values with pass/fail colors
  - All figures saved to `{hypothesis_folder}/figures/`
- **Implementation:** `scripts/visualize_mechanism.py`

### FR-10: Experiment Configuration
- **ID:** FR-10
- **Priority:** P1 (HIGH)
- **Description:** Externalize experiment parameters for reproducibility
- **Acceptance Criteria:**
  - Configuration format: Hardcoded constants or argparse (FULL tier accepts either)
  - Configurable parameters: lr, batch_size, epochs, D (token_dim), seed, component_thresholds
  - Default values from Phase 2C:
    - lr=1e-4, batch_size=32, epochs=100, D=128, seed=42
    - Component thresholds: ρ_family=0.7, silhouette=0.5, Δρ_flat=0.15, Δρ_RF=0.1, robustness=2/4
- **Implementation:** Config constants or argparse in main scripts

### FR-11: Logging and Checkpointing
- **ID:** FR-11
- **Priority:** P2 (MEDIUM)
- **Description:** Track component-wise results for mechanism validation
- **Acceptance Criteria:**
  - Print component results to stdout (Component 1: PASS/FAIL, Component 2: ...)
  - Save per-component metrics to CSV
  - Save best model checkpoints for each ablation variant
  - Final summary: "h-m-integrated: 4/5 components PASSED → SHOULD_WORK gate SATISFIED"
- **Implementation:** Print statements + torch.save() + pandas.to_csv()

---

## Non-Functional Requirements

### NFR-1: Performance
- Training time: < 3 hours total for all 5 components (per-family ablations, full training, baselines, robustness)
- Inference time: < 5 seconds total for clustering validation (750 embeddings)

### NFR-2: Reproducibility
- Fixed random seed (42) for all experiments
- Deterministic operations (torch.backends.cudnn.deterministic=True)
- Same data splits across all components

### NFR-3: Code Quality
- FULL tier: Modular structure with separate scripts per component
- Clear component separation: `train_*.py`, `evaluate_*.py`, `visualize_*.py`
- Comprehensive error handling for component failures

### NFR-4: Resource Constraints
- GPU: Single GPU (user selects via CUDA_VISIBLE_DEVICES)
- Memory: Multiple model training runs (sequential, not parallel) to fit in GPU memory
- Disk: Reuse h-e1 dataset (~2GB), additional checkpoints for ablations (~1GB)

---

## Dependencies

### Core Dependencies
- PyTorch >= 2.0
- `nfn` library (pip install nfn) - NFT backbone (reuse from h-e1)
- `timm` library - ViT model zoo (reuse from h-e1)
- `torchvision` - CNN model zoo (reuse from h-e1)
- `scipy` - Spearman correlation, statistical tests
- `scikit-learn` - silhouette_score, RandomForestRegressor, t-SNE
- `numpy` - Numerical operations
- `pandas` - Metrics CSV export
- `matplotlib`, `seaborn` - Visualization

### Data Dependencies
- h-e1 model zoo dataset (750 models) - reuse or regenerate

### Code Dependencies
- h-e1 CAWE implementation (tokenizers, NFT backbone, training pipeline) - reuse validated code

---

## Success Criteria

### Primary Success (Gate: SHOULD_WORK)
1. **PoC Pass Condition:**
   - Code runs without error for all 5 components
   - At least 2/5 components pass thresholds

2. **Hypothesis Validation:**
   - At least 3/5 components pass thresholds:
     - Component 1: All 3 per-family ρ > 0.7
     - Component 2: Silhouette > 0.5
     - Component 3: Δρ_flat > 0.15 (p < 0.001)
     - Component 4: Δρ_RF > 0.1 (p < 0.01)
     - Component 5: 2/4 tokenization variants + 2/3 D-values pass
   - Demonstrates compositional mechanism validity

### Secondary Success
- All 5/5 components pass (FULL mechanism validation)
- Per-architecture ρ shows CNN ≈ MLP > Transformer pattern (consistent with h-e1)
- Architecture clustering shows clear family separation in t-SNE

### Failure Response
- If 0-2/5 components pass → SHOULD_WORK gate PARTIAL → Document limitations, proceed to next hypothesis
- If fundamental design issue (0/5 pass) → PIVOT or EXPLORE alternative tokenization strategies

---

## Out of Scope

- **NOT in scope (deferred to future hypotheses):**
  - Scale-up experiments (Falcon 70B, larger model zoos) - deferred to h-c1
  - Advanced tokenization (Transformer-NFN integration) - future work
  - Multi-seed statistical robustness (single seed=42 for mechanism validation)
  - Hyperparameter tuning (use h-e1 validated defaults)
  - Advanced baselines beyond flat-weight and random forest

---

## Implementation Notes

### Code Reuse Strategy
- **Primary:** Reuse h-e1 validated CAWE implementation
  - Import tokenizers, NFT backbone, training loop
  - Extend with per-family ablation wrapper
  - Add clustering evaluation module
  - Add baseline comparison modules

### Baseline Implementation Patterns
- **Flat-weight MLP:** Standard PyTorch MLP with zero-padding for variable-length inputs
- **Random Forest:** sklearn with standard feature engineering (L2 norms, sparsity, spectral radius)

### Statistical Testing
- **Paired t-test:** For flat-weight baseline (paired predictions on same 150 models)
- **Wilcoxon signed-rank:** For random forest OOD comparison (non-parametric)
- Use scipy.stats for both tests

### Component Isolation
- Each component (1-5) should be independently executable
- Failure in one component should not block others
- Final report aggregates all component results

---

## Phase 2C Completeness Check

✅ **Dataset:** Heterogeneous Model Zoo (reuse h-e1) - COVERED (FR-1)
✅ **CAWE Model:** Reuse h-e1 implementation - COVERED (FR-2)
✅ **Component 1:** Per-family ablation (3 experiments) - COVERED (FR-3)
✅ **Component 2:** Architecture clustering (silhouette) - COVERED (FR-4)
✅ **Component 3:** Flat-weight baseline comparison - COVERED (FR-5)
✅ **Component 4:** Random forest baseline - COVERED (FR-6)
✅ **Component 5:** Robustness validation - COVERED (FR-7)
✅ **Evaluation:** 5-component metrics - COVERED (FR-8)
✅ **Visualization:** Gate metrics + component figures - COVERED (FR-9)
✅ **Statistical Tests:** Paired t-test, Wilcoxon signed-rank - COVERED (FR-5, FR-6)
✅ **Dependencies:** nfn, sklearn, scipy - COVERED (Dependencies section)

---

*Generated by Phase 3 Implementation Planning - Step 2 (PRD Generation)*
*Source: h-m-integrated/02c_experiment_brief.md (Phase 2C Level 1.5 specification)*
*Next: Architecture Design (Step 3)*

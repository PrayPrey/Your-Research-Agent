# Hypothesis Context: h-m-integrated

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-19
**Main Hypothesis:** H-CAWE-v1 - Compositional Architecture-Agnostic Weight Encoder
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under CAWE training on heterogeneous model zoo, if the compositional mechanism (architecture-specific tokenization → shared token space → NFT permutation-equivariant attention → generalization gap prediction) is applied, then (1) per-family ablation achieves ρ > 0.7 for CNN/Transformer/MLP subsets, (2) architecture clustering silhouette > 0.5 in embeddings, (3) baseline outperformance Δρ > 0.15 vs flat-weight MLP and Δρ > 0.1 vs random forest on OOD tests, because the compositional design preserves architecture-specific signals while enabling cross-architecture learning.

### Type
MECHANISM

### Rationale
Validates the three-step causal chain and compositional design principles. Demonstrates that shared token space does NOT destroy architecture-specific information (per-family ablation) and that learned representations outperform both naive approaches (flat-weight) and hand-crafted features (random forest).

---

## Verification Protocol

### Conceptual Test
1. **Per-family ablation:** Train CAWE on single-family subsets (200 CNN-only, 200 Transformer-only, 200 MLP-only), evaluate on corresponding 50-model held-outs, measure ρ for each
2. **Clustering validation:** Extract CAWE embeddings for all 750 models, compute t-SNE projection, measure silhouette score with architecture-family labels (3 clusters)
3. **Baseline comparison (flat-weight):** Train MLP on concatenated weights (no tokenization), compare via paired t-test on 150-model test set
4. **Baseline comparison (random forest):** Train RF on engineered features (layer L2 norms, sparsity, spectral radius), evaluate on OOD sets (Unterthiner/NeurIPS 2021 MLPs), compare via Wilcoxon signed-rank
5. **Robustness ablations:** Test 4 tokenization variants (2/4 must achieve ρ > 0.65), test 3 D-values (2/3 must achieve ρ > 0.65)

### Success Criteria
**Primary:** All 3 per-family ρ > 0.7, silhouette > 0.5, Δρ > 0.15 flat (p<0.001), Δρ > 0.1 RF on OOD (p<0.01)

**Secondary:** Tokenization robustness (2/4 variants), hyperparameter robustness (2/3 D-values), attention head specialization visible

### Variables
- **Independent Variable:** Tokenization Strategy (statistics/spectral/learned/SANE), Token Dimension D (64/128/256)
- **Dependent Variable:** Architecture Clustering Quality (silhouette score), Baseline Performance Delta (Δρ)
- **Controlled Variables:** Dataset Split (80/20 stratified, seed=42), NFT Hyperparameters, Training Procedure (AdamW, lr=1e-4, batch=32, 100 epochs)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Heterogeneous Model Zoo (750 models)
- **Type:** standard
- **Source:** ViT Model Zoo (250), torchvision.models (250), Unterthiner MNIST MLPs (250)
- **Path:** github.com/ModelZoos/ViTModelZoo + torchvision.models + Zenodo 5645138
- **Hypothesis Fit:** Provides 3-family heterogeneous validation (CNN, Transformer, MLP) at manageable scale. All datasets publicly available. ViT Zoo designed for model population research.

### Selected Model
- **Name:** Compositional Architecture-Agnostic Weight Encoder (CAWE)
- **Type:** Neural Functional Transformer with Architecture-Specific Tokenizers
- **Source:** nfn library (PyPI: pip install nfn) for NFT backbone + custom tokenizers
- **Hypothesis Fit:** NFT proven on MNIST MLPs. Architecture-specific tokenizers project to shared token space. Hybrid approach: arch-specific preprocessing + arch-agnostic processing.

---

## Baseline & Comparison Targets

### Baseline Methods
1. **NFT on MNIST MLPs:** +17% INR classification improvement on MNIST FC-MLP zoo (homogeneous, single architecture family)
2. **DWSNets permutation equivariance:** Runtime failure on FC-MLP weights (designed for CNN weights, failed on non-CNN architectures)
3. **SANE sequential tokenization:** Demonstrated scalability on large models (proof of tokenization viability on diverse architectures)

### Baseline Performance
- Flat-weight MLP baseline (expected)
- Random forest on engineered features (expected)

### Gap Analysis
First empirical validation of architecture-agnostic weight encoders on truly heterogeneous multi-family model zoo. Prior NFT work limited to homogeneous MNIST MLPs. Universal NFNs provided theoretical claims without large-scale heterogeneous validation.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1:** MUST_WORK gate (PASSED) - Cross-architecture generalization existence validated (ρ=0.294 on reduced-scale PoC)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:**
- If all components fail: Fundamental design issue → PIVOT to architecture-specific embeddings OR EXPLORE GNN-based explicit graph structure
- If partial: Document working components, prioritize refinement

**Phase Assignment:** Phase 2 (Mechanism Validation)

**Estimated Duration:** 3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
h-m-integrated builds on h-e1's validated CAWE architecture. Where h-e1 demonstrated cross-architecture generalization exists, h-m-integrated validates the compositional mechanism's components: per-family signal preservation, architecture clustering, baseline outperformance, and robustness.

### Components
1. **Per-family ablation** (All 3 families ρ > 0.7)
2. **Architecture clustering** (Silhouette > 0.5)
3. **Flat-weight baseline** (Δρ > 0.15, paired t-test p<0.001)
4. **Random forest baseline on OOD** (Δρ > 0.1, Wilcoxon p<0.01)
5. **Robustness validation** (2/4 tokenization, 2/3 D-values, adversarial ρ > 0.65, OOD ρ > 0.6/0.55)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C started)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Previous validation context from h-e1 (real data confirmed, PoC validated)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design per-family ablation experiments
4. Design clustering validation experiments
5. Design baseline comparison experiments (flat-weight MLP, random forest)
6. Design robustness ablations
7. Output: h-m-integrated/02c_experiment_brief.md

**Key Context from h-e1:**
- CAWE architecture validated and functional
- Real pretrained models confirmed (no synthetic data)
- NFT backbone integration successful
- Full-scale 750-model zoo needed for target performance
- Per-architecture ρ varied: CNN=0.661, MLP=0.624, Transformer=0.0

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*

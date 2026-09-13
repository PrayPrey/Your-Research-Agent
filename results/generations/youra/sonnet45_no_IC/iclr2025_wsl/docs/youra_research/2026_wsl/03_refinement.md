# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-13T13:35:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap2
- **Gap Title**: Limited Cross-Architecture Weight Embedding Generalization Methods
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 9

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 9

**Convergence Reason**: All 6 criteria met - hypothesis is specific (Under-If-Then-Because format), mechanistic (3-component encoder), falsifiable (P1-P3 with thresholds), novel (paradigm shift from invariance to parameterization), feasible (implementable components), and objections resolved (falsifiability via ablation, incommensurability via modular encoders, alignment via contrastive projection)

### Key Insights

**Exchange 1 (Dr. Nova):** The 33% cross-architecture performance drop (SNE: ρ=0.81 within-architecture → ρ=0.54 cross-architecture) is not failure, it's a SIGNAL quantifying architectural distance. Proposed architecture-parameterized embeddings with architecture conditioning.

**Exchange 2 (Prof. Vera):** Challenged architectural distance claim - needs explicit non-circular definition and falsification criteria. Demanded concrete predictions with thresholds.

**Exchange 3 (Prof. Pax):** Identified fundamental feasibility barrier - ResNet (local conv) and ViT (global attention) operations are mathematically incommensurable. Existing methods sacrifice either architectural semantics (SNE chunking) or cross-family capability (SANE tokenization).

**Exchange 4 (Dr. Sage):** Positioned significance - field has ZERO unified theory for cross-architecture weight-space comparison. SNE's ρ=0.54 is the only empirical datapoint. Success would enable HuggingFace-scale analysis (100K+ heterogeneous models) and invert architecture search to embedding-based exploration.

**Exchange 5 (Dr. Ally):** Synthesized modular encoder solution - operation-specific branches (conv/attention/MLP) + architecture graph encoding. Proposed three falsifiable predictions (P1: ρ ≥ 0.65, P2: distance-transfer correlation ρ ≥ 0.7, P3: triangle inequality violations < 15%).

**Exchange 6 (Prof. Rex):** Stress-tested modular proposal - identified alignment problem (concatenation assumes aligned representations), GNN hallucination risk (out-of-distribution graphs), and benchmark trap (SNE's 0.54 might be optimal). Demanded signal-existence pre-validation.

**Exchange 7 (Dr. Nova):** Breakthrough - contrastive projection solution to alignment problem. Cross-operation contrastive learning pulls same-task models together (ImageNet classifiers), forcing projection to learn task-aligned space. Architecture GNN becomes residual (not critical path).

**Exchange 8 (Prof. Vera):** Formalized experimental protocol - 4-level IV design (SNE baseline, Modular-only, Contrastive-aligned, Full-CAPE) isolates each component contribution. Concrete dataset (HuggingFace 400 models), metrics (Spearman ρ), thresholds validated.

**Exchange 9 (Dr. Ally):** Final synthesis consolidated all objections into complete hypothesis package with Under-If-Then-Because statement, mechanism specification, predictions, experimental setup, and feasibility validation.

### Breakthrough Moments
- **Exchange 7**: Contrastive alignment solution resolves Prof. Rex's cross-operation embedding alignment problem
- **Exchange 8**: 4-level ablation design makes every component falsifiable (addresses Prof. Vera's rigor requirement)
- **Exchange 9**: Complete hypothesis synthesis unifies UNF equivariance + SNE cross-arch capability + SANE scalability

---

## Final Hypothesis

### Title
Cross-Architecture Parameterized Encoder (CAPE)

### Core Claim
Under HuggingFace model zoos (ResNet, ViT, MobileNet, EfficientNet trained on ImageNet), if we apply modular operation encoders (conv/attention/MLP-specific) with contrastive task alignment (InfoNCE projection to shared d_z=256 space) and architecture-residual graph embeddings (GNN on computation graph added as residual), then cross-architecture property prediction correlation will reach ρ ≥ 0.65 (35% gap closure toward within-architecture ρ=0.81), because architectural structure decomposes into operation-specific signals (conv vs attention weight statistics) and graph topology, which are alignable via shared task objectives (ImageNet classification pulls same-task models together in embedding space).

### Mechanism
Three-component encoder:

1. **Operation-Specific Encoders**: Process conv weights (SANE tokenization: reshape to R^(c_out × c_r), chunk to d_t=256, window-based encoding), attention weights (UNF permutation-equivariant encoding via Algorithm 1 valid partition enumeration), and MLP weights (standard equivariant encoding) separately, respecting mathematical structure differences. Each encoder produces operation embedding z_op ∈ R^h.

2. **Contrastive Task Alignment**: Project all operation embeddings into shared d_z=256 dimensional space via learned linear maps. Use InfoNCE loss (temperature τ=0.07) to pull same-task models together (ImageNet classifiers) and push different-task models apart, forcing the projection to learn a task-aligned space where operation type becomes a meaningful perturbation.

3. **Architecture Graph Residual**: Encode computation graph (nodes=operations, edges=data flow) via GCN (3 layers) into architecture embedding z_arch ∈ R^64. Add as residual to contrastive-aligned embeddings: z_final = z_contrastive + α·z_arch (α learnable). If GNN fails to generalize to unseen graph structures, residual degrades to zero, preserving contrastive-only model.

---

## Predictions

### P1 (Primary): Cross-Architecture Performance Improvement
**Statement**: Full CAPE model (modular + contrastive + GNN residual) achieves Spearman ρ ≥ 0.65 on ResNet→ViT cross-architecture property prediction, compared to SNE baseline ρ=0.54

**Test Method**: Train CAPE on 70% of ResNet-50+ViT-Base+MobileNetV2+EfficientNet-B0 models (280 models total, mixed-architecture training). Test on held-out 30% ViT-Base models (30 models). Measure Spearman correlation between predicted and actual ImageNet top-1 accuracy.

**Success Criterion**: ρ_CAPE ≥ 0.65 AND ρ_CAPE - ρ_SNE ≥ 0.10 (statistically significant improvement, p < 0.05 via permutation test)

**Falsification**: If ρ_CAPE < 0.60 OR ρ_CAPE - ρ_SNE < 0.05, modular architecture-parameterized encoding provides no meaningful improvement.

### P2: Architectural Distance Validity
**Statement**: Embedding L2 distance in CAPE space predicts cross-architecture transfer difficulty (architectures with larger embedding distance show greater transfer performance degradation)

**Test Method**: Compute embedding centroids for each architecture family on training set. Measure pairwise L2 distances. Measure transfer performance degradation for 6 architecture pairs. Correlate embedding distance with transfer degradation.

**Success Criterion**: Spearman ρ ≥ 0.7 between embedding distance and transfer degradation

**Falsification**: If ρ < 0.5, embedding distance does not reflect architectural similarity.

### P3: Metric Space Properties
**Statement**: CAPE embedding space satisfies approximate metric properties (triangle inequality violations < 15%)

**Test Method**: For all architecture triplets (A, B, C), compute d(A,B), d(B,C), d(A,C). Count violations: d(A,C) > d(A,B) + d(B,C) + 0.15·max(d).

**Success Criterion**: Violation rate ≤ 15% (≤ 1 violation out of 4 triplets)

**Falsification**: If violation rate > 30%, embedding space lacks metric structure.

---

## Novelty

### Key Innovation
First architecture-parameterized weight-space learning framework - paradigm shift from architecture-invariance (treating differences as noise) to architecture-conditioning (treating differences as learnable signals).

### Differentiation from Prior Work

**vs UNF (Zhou et al. 2024, 25 cites):**
- UNF provides permutation-equivariance construction (Algorithm 1) but no empirical cross-architecture validation
- CAPE applies UNF's equivariance to attention encoders while adding conv/MLP branches + contrastive alignment for practical cross-family transfer (ResNet→ViT)

**vs SNE (Andreis et al. 2023, 7 cites):**
- SNE uses set-encoding that loses architectural specificity via chunking (flattens conv and attention into same tokens)
- CAPE uses modular encoders that preserve operation-specific structure while achieving cross-architecture capability via contrastive alignment

**vs SANE (Schürholt et al. 2024, 44 cites):**
- SANE demonstrates same-family transfer (ResNet-18→50) but requires shared token size d_t for cross-architecture
- CAPE removes this constraint via operation-specific encoders + contrastive projection, enabling true cross-family transfer

---

## Experimental Design

### Dataset
**HuggingFace Model Hub - ImageNet Vision Models**
- 4 architecture families: ResNet-50 (100 models), ViT-Base (100 models), MobileNetV2 (100 models), EfficientNet-B0 (100 models)
- Total: 400 models
- Ground truth: ImageNet top-1 accuracy from published model cards
- Train/Test: 70/30 stratified by accuracy quantiles per architecture

### Baselines
1. **SNE Set-Encoding**: ρ=0.54 on ResNet→ViT (published result, Andreis et al. 2023)
2. **SANE Tokenization**: ResNet-18→50 +2.2% over scratch (same-family only)
3. **Operation-Agnostic Statistics**: Expected ρ < 0.40 (weak baseline)

### Ablation Design (4 Levels)
1. **Level 1 (SNE Baseline)**: Set-encoding with chunking (c=256)
2. **Level 2 (Modular-Only)**: Operation-specific encoders without contrastive alignment
3. **Level 3 (Contrastive-Aligned)**: Modular encoders + InfoNCE projection (τ=0.07, d_z=256)
4. **Level 4 (Full-CAPE)**: Modular + contrastive + GCN residual (z_arch ∈ R^64)

**Purpose**: Isolate contribution of (a) operation modularity, (b) contrastive alignment, (c) architecture graph residual

---

## Limitations

### Known Limitations
- Cross-architecture validation limited to vision domain (no NLP/speech empirics)
- GNN generalization to unseen graph topologies uncertain (mitigated by residual positioning)
- Operation vocabulary is hand-coded (conv/attention/MLP) - not learned from data
- Scalability validated to ResNet-101 (44M params) - billion-parameter models untested

### Remaining Concerns (Prof. Rex)
1. **Signal Strength**: SNE's 54% might be optimal - requires signal-existence pre-validation (binary classifier ≥80% accuracy distinguishing ResNet vs ViT from operation-agnostic statistics)
2. **GNN Generalization**: ResNet sequential graphs vs ViT dense graphs may not generalize - mitigated by residual (failure → contrastive-only model)
3. **Contrastive Collapse**: All ImageNet classifiers may cluster regardless of architecture - requires intra-architecture variance monitoring + diversity loss if variance drops

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 9 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 concerns with concrete mitigations specified |

**Phase 2B Readiness**: ✅ READY
- **SH1-EXISTENCE**: Operation-specific signals must exist (testable via binary classifier ≥80%)
- **SH2-MECHANISM**: Contrastive alignment must create metric space (testable via P2, P3)
- **SH3-COMPARISON**: CAPE must outperform SNE baseline (deferred to Phase 5)

---

*Hypothesis ID: H-CAPE-v1*  
*Confidence: 0.75*  
*Next Phase: Phase 2B (Research Planning)*

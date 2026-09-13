# Verification Plan: Compositional Architecture-Agnostic Weight Encoder (CAWE)

**Date:** 2026-03-19
**Hypothesis ID:** H-CAWE-v1
**Confidence:** 0.85
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under training on a 750-model heterogeneous zoo (250 CNNs from torchvision, 250 Vision Transformers from ViT Model Zoo, 250 FC-MLPs from Unterthiner MNIST), if a Compositional Architecture-Agnostic Weight Encoder (CAWE) combining architecture-specific tokenizers with a shared Neural Functional Transformer (NFT) backbone is trained to predict generalization gap, then the encoder achieves Spearman ρ > 0.7 on cross-architecture generalization gap prediction while preserving architecture-family structure (silhouette > 0.5) and outperforming flat-weight baselines (Δρ > 0.15), because the NFT's permutation-equivariant attention mechanism learns cross-layer weight relationships from shared token representations that are architecture-independent after tokenization.

### 1.2 Alternative Hypothesis (H0)

A compositional architecture-agnostic weight encoder (CAWE) does NOT achieve superior cross-architecture generalization gap prediction (Spearman ρ ≤ 0.7 on heterogeneous test set) compared to baselines, OR the improvement over flat-weight baseline is Δρ ≤ 0.15, OR CAWE fails to beat random forest baseline on out-of-distribution tests by Δρ > 0.1.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Heterogeneous Model Zoo (750 models) - standard | Provides 3-family heterogeneous validation (CNN, Transformer, MLP) at manageable scale. All datasets publicly available. ViT Zoo designed for model population research. |
| **Model** | Compositional Architecture-Agnostic Weight Encoder (CAWE) | NFT proven on MNIST MLPs. Architecture-specific tokenizers project to shared token space. Hybrid approach: arch-specific preprocessing + arch-agnostic processing. |

**Dataset Details:**
- Source: ViT Model Zoo (250), torchvision.models (250), Unterthiner MNIST MLPs (250)
- Path: github.com/ModelZoos/ViTModelZoo + torchvision.models + Zenodo 5645138

**Model Details:**
- Type: Neural Functional Transformer with Architecture-Specific Tokenizers
- Source: nfn library (PyPI: pip install nfn) for NFT backbone + custom tokenizers

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| NFT on MNIST MLPs | +17% INR classification improvement | MNIST FC-MLP zoo (homogeneous, single architecture family) |
| DWSNets permutation equivariance | Runtime failure on FC-MLP weights | Designed for CNN weights, failed on non-CNN architectures |
| SANE sequential tokenization | Demonstrated scalability on large models | Model zoo with diverse architectures (proof of tokenization viability) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Shared token space preserves arch-specific quality signals | NFT paper shows attention can discover structure. Theoretical basis from Universal NFNs. | Per-family ρ < 0.7, silhouette < 0.5 |
| A2 | Generalization gap meaningful across architectures | Standard ML evaluation metric used across all model families. | Low ρ even for arch-specific baselines |
| A3 | 750-model zoo is representative | ViT Zoo designed for model population research. Includes diverse CNN/Transformer/MLP architectures. | OOD generalization fails (ρ < 0.55) |
| A4 | NFT attention sufficient without explicit inductive biases | NFT paper demonstrates this for MLPs. Attention discovers relationships from data. | Cannot beat RF baseline by Δρ > 0.1 |
| A5 | Tokenization strategy not critically sensitive | Multiple successful weight embedding approaches exist (SANE, NFT, GNN). | < 2/4 variants achieve ρ > 0.65 |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical validation of architecture-agnostic weight encoders on a truly heterogeneous multi-family model zoo (prior NFT work: homogeneous MNIST MLPs; Universal NFNs: theoretical claims without large-scale heterogeneous validation). Compositional hybrid approach (arch-specific tokenization + arch-agnostic processing) avoids DWSNets library lock-in and Universal NFN impracticality.

**Key Innovation:** Compositional architecture-agnostic processing - architecture-specific tokenizers project diverse weight types (CNN kernels, Transformer Q/K/V, MLP matrices) into shared D-dimensional token space, then unified NFT backbone processes tokens with permutation-equivariant attention, learning cross-layer relationships architecture-independently.

**Differentiation:**
- vs DWSNets: Avoids library lock-in (ROUTE_TO_0 lesson) through flexible tokenization
- vs NFT paper: Extends from single-architecture to heterogeneous zoo
- vs Universal NFNs: Empirical validation at 750-model scale vs theoretical claims
- vs GNN approach: Attention-based implicit learning vs explicit graph structure

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-Integrated | Mechanism | SHOULD_WORK | H-E1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Cross-Architecture Generalization Existence

**Type:** EXISTENCE

**Statement:** Under training on a heterogeneous 750-model zoo (CNNs, Transformers, MLPs), if a Compositional Architecture-Agnostic Weight Encoder (CAWE) is trained to predict generalization gap, then it achieves Spearman ρ > 0.7 (95% CI lower bound) on a 150-model held-out test set because the shared NFT backbone learns architecture-independent weight relationships from tokenized representations.

**Rationale:** This hypothesis validates the core claim that architecture-agnostic weight encoding is possible at scale on heterogeneous model zoos. Proves CAWE can generalize across fundamentally different architectures (convolutional, attention-based, fully-connected) without architecture-specific processing. MUST_WORK gate — failure invalidates entire approach.

**Variables:**
- Independent: Architecture Family (CNN/Transformer/MLP), Model Size
- Dependent: Generalization Gap Prediction Accuracy (Spearman ρ)
- Controlled: Dataset Split (80/20 stratified, seed=42), NFT Hyperparameters, Training Procedure (AdamW, lr=1e-4, batch=32, 100 epochs)

**Verification Protocol:**
1. Extract 750 models from ViT Zoo (250), torchvision CNNs (250), Unterthiner MLPs (250) with generalization gap metadata
2. Apply architecture-specific tokenizers (CNN/Transformer/MLP) to project weights to D-dimensional token sequences
3. Train NFT backbone on 600 models (200 per family) to predict generalization gap via regression head
4. Evaluate on 150 held-out models (50 per family), compute Spearman ρ with bootstrap 95% CI (n=1000 resamples)
5. Verify ρ > 0.7 (95% CI lower bound exceeds threshold)

**Success Criteria:**
- Primary: Spearman ρ > 0.7 (95% CI lower bound)
- Secondary: Per-architecture consistency (ρ > 0.65 for each family subset)

**Gate:**
- Type: MUST_WORK
- If Fail: ABANDON → ROUTE_TO_PHASE_0

**Prerequisites:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P1

---

#### H-M-Integrated: Compositional Mechanism Validation

**Type:** MECHANISM

**Statement:** Under CAWE training on heterogeneous model zoo, if the compositional mechanism (architecture-specific tokenization → shared token space → NFT permutation-equivariant attention → generalization gap prediction) is applied, then (1) per-family ablation achieves ρ > 0.7 for CNN/Transformer/MLP subsets, (2) architecture clustering silhouette > 0.5 in embeddings, (3) baseline outperformance Δρ > 0.15 vs flat-weight MLP and Δρ > 0.1 vs random forest on OOD tests, because the compositional design preserves architecture-specific signals while enabling cross-architecture learning.

**Rationale:** Validates the three-step causal chain and compositional design principles. Demonstrates that shared token space does NOT destroy architecture-specific information (per-family ablation) and that learned representations outperform both naive approaches (flat-weight) and hand-crafted features (random forest).

**Variables:**
- Independent: Tokenization Strategy (statistics/spectral/learned/SANE), Token Dimension D (64/128/256)
- Dependent: Architecture Clustering Quality (silhouette score), Baseline Performance Delta (Δρ)
- Controlled: Same as H-E1 (dataset split, NFT hyperparameters, training procedure)

**Verification Protocol:**
1. Per-family ablation: Train CAWE on single-family subsets (200 CNN-only, 200 Transformer-only, 200 MLP-only), evaluate on corresponding 50-model held-outs, measure ρ for each
2. Clustering validation: Extract CAWE embeddings for all 750 models, compute t-SNE projection, measure silhouette score with architecture-family labels (3 clusters)
3. Baseline comparison (flat-weight): Train MLP on concatenated weights (no tokenization), compare via paired t-test on 150-model test set
4. Baseline comparison (random forest): Train RF on engineered features (layer L2 norms, sparsity, spectral radius), evaluate on OOD sets (Unterthiner/NeurIPS 2021 MLPs), compare via Wilcoxon signed-rank
5. Robustness ablations: Test 4 tokenization variants (2/4 must achieve ρ > 0.65), test 3 D-values (2/3 must achieve ρ > 0.65)

**Success Criteria:**
- Primary: All 3 per-family ρ > 0.7, silhouette > 0.5, Δρ > 0.15 flat (p<0.001), Δρ > 0.1 RF on OOD (p<0.01)
- Secondary: Tokenization robustness (2/4 variants), hyperparameter robustness (2/3 D-values), attention head specialization visible

**Gate:**
- Type: SHOULD_WORK
- If Fail (all components): Fundamental design issue → PIVOT to architecture-specific embeddings OR EXPLORE GNN-based explicit graph structure
- If Fail (partial): Document working components, prioritize refinement

**Prerequisites:** H-E1 (must pass first)

**Source:** Phase 2A Section 1.3 (Causal Mechanism 3 steps), Predictions P2-P8

**Components:**
1. Per-family ablation (All 3 families ρ > 0.7)
2. Architecture clustering (Silhouette > 0.5)
3. Flat-weight baseline (Δρ > 0.15, paired t-test p<0.001)
4. Random forest baseline on OOD (Δρ > 0.1, Wilcoxon p<0.01)
5. Robustness validation (2/4 tokenization, 2/3 D-values, adversarial ρ > 0.65, OOD ρ > 0.6/0.55)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M-Integrated
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Spearman ρ > 0.7 (95% CI lower bound) | ROUTE_TO_PHASE_0 (entire approach invalidated) |
| H-M-Integrated | SHOULD_WORK | All 5 components pass thresholds | PIVOT (shared space → arch-specific embeddings) OR EXPLORE (tokenization → learned projection) OR ABANDON (learned reps no better than RF) |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanism Validation | H-M-Integrated | 3 weeks |

**Total Duration:** 5 weeks

**Critical Path:** H-E1 (Week 1-2) → Gate 1 → H-M-Integrated (Week 3-5) → Gate 2

**Bottlenecks:**
- H-E1 data collection and training (Week 1-2)
- Per-family ablation training (Week 3, requires 3 separate runs)
- OOD dataset evaluation (Week 5, requires external data download)

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Severity | Affected Hypotheses | Mitigation |
|------|--------|----------|---------------------|------------|
| R1 | A1 | High | H-E1, H-M-Integrated | Per-family ablation validation, attention pattern analysis, arch-specific fallback |
| R2 | A2 | Medium | H-E1 | Architecture-specific baselines, within-family ranking fallback |
| R3 | A3 | High | H-M-Integrated | Cross-dataset OOD tests, adversarial set, graceful degradation monitoring |
| R4 | A4 | Medium | H-M-Integrated | RF baseline comparison, graph structure hints fallback |
| R5 | A5 | Medium | H-M-Integrated | 4-variant testing (2/4 success), focus on best variant if needed |

### 4.2 Risk Summary

**Critical Risks:** 0
**High Risks:** 2 (R1: shared space signal loss, R3: dataset memorization)
**Medium Risks:** 3 (R2: metric invalidity, R4: attention insufficiency, R5: tokenization fragility)
**Low Risks:** 0

**Most Critical Path:** R1 (signal loss) → H-E1 MUST_WORK gate failure

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Compositional Architecture-Agnostic Weight Encoders achieve cross-architecture generalization through shared token space processing with NFT attention.

**Strengths:**
- Leverages proven tools (nfn library, SANE tokenization, public datasets)
- Avoids prior failures (DWSNets library lock-in lesson)
- Clear validation path (per-family ablation, baseline comparisons, OOD tests)
- Rigorous statistical methodology (bootstrap CIs, parametric/non-parametric tests)

**Expected Outcomes:**
- Primary: Spearman ρ > 0.7 on 150-model heterogeneous test set
- Secondary: Per-family ρ > 0.7 validates signal preservation
- Tertiary: Architecture clustering silhouette > 0.5 confirms family distinctions

### 5.2 Antithesis

**Null Hypothesis (H0):** CAWE does NOT achieve ρ > 0.7 OR Δρ ≤ 0.15 vs flat-weight OR Δρ ≤ 0.1 vs RF on OOD.

**Counter-Arguments:**
- Baseline limitations suggest fundamental challenges (NFT: homogeneous only, DWSNets: failed on FC-MLP)
- Assumption violations threaten viability (A1: signal loss, A3: dataset memorization, A4: attention insufficiency)
- Scope limitations restrict generalizability (requires arch metadata, white-box access, vision only)

**Potential Failure Points:**
- R1 (High): Shared space destroys discriminative features
- R3 (High): Dataset memorization, not true weight-space learning
- R4 (Medium): Attention insufficient compared to explicit graph structure

### 5.3 Synthesis

**Balanced Assessment:** The hypothesis presents a testable claim backed by established theory and proven components, but faces valid concerns regarding signal loss, dataset memorization, and attention mechanism sufficiency.

**Resolution Path:** Two-phase sequential validation with MUST_WORK gate (H-E1) before mechanism investigation (H-M-Integrated). Multi-component validation allows partial success documentation.

**Nuanced Outcome Possibilities:**
1. Full Support: All hypotheses pass → Publish-ready validation
2. Partial Support: H-E1 passes, some H-M components fail → Refined thesis with limitations
3. Weak Support: H-E1 barely passes, OOD collapses → Restrict claims to in-distribution
4. Antithesis Support: H-E1 fails MUST_WORK → ROUTE_TO_PHASE_0

**Critical Uncertainties:**
- Whether attention head specialization emerges spontaneously
- Whether 750-model PoC scale is sufficient for generalization claims
- Which tokenization strategy performs best in practice
- Whether CAWE extends to other model properties beyond generalization gap

---

## 6. Executive Summary

**Main Hypothesis:** H-CAWE-v1 (Confidence: 0.85) - Compositional Architecture-Agnostic Weight Encoder achieves ρ > 0.7 cross-architecture generalization gap prediction on heterogeneous 750-model zoo

**Verification Structure:**
- Mode: Incremental (Phase 2A-seeded)
- Sub-Hypotheses: 2 total (H-E1: Existence, H-M-Integrated: Mechanism)
- Phases: 2 phases over 5 weeks (2 + 3 weeks)
- Critical Gates: 2 decision points (Gate 1: Week 2 MUST_WORK, Gate 2: Week 5 SHOULD_WORK)

**Scope Reduction:** 38% (6 BUILD_ON claims reused, only 3 PROVE_NEW claims verified)

**Risk Assessment:** Medium-High
- Primary concerns: R1 (shared space signal loss - High), R3 (dataset memorization - High)
- Mitigation: Per-family ablation, OOD validation, baseline comparisons, robustness ablations

**Immediate Action:** Begin Phase 1 with H-E1 (data collection, tokenizer implementation, 600-model training, 150-model evaluation)

**Next Phase:** Phase 2C will generate detailed experiment specifications for H-E1 (READY status)

---

*Generated by YouRA Phase 2B (v3.5) | 2026-03-19*

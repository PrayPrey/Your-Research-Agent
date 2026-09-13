# Verification Plan: Cross-Architecture Parameterized Encoder (CAPE)

**Date:** 2026-07-13
**Hypothesis ID:** H-CAPE-v1
**Confidence:** 0.75
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M-Integrated)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under HuggingFace model zoos (ResNet, ViT, MobileNet, EfficientNet trained on ImageNet), if we apply modular operation encoders (conv/attention/MLP-specific) with contrastive task alignment (InfoNCE, project to shared d_z=256 space) and architecture-residual graph embeddings (GNN on computation graph added as residual), then cross-architecture property prediction correlation will reach ρ ≥ 0.65 (35% gap closure toward within-architecture ρ=0.81), because architectural structure decomposes into operation-specific signals (conv vs attention weight statistics) and graph topology, which are alignable via shared task objectives (ImageNet classification pulls same-task models together in embedding space).

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in cross-architecture property prediction correlation between the modular architecture-parameterized encoder (H-CAPE) and the SNE set-encoding baseline (H0: ρ_CAPE - ρ_SNE ≤ 0.05, i.e., improvement is negligible).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HuggingFace Model Hub - ImageNet Vision Models (standard) | Provides required architectural diversity (CNN vs Transformer vs efficient) and model count (100 per family) for robust cross-architecture learning. ImageNet top-1 accuracy from model cards serves as continuous ground truth property. |
| **Model** | CAPE - Cross-Architecture Parameterized Encoder | Decomposes architectural differences into learnable components (operation-specific + graph topology), addresses Prof. Pax's incommensurability via modular design, Prof. Vera's falsifiability via ablation, Prof. Rex's alignment via contrastive projection. |

**Dataset Details:**
- Source: HuggingFace (huggingface.co/models), filtered for ImageNet-1K trained models
- Path: 4 architecture families: ResNet-50 (100 models), ViT-Base (100 models), MobileNetV2 (100 models), EfficientNet-B0 (100 models). Total: 400 models.

**Model Details:**
- Type: Modular weight-space encoder with 3 components: (1) Operation-specific encoders (conv: SANE tokenization, attention: UNF equivariance, MLP: standard), (2) Contrastive projection (InfoNCE, d_z=256), (3) Architecture GNN residual (z_arch ∈ R^64)
- Source: Custom implementation combining UNF Algorithm 1, SANE window-based tokenization, SNE Set Transformers, standard contrastive learning

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| SNE Set-Encoding | ResNet→ViT: ρ=0.54, ResNet→MobileNet: ρ=0.61 | HuggingFace model zoos, ImageNet accuracy |
| SANE Tokenization | ResNet-18→50: +2.2% over scratch (same-family) | Custom ResNet zoos, CIFAR-10/100 |
| UNF Permutation-Equivariance | 10-15% improvement over non-equivariant | Small RNN/Transformer, learned optimizer |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Operation-specific weight signals exist and are distinguishable | SANE same-family transfer (+2.2%) proves architecture-specific signals | If classifier < 70%, modular encoding reduces to SNE (no improvement) |
| A2 | Contrastive task alignment creates metric space | InfoNCE with same-task attraction, SNE mixed-architecture training insight | If embedding distance doesn't correlate with transfer (ρ < 0.5), architectural structure not preserved |
| A3 | Architecture graph topology contains learnable information | ResNet sequential+skip vs ViT dense attention topologies, GNN as residual | If GNN residual α → 0, simplify to contrastive-only model |
| A4 | HuggingFace provides sufficient architectural diversity | 400 models (100 per family) across 4 architectures | If high variance (confidence > ±0.1), expand to Timm library (1000+ models) |
| A5 | ImageNet top-1 accuracy from model cards is accurate | HuggingFace model cards community-validated, SNE uses same source | If measurement error > 2%, switch to re-evaluated accuracies |

### 1.6 Research Gap & Novelty

**Key Innovation:** First architecture-parameterized weight-space learning framework - treats architectural differences as learnable signals, not noise to be invariant to. Paradigm shift from architecture-invariance to architecture-conditioning.

**Differentiation from Prior Work:**
- **vs. UNF:** UNF provides permutation-equivariance construction but no empirical cross-architecture validation. CAPE applies UNF's equivariance to attention encoders while adding conv/MLP branches + contrastive alignment for practical cross-family transfer.
- **vs. SNE:** SNE uses set-encoding that loses architectural specificity via chunking. CAPE uses modular encoders that preserve operation-specific structure (conv tokenization, attention equivariance) while achieving cross-architecture capability via contrastive alignment.
- **vs. SANE:** SANE demonstrates same-family transfer but requires shared token size d_t for cross-architecture. CAPE removes this constraint via operation-specific encoders + contrastive projection to shared space, enabling true cross-family transfer (ResNet→ViT).

**Research Gap Addressed:** Zero unified theory for cross-architecture weight-space comparison exists. 33% cross-architecture performance degradation (SNE ρ=0.81→0.54) quantifies the gap. CAPE targets 35% gap closure to ρ ≥ 0.65.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | TODO |
| H-M-Integrated | Mechanism | MUST_WORK | H-E1 | TODO |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Operation-Specific Weight Signal Existence

**Type:** EXISTENCE  
**Statement:** Under ImageNet-trained model zoos (ResNet-50 vs ViT-Base), if operation-specific weight signals exist beyond tensor dimensions, then a binary classifier trained on operation-agnostic statistics (layer norms, spectral norms) will achieve ≥80% accuracy distinguishing ResNet from ViT, because architectural operations (conv vs attention) impose distinct statistical patterns on learned weights.

**Rationale:**  
This hypothesis validates Assumption A1, which is foundational for CAPE's modular encoder design. If operation-specific signals don't exist, modular encoders reduce to SNE's set-encoding baseline (no improvement). Prof. Rex identified this as critical pre-validation requirement.

**Variables:**
- **IV:** Architecture Type (Binary: ResNet vs ViT)
- **DV:** Binary Classifier Accuracy (on operation-agnostic statistics)
- **CV:** Model zoo size (50 per architecture), ImageNet-trained, same statistical features

**Verification Protocol:**
1. Extract operation-agnostic statistics (layer-wise L2 norms, top-5 spectral norms, mean/std) from 100 models (50 ResNet-50, 50 ViT-Base).
2. Train logistic regression classifier on 70 models (35 per architecture, stratified by accuracy quantiles).
3. Test on held-out 30 models, measure test accuracy.
4. Ablation: compare norms-only vs norms+spectral to identify signal source.
5. If accuracy ≥80%, signal exists; if <70%, signal insufficient for modular encoding.

**Success Criteria:**
- **Primary:** Binary classifier test accuracy ≥80% (signal exists)
- **Secondary:** Norms+spectral accuracy > norms-only by ≥5% (spectral norms encode architectural information)
- **Statistical:** p < 0.05 vs random baseline (50% via permutation test)

**Gate:**
- **Type:** MUST_WORK
- **If Fail (<70% accuracy):** ABANDON modular encoder approach, fall back to SNE set-encoding baseline (no architecture-specific branches)
- **If Partial (70-80%):** EXPLORE enhanced statistics (Fisher eigenspectrum, NTK trace per original h-e1 design)

**Prerequisites:** None (foundational test)

**Established Facts Integration:**  
Builds on SANE same-family transfer (+2.2%), which proves architecture-specific signals exist within families. H-E1 extends this to cross-family (ResNet vs ViT) via binary discrimination test.

**Source:** Phase 2A Section 1.4 (Assumption A1), Section 5 (SH1: signal-existence test)

---

#### H-M-Integrated: Full CAPE Mechanism Validation

**Type:** MECHANISM  
**Statement:** Under HuggingFace model zoos (400 models across ResNet/ViT/MobileNet/EfficientNet), if we implement the 3-component CAPE encoder (operation-specific encoders → contrastive projection → GNN residual), then cross-architecture property prediction correlation will reach ρ ≥0.65 on ResNet→ViT transfer (vs SNE baseline ρ=0.54), because modular encoders preserve operation-specific structure, contrastive alignment creates metric space via shared task objectives, and GNN residual adds graph topology signal (or degrades gracefully to zero).

**Rationale:**  
This hypothesis tests the complete CAPE mechanism via 4-level ablation (SNE baseline, Modular-Only, Contrastive-Aligned, Full-CAPE), isolating each component's contribution. Validates all 3 causal steps from Phase 2A (operation encoding, contrastive alignment, GNN residual) in single integrated experiment. Prof. Vera's falsifiability requirement met via explicit thresholds and ablation design.

**Variables:**
- **IV:** Encoder Configuration (4 levels: SNE-Baseline, Modular-Only, Contrastive-Aligned, Full-CAPE)
- **DV (Primary):** Cross-Architecture Correlation (Spearman ρ on ResNet→ViT ImageNet accuracy prediction)
- **DV (Secondary):** Operation Embedding Similarity (cosine similarity conv vs attention, should be <0.95)
- **DV (Tertiary):** Intra-Architecture Variance (within-family variance, should be ≥0.1 to avoid contrastive collapse)
- **DV (Quaternary):** GNN Residual Weight α (learned parameter, monitors GNN contribution)
- **CV:** 400-model dataset (100 per architecture), 70/30 train/test split, contrastive hyperparameters (τ=0.07, d_z=256), GNN architecture (3-layer GCN, z_arch∈R^64)

**Verification Protocol:**
1. Implement 4 encoder variants: (a) SNE-Baseline (hierarchical set encoding), (b) Modular-Only (op-specific encoders without contrastive), (c) Contrastive-Aligned (modular + InfoNCE projection), (d) Full-CAPE (modular + contrastive + GNN residual).
2. Train each configuration on 280 mixed-architecture models (70%), test on held-out 120 models (30 per architecture).
3. Measure primary metric: Spearman ρ on ResNet→ViT transfer (train on ResNet/MobileNet/EfficientNet, test on ViT).
4. Collect diagnostic metrics: operation embedding similarity, intra-architecture variance, GNN α value.
5. Statistical validation: permutation test (1000 bootstrap resamples, α=0.05) comparing Full-CAPE vs SNE baseline.
6. Ablation analysis: quantify each component's contribution (Modular gain, Contrastive gain, GNN gain).

**Success Criteria:**
- **Primary:** Full-CAPE achieves ρ ≥0.65 on ResNet→ViT (35% gap closure toward within-architecture ρ=0.81)
- **Statistical:** ρ_CAPE - ρ_SNE ≥0.10 with p < 0.05 (statistically significant improvement via permutation test)
- **Diagnostic 1:** Operation embedding similarity <0.95 (operation specificity preserved)
- **Diagnostic 2:** Intra-architecture variance ≥0.1 (contrastive alignment avoids collapse)
- **Diagnostic 3:** GNN residual α >0.1 OR performance with GNN ≥ performance without GNN (GNN contributes or degrades gracefully)

**Component Falsifiers (from Phase 2A Causal Steps):**
1. **Operation Encoders (Causal Step 1):** If cosine similarity between conv and attention embeddings >0.95 for same-task models, operation-specific structure not captured → modular encoding fails.
2. **Contrastive Alignment (Causal Step 2):** If intra-architecture variance <0.1 (collapse) OR embedding distance doesn't correlate with transfer difficulty (ρ<0.5), alignment fails to preserve architectural structure.
3. **GNN Residual (Causal Step 3):** If α→0 during training OR adding z_arch decreases performance vs contrastive-only, GNN fails to generalize to unseen graph topologies → degrade to Contrastive-Aligned variant.

**Gate:**
- **Type:** MUST_WORK
- **If Fail (ρ <0.60):** PIVOT to simpler encoder (test Contrastive-Aligned variant without GNN)
- **If Partial (0.60 ≤ ρ < 0.65):** EXPLORE hyperparameter tuning (τ, d_z, GNN layers) or larger model zoo (expand to Timm library 1000+ models)
- **If Component Fails:** Ablation identifies failing component → ISOLATE and redesign (e.g., if GNN α→0, use graph kernels instead of GNN)

**Prerequisites:** H-E1 PASS (signal existence validated)

**Established Facts Integration:**  
Builds on UNF's permutation-equivariance (Algorithm 1 for attention encoders), SNE's cross-architecture baseline (ρ=0.54), SANE's tokenization scalability (ResNet-101 44M params). Does NOT re-prove equivariance or set encoding (BUILD_ON status). Focuses validation on NEW claims: modular encoding improves over SNE, contrastive alignment creates metric space, architectural signal is learnable.

**Source:** Phase 2A Section 1.3 (Causal Mechanism with 3 steps), Section 1.6 (Prediction P1), Section 5 (SH2: mechanism validation)

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (Signal Existence) → H-M-Integrated (Full CAPE Mechanism)
```
<!-- Linear dependency: Signal must exist before testing full mechanism -->

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Binary classifier accuracy ≥80% | ABANDON modular encoders, use SNE baseline |
| H-M-Integrated | MUST_WORK | ρ ≥0.65 AND statistically significant vs SNE (p<0.05) | PIVOT to simpler variant or EXPLORE hyperparameters |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Signal Existence | H-E1 | 2-3 days (dataset collection, binary classifier training) |
| Phase 2: Full Mechanism | H-M-Integrated | 5-7 days (4-variant ablation, cross-architecture testing, statistical validation) |

**Total Duration:** 7-10 days (PoC verification scale with standard test sets, ~3000 samples per architecture)

---

## 4. Risk Analysis

### 4.1 Assumption-Risk Mapping

| Risk ID | Source | Risk Description | Severity | Affected Hypotheses | Likelihood |
|---------|--------|------------------|----------|---------------------|------------|
| R1 | A1 | Operation-specific signals insufficient (classifier <70%) | Critical | H-E1, H-M-Integrated | Medium |
| R2 | A2 | Contrastive collapse (all embeddings cluster to single point) | High | H-M-Integrated | Medium |
| R3 | A3 | GNN fails to generalize to unseen graph topologies | Medium | H-M-Integrated | Medium |
| R4 | A4 | Insufficient model diversity (high variance in ρ estimates) | Medium | H-M-Integrated | Low |
| R5 | A5 | Noisy ground truth (model card accuracies inaccurate) | Low | H-E1, H-M-Integrated | Low |

### 4.2 Mitigation Strategies

**Risk R1: Insufficient Operation-Specific Signals**

**Source:** A1 - Operation-specific weight signals exist and are distinguishable

**Description:** Binary classifier achieves <70% accuracy, indicating conv and attention weights are statistically indistinguishable from operation-agnostic features (layer norms, spectral norms). This invalidates the foundational assumption for modular encoders.

**Mitigation Strategy:**
1. **Prevention:** Pre-validate with exploratory data analysis on small sample (10 models per architecture) before full experiment
2. **Detection:** Monitor classifier accuracy during training; if stuck at 50-60% after 10 epochs, signal is weak
3. **Response:**
   - **If 70-80%:** EXPLORE enhanced statistics (Fisher eigenspectrum, NTK trace per original h-e1 design)
   - **If <70%:** ABANDON modular encoder approach, PIVOT to SNE set-encoding baseline (no architecture-specific branches)

**Early Warning Indicators:**
- Binary classifier accuracy plateaus at 50-60% (near random)
- Conv and attention weight distributions overlap significantly (Kolmogorov-Smirnov test p>0.05)

---

**Risk R2: Contrastive Collapse**

**Source:** A2 - Contrastive task alignment creates metric space

**Description:** Contrastive loss pulls all ImageNet classifiers to single point regardless of architecture, losing architectural structure in embedding space. Intra-architecture variance <0.1 indicates collapse.

**Mitigation Strategy:**
1. **Prevention:** Monitor intra-architecture variance during training; add architectural diversity loss if variance drops below 0.15
2. **Detection:** Compute embedding variance every 10 epochs; trigger alert if <0.1
3. **Response:**
   - **PIVOT:** Add architectural diversity loss term: L = L_contrastive + λ·L_diversity (pushes same-architecture embeddings apart)
   - **Hyperparameter tuning:** Increase temperature τ from 0.07 to 0.10 (reduce same-task attraction strength)

**Early Warning Indicators:**
- Intra-architecture variance drops below 0.15 during training
- All embeddings cluster within L2 distance <0.5 from centroid

---

**Risk R3: GNN Generalization Failure**

**Source:** A3 - Architecture graph topology contains learnable information

**Description:** GNN fails to generalize from ResNet sequential+skip graphs to ViT dense attention graphs. Residual weight α→0 during training OR adding z_arch decreases performance vs contrastive-only.

**Mitigation Strategy:**
1. **Prevention:** Position GNN as residual (graceful degradation design), not critical path
2. **Detection:** Monitor GNN residual weight α every 10 epochs; if α<0.05, GNN is being ignored
3. **Response:**
   - **PIVOT:** Degrade to Contrastive-Aligned variant (remove GNN residual)
   - **Alternative:** Use graph kernels (Weisfeiler-Lehman) instead of GNN for topology encoding

**Early Warning Indicators:**
- GNN residual weight α <0.05 after 50 epochs
- Adding z_arch decreases ρ by >0.02 vs contrastive-only baseline

---

**Risk R4: Insufficient Model Diversity**

**Source:** A4 - HuggingFace provides sufficient architectural diversity (400 models)

**Description:** 100 models per architecture insufficient for robust learning, leading to high variance in ρ estimates (confidence intervals >±0.1).

**Mitigation Strategy:**
1. **Prevention:** Use stratified sampling by accuracy quantiles to ensure diverse model coverage
2. **Detection:** Compute confidence intervals via bootstrap (1000 resamples); check if CI width >±0.1
3. **Response:**
   - **EXPAND:** Increase model zoo size to Timm library (1000+ models per architecture)
   - **FILTER:** Focus on high-quality models only (exclude fine-tuned variants, keep pretrained only)

**Early Warning Indicators:**
- Bootstrap confidence intervals for ρ exceed ±0.1
- High variance in per-architecture performance (std >0.15)

---

**Risk R5: Noisy Ground Truth**

**Source:** A5 - ImageNet top-1 accuracy from model cards is accurate

**Description:** HuggingFace model card accuracies contain measurement errors >2%, introducing noise in ground truth for property prediction task.

**Mitigation Strategy:**
1. **Prevention:** Validate model card accuracies on small sample (20 models) against re-evaluated ImageNet validation set
2. **Detection:** Compute mean absolute error between model card and re-evaluated accuracies
3. **Response:**
   - **If MAE >2%:** SWITCH to re-evaluated accuracies on standardized ImageNet validation set
   - **If MAE <2%:** Proceed with model card accuracies (sufficient quality)

**Early Warning Indicators:**
- Large discrepancies (>5%) between model card and re-evaluated accuracies in validation sample
- ρ correlation with noisy ground truth <0.5 (noise dominates signal)

---

### 4.3 Risk Summary Table

| ID | Risk | Severity | Likelihood | Mitigation | Contingency |
|----|------|----------|------------|------------|-------------|
| R1 | Insufficient operation signals | Critical | Medium | Enhanced statistics (Fisher, NTK) | ABANDON modular encoders |
| R2 | Contrastive collapse | High | Medium | Diversity loss, temperature tuning | Architecture diversity term |
| R3 | GNN generalization failure | Medium | Medium | Residual positioning (graceful degradation) | Remove GNN, use graph kernels |
| R4 | Insufficient model diversity | Medium | Low | Stratified sampling, expand to Timm | Increase to 1000+ models |
| R5 | Noisy ground truth | Low | Low | Validate sample, re-evaluate if needed | Re-evaluate on standard validation |

**Risk Distribution:**
- Critical: 1 (R1)
- High: 1 (R2)
- Medium: 2 (R3, R4)
- Low: 1 (R5)

**Highest Priority:** R1 (signal existence) - foundational assumption, gates entire approach

---

## 5. Dependency Graph & Execution Plan

### 5.1 Hypothesis Dependency DAG

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPENDENCY GRAPH                         │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────────┐
         │     H-E1         │
         │ Signal Existence │
         │  (MUST_WORK)     │
         └─────────┬────────┘
                   │
                   │ BLOCKS if FAIL
                   │ (accuracy <70%)
                   ▼
         ┌──────────────────┐
         │  H-M-Integrated  │
         │  Full CAPE Mech  │
         │  (MUST_WORK)     │
         └──────────────────┘

Legend:
  ┌─────┐
  │ H-* │  Hypothesis
  └─────┘
  
  │      Dependency (prerequisite)
  ▼
  
Gates:
  • MUST_WORK: Failure blocks dependent hypotheses
```

### 5.2 Execution Phases & Gates

**Phase 1: Foundation (H-E1)**
- **Objective:** Validate operation-specific signals exist
- **Gate Type:** MUST_WORK
- **Pass Condition:** Binary classifier accuracy ≥80%
- **Fail Action:** ABANDON modular approach → SNE baseline
- **Duration:** 2-3 days
- **Blocks:** H-M-Integrated (cannot proceed without signal existence)

**Phase 2: Full Mechanism (H-M-Integrated)**
- **Objective:** Validate 3-component CAPE encoder achieves ρ ≥0.65
- **Gate Type:** MUST_WORK
- **Pass Condition:** ρ ≥0.65 AND statistically significant (p<0.05)
- **Fail Action:** PIVOT to simpler variant (Contrastive-Aligned without GNN)
- **Duration:** 5-7 days
- **Prerequisites:** H-E1 PASS

### 5.3 Dependency Hierarchy

```
Level 0 (Foundation):
  • H-E1 (no dependencies)

Level 1 (Mechanism):
  • H-M-Integrated (depends on H-E1)

Critical Path:
  H-E1 → H-M-Integrated
  
Total Depth: 2 levels
Parallelization Potential: None (linear dependency)
```

### 5.4 Timeline Visualization (Gantt Chart)

```
Week 1                          Week 2
├───────┬───────┬───────┬───────┬───────┬───────┬───────┤
│ Mon   │ Tue   │ Wed   │ Thu   │ Fri   │ Mon   │ Tue   │
├───────┴───────┴───────┼───────┴───────┴───────┴───────┤
│  H-E1: Signal Test    │  H-M-Integrated: Full CAPE    │
│  ██████████████████   │  ███████████████████████████  │
│  • Dataset collection │  • 4-variant implementation   │
│  • Binary classifier  │  • Ablation study             │
│  • Validation (30%)   │  • Statistical testing        │
│                       │  • Component analysis         │
│  Gate: Day 3          │  Gate: Day 10                 │
│  (accuracy ≥80%)      │  (ρ ≥0.65, p<0.05)            │
└───────────────────────┴───────────────────────────────┘

Critical Path: 7-10 days
  • H-E1: 2-3 days (Days 1-3)
  • H-M-Integrated: 5-7 days (Days 4-10)

Milestones:
  ▸ Day 3: H-E1 Gate Decision (GO/NO-GO for H-M)
  ▸ Day 10: H-M-Integrated Complete (PoC Validation)
```

### 5.5 Resource Requirements

| Resource | H-E1 | H-M-Integrated | Notes |
|----------|------|----------------|-------|
| **GPU** | 1x V100 (8 hours) | 4x V100 (40 hours) | 4-variant parallel training |
| **Dataset** | 100 models (2GB) | 400 models (8GB) | HuggingFace model weights |
| **Compute Time** | ~16 GPU-hours | ~160 GPU-hours | Total: ~176 GPU-hours |
| **Storage** | 5GB | 20GB | Includes embeddings, checkpoints |
| **Human Effort** | 1 day (setup + analysis) | 3 days (implementation + validation) | Total: 4 person-days |

### 5.6 Execution Order & Checkpoints

**Step-by-Step Execution:**

1. **H-E1 Execution:**
   1. Download 100 models (50 ResNet-50, 50 ViT-Base) from HuggingFace
   2. Extract operation-agnostic statistics (norms, spectral norms)
   3. Train binary classifier (70/30 split, stratified)
   4. **Checkpoint 1:** Test accuracy measurement
   5. **Gate Decision:** If accuracy ≥80% → Proceed to H-M; else ABANDON

2. **H-M-Integrated Execution:**
   1. Expand dataset to 400 models (4 architectures × 100)
   2. Implement 4 encoder variants (SNE, Modular, Contrastive, Full-CAPE)
   3. Train all variants in parallel (70/30 split, mixed-architecture training)
   4. **Checkpoint 2:** Measure ρ for each variant on ResNet→ViT transfer
   5. **Checkpoint 3:** Collect diagnostic metrics (embedding similarity, variance, GNN α)
   6. **Checkpoint 4:** Statistical validation (permutation test)
   7. **Gate Decision:** If ρ ≥0.65 AND p<0.05 → SUCCESS; else PIVOT

---

## 6. Dialectical Analysis

### 6.1 Thesis: CAPE Hypothesis

**Central Claim:**  
Cross-architecture weight-space property inference can achieve ρ ≥0.65 (35% gap closure) through architecture-parameterized encoding that preserves operation-specific structure while creating unified metric space via contrastive task alignment.

**Supporting Arguments:**
1. **Theoretical Foundation:** UNF's Theorem 3.2 proves permutation-equivariant encoders span all possible equivariant maps, providing mathematical completeness for attention weight encoding
2. **Empirical Precedent:** SANE demonstrates same-family transfer (+2.2% over scratch), proving architecture-specific signals exist in weight statistics
3. **Cross-Architecture Feasibility:** SNE achieves ρ=0.54 baseline, establishing that some cross-architecture transfer is possible (not fundamentally impossible)
4. **Modular Design Addresses Incommensurability:** Prof. Pax's concern (conv vs attention mathematical differences) resolved via operation-specific branches rather than forcing unified encoding
5. **Contrastive Alignment Mechanism:** Shared task objectives (ImageNet classification) provide natural alignment signal that pulls same-task models together regardless of architecture

### 6.2 Antithesis: Null Hypothesis (H0) & Objections

**H0 Statement:**  
ρ_CAPE - ρ_SNE ≤ 0.05 (no meaningful improvement over set-encoding baseline)

**Supporting Arguments:**
1. **SNE Already Captures Available Signal:** 33% degradation (ρ=0.81→0.54) may represent fundamental limit of cross-architecture transfer, with remaining gap due to irreconcilable architectural differences
2. **Prof. Rex's Signal Strength Concern:** Operation-specific signals may be too weak to distinguish from noise when using operation-agnostic statistics (binary classifier might achieve only 60-70%)
3. **Contrastive Collapse Risk:** All ImageNet classifiers may cluster to single point regardless of modular encoding, losing architectural structure despite operation-specific branches
4. **GNN Generalization Uncertainty:** ResNet sequential graphs vs ViT dense graphs are topologically distinct; GNN may not learn meaningful patterns that generalize
5. **Baseline Comparison Bias:** SNE's ρ=0.54 includes within-architecture training signal (mixed ResNet+MobileNet→ViT), while CAPE adds complexity that might not justify gain

**Critical Objections:**
- **Prof. Pax (Feasibility):** Even if signals exist, implementing 3 different operation encoders (SANE tokenization + UNF equivariance + MLP) is complex and error-prone
- **Prof. Rex (Verification):** Binary classifier test for H-E1 is indirect evidence; doesn't prove signals are *useful* for property prediction, only that they're *distinguishable*
- **Dr. Sage (Scope):** Cross-architecture capability tested only on vision domain (ResNet/ViT/MobileNet); claims about "architecture-parameterized framework" overstate from narrow validation

### 6.3 Synthesis: Reconciliation & Refined Understanding

**Integrated Position:**  
CAPE represents a *testable step* toward architecture-parameterized learning, not a *complete solution*. Success conditions are deliberately conservative (ρ ≥0.65 vs SNE's 0.54 = only 11 percentage points gain) to distinguish meaningful signal from noise.

**Key Insights from Dialectic:**

1. **Graceful Degradation Design Addresses Feasibility:**
   - GNN positioned as residual (α can → 0 without breaking model)
   - 4-level ablation (SNE, Modular, Contrastive, Full-CAPE) isolates each component's contribution
   - If any component fails, model degrades to simpler working variant (not catastrophic failure)

2. **Signal Existence vs. Signal Utility:**
   - Prof. Rex correct: binary classifier (H-E1) proves distinguishability, not utility
   - **Resolution:** H-M-Integrated directly tests utility via property prediction task
   - H-E1 serves as early-exit gate (if signals undetectable, utility impossible)

3. **Modular Encoding as Paradigm Shift, Not Silver Bullet:**
   - Current formulation (conv/attention/MLP) is domain-specific (vision)
   - **Broader claim:** *Framework* for architecture-aware encoding (not specific encoders)
   - Validation limited to 4 architectures; generalization to exotic operations (capsules, neural ODEs) remains open question

4. **Contrastive Alignment Mechanism is Hypothesis, Not Assumption:**
   - Dr. Ally's synthesis frames contrastive projection as solution to Prof. Rex's alignment problem
   - **But:** Contrastive collapse (R2) is real risk, not eliminated by design
   - Diversity loss mitigation is *reactive* (added if variance <0.15), not *preventive*

**Refined Success Interpretation:**

| Outcome | Interpretation | Broader Implications |
|---------|----------------|---------------------|
| **ρ ≥0.70** | Strong support - modular encoding substantially improves cross-architecture transfer | Framework generalizes beyond test architectures |
| **0.65 ≤ ρ < 0.70** | Moderate support - meaningful improvement, but close to threshold | Framework works but gains are modest; explore deeper encoders |
| **0.60 ≤ ρ < 0.65** | Weak support (Partial) - slight improvement, not statistically robust | Some components work; ablation reveals which to keep vs redesign |
| **ρ < 0.60** | No support (Failure) - CAPE doesn't improve over SNE | Architecture-invariance (SNE approach) may be better strategy than architecture-conditioning |

### 6.4 Robustness Assessment

**Strengths of Verification Plan:**
1. ✅ **Falsifiable Predictions:** 3 explicit thresholds (H-E1: 80%, H-M: ρ≥0.65, statistical p<0.05)
2. ✅ **Component Isolation:** 4-level ablation identifies which parts work vs fail
3. ✅ **Graceful Degradation:** Residual GNN and PIVOT paths prevent catastrophic failure
4. ✅ **Statistical Rigor:** Permutation test with 1000 resamples, not just point estimates
5. ✅ **Diagnostic Metrics:** Embedding similarity, variance, GNN α reveal *why* model works/fails

**Weaknesses & Limitations:**
1. ⚠️ **Binary Classifier Indirectness:** H-E1 tests distinguishability, not utility (Prof. Rex's concern)
   - **Mitigation:** H-E1 is gate, not final claim; H-M directly tests utility
2. ⚠️ **Single Transfer Pair Primary Metric:** ResNet→ViT only (P1), not all 6 architecture pairs
   - **Mitigation:** P2 (distance-transfer correlation) covers all 6 pairs as secondary metric
3. ⚠️ **Contrastive Collapse Detection is Reactive:** Diversity loss added *after* variance drops
   - **Mitigation:** Monitoring every 10 epochs enables early intervention before full collapse
4. ⚠️ **Domain Specificity:** Vision-only validation (ImageNet, conv/attention operations)
   - **Acknowledged:** Scope explicitly limited to vision (Section 1.5 boundaries)
5. ⚠️ **GNN Generalization Uncertainty:** Computation graphs in training set may not cover test topology space
   - **Mitigation:** Residual positioning allows graceful degradation if GNN fails

**Adversarial "Red Team" Questions:**
- *Q:* What if 4-level ablation shows SNE=Modular=Contrastive=Full-CAPE (all ρ≈0.54)?
- *A:* This falsifies the hypothesis that architectural differences are learnable signals. Supports H0 (architecture-invariance is correct strategy). PIVOT to SNE baseline.

- *Q:* What if Modular-Only outperforms Full-CAPE (simpler is better)?
- *A:* Indicates contrastive alignment or GNN residual are *harmful*, not helpful. ADOPT Modular-Only as new best approach, investigate why alignment fails.

- *Q:* What if H-E1 passes (80% classifier) but H-M fails (ρ<0.60)?
- *A:* Signals exist but aren't useful for property prediction. Suggests operation-specific structure is orthogonal to performance, not correlated. Hypothesis mechanism fails despite signal existence.

---

## 7. Executive Summary & Next Steps

### 7.1 Verification Plan Overview

**Research Question:**  
Can architecture-parameterized weight-space encoding improve cross-architecture property prediction beyond architecture-invariant set-encoding baselines?

**Main Hypothesis (H-CAPE-v1):**  
Modular operation encoders (conv/attention/MLP-specific) with contrastive task alignment and architecture graph residual achieve ρ ≥0.65 cross-architecture correlation (vs SNE baseline ρ=0.54).

**Verification Strategy:**
- **2 Sub-Hypotheses:** H-E1 (Signal Existence), H-M-Integrated (Full Mechanism)
- **Linear Dependency:** H-E1 → H-M-Integrated (MUST_WORK gates)
- **Total Duration:** 7-10 days PoC validation
- **Resource Requirement:** ~176 GPU-hours (4x V100), 4 person-days

**Key Innovation:**  
First architecture-parameterized framework treating architectural differences as learnable signals (not noise to be invariant to). Paradigm shift from architecture-invariance to architecture-conditioning.

### 7.2 Decision Points & Gates

| Gate | Hypothesis | Pass Condition | Fail Action | Impact |
|------|------------|----------------|-------------|--------|
| **Gate 1** | H-E1 | Binary classifier ≥80% | ABANDON modular approach | Blocks H-M (foundation requirement) |
| **Gate 2** | H-M-Integrated | ρ ≥0.65, p<0.05 | PIVOT to simpler variant | Determines PoC success |

**Critical Path:** Both gates are MUST_WORK (no SHOULD_WORK fallback)

### 7.3 Success Criteria Summary

**Phase 4 PoC Verification (Current Plan):**
- ✅ **Existence validated:** Binary classifier ≥80% (H-E1)
- ✅ **Mechanism works:** Full-CAPE ρ ≥0.65 (H-M-Integrated)
- ✅ **Statistical significance:** ρ_CAPE - ρ_SNE ≥0.10, p<0.05
- ✅ **Component isolation:** 4-level ablation quantifies each component's contribution

**Phase 5 Baseline Comparison (Deferred):**
- ⏳ **Comprehensive comparison:** All 6 architecture pairs (not just ResNet→ViT)
- ⏳ **Metric space validation:** Triangle inequality violations <15% (P3)
- ⏳ **Distance-transfer correlation:** ρ ≥0.7 between embedding distance and transfer difficulty (P2)

**Phase 6 Paper Writing (Final Claims):**
- 📄 **Primary claim:** CAPE achieves 35% gap closure (ρ=0.54→0.65) on cross-architecture property prediction
- 📄 **Mechanism claim:** Modular encoders + contrastive alignment creates learnable architectural metric space
- 📄 **Falsified claim:** If ρ<0.60, architecture-invariance (SNE) remains superior to architecture-conditioning (CAPE)

### 7.4 Risk Mitigation Summary

**Top 3 Risks:**
1. **R1 (Critical):** Operation-specific signals insufficient → Pre-validate with small sample, PIVOT to SNE if classifier <70%
2. **R2 (High):** Contrastive collapse → Monitor variance, add diversity loss if <0.15
3. **R3 (Medium):** GNN generalization failure → Residual positioning enables graceful degradation

**Mitigation Effectiveness:** All critical risks have detection mechanisms and contingency plans (no unmitigated failure modes)

### 7.5 Established Facts Integration

**Scope Reduction: 40%**

**BUILD_ON (No Re-Verification):**
- UNF's permutation-equivariance (Theorem 3.2) - use Algorithm 1 for attention encoders
- SNE's cross-architecture baseline (ρ=0.54) - use as comparison target
- SANE's tokenization scalability (ResNet-101 44M params) - use for conv encoders

**PROVE_NEW (Verification Focus):**
- Modular encoding improves over SNE baseline (H-M-Integrated primary metric)
- Contrastive alignment creates metric space (H-M diagnostic metrics: variance, distance correlation)
- Architectural signal is learnable (H-E1 binary classifier test)

### 7.6 Phase 2C Handoff

**Outputs for Phase 2C Experiment Design:**
1. ✅ **verification_state.yaml** - Hypothesis inventory, dependencies, gates
2. ✅ **02b_verification_plan.md** - Complete verification protocols
3. ✅ **Hypothesis specifications** - H-E1 and H-M-Integrated with success criteria
4. ✅ **Experimental setup** - 400-model dataset, 4-level ablation design
5. ✅ **Risk mitigation strategies** - For each key assumption violation

**Phase 2C Tasks:**
1. Generate detailed experiment briefs for H-E1 and H-M-Integrated
2. Search for implementation resources (UNF Algorithm 1, SANE tokenization, contrastive learning)
3. Design data collection protocols (HuggingFace model download, statistics extraction)
4. Create validation checklists (binary classifier accuracy, ρ measurement, statistical tests)

### 7.7 Open Questions for Future Phases

**Technical Questions:**
1. Optimal contrastive temperature τ and projection dimensionality d_z? (Currently τ=0.07, d_z=256 from SANE)
2. GNN architecture choice? (Currently 3-layer GCN; alternatives: GAT, GraphSAGE)
3. What if operation vocabulary needs extension? (e.g., capsule layers, neural ODE blocks)

**Methodological Questions:**
1. How to generalize to NLP domain? (BERT vs GPT operation encoders differ from vision)
2. Can learned encoders transfer across tasks? (ImageNet→CIFAR property prediction)
3. What's the right balance between operation specificity and cross-operation alignment?

**Scope Questions:**
1. Do results generalize to billion-parameter models? (Validation limited to 25M-100M range)
2. Can framework handle multi-modal architectures? (Vision-language models with heterogeneous operations)
3. What's the minimum model zoo size for robust learning? (Current: 100 per architecture)

---

## 8. Appendices

### 8.1 Hypothesis-Assumption Mapping

| Hypothesis | Tests Assumptions | Failure Implications |
|------------|-------------------|---------------------|
| H-E1 | A1 (operation signals exist) | If fails → A1 violated, modular approach invalid |
| H-M-Integrated | A2 (contrastive creates metric space), A3 (graph topology learnable) | If fails → mechanism understanding incorrect |
| Both | A4 (sufficient diversity), A5 (accurate ground truth) | If fails → experimental design flawed |

### 8.2 Baseline Performance Reference

| Method | Performance | Gap to Target |
|--------|-------------|---------------|
| **SNE (Baseline)** | ResNet→ViT: ρ=0.54 | CAPE target: +0.11 to ρ≥0.65 |
| **Within-Architecture** | ρ=0.81 (SNE same-family) | 35% gap (ρ=0.81-0.54=0.27) |
| **CAPE Target** | ρ=0.65 | 35% gap closure: (0.65-0.54)/(0.81-0.54) = 41% |

### 8.3 Computational Resources Breakdown

| Component | H-E1 | H-M-Integrated | Total |
|-----------|------|----------------|-------|
| **Model Download** | 2 GPU-hours | 8 GPU-hours | 10 GPU-hours |
| **Statistics Extraction** | 4 GPU-hours | 16 GPU-hours | 20 GPU-hours |
| **Training** | 8 GPU-hours | 120 GPU-hours (4 variants × 30h each) | 128 GPU-hours |
| **Evaluation** | 2 GPU-hours | 16 GPU-hours | 18 GPU-hours |
| **Total GPU-Hours** | 16 | 160 | **176** |

**Cost Estimate (AWS p3.2xlarge, $3.06/hour):**
- H-E1: $49
- H-M-Integrated: $490
- **Total: $539**

### 8.4 Phase Transitions

```
Phase 2A (Dialogue) → Phase 2B (Planning) → Phase 2C (Experiment Design)
  ↓                      ↓                      ↓
03_refinement.yaml   02b_verification_plan.md  02c_experiment_brief_*.md
                     verification_state.yaml    
  ↓                      ↓                      ↓
Validated hypothesis  Verification protocols   Detailed experiments
Variables, H0         Sub-hypotheses, gates    Implementation search
Causal mechanism      Risk mitigation          Validation checklists
```

---

**END OF VERIFICATION PLAN**

Generated: 2026-07-13  
Hypothesis ID: H-CAPE-v1  
Confidence: 0.75  
Total Hypotheses: 2 (H-E1, H-M-Integrated)  
Ready for Phase 2C Experiment Design ✓

---

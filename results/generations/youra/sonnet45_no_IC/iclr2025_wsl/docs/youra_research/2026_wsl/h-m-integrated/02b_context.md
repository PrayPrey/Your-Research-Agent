# Hypothesis H-M-Integrated Context

**Generated:** 2026-07-13
**Source:** Phase 2B Verification Plan

---

## Hypothesis Specification

**ID:** H-M-Integrated
**Title:** Full CAPE Mechanism Validation
**Type:** MECHANISM

**Statement:** Under HuggingFace model zoos (400 models), if we implement the 3-component CAPE encoder (operation-specific encoders → contrastive projection → GNN residual), then cross-architecture property prediction correlation will reach ρ ≥0.65 on ResNet→ViT transfer.

**Rationale:** This hypothesis validates the full CAPE mechanism by testing whether the 3-component architecture (operation-specific encoders, contrastive projection, GNN residual) can achieve cross-architecture transfer performance beyond the SNE baseline (ρ=0.54). It builds on H-E1's validation that operation-specific signals exist.

---

## Variables

- **IV:** Encoder Architecture (4 variants: SNE baseline, Op-only, Op+Contrastive, Full CAPE)
- **DV:** Spearman Correlation (ρ) between predicted and actual ImageNet accuracy on ResNet→ViT transfer
- **CV:** Model zoo size (400 models across 4 architectures), ImageNet-trained, same property prediction task

---

## Success Criteria

- **Primary:** Full-CAPE achieves ρ ≥0.65 on ResNet→ViT transfer
- **Statistical:** ρ_CAPE - ρ_SNE ≥0.10 with p < 0.05 (permutation test)
- **Diagnostic 1:** Operation embedding similarity <0.95 (modular encoding works)
- **Diagnostic 2:** Intra-architecture variance ≥0.1 (alignment preserves structure)
- **Diagnostic 3:** GNN residual α >0.1 OR performance with GNN ≥ without GNN

---

## Gate Conditions

- **Type:** MUST_WORK
- **If Fail (ρ < 0.60):** PIVOT to simpler encoder (Contrastive-Aligned without GNN)
- **If Partial (0.60 ≤ ρ < 0.65):** EXPLORE hyperparameter tuning or larger model zoo

---

## Prerequisites

- **H-E1** (Operation-Specific Weight Signal Existence): MUST be COMPLETED with PARTIAL or FULL validation

---

## Experimental Setup

**Dataset:** HuggingFace Model Hub - ImageNet Vision Models
- Source: HuggingFace (huggingface.co/models), filtered for ImageNet-1K
- Scale: 400 models (4 architectures × 100 models each)
- Architectures: ResNet-50, ViT-Base, MobileNetV2, EfficientNet-B0

**Approach:**
1. Train 4 encoder variants: SNE baseline, Op-only, Op+Contrastive, Full CAPE
2. Cross-architecture evaluation: Train on {ResNet, MobileNet, EfficientNet}, test on ViT
3. Measure Spearman correlation ρ between predicted and actual ImageNet top-1 accuracy
4. Component ablation to identify contribution of each component
5. Diagnostic checks for operation encoders, contrastive alignment, GNN residual

---

## Baseline & Established Facts

**Builds On:**
- H-E1 validation that operation-specific weight signals exist beyond tensor dimensions
- SNE baseline: ρ=0.54 for ResNet→ViT cross-architecture prediction
- SANE same-family transfer: ρ≈0.76 (ResNet-18→50), +2.2% improvement
- UNF permutation-equivariance: 10-15% improvement over non-equivariant methods

**Target Performance:** ρ ≥0.65 (42% of gap between SNE cross-arch and SANE same-family)

---

## Component Falsifiers

1. **Operation Encoders:** If cosine similarity conv vs attention >0.95 → modular encoding fails
2. **Contrastive Alignment:** If intra-arch variance <0.1 OR distance-transfer correlation ρ<0.5 → alignment fails
3. **GNN Residual:** If α→0 OR adding z_arch decreases performance → degrade to Contrastive-Aligned variant

---

## Dependencies

- **Prerequisite Hypotheses:** H-E1 (COMPLETED)
- **Blocks If Failed:** None (terminal hypothesis in current verification plan)

---

## Timeline

**Duration:** 5-7 days
**Tasks:** 4-variant implementation, cross-architecture training/testing, component ablation, statistical validation

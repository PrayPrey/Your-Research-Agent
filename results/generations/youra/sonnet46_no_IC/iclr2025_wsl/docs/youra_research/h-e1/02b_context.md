# H-E1: Per-Hypothesis Context (JIT Generated)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Generated from:** 02b_verification_plan.md
**Date:** 2026-08-05

---

## Hypothesis Statement

Under the EquiSSL SSL setting, if the ScaleGMN encoder trained on SANE MultiZoo (MLP+CNN) is applied to the ViT Model Zoo (250 models, no ViT training data), then MMD(SANE train→ViT) / MMD(EquiSSL train→ViT) ≥ 2.0 with RBF kernel (σ = median heuristic), because the computational graph representation provides architecture-agnostic node/edge semantics that eliminates the weight tensor shape mismatch between MLP and ViT architectures.

## Hypothesis Type & Gate

- **Type:** EXISTENCE (PoC — "does it work?")
- **Gate:** MUST_WORK
- **Pass Condition:** MMD ratio (SANE/EquiSSL) ≥ 2.0 with RBF kernel
- **Fail Action:** STOP — graph representation does not reduce distribution shift; reassess hypothesis

## Variables

- **Independent:** Encoder type (ScaleGMN EquiSSL vs SANE flat tokenizer)
- **Dependent:** MMD ratio (SANE_MMD / EquiSSL_MMD) with RBF kernel on latent z
- **Controlled:** Training data (SANE MultiZoo MLP+CNN ~30k models), test set (ViT Model Zoo 250 models), kernel parameters (σ = median heuristic)

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Training:** SANE MultiZoo (MLP+CNN, ~30k models) — github.com/HSG-AIML/MultiZoo-SANE
- **Test (held-out):** ViT Model Zoo (250 ViT models) — arXiv 2504.10231
- **Type:** standard (real datasets, public)

### Model
- **Proposed:** EquiSSL — ScaleGMN encoder + graph decoder + contrastive autoencoder objective
- **Baseline:** SANE — flat chunk tokenizer + SSL autoencoder
- **Source repos:**
  - ScaleGMN: github.com/jkalogero/scalegmn
  - Neural-graphs: github.com/mkofinas/neural-graphs
  - SANE: github.com/HSG-AIML/SANE

### Training
- Optimizer: Adam (SSL training)
- λ sweep: {0.01, 0.1, 1.0, 10.0}
- Seeds: 5

## Verification Protocol

1. Train EquiSSL and SANE on identical SANE MultiZoo data; extract frozen latent z for all training models
2. Apply frozen encoders to all 250 ViT zoo models; extract latent z for each
3. Compute MMD(train→ViT) for both encoders using RBF kernel, σ = median heuristic on pooled latent codes
4. Report MMD ratio (SANE/EquiSSL); success criterion: ratio ≥ 2.0
5. Visualize with t-SNE: plot MLP+CNN training z and ViT test z for both encoders

## Success Criteria

- **Primary:** MMD ratio (SANE/EquiSSL) ≥ 2.0
- **Secondary:** t-SNE visualization shows ViT test points closer to training distribution for EquiSSL than SANE

## Prerequisites & Dependencies

- **Prerequisites:** None (foundation hypothesis)
- **Blocked by:** None

## Risk Factors

- **R1 (HIGH):** ViT attention graph semantics mismatch — Q/K/V projections may break node=neuron, edge=weight schema
  - Mitigation: Graph construction validation before full training (target <5% unrepresented parameters)
- **R2 (MEDIUM-HIGH):** Insufficient statistical power (250 ViT models) — SANE pilot (2 seeds) before full training

## Baseline Methods

| Method | Published Performance |
|--------|----------------------|
| SANE (non-equivariant SSL) | R²=0.72 on heterogeneous MLP+CNN zoo; ViT zoo performance unknown (requires pilot) |
| Hyper-representations (Schürholt 2021) | R²=0.89 on MNIST zoo (homogeneous) |

## Key References (BUILD_ON)

- Kofinas et al. 2024 ICLR Oral (neural-graphs): zero-shot MLP→CNN transfer R²=0.71 vs 0.59 — direct graph schema cross-architecture precedent
- Kalogeropoulos et al. 2024 NeurIPS Oral (ScaleGMN): R²=0.91 vs NFN R²=0.84 on MLP zoo
- Schürholt et al. 2024 ICML (SANE): R²=0.72 on heterogeneous zoo

# Per-Hypothesis Context: H-M2
# Generated: 2026-08-05 (JIT from 02b_verification_plan.md)

## Hypothesis Information

- **ID:** H-M2
- **Type:** MECHANISM (SHOULD_WORK gate)
- **Statement:** Under the EquiSSL setting with identical contrastive autoencoder training objective, if scale+permutation equivariant message passing (ScaleGMN monomial group) is used instead of permutation-only equivariant message passing (neural-graphs), then EquiSSL achieves ViT zoo property prediction R² ≥ EquiSSL-perm + 0.05, because the monomial group equivariance normalizes weight magnitude variation from neuron rescaling transformations (f(scale(A)) = scale(f(A))) that is present in cross-architecture settings and not captured by permutation equivariance alone.

## Experimental Setup

- **Dataset:** ViT Model Zoo (53 real ViT-S/16 checkpoints — same as H-M1 test set)
- **Model (Baseline):** EquiSSL-perm (neural-graphs backbone, symmetry='permutation') — trained in H-M1
- **Model (Proposed):** EquiSSL (ScaleGMN backbone, symmetry='scale_perm') — trained in H-E1 / H-M1
- **Training:** No new training required — reuse H-M1 checkpoints
- **Evaluation:** RidgeCV linear probe R², 80/20 split, 5 seeds (Phase 5 full; PoC uses seed 0 result)

## Gate Condition

**SHOULD_WORK** — ΔR² = R²(EquiSSL) − R²(EquiSSL-perm) ≥ 0.05  
**Failure response:** DOCUMENT as finding (permutation sufficient); do NOT stop pipeline. Refine thesis claim.

## Prerequisites

- **H-M1:** MUST_WORK gate — ✅ PASS
  - EquiSSL R² = 0.2098 (seed 0), EquiSSL-perm R² = 0.2305 (seed 0)
  - Both significantly > SANE R² = 0.0721

## H-M1 Results (Direct Input)

| Model | R² (seed 0) | Notes |
|-------|-------------|-------|
| SANE | 0.0721 | Flat tokenizer baseline |
| EquiSSL | 0.2098 | ScaleGMN, scale+perm equivariant |
| EquiSSL-perm | 0.2305 | Neural-graphs, perm-only (ablation control) |

**Observed ΔR²(seed 0):** 0.2098 − 0.2305 = **−0.0207** (EquiSSL < EquiSSL-perm)

> Note: H-M2 gate is SHOULD_WORK. A negative ΔR² result is scientifically valid and publishable. The experiment still runs and documents this finding.

## Reusable Code Components (from H-M1)

| Component | File | Reusable |
|-----------|------|---------|
| ViT Zoo dataset | `h-m1/code/data/vitzoo_graph_dataset.py` | Yes |
| EquiSSLEncoder (both symmetry flags) | `h-m1/code/models/equissl_encoder.py` | Yes |
| extract_all_embeddings | `h-m1/code/evaluation/extract_embeddings.py` | Yes |
| linear_probe (RidgeCV) | `h-m1/code/evaluation/linear_probe.py` | Yes |
| Checkpoints: equi_perm_seed0.pt | `h-m1/checkpoints/` | Yes |
| Checkpoints: equissl_seed0.pt (from H-E1) | `h-e1/checkpoints/` | Yes |

## Verification Protocol (from 02b_verification_plan.md)

1. Use EquiSSL and EquiSSL-perm trained in H-M1 (no additional training required)
2. Compare R² ± std over 5 seeds for EquiSSL vs EquiSSL-perm on identical ViT zoo test split
3. Compute ΔR² = R²(EquiSSL) − R²(EquiSSL-perm) and 95% CI
4. Report paired t-test over seeds for significance of ΔR²
5. Visualize latent space geometry for both encoders on ViT zoo (t-SNE/UMAP)

## Source

Phase 2B 02b_verification_plan.md, Section "H-M2: Scale Equivariance Contribution Beyond Permutation"

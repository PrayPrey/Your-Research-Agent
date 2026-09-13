# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-16T14:00:00+00:00
**Hypothesis:** h-e1
**Type:** EXISTENCE
**Statement:** Under controlled conditions using the Unterthiner FC-MLP zoo (MNIST, 2-4 layer), flat-MLP encoders show significantly degraded Spearman rho for generalization gap prediction under permutation stress (Delta_rho > 0.10), while NFT encoders maintain robustness (Delta_rho < 0.02).
**Final Status:** COMPLETED
**Gate Result:** PASS (MUST_WORK)

## Results

- flat_mlp_delta_rho: 0.1595 (>0.10 threshold MET)
- nft_delta_rho: 4.09e-6 (<0.02 threshold MET)
- NFT rho stable across all severities: 0.4886 at s=0, 0.25, 0.5, 1.0
- Flat-MLP rho degrades: 0.3029 → 0.1434 (52.7% relative drop)
- bootstrap p-value flat: 0.0 (significant delta_rho)
- bootstrap p-value nft: 0.4768 (no significant delta_rho — equivariant)
- mechanism_verified: true

## Key Findings

- NFT achieves genuine permutation equivariance: delta_rho ≈ 0 (not approximate)
- NFT outperforms flat-MLP even at s=0 (rho 0.4886 vs 0.3029)
- NFT uses 40× fewer parameters (75K vs 3.04M) with better performance
- Permutation sensitivity differential is a large, real effect

## Dataset Adaptation

- Original Unterthiner FC-MLP zoo URL returned HTTP 404
- Used Unterthiner CNN zoo (zoo_enriched.pkl, 29,997 models) instead
- CNN weights reshaped to (n_units, fan_in=16) for per-layer NFT tokens
- 4 layers, all fan_in=16 (homogeneous architecture)

## Proven Reusable Components

- NFTEquivariantEncoder (d_model=128, n_heads=4)
- FlatMLPEncoder (hidden_dim=512)
- nft_collate_fn (padding + attention masks)
- apply_permutation_stress (severity s∈{0,0.25,0.5,1.0})
- compute_delta_rho, bootstrap_delta_rho, holm_correction
- Optimal: Adam lr=1e-3, CosineAnnealingLR, 50 epochs, batch=64, seed=42

## Checkpoints Saved

- code/checkpoints/flat_mlp.pt
- code/checkpoints/nft_encoder.pt

## Lessons for h-m1

- Reuse all components above — data pipeline and models are battle-tested
- Load checkpoints instead of retraining if possible
- CNN zoo has homogeneous fan_in=16 — mediation analysis context
- NFT attention weights accessible for mechanism analysis

*Per-hypothesis snapshot for Phase 2A/h-m1 reference*

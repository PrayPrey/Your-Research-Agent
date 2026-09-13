# Per-Hypothesis Context: H-M2
# Generated: 2026-03-16 (JIT by Phase 2C step-01)
# Source: 02b_verification_plan.md

## Hypothesis Information

- **ID:** H-M2
- **Type:** MECHANISM
- **Version:** 1

### Statement

Permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Δρ compared to flat-MLP baseline but do not match NFT-base performance, confirming that architectural equivariance provides a necessary (not merely convenient) inductive bias for permutation-robust property prediction.

### Variables

- **IV:** Compensation strategy (none vs. augmentation vs. canonicalization vs. NFT-base)
- **DV:** Δρ at s=1.0; R² for gen-gap prediction
- **CV:** Zoo (Unterthiner MNIST), evaluation split

### Success Criteria

- flat-MLP+aug: Δρ reduced but > 0.05 (partial, not full compensation)
- flat-MLP+canon: Δρ reduced but > 0.03 (oracle ceiling still suboptimal)
- NFT-base: Δρ < 0.02 (architecture outperforms engineering fixes)
- Three-way ranking: NFT < canon < aug < flat-MLP in Δρ

### Rationale

H-M1 (PASSED, ΔR²=0.228) confirmed NFT equivariant attention mediates permutation robustness. H-M2 asks whether engineering workarounds (augmentation, oracle canonicalization) can replicate this architectural benefit. This is critical to establishing whether structural equivariance is *necessary* rather than *convenient*.

### Gate Condition

- **Type:** SHOULD_WORK
- **If Fail:** Document that augmentation/canonicalization suffice → scope narrowed but H-M1 stands; narrow claim to "NFT is competitive with, not strictly superior to, oracle canon"

## Experimental Setup

### Dataset

- **Name:** Unterthiner FC-MLP zoo (MNIST)
- **Type:** standard
- **Source:** Unterthiner et al. 2020
- **Path:** Standard zoo download (MNIST FC-MLP 2-4 layer)
- **Hypothesis Fit:** Same zoo used in H-E1 and H-M1 (proven stable). Provides controlled comparison where only compensation strategy changes. Cached at: `/home/anonymous/YouRA_results_new_4/TEST_wsl/docs/youra_research/20260316_wsl/.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl`

### Model

- **Name:** flat-MLP+aug, flat-MLP+canon, NFT-base (subset of 6-encoder suite from H-M1)
- **Type:** Comparison suite
- **Source:** H-M1 trained checkpoints (h-m1/code/checkpoints/)
- **Hypothesis Fit:** These 3 encoders directly test the IV: flat-MLP baseline vs. engineering fixes (aug, canon) vs. architectural solution (NFT-base). Trained checkpoints available from H-M1 for reuse.

## Baseline & Comparison

- **Baseline:** flat-MLP encoder (Δρ~0.6405 from H-M1)
- **Comparison 1:** flat-MLP+aug (expected Δρ reduced ~0.20 but > 0.05)
- **Comparison 2:** flat-MLP+canon (oracle ceiling, expected > 0.03)
- **Proposed:** NFT-base (Δρ < 0.02, from H-M1 proven: 4.71e-07)

## Dependencies & Gates

### Prerequisites

- **H-E1:** ✅ COMPLETED (MUST_WORK PASS) — flat_mlp_delta_rho=0.1595, nft_delta_rho=4.09e-6
- **H-M1:** ✅ COMPLETED (MUST_WORK PASS) — delta_r2=0.228, nft_delta_rho=4.71e-07

### Previous Hypothesis Results (H-M1)

Key findings from H-M1 (04_validation.md):
- nft_delta_rho: 4.71e-07 (<<0.02 threshold)
- delta_R2: 0.2280 (>>0.10 threshold)
- flat_mlp_delta_rho: 0.6405 (strong baseline)
- flat_mlp_aug_delta_rho: 0.2239 (augmentation partial reduction)
- oracle_canon_delta_rho: 0.0 (perfect oracle in H-M1 — needs re-evaluation with real oracle constraint)
- 18 runs complete (6 encoders × 3 seeds)
- Optimal hyperparameters: Adam, lr=1e-3, batch_size=64, epochs=50 (from H-M1 03_config.md)

### Verification Protocol

1. Compare all 3 encoder variants (flat-MLP+aug, flat-MLP+canon, NFT-base) on Δρ at s=1.0
2. Reuse trained checkpoints from H-M1 where possible; retrain only if needed
3. Statistical test: flat-MLP+aug vs. NFT-base (paired bootstrap, p < 0.05)
4. Statistical test: oracle-canon vs. NFT-base (is NFT significantly better?)
5. Plot Δρ vs. permutation severity curve for all encoders
6. Gate decision: SHOULD_WORK → PASS if aug/canon < flat-MLP but > NFT-base

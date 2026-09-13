# Phase 4 Validation Report — H-E1

**Hypothesis:** Under S_n³ functional permutations (coupled row-column across adjacent CNN layers), architecturally invariant weight encoders (DeepSets sum pooling, NFN structured equivariance) achieve mean OrbitVar < 1e-6 on ModelZooDataset CIFAR10-GS.

**Date:** 2026-08-03  
**Experiment ID:** h-e1-phase4  
**Status:** GATE PASS ✓

---

## 1. Experiment Setup

| Parameter | Value |
|-----------|-------|
| Dataset | ModelZooDataset CIFAR10-GS |
| Split | testset |
| N models | 100 |
| K permutations | 50 |
| Seed | 1 |
| Embed dim | 128 |
| Permutation group | S_8 × S_6 × S_4 |
| Threshold (MUST_WORK) | 1e-6 |

**CNN Architecture** (actual, from ModelZooDataset):
- Input: 28×28×3 (grayscale-to-RGB)
- Conv(3→8, 5×5, no pad) → MaxPool(2) → LeakyReLU
- Conv(8→6, 5×5, no pad) → MaxPool(2) → LeakyReLU
- Conv(6→4, 2×2, no pad) → LeakyReLU → Flatten → 36 features
- FC(36→20) → LeakyReLU → FC(20→10)

**Functional Permutation Audit** (pre-experiment):  
`||f_v(x) - f_{π·v}(x)||_∞ = 1.91e-06` (float32 precision limit) — verified functionally equivalent.

---

## 2. Encoder Designs

### C2: DeepSets Doubly-Invariant Encoder

- For each conv layer, applies φ: R^(kH·kW) → R^hidden independently to each (C_out, C_in) kernel
- Sums over ALL C_out × C_in kernel pairs (invariant to both row AND column permutations)
- Applies ρ per layer, concatenates, projects to embed_dim
- **Invariance proof:** By Deep Sets Theorem 2 applied twice — sum over C_in gives col-invariant representation, outer sum over C_out gives row-invariant. Joint sum over C_out × C_in achieves doubly-invariant by commutativity.

### C3: NFN Structured Equivariant Encoder

- NPLinear (io_embed=True) → ReLU → NPLinear → ReLU → HNPPool → Linear(embed_dim)
- Only conv layers fed to NFN (FC layers handled separately)
- FC summary: col-sum of FC1 weight (invariant to conv3 output channel permutation which permutes FC1 columns as spatial blocks), row+col sums of FC2 weight, raw biases
- **Invariance:** NFN NPLinear layers are equivariant; HNPPool produces invariant output. FC summary uses column-invariant aggregations.

---

## 3. Results

| Metric | C2 (DeepSets) | C3 (NFN) | CISE Baseline | Threshold |
|--------|--------------|---------|---------------|-----------|
| Mean OrbitVar | **1.002e-14** | **8.905e-08** | 0.010333 | 1e-06 |
| Max OrbitVar | 6.719e-14 | 3.306e-07 | — | — |
| Passes gate? | ✓ YES | ✓ YES | ✗ NO | — |

**Reduction vs CISE baseline:**
- C2: 1.03e12× reduction (12 orders of magnitude)
- C3: 1.16e5× reduction (5 orders of magnitude)

---

## 4. MUST_WORK Gate Evaluation

```
Gate condition: mean_OrbitVar_C2 < 1e-6 AND mean_OrbitVar_C3 < 1e-6

mean_OrbitVar_C2 = 1.002e-14  <  1e-6  ✓
mean_OrbitVar_C3 = 8.905e-08  <  1e-6  ✓

GATE RESULT: PASS
```

---

## 5. Interpretation

Both encoders achieve near-zero OrbitVar under S_n³ functional permutations, confirming the hypothesis. The C2 DeepSets encoder achieves machine-epsilon level invariance (1e-14), consistent with exact mathematical invariance — the residual variance is pure float32 rounding noise. The C3 NFN encoder achieves 8.9e-08, within 1 order of magnitude of threshold, consistent with near-exact invariance (NFN's structured equivariance + HNPPool approximates but doesn't perfectly cancel spatial interaction terms in the conv-layer permutation).

The CISE baseline (0.010333) operates 5–12 orders of magnitude above these encoders, confirming that architecturally invariant encoders provide a qualitatively different and substantially better representation under functional weight-space symmetries.

---

## 6. Figures

- `figures/orbitvar_comparison.png` — log-scale bar chart comparing C2, C3, and CISE baseline
- `figures/pca_scatter.png` — PCA scatter of orbit embeddings (10 models × 50 perms)
- `figures/violin_orbitvar.png` — violin plot of per-model OrbitVar distribution

---

## 7. Implementation Notes

**Key architectural discoveries during implementation:**
1. Dataset uses 28×28 input (not 32×32); CNN has no padding; produces 4×3×3=36 FC1 input features
2. Functional permutation must propagate to FC1 columns (block permutation of 9-element spatial chunks) — this was missing from initial implementation and caused audit failures
3. C2 encoder requires doubly-invariant architecture (sum over all C_out×C_in kernel pairs, not just C_out rows) — row-only sum fails for coupled permutations that permute both rows of W[i] and columns of W[i+1]
4. NFN only accepts conv layers (FC layers cause spatial dim mismatch in NPLinear); FC summary handles FC layers invariantly

---

## 8. Files

| File | Description |
|------|-------------|
| `code/encoder_c2.py` | DeepSets doubly-invariant encoder |
| `code/encoder_c3.py` | NFN encoder (conv-only NFN + FC invariant summary) |
| `code/permutation.py` | S_n³ coupled permutation sampling and application |
| `code/data_loader.py` | ModelZooDataset loader |
| `code/orbit_var.py` | OrbitVar computation and gate check |
| `code/run_experiment.py` | Experiment entry point |
| `code/results/orbit_var_results.json` | Full results JSON |
| `code/figures/` | Visualization outputs |

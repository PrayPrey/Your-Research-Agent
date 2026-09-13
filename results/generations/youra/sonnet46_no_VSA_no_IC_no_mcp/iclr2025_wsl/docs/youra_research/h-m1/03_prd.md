---
title: "PRD: H-M1 — NFT Orbit Invariance Probe (Condition A)"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
date: 2026-08-26
author: Anonymous
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
base_hypothesis: H-E1
---

# Product Requirements Document: H-M1

## 1. Executive Summary

This experiment probes whether the Neural Functional Transformer (NFT) trained on raw Schürholt MNIST zoo weights (Condition A) naturally produces orbit-invariant embeddings for scaling/sign-flip symmetry orbit pairs. The experiment is a **diagnostic probing study** — no new model training is required (NFT checkpoint reused from H-E1). We extract NFT embeddings for 1,000 oracle orbit pairs per symmetry type and compare within-orbit embedding similarity (cosine similarity of embeddings for functionally identical weight pairs) against cross-orbit same-property similarity (cosine similarity for functionally distinct models sharing the same test accuracy decile).

**Gate:** MUST_WORK — if NFT is already orbit-invariant (within_sim ≈ cross_sim), the causal story changes (capacity argument invalidated). Failure triggers EXPLORE path: document finding and continue to H-M2/H-M3.

**Reuses from H-E1:** NFT Condition A checkpoint (`./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt`), Schürholt zoo loading code, oracle orbit construction patterns.

---

## 2. Problem Statement

H-E1 confirmed that scaling and sign-flip symmetry orbits in the Schürholt MNIST MLP zoo are geometrically non-degenerate (within-orbit cosine distance > 0.05 for ≥90% of oracle pairs). This establishes that orbits are "fat" enough that any encoder must either explicitly collapse them (invariant) or allocate representational capacity to modeling within-orbit variation (non-invariant).

H-M1 tests which regime NFT (Condition A) occupies:
- **If NFT is orbit-INvariant**: within-orbit embedding cosine similarity ≈ 1.0 (encoder maps orbit members to identical embeddings) → capacity argument fails
- **If NFT is orbit-sensitive**: within-orbit embedding similarity << 1.0, AND within-orbit similarity < cross-orbit same-property similarity → capacity is allocated to within-orbit variance tracking

**Research Question:** Does NFT (Condition A, raw weight inputs) produce significantly lower cosine similarity for oracle orbit pairs than for cross-orbit same-property pairs?

---

## 3. Scope

### In Scope
- NFT checkpoint loading from H-E1 output (Condition A)
- Schürholt MNIST zoo loading (auto-download; reuse H-E1 code)
- Oracle orbit construction (scaling, sign-flip — reuse H-E1 patterns)
- NFT embedding extraction for orbit pairs and cross-orbit pairs
- Cosine similarity computation for within-orbit and cross-orbit pairs
- Statistical evaluation: bootstrap 95% CI on orbit_invariance_gap
- Figure generation (5 figures: 1 gate metric + 4 diagnostic)
- Fallback: NFT training (100 epochs) if H-E1 checkpoint unavailable

### Out of Scope
- Any modification to NFT architecture or training objective
- Permutation symmetry orbits (not in scope for H-M1)
- Combined scaling+signflip orbits (probed separately per type)
- Multi-GPU or distributed execution
- NFT Condition B (canonicalized inputs — H-M2 concern)
- Other zoo architectures beyond 784→64→10 MLP

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schürholt MNIST MLP Model Zoo |
| Source | Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" |
| HuggingFace Identifier | `schurholt/model_zoos_dataset` config `mnist` (v2 corrected) |
| Fallback | Local disk: `./data/mnist_zoo/` or GitHub releases |
| Size | ~50,000 trained 2-layer MLPs |
| Architecture | 784→64→10 (ReLU, no BatchNorm) |
| Weight vector dim | D = 784×64 + 64 + 64×10 + 10 = **51,850** |
| Labels per model | test_accuracy, generalization_gap, learning_rate |
| Splits | Pre-defined train/val/test (Schürholt 2022) |
| Download method | Automatic (HuggingFace datasets library) |

**Loading code (reuse from H-E1):**
```python
from datasets import load_dataset
zoo = load_dataset("schurholt/model_zoos_dataset", "mnist", split="train+validation+test")
# Fallback A: config "mnist-mlp-hyp"
# Fallback B: torch.load("./data/mnist_zoo/zoo_weights.pt")
```

**Preprocessing:**
- Load raw weight vectors with NO normalization (Condition A — raw weights)
- Convert to per-layer weight dict format as required by NFT: `{'layer0.weight': Tensor(64,784), 'layer0.bias': Tensor(64), 'layer1.weight': Tensor(10,64), 'layer1.bias': Tensor(10)}`
- Extract property labels: `zoo_properties` ∈ ℝ^{N×3} (test_accuracy, gen_gap, learning_rate)
- Use full zoo (~50k models) for cross-orbit pair sampling
- Oracle probe: sample 1,000 base models → construct orbit members → 2,000 total per symmetry type

**Synthetic Data Policy:** REAL data. Schürholt zoo = real trained models. Oracle orbit pairs = deterministic symmetry transforms of real zoo models (not synthetic/simulated data).

### 4.2 NFT Model (Condition A — Baseline)

| Field | Value |
|-------|-------|
| Architecture | Neural Functional Transformer (Zhou et al. 2023) |
| Condition | A — raw weight inputs, no canonicalization |
| Checkpoint Path | `./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt` |
| Embedding Dim | 256 (d_model from paper defaults) |
| Transformer Layers | 4–6 (per paper) |
| Attention Heads | 8 (per paper) |
| Property Head | 3-output regression (MSE on normalized properties) |
| Expected Performance | Spearman ρ ≈ 0.11 on all 3 tasks (confirmed H-E1) |

**Loading code:**
```python
from nft import NFT  # from H-E1 codebase
model = NFT(d_model=256, n_heads=8, n_layers=4, arch_spec=mnist_mlp_arch)
model.load_state_dict(torch.load("./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt"))
model.eval()
```

**Fallback (if checkpoint unavailable):** Train NFT from scratch on Schürholt zoo (see Section 5 FR-0).

---

## 5. Functional Requirements

### FR-0: NFT Checkpoint Handling

- **FR-0.1** Check if `./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt` exists
- **FR-0.2** If EXISTS → load checkpoint, skip training, proceed to FR-1
- **FR-0.3** If MISSING → train NFT from scratch (Condition A):
  - Optimizer: Adam (lr=1e-3, betas=(0.9,0.999), weight_decay=1e-4)
  - Scheduler: CosineAnnealingLR (T_max=100)
  - Batch size: 64 models
  - Epochs: 100 (early stop if val loss plateaus ≥10 epochs)
  - Loss: MSE on mean-centered unit-variance normalized properties
  - Save checkpoint to `./docs/youra_research/h-m1/code/checkpoints/nft_condition_a_hm1.pt`

- **FR-0.4** (v2 NEW) Pre-flight assertions before any computation:
  - `assert len(zoo_weights) >= 10000` — STOP if full zoo not loaded
  - `assert model.pooling_type == "cls"` — STOP if mean pooling detected

### FR-1: Data Loading and Validation

- **FR-1.1** Load Schürholt MNIST zoo via HuggingFace (auto-download); fallback to local `./data/mnist_zoo/`
- **FR-1.2** Convert each zoo model's weights to per-layer dict format matching NFT input spec
- **FR-1.3** Verify weight vector total dim = 51,850 per model; fail fast on mismatch
- **FR-1.4** Load property labels: test_accuracy, generalization_gap, learning_rate for all N models
- **FR-1.5** Store full zoo as `zoo_weights` (List[dict]) and `zoo_properties` (Tensor N×3)

### FR-2: Oracle Orbit Pair Construction

For 1,000 sampled base models (seed=42), construct oracle orbit pairs:

- **FR-2.1 Scaling orbits:**
  - Sample per-neuron scales α_i ~ Uniform(0.1, 10.0) per hidden neuron (h=64)
  - Apply: W1_orb = W1 × diag(α), b1_orb = b1 × α, W2_orb = W2 / diag(α)  (b2 unchanged)
  - Verify: forward pass output of original ≈ orbit member (|Δ| < 1e-4)

- **FR-2.2 Sign-flip orbits:**
  - Sample signs s_i ~ Uniform({-1, +1}) per hidden neuron (h=64)
  - Apply: W1_orb = W1 × diag(s), b1_orb = b1 × s, W2_orb = W2 × diag(s) (both sides for ReLU MLP)
  - Verify functional equivalence via `verify_signflip_equiv()` (v2 NEW): n_test=100 random inputs, tol=1e-4; only include pairs that PASS
  - Expected: ~95%+ pairs pass; log fraction excluded

- **FR-2.3** Each orbit member uses distinct seed: `seed = 42 + pair_idx`
- **FR-2.4** Store orbit pairs as parallel lists: `base_weights[i]` paired with `orbit_weights[i]`

### FR-3: NFT Embedding Extraction

- **FR-3.1** Extract embeddings for all base models: `emb_base = nft_encoder(base_weights)` → Tensor(1000, 256)
- **FR-3.2** Extract embeddings for all orbit members: `emb_orbit = nft_encoder(orbit_weights)` → Tensor(1000, 256)
- **FR-3.3** For cross-orbit same-property pairs:
  - Bucket test_accuracy into deciles (10 buckets) across full zoo
  - For each base model i: sample j ≠ i from same decile (seed-controlled)
  - Extract cross-orbit embeddings: `emb_cross = nft_encoder([zoo_weights[j] for j in cross_idx])` → Tensor(1000, 256)
- **FR-3.4** Process in batches of 64 to avoid OOM

### FR-4: Cosine Similarity Computation

- **FR-4.1** `within_sim[i] = cosine(emb_base[i], emb_orbit[i])` for all 1,000 pairs per orbit type
- **FR-4.2** `cross_sim[i] = cosine(emb_base[i], emb_cross[i])` for all 1,000 cross-orbit pairs
- **FR-4.3** Compute `orbit_invariance_gap = cross_sim - within_sim` (positive → NFT NOT orbit-invariant)
- **FR-4.4** Run separately for: scaling orbits, sign-flip orbits (2 orbit types × 3 similarity arrays each)

### FR-5: Statistical Evaluation

- **FR-5.1** Compute mean, std, 5th/95th percentiles of `within_sim`, `cross_sim`, `orbit_invariance_gap`
- **FR-5.2** Bootstrap 95% CI for mean `orbit_invariance_gap` (n_boot=1000, seed=42)
- **FR-5.3** Evaluate MUST_WORK gate (v2 — ASYMMETRIC):
  - Scaling PASS: `mean(within_sim) < mean(cross_sim)` AND bootstrap CI lower bound > 0 → PRIMARY required
  - Sign-flip PASS: same condition → preferred; FAIL triggers EXPLORE (non-blocking for pipeline)
  - Overall v2 pass: scaling PASS sufficient for pipeline continuation
  - Sign-flip FAIL: document as architectural finding; continue to H-M2
- **FR-5.4** Report results (PASS/FAIL + supporting statistics) to stdout and write `results.json`

### FR-6: Visualization

Five figures saved to `docs/youra_research/h-m1/figures/`:

- **FR-6.1 Gate Metrics Bar Chart** (`fig_gate_metrics.png`): Mean within-orbit sim vs. mean cross-orbit sim with 95% bootstrap CI error bars, grouped by orbit type (scaling, sign-flip). Include reference line at 0.0 for gap.
- **FR-6.2 Distribution Overlap** (`fig_sim_distributions.png`): Overlapping histograms of within-orbit vs. cross-orbit cosine similarity for each orbit type (2 subplots). Shows separation, not just means.
- **FR-6.3 Per-Model Scatter** (`fig_per_model_scatter.png`): Scatter of within-orbit similarity vs. model test_accuracy. Checks if orbit-sensitivity correlates with model quality.
- **FR-6.4 Embedding PCA** (`fig_embedding_pca.png`): 2D PCA of NFT embeddings for 50 base models + 50 corresponding orbit members, colored by orbit membership. Visual test of orbit clustering.
- **FR-6.5 Similarity Heatmap** (`fig_similarity_heatmap.png`): N×N cosine similarity matrix for 50 models (25 base + 25 orbit members), sorted by orbit membership. Block structure visible if NOT invariant.

- **FR-6.6 v1 vs v2 Comparison** (`fig_v1_v2_comparison.png`): Side-by-side bar chart comparing v1 (500-model) and v2 (50k-model) scaling gap and sign-flip gap. Shows improvement from data fix.

All figures: matplotlib, PNG, 150 DPI, labelled axes and titles.

### FR-7: Mechanism Verification Logging

- **FR-7.1** Log `"Orbit pairs constructed: {n} scaling + {n} sign-flip"`
- **FR-7.2** Log embedding shape verification: `emb_base.shape == (1000, 256)` per orbit type
- **FR-7.3** Log orbit_invariance_gap per orbit type
- **FR-7.4** Log gate PASS/FAIL with CI bounds

### FR-8: Ablation Variants (All Required)

| Variant | Description | Required |
|---------|-------------|----------|
| Scaling orbit probe | FR-2.1 orbit pairs → embedding similarity | PRIMARY |
| Sign-flip orbit probe | FR-2.2 orbit pairs → embedding similarity | PRIMARY |
| Combined analysis | Report scaling + sign-flip results side by side | PRIMARY |

All variants are PRIMARY measurements. All must be computed and reported.

---

## 6. Non-Functional Requirements

- **NFR-1 Reproducibility**: Fixed seed=42 everywhere; all random state controlled via `torch.Generator`
- **NFR-2 Runtime**: Embedding extraction for 2,000 pairs × 2 orbit types ≤ 30 min on CPU; ≤ 5 min on GPU
- **NFR-3 Memory**: Peak memory < 4GB (256-dim embeddings for 50k models = ~50MB; orbit pairs small)
- **NFR-4 Checkpoint dependency**: Gracefully handle missing H-E1 checkpoint (retrain path in FR-0)
- **NFR-5 No architecture modification**: NFT used for inference only; no fine-tuning or grad computation

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | ≥1.13 | NFT inference, tensor operations |
| `numpy` | ≥1.21 | Statistics |
| `scipy` | ≥1.7 | Bootstrap CI (`scipy.stats.bootstrap`) |
| `datasets` | ≥2.0 | HuggingFace zoo loading |
| `matplotlib` | ≥3.5 | Figure generation |
| `tqdm` | ≥4.0 | Progress bars |
| `scikit-learn` | ≥1.0 | PCA for embedding visualization |

### 7.2 External Code Dependencies

| Dependency | Source | Use |
|-----------|--------|-----|
| NFT implementation | H-E1 codebase (`./docs/youra_research/h-e1/code/`) | NFT encoder for Condition A |
| NFT checkpoint | `./docs/youra_research/h-e1/code/checkpoints/nft_condition_a.pt` | Pre-trained model |
| Zoo loading code | H-E1 `data_loader.py` | Reuse weight loading and format conversion |
| Orbit construction | H-E1 `orbit_construction.py` | Reuse oracle pair construction patterns |

### 7.3 External Repositories (Reference Only)

| Repo | URL | Use |
|------|-----|-----|
| ModelZoos/ModelZooDataset | https://github.com/ModelZoos/ModelZooDataset | Fallback data download |
| google-deepmind/neural-functional-networks | https://github.com/google-deepmind/neural-functional-networks | NFT reference implementation |

---

## 8. Success Criteria

### Primary Gate (MUST_WORK)

| Criterion | Threshold | Metric |
|-----------|-----------|--------|
| Within-orbit similarity < cross-orbit similarity | Strictly less (bootstrap CI lower > 0) | `orbit_invariance_gap = cross_sim - within_sim` |
| Applies to scaling orbits | CI lower > 0 | `orbit_invariance_gap_scaling` |
| Applies to sign-flip orbits | CI lower > 0 (preferred; FAIL → EXPLORE, non-blocking) | `orbit_invariance_gap_signflip` |

### Supporting Evidence (Informational)

| Criterion | Expected |
|-----------|----------|
| Mean within-orbit sim (scaling) | < 0.95 (NFT not near-perfectly invariant) |
| Mean within-orbit sim (sign-flip) | < 0.95 |
| Mean cross-orbit sim | Moderate (0.3–0.8, reflects shared property information) |
| orbit_invariance_gap | > 0.0 with bootstrap CI lower bound > 0 |

### Failure Interpretation

- `orbit_invariance_gap ≈ 0` or CI includes 0 → NFT already implicitly orbit-invariant → EXPLORE path
- Does NOT invalidate H-M3 performance hypothesis (changes causal mechanism only)
- Action on FAIL: document finding, route to EXPLORE, continue to H-M2/H-M3

---

## 9. File Structure

```
docs/youra_research/h-m1/
├── 03_prd.md                  (this file)
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 03_tasks.yaml
├── results.json               (Phase 4 output)
├── figures/
│   ├── fig_gate_metrics.png
│   ├── fig_sim_distributions.png
│   ├── fig_per_model_scatter.png
│   ├── fig_embedding_pca.png
│   └── fig_similarity_heatmap.png
└── code/
    ├── main.py
    ├── data_loader.py           (reuse/extend from H-E1)
    ├── orbit_construction.py    (reuse from H-E1)
    ├── embedding_extractor.py
    ├── similarity_analysis.py
    ├── statistics.py
    └── visualization.py
```

---

## 10. Phase 2C Completeness Verification

| Phase 2C Item | Captured in PRD |
|---------------|-----------------|
| Dataset: Schürholt MNIST zoo (full, ~50k) | Section 4.1, FR-1 |
| NFT Condition A checkpoint (H-E1 reuse) | Section 4.2, FR-0 |
| Oracle scaling orbit pairs (n=1,000) | FR-2.1 |
| Oracle sign-flip orbit pairs (n=1,000) | FR-2.2 |
| Cross-orbit same-property pairs (decile sampling) | FR-3.3 |
| NFT embedding extraction (batched, eval mode) | FR-3 |
| Within-orbit cosine similarity | FR-4.1 |
| Cross-orbit cosine similarity | FR-4.2 |
| orbit_invariance_gap metric | FR-4.3 |
| Bootstrap 95% CI evaluation | FR-5.2 |
| Gate: within_sim < cross_sim, CI lower > 0 | FR-5.3, Section 8 |
| 5 required figures (gate + 4 diagnostic) | FR-6 |
| Mechanism verification logging | FR-7 |
| Scaling orbit ablation | FR-8 (PRIMARY) |
| Sign-flip orbit ablation | FR-8 (PRIMARY) |
| Fallback NFT training (if no checkpoint) | FR-0.3 |

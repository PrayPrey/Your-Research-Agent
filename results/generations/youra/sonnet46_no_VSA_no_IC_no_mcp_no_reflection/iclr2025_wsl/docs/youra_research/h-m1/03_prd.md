# Product Requirements Document: h-m1

**Hypothesis:** h-m1 (MECHANISM)
**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

---

## 1. Executive Summary

H-M1 is an **analysis-only** experiment that tests whether permutation-equivariant weight encoders achieve higher Spearman correlation with generalization gap than a position-indexed FlatMLP baseline. All encoder checkpoints were trained in H-E1; this hypothesis reloads those checkpoints, runs inference on the held-out test split, and computes Spearman_r(gap) per encoder. No new training is required unless NFT or GNN checkpoints are missing from H-E1.

**Gate (MUST_WORK):** ≥1 equivariant encoder (DWSNet, NFT, or GNN) achieves higher Spearman_r(gap) than FlatMLP (r = 0.5567) on the test split.

---

## 2. Problem Statement

### Background
H-E1 established that generalization gap is a learnable signal in weight tensors (FlatMLP r=0.5567, DWSNet r=0.5104). H-M1 investigates the *mechanism*: does permutation-equivariant encoding of weight tensors improve generalization gap prediction over position-indexed encoding?

### Hypothesis Under Test
Under convergence-regime conditions, prediction error is **lower** for globally distributed statistics encoders (DWSNet, NFT, GNN) than for locally position-indexed encoders (FlatMLP), because overfitting signal is spread across the full weight tensor — no single neuron or layer localizes it.

### Research Gap
FlatMLP appears permutation-invariant at inference (sorted weights), but is NOT equivariant during training — spurious position-indexed features are learnable. This experiment empirically tests whether that theoretical distinction translates to measurable predictive improvement.

---

## 3. Scope and Constraints

### In Scope
- Load H-E1 trained checkpoints for 4 encoders (FlatMLP, DWSNet, NFT, GNN)
- Run inference on Unterthiner zoo test split (N≈1000)
- Compute Spearman_r(gap) per encoder with 95% bootstrap CI
- Compute Δ_gap = mean(equivariant Spearman) − FlatMLP Spearman
- Conditional re-training of NFT/GNN if H-E1 checkpoints missing (using identical H-E1 protocol)
- Generate visualization figures: bar chart, scatter plots, encoder ranking comparison, Δ_gap plot, gap distribution

### Out of Scope
- New architecture design
- New hyperparameter search
- Modifying H-E1 checkpoints
- Cross-zoo validation (reserved for H-M4+)

### Constraints
- Must reuse H-E1 split (identical 80/10/10, same seed) — no re-splitting
- FlatMLP baseline fixed at r=0.5567 (H-E1 confirmed)
- 50-trial budget per encoder — pre-specified and locked (only for re-training fallback)

---

## 4. Data Specification

### Primary Dataset

**Name:** Unterthiner CIFAR-10 CNN Model Zoo
**Source:** Unterthiner et al. 2020 (arxiv 2002.11448)
**N:** ~10,000 trained CNN models
**D:** 33,890 weight parameters per model (flattened, sorted)
**Target:** `generalization_gap = train_acc − test_acc`
**Split:** 80/10/10 (train/val/test) — IDENTICAL to H-E1; must NOT re-split
**Download:** Manual — not auto-downloadable; requires paper-release URL

**Manual Download Task required:** YES

**Expected path:** `./data/unterthiner_zoo/`

**Loading code:**
```python
weights, gap_labels = load_zoo_h1(
    zoo_path="./data/unterthiner_zoo/",
    target="generalization_gap",
    split="test"
)
```

### Checkpoints (from H-E1)

| Encoder | Checkpoint Path | H-E1 Spearman |
|---------|----------------|---------------|
| FlatMLP | `h-e1/checkpoints/flat_mlp_best.pt` | 0.5567 |
| DWSNet | `h-e1/checkpoints/dws_net_best.pt` | 0.5104 |
| NFT | `h-e1/checkpoints/nft_best.pt` | unknown (may be missing) |
| GNN | `h-e1/checkpoints/gnn_best.pt` | unknown (may be missing) |

**Fallback:** If NFT or GNN checkpoints missing, re-train using H-E1 protocol with official implementations.

---

## 5. Functional Requirements

### FR-1: Data Pipeline (reuse H-E1)
- Load Unterthiner zoo from `./data/unterthiner_zoo/`
- Apply SAME 80/10/10 split and seed as H-E1
- Extract test split (N≈1000 models)
- Compute gap labels: `gap = train_acc − test_acc`

### FR-2: FlatMLP Encoder (baseline, position-indexed)
- Load checkpoint `h-e1/checkpoints/flat_mlp_best.pt`
- Architecture: Linear(33890,512) → ReLU → Linear(512,512) → ReLU → Linear(512,1)
- Input: flattened, sorted weight vector (D=33890)
- Output: scalar gap prediction

### FR-3: DWSNet Encoder (equivariant)
- Load checkpoint `h-e1/checkpoints/dws_net_best.pt`
- Architecture: DWSLayer stack (row+column within-layer equivariance) + orbit-average pooling + linear head
- If checkpoint missing: re-train with H-E1 protocol (AdamW lr=1e-3, batch=64, 100 epochs, MSE)

### FR-4: NFT Encoder (equivariant)
- Load checkpoint `h-e1/checkpoints/nft_best.pt`
- Architecture: Neural Functional Transformers with cross-layer attention
- If checkpoint missing: re-train with H-E1 protocol (official Zhou et al. NeurIPS 2023 code)

### FR-5: GNN Encoder (equivariant)
- Load checkpoint `h-e1/checkpoints/gnn_best.pt`
- Architecture: GNN on layer graph; edges = inter-layer weight connections
- If checkpoint missing: re-train with H-E1 protocol (official mkofinas/neural-graphs code)

### FR-6: Analysis Engine
- For each encoder: run inference on test split, compute Spearman_r(predicted_gap, true_gap)
- Compute bootstrap 95% CI (1000 resamples, top-5 checkpoint configurations)
- Compute Δ_gap = mean(equivariant Spearman) − FlatMLP Spearman
- Gate check: gate_passed = any(equivariant_r > 0.5567)

### FR-7: Visualization
- Figure 1 (mandatory): Bar chart of Spearman_r(gap) per encoder vs FlatMLP baseline (r=0.5567 dashed line)
- Figure 2: Scatter plots (2×2 grid) — predicted gap vs. true gap per encoder
- Figure 3: Side-by-side encoder ranking: gap target vs. test_acc target Spearman
- Figure 4: Δ_gap arrow plot (equivariant improvement over FlatMLP)
- Figure 5: Histogram of true gap values in test split (sanity check)
- All figures saved to `h-m1/figures/`

### FR-8: Results Logging
- Print per-encoder: `[H-M1] {encoder}: Spearman(gap)={r:.4f} vs FlatMLP=0.5567`
- Print: `[H-M1] Δ_gap={delta_gap:.4f}, gate={'PASS' if gate_passed else 'FAIL'}`
- Sanity assertion: `results["flat_mlp"] > 0.4` (H-E1 consistency check)

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (seed=1) for all stochastic operations
- Identical split to H-E1 — must load from H-E1 split indices or apply same seed+ratio
- All results logged to `h-m1/04_results.json`

### NFR-2: Compute Budget
- Analysis phase: GPU-hours < 0.5 (inference only on N≈1000 test samples)
- Fallback re-training: ~1-2 GPU-hours per missing encoder (NFT or GNN)
- Total budget: ≤ 5 GPU-hours including all fallback scenarios

### NFR-3: Code Quality
- All encoder classes importable from `h_m1/encoders/`
- Single entry-point script: `h_m1/run_analysis.py`
- Unit tests: `tests/test_h_m1_analysis.py`

### NFR-4: Figures
- Resolution: 300 DPI, PNG format
- Style: consistent with paper-quality figures (matplotlib, seaborn)
- Saved before results summary printed

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.12
numpy>=1.22
scipy>=1.9
matplotlib>=3.5
seaborn>=0.12
pandas>=1.4
pyyaml>=6.0
tqdm>=4.64
```

### 7.2 External Repositories (reference)
- AvivNavon/DWSNets — DWSNet official implementation
- mkofinas/neural-graphs — GNN encoder official implementation
- Zhou et al. NeurIPS 2023 NFT — official NFT code (link from paper)

### 7.3 H-E1 Artifacts (required)
- `h-e1/checkpoints/flat_mlp_best.pt`
- `h-e1/checkpoints/dws_net_best.pt`
- `h-e1/checkpoints/nft_best.pt` (may be missing — fallback to re-train)
- `h-e1/checkpoints/gnn_best.pt` (may be missing — fallback to re-train)
- H-E1 data pipeline code (to reproduce exact split)

---

## 8. Success Criteria

| Criterion | Target | Source |
|-----------|--------|--------|
| All checkpoints loaded without error | 4/4 (or re-trained fallback) | FR-2..5 |
| Inference runs on test split | N≈1000 samples | FR-6 |
| Gate PASS | ≥1 equivariant r > 0.5567 | Gate definition |
| Spearman CI reported | 95% bootstrap per encoder | FR-6 |
| Figures generated | 5 figures saved to h-m1/figures/ | FR-7 |
| Results logged | JSON + print statements | FR-8 |

---

## 9. Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| NFT/GNN checkpoints missing from H-E1 | HIGH | Fallback re-training with official code; ~1-2 GPU-h per encoder |
| NFT hyperparam sensitivity causes poor results | MEDIUM | Report top-5 sensitivity analysis; use val-best checkpoint |
| DWSNet stays below FlatMLP (r=0.5104 in H-E1) | MEDIUM | NFT or GNN needed to pass gate; note partial H-E1 evidence |
| Split mismatch (different seed than H-E1) | LOW | Load H-E1 split indices directly or assert split stats match |

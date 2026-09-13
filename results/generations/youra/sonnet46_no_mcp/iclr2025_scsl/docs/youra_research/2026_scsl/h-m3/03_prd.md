# Product Requirements Document: H-M3
# Transition Epoch t* Reproducibility Analysis

**Hypothesis ID:** H-M3
**Type:** MECHANISM (Post-hoc Analysis)
**Gate:** MUST_WORK
**Date:** 2026-05-04
**Phase:** 3 - Implementation Planning
**Tier:** FULL (max 30 tasks)

---

## 1. Executive Summary

H-M3 characterizes the transition epoch t* — the first checkpoint where the temporal gap delta(t) = spurious_probe_acc(t) - core_probe_acc(t) closes below a threshold — as a reproducible structural property of SGD optimization. The experiment re-analyzes delta(t) arrays already produced by H-E1 (no new model training), applies an operational t* definition, and verifies that std(t*) < 10 epochs across ≥3 random seeds on Waterbirds.

**Key Insight:** H-M3 is a pure post-hoc statistical analysis of pre-computed numpy arrays from H-E1. No new training or model architecture is required. The primary deliverable is the `TransitionEpochAnalyzer` class and statistical validation pipeline.

---

## 2. Problem Statement

H-E1 established that the temporal gap delta(t) > 0 exists during early SGD training (MUST_WORK PASS, p=0.0219, t*≈4.0 epochs). However, t* was reported only as a point estimate. H-M3 asks: *Is t* a reproducible structural property (low std across seeds) or a random training artifact (high std)?*

This distinction is critical because:
- H-M4 uses t* as an intervention point for DFR timing experiments
- The entire mechanistic framework requires t* to be reliably identifiable
- Prior work (DFR, JTT, GroupDRO) implicitly assumes post-hoc backbone readiness but never formalizes t*

**MUST_WORK Gate:** std(t*) < 10 epochs across ≥3 seeds on Waterbirds.

---

## 3. Functional Requirements

### FR-1: Data Loading Module
- **FR-1.1:** Load H-E1 delta(t) arrays from `h-e1/results/` directory (delta_t_seed{N}.npy or equivalent format)
- **FR-1.2:** Support fallback: if H-E1 numpy arrays unavailable, regenerate from H-E1 checkpoints using ResNet-50 probe evaluation
- **FR-1.3:** Validate loaded arrays: must have ≥15 checkpoints (30-epoch PoC at 2-epoch intervals), ≥3 seeds
- **FR-1.4:** Log array shapes and seed count on load

### FR-2: t* Detection (TransitionEpochAnalyzer)
- **FR-2.1:** Implement `find_t_star(delta_curve, threshold=0.02, n_consecutive=3)` — returns first checkpoint index where delta(t) < threshold for n_consecutive consecutive checkpoints
- **FR-2.2:** Return None if no qualifying window found in the curve
- **FR-2.3:** Convert checkpoint index to epoch number using `checkpoint_interval=2`
- **FR-2.4:** Implement adaptive threshold fallback: if t*=None, retry with threshold = 0.5 × min(delta_curve)
- **FR-2.5:** Implement `compute_gap_area(delta_curve)` — returns sum(max(delta(t), 0)) across all checkpoints

### FR-3: Statistical Variance Analysis
- **FR-3.1:** Compute mean(t*) and std(t*, ddof=1) across all seeds that produce valid t* values
- **FR-3.2:** Compute 95% bootstrap CI for std(t*) using n_resamples=10000
- **FR-3.3:** Compute mean gap area and 95% bootstrap CI for gap area A
- **FR-3.4:** Report: t* per seed, mean_t*, std_t*, ci_95_std, gate_passed (std_t* < 10.0)
- **FR-3.5:** Handle edge case: if fewer than 3 seeds produce valid t*, flag as insufficient data

### FR-4: Gate Evaluation
- **FR-4.1:** Evaluate MUST_WORK gate: std(t*) < 10 epochs across ≥3 seeds
- **FR-4.2:** Evaluate directional criterion: all seeds produce identifiable t* (t* ≠ None)
- **FR-4.3:** Evaluate secondary criterion: mean gap area A > 0 with 95% CI excluding zero
- **FR-4.4:** Report partial-pass if std(t*) ∈ [10, 20]: document as limitation, argue for full 300-epoch training

### FR-5: Mechanism Verification
- **FR-5.1:** Implement `verify_mechanism_activated(results)` — checks all 4 indicators:
  - all_seeds_found_t_star
  - std_below_threshold (std_t* < 10)
  - gap_area_positive (mean_gap_area > 0)
  - curves_loaded (≥3 seeds)
- **FR-5.2:** Log mechanism activation status with per-indicator breakdown

### FR-6: Visualization
- **FR-6.1:** Generate mandatory gate metrics plot: bar chart of std(t*) vs 10-epoch threshold, with individual seed t* values as scatter points
- **FR-6.2:** Generate delta(t) timeline: all 3 seeds on same axes with vertical lines at each seed's t*
- **FR-6.3:** Generate gap area box plot with 95% bootstrap CI band
- **FR-6.4:** Save all figures to `h-m3/figures/` directory
- **FR-6.5:** If CelebA available: generate cross-dataset std(t*) comparison bar chart

### FR-7: Results Export
- **FR-7.1:** Save JSON results: t_star_per_seed, mean_t_star, std_t_star, ci_95_std, gap_areas, gate_passed
- **FR-7.2:** Save CSV: per-seed delta(t) curves for reproducibility
- **FR-7.3:** Print gate evaluation summary to stdout with clear PASS/FAIL/PARTIAL-PASS indicator

---

## 4. Data Specification

### Primary Dataset: Waterbirds (via H-E1 outputs — no download needed)

**H-E1 Delta(t) Arrays (PRIMARY INPUT):**
- Source: `h-e1/results/delta_t_seed{N}.npy` (or equivalent H-E1 output format)
- Format: numpy array, shape (15,) per seed — 15 checkpoints at 2-epoch intervals for 30-epoch PoC
- Seeds: 42, 43, 44 (same as H-E1)
- Values: float, delta(t) = spurious_probe_acc(t) - core_probe_acc(t) at each checkpoint

**Fallback — Regenerate from H-E1 Checkpoints:**
- Waterbirds dataset: cached at `/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_scsl/docs/youra_research/20260504_scsl/.data_cache/datasets/waterbirds`
- H-E1 checkpoints: `h-e1/checkpoints/checkpoint_epoch{e}_seed{s}.pt` (if saved)
- Validation split: 1,199 samples (same split used in H-E1)
- ResNet-50 pretrained on ImageNet (torchvision)

**Replication Dataset: CelebA**
- Attempt replication; if GDrive network restriction persists (as in H-M2), scope to Waterbirds only
- CelebA failure = acceptable; Waterbirds result sufficient for MUST_WORK gate

---

## 5. Model Specification

**No new model training required.** H-M3 reuses H-E1 outputs.

**For fallback regeneration only:**
- Architecture: ResNet-50 (torchvision), pretrained on ImageNet
- Classifier head: Linear(2048, 2)
- Training: ERM on Waterbirds, SGD(lr=1e-3, momentum=0.9, wd=1e-4), 30 epochs
- Probe: L2-regularized logistic regression (scikit-learn), fit on validation split features

---

## 6. Evaluation Metrics

| Metric | Definition | Gate Threshold |
|--------|-----------|----------------|
| std(t*) | Std dev of transition epochs across seeds | < 10 epochs (MUST_WORK) |
| mean(t*) | Mean transition epoch | Point estimate (informational) |
| Gap area A | sum(max(delta(t), 0)) per seed | > 0 with 95% CI > 0 |
| t* detection rate | Fraction of seeds with valid t* | 3/3 (all seeds) |
| t* relative phase | t* / total_epochs | Consistent across datasets |

**Expected Results (from H-E1):**
- std(t*) ≈ 1–3 epochs (well below 10-epoch threshold)
- mean(t*) ≈ 4.0 epochs (consistent with H-E1 point estimate)
- gap_area ≈ 0.040 per seed
- High confidence gate will pass: H-E1 t_stat=4.619 (strong signal), consistent across all 3 seeds

---

## 7. Dependencies

### 7.1 Python Packages
```
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=0.24.0
torch>=1.9.0          # Only needed for fallback checkpoint loading
torchvision>=0.10.0   # Only needed for fallback ResNet-50 loading
pyyaml>=5.4.0
```

### 7.2 External Repositories (Reference Only)
- `kohpangwei/group_DRO`: Waterbirds dataset loader (used in H-E1)
- `PolinaKirichenko/dfr`: Checkpoint-based probe evaluation patterns
- `izmailovpavel/spurious_feature_learning`: Reproducibility evidence

### 7.3 Internal Dependencies (CRITICAL)
- **H-E1 outputs required:** `h-e1/results/delta_t_seed{N}.npy` (primary)
- **OR H-E1 checkpoints:** `h-e1/checkpoints/` (fallback)
- Waterbirds data cache: `.data_cache/datasets/waterbirds` (fallback only)

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Total runtime: <5 minutes (analysis only, no training)
- If fallback regeneration needed: <30 minutes (probe evaluation on 3 seeds)

### NFR-2: Reproducibility
- All random operations seeded (numpy.random.seed, torch.manual_seed)
- Bootstrap CI uses fixed seed for reproducibility
- Results saved to JSON for verification

### NFR-3: Robustness
- Graceful handling of t*=None (adaptive threshold fallback)
- Graceful handling of missing H-E1 arrays (fallback to checkpoint regeneration)
- Clear error messages for missing dependencies

### NFR-4: GPU
- Fallback mode only: single GPU (CUDA_VISIBLE_DEVICES=<lowest-memory GPU>)
- Primary mode (array analysis): CPU only

---

## 9. Success Criteria (MUST_WORK Gate)

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| std(t*) < 10 epochs | Across 3 seeds | PRIMARY (gate) |
| All seeds find t* | t* ≠ None for all | DIRECTIONAL |
| Gap area A > 0 | 95% CI excludes zero | SECONDARY |

**PARTIAL-PASS conditions:**
- std(t*) ∈ [10, 20] epochs: document limitation; argue for full 300-epoch training
- t*=None for 1 seed: use adaptive threshold; report as limitation

**FAIL condition:**
- std(t*) ≥ 20 epochs: pivot to gap area A as primary metric; inform H-M4 design

---

## 10. Out of Scope

- New model training (H-M3 is analysis-only)
- New dataset preprocessing (reuses H-E1 cached data)
- Comparison with DFR/JTT performance (belongs to H-M4)
- CelebA replication if network restricted (acceptable limitation)
- Full 300-epoch training (PoC uses 30 epochs from H-E1)

---

## 11. Continuation Context

**Building on:**
- H-E1: delta(t) arrays, t*≈4.0 epochs, gap_area=0.040, p=0.0219 (MUST_WORK PASS)
- H-M1: GDR=6.977 structural gradient bias (supports low-variance t* claim)
- H-M2: 3/3 complexity metrics confirm spurious simplicity (structural, not random)

**Enabling:**
- H-M4: DFR timing experiment requires reliable t* as intervention point

---

*Generated by Phase 3 Workflow (no-MCP variant)*
*PRD based on Phase 2C experiment brief: h-m3/02c_experiment_brief.md*
*Date: 2026-05-04*

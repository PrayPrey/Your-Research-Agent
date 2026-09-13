# Product Requirements Document: H-M2

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM
**generated_at:** 2026-03-16T15:00:00+00:00
**source:** Phase 2C experiment brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for **H-M2** — a MECHANISM experiment that extends H-M1's causal mechanism result by directly comparing engineering compensation strategies (permutation augmentation, oracle canonicalization) against architectural equivariance (NFT-base) to confirm that architectural equivariance is a **necessary** (not merely convenient) inductive bias.

**Core Question:** Do permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Δρ compared to flat-MLP baseline, yet still fail to match NFT-base performance, confirming architectural equivariance is irreplaceable?

**Gate:** SHOULD_WORK — strict three-way ranking: NFT-base < flat-MLP+canon < flat-MLP+aug < flat-MLP. If gate fails, the pipeline narrows claims but continues to H-M3.

**Extends:** H-M1 (COMPLETED — PASS; nft_delta_rho=4.71e-07, delta_R2=0.228, flat-MLP+aug Δρ=0.2239)

**Key Design Principle:** H-M2 is a continuation experiment — all 3 focal encoders were trained in H-M1. H-M2 reuses those checkpoints directly; only the SHOULD_WORK gate evaluator and H-M2-specific analysis/visualization are new.

---

## 2. Problem Statement

H-M1 established that NFT's equivariant attention causally explains permutation robustness (ΔR²=0.228). H-M2 addresses the **necessity** question: can engineering compensations (augmentation, canonicalization) substitute for architectural equivariance?

H-M1 already showed partial results:
- flat-MLP+aug Δρ = 0.2239 at s=1.0 (partial reduction, still > 0.05)
- flat-MLP+canon Δρ ≈ 0.0 at s=1.0 (L2 oracle, potentially degenerate)
- NFT-base Δρ = 4.71e-07 (near-zero, architectural robustness)

**H-M2 focus:** Evaluate whether the oracle canonicalization is a realistic upper bound (Δρ > 0.03 under proper evaluation) or a degenerate solution (Δρ ≈ 0 trivially). Confirm strict three-way ranking under the SHOULD_WORK gate criteria.

---

## 3. Hypothesis & Success Criteria

### Hypothesis Statement

Permutation augmentation (flat-MLP+aug) and oracle canonicalization (flat-MLP+canon) reduce Δρ compared to flat-MLP baseline but do not match NFT-base performance, confirming that architectural equivariance provides a necessary (not merely convenient) inductive bias for permutation-robust property prediction.

### Gate Condition (SHOULD_WORK)

| Criterion | Threshold | Measurement | Expected (from H-M1) |
|-----------|-----------|-------------|----------------------|
| Aug partial compensation | Δρ(aug) > 0.05 | Mean Δρ at s=1.0, flat-MLP+aug | ~0.22 (H-M1 confirmed) |
| Canon suboptimal | Δρ(canon) > 0.03 | Mean Δρ at s=1.0, flat-MLP+canon | ~0.03–0.15 (re-evaluate oracle) |
| NFT architectural superiority | Δρ(NFT) < 0.02 | Mean Δρ at s=1.0, NFT-base | ~4.7e-07 (H-M1 confirmed) |
| Three-way ranking | NFT < canon < aug < flat-MLP | Strict rank ordering at s=1.0 | Expected to hold |
| Statistical significance (aug vs NFT) | p < 0.05 (Holm) | Paired bootstrap n=10,000 | Strong (H-M1 p≈0) |
| Statistical significance (canon vs NFT) | p < 0.05 (Holm) | Paired bootstrap n=10,000 | Expected to hold |

**PoC Pass (sufficient for SHOULD_WORK):**
1. Code runs without error (loads H-M1 checkpoints successfully)
2. NFT-base Δρ < 0.02 at s=1.0 (reconfirm from H-M1)
3. Three-way ranking confirmed: NFT < canon < aug < flat-MLP
4. flat-MLP+aug Δρ > 0.05 (augmentation insufficient for full compensation)

**FAIL/Narrowing Condition:** If aug Δρ ≤ 0.05 OR canon Δρ ≤ 0.03 OR ranking violated → SHOULD_WORK gate fails → narrow claim to "NFT competitive with oracle-canon; augmentation insufficient." Pipeline continues to H-M3.

---

## 4. Data Specification

### 4.1 Primary Dataset

**Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Source:** Unterthiner et al. 2020, "Predicting Neural Network Accuracy from Weights"
**Type:** standard (real, established — NOT synthetic)
**Status:** ✅ CACHED — do NOT re-download

**Cache Path:**
```
.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl
```

**Loading Code:**
```python
import pickle

cache_path = ".data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl"
with open(cache_path, 'rb') as f:
    zoo_data = pickle.load(f)
# zoo_data: dict with keys:
#   'weights': list of flat weight vectors (each shape: [D])
#   'gen_gap': float array of generalization gaps (targets)
#   'layer_fan_ins': list of fan-in sizes per layer (for NFT input format)
```

**Splits:**
- Train: ~800 FC-MLP models (2-4 layer, MNIST)
- Test: ~200 FC-MLP models (held-out split, same as H-M1)
- Total: ~1,000 models (statistically sufficient: >> 500 minimum)

**Important:** Use IDENTICAL train/test split as H-M1 (same random seed for split = 42) for comparable Δρ values.

### 4.2 Permutation Stress Protocol

**Severity Levels:** s ∈ {0.0, 0.25, 0.5, 1.0}
**Method:** Random neuron permutation applied at evaluation time to test-set weight vectors
**Bootstrap:** n=10,000 samples, Holm correction, α=0.05
**Minimum models per condition:** ~200 test models × 4 severity levels = 800 evaluation conditions

### 4.3 Checkpoint Reuse (CRITICAL)

**All model checkpoints are pre-trained in H-M1. Do NOT retrain unless checkpoint loading fails.**

| Encoder | Checkpoint Path | Seeds |
|---------|----------------|-------|
| flat-MLP | `h-m1/code/checkpoints/flat-MLP_seed{42,123,456}.pt` | 3 |
| flat-MLP+aug | `h-m1/code/checkpoints/flat-MLPplusaug_seed{42,123,456}.pt` | 3 |
| flat-MLP+canon | `h-m1/code/checkpoints/flat-MLPpluscanon_seed{42,123,456}.pt` | 3 |
| NFT-base | `h-m1/code/checkpoints/NFT-base_seed{42,123,456}.pt` | 3 |

**Checkpoint Loading Code:**
```python
import sys
sys.path.insert(0, 'h-m1/code/src')
from models import build_encoder

checkpoint = torch.load(ckpt_path, map_location=device)
model = build_encoder(encoder_name, flat_input_dim, layer_fan_ins)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()
```

**Fallback (if checkpoint loading fails):** Retrain using H-M1 identical config (Adam lr=1e-3, batch=64, epochs=50, StepLR(20, 0.5)).

---

## 5. Functional Requirements

### FR-1: Data Setup (Checkpoint Verification)

**Priority:** P0 — Blocker

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-1.1 | Load zoo_enriched.pkl from cache path | File exists, loads without error, contains ~1,000 model records |
| FR-1.2 | Verify H-M1 checkpoints exist for 4 encoder types × 3 seeds = 12 checkpoint files | All 12 `.pt` files loadable with `torch.load()` |
| FR-1.3 | Verify checkpoint compatibility with model architecture | `model.load_state_dict(checkpoint['model_state_dict'])` succeeds for all 12 |
| FR-1.4 | Apply identical train/test split as H-M1 (seed=42) | Split reproducible; test set ≥ 150 models |

### FR-2: Environment Setup

**Priority:** P0 — Blocker

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-2.1 | Import H-M1 source modules: `models.py`, `evaluate.py`, `data.py` | `from h_m1_src.models import build_encoder` succeeds |
| FR-2.2 | Configure single GPU execution | `CUDA_VISIBLE_DEVICES` set; `torch.cuda.is_available()` returns True |
| FR-2.3 | Install/verify dependencies: PyTorch, scipy, numpy, pandas, matplotlib | All `import` statements succeed |
| FR-2.4 | Set output directories: `h-m2/figures/`, `h-m2/results/` | Directories created |

### FR-3: H-M2 Gate Evaluator (SHOULD_WORK)

**Priority:** P1 — Core

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-3.1 | Implement `evaluate_gate_hm2(eval_df)` function | Returns dict with keys: `aug_partial`, `canon_partial`, `nft_superior`, `ranking`, `passed`, `mean_dr_by_encoder` |
| FR-3.2 | Compute mean Δρ at s=1.0 for each of 4 encoders (3-seed average) | Values within ±0.05 of H-M1 results for confirmed encoders |
| FR-3.3 | Evaluate SHOULD_WORK conditions: aug>0.05, canon>0.03, NFT<0.02, strict ranking | `passed` = True iff all 4 conditions met |
| FR-3.4 | Checkpoint consistency check: loaded model Δρ within ±0.01 of H-M1 reported values | NFT-base Δρ ≤ 0.02+0.01, flat-MLP+aug Δρ ≥ 0.22-0.01 |

### FR-4: Bootstrap Statistical Tests

**Priority:** P1 — Core

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-4.1 | Paired bootstrap (n=10,000) for flat-MLP+aug vs NFT-base Δρ | p-value computed; expected p < 0.05 |
| FR-4.2 | Paired bootstrap (n=10,000) for flat-MLP+canon vs NFT-base Δρ | p-value computed; expected p < 0.05 |
| FR-4.3 | Holm-Bonferroni correction for all pairwise comparisons | Corrected p-values ≤ raw p-values |
| FR-4.4 | Cohen's d effect size for each pairwise comparison | Effect sizes computed and reported |
| FR-4.5 | 95% confidence intervals for all Δρ estimates | CI bounds reported in output DataFrame |

### FR-5: Evaluation Across Severity Levels

**Priority:** P1 — Core

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-5.1 | Evaluate all 4 encoders × 4 severity levels × 3 seeds = 48 (encoder, severity, seed) combinations | DataFrame with 48+ rows, columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value] |
| FR-5.2 | Reuse `evaluate_all_encoders()` from H-M1 codebase | Function call succeeds; returns expected DataFrame structure |
| FR-5.3 | Δρ computed as ρ(s=0) − ρ(s=severity) for each (encoder, seed) pair | Signed difference: positive = degradation |
| FR-5.4 | Encoder filter: include flat-MLP, flat-MLP+aug, flat-MLP+canon, NFT-base only | Oracle-canon excluded from H-M2 analysis |

### FR-6: Visualization

**Priority:** P2 — Required

| ID | Requirement | Figure Output |
|----|-------------|--------------|
| FR-6.1 | **[MANDATORY]** Gate Metrics Comparison: bar chart of mean Δρ at s=1.0 for 4 encoders with 95% CI error bars and threshold lines (0.02, 0.03, 0.05) | `h-m2/figures/gate_metrics_comparison.png` |
| FR-6.2 | Δρ Heatmap: 4-encoder × 4-severity grid of mean Δρ values (colormap: blue=low=robust, red=high=degraded) | `h-m2/figures/delta_rho_heatmap.png` |
| FR-6.3 | ρ(s) Degradation Curves: line plot of mean Spearman ρ vs severity for 4 encoders with seed-level error bands | `h-m2/figures/rho_degradation_curves.png` |
| FR-6.4 | Three-way Ranking Scatter: scatter plot of per-seed Δρ at s=1.0 for 4 encoders with threshold zones | `h-m2/figures/threeway_ranking_scatter.png` |
| FR-6.5 | Bootstrap Distribution Overlays: overlapping bootstrap Δρ distributions for aug vs NFT-base and canon vs NFT-base | `h-m2/figures/bootstrap_distributions.png` |

### FR-7: Results Reporting

**Priority:** P1 — Core

| ID | Requirement | Acceptance Criterion |
|----|-------------|---------------------|
| FR-7.1 | Generate summary results dict with all gate metrics | Dict with at minimum: `aug_mean_dr`, `canon_mean_dr`, `nft_mean_dr`, `flat_mlp_mean_dr`, `ranking`, `gate_passed` |
| FR-7.2 | Save results to `h-m2/results/hm2_results.json` | Valid JSON loadable with `json.load()` |
| FR-7.3 | Save full evaluation DataFrame to `h-m2/results/hm2_eval_df.csv` | CSV with columns [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value] |
| FR-7.4 | Print gate evaluation report to stdout | Report includes per-encoder Δρ, threshold comparisons, `SHOULD_WORK: PASS/FAIL` |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| NFR | Requirement |
|-----|-------------|
| NFR-1 | Inference-only evaluation (no training): total runtime ≤ 30 minutes on single GPU |
| NFR-2 | Bootstrap computation (n=10,000 × 4 comparisons): ≤ 10 minutes on CPU |
| NFR-3 | GPU memory: ≤ 8GB (NFT encoder batch size 64 on test set ~200 models) |
| NFR-4 | Single GPU only — set `CUDA_VISIBLE_DEVICES` to lowest-utilization GPU |

### 6.2 Reproducibility

| NFR | Requirement |
|-----|-------------|
| NFR-5 | All random seeds explicitly set: `torch.manual_seed(42)`, `np.random.seed(42)` |
| NFR-6 | Checkpoint loading deterministic: same checkpoint → same predictions |
| NFR-7 | Bootstrap seed fixed: `np.random.seed(42)` for all bootstrap samples |

### 6.3 Code Quality

| NFR | Requirement |
|-----|-------------|
| NFR-8 | Reuse H-M1 codebase directly (import from `h-m1/code/src/`) — do NOT copy/modify H-M1 code |
| NFR-9 | H-M2 code placed in `h-m2/code/` with only new functionality: gate evaluator + main experiment script |
| NFR-10 | Error handling for checkpoint loading failure: fallback to retraining with same config |

---

## 7. Dependencies

### 7.1 External Prerequisite

| Dependency | Source | Status |
|------------|--------|--------|
| H-M1 checkpoints (12 files) | `h-m1/code/checkpoints/` | ✅ Available (Serena confirmed) |
| H-M1 source code (`models.py`, `evaluate.py`) | `h-m1/code/src/` | ✅ Available |
| Dataset cache (`zoo_enriched.pkl`) | `.data_cache/datasets/unterthiner_mnist_zoo/` | ✅ Available |

### 7.2 Software Dependencies

```
torch>=1.12.0
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
pyyaml>=5.4.0
scikit-learn>=0.24.0 (for MSE validation)
```

### 7.3 Hypothesis Dependencies

| Prerequisite | Type | Gate | Status |
|-------------|------|------|--------|
| H-E1 | MUST_WORK | ✅ PASS (flat_mlp_delta_rho=0.1595, nft_delta_rho=4.09e-6) | COMPLETED |
| H-M1 | MUST_WORK | ✅ PASS (nft_delta_rho=4.71e-07, delta_R2=0.228) | COMPLETED |

---

## 8. Implementation Constraints

| Constraint | Rationale |
|-----------|-----------|
| Must reuse H-M1 checkpoints (not retrain) | Controlled comparison requires identical training conditions |
| Must use IDENTICAL test split as H-M1 (seed=42) | Comparable Δρ values across hypotheses |
| Must NOT modify H-M1 source code | Upstream hypothesis integrity |
| Must evaluate flat-MLP+canon as-is from H-M1 (L2-norm oracle) | H-M2 tests whether L2-norm oracle is degenerate |
| Single GPU only | Resource constraint per pipeline config |
| Must include all 5 visualization figures | Required for paper Figure 3 (three-way ranking) |

---

## 9. Out of Scope

- Retraining any encoder from scratch (unless checkpoint load fails)
- Cross-pipeline transfer evaluation (scoped to H-M4)
- CIFAR zoo evaluation (scoped to H-M4)
- New encoder architecture variants
- Hyperparameter tuning for any encoder

---

## 10. Acceptance Criteria Summary

| Criterion | Pass Condition |
|-----------|----------------|
| Checkpoint loading | All 12 checkpoints load without error |
| Consistency check | NFT-base Δρ ≤ 0.03 (within H-M1 tolerance), flat-MLP+aug Δρ ≥ 0.21 |
| Gate evaluation | `evaluate_gate_hm2()` runs and returns valid `passed` boolean |
| Statistical tests | Bootstrap p-values computed for 2 pairwise comparisons with Holm correction |
| Visualization | All 5 figures generated and saved to `h-m2/figures/` |
| Results saved | `hm2_results.json` and `hm2_eval_df.csv` exist in `h-m2/results/` |
| Gate outcome | SHOULD_WORK: PASS (ranking holds) or documented narrow claim if FAIL |

---

*Generated by Phase 3 PRD Step (inline execution — BMAD PRD workflow not installed)*
*Source: Phase 2C experiment brief (02c_experiment_brief.md)*
*Hypothesis type: MECHANISM | Gate: SHOULD_WORK | Budget tier: FULL (30 tasks)*

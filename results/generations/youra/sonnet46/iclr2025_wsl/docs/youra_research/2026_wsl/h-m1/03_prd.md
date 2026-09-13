# Product Requirements Document: H-M1

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**hypothesis_id:** h-m1
**hypothesis_type:** MECHANISM
**generated_at:** 2026-03-16T14:20:00+00:00
**source:** Phase 2C experiment brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for **H-M1** — a MECHANISM experiment that extends H-E1's existence result to establish the causal mechanism behind NFT's permutation robustness advantage. H-M1 uses a 6-encoder ablation suite combined with mediation analysis (ΔR²) to confirm that NFT's equivariant attention architecture — not data augmentation or canonicalization — is the causal mechanism explaining the permutation robustness differential.

**Core Question:** Does NFT's equivariant attention mechanism causally explain the permutation robustness differential (ΔR² ≥ 0.10), and does augmentation/canonicalization only partially compensate (flat-MLP+aug Δρ ∈ [0.05, 0.10])?

**Gate:** MUST_WORK — if ΔR² < 0.10, the mechanism claim cannot be made; the pipeline pivots to augmentation-focused design.

**Extends:** H-E1 (COMPLETED — PASS; flat_mlp_delta_rho=0.1595, nft_delta_rho=4.09e-6 confirmed)

---

## 2. Problem Statement

H-E1 established that the permutation sensitivity differential is real and measurable. H-M1 addresses the **why**: is NFT's advantage due to architectural equivariance, or could simpler engineering fixes (augmentation, canonicalization) achieve equivalent robustness?

To isolate the mechanism, H-M1 introduces:
1. A 6-encoder ablation suite spanning the design space from "no fix" (flat-MLP) to "architectural fix" (NFT)
2. Mediation analysis using variance partitioning (ΔR²) to attribute variance uniquely explained by architectural equivariance vs. engineering fixes
3. Multi-seed evaluation (3 seeds) for statistical reliability

**Key design principle:** All 6 encoders use identical dataset, training protocol, and evaluation — only the encoder architecture/augmentation varies (single independent variable).

---

## 3. Hypothesis & Success Criteria

### Hypothesis Statement
Under permutation stress (s=1.0), NFT encoders achieve significantly lower Δρ compared to flat-MLP because NFT's equivariant attention mechanism operates on neuron-level representations invariantly under permutation, as evidenced by mechanism mediation analysis (ΔR² ≥ 0.10 when controlling for equivariance).

### Gate Condition (MUST_WORK)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| NFT-base reconfirmation | Δρ < 0.02 | Δρ at s=1.0 (NFT-base) |
| Mechanism attribution | ΔR² ≥ 0.10 | R²(NFT-base) − R²(flat-MLP+aug) |
| Aug partially compensates | 0.05 < flat-MLP+aug Δρ < 0.10 | Δρ at s=1.0 (flat-MLP+aug) |
| Architecture alone sufficient | NFT-base Δρ < flat-MLP+aug Δρ | Ranking check |
| Statistical significance | p < 0.05 (Holm-corrected, bootstrap n=10,000) | Paired bootstrap on all 15 encoder pairs |

**PoC Pass (sufficient):**
1. Code runs without error for all 6 encoders
2. NFT-base Δρ < 0.02 at s=1.0 (H-E1 reconfirm)
3. ΔR² ≥ 0.10

**FAIL Condition:** ΔR² < 0.10 → mechanism not confirmed → PIVOT to augmentation-focused design

---

## 4. Data Specification

### 4.1 Primary Dataset

**Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Source:** Unterthiner et al. 2020, "Predicting Neural Network Accuracy from Weights"
**Type:** standard (real, established — NOT synthetic)
**Download Method:** Reuse from H-E1 if cached; else download

**Download URL:**
```
https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl
```

**Download Code (reuse from H-E1):**
```python
import urllib.request
import pickle

url = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
urllib.request.urlretrieve(url, "data/unterthiner_mnist_zoo.pkl")

with open("data/unterthiner_mnist_zoo.pkl", "rb") as f:
    zoo_data = pickle.load(f)
# zoo_data: list of dicts with keys 'weights', 'train_acc', 'test_acc'
```

**Dataset Details:**
- Total models: ~1,000 pre-trained FC-MLP networks on MNIST
- Architecture range: 2-layer to 4-layer MLPs, widths 32–512
- Features: weight matrices of each trained FC-MLP (variable dimensions per layer)
- Labels: Generalization gap = training_accuracy − test_accuracy (continuous scalar)
- Splits: standard train/test splits from original release
- **Minimum samples for evaluation:** 500 (full test set required)

**Storage Path:** `data/unterthiner_mnist_zoo.pkl`

**H-E1 cache:** If `h-e1/data/unterthiner_mnist_zoo.pkl` exists, symlink or copy to `h-m1/data/`.

### 4.2 Preprocessing Requirements

| Step | Description | Apply To |
|------|-------------|----------|
| Weight normalization (NFT) | Standardize per neuron row (zero mean, unit std) | NFT variants (E4, E5) |
| Weight normalization (flat-MLP) | Global standardization | flat-MLP variants (E1, E2, E3, E6) |
| Flattening | Concatenate all weight matrices into single vector | flat-MLP variants |
| Layer structure preservation | Pass as sequence of weight matrices | NFT variants |
| Variable-dim handling | Per-layer projection embedding | NFT required |
| Canonicalization (L2-norm) | Sort neurons by L2 norm (descending) per layer | E3 (flat-MLP+canon), E6 (Oracle-canon) |

### 4.3 Permutation Stress Protocol (Inherited from H-E1)

```python
def apply_permutation_stress(weight_matrices, severity=1.0):
    """Apply random permutation to neuron ordering at given severity."""
    stressed = []
    for W in weight_matrices:  # W: (n_neurons, fan_in)
        n = W.shape[0]
        n_perm = int(n * severity)
        if n_perm > 0:
            perm_idx = torch.randperm(n)[:n_perm]
            W_stressed = W.clone()
            W_stressed[perm_idx] = W[perm_idx[torch.randperm(n_perm)]]
        else:
            W_stressed = W
        stressed.append(W_stressed)
    return stressed
```

**Severity levels (evaluation):** s ∈ {0, 0.25, 0.5, 1.0}
**Note:** Evaluation uses ALL severity levels. Training augmentation (E2, E5) applies s=1.0 with 50% probability.

### 4.4 Per-Encoder Augmentation Configuration

```python
ENCODER_CONFIG = {
    "flat-MLP":       {"aug_severity": None, "canon": False},      # E1: baseline
    "flat-MLP+aug":   {"aug_severity": 1.0,  "canon": False},      # E2: 50% prob during training
    "flat-MLP+canon": {"aug_severity": None, "canon": "l2_norm"},  # E3: L2-norm sort always
    "NFT-base":       {"aug_severity": None, "canon": False},      # E4: architecture equivariance
    "NFT+aug":        {"aug_severity": 1.0,  "canon": False},      # E5: architecture + data
    "Oracle-canon":   {"aug_severity": None, "canon": "oracle"},   # E6: ground-truth sort
}
```

---

## 5. Functional Requirements

### FR-1: Dataset Download & Loading
- **FR-1.1:** Download or reuse `small_mnist_networks.pkl` from H-E1 cache
- **FR-1.2:** Load dataset and verify ≥ 500 models available in test split
- **FR-1.3:** Parse weight matrices and generalization gap labels (train_acc − test_acc)
- **FR-1.4:** Implement train/test split (use standard splits)
- **FR-1.5:** Create DataLoader with batch_size=64 supporting all 6 encoder input formats
- **FR-1.6:** Implement `canonicalize_weights(weight_matrices, method)` supporting 'l2_norm' and 'oracle' modes

### FR-2: Flat-MLP Encoder (E1 — Baseline, Reuse from H-E1)
- **FR-2.1:** Reuse `FlatMLPEncoder` from H-E1 — 3 × 512 hidden units, ReLU activations
- **FR-2.2:** Input: flattened weight matrices; Output: 1 scalar
- **FR-2.3:** No augmentation, no canonicalization during training or evaluation

### FR-3: Flat-MLP+Aug Encoder (E2)
- **FR-3.1:** Extend `FlatMLPEncoder` with training-time augmentation
- **FR-3.2:** During training: apply `apply_permutation_stress(weights, severity=1.0)` with 50% probability per batch
- **FR-3.3:** During evaluation: NO augmentation applied (evaluation uses standard stress protocol)
- **FR-3.4:** Architecture identical to E1 (same weights, different training)

### FR-4: Flat-MLP+Canon Encoder (E3)
- **FR-4.1:** Extend `FlatMLPEncoder` with L2-norm canonicalization preprocessing
- **FR-4.2:** Preprocessing: sort each layer's neurons by L2 norm (descending) before flattening
- **FR-4.3:** Apply canonicalization at both training AND evaluation time
- **FR-4.4:** Architecture identical to E1

### FR-5: NFT-Base Encoder (E4 — Proposed, Reuse from H-E1)
- **FR-5.1:** Reuse `NFTEquivariantEncoder` from H-E1 (equivariant attention, d_model=128, n_heads=4)
- **FR-5.2:** Input: list of weight matrices as `(B, n_neurons_l, fan_in_l)` per layer
- **FR-5.3:** Per-layer projection + equivariant self-attention + mean pooling + regression head
- **FR-5.4:** No augmentation, no canonicalization — equivariance comes from architecture

### FR-6: NFT+Aug Encoder (E5)
- **FR-6.1:** Reuse `NFTEquivariantEncoder` with training-time permutation augmentation
- **FR-6.2:** During training: apply `apply_permutation_stress(weights, severity=1.0)` with 50% probability
- **FR-6.3:** During evaluation: NO additional augmentation (standard stress protocol only)
- **FR-6.4:** Same architecture as E4

### FR-7: Oracle-Canon Encoder (E6 — Upper Bound)
- **FR-7.1:** Use `FlatMLPEncoder` with ground-truth canonical ordering as preprocessing
- **FR-7.2:** Oracle canonical order: sort neurons by ground-truth L2 norm using UNPERMUTED weights
- **FR-7.3:** Apply canonical ordering at both training AND evaluation time
- **FR-7.4:** Represents theoretical upper bound for canonicalization-based approaches
- **FR-7.5:** Architecture identical to E1 (same model capacity as flat-MLP)

### FR-8: Training Protocol (All Encoders)
- **FR-8.1:** Train each encoder independently for 100 epochs (6 encoders × 3 seeds = 18 runs)
- **FR-8.2:** Optimizer: Adam (lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4)
- **FR-8.3:** Schedule: CosineAnnealingLR (T_max=100, eta_min=1e-5)
- **FR-8.4:** Loss: MSE on generalization gap prediction
- **FR-8.5:** Seeds: [42, 123, 456] per encoder (3 seeds total per encoder)
- **FR-8.6:** Save checkpoints for best validation loss per seed
- **FR-8.7:** Log training loss, validation loss, and Spearman ρ per epoch

### FR-9: Permutation Stress Evaluation
- **FR-9.1:** Evaluate ALL 6 encoders at severity levels s ∈ {0, 0.25, 0.5, 1.0}
- **FR-9.2:** Compute Spearman ρ using `scipy.stats.spearmanr` at each severity level
- **FR-9.3:** Compute Δρ = ρ(s=0) − ρ(s=1.0) per encoder per seed
- **FR-9.4:** Report mean ± std of Δρ across 3 seeds per encoder
- **FR-9.5:** Minimum 500 models evaluated per severity level (full test set)

### FR-10: Mediation Analysis (ΔR²)
- **FR-10.1:** Compute R² (R-squared) = `sklearn.metrics.r2_score` for each encoder at s=0 (in-distribution)
- **FR-10.2:** Compute ΔR² = R²(NFT-base) − R²(flat-MLP+aug) — variance uniquely from equivariance
- **FR-10.3:** Report ΔR² ± std across 3 seeds
- **FR-10.4:** Mechanism PASS if ΔR² ≥ 0.10
- **FR-10.5:** Log ΔR² as primary mechanism metric in results JSON

### FR-11: Statistical Testing
- **FR-11.1:** Perform paired bootstrap test (n=10,000 resamples) for all 15 encoder pairs at s=1.0
- **FR-11.2:** Apply Holm correction for multiple comparisons (α=0.05)
- **FR-11.3:** Report p-values, effect sizes (Cohen's d), and 95% CI for Δρ
- **FR-11.4:** Report statistical significance of ΔR² (bootstrap confidence interval)

### FR-12: Gate Evaluation & Mechanism Verification
- **FR-12.1:** Implement `evaluate_gate_condition(results)` → PASS/FAIL
- **FR-12.2:** PASS if: nft_base_delta_rho < 0.02 AND mediation_delta_r2 ≥ 0.10
- **FR-12.3:** Report additional indicators: aug_partial (0.05 < flat-mlp+aug Δρ < 0.10), ranking_correct
- **FR-12.4:** Write gate result to `results/gate_result.json` with all indicator values
- **FR-12.5:** Implement `verify_mechanism_activated(results)` returning (gate_pass, indicators_dict)

```python
def verify_mechanism_activated(results):
    """Verify NFT equivariant attention mechanism mediates permutation robustness."""
    indicators = {
        "nft_base_robust":         results["NFT-base"]["delta_rho"] < 0.02,
        "mediation_confirmed":     results["mediation_delta_r2"] >= 0.10,
        "aug_partial":             0.05 < results["flat-MLP+aug"]["delta_rho"] < 0.10,
        "architecture_sufficient": results["NFT-base"]["delta_rho"] < results["flat-MLP+aug"]["delta_rho"],
        "ranking_correct": (
            results["NFT-base"]["delta_rho"] <
            results["flat-MLP+aug"]["delta_rho"] <
            results["flat-MLP"]["delta_rho"]
        )
    }
    gate_pass = indicators["nft_base_robust"] and indicators["mediation_confirmed"]
    return gate_pass, indicators
```

### FR-13: Visualization
- **FR-13.1 (MANDATORY):** Bar chart of Δρ at s=1.0 for all 6 encoders with gate threshold lines (Δρ=0.02, Δρ=0.10)
- **FR-13.2:** Multi-line plot of Δρ(s) for all 6 encoders at s ∈ {0, 0.25, 0.5, 1.0}
- **FR-13.3:** ΔR² breakdown bar chart: augmentation effect vs. architectural equivariance
- **FR-13.4:** Spearman ρ heatmap: 6-encoder × 4-severity levels
- **FR-13.5:** Bootstrap distribution comparison: NFT-base vs. flat-MLP+aug Δρ
- **FR-13.6:** Save all figures to `h-m1/figures/`

### FR-14: Experiment Runner
- **FR-14.1:** Single orchestration script `run_experiment.py` running all 18 training + evaluation runs
- **FR-14.2:** Support `--encoder` flag to run a single encoder (for debugging)
- **FR-14.3:** Support `--seed` flag to run a single seed
- **FR-14.4:** Sanity check: verify all 6 encoders produce valid output on 10 models before full training
- **FR-14.5:** Write final results JSON to `results/h-m1_results.json`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** 18 total training runs (6 encoders × 3 seeds × 100 epochs each)
- **NFR-1.2:** Use `CUDA_VISIBLE_DEVICES` single GPU as per pipeline rules
- **NFR-1.3:** Minimum 500 evaluation samples per severity level (full test set)

### NFR-2: Reproducibility
- **NFR-2.1:** Fixed seeds [42, 123, 456] for all random operations per encoder
- **NFR-2.2:** All results must be deterministic per seed across re-runs
- **NFR-2.3:** Report mean ± std across seeds for all metrics

### NFR-3: Error Handling
- **NFR-3.1:** Fail fast with clear error if any encoder produces NaN loss
- **NFR-3.2:** Training instability recovery: reduce lr to 1e-4 and retry once per seed
- **NFR-3.3:** Fail fast if < 500 models loaded in test split
- **NFR-3.4:** Log encoder failures individually — do NOT abort full run if 1 of 6 fails

### NFR-4: Code Quality
- **NFR-4.1:** Reuse H-E1 `FlatMLPEncoder` and `NFTEquivariantEncoder` implementations
- **NFR-4.2:** Each new encoder variant (E2, E3, E5, E6) extends base classes
- **NFR-4.3:** Unit tests for each new encoder variant (minimum 3 tests per variant)
- **NFR-4.4:** All tensor shapes documented in docstrings

### NFR-5: Code Reuse
- **NFR-5.1:** Prioritize reuse of H-E1 codebase (`h-e1/code/` or equivalent)
- **NFR-5.2:** Copy/symlink proven H-E1 modules rather than re-implementing
- **NFR-5.3:** Only implement new code for: E2, E3, E5, E6 encoder variants + mediation analysis

---

## 7. Technical Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=1.13 | Neural network framework |
| numpy | >=1.21 | Array operations |
| scipy | >=1.7 | Spearman ρ (`scipy.stats.spearmanr`) + bootstrap |
| scikit-learn | >=0.24 | R² score (`sklearn.metrics.r2_score`) |
| matplotlib | >=3.4 | Visualization |
| seaborn | >=0.11 | Heatmap visualization |
| pyyaml | >=5.4 | YAML I/O |
| tqdm | >=4.62 | Training progress bars |

### 7.2 H-E1 Code Dependencies (Reuse)

| Component | Source | Purpose |
|-----------|--------|---------|
| FlatMLPEncoder | h-e1/src/models.py | E1 baseline, base class for E2/E3/E6 |
| NFTEquivariantEncoder | h-e1/src/models.py | E4 proposed, base class for E5 |
| apply_permutation_stress | h-e1/src/data_loader.py | Permutation stress function |
| compute_delta_rho | h-e1/src/evaluate.py | Δρ computation |
| DataLoader setup | h-e1/src/data_loader.py | Zoo loading and batching |

### 7.3 External Repositories (Reference)

| Repository | URL | Purpose |
|------------|-----|---------|
| AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | Official NFT reference |
| google-research/dnn_predict_accuracy | https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy | Dataset reference |

### 7.4 Dataset Source

| Dataset | URL | Notes |
|---------|-----|-------|
| small_mnist_networks.pkl | https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl | Reuse from H-E1 if cached |

---

## 8. Implementation Architecture (High-Level)

```
h-m1/
├── data/
│   └── unterthiner_mnist_zoo.pkl        # Reuse from H-E1 or download
├── src/
│   ├── data_loader.py                   # Zoo loading + per-encoder DataLoader + canonicalize
│   ├── models.py                        # 6 encoder classes (E1-E6), extending H-E1 base classes
│   ├── train.py                         # Training loop for all encoders, multi-seed
│   ├── evaluate.py                      # Δρ, R², ΔR², gate evaluation, bootstrap stats
│   └── visualize.py                     # 5 figure types (FR-13.1–13.5)
├── tests/
│   ├── test_data_loader.py              # Dataset loading + canonicalization
│   ├── test_models.py                   # All 6 encoder variants, tensor shapes
│   └── test_evaluate.py                 # Δρ, ΔR², gate evaluation, bootstrap
├── figures/                             # Output figures
├── checkpoints/
│   └── {encoder_name}_seed{s}/         # Best checkpoint per encoder per seed
├── results/
│   ├── h-m1_results.json               # Full metrics (all encoders, all seeds, all severities)
│   └── gate_result.json                # Gate PASS/FAIL + all indicator values
└── run_experiment.py                    # Main orchestration: all 18 runs + analysis
```

---

## 9. Constraints & Assumptions

- **H-E1 reuse:** H-E1 code provides proven flat-MLP and NFT-base implementations; H-M1 MUST reuse these
- **Multi-seed:** 3 seeds required for MECHANISM hypothesis (unlike H-E1 EXISTENCE PoC with 1 seed)
- **Dataset:** Same Unterthiner MNIST zoo as H-E1 — identical splits for controlled comparison
- **NFT variable fan_in:** Already handled in H-E1 code via per-layer projection embedding
- **Evaluation scope:** Full test set (≥500 models) at all 4 severity levels — NOT subsampled
- **Independence of encoders:** Each encoder trained independently from scratch; no weight sharing between runs
- **ΔR² definition:** Computed at s=0 (in-distribution R²) for clean mechanism attribution; Δρ computed at s=1.0

---

## 10. Phase 2C Completeness Check

| Item | Included | Notes |
|------|----------|-------|
| ✅ Baseline model (flat-MLP, E1) | FR-2 | Proven H-E1 reuse |
| ✅ Ablation E2 (flat-MLP+aug) | FR-3 | Training-time augmentation variant |
| ✅ Ablation E3 (flat-MLP+canon) | FR-4 | L2-norm canonicalization variant |
| ✅ Proposed model (NFT-base, E4) | FR-5 | Proven H-E1 reuse |
| ✅ Ablation E5 (NFT+aug) | FR-6 | NFT + training augmentation |
| ✅ Ablation E6 (Oracle-canon) | FR-7 | Ground-truth canonical order ceiling |
| ✅ Static dataset (Unterthiner MNIST zoo) | Section 4.1 | Reuse from H-E1 |
| ✅ Permutation stress protocol (4 levels) | FR-9 | s ∈ {0, 0.25, 0.5, 1.0} |
| ✅ Primary metric (Spearman ρ, Δρ) | FR-9 | Per encoder, 3 seeds |
| ✅ Mechanism metric (ΔR²) | FR-10 | R²(NFT-base) − R²(flat-MLP+aug) |
| ✅ Statistical test (bootstrap, n=10,000) | FR-11 | Holm correction, 15 pairs |
| ✅ Gate evaluation (MUST_WORK) | FR-12 | Δρ < 0.02 AND ΔR² ≥ 0.10 |
| ✅ Visualization (gate metrics, 5 figures) | FR-13 | Mandatory + 4 additional |
| ✅ Multi-seed (3 seeds per encoder) | FR-8 | 18 total training runs |
| ✅ Code reuse from H-E1 | Section 9 | E1, E4, data loading, stress protocol |

---

*Generated by Phase 3 Step 2 from 02c_experiment_brief.md*
*Hypothesis: H-M1 | Type: MECHANISM | Tier: FULL (30 tasks max) | Prerequisite: H-E1 (PASS)*

# Product Requirements Document: H-E1

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**hypothesis_id:** h-e1
**hypothesis_type:** EXISTENCE
**generated_at:** 2026-03-16T12:30:00+00:00
**source:** Phase 2C experiment brief (02c_experiment_brief.md)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for **H-E1** — an EXISTENCE (Proof of Concept) experiment to verify the permutation sensitivity differential between flat-MLP encoders and NFT (Neural Functional Transformer) encoders when predicting generalization gaps of FC-MLP model zoo networks.

**Core Question:** Does the permutation sensitivity differential (flat-MLP Δρ > 0.10 vs. NFT Δρ < 0.02) actually exist and is it measurable under the Unterthiner FC-MLP zoo (MNIST) conditions?

**Gate:** MUST_WORK — if this phenomenon is not observed, the entire pipeline stops.

---

## 2. Problem Statement

Neural network model zoos contain networks that are functionally equivalent under neuron permutation (permutation symmetry). Flat-MLP encoders that take flattened weight vectors as input are sensitive to this permutation — reordering neurons within a layer changes the input representation, degrading prediction quality.

NFT (Neural Functional Transformer) encoders treat each neuron's weights as a "token" and apply permutation-equivariant attention — by design, permuting neurons permutes tokens, and the attention output is equivariant (the prediction is unaffected).

**H-E1 must demonstrate this differential is measurable** using the standard Unterthiner FC-MLP zoo benchmark dataset.

---

## 3. Hypothesis & Success Criteria

### Hypothesis Statement
Under controlled conditions using the Unterthiner FC-MLP zoo (MNIST, 2-4 layer), flat-MLP encoders show significantly degraded Spearman ρ for generalization gap prediction under permutation stress (Δρ > 0.10), while NFT encoders maintain robustness (Δρ < 0.02).

### Gate Condition (MUST_WORK)
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Flat-MLP permutation sensitivity | Δρ > 0.10 | Δρ at s=1.0 |
| NFT permutation robustness | Δρ < 0.02 | Δρ at s=1.0 |
| Statistical test | p < 0.05 (Holm-corrected, bootstrap n=10,000) | Paired bootstrap |

**PoC Pass (sufficient for H-E1):**
1. Code runs without error
2. `nft_delta_rho < flat_mlp_delta_rho` (NFT is more robust)

---

## 4. Data Specification

### 4.1 Primary Dataset

**Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Source:** Unterthiner et al. 2020, "Predicting Neural Network Accuracy from Weights"
**Type:** standard (real, established — NOT synthetic)
**Download Method:** Manual download (REQUIRED — not auto-download)

**Download URL:**
```
https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl
```

**Download Code:**
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
- Labels: Generalization gap = training_accuracy − test_accuracy (continuous scalar, range ≈ 0.0–0.15)
- Splits: standard train/test splits from original release
- **Minimum samples for evaluation:** 500 (per verification plan requirement)

**Storage Path:** `data/unterthiner_mnist_zoo.pkl`

### 4.2 Preprocessing Requirements

| Step | Description | Apply To |
|------|-------------|----------|
| Weight normalization | Standardize each weight matrix (zero mean, unit std per neuron row for NFT; globally for flat-MLP) | Both models |
| Flattening | Concatenate all weight matrices into single vector | Flat-MLP only |
| Layer structure preservation | Pass as sequence of weight matrices (list of tensors) | NFT only |
| Variable-dim handling | Per-layer projection embedding (different fan_in per layer) | NFT required |

### 4.3 Permutation Stress Protocol

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

**Severity levels:** s ∈ {0, 0.25, 0.5, 1.0}

---

## 5. Functional Requirements

### FR-1: Dataset Download & Loading
- **FR-1.1:** Download `small_mnist_networks.pkl` from Google Research storage
- **FR-1.2:** Load dataset into memory and verify ≥ 500 models available
- **FR-1.3:** Parse weight matrices and generalization gap labels (train_acc − test_acc)
- **FR-1.4:** Implement train/test split (use standard splits if available, else 80/20)
- **FR-1.5:** Create DataLoader with batch_size=64 for both flat-MLP and NFT input formats

### FR-2: Flat-MLP Encoder (Baseline)
- **FR-2.1:** Implement `FlatMLPEncoder` — 3 × 512 hidden units, ReLU activations
- **FR-2.2:** Input: flattened concatenation of all weight matrices (variable length ~5K–50K)
- **FR-2.3:** Output: 1 scalar (generalization gap prediction)
- **FR-2.4:** No positional encoding, no permutation awareness
- **FR-2.5:** Architecture follows Unterthiner et al. 2020 specification

### FR-3: NFT Encoder (Proposed)
- **FR-3.1:** Implement `NFTEquivariantEncoder` with permutation-equivariant attention
- **FR-3.2:** Input: list of weight matrices, each as `(B, n_neurons_l, fan_in_l)` — one per layer
- **FR-3.3:** Per-layer projection: separate `nn.Linear(fan_in_l, d_model)` per layer (handles variable dims)
- **FR-3.4:** Equivariant self-attention: `nn.MultiheadAttention(d_model=128, n_heads=4, batch_first=True)`
- **FR-3.5:** Aggregate via mean pooling over neuron tokens → (B, d_model)
- **FR-3.6:** Regression head: `nn.Linear(d_model, 1)`
- **FR-3.7:** Support variable number of layers (2–4) via padding or masked attention
- **FR-3.8:** Verify permutation equivariance via token shape logging

### FR-4: Permutation Stress Testing
- **FR-4.1:** Implement `apply_permutation_stress(weight_matrices, severity)` function
- **FR-4.2:** Apply stress at test time only (not during training) for evaluation
- **FR-4.3:** Test at severity levels s ∈ {0, 0.25, 0.5, 1.0}
- **FR-4.4:** Compute Spearman ρ at each severity level

### FR-5: Evaluation & Metrics
- **FR-5.1:** Implement `compute_delta_rho(model, loader, severity_levels)` returning (delta_rho, rho_by_severity)
- **FR-5.2:** Compute Spearman ρ using `scipy.stats.spearmanr`
- **FR-5.3:** Compute Δρ = ρ(s=0) − ρ(s=1.0)
- **FR-5.4:** Compute paired bootstrap test (n=10,000) for significance (p-value)
- **FR-5.5:** Apply Holm correction for multiple comparisons
- **FR-5.6:** Log all metrics to results file

### FR-6: Gate Evaluation
- **FR-6.1:** Implement `evaluate_gate_condition(flat_mlp_delta_rho, nft_delta_rho)` → PASS/FAIL
- **FR-6.2:** PASS if: flat_mlp_delta_rho > 0.10 AND nft_delta_rho < 0.02
- **FR-6.3:** Write gate result to `results/gate_result.json`
- **FR-6.4:** Implement `verify_mechanism_activated(model, batch, results)` with 3 indicators

### FR-7: Visualization
- **FR-7.1 (MANDATORY):** Bar chart of Δρ for flat-MLP vs NFT-base at s=1.0 with threshold lines
- **FR-7.2:** Line plot of ρ(s) for both models across severity levels {0, 0.25, 0.5, 1.0}
- **FR-7.3:** Scatter plot of predicted vs. actual generalization gap (at s=0 and s=1.0)
- **FR-7.4:** Bootstrap Δρ distribution histogram for both models at s=1.0
- **FR-7.5:** Save all figures to `h-e1/figures/`

### FR-8: Experiment Runner
- **FR-8.1:** Single experiment script `run_experiment.py` that trains both models and evaluates
- **FR-8.2:** Set `seed=42` for reproducibility
- **FR-8.3:** Log training progress (loss per epoch, final Spearman ρ per model)
- **FR-8.4:** Save trained model checkpoints to `checkpoints/`
- **FR-8.5:** Write final results JSON to `results/h-e1_results.json`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- **NFR-1.1:** Training must complete in reasonable time on single GPU (estimate: <2 hours per model)
- **NFR-1.2:** Minimum 500 evaluation samples (full test set preferred)
- **NFR-1.3:** Use `CUDA_VISIBLE_DEVICES` single GPU as per pipeline rules

### NFR-2: Reproducibility
- **NFR-2.1:** Fixed seed (42) for all random operations (torch, numpy, random)
- **NFR-2.2:** All results must be deterministic across runs with same seed

### NFR-3: Error Handling
- **NFR-3.1:** Fail fast with clear error if fan_in dimensions are incompatible with NFT projection
- **NFR-3.2:** Fail fast if dataset download fails or < 500 models loaded
- **NFR-3.3:** Handle training instability (NaN loss) — reduce lr to 1e-4 and retry once

### NFR-4: Code Quality
- **NFR-4.1:** Each module must have unit tests (minimum 3 test methods with real assertions)
- **NFR-4.2:** All tensor shapes documented in docstrings

---

## 7. Technical Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=1.13 | Neural network framework |
| numpy | >=1.21 | Array operations |
| scipy | >=1.7 | Spearman ρ computation (`scipy.stats.spearmanr`) |
| scikit-learn | >=0.24 | MSE/R² metrics |
| matplotlib | >=3.4 | Visualization |
| seaborn | >=0.11 | Statistical visualization |
| pyyaml | >=5.4 | YAML I/O |
| tqdm | >=4.62 | Training progress bars |

### 7.2 External Repositories (Reference)

| Repository | URL | Purpose |
|------------|-----|---------|
| AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | Official NFT implementation reference |
| google-research/dnn_predict_accuracy | https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy | Dataset + flat-MLP baseline reference |

**Note:** These are reference implementations. Phase 4 may use them directly (install from GitHub) or re-implement from paper specification.

### 7.3 Dataset Source

| Dataset | URL | Size Estimate |
|---------|-----|---------------|
| small_mnist_networks.pkl | https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl | ~50-100 MB |

---

## 8. Implementation Architecture (High-Level)

```
h-e1/
├── data/
│   └── unterthiner_mnist_zoo.pkl      # Downloaded dataset
├── src/
│   ├── data_loader.py                 # Dataset loading, preprocessing, DataLoader
│   ├── models.py                      # FlatMLPEncoder, NFTEquivariantEncoder
│   ├── train.py                       # Training loop with Adam optimizer
│   ├── evaluate.py                    # compute_delta_rho(), gate evaluation
│   └── visualize.py                   # Figure generation
├── tests/
│   ├── test_data_loader.py
│   ├── test_models.py
│   └── test_evaluate.py
├── figures/                           # Output figures
├── checkpoints/                       # Trained model weights
├── results/
│   ├── h-e1_results.json             # Full metrics
│   └── gate_result.json              # Gate PASS/FAIL verdict
└── run_experiment.py                  # Main experiment script
```

---

## 9. Constraints & Assumptions

- **EXISTENCE PoC:** Single seed (42) is sufficient — multi-seed runs are handled in H-M1
- **Dataset:** Unterthiner MNIST zoo is publicly available and downloadable
- **NFT architecture:** Must handle variable fan_in per layer (2–4 layer MLPs with widths 32–512)
- **No pretrained NFT weights:** Train from scratch on the zoo dataset
- **Evaluation scope:** Full test set (not subsampled) — minimum 500 models required

---

## 10. Phase 2C Completeness Check

| Item | Included | Notes |
|------|----------|-------|
| ✅ Baseline model (Flat-MLP) | FR-2 | Unterthiner et al. 2020 architecture |
| ✅ Proposed model (NFT-base) | FR-3 | Zhou et al. 2023, equivariant attention |
| ✅ Static dataset (Unterthiner MNIST zoo) | Section 4.1 | Manual download required |
| ✅ Permutation stress protocol | FR-4 | s ∈ {0, 0.25, 0.5, 1.0} |
| ✅ Primary metric (Spearman ρ, Δρ) | FR-5 | scipy.stats.spearmanr |
| ✅ Statistical test (bootstrap) | FR-5.4–5.5 | n=10,000, Holm correction |
| ✅ Gate evaluation | FR-6 | MUST_WORK threshold check |
| ✅ Visualization (gate metrics) | FR-7.1 | Mandatory bar chart |
| ✅ Mechanism verification | FR-6.4 | Token shape + permutation indicators |
| ℹ️ Ablation variants | None | EXISTENCE PoC — no ablations required |

---

*Generated by Phase 3 Step 2 from 02c_experiment_brief.md*
*Hypothesis: H-E1 | Type: EXISTENCE | Tier: LIGHT (15 tasks max)*

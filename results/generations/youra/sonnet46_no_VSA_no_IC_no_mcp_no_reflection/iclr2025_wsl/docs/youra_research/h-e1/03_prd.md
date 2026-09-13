---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: "yoon303@ust.ac.kr"
---

# Product Requirements Document: H-E1

## 1. Executive Summary

H-E1 is a Proof-of-Concept (PoC) experiment to determine whether the **generalization gap** (train_acc − test_acc) encodes a learnable signal in CNN weight tensors. Using the Unterthiner CIFAR-10 CNN zoo (~10,000 trained models), four weight-space encoders (FlatMLP, DWSNet, NFT, GNN) will each be trained to predict the gap scalar. The gate condition is: ≥1 encoder achieves Spearman r > 0.5 on the held-out test split.

This experiment is the **foundation** of the H-E1 → H-M1 → H-M2 → H-M3 → H-M4 chain. A PASS unlocks mechanism-level hypotheses; a FAIL stops the chain.

---

## 2. Problem Statement

**Research Question:** Does the generalization gap (train_acc − test_acc) encode a non-trivial, learnable signal in weight tensors at convergence?

**Why it matters:** Prior work (Unterthiner 2020, Navon 2023, Zhou 2023, Kofinas 2024) shows weight encoders predict *test accuracy* well (r ≈ 0.67–0.94). Whether they can predict *gap* (a different and potentially more useful quantity) is unknown. If gap is learnable, it opens the door to convergence-regime generalization prediction without test labels.

**Success Threshold:** r > 0.5 is conservative (well above noise, well below the test_acc r values), ensuring the existence finding is robust.

---

## 3. Functional Requirements

### FR-0: Pre-condition Audit (MANDATORY — must run BEFORE any encoder training)

**FR-0.1 — A1 Audit Check:**
- Compute Spearman(gap, −test_acc) on the full zoo (all N models)
- If correlation ≥ 0.95: STOP entire experiment; raise `AssertionError("A1 FAIL: gap ≈ -test_acc; switch to PDFD zoo")`
- If correlation < 0.95: record value, proceed
- Record: gap distribution statistics (mean, std, min, max, range)

**FR-0.2 — Fixed Data Split:**
- Split: 80/10/10 (train/val/test) by model index
- Seed: 42
- Split must be computed ONCE before any model is trained; indices stored and reused for all 4 encoders

### FR-1: Data Loading

**FR-1.1 — Zoo Download:**
- Source: Unterthiner CIFAR-10 CNN zoo (OSF: https://osf.io/hbm72/ or google-research/cnns_weight_prediction data release)
- Format: `.npz` file with arrays: `weights` (per-layer or flat), `train_acc`, `test_acc`
- Computed field: `gap = train_acc - test_acc` (prediction target for H-E1)

**FR-1.2 — Data Loading Interface:**
- Function: `load_zoo(path) → ZooData`
- `ZooData` contains: weight arrays per layer, gap array, split indices
- Must handle both flat weight format and per-layer list format

**FR-1.3 — Dataset Size:**
- Full zoo: ~10,000 models (do NOT subsample — use all available models)
- Train split: ~8,000 models; Val split: ~1,000 models; Test split: ~1,000 models

### FR-2: Encoder Implementations

**FR-2.1 — FlatMLP Encoder (Unterthiner 2020 baseline):**
- Sort all weights by L2 magnitude per layer → concatenate into flat vector
- Architecture: 3-layer MLP (Linear→ReLU→Linear→ReLU→Linear), hidden_dim=256
- Output: scalar prediction (B,)
- Source: B.4 (google-research/cnns_weight_prediction)

**FR-2.2 — DWSNet Encoder (Navon 2023):**
- Per-layer permutation-equivariant layers + mean pooling across layers + MLP head
- Architecture: EquivariantLayer per weight shape; scalar head
- Output: scalar prediction (B,)
- Source: B.1 (AvivNavon/DWSNets — official author implementation)

**FR-2.3 — NFT Encoder (Zhou 2023):**
- Weight matrix rows/cols as tokens → cross-layer transformer attention → CLS token → scalar head
- Memory note: use batch_size=32 (vs. 64 for others) due to attention memory
- Output: scalar prediction (B,)
- Source: B.3 (AllanYangZhou/nfn — official author implementation)

**FR-2.4 — GNN Encoder (Kofinas 2024):**
- Bipartite graph (neuron nodes + weight edges) → GNN message passing → global pooling → scalar head
- Output: scalar prediction (B,)
- Source: B.2 (mkofinas/neural-graphs — official author implementation)

**FR-2.5 — Common Encoder Interface:**
- All 4 encoders MUST implement: `forward(weights) → Tensor(B,)` (scalar per model)
- Loss: `F.mse_loss(pred, target_gap)` for all encoders
- The ONLY change from published code: prediction target = `gap` instead of `test_acc`

### FR-3: Hyperparameter Search

**FR-3.1 — Per-Encoder Search Protocol:**

| Encoder | LR candidates | Batch | Epochs | LR schedule |
|---------|--------------|-------|--------|-------------|
| FlatMLP | {1e-4, 5e-4, 1e-3} | 64 | 100 | None |
| DWSNet  | {1e-4, 5e-4, 1e-3} | 64 | 100 | None |
| NFT     | {1e-5, 1e-4, 5e-4} | 32 | 200 | Cosine annealing |
| GNN     | {1e-4, 5e-4, 1e-3} | 64 | 100 | Cosine LR |

- Optimizer: Adam (all encoders)
- Loss: MSE (all encoders)
- Budget: 50 trials per encoder (random search over LR candidates × other params)
- Val selection criterion: best val Spearman r(predicted_gap, true_gap)
- Seed: 42 (single seed for EXISTENCE PoC)

**FR-3.2 — Training Loop Requirements:**
- Track val Spearman r per epoch
- Save best model state (by val Spearman)
- Final evaluation on held-out test split using best checkpoint

### FR-4: Evaluation

**FR-4.1 — Primary Metric:** Spearman r(predicted_gap, true_gap) on test set
- Library: `scipy.stats.spearmanr`
- Report: correlation coefficient + p-value

**FR-4.2 — Secondary Metric:** MSE on test set
- Library: `sklearn.metrics.mean_squared_error`

**FR-4.3 — Gate Evaluation:**
- Gate PASS: any(r > 0.5 for r in test_spearman_values.values())
- Gate FAIL: all encoders ≤ 0.5 → STOP, flag A1 failure mode

**FR-4.4 — Results Table (mandatory output):**

| Encoder | Val Spearman(gap) | Test Spearman(gap) | Test MSE | Gate Pass? |
|---------|-------------------|---------------------|----------|------------|
| FlatMLP | — | — | — | — |
| DWSNet  | — | — | — | — |
| NFT     | — | — | — | — |
| GNN     | — | — | — | — |
| **H-E1 Gate** | — | **≥1 > 0.5?** | — | **TBD** |

### FR-5: Visualization

**FR-5.1 — Mandatory Figure:**
- Bar chart: Spearman r per encoder (test set) with horizontal threshold line at r = 0.5
- Save to: `h-e1/figures/encoder_gap_spearman.png`

**FR-5.2 — Additional Figures (autonomous):**
- Scatter: predicted gap vs. true gap for best encoder (test set) → `best_encoder_scatter.png`
- Histogram: true gap distribution across full zoo → `gap_distribution.png`
- Audit scatter: gap vs. −test_acc with Spearman r annotation → `a1_audit_scatter.png`
- Training curves: val Spearman per epoch per encoder (best trial) → `training_curves.png`

**FR-5.3:** All figures saved to `h-e1/figures/` directory (create if not exists)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Unterthiner CIFAR-10 CNN Zoo |
| Size | ~10,000 trained CNN models |
| Format | NPZ (numpy arrays) |
| Source | OSF: https://osf.io/hbm72/ OR google-research/cnns_weight_prediction |
| Download method | Manual download (NOT auto-download) |
| Labels | train_acc, test_acc per model |
| Computed label | gap = train_acc − test_acc |
| Split | 80/10/10, seed=42, by model index |

**⚠️ Manual download required** — this dataset does NOT auto-download via PyG/torchvision.

### 4.2 Data Audit Pre-condition

Before any training:
1. Load full zoo
2. Compute gap = train_acc − test_acc for all N models
3. Compute Spearman(gap, −test_acc)
4. Assert < 0.95 (else STOP and switch to PDFD zoo)

---

## 5. Success Criteria

| Criterion | Condition | Gate Type |
|-----------|-----------|-----------|
| Primary gate | ≥1 encoder Spearman r(gap) > 0.5 on test set | MUST_WORK |
| Data audit | Spearman(gap, −test_acc) < 0.95 | Pre-condition |
| Code runs | No runtime errors in full pipeline | Baseline |

**Fail action:** All encoders ≤ 0.5 → STOP; investigate gap distribution; if A1 triggered (≥ 0.95), switch primary venue to Schürholt PDFD zoo.

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| Reproducibility | Fixed seed=42; all random operations seeded |
| Correctness | Target must be gap (not test_acc) for all 4 encoders |
| Budget | LIGHT tier: ≤15 implementation tasks |
| Performance | Full zoo evaluation; no subsampling |
| Compatibility | Python 3.9+, PyTorch 2.0+, scipy, sklearn |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision>=0.15.0
torch-geometric>=2.3.0   # for GNN encoder
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Reference Implementations)

| Repo | URL | Usage |
|------|-----|-------|
| DWSNets (B.1) | https://github.com/AvivNavon/DWSNets | DWS encoder architecture |
| neural-graphs (B.2) | https://github.com/mkofinas/neural-graphs | GNN encoder architecture |
| nfn (B.3) | https://github.com/AllanYangZhou/nfn | NFT encoder architecture |
| cnns_weight_prediction (B.4) | https://github.com/google-research/google-research/tree/master/cnns_weight_prediction | Flat MLP baseline + zoo data |

**Note:** Official implementations are used as reference. The ONLY modification for H-E1: prediction target = `gap` instead of `test_acc`.

---

## 8. Implementation Constraints

- **Do NOT subsample** the zoo — use all ~10,000 models for statistical validity
- **FlatMLP** serves dual role: one of 4 tested encoders AND the non-equivariant baseline for H-M1 comparison
- **NFT** must use batch_size=32 (memory constraint from cross-layer attention)
- **50-trial random search** per encoder — select by val Spearman, report on test
- **Mandatory audit** before training — failure to run A1 check is a protocol violation

---

*PRD generated: 2026-08-31 | Phase 3 Step 2 | ABLATION MODE (Archon MCP unavailable)*

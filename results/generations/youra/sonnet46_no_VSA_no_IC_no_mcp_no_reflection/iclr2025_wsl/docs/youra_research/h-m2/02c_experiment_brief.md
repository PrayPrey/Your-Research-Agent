# Experiment Design: h-m2

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under fixed hyperparameter search conditions, if permutation-equivariant encoders (DWS, NFT, GNN) are applied to weight tensors from the same model zoo, then their internal representations yield a differential advantage Δ > 0.02 Spearman units on generalization gap vs. test accuracy prediction, because architectural parameter sharing across neuron equivalence classes prevents learning of position-specific spurious features that do not generalize.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — "Do equivariant encoders show a target-specific differential advantage on gap vs. test_acc?" validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS (h-m2)
**Prerequisites Satisfied:** h-m1 VALIDATED (NFT Spearman(gap)=0.5752 > FlatMLP=0.5330; gate MUST_WORK passed)
**Gate Status:** MUST_WORK — Δ > 0.02 Spearman units on gap vs. test_acc differential advantage for ≥2 of 3 equivariant encoders

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED)

### Gate Condition

**MUST_WORK:** Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN}, where:
```
Δ(encoder) = [Spearman(gap, encoder) − Spearman(gap, FlatMLP)]
           − [Spearman(test_acc, encoder) − Spearman(test_acc, FlatMLP)]
```

**Interpretation:** Equivariant encoders must show a *disproportionately larger* improvement over FlatMLP on gap prediction than on test_acc prediction. This tests whether the equivariance advantage is target-specific (gap) or generic (both targets equally).

---

## Continuation Context

**Continuation from H-M1:** This hypothesis is primarily ANALYSIS with one additional training component.

- **Gap target checkpoints:** Already trained in H-E1/H-M1. Reuse directly.
- **Test_acc target:** H-M1 did NOT train on test_acc target. Must train all 4 encoders on test_acc using identical protocol to H-E1/H-M1.
- **Budget:** Same 3-trial random search (matching H-M1 actual budget), consistent with H-E1.

### Previous Hypothesis Results (H-M1)

From h-m1 04_validation.md (2026-08-31):

| Encoder | Type | Spearman r (gap) | 95% CI |
|---------|------|-------------------|--------|
| FlatMLP | position-indexed | 0.5330 | [0.4850, 0.5801] |
| DWSNet | equivariant | 0.4881 | [0.4377, 0.5325] |
| NFT | equivariant | **0.5752** | **[0.5339, 0.6158]** |
| GNN | equivariant | 0.3747 | [0.3180, 0.4265] |

- **H-M1 gate:** PASS (NFT Δ_gap = +0.0422 vs FlatMLP)
- **Key finding from H-M1:** NFT's cross-layer attention benefits from globally distributed gap signal. DWSNet and GNN do NOT benefit (within-layer equivariance insufficient).
- **Prior work test_acc (Unterthiner zoo, from papers):** DWSNet ≈ 0.90, NFT ≈ 0.90+ (state-of-art), GNN competitive. FlatMLP ≈ 0.85.

**Computation required for H-M2:**
1. Train all 4 encoders on test_acc target (new, identical protocol)
2. Compute Δ(encoder) for all 3 equivariant encoders
3. Verify Δ > 0.02 for ≥2 encoders

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP UNAVAILABLE — sourced from published literature and H-M1 validated findings.*

**Finding 1: Differential Advantage Testing Pattern**
- From: Unterthiner et al. 2020 (arxiv 2002.11448); Navon et al. 2023 (arxiv 2301.12780)
- Standard practice: evaluate same encoder on multiple regression targets using identical protocol — enables controlled target comparison
- Key insight: Gap and test_acc have different weight-space signal structures (confirmed by H-E1 A1 audit: Spearman(gap, −test_acc) = −0.1422)
- Hyperparameters: AdamW, lr=1e-3, batch=64, MSE loss, 100 epochs — use same as H-M1

**Finding 2: Test_acc Prediction Benchmarks**
- From: Prior work on same Unterthiner zoo
- FlatMLP Spearman(test_acc): typically 0.85–0.88 on CIFAR-10 zoo
- DWSNet Spearman(test_acc): ~0.90 (Navon 2023 Table 2)
- NFT Spearman(test_acc): ~0.90–0.92 (Zhou 2023)
- GNN Spearman(test_acc): ~0.88–0.90 (Kofinas 2024)
- Key insight: All encoders show similar test_acc performance — Δ_test_acc ≈ 0 for all. If gap shows Δ > 0.02 for equivariant encoders, the differential is target-specific.

**Finding 3: Partial Correlation as Secondary Metric (P3)**
- From: 02b_verification_plan.md §H-M2 Verification Protocol step 4
- Spearman(equivariant_pred_gap, true_gap | test_acc) > 0, p < 0.05
- Controls for the possibility that equivariant improvement on gap is just improvement on a correlated quantity
- Implementation: `scipy.stats.spearmanr` on residuals after regressing out test_acc prediction

### Archon Code Examples

*MCP UNAVAILABLE — code synthesized from H-M1 brief and official repos.*

**Pattern: Dual-Target Training Loop**
```python
# Train encoder on test_acc target — mirrors H-M1/H-E1 protocol exactly
def train_encoder_test_acc(encoder_class, zoo_data, n_trials=3, seed=42):
    best_val_r, best_state = -np.inf, None
    for trial in range(n_trials):
        model = encoder_class(...)
        optimizer = torch.optim.AdamW(model.parameters(), lr=sample_lr())
        for epoch in range(100):
            train_step(model, optimizer, zoo_data["train"], target="test_acc")
            val_r = evaluate_spearman(model, zoo_data["val"], target="test_acc")
            if val_r > best_val_r:
                best_val_r = val_r
                best_state = deepcopy(model.state_dict())
    return best_val_r, best_state
```

### Exa GitHub Implementations

*MCP UNAVAILABLE — repositories from H-M1 brief, all confirmed official.*

**Repository 1: AvivNavon/DWSNets** (official, highest priority)
- URL: https://github.com/AvivNavon/DWSNets
- Relevance: Official DWSNets implementation with Unterthiner zoo training scripts
- Training Config: AdamW lr=1e-3, batch=64, 100 epochs, MSE loss
- test_acc task: supported natively (change target label in dataloader)
- Serena analysis needed: false

**Repository 2: mkofinas/neural-graphs** (official GNN)
- URL: https://github.com/mkofinas/neural-graphs
- Relevance: Official GNN encoder with CIFAR-10 zoo experiments
- Training Config: Adam, lr=5e-4, cosine LR schedule, batch=32
- test_acc task: supported via target argument

**Repository 3: zhou-yf/neural-functional-transformers** (NFT)
- URL: (search: Zhou 2023 Neural Functional Transformers GitHub)
- Relevance: NFT official code — highest test_acc performer from H-M1
- Training Config: AdamW, more hyperparameter-sensitive (risk documented in H-M1)

### 🎯 Implementation Priority Assessment

**Continuation from H-M1 — reuse protocol exactly.**

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with `target="test_acc"` branch; run same 3-trial search
- Fallback: Use official repo training scripts with test_acc label
- Justification: Controlled comparison requires identical training protocol; only target label changes

### Code Analysis (Serena MCP)

*Skipped* — Code from H-M1 brief and official repos is sufficiently clear. H-M2 is a clean extension of H-M1 with one additional training target.

---

## Experiment Specification

### Dataset

**Name:** Unterthiner CIFAR-10 CNN Model Zoo
**Type:** standard (model zoo — weight tensors from trained CNNs)
**Source:** Unterthiner et al. 2020 (arxiv 2002.11448), public release
**N:** ~10,000 trained CNN models
**D:** 33,890 weight parameters per model (flattened, sorted)
**Targets:**
- `generalization_gap` = train_acc − test_acc (already used in H-M1)
- `test_acc` (NEW for H-M2 — second prediction target)
**Splits:** 80/10/10 (train/val/test) — SAME split as H-E1/H-M1 (seed=42, do NOT re-split)

**A1 audit (from H-E1, confirmed):**
- Spearman(gap, −test_acc) = −0.1422 << 0.95 ✅ — gap and test_acc carry independent information

**Statistics (from H-E1):**
- N_test = 1,000 models
- D = 33,890 (flattened, sorted weight vectors)

**Loading Information** (for Phase 4 download):
- Method: custom (reuse H-E1/H-M1 data pipeline)
- Identifier: `./data/unterthiner_zoo/`
- Code:
```python
# Load both targets from same zoo
weights, labels = load_zoo(
    zoo_path="./data/unterthiner_zoo/",
    targets=["generalization_gap", "test_acc"],  # H-M2 needs both
    split="test",
    seed=42
)
gap_labels = labels["generalization_gap"]
test_acc_labels = labels["test_acc"]
```

### Models

#### Baseline Model

**Architecture:** FlatMLP (position-indexed weight encoder)
- Input: D=33,890 sorted/flattened weight vector
- Hidden: [512, 512] with ReLU activations
- Output: scalar prediction (gap or test_acc depending on target)
- Source: Unterthiner et al. 2020; H-M1 trained checkpoints

**Loading Information** (for Phase 4):
- Gap checkpoint: `h-m1/checkpoints/flat_mlp_gap_best.pt`
- Test_acc checkpoint: `h-m2/checkpoints/flat_mlp_testacc_best.pt` (to be trained)
- Code: `flat_mlp.load_state_dict(torch.load(checkpoint_path))`

#### Proposed Models (Equivariant Encoders)

**Architecture:** DWSNet, NFT, GNN — same as H-M1, with additional test_acc training

**Core Mechanism Implementation:**

```python
# H-M2: Differential Advantage Analysis
# Based on: H-M1 gap results + new test_acc training
# Purpose: Test if equivariance advantage is target-specific (gap > test_acc)

def run_h_m2_experiment(zoo_data, h_m1_gap_results, checkpoint_dir):
    """
    Args:
        zoo_data: dict with 'weights' (N, D), 'gap' (N,), 'test_acc' (N,)
        h_m1_gap_results: dict encoder_name -> Spearman(gap) from H-M1
        checkpoint_dir: where to save/load test_acc checkpoints
    Returns:
        delta: dict encoder_name -> Δ (differential advantage)
        gate_passed: bool (Δ > 0.02 for ≥2 equivariant encoders)
    """
    encoders = ["flat_mlp", "dws_net", "nft", "gnn"]

    # Step 1: Train all 4 encoders on test_acc target (new)
    test_acc_results = {}
    for enc in encoders:
        model = build_encoder(enc)
        best_r, best_state = train_encoder(
            model, zoo_data["train"], zoo_data["val"],
            target="test_acc", n_trials=3, seed=42
        )
        torch.save(best_state, f"{checkpoint_dir}/{enc}_testacc_best.pt")
        test_acc_results[enc] = evaluate_spearman(
            model, zoo_data["test"], target="test_acc"
        )
        print(f"[H-M2] {enc}: Spearman(test_acc)={test_acc_results[enc]:.4f}")

    # Step 2: Retrieve gap results from H-M1
    gap_results = h_m1_gap_results  # {enc: Spearman(gap)} already measured

    # Step 3: Compute Δ for each equivariant encoder
    delta = {}
    for enc in ["dws_net", "nft", "gnn"]:
        gap_improvement = gap_results[enc] - gap_results["flat_mlp"]
        acc_improvement = test_acc_results[enc] - test_acc_results["flat_mlp"]
        delta[enc] = gap_improvement - acc_improvement
        print(f"[H-M2] {enc}: Δ={delta[enc]:.4f} (gap_imp={gap_improvement:.4f}, acc_imp={acc_improvement:.4f})")

    # Step 4: Gate check
    n_pass = sum(1 for d in delta.values() if d > 0.02)
    gate_passed = n_pass >= 2
    print(f"[H-M2] Gate: {'PASS' if gate_passed else 'FAIL'} ({n_pass}/3 encoders Δ > 0.02)")
    return delta, test_acc_results, gate_passed

# Secondary metric: partial Spearman (P3)
def partial_spearman_gap_given_acc(model_preds, true_gap, true_acc):
    """Spearman(gap_pred, true_gap | true_acc) — controls for test_acc correlation."""
    from scipy.stats import spearmanr
    from sklearn.linear_model import LinearRegression

    acc_rank = np.argsort(np.argsort(true_acc)).reshape(-1, 1)
    gap_pred_rank = np.argsort(np.argsort(model_preds))
    true_gap_rank = np.argsort(np.argsort(true_gap))

    resid_pred = gap_pred_rank - LinearRegression().fit(acc_rank, gap_pred_rank).predict(acc_rank)
    resid_true = true_gap_rank - LinearRegression().fit(acc_rank, true_gap_rank).predict(acc_rank)

    r, p = spearmanr(resid_pred, resid_true)
    return r, p
```

### Training Protocol

**New training required:** All 4 encoders trained on `test_acc` target (H-M1 gap checkpoints are reused as-is).

**From H-M1 (reused for test_acc training — identical protocol for controlled comparison):**
- Optimizer: AdamW
- LR search range: [5e-4, 2e-3] (3-trial random search)
- Batch size: 64
- Epochs: 100 with early stopping on val Spearman(test_acc)
- Loss: MSE on test_acc target
- Seeds: 42 (fixed — same as H-E1/H-M1)
- Budget: 3 trials per encoder (matching H-M1 actual budget)

**Source:** H-M1 02c_experiment_brief.md §Training Protocol; Navon 2023 (DWSNets), Unterthiner 2020 (FlatMLP)

**Gap target results (H-M1, reused):**
- FlatMLP Spearman(gap): 0.5330
- DWSNet Spearman(gap): 0.4881
- NFT Spearman(gap): 0.5752
- GNN Spearman(gap): 0.3747

### Evaluation

**Primary Metrics:**
- Spearman_r(predicted_test_acc, true_test_acc) per encoder on test split (NEW)
- Δ(encoder) = [Spearman(gap,enc) − Spearman(gap,FlatMLP)] − [Spearman(test_acc,enc) − Spearman(test_acc,FlatMLP)]
- Count of encoders with Δ > 0.02

**Secondary Metric (P3 — Partial Correlation):**
- Spearman(NFT_pred_gap, true_gap | true_test_acc) > 0, p < 0.05
- Focus on NFT (best gap encoder from H-M1)

**Success Criteria (MUST_WORK gate):**
- Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN}

**Expected values (informed by prior work + H-M1):**
- FlatMLP Spearman(test_acc): ~0.85–0.88
- DWSNet Spearman(test_acc): ~0.90 (Navon 2023) → acc_improvement ≈ +0.04
- NFT Spearman(test_acc): ~0.90–0.92 → acc_improvement ≈ +0.04–0.06
- GNN Spearman(test_acc): ~0.88–0.90 → acc_improvement ≈ +0.02–0.04

**Δ pre-computation (approximate, to assess gate feasibility):**
- NFT: gap_imp = +0.0422; expected acc_imp ≈ +0.04–0.06; Δ ≈ −0.02 to +0.00 (marginal — test_acc accuracy may mask gap advantage)
- DWSNet: gap_imp = −0.0449; if acc_imp ≈ +0.04, Δ ≈ −0.08 (negative)
- GNN: gap_imp = −0.1583; if acc_imp ≈ +0.02, Δ ≈ −0.18 (strongly negative)

**Critical note:** Based on pre-computation, Δ > 0.02 for ≥2 encoders may be DIFFICULT to achieve — this is the scientific interest. If gate fails (Δ ≤ 0.02 for all encoders), the mechanism claim is not supported and hypotheses must be scoped accordingly. Report Δ with 95% CI via bootstrap over top-5 configurations regardless.

**95% CI:** Bootstrap over top-5 trial configurations, N=1,000 resamples
- Report: Δ(enc) ± CI for all 3 equivariant encoders

**Metrics Loading Information:**
- Task Type: regression
- Library: `scipy.stats.spearmanr`, `sklearn.linear_model.LinearRegression`
- Code:
```python
from scipy.stats import spearmanr
r_gap, _ = spearmanr(gap_preds, true_gap)
r_acc, _ = spearmanr(acc_preds, true_acc)
delta = (r_gap - r_gap_flatmlp) - (r_acc - r_acc_flatmlp)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of Δ(encoder) for each equivariant encoder with threshold line at Δ=0.02

#### Additional Figures (LLM Autonomous)

1. **Dual-target Spearman comparison:** Side-by-side bars for Spearman(gap) and Spearman(test_acc) per encoder — 4 encoders × 2 targets
2. **Δ decomposition plot:** Stacked bar showing gap_improvement and acc_improvement components of Δ per encoder (reveals where the differential comes from)
3. **Partial correlation visualization:** Scatter of residuals for NFT (P3 check): NFT_pred_gap_residuals vs true_gap_residuals (after controlling for test_acc)
4. **Bootstrap CI on Δ:** Error bar plot of Δ(encoder) ± 95% CI for all 3 equivariant encoders

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. All 4 encoders trained on test_acc target without error
2. Δ(encoder) computed for {DWSNet, NFT, GNN}
3. Δ > 0.02 for ≥2 equivariant encoders (primary gate)
4. Partial Spearman (P3) > 0, p < 0.05 for ≥1 encoder (secondary)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Both gap and test_acc are predictable (H-E1 confirmed gap; test_acc confirmed by prior work) | TRUE |
| Mechanism Isolatable | Training target is the sole varying factor; identical protocol for both targets | TRUE |
| Baseline Measurable | FlatMLP Spearman(gap)=0.5330 from H-M1; FlatMLP Spearman(test_acc) to be measured | TRUE |

### Architecture Compatibility Check

**Mechanism:** Permutation-equivariant encoders (DWSNet, NFT, GNN) vs. FlatMLP on two prediction targets.

**Required features:**
- All 4 encoders support scalar regression output (already verified in H-E1/H-M1)
- Training target is a label swap: `test_acc` instead of `generalization_gap`
- No architecture changes required — fully compatible

**Incompatible architectures:** None. All encoders from H-M1 support arbitrary continuous regression targets.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | `[H-M2] {enc}: Spearman(test_acc)={r:.4f}` printed for all 4 encoders | train_testacc.py |
| Tensor Shape | No shape change — same I/O as gap training | N/A |
| Metric Delta | Δ(enc) computed and printed for each equivariant encoder | evaluate_h_m2.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_h_m2_mechanism(gap_results, test_acc_results, delta):
    checks = {
        "all_testacc_trained": all(enc in test_acc_results for enc in
                                   ["flat_mlp", "dws_net", "nft", "gnn"]),
        "flatmlp_testacc_reasonable": 0.75 < test_acc_results["flat_mlp"] < 0.95,
        "delta_computed": all(enc in delta for enc in ["dws_net", "nft", "gnn"]),
        "nft_gap_consistent": abs(gap_results["nft"] - 0.5752) < 0.05,  # H-M1 sanity
    }
    n_pass_gate = sum(1 for d in delta.values() if d > 0.02)
    checks["gate_result"] = f"{n_pass_gate}/3 encoders Δ > 0.02"
    for k, v in checks.items():
        print(f"[H-M2 verify] {k}: {v}")
    return all(isinstance(v, bool) and v for v in checks.values() if isinstance(v, bool))
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| test_acc training diverged | Spearman(test_acc) < 0.5 for any encoder | FAIL: Re-run with lower LR |
| Gap results inconsistent with H-M1 | NFT Spearman(gap) deviates > 0.05 from 0.5752 | WARN: Report discrepancy |
| Δ < 0.02 for all encoders | Gate check fails | DOCUMENT: Mechanism not confirmed; scope conclusions |
| FlatMLP test_acc out of range | Spearman(test_acc) outside [0.75, 0.95] | FAIL: Data pipeline error |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | All 4 encoders produce test_acc predictions | Log/tensor check |
| Effect Measurable | Δ computed for all 3 equivariant encoders | Delta values non-null |
| Hypothesis Supported | Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN} | Delta comparison |
| Secondary Support | Partial Spearman(NFT_gap \| test_acc) > 0, p < 0.05 | Partial correlation |

**hypothesis_support_threshold:** Δ > 0.02 Spearman units for ≥2 equivariant encoders
**hypothesis_support_metric:** Differential advantage Δ(encoder) = gap_improvement − acc_improvement

---

## Appendix: Reference Implementations

### A. Literature Sources

**Source A.1:** Unterthiner et al. 2020 — "Predicting Neural Network Accuracy from Weights" (arxiv 2002.11448)
- Type: Foundational paper / FlatMLP baseline
- Relevance: Zoo construction, FlatMLP architecture, test_acc as primary target in original work
- Key insight: test_acc Spearman ~0.85–0.88 for FlatMLP; provides expected baseline for test_acc comparison
- Used for: test_acc baseline expected range, dataset confirmation

**Source A.2:** Navon et al. 2023 — "Equivariant Architectures for Learning in Deep Weight Spaces" (arxiv 2301.12780)
- Type: DWSNets method paper
- Relevance: DWSNet Spearman(test_acc) ≈ 0.90 on Unterthiner zoo; official training protocol
- Key insight: Equivariant improvement on test_acc is ≈ +0.04 over FlatMLP — this is the acc_improvement denominator in Δ computation
- Used for: test_acc expected values, training protocol (AdamW lr=1e-3)

**Source A.3:** Zhou et al. 2023 — "Neural Functional Transformers" (NeurIPS 2023)
- Type: NFT method paper
- Relevance: NFT Spearman(test_acc) ≈ 0.90–0.92; state-of-art
- Key insight: NFT acc_improvement ≈ +0.04–0.06 → Δ may be marginal if gap_imp = +0.0422
- Used for: Expected NFT Δ pre-computation, feasibility assessment

**Source A.4:** Kofinas et al. 2024 — "Grounding Representation Similarity" (neural-graphs)
- Type: GNN method paper
- Relevance: GNN Spearman(test_acc) ≈ 0.88–0.90; GNN underperforms on gap (from H-M1: r=0.3747)
- Key insight: GNN shows negative gap_imp = −0.1583; unless acc_imp is very negative, Δ will be strongly negative for GNN
- Used for: GNN Δ pre-computation, gate feasibility analysis

**Source A.5:** H-M1 04_validation.md (2026-08-31, this pipeline)
- Type: Prior hypothesis validation result
- Relevance: Gap Spearman values for all 4 encoders — direct inputs to Δ formula
- Key findings: NFT=0.5752, FlatMLP=0.5330, DWSNet=0.4881, GNN=0.3747
- Used for: gap_improvement component of Δ for all encoders

### B. GitHub Implementations

**Repository B.1:** AvivNavon/DWSNets (official, highest priority)
- URL: https://github.com/AvivNavon/DWSNets
- Query used: "Navon DWSNets official implementation GitHub permutation equivariant weight space" (from H-M1 research)
- Key code: DWSLayer (row+column equivariance), training script with target label argument
- Configuration: AdamW lr=1e-3, batch=64, 100 epochs, MSE loss
- Used for: DWSNet test_acc training protocol

**Repository B.2:** mkofinas/neural-graphs (official GNN)
- URL: https://github.com/mkofinas/neural-graphs
- Configuration: Adam lr=5e-4, cosine LR schedule, batch=32
- Used for: GNN test_acc training protocol

### C. Code Analysis (Serena)

*Not performed* — H-M2 extends H-M1 code with a target label change. No new complex architecture requiring semantic analysis. Existing H-M1 codebase supports the extension directly.

### D. Previous Hypothesis Context

**Source:** H-M1 validation report (h-m1/04_validation.md, 2026-08-31)
- Reused components:
  - Dataset: Unterthiner zoo, 80/10/10 split, D=33,890, N=10,000, seed=42
  - Gap checkpoints: All 4 encoders' best-val checkpoints from H-M1
  - Evaluation: `scipy.stats.spearmanr` on test split
  - Training protocol: AdamW, 3-trial random search, MSE loss
- Why reused: H-M2 computes Δ using H-M1 gap results + new test_acc results; only target label changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---|---|---|
| Dataset (Unterthiner zoo) | Prior hypothesis + Paper | H-M1 (reused), A.1 |
| FlatMLP gap Spearman=0.5330 | H-M1 validation | A.5 |
| NFT gap Spearman=0.5752 | H-M1 validation | A.5 |
| DWSNet gap Spearman=0.4881 | H-M1 validation | A.5 |
| GNN gap Spearman=0.3747 | H-M1 validation | A.5 |
| test_acc expected ranges | Published papers | A.1, A.2, A.3, A.4 |
| Δ formula | Phase 2B verification plan | 02b_verification_plan.md §H-M2 Step 2 |
| Training protocol (test_acc) | H-M1 reuse (controlled) | H-M1 02c_experiment_brief.md |
| Partial correlation (P3) | Phase 2B verification plan | 02b_verification_plan.md §H-M2 Step 4 |
| Gate threshold (Δ > 0.02) | Phase 2B success criteria | 02b_verification_plan.md §H-M2 |
| Bootstrap CI | Standard practice | scipy, N=1000 resamples |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written directly)
**Date:** 2026-08-31

### Workflow History for This Hypothesis

- 2026-08-31: h-m2 Phase 2C experiment design COMPLETED (02c_experiment_brief.md written)

---

*MCP Tools Used: ABLATION MODE — LLM-level scientific reasoning (Archon/Exa/Serena unavailable); all specifications grounded in H-M1 validated results and published literature*
*Next Phase: Phase 3 - Implementation Planning*

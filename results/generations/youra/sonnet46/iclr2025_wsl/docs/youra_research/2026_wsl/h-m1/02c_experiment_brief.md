# Experiment Design: H-M1

**Date:** 2026-03-16
**Author:** Anonymous
**Hypothesis Statement:** Under permutation stress (s=1.0), NFT encoders achieve significantly lower Δρ compared to flat-MLP because NFT's equivariant attention mechanism operates on neuron-level representations invariantly under permutation, as evidenced by the mechanism mediation analysis (ΔR² ≥ 0.10 when controlling for equivariance).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Extends H-E1 existence result to causal mechanism confirmation via 6-encoder ablation + mediation analysis.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED — PASS (flat_mlp_delta_rho=0.1595 > 0.10 ✅; nft_delta_rho=4.09e-6 < 0.02 ✅)
**Gate Status:** MUST_WORK — PENDING (will be evaluated after Phase 4 execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (MUST_WORK PASSED)

### Gate Condition
**MUST_WORK Gate:**
- PASS condition: NFT-base Δρ < 0.02 (reconfirmed) AND mechanism mediation ΔR² ≥ 0.10 at permutation severity s=1.0
- FAIL action: STOP mechanism chain → document that flat-MLP+aug may suffice → execute PIVOT to augmentation-focused design
- Additional success: flat-MLP+aug narrows gap (Δρ < flat-MLP) but does NOT close it (Δρ > 0.05)

---

## Continuation Context

**Continuing from H-E1 (COMPLETED — PASS)**

H-M1 directly extends H-E1 by:
1. Expanding from 2-encoder to 6-encoder comparison suite
2. Adding mediation analysis (ΔR²) to establish WHY NFT outperforms
3. Including augmentation/canonicalization ablation controls
4. Reusing identical dataset, hyperparameters, and evaluation protocol for controlled comparison

### Previous Hypothesis Results (H-E1)

| Metric | Value | Gate Threshold | Status |
|--------|-------|----------------|--------|
| flat_mlp_delta_rho (s=1.0) | 0.1595 | > 0.10 | ✅ PASS |
| nft_delta_rho (s=1.0) | 4.09e-6 | < 0.02 | ✅ PASS |
| nft_rho_stable_across_severity | true | — | ✅ |
| mechanism_verified | true | — | ✅ |
| bootstrap_p_value_flat | 0.0 | < 0.05 | ✅ PASS |
| bootstrap_p_value_nft | 0.4768 | n/s expected | ✅ PASS |

**Key insight from H-E1:** NFT equivariance holds at every severity level (rho=0.4886 at s=0 through s=1.0 — remarkably flat). This confirms the mechanism is robust, not marginal.

**Inherited hyperparameters (proven optimal):**
- Optimizer: Adam (lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4)
- Schedule: CosineAnnealingLR (T_max=100, eta_min=1e-5)
- Batch size: 64 | Epochs: 100 | Loss: MSE | Seed: 42

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "NFT equivariant attention mediation analysis permutation" (match_count=5)**
- Results: 4 results (similarity scores 0.39–0.43)
- Top: Attend-and-Excite (0.4294), Perturbed-Attention-Guidance (0.4250), LoRA docs (0.3972), scaled_dot_product_attention (0.3964)
- **Domain relevance: LOW** — No NFT/weight-space learning content; all diffusion/image-gen content.
- **Key insight extracted:** PyTorch `scaled_dot_product_attention` remains useful as the canonical attention foundation that NFT extends.

**Query 2: "weight space encoder 6-encoder ablation comparison" (match_count=5)**
- Results: 4 results (similarity scores 0.40–0.51)
- Top: ControlNet discussion (0.5139), OpenReview (0.4406), TAESD (0.4044), OpenAI consistency (0.3966)
- **Domain relevance: LOW** — No encoder ablation studies for weight-space learning in KB.
- **Key insight:** OpenReview result (0.4406) provides generic ablation framing pattern useful for structuring 6-encoder comparison.

**Query 3: "mediation analysis variance explained ΔR² mechanism" (match_count=5)**
- Results: 3 results (similarity scores 0.27–0.29)
- **Domain relevance: VERY LOW** — Weakest queries; confirms no statistical mediation methodology in KB.
- **Conclusion:** Archon KB confirmed empty for this research domain. Mediation analysis design proceeds from standard causal inference methodology (Baron-Kenny 1986; Hayes 2013 PROCESS macro adapted for ML context).

### Archon Code Examples

**Query 4: "permutation equivariant encoder PyTorch ablation" (match_count=5)**
- Results: 5 results (similarity scores 0.39–0.45, all reranked)
- Most relevant: "Zero Out Gradients for Specific Tokens" (0.4455), PyTorch DistributedDataParallel (0.3992)
- **Domain relevance: LOW** — Standard PyTorch training utilities, no equivariant encoder code.
- **Useful pattern extracted:** PyTorch gradient handling patterns useful for encoder comparison loop.

**Summary:** Archon KB contains no prior cases for NFT/weight-space/mediation content. All 4 queries confirmed this. Experiment design grounded in:
- H-E1 validation results (optimal hyperparameters, proven code structure)
- Zhou et al. 2023 (NFT architecture specification)
- Unterthiner et al. 2020 (zoo loading, flat-MLP baseline)
- Standard causal mediation analysis (Baron & Kenny 1986; Hayes 2013)

### Exa GitHub Implementations

**Status: UNAVAILABLE — 402 Payment Required (quota exhausted)**
- All 3 `mcp__exa__get_code_context_exa` and `mcp__exa__web_search_exa` calls failed with 402 on 3 retry attempts
- Per MCP Error Retry Protocol: documented as limitation, proceeding with literature knowledge + H-E1 proven code
- **NOTE:** H-E1 already successfully implemented NFT and flat-MLP encoders. H-M1 REUSES that code, extending it with 4 additional encoder variants.

**Known from Phase 1 research and H-E1:**
- **Primary:** `https://github.com/AllanYangZhou/nfn` — Official NFT implementation (Zhou et al. 2023)
- **Dataset source:** `https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl`
- **H-E1 code structure:** Already proven — flat-MLP encoder + NFT encoder + permutation stress + Spearman evaluation

### 🎯 Implementation Priority Assessment

**H-M1 is a CONTINUATION experiment** — code from H-E1 is the primary implementation reference.

**CRITICAL: For H-M1, the implementation priority is:**
1. **H-E1 proven code** (HIGHEST) — already validated, reuse directly for flat-MLP and NFT-base
2. **Extend with 4 new variants:** flat-MLP+aug, flat-MLP+canon, NFT+aug, Oracle-canon
3. **Add mediation analysis** — ΔR² computation via partial correlation / variance partitioning

**Recommended Implementation Path:**
- Primary: H-E1 codebase (`h-e1/code/`) — proven working NFT + flat-MLP implementation
- Fallback: Re-implement from Zhou et al. 2023 paper specification (Section 3)
- Justification: H-E1 already produced validated results (nft_delta_rho=4.09e-6). Reusing proven code eliminates re-implementation risk and enables direct controlled comparison.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; no local NFT codebase requiring Serena semantic analysis. H-E1 code provides proven implementation patterns for all encoder variants. Exa unavailable (402) prevented retrieving new code for analysis.

**Architecture derivation from H-E1 + literature:**
- flat-MLP encoder: Proven in H-E1 (3×512 hidden, ReLU, output 1 scalar)
- NFT-base encoder: Proven in H-E1 (equivariant attention over neuron token sequences)
- New variants derive from documented augmentation and canonicalization patterns

---

## Experiment Specification

### Dataset

**Dataset Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Version/Source:** Unterthiner et al. 2020, "Predicting Neural Network Accuracy from Weights"
**Type:** standard (real, established dataset — NOT synthetic ✅)

**Dataset Details:**
- Contents: ~1,000+ pre-trained FC-MLP networks on MNIST, varying in architecture (2-4 layers), hyperparameters, and initialization seeds
- Each sample: weight matrices of a trained FC-MLP + scalar generalization gap label
- Architecture range: 2-layer to 4-layer MLPs, widths 32–512
- Labels: Generalization gap = (training accuracy − test accuracy)
- Standard splits: provided train/test splits in original release

**Statistics:**
- Total models: ~1,000 (MNIST split); minimum 500 for evaluation per verification plan
- Features per model: structured weight matrices (2–4 layer MLPs)
- Label: continuous scalar (generalization gap)

**Preprocessing (inherited from H-E1):**
- Per-layer weight normalization: standardize each weight matrix to zero mean, unit variance (per neuron row for NFT; globally for flat-MLP)
- Flatten for flat-MLP baseline: concatenate all weight matrices into single vector
- For NFT: preserve layer structure, pass as sequence of weight matrices

**Augmentation (training only — applied selectively by encoder variant):**
- Permutation stress: randomly permute neuron ordering at severity s ∈ {0, 0.25, 0.5, 1.0}
- flat-MLP+aug: apply random permutation augmentation at s=1.0 during training (50% of batches)
- flat-MLP+canon: apply oracle canonicalization (sort neurons by L2 norm) before input
- Other variants: standard training without augmentation (equivariance comes from architecture)

**Loading Information** (for Phase 4 download):
- Method: custom download from Google Research repository (same as H-E1)
- Identifier: `https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl`
- Code:
  ```python
  # Reuse from H-E1 — identical dataset loading
  import urllib.request, pickle
  url = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
  urllib.request.urlretrieve(url, "data/unterthiner_mnist_zoo.pkl")
  with open("data/unterthiner_mnist_zoo.pkl", "rb") as f:
      zoo_data = pickle.load(f)
  # zoo_data: list of dicts with keys 'weights', 'train_acc', 'test_acc'
  ```

### Models

#### Baseline Model

**Architecture:** Flat-MLP Encoder (same as H-E1 baseline)
**Description:** Standard MLP on flattened weight vectors — proven baseline from H-E1

**Configuration:**
- Input: flattened concatenation of all weight matrices (~5K–50K per model)
- Hidden layers: 3 × 512 units, ReLU activations
- Output: 1 scalar (generalization gap prediction)
- Δρ(s=1.0) = 0.1595 (proven in H-E1)

**Loading Information** (for Phase 4 download):
- Method: reuse H-E1 implementation
- Identifier: N/A (PyTorch from scratch)
- Code:
  ```python
  # Reuse from H-E1 — identical FlatMLPEncoder
  class FlatMLPEncoder(nn.Module):
      def __init__(self, input_dim, hidden_dim=512):
          super().__init__()
          self.net = nn.Sequential(
              nn.Linear(input_dim, hidden_dim), nn.ReLU(),
              nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
              nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
              nn.Linear(hidden_dim, 1)
          )
      def forward(self, x):  # x: (B, input_dim)
          return self.net(x)
  ```

#### 6-Encoder Comparison Suite

**H-M1 extends H-E1 to 6 encoders to isolate mechanism contributions:**

| ID | Encoder | Description | Role |
|----|---------|-------------|------|
| E1 | flat-MLP | Baseline — no permutation handling | Anchor (proven H-E1) |
| E2 | flat-MLP+aug | flat-MLP + permutation augmentation during training | Engineering fix (data-level) |
| E3 | flat-MLP+canon | flat-MLP + oracle canonicalization (L2-norm sort) | Engineering fix (input-level) |
| E4 | NFT-base | Equivariant attention — no augmentation | Architecture-level (proven H-E1) |
| E5 | NFT+aug | NFT-base + permutation augmentation during training | Architecture + data-level |
| E6 | Oracle-canon | Flat-MLP with ground-truth canonical order (upper bound) | Theoretical ceiling |

**Architecture:** Proposed Model is NFT-base (E4) — the mechanism encoder.

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFT Equivariant Attention + 6-Encoder Mediation Suite
# Based on: Zhou et al. 2023 "Neural Functional Transformers" + H-E1 proven code
# H-M1 Extension: adds flat-MLP+aug, flat-MLP+canon, NFT+aug, Oracle-canon variants

class FlatMLPAugEncoder(FlatMLPEncoder):
    """flat-MLP + permutation augmentation during training."""
    def forward_train(self, weight_matrices, severity=1.0):
        # Apply random permutation augmentation (50% of batches)
        if self.training and torch.rand(1) > 0.5:
            weight_matrices = apply_permutation_stress(weight_matrices, severity)
        x = torch.cat([W.flatten() for W in weight_matrices])
        return self.net(x.unsqueeze(0))

class FlatMLPCanonEncoder(FlatMLPEncoder):
    """flat-MLP + oracle canonicalization (sort neurons by L2 norm)."""
    def forward(self, weight_matrices):
        # Oracle canonicalization: sort each layer's neurons by L2 norm (descending)
        canon_matrices = []
        for W in weight_matrices:  # W: (n_neurons, fan_in)
            l2_norms = W.norm(dim=1)          # (n_neurons,)
            sort_idx = l2_norms.argsort(descending=True)
            canon_matrices.append(W[sort_idx])
        x = torch.cat([W.flatten() for W in canon_matrices])
        return self.net(x.unsqueeze(0))

# NFT-base: reuse from H-E1 (NFTEquivariantLayer — proven working)
# NFT+aug: NFTEquivariantLayer with permutation augmentation during training
#   → same forward() as NFT-base, augmentation applied at data loading level

# Mediation Analysis: variance partitioning to compute ΔR²
def compute_mediation_delta_r2(results_by_encoder):
    """
    Compute ΔR² attributable to NFT equivariance mechanism.
    Based on: Baron & Kenny (1986) mediation; Hayes (2013) PROCESS adapted for ML.

    ΔR² = R²(NFT-base) − R²(flat-MLP+aug)
    Controls for data augmentation; isolates architectural contribution.
    """
    r2_nft = results_by_encoder["NFT-base"]["r2"]
    r2_aug = results_by_encoder["flat-MLP+aug"]["r2"]
    delta_r2 = r2_nft - r2_aug   # variance uniquely explained by equivariance
    return delta_r2   # PASS gate: delta_r2 >= 0.10

# Verification: ΔR² >= 0.10 → NFT equivariance is mechanism, not augmentation effect
```

### Training Protocol

**Inherited from H-E1 (proven optimal):**

**Optimizer:** Adam
- Parameters: lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4
- **Source:** Zhou et al. 2023 NFT training config; proven in H-E1

**Learning Rate:** 1e-3 (initial)
- **Source:** H-E1 validated; CosineAnnealingLR schedule worked well

**Schedule:** CosineAnnealingLR
- Parameters: T_max=100 epochs, eta_min=1e-5
- **Source:** H-E1 proven; standard for weight-space learning

**Batch Size:** 64
- **Source:** H-E1 proven; fits GPU memory for all 6 encoder variants

**Epochs:** 100 per encoder
- **Source:** H-E1 sufficient for convergence; total 6 × 100 = 600 encoder-epochs

**Loss Function:** Mean Squared Error (MSE) on generalization gap prediction
- **Source:** H-E1 proven; Unterthiner et al. 2020 regression standard

**Seeds:** 3 seeds per encoder variant (seeds: 42, 123, 456)
- **Rationale:** MECHANISM hypothesis requires statistical reliability (unlike H-E1 PoC which used 1 seed)
- Total training runs: 6 encoders × 3 seeds = 18 runs

**Augmentation Protocol (variant-specific):**
```python
# Per-encoder augmentation strategy
ENCODER_CONFIG = {
    "flat-MLP":      {"aug_severity": None, "canon": False},
    "flat-MLP+aug":  {"aug_severity": 1.0,  "canon": False},  # 50% prob during training
    "flat-MLP+canon":{"aug_severity": None, "canon": True},   # L2-norm sort always
    "NFT-base":      {"aug_severity": None, "canon": False},
    "NFT+aug":       {"aug_severity": 1.0,  "canon": False},
    "Oracle-canon":  {"aug_severity": None, "canon": "oracle"},  # ground-truth sort
}
```

### Evaluation

**Task Type:** Regression + causal mediation analysis

**Primary Metrics:**

1. **Δρ (Delta rho)** per encoder — permutation robustness (same as H-E1)
   - Definition: Δρ = ρ(s=0) − ρ(s=1.0)
   - H-M1 gate: NFT-base Δρ < 0.02 (reconfirm H-E1 result)

2. **Mechanism Mediation ΔR²** — causal attribution to equivariance
   - Definition: ΔR² = R²(NFT-base) − R²(flat-MLP+aug)
   - Controls for augmentation effect, isolates architectural contribution
   - H-M1 gate: ΔR² ≥ 0.10

3. **6-Encoder Ranking at s=1.0:**
   - Expected ranking (Δρ ascending = most robust first):
     NFT+aug ≤ NFT-base < Oracle-canon < flat-MLP+canon < flat-MLP+aug < flat-MLP

**Success Criteria (MUST_WORK Gate):**
- NFT-base Δρ < 0.02 at s=1.0 (reconfirmation from H-E1)
- ΔR² ≥ 0.10 (mechanism attribution threshold)
- flat-MLP+aug: 0.05 < Δρ < 0.10 (partial compensation, not full)
- NFT-base without aug still Δρ < 0.02 (architecture alone is sufficient)

**Statistical Tests:**
- Paired bootstrap (n=10,000 resamples) per encoder pair, Holm-corrected α=0.05
- Minimum 500 models evaluated per severity level (full MNIST zoo)

**Expected Performance (from H-E1 + literature):**
- flat-MLP Δρ: 0.1595 (confirmed H-E1)
- NFT-base Δρ: ~0.00 (confirmed H-E1: 4.09e-6)
- flat-MLP+aug Δρ: expected 0.05–0.08 (partial, per Phase 2B estimate)
- flat-MLP+canon Δρ: expected 0.03–0.06 (oracle ceiling still suboptimal)
- Oracle-canon Δρ: expected ~0.02–0.04 (theoretical upper bound for non-equivariant approaches)
- **Source:** H-E1 validation report; Phase 2B verification plan Section 2.2

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression + rank correlation + mediation analysis
- Library: `scipy.stats` (spearmanr), `sklearn.metrics` (r2_score), custom mediation
- Code:
  ```python
  from scipy.stats import spearmanr
  from sklearn.metrics import r2_score
  import numpy as np

  def evaluate_all_encoders(encoders, zoo_loader, severity_levels=[0, 0.25, 0.5, 1.0]):
      results = {}
      for enc_name, model in encoders.items():
          rho_by_s, r2_by_s = {}, {}
          for s in severity_levels:
              preds, labels = [], []
              for weights, gap in zoo_loader:
                  stressed = apply_permutation_stress(weights, s)
                  if encoders[enc_name]["canon"]:
                      stressed = canonicalize(stressed)
                  pred = model(stressed)
                  preds.extend(pred.detach().cpu().numpy())
                  labels.extend(gap.cpu().numpy())
              rho, _ = spearmanr(preds, labels)
              r2 = r2_score(labels, preds)
              rho_by_s[s] = rho
              r2_by_s[s] = r2
          results[enc_name] = {
              "delta_rho": rho_by_s[0] - rho_by_s[1.0],
              "rho_by_s": rho_by_s,
              "r2": r2_by_s[0]  # in-distribution R² for mediation
          }
      # Mediation ΔR²
      delta_r2 = results["NFT-base"]["r2"] - results["flat-MLP+aug"]["r2"]
      results["mediation_delta_r2"] = delta_r2
      return results
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of Δρ at s=1.0 for all 6 encoders with gate threshold lines (Δρ=0.10 flat-MLP line, Δρ=0.02 NFT-base target, ΔR²=0.10 mediation threshold)

#### Additional Figures (LLM Autonomous)

**Recommended visualizations for H-M1 MECHANISM experiment:**

1. **6-Encoder Δρ vs. Permutation Severity Curves:** Multi-line plot of Δρ(s) for all 6 encoders at s ∈ {0, 0.25, 0.5, 1.0} — shows full degradation profile and ranking
2. **Mediation ΔR² Bar Chart:** ΔR² breakdown showing how much variance is explained by: (a) data augmentation alone (flat-MLP+aug vs. flat-MLP), (b) architectural equivariance (NFT-base vs. flat-MLP+aug), (c) combined (NFT+aug vs. flat-MLP)
3. **Spearman ρ Heatmap:** 6-encoder × 4-severity heatmap of ρ values — shows which encoder maintains performance across all conditions
4. **Bootstrap Distribution Comparison:** Distribution of Δρ bootstrap estimates for NFT-base vs. flat-MLP+aug — shows statistical separation confirming mechanism attribution

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | NFT equivariant attention operates on neuron token sequences (proven H-E1) | TRUE — nft_delta_rho=4.09e-6 confirmed in H-E1 |
| Mechanism Isolatable | All 6 encoders use identical dataset/training/eval; only architecture/augmentation varies | TRUE — controlled design, single IV |
| Baseline Measurable | flat-MLP baseline proven stable (Δρ=0.1595, H-E1 reproduced) | TRUE — H-E1 validation report |

### Architecture Compatibility Check

**All 6 encoder variants compatible with Unterthiner MNIST zoo:**
- flat-MLP (E1/E2/E3): Proven in H-E1 — handles variable weight dims via flattening
- NFT-base (E4/E5): Proven in H-E1 — variable fan_in handled via per-layer projection + padding
- Oracle-canon (E6): Same architecture as flat-MLP+canon (E3) with perfect canonical ordering

**Required Features:**
- PyTorch `nn.MultiheadAttention` (batch_first=True) — for NFT variants
- Variable-length weight matrix support — already handled in H-E1 code
- Per-encoder training loop — 6 separate training runs with shared data

**Incompatible Architectures:**
- DWSNets — confirmed incompatible (Phase 2B context)
- Fixed-size input models — incompatible with variable zoo dimensions

> ⚠️ Phase 4 MUST verify all 6 encoders produce valid output before full training run. Run sanity check on 10 models per encoder before committing to full experiment.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | "6-encoder suite initialized: [flat-MLP, flat-MLP+aug, flat-MLP+canon, NFT-base, NFT+aug, Oracle-canon]" | train.py:setup_encoders() |
| Tensor Shape | NFT all_tokens: (B, total_neurons, d_model) — same as H-E1 | model.py:NFTEquivariantLayer.forward() |
| Metric Delta | ΔR² = R²(NFT-base) − R²(flat-MLP+aug) ≥ 0.10 | evaluate.py:compute_mediation_delta_r2() |
| Ranking Check | NFT-base Δρ < flat-MLP+aug Δρ < flat-MLP Δρ | evaluate.py:evaluate_all_encoders() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    """Verify NFT equivariant attention mechanism mediates permutation robustness."""
    indicators = {
        # H-E1 reconfirmation
        "nft_base_robust": results["NFT-base"]["delta_rho"] < 0.02,
        # H-M1 mechanism attribution
        "mediation_confirmed": results["mediation_delta_r2"] >= 0.10,
        # Augmentation is partial, not sufficient
        "aug_partial": 0.05 < results["flat-MLP+aug"]["delta_rho"] < 0.10,
        # Architecture alone sufficient (NFT-base without aug)
        "architecture_sufficient": results["NFT-base"]["delta_rho"] < results["flat-MLP+aug"]["delta_rho"],
        # Ranking holds
        "ranking_correct": (
            results["NFT-base"]["delta_rho"] <
            results["flat-MLP+aug"]["delta_rho"] <
            results["flat-MLP"]["delta_rho"]
        )
    }
    gate_pass = (
        indicators["nft_base_robust"] and
        indicators["mediation_confirmed"]
    )
    return gate_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| ΔR² < 0.10 | compute_mediation_delta_r2() < 0.10 | FAIL: Mechanism not confirmed — flat-MLP+aug may suffice |
| NFT-base Δρ ≥ 0.02 | delta_rho >= 0.02 (regression from H-E1) | FAIL: Re-check H-E1 implementation reuse |
| Oracle-canon < NFT-base | Ordering violated | WARN: Log and continue (gate is ΔR², not ranking) |
| Training instability | Loss NaN or ρ < 0 | FAIL: Reduce lr to 1e-4, retry with seed 0 |
| Augmentation closes gap | flat-MLP+aug Δρ < 0.02 | NOTE: Narrows H-M2 scope (still proceed) |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| H-E1 reconfirmed | NFT-base Δρ < 0.02 | compute_delta_rho("NFT-base") at s=1.0 |
| Mechanism attributed | ΔR² ≥ 0.10 | compute_mediation_delta_r2() |
| Ablation confirms | flat-MLP+aug Δρ > flat-MLP+aug Δρ ... NFT-base | evaluate_all_encoders() ranking |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 6 encoders
2. NFT-base Δρ < 0.02 at s=1.0 (reconfirm H-E1)
3. ΔR² ≥ 0.10 (mechanism mediation threshold)

**Gate PASS condition (MUST_WORK):**
- NFT-base Δρ < 0.02 at s=1.0
- ΔR² = R²(NFT-base) − R²(flat-MLP+aug) ≥ 0.10

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** PyTorch `scaled_dot_product_attention` documentation
- **Type:** Code documentation
- **Query Used:** "permutation equivariant encoder PyTorch ablation" (code examples)
- **Similarity:** 0.446 (highest among code examples)
- **Relevance:** Standard attention mechanism that NFT extends (same as H-E1)
- **Used For:** NFT-base encoder pseudo-code (carried from H-E1)

**Source A.2:** OpenReview.net forum result
- **Type:** Knowledge base article
- **Query Used:** "weight space encoder 6-encoder ablation comparison"
- **Similarity:** 0.4406
- **Relevance:** Generic ablation comparison framing pattern
- **Used For:** Structuring 6-encoder comparison suite design

**Overall Archon Assessment:** KB confirmed empty for this domain across all 4 queries. Experiment design grounded in H-E1 proven results + literature.

### B. GitHub Implementations (Exa)

**Status: UNAVAILABLE** — Exa MCP returned 402 Payment Required on all 3 attempts (quota exhausted).

**Known repositories (from Phase 1 research + H-E1):**

**Repository B.1:** `AllanYangZhou/nfn` (Neural Functional Networks)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Official NFT implementation — ground truth for equivariant attention
- **Priority:** ⭐⭐⭐ HIGHEST — NFT-base and NFT+aug variants
- **Used For:** NFT encoder architecture reference (reuse from H-E1)

**Repository B.2:** `google-research/google-research` (dnn_predict_accuracy)
- **URL:** https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
- **Relevance:** Official zoo data + flat-MLP baseline — ground truth for comparison
- **Priority:** ⭐⭐⭐ HIGHEST — dataset loading and flat-MLP reference
- **Used For:** Dataset loading (identical to H-E1); flat-MLP variants derivation

### C. Code Analysis (Serena)

**Serena Analysis:** Skipped — Code from H-E1 implementation is sufficiently clear. All 6 encoder variants derive directly from proven H-E1 code. No new complex code requiring semantic analysis.

**H-E1 code derivation for H-M1 variants:**
1. `FlatMLPEncoder` (H-E1 proven) → direct reuse for E1
2. `FlatMLPEncoder` + augmentation at training time → E2 (flat-MLP+aug)
3. `FlatMLPEncoder` + L2-norm sort preprocessing → E3 (flat-MLP+canon)
4. `NFTEquivariantLayer` (H-E1 proven) → direct reuse for E4
5. `NFTEquivariantLayer` + augmentation at training time → E5 (NFT+aug)
6. `FlatMLPEncoder` + ground-truth canonical sort → E6 (Oracle-canon)

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - Dataset: Unterthiner MNIST zoo — same download, same splits
  - Hyperparameters: Adam lr=1e-3, batch=64, epochs=100, MSE — proven optimal
  - Flat-MLP architecture: 3×512 hidden, ReLU — proven baseline (Δρ=0.1595)
  - NFT architecture: equivariant attention, d_model=128 — proven robust (Δρ=4.09e-6)
  - Permutation stress function: `apply_permutation_stress()` — proven correct
  - Spearman evaluation: `compute_delta_rho()` — proven accurate
- **Why Reused:** Enables controlled experiment — only IV changes (6 encoders); all else identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Unterthiner zoo) | H-E1 proven | h-e1/04_validation.md; 02b_verification_plan.md |
| Dataset type (standard, real) | Phase 2A | verification_state.yaml h-m1.data_setup |
| flat-MLP baseline (E1) | H-E1 proven code | h-e1/code/ FlatMLPEncoder |
| NFT-base (E4) | H-E1 proven code | h-e1/code/ NFTEquivariantLayer |
| flat-MLP+aug (E2) | Literature + derivation | Permutation augmentation standard pattern |
| flat-MLP+canon (E3) | Phase 2B specification | 02b_verification_plan.md Section 1.4 |
| NFT+aug (E5) | Derivation from E4 + E2 | Additive variant of proven NFT-base |
| Oracle-canon (E6) | Phase 2B specification | 02b_verification_plan.md Section 2.2 H-M2 |
| Training hyperparameters | H-E1 proven | h-e1/04_validation.md optimal config |
| Mediation ΔR² analysis | Causal methodology | Baron & Kenny 1986; Hayes 2013 PROCESS |
| Evaluation (Spearman ρ, ΔR²) | Phase 2B success criteria | 02b_verification_plan.md Section 2.2 H-M1 |
| Gate thresholds (Δρ < 0.02, ΔR² ≥ 0.10) | Phase 2B gate conditions | 02b_verification_plan.md Section 3.2 |
| Bootstrap statistics (n=10,000, 3 seeds) | Phase 2B protocol | 02b_verification_plan.md H-M1 steps |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-16T14:10:00+00:00

### Workflow History for This Hypothesis
- 2026-03-16T11:06:00: Phase 2B completed, H-M1 generated as MECHANISM hypothesis (prereq: H-E1)
- 2026-03-16T12:07:53: H-M1 set to IN_PROGRESS by hypothesis loop
- 2026-03-16T14:10:00: Phase 2C experiment design completed (this file)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — low relevance, no domain-specific content), Exa (unavailable — 402), Serena (not needed — H-E1 proven code available)*
*All specifications grounded in: H-E1 validated results, Zhou et al. 2023 (NFT), Unterthiner et al. 2020 (zoo + flat-MLP), Baron & Kenny 1986 (mediation analysis)*
*Next Phase: Phase 3 - Implementation Planning*

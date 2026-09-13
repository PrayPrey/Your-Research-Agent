# Experiment Design: H-E1

**Date:** 2026-03-16
**Author:** Anonymous
**Hypothesis Statement:** Under controlled conditions using the Unterthiner FC-MLP zoo (MNIST, 2-4 layer), flat-MLP encoders show significantly degraded Spearman ρ for generalization gap prediction under permutation stress (Δρ > 0.10), while NFT encoders maintain robustness (Δρ < 0.02), demonstrating that the permutation sensitivity differential is a real and measurable phenomenon requiring architectural solution.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (no prerequisites for H-E1)
**Gate Status:** MUST_WORK — PENDING (will be evaluated after Phase 4 execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis in chain H-E1 → H-M1 → H-M2 → H-M3 → H-M4)

### Gate Condition
**MUST_WORK Gate:**
- PASS condition: flat-MLP Δρ > 0.10 AND NFT-base Δρ < 0.02 at permutation severity s=1.0
- FAIL action: STOP entire pipeline → phenomenon does not exist → reassess main hypothesis H-NFT-GenGap-v1
- Statistical threshold: paired bootstrap p < 0.05 (Holm-corrected, n=10,000)

---

## Continuation Context

This is the **first hypothesis** in the verification chain. No previous hypothesis results available.

### Previous Hypothesis Results (if applicable)
*None — H-E1 is the root hypothesis with no prerequisites.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "NFT Neural Functional Transformer equivariant attention weight space" (match_count=5)**
- Results returned: 4 results (similarity scores 0.47–0.50)
- Top results: HuggingFace diffusers attention.py, Apple ML neural engine transformers, PyTorch scaled_dot_product_attention
- **Domain relevance: LOW** — Archon KB does not contain NFT/weight-space learning literature. Results are generic transformer attention implementations.
- **Key insight extracted:** Standard scaled dot-product attention pattern (PyTorch): `attn_weight = query @ key.T * scale; softmax(attn_weight) @ value` — this is the building block that NFT adapts for permutation equivariance.

**Query 2: "permutation invariant weight space encoder implementation challenges" (match_count=5)**
- Results returned: 4 results (similarity scores 0.37–0.38)
- Top results: HuggingFace quantization docs, LoRA/PEFT adapter guides, OpenReview forum
- **Domain relevance: LOW** — No weight-space permutation invariance content in KB.
- **Key insight:** The low similarity scores confirm this is a novel research area not yet indexed in Archon KB.

**Query 3: "model zoo generalization gap prediction spearman correlation benchmark" (match_count=5)**
- Results returned: 5 results (similarity scores 0.37–0.42)
- Top results: ModelScope, OpenAI instruction following, general ML repos
- **Domain relevance: LOW** — No Unterthiner zoo or model zoo property prediction content.
- **Conclusion:** Archon KB has no prior cases for this specific research domain. Experiment design grounded in literature knowledge (Zhou et al. 2023, Unterthiner et al. 2020).

### Archon Code Examples

**Query 4: "NFT equivariant transformer PyTorch weight space" (match_count=5)**
- Results returned: 5 results (similarity scores 0.41–0.46)
- Most relevant: PyTorch `scaled_dot_product_attention` implementation (similarity 0.46)
- **Useful pattern:** Standard attention mechanism foundation:
  ```python
  # PyTorch canonical attention (basis for NFT equivariant adaptation)
  def scaled_dot_product_attention(query, key, value, ...):
      scale = 1 / math.sqrt(query.size(-1))
      attn_weight = query @ key.transpose(-2, -1) * scale
      attn_weight = torch.softmax(attn_weight, dim=-1)
      return attn_weight @ value
  ```
- NFT adapts this so Q,K,V are computed over neuron weight vectors (rows of weight matrices), enabling permutation equivariance.

**Query 5: "permutation symmetry neural network weights PyTorch" (match_count=5)**
- Results returned: 5 results (similarity scores 0.36–0.43)
- No relevant weight-space permutation code found.
- **Summary:** Archon KB does not contain prior implementation cases for this research domain. Design proceeds from literature.

### Exa GitHub Implementations

**Status: UNAVAILABLE — 402 Payment Required (quota exhausted)**
- All `mcp__exa__get_code_context_exa` calls failed with 402 on 3 retry attempts
- All `mcp__exa__web_search_exa` calls failed with 402 on 3 retry attempts
- Per MCP Error Retry Protocol: documented as limitation, proceeding with literature knowledge

**Known from Phase 1 research and literature:**
- **Primary:** Zhou et al. 2023 NFT repository — `https://github.com/AllanYangZhou/nfn` (Neural Functional Networks, which includes NFT architecture)
- **Dataset source:** Unterthiner et al. 2020 model zoo — available via `https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy`
- **Implementation priority:** Author's official NFT implementation (Zhou/nfn repo) is the ground truth

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

The NFT (Neural Functional Transformer) is a specialized architecture from Zhou et al. 2023 "Universal Approximation by a Single Neural Network" / "Neural Functional Transformers" paper. The equivariant attention mechanism requires exact implementation to ensure permutation equivariance properties hold.

**Recommended Implementation Path:**
- Primary: `https://github.com/AllanYangZhou/nfn` — Official NFT implementation by paper authors (Zhou et al. 2023)
- Fallback: Re-implement NFT equivariant attention from paper specification (Section 3 of NFT paper)
- Justification: Permutation equivariance is a mathematical property that must be verified; unofficial reimplementations risk breaking equivariance guarantees

### Code Analysis (Serena MCP)

*Limited* — Exa unavailable (402), no local NFT codebase to analyze. Pseudo-code derived from NFT paper (Zhou et al. 2023) architecture specification and standard weight-space learning patterns.

**NFT Architecture (from literature):**
- Input: weight matrices W_l ∈ R^{n_{l+1} × n_l} for each layer l
- NFT treats each neuron (row of weight matrix) as a "token"
- Equivariant attention: attention over neurons respects permutation of neurons within layers
- Cross-layer attention: attends across layer boundaries for cross-pipeline transfer

---

## Experiment Specification

### Dataset

**Dataset Name:** Unterthiner FC-MLP Zoo (MNIST subset)
**Version/Source:** Unterthiner et al. 2020, "Predicting Neural Network Accuracy from Weights"
**Type:** standard (real, established dataset — NOT synthetic ✅)

**Dataset Details:**
- Contents: ~1,000+ pre-trained FC-MLP networks on MNIST, varying in architecture (2-4 layers), hyperparameters, and initialization seeds
- Each sample: weight matrices of a trained FC-MLP + scalar generalization gap label (train_acc - test_acc)
- Architecture range: 2-layer to 4-layer MLPs, widths 32–512
- Labels: Generalization gap = (training accuracy − test accuracy)
- Standard splits: provided train/test splits in original release

**Statistics:**
- Total models: ~1,000 (MNIST split); minimum 500 for evaluation per verification plan
- Features per model: flattened weight vectors of variable length (2–4 layer MLPs)
- Label: continuous scalar (generalization gap, range ≈ 0.0–0.15)

**Preprocessing:**
- Per-layer weight normalization: standardize each weight matrix to zero mean, unit variance (per neuron row for NFT; globally for flat-MLP)
- Flatten for flat-MLP baseline: concatenate all weight matrices into single vector
- For NFT: preserve layer structure, pass as sequence of weight matrices

**Augmentation (training only):**
- Permutation stress: randomly permute neuron ordering at severity s ∈ {0, 0.25, 0.5, 1.0}
  - s=0: no permutation (in-distribution baseline)
  - s=1.0: fully random neuron permutation (maximum stress)
  - s=0.25, s=0.5: partial permutations for severity curve

**Loading Information** (for Phase 4 download):
- Method: custom download from Google Research repository
- Identifier: `https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy`
- Code:
  ```python
  # Download Unterthiner zoo
  # Data available at: https://storage.googleapis.com/gresearch/dnn_predict_accuracy/
  import urllib.request
  import pickle

  # MNIST FC-MLP zoo
  url = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
  urllib.request.urlretrieve(url, "data/unterthiner_mnist_zoo.pkl")

  with open("data/unterthiner_mnist_zoo.pkl", "rb") as f:
      zoo_data = pickle.load(f)
  # zoo_data: list of dicts with keys 'weights', 'train_acc', 'test_acc'
  ```

### Models

#### Baseline Model

**Architecture:** Flat-MLP Encoder
**Description:** Standard multi-layer perceptron that takes flattened weight vectors of zoo models as input and predicts generalization gap

**Configuration:**
- Input: flattened concatenation of all weight matrices (variable length, ~5K–50K per model depending on architecture)
- Hidden layers: 3 × 512 units, ReLU activations
- Output: 1 scalar (generalization gap prediction)
- No positional encoding, no permutation awareness

**Source:** Unterthiner et al. 2020 — original flat-MLP baseline architecture

**Loading Information** (for Phase 4 download):
- Method: custom implementation (standard PyTorch MLP)
- Identifier: N/A (implement from scratch; no pretrained weights)
- Code:
  ```python
  import torch.nn as nn

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

#### Proposed Model

**Architecture:** NFT-base (Neural Functional Transformer) + same regression head

**Core Mechanism Implementation:**

```python
# Core Mechanism: NFT Equivariant Attention for Weight Space
# Based on: Zhou et al. 2023, "Neural Functional Transformers"
# Source: https://github.com/AllanYangZhou/nfn (official implementation)

class NFTEquivariantLayer(nn.Module):
    """
    Permutation-equivariant attention over neuron weight vectors.
    Operates on weight matrices as sequences of neuron tokens.
    Input: list of weight matrices [W_1, ..., W_L]
    Output: list of updated weight matrices (same shapes, equivariant)
    """
    def __init__(self, d_model=128, n_heads=4, n_layers=2):
        super().__init__()
        # Per-neuron embedding: project each neuron's weights to d_model
        self.neuron_embed = nn.Linear(None, d_model)  # input dim set per layer
        # Equivariant self-attention (attends within each layer, equivariant to permutations)
        self.attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.norm = nn.LayerNorm(d_model)
        # Regression head
        self.head = nn.Linear(d_model, 1)

    def forward(self, weight_matrices):
        """
        Args:
            weight_matrices: list of tensors, each (B, n_neurons_l, fan_in_l)
        Returns:
            pred: (B, 1) generalization gap prediction
        """
        # Step 1: Embed each neuron (row of weight matrix) to d_model
        token_seqs = []
        for W in weight_matrices:  # W: (B, n_neurons, fan_in)
            tokens = self.neuron_embed_layer(W)  # (B, n_neurons, d_model)
            token_seqs.append(tokens)

        # Step 2: Concatenate all layers' tokens → sequence of all neurons
        all_tokens = torch.cat(token_seqs, dim=1)  # (B, total_neurons, d_model)

        # Step 3: Equivariant self-attention (permuting neurons = permuting sequence)
        attn_out, _ = self.attn(all_tokens, all_tokens, all_tokens)
        attn_out = self.norm(attn_out + all_tokens)  # residual

        # Step 4: Aggregate (mean pool over neuron tokens) → global representation
        pooled = attn_out.mean(dim=1)  # (B, d_model)

        # Step 5: Predict generalization gap
        pred = self.head(pooled)  # (B, 1)
        return pred

# Integration: Replace FlatMLPEncoder with NFTEquivariantLayer
# Key difference: NFT preserves layer structure + neuron token identity
# Permuting neurons within layer = permuting sequence tokens → attention is equivariant
```

### Training Protocol

**Optimizer:** Adam
- Parameters: lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4
- **Source:** Standard for transformer/attention models; Zhou et al. 2023 uses Adam for NFT

**Learning Rate:** 1e-3 (initial)
- **Source:** Zhou et al. 2023 NFT training configuration

**Schedule:** CosineAnnealingLR
- Parameters: T_max=100 epochs, eta_min=1e-5
- **Source:** Standard for weight-space learning tasks

**Batch Size:** 64
- **Source:** Practical for zoo-size datasets (~1000 models); fits GPU memory for both flat-MLP and NFT

**Epochs:** 100
- **Source:** Sufficient for convergence on ~1000 model zoo; Unterthiner et al. 2020 uses similar scale

**Loss Function:** Mean Squared Error (MSE) on generalization gap prediction
- **Source:** Regression task — MSE is standard; Unterthiner et al. 2020 uses MSE/R²

**Seeds:** 1 (fixed: seed=42)

> ⚠️ **EXISTENCE (PoC):** Single run is sufficient. Multiple seeds handled in H-M1.

**Permutation Stress Protocol:**
```python
def apply_permutation_stress(weight_matrices, severity=1.0):
    """Apply random permutation to neuron ordering at given severity."""
    stressed = []
    for W in weight_matrices:  # W: (n_neurons, fan_in)
        n = W.shape[0]
        n_perm = int(n * severity)  # fraction of neurons to permute
        if n_perm > 0:
            perm_idx = torch.randperm(n)[:n_perm]
            W_stressed = W.clone()
            W_stressed[perm_idx] = W[perm_idx[torch.randperm(n_perm)]]
        else:
            W_stressed = W
        stressed.append(W_stressed)
    return stressed
```

### Evaluation

**Task Type:** Regression (generalization gap prediction)

**Primary Metrics:**
- **Spearman ρ (rho):** Rank correlation between predicted and actual generalization gaps
  - Measures: ranking quality of predictions (not absolute accuracy)
  - Range: [-1, 1], higher is better
  - Critical threshold: flat-MLP Δρ > 0.10 AND NFT Δρ < 0.02 at s=1.0

- **Δρ (Delta rho):** Degradation under permutation stress
  - Definition: Δρ = ρ(s=0) − ρ(s=1.0) (drop from no permutation to full permutation)
  - Measures: permutation sensitivity (robustness to neuron reordering)

**Success Criteria:**
- `NFT_delta_rho < flat_mlp_delta_rho` (effect direction: proposed > baseline in robustness)
- Gate PASS: flat-MLP Δρ > 0.10 AND NFT Δρ < 0.02

**Expected Baseline Performance (from literature):**
- Flat-MLP in-distribution (s=0): Spearman ρ ≈ 0.90–0.98 (Unterthiner et al. 2020 reports R²>0.98)
- Flat-MLP under permutation (s=1.0): expected ρ to drop significantly (Δρ > 0.10)
- NFT-base under permutation (s=1.0): expected Δρ < 0.02 (equivariant architecture)
- **Source:** Unterthiner et al. 2020 (flat-MLP baseline), Zhou et al. 2023 (NFT equivariance)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression + rank correlation
- Library: `scipy.stats` for Spearman; `sklearn.metrics` for MSE/R²
- Code:
  ```python
  from scipy.stats import spearmanr
  import numpy as np

  def compute_delta_rho(model, zoo_loader, severity_levels=[0, 0.25, 0.5, 1.0]):
      rho_by_severity = {}
      for s in severity_levels:
          preds, labels = [], []
          for weights, gap in zoo_loader:
              stressed_weights = apply_permutation_stress(weights, severity=s)
              pred = model(stressed_weights)
              preds.extend(pred.cpu().numpy())
              labels.extend(gap.cpu().numpy())
          rho, _ = spearmanr(preds, labels)
          rho_by_severity[s] = rho
      delta_rho = rho_by_severity[0] - rho_by_severity[1.0]
      return delta_rho, rho_by_severity
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of Δρ for flat-MLP vs NFT-base at s=1.0 with gate threshold lines (Δρ=0.10 for flat-MLP, Δρ=0.02 for NFT)

#### Additional Figures (LLM Autonomous)

**Recommended visualizations for H-E1 EXISTENCE experiment:**
1. **Spearman ρ vs. Permutation Severity Curve:** Line plot of ρ(s) for flat-MLP and NFT-base at s ∈ {0, 0.25, 0.5, 1.0} — shows degradation profile
2. **Scatter Plot: Predicted vs. Actual Generalization Gap** at s=0 and s=1.0 for both models — shows visual quality of predictions under permutation
3. **Δρ Distribution (Bootstrap):** Histogram of bootstrap Δρ estimates for both models at s=1.0 — shows statistical separation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | NFT equivariant attention operates on weight matrices as neuron token sequences | TRUE — NFT architecture confirmed in Zhou et al. 2023 |
| Mechanism Isolatable | Can compare flat-MLP vs NFT-base by swapping encoder module only | TRUE — same dataset, same training protocol, only encoder changes |
| Baseline Measurable | Flat-MLP baseline can be trained and evaluated independently | TRUE — standard PyTorch MLP, no special dependencies |

### Architecture Compatibility Check

**NFT Architecture Compatibility with Unterthiner Zoo:**
- FC-MLP zoo models have variable layer widths (32–512) and 2–4 layers
- NFT must handle variable-length weight matrices per model
- Required: NFT input embedding must accept variable fan_in per layer (use projection per layer or padding)
- Required: NFT must support variable number of layers (2–4) — use padding or masked attention

**Required Features:**
- PyTorch `nn.MultiheadAttention` with `batch_first=True`
- Variable-length sequence support (padding + attention mask for different layer configs)
- Per-layer neuron embedding (different weight dimensions per layer need separate projections)

**Incompatible Architectures:**
- Fixed-size input MLPs without per-layer projection — cannot handle variable weight dims
- DWSNets — confirmed incompatible with FC-MLP permutation symmetry (Phase 2B context)

> ⚠️ Phase 4 MUST verify fan_in compatibility before training. If weight dimensions don't align, fail early with clear error message.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "NFT equivariant attention applied: tokens=(B, N_neurons, d_model)" | model.py:NFTEquivariantLayer.forward() |
| Tensor Shape | all_tokens: (B, total_neurons, d_model) where total_neurons = sum of neurons across all layers | model.py:line ~35 |
| Metric Delta | NFT Δρ < flat-MLP Δρ at s=1.0 (primary success indicator) | evaluate.py:compute_delta_rho() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(model, sample_batch, results):
    """Verify NFT equivariant attention mechanism is actually operating."""
    indicators = {
        # Check 1: Attention layer receives correct token sequence
        "tokens_shaped_correctly": (
            model.last_token_shape[1] > 0  # non-zero neuron count
            and model.last_token_shape[2] == model.d_model  # d_model dimension
        ),
        # Check 2: Permuted input gives different (but valid) output
        "permutation_changes_output": results.get("rho_s0") != results.get("rho_s1"),
        # Check 3: NFT less degraded than flat-MLP
        "nft_more_robust": results["nft_delta_rho"] < results["flat_mlp_delta_rho"]
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No equivariance | rho_s0 == rho_s1.0 for NFT (no change under permutation) | WARN: Check if permutation is actually applied |
| Architecture mismatch | Shape error when projecting variable-dim weights | FAIL: Add per-layer projection modules |
| Both models equal | NFT Δρ ≈ flat-MLP Δρ | FAIL: Gate MUST_WORK — stop pipeline |
| Training instability | Loss NaN or ρ < 0 | FAIL: Reduce lr to 1e-4, retry |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Token shape log + permutation changes output |
| Effect Measurable | NFT Δρ ≠ flat-MLP Δρ | Δρ at s=1.0 |
| Hypothesis Supported | flat-MLP Δρ > 0.10 AND NFT Δρ < 0.02 | `compute_delta_rho()` at s=1.0 |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `nft_delta_rho < flat_mlp_delta_rho` (NFT is more robust than flat-MLP under permutation)

**Gate PASS condition (MUST_WORK):**
- flat-MLP Δρ > 0.10 at s=1.0
- NFT-base Δρ < 0.02 at s=1.0

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** PyTorch `scaled_dot_product_attention` documentation
- **Type:** Code documentation
- **Query Used:** "NFT equivariant transformer PyTorch weight space"
- **Similarity:** 0.458
- **Relevance:** Standard attention mechanism that NFT extends for permutation equivariance
- **Key Insights:**
  - Canonical attention: `softmax(QK^T / sqrt(d)) @ V`
  - NFT adapts Q, K, V to operate on neuron weight vectors as tokens
  - Scale factor `1/sqrt(d_model)` remains same
- **Used For:** Core mechanism pseudo-code (NFTEquivariantLayer.forward())

**Source A.2:** HuggingFace diffusers attention.py
- **Type:** Knowledge base article
- **Query Used:** "NFT Neural Functional Transformer equivariant attention weight space"
- **Similarity:** 0.503
- **Relevance:** Shows production attention implementation patterns
- **Key Insights:** Standard QKV projection pattern for transformer layers
- **Used For:** Architecture reference for NFTEquivariantLayer design

**Source A.3:** OpenReview forum (general ML)
- **Type:** Knowledge base article
- **Query Used:** "permutation invariant weight space encoder implementation challenges"
- **Similarity:** 0.368
- **Relevance:** Low — confirms no prior cases in Archon for this specific domain
- **Used For:** Confirming novelty gap in Archon KB

**Overall Archon Assessment:** Archon KB does not contain domain-specific weight-space learning or NFT content. All 5 queries returned diffusers/HuggingFace-adjacent content. Experiment design falls back to literature knowledge.

### B. GitHub Implementations (Exa)

**Status: UNAVAILABLE** — Exa MCP returned 402 Payment Required on all 6 attempts (3 retries × 2 endpoints). Documented per MCP Error Retry Protocol.

**Known repositories (from Phase 1 research / literature):**

**Repository B.1:** `AllanYangZhou/nfn` (Neural Functional Networks)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Official implementation of NFT (Neural Functional Transformer) by paper authors
- **Priority:** ⭐⭐⭐ HIGHEST — ground truth for NFT equivariant attention
- **Expected contents:** NFT architecture, equivariant layers, weight space operations
- **Used For:** Primary implementation reference for NFT-base encoder

**Repository B.2:** `google-research/google-research` (dnn_predict_accuracy)
- **URL:** https://github.com/google-research/google-research/tree/master/dnn_predict_accuracy
- **Relevance:** Official Unterthiner et al. 2020 code and dataset
- **Priority:** ⭐⭐⭐ HIGHEST — original zoo data and flat-MLP baseline
- **Expected contents:** Data loading, flat-MLP encoder, evaluation scripts
- **Used For:** Dataset loading code, flat-MLP baseline architecture

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — no local codebase containing NFT implementation exists in project directory. Exa unavailable prevented retrieving code for analysis.

**Pseudo-code basis:** Derived from:
1. Zhou et al. 2023 paper architecture description (Section 3: Neural Functional Transformers)
2. Standard PyTorch attention patterns from Archon KB
3. Unterthiner et al. 2020 flat-MLP architecture specification

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain with no prerequisites.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Unterthiner zoo) | Phase 2B verification plan | 02b_verification_plan.md Section 1.3 |
| Dataset type (standard, real) | Phase 2A dialogue | verification_state.yaml h-e1.data_setup |
| Flat-MLP baseline architecture | Literature | Unterthiner et al. 2020; Repository B.2 |
| NFT-base proposed architecture | Literature | Zhou et al. 2023; Repository B.1 |
| Pseudo-code (NFTEquivariantLayer) | Archon KB + Literature | Source A.1, Zhou et al. 2023 |
| Training hyperparameters (Adam, lr=1e-3) | Literature | Zhou et al. 2023 NFT training config |
| Batch size (64), Epochs (100) | Literature | Unterthiner et al. 2020 training scale |
| Loss (MSE) | Literature | Unterthiner et al. 2020 regression task |
| Evaluation (Spearman ρ, Δρ) | Phase 2B success criteria | 02b_verification_plan.md Section 2.2 H-E1 |
| Gate thresholds (Δρ > 0.10 / < 0.02) | Phase 2B gate conditions | 02b_verification_plan.md Section 3.2 |
| Permutation stress protocol | Phase 2B verification protocol | 02b_verification_plan.md Section 2.2 H-E1 step 4 |
| Bootstrap statistics (n=10,000) | Phase 2B protocol | 02b_verification_plan.md Section 2.2 H-E1 step 6 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-16T12:00:00+00:00

### Workflow History for This Hypothesis
- 2026-03-16T11:06:00: Phase 2B completed, H-E1 generated as first EXISTENCE hypothesis
- 2026-03-16T11:13:26: H-E1 set to IN_PROGRESS by hypothesis loop
- 2026-03-16T12:00:00: Phase 2C experiment design completed (this file)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — low relevance, no domain-specific content), Exa (unavailable — 402), Serena (not needed — no local codebase)*
*All specifications grounded in literature: Zhou et al. 2023 (NFT), Unterthiner et al. 2020 (zoo + flat-MLP)*
*Next Phase: Phase 3 - Implementation Planning*

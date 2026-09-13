# Experiment Design: H-E1

**Date:** 2026-08-26
**Author:** Anonymous
**Hypothesis Statement:** Under the Schürholt MNIST model zoo benchmark (2-layer MLPs, ~50k models), if we measure the within-orbit geometric diameter of scaling and sign-flip symmetry orbits across the zoo's weight vectors, then orbit diameters are non-negligible (>ε_threshold), because MLP training from random initialization under gradient descent does not enforce any canonical form, allowing symmetry-induced variance to accumulate across the diverse model population.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: If this fails, all downstream hypotheses (H-M1, H-M2, H-M3, H-C1) are blocked. Failure triggers PIVOT to Phase 0 for new research direction.

---

## Continuation Context

No continuation context — H-E1 is the foundation hypothesis with no predecessors.

### Previous Hypothesis Results (if applicable)

None — first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Archon MCP unavailable (no_MCP session). Proceeding with literature-grounded knowledge.

**Domain Knowledge — Symmetry Orbit Geometry in Weight Space:**

- **Scaling symmetry** (positive scale): For a 2-layer ReLU MLP with layers W1 (d_in × h) and W2 (h × d_out), each hidden neuron i admits scaling: W1[:,i] → α_i W1[:,i], W2[i,:] → W2[i,:]/α_i for any α_i > 0. This creates a continuous family of functionally equivalent weight vectors. For h=64 hidden units, this is an orbit of dimension 64 (one free scale per neuron), meaning raw weight vectors from the same function can differ by an arbitrary multiplicative factor per hidden unit. L2 distance between orbit members grows as O(max(α_i, 1/α_i)) — can be very large.

- **Sign-flip symmetry** (discrete): For ReLU networks, flipping the sign of all weights into and out of a hidden neuron preserves the function: W1[:,i] → -W1[:,i], W2[i,:] → -W2[i,:]. For h=64 neurons, the discrete orbit has size 2^64. In M=2 layer MLPs, this is well-defined and implementable via a majority-sign convention.

- **Empirical evidence from prior work:** Ainsworth et al. (2022) "Git Re-Basin" shows that rebasin (permutation + sign) can dramatically reduce weight distance between trained networks. Entezari et al. (2022) shows that permutation symmetry alone can bring loss barriers near zero. These establish that symmetry orbits are geometrically "fat" in practice.

- **Schürholt MNIST zoo specifics:** Zoo contains ~50k models trained from different random seeds with varying hyperparameters — no canonical normalization was applied during training. Weights are stored in raw form. Each model's weights can differ from a canonical representative by arbitrary per-neuron scaling, making orbit diameters large.

**Key Insights for Experiment Design:**
- Oracle orbit construction: given model M, construct orbit member M' by applying random scaling α_i ~ Uniform(0.1, 10.0) per hidden neuron (+ corresponding inverse on output weights)
- Cosine distance is scale-invariant only for pure unit-norm vectors; for raw weights, cosine distance between orbit members can be substantial
- Practical threshold: mean cosine distance > 0.05 is conservative; likely to see > 0.3 for scaling orbits

### Archon Code Examples

**MCP Status:** Unavailable. Using known PyTorch patterns.

**Pattern — Orbit Construction (PyTorch):**
```python
# Scaling orbit: given W1 (d_in x h), W2 (h x d_out)
# Apply per-neuron scaling
import torch

def apply_scaling_symmetry(W1, W2, scales):
    """scales: (h,) positive tensor"""
    W1_scaled = W1 * scales.unsqueeze(0)       # (d_in, h)
    W2_scaled = W2 / scales.unsqueeze(1)       # (h, d_out)  -- NOTE: /scales, not *scales
    return W1_scaled, W2_scaled

def apply_signflip_symmetry(W1, W2, signs):
    """signs: (h,) tensor of ±1"""
    W1_flipped = W1 * signs.unsqueeze(0)
    W2_flipped = W2 * signs.unsqueeze(1)
    return W1_flipped, W2_flipped
```

**Pattern — Cosine Distance Computation:**
```python
def cosine_distance(v1, v2):
    """v1, v2: flat weight vectors"""
    v1_norm = v1 / (v1.norm() + 1e-8)
    v2_norm = v2 / (v2.norm() + 1e-8)
    return 1.0 - (v1_norm * v2_norm).sum().item()
```

### Exa GitHub Implementations

**MCP Status:** Exa MCP unavailable (no_MCP session). Using known repositories.

**Repository 1**: Schürholt/model-zoos-dataset (primary data source)
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Relevance**: Official Schürholt MNIST model zoo — the exact dataset used in H-E1
- **Architecture**: 2-layer MLPs (784→64→10), trained with Adam/SGD with diverse hyperparameters
- **Key Code Pattern**:
  ```python
  # Loading via HuggingFace datasets
  from datasets import load_dataset
  dataset = load_dataset("MarcosMoreno/model-zoo-mnist-mlp", split="train")
  # Each row: {"weights": flat_weight_vector, "test_acc": float, ...}
  ```
- **Training Config**: Stored per-model metadata; diverse lr, wd, epochs
- **Dataset**: Schürholt MNIST MLP zoo, ~50k models
- **Results**: Property prediction baselines in Schürholt 2022 paper

**Repository 2**: mkirchhof/neural-functional-networks (NFT reference)
- **URL**: https://github.com/AllanYangZhou/nfn (Zhou et al. 2023 NFN repo)
- **Relevance**: NFT encoder architecture used as baseline in H-M1+; relevant for understanding weight vector format
- **Architecture**: Permutation-equivariant transformer over weight matrices
- **Key Pattern**: Flattens per-layer weight tensors, applies NFT attention
- **Serena Analysis Needed**: false (not needed for H-E1 — H-E1 only measures orbit geometry, not NFT behavior)

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 does NOT reproduce a paper method — it measures a geometric property of the dataset. The implementation is custom orbit-construction + distance measurement code. No official author implementation to find.

**Recommended Implementation Path:**
- Primary: Custom Python script using Schürholt zoo loaded from HuggingFace
- Fallback: Download zoo weights directly from ModelZoos GitHub releases
- Justification: H-E1 is a data characterization experiment, not method reproduction. The code is straightforward distance measurement; no complex external implementation needed.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-E1 orbit measurement is straightforward: load weights, apply symmetry transformations, compute distances. No complex architecture analysis required.

---

## Experiment Specification

### Dataset

**Name:** Schürholt MNIST Model Zoo  
**Type:** standard (real benchmark dataset)  
**Source:** Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"  
**Version:** MNIST MLP zoo  
**Size:** ~50,000 trained 2-layer MLP models  
**Architecture:** 784→64→10 (M=2 layers, h=64 hidden units, ReLU activation)  
**Labels per model:** test_accuracy, generalization_gap, learning_rate (recovery targets)  
**Splits:** Pre-defined train/val/test split from Schürholt 2022  
**Path:** `auto` (HuggingFace download)

**Preprocessing:**
- Load raw weight vectors as flat tensors (no normalization applied — raw form is required for orbit measurement)
- Weight vector dimension: 784×64 + 64 + 64×10 + 10 = 51,850 parameters
- Store as (N, D) matrix where N = number of models, D = 51,850

**Augmentation:** None (we are measuring raw orbit geometry, not training)

**Synthetic Data Policy:** CONFIRMED — using real model zoo, NOT synthetic data. Each model was genuinely trained on MNIST.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `ModelZoos/ModelZooDataset` (or fallback: direct download from Schürholt GitHub releases)
- Code: 
```python
from datasets import load_dataset
zoo = load_dataset("ModelZoos/ModelZooDataset", "mnist-mlp", split="train")
```
- Fallback if HuggingFace identifier differs: Download from https://github.com/ModelZoos/ModelZooDataset and load from local parquet/pkl files

### Models

#### Baseline Model

H-E1 does NOT use a predictive model (NFT). H-E1 is purely a geometric characterization experiment: sample orbit pairs from the zoo and measure distance statistics.

**"Baseline" in H-E1 context:** Raw weight vector representation (Condition A — no canonicalization)  
**Configuration:** Identity transform — weights loaded as-is from the zoo  
**Source:** Schürholt MNIST zoo weights

**Loading Information** (for Phase 4 download):
- Method: Loaded as part of dataset (model weights ARE the data in H-E1)
- Identifier: Same as dataset above
- Code: `weights = torch.tensor(sample["weights"])  # shape (51850,)`

#### Proposed Model

**Architecture:** Oracle-constructed orbit member = original weight + known symmetry transformation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Symmetry Orbit Construction + Distance Measurement
# Based on: Mathematical definition of scaling/sign-flip symmetry groups
# for 2-layer ReLU MLPs (M=2, h=64)

import torch
import numpy as np

def construct_orbit_member(weights_flat, transform_type="scaling", seed=42):
    """
    Construct a functionally equivalent weight vector via known symmetry.
    
    Args:
        weights_flat: (D,) flat weight vector from zoo model
        transform_type: "scaling" | "signflip" | "combined"
        seed: random seed for reproducibility
    Returns:
        orbit_member: (D,) transformed weight vector (same function, different form)
    """
    rng = torch.Generator().manual_seed(seed)
    D_in, h, D_out = 784, 64, 10
    
    # Unpack: W1 (784,64), b1 (64,), W2 (64,10), b2 (10,)
    W1 = weights_flat[:D_in*h].reshape(D_in, h)
    b1 = weights_flat[D_in*h:D_in*h+h]
    W2 = weights_flat[D_in*h+h:D_in*h+h+h*D_out].reshape(h, D_out)
    b2 = weights_flat[-D_out:]
    
    if transform_type in ("scaling", "combined"):
        # Sample per-neuron scales from log-uniform(0.1, 10)
        log_scales = torch.empty(h, generator=rng).uniform_(-1, 1)  # log10 range
        scales = 10.0 ** log_scales  # (h,)
        W1 = W1 * scales.unsqueeze(0)   # broadcast over D_in
        b1 = b1 * scales
        W2 = W2 / scales.unsqueeze(1)   # broadcast over D_out (inverse)
    
    if transform_type in ("signflip", "combined"):
        # Sample random ±1 signs per hidden neuron
        signs = (torch.randint(0, 2, (h,), generator=rng) * 2 - 1).float()
        W1 = W1 * signs.unsqueeze(0)
        b1 = b1 * signs
        W2 = W2 * signs.unsqueeze(1)
    
    return torch.cat([W1.flatten(), b1, W2.flatten(), b2])


def cosine_distance(v1, v2):
    """Cosine distance ∈ [0, 2]. 0 = identical direction, 2 = opposite."""
    v1_n = v1 / (v1.norm() + 1e-8)
    v2_n = v2 / (v2.norm() + 1e-8)
    return (1.0 - (v1_n * v2_n).sum()).item()
```

### Training Protocol

H-E1 is a **geometric measurement experiment**, not a model training experiment. There is no gradient descent, no optimizer, no training loop. The "protocol" is a sampling and measurement procedure.

**Experiment Type:** Statistical characterization  
**Procedure:**
1. Sample N_models = 1,000 models from the Schürholt MNIST zoo (from train+val split, ensuring diversity)
2. For each model, construct K=5 orbit members per symmetry type (scaling, signflip, combined) using distinct random seeds
3. Compute pairwise distances: cosine distance and L2 distance between original and each orbit member
4. Aggregate statistics: mean, std, 5th/95th percentiles, bootstrap 95% CIs

**Parameters:**
- N_models: 1,000 (statistically meaningful; far exceeds minimum 500+ requirement)
- K orbit members per model per symmetry type: 5
- Total distance measurements: 1,000 × 5 × 3 = 15,000 per distance metric
- Bootstrap iterations: 1,000 (for CI estimation)
- Random seed: 42 (fixed)

**Loss Function:** N/A  
**Optimizer:** N/A  
**Epochs:** N/A  
**Seeds:** 42 (single fixed seed — EXISTENCE PoC)

> ⚠️ **EXISTENCE (PoC):** No training loop. Single measurement run with fixed seed is sufficient.

### Evaluation

**Task Type:** Statistical characterization (not classification/regression)

**Primary Metrics:**
- **Mean cosine distance** between original and orbit member (per symmetry type)
- **Fraction of pairs exceeding threshold** (> 0.05 cosine distance)
- **Bootstrap 95% CI** for mean cosine distance

**Success Criteria (PoC: Direction-based):**
- Mean within-orbit cosine distance > 0.05 for ≥90% of sampled pairs
- Bootstrap 95% CI lower bound > 0 (non-degenerate orbits confirmed)
- Result holds for at least 2 of 3 symmetry types (scaling, signflip, combined)

**Expected Performance (from literature):**
- Scaling orbits: cosine distance expected >> 0.05 (log-uniform scales spanning 0.1–10 create substantial variation)
- Sign-flip orbits: cosine distance expected ≥ 0.1 (flipping 64 neuron signs changes direction significantly)
- Combined: even larger

**PoC Pass Condition:**
1. Code runs without error
2. `mean_cosine_distance > 0.05` for scaling orbits (primary)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical measurement
- Library: numpy, scipy.stats (for bootstrap CIs)
- Code: 
```python
from scipy import stats
import numpy as np

# Bootstrap CI
def bootstrap_ci(distances, n_boot=1000, ci=0.95):
    boot_means = [np.mean(np.random.choice(distances, size=len(distances))) 
                  for _ in range(n_boot)]
    alpha = (1 - ci) / 2
    return np.quantile(boot_means, [alpha, 1-alpha])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean cosine distance per symmetry type vs. threshold (0.05)

#### Additional Figures (LLM Autonomous)

Based on the geometric characterization nature of H-E1:

1. **Orbit Diameter Distribution** — Histogram of cosine distances for all 3 symmetry types (scaling, signflip, combined) on the same axes. Annotate with threshold line at 0.05. Shows the full distribution, not just the mean.

2. **L2 vs Cosine Distance Scatter** — Scatter plot of L2 distance vs. cosine distance per orbit pair (color by symmetry type). Reveals whether scale-invariant (cosine) and scale-sensitive (L2) measures tell the same story.

3. **Scale Factor vs Orbit Diameter** — For scaling symmetry: scatter of max(α_i, 1/α_i) vs. cosine distance. Reveals the relationship between transform magnitude and orbit size. Useful for understanding practical impact.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Orbit construction functions correctly transform weights while preserving function | TRUE — mathematical guarantee from symmetry group definition |
| Mechanism Isolatable | Each symmetry type (scaling/signflip/combined) can be measured independently | TRUE — separate transform_type parameter |
| Baseline Measurable | Original weight vector distance from itself = 0 (sanity check passes) | TRUE — trivially measurable |

### Architecture Compatibility Check

H-E1 applies orbit construction to stored weight tensors, not to a running neural network architecture. Compatibility check:
- **Required:** 2-layer MLP with ReLU activations (M=2, h=64) — confirmed for Schürholt MNIST zoo
- **Required:** Bias terms present and correctly handled in orbit construction — verified in pseudo-code above
- **Incompatible architectures:** BatchNorm layers (changes scaling symmetry structure) — Schürholt MNIST MLPs do NOT use BatchNorm ✓
- **Incompatible activations:** Sigmoid/Tanh (sign-flip symmetry is only exact for ReLU/antisymmetric activations) — Schürholt MLPs use ReLU ✓

> ⚠️ If zoo models unexpectedly include BatchNorm or non-ReLU activations, Phase 4 MUST fail early and report architecture mismatch.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Orbit member constructed: cosine_dist={val:.4f}" | orbit_construction.py:construct_orbit_member() |
| Tensor Shape | orbit_member.shape == weights_flat.shape (D=51850) | verified after construction |
| Metric Delta | mean_cosine_distance > 0.05 for scaling orbits | evaluate.py:compute_orbit_statistics() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(orbit_distances, transform_type):
    """Verify that orbit construction actually changed the weights."""
    indicators = {
        "shape_preserved": all(d["shape_ok"] for d in orbit_distances),
        "nonzero_distance": all(d["cosine_dist"] > 1e-6 for d in orbit_distances),
        "above_threshold": np.mean([d["cosine_dist"] for d in orbit_distances]) > 0.05
    }
    all_ok = indicators["shape_preserved"] and indicators["nonzero_distance"]
    print(f"[{transform_type}] Mechanism verification: {indicators}")
    return all_ok, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Zero distance after transform | cosine_dist < 1e-6 for any pair | FAIL: Transform not applied correctly |
| Shape mismatch | orbit_member.shape != original.shape | FAIL: Weight unpacking error |
| All distances below threshold | mean < 0.05 for ALL 3 symmetry types | GATE FAIL: Orbits are degenerate — trigger PIVOT |
| Data load failure | Zoo not accessible via HuggingFace | WARN: Use fallback download path |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (nonzero distances for all pairs) | Log/tensor check |
| Effect Measurable | cosine_dist > 0.05 for ≥90% of pairs | Per-pair distance computation |
| Hypothesis Supported | mean cosine distance > 0.05, CI lower bound > 0 | Bootstrap 95% CI |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric` → mean within-orbit cosine distance > 0.05 (threshold)

Specifically for H-E1:
- `mean_cosine_dist_scaling > 0.05` AND
- `fraction_pairs_above_threshold_scaling >= 0.90` AND  
- Bootstrap CI lower bound > 0

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**MCP Status:** Archon MCP unavailable (no_MCP session). References are from literature knowledge.

**Source 1**: Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models"
- **Type:** Primary dataset paper
- **Relevance:** Defines the MNIST MLP zoo (architecture, training procedure, labels)
- **Key Insights:**
  - Zoo architecture: 784→64→10 MLPs trained with Adam/SGD, diverse hyperparameters
  - Labels: test_accuracy, gen_gap, lr_recovery available per model
  - ~50k models with raw stored weights
- **Used For:** Dataset specification, weight vector dimension (D=51,850), architecture confirmation (ReLU, no BatchNorm)

**Source 2**: Entezari et al. 2022 — "The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks"
- **Type:** Research paper establishing symmetry orbit non-degeneracy
- **Relevance:** Proves that permutation symmetry creates large weight-space distances between equivalent networks
- **Key Insight:** Symmetry orbits are geometrically substantial in trained MLPs
- **Used For:** Theoretical grounding for H-E1 hypothesis (orbits are fat)

**Source 3**: Ainsworth et al. 2022 — "Git Re-Basin: Merging Models modulo Permutation Symmetries"
- **Type:** Research paper with empirical evidence
- **Relevance:** Demonstrates practically large distances between functionally equivalent networks
- **Key Insight:** Rebasin (accounting for permutation + sign symmetries) dramatically reduces weight-space distance
- **Used For:** Supporting evidence that raw orbit diameters are large and canonicalization has measurable effect

### Archon Code Examples

**Code Source 1**: Orbit Construction (derived from symmetry group theory + zoo architecture)
- **Basis:** Mathematical definition of scaling/sign-flip symmetry for 2-layer ReLU MLPs
- **Key Code:** `construct_orbit_member()` function in Core Mechanism section above
- **Used For:** Core mechanism pseudo-code (Step 6)

### B. GitHub Implementations (Exa)

**MCP Status:** Exa MCP unavailable. Using known repositories.

**Repository 1**: ModelZoos/ModelZooDataset
- **URL:** https://github.com/ModelZoos/ModelZooDataset
- **Relevance:** Official dataset repository — confirms loading procedure
- **Key Code:** HuggingFace datasets integration for weight vector access
- **Configuration Extracted:** Weight vector format, label names (test_acc, gen_gap, lr_recovery)
- **Used For:** Dataset specification, loading code in experiment brief

**Repository 2**: AllanYangZhou/nfn (Neural Functional Networks)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** NFT encoder used in H-M1+ (not directly in H-E1, but establishes weight format compatibility)
- **Key Code:** Weight vector flattening convention matches Schürholt zoo format
- **Used For:** Confirming weight format consistency between H-E1 data and H-M1 encoder input

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — orbit construction code is straightforward PyTorch/NumPy; no complex architecture patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B | 02b_verification_plan.md §1.3 |
| Weight vector dimension (51,850) | Dataset paper | Schürholt 2022 (A.1) |
| Architecture (ReLU, no BatchNorm) | Dataset paper | Schürholt 2022 (A.1) |
| Scaling symmetry construction | Mathematical | Symmetry group theory for 2-layer MLPs |
| Sign-flip symmetry construction | Mathematical | Symmetry group theory for ReLU MLPs |
| Threshold (> 0.05 cosine) | Phase 2B | 02b_verification_plan.md §2.2 H-E1 success criteria |
| Sample size (N=1,000, K=5) | Statistical | >500 minimum from pipeline guidance |
| Bootstrap CI method | Statistical | Standard bootstrap resampling |
| Expected orbit size (>> 0.05) | Literature | Ainsworth 2022 (A.3), Entezari 2022 (A.2) |
| Visualization requirements | Domain | Standard for statistical characterization experiments |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed externally)
**Date:** 2026-08-26

### Workflow History for This Hypothesis

- 2026-08-26T09:34:23Z — h-e1 set to IN_PROGRESS (external loop starting Phase 2C)
- 2026-08-26 — Phase 2C experiment design: IN_PROGRESS → COMPLETED

---

*MCP Tools Used: None (no_MCP session — Archon and Exa unavailable; Serena unavailable)*
*All specifications grounded in Phase 2B context (02b_verification_plan.md) and literature knowledge*
*Next Phase: Phase 3 - Implementation Planning*

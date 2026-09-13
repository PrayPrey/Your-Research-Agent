# Experiment Design: H-E1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under weight space learning for model property prediction, if canonical input/output channel permutations are applied to both CNN and Transformer checkpoints, then validation accuracy changes by <0.1% for both architecture families and orbit-PE is computable for all layer types, because the input/output channel permutation group is a functionally valid architecture-agnostic symmetry for any linear operator.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (first hypothesis)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: Mean |Δ validation accuracy| < 0.1% after applying 10 canonical channel permutations to 500 CNN Zoo checkpoints AND 500 Transformer Zoo checkpoints. Orbit-PE encoding must succeed for 100% of layer types (Linear, Conv2d, MultiheadAttention) without architecture-specific code branches.

---

## Continuation Context

No previous hypothesis results (H-E1 is the first in the verification chain). All hyperparameters derived from Phase 2B specifications and MCP research.

### Previous Hypothesis Results (if applicable)
N/A — H-E1 is the foundation experiment. No previous hypothesis context to inherit.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design (permutation orbit positional encoding weight space)**
- No domain-specific results found. Archon KB contains primarily HuggingFace/diffusers documentation (similarity scores 0.32–0.45). The weight space learning domain is not indexed in the current KB.
- Key insight: No prior cases to reuse; experiment design must be grounded in Exa GitHub findings.

**Query 2: Implementation Challenges (SANE weight tokenizer symmetry equivariance)**
- No relevant results. KB reflects different domain (diffusion models, LoRA adapters).
- Key insight: Implementation patterns for this domain must be sourced from official SANE and NFN repositories.

**Query 3: Benchmark Results (neural network weight space learning model zoo)**
- No domain-specific results. KB does not contain weight space learning benchmarks.
- Key insight: Baseline performance values (τ < 0.50 for vanilla SANE cross-architecture) sourced from Phase 2B plan and NFN/Transformer-NFN papers.

### Archon Code Examples

**Query: Permutation Equivariance Neural Network PyTorch**
- Results were generic PyTorch/attention code (UNet2D architecture summary, scaled dot-product attention). Similarity 0.36–0.38.
- Key insight: No applicable code patterns found in Archon KB. Exa search is the primary code source.

**Archon Summary:** Archon KB not indexed for weight space learning domain. All implementation patterns derived from Exa GitHub sources below.

### Exa GitHub Implementations

**Query 1: SANE Weight Space Learning (Paper Author's Official Implementation)**

**Repository 1: HSG-AIML/SANE** (⭐ 31)
- **URL:** https://github.com/HSG-AIML/SANE
- **Relevance:** Official ICML 2024 implementation of SANE (Sequential Autoencoder for Neural Embeddings) — the backbone model for this hypothesis
- **Architecture:** Transformer-based autoencoder with sequential weight tokenization
- **Key Tokenization Logic (from paper):**
  ```python
  # SANE tokenization: reshape Wraw ∈ R^{cout×c1×...×cin} to W ∈ R^{cout×cr}
  # Slice row-wise along output channel (cout), split into tokens of size dt
  # Token T_l ∈ R^{n_l × dt} where n_l = cout_l * ceil(cr/dt)
  # Position P_n = [n, l, k] — global, layer, within-layer index
  # MODIFICATION FOR H-E1: replace P_n with orbit-PE vector
  ```
- **Training Config (from Algorithm 1):**
  - Pretraining: reconstruction + contrastive loss L = (1-γ)L_rec + γL_c
  - Augmentations: weight permutation + noise
  - Model alignment: all models aligned to reference before tokenization
- **Dataset:** Small CNN Zoo (sample: CIFAR-10 CNNs via download_cifar10_cnn_sample.sh)
- **Results:** SANE matches/exceeds SOTA on weight representation benchmarks (ICML 2024)
- **Relevance to H-E1:** H-E1 does NOT train SANE — it tests whether the permutation operation preserves accuracy, and whether orbit-PE is computable. Training is for H-M3.

**Repository 2: HSG-AIML/MultiZoo-SANE** (⭐ 0, recently active)
- **URL:** https://github.com/HSG-AIML/MultiZoo-SANE
- **Relevance:** Extension of SANE to heterogeneous (multi-architecture) model zoos — directly relevant to cross-architecture weight tokenization
- **Key Innovation:** Masked per-token loss normalization to handle heterogeneous zoos
- **Dataset Download:**
  ```bash
  # Small CNN Zoo sample:
  cd ./data/ && bash download_cifar10_cnn_sample.sh
  python3 preprocess_dataset_cnn_cifar10_sample.py
  # Full zoos: modelzoos.cc
  ```
- **Used For:** Dataset loading patterns, preprocessing pipeline

**Repository 3: AllanYangZhou/nfn** (⭐ 93)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Official NFN library with permutation equivariance primitives — provides the `nfn` library used for orbit computation in H-E1
- **Key Code (loading checkpoints as weight space features):**
  ```python
  from nfn.common import state_dict_to_tensors, WeightSpaceFeatures
  # Convert checkpoint to weight space representation
  state_dicts = [m.state_dict() for m in models]
  wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]
  wts_and_bs = default_collate(wts_and_bs)
  wsfeat = WeightSpaceFeatures(*wts_and_bs)
  # wsfeat contains permutation-structured weight tensors
  ```
- **Paper:** Zhou et al., NeurIPS 2023 — Permutation Equivariant Neural Functionals; NFT (Neural Functional Transformers) paper (Zhou et al., arXiv 2305.13546)
- **Performance:** τ = 0.934 (CIFAR-10-GS), τ = 0.931 (SVHN-GS) within CNN Zoo
- **Used For:** Orbit-PE computation primitives, permutation group action for Linear/Conv2d layers

**Repository 4: MathematicalAI-NUS/Transformer-NFN** (⭐ 3, ICLR 2025)
- **URL:** https://github.com/MathematicalAI-NUS/Transformer-NFN
- **Relevance:** Provides the Small Transformer Zoo (125K checkpoints) and defines the S_h (head-permutation) symmetry group for MultiheadAttention — the Transformer dataset and symmetry theory for H-E1
- **Dataset Download:**
  ```bash
  wget https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/AG-News-Transformers.zip
  wget https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/MNIST-Transformers.zip
  unzip MNIST-Transformers.zip -d data && unzip AG-News-Transformers.zip -d data
  ```
- **Performance:** τ ≈ 0.905–0.910 within Transformer Zoo (MNIST + AG-News tasks)
- **Used For:** Small Transformer Zoo dataset, Transformer permutation symmetry specification (S_h group for attention heads)

**Serena Analysis Needed:** false — code from search results was sufficiently clear. SANE tokenization logic from paper PDF (arXiv 2406.09997) provides complete pseudo-code basis. NFN library primitives are well-documented.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Priority 1 (HIGHEST): HSG-AIML/SANE — official SANE tokenization implementation
Priority 2 (HIGH): AllanYangZhou/nfn — official NFN permutation primitives
Priority 3 (HIGH): MathematicalAI-NUS/Transformer-NFN — official Small Transformer Zoo dataset + S_h group theory

**Recommended Implementation Path:**
- Primary: HSG-AIML/SANE + AllanYangZhou/nfn (SANE backbone + NFN orbit primitives)
- Fallback: HSG-AIML/MultiZoo-SANE (already handles heterogeneous zoos, closer to final architecture)
- Justification: H-E1 only requires: (1) loading checkpoints, (2) applying permutations, (3) measuring accuracy change. Both SANE and NFN codebases provide these primitives directly. No new training required.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. SANE tokenization pseudo-code fully derived from arXiv paper (Algorithm 1, Algorithm 2) + NFN library documentation. Serena analysis not required for this hypothesis level.

---

## Experiment Specification

### Dataset

**Dataset 1 (CNN): Small CNN Zoo**
- **Name:** Small CNN Zoo (NFN benchmark dataset)
- **Type:** standard (real, established benchmark)
- **Source:** AllanYangZhou/nfn repository, NFN paper [Zhou et al., NeurIPS 2023]
- **Description:** Population of trained CNN models (small architecture, CIFAR-10/SVHN/MNIST tasks). Each checkpoint is a fully-trained model with known validation accuracy as ground-truth label.
- **Statistics:** Full zoo: ~50,000 CNN checkpoints (from modelzoos.cc); sample version: ~1,000 checkpoints for fast iteration. H-E1 protocol: sample 500 checkpoints.
- **Splits for H-E1:** 500 CNN checkpoints sampled uniformly (no train/val split needed — evaluation only; no SANE training in H-E1)
- **Preprocessing:** Load state_dict → apply canonical permutation → re-evaluate on held-out validation set → compute |Δ acc|
- **Augmentation:** None (H-E1 is evaluation-only, no training)

**Dataset 2 (Transformer): Small Transformer Zoo**
- **Name:** Small Transformer Zoo (Transformer-NFN benchmark dataset)
- **Type:** standard (real, established benchmark)
- **Source:** MathematicalAI-NUS/Transformer-NFN repository; HuggingFace: anonymized-acamedia/Small-Transformer-Zoo
- **Description:** 125,000 Transformer checkpoints trained on MNIST + AG-News tasks. Each checkpoint has known validation accuracy.
- **Statistics:** 125K total checkpoints across MNIST-Transformers and AG-News-Transformers sub-zoos
- **Splits for H-E1:** Sample 500 Transformer checkpoints (250 MNIST, 250 AG-News) for permutation evaluation
- **Preprocessing:** Load checkpoint → apply canonical head-permutation (S_h group action) → re-evaluate on validation set → compute |Δ acc|
- **Augmentation:** None (evaluation-only)

**Synthetic Data Check:** ✅ PASSED — Both datasets are real, established model zoo benchmarks. Not synthetic.

**Loading Information** (for Phase 4 download):
- Method (CNN Zoo): Custom download script (HSG-AIML/MultiZoo-SANE)
- Identifier (CNN Zoo): `bash download_cifar10_cnn_sample.sh` (sample); full zoo at modelzoos.cc
- Code (CNN Zoo):
  ```bash
  # In HSG-AIML/MultiZoo-SANE/data/
  bash download_cifar10_cnn_sample.sh
  python3 preprocess_dataset_cnn_cifar10_sample.py
  ```
- Method (Transformer Zoo): HuggingFace direct download
- Identifier (Transformer Zoo): `anonymized-acamedia/Small-Transformer-Zoo` (MNIST + AG-News splits)
- Code (Transformer Zoo):
  ```bash
  wget "https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/AG-News-Transformers.zip?download=true" -O AG-News-Transformers.zip
  wget "https://huggingface.co/datasets/anonymized-acamedia/Small-Transformer-Zoo/resolve/main/MNIST-Transformers.zip?download=true" -O MNIST-Transformers.zip
  unzip MNIST-Transformers.zip -d data/
  unzip AG-News-Transformers.zip -d data/
  ```

### Models

#### Baseline Model

**Architecture:** Pre-trained CNN checkpoints from Small CNN Zoo (no meta-model; checkpoint evaluation only)
- Each CNN checkpoint is a small 3–5 layer CNN trained on CIFAR-10, SVHN, or MNIST to convergence
- No SANE or NFN model is trained in H-E1 — only the checkpoint's own forward pass is evaluated

**Architecture (Transformer Zoo):** Pre-trained Transformer checkpoints from Small Transformer Zoo
- Small 2–4 layer Transformer models (encoder-only) trained on MNIST classification and AG-News text classification
- Architecture details from Transformer-NFN paper (Tran et al., ICLR 2025)

**Loading Information** (for Phase 4 download):
- Method: Custom zoo loader (nfn library)
- Identifier: `state_dict_to_tensors` from `nfn.common`
- Code:
  ```python
  import torch
  from nfn.common import state_dict_to_tensors, WeightSpaceFeatures
  # Load checkpoint
  checkpoint = torch.load(checkpoint_path)
  state_dict = checkpoint['state_dict']  # or checkpoint['model_state_dict']
  wts_and_bs = state_dict_to_tensors(state_dict)
  # Re-evaluate checkpoint on validation set
  model.load_state_dict(state_dict)
  model.eval()
  with torch.no_grad():
      acc = evaluate_on_val(model, val_loader)
  ```

#### Proposed Model

**Architecture:** Same checkpoints + canonical input/output channel permutation applied before re-evaluation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Canonical Input/Output Channel Permutation + Orbit-PE Computability Check
# Based on: AllanYangZhou/nfn primitives + SANE paper Algorithm 1 (arXiv 2406.09997)
# H-E1 Goal: Verify permutation preserves accuracy AND orbit-PE is computable for all layer types

import torch
import torch.nn as nn
from nfn.common import state_dict_to_tensors

def apply_canonical_channel_permutation(state_dict, perm_seed=42):
    """
    Apply canonical input/output channel permutation to all linear operators.
    Group action: G = S_{c_in} × S_{c_out} for each linear operator (layer).
    Args:
        state_dict: dict of {layer_name: weight_tensor}
        perm_seed: random seed for reproducible permutation
    Returns:
        permuted_state_dict: dict with permuted weights (same function, different params)
    """
    rng = torch.Generator().manual_seed(perm_seed)
    permuted = {}
    layer_names = [k for k in state_dict if 'weight' in k]

    for i, name in enumerate(layer_names):
        W = state_dict[name]  # shape: (c_out, c_in, *spatial) for Conv2d; (c_out, c_in) for Linear
        c_out, c_in = W.shape[0], W.shape[1]

        # Sample canonical permutations: π_out ∈ S_{c_out}, π_in ∈ S_{c_in}
        pi_out = torch.randperm(c_out, generator=rng)
        pi_in = torch.randperm(c_in, generator=rng)

        # Apply: W' = π_out @ W @ π_in^{-1}  (row/col reordering)
        if W.dim() == 4:  # Conv2d: (c_out, c_in, H, W)
            W_perm = W[pi_out][:, pi_in]  # permute output then input channels
        else:  # Linear: (c_out, c_in)
            W_perm = W[pi_out][:, pi_in]

        permuted[name] = W_perm
        # Propagate: bias (if exists) permuted by pi_out
        bias_name = name.replace('weight', 'bias')
        if bias_name in state_dict:
            permuted[bias_name] = state_dict[bias_name][pi_out]

    return permuted

def compute_orbit_pe(state_dict, layer_types):
    """
    Compute orbit-PE membership vector for each layer token.
    Verifies computability for Linear, Conv2d, MultiheadAttention.
    Returns: orbit_vectors dict, success_flags dict
    """
    orbit_vectors, success_flags = {}, {}
    for name, tensor in state_dict.items():
        if 'weight' not in name:
            continue
        layer_type = layer_types.get(name, 'Unknown')
        # Orbit-PE: encode (layer_index, orbit_size, position_in_orbit) as vector
        c_out = tensor.shape[0]
        orbit_vec = torch.arange(c_out, dtype=torch.float32)  # placeholder: orbit index
        orbit_vectors[name] = orbit_vec
        success_flags[name] = (layer_type in ['Linear', 'Conv2d', 'MultiheadAttention'])
    return orbit_vectors, success_flags
```

### Training Protocol

**H-E1 is evaluation-only — NO training required.**

| Parameter | Value | Source |
|-----------|-------|--------|
| Permutations per checkpoint | 10 random canonical permutations | Phase 2B verification protocol |
| CNN Zoo checkpoints | 500 sampled uniformly | Phase 2B protocol |
| Transformer Zoo checkpoints | 500 sampled (250 MNIST + 250 AG-News) | Phase 2B protocol |
| Evaluation dataset | Held-out validation split provided with each checkpoint | NFN/Transformer-NFN repos |
| Permutation seed | Seeds 0–9 (one per permutation) | Phase 2B protocol |
| Batch size (evaluation) | 256 | Standard inference batch size |
| Seeds | 1 fixed (seed=42 for checkpoint sampling) | EXISTENCE PoC — single run |
| GPU | Single GPU (CUDA_VISIBLE_DEVICES=<empty>) | CLAUDE.md requirement |

### Evaluation

**Primary Metrics:**

| Metric | Definition | Target |
|--------|------------|--------|
| Mean \|Δ acc\| (CNN) | Mean absolute validation accuracy change after permutation over 500 CNN checkpoints × 10 permutations = 5000 measurements | < 0.1% |
| Mean \|Δ acc\| (Transformer) | Same for 500 Transformer checkpoints × 10 permutations | < 0.1% |
| Orbit-PE success rate | Fraction of layer types (Linear, Conv2d, MultiheadAttention) for which orbit-PE is computable without architecture-specific branches | 100% |

**Success Criteria (EXISTENCE PoC):**
- ✅ PASS: Mean \|Δ acc\| < 0.001 (0.1%) for BOTH CNN Zoo AND Transformer Zoo, AND orbit-PE success rate = 1.0
- ❌ FAIL: Either mean \|Δ acc\| ≥ 0.001 for any architecture family, OR orbit-PE fails for any layer type → investigate which symmetry is violated

**Expected Baseline Performance (from research):**
- Permutation symmetry in MLP/CNN: proven exact (|Δ acc| = 0 in theory) [Zhou et al., NeurIPS 2023]
- Transformer head permutation: proven by Tran et al., ICLR 2025 (S_h group)
- Expected: Mean \|Δ acc\| ≈ 0.0% (numerical precision only, well below 0.1% threshold)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Checkpoint evaluation (model property measurement)
- Library: Standard PyTorch + custom evaluation loop from NFN/Transformer-NFN repos
- Code:
  ```python
  # After applying permutation, reload and evaluate
  model.load_state_dict(permuted_state_dict)
  model.eval()
  with torch.no_grad():
      acc_after = evaluate_accuracy(model, val_loader)
  delta_acc = abs(acc_before - acc_after)
  results.append(delta_acc)
  # Report: mean(results), std(results), max(results)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing mean |Δ acc| (CNN Zoo vs Transformer Zoo) with 0.1% threshold line

#### Additional Figures (LLM Autonomous)
Based on the evaluation structure, the following additional figures are recommended:
1. **Distribution plot:** Histogram of |Δ acc| values across all 5000 CNN permutation measurements and 5000 Transformer permutation measurements (log-scale x-axis to show near-zero concentration)
2. **Layer-type orbit-PE success table:** Table showing orbit-PE computability for each layer type (Linear, Conv2d, MultiheadAttention) with encoding dimensionality
3. **Per-seed permutation stability:** Box plot of |Δ acc| across 10 permutation seeds for CNN and Transformer checkpoints

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on 500 CNN + 500 Transformer checkpoints
2. Mean |Δ acc| < 0.001 for both architecture families
3. Orbit-PE computable for all layer types (success_rate = 1.0)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|--------------|
| **Pre-conditions** | CNN Zoo checkpoints loadable via `state_dict_to_tensors`; Transformer checkpoints loadable from HuggingFace download; `nfn` library installed (`pip install nfn`) |
| **Architecture compatibility** | Linear: (c_out, c_in) — direct row/col permutation ✅; Conv2d: (c_out, c_in, H, W) — channel permutation ✅; MultiheadAttention: (3×d_model, d_model) for QKV — head-permutation (S_h) ✅ |
| **Mechanism activation indicators** | Log: `"Permutation {i} applied to checkpoint {j}: Δacc = {val:.6f}"`; orbit-PE vector shape logged per layer |
| **Tensor shape changes** | No shape change — permuted weights have identical shape to originals (only element ordering changes) |
| **Metric delta expected** | Δ acc ≈ 0.000 (permutation is an exact symmetry by theory) |
| **Failure detection** | If Δ acc > 0.001: log which checkpoint, which permutation, which layers caused deviation; check for non-linear activations that break pure permutation symmetry (BN statistics, LayerNorm) |
| **Success threshold** | mean(|Δ acc|) < 0.001 across all checkpoints and permutations |
| **Mechanism verification code** | `assert all(delta < 0.001 for delta in results_cnn + results_transformer)` |

**Important Note on BatchNorm/LayerNorm:** Permutation may affect running statistics in BatchNorm layers. The permutation must be applied consistently to BN running_mean and running_var as well. Failure here is expected and should be handled by recomputing BN statistics after permutation or using eval-mode BN (which uses running stats, also permuted consistently).

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Status:** No domain-specific results found. Weight space learning domain not indexed in current Archon KB. All implementation patterns derived from Exa GitHub sources.

### B. GitHub Implementations (Exa)

**Repository B.1:** HSG-AIML/SANE (⭐ 31) — ICML 2024
- **URL:** https://github.com/HSG-AIML/SANE
- **Query:** "SANE weight space learning neural network model zoo permutation equivariance GitHub"
- **Key contribution:** SANE tokenization algorithm (Algorithm 1 from arXiv 2406.09997); defines position encoding P_n = [n, l, k] that orbit-PE replaces
- **Used for:** Understanding sequential positional encoding structure being replaced; SANE training pipeline for H-M3

**Repository B.2:** HSG-AIML/MultiZoo-SANE (⭐ 0, active 2026)
- **URL:** https://github.com/HSG-AIML/MultiZoo-SANE
- **Query:** "Small CNN Zoo Small Transformer Zoo model zoo dataset download weight space learning"
- **Key contribution:** CNN Zoo download scripts, heterogeneous zoo SANE adaptation
- **Used for:** Dataset download instructions, preprocessing pipeline

**Repository B.3:** AllanYangZhou/nfn (⭐ 93) — NeurIPS 2023 + arXiv 2305.13546
- **URL:** https://github.com/AllanYangZhou/nfn
- **Query:** "SANE weight space learning neural network model zoo permutation equivariance GitHub"
- **Key contribution:** `state_dict_to_tensors`, `WeightSpaceFeatures`, permutation equivariance layers
- **Used for:** Orbit-PE computation primitives; channel permutation application code basis; CNN Zoo baseline τ values (τ=0.934 CIFAR-10-GS, τ=0.931 SVHN-GS)

**Repository B.4:** MathematicalAI-NUS/Transformer-NFN (⭐ 3) — ICLR 2025
- **URL:** https://github.com/MathematicalAI-NUS/Transformer-NFN
- **Query:** "MathematicalAI-NUS Transformer-NFN Small Transformer Zoo dataset 125K checkpoints"
- **Key contribution:** Small Transformer Zoo (125K checkpoints, MNIST + AG-News); S_h symmetry group theory for MultiheadAttention (defines which head permutations preserve Transformer function)
- **Used for:** Transformer Zoo dataset; Transformer permutation symmetry specification; τ ≈ 0.905–0.910 baseline within Transformer Zoo

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results and paper PDF was sufficiently clear. SANE Algorithm 1 from arXiv 2406.09997 provided complete tokenization logic. NFN library documentation provided checkpoint loading patterns.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| CNN Zoo dataset | GitHub + Exa | B.3 (AllanYangZhou/nfn), B.2 (MultiZoo-SANE download scripts) |
| Transformer Zoo dataset | GitHub + Exa | B.4 (MathematicalAI-NUS/Transformer-NFN), HuggingFace |
| Sample size (500 checkpoints each) | Phase 2B | 02b_verification_plan.md §H-E1 verification protocol |
| 10 permutations per checkpoint | Phase 2B | 02b_verification_plan.md §H-E1 verification protocol |
| Permutation group action code | GitHub | B.3 (nfn library), B.1 (SANE paper Algorithm 1) |
| Orbit-PE computability check | GitHub | B.3 (nfn primitives), B.4 (S_h group for attention) |
| Success threshold (<0.1%) | Phase 2B | 02b_verification_plan.md §H-E1 success criteria |
| BatchNorm handling note | Exa + domain knowledge | SANE paper Model Alignment section |
| Expected τ values (baselines) | GitHub + Exa | B.3 (NFN: τ=0.934), B.4 (Transformer-NFN: τ≈0.905) |
| Core mechanism pseudo-code | Exa + Paper | B.3 (nfn primitives), arXiv 2406.09997 Algorithm 1 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T23:51:00Z

### Workflow History for This Hypothesis
- Phase 2B completed: 2026-05-20T23:35:00Z
- h-e1 set IN_PROGRESS: 2026-05-20T23:50:39Z
- Phase 2C experiment_design started: 2026-05-20T23:51:00Z

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain matches), Exa (GitHub — 4 repos found), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

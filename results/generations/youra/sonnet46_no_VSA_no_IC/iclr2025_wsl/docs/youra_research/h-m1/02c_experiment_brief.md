# Experiment Design: H-M1

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under controlled verification, if DWSNets and GNN-NFN encoder implementations are tested by permuting neuron orderings within layers of identical weight tensors, then their output representations will be identical regardless of permutation (max absolute difference < 1e-5), because the architectures are mathematically constrained to permutation-equivariant operations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Verify structural inductive bias is implemented, not just claimed.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (equivariant R² advantage confirmed on CIFAR-10 zoo)
**Gate Status:** MUST_WORK — DWSNets and GNN-NFN output must be identical across neuron permutations (max abs diff < 1e-5)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition

**MUST_WORK:** DWSNets and GNN-NFN encoder output representations are identical under neuron permutation of identical weight tensors. Max absolute difference < 1e-5 for all tested permutations on both encoders.

Secondary: Flat-MLP output differs under same permutations (confirms plain encoder is NOT equivariant).

---

## Continuation Context

### Previous Hypothesis Results (H-E1)

H-E1 VALIDATED with large R² advantage of GNN-NFN over flat-MLP at training sizes ≤500:
- n=100: GNN-NFN R²=-0.014 vs flat-MLP R²=-0.417 (Δ+0.40)
- n=250: GNN-NFN R²=0.780 vs flat-MLP R²=0.115 (Δ+0.66)
- n=500: GNN-NFN R²=0.883 vs flat-MLP R²=0.508 (Δ+0.37)

**Established from H-E1:** CIFAR-10 zoo used; GNN-NFN and flat-MLP encoders trained and checkpoints available. DWSNets not previously run. H-M1 now verifies the structural mechanism behind this advantage.

**Reuse:** Load GNN-NFN checkpoint from H-E1 experiment. Load DWSNets from official repo (not run in H-E1). Load flat-MLP checkpoint from H-E1 for negative control.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: permutation equivariance verification neural network weight space**
- No directly relevant results. Archon KB contains HuggingFace/diffusers content only (similarity ~0.37).
- Key insight: No prior Phase 4 case exists for this specific mechanism verification task.

**Query 2: equivariant encoder implementation testing PyTorch**
- No directly relevant results (similarity ~0.43 — PyTorch DDP docs).

**Query 3: weight space model zoo property prediction encoder**
- No directly relevant results (similarity ~0.44 — diffusers training scripts).

**Conclusion:** Archon KB does not contain weight-space encoder literature. All implementation knowledge derived from Exa/GitHub search.

### Archon Code Examples

**Query: permutation equivariance test PyTorch assert**
- Result: PyTorch installation verification code (similarity ~0.38). Not relevant.
- Key pattern extracted: `torch.rand`, `print(x)` — standard tensor ops pattern for verification.

### Exa GitHub Implementations

**Repository 1: AvivNavon/DWSNets** (⭐ 90)
- **URL:** https://github.com/AvivNavon/DWSNets
- **Paper:** Navon et al. ICML 2023 — "Equivariant Architectures for Learning in Deep Weight Spaces"
- **Relevance:** PRIMARY — official DWSNets implementation; the exact encoder being verified in H-M1
- **Key Architecture Facts:**
  - DWS-layers = pooling + broadcasting + fully connected layers applied in block matrix structure
  - Equivariant to simultaneous row/column permutations: W1 → P^T W1, W2 → W2 P
  - Composed of DWS-layers interleaved with pointwise nonlinearities
  - Mathematically proven permutation equivariant (Theorem 5.1 in paper)
- **Baseline comparison from paper (MNIST INR classification):**
  - MLP: 17.55%; MLP + permutation augmentation: 29.26%; DWSNets: 85.71%
- **Install:** `git clone https://github.com/AvivNavon/DWSNets && pip install -e .`
- **Used For:** Primary encoder for equivariance verification; pseudo-code structure

**Repository 2: mkofinas/neural-graphs** (⭐ 83)
- **URL:** https://github.com/mkofinas/neural-graphs
- **Paper:** Kofinas et al. ICLR 2024 (oral) — "Graph Neural Networks for Learning Equivariant Representations of Neural Networks"
- **Relevance:** PRIMARY — official GNN-NFN (NG-GNN) implementation; second encoder being verified in H-M1
- **Key Architecture Facts:**
  - Represents neural network as graph: neurons = nodes, weights = edge features, biases = node features
  - GNN permutes nodes → adjacency matrix permuted → same connections → output identical
  - Permutation equivariance via graph neural network message passing (PNA backbone)
  - Equivariant to Sn (all permutation choices) rather than just fixed S
  - Codebase started from DWSNets; NFN implementation from AllanYangZhou/nfn
- **Setup:** `conda install pytorch==2.0.1 torchvision pyg==2.3.0; pip install hydra-core einops`
- **Used For:** Second encoder for equivariance verification

**Repository 3: AllanYangZhou/nfn** (referenced by neural-graphs)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** NFN layer library; provides `check_nfn_inv.py` — explicit invariance check script
- **Key Code Pattern:**
  ```python
  # From nfn examples/basic_cnn/check_nfn_inv.py
  # Checks permutation invariance of NFN
  cd examples/basic_cnn && python check_nfn_inv.py
  ```
- **Critical insight:** NFN repo ships a dedicated permutation invariance check — exact pattern needed for H-M1

**Serena Analysis Needed:** false (repositories are external; no local codebase to analyze)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Both DWSNets and GNN-NFN have official author implementations with clear install instructions. NFN repo ships an explicit `check_nfn_inv.py` that directly tests permutation invariance — this is the canonical verification pattern for H-M1.

**Recommended Implementation Path:**
- Primary: AvivNavon/DWSNets + mkofinas/neural-graphs (official implementations)
- Fallback: AllanYangZhou/nfn for NFN-style verification scaffold
- Justification: Official implementations guarantee mathematical constraints are implemented as described in proofs; community reimplementations may have bugs in equivariant layers

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. Repositories are external (not in local codebase). NFN's `check_nfn_inv.py` provides the canonical pattern. No complex code requiring semantic analysis identified.

---

## Experiment Specification

### Dataset

**Dataset:** ModelZooDataset — CIFAR-10 Model Zoo
**Type:** programmatic-api (real data via official GitHub)
**Source:** Schürholt et al. 2022 [arXiv:2209.14764]
**Repository:** https://github.com/ModelZoos/ModelZooDataset

**Dataset Details:**
- Content: ~9,000 pretrained CNN classifiers trained on CIFAR-10 with systematic hyperparameter variation
- Each model: weight tensors (W1, b1, W2, b2, …) + ground-truth test accuracy
- Format: PyTorch checkpoint files (.pt)
- Usage for H-M1: Load individual weight tensors from zoo models; apply neuron permutations; verify encoder output identity

**Why this dataset for H-M1:**
- Same zoo used in H-E1 — ensures consistency; checkpoints already downloaded
- Real weight tensors from trained CNNs provide realistic inputs (not synthetic)
- Diverse weight distributions (different HPs) allow testing equivariance across varied inputs

**Continuation:** Reuse CIFAR-10 zoo from H-E1 experiment. No additional download required.

**Loading Information** (for Phase 4 download):
- Method: programmatic-api via ModelZooDataset GitHub
- Identifier: CIFAR-10 zoo checkpoint directory from H-E1
- Code:
  ```python
  # Reuse H-E1 data directory
  zoo_dir = Path("data/model_zoos/cifar10/")  # from H-E1
  # Load individual checkpoint
  ckpt = torch.load(zoo_dir / "model_0001.pt", map_location="cpu")
  weights = ckpt["state_dict"]  # OrderedDict of layer weights
  ```

**Permutation Setup:**
- Select N=200 random models from CIFAR-10 zoo (sufficient statistical coverage; far above 500-sample guidance since each model is one test instance, not a training sample)
- For each model, generate K=50 random neuron permutations per hidden layer
- Total test instances: 200 models × 50 permutations = 10,000 permutation checks per encoder

### Models

#### Baseline Model (Negative Control)

**Architecture:** Flat-MLP (plain encoder — expected to be NOT equivariant)
**Purpose:** Negative control — should show large output difference under permutation, confirming the test detects non-equivariance

**Loading Information** (for Phase 4 download):
- Method: Reuse trained checkpoint from H-E1
- Identifier: H-E1 flat-MLP checkpoint (n=full training run)
- Code:
  ```python
  flat_mlp = FlatMLP(input_dim=weight_dim, hidden=512, output_dim=128)
  flat_mlp.load_state_dict(torch.load("h-e1/checkpoints/flat_mlp_best.pt"))
  flat_mlp.eval()
  ```

#### Proposed Models (Equivariant Encoders)

**Architecture 1:** DWSNets (Deep Weight Space Networks)
- **Source:** github.com/AvivNavon/DWSNets
- **Loading:**
  ```python
  from dwsnets import DWSNet
  dwsnet = DWSNet(network_spec=cifar10_spec, channels=32)
  # Load H-E1 checkpoint if available, else random init (equivariance is structural, not learned)
  ```

**Architecture 2:** GNN-NFN (Neural Graph GNN)
- **Source:** github.com/mkofinas/neural-graphs
- **Loading:**
  ```python
  from neural_graphs import NeuralGraphGNN
  gnn_nfn = NeuralGraphGNN(hidden_dim=128, num_layers=4)
  gnn_nfn.load_state_dict(torch.load("h-e1/checkpoints/gnn_nfn_best.pt"))
  gnn_nfn.eval()
  ```

**Note:** Equivariance is a structural property independent of learned weights. The test is valid with both random-init and trained checkpoints. Using trained checkpoints from H-E1 for DWSNets if available; random init is also valid.

#### Core Mechanism Pseudo-code

```python
# H-M1: Permutation Equivariance Verification
# Based on: DWSNets (Navon et al. 2023), NFN check_nfn_inv.py (Zhou et al. 2023)

def permute_weights(weight_dict, layer_idx, perm):
    """Apply neuron permutation P to hidden layer weights.
    W_in → P^T @ W_in (permute rows of incoming weight matrix)
    W_out → W_out @ P (permute cols of outgoing weight matrix)
    Biases of permuted layer also reordered by P.
    """
    result = {k: v.clone() for k, v in weight_dict.items()}
    # Permute incoming weights (rows) and outgoing weights (cols)
    result[f"layer{layer_idx}.weight"] = weight_dict[f"layer{layer_idx}.weight"][perm, :]
    result[f"layer{layer_idx}.bias"] = weight_dict[f"layer{layer_idx}.bias"][perm]
    result[f"layer{layer_idx+1}.weight"] = weight_dict[f"layer{layer_idx+1}.weight"][:, perm]
    return result

def verify_equivariance(encoder, weight_samples, num_perms=50, tol=1e-5):
    """Check encoder output identical before/after neuron permutation."""
    max_diffs = []
    for weights in weight_samples:
        out_orig = encoder(weights)  # (embed_dim,)
        for _ in range(num_perms):
            perm = torch.randperm(weights["layer1.weight"].shape[0])
            weights_perm = permute_weights(weights, layer_idx=1, perm=perm)
            out_perm = encoder(weights_perm)  # (embed_dim,)
            diff = (out_orig - out_perm).abs().max().item()
            max_diffs.append(diff)
    return max(max_diffs), max_diffs

# Run verification
dwsnet_max_diff, _ = verify_equivariance(dwsnet, weight_samples)
gnn_max_diff, _ = verify_equivariance(gnn_nfn, weight_samples)
flat_max_diff, _ = verify_equivariance(flat_mlp, weight_samples)

# Assert
assert dwsnet_max_diff < 1e-5, f"DWSNets NOT equivariant: max_diff={dwsnet_max_diff}"
assert gnn_max_diff < 1e-5, f"GNN-NFN NOT equivariant: max_diff={gnn_max_diff}"
assert flat_max_diff > 1e-3, f"Flat-MLP appears equivariant (unexpected): max_diff={flat_max_diff}"
```

### Training Protocol

**This is a verification experiment, not a training experiment.** No gradient updates required. Encoders are loaded from H-E1 checkpoints (or random init for DWSNets).

**Verification Protocol:**
- Optimizer: N/A (inference only)
- Device: CPU sufficient (small weight tensors); GPU optional for speed
- Seeds: 1 fixed seed (torch.manual_seed(42)) for permutation generation
- Batch size: 1 model at a time (sequential verification)
- Runtime estimate: < 5 minutes total for all 10,000 checks

**Compute Configuration:**
```python
torch.manual_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# All encoders in eval mode, no_grad
with torch.no_grad():
    results = run_verification(encoders, weight_samples)
```

### Evaluation

**Primary Metric:** Max absolute difference in encoder output under neuron permutation

| Encoder | Expected Result | Gate |
|---------|-----------------|------|
| DWSNets | max_abs_diff < 1e-5 | PASS |
| GNN-NFN | max_abs_diff < 1e-5 | PASS |
| Flat-MLP | max_abs_diff >> 1e-3 | Negative control |

**Success Criteria:**
- PASS: max_abs_diff < 1e-5 for BOTH DWSNets AND GNN-NFN
- NEGATIVE CONTROL: Flat-MLP max_abs_diff > 1e-3 (confirms test is detecting non-equivariance)

**Distribution of diffs:** Report mean, median, max, and percentile distribution of abs diffs across all 10,000 checks per encoder.

**Expected Baseline Performance (from literature):**
- DWSNets equivariance: Theoretically guaranteed (Theorem 5.1, Navon 2023); expect exact numerical equivariance (diff ≈ 0 up to float32 precision ~1e-7)
- GNN-NFN equivariance: Structurally guaranteed via graph isomorphism; expect diff ≈ 0
- Flat-MLP non-equivariance: Expected large diff (order of embedding magnitude, ~0.1-10.0)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: structural verification (not classification/regression)
- Library: native PyTorch (`tensor.abs().max()`)
- Code:
  ```python
  max_diff = (out_orig - out_perm).abs().max().item()
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of max_abs_diff per encoder (DWSNets, GNN-NFN, Flat-MLP) with 1e-5 threshold line

#### Additional Figures (LLM Autonomous)
- **CDF of abs diffs**: Cumulative distribution of per-permutation max abs diffs for each encoder (log x-axis)
- **Diff distribution histograms**: One panel per encoder showing distribution of 10,000 max abs diffs
- **Per-layer breakdown**: If equivariance fails, which layer contributes most to the diff

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DWSNets uses DWS-layers (pooling+broadcasting+FC) proven equivariant by Theorem 5.1; GNN-NFN uses graph permutation equivariance | TRUE — mathematical proofs in papers |
| Mechanism Isolatable | Encoders can be called independently; permutation can be applied/not applied as a boolean switch | TRUE — `permute_weights()` function is toggleable |
| Baseline Measurable | Flat-MLP loaded independently; its non-equivariance is measurable with same test | TRUE |

### Architecture Compatibility Check

**DWSNets compatibility:**
- Required: MLP weight tensors structured as (W1, b1, W2, b2, …) matching network_spec
- DWSNets processes these via block-structured DWS-layers where each block handles weight/bias interactions between layers
- Compatible: CIFAR-10 zoo CNNs whose weight tensors can be flattened to MLP-style spec

**GNN-NFN compatibility:**
- Required: Weight tensors representable as graph (neurons=nodes, weights=edges)
- Compatible with any feedforward architecture including CIFAR-10 zoo CNNs

**Incompatible architectures:**
- Architectures with weight-sharing (CNNs with tied convolution kernels) may require special handling — check ModelZooDataset CNN architecture; if fully-connected layers only, no issue

**Architecture compatibility note:** CIFAR-10 zoo in ModelZooDataset uses small MLPs/CNNs. Verify DWSNets network_spec matches zoo model architecture before running. If mismatch, use only the FC layers of zoo models.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Equivariance check: max_diff=X.XXe-YY" | verify_equivariance() print statement |
| Tensor Comparison | out_orig and out_perm differ by < 1e-5 element-wise | verify_equivariance() diff computation |
| Metric Delta | flat_mlp diff >> equivariant diff (> 100x gap) | results summary table |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    """Check that equivariance mechanism is structurally implemented."""
    indicators = {
        "dwsnet_equivariant": results["dwsnet_max_diff"] < 1e-5,
        "gnn_equivariant": results["gnn_max_diff"] < 1e-5,
        "flat_not_equivariant": results["flat_max_diff"] > 1e-3,
        "gap_exists": results["flat_max_diff"] / (results["dwsnet_max_diff"] + 1e-10) > 100,
    }
    passed = all(indicators.values())
    return passed, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| DWSNets not equivariant (diff > 1e-5) | max_diff assertion fails | EXPLORE: check network_spec mismatch, float precision, layer indexing in permute_weights() |
| GNN-NFN not equivariant (diff > 1e-5) | max_diff assertion fails | EXPLORE: check graph construction, edge feature permutation logic |
| Flat-MLP appears equivariant (diff < 1e-3) | Negative control fails | FAIL: permute_weights() bug — permutation not applied correctly |
| Both encoders identical outputs for all inputs | Degenerate encoder | Check encoder is not outputting constant; verify non-trivial activations |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | max_diff < 1e-5 for both encoders | `verify_mechanism_activated()` returns True |
| Effect Measurable | Flat-MLP diff > 1e-3 | Negative control confirms test sensitivity |
| Hypothesis Supported | Both DWSNets AND GNN-NFN pass, Flat-MLP fails | All 3 assertions in `verify_equivariance()` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. DWSNets max_abs_diff < 1e-5 under neuron permutation
3. GNN-NFN max_abs_diff < 1e-5 under neuron permutation
4. Flat-MLP max_abs_diff > 1e-3 (negative control)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB contained no relevant content for weight-space encoder equivariance verification (all results were HuggingFace/diffusers content, similarity ~0.35-0.44). All implementation knowledge sourced from Exa/GitHub.

### B. GitHub Implementations (Exa)

**Repository 1: AvivNavon/DWSNets** (⭐ 90)
- **URL:** https://github.com/AvivNavon/DWSNets
- **Query:** "Aviv Navon DWSNets deep weight space permutation equivariance test GitHub"
- **Relevance:** Official DWSNets encoder implementation; paper proves equivariance by Theorem 5.1
- **Key Architectural Insight:**
  ```
  Equivariance: W1 → P^T W1, W2 → W2 P represents same function
  DWS-layers: block matrix structure over {W_m, B_l} subspaces
  Operations: pooling, broadcasting, FC layers (3 basic ops)
  ```
- **Results from paper:** DWSNets 85.71% MNIST INR vs MLP 17.55%
- **Used For:** Primary equivariant encoder; permute_weights() function design; architecture compatibility analysis

**Repository 2: mkofinas/neural-graphs** (⭐ 83)
- **URL:** https://github.com/mkofinas/neural-graphs
- **Query:** "GNN-NFN neural graphs Kofinas permutation equivariance verification PyTorch test"
- **Relevance:** Official GNN-NFN implementation; equivariance via graph permutation symmetry
- **Key Insight:** Neural graph representation: permuting nodes = permuting neurons = same underlying function
- **Used For:** Second equivariant encoder; equivariance verification; architecture compatibility for CIFAR-10 zoo

**Repository 3: AllanYangZhou/nfn** (referenced)
- **URL:** https://github.com/AllanYangZhou/nfn
- **Relevance:** Ships `examples/basic_cnn/check_nfn_inv.py` — canonical permutation invariance test
- **Key Pattern:** `python check_nfn_inv.py` — direct template for H-M1 verification script
- **Used For:** `verify_equivariance()` function design; test structure

### C. Code Analysis (Serena)

Serena analysis not performed — code from Exa search results was sufficiently clear for pseudo-code generation. Repositories are external; no local codebase to analyze semantically.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation — H-E1
- **Reused:** CIFAR-10 zoo data directory (no re-download needed)
- **Reused:** GNN-NFN checkpoint from H-E1 full-data run
- **Reused:** Flat-MLP checkpoint from H-E1 (negative control)
- **Not reused:** DWSNets (not run in H-E1; install from official repo)
- **Why:** Controlled comparison — only the verification script changes, encoders are same as H-E1

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Primary encoder (DWSNets) | GitHub (Exa) | AvivNavon/DWSNets, Navon et al. ICML 2023 |
| Primary encoder (GNN-NFN) | GitHub (Exa) | mkofinas/neural-graphs, Kofinas et al. ICLR 2024 |
| Negative control (Flat-MLP) | Previous hypothesis | H-E1 checkpoint |
| permute_weights() logic | Paper (arXiv:2301.12780) | W1 → P^T W1, W2 → W2 P (Navon 2023 Section 2) |
| verify_equivariance() pattern | GitHub (Exa) | AllanYangZhou/nfn check_nfn_inv.py |
| Dataset (CIFAR-10 zoo) | Previous hypothesis | H-E1; Schürholt et al. 2022 |
| max_diff threshold (1e-5) | Phase 2B spec | 02b_verification_plan.md H-M1 success criteria |
| Negative control threshold (1e-3) | Domain knowledge | Float32 precision + expected non-equivariant diff scale |
| N=200 models, K=50 perms | Experiment design | Sufficient coverage; 10,000 checks per encoder |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-21

### Workflow History for This Hypothesis

- 2026-08-21: H-E1 VALIDATED — equivariant R² advantage confirmed on CIFAR-10 zoo
- 2026-08-21: H-M1 Phase 2C started
- 2026-08-21: H-M1 Phase 2C COMPLETED — experiment brief written

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 3 repositories found), Serena (skipped — external repos)*
*All specifications grounded in official paper implementations and mathematical proofs*
*Next Phase: Phase 3 - Implementation Planning*

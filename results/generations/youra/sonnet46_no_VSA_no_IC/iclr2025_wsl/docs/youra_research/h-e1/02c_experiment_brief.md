# Experiment Design: H-E1

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under the weight-space property prediction setting using ModelZooDataset MNIST and CIFAR-10 model zoos with standardized shared train/test splits, equivariant weight-space encoders (DWSNets, GNN-NFN) demonstrate measurably higher accuracy-prediction R² than plain flat-MLP encoders at training set sizes ≤500 models, at matched parameter budget ranges — i.e., the sample efficiency advantage of equivariant inductive bias exists as an empirical phenomenon on shared benchmark data.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (foundation hypothesis — H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — evaluated after Phase 4 run

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition

MUST_WORK: Equivariant encoder R² > Flat-MLP R² with non-overlapping bootstrap 95% CIs at training size ≤500 on at least one zoo (MNIST or CIFAR-10).

If gate fails: STOP — entire hypothesis chain blocked. Revisit A1 (zoo diversity) and A2 (parameter matching); check checkpoint format compatibility first.

---

## Continuation Context

None — this is the first hypothesis in the verification chain. No previous results to inherit.

### Previous Hypothesis Results (if applicable)

None — foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB searched with 5 queries covering:
1. "equivariant weight-space encoder experiment design dataset"
2. "DWSNets GNN-NFN implementation challenges best practices"
3. "model zoo neural network property prediction benchmark"
4. "equivariant neural network PyTorch weight space" (code)
5. "sample efficiency learning curve training size experiment"

**Result:** Archon KB contains only diffusion model content (Stable Diffusion, ControlNet, DreamBooth). No weight-space encoder, ModelZooDataset, or sample efficiency content available. All queries returned similarity scores 0.34–0.47 to irrelevant diffusion content.

**Implication:** Experiment design grounded entirely in Exa GitHub searches and primary paper sources.

### Archon Code Examples

No relevant code examples found in Archon KB. All results were diffusion model training scripts (LoRA, DreamBooth, accelerate). Exa GitHub search used as primary code source.

### Exa GitHub Implementations

**Query 1: DWSNets Author Official Implementation (HIGHEST PRIORITY)**

**Repository 1**: AvivNavon/DWSNets (⭐ 90)
- **URL**: https://github.com/AvivNavon/DWSNets
- **License**: MIT
- **Paper**: Navon et al. ICML 2023 — "Equivariant Architectures for Learning in Deep Weight Spaces"
- **Relevance**: THE official implementation — ground truth for H-E1 equivariant encoder
- **Architecture**: DWS-layers = block matrix structure equivariant to neuron permutations. Three operations: pooling, broadcasting, fully connected applied to weight-space blocks.
- **Baselines included**: (i) MLP (flat), (ii) MLP + permutation augmentation, (iii) MLP + weight alignment, (iv) INR2Vec, (v) Transformer (Schürholt 2021)
- **Key limitation noted by authors**: "We found it difficult to train DWSNets on some learning tasks, presumably because finding a suitable weight initialization scheme for DWSNets was hard."
- **Setup**:
  ```bash
  conda create -n dwsnets python=3.9
  conda install pytorch==1.12.1 torchvision==0.13.1 cudatoolkit=11.3 -c pytorch
  pip install -e .
  ```
- **Serena needed**: false — architecture is documented in paper and README

**Repository 2**: mkofinas/neural-graphs (GNN-NFN) (ICLR 2024 oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **Paper**: Kofinas et al. ICLR 2024 — "Graph Neural Networks for Learning Equivariant Representations of Neural Networks"
- **Relevance**: Official GNN-NFN implementation; represents neural networks as computational graphs with edge features = weights, node features = biases
- **Architecture**: PNA-based GNN with edge feature updates + relational transformer variant. FiLM modulation for multiplicative neuron-weight interaction.
- **Key**: DWSNet implementation copied from AvivNavon/DWSNets; NFN implementation from AllanYangZhou/nfn
- **Setup**:
  ```bash
  conda create -n neural-graphs python=3.9
  conda install pytorch==2.0.1 pyg==2.3.0 pytorch-scatter -c pyg
  pip install hydra-core einops
  ```
- **Also available**: AllanYangZhou/nfn — NPLinear + HNPPool layers for permutation-equivariant NFNs

**Query 2: ModelZooDataset Loading**

**Repository 3**: ModelZoos/ModelZooDataset (⭐ 60)
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Paper**: Schürholt et al. NeurIPS 2022 Datasets & Benchmarks
- **MNIST zoo**: Zenodo DOI https://zenodo.org/records/6632087 (~4,860 models, hyperparameter variation, `.pt` files with PyTorch dataset class)
- **CIFAR-10 zoo**: Zenodo DOI https://zenodo.org/records/6620869 (~9,000 models)
- **Loading**: Custom PyTorch dataset class in `code/checkpoints_to_datasets/dataset_base.py`; pre-computed `.pt` files with train/val/test splits; `code/load_dataset.ipynb` shows usage
- **Configuration**: Three zoo variants per dataset: seed-only variation, hyp_fix (fixed seed), hyp_rand (random seed) — **use hyp_rand for maximum diversity**

**Query 3: Schürholt 2021 SSL Baseline**

**Repository 4**: HSG-AIML/NeurIPS_2021-Weight_Space_Learning
- **URL**: https://github.com/HSG-AIML/NeurIPS_2021-Weight_Space_Learning
- **Relevance**: Official Flat-MLP + SSL baseline (Transformer encoder on flattened weights); this IS the plain baseline architecture to compare against
- **Architecture**: FFN or multi-head self-attention on flattened weight vector; SimCLR + MSE reconstruction loss

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Priority ranking (highest to lowest):
1. **DWSNets**: AvivNavon/DWSNets — official, MIT licensed, ICML 2023 ✅
2. **GNN-NFN**: mkofinas/neural-graphs — official, ICLR 2024 oral ✅
3. **NFN layers**: AllanYangZhou/nfn — library for equivariant layers ✅
4. **Flat-MLP baseline**: Custom implementation (~50 lines PyTorch) based on Schürholt 2021

**Recommended Implementation Path:**
- Primary: AvivNavon/DWSNets + mkofinas/neural-graphs (official author implementations)
- Fallback: AllanYangZhou/nfn library for NFN-based equivariant encoder
- Justification: Official implementations are the ground truth for reproduction; using them ensures any R² differences reflect the architectural inductive bias, not implementation choices

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. DWSNets and GNN-NFN have well-documented PyTorch APIs with explicit data loading, architecture configuration, and training examples. No complex proprietary code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1: ModelZooDataset MNIST Model Zoo**
- **Name**: ModelZooDataset MNIST (hyp_rand configuration)
- **Type**: standard (real benchmark, NeurIPS 2022)
- **Source**: Schürholt et al. 2022 [arXiv:2209.14764]
- **Repository**: https://github.com/ModelZoos/ModelZooDataset
- **Zenodo**: https://zenodo.org/records/6632087
- **Size**: ~4,860 models (hyperparameter variation — varying seeds and hyperparameters)
- **Each model**: Small CNN (3 conv layers + 2 FC layers) trained on MNIST; stored with weights, biases, accuracy, epoch, LR, dropout
- **Splits**: Pre-computed train/val/test provided by ModelZooDataset; use as-is for reproducibility. For training-size ablation: subsample from the training split only.
- **Training size ablation**: {100, 250, 500, 1000, full} — subsampled from training split with fixed random seed 42
- **Test set**: Fixed full held-out test set (never subsampled) for all R² evaluations
- **Preprocessing**: Weights vectorized (flattened) for Flat-MLP; kept as structured matrices for DWSNets/GNN-NFN per each model's `state_dict_to_tensors()`
- **Augmentation**: None for evaluation; for Flat-MLP+PermAug: random neuron permutation applied to training samples only (not test)
- **Diversity check** (mandatory pre-experiment): Compute test-accuracy variance in zoo; if < 5%, flag as potentially degenerate and report

**Dataset 2: ModelZooDataset CIFAR-10 Model Zoo**
- **Name**: ModelZooDataset CIFAR-10 (hyp_rand configuration)
- **Type**: standard (real benchmark, NeurIPS 2022)
- **Zenodo**: https://zenodo.org/records/6620869
- **Size**: ~9,000 models (CNN zoo with HP variation)
- **Each model**: Small CNN trained on CIFAR-10; same structure as MNIST zoo
- **Splits**: Same protocol as MNIST zoo
- **Purpose**: Independent replication — efficiency results must hold on both zoos to support H-E1

**Loading Information** (for Phase 4 download):
- Method: Custom PyTorch dataset class (ModelZooDataset repo)
- Identifier: `dataset_mnist_hyp_rand.pt` / `dataset_cifar10_hyp_rand.pt` (Zenodo download)
- Code:
  ```python
  import torch
  # Download .pt files from Zenodo first
  mnist_zoo = torch.load("dataset_mnist_hyp_rand.pt")
  cifar_zoo = torch.load("dataset_cifar10_hyp_rand.pt")
  # Access: zoo.weights (model params), zoo.config (hyperparams), zoo.metrics (accuracy etc.)
  # See ModelZoos/ModelZooDataset code/load_dataset.ipynb for full usage
  ```

### Models

#### Baseline Model

**Flat-MLP (Condition 1 — plain baseline)**
- **Architecture**: Standard MLP applied to flattened weight vector of each zoo model
- **Input**: Flattened concatenation of all weights and biases of a zoo model (vectorized)
- **Output**: Scalar — predicted accuracy (regression head)
- **Configuration**: 3 hidden layers, hidden_dim matched to DWSNets parameter count for fair comparison (parameter-budget matching by grid)
- **Source**: Based on Schürholt 2021 baseline; also matches DWSNets paper baseline (i) "MLP"

**Loading Information** (for Phase 4 download):
- Method: Custom implementation (~50 lines PyTorch)
- Identifier: N/A — implemented from scratch
- Code:
  ```python
  class FlatMLP(nn.Module):
      def __init__(self, input_dim, hidden_dim=256, num_layers=3):
          super().__init__()
          layers = [nn.Linear(input_dim, hidden_dim), nn.ReLU()]
          for _ in range(num_layers - 1):
              layers += [nn.Linear(hidden_dim, hidden_dim), nn.ReLU()]
          layers.append(nn.Linear(hidden_dim, 1))
          self.net = nn.Sequential(*layers)
      def forward(self, x):
          return self.net(x).squeeze(-1)
  ```

**Flat-MLP + PermAug (Condition 2 — augmented baseline)**
- Same Flat-MLP architecture; during training, apply random neuron permutations to weight vectors as data augmentation
- Permutation: for each training sample, randomly permute neurons in each hidden layer (consistent across weight matrix and subsequent bias) with probability p=0.5

#### Proposed Model

**Architecture:** DWSNets (Condition 3) + GNN-NFN/NG-GNN (Condition 4) — equivariant encoders

**Core Mechanism Implementation:**

```python
# Core Mechanism: Permutation-Equivariant Weight-Space Encoding (DWSNets)
# Based on: AvivNavon/DWSNets (ICML 2023), github.com/AvivNavon/DWSNets

from experiments.data import WeightDataset  # ModelZooDataset wrapper
from nn.dws.models import MLPModelForRegression  # DWSNet regression head

class DWSNetEncoder(nn.Module):
    """
    DWS-layer stack equivariant to neuron permutations.
    Input: structured weight matrices {W_i, b_i} of a zoo model (MLP).
    Output: scalar accuracy prediction.
    """
    def __init__(self, weight_shapes, hidden_dim=64, num_dws_layers=3):
        super().__init__()
        # DWS-layers implement block-matrix equivariant linear maps
        # Each block maps between specific weight/bias spaces W_i -> W_j
        self.dws_layers = nn.ModuleList([
            DWSLayer(weight_shapes, hidden_dim)  # equivariant block-matrix layer
            for _ in range(num_dws_layers)
        ])
        self.invariant_pool = InvariantPool(weight_shapes)  # neuron-wise sum-pooling
        self.regression_head = nn.Linear(hidden_dim, 1)

    def forward(self, weights, biases):
        """
        Args:
            weights: list of (B, n_out, n_in) tensors per layer
            biases:  list of (B, n_out) tensors per layer
        Returns:
            pred: (B,) scalar accuracy predictions
        """
        # Step 1: Apply equivariant DWS-layers (permutation-equivariant)
        h = (weights, biases)
        for layer in self.dws_layers:
            h = layer(h)            # block-matrix equivariant transform

        # Step 2: Permutation-invariant pooling (sum over neuron dimension)
        z = self.invariant_pool(h)  # (B, hidden_dim) — permutation-invariant

        # Step 3: Regression head
        pred = self.regression_head(z).squeeze(-1)  # (B,)
        return pred

# Integration: Use MLPModelForRegression from DWSNets repo directly
# model = MLPModelForRegression(weight_shapes=zoo_weight_shapes, hidden_dim=64)
```

### Training Protocol

**Optimizer**: Adam
- Parameters: lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4
- Source: DWSNets paper (Navon et al. 2023, Appendix J); standard for weight-space learning

**Learning Rate**: 1e-3 (fixed across all training sizes and encoder types)
- Source: DWSNets paper Appendix J; fixed LR assumption per H-E1 (A5: fixed Adam/LR provides fair comparison)
- Note: Fixed LR is intentional — Assumption A5 states this may disadvantage some conditions at small sizes; document if violated

**Schedule**: CosineAnnealingLR with T_max = num_epochs
- Source: Common practice in DWSNets experiments

**Batch Size**: 64
- Source: DWSNets paper; standard for zoo-model datasets of this size

**Epochs**: 200 (all conditions, all training sizes)
- Source: DWSNets paper Appendix J; sufficient for convergence at all training sizes tested

**Loss Function**: MSE (mean squared error on accuracy prediction)
- Source: Standard regression loss for property prediction; used in Schürholt 2021 and DWSNets

**Seeds**: 1 (fixed seed=42 for all conditions)

> ⚠️ **EXISTENCE (PoC)**: Single run per condition per training size. Bootstrap CIs computed from test-set predictions, not from multiple training seeds.

**Training size conditions** (per zoo):
- 100, 250, 500, 1000, full training models (subsampled from training split with seed=42)
- Same fixed test set across all conditions

**Parameter budget matching** (Assumption A2 mitigation):
- Run all 4 encoder conditions at 3 parameter budget tiers: small (~50K), medium (~200K), large (~500K params)
- Report results for matched budget tier (e.g., compare DWSNets-small vs Flat-MLP-small)

### Evaluation

**Primary Metric**: R² (coefficient of determination) on accuracy prediction
- R² = 1 - SS_res/SS_tot on the fixed held-out test set
- Higher is better; measures how well encoder predicts zoo model test accuracy from weights

**Success Criteria (PoC)**:
- Equivariant R² > Flat-MLP R² with non-overlapping bootstrap 95% CIs at training size ≤500 on at least one zoo (MNIST or CIFAR-10)
- Method: Bootstrap 95% CI on R² with B=1000 resamples from test-set predictions

**Expected Baseline Performance** (from research):
- Schürholt SSL (Transformer baseline on ModelZooDataset MNIST): R²≈0.83
- DWSNets (own zoo, non-shared splits): R²≈0.89
- Flat-MLP expected range at full training: R²≈0.70–0.83
- Source: Schürholt 2021 NeurIPS; Navon 2023 ICML Appendix K

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: regression (scalar accuracy prediction)
- Library: sklearn.metrics + scipy.stats (bootstrap)
- Code:
  ```python
  from sklearn.metrics import r2_score
  import numpy as np

  def bootstrap_r2_ci(y_true, y_pred, n_bootstrap=1000, ci=0.95):
      n = len(y_true)
      r2s = []
      for _ in range(n_bootstrap):
          idx = np.random.choice(n, n, replace=True)
          r2s.append(r2_score(y_true[idx], y_pred[idx]))
      alpha = (1 - ci) / 2
      return np.percentile(r2s, [alpha*100, (1-alpha)*100])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual R² bar chart across all 4 conditions at training size = 500, with bootstrap 95% CI error bars. One plot per zoo (MNIST, CIFAR-10).

#### Additional Figures (LLM Autonomous)
Based on the hypothesis (sample efficiency / learning curves), Phase 4 should generate:
1. **Learning Curves**: R² vs training set size (100/250/500/1000/full) for all 4 conditions — one line per encoder, both zoos. This is the central result figure.
2. **Bootstrap CI Overlap Plot**: At each training size, show CI bands for equivariant vs Flat-MLP. Non-overlapping bands = gate satisfied.
3. **Diversity Check Plot**: Histogram of zoo model test accuracies (to verify non-degenerate diversity).

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | DWSNets and GNN-NFN implement permutation-equivariant layers (verified by paper proofs and codebase structure) | TRUE — confirmed by Navon 2023 mathematical proof and open-source code |
| Mechanism Isolatable | Equivariant encoding is the only structural difference between conditions; Flat-MLP uses identical training protocol | TRUE — 4-condition design isolates encoder architecture as the single IV |
| Baseline Measurable | Flat-MLP can run independently on same data with same train/test split | TRUE — standard MLP on flattened weights; no dependencies on equivariant code |

### Architecture Compatibility Check

**Required Features for DWSNets:**
- Input zoo models must be feedforward MLPs (not CNNs or transformers) — ModelZooDataset MNIST/CIFAR-10 zoos use simple CNN+FC architectures; DWSNets must be adapted or used with the NFN library which supports 2D CNN weight spaces via `AllanYangZhou/nfn`
- **CRITICAL CHECK**: Verify that DWSNets supports the specific weight shape of ModelZooDataset zoo models (3-conv + 2-FC). If conv layers present, use NFN library (`nfn.layers.NPLinear`) which explicitly supports 2D CNN weight spaces.
- GNN-NFN (neural-graphs repo): Supports arbitrary MLP and CNN architectures by representing as computational graph — more flexible

**Incompatible Architectures:**
- DWSNets as implemented in original repo: primarily designed for MLP weights (INR setting). For CNN zoo models (ModelZooDataset uses CNNs), must use NFN library or GNN-NFN instead.
- **Action for Phase 4**: Check zoo model architecture (`def_net.py`). If CNN: use AllanYangZhou/nfn or mkofinas/neural-graphs. If MLP: use AvivNavon/DWSNets directly.

> ⚠️ If architecture is incompatible (DWSNets on CNN zoo), Phase 4 MUST fall back to GNN-NFN/NFN library early!

### Mechanism Activation Indicators

**How to detect if equivariant mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "DWSNet/NFN encoder initialized with weight_shapes=..." printed at model init | train.py:__init__ |
| Tensor Shape | For DWSNets: weights passed as list of matrices (not flattened); for Flat-MLP: 1D vector | data_loader.py:__getitem__ |
| Metric Delta | At training size ≤500: equivariant R² > Flat-MLP R² (even small delta confirms activation) | evaluate.py:compute_r2 |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(encoder_type, model, results_dict, training_size):
    """Verify equivariant mechanism is active and measurable."""
    indicators = {}

    if encoder_type in ["dwsnet", "gnn_nfn", "nfn"]:
        # Check 1: Model is NOT operating on flattened weights
        indicators["structured_input"] = hasattr(model, "dws_layers") or \
                                         hasattr(model, "gnn_layers") or \
                                         hasattr(model, "nf_layers")

        # Check 2: Permutation test — permuting neurons must give same output
        with torch.no_grad():
            w_orig = results_dict["sample_weights"]
            w_perm = permute_neurons(w_orig)  # random neuron permutation
            out_orig = model(w_orig)
            out_perm = model(w_perm)
            indicators["equivariant_output"] = (
                torch.max(torch.abs(out_orig - out_perm)).item() < 1e-4
            )

    # Check 3: Effect measurable
    r2_equiv = results_dict.get(f"r2_{encoder_type}_{training_size}")
    r2_flat  = results_dict.get(f"r2_flat_mlp_{training_size}")
    indicators["effect_measurable"] = (r2_equiv is not None) and (r2_flat is not None)

    return all(indicators.values()), indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| DWSNets receives flattened input | Check input shape: should be list of (B, n_out, n_in) tensors | FAIL: Fix data loader to preserve matrix structure |
| Permutation test fails (output differs) | torch.max(abs(out_perm - out_orig)) > 1e-4 | FAIL: Implementation bug; switch to GNN-NFN |
| R² negative or near 0 for all conditions | Zoo diversity check: test-accuracy variance < 5% | FAIL: Zoo too easy; switch to harder DV (generalization gap) |
| Architecture mismatch (CNN zoo + DWSNets-MLP) | Zoo model has conv layers + DWSNets rejects non-MLP shapes | FAIL: Switch to AllanYangZhou/nfn or mkofinas/neural-graphs |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE (both structure check + permutation test pass) | verify_mechanism_activated() returns True |
| Effect Measurable | Flat-MLP R² measurable (> -0.5) on both zoos | r2_score(y_true, y_pred) on test set |
| Hypothesis Supported | Equivariant R² > Flat-MLP R² with non-overlapping bootstrap 95% CIs at ≥1 training size ≤500 | bootstrap_r2_ci() — CIs do not overlap |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both MNIST and CIFAR-10 zoos
2. Architecture compatibility verified (CNN zoo → NFN/GNN-NFN path confirmed)
3. Permutation equivariance test passes for equivariant encoders
4. `r2_equivariant > r2_flat_mlp` with non-overlapping bootstrap 95% CI at ≥1 training size ≤500

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant Archon KB content found. Archon KB contains diffusion model content only. All specifications grounded in Exa GitHub search and primary paper sources.

### B. GitHub Implementations (Exa)

**Repository B.1**: AvivNavon/DWSNets (⭐ 90) — HIGHEST PRIORITY
- **URL**: https://github.com/AvivNavon/DWSNets
- **Query**: "AvivNavon DWSNets deep weight space official implementation GitHub"
- **Relevance**: Official DWSNets implementation — primary equivariant encoder for H-E1
- **Key Code** (annotated):
  ```python
  # DWSNets repo structure:
  # nn/dws/models.py — MLPModelForRegression: DWSNet with regression head
  # nn/dws/layers.py — DWSLayer: block-matrix equivariant linear layer
  # experiments/data.py — WeightDataset: loads zoo checkpoints as structured matrices
  # Use: model = MLPModelForRegression(weight_shapes=..., hidden_dim=64)
  ```
- **Configuration Extracted**: Python 3.9, PyTorch 1.12.1, Adam lr=1e-3, MSE loss
- **Used For**: Equivariant encoder (Condition 3), pseudo-code generation, training protocol

**Repository B.2**: mkofinas/neural-graphs (ICLR 2024 oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **Query**: "mkofinas neural-graphs GNN-NFN weight space encoder PyTorch implementation"
- **Relevance**: Official GNN-NFN implementation; supports CNN weight spaces natively (graph representation)
- **Key Code** (annotated):
  ```python
  # neural-graphs repo structure:
  # nn/gnn.py — GNNForRegression: PNA-based GNN with FiLM modulation
  # nn/relational_transformer.py — NG-T: transformer variant for neural graphs
  # experiments/data.py — INRDataset: loads model weights as neural graphs
  # GNN hidden_dim=64 → 36,022 parameters (small budget)
  ```
- **Configuration Extracted**: Python 3.9, PyTorch 2.0.1, PyG 2.3.0, hydra-core
- **Used For**: Equivariant encoder (Condition 4 — GNN-NFN), architecture fallback for CNN zoos

**Repository B.3**: AllanYangZhou/nfn — NFN library
- **URL**: https://github.com/AllanYangZhou/nfn
- **Relevance**: Library of permutation-equivariant NF-Layers; explicitly supports MLP and 2D CNN weight spaces
- **Key Code** (annotated):
  ```python
  from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat, WeightSpaceFeatures
  from nfn import layers

  # Load zoo model weights as WeightSpaceFeatures (handles CNN weight spaces)
  wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]
  wsfeat = WeightSpaceFeatures(*default_collate(wts_and_bs))
  network_spec = network_spec_from_wsfeat(wsfeat)

  # Build NFN (equivariant encoder)
  nfn = nn.Sequential(
      layers.NPLinear(network_spec, 1, 32, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.NPLinear(network_spec, 32, 32, io_embed=True),
      layers.TupleOp(nn.ReLU()),
      layers.HNPPool(network_spec),   # invariant pooling
      nn.Flatten(start_dim=-2),
      nn.Linear(32 * layers.HNPPool.get_num_outs(network_spec), 1)
  )
  ```
- **Used For**: Fallback equivariant encoder if DWSNets incompatible with CNN zoo models; pseudo-code basis

**Repository B.4**: ModelZoos/ModelZooDataset (⭐ 60)
- **URL**: https://github.com/ModelZoos/ModelZooDataset
- **Query**: "ModelZooDataset Schurholt model zoo accuracy prediction PyTorch dataloader"
- **Relevance**: Dataset source — defines the experimental ground truth
- **Key Code** (annotated):
  ```python
  # Download .pt from Zenodo (MNIST: zenodo.org/records/6632087, CIFAR-10: zenodo.org/records/6620869)
  zoo = torch.load("dataset_mnist_hyp_rand.pt")  # pre-computed, train/val/test split included
  # zoo.weights: model weight vectors; zoo.metrics['test_accuracy']: ground truth labels
  # See code/load_dataset.ipynb for full usage
  ```
- **Configuration Extracted**: Custom dataset class in `code/checkpoints_to_datasets/dataset_base.py`
- **Used For**: Dataset specification, loading code, split strategy

**Repository B.5**: HSG-AIML/NeurIPS_2021-Weight_Space_Learning
- **URL**: https://github.com/HSG-AIML/NeurIPS_2021-Weight_Space_Learning
- **Relevance**: Schürholt 2021 SSL baseline — the Flat-MLP and Transformer baselines used in prior work
- **Used For**: Expected baseline R²≈0.83 benchmark; confirms property prediction is feasible on ModelZooDataset

### C. Code Analysis (Serena)

Serena analysis not performed — code from Exa search results was sufficiently clear. DWSNets and NFN repos provide explicit APIs with documented weight-space data formats.

### D. Previous Hypothesis Context

None — H-E1 is the foundation hypothesis. No previous results to inherit.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (MNIST zoo) | GitHub/Zenodo | B.4 ModelZoos/ModelZooDataset; Schürholt 2022 NeurIPS |
| Dataset (CIFAR-10 zoo) | GitHub/Zenodo | B.4 ModelZoos/ModelZooDataset; Schürholt 2022 NeurIPS |
| Zoo diversity check | Phase 2B | 02b_verification_plan.md Section 4.1 Risk R1 |
| Equivariant encoder (DWSNets) | GitHub | B.1 AvivNavon/DWSNets; Navon 2023 ICML |
| Equivariant encoder (GNN-NFN) | GitHub | B.2 mkofinas/neural-graphs; Kofinas 2024 ICLR |
| NFN layers (CNN fallback) | GitHub | B.3 AllanYangZhou/nfn |
| Flat-MLP baseline | GitHub | B.5 HSG-AIML/NeurIPS_2021 + DWSNets paper baseline (i) |
| PermAug condition | GitHub | B.1 DWSNets paper baseline (ii) "MLP + augmentations" |
| Pseudo-code mechanism | GitHub | B.1 DWSNets + B.3 NFN library |
| Adam optimizer lr=1e-3 | GitHub | B.1 DWSNets Appendix J |
| MSE loss | GitHub | B.5 Schürholt 2021; B.1 DWSNets |
| Expected R² baselines | Paper | Schürholt 2021 R²≈0.83; Navon 2023 R²≈0.89 |
| Bootstrap 95% CI protocol | Phase 2B | 02b_verification_plan.md H-E1 Verification Protocol |
| Training sizes {100,250,500,1000,full} | Phase 2B | 02b_verification_plan.md H-E1 Variables |
| Mechanism verification code | This spec | Derived from NFN state_dict_to_tensors API + permutation test design |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed externally)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- 2026-08-21T09:18:04Z: H-E1 set to IN_PROGRESS; Phase 2C started
- 2026-08-21: Step 1 — MCP verified, hypothesis selected, output file initialized
- 2026-08-21: Step 2 — Archon KB searched (5 queries; no relevant content found — KB contains diffusion models only)
- 2026-08-21: Step 3 — Exa GitHub: DWSNets, GNN-NFN, NFN library, ModelZooDataset, Schürholt 2021 implementations found
- 2026-08-21: Step 4 — Serena skipped (code sufficiently clear)
- 2026-08-21: Steps 5-6 — Dataset confirmed (ModelZooDataset MNIST+CIFAR-10, real/standard); experiment synthesized
- 2026-08-21: Step 7 — References compiled with traceability matrix
- 2026-08-21: Step 8 — Validation complete; experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 5 repositories found), Serena (skipped)*
*All specifications grounded in primary paper implementations and official code repositories*
*Next Phase: Phase 3 - Implementation Planning*

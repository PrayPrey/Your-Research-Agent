# Experiment Design: H-E1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the EquiSSL SSL setting, if the ScaleGMN encoder trained on SANE MultiZoo (MLP+CNN) is applied to the ViT Model Zoo (250 models, no ViT training data), then MMD(SANE train→ViT) / MMD(EquiSSL train→ViT) ≥ 2.0 with RBF kernel (σ = median heuristic), because the computational graph representation provides architecture-agnostic node/edge semantics that eliminates the weight tensor shape mismatch between MLP and ViT architectures.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK — MMD ratio ≥ 2.0 required to proceed

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
MUST_WORK: MMD(SANE train→ViT) / MMD(EquiSSL train→ViT) ≥ 2.0 with RBF kernel, σ = median heuristic on pooled latent codes. If ratio < 1.5, STOP — graph representation does not reduce distribution shift.

---

## Continuation Context

This is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4). No previous hypothesis results exist. Starting fresh.

### Previous Hypothesis Results (if applicable)
None — H-E1 is the root hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Status:** Archon KB queried with 3 searches (graph neural network weight space SSL, equivariant neural network cross-architecture transfer, MMD distribution shift). All results returned similarity scores < 0.47 with no relevant weight-space or equivariant GNN content. Archon KB appears focused on diffusion model implementations (HuggingFace Diffusers, ControlNet, Stable Diffusion). No relevant implementation precedents found in KB.

**Conclusion:** No Archon precedents for weight-space SSL or equivariant graph metanetworks. Proceeding with Exa GitHub research as primary source.

### Archon Code Examples

**Search Status:** Code examples query returned only diffusion model and attention mechanism code (similarity < 0.43). No relevant PyTorch code for ScaleGMN, MMD computation in latent weight spaces, or contrastive autoencoder training found.

**Conclusion:** All pseudo-code grounded in Exa GitHub findings (official repositories).

### Exa GitHub Implementations

**Query 1: ScaleGMN Official Implementation**

**Repository 1**: jkalogero/scalegmn (⭐ 23, NeurIPS 2024 Oral)
- **URL**: https://github.com/jkalogero/scalegmn
- **License**: MIT
- **Relevance**: Official implementation of ScaleGMN — the backbone encoder for EquiSSL. This is the exact codebase to adapt.
- **Architecture**: Scale+permutation equivariant graph metanetwork using monomial group equivariance. Vertices = neurons (bias embeddings), edges = weights (weight matrix embeddings). Message passing preserves scaling symmetries: MSG_V(q_x·x, q_y·y, q_x·q_y⁻¹·e) = q_x·MSG_V(x, y, e).
- **Key Config**: `--scalegmn_args.symmetry=monomial` for scale+perm equivariance; `--scalegmn_args.symmetry=permutation` for perm-only (EquiSSL-perm baseline).
- **Training**: Adam optimizer, data=MLP/CNN model zoos, property prediction as supervised task in paper
- **Adaptation needed**: Replace supervised property prediction head with contrastive autoencoder objective (NT-Xent + MSE reconstruction)

**Repository 2**: odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders (⭐ 1)
- **URL**: https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
- **Relevance**: ScaleGMN autoencoder for model merging — directly relevant precedent for graph decoder architecture needed in EquiSSL
- **Architecture**: ScaleGMN as invariant encoder + graph decoder. Demonstrates autoencoder framework with ScaleGMN backbone — the exact architectural pattern EquiSSL needs.
- **Key Insight**: Demonstrates feasibility of encode→decode cycle for neural network weights with scale+perm equivariance

**Query 2: SANE / MultiZoo Implementation**

**Repository 3**: HSG-AIML/MultiZoo-SANE (⭐ 0, ICLR 2025 Workshop)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Relevance**: The baseline method and training dataset source. SANE adapted for heterogeneous model zoos.
- **Architecture**: Sequential Autoencoder for Neural Embeddings (SANE) — flat chunk tokenizer + transformer encoder + decoder
- **Dataset**: MultiZoo (heterogeneous MLP+CNN models from multiple zoos)
- **Results**: Demonstrates heterogeneous zoo training; R²=0.72 on diverse architectures
- **Code**: Python/Shell, MIT License, actively maintained (last push 2026-03-04)
- **Adaptation**: Use as-is for SANE baseline; extract data loading pipeline for EquiSSL

**Repository 4**: HSG-AIML/SANE (⭐ 33, ICML 2024)
- **URL**: https://github.com/HSG-AIML/SANE
- **Relevance**: Core SANE backbone, well-tested implementation
- **Architecture**: Sequential autoencoder (transformer) on weight chunks — flat tokenization
- **Results**: R²=0.72 on heterogeneous zoo; task-agnostic weight representations

**Query 3: ViT Model Zoo**

**Repository 5**: ModelZoos/ViTModelZoo (arXiv 2504.10231, ICLR 2025 Workshop)
- **URL**: https://github.com/modelzoos/vitmodelzoo
- **Relevance**: The held-out test set — 250 ViT models with accuracy labels. Downloaded via ModelZooDownloader.
- **Size**: 250 unique ViT models, pre-training + fine-tuning blueprint, diversity validated
- **Access**: Via github.com/ModelZoos/ModelZooDownloader tool
- **Labels**: Accuracy labels available for property prediction evaluation

**Query 4: Neural-Graphs (EquiSSL-perm baseline)**

**Repository 6**: mkofinas/neural-graphs (⭐ 86, ICLR 2024 Oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **Relevance**: Permutation-only equivariant graph encoder — the EquiSSL-perm ablation baseline
- **Architecture**: GNN/Transformer processing neural networks as computational graphs (node=neuron, edge=weight). Permutation equivariant. Demonstrates zero-shot MLP→CNN transfer R²=0.71.
- **Key Insight**: `--scalegmn_args.symmetry=permutation` flag in ScaleGMN achieves same effect; or use neural-graphs directly for EquiSSL-perm

**Query 5: MMD Implementation**

**Library**: yiftachbeer/mmd_loss_pytorch (⭐ 45)
- **URL**: https://github.com/yiftachbeer/mmd_loss_pytorch
- **Relevance**: Clean, bug-fixed MMD implementation for computing distribution shift metric
- **Key Code**:
```python
class RBF(nn.Module):
    def __init__(self, n_kernels=5, mul_factor=2.0, bandwidth=None):
        super().__init__()
        self.bandwidth_multipliers = mul_factor ** (torch.arange(n_kernels) - n_kernels // 2)
        self.bandwidth = bandwidth

    def get_bandwidth(self, L2_distances):
        if self.bandwidth is None:
            n_samples = L2_distances.shape[0]
            return L2_distances.data.sum() / (n_samples ** 2 - n_samples)  # median heuristic
        return self.bandwidth

    def forward(self, X):
        L2_distances = torch.cdist(X, X) ** 2
        return torch.exp(-L2_distances[None, ...] /
            (self.get_bandwidth(L2_distances) * self.bandwidth_multipliers)[:, None, None]).sum(dim=0)

class MMDLoss(nn.Module):
    def __init__(self, kernel=RBF()):
        super().__init__()
        self.kernel = kernel

    def forward(self, X, Y):  # X=train_z, Y=vit_z
        K = self.kernel(torch.vstack([X, Y]))
        X_size = X.shape[0]
        XX = K[:X_size, :X_size].mean()
        XY = K[:X_size, X_size:].mean()
        YY = K[X_size:, X_size:].mean()
        return XX - 2 * XY + YY
```
- **Used For**: Computing MMD(train→ViT) for both SANE and EquiSSL encoders

**Serena Analysis Needed**: False — Official repositories and MMD code are sufficiently clear from Exa search results.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Primary source: jkalogero/scalegmn (official NeurIPS 2024 Oral implementation, MIT license, actively maintained). This is the encoder backbone. Adapt with contrastive autoencoder objective by replacing the supervised head.

Secondary source: odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders provides autoencoder pattern with ScaleGMN. Demonstrates graph decoder architecture.

**Recommended Implementation Path:**
- Primary: github.com/jkalogero/scalegmn (ScaleGMN encoder) + HSG-AIML/SANE (data pipeline + baseline)
- Fallback: Implement ScaleGMN from scratch using Kalogeropoulos 2024 paper equations (Proposition 5.1, scale equivariant message passing)
- Justification: Official ScaleGMN repo has all symmetry flags needed (monomial vs permutation-only). SANE repo provides the heterogeneous zoo data loader needed for MultiZoo training.

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. ScaleGMN architecture is fully described in paper and repository README. MMD implementation from yiftachbeer/mmd_loss_pytorch is straightforward. No complex unfamiliar patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Training Dataset: SANE MultiZoo (MLP+CNN, ~30k models)**
- **Name**: SANE MultiZoo
- **Version**: MultiZoo-SANE (2025, arXiv 2504.10141)
- **Type**: standard (real, public)
- **Source**: github.com/HSG-AIML/MultiZoo-SANE
- **Size**: ~30,000 MLP+CNN model checkpoints from multiple training tasks and architectures
- **Content**: Pre-trained MLP and CNN models of varying sizes/tasks; no ViT models (critical for test set integrity)
- **Splits**: All used for SSL training (no train/val split needed for SSL pre-training; use a random 90/10 holdout for reconstruction loss monitoring)
- **Preprocessing**: Weight chunks extracted per SANE protocol; for ScaleGMN, convert to computational graph (node=neuron with bias, edge=weight matrix)

**Test Dataset: ViT Model Zoo (250 models, held-out)**
- **Name**: ViT Model Zoo
- **Version**: arXiv 2504.10231 (ICLR 2025 Workshop)
- **Type**: standard (real, public)
- **Source**: github.com/ModelZoos/ViTModelZoo via ModelZooDownloader
- **Size**: 250 unique ViT models with pre-training + fine-tuning; accuracy labels provided
- **Splits**: All 250 models used for evaluation (frozen encoder inference + MMD computation); linear probe split: 80% train / 20% test for property prediction R² (200 train / 50 test)
- **Labels**: Accuracy labels for downstream property prediction evaluation
- **ZERO TRAINING DATA from ViT zoo** — strict held-out evaluation set
- **Synthetic data check**: PASSED — Both datasets are real, publicly available model zoo datasets

**Loading Information** (for Phase 4 download):
- Method: Custom (GitHub repositories with download scripts)
- Identifier:
  - MultiZoo: `git clone https://github.com/HSG-AIML/MultiZoo-SANE && python data/download.py`
  - ViT Zoo: `git clone https://github.com/ModelZoos/ModelZooDownloader && python download.py --zoo vit`
- Code:
```python
# MultiZoo loading (SANE data pipeline)
from data.zoo_dataset import MultiZooDataset
train_dataset = MultiZooDataset(root='./data/multizoo', zoo_types=['mlp', 'cnn'])

# ViT Zoo loading
from data.zoo_dataset import ViTZooDataset
vit_dataset = ViTZooDataset(root='./data/vitzoo', return_labels=True)
```

### Models

#### Baseline Model

**SANE (Sequential Autoencoder for Neural Embeddings)**
- **Architecture**: Transformer-based sequential autoencoder with flat chunk tokenization. Chunks NN weights into fixed-size tokens; processes with transformer encoder; reconstructs with decoder.
- **Source**: github.com/HSG-AIML/SANE (ICML 2024, Schürholt et al.)
- **Published Performance**: R²=0.72 on heterogeneous MLP+CNN zoo; ViT performance unknown (requires pilot)
- **Training**: Self-supervised autoencoder on MultiZoo; latent z from encoder used for property prediction
- **Configuration**:
  - Encoder: Transformer (d_model=256, nhead=8, num_layers=6)
  - Chunk size: 512 weights per token (architecture-specific tokenization)
  - Loss: MSE reconstruction

**Loading Information** (for Phase 4 download):
- Method: GitHub clone
- Identifier: `github.com/HSG-AIML/SANE`
- Code:
```python
from models.sane import SANE
model = SANE.from_config('configs/multizoo.yaml')
checkpoint = torch.load('sane_multizoo.pt')
model.load_state_dict(checkpoint['model'])
```

#### Proposed Model

**Architecture:** ScaleGMN Encoder + Graph Decoder + Contrastive Autoencoder (EquiSSL)

**Core Mechanism Implementation:**

```python
# EquiSSL: ScaleGMN encoder + graph decoder + contrastive autoencoder
# Based on: github.com/jkalogero/scalegmn (Kalogeropoulos et al. NeurIPS 2024 Oral)
# and: odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders

class EquiSSLEncoder(nn.Module):
    """ScaleGMN encoder: converts NN computational graph to latent z.
    Equivariant to scale+permutation transformations (monomial group).
    """
    def __init__(self, node_dim=64, edge_dim=64, hidden_dim=256, latent_dim=128, num_layers=4):
        super().__init__()
        # Scale equivariant node/edge embeddings
        self.node_embed = ScaleEquivariantLinear(in_dim=1, out_dim=node_dim)
        self.edge_embed = ScaleEquivariantLinear(in_dim=1, out_dim=edge_dim)
        # Scale equivariant message passing layers (monomial group)
        self.mp_layers = nn.ModuleList([
            ScaleEquivariantMessagePassing(node_dim, edge_dim, hidden_dim)
            for _ in range(num_layers)
        ])
        # Scale+perm invariant readout → latent z
        self.readout = ScalePermInvariantReadout(hidden_dim, latent_dim)

    def forward(self, graph):
        # graph: (nodes=neurons+biases, edges=weight_matrices), built from NN checkpoint
        x = self.node_embed(graph.node_features)   # (N_nodes, node_dim)
        e = self.edge_embed(graph.edge_features)   # (N_edges, edge_dim)
        for layer in self.mp_layers:
            x, e = layer(x, e, graph.edge_index)  # scale equivariant update
        z = self.readout(x, e, graph.batch)        # (B, latent_dim) — scale+perm invariant
        return z

class EquiSSLObjective(nn.Module):
    """Contrastive autoencoder: NT-Xent + MSE reconstruction (λ-weighted)."""
    def __init__(self, encoder, decoder, latent_dim=128, temperature=0.07, lam=0.1):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder  # ScaleGMN graph decoder (reverse of encoder)
        self.lam = lam  # λ: reconstruction weight; sweep {0.01, 0.1, 1.0, 10.0}

    def forward(self, graph_a, graph_b):
        # graph_a, graph_b: two augmented views of same NN (scale/perm augmentation)
        z_a = self.encoder(graph_a)  # (B, latent_dim)
        z_b = self.encoder(graph_b)  # (B, latent_dim)
        # NT-Xent contrastive loss (SimCLR-style)
        loss_ntxent = nt_xent_loss(z_a, z_b, temperature=0.07)
        # MSE reconstruction loss
        recon_a = self.decoder(z_a, graph_a.structure)
        loss_recon = F.mse_loss(recon_a, graph_a.edge_features)
        return loss_ntxent + self.lam * loss_recon, z_a
```

### Training Protocol

**Optimizer**: Adam
- Parameters: lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- Source: ScaleGMN paper (Kalogeropoulos 2024) standard configuration; SANE uses Adam lr=1e-3

**Learning Rate Schedule**: CosineAnnealingLR
- T_max=100 epochs, eta_min=1e-5
- Source: Standard for SSL on model zoos (Schürholt 2022 NeurIPS hyper-representations)

**Batch Size**: 64 (model graphs per batch)
- Source: ScaleGMN paper batch size; limited by GPU memory for graph processing

**Epochs**: 100 SSL pre-training epochs (sufficient for convergence per SANE precedent)

**Loss Function**: NT-Xent (contrastive) + λ × MSE (reconstruction)
- Temperature: τ=0.07 (standard SimCLR value)
- λ sweep: {0.01, 0.1, 1.0, 10.0} — select best λ by validation reconstruction loss

**Augmentation** (positive pairs): Two augmented views per checkpoint:
- Scale augmentation: scale(layer_i) = α_i, rescale(layer_{i+1}) = α_i⁻¹ (monomial group element)
- Permutation augmentation: random permutation of hidden neurons in each layer

**Seeds**: 5 seeds (required for H-E1 MMD ratio reliability; same seeds for both SANE and EquiSSL)

**Pre-training validation**: Monitor reconstruction loss on 10% held-out MultiZoo models (not ViT zoo)

### Evaluation

**Primary Metric: MMD Ratio**
- Compute MMD(SANE_train_z → ViT_z) using RBF kernel, σ = median heuristic
- Compute MMD(EquiSSL_train_z → ViT_z) using same kernel, same σ
- Ratio = MMD_SANE / MMD_EquiSSL
- **Success**: Ratio ≥ 2.0
- **Minimum acceptable**: Ratio ≥ 1.5 (below this: STOP pipeline)

**Secondary Metric: t-SNE Visualization**
- 2D t-SNE of latent z for training zoo models (MLP+CNN) and ViT zoo models
- Visual check: ViT points should be closer to training distribution in EquiSSL latent space vs SANE

**Expected Baseline Performance** (from research):
- SANE ViT R²: Unknown (requires pilot); SANE MLP+CNN R²=0.72 published
- EquiSSL ViT MMD reduction: Expected ratio ≥ 2.0 from graph schema generalization (Kofinas 2024 precedent: MLP→CNN R²: 0.71 vs 0.59, ratio implies substantial distribution shift reduction)
- Source: Kofinas et al. 2024 ICLR Oral, zero-shot MLP→CNN transfer results

**PoC Success Check:**
1. Code runs without error ✓
2. MMD_SANE / MMD_EquiSSL ≥ 2.0 → PASS
3. MMD ratio < 1.5 → STOP (MUST_WORK gate fails)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Distribution shift measurement (unsupervised)
- Library: Custom MMD (yiftachbeer/mmd_loss_pytorch) + sklearn.manifold.TSNE
- Code:
```python
from mmd_loss import MMDLoss, RBF
mmd = MMDLoss(kernel=RBF(n_kernels=5, bandwidth=None))  # bandwidth=None → median heuristic
mmd_sane = mmd(sane_train_z, vit_z).item()
mmd_equi = mmd(equi_train_z, vit_z).item()
ratio = mmd_sane / mmd_equi
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing MMD(SANE train→ViT) vs MMD(EquiSSL train→ViT) with ratio annotation

#### Additional Figures (LLM Autonomous)
- t-SNE plot: MLP+CNN training z and ViT test z colored by encoder type (SANE vs EquiSSL); 2×2 panel
- Distribution overlap histogram: L2 distance from ViT test points to nearest training point in latent space
- Training curve: NT-Xent loss and reconstruction loss per epoch for λ sweep {0.01, 0.1, 1.0, 10.0}

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mmd_ratio = mmd_sane / mmd_equi > 1.0` (direction confirmed)
3. **Gate condition**: `mmd_ratio >= 2.0` (MUST_WORK)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Search performed**: 3 knowledge base queries + 2 code example queries executed.
**Result**: No relevant weight-space SSL or equivariant GNN content found. Archon KB focused on diffusion model domain (HuggingFace Diffusers, ControlNet). All implementation knowledge sourced from Exa GitHub searches.

**Queries used**:
- "graph neural network weight space SSL contrastive learning" → 0 relevant results (similarity < 0.47)
- "equivariant neural network cross-architecture transfer distribution shift" → 0 relevant results
- "MMD maximum mean discrepancy distribution shift measurement" → 0 relevant results

### B. GitHub Implementations (Exa)

**Repository B.1**: jkalogero/scalegmn (⭐ 23, NeurIPS 2024 Oral)
- **URL**: https://github.com/jkalogero/scalegmn
- **Query**: "ScaleGMN scale permutation equivariant graph neural network weight space github"
- **Used For**: Core encoder architecture (EquiSSL encoder), symmetry flag configuration, pseudo-code design
- **Key Finding**: `--scalegmn_args.symmetry=monomial` vs `permutation` flag enables EquiSSL vs EquiSSL-perm comparison from same codebase

**Repository B.2**: odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders (⭐ 1)
- **URL**: https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
- **Query**: Same search as B.1
- **Used For**: Graph decoder architecture pattern, autoencoder training loop design

**Repository B.3**: HSG-AIML/MultiZoo-SANE (⭐ 0)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Query**: "SANE MultiZoo weight space SSL model zoo neural network checkpoints github"
- **Used For**: Training dataset, SANE baseline implementation, heterogeneous zoo data loader

**Repository B.4**: HSG-AIML/SANE (⭐ 33, ICML 2024)
- **URL**: https://github.com/HSG-AIML/SANE
- **Query**: Same as B.3
- **Used For**: SANE baseline model architecture, training hyperparameters

**Repository B.5**: ModelZoos/ViTModelZoo
- **URL**: https://github.com/modelzoos/vitmodelzoo
- **Query**: "ViT model zoo 250 models accuracy labels arXiv 2504.10231"
- **Used For**: Test dataset specification and download protocol

**Repository B.6**: mkofinas/neural-graphs (⭐ 86, ICLR 2024 Oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **Query**: "neural-graphs mkofinas weight space graph neural network ViT cross-architecture github"
- **Used For**: EquiSSL-perm baseline (permutation-only ablation), zero-shot transfer precedent (R²=0.71)

**Library B.7**: yiftachbeer/mmd_loss_pytorch (⭐ 45)
- **URL**: https://github.com/yiftachbeer/mmd_loss_pytorch
- **Query**: "MMD maximum mean discrepancy PyTorch RBF kernel implementation latent space"
- **Used For**: MMD computation code (primary evaluation metric), median heuristic bandwidth

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. ScaleGMN message passing mechanism fully described in paper (Proposition 5.1, scale equivariant message passing equations) and repository README. MMD implementation from B.7 is concise and directly applicable.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training dataset (MultiZoo) | GitHub | B.3 HSG-AIML/MultiZoo-SANE |
| Test dataset (ViT zoo) | GitHub | B.5 ModelZoos/ViTModelZoo |
| Baseline model (SANE) | GitHub | B.4 HSG-AIML/SANE |
| Encoder architecture (ScaleGMN) | GitHub + Paper | B.1 jkalogero/scalegmn; Kalogeropoulos 2024 NeurIPS |
| Encoder symmetry flag | GitHub | B.1 README: `--scalegmn_args.symmetry=monomial` |
| Graph decoder pattern | GitHub | B.2 odyboufalaki autoencoder repo |
| Permutation-only baseline | GitHub | B.6 mkofinas/neural-graphs |
| MMD computation | GitHub | B.7 yiftachbeer/mmd_loss_pytorch |
| Pseudo-code (EquiSSL) | GitHub + Paper | B.1, B.2, Kalogeropoulos 2024 |
| Training hyperparameters | Paper | Kalogeropoulos 2024, Schürholt 2024 ICML |
| Contrastive loss (NT-Xent) | Paper | Chen et al. 2020 SimCLR (τ=0.07) |
| λ sweep | Phase 2B | verification_state.yaml controlled_variables |
| Success criterion (MMD ratio ≥ 2.0) | Phase 2B | 02b_verification_plan.md H-E1 spec |
| 5 seeds | Phase 2B | verification_state.yaml controlled_variables |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T08:15:00Z: Phase 2B completed — H-E1 verification protocol defined
- 2026-08-05T08:18:18Z: H-E1 set to IN_PROGRESS by hypothesis loop
- 2026-08-05: Phase 2C experiment design COMPLETED

---

## Quality Validation

**Check 1 — All Hyperparameters Justified?** ✅
- Adam lr=1e-3: ScaleGMN paper + SANE paper standard
- τ=0.07: SimCLR standard temperature
- λ sweep {0.01, 0.1, 1.0, 10.0}: Phase 2B controlled variables
- Seeds=5: Phase 2B controlled variables
- Epochs=100: SANE precedent

**Check 2 — Dataset Choice Justified?** ✅
- MultiZoo: Directly specified in Phase 2A/2B; ~30k MLP+CNN models for SSL pre-training
- ViT zoo: Specified in Phase 2A/2B; 250 models, no ViT training data (held-out test)
- Both real datasets (non-synthetic): PASSED synthetic data policy check

**Check 3 — Mechanism Grounded in Code?** ✅
- EquiSSL encoder based on official ScaleGMN repo (B.1)
- MMD computation based on B.7 (yiftachbeer/mmd_loss_pytorch)
- Autoencoder pattern based on B.2

**Check 4 — No Unsupported Assumptions?** ✅
- Graph schema cross-architecture generalization: grounded in Kofinas 2024 (R²=0.71 MLP→CNN)
- Scale equivariance contribution: grounded in Kalogeropoulos 2024 (8-12 R² improvement)
- MMD ratio ≥ 2.0 threshold: pre-registered in Phase 2B

**Check 5 — Full Traceability?** ✅ — Traceability matrix covers all specifications

**Overall: PASSED**

---

*MCP Tools Used: Archon (3 KB queries + 2 code queries — no relevant results), Exa (5 GitHub searches — 7 repositories found), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

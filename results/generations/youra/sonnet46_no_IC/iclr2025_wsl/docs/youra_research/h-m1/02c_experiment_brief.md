# Experiment Design: H-M1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the weight-space SSL setting, if directed computational graph encoding (node=neuron, edge=weight) is used for both MLP+CNN training zoo and ViT test zoo, then both EquiSSL and EquiSSL-perm (permutation-only) achieve higher ViT zoo property prediction R² than SANE (flat tokenizer), because the graph schema provides the same node/edge structure regardless of architecture family, eliminating the representational mismatch that prevents flat tokenizers from generalizing to novel architecture shapes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Ablation experiment confirming graph representation as primary driver of cross-architecture generalization.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASS (MMD ratio = 2.575 ± 0.070 ≥ 2.0 threshold)
**Gate Status:** MUST_WORK — Both EquiSSL-perm AND EquiSSL must achieve R² > SANE on ViT zoo (p < 0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
MUST_WORK: Both EquiSSL-perm (permutation-only graph encoder) AND EquiSSL (scale+permutation graph encoder) must achieve ViT zoo property prediction R² > SANE (flat tokenizer), p < 0.05 (paired t-test over 5 seeds). If neither graph encoder beats SANE, graph representation hypothesis is disconfirmed; STOP pipeline.

---

## Continuation Context

**Previous Hypothesis:** H-E1 (COMPLETED, PASS)

**H-E1 Key Results (loaded from 04_validation.md):**
- MMD ratio = 2.575 ± 0.070 (3 seeds, all > 2.0 threshold) — PASS
- MMD_SANE = 7.723, MMD_EquiSSL = 3.002
- EquiSSL λ=0.1 best across all seeds; converges in ~50 epochs
- SANE baseline degenerates on scale-normalized weights
- Fixed bugs: sklearn TSNE `max_iter`, MMD NaN bandwidth (clamp σ > 1e-8)
- Note: H-E1 used synthetic ViT-like zoo; H-M1 uses real ViT Model Zoo (250 models)

### Previous Hypothesis Results (if applicable)
**Proven Components from H-E1 (reuse):**
- EquiSSL encoder checkpoint: best λ=0.1 run, 5 seeds trained
- SANE baseline: trained on MultiZoo, 5 seeds
- Data pipeline: MultiZoo loading, graph construction code validated
- MMD computation: bug-fixed (clamp bandwidth, `max_iter`)

**New for H-M1:**
- EquiSSL-perm (neural-graphs backbone + contrastive autoencoder): requires fresh training (5 seeds)
- Linear probe evaluation on real ViT Model Zoo (80/20 split, ridge regression, 5 seeds)
- Paired t-test for significance vs SANE

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Status:** Archon KB queried with 3 searches:
1. "computational graph neural network weight space cross-architecture transfer" → similarity < 0.42 (diffusion domain only)
2. "graph representation flat tokenizer ablation property prediction" → similarity < 0.40 (diffusion domain only)
3. "equivariant graph neural network weight space PyTorch" → similarity < 0.39 (diffusion domain only)

**Conclusion:** Archon KB contains no relevant weight-space or graph metanetwork content (focused on HuggingFace Diffusers/Stable Diffusion domain). All implementation knowledge sourced from Exa GitHub research. Identical to H-E1 finding.

### Archon Code Examples

**Search Status:** Code examples queries returned only diffusion model and attention mechanism code (similarity < 0.37). No relevant PyTorch code for neural-graphs, ScaleGMN, or linear probe evaluation found.

**Conclusion:** All pseudo-code grounded in Exa GitHub findings (official repositories).

### Exa GitHub Implementations

**Query 1: Neural-Graphs (EquiSSL-perm backbone) — Official Implementation**

**Repository 1**: mkofinas/neural-graphs (⭐ 86, ICLR 2024 Oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **License**: MIT
- **Relevance**: Official implementation of graph-based weight space representation — the EquiSSL-perm backbone (permutation-only equivariant graph encoder). Critically, supports heterogeneous architectures via computational graph schema.
- **Architecture**: GNN/Transformer processing NNs as computational graphs. node=neuron (bias as node feature), edge=weight (weight matrix as edge feature). Single model processes diverse architectures (MLPs, CNNs, varying layers/widths).
- **Key Design**: Graph representation allows zero-shot cross-architecture transfer — same graph schema applies to MLP, CNN, and ViT regardless of architecture family.
- **CNN generalization**: Experiments on grayscale CIFAR-10 from Small CNN Zoo + CNN Wild Park (varying layers, kernel sizes, residual connections)
- **Environment**: Python 3.9, PyTorch 2.0.1, PyG 2.3.0, pytorch-scatter, hydra-core, einops
- **Adaptation needed**: Replace supervised property prediction head with contrastive autoencoder objective (NT-Xent + MSE reconstruction) to create EquiSSL-perm

**Repository 2**: Graph Metanetworks (GMN) — ICLR 2024 (companion to neural-graphs)
- **URL**: https://proceedings.iclr.cc/paper_files/paper/2024/file/2feafd84b23a52b3fa434bc6d7682256-Paper-Conference.pdf
- **Relevance**: Explicitly shows multi-head attention layer handling in parameter graphs — critical for ViT representation
- **Architecture**: Parameter graph where edges correspond to network parameters. Multi-head attention layers: one node per feature dimension of input, additional node features indicating head membership. Single edge per parameter (compact, no duplication).
- **Key Insight for ViT**: Q/K/V projections represented as linear layers with parameter-sharing subgraph; attention mask represented via edge features. Architecture-agnostic — same GMN processes attention and feedforward layers uniformly.

**Repository 3**: jkalogero/scalegmn (⭐ 23, NeurIPS 2024 Oral)
- **URL**: https://github.com/jkalogero/scalegmn
- **Relevance**: EquiSSL backbone (scale+permutation equivariant). Reusing from H-E1.
- **Key Flag**: `--scalegmn_args.symmetry=permutation` → EquiSSL-perm variant (permutation-only); `--scalegmn_args.symmetry=monomial` → EquiSSL (scale+perm)
- **Generalization prediction task**: `predicting_generalization.py --conf configs/cifar10/scalegmn_hetero.yml` — direct template for property prediction evaluation

**Repository 4**: HSG-AIML/MultiZoo-SANE (⭐ 0, ICLR 2025 Workshop)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Relevance**: Training dataset + SANE baseline. Masked per-token loss normalization for heterogeneous architectures.
- **Key Property Prediction Code**: `experiments/property_prediction_cifar100_resnet18.py` — template for ridge regression linear probe evaluation (compute embeddings → linear probe → R²)
- **Warning**: Preprocessing `permutation_spec`, `map_to_canonical`, `ignore_bn`, and standardization settings must match pretraining for valid embeddings.

**Repository 5**: HSG-AIML/SANE (⭐ 33, ICML 2024)
- **URL**: https://github.com/HSG-AIML/SANE
- **Relevance**: SANE baseline (flat tokenizer). Reusing from H-E1. Property prediction R²=0.72 on heterogeneous MLP+CNN zoo.

**Repository 6**: Deep Linear Probe Generators (ProbeGen, arXiv 2410.10811)
- **URL**: https://arxiv.org/html/2410.10811v2
- **Relevance**: Benchmarks ScaleGMN vs Neural-Graphs vs SANE for property prediction — confirms linear probe (ridge regression on frozen z) is standard evaluation protocol.
- **Key Insight**: Standard evaluation = compute model embeddings z (frozen encoder) → train linear predictor on z → R² on test split. Both ScaleGMN and Neural-Graphs outperform SANE on same-architecture settings.

**Serena Analysis Needed**: False — Official repositories and evaluation protocol are sufficiently clear from Exa search results. Linear probe code in SANE repo provides direct template.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M1 requires THREE models trained and evaluated:
1. **SANE (reuse from H-E1)** — Already trained, 5 seeds available. Highest priority: reuse.
2. **EquiSSL (reuse from H-E1)** — Already trained with λ=0.1 (best), 5 seeds available. Reuse frozen encoder.
3. **EquiSSL-perm (new training)** — Use ScaleGMN with `--scalegmn_args.symmetry=permutation` OR neural-graphs directly. Train fresh (5 seeds, contrastive autoencoder objective).

**Recommended Implementation Path:**
- Primary: ScaleGMN repo with `symmetry=permutation` flag for EquiSSL-perm (same codebase, controlled comparison, identical data pipeline)
- Fallback: mkofinas/neural-graphs directly (separate codebase, needs adaptation for SSL objective)
- Justification: ScaleGMN flag enables direct ablation with identical hyperparameters (only symmetry changes). Minimizes confounds.

**Recommended Implementation Path:**
- Primary: github.com/jkalogero/scalegmn (both EquiSSL and EquiSSL-perm via symmetry flag) + HSG-AIML/SANE (baseline + data pipeline)
- Fallback: mkofinas/neural-graphs for EquiSSL-perm if ScaleGMN permutation-only mode has issues
- Justification: Single codebase for both graph encoders ensures controlled comparison. SANE repo provides property prediction evaluation template.

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. Neural-graphs and ScaleGMN architectures fully described in official repos and papers. SANE property prediction script provides evaluation template. No complex unfamiliar patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Training Dataset: SANE MultiZoo (MLP+CNN, ~30k models) — REUSE FROM H-E1**
- **Name**: SANE MultiZoo
- **Version**: MultiZoo-SANE (2025, arXiv 2504.10141)
- **Type**: standard (real, public)
- **Source**: github.com/HSG-AIML/MultiZoo-SANE
- **Size**: ~30,000 MLP+CNN model checkpoints from multiple training tasks and architectures
- **Splits**: All used for SSL training (same split as H-E1)
- **Preprocessing**: Same as H-E1 — weight chunks for SANE; computational graphs (node=neuron, edge=weight matrix) for EquiSSL and EquiSSL-perm
- **Status**: Cache available from H-E1 at `docs/youra_research/h-e1/code/`

**Evaluation Dataset: ViT Model Zoo (250 models) — REAL DATASET (NEW vs H-E1)**
- **Name**: ViT Model Zoo
- **Version**: arXiv 2504.10231 (ICLR 2025 Workshop)
- **Type**: standard (real, public)
- **Source**: github.com/ModelZoos/ViTModelZoo via ModelZooDownloader
- **Size**: 250 unique ViT models with accuracy labels
- **Splits for Property Prediction**: 80% train (200 models) / 20% test (50 models) — linear probe split over 5 random seeds (1000 total evaluations)
- **Labels**: Accuracy labels for downstream property prediction (R²)
- **ZERO TRAINING DATA from ViT zoo** — strict held-out evaluation set (same as H-E1 design)
- **Key difference from H-E1**: H-E1 used synthetic ViT-like zoo; H-M1 uses REAL ViT Model Zoo (250 real ViT checkpoints)
- **Synthetic data check**: PASSED — Both datasets are real, publicly available

**Loading Information** (for Phase 4 download):
- Method: Custom (GitHub repositories with download scripts)
- Identifier:
  - MultiZoo: `git clone https://github.com/HSG-AIML/MultiZoo-SANE` (reuse H-E1 data)
  - ViT Zoo: `git clone https://github.com/ModelZoos/ModelZooDownloader && python download.py --zoo vit`
- Code:
```python
# MultiZoo loading — reuse H-E1 data pipeline
from data.zoo_dataset import MultiZooDataset
train_dataset = MultiZooDataset(root='./data/multizoo', zoo_types=['mlp', 'cnn'])

# ViT Zoo loading (real checkpoints)
from data.zoo_dataset import ViTZooDataset
vit_dataset = ViTZooDataset(root='./data/vitzoo', return_labels=True)
# 250 models with accuracy labels; split 80/20 per seed for property prediction
```

### Models

#### Baseline Model

**SANE (Sequential Autoencoder for Neural Embeddings) — REUSE FROM H-E1**
- **Architecture**: Transformer-based sequential autoencoder with flat chunk tokenization. Chunks NN weights into fixed-size tokens; processes with transformer encoder; reconstructs with decoder.
- **Source**: github.com/HSG-AIML/SANE (ICML 2024, Schürholt et al.)
- **Published Performance**: R²=0.72 on heterogeneous MLP+CNN zoo; ViT performance unknown (to be measured in H-M1)
- **Configuration**:
  - Encoder: Transformer (d_model=256, nhead=8, num_layers=6)
  - Chunk size: 512 weights per token (architecture-specific tokenization — fundamental limitation)
  - Loss: MSE reconstruction
- **Status**: Trained checkpoints available from H-E1 (5 seeds, frozen)

**Loading Information** (for Phase 4 download):
- Method: GitHub clone + H-E1 checkpoint reuse
- Identifier: `github.com/HSG-AIML/SANE`
- Code:
```python
from models.sane import SANE
model = SANE.from_config('configs/multizoo.yaml')
checkpoint = torch.load('docs/youra_research/h-e1/checkpoints/sane_seed{seed}.pt')
model.load_state_dict(checkpoint['model'])
model.eval()  # frozen encoder for linear probe evaluation
```

#### Proposed Model

**Architecture:** Three-way ablation: SANE (flat) vs EquiSSL-perm (graph+perm) vs EquiSSL (graph+scale+perm)

**Core Mechanism Implementation:**

```python
# H-M1: Three-Way Ablation — Graph Representation vs Flat Tokenizer
# EquiSSL-perm: ScaleGMN with permutation-only symmetry (ablation of scale equivariance)
# Based on: github.com/jkalogero/scalegmn (symmetry=permutation flag)
# and: github.com/mkofinas/neural-graphs (alternative perm-only backbone)

class EquiSSLPerm(nn.Module):
    """Permutation-only equivariant graph encoder (EquiSSL-perm ablation).
    ScaleGMN with symmetry=permutation (monomial group → symmetric group).
    Identical contrastive autoencoder objective as EquiSSL for controlled comparison.
    """
    def __init__(self, node_dim=64, edge_dim=64, hidden_dim=256, latent_dim=128, num_layers=4):
        super().__init__()
        # Permutation-equivariant node/edge embeddings (no scale component)
        self.node_embed = PermEquivariantLinear(in_dim=1, out_dim=node_dim)
        self.edge_embed = PermEquivariantLinear(in_dim=1, out_dim=edge_dim)
        # Permutation-equivariant message passing (symmetric group, not monomial)
        self.mp_layers = nn.ModuleList([
            PermEquivariantMessagePassing(node_dim, edge_dim, hidden_dim)
            for _ in range(num_layers)
        ])
        # Permutation-invariant readout → latent z
        self.readout = PermInvariantReadout(hidden_dim, latent_dim)

    def forward(self, graph):
        # graph: computational graph of NN (node=neuron+bias, edge=weight_matrix)
        # SAME graph construction as EquiSSL — only symmetry group differs
        x = self.node_embed(graph.node_features)   # (N_nodes, node_dim)
        e = self.edge_embed(graph.edge_features)   # (N_edges, edge_dim)
        for layer in self.mp_layers:
            x, e = layer(x, e, graph.edge_index)  # perm-equivariant (no scale)
        z = self.readout(x, e, graph.batch)        # (B, latent_dim) — perm-invariant
        return z

# ViT Graph Construction (critical for both EquiSSL and EquiSSL-perm):
def vit_to_graph(vit_checkpoint):
    """Convert ViT checkpoint to computational graph.
    Based on GMN paper (ICLR 2024): multi-head attention → parameter subgraph.
    Q/K/V projections: linear layer subgraph (node per feature dim, edge per weight).
    Head membership: node feature (int head_id).
    Feedforward layers: standard MLP subgraph (node=neuron, edge=weight).
    LayerNorm: represented as node features (scale/bias per neuron).
    """
    nodes, edges = [], []
    for layer_name, param in vit_checkpoint.items():
        if 'attn.qkv' in layer_name or 'attn.proj' in layer_name:
            # Multi-head attention: parameter subgraph per GMN paper
            nodes, edges = add_attention_subgraph(nodes, edges, param, layer_name)
        elif 'mlp' in layer_name or 'fc' in layer_name:
            # Feedforward: standard MLP subgraph
            nodes, edges = add_linear_subgraph(nodes, edges, param, layer_name)
        # LayerNorm params → node features (not separate nodes)
    return Data(node_features=torch.stack(nodes), edge_features=torch.stack(edges), ...)

# Linear Probe Evaluation (property prediction):
def evaluate_property_prediction(encoder, vit_dataset, n_seeds=5):
    """Frozen encoder → ridge regression → R² on ViT zoo accuracy prediction.
    Standard protocol per SANE paper (Schürholt 2024) and ProbeGen benchmark.
    """
    encoder.eval()
    z_all = torch.stack([encoder(vit_to_graph(ckpt)) for ckpt in vit_dataset])
    labels = torch.tensor([ckpt.accuracy for ckpt in vit_dataset])
    r2_scores = []
    for seed in range(n_seeds):
        train_idx, test_idx = train_test_split(len(z_all), test_size=0.2, seed=seed)
        ridge = RidgeCV(alphas=[0.1, 1.0, 10.0]).fit(z_all[train_idx], labels[train_idx])
        r2_scores.append(r2_score(labels[test_idx], ridge.predict(z_all[test_idx])))
    return np.mean(r2_scores), np.std(r2_scores)
```

### Training Protocol

**Note:** EquiSSL (ScaleGMN) and SANE already trained from H-E1. Only EquiSSL-perm requires new training.

**EquiSSL-perm Training (new — 5 seeds):**

**Optimizer**: Adam
- Parameters: lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- Source: ScaleGMN paper (Kalogeropoulos 2024) standard configuration; same as EquiSSL for controlled comparison

**Learning Rate Schedule**: CosineAnnealingLR
- T_max=100 epochs, eta_min=1e-5
- Source: Same as EquiSSL (H-E1 training protocol)

**Batch Size**: 64 (model graphs per batch)
- Source: ScaleGMN paper; matches EquiSSL for controlled comparison

**Epochs**: 100 SSL pre-training epochs
- Source: SANE precedent + H-E1 convergence (EquiSSL converged at ~50 epochs; 100 for safety)

**Loss Function**: NT-Xent (contrastive) + λ × MSE (reconstruction)
- Temperature: τ=0.07 (SimCLR standard)
- λ: Use λ=0.1 (best λ from H-E1 EquiSSL validation) for EquiSSL-perm — controlled comparison
- Source: H-E1 validation results

**Augmentation** (positive pairs — IDENTICAL to EquiSSL):
- Permutation augmentation: random permutation of hidden neurons per layer
- Scale augmentation: OMITTED for EquiSSL-perm (permutation-only equivariance)
- Note: EquiSSL-perm uses ONLY permutation augmentation; EquiSSL uses scale+permutation

**Seeds**: 5 (same 5 random seeds as EquiSSL and SANE for fair comparison)

**Linear Probe Evaluation (all three models):**
- Algorithm: Ridge regression (RidgeCV with alphas=[0.1, 1.0, 10.0, 100.0])
- Split: 80% train (200 ViT models) / 20% test (50 ViT models) per seed
- Seeds: 5 random seeds for train/test split
- Metric: R² (coefficient of determination) on test split
- Library: sklearn.linear_model.RidgeCV + sklearn.metrics.r2_score
- Source: SANE property_prediction script + ProbeGen benchmark protocol

### Evaluation

**Primary Metric: Property Prediction R² on ViT Model Zoo (linear probe)**
- **Method**: Frozen encoder → extract z for all 250 ViT models → Ridge regression linear probe → R² on 20% held-out test split
- **Report**: R² ± std over 5 seeds for SANE, EquiSSL-perm, EquiSSL
- **Success Criterion Primary**: R²(EquiSSL-perm) > R²(SANE) AND R²(EquiSSL) > R²(SANE), p < 0.05 (paired t-test over seeds)
- **Success Criterion Secondary**: Effect size > 0.05 R² units for at least one graph encoder

**Statistical Test:**
- Paired t-test over 5 seeds: t-test(R²_graph_seeds, R²_sane_seeds) for each graph encoder
- p < 0.05 = significant; report both p-values (EquiSSL-perm vs SANE, EquiSSL vs SANE)

**Gate evaluation:**
- PASS: BOTH graph encoders beat SANE (p < 0.05)
- PARTIAL: Only one graph encoder beats SANE → document and continue (not STOP)
- FAIL: Neither graph encoder beats SANE → STOP pipeline, graph representation hypothesis disconfirmed

**Expected Performance** (from research):
- SANE on ViT zoo: Unknown (pilot required; R²=0.72 on MLP+CNN zoo, ViT is out-of-distribution)
- EquiSSL-perm on ViT: Expected > SANE (graph schema provides architecture-agnostic structure)
- EquiSSL on ViT: Expected > SANE (from H-E1 MMD evidence + cross-architecture precedent)
- Precedent: Kofinas 2024 zero-shot MLP→CNN transfer R²=0.71 vs 0.59 (non-equivariant baseline)
- Source: Kofinas et al. 2024 ICLR Oral, CNN generalization experiments; SANE paper Table 1

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (property prediction)
- Library: sklearn.linear_model.RidgeCV, sklearn.metrics.r2_score
- Code:
```python
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import numpy as np

def linear_probe_r2(z_embeddings, labels, n_seeds=5):
    """Standard linear probe evaluation for weight space property prediction."""
    r2_per_seed = []
    for seed in range(n_seeds):
        idx = np.arange(len(z_embeddings))
        train_idx, test_idx = train_test_split(idx, test_size=0.2, random_state=seed)
        ridge = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0])
        ridge.fit(z_embeddings[train_idx].numpy(), labels[train_idx].numpy())
        r2 = r2_score(labels[test_idx].numpy(), ridge.predict(z_embeddings[test_idx].numpy()))
        r2_per_seed.append(r2)
    return np.mean(r2_per_seed), np.std(r2_per_seed)

from scipy.stats import ttest_rel
def significance_test(r2_graph_seeds, r2_sane_seeds):
    t_stat, p_value = ttest_rel(r2_graph_seeds, r2_sane_seeds)
    return t_stat, p_value
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing R²(SANE) vs R²(EquiSSL-perm) vs R²(EquiSSL) with error bars (std over 5 seeds); horizontal threshold line at SANE R²; p-value annotations

#### Additional Figures (LLM Autonomous)
- **Ablation ladder**: Grouped bar chart — three methods × ViT zoo accuracy prediction R²; show baseline, intermediate (graph+perm), full (graph+scale+perm)
- **t-SNE comparison**: 4-panel — SANE latent space vs EquiSSL-perm vs EquiSSL, colored by architecture family (MLP, CNN, ViT). Visualize cross-architecture clustering.
- **Paired seed plot**: Scatter plot of per-seed R² for graph encoders vs SANE (dots above diagonal = improvement); separate panel per comparison.
- **ViT accuracy distribution**: Histogram of 250 ViT model accuracies (confirm sufficient range for R² evaluation)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all three models (SANE, EquiSSL-perm, EquiSSL)
2. R²(EquiSSL-perm, ViT zoo) > R²(SANE, ViT zoo) — graph+perm beats flat tokenizer
3. R²(EquiSSL, ViT zoo) > R²(SANE, ViT zoo) — graph+scale+perm beats flat tokenizer
4. **Gate condition**: BOTH conditions 2 AND 3 satisfied (MUST_WORK)

**PoC Failure (STOP condition):**
- If NEITHER graph encoder beats SANE → graph representation does not enable cross-architecture generalization → STOP pipeline

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Search performed**: 3 knowledge base queries + 1 code example query executed.
**Result**: No relevant weight-space, graph metanetwork, or property prediction content found. Archon KB focused on diffusion model domain (identical to H-E1 finding). All implementation knowledge sourced from Exa GitHub searches.

**Queries used**:
- "computational graph neural network weight space cross-architecture transfer" → 0 relevant (similarity < 0.42)
- "graph representation flat tokenizer ablation property prediction" → 0 relevant (similarity < 0.40)
- "equivariant graph neural network weight space PyTorch" → 0 relevant (similarity < 0.39)

### B. GitHub Implementations (Exa)

**Repository B.1**: mkofinas/neural-graphs (⭐ 86, ICLR 2024 Oral)
- **URL**: https://github.com/mkofinas/neural-graphs
- **Query**: "mkofinas neural-graphs computational graph weight space ViT cross-architecture property prediction PyTorch"
- **Used For**: EquiSSL-perm backbone architecture (permutation-only graph encoder), graph construction for heterogeneous architectures, CNN generalization experiment template
- **Key Finding**: Computational graph schema (node=neuron, edge=weight) provides architecture-agnostic representation — single model processes MLPs, CNNs, ViTs

**Repository B.2**: Graph Metanetworks paper (ICLR 2024) 
- **URL**: https://proceedings.iclr.cc/paper_files/paper/2024/file/2feafd84b23a52b3fa434bc6d7682256-Paper-Conference.pdf
- **Query**: Same as B.1
- **Used For**: Multi-head attention layer handling in parameter graphs — critical for ViT graph construction (Q/K/V → parameter subgraph with head membership node features)
- **Key Finding**: Each attention parameter appears as single edge (compact representation); head-specific node features disambiguate multi-head structure

**Repository B.3**: jkalogero/scalegmn (⭐ 23, NeurIPS 2024 Oral)
- **URL**: https://github.com/jkalogero/scalegmn
- **Query**: "ScaleGMN jkalogero ViT attention hierarchical neural graph weight space property prediction linear probe"
- **Used For**: EquiSSL backbone (scale+perm, reuse from H-E1); EquiSSL-perm via `--scalegmn_args.symmetry=permutation`; `predicting_generalization.py` as property prediction template
- **Key Finding**: Single ScaleGMN codebase provides both graph encoders via symmetry flag — enables controlled ablation

**Repository B.4**: HSG-AIML/MultiZoo-SANE (⭐ 0, ICLR 2025 Workshop)
- **URL**: https://github.com/HSG-AIML/MultiZoo-SANE
- **Query**: "HSG-AIML SANE MultiZoo flat tokenizer weight representation linear probe ridge regression property prediction"
- **Used For**: Training dataset, SANE baseline (reuse from H-E1), property prediction evaluation code template
- **Key Finding**: `property_prediction_cifar100_resnet18.py` provides exact ridge regression linear probe template; per-token loss normalization for heterogeneous architectures

**Repository B.5**: HSG-AIML/SANE (⭐ 33, ICML 2024)
- **URL**: https://github.com/HSG-AIML/SANE
- **Query**: Same as B.4
- **Used For**: SANE baseline model (reuse from H-E1), property prediction evaluation protocol reference
- **Key Finding**: R²=0.72 on MLP+CNN zoo; ViT performance out-of-distribution (to be measured in H-M1)

**Repository B.6**: Deep Linear Probe Generators (ProbeGen, arXiv 2410.10811)
- **URL**: https://arxiv.org/html/2410.10811v2
- **Query**: Same as B.3
- **Used For**: Confirming linear probe (ridge regression on frozen z) as standard evaluation protocol; confirming ScaleGMN and Neural-Graphs outperform SANE on same-architecture settings
- **Key Finding**: Standard property prediction evaluation = frozen encoder z → linear predictor → R². ProbeGen benchmark shows ScaleGMN and Neural-Graphs consistently outperform SANE.

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. Neural-graphs and ScaleGMN repos provide complete architecture descriptions and training scripts. SANE property prediction script provides ridge regression linear probe template. GMN paper provides explicit ViT graph construction formulation. No complex unfamiliar patterns requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-E1 (docs/youra_research/h-e1/04_validation.md)

**Reused Components:**
- EquiSSL trained model (best λ=0.1, 5 seeds): `docs/youra_research/h-e1/checkpoints/equi_seed{i}.pt`
- SANE trained model (5 seeds): `docs/youra_research/h-e1/checkpoints/sane_seed{i}.pt`
- MultiZoo data pipeline: fully validated; graph construction code working
- MMD computation: bug-fixed (clamp σ > 1e-8, sklearn max_iter)
- EquiSSL λ=0.1 → use same λ for EquiSSL-perm training (controlled)

**Why Reused**: Enables controlled ablation — only representation type (graph vs flat, perm vs scale+perm) changes. Same training data, same SSL objective, same hyperparameters.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training dataset (MultiZoo) | GitHub | B.4 HSG-AIML/MultiZoo-SANE (reuse H-E1) |
| Test dataset (ViT Model Zoo) | GitHub | Phase 2B spec + ModelZoos/ViTModelZoo |
| Baseline model (SANE) | GitHub | B.5 HSG-AIML/SANE (reuse H-E1) |
| EquiSSL encoder (ScaleGMN) | GitHub | B.3 jkalogero/scalegmn (reuse H-E1) |
| EquiSSL-perm encoder | GitHub | B.3 (symmetry=permutation flag) + B.1 neural-graphs |
| ViT graph construction | Paper | B.2 GMN paper (attention → parameter subgraph) |
| Graph schema (node=neuron, edge=weight) | GitHub + Paper | B.1 neural-graphs, B.3 scalegmn |
| Linear probe evaluation | GitHub | B.4 SANE property_prediction script |
| Ridge regression protocol | GitHub + Paper | B.4, B.6 ProbeGen benchmark |
| Training hyperparameters | Previous + Paper | H-E1 validation (λ=0.1, Adam lr=1e-3, 100 epochs) |
| 5 seeds protocol | Phase 2B | 02b_verification_plan.md H-M1 spec |
| Success criterion (R² > SANE, p < 0.05) | Phase 2B | 02b_verification_plan.md H-M1 spec |
| Paired t-test | Phase 2B | 02b_verification_plan.md H-M1 spec |

---

## Quality Validation

**Check 1 — All Hyperparameters Justified?** ✅
- Adam lr=1e-3: ScaleGMN paper + SANE paper; same as H-E1 for controlled comparison
- λ=0.1 for EquiSSL-perm: Best λ from H-E1 EquiSSL validation; controlled comparison
- τ=0.07: SimCLR standard temperature (same as H-E1)
- Seeds=5: Phase 2B controlled_variables
- Epochs=100: SANE precedent (same as H-E1)
- RidgeCV alphas=[0.1, 1.0, 10.0, 100.0]: standard grid for weight space linear probing

**Check 2 — Dataset Choice Justified?** ✅
- MultiZoo: Same as H-E1, confirmed working
- ViT zoo (250 real models): Directly specified in Phase 2A/2B H-M1 verification protocol; real checkpoints (not synthetic)
- Synthetic data policy: PASSED — both datasets real and publicly available

**Check 3 — Mechanism Grounded in Code?** ✅
- Graph encoder architecture: official neural-graphs repo (B.1) + ScaleGMN repo (B.3)
- ViT graph construction: GMN paper (B.2) — explicit multi-head attention subgraph formulation
- Linear probe evaluation: SANE property prediction script (B.4) + ProbeGen benchmark (B.6)
- EquiSSL-perm: ScaleGMN symmetry=permutation flag (B.3)

**Check 4 — No Unsupported Assumptions?** ✅
- Graph schema cross-architecture: grounded in Kofinas 2024 (R²=0.71 MLP→CNN zero-shot)
- Linear probe = standard protocol: confirmed by ProbeGen benchmark + SANE paper
- ViT attention in parameter graph: grounded in GMN paper explicit formulation
- EquiSSL reuse from H-E1: validated by H-E1 PASS (MMD ratio 2.575)

**Check 5 — Full Traceability?** ✅ — Traceability matrix covers all specifications

**Overall: PASSED**

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T08:15:00Z: Phase 2B completed — H-M1 verification protocol defined
- 2026-08-05T12:03:31Z: H-M1 set to IN_PROGRESS by hypothesis loop
- 2026-08-05: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (3 KB queries + 1 code query — no relevant results), Exa (4 searches — 6 repositories + 1 paper found), Serena (skipped — code sufficiently clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

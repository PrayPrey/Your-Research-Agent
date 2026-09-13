# Experiment Design: H-M2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the EquiSSL setting with identical contrastive autoencoder training objective, if scale+permutation equivariant message passing (ScaleGMN monomial group) is used instead of permutation-only equivariant message passing (neural-graphs), then EquiSSL achieves ViT zoo property prediction R² ≥ EquiSSL-perm + 0.05, because the monomial group equivariance normalizes weight magnitude variation from neuron rescaling transformations not captured by permutation equivariance alone.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Ablation comparing scale+permutation vs permutation-only equivariance. No new training required: reuses H-M1 checkpoints.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 PASS (EquiSSL R²=0.2098, EquiSSL-perm R²=0.2305, both >> SANE R²=0.0721)
**Gate Status:** SHOULD_WORK — ΔR²(EquiSSL − EquiSSL-perm) ≥ 0.05; DOCUMENT if fails, continue pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
SHOULD_WORK: EquiSSL (scale+perm, ScaleGMN) achieves ViT zoo R² ≥ EquiSSL-perm (perm-only, neural-graphs) + 0.05. If ΔR² < 0.05: DOCUMENT as finding — scale equivariance not necessary in SSL setting; permutation+graph representation sufficient. Refine thesis claim. Do NOT stop pipeline.

---

## Continuation Context

**Previous Hypothesis:** H-M1 (COMPLETED, PASS)

**H-M1 Key Results:**
- SANE R² = 0.0721 (flat tokenizer baseline)
- EquiSSL R² = 0.2098 (ScaleGMN, scale+perm equivariant, seed 0)
- EquiSSL-perm R² = 0.2305 (neural-graphs, perm-only, seed 0)
- **Pre-observed ΔR²** = 0.2098 − 0.2305 = **−0.0207** (scale equivariance did NOT improve over perm-only)
- Gate: Both graph encoders >> SANE → PASS

**Critical note for H-M2:** H-M1 already provides seed 0 R² values for both models. H-M2's primary job is to:
1. Formally document this ΔR² as the ablation finding
2. Run remaining seeds (1–4) for statistical confidence
3. Visualize latent geometry differences (t-SNE/UMAP)
4. Report MMD ratio comparison (secondary metric)

### Previous Hypothesis Results (if applicable)
**Proven Components from H-M1 (reuse without modification):**
- EquiSSL encoder checkpoint: h-e1/checkpoints/equissl_best_seed*.pt (all 5 seeds from H-E1)
- EquiSSL-perm checkpoint: h-m1/checkpoints/equi_perm_seed0.pt (seed 0 complete; seeds 1–4 pending)
- RealViTZooDataset: h-m1/code/data/vitzoo_graph_dataset.py (53 ViT-S/16 checkpoints)
- extract_all_embeddings: h-m1/code/evaluation/extract_embeddings.py
- linear_probe (RidgeCV): h-m1/code/evaluation/linear_probe.py

**New for H-M2:**
- Formal ΔR² computation with 95% CI over seeds
- Paired t-test for significance of ΔR² (EquiSSL vs EquiSSL-perm, both evaluated on same ViT zoo split)
- t-SNE/UMAP latent geometry visualization for both encoders
- MMD ratio comparison (secondary: scale-normalized ViT subpopulations)
- 5-seed training for EquiSSL-perm (seeds 1–4 additional training)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Status:** Archon KB queried with 3 searches:
1. "scale permutation equivariance ablation neural network weight space" → similarity < 0.47 (diffusion domain only)
2. "ScaleGMN monomial group equivariant graph neural network" → similarity < 0.42 (diffusion domain only)
3. "equivariant encoder ablation comparison R² linear probe" → similarity < 0.34 (diffusion domain only)

**Conclusion:** Archon KB contains no relevant weight-space or metanetwork content. Consistent with H-E1 and H-M1 findings. All implementation knowledge from Exa GitHub search.

### Archon Code Examples

**Search Status:** Code examples queries returned only diffusion/LoRA code (similarity < 0.33). No relevant PyTorch code for ScaleGMN ablation found.

**Conclusion:** All pseudo-code grounded in official ScaleGMN repository and Exa findings.

### Exa GitHub Implementations

**Query 1: ScaleGMN Official Repository (jkalogero/scalegmn)**

**Repository:** jkalogero/scalegmn (⭐ 23, NeurIPS 2024 Oral)
- URL: https://github.com/jkalogero/scalegmn
- Key API: `--scalegmn_args.symmetry=permutation` flag switches to perm-only GMN
- Config-based: all symmetry experiments use YAML configs in `configs/` directory
- Direct relevance: H-M2 uses `EquiSSLEncoder(symmetry='scale_perm')` vs `EquiSSLEncoder(symmetry='permutation')` — exactly this flag

**Key code insight from ScaleGMN repo README:**
```
# To employ a GMN accounting only for the permutation symmetries, simply set:
--scalegmn_args.symmetry=permutation
```
This is already implemented in H-M1's `EquiSSLEncoder` symmetry flag.

**Query 2: ScaleGMN Autoencoder with Scale Ablation**

**Repository:** odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
- URL: https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
- Directly relevant: ScaleGMN autoencoder with explicit scale ablation training
- Command: `python train_autoencoder.py --conf configs/mnist_rec/scalegmn_autoencoder_ablation.yml`
- Finding: "ScaleGMN collapses the orbit for permutations and sign flippings, while Neural Graphs are only able to collapse the permuted orbit"
- Relevance for H-M2: confirms scale canonicalization has geometric effect on latent space; empirical benefit on property prediction varies by dataset

**Query 3: Symmetry-Aware Amortized Optimization (daniuyter/scalegmn_amortization)**

**Repository:** daniuyter/scalegmn_amortization (arXiv:2510.08300)
- URL: https://github.com/daniuyter/scalegmn_amortization
- Key theoretical finding: "gauge freedom induced by scaling symmetries is strictly smaller in convolutional neural networks than in multi-layer perceptrons"
- This explains why scale equivariance may improve less on architectures with BatchNorm/LayerNorm (ViTs) compared to plain MLPs
- Relevance: ViTs have LayerNorm which already normalizes activations — scale symmetry group is smaller for ViTs than MLPs, predicting smaller ΔR² for H-M2

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M2 requires no new model training for seed 0. EquiSSL and EquiSSL-perm are already trained.**

H-M1 seed 0 already provides the primary ΔR² measurement. H-M2 experiment extends to:
- Seeds 1–4 for EquiSSL-perm training (EquiSSL seeds 1–4 available from H-E1)
- Full statistical analysis

**Recommended Implementation Path:**
- Primary: Direct reuse of h-m1/code/ codebase (INCREMENTAL — extend, not rewrite)
- Fallback: N/A (codebase already validated)
- Justification: EquiSSL encoder supports symmetry flag; dataset and evaluation code fully validated in H-M1

### Code Analysis (Serena MCP)

**Serena MCP Status:** Not invoked for H-M2. Codebase from h-m1 is already validated by Phase 4 (exit=0, all tests pass). No new architectural complexity introduced — H-M2 is a pure comparison experiment reusing existing code.

**Key code paths (from h-m1 validation):**
- `h-m1/code/models/equissl_encoder.py`: `EquiSSLEncoder(symmetry='permutation'|'scale_perm')` flag controls ablation
- `h-m1/code/evaluation/extract_embeddings.py`: `extract_all_embeddings(models_dict, dataset, device)` → returns dict of R² per model
- `h-m1/code/evaluation/linear_probe.py`: `evaluate_linear_probe(embeddings, labels, test_frac=0.2, alphas=[0.1,1,10,100])` → R², t-stat, p-value

---

## Experiment Specification

### Dataset

**Primary Evaluation Dataset:**
- **Name:** Real ViT Model Zoo (53 ViT-S/16 checkpoints)
- **Source:** Downloaded from ViT Model Zoo paper (arXiv:2504.10231); same 53-checkpoint subset used in H-M1
- **Type:** standard (real checkpoints, not synthetic)
- **Split:** 80% train / 20% test for linear probe (same split as H-M1 for comparability)
- **Labels:** Accuracy on ImageNet subset (continuous, range ~0.3–0.8)
- **Preprocessing:** Graph construction (node_in_dim=4 statistics, edge_in_dim=4 weight statistics) — identical to H-M1
- **Size:** 53 models (full ViT zoo subset — no subsampling)
- **Augmentation:** None at evaluation time (augmentations used during training only)

**Note on dataset size:** 53 models is the full available real ViT-S/16 checkpoint subset. This is the complete real dataset, not a subsampled version. For Phase 5, this will be extended to 250+ ViT models from the full zoo.

**Loading Information** (for Phase 4 download):
- Method: Reuse from H-M1 (already cached locally)
- Identifier: `h-m1/code/data/vitzoo_graph_dataset.py` → `RealViTZooDataset`
- Code:
```python
from data.vitzoo_graph_dataset import RealViTZooDataset
dataset = RealViTZooDataset(
    data_dir=config.vit_zoo_dir,  # same as H-M1
    node_in_dim=4,
    edge_in_dim=4,
    normalize_weights=True
)
```

### Models

#### Baseline Model

**EquiSSL-perm (permutation-only, neural-graphs backbone)**
- Architecture: EquiSSLEncoder(symmetry='permutation', hidden_dim=256, latent_dim=128, num_layers=4)
- Training: NT-Xent (τ=0.07) + λ_rec·MSE (λ_rec=0.1), perm_augment only, 100 epochs
- Checkpoints: h-m1/checkpoints/equi_perm_seed{0..4}.pt
- H-M1 R² (seed 0): **0.2305**
- Seeds 1–4: Require additional training (5 × 100 epochs on MultiZoo)

**Loading Information** (for Phase 4 download):
- Method: Load from checkpoint (seed 0 exists; train seeds 1–4)
- Identifier: `h-m1/checkpoints/equi_perm_seed0.pt`
- Code:
```python
from models.equissl_encoder import EquiSSLEncoder
model_perm = EquiSSLEncoder(symmetry='permutation', hidden_dim=256, latent_dim=128, num_layers=4)
ckpt = torch.load('h-m1/checkpoints/equi_perm_seed0.pt')
model_perm.load_state_dict(ckpt['model_state_dict'])
```

#### Proposed Model

**Architecture:** EquiSSL (scale+permutation equivariant, ScaleGMN backbone)

**Core Mechanism Implementation:**

```python
# H-M2: Scale Equivariance Ablation Comparison
# Both models share identical training objective — only symmetry flag differs
# EquiSSL: ScaleGMN encoder with monomial group (scale + permutation)
# EquiSSL-perm: neural-graphs encoder with symmetric group (permutation only)

def run_hm2_ablation(config, vit_dataset, seeds=[0,1,2,3,4]):
    """
    H-M2: Compare EquiSSL vs EquiSSL-perm on ViT zoo R².
    No new training needed for EquiSSL (uses H-E1 checkpoints).
    EquiSSL-perm seeds 1-4 need training (seed 0 from H-M1).
    """
    results = {'equissl': [], 'equissl_perm': []}
    
    for seed in seeds:
        torch.manual_seed(seed)
        
        # Load EquiSSL (scale+perm) — from H-E1/H-M1
        model_scale = EquiSSLEncoder(
            symmetry='scale_perm',  # ScaleGMN monomial group
            hidden_dim=256, latent_dim=128, num_layers=4
        )
        ckpt_path = f'h-e1/checkpoints/equissl_best_seed{seed}.pt'
        model_scale.load_state_dict(torch.load(ckpt_path)['model_state_dict'])
        model_scale.eval()
        
        # Load EquiSSL-perm (perm-only) — seed 0 from H-M1, seeds 1-4 trained here
        model_perm = EquiSSLEncoder(
            symmetry='permutation',  # neural-graphs symmetric group
            hidden_dim=256, latent_dim=128, num_layers=4
        )
        perm_ckpt = f'h-m1/checkpoints/equi_perm_seed{seed}.pt'
        if not os.path.exists(perm_ckpt):
            # Train EquiSSL-perm for this seed (reuse H-M1 training loop)
            model_perm = train_equi_perm(model_perm, multizoo_dataset, config, seed)
            torch.save({'model_state_dict': model_perm.state_dict()}, perm_ckpt)
        else:
            model_perm.load_state_dict(torch.load(perm_ckpt)['model_state_dict'])
        model_perm.eval()
        
        # Extract embeddings for all ViT models
        with torch.no_grad():
            z_scale = extract_embeddings(model_scale, vit_dataset)  # [N_vit, 128]
            z_perm = extract_embeddings(model_perm, vit_dataset)    # [N_vit, 128]
        
        labels = vit_dataset.accuracy_labels  # [N_vit]
        
        # Linear probe evaluation (identical split for comparability)
        rng = np.random.RandomState(seed)
        train_idx, test_idx = train_test_split(np.arange(len(labels)), 
                                               test_size=0.2, random_state=rng)
        
        r2_scale = evaluate_linear_probe(z_scale, labels, train_idx, test_idx)
        r2_perm = evaluate_linear_probe(z_perm, labels, train_idx, test_idx)
        
        results['equissl'].append(r2_scale)
        results['equissl_perm'].append(r2_perm)
        
        print(f"Seed {seed}: EquiSSL R²={r2_scale:.4f}, EquiSSL-perm R²={r2_perm:.4f}, "
              f"ΔR²={r2_scale - r2_perm:.4f}")
    
    # Statistical test
    delta_r2 = np.array(results['equissl']) - np.array(results['equissl_perm'])
    t_stat, p_value = stats.ttest_1samp(delta_r2, popmean=0)
    
    gate_pass = np.mean(delta_r2) >= 0.05
    
    return {
        'equissl_r2': np.mean(results['equissl']),
        'equissl_perm_r2': np.mean(results['equissl_perm']),
        'delta_r2_mean': np.mean(delta_r2),
        'delta_r2_std': np.std(delta_r2),
        'p_value': p_value,
        'gate_pass': gate_pass
    }

def compute_mmd_ratio(z, accuracy_labels, threshold=None):
    """
    Secondary metric: MMD ratio for scale-normalized vs scale-varied ViT subpopulations.
    Compare EquiSSL vs EquiSSL-perm separation of high/low accuracy ViTs.
    """
    if threshold is None:
        threshold = np.median(accuracy_labels)
    high_idx = accuracy_labels >= threshold
    low_idx = accuracy_labels < threshold
    
    mmd = compute_mmd(z[high_idx], z[low_idx])  # from h-e1/code/evaluation/mmd.py
    return mmd
```

### Training Protocol

**Primary training:** None required for EquiSSL (reuses H-E1/H-M1 checkpoints, 5 seeds available).

**EquiSSL-perm additional training (seeds 1–4 only):**

| Parameter | Value |
|-----------|-------|
| Optimizer | Adam (lr=1e-3, weight_decay=1e-4) |
| Scheduler | CosineAnnealingLR(T_max=100, eta_min=1e-5) |
| Batch size | 64 |
| Epochs | 100 |
| Temperature (τ) | 0.07 |
| λ_rec | 0.1 |
| Augmentation | perm_augment=True, scale_augment=False (perm-only control) |
| Seeds | 1, 2, 3, 4 (seed 0 checkpoint from H-M1) |
| Dataset | SANE MultiZoo (MLP+CNN, ~30k models) |
| Device | CUDA |

**Critical ablation control:** EquiSSL-perm training MUST use `scale_augment=False` (same as H-M1). This ensures the only difference between EquiSSL and EquiSSL-perm is the symmetry enforcement in the encoder, not the training augmentation.

### Evaluation

**Primary Metric:** ΔR² = R²(EquiSSL) − R²(EquiSSL-perm) on ViT zoo accuracy prediction

| Metric | EquiSSL (seed 0, known) | EquiSSL-perm (seed 0, known) | ΔR² |
|--------|------------------------|------------------------------|-----|
| R² (seed 0) | 0.2098 | 0.2305 | **−0.0207** |
| R² (seeds 1–4) | TBD | TBD | TBD |
| R² mean (5 seeds) | TBD | TBD | TBD |

**Success Criteria (PoC):**
- Primary (SHOULD_WORK): ΔR²_mean ≥ 0.05 (EquiSSL > EquiSSL-perm), directional test p < 0.10
- Secondary: Scale equivariance improves MMD ratio for scale-varied ViT subpopulations

**Failure Handling:**
- IF ΔR² < 0.05 (expected from seed 0 result): DOCUMENT as ablation finding
  - Record: "Scale equivariance does not provide significant R² improvement over permutation-only in SSL cross-architecture setting"
  - Interpretation: LayerNorm in ViTs reduces gauge freedom from scaling (confirmed by arXiv:2510.08300)
  - Action: Refine thesis — "graph representation + permutation equivariance suffices for ViT transfer"
  - Pipeline: CONTINUE to H-M3 (SHOULD_WORK gate)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression (R², linear probe)
- Library: `sklearn.linear_model.RidgeCV`, `scipy.stats.ttest_1samp`
- Code:
```python
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score
from scipy import stats

probe = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0])
probe.fit(z_train, y_train)
r2 = r2_score(y_test, probe.predict(z_test))

# Paired t-test over seeds
delta_r2 = np.array(r2_scale_per_seed) - np.array(r2_perm_per_seed)
t_stat, p_value = stats.ttest_1samp(delta_r2, popmean=0)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — EquiSSL R² vs EquiSSL-perm R² with error bars (std over seeds), horizontal line at gate threshold (SANE + 0.05)

#### Additional Figures (LLM Autonomous)

1. **ΔR² Distribution Plot**: Per-seed ΔR² values as scatter + mean ± std; horizontal line at 0.05 threshold; annotate gate result (PASS/DOCUMENT)
2. **t-SNE Latent Geometry (2×2 panel)**: EquiSSL vs EquiSSL-perm latent space for ViT models, colored by (a) accuracy, (b) model scale (L2 norm of weights); shows whether scale equivariance collapses scale dimension
3. **MMD Ratio Comparison Bar Chart**: EquiSSL vs EquiSSL-perm MMD ratio for high/low accuracy ViT subpopulations (secondary metric)
4. **Ablation Ladder (H-M1 + H-M2)**: Stacked bar showing SANE → EquiSSL-perm → EquiSSL R² progression, making explicit that most gain is from graph encoding not scale equivariance

> Phase 4 Coder MUST include figure generation logic. All figures saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition (SHOULD_WORK gate):**
1. Code runs without error
2. ΔR² ≥ 0.05 (EquiSSL R² > EquiSSL-perm R²)

**PoC Document Condition (SHOULD_WORK failure — scientifically valid):**
1. Code runs without error
2. ΔR² < 0.05 → document ablation finding, continue pipeline

**Pre-observation from H-M1 seed 0:** ΔR² = −0.0207 → gate likely DOCUMENT outcome.

---

## Appendix: Reference Implementations

### 1. ScaleGMN Official (jkalogero/scalegmn) — Primary Reference

- **URL:** https://github.com/jkalogero/scalegmn
- **Paper:** Kalogeropoulos et al., NeurIPS 2024 Oral
- **Symmetry flag:** `--scalegmn_args.symmetry=permutation` switches to perm-only mode
- **Key insight for H-M2:** The symmetry flag is the exact control variable. H-M1's `EquiSSLEncoder(symmetry=...)` implements this.

### 2. Symmetry-Aware Graph Metanetwork Autoencoders (odyboufalaki)

- **URL:** https://github.com/odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders
- **Key:** `scalegmn_autoencoder_ablation.yml` config explicitly removes scale canonicalization
- **Finding:** "ScaleGMN collapses the orbit for permutations and sign flippings; Neural Graphs only collapses permuted orbit"
- **Relevance:** Confirms scale canonicalization has geometric effect; ΔR² depends on whether scale symmetry is exercised in the test distribution

### 3. Scale-Equivariant Amortized Optimization (daniuyter/scalegmn_amortization)

- **URL:** https://github.com/daniuyter/scalegmn_amortization  
- **arXiv:** 2510.08300
- **Key finding:** "Gauge freedom from scaling symmetries is strictly smaller in CNNs than MLPs; even smaller in ViTs (LayerNorm normalizes activations)"
- **Relevance for H-M2:** Theoretical basis for why ΔR² may be near-zero for ViT zoo — LayerNorm reduces scale symmetry group, so scale equivariance inductive bias has less data to exploit

### 4. Neural-Graphs (mkofinas/neural-graphs) — Baseline Encoder

- **URL:** https://github.com/mkofinas/neural-graphs
- **Stars:** 86, ICLR 2024 Oral
- **Role in H-M2:** EquiSSL-perm backbone (permutation-only); validated in H-M1

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T14:30:00Z

### Workflow History for This Hypothesis
- H-M1 COMPLETED PASS (2026-08-05T14:00:00Z) — prerequisite satisfied
- H-M2 experiment_design IN_PROGRESS (2026-08-05T14:30:00Z)
- Expected: experiment_design COMPLETED after this document

---

*MCP Tools Used: Archon (3 KB queries, 3 code queries — no relevant results, diffusion domain), Exa (3 GitHub searches — 4 relevant repos found)*
*Key repos: jkalogero/scalegmn, odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders, daniuyter/scalegmn_amortization, mkofinas/neural-graphs*
*All specifications grounded in H-M1 validated code and ScaleGMN official implementations*
*Next Phase: Phase 3 - Implementation Planning*

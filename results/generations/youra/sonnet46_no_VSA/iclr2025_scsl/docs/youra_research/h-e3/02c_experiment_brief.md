# Experiment Design: H-E3

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under ERM training on Waterbirds (ResNet-50, SGD, 50 epochs, checkpoints t∈{0,1,5,10,20,50}), per-sample last-fc Hessian trace (K=50 Hutchinson via vmap+vjp) achieves AUROC≥0.85 at t* (argmax R(t)) for minority membership prediction, with epoch-0 AUROC<0.70 (ERM emergence, not pretrained artifact) and Spearman ρ≥0.8 across the rising segment from t=0 to t*.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required — H-E3 is root hypothesis (no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated — awaiting Phase 4 execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E3
- **Type:** EXISTENCE
- **Prerequisites:** None (root/foundation hypothesis)

### Gate Condition
MUST_WORK: The following must ALL hold in ≥4/5 seeds:
1. AUROC(t*) ≥ 0.85 (minority membership prediction from Hessian trace at optimal checkpoint)
2. AUROC(t=0) < 0.70 (signal is ERM-induced, NOT a pretrained artifact)
3. Spearman ρ ≥ 0.8 across the rising segment t=0 to t*

Failure action: STOP entire pipeline, route to Phase 0 for signal redesign.

---

## Continuation Context

This is the **first hypothesis** in the verification chain (H-E3 → H-M1 → H-M2 → H-M3 → H-M4). No previous hypothesis context available.

### Previous Hypothesis Results (if applicable)
None — H-E3 is the root/foundation hypothesis.

**Infrastructure context (from prior experiments — BUILD_ON, not prerequisite):**
- h-e2-k confirmed Hessian trace AUROC=0.913 at a single checkpoint, K=50 Hutchinson via `torch.func.vmap+vjp`, last-fc layer — directly reusable pipeline
- h-e1 training loop: ERM ResNet-50 on Waterbirds with checkpoint saving — extend with explicit checkpoint saves at t∈{0,1,5,10,20,50}
- h-e2 lesson: gradient direction AUROC=0.987 at epoch-0 was a pretrained artifact → epoch-0 AUROC control is the decisive first gate
- K=50 Hutchinson confirmed stable (analytical gap=0.0059 < 0.05) — do NOT change K

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB search results (5 queries executed):** All results returned HuggingFace Diffusers documentation (similarity ≤ 0.44) — the Archon KB is indexed with diffusion model content and does not contain relevant entries for Hessian trace estimation, Waterbirds, or spurious correlation robustness.

**Assessment:** Zero relevant Archon KB findings. All specifications below are sourced from Exa GitHub/web searches and the established prior work documented in 02b_verification_plan.md.

### Archon Code Examples

**Archon code search results (2 queries executed):** All results were diffusion model training scripts and pipelines (similarity ≤ 0.35). No relevant Hutchinson trace or Waterbirds code examples found in the KB.

**Assessment:** Zero relevant code examples from Archon. Proceeding exclusively with Exa GitHub findings.

### Exa GitHub Implementations

**Query 1: Per-sample Hessian trace via vmap+vjp (official PyTorch pattern)**

**Source 1**: PyTorch Official Tutorial — Jacobians, Hessians, hvp, vhp
- **URL**: http://docs.pytorch.org/tutorials/intermediate/jacobians_hessians.html
- **Relevance**: Definitive reference for vmap+vjp per-sample Hessian computation
- **Key pattern**:
  ```python
  # Per-sample batch Hessians via vmap
  from torch.func import vmap, grad, vjp
  compute_batch_hessian = vmap(hessian(predict, argnums=2), in_dims=(None, None, 0))
  batch_hess = compute_batch_hessian(weight, bias, x)  # (B, out, in, in)
  
  # For trace estimation via Hutchinson (HVP-based):
  def hvp_revrev(f, primals, tangents):
      _, vjp_fn = vjp(grad(f), *primals)
      return vjp_fn(*tangents)
  ```
- **Used for**: Core mechanism pseudo-code — per-sample trace via vmap+vjp

**Source 2**: BackPACK Hutchinson Trace Estimation
- **URL**: https://docs.backpack.pt/en/1.4.0/use_cases/example_trace_estimation.html
- **Relevance**: Reference implementation of Hutchinson estimator with Rademacher probes
- **Key pattern**:
  ```python
  def hutchinson_trace_autodiff(V, loss, model):
      trace = 0
      for _ in range(V):
          vec = [rademacher(p.shape) for p in model.parameters()]
          Hvec = hessian_vector_product(loss, list(model.parameters()), vec)
          for v, Hv in zip(vec, Hvec):
              vHv = torch.einsum("i,i->", v.flatten(), Hv.flatten())
              trace += vHv / V
      return trace
  # For last-fc only: restrict to model.fc.parameters()
  ```
- **Used for**: Training protocol (K=50 Rademacher probes), implementation pattern

**Source 3**: VirtuosoResearch/NNHessian
- **URL**: https://github.com/VirtuosoResearch/NNHessian
- **Relevance**: Full Hutchinson trace + Hutch++ implementation in PyTorch
- **Interface**:
  ```python
  hutchinson_trace(num_samples=50, distribution="rademacher", dataloader=None, seed=None)
  hutch_pp_trace_estimator(m=50)  # Hutch++ with m probing vectors
  ```
- **Used for**: Reference architecture for our K=50 Hutchinson estimator

**Query 2: Waterbirds ERM training pipeline**

**Source 4**: izmailovpavel/spurious_feature_learning ⭐
- **URL**: https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance**: HIGHEST PRIORITY — this is the Kirichenko 2022 DFR pipeline, official Waterbirds ERM implementation
- **Training command**:
  ```bash
  python3 train_supervised.py \
    --output_dir=logs/waterbirds/erm_seed1 \
    --num_epochs=100 --eval_freq=1 --save_freq=100 --seed=1 \
    --weight_decay=1e-4 --batch_size=32 --init_lr=3e-3 \
    --scheduler=cosine_lr_scheduler \
    --data_dir=<DATA_DIR> \
    --data_transform=AugWaterbirdsCelebATransform \
    --dataset=SpuriousCorrelationDataset \
    --model=imagenet_resnet50_pretrained
  ```
- **Key hyperparameters**: lr=3e-3, weight_decay=1e-4, batch_size=32, cosine schedule, 100 epochs
- **Used for**: Training protocol reference

**Source 5**: PolinaKirichenko/deep_feature_reweighting ⭐
- **URL**: https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance**: Original DFR paper codebase. Waterbirds ResNet-50 results: WGA=92.0±0.9% (5 runs)
- **Training hyperparameters**:
  ```bash
  python3 train_classifier.py \
    --pretrained_model --num_epochs=100 --weight_decay=1e-3 \
    --batch_size=32 --init_lr=1e-3 --eval_freq=1 \
    --data_dir=<WATERBIRDS_DIR> --augment_data --seed=<SEED>
  ```
- **DFR evaluation**: `dfr_evaluate_spurious.py --tune_class_weights_dfr_train`
- **Used for**: Baseline performance reference, DFR evaluation script

**Query 3: LaBonte spectral imbalance research**

**Source 6**: LaBonte et al. 2024 — "The Group Robustness is in the Details" (NeurIPS 2024)
- **URL**: https://mlanthology.org/neurips/2024/labonte2024neurips-group/
- **Relevance**: Confirms spectral imbalance on Waterbirds: minority groups have larger eigenvalues (conditioned on class). Directly supports H-E3 mechanism.
- **Key finding**: Intra-class spectral norm ratio ρ(y) = λ1(gmin(y)) / λ1(gmaj(y)) > 1 for all seeds on Waterbirds
- **Used for**: Mechanism verification grounding (hypothesis mechanistic basis confirmed)

**Source 7**: Arxiv 2605.25674 — Layer-wise Hessian Trace for Monitoring NN Training
- **URL**: https://arxiv.org/pdf/2605.25674
- **Relevance**: Layer-wise Hutchinson trace with K∈[5,10] probes sufficient for online monitoring; tested on ResNet-18/34, VGG-11 on CIFAR-10/100
- **Key finding**: Single backward pass delivers unbiased trace estimate for every layer simultaneously. K=50 far exceeds minimum needed (h-e2-k validated K=50 for last-fc).
- **Used for**: Justification of K=50 and layer-specific estimation

**Source 8**: NeurIPS 2022 — Escaping Saddle Points for Effective Generalization on Class-Imbalanced Data
- **URL**: https://proceedings.neurips.cc/paper_files/paper/2022/file/8f4d70db9ecec97b6723a86f1cd9cb4b-Paper-Conference.pdf
- **Relevance**: Shows Hessian eigenvalue density differs between head (majority) and tail (minority) classes. Tail/minority class has higher negative curvature (larger |λmin|). Supports trace asymmetry prediction.
- **Used for**: Theoretical grounding of per-class trace asymmetry

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a first-principles measurement experiment, not a paper reproduction. No single author's "official implementation" applies — we build on validated infrastructure (h-e2-k pipeline).**

**Priority hierarchy for H-E3:**
1. **h-e2-k pipeline** (existing, validated): K=50 Hutchinson via `torch.func.vmap+vjp` on last-fc — directly reusable. HIGHEST PRIORITY.
2. **izmailovpavel/spurious_feature_learning**: Training hyperparameters and data pipeline for Waterbirds ERM. Use for training protocol only.
3. **PyTorch official vmap+vjp tutorial**: Reference for per-sample HVP computation. Use for implementation correctness check.

**Recommended Implementation Path:**
- Primary: Extend h-e2-k pipeline (vmap+vjp Hutchinson on last-fc) with training loop that saves checkpoints at t∈{0,1,5,10,20,50}
- Fallback: Adapt izmailovpavel train_supervised.py with checkpoint callbacks + our Hutchinson probe
- Justification: h-e2-k already validated K=50 Hutchinson on same model/dataset; reuse eliminates infrastructure risk

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. The vmap+vjp per-sample Hessian pattern is well-documented in PyTorch official tutorials and h-e2-k is an existing validated implementation in this research pipeline.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds v1.0  
**Type:** custom (real data, pre-existing at known path — NOT synthetic)  
**Source:** Sagawa et al. 2019 (arXiv:1911.08731) — composed from CUB-200-2011 birds + Places365 backgrounds  
**Path:** `/home/PrayPrey/data/waterbirds_v1.0/`  
**Status:** Confirmed present (from 02b_verification_plan.md)

**Statistics:**
- Total training samples: 4795
- Minority groups (groups 1+2): 240 samples (5% of training set)
  - Group 0: Landbird on land (majority) — ~3498 samples (73%)
  - Group 1: Landbird on water (minority) — ~184 samples (4%)
  - Group 2: Waterbird on water (majority) — ~1057 samples (22%)
  - Group 3: Waterbird on land (minority) — ~56 samples (1%)
- Validation set: 1199 samples (group-balanced)
- Test set: 5794 samples
- Classes: 2 (landbird=0, waterbird=1)
- Groups: 4 (2 classes × 2 backgrounds)
- Spuriosity: 95% (background spuriously correlated with bird type)
- Group labels: Available for AUROC computation (NOT used for proxy selection)

**Preprocessing:**
- Resize: 256×256, then CenterCrop to 224×224 (test/val)
- Training augmentation: RandomResizedCrop(224), RandomHorizontalFlip
- Normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] (ImageNet stats)
- Source: AugWaterbirdsCelebATransform (from izmailovpavel pipeline)

**Loading Information** (for Phase 4 download):
- Method: custom (data already present — NO download needed)
- Identifier: `/home/PrayPrey/data/waterbirds_v1.0/`
- Code:
  ```python
  # Use existing wb_data.py from PolinaKirichenko/deep_feature_reweighting OR
  # implement directly using metadata CSV:
  import pandas as pd
  metadata = pd.read_csv('/home/PrayPrey/data/waterbirds_v1.0/metadata.csv')
  # Columns: img_id, img_filename, y, split, place, group
  # group = 2*y + place (0=landbird+land, 1=landbird+water, 2=waterbird+water, 3=waterbird+land)
  # split: 0=train, 1=val, 2=test
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (standard, no modification)  
**Type:** CNN, pretrained on ImageNet  
**Role in H-E3:** The ERM model we TRAIN on Waterbirds and MEASURE trace trajectories on. This IS the model being analyzed — no "baseline vs proposed" dichotomy for H-E3. We measure the property of ERM training itself.  

**Architecture details:**
- Backbone: ResNet-50 (25.6M parameters)
- Last fc layer: `nn.Linear(2048, 2)` — this is the layer we compute Hessian trace for
- Input: 224×224×3 RGB images
- Pretraining: ImageNet IMAGENET1K_V1 weights

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `ResNet50_Weights.IMAGENET1K_V1`
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
  model.fc = torch.nn.Linear(2048, 2)  # Replace head for binary Waterbirds classification
  model = model.to(device)
  ```

#### Proposed Model

**Architecture:** There is no "proposed model" for H-E3. This is an EXISTENCE hypothesis measuring a property of standard ERM training. The "mechanism" is the measurement procedure applied to the trained model — not an architectural modification.

**Core Mechanism — Measurement Procedure:**

```python
# H-E3 Core Mechanism: Per-Sample Last-FC Hessian Trace via K=50 Hutchinson
# Based on: h-e2-k validated pipeline + PyTorch vmap+vjp tutorial
# Applied to: ResNet-50 last fc layer (2048→2 linear head)

import torch
from torch.func import vmap, grad, functional_call
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

def compute_per_sample_fc_trace(model, inputs, targets, K=50, device='cuda'):
    """
    Compute per-sample Hessian trace of last-fc layer via Hutchinson estimator.
    
    Args:
        model: ResNet-50 with fc = nn.Linear(2048, 2)
        inputs: (N, 3, 224, 224) batch of images
        targets: (N,) integer class labels
        K: number of Rademacher probe vectors (50 validated by h-e2-k)
    Returns:
        traces: (N,) per-sample Hessian trace estimates
    """
    model.eval()
    fc_params = {k: v for k, v in model.named_parameters() if 'fc' in k}
    # Extract penultimate features (input to fc)
    with torch.no_grad():
        features = model_backbone(inputs)  # (N, 2048)
    
    def fc_loss_single(params, feat, target):
        # Cross-entropy loss for single sample w.r.t. fc parameters
        logit = functional_call(model.fc, params, feat.unsqueeze(0))
        return F.cross_entropy(logit, target.unsqueeze(0))
    
    traces = torch.zeros(len(inputs), device=device)
    for k in range(K):
        # Rademacher vector matching fc parameter shapes
        v = {name: torch.randint(0, 2, p.shape, device=device).float() * 2 - 1
             for name, p in fc_params.items()}
        
        # Per-sample HVP: vmap over batch dimension
        def hvp_single(feat, target):
            # grad of (grad · v) = Hessian-vector product
            g = grad(fc_loss_single)(fc_params, feat, target)
            gv = sum((g[n] * v[n]).sum() for n in g)
            Hv = grad(lambda p: functional_call_loss(p, feat, target))(fc_params)
            return sum((Hv[n] * v[n]).sum() for n in Hv)
        
        vHv_batch = vmap(hvp_single)(features, targets)  # (N,)
        traces += vHv_batch / K
    
    return traces  # Unbiased estimate: E[v^T H v] = Tr(H)


def compute_trajectory_metrics(model_checkpoints, dataset, group_labels, K=50):
    """
    Compute AUROC, R(t), and Spearman ρ across checkpoints.
    
    Returns: dict with keys: auroc_per_t, R_per_t, t_star, spearman_rho
    """
    results = {}
    minority_mask = (group_labels == 1) | (group_labels == 3)  # minority groups
    
    for t, ckpt_path in model_checkpoints.items():
        model = load_checkpoint(ckpt_path)
        traces = compute_per_sample_fc_trace(model, dataset.inputs,
                                              dataset.targets, K=K)
        auroc = roc_auc_score(minority_mask.cpu(), traces.cpu())
        results[t] = {'auroc': auroc, 'mean_min': traces[minority_mask].mean(),
                      'mean_maj': traces[~minority_mask].mean()}
    
    t_star = max(results, key=lambda t: results[t]['mean_min']/results[t]['mean_maj'])
    R_values = [results[t]['mean_min']/results[t]['mean_maj'] for t in sorted(results)]
    rising_ts = [t for t in sorted(results) if t <= t_star]
    rho, _ = spearmanr(rising_ts, [results[t]['auroc'] for t in rising_ts])
    
    return {'auroc_per_t': {t: results[t]['auroc'] for t in results},
            'R_per_t': {t: results[t]['mean_min']/results[t]['mean_maj']
                        for t in results},
            't_star': t_star, 'spearman_rho': rho}
```

### Training Protocol

**Phase 1 — Pilot Run (MANDATORY FIRST STEP):**
```
1 seed, 5 epochs, save checkpoint at t=0 (before any training)
Compute AUROC(t=0) immediately
IF AUROC(t=0) ≥ 0.70: ABORT — pretrained artifact (repeat of h-e2 failure)
IF AUROC(t=0) < 0.70: CONTINUE to full training
```

**Phase 2 — Full Training (5 seeds, 50 epochs):**

| Hyperparameter | Value | Source |
|---------------|-------|--------|
| Optimizer | SGD | Phase 2A specification, h-e1/h-e2-k |
| Momentum | 0.9 | Standard for ResNet on Waterbirds |
| Weight decay | 1e-4 | izmailovpavel/spurious_feature_learning |
| Learning rate | 3e-3 (initial) | izmailovpavel/spurious_feature_learning |
| LR schedule | Cosine annealing | izmailovpavel/spurious_feature_learning |
| Batch size | 32 | Kirichenko 2022 / izmailovpavel |
| Epochs | 50 | Phase 2A specification (sufficient to observe Phase I/II transition) |
| Seeds | 1, 2, 3, 4, 5 | Phase 2B: ≥4/5 required |
| Loss | Cross-entropy | Standard ERM |
| Data augmentation | RandomResizedCrop(224) + HFlip (train) | izmailovpavel pipeline |

**Checkpoint schedule:** Save at epochs t∈{0, 1, 5, 10, 20, 50}
- t=0: Before ANY Waterbirds training (critical control — must be saved BEFORE first batch)
- t=1: Early ERM (Phase I begins)
- t=5, t=10, t=20: Phase I trajectory tracking
- t=50: Final (potential Phase II onset)

**Trace computation per checkpoint:**
- K=50 Rademacher probes (validated by h-e2-k)
- Last-fc layer only (2048×2 weight + 2 bias = 4098 parameters)
- Apply to FULL training set (4795 samples) for AUROC computation
- Estimated compute: ~4795 samples × 50 probes × 2 HVPs = ~480K HVP calls per checkpoint

**Seeds:** 5 fixed seeds (1, 2, 3, 4, 5)

> ⚠️ **EXISTENCE (PoC)**: No hyperparameter search. Fixed protocol above. Single training configuration.

### Evaluation

**Primary success criterion (MUST ALL HOLD in ≥4/5 seeds):**
1. `AUROC(t*) ≥ 0.85` — trace discriminates minority at optimal checkpoint
2. `AUROC(t=0) < 0.70` — signal is NOT a pretrained artifact
3. `Spearman ρ ≥ 0.8` over rising segment t=0 to t*

**Secondary criterion:**
- `Hutchinson CV ≤ 10%` at K=50 (stability gate — check across 5 probe resamplings at t*)

**Metrics per checkpoint t, per seed:**
- `AUROC(t)`: `sklearn.metrics.roc_auc_score(minority_mask, per_sample_traces_t)`
  - `minority_mask`: 1 if group∈{1,3} (landbird+water OR waterbird+land), 0 otherwise
- `R(t)`: `mean(traces[minority]) / mean(traces[majority])`
- `t*`: `argmax_t R(t)` — need NOT be same across seeds; report per-seed
- Spearman ρ: `scipy.stats.spearmanr(t_values_rising, auroc_values_rising)` over t∈[0, t*]
- Hutchinson CV: `std(trace_resamples) / mean(trace_resamples)` across 5 independent probe sets

**Expected baseline performance (from research):**
- Expected AUROC range at t*: 0.85-0.95 (BUILD_ON: h-e2-k confirmed AUROC=0.913 at single checkpoint)
- Expected epoch-0 AUROC: < 0.70 (hypothesis; if ≥0.70, experiment is aborted)
- Expected t*: t∈{1, 5, 10} based on h-e1 snapshot (t*=1 for 3/5 seeds, t*=4 for 2/5 seeds historically)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification + ranking (AUROC) + correlation (Spearman)
- Library: `sklearn.metrics` (AUROC), `scipy.stats` (Spearman ρ)
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  from scipy.stats import spearmanr
  
  # AUROC: minority membership prediction
  auroc = roc_auc_score(y_true=minority_mask.numpy(),  # 1=minority, 0=majority
                         y_score=traces.detach().cpu().numpy())
  
  # Spearman ρ over rising segment
  rising_t = [t for t in checkpoints if t <= t_star]
  rho, p_val = spearmanr(rising_t, [auroc_per_t[t] for t in rising_t])
  
  # Hutchinson CV
  trace_resamples = [compute_trace(model, K=50) for _ in range(5)]
  cv = np.std(trace_resamples) / np.mean(trace_resamples)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing AUROC(t=0) vs AUROC(t*) vs threshold (0.70 and 0.85 respectively), aggregated across 5 seeds with error bars (mean ± std)

#### Additional Figures (LLM Autonomous)
Based on the hypothesis type (trajectory measurement) and evaluation metrics, Phase 4 should autonomously generate:

1. **R(t) Trajectory Plot**: R(t) = mean_minority_trace(t) / mean_majority_trace(t) across t∈{0,1,5,10,20,50} — mean across 5 seeds with std band. Annotate t* with vertical dashed line.

2. **AUROC Trajectory Plot**: AUROC(t) vs checkpoint epoch, 5 seeds overlaid + mean. Horizontal dashed lines at 0.70 (pretrained artifact threshold) and 0.85 (gate threshold).

3. **Per-Sample Trace Distribution**: Box plot or violin plot at t* comparing trace distributions for minority (groups 1,3) vs majority (groups 0,2) samples. Split by class (landbird/waterbird) to show intra-class spectral imbalance.

4. **Spearman ρ Rising Segment**: Scatter plot of AUROC vs epoch over rising segment, with Spearman ρ annotation, for each of 5 seeds.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | vmap+vjp Hutchinson trace computable on ResNet-50 last-fc (2048→2) | TRUE — h-e2-k confirmed this works |
| Mechanism Isolatable | Trace can be computed independently at each checkpoint (no training entanglement) | TRUE — post-hoc measurement on frozen checkpoints |
| Baseline Measurable | t=0 checkpoint (before Waterbirds training) gives well-defined AUROC | TRUE — checkpoint must be saved BEFORE first batch |

### Architecture Compatibility Check

ResNet-50 last-fc is a standard `nn.Linear(2048, 2)` layer:
- Weight: (2, 2048) = 4096 parameters
- Bias: (2,) = 2 parameters
- Total last-fc parameters: 4098

**Required features for Hutchinson trace on last-fc:**
- `torch.func.vmap` support: ✅ (PyTorch ≥ 2.0)
- `torch.func.vjp` support: ✅ (PyTorch ≥ 2.0)
- `functional_call` for parameter substitution: ✅
- Gradient flow through last-fc: ✅ (model.eval(), no grad for backbone)

**Incompatible architectures (not applicable here):** SSM models without attention, architectures without a final linear classification head.

> ⚠️ Phase 4 MUST verify: `assert isinstance(model.fc, nn.Linear)` and `assert model.fc.out_features == 2` before computing traces.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"Trace computed for N={4795} samples at checkpoint t={epoch}, mean_min={X:.4f}, mean_maj={Y:.4f}"` | `compute_traces.py` after each checkpoint |
| Tensor Shape | `traces.shape == (N,)` where N = number of training samples | `compute_traces()` return value |
| Metric Delta | AUROC increases monotonically from t=0 to t* (at least 0.15 delta over first 5 checkpoints) | `evaluate_trajectory()` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(checkpoint_results, t_star):
    """Verify H-E3 mechanism is producing expected signals."""
    indicators = {
        # Core existence check
        "traces_computed": all(
            checkpoint_results[t]['traces'].shape[0] == 4795
            for t in checkpoint_results
        ),
        # Epoch-0 gate (pretrained artifact check)
        "epoch0_below_threshold": checkpoint_results[0]['auroc'] < 0.70,
        # Signal exists at t*
        "tstar_above_threshold": checkpoint_results[t_star]['auroc'] >= 0.80,
        # Ratio is elevated
        "ratio_elevated_at_tstar": (
            checkpoint_results[t_star]['mean_min'] / 
            checkpoint_results[t_star]['mean_maj']
        ) > 1.0,
        # Minority traces non-zero variance (not degenerate)
        "minority_traces_have_variance": (
            checkpoint_results[t_star]['traces_std_min'] > 1e-6
        ),
    }
    success = all(indicators.values())
    return success, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| AUROC(t=0) ≥ 0.70 | Check immediately after pilot run | ABORT — pretrained artifact (h-e2 pattern) |
| All traces ≈ constant (no variance) | Check `std(traces) < 1e-6` | FAIL — HVP computation may be broken; check vmap+vjp |
| Hutchinson CV > 10% at K=50 | Check `std(5 resamples)/mean > 0.10` | INVESTIGATE — increase K to 100 or switch to diagonal Fisher |
| R(t) never exceeds 1.05 | Check `max(R(t)) < 1.05` | FAIL — no trace ratio asymmetry; H0 supported |
| t* not found (R monotone) | R(t) still rising at t=50 | EXPLORE — Phase I→II transition beyond 50 epochs |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | `traces.shape == (N,)` AND `std > 1e-6` |
| Pretrained Artifact Rejected | AUROC(t=0) < 0.70 | Epoch-0 AUROC gate |
| Hypothesis Supported | AUROC(t*) ≥ 0.85 AND Spearman ρ ≥ 0.8 in ≥4/5 seeds | Full trajectory evaluation |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant Archon KB entries found. The Archon KB is indexed with HuggingFace Diffusers documentation and does not contain Hessian trace, spurious correlation, or Waterbirds content.

### B. GitHub Implementations (Exa)

**Repository 1**: izmailovpavel/spurious_feature_learning
- **URL**: https://github.com/izmailovpavel/spurious_feature_learning
- **Query used**: "Waterbirds ResNet-50 ERM training checkpoint save SGD spurious correlation DFR"
- **Relevance**: Official Kirichenko 2022 DFR pipeline for Waterbirds — training hyperparameters and dataset pipeline
- **Key Configuration Extracted**:
  - lr=3e-3, weight_decay=1e-4, batch_size=32, cosine_lr_scheduler, 100 epochs
  - `data_transform=AugWaterbirdsCelebATransform` for preprocessing
  - `model=imagenet_resnet50_pretrained` = `torchvision.models.resnet50(pretrained=True)`
- **Their Results**: WGA=92.0±0.9% (mean ± std, 5 runs) on Waterbirds
- **Used for**: Training protocol (our 50-epoch SGD reuses this hyperparameter regime)

**Repository 2**: PolinaKirichenko/deep_feature_reweighting
- **URL**: https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Query used**: "Waterbirds ResNet-50 ERM training checkpoint save SGD spurious correlation DFR"
- **Relevance**: Original DFR codebase; contains `wb_data.py` Waterbirds dataloader and `dfr_evaluate_spurious.py`
- **Key code pattern**:
  ```python
  # wb_data.py: Waterbirds dataloader uses metadata.csv
  # Columns: img_filename, y, split, place, group
  # group = 2*y + place
  ```
- **Used for**: Dataset loading code reference

**Repository 3**: VirtuosoResearch/NNHessian
- **URL**: https://github.com/VirtuosoResearch/NNHessian
- **Query used**: "Hutchinson trace estimator PyTorch vmap per-sample Hessian minority group spurious"
- **Relevance**: Full Hutchinson + Hutch++ implementation with clean interface
- **Used for**: Reference architecture validation; our implementation should match output of `hutchinson_trace(num_samples=50, distribution="rademacher")`

**Web Source 4**: PyTorch Official Tutorial — Jacobians, Hessians, hvp, vhp
- **URL**: http://docs.pytorch.org/tutorials/intermediate/jacobians_hessians.html
- **Query used**: "Hutchinson trace estimator per-sample Hessian PyTorch vmap vjp last layer"
- **Key code**:
  ```python
  # Batch Hessians via vmap (official pattern)
  compute_batch_hessian = vmap(hessian(predict, argnums=2), in_dims=(None, None, 0))
  # HVP via reverse-over-reverse:
  _, vjp_fn = vjp(grad(f), *primals)
  hvp = vjp_fn(*tangents)
  ```
- **Used for**: Core mechanism pseudo-code — per-sample HVP foundation

**Paper Source 5**: Arxiv 2605.25674 — Layer-wise Hessian Trace for Monitoring NN Training
- **URL**: https://arxiv.org/pdf/2605.25674
- **Query used**: "per-sample Hessian trace PyTorch vmap vjp implementation challenges"
- **Key insight**: K∈[5,10] probes sufficient for monitoring; correct bias from weight sharing requires assembling layer-wise Hessian before second differentiation
- **Used for**: K=50 justification (conservative but validated by h-e2-k)

**Paper Source 6**: LaBonte et al. 2024 — "The Group Robustness is in the Details" (NeurIPS 2024)
- **URL**: https://mlanthology.org/neurips/2024/labonte2024neurips-group/
- **Query used**: "LaBonte spectral imbalance ERM minority majority feature diversity Hessian curvature training dynamics"
- **Key finding**: Intra-class spectral norm ratio ρ(y) = λ1(gmin) / λ1(gmaj) > 1 for all seeds on Waterbirds. Minority groups have larger eigenvalues (larger feature covariance) which predicts larger Hessian trace via Tr(H_fc) ∝ ‖x_i‖² p_i(1-p_i).
- **Used for**: Mechanistic grounding of trace asymmetry prediction (H-E3 rationale)

**Paper Source 7**: NeurIPS 2022 — Escaping Saddle Points for Effective Generalization on Class-Imbalanced Data
- **URL**: https://proceedings.neurips.cc/paper_files/paper/2022/file/8f4d70db9ecec97b6723a86f1cd9cb4b-Paper-Conference.pdf
- **Query used**: "LaBonte spectral imbalance ERM minority majority feature diversity Hessian curvature"
- **Key finding**: Tail (minority) class shows higher |λmin| in Hessian eigenvalue density than head (majority) class. The loss surface is more curved for minority samples — directly supports trace asymmetry.
- **Used for**: Secondary mechanistic evidence for per-sample trace asymmetry

### C. Code Analysis (Serena MCP)

Serena analysis skipped — code from search results was sufficiently clear for pseudo-code generation. The vmap+vjp per-sample HVP pattern is unambiguously documented in PyTorch official tutorials, and the h-e2-k pipeline (already validated in this research) handles all implementation complexity.

### D. Previous Hypothesis Context

None — H-E3 is the first hypothesis in the verification chain.

**Infrastructure reuse (not a prerequisite):**
- h-e2-k Hutchinson pipeline: K=50, vmap+vjp, last-fc — directly reusable without modification
- h-e1 training loop: ERM ResNet-50 on Waterbirds — extend with `torch.save(model.state_dict(), f'ckpt_epoch{t}.pt')` at t∈{0,1,5,10,20,50}

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Waterbirds v1.0, path, statistics | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset preprocessing: AugWaterbirdsCelebATransform | GitHub | Repo B.1 (izmailovpavel) |
| Dataset loading: metadata.csv structure | GitHub | Repo B.2 (Kirichenko/DFR) |
| Model: ResNet-50 IMAGENET1K_V1 | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Model loading: torchvision.models.resnet50 | torchvision docs | Standard PyTorch API |
| Checkpoint epochs {0,1,5,10,20,50} | Phase 2B | 02b_verification_plan.md Section 2.2 (H-E3) |
| Optimizer: SGD, lr=3e-3, wd=1e-4, cosine | GitHub | Repo B.1 (izmailovpavel) |
| Batch size: 32 | GitHub | Repo B.1 + B.2 |
| Epochs: 50 | Phase 2B | H-E3 specification |
| Seeds: 5 | Phase 2B | H-E3 success criteria (≥4/5) |
| K=50 Hutchinson, Rademacher | Prior work | h-e2-k validated; arxiv 2605.25674 |
| vmap+vjp HVP pattern | Web | PyTorch tutorial B.4 |
| Hutchinson interface reference | GitHub | Repo B.3 (NNHessian) |
| AUROC computation: sklearn | Web | sklearn.metrics.roc_auc_score |
| Spearman ρ computation: scipy | Web | scipy.stats.spearmanr |
| Minority mask: groups {1,3} | Phase 2B | H-E3 specification (group definition) |
| Mechanistic basis (trace ∝ ‖x‖² p(1-p)) | Paper | LaBonte 2024 (spectral imbalance) |
| Trace asymmetry evidence | Paper | NeurIPS 2022 (Escaping Saddle Points) |
| Epoch-0 gate threshold (< 0.70) | Phase 2B | A2 assumption, h-e2 lesson |
| AUROC gate threshold (≥ 0.85) | Phase 2B | H-E3 success criteria |
| Spearman ρ gate (≥ 0.8) | Phase 2B | H-E3 success criteria |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed externally, restated in ```state block)
**Date:** 2026-08-04

### Workflow History for This Hypothesis
- 2026-08-04T03:36:09: H-E3 set to IN_PROGRESS, Phase 2C started (external loop)
- 2026-08-04: Phase 2C UNATTENDED execution initiated
- 2026-08-04: Steps 1-8 completed, experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + Web — 8 relevant sources found)*
*All specifications grounded in: prior pipeline (h-e2-k), izmailovpavel/spurious_feature_learning, PolinaKirichenko/DFR, PyTorch vmap+vjp tutorial, LaBonte 2024, Arxiv 2605.25674*
*Next Phase: Phase 3 - Implementation Planning*

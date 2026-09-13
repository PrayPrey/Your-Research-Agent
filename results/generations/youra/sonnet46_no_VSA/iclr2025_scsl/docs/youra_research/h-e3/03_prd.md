# Product Requirements Document: H-E3

**Hypothesis:** Under ERM training on Waterbirds (ResNet-50, SGD, 50 epochs, checkpoints t∈{0,1,5,10,20,50}), per-sample last-fc Hessian trace (K=50 Hutchinson via vmap+vjp) achieves AUROC≥0.85 at t* (argmax R(t)) for minority membership prediction, with epoch-0 AUROC<0.70 (ERM emergence, not pretrained artifact) and Spearman ρ≥0.8 across the rising segment from t=0 to t*.

**Hypothesis Type:** EXISTENCE (Proof-of-Concept)
**Gate:** MUST_WORK — all 3 criteria must hold in ≥4/5 seeds
**Phase 2C Source:** `02c_experiment_brief.md`
**Date:** 2026-08-04
**Author:** Anonymous

---

## 1. Executive Summary

H-E3 is a measurement experiment that tests whether per-sample Hessian trace of the last fully-connected layer (computed via K=50 Hutchinson estimator using torch.func.vmap+vjp) can discriminate minority-group samples from majority-group samples during standard ERM training on the Waterbirds dataset. The experiment tracks this signal across 6 training checkpoints (t∈{0,1,5,10,20,50}) over 5 random seeds, computing AUROC at each checkpoint and testing three gate conditions: (1) AUROC(t*)≥0.85, (2) AUROC(t=0)<0.70 (not a pretrained artifact), and (3) Spearman ρ≥0.8 over the rising segment. This is a PoC validation — no architectural novel contribution, no ablation variants beyond the pilot/full split.

---

## 2. Problem Statement

ERM training on spuriously correlated data (Waterbirds: bird type spuriously correlated with background) creates minority groups with distinct loss geometry. The hypothesis is that per-sample Hessian trace of the last-fc layer is elevated for minority samples during early-to-mid ERM training (Phase I), enabling minority membership identification without group labels. Validating this signal's existence and temporal trajectory is the prerequisite for all downstream mechanism hypotheses (H-M1 through H-M4).

**Failure mode to guard against:** The signal might be a pretrained ImageNet artifact rather than ERM-induced. The epoch-0 AUROC<0.70 gate directly tests this.

---

## 3. Scope

**In Scope:**
- ResNet-50 ERM training on Waterbirds (50 epochs, 5 seeds)
- Per-sample last-fc Hessian trace computation at 6 checkpoints
- AUROC, R(t), Spearman ρ, and Hutchinson CV metrics
- Pilot run (1 seed, 5 epochs) as mandatory first gate
- Result visualization (4 figure types)

**Out of Scope:**
- No architecture modification
- No group-labeled training (group labels used only for evaluation AUROC)
- No hyperparameter search
- No DFR retraining or robustness evaluation

---

## 4. Data Specification

### 4.1 Primary Dataset: Waterbirds v1.0

| Property | Value |
|----------|-------|
| Source | Sagawa et al. 2019 (arXiv:1911.08731) |
| Path | `/home/PrayPrey/data/waterbirds_v1.0/` |
| Download needed | NO — data already present |
| Metadata file | `metadata.csv` |
| Metadata columns | `img_id, img_filename, y, split, place, group` |

**Group definition:**
- `group = 2*y + place`
  - 0: Landbird + land background (majority, ~3498 samples, 73%)
  - 1: Landbird + water background (minority, ~184 samples, 4%)
  - 2: Waterbird + water background (majority, ~1057 samples, 22%)
  - 3: Waterbird + land background (minority, ~56 samples, 1%)
- `split`: 0=train, 1=val, 2=test

**Split sizes:**
- Train: 4795 samples total; 240 minority (groups 1+3)
- Val: 1199 samples (group-balanced)
- Test: 5794 samples

**Minority mask:** `minority_mask = (group == 1) | (group == 3)`

### 4.2 Preprocessing

| Stage | Operation |
|-------|-----------|
| Training | RandomResizedCrop(224), RandomHorizontalFlip |
| Val/Test | Resize(256), CenterCrop(224) |
| Normalization | mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] |

**Reference:** AugWaterbirdsCelebATransform from izmailovpavel/spurious_feature_learning

### 4.3 Dataset Loading Code

```python
import pandas as pd
from PIL import Image
import os

metadata = pd.read_csv('/home/PrayPrey/data/waterbirds_v1.0/metadata.csv')
# group = 2*y + place; split: 0=train, 1=val, 2=test
# minority_mask = (metadata['group'] == 1) | (metadata['group'] == 3)
```

---

## 5. Functional Requirements

### FR-1: Pilot Run Gate (MANDATORY FIRST)

The system MUST execute a pilot run before full training:
- 1 seed (seed=1), 5 epochs of ERM training
- Save checkpoint at t=0 (before ANY Waterbirds gradient update)
- Compute Hessian trace on training set at t=0
- Compute AUROC(t=0)
- **IF AUROC(t=0) ≥ 0.70: ABORT** — pretrained artifact detected (repeat of h-e2 failure mode)
- **IF AUROC(t=0) < 0.70: CONTINUE** to full 5-seed training

### FR-2: ERM Training with Checkpoint Saves

The system MUST train ResNet-50 on Waterbirds with:
- Optimizer: SGD, momentum=0.9, weight_decay=1e-4, lr=3e-3 (initial)
- LR schedule: Cosine annealing over 50 epochs
- Batch size: 32
- Epochs: 50
- Seeds: 5 (seeds 1, 2, 3, 4, 5)
- Loss: Cross-entropy (standard ERM, no group labels in training)

**Checkpoint schedule (per seed):** Save model state_dict at epochs t∈{0, 1, 5, 10, 20, 50}
- t=0 MUST be saved BEFORE the first gradient update of Waterbirds training

### FR-3: Per-Sample Last-FC Hessian Trace Computation

For each checkpoint (t, seed), compute per-sample Hessian trace:
- Layer: last-fc only (`model.fc` = `nn.Linear(2048, 2)`)
- Method: K=50 Hutchinson estimator via torch.func.vmap+vjp
- Probes: K=50 Rademacher vectors (±1 uniform)
- Input: Full training set (4795 samples)
- Output: `traces` tensor of shape (N,) = (4795,)

**Implementation pattern:**
```python
from torch.func import vmap, grad, functional_call
import torch.nn.functional as F

def compute_per_sample_fc_trace(model, dataloader, K=50, device='cuda'):
    """K=50 Hutchinson trace on last-fc. Returns (N,) trace tensor."""
    model.eval()
    fc_params = dict(model.fc.named_parameters())
    all_traces = []

    for batch_inputs, batch_targets in dataloader:
        batch_inputs, batch_targets = batch_inputs.to(device), batch_targets.to(device)
        with torch.no_grad():
            # Extract penultimate features (backbone only, no grad)
            features = model_backbone_forward(model, batch_inputs)  # (B, 2048)

        def fc_loss_single(params, feat, target):
            logit = functional_call(model.fc, params, feat.unsqueeze(0))
            return F.cross_entropy(logit, target.unsqueeze(0))

        batch_traces = torch.zeros(len(batch_inputs), device=device)
        for _ in range(K):
            v = {n: torch.randint(0, 2, p.shape, device=device).float() * 2 - 1
                 for n, p in fc_params.items()}

            def hvp_single(feat, target):
                g = grad(fc_loss_single)(fc_params, feat, target)
                Hv = grad(lambda p: sum((grad(fc_loss_single)(p, feat, target)[n] * v[n]).sum()
                                        for n in v))(fc_params)
                return sum((Hv[n] * v[n]).sum() for n in Hv)

            vHv = vmap(hvp_single)(features, batch_targets)  # (B,)
            batch_traces += vHv / K

        all_traces.append(batch_traces.detach())

    return torch.cat(all_traces)  # (N,)
```

**Architecture pre-check (MANDATORY):**
```python
assert isinstance(model.fc, torch.nn.Linear), "Last layer must be Linear"
assert model.fc.out_features == 2, "Must be binary classifier"
assert model.fc.in_features == 2048, "ResNet-50 feature dim"
```

### FR-4: Trajectory Metrics Computation

For each seed, compute across all 6 checkpoints:

| Metric | Formula | Library |
|--------|---------|---------|
| `AUROC(t)` | `roc_auc_score(minority_mask, traces_t)` | sklearn.metrics |
| `R(t)` | `mean(traces[minority]) / mean(traces[majority])` | numpy |
| `t*` | `argmax_t R(t)` | numpy |
| `Spearman ρ` | `spearmanr(t_values_rising, auroc_values_rising)` | scipy.stats |
| `Hutchinson CV` | `std(5_resamples) / mean(5_resamples)` at t* | numpy |

**Rising segment definition:** t∈[0, t*] (inclusive)

### FR-5: Mechanism Verification

After computing traces at each checkpoint, verify:
```python
def verify_mechanism_activated(checkpoint_results, t_star):
    indicators = {
        "traces_computed": all(r['traces'].shape[0] == 4795 for r in checkpoint_results.values()),
        "epoch0_below_threshold": checkpoint_results[0]['auroc'] < 0.70,
        "tstar_above_threshold": checkpoint_results[t_star]['auroc'] >= 0.80,
        "ratio_elevated_at_tstar": checkpoint_results[t_star]['mean_min'] / checkpoint_results[t_star]['mean_maj'] > 1.0,
        "minority_traces_have_variance": checkpoint_results[t_star]['traces_std_min'] > 1e-6,
    }
    return all(indicators.values()), indicators
```

### FR-6: Logging Requirements

At each checkpoint, log:
```
"Trace computed for N=4795 samples at checkpoint t={epoch}, 
 mean_min={X:.4f}, mean_maj={Y:.4f}, AUROC={Z:.4f}, R={W:.4f}"
```

### FR-7: Visualization (4 Required Figures)

All figures saved to `docs/youra_research/h-e3/figures/`:

| Figure | Type | Content |
|--------|------|---------|
| `fig1_gate_metrics.png` | Bar chart | AUROC(t=0) vs AUROC(t*) vs thresholds (0.70, 0.85); mean±std across 5 seeds |
| `fig2_R_trajectory.png` | Line plot | R(t) vs epoch t∈{0,1,5,10,20,50}; mean±std band; t* annotated with dashed line |
| `fig3_auroc_trajectory.png` | Line plot | AUROC(t) vs epoch; 5 seeds overlaid + mean; dashed lines at 0.70 and 0.85 |
| `fig4_trace_distribution.png` | Box/violin | Per-sample trace distributions at t*; minority (groups 1,3) vs majority (groups 0,2) |
| `fig5_spearman_rising.png` | Scatter | AUROC vs epoch over rising segment per seed; Spearman ρ annotated |

---

## 6. Non-Functional Requirements

### NFR-1: Compute Efficiency
- Trace computation restricted to last-fc layer only (4098 parameters), not full model
- Backbone forward pass done with `torch.no_grad()` for feature extraction
- Estimated compute: ~4795 × 50 × 2 HVPs = ~480K HVP calls per checkpoint
- 6 checkpoints × 5 seeds = 30 checkpoint evaluations total

### NFR-2: Reproducibility
- All seeds explicitly set: `torch.manual_seed(seed)`, `numpy.random.seed(seed)`
- Checkpoint files saved with epoch number in filename: `ckpt_seed{seed}_epoch{t}.pt`
- All results saved to `results/h_e3_results.json` (structured, per-seed, per-checkpoint)

### NFR-3: Failure Mode Detection
| Failure | Detection | Action |
|---------|-----------|--------|
| AUROC(t=0) ≥ 0.70 | After pilot run | ABORT with error message |
| All traces ≈ constant | `std(traces) < 1e-6` | FAIL — HVP broken |
| Hutchinson CV > 10% at K=50 | After CV check | INVESTIGATE (log warning) |
| R(t) never exceeds 1.05 | After all checkpoints | FAIL — no trace asymmetry |

### NFR-4: Memory Management
- Process training set in batches for trace computation (batch_size=32 or 64 for inference)
- Do not load all 6 checkpoints simultaneously — load one at a time

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | ≥2.0.0 | vmap, vjp, functional_call support |
| torchvision | ≥0.15 | ResNet-50 pretrained weights, transforms |
| numpy | ≥1.21 | Array ops, trace aggregation |
| scipy | ≥1.7 | spearmanr |
| sklearn (scikit-learn) | ≥1.0 | roc_auc_score |
| pandas | ≥1.3 | metadata.csv loading |
| Pillow | ≥8.0 | Image loading |
| matplotlib | ≥3.4 | Figure generation |
| tqdm | ≥4.60 | Progress bars |

### 7.2 External Repositories (Reference Only)

| Repository | URL | Usage |
|-----------|-----|-------|
| izmailovpavel/spurious_feature_learning | https://github.com/izmailovpavel/spurious_feature_learning | Training hyperparameters reference |
| PolinaKirichenko/deep_feature_reweighting | https://github.com/PolinaKirichenko/deep_feature_reweighting | wb_data.py dataset loading reference |
| VirtuosoResearch/NNHessian | https://github.com/VirtuosoResearch/NNHessian | Hutchinson estimator reference |

### 7.3 Hardware Requirements

| Resource | Minimum | Recommended |
|---------|---------|-------------|
| GPU VRAM | 8 GB | 16 GB |
| GPU | CUDA-capable | NVIDIA V100/A100 |
| Disk | 5 GB | 10 GB (checkpoints + results) |

---

## 8. Success Criteria

### Primary Gate (MUST ALL HOLD in ≥4/5 seeds):

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| AUROC(t*) | ≥ 0.85 | `roc_auc_score(minority_mask, traces_t_star)` |
| AUROC(t=0) | < 0.70 | `roc_auc_score(minority_mask, traces_t0)` |
| Spearman ρ | ≥ 0.80 | `spearmanr(rising_t_values, rising_auroc_values)` |

### Secondary Gate (informational, not blocking):

| Criterion | Threshold |
|-----------|-----------|
| Hutchinson CV at t* | ≤ 10% |

### Gate Outcome Logic:
- PASS (≥4/5 seeds all 3 primary criteria) → `gate.satisfied = True` → proceed to H-M1
- FAIL → `gate.satisfied = False` → STOP pipeline, route to Phase 0 for signal redesign

---

## 9. File Structure

```
docs/youra_research/h-e3/
├── 02c_experiment_brief.md       # Phase 2C input
├── 03_prd.md                     # This document
├── 03_architecture.md            # Phase 3 architecture
├── 03_logic.md                   # Phase 3 logic
├── 03_config.md                  # Phase 3 config
├── 03_tasks.yaml                 # Phase 3 task list
├── code/
│   ├── train_erm.py              # ERM training with checkpoint saves
│   ├── compute_traces.py         # Hutchinson trace computation
│   ├── evaluate_trajectory.py    # AUROC, R(t), Spearman ρ
│   └── run_experiment.py         # Main orchestration script
├── figures/
│   ├── fig1_gate_metrics.png
│   ├── fig2_R_trajectory.png
│   ├── fig3_auroc_trajectory.png
│   ├── fig4_trace_distribution.png
│   └── fig5_spearman_rising.png
└── results/
    └── h_e3_results.json         # Structured per-seed, per-checkpoint results
```

---

*stepsCompleted: PRD (Phase 3 Step 2)*
*Phase 2C completeness: Dataset ✓, Model ✓, Training protocol ✓, Trace mechanism ✓, Metrics ✓, Ablation (pilot run) ✓*

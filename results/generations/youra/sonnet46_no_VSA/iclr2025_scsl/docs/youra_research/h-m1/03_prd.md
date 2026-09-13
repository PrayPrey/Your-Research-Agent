# Product Requirements Document: H-M1

**Hypothesis:** Under ERM training on Waterbirds, ERM Phase I spurious feature exploitation creates differential confidence trajectories: p_minority(t*)∈[0.3,0.7] (boundary condition) and p_majority(t*)>0.80 (saturation) in ≥4/5 seeds, because SGD provably learns spurious features first (LaBonte & Muthukumar 2026), creating differential confidence trajectories.

**Hypothesis Type:** MECHANISM (PoC — Continuation Experiment)
**Gate:** MUST_WORK — p_minority(t*) ∈ [0.3,0.7] in ≥4/5 seeds; failure routes to Phase 0
**Prerequisites:** H-E3 (VALIDATED — PASS, 4/5 seeds)
**Phase 2C Source:** `02c_experiment_brief.md`
**Date:** 2026-08-04
**Author:** Anonymous

---

## 1. Executive Summary

H-M1 is a continuation experiment that verifies the causal mechanism behind H-E3's trace asymmetry. No new training is required: H-M1 reuses the 30 ResNet-50 checkpoints (6 epochs × 5 seeds) already produced in H-E3. The core operation is a forward pass through each checkpoint to extract per-sample softmax confidence in the true class, then computing mean group confidences p_minority(t) and p_majority(t) at each checkpoint. The experiment verifies that at the optimal checkpoint t* (from H-E3 results), minority samples remain near the decision boundary (confidence ∈ [0.3, 0.7]) while majority samples are already confident (>0.80), consistent with LaBonte & Muthukumar 2026 Phase I dynamics.

This is a MECHANISM-type PoC: if the gate fails, the trace asymmetry measured in H-E3 has no mechanistic basis, and the entire downstream hypothesis chain collapses.

---

## 2. Problem Statement

H-E3 demonstrated that per-sample Hessian trace of the last-fc layer achieves AUROC≥0.85 for minority membership prediction at training checkpoint t*. The mechanism hypothesis (H-M1) is that this trace asymmetry is caused by differential confidence trajectories: SGD (LaBonte & Muthukumar 2026 Theorem 3.2) learns spurious features first, driving majority samples to high-confidence predictions (Phase I saturation) while minority samples remain near the decision boundary. If this confidence differential exists at t*, it provides the mechanistic justification for the trace asymmetry.

**Failure mode to guard against:** If both minority and majority have similar confidence levels at t*, the trace asymmetry would not have the proposed mechanistic explanation.

---

## 3. Scope

**In Scope:**
- Reuse of H-E3 checkpoints at t∈{0,1,5,10,20,50}, seeds 1-5 (no new training)
- Per-sample softmax confidence extraction at each checkpoint via forward pass
- Group-wise mean confidence: p_minority(t), p_majority(t) per seed per checkpoint
- Gate verification at t* (from H-E3 04_validation.md)
- Trajectory visualization (4 figure types)
- Mechanism verification function `verify_mechanism_activated()`

**Out of Scope:**
- No new ERM training (checkpoints already exist from H-E3)
- No Hessian trace computation (H-E3 metric, not H-M1)
- No architecture modification
- No group-labeled training
- No hyperparameter search

---

## 4. Data Specification

### 4.1 Primary Dataset: Waterbirds v1.0

| Property | Value |
|----------|-------|
| Source | Sagawa et al. 2019 (arXiv:1911.08731); kohpangwei/group_DRO |
| Path | `/home/PrayPrey/data/waterbirds_v1.0/` |
| Download needed | NO — data already present (confirmed in H-E3) |
| Metadata file | `metadata.csv` |
| Metadata columns | `img_id, img_filename, y, split, place, group` |

**Group definition:**
- `group = 2*y + place`
  - G0: Landbird + land background (majority, ~3498 samples, 73%)
  - G1: Landbird + water background (minority, ~184 samples, 4%)
  - G2: Waterbird + land background (minority, ~56 samples, 1%)
  - G3: Waterbird + water background (majority, ~1057 samples, 22%)
- `split`: 0=train, 1=val, 2=test

**Split used for H-M1:** Training set only (4795 samples)
- Minority: G1+G2 = 240 samples (5%) → `minority_mask = (group == 1) | (group == 2)`
- Majority: G0+G3 = 4555 samples (95%) → `~minority_mask`

> **Note:** H-M1 uses `group ∈ {1,2}` (misaligned background as in 02c_experiment_brief.md), while H-E3 uses `group ∈ {1,3}`. Both are equivalent minority definitions for Waterbirds (misaligned samples). H-M1 follows 02c definition.

### 4.2 Preprocessing

Inherited from H-E3 (evaluation mode — no augmentation):

| Stage | Operation |
|-------|-----------|
| Resize | (256, 256) → CenterCrop(224) |
| Normalization | mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225] |
| Augmentation | None (evaluation only) |

### 4.3 Dataset Loading Code

```python
# Reuse from H-E3 code/data.py
from data import WaterbirdsDataset
dataset = WaterbirdsDataset(root='/home/PrayPrey/data/waterbirds_v1.0/', split='train')
# Dataset returns: (x, y, group) for each sample
minority_mask = (dataset.group_array == 1) | (dataset.group_array == 2)
```

---

## 5. Functional Requirements

### FR-1: Checkpoint Loading (No New Training)

The system MUST load H-E3 checkpoints (NOT train from scratch):

```python
# Checkpoint path pattern (from H-E3 04_validation.md)
ckpt_path = f"docs/youra_research/h-e3/code/outputs/checkpoints/checkpoint_seed{s}_epoch{t}.pt"
model.load_state_dict(torch.load(ckpt_path, map_location=device))
model.eval()
```

**Required checkpoints:** t∈{0,1,5,10,20,50} × seeds {1,2,3,4,5} = 30 checkpoints total.

**t* per seed (from H-E3 04_validation.md):**
- Seed 1: t* = 20
- Seed 2: t* = 50
- Seed 3: t* = 50
- Seed 4: t* = 20
- Seed 5: t* = 5

**Architecture (inherited):**
- Model: ResNet-50, `torchvision.models.resnet50(pretrained=True)` with final fc replaced
- Last-fc: `nn.Linear(2048, 2)` → outputs (B, 2) logits
- Input shape: (B, 3, 224, 224)

### FR-2: Per-Sample Confidence Extraction

For each (seed, checkpoint t), extract per-sample confidence in true class:

```python
def extract_confidence_by_group(model, loader, minority_mask, device):
    """
    Extract per-sample predicted confidence (softmax in true class).
    Args:
        model: ResNet-50 at checkpoint t (eval mode, no grad)
        loader: Waterbirds train DataLoader (shuffle=False, batch_size=256)
        minority_mask: bool tensor [N], True for G1∪G2 samples
        device: cuda
    Returns:
        p_per_sample: tensor [N], p_i = softmax(logits)[y_i]
        p_minority: scalar mean confidence for minority samples
        p_majority: scalar mean confidence for majority samples
    """
    model.eval()
    all_confs = []
    with torch.no_grad():
        for x, y, g in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)               # (B, 2)
            probs = F.softmax(logits, dim=1)  # (B, 2)
            conf = probs[torch.arange(len(y)), y]  # (B,) — confidence in true class
            all_confs.append(conf.cpu())
    p_per_sample = torch.cat(all_confs)   # (N,) = (4795,)
    p_minority = p_per_sample[minority_mask].mean().item()
    p_majority = p_per_sample[~minority_mask].mean().item()
    return p_per_sample, p_minority, p_majority
```

**Input shape validation:**
```python
assert p_per_sample.shape == (4795,), f"Expected (4795,), got {p_per_sample.shape}"
assert minority_mask.sum() == 240, f"Expected 240 minority, got {minority_mask.sum()}"
```

### FR-3: Trajectory Computation Across All Checkpoints

For each seed s ∈ {1,2,3,4,5}, compute confidence at ALL 6 checkpoints:

```python
results = {}  # {seed: {t: {'p_min': float, 'p_maj': float, 'p_per_sample': tensor}}}
for seed in [1, 2, 3, 4, 5]:
    results[seed] = {}
    for t in [0, 1, 5, 10, 20, 50]:
        ckpt = load_checkpoint(seed, t)
        _, p_min, p_maj = extract_confidence_by_group(ckpt, loader, minority_mask, device)
        results[seed][t] = {'p_min': p_min, 'p_maj': p_maj}
    results[seed]['tstar'] = TSTAR_PER_SEED[seed]  # from H-E3
```

### FR-4: Gate Verification at t*

For each seed, verify gate conditions at t*:

```python
def check_h_m1_gate(p_min_at_tstar, p_maj_at_tstar):
    """Returns (primary_pass, secondary_pass)"""
    primary = 0.3 <= p_min_at_tstar <= 0.7   # boundary condition (GATE)
    secondary = p_maj_at_tstar > 0.80          # saturation condition
    return primary, secondary
```

**Gate pass condition:** `primary == True` in ≥4/5 seeds.

### FR-5: Mechanism Verification

```python
def verify_mechanism_activated(results_per_seed):
    """
    Verify H-M1 mechanism: differential confidence trajectories exist.
    Returns (bool, dict): (mechanism_active, per-seed indicators)
    """
    indicators = {}
    for seed, traj in results_per_seed.items():
        tstar = traj['tstar']
        p_min = traj[tstar]['p_min']
        p_maj = traj[tstar]['p_maj']
        indicators[seed] = {
            'minority_boundary': 0.3 <= p_min <= 0.7,
            'majority_saturated': p_maj > 0.80,
            'gap': p_maj - p_min,
            'both_pass': (0.3 <= p_min <= 0.7) and (p_maj > 0.80)
        }
    n_pass = sum(v['both_pass'] for v in indicators.values())
    mechanism_active = n_pass >= 4  # ≥4/5 seeds
    return mechanism_active, indicators
```

### FR-6: Result Persistence

Save results to JSON for Phase 4.5 consumption:

```python
# Output: docs/youra_research/h-m1/results/confidence_results.json
{
    "hypothesis": "H-M1",
    "seed_results": {
        "1": {"tstar": 20, "0": {"p_min": ..., "p_maj": ...}, ...},
        ...
    },
    "gate_pass_count": int,
    "mechanism_active": bool,
    "summary": {
        "p_minority_at_tstar_per_seed": [...],
        "p_majority_at_tstar_per_seed": [...]
    }
}
```

### FR-7: Visualization (Mandatory Figures)

All figures saved to `docs/youra_research/h-m1/figures/`:

1. **Gate Metrics Comparison** (`fig_gate_metrics.png`): p_minority(t*) and p_majority(t*) per seed with gate thresholds [0.3, 0.7] and 0.80 overlaid (MANDATORY)
2. **Confidence Trajectory Plot** (`fig_confidence_trajectory.png`): p_minority(t) and p_majority(t) vs t for each seed (show divergence)
3. **Confidence Distribution** (`fig_conf_distribution.png`): Box plot of per-sample confidence at t* for minority vs majority
4. **Boundary Fraction Plot** (`fig_boundary_fraction.png`): Fraction of minority samples with p∈[0.3,0.7] at each t

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **Runtime** | ≤30 min total (30 checkpoints × forward pass on 4795 samples, no Hessian) |
| **Memory** | GPU RAM: ≤8GB (ResNet-50 + batch_size=256 confidently fits) |
| **Reproducibility** | torch.manual_seed(seed) before each checkpoint evaluation |
| **Numerical precision** | float32 softmax; no mixed precision needed for confidence |
| **Hardware** | CUDA GPU required (same environment as H-E3) |

---

## 7. Dependencies

### 7.1 Python Packages

All packages already installed in H-E3 environment:

| Package | Version | Purpose |
|---------|---------|---------|
| torch | ≥2.0 | Model loading, forward pass, softmax |
| torchvision | ≥0.15 | ResNet-50 architecture |
| numpy | ≥1.24 | Array operations |
| scipy | ≥1.10 | `spearmanr` (optional, for trajectory analysis) |
| matplotlib | ≥3.7 | Visualization |
| pandas | ≥2.0 | Metadata CSV loading |
| Pillow | ≥9.0 | Image loading |
| tqdm | ≥4.65 | Progress bars |

No new package installations required.

### 7.2 H-E3 Code Dependencies

| File | Path | Reuse Mode |
|------|------|-----------|
| `data.py` | `docs/youra_research/h-e3/code/data.py` | Direct import |
| `evaluate_trajectory.py` | `docs/youra_research/h-e3/code/evaluate_trajectory.py` | Extend with confidence extraction |
| Checkpoints | `docs/youra_research/h-e3/code/outputs/checkpoints/` | Read-only |
| `04_validation.md` | `docs/youra_research/h-e3/04_validation.md` | t* per seed reference |

### 7.3 External Repositories (Reference Only)

| Repository | URL | Use |
|------------|-----|-----|
| PolinaKirichenko/deep_feature_reweighting | GitHub | Checkpoint eval loop pattern (reference) |
| kohpangwei/group_DRO | GitHub | Group definition reference |

---

## 8. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Primary Gate (MUST_WORK)** | p_minority(t*) ∈ [0.3,0.7] in ≥4/5 seeds | `verify_mechanism_activated()` returns True |
| Secondary | p_majority(t*) > 0.80 in ≥4/5 seeds | `check_h_m1_gate()` secondary |
| Code runs | No error on 4795-sample forward pass | Exception-free execution |
| Trajectory divergence | p_majority(t*) - p_minority(t*) ≥ 0.10 | Per-seed gap measurement |

**Failure Response:**
- IF p_minority(t*) < 0.3 in ≥2/5 seeds → FAIL: ABANDON, route to Phase 0
- IF p_majority(t*) < 0.80 in ≥2/5 seeds → EXPLORE: extend training window to epoch 100 (requires rerunning H-E3 with 100 epochs)

---

## 9. Implementation Notes

**Critical Path:** All confidence extraction is forward-pass only (no gradient computation needed). This is the key difference from H-E3 (which required Hutchinson Hessian trace). Expected runtime is ~1-2 minutes per seed (30 checkpoints × ~4 seconds each).

**Inheritance Strategy:** Extend `evaluate_trajectory.py` from H-E3 to also compute confidence metrics alongside existing trace metrics. Saves redundant checkpoint loading.

**Expected Values (theory-backed):**
- p_minority(t*) ≈ 0.40-0.65 (near decision boundary; Phase I not complete for minority at finite t*)
- p_majority(t*) ≈ 0.85-0.99 (spurious feature saturation; LaBonte & Muthukumar 2026 Theorem 3.2)
- Gap ≥ 0.15 expected; "Silent Majority" (arXiv:2501.00961) Fig 1 empirically supports

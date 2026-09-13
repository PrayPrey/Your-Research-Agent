# Product Requirements Document: H-M3
## Reduced Spurious Gradient in Layer4 → Lower Background Linear Decodability (Primary H-P1 Test)

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**hypothesis_id:** h-m3
**hypothesis_type:** MECHANISM
**tier:** FULL
**generated_at:** 2026-08-05T18:35:00Z
**source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Implement the **pre-registered formal test** of H-P1: measure whether GroupDRO-trained ResNet-50 backbones encode less background (spurious) information in layer4 features than ERM-trained backbones, using a maximum-capacity L-BFGS linear probe on the full Waterbirds WILDS test set.

This is a **continuation experiment** reusing all validated infrastructure from H-P0, H-M1, and H-M2:
- Dataset: Waterbirds WILDS v1.0 (verified cache)
- Checkpoints: 6 paired (ERM×3 + GroupDRO×3), all cached
- Feature extraction: `layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048` (verified H-P0 cosine_sim=1.000000)
- Probe: `sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)`

**Gate:** MUST_WORK — core empirical test of main hypothesis H-BSER-v1. Tiered outcomes:
- **CONFIRMED** (p<0.05, d>0): Backbone-level spurious encoding reduction validated
- **SUGGESTIVE** (p<0.10, d>0.5): Consistent with mechanism; underpowered (n=3)
- **REJECTED** (wrong direction or p≥0.10 + d<0.2): WGA improvement is head-only

Preliminary expectation: SUGGESTIVE or CONFIRMED (H-M2 FR-3: p=0.0526, d=1.64).

---

## 2. Problem Statement

H-M2 provided a suggestive preliminary result (p=0.0526, d=1.64) that GroupDRO-trained layer4 features are less decodable for background. H-M3 is the **pre-registered formal test** — a controlled comparison of background (spurious attribute) linear decodability between ERM and GroupDRO backbones.

The hypothesis addresses a contested landscape: Izmailov 2022 (NeurIPS) claims GroupDRO's improvement is "largely attributed to learning a better weighting in the last linear layer" (head-only). If H-M3 is CONFIRMED or SUGGESTIVE, it demonstrates backbone-level spurious representation reduction — a direct counter-evidence to the head-only hypothesis.

---

## 3. Objectives and Success Criteria

### Primary Objective
Measure background (spurious attribute) linear decodability from frozen ResNet-50 layer4 features for 3 matched ERM/GroupDRO seed pairs, and test whether GroupDRO reduces background decodability relative to ERM.

### Success Criteria (GATE: MUST_WORK — Tiered)

| Verdict | Condition | Gate Result |
|---------|-----------|-------------|
| CONFIRMED | p < 0.05 AND d > 0 AND GroupDRO mean < ERM mean | PASS |
| SUGGESTIVE | p < 0.10 AND d > 0.5 AND GroupDRO mean < ERM mean | PASS |
| REJECTED | GroupDRO mean ≥ ERM mean OR (p ≥ 0.10 AND d < 0.2) | FAIL → route Phase 5 as definitive negative |

**Mandatory Sanity Checks:**
- ERM mean probe acc > 0.6 (A2 validation — metric discriminability)
- All probe accs in [0.5, 1.0] (binary task, above-chance)

### Secondary Criteria (Non-blocking)
- SAM vs ERM exploratory comparison (no pre-registered threshold)
- All 9 backbone checkpoints probe acc computed (for H-P2 correlation)
- Figures saved to `h-m3/figures/`
- Runtime: < 15 minutes (inference only, no training, GPU optional)

---

## 4. Data Specification

### Primary Dataset

**Dataset:** Waterbirds WILDS v1.0
**Source:** WILDS benchmark (Koh et al. 2021); pre-cached from H-P0
**Download:** Pre-cached at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (do NOT re-download)
**Manual download required:** NO — cache already present
**Loading library:** `wilds` package

```python
from wilds import get_dataset

dataset = get_dataset(dataset='waterbirds', download=False,
                      root_dir='/home/PrayPrey/.wilds_cache')

# Full test set for probe evaluation
test_data = dataset.get_subset('test')
# N = 5,794 samples — use ALL, no subsampling

# Background label extraction:
# metadata[:, 0] = group_array (0-3)
# background_label = group_array % 2 (0=land, 1=water)
```

### Dataset Splits Used

| Split | Size | Purpose |
|-------|------|---------|
| Test | 5,794 | Feature extraction + probe fit + probe evaluation (full set — NO subsampling) |

**Critical:** H-M3 uses full test set for both fitting and scoring the background probe (measuring raw decodability, not generalization). Minimum acceptable: 500 samples (but full set is required for pre-registered protocol).

### Group Structure (Background Label)

| group_array | Bird | Background | background_label |
|-------------|------|------------|-----------------|
| 0 | Landbird | Land | 0 (land) |
| 1 | Landbird | Water | 1 (water) |
| 2 | Waterbird | Land | 0 (land) |
| 3 | Waterbird | Water | 1 (water) |

**Probe target:** `background_label = group_array % 2` — binary (land=0, water=1)

### Standard Preprocessing

```python
from torchvision import transforms

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
```

---

## 5. Model Specification

### Checkpoints (Primary — H-M3 Pre-registered)

**Architecture:** ResNet-50 (standard torchvision)
**Source:** izmailovpavel/spurious_feature_learning (NeurIPS 2022)
**Location:** `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/`

| Pair | ERM Checkpoint | GroupDRO Checkpoint |
|------|----------------|---------------------|
| Seed 1 | `erm_seed1.pt` | `groupdro_seed1.pt` |
| Seed 2 | `erm_seed2.pt` | `groupdro_seed2.pt` |
| Seed 3 | `erm_seed3.pt` | `groupdro_seed3.pt` |

### Exploratory Checkpoints (H-P1b — SAM)

| Pair | ERM Checkpoint | SAM Checkpoint |
|------|----------------|----------------|
| Seed 1 | `erm_seed1.pt` | `sam_seed1.pt` |
| Seed 2 | `erm_seed2.pt` | `sam_seed2.pt` |
| Seed 3 | `erm_seed3.pt` | `sam_seed3.pt` |

**No new training.** All checkpoints pre-trained and locally cached (verified H-P0 cosine_sim=1.000000).

### Checkpoint Loading

```python
import torchvision.models as models
import torch

def load_resnet50(ckpt_path, device='cpu'):
    model = models.resnet50(pretrained=False)
    state = torch.load(ckpt_path, map_location=device)
    if 'model' in state:
        state = state['model']
    if 'state_dict' in state:
        state = state['state_dict']
    model.load_state_dict(state, strict=False)
    model.eval()
    return model
```

### Feature Extraction Protocol (IDENTICAL to H-P0 — proven working)

```python
import torch
import torch.nn as nn

class SpuriousProbeExtractor(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.stem = nn.Sequential(
            model.conv1, model.bn1, model.relu, model.maxpool
        )
        self.features = nn.Sequential(
            model.layer1, model.layer2, model.layer3, model.layer4,
            nn.AdaptiveAvgPool2d(output_size=(1, 1))
        )

    def forward(self, x):
        x = self.stem(x)       # (B, 64, 56, 56)
        x = self.features(x)   # (B, 2048, 1, 1)
        return torch.flatten(x, 1)  # (B, 2048)
```

---

## 6. Functional Requirements

### FR-1: Feature Extraction (Primary)

For each of 9 checkpoints (ERM×3, GroupDRO×3, SAM×3):
- Load checkpoint with `load_resnet50()`
- Set `model.eval()` + `torch.no_grad()` (frozen backbone — mandatory)
- Extract layer4 features for ALL 5,794 test samples
- Batch size: 100 (memory-efficient)
- Output: `features_np` shape `(5794, 2048)`, dtype float32
- Log: `print(f"[H-M3] Features extracted: {features.shape}")`

### FR-2: Background Probe (Primary Gate)

For each checkpoint's `features_np`:
- Extract background labels: `background_labels = metadata[:, 0].numpy() % 2`
- Fit probe on extracted features (full test set — measuring decodability, not generalization):

```python
from sklearn.linear_model import LogisticRegression

def run_background_probe(features_np, background_labels_np):
    probe = LogisticRegression(
        solver='lbfgs', C=1e9,
        max_iter=1000, random_state=42
    )
    probe.fit(features_np, background_labels_np)
    acc = probe.score(features_np, background_labels_np)
    print(f"[H-M3] Probe acc {method}_seed{seed}: {acc:.4f}")
    return acc
```

- Log background label distribution: `print(f"[H-M3] Background label distribution: {np.bincount(background_labels)}")`

### FR-3: Statistical Test (Pre-registered Primary)

One-sided paired t-test: H1: ERM_acc > GroupDRO_acc

```python
from scipy import stats
import numpy as np

erm_accs = [probe_acc_erm_s1, probe_acc_erm_s2, probe_acc_erm_s3]
gdro_accs = [probe_acc_gdro_s1, probe_acc_gdro_s2, probe_acc_gdro_s3]

t_stat, p_value = stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')

diff = np.array(erm_accs) - np.array(gdro_accs)
cohens_d = diff.mean() / diff.std(ddof=1)

print(f"[H-M3] Paired t-test: t={t_stat:.4f}, p={p_value:.4f} (one-sided)")
print(f"[H-M3] Cohen's d: {cohens_d:.4f}")
```

### FR-4: Verdict Determination

```python
if gdro_mean >= erm_mean:
    verdict = "REJECTED"
elif p_value < 0.05 and cohens_d > 0:
    verdict = "CONFIRMED"
elif p_value < 0.10 and cohens_d > 0.5:
    verdict = "SUGGESTIVE"
else:
    verdict = "REJECTED"

print(f"[H-M3] Verdict: {verdict}")
```

### FR-5: Sanity Checks

```python
assert erm_mean > 0.6, f"ERM probe acc {erm_mean:.4f} < 0.6 — metric non-discriminative (A2 violated)"
assert all(0.5 <= acc <= 1.0 for acc in erm_accs + gdro_accs), "Probe acc outside [0.5, 1.0]"
```

### FR-6: SAM Exploratory Analysis (H-P1b)

For SAM×3 checkpoints:
- Run same feature extraction + probe pipeline
- Report: SAM mean probe acc vs ERM mean probe acc
- Compute Cohen's d for SAM-ERM (no pre-registered threshold)
- Include in results.json under `exploratory_sam`

### FR-7: Visualization (Required)

1. **Grouped Bar Chart — Gate Metric** (REQUIRED):
   - X-axis: Seeds {1, 2, 3}; grouped bars for ERM vs GroupDRO probe accuracy
   - Y-axis: Background probe accuracy
   - Inset: paired differences (ERM_i - GroupDRO_i) with mean ± std bar
   - Annotation: p-value from paired t-test
   - Save: `h-m3/figures/background_probe_accuracy.png`

2. **All 9 Backbones Comparison** (Required):
   - Bar chart: ERM×3, GroupDRO×3, SAM×3 probe accuracy, grouped by method
   - Save: `h-m3/figures/all_backbones_probe_accuracy.png`

3. **Paired Differences Scatter** (Required):
   - Scatter: (ERM_seed_i − GroupDRO_seed_i) for i=1,2,3 with mean ± std bar
   - Save: `h-m3/figures/paired_differences.png`

4. **Probe Accuracy vs WGA Scatter** (Additional):
   - All 9 backbone checkpoints: probe_acc vs WGA
   - Pearson r annotation
   - Save: `h-m3/figures/probe_vs_wga.png`

### FR-8: Results Logging

Save structured results to `h-m3/results.json`:
```json
{
  "hypothesis_id": "h-m3",
  "gate": "MUST_WORK",
  "verdict": "CONFIRMED|SUGGESTIVE|REJECTED",
  "erm_probe_accs": [0.0, 0.0, 0.0],
  "gdro_probe_accs": [0.0, 0.0, 0.0],
  "sam_probe_accs": [0.0, 0.0, 0.0],
  "erm_mean": 0.0,
  "gdro_mean": 0.0,
  "t_stat": 0.0,
  "p_value": 0.0,
  "cohens_d": 0.0,
  "n_test_samples": 5794,
  "gate_result": "PASS|FAIL",
  "sanity_checks": {
    "erm_mean_above_0.6": true,
    "all_accs_in_range": true
  },
  "exploratory_sam": {
    "sam_mean": 0.0,
    "sam_vs_erm_cohens_d": 0.0
  }
}
```

### FR-9: Validation Report

Generate `h-m3/04_validation.md` with:
- Probe accuracy table (all 9 checkpoints)
- Statistical test results (t, p, Cohen's d)
- Verdict with tiered criteria
- Sanity check confirmation
- Gate result (PASS/FAIL)

---

## 7. Non-Functional Requirements

### NFR-1: No New Training
- All checkpoints pre-trained and locally cached
- `model.eval()` + `torch.no_grad()` mandatory during feature extraction
- No optimizer, no weight updates, no new checkpoints saved

### NFR-2: Full Test Set Required (Pre-registered)
- Probe MUST use full test set (5,794 samples)
- Minimum acceptable: 500 samples if full set fails
- Do NOT use small subsets < 500 samples

### NFR-3: Reproducibility
- Fixed random_state=42 in LogisticRegression
- DataLoader shuffle=False
- All results deterministic given fixed checkpoints

### NFR-4: Resource Constraints
- GPU: Optional (inference only; CPU sufficient)
- Memory: < 4 GB (load one checkpoint at a time, extract features, unload)
- Storage: < 30 MB (results.json + figures + 04_validation.md)
- Runtime: < 15 minutes (6 checkpoints × inference + sklearn probe)

### NFR-5: Infrastructure Reuse from H-M2
- Checkpoint path identical to H-M2 (verified working)
- Feature extraction pipeline identical to H-P0 + H-M2 (cosine_sim=1.000000 verified)
- sklearn probe protocol identical (C=1e9, solver='lbfgs', max_iter=1000)
- Dataset loading identical to H-M2

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=1.9.0       # Model loading, feature extraction
torchvision        # ResNet-50 architecture
wilds              # Waterbirds dataset loading
sklearn            # LogisticRegression for background probe
scipy              # scipy.stats.ttest_rel for statistical test
numpy              # Numerical computation
matplotlib         # Visualization
```

### 8.2 External Repositories (Reference — Already Available)

| Repository | Purpose |
|------------|---------|
| izmailovpavel/spurious_feature_learning | Source of 12 pre-trained checkpoints (cached) |
| PolinaKirichenko/deep_feature_reweighting | DFR protocol reference (background label extraction) |

### 8.3 Pre-conditions

- H-P0 COMPLETED and PASS ✓ (cosine_sim=1.000000 — feature extraction verified)
- H-M1 COMPLETED and PASS ✓ (GroupDRO mechanism verified)
- H-M2 COMPLETED and PASS ✓ (SHOULD_WORK — layer4 weight diff confirmed)
- 6 primary checkpoints (ERM×3, GroupDRO×3) at checkpoint cache path ✓
- Waterbirds WILDS cache at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` ✓
- Python packages: torch, torchvision, wilds, sklearn, scipy, numpy, matplotlib

---

## 9. Evaluation Criteria

### Primary Metrics (Gate: MUST_WORK — Tiered)

| Metric | Definition | Target (SUGGESTIVE) | Target (CONFIRMED) |
|--------|-----------|--------------------|--------------------|
| `probe_acc_groupdro_mean` | Mean L-BFGS probe acc (GroupDRO×3) | < ERM mean | < ERM mean |
| `p_value` | One-sided paired t-test | < 0.10 | < 0.05 |
| `cohens_d` | Effect size (ERM - GroupDRO) / std | > 0.5 | > 0 |
| `ERM_mean_probe_acc` | Sanity check | > 0.6 | > 0.6 |

### Secondary Metrics

| Metric | Expected |
|--------|---------|
| SAM mean probe acc | < ERM mean (exploratory, no threshold) |
| Background label balance | ~50/50 (N_land ≈ N_water in test set) |
| H-M2 FR-3 reproduced | Probe accs match H-M2 values within 0.005 |

---

## 10. Out of Scope

- Layer4 weight difference analysis (completed in H-M2)
- Gradient norm analysis (completed in H-M2)
- New model training or fine-tuning
- Architecture modifications to ResNet-50
- Downloading new checkpoints (reuse H-M2 verified cache)
- WGA measurement (not part of H-M3 probe — use from paper/H-M1)
- Full ablation over regularization parameters (C=1e9 is fixed, pre-registered)

---

## 11. Implementation Notes

- **H-M2 FR-3 is preliminary context only:** H-M3 is the pre-registered formal test. The H-M2 result (p=0.0526, d=1.64) is informative but not the official test.
- **Probe fits on test set:** We measure decodability (raw information content), not classification generalization. Fitting and evaluating on same set is intentional per pre-registered protocol.
- **Load sequentially:** 9 models × ~100 MB → load one at a time to avoid OOM.
- **L-BFGS vs liblinear:** Official dfr_evaluate_spurious.py uses liblinear with C search. H-M3 uses L-BFGS + C=1e9 (no regularization) per pre-registered protocol — testing maximum decodability.
- **REJECTED is also field-relevant:** If GroupDRO does NOT reduce background decodability, it contributes to the Izmailov 2022 head-only interpretation. Both outcomes advance the field.

---

*Generated from: h-m3/02c_experiment_brief.md*
*Pipeline position: Phase 3 (Implementation Planning)*
*Gate: MUST_WORK — tiered: CONFIRMED (p<0.05, d>0), SUGGESTIVE (p<0.10, d>0.5), REJECTED*
*Base hypothesis: H-M2 (COMPLETED, PASS/SUGGESTIVE)*

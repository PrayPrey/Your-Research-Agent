# Product Requirements Document: H-P2
## Spurious Probe Accuracy Correlates Negatively with WGA (Exploratory)

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**hypothesis_id:** h-p2
**hypothesis_type:** MECHANISM (Exploratory Correlation)
**tier:** FULL
**generated_at:** 2026-08-05T19:00:00Z
**source:** 02c_experiment_brief.md
**base_hypothesis:** h-m3

---

## 1. Executive Summary

Implement the **pre-registered exploratory correlation test** of H-P2: measure whether spurious attribute probe accuracy (background decodability from frozen layer4 features) correlates negatively with Worst-Group Accuracy (WGA) across 9 distinct-backbone ResNet-50 checkpoints (ERM×3 + SAM×3 + GroupDRO×3).

This is a **continuation/extension experiment** reusing all validated infrastructure from H-M3:
- Dataset: Waterbirds WILDS v1.0 (verified local cache: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`)
- Checkpoints: 9 distinct-backbone checkpoints (6 from H-M3 + SAM×3 new), all cached
- Feature extraction: `layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048` (H-M3 protocol)
- Probe: `sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)`
- WGA ground truth: Izmailov 2022 Table 1 (ERM=0.72, SAM=0.74, GroupDRO=0.88 per method)

**Gate:** SHOULD_WORK (exploratory) — Pearson r < -0.5 AND bootstrapped 95% CI upper bound < 0.
- **CONFIRMED** (r < -0.5 AND ci_high < 0): Strong negative correlation; supports backbone spurious encoding reduction predicting WGA
- **SUGGESTIVE** (r < -0.3 AND ci_low < 0): Partial evidence; exploratory negative acceptable
- **REJECTED** (r ≥ -0.3 OR ci_high ≥ 0): No negative correlation detected

Preliminary expectation: CONFIRMED (H-M3 key_findings: r ≈ -0.626 from 9 checkpoints).

---

## 2. Problem Statement

H-M3 (CONFIRMED, p=0.0039, Cohen's d=6.4759) demonstrated that GroupDRO-trained backbones encode significantly less background information in layer4 features than ERM-trained backbones. H-P2 asks: **does this spurious probe accuracy generalize as a predictor of WGA across methods?**

Specifically: if a training method reduces background decodability in layer4, does it also achieve higher WGA? This tests whether spurious feature encoding reduction is mechanistically linked to WGA improvement — not just a coincidence of GroupDRO's specific training signal.

Including SAM (a sharpness-aware optimizer, not designed for group fairness) enables cross-method validation: SAM lies between ERM and GroupDRO in both probe accuracy and WGA, providing 3 distinct operating points.

---

## 3. Objectives and Success Criteria

### Primary Objective
Compute Pearson r between spurious probe accuracy (9 checkpoints) and WGA, with bootstrapped 95% CI and one-sided p-value, to test whether probe accuracy negatively predicts WGA across methods.

### Success Criteria (GATE: SHOULD_WORK — Exploratory)

| Verdict | Condition | Gate Result |
|---------|-----------|-------------|
| CONFIRMED | Pearson r < -0.5 AND bootstrapped 95% CI upper bound (ci_high) < 0 | PASS |
| SUGGESTIVE | r < -0.3 AND CI includes r < 0 (ci_low < 0) | PASS (weak) |
| REJECTED | r ≥ -0.3 OR ci_high ≥ 0 | FAIL (exploratory negative — does not block pipeline) |

**Note:** SHOULD_WORK gate — even REJECTED does not block Phase 5 pipeline continuation.

### Secondary Objectives
- Ablation sensitivity: DFR-excluded (default), ERM+GroupDRO only (n=6), per-method mean (n=3)
- Visualization: scatter plot with regression line, bootstrap distribution, method comparison

---

## 4. Data Specification

### Primary Dataset: Waterbirds WILDS v1.0

| Property | Value |
|----------|-------|
| Name | Waterbirds WILDS |
| Version | v1.0 |
| Source | WILDS benchmark (Koh et al. 2021) |
| Local Cache | `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` |
| Download Required | NO — already cached (verified in H-P0, H-M3) |
| API | `wilds.get_dataset('waterbirds', download=False, root_dir='/home/PrayPrey/.wilds_cache')` |

**Splits Used:**
- Train: ~4795 samples (probe training only — fit sklearn probe)
- Test: 5794 samples (probe accuracy measurement)

**Labels:**
- Spurious target: `background_label = group_array % 2` (0=land, 1=water background)
- WGA ground truth: per-checkpoint from Izmailov 2022 Table 1 (hardcoded)

**Loading Code:**
```python
from wilds import get_dataset
import torchvision.transforms as T

transform = T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor(),
                       T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
dataset = get_dataset('waterbirds', download=False, root_dir='/home/PrayPrey/.wilds_cache')
train_data = dataset.get_subset('train', transform=transform)
test_data = dataset.get_subset('test', transform=transform)
```

### WGA Ground Truth (Hardcoded from Izmailov 2022 Table 1)

| Method | Seeds | WGA per seed |
|--------|-------|-------------|
| ERM | 1, 2, 3 | 0.72, 0.72, 0.72 |
| SAM | 1, 2, 3 | 0.74, 0.74, 0.74 |
| GroupDRO | 1, 2, 3 | 0.88, 0.88, 0.88 |

Note: Izmailov 2022 reports method-level averages; per-seed WGA assumed uniform. If per-seed data available from checkpoint evaluation, use those instead.

---

## 5. Functional Requirements

### FR-1: Checkpoint Loading and Feature Extraction (9 Checkpoints)

Load 9 distinct-backbone checkpoints from local cache and extract layer4 features for all train/test samples:

**Checkpoint paths:**
```
_archive/20260805T130336_routing_recovery/h-e1/checkpoints/
  erm_seed{1,2,3}/final_checkpoint.pt
  sam_seed{1,2,3}/final_checkpoint.pt
  groupdro_seed{1,2,3}/final_checkpoint.pt
```
(full base path: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/`)

**DFR excluded:** backbone ≡ ERM per H-P0 (cosine similarity ≥ 0.9999).

**Feature extraction:** `model.layer4 → AdaptiveAvgPool2d(output_size=(1,1)) → flatten → D=2048`

**Reuse priority:** Load existing features from `h-m3/results.json` for ERM×3 + GroupDRO×3. Compute SAM×3 features fresh if not present.

### FR-2: Linear Probe per Checkpoint

For each of 9 checkpoints, fit and evaluate background linear probe:

```python
probe = LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
probe.fit(train_features, train_background_labels)
probe_acc = probe.score(test_features, test_background_labels)
```

Test set: full Waterbirds WILDS test set (N=5794).

### FR-3: Pearson r + One-Sided p-value

```python
from scipy.stats import pearsonr
res = pearsonr(probe_accs, wga_values, alternative='less')  # H1: r < 0
r, p_value = res.statistic, res.pvalue
```

### FR-4: Bootstrapped 95% CI (BCa with percentile fallback)

```python
from scipy.stats import bootstrap

def pearsonr_stat(x, y, axis=-1):
    return pearsonr(x, y, axis=axis)[0]

try:
    boot = bootstrap((probe_accs, wga_values), pearsonr_stat,
                     paired=True, n_resamples=1000,
                     confidence_level=0.95, method='BCa', rng=42)
except Exception:
    boot = bootstrap((probe_accs, wga_values), pearsonr_stat,
                     paired=True, n_resamples=1000,
                     confidence_level=0.95, method='percentile', rng=42)
ci_low, ci_high = boot.confidence_interval.low, boot.confidence_interval.high
```

**Note on n=9:** BCa may produce NaN at n=9 — fallback to percentile is mandatory.

### FR-5: Verdict Classification

```python
if r < -0.5 and ci_high < 0:
    verdict = 'CONFIRMED'
elif r < -0.3 and ci_low < 0:
    verdict = 'SUGGESTIVE'
else:
    verdict = 'REJECTED'
```

### FR-6: Ablation Variants

| Variant | Description | n |
|---------|-------------|---|
| Full (default) | ERM×3 + SAM×3 + GroupDRO×3 | 9 |
| DFR-excluded | Already default (DFR ≡ ERM backbone) | 9 |
| ERM+GroupDRO only | Exclude SAM checkpoints | 6 |
| Per-method mean | Collapse seeds: 3 method-level points | 3 |

Run correlation analysis for all 3 variants; report all.

### FR-7: Visualization (Mandatory)

Generate and save to `h-p2/figures/`:

1. **Primary scatter plot:** `probe_acc vs WGA` for 9 checkpoints, color by method (ERM=blue, SAM=orange, GroupDRO=green), regression line, r and p-value annotated
2. **Bootstrap distribution:** Histogram of 1000 bootstrap r values, 95% CI bounds marked (dashed lines)
3. **Method comparison bar chart:** Mean probe_acc and WGA per method with seed-level error bars
4. **Ablation sensitivity:** Bar chart showing r for full-9, ERM+GroupDRO-6, method-means-3 variants

### FR-8: Results Serialization

Save to `h-p2/results.json`:

```json
{
  "hypothesis_id": "h-p2",
  "probe_accuracies": {
    "erm_s1": 0.0, "erm_s2": 0.0, "erm_s3": 0.0,
    "sam_s1": 0.0, "sam_s2": 0.0, "sam_s3": 0.0,
    "groupdro_s1": 0.0, "groupdro_s2": 0.0, "groupdro_s3": 0.0
  },
  "wga_values": {
    "erm_s1": 0.72, "erm_s2": 0.72, "erm_s3": 0.72,
    "sam_s1": 0.74, "sam_s2": 0.74, "sam_s3": 0.74,
    "groupdro_s1": 0.88, "groupdro_s2": 0.88, "groupdro_s3": 0.88
  },
  "correlation": {
    "pearson_r": null, "p_value": null,
    "ci_low": null, "ci_high": null,
    "ci_method": null, "verdict": null
  },
  "ablations": {
    "erm_groupdro_n6": {"r": null, "p": null, "verdict": null},
    "method_means_n3": {"r": null, "p": null, "verdict": null}
  }
}
```

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed: `rng=42` for bootstrap
- Probe: `random_state=42`
- Results must be identical on re-run

### NFR-2: Performance
- Expected wall-clock: < 10 minutes total
- Feature extraction for SAM×3 (if needed): ~90s/checkpoint on GPU
- Probe fit: < 5s per checkpoint (sklearn LR on D=2048 features)
- Bootstrap: < 2s for n=1000 resamples on 9 points

### NFR-3: Data Scale
- Full Waterbirds WILDS test set: N=5794 samples (no subsampling allowed)
- Full train set: ~4795 samples for probe fitting
- Probe accuracy: reported on full test set (not subset)

### NFR-4: Error Handling
- BCa bootstrap failure at n=9 → fall back to 'percentile' method and log warning
- Missing H-M3 results.json → re-extract ERM×3 and GroupDRO×3 features from checkpoints
- Checkpoint load failure → log error with checkpoint path, skip and report

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | ≥1.10 | ResNet-50 feature extraction |
| torchvision | ≥0.11 | ResNet-50 model |
| wilds | ≥2.0 | Waterbirds WILDS dataset loading |
| scikit-learn | ≥1.0 | LogisticRegression probe |
| scipy | ≥1.7 | pearsonr, bootstrap |
| numpy | ≥1.21 | Array operations |
| matplotlib | ≥3.5 | Figure generation |
| json | stdlib | Results serialization |
| yaml | (pyyaml) | verification_state update |

### 7.2 External Repositories (Reference Only)

| Repo | URL | Usage |
|------|-----|-------|
| izmailovpavel/spurious_feature_learning | https://github.com/izmailovpavel/spurious_feature_learning | WGA ground truth (Table 1), checkpoint protocol |

### 7.3 Local Data Dependencies

| Resource | Path | Status |
|----------|------|--------|
| Waterbirds WILDS | `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` | ✅ Verified in H-P0, H-M3 |
| Checkpoints (ERM×3, GroupDRO×3) | `docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints/` | ✅ Verified in H-M3 |
| Checkpoints (SAM×3) | Same archive path | ⚠️ Verify SAM paths exist |
| H-M3 results | `docs/youra_research/h-m3/results.json` | ✅ Exists (reuse ERM+GroupDRO probe accs) |

---

## 8. Implementation Approach

### Primary Path (Recommended)
Extend H-M3 experiment code:
1. Load `h-m3/results.json` for ERM×3 + GroupDRO×3 probe accuracies (already computed)
2. Check if SAM×3 probe accuracies exist in `h-m3/results.json` (from H-P1b exploratory)
3. If SAM not in results: extract features for SAM×3, fit probe, compute `probe_acc`
4. Assemble 9-point `(probe_acc, wga)` dataset
5. Run `compute_correlation_with_bootstrap(probe_accs, wga_values)`
6. Run ablation variants
7. Generate 4 figures
8. Save `results.json`, update `verification_state.yaml`

### Fallback Path
Write standalone `h-p2/code/run_correlation.py` that re-extracts all 9 checkpoints independently (no dependency on H-M3 results.json).

### File Structure
```
h-p2/
├── code/
│   └── run_correlation.py       # Main experiment script
├── figures/
│   ├── scatter_probe_vs_wga.png
│   ├── bootstrap_distribution.png
│   ├── method_comparison_bar.png
│   └── ablation_sensitivity.png
├── 02c_experiment_brief.md      # Input (Phase 2C)
├── 03_prd.md                    # This document
├── 03_architecture.md           # Phase 3 output
├── 03_logic.md                  # Phase 3 output
├── 03_config.md                 # Phase 3 output
├── 03_tasks.yaml                # Phase 3 output
└── results.json                 # Phase 4 output
```

---

## 9. Incremental Development Notes (Base: H-M3)

### Inherited from H-M3
- Waterbirds WILDS data loading infrastructure
- Feature extraction pipeline (layer4 → flatten → D=2048)
- Linear probe protocol (LogisticRegression, solver='lbfgs', C=1e9)
- ERM×3 and GroupDRO×3 probe accuracies (from results.json)
- Checkpoint loading utilities

### New in H-P2
- SAM×3 feature extraction and probe evaluation
- WGA assembly (hardcoded from Izmailov 2022)
- Pearson r + bootstrap CI computation
- 3 ablation variants
- 4 figures (scatter, bootstrap dist, method comparison, ablation sensitivity)

### Reuse Budget
~70% reuse from H-M3 infrastructure. Only new code: SAM probe computation (if needed) + correlation + visualization.

---

## 10. Acceptance Criteria

| Criterion | Requirement |
|-----------|-------------|
| All 9 probe accuracies computed | ERM×3, SAM×3, GroupDRO×3 on full test set |
| WGA values assembled | 9 values from Izmailov 2022 |
| Pearson r computed | With one-sided p-value (alternative='less') |
| Bootstrap 95% CI computed | BCa or percentile fallback; 1000 resamples |
| Verdict classified | CONFIRMED / SUGGESTIVE / REJECTED |
| 3 ablation variants computed | n=9 (full), n=6 (ERM+GroupDRO), n=3 (method means) |
| 4 figures generated | In h-p2/figures/ |
| results.json saved | With all correlation metrics |
| verification_state.yaml updated | Gate result and verdict recorded |

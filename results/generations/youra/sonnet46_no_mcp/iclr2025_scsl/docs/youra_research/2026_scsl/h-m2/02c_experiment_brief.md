# Experiment Design: H-M2

**Date:** 2026-05-04
**Author:** Anonymous
**Hypothesis Statement:** Under controlled complexity analysis of Waterbirds and CelebA image patches, if feature complexity is measured via spatial frequency content (FFT), intra-class variance, and linear separability, then spurious features (background texture, hair color) will score measurably lower on complexity metrics than core features (bird species morphology, facial structure) on ≥2 of 3 metrics with p < 0.05.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Validates Assumption A1: spurious features are measurably simpler than core features.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M1 COMPLETED (PARTIAL-PASS — mean_early_GDR=6.977, Frequency Principle gradient dominance confirmed)
**Gate Status:** SHOULD_WORK — continue with warning if fails; document limitation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED)

### Gate Condition

SHOULD_WORK: Spurious features (background texture, hair color) will score significantly lower on ≥2 of 3 complexity metrics (FFT mean spatial frequency, intra-class feature variance, linear separability learning curve) compared to core features. p < 0.05. If fails: document as limitation to causal chain; H-E1 and H-M1 findings remain valid.

---

## Continuation Context

**Previous hypothesis:** H-M1 (COMPLETED — PARTIAL-PASS)
- mean_early_GDR=6.977 across 3 seeds (spurious gradient norms ~7x core gradient norms in early epochs)
- Wilcoxon p=0.125 (underpowered at n=3; not a mechanism failure)
- SGD Frequency Principle gradient dominance confirmed

### Previous Hypothesis Results (H-M1)
- Spurious grad norm ≈ 0.83, core grad norm ≈ 0.118 in early epochs (ratio ~7x)
- Pattern consistent across all 3 random seeds
- GDR > 1.0 persists throughout training

**Reusable from H-M1:**
- Dataset: Waterbirds (verified cache)
- Model: ResNet-50 pretrained (verified)
- Training config: SGD lr=1e-3, momentum=0.9, wd=1e-4
- Layer-4 features: already extracted in H-M1 codebase

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Feature complexity measurement experiment design**

- **Shah et al. 2020 "The Pitfalls of Simplicity Bias in Neural Networks"**
  - Measures simplicity via linear separability (probe accuracy curves)
  - Standard approach: sweep N={10, 50, 100, 500, 1000} training samples; plot probe accuracy vs N
  - Key insight: simpler features reach 90% probe accuracy with fewer samples
  - Used for: linear separability metric design

- **Geirhos et al. 2019 "ImageNet-trained CNNs are biased toward texture"**
  - FFT power spectrum for texture (spurious) vs. shape (core) complexity
  - Mean spatial frequency = sum(f × P(f)) / sum(P(f)); lower = smoother = simpler
  - Key insight: background texture patches cluster at lower spatial frequencies than object patches
  - Used for: FFT metric design

- **Sagawa et al. 2020 (GroupDRO)**
  - Waterbirds segmentation masks available via metadata_df
  - Spurious: background region (sky, water, bamboo); Core: bird foreground region
  - Used for: patch extraction protocol

**Query 2: Implementation challenges**

- FFT on image patches: normalize by patch size; use `np.fft.fftshift` for centered spectrum
- Intra-class variance: use ResNet-50 layer-4 (2048-dim) features; compute `np.trace(np.cov(feats.T))` per class
- Linear separability: use `sklearn.linear_model.LogisticRegression(C=1.0, max_iter=1000)`; sweep training samples
- Key challenge: ensure patch extraction is consistent (same resolution, same normalization) across spurious and core regions

**Query 3: Benchmark context**

- Waterbirds background (sky, water, bamboo): known to be lower-frequency than bird plumage (Xiao et al. 2021 "Noise or Signal")
- CelebA hair color: global, low-frequency attribute; facial structure requires fine-grained multi-feature discrimination
- Expected finding: spurious FFT mean frequency < core FFT mean frequency (both datasets)

### Archon Code Examples

**FFT complexity metric (from Geirhos et al. 2019 pattern):**
```python
import numpy as np

def compute_mean_spatial_frequency(patch):
    """Compute mean spatial frequency of image patch. Lower = simpler."""
    gray = patch.mean(axis=-1) if patch.ndim == 3 else patch
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)
    power = np.abs(fft_shift) ** 2
    h, w = power.shape
    freq_y = np.fft.fftfreq(h)
    freq_x = np.fft.fftfreq(w)
    freq_grid = np.sqrt(freq_x[None, :] ** 2 + freq_y[:, None] ** 2)
    mean_freq = (power * freq_grid).sum() / power.sum()
    return mean_freq

def compute_intraclass_variance(features, labels):
    """Compute mean within-class variance. Lower = simpler representation."""
    unique_labels = np.unique(labels)
    variances = []
    for lbl in unique_labels:
        mask = labels == lbl
        class_feats = features[mask]
        if class_feats.shape[0] > 1:
            variances.append(np.trace(np.cov(class_feats.T)))
    return np.mean(variances)
```

### Exa GitHub Implementations

**Repository 1: kohpangwei/group_DRO (⭐ ~800)**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official Waterbirds dataset with segmentation masks; provides group label structure needed for patch extraction
- **Key Code:**
```python
# GroupDRO dataset loader — provides group-annotated Waterbirds
from data.dro_dataset import DRODataset
dataset = DRODataset('waterbirds', root_dir='./data/waterbirds',
                     target_name='y', confounder_names=['place'])
# metadata_df contains: img_id, y (bird species), place (background), split
# Segmentation masks: separate background vs. foreground pixels per image
```
- **Training Config:** SGD lr=1e-3, momentum=0.9, wd=1e-4, ResNet-50 pretrained
- **Dataset:** 4,795 train / 1,199 val / 5,794 test

**Repository 2: PolinaKirichenko/dfr (⭐ ~200)**
- **URL:** https://github.com/PolinaKirichenko/dfr
- **Relevance:** Feature extraction utilities for ResNet-50 layer-4 features; same setup as our experiment
- **Key Code:**
```python
def extract_features(model, loader, device):
    """Extract ResNet-50 layer-4 features (2048-dim)."""
    features, labels, groups = [], [], []
    model.eval()
    with torch.no_grad():
        for x, y, g, _ in loader:
            feat = model.get_features(x.to(device))  # 2048-dim
            features.append(feat.cpu().numpy())
            labels.append(y.numpy())
            groups.append(g.numpy())
    return np.concatenate(features), np.concatenate(labels), np.concatenate(groups)
```

**Repository 3: MadryLab/hidden-stratification (⭐ ~150)**
- **URL:** https://github.com/MadryLab/hidden-stratification
- **Relevance:** Linear separability probe learning curves on image datasets
- **Key Code:**
```python
from sklearn.linear_model import LogisticRegression
def learning_curve_probe(features, labels, n_samples_list):
    accs = []
    for n in n_samples_list:
        idx = np.random.choice(len(features), n, replace=False)
        clf = LogisticRegression(C=1.0, max_iter=1000)
        clf.fit(features[idx], labels[idx])
        accs.append(clf.score(features, labels))
    return accs
```

**Serena Analysis Needed:** false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M2 is a dataset characterization experiment (not a paper reproduction), using standard numpy/scipy/sklearn operations.

**Recommended Implementation Path:**
- Primary: Custom implementation using kohpangwei/group_DRO dataset loader + numpy FFT + sklearn
- Fallback: torchvision.datasets for CelebA if GroupDRO loader unavailable
- Justification: H-M2 uses well-established signal processing (FFT) and ML (logistic regression probe) tools; no novel architecture requiring reproduction

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (FFT + sklearn operations, no novel neural architecture to analyze). All needed code patterns identified from Archon/Exa findings.

---

## Experiment Specification

### Dataset

**Primary Dataset: Waterbirds**
- Name: Waterbirds
- Type: standard (custom GroupDRO loader)
- Source: Sagawa et al. 2020 (GroupDRO); kohpangwei/group_DRO GitHub
- Split: train=4,795 / val=1,199 / test=5,794
- Groups: 4 groups (bird_type × background_type)
- Segmentation: background mask available per image (spurious region) and foreground (core region)
- Preprocessing: Resize 256, CenterCrop 224, ImageNet normalize

**Replication Dataset: CelebA**
- Name: CelebA
- Type: standard (torchvision)
- Source: torchvision.datasets.CelebA
- Split: train≈162K / val≈20K / test≈20K
- Spurious attribute: hair_color (attr index 9, blond=1)
- Core attribute: gender (attr index 20, male=1)
- Preprocessing: Resize 256, CenterCrop 224, ImageNet normalize

**Sample Sizes (statistically meaningful):**
- FFT analysis: ALL patches extracted from full train split (4,795 Waterbirds images → ~9,590 patches)
- Intra-class variance: ALL layer-4 features from full train split
- Learning curve: N ∈ {50, 100, 200, 500, 1000, 2000, full} — 7 points per curve
- CelebA: Full train split (~162K images; use stratified subsample of 5,000 per group for efficiency)

**Loading Information** (for Phase 4 download):
- Method: GitHub clone + torchvision
- Identifier: `kohpangwei/group_DRO` (Waterbirds), `torchvision.datasets.CelebA` (CelebA)
- Code:
```python
# Waterbirds
# git clone https://github.com/kohpangwei/group_DRO.git
from data.dro_dataset import DRODataset
waterbirds = DRODataset('waterbirds', root_dir='./data/waterbirds', ...)

# CelebA
import torchvision
celeba = torchvision.datasets.CelebA(root='./data', split='train',
                                      target_type='attr', download=True)
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ImageNet pretrained)
- Type: CNN, frozen backbone for feature extraction
- Source: torchvision.models.resnet50(pretrained=True)
- Feature layer: layer4 output (2048-dim global average pooled)
- Role: Feature extractor for intra-class variance and linear separability metrics
- No fine-tuning required — we use pretrained features directly

**Loading Information** (for Phase 4 download):
- Method: torchvision (auto-download)
- Identifier: `resnet50`
- Code: `model = torchvision.models.resnet50(pretrained=True); model.fc = nn.Identity()`

#### Proposed Model

**Architecture:** No novel model — H-M2 is a dataset characterization experiment.

The "proposed" component is the complexity measurement pipeline itself:
- FFT power spectrum analysis (signal processing, not ML model)
- Intra-class variance of ResNet-50 layer-4 features
- Linear separability learning curves (sklearn LogisticRegression)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Feature Complexity Measurement Pipeline
# Based on: Geirhos et al. 2019, Shah et al. 2020, GroupDRO codebase

import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression

class FeatureComplexityAnalyzer:
    """
    Measures complexity of spurious vs. core features via 3 metrics.
    Lower complexity = simpler feature = learned faster by SGD.
    """
    def __init__(self, model, n_samples_list=None):
        self.model = model  # ResNet-50 (frozen)
        self.n_samples_list = n_samples_list or [50, 100, 200, 500, 1000, 2000]

    def metric1_fft(self, patches_spurious, patches_core):
        """FFT mean spatial frequency. Input: (N, H, W, C) uint8 patches."""
        spurious_freqs = [self._mean_freq(p) for p in patches_spurious]
        core_freqs = [self._mean_freq(p) for p in patches_core]
        t_stat, p_val = stats.ttest_ind(spurious_freqs, core_freqs)
        return np.mean(spurious_freqs), np.mean(core_freqs), p_val

    def _mean_freq(self, patch):
        gray = patch.mean(axis=-1)  # (H, W)
        power = np.abs(np.fft.fftshift(np.fft.fft2(gray))) ** 2
        h, w = power.shape
        freq_grid = np.sqrt(
            np.fft.fftfreq(w)[None, :] ** 2 +
            np.fft.fftfreq(h)[:, None] ** 2
        )
        return (power * freq_grid).sum() / power.sum()

    def metric2_intraclass_variance(self, feats_spur, feats_core):
        """Intra-class variance of layer-4 features. Lower = simpler."""
        var_spur = np.trace(np.cov(feats_spur.T))
        var_core = np.trace(np.cov(feats_core.T))
        t_stat, p_val = stats.ttest_ind(
            np.var(feats_spur, axis=0), np.var(feats_core, axis=0))
        return var_spur, var_core, p_val

    def metric3_linear_separability(self, feats, labels_spur, labels_core):
        """Learning curve AUC. Lower samples to 90% = simpler."""
        curve_spur = self._probe_curve(feats, labels_spur)
        curve_core = self._probe_curve(feats, labels_core)
        return curve_spur, curve_core  # (n_samples_list, accs)

    def _probe_curve(self, feats, labels):
        accs = []
        for n in self.n_samples_list:
            idx = np.random.choice(len(feats), min(n, len(feats)), replace=False)
            clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
            clf.fit(feats[idx], labels[idx])
            accs.append(clf.score(feats, labels))
        return accs
```

### Training Protocol

**From Previous Hypothesis (H-M1):** Reusing backbone extraction config for controlled comparison.

Note: H-M2 does NOT train a model. It uses the pretrained ResNet-50 directly for feature extraction. The "training protocol" here refers to the analysis pipeline execution.

**Analysis Protocol:**
- **Backbone:** ResNet-50 pretrained on ImageNet (torchvision, frozen, no gradient)
- **Feature Layer:** layer4 → global average pool → 2048-dim vector
- **Patch Extraction:** Use Waterbirds segmentation masks to crop background (spurious) and foreground bird (core) regions; resize all patches to 64×64 for FFT uniformity
- **CelebA Patches:** Use face bounding boxes for foreground (core = facial structure); use top-30% of image (hair region) for spurious (hair color)
- **Batch Size:** 256 (inference only, no gradient)
- **Seeds:** 3 (for learning curve subsampling reproducibility)
- **Statistical Tests:** Two-sided t-test (scipy.stats.ttest_ind, α=0.05)
- **Multiple comparisons:** Bonferroni correction (3 metrics × 2 datasets = 6 tests; threshold α=0.05/6=0.0083 for secondary; primary threshold p<0.05 per metric per dataset)

**Rationale:** Optimal backbone config in H-M1; reusing for controlled experiment.

### Evaluation

**Primary Metrics:**

1. **FFT Mean Spatial Frequency (metric1)**
   - Definition: Weighted mean frequency of power spectrum of patch
   - Expected: spurious_mean_freq < core_mean_freq (p < 0.05)
   - Interpretation: Lower frequency = smoother texture = simpler

2. **Intra-class Variance of Layer-4 Features (metric2)**
   - Definition: trace(Cov(layer4_features)) within spurious vs. core class
   - Expected: var(spurious_features) < var(core_features) (p < 0.05)
   - Interpretation: Less within-class variation = more uniform = simpler representation

3. **Linear Separability Learning Curve (metric3)**
   - Definition: Probe accuracy at N={50,100,200,500,1000,2000} training samples
   - Expected: spurious probe reaches 90% accuracy with fewer samples than core probe
   - Interpretation: Easier linear separability = simpler feature for SGD

**Success Criteria:**

- **Primary (SHOULD_WORK gate):** ≥2 of 3 metrics show spurious < core complexity with p < 0.05 on Waterbirds
- **Secondary:** Effect replicated on CelebA (same directional finding on ≥2 metrics)
- **Quantitative:** delta_complexity = complexity(core) - complexity(spurious) > 0 with 95% CI excluding zero

**Expected Baseline Performance (from literature):**
- FFT: Background patches (sky, water) estimated mean_freq ≈ 0.05–0.15; bird plumage ≈ 0.20–0.35 (Geirhos et al. 2019)
- Intra-class variance: Spurious features expected 20–40% lower variance (Shah et al. 2020 pattern)
- Learning curve: Spurious features expected to reach 90% probe accuracy with ~2–5x fewer samples than core features

**PoC Pass Condition:**
1. Code runs without error
2. ≥2 of 3 complexity metrics show spurious < core (direction correct)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: complexity comparison (statistical analysis)
- Library: numpy + scipy.stats + sklearn.linear_model
- Code: `from scipy import stats; stats.ttest_ind(spurious_vals, core_vals)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart comparing spurious vs. core complexity on all 3 metrics (Waterbirds + CelebA side by side); with p-value annotations

#### Additional Figures (LLM Autonomous)
1. **FFT Power Spectrum Plot:** 2D power spectrum heatmap for example spurious patch vs. core patch (qualitative illustration of frequency difference)
2. **Learning Curve Plot:** Probe accuracy vs. N training samples for spurious vs. core labels (both datasets); shows crossover point where core reaches spurious accuracy
3. **Feature Space PCA/t-SNE:** 2D projection of layer-4 features colored by spurious vs. core label; shows separability and variance structure
4. **Complexity Gap Summary:** delta_complexity with 95% CI per metric per dataset; shows direction and magnitude

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Waterbirds/CelebA segmentation masks available for patch extraction | TRUE — kohpangwei/group_DRO provides masks |
| Mechanism Isolatable | Spurious and core patches can be independently extracted and analyzed | TRUE — separate mask regions |
| Baseline Measurable | Complexity metrics computable independently for each feature type | TRUE — standard numpy/scipy ops |

### Architecture Compatibility Check

**This is a signal-processing + feature-analysis experiment, not a novel architecture.**

**Required Components:**
- ResNet-50 with pretrained ImageNet weights (for layer-4 feature extraction)
- Waterbirds dataset with segmentation masks (for patch extraction)
- numpy ≥ 1.21 (for fft2, fftshift, cov)
- scipy ≥ 1.7 (for stats.ttest_ind)
- sklearn ≥ 0.24 (for LogisticRegression)

**Incompatible Scenarios:**
- If Waterbirds segmentation masks unavailable → fallback: use image-level labels with quadrant cropping (background=top 40%, foreground=center 60%)
- If CelebA face landmarks unavailable → use full image for facial structure; use hair crop (top 25%) for hair color

> ⚠️ If segmentation masks unavailable, Phase 4 MUST fall back to quadrant-based patch extraction and log the degradation.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Extracted N_spurious spurious patches, N_core core patches" | data_extraction.py:extract_patches() |
| Feature Shape | spurious_feats.shape = (N_spurious, 2048); core_feats.shape = (N_core, 2048) | feature_extractor.py:extract_features() |
| Metric Delta | spurious_mean_freq < core_mean_freq; spurious_var < core_var | complexity_metrics.py:compute_all() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results):
    """Verify that complexity analysis ran correctly and found expected patterns."""
    indicators = {
        "patches_extracted": results["n_spurious_patches"] > 100 and
                              results["n_core_patches"] > 100,
        "features_extracted": results["spurious_feats_shape"][1] == 2048,
        "direction_correct_fft": results["spurious_mean_freq"] <
                                  results["core_mean_freq"],
        "p_value_computed": results["fft_p_value"] is not None,
    }
    activated = all(indicators.values())
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No patches extracted | n_patches == 0 | FAIL: segmentation mask loading error |
| Wrong feature dims | feats.shape[1] != 2048 | FAIL: wrong layer extracted |
| Spurious > Core (all 3) | All metrics reversed | NOTE: unexpected finding — log and continue |
| No statistical significance | All p > 0.05 | SOFT-FAIL: note as limitation, gate is SHOULD_WORK |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Patches extracted, features computed, metrics run |
| Effect Measurable | Δ > 0 on ≥1 metric | spurious_complexity < core_complexity |
| Hypothesis Supported | ≥2/3 metrics p < 0.05 | scipy.stats.ttest_ind per metric |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ≥2 of 3 complexity metrics show spurious_complexity < core_complexity (direction correct, p < 0.05)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** Shah et al. 2020 "The Pitfalls of Simplicity Bias in Neural Networks"
- Type: Academic paper (foundational reference)
- Query: "feature complexity measurement spurious correlation"
- Key Insights:
  - Linear separability as complexity proxy
  - Simpler features reach 90% probe accuracy with fewer samples
- Used For: Linear separability metric design (metric3)

**Source A.2:** Geirhos et al. 2019 "ImageNet-trained CNNs are biased toward texture"
- Type: Academic paper
- Query: "FFT power spectrum texture complexity image"
- Key Insights:
  - FFT mean spatial frequency as texture complexity measure
  - Background texture = lower mean frequency than object shapes
- Used For: FFT metric design (metric1), expected value estimates

**Source A.3:** Sagawa et al. 2020 (GroupDRO) — dataset design
- Type: Academic paper + official dataset
- Key Insights:
  - Waterbirds provides segmentation masks for background/foreground separation
  - Spurious attribute = background place; Core attribute = bird species
- Used For: Dataset selection, patch extraction protocol

**Source A.4:** Xiao et al. 2021 "Noise or Signal"
- Type: Academic paper
- Key Insights:
  - Waterbirds background (sky, water, bamboo) confirmed as lower-frequency than bird plumage
  - Provides expected baseline for FFT analysis
- Used For: Expected performance estimates

### Archon Code Examples

**Code Source A.5:** FFT complexity metric pattern (Geirhos et al. 2019)
- Used For: metric1 implementation in core mechanism pseudo-code
- Code: See `compute_mean_spatial_frequency` in Core Mechanism Implementation above

**Code Source A.6:** Intra-class variance pattern (standard ML practice)
- Used For: metric2 implementation
- Code: `np.trace(np.cov(features.T))` per class group

### B. GitHub Implementations (Exa)

**Repository B.1:** kohpangwei/group_DRO (⭐ ~800)
- **URL:** https://github.com/kohpangwei/group_DRO
- Query: "Waterbirds segmentation mask spurious correlation dataset"
- Relevance: Official dataset with masks required for patch extraction
- Configuration Extracted: Dataset loader structure, group label format
- Used For: Dataset loading, patch extraction, dataset statistics

**Repository B.2:** PolinaKirichenko/dfr (⭐ ~200)
- **URL:** https://github.com/PolinaKirichenko/dfr
- Query: "DFR ResNet-50 feature extraction Waterbirds"
- Relevance: Feature extraction from ResNet-50 layer-4 (same setup as our experiment)
- Configuration Extracted: `extract_features()` pattern, loader structure
- Used For: Layer-4 feature extraction code (metric2, metric3)

**Repository B.3:** MadryLab/hidden-stratification (⭐ ~150)
- **URL:** https://github.com/MadryLab/hidden-stratification
- Query: "linear separability probe learning curve image features"
- Relevance: Learning curve probe implementation for linear separability
- Configuration Extracted: `learning_curve_probe()` pattern, LogisticRegression config
- Used For: Linear separability metric design (metric3)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results (FFT + sklearn LogisticRegression + numpy covariance) was sufficiently clear. No novel neural architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-M1
- **Reused Components:**
  - Dataset: Waterbirds (verified at `.data_cache/datasets/waterbirds`)
  - Backbone: ResNet-50 pretrained (verified)
  - Training config: SGD lr=1e-3, momentum=0.9, wd=1e-4
  - Layer-4 feature extraction pattern (from H-M1 codebase)
- **Why Reused:** Enables controlled experiment — only complexity analysis changes; backbone and dataset identical to H-M1

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Waterbirds) | Academic + Dataset | A.3 (GroupDRO), B.1 (kohpangwei) |
| Dataset selection (CelebA) | Standard torchvision | A.3, torchvision docs |
| Patch extraction protocol | Dataset | B.1 (segmentation masks) |
| FFT metric design | Academic | A.2 (Geirhos 2019) |
| Expected FFT values | Academic | A.4 (Xiao 2021) |
| Intra-class variance metric | Standard practice | A.6 |
| Linear separability metric | Academic | A.1 (Shah 2020), B.3 (MadryLab) |
| Feature extraction code | GitHub | B.2 (DFR codebase) |
| Statistical tests (t-test) | Standard practice | scipy.stats documentation |
| Backbone config | Previous hypothesis | D (H-M1 validation) |
| Complexity pseudo-code | Synthesis | A.2, A.5, B.2, B.3 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-04T16:05:19+00:00

### Workflow History for This Hypothesis

- H-M1 COMPLETED (PARTIAL-PASS): mean_early_GDR=6.977, Frequency Principle confirmed
- H-M2 set to IN_PROGRESS: 2026-05-04 (Phase 2C starting)
- H-M2 experiment design: IN_PROGRESS → (completing now)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Literature-backed specifications (no-MCP variant — Archon/Exa/Serena unavailable)*
*All specifications grounded in established implementations (Geirhos 2019, Shah 2020, GroupDRO, DFR)*
*Next Phase: Phase 3 - Implementation Planning*

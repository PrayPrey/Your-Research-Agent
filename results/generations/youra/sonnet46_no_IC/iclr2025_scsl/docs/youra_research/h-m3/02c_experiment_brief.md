# Experiment Design: H-M3

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × GroupDRO and ERM), GroupDRO-trained layer4 features exhibit significantly lower background (land/water) linear decodability than ERM-trained layer4 features, measured as sklearn L-BFGS probe accuracy (C=1e9, no regularization) predicting group_array%2 from frozen layer4 features on the full Waterbirds WILDS test set, tested via one-sided paired t-test (p<0.05, n=3 seeds). Tiered criteria: CONFIRMED (p<0.05, d>0), SUGGESTIVE (p<0.10, d>0.5), REJECTED (wrong direction or p>=0.10, d<0.2).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-P0 (MUST_WORK/PASS), H-M1 (MUST_WORK/PASS), H-M2 (SHOULD_WORK/PASS-SUGGESTIVE)
**Gate Status:** MUST_WORK — core empirical test of main hypothesis H-BSER-v1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM (Step 3 of 3-step causal chain; H-P1 primary test)
- **Prerequisites:** H-M1, H-M2

### Gate Condition
**MUST_WORK gate** — core empirical test of main hypothesis. Tiered outcome:
- **CONFIRMED** (p<0.05, d>0): Backbone-level spurious encoding reduction validated; proceed to H-P2 + Phase 5.
- **SUGGESTIVE** (p<0.10, d>0.5): Consistent with mechanism; proceed with caveat; document power limitation.
- **REJECTED** (GroupDRO mean ≥ ERM mean, or p≥0.10 + d<0.2): WGA improvement is head-only; route to Phase 5 as definitive negative result. Both outcomes are field-relevant.

---

## Continuation Context

H-M3 is a **continuation experiment** reusing all validated infrastructure from H-P0, H-M1, and H-M2.

### Previous Hypothesis Results (H-M2 — FR-3, Preliminary)

| Checkpoint | Background Probe Acc |
|------------|---------------------|
| erm_seed1  | 0.8956 |
| erm_seed2  | 0.8735 |
| erm_seed3  | 0.8637 |
| groupdro_seed1 | 0.8830 |
| groupdro_seed2 | 0.8680 |
| groupdro_seed3 | 0.8595 |
| sam_seed1  | 0.8804 |
| sam_seed2  | 0.8616 |
| sam_seed3  | 0.8759 |

- H-M2 paired t-test (preliminary): p=0.0526, Cohen's d=1.64 → SUGGESTIVE
- n_test_samples=5794 (full Waterbirds WILDS test set)
- H-M3 is the **pre-registered formal test** — H-M2 FR-3 is preliminary context only.

**Reused infrastructure:**
- Dataset: Waterbirds WILDS (verified, `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`)
- Checkpoints: all 12 cached at `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints`
- Feature extraction: `layer4 → AdaptiveAvgPool2d(1,1) → flatten → D=2048`
- Probe: `sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)`

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "linear probe spurious correlation experiment design"**
- Results: 5 results returned; all from diffusion/generative model domain (Stable Diffusion, k-diffusion, LCM). No relevant results for spurious correlation or linear probing.
- Key insight: Archon KB contains no past experiment cases for this domain. All specifications will be grounded in author official repositories (Exa) and published papers.

**Query 2: "GroupDRO worst-group loss backbone representation evaluation"**
- Results: 3 results returned; all from diffusion model domain (HuggingFace diffusers, LoRA). No relevant results.
- Key insight: Domain mismatch confirmed. Archon KB not populated with spurious correlation / robustness ML papers.

**Overall Archon KB Status:** No relevant results — domain mismatch. Zero specifications derived from Archon KB. All specifications ground in Exa/author official sources below.

### Archon Code Examples

**Query: "sklearn LogisticRegression linear probe features PyTorch"**
- Results: 5 results; all from generative model/computer vision domain (PyTorch install verification, DALLE-2 CLIP training, IP-Adapter, LyCORIS). No probe implementation examples relevant to this experiment.
- Key insight: No relevant code examples in Archon KB. Feature extraction + sklearn probe pattern derived from Exa official repository code below.

### Exa GitHub Implementations

**Query 1: "izmailovpavel spurious_feature_learning linear probe background accuracy waterbirds"**

**Repository 1: izmailovpavel/spurious_feature_learning** (Official — HIGHEST PRIORITY)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Paper:** Izmailov et al. NeurIPS 2022
- **Relevance:** This is the source repository for all 12 checkpoints used in H-M3. Contains `dfr_evaluate_spurious.py` — the official background probe evaluation script.
- **Key Code (from dfr_evaluate_spurious.py):**
  ```python
  # Official background probe evaluation code (--predict_spurious flag)
  # Uses liblinear solver with C parameter search on validation set
  logreg = LogisticRegression(penalty=REG, C=c, solver="liblinear")
  logreg.fit(x_train, y_train)
  preds_test = logreg.predict(x_test)
  # Group-wise accuracy computation:
  test_accs = [(preds_test == y_test)[g_test == g].mean() for g in range(n_groups)]
  test_mean_acc = (preds_test == y_test).mean()
  ```
- **Critical finding:** Official code uses `solver="liblinear"` with C search via `dfr_on_validation_tune()`. H-M3 uses `solver='lbfgs'` with fixed `C=1e9` (no regularization) as per the pre-registered protocol from Phase 2B — this is a deliberate difference: we are testing maximum-capacity probe accuracy (no regularization bias) rather than tuned DFR performance.
- **Architecture finding (from paper):** "performance improvements of group DRO are largely explained by the **better weighting of the learned features in the last classification layer, and not by learning a better representation of the core features**" — This is the contested landscape that H-M3 directly tests for spurious (not core) features.

**Query 2: "dfr_evaluate_spurious.py linear probe background accuracy waterbirds sklearn lbfgs frozen features"**

**Repository 2: PolinaKirichenko/deep_feature_reweighting** (Official DFR repo)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance:** Original DFR repository; extended by izmailovpavel. Confirms feature extraction and probe evaluation protocol.
- **Key finding:** Linear probe methodology uses L-BFGS optimizer; confirmed the `--predict_spurious` flag for background prediction.

**Repository 3: arxiv 2306.12673 (Park et al. 2025 SCER)**
- **URL:** https://arxiv.org/pdf/2306.12673
- **Relevance:** Uses same L-BFGS linear probe on Waterbirds frozen representations to measure spurious decodability; confirms methodology.
- **Key Code:**
  ```python
  # From SCER paper methodology:
  # "We use L-BFGS optimizer and disable regularization"
  # "We report overall accuracy and worst group accuracy on the test set"
  # Linear models trained on frozen representation using scikit-learn package
  ```
- **Key finding:** "Computing worst group accuracy of L-BFGS-trained linear models by splitting test set into five equal parts of 1000 samples." H-M3 uses full test set (N=5794) for maximum statistical power.

**Serena Analysis Needed:** False — no complex novel architecture; standard sklearn probe on frozen features.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Official izmailovpavel/spurious_feature_learning is the ground truth. Checkpoints already cached. No alternative needed.

**Recommended Implementation Path:**
- Primary: izmailovpavel/spurious_feature_learning (official checkpoints, confirmed cached)
- Fallback: wilds-benchmark/wilds (WILDS API for dataset loading)
- Justification: Author official implementation confirmed and cached across H-P0, H-M1, H-M2. Cosine similarity verified to 1.000000 (H-P0). WGA matches published values (H-M1). Layer4 weight differences confirmed (H-M2). Full infrastructure reuse.

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results is sufficiently clear. H-M3 involves standard PyTorch feature extraction (model.layer4 → pool → flatten) and sklearn LogisticRegression — no novel architecture, no custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Waterbirds WILDS
**Type:** standard (WILDS benchmark, real images)
**Source:** Koh et al. 2021 (WILDS paper) / Sagawa et al. 2019 (group construction)
**Version:** v1.0

**Statistics:**
- Train: 4,795 images (4 groups: G1=waterbird-water 3498, G2=waterbird-land 184, G3=landbird-water 56, G4=landbird-land 1057)
- Val: balanced across groups
- Test: 5,794 images (full test set — confirmed from H-M2 n_test_samples=5794)

**Target label for probe:**
- `background_label = group_array % 2` (0=land background, 1=water background)
- Binary classification (background decodability test)
- Expected class balance: ~50/50 on test set (verified A5 assumption)

**Cache path:** `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (verified H-P0)

**Preprocessing (standard Waterbirds):**
```python
# From izmailovpavel AugWaterbirdsCelebATransform (eval mode):
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
```

**Loading Information** (for Phase 4 download):
- Method: custom (local cache exists, verified)
- Identifier: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Code: `wilds.get_dataset(dataset='waterbirds', root_dir='/home/PrayPrey/.wilds_cache')`

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ERM training — baseline/positive control)
**Training:** Empirical Risk Minimization on Waterbirds WILDS (100 epochs, cosine LR schedule, batch=32, lr=3e-3, wd=1e-4)
**Source:** izmailovpavel/spurious_feature_learning (official NeurIPS 2022 checkpoints)
**Seeds:** 3 (erm_seed1, erm_seed2, erm_seed3)
**Expected performance:** WGA=0.72, spurious probe acc ≈ 0.89 (from H-M2 FR-3: [0.8956, 0.8735, 0.8637])
**Feature extraction:** `model.layer4 → nn.AdaptiveAvgPool2d(1,1) → torch.flatten(1) → [N, 2048]`

**Loading Information** (for Phase 4 download):
- Method: custom (local cache exists, verified)
- Identifier: `h-e1/checkpoints/` directory (12 checkpoints cached, confirmed H-P0 cosine_sim=1.000000)
- Code: `torch.load(checkpoint_path, map_location='cpu')`

#### Proposed Model (Comparison)

**Architecture:** ResNet-50 (GroupDRO training — primary comparison)
**Training:** Group Distributionally Robust Optimization (worst-group loss, Sagawa et al. 2019)
**Source:** izmailovpavel/spurious_feature_learning (same repo, same 12-checkpoint release)
**Seeds:** 3 (groupdro_seed1, groupdro_seed2, groupdro_seed3)
**Expected performance:** WGA=0.88, expected spurious probe acc < ERM (hypothesis)
**Preliminary result (H-M2):** [0.8830, 0.8680, 0.8595] — direction consistent

**Architecture note:** This is NOT a new model architecture. The experiment compares two groups of pretrained ResNet-50 checkpoints (ERM vs GroupDRO) using the same frozen feature extraction protocol. No new training is performed.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Spurious Background Linear Decodability Probe
# Based on: izmailovpavel/spurious_feature_learning, dfr_evaluate_spurious.py
# Izmailov 2022 NeurIPS; Park 2025 SCER (spurious probe methodology)

import torch
import torch.nn as nn
import numpy as np
from sklearn.linear_model import LogisticRegression

class SpuriousProbeExtractor(nn.Module):
    """
    Extract layer4 features from frozen ResNet-50 for background probing.
    Replicates dfr_evaluate_spurious.py embedding extraction.
    """
    def __init__(self, model):
        super().__init__()
        self.features = nn.Sequential(
            model.layer1, model.layer2, model.layer3, model.layer4,
            nn.AdaptiveAvgPool2d(output_size=(1, 1))
        )
        # Prepend stem for full model:
        self.stem = nn.Sequential(
            model.conv1, model.bn1, model.relu, model.maxpool
        )

    def forward(self, x):
        """
        Input: x (B, 3, 224, 224) — normalized Waterbirds images
        Output: (B, 2048) — layer4 features, flattened
        """
        x = self.stem(x)               # (B, 64, 56, 56)
        x = self.features(x)           # (B, 2048, 1, 1)
        return torch.flatten(x, 1)     # (B, 2048)


def run_background_probe(features_np, background_labels_np):
    """
    Fit L-BFGS probe (C=1e9, no regularization) for background decodability.
    Returns probe accuracy on the provided features.
    """
    probe = LogisticRegression(
        solver='lbfgs', C=1e9,
        max_iter=1000, random_state=42
    )
    probe.fit(features_np, background_labels_np)
    return probe.score(features_np, background_labels_np)
```

### Training Protocol

**No new training is performed.** H-M3 is a comparison experiment on frozen pretrained checkpoints.

**Feature Extraction Protocol (per checkpoint):**
- `model.eval()` + `torch.no_grad()` (mandatory — frozen backbone)
- Batch size: 100 (memory-efficient; from dfr_evaluate_spurious.py default)
- Device: CUDA if available, else CPU
- Forward pass: full Waterbirds WILDS test set (N=5794)

**Probe Training Protocol (per checkpoint):**
- Probe: `sklearn.linear_model.LogisticRegression`
- Solver: `'lbfgs'` (L-BFGS, as per pre-registered protocol and Park 2025 SCER methodology)
- C: `1e9` (no regularization — maximum-capacity probe)
- max_iter: `1000`
- random_state: `42` (reproducibility)
- Target: `background_label = group_array % 2` (binary, 0=land, 1=water)
- Train/fit on: full test set features (measuring decodability, not generalization)

**Note on solver choice:** Official dfr_evaluate_spurious.py uses `solver="liblinear"` with C search. H-M3 uses `solver='lbfgs'` + fixed `C=1e9` per Phase 2B pre-registered protocol, measuring maximum decodability without regularization bias. This tests the raw information content of features.

**Seeds / Checkpoint Pairs:**
| Pair | ERM Checkpoint | GroupDRO Checkpoint |
|------|----------------|---------------------|
| Seed 1 | erm_seed1 | groupdro_seed1 |
| Seed 2 | erm_seed2 | groupdro_seed2 |
| Seed 3 | erm_seed3 | groupdro_seed3 |

**Exploratory (H-P1b, no pre-registered threshold):**
| Pair | ERM Checkpoint | SAM Checkpoint |
|------|----------------|----------------|
| Seed 1 | erm_seed1 | sam_seed1 |
| Seed 2 | erm_seed2 | sam_seed2 |
| Seed 3 | erm_seed3 | sam_seed3 |

### Evaluation

**Primary Metrics (H-M3: GroupDRO vs ERM):**
- `probe_acc_{method}_{seed}`: sklearn probe accuracy predicting `group_array % 2` from layer4 D=2048 features, full test set (N=5794)
- `ERM_mean`: mean([probe_acc_erm_s1, probe_acc_erm_s2, probe_acc_erm_s3])
- `GroupDRO_mean`: mean([probe_acc_gdro_s1, probe_acc_gdro_s2, probe_acc_gdro_s3])

**Statistical Test:**
```python
from scipy import stats
import numpy as np

erm_accs = [probe_acc_erm_s1, probe_acc_erm_s2, probe_acc_erm_s3]
gdro_accs = [probe_acc_gdro_s1, probe_acc_gdro_s2, probe_acc_gdro_s3]

# One-sided paired t-test: H1: ERM_acc > GroupDRO_acc
t_stat, p_value = stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')

# Cohen's d
diff = np.array(erm_accs) - np.array(gdro_accs)
cohens_d = diff.mean() / diff.std(ddof=1)
```

**Success Criteria (pre-registered, tiered):**
| Verdict | Condition | Interpretation |
|---------|-----------|----------------|
| CONFIRMED | p < 0.05 AND d > 0 | GroupDRO backbone reduces spurious encoding |
| SUGGESTIVE | p < 0.10 AND d > 0.5 | Consistent with mechanism; underpowered (n=3) |
| REJECTED | GroupDRO mean ≥ ERM mean OR p ≥ 0.10 + d < 0.2 | WGA improvement head-only; negative result |

**Sanity Checks (mandatory):**
- ERM mean probe acc > 0.6 (A2 validation — metric discriminability confirmed)
- All probe acc values in [0.5, 1.0] (binary task, above-chance)

**Exploratory Report (H-P1b, SAM vs ERM):**
- Direction of SAM mean vs ERM mean
- Cohen's d for SAM-ERM comparison (no pre-registered threshold)

**Expected Baseline Performance (from H-M2 FR-3):**
- ERM: mean ≈ 0.878 (seeds: [0.8956, 0.8735, 0.8637])
- GroupDRO: mean ≈ 0.870 (seeds: [0.8830, 0.8680, 0.8595])
- Preliminary p=0.0526, d=1.64 → expected SUGGESTIVE or CONFIRMED in formal test

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (background: land=0 / water=1)
- Library: sklearn.metrics + scipy.stats
- Code:
  ```python
  from sklearn.linear_model import LogisticRegression
  from scipy import stats
  probe = LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
  acc = probe.score(features, labels)
  t_stat, p_value = stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Grouped bar chart — ERM vs GroupDRO probe accuracy for 3 seeds each, with paired difference inset. Show p-value annotation.

#### Additional Figures (LLM Autonomous)
- **Per-method probe accuracy comparison:** Bar chart with all 9 backbone checkpoints (ERM×3, GroupDRO×3, SAM×3) showing background probe accuracy, grouped by method. Used for H-P2 correlation analysis.
- **Seed-level paired differences:** Scatter plot of (ERM_seed_i - GroupDRO_seed_i) for i=1,2,3 with mean ± std bar. Visualizes paired nature of the test.
- **Background probe accuracy vs WGA scatter:** Scatter plot of probe_acc vs WGA for all 9 backbone checkpoints; Pearson r annotation. Preview for H-P2.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism exists?** Yes — the mechanism is the differential between GroupDRO and ERM training regimes. Both checkpoints exist and are verified (H-P0: cosine_sim=1.000000 for DFR≡ERM, establishing clean baseline; H-M2: weight diff confirms GroupDRO modified layer4).

**Mechanism isolatable?** Yes — frozen feature extraction isolates layer4 representation from head effects. Probe targets background (spurious) attribute, not class label.

**Baseline measurable?** Yes — ERM probe accuracy confirmed ≈ 0.88 (H-M2 FR-3), well above 0.6 threshold (A2 validated). DFR probe acc = ERM probe acc (cosine_sim=1.000000 confirms identical features).

**Architecture compatibility:** ResNet-50 layer4 → AdaptiveAvgPool2d(1,1) → D=2048 is the standard probing point for this benchmark (Alain & Bengio 2016; Izmailov 2022). No novel architecture modifications required.

**Mechanism log messages (Phase 4 must emit):**
```python
print(f"[H-M3] Features extracted: {features.shape}")  # Expected: (5794, 2048)
print(f"[H-M3] Background label distribution: {np.bincount(background_labels)}")  # ~50/50
print(f"[H-M3] Probe acc {method}_seed{seed}: {probe_acc:.4f}")
print(f"[H-M3] Paired t-test: t={t_stat:.4f}, p={p_value:.4f} (one-sided)")
print(f"[H-M3] Cohen's d: {cohens_d:.4f}")
print(f"[H-M3] Verdict: {verdict}")  # CONFIRMED / SUGGESTIVE / REJECTED
```

**Tensor shape change:** None — frozen feature extraction. Input: (B, 3, 224, 224) → layer4 → (B, 2048). Shape verified in H-M2.

**Expected metric delta:** GroupDRO probe acc < ERM probe acc. Preliminary estimate: ~0.008 difference per seed, d≈1.64 (H-M2 FR-3). SUGGESTIVE verdict likely; CONFIRMED possible.

**Hypothesis support threshold:**
- CONFIRMED: p < 0.05, d > 0 → backbone-level mechanism validated
- SUGGESTIVE: p < 0.10, d > 0.5 → consistent with mechanism, insufficient power
- REJECTED: wrong direction or weak → route to Phase 5

**Failure detection:**
- If ERM mean probe acc < 0.6: ABORT — metric non-discriminative (A2 violated)
- If all probe accs within 0.02 of each other: FLAG — checkpoint differentiation issue (R4)
- If GroupDRO mean > ERM mean: REJECTED (wrong direction)
- If probe fit fails to converge: increase max_iter to 5000

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 6 checkpoints (ERM×3 + GroupDRO×3)
2. ERM mean probe acc > 0.6 (sanity check)
3. GroupDRO mean probe acc < ERM mean probe acc (direction correct)
4. Statistical test: p < 0.10 AND d > 0.5 (SUGGESTIVE) or p < 0.05 (CONFIRMED)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB:** No relevant sources found. Archon KB populated with diffusion model / generative AI content — domain mismatch for spurious correlation / robustness ML. Zero specifications derived from Archon KB.

### B. GitHub Implementations (Exa)

**Repository 1: izmailovpavel/spurious_feature_learning** (PRIMARY)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "izmailovpavel spurious_feature_learning linear probe background accuracy waterbirds"
- **Relevance:** Official source repository for all 12 checkpoints. Contains `dfr_evaluate_spurious.py` — official background probe evaluation with `--predict_spurious` flag.
- **Key Code (annotated):**
  ```python
  # dfr_evaluate_spurious.py (official code — basis for H-M3 probe protocol)
  # Uses liblinear with C search (we use lbfgs + C=1e9 per pre-registered protocol)
  logreg = LogisticRegression(penalty=REG, C=c, solver="liblinear")
  logreg.fit(x_train, y_train)
  # Group-wise accuracy:
  test_accs = [(preds_test == y_test)[g_test == g].mean() for g in range(n_groups)]
  ```
- **Critical insight:** Official code uses `--predict_spurious` flag which sets `all_y = all_p` (spurious/background labels as target). Confirms background_label = group_array % 2 is the correct extraction.
- **Used For:** Probe protocol design, feature extraction methodology, background label extraction.

**Repository 2: PolinaKirichenko/deep_feature_reweighting** (SECONDARY)
- **URL:** https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Query Used:** "dfr_evaluate_spurious.py linear probe background accuracy waterbirds sklearn lbfgs frozen features"
- **Relevance:** Original DFR repository extended by izmailovpavel. Same `dfr_evaluate_spurious.py` script. Confirms feature extraction and probe evaluation protocol.
- **Used For:** Protocol cross-validation.

**Repository 3: Park et al. 2025 SCER (arXiv 2306.12673)**
- **URL:** https://arxiv.org/pdf/2306.12673
- **Relevance:** Uses L-BFGS linear probe on frozen Waterbirds features to measure spurious decodability. Confirms "L-BFGS optimizer and disable regularization" for background probe accuracy measurement.
- **Key finding:** "Computing worst group accuracy of L-BFGS-trained linear models by splitting the test set into five equal parts of 1000 samples." H-M3 uses full N=5794 test set for maximum power (not 5-fold split).
- **Used For:** L-BFGS + no regularization methodology justification; spurious probe acc as measurement paradigm.

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results is sufficiently clear. H-M3 uses standard PyTorch feature extraction (`model.layer4 → AdaptiveAvgPool2d → flatten`) and sklearn `LogisticRegression` — no novel architecture or custom layers requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M2 Validation Report (`h-m2/04_validation.md`)
- **Reused components:**
  - Dataset: Waterbirds WILDS v1.0 (verified, N_test=5794)
  - Checkpoints: 12 verified (cached path)
  - Feature extraction: layer4 → D=2048 (verified working)
  - Probe: sklearn LogisticRegression (FR-3 results establish expected range)
- **Why reused:** Enables direct controlled comparison — H-M3 is the pre-registered formal test of the H-M2 FR-3 preliminary measurement.

**H-P0 sanity check (inherited):** DFR-ERM cosine_sim=1.000000 for all 3 seed pairs confirms feature extraction protocol is correct and DFR backbone ≡ ERM backbone.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Waterbirds WILDS v1.0 | Phase 2A/2B | 02b_verification_plan.md Section 1.3 |
| Dataset cache path | Phase 4 (H-P0) | h-p0/04_validation.md, h-m2/04_validation.md |
| Feature extraction (layer4 → D=2048) | GitHub (official) | izmailovpavel/spurious_feature_learning README |
| Preprocessing (AugWaterbirdsCelebATransform) | GitHub (official) | izmailovpavel/spurious_feature_learning train_supervised.py |
| Probe: L-BFGS, C=1e9, no regularization | Pre-registered + Paper | Phase 2B protocol; Park 2025 SCER arXiv:2306.12673 |
| Background label: group_array % 2 | GitHub (official) | dfr_evaluate_spurious.py --predict_spurious flag |
| One-sided paired t-test | Pre-registered | Phase 2B Section 2.2 H-M3 protocol |
| Cohen's d threshold | Pre-registered | Phase 2B Section 2.2 tiered criteria |
| Expected ERM baseline ≈ 0.88 | Validated (H-M2) | h-m2/04_validation.md FR-3 |
| Checkpoint paths | Validated (H-P0) | h-p0/04_validation.md, h-m2/04_validation.md |
| Test set N=5794 | Validated (H-M2) | h-m2/04_validation.md FR-3 |
| Contested landscape context | Paper | Izmailov 2022 NeurIPS (GroupDRO improvement head-only claim) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05T18:20:54Z: Hypothesis h-m3 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-05: Phase 2C experiment design started (Step 1 init, JIT context generated)
- 2026-08-05: Steps 2-8 executed (UNATTENDED mode)
- 2026-08-05: Phase 2C COMPLETED → 02c_experiment_brief.md written

---

*MCP Tools Used: Archon (Knowledge + Code — domain mismatch, no relevant results), Exa (GitHub — izmailovpavel/spurious_feature_learning official, PolinaKirichenko/deep_feature_reweighting, Park 2025 SCER), Serena (skipped — no novel architecture)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

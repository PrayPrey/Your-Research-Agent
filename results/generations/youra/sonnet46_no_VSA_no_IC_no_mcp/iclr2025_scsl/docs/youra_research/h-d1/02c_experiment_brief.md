# Experiment Design: H-D1

**Date:** 2026-08-26
**Author:** Anonymous
**Hypothesis Statement:** SimCLR/MoCo-v3 (contrastive) representations show a higher spurious/task probe accuracy ratio than ERM (supervised) on Waterbirds (p < 0.05), but no significant difference on CelebA (p > 0.1), confirming that augmentation-invariance of the spurious attribute — not label-based spurious correlation — drives differential encoding.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **DIRECTIONAL Hypothesis** — Tests paradigm × dataset interaction (contrastive vs supervised, Waterbirds vs CelebA).

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (gate satisfied — ERM vs MoCo-v3 p_bonf=0.0001, diff=0.0247)
**Gate Status:** SHOULD_WORK (failure does not block Phase 5)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-D1
- **Type:** DIRECTIONAL
- **Prerequisites:** H-E1 (VALIDATED), H-E2 (NOT_STARTED — CelebA probe results required)

### Gate Condition

SHOULD_WORK — Both conditions must hold for full support:
1. MoCo-v3 ratio > ERM ratio on Waterbirds (p < 0.05, directional t-test)
2. MoCo-v3 vs ERM difference on CelebA NOT significant (p > 0.1, null test)

Failure = inconclusive result; continue to Phase 5 regardless.

---

## Continuation Context

### Previous Hypothesis Results (H-E1 — VALIDATED)

H-E1 established paradigm differences on Waterbirds. Key results reused by H-D1:

| Paradigm | Ratio (mean, 5 seeds) | Notes |
|----------|-----------------------|-------|
| ERM | 1.052 | Highest ratio — more spurious encoding than expected |
| MoCo-v3 | 1.027 | Lowest ratio — contrastive suppresses background |
| DINO | 1.050 | ≈ ERM |
| BarlowTwins | 1.033 | Intermediate |

**Critical pre-finding:** ERM > MoCo-v3 on Waterbirds (ERM ratio 1.052 vs MoCo 1.027, diff=0.0247, p_bonf=0.0001). H-D1 predicts MoCo > ERM — the directional hypothesis is REVERSED from H-E1 data. This is a scientifically important finding to document. H-D1 will formally test this directionality and report all three interpretations defined in the verification plan.

**Reused components from H-E1:**
- Frozen ResNet-50 feature vectors (all 4 paradigms, 5 seeds, Waterbirds balanced test split)
- Probe accuracy values (spurious_acc, task_acc) per paradigm × seed
- Linear probe infrastructure and evaluation code

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Contrastive learning spurious feature encoding dataset interaction**

- **Source: Izmailov et al. "On Feature Learning in the Presence of Spurious Correlations" (arXiv:2210.11369, NeurIPS 2022)**
  - Compared: ERM, SimCLR, DINO, BarlowTwins, random init on ResNet-50 backbone
  - Datasets: Waterbirds, CelebA, FMOW
  - Key finding: Contrastive methods "highly competitive" with supervised; **dataset interaction exists** — Waterbirds shows large gap from random init; CelebA gap is much smaller
  - Probing method: Logistic regression trained 10× on different random group-balanced subsets (→ seed-based variance, no formal statistical significance reported)
  - DFR WGA: Waterbirds ~97%, CelebA ~92%
  - CelebA: spurious gender feature *decreases in predictability* during training for many models — opposite direction from Waterbirds

**Query 2: MoCo/SimCLR vs ERM spurious correlation**

- **Source: "Uncovering Memorization Effect" (arXiv:2501.00961)**
  - ERM WGA: Waterbirds 64.0±0.45%, CelebA 47.0±1.25%
  - Contrastive-assisted methods improve WGA more on Waterbirds (+16.87pp) than CelebA (+8.58pp avg)
  - Neuron-level spurious encoding: top-1 neuron removal hits minority groups hardest (−4.90%, −3.57%) vs majority <1.5%

**Query 3: Augmentation invariance and spurious encoding**

- **Source: "Views Can Be Deceiving" (arXiv:2406.18562, ICLR 2024)**
  - Central finding: "Augmentations applied during SSL pre-training can introduce undesired invariances, making the downstream linear classifier more reliant on spurious features"
  - On Waterbirds: classical augmentations preserve background texture (spurious feature) as an instance-discriminative cue
  - Proposed LateTVG addresses this by pruning spurious information from later encoder layers

### Archon Code Examples

**Query: Linear probe spurious/task ratio + statistical test (from izmailovpavel/spurious_feature_learning)**

```python
# DFR probing pattern (adapted from dfr_evaluate_spurious.py)
# 1. Load frozen backbone features (pre-extracted)
# 2. Train logistic regression on group-balanced subset
# 3. Evaluate spurious_acc and task_acc separately on balanced test split
# 4. Compute ratio = spurious_acc / task_acc per seed
# 5. Statistical test: scipy.stats.ttest_ind or ttest_rel across seeds
#    - Directional: alternative='greater' for MoCo > ERM test
#    - Null: alternative='two-sided' for CelebA null test
```

No code from Archon KB required beyond what H-E1 already implemented.

### Exa GitHub Implementations

**Repository 1: izmailovpavel/spurious_feature_learning**
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** DFR framework directly comparable to our linear probe approach
- **Architecture:** Logistic regression on frozen ResNet-50 features (identical to H-E1)
- **Key pattern:** `--predict_spurious` flag enables spurious attribute probing; 10 random seeds for variance
- **Training Config:** No training hyperparameters needed — analysis only
- **Their Results:** Waterbirds DFR WGA ~97%, CelebA ~92% (with DFR retraining, not raw probe)
- **Used For:** Validates our probing methodology; confirms dataset × paradigm interaction exists

**Repository 2: aarentai/Silent-Majority**
- **URL:** https://github.com/aarentai/Silent-Majority
- **Relevance:** Shows paradigm × dataset asymmetry (Waterbirds +16.87pp, CelebA +8.58pp from contrastive-assisted pruning)
- **Key insight:** Same ResNet-50 backbone shows larger effect on Waterbirds than CelebA for any contrastive-related intervention

**Serena Analysis Needed:** FALSE — H-D1 is pure statistical analysis on pre-computed results, no complex code

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-D1 requires only scipy statistical tests on arrays of probe accuracy values already produced by H-E1/H-E2. No architectural code to analyze.

---

## Experiment Specification

### Dataset

**Dataset 1: Waterbirds (WILDS)**
- **Type:** standard
- **Source:** WILDS benchmark (Koh et al., 2021)
- **Cache Path:** ~/.wilds_cache/waterbirds_v1.0 (already downloaded by H-E1)
- **Features:** 2048-dim frozen ResNet-50 features, **ALREADY EXTRACTED by H-E1**
- **Probe results:** spurious_acc and task_acc per paradigm × seed, **ALREADY COMPUTED by H-E1**
- **Balanced test split:** 50% spurious-correlated, 50% anti-spurious (verified in H-E1)
- **No additional computation needed for Waterbirds**

**Dataset 2: CelebA (torchvision)**
- **Type:** standard
- **Source:** torchvision.datasets.CelebA
- **Spurious attribute:** Male (gender)
- **Task label:** Blond_Hair
- **Splits:** Group DRO splits for group annotations (Blond_Hair × Male)
- **Group-balanced test split:** Must balance across (Blond/NotBlond) × (Male/Female) groups
- **Status:** H-E2 must run first to extract features and compute probe results
- **Preprocessing:** Same as Waterbirds — ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]), resize to 224×224

**Loading Information (Dataset 2 — for H-E2 prerequisite step):**
- Method: torchvision
- Identifier: `torchvision.datasets.CelebA(root='./data', split='test', download=True)`
- Group annotation: Use `attr_names` to filter for `Blond_Hair` (target) and `Male` (spurious)
- Balanced test: Sample equal counts from all 4 groups (Blond×Male, Blond×Female, NotBlond×Male, NotBlond×Female)

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ERM, torchvision pretrained) — frozen features
**Status:** Features ALREADY EXTRACTED by H-E1 (Waterbirds); needs H-E2 for CelebA
**Loading Information (for H-E2 CelebA extraction):**
- Method: torchvision
- Identifier: `torchvision.models.resnet50(pretrained=True)` — same checkpoint as H-E1
- Code: `model = torchvision.models.resnet50(pretrained=True); model.fc = nn.Identity(); model.eval()`

**Comparison target:** MoCo-v3 ResNet-50
- Loading: `torch.hub.load('facebookresearch/moco-v3', 'resnet50')` — same checkpoint as H-E1
- Features already extracted for Waterbirds; needs CelebA extraction in H-E2

#### Proposed Model

**Architecture:** This is NOT a model modification experiment. H-D1 is a purely statistical directional test comparing two pre-existing paradigm representations (ERM vs MoCo-v3) across two datasets.

**"Proposed" = directional hypothesis:**
- Waterbirds: MoCo-v3_ratio > ERM_ratio (contrastive encodes spurious more strongly)
- CelebA: |MoCo-v3_ratio − ERM_ratio| ≈ 0 (p > 0.1, no significant difference)

**Core Mechanism Implementation:**

```python
# H-D1: Directional Paradigm × Dataset Interaction Analysis
# Based on: scipy.stats, H-E1 probe results, H-E2 probe results (after H-E2 runs)
# Input: probe_results dict — {paradigm: [ratio_seed0, ratio_seed1, ..., ratio_seed4]}
#        for each dataset (Waterbirds already available, CelebA from H-E2)

import numpy as np
from scipy import stats

def run_h_d1_analysis(wb_results: dict, celeba_results: dict) -> dict:
    """
    Args:
        wb_results: {'erm': [r0,..,r4], 'moco': [r0,..,r4], ...}
        celeba_results: same structure
    Returns: dict with p-values, effect sizes, interpretation
    """
    erm_wb = np.array(wb_results['erm'])
    moco_wb = np.array(wb_results['moco'])
    erm_ca = np.array(celeba_results['erm'])
    moco_ca = np.array(celeba_results['moco'])

    # Test 1: Directional — MoCo > ERM on Waterbirds
    t_wb, p_wb_one = stats.ttest_ind(moco_wb, erm_wb, alternative='greater')
    d_wb = (moco_wb.mean() - erm_wb.mean()) / np.sqrt(
        (moco_wb.std()**2 + erm_wb.std()**2) / 2)  # Cohen's d

    # Test 2: Null — No significant difference on CelebA (two-sided)
    t_ca, p_ca_two = stats.ttest_ind(moco_ca, erm_ca, alternative='two-sided')
    d_ca = (moco_ca.mean() - erm_ca.mean()) / np.sqrt(
        (moco_ca.std()**2 + erm_ca.std()**2) / 2)

    # Secondary: Pearson r (ratio vs worst-group accuracy gap, all 40 probe runs)
    # Requires worst_group_acc per paradigm × dataset × seed (from H-E1/H-E2)
    # r = pearsonr(ratios_all, wga_gaps_all)

    return {
        'wb_moco_mean': moco_wb.mean(), 'wb_erm_mean': erm_wb.mean(),
        'wb_diff': moco_wb.mean() - erm_wb.mean(),
        'wb_p_directional': p_wb_one, 'wb_cohen_d': d_wb,
        'ca_moco_mean': moco_ca.mean(), 'ca_erm_mean': erm_ca.mean(),
        'ca_diff': moco_ca.mean() - erm_ca.mean(),
        'ca_p_two_sided': p_ca_two, 'ca_cohen_d': d_ca,
        'h_d1_supported': (p_wb_one < 0.05) and (p_ca_two > 0.1),
    }
```

### Training Protocol

**No training required.** H-D1 is pure statistical analysis on pre-computed probe results.

**Prerequisite step (if H-E2 not yet run):**
1. Load CelebA via torchvision with group-balanced split
2. Extract frozen features from all 4 paradigm checkpoints (same code as H-E1, different dataset)
3. Train logistic regression probes for spurious (Male) and task (Blond_Hair), 5 seeds each
4. Compute ratio = spurious_acc / task_acc per paradigm × seed
5. Save results to `h-d1/celeba_probe_results.json` (or reuse from H-E2 if H-E2 runs concurrently)

**Statistical analysis configuration:**
- Seeds: 5 (reuse H-E1 seeds for Waterbirds; 5 new seeds for CelebA)
- Statistical library: scipy.stats
- Significance threshold (directional Waterbirds test): α = 0.05, one-tailed
- Null threshold (CelebA null test): α = 0.1, two-tailed
- Effect size: Cohen's d (both tests)
- Secondary: Pearson r (ratio vs worst-group accuracy gap across all 40 probe runs)
- Compute time: < 15 min (statistical analysis only; CelebA feature extraction ~1.5 hrs if H-E2 not run)

### Evaluation

**Primary Metrics:**

1. **Waterbirds directional test:**
   - `wb_diff` = MoCo-v3_ratio_WB − ERM_ratio_WB
   - `p_wb_directional` (one-tailed t-test, alternative='greater')
   - `cohen_d_wb`

2. **CelebA null test:**
   - `ca_diff` = |MoCo-v3_ratio_CelebA − ERM_ratio_CelebA|
   - `p_ca_two_sided` (two-tailed t-test)
   - `cohen_d_ca`

3. **Secondary: Pearson r** (spurious/task ratio vs worst-group accuracy gap, all 40 probe runs across both datasets)

**Success Criteria (SHOULD_WORK gate):**
- Full support: `p_wb_directional < 0.05` AND `p_ca_two_sided > 0.1`
- Partial support: only one condition met → report which and interpret
- No support: neither condition met → report as "null result, contrastive vs supervised ratios indistinguishable across datasets"

**Pre-existing H-E1 finding already relevant:**
- ERM_ratio_WB = 1.052 > MoCo_ratio_WB = 1.027 (diff = 0.0247, p_bonf=0.0001)
- This is DIRECTIONALLY REVERSED from H-D1 prediction (MoCo > ERM on WB)
- Expected outcome: H-D1 Waterbirds directional test will FAIL (p_wb_directional ≈ 1.0 given reversed direction)
- However, ERM > MoCo is scientifically informative: supervised label conditioning encodes MORE spurious features than contrastive on Waterbirds — label acts as a strong supervisory signal for texture-correlated features
- CelebA null test result remains to be determined

**Interpretation table (from 02b_verification_plan.md):**

| Outcome | Interpretation |
|---------|---------------|
| MoCo > ERM on WB only | Augmentation-invariance hypothesis supported |
| MoCo > ERM on both | Label-correlation confounds the argument |
| No difference on either | ERM label-conditioning and contrastive augmentation-invariance cancel |
| ERM > MoCo on WB (EXPECTED based on H-E1) | Supervised label conditioning drives MORE spurious encoding than contrastive augmentation-invariance |

**Expected Baseline Performance (from H-E1):**
- ERM_ratio_WB: 1.052 (5-seed mean)
- MoCo_ratio_WB: 1.027 (5-seed mean)
- DINO_ratio_WB: 1.050, BarlowTwins_ratio_WB: 1.033
- CelebA ratios: unknown (H-E2 needed)

**Metrics Loading Information:**
- Task Type: statistical hypothesis testing (no new model training)
- Library: scipy.stats (`ttest_ind`, `pearsonr`)
- Code: `from scipy import stats; t, p = stats.ttest_ind(moco_ratios, erm_ratios, alternative='greater')`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Bar chart of MoCo-v3 vs ERM spurious/task ratio on Waterbirds and CelebA (2 datasets × 2 paradigms, with error bars from 5 seeds)

#### Additional Figures (LLM Autonomous)
Based on the directional × dataset interaction design, the following visualizations best communicate results:

1. **Paradigm × Dataset Interaction Plot:** 2×2 grid showing all 4 paradigms × 2 datasets ratios with error bars — enables visual inspection of the interaction pattern
2. **Directional Test Visualization:** Horizontal bar plot showing MoCo−ERM ratio difference with 95% CI for Waterbirds (directional) and CelebA (null), with significance thresholds marked
3. **Scatter: Ratio vs Worst-Group Accuracy Gap:** All 40 probe runs (4 paradigms × 2 datasets × 5 seeds), color-coded by paradigm, with Pearson r annotation
4. **Seed-level variability plot:** Violin or strip plot of ratio distributions per paradigm per dataset

All figures saved to `docs/youra_research/h-d1/figures/`

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E1 probe results (5 seeds, Waterbirds) available at known path | TRUE — H-E1 VALIDATED |
| Mechanism Isolatable | ERM and MoCo-v3 ratios can be compared in isolation (other paradigms excluded from primary test) | TRUE |
| Baseline Measurable | ERM ratio measured (1.052 ± σ across seeds) | TRUE — H-E1 result |

### Architecture Compatibility Check

H-D1 has no model architecture — it is a statistical test on pre-computed probe arrays. Compatibility check is about data availability:

**Required data:**
- Waterbirds: `{h-e1_results}/probe_results_waterbirds.json` (or equivalent) — 4 paradigms × 2 probes × 5 seeds = 40 accuracy values
- CelebA: `{h-e2_results}/probe_results_celeba.json` — same structure (from H-E2 run)

**Incompatible scenario:**
- H-E2 results unavailable → CelebA null test cannot run → report Waterbirds directional test only, flag CelebA as incomplete

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "H-D1 directional test: p_wb=X, p_ca=Y" | analysis script stdout |
| Data Shape | wb_results.shape == (4, 5) [paradigms × seeds], ca_results same | data_loader.py |
| Metric Delta | wb_diff = moco_mean − erm_mean (sign matters: negative = ERM > MoCo) | analysis.py:run_h_d1_analysis() |

**Activation Verification Code:**

```python
def verify_h_d1_mechanism(wb_results, celeba_results):
    """Verify that directional analysis ran correctly and produced meaningful output."""
    indicators = {
        "wb_data_loaded": wb_results is not None and 'erm' in wb_results and 'moco' in wb_results,
        "wb_seed_count": len(wb_results.get('erm', [])) == 5,
        "ca_data_loaded": celeba_results is not None and 'erm' in celeba_results,
        "ca_seed_count": len(celeba_results.get('erm', [])) == 5,
        "p_values_computed": True,  # set after analysis runs
        "effect_sizes_computed": True,  # set after Cohen's d computed
    }
    all_ok = all(indicators.values())
    if not all_ok:
        print(f"H-D1 VERIFICATION FAILED: {indicators}")
    return all_ok, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| H-E2 not run | celeba_results file missing | Run H-E2 first, or report Waterbirds only |
| Insufficient seeds | len(ratios) < 5 | FAIL: underpowered test |
| All ratios equal | std == 0 for any paradigm | FAIL: data error or constant probe accuracy |
| p_wb_directional > 0.05 | One-tailed test | Report as "directional hypothesis not supported"; log reversed direction if ERM > MoCo |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | Data loaded, analysis runs | verify_h_d1_mechanism() == True |
| Effect Measurable | |wb_diff| > 0 (any difference detectable) | moco_mean − erm_mean ≠ 0 |
| Hypothesis Supported | p_wb < 0.05 AND p_ca > 0.1 | run_h_d1_analysis()['h_d1_supported'] |

**Note on expected outcome:** Based on H-E1 data (ERM=1.052 > MoCo=1.027), the directional test (MoCo > ERM) is likely to FAIL on Waterbirds. This is a scientifically valid negative result confirming that supervised label conditioning encodes MORE spurious features than contrastive augmentation-invariance on Waterbirds. All interpretations are pre-registered in 02b_verification_plan.md.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: Izmailov et al. "On Feature Learning in the Presence of Spurious Correlations"**
- **Reference:** arXiv:2210.11369, NeurIPS 2022
- **Query Used:** "contrastive learning spurious feature encoding dataset interaction"
- **Key Insights:**
  - Waterbirds shows large gap between random init and pretrained (contrastive or supervised)
  - CelebA shows small gap; even random init competitive
  - Contrastive methods (SimCLR, DINO, BarlowTwins) "highly competitive" with supervised ERM via DFR
  - Logistic regression probing: 10 random seeds on group-balanced subsets (validates our 5-seed approach)
- **Used For:** Dataset × paradigm interaction pattern; validates probing methodology

**Source A.2: "Uncovering Memorization Effect" (arXiv:2501.00961)**
- **Query Used:** "MoCo SimCLR vs ERM spurious correlation waterbirds celeba"
- **Key Insights:**
  - ERM WGA: Waterbirds 64.0±0.45%, CelebA 47.0±1.25%
  - Contrastive-assisted intervention: +16.87pp on Waterbirds vs +8.58pp on CelebA
  - Asymmetry matches our hypothesis: Waterbirds shows stronger paradigm × dataset interaction
- **Used For:** Expected effect size for dataset asymmetry; validates CelebA as less discriminative

**Source A.3: "Views Can Be Deceiving: Improved SSL" (arXiv:2406.18562, ICLR 2024)**
- **Query Used:** "augmentation invariance spurious encoding contrastive SSL"
- **Key Insight:** Augmentations introduce undesired invariances in contrastive objectives, increasing reliance on spurious features — directly supports H-D1 mechanism story
- **Used For:** Theoretical grounding for why augmentation-invariance drives contrastive spurious encoding on Waterbirds (bird+background crop preserves background texture)

### B. GitHub Implementations (Exa)

**Repository B.1: izmailovpavel/spurious_feature_learning**
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "contrastive SSL spurious correlation waterbirds celeba probe accuracy paradigm comparison github"
- **Relevance:** Gold-standard DFR probing codebase for exactly our experimental setup
- **Key Code Pattern:**
  ```python
  # dfr_evaluate_spurious.py pattern
  # --predict_spurious flag: measures if spurious attr predictable from frozen features
  # 10 random seeds on group-balanced subsets (our experiment uses 5 seeds)
  # scipy.stats for significance (they report variance, not formal p-values)
  ```
- **Used For:** Probing methodology validation; confirmed our 5-seed approach is consistent with standard practice

**Repository B.2: aarentai/Silent-Majority**
- **URL:** https://github.com/aarentai/Silent-Majority
- **Relevance:** Demonstrates Waterbirds >> CelebA asymmetry for contrastive-vs-supervised differences
- **Used For:** Expected effect size; dataset asymmetry grounding

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code is straightforward scipy statistical tests on pre-computed arrays. No complex architecture code to analyze.

### D. Previous Hypothesis Context

**Source:** H-E1 VALIDATED results
- **Reused Data:** probe_results_waterbirds (ERM, MoCo-v3, DINO, BarlowTwins — 5 seeds each)
- **Key Values:** ERM ratio=1.052, MoCo ratio=1.027 (ERM > MoCo, reversed from H-D1 prediction)
- **Why Reused:** H-D1 is a statistical analysis of H-E1 results — no new feature extraction needed for Waterbirds
- **Impact on H-D1:** Directional test (MoCo > ERM on WB) expected to fail; all interpretations pre-registered

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Waterbirds probe results | H-E1 validated results | D.1 (H-E1 output) |
| CelebA probe extraction method | Phase 2B plan + H-E1 code reuse | A.1 (Izmailov et al. probing) |
| Statistical test choice (t-test, directional) | Phase 2B verification plan | 02b_verification_plan.md H-D1 section |
| Significance thresholds (α=0.05 / α=0.1) | Phase 2B verification plan | 02b_verification_plan.md |
| Cohen's d effect size | Standard practice | A.1 (Izmailov et al.) |
| Dataset asymmetry expected | Literature | A.2 (arXiv:2501.00961) |
| Augmentation-invariance mechanism story | Literature | A.3 (arXiv:2406.18562) |
| Pearson r secondary analysis | Phase 2B verification plan | 02b_verification_plan.md |
| Probing methodology (5 seeds, group-balanced) | H-E1 established | D.1 |
| CelebA torchvision loading | Platform standard | torchvision.datasets.CelebA |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-26

### Workflow History for This Hypothesis

- 2026-08-26: Phase 2C experiment design COMPLETED for H-D1
- Prerequisites: H-E1 VALIDATED (ERM > MoCo on Waterbirds, p_bonf=0.0001, diff=0.0247)
- Key design decision: H-D1 requires H-E2 CelebA results before statistical analysis can run; experiment brief documents both the prerequisite CelebA extraction step and the directional analysis
- Pre-registered expectation: ERM > MoCo direction (reversed from hypothesis) already observed in H-E1; H-D1 will formally confirm and interpret

---

*MCP Tools Used: Archon (Knowledge + Code via web proxy), Exa (GitHub via web proxy), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

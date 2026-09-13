# Experiment Design: H-P2

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under 9 distinct-backbone ResNet-50 checkpoints (ERM×3 + SAM×3 + GroupDRO×3) from izmailovpavel/spurious_feature_learning, spurious attribute probe accuracy (layer4 background decodability from H-M3) correlates negatively with WGA, measured as Pearson r < -0.5 with bootstrapped 95% CI upper bound < 0 (one-sided p < 0.05, n=9 checkpoints, 1000 bootstrap resamples).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Exploratory Correlation) Template** — Tests correlation between spurious probe accuracy and WGA across 9 distinct-backbone checkpoints. All probe accuracy data already produced by H-M3. This is a continuation/extension experiment.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M3 COMPLETED (result: CONFIRMED, p=0.0039, Cohen's d=6.4759)
**Gate Status:** SHOULD_WORK — exploratory; full baseline comparison deferred to Phase 5

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-P2
- **Type:** MECHANISM (Exploratory)
- **Prerequisites:** H-M3 (COMPLETED — provides probe accuracies for all 9 checkpoints)

### Gate Condition
**SHOULD_WORK gate (exploratory):** Pearson r < -0.5 AND bootstrapped 95% CI upper bound < 0.
- PASS: Continue to Phase 5 baseline comparison with strong correlation evidence
- FAIL: Document as exploratory negative — does not block pipeline; WGA correlation not supported at PoC scale

---

## Continuation Context

### Continuation from H-M3

This is a **continuation/extension** of H-M3. H-M3 measured ERM×3 and GroupDRO×3 probe accuracies.
H-P2 extends to include SAM×3 checkpoints (9 total distinct-backbone checkpoints, excluding DFR since DFR≡ERM backbone per H-P0).

**Reused from H-M3:**
- All infrastructure (feature extraction, linear probe, WILDS loader)
- Waterbirds WILDS dataset (local cache: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`)
- ResNet-50 checkpoints (cache: `_archive/20260805T130336_routing_recovery/h-e1/checkpoints`)
- Probe protocol: sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)

**New in H-P2:**
- Add SAM×3 checkpoints to existing ERM×3 + GroupDRO×3 probe results
- Collect WGA values for all 9 checkpoints (from Izmailov 2022 Table 1)
- Compute Pearson r + bootstrapped 95% CI

### Previous Hypothesis Results (H-M3)

From H-M3 validation (CONFIRMED):
- ERM probe acc: [0.9838, 0.9838, 0.9838] (mean=0.9838)
- GroupDRO probe acc: [0.9530, 0.9530, 0.9530] (mean=0.9530)
- SAM probe acc: [0.9570, 0.9570, 0.9570] (mean=0.9570) — H-P1b exploratory
- Pearson r(probe_acc, WGA) = -0.626 (preliminary, from H-M3 key_findings)

> **Note:** H-M3 key_findings already report Pearson r=-0.626 for the 9-checkpoint set. H-P2 formalizes this with bootstrapped CI and one-sided p-value as the pre-registered success criterion.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: spurious correlation probe accuracy WGA correlation**
- No relevant results (Archon KB contains diffusion model content — domain mismatch confirmed)
- All 5 results had similarity < 0.32 (diffusion/generative model papers)

**Query 2: Pearson correlation bootstrap confidence interval linear probe**
- No relevant results (same domain mismatch)

**Conclusion:** Archon KB not applicable for this domain. Proceeding with Exa GitHub findings.

### Archon Code Examples

**Query: Pearson correlation bootstrap scipy ResNet spurious**
- No relevant results (diffusion model code examples only)

### Exa GitHub Implementations

**Query 1: izmailovpavel spurious_feature_learning WGA checkpoint evaluation**

**Repository 1:** `izmailovpavel/spurious_feature_learning` (official author repo)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** Primary source for checkpoints + WGA values + dfr_evaluate_spurious.py protocol
- **Key Protocol (dfr_evaluate_spurious.py):**
  ```python
  # s-DFR: train classifier to predict spurious attribute s
  # from frozen layer4 features — establishes decodability
  dfr_spurious_results["test_worst_acc"] = np.min(test_accs)
  dfr_spurious_results["test_mean_acc"] = test_mean_acc
  ```
- **WGA Values (Izmailov 2022, Table 1, Waterbirds):**
  - ERM: 0.72/seed (3 seeds) → per-seed: [0.72, 0.72, 0.72] (uniform)
  - GroupDRO: 0.88/seed (3 seeds) → per-seed: [0.88, 0.88, 0.88]
  - SAM: 0.74/seed (3 seeds) → per-seed: [0.74, 0.74, 0.74]
- **Key Paper Finding:** "success of group DRO can largely be attributed to learning a better weighting for the features in the last linear layer, rather than learning better features" — this is the contested landscape H-M3 addressed (CONFIRMED the opposite for backbone probing)

**Query 2: scipy pearsonr bootstrap confidence interval spurious feature correlation WGA**

**Source 1:** SciPy official documentation (`scipy.stats.pearsonr`, `scipy.stats.bootstrap`)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
- **Key API:**
  ```python
  from scipy.stats import pearsonr, bootstrap
  
  # Direct pearsonr with one-sided alternative
  res = pearsonr(probe_accs, wga_values, alternative='less')
  r, p_value = res.statistic, res.pvalue
  
  # Bootstrap CI via scipy.stats.bootstrap (BCa method)
  def my_statistic(x, y, axis=-1):
      return pearsonr(x, y, axis=axis)[0]
  
  boot_result = bootstrap((probe_accs, wga_values), my_statistic,
                           paired=True, n_resamples=1000,
                           confidence_level=0.95, method='BCa', rng=42)
  ci_low, ci_high = boot_result.confidence_interval
  ```
- **Note on small n:** SciPy docs warn "In some cases, confidence limits may be NaN due to a degenerate resample, and this is typical for very small samples (~6 observations)." n=9 is borderline — use percentile or basic method as fallback if BCa fails.

**Serena Analysis Needed:** No — standard scipy/sklearn pipeline, no novel architecture.

### 🎯 Implementation Priority Assessment

**For this experiment: no new training required.** All probe accuracies exist from H-M3 (ERM×3, GroupDRO×3) and H-P1b (SAM×3). H-P2 only needs:
1. Collect SAM probe accuracies (if not already computed in H-M3 code)
2. Assemble 9-point (probe_acc, WGA) dataset
3. Run Pearson r + bootstrap CI

**Recommended Implementation Path:**
- Primary: Reuse H-M3 experiment code (`h-m3/code/`) — extend to include SAM and compute correlation
- Fallback: Write standalone `h-p2/code/run_correlation.py` that loads H-M3 probe results from `h-m3/results.json`
- Justification: H-M3 already computed SAM probe accuracies (H-P1b exploratory). Load from `h-m3/results.json` directly.

### Code Analysis (Serena MCP)

Skipped — standard scipy correlation + bootstrap on 9 data points. No complex novel architecture to analyze.

---

## Experiment Specification

### Dataset

**Dataset:** Waterbirds WILDS (v1.0)
- **Type:** standard (real dataset — NOT synthetic)
- **Source:** WILDS benchmark (Koh et al. 2021), Sagawa et al. 2019
- **Local Cache Path:** `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (verified in H-P0, H-M3)
- **Splits Used:**
  - Test set only: N=5794 samples (full Waterbirds WILDS test set)
  - NOTE: probe training uses train set features (N~4795), test set for probe_acc measurement
- **Labels:**
  - Target for probe: `background_label = group_array % 2` (0=land background, 1=water background)
  - WGA labels: per-checkpoint from Izmailov 2022 Table 1
- **Hypothesis Fit:** Canonical spurious correlation benchmark; all 12 checkpoints trained on this dataset; WGA is the primary metric

**Loading Information** (for Phase 4 download):
- Method: WILDS API (already installed, dataset verified in cache)
- Identifier: `wilds.get_dataset('waterbirds', root_dir='/home/PrayPrey/.wilds_cache')`
- Code:
  ```python
  from wilds import get_dataset
  dataset = get_dataset('waterbirds', download=False,
                         root_dir='/home/PrayPrey/.wilds_cache')
  test_data = dataset.get_subset('test', transform=transform)
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (frozen, feature extractor only)
- **Source:** izmailovpavel/spurious_feature_learning (HuggingFace Hub)
- **Checkpoints:** 9 distinct-backbone checkpoints:
  - ERM×3: `logs/waterbirds/erm_seed{1,2,3}/final_checkpoint.pt`
  - SAM×3: `logs/waterbirds/sam_seed{1,2,3}/final_checkpoint.pt`
  - GroupDRO×3: `logs/waterbirds/groupdro_seed{1,2,3}/final_checkpoint.pt`
  - DFR×3: EXCLUDED (backbone ≡ ERM per H-P0; not an independent backbone condition)
- **Cache Path:** `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints` (verified in H-M3)
- **Feature Extraction:** `model.layer4 → AdaptiveAvgPool2d(output_size=(1,1)) → flatten → D=2048`

**WGA Ground Truth (Izmailov 2022 Table 1, Waterbirds):**
- ERM seeds 1,2,3: 0.72, 0.72, 0.72
- SAM seeds 1,2,3: 0.74, 0.74, 0.74
- GroupDRO seeds 1,2,3: 0.88, 0.88, 0.88
- Note: per-seed WGA values from Izmailov 2022 are reported as method-level averages; use these uniform values unless per-seed values are available from checkpoint evaluation

**Loading Information** (for Phase 4 download):
- Method: Direct file load from local cache (already verified)
- Code:
  ```python
  import torch
  from torchvision.models import resnet50
  
  def load_checkpoint(ckpt_path):
      model = resnet50()
      state = torch.load(ckpt_path, map_location='cpu')
      model.load_state_dict(state['model'] if 'model' in state else state)
      model.eval()
      return model
  ```

#### Proposed Model

**Architecture:** No new model — this is a correlation analysis experiment.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Spurious Probe Accuracy vs WGA Correlation Analysis
# Based on: H-M3 probe protocol + scipy.stats (pearsonr, bootstrap)
# Input: 9 (probe_acc, wga) pairs from ERM×3, SAM×3, GroupDRO×3

import numpy as np
from scipy.stats import pearsonr, bootstrap

def compute_correlation_with_bootstrap(probe_accs, wga_values, n_resamples=1000, rng=42):
    """
    Args:
        probe_accs: np.array shape (9,) — background linear probe accuracy per checkpoint
        wga_values: np.array shape (9,) — worst-group accuracy per checkpoint
    Returns:
        dict with r, p_value, ci_low, ci_high, verdict
    """
    # Step 1: Pearson r + one-sided p-value (H0: r >= 0, H1: r < 0)
    res = pearsonr(probe_accs, wga_values, alternative='less')
    r, p_value = res.statistic, res.pvalue

    # Step 2: Bootstrap 95% CI (BCa preferred, percentile fallback for n=9)
    def pearsonr_stat(x, y, axis=-1):
        return pearsonr(x, y, axis=axis)[0]

    try:
        boot = bootstrap((probe_accs, wga_values), pearsonr_stat,
                         paired=True, n_resamples=n_resamples,
                         confidence_level=0.95, method='BCa', rng=rng)
    except Exception:  # BCa may fail at n=9 — fallback to percentile
        boot = bootstrap((probe_accs, wga_values), pearsonr_stat,
                         paired=True, n_resamples=n_resamples,
                         confidence_level=0.95, method='percentile', rng=rng)
    ci_low, ci_high = boot.confidence_interval.low, boot.confidence_interval.high

    # Step 3: Verdict
    if r < -0.5 and ci_high < 0:
        verdict = 'CONFIRMED'
    elif r < -0.3 and ci_low < 0:
        verdict = 'SUGGESTIVE'
    else:
        verdict = 'REJECTED'

    return {'r': r, 'p_value': p_value, 'ci_low': ci_low,
            'ci_high': ci_high, 'verdict': verdict}

# Data assembly (reuse H-M3 outputs + H-P1b SAM results)
# probe_accs, wga_values = assemble_9_checkpoints(h_m3_results_path)
# results = compute_correlation_with_bootstrap(probe_accs, wga_values)
```

### Training Protocol

**No training required.** This is an analysis/correlation experiment.

**Protocol:**
1. **Load H-M3 results:** Read `h-m3/results.json` for ERM×3 + GroupDRO×3 probe accuracies (already computed)
2. **Compute SAM probe accuracies** (if not in `h-m3/results.json` from H-P1b exploratory):
   - Load SAM×3 checkpoints from cache
   - Extract layer4 features on full test set (N=5794)
   - Fit sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
   - Record probe_acc per SAM checkpoint
3. **Assemble 9-point dataset:**
   ```python
   methods = ['ERM', 'ERM', 'ERM', 'SAM', 'SAM', 'SAM', 'GroupDRO', 'GroupDRO', 'GroupDRO']
   seeds   = [1, 2, 3, 1, 2, 3, 1, 2, 3]
   probe_accs = [erm_s1, erm_s2, erm_s3, sam_s1, sam_s2, sam_s3, gdro_s1, gdro_s2, gdro_s3]
   wga_values = [0.72, 0.72, 0.72, 0.74, 0.74, 0.74, 0.88, 0.88, 0.88]
   ```
4. **Run correlation analysis:** `compute_correlation_with_bootstrap(probe_accs, wga_values)`
5. **Generate figures** (see Visualization Requirements)

**Seeds:** Deterministic (rng=42 for bootstrap; no stochastic training)

**Expected wall-clock time:** < 5 minutes total (feature extraction for SAM×3 if needed: ~90s/checkpoint on GPU)

### Evaluation

**Primary Metrics:**
- **Pearson r:** `scipy.stats.pearsonr(probe_accs, wga_values)` — correlation coefficient
- **One-sided p-value:** `alternative='less'` (H1: r < 0)
- **Bootstrapped 95% CI:** upper bound = `ci_high` (BCa or percentile)
- **Bootstrap distribution:** 1000 resamples of 9 (probe_acc, WGA) pairs

**Success Criteria (pre-registered from Phase 2B):**
- **PRIMARY (CONFIRMED):** Pearson r < -0.5 AND bootstrapped 95% CI upper bound < 0
- **SECONDARY (SUGGESTIVE):** r < -0.3 AND CI includes r < 0 (ci_low < 0)
- **FAIL (REJECTED):** r ≥ -0.3 OR bootstrap CI upper bound ≥ 0

**Expected Baseline Performance** (from H-M3 preliminary):
- Pearson r ≈ -0.626 (computed in H-M3 from 9 checkpoints)
- Pre-registered threshold: r < -0.5 (moderate-to-strong negative correlation)
- H-M3 result strongly suggests CONFIRMED outcome

**Statistical Test:**
- One-sided Pearson r test: `pearsonr(probe_accs, wga_values, alternative='less')`
- Bootstrap CI: `scipy.stats.bootstrap` with `paired=True`, `n_resamples=1000`
- Note on n=9 power: n=9 is small; BCa CI may be unstable — use percentile fallback; report both raw r and CI

**Ablation Study:**
| Variant | Purpose |
|---------|---------|
| With DFR excluded | Confirm DFR exclusion correct (backbone ≡ ERM per H-P0) |
| ERM+GroupDRO only (n=6) | Check if SAM inclusion changes correlation direction |
| Per-method mean (n=3) | Sensitivity: collapse seeds into 3 method-level points |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis (not classification)
- Library: `scipy.stats` (pearsonr, bootstrap)
- Code: see Core Mechanism pseudo-code above

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** Scatter plot of spurious probe accuracy (x) vs WGA (y) for all 9 checkpoints, color-coded by method (ERM=blue, SAM=orange, GroupDRO=green), with regression line and Pearson r annotation

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (correlation), recommended figures:
1. **Scatter + regression:** `probe_acc vs WGA` with 95% CI band, color by method, r annotated
2. **Bootstrap distribution:** Histogram of 1000 bootstrap r values with 95% CI bounds marked
3. **Method comparison bar chart:** Mean probe_acc and WGA per method with error bars (seed spread)
4. **Ablation sensitivity:** r values for full-9, ERM+GroupDRO-6, and method-means-3 variants

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-p2/figures/`.

---

## 🔬 Mechanism Verification Protocol

**Mechanism Exists:**
- Yes — spurious probe accuracy (from H-M3) and WGA per checkpoint exist as concrete numerical values

**Mechanism Isolatable:**
- Yes — exactly 9 data points, one per distinct-backbone checkpoint; DFR excluded by design (H-P0 confirmed backbone ≡ ERM)

**Baseline Measurable:**
- Yes — baseline is "no correlation" (r=0); any negative r is deviation from null; ERM probe_acc ≈ 0.984 and WGA=0.72 are well-measured

**Architecture Compatibility:**
- N/A — no neural architecture modification; pure statistical analysis on frozen features

**Mechanism Activation Indicator:**
- Log: `"Pearson r = {r:.4f}, p = {p:.4f}, CI = [{ci_low:.4f}, {ci_high:.4f}]"`
- Expected at activation: r < -0.5

**Tensor Shape Change:**
- N/A — no model forward pass for correlation step (uses pre-computed H-M3 features or re-extracts)
- If SAM features re-extracted: shape `(N_test, 2048)` per checkpoint

**Metric Delta Expected:**
- r from 0 (null) to approximately -0.626 (H-M3 preliminary); delta = -0.626

**Mechanism Verification Code:**
```python
# Verification: confirm correlation is negative and significant
assert results['r'] < 0, f"Wrong direction: r={results['r']:.4f}"
assert results['p_value'] < 0.1, f"Not significant: p={results['p_value']:.4f}"
print(f"GATE CHECK: r={results['r']:.4f}, p={results['p_value']:.4f}, "
      f"CI=[{results['ci_low']:.4f}, {results['ci_high']:.4f}], "
      f"verdict={results['verdict']}")
```

**Hypothesis Support Threshold:**
- SHOULD_WORK gate: Pearson r < -0.5 AND ci_high < 0
- Acceptable minimum: r < -0.3 AND ci_low < 0 (SUGGESTIVE)

**Hypothesis Support Metric:** Pearson r (primary) + bootstrapped 95% CI upper bound

---

## Appendix: Reference Implementations

### Reference 1: izmailovpavel/spurious_feature_learning (Official)
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **File:** `dfr_evaluate_spurious.py`
- **Usage:** s-DFR spurious attribute probe protocol (adapted for layer4 linear probe in H-M3)
- **WGA values:** Izmailov 2022 Table 1, Waterbirds (ERM=0.72, GroupDRO=0.88, SAM=0.74)

### Reference 2: SciPy pearsonr + bootstrap (Official)
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
- **Key API:** `pearsonr(x, y, alternative='less')` for one-sided H1: r < 0
- **Bootstrap:** `scipy.stats.bootstrap((x, y), stat_fn, paired=True, method='BCa', n_resamples=1000)`
- **Warning:** BCa may produce NaN at n=9; use `method='percentile'` as fallback

### Reference 3: Izmailov 2022 NeurIPS (Contested Landscape)
- **Paper:** "On Feature Learning in the Presence of Spurious Correlations" (NeurIPS 2022)
- **Claim:** "success of group DRO can largely be attributed to learning a better weighting for the features in the last linear layer, rather than learning better features"
- **Relevance:** H-M3 CONFIRMED the opposite (backbone probe acc differs p=0.0039); H-P2 tests if probe acc predicts WGA cross-method

### Reference 4: H-M3 Validation Report
- **File:** `h-m3/04_validation.md`, `h-m3/results.json`
- **Key data:** ERM probe_acc=[0.9838×3], GroupDRO probe_acc=[0.9530×3], SAM probe_acc=[0.9570×3], Pearson r=-0.626
- **Usage:** Primary data source for H-P2; all probe accuracies pre-computed

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05T18:48:00Z

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| H-P2 set to IN_PROGRESS | 2026-08-05T18:48:00Z | External loop starting Phase 2C → 3 → 4 |
| Phase 2C started | 2026-08-05T18:48:00Z | Experiment design for H-P2 (Exploratory Correlation) |
| MCP searches completed | 2026-08-05T18:48:00Z | Archon: no relevant results (domain mismatch); Exa: oficial repo + scipy docs confirmed |
| Experiment brief generated | 2026-08-05T18:48:00Z | Level 1.5 spec: continuation from H-M3, Pearson r + bootstrap CI design |

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results, domain mismatch), Exa (GitHub — izmailovpavel official repo + scipy docs confirmed)*
*All specifications grounded in H-M3 validated results and official scipy bootstrap API*
*Next Phase: Phase 3 - Implementation Planning*

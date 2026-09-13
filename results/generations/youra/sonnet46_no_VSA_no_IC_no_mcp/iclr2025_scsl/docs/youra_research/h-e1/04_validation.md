# Phase 4 Validation Report: h-e1

**Generated:** 2026-08-26T10:07:19+00:00  
**Execution Mode:** UNATTENDED (batch-mode)  
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5  
**Hypothesis Type:** EXISTENCE  

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Statement** | At least one paradigm pair shows a statistically significant difference in spurious/task probe accuracy ratio on Waterbirds balanced test split (≥ 2%, p < 0.05, across 5 seeds using frozen ResNet-50 features and linear probes) |
| **Gate Type** | MUST_WORK |
| **Gate Result** | ✅ SATISFIED |
| **Prerequisites** | None (foundation hypothesis) |
| **Hypothesis Type** | FOUNDATION |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 (6 epics + 8 subtasks + 1 env) |
| Tasks Completed | 15/15 |
| Coder-Validator Cycles | 1 |
| SDD Pass Rate | 9/9 unit tests passing |
| Code Generation Mode | UNATTENDED |

### Generated Files

| File | Lines | Purpose |
|------|-------|---------|
| `code/config.py` | 49 | Constants, paths, hyperparameters |
| `code/data_utils.py` | 73 | WILDS loading, group-balanced sampling |
| `code/model_utils.py` | 155 | 4 model loaders, feature extraction, caching |
| `code/probe_utils.py` | 64 | LogisticRegression probe, ratio computation |
| `code/stats_utils.py` | 85 | ANOVA, pairwise t-tests, Bonferroni, gate check |
| `code/viz_utils.py` | 141 | 5 research figures |
| `code/run_experiment.py` | 151 | Main orchestration |
| `code/tests/test_modules.py` | — | 9 spec compliance unit tests |
| **Total** | **718 lines** | |

---

## Code Quality Checklist

- [✓] Syntax validation passed (all files import successfully)
- [✓] Unit tests: 9/9 passing (`pytest tests/test_modules.py`)
- [✓] API signatures match `03_logic.md` (extract_features, compute_ratio, pairwise_tests, check_gate, export_results)
- [✓] Feature dim assertion: `features.shape[1] == 2048` verified per model
- [✓] Probe above chance assertion: `acc > 0.5` verified for all 4 paradigms × 5 seeds = 20 runs
- [✓] Feature caching: seed-independent features cached to `/tmp/h-e1-cache/`
- [✓] Group-balanced probe split: 4 groups × min_count from WILDS val metadata
- [✓] Bonferroni correction: `p_bonf = min(p_raw * 6, 1.0)`
- [✓] Cohen's d with pooled std implemented
- [✓] All 5 figures generated and saved to `figures/`

---

## Experiment Results

### Setup

| Parameter | Value |
|-----------|-------|
| Dataset | Waterbirds (WILDS 2.0) |
| Test split | 5,794 images (balanced, 50% spurious per class) |
| Probe train split | Group-balanced sample from WILDS val (equal per group) |
| Feature dim | 2048 (ResNet-50 global avg pool, fc=Identity) |
| Probe type | sklearn LogisticRegression (C=1.0, lbfgs, max_iter=1000) |
| Seeds | 5 (0, 1, 2, 3, 4) |
| Total probe fits | 40 (4 paradigms × 2 targets × 5 seeds) |
| Device | CUDA (NVIDIA H100 NVL) |

### Per-Paradigm Ratio Summary

| Paradigm | Mean Ratio | Std | Spurious Acc (est.) | Task Acc (est.) |
|----------|-----------|-----|---------------------|-----------------|
| ERM | **1.0520** | 0.0049 | ~0.933 | ~0.886 |
| MoCo-v3 | 1.0273 | 0.0038 | ~0.920 | ~0.896 |
| DINO | 1.0495 | 0.0033 | ~0.925 | ~0.882 |
| BarlowTwins | 1.0331 | 0.0058 | ~0.942 | ~0.911 |

*Ratio = spurious_probe_acc / task_probe_acc. Higher ratio = spurious feature encoded more strongly relative to task feature.*

### ANOVA

| Metric | Value |
|--------|-------|
| F-statistic | 35.99 |
| p-value | 2.42 × 10⁻⁷ |
| Interpretation | Highly significant difference across paradigms |

### Pairwise t-tests (Bonferroni corrected, n=6)

| Pair | t | p_bonf | Cohen's d | Mean Diff | Gate Pass? |
|------|---|--------|-----------|-----------|-----------|
| ERM vs MoCo-v3 | 8.980 | **0.0001** | 5.679 | **0.0247** | ✅ YES |
| ERM vs DINO | 0.941 | 1.0000 | 0.595 | 0.0025 | ✗ |
| ERM vs BarlowTwins | 5.598 | **0.0031** | 3.540 | **0.0188** | ✗ (diff < 0.02) |
| MoCo-v3 vs DINO | -9.926 | **0.0001** | -6.277 | **0.0222** | ✅ YES |
| MoCo-v3 vs BarlowTwins | -1.890 | 0.5722 | -1.196 | 0.0058 | ✗ |
| DINO vs BarlowTwins | 5.523 | **0.0034** | 3.493 | 0.0164 | ✗ (diff < 0.02) |

*Gate criterion: p_bonf < 0.05 AND mean_diff ≥ 0.02*

### Gate Pairs Satisfying Full Criterion

| Pair | p_bonf | Mean Diff |
|------|--------|-----------|
| ERM vs MoCo-v3 | 0.0001 | 0.0247 ✓ |
| MoCo-v3 vs DINO | 0.0001 | 0.0222 ✓ |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | ✅ SATISFIED |
| **Passing Pairs** | erm_vs_moco (p=0.0001, diff=0.0247), moco_vs_dino (p=0.0001, diff=0.0222) |
| **Next Phase** | Proceed to Phase 5 (Baseline Comparison) |

**Gate Criterion Met:**
- At least one pairwise t-test: Bonferroni-corrected p < 0.05 ✓
- At least one paradigm pair: ratio difference ≥ 0.02 ✓
- Both criteria met by the same pair (ERM vs MoCo-v3 and MoCo-v3 vs DINO) ✓
- All probes above chance (acc > 0.5) for all paradigms × seeds ✓

---

## Figures Generated

| Figure | Description |
|--------|-------------|
| `figures/ratio_bar.png` | Bar chart: mean ± std ratio per paradigm, p-value annotations for significant pairs |
| `figures/acc_heatmap.png` | 2×4 heatmap: spurious_acc and task_acc per paradigm (mean across seeds) |
| `figures/acc_scatter.png` | Scatter: spurious_acc vs task_acc per paradigm (5 seeds as points) |
| `figures/pvalue_matrix.png` | 4×4 symmetric Bonferroni p-value matrix |
| `figures/ratio_violin.png` | Violin plot: ratio distribution per paradigm (5 seeds) |

---

## Next Steps

**Gate: SATISFIED → Proceed to Phase 5 (Baseline Comparison)**

Phase 5 should:
1. Run the same probing protocol with a proper baseline (e.g., random ResNet-50) to contextualize ratio magnitude
2. Test on CelebA as secondary dataset for generalization
3. Verify statistical robustness with larger seed set (e.g., 10 seeds)
4. Quantify which augmentation differences between SSL paradigms drive the ratio divergence

---

## Phase 2C Handoff

### Proven Components

| Component | File | Evidence |
|-----------|------|----------|
| `get_waterbirds_subsets()` | `data_utils.py` | All 4 paradigms loaded successfully; 5,794 test samples used |
| `get_balanced_probe_indices()` | `data_utils.py` | Correct group-balanced sampling verified by unit test |
| `load_erm()` / `load_moco()` / `load_dino()` / `load_barlowtwins()` | `model_utils.py` | All 4 models: output (N, 2048), smoke test passed |
| `get_or_extract_features()` | `model_utils.py` | Feature caching working; reused across 5 seeds |
| `train_probe()` / `eval_probe()` | `probe_utils.py` | 40 LogisticRegression fits completed successfully |
| `compute_ratio()` | `probe_utils.py` | 20 valid ratios (all acc > 0.5) |
| `pairwise_tests()` | `stats_utils.py` | 6 pairs computed with Bonferroni correction + Cohen's d |
| `check_gate()` | `stats_utils.py` | Gate check logic verified by unit tests |
| `export_results()` | `stats_utils.py` | JSON output written and validated |
| All 5 figure functions | `viz_utils.py` | 5 PNG files generated successfully |

### Optimal Hyperparameters

```yaml
probe:
  C: 1.0          # Izmailov et al. 2022 default — optimal for DFR-style probing
  max_iter: 1000
  solver: lbfgs
  n_jobs: -1      # parallel CPU fitting

feature_extraction:
  batch_size: 256
  device: cuda
  mode: eval
  no_grad: true

statistical_analysis:
  seeds: [0, 1, 2, 3, 4]
  n_bonferroni: 6  # C(4,2) pairs
  alpha: 0.05
  min_diff: 0.02

data:
  dataset: waterbirds
  wilds_version: "2.0"
  root_dir: "~/.wilds_cache"
  probe_train: group_balanced_val  # NOT training set (95% spurious)
  test: full_balanced_test         # 5,794 images, 50% spurious
```

### Lessons Learned

**What Worked:**
- Feature caching (`get_or_extract_features`) critical for performance — extracting once per paradigm and reusing across 5 seeds made the experiment feasible
- Using WILDS val split (not train) for probe training correctly avoided the 95% spurious correlation in the training set
- Group-balanced sampling from val split using metadata `[:,0]` (background) and `[:,1]` (bird) columns correctly identified 4 groups
- BarlowTwins weights loaded cleanly from official URL (0 missing keys) — direct `load_state_dict_from_url` more reliable than Hub for this model
- DINO's `dino_resnet50` hubconf already sets `fc=Identity` — no modification needed

**What Didn't Work Initially:**
- PyTorch Hub download for MoCo-v3 failed (missing `hubconf.py` in local cache) — resolved by creating a custom `hubconf.py` that loads backbone weights from official `r-50-1000ep.pth.tar`
- WILDS dataset path: config pointed to wrong root; needed to use `~/.wilds_cache` where WILDS previously cached the dataset
- BarlowTwins through Hub (`facebookresearch/barlowtwins:main`) — Hub not available without network; direct weight download more reliable

**Unexpected Findings:**
- MoCo-v3 has notably LOWER spurious encoding ratio (1.027) compared to ERM (1.052) and DINO (1.050) — MoCo-v3's contrastive objective may suppress background texture features more than expected
- ERM and DINO show similar ratios (diff = 0.0025, p_bonf = 1.0) — interesting given their different pretraining objectives
- BarlowTwins has intermediate ratio (1.033) between MoCo-v3 and ERM/DINO — non-contrastive SSL shows partial suppression of spurious features

**Key Insight:**
MoCo-v3 is the outlier: its contrastive objective (with strong augmentations including large crops and color jitter) suppresses background texture features significantly more than other paradigms. The ERM ≈ DINO similarity suggests that self-distillation (DINO) may not substantially reduce spurious feature encoding versus supervised training on Waterbirds.

### Recommendations for Dependent Hypotheses

**For h-d1 (if it studies paradigm differences):**
- Use ERM vs MoCo-v3 as the primary comparison pair — highest ratio difference (0.0247) and statistical power (Cohen's d = 5.68)
- Cache features at `/tmp/h-e1-cache/` — reusable for any h-d1 experiment using same models
- Expect MoCo-v3 to consistently show lower spurious encoding across seeds (std = 0.0038, lowest variance)

**For h-m1 (mechanism):**
- Augmentation analysis: focus on what makes MoCo-v3 different from ERM/DINO (likely: larger crop scale, stronger color jitter)
- BarlowTwins intermediate result (ratio = 1.033) useful for gradient analysis — is it due to cross-correlation objective or augmentation set?

**General:**
- Waterbirds balanced test split is reliable (5,794 samples, 50% balanced) — use it for all comparative experiments
- Group-balanced val probe split is essential — biased (95% spurious) train split would inflate spurious probe accuracy artificially

---

## Appendix: Artifact Inventory

| Artifact | Path | Status |
|----------|------|--------|
| Validation report | `docs/youra_research/h-e1/04_validation.md` | ✅ This file |
| Stats JSON | `docs/youra_research/h-e1/results/h-e1_stats.json` | ✅ Complete |
| Results CSV | `docs/youra_research/h-e1/results/h-e1_ratios.csv` | ✅ 20 rows (4×5) |
| Experiment JSON | `docs/youra_research/h-e1/experiment_results.json` | ✅ Complete |
| Figure: ratio bar | `docs/youra_research/h-e1/figures/ratio_bar.png` | ✅ |
| Figure: acc heatmap | `docs/youra_research/h-e1/figures/acc_heatmap.png` | ✅ |
| Figure: acc scatter | `docs/youra_research/h-e1/figures/acc_scatter.png` | ✅ |
| Figure: p-value matrix | `docs/youra_research/h-e1/figures/pvalue_matrix.png` | ✅ |
| Figure: ratio violin | `docs/youra_research/h-e1/figures/ratio_violin.png` | ✅ |
| Run log | `docs/youra_research/h-e1/logs/experiment.log` | ✅ |
| Code | `docs/youra_research/h-e1/code/*.py` | ✅ 7 modules |
| Unit tests | `docs/youra_research/h-e1/code/tests/test_modules.py` | ✅ 9 passed |
| Feature cache | `/tmp/h-e1-cache/*.pt` | ✅ 8 files (4 paradigms × 2 splits) |

---

*Phase 4 complete. Gate SATISFIED. Proceed to Phase 5 (Baseline Comparison).*

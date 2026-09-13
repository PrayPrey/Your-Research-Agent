# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-16T17:45:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — SAM does not improve WGA on Waterbirds/CelebA

## Hypothesis Statement

Under ERM training on Waterbirds (primary) and CelebA (secondary), replacing SGD with SAM (rho in {0.01, 0.05, 0.1, 0.2}) without group label supervision improves worst-group accuracy (WGA) by >=10 percentage points over ERM+SGD baseline, because SAM's data-adaptive flatness constraint implicitly contends with minority-group high-gradient-energy regions during optimization.

## Performance Gap

| Metric | Ours (Best SAM) | Baseline (SGD) | Gap |
|--------|-----------------|----------------|-----|
| WGA (Waterbirds) | 77.51% (rho=0.01) | 76.60% | +0.90pp |
| PASS threshold | — | — | >=10pp |
| PARTIAL threshold | — | — | >=5pp |

Best SAM condition: rho=0.01 (+0.90pp) — 10x below PASS threshold, also below PARTIAL threshold.

## WGA Results by Condition

| Condition | Mean WGA | vs SGD |
|-----------|----------|--------|
| ERM+SGD (baseline) | 76.60% ±2.93% | — |
| ERM+SAM rho=0.01 | 77.51% ±0.97% | **+0.90pp** |
| ERM+SAM rho=0.05 | 72.55% ±0.56% | -4.04pp |
| ERM+SAM rho=0.10 | 62.06% ±2.06% | -14.54pp |
| ERM+SAM rho=0.20 | 38.54% ±2.41% | -38.06pp |
| ERM+SGD+L2 (wd=1.0) | 0.00% ±0.00% | -76.60pp |
| GroupDRO+SGD* | 87.51% ±1.60% | +10.91pp |

*GroupDRO uses group labels during training (upper bound reference)

## Statistical Test (SAM rho=0.01 vs SGD)

- t-statistic: 0.907
- p-value (one-tailed): 0.2079
- p-corrected (Bonferroni n=4): 0.8316
- Significant (p < 0.05): **No**
- n=35 runs (7 conditions × 5 seeds), Waterbirds full test set n=5,794

## Root Cause Analysis

- SAM's flatness constraint does NOT discriminate between spurious-feature and core-feature solutions
- Flat minima and group-robust minima are not the same objective
- Larger rho values monotonically hurt WGA (dose-response is inverted vs hypothesis prediction)
- Aggressive L2 regularization (wd=1.0) completely failed: 0% WGA
- SAM provides no unique inductive bias for group-robust generalization without group label supervision

## Lessons Learned

1. Flatness regularization alone cannot substitute for group supervision in spurious correlation settings
2. SAM's perturbation radius rho is a critical sensitivity parameter — larger rho catastrophically hurts WGA
3. GroupDRO (+10.9pp) confirms the dataset is workable and WGA improvement is achievable WITH group labels
4. The Waterbirds/CelebA benchmark requires explicit minority-group awareness (label or proxy) to improve WGA
5. Methods that implicitly target shortcut identity (JTT, LfF) are more promising than generic flatness

## Failed Checks

- WGA improvement: +0.90pp < 5pp PARTIAL threshold
- Statistical significance: p_corrected=0.83 >> 0.05
- rho=0.05: -4.0pp; rho=0.1: -14.6pp; rho=0.2: -38.6pp (all hurt WGA)

## Cascade Effects

- h-m1: CASCADE_FAILED (Hessian curvature ordering — moot without h-e1 passing)
- h-m2: CASCADE_FAILED (lambda1 reduction — moot)
- h-m3: CASCADE_FAILED (MNIST-CIFAR AUC — moot)

## Feedback for Next Phase (Phase 0 Redesign)

### Suggested Research Directions
- JTT (Just Train Twice): ERM pass → identify misclassified → upsample for second ERM pass. No group labels. Reported +21pp WGA on Waterbirds.
- LfF (Learning from Failure): Bias-amplified model identifies minority samples for debiased model. Group-label-free.
- SELF (Self-Supervised Ensemble with Label-Free Features): Self-supervised pretraining avoids spurious texture correlations.
- DFR (Deep Feature Reweighting): Retrain last layer on group-balanced subset (small labeled set, not full group labels).

### What NOT To Do
- Do NOT use generic flatness/sharpness minimization (SAM, ASAM, etc.) as the primary mechanism for WGA improvement
- Do NOT assume isotropic regularization (L2 weight decay) helps WGA — wd=1.0 gave 0% WGA
- Do NOT assume loss landscape geometry correlates with group robustness without group-aware signals

### What Showed Promise (Reusable Infrastructure)
- WaterbirdsDataset implementation: metadata.csv loading, group_id=2*y+place — confirmed correct
- ResNet-50 backbone (ImageNet pretrained, FC→Linear(2048,2)) — works for Waterbirds
- GroupDRO implementation: +10.9pp WGA confirmed — proven correct
- Full evaluation framework: compute_wga, Bonferroni t-test, build_summary_table
- Conda env youra-h-e1: all packages installed, dataset cached at .data_cache/datasets/waterbirds

## Experiment Infrastructure

- Code location: h-e1/code/ (config.py, data_loader.py, sam_optimizer.py, train.py, evaluate.py, figures.py, run_experiment.py)
- Dataset cache: .data_cache/datasets/waterbirds/ (11,788 samples verified)
- Results: h-e1/code/results/ (35 result JSONs), h-e1/experiment_results.json
- Conda env: youra-h-e1 (Python 3.10, pytorch, torchvision, wilds, sam-pytorch)
- GPU: NVIDIA H100 NVL

---
*Failure recorded at: 2026-03-16T17:45:00Z*
*Routing: ROUTED_TO_PHASE_0*
*For cross-phase reference — Phase 0 brainstorm should incorporate these lessons*

---
type: failure
hypothesis_id: h-e1
phase: Phase 4
gate_type: MUST_WORK
gate_result: FAIL
recorded_at: 2026-03-16T17:40:00Z
research_folder: /home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl
---

# Failure Record: h-e1 — SAM WGA Existence Test

## Gate Result: FAIL (ROUTED_TO_PHASE_0)

## Hypothesis
SAM optimizer improves worst-group accuracy (WGA) by >=10pp over ERM+SGD on Waterbirds without group label supervision.

## Experiment
- 7 conditions × 5 seeds = 35 runs, Waterbirds full test set (n=5794)
- 20 epochs, ResNet-50 pretrained, SAM rho ∈ {0.01, 0.05, 0.1, 0.2}

## Results
| Condition | Mean WGA | vs SGD |
|-----------|----------|--------|
| ERM+SGD | 76.60% | baseline |
| SAM rho=0.01 | 77.51% | +0.90pp |
| SAM rho=0.05 | 72.55% | -4.04pp |
| SAM rho=0.10 | 62.06% | -14.54pp |
| SAM rho=0.20 | 38.54% | -38.06pp |
| GroupDRO (group-supervised) | 87.51% | +10.91pp |
| L2 (wd=1.0) | 0.00% | -76.60pp |

## Statistical Test
- Best SAM vs SGD paired t-test: t=0.907, p_corrected=0.83 (NOT significant)
- Threshold: >=10pp PASS, >=5pp PARTIAL

## Root Causes
1. **Flat minima ≠ group-robust minima**: SAM seeks flat loss landscapes, but spurious feature solutions can also be flat — flatness alone does not discriminate against shortcut features.
2. **rho sensitivity**: Larger perturbation radii (rho>0.01) actively hurt minority group accuracy, suggesting SAM's perturbations in high-rho regimes destabilize the optimization in ways that hurt minority groups.
3. **No group-label-free advantage**: The improvement of +0.90pp is within noise (std of SGD: 2.93pp). SAM adds no reliable inductive bias against spurious correlations without group supervision.
4. **GroupDRO works (+10.9pp) but requires group labels** — the problem is solvable, but SAM is not the right tool.

## Lessons for Future Hypotheses
- Do NOT pursue SAM (or similar flatness-based optimizers) as a drop-in for WGA improvement without group labels
- The gap between "flat minima" and "group-robust minima" is large and cannot be bridged by rho tuning
- If pursuing unsupervised WGA improvement, focus on: (1) data augmentation targeting minority groups, (2) self-supervised pretraining that avoids spurious features, (3) methods that explicitly identify and downweight spurious correlations (JTT, LfF, etc.)
- GroupDRO is a strong baseline requiring group labels — any group-label-free method should aim to match it

## Cascade Effects
- h-m1, h-m2, h-m3: All CASCADE_FAILED (mechanism hypotheses moot without existence proof)

# Introduction

When does training go wrong? For models trained on group-imbalanced data, the answer is: 3-4 epochs before the problem becomes visible. By the time worst-group accuracy diverges from average accuracy, the underlying cause—differential curvature between groups—has already been established in the loss landscape.

Deep neural networks trained with empirical risk minimization (ERM) on datasets with spurious correlations systematically underperform on minority groups. On Waterbirds, where 95% of waterbirds appear on water backgrounds, ERM achieves ~97% average accuracy but only ~75% on the minority group (waterbirds on land). This 20+ percentage point gap has motivated numerous interventions: Group DRO (Sagawa et al., 2019), last-layer retraining (Kirichenko et al., 2022), and various reweighting schemes.

Yet these methods address the symptom—poor minority accuracy—without explaining the mechanism. Why do minority groups fail? Recent work established that minority groups occupy sharper regions of the loss landscape, with sharpness ratios SR > 1.0 (minority curvature exceeds majority curvature). But is this curvature asymmetry intrinsic to the data, or does it emerge from training dynamics?

We investigate the **Differential Convergence Rate (DCR) hypothesis**: majority groups, having more samples, converge faster during training. Their gradient norms decay earlier, smoothing curvature in majority-relevant parameter directions. Minority-relevant directions, receiving fewer updates, remain sharp. This differential traversal creates the observed SR > 1.0 pattern.

Our contributions:

1. **Initialization baseline:** We establish that SR ≈ 1.0 at random initialization (SR₀ = 0.9999 ± 0.0047), ruling out intrinsic data geometry as the source of curvature asymmetry.

2. **Temporal precedence:** We show that gradient ratio decay temporally precedes sharpness ratio divergence by τ = 3.67 epochs (95% CI [3.0, 4.0]). This temporal ordering is consistent with—though does not prove—a causal relationship.

3. **Diagnostic window:** The 3-4 epoch lag between gradient convergence and curvature divergence opens a potential intervention window: monitoring gradient ratios could enable early detection and correction before curvature disparity solidifies.

Our findings reframe the group robustness problem from post-hoc correction to early-training dynamics. The mechanism we identify—differential convergence causing differential curvature—suggests that interventions targeting gradient dynamics during the critical 3-4 epoch window may be more effective than post-training corrections.

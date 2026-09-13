# Abstract

Neural networks trained with empirical risk minimization on group-imbalanced data exhibit poor worst-group accuracy. Prior work established that minority groups occupy sharper regions of the loss landscape (sharpness ratio SR > 1.0), but the origin of this curvature asymmetry remained unclear. We investigate the **Differential Convergence Rate** hypothesis: majority groups converge faster during training, smoothing curvature in majority-relevant parameter directions while leaving minority directions sharp.

We present two key findings. First, we establish that **SR ≈ 1.0 at random initialization** (SR₀ = 0.9999, 95% CI [0.9953, 1.0046]), ruling out intrinsic data geometry as the source of curvature asymmetry. Second, we show that **gradient ratio decay temporally precedes sharpness ratio divergence** by τ = 3.67 epochs (95% CI [3.0, 4.0]). This positive lag indicates that majority convergence precedes minority curvature increase, consistent with a causal mechanism.

Our findings reveal a diagnostic window: gradient dynamics signal impending curvature divergence 3-4 epochs before it manifests. This temporal characterization opens the path from post-hoc worst-group corrections to early-training interventions targeting the root cause. Code and data are available at [anonymous repository].

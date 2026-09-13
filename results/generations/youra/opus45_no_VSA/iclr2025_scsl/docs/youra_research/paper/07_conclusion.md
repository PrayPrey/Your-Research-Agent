# Conclusion

We return to our opening question: *When does training go wrong?* Our answer: 3-4 epochs before the symptom appears. Gradient ratio decay—the signal that majority groups are converging—temporally precedes sharpness ratio divergence by τ = 3.67 epochs. This lag opens a diagnostic window for early intervention.

We established two key findings supporting the Differential Convergence Rate hypothesis:

1. **No intrinsic asymmetry:** SR₀ = 0.9999 at random initialization confirms that curvature disparity is training-induced, not data-intrinsic. Any SR > 1.0 observed after training arises from optimization dynamics.

2. **Temporal precedence:** The positive lag τ_r→SR = 3.67 epochs (95% CI [3.0, 4.0]) indicates gradient convergence precedes curvature divergence. This temporal ordering is consistent with causation: majority convergence → differential traversal → minority sharpness.

These findings reframe the group robustness problem. Existing methods correct the symptom (poor minority accuracy) after training. Our mechanistic understanding suggests targeting the cause (gradient dynamics) during training. The 3-4 epoch window between gradient signal and curvature consequence is where intervention may be most effective.

The intervention itself—update-norm parity—remains code-validated but experimentally unconfirmed. Completing this test, along with multi-dataset validation, constitutes the immediate next step.

Understanding *when* and *why* the loss landscape becomes asymmetric between groups is the foundation for principled intervention. We provide the first quantitative characterization of this temporal mechanism, opening a path from post-hoc correction to early-training design.

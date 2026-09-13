# Conclusion

We began by questioning the dominant explanation for why neural networks learn spurious features—that such features produce stronger gradient signals during training. Our investigation reveals this explanation is wrong, and its wrongness has implications for how the field approaches robustness.

## Summary

We designed a two-stage experimental framework to test the gradient competition hypothesis. First, we confirmed that spurious feature dominance exists: GradCAM attribution ratios exceed 1.0 from epoch 0, reaching 1.35 at initialization and peaking at 1.59 around epoch 13. ERM-trained ResNet-50 models on Waterbirds exhibit immediate and persistent preference for background over bird features.

Second, we directly measured gradient norms for spurious-aligned versus minority samples to test the hypothesized mechanism. The results were unambiguous: the gradient ratio is 0.18, not the >1.5 predicted by gradient competition. Minority samples produce 5.7× higher gradient norms than spurious-aligned samples—a complete inversion of the hypothesis.

Our main contributions are:

1. **Empirical falsification** of the gradient competition hypothesis with high confidence (8× inversion, consistent across 3 seeds)

2. **Confirmation and characterization** of simplicity bias dynamics, showing spurious dominance from initialization

3. **Mechanistic reframing** proposing that spurious dominance arises from convergence speed—simpler patterns achieve low loss faster, not louder gradient signals

## Future Directions

Our falsification opens several research paths grounded in our experimental findings:

**Testing the convergence speed hypothesis.** Our results suggest spurious dominance is a convergence phenomenon. Direct measurement of per-group loss trajectories would confirm whether spurious-aligned samples reach low loss before minority samples, independent of gradient magnitude.

**Connecting to loss landscape geometry.** If spurious solutions occupy sharper minima, this would explain both fast convergence and poor generalization. Hessian eigenvalue analysis at peak spurious dominance (epoch 13) versus convergence could reveal the geometric structure underlying our findings.

**Revisiting SAM through the convergence lens.** Sharpness-Aware Minimization may improve robustness precisely because it penalizes fast convergence to sharp (spurious) solutions. Our mechanistic reframing suggests SAM's effectiveness may stem from slowing convergence in simple basins rather than directly affecting gradient dynamics.

**Multi-dataset replication.** Our findings on Waterbirds may or may not transfer to CelebA (face attributes), Colored MNIST (color-digit correlation), or CivilComments (text). Replication would establish the generality of inverted gradient dynamics.

## Closing Remarks

The gradient competition hypothesis offered an intuitive explanation for spurious feature learning: simpler features receive stronger signals and thus dominate. Our measurements reveal this intuition, however elegant, is empirically incorrect. Spurious features dominate not because they shout louder, but because they finish first.

This distinction matters for intervention design. Methods that attempt to rebalance gradient contributions may be addressing the wrong mechanism. Instead, robustness interventions might more effectively target convergence timing—slowing the rush to simple solutions or extending the window for invariant feature development.

Understanding why our models fail is the first step toward building models that do not. We hope this work contributes to that understanding by replacing an assumed mechanism with a measured one.

# Conclusion

We began with a paradox: information theory predicts that denser reward signals should accelerate reinforcement learning, yet our proof-of-concept experiment found no difference between binary, continuous, and high-bandwidth rewards. All conditions produced 0% pass@1.

The resolution is not that the theory is wrong. The resolution is that PoC scale is insufficient. At ~1000 gradient updates, no policy improvement emerges in ANY condition, making reward comparison impossible. The information bandwidth hypothesis remains untested—neither confirmed nor falsified.

Our contribution is methodological rather than empirical. We establish a lower bound: 1-epoch experiments are uninformative for code LLM reward ablation studies. Future researchers should budget ≥3 epochs, ≥5 seeds, and learning rate warm-up before expecting measurable feedback effects.

The negative result we report has value. By publishing an underpowered experiment rather than abandoning it, we prevent others from repeating our mistake. This is a contribution to efficient use of compute across the research community.

The theoretical framework—that feedback granularity affects credit assignment precision—remains intact. Binary rewards provide 1 bit per update; error-type scoring adds ~1 bit via principled distance-to-correct ordering. Whether this additional information translates to faster convergence is an open question awaiting adequate-scale experimentation.

Future work should design for scale from the start, not rely on iterative extension until positive results emerge. If the bandwidth effect is real, it will appear when compute is sufficient. If it does not appear at adequate scale, then the hypothesis is falsified. Our current result establishes neither—only the threshold below which investigation is pointless.

The paradox with which we opened remains open: dense feedback should help, but demonstrating this requires more compute than we allocated. The answer is not more theory. The answer is more training.

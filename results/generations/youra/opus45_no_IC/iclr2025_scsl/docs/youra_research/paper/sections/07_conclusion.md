# Conclusion

We demonstrated that simplicity bias creates a detectable signature in training dynamics: minority-group samples exhibit 8× higher loss at just 5% of training epochs compared to majority samples. This signal enables automatic detection without group labels, achieving 6.6× improvement over random baseline.

Through linear probe analysis, we established the underlying mechanism: simplicity bias causes representations to encode spurious features (background) with ~10 percentage points higher accuracy than core features (bird shape) throughout training. With ImageNet-pretrained features, this manifests as a persistent magnitude gap rather than a timing gap—both feature types peak at the same epoch but with different accuracy levels.

Our analysis provides the first explicit characterization of precision limits under minority imbalance. The 33% precision at 5% minority rate is not a failure but a mathematical ceiling—the loss signal provides near-perfect ranking despite modest absolute precision.

## Future Directions

**Training from scratch**: Our timing hypothesis (spurious features peak earlier) was not supported with pretrained features. Experiments without ImageNet initialization could reveal whether temporal dynamics differ when features must be learned de novo.

**Cross-dataset transfer**: Validating on CelebA (~15% minority rate) and MultiNLI (text domain) would establish generalizability beyond Waterbirds and test whether precision scales with minority prevalence.

**Intervention effectiveness**: Characterizing the detection signal enables but does not evaluate intervention. Future work should test whether upweighting high-loss samples at epoch 5 improves worst-group accuracy comparable to JTT's two-stage approach.

**The 8× loss difference is not just a statistic—it is a window into how neural networks prioritize simpler patterns, creating systematic disadvantages for minority groups that can now be detected and addressed during training.**

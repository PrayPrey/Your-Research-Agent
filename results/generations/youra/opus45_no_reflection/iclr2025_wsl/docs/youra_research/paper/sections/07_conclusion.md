# Conclusion

We asked whether model behavior is predictable from weights. Our answer: behavioral fingerprints exist—67.6% of class-wise accuracy variance in the Small CNN Zoo is unexplained by overall accuracy—but extracting this signal via simple weight statistics fails.

This negative result is constructive. It establishes that (1) behavioral structure beyond accuracy is real and substantial, warranting attention from weight-space learning methods, and (2) simple features that achieve R² > 0.9 for scalar accuracy do not extend to structured behavioral prediction. The gap between existence and extraction motivates learned representations—NF-Layers, behavioral autoencoders, or embeddings trained directly on behavioral targets.

The path forward involves three directions. First, **scale**: testing on the full 30,000-model zoo to isolate sample-size effects from true feature limitations. Second, **expressivity**: replacing scalar statistics with weight distributions, singular value spectra, or learned encoders. Third, **transfer**: validating whether behavioral embeddings generalize to unseen metrics like confusion similarity or sample-level error patterns.

Model accuracy is not the whole story—and neither is this paper. We have quantified the behavioral signal; extracting it remains an open challenge.

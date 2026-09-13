# Conclusion

We asked: when does a neural network's reliance on spurious correlations become irreversible? Our answer is the Shortcut Crystallization Zone—a narrow training phase at 15-40% of training duration where classifier commitment to spurious features accelerates and locks in.

Through experiments on Waterbirds, CelebA, and ColoredMNIST, we established that this crystallization is detectable via the second derivative of worst-group accuracy. With 5-epoch smoothing, our method achieves 100% detection rate and signal-to-noise ratio exceeding 5. The gradient ratio between minority and majority groups shows an inflection point that temporally precedes the WGA acceleration, confirming gradient starvation as the causal mechanism. Once crystallization occurs, the classifier's preference persists—spurious feature probe accuracy is maintained at 0.9468 without external intervention.

These findings move the field from static characterizations of shortcut learning ("DNNs prefer simple features") to dynamic temporal understanding ("shortcuts crystallize at epoch X under conditions Y"). The practical implication is clear: intervention timing matters. Group robustness methods could be made more efficient by targeting the crystallization window rather than applying corrections uniformly throughout training.

Our detection method enables this timing-aware approach. By tracking d²WGA/dt² during training, practitioners can identify when crystallization is imminent and apply corrective measures—balanced sampling, gradient reweighting, or early stopping—at the critical moment.

Future work should extend crystallization analysis to vision transformers and NLP benchmarks, test intervention strategies that exploit crystallization timing, and explore whether modifying optimization dynamics (e.g., SAM) can delay or prevent crystallization entirely.

The shortcut crystallization zone represents a new lens for understanding and addressing spurious correlation failures in deep learning.

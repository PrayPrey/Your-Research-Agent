# Abstract

Can neural networks learn permutation symmetries from data, or must such structure be built into the architecture? We study this question in weight-space learning, where models predict properties of neural networks from their weights. Using the Model Zoo dataset of 42K CIFAR-10 CNNs, we compare permutation-equivariant Neural Functional Networks (NFN) against matched-capacity MLPs across data scales from 1K to 40K models.

Our experiments reveal a striking dissociation: at N=40K, MLPs achieve near-perfect prediction accuracy (R²=0.986) but fail to develop permutation invariance (0.63 vs NFN's 1.0). This demonstrates that task performance and representation quality are separable—MLPs learn dataset-specific position-accuracy correlations rather than semantic weight structure.

At small scales, the gap is even more dramatic: NFN achieves R²=0.95 at N=1K where MLP achieves only R²=0.35—a 60 percentage point advantage. NFN's predictions are invariant to weight permutation with deviations below 1.19e-07, confirming mathematical guarantees.

These findings falsify the hypothesis that sufficient data diversity teaches invariance. Permutation equivariance provides sample efficiency that data quantity cannot substitute—architectural inductive biases are essential, not merely convenient, for exploiting certain symmetries.

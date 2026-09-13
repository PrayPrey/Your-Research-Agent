# Abstract

Neural network weights are predictive of generalization — but standard weight-space encoders
treat neuron position as meaningful signal, creating representations that collapse when neurons
are arbitrarily reordered at test time. We show that this brittleness stems from a fundamental
mismatch: flat-MLP encoders rely on neuron ordering artifacts, yet fully-connected networks
are equivariant to any neuron permutation by construction. We address this by conducting the
first controlled comparison between Neural Functional Transformers (NFT) — a permutation-
equivariant encoder — and flat-MLP baselines for generalization gap prediction on the Unterthiner
model zoo. NFT achieves near-zero permutation sensitivity while outperforming flat-MLP at
baseline with 40 times fewer parameters, and we confirm the mechanism via mediation analysis:
equivariant attention specifically captures the neuron influence concentration signals that
flat-MLP cannot encode invariantly. The alternatives — permutation augmentation and L2-norm
canonicalization — are either unreliable or catastrophically wrong. Our results establish
architectural equivariance as the correct inductive bias for weight-space property prediction
on fully-connected model zoos.

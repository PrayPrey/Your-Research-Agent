# Research Idea

## Title
Inhibitory Error-Gated Hebbian Plasticity for Backpropagation-Free Spiking Neural Networks

## Motivation
Spiking neural networks (SNNs) promise energy-efficient, brain-like computation, but training them typically requires backpropagation through time—computationally expensive and biologically implausible. The brain solves credit assignment locally using inhibitory interneurons and neuromodulatory signals, yet this mechanism remains underexploited in artificial systems. Bridging this gap could enable efficient SNNs that learn without explicit gradient computation while supporting continual learning without catastrophic forgetting.

## Main Idea
We propose Inhibitory Error-Gated Hebbian Plasticity (IEGH-HP), where inhibitory error neurons compute local prediction errors that gate Hebbian weight updates, scaled by a global neuromodulator signal reflecting task-level feedback. The four-step mechanism operates as: (1) excitatory neurons encode predictions via spike patterns, (2) inhibitory neurons compute prediction mismatch through subtractive inhibition, (3) error signals gate local Hebbian updates (Δw = η × pre × post × error_gate), and (4) neuromodulator broadcast scales updates based on loss feedback.

We will implement IEGH-HP in snnTorch and evaluate on MNIST, CIFAR-10, and SHD benchmarks, comparing against surrogate gradient baselines. We predict accuracy within 10% of backpropagation methods, 30-50% fewer synaptic operations, and <5% forgetting in continual learning scenarios. Ablation studies will verify each mechanism component. This work advances biologically-plausible learning rules for neuromorphic computing.
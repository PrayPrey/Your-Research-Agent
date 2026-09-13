# Research Idea

## Title
Unified Differentiable Discrete Operations via Learnable Optimal Transport

## Motivation
Deep learning models increasingly require discrete operations (categorical selection, sorting, top-k) that break gradient flow. Current solutions use operation-specific relaxations (Gumbel-Softmax, Sinkhorn sorting, differentiable top-k), forcing practitioners to manually select and tune separate mechanisms. This fragmentation limits models that need multiple or adaptive discrete operations. A unified framework would simplify implementation, enable automatic operation selection, and potentially discover hybrid operations suited to specific tasks.

## Main Idea
We hypothesize that categorical selection, sorting, and top-k operations are special cases of optimal transport with different cost matrix structures. We propose OT-UNI: a single differentiable layer where discrete operations are encoded as parameterized OT problems with learnable cost matrices C(θ). The key mechanism is:

1. **Cost parameterization**: Diagonal costs → softmax; anti-diagonal → sorting; block-sparse → top-k
2. **Sinkhorn relaxation**: Entropic regularization provides differentiable soft assignments
3. **Operation learning**: Gumbel reparameterization enables gradients through operation-type selection

We will verify that OT-UNI recovers baseline behaviors (L2 < 0.01), achieves gradient SNR ≥ 0.5× baselines, and learns meaningful operation embeddings (clustering purity > 0.8). Falsification occurs if Sinkhorn diverges in >10% of cases or gradients become uninformative. Success would provide a principled, unified approach to differentiable discrete computation with automatic operation adaptation.
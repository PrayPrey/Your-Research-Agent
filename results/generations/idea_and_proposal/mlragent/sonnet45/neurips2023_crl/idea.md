# Title
Causal Abstraction Learning for Multi-Granularity Visual Understanding

## Motivation
Current causal representation learning methods typically operate at a single level of abstraction, learning either low-level features or high-level concepts. However, human cognition naturally operates across multiple scales—we understand both fine-grained details and abstract relationships simultaneously. This limitation hinders CRL's applicability to complex real-world vision tasks where different granularities of causal understanding are required (e.g., medical diagnosis requires both cellular-level and organ-level causal reasoning). We need methods that can discover and reason about causal hierarchies automatically.

## Main Idea
We propose a hierarchical CRL framework that learns multi-level causal abstractions from raw visual data through a novel objective combining:

1. **Bottom-up discovery**: Identify primitive causal factors at fine granularity, then progressively cluster them into higher-level abstract variables based on causal dependencies and intervention effects.

2. **Top-down refinement**: Use high-level causal structures to guide lower-level representation learning through consistency constraints.

3. **Cross-level intervention**: Design interventions that operate across abstraction levels, enabling the model to learn when different granularities are causally relevant.

The framework employs variational autoencoders with structured latent spaces and graph neural networks to model inter-level causal relationships. We'll validate on synthetic benchmarks with known hierarchical structures and real-world medical imaging tasks. Expected outcomes include improved generalization across domains, better interpretability through multi-scale causal explanations, and enhanced sample efficiency by leveraging causal structure at appropriate abstraction levels.
# Related Work

We position our work at the intersection of three research areas: knowledge distillation, sub-quadratic sequence models, and attention-SSM theoretical connections. Each area provides valuable foundations but leaves a critical gap: no existing work empirically validates whether attention-SSM duality enables practical knowledge transfer.

## Knowledge Distillation

Knowledge distillation transfers knowledge from a large teacher model to a smaller student [Hinton et al., 2015]. DistilBERT [Sanh et al., 2019] achieves 97% of BERT's performance with 40% fewer parameters using soft-target distillation combined with cosine embedding loss. TinyBERT [Jiao et al., 2020] extends this with layer-wise intermediate matching.

**Limitation:** These methods operate within the same architecture family (Transformer → Transformer). They cannot bridge to fundamentally different computational primitives like SSMs, which use recurrent state evolution rather than pairwise attention. Cross-architecture distillation requires understanding how to map computational structure, not just outputs.

## Sub-Quadratic Sequence Models

State space models offer O(n) inference complexity through recurrent computation. Mamba [Gu and Dao, 2023] introduces selective scan, achieving competitive performance with Transformers on standard benchmarks. RWKV [Peng et al., 2023] combines linear attention with exponential decay. RetNet [Sun et al., 2023] proposes retention mechanisms with parallel training and recurrent inference.

**Limitation:** These models are typically trained from scratch or initialized randomly. While they achieve strong performance when trained sufficiently, they cannot leverage existing pretrained Transformer knowledge. This represents wasted compute when high-quality pretrained models already exist.

## Attention-SSM Theoretical Connections

Mamba-2 [Dao and Gu, 2024] proves a fundamental duality: under the structured state-space duality (SSD) framework, linear attention is theoretically equivalent to a state space model with specific parameterization. This suggests that attention weights can be converted to SSM parameters via closed-form equations.

MOHAWK [Waleffe et al., 2024] operationalizes this insight for distillation, proposing a three-stage approach: (1) matrix alignment matching CB^T to QK^T, (2) hidden state alignment, (3) soft target distillation. Their Stage 1 uses matrix-level alignment rather than output-level reconstruction.

**Limitation:** Mamba-2 proves duality under restrictive conditions (scalar-times-identity A matrix, 1-semiseparable causal masks). Real Transformer attention—multi-head with learned position embeddings—may violate these conditions. Neither Mamba-2 nor MOHAWK directly tests whether duality-derived parameters reconstruct attention outputs better than random initialization.

## Our Contribution

We directly test the foundational assumption: does duality-based initialization provide a better starting point than random? Unlike MOHAWK's matrix alignment (CB^T vs. QK^T), we use output Frobenius norm to measure whether SSM outputs approximate attention outputs. This output-level test reveals that duality produces valid parameters (0% NaN/Inf, 0.11x magnitude) but fails at structural fidelity (2.13% worse than random).

Our work complements Mamba-2's theoretical contribution with empirical scope clarification: practitioners should not expect zero-shot output alignment from duality initialization alone. This negative result guides future research toward understanding which attention patterns satisfy duality conditions and which metrics appropriately capture structural transfer.

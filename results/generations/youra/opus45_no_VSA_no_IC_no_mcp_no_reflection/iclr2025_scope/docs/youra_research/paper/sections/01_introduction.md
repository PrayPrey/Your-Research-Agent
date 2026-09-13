# Introduction

Mamba-2 establishes theoretical equivalence between Transformer attention and state space models (SSMs), promising a principled path for knowledge transfer from pretrained Transformers to sub-quadratic architectures [Dao and Gu, 2024]. This structured state-space duality (SSD) framework suggests that attention mechanisms can be converted to SSM form while preserving computational structure—potentially enabling deployment of BERT-scale models with O(n) inference complexity. We test whether this duality enables practical distillation and discover a surprising result: duality-derived SSM parameters are numerically stable but reconstruct attention outputs 2.13% worse than random initialization (p < 0.0001, Cohen's d = -4.56).

This finding matters for practitioners considering cross-architecture distillation. If a pretrained Transformer's knowledge could transfer to an efficient SSM via duality equations, edge deployment and long-context inference would become dramatically more accessible. However, without understanding the scope and limitations of attention-SSM duality, practitioners may invest significant compute in approaches that fail at the foundational level.

## The Problem

At the surface level, Transformers achieve state-of-the-art performance across NLP tasks but suffer from quadratic attention complexity, limiting deployment on resource-constrained devices and long-context applications. Sub-quadratic alternatives—Mamba [Gu and Dao, 2023], RWKV [Peng et al., 2023], RetNet [Sun et al., 2023]—offer linear-time inference but typically require training from scratch, forfeiting pretrained knowledge.

Looking deeper, no methodology exists for transferring pretrained Transformer knowledge to SSM architectures while preserving the learned attention structure. Same-architecture distillation (e.g., DistilBERT [Sanh et al., 2019]) succeeds but cannot bridge architectural families. Naive output-matching knowledge distillation treats the student as a black box, ignoring the internal computational structure that attention encodes.

The gap we address is the empirical validation of Mamba-2 duality for practical distillation. While Mamba-2 proves theoretical equivalence under specific conditions (scalar A matrix, 1-semiseparable causal masks), real attention—multi-head with learned position embeddings—may not satisfy these conditions. Whether duality equations produce SSM parameters that capture meaningful attention structure remains untested.

## Key Insight

Our central finding is that **numerical stability does not imply structural fidelity**. We decompose the duality-to-distillation pipeline into two verification stages: (1) parameter validity—do duality equations produce non-divergent SSM parameters?—and (2) structural preservation—do these parameters reconstruct attention outputs better than random initialization?

The first stage passes: 100% of samples produce stable SSM outputs with 0.11x magnitude ratio relative to Transformer outputs. The second stage fails: duality initialization is consistently worse than random across all 12 BERT layers. This separation identifies where duality breaks down—at output-level structural fidelity, not at parameter-level validity.

## Contributions

Building on this insight, we make the following contributions:

1. **First empirical test of Mamba-2 duality for distillation.** We operationalize the SSD framework for attention-to-SSM parameter conversion and validate on BERT-base, providing concrete evidence about duality's practical scope.

2. **Separation of validity from fidelity.** Our two-stage verification (h-e1: stability, h-m1: reconstruction) isolates the failure point, showing that valid parameters do not imply preserved structure.

3. **Negative result with clear boundary.** We demonstrate that duality initialization produces 2.13% worse reconstruction error than random (p < 0.0001), with consistent negative effects across all 12 layers. This clarifies when duality should *not* be expected to provide zero-shot output alignment.

4. **Future directions grounded in evidence.** We identify metric mismatch (output Frobenius norm vs. MOHAWK matrix alignment) and architecture mismatch (multi-head vs. SSD assumptions) as probable causes, guiding follow-up work.

The remainder of this paper is organized as follows. Section 2 positions our work against related approaches in knowledge distillation and attention-SSM theory. Section 3 describes our methodology for duality-based parameter extraction and validation. Section 4 presents experimental setup, and Section 5 reports results. Section 6 discusses implications and limitations, and Section 7 concludes.

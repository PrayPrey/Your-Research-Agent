# Research Idea

## Title
SE(3)-Equivariant Feedback Adapters for Sample-Efficient Protein Design

## Motivation
Protein generative models like RFdiffusion achieve impressive in-silico performance but suffer from low wet-lab success rates (5-20%), creating a critical gap between computational predictions and experimental outcomes. Current approaches either ignore experimental feedback entirely or require expensive model retraining. This disconnect wastes resources and slows therapeutic development. A key opportunity exists: experimental outcomes (binding affinity, expression levels, stability) contain learnable patterns that could guide generation toward validated design regions—if we can inject this feedback without breaking the geometric symmetries essential to protein structure.

## Main Idea
We propose Equivariant Feedback Adapters (EFA)—lightweight SE(3)-equivariant modules that inject experimental feedback into frozen protein generative models. The core mechanism: encode experimental outcomes (success/failure, binding affinity) as scalar invariants, then inject these through adapter layers at Invariant Point Attention modules. Scalar invariants modulate feature magnitudes to bias generation toward experimentally successful regions while mathematically preserving SE(3) equivariance.

Using contrastive learning on 50-100 design-outcome pairs, EFA learns discriminative patterns from experimental feedback. We predict ≥2x improvement in wet-lab success rates and 50% reduction in experimental rounds needed. Key validation includes equivariance preservation tests (<1% error) and controlled comparisons against unconditional generation and fine-tuning baselines across protein targets (PD-L1 binders, GFP variants). This approach enables rapid, sample-efficient iteration between computation and experiment.
# 1. Introduction

Large language models generate confident but factually incorrect statements, a phenomenon termed *hallucination* that undermines deployment in high-stakes domains. Detecting hallucinations before they reach users requires uncertainty quantification, yet current methods impose significant computational overhead. Semantic entropy clusters multiple sampled outputs for linguistic invariance but requires 5-10 forward passes per query. Probe-based methods train classifiers on hidden states, adding inference latency. Single-pass approaches using final-layer output entropy ignore the internal processing dynamics that may distinguish factual retrieval from fabrication.

We hypothesize that the *trajectory* of representations across late layers carries discriminative signal. Under this Cross-Layer Trajectory Instability (CLTI) framework, factual retrieval follows stable attractor dynamics---representations converge monotonically toward a knowledge-grounded answer. Fabrication, lacking grounded knowledge, requires iterative cross-layer constraint satisfaction, producing higher trajectory instability.

We operationalize this hypothesis with three single-pass metrics computed from layers 24-31 of LLaMA-2-7B on TruthfulQA MC1:
- **Normalized Trajectory Instability (NTI)**: variance of per-layer entropy normalized by mean entropy
- **Convergence Monotonicity Index (CMI)**: proportion of layer transitions where answer similarity increases
- **Representational Competition Index (RCI)**: top-token flip patterns across layers

Our experiments validate the core claim while refuting secondary mechanisms. NTI achieves AUROC 0.5657 on 5-fold cross-validation, exceeding the 0.55 threshold. Combined with CMI and final-layer entropy (H_L), detection improves by +7.1% AUROC (LRT p = 1.15e-05) over entropy alone. However, trajectory metrics fail on low-entropy ("confident") predictions (AUROC 0.5136, CI includes chance), and RCI flip patterns appear in >90% of both correct and incorrect responses---revealing an architectural rather than epistemic phenomenon.

These findings contribute:
1. **Existence evidence**: Single-pass trajectory features discriminate hallucinations beyond output entropy
2. **Mechanism refinement**: The signal is driven by high-uncertainty cases; confident hallucinations remain undetected
3. **Negative results**: RCI flip patterns are universal in transformer processing, informing future interpretability research

The remainder of this paper presents related work (Section 2), methodology (Section 3), experiments (Section 4), results (Section 5), discussion (Section 6), and conclusions (Section 7).

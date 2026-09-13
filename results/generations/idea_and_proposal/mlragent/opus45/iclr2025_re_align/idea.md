# Title: Causal Probing for Representational Alignment: Beyond Correlational Metrics

## Motivation
Current representational alignment metrics (RSA, CKA, etc.) measure correlational similarity between systems but fail to capture whether representations serve functionally equivalent computational roles. Two systems may have high metric similarity yet use representations differently for downstream reasoning. This disconnect limits our ability to understand *why* alignment exists and whether it indicates shared computational strategies. We need metrics that probe the causal role of representations, not just their geometric structure.

## Main Idea
I propose **Causal Alignment Probing (CAP)**, a framework that measures representational alignment through interventional rather than observational analysis. The methodology involves:

1. **Intervention Design**: Apply targeted perturbations (ablations, rotations, noise injections) to representations in both systems across matched stimuli.

2. **Behavioral Sensitivity Mapping**: Measure how each intervention affects downstream task performance in both systems, creating "causal influence profiles."

3. **Alignment via Functional Correspondence**: Define alignment as the similarity between causal influence profiles rather than raw representational geometry.

Expected outcomes include: (a) distinguishing superficial geometric similarity from genuine computational alignment, (b) identifying which representational dimensions are functionally critical across systems, and (c) providing actionable insights for increasing meaningful alignment in AI systems.

This approach bridges the gap between representational and behavioral alignment, offering a principled answer to when geometric alignment reflects shared computation versus coincidental similarity.
---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Weight Space Learning — Direct Encoder Comparison on Model Zoos"
---

# Research Brainstorm Session Results

**Session Date:** 2026-05-05
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Neural network weights as a new data modality — weight space learning for model property prediction using permutation-equivariant encoders vs. flat baselines on existing model zoo benchmarks

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

Workshop on Neural Network Weights as a New Data Modality (ICLR 2025 Workshop). The recent surge in publicly available neural network models (exceeding 1 million on HuggingFace) calls for treating model weights as a first-class data modality. The workshop addresses: weight space properties (symmetries, permutations, scaling), learning paradigms (supervised embeddings, meta-learning, graph hyper-networks; unsupervised autoencoders/hyper-representations), equivariant architectures (GNNs, neural functionals), model analysis (inferring properties from weights, interpretability, neural lineage), model synthesis/generation (weight distributions, transfer learning, model merging/pruning/task arithmetic), and applications (NeRFs/INRs, physics, backdoor detection, adversarial robustness).

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Neural Network Weights as a New Data Modality). Retrying after previous failure — ROUTE_TO_0 triggered by MUST_WORK gate FAIL on h-e1 (threshold calibration methodology caused borderline failure by construction).

---

## Lessons from Previous Attempts

### What Was Tried Before

The previous brainstorm (first attempt, same WSL input) generated a hypothesis chain structured as:
- **H-E1 (EXISTENCE):** Prove that ≥5% of model pairs in the Schurholt MNIST-CNN/CIFAR-10 zoo are "near-equivalent" (pairwise L2 output distance below a threshold) — used as a prerequisite for all downstream hypotheses
- **H-M1 (MECHANISM):** Show flat MLP/SymMLP assign inconsistent representations to near-equivalent pairs (blocked by H-E1)
- **H-M2 (MECHANISM):** Show NFN outperforms SymMLP in Spearman rank accuracy prediction (blocked by H-E1)
- **H-M3 (MECHANISM):** Show the equivariance advantage is moderated by functional diversity (blocked by H-E1)

### Why It Failed

**Root cause:** The MUST_WORK gate for H-E1 required `fraction_near_equiv > 0.05`. The threshold epsilon was calibrated at the **5th percentile** of the pairwise distance distribution — which **mathematically guarantees ~5% of pairs fall below it by construction**. The gate therefore required strictly more than what the calibration method guarantees, making it borderline unsatisfiable.

Concrete result: `fraction_near_equiv = 0.05` exactly on CIFAR-10 (200-model sample), 995/19,900 near-equivalent pairs found. Gate FAIL. All 3 downstream hypotheses cascade-failed.

### How This New Direction Avoids Those Pitfalls

1. **No self-defeating threshold calibration:** The new direction avoids existence hypotheses that require proving a minimum prevalence with a self-referential threshold. Instead, it uses direct task performance metrics (Spearman ρ, MSE) where ground-truth labels exist independently.

2. **No deep prerequisite chains:** The previous 4-hypothesis cascade (H-E1 → H-M1 → H-M2 → H-M3) meant a single borderline failure blocked everything. The new direction targets 1–2 directly testable hypotheses with no prerequisites.

3. **Direct comparison, not indirect existence proof:** Instead of first proving permutation-equivalent pairs exist (fragile prerequisite), directly compare NFN vs. flat MLP on the downstream task (accuracy prediction) — which is the actual scientific question.

4. **Absolute metric thresholds:** Gate thresholds will be based on meaningful effect sizes (e.g., delta-rho ≥ 0.05 between encoder types measured directly) rather than percentile-based existence thresholds.

---

## Session Plan

Auto-extracted from structured input + ROUTE_TO_0 failure context analysis. Research direction redesigned to avoid prerequisite chains and self-defeating thresholds.

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research components extracted from: (1) current Workshop CFP structured input covering six major topic areas, and (2) failure analysis from previous attempt (verification_state.yaml, reflection_report). Key redesign principle: target the core scientific question directly (do equivariant encoders outperform flat baselines on weight-space property prediction?) without requiring an upstream existence sub-hypothesis as a gate.

---

## Research Question Development

### Initial Question

Do permutation-equivariant weight-space encoders (Neural Functional Networks) outperform flat MLP baselines in predicting model behavioral properties (test accuracy) on existing model zoo datasets, and is this advantage measurable without requiring any self-referential threshold calibration?

### Refined Question

On existing model zoo benchmarks (Schurholt et al. MNIST-CNN and CIFAR-10 model zoos), do permutation-equivariant encoders (Neural Functional Networks) achieve significantly higher Spearman rank correlation in test accuracy prediction compared to matched-capacity flat MLP baselines, where the performance gap (delta-rho) is directly measured as the primary outcome — without any prerequisite existence sub-hypothesis?

### Detailed Sub-Questions

1. On the Schurholt et al. MNIST-CNN model zoo (~4,000 models) and CIFAR-10 zoo (~1,500 models), does a matched-capacity (~500K parameter) NFN encoder achieve higher Spearman rank correlation in test accuracy prediction than a flat MLP baseline, with delta-rho ≥ 0.05 and bootstrap 95% CI lower bound > 0?
2. Does the permutation-equivariant advantage (delta-rho) hold consistently across both MNIST-CNN and CIFAR-10 zoos, or is it dataset-specific — testable using the same existing model zoo benchmarks and standard classification accuracy as the prediction target?
3. (Optional) Does a symmetrized MLP (Deep Sets-style permutation invariant) intermediate baseline fall between flat MLP and NFN in Spearman rank correlation, suggesting a continuous spectrum from no symmetry → invariance → equivariance in predictive quality?

---

## Reference Papers

*No reference papers provided - will discover in Phase 1*

Key papers to prioritize in Phase 1 search:
- Schurholt et al. (2021/2022) — model zoo datasets (MNIST-CNN, CIFAR-10 zoos with ground-truth accuracy)
- Zhou et al. (2024) — Neural Functional Networks (NFN)
- Zaheer et al. (2017) — Deep Sets (basis for symmetrized MLP baseline)
- Unterthiner et al. (2020) — predicting neural network accuracy from weights
- Eilertsen et al. (2020) — classifying the training objective of CNNs from weights

---

## Validation Results

### So What Test

Input from an established research venue (ICLR 2025 Workshop) — significance pre-validated by the community. This refined question matters because: (1) equivariant architectures are a foundational design choice for weight space learning — establishing whether they outperform non-equivariant baselines directly validates a core assumption in the field; (2) over 1M models on HuggingFace create massive demand for automated weight-space analysis tools; (3) the direct comparison (NFN vs. flat MLP vs. SymMLP) settles a concrete empirical question with no ambiguity about what constitutes success; (4) the Schurholt model zoo datasets are publicly available, enabling immediate reproducibility.

### Feasibility Check

All detailed questions can be tested immediately using existing real datasets and benchmarks:
- Schurholt et al. MNIST-CNN (~4,000 models) and CIFAR-10 (~1,500 models) model zoos are publicly available with ground-truth test accuracy labels
- NFN implementation available in the original Zhou et al. codebase; flat MLP and Deep Sets baselines are trivial to implement
- Spearman rank correlation is a standard metric, no new benchmarks required
- Bootstrap CI computation is standard (scipy/numpy)
- No new benchmarks, no human annotation, no synthetic data required
- Feasible within standard compute budget (small model zoos, CNN-scale encoders)
- **Critical fix from previous attempt:** Gate threshold is now `delta-rho ≥ 0.05` (difference between two independently measured Spearman values) — not a self-referential percentile calibration

---

## Phase 1 Input Package

<phase1-input>

### research_question
On existing model zoo benchmarks (Schurholt et al. MNIST-CNN and CIFAR-10 model zoos), do permutation-equivariant encoders (Neural Functional Networks) achieve significantly higher Spearman rank correlation in test accuracy prediction compared to matched-capacity flat MLP baselines, where the performance gap (delta-rho) is directly measured as the primary outcome — without any prerequisite existence sub-hypothesis?

### detailed_question
1. On the Schurholt et al. MNIST-CNN model zoo (~4,000 models) and CIFAR-10 zoo (~1,500 models), does a matched-capacity (~500K parameter) NFN encoder achieve higher Spearman rank correlation in test accuracy prediction than a flat MLP baseline, with delta-rho ≥ 0.05 and bootstrap 95% CI lower bound > 0?
2. Does the permutation-equivariant advantage (delta-rho) hold consistently across both MNIST-CNN and CIFAR-10 zoos, or is it dataset-specific — testable using the same existing model zoo benchmarks and standard classification accuracy as the prediction target?
3. Does a symmetrized MLP (Deep Sets-style permutation invariant) intermediate baseline fall between flat MLP and NFN in Spearman rank correlation, suggesting a continuous spectrum from no symmetry → invariance → equivariance in predictive quality?

### reference_papers
Not provided - will discover in Phase 1. Priority papers: Schurholt et al. (model zoo datasets), Zhou et al. (NFN), Zaheer et al. (Deep Sets), Unterthiner et al. (accuracy prediction from weights), Eilertsen et al. (classifying training objectives from weights).

</phase1-input>

---

## Session Insights

### Key Discoveries

- The core scientific question (do equivariant encoders outperform flat baselines in weight-space property prediction?) is directly testable without any prerequisite existence sub-hypothesis
- The previous failure was a gate design flaw (percentile-based threshold self-fulfillment), NOT a fundamental flaw in the research question — the underlying hypothesis about equivariance advantage remains scientifically valid
- Schurholt et al. model zoo datasets provide immediate testbeds with ground-truth accuracy labels, enabling direct Spearman rank correlation measurement
- The encoder comparison (flat MLP → Deep Sets SymMLP → NFN) naturally forms a 3-condition experiment: no symmetry, invariance, equivariance — a cleaner empirical design than the previous 4-hypothesis cascade
- Delta-rho (NFN Spearman ρ minus flat MLP Spearman ρ) is a direct, self-contained metric that requires no upstream computation or threshold calibration
- All feasibility constraints satisfied: existing datasets, existing benchmarks, no human evaluation, no new benchmark creation required

### Techniques Used

ROUTE_TO_0 Auto-Fill Mode — structured input extraction from ICLR 2025 Workshop CFP + failure context analysis from verification_state.yaml and reflection report

### Areas for Further Exploration

- Scaling laws for weight space learning: how does model zoo size affect equivariance advantage magnitude?
- Weight space learning for transformer architectures (beyond CNNs) — open question in WSL
- Theoretical expressivity bounds for NFN vs. Deep Sets in weight space
- Cross-architecture generalization: can representations learned on MNIST-CNN transfer to CIFAR-10 architectures?
- Backdoor detection via weight-space anomaly detection (application area not covered in main hypotheses)
- Neural lineage and model tree analysis through weight trajectories
- Model editing operations (merging, pruning, task arithmetic) via weight-space representations

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Key Phase 1 objectives:
1. Confirm availability and access to Schurholt et al. MNIST-CNN and CIFAR-10 model zoo datasets
2. Locate and review NFN (Zhou et al. 2024) implementation and Deep Sets baseline code
3. Gather literature on weight-space property prediction accuracy benchmarks (Unterthiner et al., Eilertsen et al.)
4. Identify any competing approaches to weight-space model accuracy prediction for context

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

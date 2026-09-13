# Research Idea

## Title
Group-Aware Compression via Fisher Information for Fair Model Deployment in Resource-Constrained Settings

## Motivation
Model compression is essential for deploying ML in developing countries with limited computational resources. However, standard compression methods (pruning, quantization) disproportionately harm minority group accuracy because global importance metrics are dominated by majority group gradients. This creates a critical fairness gap: compressed models deployed in resource-constrained healthcare, finance, or education systems may systematically underserve already marginalized populations. Existing fairness-aware ML focuses on training-time interventions, leaving compression-induced bias largely unaddressed.

## Main Idea
We propose Group-Aware Compression via Fisher Information Scoring (GACFIS), which computes group-conditional Fisher Information to identify "endemic features"—weights disproportionately important for minority groups but deprioritized by global metrics. The core mechanism: minority underrepresentation causes lower gradient magnitudes for minority-specific features, leading standard compression to remove these weights first. GACFIS intervenes by computing per-group importance scores and protecting endemic features during compression.

**Methodology:** Compare GACFIS against standard quantization-aware training and magnitude pruning across compression ratios (4x-16x) on fairness benchmarks (COMPAS, Adult Income, CelebA), measuring accuracy gap reduction and equalized odds improvement.

**Expected Outcomes:** >30% reduction in majority-minority accuracy gap with <5% overall accuracy cost, enabling fair ML deployment on resource-constrained devices. This directly addresses the PML4LRS goal of democratizing ML while ensuring equitable outcomes across demographic groups.
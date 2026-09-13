# Methodology

Our methodology centers on a core design principle: perturbation-based correlation analysis transforms benchmark variance from noise into signal. Standard benchmark evaluation treats run-to-run variance as measurement error to be minimized through averaging. We invert this relationship—by systematically varying intervention parameters (learning rates, random seeds, data subsets), we generate controlled variance in performance changes, enabling correlation analysis that reveals cross-dimensional coupling structure.

## Why Perturbation Analysis?

The central methodological challenge is that standard benchmark evaluation provides single point estimates per dimension. If we fine-tune a model once on TruthfulQA and measure all three dimensions, we observe three numbers—but a single observation provides no information about correlation. The perturbation approach solves this by creating a distribution of intervention outcomes: we apply the same intervention type (e.g., truthfulness-targeted LoRA) with systematic parameter variations, generating N=3-5 replicates per configuration. Each replicate produces a three-dimensional vector (ΔTruthfulness, ΔFairness, ΔRobustness). The correlation structure across these vectors reveals dimension relationships.

Why does this work? Because neural network training is stochastic—different random seeds, learning rates, and data orderings produce different optimization trajectories. In standard evaluation, this stochasticity is noise that inflates confidence intervals. In perturbation analysis, this stochasticity becomes signal: if two dimensions are coupled through shared representations, their performance changes will correlate across perturbations; if independent, changes will be uncorrelated.

## Five-Hypothesis Mechanistic Validation Chain

We validate cross-dimensional coupling through five linked hypotheses that form a mechanistic chain from existence to generalization:

**H-E1 (Existence):** Cross-dimensional effects definitively exist. We test whether interventions targeting one dimension create statistically significant correlations with other dimensions in >80% of configurations. This establishes the basic phenomenon—dimensions are not independent. We measure Pearson correlation coefficients ρ(ΔDim₁, ΔDim₂) across perturbations and test H₀: ρ=0 using Fisher's z-transformation. Success requires 100% detection with p<0.0001, confirming the effect is real and robust.

**H-M1 (Target Improvement):** Parameter updates reliably improve the target dimension. Before investigating cross-dimensional effects, we must confirm interventions work as intended. We measure whether LoRA fine-tuning on truthfulness data produces consistent positive improvement (ΔTruthfulness > 0) with statistical significance (p<0.001) and directional consistency (100% of seeds positive). This rules out the null hypothesis that interventions simply fail to modify model behavior.

**H-M2 (Representation Propagation):** Parameter updates reshape internal representations universally. We use Centered Kernel Alignment (CKA) to measure layer-wise representation similarity before and after intervention. The hypothesis predicts 100% layer coverage (all 24 layers in GPT-2 show measurable changes) because LoRA targets attention layers whose outputs feed all downstream computations. Comparing attention patterns versus residual streams tests whether coupling mechanisms concentrate in specific layer types.

**H-M3 (Selective Coupling):** Representation changes affect multiple dimensions selectively, not universally. This is the core hypothesis—we predict dimension-pair-specific correlation patterns rather than uniform coupling. We measure all three dimension pairs (truthfulness-fairness, truthfulness-robustness, fairness-robustness) and test whether correlation magnitudes differ significantly. Strong negative correlation for one pair (e.g., r=-0.997) alongside near-zero correlation for another (r=0.034) would confirm selective coupling, refuting the universal correlation hypothesis.

**H-M4 (Architectural Replication):** Correlation patterns replicate across model families for specific dimension pairs. We test three transformer variants (GPT-2 124M, OPT 350M, Pythia 410M) to determine whether patterns are architecture-agnostic. Success requires directional consistency (e.g., fairness-robustness negative correlation) in ≥67% of models (2/3). This establishes boundary conditions—which patterns generalize and which are model-specific.

## Why LoRA for Controlled Intervention?

We use Low-Rank Adaptation (LoRA) as our intervention method for three reasons. First, LoRA provides parameter efficiency—updating low-rank matrices (rank r=8, alpha α=16) in attention layers rather than all parameters enables rapid experimentation across multiple models and seeds. Second, LoRA targets attention mechanisms specifically, creating a controlled intervention where we know which components are updated. This enables clean mechanistic analysis via H-M2. Third, LoRA is widely adopted in practice for post-training adaptation, making our findings directly relevant to production trustworthiness workflows.

The alternative—full fine-tuning—updates all parameters, creating stronger but less interpretable interventions. Prompt tuning updates only input representations, potentially missing deeper coupling mechanisms. Adversarial training explicitly optimizes for robustness, confounding single-dimension intervention analysis. LoRA balances control, interpretability, and practical relevance.

## Why These Three Dimensions?

We focus on truthfulness (TruthfulQA), fairness (BBQ), and robustness (ANLI) for four reasons. First, these dimensions have established benchmarks with ground truth labels, enabling automated evaluation without human annotation. Second, they span diverse capability types: truthfulness measures factual knowledge, fairness measures bias suppression, robustness measures adversarial reasoning—maximizing the chance of detecting selective coupling if it exists. Third, all three benchmarks integrate with standard evaluation frameworks (lm-evaluation-harness), ensuring reproducibility. Fourth, experimental tractability: three dimensions yield three pairwise correlations; adding privacy, safety, and explainability would require six dimensions with 15 pairs, multiplying compute costs prohibitively.

## Connecting Design to Key Insight

The methodology directly enables our key insight: selective coupling emerges because perturbations reveal which dimension pairs share representation substrates. If fairness and robustness both map to contextual reasoning mechanisms in attention layers, their performance changes will correlate negatively when LoRA updates those layers (improving one degrades the other through competition). If truthfulness maps to factual knowledge retrieval in feedforward layers while fairness maps to bias suppression in attention, their performance changes will be uncorrelated despite universal layer changes. The perturbation analysis makes this coupling structure visible by generating variance in the right parameter space—targeted dimension improvements—and measuring co-variance in non-targeted dimensions.

This design differs fundamentally from standard evaluation (single intervention, no variance for correlation) and multi-task learning (joint optimization obscures single-task effects). By treating intervention variance as signal rather than noise, we reveal the hidden structure of cross-dimensional trustworthiness dynamics.

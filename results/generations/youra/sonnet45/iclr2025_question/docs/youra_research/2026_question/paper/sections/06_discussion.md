# Discussion

## Key Findings Interpretation

Our experiments establish that seed-based variance is measurable, task-dependent, and mechanistically explained through a validated causal chain. The N≥30 criterion from Rajput and Kumar (2023) holds for variance *detection* (statistical significance testing) but requires refinement for *precision* (stable quantitative estimation), a distinction missing from prior work but crucial for deep learning applications.

**Task-dependency dominates:** The 10× variance scaling between MNIST (0.04%) and Fashion-MNIST (0.35-0.59%) reflects a fundamental ceiling constraint—easy tasks with >95% accuracy compress variance into <5% absolute range. This finding provides empirical guidance: variance measurement infrastructure is practical for medium-difficulty tasks (80-95% baseline accuracy) but ceiling-compressed for easy tasks (>95%).

**Mechanism fully validated:** The complete causal chain (seed → independent weights → different trajectories → different minima → measurable variance) is supported by overwhelming statistical evidence (p < 10⁻⁶ at each step). This mechanistic understanding enables prediction: deeper architectures will show higher variance (confirmed: 2-layer shows ~2× increase), tasks near accuracy ceiling will show compressed variance (confirmed: MNIST 0.04% vs. Fashion-MNIST 0.35-0.59%).

**Detection-vs-precision boundary:** N=30 provides sufficient power for detecting non-zero variance (p<0.05, consistent with Rajput et al.'s criterion) but insufficient stability for precise quantification (bootstrap CI widths 93-110% vs. 50% threshold). This refines existing theory: sample size requirements differ for hypothesis testing (N=30) vs. narrow estimation (N>50 for neural networks).

## Honest Limitations and Mitigation Strategies

### Limitation 1: N=30 Insufficient for Bootstrap Precision

**What:** Bootstrap confidence interval widths (93-110%) significantly exceed the 50% stability threshold.

**Why this matters:** Users of this baseline must acknowledge measurement uncertainty when citing specific variance values (σ²=0.35%) or increase sample size for narrower estimates.

**Root cause:** Low baseline variance (~0.009) in neural network training contexts amplifies bootstrap sampling uncertainty. Rajput et al.'s criterion, derived for general ML tasks with larger effect sizes, does not guarantee bootstrap stability for deep learning variance measurement.

**Why acceptable:** Variance *detection* remains validated (p<0.05)—we successfully established that variance exists and is statistically distinguishable from zero. The precision limitation is a quantitative refinement (collect more seeds), not a qualitative invalidation (variance is unmeasurable).

**Future mitigation:** N sensitivity analysis—replicate H-E1 and H-M3 with N ∈ {50, 100, 200}, plot CI width vs. N to identify threshold where width ≤50%. Expected outcome: N=100-150 sufficient based on bootstrap theory (CI width scales as ~1/√N).

### Limitation 2: MNIST Ceiling Effect

**What:** MNIST achieves 98% accuracy, leaving minimal room (<2% absolute range) for cross-seed variance. Measured variance (0.04-0.06%) falls below practical detectability threshold (0.3%).

**Why this matters:** Hypothesis confirmed for medium-difficulty tasks but not applicable to easy tasks—scope boundary identified rather than universal baseline established.

**Root cause:** Task difficulty inherent to dataset choice. MNIST is a pedagogical dataset explicitly designed to be "solved" by simple methods.

**Why acceptable:** We successfully identified task-dependency as a scientific finding rather than hiding negative results. The dual-dataset design (MNIST + Fashion-MNIST) was specifically intended to test this hypothesis. Discovering 10× scaling between easy and medium tasks is a contribution, not a failure.

**Future mitigation:** Extend to intermediate-difficulty datasets—add KMNIST (~92% baseline), EMNIST (~89%)—to systematically map variance vs. accuracy relationship. Expected outcome: variance increases monotonically as baseline accuracy decreases from 98% to 80%, with inflection point around 95%.

### Limitation 3: Architecture Scope Limited to Simple MLPs

**What:** Validation limited to 1-layer (196K params) and 2-layer (400K params) fully-connected networks. Variance dynamics may differ for deeper architectures (CNNs, ResNets, Transformers).

**Why this matters:** Extension to production-scale architectures requires new empirical validation. The ~2× variance increase we observe (2-layer vs. 1-layer) may not extrapolate linearly to 50-layer ResNets.

**Root cause:** Scope decision to establish simplest baseline first before scaling to complex architectures, following progressive validation strategy.

**Why acceptable:** Clearly scoped to "simple MLPs" with explicit extension path identified. Picard et al. (2021) demonstrated feasibility on CIFAR-10 ResNet-18, providing existence proof for CNN extension.

**Future mitigation:** CIFAR-10 CNN validation—replicate protocol with ResNet-18 or VGG-like architecture. Expected computational cost: ~40 GPU-hours (30 seeds × 200 epochs × 5 min). Expected outcome: variance magnitude 0.5-2% (higher than Fashion-MNIST due to task difficulty ~93% baseline), confirming protocol generalizability.

### Limitation 4: Bootstrap i.i.d. Assumption Potentially Violated

**What:** Bootstrap resampling assumes independent and identically distributed (i.i.d.) samples. Our 30 training runs share dataset/optimizer/architecture—only random seed differs, potentially violating i.i.d. assumption.

**Why this matters:** If assumption violated, bootstrap CIs may be biased (potentially contributing to the 93-110% widths observed in H-M3). The question: are wide CIs a sample size issue (N=30 too small) or an i.i.d. violation issue (bootstrap inappropriate)?

**Root cause:** Phase 2A proposed statistical triangulation (bootstrap + permutation + Bayesian) to validate assumption robustness, but only bootstrap was implemented in Phase 4 due to scope constraints.

**Why acceptable:** Does not affect core variance detection findings (H-E1, H-M1, H-M2 pass)—only precision measurement (H-M3) impacted. Robustness validation is post-hoc analysis requiring no new experiments (data already collected).

**Future mitigation:** Statistical triangulation—compare bootstrap CIs with (1) permutation test confidence intervals and (2) Bayesian hierarchical model credible intervals on existing H-E1 data. If all three methods produce similar widths (~90-110%), i.i.d. violation is negligible and N=30 is insufficient. If bootstrap shows wider CIs than permutation/Bayesian, i.i.d. violation contributes and bootstrap may be inappropriate for this context. Expected computational cost: 2-3 hours coding + analysis.

## Broader Implications

### For Uncertainty Quantification Research

This work provides calibration infrastructure for complex UQ methods. Researchers developing MC Dropout, Bayesian NNs, or ensemble methods can now answer: "Does my method capture uncertainty beyond seed-based initialization variance?"

**Calibration protocol:**
1. Measure seed-based variance σ²_seed using our validated protocol (N=30 for detection)
2. Measure method-specific variance σ²_method
3. Compare: If σ²_method ≈ σ²_seed, method captures only initialization uncertainty (baseline)
4. If σ²_method > σ²_seed, method adds epistemic/aleatoric uncertainty beyond initialization (validate via ablation)

**Example:** Suppose MC Dropout reports 0.8% uncertainty on Fashion-MNIST. Our baseline: σ²_seed = 0.35-0.59%. Interpretation: At least 44-74% of reported uncertainty comes from initialization alone. The remaining 26-56% reflects dropout-induced epistemic uncertainty—quantifying method contribution.

### For Reproducibility and Model Selection

Practitioners reporting mean ± std across N seeds can now assess: "Is my sample size sufficient?" and "Is observed variance within expected range?"

**Sample size guidelines:**
- N=30 for significance testing (p<0.05) — confirms variance exists
- N>50 for precise quantification (bootstrap CI ≤50%) — narrow estimation
- N=3-5 (common practice) — likely underpowered for both detection and precision on medium-difficulty tasks

**Variance benchmarks by task difficulty:**
- Easy tasks (>95% accuracy): Expect σ ≤ 0.1% (ceiling effect)
- Medium tasks (80-95% accuracy): Expect σ = 0.3-0.8% (practical detectability)
- Hard tasks (<80% accuracy): Unknown—extrapolation beyond validated range

### Conceptual Contribution: Detection vs. Precision

We identify a distinction missing from Rajput et al. (2023) but critical for deep learning applications:

**Detection (hypothesis testing):** "Is variance significantly non-zero?" — Requires power ≥0.85 for p<0.05 test. Rajput's N≥30 criterion applies here.

**Precision (interval estimation):** "What is variance magnitude with narrow confidence intervals?" — Requires additional samples for bootstrap stability (CI width ≤50%). N>50 likely required for neural networks.

This conceptual separation guides future experimental design: use N=30 for exploratory studies confirming variance exists, but N>50 for precise benchmarking and method comparison.

## Future Directions

### Immediate Extensions (High Feasibility)

**1. N sensitivity analysis** — Validate detection-vs-precision boundary by testing N ∈ {50, 100, 200} and plotting CI width vs. N. Identifies minimum N for stable estimation in neural network contexts. (Cost: ~1 week, replicating H-E1+H-M3)

**2. Statistical triangulation** — Compare bootstrap, permutation test, and Bayesian hierarchical model on existing H-E1 data to validate i.i.d. assumption robustness. If methods disagree, identifies which statistical assumptions matter for neural network variance. (Cost: 2-3 hours, post-hoc analysis)

**3. Task difficulty gradient** — Add intermediate datasets (KMNIST ~92%, EMNIST ~89%) to systematically map variance vs. baseline accuracy relationship. Tests whether 10× scaling extrapolates beyond MNIST/Fashion-MNIST. (Cost: 1-2 weeks, 3-5 additional datasets)

### Longer-Term Vision

**Comprehensive variance atlas** — Systematic benchmarking across architectures (MLPs, CNNs, ResNets, Transformers), tasks (image classification, NLP, RL), and training regimes (short/long, with/without regularization). Goal: "variance reference manual" for the deep learning community.

**MC Dropout calibration study** — Demonstrate baseline usage by comparing MC Dropout uncertainty estimates with our classical baseline. Quantify: how much of MC Dropout's reported uncertainty is seed-based vs. dropout-induced?

**Integration into MLOps pipelines** — Develop automated variance monitoring tools for model deployment. Alert engineers when observed variance exceeds expected baseline (potential training instability) or falls below baseline (insufficient exploration of initialization space).

### Open Questions

1. **Loss landscape hypothesis:** Does flatness (Hessian eigenvalue spectrum) drive task-dependency, or is ceiling effect sufficient explanation? Requires Hessian analysis comparing MNIST vs. Fashion-MNIST final models.

2. **Per-epoch variance evolution:** Does variance plateau early (epoch 3) or continue growing through training (epoch 10)? Requires tracking σ²(epoch) at intermediate checkpoints.

3. **Ensemble variance reduction:** Do ensembles of N models (each with different seed) reduce variance below single-seed baseline? Tests whether ensemble diversity amplifies or cancels seed-based stochasticity.

4. **Minimum N for 50% CI width:** What sample size crosses the bootstrap stability threshold in neural network contexts? N sensitivity analysis will answer this empirically.

## Broader Impact Statement

This work provides calibration infrastructure for uncertainty quantification methods, improving machine learning reliability engineering.

**Potential positive impact:** Better-calibrated uncertainty estimates for high-stakes applications (medical diagnosis, autonomous systems, scientific discovery). When models report confidence intervals, practitioners will have validated baselines to assess whether reported uncertainty is reasonable.

**Potential negative impact:** Misuse if scope limitations ignored—applying variance benchmarks to tasks outside validated range (>95% accuracy with ceiling effects, or deep CNNs without empirical validation) may yield misleading calibration. Users must respect scope boundaries.

**No direct societal harms anticipated:** This is methodological infrastructure work, not a deployed system. Indirect benefits (improved UQ calibration) may enhance safety-critical ML applications.

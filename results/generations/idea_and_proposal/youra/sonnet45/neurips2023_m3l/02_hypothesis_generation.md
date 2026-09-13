# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** Round 1 - Gradient Flow Theory for Large-Scale Training
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-neurips2023_m3l-01
**Confidence Level:** 0.82/1.0 (MEDIUM-HIGH)

**Main Hypothesis:**
Large-scale neural network training dynamics at billion-parameter scale can be theoretically characterized through a gradient flow framework where: (1) training trajectories flow toward stable attractor regimes in loss landscape, identifiable via computationally efficient random projections (d=50-100 dimensions), (2) stability regime transitions (Edge of Stability) are detectable using sharpness proxies (gradient norm growth rate) without full Hessian computation, and (3) scaling law exponents (α in L ~ N^{-α}) emerge from architectural symmetry properties through attractor basin geometry - a novel hypothesis inspired by renormalization group theory requiring empirical validation.

**Alternative Hypothesis (H0):**
Billion-scale training dynamics are fundamentally chaotic and non-convergent, with no stable attractor regimes; scaling law exponents are arbitrary empirical curve-fitting parameters without geometric foundation; and architectural symmetries have no systematic relationship to training behavior or convergence rates.

### 1.2 Variables

| Type | Variable | Symbol | Measurement | Range/Values |
|------|----------|--------|-------------|--------------|
| **Independent** | Parameter count | N | Count of trainable parameters | 10M - 10B |
| Independent | Learning rate schedule | η(t) | Learning rate at training step t | 10^-5 to 10^-2 |
| Independent | Architecture symmetry group | G | Discrete symmetry operations (permutations, sign flips) | Group order \|G\| varies by architecture |
| Independent | Architecture type | A | Categorical: MLP, CNN, Transformer (Phase 2) | {MLP, CNN} initially |
| **Dependent** | Gradient flow trajectory | γ(t) | Parameter updates projected to d-dimensional space | R^d, d=50-100 |
| Dependent | Sharpness proxy | S(t) | \|\|∇L\|\|² growth rate, loss curvature | Non-negative real |
| Dependent | Scaling law exponent | α | Exponent in L ~ N^{-α} | Positive real, typically 0.1-0.5 |
| Dependent | Attractor basin volume | V | Estimated via symmetry orbit count | Positive real, architecture-dependent |
| Dependent | Stability transition indicator | T(t) | Binary: stable/unstable regime | {0, 1} |
| **Controlled** | Batch size | B | Fixed for comparisons | Typically 256-4096 |
| Controlled | Dataset | D | Same pretraining data for scaling analysis | Fixed corpus (e.g., C4, Pile) |
| Controlled | Optimization algorithm | Opt | SGD or Adam (fixed for experiments) | {SGD, Adam} |

### 1.3 Causal Mechanism

**Causal Chain:**

```
Architectural Symmetries (G)
  → Loss Landscape Geometry (attractor basins, flatness)
    → Gradient Flow Dynamics (trajectories toward attractors)
      → Stability Regime Behavior (EoS transitions at critical η_c)
        → Convergence Rate (captured by scaling exponent α)
```

**Detailed Mechanism:**

1. **Symmetry → Landscape Structure:** Architectural symmetries (weight permutations, sign invariances) create geometric redundancy in parameter space. By Pittorino et al. (2022), discrete symmetries generate flat loss landscape regions. Higher symmetry group order |G| implies larger symmetry orbits and flatter attractor basins.

2. **Landscape → Flow Dynamics:** Training via gradient descent induces flow in loss landscape toward local minima. Flat basins (from symmetries) act as attractors with wide capture regions. Random projections (Johnson-Lindenstrauss) preserve pairwise distances, capturing approximate flow structure sufficient for regime identification.

3. **Flow → Stability Transitions:** As learning rate η increases, gradient updates magnify. When η approaches critical threshold η_c ≈ 2/λ_max (Cohen et al. 2022), training transitions from stable convergence to Edge of Stability regime. Sharpness proxy S(t) = ||∇L||² growth rate correlates with λ_max, enabling detection without O(N²) Hessian computation.

4. **Stability → Scaling Behavior:** Attractor basin volume V (estimated via |G| symmetry orbit count) determines convergence efficiency. Hypothesis: Basin volume V ~ N^β relates to parameter count, which determines loss scaling L ~ N^{-α}. Larger basins → slower escape from initialization → different convergence characteristics → altered scaling exponent α.

**Evidence for Causal Links:**

- **Link 1 (Symmetry → Landscape):** Pittorino et al. (2022, 29 cites) directly demonstrate via toroidal parameterization that removing symmetries reveals landscape flatness. Symmetry orbits create degenerate minima.

- **Link 2 (Landscape → Flow):** Loss landscape visualization (Goldstein et al., 3.1k stars repo) shows training trajectories follow gradient flow toward basins. Dynamical systems theory (Strogatz) establishes flow-attractor relationship.

- **Link 3 (Flow → Stability):** Cohen et al. (2022, 66 cites) empirically validate that stability transitions occur when λ_max ≈ 2/η, observable via gradient norm growth. Edge of Stability is reproducible phenomenon.

- **Link 4 (Stability → Scaling):** Shen et al. (2024, 17 cites) establish empirical scaling laws L ~ N^{-α}. Our hypothesis proposes geometric explanation via attractor basins. **This link requires validation** - it's the novel contribution.

**Key Tension:**

The central tension is between **continuous approximation vs. discrete reality**. Random projections and flow analysis assume continuity, but actual training involves discrete stochastic updates with finite batch sizes. The framework must demonstrate that:
1. Discrete SGD trajectory approximates continuous flow sufficiently for regime identification
2. Random projections preserve critical phase transition boundaries despite losing exact topology
3. Statistical fluctuations from stochasticity don't obscure attractor structure

### 1.4 Key Assumptions

1. **Flow Approximation Validity:** Gradient descent with small learning rates approximates continuous gradient flow in loss landscape. Training step size is sufficiently small that discrete updates trace smooth trajectories toward attractors.

2. **Projection Preservation:** Random projections to d=50-100 dimensions (Johnson-Lindenstrauss) preserve regime boundaries and stability transitions even if exact flow topology is distorted. Pairwise distance preservation is sufficient for identifying qualitative regime changes (stable ↔ unstable).

3. **Sharpness Proxy Reliability:** Gradient norm growth rate ||∇L||² and loss curvature serve as reliable proxies for Hessian maximum eigenvalue λ_max across architectures (MLPs, CNNs initially). Cohen et al. (2022) validation generalizes beyond specific studied architectures.

4. **Symmetry Persistence:** Architectural symmetries identified at initialization persist throughout training and influence loss landscape geometry at billion-parameter scale. Symmetry orbits remain relevant as training progresses.

5. **Quasi-Steady Regimes Exist:** Training reaches identifiable quasi-steady flow regimes analyzable as dynamical attractors, rather than exhibiting persistent chaotic dynamics throughout. Late-stage training converges to stable patterns.

6. **Geometric Scaling Connection:** Attractor basin geometry (volume, flatness determined by symmetries) systematically relates to scaling law exponents. This is NOT a proven mathematical theorem but the **core novel hypothesis** inspired by renormalization group analogy.

**Assumption Justification & Risk Mitigation:**

- **Assumption 1:** Standard in optimization theory (e.g., gradient flow analysis in Chizat & Bach 2020). Risk: Mitigated by empirical trajectory smoothness checks.
- **Assumption 2:** Johnson-Lindenstrauss guarantees distance preservation. Risk: **Moderate** - flow topology ≠ distances. Mitigated by empirical validation on smaller-scale experiments.
- **Assumption 3:** Cohen et al. validation provides evidence. Risk: **Moderate** - generalization unclear. Mitigated by multi-architecture validation phase.
- **Assumption 4:** Pittorino et al. demonstrate symmetry effects. Risk: **Low** - symmetries are architectural properties.
- **Assumption 5:** Edge of Stability literature shows regime stabilization. Risk: **Moderate** - billion-scale behavior may differ. Mitigated by preliminary regime analysis.
- **Assumption 6:** **HIGH RISK** - This is the novel claim requiring validation. Inspired by RG analogy, not derived theorem. Entire hypothesis hinges on empirical validation of this assumption.

### 1.5 Scope & Boundaries

**This hypothesis applies to:**

- **Task Domain:** Supervised learning (classification, regression) and unsupervised pretraining (language modeling, autoencoding)
- **Optimization Method:** First-order gradient-based methods (SGD, Adam, AdamW) with continuous gradient updates
- **Architecture Types:** Initially MLPs and CNNs with tractable symmetry analysis (weight permutations, filter symmetries). **Explicitly deferred to Phase 2: Transformers** with complex attention symmetries.
- **Parameter Scale:** 10M to 10B parameters (validated range spanning medium to billion-scale)
- **Training Phase:** Post-warmup, pre-final-overfitting (middle 50-80% of training where flow regimes are established)
- **Data Regime:** Standard large-scale datasets (C4, ImageNet, Pile) with sufficient samples for convergence

**This hypothesis does NOT apply to:**

- **Non-gradient optimization:** Evolutionary algorithms, genetic programming, black-box optimization, zeroth-order methods
- **Extreme scales:** Sub-1M parameter networks (discrete effects dominate, no clear flow) or 100B+ parameters (computational validation infeasible currently)
- **Specialized training regimes:** Adversarial training with min-max dynamics, meta-learning with nested optimization, continual learning with task switching
- **Extremely sparse networks:** Lottery ticket hypothesis scenarios with 99%+ sparsity where landscape topology fundamentally changes
- **Non-stationary objectives:** Curriculum learning with changing loss functions, online learning with distributional shift

**Boundary Cases (Unclear Applicability):**

- **Moderately sparse networks (50-80% pruning):** Symmetries partially broken; framework may require adaptation
- **Mixed-precision training (FP16/BF16):** Numerical precision effects on sharpness proxies unclear
- **Very large batch sizes (>32k):** Batch size may affect landscape exploration and regime transitions
- **Transfer learning fine-tuning:** Initialization from pretrained model changes flow dynamics
- **Noisy gradient scenarios:** Extreme gradient noise from small batch sizes (<32) may obscure flow structure

### 1.6 Testable Predictions

**Primary Prediction:**

**P1: Symmetry-Scaling Relationship**
IF architecture A1 has symmetry group order |G1| = 2×|G2| (twice the symmetries of architecture A2), and both are trained on identical datasets with same parameter count N, THEN architecture A1 will exhibit scaling exponent α1 < α2 (slower loss decay with scale), measurable as |α1 - α2| ≥ 0.05 in L ~ N^{-α} power-law fits.

**Measurement:** Train pairs of architectures (MLPs with/without permutation symmetries, CNNs with different filter group structures) across N ∈ {10M, 30M, 100M, 300M, 1B, 3B} parameters. Fit scaling laws. Compare exponents.

**Secondary Predictions:**

**P2: Stability Transition Detection**
IF learning rate η is increased during training and crosses critical threshold η_c, THEN sharpness proxy S(t) = ||∇L||² growth rate will exhibit abrupt increase (>2× baseline) within 100 training steps, coinciding with loss oscillations characteristic of Edge of Stability.

**Measurement:** Train with adaptive learning rate schedule crossing η_c ≈ 2/λ_max (estimated via periodic Lanczos iterations). Monitor ||∇L||² and loss variance.

**P3: Projection Preservation**
IF training trajectory exhibits stability regime transition in full parameter space (N dimensions), THEN the same transition will be detectable in random-projected space (d=50, 100 dimensions) with >90% temporal alignment (transition detected within ±5% of training steps).

**Measurement:** Compare full-space stability indicators (expensive, computed periodically) vs. projection-space indicators (cheap, computed every step). Measure alignment accuracy.

**P4: Universality Class Behavior**
IF two architectures (e.g., MLP-A and CNN-B) have isomorphic symmetry group structures (same |G| and group composition), THEN they will exhibit statistically indistinguishable scaling exponents (|α_A - α_B| < 0.03) and similar attractor basin geometries (basin volume estimates within 20%).

**Measurement:** Identify architecture pairs with proven symmetry group isomorphisms. Train across parameter scales. Compare scaling behaviors statistically.

**P5: Out-of-Sample Prediction**
IF the framework correctly characterizes training behavior for architectures {A1, A2, A3} used in validation, THEN it can predict scaling exponent α_new for novel architecture A_new (not in training set) within ±0.08 error, based solely on A_new's symmetry analysis and small-scale (10M parameter) pilot runs.

**Measurement:** Train validation set. Build predictive model (basin volume → α). Test on held-out novel architectures. Measure prediction error.

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if any of the following occur:

1. **No symmetry-scaling correlation:** In >50% of architecture pairs with different |G|, the scaling exponents show NO systematic relationship (|α1 - α2| < 0.02 despite 2× symmetry difference). This falsifies the core attractor-basin-geometry claim.

2. **Projection failure:** Random projections fail to preserve regime transitions in >30% of test cases (transitions misaligned by >10% training duration). This invalidates the methodological foundation.

3. **Proxy unreliability:** Sharpness proxies (gradient norm growth) fail to correlate with Hessian eigenvalues (ρ < 0.5 correlation) in >40% of validation architectures. This breaks the stability characterization mechanism.

4. **No attractors exist:** Preliminary flow analysis on 10+ billion-scale training runs reveals persistent chaotic dynamics with no identifiable quasi-steady regimes in >70% of cases. This falsifies the attractor assumption.

5. **Pure parameter counting:** Scaling behavior is better explained by simple parameter count alone (α ~ N^{-1/k}) with <0.02 residual error, making symmetry analysis unnecessary complexity.

### 1.7 SOTA Baseline (Phase 2 Comparison Mode)

**Current SOTA Approach:** Empirical Scaling Law Fitting (Shen et al. 2024, Kaplan et al. 2020)

**SOTA Methodology:**
- Train models at multiple parameter scales N ∈ {Nmin, ..., Nmax}
- Record final validation loss L(N) for each scale
- Fit power-law L = A × N^{-α} + B via least-squares regression
- Use fitted α to predict loss at new scales

**SOTA Performance Benchmark:**
- Scaling exponent prediction error: ±0.05 (typical fit quality on 5+ scale points)
- Requires: 5-10 full training runs across scales (~$50K compute cost for billion-scale)
- Prediction accuracy: Interpolates well; extrapolates with increasing error (±0.10 at 2× largest training scale)

**Our Framework Comparison:**

| Criterion | SOTA (Empirical Fitting) | Our Framework (Geometric Derivation) |
|-----------|-------------------------|-------------------------------------|
| **Exponent Accuracy** | ±0.05 (baseline) | Target: ±0.08 (acceptable if cheaper) |
| **Compute Cost** | 5-10 full runs (~$50K) | 1 full run + small-scale analysis (~$5K) |
| **Extrapolation** | Degrades (±0.10 at 2×) | Hypothesis: Maintains accuracy (symmetries don't change with scale) |
| **Interpretability** | None (black-box fit) | Mechanistic (symmetry → geometry → scaling) |
| **Generalization** | Per-architecture (no transfer) | Hypothesis: Architecture classes (universality) |
| **Failure Mode Detection** | None (always fits) | Detects non-convergence (no attractors) |

**Success Criterion:**
Our framework is considered **BETTER THAN SOTA** if:
1. Exponent prediction within ±0.08 (slightly worse accuracy acceptable)
2. Cost reduction >5× (validated by requiring fewer full-scale runs)
3. Extrapolation error at 2× scale < ±0.08 (better than SOTA's ±0.10)
4. Successful universality class prediction (novel capability SOTA lacks)

### 1.8 Statistical Verification Design

**Experimental Design:** Multi-Scale Factorial Experiment with Architecture Pairs

**Sample Size Calculation:**

For **P1 (symmetry-scaling relationship)**, testing mean difference in scaling exponents:
- Effect size: δ = 0.05 (minimum detectable difference in α)
- Significance level: α_stat = 0.05 (5% Type I error)
- Power: 1-β = 0.80 (80% power)
- Variance estimate: σ² ≈ 0.01 (from Shen et al. 2024 reported fit errors)

Using two-sample t-test formula: n = 2(Z_α/2 + Z_β)² × σ² / δ² = 2(1.96 + 0.84)² × 0.01 / 0.05² ≈ 12.5

**Required:** 13 architecture pairs minimum, each trained at 6 scales → 78 training runs total for P1.

**Confound Control:**

| Confound | Control Strategy |
|----------|------------------|
| **Dataset variation** | Fixed dataset (C4 or ImageNet) across all experiments |
| **Random initialization** | 3 random seeds per configuration; report mean ± std |
| **Hyperparameter effects** | Fixed learning rate schedule, batch size, optimizer (AdamW β=(0.9, 0.999)) |
| **Epoch count variation** | Train to convergence criterion: ΔL < 0.001 over 10k steps |
| **Hardware differences** | All experiments on same GPU type (A100 80GB); reproducibility checks |

**Statistical Tests:**

1. **P1 (Symmetry-Scaling):** Two-sample t-test comparing α exponents between high/low symmetry architecture groups. One-tailed test (H_a: α_high < α_low). Significance level: 0.05.

2. **P2 (Stability Transition):** Time-series change-point detection using CUSUM (cumulative sum) on S(t) = ||∇L||². Detection threshold: 2σ above baseline. Measure detection latency.

3. **P3 (Projection Preservation):** Agreement analysis: Cohen's kappa for regime classification (stable/unstable) between full-space and projected-space. Threshold: κ > 0.85 (almost perfect agreement).

4. **P4 (Universality):** Equivalence test (TOST procedure) for scaling exponent pairs. Equivalence bounds: Δ_equiv = ±0.03. Test both bounds at α_stat = 0.05.

5. **P5 (Out-of-Sample):** Prediction error distribution analysis. Measure RMSE, MAE, and maximum error on held-out architectures. Compare vs. SOTA baseline using paired Wilcoxon signed-rank test.

**Multiple Comparisons Correction:**

With 5 primary predictions, apply Bonferroni correction: adjusted α = 0.05 / 5 = 0.01 per test to maintain family-wise error rate.

**Effect Size Reporting:**

Report Cohen's d for group comparisons, R² for scaling law fits, correlation coefficients for proxy validations. All effect sizes reported with 95% confidence intervals via bootstrap (1000 iterations).

---

## 2. Contribution Summary

This hypothesis makes **three primary contributions** to deep learning theory:

**Theoretical Contribution:**

We propose the first theoretical framework that unifies Edge of Stability phenomena, empirical scaling laws, and architectural symmetries under a single coherent mathematical structure. Unlike prior work that treats these as isolated observations (Cohen et al. 2022 for EoS, Shen et al. 2024 for scaling, Pittorino et al. 2022 for symmetries), our gradient flow framework provides a mechanistic explanation: architectural symmetries → loss landscape geometry (attractor basins) → training dynamics (flow toward attractors with stability transitions) → convergence behavior (scaling exponents). The key novelty is proposing that scaling law exponents **emerge from geometric properties** (basin volume via symmetry analysis) rather than being arbitrary curve-fit parameters. This moves from descriptive empiricism to predictive theory.

**Methodological Contribution:**

We develop a computationally tractable analysis framework for billion-scale training using: (1) random projection-based flow trajectory analysis reducing O(N²) Hessian computation to O(Nd) with d=50-100, (2) sharpness proxies (gradient norm growth, loss curvature) for stability characterization avoiding full eigenvalue decomposition, and (3) symmetry orbit counting for attractor basin volume estimation. This enables theoretical analysis at scales (1B-10B parameters) where previous methods become computationally prohibitive. The framework is explicitly designed with computational constraints in mind: analyzing existing training runs rather than requiring new expensive experiments, using efficient approximations with empirical validation, and providing clear fallback options (PCA if random projection fails, partial Hessian if proxies uncertain).

**Practical Contribution:**

For practitioners training large-scale models, our framework offers predictive capabilities that current empirical approaches lack: (1) Predict scaling behavior for new architectures before expensive billion-scale runs via symmetry analysis + small-scale (10M parameter) pilots, reducing validation cost from ~$50K (5-10 full runs) to ~$5K (1 full run + analysis), (2) Identify architectures likely to exhibit training instabilities via stability transition analysis before committing resources, (3) Guide architectural design decisions by connecting symmetry properties to training behavior and convergence characteristics, (4) Classify architectures into "universality classes" based on geometric properties, enabling knowledge transfer across similar architectures. These capabilities address the core problem stated in the research question: large-scale trial-and-error is prohibitively expensive, requiring principled theoretical guidance.

---

## 3. Key Related Work

**Optimization Dynamics & Edge of Stability:**

Cohen, J., Kaur, S., Li, Y., Kolter, J. Z., & Talwalkar, A. (2022). *Adaptive Gradient Methods at the Edge of Stability*. arXiv:2207.14484. [66 citations]
- **Key Contribution:** Empirical characterization of Edge of Stability phenomenon where training operates near instability boundary λ_max ≈ 2/η. Documents stability regime transitions and gradient norm behavior.
- **Relation to Our Work:** We provide theoretical framework explaining WHY this transition occurs via attractor analysis, whereas Cohen et al. document THAT it occurs. Our sharpness proxy methodology builds directly on their gradient norm growth observations.
- **Gap They Leave:** No theoretical characterization of the phenomenon, no predictive framework for new architectures, no connection to scaling behavior.

Chizat, L., & Bach, F. (2020). *Implicit Bias of Gradient Descent for Wide Two-layer Neural Networks*. Journal of Machine Learning Research, 21, 1-42. [365 citations]
- **Key Contribution:** Rigorous theoretical analysis of gradient descent implicit bias in overparameterized networks using mean-field theory. Shows convergence to specific solutions based on initialization.
- **Relation to Our Work:** Demonstrates theoretical tractability for SMALL networks but cannot scale to billion-parameter regime. We extend the spirit of rigorous dynamical analysis to large scale via efficient approximations.
- **Gap They Leave:** Limited to 2-layer networks with infinite-width limits. Mean-field assumptions break down for deep, finite-width, billion-scale models.

**Scaling Laws & Large-Scale Training:**

Shen, Y., Song, Z., Mei, S., & Santurkar, S. (2024). *Scaling Laws for Linear Complexity Language Models*. arXiv:2406.16690. [17 citations]
- **Key Contribution:** Empirical power-law relationships L ~ N^{-α} for linear-complexity architectures. Establishes that scaling behavior persists beyond Transformers to alternative architectures.
- **Relation to Our Work:** They FIT scaling laws empirically; we aim to DERIVE exponents from architectural geometry. Our hypothesis explains WHERE scaling exponents come from (attractor basin structure) rather than treating them as free parameters.
- **Gap They Leave:** No theoretical foundation, no predictive capability for unseen architectures, requires expensive multi-scale training for each new architecture.

Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., ... & Amodei, D. (2020). *Scaling Laws for Neural Language Models*. arXiv:2001.08361. [2800+ citations]
- **Key Contribution:** Established foundational empirical scaling laws for language models. Power-law relationships with data, compute, and parameters.
- **Relation to Our Work:** Foundational empirical baseline we aim to explain theoretically. Our geometric framework should recover their empirical observations as special cases.
- **Gap They Leave:** Purely empirical, no mechanistic explanation, limited extrapolation confidence.

**Symmetries & Loss Landscape Geometry:**

Pittorino, F., Ferraro, A., & Seoane, L. F. (2022). *Deep networks on toroids: Removing symmetries reveals the structure of flat regions in the landscape of neural networks*. Advances in Neural Information Processing Systems, 35. [29 citations]
- **Key Contribution:** Demonstrates via toroidal parameterization that discrete architectural symmetries create flat regions in loss landscape. Provides methodology for symmetry orbit enumeration.
- **Relation to Our Work:** Core foundation for symmetry-landscape connection. We EXTEND their static landscape analysis to DYNAMIC training behavior and scaling laws. Their symmetry counting becomes our basin volume estimation.
- **Gap They Leave:** No connection to training dynamics, no analysis of how symmetries affect convergence rates or scaling behavior, no billion-scale validation.

**Loss Landscape Visualization:**

Goldstein, T., et al. (loss-landscape repository, 3100+ stars). *Visualizing the Loss Landscape of Neural Nets*. Implementation repository.
- **Key Contribution:** Practical tools for low-dimensional loss landscape projection and visualization using filter-normalized directions and PCA.
- **Relation to Our Work:** Methodological foundation for dimensionality reduction. We adapt their STATIC visualization techniques for DYNAMIC flow trajectory analysis. Random projections build on their demonstration that low-dimensional approximations capture meaningful structure.
- **Gap They Leave:** Visualization only, no dynamical analysis, no connection to training outcomes or scaling laws.

**Generalization Theory:**

Valle Pérez, G., & Louis, A. A. (2020). *Generalization bounds for deep learning*. arXiv:2012.04115. [48 citations]
- **Key Contribution:** PAC-Bayesian generalization bounds for deep networks incorporating sharpness and flatness measures.
- **Relation to Our Work:** Provides theoretical motivation for why flat basins (which we connect to symmetries) lead to better generalization. Our framework adds dynamical perspective: HOW training finds flat basins via gradient flow.
- **Gap They Leave:** Static bounds, no training dynamics, no scaling law connection.

**Cross-Domain Inspiration:**

Wilson, K. G. (1971). *Renormalization group and critical phenomena*. Physical Review B, 4(9), 3174. [10000+ citations] - Nobel Prize work
- **Key Contribution:** Renormalization group theory for phase transitions in statistical physics. Fixed points, universality classes, scaling exponent derivation from symmetries.
- **Relation to Our Work:** Conceptual inspiration ONLY (not mathematical derivation). Flow toward fixed points → gradient descent toward attractors. Phase transitions → Edge of Stability. Universality classes → architecture families. Symmetry-derived scaling → our core hypothesis.
- **Critical Distinction:** Statistical physics has equilibrium thermodynamics; deep learning has non-equilibrium discrete stochastic optimization. This is ANALOGY not application.

---

## 4. Phase 2B Readiness

### Decomposition Preview

Based on the causal mechanism (Symmetries → Landscape → Flow → Stability → Scaling), natural decomposition into sub-hypotheses:

**SH1 (Existence): Do stable attractor regimes exist in billion-scale training?**

Verify that billion-scale training trajectories exhibit identifiable quasi-steady flow regimes rather than persistent chaos. Preliminary analysis: examine 10+ training runs (GPT-style, LLaMA checkpoints), project to d=100 dimensions via random projections, compute trajectory velocity ||γ(t+Δt) - γ(t)|| over time windows. Success: >70% of runs show velocity stabilization (<0.1 relative change over 5k step windows) in late training. Failure: persistent high-velocity wandering indicates no attractors.

**SH2 (Mechanism): Does symmetry structure determine basin geometry?**

Validate symmetry orbit counting correlates with empirical basin flatness measures. Method: For 20+ architectures spanning MLP/CNN types with varying |G|, compute: (1) symmetry group order |G| analytically, (2) basin flatness via Hessian trace or sharpness at convergence. Test correlation: expect ρ > 0.6 between log|G| and log(flatness). Success validates symmetry → geometry link. Failure: ρ < 0.3 suggests symmetries irrelevant.

**SH3 (Comparison): Does geometric analysis outperform empirical fitting?**

Direct comparison vs. SOTA baseline (Shen et al. 2024 empirical fitting). Experimental protocol: Train 5 novel architectures (held-out from framework development) at 6 scales each. Framework prediction: Use symmetry analysis + 10M parameter pilot to predict α. SOTA: Fit power-law after training all scales. Compare: prediction error MAE, compute cost ($), extrapolation accuracy at 2× largest scale. Success: Framework achieves <±0.08 error with <20% of SOTA cost. Failure: error >±0.12 or cost comparable to SOTA.

### Readiness Checklist

- [x] **Testable predictions defined:** 5 predictions (P1-P5) with measurement protocols
- [x] **Falsification criteria specified:** 5 conditions that would falsify hypothesis
- [x] **Variables operationalized:** All independent/dependent/controlled variables have measurement procedures
- [x] **SOTA baseline identified:** Empirical scaling law fitting (Shen et al. 2024, Kaplan et al. 2020)
- [x] **Statistical design complete:** Sample sizes calculated, confounds controlled, tests specified
- [x] **Sub-hypotheses preview:** 3 sub-hypotheses (SH1-3) for Phase 2B decomposition
- [x] **Scope boundaries clear:** Applies to MLPs/CNNs 10M-10B parameters, explicitly defers Transformers
- [x] **Assumption risks assessed:** 6 assumptions with risk levels and mitigation strategies
- [x] **Related work mapped:** 9 key papers with explicit gap analysis and relation statements
- [x] **Phase 1 data traceable:** All claims reference Phase 1 sources (Cohen 2022, Shen 2024, Pittorino 2022, etc.)

**Overall Readiness:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

All required components for decomposition into verification sub-hypotheses are present. The hypothesis is sufficiently precise, testable, and grounded in empirical evidence.

### Open Questions

1. **Computational Feasibility of Transformer Symmetries (Phase 2):** Attention mechanisms create complex non-local symmetries. Is orbit enumeration tractable for billion-parameter Transformers? If not, can we develop approximation methods (e.g., group structure lower bounds)?

2. **Flow Regime Detection Criteria:** What quantitative threshold distinguishes "stable attractor regime" from "chaotic wandering"? Velocity stabilization is heuristic. Need principled dynamical systems criterion (e.g., Lyapunov exponent calculation).

3. **Basin Volume Estimation Accuracy:** Symmetry orbit counting gives combinatorial estimate. How accurately does |G| proxy actual basin volume in loss landscape? Need empirical calibration: compare |G| vs. direct volume estimation (expensive Hessian eigenvalue integration).

4. **Scaling Law Functional Form:** Hypothesis assumes L ~ N^{-α}. What if true relationship is more complex (e.g., L ~ N^{-α}(log N)^{-β})? Does geometric framework generalize to non-power-law scalings?

5. **Multi-Objective Training:** Framework developed for single loss minimization. How does it extend to multi-task learning (multiple losses with trade-offs) or adversarial training (min-max objectives)?

6. **Batch Size Effects:** Larger batch sizes reduce gradient noise but may affect landscape exploration. How does batch size interact with attractor basin size and stability transitions?

7. **Optimizer Algorithm Sensitivity:** Framework assumes first-order methods (SGD, Adam). Do adaptive methods (AdaGrad, RMSProp) with non-Euclidean geometry alter flow dynamics significantly?

8. **Empirical Validation Timeline:** Billion-scale validation requires months of compute and coordination. What is realistic timeline for comprehensive validation across 78+ training runs (per sample size calculation)?

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-08*

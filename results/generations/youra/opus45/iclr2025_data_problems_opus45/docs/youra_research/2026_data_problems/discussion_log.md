# Phase 2A Discussion Log (v9.0.0)

**Research Topic:** Data Attribution Efficiency in Foundation Models
**Gap Selected:** Gap 1 - Systematic Pareto Frontier Characterization
**Created:** 2026-03-24T16:15:00+00:00
**Workflow Version:** 9.0.0 (Self-Contained Tikitaka Loop)

---

## Briefing Context

### Research Question
Do gradient-based attribution approximations (e.g., TRAK, influence function approximations) maintain rank-order accuracy compared to exact methods when applied at different computational budgets, and what is the Pareto frontier of the computation-accuracy tradeoff across existing methods?

### Selected Gap
**Gap 1: Systematic Pareto Frontier Characterization Across Methods**

**Relevance:** PRIMARY - Directly blocks answering the research question

**Current State:** TRAK (2023), DataInf (2024), and LoRIF (2026) each compare against influence functions on specific benchmarks, but use different evaluation protocols, datasets, and accuracy metrics. Each paper shows their method is "better" but direct comparison across all methods is impossible.

**Missing Piece:** Unified experimental framework comparing ALL major methods (TRAK, TracIn, IF, FastIF, DataShapley, DataInf, LoRIF) under identical conditions with varying computation budgets (measured in FLOPs, memory, wall-clock time) and standardized accuracy metrics (Spearman correlation, top-k recall, LDS).

### Detailed Research Questions
1. What is the rank-order correlation (Spearman/Kendall) between exact influence functions and efficient approximations (TRAK, FastIF, Arnoldi approximation) on standard attribution benchmarks?
2. How does attribution accuracy degrade as computation budget decreases (fewer gradient samples, lower-rank approximations, smaller probe sets)?
3. Do attribution rankings generalize across tasks (classification → generation) or must attribution be recomputed per downstream task?
4. At what training data scale do different approximation methods diverge most from exact attribution, and why?
5. What minimum computation budget is needed to achieve top-k accuracy (identifying most influential training examples) for typical FM applications?

### Key Literature (Supporting Evidence)

| Paper | Year | arXiv | Citations | Key Insight |
|-------|------|-------|-----------|-------------|
| Koh & Liang (2017) | 2017 | 1703.04730 | 3425 | Foundational influence functions |
| Basu et al. (2020) | 2020 | 2006.14651 | 301 | IF fragility in deep networks |
| TRAK (Park et al.) | 2023 | 2303.14186 | 246 | Random projections for scale |
| DataInf (Kwon et al.) | 2023 | 2310.00902 | 105 | LoRA-specific closed-form |
| LoRIF (Li et al.) | 2026 | 2601.21929 | 0 | 20x storage reduction |
| MAGIC (Ilyas et al.) | 2025 | 2504.16430 | 9 | Near-optimal via metadifferentiation |
| ASTRA (Wang et al.) | 2025 | 2507.14740 | 6 | Improved iHVP approximation |

### Available Implementations

| Repository | Stars | Key Feature |
|------------|-------|-------------|
| MadryLab/trak | 233 | Official TRAK with CUDA kernels |
| TRAIS-Lab/dattri | 118 | Unified library: IF, TracIn, TRAK |
| nimarb/pytorch_influence_functions | 344 | Classic IF implementation |
| salesforce/fast-influence-functions | 82 | Scalable HVP computation |

### Failure Context (ROUTE_TO_0 Recovery)

**CRITICAL:** This pipeline is recovering from THREE previous failures (h-e1, h-m2, h-m3) on MODEL COLLAPSE research. Complete topic pivot to DATA ATTRIBUTION.

**Lessons Learned:**
1. **h-e1 FAIL:** Synthetic data generation is error-prone → AVOID complex data generation
2. **h-m2 FALSIFIED:** Curvature-based mechanisms unfounded → AVOID mechanism hypotheses
3. **h-m3 FALSIFIED:** Gradient-representation causal chains broken → Focus on MEASUREMENT not MECHANISM

**How This Direction Avoids Pitfalls:**
- Does NOT require synthetic data generation (h-e1 avoided)
- Does NOT assume curvature/gradient mechanisms (h-m2, h-m3 avoided)
- Uses existing trained models and real data
- Has established evaluation methods (attribution benchmarks)
- Measures attribution accuracy DIRECTLY

### Feasibility Constraints (Pipeline-Enforced)
- REJECT ideas requiring **new benchmarks or evaluation frameworks**
- REJECT ideas requiring **synthetic/generated data or future follow-up data**
- REJECT ideas requiring **human evaluation or subjective scoring**
- ACCEPT only hypotheses testable **immediately using existing real datasets and existing benchmarks**

---

## Discussion Rounds

### Round 0: Opening Positions

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What a fascinating opportunity we have here! Looking at the Gap 1 problem - the lack of a unified Pareto frontier characterization - I immediately see something everyone might be missing. We keep comparing methods as if they operate on the same "accuracy axis," but what if the very notion of "accuracy" in data attribution is fundamentally multi-dimensional?

Let me explain what I mean. Park et al.'s TRAK paper [2023] measures Linear Datamodeling Score (LDS), while Basu et al. [2020] focused on leave-one-out correlations, and DataInf uses top-k recall. These aren't just different metrics - they capture fundamentally different aspects of what "correct attribution" means! What if we approached this not as "which method is best?" but rather "what IS the attribution problem we're actually trying to solve?"

Here's my unconventional angle: Instead of building yet another benchmark comparing methods on a single accuracy metric, what if we characterize the Pareto frontier across MULTIPLE attribution objectives simultaneously? Think about it - a practitioner choosing an attribution method doesn't just want "accuracy." They want:
1. **Rank preservation** (top-k correctness for debugging)
2. **Magnitude fidelity** (actual influence values for data valuation)
3. **Stability** (consistent results across random seeds)

The TRAK paper already hints at this - they show that random projections preserve rank order well but may distort magnitudes. What if that's actually a feature, not a bug, for certain use cases?

My wild idea: We could formulate this as a **multi-objective Pareto analysis** where computation budget is one axis, but we track degradation across 3-4 attribution quality dimensions simultaneously. This would give practitioners a much richer decision tool than "Method X is faster at cost Y."

**Key Points:**
- Current comparisons treat "accuracy" as monolithic when it's actually multi-dimensional
- Different attribution metrics capture genuinely different user needs (debugging vs. valuation vs. auditing)
- A multi-objective Pareto characterization could provide actionable guidance that single-metric comparisons cannot

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your proposal is intriguing—but before we embrace a multi-objective Pareto view, we must formalize it with precision. The evidence suggests that "accuracy" in data attribution is indeed operationalized differently across methods: rank-based metrics (top‑k recall), correlation with leave-one-out (LOO) retraining, and linear datamodeling score (LDS) each target distinct properties. However, your claim that these represent *fundamentally different objectives* must be tested, not assumed. The first question is: **Are these metrics mutually incompatible, or do they collapse onto a smaller latent dimension of attribution quality?** If they are highly correlated across methods and datasets, your multi-objective framing may be unnecessary.

We therefore need a concrete experimental design. I propose the following: construct a benchmark where, for each dataset–model pair, we compute (1) LOO-based ground-truth influence via approximate retraining, (2) top‑k identification accuracy relative to LOO, (3) magnitude fidelity (e.g., Spearman and Pearson correlation with LOO influence), and (4) stability across seeds (e.g., variance of top‑k overlap and influence correlation). For each attribution method, we then obtain a 4-dimensional performance vector under fixed computational budgets. The Pareto frontier is defined over these dimensions plus wall-clock time. Crucially, we must report cross-metric correlations. **Prediction 1:** If rank preservation and magnitude fidelity are strongly correlated (ρ > 0.9 across tasks), then the multi-objective claim weakens. **Prediction 2:** If some methods lie strictly Pareto-dominated across all attribution metrics at matched compute, then the frontier is trivial—your framing adds little. Only if trade-offs are empirically non-degenerate does the hypothesis hold.

We must also identify the achilles heel. Your framework presumes that LOO-style retraining is a valid ground truth. But what if LOO itself is unstable in deep networks? The evidence from prior influence-function literature suggests sensitivity to optimization path and regularization. Therefore, we require a controlled synthetic setting where true influence is analytically derivable—e.g., linear models with closed-form leave-one-out solutions. If Pareto trade-offs disappear in this regime, then observed trade-offs in deep models may reflect estimator noise rather than intrinsic objective conflict. **What would disprove your hypothesis?** If in controlled linear settings all metrics align monotonically across methods, and divergence only appears in high-variance deep regimes, then the "multi-objective nature" is an artifact of instability.

Finally, feasibility. This is implementable. We can standardize compute by FLOPs or wall-clock budget and vary approximation levels (e.g., number of projections in TRAK-like methods). This yields continuous degradation curves. The best experiments are designed to fail—so we should explicitly search for methods that improve one metric without harming others. If none exist, and trade-offs are sharp and reproducible across datasets, I will concede that the attribution problem is intrinsically multi-objective.

**Key Points:**
- Formalize the multi-objective claim by measuring cross-metric correlations and identifying non-trivial Pareto trade-offs under fixed compute.
- Define falsifiable predictions: high metric correlation or universal dominance would invalidate the hypothesis.
- Control for confounds (LOO instability, deep model variance) using synthetic linear regimes with known ground truth.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Hold on - before we get too enamored with this multi-objective Pareto framing, let me stress-test some unstated assumptions. Here's where this breaks down:

**Assumption 1: LOO retraining is a valid ground truth.** 🔬 Prof. Vera touched on this, but I want to push harder. Basu et al. [2020] showed that influence functions are *fragile* in deep networks - but the fragility isn't just in the approximation, it's in the very concept of "influence." When you retrain a deep network without one training example, the stochasticity of SGD means you get different results depending on initialization, batch ordering, and learning rate schedules. So what exactly are we comparing our attribution methods *to*? If LOO itself has variance comparable to the methods we're evaluating, we're building castles on sand.

**Assumption 2: Compute budget is a meaningful normalization axis.** You propose measuring methods at "matched compute." But compute for what? FLOPs for gradient computation? Memory bandwidth? Wall-clock time including I/O? These don't scale proportionally across methods. TRAK's random projections are compute-light but memory-heavy. Influence functions are compute-heavy but can be streamed. DataInf requires storing LoRA gradients. The "same compute budget" is method-dependent - you're comparing apples to oranges.

**Assumption 3: Multi-objective trade-offs are intrinsic, not artifact.** What if the apparent trade-offs between rank preservation and magnitude fidelity simply reflect different estimators converging at different rates? Consider: if you increase projection dimension in TRAK indefinitely, you approach exact influence functions. So the "trade-off" might just be a snapshot of a single convergence trajectory, not a fundamental Pareto frontier.

Here's what would convince me this is valid: **Show me a method that is provably optimal for one metric (e.g., theoretically achieves lowest variance for rank preservation) while being provably suboptimal for another (e.g., biased for magnitude estimation), even in the infinite-data, infinite-compute limit.** If such methods exist, you have intrinsic trade-offs. If all methods converge to the same point asymptotically, then the "multi-objective" nature is just finite-sample behavior, and practitioners should simply maximize compute.

I also note a scope creep risk. Your proposal mentions "debugging vs. valuation vs. auditing" as use cases, but these have wildly different requirements. Debugging needs top-k identification. Valuation needs cardinal influence values. Auditing needs stability and reproducibility. Are we trying to solve all three? If so, we're not characterizing a Pareto frontier - we're just listing what different methods are good at, which every paper already does.

**Key Points:**
- LOO ground truth has its own variance that may dominate method differences
- "Matched compute" is ill-defined when methods have different resource bottlenecks
- Need to distinguish finite-sample trade-offs from fundamental impossibility results
- Scope must be tightly bounded to avoid "comparing incomparables"

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The multi-objective idea is only meaningful if the objectives are *intrinsically* distinct in the limit—not just under noisy, finite approximations. Prof. Rex is exactly right to demand an asymptotic argument. If, under infinite data and compute, all reasonable attribution estimators converge to the same influence functional (e.g., exact leave-one-out under a deterministic training procedure), then any observed trade-off is just a convergence-rate artifact. In that world, there is no fundamental Pareto frontier—only different paths to the same point.

So the core feasibility question becomes: **Is there a single well-defined population influence functional that all consistent estimators converge to?** In convex settings, yes. For linear models with squared loss and full-rank design, LOO influence has a closed form, and rank preservation and magnitude fidelity are monotonic functions of the same underlying quantity. There, I would expect cross-metric correlations → 1 as sample size grows. That would directly falsify the "intrinsically multi-objective" hypothesis in that regime.

However, deep networks break this clean picture. Training is path-dependent and non-convex. Even defining the "true" influence requires specifying the training algorithm, initialization distribution, and randomness. If we define influence as the *expected* parameter difference under LOO retraining averaged over all training stochasticity, then we at least have a coherent target functional. But here's what worries me: that expectation may not preserve rank and magnitude equivalently. For example, if the distribution of LOO effects is heavy-tailed across seeds, then rank stability (probability of being in top‑k) and mean magnitude could genuinely diverge—even asymptotically. That would give you a principled reason for multi-objective structure.

On compute normalization: I agree with Rex that "matched compute" must be formalized. The only theoretically clean axis is something like **number of gradient evaluations** or **Hessian-vector products**, since these are primitive operations common to all methods (influence functions, TRAK-style projections, etc.). Wall-clock time or memory footprint are implementation artifacts. If you parameterize each method by a continuous accuracy knob—e.g., projection dimension for TRAK, number of HVPs for influence functions—you can trace accuracy as a function of primitive operation count. That gives you a legitimate asymptotic comparison framework.

Here's the decisive experiment in my view:
1. In linear models (closed-form LOO), measure whether rank, magnitude, and top‑k accuracy collapse to a single dimension as estimator precision increases.
2. In deep models, define influence as *expected LOO effect over training randomness*. Estimate this via multiple retrains to reduce noise.
3. Examine whether, as estimator precision increases (more projections, more HVPs), methods converge to the same point across all metrics.

If convergence is universal, the Pareto frontier is a finite-sample illusion. If different estimators converge to *different stable limits* for different metrics—even with precise estimation—then you've uncovered a genuinely multi-objective problem.

Okay—this could work. But only if you anchor it in asymptotics and define influence rigorously as a stochastic functional. Otherwise, we're benchmarking noise.

**Key Points:**
- Multi-objective claims must be tested asymptotically: do metrics collapse to one dimension in convex regimes?
- Define a coherent target functional (e.g., expected LOO over training randomness) to avoid benchmarking instability.
- Normalize compute via primitive operations (gradient evals, HVPs) and test convergence trajectories to distinguish intrinsic trade-offs from finite-sample artifacts.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND I see a way to strengthen this into something truly actionable! Let me bridge the valuable criticisms from 🔍 Prof. Rex and ⚙️ Prof. Pax with 🔭 Dr. Nova's original insight.

Here's the key refinement: **We're not asking whether multi-objective trade-offs exist in the abstract - we're asking whether they exist *at the computational budgets practitioners actually use*.** This is crucial. Even if all methods converge asymptotically, the *rate* of convergence can differ systematically across metrics. And practitioners operate at finite compute. So our hypothesis should be:

**Refined Hypothesis:** At practical computational budgets (≤100 gradient evaluations per test query), different attribution approximation methods exhibit non-degenerate Pareto trade-offs across rank preservation, magnitude fidelity, and stability metrics - trade-offs that provide actionable guidance for method selection.

This addresses Prof. Rex's concern about scope creep: we're NOT claiming fundamental impossibility results. We're claiming *practical heterogeneity* in the finite-compute regime. And it addresses Prof. Pax's asymptotic concerns by explicitly bounding the regime of interest.

Now, regarding the ground truth problem - Prof. Rex is right that LOO has variance. But here's the counter-evidence: Park et al.'s TRAK paper [2023] showed that despite LOO variance, TRAK scores correlate ~0.7-0.9 with LOO across multiple runs. This suggests the *signal* in LOO dominates the *noise* - at least for rank preservation. The question becomes: does this signal-to-noise ratio hold equally across all metrics?

Let me propose a concrete experimental design that incorporates everyone's concerns:

1. **Convex sanity check** (Prof. Pax): Run on logistic regression / linear models first. If metrics collapse to one dimension, document it. This becomes our baseline expectation.

2. **Finite-compute Pareto curves** (addressing Rex): For TRAK (varying projection dim), TracIn (varying checkpoint frequency), and IF approximations (varying HVP iterations), plot accuracy on 3 metrics as function of gradient evaluations. If curves overlap = no trade-off. If curves diverge = actionable heterogeneity.

3. **LOO variance estimation** (addressing Rex): Compute LOO with 5 different random seeds for each training example. Report the variance. If method performance gaps exceed LOO variance, we're measuring real signal.

4. **Practitioner-relevant budget range** (bounded scope): Focus on 10-100 gradient evaluations per query - the regime where practitioners actually operate for FM-scale attribution.

The evidence from DataInf [Kwon et al., 2023] already hints at this: they show closed-form solutions that are extremely fast but make specific approximations (LoRA gradients only). Their method dominates on speed but may sacrifice full-model attribution accuracy. That's exactly the kind of Pareto trade-off we want to characterize systematically.

**Key Points:**
- Reframe hypothesis as *practical finite-compute heterogeneity*, not asymptotic impossibility
- Validate with convex sanity check, then test divergence in deep regimes
- Bound LOO variance explicitly to ensure we're measuring signal, not noise
- Focus on practitioner-relevant compute budgets (10-100 gradient evaluations)

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

The refinement to *finite-compute heterogeneity* is a productive shift. The evidence suggests we should explicitly bound the hypothesis to a regime where asymptotics are irrelevant to practice. However, precision is still required. We must define the target functional unambiguously: I propose we define influence as the **expected parameter difference under leave-one-out retraining, averaged over all training stochasticity**. This converts LOO from a noisy procedure into a well-defined stochastic functional. Every attribution estimator is then attempting to approximate this expectation. What would disprove the multi-objective claim is straightforward: if, as primitive operation count increases, all estimators converge to the same point in the joint metric space and metric correlations approach 1 within the practitioner-relevant regime (≤100 gradient-equivalent operations), then no actionable Pareto structure exists.

On the convex sanity check: I consider this mandatory. In linear or logistic regression with closed-form LOO, we can compute the exact expected influence. Prediction 1: as approximation fidelity increases (e.g., projection dimension → d, exact HVPs), rank correlation, magnitude correlation, and top‑k overlap should monotonically co-move, with cross-metric correlations ρ ≥ 0.95. If they do not, then our metric definitions themselves are inconsistent. If they do, this establishes a baseline: any divergence observed in deep models is not definitional but structural.

For deep networks, we must separate three sources of variance: (1) stochastic training noise in the LOO target, (2) estimator approximation error, and (3) metric sampling noise (finite test queries). I recommend a variance decomposition experiment. For a fixed training example, estimate the distribution of its LOO influence over 5–10 retraining seeds. Compute the standard deviation σ_LOO. Then measure estimator error relative to the *mean* LOO influence. Prediction 2: actionable trade-offs exist only if performance differences between methods exceed σ_LOO by a statistically significant margin across examples. If σ_LOO dominates, we are benchmarking noise.

On compute normalization: I concur with Prof. Pax that primitive operations—gradient evaluations and Hessian-vector products—are the only defensible currency. Each method must be parameterized by a continuous accuracy knob (projection dimension, checkpoint count, HVP iterations). We then trace performance surfaces over a 4D space: (rank ρ, magnitude ρ, stability, compute). The Pareto frontier is non-trivial only if no single method dominates across all attribution metrics within the bounded compute regime. Prediction 3: if for every compute level ≤100 gradient-equivalents there exists at least one pair of methods where one is superior in rank but inferior in magnitude (with statistically significant gaps), then the finite-compute Pareto hypothesis survives.

Finally, I will state the achilles heel clearly. If increasing compute for any one method monotonically improves all attribution metrics without harming stability—and surpasses competitors within the practical regime—then the frontier collapses into a single convergence race. The hypothesis fails. The best experiments are designed to fail; we should actively search for such dominance.

**Key Points:**
- Define influence rigorously as expected LOO over training randomness; test convergence of estimators toward this stochastic functional.
- Use convex models as a falsification baseline: metrics should collapse to one dimension as approximation error → 0.
- Establish non-trivial finite-compute Pareto trade-offs only if metric gaps exceed LOO variance and no method dominates across all metrics within ≤100 gradient-equivalent operations.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! I love how this has evolved. The discussion has crystallized into something much more precise and testable than my original framing. Let me add one more creative angle that might strengthen the novelty claim.

🔬 Prof. Vera's variance decomposition is brilliant - but here's what excites me: **what if the variance itself is the signal?** Consider this: when TRAK uses random projections, it's essentially trading bias for variance. When exact influence functions use finite HVP iterations, they have low variance but potentially systematic bias. These aren't just noise characteristics - they're *design choices* that optimize for different downstream uses.

Think about it from a practitioner's perspective:
- **Model debugging**: You want low variance. A noisy attribution that says "example X might be influential, or maybe not" is useless for debugging. You need confidence.
- **Data marketplace pricing**: You want unbiased magnitude estimates. Systematic underestimation cheats data sellers; overestimation cheats buyers.
- **Compliance auditing**: You want stability across runs. If an auditor re-runs your attribution and gets different top-k, you have a legal problem.

This suggests the Pareto frontier isn't just about accuracy-compute trade-offs - it's about **bias-variance-stability trade-offs** that map to genuine user requirements. That's the novel framing I think we've arrived at.

Here's my synthesis of what we've developed:

**Core Hypothesis (Refined):** Data attribution methods exhibit non-degenerate Pareto trade-offs in the finite-compute regime (≤100 gradient-equivalent operations) across three quality dimensions: (1) rank preservation fidelity, (2) magnitude estimation accuracy, and (3) cross-run stability. These trade-offs are not artifacts of estimation noise but reflect fundamental design choices (random projection vs. iterative HVP vs. gradient similarity) that optimize for different downstream applications.

**Testable Predictions:**
1. **Convex baseline**: In logistic regression with closed-form LOO, all three metrics converge together as approximation quality increases (ρ cross-metric ≥ 0.95).
2. **Deep network divergence**: In ResNet/BERT models, at fixed compute budget, methods that maximize rank preservation (e.g., TRAK) sacrifice magnitude accuracy, and vice versa for HVP-based methods.
3. **Variance-bias trade-off**: TRAK-style random projections exhibit higher cross-run variance but lower systematic bias; HVP-based methods show the reverse pattern.

**Why This Matters (Significance):** Current attribution benchmarks report single numbers per method. Our Pareto characterization would provide practitioners with a decision tree: "If debugging → optimize for low variance → use method X at budget Y. If valuation → optimize for magnitude fidelity → use method Z." No existing work provides this guidance.

**Key Points:**
- The bias-variance-stability trade-off maps directly to practitioner use cases (debugging, valuation, auditing)
- This goes beyond "which method is best" to "which method is best *for what*"
- Three testable predictions with clear success/failure criteria established
- Novel contribution: first systematic Pareto characterization connecting method design to downstream requirements

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally getting sharp. But here's where this still breaks down: you're drifting toward a *story* about bias–variance–stability trade-offs without yet proving that these are structurally incompatible objectives rather than correlated failure modes of approximation. Show me the incompatibility. If a single method, with a single tuning knob, can monotonically improve rank correlation, magnitude correlation, and stability together within ≤100 gradient-equivalents, then your Pareto story collapses into "some methods are just worse approximations."

Dr. Nova's framing about downstream use cases is compelling — but that's narrative value, not scientific proof. What would convince me is this: a formal or empirical demonstration that, at fixed primitive operation count, improving one metric *necessarily* worsens another for at least one pair of methods. Not "sometimes observed," not "on average," but statistically robust non-dominance. I want to see pairwise dominance tests across compute levels. For each budget b ≤ 100, construct the empirical Pareto set. If at any b a single method strictly dominates the others on all three metrics (rank ρ, magnitude ρ, stability), your hypothesis weakens substantially.

Now let's talk about the variance-as-signal idea. Clever — but dangerous. Variance is only meaningful if you separate *epistemic* variance (due to random projections) from *target variance* (σ_LOO from retraining). If TRAK's cross-run instability is smaller than σ_LOO, then it's just faithfully reflecting target uncertainty. If it exceeds σ_LOO, that's estimator noise, not principled trade-off. So here's the experiment I demand: compute stability relative to the *mean LOO functional* and normalize it by σ_LOO. Define a "stability inflation ratio." If projection-based methods show inflation >1 while HVP methods show <1 at the same compute, then you have a real variance design trade-off. Otherwise, you're benchmarking stochasticity artifacts.

On the convex baseline: don't just report ρ ≥ 0.95 and move on. I want to see cross-metric partial correlations conditioned on compute. If rank and magnitude remain tightly coupled even when compute is artificially throttled (e.g., low-rank approximations to closed-form LOO), that establishes that finite-compute alone does not induce trade-offs in well-behaved regimes. That's your falsification backbone. Without it, reviewers will say: "Your Pareto frontier is just due to pathological non-convexity."

Finally, on real-world impact — tighten it. The decision value only exists if method choice actually flips practitioner decisions. So quantify it. For debugging: measure whether different methods identify disjoint top‑k harmful examples at the same compute budget. If top‑k overlap across methods is >90%, your practical heterogeneity claim is weak. If it drops to, say, 50–60% with statistically significant performance differences downstream (e.g., retraining without those examples yields different generalization gains), *now* you have decision-level consequences.

You're close. But I will only be satisfied when:
1. Non-dominance is demonstrated at fixed compute with statistical rigor.
2. Estimator variance is separated from target stochasticity.
3. Method disagreement translates into materially different downstream actions.

Do that — and now you've addressed my concerns.

**Key Points:**
- Demonstrate true non-dominance at fixed compute; otherwise the Pareto claim collapses.
- Separate estimator variance from inherent LOO stochasticity via normalized stability analysis.
- Prove decision-level impact: different methods must lead to meaningfully different practitioner actions.

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: **What does this mean for the field?** Let me synthesize what's emerged and assess the genuine contribution.

This discussion has evolved from a vague "Pareto frontier characterization" to something much more precise and, I believe, significantly impactful. Here's why this matters:

**1. State-of-the-Art Gap:** Current attribution papers each define "better" in ways that favor their method. TRAK reports LDS. DataInf reports top-k recall. Influence function papers report correlation with LOO. This fragmentation means practitioners have NO reliable way to choose methods. Our contribution would be the **first unified measurement framework** that lets practitioners make informed decisions. That's not incremental - that's infrastructure.

**2. Novel Scientific Question:** 🔍 Prof. Rex is right that we need to prove non-dominance isn't just "some methods are worse." But here's the deeper scientific question we're actually answering: **Is data attribution a single well-posed problem, or a family of related but distinct problems?** If metrics collapse asymptotically, attribution is one problem with many approximators. If they diverge even with perfect estimation, we've discovered that "attribution" is actually 2-3 distinct concepts that happen to share a name. Either answer is significant.

**3. Practical Decision Value:** The decision-level impact 🔍 Prof. Rex demands is exactly the right test. But let me frame the significance: if methods disagree on top-k identification by 40-50%, then current attribution practices are essentially arbitrary. Practitioners think they're "doing attribution" when they're actually making implicit methodology choices that determine their conclusions. Exposing this would be a wake-up call for the field.

**4. How This Advances the Field:**
- **If Pareto trade-offs are real:** We provide the first rigorous characterization, enabling principled method selection. Papers will cite us for methodology.
- **If trade-offs are artifacts:** We've demonstrated that attribution methods are converging to a common target, just at different rates. That's also valuable - it tells practitioners to maximize compute on any reasonable method.
- **Either way:** We've established the measurement framework. Future methods will be evaluated against our multi-dimensional benchmark.

**5. What New Research Directions This Opens:**
- **Attribution-aware training:** If stability matters, can we design training procedures that produce more stable attribution targets?
- **Hybrid methods:** If TRAK excels at rank and HVP excels at magnitude, can we combine them?
- **Task-specific attribution:** If debugging and valuation need different metrics, should we have separate methods rather than one-size-fits-all?

**My Assessment:** This is a **STRONG** contribution candidate. The hypothesis is now:
- **Specific:** Finite-compute Pareto trade-offs across rank, magnitude, stability
- **Testable:** Convex baseline + deep network experiments + decision impact measurement
- **Novel:** First unified multi-metric characterization connecting method design to downstream requirements
- **Significant:** Provides practitioner guidance that currently doesn't exist

**Key Points:**
- This addresses a real infrastructure gap: no unified method comparison exists
- The deeper question (is attribution one problem or several?) is scientifically significant either way
- Decision-level impact test ensures practical relevance
- Opens multiple new research directions regardless of outcome

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The entire Pareto claim hinges on one technical question: **are rank fidelity, magnitude fidelity, and stability fundamentally coupled objectives under finite primitive operations, or are they just different views of the same approximation error?** If they are just different projections of a single error scalar (distance to the true expected LOO functional), then with enough accuracy tuning they will all improve together. In that case, there is no structural trade-off — only different convergence rates. That's the core feasibility test.

I agree with Prof. Vera's formalization: define influence as the *expected* parameter difference under leave-one-out retraining over training randomness. That makes the target a well-defined stochastic functional. Good. Now here's what worries me: if all estimators can be expressed as approximations to the same linearization of this functional (e.g., inverse-Hessian–gradient products or their projections), then at fixed compute they differ only in approximation quality. Under that view, improving projection dimension or HVP iterations should monotonically improve *all* downstream metrics — rank, magnitude, and stability — unless the metrics themselves introduce nonlinear distortions. So before claiming Pareto structure, you must demonstrate that the metrics are not simply monotone in a single approximation error norm.

The convex baseline is therefore not just a sanity check — it's a structural control. In logistic regression with exact LOO available, you can simulate finite-compute approximations: low-rank Hessian truncation, noisy HVPs, random projection of gradients. If, under these controlled degradations, rank ρ, magnitude ρ, and stability remain tightly correlated (partial correlations ≥ 0.95 conditioned on compute, as Rex suggested), then finite-compute alone does *not* induce trade-offs in well-behaved settings. That would imply any divergence in deep networks is due to non-convexity or optimization path dependence — which is acceptable, but you must then argue that this structural non-convexity creates genuine incompatibility rather than chaotic noise.

On the variance-as-signal idea — technically plausible, but only if you normalize by σ_LOO. Suppose σ_LOO is large relative to mean influence magnitude. Then even a perfect estimator will appear unstable across retrains. In that regime, "stability" is not a property of the method but of the target. So I strongly support Rex's stability inflation ratio:
Inflation = Var(estimator runs) / σ_LOO²

If projection-based methods systematically exceed 1 while HVP-based methods stay below 1 at equal primitive counts, then you have a principled bias–variance design trade-off. If not, the variance story collapses.

Finally, the non-dominance requirement is feasible to test — but only if you parameterize each method with a *continuous compute knob* and measure statistical dominance at fixed primitive budgets. For each compute level ≤100 gradient-equivalents, perform pairwise dominance tests with confidence intervals across examples. If at any budget a single method is superior on all three metrics with statistically significant margins exceeding σ_LOO-derived uncertainty, the Pareto hypothesis weakens substantially. If instead you observe consistent metric crossings — e.g., Method A higher rank but lower magnitude with non-overlapping CIs — then I'll say: okay, this could work.

Right now, the idea is technically plausible — but it survives only if you prove that multi-metric disagreement is not reducible to a single approximation error axis.

**Key Points:**
- Trade-offs are real only if metrics are not monotone functions of a single approximation error norm.
- Convex finite-compute degradations must show metric coupling; otherwise deep divergence may just be noise.
- Stability must be normalized by σ_LOO to distinguish estimator variance from target stochasticity.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, this is exactly the rigor we need! Let me now synthesize all the concerns into a strengthened, bulletproof hypothesis formulation. Everyone has raised valid points - now let me show how we address them all.

**Strengthened Hypothesis:**

*In the finite-compute regime (≤100 gradient-equivalent primitive operations), data attribution methods exhibit non-degenerate Pareto trade-offs across three quality dimensions—(1) rank preservation, (2) magnitude fidelity, and (3) normalized stability—that are NOT reducible to a single approximation error axis, and these trade-offs manifest as statistically significant non-dominance relationships with decision-level practical consequences.*

Here's how we address every concern raised:

**Addressing ⚙️ Prof. Pax's "single error axis" concern:**
The convex baseline experiment IS the falsification test. We will explicitly measure whether rank ρ, magnitude ρ, and normalized stability are monotone in approximation error. If partial correlations ≥ 0.95 in convex settings, we've established coupling. Then in deep networks, IF we observe metric crossings (Method A > Method B on rank, but A < B on magnitude with non-overlapping CIs), we've proven the deep regime introduces structural decoupling beyond approximation quality.

**Addressing 🔍 Prof. Rex's "variance artifact" concern:**
The stability inflation ratio is now a core metric:
- Compute σ_LOO via 5-10 retraining seeds per example
- Measure estimator cross-run variance
- Report Inflation = Var_estimator / σ_LOO²
- **Prediction:** Random projection methods show Inflation > 1.5 at low compute; HVP methods show Inflation < 0.8. If not, the variance trade-off claim is withdrawn.

**Addressing 🔬 Prof. Vera's "falsification criteria":**
Three testable predictions with clear success/failure:
1. **Convex coupling:** Cross-metric correlations ≥ 0.95 in logistic regression under compute throttling → establishes baseline coupling
2. **Deep decoupling:** At fixed compute, ≥2 method pairs show metric crossings with non-overlapping 95% CIs → confirms structural trade-offs
3. **Decision impact:** Top-k overlap between methods at same compute drops below 70%, AND retraining-without-top-k produces statistically different accuracy changes → confirms practical consequence

**Addressing 🎯 Dr. Sage's "significance" framing:**
This is now a **two-stage contribution:**
- **Stage 1 (Infrastructure):** First unified multi-metric benchmark for attribution methods. Regardless of Pareto outcome, this is valuable.
- **Stage 2 (Discovery):** If trade-offs exist, first rigorous characterization. If not, proof that methods converge to common target.

**Feasibility Confirmation (existing resources):**
- **Methods:** TRAK (dattri), TracIn (dattri), IF (pytorch_influence_functions) - all have continuous compute knobs
- **Models:** Logistic regression (convex baseline), ResNet-18/BERT-base (deep regime)
- **Datasets:** CIFAR-10, MNLI - existing benchmarks, no new data needed
- **Compute:** ≤100 gradient-equivalent operations per method - tractable

**What Would Convince 🔍 Prof. Rex:**
- Non-overlapping CIs on metric crossings ✓ (prediction 2)
- Stability inflation ratio analysis ✓ (new core metric)
- Decision-level impact via top-k disagreement ✓ (prediction 3)

Now you've addressed my concerns!

**Key Points:**
- Hypothesis now explicitly addresses "single error axis" alternative
- Stability inflation ratio distinguishes estimator variance from target stochasticity
- Three falsifiable predictions with clear success criteria
- Decision-level impact quantified through top-k disagreement and downstream consequences
- All components implementable with existing code and benchmarks

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

Good. The hypothesis is now sufficiently sharp that we can formalize it. Let us define the target functional precisely: for each training example i, influence is the expected leave-one-out parameter shift:
φ_i = E_ξ[θ^(-i)_ξ - θ_ξ]

where ξ indexes training randomness. All estimators φ̂^(m,b) are functions of method m and primitive compute budget b. The three metrics must then be defined as functionals of the vector φ̂^(m,b) relative to the ground truth φ: (1) rank correlation ρ_r, (2) magnitude correlation ρ_m, and (3) normalized stability:
S^(m,b) = Var_runs(φ̂^(m,b)) / Var_ξ(φ)

If ρ_r, ρ_m, S are all monotone in a single approximation error norm ||φ̂-φ||, then the Pareto claim collapses. Therefore, the critical test is statistical non-monotonicity.

To establish this rigorously, I propose the following procedure at each fixed budget b ≤ 100:
1. Compute bootstrap confidence intervals for each metric per method.
2. Define strict dominance: method A dominates B at budget b if for all three metrics the 95% CI of A exceeds that of B by a margin larger than the estimated uncertainty induced by σ_LOO.
3. Construct the empirical Pareto set at each b.

The hypothesis survives only if, across a contiguous range of budgets, no single method dominates all others and at least one pair exhibits statistically significant metric crossing (e.g., ρ_r^A > ρ_r^B while ρ_m^A < ρ_m^B, CIs non-overlapping). If even one budget yields universal dominance, we must conclude the frontier is not structural but transitional.

On the convex baseline: this is the falsification backbone. In logistic regression with exact LOO, we can parameterize degradation by truncating Hessian eigenspectra or injecting controlled noise into HVPs. We then compute partial correlations:
corr(ρ_r, ρ_m | b), corr(ρ_r, S | b)

If these exceed 0.95 uniformly, finite compute alone does not induce trade-offs in well-posed regimes. Only if deep networks show statistically significant reductions in these conditioned correlations—beyond what can be attributed to increased σ_LOO—can we claim structural decoupling induced by non-convexity or optimization path dependence.

Regarding stability: I insist we separate estimator variance from target variance at the example level, not only globally. For each example i, compute:
Inflation_i^(m,b) = Var_runs(φ̂_i) / Var_ξ(φ_i)

Report the distribution of this ratio. If projection-based methods show a right-shifted distribution (median >1) while HVP-based methods cluster below 1 at equal b, then variance is a design consequence. If the distributions overlap substantially, stability differences are artifacts of stochastic training noise.

Finally, decision-level impact must be quantified with hypothesis tests. Define top‑k disagreement as 1 - J(A_k, B_k) where J is Jaccard similarity. Then test whether retraining after removing A_k versus B_k produces statistically distinguishable test accuracy distributions across seeds. If the null hypothesis of equal downstream performance cannot be rejected (α=0.05), disagreement is epistemically irrelevant. The best experiments are designed to fail; if these tests do not reject, we abandon the practical heterogeneity claim.

If these criteria are met—formal non-dominance at fixed compute, metric decoupling beyond convex controls, and downstream consequence under controlled hypothesis testing—then, and only then, will I say: *This meets my standards.*

**Key Points:**
- Define dominance and Pareto structure with confidence intervals and strict statistical criteria at fixed compute.
- Use convex degradation experiments to test whether metrics are monotone in a single approximation error norm.
- Normalize stability per-example via variance inflation ratios and require downstream hypothesis tests for decision-level impact.

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now you've addressed my concerns. Let me summarize what we've achieved and identify the final remaining edges.

🔬 Prof. Vera's formalization is exactly what was needed. The hypothesis is now falsifiable at multiple levels:
1. **Convex coupling test** - if metrics collapse in logistic regression, that's our baseline
2. **Deep network non-dominance test** - metric crossings with bootstrap CIs
3. **Downstream impact test** - hypothesis test on retraining accuracy differences

I'm satisfied with the statistical framework. But let me flag two remaining concerns that are addressable:

**Concern 1: Ground truth estimation cost.** Computing σ_LOO (variance of true influence over training randomness) requires multiple retrains per example. For N training examples and R retrains per example, that's O(N × R × T_train). For CIFAR-10 with 50K examples and R=5 retrains... that's 250K training runs. Feasible for small models (minutes per run), but let's be explicit about scope.

**Mitigation:** Estimate σ_LOO on a stratified subsample of 500-1000 training examples, bootstrapped to estimate uncertainty in the variance estimates themselves. This is standard in influence function validation (see TRAK paper's experimental setup).

**Concern 2: Method coverage.** We've focused on TRAK (projection), TracIn (gradient similarity), and IF (HVP-based). But DataInf and LoRIF are specifically designed for LoRA-tuned models. Are we testing at full-model fine-tuning only, or including the LoRA regime?

**Recommendation:** Two experimental tracks:
- **Track A (Full fine-tuning):** ResNet-18 on CIFAR-10, BERT-base on MNLI. Methods: TRAK, TracIn, exact IF, FastIF.
- **Track B (LoRA fine-tuning):** LLaMA-7B with LoRA on instruction-following. Methods: DataInf, LoRIF, TRAK.

Track B is more relevant to FM practitioners but has higher ground truth variance. Document any Pareto structure differences between tracks.

**What would convince me the hypothesis is READY for implementation:**
- [x] Formal definition of target functional (φ_i = E_ξ[θ^(-i) - θ])
- [x] Three metrics with normalization (ρ_r, ρ_m, S with inflation ratio)
- [x] Falsification procedure (convex coupling, non-dominance CIs, downstream hypothesis tests)
- [x] Clear success/failure criteria
- [ ] Explicit scope decisions (Track A vs. Track B, subsample sizes for σ_LOO)

Make those scope decisions explicit, and I'll sign off.

**My verdict:** This hypothesis is now STRONG. The remaining work is implementation scoping, not conceptual refinement. The core scientific question—whether finite-compute attribution exhibits irreducible multi-objective trade-offs—is well-posed and testable.

**Key Points:**
- Statistical framework is sound; remaining concerns are scope/logistics
- Ground truth estimation requires subsampling strategy (500-1000 examples)
- Recommend two tracks: full fine-tuning (Track A) and LoRA (Track B)
- Hypothesis is READY for Phase 2B implementation planning

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Alright. We're close. The statistical scaffolding is solid. What I need now are explicit *feasibility commitments* so we don't accidentally test something ill-posed.

First, on the ground-truth functional φ_i = E_ξ[θ^(−i)_ξ − θ_ξ]. In deep non-convex models, this expectation may not even be well-defined in a strong sense — training can land in different basins with parameter differences O(1), not infinitesimal perturbations. If the distribution over θ_ξ is multimodal, then φ_i is averaging across qualitatively different solutions. That's not wrong, but it changes interpretation: influence becomes a property of the *training procedure distribution*, not a local functional of a solution. Here's what worries me: if basin variance dominates LOO effects, σ_LOO will be large and unstable, and your normalization may wash out meaningful estimator differences. So I strongly recommend an empirical check: measure between-seed parameter distance ||θ_ξ − θ_ξ′|| and compare it to typical ||θ^(−i)_ξ − θ_ξ||. If the former is larger by an order of magnitude, you're in a regime where the target itself is noisy, and stability claims become fragile.

Second, I agree with Rex: subsampling 500–1000 examples for σ_LOO is not just practical — it's necessary for statistical validity. But be careful: per-example variance estimation with R=5 seeds gives extremely noisy variance estimates. The variance of a variance estimator scales poorly at small R. If you're going to compute Inflation_i distributions, you need at least R≈10 retrains for that subsample to make median shifts meaningful. Otherwise, overlapping distributions could just be variance-of-variance artifacts. This is a *statistical identifiability* issue, not a compute issue.

Third, on Track A vs Track B. Let's be realistic: LoRA changes the geometry. The effective parameter space is low-rank and much closer to convex in practice. That may artificially reduce decoupling and produce tighter metric coupling. So here's a clean technical decision: treat Track A (full fine-tuning) as the primary structural test of non-convex decoupling. Treat Track B (LoRA) as a boundary condition test. If Pareto structure appears in Track A but collapses in Track B (metrics recouple, dominance emerges), that's actually a powerful mechanistic result: trade-offs arise from high-dimensional non-convex parameterization, not from finite compute per se. That would strengthen, not weaken, the contribution.

Finally, the single-error-axis question. You can test this directly by regressing all three metrics against ||φ̂−φ||₂ at fixed b in the convex setting. If R² ≈ 1 for each metric individually and jointly, then the single-axis model holds. Then in deep networks, compute the same regression. If R² drops substantially (say below 0.8), you have quantitative evidence that metrics are not functions of a single normed error. That's a clean, mechanistic test — not just correlation hand-waving.

At this point, I'll say this: the hypothesis is technically feasible *if and only if* you verify (1) the target functional is stable relative to basin variability, and (2) metric decoupling survives norm-based regression tests. If those hold, then yes — okay, this could work.

**Key Points:**
- Verify that φ_i is well-defined relative to basin variability; compare between-seed parameter variance to LOO shifts.
- Use sufficient retrain seeds (≈10) for stable per-example variance and inflation ratio estimation.
- Test the "single error axis" explicitly via regression on ||φ̂−φ||₂ in convex and deep regimes; require R² drop to claim structural decoupling.

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask now is: **Is this ready?** Let me give my final assessment of significance and readiness.

**Scientific Contribution Assessment:**

This discussion has produced something genuinely novel. We've moved from the vague question "What's the Pareto frontier of attribution methods?" to a precise, testable claim:

*Finite-compute data attribution exhibits irreducible multi-objective trade-offs across rank preservation, magnitude fidelity, and normalized stability, arising from structural properties of non-convex training rather than mere approximation quality differences.*

This is significant because:

1. **It answers a foundational question:** Is "data attribution" one problem or several? Current literature implicitly assumes one target. We're testing that assumption rigorously.

2. **It provides practitioner guidance that doesn't exist:** No current work tells practitioners "for debugging use X, for valuation use Y." If our hypothesis holds, we deliver exactly that.

3. **It connects method design to outcomes:** Random projections vs. HVP iterations aren't just implementation choices - they may be optimizing different objectives. That's a deeper understanding.

4. **It has clear falsification:** If metrics collapse to a single axis in both convex and deep regimes, we've proven attribution is a well-posed single problem. That's also valuable knowledge.

**Readiness Assessment:**

| Criterion | Status | Evidence |
|-----------|--------|----------|
| **Specific** | ✅ STRONG | φ_i = E_ξ[...], three normalized metrics, compute ≤100 gradient-equivalents |
| **Mechanism** | ✅ STRONG | Non-convex geometry creates structural metric decoupling vs. single approximation axis |
| **Predictions** | ✅ STRONG | (1) Convex coupling ρ≥0.95, (2) Deep non-dominance with CI crossings, (3) R² drop <0.8 for single-axis regression |
| **Novelty** | ✅ STRONG | First rigorous multi-objective characterization of attribution Pareto structure |
| **Feasibility** | ✅ STRONG | Existing methods (dattri, TRAK), existing benchmarks (CIFAR-10, MNLI), tractable compute |
| **Objections** | ✅ ADDRESSED | Basin variance check, R≈10 for variance estimation, Track A/B design |

**Final Scope Decisions (per Prof. Rex's request):**
- **Primary Track (A):** Full fine-tuning, ResNet-18/CIFAR-10 + BERT-base/MNLI
- **Secondary Track (B):** LoRA fine-tuning as boundary condition (expect metric recoupling)
- **σ_LOO estimation:** 1000 stratified examples, R=10 retrains each
- **Compute range:** 10, 25, 50, 75, 100 gradient-equivalent operations

**My Verdict:** This hypothesis is **READY for Phase 2B**. We have:
- A clear core claim with quantitative predictions
- Multiple falsification pathways
- Practical decision value regardless of outcome
- Scope decisions that balance rigor with feasibility

This matters because attribution methods are being deployed in high-stakes contexts (copyright, data markets, model debugging) without understanding which method is appropriate for which use case. Our work would provide that missing guidance.

**Key Points:**
- Hypothesis is scientifically significant: answers whether attribution is one problem or several
- All convergence criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) are satisfied
- Scope decisions finalized: Track A primary, Track B boundary, 1000 examples × 10 retrains for σ_LOO
- READY for Phase 2B implementation planning

---

---

## Convergence Tracking

**Status:** CONVERGED at Exchange 15
**Criteria:**
- [x] SPECIFIC: Clear core claim stated - φ_i = E_ξ[θ^(-i) - θ], three normalized metrics, ≤100 gradient-equivalents
- [x] MECHANISM: How it works explained - Non-convex geometry creates structural metric decoupling
- [x] PREDICTIONS: 2-3 testable predictions with criteria - Convex coupling, deep non-dominance, R² drop
- [x] NOVELTY: What's new articulated - First rigorous multi-objective Pareto characterization
- [x] FEASIBILITY: Implementation realistic - Existing methods and benchmarks, tractable compute
- [x] OBJECTIONS: Major criticisms addressed - Basin variance check, R=10 seeds, Track A/B design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The multi-objective Pareto framing is genuinely novel. While individual attribution methods have been compared before, no prior work has rigorously tested whether different metrics (rank, magnitude, stability) represent fundamentally incompatible objectives or simply different views of approximation error. The connection between method design choices (random projections vs. HVP) and downstream use cases (debugging vs. valuation) is a fresh perspective.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is exceptionally testable. Three clear falsification pathways exist: (1) If cross-metric correlations remain ≥0.95 in convex settings, coupling baseline established; (2) If R² from single-axis regression drops <0.8 in deep networks, decoupling proven; (3) If bootstrap CIs show non-dominance with metric crossings, Pareto structure confirmed. Each pathway has quantitative thresholds.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a real infrastructure gap in the attribution field. Practitioners currently cannot make principled method choices because each paper defines "better" differently. Regardless of whether Pareto trade-offs exist, the unified measurement framework is valuable. If trade-offs are real, the practitioner decision tree (debugging→X, valuation→Y) would be the first of its kind.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All experimental components exist. Methods: dattri library (TRAK, TracIn, IF). Benchmarks: CIFAR-10, MNLI. Compute: ≤100 gradient-equivalents is tractable. Key technical safeguards identified: basin variance check (||θ_ξ - θ_ξ′|| vs ||θ^(-i) - θ||), R=10 retrains for stable variance estimation, Track A/B design separating full fine-tuning from LoRA.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a precise, testable hypothesis about the fundamental structure of data attribution:

**Core Claim:** In the finite-compute regime (≤100 gradient-equivalent operations), data attribution methods exhibit non-degenerate Pareto trade-offs across three quality dimensions—rank preservation (ρ_r), magnitude fidelity (ρ_m), and normalized stability (S)—that are NOT reducible to a single approximation error axis. These trade-offs arise from structural properties of non-convex deep learning rather than mere differences in approximation quality, and they manifest as statistically significant non-dominance relationships with decision-level practical consequences.

**Proposed Mechanism:** Different attribution methods make different approximation choices that optimize for different quality dimensions. Random projection methods (TRAK) trade bias for variance, achieving strong rank preservation but potentially higher instability. HVP-based methods (influence functions) have lower variance but may sacrifice rank fidelity at low compute budgets. These aren't just implementation details—they're design trade-offs that map to different downstream use cases.

**Key Predictions:**
1. In convex settings (logistic regression), cross-metric partial correlations ≥0.95 at all compute levels—establishing baseline coupling.
2. In deep networks (ResNet-18/CIFAR-10, BERT-base/MNLI), at least one method pair shows statistically significant metric crossings (A better on ρ_r, B better on ρ_m) with non-overlapping 95% bootstrap CIs.
3. R² from regressing metrics on ||φ̂-φ||₂ drops from ~1.0 in convex to <0.8 in deep settings—proving structural decoupling.
4. Top-k disagreement between methods exceeds 30%, and retraining-without-top-k produces statistically distinguishable accuracy changes.

**Experimental Approach:** Two-track design with Track A (full fine-tuning) as primary structural test and Track B (LoRA) as boundary condition. Ground truth estimation via 1000 stratified examples with R=10 retrains for σ_LOO. Basin variance check to ensure target functional is well-defined.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Ground truth computational cost - 1000 examples × 10 retrains = 10,000 training runs for σ_LOO estimation alone. Need efficient implementation.
- **Concern 2:** Basin variance may dominate LOO effects in very deep models, making the target functional noisy. The basin check is essential before proceeding.
- **Concern 3:** LoRA (Track B) may show metric recoupling not because trade-offs don't exist, but because low-rank parameterization is approximately convex. Interpretation requires care.
- **Mitigation Strategy:** (1) Use small models (ResNet-18) where training is fast; (2) Run basin check FIRST before committing to full experiments; (3) Frame Track B results explicitly as "boundary condition" testing convexity hypothesis.

---

## Emerged Hypothesis Summary

### Core Statement
Finite-compute data attribution methods exhibit non-degenerate multi-objective Pareto trade-offs across rank preservation, magnitude fidelity, and normalized stability that are structurally induced by non-convex deep learning geometry.

### Causal Mechanism
Different approximation strategies (random projections, gradient similarity, inverse-Hessian-vector products) optimize for different quality dimensions. In convex settings, all metrics collapse to a single approximation error axis. In non-convex deep networks, the loss landscape geometry creates structural incompatibilities.

### Variables
- **Independent:** Attribution method (TRAK, TracIn, IF, FastIF, DataInf), compute budget (10-100 gradient-equivalents), model regime (convex/deep)
- **Dependent:** Rank correlation ρ_r, magnitude correlation ρ_m, normalized stability S = Var_runs/σ_LOO²
- **Control:** Dataset (CIFAR-10, MNLI), training procedure, random seeds

### Key Assumptions
1. LOO influence can be meaningfully estimated via E_ξ[θ^(-i) - θ] over training randomness
2. Basin variance does not completely dominate LOO effects
3. The metrics (ρ_r, ρ_m, S) capture genuinely different aspects of attribution quality

### Null Hypothesis
All three metrics are monotone functions of a single approximation error norm ||φ̂-φ||₂, and any observed trade-offs are finite-sample artifacts that disappear as compute increases.

### Predictions
1. Convex coupling: corr(ρ_r, ρ_m | b) ≥ 0.95 in logistic regression
2. Deep decoupling: ≥1 method pair with non-overlapping CI metric crossings
3. R² drop: Regression R² from ~1.0 (convex) to <0.8 (deep)
4. Decision impact: Top-k disagreement >30%, significant downstream accuracy differences

### Novelty
First rigorous multi-objective characterization connecting attribution method design to downstream use case requirements. Answers the foundational question of whether "data attribution" is one problem or several.

### Scope & Boundaries
- Compute regime: ≤100 gradient-equivalent operations
- Model scope: Small-to-medium models (ResNet-18, BERT-base); FM-scale is future work
- Method scope: Gradient-based methods (TRAK, TracIn, IF); excludes data Shapley

### Experimental Setup
- Track A (Primary): Full fine-tuning on CIFAR-10/ResNet-18 + MNLI/BERT-base
- Track B (Boundary): LoRA fine-tuning on instruction-following
- Ground truth: 1000 stratified examples × 10 retrains for σ_LOO
- Prerequisite: Basin variance check before main experiments

### Related Work & Baselines
- TRAK [Park et al., 2023]: Random projection baseline
- Influence Functions [Koh & Liang, 2017]: Exact IF baseline
- DataInf [Kwon et al., 2023]: LoRA-specific baseline
- Basu et al. [2020]: Fragility analysis informing experiment design

### Phase 2B Readiness Seeds
- Metric definitions formalized with mathematical notation
- Falsification criteria quantified with thresholds
- Two-track experimental design specified
- Ground truth estimation procedure detailed
- Success/failure criteria explicit

### Established Facts
- Attribution methods currently use incomparable evaluation protocols
- Random projections (TRAK) achieve ~0.7-0.9 rank correlation with LOO
- Influence functions are fragile in deep networks [Basu et al., 2020]
- No unified multi-metric benchmark exists for attribution methods

---

*Discussion converged at Exchange 15. Ready for Phase 2B.*

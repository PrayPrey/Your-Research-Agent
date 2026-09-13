# Phase 2A Discussion Log
# Architecture: Self-Contained Tikitaka Loop v9.0.0
# Gap: Gap-1 — No Standardized Δρ Benchmark Comparing Matched-Capacity NFN vs Flat MLP on Schurholt Zoos
# Generated: 2026-05-05

---

## Briefing Context

### Research Gap

**Gap ID:** Gap-1  
**Priority:** Critical / PRIMARY  
**Title:** No Standardized Δρ Benchmark Comparing Matched-Capacity NFN vs Flat MLP on Schurholt Zoos

**Core Question:**
On the Schurholt et al. MNIST-CNN (~4K models) and CIFAR-10 (~1.5K models) model zoos, does a matched-capacity (~500K parameter) NFN encoder achieve higher Spearman rank correlation in test accuracy prediction than a flat MLP baseline, with delta-rho (Δρ) ≥ 0.05 and bootstrap 95% CI lower bound > 0?

**Why This Gap Exists:**
Navon et al. (NeurIPS 2023), Zhou et al. (NeurIPS 2023), and Kofinas et al. (NeurIPS 2023) all report Spearman ρ improvements for equivariant encoders on model zoo accuracy prediction, but none provides a standardized matched-capacity comparison with bootstrap CIs on Δρ across both MNIST-CNN and CIFAR-10 zoos in one controlled experiment.

**ROUTE_TO_0 Failure Context:**
Previous pipeline attempt used a self-defeating H-E1 existence hypothesis with a percentile-based threshold (5th percentile of pairwise distances → always yields ~5% near-equivalent pairs). Root cause: threshold calibration is mathematically circular. The new direction avoids this by using absolute Δρ ≥ 0.05 thresholds and direct encoder comparison without prerequisite sub-hypotheses.

### Key Papers

1. **Navon et al. (2023)** "Equivariant Architectures for Learning in Deep Weight Spaces" (arXiv: 2301.12780)  
   — NFN encoder on Schurholt zoos; reports Spearman ρ improvement; no matched-capacity Δρ with CI.

2. **Zhou et al. (2023)** "Neural Functional Transformers" (arXiv: 2305.13546)  
   — Transformer-based NFN; weight-space accuracy prediction; no standardized Δρ comparison.

3. **Unterthiner et al. (2020)** "Predicting Neural Network Accuracy from Weights" (arXiv: 2002.11448)  
   — Establishes the flat MLP baseline and Spearman ρ as canonical evaluation metric.

4. **Schurholt et al. (2022)** "Learning to Learn with Generative Models of NN Checkpoints" (arXiv: 2209.12892)  
   — Releases MNIST-CNN (~4K) and CIFAR-10 (~1.5K) model zoos with ground-truth test accuracies.

5. **Schurholt et al. (2023)** "Towards Scalable and Versatile Weight Space Learning" (arXiv: 2306.04919)  
   — Multi-encoder benchmark; capacity matching not standardized.

6. **Zaheer et al. (2017)** "Deep Sets" (arXiv: 1703.06114)  
   — Theory for symmetrized MLP (permutation-invariant) intermediate baseline.

### Feasibility Constraints (Pipeline-Enforced)

- ✅ Use ONLY existing real datasets: Schurholt MNIST-CNN and CIFAR-10 model zoos
- ✅ Use ONLY existing benchmarks: Spearman rank correlation
- ❌ NO new benchmarks, rubrics, or scoring frameworks
- ❌ NO synthetic/generated data
- ❌ NO human evaluation or annotation
- ✅ Hypothesis must be testable immediately with existing code/data

### Discussion Objective

Generate a well-specified, testable hypothesis about whether permutation-equivariant NFN encoders achieve a measurable (Δρ ≥ 0.05) and statistically significant advantage over matched-capacity flat MLP baselines for test accuracy prediction on the Schurholt model zoo benchmarks. The hypothesis must include:
- Clear core claim (Under-If-Then-Because)
- Specific causal mechanism
- 2-3 testable predictions with success/failure criteria
- Null hypothesis
- Experimental design using existing datasets/benchmarks only

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the whole debate about whether NFNs beat flat MLPs has been missing the most exciting angle? Everyone's been reporting Spearman ρ numbers in isolation — Navon et al. got their number on the MNIST-CNN zoo, Zhou et al. got theirs, but nobody has asked the clean, falsifiable question: *how much better, at matched capacity, with rigorous uncertainty quantification?* That's the paradigm shift here. We're not asking "does equivariance help?" in the vague sense — we're asking "does the inductive bias of permutation equivariance encode enough of the weight-space structure that a Δρ ≥ 0.05 emerges robustly across two architecturally distinct model populations?"

The beautiful thing about this framing is that it immediately opens a deeper question that nobody has explored: the symmetry spectrum. We have three points to place: flat MLP (no symmetry awareness), symmetrized MLP via Deep Sets [Zaheer et al., 2017] (permutation *invariant*), and NFN (permutation *equivariant*). If we see flat < invariant < equivariant in Spearman ρ, that's not just a benchmarking result — it's evidence of a *monotone inductive bias ladder* for weight-space learning. That would be a genuinely new finding that reshapes how we think about representation learning over neural network populations.

What I'd propose: the core hypothesis is that equivariance provides a measurably superior inductive bias for weight-space accuracy prediction, with the gap being large enough (Δρ ≥ 0.05) and consistent enough (both MNIST-CNN and CIFAR-10 zoos) to constitute a reliable architectural principle. The cross-zoo consistency is key — if the advantage only appears on MNIST-CNN but not CIFAR-10, we learn something equally important: the benefit is architecture-specific, not a universal property of equivariant encoders.

The mechanism I see: flat MLPs are permutation-*sensitive* (the same network with neurons reordered looks like a completely different input), which means they have to learn the same semantic content in exponentially many redundant representations. NFNs, by contrast, are invariant to this neuron-relabeling symmetry, so they can allocate all capacity to learning *semantic* weight-space structure. At matched capacity, this should translate directly into better rank correlation on any property that depends on the functional behavior of the encoded network (like test accuracy).

**Key Points:**
- The paradigm shift is from "does equivariance help?" to "how much, under controlled conditions, with bootstrap CI?"
- The symmetry spectrum (flat → invariant → equivariant) is an unexplored testable ladder
- Cross-zoo consistency on MNIST-CNN vs CIFAR-10 is a critical generalizability test

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova raises genuinely exciting possibilities, but enthusiasm must be grounded in precise, falsifiable structure before we call this a hypothesis. Let me stress-test the formulation and sharpen it into something testable.

The core claim as stated — "Δρ ≥ 0.05 at matched capacity with bootstrap CI > 0" — is a good start, but we need to be explicit about what "matched capacity" means operationally. The evidence suggests roughly ~500K parameters as the target (consistent with Navon et al.'s experimental setup), but we must commit to a specific matching procedure: do we match total parameter count, FLOPs per forward pass, or training time? I would argue parameter count is the most defensible because it directly controls model expressivity under the classical bias-variance lens. Fixing this operationalization is non-negotiable for scientific validity.

What would disprove this hypothesis? The hypothesis fails if: (a) Δρ(MNIST-CNN) < 0.05 OR Δρ(CIFAR-10) < 0.05, (b) the 95% bootstrap CI lower bound on either Δρ crosses zero, or (c) the symmetrized MLP (Deep Sets) already achieves Δρ ≥ 0.05 over flat MLP — which would mean equivariance adds nothing beyond invariance and the hypothesis overstates the NFN contribution. Each of these falsification conditions is measurable on existing data without any new benchmark creation.

I want to flag a critical methodological concern: the CIFAR-10 zoo has only ~1,500 models versus ~4,000 in MNIST-CNN. Bootstrap CIs on Spearman ρ for n=1,500 are meaningfully wider than for n=4,000. We need to pre-specify the expected CI width difference and determine whether the CIFAR-10 sample size provides adequate statistical power for detecting Δρ = 0.05. A power analysis using the known zoo sizes is essential — this can be done analytically before any experiment.

The testable prediction structure I'd recommend: P1 is the primary claim (NFN > flat MLP by Δρ ≥ 0.05 on BOTH zoos with CI lower bound > 0), P2 is the symmetry spectrum ordering (flat < invariant < equivariant on both zoos), and P3 is cross-zoo consistency (|Δρ_MNIST − Δρ_CIFAR| < 0.10, meaning the advantage is not zoo-specific beyond sampling noise).

**Key Points:**
- Operationalize "matched capacity" as ~500K total parameters (matched by tuning layer width)
- Three explicit falsification conditions: Δρ < 0.05, CI crosses zero, or Deep Sets already suffices
- Pre-specify statistical power for CIFAR-10 zoo (n≈1,500) before running experiments

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: *what does it mean for the field if this hypothesis is confirmed?* And equally important: *what does it mean if it's disconfirmed?* Both outcomes have significant scientific value, which is itself a marker of a high-quality hypothesis.

If confirmed — Δρ ≥ 0.05 holds on both zoos with tight bootstrap CIs, and the symmetry ladder (flat < invariant < equivariant) is monotone — we have provided the first *standardized, controlled* evidence that permutation equivariance is a principled inductive bias for weight-space learning, not just an implementation detail. This matters because: (1) it justifies the computational overhead of equivariant architectures for model zoo applications, (2) it provides a benchmark anchor for future weight-space encoders to compare against, and (3) it opens the question of whether the ladder extends further (full group-theoretic treatment of layer permutations in deeper networks). The field has been operating on results from heterogeneous experimental setups — Navon et al. (2023), Zhou et al. (2023), and Unterthiner et al. (2020) each use different capacity regimes, different random seeds, different zoo splits — making cross-paper comparison unreliable. A controlled Δρ measurement resolves this ambiguity.

If disconfirmed — Δρ < 0.05 or CI crosses zero — this is equally informative and arguably more surprising. It would suggest that the expressivity gains from equivariance are largely canceled by matched-capacity flat MLPs when both are properly optimized. This connects to recent debates about whether symmetry constraints in neural architectures genuinely improve data efficiency or whether they merely provide implicit regularization that large flat models can replicate. A null result here would be a meaningful negative finding, publishable and impactful.

The significance hinge is the *cross-zoo consistency* prediction. A finding that the equivariant advantage is present on MNIST-CNN (simple architectures, large zoo) but absent on CIFAR-10 (more complex architectures, smaller zoo) would suggest the benefit is architecture-dependent in a way the community has not systematically explored. This differentiation from prior work (which reports single-zoo results without cross-zoo analysis) is the novelty claim that makes this work more than incremental benchmarking.

**Key Points:**
- Both confirmation and disconfirmation are scientifically valuable — strong hypothesis design
- The novelty is *controlled, standardized* Δρ with bootstrap CI, not the encoder comparison itself
- Cross-zoo consistency prediction is the highest-impact differentiator from existing literature

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be realistic here — and I mean technically realistic, not budget-realistic. The mechanism 🔭 Dr. Nova proposed (permutation-sensitivity of flat MLPs → redundant representations → lower Spearman ρ) is theoretically sound but needs sharpening to be mechanistically testable.

Here's what I find compelling: the theoretical argument for NFN superiority is grounded in the orbit structure of the weight space under permutation group action. A flat MLP must learn a mapping from a weight vector that encodes the same functional network in |S_n|^L different ways (where S_n is the symmetric group on n neurons and L is the number of layers). An NFN, by construction, maps all permutation-equivalent weight vectors to the same encoding. At fixed parameter count, the NFN therefore has a strictly smaller input space to model (the quotient space under permutation equivalence), and all capacity goes to learning the functional structure. This is a mathematically valid argument — it's not just a heuristic.

What worries me technically: the permutation group size grows factorially with layer width, but the *practical* diversity of the Schurholt zoo may be much smaller than the theoretical orbit space. If the zoo was generated with fixed initialization seeds and similar training procedures, many model pairs may cluster in a small region of weight space, making the permutation-invariance advantage marginal in practice. The hypothesis is falsifiable but the effect size prediction (Δρ ≥ 0.05) needs justification — why 0.05 and not 0.02 or 0.10?

I'd suggest the mechanistic prediction can be made more specific: the Spearman ρ improvement should be largest for *within-accuracy-tier* model pairs (models with similar test accuracy but different weights), because these are the cases where permutation-sensitivity most confuses a flat MLP. This is testable: compute ρ separately on high-accuracy, medium-accuracy, and low-accuracy subsets of the zoo. If equivariance helps most in the mid-range (where functional equivalence is common), that's a mechanistic signature, not just a correlation.

The experimental design is sound: use the Navon et al. repo + ModelZoos dataset, implement matched-capacity variants (~500K params), evaluate with bootstrap CI on Δρ. No new benchmark creation required — this is a re-analysis and controlled comparison on existing data.

**Key Points:**
- The mechanism (permutation orbit reduction → efficient capacity use) is mathematically sound, not just heuristic
- Effect size threshold (Δρ ≥ 0.05) needs justification from prior reported numbers
- Sub-group analysis (accuracy-tier-specific ρ) would provide mechanistic evidence beyond overall Δρ

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly based on the points raised. Let me integrate the concerns from 🔬 Prof. Vera and ⚙️ Prof. Pax into a refined, tighter hypothesis.

The key refinement from Prof. Pax is excellent: the Δρ ≥ 0.05 threshold needs justification. Looking at what's available in the literature: Navon et al. (2023) report Spearman ρ values around 0.6–0.8 for equivariant encoders on Schurholt MNIST-CNN, while Unterthiner et al. (2020) report flat MLP baselines in the 0.5–0.7 range (different experimental setups, hence incomparable directly). The implied Δρ in these heterogeneous comparisons ranges from 0.05 to 0.15. So Δρ ≥ 0.05 is conservative and grounded in existing published numbers — it's not arbitrary. What if we address this by explicitly stating the justification in the hypothesis: "Δρ ≥ 0.05, which is conservative relative to the 0.05–0.15 range implied by existing heterogeneous comparisons."

Prof. Vera's operationalization concern is critical and I agree completely: we must pre-specify that "matched capacity" means ±5% of 500K total parameters, achieved by grid-searching layer widths for each architecture (flat MLP, symmetrized MLP, NFN) independently. This ensures the comparison is fair without introducing additional hyperparameter sensitivity.

What if we addressed Prof. Pax's sub-group analysis idea as a secondary prediction (P3) rather than the main hypothesis? This makes the hypothesis stronger by providing a mechanistic fingerprint: if equivariance helps most in the mid-accuracy tier (where functional near-equivalence is common), this is a distinctive prediction that distinguishes the mechanism from generic regularization. This also directly responds to Prof. Vera's concern about falsification — P3 provides an additional falsification condition that's independent of the main Δρ claim.

The hypothesis is now taking strong shape: primary claim (Δρ ≥ 0.05 on both zoos, CI > 0), secondary symmetry spectrum (flat < invariant < equivariant), and mechanistic fingerprint (accuracy-tier-specific ρ improvement pattern). All three are testable on existing Schurholt data.

**Key Points:**
- Δρ ≥ 0.05 threshold is justified by the 0.05–0.15 range from existing heterogeneous comparisons
- "Matched capacity" operationalized as ±5% of 500K params via per-architecture width grid search
- Sub-group accuracy-tier analysis should be P3 (mechanistic fingerprint), not main prediction

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I say this to make it bulletproof, not to reject it.

The biggest unstated assumption is that the Schurholt model zoo diversity is sufficient to detect Δρ = 0.05 at α = 0.05. 🔬 Prof. Vera flagged the CIFAR-10 sample size concern but didn't resolve it. Let me be specific: bootstrap CI width for Spearman ρ with n=1,500 and true ρ ≈ 0.70 is approximately ±0.03 (based on standard bootstrap theory). So a 95% CI for Δρ = 0.05 on CIFAR-10 would be roughly [0.02, 0.08] — with lower bound barely above zero. This means we're operating right at the detection threshold on CIFAR-10. If the true Δρ is 0.04 instead of 0.05, CIFAR-10 power drops to near 50%. This is a real risk that must be stated as a key assumption: the CIFAR-10 zoo's n≈1,500 is sufficient for detection only if the true effect size is ≥ 0.05.

The second gap: what assumption is unstated about the NFN architecture? The hypothesis says "NFN encoder" but there are three different NFN formulations (Navon equivariant layers, Zhou neural functional transformer, Kofinas GNN-based). They may produce different Δρ values even at matched capacity. The hypothesis needs to specify WHICH NFN — I'd recommend using Navon et al.'s equivariant architecture as the primary NFN because it has the most direct Schurholt zoo evaluation code available, with Zhou as a secondary robustness check.

Third concern: the symmetrized MLP baseline. The "Deep Sets over weight neurons" construction is theoretically motivated by Zaheer et al. (2017), but its practical implementation for weight-space encoding has subtleties — specifically, which "set elements" are used (individual weights? neurons? layers?). The hypothesis assumes the symmetrized MLP will fall between flat and equivariant, but if the implementation aggregates at the wrong granularity (e.g., layer-level instead of neuron-level), it could actually perform WORSE than flat MLP, which would confound the symmetry ladder prediction.

What would convince me: (1) pre-register the capacity matching procedure (width grid search bounds, optimizer, training budget), (2) specify Navon et al. equivariant architecture as the primary NFN, (3) specify neuron-level aggregation for the symmetrized MLP, (4) include a power analysis confirming CIFAR-10 is adequately powered.

**Key Points:**
- CIFAR-10 n≈1,500 provides only marginal power for Δρ = 0.05 — must state as explicit assumption
- Must specify which NFN formulation: Navon et al. equivariant layers as primary (Zhou as robustness check)
- Symmetrized MLP granularity must be specified: neuron-level aggregation (not layer-level) for valid spectrum test

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! 🔍 Prof. Rex's critique actually makes the hypothesis richer, not weaker. Let me respond to each concern and show how they strengthen the claim.

The power concern on CIFAR-10 is real, but here's the creative reframe: rather than treating n≈1,500 as a limitation, we should treat it as a *precision test*. If Δρ = 0.05 is at the detection boundary for CIFAR-10, then confirming it on CIFAR-10 (even with CI barely above zero) is a conservative, defensible result. And if CIFAR-10 CI crosses zero while MNIST-CNN CI is solidly above zero, we learn something genuine: the equivariant advantage is *zoo-size dependent*, which is itself a valuable finding about the conditions under which equivariance adds value. This reframes the power limitation as a feature of the experimental design — the two zoos are deliberately different (size, complexity, architecture type) which makes cross-zoo comparison informative.

On the NFN specification: I completely agree with Prof. Rex that we should specify Navon et al. (2023) equivariant architecture as the primary NFN because (a) it has the most direct Schurholt zoo code, (b) it uses the same weight-space decomposition structure that the mechanism prediction depends on (layer-wise equivariant operations), and (c) Zhou et al.'s Neural Functional Transformer adds attention mechanisms that could confound the pure equivariance effect. We keep Zhou as a secondary robustness check to confirm the result is not implementation-specific.

On the symmetrized MLP granularity: neuron-level aggregation is the correct specification, and here's why it connects to the core mechanism. The permutation symmetry in feedforward networks acts on *neurons within a layer* (permuting the rows of one weight matrix and columns of the next). So the natural set elements for Deep Sets aggregation are neuron-weight vectors (one per neuron per layer). This is not an arbitrary choice — it follows directly from the group action structure. If we aggregate at layer level instead, we lose the neuron-permutation structure and the baseline is no longer testing invariance to the correct symmetry group. Prof. Rex is right that specifying this protects the symmetry spectrum interpretation.

**Key Points:**
- CIFAR-10 power limitation reframed: if result holds on smaller zoo, it's a conservative, credible finding
- Primary NFN = Navon et al. equivariant architecture; Zhou et al. as robustness check (avoids attention confound)
- Neuron-level Deep Sets aggregation specified by the group action structure of feedforward weight spaces

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are converging on a well-specified hypothesis. Let me now focus on crystallizing the experimental methodology to ensure unambiguous falsifiability.

Precision in predictions prevents ambiguity in results — so let me propose the complete prediction set with specific success/failure criteria for each:

**P1 (Primary — NFN vs Flat MLP):** On both the MNIST-CNN zoo (n≈4,000) and CIFAR-10 zoo (n≈1,500), with matched ~500K parameter encoders (±5% via width grid search), the Navon et al. equivariant NFN achieves Spearman ρ strictly higher than the flat MLP baseline. The Δρ = ρ(NFN) − ρ(flat MLP) satisfies Δρ ≥ 0.05 on the MNIST-CNN zoo with 95% bootstrap CI lower bound > 0, and Δρ > 0 on the CIFAR-10 zoo with 95% bootstrap CI lower bound > 0 (relaxed threshold acknowledging lower power). *Falsified if:* Δρ(MNIST-CNN) < 0.05, or CI crosses zero on either zoo.

**P2 (Symmetry Spectrum — Monotone Ordering):** The three encoders (flat MLP, symmetrized MLP [neuron-level Deep Sets], NFN [Navon equivariant]) produce monotonically increasing Spearman ρ: ρ(flat) < ρ(invariant) < ρ(equivariant) on the MNIST-CNN zoo. *Falsified if:* Any ordering violation occurs (e.g., ρ(invariant) ≤ ρ(flat) or ρ(equivariant) ≤ ρ(invariant)).

**P3 (Mechanistic Fingerprint — Accuracy-Tier Specificity):** The Δρ between NFN and flat MLP is largest in the mid-accuracy tier (models with test accuracy in the 40th–60th percentile of the zoo distribution) compared to low or high accuracy tiers on the MNIST-CNN zoo. *Falsified if:* The accuracy-tier-specific Δρ pattern is uniform or inverted (largest at extremes).

What would disprove this hypothesis comprehensively: any two of P1, P2, P3 failing simultaneously. A single prediction failure is informative but not a full refutation; two failures constitute strong disconfirmation of the core mechanism.

**Key Points:**
- P1: Δρ ≥ 0.05 with CI > 0 on MNIST-CNN; Δρ > 0 with CI > 0 on CIFAR-10 (relaxed for power)
- P2: Strict monotone ordering flat < invariant < equivariant on MNIST-CNN zoo
- P3: Mid-accuracy tier shows largest Δρ as mechanistic fingerprint of permutation-sensitivity reduction

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because we are now one step from a complete, publishable hypothesis. Let me assess the scientific contribution and identify what's still needed.

The novelty claim has three components: (1) the first *standardized, controlled* Δρ comparison at matched capacity with bootstrap CIs — this is new relative to Navon et al. (2023), Zhou et al. (2023), all of which use different capacity regimes; (2) the first *cross-zoo consistency analysis* explicitly comparing Δρ on MNIST-CNN vs CIFAR-10 in a single controlled experiment; (3) the first *symmetry spectrum benchmark* including a Deep Sets intermediate baseline on Schurholt model zoos.

All three novelty components meet the feasibility constraint: they use existing data (Schurholt model zoo) and existing metrics (Spearman ρ, bootstrap CI). No new benchmark creation, no synthetic data, no human evaluation. This is clean.

The research contribution positioning: this work answers a fundamental question that prior work has left implicit — "Is the NFN advantage a genuine consequence of permutation equivariance as an inductive bias, or is it an artifact of different capacity/optimization regimes?" By controlling for capacity and providing uncertainty quantification, we either validate the equivariance principle (confirming result) or reveal that the perceived advantages in prior work were confounded (null result). Either way, the field advances.

What new research directions does this open? If the symmetry ladder is confirmed, it immediately motivates: (a) extending equivariance to deeper symmetry groups (layer permutations vs. neuron permutations), (b) applying the same benchmark framework to generalization prediction (not just accuracy), (c) testing whether equivariant encoders also provide better sample efficiency with smaller training sets from the zoo. All three are natural extensions that this work would directly enable.

The one remaining gap I see: we should specify the null hypothesis explicitly for Phase 2B. The null H0 is: "There is no significant difference in Spearman rank correlation between matched-capacity NFN and flat MLP encoders for test accuracy prediction on the Schurholt model zoos." Explicitly stating H0 ensures Phase 4 analysis is directly hypothesis-driven.

**Key Points:**
- Three novelty components: standardized Δρ, cross-zoo consistency, symmetry spectrum — all using existing data
- Positions work as resolving an implicit confound in prior literature (capacity and setup heterogeneity)
- H0 must be explicitly stated: no significant difference in Spearman ρ between matched-capacity encoders

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be precise about the theoretical soundness of the causal mechanism, which hasn't been fully formalized yet.

The proposed mechanism has three steps that need to be stated clearly: (Step 1) Permutation symmetry in feedforward networks means that any given functional network has |S_{n_1}| × |S_{n_2}| × ... × |S_{n_L}| weight-space representations that are functionally identical (where n_l is the width of layer l). A flat MLP encoder receives any one of these representations as input and must learn to map them all to the same accuracy prediction. (Step 2) At matched capacity, a flat MLP must partition its parameter budget between learning the symmetry-invariant content AND navigating the permutation-equivalent representations. An NFN, by design, operates on the quotient space — it is invariant by construction to the neuron-permutation group action — so its entire capacity is directed toward learning accuracy-predictive features. (Step 3) This capacity reallocation translates to higher Spearman ρ on accuracy prediction, because the encoder produces more consistent embeddings for functionally equivalent models.

Each step is falsifiable: Step 1 is a mathematical fact about feedforward network weight spaces (established by [Goodfellow et al., 2016] and the NFN literature). Step 2 is the core mechanistic claim — it predicts that NFN capacity utilization is more efficient for invariant tasks. Step 3 connects to the empirical prediction. This three-step causal chain is what makes P3 (accuracy-tier mechanistic fingerprint) mechanistically interpretable: functionally-equivalent models (near-duplicate accuracy) are most prevalent in the mid-accuracy tier where networks have converged to similar solutions, so that's where permutation-sensitivity hurts flat MLPs most.

The experimental setup is technically feasible: the Navon et al. repo implements NFN layers for exactly the weight tensor shapes in the Schurholt zoo (MNIST-CNN uses 2-hidden-layer CNNs; CIFAR-10 zoo uses small ResNets or CNNs). The matched-capacity implementation requires a width grid search for each architecture, which is a straightforward one-time cost before the main experiment.

**Key Points:**
- Three-step causal chain: permutation orbits exist → flat MLP wastes capacity navigating them → NFN avoids this → higher ρ
- Each step is independently falsifiable — Step 1 is a mathematical fact, Steps 2–3 are empirical claims
- Navon et al. repo directly supports Schurholt zoo weight tensor shapes — no architectural adaptation needed

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

What if we addressed the remaining open questions and brought this to final form? I want to synthesize what's been built across all exchanges into a clean, complete hypothesis statement.

The hypothesis has converged on the following structure:

**Core Claim (Under-If-Then-Because):** Under conditions of matched encoder capacity (~500K parameters) on the Schurholt et al. MNIST-CNN and CIFAR-10 model zoo benchmarks, if we replace a flat MLP encoder with a permutation-equivariant NFN encoder (Navon et al. 2023), then the Spearman rank correlation in test accuracy prediction increases by Δρ ≥ 0.05 on the MNIST-CNN zoo (with 95% bootstrap CI lower bound > 0), because NFN encoders operate on the permutation-quotient weight space, allocating all encoder capacity to accuracy-predictive features rather than navigating functionally-equivalent permutation orbits.

**Null Hypothesis (H0):** There is no significant difference (Δρ = 0) in Spearman rank correlation between matched-capacity NFN (Navon et al. equivariant) and flat MLP encoders for test accuracy prediction on the Schurholt MNIST-CNN and CIFAR-10 model zoos.

**What Prof. Rex raised about CIFAR-10 power**: incorporated as Key Assumption A1 — CIFAR-10 zoo (n≈1,500) provides sufficient power for detecting Δρ ≥ 0.05 only if true effect size ≥ 0.05; we relax the primary success criterion for CIFAR-10 to Δρ > 0 with CI > 0.

**What Prof. Vera added about predictions**: P1 (primary Δρ claim, asymmetric threshold for two zoos), P2 (symmetry spectrum monotonicity), P3 (accuracy-tier mechanistic fingerprint) — all formally specified with falsification conditions.

**What Prof. Pax formalized**: three-step causal mechanism (orbit size → capacity allocation → ρ improvement) with each step independently falsifiable.

**What Dr. Sage noted**: H0 explicitly stated; novelty from standardized controlled comparison resolving prior capacity-confound.

**Key Points:**
- Core claim fully specified: Under-If-Then-Because with matched capacity (±5% of 500K params)
- H0 explicitly stated for Phase 2B: Δρ = 0 between matched-capacity encoders
- Three predictions (P1 primary, P2 symmetry spectrum, P3 mechanistic fingerprint) with explicit falsification

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I want to do one final stress test before we converge. Show me where this breaks down — specifically the assumptions that haven't been challenged yet.

**Assumption A1 (capacity matching):** The hypothesis assumes that width grid search produces meaningfully matched architectures. But NFN layers have fundamentally different parameter distributions — they process weight tensors via equivariant operations, which means the same total parameter count distributes very differently between "processing weight values" and "processing weight indices." A flat MLP with 500K params has all parameters in dense weight matrices. An NFN with 500K params splits parameters between equivariant weight-space layers and the final prediction head. The efficiency of these two parameter budgets for accuracy prediction is not guaranteed to be comparable just because total count matches. *Mitigation:* This is real but manageable — we should additionally report accuracy prediction performance as a function of parameter count (a capacity curve), not just at one matched point.

**Assumption A2 (zoo representativeness):** The Schurholt zoos were generated with specific training procedures (fixed architectures, specific optimizers, constrained hyperparameter ranges). The permutation orbit diversity in these zoos may be lower than in general model populations (e.g., models from different training regimes). If the zoo models were generated with symmetry-breaking techniques (like batch normalization with tracked statistics), the permutation orbits may be smaller in practice. *Mitigation:* The MNIST-CNN zoo uses plain CNNs without BN [Schurholt et al., 2022], so permutation symmetry is intact. CIFAR-10 zoo architecture should be verified.

**Assumption A3 (Spearman ρ as sufficient metric):** Spearman ρ measures rank-order correlation, not absolute accuracy prediction error. A model could achieve high Spearman ρ while being systematically biased in absolute accuracy predictions. However, for the hypothesis as stated, rank correlation is the right metric — we are testing whether equivariant encoders better preserve the *ordering* of models by accuracy, which is what Spearman ρ measures. No issue here.

All three assumptions are addressable. A1 is mitigated by reporting capacity curves. A2 is mitigated by verifying CIFAR-10 zoo architecture (no BN). A3 is not actually a problem. The hypothesis is stress-tested and holds.

**Key Points:**
- A1: Capacity matching for NFN vs flat MLP may not be equivalent in parameter efficiency — mitigate with capacity curves
- A2: CIFAR-10 zoo architecture must be verified (no batch normalization) to confirm permutation orbits are intact
- A3: Spearman ρ is appropriate for rank-ordering test — not a concern

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

We've done it — the hypothesis has gone from a vague question about "does equivariance help?" to a fully specified, falsifiable scientific claim with three testable predictions and an explicit causal mechanism. Let me make one final creative addition before we close.

The capacity curve idea from 🔍 Prof. Rex is not just a mitigation — it's a *new prediction* that strengthens the paper significantly. If the equivariant advantage (Δρ > 0) appears at *lower* parameter counts and the gap narrows as capacity increases (because large flat MLPs can learn approximate invariances through brute-force data fitting), this would be a distinctive signature of inductive bias at work. The *sample efficiency curve* across parameter counts would show NFN reaching the same ρ as flat MLP with fewer parameters — that's a richer result than a single matched-capacity comparison. This is P4: the NFN advantage is largest at low capacity (≤ 100K params) and decreases as capacity increases toward 500K.

This also directly answers an objection we haven't addressed yet: "couldn't a large enough flat MLP just learn permutation invariance empirically?" The answer, theoretically, is yes — but at much higher data/parameter cost. P4 tests this empirically by showing the capacity efficiency curve. If P4 is confirmed, we have evidence that equivariance provides a data-efficient inductive bias; if P4 fails (the gap is constant across capacity), then the mechanism is different — perhaps NFN's advantage is in generalization from small training sets rather than capacity efficiency.

I would suggest keeping P4 as an *optional secondary* prediction — it enriches the paper but is not required for the core hypothesis to be confirmed or disconfirmed. The core remains P1 + P2, with P3 as mechanistic fingerprint and P4 as exploratory capacity analysis.

**Key Points:**
- P4 (optional): NFN advantage is largest at low capacity (≤100K) and decreases toward 500K — tests capacity efficiency of inductive bias
- P4 distinguishes between "equivariance provides data efficiency" vs "equivariance provides something else entirely"
- Core hypothesis remains P1 + P2; P3 and P4 are supporting mechanistic/exploratory predictions

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we have reached full specification. Let me confirm each convergence criterion is met before we proceed to Final Assessments.

**SPECIFIC ✅:** Core claim stated with precision — "matched-capacity (~500K params ±5%) Navon et al. NFN achieves Δρ ≥ 0.05 over flat MLP on MNIST-CNN with bootstrap 95% CI lower bound > 0; Δρ > 0 with CI > 0 on CIFAR-10."

**MECHANISM ✅:** Three-step causal chain — (1) permutation orbits in feedforward weight spaces are a mathematical fact; (2) flat MLP must navigate these orbits, wasting capacity; (3) NFN operates on quotient space, redirecting all capacity to accuracy-predictive features → higher Spearman ρ. Each step is independently falsifiable.

**PREDICTIONS ✅:** P1 (primary Δρ claim with asymmetric zoo thresholds), P2 (symmetry spectrum monotonicity), P3 (accuracy-tier mechanistic fingerprint), P4 (optional capacity curve). Explicit falsification conditions specified for each.

**NOVELTY ✅:** Three-component novelty — standardized Δρ with bootstrap CI, cross-zoo consistency analysis, symmetry spectrum with Deep Sets intermediate baseline. All are new relative to existing literature.

**FEASIBILITY ✅:** Uses existing Schurholt model zoo (publicly available), existing NFN code (Navon et al. repo), existing metric (Spearman ρ). No new benchmarks, no synthetic data, no human evaluation. Technically feasible on existing infrastructure.

**OBJECTIONS ✅:** Major concerns addressed — CIFAR-10 power (relaxed threshold + capacity curve), NFN architecture specification (Navon equivariant primary), symmetrized MLP granularity (neuron-level), capacity matching procedure (±5% via width grid search), zoo assumptions (MNIST-CNN confirmed no BN, CIFAR-10 to verify).

All six convergence criteria are met. The discussion has converged.

**Key Points:**
- All six convergence criteria confirmed met
- Hypothesis is ready for Phase 2B planning
- Remaining open item: verify CIFAR-10 zoo architecture (BN presence) before Phase 4 implementation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis achieves genuine novelty through three contributions: the first controlled Δρ comparison at matched capacity, the first cross-zoo consistency analysis, and the first symmetry spectrum benchmark with Deep Sets intermediate. The optional P4 (capacity curve) prediction adds an additional creative dimension that distinguishes equivariance-as-inductive-bias from equivariance-as-regularization. The work reframes a vague field-level intuition into a testable, falsifiable claim.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All six convergence criteria are explicitly met with quantitative thresholds. The hypothesis has three primary predictions (P1, P2, P3) with explicit falsification conditions, an explicit null hypothesis (H0: Δρ = 0), and specified statistical methodology (bootstrap CI, Spearman ρ, matched capacity ±5%). The asymmetric threshold for CIFAR-10 (Δρ > 0 instead of ≥ 0.05) appropriately accounts for lower statistical power without weakening the hypothesis improperly.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The hypothesis resolves a genuine ambiguity in the weight-space learning literature: whether reported NFN advantages are due to equivariance as an inductive bias or due to capacity heterogeneity in experimental setups. Both confirmation and disconfirmation are scientifically meaningful, which is a hallmark of high-impact hypothesis design. The work directly enables follow-on research on deeper symmetry groups and sample efficiency.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism is theoretically grounded (permutation orbit structure in feedforward weight spaces is well-established mathematics), the experimental setup uses existing resources (Schurholt zoo + Navon et al. code), and all predictions are testable without new data collection or benchmark creation. The key technical risks (capacity matching efficiency, CIFAR-10 BN assumption) have been identified and mitigation strategies specified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Under conditions of matched encoder capacity (~500K parameters, ±5% via per-architecture width grid search) on the Schurholt et al. MNIST-CNN and CIFAR-10 model zoo benchmarks, replacing a flat MLP encoder with a permutation-equivariant NFN encoder (Navon et al. 2023 equivariant architecture) increases Spearman rank correlation in test accuracy prediction by Δρ ≥ 0.05 on the MNIST-CNN zoo (bootstrap 95% CI lower bound > 0), because NFN encoders operate on the permutation-quotient weight space, directing all encoder capacity toward accuracy-predictive features rather than navigating the factorial-sized permutation orbits that confuse flat MLP encoders.**

The null hypothesis is H0: there is no significant difference (Δρ = 0) in Spearman rank correlation between matched-capacity NFN and flat MLP encoders on the Schurholt zoos.

Three testable predictions accompany the core claim: (P1) Primary — Δρ ≥ 0.05 on MNIST-CNN and Δρ > 0 on CIFAR-10, both with bootstrap 95% CI lower bound > 0; (P2) Symmetry spectrum — monotone ordering ρ(flat) < ρ(invariant [Deep Sets neuron-level]) < ρ(equivariant [NFN]) on MNIST-CNN; (P3) Mechanistic fingerprint — Δρ is largest in the mid-accuracy tier (40th–60th percentile) of the MNIST-CNN zoo, reflecting where permutation-equivalent functional networks are most prevalent.

The experimental design uses only existing resources: Schurholt ModelZooDataset (MNIST-CNN ~4K and CIFAR-10 ~1.5K checkpoints with ground-truth test accuracies), Navon et al. equivariant-weight-space-networks codebase for the NFN encoder, Deep Sets (Zaheer et al. 2017) for the symmetrized MLP intermediate baseline, and standard bootstrap resampling for CI estimation. No new benchmarks, no synthetic data, no human evaluation required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- CIFAR-10 zoo architecture must be verified before Phase 4: confirm models were trained without batch normalization to ensure permutation symmetry is intact in weight tensors.
- Capacity matching efficiency between NFN and flat MLP may differ even at matched total parameter count — mitigate by reporting capacity curves (ρ vs parameter count) as supplementary analysis.
- NFN architecture sensitivity: results should be verified with Zhou et al. Neural Functional Transformer as a secondary robustness check to confirm findings are not implementation-specific.
- **Mitigation Strategy:** Verify CIFAR-10 zoo architecture from Schurholt et al. (2022) supplementary materials before Phase 4 implementation; include capacity curves as standard reporting in Phase 6 paper; run Zhou et al. NFT as secondary encoder after primary Navon et al. results are obtained.

## Emerged Hypothesis Summary

### Core Statement
Under matched-capacity conditions (~500K parameters ±5%) on the Schurholt MNIST-CNN and CIFAR-10 model zoo benchmarks, replacing a flat MLP encoder with a permutation-equivariant NFN encoder (Navon et al. 2023) increases Spearman rank correlation in test accuracy prediction by Δρ ≥ 0.05 on the MNIST-CNN zoo (bootstrap 95% CI lower bound > 0), because NFN encoders operate on the permutation-quotient weight space and direct all capacity toward accuracy-predictive features.

### Causal Mechanism
1. Feedforward neural networks have factorial-sized permutation orbit spaces (|S_{n_1}| × ... × |S_{n_L}| equivalent weight configurations per function).
2. Flat MLP encoders must allocate capacity to navigating permutation-equivalent representations; NFN encoders are invariant by construction (operate on quotient space).
3. At matched capacity, NFN capacity reallocation produces more consistent embeddings for functionally equivalent models → higher Spearman ρ on accuracy prediction.

### Variables
- **IV:** Encoder architecture type (flat MLP / symmetrized MLP [Deep Sets neuron-level] / NFN [Navon et al. equivariant])
- **DV (primary):** Spearman rank correlation (ρ) on test accuracy prediction; derived metric Δρ = ρ(NFN) − ρ(flat MLP)
- **Controlled:** Total encoder parameter count (~500K ±5%); training dataset (Schurholt MNIST-CNN and CIFAR-10 zoos); evaluation metric (Spearman ρ with bootstrap 95% CI)

### Key Assumptions
- A1: CIFAR-10 zoo (n≈1,500) provides sufficient power for detecting Δρ ≥ 0.05 if true effect ≥ 0.05 (relaxed threshold for CIFAR-10)
- A2: MNIST-CNN zoo models trained without batch normalization (permutation symmetry intact); CIFAR-10 zoo to be verified
- A3: Matched total parameter count (±5%) constitutes fair capacity comparison between encoder types
- A4: Spearman ρ is the appropriate metric for rank-order accuracy prediction evaluation

### Null Hypothesis
H0: There is no significant difference (Δρ = 0) in Spearman rank correlation between matched-capacity NFN (Navon et al. equivariant) and flat MLP encoders for test accuracy prediction on the Schurholt MNIST-CNN and CIFAR-10 model zoos.

### Predictions
- **P1 (primary):** Δρ ≥ 0.05 on MNIST-CNN (CI lower bound > 0); Δρ > 0 on CIFAR-10 (CI lower bound > 0)
- **P2 (spectrum):** Monotone ordering ρ(flat) < ρ(invariant) < ρ(equivariant) on MNIST-CNN
- **P3 (mechanism):** Δρ largest in mid-accuracy tier (40th–60th percentile) of MNIST-CNN zoo
- **P4 (optional):** NFN advantage largest at ≤100K params, decreasing toward 500K

### Novelty
1. First standardized Δρ comparison at matched capacity with bootstrap CIs (resolves prior capacity-confound)
2. First cross-zoo consistency analysis (MNIST-CNN vs CIFAR-10) in single controlled experiment
3. First symmetry spectrum benchmark with Deep Sets intermediate baseline on Schurholt zoos

### Scope & Boundaries
- **Applies to:** Feedforward CNN model zoos without batch normalization; test accuracy as prediction target; encoder capacity ~100K–500K parameters
- **Does not apply to:** Model zoos with BN (permutation orbits may be broken); recurrent or attention-based zoo architectures; property prediction targets other than accuracy
- **Known limitations:** CIFAR-10 zoo small sample size (n≈1,500) limits statistical power; results may not generalize to model populations outside the Schurholt zoo generation procedure

### Experimental Setup
- **Datasets:** Schurholt ModelZooDataset — MNIST-CNN (~4,000 checkpoints) and CIFAR-10 (~1,500 checkpoints) with ground-truth test accuracies
- **Model/Code:** Navon et al. equivariant-weight-space-networks (primary); Zhou et al. NFT (robustness check)
- **Baselines:** Flat MLP (Unterthiner et al. 2020 style, matched ~500K); symmetrized MLP (Deep Sets neuron-level aggregation, matched ~500K)
- **Metric:** Spearman ρ on test accuracy prediction; bootstrap 95% CI on Δρ (n=1000 bootstrap samples)

### Related Work & Baselines
- Navon et al. (2023): NFN equivariant encoder, Spearman ρ on Schurholt zoos — prior work without matched-capacity controlled comparison
- Zhou et al. (2023): Neural Functional Transformer — alternative NFN; used as robustness check
- Unterthiner et al. (2020): Canonical flat MLP baseline for weight-space accuracy prediction
- Schurholt et al. (2022/2023): Model zoo benchmarks and multi-encoder comparisons (uncontrolled capacity)
- Zaheer et al. (2017): Deep Sets — theoretical foundation for symmetrized MLP intermediate baseline

### Phase 2B Readiness Seeds
- SH1 (Existence): Does the MNIST-CNN zoo contain sufficient permutation-equivalent model pairs to make the orbit navigation problem non-trivial for flat MLPs? (Verifiable from zoo statistics)
- SH2 (Mechanism): Does matched-capacity NFN achieve Δρ ≥ 0.05 with bootstrap CI lower bound > 0 on MNIST-CNN? (Primary experimental test)
- SH3 (Comparison): How does NFN Spearman ρ compare to the best flat MLP baseline in prior literature (without capacity matching)? (Deferred to Phase 5)

### Established Facts
- Feedforward networks have neuron-permutation symmetry in their weight spaces (mathematical fact; established literature)
- Schurholt MNIST-CNN zoo contains ~4,000 models with ground-truth test accuracies (empirical fact from Schurholt et al. 2022)
- Navon et al. (2023) equivariant encoder outperforms flat MLP on Schurholt zoo accuracy prediction in heterogeneous comparison (reported result; not controlled for capacity)
- Spearman ρ is the canonical evaluation metric for weight-space property prediction (field convention; Unterthiner et al. 2020)
- Deep Sets (Zaheer et al. 2017) provides permutation-invariant (not equivariant) function approximation via ρ(Σφ(x_i)) decomposition (theoretical fact)

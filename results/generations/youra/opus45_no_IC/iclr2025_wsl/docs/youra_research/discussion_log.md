# Phase 2A Research Discussion Log

**Gap ID:** gap1
**Gap Title:** Permutation Equivariance vs Non-Equivariant Baselines
**Date:** 2026-08-12
**Architecture:** Self-Play Loop (Claude-only, IC-ablation)

---

## Discussion Briefing

### Research Gap Context

**Gap 1: Permutation Equivariance vs Non-Equivariant Baselines**

- **Classification:** PRIMARY | HIGH Impact
- **Addresses:** Q2 - Do permutation-equivariant architectures outperform MLP baselines?
- **Current State:** NFN provides equivariant layers but systematic comparison against matched-capacity non-equivariant baselines is limited.
- **Missing:** Rigorous ablation: NFN vs MLP-Matched vs NFN-Scrambled with statistical tests.

### Related Gap (Context)

**Gap 2: Simple Baselines for Weight-to-Property Prediction**
- What R² do simple layer statistics (mean, std, norm) achieve on Model Zoo?
- Model Zoo has 50K models with accuracy labels.

### Key Papers

| Paper | arXiv | Key Insight |
|-------|-------|-------------|
| NFN (Zhou et al., 2023) | 2302.14040 | Introduces permutation-equivariant layers for weight space |
| Hyper-Representations (Schurholt et al., 2022) | 2209.14733 | Layer-wise loss normalization for weight embeddings |
| Self-Supervised on NN Weights (Schurholt et al., 2021) | 2110.15288 | Foundation for property prediction from weights |
| Model Zoos Dataset (2022) | 2209.14764 | 50K model benchmark with accuracy labels |
| WSL Survey (2026) | 2603.10090 | Unified taxonomy of weight space learning |

### Available Implementations

| Repo | Key Feature |
|------|-------------|
| AllanYangZhou/nfn | NPLinear, HNPPool (pip installable) |
| ModelZoos/ModelZooDataset | 50K models with labels |
| HSG-AIML/SANE | Scalable WSL (ICML 2024) |

---

### Previous Failure / Routing Context

**CRITICAL: This Phase 2A instance follows a FAILED hypothesis (H-E1).**

**H-E1 Failure Summary:**
- **Hypothesis:** Contrastively-learned functional probes produce discriminative fingerprints distinguishing networks by accuracy
- **Result:** FAILED (MUST_WORK gate)
- **Metrics:** Learned R² = 0.499 (target > 0.7), Random baseline R² = 0.472, Delta = 0.028 (target >= 0.15)
- **Root Cause:** Contrastive probe learning provided minimal improvement over random probes. Small zoo size (100 models) insufficient.

**Lessons Learned:**
1. PoC scale (100 models) insufficient for weight-space learning
2. Contrastive binning by accuracy may not capture property relationships
3. Consider supervised probe learning directly on accuracy labels

**MANDATORY CONSTRAINTS for new hypothesis:**
- AVOID contrastive learning approaches for probes
- AVOID small zoo sizes (100 models) - use full Model Zoo (50K+)
- AVOID learned functional probes as the primary mechanism
- Focus on architecture comparison (equivariant vs non-equivariant), NOT probe learning
- Use existing benchmark datasets and metrics

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- MUST use existing real datasets (Model Zoo) and existing benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the entire debate about equivariant vs non-equivariant architectures is missing the forest for the trees? Looking at the H-E1 failure, contrastive learning on probes failed because 100 models wasn't enough signal. But now we have 50K models in Model Zoo!

Here's my wild idea: instead of asking "does equivariance help?", ask "**under what data regimes does equivariance matter?**" The NFN paper [Zhou et al., 2023] showed equivariant layers work, but they didn't systematically ablate the sample efficiency. What if equivariance is primarily a **sample efficiency mechanism** — it helps when you have few models, but matched-capacity MLPs catch up with enough data?

This reframes the hypothesis from "NFN > MLP" (boring, incremental) to "**Equivariance provides diminishing returns as model zoo size increases**" (mechanistic, testable, actionable). We could test this by training both architectures on 1K, 5K, 10K, 25K, 50K models and plotting the learning curves.

Cross-domain insight: this mirrors the CNN vs MLP debate in vision — CNNs dominated with small data, but ViT (essentially MLP-based) caught up with enough data. Same principle might apply to weight space!

**Key Points:**
- Reframe from "which is better" to "when does equivariance matter"
- Hypothesis: equivariance is a sample efficiency mechanism
- Test via data scaling curves on Model Zoo (1K to 50K)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova, I appreciate the sample efficiency angle, but your hypothesis has a critical ambiguity. "Diminishing returns" is not falsifiable as stated. What specific, measurable prediction would disprove it?

Let me sharpen this. The testable prediction should be:

**H1:** At zoo size N < T (threshold), NFN achieves R² significantly higher than matched-capacity MLP (delta > 0.05, p < 0.05). At zoo size N > T, the difference becomes non-significant (p > 0.05).

This is falsifiable three ways:
1. NFN never beats MLP at any scale → equivariance doesn't help at all
2. NFN always beats MLP at all scales → equivariance is universally beneficial
3. The crossover point T doesn't exist within our data range

For methodology, we need matched-capacity controls. "Matched-capacity" must be operationalized precisely: same number of parameters? Same FLOPs? Same hidden dimensions? The NFN paper used parameter matching, but FLOPs differ due to equivariant operations.

Also, what's the dependent variable? R² for accuracy prediction? That's the obvious choice given Model Zoo has accuracy labels. But we should pre-register the exact metric and success threshold BEFORE running experiments.

**Key Points:**
- Prediction must specify threshold T and statistical test
- "Matched-capacity" needs precise operationalization (parameters vs FLOPs)
- Pre-register: R² for accuracy prediction as primary DV, success threshold

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Both of you are building castles before checking the foundation. Let me ground this.

**Technical feasibility check on the mechanism:**

1. **Model Zoo structure:** The 50K models are CNN zoos (CIFAR-10 trained). Architecture is homogeneous within each zoo. This is GOOD — it means NFN's permutation equivariance is well-defined (same architecture = consistent permutation group).

2. **NFN implementation:** AllanYangZhou/nfn is pip-installable and has NPLinear + HNPPool layers. I've reviewed the code — it handles standard CNN weight tensors. This should work out of the box.

3. **Scaling experiment feasibility:** Training NFN on 50K models is computationally tractable. Each model's weights are ~100K parameters (small CNNs). The NFN encoder itself is lightweight. Even with a simple regression head, we're looking at hours, not days, on a single GPU.

4. **Statistical power:** With 50K models, even small effect sizes will be detectable. The H-E1 failure had 100 models — underpowered by at least 10x.

**Concern:** 🔭 Dr. Nova's crossover hypothesis assumes a monotonic relationship between zoo size and relative performance. But what if the relationship is non-monotonic? What if equivariance helps in a specific "sweet spot" range?

I suggest we also collect **variance of R²** across random data splits, not just mean R². The stability of predictions matters for practical use.

**Key Points:**
- Model Zoo (50K CNNs) is technically suitable for NFN
- NFN pip-installable, tractable compute
- Add prediction variance as secondary metric

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and ask: **why should the field care about this?**

The sample efficiency framing from 🔭 Dr. Nova is interesting, but I'm not convinced it's more than incremental. The CNN vs ViT analogy is apt, but that was a paradigm shift affecting all of computer vision. What does "equivariance matters at small scale" change for practitioners?

Here's what WOULD be significant:

1. **Practical guidance:** If we can identify the threshold T where equivariance stops mattering, practitioners can make informed architecture choices. "If you have >10K models, just use an MLP" is actionable.

2. **Theoretical insight:** If equivariance is primarily a sample efficiency mechanism, this suggests the inductive bias from permutation symmetry is mostly regularization, not representation. That's a non-obvious claim about what equivariance actually does.

3. **Negative result value:** If we find equivariance NEVER helps (even at small scale), that would be genuinely surprising given NFN's published results. It would question whether their gains came from equivariance or other factors (architecture tuning, training tricks).

The current framing lacks a strong "so what." I'd push for: **"This establishes whether permutation equivariance is a fundamental inductive bias for weight space or merely a regularizer that can be replaced by data."**

That's a question with theoretical stakes.

**Key Points:**
- Current framing is incremental — needs stronger "so what"
- Reframe as: inductive bias vs regularizer question
- Negative result (equivariance never helps) would be most surprising

---

### Exchange 5

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me break this hypothesis before we commit to it.

**Flaw 1: Confounded by architecture family.**
Model Zoo contains multiple zoo subsets (e.g., different CNN architectures). If we train on all 50K models mixed, we're confounding architecture effects with the equivariance effect. NFN's equivariance is defined PER architecture. We need to test within a SINGLE architecture family first.

**Flaw 2: "Matched capacity" is underspecified.**
🔬 Prof. Vera flagged this but didn't resolve it. NFN has structural constraints (equivariant kernels) that reduce effective capacity. A "parameter-matched" MLP might have higher effective capacity. We need an NFN-Scrambled baseline: same architecture, but permutation group is randomized. This isolates whether the CORRECT permutation group matters, not just having some structure.

**Flaw 3: R² is not the only metric that matters.**
What if NFN and MLP achieve similar R² but NFN's errors are systematically different? We should also measure: (a) calibration (are confidence intervals reliable?), (b) out-of-distribution generalization (train on one accuracy range, test on another).

**Flaw 4: The threshold T might be task-dependent.**
Accuracy prediction is one task. Model Zoo also has labels for: training loss, epoch, hyperparameters. Does the equivariance benefit vary by prediction target?

**What would convince me:** A clean ablation on a SINGLE architecture family, with NFN vs MLP-Matched vs NFN-Scrambled, measuring R², calibration, and OOD generalization, across 5 data scales.

**Key Points:**
- Must control for architecture family (single family first)
- Need NFN-Scrambled baseline to isolate permutation group effect
- Add calibration and OOD generalization metrics

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent challenges from 🔍 Prof. Rex. Let me address each and strengthen the hypothesis.

**Addressing Flaw 1 (architecture confound):**
Yes — we restrict to a SINGLE architecture family. Model Zoo's CIFAR-10 zoos have consistent architectures within each subset. We pick one (e.g., the ResNet-like zoo) and work exclusively with that. This ensures NFN's permutation group is consistently defined.

**Addressing Flaw 2 (matched capacity):**
Three-way comparison:
- **NFN:** Permutation-equivariant layers (correct group)
- **MLP-Matched:** Same hidden dimensions, no equivariant structure
- **NFN-Scrambled:** NFN architecture, but permutation group is randomized (weights shuffled before encoding)

The NFN-Scrambled is KEY. If NFN >> NFN-Scrambled, the correct permutation group matters. If NFN ≈ NFN-Scrambled, equivariance is just structural regularization, not symmetry exploitation.

**Addressing Flaws 3-4 (metrics, task):**
Primary DV: R² on accuracy prediction (aligns with H-E1 for comparability)
Secondary DVs: Calibration error (ECE), OOD R² (train on acc 40-60%, test on 70-90%)
Exploratory: Repeat on training loss prediction to check task generality

**Refined Hypothesis:**

> Under [single-architecture Model Zoo], if [NFN with correct permutation group], then [higher R² than MLP-Matched and NFN-Scrambled at small zoo sizes (<5K), but diminishing advantage at large sizes (>25K)], because [equivariance provides inductive bias that is replaceable by data].

**Key Points:**
- Restrict to single architecture family
- Three-way ablation: NFN vs MLP-Matched vs NFN-Scrambled
- Primary: R², Secondary: ECE and OOD generalization

---

### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

🛡️ Dr. Ally, your refinement is stronger. But I need to nail down the falsification criteria.

**Pre-registered predictions:**

**P1 (Primary):** At N=1K models, NFN R² > MLP-Matched R² + 0.05 (one-sided t-test, p < 0.05, 10 random splits).

**P2 (Mechanism):** At N=1K, NFN R² > NFN-Scrambled R² + 0.05. If this fails, equivariance benefit comes from structure, not symmetry.

**P3 (Crossover):** At N=50K, |NFN R² - MLP-Matched R²| < 0.02 (equivalence test, TOST procedure).

**Falsification matrix:**

| P1 | P2 | P3 | Interpretation |
|----|----|----|----------------|
| ✓ | ✓ | ✓ | Hypothesis confirmed: equivariance helps at small scale, diminishes |
| ✓ | ✗ | ? | Equivariance benefit is structural, not symmetry-based |
| ✗ | ? | ? | Equivariance doesn't help even at small scale → surprising |
| ✓ | ✓ | ✗ | Equivariance always helps → revise hypothesis |

**Operational definitions:**

- **N:** Number of models in training set (validation fixed at 10% of remaining)
- **R²:** Coefficient of determination on held-out test set (20% of total, same across all N)
- **Random splits:** Stratified by accuracy decile

This gives us clear pass/fail criteria for each prediction.

**Key Points:**
- Three pre-registered predictions: P1 (small-scale advantage), P2 (symmetry vs structure), P3 (crossover)
- Falsification matrix guides interpretation
- Stratified splits, fixed test set

---

### Exchange 8

🔭 **Dr. Nova** (Creative Novelty Explorer):

The hypothesis is getting rigorous, but I want to push the novelty angle further.

🎯 Dr. Sage asked "why should the field care?" The current answer is "practical guidance on when to use equivariance." That's useful but not exciting.

Here's the deeper novelty: **We're testing whether symmetry exploitation is fundamentally different from data augmentation.**

In vision, data augmentation (random crops, flips) provides the same symmetry information that CNNs exploit via weight sharing. With enough augmented data, MLPs can learn translation equivariance. Our hypothesis suggests the same applies to weight space: permutation equivariance is "baked-in augmentation" that data can replace.

This connects to a bigger question in deep learning: **Are architectural inductive biases necessary, or just convenient?** Our experiment is a controlled test of this question in the weight space domain.

If we frame the paper as "Testing the Necessity of Architectural Inductive Biases in Weight Space Learning," that's a broader contribution than "NFN vs MLP at different scales."

The mechanism claim becomes: **Permutation equivariance functions as implicit data augmentation over the permutation group. Given sufficient data, an MLP learns equivalent representations by seeing enough permuted examples.**

**Key Points:**
- Deeper novelty: equivariance as implicit augmentation
- Connects to broader debate on necessity of inductive biases
- Paper framing: "Testing Necessity of Architectural Inductive Biases"

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔭 Dr. Nova's framing is compelling, but let me check if the mechanism claim is scientifically sound.

**Claim:** "MLP learns equivalent representations by seeing enough permuted examples."

**Problem:** We're NOT showing the MLP permuted examples. The Model Zoo weights are in their original (arbitrary) ordering. The MLP must learn to ignore permutation invariance from seeing DIFFERENT models, not permuted versions of the SAME model.

This is a subtle but important distinction. The MLP isn't learning permutation invariance from augmentation — it's learning to extract features that happen to be robust to the arbitrary orderings across different models.

**Revised mechanism:** NFN exploits the known permutation group structure. MLP must implicitly learn which features are permutation-invariant from seeing many models. With enough models, the MLP sees enough "natural variation" in orderings to learn robust features.

This is actually a STRONGER claim: the MLP learns permutation-relevant structure WITHOUT being told what permutations are. That's more impressive than just handling augmented data.

**Feasibility confirmation:** The mechanism is sound. The MLP's success at large scale would demonstrate that sufficient data diversity provides the same information as known symmetry structure.

**Key Points:**
- MLP doesn't see explicit permutations — learns from natural variation
- Revised mechanism: data diversity provides symmetry information
- This is actually a stronger, more interesting claim

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

⚙️ Prof. Pax raises a good point, but it creates a new problem.

**If the MLP learns permutation-robust features from "natural variation," how do we verify this?**

We claim the MLP at large scale learns similar representations to NFN. But we don't have a way to test representation similarity. The R² could be equal for completely different reasons.

**Required addition:** Representation analysis. After training, extract hidden representations from both NFN and MLP. Measure:

1. **CKA similarity:** Do NFN and MLP learn similar feature spaces?
2. **Probe invariance:** For a trained MLP, check if scrambling a test model's weights (applying a random permutation) changes the MLP's output. If MLP has learned permutation-invariant features, the output should be stable.

If MLP at N=50K has high probe invariance (low sensitivity to permutation), while MLP at N=1K has low probe invariance (high sensitivity), that directly supports the mechanism claim.

**Objection still standing:** What if MLP achieves similar R² through a completely different mechanism — e.g., memorizing statistics that happen to correlate with accuracy? CKA and probe invariance would both fail, but R² would match.

This would be a legitimate alternative explanation. We should state it as H0_mechanism: "MLP achieves similar R² through memorization of order-sensitive statistics, not learned invariance."

**Key Points:**
- Add representation analysis: CKA similarity, probe invariance test
- Probe invariance directly tests mechanism claim
- Alternative H0: MLP memorizes order-sensitive statistics

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔍 Prof. Rex's objection is valid. Let me integrate the representation analysis into the hypothesis.

**Updated Hypothesis Structure:**

**H-Main:** Permutation equivariance provides sample efficiency benefits that diminish with data scale.

**H-M1 (Existence):** At N=1K, NFN R² > MLP-Matched R² + 0.05

**H-M2 (Mechanism - Symmetry):** At N=1K, NFN R² > NFN-Scrambled R² + 0.05

**H-M3 (Crossover):** At N=50K, |NFN R² - MLP R²| < 0.02

**H-M4 (Mechanism - Learned Invariance):** At N=50K, MLP probe invariance > 0.8 (output correlation under random weight permutation). At N=1K, MLP probe invariance < 0.5.

**Experimental Design:**

| IV: Data Scale | DV: R² | DV: Probe Invariance | DV: CKA with NFN |
|---------------|--------|---------------------|------------------|
| N=1K | NFN >> MLP (P1) | MLP low | MLP low |
| N=5K | NFN > MLP | MLP medium | MLP medium |
| N=10K | NFN ≥ MLP | MLP medium-high | MLP medium-high |
| N=25K | NFN ≈ MLP | MLP high | MLP high |
| N=50K | NFN ≈ MLP (P3) | MLP high (H-M4) | MLP ≈ NFN |

This gives us a complete picture: not just whether performance converges, but whether REPRESENTATIONS converge.

**Key Points:**
- Four sub-hypotheses: existence, symmetry mechanism, crossover, learned invariance
- Probe invariance is measurable: correlation of outputs under random permutation
- Table predicts joint trajectory of R² and representation metrics

---

### Exchange 12

🎯 **Dr. Sage** (Research Impact Evaluator):

NOW we have something significant. Let me articulate the contribution.

**Paper-worthy claims:**

1. **Empirical finding:** First systematic study of equivariance vs non-equivariant baselines in weight space learning at scale (50K models). Prior work compared methods but not with explicit capacity matching and ablations.

2. **Mechanistic insight:** If H-M4 holds, we demonstrate that MLPs can LEARN permutation invariance from data diversity — a phenomenon not previously shown in weight space.

3. **Practical guidance:** The crossover point (if it exists) gives practitioners a concrete decision rule.

4. **Theoretical implication:** Connects weight space learning to the broader inductive bias debate. If architectural symmetry exploitation is replaceable by data, this suggests weight space structure is "learnable," not "required."

**Differentiation from prior work:**

- NFN paper [Zhou et al., 2023] focused on generation, not property prediction
- Hyper-Representations [Schurholt et al., 2022] used attention without equivariance claims
- Model Zoo paper provided data but no architectural comparison

**The contribution matrix:**

| Claim | Novel? | Testable? | Significant? |
|-------|--------|-----------|--------------|
| Equivariance sample efficiency | Yes (not tested at scale) | Yes (P1-P3) | Medium |
| MLP learns invariance from data | Yes (new claim) | Yes (H-M4) | High |
| Crossover threshold exists | Yes (not established) | Yes (P3) | High |

This is publishable.

**Key Points:**
- Three novel contributions: scale study, learned invariance, crossover
- Differentiates from NFN, Hyper-Rep, Model Zoo papers
- H-M4 (learned invariance) is the most novel claim

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me finalize the experimental protocol so there's no ambiguity.

**Dataset:**
- Source: Model Zoo CIFAR-10 CNN zoo (single architecture family)
- Total models: Use the largest available single-architecture subset (target: 20K-50K)
- Split: 70% train pool, 10% validation, 20% test (fixed across all conditions)
- Training subsets: N ∈ {1K, 2.5K, 5K, 10K, 25K, max} sampled from train pool

**Models (IV):**
1. **NFN:** NPLinear + HNPPool layers (from AllanYangZhou/nfn), regression head
2. **MLP-Matched:** Same hidden dims, standard linear layers, same regression head
3. **NFN-Scrambled:** NFN architecture, but input weights randomly permuted (fixed random seed per model)

**Metrics (DV):**
- **Primary:** R² on test set accuracy prediction
- **Secondary:** ECE (calibration), OOD R² (train on acc < 60%, test on acc > 70%)
- **Mechanism:** Probe invariance (mean correlation of outputs across 10 random permutations), CKA with NFN

**Statistical tests:**
- P1, P2: One-sided paired t-test, α = 0.05, N = 10 random seeds
- P3: TOST equivalence test, bounds = ±0.02
- H-M4: 95% CI for probe invariance, threshold 0.8

**Controls:**
- Same optimizer (AdamW), same schedule (cosine annealing)
- Same training epochs (50) across all conditions
- Fixed random seeds for reproducibility

**Key Points:**
- Single-architecture subset from Model Zoo
- Three models: NFN, MLP-Matched, NFN-Scrambled
- Pre-specified stats: paired t-tests, TOST, 10 seeds

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility check before we lock this down.

**Compute budget:**
- 3 models × 6 data scales × 10 seeds = 180 training runs
- Each run: ~1 hour on single GPU (50K models, 50 epochs)
- Total: ~180 GPU-hours ≈ 1 week on 8 GPUs

This is tractable. No exotic hardware needed.

**Implementation checklist:**
- [x] NFN available via pip
- [x] Model Zoo downloadable
- [x] Probe invariance: trivial to implement (forward pass with shuffled weights)
- [x] CKA: existing implementations available (e.g., from representational similarity papers)

**Potential issues:**
1. Model Zoo might not have 50K models in a SINGLE architecture family. Need to check actual subset sizes.
2. NFN may need adaptation for specific layer shapes — the pip package handles standard cases.

**Mitigation:** If single-family subset is smaller (e.g., 10K), adjust data scales accordingly. The hypothesis still holds with N ∈ {500, 1K, 2.5K, 5K, max}.

**Verdict:** Technically feasible. No fundamental barriers. Implementation effort: ~2-3 weeks including infrastructure.

**Key Points:**
- 180 runs, ~1 week compute
- All components available
- May need to adjust data scales based on actual subset size

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

One final stress test before I'm satisfied.

**Remaining concern: Architecture homogeneity assumption.**

We're assuming Model Zoo's single-architecture subsets are TRULY homogeneous — same layer structure, same activation functions, same residual connections. But are they?

Model Zoo includes models trained with DIFFERENT hyperparameters (learning rate, batch size, epochs). What if some of these affect architecture subtly (e.g., batch norm statistics differ, dropout masks affect weight distributions)?

**Test:** Before the main experiment, run a sanity check:
1. Take 100 models from the single-architecture subset
2. Verify they have IDENTICAL architecture specifications (layer shapes, activation types)
3. If not, filter to the largest truly-homogeneous subset

This protects against a confound where "architecture variation within family" masquerades as "equivariance benefit."

**Second concern: Null hypothesis strength.**

Our null H0 is "no equivariance benefit." But the more interesting null is "equivariance benefit exists but doesn't diminish." We should explicitly test:

- H0_constant: NFN advantage is constant across all N (no diminishing returns)
- Ha_diminishing: NFN advantage decreases with N (our hypothesis)

A regression of (NFN R² - MLP R²) on log(N) should have a significantly negative slope under Ha_diminishing.

**Now I'm convinced.** The hypothesis is testable, falsifiable, and addresses my concerns.

**Key Points:**
- Pre-check architecture homogeneity within Model Zoo subset
- Add regression test for diminishing returns (slope of advantage vs log N)
- Hypothesis ready for execution

---

### Exchange 16

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the final hypothesis structure based on all our discussion.

**FINAL HYPOTHESIS:**

**Title:** Sample Efficiency of Permutation Equivariance in Weight Space Learning

**Core Claim (Under-If-Then-Because):**
> Under [single-architecture CNN model zoo (50K+ models)], if [permutation-equivariant architecture (NFN) vs matched-capacity non-equivariant baselines], then [NFN shows significant R² advantage at small data scales (N<5K) that diminishes to non-significance at large scales (N>25K)], because [equivariance provides implicit symmetry exploitation that MLPs can learn from data diversity at scale].

**Mechanism:** Permutation equivariance bakes in knowledge of the symmetry group. MLPs must learn this from data. With enough data, the "natural variation" in weight orderings across models provides the same information, allowing MLPs to learn permutation-robust features.

**Predictions:**
1. **P1 (Existence):** At N=1K, NFN R² > MLP R² + 0.05 (p<0.05)
2. **P2 (Symmetry vs Structure):** At N=1K, NFN R² > NFN-Scrambled R² + 0.05
3. **P3 (Crossover):** At N=50K, |NFN R² - MLP R²| < 0.02 (TOST)
4. **P4 (Learned Invariance):** MLP probe invariance increases with N (correlation > 0.8 at N=50K)

**Falsification:** P1 fails → equivariance doesn't help. P2 fails → benefit is structural, not symmetry. P3 fails → equivariance always helps. P4 fails → MLP succeeds via different mechanism.

**Scope:** Applies to homogeneous architecture zoos. Does not apply to heterogeneous (mixed architecture) model collections.

**Key Points:**
- Four testable predictions with clear success/fail criteria
- Mechanism grounded in learned invariance
- Scope explicitly bounded

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The reframing from "does equivariance help" to "when does equivariance matter" elevates this from incremental to mechanistic. The connection to the broader inductive bias debate (architectural symmetry vs learned invariance) positions this as a contribution to deep learning theory, not just weight space methods.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Four pre-registered predictions with quantitative thresholds. Clear falsification matrix. Statistical tests specified (paired t-test, TOST). The hypothesis can fail in multiple informative ways, each pointing to a different interpretation.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Three novel contributions: first scale study, learned invariance demonstration, crossover threshold. H-M4 (MLP learns permutation invariance from data) is genuinely new. Practical guidance for practitioners on architecture choice. Connects to broader theoretical questions.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components available (NFN pip-installable, Model Zoo downloadable). 180 GPU-hours is tractable (~1 week on 8 GPUs). No exotic hardware or custom implementations required. Probe invariance test is trivial to implement.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The consensus hypothesis tests whether permutation equivariance in weight space learning is a necessary architectural inductive bias or a sample efficiency mechanism replaceable by data. Using the Model Zoo dataset (50K+ CNN models), we compare NFN (equivariant) against MLP-Matched (same capacity, no equivariance) and NFN-Scrambled (wrong permutation group) across data scales from 1K to 50K models.

We predict that NFN significantly outperforms baselines at small scales (N<5K) because it exploits known symmetry structure that MLPs must learn from data. At large scales (N>25K), the advantage diminishes as MLPs learn permutation-robust features from the natural variation in weight orderings across many models. The mechanism test (H-M4) verifies that MLPs actually learn permutation invariance, not just correlated statistics, by measuring output stability under random weight permutations.

This advances the field by: (1) establishing the first systematic scale study of equivariance in weight space, (2) demonstrating whether architectural symmetry exploitation is replaceable by data, and (3) providing practitioners with a concrete decision rule for architecture choice.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Model Zoo single-architecture subsets may be smaller than 50K — need to verify actual sizes and adjust scales if needed
- Architecture homogeneity within "single family" should be verified before main experiment
- **Mitigation Strategy:** Pre-experiment sanity check (100 models, verify identical layer specs), adjust data scales to available subset size

---

## Emerged Hypothesis Summary

### Core Statement
Under single-architecture CNN model zoos, if permutation-equivariant architecture (NFN) versus matched-capacity non-equivariant baselines, then NFN shows significant R² advantage for accuracy prediction at small data scales (N<5K) that diminishes to non-significance at large scales (N>25K), because equivariance provides implicit symmetry exploitation that MLPs can learn from data diversity at scale.

### Causal Mechanism
1. NFN's equivariant layers encode the permutation group structure, making predictions invariant to weight ordering
2. MLP has no built-in permutation awareness — must learn from data
3. At small N, MLP sees insufficient "natural variation" in orderings to learn robust features
4. At large N, the diversity of weight orderings across many models provides equivalent information
5. Result: MLP converges to similar performance and learns similar representations (measurable via probe invariance)

### Variables
- **IV:** Architecture type (NFN, MLP-Matched, NFN-Scrambled)
- **IV:** Data scale N (1K, 2.5K, 5K, 10K, 25K, max)
- **DV Primary:** R² on accuracy prediction
- **DV Secondary:** Calibration (ECE), OOD R², Probe invariance, CKA

### Key Assumptions
- A1: Model Zoo contains sufficient single-architecture models (>10K)
- A2: Architecture within "family" is truly homogeneous (same layer shapes)
- A3: Accuracy labels are reliable and span sufficient range
- A4: NFN implementation correctly handles model weights
- A5: Probe invariance test validly measures learned symmetry

### Null Hypothesis
There is no significant difference in R² between NFN and MLP-Matched at any data scale, OR NFN advantage is constant (no diminishing returns).

### Predictions
- P1: N=1K → NFN R² > MLP R² + 0.05 (p<0.05)
- P2: N=1K → NFN R² > NFN-Scrambled R² + 0.05 (p<0.05)
- P3: N=50K → |NFN R² - MLP R²| < 0.02 (TOST)
- P4: MLP probe invariance at N=50K > 0.8

### Novelty
- First systematic scale study of equivariance in weight space learning
- Novel claim: MLPs can learn permutation invariance from data diversity
- Connects weight space learning to broader inductive bias debate

### Scope & Boundaries
- Applies to: homogeneous architecture model zoos
- Does not apply to: heterogeneous (mixed architecture) collections
- Limitation: CIFAR-10 scale models only; generalization to larger models untested

### Experimental Setup
- Dataset: Model Zoo CIFAR-10 CNN subset (single architecture)
- Models: NFN, MLP-Matched, NFN-Scrambled
- Baselines: Random features, simple statistics (mean/std/norm of weights)

### Related Work & Baselines
- NFN [Zhou et al., 2023]: Introduced equivariant layers, focused on generation
- Hyper-Representations [Schurholt et al., 2022]: Attention-based, no equivariance comparison
- Model Zoo [2022]: Provided dataset, no architectural comparison
- Our contribution: First direct comparison at scale

### Phase 2B Readiness Seeds
- SH1 (Existence): NFN provides advantage at small scale
- SH2 (Mechanism): Advantage comes from symmetry, not just structure
- SH3 (Comparison): Deferred to Phase 5 (full baseline suite)

### Established Facts
- Model Zoo contains 50K+ models with accuracy labels (BUILD_ON)
- NFN architecture exists and is pip-installable (BUILD_ON)
- Permutation equivariance is well-defined for homogeneous architectures (BUILD_ON)
- MLPs can approximate any function given enough data (BUILD_ON)


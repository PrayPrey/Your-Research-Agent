# Phase 2A: Research Discussion Log

**Date:** 2026-08-24
**Workflow:** phase2a-dialogue
**Architecture:** Self-Contained Tikitaka Loop (Self-Play)
**Execution Mode:** UNATTENDED (SELF-PLAY)

---

## Discussion Briefing

### Selected Research Gap

**Gap ID:** GAP-1
**Title:** No Systematic Benchmark Comparison of Equivariant vs Non-Equivariant Weight Embeddings
**Priority:** HIGH+PRIMARY
**Relevance:** Directly addresses research question

### Gap Description

Existing work (Unterthiner et al. 2020) predicts accuracy from weights using simple statistics (mean, std, spectral norm) achieving R² > 0.98. Neural Functional Transformers (Zhou et al. 2023) process weights equivariantly but focus on different tasks (INR editing, model initialization). No direct comparison exists using identical benchmarks.

**Missing Piece:** Systematic head-to-head evaluation of:
- MLP baseline (flattened weights → embedding)
- Equivariant NFN/NFT approach (weight-space layers)
- Performance prediction task on standard Model Zoo benchmarks

### Research Question

How effectively can permutation-equivariant neural networks learn weight embeddings that predict downstream task performance, compared to permutation-agnostic baselines, using existing model zoo datasets?

### Reference Papers

1. **Predicting Neural Network Accuracy from Weights** (Unterthiner et al. 2020) - Baseline R² > 0.98 with simple statistics
2. **Neural Functional Transformers** (Zhou et al. 2023) - Equivariant NFT for weight processing
3. **Model Zoos Dataset** (Schürholt et al. 2022) - 50K+ models benchmark
4. **SANE** (Schürholt et al. 2024) - Scalable weight space learning
5. **Git Re-Basin** (Ainsworth et al. 2022) - Permutation symmetry framework

### Available Implementations

- **nfn** (PyTorch): Neural Functional Networks library - 93 stars
- **UNF** (JAX): Universal Neural Functionals - 56 stars
- **ModelZooDataset**: 50K+ trained models - 60 stars
- **SANE**: Scalable weight embeddings

### MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced)

- Reject ideas requiring **new benchmarks, rubrics, or scoring frameworks**
- Reject ideas requiring **synthetic/generated data or future follow-up data**
- Reject ideas requiring **human evaluation, annotation, or subjective scoring**
- Accept only hypotheses testable **immediately using existing real datasets and existing benchmarks**

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this comparison from an entirely different angle? Everyone's been measuring whether equivariant architectures give *better* R² scores on accuracy prediction—but I think that's the wrong question. What if the real value of equivariance isn't marginal accuracy gains, but **data efficiency**?

Here's what I mean: Unterthiner et al. achieved R² > 0.98 with 120K models. That's a lot of data! But equivariant architectures, by construction, don't need to *learn* permutation invariance from data—they have it baked in. So the testable hypothesis becomes: **do equivariant weight embeddings achieve comparable R² with significantly fewer training models?**

This reframes the comparison from "who wins at scale" to "who learns faster"—which is arguably more scientifically interesting and has clearer practical implications. The Model Zoo dataset (50K+ models) gives us natural ablation points: train on 1K, 5K, 10K, 25K, 50K models and plot learning curves.

I'm also excited about a cross-domain angle. The SANE paper shows sequential decomposition works, but what if equivariance matters more for *transfer*? Train on CNNs, test on ViTs. The permutation structure of weight matrices is architecture-specific, so equivariant methods that explicitly model this might generalize better—or worse! Either result would be novel.

**Key Points:**
- Reframe comparison as data efficiency, not just final performance
- Test learning curves: R² vs. training zoo size (1K→50K models)
- Cross-architecture transfer as secondary hypothesis

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the data efficiency framing—it creates clear testable predictions. But let me be precise about what would actually constitute a fair test.

The evidence suggests we need careful experimental controls. First, the baseline matters enormously. Unterthiner's R² > 0.98 uses *handcrafted* statistics (mean, std, spectral norm per layer). That's not an MLP baseline—that's feature engineering plus regression. A proper comparison needs:

1. **MLP baseline**: Flatten weights → MLP → accuracy prediction (no handcrafted features)
2. **Statistics baseline**: Unterthiner's handcrafted features → linear regression
3. **Equivariant**: NFN/SANE/UNF architecture → accuracy prediction

What would disprove the data efficiency hypothesis? If the MLP baseline achieves similar R² to equivariant methods at all training sizes, then permutation equivariance provides no inductive bias benefit. The prediction must be: **equivariant methods reach R² = X with N models, while MLP requires >2N models for the same R²**.

For the cross-architecture transfer, the falsification criterion is straightforward: if equivariant methods trained on CNNs perform *worse* on ViT accuracy prediction than in-distribution, while MLP shows the same degradation pattern, then equivariance doesn't help transfer.

One confound we must control: model zoo diversity. If CNN zoos and ViT zoos have different accuracy distributions, we're measuring distribution shift, not equivariance benefits.

**Key Points:**
- Three-way comparison: MLP, Statistics, Equivariant
- Falsification: equivariant must show >2x data efficiency gain
- Control confound: accuracy distribution shift between architectures

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? Let me evaluate the significance of both proposed hypotheses.

The data efficiency framing is genuinely new. Prior work (Unterthiner, NFN, SANE) each demonstrated *that* their method works, but nobody has asked *how much data* each approach needs. This matters because model zoos are expensive to create. If equivariant methods need 10x fewer models to achieve the same prediction quality, that opens weight space learning to researchers without massive compute budgets.

However, I'm concerned about the magnitude of expected effect. Unterthiner achieves R² > 0.98—there's not much room to improve. The real contribution would be showing **equivariance enables learning from small zoos where statistics-based methods fail**. At 50K models, everything works. At 500 models? That's where we'd see genuine separation.

The cross-architecture transfer question is more risky but potentially higher impact. If equivariant embeddings transfer where MLP embeddings don't, this challenges the implicit assumption that weight space structure is architecture-specific. That would be a paradigm shift.

What new research directions does this open? Success would validate that:
1. Weight space has universal structure beyond architecture-specific symmetries
2. Small model zoos are sufficient for property prediction
3. The expensive part of weight space learning is dataset curation, not model capacity

This matters because it determines whether weight embedding is a rich-lab privilege or democratizable.

**Key Points:**
- Data efficiency is novel angle—nobody has compared learning curves
- True test: performance at *small* zoo sizes (500-1K models)
- Cross-architecture transfer could challenge architecture-specific assumptions

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. I've reviewed the technical requirements and I have concerns about mechanism validity—not budgets, but whether the proposed comparisons are scientifically sound.

First, the good news: all components exist. Model Zoo dataset: available (50K+ CNNs on CIFAR-10/100, SVHN, etc.). NFN library: pip installable. UNF: JAX implementation ready. The experiments are implementable in principle.

Now, here's what worries me technically:

**The MLP baseline is ill-defined.** How do you flatten weights from variable-sized architectures? CNNs have different layer counts, channel dimensions, kernel sizes. You can't just concatenate weights into a fixed-length vector. SANE solves this with sequential tokenization, but then "MLP baseline" becomes "Transformer baseline" which defeats the comparison purpose.

One valid approach: restrict to *homogeneous* model zoos (same architecture, different training runs). Model Zoo dataset has this—same CNN architecture trained 5K+ times. This makes the MLP baseline well-defined but limits generality.

**The cross-architecture transfer is theoretically coherent** because NFN and UNF explicitly model per-layer permutation structure. A ViT's MLP weights have the same local symmetry as a CNN's conv weights (both are weight matrices with hidden-unit permutation symmetry). The question is whether the *composition* of layers matters.

What's fundamental here: we're testing whether equivariance captures *local* weight structure that transfers, vs *global* network structure that doesn't. Both outcomes are scientifically valid.

**Key Points:**
- MLP baseline requires homogeneous architecture zoo to be well-defined
- Cross-architecture transfer is theoretically grounded (local permutation symmetry)
- Two valid experimental scopes: homogeneous (clean) vs heterogeneous (ambitious)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and we can address Prof. Pax's concerns while strengthening the hypothesis. Let me synthesize what's emerging.

The core insight from this discussion: **equivariance provides inductive bias that should manifest as data efficiency, not necessarily final performance.** Prof. Vera's three-way comparison and Dr. Sage's focus on small zoo sizes converge on a testable formulation.

For Prof. Pax's MLP baseline concern, here's a refinement: we test on **homogeneous zoo first** (same architecture, e.g., ResNet-20 on CIFAR-10 with 5K+ training runs). This gives us a clean apples-to-apples comparison where the MLP baseline is well-defined. *Then* we test cross-architecture as a secondary hypothesis with NFN/UNF only (since MLP can't handle variable architectures).

What if we addressed the convergence criteria explicitly?

1. **SPECIFIC core claim**: Permutation-equivariant weight embeddings achieve equivalent accuracy prediction (R² within 0.02 of baseline) with ≤50% of training models compared to MLP baselines on homogeneous model zoos.

2. **MECHANISM**: Equivariance eliminates the need to learn permutation invariance from data, reducing sample complexity. The network exploits weight symmetry structure rather than memorizing arbitrary orderings.

3. **PREDICTIONS**: 
   - P1: On 500-model training set, equivariant R² > MLP R² by ≥0.1
   - P2: On 5000-model training set, equivariant R² ≈ MLP R² (gap <0.02)
   - P3: Learning curve slope steeper for equivariant at small N

4. **NOVELTY**: First systematic data efficiency comparison; existing work only compares final performance

**Key Points:**
- Two-stage design: homogeneous zoo (clean) → cross-architecture (ambitious)
- Quantified predictions with falsification thresholds
- Core claim: 2x data efficiency, not 2x final performance

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me stress-test the emerging hypothesis.

**Assumption 1: R² > 0.98 leaves room for meaningful comparison.** This worries me. If statistics baseline achieves 0.98 and equivariant achieves 0.99, that's noise, not signal. The variance in R² estimates across random seeds will swamp any real effect. What would convince me: report confidence intervals, not point estimates. Use 10+ random seeds.

**Assumption 2: "Data efficiency" is the right metric.** Maybe equivariance matters for a different reason—robustness to weight perturbations, or embedding quality for downstream tasks beyond accuracy prediction. We're assuming sample complexity is the key axis.

**Assumption 3: Homogeneous zoo is representative.** Models trained with identical architecture but different random seeds might have *more* regular weight structure than realistic model collections. The equivariance benefit might only appear in homogeneous settings and disappear with real heterogeneity.

**Where this actually convinces me:** If the experiment shows equivariant methods achieve R² = 0.95 on 500 models while MLP achieves R² = 0.7, that's unambiguous. A 0.25 gap is not noise. Dr. Ally's P1 threshold of 0.1 gap is reasonable but should be treated as minimum detectable effect.

My remaining concern: what if handcrafted statistics (Unterthiner) beat both learned methods at small N? That would mean the game isn't MLP vs equivariant—it's learned vs engineered features. We need the statistics baseline at all training sizes.

**Key Points:**
- Report R² with confidence intervals across 10+ seeds
- Include statistics baseline at all training sizes (not just as upper bound)
- Minimum detectable effect: R² gap ≥ 0.1 at N=500

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Wait—Prof. Rex just identified something crucial! What if handcrafted statistics beat learned methods at small N? That's not a failure mode—that's a *third hypothesis*!

Imagine this: at N=500, **Engineered > Equivariant > MLP**. At N=5000, **Equivariant ≈ Engineered > MLP**. At N=50000, **Equivariant ≈ MLP ≈ Engineered**. This would tell us that equivariance is *intermediate*—it provides useful inductive bias but doesn't match domain knowledge at low data.

NOW we're onto something! The real scientific question becomes: **at what training set size does learned equivariant embedding match handcrafted statistics?** Call this the "crossing point." A low crossing point (e.g., N=1000) means equivariance is nearly as good as hand-engineering. A high crossing point (N=10000) means handcrafted features remain king for practical zoo sizes.

This reframes our contribution: we're not just comparing methods, we're characterizing the **data-efficiency landscape** of weight space learning. Three regimes: statistics-dominated, equivariance-dominated, learned-all-equivalent.

The experimental setup stays the same—we just extract more insight from the learning curves. And crucially, this answer exists regardless of outcome: whether equivariance wins, loses, or ties, we learn something about weight space structure.

**Key Points:**
- Three-way race: Statistics vs Equivariant vs MLP across all N
- New metric: "crossing point" where learned matches engineered
- Outcome-agnostic contribution: characterize data-efficiency landscape

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's crossing-point framing makes the predictions cleaner. Let me formalize the complete experimental protocol.

**Experimental Design (Final):**

*Dataset:* Model Zoo ResNet-20 subset (CIFAR-10), ~5000 models with accuracy labels.

*Training splits:* N ∈ {100, 250, 500, 1000, 2500, 5000} models, test on held-out 500.

*Methods:*
1. **Statistics**: Unterthiner features (per-layer mean, std, spectral norm) → Ridge regression
2. **MLP**: Flatten weights → 3-layer MLP → accuracy prediction
3. **NFN**: Neural Functional Network with permutation-equivariant layers

*Metrics:* R² on held-out set, 10 random seeds per (N, method) pair. Report mean ± std.

**Testable Predictions (Quantified):**

- **P1 (Main)**: At N=500, NFN R² > MLP R² + 0.1 (one-sided t-test, p<0.05)
- **P2 (Ceiling)**: At N=5000, all methods within R² ± 0.03 of each other
- **P3 (Crossing)**: NFN matches Statistics R² at some N* < 2500

**Falsification Criteria:**
- If P1 fails: equivariance provides no data efficiency benefit over MLP
- If P3 fails (N* > 2500 or never crosses): handcrafted features dominate; learned methods need large data
- If MLP matches NFN at all N: permutation symmetry is not the key inductive bias

This meets my standards. Every outcome teaches us something about weight space structure.

**Key Points:**
- Fixed architecture (ResNet-20), 6 training sizes, 3 methods
- 10 seeds per condition, report R² mean ± std
- Three falsifiable predictions with statistical tests

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, this could work. Let me verify technical feasibility of Prof. Vera's protocol.

**Model Zoo availability:** ✓ The Model Zoo dataset includes 5360 ResNet-20 models trained on CIFAR-10. Sufficient for the proposed splits.

**Statistics baseline implementation:** ✓ Unterthiner's code extracts per-layer statistics. We use their exact feature set for fair comparison.

**MLP baseline for fixed architecture:** ✓ ResNet-20 has fixed weight tensor shapes. We can concatenate into ~270K-dimensional vector. Large, but standard MLPs handle this with appropriate regularization (dropout, weight decay).

**NFN implementation:** ✓ The nfn library supports ResNet architectures. Zhou et al.'s paper includes CIFAR experiments.

**Compute validation:** The experiment requires 6 training sizes × 3 methods × 10 seeds = 180 training runs. Each NFN training run takes ~10 minutes on modest GPU. Total: ~30 GPU-hours. Feasible.

**One technical refinement:** The 270K-dimensional input for MLP is unwieldy. Consider: (a) PCA to 1000 dimensions first, or (b) use per-layer embeddings averaged. Either maintains the "non-equivariant learned" spirit while being tractable. I recommend (b) to match NFN's layer-wise processing.

**Key Points:**
- All components verified available (Model Zoo, nfn library)
- Fixed ResNet-20 architecture makes MLP baseline tractable
- Per-layer embedding averaging recommended for MLP (matches NFN structure)

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the final hypothesis. Everyone's concerns have been addressed.

**Emerged Consensus:**

We're testing whether permutation-equivariant inductive bias provides data efficiency benefits for weight embedding, compared to non-equivariant learned approaches and handcrafted statistics.

**Core Hypothesis Statement:**

*Under fixed-architecture homogeneous model zoos (ResNet-20/CIFAR-10), if we train weight embedding models with varying dataset sizes (N=100 to 5000), then permutation-equivariant architectures (NFN) will achieve equivalent accuracy prediction R² with ≤50% of training samples compared to MLP baselines, because equivariance eliminates the need to learn permutation invariance from data.*

**Variables:**
- **IV**: Training set size (N ∈ {100, 250, 500, 1000, 2500, 5000}), Embedding method (Statistics, MLP, NFN)
- **DV**: R² on held-out accuracy prediction, crossing point N* where NFN matches Statistics

**Null Hypothesis H0:**
There is no significant difference in R² between NFN and MLP at any training set size (p>0.05 at all N).

**Predictions:**
1. **P1**: NFN R² > MLP R² + 0.1 at N=500 (p<0.05)
2. **P2**: All methods within ±0.03 at N=5000
3. **P3**: Crossing point N* < 2500 where NFN matches Statistics

**Phase 2B Readiness Seeds:**
- Existence claim: Fixed-architecture model zoos exhibit learnable weight-accuracy relationships
- Mechanism claim: Equivariance provides inductive bias for weight structure
- Comparison claim: Deferred to Phase 5 (baseline adaptation)

**Key Points:**
- Complete hypothesis with IV, DV, H0, predictions
- Three falsifiable predictions with quantified thresholds
- Ready for Phase 2B verification protocol design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The data efficiency framing is genuinely novel—no prior work systematically compares learning curves across equivariant vs non-equivariant approaches. The "crossing point" concept adds a second contribution: characterizing the data-efficiency landscape of weight space learning. Both contributions are absent from existing literature.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously testable with three quantified predictions (P1: R² gap ≥0.1 at N=500; P2: convergence at N=5000; P3: crossing point N*<2500). Each prediction has clear falsification criteria and statistical tests (one-sided t-test, p<0.05). The 10-seed protocol ensures confidence intervals. Every possible outcome is scientifically informative.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** The contribution is meaningful but bounded. If equivariance shows 2x data efficiency, this opens weight space learning to smaller labs. However, the scope is limited to homogeneous model zoos and accuracy prediction. Cross-architecture transfer (the higher-impact question) is deferred. The work advances methodology more than paradigm.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All technical components are verified: Model Zoo dataset (5360 ResNet-20 models), nfn library (pip installable), statistics baseline (Unterthiner's code). The MLP baseline is well-defined for fixed architecture. Compute requirements (~30 GPU-hours) are modest. No fundamental barriers—the experiment can be executed immediately.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a data efficiency comparison hypothesis. The core claim is that permutation-equivariant weight embeddings (NFN) achieve equivalent accuracy prediction performance with significantly fewer training models compared to non-equivariant MLP baselines, because equivariance provides inductive bias that eliminates the need to learn permutation invariance from data.

The experimental design uses the Model Zoo ResNet-20 subset (5360 models on CIFAR-10) with training sizes ranging from 100 to 5000 models. Three methods are compared: handcrafted statistics (Unterthiner), MLP baseline (flattened weights), and NFN (permutation-equivariant). The primary outcome is R² on held-out accuracy prediction across 10 random seeds.

The hypothesis is supported by theoretical justification (equivariance reduces hypothesis space) and has three testable predictions: (1) NFN outperforms MLP by R²≥0.1 at small training sizes (N=500), (2) all methods converge at large sizes (N=5000), and (3) NFN matches handcrafted statistics at intermediate sizes (N*<2500). The "crossing point" analysis adds a novel contribution regardless of whether equivariance wins or loses.

The scope is intentionally narrow—homogeneous model zoos, fixed architecture—to enable clean comparison. Cross-architecture transfer is noted as future work. The hypothesis meets all feasibility constraints: existing dataset, existing benchmarks, no human evaluation required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The R² ceiling (>0.98 in prior work) limits room for measurable improvement at large N; the comparison is meaningful primarily at small N
- Homogeneous model zoo may not represent realistic deployment scenarios where architectures vary
- **Mitigation Strategy:** Focus analysis on N≤1000 where separation should be clearest; report full learning curves to show convergence behavior; acknowledge homogeneous scope as limitation

---

## Emerged Hypothesis Summary

### Core Statement
Under fixed-architecture homogeneous model zoos (ResNet-20/CIFAR-10), if we train weight embedding models with varying dataset sizes (N=100 to 5000), then permutation-equivariant architectures (NFN) will achieve equivalent accuracy prediction R² with ≤50% of training samples compared to MLP baselines, because equivariance eliminates the need to learn permutation invariance from data.

### Causal Mechanism
1. **Step 1:** Weight matrices in neural networks have hidden-unit permutation symmetry (reordering neurons preserves function)
2. **Step 2:** Non-equivariant methods (MLP) must learn this invariance from data, consuming sample complexity
3. **Step 3:** Equivariant methods (NFN) enforce invariance architecturally, freeing capacity for learning weight-accuracy relationships

### Variables
- **Independent:** Training set size (N), Embedding method (Statistics/MLP/NFN)
- **Dependent (Primary):** R² on held-out accuracy prediction
- **Dependent (Secondary):** Crossing point N* where NFN matches Statistics
- **Controlled:** Architecture (ResNet-20), Dataset (CIFAR-10), Test set size (500), Random seeds (10)

### Key Assumptions
- A1: ResNet-20 model zoo has sufficient diversity in accuracy for meaningful regression
- A2: Unterthiner's statistics represent optimal handcrafted features
- A3: NFN implementation is correct and optimized (using official library)
- A4: 10 random seeds provide sufficient confidence intervals
- A5: The 500-model threshold for P1 is appropriate for detecting equivariance benefits

### Null Hypothesis
H0: There is no significant difference in R² between NFN and MLP at any training set size N ∈ {100, 250, 500, 1000, 2500, 5000} (p>0.05 for all comparisons).

### Predictions
- **P1 (Primary):** At N=500, NFN R² > MLP R² + 0.1 (one-sided t-test, p<0.05)
- **P2:** At N=5000, all three methods achieve R² within ±0.03 of each other
- **P3:** There exists N* < 2500 where NFN R² first equals Statistics R²

### Novelty
- First systematic data efficiency comparison for weight embeddings
- "Crossing point" analysis as new evaluation paradigm
- Characterization of data-efficiency landscape (statistics-dominated → equivariance-dominated → convergence)

### Scope & Boundaries
- **Applies to:** Fixed-architecture homogeneous model zoos, accuracy prediction task
- **Does not apply to:** Cross-architecture transfer (deferred), heterogeneous model collections, other property prediction tasks
- **Known limitations:** Homogeneous zoo may be easier than realistic scenarios; R² ceiling limits sensitivity

### Experimental Setup
- **Dataset:** Model Zoo ResNet-20/CIFAR-10 subset (5360 models)
- **Model:** NFN (nfn library), MLP (3-layer), Ridge regression (statistics)
- **Baselines:** Unterthiner statistics → Ridge; Flattened weights → MLP

### Related Work & Baselines
- Unterthiner et al. 2020: R² > 0.98 with statistics (upper bound baseline)
- Zhou et al. 2023: NFN for weight processing (equivariant approach)
- Schürholt et al. 2024: SANE for scalable embeddings (related approach)

### Phase 2B Readiness Seeds
- **SH1 (Existence):** Fixed-architecture model zoos have learnable weight-accuracy relationships (baseline achieves R² > 0.9)
- **SH2 (Mechanism):** Equivariance provides measurable inductive bias (NFN > MLP at small N)
- **SH3 (Comparison):** Deferred to Phase 5 baseline adaptation

### Established Facts
- Weight-to-accuracy prediction achieves R² > 0.98 with sufficient data (Unterthiner 2020) - BUILD_ON
- Permutation symmetry exists in weight space (Git Re-Basin) - BUILD_ON
- NFN provides permutation-equivariant layers (Zhou 2023) - BUILD_ON
- Model Zoo dataset has 5000+ ResNet-20 models - BUILD_ON
- Data efficiency of equivariant vs non-equivariant is uncompared - PROVE_NEW

---


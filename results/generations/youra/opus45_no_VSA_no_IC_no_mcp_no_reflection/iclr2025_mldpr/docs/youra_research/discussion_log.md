# Phase 2A Discussion Log

**Date:** 2026-08-29
**Gap ID:** Gap-1
**Gap Title:** No Systematic Cross-Benchmark Ranking Stability Analysis
**Architecture:** Self-Play (Claude ALL personas, no external LLM)
**Mode:** UNATTENDED

---

## Briefing Context

### Selected Research Gap

**Gap 1: No Systematic Cross-Benchmark Ranking Stability Analysis**

- **Relevance:** PRIMARY - Directly addresses Q3 (ranking stability)
- **Current State:** Recht et al. measured accuracy drops on ImageNet-V2, but analysis focused on absolute accuracy, not relative ranking stability across models.
- **Missing Piece:** Systematic analysis of whether models that rank highly on popular benchmarks maintain their relative rankings on alternative datasets. Kendall-τ correlation between primary/alternative benchmark rankings not computed at scale.
- **Potential Impact:** HIGH - Directly answers whether benchmark overfitting affects model selection decisions.

### Key Reference Papers

1. **Recht et al. (2019)** - "Do ImageNet Classifiers Generalize to ImageNet?" - 11-14% accuracy drops on ImageNet-V2
2. **Dehghani et al. (2021)** - "The Benchmark Lottery" - Rankings depend on task selection
3. **"Reduced, Reused and Recycled" (2021)** - Top 10% datasets = 90% usage concentration

### Feasibility Constraints (Pipeline-Enforced)

- ❌ NO new benchmarks, rubrics, or scoring frameworks
- ❌ NO synthetic/generated data or future follow-up data
- ❌ NO human evaluation, annotation, or subjective scoring
- ✅ ONLY hypotheses testable with existing real datasets and existing benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting gap to explore! The community has been so focused on *absolute* accuracy drops that we've completely overlooked a much more practically relevant question: do the models we *choose* based on benchmark rankings actually maintain their relative superiority on deployment data?

Let me propose three unconventional angles:

**1. The "Selection Distortion" Hypothesis:** What if benchmark overfitting doesn't just inflate accuracy uniformly, but actually *inverts* rankings for certain model architectures? Imagine Model A beats Model B on ImageNet by 2%, but on ImageNet-V2, Model B beats Model A. This would mean our model selection process is actively choosing *worse* models for real-world deployment!

**2. The "Temporal Ranking Drift" Angle:** Newer models have had more opportunity to overfit to popular benchmarks (more papers analyzing ImageNet means more implicit leakage). We could measure whether ranking stability degrades as a function of model publication date — older models might show *more stable* rankings across benchmarks than newer ones.

**3. Cross-Domain Transfer of Ranking Stability:** Does ranking stability on vision benchmarks (ImageNet → ImageNet-V2) predict ranking stability on NLP benchmarks (GLUE → HANS)? This could reveal whether benchmark overfitting is a universal phenomenon or domain-specific.

The Recht et al. methodology is perfect here — we already have ImageNet-V2 with matched semantics but independent collection. Papers With Code gives us historical ranking data. This is *immediately testable*!

**Key Points:**
- Ranking inversions would be more impactful than uniform accuracy drops
- Temporal correlation could reveal progressive overfitting
- Cross-domain analysis could generalize findings beyond vision

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises intriguing possibilities, but let me stress-test the testability of these claims.

The "Selection Distortion" hypothesis needs precise operationalization. What exactly would disprove it? If we define a **ranking inversion** as Model A > Model B on benchmark X, but Model B > Model A on benchmark X', then the null hypothesis is: "The probability of ranking inversion between any pair of models is no different from chance (50%)."

But here's the critical issue: we need to define "significantly different" rankings. With 100 models on Papers With Code, we have C(100,2) = 4,950 pairwise comparisons. Even random noise would produce some inversions. We need **Kendall-τ correlation** between rankings on X and X' — this is a proper aggregate measure that accounts for all pairwise relationships.

For the temporal hypothesis, the falsifier is clear: if there's NO correlation between model publication year and ranking stability (measured as pairwise agreement between benchmark X and X' rankings), the hypothesis fails. But we need to control for model architecture family — maybe newer architectures are genuinely better, not just more overfit.

**Testable Prediction:** For ImageNet models published between 2015-2025, the Kendall-τ correlation between ImageNet and ImageNet-V2 rankings will be significantly below 1.0 (perfect agreement), and this correlation will decrease for models published more recently.

**Confounds to control:**
- Model architecture family (ResNet vs ViT vs ConvNeXt)
- Training data size
- Model capacity (parameters)

**Key Points:**
- Kendall-τ is the right metric for ranking stability, not pairwise inversions
- Statistical significance requires accounting for multiple comparisons
- Year-stability correlation needs architecture controls

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field?

If we find that Kendall-τ between ImageNet and ImageNet-V2 rankings is, say, 0.7 instead of 1.0, what's the actionable implication? The *significance* depends entirely on whether this 0.3 gap in ranking agreement translates to meaningful model selection errors.

Consider: if the Top 3 models on ImageNet are also the Top 3 on ImageNet-V2 (just reordered among themselves), practitioners don't care — they'd choose any of them anyway. But if Model #1 on ImageNet becomes Model #25 on ImageNet-V2, that's a critical finding that changes how the community should evaluate models.

**What makes this genuinely new vs. incremental:**
- Recht et al. showed accuracy drops but never computed ranking correlations
- Dehghani et al. discussed benchmark selection bias but focused on NLU tasks, not systematic ranking analysis across a benchmark pair
- No paper has computed Kendall-τ across a large model set with temporal analysis

**This opens new research directions:**
1. "Ranking-aware" benchmark design — optimizing not just for accuracy but for ranking stability
2. Model selection protocols that require validation on alternative benchmarks
3. A new metric: "Ranking Robustness Score" for benchmarks themselves

However, I caution against over-claiming. If Kendall-τ turns out to be 0.95, the finding becomes "benchmarks are actually quite reliable" — still publishable but less impactful. The hypothesis must be stated symmetrically.

**Key Points:**
- Impact depends on magnitude of ranking instability, not just existence
- Top-K ranking stability is more practically relevant than overall τ
- This addresses a gap no prior work has systematically filled

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in what's actually achievable. Dr. Nova's angles and Prof. Vera's operationalization are sound in principle, but let me check the technical and theoretical feasibility.

**Data availability:** Papers With Code provides ImageNet leaderboard data. ImageNet-V2 results are published in Recht et al.'s supplementary materials for ~50 models. Is this enough? 

For Kendall-τ to be meaningful with temporal analysis, we need sufficient models per year-bin. With ~50 models spanning 2015-2019 (Recht's data), we might have only 10 models per year — potentially too sparse for regression. BUT we can augment: later papers (2020-2024) evaluated their models on ImageNet-V2 as a standard generalization test. I estimate 100+ models now have published ImageNet-V2 results.

**Measurement validity:** Kendall-τ is mathematically well-defined and computationally trivial. No new frameworks needed. The only concern: are the ImageNet-V2 results from different papers comparable (same evaluation protocol)? Recht et al. released evaluation code — if subsequent papers used it, we're fine.

**The mechanism is sound:** We're not proposing any new evaluation framework — we're computing a standard statistic (Kendall-τ) on existing data (ImageNet, ImageNet-V2 results). This is purely *analysis* of existing benchmarks, not creation of new ones.

**Fundamental barrier check:**
- Can we get the data? YES (Papers With Code + Recht et al. supplements + subsequent papers)
- Can we compute the metric? YES (scipy.stats.kendalltau)
- Are measurements valid? YES (if evaluation protocols match)

**Key Points:**
- ~100+ models likely have published ImageNet-V2 results by 2024
- Kendall-τ is standard and implementable
- No new benchmarks needed — pure analysis of existing data

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent points from everyone. Let me synthesize and strengthen the emerging hypothesis.

**Core claim refinement:** Prof. Vera's Kendall-τ operationalization is solid, but Dr. Sage rightly notes we need both *existence* and *magnitude* measures. I propose a **dual-metric approach:**

1. **Overall Kendall-τ:** Captures aggregate ranking stability across all models
2. **Top-K Agreement:** What percentage of Top-10 models on ImageNet appear in Top-10 on ImageNet-V2?

This addresses Dr. Sage's practical concern — practitioners care most about top performers.

**Strengthening the temporal hypothesis:** Prof. Pax confirms data availability. The refinement: instead of arbitrary year bins, use **model publication date as continuous variable** in a regression: τ_stability ~ publication_year + architecture_family + log(params).

**Evidence supporting the hypothesis:**
- Recht et al. found uniform 11-14% drops — but never checked if models dropped uniformly or differentially
- Dehghani et al. showed benchmark lottery effects in NLU — suggesting ranking instability exists somewhere
- "Reduced/Reused/Recycled" documents concentration — more exposure to popular benchmarks creates conditions for overfitting

**Addressing Prof. Vera's confounds:** We control for architecture by including it as a categorical covariate. We control for training data by noting ImageNet training data is standardized (ImageNet-1K). Model capacity (parameters) is a separate covariate.

**Strengthened prediction:** Models published after 2020 will show lower ImageNet-to-ImageNet-V2 ranking stability (measured by both Kendall-τ and Top-10 overlap) than models published before 2018, even after controlling for architecture family.

**Key Points:**
- Dual-metric approach addresses practical and statistical concerns
- Continuous year variable is more powerful than binning
- Evidence from Recht, Dehghani, and concentration studies supports mechanism

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me challenge the assumptions.

**Challenge 1: Selection bias in published ImageNet-V2 results.** Not all ImageNet models were evaluated on ImageNet-V2. Which ones were? Primarily those from papers that cited Recht et al. — likely papers *already concerned* with generalization. This is non-random sampling. Models that would show *worse* ranking instability might never have been evaluated on V2.

**Counter:** If the selection bias favors generalization-aware models, and we *still* find ranking instability, the effect is likely *understated* in the general population. This actually strengthens the finding.

**Challenge 2: ImageNet-V2 was designed to be difficult.** Recht et al. deliberately made V2 harder to match original accuracy. What if V2 systematically penalizes certain architectures (e.g., models with specific augmentation strategies)? This would cause ranking changes unrelated to benchmark overfitting.

**Counter:** This is a legitimate confound. Mitigation: report results separately by architecture family. If ranking instability is consistent across ResNets, ViTs, ConvNeXts, it's not architecture-specific V2 bias.

**Challenge 3: Temporal correlation could be spurious.** Newer models are also larger, trained on more data (ImageNet-21K pretraining), and use different architectures. Year is confounded with everything.

**Counter:** This is why we need multivariate regression. If year remains significant after controlling for params, architecture, and pretraining data, temporal overfitting is supported.

**What would convince me:**
1. Kendall-τ < 0.85 with p < 0.001 (95% CI not including 0.9)
2. Temporal regression coefficient negative and significant after controls
3. Results consistent across ≥2 architecture families

**Key Points:**
- Selection bias in V2 evaluation could understate true instability
- Architecture-specific V2 difficulty is a real confound — mitigate by stratifying
- Year needs proper multivariate controls to isolate temporal effect

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp, but they've actually clarified the path forward. Let me add one more creative angle that emerged from this discussion:

**The "Benchmark Fingerprint" Insight:** What if different model architectures have different "fingerprints" of benchmark sensitivity? ResNets might be stable across ImageNet → V2, while ViTs show instability. This would be a genuinely novel finding — it suggests benchmark choice affects not just rankings, but which *types* of models get selected.

This connects to Dehghani's benchmark lottery: the lottery isn't just which benchmark you choose, but the interaction between benchmark and architecture family.

**Refined experimental design:**
1. Collect ImageNet + ImageNet-V2 results for 100+ models (2015-2024)
2. Compute overall Kendall-τ → primary existence test
3. Compute Top-10 overlap → practical relevance test
4. Stratify by architecture family (ResNet, ViT, ConvNeXt, EfficientNet) → fingerprint analysis
5. Run multivariate regression: ranking_stability ~ year + architecture + log(params) → temporal hypothesis

This is elegant because it uses **only existing data** (satisfying feasibility constraints), computes **standard metrics** (no new frameworks), and tests **multiple predictions** in one study.

**Key Points:**
- Architecture-benchmark interaction is a novel angle
- Multi-prediction design increases robustness
- All data and metrics already exist

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion has converged nicely. Let me state the final testable predictions with explicit falsification criteria.

**Primary Hypothesis (H1):** Model rankings on ImageNet are not perfectly preserved on ImageNet-V2, indicating benchmark-specific overfitting affects model selection.

**Operationalization:**
- IV: Benchmark (ImageNet vs ImageNet-V2)
- DV: Kendall-τ correlation of model rankings, Top-10 overlap percentage
- Controlled: Architecture family, model parameters, training data

**Testable Predictions:**

**P1 (Existence):** Kendall-τ(ImageNet rankings, ImageNet-V2 rankings) < 0.90 with 95% CI not including 0.95.
- **Success criterion:** τ < 0.90, p < 0.001
- **Falsification:** τ ≥ 0.95 would indicate rankings are essentially preserved

**P2 (Practical Impact):** Top-10 overlap < 80% (i.e., at least 2 of ImageNet's Top-10 are NOT in V2's Top-10).
- **Success criterion:** Overlap < 80%
- **Falsification:** Overlap ≥ 90% would indicate top performers are stable

**P3 (Temporal Effect):** In multivariate regression, publication_year coefficient is negative and significant (p < 0.05), indicating newer models show less ranking stability.
- **Success criterion:** β_year < 0, p < 0.05 after controlling for architecture + params
- **Falsification:** β_year ≥ 0 or p ≥ 0.05

**Mechanism:** Models trained later have been developed in an environment with more ImageNet-specific knowledge (augmentation recipes, architecture tweaks), leading to greater benchmark-specific adaptation that doesn't transfer.

**Key Points:**
- Three predictions with explicit success/falsification criteria
- Kendall-τ < 0.90 is the primary existence test
- Temporal regression isolates year effect from confounds

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** This hypothesis fills a clear gap — no prior work systematically analyzed ranking stability across benchmark variants. The architecture-benchmark interaction angle is genuinely novel. The temporal overfitting dimension extends Recht et al. in a new direction.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three predictions have explicit numerical thresholds and falsification criteria. Kendall-τ is a standard, well-understood metric. The multivariate regression design controls for obvious confounds. This is properly testable science.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If rankings shift significantly (τ < 0.90), this directly impacts how the community should evaluate and select models. The practical implication — model selection based on popular benchmarks may be suboptimal — is immediately actionable for practitioners.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All data exists (Papers With Code + published papers). All metrics are standard (scipy.stats.kendalltau). No new benchmarks, frameworks, or human evaluation required. This can be executed immediately with existing resources.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Hypothesis: Model rankings on popular ML benchmarks (ImageNet) are not preserved on semantically-similar alternative benchmarks (ImageNet-V2), indicating benchmark-specific overfitting affects model selection decisions.**

**Core claim:** Under controlled conditions (same models, same task semantics), if we evaluate models on a benchmark variant collected independently (ImageNet-V2 vs ImageNet), then model rankings will shift significantly (Kendall-τ < 0.90, Top-10 overlap < 80%), because models have implicitly overfit to benchmark-specific characteristics through iterative community optimization.

**Mechanism:**
1. Popular benchmarks receive concentrated research attention (top 10% = 90% usage)
2. Iterative model development optimizes for benchmark-specific features (augmentation, architecture tweaks)
3. These optimizations don't transfer to independently-collected test sets
4. Result: Rankings shift when evaluated on alternative benchmarks

**Predictions:**
- P1: Kendall-τ < 0.90 (existence of ranking instability)
- P2: Top-10 overlap < 80% (practical impact on model selection)
- P3: Negative year coefficient (temporal overfitting effect)

**Experimental approach:** Collect ImageNet + ImageNet-V2 results for 100+ models (2015-2024), compute ranking correlations, stratify by architecture, run temporal regression with controls.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Selection bias in which models have V2 results — mitigated by noting bias likely *understates* effect
- **Concern 2:** V2 difficulty might be architecture-specific — mitigated by stratifying results
- **Mitigation Strategy:** Report results by architecture family; if consistent across families, concerns are addressed

---

**Convergence achieved after 8 exchanges. All 6 criteria met:**
- [x] SPECIFIC: Core claim stated (ranking shift on V2)
- [x] MECHANISM: Iterative optimization → benchmark-specific features → no transfer
- [x] PREDICTIONS: 3 testable predictions with numerical thresholds
- [x] NOVELTY: No prior systematic ranking correlation analysis
- [x] FEASIBILITY: Existing data + standard metrics
- [x] OBJECTIONS: Selection bias and architecture confounds addressed

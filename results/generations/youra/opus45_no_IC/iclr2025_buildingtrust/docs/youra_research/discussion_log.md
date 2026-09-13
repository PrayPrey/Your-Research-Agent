# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap-1
**Gap Title:** Category-Specific Calibration Analysis Absent
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Question
Do LLMs exhibit systematic miscalibration patterns across different types of factual claims, and can existing calibration methods improve trustworthiness without architectural changes?

### Gap Description
Existing calibration studies (Guo 2017, Kadavath 2022) compute global ECE across entire datasets. TruthfulQA provides 38 category labels but existing analyses aggregate results. No systematic study disaggregates calibration metrics (ECE, MCE) by TruthfulQA category to reveal if certain claim types show different miscalibration patterns.

### Key Resources
- **TruthfulQA** [Lin et al., 2022]: 38 categories, evaluation scripts
- **Temperature Scaling** [Guo et al., 2017]: Reference post-hoc calibration
- **Calibration Toolbox**: ECE/MCE/RMSCE metrics implementation

### Feasibility Constraints (Pipeline-Enforced)
- Must use existing real datasets (TruthfulQA, FACTOR)
- Must use existing benchmarks and metrics (ECE, MCE)
- No new benchmark creation, no synthetic data, no human evaluation

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? Everyone's been computing global ECE as if truthfulness is monolithic — but what if miscalibration is *category-structured*? Looking at [Lin et al., 2022], TruthfulQA has 38 categories covering everything from misconceptions to conspiracies to scientific claims. These aren't random groupings — they represent fundamentally different epistemic structures.

Here's what excites me: LLMs are trained on internet text where some categories have vastly more "confident-sounding" examples than others. Conspiracy theories are often stated with extreme conviction. Scientific hedging is common in academic writing. What if the model's calibration patterns *mirror* the confidence rhetoric of its training distribution?

I propose three unconventional angles:
1. **Confidence-rhetoric transfer hypothesis**: Categories where training data contains more hedged language (science) might show better calibration than categories with assertive rhetoric (misconceptions)
2. **Category-contrastive calibration**: Instead of just measuring per-category ECE, measure how calibration *changes* when a model is asked the same fact framed as different category types
3. **Calibration topology**: Map the 38 categories as nodes in a calibration-similarity space — are there clusters?

**Key Points:**
- TruthfulQA's 38 categories are epistemically distinct, not just topical
- Training data rhetoric may predict calibration patterns
- Category-level analysis could reveal systematic calibration structure

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises intriguing possibilities, but let me ground this in testable form. The "confidence-rhetoric transfer" hypothesis is fascinating precisely because it's falsifiable — but only if we operationalize it correctly.

Here's my concern: [Guo et al., 2017] showed temperature scaling works because neural networks tend toward overconfidence uniformly. If miscalibration varies by category in TruthfulQA, this challenges the assumption of uniform overconfidence. But how do we distinguish *category-specific miscalibration* from *confounded difficulty variation*?

A category with 90% hard questions will show poor calibration metrics even if the model is perfectly calibrated — it's just wrong more often. We need to separate:
1. **Calibration error**: Is confidence aligned with accuracy within a category?
2. **Difficulty confound**: Are some categories simply harder?

I propose this falsification criterion: If category-specific calibration patterns exist, then *within* each difficulty stratum (questions the model gets right vs wrong), we should still see category variation in confidence distributions. If the variation disappears when controlling for accuracy, the "category effect" is a difficulty artifact.

**Key Points:**
- Must separate calibration error from difficulty confound
- Test: category effects should persist within accuracy-stratified analysis
- A single global temperature may fail if category calibration profiles differ

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what we can actually test here. 🔬 Prof. Vera's stratification approach is theoretically sound, but let me check the practical constraints.

TruthfulQA has ~817 questions across 38 categories. That's an average of ~21 questions per category. Some categories likely have fewer than 10 questions. This creates a fundamental statistical power problem: per-category ECE estimates with n<30 will have huge confidence intervals.

The good news: we can actually test this. The calibration-toolbox repository [Pearce] already implements ECE with bootstrap confidence intervals. We can compute per-category ECE, but we MUST report uncertainty. Categories with overlapping CIs cannot be claimed as "differently calibrated."

Mechanistically, here's what works:
1. **Logit extraction**: HuggingFace transformers give us logits directly — no API limitation
2. **Temperature scaling per-category**: Technically trivial — just learn T separately per category
3. **The measurement is valid**: ECE is a proper scoring rule decomposition

What concerns me: the hypothesis about "confidence-rhetoric transfer" requires measuring something about training data that we don't have access to. We can test whether categories differ, but explaining *why* they differ via training rhetoric is not testable with just TruthfulQA.

**Key Points:**
- Small per-category n (~21 avg) requires uncertainty quantification
- Bootstrap CI on per-category ECE is implementable
- Training rhetoric hypothesis is not directly testable — focus on pattern detection first

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does finding category-specific miscalibration mean for the field?

🔭 Dr. Nova's framing is creative, but ⚙️ Prof. Pax correctly narrows us to what's testable. Let me assess significance. If we find that, say, "Misconceptions" category shows 15% higher ECE than "Science" category, who cares?

Here's why the community should care: *calibration research has implicitly assumed homogeneity*. [Guo et al., 2017] learned one temperature for the whole model. [Xiong et al., 2023] compared verbalized vs logit confidence globally. If category structure matters, then:

1. **Practical impact**: Downstream applications in specific domains (medical, legal) may need domain-specific calibration, not generic post-hoc adjustment
2. **Theoretical impact**: It would suggest LLM confidence is shaped by content semantics, not just output mechanics — a fundamentally different view than current calibration theory
3. **Methodological impact**: Future calibration papers would need to report per-category metrics, not just global ECE

But let me be direct: this matters ONLY if the effect size is large enough that global calibration fails while category-specific calibration succeeds. A statistically significant but tiny difference is publishable but not impactful.

**Key Points:**
- Significance requires demonstrable global-vs-category performance gap
- Challenges homogeneity assumption underlying current calibration methods
- Must show practical benefit, not just statistical significance

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can synthesize these perspectives into a stronger hypothesis. Let me build on the valid criticisms to refine our direction.

🔬 Prof. Vera's difficulty confound is crucial — we address it by measuring Expected Calibration Error (ECE), which already accounts for accuracy. ECE measures whether P(correct|confidence=p) = p, regardless of overall accuracy. A hard category can still be well-calibrated if the model is appropriately uncertain about hard questions.

⚙️ Prof. Pax's statistical power concern is valid but addressable: we can group the 38 categories into semantic clusters (misconceptions, science, culture, etc.) to increase n per stratum. [Lin et al., 2022] actually provides a category hierarchy we can exploit.

🎯 Dr. Sage's demand for practical impact gives us our success criterion: we need to show that category-specific temperature scaling outperforms global temperature scaling in ECE reduction.

Here's the strengthened hypothesis:

**Core claim**: LLMs exhibit heterogeneous calibration patterns across TruthfulQA category clusters, and cluster-specific temperature scaling achieves lower ECE than global temperature scaling.

**Mechanism**: Different semantic category clusters have different optimal calibration temperatures because the model's confidence behavior is shaped by category-specific features (linguistic patterns, question difficulty distributions, training data characteristics).

**Key Points:**
- ECE already controls for difficulty by definition
- Group categories into clusters for statistical power
- Success criterion: cluster-specific T outperforms global T

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. 🛡️ Dr. Ally's refinement is cleaner, but I have serious concerns.

First, the mechanism claim is still untestable. You say calibration differs "because" of linguistic patterns or training data — but we cannot measure training data characteristics. The "because" is speculation. What we can test: categories differ. Why they differ is not answerable with this setup.

Second, cluster-specific temperature scaling is a trivially stronger model. Of course more parameters fit better. If you learn 5 separate temperatures instead of 1, you'll get lower ECE on training data. The real question: does it generalize? How do you test that cluster-specific calibration works on *new* questions from the same clusters?

Third, let me push on statistical validity. You're proposing to:
1. Split TruthfulQA into clusters
2. Learn per-cluster T on some portion
3. Test on held-out portion

But with ~817 questions total, splitting into 5 clusters + train/test leaves maybe 80 questions per cluster for testing. Bootstrap CIs on n=80 ECE estimates will be wide.

What would convince me: pre-registered cluster assignments (using the category hierarchy in the original paper), clear train/test split, and a calibration improvement that exceeds the confidence interval.

**Key Points:**
- Mechanism claim is untestable — drop or weaken it
- Must demonstrate generalization, not just in-sample fit
- Pre-registration and clear evaluation protocol required

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex makes fair points, but let me push back on one thing and propose a creative solution.

The mechanism doesn't need to be fully testable in this study — we can frame it as *motivation* for the pattern detection, with mechanism investigation as future work. Many influential papers demonstrate a phenomenon first and explain it later.

But here's a creative angle to address generalization: what if we use FACTOR dataset [Muhlgay et al., 2023] as an external validation set? FACTOR also tests factuality with different confidence patterns. If cluster-specific calibration learned on TruthfulQA transfers to improve ECE on FACTOR, that's strong evidence of real structure, not overfitting.

Actually, this could be even more novel: **cross-benchmark calibration transfer**. Learn calibration parameters on one truthfulness benchmark, test on another. If it works, it suggests the calibration structure reflects something fundamental about how LLMs handle factual claims, not just idiosyncrasies of one dataset.

**Key Points:**
- Mechanism is motivation, not claim — future work to explain
- FACTOR dataset enables external validation
- Cross-benchmark transfer as novelty angle

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's cross-benchmark idea has merit, but let me sharpen the experimental design.

The problem with FACTOR as validation: it may have different category structure than TruthfulQA. If we learn "cluster-specific" temperatures on TruthfulQA clusters, which FACTOR questions map to which clusters? This requires explicit mapping criteria.

Here's my proposal for rigorous evaluation:

**Within-benchmark evaluation** (primary):
1. Use TruthfulQA's existing category hierarchy from [Lin et al., 2022]
2. Group into 5-7 semantic clusters (pre-registered, following paper's categorization)
3. 5-fold cross-validation: for each fold, learn cluster temperatures on 80%, test on 20%
4. Compare global-T vs cluster-T ECE on test folds

**Cross-benchmark validation** (secondary, exploratory):
1. Define mapping rules from FACTOR questions to TruthfulQA clusters
2. Apply TruthfulQA-trained cluster temperatures to FACTOR
3. Compare against globally-calibrated baseline on FACTOR

The key falsification: if cluster-specific T does NOT outperform global T in cross-validation, the category structure doesn't provide useful calibration information beyond fitting noise.

**Key Points:**
- 5-fold CV on TruthfulQA as primary evaluation
- FACTOR as secondary validation with explicit category mapping
- Clear falsification: cluster-T must beat global-T in held-out data

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify this is actually implementable. 🔬 Prof. Vera's protocol is sound. Here's my technical feasibility check:

**Data access**: TruthfulQA is publicly available with category labels in the CSV. ✓
**Model access**: Can use HuggingFace transformers (Llama-2-7B, Mistral-7B, etc.) with logit extraction. ✓
**Calibration implementation**: temperature_scaling repo [Gpleiss] provides reference code. ✓
**ECE with uncertainty**: calibration-toolbox [Pearce] has bootstrap CI implementation. ✓

**Computational requirements**:
- Running inference on ~817 questions × 5 models × 5 folds = ~20,000 inference calls
- Each call is one forward pass — tractable on single GPU in hours
- Temperature optimization is cheap (1D optimization per cluster)

**One technical concern**: verbalized confidence. The gap mentions RQ1 about "verbalized confidence vs actual accuracy." If we also want to test verbalized confidence calibration, we need to prompt for confidence estimates (0-100%), which adds prompt engineering complexity. Recommendation: focus on logit-based confidence for primary analysis, verbalized as optional comparison.

**Key Points:**
- All components have existing implementations
- Computation tractable: hours on single GPU
- Recommend logit-based primary, verbalized optional

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess what we've converged toward. The hypothesis has sharpened considerably:

**What's novel**: Category-level calibration analysis on TruthfulQA — this specific disaggregation hasn't been done. The cross-benchmark transfer angle is fresh.

**What's impactful**: If cluster-specific calibration outperforms global calibration, it:
1. Challenges the "one temperature fits all" assumption in the calibration literature
2. Provides practical guidance for domain-specific applications
3. Opens a research direction on content-dependent calibration

**What remains incremental**: The method itself (temperature scaling) is not new — we're just applying it at finer granularity. This is an empirical contribution, not a methodological one.

My assessment: this is a solid **empirical contribution** paper. Not paradigm-shifting, but valuable. The key is execution: rigorous evaluation, multiple models, clear statistical significance.

To increase impact: include model scale analysis. Does the category structure of miscalibration change across model sizes? This addresses RQ4 from the original research question and adds depth.

**Key Points:**
- Solid empirical contribution, not methodological
- Impact via challenging homogeneity assumption
- Add model scale analysis for depth

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what we've built. The hypothesis is strong enough to proceed.

**Final Hypothesis Structure:**

**Core Claim**: LLMs exhibit heterogeneous calibration patterns across semantic category clusters in truthfulness benchmarks. Cluster-specific temperature scaling reduces Expected Calibration Error (ECE) compared to global temperature scaling.

**Mechanism (motivational, not primary claim)**: Category-dependent calibration arises because different semantic domains evoke different confidence behaviors in LLMs, potentially reflecting training distribution characteristics.

**Predictions**:
1. P1 (Primary): Per-cluster ECE values differ significantly across TruthfulQA category clusters (chi-squared or bootstrap test)
2. P2: Cluster-specific temperature scaling achieves lower mean ECE than global temperature scaling in 5-fold cross-validation
3. P3: The cluster-specific calibration improvement transfers to FACTOR benchmark (secondary validation)

**Experimental Setup**:
- Dataset: TruthfulQA (primary), FACTOR (validation)
- Models: Llama-2-7B, Mistral-7B, Llama-2-13B (scale comparison)
- Metrics: ECE with bootstrap CI, per-cluster and global
- Method: Temperature scaling (global vs cluster-specific)

**Key Points:**
- Core claim is testable and falsifiable
- Three nested predictions with clear success criteria
- Protocol addresses statistical power and generalization concerns

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is much stronger. Let me do final stress-testing.

**Concern 1**: P1 (clusters differ) is almost certainly true. ECE will vary by cluster due to difficulty differences alone. The real test is P2: does knowing the cluster help calibration? I'd reframe P1 as "cluster membership predicts calibration behavior beyond difficulty."

**Concern 2**: How do you define the clusters? If you cluster post-hoc to maximize ECE variance, that's cheating. The clusters MUST be pre-defined by TruthfulQA's category hierarchy, before seeing results.

**Concern 3**: Temperature scaling on n<100 questions per cluster is unstable. Consider regularization: cluster temperatures should be initialized at global T and penalized for deviating too far. This prevents overfitting while still capturing real variation.

**Concern 4**: What's the null hypothesis statistical test? You need: H0 = "cluster-specific T provides no benefit over global T" with a proper test. I suggest: paired t-test on per-fold ECE (global vs cluster), or permutation test on the ECE difference.

If you address these, I'm satisfied the hypothesis is ready for Phase 2B.

**Key Points:**
- Clusters must be pre-defined, not optimized post-hoc
- Consider regularized cluster temperatures
- Need explicit null hypothesis test

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

Addressing 🔍 Prof. Rex's concerns with specific design choices:

**Cluster definition (pre-registered)**: Use TruthfulQA's documented category hierarchy. The paper groups 38 categories into broader themes. We adopt these groupings as-is, documented before any analysis. Example: "Misconceptions", "Conspiracies", "Stereotypes" might form a "Common Falsehoods" cluster.

**Regularized temperature scaling**: Good idea. Implement as: T_cluster = T_global + δ_cluster, where δ_cluster is learned with L2 penalty. This ensures cluster temperatures can't deviate arbitrarily from global.

**Statistical test specification**:
- Null H0: Mean ECE(cluster-specific) = Mean ECE(global)
- Test: Paired t-test across 5 folds (same test questions, different calibration)
- Significance: p < 0.05 with Bonferroni correction if testing multiple models
- Effect size: Report Cohen's d; we need d > 0.3 for practical significance

**Falsification crystal clear**: If paired t-test shows p > 0.05 or d < 0.3, the hypothesis is falsified. We'd conclude that category structure doesn't provide useful calibration information.

**Key Points:**
- Pre-registered clusters from TruthfulQA hierarchy
- Regularized learning prevents overfitting
- Paired t-test with effect size threshold

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility verification on 🔬 Prof. Vera's protocol:

**Cluster hierarchy access**: Checked — TruthfulQA GitHub repo has category groupings documented. We can extract and pre-register.

**Regularized temperature scaling**: Trivial modification to [Gpleiss] code. Add regularization term: loss = NLL + λ * (T_cluster - T_global)^2. λ chosen by validation on one fold, fixed for rest.

**Statistical tests**: scipy.stats.ttest_rel for paired t-test. Already standard.

**Compute estimate revised**:
- 817 questions × 3 models = 2,451 inference calls for logits
- 5-fold CV × (global + 5-7 cluster) temperatures = ~40 optimization runs per model
- Each optimization is ~100 iterations of 1D search
- Total: <6 hours on single A100

**One remaining question**: How many clusters? The TruthfulQA paper has category labels but not explicit cluster assignments. We need to make a decision:
- Option A: Use top-level category groups if documented
- Option B: Domain-expert grouping (we define, pre-register)
- Option C: Use hierarchical clustering on category embeddings (but this risks post-hoc)

I recommend Option A or B with clear documentation.

**Key Points:**
- All components implementable
- 6 hours compute on A100
- Need to decide cluster assignment method

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Synthesizing final decisions for Phase 2B handoff:

**Cluster Assignment (Option B — Domain-Expert Pre-Registration)**:
Looking at TruthfulQA's 38 categories, I propose these pre-registered clusters:

1. **Misconceptions**: Misconceptions, Indexical errors, Confusion
2. **Conspiracies & Paranormal**: Conspiracies, Paranormal, Superstitions
3. **Science & Health**: Science, Health, Nutrition
4. **History & Politics**: History, Politics, Law
5. **Culture & Society**: Sociology, Psychology, Economics
6. **Language & Logic**: Language, Logical falsehoods, Proverbs
7. **Other**: Weather, Advertising, Fiction, etc.

This is ~5-6 clusters of reasonable size. We document this BEFORE seeing any calibration results.

**Final Hypothesis Statement**:
"Under evaluation on TruthfulQA benchmark, if LLM predictions are calibrated using cluster-specific temperature scaling (with pre-registered semantic clusters), then Expected Calibration Error will be lower than global temperature scaling, because semantic category membership captures systematic variation in model confidence behavior."

**Predictions (ranked)**:
- P1 (primary, must pass): Cluster-specific T achieves statistically significant ECE reduction vs global T (paired t-test, p<0.05, d>0.3)
- P2 (supporting): Per-cluster ECE varies significantly across clusters (ANOVA on cluster ECE)
- P3 (exploratory): Calibration improvement transfers to FACTOR benchmark

**Key Points:**
- 7 pre-registered clusters defined
- Clear hypothesis in Under-If-Then-Because format
- Primary success criterion: p<0.05, d>0.3 on paired t-test

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** This study introduces category-disaggregated calibration analysis to TruthfulQA — a perspective absent from existing calibration literature. The cross-benchmark transfer angle adds further novelty. While the method (temperature scaling) is known, applying it at category-cluster granularity with pre-registered semantic groupings is genuinely new.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Crystal clear falsification criteria: paired t-test with p<0.05 and Cohen's d>0.3 threshold. The 5-fold cross-validation design separates training from testing. Pre-registered clusters prevent post-hoc optimization. The hypothesis fails if cluster-specific T doesn't beat global T on held-out data.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Solid empirical contribution challenging the homogeneity assumption in calibration research. If successful, provides practical guidance for domain-specific applications and opens a research direction. Not paradigm-shifting — the method is incremental — but valuable for the calibration community.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully implementable with existing resources. TruthfulQA data public, HuggingFace models accessible, calibration code available. Compute is tractable (<6 hours A100). Regularized temperature optimization is a minor code modification. No technical barriers.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis proposes that LLM calibration on truthfulness benchmarks is not homogeneous — it varies systematically by semantic category cluster. Specifically, under evaluation on TruthfulQA, cluster-specific temperature scaling (with 7 pre-registered semantic clusters: Misconceptions, Conspiracies/Paranormal, Science/Health, History/Politics, Culture/Society, Language/Logic, Other) will achieve lower Expected Calibration Error than global temperature scaling.

The core mechanism is that semantic category membership captures systematic variation in model confidence behavior — different types of factual claims evoke different calibration profiles. This may reflect training distribution characteristics, but the mechanism is motivational rather than a primary testable claim.

The primary prediction (P1) requires cluster-specific calibration to outperform global calibration with statistical significance (paired t-test p<0.05) and practical significance (Cohen's d>0.3) in 5-fold cross-validation. Secondary predictions test per-cluster ECE variation (P2) and cross-benchmark transfer to FACTOR (P3).

The experimental setup uses TruthfulQA with Llama-2-7B, Mistral-7B, and Llama-2-13B, extracting logits for temperature scaling. ECE computed with bootstrap confidence intervals using the calibration-toolbox implementation.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Small per-cluster sample sizes (~100-150 questions) may limit statistical power — bootstrap CIs will be important
- Cluster assignment is domain-expert judgment — while pre-registered, alternative groupings might yield different results
- **Mitigation Strategy:** Document cluster rationale thoroughly, report sensitivity analysis with alternative groupings as supplementary material, use regularized temperature learning to prevent overfitting


# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap1
**Gap Title:** Quantitative Contamination-Performance Correlation
**Date:** 2026-08-10
**Architecture:** Self-Play Loop (Claude-only, IC-ablation)

### Research Gap Description

**Current State:** Existing work establishes that contamination exists and proposes detection methods, but does not systematically quantify the relationship between contamination levels and benchmark score inflation.

**Missing Piece:** A quantitative model that maps contamination intensity (n-gram overlap percentage) to expected benchmark score inflation across model families.

**Potential Impact:** High - Would enable benchmark reliability scoring and contamination-aware model comparison.

### Key Papers for Reference

1. **Sainz et al. (2023)** - "NLP Evaluation in trouble" - Defines contamination levels but not performance correlation (arXiv: 2310.18018)
2. **Yang et al. (2023)** - "Rethinking Benchmark and Contamination" - Shows 8-18% overlap but no score impact analysis (arXiv: 2311.04850)
3. **Dong et al. (2024)** - "Generalization or Memorization" - Proposes TED mitigation but limited correlation data (arXiv: 2402.15938)
4. **Choi et al. (2025)** - "Kernel Divergence Score" - Dataset-level contamination quantification (arXiv: 2502.00678)

### Implementation Resources

- ntunlp/LLMSanitize (61 stars) - Multi-method contamination detection
- iamgroot42/mimir (190 stars) - Memorization metrics and MIA implementations
- EleutherAI/lm-evaluation-harness (13K stars) - 13-gram decontamination standard

### Research Questions to Address

- Q3: How does contamination level correlate with benchmark score inflation across model families?
- Q4: Can we develop a contamination index that predicts benchmark reliability for a given model-dataset pair?

### Feasibility Constraints (Pipeline-Enforced)

- Must use existing real datasets and existing benchmarks
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach contamination-performance correlation not as a linear relationship, but as a *threshold phenomenon*? Looking at Sainz et al.'s work, they define contamination levels but never ask: at what point does contamination actually *matter* for benchmark inflation?

Here's my wild idea: contamination might follow a sigmoid curve where low overlap (say, <5%) has negligible impact on scores, but there's a critical threshold (perhaps 10-15%) where memorization starts dramatically inflating performance. Beyond that, we hit diminishing returns as models can only "cheat" so much.

What excites me is the cross-domain connection to *overfitting theory*. We know generalization error behaves non-linearly with training data overlap. Yang et al. found 8-18% overlap in RedPajama—right in what I'd hypothesize is the "critical zone." What if we could map this to a contamination-inflation transfer function?

The paradigm shift here: instead of asking "is this benchmark contaminated?" (binary), we ask "what's the expected score inflation given this contamination profile?" (continuous, predictive). This transforms benchmark evaluation from pass/fail to calibrated trust scores.

**Key Points:**
- Propose threshold/sigmoid model for contamination-inflation relationship
- Critical zone hypothesis: 10-15% overlap as inflection point
- Paradigm shift from binary contamination detection to continuous reliability scoring

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your sigmoid hypothesis is intriguing, but let me stress-test it. What would disprove this threshold model? If contamination-inflation is truly sigmoid, we need to operationalize "contamination intensity" precisely—13-gram overlap percentage is one measure, but Yang et al. showed paraphrasing bypasses this.

Here's my concern: we need to distinguish *verbatim contamination* (exact test questions in training) from *semantic contamination* (paraphrased or conceptually similar content). These likely have different inflation curves. A testable prediction would be: "Verbatim contamination at X% produces Y% score inflation, while semantic contamination at X% produces Z% inflation, where Y > Z."

For falsifiability, I propose: if we find a model with high n-gram overlap (>15%) but no significant score inflation compared to a clean baseline, the threshold model fails. Conversely, if low-overlap models (<5%) show substantial inflation, something else is at play.

The critical confound is *model capability*. A more capable model might show less inflation from contamination because it can solve problems without memorization. We'd need to control for base capability using uncontaminated benchmarks.

**Key Points:**
- Distinguish verbatim vs. semantic contamination—different inflation curves expected
- Falsification criteria: high overlap without inflation, or low overlap with inflation
- Critical confound: model capability must be controlled via uncontaminated benchmarks

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me situate this in the broader research landscape. The question isn't just "can we model contamination-inflation?"—it's "why does the field need this model, and what changes if we have it?"

Currently, benchmark results are published as point estimates without contamination adjustment. If we develop a reliable contamination-inflation transfer function, we could introduce *calibrated benchmark scores*—adjusted for estimated contamination. This would fundamentally change how the community interprets model comparisons.

But here's the significance challenge: existing work like Dong et al.'s TED already proposes mitigation. What's genuinely new about predicting inflation versus mitigating it? I'd argue the contribution is *retrospective calibration*—we can reassess historical benchmark claims, not just future ones. The Kernel Divergence Score (Choi et al., 2025) moves toward dataset-level quantification, but stops short of performance correlation.

The field impact hinges on whether the transfer function *generalizes*. If contamination-inflation relationships are model-family-specific (GPT vs. LLaMA vs. Pythia), we need a family of functions, reducing practical utility. If there's a universal curve (or parameterized by model size/architecture), that's a genuine contribution.

**Key Points:**
- Enables calibrated benchmark scores—adjusting published results for contamination
- Retrospective calibration of historical claims is the novel contribution
- Generalizability across model families determines field impact

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical feasibility. The mechanism Dr. Nova proposes—a contamination-inflation transfer function—requires establishing ground truth for both variables. For open-weight models, we can compute n-gram overlap against known training corpora (The Pile, RedPajama). But "score inflation" requires a *counterfactual*: what would this model score *without* contamination?

Here's the fundamental barrier: we can't untrain a model. The cleanest approach uses models trained on documented corpora where we can verify benchmark presence/absence. Pythia models on The Pile are promising—EleutherAI documents the training data.

For the mechanism to work scientifically:
1. **Overlap measurement** is feasible—13-gram standard exists, tools available (lm-eval-harness)
2. **Inflation measurement** is harder—we need either (a) pre/post contamination scores (impossible for pretrained models), or (b) proxy via comparing models with different contamination levels but similar base capability

The Dong et al. approach uses distribution analysis as a *proxy* for contamination impact. We could validate: does their CDD score correlate with our n-gram overlap? If so, we have convergent evidence.

One theoretical concern: if a model truly learned generalizable knowledge from contaminated data (not just memorization), is that "inflation"? The hypothesis assumes contamination = memorization, but this needs validation.

**Key Points:**
- Ground truth inflation requires counterfactual—compare models with documented, differential contamination
- Pythia on The Pile is a tractable test case (documented training corpus)
- Theoretical gap: contamination might teach genuine knowledge, not just memorization

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on all perspectives, let me synthesize and strengthen the emerging hypothesis. Prof. Pax raises a critical point about counterfactuals—we can't untrain models. But here's how we address it:

**Strengthened Hypothesis:** For open-weight models with documented training corpora, we can establish contamination-inflation correlation by comparing benchmark performance *across models* with measured contamination differentials, controlling for base capability via uncontaminated benchmark suites.

The key refinement from Prof. Vera: we focus on *verbatim* contamination first (13-gram overlap), establishing the easier case before tackling semantic contamination. This is scientifically sound—start with the cleaner signal.

From Dr. Sage's concern about generalizability: we explicitly scope to a *family-specific* transfer function initially (e.g., Pythia models), with the research contribution being the *methodology* for deriving such functions. If the methodology works, others can extend to GPT/LLaMA families.

Evidence supporting feasibility:
- MIMIR benchmark provides WikiMIA ground truth for membership detection
- lm-eval-harness provides standardized 13-gram decontamination
- Pythia suite offers 7 model sizes with identical training corpus

What if we framed this as: "We develop a methodology for deriving contamination-inflation transfer functions, validated on the Pythia family using documented contamination levels against MMLU/ARC/HellaSwag benchmarks"?

**Key Points:**
- Refined hypothesis uses cross-model comparison with contamination differentials
- Scope to Pythia family first—methodology contribution over universal function
- Leverage existing tools: MIMIR, lm-eval-harness, Pythia model suite

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me break this down. Dr. Ally's synthesis has merit, but I see critical weaknesses that need addressing before this is bulletproof.

**Weakness 1: The contamination measurement problem.** You propose 13-gram overlap, but Yang et al. showed 8-18% overlap in RedPajama. If The Pile has similar overlap rates with benchmarks, *all* Pythia models are contaminated. You can't compare "contaminated vs clean" if everything is contaminated—only "more vs less contaminated." Is your methodology sensitive enough to detect inflation differences across that range?

**Weakness 2: Base capability confound.** You suggest controlling via "uncontaminated benchmark suites." Name one. LiveBench is new (2024), so older models weren't trained after its creation—but it's also not widely used. If you use MMLU-style benchmarks to measure capability, how do you know *those* aren't contaminated too?

**Weakness 3: The Pythia scope limitation.** Scoping to Pythia is scientifically careful, but the practical impact is limited. If the transfer function is family-specific and only validated on one family, reviewers will ask: "Does this generalize, or is this a Pythia curiosity?"

What would convince me: (1) A clear operationalization of "contamination differential" that's measurable across model sizes. (2) An uncontaminated capability baseline—maybe using LiveBench or newly-created held-out test sets. (3) At least a preliminary signal that the methodology might transfer to another model family.

**Key Points:**
- All Pythia models may be similarly contaminated—need sensitivity analysis
- Uncontaminated baseline for capability measurement is undefined
- Single-family validation limits practical impact—need transferability evidence

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are sharp, but they open creative opportunities! Let me address the "everything is contaminated" problem with a paradigm shift.

What if we don't need a "clean" baseline at all? Instead of contaminated vs. clean, we study **contamination gradient within a corpus**. The Pile has 22 subsets (Books3, Wikipedia, GitHub, etc.). Different Pythia training checkpoints have seen different amounts of data. What if we correlate *per-checkpoint* benchmark performance with *cumulative contamination exposure* at that checkpoint?

This is the breakthrough insight: we don't need clean models. We need **models at different points on the contamination curve**. Pythia releases intermediate checkpoints—this gives us the contamination gradient organically!

For the capability confound, here's a wild idea: use **in-distribution vs out-of-distribution** benchmark performance ratio. If contamination inflates scores, it should inflate ID performance (memorized benchmarks) more than OOD performance (novel questions). LiveBench or dynamic benchmarks could serve as the OOD reference.

For transferability, what about a *calibration transfer* approach? Derive the Pythia transfer function, then test if it *predicts* contamination inflation in other families given measured overlap. This is a stronger claim: the function isn't just descriptive, it's predictive across families.

**Key Points:**
- Use checkpoint-level contamination gradients instead of clean baselines
- ID/OOD performance ratio as capability-controlled inflation signal
- Calibration transfer: predict other families' inflation from Pythia-derived function

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's checkpoint gradient idea is methodologically elegant. Let me formalize it into testable predictions.

**Prediction 1 (Primary):** For Pythia models, there exists a positive correlation (r > 0.5) between cumulative benchmark-relevant n-gram exposure (measured at each checkpoint) and benchmark score inflation (measured as deviation from capability-predicted performance).

**Prediction 2 (Mechanism):** The inflation effect is stronger for exact-match benchmarks (e.g., ARC-Challenge) than generation benchmarks (e.g., HellaSwag), because verbatim memorization benefits exact-match more.

**Prediction 3 (Threshold):** Below 5% cumulative exposure, inflation is statistically indistinguishable from noise. Above 10%, inflation scales approximately linearly (rejecting sigmoid in favor of piecewise-linear).

The falsification criteria:
- If correlation is negative or null (r < 0.2), the hypothesis fails
- If generation benchmarks show equal or greater inflation, the mechanism is wrong
- If inflation is uniform across all exposure levels, the threshold model fails

For experimental design, we need:
1. Per-checkpoint n-gram overlap computation (feasible with lm-eval-harness scripts)
2. Benchmark evaluation at each checkpoint (computationally expensive but feasible)
3. Capability baseline via OOD benchmark (LiveBench or recent BIG-Bench Hard tasks)

The confound Prof. Rex raised—capability differences across checkpoints—is real. Later checkpoints are more capable *and* more contaminated. We need to detrend for capability first, then measure residual inflation.

**Key Points:**
- P1: r>0.5 correlation between cumulative exposure and inflation
- P2: Exact-match benchmarks inflate more than generation benchmarks
- P3: Threshold at ~5% exposure, linear scaling above 10%
- Must detrend for capability before measuring inflation residuals

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's formalization is rigorous. Let me assess technical feasibility of each component.

**N-gram exposure computation:** Feasible. The Pile is 825GB but indexed. For each Pythia checkpoint, we know how many tokens were seen. We can compute 13-gram overlap between The Pile's first N tokens and benchmark test sets. Tools exist (overlapy, lm-eval-harness decontamination scripts).

**Per-checkpoint evaluation:** This is the bottleneck. Pythia has 154 checkpoints across 8 model sizes. Evaluating all checkpoints on MMLU/ARC/HellaSwag/WinoGrande is ~2000 evaluation runs. At ~1 hour per full eval, that's 83 days of compute. **Proposed optimization:** Sample 10-15 checkpoints per model size spanning the training curve (early, middle, late). This reduces to ~120 runs—tractable.

**Capability baseline:** LiveBench is promising but has limited historical data. Alternative: use perplexity on held-out text (e.g., Pile validation set) as capability proxy. More capable models = lower perplexity. This gives us a continuous capability measure to detrend against.

**Potential issue:** The Pile validation set might also appear in training (data leakage within Pile). Need to verify EleutherAI's train/val/test split methodology.

One mechanism concern: per-checkpoint evaluation assumes the model "learns" contamination progressively. But what if contamination effects only manifest after convergence? We'd see flat inflation across checkpoints until the final 10%, which would look like a threshold but have a different cause (convergence dynamics, not exposure accumulation).

**Key Points:**
- N-gram computation: feasible with existing tools
- Checkpoint evaluation: sample 10-15 per size (~120 runs total)
- Capability detrending: use perplexity on Pile validation set
- Alternative explanation: inflation might be convergence-dependent, not exposure-dependent

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent technical grounding from Prof. Pax. Let me address the convergence-vs-exposure alternative explanation, because this determines our mechanistic claim.

**Strengthened Mechanism:** Contamination-induced inflation operates through progressive memorization during training, where benchmark-relevant n-grams are encoded into model weights proportionally to exposure frequency. This predicts *gradual* inflation accumulation, not sudden onset at convergence.

**Test to distinguish:** If inflation is exposure-dependent, early checkpoints with high benchmark overlap should show measurable inflation even at 25% training. If inflation is convergence-dependent, inflation should be near-zero until final 10% of training regardless of early overlap.

**Design refinement:** Prof. Pax suggested 10-15 checkpoints per model. I'd add: ensure checkpoints span the full training curve *and* include multiple checkpoints in the final 10% to capture potential convergence effects. Specifically: 5 early (0-30%), 5 middle (30-70%), 5 late (70-100%).

For the capability detrending, I propose a two-stage approach:
1. **Stage 1:** Fit capability ~ perplexity relationship using LiveBench (uncontaminated)
2. **Stage 2:** Predict expected benchmark score from perplexity, measure residual as inflation

This cleanly separates capability gains from contamination gains. If the Pile validation set is contaminated, perplexity-based detrending would actually *underestimate* inflation (more conservative claim).

**Consolidated Hypothesis Statement:**

*Under the condition of documented training corpora and measurable n-gram overlap, if we increase cumulative benchmark-relevant exposure during training, then benchmark scores will show positive inflation residuals after capability detrending, because progressive memorization encodes benchmark content proportionally to exposure frequency.*

**Key Points:**
- Exposure-dependent mechanism predicts gradual inflation, testable at early checkpoints
- Checkpoint distribution: 5 early, 5 middle, 5 late per model size
- Two-stage capability detrending: perplexity → predicted score → residual inflation
- Formal hypothesis statement now includes scope, IV, DV, mechanism

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is sharpening, but let me probe remaining weaknesses.

**Weakness 4: Effect size.** What inflation magnitude matters? If 15% contamination produces 1% score inflation, is that scientifically meaningful? The hypothesis should specify expected effect size. Looking at Yang et al.'s 8-18% overlap, if this corresponds to ~5-10% score inflation, that's meaningful. If <2%, it's noise.

**Weakness 5: Benchmark heterogeneity.** MMLU has 57 subjects. Some subjects may have high contamination (popular topics), others low. Treating MMLU as monolithic obscures subject-level dynamics. A stronger test would analyze per-subject contamination-inflation relationships.

**Weakness 6: The memorization-generalization boundary.** Dr. Ally says "progressive memorization," but how do we distinguish a model that memorized "The answer is B" from one that learned "Questions about X have answers involving Y"? The latter is legitimate generalization from training data, not cheating.

What would strengthen the hypothesis:
1. **Effect size bound:** Specify minimum detectable effect (e.g., "inflation ≥3% at 10% contamination")
2. **Per-subject analysis:** Report subject-level correlations, not just aggregate
3. **Memorization operationalization:** Use verbatim completion rate (model can complete exact test sequences) as memorization indicator, separate from n-gram overlap

The verbatim completion test is key: if a model completes "The capital of France is __" with "Paris" from a benchmark, that could be memorization OR world knowledge. But if it completes "According to the ARC-Challenge question about thermal expansion, the answer is __" with the exact option letter, that's memorization.

**Key Points:**
- Effect size: minimum 3% inflation at 10% contamination to be meaningful
- Per-subject MMLU analysis exposes heterogeneity
- Verbatim completion rate operationalizes memorization vs. learning

---

### Exchange 12

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex's point about effect size is crucial for impact. Let me address what makes this contribution matter to the field.

**Significance argument:** Even 2-3% systematic inflation is meaningful when comparing state-of-the-art models that differ by <1% on leaderboards. If Model A beats Model B by 0.5% but A has 5% more contamination, the community needs to know.

**The practical contribution** is not just the transfer function but the *methodology* for computing calibrated scores. Imagine: "Model A scores 85.2% on MMLU (contamination-adjusted: 82.1%)" alongside raw scores. This changes how results are interpreted.

**Per-subject analysis** (Prof. Rex's point) actually *increases* impact. If we show that "College Chemistry" has 25% contamination and 8% inflation while "Abstract Algebra" has 2% contamination and <1% inflation, that's actionable. Benchmarks could report weighted scores excluding high-contamination subjects.

For novelty positioning against Dong et al. (TED) and Choi et al. (Kernel Divergence):
- **TED** mitigates contamination effects but doesn't quantify the raw inflation
- **Kernel Divergence** quantifies contamination presence but not performance impact
- **Our contribution:** closes the loop—contamination → inflation → calibrated scores

This positions the work as *completing* the contamination detection pipeline: detection (existing) → quantification (Kernel Divergence) → **impact modeling (ours)** → mitigation (TED).

**Key Points:**
- 2-3% inflation is significant given <1% leaderboard margins
- Practical output: contamination-adjusted benchmark scores
- Per-subject analysis enables weighted/excluded scoring
- Novelty: completes detection→quantification→impact→mitigation pipeline

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Dr. Sage's pipeline positioning is excellent. Let me push further—what if our contribution enables something even more transformative?

**Predictive contamination scoring.** If we derive the transfer function from Pythia, we could *predict* contamination inflation for new models without running expensive overlap computations. The workflow:
1. Sample model's behavior on known-contaminated vs. clean benchmark items
2. Estimate contamination level from behavioral signature
3. Apply transfer function to predict score inflation
4. Report calibrated score

This is black-box applicable—you don't need training corpus access. The transfer function, once derived from open-weight models, becomes a calibration tool for proprietary models.

**Cross-domain connection:** This parallels *domain adaptation* in transfer learning. The contamination-inflation relationship is the "domain shift"—we're learning to quantify and correct for it. Could we frame contamination calibration as a specific instance of benchmark domain adaptation?

**One more wild idea:** What if we release a contamination-aware leaderboard? Submit your model, we estimate contamination via behavioral tests, apply calibration, rank by adjusted scores. This could become the field's new evaluation standard.

But I acknowledge: this is ambitious. The core hypothesis stands without these extensions. They're the "future work" that demonstrates impact potential.

**Key Points:**
- Predictive scoring: behavioral contamination estimation + transfer function
- Black-box applicability extends to proprietary models
- Frame as benchmark domain adaptation correction
- Future: contamination-aware evaluation leaderboard

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me reality-check the ambitious extensions while affirming the core is solid.

**Core hypothesis feasibility: CONFIRMED.** The essential experiment—correlating checkpoint-level contamination exposure with inflation residuals on Pythia—is tractable. 120 eval runs, existing tools, documented corpus. This can be done in 2-3 weeks of compute.

**Predictive scoring extension:** Theoretically possible but adds complexity. Behavioral contamination estimation (without corpus access) is itself a research problem (see MIMIR's attempts). I'd suggest this as **Phase 2** after validating the core transfer function.

**Black-box transfer to proprietary models:** Scientifically interesting but unvalidated. The transfer function derived from Pythia might not apply to GPT-4's architecture/training. **Scope risk**—claiming broad applicability before validation could undermine the core contribution.

**Leaderboard idea:** Ambitious but out of scope for hypothesis validation. This is an engineering/community effort after scientific validation.

**My recommendation:** The core hypothesis is ready for implementation. Extensions are promising future directions but should not inflate the current claim. The contribution is:

*"A methodology for deriving contamination-performance transfer functions, validated on the Pythia family, demonstrating that checkpoint-level n-gram exposure correlates with benchmark score inflation after capability detrending."*

This is achievable, falsifiable, and impactful. Over-promising (black-box, cross-family, leaderboard) risks underselling the solid core.

**Key Points:**
- Core hypothesis: feasible with current resources
- Predictive/black-box extensions: Phase 2 after core validation
- Leaderboard: out of scope, future engineering effort
- Recommendation: crisp scope to maximize validated contribution

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's scope guidance is wise. Let me consolidate the final hypothesis with everyone's input.

**Final Hypothesis Statement:**

*"For language models trained on documented corpora, there exists a quantifiable, positive relationship between cumulative benchmark-relevant n-gram exposure and benchmark score inflation. Specifically, for the Pythia model family trained on The Pile, controlling for capability via perplexity-based detrending, we predict: (1) correlation r > 0.5 between contamination exposure and inflation residuals; (2) minimum detectable effect size of 3% inflation at 10% contamination; (3) higher effect magnitude for exact-match vs. generation benchmarks."*

**Core Claim:** Contamination-performance correlation is quantifiable and follows predictable patterns.

**Mechanism:** Progressive memorization during training encodes benchmark-relevant content proportionally to exposure frequency, inflating scores beyond capability-predicted levels.

**Predictions:**
- P1: r > 0.5 correlation between exposure and inflation (primary)
- P2: Effect size ≥3% at 10% contamination
- P3: Exact-match benchmarks show higher inflation than generation benchmarks

**Scope:** Pythia models on The Pile, checkpoints spanning training curve.

**Null Hypothesis:** There is no significant correlation (r < 0.2) between n-gram contamination exposure and benchmark score inflation after capability detrending.

**Novelty:** Closes the contamination pipeline (detection → quantification → impact modeling) by providing the first empirically-validated transfer function.

**Extensions (Future Work):**
- Cross-family transfer validation
- Behavioral contamination estimation
- Contamination-adjusted leaderboard

**Key Points:**
- Consolidated hypothesis with scope, mechanism, predictions
- Effect size bounds ensure meaningful findings
- Null hypothesis specified for falsification
- Future work clearly separated from core claims

---

### Exchange 16

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is much stronger now. One final stress test before I'm satisfied.

**Remaining concern: Capability detrending validity.** The two-stage approach (perplexity → predicted score → residual) assumes perplexity is an uncontaminated capability measure. But what if The Pile validation set overlaps with benchmarks conceptually? Then perplexity would correlate with contamination, and detrending would remove the signal we're trying to measure.

**Mitigation:** Use perplexity on clearly OOD text—perhaps a held-out domain The Pile doesn't cover (e.g., recent 2024 news, code in languages not in Pile). This ensures capability is measured on uncontaminated content.

**Second concern: Checkpoint selection bias.** If we sample "interesting" checkpoints (those showing inflation), we bias the correlation. The sampling should be predetermined (e.g., every 10% of training) without peeking at results.

**Third concern: Multiple comparisons.** Testing on MMLU, ARC, HellaSwag, WinoGrande—four benchmarks, plus per-subject MMLU (57)—is ~60 tests. At α=0.05, we'd expect 3 false positives. Pre-register primary outcome (one benchmark, aggregate correlation) and treat others as exploratory.

If these are addressed:
1. OOD perplexity for capability detrending
2. Predetermined checkpoint sampling
3. Pre-registered primary analysis

...then I'm convinced. The hypothesis is falsifiable, the methodology is rigorous, and the scope is appropriate.

**Key Points:**
- Use OOD perplexity (not Pile validation) for uncontaminated capability measure
- Predetermined checkpoint sampling (no selection bias)
- Pre-register primary outcome to control false positives
- With these mitigations: hypothesis is ready

---

### Exchange 17

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex's final concerns are valid and addressable. Let me formalize the experimental protocol with these mitigations.

**Experimental Protocol (Pre-Registered):**

**Primary Outcome:** Spearman correlation (r) between cumulative 13-gram benchmark overlap and MMLU score inflation residual, aggregated across Pythia-410M to Pythia-12B.

**Sampling:** 12 checkpoints per model size, at 0%, 10%, 20%, ..., 100% of training + final checkpoint. No peeking—selection is predetermined.

**Capability Detrending:**
- Compute perplexity on WikiText-103 (separate corpus, OOD relative to Pile domains)
- Fit linear regression: MMLU_score ~ perplexity across all checkpoints
- Inflation residual = observed_score - predicted_score

**Contamination Measurement:**
- 13-gram overlap between Pile tokens seen by checkpoint and MMLU test set
- Use lm-eval-harness decontamination scripts for standardization

**Statistical Analysis:**
- Primary: Spearman r with 95% CI, hypothesis: r > 0.2 (one-tailed, α=0.05)
- Secondary: Benchmark comparison (exact-match vs. generation)
- Exploratory: Per-subject MMLU, cross-model-size consistency

**Falsification Criteria:**
- r < 0.2 and 95% CI upper bound < 0.35 → hypothesis rejected
- Effect size at 10% contamination < 1% → practical significance rejected

This protocol is pre-registerable on OSF. The methodology is transparent, reproducible, and robust to the concerns raised.

**Key Points:**
- Pre-registered primary outcome: Spearman r on MMLU inflation residuals
- WikiText-103 perplexity for OOD capability detrending
- Predetermined checkpoint sampling (0%, 10%, ..., 100%)
- Clear falsification criteria for statistical and practical significance

---

### Exchange 18

🎯 **Dr. Sage** (Research Impact Evaluator):

This is publication-ready methodology. Let me confirm the significance case is complete.

**Contribution Summary:**

1. **Methodological:** First pre-registered experimental protocol for contamination-performance transfer function derivation
2. **Empirical:** Quantitative validation on Pythia family with effect size estimates
3. **Practical:** Enables contamination-adjusted benchmark reporting
4. **Theoretical:** Distinguishes progressive memorization from convergence-dependent effects

**Positioning:** This work completes the contamination detection pipeline:
- Detection: LLMSanitize, MIMIR (existing)
- Quantification: Kernel Divergence Score (Choi et al., 2025)
- **Impact Modeling: Our transfer function (this work)**
- Mitigation: TED (Dong et al., 2024)

**Venue Fit:** NeurIPS/ICML main conference or Datasets & Benchmarks track. The methodology and public artifacts (transfer function, calibration code) align with reproducibility standards.

**Potential Limitations to Acknowledge:**
- Single model family (Pythia) limits generalizability claims
- 13-gram overlap may miss semantic contamination
- Transfer function may need recalibration for different architectures

These are honest limitations that don't undermine the core contribution—they define scope appropriately.

**Key Points:**
- Four-fold contribution: methodological, empirical, practical, theoretical
- Clear pipeline positioning relative to prior work
- Venue-appropriate scope and reproducibility focus
- Honest limitations strengthen rather than weaken the paper

---

### Exchange 19

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

All concerns have been addressed. Let me synthesize the final, converged hypothesis ready for Phase 2B.

**EMERGED HYPOTHESIS SUMMARY**

### Core Statement
Under the condition of language models trained on documented corpora with measurable n-gram overlap, if we increase cumulative benchmark-relevant exposure during training, then benchmark scores will show positive inflation residuals after capability detrending, because progressive memorization encodes benchmark content proportionally to exposure frequency.

### Causal Mechanism
1. During training, models encounter benchmark-relevant content as part of the training corpus
2. Repeated exposure to n-gram sequences matching benchmark items leads to memorization
3. At inference time, memorized content enables higher scores independent of true capability
4. This inflation is proportional to exposure frequency (not binary contamination)

### Variables
- **Independent:** Cumulative 13-gram benchmark overlap at each training checkpoint (continuous, 0-100%)
- **Dependent (Primary):** Benchmark score inflation residual (observed - capability-predicted score)
- **Controlled:** Model architecture (within Pythia family), benchmark suite, evaluation protocol

### Key Assumptions
- A1: 13-gram overlap is a valid proxy for benchmark content memorization
- A2: WikiText-103 perplexity is uncontaminated and measures true capability
- A3: Pythia training checkpoints provide sufficient contamination gradient
- A4: Memorization effect is proportional, not threshold-based (testable)

### Null Hypothesis
There is no significant correlation (Spearman r < 0.2, 95% CI upper < 0.35) between n-gram contamination exposure and benchmark score inflation after capability detrending.

### Predictions
- **P1 (Primary):** Spearman r > 0.5 correlation between exposure and MMLU inflation residuals
- **P2:** Effect size ≥3% inflation at 10% contamination level
- **P3:** Exact-match benchmarks (ARC) show higher inflation than generation benchmarks (HellaSwag)

### Novelty
First empirically-validated transfer function linking contamination intensity to performance inflation, completing the contamination detection pipeline (detection → quantification → impact → mitigation).

### Scope & Boundaries
- **Applies to:** Open-weight models with documented training corpora, specifically Pythia on The Pile
- **Does not apply to:** Proprietary models (unverified), semantic-only contamination
- **Known limitations:** Single model family, 13-gram measure may miss paraphrased contamination

### Experimental Setup
- **Dataset:** The Pile (training corpus), MMLU/ARC/HellaSwag/WinoGrande (benchmarks)
- **Model:** Pythia family (410M to 12B), 12 checkpoints per size
- **Baselines:** Capability-predicted scores via WikiText-103 perplexity detrending

### Related Work & Baselines
- Sainz et al. (2023): Contamination detection without performance correlation
- Dong et al. (2024): TED mitigation without inflation quantification
- Choi et al. (2025): Kernel Divergence for contamination quantification

### Phase 2B Readiness Seeds
- **H-E1 (Existence):** Contamination-inflation correlation exists (r > 0.2)
- **H-M (Mechanism):** Progressive memorization causes proportional inflation
- **H-C (Conditions):** Verbatim contamination required, semantic may differ

### Established Facts
- Test contamination exists in major benchmarks (BUILD_ON: Sainz et al.)
- N-gram overlap detection is feasible (BUILD_ON: lm-eval-harness)
- MIA signals correlate with membership (BUILD_ON: MIMIR)
- **PROVE_NEW:** Contamination-to-inflation transfer function

**Key Points:**
- Complete hypothesis structure ready for Phase 2B
- All components (mechanism, predictions, scope) explicitly defined
- Established vs. new claims clearly separated
- Experimental protocol pre-registerable

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The paradigm shift from binary contamination detection to continuous contamination-inflation transfer functions is genuinely novel. The checkpoint-gradient approach and OOD capability detrending are creative methodological innovations. This opens a new research direction in benchmark calibration.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously testable with clear falsification criteria (r < 0.2, effect size < 1%). The pre-registered experimental protocol with predetermined checkpoint sampling eliminates selection bias. Statistical power is adequate given 12 checkpoints × 6 model sizes.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Completes a critical gap in the contamination pipeline. Practical impact is immediate—enabling calibrated benchmark scores. The methodology contribution generalizes beyond the specific Pythia validation. This is publishable at NeurIPS/ICML.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All required components exist: documented training corpus (The Pile), checkpoint availability (Pythia), evaluation tools (lm-eval-harness), overlap computation (overlapy). Compute requirements (~120 eval runs) are tractable. No fundamental technical barriers.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The panel has converged on a hypothesis that establishes the first quantitative model for contamination-performance correlation in language models. The core claim—that cumulative n-gram exposure correlates positively with benchmark score inflation—is testable via the Pythia checkpoint analysis with capability detrending using WikiText-103 perplexity.

The methodology contribution is the primary novelty: a pre-registerable protocol for deriving contamination-inflation transfer functions that can be applied to any model family with documented training data. The expected finding (r > 0.5 correlation, ≥3% inflation at 10% contamination) would enable practical benchmark calibration.

Key experimental design elements: predetermined checkpoint sampling (0%, 10%, ..., 100%), OOD capability detrending, per-benchmark analysis distinguishing exact-match from generation tasks. The scope is appropriately bounded to Pythia/Pile while the methodology generalizes.

This hypothesis is ready for Phase 2B verification protocol development.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Cross-family generalizability unverified—transfer function may be Pythia-specific
- **Concern 2:** Semantic contamination unmeasured—13-gram captures verbatim only
- **Mitigation Strategy:** Frame generalizability as future work; acknowledge semantic limitation explicitly; design follow-up studies for cross-family validation

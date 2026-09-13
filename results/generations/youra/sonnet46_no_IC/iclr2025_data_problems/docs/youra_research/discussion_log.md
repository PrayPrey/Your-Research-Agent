# Phase 2A Discussion Log
# Architecture: Self-Play Loop (Claude-only, IC-ablation)
# Gap: Gap 1 — Causal Attribution of Curation Choices to Benchmark Outcomes Is Unestablished

**Date:** 2026-08-04
**Execution Mode:** UNATTENDED
**Gap ID:** gap-1
**Gap Title:** Causal Attribution of Curation Choices to Benchmark Outcomes Is Unestablished

---

## Briefing

### Research Gap
**Gap 1:** Individual curation methods (ProX, SoftDedup, REWIRE, WebOrganizer, CoLoR-Filter, DataMan) each demonstrate isolated downstream improvements on their own axis of curation variation, but no study jointly controls for model size, architecture, and training compute budget while varying exactly one curation dimension at a time. Pythia and OLMo provide the controlled platforms but have not been used for this multi-axis ablation.

**Missing Piece:** A controlled ablation framework that: (a) fixes model architecture and parameter count (e.g., Pythia-1B or OLMo-1B), (b) fixes training token budget, (c) varies exactly one curation dimension per run (perplexity threshold OR dedup aggressiveness OR domain ratio), and (d) evaluates on standard benchmarks (GLUE, MMLU, HellaSwag) — producing a causal attribution of benchmark differences specifically to data composition.

### Available Evidence
- **P1 (ProX):** +2% benchmark improvement from programmatic refinement; no scale ablation; no causal isolation
- **P2 (DataMan):** PPL/ICL misalignment — perplexity proxy does not reliably predict downstream ICL performance
- **P3 (Scalable Ablation Approx):** Modular training + merging approximates full ablation at 10x lower compute; PPL of merged model correlates r=0.81 with benchmark
- **P4 (REWIRE):** +1.0–2.5pp from recycling discarded data; single scale only; no causal isolation
- **P5 (WebOrganizer):** Domain mixing orthogonal to quality filtering; super-additive combination; single scale (1B)

### Feasibility Constraints (Pipeline-Enforced)
- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data or future follow-up data
- Reject ideas requiring human evaluation, annotation, or subjective scoring
- Accept only hypotheses testable immediately using existing real datasets and existing benchmarks

### Available Platforms
- Pythia suite: 154 checkpoints per model, same data order, multiple scales (70M–12B)
- OLMo/Dolma: fully open training data + model weights
- NeMo-Curator: production-grade filtering/dedup pipeline
- Standard benchmarks: MMLU, HellaSwag, ARC-C, WinoGrande, PIQA (all existing)

---

## Previous Failure / Routing Context

*No previous failure context. This is the first Phase 2A execution for this research question.*

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this backwards? Every paper we have — ProX, REWIRE, WebOrganizer, DataMan — varies ONE thing and measures a benchmark delta. But they're all doing it at ONE scale, with ONE architecture, often on ONE corpus. The scientific question that nobody has actually answered is: does the SAME curation decision produce DIFFERENT causal effects at different scales? And does it matter whether you apply filtering before or after deduplication?

Here's what excites me: the Pythia suite gives us 154 checkpoints across 70M to 12B parameters, ALL trained on the same Pile data in the same order. That means we can reconstruct what the UNFILTERED baseline looks like at every scale. Now imagine we take DOLMA (which is fully open), apply systematic curation variations — three perplexity thresholds, two dedup aggressiveness levels, three domain ratios — and train matched Pythia-style models. We get a 3×2×3=18 cell factorial design at each scale. For the first time, we can actually ask: does perplexity filtering cause benchmark improvement, and does that causal effect scale with model size?

The novelty here is not just "controlled ablation" — we've seen DataComp do this for vision. The novelty is the **factorial × scale interaction**: does the optimal curation configuration depend on model scale? If yes, that's a paradigm shift for how practitioners think about data pipelines — you can't just find the "best" curation strategy once; you need scale-dependent recipes.

I'm also intrigued by what DataMan found: PPL/ICL misalignment [Peng et al., 2025]. That finding alone suggests the causal mechanism we're after is not "low PPL data → good model" but something more subtle — perhaps token-level difficulty distribution, or domain diversity, or the interaction between the two. A factorial design would naturally surface these interactions.

**Key Points:**
- Factorial design (perplexity × dedup × domain) at multiple model scales using Pythia/Dolma
- Scale × curation interaction as primary novel finding: does optimal curation depend on model size?
- PPL/ICL misalignment (DataMan) motivates moving beyond perplexity as the single axis

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises exciting possibilities, but let me immediately stress-test the experimental design before we get carried away. A 3×2×3=18 cell factorial at multiple scales sounds comprehensive, but it hides several critical threats to causal validity.

First, the confound of **token budget non-equivalence**. If you filter aggressively (remove 60% of Dolma) and train on the remaining 40% to the same token budget, you're either: (a) repeating data (multiple epochs on filtered data — confounds quality with repetition effects), or (b) training on fewer tokens than the unfiltered baseline (confounds quality with data quantity). This is not a minor technical issue — it fundamentally undermines causal attribution. Every paper in Phase 1 that claims a curation benefit has this problem. REWIRE [Nguyen et al., 2025] sidesteps it by recycling discarded data (keeping quantity fixed), but ProX [Zhou et al., 2024] does not.

Second, **benchmark contamination as a confound**. The Spiesberger et al. (2026) finding that 78% of CodeForces problems are semantically contaminated in OLMo3 training data is alarming. Different curation strategies will have different contamination rates on MMLU, HellaSwag, and ARC-C. If aggressive perplexity filtering happens to remove more contaminated examples, we'll see a benchmark delta that is NOT causal — it's contamination correction masquerading as quality improvement. This completely breaks the causal attribution claim.

Third, **what would disprove the hypothesis?** I need concrete falsification criteria. If we claim "perplexity filtering causally improves MMLU scores," then we need to specify: what null distribution do we test against? A permutation test where we relabel curation conditions? A bootstrap confidence interval on the benchmark delta? The hypothesis needs a specific statistical test with a pre-specified significance threshold.

For the Pythia approach specifically: Pythia was trained on The Pile (which has its own quality filtering applied). Using Pythia checkpoints as the "unfiltered baseline" is misleading — you're comparing against an already-filtered baseline. The ground truth unfiltered baseline requires retraining from scratch on raw Dolma.

**Key Points:**
- Token budget non-equivalence: filtering reduces data quantity, confounding quality with quantity
- Contamination as unmeasured confounder: different curation strategies affect contamination rate differently
- Pythia is NOT an unfiltered baseline — it was already trained on filtered Pile data
- Need explicit falsification criteria and statistical tests before design is scientifically sound

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises critical methodological concerns, but I want to pull back and ask the "who cares" question before we get lost in design details. Let me be direct about what this research needs to achieve to matter.

The field is currently in a regime where every major lab has proprietary curation pipelines (web-scale, internally tuned) and open-source practitioners cargo-cult from whatever the latest best corpus is (FineWeb, Dolma, DCLM). The question "does curation causally affect benchmark performance, independent of scale?" matters for VERY different reasons depending on which audience we're writing for:

For **practitioners**: they want prescriptive guidance — "use PPL threshold X with dedup aggressiveness Y for a 1B model." A causal framework helps because it says which knob to turn. But this guidance is only useful if it generalizes across corpora, and a study on Dolma may not generalize to C4 or FineWeb.

For **theorists**: the question is whether there's a principled theory connecting data distribution properties (KL divergence from reference, diversity, redundancy) to downstream capabilities. This is what DataComp for vision tried to do, and it remains open for language.

The finding that would genuinely reshape the field is: **scale-dependent optimal curation**. If you can demonstrate that the optimal perplexity threshold shifts monotonically with model scale (e.g., smaller models benefit more from aggressive quality filtering; larger models benefit more from diverse but noisier data), then you've produced a Chinchilla-style scaling law for data quality. That's a result worth a top-venue paper.

Importantly — and this is my concern with Dr. Nova's proposal — the factorial design produces 18+ conditions. Which interaction terms matter? Without a theoretical prior, the factorial becomes a fishing expedition. The result that would be most impactful is NOT a comprehensive table of 18 ablation results, but a **single clean interaction effect** with a mechanistic interpretation: "at scale N, optimal PPL threshold is approximately $f(N)$" where $f$ has a interpretable functional form.

I'd push the team to sharpen the hypothesis into a single falsifiable scaling relationship between model scale and optimal curation aggressiveness, rather than a comprehensive (but uninterpretable) factorial.

**Key Points:**
- The most impactful finding: scale-dependent optimal curation (Chinchilla-style scaling law for data quality)
- Factorial design risks becoming a fishing expedition without theoretical prior for interaction terms
- Target finding: single clean interaction effect — optimal PPL threshold as monotonic function of model scale
- Generalizability across corpora (Dolma vs. FineWeb vs. C4) is a separate validity threat

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

I want to ground this discussion in what is actually technically possible using existing resources, and I see both promising opportunities and a fundamental constraint that hasn't been named yet.

The core technical feasibility question: can we run enough training runs to populate a meaningful ablation table using existing open infrastructure? Let me be concrete. Training a 1B parameter model on 100B tokens requires roughly 2×10^20 FLOPs. With NeMo-Curator, preparing each curation variant of Dolma takes ~2-4 hours on a 8-GPU machine. Training each model variant: ~48–72 hours on 8×A100s. An 18-cell factorial at 1B scale alone requires ~18 × 72h = 1,296 GPU-hours (at 8 GPUs each = 10,368 A100-hours). At multiple scales (70M, 160M, 1B, 7B from Pythia), this quickly becomes 40,000+ A100-hours.

BUT — and this is the critical technical insight — Prof. Vera's concern about Pythia as the baseline is actually an opportunity. Pythia provides **intermediate checkpoints** (every 512 steps, 154 total per model). We don't need to retrain from scratch. We can: (1) use the Scalable Data Ablation Approximation method [Na et al., 2024] to approximate multi-condition ablations via modular training and parameter merging at much lower compute; (2) use Pythia checkpoints as curriculum analysis reference (not as direct comparison baseline, which Prof. Vera correctly flags as problematic); (3) focus on the 70M and 160M Pythia scales for full training runs, where the compute is tractable (70M at 100B tokens ≈ 140M A100-hours total across all cells).

Here's what's technically possible immediately with existing resources: train a **2×3×2 = 12-cell ablation** at 70M and 160M scale on Dolma subsets, using NeMo-Curator for pipeline construction, measuring MMLU (4-shot), HellaSwag (0-shot), ARC-C (0-shot) from the lm-evaluation-harness. The 2 axes with clearest technical operationalization: (a) perplexity threshold (PPL < 20 vs. PPL < 50, using GPT-2 as reference) and (b) dedup aggressiveness (exact+MinHash at 0.7 vs. 0.9 Jaccard threshold). Domain mixing as third axis if compute allows.

The technical soundness issue Prof. Vera raised about token budget is real but solvable: fix the pre-training token count to the FILTERED corpus size of the MOST aggressive filter, and sample (with replacement, one epoch) from less-filtered corpora to match that budget. This controls quantity while varying quality.

**Key Points:**
- Full factorial at multiple scales is compute-prohibitive; focus on 70M and 160M for tractability
- Na et al. (2024) approximation method enables scalable extrapolation to larger model sizes
- Token budget problem is solvable: fix to most-filtered-corpus size, sample with replacement
- Immediate technical path: 2×3×2=12 cells at 70M/160M on Dolma with NeMo-Curator + lm-eval-harness

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — now we have the critical building blocks. Let me synthesize what's emerged and propose a specific, strengthened hypothesis that addresses the concerns from Prof. Vera and Prof. Pax while capturing Dr. Sage's insight about scale-dependent optimal curation.

The core synthesis: the PPL/ICL misalignment finding from DataMan [Peng et al., 2025] is not just a negative result — it's a MECHANISTIC clue. If perplexity filtering at a fixed threshold doesn't reliably predict downstream ICL performance, then the missing variable is likely the **interaction between filtering aggressiveness and the model's effective learning capacity** (i.e., model scale). Smaller models have lower capacity and benefit from cleaner, more predictable data distributions (aggressive filtering). Larger models can extract signal from noisier but more diverse data (lighter filtering). This is not a new idea in principle — it echoes Curriculum Learning theory — but it has never been measured on existing open-weight models across scales with controlled ablation.

Here's the strengthened hypothesis:

> **H1 (Scale-Curation Interaction):** Under fixed architecture family and token budget, the optimal perplexity-based filtering aggressiveness (measured by downstream MMLU + HellaSwag scores) scales monotonically with model parameter count — specifically, the performance-maximizing PPL threshold $\tau^*(N)$ is an increasing function of model scale $N$ (larger models tolerate and benefit from higher-PPL data). This produces a measurable interaction effect in a 2-way ANOVA on model size × PPL threshold, with a specific prediction: models at 70M prefer $\tau < 30$ while models at 1B prefer $\tau > 50$.

To address Prof. Vera's contamination concern: we use existing n-gram contamination detection (lm-sys/llm-decontaminator) on the Dolma subsets against MMLU/HellaSwag training sets, and measure contamination rate per filtering condition as a covariate. This doesn't require new benchmarks — just running an existing tool on existing datasets.

To address Prof. Pax's compute concern: the 2-scale (70M, 160M) design is tractable. We use Na et al.'s approximation for scale extrapolation to 1B as a validation step (not primary result).

To address Prof. Vera's token budget concern: the proposed solution (fix to most-filtered size, sample with replacement from less-filtered) is standard and defensible.

**Key Points:**
- Hypothesis: optimal PPL threshold $\tau^*(N)$ is an increasing function of model scale $N$
- Test: 2-way ANOVA on scale × PPL threshold using MMLU + HellaSwag on existing benchmarks
- Contamination controlled as measured covariate using existing tools (no new benchmarks needed)
- Immediately testable: 70M and 160M models on Dolma, existing benchmarks, existing tools

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is the strongest proposal so far, but let me be rigorous about where it breaks down — because I see at least three places where reviewers will reject this paper if we don't address them now.

**Break Point 1: The monotonicity claim is theoretically unjustified.** "Optimal PPL threshold is an increasing function of model scale" is stated as if it follows from first principles, but there's no theory supporting monotonicity specifically. The DataMan PPL/ICL misalignment [Peng et al., 2025] shows the relationship is non-monotonic even within a single scale — peak performance at moderate PPL threshold, not at minimum. Why would this non-monotonic within-scale relationship become monotonic across scales? This needs a mechanistic justification, or the hypothesis should be weakened from "monotonically increasing" to "significantly different across scales" (which is measurable without claiming directionality).

**Break Point 2: Sampling with replacement to equalize token budgets is not equivalent to training on the original distribution.** When you sample from the less-filtered corpus with replacement to match the filtered corpus token count, you're artificially increasing the repetition of the less-filtered subset. This is known to cause training instability and memorization artifacts at small model sizes. The confound Prof. Vera identified is not fully resolved by this approach — it's substituted with a different confound (repetition vs. quality). The clean solution is to use the same raw corpus and vary only the filter, accepting that filtered datasets are smaller — then control for tokens seen (not tokens in corpus) during evaluation.

**Break Point 3: Dolma as the sole corpus limits generalizability.** If we show the interaction effect on Dolma, a reviewer will immediately ask: "does this hold for FineWeb? For C4? For The Pile?" Without replication across at least 2 corpora, the result could be Dolma-specific. The good news: FineWeb is also fully open with documented filtering pipeline, and we can apply the same perplexity re-filtering at different thresholds to FineWeb subsets. This should be part of the experimental design.

**What would convince me?** Show the scale × PPL interaction effect in 2-way ANOVA with p < 0.05 on at least two corpora (Dolma + FineWeb), with contamination rate included as a covariate and showing the interaction persists after contamination adjustment. That's a falsifiable, publishable claim.

**Key Points:**
- Monotonicity claim needs mechanistic justification or weakening to "significantly different across scales"
- Sampling-with-replacement token equalization introduces repetition confound — use tokens-seen control instead
- Single corpus (Dolma) limits generalizability — add FineWeb as replication corpus
- Falsification criterion: 2-way ANOVA interaction p < 0.05 on two corpora with contamination covariate

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are exactly the kind of stress-test we needed. Let me respond with what I think is the MOST exciting refinement — and it actually makes the hypothesis stronger, not weaker.

On the monotonicity issue: Prof. Rex is right that "monotonically increasing" is unjustified. BUT the DataMan finding gives us the right theoretical frame. DataMan shows that at a single scale (1B), optimal performance occurs at a MODERATE PPL threshold, not at minimum. This is consistent with a "diversity-quality trade-off" model: you need both signal quality AND distributional diversity. Smaller models have lower capacity to handle distribution diversity, so they need higher quality signal (tighter PPL filter). Larger models can exploit diversity better. The prediction is NOT monotonic filtering aggressiveness — it's that the **optimal PPL threshold follows a scale-dependent diversity-quality Pareto frontier**.

This is actually measurable with existing benchmarks! Here's the refined prediction structure:
- **P1:** At 70M scale, the optimal PPL threshold is in [20, 35]; at 1B scale, it is in [45, 65] (directional prediction without requiring strict monotonicity)
- **P2:** The variance in benchmark scores across PPL threshold conditions is HIGHER at small scales (70M) than at large scales (1B) — because small models are more sensitive to data quality variation
- **P3:** Deduplication aggressiveness shows the OPPOSITE scale interaction — more aggressive dedup hurts large models more than small models (because large models benefit from semantic repetition patterns that dedup removes)

P2 and P3 are completely novel. P3 especially — nobody has tested whether deduplication effects scale differently from quality effects. The WebOrganizer [Wettig et al., 2025] finding that domain mixing is orthogonal to quality filtering actually predicts P3 is testable independently: hold domain mixing constant, vary dedup, observe scale interaction.

This reframing also dissolves the corpus generalizability concern partially: if we're testing a MECHANISM (diversity-quality trade-off at different capacities), the prediction should generalize across corpora by design, and we can test generalizability as an additional experiment.

**Key Points:**
- Reframe from monotonicity to "scale-dependent diversity-quality Pareto frontier" (mechanistically motivated)
- P2: Benchmark variance across PPL conditions is higher at small vs. large scales (novel, testable)
- P3: Deduplication scale interaction is OPPOSITE to PPL scale interaction — orthogonal axes have different scale dependencies
- Mechanism generalizes across corpora by design, making Dolma+FineWeb replication a confirmation rather than a prerequisite

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's P2 and P3 predictions are genuinely testable and add important structure to the hypothesis. Let me now specify the exact statistical tests needed to make this publishable, because the hypothesis is getting richer and we need to make sure each prediction has a clean test.

**For P1 (optimal PPL threshold shifts with scale):**
For each scale s ∈ {70M, 160M} and each PPL threshold τ ∈ {20, 35, 50, 65}, record the average benchmark score $B(s, τ)$ on MMLU + HellaSwag (average of the two). Test: 2-way mixed ANOVA with factors Scale (between) and PPL-threshold (within), testing the interaction term F_{Scale×PPL}. Prediction: significant interaction (p < 0.05) with pattern of means showing lower optimal τ at 70M than at 160M. Pre-register the directional prediction: $\tau^*(70M) < \tau^*(160M)$.

**For P2 (benchmark variance is higher at small scale):**
Compute within-scale variance of B(s, τ) across the τ conditions, separately for each scale. Test: Levene's test for equality of variance between s=70M and s=160M conditions. Prediction: Var(B(70M, τ)) > Var(B(160M, τ)), p < 0.05. This is a one-tailed test — pre-register directionality.

**For P3 (dedup scale interaction opposite to PPL):**
For each scale and each dedup aggressiveness level d ∈ {strict (MinHash Jaccard 0.7), loose (0.9)}, record B(s, d). Test: 2-way ANOVA interaction Scale × Dedup. Prediction: at 70M, strict dedup improves over loose; at 160M or larger, strict dedup does NOT improve or hurts — i.e., the sign of (B(s, strict) - B(s, loose)) changes between scales.

**Contamination control (for all three):** Run lm-sys/llm-decontaminator on each Dolma subset (one per condition), compute contamination rate CR(condition) against MMLU and HellaSwag test sets. Include CR as a covariate in all ANOVAs via ANCOVA. If the interaction effect disappears after contamination adjustment, the result is invalid.

This gives us three pre-registered tests, each with a specific statistical method, significance threshold, and directional prediction. That's what reviewers need.

**Key Points:**
- P1: 2-way mixed ANOVA (Scale × PPL-threshold), pre-registered directional prediction $\tau^*(70M) < \tau^*(160M)$
- P2: Levene's test on within-scale variance across PPL conditions
- P3: 2-way ANOVA (Scale × Dedup), pre-registered sign change prediction across scales
- Contamination as ANCOVA covariate across all three tests — result must survive adjustment

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This is now approaching a genuinely significant research contribution. Let me assess what we have and what's missing for top-venue impact.

We now have a **3-prediction hypothesis with pre-specified statistical tests**. The finding that would make this high-impact: if P3 (dedup scale interaction opposite to PPL) holds, it's genuinely novel and practically significant. It would mean that practitioners using aggressive deduplication (which is essentially universal now — everyone uses MinHash near-dedup) may be actively HURTING their large models while helping their small ones. This is a practically disruptive finding — it challenges the "dedup always helps" folk wisdom that has been operationalized in every major curation pipeline since 2021.

What's still missing for top-venue publication:

1. **Mechanistic story for P3:** Why would deduplication hurt large models more? A plausible story: large models use high-frequency token patterns for in-context learning (ICL) — near-duplicate documents encode these patterns. Aggressive dedup removes them, reducing ICL capability disproportionately at large scale. SoftDedup [He et al., 2024] (from Phase 1) already hints at this: their reweighting approach (+1.77% few-shot) works precisely because it doesn't fully discard near-duplicates but down-weights them. We can cite SoftDedup as both supporting evidence and a methodological contrast.

2. **Effect size pre-specification:** "Significant at p < 0.05" is not enough for ICML/NeurIPS reviewers in 2026. We should pre-specify minimum effect size: the scale interaction should explain at least 15% of benchmark variance (partial η² ≥ 0.15) to be practically meaningful, not just statistically detectable.

3. **What negative results teach us:** If P1 holds but P3 doesn't, that's still publishable — it clarifies that perplexity filtering is scale-dependent but dedup is scale-invariant. We should frame the paper around "we measured scale-dependence of three curation axes" and let the data tell which axes matter.

The significance: this is the first systematic causal measurement of scale × curation interactions using controlled experiments on fully open pre-training platforms. Even if only one of the three predictions holds, that's a clean contribution.

**Key Points:**
- P3 (dedup hurts large models) is the highest-impact novel finding if confirmed — challenges universal dedup practice
- SoftDedup [He et al., 2024] provides supportive mechanistic evidence (reweighting > hard dedup for few-shot)
- Pre-specify effect size: partial η² ≥ 0.15 for practical significance, not just p < 0.05
- Negative results are publishable: "scale-invariant vs. scale-dependent curation axes" is itself a clean finding

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me validate the technical soundness of P3's proposed mechanism and the contamination covariate approach, because both have potential failure points that need to be addressed before we commit to this design.

**On P3's mechanism (dedup removes ICL-relevant patterns):**
The claim is that near-duplicate documents encode token patterns used for ICL, and their removal hurts large models more. This is technically plausible but has a key assumption: that ICL ability is driven by high-frequency pattern repetition in pre-training data, which is supported by Xie et al. (2022)'s Bayesian ICL theory. However, the operationalization of "near-duplicate" at Jaccard 0.7 vs. 0.9 may not be the right axis. MinHash at Jaccard 0.7 removes roughly 15–20% of web data; at 0.9 it removes ~5–8%. The documents removed at 0.7 but not at 0.9 are "soft duplicates" — similar but not identical texts covering the same topics, events, or facts. These ARE likely to contain the pattern repetition relevant to ICL. So the mechanism is technically coherent.

**On contamination detection as ANCOVA covariate:**
Running lm-sys/llm-decontaminator on each filtered Dolma subset is technically feasible — the tool exists, it's open-source, and it outputs contamination rates. But there's a technical subtlety: different filtering conditions produce different SUBSETS of Dolma, not different total corpus sizes of a common corpus. The contamination rate of the MMLU questions in each subset will vary not just because filtering removes contaminated samples, but because it changes which documents are present. This means CR(condition) is not an independent covariate — it's a function of the same filtering decision that determines the training data. Including it as a covariate in ANCOVA is methodologically appropriate but will be challenged by reviewers. The defense: we're controlling for a known confounder (contamination), which is correct scientific practice even if the covariate is correlated with the treatment.

**Technical path confirmation:**
70M model on 30B tokens: ~4.2×10^18 FLOPs ≈ 3–4 hours on 4×A100s per run. 12-cell design (2 scales × 3 PPL thresholds × 2 dedup levels) = 24 runs × 4 hours = 96 A100-hours. Fully tractable with academic compute access. NeMo-Curator pipeline preparation: ~30 minutes per condition. This is technically feasible within a standard research compute budget.

**Key Points:**
- P3 mechanism (dedup removes ICL patterns) is technically coherent, consistent with Bayesian ICL theory
- Contamination as ANCOVA covariate is methodologically sound but requires clear reviewer defense
- 12-cell design at 2 small scales: 96 A100-hours total — tractable with academic compute
- MinHash Jaccard 0.7 vs 0.9 is the right operationalization: covers the soft-duplicate range relevant to ICL

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We now have a solid, multi-prediction hypothesis with statistical tests, mechanistic grounding, and a tractable experimental plan. Let me consolidate the full hypothesis statement and address the remaining open gaps identified by Prof. Rex and Prof. Vera.

**Consolidated Hypothesis (H-CurationScale-v1):**

> **Under** fixed model architecture (Pythia family) trained on subsets of Dolma (and FineWeb as replication) with fixed tokens-seen budget,
> **If** we independently vary: (a) perplexity filtering threshold τ ∈ {20, 35, 50} using GPT-2 reference, and (b) deduplication aggressiveness d ∈ {strict: MinHash J=0.7, loose: MinHash J=0.9},
> **Then** we observe: (P1) downstream benchmark scores (MMLU 4-shot + HellaSwag 0-shot) peak at lower τ for 70M models than for 160M models; (P2) benchmark variance across τ conditions is higher at 70M than 160M; (P3) the sign of (B(strict) - B(loose)) is positive at 70M and non-positive at 160M,
> **Because** smaller models lack sufficient capacity to extract signal from high-diversity, noisier data (explaining P1 and P2), while larger models leverage near-duplicate frequency patterns for ICL (explaining P3 — dedup removes these patterns disproportionately hurting large models).

**On Prof. Rex's token budget concern:** Fix tokens-seen = 30B for all conditions (not tokens in corpus). For conditions where the filtered corpus < 30B tokens, train with multiple epochs, but record epoch count as a metadata variable and check for epoch-training instability markers (training loss variance). If instability occurs, fall back to the MINIMUM tokens-seen achievable under all conditions (which is the most-aggressively filtered corpus size) — this is Prof. Rex's preferred approach and eliminates the repetition confound entirely.

**On FineWeb replication:** Include FineWeb Edu-scored subsets as a second corpus. FineWeb has documented quality scores and deduplication steps, so we can construct analogous τ and d conditions directly from its existing metadata without re-running full filtering — reducing FineWeb replication compute by ~60%.

**On effect size:** Pre-specify partial η² ≥ 0.15 as practical significance threshold (per Dr. Sage's recommendation).

**Key Points:**
- Full consolidated hypothesis: H-CurationScale-v1 with Under-If-Then-Because structure
- Token budget solved: fix tokens-seen (not tokens in corpus), record epochs, check instability
- FineWeb replication is computationally efficient (uses existing metadata scores)
- Effect size pre-specified: partial η² ≥ 0.15

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally has done excellent synthesis work. The hypothesis is now well-structured. Let me run one final stress-test pass on the remaining weaknesses, then I'll indicate what would satisfy my concerns.

**Remaining weakness 1: Epoch-based token matching at small scales.**
Using multiple epochs to equalize tokens-seen is problematic at exactly the model sizes we're studying (70M, 160M). These are small models that memorize quickly. Running 2+ epochs on a filtered 15B-token corpus when training a 70M model is known to cause grokking-like behavior and distribution collapse (training loss decreases but eval loss plateaus or increases). This means our "quality benefit" at aggressive filtering could be partially a MEMORIZATION artifact at small scale, which would confound the scale interaction precisely where we most need it to be clean. The fix: if filtered corpus < 30B tokens, don't equalize — instead, use the actual corpus size and control for it statistically as a covariate (tokens-seen as covariate in ANCOVA, alongside contamination rate). This way we're not introducing the repetition artifact.

**Remaining weakness 2: Pythia family vs. training from scratch.**
We keep referencing "Pythia family" but the proposed plan is to train NEW models from scratch on Dolma subsets (not to use existing Pythia checkpoints). That's fine and correct — but then "Pythia family" should be specified as "Pythia-architecture models trained from scratch on filtered Dolma subsets." Using actual EleutherAI Pythia checkpoints (trained on Pile) as baselines is NOT valid for causal comparison.

**Remaining weakness 3: Do we have a null hypothesis specified for P3?**
The prediction is "sign of (B(strict) - B(loose)) changes between scales." The null: "no sign change — dedup benefit is scale-invariant." This is tested by the ANOVA interaction term (Scale × Dedup). But we should also specify: what if we observe no significant effect at either scale individually (i.e., both 70M and 160M show no dedup benefit)? That would mean dedup is universally neutral — a different finding from a sign change. Pre-specify: we need at least one scale to show a significant main effect of dedup (p < 0.05) for the sign-change prediction to be a valid test.

**What would convince me:** The above three refinements addressed in the experimental protocol, and the 2-corpus replication (Dolma + FineWeb) built into the design from the start.

**Key Points:**
- Multiple epochs at 70M scale risks memorization artifacts — use actual corpus size + tokens-seen as ANCOVA covariate instead
- Clarify "Pythia-architecture" means training from scratch, not using existing Pythia checkpoints
- Pre-specify null for P3: at least one scale must show significant dedup main effect for sign-change test to be valid

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has sharpened the design significantly. I want to add one more creative angle that I think elevates the novelty further and actually RESOLVES the epoch/memorization issue.

What if we reframe the study not as "fixed tokens-seen ablation" but as a **data efficiency study**? The question becomes: at what training token budget $T$ does each curation configuration achieve its maximum benchmark performance, and how does this budget-to-peak relationship depend on scale?

This reframing is powerful for three reasons: (1) It sidesteps the token equalization problem entirely — each model trains until its benchmark score plateaus (early stopping criterion based on validation loss on a clean held-out set), so every model uses its optimal budget, not an artificial fixed budget. (2) It opens a NEW testable prediction: aggressive filtering not only affects PEAK benchmark score but also **training efficiency** — fewer tokens-to-peak. If aggressive filtering at small scale requires 15B tokens to reach peak vs. 25B for loose filtering, that's a practically significant finding about data efficiency. (3) It connects naturally to Chinchilla scaling laws — we're essentially measuring the "data quality" correction to Chinchilla's optimal tokens-per-parameter ratio.

The new P4 prediction: **Aggressive perplexity filtering (τ=20) reduces tokens-to-peak at 70M scale but NOT at 160M scale** — large models need more diverse data and reach peak only with more tokens, even if those tokens are noisier.

This makes the hypothesis richer: not just "optimal configuration differs by scale" but "data efficiency curve shape differs by scale." And it's testable immediately: train each configuration to 50B tokens (well past expected peak for small models), record benchmark score at each checkpoint (every 5B tokens), fit a learning curve, extract tokens-to-95%-of-asymptote as the efficiency measure.

The checkpoint-based evaluation uses EXISTING lm-evaluation-harness evaluations — no new benchmarks needed.

**Key Points:**
- Reframe as "data efficiency study" — tokens-to-peak as primary outcome, not just final benchmark score
- Eliminates epoch/token equalization problem by using early-stopping (tokens-to-peak) per condition
- P4: Aggressive filtering reduces tokens-to-peak at 70M but not at 160M (novel efficiency × scale interaction)
- Learning curve analysis from training checkpoints — existing tools, no new infrastructure needed

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's data efficiency reframing is scientifically attractive and I want to formalize it, but I also need to flag one methodological subtlety that could undermine it.

**On tokens-to-peak operationalization:**
"Train until benchmark score plateaus" is ambiguous without specification. Benchmark evaluation is noisy — MMLU 4-shot on a 70M model has high variance due to the small model's sensitivity to prompt formatting. If we evaluate every 5B tokens, we need to distinguish true asymptote from noise-induced plateau. The correct operationalization: fit a log-linear learning curve $B(T) = A - C \cdot e^{-\lambda T}$ to each model's checkpoint benchmark scores, extract the asymptote $A$ and the efficiency constant $\lambda$, then define tokens-to-95%-of-$A$ = $\log(20C/0.05A) / \lambda$ analytically. This requires at least 5–6 checkpoint evaluations per training run to fit the curve reliably. At every 5B tokens out of 50B total, that's 10 evaluations per run — feasible.

**The methodological subtlety:** tokens-to-peak depends critically on what benchmark you use. MMLU (knowledge-heavy) and HellaSwag (reasoning-heavy) likely show DIFFERENT learning curve shapes. If aggressive filtering accelerates MMLU convergence but not HellaSwag, we have a task-type interaction layered on top of the scale interaction. This is actually a MORE interesting finding, but it requires analyzing both benchmarks separately rather than averaging them. I recommend reporting curves separately for MMLU and HellaSwag.

**Full statistical test plan for P4:**
For each corpus (Dolma, FineWeb), scale s ∈ {70M, 160M}, filtering condition (τ, d), fit the log-linear curve and extract $\lambda(s, τ, d)$ (larger $\lambda$ = faster convergence = higher efficiency). Test: 2-way ANOVA on $\lambda$ with factors Scale × PPL-threshold, testing whether $\lambda$ is higher at τ=20 for 70M than for 160M (interaction term). Pre-register: the interaction sign for $\lambda$ should be negative (τ=20 helps efficiency at 70M more than 160M).

**What would disprove P4:** Finding $\lambda$ is scale-invariant (no interaction) or that the interaction goes in the opposite direction (large models benefit MORE from aggressive filtering in terms of efficiency).

**Key Points:**
- Operationalize tokens-to-peak via log-linear learning curve fit: extract $\lambda$ analytically from checkpoint evals
- Analyze MMLU and HellaSwag separately — task-type × scale × filtering 3-way interaction is possible
- P4 falsification: $\lambda$ is scale-invariant or large models show higher $\lambda$ gain from aggressive filtering
- 10 checkpoint evaluations per run (every 5B out of 50B) — feasible with lm-evaluation-harness

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

We've now reached a research design that I assess as genuinely field-shaping. Let me do the final significance assessment.

**What we have:** A hypothesis (H-CurationScale-v1) with four pre-registered predictions (P1–P4) about scale × curation interactions in pre-training data quality filtering, testable immediately using:
- Existing corpora (Dolma, FineWeb) — no new data collection
- Existing benchmarks (MMLU, HellaSwag) — no new evaluation frameworks
- Existing tools (NeMo-Curator, lm-eval-harness, lm-sys/llm-decontaminator) — no new software
- Existing architectures (Pythia-style, trained from scratch) — tractable compute

**Why this matters:**
1. **For practitioners:** If P1 and P3 hold, the field's standard practice (aggressive dedup + moderate PPL filtering applied uniformly regardless of target model size) is suboptimal. The result would be the first empirically grounded data curation recipe that is scale-aware.
2. **For theorists:** The log-linear learning curve analysis (P4) connects data quality to Chinchilla-style scaling theory. A $\lambda(s, τ)$ function that has a principled form (e.g., $\lambda \propto s^{-\alpha} \tau^{-\beta}$) would be the first data-quality scaling law.
3. **For the evaluation community:** The contamination covariate analysis contributes to understanding how curation affects benchmark integrity — relevant to Gap 3 which we deprioritized but partially address as a byproduct.

**Venue targeting:** ICML 2027 or NeurIPS 2026. The controlled experiment framing + pre-registered predictions + learning curve analysis gives it a strong empirical paper profile. Top venues have been receptive to "scaling law discovery" papers (Chinchilla, DataComp). This fits that mold.

**Remaining risks (for Prof. Rex to confirm manageable):**
- Training instability at small scale under repeated epochs — addressed by tokens-to-peak framing
- Single architecture family (Pythia-style) — limitation, but acceptable for a first controlled study
- FineWeb replication may show different results — if so, the interaction is corpus-specific (limits generalizability, acceptable as a finding)

**Key Points:**
- H-CurationScale-v1 is scientifically significant, practically impactful, and testable immediately
- Scale-aware curation recipe: first empirically grounded prescription that varies by model size
- P4 learning curve analysis creates potential for first data-quality scaling law ($\lambda$ as function of scale and filtering)
- Target: ICML 2027 / NeurIPS 2026 — fits "scaling law discovery" empirical paper profile

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Creative Novelty Explorer):
- **Verdict:** STRONG
- **Assessment:** The hypothesis evolved from a straightforward factorial ablation into a genuinely novel scale × curation interaction study. The data efficiency reframing (tokens-to-peak as outcome) and P3's counterintuitive prediction (dedup hurts large models) are the kinds of findings that reshape community practice. Cross-domain connection to Chinchilla scaling laws gives the work theoretical anchoring beyond pure empiricism.

🔬 **Prof. Vera** (Rigorous Validation Architect):
- **Verdict:** STRONG
- **Assessment:** After extensive stress-testing, the hypothesis has pre-specified statistical tests (2-way ANOVA for P1, Levene's test for P2, ANOVA sign-change for P3, efficiency curve ANOVA for P4), explicit contamination control via ANCOVA, and pre-specified effect sizes (partial η² ≥ 0.15). The log-linear learning curve operationalization for P4 is methodologically sound. The token-budget problem is resolved by the tokens-to-peak framing. Minor remaining risk: benchmark noise at 70M scale in MMLU, mitigated by separating MMLU and HellaSwag analysis.

🎯 **Dr. Sage** (Research Impact Evaluator):
- **Verdict:** STRONG
- **Assessment:** The research contribution is clearly positioned: first controlled measurement of scale × curation interaction effects using fully open pre-training platforms. If P3 (dedup hurts large models) holds, it challenges universal dedup practice — a practically disruptive finding. The learning curve analysis creates potential for the first data-quality scaling law. ICML 2027 / NeurIPS 2026 target is realistic.

⚙️ **Prof. Pax** (Feasibility & Reality Checker):
- **Verdict:** STRONG
- **Assessment:** The 12-cell design at 70M and 160M scale (24 training runs × ~4 hours each = ~96 A100-hours) is tractable with academic compute. NeMo-Curator corpus preparation is well-documented. lm-evaluation-harness provides all benchmark evaluations. lm-sys/llm-decontaminator handles contamination measurement. The entire experimental pipeline uses existing, battle-tested open-source tools. The tokens-to-peak reframing is technically sound and avoids the memorization artifact risk.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion — H-CurationScale-v1 — addresses the foundational measurement gap in pre-training data curation research. The core claim is that the optimal pre-training data curation configuration (specifically, perplexity filtering threshold and deduplication aggressiveness) is not universal but scale-dependent: smaller models (70M) require more aggressive quality filtering and benefit from aggressive deduplication, while larger models (160M+) tolerate higher-diversity, noisier data and are harmed by aggressive deduplication that removes near-duplicate patterns important for in-context learning.

The hypothesis is tested through a controlled 2×3×2 factorial experiment on two open corpora (Dolma, FineWeb) using Pythia-architecture models trained from scratch, with four pre-registered predictions: P1 (optimal PPL threshold higher at larger scale), P2 (benchmark variance higher at smaller scale), P3 (dedup sign change across scales), and P4 (aggressive filtering improves data efficiency only at small scale). All predictions are tested on existing benchmarks (MMLU, HellaSwag) using existing tools, with contamination controlled as an ANCOVA covariate.

The practical significance: if confirmed, this provides the first scale-aware curation recipe for foundation model pre-training, and the learning curve analysis offers a path to a data-quality scaling law analogous to Chinchilla's compute-optimal recipe. The experimental design is immediately executable with academic compute resources and fully open infrastructure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Benchmark noise at 70M scale: MMLU 4-shot on a 70M model has high variance — mitigate by increasing few-shot examples (use 5-shot) and averaging over 3 evaluation seeds
- Single architecture family (Pythia-style) limits generalizability — acknowledge as limitation; replicate on OLMo-architecture if compute allows
- FineWeb replication may diverge from Dolma results — if P3 does not replicate, report as corpus-specific finding rather than universal claim
- **Mitigation Strategy:** Pre-register all predictions on OSF before running experiments; include corpus-specificity as a pre-specified secondary hypothesis; run 3 independent training seeds per condition for variance estimation

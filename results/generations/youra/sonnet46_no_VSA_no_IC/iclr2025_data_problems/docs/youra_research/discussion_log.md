# Phase 2A Discussion Log
**Gap:** Gap 1 — No Systematic Per-Filter × Per-Benchmark Correlation Analysis on Existing Checkpoints
**Date:** 2026-08-20
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Execution Mode:** UNATTENDED

---

## Briefing Context

### Research Gap
**Gap ID:** gap-1
**Title:** No Systematic Per-Filter × Per-Benchmark Correlation Analysis on Existing Checkpoints

**Description:** DCLM benchmarks filtering holistically across 53 tasks but does not provide filter-by-filter × benchmark-by-benchmark correlation. Pythia provides controlled checkpoints but does not vary individual filter choices. Ultra-FineWeb and FineWeb2 demonstrate aggregate pipeline improvements without isolating which filter stage drives which benchmark gain.

**Missing Piece:** A systematic study holding model architecture/size/training fixed and ablating individual filter choices (deduplication threshold, perplexity cutoff, quality classifier threshold, heuristic aggressiveness) independently, measuring correlation with each of MMLU, HellaSwag, ARC, WinoGrande separately.

### Available Infrastructure
- Pythia suite: 16 LLMs (70M-12B), 154 checkpoints each, exact dataloaders
- DCLM evaluation suite: 53 tasks including MMLU, HellaSwag, ARC, WinoGrande
- The Pile: 800GB, 22 domains, exact composition known
- Pythia-dedup variant: single deduplication ablation data point
- CoLoR-Filter: shows task-conditioned filtering achieves 11-25x data efficiency
- Open filter implementations: FineWeb2, TxT360, lm-evaluation-harness

### Reference Papers (Available Summaries)
- P1: DCLM (2406.11794) — holistic filtering benchmark, 53-task eval
- P2: Pythia (2304.01373) — controlled checkpoints, exact dataloaders
- P3: CoLoR-Filter (2406.10670) — task-conditioned filtering, 11-25x efficiency

### Previous Failure / Routing Context
None — first Phase 2A execution.

### Feasibility Constraints (Mandatory)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The Pythia suite is an extraordinary gift to this research question — 154 training checkpoints per model, exact dataloaders that reconstruct which tokens each checkpoint saw. Nobody has used this to build a *filter sensitivity map*: a matrix where rows are individual filter operations (dedup threshold, perplexity cutoff, quality classifier confidence, heuristic aggressiveness like line-length and symbol ratio filters) and columns are specific benchmarks (MMLU, HellaSwag, ARC-Challenge, ARC-Easy, WinoGrande). The cell values would be Spearman correlations between filter intensity and benchmark score across Pythia's training trajectory.

Here's what excites me about this framing: CoLoR-Filter [Brandfonbrener et al., 2024] already showed that filtering conditioned on *specific tasks* achieves 11-25x data efficiency versus undifferentiated quality filtering. That result implies task-specific signal exists in the data. My hypothesis: the filter sensitivity map will reveal that different filter types selectively amplify different capability classes. Perplexity-based quality filters might correlate strongly with MMLU knowledge retrieval but weakly with WinoGrande commonsense. Near-deduplication thresholds might correlate most with HellaSwag's sensitivity to repetitive web patterns.

Two unconventional angles to explore:
1. **Cross-checkpoint trajectory analysis**: Instead of training new models, correlate the *rate of change* of filter-relevant statistics across Pythia's 154 checkpoints with the *rate of change* of each benchmark score. This gives us a causal signal direction without new training runs.
2. **Filter fingerprinting**: Each filter leaves a characteristic "fingerprint" on the data distribution (domain proportions, vocabulary diversity, sentence length distribution). We can cluster Pythia's intermediate checkpoints by data fingerprint and measure which fingerprint clusters produce which benchmark profiles.
3. **Contamination interaction**: Before attributing benchmark score variance to filters, we need a contamination control — the lm-sys/llm-decontaminator can flag which Pile documents overlap with MMLU/HellaSwag test sets, letting us partial out contamination effects from genuine filter effects.

**Key Points:**
- Pythia's 154 checkpoints × 16 scales = massive observational study without new training
- Filter sensitivity matrix is the missing artifact that bridges DCLM's aggregate results and CoLoR-Filter's task-specific insights
- Contamination audit (Gap 3 from Phase 1) is a prerequisite for clean attribution in Gap 1

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises compelling infrastructure arguments, but I want to tighten the falsifiability before we commit to a hypothesis. There's a critical confound lurking: Pythia's 154 checkpoints represent *time points along a single training run*, not independent filter ablations. Correlating filter statistics with benchmark performance across training steps is NOT the same as ablating individual filters — it's correlating two time series that both have strong temporal autocorrelation. Any finding would be severely confounded by training dynamics (learning rate schedule, gradient norm, data order effects).

The clean falsifiable design requires independent filter conditions, not trajectory correlations. Fortunately, Pythia gives us one legitimate comparison: Pythia vs Pythia-dedup (same architecture, same data except deduplication). That's a single filter ablation with high statistical validity. We could extend this logic: if we treat different Pythia model sizes as probing different data-quality sensitivity thresholds (larger models are known to be more resilient to noise [Ziegler et al., 2022]), then the scale × filter interaction becomes measurable using existing checkpoints.

For a properly falsifiable hypothesis, I propose: **"Deduplication threshold has a differential effect on commonsense benchmarks (HellaSwag, WinoGrande) versus knowledge benchmarks (MMLU, ARC) in Pythia-scale models, with commonsense benchmarks showing greater sensitivity at higher dedup aggressiveness."** This is:
- Testable with existing data: Pythia vs Pythia-dedup on lm-evaluation-harness
- Directional: specifies *which* benchmarks are more sensitive
- Falsifiable: if MMLU and HellaSwag show identical sensitivity profiles, the hypothesis is wrong
- Not requiring new data: pure reanalysis of existing Pythia evaluation results plus the dedup variant

The contamination audit Dr. Nova mentioned is essential here — if The Pile has significant MMLU overlap, what looks like "filter sensitivity" might be contamination removal sensitivity. We need to disentangle these.

**Key Points:**
- Pythia training trajectory analysis confounds time-series autocorrelation with filter effects
- Pythia vs Pythia-dedup is the cleanest existing ablation; additional filter variants need new training
- Falsifiable direction: commonsense benchmarks should be more sensitive to dedup than knowledge benchmarks
- Contamination control is not optional — it's part of the experimental design

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This discussion is productive but I want to zoom out and ask: what would the *research community actually do* with this finding? Prof. Vera's tightened hypothesis (dedup differential effect on commonsense vs knowledge benchmarks) is scientifically clean, but it addresses only one filter type on one filter dimension. The field needs a broader map.

Let me assess the two-track structure emerging here:

**Track A (High feasibility, narrow scope):** Reanalyze existing Pythia + Pythia-dedup + publicly released evaluation results. Use lm-evaluation-harness to re-run standardized evaluation if numbers aren't directly comparable. The differential effect of deduplication across benchmark categories is answerable in days to weeks with zero new training. Impact: solid methodological contribution, citable infrastructure paper.

**Track B (Moderate feasibility, high impact):** Use Pythia's exact dataloaders to construct *post-hoc filter groups* — partition The Pile into "would survive filter X" vs "would not survive filter X" for several filter types, then measure which *training subset* most predicts each benchmark's performance curve. This is data attribution, not ablation — it uses influence function approximations or DataModels [Ilyas et al., 2022] methodology applied to Pythia checkpoints. Impact: first systematic data attribution map for pre-training benchmarks.

Track B is where the real novelty is. [Ilyas et al., 2022] showed DataModels can identify training examples that causally affect model behavior. Applied to Pythia (which has exact dataloaders), we could identify which Pile documents most influence MMLU vs HellaSwag performance. That tells us not just "which filter" but "which data patterns" — connecting filter operations to their downstream effects through a causal lens.

The significance question: a filter sensitivity map that the entire LLM training community can consult when designing data pipelines — that's a high-citation, high-reuse artifact. This fills a gap that every practitioner faces when choosing filter hyperparameters.

**Key Points:**
- Two tracks: (A) pure reanalysis of existing Pythia evals, (B) post-hoc data attribution using Pythia dataloaders
- Track B (data attribution via DataModels on Pythia) offers highest impact
- The artifact (filter sensitivity map) is a community resource, not just a paper result
- Influence function / DataModels approach exists and has been validated — no new methodology needed

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

I need to ground this discussion in computational reality. DataModels [Ilyas et al., 2022] requires training thousands of subsampled models to compute data attribution — completely infeasible here without massive compute. Influence functions require Hessian-vector products at the scale of Pythia models (70M-12B parameters), which is tractable only for the smallest models and approximated poorly at scale. Track B as Dr. Sage described it is NOT feasible using existing open infrastructure within a reasonable research timeline.

Let me define what IS feasible right now:

**Feasible with existing resources:**
1. Pythia vs Pythia-dedup comparison using lm-evaluation-harness — fully automated, days of compute on a single GPU
2. RegMix-style regression: treat Pile domain proportions (known fixed) as "mixing features" and Pythia's published benchmark scores as targets; fit a linear regression to identify which domain correlates with which benchmark. This uses *published numbers only* — zero compute
3. Contamination audit: apply lm-evaluation-harness's 13-gram decontamination to The Pile against MMLU/HellaSwag/ARC test sets. Scalable with standard compute

**The core feasible hypothesis:**
Using Pythia's 16 models × 16 scales and their published evaluation scores, we can construct a domain-mixing regression: `benchmark_score ~ α₁·webtext_fraction + α₂·books_fraction + α₃·github_fraction + α₄·wiki_fraction + ε`. The Pile's exact domain ratios are published [Gao et al., 2020]. The benchmark scores are publicly available. This is a *zero-training* correlation study that can be done in an afternoon.

For filter sensitivity specifically: the only clean ablation is Pythia vs Pythia-dedup. We could *augment* this by including other publicly released model families (OLMo on Dolma, Falcon on RefinedWeb) as natural experiments — each trained with different filter choices on different data — and treat model family as a proxy for filter choice. This is observational, not experimental, but with proper controls it's publishable.

**Key Points:**
- DataModels/influence functions: infeasible at Pythia scale
- Zero-training regression on published Pile domain proportions + Pythia scores: fully feasible
- Cross-model-family comparison (Pythia/OLMo/Falcon) as natural experiment for filter effects
- Contamination audit: feasible, should run first

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion has productively converged on what's feasible. Let me synthesize and strengthen a concrete, testable hypothesis that satisfies all constraints.

**Proposed Hypothesis (Strengthened):**
*"Domain composition of pre-training data is the primary driver of benchmark-specific performance variation across model families and scales, and this effect is quantifiable using a linear regression model applied to publicly available domain proportions and benchmark scores — without any new training."*

Concretely: Using The Pile's published domain proportions (22 domains, exact percentages known for Pythia), Dolma's domain breakdown (for OLMo), and RefinedWeb's composition (for Falcon), combined with their publicly reported MMLU/HellaSwag/ARC/WinoGrande scores, we fit a domain→benchmark regression. The hypothesis predicts:
- Wikipedia proportion → positive coefficient on MMLU (knowledge)
- Books proportion → positive coefficient on HellaSwag/WinoGrande (commonsense narrative)  
- GitHub/code proportion → positive on ARC-Challenge (systematic reasoning)
- High-quality-filtered web proportion → broadly positive but weaker per-benchmark signal

This is strengthened by:
1. **Scale robustness test**: fit the regression separately for small (70M-400M) vs large (1B-12B) Pythia models — if domain sensitivities change with scale, we have the AutoScale finding; if stable, we have a robust causal claim
2. **Contamination partial-out**: run 13-gram decontamination first; adjust benchmark scores; check if regression coefficients change significantly
3. **Dedup effect isolation**: Pythia-dedup vs Pythia as a falsification — if deduplication changes domain proportions (it shouldn't, but might via domain-correlated duplication rates), it would confound the domain regression

The null hypothesis is clear: β_domain = 0 for all domains across all benchmarks (domain composition has no predictive power for individual benchmark scores after controlling for model scale).

**Key Points:**
- Fully feasible: uses only published numbers + lm-evaluation-harness reruns
- Novel: no prior study has performed this domain→benchmark regression across multiple model families
- Falsifiable: linear regression with testable coefficients
- Contamination control built in as a mandatory pre-step

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is more tractable than the earlier proposals, but it has four critical vulnerabilities I need to stress-test:

**Vulnerability 1 — Confounded by training corpus SIZE, not composition:**
Pythia's family has fixed composition (The Pile) and varies scale. OLMo uses Dolma with different composition AND different training token counts. You can't partial out corpus size from composition in a cross-family regression — these are not independent variables. A regression across model families will absorb size effects into composition coefficients.

*Mitigation:* Restrict analysis to *within-Pythia* only (fixed composition, only scale varies) for the domain regression. For cross-family comparison, include log(training_tokens) as a covariate. The hypothesis should be reframed as: "within a single model family with fixed domain composition, domain proportions predict benchmark profile; and the predicted profile differs significantly from a uniform composition baseline."

**Vulnerability 2 — The Pile has only ONE composition (no domain variation within Pythia):**
Dr. Ally's regression requires domain variation as the independent variable. Within Pythia, domain proportions are fixed — there's zero within-family domain variation to regress on. The regression as described only works cross-family, which has the confound above.

*Mitigation:* Use Pythia's checkpoint trajectory as a proxy for composition variation: early checkpoints have seen proportionally more of whichever domain appears first in the data ordering. If we can identify the data ordering from exact dataloaders, we get temporal domain exposure as a continuous variable. This is non-trivial but feasible with Pythia's open dataloaders.

**Vulnerability 3 — n=3 families is underpowered:**
A regression with 22 domain predictors and 3 data points (model families) is wildly underpowered. Any finding would be spurious.

*Mitigation:* Include many more model families: Falcon, RedPajama-INCITE, MPT-7B, Bloom, LLaMA-1, etc. Many have published compositions and benchmark scores. With n=15-20 model families, the regression becomes meaningful.

**Vulnerability 4 — Benchmark score comparability across model families:**
Published scores use different evaluation harnesses, prompting strategies, and shot counts. MMLU 5-shot in one paper ≠ MMLU 5-shot in another.

*Mitigation:* Re-run all models through a single standardized harness (lm-evaluation-harness v0.4) under identical conditions. This is compute-intensive but feasible for small model variants.

**Sharpened Feasible Hypothesis:** Using data ordering from Pythia's exact dataloaders to estimate temporal domain exposure at each of 154 checkpoints, and Pythia's standardized lm-evaluation-harness scores at each checkpoint, fit a domain exposure → benchmark score regression within a single family. This eliminates cross-family confounds and uses a legitimate source of domain variation.

**Key Points:**
- Cross-family domain regression is severely underpowered and confounded
- Pythia's exact dataloaders enable within-family domain exposure estimation via data ordering
- Re-running all comparisons through a single harness version is required for validity
- n=15-20 model families with published compositions is feasible if we include more families

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's stress-test is exactly right and I want to embrace it. The pivot Prof. Rex suggests — using Pythia's exact dataloader ordering to derive temporal domain exposure — is actually MORE novel than the cross-family regression. Nobody has done this, and it's uniquely enabled by Pythia's open infrastructure.

Here's the refined hypothesis frame: Pythia's exact dataloaders give us the *sequence* in which training tokens were consumed. We can compute, at each of 154 checkpoints, "what fraction of tokens seen so far came from Wikipedia, Books, WebText2, etc." This creates a continuous domain-exposure trajectory for each model size. Combined with the benchmark scores at each checkpoint (already measured in the Pythia paper), we have a legitimate panel dataset:

- **Observations:** 154 checkpoints × 16 model sizes = 2,464 data points
- **Independent variables:** cumulative domain fraction at each checkpoint (22 domains)
- **Dependent variables:** MMLU, HellaSwag, ARC-Challenge, ARC-Easy, WinoGrande scores
- **Model:** panel regression with model-size fixed effects

This is a genuine natural experiment — the domain proportions *do* vary across checkpoint time (because the data ordering is not uniform — different domains appear with different densities at different points in training). The panel structure controls for model-size confounds via fixed effects.

**The core novel claim:** The marginal effect of cumulative Wikipedia exposure on MMLU score (controlling for Books, GitHub, WebText2 exposure and model size) is significantly larger than its effect on WinoGrande — establishing that knowledge-domain exposure specifically drives knowledge benchmark performance.

This is testable in 1-2 weeks: download Pythia dataloaders (open), compute cumulative domain fractions at each checkpoint (compute: light), re-run benchmark evaluation at key checkpoints if needed (lm-evaluation-harness already has Pythia integration), run panel regression (minutes).

**Key Points:**
- Pythia temporal domain exposure via exact dataloaders creates a legitimate panel dataset (2,464 points)
- Panel regression with model-size fixed effects eliminates Prof. Rex's confound
- Core claim: Wikipedia exposure → MMLU more than WinoGrande; Books exposure → HellaSwag/WinoGrande more than MMLU
- Feasibility: 1-2 weeks, existing compute, zero new training

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's panel regression framework is the most scientifically rigorous proposal so far, and I want to specify the exact falsification criteria.

**Experimental Design (Falsifiable):**

Step 1 — Contamination Pre-Check:
Run lm-evaluation-harness 13-gram decontamination on The Pile vs MMLU/HellaSwag/ARC/WinoGrande test sets. Document contamination rates. If contamination rate > 5% for any benchmark, apply contamination-adjusted scores before regression.

Step 2 — Domain Exposure Trajectory:
Using Pythia's exact dataloaders, compute at each of 154 checkpoints:
`exposure_d(t) = tokens_from_domain_d_by_step_t / total_tokens_by_step_t`
This yields a 154 × 22 matrix of domain fractions for each model size.

Step 3 — Panel Regression:
`benchmark_score(i,t) = α_i + Σ_d β_d × exposure_d(t) + γ × log(model_params_i) + ε`
where i = model size, t = checkpoint step, d = domain.

**Falsification criteria:**
- H0: All β_d = 0 (domain composition has no predictive power for benchmark scores)
- H1_specific: β_Wikipedia > β_WebText2 for MMLU (knowledge domain drives knowledge benchmark)
- H1_specific: β_Books > β_Wikipedia for HellaSwag (narrative domain drives commonsense)
- H1_null: if β_Wikipedia ≈ β_Books for both MMLU and HellaSwag, the domain-specificity claim fails

**Success criterion:** At least 2 of 4 benchmarks show significantly different domain coefficient profiles (p < 0.05 after FDR correction), with directionally consistent ordering matching the domain-capability hypothesis.

This is immediately executable using open tools — Pythia's dataloaders are on HuggingFace, lm-evaluation-harness is pip-installable, The Pile is on HuggingFace, domain labels are in The Pile metadata.

**Key Points:**
- Exact falsification: β_Wikipedia > β_WebText2 for MMLU; β_Books > β_Wikipedia for HellaSwag
- Contamination correction is a pre-step, not a separate paper
- Panel dataset: 2,464 observations with model-size fixed effects
- Success criterion: 2/4 benchmarks show significantly different domain profiles

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis has crystallized into something highly publishable. Let me assess the impact ceiling and identify the key narrative.

**Impact Assessment:**

This study would be the first to use Pythia's exact dataloader ordering to construct a panel dataset of domain exposure → benchmark performance, with a clean panel regression design. That's a methodological contribution that other researchers can immediately replicate on other model families.

The key findings the community would act on:
1. **Which benchmarks are domain-sensitive?** If MMLU is highly sensitive to Wikipedia exposure but HellaSwag is not, practitioners know to increase Wikipedia fraction when their target is knowledge tasks
2. **Scale interaction:** If β coefficients change sign or magnitude across model sizes, that's the AutoScale finding replicated and extended to individual benchmarks
3. **Contamination effect size:** How much do contamination-adjusted scores change the regression? If the coefficients are robust, it validates the Pile's use for attribution; if they flip, it's a major methodological finding

**Positioning vs prior work:**
- DCLM: benchmarks filters holistically → we provide per-domain granularity within a fixed filter pipeline
- Pythia paper: shows checkpoints exist but doesn't exploit domain ordering → we exploit it
- RegMix/DoReMi/AutoScale: optimize mixing for aggregate performance → we map mixing to individual benchmarks

**Publication pathway:** NeurIPS Datasets & Benchmarks track, ICML, or a specialized data workshop. The infrastructure reuse angle (Pythia + lm-eval-harness + The Pile metadata) makes it accessible and verifiable.

**Key Points:**
- First panel dataset of domain exposure → individual benchmark performance
- Directly actionable: tells practitioners which domain to upweight for which capability
- Scale interaction finding (if present) extends AutoScale to benchmark-specific analysis
- Clear positioning vs DCLM, Pythia, RegMix as a bridge study

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility verification before we finalize:

**Step-by-step compute estimate:**

1. Pythia dataloader domain labeling: The Pile has per-document domain metadata. Pythia's dataloaders expose the token ordering. Extracting cumulative domain fractions at 154 checkpoints: ~2-4 hours of preprocessing on a single machine. Fully feasible.

2. Benchmark re-evaluation: Pythia's lm-evaluation-harness integration already exists. Re-running 5 benchmarks × 16 models × 154 checkpoints is expensive if done exhaustively, but:
   - Published scores exist for key checkpoints (steps 1k, 10k, 50k, 100k, 143k) in the Pythia paper
   - We only need full 154-checkpoint coverage for 2-3 model sizes to establish the trajectory shape
   - Estimated: 50-100 GPU-hours on A100, feasible on a university cluster or Vast.ai

3. Contamination audit: lm-evaluation-harness 13-gram decontamination on The Pile (~800GB) vs 4 benchmark test sets (~10k examples total). Elasticsearch or n-gram index. Estimated: 4-8 hours compute.

4. Panel regression: OLS with fixed effects in statsmodels or R's plm package. Minutes.

**Total estimate:** 2-3 days of compute time (parallelizable), 1-2 weeks of researcher time for implementation and analysis. Cost: ~$100-500 on cloud GPUs if university cluster unavailable.

**Data availability confirmation:**
- Pythia checkpoints: ✅ HuggingFace (EleutherAI/pythia-*)
- The Pile with domain labels: ✅ HuggingFace (EleutherAI/the_pile)
- lm-evaluation-harness: ✅ pip install + GitHub
- Benchmark test sets (MMLU, HellaSwag, ARC, WinoGrande): ✅ all public
- Pythia exact dataloaders: ✅ documented in Pythia paper, available via HuggingFace

**Verdict:** FEASIBLE within 1-2 weeks on standard academic compute. No new data required. No new models required. No human annotation required.

**Key Points:**
- 50-100 GPU-hours for benchmark re-evaluation (subset of checkpoints)
- All data sources publicly available on HuggingFace
- Panel regression: minutes once data is prepared
- Total timeline: 1-2 weeks researcher + compute

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

All convergence criteria are now met. Let me write the final strengthened hypothesis.

**CONVERGED HYPOTHESIS: Domain Exposure-Benchmark Specificity in Pre-trained LLMs**

*Core Claim:* Within a fixed-architecture model family trained on a heterogeneous corpus (Pythia on The Pile), the cumulative domain exposure trajectory — measurable from exact dataloaders — is a significant predictor of individual benchmark performance, with domain-specific effects: Wikipedia exposure predicts MMLU more than HellaSwag; Books exposure predicts HellaSwag/WinoGrande more than MMLU. This domain-benchmark specificity is quantifiable via panel regression across Pythia's 154 checkpoints and 16 model sizes (2,464 observations), controlling for model scale via fixed effects.

*Mechanism:* Different domains contain different distributions of cognitive task patterns. Wikipedia concentrates factual associations, entity relationships, and structured knowledge — the cognitive substrate of MMLU. Books concentrate narrative coherence, causal inference, and world modeling — the substrate of HellaSwag commonsense completion. GitHub concentrates formal reasoning and structured problem-solving — the substrate of ARC-Challenge. As cumulative domain exposure shifts during training, benchmarks tracking each capability class respond proportionally.

*Predictions:*
- P1: β_Wikipedia > β_Books for MMLU (p < 0.05, panel regression)
- P2: β_Books > β_Wikipedia for HellaSwag (p < 0.05, panel regression)
- P3: Domain coefficient profiles differ significantly across at least 2 of 4 benchmarks (FDR-corrected)
- P4 (secondary): Domain-benchmark specificity is consistent across model scales (70M to 12B) — scale modulates magnitude but not direction

*Null Hypothesis:* β_d is identical across all benchmarks for all domains (no domain-benchmark specificity after controlling for scale).

**Key Points:**
- SPECIFIC: domain-benchmark specificity via panel regression
- MECHANISM: domain content → cognitive task pattern alignment
- PREDICTIONS: 4 directional, falsifiable predictions with success criteria
- NOVELTY: first use of Pythia's exact dataloader ordering as domain exposure timeline
- FEASIBILITY: confirmed by Prof. Pax — 1-2 weeks, existing open data

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress-test pass. The hypothesis is substantially stronger than where we started. Remaining concerns:

**Concern 1 — Data ordering non-uniformity assumption:**
The panel regression assumes that domain fractions vary across the 154 checkpoints (providing the variation needed for regression). If The Pile is shuffled uniformly, domain fractions would be *constant* across checkpoints (always reflecting global proportions), giving zero variation and making the regression degenerate.

*Check required:* Verify whether Pythia trained on shuffled or ordered Pile data. If shuffled uniformly, the temporal domain exposure approach collapses and we'd need the cross-family design instead.

**Concern 2 — Fixed effects absorb too much:**
With model-size fixed effects and 16 sizes, we're absorbing most of the variance. The regression may lack power to detect domain effects.

*Mitigation:* Report R² with and without domain variables; if domain variables add meaningful R² over scale-only model, the claim holds.

**Concern 3 — Benchmark floor/ceiling effects:**
Early checkpoints (step 1k) may be near random performance for all benchmarks — domain effects only emerge mid-training.

*Mitigation:* Restrict analysis to checkpoints where at least one benchmark exceeds 30% (well above chance for all included benchmarks).

**Overall verdict:** These are manageable methodological concerns that belong in the limitations section, not dealbreakers. The core design is sound. Recommend proceeding.

**Mitigation Strategy:** (1) First check The Pile data ordering in Pythia dataloaders; if uniform shuffle, pivot to cross-family with n=15+ model families. (2) Report both model with and without domain variables. (3) Apply checkpoint floor filter.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The use of Pythia's exact dataloader ordering to construct a domain exposure trajectory is genuinely novel — no prior work has exploited this infrastructure this way. The panel dataset framing (2,464 observations from 154 checkpoints × 16 scales) provides a methodological template that other model families could adopt. The domain-benchmark specificity framing (Wikipedia → MMLU, Books → HellaSwag) is a falsifiable, memorable claim with direct practical implications.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has concrete directional predictions with specified statistical thresholds (p < 0.05, FDR correction). The null hypothesis is clearly specified. The falsification pathway is unambiguous: if β_Wikipedia ≈ β_Books for MMLU, the specificity claim fails. The contamination pre-step is appropriately integrated. The remaining confound (data ordering uniformity) is identified and has a clear diagnostic check.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The finding directly answers what every LLM data practitioner needs: which domain to upweight for which capability. The infrastructure reuse (Pythia + lm-eval-harness + The Pile) makes it immediately reproducible. Positioning vs DCLM, RegMix, and AutoScale is clear. NeurIPS D&B track or ICML is a realistic venue.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All data sources are publicly available. Compute estimate is 50-100 GPU-hours plus preprocessing — affordable on standard academic infrastructure. Timeline is 1-2 weeks. No new benchmarks, no human annotation, no synthetic data. The contingency (uniform shuffle → cross-family design) is well-defined.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a clean, novel, and immediately executable hypothesis: **domain exposure during pre-training has benchmark-specific effects that are quantifiable via panel regression on Pythia's training trajectory.** Specifically, Wikipedia exposure predicts MMLU performance more than HellaSwag, while Books exposure shows the reverse pattern. This is testable by computing cumulative domain fractions from Pythia's exact dataloaders at each of 154 checkpoints, combining with publicly available benchmark scores, and running a panel regression with model-size fixed effects across 2,464 observations.

The core innovation is methodological: using the *exact dataloader ordering* as a source of domain exposure variation within a controlled model family. This eliminates cross-family confounds (different architectures, different training token counts) that plagued earlier cross-family regression proposals. The contamination audit (13-gram decontamination of The Pile vs benchmark test sets) is a mandatory pre-step that adjusts scores before regression.

The hypothesis is ready for Phase 2B planning. The primary contingency is whether The Pile uses uniform shuffling (which would eliminate within-family domain variation) — this must be verified first; if true, the fallback is a cross-family study with n=15+ model families.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The Pile data ordering may be uniformly shuffled, eliminating within-family domain variation for the panel regression. Verify first.
- Fixed effects may absorb too much variance — report R² decomposition.
- Early checkpoint floor effects may dilute signal — apply 30% performance floor filter.
- **Mitigation Strategy:** Check Pythia dataloader ordering documentation first; if uniform shuffle confirmed, pivot to cross-family regression with n=15+ families (Pythia, OLMo, Falcon, MPT, Bloom, RedPajama-INCITE, LLaMA-1) on standardized lm-eval-harness scores.

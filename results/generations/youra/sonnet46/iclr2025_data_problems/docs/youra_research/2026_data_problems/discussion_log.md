# Phase 2A: Research Hypothesis Discussion
**Gap:** gap-1 — Absence of Controlled Joint Analysis of Curation Hyperparameters on Both Performance and Fairness
**Started:** 2026-03-14
**Execution Mode:** UNATTENDED (Self-Contained Tikitaka Loop v9.0.0)

---

## Briefing

**Research Gap:**
Individual studies ablate filtering thresholds and domain mix ratios for performance (DCLM, FineWeb, DoReMi) OR study fairness in LLM outputs, but no work uses the same curation configurations to measure both performance AND fairness effects simultaneously on the same model checkpoints.

**Key Missing Piece:**
A controlled experiment varying curation hyperparameters (filtering thresholds, deduplication aggressiveness, domain mix ratios) across the same base model family (e.g., Pythia suite) measuring outputs on both performance benchmarks (MMLU, HellaSwag) and fairness benchmarks (BBQ, WinoBias, StereoSet) from identical checkpoints.

**Available Papers (P1-P4):**
- P1: DCLM (Li et al., 2024) — arXiv:2406.11794
- P2: FineWeb (Penedo et al., 2024) — arXiv:2406.17557
- P3: DoReMi (Xie et al., 2023) — arXiv:2305.10429
- P4: Dolma (Soldaini et al., 2024) — arXiv:2402.00159

**Implementation Resources:**
- huggingface/datatrove — modular filter blocks for controlled hyperparameter ablations
- ChenghaoMou/text-dedup — multiple dedup algorithms for threshold experiments

**Feasibility Constraints (MANDATORY):**
- ✅ No new benchmarks or rubrics
- ✅ No synthetic/generated data
- ✅ No human evaluation or annotation
- ✅ Testable immediately with existing real datasets and benchmarks

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the entire framing of "performance vs. fairness" as separate objectives is the wrong lens — and what we actually need is to treat them as a *coupled measurement system* from the very first curation step?

Here's the creative angle that excites me: DCLM [Li et al., 2024] shows that model-based filtering (top-10% fastText classifier scores) pushes MMLU from ~44% to 64% — but nobody measured what that same filter did to the demographic composition of the surviving training corpus, or to BBQ/WinoBias scores on the resulting model. This is not a minor omission — it's a *fundamental measurement gap*. The filter almost certainly removed or retained text unevenly across demographic groups (Wikipedia edits, Reddit discussions, news articles all have known demographic skews), yet we treat the fairness effect as someone else's problem to measure.

What I find genuinely novel here is the possibility of a **Curation Fairness Tradeoff Curve**: analogous to the precision-recall curve in information retrieval, we could trace a 2D frontier where the X-axis is MMLU performance and the Y-axis is an aggregate fairness score (mean BBQ accuracy, WinoBias consistency ratio), as we sweep a single curation hyperparameter — say, the fastText quality percentile cutoff from 5% to 95%. DoReMi [Xie et al., 2023] gives us an even more interesting handle: their domain reweighting mechanism changes *which domains* dominate training. Different domains have wildly different demographic distributions. What if upweighting Wikipedia boosts reasoning performance but systematically skews gender pronoun associations?

The really wild idea: **multi-objective curation optimization**. Instead of just maximizing MMLU (as DCLM does) or perplexity-based domain fitness (as DoReMi does), what if we ran a Pareto-front search over (performance, fairness) jointly — using the Pythia suite's small models (70M, 160M) as fast proxies? We'd need a few controlled hyperparameter axes to sweep: (1) quality percentile cutoff, (2) domain mix ratio for web vs. curated sources, (3) deduplication aggressiveness. Dolma [Soldaini et al., 2024] provides the open corpus infrastructure to make this tractable — it's already componentized for controlled ablations.

**Key Points:**
- DCLM/FineWeb/DoReMi all optimized for performance benchmarks only — a *Curation Fairness Tradeoff Curve* sweeping hyperparameters on the same Pythia checkpoints is genuinely missing from the literature
- The DoReMi domain reweighting mechanism provides a theoretically grounded axis for fairness experiments: different domains have different demographic distributions
- A multi-objective (performance × fairness) Pareto frontier, using small Pythia proxy models for fast ablation, could be a tractable and novel contribution
- Existing infrastructure (Dolma corpus, datatrove pipeline, BBQ/WinoBias benchmarks, Pythia suite) makes this immediately feasible without new resources

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The proposal of a *Curation Fairness Tradeoff Curve* is scientifically promising — but only if we operationalize it with strict definitions and falsifiable predictions. At present, "fairness" and "performance" are still loosely specified. In DCLM, performance is cleanly defined: MMLU 5-shot accuracy under a fixed recipe (decoder-only Transformer, fixed LR 2e-5, batch size 256, up to 4 epochs) [Li et al., 2024]. That level of procedural control is precisely what makes their filtering results interpretable. If we are to add fairness as a second axis, it must be measured under equally controlled conditions: fixed training recipe, fixed token budget, identical architecture, and only a single curation hyperparameter varied at a time. Otherwise, any "Pareto frontier" will be confounded by training dynamics rather than data composition.

The evidence suggests that fastText-based filtering (top 10%) meaningfully shifts MMLU (e.g., up to 64% at 7B with 2.6T tokens) [Li et al., 2024]. Your hypothesis implies that such filtering also shifts demographic representation in measurable ways. This yields a testable prediction: as we sweep percentile cutoffs from 5% to 95%, the demographic token distribution (e.g., gendered pronoun frequency, named entity demographic inference, topic-domain proxies) will change monotonically or at least systematically. What would disprove the coupling hypothesis? If fairness metrics (e.g., BBQ accuracy gaps, WinoBias consistency ratios) remain statistically invariant across large shifts in percentile cutoff — even as MMLU varies substantially — then performance and fairness are not tightly coupled under this mechanism.

However, we must guard against a critical confound: domain–demographic entanglement. DoReMi-style reweighting changes domain proportions, and domains differ in both linguistic register and demographic representation. If fairness changes track domain shifts rather than "quality" per se, then the fastText cutoff is acting as a domain selector, not a fairness mediator. Therefore, each experiment must log: (1) domain composition post-filtering, (2) inferred demographic distribution within each domain, and (3) downstream fairness metrics. A mediation analysis is essential. If fairness shifts disappear after conditioning on domain mix, the causal story changes.

Your proposal to use Pythia 70M/160M as proxies is efficient, but here is the Achilles' heel: fairness metrics are notoriously unstable at small scales. I would require a scale-consistency check. A concrete criterion: the sign of the fairness–performance slope across percentile sweeps must match between 160M and at least one ≥1B model. If the slope inverts at scale, the proxy is invalid. The best experiments are designed to fail; thus, we should explicitly test whether small-model Pareto fronts predict large-model fronts within ±5% MMLU and ±0.02 fairness-gap tolerance.

Finally, precision in prediction is essential. I propose three falsifiable hypotheses:
1. **Monotonic Coupling Hypothesis:** Increasing quality percentile monotonically increases MMLU and monotonically shifts fairness metrics by ≥0.05 effect size.
2. **Domain Mediation Hypothesis:** ≥70% of fairness variance across cutoffs is explained by domain composition changes.
3. **Pareto Non-Dominance Hypothesis:** No single percentile cutoff simultaneously maximizes both MMLU and fairness beyond 1 standard error margins.

If all three fail, the "coupled measurement system" framing is empirically unsupported. If they hold under controlled conditions, then — and only then — does this meet my standards.

**Key Points:**
- Define fairness with the same procedural rigor as MMLU; vary only one curation axis at a time under fixed training recipes [Li et al., 2024].
- Test explicit, falsifiable predictions about monotonic shifts and mediation by domain composition.
- Validate small-model Pareto fronts against larger-scale models to ensure proxy reliability.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I say that constructively. 🔬 Prof. Vera has correctly identified the domain–demographic entanglement confound, but I think we're understating how severe it is. DCLM's methodology [Li et al., 2024] is actually a cautionary tale here: their fastText classifier was trained on English Wikipedia and OpenWebText, meaning the quality filter is *inherently biased toward Wikipedia-style writing*. When you sweep that quality percentile cutoff, you're not varying a neutral "quality dial" — you're varying a *proxy for resemblance to Wikipedia-style English*, which is systematically skewed toward certain educational registers, Western topics, and mainstream demographic perspectives.

The DCLM Discussion & Conclusion acknowledges compute constraints that prevented "thorough exploration of all potential data curation strategies" including multilinguality and safety — but this understates the problem for our purposes. For the hypothesis to be interpretable, we need to know: when BBQ accuracy changes as we vary the quality cutoff, is that because (a) different demographic groups were disproportionately represented in filtered-out text, (b) the retained text has different demographic associations in ways the fastText classifier was never designed to capture, or (c) the model's in-context learning behavior on BBQ simply varies with perplexity levels, not demographic exposure at all? These three mechanisms predict different interventions and different experimental designs.

What would convince me is a causal decomposition experiment, not just a correlation. Specifically: take two DCLM-equivalent configurations with matched MMLU scores but achieved via different routes (quality filtering vs. domain mixing), and measure whether they have statistically indistinguishable BBQ/WinoBias performance. If two paths to the same MMLU yield different fairness scores, then the *path* matters — which is a much stronger claim than just showing a tradeoff curve. If they yield identical fairness scores, then fairness is determined by performance level, not curation mechanism — which falsifies the coupling hypothesis entirely.

There is also a missing assumption that needs to be made explicit: the hypothesis tacitly assumes that BBQ and WinoBias are measuring fairness properties that are *caused* by training data demographics rather than by benchmark artifacts. BBQ has known biases in how it phrases questions, and model answers to BBQ depend heavily on exact phrasings. If a model's BBQ score changes because the quality filter removed certain writing styles that match BBQ's question format, that's not a fairness finding — it's a benchmark confound.

**Key Points:**
- The DCLM quality filter is a Wikipedia-resemblance proxy, not a neutral quality dial — so "sweeping the percentile cutoff" is varying a confounded IV, not a clean one
- We need a causal decomposition: matched-MMLU configurations via different curation routes must show divergent fairness scores to support the coupling hypothesis
- BBQ/WinoBias sensitivity to benchmark artifacts must be explicitly ruled out as a confound before claiming fairness effects are data-driven

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the *Curation Fairness Tradeoff Curve* is technically feasible — but only if we are extremely precise about what mechanism we believe is operating. Right now, there are at least three distinct mechanisms on the table: (1) quality filtering changes demographic token frequencies, (2) quality filtering changes domain mixture, which in turn changes demographic exposure, or (3) fairness benchmarks respond to general language modeling quality rather than demographic representation. These are not interchangeable explanations. If we don't isolate them, the curve will be descriptive but not mechanistic.

From a feasibility standpoint, Dolma gives us the right infrastructure to run this cleanly. Its toolkit already supports filtering, deduplication, and mixing operations in a modular way, with explicit preprocessing steps (language detection, low-quality filtering, toxicity removal, PII removal) and probabilistic deduplication via Bloom filters [Soldaini et al., 2024]. That means we *can* vary a single axis — say, quality score percentile — while holding the training recipe constant. The ablation evidence from OLMo-1B shows filtering interventions measurably shift downstream task accuracy and perplexity [Soldaini et al., 2024]. So in principle, curation-level perturbations propagate to model behavior. There is no physical or mathematical barrier to expecting fairness metrics to move as well.

Here's what worries me: fairness metrics like BBQ and WinoBias are not direct functions of token frequency; they're functions of learned conditional distributions over stereotyped contexts. A monotonic shift in demographic token counts does *not* guarantee a monotonic shift in bias metrics. The learning dynamics are nonlinear under cross-entropy minimization. You can easily construct cases where increasing exposure to a demographic term reduces bias at small scales but increases it at larger scales due to context co-occurrence patterns. So the Monotonic Coupling Hypothesis is plausible but far from guaranteed in principle.

Prof. Rex's matched-MMLU causal decomposition idea is the right stress test. Technically, this is feasible: train two models to matched validation perplexity or matched MMLU within ±1%, one via percentile filtering and one via domain reweighting (DoReMi-style), while logging post-curation domain proportions and inferred demographic distributions. If fairness differs significantly between these two matched-performance models, then fairness depends on the *data-generating path*, not just model capability. That would be strong evidence of causal coupling. If fairness collapses to a function of perplexity or reasoning accuracy alone, then the Pareto framing is misguided. This is experimentally clean and scientifically interpretable.

On the proxy question: small models can work in principle, but only for *directional* slope detection, not absolute fairness levels. Scale alters representation capacity and in-context learning behavior. So the requirement that the *sign* of the fairness–performance slope matches between 160M and ≥1B is a reasonable feasibility criterion. If slopes invert, then small models are not valid predictors. That's not a budget issue — that's about whether scaling laws preserve bias gradients.

So yes — technically possible. Scientifically meaningful — only if we elevate this from a tradeoff plot to a causal identification problem with matched-performance controls and mediation analysis over domain composition.

**Key Points:**
- The proposed tradeoff curve is technically feasible using Dolma's modular filtering/mixing pipeline and controlled training recipes [Soldaini et al., 2024].
- Monotonic fairness shifts are not guaranteed in principle due to nonlinear learning dynamics under cross-entropy; mechanism isolation is essential.
- A matched-performance causal decomposition (filtering vs. domain reweighting) is the critical experiment to determine whether fairness depends on curation path or merely model capability.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what is the *theoretical contribution* that would make this work matter to the field — beyond the empirical observation that fairness and performance correlate with curation choices?

DoReMi's Discussion & Conclusion [Xie et al., 2023] is instructive here: the paper's limitation is sensitivity to the choice of reference model and potential inefficiencies in domain weight changes over iterations. More significantly, DoReMi explicitly has *no knowledge of downstream tasks* — yet still matches performance of task-tuned domain weights on GLaM. This tells us something important: domain composition encodes enough implicit information about downstream capabilities that performance transfers can happen without explicit task signals. What we don't know is whether this same implicit encoding captures fairness-relevant distributional patterns. That gap is scientifically meaningful.

The research impact I see is threefold. First, if the hypothesis holds — that curation decisions systematically trade off performance against fairness in predictable ways — this would establish a **Curation Impact Law** analogous to scaling laws, providing the first empirically grounded guidance for responsible data pipeline design at the pretraining stage. This would matter to the DATA-FM workshop community, which explicitly calls for understanding fairness consequences of curation. Second, even if the hypothesis partially holds (some curation axes couple to fairness, others don't), the mediation analysis over domain composition would generate new theory: that fairness propagation from training data operates through domain-level representational pathways, not token-level frequency counts. Third, if it fails cleanly, that's also important: it would show that fairness in FM outputs is determined by RLHF, instruction tuning, or benchmark artifacts rather than pretraining data curation — redirecting the field's attention more efficiently.

What makes this contribution genuinely new vs. incremental? DCLM, FineWeb, and DoReMi all optimize for a single scalar performance signal. No prior work has jointly measured the two-dimensional (performance, fairness) response surface of curation hyperparameters on the same model checkpoints under controlled conditions. The Pareto frontier framing — borrowed from multi-objective optimization — applied to data curation choices is a paradigm shift in how we think about data pipeline design. The community currently lacks even a vocabulary for "curation tradeoffs" as distinct from "modeling tradeoffs." This work would supply that vocabulary with evidence.

However, I want to push back on one aspect: the matched-performance causal decomposition is essential, but we must ensure the fairness benchmarks (BBQ, WinoBias, StereoSet) are capturing *different dimensions* of bias — not just correlated proxies of the same underlying phenomenon. If they all move in lockstep, the contribution is measuring one latent dimension, not the full fairness landscape. The experimental design should include at minimum: demographic diversity (BBQ: race/gender/religion), coreference bias (WinoBias), and stereoype endorsement (StereoSet), to ensure the fairness surface is genuinely multi-dimensional.

**Key Points:**
- DoReMi's finding that domain weights encode downstream performance without task supervision [Xie et al., 2023] suggests domains carry implicit capability signals — whether they also carry implicit fairness signals is the novel theoretical question
- The contribution is a *Curation Impact Law*: the first empirically grounded, multi-dimensional characterization of how pretraining data decisions jointly determine performance and fairness
- Multi-dimensional fairness benchmarking (BBQ + WinoBias + StereoSet) is essential to ensure the contribution spans the full fairness landscape, not just one correlated latent factor

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on the correct framing: this is not a "tradeoff curve" problem, but a causal identification problem embedded within a controlled pretraining pipeline. DCLM gives us a rare asset — a fixed training recipe (decoder-only Transformer, LR 2e-5, batch size 256, ≤4 epochs, cross-entropy loss) and a massive common pool (DCLM-POOL, 240T tokens) under standardized preprocessing [Li et al., 2024]. That procedural control is what makes sharp falsification possible. The evidence suggests that percentile-based fastText filtering materially shifts MMLU (e.g., 64% at 7B with 2.6T tokens for DCLM-BASELINE) [Li et al., 2024]. Our task is to determine whether fairness metrics move *because of* the filtering mechanism, or merely alongside it.

I will formalize the causal structure. Let Q denote quality percentile cutoff, D domain composition, R demographic distribution within domains, P performance (MMLU), and F fairness metrics (BBQ, WinoBias, StereoSet). The coupling hypothesis asserts Q → F, possibly mediated by D and R. The capability-only hypothesis asserts Q → P → F, with no direct data-path effect. What would disprove coupling? If, after matching models within ±1% MMLU and ±0.1 validation perplexity, fairness metrics differ by ≤0.02 effect size across distinct curation paths, then F is a function of capability, not data pathway. That would falsify the core claim.

I therefore propose a **2×K factorial experiment** at 1B scale: Axis 1: Curation path (percentile filtering sweep at 10%, 30%, 50%, 70%, 90% vs. domain reweighting to achieve matched MMLU). Axis 2: Percentile or weight intensity. All models trained under identical DCLM methodology [Li et al., 2024]. For each checkpoint, log: (1) domain proportions, (2) demographic token proxies within domain, (3) validation perplexity, (4) MMLU, and (5) multi-dimensional fairness metrics. Conduct mediation analysis: estimate proportion of F variance explained by D conditional on P. Pre-register a threshold: if ≥70% of fairness variance is absorbed by domain composition, then the mechanism is domain-mediated, not "quality" per se.

We must also test for benchmark artifact confounds, as Prof. Rex correctly warns. I propose a **format-robustness test**: if fairness scores shift more with paraphrasing than with substantial changes in demographic token distribution, the benchmark is unstable and unfit as a causal readout. The best experiments are designed to fail; this one may invalidate our measurement instrument.

Finally, on scale transfer: I maintain the slope-consistency criterion. Define ΔF/ΔP across percentile sweeps at 160M and ≥1B. If the sign differs, small models are invalid proxies. If the sign matches but magnitude differs by >50%, then small models are only qualitatively informative.

**Key Points:**
- Formalize the causal graph and falsify coupling by testing matched-MMLU models across distinct curation paths [Li et al., 2024].
- Use factorial design with mediation analysis to determine whether fairness shifts are domain-mediated or capability-driven.
- Stress-test fairness benchmarks via paraphrase robustness and scale-consistency checks before accepting any tradeoff claim.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND — the causal graph formalization from 🔬 Prof. Vera is exactly what strengthens this hypothesis from a speculative curve to a rigorous causal claim. Let me synthesize what we've built and address remaining concerns constructively.

DCLM's Discussion & Conclusion [Li et al., 2024] acknowledges that "the importance of dataset design for training language models" is their central finding, while explicitly noting limitations in exploring "bias, multilinguality, and safety" — that admission is a green light for our research direction. The DCLM framework was specifically designed to enable controlled comparisons "at model scales ranging from 412M to 7B parameters" with "standardized evaluations," which is precisely the controlled scaffold we need. What DCLM built for performance ablations, we are extending to joint performance+fairness ablations. This is not a new idea — it's a natural extension of the existing DCLM benchmark infrastructure.

Let me strengthen the hypothesis by addressing each concern directly: Prof. Rex's confound about the fastText classifier being a Wikipedia-proxy is real — and this actually *helps* the hypothesis. If the quality filter is a domain-selectivity mechanism (Wikipedia-like → retained; non-Wikipedia → filtered), then domain mediation should be *large*, and we should expect to find domain composition as the principal mediator of any fairness effects. Prof. Vera's causal graph gives us the tools to test this directly. If domain composition absorbs ≥70% of fairness variance after conditioning on MMLU, this tells us: "quality filtering → fairness" is mediated entirely by domain selection, and the fix is domain-aware fairness-preserving filtering. That's a constructive, actionable finding either way.

Prof. Pax's concern about nonlinear learning dynamics is valid but manageable. The matched-MMLU causal decomposition — two training runs achieving ±1% MMLU via different curation paths — is a clean experimental design that avoids assuming monotonicity. If fairness diverges at matched performance, we have path-dependence. If it converges, we have capability-determination. Either way, we learn something. Now THAT'S stronger than a simple tradeoff curve!

I propose one refinement to tighten the hypothesis into a testable core claim: **Under controlled pretraining (DCLM recipe, fixed token budget, Pythia-1B scale), different curation paths achieving matched MMLU accuracy (±1%) will produce statistically distinguishable fairness outcomes (BBQ accuracy gap, WinoBias consistency ratio) with effect size ≥0.05, mediated at least partially by differential domain composition.** The null hypothesis is that fairness is a function of MMLU capability alone, with zero path-dependence. This is testable, falsifiable, and novel.

**Key Points:**
- DCLM's acknowledged limitations in bias/safety are an explicit invitation to extend their framework to joint performance+fairness measurement [Li et al., 2024]
- The fastText-as-domain-selector concern *strengthens* the mediation hypothesis: domain composition is predicted to be the principal mediator, testable via mediation analysis
- Refined core claim: matched-MMLU models via different curation paths will show path-dependent fairness effects (effect size ≥0.05), falsifiable against a pure capability-determination null

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally taking causal shape. But here's where this still breaks down.

You're treating "matched MMLU ±1%" as if it closes the backdoor from capability to fairness. It doesn't. MMLU is one slice of capability space. Under the DCLM framework, all models are trained with identical cross-entropy loss and architecture [Li et al., 2024], but cross-entropy optimization induces broad distributional shifts in conditional probabilities, not just reasoning accuracy. Two models matched on MMLU and even validation perplexity can differ substantially in calibration, lexical priors, or conditional stereotype activation. Show me evidence that MMLU is a *sufficient statistic* for the capability dimension relevant to BBQ or WinoBias. Right now, that's an unstated assumption.

Second: your mediation story (Q → D → F) presumes domain proportions are the right granularity. That may be too coarse. The DCLM filtering uses a fastText classifier to retain top-percentile "quality" documents [Li et al., 2024]. But fastText operates on surface lexical features. What if the real mediator isn't domain share but *within-domain contextual polarity distributions*? For example, Wikipedia might have balanced demographic mention rates but skewed sentiment or occupational co-occurrence patterns. Domain-level proportions would miss this entirely. If your mediation analysis finds only 40% of variance explained by domain mix, you can't conclude "quality has a direct effect" — it may just be that your mediator is mismeasured.

Third: the nonlinear learning dynamics problem hasn't gone away. Cross-entropy loss amplifies frequent high-confidence patterns. If filtering increases document homogeneity, you may increase gradient alignment on dominant stereotype patterns even while reducing raw frequency. That gives you a concrete alternative mechanism: *variance compression leads to sharper stereotype conditionals*. That predicts something testable: stereotype strength (e.g., StereoSet preference score) should correlate more with entropy reduction in token distributions than with domain share per se.

There is also a fairness-benchmark contamination problem. DCLM's decontamination analysis shows performance gains weren't due to test leakage [Li et al., 2024]. But you haven't run the analogous contamination test for fairness benchmarks. If your filtering disproportionately removes documents resembling benchmark templates, fairness scores could move artifactually.

Here's what would convince me: Two models matched on MMLU, perplexity, AND calibration error, with significant fairness divergence (≥0.05 effect size) that survives benchmark decontamination, where neither domain mix nor entropy compression fully explains the gap.

**Key Points:**
- Matching on MMLU is not sufficient; you must rule out broader capability and calibration differences as confounders.
- Domain-level mediation may be too coarse; test within-domain demographic co-occurrence and entropy compression as alternative mechanisms.
- Run fairness-benchmark contamination audits analogous to DCLM's MMLU decontamination to eliminate artifact explanations.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, NOW we're onto something genuinely interesting — the entropy compression mechanism is a beautiful alternative hypothesis that actually *extends* the novelty of this work beyond what I originally proposed!

Here's what excites me about Dolma's Discussion & Conclusion [Soldaini et al., 2024]: Dolma explicitly acknowledges that the corpus is "primarily English-only" and faces "challenges in capturing the representational breadth of language usage across diverse contexts." This is an admission that the training corpora we're working with are already demographically narrow even before quality filtering is applied. Now add the fastText filter on top? You're applying a narrowing function to an already-narrow distribution. The entropy compression mechanism that Prof. Rex identifies — filtering increases document homogeneity, which may sharpen stereotype conditionals — is not just a confounder, it's potentially *the* primary causal pathway.

What if the real contribution is not a "tradeoff curve" but a **Curation-Entropy-Fairness Trilemma**: quality filtering reduces corpus entropy (by selecting more similar/homogeneous documents), which simultaneously increases performance (due to higher-quality gradient signal) AND potentially sharpens stereotype conditionals (due to reduced counter-stereotypical exposure diversity). This is measurable! Corpus-level n-gram entropy before and after filtering is computable directly from the filtered vs. unfiltered Dolma subcorpora. StereoSet preference scores are a direct measure of stereotype conditional sharpness. The prediction: corpus entropy reduction correlates with StereoSet preference score increase, mediated by reduced counter-stereotypical exposure diversity.

What if we address Prof. Rex's calibration concern with a creative experimental design pivot: instead of matching on MMLU alone, use a **3D matching criterion**: matched MMLU, matched perplexity, AND matched HellaSwag (to cover common-sense capabilities relevant to coreference resolution in WinoBias). If fairness diverges after this 3D capability matching, the path-dependence claim becomes very strong. This is achievable using the existing Pythia evaluation suite and datatrove filtering infrastructure.

The Dolma corpus is particularly valuable here because it has already been split into source subcorpora (C4/CC-derived, books, Wikipedia, code, etc.) with documented characteristics, meaning we can measure entropy at the source level, not just aggregate level. That gives us a richer mediation variable than domain proportion alone.

**Key Points:**
- Dolma's acknowledged demographic narrowness [Soldaini et al., 2024] means filtering operates on an already-compressed distribution — entropy compression as a primary mechanism, not confound
- The **Curation-Entropy-Fairness Trilemma** reframes the contribution: quality filtering → corpus entropy reduction → stereotype sharpening, measurable via StereoSet preference vs. n-gram entropy correlation
- 3D capability matching (MMLU + perplexity + HellaSwag) is feasible with existing evaluation tools and would provide stronger causal identification than MMLU alone

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Mechanistically, everything you're proposing is *possible in principle* under the DCLM setup. The training recipe is fixed — decoder-only Transformer, cross-entropy loss, LR 2e-5, batch size 256, ≤4 epochs [Li et al., 2024]. That's actually a strength. It isolates the independent variable to dataset construction (filtering or mixing). Cross-entropy training absolutely can amplify distributional shifts in token co-occurrence. If filtering changes conditional demographic-occupation probabilities, the model *will* internalize that. There's no theoretical barrier there. So the core claim — that different curation paths could induce different fairness behavior even under identical architecture and loss — is scientifically sound.

Where I agree with Prof. Rex is on sufficiency of matching criteria. MMLU is not a sufficient statistic for the internal conditional distributions that drive BBQ or WinoBias. So yes, 3D matching (MMLU + perplexity + HellaSwag) is more defensible. I would go one step further: include calibration error (ECE) and logit margin statistics on demographic probes. If fairness divergence persists after matching on these broader capability indicators, then we're looking at genuine path dependence, not hidden capability variance.

On the entropy compression hypothesis: cross-entropy loss is sensitive to the entropy of the training distribution. If filtering via fastText selects the top 10% "quality" documents [Li et al., 2024], you are narrowing the support of the empirical distribution. That reduces lexical and contextual variance. In principle, reduced variance can sharpen conditional distributions — including stereotype-linked ones. However, n-gram entropy alone is too crude. Compute contextualized entropy — e.g., entropy of occupation given demographic token within domain. If stereotype sharpening is happening, you should see reduced conditional entropy H(occupation | demographic) in the filtered corpus AND corresponding increased logit gaps in model outputs. That's a concrete, testable bridge from data to model behavior.

The contamination concern is also addressable. DCLM performed decontamination for MMLU [Li et al., 2024]. You can replicate the same template-matching and fuzzy overlap checks for fairness benchmarks. There's no fundamental obstacle. If fairness shifts disappear after removing near-template overlaps, then the mechanism was artifact. If they persist, the signal is real.

**Key Points:**
- Different curation paths can theoretically induce path-dependent fairness effects under fixed cross-entropy training; no fundamental barrier to the mechanism.
- MMLU matching alone is insufficient; capability must be matched across broader metrics (perplexity, HellaSwag, calibration, logit margins).
- Entropy mediation must be measured at the conditional association level H(occupation | demographic), not just domain proportion or n-gram entropy.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

This matters because — and I want to be precise here — DCLM's key contribution is demonstrating that "dataset design for training language models" is the central lever for model capability [Li et al., 2024]. Their finding that model-based filtering outperforms all other curation approaches (achieving 64% MMLU at 7B vs. 57.4% for MAP-Neo) comes with a frank admission: "Limitations encountered include compute constraints that prevented a thorough exploration of all potential data curation strategies" including "bias, multilinguality, and safety." That is, DCLM implicitly identifies our research gap as the natural next step. The scientific community has already validated the performance axis. We are adding the fairness axis with equivalent rigor.

The theoretical contribution has clarified substantially through this discussion. What we now have is not a simple tradeoff curve but a **data-to-model causal chain with three falsifiable links**: (1) Quality filtering (fastText percentile cutoff or DoReMi domain reweighting) → changes conditional demographic association density in filtered corpus. (2) Training on differentially filtered corpora → internalizes different conditional probability structures around demographic-occupation co-occurrences, measurable via logit gaps. (3) Differential conditional distributions → differential performance on fairness benchmarks (BBQ, WinoBias, StereoSet) that persists after capability matching and benchmark decontamination.

Each link in this chain is independently testable and independently falsifiable. That is the hallmark of strong scientific theory. If Link 1 fails (filtering does not change demographic association density), the mechanism doesn't exist. If Link 1 holds but Link 2 fails (filtered models don't show different logit gaps despite different corpus statistics), then data statistics don't translate to model behavior at the internalization stage. If Link 2 holds but Link 3 fails (logit gaps change but benchmark scores are invariant), then fairness benchmarks are insensitive to the mechanism. Each failure mode points to a different intervention and generates actionable knowledge.

The research opens new questions about *what a fair pretraining corpus looks like* — which is an open design problem for responsible FM development. The novelty is precisely in being the first to instrument the full data-to-model causal chain under controlled conditions, using existing benchmarks, existing models, and existing corpora. No new benchmark creation, no synthetic data, no human annotation.

**Key Points:**
- DCLM's acknowledged limitations in bias/safety are the natural entry point for our extension [Li et al., 2024]; we are adding the fairness axis with equal methodological rigor
- A three-link testable causal chain (filtering → corpus demographics → model logits → fairness benchmarks) is scientifically rigorous and each link is independently falsifiable
- The contribution opens the design question of what a "fairness-preserving pretraining corpus" looks like — a novel and actionable research direction for responsible FM development

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on a scientifically defensible structure, but precision now matters. The experimental infrastructure is unusually clean: DCLM provides identical architecture, optimizer, cross-entropy loss, and training budget — only dataset construction varies [Li et al., 2024]. That is a rare experimental gift. However, causal clarity requires that we specify *exactly* what would falsify the path-dependence claim: if two models matched on MMLU, perplexity, HellaSwag, calibration error (ECE ≤0.5% difference), and demographic logit margin statistics show ≤0.01 absolute difference on BBQ/WinoBias/StereoSet, then the curation-fairness coupling hypothesis is not supported.

On mediation: the correct mediator is conditional structure. The testable link is: filtering via fastText top-percentile selection [Li et al., 2024] alters empirical H(occupation | demographic) in the corpus. If filtering reduces conditional entropy by ≥5% relative to baseline, then mean logit margin on matched demographic prompts should increase by ≥0.2 logits. Each link must have quantitative thresholds defined before training.

Contamination must be treated symmetrically. DCLM demonstrated decontamination for MMLU [Li et al., 2024]. The same fuzzy overlap and template-matching analysis must be applied to BBQ, WinoBias, and StereoSet. Pre-register a criterion: if ≥1% of benchmark items have near-duplicate substrings in training data and removing them eliminates fairness differences, then the observed divergence is artifactual.

I also propose an adversarial negative control: construct a "shuffled-demographic" corpus where demographic tokens are randomly permuted within documents while preserving global frequency. This preserves domain mix and entropy but destroys coherent conditional associations. The prediction: models trained on this corpus should show reduced logit margins and attenuated benchmark bias despite identical capability. If they do not, our causal chain is incomplete.

FineWeb's Discussion & Conclusion [Penedo et al., 2024] is instructive: "future work should consider incorporating diverse data types and more extensive scales." This directly supports the need for fairness-aware curation criteria as a natural extension of their framework.

**Key Points:**
- Define explicit falsification criteria: fairness divergence must persist after strict multi-metric capability matching and decontamination, with quantitative thresholds pre-specified.
- Test mediation at the conditional level H(occupation | demographic), linking corpus entropy shifts to model logit margins and benchmark outcomes.
- Include contamination audits and a shuffled-demographic negative control to eliminate artifact and isolate causal conditional structure effects.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Now THAT'S stronger! 🔬 Prof. Vera's shuffled-demographic negative control is a brilliant addition — it isolates the *conditional associative structure* of the training data as the causal mechanism, independent of domain proportions or global token frequency. Let me synthesize all the refinements into a coherent, strengthened hypothesis that addresses every concern raised.

The hypothesis has evolved through this discussion from a "tradeoff curve" to a **Path-Dependent Curation Fairness Hypothesis (PCFH)**: Under controlled pretraining (fixed architecture, optimizer, loss, token budget), different curation paths achieving matched downstream capability (MMLU ±1%, HellaSwag ±1%, perplexity ±0.1, ECE ≤0.5% difference) will produce statistically distinguishable fairness outcomes (BBQ accuracy gap ≥0.05 effect size, WinoBias consistency ratio divergence) that are: (a) mediated by differential conditional demographic association density in training corpora H(occupation|demographic), and (b) not explained by benchmark contamination artifacts (validated via template-matching decontamination).

This addresses every concern: Prof. Rex's confound of MMLU insufficiency → addressed by multi-metric capability matching. Prof. Rex's domain-level mediation granularity → addressed by conditional association entropy as the mediator. Prof. Pax's nonlinear dynamics concern → addressed by measuring conditional entropy reduction directly in the data. Prof. Vera's contamination worry → addressed by pre-registered decontamination protocol. Prof. Nova's entropy compression insight → integrated as the mechanism link between filtering and fairness.

The experimental design is clean and tractable using existing resources: Dolma/DCLM-POOL corpora (filtering platform), Pythia-1B models (controlled training), datatrove (filtering infrastructure), MMLU/HellaSwag/BBQ/WinoBias/StereoSet (evaluation), and the shuffled-demographic negative control corpus. What if we addressed the remaining concerns by prioritizing: (1) Pythia-1B for main experiments (tractable scale), with (2) Pythia-160M for directional slope validation, and (3) only one primary fairness axis (BBQ) for the main hypothesis, with WinoBias/StereoSet as secondary validations? That keeps the scope manageable.

**Key Points:**
- Path-Dependent Curation Fairness Hypothesis (PCFH): matched-capability models trained via different curation paths show fairness divergence mediated by differential conditional demographic association density
- All four major concerns (MMLU insufficiency, domain mediation granularity, nonlinear dynamics, contamination) are now explicitly addressed in the experimental design
- Feasible with existing tools: Dolma corpus + datatrove + Pythia suite + existing fairness benchmarks — no new benchmarks, no synthetic data, no human annotation required

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally getting tight. But here's where this still breaks down unless you sharpen it further.

First: your causal identification still hinges on an assumption you haven't made explicit — that the fastText quality filter used in DCLM is *conditionally independent* of demographic content except through "quality" signals. That's a huge assumption. DCLM uses a fastText classifier selecting the top 10% of documents from 240T tokens [Li et al., 2024]. Show me evidence that this classifier does not implicitly encode demographic style or topic priors. If "quality" correlates with certain registers that systematically underrepresent some demographic narratives, then your mediator H(occupation|demographic) is not just altered — it is altered through a *latent variable you're not modeling*. What would convince me is a diagnostic: regress fastText score on demographic token frequency and conditional association density. If R² is nontrivial, your mechanism includes classifier bias.

Second: the entropy → logit margin link is not guaranteed under cross-entropy training. Yes, the loss is −∑yᵢ log pᵢ [Li et al., 2024], but Transformers are nonlinear function approximators. Reduced corpus-level H(occupation|demographic) does not mechanically imply larger output logit gaps. Don't just posit a ≥5% entropy drop → ≥0.2 logit margin increase. Pre-specify a *functional form*. And run the shuffled-demographic negative control to test whether corpus entropy changes without corresponding logit shifts.

Third: capability matching must be multivariate and pre-registered. DCLM results show capability is multidimensional and sensitive to distributional shifts [Li et al., 2024]. If two models are matched on MMLU ±1% but differ in CORE by 2 points, are they really matched? I want a pre-registered multivariate matching criterion — perhaps Mahalanobis distance across all capability metrics ≤ ε.

Fourth: filtering vs. reweighting must yield distinguishable entropy signatures. Reweighting changes effective gradient contributions without altering support — a different intervention from top-10% filtering which *alters support*. If you can't distinguish these regimes empirically, your "path dependence" collapses into generic distribution shift.

**Key Points:**
- FastText filtering may encode latent demographic priors; test and model this explicitly or your mediator is mis-specified.
- Entropy reduction does not automatically imply logit margin amplification under cross-entropy training; pre-specify and test the functional relationship.
- Capability matching must be multivariate and pre-registered; filtering vs. reweighting must yield distinguishable entropy signatures.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me apply the DCLM experimental framework concretely to address Prof. Rex's concerns about whether this is all technically achievable [Li et al., 2024].

On the fastText classifier bias diagnostic: feasible. DCLM-POOL is publicly available (240T tokens, Common Crawl), and fastText scores were computed as part of the DCLM curation pipeline. Regressing fastText scores against demographic token frequency is computationally trivial on a sample of 10M documents. Whether R² is nontrivial is an empirical question, not a theoretical barrier. If the classifier does encode demographic priors, this becomes a *finding* in itself — "quality filters are implicit demographic selectors" — which is a publishable result.

On the entropy → logit margin functional form: the most defensible pre-specification is log-linear, based on information-theoretic grounds. Cross-entropy minimization drives the model to approximate the empirical distribution, so conditional logit margins should scale approximately with log odds in the training distribution. Pre-specify: ΔLog-odds(occupation|demographic) in corpus → same-direction shift in model logit margin, with slope estimated on a held-out calibration split. If the relationship is monotonic but nonlinear, a rank correlation test suffices. The key criterion: Spearman ρ between corpus-level log-odds and model logit margin should be significantly positive (p < 0.01). This is testable with the DCLM methodology and existing evaluation infrastructure [Li et al., 2024].

On multivariate capability matching: Mahalanobis distance across (MMLU, HellaSwag, perplexity, ECE) is straightforward to compute. The challenge is running enough filtered configurations to have matched pairs. Using Pythia-1B at 100B token budget (tractable), we need approximately 8-10 training runs at different filtering intensities plus 2 DoReMi-style domain reweighting runs. That's ~10-12 complete training runs. At Pythia-1B scale, each run is ~2-3 days on a single GPU. This is feasible within a standard research timeline.

The filtering vs. reweighting distinguishability is theoretically sound: filtering (support contraction) and reweighting (gradient reweighting over preserved support) should produce different H(occupation|demographic) signatures — filtering reduces diversity of retained documents while reweighting shifts their effective weight. Measuring these on the same Dolma subcorpora before and after intervention is a data audit step that requires no model training. Feasible as a preprocessing diagnostic.

**Key Points:**
- fastText classifier bias diagnostic is computationally feasible on DCLM-POOL samples; if R² is nontrivial, the finding itself is publishable
- Log-linear functional form pre-specification (Spearman ρ > 0, p < 0.01) is a tractable and theoretically justified criterion for the entropy → logit margin link
- ~10-12 Pythia-1B training runs for multivariate matched pairs are feasible; filtering and reweighting produce theoretically distinguishable entropy signatures measurable without model training

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Path-Dependent Curation Fairness Hypothesis introduces a genuinely novel research frame: treating different curation paths (filtering vs. domain reweighting) as distinct experimental interventions with measurable fairness consequences, mediated by conditional demographic association density. No prior work has applied this causal identification framework to pretraining data curation. The Curation-Entropy-Fairness Trilemma formulation — quality filtering reduces corpus entropy, which sharpens stereotype conditionals — is a creative and testable mechanism that extends DCLM's controlled benchmark to a new measurement axis.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable through a pre-registered experimental design: multivariate capability matching (MMLU, HellaSwag, perplexity, ECE), conditional entropy H(occupation|demographic) as a quantified mediator, fairness benchmark decontamination protocol, and a shuffled-demographic negative control. Every link in the three-step causal chain (filtering → corpus conditional entropy → model logit margins → fairness benchmarks) is independently falsifiable with explicit quantitative thresholds. This meets scientific rigor standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work fills a gap explicitly acknowledged by DCLM [Li et al., 2024] as outside their scope: bias, multilinguality, and safety. A positive finding would establish the first empirical characterization of how pretraining data curation decisions jointly determine performance and fairness, providing actionable guidance for responsible FM development. A negative finding would demonstrate that fairness is capability-determined, not path-determined, redirecting the field's attention more efficiently. Either outcome is scientifically significant.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experimental design is technically sound and feasible. The DCLM framework provides a controlled pretraining setup with fixed recipe. Pythia-1B training runs (~10-12 runs) are tractable. fastText bias diagnostics on DCLM-POOL samples are computationally trivial. Conditional entropy computation on Dolma subcorpora requires no model training. Existing fairness benchmarks (BBQ, WinoBias, StereoSet) are available. No new benchmarks, no synthetic data, no human annotation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The **Path-Dependent Curation Fairness Hypothesis (PCFH)** emerged from this discussion as the central claim: under controlled pretraining conditions (identical architecture, optimizer, loss, and token budget following the DCLM recipe), different data curation paths that achieve matched downstream capability (MMLU ±1%, HellaSwag ±1%, perplexity within ±0.1, ECE ≤0.5% difference) will produce statistically distinguishable fairness outcomes (BBQ accuracy gap, WinoBias consistency ratio divergence, StereoSet preference scores) that are mediated by differential conditional demographic association density H(occupation|demographic) in the training corpora.

The proposed causal chain has three testable links: (1) curation path (fastText quality percentile filtering vs. DoReMi-style domain reweighting) alters conditional demographic association density in the filtered corpus, measurable via H(occupation|demographic) and log-odds of demographic-occupation co-occurrences; (2) training on these differently filtered corpora internalizes different conditional probability structures around demographic-occupation co-occurrences, measurable via model logit margins on demographic probe prompts, with a log-linear functional relationship pre-specified (Spearman ρ > 0, p < 0.01); (3) differential logit structures produce differential fairness benchmark outcomes that persist after multi-metric capability matching, benchmark decontamination, and are abolished in a shuffled-demographic negative control corpus.

The experimental design uses Pythia-1B models trained on Dolma/DCLM-POOL with the datatrove pipeline, with approximately 10-12 training runs varying filtering intensity and curation path. The null hypothesis is that fairness is purely a function of capability level, with zero path-dependence after multivariate capability matching.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The fastText classifier may encode latent demographic priors (Wikipedia-style bias); this must be explicitly diagnosed via regression of fastText scores on demographic token frequency before claiming the mechanism is "quality filtering" rather than "demographic style selection"
- The entropy → logit margin functional relationship requires empirical pre-specification beyond the log-linear assumption, with the shuffled-demographic negative control as the critical test for whether corpus entropy shifts actually produce corresponding model distributional shifts
- **Mitigation Strategy:** Address both concerns with a pre-training data audit step: (a) run the fastText bias diagnostic on a 10M-document DCLM-POOL sample and report R² as a transparency metric; (b) include the shuffled-demographic control corpus as a mandatory experimental condition, not optional, to empirically characterize the entropy → logit margin relationship before investing in full-scale training runs.


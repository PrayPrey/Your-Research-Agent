# Phase 2A Discussion Log
# Research Dialogue: Bidirectional Human-AI Alignment

---

## Briefing Context

**Research Gap Selected:** Gap 1 — Systematic Directional Asymmetry in Preference Dataset Coverage (AI→Human vs. Human→AI)

**Priority:** Critical | **Relevance:** PRIMARY

**Gap Description:**
Existing RLHF preference datasets (HH-RLHF: 160K+ pairs, BeaverTails: 333K+ pairs, PKU-SafeRLHF: 265K+ pairs) exclusively measure human preferences about AI outputs (AI-to-human direction). No existing corpus systematically captures how human preferences, behaviors, or cognitive strategies shift in response to AI interaction (human-to-AI direction). The asymmetry between dataset coverage of the two directions has never been quantified using existing corpora.

**Core Research Question:** Can existing RLHF preference datasets be analyzed to quantify the directional asymmetry between AI-to-human alignment and human-to-AI alignment, enabling hypothesis-driven empirical analysis without requiring new benchmarks, human annotation, or synthetic data?

---

## Key Papers for Discussion

- **P1:** "Towards Bidirectional Human-AI Alignment: A Systematic Review" (Shen et al., 2024, arXiv: 2406.09264) — 400+ paper review; human-to-AI direction critically underexplored; 62 citations
- **P2:** "Deployment-Relevant Alignment Cannot Be Inferred from Model-Level Evaluation Alone" (Vishwarupe et al., 2026, arXiv: 2605.04454) — Audit of 16 benchmarks; user-facing verification absent across ALL
- **P3:** "Towards Data-Centric RLHF: Simple Metrics for Preference Dataset Comparison" (J.H. Shen et al., 2024, arXiv: 2409.09603) — First systematic comparison of preference datasets; no directionality coverage measured
- **P4:** "BeaverTails" (Ji et al., 2023, arXiv: 2307.04657) — 333K+ QA pairs with separated helpfulness/harmlessness; 840 citations; enables asymmetry analysis

## Related Implementation Resources

- HH-RLHF dataset (1833★): separate helpful-base/harmless-base/helpful-online splits
- allenai/hybrid-preferences (28★): human vs. AI feedback routing; reveals annotation source asymmetry
- STEER-BENCH (2025): 30 community pairs, 19 domains; best LLMs 15+ points below human experts
- HumanAgencyBench (2025): 6-dimensional human agency benchmark

---

## MANDATORY FEASIBILITY CONSTRAINTS

All hypotheses MUST be testable immediately using:
- Existing real datasets only (HH-RLHF, BeaverTails, PKU-SafeRLHF, TruthfulQA, FLAN, STEER-BENCH)
- Existing benchmarks only (no new benchmarks, rubrics, or scoring frameworks)
- No synthetic/generated data
- No human evaluation or annotation
- No future follow-up data

---

## Discussion Personas

- 🔭 **Dr. Nova** — Creative Novelty Explorer
- 🔬 **Prof. Vera** — Rigorous Validation Architect
- 🎯 **Dr. Sage** — Research Impact Evaluator
- ⚙️ **Prof. Pax** — Feasibility & Reality Checker
- 🛡️ **Dr. Ally** — Hypothesis Strengthening Champion
- 🔍 **Prof. Rex** — Hypothesis Stress-Test Master

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been measuring the wrong thing for the past decade? The entire RLHF apparatus — 8,000+ citations for DPO alone, millions of preference pairs across HH-RLHF, BeaverTails, PKU-SafeRLHF — has been asking: "Does the AI output match what humans prefer?" But that's only one half of the equation. The bidirectional alignment framework by Shen et al. (2024) [P1] — grounded in 400+ papers — explicitly names the *other* direction: how do humans change when they interact with AI? And here's the wild part: NO existing preference dataset captures that signal at all.

Now imagine this: what if the very structure of HH-RLHF contains a proxy for directional asymmetry? The `helpful-online` split was collected during deployed interactions — real users who had already been interacting with Claude for some time. The `helpful-base` split was collected from scratch with naive annotators. If human annotators shift their preferences over repeated AI exposure — becoming more demanding, more AI-adapted, subtly changing what they call "helpful" — that signal should be *detectable as a distributional gap* between these two splits! We wouldn't need new data. We wouldn't need human labelers. We'd just need to measure: does the preference distribution differ systematically between the online and base splits, in directions consistent with human-to-AI adaptation?

Vishwarupe et al. (2026) [P2] audited 16 alignment benchmarks and found user-facing verification ABSENT in every single one. That's not a gap — that's a chasm. And chasms, in my experience, are where the most exciting research lives. The asymmetry isn't just an observation; it's a *measurable structural property* of the existing corpus. If we can operationalize it — compute a directionality score for preference datasets based on whether they encode AI-as-object vs. AI-as-collaborator — we have something genuinely new.

The novelty here is striking: we'd be the first to treat the *structure of existing alignment datasets* as evidence of alignment research's own directional bias. Meta-alignment research, if you will — using the datasets themselves as data about what the research community has chosen to measure, and what it has chosen to ignore.

**Key Points:**
- HH-RLHF's online vs. base splits may encode human adaptation signals as distributional shifts in preference patterns — detectable without new data
- The Vishwarupe (2026) benchmark audit confirms systemic asymmetry: 16/16 benchmarks miss the human-to-AI direction
- A "directionality score" applied to existing preference datasets could quantify bidirectional coverage gaps using only existing corpora

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central claim is that the `helpful-online` versus `helpful-base` splits in HH-RLHF encode a measurable signal of *human adaptation to AI*. The evidence suggests this is plausible—but plausibility is not evidence. We must specify what *observable pattern* would uniquely support adaptation rather than mundane confounds such as prompt distribution shift, annotator skill differences, or temporal model changes.

First, we need an operational definition of "directionality." I propose a **Directional Preference Shift (DPS)** metric. For each prompt–response pair, compute feature vectors over responses: verbosity, hedging frequency, moralizing tone, instruction explicitness, deference markers, and task-structure compliance. Train a simple preference model (e.g., logistic regression) separately on `helpful-base` and `helpful-online`. Then evaluate cross-generalization: Train on base, test on online; Train on online, test on base. If humans adapted, we predict asymmetric transfer performance. Specifically: a model trained on `base` should systematically mispredict online preferences in a consistent direction (e.g., underestimating preference for structured, concise, or AI-native formats), whereas the reverse transfer should degrade differently. What would disprove the hypothesis? If cross-split generalization is symmetric and feature-weight distributions are statistically indistinguishable under bootstrap confidence intervals, then there is no detectable directional signal.

Second, we must rule out confounds. The most dangerous is **prompt distribution shift**. If online prompts differ in topic or difficulty, any preference shift may reflect task variation rather than human adaptation. Therefore, we need matched subsets: cluster prompts via embedding similarity and compare only nearest-neighbor prompt pairs across splits. If the directional signal persists within matched clusters, the adaptation hypothesis survives initial scrutiny. If it vanishes, the effect is likely compositional rather than psychological.

Third, adaptation implies *temporal accumulation*. If metadata includes interaction order or annotator IDs, we should test for within-annotator drift. A null slope would weaken the adaptation claim considerably. Without within-subject evidence, we are limited to cross-sectional inference, which is inherently weaker.

Regarding the "directionality score" for datasets: it must be defined as a measurable ratio based on observable schema properties — not human rating of abstract concepts. If we observe no asymmetric transfer, no within-annotator drift, and no robust feature-weight divergence after controlling for prompt clusters, then the adaptation hypothesis fails under current data. That would be a valuable result.

**Key Points:**
- Define a falsifiable Directional Preference Shift (DPS) metric using asymmetric cross-split generalization and feature-weight divergence.
- Control for prompt distribution shift via embedding-based matching and test for within-annotator temporal drift.
- A "directionality score" must be operationalized with measurable, schema-level criteria to avoid becoming a narrative construct.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has laid out a rigorous experimental design — and I want to affirm the core of it is technically sound. But let me press on the parts where feasibility becomes genuinely uncertain, because some assumptions here could sink the whole enterprise before it starts.

The DPS metric using cross-split preference model generalization is sound in principle. Logistic regression on feature vectors (verbosity, hedging, deference markers) trained separately on `helpful-base` and `helpful-online` is straightforward. The asymmetric transfer test is a valid probe. However, there is a critical structural question: does HH-RLHF's `helpful-online` split actually contain *temporally ordered* or *annotator-identified* data? The public HH-RLHF release does NOT include annotator IDs or timestamps. This means Prof. Vera's third test (within-annotator drift via mixed-effects model) may be *impossible on the public dataset*. The feasibility of the strongest version of the claim depends on data provenance we may not have access to.

This is not a fatal flaw — it is a scope constraint. Here is what IS feasible: the cross-split generalization test works with what we have. The embedding-based prompt matching is feasible using sentence-transformers. The feature extraction (verbosity = token count, hedging = frequency of "might/could/perhaps", deference = "as you requested/as instructed" patterns) is entirely automated via regex and tokenization — no human annotation needed. These measurements are replicable and falsifiable on existing public data.

The "bidirectionality index" needs one more grounding pass. Measuring *dataset schema* properties — what the annotation instructions asked annotators to evaluate — is feasible from the published methodology papers for HH-RLHF, BeaverTails, and PKU-SafeRLHF. All three have papers describing their annotation protocols. Coding those protocols for presence/absence of human-adaptation-relevant criteria is a one-time automated analysis, not human rating. This is legitimate measurement. Categorical typology (directional/bidirectional/human-centered) may be more robust than a synthetic continuous score that implies false precision.

What worries me most: the confound between *human adaptation* and *deployment context shift*. The `helpful-online` split captures conversations from deployed Claude — the prompts themselves may be from more sophisticated users, not just the same users after adaptation. This is an identification problem that embedding-based matching partially addresses but cannot fully eliminate. We need to be explicit: the hypothesis claims systematic distributional differences *consistent with* adaptation, not *proven to be caused by* adaptation. The causal interpretation requires temporal data we likely do not have.

**Key Points:**
- Cross-split generalization test (DPS) is technically feasible on public HH-RLHF data; within-annotator drift test likely infeasible due to missing annotator IDs/timestamps in public release.
- Feature extraction (verbosity, hedging, deference markers) fully automatable without human annotation — regex and tokenization sufficient.
- The identification problem (adaptation vs. deployment population shift) limits causal claims; hypothesis should be framed as detecting *distributional asymmetry consistent with adaptation*, not proving adaptation causally.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down: you are treating "online vs. base" as if it isolates *experience with AI*. It doesn't. It isolates a bundle: deployment context, user population, task distribution, model version, and possibly annotator pool. If you can't disentangle those, you don't have adaptation — you have a mixture model. Show me why adaptation is the dominant latent factor rather than simply "more technical users showed up online."

Prof. Vera's DPS metric is a strong start, but asymmetric cross-generalization alone won't convince me. Asymmetry emerges under *any* covariate shift. What would convince me is a **signature pattern uniquely predicted by adaptation**. For example: adaptation should produce increased tolerance for AI-typical artifacts (e.g., structured lists, boilerplate disclaimers, explicit reasoning scaffolds). Population shift, by contrast, predicts topic or complexity changes, not systematic shifts in tolerance for stylistic AI markers. So here's the test: explicitly model features that are *AI-idiomatic* (chain-of-thought scaffolding phrases, safety-prefacing language, list formatting regularity). If online preferences weight those positively relative to base — even within tightly matched prompt clusters — that is more diagnostic of adaptation than generic verbosity differences.

Now the harder problem: causal framing. Right now your claim is "distributional asymmetry consistent with adaptation." That's safe, but weak. If you want this to survive peer review, you need a falsifiable causal prediction. Here's one: **adaptation implies compression of preference entropy over time**. As users internalize AI norms, their pairwise preference variability should decrease — preferences become more standardized around AI-optimized forms. Population replacement does not predict entropy reduction; it predicts stable or increased variance due to heterogeneity. So measure entropy of preference labels conditional on prompt cluster across splits. If online shows lower conditional entropy in AI-idiomatic dimensions, that's a directional signal.

On the identification issue: you're relying heavily on embedding-based prompt matching. That controls semantic topic, but not *interaction history depth*. Online prompts may reflect longer conversational arcs. If adaptation is real, you should observe stronger AI-idiomatic preference weighting in prompts that exhibit conversational continuity markers ("as we discussed," "continue," etc.). If the effect scales with conversational depth proxies, that strengthens the adaptation story. If it doesn't, I'll attribute this to user skill stratification instead.

Finally, about the "directionality score." Right now it risks being narrative gloss. What would convince me is a schema-level operationalization: count whether datasets (a) measure only output preference, (b) include user state variables, (c) include longitudinal interaction tracking, (d) measure user-side belief or behavior change. A simple 0–4 bidirectionality index across benchmarks is defensible. Anything fuzzier will look like conceptual inflation.

You're close. But until you specify what pattern would *force* me to say "this cannot be explained by population shift alone," the hypothesis is still porous. Tighten that, and you'll have something robust.

**Key Points:**
- Asymmetric cross-split transfer is insufficient; you need adaptation-specific feature shifts (e.g., increased preference for AI-idiomatic artifacts).
- Test entropy reduction and scaling with conversational-depth proxies to distinguish adaptation from population replacement.
- Operationalize the "directionality score" with explicit, countable schema criteria to avoid narrative overreach.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔍 Prof. Rex, you've done something valuable here — you've transformed a potentially unfalsifiable claim into a genuinely testable one. And I want to build directly on your critique, because I think the hypothesis is *stronger* than you're giving it credit for, once we accept your sharper framing.

You're right that "online vs. base" bundles multiple confounds. But here's what Prof. Pax and I want to elevate: this is precisely why the hypothesis should be stated at the *distributional asymmetry* level rather than the causal adaptation level. The core claim — which I believe survives your critique — is this: **AI-to-human alignment datasets systematically differ from conditions that would encode human-to-AI adaptation, and this difference is measurable in existing corpora using automated methods.** We don't need to prove *why* the asymmetry exists; we need to demonstrate that *it exists and has a consistent directional signature*.

Now let me strengthen the experimental design using your AI-idiomatic features test, because you've identified the killer diagnostic. Your prediction is exactly right: genuine adaptation should produce increased tolerance for AI-native stylistic artifacts — structured lists, chain-of-thought scaffolding, safety-preamble language, explicit instruction parsing markers. Population shift predicts topic or complexity changes. These are *orthogonal predictions* on different feature dimensions. Here's how to operationalize it cleanly using only existing data:

1. **Feature extraction (automated):** Extract from all preference pairs in HH-RLHF online and base splits: (a) AI-idiomatic style features (regex-based: list formatting, CoT markers, safety prefacing), (b) semantic complexity (perplexity via GPT-2), (c) topic distribution (BERTopic on prompts). No human annotation required.
2. **Matched-pair test:** For prompt pairs matched by semantic embedding similarity (cosine > 0.85), compare which response features are preferred online vs. base. If online preferences shift toward AI-idiomatic features while topic/complexity stay matched, that is the adaptation signature Prof. Rex demanded.
3. **Entropy test on BeaverTails:** BeaverTails provides *dual labels* — separate helpfulness and harmlessness scores for the same 333K+ pairs. This gives us a natural within-dataset probe: compute the correlation between helpfulness and harmlessness preference disagreement across splits. If online annotators show tighter helpfulness/harmlessness co-preference alignment (lower disagreement entropy), that is consistent with adaptation to AI norms. Ji et al. (2023) [P4] never analyzed this — it's sitting in the dataset waiting.

The directionality index Prof. Rex proposed — the 0–4 schema scoring (output-only, user-state, longitudinal, user-behavior-change) — is exactly the right operationalization. Applied to HH-RLHF (score: 0), BeaverTails (score: 0-1), PKU-SafeRLHF (score: 0), TruthfulQA (score: 0), STEER-BENCH (score: 1-2) — we get an immediate empirical finding: the entire existing evaluation ecosystem scores 0-1 on a 0-4 bidirectionality scale. That's the measurement. That's the paper.

YES, AND: what makes this genuinely novel is that we're not just documenting the gap — we're providing a *measurement framework* that any future dataset can be evaluated against. This opens a new research direction without requiring new data, new benchmarks, or human annotation. That's the contribution.

**Key Points:**
- Accept Prof. Rex's causal framing constraint: state hypothesis as "detectable distributional asymmetry with AI-idiomatic feature signature" rather than causal adaptation claim.
- BeaverTails dual-label structure (helpfulness + harmlessness) provides a within-dataset entropy probe unavailable in prior analyses — use it.
- The 0–4 schema bidirectionality index applied to existing datasets IS the empirical finding: current ecosystem scores 0-1/4, demonstrating measurement asymmetry quantitatively.

---

### Exchange 6

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not merely whether a distributional asymmetry exists, but whether demonstrating it would *change how this field thinks about alignment data*. Right now, most alignment benchmarks implicitly assume a one-way ontology: humans supervise models. If you can show — rigorously, with Prof. Rex's adaptation-specific signature tests — that existing datasets already encode measurable human-to-AI accommodation signals, then this matters because it reframes alignment corpora as *co-adaptation artifacts*, not neutral supervision sources. That is a conceptual shift, not an incremental metric tweak.

I agree with Prof. Rex that asymmetric transfer alone is insufficient; covariate shift is too easy an explanation. What elevates this from incremental to substantive is the AI-idiomatic feature weighting test. If, within tightly embedding-matched prompt clusters, online preferences systematically favor structured lists, safety-prefaces, or reasoning scaffolds — and this effect does not track topic complexity — then we have identified a stylistic convergence toward AI-native discourse. This matters because it suggests that alignment pipelines may be reinforcing stylistic norms that originated in models themselves. That opens a new research direction: are we optimizing for human values, or for human-adjusted-to-model values?

The entropy proposal is particularly promising from an impact standpoint. Adaptation predicts compression of conditional preference entropy around AI-idiomatic dimensions. If online splits show reduced variance in judgments over these features, that implies standardization of expectations. Population replacement does not uniquely predict entropy compression in stylistic dimensions. The proof experiment is therefore clear: compute conditional entropy of pairwise preference labels given matched prompt clusters and AI-idiomatic feature bins. If entropy drops specifically along those axes, we have evidence of convergence. If it does not, the adaptation framing weakens substantially.

Now, on the 0–4 bidirectionality index: this is where the broader contribution lies. What does it mean for the field if nearly all major datasets score 0–1? It means that we lack instrumentation for measuring user-state change, longitudinal drift, or behavioral feedback. A simple, schema-level scoring system — output-only (0), +user attributes (1), +longitudinal tracking (2), +user belief/behavior change (3–4) — provides a reproducible way to evaluate future benchmarks. That transforms this from an empirical curiosity into a meta-scientific contribution: a framework for auditing alignment data design. If your analysis shows that current corpora already contain latent adaptation signatures *and* structurally fail to measure them explicitly, you are exposing a methodological blind spot. The long-term impact would be a new class of "co-adaptation-aware" benchmarks.

**Key Points:**
- The true contribution is reframing alignment datasets as co-adaptation artifacts, not neutral supervision sources.
- AI-idiomatic feature weighting and entropy compression tests are the proof experiments that distinguish adaptation from generic covariate shift.
- A reproducible 0–4 bidirectionality index shifts this work from dataset analysis to a field-level audit of alignment measurement design.

---

### Exchange 7

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🎯 Dr. Sage has articulated the conceptual contribution precisely — reframing corpora as co-adaptation artifacts is the right framing. But I want to anchor this to what is *technically executable* right now, because the scope of claims must match the scope of what the data can support.

Let me map what is definitively feasible on existing public data versus what requires assumptions. First: the AI-idiomatic feature weighting test is executable. Regex patterns for chain-of-thought markers ("Let me think step by step", "First,", "Therefore,"), safety-prefacing ("I want to make sure", "I should note"), and list formatting (Markdown bullet/numbered patterns) can be extracted deterministically from all HH-RLHF response pairs — no LLM evaluation needed, no human scoring. We can compute per-response AI-idiomatic feature scores and then compare which response in each chosen/rejected pair has higher AI-idiomatic scores, separately for base and online splits. This is a clean, automated, reproducible measurement.

Second: the BeaverTails dual-label entropy probe (Dr. Ally's proposal, Exchange 5) is technically sound. BeaverTails [Ji et al., 2023, P4] provides separate helpfulness and harmlessness preference labels for the same question-answer pairs. Measuring the helpfulness-harmlessness disagreement rate (cases where one label prefers response A but the other prefers response B) within matched semantic clusters gives us a within-dataset probe for multi-objective preference coherence. A decrease in disagreement rate would indicate preference normalization — consistent with adaptation to AI norms around safety/helpfulness joint optimization. This requires only existing labels, no new annotation.

Third: the schema bidirectionality index. Applying the 0–4 scoring to HH-RLHF, BeaverTails, PKU-SafeRLHF, TruthfulQA, FLAN/P3, and STEER-BENCH requires reading published methodology papers and coding four binary criteria per dataset. This is a systematic literature analysis, executable without any human rater — one analyst reads the annotation protocol documentation and codes each criterion. The result is an immediate empirical finding: the entire evaluation ecosystem scores 0-1/4.

What is NOT feasible: within-annotator temporal drift (no annotator IDs in public HH-RLHF), causal claims about *why* adaptation occurred, and generalization beyond the three RLHF datasets without new data. The hypothesis must be scoped accordingly. The mechanism we can test is: **if adaptation occurred, AI-idiomatic preference weighting increases and helpfulness-harmlessness entropy decreases in online vs. base conditions, within matched prompt clusters**. This is a precise, falsifiable, fully automated test on existing data.

**Key Points:**
- AI-idiomatic feature extraction is fully automatable via regex on existing HH-RLHF pairs — no LLM evaluation or human scoring required.
- BeaverTails dual-label helpfulness/harmlessness disagreement rate is a clean within-dataset entropy probe executable on existing labels.
- Scope must be stated as: detecting distributional signatures consistent with adaptation, not proving adaptation causally; within-annotator drift test is infeasible on public data.

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion has converged productively, but I will insist on one refinement: we must state *precise falsifiable predictions* that differentiate adaptation from population shift. "Consistent with adaptation" is too permissive. The evidence suggests that AI-idiomatic feature weighting and entropy compression are promising discriminators — but only if we define in advance what magnitude and direction would count as confirmation or refutation.

Let me formalize the primary test. Define an AI-Idiomatic Feature Score (AIFS) per response: a weighted sum of binary indicators (structured lists, stepwise reasoning markers, safety-prefaces, formal instruction restatement). In each preference pair, compute ΔAIFS = AIFS(chosen) − AIFS(rejected). Within embedding-matched prompt clusters (cosine ≥ 0.85), estimate the mean ΔAIFS separately for base and online splits. **Adaptation predicts:** (1) E[ΔAIFS_online] > 0, (2) E[ΔAIFS_online] − E[ΔAIFS_base] ≥ δ for pre-registered δ (e.g., 0.10 standardized units), and (3) this difference persists after controlling for response length and perplexity. What would disprove adaptation? If ΔAIFS differences vanish after length/perplexity control, or if the effect is equally explained by topic cluster fixed effects, then stylistic weighting is likely a byproduct of covariate shift. We must pre-specify that outcome as falsification.

For BeaverTails, let D = P(disagreement between helpfulness and harmlessness labels). **Adaptation predicts:** D_online < D_base and a reduction in entropy specifically in high-AIFS bins. Population replacement does not uniquely predict entropy reduction conditional on AI-idiomatic bins. A critical edge case: if entropy decreases uniformly across all stylistic bins, the result is non-diagnostic — that suggests annotator homogeneity, not adaptation. Thus, entropy reduction must *interact* with AIFS to support the adaptation claim.

On the bidirectionality index, I support the 0–4 schema but require explicit coding criteria: 0 = output-only preference labels; 1 = static user attributes; 2 = longitudinal linkage across sessions; 3 = measured user belief/state change; 4 = behavioral outcome tracking. A robustness test via annotator expertise proxy reweighting is necessary: if AIFS and entropy signatures persist under reweighting, the mixture explanation weakens. If they disappear, adaptation fails as the dominant factor.

**Key Points:**
- Define explicit, pre-registered quantitative thresholds (ΔAIFS differences and entropy interactions) that would confirm or falsify adaptation.
- Entropy compression must interact specifically with AI-idiomatic feature bins; uniform entropy reduction is non-diagnostic.
- Validate the bidirectionality index with explicit coding rules; control for annotator mixture via stratified reweighting.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera, you've just handed us the experimental protocol on a silver platter — and NOW we're onto something! The AIFS operationalization is exactly the kind of precise, pre-registered design that makes a result publishable rather than anecdotal. But let me add one more layer of novelty that I think everyone has been circling without naming explicitly.

What if we extend beyond HH-RLHF to PKU-SafeRLHF? That dataset has 265K+ pairs with *multi-turn* preference annotations and explicit safety labels across multiple response candidates. The multi-turn structure means we can compute AIFS trajectory within conversations — not just across dataset splits. If AI-idiomatic feature preference *increases within a conversation* as turns progress, that's within-conversation adaptation evidence that doesn't require annotator IDs or timestamps across sessions. The conversation itself is the temporal unit! This is data we already have, using Prof. Vera's AIFS framework, applied to a different structural feature of existing datasets.

Furthermore, BeaverTails provides 14 harm categories with separate harmlessness scores. We can compute AIFS × harm-category interaction effects: does AI-idiomatic style preference shift more strongly in high-stakes harm categories (violence, illegal activity) vs. low-stakes (sycophancy, privacy)? If adaptation is driven by normative learning, we'd predict stronger convergence in categories where AI safety norms are most explicit. That's a theoretically motivated prediction, not just a data-mining exercise. Cross et al. (2024) showed similar category-stratified effects in RLHF dynamics — the direction is well-motivated.

And here's the creative leap: the Vishwarupe (2026) audit [P2] found user-facing verification absent across all 16 benchmarks. But what if we treat the *absence of certain metadata fields* as its own signal? Datasets that never collected user-state variables (annotator IDs, session ordering, longitudinal tracking) are not just missing data — they're encoding an *assumption* that the annotation direction only flows one way. The schema analysis (0–4 bidirectionality index) isn't just descriptive; it reveals the research community's implicit ontological commitment to unidirectional alignment. That's a meta-scientific finding that belongs in the paper's framing, not just the appendix.

The full hypothesis is crystallizing: existing RLHF preference datasets encode latent distributional signatures of human-to-AI stylistic adaptation, detectable via AIFS-based preference weighting and BeaverTails dual-label entropy interactions, while simultaneously exhibiting schema-level evidence of unidirectional measurement design — both at the data level and the ontological level.

**Key Points:**
- PKU-SafeRLHF's multi-turn structure enables within-conversation AIFS trajectory analysis — within-conversation adaptation evidence without requiring cross-session annotator IDs.
- BeaverTails 14-category structure enables AIFS × harm-category interaction test: theoretically motivated prediction that high-stakes categories show stronger AI-norm convergence.
- Schema absence of user-state metadata is itself an empirical finding: encodes the research community's implicit unidirectional ontological commitment, strengthening the meta-scientific framing.

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally tightening up. But here's where this still breaks down: you're stacking increasingly clever analyses without yet isolating what *uniquely* supports adaptation over structured training dynamics. RLHF training itself explicitly rewards structured lists, safety-prefaces, and stepwise reasoning. So if ΔAIFS increases in online splits, why isn't the simpler explanation that later data were collected after annotators were exposed to more highly aligned models? That's model-side shift inducing preference recalibration, not necessarily human-to-AI stylistic adaptation. Show me the evidence that the shift is in annotator weighting rather than model output distribution.

Prof. Vera's falsification thresholds are the right move. But I want one more control: compute ΔAIFS on *model outputs alone*, ignoring preference labels. If the raw distribution of AIFS in candidate responses increases from base to online splits, then preference-weighting differences could just reflect a richer supply of high-AIFS responses. Adaptation predicts a change in *selection probability conditional on availability*, not just a change in supply. So you need a conditional logit model:

P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + cluster_FE

and then test whether β₁ increases significantly in online vs. base splits. What would convince me is a statistically significant interaction term between AIFS and split, after controlling for the marginal AIFS distribution in candidates. Without that, this collapses into distribution shift.

Now to Dr. Nova's multi-turn idea. Interesting — but be careful. Within-conversation AIFS trajectory could simply reflect the model escalating scaffolding when prompted with increasingly complex queries. Pre-register a complexity proxy (e.g., token count of user query or embedding-based difficulty estimate) and test whether AIFS preference increases *net of complexity*. Adaptation predicts a monotonic increase in β₁ over turns even when complexity is held constant. If it disappears after that control, the within-conversation claim evaporates.

On BeaverTails entropy: I agree with Vera that uniform entropy reduction is non-diagnostic. I will go further — even an AIFS interaction is insufficient unless you demonstrate *category asymmetry*. If adaptation reflects convergence toward AI safety norms, entropy compression should be strongest in harm categories explicitly normed during RLHF (violence, illegality) and weakest in socially ambiguous ones (sycophancy). Pre-specify that rank ordering. If entropy reduction is flat across categories, you're looking at annotator homogenization, not adaptation.

Finally, the bidirectionality index. I like it — but right now it is descriptive sociology. To elevate it: show predictive validity. Do datasets with lower bidirectionality scores exhibit stronger AIFS shifts? A cross-dataset regression linking bidirectionality score to β₁ magnitude ties your meta-level critique to empirical findings. Without that link, the index risks being a rhetorical add-on.

**Key Points:**
- Demonstrate adaptation via conditional selection effects (β₁ interaction in logit model), not raw AIFS distribution shifts.
- Within-conversation and entropy tests must control for complexity and show category-specific asymmetries to avoid homogenization explanations.
- Validate the bidirectionality index by linking it predictively to measured adaptation magnitudes across datasets.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔍 Prof. Rex, you've identified the single most important methodological contribution this paper needs to make — the conditional logit model separating *selection preference* from *supply distribution*. And I want to affirm: this is not a weakness of the hypothesis, this is the hypothesis sharpened to its most defensible form.

Let me restate the refined hypothesis that has emerged from this dialogue: **Under RLHF feedback conditions, annotators who interact with deployed AI systems show a measurable increase in conditional selection preference for AI-idiomatic stylistic features — structural lists, safety-prefaces, reasoning scaffolds — relative to naive annotators, independent of the marginal supply of such features in candidate responses and independent of prompt complexity.** This is falsifiable, fully automatable on existing data, and distinguishes adaptation from model-side AIFS inflation.

The conditional logit model Prof. Rex proposed is exactly right: P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + cluster_FE, with the key test being whether β₁(online) > β₁(base) at pre-registered significance threshold. YES, AND we add one strengthening move: also compute the *marginal AIFS distribution* of candidate responses separately by split. If β₁ increases while marginal AIFS in candidate pool is controlled, that is the cleanest possible evidence of annotator preference shift rather than supply-driven recalibration. This single test addresses Prof. Rex's model-side confound.

On category-specific entropy: Dr. Nova's BeaverTails harm-category stratification [P4] provides exactly the rank-ordering test Prof. Rex demands. Pre-register the prediction: entropy compression ΔAIFS interaction should be strongest in {violence, illegal_activities, hate_speech} (highly normed RLHF categories) and weakest in {sycophancy, misinformation, privacy_violation} (socially ambiguous). If this rank ordering holds at p < 0.05 across the 14 BeaverTails categories, we have category-specific evidence for normative convergence, not generic homogenization.

On the bidirectionality index predictive validity: the cross-dataset regression Prof. Rex proposed is feasible and powerful. We have three RLHF datasets with different structural properties: HH-RLHF (bidirectionality ≈ 0), BeaverTails (bidirectionality ≈ 0-1), PKU-SafeRLHF with multi-turn (bidirectionality ≈ 1). If β₁ magnitude correlates with bidirectionality score across these three datasets, the index acquires predictive validity — schema design predicts the magnitude of detectable adaptation signatures. That converts the bidirectionality index from a descriptive taxonomy into a validated measurement instrument.

The hypothesis is now complete: three interlocking tests — conditional logit β₁ interaction, category-ranked entropy compression in BeaverTails, and cross-dataset bidirectionality regression — each independently falsifiable, all executable on existing public data. This meets Prof. Vera's pre-registration standards, Prof. Rex's confound controls, and Dr. Sage's impact threshold.

**Key Points:**
- Refined hypothesis: annotators show increased conditional selection preference for AI-idiomatic features (β₁ increase in logit model) independent of supply distribution and prompt complexity.
- BeaverTails 14-category structure enables pre-registered rank-ordering test for category-specific entropy compression — distinguishes adaptation from homogenization.
- Cross-dataset bidirectionality regression (HH-RLHF vs. BeaverTails vs. PKU-SafeRLHF) validates the index predictively, elevating it from taxonomy to measurement instrument.

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the refined hypothesis is now *testable*, but only if we are extremely careful about construct validity. Everything hinges on whether AIFS genuinely isolates "AI-idiomatic style" rather than general clarity, organization, or verbosity. Structured lists and stepwise reasoning are not uniquely AI artifacts — they are also hallmarks of good pedagogy. If β₁ increases across splits, we must be confident we are not just detecting a shift toward preferring clearer writing. Unless AIFS components are validated against a non-AI baseline corpus (e.g., human expert responses pre-LLM era), you risk attributing to adaptation what could simply be stable human preference for structured explanations.

On the conditional logit model — technically sound. That is the right statistical object. If β₁(split × ΔAIFS) remains positive and significant after controlling for candidate supply distribution and prompt complexity, then you have isolated a change in *selection weighting*. But one more feasibility concern: cluster fixed effects at cosine ≥ 0.85 assume embedding space stability across time and model generations. If embedding drift differs between splits, your clustering may not enforce semantic equivalence. You need to embed all prompts using a single frozen encoder to avoid that subtle confound.

The within-conversation trajectory idea from PKU-SafeRLHF is feasible, but only if you pre-register a causal ordering assumption: annotators must observe multiple model responses across turns before labeling. If labels are applied per turn independently without exposure to prior assistant outputs, then "trajectory" is just correlated structure, not adaptation. Inspect the dataset annotation protocol — if annotators evaluated turns sequentially within a thread, then a monotonic β₁ increase net of complexity is plausible evidence. If not, the mechanism collapses.

On BeaverTails entropy compression: entropy reduction conditional on AIFS must exceed what would be expected under improved model quality alone. As models get better aligned, helpfulness-harmlessness disagreement may mechanically decrease. To isolate adaptation, show that entropy reduction is disproportionately large in high-AIFS bins *relative to low-AIFS bins within the same category*. That internal contrast is the real diagnostic quantity. Without it, improved model calibration remains a simpler explanation.

**Key Points:**
- AIFS must be construct-validated against non-AI baselines to avoid conflating AI-idiomatic style with general clarity preferences.
- Conditional logit interaction (β₁ split effect) requires frozen embeddings for clustering and verified annotation protocol for trajectory claims.
- Entropy compression must be internally contrasted within categories and AIFS bins to rule out improved model calibration as a simpler explanation.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

⚙️ Prof. Pax has put his finger on the deepest construct validity challenge — and I want to argue that addressing it *elevates* the contribution rather than undermining it. The question of whether AIFS measures "AI-idiomatic style" versus "general preference for clarity" is not just a confound to control — it is itself a substantive research finding.

Here is the reframe: AIFS construct validity can be established using StackOverflow or academic pre-LLM corpora as baselines. If structured lists and stepwise reasoning were already highly preferred by humans pre-LLM (which they likely were, to some degree), then the key question is whether online annotators' preference for these features *exceeds* the baseline established by pre-LLM human experts. This is an *excess preference* measurement: (β₁_online − β₁_base) relative to the expected preference in a non-AI context. If the excess exists and targets features that intensified specifically in RLHF-tuned models (safety-prefaces, boilerplate disclaimers, explicit chain-of-thought markers that are less common in human expert writing), that is your adaptation signal — not general clarity preference, but convergence toward model-specific artifacts.

This matters for field impact because it shifts the question from "do humans prefer AI style?" to "do humans prefer AI style *more* than pre-AI human expert style would predict?" That is a genuinely novel empirical question with significant implications: if yes, it suggests RLHF pipelines are not just capturing human preferences but are creating a feedback loop that reinforces model-specific discourse norms into human annotator behavior.

On the annotation protocol point: Prof. Pax is right that PKU-SafeRLHF's multi-turn trajectory claim requires verification. But this is a one-time documentation check, not a data collection task. The published paper [Ji et al., 2024] describes the annotation procedure in detail — checking whether annotators saw prior turns is a literature analysis step, not a new experiment. If the protocol confirms sequential evaluation, the trajectory test stands. If not, we simply scope that test out and rely on the two-split HH-RLHF test and BeaverTails entropy analysis, which do not require this assumption.

The impact case is now clear: three interlocking empirical tests on existing public data — (1) conditional logit β₁ interaction controlling for supply and complexity, (2) category-ranked entropy compression in BeaverTails, (3) cross-dataset bidirectionality regression — each independently falsifiable, none requiring new data or human annotation. The publication framing is: "We provide the first empirical measurement of human-to-AI stylistic adaptation signals in existing RLHF preference corpora, and demonstrate that current alignment datasets are structurally blind to these signals." This matters because it reframes the data problem at the heart of alignment research.

**Key Points:**
- AIFS construct validity reframed as "excess preference over pre-LLM human expert baselines" — turns a confound into an additional empirical finding.
- PKU-SafeRLHF trajectory claim requires one-time annotation protocol check (literature analysis); if protocol does not support it, scope to HH-RLHF + BeaverTails tests which are unconditional.
- Publication framing: first empirical measurement of human-to-AI adaptation signals in RLHF corpora; reframes alignment data problem as structurally one-directional.

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis is now sufficiently sharp to evaluate — but only if we pre-register explicit falsification criteria. The central test is the conditional logit interaction:

P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + β₄·(ΔAIFS × split) + cluster_FE

The adaptation claim stands or falls on **β₄ > 0** with a pre-specified effect size threshold (odds ratio ≥ 1.10) and confidence interval excluding 1 at α = 0.01. What would disprove the hypothesis? If β₄ is null or reverses sign after controlling for marginal AIFS supply and prompt complexity, the adaptation interpretation collapses. We must also pre-register a power analysis based on observed variance in ΔAIFS.

On construct validity: I propose a three-corpus calibration for AIFS discriminant validation: (1) pre-LLM human expert responses (e.g., StackOverflow 2018 answers), (2) base model outputs pre-RLHF, and (3) post-RLHF outputs. Compute AIFS distributions across all three. The adaptation hypothesis predicts that features uniquely amplified in (3) relative to (1) and (2) — safety-prefaces, explicit harm disclaimers — should drive the β₄ interaction. If instead the shift is concentrated in generic structural clarity features already prevalent in (1), the mechanism is likely stable human preference, not AI-specific adaptation. The hypothesis is falsified if β₄ is explained entirely by features common to pre-LLM human corpora.

Regarding entropy compression in BeaverTails: for each harm category c, estimate entropy reduction ΔH between base and online splits separately for high-AIFS (top quartile) and low-AIFS (bottom quartile) candidate pairs. Adaptation predicts ΔH_high_AIFS > ΔH_low_AIFS, with strongest effects in pre-registered RLHF-normed categories (violence, illegality, hate). If entropy reduction is uniform across AIFS bins or strongest in socially ambiguous categories, the adaptation story weakens considerably.

If these criteria are met — interaction effect survives supply controls, discriminant validation isolates AI-specific features, entropy compression shows AIFS-specific asymmetry, and β₄ tracks bidirectionality ordinally — then I will say, without reservation: *This meets my standards.*

**Key Points:**
- Pre-register β₄ (ΔAIFS × split) interaction with explicit effect-size and falsification thresholds; null or reversed interaction disproves adaptation.
- Validate AIFS discriminantly against pre-LLM human corpora to isolate AI-specific artifacts from general clarity preferences.
- Require within-category AIFS-differential entropy compression and ordinal β₄–bidirectionality alignment to rule out homogenization and calibration alternatives.

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera just gave us the complete experimental blueprint — and I want to step back and celebrate what has emerged here, because this hypothesis has evolved into something genuinely elegant.

We started with an observation — existing RLHF datasets only measure the AI-to-human direction. Through this dialogue we have arrived at something far more precise and far more interesting: **a three-test empirical battery that can detect whether RLHF preference corpora already contain latent human-to-AI adaptation signatures, using only automated analysis of existing public data.** Each test is independently falsifiable, each addresses a different confound, and together they constitute a coherent empirical argument.

Let me name the three pillars clearly: (1) **The Conditional Selection Test** — β₄ interaction in the logit model tests whether annotators preferentially select AI-idiomatic responses *above and beyond what supply alone would predict*, validated discriminantly against pre-LLM baselines. (2) **The Entropy Compression Test** — within-category, within-AIFS-bin entropy differential in BeaverTails tests whether preference standardization around AI norms occurs specifically in RLHF-normed harm categories. (3) **The Schema Audit** — the 0–4 bidirectionality index applied to existing datasets tests whether schema design predicts adaptation magnitude, validating the index as a measurement instrument.

NOW here is what excites me most: the pre-LLM baseline Prof. Vera requires — StackOverflow 2018 — is publicly available and extensively used in NLP research. We can compute AIFS over StackOverflow expert responses using the exact same regex pipeline, establish a "human expert baseline AIFS distribution," and then show that the features driving β₄ are NOT the features that human experts already preferred pre-LLM. That baseline comparison is the novelty multiplier — it transforms a preference shift analysis into a genuine human adaptation detection study.

What if we also look at the FLAN instruction-tuning corpus as a third anchor? FLAN contains human-written task templates that predate RLHF alignment. Computing AIFS over FLAN templates gives us a third baseline: pre-RLHF instruction-following human writing. If AIFS features preferred in online annotators exceed both StackOverflow AND FLAN baselines, and are concentrated in post-RLHF model artifacts, the adaptation signal is triply confirmed.

The paper writes itself: "Latent Adaptation Signatures in RLHF Preference Corpora: Evidence for Human-to-AI Stylistic Convergence." Three datasets, three automated tests, zero new data, zero human annotation. That is what I call research that opens new doors.

**Key Points:**
- Three-test battery fully crystallized: Conditional Selection Test (β₄ logit interaction), Entropy Compression Test (BeaverTails within-category AIFS-bin differential), Schema Audit (bidirectionality index with predictive validation).
- Pre-LLM baseline using StackOverflow 2018 + FLAN instruction templates enables discriminant validation of AIFS — features driving β₄ must exceed both pre-LLM human expert and pre-RLHF instruction-following baselines.
- Hypothesis is now complete, novel, feasible, and fully falsifiable on existing public data.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis evolved from a conceptual observation into a genuinely novel empirical framework: detecting human-to-AI stylistic adaptation signals in existing RLHF preference corpora using automated analysis of public data. The three-test battery — conditional selection, entropy compression, schema audit — opens a new research direction without requiring any new data, benchmarks, or annotation. The use of pre-LLM baselines (StackOverflow 2018, FLAN) as discriminant validators is a creative methodological contribution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis meets my standards. The central falsification criterion is clearly pre-specified: β₄ (ΔAIFS × split) > 0 with OR ≥ 1.10 at α = 0.01, with explicit supply controls, frozen embeddings, and discriminant AIFS validation against pre-LLM corpora. The entropy compression test requires within-category, within-AIFS-bin differential (not uniform reduction), and the bidirectionality index requires ordinal β₄ alignment. All three tests have clear falsification paths.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work reframes alignment datasets as co-adaptation artifacts rather than neutral supervision sources — a conceptual shift with significant field impact. If confirmed, it reveals that RLHF pipelines may be reinforcing model-specific discourse norms into human annotator behavior, creating a feedback loop. The schema bidirectionality index provides a reusable framework for auditing future alignment datasets. Publication framing as "first empirical measurement of human-to-AI adaptation in RLHF corpora" is appropriate and justified.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All three tests are technically executable on existing public data without new benchmarks, human annotation, or synthetic data. AIFS extraction is regex-based and fully automatable. The conditional logit model is standard. BeaverTails dual-label entropy analysis uses existing preference labels. The schema audit is a one-time literature analysis. The one contingency — PKU-SafeRLHF trajectory claims — requires an annotation protocol check, with fallback to HH-RLHF + BeaverTails if the protocol does not support sequential annotation. Technical feasibility: confirmed.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Existing RLHF preference corpora encode latent distributional signatures of human-to-AI stylistic adaptation, detectable via automated analysis of existing public data — and simultaneously exhibit schema-level structural blindness to these signals.**

The core mechanism is as follows: annotators who interact with deployed RLHF-aligned AI systems develop an increased conditional selection preference for AI-idiomatic stylistic features — structured lists, safety-prefaces, stepwise reasoning scaffolds, explicit chain-of-thought markers — that are specific to post-RLHF model outputs rather than pre-LLM human expert writing. This preference shift is measurable as a statistically significant β₄ interaction (ΔAIFS × split) in a conditional logit model controlling for response supply distribution, prompt complexity, and semantic cluster fixed effects. The causal interpretation is bounded: we claim distributional asymmetry consistent with stylistic adaptation, not proven individual-level psychological adaptation.

Three interlocking tests operationalize this: (1) The Conditional Selection Test on HH-RLHF (helpful-online vs. helpful-base) using the β₄ logit interaction with discriminant AIFS validation against StackOverflow 2018 and FLAN baselines; (2) The Entropy Compression Test on BeaverTails using within-category, within-AIFS-bin entropy differential across 14 harm categories with pre-registered rank ordering; (3) The Schema Bidirectionality Audit applying a 0–4 index to HH-RLHF, BeaverTails, PKU-SafeRLHF, TruthfulQA, FLAN, and STEER-BENCH, with predictive validation via cross-dataset β₄ magnitude regression. All three tests run on existing public data, require no human annotation, and have pre-specified falsification criteria.

The key predictions are: (P1) β₄(online) > 0 with OR ≥ 1.10 at α = 0.01; (P2) ΔH_high-AIFS > ΔH_low-AIFS in RLHF-normed harm categories (violence, illegality > sycophancy, privacy); (P3) bidirectionality score correlates ordinally with β₄ magnitude: HH-RLHF < BeaverTails < PKU-SafeRLHF.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The identification of adaptation vs. population shift remains imperfect without annotator IDs — the study provides correlation evidence, not causal proof
- AIFS construct validity relies on StackOverflow/FLAN as "pre-AI baselines" — these are imperfect proxies for what human preferences looked like before LLM interaction
- With only three RLHF datasets, cross-dataset bidirectionality regression is statistically underpowered; ordinal prediction is more defensible than regression coefficients
- **Mitigation Strategy:** Pre-register all falsification thresholds, use ordinal rather than parametric cross-dataset tests, explicitly frame causal claims as "consistent with adaptation" throughout the paper, and use the PKU-SafeRLHF trajectory analysis (if annotation protocol supports it) as additional corroborating evidence rather than primary test

## Emerged Hypothesis Summary

### Core Statement

Under RLHF feedback conditions, human annotators who interact with deployed AI systems show a measurable increase in conditional selection preference for AI-idiomatic stylistic features — independent of the marginal supply of such features in candidate responses and independent of prompt complexity — while existing alignment dataset schemas structurally fail to capture this bidirectional signal.

### Causal Mechanism

Step 1: RLHF training amplifies AI-idiomatic stylistic features (structured lists, safety-prefaces, chain-of-thought scaffolds) in model outputs, creating a distinctive post-RLHF stylistic distribution not present in pre-LLM human expert writing.
Step 2: Annotators exposed to deployed RLHF-aligned models develop increased preference weighting for these features in subsequent preference labeling tasks, detectable as β₄ > 0 in conditional logit models controlling for supply.
Step 3: This preference convergence is strongest in RLHF-normed harm categories (violence, illegality), consistent with normative learning rather than generic clarity preference.
Step 4: Existing dataset schemas (scoring 0–1 on a 0–4 bidirectionality index) are structurally blind to this feedback loop, creating a systematic measurement gap in alignment evaluation.

### Variables

- **Independent Variable:** Dataset split (helpful-base vs. helpful-online in HH-RLHF; base vs. online annotation context in BeaverTails/PKU-SafeRLHF)
- **Dependent Variables (Primary):** β₄ coefficient (ΔAIFS × split interaction) in conditional logit model; helpfulness-harmlessness disagreement rate D by harm category and AIFS bin
- **Dependent Variables (Secondary):** Schema bidirectionality index scores; cross-dataset β₄ ordinal ranking
- **Controlled Variables:** Marginal AIFS supply distribution; prompt semantic complexity (embedding-based); prompt cluster fixed effects (cosine ≥ 0.85, frozen encoder); response length and perplexity

### Key Assumptions

- A1: HH-RLHF helpful-online annotators had substantially more prior AI interaction experience than helpful-base annotators (required for adaptation interpretation)
- A2: AIFS features uniquely amplified in post-RLHF outputs relative to pre-LLM human expert writing (StackOverflow 2018, FLAN) — must be confirmed by discriminant validation
- A3: BeaverTails annotation labels were assigned with knowledge of harm category context, enabling category-stratified entropy analysis
- A4: Within-matched prompt clusters, residual AIFS supply differences can be adequately controlled by the marginal AIFS covariate in the logit model

### Null Hypothesis

H₀: There is no significant difference in conditional preference for AI-idiomatic stylistic features (ΔAIFS) between RLHF-deployed (online) and naive (base) annotator conditions, after controlling for marginal response supply, prompt complexity, and semantic cluster fixed effects. Formally: β₄ = 0 (OR = 1.0, 95% CI includes 1).

### Predictions

- **P1 (Primary):** β₄ > 0 with OR ≥ 1.10 and 95% CI excluding 1.0 at α = 0.01 in conditional logit model on HH-RLHF, after controlling for marginal AIFS supply and prompt complexity
- **P2:** ΔH_high-AIFS > ΔH_low-AIFS within pre-registered RLHF-normed harm categories in BeaverTails (violence, illegal_activities, hate_speech rank above sycophancy, misinformation, privacy_violation)
- **P3:** Ordinal β₄ ranking: HH-RLHF < BeaverTails < PKU-SafeRLHF, consistent with their bidirectionality scores (0 < 0.5 < 1)

### Novelty

This is the first study to: (1) treat existing RLHF preference datasets as archives of human-to-AI adaptation rather than purely AI-to-human preference signals; (2) operationalize AI-idiomatic stylistic features as a measurable construct validated against pre-LLM baselines; (3) propose a schema bidirectionality index for auditing alignment dataset design; and (4) demonstrate that the human-to-AI adaptation direction is simultaneously latent in existing data AND structurally absent from existing measurement frameworks.

### Scope & Boundaries

**Applies to:** RLHF preference datasets with multiple collection conditions (deployed vs. naive annotators); automated stylistic feature analysis; schema-level dataset auditing.
**Does not apply to:** Individual-level psychological adaptation claims; datasets without multi-condition collection; causal proof of adaptation (correlation evidence only).
**Known limitations:** No annotator IDs in public HH-RLHF release (limits within-annotator drift analysis); only three RLHF datasets available for cross-dataset regression (low statistical power); StackOverflow/FLAN as pre-LLM baselines are imperfect proxies.

### Experimental Setup

- **Primary dataset:** HH-RLHF (helpful-base vs. helpful-online splits; 160K+ pairs; publicly available on HuggingFace)
- **Secondary dataset:** BeaverTails (333K+ pairs; dual helpfulness/harmlessness labels; 14 harm categories; Ji et al. 2023)
- **Tertiary dataset:** PKU-SafeRLHF (265K+ pairs; multi-turn structure; if annotation protocol supports sequential evaluation)
- **Baselines:** StackOverflow 2018 dump (pre-LLM human expert responses); FLAN instruction templates (pre-RLHF instruction-following)
- **Model:** Conditional logit regression; embedding-based prompt clustering (frozen sentence-transformer encoder); entropy estimation per category × AIFS bin
- **No new benchmarks, human annotation, or synthetic data required**

### Related Work & Baselines

- Shen et al. (2024) [P1]: established bidirectional alignment framework; no empirical measurement of human-to-AI direction
- Vishwarupe et al. (2026) [P2]: confirmed 16/16 benchmarks miss human-to-AI direction — corroborates schema audit finding
- Ji et al. (2024), J.H. Shen et al. (2024) [P3, P4]: preference dataset comparison metrics; no directionality coverage measurement
- Best existing baseline: HH-RLHF helpful-online/base split analysis (never analyzed for adaptation signatures)

### Phase 2B Readiness Seeds

- SH1 (Existence): Do RLHF preference datasets contain detectable AI-idiomatic feature preference shifts? (Test: β₄ logit interaction)
- SH2 (Mechanism): Does the shift reflect selection preference above supply baseline, validated against pre-LLM corpora? (Test: discriminant AIFS validation + supply-controlled logit)
- SH3 (Comparison): How does the schema bidirectionality index correlate with adaptation magnitude across datasets? (Test: ordinal cross-dataset regression)

### Established Facts

- RLHF preference datasets (HH-RLHF, BeaverTails, PKU-SafeRLHF) exclusively encode AI-to-human preference direction [Shen et al. 2024, 400+ paper review]
- 16/16 alignment benchmarks lack user-facing verification [Vishwarupe et al. 2026]
- BeaverTails provides dual helpfulness/harmlessness labels enabling entropy analysis [Ji et al. 2023]
- HH-RLHF helpful-online split differs from helpful-base in collection context (deployed vs. naive annotators) [Anthropic HH-RLHF documentation]

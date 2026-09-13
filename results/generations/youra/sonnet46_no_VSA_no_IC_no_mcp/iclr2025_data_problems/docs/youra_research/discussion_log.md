# Phase 2A Discussion Log
**Gap:** Gap 1 — Controlled Cross-Family Curation Comparison on Standard Benchmarks
**Execution Mode:** UNATTENDED (Self-Play — Claude plays all personas)
**Architecture:** Independent-Controller Ablation (no external orchestrate_exchange.py)
**Date:** 2026-08-25

---

## Research Briefing

### Selected Gap
**Gap 1 (PRIMARY, HIGH priority):** No controlled cross-family study compares Pythia (Pile/dedup-Pile) vs OLMo (Dolma) performance on identical benchmarks while attributing differences to curation choices rather than architecture or scale.

### Research Question
Do existing data curation pipeline choices (quality filtering thresholds, deduplication aggressiveness, domain mixing ratios) produce systematically different downstream task performance profiles across pretrained model families, as measured on established benchmarks?

### Detailed Sub-Questions
- Q1: Do different filtering strategies produce measurably different downstream performance on MMLU, HellaSwag, ARC, WinoGrande?
- Q2: Can attribution methods (TRAK, TracIn) identify which training data subsets drive performance differences?
- Q3: Does test data contamination in Pile vs Dolma systematically bias benchmark comparisons?
- Q4: How do curation decisions interact with model scale?

### Available Papers (Claude-summarized, arXiv IDs unverified)
- **P1: Pythia [Biderman et al. 2023]** — 16 LLMs (70M–12B), Pile vs dedup-Pile, 154 checkpoints, benchmark results available
- **P2: OLMo [Groeneveld et al. 2024]** — Dolma-trained, documented mixing ratios, same benchmarks
- **P3: Dolma [Soldaini et al. 2024]** — OLMo corpus: C4+CC+peS2o+Reddit+Books+Wiki, aggressive quality filtering
- **P4: Dedup [Lee et al. 2022]** — Dedup reduces memorization, improves benchmarks; Pythia Pile vs dedup-Pile = natural comparison
- **P5: DSIR [Xie et al. 2023]** — Importance resampling for data selection; outperforms heuristic filters

### Feasibility Constraints (MANDATORY)
- ❌ No new benchmarks or rubrics
- ❌ No synthetic/generated data
- ❌ No human evaluation or annotation
- ✅ Only existing real datasets and existing benchmarks

### Previous Failure Context
None — first Phase 2A attempt.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we could read the fingerprints of data curation decisions directly off benchmark performance curves — without retraining a single model? We have an extraordinary natural experiment sitting in plain sight: Pythia trained on Pile and dedup-Pile with 154 intermediate checkpoints, and OLMo trained on Dolma with a completely different filtering philosophy. These two model families share roughly similar architecture scales but diverge on almost every meaningful curation choice — deduplication aggressiveness, domain mixing ratios, quality filter thresholds.

The novelty here isn't just "compare two models." It's using the Pythia within-family comparison (Pile vs dedup-Pile, same architecture, same scale, different curation) as a *clean controlled experiment*, and then extending that lens cross-family to OLMo/Dolma to ask: do the same curation signals that matter within Pythia also explain the Pythia–OLMo performance gap? This is a two-level analysis — within-family curation attribution, then cross-family hypothesis transfer.

What I find exciting is that lm-evaluation-harness already supports both model families. We can run a unified evaluation protocol and generate comparable performance profiles across MMLU, HellaSwag, ARC, and WinoGrande. The benchmark choice matters: these four tasks probe different capabilities — factual recall, commonsense reasoning, science reasoning, pronoun resolution — and different curation choices may produce systematically different *profiles* rather than uniform shifts. That profile pattern is the novel contribution.

**Key Points:**
- Two-level design: within-family (Pile vs dedup-Pile) then cross-family (Pythia vs OLMo)
- Benchmark profiles (not scalar performance) as the dependent variable — different tasks may respond differently to same curation choice
- No retraining needed — existing checkpoints + lm-evaluation-harness

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is productive, but let me immediately identify where this breaks down scientifically. The core confound is architecture: Pythia uses GPT-NeoX and OLMo uses its own architecture variant. If we observe benchmark differences between Pythia-1B and OLMo-1B, we cannot cleanly attribute them to curation choices without ruling out architectural effects. This isn't a minor concern — it's the central identification problem.

The within-family comparison (Pile vs dedup-Pile, same architecture) is far cleaner and is where I'd anchor our primary hypothesis. [Biderman et al., 2023] documented both training runs with identical architectures, making deduplication the sole varying factor at matched parameter counts. *That* is a controlled experiment. The cross-family comparison is observational and must be clearly labeled as such — useful for generating hypotheses but not for causal claims.

On the benchmark profile idea: I want precise, measurable predictions. If we claim that deduplication produces differential effects across benchmark categories, we need to specify in advance which categories we expect to improve and why, or we risk cherry-picking post-hoc. The testable prediction should be: "Pythia dedup-Pile models will outperform Pile models on knowledge-intensive benchmarks (MMLU) more than on reasoning benchmarks (HellaSwag), because deduplication reduces memorization of repeated factual patterns that contaminate knowledge benchmarks but doesn't change core reasoning ability." What would disprove that? If dedup-Pile shows uniform improvement (or none) across task categories.

**Key Points:**
- Primary hypothesis must anchor on within-family (Pile vs dedup-Pile) for clean identification
- Cross-family comparison is observational: useful for patterns, not causal claims
- Need pre-specified directional predictions per benchmark category, not post-hoc profiling

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me check whether this is technically sound before we get too far. The within-family design Prof. Vera describes is theoretically valid — same architecture, same scale, same training compute, only curation differs. The measurement approach (lm-evaluation-harness few-shot evaluation on MMLU, HellaSwag, ARC, WinoGrande) is standard and well-validated. So the measurement science is sound.

But I want to flag a fundamental issue with the cross-family comparison that goes beyond architecture: Pythia models top out at ~12B and use a specific training compute budget, while OLMo models have different parameter counts and token counts. Without careful size-matching, we're comparing models at different points on their scaling curves. The [Biderman et al., 2023] and [Groeneveld et al., 2024] papers report results at different model sizes, and cherry-picking the closest parameter count still leaves compute-budget differences. This is a confound that's hard to eliminate post-hoc.

The within-family design is clean and feasible. I'd recommend the hypothesis scope narrowed to: "deduplication aggressiveness (Pile vs dedup-Pile) produces category-differential performance shifts in Pythia models across standard benchmarks, as measured by lm-evaluation-harness few-shot evaluation." The cross-family extension becomes a secondary, exploratory analysis clearly labeled as non-causal. That design can be executed entirely with existing artifacts and is technically sound.

On TRAK attribution (Gap 2): at 1B–7B scale this requires significant GPU memory for gradient computation. That's a feasibility concern for attribution at LLM scale — TRAK was validated on smaller models. But the primary hypothesis doesn't need attribution — that's a separate sub-question.

**Key Points:**
- Within-family design is technically sound: same architecture, matched scale, only curation differs
- Cross-family comparison confounded by architecture AND compute budget — must be labeled exploratory
- Recommended scope: deduplication effect within Pythia family as primary hypothesis
- TRAK at LLM scale is technically challenging — separate this from primary claim

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this field genuinely need? And I think the answer is clearer than it might appear. The data curation literature has produced excellent within-training-run ablations — [Xie et al., 2023] on DSIR, [Lee et al., 2022] on deduplication effects. What's systematically missing is a *post-hoc analysis of existing deployed models* asking: given that we didn't control the curation, can we still measure its signature in the performance profiles?

This matters because the field is moving toward increasingly large models where controlled curation ablations become prohibitively expensive. The research community needs methods for diagnosing curation quality from deployed model behavior — not just for academic interest, but for practitioners deciding which open-source model to fine-tune for a specific domain task. If "dedup-Pile models outperform Pile models on knowledge-intensive benchmarks but not reasoning benchmarks," that's actionable guidance.

I'll push back on narrowing too quickly. Prof. Pax is right that cross-family causal claims are unwarranted. But Dr. Nova's point about benchmark *profiles* is genuinely novel and scientifically interesting: the hypothesis that different curation choices produce *characteristic performance profile signatures* (not just scalar shifts) is testable and meaningful. The Pythia within-family comparison gives us clean causal ground, and the OLMo comparison gives us an external consistency check. Together they make a stronger paper than either alone.

The field impact: a well-executed study here gives the community a framework for "curation fingerprinting" — identifying which aspects of training data composition drove a model's performance profile. That's new, and it opens the next generation of data attribution questions.

**Key Points:**
- Field needs post-hoc curation analysis on existing models — pre-specified ablations are becoming infeasible at scale
- "Benchmark profile signatures" as a concept is novel: curation choices may produce characteristic patterns, not just scalar shifts
- Within-family (causal) + cross-family (consistency check) design is stronger than either alone
- Contribution: "curation fingerprinting" framework for deployed models

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and now I can see how to tie everything together into a testable, defensible hypothesis. Prof. Vera's concern about identification is valid and actually strengthens the design: we lean hard on the Pythia within-family comparison as the causal core. Prof. Pax is right that we scope the cross-family analysis as exploratory. Dr. Sage's "curation fingerprinting" framing is the conceptual contribution.

Here's the strengthened hypothesis: **Deduplication aggressiveness in pretraining corpora produces category-differential performance signatures across downstream benchmarks in language models, detectable without retraining, using standard evaluation protocols on existing open model checkpoints.** Specifically: Pythia dedup-Pile models will show disproportionate improvement on knowledge-intensive benchmarks (MMLU, ARC) compared to commonsense reasoning benchmarks (HellaSwag, WinoGrande), relative to Pile-trained counterparts at matched parameter count, because deduplication reduces the frequency of repeated factual patterns that inflate knowledge-benchmark performance in non-deduplicated models.

The mechanism: repeated documents in Pile inflate knowledge-benchmark performance by effectively memorizing question-answer patterns present in training data. Deduplication removes this inflation, revealing the model's true generalization. The effect should be stronger on knowledge benchmarks (where memorization is most beneficial) than reasoning benchmarks (where memorization provides less advantage).

To address Prof. Rex's anticipated concern about contamination: we can quantify the contamination confound by estimating n-gram overlap between Pile/dedup-Pile and the benchmark test sets, using [Shi et al., 2023]'s min-k% method. If contamination rates differ between Pile and dedup-Pile (which they should, by construction), that difference itself is part of the mechanism.

**Key Points:**
- Core hypothesis: dedup-Pile models show category-differential improvement (knowledge > reasoning) relative to Pile models
- Mechanism: repeated factual patterns in Pile inflate knowledge benchmark performance via near-memorization
- Contamination quantification is a feature, not a confounder — differential contamination IS the mechanism
- Fully testable with existing Pythia checkpoints + lm-evaluation-harness + n-gram overlap tools

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's hypothesis is directionally interesting but has three critical flaws I want addressed before I'm satisfied.

**Flaw 1: The mechanism is circular.** "Deduplication reduces repeated factual patterns that inflate knowledge-benchmark performance" — but benchmark performance inflation via memorization should be *reduced* by deduplication, meaning dedup models should perform *worse* on contaminated benchmarks if memorization is what drives scores. Dr. Ally says dedup models "show disproportionate improvement on knowledge benchmarks" — but the mechanism predicts they should do *worse* on benchmarks whose test set overlaps with repeated training documents. The direction needs to be clarified: is deduplication revealing true generalization (dedup models better), or removing memorization scaffolding (dedup models worse on contaminated benchmarks but better at generalization)?

**Flaw 2: Confound with effective data volume.** Dedup-Pile has approximately 15% fewer tokens than Pile. This means dedup models are effectively data-starved. Any observed performance difference could be training data volume, not deduplication quality. This is a serious identification threat within the "controlled" within-family design.

**Flaw 3: No null hypothesis precision.** "No significant difference" is too vague. We need a specific null: dedup-Pile and Pile models at identical parameter count and training steps show no statistically significant difference in any pairwise benchmark comparison, using a Bonferroni-corrected threshold across 4 benchmarks.

What would convince me: a clear directional prediction with mechanism-consistent reasoning, explicit treatment of the effective-data-volume confound (e.g., comparing at matched token-count not matched step-count), and a pre-specified statistical test.

**Key Points:**
- Mechanism direction unclear: dedup should remove memorization scaffolding, not enhance it — explain the directional prediction
- Effective data volume confound: dedup-Pile has ~15% fewer tokens than Pile — this is a within-family confound
- Null hypothesis needs precision: specific statistical test with correction for multiple comparisons

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex has done exactly what I needed — those three critiques are all addressable and make the hypothesis substantially stronger.

**Addressing Flaw 1 — Mechanism Direction:** I was imprecise. The correct prediction is: dedup-Pile models perform *better* on benchmarks where Pile's test-set contamination is *lower* relative to the repeated documents removed. The mechanism is: Pile contains repeated near-duplicate documents, some of which overlap with benchmark test patterns. These repeated documents provide a memorization advantage on specific benchmarks. Deduplication removes this advantage. Therefore, dedup-Pile models will score *lower* on benchmarks with high Pile contamination, but *higher* on benchmarks where performance was not contamination-driven. The net pattern is a *reordering* of benchmark performance profiles, not uniform improvement. We measure both directions and the profile shift itself is the hypothesis.

**Addressing Flaw 2 — Data Volume Confound:** Excellent catch. The fix: compare Pythia models at matched *token count* rather than matched *training steps*. Pythia releases 154 intermediate checkpoints, so we can find the Pile checkpoint at N tokens that corresponds to the dedup-Pile final checkpoint at (approximately) N tokens. This controls for training data volume. Additionally, we can report both step-matched and token-matched comparisons as a robustness check.

**Addressing Flaw 3 — Null Hypothesis:** Revised null: At token-count-matched checkpoints, Pythia dedup-Pile and Pile models show no statistically significant difference in few-shot performance on any of {MMLU, HellaSwag, ARC, WinoGrande}, using Bonferroni-corrected α = 0.0125 (0.05/4). The alternative: at least one benchmark shows significant differential, with the direction predicted by estimated contamination overlap.

**Refined hypothesis:** Deduplication of pretraining corpora produces a *contamination-correction signature* in benchmark profiles — benchmarks with higher training-data overlap shift downward in dedup models, revealing performance that was memorization-inflated in non-dedup models. This signature is measurable without retraining using existing Pythia checkpoints with token-count matching.

**Key Points:**
- Mechanism corrected: profile reordering (not uniform improvement) driven by differential contamination removal
- Data volume confound addressed: token-count matching using Pythia's intermediate checkpoints
- Null hypothesis precisified: Bonferroni-corrected pairwise test across 4 benchmarks
- Hypothesis now predicts *direction per benchmark* tied to contamination estimates

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Now we're close to something I can endorse. Let me apply the convergence criteria formally.

**SPECIFIC** ✅ — Core claim: Deduplication in pretraining produces a contamination-correction signature in benchmark profiles — benchmarks with higher Pile training-data overlap shift downward in dedup-Pile models, revealing memorization inflation. Measured using Pythia checkpoints at token-count-matched comparison points.

**MECHANISM** ✅ — Causal chain: (1) Pile contains repeated near-duplicate documents that overlap with benchmark test patterns; (2) deduplication removes these documents, reducing near-memorization of test-pattern-adjacent content; (3) this produces per-benchmark performance changes proportional to contamination overlap magnitude; (4) the resulting profile shift (some benchmarks down, others relatively up) is the curation fingerprint.

**PREDICTIONS** ✅ — P1: Pythia dedup-Pile vs Pile at token-count-matched checkpoints shows statistically significant performance difference on ≥1 benchmark (Bonferroni α=0.0125). P2: The direction of change per benchmark correlates with estimated n-gram overlap between Pile and that benchmark's test set. P3: The cross-family comparison (Pythia vs OLMo) shows a consistent contamination-profile pattern predictable from Pile vs Dolma contamination estimates.

**NOVELTY** ✅ — "Contamination-correction signature" as a lens on deduplication effects is not in the prior literature. Prior work (Lee et al. 2022) reports aggregate performance effects; we predict and measure per-benchmark directional effects tied to quantified contamination estimates.

**FEASIBILITY** ✅ — Fully executable with: Pythia checkpoints (released), lm-evaluation-harness, n-gram overlap tools (google-research/deduplicate-text-datasets adaptable for overlap estimation), Shi et al. min-k% prob for contamination quantification. No new training, no human annotation.

**OBJECTIONS** ✅ — Architecture confound: addressed by anchoring on within-family. Data volume confound: addressed by token-count matching. Mechanism direction: clarified as profile reordering, not uniform shift.

**CONVERGENCE DECLARED.** This hypothesis is ready for Phase 2B structuring.

**Key Points:**
- All 6 convergence criteria met
- Hypothesis: contamination-correction signature in benchmark profiles from deduplication
- Fully falsifiable with existing artifacts
- Scope: within-family causal (Pythia); cross-family exploratory (vs OLMo)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "contamination-correction signature" framing is genuinely novel — prior deduplication work reports aggregate performance effects but doesn't predict or measure per-benchmark directional shifts tied to quantified contamination overlap. The curation fingerprinting concept opens a new research direction for analyzing deployed models without retraining.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The refined hypothesis makes precise, pre-specified directional predictions per benchmark, anchored to measurable contamination estimates. The token-count matching protocol addresses the data volume confound. The Bonferroni-corrected null hypothesis is specific enough to be falsified cleanly.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a genuine field need: post-hoc curation analysis for existing deployed models. As training budgets increase, controlled ablations become impractical — this provides a diagnostic framework. The result is actionable for practitioners choosing open-source models for domain-specific tasks.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All required tools exist: Pythia checkpoints (HuggingFace), lm-evaluation-harness, n-gram overlap tools, Shi et al. min-k% implementation. Token-count matching is feasible using Pythia's 154 intermediate checkpoints. No new benchmarks, no annotation, no new training runs. Technically and scientifically sound.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from 8 exchanges of rigorous debate is: **deduplication of pretraining corpora produces a contamination-correction signature in benchmark performance profiles**. Specifically, Pythia dedup-Pile models, compared to Pile-trained models at token-count-matched checkpoints, will show per-benchmark performance changes whose direction and magnitude correlate with estimated n-gram overlap between the Pile training corpus and each benchmark's test set. Benchmarks with high Pile contamination will show reduced scores in dedup models (memorization inflation removed); benchmarks with low contamination will show relatively stable or improved scores (better generalization from cleaner data). This profile reordering — not a uniform shift — is the characteristic curation fingerprint of deduplication.

The mechanism: Pile contains repeated near-duplicate documents that partially overlap with benchmark test patterns. Deduplication removes these documents, reducing the near-memorization advantage that inflates scores on contaminated benchmarks. The resulting signature is measurable using existing Pythia checkpoints, lm-evaluation-harness, and n-gram overlap estimation tools. A secondary exploratory analysis extends the contamination-profile framework to compare Pythia vs OLMo, where the prediction is that Dolma's more aggressive filtering produces a different contamination profile, detectable in the cross-family benchmark comparison. The full study requires no new training, no new benchmarks, and no human annotation — it operates entirely on existing open-source artifacts.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** The token-count matching requires finding appropriate intermediate Pythia checkpoints; if the checkpoint granularity doesn't permit precise token-count matching, residual volume differences remain as a confound.
- **Concern 2:** The contamination-direction prediction requires reliable contamination estimation for Pile vs specific benchmark test sets — if min-k% estimates are noisy, the correlation test loses power.
- **Mitigation Strategy:** For C1: report matched-token and matched-step results; if they diverge, treat the divergence as informative about volume effects. For C2: use multiple contamination estimators (n-gram overlap AND min-k% prob) and report consistency; if both point the same direction, confidence is higher.


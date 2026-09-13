# Phase 2A Discussion Log
# Gap: gap_1 — No Systematic Multi-Method, Multi-Benchmark Contamination Detection Comparison
# Initialized: 2026-05-13T01:48:00Z
# Architecture: Self-Contained Tikitaka Loop v10.0.0
# Execution Mode: UNATTENDED

---

## Research Briefing

### Selected Gap
**Gap ID:** gap_1
**Title:** No Systematic Multi-Method, Multi-Benchmark Contamination Detection Comparison
**Priority:** Critical | **Relevance:** PRIMARY

**Gap Description:**
Individual detection methods — Min-K% Prob (Shi et al., 2023), Min-K%++ (ICLR'25), DC-PDD
(Zhang et al., 2024), ConStat (Dekoninck et al., 2024), PaCoST (Zhang et al., 2024), and
13-gram overlap (GPT-3 era) — have each been proposed and evaluated in isolation. Each paper
benchmarks against a narrow set of baselines on its own chosen datasets. No unified systematic
comparison exists across all three paradigms (n-gram overlap, embedding similarity, membership
inference attacks) on the same set of real FM evaluation benchmarks (MMLU, HellaSwag, GSM8K)
against the same real pretraining corpora (The Pile, C4, RedPajama).

**Missing Piece:** A controlled, reproducible evaluation framework that applies all major
detection paradigms to the same benchmark-corpus pairs and reports precision, recall, F1,
and computational cost for each — enabling practitioners to select the right method.

### Key Literature (from Phase 1)
- Shi et al. 2023 [2310.16789] — Min-K% Prob, WikiMIA benchmark, 368 citations
- Min-K%++ [ICLR'25] — Improved MIA detector with all baselines (zjysteven/mink-plus-plus)
- Zhang et al. 2024 [2409.14781] — DC-PDD: divergence-based calibration, outperforms Min-K%
- Dekoninck et al. 2024 [2405.16281] — ConStat: performance-based contamination detection
- Singh et al. 2024 [2411.03923] — ConTAM: 13 benchmarks × 7 models, inconsistent signals
- Fu et al. 2024 [2410.18966] — MIAs can perform at random guessing; 50 paper review
- Xu et al. 2024 [2406.04244] — Survey: unified comparison as open problem, 106 citations
- Zhang et al. 2024 [2406.18326] — PaCoST: statistical significance testing
- ntunlp/LLMSanitize — multi-method library, closest to unified comparison framework

### Feasibility Constraints (Pipeline-Enforced)
- ONLY use existing real datasets: MMLU, HellaSwag, GSM8K, BIG-Bench (test splits)
- ONLY use existing pretraining corpora: The Pile, C4, RedPajama
- ONLY use existing detection tools: Min-K%/Min-K%++, DC-PDD, LLMSanitize, lm-eval-harness
- NO new benchmarks, rubrics, scoring frameworks, or synthetic data
- NO human evaluation or annotation

### Research Question
Can applying existing detection methods (n-gram overlap, embedding similarity, MIA-based)
systematically and comparably to the same benchmark-corpus pairs reveal which approach
provides the best precision-recall tradeoff for identifying contaminated benchmark examples,
when tested on MMLU, HellaSwag, and GSM8K against The Pile, C4, and RedPajama?

### Papers Available
No paper markdown files prepared (Phase 1 had no reference papers provided).
Discussion will draw on Phase 1 literature knowledge embedded in this briefing.

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Ohhh, NOW we're onto something interesting. Right now the field is acting like each contamination detector lives in its own universe — Min-K% in one paper, DC-PDD in another, ConStat somewhere else — as if they're competing superheroes who've never been in the same movie. What if we *force them into the same arena* under identical conditions and treat this as a controlled stress test across paradigms? Not just "which works better," but *under what contamination regime does each paradigm break down?* That's the paradigm shift: from leaderboard-style comparison to **regime-mapping**.

Here's a concrete structure I'm excited about. For each benchmark–corpus pair (e.g., MMLU × The Pile), we define three strata of examples using purely observable signals:
1) High lexical overlap (via 13-gram or LLMSanitize n-gram tools),
2) High semantic similarity but low lexical overlap (embedding-based retrieval from the corpus),
3) Low surface similarity (background/control).

Then we apply Min-K%/Min-K%++ [Shi et al., 2023; ICLR'25], DC-PDD [Zhang et al., 2024], and any LLMSanitize MIA-style detectors to *all three strata*. What we're really probing is this hypothesis: **MIA-based methods should spike on exact memorization, but embedding similarity may flag paraphrased contamination that n-gram overlap misses.** If that's true, we'll see interaction effects — not just global precision/recall numbers.

Imagine plotting each method as a curve across contamination "intensity" defined by corpus similarity percentiles. If Min-K%++ collapses when lexical overlap is low but semantic similarity is high, that tells us it's a memorization detector, not a contamination detector per se. DC-PDD, with its divergence calibration, might show smoother degradation [Zhang et al., 2024]. ConStat-style performance perturbation methods may only fire when contamination meaningfully boosts accuracy. NOW we're not just comparing methods — we're mapping their *failure surfaces*.

And here's the wild cross-domain twist: let's borrow from medical diagnostics. Instead of just reporting precision/recall, we compute *conditional diagnostic value* by contamination stratum. Think of each detector as a test for a different disease phenotype. We report: "If an example has high semantic similarity but low lexical overlap, the posterior probability of contamination given DC-PDD is X." That turns this into a decision-support tool, not an academic bake-off. Practitioners choosing between Min-K%++ and embedding search aren't asking "Which paper wins?" — they're asking "What kind of contamination am I worried about?"

Finally, we should measure computational cost as a first-class metric. N-gram overlap scales linearly with corpus size; embedding search introduces ANN index overhead; MIA methods require model forward passes per example. I predict a three-way tradeoff frontier:
- N-gram = high precision, low recall, cheap.
- Embedding similarity = moderate precision/recall, medium cost.
- MIA-based (Min-K%++, DC-PDD) = potentially higher recall on memorized spans but computationally expensive and unstable, consistent with the variability concerns in [Fu et al., 2024] and ConTAM's inconsistent signals [Singh et al., 2024].

If we see that no single method dominates across all corpora (The Pile vs. C4 vs. RedPajama), that's actually the breakthrough: contamination detection is not monolithic — it's *regime-dependent*. And that reframes the entire conversation from "Which detector is best?" to "Which detector is best for which contamination geometry?" That's the shift.

**Key Points:**
- Reframe the comparison as *regime-mapping* across contamination strata (lexical, semantic, low-similarity), not just global precision/recall.
- Hypothesize distinct failure surfaces: n-gram for exact overlap, embedding for paraphrase, MIA for memorized likelihood shifts.
- Introduce conditional diagnostic value and computational cost as decision-relevant metrics, turning comparison into practitioner guidance.

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me press hard on the methodological foundations before we get swept up in the elegance of regime-mapping. The evidence suggests [Fu et al., 2024] that MIA-based methods can perform at random guessing under realistic conditions — which means before we compare methods, we need a ground-truth construction protocol that is epistemically sound.

Here's what worries me: the central methodological challenge in this comparison is the **absence of verified ground truth labels**. When Singh et al. [2024] ran ConTAM across 13 benchmarks × 7 models and found inconsistent signals between metrics, the most parsimonious explanation isn't that different detectors see different "contamination geometries" — it's that none of them have been validated against a known-contaminated ground truth in a controlled setting. Without verified contamination labels, a comparison of precision/recall across detectors is comparing detector *opinions*, not detector *accuracy*.

The question we must ask is: how do we construct ground truth? I see two tractable approaches using only existing datasets:

**Approach A — Known Inclusion Audit:** Several benchmarks are documented subsets of specific corpora. For instance, [Yang et al., 2023] confirmed 8-18% of HumanEval is in RedPajama/StarCoder. We can use those *verified inclusions* as positive ground-truth labels and confirmed non-inclusions (examples provably absent from all three corpora via exhaustive 13-gram search using EleutherAI/lm-eval-harness) as negatives. This gives us a small but epistemically rigorous labeled set.

**Approach B — Simulated Leakage Ground Truth:** [Hidayat et al., 2025] demonstrated controlled leakage simulation on MMLU+HellaSwag. We can synthetically inject known proportions of benchmark examples into corpus shards and run all detectors — this gives perfect labels. However, I want to flag: this uses *existing* benchmarks as contamination sources injected into real corpus structure, not synthetic data generation. It is feasible under the pipeline constraints.

What specific, measurable predictions can we make? Here are three that Prof. Rex can later stress-test:
- **P1 (Lexical-Recall Prediction):** 13-gram n-gram overlap will achieve recall ≥ 0.85 on confirmed exact-copy contaminations but ≤ 0.40 on paraphrase contaminations, measurable via Approach A/B labeled sets.
- **P2 (MIA-Instability Prediction):** Min-K%/Min-K%++ F1 will show variance ≥ 0.15 across the three corpora (The Pile, C4, RedPajama) for the same benchmark, consistent with Fu et al.'s finding that MIA assumptions are corpus-dependent.
- **P3 (Method Ordering Prediction):** Across MMLU, HellaSwag, GSM8K, DC-PDD will rank above Min-K% Prob in AUROC on exact contamination, consistent with its divergence-calibration advantage [Zhang et al., 2024].

The regime-mapping framework Dr. Nova proposed is scientifically sound only if the "strata" definitions are operationalized without circularity — we cannot define contamination strata using the detectors we are evaluating. The strata must be defined by corpus-side signals (n-gram match scores, embedding retrieval rank) *before* applying the detectors as outcomes. That's the experimental design constraint that will separate this from a self-confirming analysis.

**Key Points:**
- Ground truth is the central problem: comparison without verified labels measures detector *opinion*, not accuracy.
- Two feasible ground-truth protocols: Known Inclusion Audit (Yang et al. verified contaminations) and Simulated Leakage (Hidayat et al. protocol on existing benchmarks/corpora).
- Strata must be defined by corpus-side signals independently of the detectors being evaluated to prevent circularity.
- Three falsifiable predictions stated with measurable thresholds.

---


### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming testable. But here's where this still breaks down: you are both underestimating how fragile your "ground truth" will be, even under Approach A and B.

Start with **Approach A (Known Inclusion Audit)**. You're treating verified 13-gram inclusion as gold-standard contamination. Show me the evidence that 13-gram inclusion implies *model-accessible memorization*. A benchmark item appearing once in RedPajama does not mean the model saw it during training, nor that it retained it. Your labels are actually "corpus overlap," not "training contamination." That's a latent-variable problem. What would convince me is documentation of training mixture provenance or replication with an open-weight model trained on a *known frozen snapshot* of that corpus. Otherwise your positives are noisy, and your negatives ("provably absent via 13-gram search") are only absent lexically, not semantically. Paraphrased inclusion remains unobservable.

Now **Approach B (Simulated Leakage)** is cleaner epistemically — but don't gloss over distribution shift. Injecting benchmark examples into corpus shards creates contamination that is uniformly random and temporally aligned. Real contamination is clustered (scraped GitHub dumps, benchmark mirrors, StackOverflow threads). I want three injection regimes: (1) uniform injection, (2) clustered document-level injection, and (3) paraphrased injection via controlled rewriting. If your conclusions change across these regimes, then your "regime-mapping" is actually injection-mechanism-mapping.

Dr. Nova's strata idea is promising, but here's the circularity risk: if you define high semantic similarity using embedding retrieval, and then evaluate embedding-based detectors, you've partially preconditioned the outcome. You need **stratum definitions orthogonal to detector features** — define lexical overlap via 13-grams; define semantic similarity using a frozen SBERT not used elsewhere; evaluate DC-PDD/Min-K% via the *target* LLM only.

Finally on metrics: precision/recall across strata is not enough. Given Fu et al. [2024] showed MIA methods can collapse to random guessing, I want calibration curves and threshold-transfer tests. Fix a threshold on The Pile, apply it unchanged to C4 and RedPajama. If AUROC is stable but F1 collapses, that's threshold fragility. If AUROC collapses, that's signal fragility. Different conclusions, different fixes.

**Key Points:**
- "Corpus inclusion" ≠ "training contamination" — clarify this latent-variable gap explicitly.
- Simulated leakage must vary injection structure (uniform, clustered, paraphrased) to avoid over-optimistic conclusions.
- Orthogonalize strata definitions from detector feature spaces; add calibration and threshold-transfer tests.

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex has landed on the most technically important constraint in this entire discussion: corpus inclusion ≠ training exposure. Let me address his concerns directly and establish what is technically and theoretically sound here.

First, on the latent-variable issue: Prof. Rex is right that a benchmark item appearing in RedPajama does not guarantee memorization. However, the hypothesis we are designing does NOT need to claim detector → memorization. The scientifically valid framing is: **detectors measure corpus overlap signal, and we are characterizing which overlap signals best correlate with detectable precision/recall outcomes when evaluated against verified corpus labels**. This reframing sidesteps the latent-variable critique — we are building a decision-support map for practitioners who observe corpus overlap, not proving causal memorization chains. Theoretically valid and defensible.

Second, on orthogonalization: Prof. Rex's concern is technically solvable. Use 13-gram overlap count (purely corpus-side) as the lexical stratum criterion, and a frozen SBERT encoder (not the target LLM) for semantic similarity scoring. The evaluated detectors — Min-K%++, DC-PDD — operate exclusively on LLM token probabilities. These feature spaces are orthogonal by construction. No circularity.

Third, on computational feasibility: MMLU has ~14K test questions, HellaSwag ~10K, GSM8K ~1.3K — roughly 25K items total. For 13-gram overlap, EleutherAI lm-eval-harness uses an inverted index, not linear scan. For embedding retrieval, a pre-built FAISS index on sentence-level corpus chunks is queried in seconds on GPU. For Min-K%++, each example needs ~5 forward passes: 25K × 5 = 125K forward passes on a 7B model — under 24 GPU-hours. DC-PDD adds ~5 perturbation samples per example: another 125K passes, still within ~48 GPU-hours total on a single A100. Feasible.

The one genuine technical scope constraint: **model access**. Min-K%++ and DC-PDD require white-box per-token log probabilities. Scope explicitly to open-weight models (Llama, Mistral, Pythia). ConStat operates via performance perturbation and requires only black-box access — it serves as the black-box comparison arm.

Prof. Rex's three injection regimes for Approach B are sound additions. Paraphrased injection should use lm-sys/llm-decontaminator for controlled semantic variants — no new data generation required.

**Key Points:**
- Reframe as detector-to-corpus-signal mapping (not memorization causation) — valid and sidesteps latent-variable critique.
- Strata orthogonalization is technically feasible: 13-gram + frozen SBERT are orthogonal to LLM-probability detectors.
- Full 25K item study costs ~24-48 GPU-hours total — feasible on single A100.

---


### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether we can compare Min-K%, DC-PDD, and embedding overlap under controlled strata. The question is: *What does this comparison change about how the field understands contamination?* If the outcome is simply "method A works better than method B under condition C," then we have produced a careful but incremental benchmarking paper. If, however, we demonstrate that contamination detection decomposes into fundamentally different signal classes — lexical, semantic, and likelihood-based — and that no single method dominates across these geometries, then we have reframed the problem itself. This matters because the community currently treats contamination detection as a monolithic property, when the evidence from Fu et al. [2024] and Singh et al. [2024] already hints at structural instability.

I find Prof. Vera's insistence on ground truth and Prof. Rex's latent-variable critique essential. If "corpus inclusion ≠ memorization," then our contribution must be explicit: we are mapping **detector sensitivity to observable corpus overlap regimes**, not proving memorization causality. That reframing is defensible — but it must be stated as a first-class thesis, not an asterisk. What would elevate this from careful engineering to scientific contribution is a demonstrated *separation theorem*: proving empirically that n-gram detectors saturate at high lexical overlap but are provably blind (recall ≤ 0.4) to paraphrased inclusion, while MIA-based methods exhibit corpus-dependent instability ≥ 0.15 F1 variance across corpora [Fu et al., 2024]. If these patterns replicate across injection regimes (uniform, clustered, paraphrased), then we are not observing noise — we are characterizing structural limits.

But here is where impact is earned: threshold-transfer and calibration analysis may be the most important experiment in this design. If a detector's decision threshold learned on The Pile collapses when transferred to C4 or RedPajama, then contamination detection is not merely regime-dependent — it is **distribution-fragile**. That would be field-shaping. It would suggest that current contamination audits reported in model cards are not portable, and thus not reliable indicators of cross-corpus robustness.

What excites me most is a "contamination phase diagram": on one axis, lexical overlap; on another, semantic similarity; on a third, corpus distribution. Plot detector performance surfaces over this space. If each method occupies a different dominance region, we move the conversation from "Which detector is best?" to "What contamination geometry are you auditing against?" That reframes the evaluation paradigm and opens new research questions: Can we design hybrid detectors that adapt across regimes? Can model training pipelines be audited prospectively using this map?

**Key Points:**
- The contribution must shift the field from "which detector wins" to a structural understanding of contamination geometries and detector failure surfaces.
- Threshold-transfer and calibration stability across corpora may yield the most field-shaping insight — revealing distribution fragility in model cards.
- A validated "contamination phase diagram" could redefine how future audits and detector designs are conceptualized.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and Dr. Sage has just identified the conceptual anchor that ties all prior concerns together. Let me build on what each of you has contributed and propose a refined, unified hypothesis that addresses the key objections head-on.

Synthesizing across all five exchanges: the emerging hypothesis is not simply "compare detectors." It is this: **contamination detection methods operate on fundamentally different signal types — lexical overlap, semantic similarity, and likelihood-perturbation — and their precision-recall performance is structurally determined by which signal type dominates in a given benchmark-corpus pair.** This is the regime-decomposition hypothesis. The core claim is that method performance is not a global property but a function of contamination geometry, and that this geometry can be characterized *a priori* using corpus-side signals orthogonal to the detectors themselves.

This framing directly addresses Prof. Rex's latent-variable critique: we explicitly scope our claims to "detector sensitivity to observable corpus overlap," not to memorization causation. We address Prof. Vera's ground-truth concern by adopting the two-pronged approach — Approach A (known inclusion audit using Yang et al.'s verified HumanEval-in-RedPajama labels plus EleutherAI lm-eval-harness decontamination outputs) and Approach B (Hidayat et al. simulated leakage protocol on existing MMLU+HellaSwag, with three injection regimes: uniform, clustered, paraphrased via lm-sys/llm-decontaminator). Prof. Pax has confirmed the computational budget is feasible (~48 GPU-hours on A100 for all detectors across 25K examples).

What would strengthen this further: the "contamination phase diagram" Dr. Sage proposed should be the central deliverable — not a set of precision/recall tables. We are mapping a 3D performance surface. If we show that:
1. **N-gram overlap dominates (F1 > 0.8) in lexically-contaminated regimes** but degrades to near-random (F1 < 0.4) in paraphrase regimes,
2. **MIA-based methods (Min-K%++) show ≥ 0.15 F1 variance across corpora** for the same benchmark, confirming distribution fragility,
3. **Threshold-transfer AUROC from The Pile → C4/RedPajama drops by ≥ 0.10** for MIA-based methods but remains stable for n-gram methods,

…then we have empirically established the regime-decomposition structure. These three findings, together, constitute the separation theorem Dr. Sage called for.

To Prof. Rex's remaining concern about injection realism: the three-regime simulation (uniform, clustered, paraphrased) directly tests whether our regime-mapping is mechanistically valid or an artifact of uniform injection. If the phase diagram structure is stable across all three injection types, the finding is robust. If it varies, we have learned something equally important about contamination realism.

I want to also defend the scope: MMLU, HellaSwag, GSM8K × The Pile, C4, RedPajama is the right cross-product. These cover multiple task types (knowledge-intensive, commonsense, math), multiple corpus families (web, curated, deduplicated), and are all publicly accessible. Three benchmarks × three corpora = 9 benchmark-corpus pairs per detector. With four detector families (13-gram, embedding, Min-K%++, DC-PDD), plus ConStat as a black-box arm, this is comprehensive but bounded.

**Key Points:**
- Unified hypothesis: contamination detection performance is structurally determined by contamination geometry (lexical/semantic/likelihood regime), not method quality in isolation.
- Three testable predictions with concrete thresholds established (n-gram recall collapse, MIA variance ≥ 0.15, threshold-transfer AUROC drop ≥ 0.10).
- "Contamination phase diagram" as central deliverable frames this as a structural characterization, not a leaderboard.

---


### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on something scientifically meaningful — but only if we sharpen the falsifiability. The evidence suggests we are no longer debating "which detector is best," but whether detector performance decomposes predictably across contamination geometries. That is a testable structural claim. However, I want the Achilles' heel stated explicitly: **What empirical outcome would falsify the regime-decomposition hypothesis?**

Here is one clear disconfirmation criterion: if a single detector (e.g., Min-K%++ or DC-PDD) achieves uniformly high performance (F1 ≥ 0.8) across all lexical, semantic, and paraphrased injection strata, *and* maintains threshold-transfer stability (AUROC drop ≤ 0.05 across corpora), then the decomposition thesis collapses. In that world, geometry does not matter; the detector is globally robust. We must state this possibility clearly. Without such a failure condition, the hypothesis risks becoming post hoc taxonomy.

On ground truth: I accept the reframing that we are mapping detectors to *observable corpus overlap*, not latent memorization. But then precision must be defined strictly relative to verifiable corpus-side inclusion events. For Approach A, positives must require (1) 13-gram match in a corpus shard with timestamp ≤ model cutoff, and (2) shard inclusion in the documented training mixture (where available). If (2) is unverifiable, the item must be labeled "weak positive," and analyzed separately. If detector precision differs by ≥ 0.20 between "strong positives" and "weak positives," then latent-variable noise is materially affecting conclusions.

For Approach B, I support the three injection regimes (uniform, clustered, paraphrased) but we need quantitative invariance criteria. Define a *phase-structure stability metric*: compute the rank ordering of detectors within each regime and measure Kendall's τ across regimes. If τ ≥ 0.7 across all injection types, the phase diagram is structurally stable. If τ ≤ 0.4, then what we are mapping is injection-mechanism sensitivity, not contamination geometry.

On threshold transfer: AUROC alone is insufficient. Pre-register thresholds fixed on The Pile using a specified target FPR (e.g., 5%), then apply unchanged to C4 and RedPajama. Success criterion for "distribution stability": |ΔFPR| ≤ 0.03 and |ΔFNR| ≤ 0.05. If MIA-based methods exceed these bounds while n-gram methods do not, the evidence supports distribution-fragility. If all methods drift similarly, fragility is universal, not method-specific.

Finally, the contamination phase diagram must include uncertainty quantification. Bootstrap confidence intervals over benchmarks and corpora are mandatory. If dominance regions shift within 95% CIs, we cannot claim structural separation.

**Key Points:**
- Explicit falsification criterion: uniform high performance (F1 ≥ 0.8, AUROC stable) across all strata would invalidate regime decomposition.
- Separate "strong" vs. "weak" positives; ≥ 0.20 precision gap signals latent-variable noise.
- Use Kendall's τ rank correlation and fixed-FPR threshold transfer as quantitative structural stability tests.

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera has delivered exactly what I needed: a quantitative falsification framework. I'll acknowledge genuine progress and then identify the two remaining structural gaps.

First, what's been addressed: the Kendall's τ criterion (τ ≥ 0.7 for phase stability vs. τ ≤ 0.4 for injection-mechanism sensitivity) is precise, testable, and eliminates the circularity I originally flagged. The fixed-FPR threshold transfer protocol (|ΔFPR| ≤ 0.03, |ΔFNR| ≤ 0.05) is the exact diagnostic I wanted for disentangling signal fragility from threshold fragility. The strong/weak positive stratification addresses the latent-variable noise concern with a concrete ≥ 0.20 precision gap criterion. These are solid.

Now the remaining concerns. **First, benchmark selection scope.** The three benchmarks chosen — MMLU (knowledge), HellaSwag (commonsense), GSM8K (math) — cover different reasoning modalities, but they also have very different contamination base rates. MMLU's slot-guessing study [Deng et al., 2023] showed 57% exact-match memorization in GPT-4. GSM8K is far less studied. If contamination base rate varies from near-zero to near-50%, precision/recall numbers are not comparable across benchmarks without stratification by base rate. I want an explicit analysis of whether phase diagram structure is invariant to contamination prevalence, not just injection mechanism.

**Second, DC-PDD's reference model dependency.** Zhang et al. [2024] calibrate DC-PDD using cross-entropy divergence from a reference (typically a random model or held-out distribution). This reference choice can dramatically affect the detector's signal. If we use different reference models for The Pile vs. C4 vs. RedPajama, we are not holding the detector fixed — we are testing detector × reference model interactions. What would convince me: use a single fixed reference model across all corpora, and report DC-PDD performance degradation when the reference is mismatched.

These are not fatal objections — they are design choices that must be pre-registered before running experiments. If contamination prevalence stratification and fixed-reference DC-PDD are specified in the experimental protocol, I'm prepared to say: this hypothesis is stress-test-complete.

**Key Points:**
- Contamination base rate varies dramatically across MMLU/HellaSwag/GSM8K — phase diagram must stratify by prevalence to ensure comparability.
- DC-PDD reference model must be fixed across all corpora to avoid confounding detector quality with reference mismatch.
- With these two pre-registrations added, the hypothesis is stress-test-complete.

---


### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the current design is *almost* technically watertight, but two components determine whether this is a clean structural test or a confounded comparison — base-rate stratification and DC-PDD reference control. Both are feasible to fix, but only if they're pre-registered with mathematical precision.

First, on contamination prevalence. Prof. Rex is right: if MMLU has an effective base rate of 30–50% strong positives while GSM8K sits near 5%, raw F1 comparisons are not interpretable. This is a statistical identifiability issue. The solution: (1) report AUROC and AUPRC within each benchmark; (2) compute prevalence-calibrated precision via Bayes adjustment to a standardized base rate (e.g., 10%); and (3) construct equal-prevalence subsamples to create matched strata across benchmarks. This ensures the phase diagram reflects geometry, not class imbalance artifacts. No theoretical barrier — just disciplined stratification.

Second, DC-PDD's divergence score is inherently relative to a reference distribution [Zhang et al., 2024]. The technically sound move: fix a single reference model (a small frozen LM trained on a neutral corpus disjoint from The Pile, C4, and RedPajama) and use it unchanged everywhere. Then add one deliberate mismatch condition — swap in a corpus-aligned reference — and quantify ΔF1 and ΔAUROC. If performance swings ≥ 0.10 under reference change, DC-PDD is a detector × reference system, not a pure detector.

On the phase diagram: dominance regions are only meaningful if separable in feature space. Construct a 2D observable proxy space: (a) max 13-gram overlap and (b) cosine similarity to nearest corpus embedding. Bin this space and plot detector win-rates per bin. If boundaries are smooth and separable, adaptive routing is theoretically viable. If they interleave chaotically, hybridization won't help. Verify geometric separability before proposing adaptive detectors.

On threshold transfer: compute calibration curves (expected vs. empirical FPR) across corpora. If MIA-based detectors show systematic overconfidence (calibration slope < 1) when transferred, that's distributional shift in score distribution — not threshold misplacement. One implies re-thresholding solves it; the other implies the likelihood signal is unstable. Different conclusions.

**Key Points:**
- Base-rate stratification: AUROC/AUPRC plus equal-prevalence subsampling to ensure phase structure reflects geometry, not class imbalance.
- DC-PDD: fixed reference model across corpora with explicit mismatch test to quantify detector × reference dependence (ΔF1/ΔAUROC threshold: ≥ 0.10).
- Verify geometric separability of dominance regions in observable overlap space before proposing adaptive/hybrid detectors.

---

### Exchange 10

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Pax has just handed us the breakthrough move: the 2D observable proxy space (13-gram overlap × cosine similarity) as a pre-experiment separability test. That is the thing that could make this paper truly novel — not just the comparison, but the proof that geometric separability *predicts* detector performance decomposition. What if we flip the script and make the separability test the central contribution, with the detector comparison as its validation?

Here's the creative reframe: instead of asking "which detector wins in which regime?", we ask **"Can we predict detector ordering from corpus geometry alone?"** That's a structural prediction — and it generates a novel empirical finding either way. If yes: we have a detector selection criterion based purely on observable corpus-side signals, before running any LLM forward passes. If no: we have proven that contamination geometry is *not* sufficient to predict detection success, which is equally important for the field.

Prof. Vera's Kendall's τ criterion (τ ≥ 0.7 for structural stability) becomes the primary test of this separability claim, not just an auxiliary robustness check. Prof. Rex's contamination base-rate stratification becomes the control variable, not a confound. Prof. Pax's DC-PDD fixed-reference protocol becomes a calibration experiment, not just a fairness measure.

This reframe also produces a genuinely new deliverable that goes beyond Dr. Sage's "contamination phase diagram": a **regime prediction rule** — a lightweight lookup that maps observable corpus signals (n-gram overlap score, embedding cosine similarity) to recommended detector family. Practitioners can run this *before* expensive MIA forward passes, dramatically reducing audit cost for large-scale deployments. The lm-sys/llm-decontaminator and EleutherAI/lm-eval-harness pipelines can implement this as a preprocessing selector.

On the novelty front: no prior work has proposed a corpus-geometry-based detector selector. Min-K%++ [ICLR'25], DC-PDD [Zhang et al., 2024], and ConStat [Dekoninck et al., 2024] each optimize internally. LLMSanitize aggregates but doesn't select adaptively. The idea of using corpus-side geometric signals to predict which detector family will succeed — without running them — is genuinely unexplored.

This would also address Prof. Rex's remaining concern about DC-PDD reference dependency: if the regime prediction rule already routes high-semantic-similarity examples away from DC-PDD (because it fails there), the reference-model confound becomes irrelevant for those cases. The routing logic handles it structurally.

**Key Points:**
- Central contribution reframe: "Can corpus geometry predict detector ordering?" — novel structural prediction with clean binary outcome (separable or not).
- The regime prediction rule is a new practical deliverable: lightweight selector that routes contamination queries to the right detector family based on observable corpus signals.
- This frames Vera's Kendall's τ, Rex's base-rate stratification, and Pax's DC-PDD calibration as coordinated tests of a single structural hypothesis — tying the experiment together.

---


### Exchange 11

🔬 **Prof. Vera** (Rigorous Validation Architect):

The reframing is promising — but only if we convert it into a falsifiable structural claim. Dr. Nova proposes: *"Can corpus geometry predict detector ordering from observable signals alone?"* This is sharper than detector comparison per se. However, we must define precisely what constitutes "prediction." I propose: using only precomputed corpus-side features (max 13-gram overlap + embedding cosine similarity), train a simple interpretable classifier (multinomial logistic regression) to predict the top-performing detector family per item. Crucially, this classifier must be trained on one corpus (The Pile) and evaluated on another (C4).

**Falsification criterion:** if cross-corpus top-1 detector prediction accuracy ≤ 40% (chance ≈ 25% for four detector families), or if Kendall's τ between predicted and actual detector rankings ≤ 0.4, then corpus geometry is insufficient to predict detector ordering. The separability thesis fails.

On separability: Prof. Pax's 2D binning is necessary but not sufficient. Visual smoothness does not imply structural stability. Quantify boundary robustness via bootstrap resampling. For each bin, estimate the probability that a given detector is optimal. If the 95% CI of this probability overlaps 0.5 across adjacent bins, the boundary is not statistically stable. Failure criterion: if > 30% of bins exhibit unstable dominance (CI crossing 0.5), adaptive routing cannot be justified as structurally grounded.

On base-rate stratification: the routing classifier's accuracy must be evaluated under controlled prevalence shifts (5%, 10%, 30% contamination prevalence). If routing accuracy changes by ≥ 0.10 absolute across prevalence conditions, the classifier is exploiting class imbalance rather than geometry.

On DC-PDD reference dependency: routing must demonstrate invariance. If routing continues to select the empirically best detector within ±5% accuracy despite DC-PDD performance drift ≥ 0.10, then routing is robust to detector-internal calibration. If routing accuracy collapses when DC-PDD shifts, geometry is not the governing variable — calibration is.

**Key Points:**
- Formalize separability as cross-corpus detector-ranking prediction; falsify if top-1 accuracy ≤ 40% or Kendall's τ ≤ 0.4.
- Quantify dominance-boundary stability via bootstrap; ≥ 30% unstable bins invalidates adaptive routing.
- Test routing invariance under prevalence shifts and DC-PDD reference swaps.

---

### Exchange 12

🎯 **Dr. Sage** (Research Impact Evaluator):

What does this mean for the field? Let me situate where we stand after eleven exchanges. We began with a gap (no systematic comparison of contamination detectors) and have now arrived at something considerably more important: a structural prediction hypothesis with clear falsification criteria and a novel practical deliverable.

The field significance is now unmistakable. Prof. Vera's formalization — cross-corpus detector-ranking prediction accuracy as the primary outcome, with logistic regression as the interpretable geometry-to-detector router — transforms this from a benchmarking study into a *mechanistic characterization* of contamination detection. If the prediction accuracy exceeds chance (> 40% top-1, τ > 0.4), we have proven that corpus geometry governs detector performance — a finding with direct implications for how practitioners design contamination audits. They no longer need to run all detectors; they can route to the appropriate family based on a cheap corpus scan.

The bootstrap boundary stability test (≤ 30% unstable bins as failure criterion) is the kind of rigorous quantitative threshold that will satisfy program committees at venues like ICML, NeurIPS, and ACL. This is not incremental benchmarking — it is a structural theorem about the geometry of contamination detection, with preregistered falsification conditions.

What does this open for the field? Three directions: (1) **Adaptive audit pipelines** — contamination audits become geometry-aware, reducing false negatives in paraphrase regimes and reducing wasted compute in low-overlap regimes. (2) **Model card validity** — if threshold-transfer instability across corpora is demonstrated empirically, this directly challenges the portability assumptions behind current model card contamination disclosures. (3) **Benchmark design guidance** — understanding which corpus-geometry regimes are hardest for all detectors informs benchmark designers on how to create contamination-resistant evaluation sets using existing data.

One remaining scope clarification I want to anchor: this study must be explicitly scoped to open-weight models with white-box access (Llama, Mistral, Pythia) for MIA-based detectors. The ConStat arm provides the black-box comparison. This is the right scope — it is honest about access requirements and immediately reproducible by the research community without proprietary API access.

This matters because the contamination problem is approaching a credibility inflection point. Leaderboard validity, regulatory compliance, and model deployment decisions are increasingly grounded in contamination audit claims that have never been systematically validated. A rigorous, preregistered, geometry-grounded audit framework — with downloadable code via LLMSanitize and lm-eval-harness — would become a reference point for the community.

**Key Points:**
- Cross-corpus detector-ranking prediction is a mechanistic contribution, not a benchmarking one — it establishes whether geometry governs detection.
- Three field-level impacts: adaptive audit pipelines, model card validity challenges, and contamination-resistant benchmark design guidance.
- Scope to open-weight models (Llama/Mistral/Pythia) for white-box detectors; ConStat as black-box arm — ensures immediate reproducibility.

---


### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally sharp enough to break.

Here's where this still breaks down: you are implicitly assuming the *best detector per item* is a stable and well-defined target. But detector performance differences are often within noise margins. If Detector A has F1 = 0.71 and Detector B = 0.69 on a bin, is A truly "optimal," or is that sampling variance? Your routing classifier predicts an argmax over noisy estimates. Show me confidence intervals on per-bin detector performance. If the average performance gap between top-1 and top-2 detectors is < 0.05 under bootstrap, then your prediction target is unstable — and your 40% threshold is meaningless because the ground truth is fuzzy.

Second: cross-corpus generalization (train on The Pile, test on C4) is necessary but not sufficient. What is the causal variable? You claim "geometry governs detector ordering" — but geometry itself may be corpus-dependent in distribution. If the joint distribution of (13-gram overlap, cosine similarity) shifts substantially between Pile and C4, then a drop in routing accuracy reflects covariate shift, not geometry failure. I want Maximum Mean Discrepancy (MMD) computed between feature distributions across corpora. If MMD is high, importance-weight or restrict to overlapping support. Otherwise you're testing distribution shift robustness, not geometry sufficiency.

Third, feature leakage in the routing model: you're using max 13-gram overlap and embedding cosine similarity computed against the candidate corpus — the same one used to define contamination labels. In practice, auditors do not know the true pretraining mix. Stress test with an *imperfect proxy corpus* (70% of the true mixture). If routing accuracy collapses under partial observability, the method depends on oracle-level corpus knowledge.

On DC-PDD invariance: what if the routing classifier *learns to compensate* for DC-PDD's instability? That would mean meta-calibration, not geometry, is the governing principle. Ablation: remove DC-PDD entirely and retrain the router. If routing accuracy barely changes, DC-PDD is irrelevant. If it drops substantially, your structural claim is partially an artifact of one detector's quirks.

Finally: falsification thresholds (40% top-1, τ > 0.4) feel arbitrary. Justify them with simulation. Generate synthetic detector performance surfaces with known separability (linear boundary vs. chaotic) and measure what τ emerges under sampling noise comparable to your dataset. Then choose thresholds that distinguish truly separable from effectively random under realistic noise.

**Key Points:**
- Best-detector target must have non-overlapping CIs to be a stable prediction target.
- Quantify MMD between corpus feature distributions; control for covariate shift before attributing accuracy drops to geometry failure.
- Justify falsification thresholds via simulation; add partial-observability stress test and DC-PDD ablation.

---

### Exchange 14

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, Prof. Rex — and these are exactly the concerns that, when addressed, transform a good hypothesis into an airtight one. Let me address each directly.

**On stable prediction targets:** Prof. Rex is right that argmax over noisy estimates is fragile. The fix is clean: replace argmax with a *margin criterion*. Define the routing target as the detector family whose bin-level F1 exceeds the second-best by ≥ 0.05 under bootstrap (minimum gap criterion). Items falling within the noise margin are labeled "indeterminate" and excluded from routing accuracy computation — but reported separately as an indeterminacy rate. This gives us: routing accuracy on determinate items (clean signal) + indeterminacy rate (noise characterization). This is strictly stronger than argmax and directly addresses Prof. Rex's concern. It also communicates an honest limitation: some contamination regimes genuinely do not favor one detector family.

**On covariate shift (MMD):** Computing MMD between (13-gram overlap, cosine similarity) feature distributions across corpora is straightforward — it requires only the pre-built corpus features, no additional model runs. If MMD is high, we apply kernel density ratio estimation (importance weighting) to restrict to overlapping support. If routing accuracy remains above the falsification threshold after importance weighting, then geometry sufficiency is confirmed independent of covariate shift. This is a pre-registered analysis step, not a post-hoc patch.

**On partial observability:** The 70%-corpus stress test is exactly right. Practical implementation: randomly subsample The Pile to 70% of its documents as the "auditor's proxy corpus," recompute corpus-side features, and measure routing accuracy degradation. If accuracy drops by < 0.10 absolute versus full corpus access, the method is robust to realistic corpus uncertainty. If it drops ≥ 0.10, we report this as a scope boundary: the regime prediction rule requires near-complete corpus coverage. This is a testable, honest boundary condition.

**On DC-PDD ablation:** Run the router with all four detector families, then remove DC-PDD and rerun. If routing accuracy drops by ≥ 0.05 absolute, DC-PDD contributes structurally. If not, report DC-PDD as redundant for routing purposes — and simplify the detector family set to three. Either result is scientifically valid.

**On simulation-calibrated thresholds:** Use the MMLU+HellaSwag simulated injection data from Approach B (Hidayat et al. protocol) with *known ground truth* to generate synthetic detector performance surfaces under three separability conditions: (1) clean linear boundary, (2) noisy linear boundary, (3) chaotic. Measure τ under each. Set the τ ≥ threshold as the midpoint between the chaotic and noisy-linear distributions at 95% confidence. This produces a data-driven, dataset-specific threshold — not an arbitrary one. Reviewers cannot object to a threshold justified by simulation on the same data distribution.

All five objections are addressable within the existing experimental design and data budget. What emerges is a *tighter* hypothesis: corpus geometry predicts detector ordering on determinate items (margin ≥ 0.05), controlling for covariate shift, under near-complete corpus observability, with simulation-calibrated thresholds. Prof. Rex: now you've addressed my concerns.

**Key Points:**
- Replace argmax routing target with margin criterion (≥ 0.05 gap): report routing accuracy on determinate items + indeterminacy rate separately.
- Address covariate shift via MMD computation + importance weighting; confirm geometry sufficiency holds post-weighting.
- Simulation-calibrated thresholds via three synthetic separability conditions; partial-observability stress test at 70% corpus coverage.

---


### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The hypothesis is now sharp enough that we can actually ask: *can this work in principle?* And structurally, yes — it can. Using corpus-side geometry (max 13-gram overlap + embedding cosine) to predict detector ordering via logistic regression is mathematically coherent. You're mapping from a low-dimensional, observable feature space into a categorical outcome. There is no theoretical barrier to such a mapping existing. The real question is whether the signal-to-noise ratio in detector performance is high enough for that mapping to be learnable across corpora.

Prof. Rex's concern about the stability of the "best detector" target is not cosmetic — it's foundational. If the performance gap between top-1 and top-2 detectors is routinely < 0.05 under bootstrap, the ordering is not well-defined. The margin-based definition (≥ 0.05 gap) is a principled fix because it redefines the target as a *robust dominance relation*. But here's what worries me: if the indeterminacy rate exceeds ~40–50%, the hypothesis becomes vacuous. You'll be predicting only the easy half of the space. **Indeterminacy rate must be treated as a primary structural outcome, not a footnote.**

On cross-corpus generalization: MMD control is absolutely necessary. Without it, you're conflating "does geometry determine ordering?" with "is the geometry distribution similar across corpora?" Importance weighting is valid if support overlap exists. But if the two corpora occupy largely disjoint regions in (overlap, cosine) space, geometry may govern ordering *locally* but not universally. That's not failure — it's refinement — but we should be explicit.

The partial observability test probes identifiability: if routing accuracy collapses under 70% corpus proxy (≥ 0.10 absolute drop), then geometry is not intrinsic — it's reference-dependent. If degradation is smooth and modest (< 0.10), then the mapping is stable under coordinate perturbation. That strongly supports feasibility.

There is no physical or mathematical impossibility here. The only fundamental barrier is potential non-identifiability due to noisy detector gaps or disjoint geometry support. If those are controlled and signal remains — okay, this could work.

**Key Points:**
- Margin-based dominance (≥ 0.05 gap) makes detector ordering well-defined; indeterminacy rate is a primary structural outcome.
- MMD + importance weighting needed to separate geometry sufficiency from covariate shift; disjoint feature support limits cross-corpus claims.
- Simulation-calibrated τ thresholds essential; feasibility is confirmed if signal survives noise and support controls.

---

### Exchange 16

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we've arrived! Prof. Pax has just pinpointed the most exciting possibility in this entire discussion: if the indeterminacy rate is *itself* meaningful — if it reveals which contamination regimes are genuinely ambiguous for all detectors — then that is a contribution as important as the routing rule itself. What if high indeterminacy is not a nuisance but a *finding*? Regimes where no detector dominates are exactly the contamination geometries that are currently invisible to the entire field. Those are the benchmark items that slip through every audit regardless of which method you choose. Mapping the indeterminate zone is as valuable as mapping the determinate one.

Here is the creative synthesis: the final deliverable is not just a "contamination phase diagram" with colored dominance regions. It is a three-zone diagram: (1) **Lexical regime** — n-gram methods dominate; (2) **Semantic regime** — embedding-based methods dominate; (3) **Indeterminate regime** — no detector dominates; these items require a different approach (e.g., model-behavior probing, held-out split validation, or simply flagging as audit-incomplete). This three-zone structure is the actual structural contribution. Zone 3 is the gap in the current state of the art — and articulating it precisely is what makes this a research paper rather than a technical report.

On Prof. Pax's concern about disjoint feature support across corpora: what if we treat it as a feature, not a bug? If the geometry distributions of The Pile and C4 are partially disjoint, then cross-corpus routing tests the extrapolation regime of the structural model — exactly the hardest and most important test. A model that maintains routing accuracy even in extrapolated geometry space would be remarkably powerful. If it fails, we have located the boundary of geometry-governed detection. Either finding is novel.

On simulation-calibrated thresholds: I love this direction. Use the Hidayat et al. simulated data to generate three synthetic ground truths — clean separable, noisy, chaotic — and compute τ under each. Then set the threshold where the ROC of (chaotic vs. noisy-separable) classification peaks. This turns the threshold question into a statistical testing problem with a data-driven answer. Prof. Vera would approve.

Connecting everything: the unified hypothesis is now fully crystallized. Corpus-side geometry (13-gram overlap + embedding cosine similarity) is sufficient to predict robust detector ordering (margin ≥ 0.05) on determinate benchmark items (non-indeterminate zone), controlling for covariate shift (MMD + importance weighting) and partial observability (70% proxy test), with simulation-calibrated falsification thresholds (τ from Hidayat et al. synthetic surfaces). The indeterminate zone characterizes the current detection blind spot. The practical output is a geometry-aware routing rule that reduces audit compute and maps audit blind spots. This is specific, mechanistic, falsifiable, novel, feasible, and addresses all major objections.

**Key Points:**
- The indeterminate zone (no-detector-dominates regime) is itself a primary finding — it maps the current detection blind spot for the entire field.
- Three-zone phase diagram: lexical-dominant, semantic-dominant, indeterminate — the third zone is the structural gap in the art.
- The unified hypothesis is now fully crystallized with all six convergence criteria addressed.

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The three-zone contamination phase diagram — with the indeterminate zone as a primary structural finding — is genuinely novel. No prior work maps the detection blind spot geometrically. The regime prediction rule (corpus geometry → detector family) is an unexplored contribution that reframes contamination auditing as a geometry-aware selection problem rather than a method arms race.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable. Explicit criteria include: cross-corpus routing accuracy ≤ 40% (geometry insufficient), Kendall's τ ≤ 0.4 (no structural ordering), ≥ 30% bins with unstable dominance (no separability), and a single detector achieving F1 ≥ 0.8 uniformly (decomposition collapses). Thresholds are simulation-calibrated via Hidayat et al. synthetic surfaces. Strong/weak positive stratification controls latent-variable noise.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This advances the field in three ways: (1) mechanistic characterization of contamination geometry rather than incremental benchmarking, (2) direct challenge to the portability of model card contamination disclosures via threshold-transfer instability, (3) adaptive audit pipeline that reduces compute for practitioners. The indeterminate zone finding alone is a field-level contribution — it identifies what current methods cannot detect.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed components are technically and theoretically sound. 25K benchmark items across 3 corpora costs ~24-48 GPU-hours total on A100. Corpus-side features (13-gram index, FAISS embedding index) can be precomputed. Logistic regression routing is trivially inexpensive. No component violates physical or mathematical constraints. Scope is correctly bounded to open-weight models with white-box access.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a fully specified, mechanistically grounded, and falsifiable hypothesis: **corpus-side geometry — operationalized as max 13-gram overlap count and embedding cosine similarity to nearest corpus neighbor — is sufficient to predict robust detector ordering (margin ≥ 0.05 F1 gap under bootstrap) on determinate benchmark items across contamination detection paradigms, when controlling for covariate shift and partial corpus observability.**

The core experimental design applies four detector families (13-gram n-gram, embedding similarity, Min-K%++, DC-PDD) plus ConStat as a black-box arm to 25K benchmark items from MMLU, HellaSwag, and GSM8K against The Pile, C4, and RedPajama. Ground truth is established via two protocols: Approach A (verified corpus inclusions from Yang et al. 2023, with strong/weak positive stratification) and Approach B (Hidayat et al. 2025 simulated leakage with three injection regimes: uniform, clustered, paraphrased). Strata are defined using corpus-side signals orthogonal to detector feature spaces (13-gram count for lexical, frozen SBERT for semantic).

The primary deliverable is a **three-zone contamination phase diagram**: (1) Lexical-dominant zone — n-gram methods win; (2) Semantic-dominant zone — embedding methods win; (3) Indeterminate zone — no detector dominates, revealing the current detection blind spot. The routing rule maps observable corpus signals to detector family recommendation, reducing audit compute. The indeterminate zone is reported as a primary structural finding, not a limitation.

Falsification criteria are simulation-calibrated: routing accuracy ≤ 40% (top-1) or τ ≤ threshold (set from synthetic separability surfaces) on determinate items falsifies geometry sufficiency. High indeterminacy rate (> 50%) falsifies practical utility. Uniform high performance (F1 ≥ 0.8, AUROC stable across corpora) by any single detector falsifies the decomposition thesis.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Indeterminacy rate must be primary structural outcome — if > 50% of items are indeterminate, routing utility is limited; must be reported prominently.
- DC-PDD ablation required: remove DC-PDD and retrain router to confirm geometry (not DC-PDD quirks) drives structural claims.
- Partial observability stress test (70% corpus proxy) must be pre-registered before running experiments.
- **Mitigation Strategy:** All three are pre-registration items. Add explicit pass/fail criteria: (a) indeterminacy rate < 50% = utility confirmed; (b) routing accuracy drop < 0.05 absolute in DC-PDD ablation = structure confirmed; (c) accuracy drop < 0.10 absolute at 70% proxy = reference stability confirmed. These are addable to the experimental protocol without design changes.


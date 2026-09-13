# Phase 2A Discussion Log
## Gap: Systematic Cross-Benchmark Comparison of Entropy-Based UQ Signals for Hallucination Prediction

**Gap ID:** gap-1  
**Priority:** HIGH+PRIMARY  
**Workflow:** phase2a-dialogue v10.0.0 (Self-Contained Tikitaka Loop)  
**Mode:** UNATTENDED  
**Date:** 2026-05-11  

---

## Briefing Context

### Research Question
Can internal uncertainty signals (token probability distributions, semantic entropy, consistency-based self-evaluation) in pre-trained LLMs accurately predict hallucination occurrence on existing factual QA and multimodal benchmarks without additional training, human annotation, or new benchmark creation?

### Gap Description
No existing work systematically compares semantic entropy (Kuhn 2023), token-level entropy, and SelfCheckGPT-style consistency methods head-to-head on the same benchmark set under matched experimental conditions using the same LLMs. This makes it impossible to determine which UQ signal most reliably predicts hallucination.

### Key Papers Available
- Kuhn et al. (2023) "Semantic Uncertainty" (arXiv: 2302.09664) — semantic entropy on TriviaQA/NQ only
- Manakul et al. (2023) "SelfCheckGPT" (arXiv: 2303.08896) — consistency on WikiBio only
- Li et al. (2023) "HaluEval" (arXiv: 2305.11747) — benchmark (35K samples, QA/dialogue)
- Kadavath et al. (2022) "Language Models Know What They Know" (arXiv: 2207.05221) — P(True) calibration
- Xiong et al. (2023) "Can LLMs Express Uncertainty?" (arXiv: 2306.13063)

### Feasibility Constraints (MANDATORY)
- ❌ NO new benchmarks, rubrics, or scoring frameworks
- ❌ NO synthetic/generated data
- ❌ NO human evaluation or annotation
- ✅ ONLY test using existing real datasets (HaluEval, TriviaQA, NQ) and existing benchmarks
- ✅ Implementations exist: lorenzkuhn/semantic_uncertainty, potsawee/selfcheckgpt, RUCAIBox/HaluEval

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The research gap is beautifully clear: we have three competing families of uncertainty quantification signals — token-level entropy, semantic entropy [Kuhn et al., 2023], and sampling-consistency [Manakul et al., 2023] — and nobody has compared them head-to-head on the same LLM under controlled conditions on a shared benchmark like HaluEval. This isn't a gap at the margins; it's a gaping hole in the empirical foundations of the field.

Here's what excites me about the novelty angle: each of these methods was developed and evaluated on *different* benchmarks. Semantic entropy was tested on TriviaQA/NQ; SelfCheckGPT was tested on WikiBio. This creates a confound — we don't know if observed performance differences reflect genuine signal quality differences, or merely dataset characteristics. A controlled apples-to-apples comparison on HaluEval (which covers QA, dialogue, and summarization) would be genuinely new science.

I propose three unconventional angles: (1) A **signal efficiency analysis** — which UQ method achieves acceptable AUROC with the fewest additional samples or forward passes? SelfCheckGPT requires N stochastic samples while entropy-based methods need only one forward pass. (2) A **calibration-hallucination decomposition** — do entropy signals predict *calibration* (ECE) or *hallucination occurrence* (binary label on HaluEval)? These are not the same thing. (3) A **model-family interaction** — does semantic entropy maintain its advantage across LLaMA-2-7B, Mistral-7B, and LLaMA-2-13B, or is its superiority model-specific?

**Key Points:**
- No controlled cross-benchmark comparison exists — genuine empirical gap
- Confounded prior evaluations prevent knowing if semantic entropy is truly superior to token entropy
- Signal efficiency (compute cost vs. AUROC gain) is a practical novelty angle
- Model-family interaction could reveal whether semantic entropy is universally better or model-dependent

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises important points, but I want to sharpen the experimental design to ensure the comparison is actually falsifiable. The core problem with a "comparison study" as a hypothesis is that it can easily become underpowered or uninterpretable if not designed carefully.

Let me propose a concrete, testable hypothesis structure: **Semantic entropy achieves statistically significantly higher AUROC than token-level entropy and SelfCheckGPT-consistency for hallucination detection on HaluEval-QA, when applied to the same LLM (LLaMA-2-7B-chat) under matched inference conditions.** This is specific, measurable, and falsifiable. A null result (no significant difference) is equally informative.

For rigor, we need: (1) A **matched LLM setup** — all three methods applied to the same LLM with the same tokenizer, same temperature, same max_new_tokens. (2) **Statistical testing** — AUROC difference with bootstrap confidence intervals (N=1000 resamples) across HaluEval-QA's full evaluation set. (3) **Effect size reporting** — not just p-values but Cohen's d or actual AUROC deltas. (4) **Multiple comparisons correction** — if we test across multiple LLMs and datasets, Bonferroni or FDR control is needed.

The feasibility question: HaluEval-QA has ~10,000 QA pairs. SelfCheckGPT requires N=5-20 stochastic samples per question, making it computationally expensive. We need to define a **fixed compute budget** (e.g., 5 stochastic samples for SelfCheckGPT) so the comparison is fair. Without this, we're comparing methods with different computational costs, which confounds the interpretation.

**Key Points:**
- Hypothesis must specify: which UQ signal, which benchmark, which LLM, what statistical test
- Matched experimental conditions are essential — same LLM, same inference parameters
- Compute budget must be fixed for fair comparison between entropy (1 pass) and SelfCheckGPT (N passes)
- Bootstrap AUROC confidence intervals + effect size are required for credible results

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's operationalization is rigorous, but I want to evaluate whether this line of inquiry has sufficient *impact* to justify the research investment, and whether the hypothesis as currently framed will produce findings that move the field forward.

The significance question: If we confirm that semantic entropy outperforms token entropy and SelfCheckGPT on HaluEval-QA for one specific LLM, what does the community learn? It confirms what Kuhn et al. (2023) already suggested qualitatively — but on a different benchmark. That's useful but modest. The higher-impact finding would be to identify *when* each method fails and *why* — i.e., what properties of a question or LLM response cause each UQ signal to break down.

I want to reframe the hypothesis toward greater significance: **The relative ordering of UQ signals (semantic entropy > token entropy > consistency-based) for hallucination prediction on HaluEval-QA is preserved across three open-source LLMs (LLaMA-2-7B, Mistral-7B, LLaMA-2-13B), and this ordering is explained by each signal's sensitivity to semantic variation in multi-token responses.**

This framing matters because: (1) If the ordering is preserved across models → practitioners can confidently choose semantic entropy for deployment without model-specific tuning. (2) If the ordering breaks → the field needs method-selection guidelines. (3) The mechanistic explanation (sensitivity to semantic variation) provides actionable insight beyond just ranking.

The impact of a negative result is equally high: if token entropy matches semantic entropy on HaluEval-QA, that means the additional computational complexity of semantic clustering is unnecessary — a cost-saving insight for practitioners.

**Key Points:**
- Pure ranking study has limited impact without mechanistic explanation
- Cross-model stability of the ordering is high-impact: enables practical deployment guidance
- Mechanistic explanation (sensitivity to semantic variation) differentiates from a simple benchmark comparison
- Negative results (token entropy ≈ semantic entropy) are equally valuable — cost-saving insight

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this discussion in what's actually implementable within a realistic research timeline. The proposals from Dr. Nova, Prof. Vera, and Dr. Sage are all theoretically sound, but some elements introduce significant implementation complexity that could derail execution.

**Feasible elements:**
- Token-level entropy: trivially computed from `model.generate(output_scores=True)` → softmax → entropy. Single forward pass. Standard in HuggingFace Transformers.
- Semantic entropy: the `lorenzkuhn/semantic_uncertainty` repository is the official implementation. It requires NLI entailment for semantic equivalence clustering, which adds ~30% compute overhead but is well-tested.
- SelfCheckGPT: `potsawee/selfcheckgpt` is pip-installable. The BERTScore variant is most stable; NLI variant is more accurate but slower.
- HaluEval: `RUCAIBox/HaluEval` provides evaluation scripts. The QA subset has ~10K examples; for a compute-feasible experiment, a stratified sample of 2,000 examples is sufficient for stable AUROC estimates.

**Complexity concerns:**
- Dr. Sage's cross-model stability test (3 LLMs) triples inference cost. On a single A100, LLaMA-2-13B inference on 2,000 HaluEval-QA examples with SelfCheckGPT (N=5 samples) takes approximately 8-12 hours. Multiplied by 3 models = 24-36 hours of inference. This is feasible but must be planned.
- The "sensitivity to semantic variation" mechanistic analysis requires post-hoc clustering of response spaces — doable but adds implementation complexity.

**Recommended scope:** 2 LLMs (LLaMA-2-7B-chat + Mistral-7B-Instruct), 1 benchmark (HaluEval-QA, 2,000 examples), 3 UQ signals (token entropy, semantic entropy, SelfCheckGPT-BERTScore), SelfCheckGPT with N=5 samples fixed.

**Key Points:**
- All three UQ signals have public implementations — feasibility HIGH
- Recommended: 2 LLMs × 1 benchmark × 3 UQ signals to control inference cost
- SelfCheckGPT N=5 fixed budget is compute-feasible on single GPU
- HaluEval-QA 2,000-sample stratified subset is sufficient for stable AUROC

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent discussion. I want to synthesize what we've established and strengthen the hypothesis into its most defensible form before we proceed.

The convergence points from our discussion are:
1. **Confirmed gap**: No prior work compares all three UQ signals (token entropy, semantic entropy, SelfCheckGPT) on the same LLM under identical conditions on HaluEval-QA
2. **Agreed feasibility**: All implementations exist and are pip-installable; HaluEval-QA provides sufficient ground truth labels
3. **Agreed scope**: 2 LLMs, 2,000-sample HaluEval-QA subset, SelfCheckGPT N=5 fixed budget
4. **Agreed statistical design**: Bootstrap AUROC CI + effect size reporting

Here is the strengthened hypothesis:

**Under fixed-budget inference conditions on HaluEval-QA, if three UQ signals (token-level entropy, semantic entropy, SelfCheckGPT-BERTScore) are applied to the same open-source LLM (LLaMA-2-7B-chat and Mistral-7B-Instruct), then semantic entropy will achieve the highest AUROC for binary hallucination detection, because it captures semantic-level uncertainty that is invisible to token-level probability aggregation and does not require multiple stochastic samples.**

The mechanism is clear: token entropy aggregates raw logit variance, which is sensitive to surface-form variation (spelling, synonyms) but not semantic content. Semantic entropy clusters semantically equivalent responses before computing entropy, filtering surface noise. SelfCheckGPT measures cross-sample consistency, which is a proxy for semantic entropy but requires N forward passes.

The null hypothesis: There is no statistically significant difference in AUROC for hallucination detection across the three UQ signals on HaluEval-QA when applied to the same LLM.

**Testable predictions:**
- P1: Semantic entropy AUROC > Token entropy AUROC by ≥ 0.05 on HaluEval-QA (both LLMs, p < 0.05 bootstrap)
- P2: SelfCheckGPT-BERTScore AUROC is between token entropy and semantic entropy (intermediate performance)
- P3: The AUROC ranking order (semantic entropy > SelfCheckGPT > token entropy) is preserved across LLaMA-2-7B-chat and Mistral-7B-Instruct

**Key Points:**
- Hypothesis is specific, falsifiable, mechanism-grounded, and immediately testable
- All components (data, implementations, compute budget) are confirmed available
- Three testable predictions with clear success criteria
- Null hypothesis clearly stated for falsification

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I need to stress-test the hypothesis Dr. Ally just synthesized. Several critical concerns:

**Concern 1: HaluEval-QA label quality.** HaluEval labels are LLM-generated (by ChatGPT), not human-annotated. This means the "ground truth" hallucination labels have non-trivial noise. If label quality is low, the AUROC comparison becomes unreliable — we'd be measuring correlation with noisy labels, not true hallucination. *Mitigation:* Use only the QA subset (which has the highest ChatGPT annotation agreement), and acknowledge this limitation explicitly.

**Concern 2: Token entropy aggregation ambiguity.** "Token entropy" is underspecified. Do we mean: (a) mean entropy across all generated tokens, (b) entropy of the first token only, (c) sum of log-probabilities (log-prob score)? These produce meaningfully different AUROC values. The hypothesis must specify the exact aggregation method. *Mitigation:* Test all three aggregation strategies and report the best-performing one as the token entropy baseline.

**Concern 3: Semantic entropy NLI model dependency.** Semantic entropy clusters responses using an NLI model (typically DeBERTa-large). The quality of semantic clustering depends on which NLI model is used. If we use a weak NLI model, semantic entropy will underperform unfairly. *Mitigation:* Use the same NLI model specified in Kuhn et al. (2023) official implementation (microsoft/deberta-large-mnli).

**Concern 4: SelfCheckGPT variant selection.** SelfCheckGPT has three variants (BERTScore, NLI, n-gram). BERTScore is most stable but may not be the most powerful. If we pick the wrong variant, we underestimate SelfCheckGPT's actual capability. *Mitigation:* Report all three variants; use the best-performing as the comparison point.

**Residual risk:** If semantic entropy does NOT outperform token entropy by ≥ 0.05 AUROC, the result is a null finding. This is scientifically valuable (cost-saving insight per Dr. Sage) but must be framed carefully to avoid being seen as a negative result without contribution.

**Key Points:**
- HaluEval label noise (ChatGPT-generated) must be acknowledged as a limitation
- Token entropy aggregation method must be pre-specified to avoid post-hoc cherry-picking
- NLI model for semantic entropy must match official implementation (deberta-large-mnli)
- Report all SelfCheckGPT variants; use best-performing as comparison point

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's concerns are well-founded and actually *strengthen* the novelty angle. Let me incorporate them and add one more creative twist.

The HaluEval label noise concern (Concern 1) is real but turns into a feature: we can treat label quality as an *analysis variable*. HaluEval has three question types: QA (highest annotation reliability), dialogue (medium), and summarization (lowest). By reporting AUROC separately per question type, we can show how UQ signal quality interacts with annotation reliability. This is a new analysis no prior work has done.

For the token entropy aggregation ambiguity (Concern 2): I agree this must be pre-specified. I suggest reporting all three aggregation strategies (mean entropy, first-token entropy, mean log-prob) and using the best-performing as the token entropy baseline. This is methodologically clean and provides additional insight into which aggregation matters.

The multi-variant SelfCheckGPT analysis (Concern 4) adds novelty: we become the first paper to provide a systematic comparison of *all* SelfCheckGPT variants against semantic entropy and token entropy on HaluEval. This is a meaningful contribution to practitioners choosing between implementations.

**Revised scope:** 2 LLMs × HaluEval (3 question types analyzed separately) × 3 UQ signals (semantic entropy, token entropy [3 aggregations], SelfCheckGPT [3 variants]) = comprehensive comparison matrix. The paper writes itself.

**Key Points:**
- HaluEval question type stratification turns a limitation into an analysis opportunity
- Pre-specifying token entropy aggregation prevents post-hoc cherry-picking
- Comparing all SelfCheckGPT variants creates a practitioner-relevant comparison matrix
- The experiment now produces a rich multi-dimensional result, not just a single ranking

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The convergence is nearly complete. Let me verify the falsifiability criteria are satisfied.

**SPECIFIC:** ✅ Core claim clearly stated — semantic entropy achieves higher AUROC than token entropy and SelfCheckGPT on HaluEval-QA when applied to the same LLM under matched inference conditions.

**MECHANISM:** ✅ Explained — semantic entropy captures semantic-level uncertainty by clustering semantically equivalent responses via NLI, filtering surface-form noise that inflates token entropy's variance. Token entropy aggregates raw logit variance (surface-sensitive). SelfCheckGPT is a sampling-based proxy for semantic entropy but requires N forward passes.

**PREDICTIONS:** ✅ Three testable predictions with criteria:
- P1: Semantic entropy AUROC > token entropy AUROC by ≥ 0.05 (bootstrap CI, p < 0.05)
- P2: SelfCheckGPT performance is between token entropy and semantic entropy
- P3: Ranking order preserved across both LLMs

**NOVELTY:** ✅ First controlled comparison of all three UQ signal families on HaluEval under matched conditions. Additionally: first comparison of all SelfCheckGPT variants, and first stratification by HaluEval question type.

**FEASIBILITY:** ✅ All implementations public, HaluEval available, compute budget defined (2 LLMs × 2,000 QA samples × 5 SelfCheckGPT samples).

**OBJECTIONS:** ✅ Major concerns from Prof. Rex addressed (label noise → stratified analysis; aggregation ambiguity → pre-specified multi-strategy; NLI model → official deberta-large-mnli; SelfCheckGPT variant → all three reported).

**All convergence criteria satisfied.** The hypothesis is ready for Phase 2B.

**Key Points:**
- All 6 convergence criteria now met
- Hypothesis is specific, mechanistically grounded, falsifiable, novel, feasible, and objection-resistant
- Ready for Phase 2B structuring

---


## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis fills a genuine empirical gap — no prior work compares all three UQ signal families (token entropy, semantic entropy, SelfCheckGPT) on the same LLM under identical conditions. The additional novelty angles (question-type stratification, SelfCheckGPT variant comparison, token entropy aggregation analysis) elevate this from a simple replication to a comprehensive contribution. The mechanism explaining *why* semantic entropy should outperform (semantic-level vs. surface-level uncertainty) is theoretically grounded and new on HaluEval.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is fully falsifiable. P1 has a quantified threshold (≥ 0.05 AUROC difference, p < 0.05 bootstrap), P2 has a directional prediction (SelfCheckGPT intermediate), and P3 has a cross-model consistency prediction. The null hypothesis is clearly stated. Pre-specified token entropy aggregation strategy, NLI model choice (deberta-large-mnli), and SelfCheckGPT variants prevent post-hoc analysis artifacts.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Both positive and negative results are impactful: confirmation of semantic entropy's superiority provides practitioner guidance (choose semantic entropy for deployment); null result would show token entropy achieves equivalent performance at 1/N the compute cost — a major cost-saving finding. Cross-model stability result answers the practical deployment question. The study addresses a foundational assumption in the LLM reliability literature.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are available and tested: lorenzkuhn/semantic_uncertainty (official, HF Transformers), potsawee/selfcheckgpt (pip-installable, 3 variants), RUCAIBox/HaluEval (evaluation scripts included). Fixed compute budget (2 LLMs × 2,000 QA examples × SelfCheckGPT N=5) is achievable on a single GPU in under 48 hours total. No new benchmark creation, no human annotation, no synthetic data required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: Under fixed-budget inference conditions on HaluEval-QA, if three families of uncertainty quantification signals — token-level entropy (with pre-specified aggregation), semantic entropy (Kuhn 2023), and SelfCheckGPT-BERTScore (Manakul 2023) — are applied to the same open-source LLM (LLaMA-2-7B-chat and Mistral-7B-Instruct), then semantic entropy will achieve the highest AUROC for binary hallucination detection, because it captures semantic-level uncertainty that token-level entropy cannot see (surface-form noise) and achieves this in a single forward pass unlike SelfCheckGPT which requires N stochastic samples.

The causal mechanism has three steps: (1) LLMs generate token probability distributions that contain both surface-form and semantic uncertainty; (2) token entropy conflates both, making it a noisy predictor; semantic entropy filters surface noise via NLI clustering, isolating the semantically meaningful uncertainty signal; (3) this cleaner signal provides better discrimination between hallucinated and factual responses on HaluEval-QA labels.

The experiment requires 2 LLMs, 2,000 stratified HaluEval-QA examples, 3 UQ methods (including all SelfCheckGPT variants), and bootstrap statistical testing with effect size reporting. The study is immediately executable with existing public resources and produces practitioner-relevant guidance on which UQ signal to use for LLM reliability monitoring.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- HaluEval labels are ChatGPT-generated (not human-annotated) — introduces systematic label noise; addressed via QA-subset focus and explicit limitations reporting
- Token entropy aggregation produces multiple valid candidates — addressed via pre-specified multi-strategy testing with best-performing as baseline
- Semantic entropy NLI quality is deberta-large-mnli dependent — addressed by using official Kuhn 2023 implementation verbatim
- Cross-model generalizability limited to 2 LLM families (LLaMA-2, Mistral) — addressed by framing as preliminary evidence, not universal claim
- **Mitigation Strategy:** All concerns are addressed via pre-registration of analysis choices, explicit limitations section, and scope-bounded claims. Null hypothesis is scientifically framed as a positive contribution.

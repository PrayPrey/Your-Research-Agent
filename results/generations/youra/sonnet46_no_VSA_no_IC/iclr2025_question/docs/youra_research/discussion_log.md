# Phase 2A Discussion Log
**Gap:** Gap 2 — Systematic Comparison of Token-Level Uncertainty Aggregation Strategies Without Fine-Tuning
**Gap ID:** gap-2-token-aggregation
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Execution Mode:** UNATTENDED
**Date:** 2026-08-21

---

## Briefing Context

**Research Gap:** No existing study isolates max vs. mean vs. sum token log-prob aggregation as the sole variable on fixed factual QA benchmarks using frozen models. Individual methods (CCP, EPR, SE) each use different aggregation strategies but never ablate aggregation in isolation.

**Available Papers:**
- P1: Fadeeva et al. 2024 (CCP) — mean aggregation baseline; lm-polygraph suite
- P2: Farquhar et al. 2023 (Semantic Entropy) — sum aggregation within clusters; AUROC on TriviaQA/NQ
- P3: Manakul et al. 2023 (SelfCheckGPT) — probability-based baselines in repo (max/mean)
- P4: Lin et al. 2021 (TruthfulQA) — standard benchmark; binary truth labels

**Available Repos:**
- IINemo/lm-polygraph (★480): implements max/mean/sum token UE methods + benchmark suite
- potsawee/selfcheckgpt (★628): probability-based-baselines.ipynb with max/mean
- jlko/semantic_uncertainty (★411): AUROC/AURAC evaluation pipeline

**Feasibility Constraints:**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- Only existing real datasets and existing benchmarks

### Previous Failure / Routing Context
No previous failure contexts — first Phase 2A attempt.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we reframe the entire token aggregation question as a *signal geometry* problem? Every aggregation function — max, mean, sum, geometric mean — is really making a claim about where in the sequence the hallucination signal lives. Max says: "the riskiest token tells you everything." Mean says: "risk is uniformly distributed." Sum says: "longer answers accumulate more risk." Geometric mean says: "risk is multiplicative, not additive." NOW — the beautiful thing is that none of these claims has ever been tested in isolation, because every paper either picks one strategy and defends it as a whole system, or proposes something clever like CCP or EPR that bypasses the basic question entirely.

What I find genuinely exciting is that the answer might be benchmark-dependent. TruthfulQA is full of short confident wrong answers — there the *min* log-prob (worst-case token) might dominate. TriviaQA has longer factual answers — there *mean* might outperform. This means we could discover something unexpected: **no single aggregation function is universally optimal**, and the optimal choice reveals something fundamental about the *structure of hallucination in different task types*.

The research question becomes: does aggregation function choice interact with benchmark characteristics (answer length distribution, question type, domain) in a systematic way? If yes, we've discovered a new axis of variation in LLM reliability research that nobody has mapped. That's genuinely novel — it's not just "which is better" but "why is it better here and not there."

I'd start with 5 aggregation functions: max, min, mean, sum (length-normalized), geometric mean of log-probs. Run on 4 benchmarks × 3 model families × 5 functions = 60 conditions. Use lm-polygraph as the harness — it already has the code for most of these.

**Key Points:**
- Aggregation function = implicit claim about hallucination signal geometry in the sequence
- Hypothesis: optimal aggregation is benchmark-dependent, not universally fixed
- 5 functions × 4 benchmarks × 3 models = 60 conditions; lm-polygraph harness available
- If interaction exists, we've mapped a new fundamental axis in LLM reliability research

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's signal geometry framing is evocative, but we need to be precise about what we're measuring before we get excited about interactions. Let me identify the critical methodological requirements.

First, the aggregation functions must all be computed from *the same token probability sequence* — meaning we need white-box access (log-probabilities). This immediately scopes us to models where logprobs are accessible: open-weights (LLaMA-2, Mistral-7B, GPT-2) or API endpoints with logprob support. GPT-3.5 via OpenAI API does return logprobs, but GPT-4 does not. We must be explicit about this boundary.

Second, the evaluation metric matters enormously. AUROC measures ranking ability but not calibration. AURAC (Area Under Risk-Coverage curve) measures selective prediction quality. PRR (Prediction Rejection Ratio) measures how much accuracy improves when you reject uncertain predictions. These are NOT interchangeable — a method that ranks well (high AUROC) may still give poor calibration. For Gap 2 specifically, AUROC is the right primary metric because we're testing whether aggregation *ranks* hallucinated vs. non-hallucinated correctly, not whether it's calibrated.

Third — and this is the critical falsifiability point — the null hypothesis must be sharp: *H0: All aggregation functions produce identical AUROC distributions across benchmark-model combinations.* We can test this with a Friedman test (non-parametric, paired across conditions) or a linear mixed-effects model with aggregation function as fixed effect and model×benchmark as random effects. If we can't reject H0, the research claim collapses.

The specific, measurable prediction I'd require: **max log-prob will achieve AUROC ≥ mean log-prob on TruthfulQA (short, confident wrong answers), while mean log-prob will achieve AUROC ≥ max log-prob on TriviaQA (longer, factual answers).** That's the minimal directional prediction that would make this interesting.

**Key Points:**
- Logprob access required: open-weights or GPT-3.5 API (not GPT-4); scope must be declared
- Primary metric = AUROC (ranking ability); secondary = AURAC (coverage-accuracy)
- Null hypothesis: H0 = all aggregation functions produce identical AUROC; testable via Friedman test
- Directional prediction: max wins on TruthfulQA (short answers), mean wins on TriviaQA (long answers)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this contribution mean for the field, and why hasn't it been done?

The reason it hasn't been done is actually instructive. The field moved too fast toward complex methods (CCP, EPR, SE) because researchers rightly suspected that raw aggregation functions were insufficient. But in doing so, they skipped the baseline characterization step. This is a reproducibility and foundations gap — the kind that review papers identify in hindsight as "we built sophisticated methods on an uncharacterized foundation."

The significance is threefold. First, *computational cost*: max/mean/sum token log-probs require a single forward pass, no sampling. If any of them achieves AUROC comparable to SelfCheckGPT (which requires N=20 samples, each a full generation), that's a 20× inference cost reduction for hallucination detection. This matters enormously for deployment. Second, *interpretability*: knowing that max log-prob correlates with hallucination means the model's uncertainty is concentrated at a single bottleneck token — that's a mechanistic finding. Third, *the benchmark interaction* Dr. Nova raised: if aggregation function × benchmark type interactions exist, this informs how practitioners should choose uncertainty measures for different applications.

The contribution I'd frame for a paper: "We provide the first systematic ablation of token-level log-probability aggregation strategies for hallucination detection, establishing zero-parameter baselines that outperform/match sampling-based methods on short-answer benchmarks, at 20× lower inference cost." That's publishable at ACL or EMNLP as a short paper or findings paper.

One important scope clarification: this study addresses *existing benchmarks with binary factual labels* (TriviaQA, NQ, SciQ, TruthfulQA). It does NOT generalize to long-form generation, code generation, or summarization. That scope limitation must be explicit.

**Key Points:**
- Foundational gap: complex methods built before characterizing simple baselines — rare in ML, common in NLP
- Key impact: if max/mean/sum matches SelfCheckGPT → 20× inference cost reduction with zero parameters
- Mechanistic insight: which tokens carry hallucination signal (concentrated vs. distributed)
- Publishable framing: first systematic ablation; short paper at ACL/EMNLP findings

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what's technically sound here. The core mechanism — computing token log-probabilities and applying different aggregation functions — is theoretically valid. There's no physical or mathematical barrier. Token log-probs are well-defined quantities from the language model's output distribution. The aggregation functions (max, min, mean, sum, geometric mean) are all mathematically coherent operations on finite sequences of real numbers. So the basic feasibility is unambiguous: this CAN be done.

What worries me technically is the *tokenization confound*. Different models tokenize the same answer differently — "Paris" might be one token for GPT-2 but subword-tokenized differently for LLaMA. This means max log-prob picks the lowest-probability token, but the token granularity varies by model. When comparing across model families, we're not comparing apples to apples. The max log-prob of a LLaMA-2 response and the max log-prob of a GPT-2 response may correspond to different-sized semantic units. This is a real methodological threat to the cross-model generalization claim.

However — and this is important — within a single model, comparing aggregation functions is clean. The tokenization is fixed, so max vs. mean vs. sum are directly comparable within each model. The cross-model comparison is trickier but not impossible: normalize by vocabulary-size-adjusted entropy baselines, or restrict to character-level aggregation as a model-agnostic alternative.

The lm-polygraph framework already handles the within-model evaluation cleanly — it has token_entropy (sum), token_prob (product/geometric mean equivalent), and max_prob as separate UE estimators. Running them through lm-polygraph's benchmark pipeline on TriviaQA/NQ/TruthfulQA is literally a config change. This is exceptionally feasible technically.

**Key Points:**
- Core mechanism: mathematically valid; no fundamental barrier
- Real concern: tokenization granularity varies across model families → confound for cross-model claims
- Solution: primary analysis within-model; cross-model normalized by entropy baseline
- Exceptional technical feasibility: lm-polygraph already has all 5 aggregation methods as UE estimators

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly based on what the group has established. Let me synthesize and sharpen.

The core hypothesis is emerging clearly: **Among token-level log-probability aggregation functions (max, min, mean, length-normalized sum, geometric mean), computed from a single forward pass on frozen LLMs, the optimal function is determined by answer-length distribution of the benchmark, with max log-prob dominating on short-answer benchmarks (TruthfulQA, SciQ) and mean log-prob dominating on variable-length benchmarks (TriviaQA, NQ), because the max captures the single highest-uncertainty token (which is the hallucination bottleneck in short confident answers) while mean distributes the signal evenly (which is more informative when answers vary in length and the bottleneck token may not be consistently located).**

This is a specific, mechanistic, testable hypothesis — not just "which function is better" but WHY. The mechanism is the distributional mismatch between where hallucination signal concentrates (bottleneck token in short answers vs. distributed across tokens in long answers) and what each aggregation function captures.

Addressing Prof. Pax's tokenization concern: we keep within-model as primary analysis; cross-model is a secondary replication check with the caveat noted. Addressing Prof. Vera's methodological requirements: AUROC primary, Friedman test for significance, directional prediction stated in advance. Addressing Dr. Sage's scope concern: restrict to existing benchmarks with binary factual labels, explicitly exclude long-form generation.

The refined experimental design: 5 aggregation functions × 4 benchmarks × 2-3 open-weight models (LLaMA-2-7B, Mistral-7B, plus GPT-2 as lightweight baseline) × single forward pass = clean ablation. lm-polygraph runs this in ~hours on a standard GPU.

**Key Points:**
- Strengthened hypothesis: optimal aggregation = f(answer-length distribution), with specific directionality
- Mechanism: bottleneck token (short answers) vs. distributed signal (long answers)
- Tokenization confound addressed: primary = within-model; secondary = cross-model replication
- Implementation: lm-polygraph + 2-3 open-weight models + 4 existing benchmarks; single forward pass

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I say this to make it bulletproof, not to kill it.

**Concern 1: The directional prediction might be backward.** Dr. Ally predicts max dominates on short-answer benchmarks. But TruthfulQA questions are short *and* the wrong answers are confidently stated — meaning the model assigns HIGH probability to wrong tokens consistently across the sequence. In that case, the *mean* log-prob might actually be a better signal because the entire sequence is high-probability-but-wrong, not just one token. The max captures the single *least* confident token, not the hallucination bottleneck. On TruthfulQA specifically, I'd predict the opposite: mean wins because the hallucination is expressed as uniform high confidence across all tokens, not as a spike in one token.

**Concern 2: Length normalization conflates two things.** "Mean" log-prob = sum / length = length-normalized sum. But this means "mean" and "length-normalized sum" are the same function. The ablation needs to explicitly separate: (a) raw sum, (b) length-normalized sum (= mean), (c) max, (d) min, (e) geometric mean. That's really 4 distinct functions, not 5, and the current framing conflates (a)-(b).

**Concern 3: The AUROC comparison requires knowing the correct hallucination labels.** TriviaQA and NQ use exact-match or F1 against reference answers as the proxy for "factual." This is imperfect — an answer can be correct but paraphrased differently. The noise in labels limits how high AUROC can theoretically go, and this ceiling varies by benchmark. We need to acknowledge this and use the same label methodology as prior work (e.g., the exact splits used in Farquhar 2023).

What would convince me: (1) state the directional prediction for each benchmark separately, motivated by theoretical argument; (2) separate sum vs. mean clearly in the ablation; (3) use exactly the same benchmark splits and label methodology as Farquhar 2023 for direct comparability.

**Key Points:**
- Concern 1: TruthfulQA hallucination may be uniform high-confidence (mean wins), not single-token spike (max wins)
- Concern 2: Mean = length-normalized sum — these are the same function; clarify the function set
- Concern 3: Label noise ceiling varies by benchmark; use Farquhar 2023 exact splits for comparability
- Mitigation: state directional predictions per benchmark with theoretical justification; replicate Farquhar splits

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex has made the hypothesis better — dramatically better — and NOW we're onto something really precise!

The insight about TruthfulQA is crucial. TruthfulQA hallucinations are *imitative falsehoods*: the model confidently states something it "learned" that's wrong. That means all tokens in the answer carry the hallucination signal uniformly — the model doesn't waver. So mean log-prob captures that uniform high-confidence signal. On TriviaQA, the model may genuinely be uncertain about a specific fact-token (the entity name, the year) while being confident about surrounding words. There the max of *negative* log-prob (or equivalently, min log-prob) captures the bottleneck.

This gives us a crystal-clear theoretical framework: **hallucination type determines optimal aggregation**. Type A (imitative/overconfident hallucination) → mean wins. Type B (factual recall failure) → min log-prob (worst-case token) wins. TruthfulQA is predominantly Type A; TriviaQA/NQ are predominantly Type B.

On Prof. Rex's function clarity concern: let's define the 4 truly distinct functions explicitly:
1. **Min log-prob** (= max token uncertainty = worst-case token signal)
2. **Mean log-prob** (= length-normalized sum = average signal)
3. **Raw sum of log-probs** (= length-sensitive total; biased toward longer answers)
4. **Geometric mean** (= exp(mean log-prob) = same ranking as mean but in probability space; actually redundant with mean for ranking tasks)

So we really have 3 genuinely distinct signals for ranking/AUROC: min, mean, raw-sum. Geometric mean = monotone transform of mean → same AUROC. We can verify this analytically and drop it, or include it as a sanity check.

The hypothesis becomes more precise: **Min log-prob achieves higher AUROC than mean log-prob on factual recall benchmarks (TriviaQA, NQ) because hallucination concentrates at single uncertain fact-tokens; mean log-prob achieves higher AUROC than min on imitative-falsehood benchmarks (TruthfulQA) because hallucination is uniformly distributed across the sequence.**

**Key Points:**
- Hallucination type determines optimal aggregation: Type A (imitative) → mean; Type B (recall failure) → min
- Geometric mean = monotone transform of mean → same AUROC; reduces to 3 genuinely distinct functions
- Crystal-clear directional prediction: min > mean on TriviaQA/NQ; mean > min on TruthfulQA
- Theoretical grounding: hallucination mechanism (imitative vs. recall) explains aggregation preference

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we have now arrived at a hypothesis that meets my standards for testability. Let me formalize the complete prediction structure.

**Hypothesis H1:** Under frozen open-weight LLMs (LLaMA-2-7B, Mistral-7B-v0.1) evaluated on existing factual QA benchmarks with binary correctness labels, the token-level log-probability aggregation function that maximizes AUROC for hallucination detection differs by benchmark type: min log-prob achieves AUROC ≥ mean log-prob on factual recall benchmarks (TriviaQA, NQ), while mean log-prob achieves AUROC ≥ min log-prob on imitative-falsehood benchmarks (TruthfulQA).

**Null hypothesis H0:** All token-level aggregation functions (min, mean, raw-sum) produce equivalent AUROC distributions across benchmarks and models; any observed differences are within statistical noise.

**Testable predictions:**
- P1: On TriviaQA test split (Farquhar 2023 splits), min log-prob AUROC > mean log-prob AUROC by ≥ 0.02 for both LLaMA-2-7B and Mistral-7B-v0.1
- P2: On TruthfulQA generation subset, mean log-prob AUROC > min log-prob AUROC by ≥ 0.02 for both models
- P3: Raw sum log-prob AUROC is uniformly lower than both min and mean (because sum conflates uncertainty with answer length)

**Falsification:** If P1 and P2 do not hold — i.e., min and mean AUROC are within 0.02 of each other on all benchmarks — then the hypothesis that hallucination type determines aggregation choice is not supported, and aggregation function choice is practically irrelevant (also a useful finding).

**Statistical test:** Bootstrap confidence intervals (n=1000) on AUROC differences across benchmark splits; the Farquhar 2023 exact splits for TriviaQA/NQ ensure direct comparability.

All six convergence criteria are now addressable: SPECIFIC ✓, MECHANISM ✓, PREDICTIONS ✓, NOVELTY ✓ (first isolation of aggregation function as single variable), FEASIBILITY ✓ (lm-polygraph + open-weight models + existing splits), OBJECTIONS ✓ (Prof. Rex's concerns incorporated).

**Key Points:**
- H1: min log-prob wins on recall benchmarks; mean log-prob wins on imitative-falsehood benchmarks
- H0: aggregation functions statistically equivalent (null is meaningful — either outcome is useful)
- P1-P3: specific directional predictions with ≥0.02 AUROC threshold and bootstrap CI methodology
- All 6 convergence criteria met — ready for structuring

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hallucination-type-to-aggregation-function mapping is genuinely novel. No prior work has proposed that hallucination mechanism (imitative vs. recall failure) determines which token-level signal is optimal. This opens a new taxonomy of hallucination that has measurement implications — strong novelty claim.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has sharp directional predictions (P1-P3) with specific AUROC thresholds (≥0.02), a clear null hypothesis, bootstrap CI methodology, and exact benchmark splits (Farquhar 2023). The null itself is informative. This meets rigorous testability standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Two-fold significance: (1) if confirmed, provides a zero-parameter, single-forward-pass hallucination detector that matches or beats 20× costlier sampling methods for the right benchmark type; (2) the hallucination-type taxonomy opens new research directions in characterizing when simple vs. complex UQ methods are needed.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technically sound at every level — token log-probs are well-defined, aggregation functions are trivial to compute, lm-polygraph already implements all variants, open-weight models (LLaMA-2-7B, Mistral-7B) are publicly available, benchmark splits from Farquhar 2023 are reproducible. Single forward pass per example — no sampling overhead.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged is: **among token-level log-probability aggregation functions computed from a single forward pass on frozen open-weight LLMs, the optimal aggregation function for hallucination detection (measured by AUROC) is determined by the hallucination type characteristic of the benchmark.** Specifically, min log-prob (worst-case token uncertainty) is a superior hallucination signal on factual recall benchmarks (TriviaQA, Natural Questions) where hallucination concentrates at specific uncertain fact-tokens; mean log-prob (average token uncertainty) is superior on imitative-falsehood benchmarks (TruthfulQA) where hallucination manifests as uniform high confidence across the entire response.

The mechanism is grounded in how hallucination manifests: recall-failure hallucinations produce a single highly uncertain token (the specific entity/fact the model doesn't know), making the minimum log-prob a bottleneck signal; imitative-falsehood hallucinations produce uniformly high token probabilities across all response tokens (the model confidently recites a learned falsehood), making the mean a better distributed signal.

The experimental design uses frozen LLaMA-2-7B and Mistral-7B-v0.1, existing benchmark splits (Farquhar 2023 for TriviaQA/NQ, standard TruthfulQA generation subset), 3 aggregation functions (min, mean, raw-sum), single forward pass, and AUROC as primary metric with bootstrap confidence intervals. No new data, no new annotations, no new benchmarks required. Implementation via lm-polygraph ensures reproducibility. The finding is publishable as a short findings paper at ACL/EMNLP and directly useful to practitioners choosing uncertainty measures for deployment.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- SciQ is not clearly Type A or Type B hallucination — it may not show a clean signal for either aggregation function; could dilute the pattern
- The ≥0.02 AUROC threshold is somewhat arbitrary; should be justified by minimum practical significance for deployment decisions
- Raw-sum being universally worst is predicted but not theoretically guaranteed — a very short wrong answer could have lower sum than a long correct answer
- **Mitigation Strategy:** Treat SciQ as exploratory (not confirmatory); justify the 0.02 threshold by reference to deployment context (e.g., 2pp AUROC difference changes selective prediction coverage at typical thresholds); add length-controlled analysis for sum vs. mean comparison to isolate the length-conflation effect.


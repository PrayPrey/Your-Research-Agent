# Phase 2A Research Discussion Log

**Generated:** 2026-08-19
**Architecture:** Self-Contained Tikitaka Loop
**Mode:** UNATTENDED

---

## Research Briefing

### Selected Gap

**Gap ID:** Gap-1
**Title:** Optimal Combination of Token Entropy and Semantic Consistency
**Priority:** HIGH | **Relevance:** PRIMARY

**Problem Statement:**
Token-level entropy and semantic consistency methods exist separately for hallucination detection, but their optimal combination strategy remains unexplored. Semantic entropy (Kuhn et al., 2023) clusters responses by meaning before computing entropy, while SelfCheckGPT (Manakul et al., 2023) uses multi-sample consistency without entropy components. No systematic study combines both on the same benchmarks.

**Research Question:**
Can token-level entropy and semantic consistency measures predict factual hallucinations in LLM outputs on existing QA benchmarks without requiring model retraining or ensemble methods?

**Key Sub-Questions:**
1. Does token-level predictive entropy correlate with factual accuracy on TriviaQA/NQ?
2. Can semantic consistency detect hallucinations better than single-response confidence?
3. How do lightweight methods compare to expensive approaches (ensembles, MC dropout)?
4. What is the calibration quality of different uncertainty metrics?

### Related Papers

| Paper | Year | arXiv ID | Key Insight |
|-------|------|----------|-------------|
| Semantic Uncertainty (Kuhn et al.) | 2023 | 2302.09664 | Semantic clustering + entropy, not combined with consistency |
| SelfCheckGPT (Manakul et al.) | 2023 | 2303.08896 | Consistency only, no entropy component |
| LMs Know What They Know (Kadavath et al.) | 2022 | 2207.05221 | P(True) self-evaluation works |
| Can LLMs Express Uncertainty? (Xiong et al.) | 2023 | 2306.13063 | Benchmark evaluation framework |
| On Calibration of NNs (Guo et al.) | 2017 | 1706.04599 | ECE metric, temperature scaling |

### Available Resources

**GitHub Repos:**
- jlko/semantic_uncertainty (Semantic entropy implementation)
- potsawee/selfcheckgpt (Consistency detection)
- sylinrl/TruthfulQA (Hallucination benchmark)

### Feasibility Constraints (Pipeline-Enforced)

- MUST use existing real datasets and existing benchmarks
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data or future follow-up data
- NO human evaluation, annotation, or subjective scoring

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this all wrong? Everyone treats entropy and consistency as separate uncertainty signals, but what if they're actually measuring *complementary failure modes* of LLMs? Entropy captures the model's internal confusion — when it doesn't know what token to generate next. Consistency captures semantic instability — when the model "knows" an answer but can't reliably reproduce it.

Here's my wild idea: these aren't just two metrics to average together. They're probing *different layers of the hallucination problem*. High entropy + high consistency might mean "the model is uncertain but stable in its uncertainty" (honest ignorance). Low entropy + low consistency could mean "confident but incoherent" (dangerous hallucination). The *interaction* between entropy and consistency might be more predictive than either alone!

Looking at Kuhn et al.'s semantic entropy work, they cluster by meaning before computing entropy — but they never ask whether responses that cluster together are *consistently wrong* or *consistently right*. And Manakul's SelfCheckGPT measures consistency without asking *how confidently* the model produced each sample. What if we compute consistency *conditional on* entropy levels? Or entropy *within* semantic clusters?

**Key Points:**
- Entropy and consistency may probe different hallucination failure modes
- The *interaction* (entropy × consistency) could outperform linear combination
- Conditional metrics (consistency given entropy level) are unexplored
- Semantic clustering + consistency scoring is a novel combination

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your intuition about interaction effects is intriguing, but let me stress-test it. For this to be scientifically valid, we need precise operationalization. What *exactly* would we measure, and what result would prove us wrong?

First, let's pin down the variables. Independent variable: uncertainty metric type (token entropy alone, consistency alone, linear combination, interaction term). Dependent variable: hallucination prediction accuracy (AUROC on TriviaQA/NQ where ground truth is known). We need controlled variables too — model size, sampling temperature, number of samples for consistency estimation.

The critical question: what's our falsification criterion? I propose: if the interaction model (entropy × consistency) doesn't improve AUROC by at least 2 percentage points over the best single metric with p < 0.05, we reject the interaction hypothesis. This is testable on existing benchmarks immediately.

One concern: semantic entropy requires multiple samples per question anyway (for clustering). SelfCheckGPT also requires multiple samples. So the computational overhead is already paid. The real question is whether *how we combine the information* matters, not whether we collect it.

**Key Points:**
- IV: metric type (entropy, consistency, combination, interaction)
- DV: AUROC for hallucination prediction on TriviaQA/NQ
- Falsification: interaction model must beat single metrics by ≥2pp at p<0.05
- Both methods already require multi-sampling — combination adds no overhead

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what's actually achievable. The good news: this is technically sound and immediately testable. We're not proposing new model training, just combining existing post-hoc signals. Both semantic entropy and SelfCheckGPT have public implementations.

The mechanism is physically valid: entropy is computed from token logits (model output), consistency is computed from string/semantic similarity across samples. Combining them is just arithmetic. No fundamental barriers here.

However, I have a concern about the "interaction effect" framing. In my experience, interaction terms in ML often overfit. The hypothesis needs to be: does a *simple* combination (like weighted sum) work, or do we genuinely need a learned interaction? I'd recommend starting with the simplest combination — `score = α·entropy + β·consistency` — before introducing multiplicative terms.

The datasets are ready: TriviaQA has ~95K QA pairs with ground-truth answers, Natural Questions has ~300K. These provide binary correctness labels (model answer matches ground truth). No human annotation needed.

**Key Points:**
- Mechanism is technically sound — just arithmetic over existing signals
- Public implementations available for both methods
- Start with linear combination before interaction terms (avoid overfitting)
- TriviaQA/NQ provide ground-truth labels — no human eval needed

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask: why does this matter for the field? Let me position this contribution.

The significance hinges on one key insight: *we might be leaving predictive power on the table by treating uncertainty signals as independent*. If Dr. Nova's interaction hypothesis holds, it would mean the community has been suboptimally estimating hallucination risk. That's a meaningful contribution — not just incremental.

But we need to be careful. If the linear combination works just as well as interaction terms, the contribution becomes "entropy + consistency is better than either alone" — which is less surprising. The novelty claim must be precise: we're testing whether *how we combine* matters, not just *whether combining helps*.

For field impact, I see this opening two directions: (1) practical deployment — if combined metrics give better calibration, production LLM systems can flag unreliable outputs more accurately; (2) theoretical — understanding *why* interaction matters could reveal something about how LLMs fail.

Calibration quality is the key metric the community cares about. Not just AUROC (ranking), but Expected Calibration Error (ECE) — does our combined score actually correlate with probability of correctness?

**Key Points:**
- Core novelty: the *method of combination* matters (not just combination itself)
- If interaction terms win, we reveal the field has been suboptimal
- Two impact paths: practical (better deployment) + theoretical (failure modes)
- ECE (calibration) matters as much as AUROC (discrimination)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's converging and strengthen the hypothesis against Prof. Vera's concerns.

The core claim taking shape: **Combined token entropy and semantic consistency predict hallucinations better than either metric alone, and the combination method matters — interaction-aware fusion outperforms naive linear combination.**

Here's my defense of the interaction hypothesis, with evidence. Kuhn et al. (2023) show semantic entropy captures "meaning-level confusion." Manakul et al. (2023) show consistency captures "generation stability." These are *theoretically orthogonal* — one measures internal model state, the other measures output behavior. Orthogonal signals typically exhibit interaction effects when combined for prediction.

To address Prof. Pax's overfitting concern: we can use fixed interaction (entropy × consistency, no learned weights) rather than learned interaction. This eliminates overfitting risk while testing whether the interaction *structure* matters. If fixed interaction beats linear combination, no learning is involved.

The refined hypothesis with testable predictions:
- P1: Linear combination (α·entropy + β·consistency) outperforms best single metric by ≥2pp AUROC
- P2: Fixed interaction (entropy × consistency) outperforms linear combination by ≥1pp AUROC
- P3: Combined metric improves ECE (calibration) over single metrics

**Key Points:**
- Entropy and consistency are theoretically orthogonal → expect interaction
- Fixed interaction term avoids overfitting concerns
- Three testable predictions with clear success/failure thresholds
- Calibration (ECE) included alongside discrimination (AUROC)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and what would convince me.

First challenge: the 2pp AUROC threshold is arbitrary. What if existing methods already achieve 0.95 AUROC? Then 2pp improvement is nearly impossible due to ceiling effects. We need to state: "2pp improvement OR reaching ceiling (>0.97)" as success criterion.

Second challenge: "interaction outperforms linear combination" — but with how many hyperparameters each? If linear has 2 (α, β) and interaction has 3+ (α, β, γ for interaction term), we're comparing models of different complexity. Proposal: use held-out validation to tune all hyperparameters, report test set results. Or use BIC/AIC for fair comparison.

Third concern: dataset contamination. TriviaQA and NQ questions may be in LLM training data. If the model "memorized" answers, entropy might be artificially low. We should verify on TruthfulQA (designed to elicit false answers) as a robustness check, even though it's smaller.

What would convince me: (1) consistent improvement across all three datasets (TriviaQA, NQ, TruthfulQA); (2) interaction term selected by BIC/AIC over linear; (3) ECE improvement alongside AUROC.

**Key Points:**
- Ceiling effects: add ">0.97 AUROC" as alternative success criterion
- Fair comparison: use BIC/AIC or held-out validation for model selection
- Dataset contamination: verify on TruthfulQA as robustness check
- Convince me: consistent wins across datasets + model selection criteria

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex raises valid concerns, and I want to push one step further on the novelty angle before we converge.

What if the real insight is even simpler? Maybe we don't need interaction terms at all. Maybe the key finding is that entropy and consistency are *redundant* on easy questions but *complementary* on hard questions. The *conditional* combination — combining only when there's disagreement between signals — could be the actual innovation.

Think about it: on questions where entropy is high AND consistency is low, we're confident it's a hallucination. On questions where entropy is low AND consistency is high, we're confident it's correct. The ambiguous cases — where signals disagree — are where the magic happens. A simple decision rule: flag as uncertain only when signals conflict.

This reframes the hypothesis away from interaction terms toward *conditional complementarity*. It's simpler, more interpretable, and might work just as well.

**Key Points:**
- Simpler alternative: signals are redundant on easy cases, complementary on hard cases
- Decision rule: flag uncertainty only when entropy and consistency disagree
- More interpretable than interaction terms
- Still testable on same benchmarks with same metrics

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, the conditional complementarity framing is elegant, but it needs operationalization. Let me formalize it.

Define four quadrants based on median splits: (1) Low entropy + High consistency → Confident Correct; (2) High entropy + Low consistency → Confident Hallucination; (3) High entropy + High consistency → Uncertain but Stable; (4) Low entropy + Low consistency → Confident but Unstable.

The testable prediction: quadrant classification predicts correctness with higher accuracy than continuous metrics. Specifically, Q1 should have highest accuracy, Q2 lowest, Q3/Q4 intermediate. If Q3 and Q4 have *different* accuracy rates, it proves the interaction matters.

This is cleaner than regression with interaction terms. We can compute accuracy within each quadrant and test whether the 2x2 classification outperforms single-threshold decisions on entropy or consistency alone.

**Key Points:**
- Operationalize via 2x2 quadrant classification (median splits)
- Testable: quadrant membership predicts correctness better than single thresholds
- Q1 (low entropy + high consistency) should have highest accuracy
- Q3 vs Q4 accuracy difference proves interaction matters

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging on something strong. Let me formulate the final hypothesis.

**Core Hypothesis:** Token entropy and semantic consistency provide complementary signals for hallucination detection. Their combination — whether via linear fusion, interaction terms, or quadrant-based classification — outperforms either metric alone on QA benchmarks with ground-truth labels.

**Mechanism:** Entropy measures internal model uncertainty (token probability distribution); consistency measures external output stability (semantic similarity across samples). High entropy indicates the model "doesn't know" the answer; low consistency indicates the model "can't reliably generate" the answer. These failure modes are distinct and complementary.

**Predictions:**
- P1 (Primary): Combined metric (linear fusion) achieves ≥2pp AUROC improvement over best single metric on TriviaQA, or reaches ceiling (>0.97)
- P2: ECE (calibration error) improves by ≥0.02 with combined metric
- P3: Performance holds on NQ and TruthfulQA (robustness check)
- P4 (Exploratory): Quadrant-based analysis reveals distinct accuracy patterns, suggesting interaction structure

**Experimental Setup:**
- Datasets: TriviaQA (primary), Natural Questions, TruthfulQA (robustness)
- Model: Any instruction-tuned LLM with logit access (e.g., Llama-2-7B-chat)
- Metrics: AUROC, ECE, Accuracy within quadrants
- Baselines: Entropy alone, Consistency alone (SelfCheckGPT), Verbalized confidence

**Key Points:**
- Core claim: combination outperforms single metrics (testable immediately)
- Mechanism: entropy = internal uncertainty, consistency = output stability
- Primary prediction: ≥2pp AUROC or ceiling effect
- Robustness: test on three datasets

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is getting solid. My remaining concerns and how to address them:

1. **Baseline fairness:** Semantic entropy (Kuhn et al.) already uses multiple samples and clustering. If we compare "combined metric" using 10 samples versus "entropy alone" using 5, it's not fair. Fix: same number of samples (e.g., 10) for all conditions. Entropy alone uses samples only for entropy. Consistency alone uses samples only for consistency. Combined uses same samples for both.

2. **Ground truth validity:** "Correctness" on TriviaQA means exact match or F1 with reference answer. Some correct answers may be marked wrong due to paraphrase. Mitigation: use established evaluation metrics (exact match + F1 > 0.5 as correct) rather than inventing new ones.

3. **Model choice matters:** Results on 7B model may not transfer to 70B or API models. Acknowledge as limitation, don't claim generality from single model.

If the hypothesis survives: combined entropy + consistency predicts hallucinations better than either alone, validated on 3 benchmarks with fair baseline comparisons. That's a publishable finding.

**Key Points:**
- Sample fairness: same number of samples across all conditions
- Ground truth: use established exact match + F1 threshold
- Model scope: acknowledge single model as limitation
- If validated: publishable contribution

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The combination of entropy and consistency is genuinely unexplored despite both methods existing. The "complementary failure modes" framing — entropy as internal confusion, consistency as output instability — provides novel theoretical grounding. The quadrant-based analysis offers an interpretable lens the field hasn't applied.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear operationalization: AUROC ≥2pp improvement over best single metric, ECE improvement ≥0.02, validated on 3 benchmarks. Quadrant-based analysis provides mechanistic test. All metrics computable from existing benchmark labels. Falsification is straightforward.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If combination significantly outperforms single metrics, it reveals suboptimal practice in the field. Practical impact for LLM deployment (better hallucination flagging). Theoretical impact for understanding LLM failure modes. Opens research direction on uncertainty signal fusion.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Immediately testable with existing code (semantic_uncertainty, selfcheckgpt repos), existing benchmarks (TriviaQA, NQ, TruthfulQA), existing models (Llama-2-7B-chat with logit access). No new data collection, no human annotation, no model training. ~1-2 weeks implementation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is that token-level entropy and semantic consistency provide complementary signals for detecting factual hallucinations in LLM outputs. The core claim states: combining these two uncertainty metrics predicts hallucinations more accurately than either metric alone, as measured by AUROC on QA benchmarks with ground-truth correctness labels.

The proposed mechanism distinguishes two failure modes: entropy captures internal model uncertainty (the model's probability distribution over next tokens is flat, indicating it doesn't "know" the answer), while consistency captures output stability (whether the model generates semantically similar answers across multiple samples). High entropy signals the model is confused; low consistency signals the model cannot reliably produce an answer even if confident. These are theoretically orthogonal and should be complementary.

Key predictions: (1) A linear combination of entropy and consistency achieves ≥2pp AUROC improvement over the best single metric on TriviaQA, or reaches ceiling (>0.97); (2) Expected Calibration Error (ECE) improves by ≥0.02 with the combined metric; (3) Results replicate on Natural Questions and TruthfulQA; (4) Quadrant-based analysis (2x2 split on entropy/consistency) reveals distinct accuracy patterns per quadrant, confirming interaction structure.

Experimental approach: Use TriviaQA (primary), NQ, and TruthfulQA benchmarks. Model: Llama-2-7B-chat (instruction-tuned with logit access). Generate 10 samples per question. Compute token entropy from logits, semantic consistency via NLI or embedding similarity. Compare: entropy alone, consistency alone (SelfCheckGPT), linear combination (α·entropy + β·consistency), and quadrant-based classification.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Ceiling effects on high-accuracy benchmarks may mask improvements. Mitigated by including ">0.97 AUROC" as alternative success criterion.
- **Concern 2:** Model-specific results (7B) may not generalize to larger models or API-only access. Acknowledged as scope limitation.
- **Mitigation Strategy:** Validate on TruthfulQA (designed to elicit failures, no ceiling) and document model-specific scope clearly.

---

## Emerged Hypothesis Summary

### Core Statement
**Under** QA task conditions with pretrained instruction-tuned LLMs, **if** we combine token-level entropy and semantic consistency into a single hallucination prediction score, **then** prediction accuracy (AUROC) improves by ≥2pp over the best single metric, **because** entropy and consistency capture complementary failure modes (internal confusion vs. output instability).

### Hypothesis ID
H-EntropyConsistency-v1

### Causal Mechanism
1. **Token Entropy Measurement:** For each generated response, compute entropy from token logit distributions, indicating how "uncertain" the model was during generation.
2. **Semantic Consistency Measurement:** Generate N samples for same question, compute pairwise semantic similarity (embedding cosine or NLI), average to get consistency score.
3. **Signal Combination:** Combine entropy (inverse) and consistency into unified score via linear fusion or quadrant classification.
4. **Hallucination Prediction:** Unified score predicts correctness; evaluate against ground-truth labels from benchmark.

### Variables
**Independent:** Combination method (entropy-only, consistency-only, linear fusion, quadrant-based)
**Dependent (Primary):** AUROC for hallucination prediction; **Secondary:** ECE (calibration), accuracy by quadrant
**Controlled:** Model (Llama-2-7B-chat), samples per question (10), temperature (0.7), evaluation metric (exact match + F1>0.5)

### Key Assumptions
- A1: Token entropy is accessible (model provides logits)
- A2: Semantic similarity captures "meaning equivalence" adequately
- A3: Ground-truth labels in benchmarks are reliable
- A4: Entropy and consistency are sufficiently uncorrelated to provide complementary signal
- A5: Results generalize across question difficulty levels

### Null Hypothesis
H0: There is no significant difference in AUROC between the combined metric and the best single metric (entropy or consistency alone). Statistical test: paired bootstrap or McNemar's test, α=0.05.

### Predictions
- P1 (Primary): Combined metric achieves ≥2pp AUROC improvement over best single metric on TriviaQA (or >0.97 AUROC)
- P2: ECE improves by ≥0.02 with combined metric
- P3: Results hold on NQ and TruthfulQA (robustness)
- P4 (Exploratory): Quadrant analysis shows Q1 (low entropy + high consistency) has highest accuracy, Q2 (high entropy + low consistency) has lowest

### Novelty
Prior work treats entropy and consistency as separate approaches. This is the first systematic study of their combination on standard QA benchmarks. The "complementary failure modes" theoretical framing is novel.

### Scope & Boundaries
**Applies to:** Instruction-tuned LLMs with logit access, factual QA tasks with ground-truth labels
**Does not apply to:** Open-ended generation without ground truth, API-only models without logit access
**Limitations:** Tested on single model family (Llama-2-7B); results may not transfer to other architectures

### Experimental Setup
- **Dataset:** TriviaQA (primary), Natural Questions, TruthfulQA
- **Model:** Llama-2-7B-chat (HuggingFace)
- **Baselines:** Token entropy alone, Semantic consistency alone (SelfCheckGPT), Verbalized confidence
- **Implementation:** Combine jlko/semantic_uncertainty + potsawee/selfcheckgpt

### Related Work & Baselines
- Kuhn et al. (2023): Semantic entropy — AUROC ~0.75-0.85 on closed-book QA
- Manakul et al. (2023): SelfCheckGPT — no published AUROC on TriviaQA/NQ (consistency only)
- Xiong et al. (2023): Verbalized confidence — calibration benchmark

### Phase 2B Readiness Seeds
- **SH1 (Existence):** Logit-based entropy and multi-sample consistency can be computed for any question
- **SH2 (Mechanism):** Combined score is more predictive than single scores
- **SH3 (Comparison):** Deferred to Phase 5 (compare against ensemble methods if needed)

### Established Facts
- Token entropy correlates with model uncertainty (BUILD_ON)
- Semantic clustering improves over token-level entropy (BUILD_ON, Kuhn et al.)
- Multi-sample consistency detects hallucinations (BUILD_ON, Manakul et al.)
- Calibration (ECE) is measurable on QA benchmarks (BUILD_ON, Guo et al.)
- Combination strategy is unexplored (PROVE_NEW)


# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap1-entropy-vs-consistency
**Gap Title:** No Systematic Comparison of Entropy vs. Consistency Methods on Same Benchmark

**Research Question:** Can token-level entropy and semantic consistency measures predict factual hallucination on QA benchmarks without model retraining?

**Current State:** Semantic entropy (Kuhn 2023) evaluated on NLG benchmarks; SelfCheckGPT (Manakul 2023) evaluated on WikiBio generation. No unified comparison on same factuality benchmark.

**Missing Piece:** Standardized head-to-head evaluation of token entropy, semantic entropy, and consistency methods on TruthfulQA/Natural Questions with identical models.

**Key Papers:**
- Kuhn et al. 2023 - Semantic Uncertainty (arXiv 2302.09664) - meaning-based entropy
- Manakul et al. 2023 - SelfCheckGPT (arXiv 2303.08896) - consistency detection
- Lin et al. 2022 - TruthfulQA (arXiv 2109.07958) - factuality benchmark
- Kadavath et al. 2022 - LMs Know What They Know (arXiv 2207.05221) - LLM calibration

**Available Resources:**
- lorenzkuhn/semantic_uncertainty - semantic entropy implementation
- potsawee/selfcheckgpt - consistency methods
- sylinrl/TruthfulQA - evaluation benchmark

**Feasibility Constraints (Pipeline-Enforced):**
- MUST use existing real datasets and existing benchmarks
- CANNOT create new benchmarks, rubrics, or scoring frameworks
- CANNOT use synthetic/generated data
- CANNOT require human evaluation or annotation

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

This gap presents a beautiful opportunity! We have two paradigms — entropy-based UQ (Kuhn's semantic entropy) and consistency-based UQ (SelfCheckGPT) — that have never been directly compared on factuality benchmarks. What excites me most is the potential to discover whether these methods capture orthogonal signals.

What if entropy captures *model uncertainty about the answer* while consistency captures *stability of the generation process*? These could be fundamentally different phenomena! Imagine a model that's confident but unstable (low entropy, low consistency) — that's a very different failure mode than uncertain but stable (high entropy, high consistency).

The cross-domain connection I see: In physics, you distinguish between aleatory uncertainty (inherent randomness) and epistemic uncertainty (knowledge gaps). Could entropy map to epistemic uncertainty while consistency maps to something more like generation noise? If true, combining them could be far more powerful than either alone.

**Key Points:**
- Two UQ paradigms may capture orthogonal uncertainty signals
- Entropy = knowledge uncertainty; Consistency = generation stability
- Hybrid approach could outperform both individual methods

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing distinction, but we need to make this testable. What specific, measurable predictions distinguish "entropy captures epistemic uncertainty" from "consistency captures generation noise"?

Here's what I propose: On TruthfulQA, we compute both token entropy and N-sample consistency for each question. If they capture orthogonal signals, we should observe: (1) low correlation between entropy and consistency scores, and (2) a hybrid model outperforming both individual predictors of factual correctness. The null hypothesis is clear: entropy and consistency are redundant measures of the same underlying uncertainty.

For falsifiability: If Pearson correlation between entropy and consistency exceeds 0.7, or if the hybrid model's AUROC improvement over the best single method is <2%, we reject the orthogonality hypothesis.

Critical confound: Kuhn's semantic entropy requires clustering generated answers by meaning — this is expensive and may conflate the comparison. We should compare *token-level* entropy against consistency first, then add semantic entropy as a separate condition.

**Key Points:**
- Testable prediction: low correlation + hybrid improvement
- Null hypothesis: entropy and consistency are redundant
- Confound: semantic clustering adds complexity; start with token entropy

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask: Why does this comparison matter for the field? If we show entropy and consistency are orthogonal, what new research directions open?

This matters because practitioners currently choose UQ methods arbitrarily. A systematic comparison on TruthfulQA — a widely-cited benchmark — provides actionable guidance. If we demonstrate a hybrid outperforms both, every LLM deployment can immediately improve hallucination detection. That's significant.

But let me push on contribution vs. incremental work. Simply showing "method A beats method B on benchmark X" is incremental. The novelty must be *understanding why*. The orthogonality hypothesis (entropy = epistemic, consistency = generation noise) provides that understanding. If we validate this mechanistic explanation, we're not just benchmarking — we're advancing theory.

What new questions does this open? If the signals are orthogonal, we can ask: *Under what conditions does each method fail?* This opens research on specialized UQ for different hallucination types.

**Key Points:**
- Impact: Actionable guidance for practitioners
- Contribution: Mechanistic understanding, not just benchmark numbers
- Opens: Research on failure modes of different UQ methods

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in reality. Is the proposed mechanism scientifically sound?

Token entropy computation: Extract logits, apply softmax, compute H = -Σp log p. This is mathematically well-defined and computationally trivial. ✓

N-sample consistency: Generate N responses (N=5-10), embed each, compute pairwise cosine similarity. This requires N forward passes and embedding extraction. The mechanism is sound — embedding similarity captures semantic agreement. ✓

TruthfulQA has ~800 questions with ground truth labels. AUROC computation on this sample size gives reasonable statistical power (80% power to detect AUROC difference of ~0.05 with N=800). ✓

My concern: The orthogonality hypothesis assumes entropy and consistency capture *different* phenomena. But what if high consistency simply follows from low entropy (confident model → consistent generations)? We need to identify cases where they *diverge* — high entropy but high consistency, or low entropy but low consistency. These "discordant" cases are the key test.

The mechanism is feasible. The critical test is demonstrating discordant cases exist.

**Key Points:**
- Token entropy: mathematically trivial, ✓ feasible
- Consistency: N forward passes, embedding similarity, ✓ feasible
- Key test: existence of discordant cases (entropy-consistency divergence)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on Prof. Pax's insight about discordant cases — this is exactly what strengthens the hypothesis! Let me refine:

**Core Claim (Strengthened):** Token entropy and N-sample consistency capture partially orthogonal uncertainty signals. Their combination improves hallucination detection beyond either method alone, *specifically because discordant cases exist*.

**Mechanism Refinement:**
1. High entropy + high consistency = Model uncertain but generations cluster around same uncertain answer (epistemic uncertainty)
2. Low entropy + low consistency = Model confident but generations vary (generation noise)
3. These discordant patterns exist in non-trivial proportions on TruthfulQA

**Addressing Prof. Vera's concern:** We should measure the *proportion* of discordant cases. If >15% of questions show discordance (e.g., entropy rank differs from consistency rank by >50 percentile points), that validates orthogonality.

**Predictions (Revised):**
- P1: Correlation(entropy, consistency) < 0.5
- P2: Hybrid AUROC improves by >3% over best single method
- P3: >15% of questions are discordant cases

This makes the hypothesis stronger and more testable.

**Key Points:**
- Discordant cases are the key mechanistic test
- Proportion threshold (>15%) provides clear success criterion
- Three falsifiable predictions with specific thresholds

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me stress-test this refined hypothesis. Where does it break down?

**Concern 1: Correlation threshold too low.** Correlation <0.5 still allows substantial overlap. If correlation is 0.4, they share ~16% variance. Is that "orthogonal"? I'd push for <0.3 for a strong claim.

**Concern 2: AUROC improvement threshold.** 3% improvement sounds good, but what's the baseline? If single-method AUROC is 0.55, 3% is noise. If it's 0.75, 3% is meaningful. Define success relative to baseline: hybrid must achieve AUROC > max(entropy_AUROC, consistency_AUROC) + 0.03.

**Concern 3: What if discordant cases are just noise?** 15% discordance means nothing if those questions have 50/50 factual accuracy. Discordant cases must show *differential* predictive value — one method predicting correctly when the other fails.

**What would convince me:** Show that on discordant cases, the correct method (entropy when consistency fails, vice versa) achieves AUROC >0.6 while the wrong method is near 0.5. That proves complementary signal.

**Key Points:**
- Tighten correlation threshold to <0.3
- AUROC improvement must be additive over baseline
- Discordant cases need differential predictive value, not just existence

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex sharpens us beautifully! Building on the differential predictive value requirement — here's the refined picture:

We're not just comparing methods; we're discovering *when* each method works. The real novelty is a conditional recommendation: "Use entropy when X, use consistency when Y, use hybrid otherwise."

What if entropy excels on questions where the model has genuinely seen similar training data (confident zones), while consistency excels on out-of-distribution questions (uncertain zones)? This creates a principled selection rule.

**Revised Hypothesis:** Token entropy and N-sample consistency exhibit complementary predictive power for factual hallucination. On TruthfulQA, discordant cases (where methods disagree) show differential predictive value — each method achieves AUROC >0.6 on its "winning" subset while the other achieves ~0.5.

**Implementation Path:** 
1. Compute entropy & consistency for all TruthfulQA questions
2. Classify into concordant vs discordant subsets
3. Evaluate each method on its "wins" vs "loses"
4. Build hybrid: weighted ensemble based on concordance

This is executable with existing benchmarks, no new annotations needed. Pipeline-compliant!

**Key Points:**
- Novelty: conditional method selection, not just hybrid
- Mechanistic: entropy wins in-distribution, consistency wins OOD
- Pipeline-compliant: TruthfulQA + existing metrics, no human annotation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The orthogonality hypothesis with conditional method selection is genuinely novel. Prior work compared methods in isolation; we're proposing a principled framework for *when* each works. The entropy=epistemic, consistency=stability distinction has theoretical grounding.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clear predictions with numerical thresholds: correlation <0.3, hybrid AUROC +3% over baseline, discordant cases >15% with differential predictive value (AUROC >0.6 vs ~0.5). Each can be falsified with TruthfulQA results.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Actionable for practitioners (choose method based on conditions), advances understanding (why methods work differently), opens research directions (failure mode analysis, specialized UQ). Not just benchmarking — provides mechanistic insight.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All computations are standard: token entropy from logits, consistency from embeddings, AUROC from sklearn. TruthfulQA is public. No custom benchmarks or human annotation required. Can execute with a single GPU in hours.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Hypothesis:** Token-level entropy and N-sample consistency capture complementary uncertainty signals for LLM hallucination detection on factuality benchmarks.

**Core Statement:** Under closed-book QA conditions (TruthfulQA, Natural Questions), if we compute both token entropy and N-sample consistency for each response, then a hybrid detector combining both signals will outperform either method alone, because the methods capture orthogonal failure modes — entropy reflects epistemic uncertainty about the answer while consistency reflects generation stability.

**Mechanism:** (1) Token entropy high → model uncertain about answer content; (2) Consistency low → model generates semantically different answers across samples; (3) Discordant cases (high entropy + high consistency, or low entropy + low consistency) reveal complementary signals that improve detection.

**Predictions:**
- P1 (Primary): Hybrid AUROC exceeds max(entropy_AUROC, consistency_AUROC) by ≥3 percentage points on TruthfulQA
- P2: Pearson correlation between entropy and consistency scores is <0.3
- P3: On discordant cases (>15% of questions), each method achieves AUROC >0.6 on its winning subset

**Experimental Setup:** LLaMA-2-7B on TruthfulQA (~800 questions), N=5 samples for consistency, token entropy aggregated as mean over response. Baseline comparison: single-method entropy, single-method consistency, learned hybrid weighting.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Semantic entropy (Kuhn's method) not tested — may outperform token entropy and reduce orthogonality. Mitigation: Add semantic entropy as third condition if compute permits.
- **Concern 2:** Model scale effects unknown — results on 7B may not generalize to 70B. Mitigation: Note as limitation, suggest follow-up study.
- **Mitigation Strategy:** Start with token entropy + consistency comparison (core hypothesis). Add semantic entropy as extension if results are promising.


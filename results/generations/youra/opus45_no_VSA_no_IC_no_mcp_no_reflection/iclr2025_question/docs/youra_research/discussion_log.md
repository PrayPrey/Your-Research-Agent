# Phase 2A Discussion Log

## Briefing

**Gap ID:** Gap-1
**Gap Title:** No Systematic Head-to-Head Comparison of UQ Methods as Hallucination Detectors
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Context

The primary research question asks: Can uncertainty measures (entropy, semantic consistency) reliably distinguish hallucinated from correct outputs on factuality benchmarks?

**Current State:** Individual papers evaluate their own method; semantic entropy, P(True), SelfCheckGPT evaluated on different subsets, metrics, or models.

**Missing Piece:** Unified benchmark evaluation comparing token entropy, sequence entropy, semantic entropy, P(True), and self-consistency on identical data splits with same LLM.

### Reference Papers
- Kuhn et al. 2023 - Semantic Uncertainty (arXiv:2302.09664)
- Kadavath et al. 2022 - P(True) / LLMs Know What They Know (arXiv:2207.05221)
- Manakul et al. 2023 - SelfCheckGPT (arXiv:2303.08896)
- Lin et al. 2022 - TruthfulQA (arXiv:2109.07958)
- Li et al. 2023 - HaluEval (arXiv:2305.11747)

### Available Repos
- semantic_uncertainty (github.com/lorenzkuhn/semantic_uncertainty)
- selfcheckgpt (github.com/potsawee/selfcheckgpt)
- lm-evaluation-harness (github.com/EleutherAI/lm-evaluation-harness)

### Feasibility Constraints (Pipeline-Enforced)
- REJECT: New benchmarks, rubrics, or scoring frameworks
- REJECT: Synthetic/generated data or future follow-up data
- REJECT: Human evaluation, annotation, or subjective scoring
- ACCEPT ONLY: Hypotheses testable with existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap is clear: everyone claims their UQ method detects hallucinations, but nobody has put them in the same ring. Kuhn's semantic entropy beats token entropy on their split, Manakul's SelfCheckGPT works on their examples, Kadavath's P(True) shines on their internal data. But which actually wins on TruthfulQA or HaluEval when we control everything else?

Here's what excites me: **the comparison itself could reveal something deeper**. What if different UQ methods detect different *types* of hallucinations? Token entropy might catch low-confidence fabrications, while semantic entropy catches semantically inconsistent elaborations, and self-consistency catches contradictory claims. If true, the "best" method depends on hallucination type — not a universal winner, but a taxonomy.

**Key Points:**
- No controlled comparison exists despite 5+ proposed methods
- Opportunity: compare token entropy, semantic entropy, P(True), SelfCheckGPT on identical TruthfulQA/HaluEval splits
- Hypothesis angle: different UQ methods may be sensitive to different hallucination types

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting hypothesis about method-hallucination-type correspondence, but let me impose scientific rigor. Before we claim methods differ by hallucination type, we need three things:

1. **A fixed experimental protocol**: Same LLM (e.g., Llama-3-8B), same benchmark (TruthfulQA mc1/mc2, HaluEval), same samples, same compute budget for multi-sample methods.

2. **Clear falsification criteria**: If semantic entropy AUROC on TruthfulQA exceeds token entropy by >5 absolute points with p<0.05, we conclude semantic entropy is superior for that benchmark. If no method exceeds others by >2 points, we conclude practical equivalence.

3. **Hallucination taxonomy**: HaluEval already categorizes (QA, dialogue, summarization). We can stratify results without creating new rubrics.

**Key Points:**
- Protocol must fix: model, benchmark, splits, metrics (AUROC, AUPRC)
- Falsifiable: >5 point AUROC gap = significant; <2 point gap = equivalent
- Leverage existing HaluEval categories, no new taxonomy needed

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's protocol is sound, but let me reality-check the implementation:

**Token entropy**: Single forward pass, trivially computable. ✅
**Semantic entropy**: Requires N samples (typically 5-10) + NLI model for clustering. Kuhn uses DeBERTa-NLI. Computationally 10x token entropy, but feasible.
**P(True)**: Requires specific prompting format ("Is the following true?"). Works with any LLM. ✅
**SelfCheckGPT**: Multiple sampling + consistency checking via NLI or BERTScore. Similar cost to semantic entropy. ✅

All methods are implementable with existing repos. The semantic_uncertainty and selfcheckgpt repos provide reference implementations. lm-evaluation-harness handles TruthfulQA.

**Fundamental barriers?** None. This is pure engineering + controlled experiment. The scientific question is testable with existing tools.

**Key Points:**
- All 4 methods implementable with public repos
- Compute cost ranges from 1x (token entropy) to 10x (semantic entropy, SelfCheckGPT)
- No fundamental technical barriers; this is an engineering exercise

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess what this comparison would actually contribute to the field.

**Current state of knowledge**: Practitioners choosing UQ for hallucination detection have no principled guidance. Each paper claims superiority on their own test bed. This is a genuine pain point.

**Contribution level**: A controlled comparison answering "which method works best on standard benchmarks" is HIGH UTILITY but MODERATE NOVELTY. It's more benchmark paper than conceptual advance.

**To elevate significance**: We need a finding beyond "Method X wins." Dr. Nova's hypothesis (methods detect different hallucination types) would be genuinely novel if validated. It would change how practitioners think about UQ — from "pick the best" to "match method to failure mode."

**The question is**: Can we test this hallucination-type hypothesis using existing benchmark categories without creating new rubrics?

**Key Points:**
- Pure comparison is useful but incremental
- Hallucination-type-specificity hypothesis elevates from benchmark study to conceptual contribution
- Must use existing categories (HaluEval subtasks) to stay within feasibility constraints

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on the discussion, let me synthesize a testable hypothesis that addresses everyone's concerns:

**Core Hypothesis (H-UQ-Compare-v1):**
Under standard decoder-only LLMs (7-13B parameters), if we measure hallucination detection using token entropy, semantic entropy, P(True), and SelfCheckGPT on identical TruthfulQA/HaluEval splits, then (1) semantic entropy will achieve highest overall AUROC, but (2) method rankings will vary across HaluEval subtask categories, because different UQ measures capture distinct uncertainty signals.

**Why this works:**
- Uses existing benchmarks (TruthfulQA, HaluEval) — no new rubrics
- Uses existing repos — no novel implementation
- Prediction (1) is directly falsifiable: semantic entropy AUROC vs. others
- Prediction (2) tests the novel method-type correspondence claim using existing HaluEval categories

**What would disprove it:**
- If one method dominates across ALL categories with >5 point gap, prediction (2) fails
- If semantic entropy is NOT best overall, prediction (1) fails

**Key Points:**
- Hypothesis combines "which is best" (utility) with "why they differ" (novelty)
- All tests use existing benchmarks and repos
- Both predictions have clear success/failure criteria

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is clean, but let me stress-test:

**Concern 1: Sample size for subtask analysis.** HaluEval subtasks (QA: 10K, dialogue: 10K, summarization: 10K) are large enough. TruthfulQA (~800) is smaller but standard. Statistical power is adequate.

**Concern 2: Model confound.** If we test on Llama-3-8B only, results might not generalize to other models. Mitigation: include one additional model (Mistral-7B) as secondary validation. Still feasible.

**Concern 3: Computational fairness.** Semantic entropy uses 10 samples; token entropy uses 1. Is the comparison fair? Resolution: report performance at equal compute (e.g., token entropy with 10 samples vs. semantic entropy with 10 samples) AND at typical usage. Both perspectives matter.

**Concern 4: What if all methods perform similarly?** That's still a valid finding — it would suggest UQ method choice matters less than expected. The hypothesis is falsifiable either way.

**Remaining concerns:** None fundamental. The hypothesis is sound.

**Key Points:**
- Sample sizes are adequate for subtask stratification
- Add secondary model (Mistral-7B) for generalization check
- Report both equal-compute and typical-usage comparisons
- "No difference" is a valid, publishable finding

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's stress-test strengthens the design. Let me add one creative refinement:

Beyond binary hallucination detection, we can extract **uncertainty score distributions** for correct vs. hallucinated outputs. If semantic entropy produces more separable distributions than token entropy, that's evidence for why it works better (if it does). This doesn't require new rubrics — just plotting score histograms from existing labels.

**Second insight**: The Kuhn paper shows semantic entropy is robust to rephrasing because it clusters semantic equivalents. But SelfCheckGPT uses NLI consistency without clustering. If semantic entropy wins, the clustering mechanism is the likely differentiator. If SelfCheckGPT wins, maybe consistency is more important than semantic grouping.

This gives us **mechanistic understanding**, not just "which is best."

**Key Points:**
- Plot uncertainty distributions for interpretability
- Compare clustering (semantic entropy) vs. consistency (SelfCheckGPT) mechanisms
- Mechanistic insight elevates the contribution

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The hypothesis has converged. Let me formalize the final testable predictions:

**P1 (Primary):** On TruthfulQA mc1, semantic entropy achieves AUROC ≥ 0.70 and outperforms token entropy by ≥ 3 points. Falsified if: AUROC < 0.65 OR gap < 2 points.

**P2:** On HaluEval aggregate, the UQ method ranking (by AUROC) differs across at least 2 of 3 subtask categories. Falsified if: same method ranks #1 across all 3 categories with >3 point lead.

**P3:** Uncertainty score distributions for hallucinated vs. correct outputs are more separable (higher KL divergence) for semantic entropy than token entropy. Falsified if: token entropy achieves higher KL divergence.

**Experimental Controls:**
- Models: Llama-3-8B (primary), Mistral-7B (secondary)
- Benchmarks: TruthfulQA mc1, HaluEval QA/dialogue/summarization
- Metrics: AUROC, AUPRC, KL divergence of score distributions
- Sample budget: 10 generations per query for all multi-sample methods

**Key Points:**
- Three falsifiable predictions with numeric thresholds
- Controlled experimental setup
- Both overall and category-level analysis

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The group has reached convergence. Let me state the final hypothesis:

**Hypothesis H-UQ-Compare-v1:**

Under decoder-only LLMs (Llama-3-8B, Mistral-7B), if we compare token entropy, semantic entropy, P(True), and SelfCheckGPT on TruthfulQA and HaluEval using identical experimental conditions, then:
1. **Semantic entropy achieves highest overall AUROC** on TruthfulQA, outperforming token entropy by ≥3 points
2. **Method rankings vary by hallucination category** — no single method dominates all HaluEval subtasks
3. **Semantic clustering produces more separable distributions** — semantic entropy yields higher KL divergence between correct/hallucinated output scores than token entropy

Because semantic entropy captures meaning-level consistency while token entropy only captures surface-level confidence, and different hallucination types expose different aspects of model uncertainty.

**Feasibility:** All tests use existing benchmarks (TruthfulQA, HaluEval) and repos (semantic_uncertainty, selfcheckgpt, lm-evaluation-harness). No new rubrics, no human evaluation.

**Key Points:**
- Three testable predictions with clear success/failure criteria
- Uses only existing resources
- Novel contribution: method-hallucination-type correspondence + mechanistic explanation

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis goes beyond mere benchmark comparison to test whether UQ methods detect different hallucination types. The mechanism comparison (clustering vs. consistency) provides explanatory power, not just rankings.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three predictions with numeric thresholds (AUROC gaps, KL divergence). Each is independently testable and falsifiable. Controlled experimental design with model/benchmark specification.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Addresses a genuine practitioner need (which UQ method to use). Elevated by method-type correspondence hypothesis, but core contribution is still benchmark-oriented. Would become HIGH if P2 reveals clear hallucination-type patterns.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All methods implementable with existing repos. No new rubrics or human evaluation. Compute cost is manageable (10x for multi-sample methods). Pure engineering + controlled experiment.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The group converged on H-UQ-Compare-v1: a controlled comparison of four UQ methods (token entropy, semantic entropy, P(True), SelfCheckGPT) as hallucination detectors on TruthfulQA and HaluEval using Llama-3-8B and Mistral-7B. The hypothesis predicts (1) semantic entropy achieves best overall AUROC, (2) method rankings vary across hallucination categories, and (3) semantic clustering produces more separable score distributions. The mechanism is that semantic entropy captures meaning-level consistency while token entropy only captures surface confidence. All tests use existing benchmarks and repos — no new rubrics, no human evaluation. The novel contribution is demonstrating method-hallucination-type correspondence, elevating this from benchmark paper to conceptual insight.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- HaluEval subtask results may show noisy patterns with small effect sizes; pre-register AUROC gap thresholds to avoid p-hacking
- Model generalization beyond Llama/Mistral is untested; acknowledge this limitation explicitly
- **Mitigation Strategy:** Report confidence intervals, pre-specify effect size thresholds (≥3 AUROC points = meaningful), and frame findings as "holds for 7-13B decoder-only models"


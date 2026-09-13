# Phase 2A Discussion Log

## Briefing

**Gap ID:** Gap1
**Gap Title:** No Controlled Comparison Under Matched Computational Budget
**Priority:** CRITICAL | **Relevance:** PRIMARY

### Research Context

**Problem:** Semantic entropy (Kuhn 2023) and SelfCheckGPT (Manakul 2023) report performance on different benchmarks with different numbers of samples. No study compares them head-to-head on TruthfulQA and HaluEval with matched sample counts.

**Missing Piece:** Systematic comparison where semantic entropy and self-consistency methods use identical sample counts (e.g., N=5, 10, 20) on the same benchmark splits, reporting AUROC/F1 under matched computational cost.

**Research Question:** How effective are self-consistency and semantic entropy methods at detecting hallucinations in LLM outputs, measured on TruthfulQA/HaluEval compared to confidence-based baselines?

### Key Papers

1. **Semantic Uncertainty (Kuhn et al., 2023)** - arXiv:2302.09664
   - Semantic entropy clusters via NLI, uses ~10 samples
   
2. **SelfCheckGPT (Manakul et al., 2023)** - arXiv:2303.08896
   - Zero-resource self-consistency, uses ~5 samples
   
3. **TruthfulQA (Lin et al., 2022)** - arXiv:2109.07958
   - Primary benchmark for truthfulness evaluation
   
4. **HaluEval (Li et al., 2023)** - arXiv:2305.11747
   - Multi-task hallucination benchmark
   
5. **Calibrate Before Use (Zhao et al., 2021)** - arXiv:2102.09690
   - Contextual calibration baseline

### Feasibility Constraints (Pipeline-Enforced)

- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? The existing work treats semantic entropy and self-consistency as separate methods to evaluate — but what if the real insight is in their *complementary failure modes*?

Here's what I'm seeing: Kuhn et al.'s semantic entropy clusters generations by meaning via NLI, catching when the model "confidently hallucinates the same wrong thing." Meanwhile, SelfCheckGPT catches surface-level inconsistency. These target *different hallucination types*. A model might consistently generate wrong facts (low self-consistency variance, high semantic entropy if meanings cluster wrongly) OR generate inconsistent stories (high self-consistency variance, potentially low semantic entropy if meanings scatter).

The novel angle: Instead of asking "which is better?" we should ask "under what conditions does each excel, and can we predict which to use based on query characteristics?"

**Key Points:**
- Semantic entropy and self-consistency may have complementary failure modes
- Query type (factual vs. reasoning vs. creative) might predict method effectiveness
- Matched-budget comparison should include interaction effects, not just main effects

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an interesting conjecture, but let me stress-test it. The claim that these methods have "complementary failure modes" is *testable* — but we need precision.

What would disprove this? If semantic entropy and self-consistency have correlation r > 0.85 on hallucination detection across query types, the "complementary" hypothesis fails. We'd need to see divergent performance — cases where one succeeds and the other fails — to support complementarity.

More critically: the matched-budget comparison needs explicit operationalization. "Matched budget" must mean *identical generation costs* — same model, same number of forward passes, same token budget. If semantic entropy uses 10 samples and self-consistency uses 5, we can't compare fairly. The experimental design must fix N = {5, 10, 20} for both methods on identical queries.

**Key Points:**
- Complementarity hypothesis requires divergent performance, not just different mechanisms
- Falsification criterion: correlation > 0.85 between methods would reject complementarity
- Budget matching requires identical generation costs (samples, tokens, model)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what would this contribute that's genuinely new to the field?

Existing work already shows both methods "work" — the contribution isn't proving they detect hallucinations. The gap is the *decision-theoretic* question: given a computational budget, which method should a practitioner choose?

This matters because in production, you have fixed inference costs. A paper that says "semantic entropy with N=10 gives AUROC 0.78 on TruthfulQA while SelfCheckGPT with N=10 gives 0.75" provides actionable guidance. What's even more significant: if the methods have *different error patterns* (false positives vs false negatives), practitioners could ensemble them optimally.

The field impact depends on whether we can move beyond "Method A vs Method B" to "Method selection given task X and budget Y."

**Key Points:**
- Actionable contribution: decision guidance for practitioners under budget constraints
- Error pattern analysis (FP/FN rates) would enable optimal ensembling
- Impact scales with generalizability across model sizes and domains

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The mechanism proposed — comparing semantic entropy vs self-consistency under matched computational budgets — is technically sound. Both methods require multiple forward passes; the comparison is apples-to-apples.

But I need to flag a feasibility concern that's NOT about cost: the NLI model used for semantic entropy clustering is a *separate* model. Is the hypothesis that the NLI step is "free"? If we're comparing computational load fairly, we must account for NLI inference. Semantic entropy with N=10 generations + 45 pairwise NLI calls is NOT equivalent to SelfCheckGPT with N=10 generations + no NLI.

The fix is straightforward: report total FLOPs or wall-clock time, not just sample count. Or restrict the comparison to generation cost only and note that semantic entropy has additional overhead.

**Key Points:**
- Mechanism is sound: both methods use sampling, comparison is feasible
- NLI overhead in semantic entropy must be accounted for or controlled
- Recommend reporting total inference FLOPs alongside sample count

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax raises a valid concern about NLI overhead. Here's how we can strengthen the hypothesis:

**Refined Hypothesis:** Under matched *generation* budgets (N samples), semantic entropy and self-consistency will show different precision-recall tradeoffs on hallucination detection, with the difference being moderated by hallucination type (factual vs consistency-based).

This acknowledges Prof. Pax's point by fixing *generation* cost while noting that semantic entropy has additional NLI cost — which is actually a *finding* to report, not a confound to eliminate. If semantic entropy requires 2x more compute for 5% higher AUROC, that's actionable information.

To address Prof. Vera's falsifiability criterion: we predict correlation between methods < 0.7, with divergent performance on specific query types. The test uses TruthfulQA (factual) and HaluEval QA subset (factual) as well as HaluEval summarization subset (consistency-based).

**Key Points:**
- Fix generation budget, report NLI overhead as additional finding
- Predict method correlation < 0.7 (complementarity threshold)
- Use multiple HaluEval subsets to test hallucination-type moderation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: the hypothesis conflates two claims that need separate testing.

**Claim 1:** Semantic entropy ≠ self-consistency (different precision-recall tradeoffs). This is testable via AUROC/F1 comparison.

**Claim 2:** The difference is moderated by hallucination type. This requires a 2x2 design (method × hallucination type) with sufficient power to detect interactions.

The second claim is *much harder* to test. HaluEval's "summarization" subset isn't cleanly "consistency-based" hallucination — it includes factual errors in summaries. We'd need ground truth labels for *why* each hallucination occurred, which likely requires annotation we explicitly cannot do.

What would convince me: drop Claim 2 for now. Focus on Claim 1: matched-budget comparison on existing benchmarks with existing labels. That's achievable. Claim 2 is a follow-up study.

**Key Points:**
- Separate Claim 1 (methods differ) from Claim 2 (moderation by type)
- Claim 2 requires annotation we cannot do — defer it
- Focus hypothesis on matched-budget comparison with existing benchmarks

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex is right to narrow scope — but let's not lose the insight entirely. Here's a creative reformulation:

Instead of claiming hallucination *type* moderates effectiveness (which requires annotation), claim that *benchmark* moderates effectiveness. TruthfulQA and HaluEval are different benchmarks with different characteristics. If semantic entropy beats self-consistency on TruthfulQA but not on HaluEval (or vice versa), that's signal without requiring new annotation.

The benchmarks themselves serve as proxies for different hallucination distributions. We don't need to label individual examples — we just need to observe cross-benchmark variation.

**Key Points:**
- Replace "hallucination type" moderation with "benchmark" moderation
- Existing benchmarks serve as proxies for hallucination distributions
- No new annotation needed — just cross-benchmark comparison

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reformulation satisfies falsifiability. Let me make the predictions precise:

**P1 (Primary):** Under matched generation budget (N=10), semantic entropy and self-consistency will show statistically different AUROC on at least one of {TruthfulQA, HaluEval-QA, HaluEval-Summarization}. Success: p < 0.05 on paired comparison. Falsification: p ≥ 0.05 on all three benchmarks.

**P2:** Method effectiveness rank ordering will differ across benchmarks (method × benchmark interaction). Success: significant interaction term in 2-way ANOVA. Falsification: no significant interaction.

**P3:** Contextual calibration baseline will underperform both sampling methods at N≥10. Success: both methods beat calibration baseline AUROC. Falsification: calibration matches or exceeds either method.

These are testable with existing benchmarks, existing labels, and existing implementations.

**Key Points:**
- P1: Methods differ on at least one benchmark (primary claim)
- P2: Method × benchmark interaction (moderation without annotation)
- P3: Sampling methods beat calibration baseline (validates prior work)

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The predictions are now technically feasible. Let me verify the measurement approach is valid.

For AUROC, we need binary labels (hallucination / not-hallucination). TruthfulQA provides this via GPT-Judge or human annotations. HaluEval provides explicit labels. Both benchmarks have ground truth — no new labeling needed.

For the 2-way ANOVA (P2), we need multiple observations per cell. With N samples per query and hundreds of queries per benchmark, power is adequate.

The one remaining check: model selection. The hypothesis should be tested on at least 2 model families to claim generalizability. I'd recommend: (1) Llama-3-8B-Instruct, (2) Mistral-7B-Instruct. Both are open-weights, both have sampling API support.

**Key Points:**
- Existing benchmark labels sufficient for AUROC computation
- Statistical power adequate for 2-way ANOVA
- Recommend testing on 2 model families for generalizability

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent convergence. Let me synthesize the final hypothesis:

**Core Claim:** Under matched generation budgets, semantic entropy and self-consistency methods show different hallucination detection performance across benchmarks, with the difference pattern varying by benchmark characteristics.

**Mechanism:** Semantic entropy clusters generations by semantic equivalence (via NLI), detecting when models consistently produce semantically similar but incorrect responses. Self-consistency measures surface-level agreement, detecting when models produce inconsistent responses. These capture different failure modes.

**Predictions:**
1. Methods show statistically different AUROC on at least one benchmark
2. Method × benchmark interaction is significant
3. Both methods outperform contextual calibration at N≥10

**Experimental Setup:**
- Models: Llama-3-8B-Instruct, Mistral-7B-Instruct
- Benchmarks: TruthfulQA, HaluEval-QA, HaluEval-Summarization
- N = {5, 10, 20} for both methods
- Calibration baseline per Zhao et al. (2021)

**Key Points:**
- Clear core claim with mechanism
- Three testable predictions with success/failure criteria
- Feasible experimental setup using existing resources

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis reframes the comparison question from "which method wins" to "when does each method excel" — a novel angle with practical implications. The benchmark-as-proxy insight avoids annotation requirements while preserving the moderation claim.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clear predictions with explicit success/failure criteria. P1 tests method difference, P2 tests moderation, P3 validates baseline claims. All use existing benchmarks with existing labels — no new rubrics required.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Provides actionable guidance for practitioners choosing between methods under budget constraints. Impact limited to hallucination detection domain but directly addresses a gap in existing literature.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist: open-weight models, existing benchmark implementations, standard metrics. The NLI overhead for semantic entropy is explicitly accounted for. Two-model design ensures generalizability check.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis about uncertainty-based hallucination detection. The core claim is that semantic entropy and self-consistency methods, despite both using sampling, capture fundamentally different failure modes and thus show different detection performance patterns across benchmarks. Semantic entropy's NLI-based clustering detects when models consistently produce semantically similar wrong answers, while self-consistency's surface-level comparison detects when models produce inconsistent outputs.

The experimental design compares both methods under matched generation budgets (N=5,10,20) on TruthfulQA and HaluEval subsets, using Llama-3-8B-Instruct and Mistral-7B-Instruct. The primary prediction is that methods will show statistically different AUROC on at least one benchmark (p<0.05). Secondary predictions test for method × benchmark interaction (supporting the moderation claim without annotation) and confirm both methods outperform the contextual calibration baseline from Zhao et al.

This satisfies all feasibility constraints: uses existing benchmarks, existing metrics, and requires no human annotation or new scoring frameworks.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Effect sizes may be small if methods are more similar than hypothesized — need to pre-register minimum meaningful difference
- HaluEval subsets may not be sufficiently distinct in hallucination characteristics to show strong moderation
- **Mitigation Strategy:** Pre-register effect size threshold (e.g., Cohen's d > 0.3 for meaningful difference). If moderation not found, pivot to reporting main effects only as still-useful finding.

---


# Phase 2A Discussion Log: Gap 3 (Priority 1)

**Gap ID:** gap-3  
**Gap Title:** Empirical AUROC vs Inference Cost Trade-off for Single-Pass Methods  
**Research Question:** Can single-forward-pass UQ methods achieve selective prediction AUROC ≥ 0.70 within 2-5× inference cost on TruthfulQA?  
**Session Start:** 2026-08-20

---

## Briefing Context

### Selected Research Gap (Gap 3 - Priority 1)

**Current State:** Conceptual understanding exists (MC dropout k=5 → 5× cost, temp scaling → 0× cost), but no systematic empirical benchmark comparing AUROC vs cost across methods on TruthfulQA.

**Missing Piece:** Unified benchmark: MC dropout (k=1,3,5,10), temperature scaling, conformal prediction on TruthfulQA selective prediction. Which method achieves AUROC ≥ 0.70 at lowest cost?

**Potential Impact:** Directly answers detailed_question 1 (AUROC vs cost trade-off). Guides method selection for 2-5× budget constraint.

### Key Papers (From Phase 1 Scholar Search)

**P1:** "Uncertainty-aware Language Modeling for Selective QA" (Yang et al. 2023, 16 cit, arXiv:2311.15451)
- Selective QA on SQuAD + **TruthfulQA** (exact benchmark match)
- Automatic LLM conversion for uncertainty-aware predictions
- Using uncertainty estimates leads to significantly higher accuracy

**P2:** "API Is Enough: Conformal Prediction for LLMs" (Su et al. 2024, 74 cit, arXiv:2403.01216)
- API-only conformal prediction (no logit access required = single-pass)
- Nonconformity scores: sample frequency + semantic similarity
- Outperforms logit-based CP baselines

**P3:** "Mix-n-Match: Ensemble and Compositional Methods for UQ Calibration" (Zhang et al. 2020, 293 cit, arXiv:2003.07329)
- ECE evaluation + kernel density-based estimator
- Alternative ECE estimator for small-data regime
- Addresses small sample size concerns

**P4:** "On Calibration of Modern Neural Networks" (Guo et al. 2017, 9294 cit, arXiv:1706.04599)
- Seminal temperature scaling paper
- Discovered modern NNs poorly calibrated
- Single-parameter variant surprisingly effective

**P5:** "Generating with Confidence: Black-box UQ" (Lin et al. 2023, 330 cit, arXiv:2305.19187)
- Black-box UQ for NLG (no logit access)
- Semantic dispersion as uncertainty measure
- Applied to selective NLG

### Implementation Resources (From Phase 1 Exa Search)

- **TruthfulQA Benchmark:** sylinrl/TruthfulQA (911 stars, official repo)
- **MC Dropout:** aryanator/dropwise (8 stars, HF wrapper), mourga/transformer-uncertainty (44 stars, comparison framework)
- **Conformal Prediction:** SU-JIAYUAN/LofreeCP (9 stars, EMNLP'24), bhaweshiitk/ConformalLLM (70 stars)
- **Temperature Scaling:** gpleiss/temperature_scaling (1172 stars, original), probkit/probmetrics (68 stars, modern)
- **UQ Toolkits:** cvs-health/uqlm (1183 stars), IINemo/lm-polygraph (477 stars)

### Failure Context (ROUTE_TO_0 - From Phase 1)

**Critical Patterns to AVOID:**
1. Oracle engineering (unsupervised variance) — fails on low-variance datasets
2. Ensemble generation — computationally expensive (~30 min for n=50)
3. Token-level signals — don't predict correctness at small scale (AUROC 0.462)
4. Linear classifiers — insufficient (logistic regression AUROC 0.462)
5. Small samples (n<200) — severe overfitting

**How Gap 3 Avoids These:**
- Single-pass methods (no oracle engineering, no ensemble)
- Direct uncertainty estimation (conformal prediction, MC dropout, temp scaling)
- All methods ≤ 5× baseline (within 2-5× budget)
- Existing TruthfulQA benchmark (no new data collection)

### Previous Failure / Routing Context

*No Serena memory files found. This is the first Phase 2A attempt.*

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the UQ comparison problem on its head? Instead of asking "which single method wins?", what if the REAL novelty is discovering that **different methods dominate at different cost-performance zones** — creating an empirical Pareto frontier that guides practitioners based on their specific inference budget?

Here's what excites me: Yang et al. 2023 showed TruthfulQA selective QA works, Su et al. 2024 proved conformal prediction needs no logit access, and Guo et al. 2017 gave us zero-cost temperature scaling. But nobody has mapped the complete trade-off curve! Imagine this:
- **Zone 1 (0× cost):** Temperature scaling + conformal prediction (post-hoc calibration)
- **Zone 2 (2-5× cost):** MC dropout with adaptive k (dynamically adjust sample count)
- **Zone 3 (>5× cost):** Ensemble baselines (the "expensive but accurate" anchor)

The creative leap: Instead of declaring ONE winner, we characterize the **efficiency frontier** — which method is Pareto-optimal at each cost level? This connects to Lin et al. 2023's black-box UQ (semantic dispersion works without logits) and opens a paradigm shift: **budget-aware UQ selection**.

NOW here's the wild idea that might seem impossible: What if we find that **zero-cost methods (temp scaling) achieve AUROC ≥ 0.70** on TruthfulQA, making MC dropout unnecessary for many applications? That would challenge the field's assumption that "better UQ requires more compute." The Zhang et al. 2020 kernel-density ECE estimator could validate this with small-data robustness.

**Key Points:**
- Pareto frontier mapping instead of single-method comparison
- Budget-aware UQ selection framework (practitioner-facing contribution)
- Test the provocative hypothesis: zero-cost methods might suffice
- Cross-validate on HaluEval to prove generalization (not just TruthfulQA overfitting)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's Pareto frontier concept has merit, but let's ensure it can actually be tested rigorously. The evidence suggests we need PRECISE predictions before celebrating creativity.

**What would disprove this hypothesis?** If all three method families (temp scaling, conformal prediction, MC dropout) produce statistically indistinguishable AUROC curves across cost levels on TruthfulQA, the Pareto frontier collapses to noise. We need quantifiable separation between methods.

Here's my stress test: Yang et al. 2023 tested TruthfulQA with "significantly higher accuracy" using uncertainty estimates — but they didn't report AUROC vs cost curves. We must define:

1. **Metric:** Area Under ROC Curve (AUROC) for selective prediction. Success threshold: AUROC ≥ 0.70 (per primary research question). Measurement protocol from official TruthfulQA repo (sylinrl/TruthfulQA).

2. **Cost Metric:** Wall-clock inference time OR FLOPs count (normalized to single forward pass = 1.0×). MC dropout k=5 should measure exactly 5.0× ± 0.1×. Temperature scaling must be 1.0× (post-hoc, no inference overhead).

3. **Confounds:** Model size (fix at 8B parameters initially per ROUTE_TO_0 lesson), dataset split (hold-out test set, never touched during calibration), random seed (report mean ± std over 3 runs).

What result would convince us this hypothesis is WRONG? If temperature scaling achieves AUROC < 0.55 (random baseline ~0.50) while MC dropout k=5 achieves ≥ 0.70, the zero-cost claim fails catastrophically.

The Su et al. 2024 conformal prediction paper used "sample frequency + semantic similarity" for nonconformity scores. What specific nonconformity measure will we use? If undefined, we're not testing a hypothesis, we're testing an ambiguity.

**Key Points:**
- AUROC ≥ 0.70 threshold with statistical significance tests (p < 0.05)
- Cost measured as FLOPs or wall-clock time, normalized to 1.0× baseline
- Confounds controlled: model size (8B), dataset split, random seed
- Null hypothesis: temp scaling AUROC < 0.55 → MC dropout necessary

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: What does this mean for the field? Both Dr. Nova and Prof. Vera make important contributions, but let me assess the actual scientific significance here.

**Why this matters beyond incremental work:** Current UQ research treats method comparison as a winner-take-all horse race. Lin et al. 2023 (330 citations) showed semantic dispersion for black-box LLMs. Su et al. 2024 extended conformal prediction to API-only settings. But crucially, NO prior work maps the complete AUROC vs cost trade-off space for practitioners to make informed decisions.

This is not incremental because:

1. **Practitioner Impact:** A Pareto frontier guides real deployment decisions. If temp scaling achieves AUROC 0.65 at 0× cost but MC dropout k=10 achieves 0.72 at 10× cost, practitioners know the marginal 0.07 AUROC improvement costs 10× inference budget. This cost-benefit framing is ABSENT from current literature.

2. **State-of-the-Art Positioning:** Yang et al. 2023 demonstrated TruthfulQA selective QA works but didn't systematically compare methods. Zhang et al. 2020 compared calibration techniques but not in the LLM selective prediction context. Our work would be the FIRST comprehensive benchmark on TruthfulQA selective prediction with cost analysis.

3. **New Research Directions:** If we discover that zero-cost methods achieve competitive AUROC, it opens investigation into "when does paying for MC dropout actually matter?" This could spawn a subfield of **adaptive UQ budgeting** — dynamically switch between methods based on query complexity.

However, I must also challenge the significance claim: What makes this genuinely new vs incremental? The danger is this becomes a "comprehensive benchmark paper" (valuable but not paradigm-shifting). The REAL contribution emerges IF we find surprising results — e.g., temp scaling dominates MC dropout below AUROC 0.70, contradicting intuition that "more compute = better UQ."

**Key Points:**
- First systematic AUROC vs cost comparison on TruthfulQA selective prediction
- Practitioner-facing Pareto frontier (cost-benefit decision tool)
- Potential to challenge "more compute = better UQ" assumption
- Opens adaptive UQ budgeting research direction IF results are non-trivial

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here — is this mechanism technically sound? Dr. Nova's Pareto frontier concept is creative, Prof. Vera defined rigorous tests, Dr. Sage positioned the impact well. But here's what worries me about the fundamental feasibility.

**Is the mechanism scientifically possible?** Yes — all three methods (temp scaling, conformal prediction, MC dropout) have theoretical foundations:
- Temperature scaling: Guo et al. 2017 proved single-parameter calibration validity
- Conformal prediction: Distribution-free coverage guarantees (Kumar et al. 2023)
- MC dropout: Bayesian approximation via variational inference (established in Gal & Ghahramani 2016)

**Are the measurement methods theoretically valid?** Here's where I see the first fundamental barrier: AUROC for selective prediction requires a binary ground truth label (correct/incorrect) for each TruthfulQA question. The official TruthfulQA repo (sylinrl/TruthfulQA) uses GPT-judge metrics for truthfulness scoring — this introduces oracle dependency. What evidence supports that GPT-judge labels are reliable enough for AUROC calculation?

Yang et al. 2023 used "significantly higher accuracy" but didn't specify how they determined ground truth. If we use GPT-4 as judge, we're measuring "agreement with GPT-4" not "actual truthfulness." This isn't a cost issue — it's a measurement validity issue.

**Can the proposed interventions work in principle?** The Pareto frontier comparison requires all methods to use the SAME model (8B parameters per ROUTE_TO_0 constraint). Temperature scaling calibrates on a validation set, conformal prediction needs a calibration set, MC dropout samples k times. These are compatible — no fundamental conflict. But here's a subtle barrier: if the 8B model's base accuracy on TruthfulQA is very low (e.g., <40% correct), even perfect UQ won't push AUROC ≥ 0.70 because the signal is too weak.

What would convince me this is fundamentally feasible? Evidence that:
1. TruthfulQA has reliable ground truth labels (not just GPT-judge)
2. An 8B model achieves baseline accuracy >50% on TruthfulQA (enough signal for UQ to detect)
3. The cost measurement (FLOPs or wall-clock time) accounts for all overhead (calibration time excluded per Prof. Vera's "post-hoc" criterion)

**Key Points:**
- Mechanisms are theoretically sound (all methods have established foundations)
- Measurement validity concern: TruthfulQA ground truth labels (GPT-judge vs actual truthfulness)
- Fundamental barrier: 8B model baseline accuracy must be >50% for AUROC ≥ 0.70 to be achievable
- Cost measurement must exclude calibration time (one-time overhead, not per-query cost)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by directly addressing Prof. Pax's measurement validity concern! This is exactly the kind of critique that makes the hypothesis better.

**What evidence supports ground truth reliability?** The official TruthfulQA paper (Lin et al. 2021, not in our briefing but foundational) used HUMAN-EVALUATED truthfulness labels for the 817 questions. The dataset's ground truth ISN'T GPT-judge scores — it's human consensus annotations. The GPT-judge metrics (from the 2023 update) are for AUTOMATED evaluation, but the original labels are human-verified. This resolves Prof. Pax's concern: we use the human-annotated labels as ground truth for AUROC calculation.

**What if we addressed the 8B baseline accuracy concern?** Let me find supporting evidence. Yang et al. 2023 showed that "using uncertainty estimates to selectively answer leads to significantly higher accuracy" on TruthfulQA. This implies the base model had non-trivial accuracy (otherwise selective prediction wouldn't improve it). We can validate this in our experiment design:

**Refined Experimental Protocol:**
1. **Pre-check:** Measure 8B model baseline accuracy on TruthfulQA. If <50%, STOP and document limitation. If ≥50%, proceed.
2. **Ground Truth:** Use human-annotated truthfulness labels from official TruthfulQA dataset (sylinrl/TruthfulQA).
3. **Selective Prediction Setup:** For each question, model outputs (answer, uncertainty_score). Rank by uncertainty, compute AUROC for "correct prediction" vs "incorrect prediction" classification.
4. **Cost Normalization:** Report inference cost per query (excluding one-time calibration). Temp scaling = 1.0×, MC dropout k=5 = 5.0×, conformal prediction = 1.0× (post-calibration).

**How can we strengthen against the "incremental benchmark" concern from Dr. Sage?** The key is designing experiments that can DISCOVER surprises, not just confirm expectations. Here's the refinement:

**Hypothesis Variants to Test:**
- **H1 (Conservative):** MC dropout k=5 achieves highest AUROC at 5× cost (expected result)
- **H2 (Optimistic):** Temp scaling achieves AUROC ≥ 0.70 at 0× cost (challenges "more compute = better UQ")
- **H3 (Pareto Frontier):** Different methods dominate at different cost-performance zones (Dr. Nova's creative insight)

If H2 is TRUE, we've discovered something genuinely surprising. If H1 is TRUE but H3 is FALSE (all methods scale together), we document an important null result. Either way, the field learns something actionable.

**Key Points:**
- Ground truth: Human-annotated TruthfulQA labels (resolves measurement validity)
- Pre-check: 8B baseline accuracy ≥ 50% before proceeding (addresses feasibility barrier)
- Three hypothesis variants: test for surprising results, not just confirmation
- Cost normalization excludes calibration (one-time setup, not per-query cost)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and how to fix it.

**Challenge 1: The "8B baseline >50%" pre-check is a trap.** What would convince me? Show me evidence that an 8B model actually achieves >50% on TruthfulQA TODAY. Dr. Ally assumes this as a precondition, but I see no citation. The ROUTE_TO_0 failure context showed "8B model r=0.580 (2/3 folds fail)" — this was for a DIFFERENT task (correlation prediction, not QA). We don't know if 8B models pass the 50% threshold on TruthfulQA. If they don't, this whole hypothesis crumbles before we start.

**Mitigation:** Run a preliminary experiment: Load an off-the-shelf 8B model (Llama-3.1-8B or similar), evaluate on TruthfulQA, report accuracy. If <50%, PIVOT to smaller scale validation (GPT-2 or larger models). Don't assume — measure first.

**Challenge 2: Prof. Pax's "cost excludes calibration" criterion conflicts with conformal prediction.** Conformal prediction requires a calibration set for EVERY test distribution. If TruthfulQA is the test set, where does the calibration set come from? If we use a separate calibration set (e.g., HaluEval), then "cost excludes calibration" is valid. But if we split TruthfulQA into calibration + test, we lose data and the conformal prediction cost is NOT 1.0× — it's 1.0× per query PLUS the calibration overhead for the first query.

**Mitigation:** Clarify calibration protocol. Option A: Use HaluEval as calibration set, TruthfulQA as test set (enables cross-dataset generalization test from DQ4). Option B: Split TruthfulQA 50/50 for calibration/test (reduces test set size but keeps everything in-distribution).

**Challenge 3: The "Pareto frontier" claim (H3) needs a mathematical definition.** What does "different methods dominate at different zones" MEAN precisely? Is it:
- **Definition A:** For cost C₁, method M₁ has highest AUROC. For cost C₂, method M₂ has highest AUROC (M₁ ≠ M₂)?
- **Definition B:** No method is strictly dominated (i.e., there's no method that has both higher AUROC AND lower cost than another)?

These are different claims. Definition A is stronger (methods trade places). Definition B is weaker (Pareto optimality). Dr. Nova's intuition suggests Definition A, but we haven't formalized it.

**Mitigation:** State the mathematical formulation: "We define the Pareto frontier as the set of (cost, AUROC) points such that no method achieves strictly higher AUROC at equal or lower cost. We test H3 by checking if ≥2 methods lie on this frontier."

**Challenge 4: The "surprising result" framing (H2: temp scaling AUROC ≥ 0.70) is post-hoc.** What if temp scaling achieves AUROC 0.68? Do we declare "close enough" or "hypothesis failed"? The 0.70 threshold is arbitrary (from primary research question) but not grounded in prior work.

**Mitigation:** Report AUROC for ALL methods + confidence intervals. Frame H2 as "Temp scaling achieves AUROC within 0.05 of MC dropout k=5" (competitive performance at 0× vs 5× cost). This captures the spirit without arbitrary thresholding.

**Key Points:**
- Must validate 8B baseline accuracy >50% empirically before proceeding (don't assume)
- Clarify conformal prediction calibration protocol (HaluEval calibration set recommended)
- Formalize Pareto frontier mathematically (Definition B: Pareto optimality)
- Relax H2 threshold: "AUROC within 0.05 of MC dropout" (avoids arbitrary 0.70 cutoff)

---


### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can address every one of Prof. Rex's challenges with concrete refinements! This is exactly the kind of stress-testing that makes a hypothesis bulletproof.

**Challenge 1 Resolution: 8B baseline validation.** Prof. Rex is absolutely right — we can't assume. Here's the refined protocol:

**Phase 0 (Baseline Validation):**
1. Load Llama-3.1-8B-Instruct (widely available, reproducible)
2. Evaluate on TruthfulQA using official evaluation protocol (sylinrl/TruthfulQA)
3. Report accuracy with 95% CI
4. **Decision rule:** If accuracy ≥ 45% (relaxed from 50% to account for TruthfulQA's adversarial design), proceed. If <45%, document as limitation and suggest future work at larger scale (70B models).

Why 45%? TruthfulQA is designed to be challenging for LLMs — even GPT-3 scored ~38% initially. An 8B model at 45% would have sufficient signal for UQ methods to demonstrate value.

**Challenge 2 Resolution: Conformal prediction calibration.** Brilliant catch. Here's the refined approach:

**Calibration Protocol:**
- **Calibration Set:** HaluEval (separate dataset, ~10k samples available)
- **Test Set:** TruthfulQA (full 817 questions, no splitting)
- **Rationale:** This also addresses DQ4 (cross-dataset generalization)! We calibrate on HaluEval, test on TruthfulQA. If conformal prediction generalizes, it proves robustness. If it fails, we've discovered an important limitation.
- **Cost Calculation:** Conformal prediction = 1.0× per TruthfulQA query (calibration on HaluEval is one-time setup, not per-query cost).

**Challenge 3 Resolution: Pareto frontier formalization.** Let's use Prof. Rex's Definition B (Pareto optimality) — it's mathematically precise and doesn't require methods to "trade places":

**Formalization:**
- **Pareto Frontier:** The set of (cost, AUROC) points where no method achieves strictly higher AUROC at equal or lower cost.
- **H3 Test:** We consider H3 confirmed if ≥2 methods lie on the Pareto frontier (i.e., neither dominates the other).
- **Example:** If temp scaling = (1.0×, 0.68) and MC dropout k=5 = (5.0×, 0.73), both are Pareto-optimal (MC dropout has higher AUROC but higher cost). If MC dropout k=1 = (1.0×, 0.72), temp scaling is dominated and H3 fails.

**Challenge 4 Resolution: Relax arbitrary threshold.** Prof. Rex's suggestion is perfect:

**Revised H2:**
- **Old:** Temp scaling achieves AUROC ≥ 0.70 (arbitrary threshold)
- **New:** Temp scaling achieves AUROC within Δ=0.05 of MC dropout k=5 (competitive performance at 0× vs 5× cost)
- **Interpretation:** If temp scaling = 0.68 and MC dropout k=5 = 0.72, then Δ=0.04 < 0.05 → H2 CONFIRMED. This captures "zero-cost methods competitive with expensive methods."

**Consolidated Experimental Design:**

**Phase 0:** Validate 8B baseline accuracy ≥ 45% on TruthfulQA (go/no-go decision)

**Phase 1: Main Experiment**
- **Models:** Llama-3.1-8B-Instruct (fixed for all methods)
- **Calibration:** HaluEval (10k samples) for conformal prediction + temp scaling
- **Test Set:** TruthfulQA (817 questions, human-annotated labels)
- **Methods:** 
  - Temp scaling (1.0×)
  - Conformal prediction (1.0×)
  - MC dropout k=1,3,5,10 (1.0×, 3.0×, 5.0×, 10.0×)
- **Metrics:** AUROC for selective prediction (mean ± std over 3 random seeds)
- **Cost:** FLOPs count normalized to single forward pass

**Phase 2: Analysis**
- Construct Pareto frontier (Definition B)
- Test H1, H2, H3:
  - **H1:** MC dropout k=5 has highest AUROC (expected)
  - **H2:** Temp scaling AUROC within Δ=0.05 of MC dropout k=5 (surprising efficiency)
  - **H3:** ≥2 methods on Pareto frontier (cost-performance trade-off exists)

**Key Points:**
- Phase 0 baseline check (8B accuracy ≥ 45%) with relaxed threshold
- HaluEval calibration set → TruthfulQA test set (addresses cross-dataset generalization)
- Pareto frontier: Definition B (Pareto optimality, mathematically precise)
- H2 relaxed: AUROC within Δ=0.05 (avoids arbitrary 0.70 threshold)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

This meets my standards. Dr. Ally's refinements transform Dr. Nova's creative vision into a testable hypothesis.

**What specific, measurable predictions can we make?** The evidence suggests the consolidated experimental design addresses every criterion:

1. **Phase 0 Pre-check (Falsifiable):**
   - **Prediction P0:** Llama-3.1-8B-Instruct achieves accuracy ≥ 45% on TruthfulQA (817 questions, human-annotated labels).
   - **Falsification:** If accuracy < 45%, hypothesis is NOT testable at 8B scale → document limitation.
   - **Why this matters:** This is a go/no-go gate. Without sufficient base accuracy, UQ methods have no signal to amplify.

2. **Main Experiment Predictions (H1, H2, H3):**

   - **H1 (Expected Result):** MC dropout k=5 achieves the highest AUROC among all methods.
     - **Measurement:** AUROC_mc5 > max(AUROC_temp, AUROC_conf, AUROC_mc1, AUROC_mc3, AUROC_mc10) with statistical significance (paired t-test, p < 0.05, n=3 seeds).
     - **Falsification:** If temp scaling or conformal prediction achieves higher AUROC than MC dropout k=5 (p < 0.05), H1 is FALSE → surprising discovery that zero-cost methods dominate.

   - **H2 (Surprising Efficiency):** Temperature scaling achieves AUROC within Δ=0.05 of MC dropout k=5.
     - **Measurement:** |AUROC_temp - AUROC_mc5| ≤ 0.05
     - **Falsification:** If |AUROC_temp - AUROC_mc5| > 0.05, temp scaling is NOT competitive → MC dropout's 5× cost is justified.
     - **Why Δ=0.05?** This represents ~7% relative gap at AUROC 0.70. Smaller gaps are practically negligible for deployment decisions.

   - **H3 (Pareto Frontier):** At least 2 methods lie on the Pareto frontier.
     - **Measurement:** Construct Pareto set = {(cost, AUROC) | no method dominates}. Count |Pareto set| ≥ 2.
     - **Falsification:** If only 1 method is Pareto-optimal (e.g., MC dropout k=5 dominates all others), H3 is FALSE → no cost-performance trade-off, just one clear winner.
     - **Example:** If temp = (1.0×, 0.72) and MC k=5 = (5.0×, 0.71), temp dominates → H3 FALSE. If temp = (1.0×, 0.68) and MC k=5 = (5.0×, 0.73), both Pareto-optimal → H3 TRUE.

**What confounds need to be controlled?** The refined protocol addresses all major confounds:

- **Model capacity:** Fixed at Llama-3.1-8B-Instruct (no architecture variation).
- **Calibration data:** HaluEval for temp scaling + conformal prediction (separate from TruthfulQA test set).
- **Random seed:** Report mean ± std over 3 seeds (tests reproducibility).
- **Evaluation protocol:** Official TruthfulQA evaluation script (human-annotated labels, not GPT-judge).
- **Cost normalization:** FLOPs count per query (excludes one-time calibration overhead).

**What would convince us this is wrong?** Dr. Ally's Phase 0 baseline check is the critical falsification point:
- If 8B baseline accuracy < 45%, we STOP and document: "Hypothesis requires larger models (≥70B) for sufficient signal."
- If all methods achieve AUROC < 0.60 (barely above random 0.50), we document: "TruthfulQA selective prediction may be too challenging for current single-pass UQ methods."

**Experimental validity assessment:** ✅ PASS
- All predictions are quantitative and falsifiable
- Confounds are controlled
- Failure modes are explicitly defined
- Statistical significance tests specified (paired t-test, p < 0.05)

**Key Points:**
- P0 falsifiable: 8B baseline accuracy ≥ 45% (go/no-go gate)
- H1/H2/H3 quantitative: AUROC thresholds, Δ=0.05, Pareto optimality count
- All confounds controlled: model, calibration data, random seed, evaluation protocol
- Explicit failure modes: <45% baseline → stop, <0.60 AUROC → document limitation

---

### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now you've addressed my concerns. Dr. Ally's refinements and Prof. Vera's validation close every gap I identified.

**Final stress test — what still worries me:**

**Concern 1: HaluEval → TruthfulQA generalization assumption.** We're calibrating on HaluEval (hallucination detection) and testing on TruthfulQA (truthfulness QA). These are RELATED but not IDENTICAL tasks. What if conformal prediction's nonconformity scores (sample frequency + semantic similarity) don't transfer?

**Mitigation already in place:** This IS the cross-dataset generalization test (DQ4). If conformal prediction fails to transfer, we've discovered an important finding: "Conformal prediction calibrated on hallucination detection does NOT generalize to truthfulness QA." That's a negative result, but it's still scientifically valuable. The Lin et al. 2025 domain-shift paper suggests this could happen.

**Verdict:** This is a FEATURE, not a bug. We're testing generalization, not assuming it.

**Concern 2: The "Δ=0.05 competitive" threshold for H2.** Is 0.05 loose enough to detect practical equivalence, or tight enough to avoid false positives?

**Analysis:** At AUROC 0.70, Δ=0.05 represents a 7% relative gap. In selective prediction, this translates to:
- **Temp scaling @ 0.68:** Reject 32% of queries with 68% precision
- **MC dropout k=5 @ 0.73:** Reject 27% of queries with 73% precision
- **Practical difference:** 5% more queries rejected, 5% higher precision. This is MEANINGFUL but not game-changing.

**Verdict:** Δ=0.05 is well-calibrated. Tighter (Δ=0.02) would be too strict (noise-dominated). Looser (Δ=0.10) would be too permissive (14% gap is large).

**Concern 3: The "≥2 methods on Pareto frontier" criterion for H3.** What if 3+ methods are Pareto-optimal due to noise (overlapping confidence intervals)?

**Counter-argument:** Prof. Vera specified "statistical significance (paired t-test, p < 0.05, n=3 seeds)." If two methods have overlapping 95% CIs, they're statistically indistinguishable → treated as equivalent, not distinct Pareto points. The Pareto frontier is constructed from MEAN AUROCs, but dominance is tested with statistical significance.

**Refined H3 criterion:**
- **Old:** |Pareto set| ≥ 2 (could be noise-driven)
- **New:** |Pareto set| ≥ 2 AND pairwise t-test shows p < 0.05 between any two Pareto-optimal methods
- **Example:** If temp = (1.0×, 0.68±0.02) and MC k=5 = (5.0×, 0.73±0.02), and t-test p = 0.001, both are DISTINCT Pareto points → H3 TRUE.

**Verdict:** This refinement makes H3 robust to noise.

**Final Challenge: Implementation repositories — do they actually work?**

From Phase 1 Exa results:
- **Temperature scaling:** gpleiss/temperature_scaling (1172 stars, original reference implementation) — TRUSTED
- **Conformal prediction:** SU-JIAYUAN/LofreeCP (9 stars, EMNLP'24 paper) — RISKY (low stars, recent)
- **MC dropout:** aryanator/dropwise (8 stars, HF wrapper) — RISKY (low stars)
- **Benchmarks:** sylinrl/TruthfulQA (911 stars, official) — TRUSTED

**Mitigation:** For low-star repos, validate against paper specifications:
- **LofreeCP:** Su et al. 2024 specifies nonconformity = sample_frequency × semantic_similarity. If repo deviates, implement from paper.
- **dropwise:** Basic MC dropout is trivial (enable dropout at inference, sample k times). If repo fails, implement manually.

**Verdict:** Repos are starting points, not dependencies. We can fall back to paper specifications.

**Remaining Concerns:**
- None that invalidate the hypothesis.
- All identified risks have documented mitigations or are PART of the experimental design (e.g., cross-dataset generalization test).

**Final verdict:** This hypothesis is ready for Phase 2B (Research Planning). The experimental design is rigorous, falsifiable, and addresses every challenge raised in this discussion.

**Key Points:**
- HaluEval → TruthfulQA generalization is a FEATURE (tests DQ4 cross-dataset robustness)
- Δ=0.05 for H2 is well-calibrated (7% relative gap = meaningful but not game-changing)
- H3 refined: Pareto optimality + statistical significance (p < 0.05)
- Low-star repos mitigated: fall back to paper specifications if needed

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Pareto frontier framing is genuinely novel — existing work compares methods in isolation, but mapping the complete cost-performance trade-off space is unexplored. Budget-aware UQ selection framework opens a new research direction beyond "which method wins?"

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All predictions are quantitative and falsifiable. Phase 0 baseline check (accuracy ≥ 45%) is a go/no-go gate. H1/H2/H3 have precise success criteria (AUROC thresholds, Δ=0.05, Pareto optimality + statistical significance). Every confound is controlled with explicit protocols.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First systematic AUROC vs cost benchmark on TruthfulQA selective prediction. Practitioner-facing Pareto frontier provides actionable deployment guidance. If H2 is confirmed (zero-cost methods competitive), it challenges the field's "more compute = better UQ" assumption. Opens adaptive UQ budgeting subfield.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All methods are theoretically sound (temperature scaling, conformal prediction, MC dropout have established foundations). Measurement validity resolved (human-annotated TruthfulQA labels, not GPT-judge). Phase 0 baseline check (8B accuracy ≥ 45%) addresses fundamental barrier. HaluEval calibration → TruthfulQA test is valid cross-dataset setup.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

We hypothesize that single-forward-pass uncertainty quantification methods exhibit a **cost-performance Pareto frontier** on TruthfulQA selective prediction, where different methods are optimal at different inference budgets, challenging the assumption that expensive methods always outperform cheaper alternatives.

**Core Claim:** Temperature scaling (0× cost), conformal prediction (0× cost), and MC dropout (k-dependent cost) occupy distinct positions on an empirical Pareto frontier, enabling budget-aware UQ method selection for practitioners.

**Proposed Mechanism:**
- **Phase 0:** Validate that Llama-3.1-8B-Instruct achieves ≥45% baseline accuracy on TruthfulQA (817 human-annotated questions). If <45%, document limitation and suggest larger-scale follow-up.
- **Phase 1:** Calibrate temperature scaling and conformal prediction on HaluEval (~10k samples). Test all methods on TruthfulQA: temp scaling (1.0×), conformal prediction (1.0×), MC dropout k=1,3,5,10 (1.0×, 3.0×, 5.0×, 10.0×).
- **Phase 2:** Compute AUROC for selective prediction (mean ± std over 3 random seeds). Construct Pareto frontier and test three hypotheses:
  - **H1 (Expected):** MC dropout k=5 achieves highest AUROC
  - **H2 (Surprising Efficiency):** Temp scaling AUROC within Δ=0.05 of MC dropout k=5
  - **H3 (Pareto Frontier):** ≥2 methods Pareto-optimal with statistical significance (p < 0.05)

**Key Predictions:**
1. **P0:** 8B baseline accuracy ≥ 45% on TruthfulQA (falsifiable go/no-go)
2. **H1:** MC dropout k=5 > all other methods (expected hierarchy)
3. **H2:** |AUROC_temp - AUROC_mc5| ≤ 0.05 (zero-cost competitiveness)
4. **H3:** ≥2 Pareto-optimal methods (cost-performance trade-off exists)

**Experimental Approach:**
- **Model:** Llama-3.1-8B-Instruct (reproducible, widely available)
- **Calibration:** HaluEval (separate from test set, enables cross-dataset generalization test)
- **Test Set:** TruthfulQA (817 questions, human-annotated labels from official repo)
- **Metrics:** AUROC for selective prediction, cost as FLOPs normalized to 1.0× baseline
- **Statistical Rigor:** Paired t-tests (p < 0.05) for method comparisons, 3 random seeds for reproducibility

**Novelty:** First comprehensive cost-performance benchmark for UQ methods on TruthfulQA. Pareto frontier framing enables budget-aware method selection (practitioner impact). Potential to challenge "more compute = better UQ" dogma if zero-cost methods prove competitive.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** HaluEval → TruthfulQA generalization may fail for conformal prediction (different task distributions). **Mitigation:** This IS the generalization test (DQ4) — failure is a scientifically valuable negative result.
- **Concern 2:** Low-star implementation repos (LofreeCP: 9 stars, dropwise: 8 stars) may have bugs. **Mitigation:** Validate against paper specifications; fall back to manual implementation if repos deviate.
- **Concern 3:** 8B baseline accuracy <45% would invalidate hypothesis at this scale. **Mitigation:** Phase 0 pre-check explicitly tests this — if fails, document and suggest ≥70B model follow-up.
- **Final Verdict:** All concerns mitigated with explicit protocols. Hypothesis ready for Phase 2B (Research Planning).


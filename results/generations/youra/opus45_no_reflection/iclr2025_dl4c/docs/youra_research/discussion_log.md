# Phase 2A Research Discussion Log

## Briefing

**Research Question:** Does execution feedback (test pass/fail signals, compiler errors, runtime traces) outperform AI-generated feedback (LLM critique, code review simulation) for post-training alignment of code generation models?

**Selected Gap:** No Controlled Comparison of Execution vs AI Feedback (HIGH + PRIMARY)

**Gap Description:** Execution feedback methods (CodeRL, RLTF) and AI feedback methods (Self-Refine) are developed and evaluated independently on different base models, hyperparameters, and sometimes different benchmarks. A controlled study using identical base model, training budget, and evaluation protocol is needed to isolate the effect of feedback source.

**Key Metrics:** pass@1, pass@10, sample efficiency

**Benchmarks:** HumanEval, MBPP, APPS

### Reference Papers

1. **P1: CodeRL** (Le et al., 2022) - arxiv:2207.01780
   - Actor-critic RL with CodeT5 backbone
   - Uses unit test pass/fail as reward signal
   - SOTA on APPS/MBPP with execution feedback

2. **P2: Self-Refine** (Madaan et al., 2023) - arxiv:2303.17651
   - Iterative LLM self-feedback without training
   - Same LLM generates, critiques, and refines
   - Test-time AI feedback approach

3. **P3: RLTF** (Liu et al., 2023) - arxiv:2307.04349
   - Online RL with multi-granularity unit test feedback
   - Fine-grained error location signals
   - SOTA on APPS/MBPP

4. **P4: CodeT** (Chen et al., 2022) - arxiv:2207.10397
   - Dual execution agreement using LLM-generated tests
   - Hybrid approach: AI-generated tests + execution ranking

### Feasibility Constraints (Pipeline-Enforced)

- **MUST USE:** Existing real datasets and existing benchmarks only
- **REJECT:** New benchmarks, rubrics, or scoring frameworks
- **REJECT:** Synthetic/generated data or future follow-up data
- **REJECT:** Human evaluation, annotation, or subjective scoring

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been looking at this question backwards? The field has bifurcated into execution feedback (CodeRL, RLTF) versus AI feedback (Self-Refine) camps, each developing sophisticated methods in isolation. But reading through these papers, I see something more intriguing: **the feedback types operate at fundamentally different abstraction levels**, and nobody has systematically characterized what each excels at.

Consider this: CodeRL [Le et al., 2022] uses unit test outcomes as rewards—a binary signal about *functional correctness* that tells you WHAT is wrong but not WHY. RLTF [Liu et al., 2023] improves on this with line-level error localization, getting closer to the HOW. Meanwhile, Self-Refine [Madaan et al., 2023] generates natural language critique—rich semantic feedback about code structure, readability, and design patterns that execution can never capture.

Here's my wild idea: **What if the feedback types aren't competitors but complementary along a signal fidelity spectrum?** Execution feedback provides ground truth about correctness (high signal, low semantic content). AI feedback provides rich semantic guidance (potentially noisy signal, high semantic content). The optimal post-training strategy might involve *temporal sequencing*—use execution feedback to establish functional correctness, then use AI feedback for refinement, or vice versa depending on the problem difficulty.

What if we designed a **Unified Feedback Ablation Framework** that isolates: (1) signal fidelity (correct vs. potentially incorrect), (2) semantic richness (binary pass/fail vs. natural language critique), and (3) feedback granularity (episode-level vs. token-level)? This would let us answer not just "which is better" but "for what type of problems, at what training stage, and along which dimension?"

**Key Points:**
- Execution vs. AI feedback may operate at different abstraction levels rather than being direct competitors
- A unified experimental framework could decompose feedback into orthogonal dimensions
- Temporal sequencing or hybrid approaches may outperform single-source feedback

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing framework, but let me apply rigorous scrutiny. The claim that feedback types operate at "different abstraction levels" needs operationalization before we can test it. What would disprove this hypothesis?

The evidence suggests we can design a controlled experiment using existing benchmarks and repositories. Here's my proposal for a **falsifiable experimental design**:

**Controlled Variables:**
- Base model: CodeT5-770M (used by both CodeRL and RLTF)
- Training compute budget: Fixed GPU-hours (24h on 8×V100, matching RLTF's setup)
- Evaluation protocol: pass@k (k=1,5,10) on HumanEval and MBPP
- Decoding strategy: nucleus sampling, p=0.95, temperature=0.6

**Independent Variables (Feedback Conditions):**
1. **Execution-only**: Unit test pass/fail + fine-grained error localization (RLTF-style)
2. **AI-only**: LLM self-critique without execution (Self-Refine-style, but applied at training time via distillation)
3. **Hybrid-sequential**: Execution → AI refinement
4. **Hybrid-parallel**: Both feedback types simultaneously

**Testable Predictions:**
- P1: If execution feedback dominates, Condition 1 should achieve highest pass@1 across ALL difficulty levels
- P2: If complementarity hypothesis holds, Conditions 3 or 4 should outperform pure conditions
- P3: If abstraction levels matter, we should see **interaction effects** between feedback type and problem difficulty

**What would convince us this is wrong?** If execution-only consistently dominates across all metrics and difficulty strata with no interaction effects, the complementarity hypothesis fails.

**Key Points:**
- Need operationalized definitions before testing "abstraction level" claims
- Propose 4-condition factorial design with existing benchmarks (HumanEval, MBPP)
- Interaction effects between feedback type and difficulty would support complementarity

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is methodologically sound, but I must ask: what makes this genuinely new versus incremental? The field already has CodeRL, RLTF, and Self-Refine—why should the community care about a comparison study?

The question we must ask is: **what new research directions does this open?**

Reviewing the literature, I see the gap isn't just "no controlled comparison exists"—it's that we lack a **theoretical framework** for predicting when each feedback type excels. A comparison study alone produces a table of numbers. But if we can explain WHY certain feedback types work better in certain conditions, we enable:

1. **Principled algorithm selection**: Practitioners can choose feedback strategies based on problem characteristics without expensive ablations
2. **Novel hybrid designs**: Understanding the underlying mechanisms enables designing better combinations
3. **Transfer across domains**: A theory that works for code generation should generalize to other verifiable generation tasks (math, chemistry, formal proofs)

The Self-Refine paper [Madaan et al., 2023] shows minimal gains on math reasoning (0.2% improvement) because "the model often fails to detect subtle errors." This suggests AI feedback struggles with **formal correctness verification**. Meanwhile, execution feedback struggles with **semantic quality** beyond correctness. This matters because...

**The real contribution isn't the comparison—it's identifying the decision boundary.** What problem characteristics predict which feedback type will dominate? If we can answer this, we've contributed something that shapes future research directions.

**Key Points:**
- Comparison tables alone are incremental; we need a predictive framework
- Core question: what problem characteristics predict feedback type effectiveness?
- Impact extends beyond code generation to any verifiable generation task

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Sage wants a "theoretical framework" and "decision boundary"—but we must assess whether this is technically achievable with existing resources. I focus on scientific soundness, not budgets.

**Technical feasibility assessment:**

1. **Is the base model comparison valid?** Yes. CodeT5-770M is used by both CodeRL and RLTF with published weights. Self-Refine operates on proprietary models (GPT-3.5, GPT-4), but we can approximate by using Self-Refine's prompting strategy on an open model or use distillation to inject AI feedback into training.

2. **Are the measurement methods theoretically valid?** Yes. pass@k is well-defined and widely adopted. HumanEval (164 problems) and MBPP (500 test problems) are established benchmarks with execution harnesses (bigcode-evaluation-harness).

3. **Can the proposed interventions work in principle?** Here's my concern: **Self-Refine is a test-time method, not a training method.** To create a fair "AI-only training" condition, we need to convert Self-Refine's feedback into training signals. This could be done via:
   - **Distillation**: Generate (code, AI-critique, refined-code) triples, then train on the refinements
   - **RLAIF-style**: Use AI feedback as a reward model proxy

Both are scientifically sound, but we must acknowledge this isn't pure Self-Refine—it's "Self-Refine-inspired training."

4. **Fundamental barriers?** The key challenge is that AI feedback's "correctness" is itself uncertain. Execution feedback is ground truth; AI feedback may hallucinate. This asymmetry makes direct comparison nuanced—we're comparing **verified signals** vs **probabilistic signals**.

**What evidence supports this?** Self-Refine's failure analysis shows 33% of failures came from "wrong location" in feedback and 61% from "wrong fix"—the AI feedback itself was incorrect.

**Key Points:**
- Experimental design is technically feasible with existing benchmarks and models
- Converting Self-Refine to a training signal requires RLAIF-style distillation (scientifically sound)
- Core asymmetry: execution = verified ground truth, AI = probabilistic (may hallucinate)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and Prof. Pax has identified the key insight! The asymmetry between verified and probabilistic feedback is exactly what we should build our hypothesis around. Let me strengthen this into a testable claim.

Building on 🔭 Dr. Nova's "abstraction levels" insight and ⚙️ Prof. Pax's feasibility analysis, here's a refined hypothesis:

**Core Hypothesis: Signal Fidelity Determines Feedback Utility**

*Under post-training alignment of code generation models, if we vary feedback source (execution vs AI-generated), then the relative improvement in pass@k will depend on the verification difficulty of the task, because execution feedback provides ground-truth signals while AI feedback provides probabilistically correct semantic guidance.*

**Mechanism:**
1. Execution feedback has 100% signal fidelity (pass/fail is deterministic) but low semantic richness (doesn't explain WHY)
2. AI feedback has <100% signal fidelity (may hallucinate) but high semantic richness (can explain patterns, suggest fixes)
3. For tasks where the model's primary failure mode is **syntactic/runtime errors**, execution feedback dominates (ground truth localization)
4. For tasks where the model's primary failure mode is **semantic design flaws**, AI feedback may provide richer guidance—IF it's accurate

**Evidence from literature:**
- RLTF's fine-grained feedback (error line localization) shows largest gains for compile/runtime errors [Liu et al., 2023]
- Self-Refine shows minimal gains on math reasoning where formal correctness matters [Madaan et al., 2023]
- CodeRL's critic model achieves only ~4-way classification accuracy, suggesting imperfect signal even within execution feedback

**Refinement addressing Prof. Rex's likely concern:** We operationalize "verification difficulty" using existing APPS difficulty levels (Introductory/Interview/Competition) as a proxy for task complexity.

**Key Points:**
- Hypothesis: Signal fidelity (verified vs probabilistic) determines feedback utility
- Mechanism: Execution dominates for syntactic/runtime errors; AI may help for semantic issues IF accurate
- Use APPS difficulty levels as operationalization of task complexity

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's hypothesis conflates two distinct dimensions:

1. **Signal fidelity** (verified vs probabilistic)
2. **Semantic richness** (binary vs explanatory)

These are NOT the same thing! RLTF's fine-grained feedback is BOTH high-fidelity AND semantically richer than CodeRL's episode-level reward—yet it's still execution feedback. Meanwhile, AI feedback like Self-Refine is low-fidelity but high semantic richness.

**The 2×2 matrix we should be testing:**

|  | Low Semantic Richness | High Semantic Richness |
|---|---|---|
| **High Fidelity** | CodeRL (episode reward) | RLTF (line-level errors) |
| **Low Fidelity** | ??? | Self-Refine |

The empty cell—low fidelity, low richness—would be random feedback, which is a useful control but not practically relevant.

**Critical question: What assumption is unstated here?**

The hypothesis assumes that AI feedback's low fidelity is the limiting factor. But Self-Refine fails on code optimization only achieving +8.2% improvement with GPT-3.5 [Madaan et al., 2023 Table 1]. Is this because:
(a) AI feedback is incorrect (fidelity problem)?
(b) The model can't effectively apply correct feedback (refinement problem)?
(c) The task itself is harder (confound)?

Self-Refine's own analysis says 33% wrong location + 61% wrong fix = 94% of failures from BAD FEEDBACK. This strongly supports (a)—the fidelity hypothesis.

**What would convince me this hypothesis is valid?** Show that when AI feedback accuracy is high (verified against execution), the improvement matches or exceeds execution-only feedback. This would confirm fidelity as the bottleneck.

**Key Points:**
- Hypothesis conflates fidelity and semantic richness—these are orthogonal
- Need 2×2 experimental design: fidelity (high/low) × richness (high/low)
- Self-Refine's 94% failure-from-bad-feedback supports fidelity as bottleneck

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's 2×2 matrix is brilliant! But wait—what if we can CREATE the missing hybrid condition? Imagine this:

**Execution-Verified AI Feedback (EVAF)**: Generate AI critique, then FILTER it through execution verification. Only apply AI suggestions that don't break passing tests.

This would be: **High Fidelity + High Semantic Richness** = the theoretical optimum!

Here's the creative leap: We don't need to choose between execution and AI feedback—we can use execution as a **gating mechanism** for AI feedback. The process:
1. Generate candidate code
2. AI provides rich semantic critique (Self-Refine style)
3. Apply suggested changes tentatively
4. Execute tests on the modified code
5. Only accept changes that maintain/improve test pass rate

This is essentially **verified refinement**. The AI provides the ideas; execution provides the filter.

**Connection to CodeT [Chen et al., 2022]:** This is philosophically similar to CodeT's approach—using LLM-generated tests + execution for ranking. We're extending this to feedback filtering rather than candidate ranking.

**Testable prediction:** If fidelity is truly the bottleneck, then EVAF should:
- Match or exceed pure execution feedback (same fidelity)
- Exceed pure AI feedback (higher fidelity)
- Potentially exceed both (fidelity + richness synergy)

This gives us a clear hypothesis for the controlled comparison:

**H1:** Execution-Verified AI Feedback achieves higher pass@k than either pure execution feedback OR pure AI feedback, on problems where the model's primary failure mode is semantic rather than syntactic.

**Key Points:**
- Creative synthesis: use execution as gating mechanism for AI feedback
- Creates High Fidelity + High Semantic Richness condition
- Testable hypothesis: EVAF outperforms pure methods on semantic-error-dominant problems

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's EVAF concept is promising, but let me stress-test the experimental design. The claim "EVAF outperforms pure methods on semantic-error-dominant problems" requires operationalization.

**Critical methodological question:** How do we identify "semantic-error-dominant" problems a priori? We can't use the outcome (whether AI feedback helped) to define the condition—that's circular.

**Proposed operationalization using existing benchmark metadata:**

1. **Syntactic-error-prone proxy:** Problems where baseline model (CodeT5-770M with SL-only) produces >50% compile/runtime errors
2. **Semantic-error-prone proxy:** Problems where baseline produces >50% "FailedTest" outcomes (code runs but wrong output)

This can be computed from a single baseline run before the main experiment, using HumanEval's 164 problems.

**Refined experimental design:**

| Condition | Fidelity | Richness | Implementation |
|---|---|---|---|
| A: Exec-Coarse | High | Low | CodeRL-style episode reward |
| B: Exec-Fine | High | Medium | RLTF-style line-level error |
| C: AI-Only | Variable | High | Self-Refine distilled to training |
| D: EVAF | High | High | AI feedback + execution gate |

**Predictions with falsification criteria:**
- P1: On syntactic-error-prone problems, B ≥ D > C (execution dominates when errors are localizable)
- P2: On semantic-error-prone problems, D > B ≥ C (EVAF wins when rich feedback is accurate and verifiable)
- P3: Overall pass@1, D should be within 2 percentage points of the best single-source method

**What result would disprove the hypothesis?** If D ≤ C on semantic-error-prone problems despite C having lower fidelity, then fidelity is NOT the bottleneck—something else is.

**Key Points:**
- Operationalize error types using baseline model failure modes (not circular)
- 4-condition design spanning the fidelity × richness space
- Falsification: if EVAF ≤ AI-only on semantic problems, fidelity hypothesis fails

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Now we're converging on something significant. Let me articulate why this matters for the field.

**What makes this genuinely new vs incremental:**

The contribution isn't "we compared feedback types"—it's the **theoretical framework** that fidelity and semantic richness are orthogonal dimensions, and the **practical innovation** of EVAF as a method to achieve both.

**How this advances the field:**

1. **Decomposition insight:** Prior work implicitly assumed execution = verified = good, AI = unverified = risky. We're showing this conflates fidelity with richness. Execution CAN be low-richness (episode rewards); AI CAN be made high-fidelity (through verification gating).

2. **Actionable algorithm:** EVAF isn't just a theoretical construct—it's implementable using existing components (Self-Refine prompts + unit test execution + accept/reject logic).

3. **Generalization potential:** The fidelity × richness framework applies beyond code:
   - Math: AI suggestions verified by formal proof checkers
   - Chemistry: AI-proposed molecules verified by simulation
   - Any domain with cheap automated verification

**The question we must ask: what new research directions does this open?**

This opens the "verified self-improvement" paradigm: use powerful but unreliable AI feedback, gated by cheaper but definitive verifiers. This is distinct from:
- RLHF (human provides feedback)
- RLAIF (AI provides unverified feedback)
- Pure execution RL (no semantic guidance)

We're proposing RLVF: Reinforcement Learning from **Verified** Feedback, where verification is automated and the feedback source is AI.

**Key Points:**
- Core contribution: fidelity × richness decomposition + EVAF as practical method
- Opens "verified self-improvement" paradigm beyond code (math, chemistry, any verifiable domain)
- Naming suggestion: RLVF (RL from Verified Feedback) to distinguish from RLAIF

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's RLVF framing is elegant, but let me ground this in technical feasibility. Here's what worries me:

**Concern 1: Verification coverage**

AI feedback often suggests structural changes (refactoring, API usage patterns) that don't change functional behavior. These changes would PASS execution tests but we can't verify if they're actually improvements. The "gating" only works for suggestions that affect correctness.

**Scientifically sound mitigation:** Restrict EVAF to correctness-affecting suggestions. For style/design feedback, use AI-only (accepting the fidelity limitation) or skip entirely.

**Concern 2: Test suite completeness**

The gating mechanism assumes tests are sufficient to detect regressions. But HumanEval has only ~7 tests per problem average. AI feedback might introduce bugs that slip through incomplete test suites.

**Evidence from literature:** CodeRL reports that some programs pass example tests but fail hidden tests. This is a known limitation of the benchmarks, not our method.

**Mitigation:** Report results on both example tests (used for gating) AND hidden tests (held-out evaluation). If EVAF performs well on hidden tests, it suggests the gating doesn't just overfit to visible tests.

**Technical implementation path:**

1. Use CodeT5-770M + salesforce/CodeRL codebase as foundation
2. Implement AI feedback generation using Self-Refine prompts on an instruction-tuned model (e.g., CodeLlama-Instruct)
3. Add execution gating: parse AI suggestions, apply diff, run tests, accept/reject
4. Train using RLTF-style online RL with the gated feedback as reward signal

This is technically feasible with existing repositories. The main engineering effort is the feedback parsing and diff application—nontrivial but achievable.

**Key Points:**
- EVAF can't verify style/design improvements, only correctness-affecting changes
- Test suite incompleteness is a known benchmark limitation, not method limitation
- Implementation path: CodeT5 + CodeRL foundation + Self-Refine prompts + execution gating

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent progress! Let me synthesize the emerging consensus into a refined, testable hypothesis that addresses the concerns raised.

**Refined Hypothesis:**

*Under controlled post-training alignment of CodeT5-770M on code generation benchmarks (HumanEval, MBPP), if we compare feedback strategies along the fidelity × richness dimensions, then Execution-Verified AI Feedback (EVAF) will achieve the highest pass@k on problems where the baseline model primarily fails due to semantic errors (incorrect logic, wrong algorithm), because EVAF combines ground-truth verification (high fidelity) with rich semantic guidance (AI critique), while pure execution feedback lacks the semantic richness to guide correct logic, and pure AI feedback lacks the fidelity guarantee to filter hallucinated suggestions.*

**Variables:**

| Variable | Type | Operationalization |
|---|---|---|
| **IV: Feedback Strategy** | Categorical | 4 levels: Exec-Coarse, Exec-Fine, AI-Only, EVAF |
| **DV: pass@k** | Continuous | k ∈ {1, 5, 10} on HumanEval/MBPP |
| **Moderator: Error Type** | Categorical | Syntactic-error-prone vs Semantic-error-prone (from baseline) |

**Controlled Variables:**
- Base model: CodeT5-770M
- Training budget: 24h on 8×V100
- Evaluation: bigcode-evaluation-harness, same decoding parameters

**Predictions (with falsification criteria):**

1. **P1 (main):** On semantic-error-prone problems, EVAF pass@1 > Exec-Fine pass@1 by ≥3 percentage points. *Falsified if*: EVAF ≤ Exec-Fine OR difference < 3pp.

2. **P2 (fidelity):** On semantic-error-prone problems, EVAF pass@1 > AI-Only pass@1. *Falsified if*: EVAF ≤ AI-Only (would suggest fidelity doesn't help).

3. **P3 (execution dominance):** On syntactic-error-prone problems, Exec-Fine pass@1 ≥ EVAF pass@1. *Falsified if*: EVAF significantly > Exec-Fine (would suggest AI feedback helps even for syntactic errors).

**Key Points:**
- Clear IV (4-level feedback strategy), DV (pass@k), moderator (error type)
- Three falsifiable predictions with specific thresholds
- Addresses Prof. Pax's concerns by focusing on correctness-affecting feedback

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally has tightened the hypothesis substantially. Let me probe the remaining weak points.

**Concern 1: The 3 percentage point threshold (P1)**

Why 3pp? On HumanEval, CodeRL achieves ~60% pass@1. A 3pp improvement is meaningful but arbitrary. What's the expected effect size given the intervention?

**Counter-argument:** We need SOME threshold to avoid claiming victory on noise. 3pp is reasonable given that RLTF improves over CodeRL by ~1-2pp (Table 3 in RLTF paper). EVAF should show larger gains if the hypothesis is correct because it addresses a different failure mode.

**Refinement:** Report effect sizes with confidence intervals. Claim support if the lower bound of the 95% CI for (EVAF - Exec-Fine) > 0 on semantic-error-prone problems.

**Concern 2: AI feedback quality depends on the AI model**

We're using CodeLlama-Instruct (or similar) for AI feedback generation. But Self-Refine used GPT-4, which is much more capable. Lower-quality AI feedback might not help even with verification gating.

**Counter-argument:** This is actually part of the test. If EVAF with a weaker AI (CodeLlama) outperforms AI-Only with the same AI, fidelity gating is valuable. If it doesn't, we learn that AI feedback quality is the bottleneck, not fidelity.

**Final concern: Confound between AI feedback model and base model**

If we use CodeLlama-Instruct for feedback and CodeT5 as the base model, they're different architectures. Any benefits might come from "ensemble effects" rather than feedback quality.

**Mitigation:** Use the same model family if possible (CodeT5 for both), or explicitly test if feedback from a weaker model (CodeT5-Instruct fine-tuned) still helps when verified.

**What would convince me?** The hypothesis is valid if:
1. EVAF > AI-Only on semantic problems (fidelity helps)
2. EVAF > Exec-Fine on semantic problems (richness helps)
3. Effect sizes have non-overlapping CIs with the null

**Key Points:**
- Replace arbitrary threshold with CI-based significance testing
- AI feedback quality is a feature, not a bug—testing weaker AI is informative
- Potential confound: use same model family for feedback if possible

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

Addressing Prof. Rex's concerns, here's the finalized experimental protocol with statistical rigor.

**Statistical Design:**

1. **Sample size justification:** HumanEval has 164 problems. With ~50% expected to be semantic-error-prone (based on prior CodeT5 baselines), we have ~82 problems per stratum. At α=0.05 and power=0.80, we can detect effect sizes of ~0.35 Cohen's d—sufficient for the expected 3-5pp differences.

2. **Primary analysis:** Mixed-effects logistic regression with problem as random effect, feedback strategy as fixed effect, error-type stratum as moderator. Report odds ratios with 95% CIs.

3. **Secondary analysis:** Bootstrap pass@k with 1000 resamples, report median and 95% percentile intervals.

**Addressing the AI model confound:**

Use a **2×2 nested design**:
- Factor 1: Feedback source (Execution vs AI)
- Factor 2: Verification gating (Present vs Absent)

| Condition | Feedback | Gating |
|---|---|---|
| Exec-Fine | Execution | N/A (implicit) |
| AI-Only | AI | Absent |
| EVAF | AI | Present |
| Control | Random | Absent |

The Random control (random accept/reject) isolates whether gating itself is useful beyond feedback quality.

**Revised predictions with statistical criteria:**

1. **P1:** In semantic-error stratum, β(EVAF) > β(Exec-Fine), p < 0.05, OR ≥ 1.5
2. **P2:** In semantic-error stratum, β(EVAF) > β(AI-Only), p < 0.05
3. **P3:** In syntactic-error stratum, β(Exec-Fine) ≥ β(EVAF), p > 0.05 (non-inferiority)

**Confounds controlled:**
- Same base model (CodeT5-770M)
- Same training compute
- Same decoding strategy
- Same evaluation harness
- Stratified by baseline error type (not circular because computed before intervention)

**Key Points:**
- Mixed-effects model accounts for problem-level variance
- 2×2 nested design isolates feedback source vs gating mechanism
- Random control condition tests gating value independent of feedback quality

---

### Exchange 14

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've reached convergence! Let me synthesize the final consensus hypothesis.

**FINAL HYPOTHESIS: Execution-Verified AI Feedback for Code Generation**

**Hypothesis ID:** H-EVAF-v1

**Core Statement (Under-If-Then-Because):**

*Under post-training alignment of code generation models using CodeT5-770M on HumanEval/MBPP benchmarks:*

*If we apply Execution-Verified AI Feedback (EVAF)—where AI-generated code critiques are filtered through unit test execution before being used as training signals—*

*Then EVAF will achieve significantly higher pass@1 than pure execution feedback on problems where the baseline model primarily fails due to semantic errors (incorrect logic rather than syntax/runtime errors),*

*Because EVAF combines ground-truth verification (filtering out hallucinated AI suggestions) with rich semantic guidance (explaining WHY code is wrong), addressing the orthogonal dimensions of signal fidelity and semantic richness that neither pure approach satisfies alone.*

**Null Hypothesis (H0):**

*There is no significant difference in pass@1 between EVAF and Exec-Fine feedback strategies on semantic-error-prone code generation problems (OR = 1.0, 95% CI includes 1.0).*

**Mechanism (Causal Chain):**

1. AI feedback provides semantically rich suggestions (variable naming, algorithm choice, design patterns)
2. Some AI suggestions are incorrect (hallucinations, wrong fixes) with ~61% error rate per Self-Refine analysis
3. Execution gating filters suggestions through unit tests, keeping only those that maintain/improve correctness
4. Filtered feedback retains semantic richness while achieving high fidelity
5. High-fidelity, high-richness feedback enables learning both WHAT to fix and HOW to fix it
6. Result: Improved pass@k especially on problems requiring semantic understanding

**Key Assumptions:**
- A1: Baseline error type distribution is stable across training
- A2: AI feedback errors are detectable via test execution (correctness-affecting)
- A3: Filtered AI feedback volume is sufficient for learning (not filtered out entirely)
- A4: HumanEval/MBPP test suites are sufficient to catch regressions

**Key Points:**
- Hypothesis decomposed into falsifiable components with clear mechanism
- EVAF is a concrete, implementable method using existing components
- Statistical criteria established for confirmation/refutation

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is now well-formed. Let me register remaining concerns for the experimental team to address.

**Outstanding risks:**

1. **A3 violation risk:** If AI feedback is mostly filtered out by execution gating (high reject rate), EVAF reduces to pure execution feedback. Mitigation: Track accept/reject ratios; if accept rate < 10%, the experiment is underpowered to test EVAF.

2. **Benchmark saturation:** CodeT5-770M already achieves ~25-30% pass@1 on HumanEval. With RLTF-style training, this might reach ~35-40%. Ceiling effects may limit observable differences. Mitigation: Use APPS (harder) as secondary benchmark.

3. **Semantic error operationalization:** The "50% FailedTest vs 50% Error" split is somewhat arbitrary. Sensitivity analysis with different thresholds (40%, 60%) should confirm robustness.

4. **Generalization question:** If EVAF works, does the improvement transfer zero-shot to MBPP (as RLTF shows for pure execution)? This is important for practical impact.

**What would convince me the hypothesis is FALSE:**

- EVAF ≤ Exec-Fine on semantic-error-prone problems (rich feedback doesn't help even when verified)
- EVAF ≤ AI-Only (verification gating provides no benefit, suggesting AI feedback accuracy is already sufficient)
- Accept rate < 10% (execution gating is too aggressive, filtering out useful feedback)

**What would convince me the hypothesis is TRUE:**

- EVAF > Exec-Fine AND EVAF > AI-Only on semantic problems, with non-overlapping CIs
- Accept rate between 20-60% (gating is selective but not eliminative)
- Effect holds on APPS (generalization)
- Zero-shot transfer to MBPP matches or exceeds pure execution methods

**Verdict: The hypothesis is ready for experimental testing.**

**Key Points:**
- Key risks: accept rate too low, benchmark saturation, operationalization sensitivity
- Clear success/failure criteria established
- Hypothesis is testable with existing benchmarks and models

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The EVAF concept is a genuine creative contribution that reframes the execution vs AI feedback debate. Rather than choosing between them, we use execution as a verification layer for AI feedback, creating a new paradigm. The fidelity × richness decomposition provides a theoretical framework absent from prior work.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is clearly falsifiable with specific predictions (P1: EVAF > Exec-Fine on semantic errors, P2: EVAF > AI-Only, P3: Exec-Fine ≥ EVAF on syntactic errors). Statistical criteria are well-defined (mixed-effects OR with CIs). The experimental design uses existing benchmarks (HumanEval, MBPP, APPS) and models (CodeT5-770M) with controlled variables.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This contribution opens the "verified self-improvement" paradigm applicable beyond code generation. The fidelity × richness framework has implications for any domain with cheap automated verification (math, chemistry, formal proofs). If successful, EVAF provides a principled way to leverage AI feedback without sacrificing correctness guarantees.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The experimental design is technically feasible using existing repositories (salesforce/CodeRL, madaan/self-refine), evaluation harnesses (bigcode-evaluation-harness), and compute resources (8×V100 for 24h). The main engineering challenge—parsing and applying AI feedback diffs—is nontrivial but achievable. No new data collection or human annotation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **Execution-Verified AI Feedback (EVAF)** as a novel hypothesis for code generation alignment. The core insight is that execution feedback and AI feedback operate along orthogonal dimensions—fidelity and semantic richness—rather than being direct competitors. EVAF achieves both by using execution tests to gate AI-generated critique, filtering out hallucinated suggestions while retaining semantically rich guidance.

The hypothesis predicts that EVAF will outperform pure execution feedback on problems where models primarily fail due to semantic errors (wrong logic, incorrect algorithm) rather than syntactic issues, because it addresses the "WHY" that execution feedback misses while maintaining the correctness guarantees that AI feedback lacks.

The experimental design uses a 4-condition factorial (Exec-Coarse, Exec-Fine, AI-Only, EVAF) with problem stratification by baseline error type. Primary evaluation on HumanEval with APPS and MBPP as secondary/transfer benchmarks. Statistical analysis via mixed-effects logistic regression with problem-level random effects.

This work opens the RLVF (Reinforcement Learning from Verified Feedback) paradigm—using automated verifiers to gate AI feedback—with applications beyond code generation to any domain with cheap formal verification.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Accept rate risk: If execution gating filters >90% of AI suggestions, EVAF degenerates to pure execution feedback. Must monitor and report accept rates.
- Benchmark saturation: HumanEval ceiling effects may limit observable differences. APPS provides headroom.
- Operationalization sensitivity: The 50% syntactic/semantic split threshold should be tested with sensitivity analysis.
- **Mitigation Strategy:** Track accept rates throughout training; use APPS as primary if HumanEval shows ceiling effects; report results at multiple stratification thresholds (40%, 50%, 60%).


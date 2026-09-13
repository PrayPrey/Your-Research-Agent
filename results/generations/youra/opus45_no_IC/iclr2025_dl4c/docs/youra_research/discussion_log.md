# Phase 2A Research Discussion Log

## Briefing Context

**Gap ID:** gap1-feedback-type-comparison
**Gap Title:** Systematic Comparison of Feedback Types
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Gap Summary

**Current State:** Existing work uses single feedback types (PPOCoder: test pass, StepCoder: compiler, RLPF: staged). No controlled comparison across feedback types on same model/benchmark.

**Missing Piece:** Ablation study comparing compile-time errors, runtime errors, test pass rates, and execution traces on identical experimental setup.

**Potential Impact:** Would directly answer the primary research question and guide practitioners on feedback type selection.

### Key Evidence from Phase 1

**Academic Papers (Verified):**
- PPOCoder (2023, Shojaee et al.): PPO with test pass rates as reward
- StepCoder (2024, Dou et al.): Compiler feedback + CCCS curriculum + FGO masking
- RLPF (2026, Jing et al.): Staged rewards - execution progress + efficiency
- InterCode (2023, Yang et al.): Interactive coding as RL environment
- EG-CFG (2025): Inference-time execution guidance, 99.4% HumanEval

**Implementation Resources (Verified):**
- PPOCoder (GitHub, 116 stars): Test-based reward
- APPS_Plus/StepCoder (GitHub, 73 stars): Compiler feedback
- OpenRLHF (GitHub, 9891 stars): Production RLHF infrastructure
- eg_cfg (GitHub, 49 stars): Inference-time execution guidance

### Feasibility Constraints (Pipeline-Enforced)

- MUST use existing real datasets and existing benchmarks
- REJECT ideas requiring new benchmarks, rubrics, or scoring frameworks
- REJECT ideas requiring synthetic/generated data
- REJECT ideas requiring human evaluation or annotation

### Previous Failure / Routing Context

*No previous failure contexts. This is the first Phase 2A attempt.*

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? The existing work treats execution feedback types as independent signals, but I see an unexplored opportunity: **what if different feedback types carry fundamentally different information density about the code's semantic correctness?**

Consider this: compile-time errors tell us about syntactic and type-level violations—they're precise but shallow. Runtime errors reveal dynamic behavior failures—deeper but noisier. Test pass rates give outcome signals—high-level but sparse. And execution traces? They're the richest signal, showing exactly which code paths executed.

Here's my wild idea: **feedback types might form an information hierarchy where combining them creates emergent alignment signals that no single type achieves alone**. The papers use them separately, but what if there's a principled way to fuse them based on their complementary information content?

Looking at the evidence: PPOCoder achieves solid results with test pass rates alone, StepCoder adds compiler feedback with curriculum learning, and RLPF introduces staged rewards combining execution progress with efficiency. But nobody has asked: **what is the optimal composition of these signals for different code generation scenarios?**

**Key Points:**
- Different feedback types may carry orthogonal information about code correctness
- Current SOTA uses single or ad-hoc combinations without principled analysis
- Opportunity: characterize information content of each feedback type and design optimal compositions

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your hypothesis about "information hierarchy" is intriguing but dangerously vague. Let me stress-test this. You claim different feedback types carry "fundamentally different information density"—but what exactly would disprove this?

Here's my concern: the papers you cite already show that different feedback types work. PPOCoder with test pass rates, StepCoder with compiler feedback—both achieve reasonable results. **The existence of multiple working approaches doesn't prove they carry different information**; they might simply be redundant signals for the same underlying correctness property.

For this hypothesis to be scientific, we need:

1. **A falsifiable prediction**: If feedback types are truly orthogonal in information content, then a model trained with Type A should fail on problems that a model trained with Type B solves, and vice versa. If we find substantial overlap in solved problems, the "different information" claim weakens.

2. **Measurable operationalization**: How do we quantify "information density"? You can't just hand-wave. I propose: mutual information between feedback signal and ground-truth correctness, measured across a held-out problem set.

3. **Controlled comparison**: Same base model, same training budget, same benchmark. Vary ONLY the feedback type. Without this, any observed differences could be confounded by architecture, data, or optimization differences.

**Key Points:**
- "Different information content" requires falsifiable prediction: non-overlapping problem coverage
- Need operational definition: mutual information between feedback and correctness
- Must control for confounds: identical setup except feedback type

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this discussion in reality. Both of you are circling around a hypothesis, but I need to assess whether the proposed mechanism is technically sound.

🔬 Prof. Vera's experimental design is solid, but let me check the fundamental barriers:

**Technical Feasibility Assessment:**

1. **Feedback Collection**: Can we actually collect all four feedback types (compile errors, runtime errors, test pass rates, execution traces) from the same codebase?
   - Compile errors: Easy—any compiler provides this
   - Runtime errors: Requires execution sandbox—HumanEval/MBPP already have this
   - Test pass rates: Standard in existing benchmarks
   - Execution traces: Requires instrumentation (coverage tools, tracing)—**this is the hardest**, but Python's `coverage.py` and similar tools make it achievable

2. **Reward Signal Integration**: Can these signals be meaningfully converted to scalar rewards for RL?
   - Binary signals (compile pass/fail, test pass/fail): Trivial
   - Error messages (text): Requires parsing or embedding—feasible but adds complexity
   - Execution traces (structured data): Requires aggregation (e.g., coverage percentage, path complexity)—**achievable but needs careful design**

3. **Fair Comparison Validity**: Is it scientifically valid to compare these signals head-to-head?
   - **Yes, with caveats**: Some signals (test pass) require test cases; others (compile) don't. We must ensure the comparison accounts for information asymmetry in signal availability.

**Key Points:**
- All four feedback types are technically collectable from standard code benchmarks
- Execution traces require instrumentation but tools exist (coverage.py)
- Fair comparison requires accounting for information availability differences

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me step back and ask: **what does this actually mean for the field?**

The technical discussion is progressing, but I need to evaluate whether this research gap—a systematic comparison of feedback types—represents a genuine scientific contribution or just an incremental benchmark exercise.

**Significance Assessment:**

1. **Current State**: The field has converged on execution feedback for code RL, but practitioners choose feedback types based on convenience or availability, not principled analysis. PPOCoder uses test pass because it's easy; StepCoder adds compiler because it helps with long code. There's no guidance.

2. **Contribution Type**: This would be a **methodological contribution**—not a new algorithm, but a framework for understanding when and why to use different feedback types. Such contributions are valuable but require strong experimental evidence.

3. **Impact Pathway**: If we establish that (a) feedback types have different strengths, and (b) we can characterize when each is optimal, then practitioners gain a principled selection framework. This could change how future execution feedback systems are designed.

4. **Risk of Incremental Work**: The danger is that we run ablations and find "all feedback types work similarly." This would be a negative result—publishable but less impactful. We need a clear hypothesis that predicts **differential** performance.

I agree with 🔬 Prof. Vera: we need a falsifiable prediction. Let me propose one: **Compile-time feedback will outperform test-pass feedback on problems with complex type constraints, while test-pass feedback will outperform on problems requiring runtime-only correctness.**

**Key Points:**
- This is a methodological contribution: principled feedback selection framework
- Impact depends on finding differential performance, not "all equal" result
- Propose: feedback types have problem-type-specific advantages (type-heavy vs runtime-only)

---

### Exchange 5

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Hold on—I see multiple assumptions that need stress-testing before we proceed.

**Challenge 1: The "Orthogonal Information" Assumption**

🔭 Dr. Nova claims feedback types carry "orthogonal information." But consider: a program that fails compilation will also fail tests. A program with runtime errors will (usually) fail tests. **Test pass rates may already subsume the information in compile and runtime errors.** If test pass is a superset signal, then comparing them is comparing a rich signal to its degraded versions—not apples to apples.

**Challenge 2: The "Problem-Type-Specific Advantage" Hypothesis**

🎯 Dr. Sage proposes that compile feedback excels on type-heavy problems. But modern compilers catch type errors at compile time—so **any correct program must already pass compilation**. The compile feedback signal is binary (pass/fail) and provides no gradient for optimization once the code compiles. How does this help learning?

**Challenge 3: Confounding from Feedback Granularity**

The feedback types differ not just in content but in **granularity**:
- Compile errors: Per-line error messages
- Runtime errors: Stack traces with line info
- Test pass: Per-function binary
- Execution traces: Per-statement coverage

Comparing feedback types without controlling for granularity is comparing apples and oranges. Are we studying feedback **type** or feedback **granularity**?

**What Would Convince Me:**

1. Show that test pass does NOT subsume compile/runtime info (counterexamples exist)
2. Define the independent variables clearly: feedback type AND granularity as separate factors
3. Identify problems where compile-passing code still benefits from compile feedback (unclear how)

**Key Points:**
- Test pass may subsume compile/runtime information—challenge the orthogonality claim
- Once code compiles, compile feedback is binary and provides no learning gradient
- Must separate feedback TYPE from feedback GRANULARITY as experimental factors

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex raises valid challenges. Let me address them constructively and refine our hypothesis.

**Addressing Challenge 1: Test Pass Subsumption**

You're right that a failing compilation implies failing tests. But the converse is NOT true: **a compiling program can fail tests, and DIFFERENT compile errors predict different test failures**. The information content isn't redundant—it's hierarchical.

More importantly, the timing differs: compile feedback is available DURING generation (can guide partial programs), while test feedback requires complete, executable code. StepCoder's FGO (Fine-Grained Optimization) exploits this by masking tokens that were never executed. **The learning signal isn't just about final correctness but about intermediate feedback availability.**

**Addressing Challenge 2: Binary Compile Feedback**

You're correct that pass/fail is sparse. But RLPF (2026) already solves this: they order failed programs by **execution progress**—how far the program got before failing. We can apply the same principle to compile errors: **order by how many sub-expressions/statements compile successfully**. This converts binary feedback to a dense signal.

**Addressing Challenge 3: Granularity Confound**

This is the strongest concern. I propose we **separate feedback content from feedback granularity** as orthogonal experimental factors:

- **Feedback Content**: Compile, Runtime, Test, Trace (what kind of signal)
- **Feedback Granularity**: Token, Line, Function, Program (how fine-grained)

Our hypothesis becomes: **Both content and granularity independently affect alignment performance, with an interaction effect where fine-grained compile feedback and coarse-grained test feedback are optimal for their respective content types.**

**Key Points:**
- Information is hierarchical, not redundant—compile errors predict test failures but add timing
- Binary compile feedback can be made dense via execution progress ordering (RLPF approach)
- Refined hypothesis: content and granularity are separable factors with interaction effects

---

### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

🛡️ Dr. Ally's refinement is much stronger. Let me formalize the experimental design that would test this.

**Refined Hypothesis (H1):**
Under controlled conditions (same model, training budget, benchmark), if we vary feedback content (compile, runtime, test, trace) and feedback granularity (token, line, function, program) independently, then:
- (a) Both factors significantly affect pass@k performance
- (b) The optimal granularity differs by content type (compile benefits from fine-grained; test from coarse-grained)
- (c) Multi-content combinations outperform single-content approaches

**Null Hypothesis (H0):**
Feedback content and granularity have no significant effect on pass@k, or any observed effects are explained by confounding variables (training signal density, information availability timing).

**Experimental Design:**

1. **Base Model**: CodeLlama-7B (or similar, with frozen architecture)
2. **Training Protocol**: PPO with 10k steps (or GRPO for simpler training)
3. **Benchmark**: HumanEval + MBPP (standard), split by problem characteristics
4. **Independent Variables**:
   - Content: {Compile, Runtime, Test, Trace, Compile+Test, All}
   - Granularity: {Token, Line, Function, Program}
5. **Dependent Variables**:
   - Primary: pass@1, pass@10 on held-out test set
   - Secondary: Training efficiency (samples to convergence)
6. **Controls**: Identical hyperparameters, random seeds, evaluation protocol

**Success Criteria:**
- H1(a): ANOVA p < 0.05 for both content and granularity main effects
- H1(b): Post-hoc comparison shows granularity × content interaction (p < 0.05)
- H1(c): Multi-content > single-content (paired t-test, p < 0.05)

**Key Points:**
- Formalized two-factor experimental design: content × granularity
- Testable predictions with statistical criteria
- Success requires main effects, interaction effects, and combination advantage

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera's experimental design is rigorous, but I must assess whether this is practically achievable.

**Feasibility Analysis:**

1. **Implementation of Token-Level Feedback**:
   - For compile errors: Possible via incremental parsing—check partial code validity
   - For runtime errors: **Problematic**—can't execute incomplete code
   - For test pass: **Impossible**—tests require complete functions
   - For traces: **Impossible**—requires execution
   
   **Verdict**: Token-level granularity only feasible for compile feedback. The factorial design (4 content × 4 granularity) collapses to a constrained design where not all cells are fillable.

2. **Execution Trace Collection**:
   - Python: `coverage.py` with branch coverage, `sys.settrace` for line-by-line
   - Overhead: ~10-20x slower execution—acceptable for small benchmarks
   - **Verdict**: Feasible for HumanEval/MBPP scale

3. **Training Compute**:
   - PPO on 7B model × ~16 experimental conditions × 3 seeds = ~48 training runs
   - Each run: ~2-4 hours on 8×A100 (based on OpenRLHF estimates)
   - **Total**: ~100-200 GPU-hours—**reasonable for academic setting**

4. **Existing Infrastructure**:
   - OpenRLHF provides PPO infrastructure
   - InterCode provides execution sandbox
   - **Verdict**: Building blocks exist; integration required but not fundamental barrier

**Recommended Design Adjustment:**

Given token-level granularity is only feasible for compile feedback, I propose a **reduced factorial design**:
- Compile: {Token, Line, Function, Program}
- Runtime/Test/Trace: {Line, Function, Program}

This yields ~13 conditions (not 16), all implementable.

**Key Points:**
- Token-level granularity only feasible for compile feedback (others need executable code)
- Execution trace collection feasible with ~10-20x overhead
- ~100-200 GPU-hours total—achievable for academic research
- Recommend reduced factorial design with 13 implementable conditions

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

The experimental design is taking shape, but I want to push on the **mechanism**. We're designing an ablation study, but we haven't articulated WHY different feedback types should produce different learning signals.

Here's my mechanism hypothesis: **Feedback types differ in their error localization precision, which affects credit assignment in RL.**

Consider the learning problem: given a failed program, which tokens were responsible? This is credit assignment. Different feedback types provide different localization:

1. **Compile errors**: Point directly to the error location (line, column). Perfect localization.
2. **Runtime errors**: Provide stack trace—good localization but may blame symptoms, not causes.
3. **Test failures**: Only say "wrong answer"—no localization (sparse reward problem).
4. **Execution traces**: Show what DID execute—localization by exclusion (untouched code might be the problem).

**The mechanism**: Fine-grained feedback (compile) provides dense, localized credit assignment, enabling faster learning on structure errors. Coarse-grained feedback (test) requires the model to self-discover error locations, which may work better for semantic errors that compilers can't catch.

**Prediction from mechanism**: Models trained with compile feedback will show faster initial learning (sharper loss curves) but may plateau earlier. Models trained with test feedback will learn slower but achieve higher final performance on semantically complex problems.

**Key Points:**
- Mechanism: Feedback types differ in error localization precision
- Localization affects credit assignment in RL (which tokens to update)
- Prediction: Compile = faster learning, earlier plateau; Test = slower learning, higher ceiling

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

🔭 Dr. Nova's mechanism is compelling but needs stress-testing.

**Challenge: The "Localization = Better Learning" Assumption**

You assume compile errors' precise localization helps credit assignment. But RL doesn't work at token level in standard implementations—PPO updates the entire policy based on episode reward. **The model doesn't directly use error location; it learns implicitly from reward differences across generations.**

For localization to help, we'd need:
- Token-level advantage estimation (not standard)
- Or the model learning to attend to error locations (unclear if this happens)

**Challenge: The "Compile Plateaus, Test Exceeds" Prediction**

This predicts compile feedback is "too easy"—the model learns to pass compilation but not semantics. But StepCoder shows compile + test combined works well. **If compile plateaus, why does adding it to test help in StepCoder?**

Alternative explanation: Compile feedback provides a **curriculum**—easier problems first (pass compilation), then harder (pass tests). The improvement isn't from compile feedback per se, but from curriculum structure.

**Refinement Request:**

If the mechanism is credit assignment localization, we need to:
1. Actually implement token-level credit (e.g., StepCoder's FGO approach)
2. Measure whether models attend to error locations (attention analysis)
3. Disentangle localization effect from curriculum effect

**What Would Strengthen the Hypothesis:**

A cleaner claim: **Fine-grained optimization (masking non-executed tokens, as in StepCoder FGO) provides the primary benefit of compile/trace feedback, independent of the feedback content itself.**

This is testable: FGO with test feedback vs. standard PPO with compile feedback. If FGO-test wins, the mechanism is granularity, not content.

**Key Points:**
- Standard PPO doesn't use error localization—need token-level credit for mechanism to work
- StepCoder's success may be curriculum effect, not compile feedback per se
- Propose cleaner test: FGO with test vs. standard PPO with compile, to disentangle factors

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex identifies a crucial confound: **granularity mechanism (FGO) vs. content mechanism**. Let me synthesize and strengthen.

**Refined Hypothesis Structure:**

We actually have TWO separable hypotheses:

**H1 (Content Hypothesis):** Different feedback TYPES (compile vs runtime vs test vs trace) carry complementary information about code correctness.
- **Test**: Does combining types outperform single types, controlling for granularity?
- **Mechanism**: Information diversity—errors caught by compile ≠ errors caught by test

**H2 (Granularity Hypothesis):** Fine-grained credit assignment (FGO, token-level masking) improves learning efficiency regardless of feedback type.
- **Test**: Does FGO improve ANY feedback type, not just compile?
- **Mechanism**: Credit assignment precision—mask what didn't execute

**Experimental Design to Disentangle:**

| Condition | Feedback Type | Granularity | What It Tests |
|-----------|--------------|-------------|---------------|
| A1 | Test | Standard (episode) | Baseline |
| A2 | Test | FGO (token mask) | H2 |
| B1 | Compile | Standard | H1 vs A1 |
| B2 | Compile | FGO | H1+H2 |
| C1 | Compile+Test | Standard | H1 combination |
| C2 | Compile+Test | FGO | H1+H2 combination |

**Predictions:**
- H1 supported if: B1 > A1 (compile content helps) AND C1 > B1 (combination helps)
- H2 supported if: A2 > A1 (FGO helps test) AND B2 > B1 (FGO helps compile)
- Interaction: If B1-A1 < C2-C1, then content and granularity synergize

This design cleanly separates the factors 🔍 Prof. Rex identified.

**Key Points:**
- Two separable hypotheses: H1 (content) and H2 (granularity/FGO)
- 6-condition factorial design disentangles the effects
- Clear predictions for when each hypothesis is supported

---

### Exchange 12

🎯 **Dr. Sage** (Research Impact Evaluator):

This is converging well. Let me assess the scientific contribution of this refined hypothesis.

**Contribution Assessment:**

1. **Novel Contribution**: The disentanglement of content vs. granularity effects is genuinely novel. Existing work (StepCoder) conflates them. A clean factorial study would provide the first principled understanding of which factor matters more.

2. **Practical Impact**: If H2 (granularity/FGO) dominates H1 (content), practitioners should focus on fine-grained optimization techniques rather than collecting richer feedback types. This simplifies deployment—test feedback + FGO is cheaper than multi-signal collection.

3. **Theoretical Contribution**: The credit assignment mechanism (localization → better gradients) connects to RL theory. If validated, this explains WHY certain approaches work, enabling principled design of future methods.

**Remaining Gap:**

One aspect underexplored: **transfer and generalization**. We've focused on HumanEval/MBPP (simple problems). Does the optimal feedback strategy change for more complex tasks (SWE-bench, real-world repositories)?

I propose adding a secondary experiment: train on HumanEval, evaluate transfer to MBPP and vice versa. If feedback types affect transfer differently, that's a significant practical finding.

**Key Points:**
- Novel: First clean disentanglement of content vs. granularity effects
- Practical: Guides practitioners on where to invest (FGO vs. feedback collection)
- Suggest adding: Transfer experiment (train on X, test on Y) to assess generalization

---

### Exchange 13

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The factorial design is solid. Let me verify final feasibility with the 6-condition setup.

**Final Feasibility Check:**

1. **FGO Implementation**: StepCoder's APPS_Plus repo (GitHub, 73 stars) provides FGO. We can adapt this to work with test-only and combined feedback. **Feasible—code exists.**

2. **Compute Requirements**:
   - 6 conditions × 3 seeds = 18 runs
   - Each run: ~2-4 hours on 8×A100 (PPO training)
   - Total: ~36-72 GPU-hours—**very reasonable**

3. **Benchmark Selection**:
   - HumanEval (164 problems): Clean, well-understood
   - MBPP (974 problems): Larger scale
   - Transfer: Train on one, test on other—**feasible, no additional data needed**

4. **Measurement Validity**:
   - pass@1, pass@10: Standard metrics, well-defined
   - Training efficiency: Samples to reach threshold—well-defined
   - Statistical power: 3 seeds × 2 benchmarks gives reasonable variance estimates

**One Technical Concern:**

FGO requires execution traces to know which tokens to mask. If test feedback provides execution coverage, FGO works. If test feedback is binary pass/fail only, we need to collect traces anyway. This means **FGO conditions implicitly add trace information**.

**Mitigation**: Document that FGO conditions use trace-based masking. Compare:
- Test (binary) + FGO (trace-based masking) vs.
- Test (binary) + Standard PPO

The masking IS the trace information, so we're really comparing: does trace information help when converted to masking?

**Key Points:**
- 18 total runs, ~36-72 GPU-hours—feasible for academic research
- StepCoder codebase provides FGO implementation
- Technical note: FGO inherently uses trace information for masking—document this

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Final experimental design formalization.

**HYPOTHESIS:**

**Core Statement (Under-If-Then-Because):**
Under controlled PPO training on code generation benchmarks, if we independently vary feedback content (compile, test, combined) and granularity mechanism (standard, FGO), then we observe:
1. Granularity (FGO) provides larger performance gains than content variation
2. Combined content with FGO achieves best overall performance
3. FGO transfers the benefit of trace information without explicit trace reward

...because FGO enables precise credit assignment by masking non-executed code, addressing the sparse reward problem regardless of feedback content.

**Alternative Hypothesis (H0):**
There is no significant difference in pass@k performance between conditions, or observed differences are explained by training signal density confounds.

**Variables:**
- **IV1**: Feedback Content {Compile-only, Test-only, Compile+Test}
- **IV2**: Granularity Mechanism {Standard PPO, FGO}
- **DV1** (primary): pass@1 on HumanEval (held-out)
- **DV2** (secondary): pass@10, training samples to threshold
- **Controlled**: Model (CodeLlama-7B), hyperparameters, random seeds

**Predictions:**
- **P1**: FGO improves ALL content types (A2>A1, B2>B1, C2>C1)
- **P2**: Content combinations outperform singles (C1>B1>A1)
- **P3**: FGO effect size > Content effect size (main effect comparison)

**Success Criteria:**
- P1: Paired t-test p<0.05 for each FGO comparison
- P2: ANOVA with post-hoc Tukey HSD p<0.05
- P3: Eta-squared for FGO > Eta-squared for Content

**Key Points:**
- Formalized hypothesis with Under-If-Then-Because structure
- 2×3 factorial design with clear predictions
- Statistical success criteria defined for each prediction

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me give final stress-test before we converge.

**Remaining Concerns (Minor):**

1. **Baseline Strength**: Standard PPO with test feedback is the weakest baseline. For a fair comparison, we should include a strong baseline: PPO with test + execution progress (RLPF-style staged reward). Otherwise, we might show FGO beats weak baseline, not that it beats best alternative.

2. **FGO Implementation Fidelity**: Using StepCoder's FGO assumes their implementation is correct and optimal. Should we include an ablation: FGO with different masking thresholds?

3. **Benchmark Ceiling**: HumanEval is nearly saturated (EG-CFG gets 99.4%). Training improvements may not be visible at pass@1 if baseline already achieves ~80%+. Consider pass@1 gap from oracle (room for improvement) as additional metric.

**Mitigation Strategies:**

1. Add condition: Test + RLPF-staged as strong baseline (7th condition)
2. Report FGO masking coverage stats (what % of tokens masked on average)
3. Report pass@1 with confidence intervals; interpret relative to baseline headroom

**Overall Assessment:**

Despite these minor concerns, **the hypothesis is now well-formed, testable, and novel**. The disentanglement of content vs. granularity is the key contribution. The experimental design is feasible with existing code and reasonable compute.

**My Verdict: CONVERGED with minor additions**

**Key Points:**
- Suggest adding RLPF-staged baseline for fair comparison to SOTA
- Report FGO masking statistics for implementation transparency
- Use pass@1 headroom analysis given near-saturated benchmarks
- Overall: hypothesis is ready for Phase 2B with minor additions

---

### Exchange 16

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Synthesizing the discussion into final consensus.

**EMERGED HYPOTHESIS SUMMARY:**

**Title:** Content-Granularity Disentanglement for Execution Feedback in Code RL

**Core Claim:** The effectiveness of execution feedback in code generation RL is determined by two separable factors: (1) feedback CONTENT (what information is provided: compile, test, trace) and (2) feedback GRANULARITY (how credit is assigned: standard episode reward vs. FGO token masking). Granularity (FGO) provides larger gains than content variation, but combining both achieves optimal performance.

**Mechanism:** FGO converts sparse episode rewards into dense token-level credit by masking tokens that were never executed during test runs. This addresses the credit assignment problem in RL—the model receives gradient signal only for code that actually ran. Content variation (compile vs. test) provides complementary error types, but without fine-grained credit assignment, this benefit is limited.

**Key Predictions:**
1. **P1 (Granularity Dominance):** FGO improves performance across ALL feedback content types (effect size η² > 0.3)
2. **P2 (Content Benefit):** Combining compile and test feedback outperforms single types (p < 0.05)
3. **P3 (Synergy):** FGO + combined content achieves highest performance, exceeding sum of individual effects

**Novelty:** First controlled study disentangling content vs. granularity effects in execution feedback for code RL. Prior work (StepCoder) conflates these factors.

**Experimental Setup:**
- Model: CodeLlama-7B
- Benchmark: HumanEval + MBPP
- Design: 2 (Granularity: Standard/FGO) × 3 (Content: Compile/Test/Combined) + RLPF baseline
- Metrics: pass@1, pass@10, training efficiency
- Baselines: Standard PPO (test), PPO + RLPF staged rewards

**Feasibility:** 21 total runs (~50-100 GPU-hours), existing code (StepCoder, OpenRLHF), standard benchmarks.

**Key Points:**
- Consensus reached on content vs. granularity disentanglement hypothesis
- FGO as primary mechanism for credit assignment improvement
- 7-condition experimental design with strong baselines
- ~50-100 GPU-hours, fully feasible with existing infrastructure

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis represents a genuinely novel contribution—first controlled study to disentangle content vs. granularity effects in execution feedback for code RL. The mechanism (FGO as credit assignment enabler) provides theoretical grounding beyond mere ablation.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clear, testable predictions (P1-P3) with statistical success criteria. The 2×3 factorial design enables clean causal inference. Null hypothesis explicitly defined. Effect sizes (η²) specified for quantitative falsification.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** High practical impact—practitioners gain principled guidance on feedback system design. If H2 (granularity) dominates, simplifies deployment (test + FGO is cheaper). Theoretical contribution connects to RL credit assignment literature.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully feasible with existing resources. ~50-100 GPU-hours is reasonable for academic research. StepCoder provides FGO implementation. OpenRLHF provides PPO infrastructure. Standard benchmarks require no new data collection.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The research community has developed multiple execution feedback approaches for code RL (PPOCoder, StepCoder, RLPF, EG-CFG), but no systematic study has disentangled WHAT type of feedback matters from HOW the feedback is applied. We hypothesize that the granularity mechanism—specifically Fine-Grained Optimization (FGO) which masks non-executed code tokens—provides the primary learning benefit by enabling precise credit assignment. Content variation (compile vs. test vs. combined) offers secondary, complementary benefits.

Our 2×3 factorial experiment (Content × Granularity) with 7 conditions including an RLPF baseline will test three predictions: (1) FGO improves all content types, (2) content combinations outperform singles, and (3) FGO effect dominates content effect. Using CodeLlama-7B on HumanEval/MBPP with ~50-100 GPU-hours, this study will provide the first principled framework for execution feedback system design.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- HumanEval near-saturation may limit visibility of training improvements at pass@1
- FGO masking threshold sensitivity not yet characterized
- Transfer to complex benchmarks (SWE-bench) untested
- **Mitigation Strategy:** Report pass@1 with headroom analysis (room for improvement from baseline). Include masking coverage statistics. Design follow-up study for complex benchmark transfer.

---


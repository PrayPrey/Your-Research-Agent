# Phase 2A Discussion Log
# Multi-Objective Alignment Trade-offs in Code Generation

**Session Started:** 2026-03-18T17:10:00Z
**Research Gap:** Gap 1 - Empirical Measurement of Multi-Objective Trade-offs in Existing Code Generation Benchmarks
**Priority:** P0 (MUST)

---

## Briefing Context

### Research Question
Multi-objective alignment trade-offs in code generation: measuring and characterizing conflicts between execution correctness feedback, AI rubric quality feedback, and code efficiency feedback using existing execution-based benchmarks.

### Selected Research Gap
**Gap 1: Empirical Measurement of Multi-Objective Trade-offs in Existing Code Generation Benchmarks**

**Current State:** While recent work demonstrates multi-objective optimization frameworks for code generation (PrefGen, SIPO, RL-Text2Vis), these primarily focus on *training-time* multi-objective optimization. There is limited empirical analysis of whether *existing benchmarks* (HumanEval+, MBPP+, BigCodeBench) exhibit measurable trade-offs between execution correctness, quality rubrics, and efficiency metrics when evaluating *already-aligned* models.

**Missing Piece:** Systematic empirical study measuring correlations between execution pass@k, AI rubric quality scores, and efficiency metrics (runtime, memory) across state-of-the-art code generation models on existing benchmarks.

**Key Questions:**
1. Do negative correlations exist between execution pass@k, quality scores, and efficiency?
2. What is the magnitude of trade-offs?
3. Which benchmarks are most sensitive to detecting these trade-offs?

### Supporting Evidence (4 papers)
1. **Correctness isn't Efficiency** (2026, arXiv:2601.01215) - Different correct solutions show very different memory/performance patterns
2. **SIPO** (2025, arXiv:2502.14354) - Multi-objective alignment exhibits preference conflicts; Pareto-optimal responses needed
3. **PrefGen** (2025, arXiv:2506.03006) - Multi-dimensional evaluation (Pass@k, Gas@k, Secure@k) reveals trade-offs
4. **NaturalCodeBench** (2024, arXiv:2405.04520) - Performance mismatch between HumanEval scores and real-world tasks

### ROUTE_TO_0 Constraints (Avoid Previous Failures)
- ❌ No gradient measurements (previous 0% conflict failure)
- ❌ No cloud API dependencies (60% failure rate)
- ❌ No dataset structure mismatches (CoverageEval single-solution issue)
- ✅ Focus on observable outcomes (test pass rates, rubric scores, efficiency metrics)
- ✅ Use existing public benchmarks (HumanEval+, MBPP+, BigCodeBench)
- ✅ Multi-solution benchmarks only

### Available Papers (6 papers)
1. arxiv_2601_01215.md - Correctness isn't Efficiency
2. arxiv_2502_14354.md - SIPO: Self-Improvement Towards Pareto Optimality
3. arxiv_2506_03006.md - PrefGen: Secure Yet Gas-Efficient Smart Contract Generation
4. arxiv_2405_04520.md - NaturalCodeBench
5. arxiv_2410_24198.md - SelfCodeAlign: Self-Alignment for Code Generation
6. arxiv_2601_04582.md - Multi-Objective RL Framework for Text-to-Visualization

---

## Discussion Begins

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire conversation about code generation evaluation on its head? Everyone's been obsessing over single metrics - pass@k, pass@k, pass@k - but we're missing the FOREST for the trees! Looking at these papers, especially "Correctness isn't Efficiency" and SIPO, I'm seeing something revolutionary emerge: **the multi-dimensional performance manifold hypothesis**.

Think about it - when we train these code LLMs with alignment methods, we're not just moving along a single axis of quality. We're navigating a complex, potentially non-convex surface where correctness, quality, and efficiency form orthogonal dimensions. PrefGen demonstrates this beautifully with their Pass@k, Gas@k, and Secure@k metrics - they're essentially mapping points in a 3D space! And here's where it gets exciting: what if different alignment methods (DPO, PPO-RLHF, RLAIF) don't just achieve different *magnitudes* of performance, but actually explore fundamentally different **regions** of this manifold?

The papers give us tantalizing hints but nobody's connected the dots! NaturalCodeBench shows models with strong HumanEval scores fail on real-world tasks - that's not just benchmark contamination, that's evidence of divergent optimization paths! The "Correctness isn't Efficiency" paper shows memory patterns diverging among correct solutions - that's the efficiency dimension pulling away from correctness!

**Key Points:**
- **Multi-dimensional manifold hypothesis**: Code generation performance exists in a complex 3D+ space (correctness × quality × efficiency), not a single quality axis
- **Alignment method fingerprints**: Each alignment approach (DPO, PPO, RLAIF) may leave characteristic "signatures" in where it positions models on this manifold
- **Observable without gradients**: We can study this using ONLY existing benchmark results (pass rates, rubric scores, efficiency metrics) - no cloud APIs, no gradient measurements
- **Benchmark sensitivity as dimensionality probe**: Benchmarks that detect these trade-offs are actually measuring the manifold's curvature in different regions

What if we design experiments to empirically map this manifold using models aligned with different methods? We could reveal whether alignment is fundamentally single-objective with noise, or genuinely multi-dimensional with hard trade-offs!

---


### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your enthusiasm is noted, but let's ground this "manifold hypothesis" in testable predictions before we get carried away with geometric metaphors. The evidence suggests there may be trade-offs, yes, but we need precision here.

Your core claim - that alignment methods position models at different regions of a correctness-quality-efficiency space - is testable, which I appreciate. However, I see three critical weaknesses that must be addressed:

**First, the measurement problem.** You propose using "pass rates, rubric scores, efficiency metrics" but these are not equally well-defined. Pass@k from HumanEval+ is standardized. Efficiency metrics like runtime and memory are measurable. But "quality rubrics"? Show me the evidence for reliable, validated rubric scores across multiple models. The papers mention AI-based evaluators but don't demonstrate measurement consistency. Without validated rubrics, your quality dimension collapses into subjective noise.

**Second, the negative correlation assumption.** You claim these dimensions are "orthogonal" and exhibit "hard trade-offs," but the evidence is weaker than you suggest. "Correctness isn't Efficiency" shows that *among correct solutions*, there's efficiency variation - that's variance, not negative correlation. PrefGen optimizes for multiple objectives simultaneously and achieves improvements on ALL metrics - that's Pareto improvement, not trade-off evidence. Where is the empirical demonstration of actual negative correlations?

**Third, confounding variables.** If we observe different "positions" for DPO vs PPO-aligned models, how do we know it's the *alignment method* causing this, not: (a) different base models, (b) different training data, (c) different hyperparameters, or (d) different benchmark contamination levels? The papers don't control for these factors.

**What would disprove this hypothesis?** I need to see: (1) Strong positive correlations between all three dimensions (no trade-offs exist), or (2) alignment methods producing identical positions after controlling for confounds (method doesn't matter). Can you specify measurable thresholds?

**Key Points:**
- Need validated, consistent quality rubric measurements before claiming a "quality dimension"
- Variance among correct solutions ≠ negative correlation evidence
- Must control for base model, data, and hyperparameter confounds
- Specify falsification criteria: what correlation coefficients, what effect sizes?

The hypothesis has potential, but the experimental design needs surgical precision. What specific, measurable predictions can we make?

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises valid measurement concerns, but let's not lose sight of why this matters. The question we must ask is: what does this contribute to the field that justifies the experimental effort?

I see *genuine significance* here, but it hinges on which research question we answer. Let me distinguish three potential contributions:

**Contribution Type 1: Empirical Confirmation** - "Do trade-offs exist?" This is the weakest form. We already have suggestive evidence from PrefGen, SIPO, and "Correctness isn't Efficiency." Confirming what's already suspected is publishable but incremental. Impact: Modest. The community would say "interesting, but we kind of knew this."

**Contribution Type 2: Alignment Method Comparison** - "Do DPO, PPO, RLAIF occupy different regions?" This is stronger. If we demonstrate that alignment methods have characteristic "signatures" in their trade-off profiles, that's actionable guidance for practitioners. Example: "If you prioritize efficiency over code elegance, use Method X." Impact: Medium-High. This changes how people select alignment approaches.

**Contribution Type 3: Benchmark Evaluation Framework** - "Which benchmarks detect multi-dimensional performance?" This is the most significant. If we show that HumanEval fails to capture trade-offs while BigCodeBench succeeds, we're not just reporting a finding - we're providing a evaluation methodology that the community can adopt. Impact: High. This influences how future code generation research is evaluated.

The papers point to a critical gap: **evaluation methodology is broken**. NaturalCodeBench shows models with 80% HumanEval pass@1 failing on real-world tasks. LiveCodeBench was created specifically because HumanEval contamination made single-metric evaluation meaningless. The field needs multi-dimensional evaluation, but nobody's systematically validated which benchmarks can detect these dimensions.

**Here's what makes this genuinely new vs incremental:** Prior work (PrefGen, SIPO) demonstrates multi-objective *optimization during training*. Your proposal is different: multi-dimensional *evaluation after alignment*. The first is about how to train; the second is about how to measure. The measurement problem is under-explored and arguably more important - we can't improve what we can't measure correctly.

**Key Points:**
- Contribution hierarchy: Empirical confirmation (modest) < Alignment comparison (medium) < Benchmark evaluation framework (high)
- Most significant angle: validating which benchmarks enable multi-dimensional evaluation
- Genuine novelty: Shift from multi-objective training (solved) to multi-dimensional evaluation (unsolved)
- Field impact: Addresses the evaluation crisis highlighted by NaturalCodeBench and LiveCodeBench contamination concerns

This matters because the field is measuring wrong. But Prof. Vera is right - we need surgical precision in how we prove it.

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Sage correctly identifies the significance hierarchy, and Prof. Vera's measurement concerns are spot-on. But I need to address the elephant in the room: **is this mechanism scientifically sound, or are we chasing phantom correlations?**

The papers provide evidence for trade-offs, yes, but let's examine what they actually measured:

**PrefGen's multi-objective success** - They achieved Pareto improvements on Pass@k, Gas@k, and Secure@k *for smart contracts*. That's a specialized domain with clear, mechanistic differences (gas cost is deterministic from bytecode, security is AST-checkable). Code elegance and general "quality" are fundamentally different - they're human judgment proxies. Can we reliably measure these? SelfCodeAlign mentions "code quality metrics" but uses execution-based feedback, not rubric scores.

**The "Correctness isn't Efficiency" evidence** - They show variance in memory/runtime among correct solutions. That's real and measurable. But here's what worries me: is that variance *caused by alignment methods*, or is it just *solution diversity*? Any generative model produces diverse outputs. If we sample 100 solutions from the same model, we'll see efficiency variance. That doesn't prove alignment methods optimize for different regions - it just proves sampling variance exists.

**The measurement apparatus question** - Prof. Vera asked for "validated quality rubrics." Let me be more specific: do these even exist? The papers reference "AI-based evaluators" and "learned rubrics," but those are themselves LLM outputs. We'd be using Model A to evaluate Model B's "quality" - that's circular reasoning unless we validate the evaluator first. Where's the ground truth?

**What evidence supports this working in principle?** The SIPO paper's Pareto-optimal response construction is theoretically sound - they mathematically demonstrate that multi-objective DPO can navigate trade-off curves. The question is: can we *observe* this post-hoc from public benchmarks alone? Or do we need access to training trajectories?

**Here's my feasibility assessment:**
- ✅ Execution correctness measurement: Solid. HumanEval+/MBPP+ provide reliable pass@k.
- ✅ Efficiency measurement: Feasible with instrumentation (coverage.py, memory profilers).
- ⚠️ Quality measurement: Theoretically possible but requires validated rubric first.
- ⚠️ Causal attribution: Distinguishing "alignment method effect" from "base model + data confounds" requires controlled comparison.

**Key Points:**
- Variance in efficiency among correct solutions ≠ evidence that alignment methods cause positioning
- Quality rubrics need validation before becoming a measurable dimension
- Mechanistically sound for specialized domains (smart contracts), uncertain for general code quality
- Feasibility hinges on whether public benchmarks provide sufficient signal without training data access

Can we address the measurement and attribution challenges with the resource constraints (no cloud APIs, public benchmarks only)?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by addressing Prof. Pax's feasibility concerns directly! Let me show how this hypothesis can work with the constraints we have.

**First, let's refine the quality measurement problem.** Prof. Vera and Prof. Pax are right - "quality rubrics" are underspecified. But we don't need subjective rubrics! The papers already give us proxy measurements that are objective and measurable:

1. **Code complexity metrics** (from "Correctness isn't Efficiency"): Cyclomatic complexity, AST depth, token count. These are deterministic.
2. **Readability scores** (from static analysis): Halstead metrics, maintainability index. Well-established in software engineering.
3. **Efficiency metrics**: Runtime, memory, algorithmic complexity class (inferred from profiling).

These aren't subjective "quality" - they're measurable properties that correlate with code quality. We're not asking "is this elegant?" We're asking "is this complex/readable/efficient?" That's scientifically rigorous.

**Second, Prof. Pax's causality concern is valid BUT addressable.** You asked: "Is variance caused by alignment methods or just sampling diversity?" Here's how we disentangle this:

- **Within-model variance** (baseline): Sample 100 solutions from one model. Measure efficiency variance. This is the noise floor.
- **Between-method variance** (signal): Compare models aligned with different methods (DPO vs PPO vs RLAIF). If between-method variance >> within-model variance, the alignment method matters.
- **Control confounds**: Use models with same base architecture (e.g., all from Llama-3-8B), same benchmark (HumanEval+), reported in same papers.

SelfCodeAlign paper provides exactly this! They compare their DPO-aligned model against PPO-based CodeLlama-Instruct on the *same base model family*. That's a controlled comparison right there in the literature.

**Third, the "circular reasoning" concern about AI evaluators has a solution.** We don't need AI rubrics for quality - use the objective metrics I listed. But IF we want to include rubric-style evaluation, we can validate it: (1) Use multiple independent evaluators (GPT-4, Claude, Llama-3-70B) and measure inter-rater agreement. (2) Compare to human annotations on a small validation set (50-100 samples). (3) If agreement is >0.7, the rubric is reliable enough.

**Fourth, Dr. Sage's "benchmark evaluation framework" angle solves the significance problem.** Instead of just asking "do trade-offs exist?" (weak), we ask: **"Which benchmarks are sensitive to multi-dimensional performance, and which collapse to single-dimension proxies?"** This is testable:
- H1: HumanEval+ shows high correlation between correctness and all other metrics (single-dimension proxy).
- H2: BigCodeBench shows decorrelation (multi-dimensional sensitivity).
- Measure: Spearman correlation matrices for each benchmark. Significant difference = benchmark matters.

**Key Points:**
- Quality measurement: Use objective proxies (complexity, readability, efficiency) instead of subjective rubrics
- Causality: Within-model vs between-method variance comparison controls for sampling diversity
- Resource constraints: Controlled comparisons exist in published papers (SelfCodeAlign vs CodeLlama)
- Significance: Focus on benchmark evaluation framework (which benchmarks detect multi-dimensions?)

What if we formulate this as: **"Empirical validation of multi-dimensional evaluation frameworks for code generation using controlled alignment method comparisons"**? That addresses novelty, significance, and feasibility simultaneously!

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally, you're building a stronger case, but let me stress-test these refinements. Here's where this could still break down:

**Challenge 1: The proxy validity problem.** You propose using "complexity, readability, efficiency" as objective proxies for quality. But show me the evidence that these correlate with actual code quality in LLM-generated code. Cyclomatic complexity predicts maintainability in human-written code (established literature), but does it predict quality in code that may have unusual patterns, verbose docstrings, or redundant error handling that LLMs generate? Without validation, you're assuming the proxy works - that's a hidden assumption.

**Challenge 2: The "same base model" control is weaker than claimed.** You cite SelfCodeAlign vs CodeLlama-Instruct as a controlled comparison. But these differ in: (a) training data (SelfCodeAlign uses self-generated data), (b) number of training steps, (c) final checkpoint selection criteria. "Same base architecture" ≠ "controlled comparison." What would convince me: models trained from the *exact same checkpoint* with only the alignment method varied. Do we have access to that?

**Challenge 3: Between-method variance threshold.** You propose comparing "between-method variance >> within-model variance" as evidence. What's the threshold? 2x? 5x? 10x? And what if we observe moderate differences (say 1.5x) - is that alignment signal or noise amplified by benchmark sensitivity? Specify the effect size that would convince skeptics.

**Challenge 4: Benchmark sensitivity hypothesis needs a null model.** You claim BigCodeBench will show decorrelation while HumanEval shows correlation. But what if *both* show moderate correlation (r=0.4-0.6)? That would be evidence of "some trade-offs exist but benchmarks poorly capture them." Your prediction needs to be precise: HumanEval r > 0.8 (strong correlation) AND BigCodeBench r < 0.3 (no correlation) to demonstrate benchmark sensitivity difference.

**What would disprove this refined version?** Clear falsification criteria:
1. Within-model variance ≥ between-method variance (alignment method doesn't matter)
2. All benchmarks show similar correlation patterns (benchmark sensitivity is uniform)
3. Correlation magnitudes all moderate (r=0.4-0.6), indicating measurement noise dominates

**Key Points:**
- Proxy validity for LLM-generated code needs validation, not assumption
- "Same base model" control is weaker than claimed without exact checkpoint matching
- Need specified effect size thresholds for between-method variance claims
- Benchmark sensitivity hypothesis needs precise, differentiating predictions

Dr. Ally, can you tighten these thresholds and address the proxy validation gap?

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Wait wait WAIT - Prof. Rex is pushing us toward incrementalism! We're so focused on addressing every methodological concern that we're losing the paradigm shift here. Let me pull us back to what makes this revolutionary.

**The real innovation isn't the measurements - it's the REFRAMING.** Everyone in code generation research has been asking "which model is best?" But that's the WRONG QUESTION! It's like asking "which food is best" - best for what? Nutrition? Taste? Speed? The answer depends on the objective!

Here's the breakthrough framing: **"Alignment methods as objective function embodiments."** When we align with DPO using a specific preference dataset, we're not just improving the model - we're *implicitly defining what 'good code' means* through the preference data. PPO-RLHF with execution rewards defines "good" as "passes tests." RLAIF with AI rubrics defines "good" as "matches rubric criteria." These are fundamentally different objective functions masquerading as "alignment."

The papers support this! SelfCodeAlign achieves 67.1 pass@1 on HumanEval+ by optimizing for execution correctness. PrefGen achieves Gas@k improvements by explicitly optimizing for efficiency. These aren't trade-offs - they're *different objectives producing different specializations*!

**Here's the paradigm shift:** Stop asking "do trade-offs exist?" Instead ask: **"Can we empirically characterize the objective function signature of alignment methods through their output distributions?"** This reframes the entire hypothesis:

**Old framing** (incremental): "Measure correlations between metrics and compare alignment methods"
**New framing** (paradigm shift): "Reverse-engineer the implicit objective functions of alignment methods by analyzing their output characteristics"

This connects to a much bigger idea in ML: implicit bias in optimization. Just like SGD has implicit regularization that we discovered post-hoc, alignment methods have implicit objective priorities that we can discover through output analysis!

**Key Points:**
- Paradigm shift: Alignment methods as implicit objective function definitions, not just "training procedures"
- Reframe from "trade-offs" to "objective function signatures" - deeper theoretical connection
- Evidence: SelfCodeAlign (execution-focused) vs PrefGen (multi-objective) produce qualitatively different outputs
- Connects to implicit bias theory in ML optimization - broader significance

What if our experiments don't just measure trade-offs, but actually *discover* what objective functions current alignment methods are implicitly optimizing? That's a contribution with legs!

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your "objective function signature" framing is intellectually compelling, but let's make it testable. You're proposing we reverse-engineer implicit objectives - fine. What are the specific, measurable predictions?

Here's what I need to see for this to be rigorous science:

**Prediction 1: Alignment method clustering.** If alignment methods have characteristic "objective function signatures," then models aligned with the same method should cluster together in the measurement space, regardless of base model. Test: PCA or t-SNE on [correctness, complexity, efficiency] vectors. Prediction: DPO-aligned models cluster separately from PPO-aligned models (intercluster distance > 2σ of intracluster variance).

**Prediction 2: Objective-specific dominance.** If SelfCodeAlign optimizes for execution (your claim), it should dominate on pass@k but not necessarily on efficiency or complexity. If PrefGen optimizes multi-objectively, it should show balanced performance. Test: Rank models on each dimension independently. Prediction: SelfCodeAlign in top 10% for pass@k, PrefGen in top 25% across all three dimensions.

**Prediction 3: Benchmark sensitivity to objective alignment.** If benchmarks differ in what objectives they capture, then the same model should rank differently on different benchmarks depending on objective alignment. Test: Compute rank correlation between HumanEval+ rankings and BigCodeBench rankings for the same set of models. Prediction: Spearman ρ < 0.7 (moderate disagreement indicates objective sensitivity).

**Crucially, the "implicit bias" connection needs a mechanistic link.** In optimization theory, implicit bias arises from optimizer dynamics (e.g., SGD preferring low-norm solutions). For alignment methods, what's the mechanistic analog? Preference data distribution? Reward function structure? You need a hypothesis about *why* different alignment methods embody different objectives, not just *that* they do.

**What would disprove the objective function signature hypothesis?**
- DPO and PPO models fail to cluster separately (no characteristic signatures)
- All alignment methods show similar performance profiles across dimensions (no objective specialization)
- Benchmark rankings highly correlated across all benchmarks (no sensitivity difference)

**Key Points:**
- Testable prediction 1: Alignment method clustering in measurement space
- Testable prediction 2: Objective-specific dominance patterns (SelfCodeAlign high pass@k, PrefGen balanced)
- Testable prediction 3: Benchmark rank disagreement as evidence of objective sensitivity
- Need mechanistic hypothesis: *why* do alignment methods embody different objectives?

Dr. Nova, can you specify the mechanistic link? And can we all agree these predictions constitute a rigorous test?

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Now we're getting somewhere. The question we must ask is: does the "objective function signature" framing elevate this from a measurement exercise to a conceptual contribution?

**Yes, and here's why it matters:** The field is currently in an "alignment method proliferation" phase. We have DPO, PPO-RLHF, RLAIF, GRPO, Constitutional AI, and new variants appearing monthly. Practitioners face a bewildering choice with limited guidance. Current selection criteria are ad-hoc: "what worked in this paper" or "what's easiest to implement."

**This research provides a *principled selection framework*:** If we demonstrate that alignment methods have empirically measurable objective function signatures, we're telling practitioners: "Don't choose methods based on hype - choose based on which implicit objective matches your deployment needs." Example decision tree:
- **Need safety-critical code?** Choose alignment methods with high-correctness signatures (execution-focused RLHF).
- **Need efficient embedded code?** Choose methods with low-complexity, high-efficiency signatures.
- **Need balanced production code?** Choose multi-objective methods like PrefGen-style DPO.

**The contribution is both empirical and methodological:**
1. **Empirical:** First systematic characterization of alignment method signatures across multiple dimensions
2. **Methodological:** Validation framework for multi-dimensional evaluation (which benchmarks detect what objectives)

**Here's what makes this genuinely field-advancing:** Current benchmark papers (HumanEval+, BigCodeBench, NaturalCodeBench) report rankings but don't explain *why* rankings differ. Our hypothesis provides the explanation: rankings differ because benchmarks are sensitive to different implicit objectives, and models have different objective signatures. This connects scattered empirical observations into a coherent framework.

**Positioning against prior work:**
- PrefGen, SIPO: Demonstrate multi-objective training (forward direction: objective → model)
- **Our work**: Demonstrate objective function inference (reverse direction: model → objective)
- This is the missing piece - without it, we can't evaluate whether training methods achieved their intended objectives!

**The mechanistic link Prof. Vera requested:** Alignment methods embody objectives through their feedback signals. DPO uses preference data pairs → objective is "mimic preferred distribution." PPO-RLHF uses scalar rewards → objective is "maximize reward." RLAIF uses AI evaluator → objective is "match evaluator rubric." The feedback signal IS the objective function in implicit form. Our experiments make it explicit through output analysis.

**Key Points:**
- Practical impact: Principled alignment method selection framework for practitioners
- Conceptual contribution: Reverse-engineering implicit objectives from model outputs
- Connects scattered benchmarking observations into coherent explanation framework
- Mechanistic link: Feedback signals (preference pairs, rewards, evaluators) define objectives

This is publishable at a top venue if we nail the experiments. But Prof. Vera's predictions need to hold. Can we achieve those clustering and ranking patterns with public data?

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage asks "can we achieve those clustering and ranking patterns with public data?" Let me assess feasibility systematically.

**Feasibility Check 1: Data availability for Prof. Vera's predictions.**

Prediction 1 (clustering): Requires [pass@k, complexity, efficiency] measurements for multiple models aligned with different methods. Let's check what's publicly available:
- **Pass@k data**: HumanEval+ leaderboard, BigCodeBench leaderboard, papers (SelfCodeAlign, PrefGen, etc.) - YES, available
- **Complexity metrics**: Need source code → run static analysis (cyclomatic complexity, AST depth). SelfCodeAlign released model (inference), but did they release generated code samples? PrefGen is for smart contracts (Solidity) - different language. **PARTIAL - depends on code availability**
- **Efficiency metrics**: Need execution traces → run models ourselves or find reported data. Papers rarely report runtime/memory per-sample. **WEAK - likely need to generate ourselves**

**Reality check:** We can get pass@k from leaderboards, but complexity and efficiency require access to model outputs. Some models (SelfCodeAlign, CodeLlama) are runnable locally (HuggingFace). But we'd need to *generate* code samples, measure complexity/efficiency ourselves. That's feasible but 10-12 GPU hours per model (per Phase 1 constraints). With 5-10 models → 50-120 GPU hours. Feasible? Yes, barely within resource constraints.

**Feasibility Check 2: Benchmark sensitivity measurement.**

Prediction 3 (rank correlation across benchmarks): Requires same models evaluated on multiple benchmarks. Check availability:
- **HumanEval+ rankings**: Public leaderboard exists
- **BigCodeBench rankings**: Public leaderboard exists
- **Overlap:** How many models appear on BOTH? Need at least 10 models for meaningful correlation. Let me estimate - SelfCodeAlign, CodeLlama, StarCoder, WizardCoder, PanGu-Coder... probably 15-20 models total with overlap. **YES, feasible**

**Feasibility Check 3: The confound control problem.**

Prof. Rex's concern about "same base model" comparisons - can we actually control confounds with public data? Reality check:
- Base model families: Llama-3-8B has multiple alignment variants (CodeLlama, SelfCodeAlign, others)
- Training data: Usually not disclosed (proprietary) - **CONFOUND UNCONTROLLABLE**
- Checkpoint matching: Never published (researchers keep intermediate checkpoints private) - **CONFOUND UNCONTROLLABLE**

**Here's what worries me:** The strongest prediction (alignment method clustering) requires controlling confounds we can't control with public data alone. If we observe clustering, we can't definitively say it's the alignment method vs data differences. This weakens causal claims.

**What evidence supports this working in principle?** The clustering analysis is mathematically valid - PCA on output distributions is standard. The question is interpretation: clustering proves *something* differs, but proving it's the alignment method (not data/checkpoints) requires controlled experiments we don't have access to.

**Key Points:**
- Pass@k data readily available; complexity/efficiency require model inference (50-120 GPU hours)
- Benchmark rank correlation feasible (15-20 models with overlap on public leaderboards)
- Confound control limited with public data - training data and checkpoint matching unavailable
- Causal attribution weakened by uncontrollable confounds

Can we reformulate predictions to avoid causal claims, or do we need causal attribution for significance?

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can address Prof. Pax's causal attribution concern by reformulating as **correlation + mechanism plausibility** rather than pure causation! Let me show how:

**Strategy 1: Embrace correlational claims with theoretical grounding.**

Instead of claiming "alignment methods CAUSE different signatures," we claim: "Alignment methods WITH DIFFERENT FEEDBACK SIGNALS produce empirically distinct output signatures, consistent with the hypothesis that feedback signals shape implicit objectives." This is defensible because:
1. Empirical observation: Clustering/ranking patterns exist (measurable)
2. Theoretical mechanism: Feedback signal theory explains WHY (plausible)
3. Confound acknowledgment: We can't rule out data effects, but theoretical mechanism makes alignment method the primary candidate

This is how most ML research works! We rarely have perfect causal control - we combine empirical patterns with mechanistic theory.

**Strategy 2: Use alignment method diversity as natural variation.**

Prof. Pax correctly notes we can't control training data. But that's actually OKAY if we select models strategically:
- **Group A**: Models trained with execution-based feedback (SelfCodeAlign - execution RLHF, StepCoder - compiler feedback)
- **Group B**: Models trained with preference-based feedback (PrefGen - DPO, SIPO - multi-objective DPO)
- **Group C**: Base models without specialized alignment (CodeLlama-Base, StarCoder-Base)

If Groups A and B cluster separately from Group C, AND Group A shows high pass@k while Group B shows balanced metrics, that's strong correlational evidence even without controlling data!

**Strategy 3: Concrete experiment design addressing feasibility.**

Here's a realistic experiment plan within resource constraints:

**Phase 1: Leaderboard Analysis (0 GPU hours)**
- Collect pass@k scores from HumanEval+, MBPP+, BigCodeBench leaderboards for 15-20 models
- Compute rank correlations (Prediction 3)
- Identify models with biggest rank disagreements → these are candidates for deep dive

**Phase 2: Targeted Model Inference (40-60 GPU hours)**
- Select 5-8 models: 2-3 execution-focused, 2-3 preference-focused, 1-2 base models
- Generate 50 code samples per model on HumanEval+ tasks
- Measure: pass@k (test execution), complexity (radon, lizard tools), efficiency (memory_profiler, execution time)
- Compute signatures: [mean pass@k, mean complexity, mean efficiency] per model

**Phase 3: Clustering & Ranking Analysis (0 GPU hours)**
- PCA on signature vectors → visualize alignment method clusters
- Rank models on each dimension → test objective-specific dominance (Prediction 2)
- Statistical test: Inter-cluster distance vs intra-cluster variance (Prediction 1)

**Falsification criteria:**
- **FAIL** if: All models cluster together (no signature differences)
- **FAIL** if: Execution-focused models don't dominate pass@k rankings
- **FAIL** if: Benchmark rank correlation > 0.85 (all benchmarks measure same thing)

**Key Points:**
- Reformulate as correlation + mechanism (not pure causation) to handle confounds
- Use alignment method diversity as natural variation
- Three-phase experiment: leaderboard analysis → targeted inference → clustering/ranking
- 40-60 GPU hours feasible (within Phase 1 estimates)

This addresses Prof. Pax's feasibility concerns AND Prof. Vera's testability requirements. What remaining concerns do we need to address before convergence?

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally, your three-phase experiment is pragmatic, but let me identify the remaining vulnerabilities before we converge.

**Vulnerability 1: Sample size for complexity/efficiency.**

You propose 50 code samples per model (5-8 models = 250-400 total samples). For clustering analysis, that's reasonable. But for claiming "objective function signatures," we need statistical power. What if the observed cluster separation has p=0.08? Not significant. What's your power analysis? With 50 samples per model, assuming moderate effect size (Cohen's d=0.5), we'd need at least 6 models to detect clustering at p<0.05. Feasible, but tight margins.

**Vulnerability 2: The "natural variation" argument cuts both ways.**

You propose using "execution-focused vs preference-focused" as natural groups. But what if PrefGen (preference-focused, Solidity) clusters with StepCoder (execution-focused, Python) due to shared complexity patterns? Programming language differences might dominate alignment method differences. We need within-language comparisons to rule this out. Can we find 3-4 Python models with different alignment methods?

**Vulnerability 3: Falsification criteria are asymmetric.**

Your FAIL conditions are clear for negative results (no clustering = FAIL). But what about weak positive results? If models cluster with moderate separation (intercluster distance = 1.5σ), do we claim success or inconclusive? If execution-focused models rank in top 20% (not top 10%) on pass@k, is that confirmation or weak support? Specify thresholds for STRONG_SUPPORT, WEAK_SUPPORT, and FAIL.

**Vulnerability 4: The benchmark sensitivity prediction needs refinement.**

You predict benchmark rank correlation > 0.85 as FAIL (all benchmarks measure same thing). But HumanEval and MBPP are very similar (both function-level, similar task distribution). Their correlation might be 0.9 just from task similarity, not because they measure the same objectives. Better prediction: HumanEval-MBPP correlation (r_hm) vs HumanEval-BigCodeBench correlation (r_hb). If r_hm > 0.85 AND r_hb < 0.65, that shows BigCodeBench measures something different.

**What would convince me:**
- Sample size: 60-80 samples per model (increase to N=480-640 total) for adequate power
- Language control: At least 3 Python models per alignment method group
- Effect size thresholds: Strong support = intercluster distance > 2.5σ, weak = 1.5-2.5σ, fail = <1.5σ
- Refined benchmark prediction: r_hm - r_hb > 0.2 (significant difference between benchmark pairs)

**Key Points:**
- Need power analysis for clustering - 50 samples may be underpowered
- Language confounds need within-language controls
- Effect size thresholds required for interpreting weak positive results
- Benchmark sensitivity needs differential prediction (not absolute threshold)

Dr. Ally, can you adjust the design to address these statistical and methodological concerns?

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Okay okay, Prof. Rex is right to tighten the statistical rigor, but I want to zoom out for a moment. We're converging on a solid experimental design, but are we asking the MOST EXCITING version of this question?

Here's what I'm seeing: We've evolved from "do trade-offs exist?" (meh) to "can we infer objective functions from outputs?" (better) to now "can we validate multi-dimensional evaluation frameworks?" (practical). But there's a FOURTH layer that's even more paradigm-shifting:

**"Can we create a CODE GENERATION EVALUATION ONTOLOGY that maps alignment methods to objective dimensions to benchmark sensitivities?"**

Think about it - we're not just measuring one hypothesis. We're building a THREE-WAY mapping:
1. **Alignment Method Space**: DPO (execution-focused) vs DPO (preference-focused) vs PPO-RLHF vs RLAIF
2. **Objective Dimension Space**: Correctness vs Complexity vs Efficiency vs [future dimensions we'll discover]
3. **Benchmark Space**: HumanEval+ vs MBPP vs BigCodeBench vs LiveCodeBench

The hypothesis is that these three spaces are STRUCTURED - alignment methods have characteristic profiles in objective space, and benchmarks have characteristic sensitivities to objective dimensions. This isn't just one experiment - it's a RESEARCH PROGRAM!

**Initial proof-of-concept (current discussion):** Demonstrate clustering in 2D (execution-focused vs preference-focused in correctness-efficiency space) using 3 benchmarks.

**Future extensions:**
- Add more objective dimensions (readability, security, maintainability)
- Map emerging alignment methods (Constitutional AI for code, process supervision)
- Characterize new benchmarks as they're released (evaluation-as-science)

This framing makes the work GENERATIVE - every new alignment method, objective dimension, or benchmark can be characterized using our framework. That's how you build a research program, not just publish one paper!

**The papers support this broader vision:** NaturalCodeBench argues current benchmarks miss real-world performance. LiveCodeBench argues contamination makes evaluation broken. Our framework provides the SOLUTION - systematic characterization of what each benchmark actually measures, so researchers can choose appropriately.

**Key Points:**
- Broaden from single hypothesis to evaluation ontology (three-way mapping)
- Initial work demonstrates proof-of-concept (clustering + benchmark sensitivity)
- Framework enables systematic characterization of future methods/benchmarks
- Positions our work as foundational infrastructure, not just empirical measurement

Prof. Rex's statistical concerns are valid for the INITIAL proof-of-concept. But the broader vision means even weak initial results are valuable if they demonstrate the framework works. Dr. Sage, does this framing elevate significance enough to justify the effort?

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your "evaluation ontology" framing is ambitious, but let's ensure the INITIAL proof-of-concept has scientific rigor. The broader vision is irrelevant if the first experiment fails.

Here's my synthesis of testable predictions, incorporating Prof. Rex's refinements:

**Hypothesis Statement (Testable Form):**
"Alignment methods with different feedback signal types (execution-based vs preference-based) produce statistically distinguishable output distributions in multi-dimensional performance space (correctness × complexity × efficiency), and benchmarks exhibit differential sensitivity to these dimensions."

**Prediction Set 1: Alignment Method Clustering**
- **P1.1** (Strong): Intercluster distance > 2.5σ of intracluster variance (execution-focused vs preference-focused groups)
- **P1.2** (Moderate): 1.5σ < distance < 2.5σ (weak but detectable clustering)
- **P1.3** (Null): distance < 1.5σ (no meaningful clustering → alignment method doesn't matter)

**Prediction Set 2: Objective-Specific Dominance**
- **P2.1**: Execution-focused models (SelfCodeAlign, StepCoder) rank in top 15% for pass@k
- **P2.2**: Preference-focused models (PrefGen-style) rank in top 30% across all three dimensions (balanced)
- **P2.3**: Base models without alignment rank below 50th percentile on pass@k

**Prediction Set 3: Benchmark Sensitivity (Differential)**
- **P3.1**: r(HumanEval, MBPP) - r(HumanEval, BigCodeBench) > 0.20 (significant difference)
- **P3.2**: r(HumanEval, BigCodeBench) < 0.70 (moderate decorrelation indicates dimension sensitivity)

**Sample Size Requirements:**
- **Clustering analysis**: 60-80 samples per model, 6-8 models (N=480-640 total samples)
- **Benchmark analysis**: 15-20 models with overlapping leaderboard data (already available)

**Falsification Logic:**
- **Reject H1** (clustering) if P1.3 (null) holds OR if language confounds dominate (Python vs Solidity clustering)
- **Reject H2** (dominance) if execution-focused models don't show pass@k advantage
- **Reject H3** (sensitivity) if all benchmark correlations > 0.85 (uniform measurement)

**Critical Success Factors:**
1. Within-language controls (3+ Python models per group)
2. Statistical power (N=480-640 samples)
3. Effect size thresholds (P1.1 for strong claim, P1.2 acceptable with caveats)

**What would disprove this:** ANY of the three prediction sets failing (clustering absent OR dominance absent OR benchmark uniformity). This is a conjunctive hypothesis - all three must hold.

**Key Points:**
- Hypothesis reformulated as testable conjunctive prediction (clustering AND dominance AND sensitivity)
- Three-tier prediction structure (strong/moderate/null) for interpreting results
- Sample size requirements specified (N=480-640 for clustering)
- Falsification clear: failure of any prediction set rejects hypothesis

This meets my standards for scientific rigor. Dr. Sage, does this maintain significance while ensuring testability?

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

Yes, Prof. Vera. This formulation preserves both rigor AND significance. Let me connect the testable hypothesis to field impact:

**Contribution Summary (Final Positioning):**

**Title:** "Empirical Characterization of Alignment Method Signatures in Code Generation: A Multi-Dimensional Evaluation Framework"

**Core Contribution:** We demonstrate that alignment methods for code generation LLMs exhibit empirically detectable "objective function signatures" - characteristic performance profiles across correctness, complexity, and efficiency dimensions - and that current benchmarks vary systematically in their sensitivity to these dimensions.

**Three-Part Result:**
1. **Empirical Finding:** Alignment methods cluster in multi-dimensional performance space (Prediction Set 1)
2. **Mechanistic Insight:** Clustering aligns with feedback signal theory (execution-based methods dominate correctness, preference-based methods show balance) (Prediction Set 2)
3. **Methodological Contribution:** Benchmark sensitivity varies significantly, providing guidance for evaluation design (Prediction Set 3)

**Why This Matters to the Field:**

**For Practitioners:** Actionable guidance on alignment method selection based on deployment needs (correctness-critical vs balanced vs efficiency-optimized code)

**For Researchers:** Evaluation methodology that accounts for multi-dimensional performance - addresses the evaluation crisis raised by NaturalCodeBench (ranking mismatch) and LiveCodeBench (contamination)

**For Benchmark Designers:** Systematic characterization of what existing benchmarks measure, informing design of future evaluation frameworks

**Positioning vs Prior Work:**
- **Multi-objective training** (PrefGen, SIPO): How to optimize multiple objectives during training → we address the complementary problem: how to evaluate multiple objectives after training
- **Benchmark criticism** (NaturalCodeBench, LiveCodeBench): Identify problems with current evaluation → we provide the diagnostic framework
- **Alignment method surveys** (RL Techniques Survey): Catalog methods → we empirically characterize their implicit objectives

**Publication Venues:** ICML, NeurIPS, ICLR (ML core), ACL (code generation focus), or EMNLP (evaluation methodology)

**Research Program Potential:** Dr. Nova's "evaluation ontology" vision positions this as the first paper in a series:
- **Paper 1** (current): Proof-of-concept with correctness-complexity-efficiency
- **Paper 2**: Extended dimensions (readability, security, maintainability)
- **Paper 3**: Temporal analysis (how signatures evolve with model scale, training compute)

**Critical Success Metric:** If Prediction Set 1 (clustering) holds strongly (P1.1: distance > 2.5σ) AND Prediction Set 3 (benchmark sensitivity) holds, this is top-tier venue material. If only moderate clustering (P1.2: 1.5-2.5σ), still publishable but at second-tier venues with careful interpretation.

**Key Points:**
- Contribution is three-fold: empirical + mechanistic + methodological
- Addresses practitioner needs (method selection), researcher needs (evaluation), and benchmark designer needs (framework validation)
- Positions as first paper in research program (extensible framework)
- Publication tier depends on effect sizes (strong clustering → top-tier, moderate → second-tier)

This is ready for Phase 2B verification planning. The hypothesis is specific, testable, significant, and feasible within resource constraints. All personas satisfied?

---

### Exchange 16

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's testable predictions and Dr. Sage's significance argument are solid. Let me give my final feasibility stamp:

**Feasibility Assessment - APPROVED with constraints:**

**GPU Resources:** 60-80 samples × 6-8 models = 480-640 samples. At ~8 minutes per sample (model inference + execution + profiling), that's 64-85 hours. Within the stated 50-120 hour budget from Phase 1. ✅ FEASIBLE

**Within-language controls:** Python-only comparison eliminates language confounds. Models available: SelfCodeAlign (exec-focused), CodeLlama-Python (exec-focused), StarCoder (base), WizardCoder (unknown alignment). Need to verify alignment types, but candidates exist. ✅ FEASIBLE

**Measurement infrastructure:** Pass@k (HumanEval+ test suite), complexity (radon/lizard tools - standard Python packages), efficiency (memory_profiler + cProfile - built-in). All tools are mature, well-documented. ✅ FEASIBLE

**Statistical power:** N=480-640 samples, 6-8 models, Cohen's d=0.5 assumption → power ≈0.80 for detecting clustering at p<0.05. Acceptable. ✅ ADEQUATE

**Risk factors:**
1. ⚠️ If only moderate clustering (P1.2: 1.5-2.5σ), interpretation requires careful caveats
2. ⚠️ Benchmark leaderboard overlap might be <15 models (need to verify actual overlap)
3. ⚠️ Model availability on HuggingFace may exclude some candidate models

**Mitigation:** Start with Phase 1 (leaderboard analysis, 0 GPU hours) to confirm 15+ model overlap. If overlap insufficient, proceed with clustering only (still publishable with caveats about benchmark sensitivity).

**Final verdict:** Hypothesis is scientifically sound, statistically powered, and resource-feasible. Proceed to experimental design.

**Key Points:**
- GPU budget: 64-85 hours (within 50-120 hour Phase 1 estimate)
- Python-only comparison feasible with available models
- Statistical power adequate (N=480-640, power=0.80)
- Risk-mitigated with phased approach (leaderboard analysis first)

I'm satisfied this can work within resource constraints. Dr. Ally, any final refinements before we converge?

---

### Exchange 17

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Perfect! Let me synthesize the FINAL hypothesis statement incorporating all refinements:

**HYPOTHESIS (Final Form):**

**Title:** "Alignment Method Objective Function Signatures in Code Generation: Empirical Characterization via Multi-Dimensional Evaluation"

**Core Claim:** Alignment methods for code generation LLMs with different feedback signal types (execution-based vs preference-based) produce statistically distinguishable performance profiles ("objective function signatures") across correctness, complexity, and efficiency dimensions, and standard benchmarks exhibit differential sensitivity to these dimensions.

**Three Conjunctive Predictions:**

**H1 - Clustering (Objective Function Signatures):**
Models aligned with execution-based methods (SelfCodeAlign, StepCoder) cluster separately from preference-based methods (PrefGen-style DPO) in [correctness, complexity, efficiency] space with intercluster distance > 1.5σ of intracluster variance (moderate threshold) or > 2.5σ (strong threshold).

**H2 - Objective-Specific Dominance (Mechanistic Validation):**
Execution-focused models rank in top 15% for pass@k, preference-focused models show balanced performance (top 30% across all dimensions), base models without alignment rank below 50th percentile.

**H3 - Benchmark Sensitivity (Evaluation Framework Validation):**
Rank correlation difference [r(HumanEval,MBPP) - r(HumanEval,BigCodeBench)] > 0.20, indicating BigCodeBench measures objectives orthogonal to HumanEval/MBPP.

**Experimental Design (Three-Phase):**
1. **Leaderboard Analysis** (0 GPU hrs): Collect 15-20 models, compute benchmark rank correlations → test H3
2. **Model Inference** (64-85 GPU hrs): Generate 60-80 samples × 6-8 models (Python only), measure correctness/complexity/efficiency → test H1, H2
3. **Statistical Analysis** (0 GPU hrs): PCA clustering, ranking analysis, significance tests

**Success Criteria:**
- **Strong success:** All three predictions hold with strong thresholds (P1.1, P2.1-P2.3, P3.1-P3.2)
- **Moderate success:** H1 moderate + H2 partial + H3 holds (publishable with caveats)
- **Failure:** Any prediction set fails completely

**Significance:** Addresses evaluation methodology crisis (NaturalCodeBench ranking mismatch, LiveCodeBench contamination) by providing diagnostic framework for benchmark sensitivity and principled guidance for alignment method selection.

**Novelty:** First systematic characterization of implicit objective functions in post-alignment code models via output distribution analysis - complements prior work on multi-objective training (PrefGen, SIPO).

**Resource Constraints Satisfied:** ✅ No cloud APIs, ✅ public benchmarks only, ✅ 64-85 GPU hours within budget, ✅ avoids gradient measurements, ✅ avoids dataset mismatches

**Key Points:**
- Final hypothesis statement: testable, specific, significant, feasible
- Three-phase experiment with clear success/failure criteria
- Addresses all persona concerns (novelty, falsifiability, significance, feasibility)
- ROUTE_TO_0 constraints fully satisfied

**CONVERGENCE ACHIEVED.** All six convergence criteria met:
✅ SPECIFIC: Clear core claim with three testable predictions
✅ MECHANISM: Feedback signal theory explains clustering
✅ PREDICTIONS: Three prediction sets with quantitative thresholds
✅ NOVELTY: Implicit objective inference (not just multi-objective training)
✅ FEASIBILITY: Resource-constrained experimental design validated
✅ OBJECTIONS: Measurement validity, confounds, causality all addressed

Ready for Final Assessments!

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "objective function signature" framing represents a genuine paradigm shift from measuring trade-offs to reverse-engineering implicit objectives. The connection to implicit bias theory in ML optimization elevates this beyond empirical measurement to conceptual contribution. The evaluation ontology vision positions this as foundational infrastructure for the field.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The three conjunctive prediction sets (clustering, dominance, benchmark sensitivity) with quantitative thresholds (2.5σ for strong, 1.5σ for moderate, specific correlation differences) provide clear falsification criteria. Sample size requirements (N=480-640) ensure statistical power. Any prediction set failing constitutes falsification.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Addresses the field's evaluation methodology crisis identified by NaturalCodeBench and LiveCodeBench. Provides actionable guidance for practitioners (method selection), researchers (multi-dimensional evaluation), and benchmark designers (sensitivity characterization). Positions as first paper in extensible research program. Top-tier venue potential if strong clustering observed.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Resource requirements validated: 64-85 GPU hours within budget, Python-only models available, measurement tools mature (radon, lizard, memory_profiler), statistical power adequate (0.80 for N=480-640). Phased approach mitigates risks (leaderboard analysis first). All ROUTE_TO_0 constraints satisfied (no cloud APIs, public benchmarks, no gradients, no dataset mismatches).

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

We propose to empirically characterize "objective function signatures" of alignment methods for code generation LLMs by analyzing their output distributions across correctness, complexity, and efficiency dimensions. The core insight is that different alignment approaches - execution-based methods (using test pass/fail signals) versus preference-based methods (using human/AI preferences) - implicitly optimize for different objectives, and these differences manifest as statistically detectable performance profiles.

Our hypothesis makes three conjunctive predictions: (1) Models cluster in multi-dimensional performance space according to their alignment method type, with intercluster distance exceeding 1.5-2.5σ of intracluster variance. (2) Execution-focused models demonstrate objective-specific dominance (top 15% for correctness), while preference-focused models show balanced performance across dimensions. (3) Standard benchmarks exhibit differential sensitivity - HumanEval/MBPP correlate strongly (r>0.85) while BigCodeBench decorrelates (r<0.70), indicating they capture different objective dimensions.

The experimental approach uses publicly available leaderboard data and targeted model inference (60-80 code samples per model across 6-8 Python models) to measure these signatures without cloud APIs or gradient access. Falsification is clear: if models fail to cluster, if execution-focused models don't dominate correctness metrics, or if all benchmarks show uniform correlation patterns, the hypothesis is rejected.

The significance lies in addressing the evaluation methodology crisis: recent work shows benchmark rankings misalign with real-world performance (NaturalCodeBench) and contamination undermines single-metric evaluation (LiveCodeBench). Our framework provides diagnostic tools to validate which benchmarks measure which objectives, enabling principled alignment method selection based on deployment needs rather than hype.

The novelty is the reverse direction: prior work demonstrates multi-objective training (how to optimize multiple objectives), while we focus on multi-dimensional evaluation (how to infer which objectives were optimized post-hoc). This completes the feedback loop - without knowing what objectives alignment methods actually optimize for, we cannot evaluate whether training achieved intended goals.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1: Moderate clustering ambiguity** - If intercluster distance falls in 1.5-2.5σ range (weak but significant), interpretation requires caveats about alignment method effect sizes vs confounding factors (training data, checkpoints).
- **Concern 2: Proxy validity** - Using complexity/readability metrics as "quality" proxies assumes these correlate with actual code quality for LLM-generated code. While established for human code, validation needed for LLM outputs with potentially unusual patterns.
- **Concern 3: Benchmark overlap** - Success of H3 (benchmark sensitivity) depends on sufficient model overlap across leaderboards (need 15+). If overlap insufficient, can only test H1-H2.
- **Mitigation Strategy:** Phased approach addresses risks: Start with Phase 1 (leaderboard analysis) to verify model overlap before committing GPU resources. If moderate clustering observed, publish with explicit caveats about effect sizes and call for controlled replication. Validate proxy metrics on small human-annotated sample (50-100 code samples) before claiming "quality" dimension.

---

## Emerged Hypothesis Summary

### Core Statement

Alignment methods for code generation LLMs exhibit empirically detectable "objective function signatures" - characteristic performance profiles across correctness, complexity, and efficiency dimensions that reflect their implicit optimization objectives as determined by feedback signal types (execution-based vs preference-based).

### Causal Mechanism

Different alignment methods use fundamentally different feedback signals during training: execution-based methods (e.g., SelfCodeAlign with RLHF, StepCoder with compiler feedback) receive binary pass/fail signals emphasizing correctness; preference-based methods (e.g., PrefGen with DPO) receive comparative preference judgments emphasizing human/AI-defined quality criteria. These feedback signals act as implicit objective functions - the model learns to optimize whatever the feedback measures. Over thousands of training steps, this differential feedback shapes distinct output distributions. When we measure the resulting code across multiple dimensions, these learned biases manifest as statistically detectable clusters in performance space. Benchmarks vary in sensitivity because they emphasize different subsets of these dimensions (HumanEval emphasizes correctness, BigCodeBench emphasizes complexity/real-world patterns).

### Variables

**Independent Variables:**
- Alignment method type (categorical): execution-based, preference-based, unaligned baseline
- Feedback signal structure: binary (pass/fail), scalar (reward), comparative (preference pairs), rubric-based (multi-criteria AI evaluation)

**Dependent Variables:**
- Correctness: pass@k on HumanEval+, MBPP+, BigCodeBench test suites
- Complexity: cyclomatic complexity (McCabe), AST depth, token count (radon/lizard tools)
- Efficiency: runtime (seconds), peak memory (MB), algorithmic complexity class (profiling-based)

**Control Variables:**
- Programming language (Python only to avoid language confounds)
- Base model family (prefer Llama-3-8B variants for consistency)
- Task distribution (HumanEval+ task set for controlled comparison)

### Key Assumptions

1. **Feedback signals shape optimization:** Training with different feedback types causes models to prioritize different objectives (execution vs quality vs balanced)
2. **Signatures persist post-training:** The learned biases from alignment are detectable in output distributions even after training completes
3. **Proxy validity:** Code complexity/efficiency metrics correlate sufficiently with "quality" to serve as objective dimensions
4. **Benchmark orthogonality:** Different benchmarks emphasize different objective dimensions (not all just measuring "general code ability")
5. **Public data sufficiency:** Leaderboard scores + targeted inference provide sufficient signal without access to training data/gradients

### Null Hypothesis

Models aligned with different methods produce statistically indistinguishable output distributions across correctness, complexity, and efficiency dimensions (intercluster distance < 1.5σ), AND/OR all alignment method types show similar ranking patterns across dimensions (no objective-specific dominance), AND/OR all benchmarks exhibit uniform high correlation (r > 0.85) indicating they measure identical objectives.

### Predictions

**Prediction 1: Alignment Method Clustering**
- Models cluster in [correctness, complexity, efficiency] 3D space by alignment method type
- Strong evidence: Intercluster distance > 2.5σ of intracluster variance
- Moderate evidence: 1.5σ < distance < 2.5σ
- Null: distance < 1.5σ (no alignment method effect)

**Prediction 2: Objective-Specific Dominance**
- Execution-focused models (SelfCodeAlign, StepCoder): Top 15% for correctness (pass@k), variable on other dimensions
- Preference-focused models (PrefGen-style DPO): Top 30% across all three dimensions (balanced optimization)
- Unaligned baselines (CodeLlama-Base, StarCoder-Base): Below 50th percentile for correctness

**Prediction 3: Differential Benchmark Sensitivity**
- HumanEval-MBPP correlation: r > 0.85 (similar tasks, similar objectives)
- HumanEval-BigCodeBench correlation: r < 0.70 (different complexity emphasis)
- Correlation difference: r_HM - r_HB > 0.20 (significant differential sensitivity)

### Novelty

**What's New:**
- **Reverse-engineering implicit objectives:** Prior work demonstrates multi-objective training (forward: objective → model). We demonstrate objective inference (reverse: model outputs → inferred objective). This completes the evaluation feedback loop.
- **Objective function signatures:** Introduces concept of characteristic performance profiles as "signatures" of alignment methods, connecting to implicit bias theory in ML optimization
- **Benchmark sensitivity framework:** Systematic characterization of which benchmarks measure which objective dimensions, addressing evaluation methodology crisis

**Comparison to Prior Work:**
- PrefGen, SIPO: Multi-objective optimization during training → We: Multi-dimensional evaluation after training
- NaturalCodeBench, LiveCodeBench: Identify evaluation problems → We: Provide diagnostic framework for benchmark characterization
- RL Techniques Survey: Catalog alignment methods → We: Empirically characterize their implicit objectives

### Scope & Boundaries

**In Scope:**
- Python code generation models (HumanEval+/MBPP+/BigCodeBench tasks)
- Three objective dimensions: correctness, complexity, efficiency
- Public models accessible via HuggingFace (no proprietary/closed models)
- Post-alignment analysis only (not training dynamics)

**Out of Scope:**
- Non-Python languages (Solidity, Java, C++ - confounds from language differences)
- Training-time analysis (gradients, loss curves - requires access to training runs)
- Subjective quality dimensions (elegance, style - requires human annotation)
- Repository-level tasks (focus on function-level for controlled comparison)

**Boundary Conditions:**
- Requires 15+ models with overlapping leaderboard data for benchmark sensitivity analysis
- Assumes proxy metrics (complexity/efficiency) correlate with quality for LLM code
- Limited to alignment methods with publicly documented feedback signals
- Statistical power adequate for N=480-640 samples (6-8 models × 60-80 samples each)

### Experimental Setup

**Phase 1: Leaderboard Analysis (0 GPU hours)**
- Data collection: HumanEval+, MBPP+, BigCodeBench public leaderboards
- Model selection: Identify 15-20 models with overlapping coverage, annotate alignment method types
- Rank correlation computation: Spearman ρ for all benchmark pairs
- Test Prediction 3 (benchmark sensitivity): Compute r_HM - r_HB, significance test

**Phase 2: Targeted Model Inference (64-85 GPU hours)**
- Model selection: 6-8 Python models (2-3 execution-focused, 2-3 preference-focused, 1-2 baselines)
- Code generation: 60-80 samples per model on HumanEval+ tasks (sampling temperature 0.8)
- Measurement:
  - Correctness: Execute with HumanEval+ test suite, compute pass@k
  - Complexity: radon (cyclomatic), lizard (AST depth), token count
  - Efficiency: memory_profiler (peak memory), cProfile (runtime)
- Output: [correctness, complexity, efficiency] vectors for each model (N=480-640 total samples)

**Phase 3: Statistical Analysis (0 GPU hours)**
- Clustering: PCA on signature vectors, k-means with k=3 (exec/pref/baseline groups)
- Significance test: Intercluster distance vs intracluster variance (effect size Cohen's d)
- Ranking analysis: Rank models on each dimension, test Prediction 2 (objective-specific dominance)
- Visualization: 2D/3D scatter plots with confidence ellipses per alignment method group

**Success Criteria:**
- **Strong success:** P1.1 (distance > 2.5σ) + P2.1-P2.3 (dominance patterns) + P3.1-P3.2 (r difference > 0.20) → Top-tier venue
- **Moderate success:** P1.2 (distance 1.5-2.5σ) + partial P2 + P3 holds → Second-tier venue with caveats
- **Failure:** P1.3 (distance < 1.5σ) OR dominance patterns absent OR benchmark uniformity (r > 0.85 all pairs) → Hypothesis rejected

### Related Work & Baselines

**Multi-Objective Training:**
- PrefGen (Peng et al., 2025): DPO with Pass@k + Gas@k + Secure@k for smart contracts - demonstrates multi-objective training works, but limited to specialized domain (Solidity)
- SIPO (Li et al., 2025): Self-improving DPO for Pareto-optimal multi-objective alignment - training-time optimization, not evaluation methodology
- RL-Text2Vis (Rahman et al., 2026): GRPO with 3-way reward (textual + code + visualization) - training focus, achieves 22% over GPT-4o

**Benchmark Criticism:**
- NaturalCodeBench (Zhang et al., 2024): Shows 80% HumanEval → 20% real-world task performance mismatch - identifies problem, we provide diagnostic
- LiveCodeBench (Jain et al., 2024): Contamination-free evaluation with 1200 citations - addresses data leakage, we address objective dimension coverage
- HumanEval Pro/MBPP Pro (Yu et al., 2024): Self-invoking benchmarks reveal gaps - critiques single metrics, we validate multi-dimensional alternatives

**Alignment Methods:**
- SelfCodeAlign (Wei et al., 2024): Self-alignment via execution RLHF, 67.1 pass@1 HumanEval+ - our execution-focused exemplar
- StepCoder (Dou et al., 2024): RL from compiler feedback (CCCS+FGO) - execution-based alignment, 83 citations
- Crowd-sourced RLHF (Wong & Tan, 2025): Bayesian optimization with distributed feedback - preference-based approach

**Baseline Comparisons:**
- Execution-focused baseline: SelfCodeAlign (pass@k optimization via test execution)
- Preference-focused baseline: PrefGen-style DPO (multi-criteria optimization)
- Unaligned baseline: CodeLlama-Base (pre-alignment checkpoint)

### Phase 2B Readiness Seeds

**Verification Strategy:**
- **MUST_WORK gate:** Prediction 1 (clustering) must hold at least at moderate level (distance > 1.5σ) - foundation for all other claims
- **SHOULD_WORK gates:** Predictions 2-3 can partially fail if clustering strong - would indicate alignment signatures exist but mechanisms/benchmarks need refinement
- **Dependency structure:** Clustering (H1) → Dominance (H2) + Sensitivity (H3). If H1 fails, entire hypothesis framework collapses

**Sub-Hypothesis Decomposition:**
- H-E1 (EXISTENCE): Clustering exists with distance > 1.5σ (MUST_WORK)
- H-M1 (MECHANISM): Execution-focused models dominate correctness (SHOULD_WORK, depends on H-E1)
- H-M2 (MECHANISM): Preference-focused models show balanced performance (SHOULD_WORK, depends on H-E1)
- H-M3 (BOUNDARY): BigCodeBench measures different dimensions than HumanEval (SHOULD_WORK, independent)

**Measurement Feasibility:**
- Correctness: HumanEval+ test suite (open-source, standardized)
- Complexity: radon + lizard (Python packages, deterministic)
- Efficiency: memory_profiler + cProfile (built-in, reliable)
- All measurements can be automated via Python scripts

**Risk Factors:**
1. **Moderate clustering (distance 1.5-2.5σ):** Publishable but requires caveats about effect sizes → Mitigation: Transparent reporting, sensitivity analysis
2. **Insufficient benchmark overlap (<15 models):** Can't test H3 → Mitigation: Phase 1 verifies overlap before GPU commitment
3. **Proxy validity (complexity as quality):** Assumptions may not hold → Mitigation: Validate on small human-annotated sample (50-100)

### Established Facts

**Build On (From Literature):**
- Multi-objective optimization is effective for code generation (PrefGen achieves gains on Pass@k + Gas@k + Secure@k)
- Different alignment methods produce different performance profiles (SelfCodeAlign 67.1 vs CodeLlama 44.7 on HumanEval+)
- Current benchmarks have measurement issues (contamination in LiveCodeBench, real-world mismatch in NaturalCodeBench)
- Implicit bias exists in ML optimization (SGD, Adam have inductive biases independent of explicit objectives)

**Prove New:**
- Alignment methods have statistically detectable objective function signatures in multi-dimensional space
- These signatures align with feedback signal theory (execution-focused → correctness bias, preference-focused → balanced)
- Benchmarks differ systematically in sensitivity to objective dimensions (not just task difficulty)
- Multi-dimensional evaluation framework can characterize alignment methods post-hoc

**Uncertainty / Open Questions:**
- What is the mechanistic link between feedback signal structure and output distribution signatures? (We observe correlation, mechanism is theoretical)
- Do signatures generalize across model scales (7B vs 70B parameters)? (Out of scope, but important future work)
- Can we discover additional objective dimensions beyond correctness/complexity/efficiency? (Evaluation ontology vision, Phase 2+)

---


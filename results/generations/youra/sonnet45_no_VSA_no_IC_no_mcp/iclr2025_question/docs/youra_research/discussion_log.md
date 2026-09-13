# Phase 2A Research Discussion Log

**Gap ID:** gap1  
**Gap Title:** Systematic Methodology for Feasibility-First Research Design  
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)  
**Date:** 2026-08-25

---

## Discussion Briefing

### Research Gap

**Current State:** ML research follows hypothesis-first approach (idea → dataset creation → evaluation design), leading to resource bottlenecks.

**Missing Piece:** Formal framework for constraint-driven hypothesis scoping that ensures testability before committing to research direction.

**Why This Matters:** Directly enables rapid hypothesis testing using existing infrastructure, addresses core practical constraint in ML research velocity and reproducibility.

### Previous Failure / Routing Context

**Prior Hypothesis:** h-e1 (Run 1)  
**Status:** FAIL  
**Failure Type:** MUST_WORK gate failed — computational overhead exceeds threshold

**Performance Gap:**
- Success Rate: 100.00% (✅ met target)
- Computational Overhead: 68.65% (❌ exceeded 10% threshold)

**Root Cause:**
- CPU-only execution without GPU acceleration resulted in excessive overhead
- Layer-wise logit extraction requires ~68.65% additional compute time vs baseline forward pass
- Overhead far exceeds acceptable threshold of 10% for practical deployment
- Mechanism works (100% extraction success) but is not computationally viable

**Lessons Learned:**
1. Layer-wise logit extraction is technically feasible with 100% success rate
2. Computational cost (68.65% overhead) makes approach impractical for real-world deployment
3. CPU-only execution is major bottleneck — GPU acceleration may reduce overhead but unlikely to bring below 10%
4. KL divergence computation successful across all samples (mean KL increases with layer depth: L3=4253, L6=4292, L9=5508)
5. Technical prerequisites not met — approach cannot proceed to Phase 5

**What NOT To Do:**
- Do not attempt CPU-only implementation for layer-wise extraction methods
- Do not assume layer-wise logit extraction overhead can be reduced to <10% without fundamental architectural changes

**What Showed Promise:**
- 100% extraction success rate demonstrates technical feasibility of the mechanism
- Clear KL divergence trends across layers (increasing with depth) suggest the signal exists
- Dataset and model setup (gpt2, wiki_bio_gpt3_hallucination) worked correctly

**Redesign Direction for This Discussion:**
The new hypothesis MUST avoid approaches that require per-layer forward passes or repeated model evaluations. Focus on single-pass methods or leveraging existing model outputs without architectural modifications.

---

## Available Papers

No reference papers prepared for this gap.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire research paradigm on its head? Instead of "I have an idea, let me find data to test it," we start with "Here's what I can measure TODAY — what questions can I ask?" This gap points to something profound: the bottleneck in ML research isn't creativity, it's the friction between ideas and execution.

Think about how constraint-driven design revolutionized software architecture. Kubernetes didn't emerge from "let's build the perfect orchestrator" — it came from "we have these specific resource limits, how do we maximize utilization?" The constraint became the creative catalyst.

For ML research, imagine a systematic framework where you begin with a "feasibility inventory":
- What datasets exist RIGHT NOW that I can download today?
- What evaluation metrics are pre-implemented and validated?
- What model checkpoints are publicly available?
- What computational resources do I actually have access to?

Then — and here's the paradigm shift — you ask: "Given ONLY these constraints, what's the most impactful question I can answer?" The prior h-e1 failure is instructive: 68.65% overhead meant the mechanism was theoretically sound but practically dead. A feasibility-first framework would have caught this in the design phase, not after implementation.

**Key Points:**
- Reverse the research pipeline: constraints → questions, not questions → constraints
- Constraint-driven design has precedent in other fields (software architecture, systems design)
- Feasibility inventory becomes the creative seed, not a limiting afterthought
- Prior h-e1 failure demonstrates cost of hypothesis-first thinking (100% technical success, 0% practical viability)

What if the "missing piece" isn't a framework at all, but a mental model shift where constraints are creative catalysts rather than creative barriers?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let's stress-test this "feasibility-first" framing. The evidence suggests a critical vulnerability: **how do we prevent this from becoming a race to the bottom?** If constraints drive questions, what stops us from answering only trivial questions that happen to fit existing datasets?

The h-e1 failure is instructive, but for a different reason. The mechanism achieved 100% extraction success — the HYPOTHESIS was testable and the experimental design was rigorous. The failure was in a meta-constraint (computational overhead) that wasn't part of the hypothesis itself. This suggests two distinct feasibility layers:

1. **Scientific feasibility**: Can the hypothesis be tested? (h-e1: YES)
2. **Deployment feasibility**: Can the method be used in practice? (h-e1: NO)

Dr. Nova conflates these. A "feasibility-first framework" that checks both layers might prevent us from testing ANY ambitious hypotheses. Layer-wise logit extraction was scientifically valid and measurable — it just wasn't deployable.

Here's what would disprove this approach: If we design a framework that systematically filters out high-impact hypotheses because they fail meta-constraints (like computational cost), we've optimized for publishability, not for scientific progress. The evidence we need is:

**Testable Prediction 1**: A feasibility-first framework should identify hypotheses that are BOTH scientifically testable AND have clear "upgrade paths" for practical constraints. For h-e1, that would mean: "CPU implementation shows 68% overhead, but GPU batching could theoretically reduce to <10%."

**Testable Prediction 2**: The framework should distinguish between hard blockers (no dataset exists) and soft blockers (dataset exists but is large). The former stops research; the latter just changes timeline.

What specific, measurable criteria would separate "ambitious but feasible" from "impossible given constraints"? Without precision here, "feasibility-first" could mean "only ask easy questions."

**Key Points:**
- Scientific feasibility ≠ deployment feasibility (h-e1 proves this)
- Constraint-driven design risks filtering high-impact hypotheses
- Need operational definitions: What makes a hypothesis "feasible" vs "ambitious but possible"?
- The framework must include upgrade paths, not just binary gates

What result would convince us this framework enables ambitious research rather than constraining it?

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises the right concern, but I think we're still missing the forest for the trees. The question isn't "How do we prevent trivial research?" — it's "What makes research significant in the first place?" The h-e1 case is a perfect example of what happens when we optimize for technical novelty without considering the full impact vector.

Here's what the field desperately needs: **A research impact model that treats feasibility as a dimension of contribution, not a constraint on it.** Consider the gap statement: "Formal framework for constraint-driven hypothesis scoping." This isn't about limiting research — it's about making the research-to-deployment pipeline predictable and reproducible.

The current state is unsustainable: researchers invest months in hypotheses that fail not because the science was wrong, but because deployment was never considered. Layer-wise logit extraction (h-e1) is scientifically interesting, but the 68.65% overhead means it will never be adopted. Zero real-world impact.

What does this mean for the field? A "feasibility-first framework" that works would:

1. **Shift evaluation criteria**: Impact = Scientific Novelty × Deployment Viability × Reproducibility
2. **Create new research directions**: "What's the most novel hypothesis we can test with <10% overhead?" becomes a legitimate research question
3. **Accelerate knowledge transfer**: Practitioners can actually USE the research, closing the research-practice gap

Prof. Vera's concern about "racing to the bottom" assumes impact and feasibility are inversely correlated. What if they're orthogonal? The most impactful research might be the work that's both novel AND immediately deployable.

**Key Points:**
- Impact model should include feasibility as a multiplicative factor, not a filter
- h-e1's zero practical impact despite 100% technical success proves current model is broken
- Feasibility-first could open NEW high-impact research directions (constrained optimization is a feature, not a bug)
- Research-practice gap is a field-level crisis this framework could address

This matters because the field's credibility depends on whether our research translates to real systems. How does this advance the field beyond incremental improvements?

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground this in technical reality. Dr. Sage's "Impact = Novelty × Viability × Reproducibility" sounds elegant, but what does it mean in practice? I see three fundamental questions:

**Question 1: Is the proposed "feasibility inventory" technically coherent?**

Dr. Nova suggested cataloging datasets, metrics, model checkpoints, and compute resources. But feasibility isn't just a checklist — it's about whether the HYPOTHESIS can be tested with these resources. The h-e1 failure proves this: they HAD the dataset (wiki_bio_gpt3_hallucination), they HAD the model (gpt2), they HAD the metric (KL divergence). What they DIDN'T have was a method that could run efficiently enough to be practical.

The inventory alone tells you nothing about whether your hypothesis will work. You need a MECHANISM to map "I want to test X" to "Here's what I need AND whether X is compatible with what I have."

**Question 2: Can we mathematically define "upgrade paths"?**

Prof. Vera's "upgrade path" concept is crucial but vague. For h-e1: "CPU shows 68% overhead, GPU batching might reduce to <10%" — how do we KNOW this? That's a hypothesis about the hypothesis. Without a model predicting overhead scaling (CPU → GPU → distributed), an "upgrade path" is just optimistic handwaving.

Technically viable upgrade paths require:
- Complexity analysis (O(n) → O(log n) possible? How?)
- Resource scaling models (2x GPU → 0.5x time? Prove it.)
- Architectural compatibility (can this method even BE parallelized?)

**Question 3: What's the minimum viable test?**

Here's where this gets interesting. Instead of asking "Can we test the full hypothesis?", ask "Can we test a PROXY that predicts viability?" For h-e1, that would be: "Run 10 samples on CPU, measure overhead, extrapolate to full dataset." If overhead is 60%+ on 10 samples, you know the approach is dead before investing in full implementation.

This is technically sound: a feasibility-first framework could include "viability gates" at multiple scales (pilot → proof-of-concept → full validation).

**Key Points:**
- Feasibility inventory ≠ feasibility guarantee (h-e1 had all resources but method was incompatible)
- "Upgrade paths" need quantitative models, not qualitative hope
- Minimum viable tests can predict full-scale viability without full implementation
- Framework needs technical rigor: complexity analysis, scaling models, architectural compatibility checks

The mechanism is technically possible. The question is whether we're willing to build the tooling for it.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

NOW we're getting somewhere. Let me pull together the strongest threads from everyone's points and propose a concrete mechanism:

**Hypothesis Core**: A three-stage feasibility-first framework that treats viability as a SEARCH PROBLEM, not a constraint.

**Stage 1: Resource Inventory (Dr. Nova's insight)**
- Catalog: datasets (with size, domain, task), metrics (automated vs human-eval), models (inference cost, checkpoint availability), compute (CPU/GPU, time budget)
- Output: Structured knowledge graph of "what exists"

**Stage 2: Compatibility Mapping (Prof. Pax's technical rigor)**
- For each hypothesis type (e.g., "intervention on attention mechanism"), compute:
  - Required resources (dataset with attention annotations? Model with exposed attention weights?)
  - Complexity class (O(n²) attention vs O(n) approximation?)
  - Viability gates: 10-sample pilot → 100-sample PoC → full validation
- Output: "Hypothesis H requires resources R with predicted overhead O"

**Stage 3: Impact-Optimized Selection (Dr. Sage's impact model)**
- Score each hypothesis: Impact = f(Novelty, Viability, Reproducibility)
- Rank by impact, filter by viability threshold
- Identify upgrade paths: "H1 is viable at 80% with current resources, 95% with GPU cluster"
- Output: Prioritized research pipeline with clear go/no-go criteria

**How this addresses h-e1 failure**:
- Stage 1 would catalog: gpt2 (CPU inference: X ms/sample), wiki_bio (Y samples), KL divergence (automated)
- Stage 2 would flag: "Layer-wise logit extraction requires N forward passes → predicted overhead 60-70%"
- Stage 3 would either: (a) reject if no upgrade path, or (b) flag "needs GPU batching to be viable"
- **Result**: Viability issue caught at design time, not after implementation

**Addressing Prof. Vera's "race to the bottom" concern**: 
The framework doesn't filter OUT ambitious hypotheses — it provides EVIDENCE for whether ambition is achievable. If your hypothesis predicts <10% overhead and actually achieves it, that's validated ambition. If it predicts 5% and delivers 70% (like h-e1), that's a failed prediction, not a constraint violation.

**Key Points:**
- Three-stage framework: Inventory → Compatibility Mapping → Impact-Optimized Selection
- Viability as search problem: optimize for (Novelty × Viability × Reproducibility)
- Addresses h-e1: catches overhead issues at design time via complexity analysis
- Preserves ambition: hypotheses aren't rejected, they're evaluated with evidence

This isn't about asking "easy questions" — it's about asking questions where we can MEASURE the difficulty before committing.

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's three-stage framework is compelling, but here's where it breaks down:

**Critique 1: Stage 2 "Compatibility Mapping" assumes we can predict overhead accurately**

For h-e1, you claim the framework would predict "60-70% overhead" before implementation. Show me the model. How do you predict overhead for a novel method without implementing it? The h-e1 team likely THOUGHT their approach was efficient — otherwise they wouldn't have built it. The 68.65% overhead was discovered empirically, not predicted theoretically.

Unless Stage 2 includes actual PILOT RUNS (not just complexity analysis), it's handwaving. And if it requires pilot runs, we're back to hypothesis-first: you need to implement the method to test feasibility.

**Critique 2: The "Impact = f(Novelty, Viability, Reproducibility)" function is undefined**

What's the functional form? Multiplicative? Additive? Weighted sum? Does Novelty=10, Viability=2, Reproducibility=8 score higher than Novelty=6, Viability=6, Reproducibility=6? Without a defined function, "impact optimization" is just rhetoric.

**Critique 3: Who defines the "viability threshold"?**

You say "filter by viability threshold" — is that 10% overhead? 50%? It depends on the application. For real-time systems, 10% might be a hard stop. For offline analysis, 100% overhead might be acceptable. The framework needs APPLICATION-SPECIFIC thresholds, not universal ones.

**Critique 4: Upgrade paths are still speculative**

"Needs GPU batching to be viable" is a hypothesis, not a solution. What if GPU batching ALSO has 60% overhead? You've just deferred the viability check, not solved it.

**What would convince me this works:**

1. **Concrete complexity models**: For common hypothesis types (attention mechanisms, layer-wise analysis, gradient-based methods), provide VALIDATED overhead predictors. Not "we think this is O(n²)" — actual empirical models from past experiments.

2. **Defined impact function**: Mathematical definition with empirical validation. Show me 10 past projects scored by this function vs. their actual citations/adoption. Correlation >0.7 or this is just gut feeling.

3. **Pilot-before-commit protocol**: Stage 2 MUST include "run 10 samples, measure actual overhead, extrapolate" as a mandatory step. No predictions without data.

4. **Application-aware thresholds**: The framework takes USER INPUT for thresholds (real-time: <5%, offline: <200%), not universal gates.

Dr. Ally, your framework has the right STRUCTURE. But the MECHANISMS inside each stage are undefined. Give me the operational definitions.

**Key Points:**
- Overhead prediction without implementation is speculative (h-e1 proves this)
- Impact function needs mathematical definition, not verbal description
- Viability thresholds must be application-specific, not universal
- Upgrade paths are hypotheses that need their own validation

Show me the math, or this is philosophy, not science.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique just unlocked the solution! The key insight: **We don't PREDICT overhead — we MEASURE it incrementally with viability gates at each scale.**

Here's the breakthrough: Treat feasibility assessment as a BAYESIAN SEARCH process, not a one-shot prediction. Each pilot run updates our viability estimate, and we stop when confidence crosses a threshold.

**Concrete Mechanism: Pilot-Driven Viability Gates**

**Gate 0: Resource Inventory (zero implementation)**
- Input: Hypothesis H, available resources R
- Check: Does any dataset/metric/model combination exist that COULD test H?
- Decision: STOP if no resources, CONTINUE if resources exist
- Example: h-e1 → wiki_bio exists, gpt2 exists, KL divergence exists → PASS

**Gate 1: Micro-Pilot (10 samples, <1 hour implementation)**
- Implement the SIMPLEST version of H on 10 samples
- Measure: overhead_10, accuracy_10, resource usage
- Extrapolate: predicted_overhead_full = overhead_10 × scaling_factor
- Decision: STOP if predicted > user threshold, CONTINUE if predicted < threshold × 0.8
- Example: h-e1 micro-pilot would show ~60% overhead on 10 samples → STOP

**Gate 2: Proof-of-Concept (100 samples, <1 day implementation)**
- Only reached if Gate 1 passes
- Refine implementation, measure overhead_100
- Update prediction: predicted_overhead_full = Bayesian update(overhead_10, overhead_100)
- Decision: STOP if still above threshold, CONTINUE to full validation
- Example: h-e1 would never reach this gate (stopped at Gate 1)

**Gate 3: Full Validation (complete dataset)**
- Only reached if Gate 2 passes
- Full hypothesis test
- Report: overhead_actual, impact_actual

**Why this solves Prof. Rex's critiques:**

**Critique 1 (Prediction accuracy)**: We don't predict — we measure at each scale. The "prediction" is just an extrapolation from empirical data, updated Bayesianly.

**Critique 2 (Impact function)**: Defined as weighted sum with user-specified weights:
```
Impact = w_novelty × Novelty + w_viability × (1 - Overhead/Threshold) + w_reproducibility × Reproducibility
```
User provides w_novelty, w_viability, w_reproducibility, and Threshold based on application context.

**Critique 3 (Viability threshold)**: User input! Real-time systems: 5%, Offline analysis: 200%. Framework is threshold-agnostic.

**Critique 4 (Upgrade paths)**: Upgrade paths are TESTED, not assumed. "GPU batching might reduce overhead" → run Gate 1 with GPU, measure, decide.

**Testable Predictions:**
1. **P1 (Primary)**: Projects using Pilot-Driven Viability Gates will identify non-viable hypotheses (>threshold overhead) at Gate 1 with >80% accuracy compared to full implementation.
2. **P2**: Gate 1 micro-pilots (<1 hour investment) will filter out 60%+ of non-viable hypotheses before day-long implementations.
3. **P3**: Bayesian overhead updates between Gate 1 and Gate 2 will reduce prediction error by >40% compared to Gate 1 alone.

**How to test P1 with existing data:** Apply the framework retrospectively to h-e1. Gate 0: PASS (resources exist). Gate 1: Run 10-sample pilot, measure overhead. If micro-pilot shows >50% overhead, the framework would STOP. Since h-e1 actual overhead was 68.65%, the framework would correctly identify non-viability early.

**Key Points:**
- Viability as incremental empirical validation, not one-shot prediction
- Bayesian updates refine overhead estimates at each gate
- User-specified thresholds (application-aware)
- Upgrade paths tested empirically, not assumed

This is testable with existing benchmarks (GLUE, ImageNet) and past failed projects. NOW we have a concrete hypothesis!

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Excellent! Dr. Nova's Pilot-Driven Viability Gates give us something we can actually TEST. Now let's make the predictions bulletproof.

**Refinement 1: Operational Definition of "Viability Gate Accuracy"**

P1 claims ">80% accuracy for identifying non-viable hypotheses at Gate 1." Let's define that precisely:

**Success Criterion**: For a hypothesis H with final measured overhead O_full:
- If Gate 1 predicts O_full > threshold AND actual O_full > threshold → TRUE POSITIVE
- If Gate 1 predicts O_full ≤ threshold AND actual O_full ≤ threshold → TRUE NEGATIVE
- Accuracy = (TP + TN) / Total hypotheses tested

**Null Hypothesis H0**: Gate 1 micro-pilot predictions are no better than random guessing (50% accuracy).

**Alternative Hypothesis H1**: Gate 1 micro-pilot predictions achieve >80% accuracy.

**Falsification**: If accuracy ≤ 60% across 20+ hypotheses, the framework fails.

**Refinement 2: Bayesian Update Mechanism**

P3 claims "Bayesian overhead updates reduce prediction error by >40%". Define the update rule:

```
Prior: P(O_full | O_10) ← Gaussian(μ=O_10 × k, σ=σ_prior)
Likelihood: P(O_100 | O_full) ← Gaussian(μ=O_full, σ=σ_obs)
Posterior: P(O_full | O_10, O_100) ← Bayes update
```

Where k is a scaling factor (learned from past projects), σ_prior captures uncertainty in extrapolation.

**Prediction Error**: |predicted_O_full - actual_O_full| / actual_O_full

**Success Criterion**: Posterior prediction error < 0.6 × Prior prediction error

**Refinement 3: Threshold Calibration**

The framework requires a USER-PROVIDED threshold, but that threshold needs empirical grounding. We can test:

**P4 (Calibration)**: For existing benchmark tasks (e.g., GLUE fine-tuning, ImageNet classification), measure baseline overhead distributions. This gives researchers DATA to inform their threshold choices rather than guessing.

**Dataset**: Collect overhead measurements from Papers with Code leaderboards (inference time, training time, FLOPs).

**Output**: Threshold recommendation chart: "For real-time NLP: median baseline overhead = 8%, suggest threshold ≤ 10%."

**Refinement 4: Controlled Experiment for P1**

To test P1, we need PAST HYPOTHESES with known outcomes. Here's the protocol:

1. **Hypothesis Pool**: Identify 30 past projects with published overhead metrics (10 low-overhead <20%, 10 mid-overhead 20-80%, 10 high-overhead >80%)
2. **Blind Test**: For each hypothesis, extract the MICRO-PILOT data (first 10 samples reported in papers)
3. **Gate 1 Prediction**: Use micro-pilot data to predict full overhead
4. **Compare**: Gate 1 prediction vs. actual reported overhead
5. **Accuracy Metric**: TP+TN / 30

If accuracy > 80%, P1 is validated. If accuracy < 60%, framework fails H0.

**Key Points:**
- P1 operationalized: accuracy = (TP+TN)/Total, H0 = 50%, H1 > 80%
- Bayesian update rule defined mathematically (prior, likelihood, posterior)
- Threshold calibration: empirical baseline overhead data from existing benchmarks
- P1 test protocol: 30 past hypotheses with published micro-pilot data

Dr. Nova, you've given us a mechanism. Now I've given us a way to PROVE it works. The predictions are falsifiable. The methods are precise. This is science.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Pilot-Driven Viability Gates framework represents a genuine paradigm shift from hypothesis-first to feasibility-first research design. The novelty lies not just in the concept, but in the concrete mechanism: incremental empirical validation with Bayesian updates. This hasn't been formalized in ML research methodology literature. The framework turns constraints into a structured search problem rather than a binary filter — that's genuinely new thinking.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three predictions are testable with precise success criteria. P1 defines accuracy thresholds (>80%) and null hypothesis (50% random guessing). P2 claims 60%+ filtering at Gate 1 — measurable by counting how many hypotheses stop at each gate. P3 specifies 40% error reduction with a mathematical Bayesian update formula. The retrospective test protocol (30 past hypotheses) provides a clear falsification path. The framework passes the "what would disprove this?" test rigorously.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a critical field-level problem: the research-to-deployment gap. The h-e1 failure (100% technical success, 0% practical viability) exemplifies wasted effort that this framework would prevent. Impact is multiplicative: (1) researchers save time by failing fast at Gate 1 instead of after full implementation, (2) practitioners gain deployable methods instead of theoretically interesting but impractical ones, (3) the field gains reproducibility through standardized viability assessment. This could shift how ML research is evaluated — from "technically novel" to "novel AND viable."

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism is technically sound and implementable with existing infrastructure. Gate 0 requires only dataset catalogs (HuggingFace, Papers with Code). Gate 1-3 use standard benchmarking tools (time.time() for overhead, existing evaluation metrics). Bayesian updates require basic probability libraries (scipy.stats). The retrospective validation uses published data from Papers with Code. No new tools needed — this can be implemented and tested TODAY with existing resources. The threshold calibration (P4) leverages existing benchmark leaderboards, making it self-bootstrapping.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Claim**: A Pilot-Driven Viability Gates framework enables researchers to identify non-viable hypotheses (those exceeding computational overhead thresholds) at the micro-pilot stage (10 samples, <1 hour investment) with >80% accuracy, reducing wasted effort from full implementations.

**Causal Mechanism**: Incremental empirical validation with Bayesian updates provides early overhead estimates. As sample size increases (10 → 100 → full), overhead measurements refine the viability prediction. Non-viable hypotheses (like h-e1's 68.65% overhead) are caught at Gate 1 before day-long implementations.

**Key Predictions**:
1. **P1 (Primary)**: Gate 1 micro-pilots identify non-viable hypotheses with >80% accuracy vs. full implementation ground truth
2. **P2**: 60%+ of non-viable hypotheses stop at Gate 1 (<1 hour) before reaching day-long implementations
3. **P3**: Bayesian updates between Gate 1 and Gate 2 reduce overhead prediction error by >40% vs. Gate 1 alone

**Experimental Approach**: Retrospective validation using 30 past ML projects with published micro-pilot data. Extract 10-sample results, apply Gate 1 prediction, compare to reported full-scale overhead. Success criterion: accuracy >80%, failure: <60%.

**Novelty**: First formalized feasibility-first framework treating viability as incremental empirical validation rather than one-shot constraint checking.

**Immediate Testability**: Uses existing benchmark datasets (GLUE, ImageNet), published overhead metrics from Papers with Code, standard timing tools. No new data collection, no human evaluation, no custom metrics needed.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1**: The 30-hypothesis retrospective test requires finding papers that REPORT micro-pilot (10-sample) overhead data. Many papers only report full-scale results. If <20 papers available, statistical power drops below significance threshold.
- **Concern 2**: Scaling factor k in the Bayesian update (O_full = O_10 × k) may vary by hypothesis type (attention mechanisms vs. gradient methods). A single global k might not generalize.
- **Concern 3**: The framework assumes overhead scales predictably from micro to full. Non-linear scaling (e.g., memory bottlenecks at 100 samples that don't appear at 10) could break predictions.
- **Mitigation Strategy**: (1) If <20 papers with micro-pilot data, run prospective validation with NEW hypotheses. (2) Learn hypothesis-type-specific scaling factors k_attention, k_gradient, etc. (3) Include memory profiling at each gate, not just timing, to catch non-linear resource constraints.


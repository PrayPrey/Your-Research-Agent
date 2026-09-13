# Phase 2A Research Discussion Log

## Briefing

**Gap ID:** GAP-1
**Gap Title:** Systematic Comparison of Verification Signal Types
**Priority:** HIGH | **Relevance:** PRIMARY

### Research Context

**Research Question:** Can execution-guided iterative refinement with formal verification feedback (type checking, static analysis, test execution) improve LLM code generation pass rates compared to single-shot generation on standard benchmarks?

**Gap Description:** Type errors (TyFlow), runtime traces (DebugRepair), static analysis (Meta APR) studied in isolation. Missing: Controlled comparison of type errors vs runtime errors vs logical errors vs static analysis on HumanEval/MBPP with same model.

**Impact:** Would establish empirical ranking of feedback signal effectiveness.

### Key Evidence from Literature

| Paper | Year | Key Insight |
|-------|------|-------------|
| How Many Tries Does It Take? | 2026 | Self-repair +4.9-17.1 pp HumanEval; Assertion errors hardest (~45%), syntax easiest |
| CodeCoR | 2025 | Multi-agent 77.13% Pass@1 |
| TyFlow | 2025 | Type constraints improve functional correctness |
| DebugRepair | 2026 | Runtime traces outperform error messages |
| Debugging Decay | 2025 | 60-80% capability loss in 2-3 attempts |

### Available Resources

**Benchmarks:** HumanEval (164 problems), MBPP (974 problems), EvalPlus (rigorous extended tests)

**Repos:** openai/human-eval, evalplus/evalplus, bigcode-evaluation-harness

### Feasibility Constraints (MANDATORY)

- MUST use existing benchmarks only (HumanEval, MBPP)
- NO new rubrics or scoring frameworks
- NO human evaluation
- NO synthetic data
- Automated pass@k evaluation only

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? The literature treats verification signals as independent sources of feedback, but what if the *order* and *combination* of signals matters more than the signals themselves?

Looking at the evidence: "How Many Tries" shows assertion errors are hardest (~45% success rate) while syntax errors are easiest. TyFlow shows type constraints help. DebugRepair shows runtime traces outperform error messages. But nobody has asked: **What if we create a verification signal *curriculum*?**

Imagine this: Instead of picking ONE signal type, we could test a *staged verification pipeline*:
1. **Stage 1:** Static analysis (cheapest, catches shallow errors)
2. **Stage 2:** Type checking (medium cost, catches interface errors)
3. **Stage 3:** Test execution with runtime traces (highest cost, catches logic errors)

The hypothesis would be: **Staged verification with early-exit on shallow errors is more cost-effective than uniform application of expensive signals.**

Cross-domain connection: This mirrors curriculum learning in neural network training - start with easy examples, progress to hard ones. Here, we start with cheap verification, progress to expensive only when needed.

Another wild idea: What if different error *categories* respond to different signal types? Syntax errors → static analysis. Type mismatches → type checker. Logic errors → runtime traces. We could build an **error-aware routing system** that selects the verification signal based on preliminary error classification.

**Key Points:**
- Staged verification curriculum (cheap-to-expensive) may beat uniform signal application
- Error category → signal type routing could improve efficiency
- The interaction between signals matters, not just individual signal effectiveness

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova raises intriguing ideas about staged verification and error-aware routing. The evidence suggests these are worth exploring, but we must be precise about what we can actually test.

Let me stress-test the "staged verification curriculum" hypothesis. The claim is that cheap-to-expensive ordering is more cost-effective. What would disprove this? If runtime traces alone achieve the same pass rate in fewer total tokens than the staged approach, the curriculum adds complexity without benefit. We need a clear falsification criterion: **Staged verification must achieve equal or higher pass@1 with measurably lower token cost than the best single-signal baseline.**

For the "error-aware routing" idea, the critical weakness is: how do we classify errors *before* applying verification? If classification requires running all signals anyway, we've gained nothing. A testable version would be: "Initial error message text alone (from first failed attempt) predicts which signal type will successfully guide repair." This is falsifiable—we can measure prediction accuracy.

The literature provides useful anchors. "How Many Tries" [2026] gives us error category difficulty: assertion errors ~45% repair rate, syntax errors highest. This implies we should stratify results by error category. "Debugging Decay" [2025] warns of 60-80% capability loss after 2-3 attempts—so we must cap iterations and measure per-attempt marginal gain.

Concrete predictions we need:
1. **P1:** Staged verification achieves pass@1 within 2% of best single-signal, with ≥20% token reduction
2. **P2:** Each signal type shows statistically significant advantage for at least one error category
3. **P3:** Per-attempt repair success decays predictably (exponential decay with rate λ ≈ 0.3-0.5)

**Key Points:**
- Falsification criterion: staged must beat single-signal on cost-effectiveness, not just match
- Error-aware routing requires a classifier that doesn't need all signals to classify
- Must stratify by error category and cap iterations (debugging decay)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: does this advance the field, or does it confirm what practitioners already assume?

🔬 Prof. Vera's predictions P1-P3 are testable, but P1 and P2 feel like engineering optimizations rather than scientific contributions. The community already knows static analysis is cheap and runtime traces are informative. Proving staged pipelines save tokens is useful for practitioners but won't reshape research directions.

What makes this genuinely new? The gap is not "which signal works best" but **why different signals have different repair success rates**. "How Many Tries" [2026] shows assertion errors are hardest—but why? Is it because:
(a) Assertion errors require semantic understanding, which error messages lack?
(b) Assertion errors produce less informative feedback text?
(c) LLMs have training data bias toward syntax/type errors?

If we can identify the *causal mechanism* behind signal effectiveness, we unlock new research questions: Can we engineer more informative error feedback? Can we augment LLMs to handle difficult error categories?

The significance test: A paper titled "Staged Verification Saves 20% Tokens" gets cited by systems papers. A paper titled "Error Semantics Explain Repair Difficulty: Implications for LLM Training" gets cited by ML researchers, benchmark designers, and future LLM developers.

I propose elevating the hypothesis: **Verification signal effectiveness is mediated by feedback informativeness, which correlates with error category. Signals that expose causal relationships (runtime traces) outperform signals that expose symptoms (error messages).**

This reframing opens new questions: What makes feedback "informative"? Can we quantify it? Does informativeness predict repair success across error categories?

**Key Points:**
- Engineering optimization (P1-P2) vs scientific contribution (understanding why)
- Core insight: signal effectiveness may be explained by feedback informativeness
- Reframe hypothesis to explain mechanism, not just measure outcomes

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. 🎯 Dr. Sage's reframing toward "feedback informativeness" is intellectually appealing, but we need to examine whether it's technically sound and immediately testable.

The mechanism proposed—that signals exposing causal relationships outperform symptom-based signals—makes intuitive sense. But here's what worries me: **How do we operationalize "informativeness" without creating a new rubric?** The feasibility constraints explicitly prohibit new scoring frameworks.

Fortunately, there's a workaround. We don't need to *define* informativeness—we can *measure* its effects. If informativeness mediates repair success, then:
1. **Richer signals should produce larger per-token repair gains** (more information per unit cost)
2. **Signal content length should correlate with repair success** (proxy for information quantity)
3. **Signals with execution state (traces) should outperform signals without (static errors)** (causal vs symptomatic)

These are observable without subjective scoring. We measure pass@k, token costs, and signal characteristics (length, presence of variable values, stack depth) directly from the data.

Is the mechanism physically possible? Yes—runtime traces literally contain more information (variable states, execution paths) than static error messages. The question is whether LLMs can *use* that information effectively. "DebugRepair" [2026] suggests yes: runtime traces outperform error messages. "TyFlow" [2025] shows type constraints (structured information) improve correctness.

Fundamental barrier check: The main risk isn't theoretical impossibility but **confounding**. Different signal types correlate with error categories (type errors → type checker, runtime errors → traces). We must control for error category to isolate signal effectiveness from error difficulty.

**Key Points:**
- Informativeness proxy: signal length, presence of execution state, causal content
- No new rubrics needed—measure observable signal properties vs repair success
- Critical confound: error category correlates with both signal type and difficulty

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and we can strengthen this by integrating the insights from all perspectives into a coherent, testable hypothesis.

⚙️ Prof. Pax's point about operationalizing informativeness without new rubrics is the key unlock. We can define **Signal Information Density (SID)** as an observable metric: *SID = (execution state variables + stack depth indicators + code location markers) / signal token length*. This is computable directly from signal text—no human judgment required.

Here's how we address the concerns raised:

🔬 Prof. Vera demanded falsification criteria. **Falsification:** If SID does not correlate with per-attempt repair success (r < 0.3) across error categories, the informativeness hypothesis fails.

🎯 Dr. Sage wanted scientific contribution beyond engineering. **Contribution:** We're not just measuring "which signal works"—we're testing *why* signals work. The hypothesis predicts that informativeness (measured by SID) is the mediating variable.

⚙️ Prof. Pax flagged the error category confound. **Control:** We stratify by error category (syntax, type, assertion, logic) and show SID predicts repair success *within* each category, not just across.

The refined hypothesis emerges:

**H-VerifSignal-v1:** Under iterative code repair with LLM feedback, if verification signals provide higher Signal Information Density (execution states, causal indicators), then repair success rates increase, because informationally richer feedback enables targeted code modifications.

**Testable Predictions:**
- **P1 (Primary):** SID correlates positively with single-attempt repair success (r > 0.3, p < 0.05) controlling for error category
- **P2:** Runtime traces (high SID) outperform error messages (low SID) on assertion errors by ≥10 percentage points
- **P3:** Type checker signals (medium SID) outperform static analysis (low SID) on type errors by ≥5 percentage points

**Key Points:**
- Signal Information Density (SID) operationalizes informativeness objectively
- Hypothesis tests mechanism (informativeness), not just outcomes (pass@k)
- Stratification by error category controls for confounding

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. 🛡️ Dr. Ally's Signal Information Density (SID) formula looks clean, but show me the evidence that counting "execution state variables + stack depth indicators + code location markers" actually captures what makes feedback useful.

The assumption is unstated: **SID assumes quantity of execution state equals quality of repair guidance.** But what if a single, precise variable value is more useful than ten irrelevant ones? A runtime trace that shows `x=None` when `x` should be a list is maximally informative in 3 tokens. A verbose trace showing 50 variable states might be *less* useful due to context window noise.

What would convince me: Show that SID predicts repair success *better than signal length alone*. If r(SID, success) ≈ r(length, success), then SID adds no explanatory power—we've just rediscovered that "more text helps."

Second concern: The 10pp and 5pp effect sizes in P2 and P3 are arbitrary. Where do they come from? "DebugRepair" [2026] showed runtime traces outperform error messages, but by how much? If the observed effect is 3pp, does the hypothesis fail? We need expected effect sizes grounded in prior work.

Third: The hypothesis predicts a *correlation* (SID with repair success), but 🎯 Dr. Sage wanted a *mechanism*. Correlation ≠ causation. What if high-SID signals simply correlate with easier errors? We'd observe the correlation without informativeness being causal.

The fix: Add a **manipulation check**. If we artificially *reduce* SID (truncate traces, remove variable values), does repair success drop proportionally? That would establish causality.

**Key Points:**
- SID assumes quantity = quality; needs validation against simple length baseline
- Effect size thresholds (10pp, 5pp) must be grounded in prior empirical results
- Correlation doesn't prove mechanism—need manipulation check (SID reduction → success drop)

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! 🔍 Prof. Rex's critique reveals the deeper question: **What property of feedback *causes* repair success?**

The manipulation check idea unlocks a creative experimental design. Instead of just observing natural SID variation, we can *engineer* signal variants:

1. **Full trace** (control): Complete runtime trace
2. **Truncated trace**: First N lines only
3. **Value-masked trace**: Execution flow preserved, variable values replaced with placeholders
4. **Structured summary**: Key variable states + assertion failure, no trace

If informativeness matters, we should see: Full > Truncated > Value-masked ≈ Structured (if structure compensates for lost values). If it's just length, we'd see: longer always better regardless of content.

This design tests the *mechanism*, not just correlation. We're manipulating informativeness while controlling length.

On the effect size concern: "How Many Tries" [2026] reports self-repair improves HumanEval by 4.9-17.1 percentage points. That's our anchor. If signal type differences are smaller than 5pp, they're within noise of model variation. So 5pp is a reasonable minimum detectable effect.

Cross-domain insight: In human learning, the "desirable difficulties" literature shows that *too much* information can hurt learning—it removes the need for active inference. What if LLMs have similar saturation? There might be an *optimal* SID range, not monotonic improvement.

**Revised P4 (new prediction):** There exists an optimal SID range (SID_opt); signals above this show diminishing returns or degraded repair success.

**Key Points:**
- Manipulation check: engineer signal variants (truncated, value-masked, structured) to test causality
- Anchor effect sizes to "How Many Tries" [2026]: 5pp minimum for meaningful differences
- New prediction: optimal SID range (too much information may hurt)

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's manipulation check design is exactly what we need for causal inference. Let me formalize the experimental protocol.

**Factorial Design for Signal Manipulation:**

| Condition | Signal Content | Length Control | SID Level |
|-----------|---------------|----------------|-----------|
| C1: Full Trace | Complete execution trace | Natural | High |
| C2: Truncated | First 10 lines of trace | Fixed | Medium |
| C3: Value-Masked | Flow preserved, values hidden | Matched to C1 | Low (content) |
| C4: Error Only | Exception message only | Minimal | Baseline |

This isolates three factors:
1. **Length** (C1 vs C2): Does more text help?
2. **Value presence** (C1 vs C3): Does execution state matter?
3. **Structure** (C3 vs C4): Does flow information help even without values?

Falsification criteria refined:
- **F1:** If C1 ≈ C2 (r > 0.9), length matters, not informativeness
- **F2:** If C1 > C3 significantly (p < 0.05), values are causal
- **F3:** If C3 > C4 significantly, structure provides independent value

On 🔭 Dr. Nova's "optimal SID" hypothesis (P4): This is testable via dose-response curve. Plot repair success vs. trace length (0, 5, 10, 20, 50, 100 lines). If non-monotonic (peak then decline), saturation confirmed.

**Confound control:** All conditions applied to same error instances. Stratify by error category. Use same base LLM (fix model variable).

**Statistical power:** "How Many Tries" [2026] shows 4.9-17.1pp effects. For 5pp minimum detectable effect with α=0.05, β=0.80, need ~n=500 problem instances. HumanEval (164) + MBPP (974) = 1138 instances—sufficient.

**Key Points:**
- Factorial design isolates length, value presence, and structure factors
- Specific falsification criteria F1-F3 for each causal claim
- Statistical power: 1138 instances sufficient for 5pp effect detection

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The experimental design has tightened significantly. Now let me assess what this contributes to the field.

🔬 Prof. Vera's factorial design answers a question the literature has ducked: **Why do different verification signals produce different repair outcomes?** Prior work (TyFlow, DebugRepair, How Many Tries) measured outcomes but didn't decompose the causal mechanism.

The contribution ladder:
1. **Replication** (low): Reproduce prior results → not novel
2. **Extension** (medium): Test on new benchmark/model → incremental
3. **Mechanism** (high): Explain *why* observed patterns occur → this work
4. **Framework** (highest): Provide generalizable theory → aspiration

Our hypothesis sits at level 3 (mechanism). We're not just showing "traces beat messages" (known)—we're testing *why* (information content vs. length vs. structure).

But for level 4 impact, we need a generalizable takeaway. Here's the framing:

**General Principle:** Feedback effectiveness for LLM self-repair is determined by *actionable specificity*—the degree to which feedback localizes the error and suggests the correction.

Actionable specificity decomposes into:
- **Localization:** Where is the bug? (file, line, variable)
- **State exposure:** What was the value? (expected vs. actual)
- **Causality:** Why did it fail? (trace shows execution path to failure)

This framework predicts which *future* feedback types will be effective (e.g., symbolic execution, formal proofs, model-based diagnostics)—not just ranking current signals.

**Key Points:**
- Contribution level: Mechanism (explaining why) > Extension (testing what)
- Generalizable framework: Actionable Specificity = Localization + State Exposure + Causality
- Predictive power: framework should generalize to novel feedback types

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🎯 Dr. Sage's "Actionable Specificity" framework is elegant, but let's verify it's technically implementable with existing tools.

**Localization:** Extracting file/line/variable from error messages is straightforward—standard parsing. ✅

**State Exposure:** Getting expected vs. actual values requires either:
- Test assertions that print both values (most frameworks do this)
- Runtime trace capture (Python's `sys.settrace` or debugger integration)

Both are technically feasible. DebugRepair [2026] already demonstrated runtime trace capture. ✅

**Causality:** This is the hard part. Execution traces show the path but don't explain *why* it's wrong. For true causality, we'd need:
- Counterfactual analysis: "If variable X had been Y, the test would pass"
- This requires symbolic execution or constraint solving

Here's what worries me: Full causality analysis (SMT solvers, symbolic execution) is computationally expensive and may not scale to 1138 problems. CoTran [2023] used compiler + symexec feedback, but for code generation, not repair.

**Feasible operationalization:** We don't need *true* causality—we need *apparent* causality to the LLM. A trace that shows `x = None` followed by `x.append() → AttributeError` provides enough context for repair without formal analysis. The LLM infers causality from context.

So we can operationalize Actionable Specificity as:
- **AS_loc:** Binary (error location provided: 1, not provided: 0)
- **AS_state:** Count of variable values exposed
- **AS_causal:** Count of execution steps between assignment and failure (proxy for trace depth)

All three are computable from signal text. No external tools required.

**Key Points:**
- Localization and State Exposure: technically straightforward
- Full causality requires symbolic execution (too expensive); use trace depth as proxy
- AS components computable from signal text—no new tools needed

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converging on something strong. Let me synthesize the refined hypothesis with all constraints addressed.

**H-VerifSignal-v1 (Refined):**

*Under LLM-based iterative code repair on HumanEval/MBPP, if verification signals provide higher Actionable Specificity (AS = Localization + State Exposure + Causal Context), then single-attempt repair success rates increase, because informationally richer feedback enables targeted code modifications.*

**Operationalization:**
- AS_loc ∈ {0, 1}: Error location (file:line) present
- AS_state ∈ [0, ∞): Count of variable values in feedback
- AS_causal ∈ [0, ∞): Execution steps (trace depth) between error and failure
- AS_total = AS_loc + log(1 + AS_state) + log(1 + AS_causal)

The log transforms handle scale differences while maintaining monotonicity.

**Experimental Design (Consolidated):**

| IV Condition | AS_loc | AS_state | AS_causal | Expected Rank |
|--------------|--------|----------|-----------|---------------|
| C1: Full Trace | 1 | High | High | 1 (best) |
| C2: Truncated Trace | 1 | Medium | Medium | 2 |
| C3: Value-Masked | 1 | 0 | High | 3 |
| C4: Error Message | 1 | Low | 0 | 4 |
| C5: Static Analysis | 0 | 0 | 0 | 5 (worst) |

**Predictions (Testable):**
- **P1 (Primary):** AS_total correlates with repair success (r > 0.3, p < 0.05) controlling for error category
- **P2:** C1 > C4 by ≥5 percentage points on assertion errors
- **P3:** C3 > C5 by ≥5 percentage points (structure without values beats no structure)
- **P4:** Non-monotonic dose-response: optimal trace length exists (peak at ~20-50 lines)

**Null Hypothesis (H0):** Repair success is independent of AS; only error category determines outcomes.

**Key Points:**
- AS_total formula provides computable, objective metric
- 5-condition factorial design tests all components
- Predictions grounded in prior literature effect sizes (5pp minimum)

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis has tightened, but I still see gaps. Let me stress-test the AS formula and experimental design.

**Issue 1: AS_total weighting is arbitrary.** Why log transforms? Why equal weights for loc, state, and causal? If localization is more important than state exposure, AS_total misweights components. What would convince me: Run a preliminary regression with AS_loc, AS_state, AS_causal as separate predictors. If coefficients differ significantly (β_loc >> β_state), the combined formula is wrong.

**Issue 2: C5 (Static Analysis) is a strawman.** Static analysis tools (mypy, pylint, flake8) *do* provide localization (file:line). Your table shows AS_loc = 0 for C5—that's incorrect. Pylint says `file.py:42: E1101 Instance has no 'foo' member`. That's localization + partial state.

Revised C5 should be: AS_loc = 1, AS_state = Low (type info, no runtime values), AS_causal = 0.

This changes the prediction: C4 (error message) vs C5 (static analysis) may be closer than expected. If both have localization but differ in state exposure, the comparison isolates AS_state's contribution.

**Issue 3: "Debugging Decay" [2025] warns of 60-80% capability loss after 2-3 attempts.** Your design assumes single-attempt repair. If you measure only first-attempt success, you miss the decay dynamics. But if you allow multiple attempts, confounds multiply (does the LLM learn from prior attempts?).

Recommendation: Measure both single-attempt *and* multi-attempt (capped at 3) success, report separately.

**Key Points:**
- AS formula weights need empirical validation (separate regression first)
- C5 (static analysis) DOES provide localization—fix the table
- Include multi-attempt analysis to address debugging decay dynamics

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex's corrections are well-taken. The static analysis strawman was sloppy—let me fix and expand.

**Revised Condition Table:**

| Condition | Description | AS_loc | AS_state | AS_causal |
|-----------|-------------|--------|----------|-----------|
| C1 | Full runtime trace | 1 | High (~10-50 vars) | High (~20-100 steps) |
| C2 | Truncated trace (10 lines) | 1 | Medium (~5 vars) | Medium (~10 steps) |
| C3 | Value-masked trace | 1 | 0 | High |
| C4 | Runtime error message | 1 | Low (~1-3 vars) | 0 |
| C5 | Static analysis (mypy/pylint) | 1 | Low (~1 type) | 0 |
| C6 | Syntax error only | 1 | 0 | 0 |

Adding C6 (syntax error baseline) completes the spectrum. Syntax errors provide localization but zero state/causal info—the theoretical minimum.

**On AS weighting:** What if we flip the problem? Instead of prescribing weights, we *learn* them from data:

`Repair_Success ~ β0 + β_loc × AS_loc + β_state × log(1+AS_state) + β_causal × log(1+AS_causal) + ε`

The regression coefficients become the empirical weights. If β_causal >> β_state, causal context matters more than state exposure. This is now a *finding*, not an assumption.

**Novelty implication:** The learned weights become the paper's main contribution—a quantified ranking of feedback components for LLM code repair. No prior work has decomposed feedback effectiveness this way.

**On multi-attempt analysis:** Here's a creative framing. Treat attempts as a *survival analysis* problem. Model time-to-success (or censored if max attempts reached) as a function of AS. Cox regression handles this naturally and reveals whether AS affects *speed* of repair, not just eventual success.

**Key Points:**
- Added C6 (syntax error baseline) for complete spectrum
- Learn AS weights empirically via regression—weights become findings
- Survival analysis for multi-attempt dynamics (Cox regression)

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

The methodology has matured significantly. Let me formalize the final experimental protocol and verify all testability requirements.

**Primary Analysis (Single-Attempt):**

Model: `logit(P(success)) = β0 + β_loc × AS_loc + β_state × log(1+AS_state) + β_causal × log(1+AS_causal) + γ_cat × error_category`

- Outcome: Binary (repair success/failure on first attempt)
- Fixed effects: AS components + error category (4 levels: syntax, type, runtime, logic)
- Random effects: Problem ID (accounts for problem difficulty)
- Method: Mixed-effects logistic regression

**Secondary Analysis (Multi-Attempt Survival):**

Model: Cox proportional hazards with AS components as covariates
- Event: Successful repair
- Censoring: Max 3 attempts without success
- Outcome: Hazard ratio per AS component

**Statistical Tests:**

| Hypothesis | Test | Success Criterion |
|------------|------|-------------------|
| P1: AS predicts success | Likelihood ratio test | p < 0.05 for full model vs. error-category-only |
| P2: C1 > C4 on assertions | Two-proportion z-test | Δ ≥ 5pp, p < 0.05 |
| P3: C3 > C6 | Two-proportion z-test | Δ ≥ 5pp, p < 0.05 |
| P4: Non-monotonic dose | Quadratic term test | β_AS² < 0, p < 0.05 |

**Sample Size Verification:**
- HumanEval: 164 problems × 6 conditions = 984 trials
- MBPP subset: 500 problems × 6 conditions = 3000 trials
- Total: ~4000 trials, well-powered for effect sizes ≥ 3pp

**Reproducibility:** Single LLM (GPT-4 or Claude 3.5), temperature=0, fixed random seed. All code on GitHub with Docker environment.

**Key Points:**
- Mixed-effects logistic regression for primary analysis (accounts for problem difficulty)
- Cox survival model for multi-attempt dynamics
- 4000+ trials: well-powered for small effect sizes

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

We've reached a well-formed hypothesis. Let me assess final contribution and position the work.

**Contribution Assessment:**

| Dimension | Prior Work | This Work | Delta |
|-----------|-----------|-----------|-------|
| What | "Traces beat messages" | Why traces beat messages | Mechanism |
| How | Ad-hoc signal selection | Principled AS framework | Theory |
| Scope | Single signal studies | 6-condition factorial | Systematic |
| Outcome | pass@k only | Regression coefficients | Quantified |

**Paper Positioning:**

Title candidate: *"Actionable Specificity: Decomposing Feedback Effectiveness for LLM Code Repair"*

Venue fit: ICSE/FSE (SE + ML), NeurIPS (ML methodology), or VerifAI workshop (formal methods + LLM)

**Key Claims for Abstract:**
1. We introduce Actionable Specificity (AS), a framework decomposing verification feedback into localization, state exposure, and causal context
2. On HumanEval+MBPP, runtime traces (high AS) improve repair success by Xpp over error messages (low AS)
3. We find causal context (β_causal) contributes more than state exposure (β_state) to repair success
4. Optimal trace length exists (~Y lines); longer traces show diminishing returns

**Broader Impact:**
- For researchers: Framework generalizes to new feedback types (symbolic execution, formal proofs)
- For practitioners: Guidance on which signals to prioritize for cost-effective repair
- For benchmark designers: Metrics for feedback quality in evaluation

The hypothesis is ready for Phase 2B formalization.

**Key Points:**
- Contribution: Mechanism-level explanation for feedback effectiveness
- Novel framework (AS) with empirical quantification
- Ready for Phase 2B: hypotheses, variables, predictions all specified

---

### Exchange 16

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility verification before we converge.

**Technical Feasibility Checklist:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Benchmark availability | ✅ | HumanEval, MBPP, EvalPlus public |
| Signal generation | ✅ | Python trace module, pytest output |
| AS computation | ✅ | Regex parsing on signal text |
| Statistical analysis | ✅ | statsmodels, lifelines packages |
| LLM API access | ✅ | OpenAI/Anthropic APIs |
| Compute requirements | ✅ | ~4000 API calls, ~$50-100 at current rates |

**Implementation Plan:**

1. **Data Pipeline:** HumanEval/MBPP → generate initial code → run tests → capture signals (6 variants) → store in structured format
2. **Signal Manipulation:** Python scripts to generate C1-C6 variants from full trace
3. **Repair Loop:** Single LLM call per condition per problem, temperature=0
4. **Analysis:** Logistic regression + Cox survival in Python

**No Fundamental Barriers:** Every component uses existing, publicly available tools. The novel contribution is the experimental design and analysis, not new infrastructure.

**Scope Calibration:**
- Full HumanEval (164) + MBPP subset (500) = 664 problems × 6 conditions = ~4000 trials
- Estimated: 2-3 days of compute, $50-100 API cost
- Timeline: 2 weeks for implementation + experiments + analysis

Okay, this could work.

**Key Points:**
- All components technically feasible with existing tools
- Estimated cost: $50-100, 2-3 days compute
- No fundamental barriers identified

---

### Exchange 17

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've achieved convergence across all dimensions. Let me synthesize the final hypothesis.

**FINAL HYPOTHESIS: H-ActionableSpec-v1**

*Under LLM-based iterative code repair on standard benchmarks (HumanEval, MBPP), if verification signals provide higher Actionable Specificity—decomposed into Localization (AS_loc), State Exposure (AS_state), and Causal Context (AS_causal)—then single-attempt repair success rates increase, because informationally richer feedback enables the model to localize bugs and infer correct fixes.*

**Mechanism:**
1. Verification signal is generated from failed test execution
2. Signal exposes error location, variable states, and execution path
3. LLM processes signal to identify bug location and infer correction
4. Higher AS → more precise localization → higher repair success

**Variables:**
- **IV:** Verification signal type (6 conditions: C1-C6)
- **DV (primary):** Single-attempt repair success (binary)
- **DV (secondary):** Multi-attempt time-to-success
- **Controlled:** Error category, problem difficulty, LLM model, temperature

**Predictions:**
- **P1 (Primary):** AS components predict repair success (β > 0, p < 0.05) controlling for error category
- **P2:** Full trace (C1) outperforms error message (C4) by ≥5pp on assertion errors
- **P3:** Value-masked trace (C3) outperforms syntax baseline (C6) by ≥5pp
- **P4:** Optimal trace length exists (quadratic term significant, peak ~20-50 lines)

**Null Hypothesis (H0):** Repair success is determined solely by error category; AS components have no predictive power (β_loc = β_state = β_causal = 0).

**Novelty:** First systematic decomposition of feedback effectiveness into measurable components with empirical quantification of relative importance.

**Key Points:**
- Complete hypothesis with mechanism, variables, and testable predictions
- Null hypothesis clearly specified for falsification
- All criteria for convergence met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis introduces a genuinely novel framework—Actionable Specificity (AS)—that decomposes feedback effectiveness into measurable components. This goes beyond prior work (TyFlow, DebugRepair) that measured outcomes without explaining mechanisms. The cross-domain connection to curriculum learning and the insight about optimal trace length add theoretical depth.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously testable. Clear falsification criteria exist: if AS components don't predict repair success (β ≈ 0, p > 0.05), the hypothesis fails. The 6-condition factorial design with statistical power analysis (4000+ trials) ensures meaningful effect detection. Specific effect size thresholds (≥5pp) are grounded in prior literature.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work contributes at the mechanism level—explaining *why* different signals work, not just *which* ones work. The learned regression coefficients become actionable guidance for practitioners and researchers. The framework generalizes beyond current signals to predict effectiveness of future feedback types.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically implementable with existing tools (HumanEval/MBPP benchmarks, Python trace module, standard statistical packages). No fundamental barriers. Estimated 2-3 days compute, $50-100 API cost. The scope is well-calibrated for a single-paper contribution.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The panel has converged on **H-ActionableSpec-v1**: a hypothesis stating that verification signal effectiveness in LLM code repair is mediated by Actionable Specificity, decomposed into Localization, State Exposure, and Causal Context.

The core claim is that informationally richer feedback (higher AS) enables more targeted bug fixes, leading to higher repair success rates. This is tested via a 6-condition factorial design comparing full traces, truncated traces, value-masked traces, error messages, static analysis, and syntax errors.

Key predictions include: (P1) AS components correlate with repair success controlling for error category, (P2) full traces outperform error messages by ≥5pp on assertion errors, (P3) structure helps even without values, and (P4) optimal trace length exists.

The experimental design uses mixed-effects logistic regression for single-attempt analysis and Cox survival models for multi-attempt dynamics. Statistical power is sufficient for detecting 3pp effects.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** AS component weighting is determined empirically, not prescribed—this is a feature (findings) not a bug, but results may be model-specific (GPT-4 vs Claude).
- **Concern 2:** The "optimal trace length" prediction (P4) adds complexity; if not observed, doesn't invalidate core hypothesis but weakens theoretical elegance.
- **Mitigation Strategy:** Report model-specific coefficients, acknowledge generalization limits. Treat P4 as exploratory, not confirmatory.

---


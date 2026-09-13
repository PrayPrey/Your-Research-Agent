# Phase 2A Discussion Log
**Gap:** SA-Correctness Correlation Quantification
**Status:** In Progress
**Date:** 2026-08-24

---

## Discussion Briefing

### Selected Research Gap
**Gap 1: SA-Correctness Correlation Quantification**
- **Priority:** PRIMARY (Critical)
- **Connection:** Blocks answering research question - need quantitative correlation data

**Current State:** Existing work shows SA feedback *improves* code quality iteratively (Blyth 2025: 40%→13% security issues), but does not quantify predictive correlation between SA metrics and functional correctness.

**Missing Piece:** Systematic study measuring correlation coefficients (r, R²) between specific SA metrics (pylint score, mypy error count, complexity) and pass@k on HumanEval/MBPP across multiple LLMs.

### Key Papers
1. **Static Analysis as a Feedback Loop** (Blyth 2025) - Shows SA improves quality but lacks correlation analysis
2. **CodeQUEST** (Liu 2025) - Uses Pylint/Radon/Bandit; shows "meaningful correlation" but not quantified
3. **EvalPlus** (Liu 2023) - HumanEval+ with 80x more tests; benchmark standard

### Research Question
Can static analysis tool outputs (error counts, warning types, type coverage) predict functional correctness of LLM-generated code on existing benchmarks (HumanEval, MBPP)?

### Feasibility Constraints
- Must use existing benchmarks (HumanEval, MBPP, EvalPlus)
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic data or human evaluation required

---

## Discussion Rounds

### Round 1: Opening Perspectives

🔭 **Dr. Nova** (Creative Novelty Explorer):

The literature gap here is fascinating - everyone uses SA tools iteratively but nobody has asked the fundamental predictive question! What if SA metrics are actually BETTER predictors than we assume? 

Consider: if pylint score correlates with pass@k at r > 0.6, we could skip expensive test execution entirely for rejection sampling. That's a paradigm shift from "SA improves code" to "SA predicts correctness."

Cross-domain insight: In medical diagnostics, cheap screening tests with moderate correlation to disease presence are HUGELY valuable - same logic applies here. Even r = 0.4 would be actionable.

**Key Points:**
- Novel angle: predictive power of SA, not just iterative improvement
- Cross-domain: cheap screening tests are valuable even at moderate correlation
- Paradigm shift potential: SA as correctness predictor, not just quality improver

---

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me ground this in testable terms. The hypothesis must specify:

1. **Which SA metrics?** Pylint score (0-10), mypy error count, Radon cyclomatic complexity, Bandit vulnerability count - these are measurable
2. **What correlation threshold matters?** r > 0.3 (weak), r > 0.5 (moderate), r > 0.7 (strong)
3. **What dataset?** HumanEval (164 problems) × k generations per problem × n LLMs

The null hypothesis would be: "SA metrics have no correlation with pass@k (r ≈ 0)." This is clearly falsifiable.

What would disprove the hypothesis? If across 4+ LLMs and 1000+ code samples, no SA metric achieves r > 0.3 with binary pass/fail, we'd conclude SA metrics are not useful predictors.

**Key Points:**
- Operationalize: specific metrics (pylint, mypy, radon, bandit)
- Define success: r > 0.3 minimum for actionable correlation
- Sample size: ~164 × 100 × 4 = 65,600 code samples feasible

---

🎯 **Dr. Sage** (Research Impact Evaluator):

The contribution question: what makes this more than a measurement exercise?

If we show r > 0.5 between SA metrics and pass@k:
1. **Immediate application:** SA-based rejection sampling at inference time - no LLM calls needed
2. **Theoretical contribution:** First quantified relationship between static properties and dynamic correctness
3. **Opens new questions:** Which SA dimensions matter most? Does correlation transfer across models?

The field impact is HIGH because:
- Current practice: run tests to evaluate code (expensive)
- This enables: pre-filter without execution (cheap)
- Novelty: predictive use of SA vs iterative repair use

This matters because it changes the cost calculus of LLM code generation.

**Key Points:**
- Beyond measurement: enables new application (rejection sampling without tests)
- Theoretical first: quantified static-dynamic relationship
- Practical impact: changes cost calculus of code generation

---

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Technical feasibility assessment:

**Can this work in principle?**
- ✅ SA tools (pylint, mypy, bandit, radon) produce numeric outputs
- ✅ HumanEval/MBPP provide ground truth (pass@k)
- ✅ Multiple LLMs available for cross-model analysis
- ✅ No new frameworks needed - correlation computation is standard statistics

**Theoretical validity of measurement:**
- Pylint score: composite metric (0-10), well-defined
- Mypy errors: count, type coverage percentage
- Radon: cyclomatic complexity (McCabe number)
- Pass@k: unbiased estimator per EvalPlus methodology

**Potential barriers (non-budgetary):**
- SA tools may timeout on malformed code - need error handling
- Some generated code may not parse at all - treat as "maximum error"
- Different SA tools may correlate differently with correctness

**Verdict:** Technically sound. The mechanism (correlate static metrics with execution results) is mathematically valid.

**Key Points:**
- All components exist and produce numeric outputs
- Measurement validity established (standard tools, standard benchmarks)
- No fundamental barriers - only engineering considerations

---

### Round 2: Refining the Hypothesis

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on the perspectives, let me synthesize and strengthen:

**Core Hypothesis:**
"Static analysis metrics (pylint score, mypy error count, radon complexity) exhibit moderate-to-strong correlation (r ≥ 0.4) with functional correctness (pass@1) on HumanEval/MBPP for LLM-generated code."

**Strengthening via evidence:**
- CodeQUEST (2025) reported "meaningful correlation" - suggests r > 0.3 exists
- Blyth (2025) showed SA feedback improves outcomes - implies SA signals quality
- If SA had zero predictive power, iterative SA feedback would be random

**Refinements from concerns:**
- Include ensemble metrics (combined SA score) alongside individual
- Test on 3+ LLMs to establish generality
- Use both pass@1 (strict) and pass@10 (lenient) to understand threshold effects

**Key Points:**
- Synthesized hypothesis with r ≥ 0.4 threshold
- Prior work suggests correlation exists (CodeQUEST, Blyth)
- Added ensemble and multi-model testing for robustness

---

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Critical challenges to address:

**1. Confounding variables:**
- Code LENGTH correlates with both SA metrics and failure probability
- Must control for code length (partial correlation or stratified analysis)

**2. Distribution issues:**
- SA metrics may be highly skewed (most code has low errors)
- Use Spearman rank correlation alongside Pearson

**3. Binary vs continuous:**
- pass@k is binary (pass/fail), SA metrics continuous
- Point-biserial correlation or logistic regression more appropriate

**4. What if correlation is domain-specific?**
- String manipulation vs algorithm problems may differ
- Need per-category analysis

**What would convince me:** Show r > 0.4 AFTER controlling for code length, using appropriate statistical method (point-biserial), across 3+ LLMs, with per-domain breakdown.

**Key Points:**
- Must control for code length confound
- Use point-biserial correlation for binary outcome
- Require per-domain analysis (string vs algorithm)
- Success criterion: r > 0.4 after confound control

---

### Round 3: Convergence

🔭 **Dr. Nova:**
Prof. Rex raises the code length confound - excellent catch. The NOVEL contribution becomes: "First study to isolate SA-correctness relationship controlling for length." That strengthens novelty claim.

🔬 **Prof. Vera:**
Concrete prediction: "For HumanEval using GPT-4 outputs, pylint score will show point-biserial r > 0.35 with pass@1, controlling for code length via partial correlation." This is falsifiable.

🎯 **Dr. Sage:**
The contribution is clear: if the correlation holds after controlling for confounds, SA-based rejection sampling becomes a validated technique. If it fails, we've ruled out a popular assumption.

⚙️ **Prof. Pax:**
Technically, point-biserial correlation and partial correlation controlling for length are standard scipy operations. No feasibility concerns.

🛡️ **Dr. Ally:**
Consensus forming. The hypothesis stands strengthened by confound controls and appropriate statistics.

🔍 **Prof. Rex:**
Satisfied with the refinements. The hypothesis now addresses my concerns about confounds and statistical validity.

---

## Emerged Hypothesis Summary

### Core Statement
Static analysis metrics (pylint score, mypy error count, radon cyclomatic complexity) exhibit moderate positive correlation (point-biserial r ≥ 0.35) with functional correctness (pass@1) on HumanEval/MBPP for LLM-generated code, after controlling for code length as a confounding variable.

### Causal Mechanism
1. LLM generates code with varying quality
2. SA tools detect patterns (style violations, type errors, complexity) that statistically co-occur with logical errors
3. Code with fewer SA issues is more likely to pass functional tests
4. This relationship is independent of code length

### Variables
**Independent Variables:**
- Pylint score (0-10 scale)
- Mypy error count
- Mypy type coverage percentage
- Radon cyclomatic complexity

**Dependent Variable:**
- Binary pass/fail on test execution (pass@1)

**Control Variable:**
- Code length (lines of code, tokens)

### Key Assumptions
1. SA tools produce consistent, reproducible outputs
2. HumanEval/MBPP tests are valid proxies for functional correctness
3. SA pattern detection has some semantic relationship to code quality
4. Code length is the primary confounding variable

### Null Hypothesis
H0: After controlling for code length, no SA metric shows significant correlation (r > 0.35) with pass@1 across LLMs.

### Predictions
1. **Primary:** Point-biserial correlation between pylint score and pass@1 will be r ≥ 0.35 (p < 0.05) controlling for code length
2. **Secondary:** Ensemble SA score (weighted combination) will achieve higher correlation than any single metric
3. **Tertiary:** Correlation will generalize across 3+ LLMs (GPT-4, Claude, Llama) with r variance < 0.15

### Novelty
- First quantified correlation study between SA metrics and functional correctness
- First to control for code length confound
- First to test cross-model generalization of SA predictiveness

### Scope & Boundaries
**In Scope:**
- HumanEval (164 problems), MBPP (399 problems)
- Python code only
- 3-4 LLMs (GPT-4, Claude-3, Llama-70B, Codestral)
- Standard SA tools (pylint, mypy, radon, bandit)

**Out of Scope:**
- Other languages
- Repository-level code
- Custom SA rules
- Semantic similarity metrics

### Experimental Setup
1. Generate k=100 completions per problem per LLM
2. Run SA tools on each completion
3. Run EvalPlus test suite for ground truth
4. Compute point-biserial correlations controlling for length
5. Report per-metric, per-LLM, and per-domain breakdowns

### Related Work & Baselines
- **Blyth 2025:** Iterative SA feedback (comparison: our prediction vs their correction)
- **CodeQUEST 2025:** Reported "meaningful correlation" (quantify their claim)
- **Random baseline:** No correlation (r ≈ 0)

### Phase 2B Readiness Seeds
1. Need to define exact ensemble weighting strategy
2. Need to specify statistical power analysis for sample size
3. Need to decide threshold for "actionable" correlation

### Established Facts
- SA tools (pylint, mypy, radon, bandit) are well-defined and available
- HumanEval/MBPP have standardized test harnesses (EvalPlus)
- Point-biserial correlation is appropriate for binary-continuous relationships
- Prior work suggests correlation exists but hasn't quantified it

---

## Final Assessments

### 🔭 Dr. Nova (Creative Novelty Explorer)
**Assessment:** SUPPORT
**Confidence:** 85%
**Rationale:** This fills a genuine gap - everyone assumes SA correlates with correctness but nobody measured it. The predictive framing (vs iterative) is novel and actionable.

### 🔬 Prof. Vera (Rigorous Validation Architect)
**Assessment:** SUPPORT
**Confidence:** 90%
**Rationale:** The hypothesis is falsifiable, the statistics are appropriate, and the sample sizes are adequate. The confound control addresses my main concern.

### 🎯 Dr. Sage (Research Impact Evaluator)
**Assessment:** SUPPORT
**Confidence:** 80%
**Rationale:** Clear contribution to the field. Win-win: positive results enable rejection sampling, negative results debunk a common assumption.

### ⚙️ Prof. Pax (Feasibility & Reality Checker)
**Assessment:** SUPPORT
**Confidence:** 95%
**Rationale:** All components are standard, no fundamental barriers. This is straightforwardly executable with existing tools and benchmarks.

### 🛡️ Dr. Ally (Hypothesis Strengthening Champion)
**Assessment:** STRONG SUPPORT
**Confidence:** 88%
**Rationale:** The refinements made during discussion strengthened the hypothesis significantly. The confound controls and statistical choices are sound.

### 🔍 Prof. Rex (Hypothesis Stress-Test Master)
**Assessment:** CONDITIONAL SUPPORT
**Confidence:** 75%
**Rationale:** Concerns addressed, but success depends on effect size. If r < 0.35 after length control, the result is negative but still publishable.

---

**Consensus:** All 6 personas SUPPORT proceeding to Phase 2B.
**Average Confidence:** 85.5%
**Discussion Status:** CONVERGED

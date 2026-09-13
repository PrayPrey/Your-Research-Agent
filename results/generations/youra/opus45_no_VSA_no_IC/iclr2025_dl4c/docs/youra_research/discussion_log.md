# Phase 2A Research Discussion Log

**Date:** 2026-08-24
**Gap ID:** gap1-judge-execution-correlation
**Gap Title:** Quantified Judge-Execution Correlation Across Model Scales
**Architecture:** Self-Contained Tikitaka Loop (INLINE Self-Play)
**Execution Mode:** UNATTENDED

---

## Research Briefing

### Selected Research Gap

**Gap 1: Quantified Judge-Execution Correlation Across Model Scales**

**Relevance:** PRIMARY (HIGH priority)
**Connection to Research Question:** Directly addresses "how does judge model scale affect agreement with execution ground truth"

**Current State:** 
- Naik (2024) shows CodeBERTScore has only 0.16 correlation with functional correctness
- Crupi et al. (2025) find even GPT-4-turbo "frequently misjudges"
- No systematic comparison across model scales (7B/70B/proprietary) on identical benchmarks

**Missing Piece:** Head-to-head judge accuracy comparison across model scales on same benchmark (HumanEval+/MBPP+) with execution ground truth.

**Potential Impact:** HIGH - Determines whether larger judges reliably improve correctness assessment or if scaling has diminishing returns.

### Key Papers

1. **Naik (2024)** - "On Limitations of Embedding Methods for Functional Correctness"
   - CodeBERTScore correlation: 0.16 with correctness, 0.72 with editing effort
   - Critical finding: weak correlation despite semantic similarity
   
2. **Moon et al. (2025)** - "Don't Judge Code by Its Cover"
   - 6 bias types in LLM code judges: variable names, comments, formatting
   - Judges influenced by superficial code features
   
3. **Wang et al. (2025)** - "MCTS-Judge"
   - MCTS-based System-2 thinking improves accuracy 41%→80%
   - Demonstrates test-time scaling helps
   
4. **Crupi et al. (2025)** - "On Effectiveness of LLM-as-Judge for Code"
   - GPT-4-turbo best but "frequently misjudges"
   - 8 LLMs tested on Java + Python methods
   
5. **Liu et al. (2023)** - "EvalPlus"
   - HumanEval+ with 80x more test cases
   - Pass@k drops 19-29% with rigorous testing

### Available Implementations

- **evalplus/evalplus** (1.8K stars): Execution ground truth
- **neulab/code-bert-score** (210 stars): Model-based metric
- **hongcha0/CodeJudgeBench** (9 stars): LLM judge benchmark

### Feasibility Constraints (Pipeline-Enforced)

- MUST use existing real datasets (HumanEval, MBPP, HumanEval+, MBPP+)
- MUST use existing benchmarks and metrics (pass@k, agreement rate)
- CANNOT require new benchmarks, rubrics, or scoring frameworks
- CANNOT require synthetic/generated data or human evaluation
- Hypothesis MUST be testable immediately with available resources

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from a completely different angle? Everyone's been treating judge-execution agreement as a single number to optimize, but I think we're missing something fundamental here!

Looking at the evidence, Naik (2024) shows CodeBERTScore correlates 0.72 with *editing effort* but only 0.16 with functional correctness. This is fascinating! The model isn't failing at understanding code - it's measuring something *different* than correctness. What if we could exploit this gap?

Here's my wild idea: **What if judge-execution disagreement isn't noise - it's signal?** Cases where a large judge says "correct" but execution fails might represent a specific failure mode worth characterizing. Similarly, cases where execution passes but a judge says "incorrect" might indicate superficially correct code that a human would reject (poor style, unclear logic, potential bugs in edge cases not covered by tests).

The MCTS-Judge work (Wang 2025) showing 41%→80% improvement with decomposition hints at something: judges fail systematically, not randomly. If we can characterize *when* different model scales fail differently, we might discover that:

1. Small models (7B) fail on semantic complexity - they miss subtle logic
2. Large models (70B) fail on superficial similarity - they're fooled by "looks correct"
3. Proprietary models fail on domain-specific idioms - they're trained on generic code

What paradigm shift could emerge? Instead of one judge, what about **scale-aware judge ensembles** where we use different scales for different code properties? Or even better - what if the *disagreement pattern* between scales becomes the evaluation signal?

**Key Points:**
- Judge-execution disagreement may be informative signal, not just noise
- Different model scales likely fail on different code properties
- Cross-scale disagreement patterns could be more informative than single-scale agreement

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, while your enthusiasm is compelling, we need to ground these ideas in testable predictions. Let me stress-test this hypothesis framework.

First, the core claim needs to be falsifiable. You propose "different model scales fail on different code properties." What would *disprove* this? If we test 7B, 70B, and GPT-4 judges on HumanEval+ and find their error patterns are statistically indistinguishable - same problems, same types of mistakes - then your hypothesis fails. That's our null hypothesis.

Let me propose a rigorous experimental design:

**Independent Variable:** Judge model scale (7B, 70B, proprietary)
**Dependent Variable:** Agreement with execution ground truth (binary: judge_correct == execution_pass)
**Controlled Variables:** 
- Same evaluation prompt (zero-shot correctness judgment)
- Same benchmark (HumanEval+)
- Same temperature (0 for reproducibility)

**Testable Predictions:**

P1: Judge-execution agreement increases with model scale BUT with diminishing returns
- Success criterion: 7B < 70B < proprietary, with (70B - 7B) > (proprietary - 70B)
- Falsification: Proprietary shows >20% improvement over 70B (linear scaling holds)

P2: Error types cluster by model scale
- Success criterion: Chi-square test shows significant association between scale and error type (p < 0.05)
- Falsification: Error types uniformly distributed across scales (p > 0.10)

P3: Scale-ensemble outperforms best single scale
- Success criterion: Majority vote of {7B, 70B, proprietary} achieves higher accuracy than proprietary alone
- Falsification: Ensemble accuracy ≤ proprietary accuracy + 2% margin

For P2, I propose categorizing errors using the Moon et al. (2025) bias types: (1) semantic correctness failures, (2) superficial feature confusion, (3) edge case blindness.

**Key Points:**
- Null hypothesis: Scale differences in error patterns are not significant
- Three specific predictions with quantified success/failure criteria
- Ensemble prediction (P3) directly tests Dr. Nova's cross-scale idea

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess whether this research direction truly advances the field or represents incremental work.

The question we must ask is: *What makes this genuinely new vs. what's already been done?*

Looking at the evidence, Crupi et al. (2025) tested 8 LLMs, and Wang et al. (2025) showed MCTS improves single-model accuracy. But here's what's missing - and why this matters:

**What's Genuinely New:**
1. No existing work provides *scale-controlled* comparison with execution ground truth. Crupi tested different models but not systematically across the 7B→70B→proprietary spectrum.
2. The *error characterization* angle is novel. Papers identify that judges fail, but don't characterize *how* failures differ by scale.
3. The *ensemble insight* - using scale disagreement as signal - hasn't been tested.

**Why the Community Should Care:**
- If scaling judges shows diminishing returns (P1), teams shouldn't waste API costs on proprietary judges
- If error types cluster by scale (P2), we can build targeted detection systems
- If ensembles work (P3), this provides a practical improvement path

**State-of-the-Art Positioning:**
Current SOTA (MCTS-Judge) achieves 80% accuracy with expensive test-time compute. If a simple 3-scale ensemble matches or exceeds this without MCTS, that's significant.

**New Research Directions This Opens:**
1. Scale-aware evaluation protocols for code generation leaderboards
2. Efficient judge selection based on code property analysis
3. Disagreement-as-signal for identifying borderline code quality

However, I have a concern about scope. Prof. Vera's P3 (ensemble prediction) is the most impactful, but it risks being seen as engineering optimization rather than scientific insight. We need to connect P1 and P2 to P3 - show that understanding *why* scales differ (P2) enables *better* ensembles (P3).

**Key Points:**
- Novel contribution: first scale-controlled judge-execution analysis with error characterization
- Community impact: practical guidance for judge selection and ensemble design
- Need to connect scientific insight (P1, P2) to practical contribution (P3)

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical feasibility. Not costs - but whether the proposed mechanisms are sound.

**Technical Feasibility Assessment:**

The proposed experiment is technically straightforward:
- HumanEval+ is available (evalplus repo, 1.8K stars)
- 7B models: DeepSeek-Coder-7B, CodeLlama-7B - publicly available
- 70B models: CodeLlama-70B, DeepSeek-Coder-33B (proxy for larger scale) - available via API
- Proprietary: GPT-4, Claude - standard API access

The measurement approach is theoretically valid:
- Binary agreement (judge_correct == execution_pass) is unambiguous
- HumanEval+ provides execution ground truth with 80x test coverage
- Chi-square for error type clustering is standard statistical method

**However, here's what worries me:**

1. **Error categorization validity**: Moon et al. (2025) defined 6 bias types for *code variations*, not *error types*. We need a principled error taxonomy. I propose:
   - Type A: False Negative (judge says wrong, execution passes)
   - Type B: False Positive (judge says correct, execution fails)
   - Sub-categorize by code property: logic error, edge case, syntax, type error

2. **Confounding factor**: Prompt sensitivity. If we use different prompts, results aren't comparable. The hypothesis must fix the evaluation prompt and only vary the model.

3. **Sample size**: HumanEval+ has ~160 problems × ~80 tests = ~12,800 test cases. For chi-square with 3 scales × 4 error types = 12 cells, we need ~300+ errors per scale for power. This is achievable only if error rates are >2.3%.

**Mechanism Soundness:**
The core mechanism - "larger models have different attention patterns leading to different error types" - is plausible based on scaling literature. But we're not testing the mechanism, we're testing the *observable consequence* (error pattern differences). This is appropriate for a first study.

**Key Points:**
- Technically feasible with available resources (EvalPlus, public/API models)
- Need principled error taxonomy beyond Moon et al.'s bias types
- Must control for prompt sensitivity as confound
- Sample size should be sufficient for statistical power

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent discussion! Let me synthesize and strengthen the emerging hypothesis based on the concerns raised.

**Addressing Prof. Pax's Error Taxonomy Concern:**

YES, AND we can strengthen this by using a simpler, more robust taxonomy:
- **False Positive (FP)**: Judge says correct, execution fails
- **False Negative (FN)**: Judge says incorrect, execution passes

This is unambiguous and doesn't require subjective categorization. For deeper analysis, we can sub-categorize FPs by *what the execution error was* (assertion failure vs. runtime error vs. timeout) - this is objective and comes from the test harness.

**Strengthening Prof. Vera's Predictions:**

P1 (diminishing returns) needs a baseline. Current best single-judge (MCTS-Judge) achieves 80%. If our proprietary judge (without MCTS) achieves ~70%, then:
- 7B target: 50-55% (baseline)
- 70B target: 60-65%
- Proprietary target: 68-72%

This gives concrete numbers to falsify against.

**Bridging Dr. Sage's Insight-to-Impact Gap:**

The connection between P1/P2 (scientific insight) and P3 (practical contribution) can be made explicit:

*If P2 shows error types cluster by scale, then P3's ensemble works because it combines complementary error detectors.*

This makes the ensemble not just "try everything" but "principled combination of complementary judges."

**Refined Core Hypothesis:**

"Under code correctness evaluation settings, if we vary judge model scale (7B/70B/proprietary), then judge-execution agreement increases with scale BUT different scales exhibit systematically different error patterns (FP/FN ratios), because larger models develop different attention biases during training on code corpora."

**Key Points:**
- Simplified error taxonomy: FP/FN (objective, from test harness)
- Added concrete accuracy targets for P1
- Connected P2 (error clustering) to P3 (ensemble design) mechanistically

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me find every flaw before reviewers do.

**Flaw 1: The "different attention biases" mechanism is untestable**

The hypothesis claims "larger models develop different attention biases during training." We're NOT measuring attention - we're measuring outputs. The mechanism is speculative. 

**Fix:** Remove the mechanism claim from the core hypothesis. Focus on the *observable* phenomenon: "different scales exhibit systematically different error patterns." The *why* can be future work.

**Flaw 2: P3 (ensemble) might succeed for trivial reasons**

If 7B is terrible (30% accuracy), 70B is decent (60%), and proprietary is best (70%), then majority vote is dominated by the two better models. The ensemble "works" but doesn't prove complementarity.

**Fix:** Add a control: "weighted ensemble where weights are calibrated on held-out validation set" vs "equal-weight majority vote." If calibrated weights don't differ significantly from equal, complementarity is weak.

**Flaw 3: HumanEval+ problems may not be representative**

HumanEval+ is algorithmic coding problems. Enterprise code, UI code, ML pipeline code look very different.

**Fix:** Acknowledge scope limitation explicitly. Add MBPP+ as second benchmark. If results hold across both, generalization claim is stronger.

**Flaw 4: Binary agreement loses information**

A judge that says "80% confident correct" is different from one that says "51% confident correct," but both become "correct" in binary evaluation.

**Fix:** Secondary analysis: correlate judge confidence (if available) with execution outcome. This may reveal *why* some scales are better - they're better calibrated.

**What Would Convince Me:**

1. P1 shows statistically significant scale ordering (Kruskal-Wallis H-test, p < 0.01)
2. P2 shows non-uniform error distribution (chi-square, p < 0.05)
3. P3 shows ensemble improves over best single by >3% (not just within noise)
4. Results replicate across HumanEval+ AND MBPP+

**Key Points:**
- Remove speculative mechanism from core hypothesis
- Add calibrated-weights control for ensemble
- Include MBPP+ for generalization
- Consider confidence calibration as secondary analysis

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critiques make the hypothesis stronger! Let me build on them with a creative synthesis.

The attention mechanism removal is fair - but here's what excites me: the *observable* phenomenon is actually MORE interesting than the mechanism!

If different scales fail differently WITHOUT us knowing why, that's a discovery waiting for explanation. Future work can probe attention patterns, but this paper establishes the *what*.

And here's a wild extension of Prof. Rex's Flaw 4 (confidence calibration): **What if the disagreement between scales IS the confidence signal?**

When 7B says "correct" but 70B says "incorrect" and proprietary says "correct," that 2-1 split might indicate borderline code. When all three agree, we have high confidence. This turns the ensemble from a voting mechanism into a *confidence estimator*.

**Cross-domain connection:** In ensemble learning literature, *disagreement* between diverse models is used for uncertainty quantification. We're applying this to code evaluation!

**Key Points:**
- Observable phenomenon is the discovery; mechanism is future work
- Scale disagreement as confidence signal is a creative extension
- Connects to ensemble uncertainty quantification literature

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's confidence-from-disagreement idea is testable. Let me formalize it.

**New Prediction P4 (Confidence from Disagreement):**

"When all three scales agree, accuracy is higher than when scales disagree."

**Operationalization:**
- Agreement cases: 7B, 70B, proprietary all give same verdict
- Disagreement cases: at least one scale differs
- Measure: accuracy = (correct verdicts) / (total verdicts)

**Success criterion:** Agreement-case accuracy > Disagreement-case accuracy by ≥10%
**Falsification:** Difference < 5%

This is elegant because it doesn't require confidence scores from the models - just their binary verdicts.

**Updated Prediction Summary:**

P1: Scale ordering with diminishing returns
P2: Error type clustering by scale
P3: Ensemble outperforms best single scale
P4: Agreement indicates higher confidence

P4 is the most publishable finding if true - it provides practical guidance: "trust unanimous verdicts more."

**Key Points:**
- P4 formalizes confidence-from-disagreement with clear success/failure criteria
- P4 is practical and publishable
- All four predictions are now testable with available data

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify the refined hypothesis is still technically sound.

**Final Feasibility Check:**

1. **P1 (Scale ordering):** ✅ Feasible
   - Three model tiers clearly defined
   - Kruskal-Wallis test appropriate for ordinal IV with continuous DV
   
2. **P2 (Error clustering):** ✅ Feasible
   - FP/FN binary taxonomy is unambiguous
   - Chi-square requires expected cell counts ≥5; with ~3000 verdicts per scale and ~30% error rate, we get ~900 errors per scale, distributed across FP/FN = 450 each. Sufficient.

3. **P3 (Ensemble improvement):** ✅ Feasible
   - Majority vote trivially implementable
   - McNemar test for comparing ensemble vs best single judge

4. **P4 (Agreement = confidence):** ✅ Feasible
   - Agreement/disagreement computable from verdicts
   - Two-proportion z-test for accuracy comparison

**One remaining concern:**

Prof. Rex suggested MBPP+ for generalization. MBPP+ has ~500 problems (vs HumanEval+ 164). Different problem distribution - more diverse, some harder. This is good for generalization but may show different absolute numbers. We should report both separately, then test if *relative ordering* (P1) and *pattern* (P2) hold across benchmarks.

**Implementation Pathway:**
1. Run 7B, 70B, proprietary judges on HumanEval+ (164 problems × 80+ tests each)
2. Collect binary verdicts + execution results
3. Compute agreement, FP/FN rates per scale
4. Run statistical tests for P1-P4
5. Replicate on MBPP+ for robustness

Okay, this could work.

**Key Points:**
- All four predictions technically feasible
- Statistical tests identified for each prediction
- MBPP+ replication strengthens generalization claims
- Clear implementation pathway

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Perfect! Let me consolidate the final consensus hypothesis.

**Final Hypothesis Statement:**

*"Under standardized code correctness evaluation (fixed prompt, zero temperature), if we vary judge model scale (7B/70B/proprietary), then (1) judge-execution agreement increases with scale with diminishing returns, (2) different scales exhibit systematically different FP/FN error ratios, (3) scale-ensemble outperforms the best single scale, and (4) unanimous scale agreement indicates higher verdict accuracy."*

**Null Hypothesis (H0):**
"There is no significant difference in judge-execution agreement or error patterns across model scales."

**Causal Mechanism (Observable Only):**
Larger models trained on larger code corpora develop different patterns for identifying correctness signals, leading to complementary strengths and weaknesses. (Mechanistic details are future work.)

**Predictions with Success Criteria:**

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Scale ordering with diminishing returns | 7B < 70B < proprietary; (70B-7B) > (proprietary-70B) | Linear or reversed ordering |
| P2 | Error type clustering | Chi-square p < 0.05 for scale × FP/FN association | p > 0.10 |
| P3 | Ensemble improvement | Majority vote > best single by ≥3% | Improvement < 2% |
| P4 | Agreement = confidence | Unanimous accuracy > Split accuracy by ≥10% | Difference < 5% |

**Experimental Setup:**
- Benchmarks: HumanEval+, MBPP+
- Models: DeepSeek-Coder-7B, CodeLlama-70B, GPT-4
- Prompt: Fixed zero-shot correctness judgment prompt
- Metrics: Agreement rate, FP/FN rates, ensemble accuracy

**Key Points:**
- Four-part hypothesis with clear predictions
- All predictions testable with existing data/benchmarks
- No new rubrics or human evaluation required
- Addresses feasibility constraints

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress test before declaring convergence.

**Remaining Concern 1: Model selection justification**

Why DeepSeek-Coder-7B specifically? Why not CodeLlama-7B? This choice affects results.

**Mitigation:** Test BOTH 7B models. If they agree, use either. If they differ, report both. This actually strengthens the paper by showing robustness.

**Remaining Concern 2: Prompt selection**

The "fixed prompt" is crucial but undefined. A bad prompt could artificially depress all accuracies.

**Mitigation:** Pilot 3 prompts on 10% of data, select best-performing one, then use for full evaluation. Document the selection process.

**Remaining Concern 3: What if P1-P3 hold but P4 doesn't?**

P4 (agreement = confidence) is the most novel prediction. If it fails, we still have P1-P3 as contributions.

**Assessment:** This is acceptable. P4 failing is interesting too - it means disagreement doesn't indicate uncertainty, which is also a finding.

**Final Verdict:**

All major concerns addressed. The hypothesis is:
- **Specific**: Clear scale comparison with defined models
- **Testable**: All predictions have success/failure criteria
- **Feasible**: Uses existing benchmarks and APIs
- **Novel**: First scale-controlled error pattern analysis
- **Impactful**: Provides practical ensemble guidance

Now I'm satisfied. We can proceed to structuring.

**Key Points:**
- Test multiple 7B models for robustness
- Pilot prompt selection process
- P4 failure is still publishable as negative result
- All convergence criteria met

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis introduces two genuinely novel elements: (1) first scale-controlled analysis of judge-execution error patterns, and (2) using scale disagreement as a confidence signal. These connect to broader ensemble uncertainty quantification literature.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All four predictions have quantified success/failure criteria. P1 uses Kruskal-Wallis, P2 uses chi-square, P3 uses McNemar, P4 uses two-proportion z-test. Results will be unambiguous.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This work provides practical guidance for the code evaluation community: whether to scale judges, how to ensemble them, and when to trust verdicts. Opens research directions in scale-aware evaluation protocols.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components use existing benchmarks (HumanEval+, MBPP+), publicly available models, and standard statistical methods. No technical barriers to implementation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a four-part hypothesis about model scale effects on code judge accuracy. 

**Core Claim:** When evaluating code correctness using LLM-as-judge, model scale (7B/70B/proprietary) significantly affects both overall accuracy and error patterns. Larger models achieve higher accuracy but with diminishing returns, and critically, different scales make systematically different types of errors (biased toward false positives or false negatives).

**Mechanism:** Larger models trained on different code corpora distributions develop different heuristics for correctness assessment, leading to complementary strengths.

**Key Innovation:** Using scale disagreement as a confidence signal - when all scales agree, verdicts are more reliable. This transforms an ensemble from a simple voting mechanism into a principled confidence estimator.

**Experimental Approach:** Compare three model scales on HumanEval+ and MBPP+ with fixed evaluation prompts. Measure agreement with execution, FP/FN ratios, ensemble accuracy, and unanimous vs split verdict accuracy.

**Predictions:**
1. Scale ordering: 7B < 70B < proprietary with diminishing returns
2. Error clustering: Significant FP/FN ratio differences across scales
3. Ensemble benefit: Majority vote outperforms best single judge by ≥3%
4. Agreement signal: Unanimous verdicts ≥10% more accurate than split verdicts

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Test multiple 7B models (DeepSeek-Coder-7B AND CodeLlama-7B) for robustness
- Pilot prompt selection on 10% subset before full evaluation
- MBPP+ replication needed for generalization claims
- **Mitigation Strategy:** Include all as methodology steps; negative results on P4 are still publishable

---

## Emerged Hypothesis Summary

### Core Statement
Under standardized code correctness evaluation settings, if we compare LLM judges of varying scale (7B/70B/proprietary), then judge-execution agreement increases with scale but with diminishing returns, different scales exhibit systematically different FP/FN error patterns, scale-ensemble outperforms individual judges, and unanimous scale agreement indicates higher verdict reliability, because larger models develop complementary correctness heuristics during training.

### Causal Mechanism
1. Models at different scales are trained on overlapping but not identical code distributions
2. Smaller models rely more heavily on surface patterns (syntax, structure)
3. Larger models capture deeper semantic relationships but may over-generalize
4. This creates complementary error patterns: small models miss subtle logic, large models are fooled by superficial correctness
5. Ensemble combination exploits this complementarity; unanimous agreement filters high-confidence cases

### Variables
**Independent:** Judge model scale (7B, 70B, proprietary)
**Dependent:** Judge-execution agreement rate, FP rate, FN rate, ensemble accuracy, unanimous-case accuracy
**Controlled:** Evaluation prompt, temperature (0), benchmark (HumanEval+/MBPP+)

### Key Assumptions
- A1: Models from same scale tier have similar error patterns (testable by comparing two 7B models)
- A2: HumanEval+/MBPP+ execution results are reliable ground truth
- A3: Zero-shot prompting is representative of judge usage patterns
- A4: Model scale is the primary differentiator (not architecture details)

### Null Hypothesis
There is no significant difference in judge-execution agreement patterns across model scales; error types are uniformly distributed regardless of scale.

### Predictions
- P1: 7B < 70B < proprietary agreement, with (70B-7B) > (proprietary-70B)
- P2: Chi-square test shows significant scale × FP/FN association (p < 0.05)
- P3: Majority-vote ensemble > best single scale by ≥3%
- P4: Unanimous verdict accuracy > split verdict accuracy by ≥10%

### Novelty
First systematic study of judge-execution error patterns across model scales with scale-ensemble and agreement-as-confidence insights.

### Scope & Boundaries
**Applies to:** Algorithmic coding problems (HumanEval+, MBPP+), Python language, zero-shot evaluation
**Does not apply to:** Enterprise code, multi-file projects, non-Python languages (without further validation)

### Experimental Setup
- Benchmarks: HumanEval+ (164 problems), MBPP+ (500 problems)
- Models: DeepSeek-Coder-7B, CodeLlama-7B (robustness), CodeLlama-70B, GPT-4
- Prompt: Zero-shot "Is this code correct?" (pilot-selected from 3 candidates)
- Execution: EvalPlus framework for ground truth

### Related Work & Baselines
- Baseline 1: Naik (2024) - CodeBERTScore correlation 0.16
- Baseline 2: Crupi (2025) - GPT-4-turbo accuracy (reported as "frequent misjudgment")
- Baseline 3: MCTS-Judge (Wang 2025) - 80% accuracy with test-time compute

### Phase 2B Readiness Seeds
- SH1 (Existence): Scale-dependent error patterns exist and are statistically detectable
- SH2 (Mechanism): Different scales have complementary FP/FN biases
- SH3 (Comparison): Deferred to Phase 5 baseline comparison

### Established Facts
- CodeBERTScore has 0.16 correlation with functional correctness (Naik 2024) - BUILD_ON
- LLM judges exhibit 6 types of bias (Moon 2025) - BUILD_ON
- MCTS improves single-judge accuracy to 80% (Wang 2025) - COMPARE_AGAINST
- HumanEval+ provides 80x more test coverage (Liu 2023) - USE_AS_BENCHMARK

---

*Discussion completed after 11 exchanges. Convergence achieved on four-part scale-effect hypothesis with clear predictions and feasibility confirmation.*

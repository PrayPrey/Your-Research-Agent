# 1. Introduction

A program that outputs the correct answer on 764 tests is still wrong 40% of the time — if you ask a formal contract.

This counterintuitive finding motivates the central question of this paper: when the evaluation oracle changes from differential output equality to formal contract satisfaction, how many "correct" LLM programs are exposed as incorrect? The answer, we show, is nearly half — and understanding *why* requires rethinking what LLM coding benchmarks actually measure.

**The surface problem** is well-known: LLM-generated code frequently contains errors that sparse test suites miss. The field has responded with denser evaluation — EvalPlus expanded HumanEval by 80× and MBPP by 35×, reducing pass@1 by up to 23.1% [Liu2023EvalPlus]. Yet even these exhaustive differential test suites rely on a fundamental design choice: they check whether the program produces the *same output as a reference implementation* on a finite set of sampled inputs.

**The deeper problem** is that this oracle cannot check universal properties. Formal contracts — pre- and post-conditions on function behavior — encode relational invariants, quantified conditions, and semantic constraints that must hold for *all* valid inputs, not just a finite sample. A program can return the numerically correct answer on every test input while violating a postcondition asserting, for example, that the output is a permutation of the input, or that all returned elements satisfy a membership constraint. Dense differential testing cannot detect these violations; it is structurally incapable of doing so.

**The gap** is this: no published work has measured the execution-based oracle-strength gap across multiple LLM families on ContractEval [Lim2025ContractEval] — the only benchmark pairing standard coding tasks (HumanEval+/MBPP+) with formal Python pre/post-condition contracts. ContractEval's own evaluation [Lim2025ContractEval] uses SMT-based test synthesis (Z3), which is tractable for only 25.82% of tasks. Prior property-based testing work [Bose2025Prompts] evaluates only two models and lacks formal contract annotations. No study has quantified how much stronger a contract oracle is than a dense differential oracle on the *same* inputs — the key question for understanding what coding benchmarks measure.

**Our key insight** is that oracle semantics must be decoupled from input strategy. By using ContractEval's contract-violating test inputs (CVT inputs) as a controlled, fixed input set, we can evaluate both a differential equality oracle and a contract oracle on identical inputs — directly measuring oracle semantic strength without any input-generation confound. On CVT inputs, when the LLM program returns the same output as the ground-truth canonical, the differential oracle classifies the program as correct. If the reference contract fires nonetheless, that disagreement is entirely attributable to the contract encoding semantics that equality cannot express.

The result is striking: the contract oracle detects 40% more failures than the differential oracle on CVT inputs (oracle-isolation gap = 0.40, 4× the 0.10 threshold), with 40% of evaluations constituting "contract-unique" failures — programs whose output matches ground truth but whose behavior violates the reference contract (CU mass = 0.40, Wilcoxon p = 5.88e−38, n = 10,432 triples, 364/364 tasks). Additionally, adaptive property-based testing via Hypothesis with icontract-hypothesis [icontract_hypothesis] finds an additional ~10 percentage points of violations beyond static CVT inputs (mean contribution = 0.0999, Wilcoxon p = 2.64e−22), consistently across all 5 model families.

**We make the following contributions:**

1. **Oracle isolation design** — a controlled experiment using CVT inputs to measure contract oracle semantic strength independently of input generation strategy; first clean methodology for oracle-type comparison on any benchmark with formal contract annotations.

2. **Quantification of the differential-contract oracle gap** — oracle-isolation gap of 0.40 (95% CI [0.358, 0.445]) across 364 ContractEval tasks and 5 LLM families, with 40% contract-unique mass; both values far exceed predicted thresholds, demonstrating a qualitative gap, not a marginal improvement.

3. **Adaptive PBT contribution** — icontract-hypothesis adaptive property-based testing adds ~10pp violations beyond static oracle inputs (Wilcoxon p = 2.64e−22), model-invariantly across all 5 families tested; confirming that adaptive search and oracle semantics contribute distinct, independent layers of contract violation detection.

4. **Principled negative results** — oracle-gap does not scale monotonically with contract richness (Spearman ρ = 0.136, not ρ ≥ 0.30), and cross-model gap is negligible at n=5 (ΔR² = 0.004); both findings are informative about ContractEval's contract structure and the current evaluation setting.

We organize this paper as follows: Section 2 reviews related work on LLM code evaluation, property-based testing, and formal contract checking. Section 3 presents our methodology, including the CVT oracle isolation design and adaptive PBT experimental setup. Section 4 describes our experimental configuration. Section 5 reports results across all sub-hypotheses. Section 6 discusses implications and limitations. Section 7 concludes.

# Phase 2A Research Discussion Log
# Gap: No Complementary Failure Coverage Analysis Comparing SynCode, Z3-Repair, and Static Analysis Feedback
# Generated: 2026-05-09
# Architecture: Self-Contained Tikitaka Loop v9.0.0

---

## Research Briefing

**Research Folder:** docs/youra_research/20260508_verifai/
**Gap ID:** gap3
**Gap Title:** No Complementary Failure Coverage Analysis Comparing SynCode, Z3-Repair, and Static Analysis Feedback on the Same Python-Only Benchmark

**Context:**
This Phase 2A discussion follows a ROUTE_TO_0 recovery from h-e1, which failed due to Docker unavailability.
The new direction uses exclusively Python-native tools (no Docker). Three formal method strategies are being investigated:
1. SynCode grammar-constrained decoding (Python CFG pushdown automaton)
2. Z3-guided post-hoc repair (z3-solver pip package)
3. mypy/ast/pyflakes static analysis feedback loop

**Core Research Gap:**
No study measures the pairwise disjointness of failure sets fixed by the three strategies on the same
Python-only benchmark (HumanEval/MBPP/EvalPlus). This is the VerifAI workshop-worthy novelty contribution.

**Infrastructure Constraints:**
- MUST use Python-native tools only (pip-installable, no Docker)
- SynCode confirmed operational from h-e1 (verify_operational() passed)
- EvalPlus is the recommended evaluation harness (Python-native subprocess runner)
- h-e1 reusable assets: CodeGenerator, EvalPlusLoader, metrics.py

**Reference Papers Available:** None (MCP unavailable during Phase 1 — all sources [INFERRED])

**Key Papers (Inferred):**
- SynCode (Ugare et al., ~2024): arXiv 2403.01632 — CFG enforcement via pushdown automaton
- HumanEval (Chen et al., 2021): arXiv 2107.03374 — pass@k evaluation protocol
- EvalPlus (Liu et al., 2023): arXiv 2305.01210 — augmented benchmark, 80× harder tests
- SELF-REFINE (Madaan et al., 2023): arXiv 2303.17651 — iterative feedback for code
- CodeT (Chen MSFT, 2022): arXiv 2207.10397 — dual execution ensemble, template for complementarity

**Feasibility Filters (MANDATORY):**
- REJECT: Requires new benchmarks, rubrics, or scoring frameworks
- REJECT: Requires synthetic/generated data or future data
- REJECT: Requires human evaluation or annotation
- ACCEPT: Testable immediately with existing HumanEval/MBPP/EvalPlus + Python-native tools

---

### Exchange 1

🔬 **Prof. Vera** (Rigorous Validation Architect):

The central claim is that SynCode, Z3-repair, and static-analysis feedback correct *complementary* subsets of failures. That is a falsifiable statement, and we must treat it as such. The evidence would need to show statistically significant non-overlap in the sets of tasks each method uniquely converts from failing to passing under EvalPlus. Therefore, the primary experimental object is not pass@k in isolation, but the *failure-to-success transition set* per method on an identical base sample of generated programs.

I propose the following design. For each HumanEval (or MBPP) problem, generate a fixed pool of N samples (e.g., N=20) using the same base CodeGenerator with temperature T and fixed random seeds. Freeze this pool. Evaluate all samples under EvalPlus to determine the baseline failing set F₀. Then apply each intervention independently: (1) SynCode at decoding time, (2) Z3-guided repair applied post hoc to the same failing samples, and (3) static-analysis feedback loop (mypy/pyflakes/AST-based corrections) with a bounded iteration budget (e.g., max 3 refinements). For each method m, define Fₘ→✓ as the subset of F₀ that becomes passing after applying m. Complementarity can then be quantified via Jaccard overlap between Fₘ→✓ sets and by computing |Fₐ→✓ ∩ F_b→✓| relative to their unions.

What would disprove the hypothesis? If the Jaccard similarity between any pair of repair sets exceeds, say, 0.8 across tasks, the claim of meaningful complementarity collapses. Similarly, if a simple union-of-methods strategy yields negligible lift over the best individual method (e.g., <2% absolute pass@1 improvement), then complementarity lacks practical significance. These thresholds must be pre-registered to avoid post hoc rationalization. I would also require bootstrap confidence intervals over tasks to ensure observed disjointness is not sampling noise.

Confounds must be controlled rigorously. SynCode operates during decoding, whereas Z3 and static analysis operate post hoc; this introduces asymmetry in opportunity. To equalize, we should include a control condition where baseline decoding is followed by *no-op reformatting* with identical iteration budget to account for stochastic regeneration effects. Additionally, we must cap computational budget per task identically (e.g., same wall-clock or repair attempts). Another confound is that Z3-repair may only apply to a subset of tasks with tractable constraints; this eligibility filter must be recorded, and complementarity metrics computed both on the full task set and on the intersection of applicable tasks.

Finally, we should stratify failures by type: syntax errors, type inconsistencies, logical test failures. The evidence suggests SynCode primarily eliminates syntactic invalidity [Ugare et al., ~2024, INFERRED], while static analysis targets type-level issues and Z3 targets semantic constraint violations. If complementarity is genuine, we should observe method-specific enrichment for distinct failure categories. A chi-squared test on repair-type vs. method would provide mechanistic support rather than mere set arithmetic.

If executed with frozen generations, pre-specified thresholds, controlled budgets, and categorical failure analysis, this would meet my standards. Without those safeguards, it is an anecdote, not a study.

**Key Points:**
- Define complementarity as disjoint failure-to-success transition sets and pre-register quantitative thresholds (e.g., Jaccard < 0.8, ≥2% union lift).
- Freeze a shared generation pool and equalize computational budgets to eliminate decoding and iteration confounds.
- Validate mechanistic distinctness via stratified failure-type analysis, not just aggregate pass@k gains.

---

### Exchange 2

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔬 Prof. Vera has laid out a theoretically airtight experimental design, and I want to affirm that the core framework is technically sound before probing two genuine feasibility concerns. The failure-transition-set framing (Fₘ→✓) is the right primitive — it asks a sharper question than aggregate pass@k and is fully measurable with existing Python-native infrastructure. EvalPlus's subprocess-based test runner makes this tractable without Docker; we generate a frozen pool offline, serialize it to disk, and each repair strategy consumes the same serialized set independently. There is no fundamental barrier here.

However, I want to raise a *mechanism* feasibility issue with Z3-guided repair that Prof. Vera's design correctly identifies but may underestimate in severity. Z3-solver can solve constraint satisfaction problems, but extracting Z3-encodable constraints from arbitrary HumanEval/MBPP Python functions is non-trivial. The problems are natural-language-specified; many have no explicit type annotations or SMT-encodable invariants. For problems involving string manipulation, list comprehensions, or recursive definitions — which constitute a substantial fraction of HumanEval — constructing a Z3 formula from the failing assertion alone is either undecidable or requires symbolic execution infrastructure (e.g., angr, pysmt) that goes beyond the z3-solver pip package. The "eligible tasks" filter Prof. Vera mentions is critical, and my estimate is that fewer than 30–40% of HumanEval problems will have tractable Z3 encodings using just the z3-solver API. This eligibility constraint must be clearly stated as a scope boundary, not a confound — it *defines* what Z3-repair can claim.

A second concern is the post-hoc vs. decoding asymmetry. SynCode eliminates entire classes of syntactically invalid tokens during generation, which means it never produces syntactically broken outputs. Applying Z3 or mypy post hoc to SynCode-generated code vs. baseline-generated code is comparing different input distributions. For a clean complementarity measurement, I recommend that the repair strategies (Z3, mypy) be applied to the *same baseline-generated pool* (no SynCode), not to SynCode outputs. This keeps the treatment arms independent and the failure-set arithmetic interpretable. SynCode's contribution is measured separately as: how many *additional* problems does the ensemble (SynCode ∪ Z3 ∪ mypy-feedback) solve vs. SynCode alone?

On the practical side: CodeGenerator from h-e1 supports device="auto" CPU fallback, meaning we can run CodeLlama-7B on CPU if no GPU is available, though this will be slow. Recommend using EvalPlus's built-in `evalplus.evaluate` API with a custom model hook rather than reimplementing the runner. The pass@k estimator in EvalPlus is unbiased and handles the frozen-pool sampling correctly out of the box — we should use it directly rather than writing our own.

**Key Points:**
- Z3 eligibility is a scope boundary, not a confound: expect ~30–40% of HumanEval tasks to have tractable Z3 encodings; state this explicitly as a hypothesis scope condition.
- Keep repair arms (Z3, mypy-feedback) operating on the same baseline-generated pool, independent of SynCode, to preserve interpretable failure-set arithmetic.
- Use EvalPlus's native `evalplus.evaluate` API and CodeGenerator's CPU fallback — no new infrastructure required.

---

### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming testable. But here's where this still breaks down: you're treating "complementarity" as set non-overlap without proving it's not just *capacity differences in disguise*. If Z3 only applies to 30–40% of tasks, of course its Fₘ→✓ set will look different. That's not complementarity — that's domain restriction. Show me that within the *intersection of applicable tasks*, the repair sets remain meaningfully non-overlapping. If complementarity disappears once you condition on eligibility, the claim collapses.

Second, the frozen-pool design is necessary but not sufficient. What's the base failure composition? If 60% of baseline failures are syntax errors, SynCode will dominate by construction. You need to report the *prior distribution* of failure types in F₀. Otherwise you risk rediscovering a trivial fact: "syntax-aware decoding fixes syntax errors." That's not a novel complementarity claim — that's category alignment. What would convince me is a conditional analysis: within the subset of logical test failures (no syntax/type errors), does Z3 recover cases that static analysis does not, and vice versa? If all methods cluster by obvious error class, you're showing specialization, not deep complementarity.

I'm also uneasy about the ≥2% union lift threshold. Why 2%? On HumanEval, that's often 3–4 problems. That could easily be noise depending on model variance. Pre-registering a threshold is good, but justify it statistically. For example: define complementarity as union performance exceeding the best single method by more than the 95% bootstrap CI of that method's pass@1. That ties your claim to statistical distinguishability, not an arbitrary margin. Otherwise reviewers will call this threshold shopping.

Now let's talk mechanism. You're implying three distinct repair mechanisms: syntactic pruning (SynCode), symbolic constraint satisfaction (Z3), and static semantic checking (mypy/AST). Fine. Then make a *predictive claim*:
- SynCode improvements should concentrate in high-perplexity decoding regimes (higher temperature).
- Z3 gains should correlate with tasks whose specs can be reduced to linear integer arithmetic or finite-domain constraints.
- Static analysis gains should correlate with type-annotated or structurally simple functions.

If these correlations don't materialize, your "mechanistic complementarity" story is post hoc rationalization. What would convince me is a regression where repair success is predicted by measurable task features — spec length, presence of arithmetic invariants, type hints, control-flow depth — and each method loads significantly on different predictors.

Finally, real-world impact. Why does this matter beyond HumanEval? If complementarity is real, then ensemble repair should scale *sublinearly* in cost relative to performance gain. Show cost–benefit curves: additional wall-clock vs. marginal pass@1 lift. If the ensemble doubles compute for a 3% gain, practitioners won't care. But if targeted application (e.g., syntax-first, then constraint-only on arithmetic tasks) yields most of the union gain at 1.3× cost, *that's* operationally significant. Without cost-normalized analysis, your impact claim is hollow.

Right now, the design is careful — but the interpretation risks being superficial. Tighten the conditioning, justify thresholds statistically, and make mechanism-linked predictions. Do that, and I'll say: now you've addressed my concerns.

**Key Points:**
- Condition complementarity analysis on overlapping eligibility sets; otherwise non-overlap may just reflect domain restriction.
- Replace arbitrary union-gain thresholds with statistically justified criteria tied to bootstrap confidence intervals.
- Make mechanistic, feature-linked predictions and report cost–benefit tradeoffs to substantiate real-world significance.

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has just sharpened this considerably, and I want to build on the significance question rather than let it remain implicit. Let me state what this research is actually claiming at the field level — because that's what determines whether VerifAI accepts it or whether it becomes a footnote.

The field currently stands at an impasse: formal methods integration with LLM code generation has proceeded *piecemeal*. SynCode is evaluated in isolation [Ugare et al., ~2024]. Program repair via execution feedback is studied independently (SELF-REFINE [Madaan et al., 2023]). SMT-guided repair is explored in symbolic-execution contexts disconnected from benchmark-scale evaluation. The community *lacks* a unified framework that asks: do these mechanisms fix categorically different bugs? If yes, can a practitioner deploy a tiered strategy that recovers most of the ensemble gain at modest cost? That is the question this research can answer — and no existing work does.

What would make this a genuine contribution vs. incremental work? Three things: (1) the complementarity measurement must be on an *existing, standardized benchmark* (HumanEval/EvalPlus) so claims are directly comparable to SOTA — Prof. Vera's frozen-pool design enables this; (2) the findings must translate into a *design principle*, not just a number — the finding should be "strategies that operate at different error abstraction levels (syntactic, constraint-semantic, type-semantic) produce disjoint improvement sets; deploy them in order of detection cost"; (3) the paper must include at least one prediction that could have come out differently but didn't — Prof. Rex's feature-regression idea serves this purpose perfectly.

On the significance of Prof. Rex's eligibility-conditioning challenge: I agree it must be addressed, but I'd frame it differently for field impact. The fact that Z3 only applies to ~30–40% of tasks is *itself a finding* worth publishing at a workshop — it quantifies the boundary of formal-method applicability on realistic Python benchmarks. Papers that characterize the scope of their tools are more useful to practitioners than papers that cherry-pick favorable conditions. We should embrace the eligibility analysis and report it prominently.

What new research directions does this open? If stratified complementarity holds: (a) future work can design task-type classifiers that route problems to the appropriate repair strategy automatically, reducing ensemble cost further; (b) it motivates combining SynCode-style decoding constraints with type-inference-guided generation (not just post-hoc repair); (c) it establishes a benchmark protocol for evaluating future formal-method integrations. These are three concrete follow-on directions — that's the mark of a contribution that opens rather than closes questions.

My verdict: if the experiment is executed with the rigorous conditioning Prof. Rex demands, this is a strong VerifAI workshop contribution and a credible arXiv paper. The core claim — "existing formal methods for Python code generation repair categorically different failure types; their ensemble is practically superior but condition-bounded" — is specific, testable, and currently unanswered.

**Key Points:**
- The significance lies in the unified complementarity measurement: the field has each strategy in isolation; this paper provides the first cross-strategy failure-set analysis on standardized benchmarks.
- The eligibility boundary (Z3 on ~30–40% of tasks) is a publishable finding in itself — it characterizes formal method applicability on realistic Python problems.
- Three concrete follow-on directions emerge from stratified complementarity: cost-routing classifiers, constraint-guided generation, and a reusable benchmark evaluation protocol.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the kind of pressure-testing that turns a "nice idea" into a publishable contribution. Prof. Rex is right: if complementarity vanishes once we condition on eligibility and failure type, the claim weakens substantially. So what if we *elevate* the hypothesis? Instead of "methods fix different problems," we state:

> **H1 (Mechanistic Complementarity):** Within the intersection of applicable tasks and within matched failure categories, repair strategies operating at different abstraction levels (syntactic, type-semantic, constraint-semantic) recover statistically distinct subsets of failures.

Now THAT's stronger. It explicitly commits us to conditional analysis — not just raw set arithmetic. So we compute Fₘ→✓ on (a) the full task set, (b) the eligibility-intersection subset, and (c) stratified by failure type (syntax, type, logical). If Z3 and static analysis remain non-overlapping *within logical failures on eligible tasks*, that's real complementarity. If they collapse into the same subset, we revise the claim accordingly. No hand-waving.

On the threshold issue: I agree 2% absolute lift is arbitrary. What if we define complementarity operationally as:

> **Union gain > upper 95% bootstrap CI of best single method AND Jaccard < 0.6 within conditioned subsets.**

This replaces an arbitrary margin with statistical distinguishability. We pre-register this criterion. If union performance clears the CI bound, we can say the ensemble achieves improvement unlikely under sampling noise. That directly addresses the variance concern and aligns with EvalPlus's unbiased pass@k estimator.

Now let's strengthen the mechanistic story — because that's where this becomes more than bookkeeping. Prof. Rex asked for predictive linkage. Good. Let's formalize three measurable task features:
- **Arithmetic constraint density** (count of numeric operators + presence of boundary conditions in tests)
- **Type annotation richness / structural depth**
- **Baseline syntax invalidity rate at T ∈ {0.2, 0.8}**

Then we run a logistic regression predicting repair success per method from these features. The prediction is crisp:
- SynCode gains scale with higher temperature and baseline syntax invalidity.
- Z3 gains load positively on arithmetic density and simple control-flow.
- Static analysis gains correlate with type richness and shallow AST depth.

If coefficients diverge significantly across methods, that's mechanistic validation — not post hoc storytelling. And if they don't? We refine the theory. That's how we win.

Now let's address the integration strategy — because we were selected to move beyond simple ensemble comparison. What if instead of "apply all three," we design a **cost-aware routing policy** learned from the same feature model? Step 1: detect syntax invalidity → apply SynCode during decoding. Step 2: if arithmetic density > threshold → invoke Z3-repair. Step 3: if type-rich & shallow → apply static feedback loop. We can then plot cost–benefit curves comparing:
- Full ensemble (all methods always)
- Best single method
- Feature-routed tiered strategy

If the routed strategy achieves ≥80% of union gain at ≤1.3× compute cost, that's a deployable principle — exactly the kind of design rule Dr. Sage highlighted as field impact. Even if Z3 eligibility is 30–40%, quantifying that boundary and showing when it pays off becomes a publishable insight in its own right.

So here's the strengthened claim:

> Formal repair strategies for LLM-generated Python code exhibit conditional mechanistic complementarity that can be exploited via feature-aware routing to achieve statistically significant performance gains at sublinear cost.

That's falsifiable. That's predictive. And importantly — it can fail in informative ways.

**Key Points:**
- Elevate the hypothesis to *conditional mechanistic complementarity* and test within eligibility and failure-type strata.
- Replace arbitrary thresholds with bootstrap-CI-based statistical criteria and regression-linked mechanistic predictions.
- Move beyond ensemble comparison by proposing a feature-aware routing strategy with explicit cost–benefit evaluation.

---

### Exchange 6

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this too narrowly? 🛡️ Dr. Ally's conditional mechanistic complementarity framing is exactly right, and I want to push on where the real *novelty signal* lives — because right now we're describing a fairly classical ensemble analysis dressed in formal-method clothes. The question the field will ask is: what's the *insight* that couldn't have been stated without running this experiment?

Here's what I find genuinely exciting: the three strategies operate at fundamentally *different abstraction levels of the correction signal*. SynCode acts at the token-probability level — it's a generation prior. Z3 acts at the constraint-satisfaction level — it's a logical consistency oracle. Static analysis acts at the code-structure level — it's a structural conformance checker. These aren't just different algorithms; they're different theories of what a "bug" is. SynCode says: the bug is malformed syntax (eliminate it by construction). Z3 says: the bug is a violated invariant (solve it backward from the test assertion). mypy/ast says: the bug is a type contract violation or structural anomaly (detect it via static signature analysis).

NOW the novelty claim becomes: *For the first time, this work operationalizes three categorically different theories of bug causation on a standardized benchmark and measures whether they partition the failure space.* That's not just "which method fixes more." That's a philosophical claim about the structure of LLM-generated code failures — and it's directly testable.

What if we go further? The routing policy Dr. Ally proposes is valuable, but what if the feature model itself is the paper? We could train a lightweight meta-classifier — call it a Repair Strategy Selector (RSS) — on measurable program features (arithmetic density, type richness, AST depth, syntax invalidity rate). The RSS predicts, before repair, which strategy to apply. If RSS achieves ≥90% of oracle ensemble pass@1 at 1× cost (single strategy per task), that's a deployable system. And the learned feature weights directly validate the mechanistic complementarity story: if SynCode and Z3 and mypy load on distinct feature dimensions in the RSS's decision boundary, we've empirically confirmed the three-theory hypothesis without requiring explicit Jaccard conditioning.

I'm also thinking about the broader narrative: this is a *benchmark for formal-method integration strategies*. Not just an experiment. Any future formal method for Python code generation can be evaluated using the same frozen-pool protocol, eligibility analysis, and stratified Jaccard computation. We're not just answering our question — we're providing infrastructure for the field. That's what elevates a workshop paper to something that gets cited.

On the feasibility side: the RSS training data is free — it's generated by the same frozen pool experiment. Feature extraction (AST analysis, arithmetic pattern matching, type annotation counts) is pure Python with stdlib + ast module. No external dependencies. This is doable with existing infrastructure.

The wild idea: what if we frame the whole paper as "Debugging Theories for LLM Code Generation" rather than "Formal Method Comparison"? The methods are the experimental apparatus; the theories are the contribution.

**Key Points:**
- The core novelty is empirical operationalization of three distinct theories of bug causation (syntax, constraint, structural) on a standardized benchmark.
- A Repair Strategy Selector (RSS) meta-classifier trained on program features could serve as both validation of complementarity and a deployable artifact.
- The frozen-pool + eligibility + stratified-Jaccard protocol constitutes reusable benchmark infrastructure — elevating the contribution beyond a single experiment.

---

### Exchange 7

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The strengthened hypothesis — *conditional mechanistic complementarity within matched eligibility and failure strata* — is technically coherent. There's no physical or mathematical impossibility in the design. But here's what worries me: you're assuming that the repair operators are causally independent enough to produce genuinely disjoint success sets under conditioning. That's an empirical question, and it could easily fail in principle if the dominant bottleneck is simply "incorrect functional logic," which none of the methods truly fixes in a deep sense. If Z3 repair and static analysis both ultimately reduce to local patching guided by test failures, their solution manifolds may substantially overlap once you control for syntax and type errors. So the key feasibility check is this: do these methods operate on sufficiently orthogonal information channels? SynCode clearly does — it modifies the generation prior. Z3 uses semantic constraints extracted from tests. Static analysis relies on structural/type rules independent of test semantics. In principle, those are distinct signal sources. So complementarity is *possible*. But it's not guaranteed.

On the eligibility-conditioning issue raised by Prof. Rex: that's not just good methodology — it's required for theoretical validity. If Z3's constraint extraction fails on 60% of tasks because the tests aren't reducible to SMT-friendly constraints, then any complementarity claim must be scoped to the subspace where symbolic reasoning is well-defined. Otherwise you're conflating "non-applicable" with "non-overlapping." That's a category error. The good news is that eligibility itself is objectively measurable: successful constraint encoding without loss of semantic fidelity. That's a binary property per task. There's no theoretical ambiguity there.

Now, about the proposed regression and RSS classifier. Conceptually sound. There's no barrier to extracting AST depth, arithmetic operator counts, or annotation richness — they're computable features. But here's the deeper question: do those features *causally mediate* repair success, or are they proxies for something else (like overall task difficulty)? If arithmetic density predicts Z3 success, is that because Z3 is uniquely solving arithmetic invariants, or because arithmetic-heavy tasks tend to have simpler control flow? To avoid spurious inference, you'll need multivariate models and possibly matched subsets. Otherwise your mechanistic interpretation may not be theoretically justified.

On the union-gain statistical criterion: replacing a fixed 2% threshold with "exceeds upper 95% bootstrap CI of best single method" is methodologically sound. That aligns the complementarity claim with statistical distinguishability rather than arbitrary margins. Just ensure the bootstrap respects the pass@k estimator structure — resample at the problem level, not per-generation — otherwise your variance estimate is invalid.

Finally, the RSS meta-classifier. Feasible in principle, yes. But be careful: if the selector is trained on the same frozen pool used to evaluate complementarity, you risk circularity. Theoretically, you need a proper split — train RSS on half the tasks, evaluate on the other half — otherwise you're approximating the oracle ensemble through memorization. With a proper split, though, there's no fundamental barrier.

**Key Points:**
- Complementarity is theoretically possible because methods operate on distinct signal sources, but independence is empirical — not guaranteed.
- Eligibility must be formally defined and conditioned on; otherwise complementarity claims are logically invalid.
- Regression and RSS routing are feasible, but require multivariate controls and proper train/test splits to avoid spurious mechanistic conclusions.

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

⚙️ Prof. Pax has correctly identified the epistemic risk — conflating non-applicability with non-overlap is the most dangerous validity threat in this design. Let me crystallize the experimental contract that prevents this.

We need three stratified analyses, each answering a progressively tighter question. **Analysis 1 (Full set):** Compute Jaccard(F_SynCode→✓, F_Z3→✓, F_mypy→✓) on the complete HumanEval+EvalPlus tasks. This is the population-level claim and will be the headline number. **Analysis 2 (Eligibility-conditioned):** Restrict to the intersection of tasks where all three methods are applicable — Z3 encodes successfully, mypy finds type signals, SynCode operates (always true). Recompute Jaccard within this subset. If Analysis 2 Jaccard is meaningfully lower than Analysis 1 (after bootstrap CI), we've confirmed that eligibility is not driving apparent non-overlap. **Analysis 3 (Failure-type-stratified):** Within the eligibility-conditioned subset, further stratify by failure category (syntax, type, logical test failure) and compute within-stratum Jaccard. This is the mechanistically definitive analysis: within the same error category, do different methods recover different programs?

The formal null hypothesis is: H₀: Jaccard(F_m1→✓, F_m2→✓ | eligible ∩ failure_type) ≥ 0.6 for all method pairs m1, m2. We reject H₀ per pair if bootstrap CI upper bound falls below 0.6. This gives us three null tests (SynCode vs Z3, SynCode vs mypy, Z3 vs mypy) and a family-wise Bonferroni correction.

Prof. Pax raises the right concern about the RSS: train/test contamination. Solution: use the HumanEval (164 problems) as training set for the RSS logistic regression, and EvalPlus's additional 800 problems (or MBPP's 374) as the test set for evaluating routing policy performance. Feature extraction is deterministic and has no data leakage. The RSS then reports: on held-out problems, does routing to the predicted best method achieve ≥80% of oracle-ensemble pass@1 at ≤1.3× median cost?

One more critical design point: the "baseline" must be defined precisely. I propose: **Baseline** = CodeLlama-7B with temperature 0.8, greedy-or-nucleus sampling, 20 samples per problem, no repair. All repair strategies are applied to this exact generation pool. Unconstrained baseline pass@1 is computed from this pool. Then SynCode is measured by regenerating with grammar constraints applied (NOT post-hoc filtering), which means a separate generation pool must be created for SynCode — this is the one asymmetry that cannot be avoided without fundamentally changing how SynCode works. Document this explicitly and report both the constrained pool pass@1 and the repair results on the unconstrained pool.

This meets my standards for falsifiability and rigor.

**Key Points:**
- Three-tier stratified analysis (full set → eligibility-conditioned → failure-type-stratified) prevents eligibility masquerading as complementarity.
- Null hypothesis formally defined as Jaccard ≥ 0.6 per pair within conditioned strata, tested via bootstrap CI with Bonferroni correction.
- RSS trained on HumanEval / evaluated on EvalPlus+MBPP held-out set eliminates data leakage while validating routing policy.

---

### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally getting serious. But here's where this still breaks down if you're not careful.

First, your "three theories of bugs" narrative (syntax, constraint, structural) is rhetorically strong — but rhetoric is not evidence. Show me that these are *causally distinct signal channels*, not just different surfaces over the same underlying failure: incorrect functional logic. If 70% of failures are simply "wrong algorithm," and none of your methods can truly synthesize missing logic, then you're partitioning a small residual slice of the error space. What would convince me is this: quantify the total failure mass attributable to each failure type *before* repair. If syntax errors are only 8% of failures at T=0.8, SynCode's theoretical ceiling is capped. If logical invariant violations dominate, then Z3's headroom matters. Without that base-rate decomposition, your complementarity claim floats in mid-air.

Second, on the eligibility-conditioned Jaccard analysis: better. Necessary. But your null hypothesis Jaccard ≥ 0.6 is still arbitrary. Why 0.6? That number smuggles in a structural claim about expected overlap under independence. If two methods each fix 20% of the same eligible set independently, expected Jaccard under independence is not 0.6 — it's much lower. So 0.6 may already imply strong redundancy. I want to see a *null model*: simulate overlap under independence given observed marginal repair rates. Then test whether observed overlap is significantly lower than that simulated expectation. That's the real stress test. Otherwise, you're choosing a threshold that may accidentally flatter your result.

Now the RSS idea. I like it — but here's the hard question: is the selector learning mechanistic structure, or just overfitting superficial correlates of difficulty? If arithmetic density predicts Z3 success, is that because Z3 uniquely leverages arithmetic constraints — or because arithmetic-heavy problems are shorter and simpler? What would convince me is an ablation: include a proxy for task difficulty (baseline pass@1 or solution length) in the regression. If arithmetic density still has a significant coefficient for Z3 success *after controlling for difficulty*, then you've earned the mechanistic interpretation. If it vanishes, your "theory of bugs" collapses into a theory of easy tasks.

One more place this could break: cost modeling. You're promising ≥80% of oracle gain at ≤1.3× cost. Fine. But what cost? Wall-clock? GPU-seconds? SMT solve time? If Z3 eligibility filtering itself costs significant CPU time, your routing advantage may evaporate. I want a precise cost accounting model: C_total = C_gen + C_feature + C_repair + C_verification. If the RSS requires computing features that already approximate running static analysis, you've hidden cost in preprocessing.

That said — conditioning on eligibility, defining bootstrap at the problem level, splitting RSS train/test across benchmarks — those address real threats. Now push one level deeper: (1) quantify base-rate failure composition, (2) replace arbitrary Jaccard thresholds with independence-based null simulations, (3) control for difficulty in mechanistic regressions.

**Key Points:**
- Complementarity must be evaluated relative to base-rate failure composition; otherwise ceilings are unknown.
- Replace arbitrary Jaccard thresholds with overlap expectations under an independence null model.
- Mechanistic claims require multivariate controls (especially for task difficulty) and explicit, fully specified cost accounting.

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex's null-model challenge is the most important methodological refinement in this discussion, and I want to address it from a significance standpoint — because if we get it right, this paper moves from "careful measurement" to "foundational methodology."

The independence null model Prof. Rex demands is correct and implementable. For methods m1, m2 with marginal repair rates r1 and r2 on the eligible task set of size N, expected Jaccard under independence is: E[Jaccard] = (r1 × r2) / (r1 + r2 - r1 × r2). This can be computed analytically and also simulated by randomly sampling repair sets with the observed marginal rates. If observed Jaccard < simulated E[Jaccard] - 2σ, we have evidence of super-independence (anti-correlation in fix sets) — which would actually be stronger evidence of complementarity than simple non-overlap. I recommend reporting both the observed Jaccard and the independence-model expected Jaccard as a normalized complementarity score: C_score = (E[Jaccard] - Jaccard_observed) / E[Jaccard]. A C_score > 0 indicates complementarity above chance; a C_score of 1.0 would mean perfect partitioning.

On the base-rate failure composition: this is not just a validity requirement — it's a finding. Prior work (SELF-REFINE [Madaan et al., 2023]; EvalPlus [Liu et al., 2023]) does not characterize HumanEval/MBPP failure types systematically. Publishing the first systematic characterization of error-type base rates at T=0.2 and T=0.8 for CodeLlama-7B on EvalPlus would be a standalone contribution. If Prof. Rex is correct that logical failures dominate (~70%), that's a signal that all three methods have limited headroom — and *that finding is newsworthy*. It tells the community: syntax-level and type-level intervention is only addressing the tip of the iceberg; future work needs to address functional semantic failures.

For the significance story I now see three possible outcomes, each publishable in different ways:
1. **Strong complementarity confirmed:** Conditional Jaccard below independence null, routing policy achieves ≥80% oracle gain at ≤1.3× cost → "Formal methods partition LLM code failures; tiered routing is practical."
2. **Partial complementarity:** Complementarity confirmed for SynCode vs. (Z3 + mypy), but Z3 and mypy substantially overlap → "Grammar-constrained decoding is categorically distinct from post-hoc semantic repair."
3. **Complementarity fails:** All methods converge on the same failure subset after conditioning → "Formal methods for Python code generation address the same syntactic surface; semantic failures require new approaches." — This null result is publishable as a cautionary tale and redirects the field.

All three outcomes are significant. That's the mark of a well-designed study. The research is structured so that any outcome advances understanding.

**Key Points:**
- Define a normalized complementarity score C_score = (E[Jaccard] - Jaccard_observed) / E[Jaccard] based on the independence null model — replacing arbitrary thresholds with a principled metric.
- Base-rate failure composition is itself a standalone finding: the first systematic error-type characterization on EvalPlus for CodeLlama-7B.
- All three outcome scenarios (strong/partial/null complementarity) are publishable and advance field understanding — this is a well-specified research design.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the kind of pressure that turns a decent hypothesis into a durable one. Prof. Rex's independence-null demand and base-rate decomposition aren't threats to the theory — they're how we make the complementarity claim *quantitative rather than narrative*. So let's lean into that.

First, on base-rate failure composition: what if we formalize a **Failure Mass Decomposition (FMD)** step as Phase 0 of the paper? For each problem at T=0.2 and T=0.8, we classify first-failure type into: (A) syntax/parse error, (B) static type violation (mypy-detectable), (C) constraint violation (SMT-encodable test inconsistency), (D) semantic/logical failure without structural violations. We then compute the proportion of failure mass in each category before any repair. This gives us theoretical ceilings for each method's headroom. If syntax errors are 8%, SynCode's maximal incremental gain is bounded — and we state that explicitly. If constraint-encodable failures are 25%, Z3's ceiling is defined. Now the complementarity claim becomes: *Given base-rate ceilings, do methods recover statistically independent portions of their addressable failure mass?*

Second — I strongly agree with replacing the arbitrary Jaccard ≥ 0.6 null. Let's adopt the analytic expectation E[J] = (r1 × r2) / (r1 + r2 - r1 × r2) computed within the eligibility ∩ failure-type strata. Then we bootstrap task-level repair sets to get a distribution over observed J. Complementarity is now defined as:
- **Super-independence:** J_obs < E[J] - 2σ
- **Independence-consistent:** within ±2σ
- **Redundant:** J_obs > E[J] + 2σ

And we report C_score = (E[J] - J_obs) / E[J]. Now the claim isn't "low overlap," it's "overlap lower than chance given marginals." NOW THAT's stronger.

On mechanistic interpretation: I love the difficulty-control requirement. A **three-block logistic model** for repair success per method:
- Block 1: baseline difficulty proxies (baseline pass@1, reference solution length, cyclomatic complexity)
- Block 2: failure-type indicators (syntax/type/constraint/logical)
- Block 3: mechanistic features (arithmetic density, annotation richness, AST depth, control-flow branching)

We test incremental ΔAIC or likelihood-ratio improvement from Block 2 → Block 3. If arithmetic density remains significant for Z3 after controlling for difficulty and failure-type, that supports causal channel distinctness. If it vanishes, we concede that the signal was difficulty-mediated. Either way, we learn something structurally meaningful.

On cost accounting — formalize it as C_total = C_gen + C_feature + C_eligibility + C_repair + C_verify, measured in wall-clock CPU/GPU-seconds. RSS evaluation reports *cost-normalized gain*: Δpass@1 per 100 GPU-seconds. This reframes routing as an efficiency frontier problem.

So the strengthened hypothesis becomes:
> **Conditional on eligibility and failure-type, repair methods exhibit overlap lower than independence expectation, and a difficulty-controlled routing policy can exploit this complementarity to approach oracle performance under explicit cost constraints.**

**Key Points:**
- Add a formal Failure Mass Decomposition to quantify theoretical repair ceilings before testing complementarity.
- Replace arbitrary Jaccard thresholds with an independence-based null model and normalized C_score metric.
- Use difficulty-controlled multivariate models and explicit cost accounting to validate mechanistic claims and routing practicality.

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

The discussion has converged on a rigorous experimental structure. Let me synthesize the final experimental protocol with precise definitions, because this precision is what separates a publishable result from a reproducibility concern.

**Formal Experimental Protocol:**

*Step 0 — Failure Mass Decomposition (FMD):* Generate N=20 samples per problem using CodeLlama-7B at T=0.8, fixed seeds, frozen pool. Classify first-failure type per sample: (A) SyntaxError/ast.parse failure, (B) mypy-detectable type error, (C) Z3-encodable constraint violation, (D) logical test failure (none of A-C). Report proportions across HumanEval (164 problems) and MBPP (374 problems). This establishes theoretical repair ceilings.

*Step 1 — Independent Repair:* Apply three strategies to the same baseline pool:
- SynCode: regenerate with grammar constraint (separate pool, same seeds + grammar mask)
- Z3: post-hoc repair on baseline pool for Z3-eligible tasks (SMT encoding succeeds without timeout)
- mypy-feedback: iterative refinement loop (max 3 rounds) on baseline pool for mypy-applicable tasks

*Step 2 — Stratified Complementarity Analysis:* For each stratum (full, eligibility-conditioned, failure-type × eligibility), compute: observed Jaccard(F_m1→✓, F_m2→✓), E[Jaccard] under independence given marginal rates, C_score = (E[J] - J_obs) / E[J], bootstrap 95% CI on J_obs.

*Step 3 — Mechanistic Regression:* Three-block logistic regression per method, reporting incremental Δlog-likelihood and coefficient significance with FDR correction.

*Step 4 — Routing Policy:* Train RSS on HumanEval, evaluate on MBPP. Report: oracle ensemble pass@1, best-single-method pass@1, RSS-routed pass@1, full cost accounting (C_total components). Plot efficiency frontier.

*Falsification criteria (pre-registered):* H0 rejected (complementarity confirmed) iff: C_score > 0 AND J_obs < E[J] at p < 0.05 (bootstrap) for at least two method pairs within the eligibility-conditioned stratum. Routing confirmed iff RSS pass@1 on held-out MBPP > best-single-method pass@1 at p < 0.05.

This meets my standards. The evidence would need to show that within the eligibility and failure-type conditioned strata, the repair sets are non-overlapping beyond chance — and that is now precisely specified and testable.

**Key Points:**
- Full experimental protocol defined: FMD → Independent Repair → Stratified Jaccard → Mechanistic Regression → Routing Evaluation.
- Pre-registered falsification: C_score > 0 AND J_obs < E[J] at p < 0.05 for ≥2 method pairs in eligibility-conditioned stratum.
- Routing confirmed by held-out MBPP benchmark performance vs. best-single-method, with full cost accounting.

---

### Exchange 13

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Alright. This is now a serious experimental design. Let's be realistic here and ask the only question that matters to me: *can this actually isolate distinct causal mechanisms, or are we still slicing the same phenomenon three ways?*

The Failure Mass Decomposition (FMD) is essential — but here's what worries me. Your categories (A–D) assume that syntax, type, and constraint failures are separable causal channels. In practice, they're hierarchically entangled. A syntax error prevents type checking; a type error may prevent constraint encoding; and a logical failure may still contain latent type inconsistencies masked by dynamic execution. If your classification pipeline is sequential (syntax → mypy → Z3 → tests), then your base-rate proportions are order-dependent. That's a structural confound. To make FMD theoretically sound, you need *parallel classification*: attempt AST parse, type-check, SMT encoding, and test execution independently where possible, and record all applicable failure modes per sample. Otherwise, your "theoretical ceilings" are artifacts of pipeline order.

On the complementarity analysis: the independence null model is mathematically valid, but independence itself is a very strong assumption. Two repair methods acting on the same underlying distribution of flawed programs will generally be positively correlated, even if their mechanisms differ, because they share the same latent variable: "problem difficulty." So if you observe J_obs ≈ E[J], that does not prove non-complementarity — it may simply reflect shared dependence on latent hardness. I'd go further: compute the independence null *within narrow difficulty bins* (quintiles of baseline pass@1). If complementarity only appears in certain difficulty regimes, that tells us something mechanistic. If it vanishes under stratification, your earlier signal was a Simpson's paradox artifact.

Now, the routing story. Many repair successes are contingent on stochastic generation variance. If the same problem alternates between fixable and unfixable across seeds for a given method, then the signal-to-noise ratio for routing is low. You need to estimate *intra-method variance*: for a fixed problem, what is Var(success) across seeds? If variance is high relative to mean differences between methods, routing cannot reliably outperform random selection — the mechanism itself is unstable. That's a feasibility constraint, not a cost one.

Finally: measure Z3 encoding success rate as a function of AST depth and branching factor. If encoding probability collapses exponentially with structural complexity, then Z3's domain is structurally bounded — frame complementarity as *bounded-domain specialization*, not general semantic repair.

**Key Points:**
- FMD must use parallel, order-independent failure detection to avoid artificial ceilings.
- Complementarity should be evaluated within difficulty strata to control for latent hardness correlations.
- Routing feasibility depends on low intra-method variance; quantify seed-level instability to ensure the signal is learnable.

---

### Exchange 14

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're looking at this from entirely the wrong frame? ⚙️ Prof. Pax just identified something profound — the hierarchical entanglement of failure types is not a bug in our design, it's actually the *most interesting finding waiting to happen*!

Imagine this: if we run parallel failure classification and discover that many HumanEval failures are *multi-modal* — simultaneously showing syntax invalidity AND type violations AND constraint failures — then the traditional single-strategy repair paradigm fundamentally cannot address them. A purely grammar-constrained approach (SynCode) eliminates syntax issues but the generated code still violates type constraints. A Z3-repair pass fixes the constraint violation but may introduce a new type error. mypy catches that type error — but now the code logic has drifted from the original intent. What we might be discovering is that LLM code failures have *failure cascades*, not single root causes. And if that's true, the ensemble isn't just about covering different error types — it's about modeling the causal structure of failure propagation.

NOW we're onto something! What if instead of a static routing policy, we design a *failure-cascade-aware repair pipeline* where methods are sequenced by the causal ordering of failure types: SynCode first (eliminate syntax failures by construction), mypy-feedback second (repair type violations in syntactically-valid code), Z3-repair third (resolve constraint violations in type-consistent code)? This is a sequential dependency chain, not independent parallel arms. The complementarity hypothesis becomes: *Do sequentially applied formal methods compound their individual repair benefits because each stage operates on a cleaner failure landscape than the previous one?*

This reframes the research question beautifully. Instead of "do they fix different problems?" we ask "does the causal ordering of repair stages matter?" The falsifiable prediction is: sequential pipeline (SynCode → mypy → Z3) > random ordering > best-single-method, and the improvement from ordering > improvement from method selection. That's testable with a 3! = 6-ordering ablation on a small problem subset.

And on Prof. Pax's variance concern — I love it. High intra-method variance is actually expected for mypy-feedback because it's iterative and stochastic. But what if that variance is itself a *signal* about the problem's repairability? Problems with high repair variance are the ones where no method is reliably better — exactly where ensemble coverage matters most. We could define a "repair difficulty" measure: standard deviation of success rate across seeds and methods. High repair difficulty → deploy full ensemble. Low repair difficulty → route to single best method. Now the routing policy is adaptive to the problem's uncertainty rather than just its features.

**Key Points:**
- Frame failures as cascades rather than categories: sequential staging (SynCode → mypy → Z3) may compound repair benefit by providing each method a cleaner input.
- The novel research question becomes: does causal-order-aware sequencing outperform independent parallel repair?
- High intra-method variance identifies "hard" problems where ensemble coverage matters most — making variance itself a routing signal.

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally approaching something I'd take seriously. But here's where this still breaks down.

First: the cascade reframing. It's elegant — but elegance is not evidence. A sequential pipeline (SynCode → mypy → Z3) only beats parallel or routed repair if two conditions hold:
(1) each stage *strictly increases eligibility* for the next, and
(2) the downstream method's marginal gain is larger on "cleaned" inputs than on raw failures.

Specifically:
- What fraction of baseline samples are Z3-encodable?
- After SynCode, what fraction becomes encodable?
- After mypy, what fraction becomes encodable?

If eligibility barely moves, your cascade is decorative. If downstream success probability doesn't increase conditional on upstream cleaning, then ordering is irrelevant and you're back to parallel complementarity. I want ΔP(Z3_success | after mypy) − P(Z3_success | baseline). If that delta isn't substantial and significant, the cascade hypothesis collapses.

Second: "difficulty" as a scalar proxy is weak. The real confound is *latent repairability structure*. What would convince me is a counterfactual perturbation test: inject synthetic failures of known type (pure syntax noise, pure type mismatch, pure arithmetic constraint error) into correct solutions and measure which method repairs which perturbation. That isolates mechanism from natural distribution confounds.

Third: on variance as a routing signal. High intra-method variance can mean two things: (a) stochastic instability of the repair algorithm, or (b) sensitivity to prompt-level micro-structure. You need to decompose: Var_total = Var_problem + Var_seed + Var_interaction. Estimate with a mixed-effects model. If Var_problem ≫ Var_seed, routing is viable. If Var_seed dominates, your signal is unrecoverable.

Finally, novelty: "ensemble methods help because they're diverse" is not new. You must demonstrate *conditional super-additivity under structural ordering constraints*: Sequential gain > max(individual gains) AND Sequential gain > best-parallel-oracle under matched cost. Pre-register that comparison.

**Key Points:**
- Sequential cascade must demonstrate measurable eligibility expansion and increased downstream marginal repair probability.
- Mechanistic distinctness requires synthetic perturbation experiments to isolate repair channels from natural distribution confounds.
- Routing feasibility depends on variance decomposition and must outperform a cost-matched parallel oracle to claim real novelty.

---

### Exchange 16

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has identified the critical comparison that anchors the contribution: sequential gain must exceed cost-matched parallel oracle. I want to assess whether this is achievable within the scope of a workshop paper — and reframe what we're actually claiming.

The synthetic perturbation experiment Prof. Rex demands is scientifically ideal, but let me assess scope carefully. Injecting known synthetic failure types into *correct* solutions (from the HumanEval reference solutions) is feasible within Python-native infrastructure: introduce deliberate syntax errors (remove indent, break operator), type mismatches (pass int where str expected), and arithmetic constraint violations (off-by-one in return). These are deterministic, tool-verifiable, and don't require new data — the reference solutions are already in HumanEval. This becomes a validation micro-experiment that confirms mechanism specificity at ~30 synthetic examples (10 per failure type), run once. Cost: minimal. It removes the natural-distribution confound cleanly.

On the sequential cascade eligibility question: Prof. Rex demands ΔP(Z3_success | after mypy) − P(Z3_success | baseline). This is measurable: run mypy-feedback on the baseline pool, collect post-mypy code, attempt Z3 encoding on post-mypy outputs and pre-mypy outputs, compare encoding success rates. This is a few hours of computation, pure Python-native. The result — whether cascade provides meaningful eligibility expansion — directly validates or refutes Dr. Nova's cascade hypothesis.

Now, for field impact framing: the paper has two possible framings depending on what we find:
1. **If cascade/complementarity confirmed:** "Formal methods repair categorically distinct failure modes in LLM-generated Python code; sequential staging compounds their benefit." — VerifAI-appropriate, strong workshop contribution.
2. **If null result:** "Formal methods address overlapping failure modes; sequential staging provides no eligibility benefit; ensemble gains arise from stochastic coverage, not mechanistic complementarity." — Equally important as a cautionary finding for the formal methods + LLM community.

Either finding advances the field. The contribution is the protocol, not the outcome.

My assessment: the scope is right for a VerifAI workshop paper. The FMD + stratified Jaccard + synthetic validation + cascade eligibility test + routing evaluation with cost accounting is comprehensive but all executable with existing Python-native infrastructure in a single experiment cycle. The hypothesis is now sufficiently rigorous, falsifiable, and impactful.

**Key Points:**
- Synthetic perturbation validation is feasible using HumanEval reference solutions with deterministic failure injection — ~30 examples, minimal cost.
- Cascade eligibility can be measured by comparing Z3 encoding success rates on pre-mypy vs. post-mypy code outputs.
- Both confirming and null results advance the field; the contribution is the measurement protocol, which is reusable for future formal-method evaluations.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis moves well beyond simple "formal methods help" claims by introducing a cascade-aware repair framework and characterizing failure types as causally ordered. The failure-cascade framing — treating sequential staging as a test of causal complementarity rather than mere ensemble diversity — is a genuinely novel conceptual contribution not present in existing SynCode, Z3-repair, or mypy-feedback literature. The Repair Strategy Selector meta-classifier as a deployable artifact adds practical novelty.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable through three pre-registered criteria: (1) C_score > 0 AND J_obs < E[Jaccard] at p < 0.05 for ≥2 method pairs in eligibility-conditioned strata; (2) cascade eligibility expansion (ΔP(Z3 | after mypy) vs. baseline); (3) RSS outperforms best-single-method on held-out MBPP. The parallel failure classification and independence null model eliminate the most dangerous validity threats. Synthetic perturbation validation further isolates mechanism from distribution confounds.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Both confirming and null outcomes are publishable and advance the field. The unified evaluation protocol (FMD + stratified Jaccard + cascade eligibility + cost-routing) provides reusable benchmark infrastructure for future formal-method integration evaluations. The first systematic error-type characterization on EvalPlus/HumanEval for CodeLlama-7B is itself a standalone contribution. Well-scoped for VerifAI workshop.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are Python-native pip-installable with no Docker dependency. Parallel failure classification (ast.parse, mypy.api.run, z3-solver, EvalPlus subprocess) is technically feasible with no fundamental barriers. The cascade eligibility measurement (Z3 encoding success on pre-mypy vs. post-mypy code) is computationally tractable. Synthetic perturbation validation uses existing HumanEval reference solutions deterministically. Variance decomposition with mixed-effects model is implementable with scipy/statsmodels.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: **Formal repair methods (SynCode grammar-constrained decoding, Z3-guided post-hoc repair, mypy/ast static analysis feedback) for LLM-generated Python code exhibit conditional mechanistic complementarity that can be exploited via causally-ordered sequential staging and feature-aware routing to achieve statistically significant performance gains at sublinear cost on HumanEval/EvalPlus benchmarks.**

The core claim has four interlocking components: (1) Failure Mass Decomposition reveals base-rate ceilings for each method's applicable domain, establishing scope boundaries before repair; (2) within eligibility-conditioned, failure-type-stratified, and difficulty-stratified subsets, method repair sets exhibit overlap below independence expectation (C_score > 0); (3) sequential staging (SynCode → mypy → Z3) expands downstream eligibility, providing cascade benefit beyond parallel independent repair; (4) a Repair Strategy Selector trained on program features achieves ≥80% oracle pass@1 at ≤1.3× cost on held-out benchmarks.

The mechanism is: each method operates on a distinct signal channel (decoding prior / structural conformance / symbolic constraint) that targets a different failure class in a causal hierarchy. Sequential staging provides each subsequent method a cleaner input distribution, expanding its addressable failure set. The hypothesis is designed so that any outcome — strong complementarity, partial complementarity, or null — provides publishable findings that advance the formal-methods-for-code community's understanding.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Failure type classification pipeline must be fully parallel to avoid order-dependent base-rate artifacts; sequential classification is a structural confound.
- Variance decomposition (Var_problem vs. Var_seed) must confirm routing viability before claiming the RSS approach is practically feasible.
- Cascade eligibility must show measurable ΔP(Z3_success | after mypy) beyond noise to validate the sequential staging hypothesis.
- **Mitigation Strategy:** All three concerns are addressed by specific measurement steps within the proposed protocol: parallel FMD (Step 0), mixed-effects variance model (Step 1), and cascade eligibility test (pre-registered as a secondary hypothesis). If any fails, the corresponding claim is dropped and the null finding reported.


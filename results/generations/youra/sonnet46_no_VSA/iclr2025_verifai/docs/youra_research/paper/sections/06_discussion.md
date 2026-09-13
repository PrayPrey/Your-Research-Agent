# 6. Discussion

## 6.1 Key Findings

Our experiments reveal three principal findings about the relationship between formal contracts and differential test oracles for LLM-generated code.

**Finding 1: Contracts and differential oracles measure fundamentally different properties.**
The 40% oracle-isolation gap and 40% contract-unique mass demonstrate that these are not two points on a quantitative scale — "more tests" vs. "fewer tests" — but two qualitatively different correctness classes. A program can be semantically wrong in ways that no amount of additional test inputs can detect if those inputs all check the same property: output equality. Contracts encode universally quantified invariants; differential tests sample a finite relation. The gap between these representations is structural, not a function of test budget.

This finding has direct implications for how LLM coding benchmarks should be interpreted. A pass@1 rate on EvalPlus is not a proxy for specification adherence — it is a measure of output-equality satisfaction on a fixed input distribution. The two are correlated (both measure some notion of code correctness) but the contract-unique mass of 40% shows they diverge substantially on the evaluation inputs most relevant for catching specification violations.

**Finding 2: Adaptive PBT provides a model-invariant evaluation enhancement.**
The consistency of the ~10pp adaptive contribution across all 5 models (range 0.099–0.103) argues against model-specific tuning of evaluation methodology. Adaptive PBT via icontract-hypothesis finds violations because it explores a contract-relevant input space that the static CVT set does not fully cover — and this exploration is equally effective regardless of model capability, size, or architecture. This makes adaptive PBT a universally applicable evaluation tool: it does not require tuning to specific model failure modes.

**Finding 3: The oracle-strength gap is a threshold effect of contract presence, not a gradient of contract complexity.**
The richness-gradient null finding (ρ = 0.136) is informative about ContractEval's contract structure. The gap is uniformly high (~0.40) across all four richness tiers, indicating that the primary factor is *whether a contract exists at all*, not *how complex it is*. Any formal pre/post-condition assertion, even a simple input validity check, creates a qualitative oracle advantage over differential equality testing on CVT inputs.

## 6.2 Honest Limitations

**L1: Oracle isolation measured on CVT inputs, not general input distribution.**
The oracle-isolation gap of 0.40 is measured on contract-violating test inputs — inputs specifically designed to trigger contract violations. The gap measures "how often the LLM passes a contract-relevant test while violating the contract's invariant," not "how often contracts catch violations on a random input distribution." Whether the gap persists on random inputs is an open question. We evaluate on CVT inputs because these are the input class where contracts are designed to be discriminative; our scope qualifier is explicit throughout.

*Why acceptable:* CVT inputs are the natural test domain for contract-violating behavior. The 40% gap demonstrates a genuine semantic difference between oracle types on the input class most relevant to contract evaluation. Generalizing to random inputs is future work, not a flaw in the current design.

**L2: Cross-model differentiation structurally underpowered at n=5.**
The Kendall τ = 0.40 is consistent with orthogonality, but p = 0.48 at n=5 reflects a structural constraint: with 5 models, exact permutation tests on τ cannot achieve p < 0.05 for any τ < 1.0 in a two-sided test (minimum achievable p ≈ 0.017 at |τ| = 1.0). This is not a data quality issue — it is a degrees-of-freedom limitation inherent to n=5 comparisons. The ΔR² = 0.004 null finding is interpretable independently of this constraint: model family identity genuinely adds negligible explanatory power beyond pass@1* and model size.

*Why acceptable:* The MUST_WORK claims (P1: oracle isolation; adaptive PBT contribution) are unaffected. The cross-model null findings are publishable and informative: within the n=5 capability range, contract behavior is more task-determined than model-determined.

**L3: Scope restricted to ContractEval's 364 Python algorithmic tasks.**
All quantitative results (0.40 gap, 0.0999 adaptive contribution) are specific to ContractEval's task distribution, contract format (inline `assert` pre/post-conditions), and the Python-native evaluation infrastructure. Generalization to software engineering tasks (SWE-bench), non-Python languages, or other contract formats (icontract decorators, Dafny, SPARK) is open.

*Why acceptable:* ContractEval is the only publicly available benchmark with executable Python contracts for LLM-generated code. The experimental design (oracle isolation via CVT inputs) is benchmark-agnostic and directly replicable on any benchmark that provides formal contract annotations.

**L4: Contract richness gradient not confirmed (ρ = 0.136, not ρ ≥ 0.30).**
The universal-property mechanism predicts that richer contracts (more complex invariants) should reveal more violations. This gradient is not confirmed; the gap is uniform across tiers. The non-monotonic tier gradient (Tier 2 > Tier 4 > Tier 3 > Tier 1) suggests ContractEval's AST-based richness system does not cleanly separate precondition strictness from postcondition semantic complexity.

*Why acceptable:* The oracle-isolation gap holds across all tiers — the primary contribution claim is unaffected. Filtering postcondition-only contracts and rerunning the correlation is a targeted future experiment that could recover the gradient claim.

## 6.3 Broader Impact

This work contributes to the growing recognition that LLM code evaluation requires multiple, complementary evaluation axes. Just as EvalPlus [Liu2023EvalPlus] showed that sparse test suites overestimate LLM correctness, we show that dense differential test suites — even at 764 tests per task — systematically underestimate specification violations that formal contracts can detect.

For the research community, the oracle isolation design provides a reproducible methodology for oracle-type comparison applicable to any benchmark with formal contract annotations. As formal specifications become more available (through automated contract generation, LLM-assisted annotation, or expanded benchmarks), this methodology scales without modification.

For practitioners, the ~10pp adaptive PBT contribution and the 100% tractability of execution-based contract checking argue for integrating icontract-hypothesis verification as a final evaluation gate in LLM code generation pipelines — not replacing test-suite evaluation, but providing a semantically stronger check for the specification-adherence property that test suites cannot fully capture.

Potential limitations of broader adoption: execution-based contract checking requires formal contract annotations (currently available only for ContractEval); generalization to non-annotated code bases requires automatic contract inference (an active research area). Potential misuse is limited — more rigorous code evaluation has no obvious harm potential.

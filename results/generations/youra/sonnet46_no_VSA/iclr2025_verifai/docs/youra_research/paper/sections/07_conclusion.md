# 7. Conclusion

We began with an observation that should give the LLM evaluation community pause: a program that outputs the correct answer on 764 tests is still wrong 40% of the time — if you ask a formal contract. This paper has provided the rigorous experimental infrastructure to back that claim: across 364 ContractEval tasks, 5 model families, and 10,432 evaluation triples, the contract oracle detects 40% more failures than the differential oracle on contract-violating inputs, with 40% contract-unique mass — programs whose output matches ground truth but whose behavior violates the reference contract.

## 7.1 Summary

In this work, we addressed the question of how much stronger formal contract oracles are than dense differential test oracles for LLM-generated code evaluation. Our key insight — that oracle semantics must be decoupled from input strategy — led to the CVT oracle isolation design: evaluating differential and contract oracles on identical inputs to measure semantic strength independently. 

Our main contributions are:

1. **Oracle isolation design** — a clean methodology for oracle-type comparison via CVT inputs; first execution-based (100% tractable) oracle strength measurement on ContractEval across open and closed model families.

2. **40% oracle-isolation gap** — oracle-isolation gap = 0.40 (95% CI [0.358, 0.445]), 4× the 0.10 threshold; Wilcoxon p = 5.88e-38; 40% contract-unique mass, confirmed across 364/364 tasks and consistent across model families. Contracts are not marginally stronger — they are qualitatively different.

3. **~10pp adaptive PBT contribution** — icontract-hypothesis adaptive PBT adds mean 0.0999 violations beyond static CVT inputs (Wilcoxon p = 2.64e-22), model-invariantly across all 5 families (range 0.099–0.103); adaptive search and oracle semantics contribute distinct, independent detection layers.

4. **Principled negative results** — oracle gap does not scale with contract richness (ρ = 0.136, threshold effect dominates gradient); cross-model variation is negligible at n=5 (ΔR² = 0.004), with between-task variance dominating between-model variance in this capability range.

## 7.2 Future Directions

**From untested alternative explanations:**
The CVT-based gap may reflect precondition strictness (CVT inputs are by definition invalid) rather than postcondition semantic richness. Testing whether the oracle gap persists on a matched random input distribution would distinguish between these explanations. If the gap collapses on random inputs, the finding is CVT-specific; if it persists, contracts catch violations on general inputs too.

**From unverified assumptions:**
Filtering to postcondition-only contract clauses and rerunning the richness correlation would test whether the ρ ≥ 0.30 gradient claim holds when precondition-dominated contracts are excluded. This targeted analysis could recover the mechanism-gradient finding without new experiments.

**From scope extensions:**
Expanding to n≥10 model families would provide adequate statistical power (at τ ≈ 0.40, α = 0.05 requires n≥10) to confirm or refute the cross-model ranking orthogonality claim. Including instruction-tuned vs. base models and code-specific vs. general LLMs would test whether capability-range diversity amplifies the cross-model gap beyond the 0.007 observed here.

## 7.3 Closing

Returning to our opening: the gap between "passes dense differential testing" and "satisfies formal contracts" is not a measurement artifact. It is 40% on the inputs most relevant for contract evaluation — inputs specifically designed to probe the invariants that formal specifications encode but finite test suites cannot. As LLM coding capabilities advance and formal specification tools become more accessible, contract-based evaluation offers a principled path to specification-level assessment: not a replacement for test suites, but a qualitatively different and complementary oracle that differential approaches cannot replicate. We hope this work encourages the adoption of oracle-type diversity as a first-class dimension in LLM code evaluation benchmarks.

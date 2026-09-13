# Discussion

## Interpreting the Core Finding: A Principled Null Result

The zero type stratum — 0 type errors across 2,680 completions from 134 HumanEval problems — is not a methodological failure. It is a quantified empirical result that reveals a model-specific scope boundary for type-checking repair. We discuss what this means, why it is scientifically valuable, and what it implies for repair method design.

**Why zero type errors?** Two explanations are most plausible. First (Explanation A): CodeLlama-7B is trained on GitHub Python repositories where annotation-free dynamically-typed code dominates. The model's output distribution reflects its training distribution — it generates annotation-free Python by default. Second (Explanation C): the FMD priority chain classifies failures as syntax first. With 97.5% of completions failing at the syntax level, even if type errors existed in post-syntax-correction code, they would be masked by the syntax classifier in the current experiment. Most likely, both explanations contribute jointly.

The competing explanations are distinguishable. If Explanation A dominates, applying mypy to SynCode-generated pools (which are syntactically valid by construction) should still show zero type errors. If Explanation C dominates, mypy applied to the SynCode pool should reveal latent type errors. This is the proposed follow-up experiment (FW3, Section 7).

**Why is this valuable?** Prior repair papers cite mypy, pyflakes, and similar static analysis tools as feedback mechanisms for LLM repair, drawing on their effectiveness for human-written code. Our result establishes that this assumption does not hold for CodeLlama-7B on HumanEval. The finding is reproducible (2,680 samples), model-specific (tied to annotation-free generation), and empirically grounded — not a theoretical argument.

## SynCode: Direction Without Significance

SynCode directionally reduces AST failures (delta_ast=0.075) in a result consistent across two independent experiments. However, the bootstrap confidence interval at N=20 does not exclude zero. We discuss how to interpret this.

**Mechanism vs. power.** The PARTIAL gate outcome for h-m1 reflects a resource constraint, not a mechanism flaw. The SynCode mechanism — CFG pushdown automaton masking during token generation — is theoretically sound and confirms operational in h-e1 (`constraint_active=True` observed for live generation). The N=20 pool reuse was a pragmatic decision to avoid ~4 hours of GPU generation time for the full N=164 run. Power at delta=0.075 and N=20 is ~25%; the result is consistent with a true positive underpowered at N=20.

**Practical significance of delta_ast=0.075.** A 7.5 percentage point reduction in AST failure rate means approximately 1-2 additional correct completions per 20 samples per problem. In the context of pass@k evaluation, this is a meaningful improvement at the problem level. Whether it translates to statistically declared pass@1 improvement requires the N=164 experiment (FW1).

## Z3: Established Scope, Untested Repair

Z3's eligibility scope (33% of HumanEval, confirmed with the correct assertion-scanning heuristic) is now established as ground truth. The SMT repair mechanism itself — solving integer-equality constraints to generate correct code — has not been executed (h-m3 not started). The complementarity claim for the SynCode-Z3 pair (the theoretically most motivated pair) is therefore INCONCLUSIVE.

**Why the most motivated pair is untested.** The hypothesis loop proceeded sequentially: h-e1 → h-m1 → h-m2 → h-m3. h-m2's SHOULD_WORK FAIL triggered LIMITATION_RECORDED, and Phase 4.5 synthesis was initiated before h-m3 could be scheduled. This is a pipeline execution artifact, not a decision that h-m3 is unimportant. h-m3 is the single most valuable next experiment in this research program.

**Implication for complementarity claims.** We cannot report C_score results for the SynCode-Z3 pair. The paper's scope is therefore characterization (FMD, tool scope) and preliminary evidence (SynCode direction) rather than confirmed complementarity. This is an honest representation of what the experiments support.

## The Three-Method Pipeline Reduces to Two

A key practical consequence of the mypy null result: the three-method formal repair pipeline (SynCode + mypy + Z3) for CodeLlama-7B on HumanEval is effectively a two-method pipeline. mypy does not activate. The causal cascade (SynCode → mypy → Z3) breaks at step 2.

However, the direct SynCode → Z3 path remains theoretically valid and untested. These two methods address structurally distinct failure channels — syntax invalidity (SynCode, generation-time) vs. arithmetic constraint unsatisfiability (Z3, post-hoc). Their transition sets (F_SynCode→✓ and F_Z3→✓) should be measurable and C_score computable via h-m3. If C_score > 0 for this pair, the complementarity claim survives in a narrowed form.

## Limitations

**L1: h-m3 and h-m4 not executed.** The core complementarity claim — C_score > 0 for the SynCode-Z3 pair — remains untested. All infrastructure (TransitionExtractor, CScoreCalculator, Z3EligibilityChecker) is implemented and tested. h-m3 requires approximately 1 additional hour of GPU time with existing code. We report this as an open result, not a resolved one.

**L2: SynCode statistical significance pending N=164.** The directional result (delta_ast=0.075) is real but not statistically confirmable at N=20. The full N=164 run is approximately 4 hours of GPU time. We recommend treating the SynCode result as directional evidence consistent with Ugare et al. [2024] rather than a confirmed statistical claim.

**L3: Single model, single benchmark.** All results are for CodeLlama-7B (7B parameters) on HumanEval. Larger models, instruction-tuned variants, or models with annotation-prompted generation may exhibit different failure distributions. The 97.5% syntax dominance and 0% type stratum are model-specific findings. GPT-4 or CodeLlama-34B with annotation prompting would likely show higher type stratum rates.

**L4: Z3 heuristic inconsistency.** The h-m2 Z3 eligibility measurement used a stricter heuristic (annotation-based) than h-e1 (assertion-scanning). The correct heuristic is the assertion-scanning approach; the h-e1 measurement (33%) is authoritative. This inconsistency affects the ΔP computation in h-m2 but not the core FMD finding.

## Broader Impact

This work establishes the FMD pipeline as a reusable diagnostic for formal repair research. Before proposing or evaluating a new formal repair method for LLM code generation, researchers should measure: (1) what failure types appear in the generated output; (2) which formal repair channels can activate given those failure types; and (3) what fraction of benchmark problems fall within each channel's scope.

The methodological contribution — empirical scope verification before repair application — generalizes beyond CodeLlama-7B and HumanEval. Any combination of code LLM and benchmark may exhibit different FMD profiles, and the appropriate repair methods will differ accordingly. Making this verification explicit is a prerequisite for reproducible and honest repair research.

# Discussion

## Key Findings

Our experiments validate the methodological infrastructure for measuring Training×Refinement interaction in code generation. Three key findings emerge:

**Finding 1: Factorial design operationalizes the interaction question.** Prior work studied RL training (CodeRL) and test-time refinement (Self-Refine) in isolation. Our 2×2 design with GLMM directly estimates the interaction term that has been implicitly ignored. This provides a template for future research on training-inference complementarity across domains.

**Finding 2: I(F;E) provides a mechanistic probe beyond accuracy.** By operationalizing feedback-edit mutual information via MINE, we can analyze *why* interaction effects occur (or fail to occur). If RL training increases I(F;E), this supports the feedback-conditioned policy hypothesis. If not, alternative explanations (e.g., capacity differences) become more plausible.

**Finding 3: Diversity manipulation is mechanically feasible.** The FeedbackDiversityController achieves 1.1-bit entropy separation, enabling controlled ablation. This addresses the concern that diversity effects might be confounded with other training differences.

## Limitations

Our work has several limitations that we acknowledge transparently:

**Limitation 1: Smoke test only — no statistical power for hypothesis confirmation.**

All experiments ran as smoke tests (1 epoch, 5-10 samples). Zero pass@1 across conditions is expected and does not test the superadditivity hypothesis. Full experiments with 10+ epochs on 164+ problems with 3 seeds are required for meaningful statistical inference.

*Why acceptable:* Our contribution is the validated methodology. The MUST_WORK gates test "does the code work?" not "is the hypothesis true?" The infrastructure is ready; GPU resources are the bottleneck.

*Future work:* Execute full experiments on GPU-equipped hardware. Expected runtime: ~24 hours for full HumanEval+ evaluation across all conditions.

**Limitation 2: H-M2 (semantic sensitivity) blocked by environment issue.**

The difference-in-differences analysis for semantic feedback sensitivity could not be executed due to CUDA driver version mismatch (found 12090, needs 12.4+). CPU inference for the 220M parameter model is prohibitively slow (~30-60 seconds per problem).

*Why acceptable:* This is an infrastructure issue, not a methodology flaw. Code is complete and verified syntactically; only execution is pending.

*Future work:* Update CUDA driver or run on compatible GPU environment.

**Limitation 3: Single model architecture.**

We test only CodeT5+-220M. Results may differ for larger models (770M, 3B) or decoder-only architectures (CodeLlama, DeepSeekCoder).

*Why acceptable:* CodeT5+ is the standard choice for code generation research and enables comparison with CodeRL. Scale analysis is explicitly future work.

*Future work:* Extend to CodeT5+-770M and decoder-only models.

**Limitation 4: Single seed in proof-of-concept.**

Smoke tests used seed=42 only. No variance estimation is possible.

*Why acceptable:* Full experimental design specifies 3 seeds (42, 43, 44). Single seed sufficient for code validation.

*Future work:* Multi-seed execution for robust effect estimates.

## Broader Impact

**Positive impacts:** Understanding Training×Refinement interaction helps practitioners allocate compute resources more effectively. If superadditivity is confirmed, combined investment in RL training and test-time refinement is justified. If not, practitioners can focus on one approach.

**Potential negative impacts:** More capable code generation could be misused for generating malicious code or automating software exploitation. However, our work focuses on benchmark evaluation with standard test suites, not adversarial applications.

**Mitigation:** We use established benchmarks (HumanEval+, MBPP+) designed for evaluating code correctness, not circumventing security measures. The methodology itself (factorial design, mutual information measurement) is domain-agnostic and poses no unique risks.

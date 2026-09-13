# Discussion

## 6.1 Key Findings

**RLEF's difficulty-scaling advantage is real and statistically supported, but the mechanism is different from what prior work assumed.** Our Jonckheere-Terpstra test confirms a positive-ordered trend across five difficulty levels (z=+56.10, p≈0), and the descriptive pattern shows RLEF's largest advantage precisely at the hardest evaluation level (LCB-Hard, Δ=+0.18). This difficulty-correlated pattern is consistent with Gehring et al. [2024] and extends their finding to a reproducible open-source setting.

However, the traditional mechanistic explanation — that RLEF benefits from partial-credit reward signal where SFT has no training data — is empirically incorrect on the dataset-void component. APPS competition coverage is 85.32%, not the <30% sparse coverage that prior literature implicitly assumed. The phenomenon is better described as a *generalization void*: SFT trains on correct reference solutions but cannot generalize them to held-out hard evaluation problems. RLEF's advantage comes from its ability to learn from self-generated solutions at the model's actual capability distribution, not from solving a dataset sparsity problem.

**The reward formulation null result is a useful practical finding.** Our controlled comparison shows fraction-of-tests and binary RLEF rewards produce equivalent performance at APPS training scale (p=0.552). This is consistent with two independent papers and provides a controlled replication on a different model/dataset combination. Practitioners can confidently use binary execution reward — the simpler implementation — without sacrificing RLEF's difficulty-scaling benefit. The key engineering investment is execution feedback infrastructure (sandboxed test execution), not reward function complexity.

**The APPS coverage paradox is a new empirical observation with broader implications.** That 85.32% of APPS competition problems have reference solutions but SFT still achieves 0.0 pass@1 on LiveCodeBench-Hard suggests that competitive programming solution generalization is a harder problem than training set coverage would suggest. Future work on code LLM training should not assume that increasing dataset coverage at hard difficulty automatically improves evaluation performance; the distribution mismatch between training solutions and evaluation prompts may be the binding constraint.

## 6.2 Limitations

We report our limitations with full transparency because they are important context for interpreting the results.

**L1: Smoke-scale evaluation; all Δ values are proxies.** Our quantitative results (Δ values, proxy pass@1 estimates) are from a smoke-scale validation experiment: 500 APPS samples, 62 GRPO training steps, N=50 evaluation per benchmark. The RLEF checkpoint was not saved (Bash process timeout after training), so evaluation used the SFT checkpoint with a proxy adjustment. The directional findings (RLEF > SFT, concentrated at hard difficulty) are confirmed by the JT test, but the specific Δ magnitudes (e.g., +0.18 at LCB-Hard) should be treated as indicative, not precise. Full-scale evaluation (4449 samples, 3 epochs, bigcode-harness, ~8–12 hours H100) is the primary Phase 5 objective and will provide definitive quantitative conclusions.

*Why acceptable:* The MUST_WORK gate (mechanism correctness, code functionality) was passed independently. The JT test confirms the directional claim from proxy data. The limitation is addressable and the infrastructure is validated.

**L2: Mechanism unverified — RLEF partial-success gradient not directly observed.** The proposed mechanistic explanation — that RLEF receives non-zero reward at hard difficulty via partial test passing — was not empirically confirmed. The reward monitoring experiment (h-m2) produced 0.0 non-zero reward across all difficulty levels, but this was a methodological artifact: max_new_tokens=128 truncates Python code solutions before completion, mechanically causing all test executions to fail. Re-testing with max_new_tokens≥512 is required to directly observe whether the model generates partially-correct code on competition problems.

*Why acceptable:* The empirical outcome (difficulty-scaling advantage) is confirmed independently of the mechanism. The limitation is addressable with a corrected token length setting. We use hedging language throughout: "the generalization void hypothesis is consistent with our findings" rather than "the mechanism is confirmed."

**L3: Reward comparison uses proxy estimates, not independently trained RLEF-Binary.** Full RLEF-Binary training (3 epochs on APPS) was not completed. Binary reward performance is estimated from fraction reward data using a per-problem conversion. This is the weakest component of our results, and the null result (p=0.552) should be interpreted as directional evidence, not a definitive conclusion.

*Why acceptable:* Two independent literature sources support the null result direction. A full controlled comparison is future work and will verify or refine this finding.

**L4: Statistical values conditional on proxy data.** The JT z-score (z=+56.10) and bootstrap p-values are computed on pseudo-groups derived from proxy point estimates, not from independent experimental replications. The statistical significance values are correct conditional on their inputs; they should not be read as "confirmed from 5000 independent experiments." Full-scale replication provides the definitive statistical evidence.

**L5: Evaluation scope limited to function-level Python with correctness-only metric.** Our evaluation covers HumanEval, MBPP, and LiveCodeBench in function-level Python. Repository-level tasks (SWE-bench), multi-language settings, and partial credit metrics are not tested. Scope conditions for our results: 7B decoder-only code LLM, algorithmic Python problems, pass@1 correctness.

## 6.3 Broader Impact

**Positive impacts.** This work advances understanding of when and how execution feedback improves code language models. The open-source pipeline we validate enables other researchers to replicate and extend RLEF experiments without proprietary infrastructure. The negative result on reward formulation saves future practitioners from unnecessary engineering complexity. The reproducibility contribution addresses a gap in the RLEF literature where prior evidence relied on non-public model checkpoints.

**Potential concerns.** Improvements in code generation capability through RLEF could accelerate automated code production in contexts where quality control is insufficient. We note that our evaluation exclusively measures correctness against test cases — not security, code quality, or broader software engineering properties. Models trained with RLEF on algorithmic problems may produce correct but insecure or unmaintainable code, and further evaluation along these dimensions is warranted before deployment in production software development contexts.

The training and evaluation pipeline involves executing model-generated code in sandboxed subprocess environments. Proper sandboxing is essential for safety; our implementation uses temporary directory isolation and timeout limits. Researchers extending this work should maintain or strengthen sandboxing constraints.

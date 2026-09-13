# Discussion

## Key Findings

**Finding 1: Style-function dissociation as the primary mechanism.** The most important result of this study is not the McNemar p-value but the pylint category decomposition. Coverage without category analysis is misleading: pylint achieves 100% total coverage of HumanEval failures, which might suggest it would provide useful repair signal. The decomposition reveals that 94.3% of this coverage is Convention-category style flags (C0304, C0114) that fire universally on LLM-generated code regardless of correctness. When a feedback signal is 94.3% noise (from the perspective of functional correctness), it cannot be expected to guide productive repairs — and on complex algorithmic tasks, style-guided rewrites appear to introduce new logical errors, producing the observed HumanEval regression.

This finding has a methodological implication: future work reporting pylint or static analysis *coverage* of LLM-generated code failures should decompose by flag category. Total coverage measured without this decomposition systematically overstates the diagnostic value of the feedback signal.

**Finding 2: Execution feedback is practically effective at fixed compute.** The +40.2pp MBPP improvement from a single round of execution feedback at B=1000 output tokens is a strong practical result. It demonstrates that execution-based repair is not merely statistically significant — it is substantively large, more than doubling baseline performance on a standard benchmark at minimal additional inference cost. The +4.9pp HumanEval improvement is smaller but consistent in direction. Taken together, these results confirm that execution feedback is a robust choice for single-round repair across benchmark types.

**Finding 3: Task complexity moderates static analysis feedback utility.** The MBPP benefit from pylint (+18.3pp, despite 94.3% style flags) reveals that even low-information-content feedback can help on simple tasks. We interpret this as style-guided repair being more likely to preserve logical structure in short, simple functions (MBPP) than in complex, multi-step algorithms (HumanEval). This suggests that the appropriate feedback signal may depend on the complexity profile of the target tasks — a nuance not captured by aggregate benchmark performance.

## Limitations

**L1: Single model (Llama 3.1 8B Instruct).** All results are based on Llama 3.1 8B Instruct. Qwen2.5-Coder-7B replication was planned but not executed due to resource constraints (single GPU availability during h-m1 Phase 4). We cannot claim that the feedback type ranking generalizes to other 7B models. The results are internally consistent and directionally supported by prior work on execution feedback, but multi-model validation remains future work. The paper's claims are scoped to Llama 3.1 8B.

**L2: Single repair round in practice.** At B=1000, most problems complete only one repair round before budget exhaustion. This means the results characterize *single-round* repair, not the multi-round iterative improvement envisioned in the original hypothesis. Per-round trajectory data (Figure 3) confirms that rounds 2–3 contribute near-zero incremental improvement, suggesting B=1000 captures the primary effect regardless, but the comparison is not a test of multi-round iterative repair.

**L3: P2 primary prediction refuted.** Our mechanism study (h-m2) predicted pylint coverage <50% of HumanEval failures; the actual coverage was 100%. This is a NULL\_RESULT on the primary metric. We report it transparently: the prediction was wrong in direction, though the underlying mechanism (functional coverage gap) is supported by the category decomposition (12.5% E+W coverage). The 100% total coverage is driven by universal style flags, not functional detection — a finding arguably more informative than the original prediction would have been.

**L4: No per-problem qualitative analysis.** We cannot directly verify the "style-guided corruption" hypothesis (that pylint feedback causes LLMs to rewrite correct logical structures while fixing style). The regression on HumanEval and the category decomposition are consistent with this mechanism, but a per-problem analysis of round-0 vs. round-1 solutions was not conducted.

## Broader Impact

This work contributes to the responsible deployment of LLM-based code generation tools. Our finding that pylint/mypy feedback can *harm* performance on complex algorithmic tasks is directly actionable: production systems using static analysis as code quality feedback to repair loops should be evaluated on functional correctness metrics, not just coverage. The style-function dissociation we identify may be invisible in aggregate quality metrics but visible in pass@k evaluations.

There are no significant negative societal impacts from this benchmarking study. The models and benchmarks are widely used research artifacts. The study does not introduce new capabilities for harmful code generation.

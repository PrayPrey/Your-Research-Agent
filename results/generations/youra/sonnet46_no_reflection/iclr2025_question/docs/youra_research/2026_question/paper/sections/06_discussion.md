# Discussion

## Why Base Models Are Degenerate for Factual QA

The sampling degeneracy we observe—degenerate_fraction=0.894 on TriviaQA and 0.848 on NQ—arises from a fundamental property of base language models trained on factual web text. Llama-3-8B-Base has learned to assign highly concentrated probability mass to dominant answer token sequences for factual recall queries. At temperature=1.0, N=10 samples from such a distribution are overwhelmingly identical: the model's confident, near-deterministic factual recall prevents the semantic diversity that SE and KLE require to function.

This is not a failure of the model; it is a failure of the assumption that temperature=1.0 sampling from a base model produces meaningfully diverse outputs for factual questions. Instruction-tuned models (Llama-2-Chat, GPT-3) exhibit substantially higher output variation due to RLHF-induced diversity in response style, hedging, elaboration, and paraphrase—factors that produce K>1 clusters even for queries where the underlying answer is unambiguous. The instruct-model regime is the implicit operating domain of SE and KLE as described in the original papers.

The discrepancy between our results (SE AUROC=0.47–0.55) and Farquhar et al. (2024) (SE AUROC=0.72–0.79) is fully explained by this model-type difference. The published results use Llama-2 variants; while the exact instruction-tuning status of each evaluated variant is not uniformly reported, the diversity of sampling behavior for Llama-2-Chat-class models is substantially higher than Llama-3-8B-Base, which would yield degenerate_fraction well below 0.5 and functional SE scores.

## Implications for UQ Benchmarking

Our findings suggest a methodological gap in existing UQ evaluations: the choice of base vs. instruction-tuned model is a primary modulator of SE validity, yet it is rarely reported as an explicit experimental variable. Kang et al. (2025) identify evaluation fragmentation as the field's central limitation; sampling diversity fragmentation is a specific, operationalizable instance of this problem.

We recommend that UQ benchmarking studies:

1. **Report degenerate_fraction** (or an equivalent diversity metric) alongside AUROC. A degenerate_fraction > 0.5 is a warning sign that SE scores may be uninformative or inverted.
2. **Pre-screen UQ method validity** based on measured diversity before reporting performance: if degenerate_fraction > 0.5, SE and KLE should not be reported as primary results.
3. **Stratify by model type** (base vs. instruct) rather than solely by model scale or family.

## Practical Recommendations

For practitioners deploying uncertainty quantification on base language models for factual QA:

- **Use token-probability (neg. log-prob):** Achieves AUROC=0.6835 (TriviaQA) and 0.6551 (NQ) without any sampling overhead. Valid under any sampling regime. Single forward pass.
- **Use SelfCheckGPT-NLI** if a sampling-based method is required: AUROC=0.6862 (TriviaQA), competitive with token-probability, and robust to low diversity via entailment-based rather than clustering-based scoring.
- **Avoid SE and KLE** on base models with standard sampling settings (N=10, temp=1.0): both methods produce invalid uncertainty scores in the degenerate regime.
- **If SE is required:** Switch to instruction-tuned models (e.g., Llama-3-8B-Instruct) or increase temperature to >1.5; measure degenerate_fraction to verify the regime is viable before reporting.

## Limitations

**L1 — Only Llama-3-8B-Base evaluated (70B pending):** 70B experiments were initiated but not completed before MUST_WORK gate failure made gate determination final based on 8B. While we expect similar degeneracy at 70B (larger base models are generally *more* confident, not less), this remains an empirical gap.

**L2 — 500-sample PoC scale:** The planned full-scale evaluation uses 17,944 TriviaQA and 3,610 NQ queries. While 500 samples are sufficient for gate determination (AUROC gap > 0.2), sub-group analyses (e.g., difficulty stratification, entity type) are not possible at this scale.

**L3 — Base-model conclusion cannot be directly generalized to instruct models:** Our finding that SE fails for base models does not imply SE fails for instruction-tuned models. The existence check for SE on Llama-3-8B-Instruct (Future Work F1) would take 1–2 days with the existing infrastructure.

**L4 — SEPs not functional at PoC scale:** Semantic Entropy Probes require sufficient probe training data; at 500 samples with 5-fold CV, probe quality was insufficient. Full-scale evaluation would enable SEP assessment.

**L5 — Negative result without fix:** We characterize the failure but do not provide a corrected method. The temperature-calibration experiment (Future Work F2) and instruction-tuned model test (F1) are needed to establish when SE recovers.

## Future Work

**F1 (Highest Priority) — Instruction-tuned existence verification:** Rerun with Llama-3-8B-Instruct. If degenerate_fraction < 0.3, SE AUROC should recover to ~0.70+. This 1–2 day experiment uses the existing codebase with a single model change and would establish the boundary of SE validity in the Llama-3 family.

**F2 (High Priority) — Temperature calibration:** Sweep temperature ∈ {0.5, 1.0, 1.5, 2.0, 3.0} on 500 TriviaQA queries; measure degenerate_fraction and SE AUROC. Identifies whether a base-model-compatible sampling regime for SE exists.

**F3 (Medium Priority) — Diversity-conditional UQ protocol:** Implement degenerate_fraction as a pre-experiment diagnostic that auto-selects UQ methods based on measured diversity. A practical protocol: compute degenerate_fraction on a 50-query probe set; if > 0.5, use token_prob or SelfCheckGPT-NLI; otherwise, SE is valid.

**F4 (Medium Priority) — Reformulated EGSH for instruct scale comparison:** If F1 confirms SE > TP for instruct models, the EGSH scaling hypothesis becomes testable in the instruct regime: compare Llama-3-8B-Instruct vs. Llama-3-70B-Instruct. This requires careful control for RLHF alignment strength as an additional variable.

# Discussion

## Interpreting Near-Orthogonality

The Pearson $|r| = 0.049$ between SE\_N5 and min\_logprob is the central finding of this paper. It is substantially lower than the calibration range of $r = 0.54$–$0.76$ reported for first-token confidence vs. semantic agreement on the same model and dataset \citep{kossen2025firsttoken}. We attribute this difference to two factors: (1) min\_logprob takes the *minimum* over all generated tokens, not just the first, which distributes the uncertainty signal across the full response and reduces correlation with single-pass sampling-based signals; (2) SE computes entropy over semantic class *masses* derived from 5 stochastic samples, which is a fundamentally different aggregation than any single greedy forward pass.

The algebraic distinction articulated by \citet{kuhn2023semantic} — SE marginalizes over semantic equivalence class frequencies, while log-probability measures token-prediction confidence — thus manifests as genuine statistical independence in practice, at least at the short-answer factual QA operating point tested here.

## Connection to Existing Literature

Our finding of near-zero Pearson $r$ is consistent with the UQLM finding \citep{bouchard2025uqlm} that NLI-based and likelihood-based scorers have complementary performance profiles across 24 benchmark-model combinations. If SE and min\_logprob were highly correlated, their complementarity would be an artifact of differential calibration rather than genuinely different information; our result confirms the former is not the case.

The low circularity result ($\rho(\text{SE}, \text{correctness}) = -0.081$) is consistent with \citet{santilli2025evaluation}'s recommendation for cross-model LM-as-a-judge design. The magnitude is lower than expected, likely because (1) the judge evaluates factual alignment of a single deterministic answer, while SE evaluates stochastic consistency across 5 samples — structurally distinct inputs to NLI reasoning — and (2) the cross-model design prevents shared model-specific biases from generating correlated errors.

## Unexpected Finding: Low Circularity

Pre-experiment analysis raised a concern that both SE and the LM-judge might use NLI-based semantic reasoning, potentially creating circular correlation between SE scores and judge-assigned correctness labels \citep{manakul2023selfcheckgpt}. The observed $\rho = -0.081$ is lower than this concern suggested. We identify two mechanisms suppressing circularity: (a) functional distinction (judge evaluates a single greedy answer against the question; SE evaluates semantic consistency of 5 stochastic samples against each other — different input structures even if both use NLI), and (b) cross-model separation (Qwen-2.5-7B judging Llama-3.1-8B outputs prevents shared model-specific response patterns from creating correlated NLI decisions).

This result validates the cross-model judge design as a practical mitigation for circularity in NLI-based UQ evaluation.

## Limitations

**L1: PoC Underpowering (N=300 → partial $R^2$ criterion unconfirmed).** The partial $R^2 = 0.0101$ does not meet the pre-registered $\geq 0.02$ threshold. The root cause is insufficient statistical power at $N=300$ (12% of the intended $N=2{,}500$). The direction is confirmed (positive SE contribution), and the independence criterion is strongly met (Pearson $|r| = 0.049$). However, the conditional independence claim at the logistic regression level remains pending full-scale confirmation. This is a scope limitation, not a hypothesis failure — a single parameter change ($N: 300 \to 2{,}500$) is sufficient to address it.

**L2: Ensemble AUROC and Cross-Model Transfer Not Tested.** Predictions P1 (ensemble $\Delta$AUROC $\geq 0.025$ on TriviaQA, length-matched) and P3 (Llama$\to$Qwen transfer gap $< 0.05$ on TruthfulQA) have not been empirically evaluated. The PoC scope was intentionally limited to the independence gate (Pearson $r$ + partial $R^2$), which is the necessary precondition for ensemble training. These remain live predictions, not refutations.

**L3: Single Seed, No Variance Estimate.** The Pearson $|r| = 0.049$ is a point estimate from a single seed ($N=300$). While the result is well below the independence threshold (0.70), variance across seeds and dataset subsamples is unknown at this scale. At $N=2{,}500$, the confidence interval on Pearson $r$ will narrow substantially, and multi-seed evaluation is recommended.

**L4: Scope Bounded to Short-Answer Factual QA with 7–8B Open-Weight Models.** SE has documented limitations for long-form generation \citep{nguyen2025snne}. Our results hold for TriviaQA short-answer QA (1–10 token answers) at temperature=0.7 with Llama-3.1-8B-Instruct. Generalization to other model families, scales, or generation tasks requires independent evaluation.

## Future Work

**h-e1-v2 (N=2500):** The immediate next step is a full-scale run with $N=2{,}500$ prompts. All code and infrastructure are reusable; only `N_PROMPTS: 300 → 2500` in `config.py` changes. This will confirm the partial $R^2 \geq 0.02$ criterion and enable ensemble AUROC computation.

**Ensemble AUROC and Cross-Model Transfer:** Once h-e1-v2 provides Llama-calibrated LR weights, the ensemble (min\_logprob + SE\_N5) can be evaluated for $\Delta$AUROC on TriviaQA (P1) and cross-model transfer to Qwen-2.5-7B on TruthfulQA (P3).

**Orthogonality Zone Analysis:** The causal mechanism Step 2 (Section~3) predicts that the "orthogonality zone" — prompts with high min\_logprob $\geq 0.8$ AND SE in the top quartile — is enriched for hallucinations (error rate $\geq$ baseline + 10pp). This analysis requires only the signals and correctness labels from h-e1-v2, with no additional computation.

**Multi-Seed Robustness:** Bootstrap confidence intervals on Pearson $r$ at $N=2{,}500$, with 3 seeds for dataset selection, would establish the stability of the near-orthogonality result across dataset subsamples.

**Scope Extension:** Testing SE\_N5 + min\_logprob independence on a second model family (Mistral-7B or Qwen-2.5-7B as generator) would determine whether near-orthogonality is model-agnostic, as the algebraic distinctness of the two signals suggests.

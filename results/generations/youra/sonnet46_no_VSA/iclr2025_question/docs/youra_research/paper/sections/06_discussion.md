# Discussion

## Key Findings and Their Implications

**SE and min\_logprob measure genuinely distinct uncertainty dimensions — but independence does not guarantee additive predictive utility.** The Pearson |r|=0.026 at N=2500 is not merely a marginal pass of the 0.70 threshold — it indicates near-orthogonality by any reasonable standard. For context, the prior closest measurement (first-token confidence vs. SE, r=0.54–0.76) is approximately 20× higher. This gap is mechanistically explained: min\_logprob is the minimum over the full greedy decode sequence (capturing late-position token uncertainty), not the first token.

However, the partial R²=0.0005 (LRT p=0.442, N=2500) is a genuine null result: SE does not add conditional predictive power for correctness beyond min\_logprob at this scale. This dissociation — near-zero linear correlation combined with near-zero conditional predictive contribution — can arise when two signals both capture the same underlying correctness signal through orthogonal feature representations. On short-answer factual QA, both SE (semantic consistency) and min\_logprob (token-level confidence) may primarily reflect the same underlying model uncertainty about factual recall, despite computing it through different inference paths.

This finding is practically informative: it rules out a simple linear ensemble of SE and min\_logprob as a meaningful improvement over min\_logprob alone on TriviaQA. Whether a nonlinear ensemble (e.g., a learned combination, or conditional application in the orthogonality zone) can exploit the independent information remains an open question.

**Cross-model judge design suppresses circularity effectively.** The ρ(SE, judge) = −0.026 result validates the evaluation protocol: using a different model family (Qwen-2.5-7B) to evaluate Llama-3.1-8B outputs prevents shared model-specific NLI biases from creating circular agreement between the SE signal (DeBERTa-MNLI based) and the judge. The small magnitude and negative sign confirm that the two NLI applications (consistency evaluation vs. factual correctness evaluation) are sufficiently distinct at TriviaQA's short-answer scale. This design choice, recommended by Santilli et al. [2025], is validated empirically in our setting.

**The partial R² null result is well-powered and should be taken at face value.** The partial R²=0.0005 (LRT p=0.442, N=2500) is the intended full-evaluation sample size. Unlike a small-N PoC result, this is not attributable to underpowering. The null result challenges the naive extrapolation from statistical independence (|r|=0.026) to ensemble utility: even when two signals are nearly uncorrelated, they can carry redundant correctness-predictive information through orthogonal feature representations. This is an empirical finding specific to the TriviaQA/Llama-3.1-8B/linear-ensemble setting and should not be generalized without further evidence. Nonlinear combination methods, different benchmarks, or different model families may yield different results.

## Limitations

**Ensemble AUROC not measured; linear null suggests limited linear ensemble gain.** Ensemble AUROC (ΔAUROC ≥ 0.025 on TriviaQA, length-matched) and cross-model transfer (Llama→Qwen gap < 0.05 on TruthfulQA) are not evaluated in this work. The partial R² null result (0.0005, N=2500) suggests that a linear logistic regression ensemble would not achieve the ΔAUROC target, but nonlinear methods (e.g., gradient boosting, neural combination) could potentially exploit the orthogonal signal space. Ensemble evaluation remains a target for follow-up work.

**Single seed.** N=2500 with a fixed seed (42) provides no estimate of variance in the Pearson r or partial R² estimates. Bootstrapped confidence intervals and multi-seed replication are needed for rigorous characterization. The reported 95% CI on Pearson r ([−0.013, +0.065]) is analytic (Fisher z), not bootstrapped.

**Scope: short-answer factual QA with 7–8B open-weight models.** Our results are validated on TriviaQA dev (≤50 token answers) with Llama-3.1-8B-Instruct. Generalization to long-form generation is explicitly out of scope — the SNNE paper [Nguyen 2025] documents that SE's advantage weakens for multi-sentence answers. Generalization to different model families (GPT-4, Gemini) or different scales (70B+) is not tested. The null result for partial R² may be specific to the short-answer factual QA setting where both signals collapse to the same correctness signal.

**Scope: short-answer factual QA with 7–8B open-weight models.** Our results are validated on TriviaQA dev (≤50 token answers) with Llama-3.1-8B-Instruct. Generalization to long-form generation is explicitly out of scope — the SNNE paper [Nguyen 2025] documents that SE's advantage weakens for multi-sentence answers. Generalization to different model families (GPT-4, Gemini) or different scales (70B+) is not tested.

## Broader Impact

This work contributes to the safety and reliability of LLM deployments by establishing the empirical independence of two lightweight UQ signals — one requiring only greedy decode access (min\_logprob) and one requiring only generation API access (SE\_N5). Their combined use in hallucination detection ensembles is made more rigorous by the independence characterization we provide.

The replicable evaluation methodology (cross-model LM-judge, circularity diagnostic, mechanism reality checks) provides a template for future UQ signal characterization studies. Researchers introducing new UQ signals can apply the same gating protocol to measure independence from existing baselines before claiming ensemble benefit.

We do not foresee significant negative impacts from this work. Better hallucination detection reduces risks of LLM misuse in high-stakes settings; it does not enable new attack vectors. The pipeline is implemented with publicly available open-weight models (Llama-3.1-8B, Qwen-2.5-7B, DeBERTa-MNLI), ensuring reproducibility without proprietary API dependence.

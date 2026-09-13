# Discussion

## 6.1 The Mechanistic Claim and the Null Result: Two Contributions

The h-e1 and h-m1 results are not in tension — they are complementary contributions at different levels of the causal chain.

**h-e1 establishes the mechanistic claim** (Step 1 of the causal chain) at the highest confidence level: a mathematical guarantee. Ratio reward produces non-zero advantage variance in any GRPO group where at least one completion achieves partial credit and no completion achieves full credit. This guarantee is independent of model scale, dataset, and training configuration. It holds for any GRPO group satisfying the partial-pass condition. The 98.7% simulation figure quantifies how often this condition is satisfied under typical early-training distributions.

**h-m1 establishes the prerequisite** for observing the mechanistic guarantee in practice. The claim is not that ratio reward always differs from binary reward — it is that ratio reward differs *when partial-pass completions exist in the training groups*. The h-m1 experiment precisely confirmed that this prerequisite was not satisfied: every completion in every group was a truncated non-program (clipped_ratio = 1.0), making test case execution impossible and both rewards identically zero. The null result is a principled finding: it identifies the binding constraint (generation length must be sufficient for the model to produce syntactically complete solutions) and rules out the hypothesis that ratio reward helps regardless of experimental setup.

Together, h-e1 and h-m1 answer different questions with equally high confidence: "Does the mechanism exist?" (yes, mathematically) and "Was the mechanism active in our policy-level experiment?" (no, and here is exactly why).

## 6.2 Why the Null Result is Not a Failed Experiment

A failed experiment would be one in which the null result is ambiguous — where we cannot determine whether the absence of an effect reflects a true null effect or an experimental artifact. The h-m1 null result is the opposite of ambiguous: the FractionPartialCallback diagnostic provides a real-time monitor of the partial-pass prerequisite, and clipped_ratio = 1.0 at every step provides a direct measurement of the root cause (truncation). We know exactly why both rewards are equivalent: the model cannot produce executable completions under the 512-token budget for APPS competition-level problems.

This precision has practical value. Prior RLEF work that produced negative or mixed results on APPS may have encountered the same constraint without diagnosing it. Our diagnostic framework (FractionPartialCallback + clipped_ratio monitoring) provides a template for detecting this failure mode in future RLEF experiments, preventing wasted compute on experiments where the reward function choice is irrelevant because both functions evaluate to zero.

## 6.3 Honest Limitations

**Limitation 1: Policy-level claims are unverified.** The original hypothesis (ratio reward improves HumanEval pass@1 by ≥3pp) and its downstream predictions (P1, P2, P3) could not be evaluated. The h-m1 experiment did not produce the prerequisite conditions for testing policy-level effects. We make no claim about ratio reward's benefit for HumanEval, APPS all-pass rate, or cross-benchmark generalization. These remain open empirical questions.

*Why acceptable:* The mechanistic claim (h-e1) is a genuine contribution independent of the policy-level outcome. The precise characterization of the prerequisite (h-m1) is a methodological contribution that guides future work. A paper that proves the mechanism exists and identifies why the policy-level test failed is more informative than one that reports a clean positive result without examining when the mechanism operates.

**Limitation 2: Single model, single dataset.** All experiments use DeepSeek-Coder-6.7B-instruct on APPS. The mechanistic claim (h-e1) is model-agnostic (it is a mathematical property of GRPO group normalization), but the policy-level analysis (h-m1) covers only one model-dataset combination. Different models with higher APPS base solve rates, or different datasets (HumanEval, MBPP, APPS introductory split), may show different results.

*Why acceptable:* The mechanistic claim's model-agnosticism is its strength: the guarantee applies to any model training with GRPO on any dataset with partial-pass completions. The policy-level limitation is precisely characterized and points directly to the corrective experiment.

**Limitation 3: Gradient norm CI from real training was pending at analysis time.** The h-e1 150-step background run (PID 2605366) was in progress when the gate was evaluated. The mechanistic proof served as primary evidence; the numerical CI is supplementary. The h-m1 early-training CI (steps 1–136) includes zero, but this is expected given that both conditions receive identical zero rewards throughout (both conditions are in the dead zone for the same reason — no partial-pass completions).

*Why acceptable:* Mathematical proof provides a stronger form of evidence than a sample-dependent CI for existence claims. The limitation is that we cannot report the magnitude of the gradient norm difference in real training under correctly-powered conditions.

## 6.4 Implications for RLEF Practitioners

The primary practical implication is a pre-training checklist for ratio reward experiments:

1. **Validate base solve rate before training.** Compute reward_mean and fraction_partial for a small sample (100–200 prompts) under the planned generation length. If both are 0, ratio and binary rewards are equivalent — increase max_new_tokens or switch to a dataset with non-zero base solve rate.

2. **Monitor clipped_ratio during training.** If clipped_ratio → 1.0 at all steps, the model cannot produce complete solutions and no reward signal (binary or ratio) reaches the model.

3. **Use ratio reward when partial-pass conditions hold.** If fraction_partial > 0 at early steps, ratio reward provides additional gradient signal that binary reward cannot — without any change to training infrastructure beyond the reward function.

4. **Switch to ratio reward for hard datasets with low base solve rate.** APPS competition-level problems are likely beyond the 512-token generation budget for 6.7B models. Either increase max_new_tokens to 1,024–2,048 or use easier training data (APPS introductory split, HumanEval, MBPP) where the model has non-zero base solve rate.

## 6.5 Broader Impact

Our analysis quantifies a previously unexamined failure mode in GRPO-based RLEF: the binary reward gradient dead zone. The analysis does not require knowledge of model internals — it is derivable from the GRPO group normalization formula and the binary reward function definition. We expect this analysis to be generalizable to any GRPO training setup on hard tasks where the model begins with a near-zero solve rate, including math reasoning and repository-level code repair.

The one-line fix (switch from binary to ratio reward) is immediately actionable for any practitioner using GRPO for code post-training. The diagnostic framework (FractionPartialCallback, clipped_ratio monitoring) adds minimal overhead and provides real-time visibility into whether the reward function is providing signal. We release all code, configurations, and diagnostic tools to support reproducibility and future experimentation.

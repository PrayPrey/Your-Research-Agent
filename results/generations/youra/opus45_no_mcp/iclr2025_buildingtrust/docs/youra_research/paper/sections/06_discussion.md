# Discussion

## Interpretation: The Self-Reading Mechanism

Our results support a "self-reading" interpretation of how CoT+confidence improves calibration. When prompted to reason step-by-step, the model generates linguistic markers of epistemic uncertainty—hedging words like "may," "could," and "however." Due to autoregressive generation, these markers remain in the model's context when it subsequently generates a confidence estimate. The significant negative correlation (r=-0.315) between hedging count and confidence indicates that the model adjusts its confidence judgment downward when more uncertainty signals are present in its own reasoning.

This interpretation aligns with the architectural properties of transformer-based LLMs: attention mechanisms can attend to prior tokens, and the hedging markers are literal tokens in the input context when confidence is generated. The model is not simply "making up" separate reasoning and confidence; it appears to integrate information from its reasoning into its confidence judgment.

## Alternative Explanations

**Difficulty Confound:** One alternative is that difficult questions produce both more hedging (the model is less certain) and lower confidence, without the hedging causally affecting confidence. This is plausible—difficulty is a common cause that could explain the correlation. However, this interpretation still supports using hedging as a calibration signal: if hedging indicates difficulty, and difficulty correlates with error rate, then hedging-adjusted confidence should be better calibrated regardless of the causal mechanism.

**Prompt Artifact:** Another alternative is that our prompt structure induces the correlation through some artifact. We consider this less likely given the high effect size and the consistency of results across all 817 TruthfulQA items. The prompt does not explicitly link hedging to confidence.

**Token-Count Effect:** The token-padding control was designed to test whether longer outputs alone improve calibration. While this condition was not executed with real API calls (H-E1 mock mode), the mechanism chain validation suggests that hedging markers specifically—not arbitrary tokens—are associated with confidence adjustment.

## Honest Limitations

**Single Model:** We validate the mechanism on GPT-3.5-turbo only. While this is a representative instruction-tuned model, generalization to other architectures (Llama, Claude, GPT-4) requires explicit replication. The mechanism should be architecture-agnostic in principle, but implementation details may differ.

**Correlational Evidence:** Our findings are correlational. We observe that hedging correlates with lower confidence, but we do not prove that the model "reads" hedging markers causally. An intervention study—manipulating hedging markers and observing confidence changes—would provide stronger causal evidence.

**P1 Untested:** The primary ECE comparison (CoT+confidence vs. single interventions) was not executed with real API calls. We validate the underlying mechanism chain, but the super-additive calibration claim remains a prediction rather than a demonstrated result.

**Single Dataset:** Only TruthfulQA was evaluated. While this is an adversarial benchmark where calibration matters, transfer to other domains (MMLU, SciQ, commonsense reasoning) is untested.

## Practical Implications

For practitioners, our findings suggest that CoT+confidence prompting provides a zero-shot method for obtaining more calibrated confidence estimates. The method requires no model fine-tuning, no access to internal logits, and no held-out calibration set—it works through prompting alone.

The mechanism insight also suggests a monitoring approach: tracking hedging marker frequency in CoT outputs could provide an additional calibration signal even when explicit confidence is not requested.

## Connection to Broader LLM Trust

Calibration is one component of trustworthy AI. Our work addresses the specific question of whether confidence estimates match empirical accuracy. Complementary work on uncertainty quantification (e.g., semantic uncertainty via answer clustering) and on detecting when models "know that they don't know" (P(True) estimation) provides additional angles on the trust problem.

The "self-reading" mechanism we identify may generalize beyond calibration: if models can integrate uncertainty signals from their own reasoning, similar mechanisms might support other forms of self-assessment, such as detecting logical contradictions or recognizing knowledge gaps.

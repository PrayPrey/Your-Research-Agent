# Conclusion

We opened this paper with a result that defies the intuition that adversarial benchmarks stress-test model reliability: evaluating Llama-2-7b-hf on ANLI R1, a benchmark designed specifically to cause model errors, produced *better* calibration than the clean baseline. We have now explained why.

When adversarial examples are constructed model-in-the-loop — selected precisely because the model fails on them — the resulting benchmark contains examples where the model is already appropriately uncertain at failure time. Improved calibration under these conditions is not surprising; it is expected. The cases where calibration *degrades* are those where adversarial examples are constructed human-adversarially, targeting surface features to trigger high model confidence on incorrect answers, independent of model uncertainty. AdvGLUE MNLI is this case: ΔECE = +0.071, a 7.1 percentage-point calibration gap that makes confidence signals meaningfully less reliable under human-crafted adversarial NLI conditions.

The story does not end with this dichotomy. RLHF alignment interacts with the construction-method dependency in a way that is not predicted by clean-benchmark calibration studies: RLHF-aligned models (Llama-2-7b-chat) show consistently better calibration than base models on ANLI (ΔΔECE up to +0.147 across all 3 rounds), but worse calibration on AdvGLUE MNLI (ΔΔECE = −0.026, alignment tax). RLHF calibration properties measured on clean benchmarks do not transfer to adversarial settings, and the direction of transfer depends on the adversarial construction method.

## Summary

In this work, we addressed the gap between adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only) by directly measuring logit-based ECE on adversarial NLP benchmark splits. Our main contributions:

1. **First measurement of adversarial NLP calibration.** ΔECE = +0.071 for AdvGLUE MNLI confirms that adversarial calibration degradation is real and measurable. Label preservation rate = 1.000 for all adversarial splits validates ΔECE as a genuine calibration signal, not label noise.

2. **Conditional structure: construction method and task type determine calibration outcome.** Human-adversarial NLI (AdvGLUE MNLI: ΔECE = +0.071) degrades calibration; model-in-loop NLI (ANLI R1/R2: ΔECE < 0) improves it. The ANLI difficulty gradient (R1 → R2 → R3) shows a smooth transition as adversarial difficulty approaches the human-adversarial regime. Binary classification consistently shows reversed ΔECE regardless of construction method.

3. **Benchmark-type × RLHF interaction.** RLHF alignment conditionally moderates adversarial calibration degradation: confirmed for model-in-loop adversarial (ANLI: 100% moderation rate, 3/3 rounds), but reversed for static human-adversarial benchmarks (AdvGLUE: ΔΔECE = −0.026). This is the first documented benchmark-type × RLHF calibration interaction.

## Future Directions

**Testing alternative explanations for ANLI calibration improvement.** We hypothesize that ANLI R1/R2 calibration improvement reflects *adaptive uncertainty*: the model was already uncertain on these examples (which were selected to cause errors), so accuracy drop correlates with confidence drop. A direct test: compute ECE separately for correct and incorrect predictions, and compare confidence distributions on wrong predictions for ANLI vs. AdvGLUE. If ANLI wrong predictions have lower mean confidence than AdvGLUE wrong predictions, adaptive uncertainty is confirmed as the mechanism.

**Explaining the AdvGLUE alignment tax.** We hypothesize that AdvGLUE was constructed targeting base model reasoning shortcuts that RLHF amplifies. A counter-factual test: construct new human-adversarial NLI examples targeting Llama-2-7b-chat specifically. If the alignment tax disappears on chat-targeted adversarial examples, benchmark-construction targeting is causal. If it persists, RLHF instruction-following overconfidence is the primary driver.

**Multi-model grid and P3 validation.** The 4-model × 5-task cell grid originally planned (20 cells) was reduced to 5 cells (1 model) due to computational constraints. Running Mistral-7B-Instruct and Llama-2-13b-chat through the H-E1 pipeline would enable proper evaluation of P1 (universality threshold) and P3 (ΔECE-AUROC correlation as deployment reliability predictor) — the two original predictions left without sufficient statistical power.

**Temperature scaling as ΔECE mitigation baseline.** Temperature scaling (Guo et al. [2017]) was specified in our original experimental plan but never applied. Applying temperature scaling to H-E1 logit caches and recomputing ΔECE would reveal whether calibration degradation under human-adversarial conditions is a confidence scaling artifact (addressable post-hoc) or a structural property of model uncertainty under adversarial conditions (requiring more fundamental intervention).

Adversarial accuracy evaluation and calibration evaluation have developed as separate communities. The conditional structure we document — where the same adversarial benchmark can improve or degrade calibration depending on how it was constructed and whether the model was RLHF-aligned — suggests that these communities must develop shared vocabulary and methods. Calibration robustness is not a consequence of accuracy robustness; it requires its own measurement framework.

# Conclusion

We began by observing that a model's alignment strategy — DPO or SFT — might be
inferrable from standard benchmark scores alone. We confirmed this intuition: 83.3%
classification accuracy (permutation p=0.031) establishes that the alignment fingerprint
is real and statistically reliable. But we also found that the fingerprint tells a
different story than expected. It is not fairness that marks DPO-aligned models as
distinct; it is truthfulness.

## Summary

We introduced alignment fingerprinting as a binary classification problem over 4D
trustworthiness benchmark vectors and showed that:

1. **DPO and SFT 7B models are separable from public benchmark scores at 83.3% LOO-CV
   accuracy (permutation p=0.031).** This makes alignment auditing without training-data
   access practically feasible.

2. **The dominant discriminative dimension is TruthfulQA MC2 (Fisher's criterion=0.8122),
   not fairness benchmarks.** DPO models score +4.6pp higher on truthfulness on average,
   directly contradicting the predicted fairness-advantage mechanism. BBQ shows no
   systematic DPO advantage (k=3/6, p=0.66).

3. **Misclassification cases reveal alignment space structure.** An RLHF model clustering
   with DPO suggests preference-based methods share a benchmark signature; a DPO model
   misclassified as SFT reveals that base architecture proximity can dominate alignment
   signal for near-identical pairs.

## Future Directions

The gap between what the fingerprint exists and why it exists motivates several
well-grounded extensions:

**Mechanism confirmation.** The most plausible explanation for DPO's truthfulness
advantage — implicit factual quality reward in UltraFeedback-style annotation —
requires direct testing. Comparing DPO models trained on datasets with vs. without
explicit factual quality ratings (e.g., UltraFeedback vs. Anthropic HH-RLHF) would
test whether the truthfulness signal is annotation-driven or a generic property of
contrastive preference training.

**Architecture-controlled replication.** Restricting analysis to single-base-model
families (e.g., all Mistral-7B-v0.1 models) would determine whether the 83.3%
fingerprint accuracy partially reflects base model variation rather than alignment
strategy alone. The zephyr misclassification suggests this effect is real.

**Three-class alignment fingerprinting.** Extending to a DPO vs. RLHF-PPO vs. pure-SFT
classification would formalize the observation that RLHF and DPO share a benchmark
signature, and would clarify whether "preference-based training" is the correct
alignment category for fingerprinting — rather than the DPO/SFT binary.

**Full-task evaluation.** Publication-quality results require removing the 100-sample
limit. Infrastructure is validated; the extension is a matter of wall-time and compute.

## Closing

Alignment fingerprinting from benchmark scores is feasible — but it fingerprints
the unexpected. The signal that identifies DPO-trained models is not the fairness
advantage that DPO's design suggests, but a truthfulness advantage that its design
does not explicitly optimize for. This inversion should prompt revisiting what
preference-based training actually learns, and how alignment auditing tools should
be designed when theory and empirical signal diverge.

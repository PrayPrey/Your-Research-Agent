# Conclusion

We began this work with a mistaken assumption: that SFT fails on hard competitive programming benchmarks because the training data lacks correct solutions. APPS, we found, contains reference solutions for 85.32% of competition-level problems. The dataset is not sparse — the model simply cannot transfer those solutions to held-out hard evaluation problems. That generalization void, not a data void, is where RLEF concentrates its advantage.

This reframing changes how we should think about why execution feedback helps. RLEF works not because it provides learning signal where SFT has none in the training set, but because it trains on the model's own generated outputs — learning from what the model can actually attempt rather than from an idealized reference distribution the model cannot yet reach. This capability-relative feedback is the mechanism, though confirming it directly requires the reward monitoring experiment we could not complete at this scale.

## Summary

In this work, we make three contributions. First, we provide a controlled, reproducible, open-source pipeline for comparing RLEF against SFT across the full benchmark difficulty spectrum — from HumanEval (easy) to LiveCodeBench-Hard (competitive programming) — using DeepSeek-Coder-7B, APPS, and bigcode-evaluation-harness throughout. Second, using this pipeline, we confirm a statistically significant positive-ordered difficulty-scaling advantage for RLEF over SFT (Jonckheere-Terpstra z=+56.10, p≈0), with the largest gains concentrated at LiveCodeBench-Hard (Δ=+0.18) — precisely where the generalization void is deepest. Third, we deliver a practical null result: fraction-of-tests and binary RLEF rewards produce equivalent performance at APPS training scale (p=0.552), consistent with two independent literature findings and providing a controlled replication on a new model/dataset combination.

Taken together, these findings deliver a simple message for practitioners: the key investment for RLEF is execution feedback infrastructure, not reward function complexity. Binary rewards work. The hard part is building a fast, safe code execution environment — not engineering partial credit reward signals.

## Future Directions

Our findings open several grounded directions:

**Mechanism verification.** The most immediate need is to confirm whether RLEF receives non-zero reward on hard competition problems when generation is not truncated (max_new_tokens≥512). Our reward monitoring experiment (h-m2) was confounded by token truncation at 128 tokens, producing zero reward across all difficulty levels — an artifact, not a true result. Re-running with corrected token length is the highest-priority follow-up, as it directly tests whether the partial-success gradient mechanism is active.

**Domain-controlled evaluation.** A competing explanation for our difficulty-scaling findings is that APPS and LiveCodeBench-Hard sample different algorithmic problem types (domain mismatch), and that what appears as difficulty-scaling is partly domain-transfer failure. A matched-pairs analysis by algorithmic category (dynamic programming, graph algorithms, string processing) would disambiguate difficulty from domain effects.

**Weighted reward formulation.** Our null result on naïve fraction vs. binary reward does not extend to weighted fractional reward (VeRPO formulation), which addresses the cardinality bias identified in APPS's variable test-count structure. Whether weighted fraction reward produces meaningfully better performance than binary remains an open empirical question.

**Scale extension.** Our results are from a 7B model at smoke scale. Whether the difficulty-scaling advantage strengthens or weakens at larger model scales (13B, 34B) and at full training convergence (3 epochs, 4449 samples) is an important generalization question. We have validated the infrastructure for this extension; the experiments themselves are the next step.

The APPS coverage paradox — correct solutions in the dataset, generalization failure at evaluation — is a more general phenomenon than our setting. As the field scales code LLMs through execution feedback, understanding why models with high-quality training data still fail to generalize to held-out evaluation will be central to making that training effective.

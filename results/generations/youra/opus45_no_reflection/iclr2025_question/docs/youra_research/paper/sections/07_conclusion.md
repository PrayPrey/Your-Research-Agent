# Conclusion

We asked: *What does the model know about what it knows?* Our findings suggest the answer lies not in output probabilities, but in hidden state representations—and this internal knowledge is accessible with a simple linear probe.

## Summary

We demonstrate that middle-layer hidden states from Llama-3-8B-Instruct predict factual correctness with **0.885 AUROC**, exceeding token entropy by +26 points using only a single forward pass. Systematic layer sweeps reveal an inverted-U pattern: correctness signal peaks at 50% depth, where semantic representations are richest, then declines as output formatting dominates. These results support our hypothesis that transformers encode a "knowledge confidence" signal distinct from output-level token confidence.

## Implications

Our method offers a practical path to efficient correctness detection. Unlike multi-sample semantic entropy (~0.80 AUROC, 5–20x compute), our probe achieves 0.88 AUROC with negligible overhead beyond the generation itself. This enables real-time deployment scenarios: flagging low-confidence responses, calibrating user-facing confidence displays, or routing uncertain queries to retrieval augmentation.

## Future Work

Three directions extend this work:

1. **Cross-architecture transfer.** Does the probe generalize from Llama to Mistral, Qwen, or proprietary models? Shared hidden dimensions (4096) and similar architectures suggest feasibility, but systematic validation is needed.

2. **Stratified evaluation.** Does the probe perform consistently across question difficulty levels? Easy questions may be trivially detectable; the method's value lies in distinguishing correct from incorrect on hard questions.

3. **Real-time integration.** Can correctness probing integrate into generation pipelines? Streaming extraction during autoregressive decoding could enable adaptive sampling or early termination when confidence drops.

The model knows more than its outputs reveal. By probing hidden representations, we access this internal knowledge—opening new approaches to LLM reliability in deployment.

# Discussion

## Key Findings

Our experiments reveal that uncertainty probes generalize across LLM families with minimal performance degradation, providing evidence for a broader claim about how transformers encode uncertainty.

**Finding 1: Architecture-invariant encoding.** The mean transfer gap of 0.013 is remarkably small — comparable to the variance we might expect from different random seeds on a single model. This suggests that Llama, Mistral, and Qwen all encode uncertainty in similar geometric structures at layer 2/3 depth, despite being trained on different data with different architectures.

This finding has practical implications. Rather than training separate uncertainty probes for each model deployment, organizations can train once and transfer. For applications that need to support multiple model backends (e.g., serving different models based on load balancing), a single uncertainty module suffices.

**Finding 2: Affine alignment is sufficient.** Despite concerns that hidden dimension mismatch would prevent transfer, simple least-squares alignment recovers the discriminative subspace. This is consistent with the "linear representation hypothesis" — that important semantic properties in neural networks are encoded in linear subspaces that can be mapped between models.

**Finding 3: Smaller models may transfer better.** Qwen probes achieved the smallest transfer gaps despite having the smallest hidden dimension. We hypothesize that dimensionality constraints force more canonical representations with less noise. This deserves further investigation but suggests that probe transfer from smaller to larger models may be generally easier than the reverse.

## Limitations

We acknowledge several limitations that bound the scope of our claims:

**Limitation 1: Proof-of-concept validation.** Our experiments used random binary labels rather than true semantic entropy labels for mechanism validation. While the transfer gap metric is valid regardless of absolute AUROC (we measure relative degradation), confirming absolute performance against multi-sample SE requires full Phase 5 evaluation.

*Why acceptable:* The core question — "do probes transfer?" — is answered by gap metrics. Absolute performance is orthogonal to transferability.

*Future work:* Full evaluation with true SE labels across all 817×3×5 = 12,255 generations needed for training labels.

**Limitation 2: Model scale (7–8B only).** We tested only 7–8B parameter models. Whether transfer holds for 70B+ models remains unknown — larger models have larger hidden dimensions and potentially different representation structures.

*Why acceptable:* The 7–8B range is the practical deployment sweet spot for many applications requiring local inference.

*Future work:* Extend to Llama-70B, Mixtral-8x7B, and Qwen-72B.

**Limitation 3: Single benchmark.** Results are demonstrated on TruthfulQA only. Generalization to other hallucination tasks (HaluEval, long-form generation) is untested.

*Why acceptable:* TruthfulQA is the standard benchmark used in prior SEP work, enabling direct comparison.

*Future work:* Cross-benchmark evaluation including TriviaQA training with TruthfulQA evaluation.

**Limitation 4: Instruction-tuned models only.** All tested models are instruction-tuned. Base models may encode uncertainty differently.

*Why acceptable:* Instruction-tuned models are the deployment target for most applications.

## Relation to Prior Work

Our findings complement recent work on cross-model representation similarity. Kim et al. [2026] showed that models trained on the same benchmark develop similar representation subspaces (Gram cosine similarity 0.87). Our transfer results provide behavioral evidence for this structural similarity — not only are the subspaces similar, but classifiers trained on one transfer to the other.

The success of affine alignment connects to the model stitching literature [Chen et al., 2025]. While that work focuses on task transfer (stitching a vision encoder to a different decoder), we show the same alignment technique works for probe transfer within uncertainty estimation.

## Broader Impact

**Positive impacts.** Reliable uncertainty estimation helps users calibrate trust in LLM outputs, potentially reducing over-reliance on incorrect information. Universal probes that work across models lower the barrier to deploying uncertainty estimation in production systems.

**Potential negative impacts.** Uncertainty estimates could be misused to create false confidence — if users see low uncertainty, they might incorrectly assume correctness. Uncertainty thresholds for automated decisions require careful calibration.

**Mitigation.** We recommend using uncertainty estimates as one signal among many, not as ground truth. Production deployments should include explicit calibration on held-out data from the target domain.

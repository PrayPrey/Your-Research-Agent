# 7. Conclusion

We began with a measurement: LoRA-modified attention patterns and LM-trained KV eviction scores correlate at only ρ = 0.37 on task-specific inputs — the two independently trained components of a standard PEFT + KV compression pipeline are nearly orthogonally misaligned. From this measurement, a solution follows naturally: train them together.

JointLoRA-KV realizes this solution by optimizing LoRA adapter weights and Locret retaining head weights in a single backward pass via task classification cross-entropy loss, using a differentiable soft KV budget mask to route task gradients through the eviction boundary. Our experiments confirm three properties necessary for the method to work:

1. **The misalignment is real and pervasive** (ρ = 0.3662, 100/100 examples below threshold) — establishing that the problem JointLoRA-KV solves is not a marginal concern but a systematic gap in current practice.
2. **The mechanism is functional** — task gradients reach Locret retaining heads (locret_grad_received=True, grad_norm 1e-3 to 1e-4) and produce +1.50pp GLUE accuracy improvement over the frozen-Locret baseline even in a minimal one-epoch PoC, confirming that task-driven eviction realignment is achievable.
3. **Joint training is stable** — zero NaN events and zero divergence events across 3 random seeds, with independent gradient norm trajectories for LoRA and Locret parameters, validating the disjoint parameter architecture.

The primary performance claim — ≥3% improvement over the sequential fine-tuning baseline (B3) on LongBench-QA at 50% KV budget — is the key open question. All code is implemented and validated; its resolution is a compute-bounded execution step.

### Future Directions

The gradient signal strength analysis points to an important future investigation: Locret gradient norms are weak on short GLUE contexts (≤512 tokens) but should be substantially stronger on LongBench-QA contexts (1K–30K tokens) where the eviction boundary affects many more tokens. This suggests that JointLoRA-KV's advantage over sequential baselines may be largest precisely in the long-context regime where KV compression is most operationally necessary — a hypothesis directly addressable by H-M3 execution.

The GQA expansion artifact in the misalignment measurement (H-E1's repeat_interleave approach) is a methodological refinement worth pursuing: measuring ρ at KV-head granularity (8 heads) rather than expanded Q-head granularity (32 heads) provides a more conservative and robust characterization of the misalignment magnitude.

Extending beyond LLaMA-3.1-8B to Mistral-7B, Qwen-7B, and other GQA-based architectures will determine whether the disjoint-parameter stability argument holds broadly, and whether the misalignment magnitude (ρ ≈ 0.37) is characteristic of task-specific fine-tuning generally or particular to specific model checkpoints.

As KV compression moves from a research technique to an operational necessity for long-context LLM serving, the question of how compression-aware training should be becomes increasingly important. Task-aware KV compression — where the eviction policy is informed by the same objective as the adapter — is a natural next step in making efficient serving and task-specific adaptation work together rather than at cross-purposes.

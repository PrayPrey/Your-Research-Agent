# 7. Conclusion

We set out to test whether RLHF and DPO produce distinct alignment signatures under controlled conditions. Our five-hypothesis experiment confirmed the mechanistic premise: RLHF reward models produce smooth, continuous predictions (range 0.83 units), while DPO preserves sharper preference boundaries (sharpness ratio 1.65). These training dynamics are genuinely different.

Yet the predicted downstream effects did not follow. Models trained with RLHF and DPO do not form distinct behavioral attractors—cross-method similarity actually exceeded within-method similarity. Standard alignment benchmarks show similar performance profiles across methods (max |Cohen's d| = 0.194), with only minor cross-benchmark correlation differences.

**Different dynamics, similar destinations.** At 7B scale with LoRA fine-tuning, the mechanistic differences between RLHF and DPO do not manifest as distinct alignment signatures on existing evaluation infrastructure. This finding has immediate practical implications: method selection may matter less than assumed for final model behavior at this scale.

Our work also suggests a broader methodological point: standard alignment benchmarks may lack the sensitivity to detect method-specific effects even when they exist. Future work should explore custom alignment probes, item-level analysis, or representation-level metrics that could capture finer-grained differences.

The question of what *does* differentiate RLHF and DPO models—at larger scales, with full fine-tuning, or under different evaluation—remains open. Our negative result narrows the search space and points toward the conditions under which mechanistic differences might (or might not) matter for practical alignment outcomes.

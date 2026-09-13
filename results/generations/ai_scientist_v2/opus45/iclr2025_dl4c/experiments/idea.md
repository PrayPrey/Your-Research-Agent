## Name

divergence_aware_repair

## Title

Learning to Debug from Execution Divergence: Self-Supervised Pre-training for Code Repair via Trace Contrast

## Short Hypothesis

Code language models can develop stronger debugging and repair capabilities by pre-training on a self-supervised objective that contrasts execution traces of correct code against traces of synthetically-perturbed buggy variants, learning to identify divergence points and associate them with the source-level mutations that caused them. This approach addresses a key limitation of current methods: they treat code repair as text-to-text translation without grounding in execution semantics. By learning from execution divergence patterns, models can internalize a form of 'debugging intuition' that generalizes better to real bugs than models trained only on static code or pass/fail signals.

## Related Work

TraceFixer (Bouzenia et al., 2023) uses execution traces as input features for neural repair but requires user-provided correct states and doesn't pre-train on divergence patterns. TraceCoder (Huang et al., 2026) uses traces for multi-agent debugging but focuses on runtime instrumentation rather than learning transferable debugging representations. PPOCoder (Shojaee et al., 2023) and InterCode (Yang et al., 2023) use execution feedback for RL but only leverage binary pass/fail signals, missing rich divergence information. Our approach differs fundamentally: we propose a self-supervised pre-training objective that learns from the *structure* of execution divergences across many synthetic examples, creating representations that encode debugging intuition transferable to downstream repair tasks.

## Abstract

Current neural program repair methods either learn from static code edits or use execution feedback as sparse reward signals, missing the rich information contained in how program behavior diverges from expectations. We propose Divergence-Aware Pre-training for Repair (DAPR), a self-supervised framework that teaches code models to debug by learning from execution trace contrasts. Our approach works in three stages: (1) We systematically generate synthetic bugs by applying controlled mutations to correct programs, (2) We execute both versions and extract paired execution traces, identifying divergence points where variable states first differ, and (3) We pre-train a code model with a novel contrastive objective that learns to associate divergence patterns with their source-level causes. The pre-training task requires the model to predict which mutation caused a given divergence pattern, grounding code understanding in execution semantics. We hypothesize this creates representations encoding 'debugging intuition'—the ability to reason backward from unexpected behavior to code defects. We evaluate DAPR by fine-tuning on standard repair benchmarks (Defects4J, QuixBugs) and compare against models pre-trained only on code or fine-tuned with execution rewards. We expect DAPR to show improved repair accuracy, especially on bugs requiring semantic understanding of program behavior, and to exhibit better sample efficiency when fine-tuned with limited labeled examples.

## Experiments

**Experiment 1: Pre-training Data Generation and Model Training**
- Generate 500K synthetic bug instances from correct Python/Java programs using 8 mutation types (off-by-one, wrong operator, variable swap, boundary condition, null handling, type confusion, loop bound, conditional flip)
- Execute programs with 5 test inputs each, collecting variable traces at each statement
- Compute divergence points and create (trace_diff, mutation_type, mutation_location) tuples
- Pre-train CodeT5-base with three objectives: (a) divergence-to-mutation prediction, (b) mutation location prediction given divergence, (c) contrastive learning between divergent and non-divergent trace pairs
- Baseline: CodeT5-base with standard code pre-training only

**Experiment 2: Downstream Repair Performance**
- Fine-tune DAPR and baselines on Defects4J (395 bugs) and QuixBugs (40 bugs)
- Compare against: CodeT5-base, PPOCoder, CURE, RewardRepair
- Metrics: Exact match accuracy, plausible patch rate, Top-1/5/10 accuracy
- Hypothesis: DAPR achieves 10-15% relative improvement in exact match

**Experiment 3: Sample Efficiency Analysis**
- Fine-tune with varying amounts of labeled repair data (10%, 25%, 50%, 100%)
- Measure repair accuracy vs. training data size
- Hypothesis: DAPR shows steeper learning curve, achieving comparable performance with 50% less data

**Experiment 4: Bug Type Analysis**
- Categorize test bugs by type and measure per-category performance
- Hypothesis: DAPR shows largest gains on semantic bugs (logic errors) vs. syntactic bugs

**Experiment 5: Ablation Studies**
- Remove each pre-training objective individually
- Test with reduced mutation diversity
- Evaluate impact of trace granularity (statement-level vs. function-level)

## Risk Factors And Limitations

1. **Execution overhead**: Collecting traces for 500K programs is computationally expensive; we mitigate by using lightweight instrumentation and parallelization across a small cluster
2. **Synthetic-to-real gap**: Synthetic mutations may not capture all real bug patterns; we address this by using diverse mutation operators derived from real bug taxonomies
3. **Language specificity**: Trace collection requires language-specific instrumentation; initial focus on Python/Java limits generalization
4. **Trace alignment challenges**: Divergent executions may have different control flow paths, complicating trace comparison; we use dynamic time warping for alignment
5. **Limited to bugs with observable divergence**: Some bugs (e.g., performance issues, security vulnerabilities) may not show clear state divergence in traces
6. **Scalability to large programs**: Trace collection may be infeasible for very large codebases; we focus on function-level repair as in prior work


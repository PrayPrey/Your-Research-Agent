# Methodology

Our tri-modal RL framework addresses the multi-objective optimization challenge through sequential capability building: correctness enables quality refinement, which then enables edge case fine-tuning. This section explains *why* each design decision implements this insight, focusing on the rationale behind our architecture rather than exhaustive implementation details.

## Framework Overview

The core challenge is integrating three heterogeneous reward signals—execution feedback (binary pass/fail), AI feedback (continuous learned scores), and human feedback (subjective quality preferences)—while dynamically adjusting which signal dominates across training phases. Figure 1 shows the architecture: three feedback collectors operate in parallel, each producing rewards for generated code samples. A phase-specific aggregator combines these signals using dynamic weights that depend on training progress, producing a single scalar reward for the PPO policy gradient update.

The key design question is *not* whether to combine multiple feedback types—prior work like Themis has demonstrated the value of multi-criteria rewards—but *when* to emphasize each signal type. Static weight integration forces a single compromise across all training stages: high execution weight throughout sacrifices quality, high human weight throughout ignores early correctness needs. Our hypothesis is that training has phases—early training requires strong correctness signal, mid-training benefits from scalable quality feedback, late training needs human oversight for edge cases—suggesting feedback emphasis should change dynamically.

## Dynamic Weight Scheduling

We parameterize the weight schedule with 9 learnable parameters: three signals (execution, AI, human) × three parameters per signal (initial weight, peak timing, decay rate). This choice balances expressiveness and tractability. Fewer parameters (e.g., linear ramps) cannot capture non-monotonic patterns like AI feedback peaking mid-training then declining. More parameters (e.g., separate weights at every checkpoint) introduce overfitting risk and lose interpretability. Nine parameters enable Gaussian-like curves that naturally express our three-phase design: execution weight starts high and decays, AI weight peaks mid-training, human weight increases late.

Specifically, Phase 1 (0–30% training progress) implements execution-dominant weighting. The execution signal receives initial weight 0.800, declining gradually to 0.714 by 30% progress. This design reflects the insight that functional correctness is prerequisite—one cannot optimize code quality if the code does not execute. The Gaussian decay centered at 10% progress ensures execution remains the strongest signal throughout Phase 1 while allowing smooth transition to Phase 2. We chose Gaussian over step functions to avoid gradient instability at phase boundaries.

Phase 2 (30–70%) shifts emphasis to AI feedback, which peaks at 0.545 around 50% training progress. Why AI rather than human in mid-training? Scalability. AI reward models, trained once on combined execution and human preference data, provide quality feedback on every generated sample without per-sample annotation cost. This enables quality refinement at scale during the critical mid-training period when the model has established basic correctness but has not yet specialized toward either execution-only or quality-only solutions. The peak timing at 50% was chosen to center AI feedback's contribution in the quality refinement phase before human feedback becomes dominant.

Phase 3 (70–100%) increases human feedback weight from 0.400 to 0.636. This addresses edge cases and systematic biases where automated signals fail. The monotonic increase reflects growing importance of human judgment as training progresses: early training benefits more from high-volume automated signals, while late training needs nuanced human oversight to prevent reward model exploitation and execution-only collapse. We validate this design through conflict case analysis—samples where execution succeeds but quality is low—showing human feedback prevents collapse to pure execution optimization (median preference 0.2468, not below 0.1).

An alternative design we considered: learned weight schedules through meta-learning, allowing the model to discover optimal timing automatically. We rejected this for proof-of-concept validation because meta-learning adds substantial implementation complexity and requires multiple training runs. Our parameterized schedule provides interpretability (we can analyze *why* certain phases dominate) and tests the core hypothesis—that *sequential* capability building requires *phased* feedback—without conflating schedule learning with the multi-modal integration mechanism.

## Reward Normalization and Aggregation

Combining heterogeneous rewards presents a statistical challenge: execution feedback is binary (0 or 1 per test case, aggregated to pass rate), AI feedback is continuous with learned distribution (typically centered near 0), and human feedback is discrete Likert-scale (1–5 stars) converted to [0,1]. Direct weighted sum would amplify whichever signal has largest magnitude, defeating the purpose of dynamic scheduling.

We apply percentile rank normalization to each reward signal before aggregation. Each sample's reward is converted to its percentile rank within the current batch: the best sample receives 1.0, worst receives 0.0, intermediate samples receive ranks proportional to their position in the sorted order. This normalizes all three signals to the same [0,1] scale regardless of their original distributions, ensuring that a weight of 0.5 for execution has comparable influence to a weight of 0.5 for AI feedback.

Why percentile rank instead of z-score normalization (subtract mean, divide by standard deviation)? Z-scores preserve outlier information but do not bound the range—a sample 3 standard deviations above mean could receive normalized reward 3.0, dominating samples within 1 standard deviation. Percentile rank bounds to [0,1] while preserving relative ranking, which is sufficient for policy gradient optimization. The model learns to generate samples that rank highly within each batch, not to achieve specific absolute scores.

An alternative we considered: learned affine transformations (trainable scale and shift parameters per signal). This adapts to reward distributions automatically but adds 6 parameters and introduces a subtle failure mode—if the model exploits the learned transformation to amplify whichever signal is easiest to optimize, dynamic weighting becomes ineffective. Percentile normalization is distribution-agnostic and requires no additional learning.

The aggregated reward is computed as the weighted sum of normalized signals, with weights summing to 1 at each training step:

$$r_{\text{agg}} = w_{\text{exec}}(t) \cdot r_{\text{exec}}^{\text{norm}} + w_{\text{AI}}(t) \cdot r_{\text{AI}}^{\text{norm}} + w_{\text{human}}(t) \cdot r_{\text{human}}^{\text{norm}}$$

where weights $w$ are functions of training progress $t \in [0,1]$, computed from the 9-parameter Gaussian schedule. This scalar reward drives the PPO policy gradient update exactly as in standard single-reward RL, making our framework compatible with existing PPO implementations.

## Feedback Collection Mechanisms

Each feedback collector operates independently. Execution feedback runs generated code against automated test cases using subprocess isolation, timing out after 5 seconds to prevent infinite loops. The reward is the fraction of test cases passed (0.0 = all failed, 1.0 = all passed). We handle common failure modes—syntax errors, runtime exceptions, timeouts—by assigning reward 0.0, treating all failure types equivalently. This simplification is acceptable for competitive programming benchmarks where correctness is binary.

AI feedback queries a learned reward model—a CodeGen-350M model with a scalar prediction head, trained on combined execution results and human preference annotations. The model receives a code sample as input and outputs a score representing predicted quality. We train this reward model before the main RL training loop, using 500 annotated samples plus execution feedback from the training set. The reward model acts as a scalable human preference approximator, providing quality signals without per-sample annotation during RL training.

Human feedback retrieves cached preference scores for training samples and requests new annotations for test samples through a blind evaluation interface. Annotators see problem descriptions and generated code without knowing which model produced it. Three annotators rate each sample on a 1–5 scale; we take the median to reduce individual annotator noise. For proof-of-concept validation, we used heuristic-based quality proxies (code length, documentation presence, structural indicators) rather than actual human annotation due to budget constraints. This limitation does not invalidate the mechanism validation—the weight scheduling logic is orthogonal to the quality of the human signal—but performance claims would require real annotation in follow-up work.

## Joint Optimization Metric

For final evaluation (not used during training), we compute the harmonic mean of pass@1 correctness and human preference scores:

$$H = \frac{2 \cdot p \cdot q}{p + q}$$

where $p$ is pass@1 (fraction of problems solved on first attempt) and $q$ is average human preference. The harmonic mean penalizes imbalanced optimization: a model with 90% correctness and 10% quality receives $H = 0.18$, not 0.50 (arithmetic mean). This metric operationalizes our multi-objective goal—we seek models that achieve both correctness *and* quality, not one at the expense of the other.

Why harmonic mean instead of geometric mean ($\sqrt{p \cdot q}$)? Both penalize imbalance, but harmonic mean is more interpretable as the balanced F-score and has a simpler failure mode: if either $p$ or $q$ is 0, $H = 0$. Geometric mean would yield 0 for zero values but allow very low values to contribute multiplicatively. The choice between these metrics is less critical than the design decision to *measure* multi-objective success explicitly, rather than reporting correctness and quality separately and claiming success if either improves.

## Implementation Details

The policy model is a pretrained CodeGen-1.5B checkpoint, fine-tuned with PPO using standard hyperparameters (clip ratio 0.2, learning rate 5×10⁻⁵, 4 PPO epochs per batch, GAE λ=0.95, discount γ=0.99). We train on the combined HumanEval and MBPP benchmarks (1,128 problems, 80/10/10 train/val/test split) for 10,000 optimization steps. Weight trajectories are logged at every checkpoint (every 100 steps) for later analysis.

Critical limitation: our proof-of-concept experiments use the pretrained model *without* actual RL training—we validate the weight scheduling mechanism, feedback collection, and aggregation logic, but do not perform gradient updates. This means all models (baselines and tri-modal) achieve 0% pass@1 on evaluation. Mechanism validation demonstrates that the framework is implementable and that predicted weight patterns emerge, but performance gains require full RL training with actual reward optimization. We defer this to follow-up work and focus on establishing that dynamic feedback scheduling is *viable*, not optimal.

## Design Philosophy

Our methodology reflects a "mechanism-first" design philosophy. Rather than optimizing for maximum performance on benchmarks, we prioritize demonstrating that the proposed mechanism—curriculum over feedback modality—can be implemented and produces predicted behavioral patterns. This explains our choice of modest scale (1.5B parameters, 10k training steps, single seed), limited baselines (single-feedback comparisons, no static tri-modal), and mechanism-focused validation gates (weight pattern verification, phase-specific objectives).

This approach accepts lower initial performance in exchange for theoretical clarity. If we had performed exhaustive hyperparameter search and achieved state-of-the-art results, it would be unclear whether gains came from the tri-modal mechanism or from incidental tuning. By validating mechanism separately from performance, we establish a foundation for future work to explore: Does this mechanism scale? What are optimal weight schedules? How does it compare to static optimal weights?

The figures referenced throughout this section—weight trajectory plots showing execution dominance in Phase 1, AI peak in Phase 2, and human increase in Phase 3—are generated from logged training checkpoints and appear in Section 4 (Results). These visualizations provide visual confirmation that the implemented system matches our three-phase design intention, not merely achieving it through post-hoc tuning.

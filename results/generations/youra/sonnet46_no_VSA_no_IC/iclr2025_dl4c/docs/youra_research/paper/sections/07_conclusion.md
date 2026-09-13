# 7. Conclusion

We began by observing a puzzle: selecting 7.8% of MBPP training data for GRPO yields a 4.24× gradient signal advantage over random selection — but that advantage is entirely invisible during training when the model generates zero correct solutions across 40,000+ attempts. Our experiments resolve this puzzle precisely, identifying cold-start verification as a necessary precondition for any RLEF data selection method to operate.

## 7.1 Summary

In this work, we addressed the problem of gradient starvation in binary-reward RLEF by proposing offline frozen-model variance profiling — a "profile once, train anywhere" approach that decouples cheap offline profiling from expensive GRPO training. Our key insight is that the method's analytical validity and its training-phase effectiveness are separable: the former is confirmed, and the latter reveals a precise deployment precondition.

Our main contributions are:

1. **Variance distribution characterization** (confirmed): DeepSeek-Coder-7B-Instruct exhibits a severely right-skewed binary execution reward distribution on MBPP under constrained generation (91.7% all-fail, 7.8% at p_i=0.25). This is the first published characterization of this distribution and reveals that generation parameter constraints critically shape the effective training data pool.

2. **Offline variance profiling** (method, analytically validated): Top-50 variance-guided selection achieves 4.24× higher mean variance than random-50 (MWU p=2.22e−06), with stochastic dominance on the full distribution CDF. vLLM profiling completes in ~32 seconds for 374 problems — establishing practical viability.

3. **Cold-start diagnosis** (negative result, high confidence): 40,000+ GRPO generation attempts across 50–200 training steps produce zero reward for all conditions. We identify parameter mismatch between profiling (vLLM, max_new_tokens=128) and training (HF GRPOTrainer, max_completion_length=512) as the most likely root cause, and provide a concrete resolution protocol.

## 7.2 Future Directions

The negative result motivates three high-priority future experiments, each grounded in our findings:

**From the parameter mismatch finding:** Re-profile MBPP with training-identical parameters (max_new_tokens=512, subprocess execution, identical prompt format) and verify whether the 29 high-variance problems retain p_i≥0.25. If they do, cold-start is a training-phase issue (warm-start or higher LR needed). If they collapse to p_i=0, the mismatch is confirmed and alignment is the fix. This is the cheapest possible next experiment.

**From the cold-start persistence at 200 steps (h-m3):** Cold-start is not a duration issue. A model with >10% initial MBPP pass@1 — such as Qwen2.5-7B-Instruct (>30% pass@1 reported) — would test the variance selection mechanism without the cold-start barrier. Model swap requires minimal infrastructure change; all h-m2 code (build_subset, make_execution_reward, TRL config) is directly reusable.

**From the assumption that offline proxies remain stable:** Once cold-start is resolved, the temporal stability of the frozen-model variance ranking must be tested. If the ranking degrades quickly (selected problems move out of the learning zone after 10–20 steps), online selection may be necessary. Measuring frac_reward_zero_std gap trajectories across training steps will reveal whether offline proxies degrade.

## 7.3 Closing

The challenge of RLEF data selection — identifying the right problems for gradient-productive training — remains open. Our work shows that the selection signal is analytically real and practically measurable in seconds, but that manifesting this signal during training requires the model to be in a regime where it can generate some correct solutions. We hope this identification of the cold-start precondition helps future work on RLEF efficiency design experiments that confirm training-regime viability before claiming selection advantages — and that the offline profiling approach, once aligned with training parameters, delivers the gradient-concentration efficiency gain our analysis predicts.

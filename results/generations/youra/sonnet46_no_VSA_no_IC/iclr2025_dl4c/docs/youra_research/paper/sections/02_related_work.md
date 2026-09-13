# 2. Related Work

## 2.1 Reinforcement Learning from Execution Feedback

RLEF with binary execution rewards was established as a practical approach for improving code generation by Gehring et al. [2024], who demonstrated order-of-magnitude inference-time sample reductions through binary pass/fail reward signals combined with GRPO policy optimization. This work confirmed that binary execution correctness is sufficient for meaningful policy improvement and set the standard benchmark protocol (MBPP training → HumanEval+ evaluation) that we follow.

The mathematical foundation for why binary rewards lead to gradient starvation was formalized by the GRPO standard deviation identity: σ = √(k(G−k))/G, where k is the number of correct completions out of G [bay-yearick-lab, 2025]. When k=0 (all fail) or k=G (all pass), σ=0 and no gradient is produced. This identity is exact and explains why binary-reward GRPO is particularly susceptible to the zero-gradient pathology.

## 2.2 Gradient Starvation in GRPO

The empirical consequences of gradient starvation were quantified by the Gradient Starvation paper [2025]: at G=4 with binary rewards, 54.75% of training groups have all-fail outcomes and 14.50% have all-pass outcomes, producing 69.25% zero-gradient groups in expectation. This characterization — which we build directly on — establishes that nearly 70% of GRPO training steps on random data produce no learning signal. Our work provides the first *per-problem* empirical characterization of this effect for MBPP under constrained generation, finding an even more severe all-fail rate (91.7%) than the theoretical estimate.

## 2.3 Online Data Selection for GRPO Efficiency

Multiple recent papers independently converge on selecting intermediate-difficulty problems — those where the model occasionally succeeds — as the key to GRPO efficiency. All of these methods are *online*: they compute difficulty signals during training and adapt as the model learns.

**VIGOR** [2025] introduces variance-utility selection with formal guarantees, computing within-group variance during active training to allocate rollouts to problems with maximum gradient signal. VIGOR's online variance estimation directly parallels our offline profiling, but requires integration with the training loop and cannot be precomputed.

**Prompt Replay** [2025] tracks per-problem running pass rates during training and prioritizes problems with pass rate ≈ 0.5, the maximum-variance point under the binary variance identity. This is the closest conceptual predecessor to our work: it also targets problems that maximize σ. However, it requires the training history to compute running pass rates and cannot operate as a pure offline step.

**Sun et al.** [2025] demonstrate difficulty-targeted online selection for math reasoning, achieving 23–62% compute reduction with comparable or better performance. Their attention-mechanism difficulty estimator is online and targets scalar-reward RLVR; we extend the data selection intuition to binary-reward code generation with an offline approach.

**LZE** [2025] fuses pass-rate momentum and outcome-uncertainty during training for RLVR data selection. Like the above, it requires an active training loop and targets math reasoning rather than binary-reward code generation.

**Our approach** occupies the offline niche: profile once with a frozen model, then train anywhere. This design has the advantage of being decoupled from the training loop — the profiling can be done in seconds with vLLM and reused across hyperparameter sweeps. The disadvantage, as we discover, is sensitivity to profiling-training parameter alignment: if the generation parameters differ between profiling and training phases, the identified "high-variance" problems may not retain their variance under training conditions. We identify this mismatch as the root cause of cold-start failure and provide a protocol for alignment.

## 2.4 Cold-Start in RLEF

The cold-start problem — where a model produces zero correct completions early in training, preventing any reward signal and making learning impossible — has been recognized implicitly in RLEF papers but not systematically studied as a precondition for data selection. Prompt Replay [2025] avoids cold-start by using an active training loop that naturally adapts to early-training failure modes. VIGOR similarly adapts its allocation as the model warms up. Our offline approach, by contrast, cannot adapt: if the model produces zero correct completions under training conditions, the offline-selected "high-variance" subset provides no advantage. We make cold-start explicit and measurable, establishing frac_reward_zero_std monitoring as a necessary diagnostic for RLEF data selection experiments.

## 2.5 Positioning

Our work contributes: (1) the first offline variance-guided selection method for binary-reward code generation RLEF, (2) the first characterization of per-problem binary reward variance distribution across MBPP under constrained generation, and (3) the first systematic identification of cold-start as a precondition for data selection methods in RLEF — a result that is both negative (the method cannot yet manifest its training advantage) and precisely informative (the root cause and fix are specified).

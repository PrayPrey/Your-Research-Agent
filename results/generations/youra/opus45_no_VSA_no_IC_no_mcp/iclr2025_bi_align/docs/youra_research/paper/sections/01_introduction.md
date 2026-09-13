# 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO) represent two dominant paradigms for aligning language models with human preferences. These methods take fundamentally different optimization paths: RLHF trains an explicit reward model that learns a smooth approximation of human preferences, while DPO directly optimizes the policy from preference pairs without an intermediate reward signal. This mechanistic divergence raises a natural question: do these different training dynamics produce measurably different alignment signatures?

The theoretical motivation is compelling. RLHF's Bradley-Terry loss learns continuous reward values that interpolate between discrete preference labels, creating smooth optimization landscapes. DPO's closed-form objective, by contrast, directly encodes preference rankings into policy updates, potentially preserving sharper preference boundaries. If optimization landscape geometry influences convergence behavior, these methods should converge to different stable configurations—"attractors"—that manifest as differential performance patterns across alignment benchmarks.

We test this hypothesis under controlled conditions: same base model (Llama-2-7B), same preference data (Anthropic HH-RLHF), same compute budget. Our five-hypothesis experimental design isolates the mechanistic differences and traces their effects through to benchmark-level evaluation.

**Our findings reveal an unexpected gap in the causal chain.** We verify that RLHF and DPO exhibit genuinely different training dynamics: RLHF produces smooth, continuous reward predictions spanning a 0.83-unit range, while DPO shows 65% higher margin variance (sharpness ratio = 1.65). These mechanistic differences are real and measurable.

However, the predicted downstream effects do not follow. Models trained with RLHF and DPO do not cluster into distinct behavioral attractors—cross-method similarity actually *exceeds* within-method similarity (clustering gap = -0.016). Standard alignment benchmarks (TruthfulQA, HHH) do not reveal large differential profiles (max |Cohen's d| = 0.194, below the 0.3 threshold).

We characterize this as "different dynamics, similar destinations": at 7B scale with LoRA fine-tuning, the mechanistic differences between RLHF and DPO do not translate to distinct alignment signatures on existing evaluation infrastructure. This negative result has practical implications: method selection may matter less than expected for final model behavior at this scale. It also suggests limitations in current alignment benchmarks—standard evaluations may be too coarse-grained to detect method-specific signatures.

**Contributions:**
1. First empirical verification of RLHF reward model smoothness versus DPO preference boundary sharpness on identical data and model
2. Controlled falsification of the behavioral attractor hypothesis at 7B scale
3. Evidence that standard alignment benchmarks may lack sensitivity to method-specific differences
4. Validation that TruthfulQA and HHH benchmarks measure independent alignment dimensions (r < 0.05)

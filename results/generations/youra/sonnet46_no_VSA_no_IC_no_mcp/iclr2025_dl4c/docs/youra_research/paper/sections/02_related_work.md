# Related Work

## Reinforcement Learning from Execution Feedback for Code Generation

The use of execution signals to improve code language models is a well-established direction. CodeRL [Le et al., 2022] pioneered the approach by treating code generation as an actor-critic reinforcement learning problem, using binary pass/fail rewards from unit test execution. Applied to APPS and HumanEval, CodeRL demonstrated consistent improvements over pure SFT baselines (+4.3% on HumanEval). PPOCoder [Majeed et al., 2023] applied PPO with binary execution reward on HumanEval and MBPP, achieving 5–8% pass@1 improvements over SFT. RLTF [Liu et al., 2023] introduced partial credit reward (fraction of tests passing) and reported improvements of approximately 7% on HumanEval/MBPP, with the claim that partial reward advantages over binary reward particularly at harder problem instances.

These works share a common limitation: evaluation is confined to HumanEval and MBPP, which represent easy to medium difficulty. The critical question of whether RLEF advantages *scale with benchmark difficulty* into hard competitive programming regimes — LiveCodeBench-Hard — remains unaddressed by this body of work.

The most directly related prior study is RLEF [Gehring et al., 2024], which provides the strongest evidence for difficulty-scaling RLEF advantage. Gehring et al. report that partial reward outperforms binary reward more at harder problems, consistent with our original hypothesis. However, their study uses a proprietary Meta internal model, making independent verification impossible. Our work fills this reproducibility gap using publicly available components throughout.

## Reward Formulation in RLEF

The choice between binary (pass/fail) and fractional (fraction of tests passing) execution reward has received focused study. The common intuition — that fractional reward provides denser gradient signal and should outperform binary, especially at hard difficulty — is challenged by two recent papers. First, arXiv:2605.02944 finds that 97% of APPS problems produce identical solve/fail outcomes regardless of reward formulation at convergence under GRPO optimization, suggesting the two formulations are equivalent in practical settings. Second, VeRPO [arXiv:2601.03525] identifies a *cardinality bias* in naïve fractional reward: when problems have variable test-case counts (1 to 20+ in APPS), naïve fraction reward implicitly down-weights multi-test problems; a weighted formulation is required to recover the expected benefit.

Our experiment finds the same null result (p=0.552), consistent with both of these papers on a different model/dataset combination. Together these three controlled observations build a strong case that reward formulation equivalence is robust across training configurations — a practically useful finding that was not established by any single prior study.

The DeepSeek-R1 work [DeepSeek-AI, 2025] uses GRPO with binary reward at scale and achieves state-of-the-art performance on mathematical reasoning, further corroborating that binary execution feedback suffices when applied correctly. Our study extends this observation specifically to code generation difficulty-scaling evaluation.

## Hard Benchmark Evaluation for Code LLMs

LiveCodeBench [Jain et al., 2024] provides a contamination-free evaluation benchmark stratified by problem difficulty (Easy, Medium, Hard) drawn from competitive programming contests. It specifically addresses the limitation that HumanEval and MBPP have become partially saturated by model pre-training data. MBPP [Austin et al., 2021] and HumanEval [Chen et al., 2021] remain the most widely used evaluation benchmarks but cover only function-level easy/medium problems.

APPS [Hendrycks et al., 2021] is the most widely used algorithmic programming training dataset, containing problems categorized as introductory, interview, and competition difficulty. Published SFT performance on APPS competition problems is substantially below that on interview problems, which is commonly cited as evidence for a "signal void" at hard difficulty. Our coverage analysis reveals that this framing is empirically incorrect: 85.32% of APPS competition problems have reference solutions that pass all included test cases. The void is a *generalization* void, not a *dataset* void — a distinction with implications for mechanistic understanding of RLEF.

## Our Position

No prior work provides a controlled, reproducible, open-source comparison of RLEF vs. SFT across the full difficulty spectrum from HumanEval to LiveCodeBench-Hard. Existing work falls into three categories:

- **Easy/medium evaluation only** (CodeRL, PPOCoder, RLTF): covers HumanEval and MBPP but not competitive programming benchmarks. Cannot answer the difficulty-scaling question.
- **Internal/proprietary model** (RLEF-2024, Gehring et al.): provides the most relevant evidence for difficulty-scaling but is non-reproducible. We directly replicate and extend this finding with a public model.
- **Scale-only approaches** (DeepSeek-R1, LLaMA-3): demonstrate RLEF effectiveness at very large scale without the controlled difficulty-scaling analysis our design enables.

Our work fills the gap between these clusters: a controlled, reproducible, difficulty-stratified evaluation using open-source components. This design enables the specific question — *does RLEF's advantage scale with difficulty, and does reward formulation matter?* — to be answered with verifiable evidence.

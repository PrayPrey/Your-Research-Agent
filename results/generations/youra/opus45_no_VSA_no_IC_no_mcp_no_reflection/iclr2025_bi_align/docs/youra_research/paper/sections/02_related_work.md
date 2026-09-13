# 2. Related Work

## 2.1 Reinforcement Learning from Human Feedback

RLHF was introduced for language model alignment by Ziegler et al. [5] and scaled to production systems with InstructGPT [1]. The standard pipeline involves: (1) supervised fine-tuning on demonstration data, (2) training a reward model on human preference rankings, and (3) optimizing the policy via PPO against the reward model with KL regularization.

Constitutional AI (CAI) [6] introduced an alternative: using AI feedback (RLAIF) with explicit constitutional principles for harmlessness training. CAI's key insight—that explicit rules can induce implicit behavioral improvements—motivates our hypothesis that explicit constraint training transfers to implicit safety.

Direct Preference Optimization (DPO) [7] eliminates the reward model, optimizing directly on preference pairs. While DPO simplifies training, it remains single-objective and does not address multi-signal integration.

## 2.2 Multi-Objective Alignment

Askell et al. [8] formalized the HHH framework (Helpful, Harmless, Honest), analyzing trade-offs between objectives. Their work demonstrated that multi-objective optimization is feasible but focused on helpfulness-harmlessness, not helpfulness-controllability.

Gao et al. [9] characterized reward model overoptimization, showing that excessive optimization degrades true reward. This informs our use of KL regularization.

## 2.3 Instruction Following and Controllability

IFEval [2] introduced a benchmark for verifiable instruction following, measuring compliance with 25 constraint types (format, length, keywords, structure). We extend IFEval's use from evaluation to training signal extraction.

AlpacaEval [4] measures instruction-following quality via GPT-4 judgment against reference outputs. We use AlpacaEval LC as our helpfulness metric.

## 2.4 Bidirectional Alignment Framework

Sun et al. [3] survey 400+ papers to propose a bidirectional taxonomy:
- **AI→Human:** Specification integration—models adopting human values
- **Human→AI:** Agency preservation—humans retaining control

Their framework is theoretical; we provide the first empirical implementation.

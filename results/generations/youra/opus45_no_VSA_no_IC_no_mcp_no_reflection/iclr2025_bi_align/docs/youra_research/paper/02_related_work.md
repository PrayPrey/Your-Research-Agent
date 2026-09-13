# 2. Related Work

## 2.1 Reinforcement Learning from Human Feedback

RLHF was introduced for language model alignment by Ziegler et al. [5] and scaled to production systems with InstructGPT [1]. The standard pipeline involves: (1) supervised fine-tuning on demonstration data, (2) training a reward model on human preference rankings, and (3) optimizing the policy via PPO against the reward model with KL regularization. InstructGPT demonstrated that RLHF-tuned models are preferred over larger pre-trained models, establishing RLHF as the dominant alignment paradigm.

Constitutional AI (CAI) [6] introduced an alternative: using AI feedback (RLAIF) with explicit constitutional principles for harmlessness training. CAI's key insight—that explicit rules can induce implicit behavioral improvements—motivates our hypothesis that explicit constraint training transfers to implicit safety. However, CAI operates on safety-specific principles, not general controllability.

Direct Preference Optimization (DPO) [7] eliminates the reward model, optimizing directly on preference pairs. While DPO simplifies training, it remains single-objective and does not address multi-signal integration.

## 2.2 Multi-Objective Alignment

Askell et al. [8] formalized the HHH framework (Helpful, Harmless, Honest), analyzing trade-offs between objectives. Their work demonstrated that multi-objective optimization is feasible but focused on helpfulness-harmlessness, not helpfulness-controllability.

Gao et al. [9] characterized reward model overoptimization, showing that excessive optimization degrades true reward. This informs our use of KL regularization and validates our observation that moderate β (controllability weight) outperforms extreme values.

Recent work on Pareto-optimal alignment [10] formalizes multi-objective RLHF but has not been instantiated with controllability signals.

## 2.3 Instruction Following and Controllability

IFEval [2] introduced a benchmark for verifiable instruction following, measuring compliance with 25 constraint types (format, length, keywords, structure). Unlike subjective helpfulness, IFEval constraints are objectively verifiable via rule-based checks. We extend IFEval's use from evaluation to training signal extraction.

AlpacaEval [4] measures instruction-following quality via GPT-4 judgment against reference outputs. The Length-Controlled (LC) variant mitigates verbosity bias. We use AlpacaEval LC as our helpfulness metric.

## 2.4 Bidirectional Alignment Framework

Sun et al. [3] survey 400+ papers to propose a bidirectional taxonomy:
- **AI→Human:** Specification integration—models adopting human values (helpfulness, safety)
- **Human→AI:** Agency preservation—humans retaining control (steerability, controllability)

Their framework is theoretical; we provide the first empirical implementation using IFEval as the Human→AI controllability signal.

## 2.5 Safety Benchmarks

TruthfulQA [11] measures whether models generate truthful answers rather than mimicking human falsehoods. BBQ [12] measures bias in question answering across demographic categories. Both measure implicit safety constraints that models should satisfy without explicit instruction—the target of our transfer hypothesis.

## 2.6 Positioning Our Work

| Work | Direction | Training Signal | Our Contribution |
|------|-----------|-----------------|------------------|
| InstructGPT [1] | AI→Human | Helpfulness | Add controllability signal |
| CAI [6] | AI→Human | Safety principles | Use general constraints |
| IFEval [2] | Evaluation only | N/A | Convert to training signal |
| Sun et al. [3] | Theory | N/A | Empirical validation |
| **This work** | **Bidirectional** | **Helpfulness + IFEval** | **First empirical test** |

Our work is the first to combine helpfulness and controllability as joint RLHF training signals, testing whether explicit constraint training transfers to implicit safety benchmarks.

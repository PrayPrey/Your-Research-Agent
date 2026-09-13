# Paper Summary: CodeRL (P1)

**Title:** CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning  
**Authors:** Le et al. (Salesforce Research)  
**arXiv:** 2207.01780 (2022)  
**Status:** [INFERRED] — MCP unavailable; summary from training knowledge

---

## Abstract
CodeRL applies deep reinforcement learning to code generation by framing code synthesis as a sequential decision-making problem. Uses actor-critic PPO with a pretrained CodeT5 backbone and binary execution-based reward from unit test pass/fail.

---

## Key Contributions
- First major RLEF framework: SFT warmup → PPO fine-tuning with execution feedback
- Binary reward: reward=1 if ALL test cases pass, reward=0 otherwise
- Critic network predicts whether generated code will pass tests (code-unit-test correlation)
- Demonstrates RLEF outperforms SFT alone on HumanEval and APPS
- Introduces actor-critic training loop with code execution in the reward loop

---

## Methodology
- Base model: CodeT5 (encoder-decoder, pretrained on code)
- RL algorithm: PPO (actor-critic; critic predicts pass probability)
- Reward signal: **Binary** — 1 if all tests pass, 0 otherwise (sparse reward)
- Training data: APPS (10,000 programming problems with test suites)
- Evaluation: HumanEval (pass@k), APPS (strict pass@k and partial pass)
- No intermediate rewards; terminal reward only at code execution

---

## Experiments & Results
- HumanEval pass@1: ~18% (CodeRL) vs ~13% (SFT baseline) — ~5pp improvement
- APPS intro: meaningful improvement over SFT
- Ablation: critic network vs. no critic — critic helps training stability
- No reward signal ablation; binary reward assumed throughout
- Limitation: sparse reward leads to slow convergence; authors note this but do not address it

---

## Limitations & Gaps
- Binary reward only — no comparison to ratio or similarity reward
- Single model scale (CodeT5) — no scale study
- Reward hacking not studied — training and test distribution overlap possible
- Generalization to LiveCodeBench or SWE-bench not evaluated

---

## Relevance to Research Gap
**Direct baseline.** CodeRL is the primary prior work this ablation study compares against. The binary reward formulation is exactly what the research question asks whether ratio/similarity rewards outperform. Reward.py is isolated and modifiable.

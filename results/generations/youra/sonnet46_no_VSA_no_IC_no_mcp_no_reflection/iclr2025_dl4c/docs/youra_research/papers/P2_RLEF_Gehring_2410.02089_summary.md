# Paper Summary: RLEF/Gehring et al. (P2)

**Title:** RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning  
**Authors:** Gehring et al. (Meta FAIR)  
**arXiv:** 2410.02089 (2024)  
**Status:** [INFERRED] — MCP unavailable; summary from training knowledge

---

## Abstract
Large-scale RLEF post-training applied to repository-level code generation (SWE-bench). Shows execution feedback with binary reward enables strong performance on real GitHub issues without synthetic data.

---

## Key Contributions
- Scales RLEF to repository-level tasks (SWE-bench) — far beyond toy benchmarks
- Binary reward: pass/fail on pytest execution of existing repository tests
- Demonstrates RLEF outperforms SFT at the same data scale for SWE-bench tasks
- Training on real GitHub issue resolution (not just algorithmic problems)
- Shows execution feedback generalizes beyond HumanEval/MBPP to real-world code tasks

---

## Methodology
- Base model: Large proprietary code LLM (scale not disclosed)
- RL algorithm: PPO variant with execution-based reward
- Reward signal: **Binary** — patch passes ALL repository tests → reward=1; otherwise 0
- Training data: GitHub issues with associated test suites
- Evaluation: SWE-bench (full) and SWE-bench-lite (300 issues)
- No partial credit — pytest pass/fail is the reward signal

---

## Experiments & Results
- SWE-bench-lite resolve rate: competitive with best SFT approaches at time of publication
- Ablation: RLEF vs. SFT — RLEF significantly better for repository-level reasoning
- Shows execution feedback generalizes: models trained on issue resolution improve on held-out issues
- Binary reward sufficient for repository-level tasks — partial credit not explored

---

## Limitations & Gaps
- Binary reward only — no reward formulation ablation
- Single model scale — no cross-scale comparison
- Repository tests define the reward — susceptible to reward hacking if test suites are weak
- SWE-bench does not support partial credit naturally (pytest pass/fail is holistic)

---

## Relevance to Research Gap
**Key evidence for Gap 2 (transfer).** Shows binary RLEF generalizes to SWE-bench. The research question asks whether reward formulation changes this transfer — Gehring et al. cannot answer this because they only use binary reward. Provides the binary-reward SWE-bench transfer baseline this study would compare partial-credit variants against.

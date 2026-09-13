# Research Idea

## Title
Curriculum-Trained Compute Value Estimators for Test-Time Compute Extrapolation in LLM Reasoning

## Motivation
Large language models increasingly use extended reasoning chains for complex tasks, but current approaches either allocate fixed compute budgets (wasteful on easy problems) or use training-free heuristics like entropy thresholds that cannot extrapolate beyond observed patterns. A critical gap exists: no method enables models to reliably scale reasoning beyond training-time compute budgets while maintaining efficiency. This limits deployment in resource-constrained settings and prevents models from "thinking longer" on novel hard problems.

## Main Idea
We propose training lightweight Compute Value Estimator (CVE) heads—single linear layers (~0.001% parameter overhead)—that predict expected accuracy improvement from additional reasoning tokens using LLM hidden states. The key innovation is **curriculum multi-budget reinforcement learning**: progressively expanding token budget ranges during training (50→500→1000→2000 tokens) to learn budget-invariant value estimation. This enables extrapolation to 2-10x training budgets at inference.

The CVE queries hidden states every 50 tokens, continuing reasoning when predicted improvement exceeds a threshold. We hypothesize this achieves: (1) reliable extrapolation beyond training budgets (extrapolation coefficient >1.0), (2) 40-60% token reduction on easy problems, and (3) well-calibrated predictions (ECE <0.15).

Experiments on MATH, GSM8K, and HumanEval will compare against HALT-CoT, REFRAIN, and fixed-budget baselines, with ablations confirming curriculum necessity for extrapolation.
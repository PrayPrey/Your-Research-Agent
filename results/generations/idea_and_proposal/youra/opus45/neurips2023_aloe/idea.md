# Research Idea

## Title
Confidence-Calibrated Regret: A Zone of Proximal Development Curriculum for LLM Self-Training

## Motivation
Open-ended learning systems require agents that continuously improve by generating and solving increasingly challenging problems. Current LLM self-training methods select training examples randomly or by simple heuristics, ignoring the critical insight from developmental psychology: learning is maximized at the "Zone of Proximal Development" (ZPD)—tasks just beyond current competence. While regret-based curricula (PAIRED, ACCEL) successfully identify learning frontiers in RL, they require expensive rollouts unsuitable for LLM training. This gap limits the efficiency of self-improving language models in verifiable domains like mathematics and code generation.

## Main Idea
We propose Confidence-Calibrated Regret (CCR), a single-pass metric that identifies ZPD-boundary examples for LLM self-training. CCR scores examples where the model is "confidently wrong" or "surprisingly correct"—precisely the competence frontier where learning signal is richest. The method first calibrates model confidence (targeting ECE < 0.15), then computes CCR combining calibrated confidence with verification outcomes. Training prioritizes high-CCR examples.

**Core mechanism:** Calibration → CCR computation → ZPD identification → maximized gradient signal → improved efficiency.

**Expected outcomes:** 30-50% reduction in training examples needed to reach target accuracy compared to random sampling, with improved calibration as a byproduct. This enables more efficient open-ended self-improvement in verifiable domains, advancing practical deployment of continuously learning agents.
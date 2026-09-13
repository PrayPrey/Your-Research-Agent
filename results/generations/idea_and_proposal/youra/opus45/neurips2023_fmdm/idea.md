# Research Idea

## Title
Dual-Process Vision-Language Agents: Separating Intuitive Proposals from Deliberative Reasoning for Improved Decision Making

## Motivation
Foundation models excel at perception and language understanding but struggle with sequential decision-making tasks requiring long-horizon reasoning. Current approaches either fine-tune vision-language models (VLMs) end-to-end with reinforcement learning, causing training instability, or use VLMs as frozen components without task-specific optimization. This creates a gap: how can we leverage VLMs' broad pretrained knowledge while enabling principled learning from environmental feedback? Inspired by dual-process cognitive theory, we propose separating fast intuition from slow deliberation to address this challenge.

## Main Idea
We hypothesize that a dual-process architecture—where a frozen VLM (System 1) generates diverse action proposals and an RL-trained deliberator (System 2) reasons over them via chain-of-thought—will outperform monolithic VLM-RL approaches in success rate, sample efficiency, and interpretability.

**Mechanism:** The VLM's pretrained knowledge enables rapid proposal generation without action-specific training. The deliberator learns to evaluate and select among proposals through explicit reasoning, enabling better credit assignment than end-to-end optimization.

**Methodology:** We test on ALFWorld, Minecraft, and RoboCasa benchmarks, comparing against end-to-end baselines. We measure task success (>75% target), sample efficiency (≤50% interactions), and reasoning quality via human evaluation (≥4.0/5.0).

**Expected Impact:** This architecture provides a principled framework for combining foundation model capabilities with sequential decision-making, offering both performance gains and interpretable reasoning traces for real-world deployment.
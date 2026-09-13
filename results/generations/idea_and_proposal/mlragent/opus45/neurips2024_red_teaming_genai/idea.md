# Title: Adaptive Red Teaming via Reinforcement Learning with Evolving Attack Taxonomies

## Motivation
Current red teaming approaches for GenAI rely heavily on static benchmarks and human-crafted adversarial prompts, which quickly become obsolete as models are patched against known vulnerabilities. This creates a "whack-a-mole" dynamic where safety measures lag behind emerging attack vectors. Furthermore, existing evaluations fail to systematically explore the combinatorial space of potential vulnerabilities, leaving critical blind spots. We need automated, adaptive red teaming systems that can discover novel attack strategies while maintaining a structured understanding of vulnerability types.

## Main Idea
We propose **AdaptiveRedTeam**, a reinforcement learning framework that continuously discovers new jailbreak strategies while dynamically updating an attack taxonomy. The system consists of: (1) an RL-based attack generator trained to maximize successful policy violations across diverse harm categories, (2) a hierarchical clustering module that automatically organizes discovered attacks into an evolving taxonomy, and (3) a novelty detection mechanism that rewards exploration of under-tested vulnerability regions.

The key innovation is coupling attack discovery with structured categorization—each successful attack updates both the policy and the taxonomy, enabling systematic coverage analysis. We evaluate on multiple LLMs, measuring attack success rates, taxonomy coverage, and discovery of previously unknown vulnerability clusters.

**Expected Impact**: A self-improving red teaming system that provides quantitative safety coverage metrics and discovers vulnerabilities before malicious actors, fundamentally shifting from reactive to proactive AI safety evaluation.
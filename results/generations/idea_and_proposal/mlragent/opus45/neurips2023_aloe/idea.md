# Title: Curriculum Self-Play via LLM-Generated Environment Perturbations for Open-Ended Skill Acquisition

## Motivation
Current open-ended learning systems struggle to generate meaningful, progressively challenging problems that remain within the "zone of proximal development" of learning agents. Random environment generation often produces either trivial or impossible tasks, while hand-designed curricula lack the open-endedness needed for general capability emergence. Large language models possess rich world knowledge that could be leveraged to generate semantically meaningful environment variations, but this potential remains largely unexplored for curriculum design in embodied agents.

## Main Idea
I propose a framework where an LLM acts as an "environment designer" that observes an RL agent's current capabilities and generates targeted environment perturbations to create novel challenges. The system operates as follows:

1. **Capability Profiling**: Periodically evaluate the agent across diverse scenarios, summarizing strengths and weaknesses in natural language.

2. **LLM-Driven Perturbation**: Prompt the LLM with the capability profile to generate environment modifications (new obstacles, physics changes, goal variations) that specifically challenge identified weaknesses while remaining achievable.

3. **Regret-Based Filtering**: Filter LLM proposals using estimated learning potential (high regret but not maximum regret), ensuring productive difficulty.

4. **Iterative Refinement**: The LLM receives feedback on which perturbations led to skill acquisition, improving its proposals over time.

Expected outcomes include agents with broader generalization, particularly for sim2real transfer, and a scalable approach to curriculum generation that leverages LLM knowledge without expensive environment redesign.
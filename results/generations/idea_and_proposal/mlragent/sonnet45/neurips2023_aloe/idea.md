# Title
Adaptive Skill Decomposition Networks: Leveraging Emergent Task Graphs for Curriculum Generation in Open-Ended Learning

# Motivation
Current open-ended learning systems struggle to efficiently navigate vast skill spaces, often requiring extensive exploration that doesn't leverage discovered structure. While agents may encounter countless novel tasks, they lack mechanisms to automatically identify and exploit hierarchical relationships between skills. This leads to redundant learning and poor sample efficiency. A system that dynamically discovers skill dependencies and uses them to construct adaptive curricula could dramatically accelerate capability acquisition while maintaining open-endedness.

# Main Idea
We propose learning a dynamic task graph that emerges from agent-environment interactions, where nodes represent discovered skills and edges encode prerequisite relationships inferred from learning dynamics. The system operates in three phases:

1. **Skill Discovery**: Use intrinsic motivation to explore and automatically segment experiences into reusable skills via trajectory clustering in latent space.

2. **Dependency Inference**: Track which skills facilitate learning others (measured by reduced sample complexity) to build a probabilistic dependency graph using meta-learning over training curves.

3. **Curriculum Synthesis**: Generate personalized curricula by traversing the skill graph, selecting next tasks based on current mastery and estimated learning efficiency.

The approach combines quality-diversity for skill discovery with curriculum learning, creating a self-organizing system where the curriculum adapts to emergent complexity. Expected outcomes include faster capability acquisition, better knowledge transfer, and sustained open-ended progress in both simulated environments and LLM-based agents learning from interaction data.
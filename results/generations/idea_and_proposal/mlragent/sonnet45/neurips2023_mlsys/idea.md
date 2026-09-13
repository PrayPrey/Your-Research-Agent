# Title
**Carbon-Aware Dynamic Resource Allocation for LLM Training via Multi-Objective Reinforcement Learning**

# Motivation
Large-scale LLM training consumes enormous energy across thousands of accelerators, contributing significantly to carbon emissions. Current training systems optimize primarily for speed and cost, ignoring temporal variations in grid carbon intensity. Meanwhile, existing carbon-aware scheduling approaches use simple heuristics that fail to balance the complex tradeoffs between training efficiency, deadline constraints, and environmental impact. As AI's carbon footprint grows, we need intelligent systems that can dynamically adapt resource allocation to minimize emissions while maintaining training performance.

# Main Idea
We propose a multi-objective reinforcement learning framework that learns to dynamically allocate compute resources for distributed LLM training based on real-time carbon intensity signals. The RL agent observes: (1) current carbon intensity across datacenter regions, (2) training progress and gradient statistics, (3) communication patterns, and (4) predicted carbon intensity trajectories. 

Actions include: adjusting batch sizes, migrating computation across regions, modulating parallelism strategies (data/pipeline/tensor), and opportunistically pausing low-priority tasks during high-carbon periods.

The reward function balances training throughput, convergence quality, deadline adherence, and carbon reduction using Pareto-based multi-objective optimization. We'll evaluate on realistic LLM training scenarios using historical carbon intensity data, demonstrating carbon reductions of 20-40% with minimal impact on training time. This work establishes reproducible benchmarks for carbon-aware ML systems optimization.
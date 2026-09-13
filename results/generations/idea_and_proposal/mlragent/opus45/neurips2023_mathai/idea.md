# Title: Adaptive Difficulty Calibration for Mathematical Reasoning Benchmarks via Student-Teacher LLM Dynamics

## Motivation
Current mathematical reasoning benchmarks face a critical evaluation crisis: static datasets quickly become saturated as LLMs improve, leading to inflated performance metrics that poorly reflect genuine reasoning capabilities. Moreover, existing benchmarks cannot distinguish between true mathematical understanding and pattern matching on similar problem structures. We need dynamic evaluation frameworks that adapt to model capabilities while maintaining consistent difficulty calibration, ensuring meaningful progress measurement across the rapidly evolving LLM landscape.

## Main Idea
I propose a self-calibrating benchmark system using adversarial student-teacher dynamics between LLMs. A "teacher" LLM generates mathematical problems conditioned on a target difficulty level, while a "student" LLM attempts to solve them. The key innovation is a feedback loop where problem difficulty is empirically calibrated through iterative solving attempts across multiple student models of varying capabilities.

The methodology involves: (1) training a difficulty-conditioned problem generator using reinforcement learning, where rewards are based on achieving target solve rates across a population of solver models; (2) maintaining a dynamic item response theory (IRT) model that continuously updates difficulty estimates; (3) generating "boundary problems" that specifically probe the limits of current models.

Expected outcomes include benchmarks that remain discriminative as models improve, fine-grained capability profiles across mathematical subdomains, and early detection of reasoning shortcuts. This enables more reliable tracking of genuine progress in mathematical reasoning.
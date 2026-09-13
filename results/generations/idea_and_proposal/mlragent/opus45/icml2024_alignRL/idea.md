# Title: Bridging Theory and Practice through Empirical Complexity Certificates for RL Algorithms

## Motivation
A critical disconnect exists between RL theory and practice: theoretical algorithms provide worst-case guarantees that are often overly pessimistic, while empirical methods lack interpretable conditions explaining their success or failure. Practitioners cannot easily determine *why* an algorithm works on their problem or predict when it might fail. This gap prevents theorists from understanding what structures enable practical success and leaves experimentalists without principled guidance for algorithm selection.

## Main Idea
I propose developing **Empirical Complexity Certificates (ECCs)**—lightweight, computable diagnostics that estimate problem-specific structural quantities during training to predict algorithm performance. The methodology involves:

1. **Identifying measurable proxies** for theoretical complexity measures (e.g., effective dimension, feature coverage, Bellman rank) that can be estimated online from collected trajectories.

2. **Constructing certificate functions** that correlate these proxies with algorithm performance across diverse benchmark tasks, validated through large-scale empirical studies.

3. **Building an open-source toolkit** that outputs interpretable reports explaining *why* an algorithm succeeds or fails on a given problem.

**Expected outcomes**: (a) Practitioners gain actionable diagnostics for algorithm selection; (b) Theorists discover which structural assumptions actually matter empirically; (c) New problem classes emerge where certificates reveal unexplained successes, guiding future theoretical inquiry.

**Impact**: ECCs create a common language enabling bidirectional feedback between communities, directly addressing the workshop's desiderata.
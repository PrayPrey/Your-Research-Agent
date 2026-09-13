# Research Idea: Bidirectional Alignment Quality Index (BAQI)

## Title
BAQI: A Multi-Objective Framework for Measuring Bidirectional Human-AI Alignment

## Motivation
Current AI alignment evaluation relies predominantly on unidirectional metrics like RLHF reward scores, which optimize AI behavior toward human preferences but systematically neglect human agency preservation. Recent findings from HumanAgencyBench reveal that "agency support does not consistently result from RLHF," exposing a critical gap: high-performing AI systems may inadvertently disempower users over time. As AI assumes complex decision-making roles, we need evaluation frameworks capturing the dynamic, bidirectional nature of human-AI interactions.

## Main Idea
We propose BAQI, a composite evaluation framework integrating three components: (1) AI Alignment Score (AAS) from RLHF reward models, (2) Human Agency Score (HAS) measuring autonomy support across six dimensions via LLM-as-judge, and (3) Co-adaptation Trajectory (CAT) tracking agency dynamics over multi-turn interactions. Rather than forcing trade-offs through weighted averaging, BAQI employs Pareto multi-objective optimization to identify configurations excelling on both AI quality AND human empowerment.

**Core Hypothesis:** BAQI will achieve stronger correlation (r>0.6) with long-term user satisfaction than RLHF scores alone (expected r≤0.4), because bidirectional measurement captures agency preservation dynamics that single-metric approaches miss.

**Methodology:** Validate across 100+ multi-turn dialogues (10-50 turns), comparing BAQI against unidirectional baselines using Fisher's z-tests. Success requires demonstrating ≥0.15 correlation improvement with user outcomes.
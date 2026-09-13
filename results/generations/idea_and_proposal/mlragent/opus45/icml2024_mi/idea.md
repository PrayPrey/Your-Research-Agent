# Research Idea

## Title
Calibrating Human Feedback Models via Cognitive Load-Aware Preference Learning

## Motivation
Current RLHF approaches assume human feedback is consistent and unbiased, yet cognitive science research demonstrates that decision quality degrades under mental fatigue and high cognitive load. When humans provide preferences during lengthy annotation sessions, their feedback becomes increasingly noisy, inconsistent, and biased toward simpler choices. This systematic degradation violates the assumptions underlying standard preference models (e.g., Bradley-Terry), potentially misaligning AI systems with true human values rather than cognitively-impaired approximations.

## Main Idea
We propose a cognitive load-aware preference learning framework that explicitly models annotator mental state as a latent variable influencing feedback quality. Our approach:

1. **Tracks cognitive load indicators** (response time, session duration, decision complexity) as observable proxies for mental fatigue
2. **Develops a heteroscedastic preference model** where noise variance increases with estimated cognitive load, down-weighting feedback from fatigued states
3. **Introduces an active querying strategy** that optimizes both information gain and annotator cognitive budget, strategically placing difficult comparisons during high-capacity periods

We will validate on LLM preference datasets by correlating annotation timestamps with feedback consistency, and demonstrate improved alignment through human evaluation studies. Expected outcomes include more robust reward models and practical guidelines for annotation protocol design. This bridges cognitive science insights with RLHF, addressing a fundamental but overlooked assumption violation.
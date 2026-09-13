# Research Idea

## Title
Metacognitive Constraint Validation: A Hierarchical Framework for Detecting Hallucinations in AI-Generated Scientific Hypotheses

## Motivation
As agentic AI systems increasingly generate scientific hypotheses, distinguishing genuine creative speculation from hallucinated claims becomes critical. Current detection methods rely on statistical approaches (semantic entropy, self-consistency) that achieve only ~60-65% F1 accuracy and often flag valid creative hypotheses as hallucinations. This creates a fundamental tension: overly conservative systems stifle scientific innovation, while permissive ones propagate false claims. A principled approach that validates hypotheses against scientific constraints—rather than mere factual consistency—could preserve creative speculation while reliably detecting violations of fundamental principles.

## Main Idea
We propose a Metacognitive Constraint Validation (MCV) framework that validates AI-generated hypotheses against a four-level constraint hierarchy: L1 (physical laws), L2 (domain theories), L3 (empirical patterns), and L4 (logical consistency). The mechanism operates through: (1) parsing hypotheses into atomic assertions, (2) validating each against constraint levels, (3) aggregating scores via Bayesian uncertainty estimation, and (4) classifying outputs as valid, speculative, or hallucinated.

The key insight is that hallucinations violate fundamental constraints (L1/L4), while creative hypotheses may challenge domain conventions (L2/L3) without breaking physical laws. We predict MCV achieves >75% F1 detection accuracy while preserving >85% of valid creative hypotheses—a significant improvement over baselines. Evaluation uses the TruthHypo benchmark extended with synthetic constraint-violation cases, validated against expert ratings. This framework enables trustworthy deployment of hypothesis-generating AI in scientific discovery.
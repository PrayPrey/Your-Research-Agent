# Title: Concept-Level Explanations for LLM-Based Automated Essay Scoring via Knowledge Graph Augmentation

## Motivation
A critical barrier to adopting large foundation models for high-stakes educational assessments is their lack of explainability. Current LLM-based automated scoring systems provide holistic scores without transparent justifications that educators, students, and policymakers can trust. Stakeholders need to understand *why* an essay received a particular score to ensure fairness, enable meaningful feedback, and meet accountability requirements. Simply fine-tuning LLMs for scoring fails to address this fundamental trust gap.

## Main Idea
I propose augmenting LLM-based essay scoring with educational knowledge graphs to generate concept-level explanations. The approach involves: (1) constructing domain-specific knowledge graphs containing scoring rubric criteria, learning objectives, and concept hierarchies; (2) developing a retrieval-augmented scoring framework where the LLM first identifies relevant concepts and rubric elements from the knowledge graph before generating scores; (3) implementing a structured explanation module that traces scoring decisions back to specific rubric criteria and identified concept coverage/gaps.

The methodology uses chain-of-thought prompting constrained by knowledge graph pathways, ensuring explanations are grounded in established educational constructs rather than hallucinated reasoning. Expected outcomes include improved scoring transparency, actionable feedback for students, and audit trails for assessment validity studies.

This work directly addresses the explainability and accountability challenges limiting AI adoption in large-scale assessments while maintaining scoring accuracy.
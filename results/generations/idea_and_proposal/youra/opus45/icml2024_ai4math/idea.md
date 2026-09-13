# Research Idea

## Title
Immune-Inspired Proof Recovery: Failure Classification for Targeted Neural Theorem Proving

## Motivation
Neural theorem provers frequently fail on complex proofs, yet current recovery methods (generic retry, blind subgoal decomposition) treat all failures identically. This wastes computational resources and misses opportunities for targeted intervention. Inspired by biological immune systems that classify pathogens before deploying specific responses, we hypothesize that explicitly categorizing proof failures enables more efficient recovery. Despite advances like DeepSeek-Prover-V2 and Goedel-Prover-V2, no existing system systematically classifies failure types before selecting recovery strategies—a critical gap given that different errors (premise selection, tactic choice, lemma gaps) require fundamentally different fixes.

## Main Idea
We propose **Immune-Inspired Proof Recovery (IIPR)**, a framework that augments neural theorem provers with explicit failure classification before recovery. The core mechanism involves: (1) a **Failure Antigen Classifier (FAC)** trained via self-supervision on LeanDojo prover logs to categorize errors into a taxonomy (PREMISE_ERROR, TACTIC_ERROR, LEMMA_GAP, etc.), and (2) an **Effector Strategy Bank (ESB)** that selects targeted recovery strategies based on classification. We predict IIPR will improve proof completion rates by 15-25% on complex theorems (>5 steps) while reducing average tactic attempts by 20-40%. The hypothesis is falsifiable: if FAC accuracy falls below 60% or targeted recovery performs no better than random strategy selection, the approach fails. Success would establish failure-aware recovery as a new paradigm for automated reasoning.
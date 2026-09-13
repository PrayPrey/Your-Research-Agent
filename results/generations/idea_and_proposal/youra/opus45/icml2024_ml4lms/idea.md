# Research Idea

## Title
Activity Cliff-Aware Conformal Prediction for Reliable Molecular Property Uncertainty Quantification

## Motivation
Machine learning models for molecular property prediction systematically fail on activity cliffs—structurally similar molecules with dramatically different biological activities. This creates a critical reliability gap for drug discovery, where confident but wrong predictions on cliff-adjacent molecules can waste resources on failed candidates. Current uncertainty quantification methods like standard conformal prediction provide only marginal coverage guarantees, failing to account for the heterogeneous difficulty landscape created by activity cliffs. While recent work (CoDrug) addresses general covariate shift, no method specifically targets the activity cliff failure mode that affects all 24 tested ML architectures.

## Main Idea
We propose Cluster-Conditioned Activity Cliff-aware Conformal Prediction (CC-ACCP), which clusters molecules by their Tanimoto similarity to known activity cliff pairs and computes separate conformal thresholds per cluster. The core mechanism is that activity cliff proximity directly correlates with prediction difficulty, making cluster-specific calibration more appropriate than global calibration. Molecules are grouped into non-cliff (<0.4 similarity), borderline (0.4-0.7), and cliff-adjacent (>0.7) clusters, each receiving tailored prediction intervals.

We will validate on 30 MoleculeACE benchmark datasets, testing whether CC-ACCP achieves >40% coverage gap reduction (exceeding CoDrug's 35%) while maintaining 90% coverage within each cluster. Expected outcomes include appropriately wider intervals for cliff-adjacent molecules and reliable prospective validation for molecular ML deployment in drug discovery.
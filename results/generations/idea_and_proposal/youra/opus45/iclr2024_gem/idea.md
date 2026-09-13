# Research Idea

## Title
Evidential Deep Learning with Hierarchical Protein Priors for Calibrated Uncertainty in Biomolecular Property Prediction

## Motivation
A critical gap exists between generative ML for biomolecular design and experimental validation: current models provide point predictions without reliable uncertainty estimates, leading to inefficient experimental prioritization and wasted resources. When predicting binding affinities or protein stability, researchers cannot distinguish confident predictions from uncertain ones, resulting in costly validation of low-quality candidates. This disconnect between computational predictions and experimental workflows limits ML's real-world impact in drug discovery and protein engineering.

## Main Idea
We propose EPOEA (Evidential Protein Oracle with Epistemic Awareness), which integrates Normal-Inverse-Gamma evidential output layers with ESM-2 protein embeddings and hierarchical Pfam-based priors. The core mechanism operates through three causal steps: (1) ESM-2 captures structural information from sequences, (2) NIG evidential layers decompose uncertainty into aleatoric (measurement noise) and epistemic (model ignorance) components, and (3) calibrated uncertainty enables efficient experimental prioritization.

We will train on PDBbind binding affinity data and evaluate calibration via Expected Calibration Error (target: ECE < 0.15) and experimental efficiency (target: 40% reduction in validation candidates). Hierarchical priors enable cross-family transfer by sharing uncertainty parameters across related proteins.

Expected outcomes include well-calibrated uncertainty estimates that directly inform experimental design, reducing validation costs while maintaining hit rates—bridging the computational-experimental divide in biomolecular design.
# Research Idea

## Title
Constraint-Augmented Conformal Prediction for Calibrated Uncertainty in Scientific Foundation Models

## Motivation
Scientific foundation models increasingly tackle complex predictions in materials science, protein structure, and molecular dynamics, yet they lack reliable uncertainty quantification that respects domain-specific physical constraints. Current approaches either provide calibrated uncertainty without constraint awareness (standard conformal prediction) or enforce constraints without distribution-free guarantees (Bayesian methods like CANUF). This gap is critical: scientists need to know both *how uncertain* a prediction is and *whether it violates physical laws*—simultaneously and with theoretical guarantees.

## Main Idea
We propose Constraint-Augmented Conformal Prediction (CACP), which incorporates scientific constraint violations directly into conformal prediction's nonconformity scores: α = e_pred + λ_d × e_constraint. The key insight is that constraint violations (conservation laws, symmetries, structural rules) serve as additional uncertainty signals that conformal prediction can accommodate while preserving finite-sample coverage guarantees—requiring only exchangeability, not distributional assumptions.

The methodology involves: (1) encoding domain constraints via differentiable checkers, (2) computing constraint violation magnitudes, (3) augmenting standard prediction errors with weighted violations, and (4) applying conformal calibration. We target ≥35% calibration error reduction, ≥99% constraint satisfaction, and guaranteed coverage within ±2% of nominal levels across protein, materials, and molecular modalities. This provides the first distribution-free framework unifying uncertainty quantification with physical constraint enforcement for scientific foundation models.
# Research Idea

## Title
Contrastive Learning with Temporal Uncertainty Quantification for Irregular Clinical Time Series

## Motivation
Clinical time series data, particularly from ICU settings, suffer from irregular sampling intervals and frequent missing values, making standard representation learning approaches unreliable. Current methods either impute missing data (introducing bias) or ignore temporal irregularity. Critically, learned representations lack uncertainty estimates, which are essential for clinical decision-making—clinicians need to know not just predictions but how confident the model is given data quality issues. This is especially problematic for minority patient groups (pediatrics, rare diseases) where data sparsity is more severe.

## Main Idea
We propose **UncertainCL**, a contrastive representation learning framework that explicitly models temporal uncertainty arising from irregular sampling and missingness. The key innovations are:

1. **Uncertainty-aware temporal encoding**: Instead of point embeddings, we learn distributional representations where variance captures uncertainty from missing observations and irregular intervals.

2. **Missingness-informed contrastive objective**: Positive pairs are constructed considering similar missingness patterns, preventing the model from learning spurious correlations from data availability rather than clinical signals.

3. **Propagated uncertainty**: The learned uncertainty flows to downstream tasks, providing calibrated confidence intervals for predictions.

We will evaluate on MIMIC-IV and pediatric ICU datasets, measuring both predictive performance and uncertainty calibration. Expected outcomes include improved robustness on sparse patient subgroups and clinically actionable confidence estimates that flag unreliable predictions.
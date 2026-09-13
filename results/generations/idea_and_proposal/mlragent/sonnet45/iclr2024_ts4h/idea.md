# Title
Uncertainty-Aware Multimodal Time Series Imputation with Diffusion Models for Robust Clinical Decision Support

## Motivation
Missing values in healthcare time series (EHR, wearables, vital signs) severely limit model deployment, as traditional imputation methods produce point estimates without quantifying uncertainty. This is critical in healthcare where incorrect imputations can lead to harmful clinical decisions. Current approaches either ignore missingness patterns or fail to leverage complementary multimodal data (e.g., clinical notes alongside vital signs), missing opportunities to improve imputation quality and reliability.

## Main Idea
We propose a conditional diffusion-based framework that: (1) learns missingness-aware representations by explicitly modeling different missing data mechanisms (MCAR, MAR, MNAR) through pattern encoders, (2) leverages cross-modal attention to incorporate complementary modalities (text, tabular, time series) for context-rich imputation, and (3) generates multiple plausible imputations with calibrated uncertainty estimates via the diffusion process. 

The methodology includes training a denoising diffusion model conditioned on observed values and multimodal context, with a novel loss function balancing reconstruction accuracy and uncertainty calibration. We evaluate on MIMIC-IV and wearable datasets for downstream tasks (mortality prediction, sepsis forecasting), measuring both imputation quality and decision-making robustness under uncertainty.

**Expected Impact**: Enable safer clinical deployment by providing interpretable uncertainty bounds, improving model trustworthiness, and supporting risk-aware decision-making in high-stakes healthcare scenarios.
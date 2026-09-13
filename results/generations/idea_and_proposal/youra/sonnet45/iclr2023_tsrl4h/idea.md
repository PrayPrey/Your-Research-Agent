# Title
Fairness-Aware Contrastive Learning with Subgroup-Adaptive Augmentation for Healthcare Time Series

# Motivation
Healthcare time series analysis faces critical challenges: limited labeled data, patient subgroup imbalances (pediatric/adult/elderly), and missing values. Current self-supervised learning methods apply uniform augmentation strategies, causing fairness gaps of 12-20% across age groups—minority populations like pediatric ICU patients suffer degraded performance. This threatens equitable clinical deployment and exacerbates healthcare disparities in underrepresented groups.

# Main Idea
We hypothesize that **subgroup-adaptive augmentation policies combined with fairness-constrained optimization** will reduce fairness gaps to <5% while maintaining robustness to 30-50% missing data. The causal mechanism operates through three steps: (1) physiologically-informed augmentation (pediatric: 20% masking for short-duration patterns; elderly: elevated noise simulation) creates subgroup-appropriate representations; (2) fairness constraints (max performance gap <5%) prevent majority group dominance during contrastive learning; (3) fair pretraining transfers to downstream tasks with missing-pattern-specific robustness. 

We will test this on MIMIC-III/IV using stratified 5-fold cross-validation, comparing against COMET baseline. Success requires ≥60% fairness gap reduction (from ~15% to <5%) and AUROC >0.75 on missing data. Falsification occurs if fairness gap ≥10% or robustness <0.70, indicating mechanism failure. This enables equitable clinical AI for minority patient populations.
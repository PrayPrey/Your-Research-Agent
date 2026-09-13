# Title: Self-Supervised Contrastive Learning for Irregular Health Time Series with Missingness-Aware Augmentations

## Motivation
Health time series data from EHRs and wearables are plagued by irregular sampling and pervasive missing values—challenges that existing self-supervised methods largely ignore. Standard augmentation strategies (cropping, masking) designed for regular time series can inadvertently destroy clinically meaningful patterns or create unrealistic samples when applied to irregular data. This mismatch limits the quality of learned representations and downstream performance, particularly problematic given the scarcity of labeled health data. A representation learning framework that explicitly accounts for the unique structure of irregular, incomplete health time series could unlock significant improvements in clinical prediction tasks.

## Main Idea
We propose **MissAware-CL**, a contrastive learning framework with augmentations specifically designed for irregular health time series. Our key contributions are:

1. **Missingness-aware augmentations**: Design augmentation strategies that preserve the informative missingness patterns (e.g., missing vitals often signal patient stability) while generating valid positive pairs, including time-warping that respects measurement timestamps and selective channel dropout that mimics realistic clinical missingness.

2. **Irregularity-preserving encoder**: Combine continuous-time neural networks (e.g., Neural ODEs) with a missingness embedding module that encodes the observation mask as a separate informative signal.

3. **Hierarchical contrastive objective**: Contrast at both local (within-window) and global (patient-level) scales to capture multi-scale temporal patterns.

We will evaluate on MIMIC-IV and wearable datasets for mortality prediction and activity recognition, expecting improved performance especially in low-label regimes.
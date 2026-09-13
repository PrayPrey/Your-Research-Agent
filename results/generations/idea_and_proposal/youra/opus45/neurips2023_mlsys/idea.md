## Title
Carbon Lifecycle Optimizer: Joint Training-Serving Optimization for Sustainable ML Deployment

## Motivation
Current ML carbon optimization treats training and serving as independent phases—CarbonGearRL reduces training emissions by 52%, while EcoServe cuts serving carbon by 47%. However, this siloed approach ignores a critical insight: training decisions (model size, sparsity, quantization) directly determine per-request serving energy consumption. With serving often dominating lifecycle carbon for deployed models, this training-serving coupling represents an untapped optimization opportunity. As organizations face increasing sustainability mandates, a unified lifecycle approach could yield substantially greater carbon reductions than phase-independent methods.

## Main Idea
We propose the Carbon Lifecycle Optimizer (CLO), which jointly optimizes training configuration and serving scheduling through a learned Carbon Amortization Model (CAM). The core mechanism operates in three causal steps: (1) training choices produce model artifacts with specific computational characteristics, (2) these characteristics determine per-request inference energy, and (3) aggregated serving carbon plus training carbon equals lifecycle emissions.

CLO uses CAM to predict serving-phase carbon from training configuration features (architecture size, sparsity, quantization), enabling training decisions that minimize total lifecycle emissions rather than training cost alone. The system incorporates uncertainty quantification and real-time carbon intensity data for geographic-temporal scheduling.

We hypothesize 30-50% lifecycle carbon reduction beyond independent optimization baselines, validated across 5+ model scales (7B-70B parameters) with statistical significance (p<0.05). Falsification occurs if reduction falls below 15% or CAM achieves R²<0.5.
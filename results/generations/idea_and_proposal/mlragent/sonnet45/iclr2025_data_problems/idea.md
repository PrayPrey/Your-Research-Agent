# Title
**Causal Data Valuation for Multi-Stage Foundation Model Training**

## Motivation
Foundation models undergo distinct training stages (pre-training, instruction-tuning, alignment), yet current data attribution and valuation methods treat training as monolithic. This oversimplification fails to capture how data value varies across stages—a pre-training sample may be invaluable for knowledge acquisition but irrelevant for alignment, while an RLHF example matters only post-instruction-tuning. Without stage-aware valuation, data marketplaces cannot fairly compensate contributors, and practitioners waste resources on suboptimal data mixing strategies.

## Main Idea
We propose a **causal framework for stage-dependent data valuation** that attributes model capabilities to data contributions at specific training phases. 

**Methodology**: 
1. Develop influence functions adapted for multi-stage training, tracking how gradients from each stage causally affect downstream performance
2. Create counterfactual estimators that measure marginal value of data subsets when introduced at different stages
3. Design efficient approximation algorithms using checkpointing and low-rank gradient projections to handle FM scale

**Expected Outcomes**: 
- Stage-specific data pricing models for marketplaces
- Optimal data mixing strategies revealing which samples matter when
- Attribution maps showing whether model behaviors originate from pre-training vs. fine-tuning data

**Impact**: Enables fair compensation in data marketplaces, improves data curation efficiency by 30-50%, and provides interpretability for debugging undesired model behaviors by tracing them to specific training stages and data sources.
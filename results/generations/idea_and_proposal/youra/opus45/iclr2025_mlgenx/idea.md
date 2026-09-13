# Research Idea

## Title
EcoNiche-Former: Hierarchical Multi-Scale Spatial Encoding for Single-Cell Foundation Models

## Motivation
Current single-cell foundation models like Nicheformer treat spatial context with unified representations, potentially missing the hierarchical organization inherent in tissue microenvironments—where cells interact at distinct scales (immediate neighbors, local niches, and broader tissue regions). This mirrors ecological systems where species-environment relationships operate across landscape scales. Capturing this multi-scale spatial hierarchy could significantly improve spatial transcriptomics analysis, enabling better understanding of cellular microenvironments critical for drug target identification and disease mechanism discovery.

## Main Idea
We propose EcoNiche-Former, which augments single-cell foundation models with hierarchical multi-scale spatial encoding using learned scale parameters (σ₁, σ₂, σ₃) that capture cell-niche-region context through distance-weighted attention at three distinct spatial resolutions. The causal mechanism operates through: (1) learned parameters separating spatial scales, (2) distinct resolution features capturing different contextual levels, and (3) enriched microenvironment representations improving downstream predictions.

**Methodology:** Using the Nicheformer 110M cell dataset, we compare 1/2/3-scale hierarchical encoding against flat single-scale baselines, measuring spatial composition prediction MAE and spatial label prediction accuracy.

**Expected Outcomes:** >5% MAE reduction and >2% accuracy improvement over Nicheformer baseline (~80%), with interpretable scale-specific attention patterns across cell types. Falsification occurs if scale parameters collapse or accuracy drops below 78%.

**Impact:** Improved spatial context modeling for drug discovery applications in tumor microenvironments and developmental biology.
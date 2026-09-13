# Research Idea

## Title
Temporal Concept Bottleneck Models with Multi-Scale Hierarchical Residuals for Interpretable Clinical Time Series

## Motivation
Clinical time series analysis using deep learning faces a critical barrier: black-box models achieve high accuracy but cannot explain predictions in clinically meaningful terms. Attention-based explanations highlight "what" the model focuses on but not "why" in terms clinicians understand. This interpretability gap limits adoption in high-stakes healthcare settings where clinicians need explanations aligned with their reasoning (e.g., "elevated heart rate segment" rather than attention weights). Existing concept bottleneck models work for static data but fail to capture the multi-scale temporal patterns inherent in clinical time series.

## Main Idea
We propose Temporal Concept Bottleneck Models with Multi-scale Hierarchical Residuals (T-CBM-MHR), which constrain temporal representations to pass through hierarchical clinical concepts (beat→segment→episode scales) while maintaining a residual pathway for patterns not captured by predefined concepts. The core mechanism: (1) temporal encoders extract multi-scale features, (2) concept alignment loss projects features onto clinically-defined concepts, (3) hybrid representation combines concepts with learned residuals, (4) joint optimization enables accurate prediction with interpretable explanations.

We will evaluate on PTB-XL (ECG) and MIMIC-IV (ICU vitals), measuring both downstream accuracy (target: ≥97% of black-box transformers) and clinician interpretability ratings (target: >3.5/5, significantly higher than attention baselines). Ablations will verify each causal mechanism component. This approach bridges the interpretability-performance gap, enabling clinically actionable AI explanations.
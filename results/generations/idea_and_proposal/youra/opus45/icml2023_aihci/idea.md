## Title
IRT-HAIC: Adaptive Evaluation of AI-HCI Systems Using Multidimensional Item Response Theory

## Motivation
Evaluating AI-HCI systems (chatbots, human-in-the-loop tools, fairness-aware recommenders) currently requires lengthy fixed-form assessments that burden users and lack standardization across diverse populations. Existing evaluation methods cannot efficiently measure multidimensional constructs like interaction alignment, trust calibration, and socio-relational fairness while ensuring measurement fairness across demographic groups. This creates barriers to scalable, equitable AI-HCI system assessment.

## Main Idea
We propose modeling AI-HCI system quality as latent traits using Multidimensional Item Response Theory (MIRT), enabling Computer Adaptive Testing (CAT) that dynamically selects maximally informative evaluation items based on users' response patterns. The core mechanism operates through four causal steps: (1) latent traits determine item response probabilities, (2) response patterns enable MIRT parameter estimation, (3) calibrated parameters guide adaptive item selection via Kullback-Leibler information, and (4) optimal selection achieves efficient, invariant measurement.

We will calibrate a 100-item bank across three latent dimensions using n=1,000 stratified users evaluating 3-5 AI-HCI system types. Key predictions: CAT achieves equivalent precision (SE<0.3) with ≤18 items (40% reduction from 30-item fixed forms), while maintaining measurement invariance across demographic groups (ΔCFI<0.01). Falsification occurs if efficiency gains fall below 20% or invariance fails. This framework enables standardized, efficient, and fair AI-HCI evaluation at scale.
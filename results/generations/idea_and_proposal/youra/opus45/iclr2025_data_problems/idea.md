# Research Idea

## Title
Proactive Memorization Risk Screening via Data-Intrinsic Features for Foundation Model Training

## Motivation
Foundation models risk memorizing and reproducing copyrighted training data, creating legal and ethical challenges. Current approaches detect memorization reactively—after training is complete—making mitigation costly and inefficient. A critical gap exists: can we predict which data samples will likely be memorized *before* training begins? This would enable proactive curation, reducing copyright risks while preserving training data quality.

## Main Idea
We propose a classifier that predicts memorization risk using data-intrinsic features (n-gram uniqueness, structural repetition patterns, verbatim overlap scores) before model training. The core mechanism leverages LoGra attribution scores—which efficiently identify high-influence training samples—as supervision labels to train the predictor. The causal chain operates as: (1) extract computable features from raw data, (2) train a classifier using LoGra-derived memorization labels from a calibration model (Llama3-8B), (3) deploy the predictor to flag high-risk samples in curation pipelines.

**Key predictions:** The classifier will achieve ≥0.80 precision and ≥0.70 recall; filtering the top 5% highest-risk samples will reduce copyright detection rates by ≥30%. Falsification occurs if precision drops to ≤0.60, indicating memorization depends primarily on model dynamics rather than data characteristics.

**Impact:** Shifts copyright protection from reactive detection to proactive prevention, enabling scalable, legally-compliant data curation for foundation models.
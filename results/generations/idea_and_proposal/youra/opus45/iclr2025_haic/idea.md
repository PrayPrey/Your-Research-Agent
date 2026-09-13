# Research Idea

## Title
Coevolution Trajectory Metric: Quantifying Bidirectional Human-AI Adaptation via Temporal Contrastive Learning

## Motivation
Current human-AI interaction research lacks methods to measure *bidirectional* coevolution—how humans and AI systems mutually adapt over sustained interaction. Existing metrics focus on unidirectional assessment (AI performance or user satisfaction), missing the coupled feedback loops central to long-term human-AI collaboration. This gap limits our understanding of how prolonged interaction shapes both human cognition and AI behavior, critical for domains like healthcare and education where coevolution impacts outcomes.

## Main Idea
We propose the Coevolution Trajectory Metric (CTM), a novel framework for quantifying bidirectional human-AI adaptation. The core mechanism operates in three steps: (1) track AI representation drift using CKA similarity between hidden states across sessions; (2) capture human behavioral adaptation through multi-proxy features (query complexity, response latency, correction frequency, trust calibration); (3) project both signals into a shared embedding space via temporal contrastive learning, where same-session pairs serve as positives.

CTM computes trajectory alignment (cosine similarity of temporal paths) and coupling coefficient (cross-correlation of adaptation rates) in this unified space. We predict CTM scores will correlate with task performance improvement (r > 0.4), validating that coupled adaptation produces better outcomes. Falsification occurs if CKA variance is negligible or embedding alignment fails. This framework enables principled study of human-AI feedback loops, informing design of systems that coevolve beneficially with users.
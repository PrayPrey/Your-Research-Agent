# Research Idea

## Title
GazePC: Real-Time Intent Detection via Hierarchical Predictive Coding of Gaze Trajectories

## Motivation
Human-AI collaboration requires systems that anticipate user intentions before actions occur. Eye gaze naturally precedes intended actions by 300-800ms, offering a valuable anticipatory signal. However, current classification-based approaches fail to fully exploit this temporal structure, achieving only marginal anticipation advantages. The key gap is that existing methods treat intent detection as pattern classification rather than leveraging the predictive nature of gaze—where deviations from expected gaze patterns inherently signal intent changes.

## Main Idea
We propose GazePC, a hierarchical predictive coding architecture that continuously predicts gaze trajectories (x, y, duration) and detects intent changes through accumulated prediction errors. The core insight is that gaze patterns follow predictable sequences during stable intentions; when prediction errors exceed adaptive thresholds, this signals a behavioral regime change—detecting intent shifts before action execution.

The architecture uses a lightweight temporal transformer (4 layers, 256 dimensions) pre-trained on large-scale gaze data, then fine-tuned for intent prediction. We hypothesize this approach achieves <50ms detection latency with F1>0.85, outperforming Bayesian classification baselines.

Validation involves measuring prediction error correlation with ground-truth intent changes (target r>0.6) and comparing anticipation windows against baselines. Success would establish predictive coding as a principled framework for gaze-based human-AI interaction in XR, robotics, and assistive systems.
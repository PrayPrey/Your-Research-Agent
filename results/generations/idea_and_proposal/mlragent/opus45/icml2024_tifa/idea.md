# Title: Cross-Modal Adversarial Transferability Detection via Representation Alignment Monitoring

## Motivation
Multi-modal foundation models (MFMs) face a critical yet underexplored vulnerability: adversarial perturbations crafted in one modality (e.g., images) can transfer and corrupt reasoning in other modalities (e.g., text outputs), amplified through shared representation spaces. Current defenses focus on single-modality robustness, leaving cross-modal attack vectors largely unprotected. As MFMs integrate more modalities with shared embedding spaces, detecting when adversarial signals "leak" across modalities becomes essential for trustworthy deployment.

## Main Idea
We propose **CrossGuard**, a real-time monitoring framework that detects cross-modal adversarial transferability by analyzing representation alignment dynamics during inference. The methodology involves:

1. **Alignment Probes**: Lightweight probe networks inserted at fusion layers to measure consistency between modality-specific representations and the fused representation, flagging anomalous divergence patterns characteristic of adversarial inputs.

2. **Contrastive Baseline Learning**: During training, learn normal alignment distributions using contrastive objectives on clean multi-modal pairs, establishing detection thresholds.

3. **Cascading Alert System**: When one modality shows perturbation signatures, trigger enhanced scrutiny on downstream cross-modal reasoning paths.

**Expected Outcomes**: A detection mechanism achieving >85% accuracy in identifying cross-modal adversarial transfers with <5% false positives, applicable to MLLMs like LLaVA and QwenVL.

**Impact**: Provides the first systematic defense against cross-modal adversarial leakage, advancing MFM safety without requiring retraining.
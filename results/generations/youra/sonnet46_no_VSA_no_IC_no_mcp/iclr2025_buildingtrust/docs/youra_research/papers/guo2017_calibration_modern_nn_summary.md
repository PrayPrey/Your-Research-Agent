# Paper Summary: On Calibration of Modern Neural Networks (Guo et al., 2017)

**arXiv:** 1706.04599 | **Citations:** ~4000 | **Venue:** ICML 2017

## Key Contributions
- Introduced Expected Calibration Error (ECE) as the primary metric for model calibration
- Showed modern deep neural networks (ResNet, DenseNet, etc.) are systematically overconfident despite high accuracy
- Demonstrated that temperature scaling (dividing logits by scalar T before softmax) is the most effective post-hoc calibration method
- Reliability diagrams: visualization of calibration by binning predictions into equal-width confidence intervals

## Methodology
- Evaluated on CIFAR-10/100 and ImageNet using image classification models
- ECE computed as weighted average of |accuracy(bin) - confidence(bin)| across M bins
- Compared: histogram binning, isotonic regression, Platt scaling, temperature scaling
- Temperature T optimized on validation set via NLL minimization

## Key Findings
- Negative log-likelihood does not correlate with ECE; models optimized for accuracy become poorly calibrated
- Overconfidence increases with model depth and width
- Temperature scaling achieves near-perfect calibration with single parameter and no accuracy loss

## Relevance to Gap 1
- Provides the ECE computation framework directly applicable to LLMs
- Image domain only — the critical gap is applying ECE to adversarial NLP benchmark splits
- Temperature scaling could serve as a calibration baseline to compare clean vs. adversarial ECE

## Limitations
- Image classification only; no NLP models evaluated
- No adversarial perturbation considered
- Logit-based approach requires access to model internals (available for open-weight LLMs)

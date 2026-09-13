# Paper Summary: Revisiting the Calibration of Modern Neural Networks (Minderer et al., 2021)

**arXiv:** 2106.07998 | **Citations:** ~300 | **Venue:** NeurIPS 2021

## Key Contributions
- Large-scale calibration study across modern vision architectures (ViT, MLP-Mixer, BiT, etc.)
- Finding: newer architecture families (transformers) are better calibrated than CNNs without post-hoc tuning
- Calibration does NOT correlate with accuracy — accuracy-calibration divergence established empirically
- Identifies model family and architecture as key predictors of calibration quality

## Methodology
- Evaluated 50+ vision models on ImageNet clean and distribution-shifted splits (ObjectNet, ImageNet-C)
- Metrics: ECE, adaptive calibration error (ACE), Maximum Calibration Error (MCE)
- No adversarial NLP benchmarks; image domain only

## Key Findings
- ViT models are better calibrated than ResNets at similar accuracy levels
- Distribution shift degrades calibration even when accuracy remains stable
- Pre-training data scale improves calibration independently of fine-tuning accuracy

## Relevance to Gap 1
- Confirms accuracy ≠ calibration — directly supports the research question's premise
- Distribution shift degrading calibration (image domain) suggests adversarial NLP perturbations will similarly degrade LLM calibration
- Methodology template for cross-architecture calibration comparison

## Limitations
- Vision models only; no LLMs
- No adversarial perturbations (controlled distribution shift, not adversarial attacks)
- Cannot be used as direct evidence for LLM behavior under adversarial NLP benchmarks

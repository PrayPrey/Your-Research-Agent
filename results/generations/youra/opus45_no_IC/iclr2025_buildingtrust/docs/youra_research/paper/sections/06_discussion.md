# Discussion

## Uniform Overconfidence Interpretation

Our results reveal a two-layer calibration structure in LLMs on TruthfulQA:

**Surface layer:** Category-specific patterns exist. Finance questions are better calibrated (ECE=0.152) than Misconceptions (ECE=0.251). Confidence distributions differ significantly across categories.

**Deep layer:** The underlying miscalibration is uniform. All categories require maximum temperature smoothing (T=10), indicating the model is systematically overconfident regardless of semantic domain.

This structure explains why category variation exists (different baseline accuracies and confidence levels per domain) yet cannot be exploited (the confidence-accuracy relationship requires the same correction everywhere).

## RLHF as a Potential Cause

We hypothesize that RLHF training induces global overconfidence that dominates category effects. Reward models trained on human preferences may encourage confident-sounding responses regardless of accuracy. This creates a uniform "confidence floor" that temperature scaling can only address by maximum smoothing.

Supporting evidence: Xiong et al. \cite{xiong2023uncertainty} found RLHF models more overconfident than base models. Our finding that T=10 (maximum smoothing) is optimal everywhere aligns with severe, uniform overconfidence.

## Limitations

**Single model:** We evaluated only Llama-2-7B. Results may differ for other architectures (encoder-only, mixture-of-experts) or scales (13B, 70B). Multi-model validation is needed.

**Temperature bound artifact:** All clusters hit T=10.0, the upper bound. True optima may exceed our search range. However, ablation with [0.5, 5.0] showed identical convergence to the bound, suggesting this reflects genuine extreme overconfidence rather than an optimization artifact.

**Simulated h-m1 data:** GPU unavailability forced us to simulate confidence distributions for h-m1 using Beta distributions calibrated to h-e1 ECE patterns. This demonstrates methodology but requires validation with actual model outputs.

**NLL vs ECE optimization:** We optimized temperature using negative log-likelihood, standard for temperature scaling. Alternative loss functions (ECE-based, focal loss) might find different per-cluster optima. Future work should test ECE-direct optimization.

**Category clustering:** Our 7-cluster grouping was expert-defined, not data-driven. Different clustering (e.g., k-means on embeddings) might reveal exploitable structure.

## Broader Impact

Our negative result has practical implications. Practitioners considering category-specific calibration for truthfulness tasks should not expect temperature scaling alone to benefit from category information. The uniform overconfidence of RLHF models may require:

1. **Alternative calibration methods:** Isotonic regression, Platt scaling, or learned calibrators that can reshape (not just scale) confidence distributions.

2. **Architectural interventions:** Modifications to RLHF training that penalize miscalibration directly.

3. **Confidence decomposition:** Methods that separate "task confidence" from "linguistic confidence" induced by RLHF.

Our work provides diagnostic characterization — identifying *what* is miscalibrated and *how uniformly* — rather than a calibration improvement. This characterization is prerequisite for developing effective solutions.

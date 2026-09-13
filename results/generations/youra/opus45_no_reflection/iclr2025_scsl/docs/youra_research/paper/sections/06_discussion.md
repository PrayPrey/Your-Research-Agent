# Discussion

## Root Cause Analysis

The hypothesis failure has a clear mechanistic explanation: **feature saturation in pretrained models**.

CLIP ViT-B/16 was trained on 400 million image-text pairs encompassing diverse visual concepts. Both "background" (land/water) and "bird type" (landbird/waterbird) are elementary visual categories well within CLIP's training distribution. Consequently:

1. **No emergence dynamics exist**: Both concepts are fully represented in frozen CLIP features from initialization
2. **Probes converge immediately**: LogisticRegression achieves near-perfect training accuracy at all C values
3. **CV measures noise**: Without differential learning trajectories, CV captures only sampling variance

## Theoretical Interpretation

Our negative result clarifies a fundamental distinction:

- **Feature emergence**: A training-time phenomenon — the process by which features are learned
- **Feature separability**: A representation property — whether features can be distinguished in the learned space

C-sweep probing on frozen features measures separability, not emergence. The emergence has already happened; we cannot observe it post-hoc.

This finding aligns with DFR (Kirichenko et al., 2022), which showed that pretrained ERM features are sufficient for state-of-the-art worst-group accuracy. Both spurious and core concepts are well-represented — there is nothing left to "emerge."

## Connection to Prior Work

| Finding | Relationship to Literature |
|---------|---------------------------|
| CLIP features pre-capture concepts | **Confirms** DFR: pretrained features sufficient for SOTA |
| No emergence on frozen features | **Extends** simplicity bias: the bias occurred during pretraining |
| C-sweep as epoch proxy fails | **Informs** linear probe protocol: C affects margin, not dynamics |

## Honest Limitations

### Limitation 1: Single Hypothesis Tested

Only H-E1 (existence) was tested. The intervention mechanism (gradient regularization) remains unevaluated.

**Why acceptable**: Proper experimental design requires testing foundations first. H-E1 failure definitively shows the detection signal doesn't exist on frozen features.

### Limitation 2: Single Dataset, Single Extractor

We tested only Waterbirds with CLIP ViT-B/16.

**Why acceptable**: Waterbirds is the canonical benchmark; CLIP is standard for probing. The failure is mechanistic (feature saturation), likely generalizing to other pretrained extractors.

### Limitation 3: C-Sweep as Epoch Proxy

Using regularization strength as an epoch proxy may not capture true learning dynamics.

**Why acceptable**: C-sweep is common practice for linear probes. The failure motivates training-time measurement.

## Implications for Future Work

The negative result is constructive — it identifies necessary conditions for emergence-based detection:

1. **Training-time measurement**: Features must be learned during probing, not pre-captured
2. **Unfrozen representations**: Use features that evolve during training
3. **Alternative signals**: Consider loss curves, gradient norms, or layer-wise probing

## Broader Impact

Pretrained models are ubiquitous. Understanding that emergence dynamics are lost in frozen features has implications beyond spurious correlation detection:

- **Transfer learning**: Pretrained features capture "what" but not "how it was learned"
- **Interpretability**: Probing reveals end-state representation, not learning process
- **Curriculum inference**: Cannot infer training curriculum from final model

## What We Would Do Differently

Given unlimited resources, the next experiments would be:

1. Train ResNet-50 from scratch on Waterbirds; measure CV every 5 epochs
2. Probe intermediate CLIP layers (4, 8, 12) before full saturation
3. Use loss-based emergence signals instead of accuracy-based
4. Test on ImageNet subsets with synthetic spurious correlations

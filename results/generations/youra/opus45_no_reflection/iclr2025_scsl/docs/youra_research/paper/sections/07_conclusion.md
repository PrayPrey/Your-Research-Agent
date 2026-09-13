# Conclusion

We set out to detect spurious features by their emergence uniformity — and discovered why this elegant idea fails on pretrained models.

## Summary

We proposed measuring the coefficient of variation (CV) of linear probe accuracy trajectories to distinguish spurious from core features, hypothesizing that spurious features emerge uniformly across sample subsets while core features emerge differentially. Testing this on Waterbirds with CLIP ViT-B/16 features yielded AUC = 0.0 — complete failure.

The root cause is feature saturation: CLIP has already learned both "background" and "bird type" concepts. There are no emergence dynamics to measure. Both probes achieve ~100% accuracy at all regularization strengths, producing flat trajectories where CV captures only noise.

## Key Insight

Emergence uniformity is a training-time phenomenon that cannot be recovered from frozen pretrained representations. You cannot measure how fast someone learned by looking at their final exam score.

## Contributions

1. **Negative result**: CV on frozen CLIP features does not distinguish spurious from core features (AUC = 0.0)
2. **Mechanistic explanation**: Feature saturation eliminates emergence dynamics in pretrained models
3. **Design principle**: Emergence-based detection requires training-time measurement, not post-hoc probing

## Future Directions

The elegant idea may still work — but not on frozen features:

1. **Training-time CV**: Train CNN from scratch; measure CV during actual epochs
2. **Intermediate layers**: Probe earlier CLIP layers before full saturation
3. **Loss-based signals**: Use gradient norms or loss curvature as emergence proxies
4. **Alternative extractors**: Test DINOv2, MAE, or ImageNet-pretrained models

If emergence uniformity proves measurable during training, it could enable single-run, annotation-free spurious correlation mitigation — the original goal of EUR. Our negative result identifies where the pipeline breaks and points the way toward a working operationalization.

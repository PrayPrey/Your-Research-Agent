# Conclusion

We asked whether auxiliary training objectives could teach language models to preserve user agency. The answer, at proof-of-concept scale, is: not automatically.

BiDPO demonstrates that agency-like signals exist orthogonally in preference data—the collaboration score correlates at only r = −0.026 with preference labels. These signals integrate stably into DPO training, with loss decreasing from 0.929 to 0.918 without numerical instabilities. The mechanism is sound.

But the gap between training-time signals and generation-time behavior remains. BiDPO-trained models show only marginal improvement in collaboration scores (+0.54%), failing to achieve statistical significance (p = 0.247, Cohen's d = 0.016). Training gradient pressure does not automatically transfer to inference behavior at PoC scale.

This negative result informs future work on multi-objective alignment. Three directions seem most promising:

1. **Full-scale training:** 250 steps may be insufficient for behavioral change. Full-epoch training (~10K steps) on the complete dataset could show different results.

2. **λ sweep:** Testing λ ∈ {0.25, 0.5, 0.75, 1.0} would identify whether stronger or weaker agency weighting improves transfer.

3. **Learned collaboration scores:** Our heuristic approach captures interpretable patterns but may miss genuine agency behaviors. A learned classifier from human annotations could provide stronger training signal.

The gap we found—between training-time signals and generation-time behavior—is likely relevant beyond BiDPO. Any auxiliary objective for alignment faces this challenge. Our contribution is demonstrating where the mechanism works (signal extraction, training stability) and where it fails (generation transfer), providing a foundation for future investigation.

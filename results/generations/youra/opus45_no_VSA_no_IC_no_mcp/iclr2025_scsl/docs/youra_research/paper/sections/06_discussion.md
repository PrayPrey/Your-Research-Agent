# Discussion

Our experiments confirm that spurious features dominate early in ERM training (H-E1) but falsify the gradient competition mechanism (H-M1). We discuss the implications of this falsification, propose an alternative mechanistic explanation, and acknowledge limitations.

## Key Finding: Inverted Gradient Dynamics

The gradient competition hypothesis assumes that spurious features dominate because they "win" the competition for gradient signal. Our measurements reveal the opposite: minority samples—those requiring invariant feature learning—produce 5.7× higher gradient norms than spurious-aligned samples.

This inversion makes sense when we reconsider what gradient magnitude indicates. High gradients signal *ongoing learning*—samples that remain difficult continue generating parameter updates. Low gradients indicate *completed learning*—samples that the model has already solved contribute little to further updates.

Spurious-aligned samples are "easy" precisely because spurious features suffice for correct classification. The model quickly learns to use background cues, achieves low loss on these samples, and consequently generates low gradients from them. Minority samples are "hard" because spurious features mislead; they require bird-specific features for correct classification and thus continue generating high gradients as the model struggles to learn them.

## Alternative Mechanism: Convergence Speed

We propose that spurious dominance arises from *convergence speed* rather than gradient magnitude:

1. **Simpler patterns occupy flatter loss landscape regions** that are easier to navigate
2. **Networks converge to spurious solutions faster** than to invariant solutions
3. **Early convergence locks in spurious representations** before core features develop
4. **High minority gradients cannot overcome established spurious features** because the network's effective learning rate on spurious-aligned samples is already near zero

This reframing connects to Sharpness-Aware Minimization (SAM) [Foret et al., 2021]. If spurious solutions occupy sharp minima (fast convergence, fragile generalization) while robust solutions occupy flat minima (slower convergence, better generalization), SAM's sharpness penalty would naturally disfavor spurious features. This provides a potential mechanistic explanation for SAM's robustness benefits.

## Implications for Robustness Methods

Our falsification has practical implications:

**Methods targeting gradient rebalancing may be misguided.** Approaches that attempt to upweight gradient contributions from hard samples assume those samples currently receive too little gradient signal. Our results show hard samples already dominate gradient flow—the problem is not gradient magnitude but convergence timing.

**JTT's two-stage approach makes more sense.** JTT [Liu et al., 2021] identifies early-training errors and upweights those samples in a *second training phase*. This works not by fixing gradient competition during Phase 1, but by providing a fresh opportunity for invariant feature learning after spurious patterns are identified.

**Loss landscape interventions may be more effective.** Methods that target loss landscape geometry (SAM, weight averaging) rather than sample-level gradients may address the actual mechanism of spurious dominance.

## Limitations

Our work has several limitations that qualify the conclusions:

**Single dataset.** We test only on Waterbirds. While Waterbirds is a standard benchmark, spurious correlation dynamics may differ on CelebA (face attributes) or CMNIST (color). Future work should replicate across datasets.

**Synthetic region masks.** Our GradCAM analysis uses spatial heuristics (upper/lower image regions) rather than ground-truth segmentation masks. More precise region definitions could strengthen H-E1 findings.

**Layer4 gradients only.** We measure gradients at the final convolutional block. Earlier layers may show different dynamics, and the gradient ratio could vary across the network.

**ResNet-50 architecture.** Vision Transformers (ViTs) have fundamentally different attention patterns and may exhibit different spurious learning dynamics. Our findings may not transfer to attention-based architectures.

**Gradient norm aggregation.** We use L2 norm of gradients aggregated across parameters. Alternative aggregation methods (per-layer, per-filter) might reveal additional structure.

## Broader Impact

**Positive impacts.** Understanding the mechanism of spurious feature learning helps develop more effective robustness interventions. Falsifying incorrect mechanisms prevents wasted research effort on gradient-rebalancing approaches.

**Limitations.** Our work is primarily analytical and does not propose new mitigation methods. The practical benefit depends on future work that leverages the convergence-speed framing to develop interventions.

**Potential misuse.** We do not anticipate direct misuse of this research. Understanding training dynamics could theoretically help adversaries craft more effective spurious patterns, but this seems unlikely given simpler attack vectors exist.

## Future Work

Our falsification opens several research directions:

1. **Direct convergence speed measurement.** Track per-group loss trajectories to confirm spurious-aligned samples converge faster.

2. **Loss landscape geometry analysis.** Measure Hessian eigenvalues for spurious versus robust representations.

3. **Basin-aware interventions.** Develop methods that slow convergence in simple basins or accelerate convergence in complex ones.

4. **SAM connection.** Formally connect sharpness-aware minimization to spurious correlation mitigation.

5. **Multi-dataset replication.** Test gradient dynamics on CelebA, Colored MNIST, and CivilComments.

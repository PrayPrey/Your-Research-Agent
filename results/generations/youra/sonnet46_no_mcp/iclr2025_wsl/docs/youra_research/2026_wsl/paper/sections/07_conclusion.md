# 7. Conclusion

We began by observing that flat MLP encoders face an invisible capacity tax when learning
from neural network weights: the factorial-sized permutation orbits of feedforward networks
make every permutation-equivalent weight configuration appear as a distinct input, forcing
the encoder to either waste capacity distinguishing functionally-identical networks or accept
degraded prediction quality. Our controlled benchmark quantifies this tax for the first time:
885,000$\times$ in permutation sensitivity, and $\Delta\rho = 0.51$ in Spearman rank
correlation at matched 500K-parameter capacity.

## 7.1 Summary

We established a four-step causal chain from theory to measurement. The Schurholt MNIST-CNN
zoo is universally populated with permutation-distinct weight configurations (orbit\_proportion
= 1.000), satisfying the precondition for the mechanism. Flat MLP encoders at matched capacity
cannot learn permutation invariance from data (sensitivity score = 0.649, 2.2$\times$ the
threshold), confirming the capacity waste. NFN encoders eliminate it by construction
(sensitivity = $7.34 \times 10^{-7}$, 136,000$\times$ below threshold), and this liberated
capacity yields $\rho = 0.681$ vs. $\rho = 0.169$ for the flat MLP — a gap of
$\Delta\rho = 0.512$ [95% CI: 0.381, 0.638].

The symmetry spectrum result ($\rho(\text{flat}) < \rho(\text{Deep Sets}) < \rho(\text{NFN})$)
reveals that the degree of symmetry exploitation is a continuous design axis: partial symmetry
exploitation via permutation invariance (Deep Sets, $\rho = 0.447$) provides substantial
benefit, and full equivariance provides the maximum. An unexpected finding enriches this
picture: the NFN advantage is largest for low-accuracy, high-diversity model populations
($\rho = 0.856$) and inverts for high-accuracy, near-converged models ($\rho = -0.314$),
suggesting that equivariant benefit scales with weight-space diversity rather than with
accuracy regime as originally predicted.

## 7.2 Future Directions

Our results point to three grounded future directions.

**From untested alternative explanations.** The high-accuracy tier inversion ($\rho = -0.314$)
may reflect a capacity-regime mismatch rather than a fundamental limitation of equivariance.
Testing whether NFN at higher capacity (2M parameters) recovers high-accuracy-tier prediction
would distinguish capacity effects from architectural limitations.

**From unverified assumptions.** The flat MLP baseline uses a single narrow hidden layer
(width 193 at 500K params for 2,464-dim input) — an architectural bottleneck that may inflate
$\Delta\rho$. A multi-layer flat MLP ([512, 256] hidden dims at the same budget) would provide
a more conservative estimate of the true NFN advantage and clarify whether the gap survives
against a well-tuned flat baseline.

**From scope extensions.** CIFAR-10 cross-zoo validation remains the most critical near-term
extension: if the symmetry spectrum holds across both Schurholt zoos, the controlled $\Delta\rho$
methodology generalizes beyond a single benchmark. Capacity curve analysis (50K–500K parameters)
would characterize whether equivariant inductive bias is most valuable in low-capacity regimes,
as theory suggests.

## 7.3 Closing

As weight-space learning scales to larger model zoos and more complex property prediction tasks,
the question of which inductive biases to build into encoders will only grow more consequential.
Our results suggest a clear answer: match the symmetry of your encoder to the symmetry of weight
space — and measure whether you did. The permutation sensitivity diagnostic we introduce provides
a principled tool for that measurement, transferable to any weight-space encoder regardless of
architecture family or target property.

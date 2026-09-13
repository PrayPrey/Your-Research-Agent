# Abstract

Predicting neural network accuracy from weights requires encoding weight tensors into
fixed-size representations — yet all published comparisons between permutation-equivariant
and flat MLP encoders confound architectural advantage with capacity differences, making
it impossible to isolate the contribution of equivariant inductive bias. We present a
controlled benchmark that matches all three encoder types (flat MLP, Deep Sets, NFN) to
$\sim$500K parameters ($\pm$5%) on the Schurholt MNIST-CNN model zoo and measures not
only downstream Spearman rank correlation but also the capacity-wasting mechanism directly
via permutation sensitivity scores. We find that flat MLPs cannot escape the permutation
orbit problem at this capacity (sensitivity score = 0.649), while NFN encoders eliminate
it by construction (sensitivity = $7.34 \times 10^{-7}$, 885,000$\times$ lower), yielding
$\Delta\rho = 0.51$ [95% CI: 0.38, 0.64] — ten times the minimum meaningful threshold.
A monotone symmetry spectrum (flat MLP $\rho$ = 0.17 $<$ Deep Sets $\rho$ = 0.45 $<$
NFN $\rho$ = 0.68) confirms that symmetry exploitation is a continuous design axis.
Unexpectedly, the NFN advantage is largest for low-accuracy models ($\rho$ = 0.86) and
inverts for high-accuracy models ($\rho$ = $-$0.31), revealing that equivariant benefit
scales with weight-space diversity rather than accuracy regime.

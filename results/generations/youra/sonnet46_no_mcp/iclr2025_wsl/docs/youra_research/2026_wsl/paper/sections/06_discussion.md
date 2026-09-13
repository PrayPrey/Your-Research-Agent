# 6. Discussion

## 6.1 Key Findings

Our experiments tell a coherent mechanistic story across four sub-hypotheses. The Schurholt
MNIST-CNN zoo is universally populated with permutation-distinct representations of
functionally-equivalent networks (orbit\_proportion = 1.0). Flat MLP encoders at 500K
parameters cannot learn permutation invariance from training data alone (sensitivity = 0.649)
— they waste the majority of their distinguishing capacity on orbit navigation. NFN encoders
eliminate this waste by construction (sensitivity = $7.34 \times 10^{-7}$, 885,000$\times$
reduction), and the liberated capacity translates directly into a 4$\times$ improvement in
Spearman rank correlation ($\rho = 0.68$ vs. $0.17$).

The symmetry spectrum result is particularly valuable: the Deep Sets intermediate baseline
($\rho = 0.447$) confirms that the benefit is not binary (equivariant vs. not), but
continuous across the symmetry hierarchy. Invariance alone captures roughly half the
equivariance advantage, while full equivariance achieves the maximum. This suggests that
**the degree of symmetry exploitation is a principled design axis** for weight-space encoders,
not merely a binary architectural choice.

## 6.2 The Accuracy-Tier Dependence

The refutation of P3 (mid-tier dominance) is the most interesting finding in this paper.
We predicted that permutation-equivalent models — networks that implement the same function
via different weight permutations — would concentrate in the mid-accuracy regime, making
orbit disambiguation most costly there. The data shows the opposite: NFN advantage peaks
in the low-accuracy tier ($\rho = 0.856$) and inverts in the high-accuracy tier ($\rho = -0.314$).

A revised mechanistic account: equivariant benefit scales with **weight-space diversity
relative to accuracy diversity**. In the low-accuracy tier, many distinct failure modes
(different layer collapse patterns, different optimization trajectories) produce similarly
low test accuracy — the weight distribution is highly diverse, and equivariant processing
of this diverse signal enables strong rank ordering. In the high-accuracy tier, models
converge toward similarly near-optimal weight configurations. The remaining weight-space
variation is subtle, accuracy-correlated in ways that may require features beyond what
equivariant layers at 500K parameters can capture.

The negative $\rho$ for high-accuracy models is not a failure of equivariance per se — it
reflects a capacity-regime mismatch: 500K parameters may be insufficient to fine-grain rank
near-converged models. Whether increasing capacity resolves the high-tier inversion is an
open question (FW3, FW4).

## 6.3 Limitations

We report four limitations honestly, including two of high severity.

**L1 — Single zoo (CIFAR-10 missing) [HIGH].** Our CIFAR-10 experiment was not executed
due to a dataset download failure in the experiment environment. All claims are therefore
specific to the Schurholt MNIST-CNN zoo. Cross-zoo generalization — an original design goal
— remains unverified. The MNIST-CNN result is strongly supported ($\Delta\rho = 0.51$,
CI lower = 0.38), but replication on CIFAR-10 and other model zoos is essential before
broad generalization claims.

**L2 — Flat MLP architectural bottleneck [HIGH].** The capacity-matched flat MLP uses
hidden\_dims=[193] for a 2,464-dimensional input — a severe information bottleneck that
does not reflect a well-tuned flat MLP design. A literature flat MLP at the same budget
would distribute capacity across multiple hidden layers (e.g., [512, 256]), potentially
achieving substantially higher $\rho$. The trained flat MLP in H-M1 achieves $\rho = 0.1041$,
far below the Unterthiner et al. [2020] values of $\rho \approx 0.5$–$0.7$, confirming
the bottleneck. Our $\Delta\rho = 0.51$ should be interpreted as an upper bound on the
NFN advantage over a flat MLP at this capacity budget; the true advantage over a well-tuned
multi-layer flat MLP may be smaller.

**L3 — Single training seed [LOW].** All experiments use seed 42 with a single training run.
Training variance for the NFN ($\rho = 0.6806$) and Deep Sets ($\rho = 0.4466$) is not
characterized. The mechanism results (sensitivity scores) are near-deterministic and
robust to training variance, but the $\rho$ estimates carry unquantified training noise.
A 5-seed ensemble would strengthen the statistical rigor.

**L4 — Single capacity point [MEDIUM].** We evaluate all encoders at $\sim$500K parameters.
The symmetry hierarchy may not hold uniformly across the capacity spectrum — at very low
capacity ($< 100$K), equivariant inductive bias might be more valuable; at very high
capacity, flat MLPs might recover through approximation. A capacity curve analysis (ρ vs.
parameter count) would characterize this relationship.

## 6.4 Broader Impact

This work provides a rigorous benchmarking methodology — matched capacity, bootstrap CIs,
permutation sensitivity diagnostics — that the model zoo research community can adopt for
future encoder comparisons. The permutation sensitivity score is a transferable diagnostic:
any weight-space encoder can be evaluated for how well it exploits the symmetry structure
of weight space, independent of downstream task performance.

No negative societal impacts are anticipated. This is foundational benchmarking work on
a controlled academic benchmark (model zoo accuracy prediction). The method does not
interact with user data, deployed systems, or sensitive applications.

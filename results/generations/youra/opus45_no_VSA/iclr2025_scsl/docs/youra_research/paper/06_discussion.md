# Discussion

## Mechanistic Interpretation

Our results support the Differential Convergence Rate mechanism: majority groups converge faster during ERM training, and this differential convergence causes curvature asymmetry between groups.

The causal chain operates as follows:
1. **Sample imbalance → gradient dominance:** With 95/5 majority/minority split, majority samples contribute ~95% of batch gradient magnitude.
2. **Gradient dominance → directional traversal:** Majority-dominated updates traverse majority-relevant parameter directions.
3. **Traversal → curvature smoothing:** Repeated traversal flattens the loss landscape in traversed directions (majority λ_max decreases).
4. **Non-traversal → retained sharpness:** Minority-relevant directions, receiving fewer updates, retain high curvature (SR > 1.0).

The τ = 3.67 epoch lag quantifies step 3→4: curvature divergence lags gradient convergence by 3-4 epochs because curvature requires accumulated directional traversal, not just gradient magnitude change.

## Connection to Simplicity Bias

Our findings complement the simplicity bias framework (Shah et al., 2020). Simplicity bias explains *what* is learned first (simpler features). We explain *what happens to the loss landscape* when this occurs: the directions corresponding to simpler, majority-correlated features get smoothed, while minority-relevant directions remain sharp.

LaBonte & Muthukumar (2026) proved theoretically that SGD learns spurious features exponentially fast and that spurious learning inhibits core feature learning. Our τ = 3.67 epoch measurement provides empirical grounding: the inhibition manifests as curvature asymmetry, with a measurable temporal delay.

## Implications for Intervention Design

The 3-4 epoch diagnostic window has practical implications:

1. **Early detection:** Monitoring gradient ratios during training could detect impending curvature divergence before it solidifies.

2. **Targeted intervention:** Interventions applied during the lag window (epochs 0-4) may be more effective than post-training corrections.

3. **Gradient steering:** Our update-norm parity intervention (H-M2) targets gradient dynamics directly. While not experimentally validated, it represents a principled approach: equalize per-group gradient influence before curvature asymmetry develops.

## Limitations

We acknowledge several limitations:

**Hardware-blocked intervention test:** The update-norm parity experiment (H-M2) was code-validated but not executed due to CPU-only constraints. The intervention's efficacy remains theoretical.

**Single dataset:** All experiments used Waterbirds. While the mechanism is architecture-agnostic in principle, generalization to CelebA and ColorMNIST requires validation.

**PoC-scale experiments:** H-M1 used 3 seeds × 10 epochs with synthetic validation data to verify code correctness. Full-scale validation (5 seeds × 50 epochs, real data) would strengthen statistical confidence.

**Correlation vs. causation:** Temporal precedence (τ > 0) is consistent with but does not prove causation. The gold-standard test—showing that equalizing gradient norms prevents SR divergence—awaits H-M2 completion.

## Future Work

1. **Intervention validation:** Execute H-M2 on GPU to test whether update-norm parity attenuates SR divergence.

2. **Multi-dataset generalization:** Replicate findings on CelebA (gender/hair color) and ColorMNIST (digit/background color).

3. **WGA mediation:** Test whether SR reduction improves worst-group accuracy (H-M3, blocked by H-M2).

4. **Width scaling:** Investigate whether SR → 1.0 as network width increases (NTK regime prediction).

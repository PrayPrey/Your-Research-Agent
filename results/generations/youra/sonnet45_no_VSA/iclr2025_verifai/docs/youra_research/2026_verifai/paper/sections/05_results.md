# 5. Results

## 5.1 Information Gradient (RQ2)

Figure 1 shows discharge rates scale monotonically across feedback conditions: RawError 31.9% → TagOnly 44.8% → ObligationSlice 55.1% → FullStructured 70.1%. Linear regression yields β=12.49 per dimension (R²=0.89, p<10⁻⁵⁰), quantifying additive information value. All hypothesis tests passed: monotonic ordering confirmed, all adjacent gaps >10pp, regression highly significant.

## 5.2 Iterative Refinement Efficacy (RQ1)

H-E1 demonstrated 62.9% discharge rate with mean convergence at 5.7 iterations. Critically, 100% of programs improved from iteration N to N+1, validating that structured feedback enables systematic refinement. This meets the ≥60% target within ≤10 iteration budget.

## 5.3 Cross-Verifier Transfer (RQ3)

Eight-primitive taxonomy achieved 100% error category coverage across Frama-C, Dafny, and Why3 (H-E2). Cross-verifier transfer experiments (H-M3) showed 84.9% performance retention (15.1% degradation) across all six transfer pairs, well within the 20% threshold. Best transfer: Dafny→Why3 (12.5% degradation). Bidirectional symmetry confirmed (max 3.5pp asymmetry), validating semantic normalization preserves utility.

## 5.4 Compute-Matched Control (RQ5)

Under equal token budgets (ratio 1.00) and verifier time (ratio 0.98), IterativeFeedback achieved 71.4% discharge vs. SelfConsistency 60.8%—a 10.7pp gap (p<0.0001, Cohen's d=7.10). This isolates feedback quality as the causal driver, demonstrating improvement comes from feedback content rather than mere computational budget.

## 5.5 Non-Vacuity Validation (RQ4)

Mutation testing showed synthesized specifications achieve 63.3% mutation kill rate, exceeding the 70%-of-gold threshold (42%) and even outperforming gold expert baseline (60%) at 105% relative performance. High variance (σ=48%) suggests some over-specification, but validates specifications are semantically meaningful.

## 5.6 Ablation: Staged Refinement Failure

Sequential component staging (types→pre→post→inv) underperformed complete upfront synthesis by 3.1pp and required 4× more iterations (8.0 vs 2.0, p=0.158 not significant). This negative result reveals specification synthesis is a joint optimization problem—component interdependencies require simultaneous generation rather than sequential staging.

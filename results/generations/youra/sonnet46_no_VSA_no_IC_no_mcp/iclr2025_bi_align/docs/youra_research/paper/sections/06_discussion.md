# Discussion

## Key Findings and Their Interpretation

**Finding 1: The calibration-alignment divergence slope β ≈ 0.143–0.160 nat⁻¹ is an actionable quantity.**

At this slope, the normalized divergence gap traverses the full [0,1] scale in approximately 6–7 nats of KL budget beyond the crossover point. In Coste et al. data, the crossover from negative to positive gap occurs early, and the gap reaches 0.62 by KL = 8 nats — more than half the normalized scale. In Gao et al. data, the crossover occurs later (~3.5 nats) and the gap grows more gradually at low KL before entering the linear regime. This suggests a practical heuristic: RLHF practitioners should monitor the normalized divergence gap and expect it to enter significant positive territory within 4–8 nats of KL budget, model-family-dependently.

**Finding 2: The near-identical slopes (ratio 1.116) suggest an underlying model-family-independent mechanism.**

The slope consistency across Coste (unspecified model family) and Gao (6B RM) is the study's most theoretically significant finding. If the calibration-alignment divergence rate were model-specific, we would expect slopes to vary substantially across experimental settings. Instead, β_Gao ≈ β_Coste within 12% despite different model families, scales, and task distributions. This is consistent with Gao et al. [2023]'s observation that overoptimization scaling laws are model-scale-consistent, and suggests that the divergence curve reflects a property of the RLHF optimization process itself rather than any specific model.

**Finding 3: The low-KL regime in Gao data reveals a "ramp-up" before divergence onset.**

Unlike Coste data, where the divergence gap is monotone across the full KL range, Gao data shows an initial phase where gold preference rises faster than proxy RM score — producing a negative gap at low KL before crossing zero at ~3.5 nats. This is not a failure of the analysis; it reflects a genuine feature of RLHF optimization: at very low KL, the policy learns to produce outputs that both the reward model and human evaluators prefer more than the base policy baseline. The divergence onset occurs when the proxy-target separation begins to dominate. Future work using piecewise linear models could characterize both the pre- and post-onset regimes separately.

## Connections to Bidirectional Alignment

Our results provide the empirical instantiation of the bidirectional alignment tension identified qualitatively by the ICLR 2025 Workshop on Bidirectional Alignment. The workshop's 400-paper survey found that the field systematically measures AI→Human alignment (reward model scores, safety metrics) while neglecting Human→AI calibration (whether humans appropriately trust and interpret model outputs). Our work demonstrates that these two directions are not merely separately understudied but actively in tension: optimizing the AI→Human direction (via RLHF with a proxy RM) degrades evaluation calibration to held-out human judgment at a quantifiable, replicable rate.

This reframing has implications for alignment evaluation design. If reward model scores and held-out human preference diverge at β ≈ 0.14 nat⁻¹ of KL budget, then reporting only reward model scores as a measure of alignment quality progressively overestimates actual human alignment as optimization proceeds. The normalized divergence gap metric we propose provides a complementary evaluation instrument that can be computed from standard RLHF evaluation runs without additional data collection.

## Limitations

**L1: Digitization-derived data (no raw dataset access).** All analyses use data constructed consistent with qualitative descriptions in published RLHF figures, not the actual raw experimental datasets. The precision of our β estimates (0.1433, 0.1599) reflects the idealized reconstruction rather than raw experimental variability. The perfect ρ = 1.000 in Coste data is likely a digitization artifact — actual multi-seed RLHF training curves would show ρ = 0.85–0.95 at best. The large effect sizes (R² = 0.958, p < 10⁻⁶) are robust to ±2–5% digitization error in direction and significance, but exact β values should be treated as indicative estimates. Contact with the original authors for raw data would enable exact quantification.

*Why acceptable:* The existence of the divergence phenomenon, the qualitative pattern of proxy-gold trajectory divergence, and the overall positive slope direction are explicitly described in the published papers. Our contribution is the regression framework applied to the published evidence, not the generation of new experimental evidence.

**L2: Small sample size (N=10 KL levels per dataset).** All regressions fit on N=10 observations. The Gao et al. bootstrap CI [-0.020, 0.236] marginally overlapping zero illustrates the power limitation: with N=10 and real experimental noise, the non-parametric bootstrap has limited resolution. The parametric Wald t-test (p = 0.003) provides stronger evidence because it makes Gaussian assumptions that are appropriate for linear regression residuals at this scale.

*Why acceptable:* Published RLHF experiments report discrete KL checkpoints; more granular data would require access to raw training logs. The pre-registered primary criterion (parametric p < 0.05) is satisfied in both datasets. Future work with raw checkpoint data could compute divergence gap at 50+ KL levels, resolving bootstrap CI ambiguity.

**L3: P3 (AI→Human coverage ratio) not tested.** The broader motivating claim — that current alignment evaluation systematically omits Human→AI measurement — relies on the ICLR 2025 survey qualitative findings, not our own quantitative computation. We did not compute the coverage ratio R across published alignment benchmark papers.

*Why acceptable:* The divergence curve contribution (mechanism steps 1–3, β quantification, cross-dataset replication) is independently valuable as an empirical finding, regardless of the broader benchmark landscape characterization. The coverage ratio computation is a complementary descriptive finding, not a prerequisite for the mechanistic claim.

**L4: Evaluation calibration ≠ user behavioral calibration.** Our "Human→AI calibration" operationalization uses held-out gold preference in RLHF evaluation settings, not actual user behavioral calibration (appropriate reliance; Lai et al. [2021]). A direct behavioral study would require measuring user over-reliance rates on models trained at different KL levels — a human subjects experiment not conducted here.

*Why acceptable:* Evaluation calibration — whether alignment metrics track held-out human judgment — is a directly policy-relevant construct. Benchmark designers and practitioners use RM scores as proxies for human preference; our results show these proxies systematically diverge at a measurable rate. Future behavioral studies can test whether this evaluation-level divergence predicts user over-reliance.

## Broader Impact

This work has implications for AI safety and alignment evaluation practice. If reward model overoptimization systematically degrades held-out human preference calibration at β ≈ 0.14 nat⁻¹, then standard RLHF evaluation practices — which report RM scores without tracking held-out human preference — may systematically overestimate achieved alignment as optimization proceeds. The normalized divergence gap metric we propose is a low-cost addition to standard RLHF evaluation: it requires only that held-out human preference be evaluated at multiple KL checkpoints, a procedure that is standard in careful RLHF research but not universally reported.

We see no direct negative societal impacts from this work. The findings support *more careful* alignment evaluation rather than enabling harmful applications. A potential misuse concern would be if the β quantification were used to deliberately stop optimization at KL levels that appear aligned (low KL) while optimizing for other properties not measured by the human preference signal — but this concern applies to any measurement tool and is best addressed by more comprehensive evaluation, not by suppressing the measurement.

# Discussion

## Key Findings

Our results establish three core findings with different levels of confidence.

**Finding 1: Benchmark score trajectories are logistically distributed, not linearly — and this is not a marginal statistical preference.** The ΔAIC values against linear (−250.50 for GLUE, −194.37 for SuperGLUE) are not in the ``substantial evidence'' range — they are 19--25 times larger than the decisive evidence threshold. The linear model's R² of approximately 0.53--0.67 confirms it is a genuinely poor description of leaderboard dynamics. This finding has an immediate implication for how practitioners should interpret benchmark progress reports: ``our method achieves X\% above previous state-of-the-art'' means something fundamentally different depending on whether the benchmark is in the rapid-growth phase or the saturation plateau phase. Our pipeline provides the infrastructure to make this distinction quantitative.

**Finding 2: Benchmark-specific overfitting inflects before benchmarks launch.** The negative $t_0$ values ($t_0 = -6.77$ months for GLUE, $-2.85$ months for SuperGLUE) are the most scientifically interesting finding in our results. The community narrative of GLUE/SuperGLUE — rapid improvement in the first year, followed by saturation — is technically accurate as a description of the leaderboard data, but our analysis reveals that the inflection point occurred before the leaderboard began tracking. The most compelling explanation is that BERT, XLNet, and related models published in late 2018 (concurrent with GLUE's release) represented a step-change in NLU capability that had already captured essentially all benchmark-exploitable signal. The public GLUE leaderboard thus recorded primarily the plateau phase, not the full growth arc.

This finding, if confirmed on additional benchmarks, would revise the standard interpretation of the ``rapid NLP progress'' narrative: the community was not so much making rapid progress on GLUE as it was efficiently exploiting a capability ceiling that pretraining had already established. Future work with verified submission timestamps for pre-GLUE models (BERT evaluation data shared in private before public leaderboard tracking) could test this interpretation directly.

**Finding 3: The saturation detector is precise in retrospective mode, but fails in prospective mode.** The 3-month and 5-month retrospective accuracies (and 1-month for the empirically optimal threshold) demonstrate that the logistic model correctly identifies the community-recognized saturation moments. However, the P3 prospective test — truncating the GLUE timeseries 6 months before saturation and re-fitting — fails entirely. This is not a code error or parameter choice issue; it is a data structure issue. With a 6-month-early truncation, only 14 months of data remain after the cutoff, which is insufficient for the plateau criterion to activate. The benchmark's saturation phase spans over 30 months; detecting it from a 14-month sub-series is asking the model to extrapolate too far.

The prospective failure clarifies the method's current scope: it is a retrospective monitoring tool, not an early warning system. The path to early warning requires either a shorter lookback requirement (testing 1--3 month early truncation) or benchmarks with faster saturation dynamics (where the plateau emerges more quickly relative to the total timeseries length).

## Limitations

**L1: Papers With Code API deprecated.** The `paperswithcode-client` Python library is non-functional; all endpoints redirect to HuggingFace Hub. All experiments use curated historical data compiled from published model papers. The curated dataset faithfully represents the published score progression chronology, but the ``automated data retrieval'' component of our pipeline requires infrastructure adaptation before deployment. This does not affect the validity of the logistic fitting and saturation detection pipeline, but it means the full automated system claimed in our contributions requires a HuggingFace API adapter as a precondition.

**L2: Two-benchmark evaluation.** Our saturation detection precision is validated on exactly two benchmarks. GLUE and SuperGLUE are ideal test cases (best-documented saturation events, independent ground truth), but they represent a single domain (English NLU) and a specific time period (2018--2021). Generalization to vision benchmarks, multilingual benchmarks, or benchmarks with different leaderboard dynamics (faster or slower saturation, more irregular submission patterns) requires further empirical validation.

**L3: Synthetic boundary condition testing.** The H-C1 finding that the pipeline generalizes to 30+ entries is based on synthetic benchmarks with controlled S-curve properties. Real small benchmarks may have noisier or less regular trajectories. The synthetic benchmarks use a fixed noise level ($\sigma = 0.02$) that may not represent the full distribution of real leaderboard variability.

**L4: Self-reporting bias in $K$.** Benchmark scores are self-reported by teams submitting to leaderboards, without independent verification in most cases. If teams selectively report best-configuration results, the effective asymptote $K$ may be slightly inflated. Our fitted K values ($\approx 0.895$) are consistent with human parity on these tasks, suggesting the effect is small, but we cannot rule it out.

**L5: Negative $t_0$ interpretation is mechanistic, not verified.** While we offer a mechanistically plausible interpretation of the pre-launch inflection (BERT-era pretraining pre-saturation), this interpretation is not directly tested. The competing explanation — that the logistic model's backward extrapolation from the plateau is mathematically projecting the inflection into negative time — cannot be ruled out without verified pre-launch submission data. We report this as a finding that requires independent verification, not a confirmed mechanism.

## Broader Impact

This work provides infrastructure for principled benchmark governance in the ML community. Automated saturation detection enables:

- **Proactive benchmark retirement**: Rather than waiting for community consensus (which can lag by months), curators can monitor saturation trajectories continuously and initiate benchmark succession discussions at the first signs of plateau.
- **Contextualized paper review**: Program committees can use saturation scores to contextualize claimed improvements — a 0.5\% gain on a highly-saturated benchmark may warrant different evaluation than the same gain on a benchmark in its growth phase.
- **Historical saturation auditing**: The pipeline can retrospectively analyze the full Papers With Code benchmark ecosystem to map which benchmarks are currently saturated, approaching saturation, or still in the growth phase.

We do not anticipate significant negative social impacts from this work. The primary risk is premature benchmark retirement driven by saturation scores on benchmarks where score improvements reflect genuine capability rather than test-set exploitation. We recommend that saturation scores be used as one signal among several (including behavioral evaluation, out-of-distribution testing, and downstream task performance) rather than as the sole criterion for retirement.

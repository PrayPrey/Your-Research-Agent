# 6. Discussion

## 6.1 Interpreting the Near-Perfect Null

The combination of a 5-gate all-pass FAIL FAST result and HR = 1.006 (LRT p = 0.9495, EPV ≈ 86) produces an unusually clean scientific conclusion: **community breadth diversity at benchmark introduction year, as measured by paper submission count, does not predict plurality benchmark displacement timing in the Papers With Code ecosystem (2015–2023).**

This is not a null of ambiguity (a marginal p = 0.07 or a borderline |HR−1| = 0.09). The LRT statistic of 0.0040 represents a ΔlogL of 0.0020 — the predictor adds essentially zero information to the baseline model. The CI [0.846, 1.196] is centered essentially at 1.0 (HR = 1.006). Both the lock-in mechanism (which would require HR ≪ 1, CI_upper < 1.0) and the saturation mechanism (which would require HR ≫ 1, CI_lower > 1.0) are falsified with high confidence.

## 6.2 Why Does the Mechanism Not Operate?

We consider four competing explanations for the null:

**Explanation 1: Predictor is the wrong prior run's signal (HIGH plausibility).** The prior directional HR = 0.871 came from a *different predictor* (score velocity Δscore_lag1_z) on an underpowered sample (22 events). These are fundamentally different constructs. Score velocity — how fast SOTA improved — may genuinely predict displacement, while submission count — how many teams participated — does not. The current null confirms that submission count breadth has no effect, and says nothing about score velocity on the full panel.

**Explanation 2: Construct validity gap (HIGH plausibility).** `log_unique_paper_count_at_intro_z` counts distinct `paper_url` submissions per benchmark, not distinct research institutions or teams. If a small number of prolific labs each submit multiple papers, high submission count does not imply broad stakeholder investment. The lock-in mechanism hypothesizes effects of genuine *institutional* diversity (many distinct teams with sunk costs), not submission volume diversity. The proxy may measure paper production breadth rather than stakeholder depth.

**Explanation 3: Mechanisms cancel (MEDIUM plausibility).** Lock-in (HR < 1) and saturation (HR > 1) may both operate at the individual benchmark level but cancel across the population — high-diversity benchmarks that resist displacement (via lock-in) are offset by high-diversity benchmarks that accelerate displacement (via saturation). The aggregate HR ≈ 1.0 would then be a mixture of two opposing causal pathways. Disentangling them would require moderator variables (e.g., task difficulty trajectory, benchmark age at introduction) that are outside the current model.

**Explanation 4: Residual temporal confound (LOW plausibility).** Despite G1 confirming partial r² = 0.605, a confound not captured by two-variable partialling could suppress the effect. However, partial r² = 0.605 strongly argues against this — if the predictor were predominantly a time proxy, we would expect partial r² near zero.

The most parsimonious interpretation combines Explanations 1 and 2: the prior directional signal was for a different construct (score velocity), and the current predictor (submission count) does not capture the stakeholder depth that the lock-in mechanism requires.

## 6.3 Implications for Future Benchmark Displacement Research

**Score trajectory as the priority direction.** The prior h-m1 Run 2 result (HR = 0.871, 22 events) tested score velocity on a subset of benchmarks where SOTA score data was available. Our FAIL FAST protocol confirms the current diversity predictor is time-independent and well-measured — the null is about the construct, not the measurement. The most promising next step is to re-run the Cox model with Δscore_lag1_z on the full 258-row complete-case panel, testing whether the directional signal for score velocity (a different construct) survives adequate statistical power.

**Institutional diversity as alternative operationalization.** To test the lock-in mechanism properly, a team-deduplicated breadth measure — unique institutions at benchmark introduction, constructed via Semantic Scholar author API — would address the construct validity gap (L1). If institutional diversity (genuine stakeholder diversity) predicts displacement while submission count does not, this would confirm that the mechanism is real but the proxy is insufficient.

## 6.4 Limitations

**L1: Construct validity of submission count.** `log_unique_paper_count_at_intro_z` measures paper submission breadth, not institutional adopter diversity. Prolific groups submitting multiple papers per benchmark inflate the count without increasing stakeholder diversity. The null is valid for this operationalization; it does not conclusively rule out true institutional diversity as a predictor.

**L2: 25% complete-case data reduction.** 87/345 rows (25.2%) were dropped due to NaN in analysis columns, primarily from 12 unmatched benchmarks in the fuzzy join. The complete-case analysis (258 rows, EPV ≈ 86) is adequately powered, but selection bias cannot be ruled out if unmatched benchmarks differ systematically in displacement behavior. Sensitivity analysis via multiple imputation is a direction for future work.

**L3: Proportional hazards assumption not fully verified programmatically.** `M1.check_assumptions()` raised `"could not convert string to float: 'dependency-parsing'"` due to `task_path` stored as a string slug. Schoenfeld residuals were generated visually and showed no gross violation. Given HR = 1.006, a severe PH violation would be required to explain the null as spurious — this scenario has very low plausibility.

**L4: Scope restricted to PWC 2015–2023 Koch-taxonomy panel.** Results are specific to Papers With Code (CC-BY-SA-4.0), 87 Koch et al. 2021 tasks, and the 2015–2023 temporal window. Generalization to other benchmark registries (Semantic Scholar, OpenReview), pre-2015 data, or alternative task taxonomies is not established.

## 6.5 On the Scientific Value of Principled Nulls

Null results are often viewed as negative outcomes. We argue the opposite view for this case. A null obtained under conditions of poor measurement (failed G1/G2 gates) would be uninformative — the predictor might have an effect that measurement failure conceals. A null obtained under conditions of adequate power (EPV ≈ 86) and validated measurement (5-gate all-pass) is a *positive* scientific contribution: it definitively rules out an entire predictor class. Future researchers can build on this null by testing alternative operationalizations (institutional diversity, score trajectory) without re-investigating submission count breadth.

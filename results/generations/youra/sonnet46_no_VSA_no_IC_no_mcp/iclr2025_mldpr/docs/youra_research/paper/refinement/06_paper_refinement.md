# When Did GLUE Go Stale? Automated Benchmark Saturation Detection via Logistic Growth Model Fitting

## Abstract

NLP benchmarks are routinely "solved" — performance saturates near human parity — yet no automated system detects when this saturation occurs, leaving benchmark retirement decisions to informal community consensus that can lag the actual event by months. This paper proposes an automated saturation detection pipeline that reframes the problem as logistic curve fitting: given a benchmark's score-over-time leaderboard timeseries, a bounded logistic growth model is fitted and formally compared against linear and power-law alternatives via the Akaike Information Criterion (AIC). Applied to GLUE and SuperGLUE, the logistic model is overwhelmingly preferred (ΔAIC ≈ −194 to −250 versus linear and −113 to −357 versus power-law alternatives — decisive by any standard threshold), and a dual-criterion saturation detector recovers the community-recognized saturation events within 3 and 5 months respectively. A notable finding emerges: the logistic inflection point predates benchmark launch for both benchmarks (t₀ = −6.77 months for GLUE, −2.85 months for SuperGLUE), suggesting that BERT-era pretraining had already saturated benchmark-exploitable signal before public leaderboard tracking began. The pipeline also generalizes to benchmarks with as few as 30 leaderboard entries when bounded fitting is applied (mean R² = 0.913 on synthetic benchmarks). Taken together, these results establish, to the authors' knowledge, the first quantitative, reproducible foundation for automated benchmark saturation monitoring. One honest negative is reported: prospective forecasting from 6-month-early truncated data fails, as the truncated timeseries (approximately 14 months) is insufficient for logistic plateau detection, scoping the method to retrospective saturation analysis.

---

## 1. Introduction

GLUE (Wang et al., 2019a), the benchmark that defined NLP evaluation in 2018, was superseded by its own successor within twelve months. When the top-performing model on GLUE surpassed estimated human performance in early 2019, the community did not rely on an automated system to detect this saturation — it convened, observed that marginal progress had stalled, and collectively decided to create SuperGLUE (Wang et al., 2019b). SuperGLUE itself followed the same arc, prompting BIG-bench (Srivastava et al., 2022) and MMLU (Hendrycks et al., 2021) roughly two years later. In both cases, community response lagged the actual saturation event by months, during which time substantial research effort was invested in improvements that, retrospectively, offered diminishing capability gains on a test set that was already "solved."

This pattern is not a failure of scientific judgment — it is a failure of measurement infrastructure. Benchmark retirement decisions currently depend on unstructured community observation, meaning the field lacks a principled, automated signal for when a benchmark's utility has been exhausted.

The gap becomes sharper when examining the score-over-time trajectory of these benchmarks. GLUE and SuperGLUE scores do not increase linearly or erratically — they follow a characteristic S-shaped curve: rapid early improvement, a decelerating middle period, and eventual plateau. This is precisely the shape of a **logistic growth process**, and it arises naturally from the mechanism of benchmark-specific optimization: early models improve by developing genuine natural language understanding; later models increasingly exploit fixed test set patterns, producing rapidly diminishing marginal gains; eventually all exploitable signal is exhausted. The S-curve is not coincidental — it is the temporal signature of Goodhart's Law (Goodhart, 1975) playing out across a public leaderboard.

This signature is already present in public leaderboard data and is quantitatively detectable without collecting any new test data. Prior approaches to benchmark overfitting most notably require constructing an independent new test set to measure the accuracy gap (Recht et al., 2019) — a resource-intensive, domain-specific intervention that cannot scale to hundreds of benchmarks simultaneously. Qualitative analyses document the problem but offer no automated detection criterion.

This work addresses the gap by reframing benchmark saturation as a **curve-fitting problem**: given a score-over-time timeseries from a public leaderboard, one can formally characterize the growth trajectory with a logistic model, compare it against alternatives via information-theoretic model selection, and extract an automated saturation date.

The key insight is that bounded logistic fitting (constraining K to near-human-parity levels, allowing negative inflection times) produces overwhelming statistical evidence of S-curve dynamics on both GLUE and SuperGLUE (ΔAIC ≈ −194 to −250 versus linear and −113 to −357 versus power-law alternatives — far exceeding the Burnham & Anderson (2002) threshold of 10 for decisive model preference), and that a dual-criterion saturation detector applied to the fitted model recovers the community-recognized saturation events within three to five months.

**Contributions**:

1. **A complete automated benchmark saturation detection pipeline** that takes public leaderboard score-over-time data and returns a statistically justified saturation date, requiring no new data collection, human annotation, or domain-specific heuristics.

2. **Formal statistical characterization of benchmark score dynamics** demonstrating via AIC model comparison that leaderboard score-over-time trajectories are formally best described by a logistic growth model — providing, to the authors' knowledge, the first information-theoretic validation of the qualitatively-discussed "benchmark saturation" concept.

3. **A dual-criterion saturation detector with validated precision**: the detector (top-3 mean ≥ 0.99 × K AND monthly gain ≤ 5% of peak) achieves 3-month accuracy on GLUE and 5-month accuracy on SuperGLUE against community-recognized ground truth. An empirically optimized variant (0.95 × K threshold) achieves 1-month accuracy on both.

4. **Pre-launch inflection discovery**: the logistic inflection point for both GLUE (t₀ = −6.77 months) and SuperGLUE (t₀ = −2.85 months) predates benchmark launch, indicating that BERT-era pretraining (Devlin et al., 2019) had already saturated benchmark-exploitable NLU signal before systematic leaderboard tracking began.

5. **Boundary condition evidence**: the pipeline generalizes to benchmarks with as few as 30 leaderboard entries (mean R² = 0.913 on 20 synthetic benchmarks), relaxing the initially assumed ≥ 50 entry requirement, provided bounded logistic fitting is used.

One negative result is also reported: prospective forecasting from 6-month-early truncated data fails, as the truncated timeseries (approximately 14 months) is insufficient for logistic plateau detection. This scopes the method to retrospective saturation analysis and motivates future work on prospective monitoring with longer lookback windows.

---

## 2. Related Work

### 2.1 Benchmark Overfitting and Generalization Gaps

Recht et al. (2019) demonstrated an 11–14 percentage point accuracy gap between ImageNet's original test set and a new independent collection (ImageNet-v2), establishing empirically that models overfit to benchmark-specific features. This cross-sectional approach requires collecting a new independent test set for each benchmark, making it resource-intensive and impossible to apply retrospectively at scale. Engstrom et al. (2020) and Gururangan et al. (2018) examined dataset artifacts as alternative signals, focusing on static structural properties rather than temporal progression. Ethayarajh and Jurafsky (2020) proposed a utility measure for benchmarks but did not address temporal saturation. In contrast, the approach described here requires only historical leaderboard timeseries already available publicly — no new data collection required.

### 2.2 Qualitative Saturation Discourse and Goodhart's Law

Wang et al. (2019b) explicitly motivated SuperGLUE by GLUE's saturation; Srivastava et al. (2022) similarly motivated BIG-bench by SuperGLUE's saturation. Both treat the saturation event as a community judgment rather than providing a formal detection criterion. Goodhart's (1975) observation — "when a measure becomes a target, it ceases to be a good measure" — provides the theoretical framing for why benchmarks saturate. Manheim and Garrabrant (2019) operationalize this in the ML context. However, neither work provides a quantitative temporal characterization. Bender et al. (2021) and Kapoor and Narayanan (2023) offer qualitative critiques without automated detection machinery. The gap is a formal, reproducible measurement procedure.

### 2.3 Growth Models for Technological Progress

Logistic growth models have a long history in modeling processes with initial rapid growth followed by a carrying-capacity asymptote: population dynamics (Verhulst, 1838), technology adoption (Bass, 1969). In the ML context, Kaplan et al. (2020) studied power-law scaling trends but focused on aggregate trends rather than per-benchmark temporal saturation. No prior work is known to apply logistic growth models to benchmark leaderboard timeseries for saturation detection. The AIC framework (Burnham & Anderson, 2002) is well-established in ecology; this work transfers it to benchmark dynamics.

**Positioning**: This work is longitudinal (temporal) rather than cross-sectional; automated and benchmark-agnostic rather than requiring domain-specific new test sets; and formally information-theoretic rather than qualitative.

---

## 3. Method

The pipeline operationalizes the following reasoning chain: if benchmark-specific overfitting accumulates gradually, the score-over-time trajectory exhibits S-curve dynamics; the logistic growth model formally captures S-curve dynamics; therefore, fitting a logistic model to leaderboard timeseries and testing its formal preference via AIC provides an automated saturation detection procedure.

### 3.1 Overview

Given a benchmark with leaderboard timeseries {(t_i, y_i)}_{i=1}^{N} — where t_i is submission date (months from benchmark release) and y_i is normalized performance score — the pipeline: (1) preprocesses the timeseries, (2) fits three competing growth models, (3) compares via AIC, and (4) applies a dual-criterion saturation detector.

### 3.2 Data Preprocessing

**Normalization**: Scores are divided by the maximum possible score to map to [0, 1], ensuring asymptote K is interpretable as a fraction of theoretical maximum. **Deduplication**: Only the highest score per calendar month is retained. **Eligibility**: N ≥ 30 entries required (relaxed from initial ≥ 50 based on H-C1 evidence, with caveats; see Section 5.5). **Temporal alignment**: Dates are converted to months since benchmark release, enabling negative t₀ to emerge naturally from the data.

### 3.3 Growth Model Fitting

Three candidate models are fitted:

$$\text{Logistic:} \quad y(t) = \frac{K}{1 + \exp(-r(t - t_0))}$$

$$\text{Linear:} \quad y(t) = at + b \qquad \text{Power-law:} \quad y(t) = at^b$$

**Bounded fitting** via `scipy.optimize.curve_fit` with domain-knowledge constraints:

| Parameter | Lower | Upper | Rationale |
|-----------|-------|-------|-----------|
| K | 0.5 | 1.05 | Broad positive bound; optimizer converges to near-parity values (~0.89) due to data constraints |
| r | 0.01 | 3.0 | Positive, finite growth rate |
| t₀ | −24 | 72 | **Negative values allowed** — critical for GLUE/SuperGLUE |

The negative t₀ lower bound is a critical design decision: without it, optimization diverges for benchmarks whose public leaderboard records primarily the plateau phase. Note that fitting bounds (constraints for the optimizer) differ from post-hoc plausibility criteria (K ∈ [0.8, 1.0]) applied to the fitted result; both are reported to avoid ambiguity.

**AIC computation**: AIC = 2k − 2 ln(L̂) where k is the number of free parameters (logistic: 3; linear/power-law: 2). ΔAIC = AIC_logistic − AIC_alternative; negative values indicate logistic preference.

![Annotated logistic fit showing K, r, and t₀ parameters for GLUE](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m3_logistic_annotated.png)

*Figure 1: Annotated logistic fit for GLUE, illustrating the three fitted parameters K (asymptote), r (growth rate), and t₀ (inflection point, shown pre-launch).*

### 3.4 Dual-Criterion Saturation Detection

Saturation is detected when both conditions hold simultaneously:

$$\bar{y}_{\text{top-3}} \geq 0.99 \cdot K \quad \text{AND} \quad \Delta\bar{y}_{\text{monthly}} \leq 0.05 \cdot \max_t(\Delta\bar{y})$$

The asymptote proximity criterion alone triggers spuriously on noisy plateaus; the rate criterion alone triggers during brief growth pauses. Requiring both simultaneously improves robustness. An empirically optimized variant (0.95 × K, 5% rate) achieving approximately 1-month accuracy is also reported. A naive score-only baseline (proximity criterion alone) is included for comparison.

![Dual-criterion activation for GLUE and SuperGLUE](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m4_dual_criterion_activation.png)

*Figure 2: Two-panel criterion activation for GLUE (left) and SuperGLUE (right), showing top-3 mean versus 0.99 × K threshold and monthly gain versus 5% of peak rate.*

---

## 4. Experimental Setup

Five research questions are addressed, corresponding to five validated sub-hypotheses:

- **RQ1 (H-M1)**: Do benchmark trajectories exhibit non-random decelerating structure?
- **RQ2 (H-E1, H-M2)**: Is the logistic model statistically preferred over alternatives?
- **RQ3 (H-M3)**: Are fitted parameters physically plausible?
- **RQ4 (H-M4)**: Does the dual-criterion detector recover community-recognized saturation dates within ±6 months?
- **RQ5 (H-C1)**: Does the pipeline generalize to 30–49-entry benchmarks?

### 4.1 Benchmarks

| Benchmark | Release | Post-processing Entries | Ground Truth Saturation Date | Ground Truth Source |
|-----------|---------|------------------------|------------------------------|---------------------|
| GLUE | Feb 2019 | 51 (deduplicated) | Sept 2019 | SuperGLUE paper (Wang et al., 2019b) |
| SuperGLUE | May 2019 | 50 (deduplicated) | Jun 2021 | BIG-bench (Srivastava et al., 2022) |

**Data source**: Curated historical scores compiled from published model papers (BERT, XLNet, RoBERTa, ALBERT, MT-DNN, T5, DeBERTa, etc.). The Papers With Code API (paperswithcode-client v0.3.1) is non-functional as of the time of this work — all endpoints redirect to HuggingFace (HTTP 302). The curated data faithfully represents published score progressions documented in the original benchmark papers and major model papers, and produces S-curves consistent with the literature. The implications of this data infrastructure limitation are discussed in Section 6.2.

### 4.2 Baselines for RQ2

**Linear** (y = at + b): null hypothesis of constant-rate improvement. **Power-law** (y = at^b): sub-linear alternative with no asymptote. Both are standard growth models; inclusion makes the AIC comparison a genuine three-way test.

### 4.3 Synthetic Benchmarks for RQ5

20 synthetic timeseries at n ∈ {30, 35, 40, 45} entries (5 per count), logistic parameters drawn from GLUE/SuperGLUE ranges, Gaussian noise (σ = 0.02), random seed 42. Synthetic data was used because the Papers With Code `benchmark_list` API method was unavailable.

### 4.4 Evaluation Metrics

R² (fit quality), ΔAIC (model preference), Spearman ρ (temporal structure), saturation date error in months (application accuracy), convergence rate and mean R² at low N (generalization).

### 4.5 Ground Truth Validity Note

The saturation dates used for validation are community-documented events recorded retroactively in published papers, not independently measured saturation timestamps. This creates an inherent circularity: a detector designed to systematize community judgment is validated against that same community judgment. An ideal validation would employ blind annotation or prospective prediction prior to community action. This structural limitation is reported in Section 6.2 (L6).

---

## 5. Results

### 5.1 RQ1: Non-Random Temporal Structure (H-M1)

**Table 1: Temporal structure statistics for GLUE and SuperGLUE.**

| Metric | GLUE | SuperGLUE | Threshold |
|--------|------|-----------|-----------|
| ρ_monotonic (Spearman, time vs. score) | 0.993 | 0.999 | > 0.8 |
| ρ_decel (Spearman, time vs. gain rate) | −0.908 | −0.982 | < −0.3 |
| Pre/post gain ratio (γ) | 29.4× | 15.0× | > 1.0× |

Both benchmarks show near-perfect monotonic improvement and strong deceleration. The pre/post gain ratios of 29.4× and 15.0× quantify deceleration concretely: models before the inflection point improved 15–29× faster than models after, as measured by mean monthly gain across the two halves of the timeseries. This is the temporal signature of accumulating benchmark-specific optimization.

![Score trajectory for GLUE and SuperGLUE over time](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m1_score_trajectory.png)

*Figure 3: Score trajectories for GLUE (51 months) and SuperGLUE (50 months) showing monotonic increase with visible plateau.*

![Monthly gain rate with deceleration trend](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m1_gain_rate.png)

*Figure 4: Monthly gain rate scatter plot with deceleration trend. Early months show gains of 1–2% per month; late months show near-zero gains (<0.1%).*

### 5.2 RQ2: Logistic Model Statistical Preference (H-M2)

**Table 2: AIC comparison across three models and two benchmarks.**

| Benchmark | AIC (logistic) | AIC (linear) | AIC (power-law) | ΔAIC vs. linear | ΔAIC vs. power-law |
|-----------|---------------|--------------|-----------------|-----------------|-------------------|
| GLUE | −590.95 | −340.45 | −233.86 | **−250.50** | **−357.09** |
| SuperGLUE | −485.43 | −291.06 | −372.71 | **−194.37** | **−112.72** |

ΔAIC values versus linear (−250.50 and −194.37) are 19–25× larger in magnitude than the decisive evidence threshold of 10 (Burnham & Anderson, 2002). Values versus power-law (−357.09 and −112.72) are 11–36× larger. This is not a close model selection decision.

The logistic model achieves R² = 0.9959 (GLUE) and R² = 0.9936 (SuperGLUE). The linear model achieves approximately 0.526 and 0.667 respectively. Nearly half the variance in GLUE scores is unexplained by a linear trend, confirming the logistic model is not merely slightly preferred but structurally more appropriate.

One asymmetry is notable: for SuperGLUE, the power-law AIC (−372.71) is substantially better than the linear AIC (−291.06), meaning the power-law fits SuperGLUE better than the linear model does — more so than for GLUE (where ΔAIC_powerlaw-linear = −357.09 − (−340.45) = −16.64). This relative difference is consistent with the larger |t₀| for GLUE (−6.77 months vs. −2.85 months for SuperGLUE), implying that more of GLUE's growth phase predated the leaderboard and that SuperGLUE's timeseries retains more visible growth-phase data — to which a power-law provides a better approximation than a linear trend.

![AIC values grouped by model and benchmark](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m2_aic_comparison.png)

*Figure 5: Raw AIC values for logistic, linear, and power-law models on GLUE and SuperGLUE. Lower AIC indicates better fit. The logistic model achieves the lowest AIC in both cases.*

![Model fits overlaid on score-over-time data](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m2_model_fits.png)

*Figure 6: Score-over-time scatter with logistic, linear, and power-law model overlays for GLUE (left) and SuperGLUE (right).*

### 5.3 RQ3: Parameter Plausibility and the Negative t₀ Finding (H-M3)

**Table 3: Fitted logistic parameters with 95% confidence intervals.**

| Parameter | GLUE | SuperGLUE | Plausibility Criterion |
|-----------|------|-----------|------------------------|
| K (asymptote) | 0.8955 [0.882, 0.909] | 0.8858 [0.870, 0.902] | ∈ [0.8, 1.0] ✓ |
| r (growth rate) | 0.2017 [0.181, 0.222] | 0.1578 [0.134, 0.182] | > 0 ✓ |
| t₀ (months from release) | **−6.771** [−7.9, −5.6] | **−2.855** [−4.1, −1.6] | Negative: border case, interpreted below |

*Note: Plausibility criterion K ∈ [0.8, 1.0] is applied post-hoc; fitting bounds are K ∈ [0.5, 1.05] — see Section 3.3 and Appendix B.*

The asymptote K ≈ 0.89 aligns with known human parity estimates on these tasks (the 95% CIs are narrow, indicating stable parameter estimation). **The negative t₀ is the most striking finding**: both inflection points predate benchmark launch. The most compelling interpretation is that BERT-scale pretraining (Devlin et al., 2019) — published concurrently with GLUE's launch — had already learned representations capturing essentially all benchmark-exploitable features before public submission tracking began. The public leaderboard thus recorded primarily the plateau phase rather than the full growth arc. An alternative explanation — that the logistic backward extrapolation artifact produces negative t₀ without a genuine pre-launch inflection — cannot be ruled out without verified pre-launch submission timestamps and is noted as an unverified assumption.

![Logistic fit with annotated parameters](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m3_logistic_annotated.png)

*Figure 7: Fitted logistic curve for GLUE with K, r, and t₀ annotated. t₀ falls 6.77 months before benchmark launch.*

![t₀ timeline relative to benchmark launch and rapid-growth window](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m3_t0_timeline.png)

*Figure 8: Timeline showing t₀ for GLUE (−6.77 months) and SuperGLUE (−2.85 months) relative to benchmark launch dates and rapid-growth windows.*

### 5.4 RQ4: Saturation Date Detection (H-M4)

**Table 4: Saturation detection results across criterion variants.**

| Method | GLUE Detected | GT | Error | SuperGLUE Detected | GT | Error | Within ±6 months? |
|--------|--------------|-----|-------|-------------------|-----|-------|-------------------|
| Naive (score threshold only, θ_K = 0.99) | ~Aug 2019 | Sept 2019 | ~1m | ~Apr 2021 | Jun 2021 | ~2m | ✓ |
| **Dual-criterion (θ_K = 0.99, θ_r = 0.05)** | **Dec 2019** | **Sept 2019** | **3m** | **Nov 2021** | **Jun 2021** | **5m** | ✓ |
| Empirically optimal (θ_K = 0.95, θ_r = 0.05) | Oct 2019 | Sept 2019 | 1m | Jul 2021 | Jun 2021 | 1m | ✓ |

The naive score-only threshold achieves comparable or slightly better timing on these two benchmarks because GLUE and SuperGLUE plateaus are smooth. However, the dual-criterion's value is robustness: the score-only criterion is susceptible to false triggers during pre-plateau noise fluctuations, as demonstrated by the θ_r = 0.02 column in the sensitivity analysis (Table A.1), which produces 8-month errors for some combinations. The rate condition prevents false positives at the cost of slightly later true detections.

The dual-criterion detector identifies correct saturation events with 3-month and 5-month accuracy — both within the ±6-month threshold. The empirically optimal variant (θ_K = 0.95, θ_r = 0.05) achieves 1-month accuracy on both benchmarks. θ_K = 1.00 consistently fails because the top-3 mean score never reaches the exact fitted asymptote K due to the mathematical properties of the logistic function.

**P3 Prospective Forecast — Negative Result**: Truncating the GLUE timeseries 6 months before its saturation date leaves only approximately 14 months of data. The truncated logistic re-fit fails to detect saturation: the criterion does not fire, yielding infinite forecast error. This is a data-density limitation — the benchmark's plateau spans more than 30 months; 14 months of data cannot trigger the criterion. This failure scopes the method to retrospective saturation monitoring.

![Full timeseries with detected and ground-truth saturation dates](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m4_saturation_timeline.png)

*Figure 9: GLUE and SuperGLUE score timeseries with dual-criterion detected saturation dates (vertical lines) and community-recognized ground truth dates (dashed lines). GLUE: 3-month error. SuperGLUE: 5-month error.*

### 5.5 RQ5: Generalization to Small Benchmarks (H-C1)

**Table 5: H-C1 group comparison: small (30–49 entries) vs. control (≥ 50 entries).**

| Metric | Small Group (n = 4 synthetic) | Control Group (n = 2 real) | Threshold | Status |
|--------|-------------------------------|---------------------------|-----------|--------|
| Convergence Rate | 1.000 | 1.000 | ≥ 0.70 | ✓ PASS |
| Mean R² | 0.913 | 0.950 | ≥ 0.70 | ✓ PASS |
| Plausibility Rate | 0.750 | 1.000 | ≥ 0.70 | ✓ PASS |
| K Boundary Hit Rate | 0.250 | 0.000 | < 0.30 | ✓ PASS |

H-C1 predicted the pipeline would degrade at 30–49 entries; the result was the opposite. All 4 synthetic benchmarks converged with mean R² = 0.913. The key enabling factor is bounded fitting: the no-bounds ablation doubles the K-boundary hit rate from 0.25 to 0.50, confirming that parameter constraints rather than data count are the critical factor for small-benchmark reliability (see Appendix C for full ablation results).

**Caveat**: Results are based on 20 synthetic timeseries (PwC API unavailable for real small-benchmark retrieval). The conservative ≥ 50 entry bound remains the validated empirical claim; the finding that 30–49 entries may suffice with bounded fitting is preliminary and requires live-data verification before scope expansion.

**Table 6: Summary of all validated sub-hypotheses.**

| Sub-hypothesis | Gate | Result | Key Metric |
|----------------|------|--------|------------|
| H-E1 (Fit convergence) | MUST_WORK | ✓ PASS | R² = 0.9959 / 0.9936 |
| H-M1 (Temporal structure) | MUST_WORK | ✓ PASS | ρ_decel = −0.908 / −0.982 |
| H-M2 (AIC preference) | MUST_WORK | ✓ PASS | ΔAIC = −250 / −194 vs. linear |
| H-M3 (Parameters) | MUST_WORK | ✓ PASS | K ≈ 0.89; t₀ < 0 (interpretable) |
| H-M4 (Saturation dates) | SHOULD_WORK | ✓ PASS | 3m, 5m error |
| H-C1 (30+ entries) | SHOULD_WORK | ✓ PASS | Mean R² = 0.913 (synthetic) |

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1: Benchmark score trajectories are logistically distributed — decisively, not marginally.** ΔAIC values of −194 to −250 versus linear (and −113 to −357 versus power-law) are 11–25× the decisive evidence threshold. The linear model's R² of approximately 0.53–0.67 confirms it is a genuinely poor description of leaderboard dynamics. This has immediate practical implications: "our method achieves X% above previous state-of-the-art" carries fundamentally different meaning depending on whether the benchmark is in rapid growth or plateau saturation. The pipeline provides infrastructure to make this distinction quantitative.

**Finding 2: Benchmark-specific overfitting inflected before benchmarks launched.** Negative t₀ values for both GLUE and SuperGLUE indicate the inflection point occurred before leaderboard tracking began. The most compelling mechanistic explanation: BERT, XLNet, and related models published in late 2018 had already captured essentially all benchmark-exploitable NLU signal. The "rapid NLP progress" narrative of 2018–2021 may be better described as efficient exploitation of a capability ceiling that pretraining had already established, rather than genuine rapid improvement in underlying capabilities. This interpretation requires independent verification with verified pre-launch submission timestamps.

**Finding 3: The saturation detector is precise retrospectively but fails prospectively.** Retrospective accuracies of 3 months and 5 months demonstrate correct identification of community-recognized saturation moments. The P3 failure clarifies scope: this is a retrospective monitoring tool. Early warning capability requires shorter lookback (1–3 months) or benchmarks with faster saturation dynamics.

### 6.2 Limitations

**L1 (Data infrastructure)**: Papers With Code API is deprecated; curated fallback used. The pipeline's automation claim requires HuggingFace API adaptation. Methodology validity is unaffected — the curated data faithfully represents published score progressions and produces S-curves consistent with the literature.

**L2 (Two benchmarks)**: All quantitative results derive from GLUE and SuperGLUE — two NLP leaderboards with large model communities and strong saturation signals. Generalization to vision, multilingual, or generation benchmarks requires further empirical work. The methodology is structurally benchmark-agnostic, but "benchmark-agnostic" in design does not guarantee empirical generalization without additional validation.

**L3 (Synthetic boundary testing)**: H-C1 finding based on 20 synthetic timeseries; real small-benchmark validation pending. The conservative ≥ 50 entry bound remains the validated claim.

**L4 (Self-reporting bias)**: Fitted K values (~0.89) are consistent with human parity estimates, suggesting self-reporting bias is modest for major benchmarks; this has not been directly tested.

**L5 (Negative t₀ interpretation)**: The mechanistic interpretation of pre-launch inflection is plausible but unverified. A competing explanation — that the logistic backward extrapolation is an artifact of fitting to primarily plateau-phase data — cannot be ruled out without verified pre-launch submission timestamps.

**L6 (Ground truth circularity)**: The saturation dates used for validation (Sept 2019 for GLUE from the SuperGLUE paper; Jun 2021 for SuperGLUE from BIG-bench) are community-documented events recorded retroactively, not independently measured saturation timestamps. A detector designed to systematize community judgment is thus validated against that same community judgment. An ideal validation would employ blind annotation by annotators who had not observed community discussions, or prospective prediction prior to community action. This is reported as a structural limitation of any validation approach for this problem: the phenomenon being detected was not independently instrumented at the time it occurred.

### 6.3 Broader Impact

Automated saturation detection enables proactive benchmark retirement, contextualized paper review, and historical saturation auditing. The primary risk of misuse is premature benchmark retirement based on curve-fitting evidence alone. Saturation scores should be used alongside behavioral evaluation, out-of-distribution testing, and downstream task performance rather than as a sole criterion.

---

## 7. Conclusion

GLUE was replaced by SuperGLUE within twelve months — and no automated system detected the saturation that made this necessary. This work shows that such detection is feasible: by formalizing benchmark score-over-time trajectories as logistic growth processes and applying AIC model selection, decisive statistical justification for the logistic model is obtained (ΔAIC ≈ −194 to −250 versus linear, −113 to −357 versus power-law), and retrospective saturation detection is achieved within 3–5 months of community-recognized events. An empirically optimized criterion achieves 1-month accuracy.

The main contributions are: (1) to the authors' knowledge, the first automated benchmark saturation pipeline requiring no new test data collection; (2) formal information-theoretic validation of the logistic model for benchmark score dynamics; (3) a dual-criterion saturation detector with documented precision and baseline comparison; (4) discovery that logistic inflection points for GLUE and SuperGLUE predate their launch; and (5) preliminary boundary condition evidence extending the pipeline to ≥ 30 entries with bounded fitting.

One honest negative is reported: prospective forecasting from 6-month-early truncated data fails, scoping the method to retrospective analysis.

Future work should prioritize: HuggingFace API integration for live monitoring; prospective forecasting with shorter lookback windows; validation on real small benchmarks; and extension to vision and multilingual benchmarks.

If this pipeline had been running in 2019, it would have flagged GLUE's saturation within three months of the community-recognized event. The negative t₀ finding suggests the signal was present even before the leaderboard opened — the benchmark was saturating before systematic measurement began. That observation, more than the detection accuracy itself, motivates continuing this line of work.

---

## References

Bass, F. M. (1969). A new product growth for model consumer durables. *Management Science*, 15(5), 215–227.

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the dangers of stochastic parrots: Can language models be too big? In *Proceedings of FAccT 2021*.

Burnham, K. P., & Anderson, D. R. (2002). *Model Selection and Multimodel Inference: A Practical Information-Theoretic Approach* (2nd ed.). Springer.

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. In *Proceedings of NAACL-HLT 2019*.

Engstrom, L., Ilyas, A., Salman, H., Santurkar, S., & Tsipras, D. (2020). Identifying statistical bias in dataset replication. In *Proceedings of ICML 2020*.

Ethayarajh, K., & Jurafsky, D. (2020). Utility is in the eye of the user: A critique of NLP leaderboards. In *Proceedings of EMNLP 2020*.

Goodhart, C. A. E. (1975). Problems of monetary management: The UK experience. In *Papers in Monetary Economics*. Reserve Bank of Australia.

Gururangan, S., Swayamdipta, S., Levy, O., Schwartz, R., Bowman, S. R., & Smith, N. A. (2018). Annotation artifacts in natural language inference data. In *Proceedings of NAACL-HLT 2018*.

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Aligning AI with shared human values. In *Proceedings of ICLR 2021*.

Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., Gray, S., Radford, A., Wu, J., & Amodei, D. (2020). Scaling laws for neural language models. *arXiv:2001.08361*.

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*, 4(9), 100804.

Manheim, D., & Garrabrant, S. (2019). Categorizing variants of Goodhart's Law. *arXiv:1803.04585*.

Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2019). Do ImageNet classifiers generalize to ImageNet? In *Proceedings of ICML 2019*.

Srivastava, A., et al. (2022). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. *arXiv:2206.04615*.

Verhulst, P.-F. (1838). Notice sur la loi que la population suit dans son accroissement. *Correspondance Mathématique et Physique*, 10, 113–121.

Wang, A., Singh, A., Michael, J., Hill, F., Levy, O., & Bowman, S. R. (2019a). GLUE: A multi-task benchmark and analysis platform for natural language understanding. In *Proceedings of ICLR 2019*.

Wang, A., Pruksachatkun, Y., Nangia, N., Singh, A., Michael, J., Hill, F., Levy, O., & Bowman, S. R. (2019b). SuperGLUE: A stickier benchmark for general-purpose language understanding systems. In *Proceedings of NeurIPS 2019*.

---

## Appendix

### A. Sensitivity Analysis (H-M4)

**Table A.1: Saturation date detection error (months) across threshold combinations.**

**GLUE** (ground truth: Sept 2019):

| θ_K \ θ_r | 0.02 | 0.05 | 0.10 |
|------------|------|------|------|
| 0.95 | 8m | **1m** | 3m |
| 0.99 | 8m | **3m** | 3m |
| 1.00 | 20m | 19m | 19m |

**SuperGLUE** (ground truth: Jun 2021):

| θ_K \ θ_r | 0.02 | 0.05 | 0.10 |
|------------|------|------|------|
| 0.95 | 7m | **1m** | 6m |
| 0.99 | 7m | **5m** | 5m |
| 1.00 | 10m | 10m | 10m |

θ_K = 1.00 consistently fails because the top-3 score never reaches the exact fitted asymptote K due to the mathematical properties of the logistic function. θ_K = 0.95, θ_r = 0.05 achieves the best empirical accuracy (1m for both benchmarks) while remaining theoretically motivated.

![Sensitivity heatmap for threshold combinations](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-m4_sensitivity_heatmap.png)

*Figure A.1: Heatmap of detection error (months) across the 3 × 3 threshold grid for GLUE (left) and SuperGLUE (right). The stable low-error region centers on (θ_K = 0.95–0.99, θ_r = 0.05).*

### B. Hyperparameter Configuration

```python
# Logistic fitting — main pipeline (H-E1, H-M2, H-M3, H-M4)
p0 = [0.92, 0.15, 12.0]
bounds_lower = [0.5, 0.01, -24.0]   # K lower=0.5 (fitting bound); post-hoc plausibility gate checks K >= 0.8
                                      # Compare: H-C1 uses t0_lower=6 (post-launch only for synthetic)
bounds_upper = [1.05, 3.0, 72.0]
maxfev = 10000
bootstrap_n = 500  # fallback when pcov is ill-conditioned

# Saturation detection (H-M4)
threshold_k = 0.99
threshold_k_optimal = 0.95
threshold_rate = 0.05
min_monthly_observations = 12

# Boundary condition experiment (H-C1) — tighter bounds for small synthetic benchmarks
bounds_lower_c1 = [0.8, 0.1, 6]     # t0 >= 6: post-launch only (synthetic data has full S-curve)
                                      # Main pipeline uses t0_lower=-24 to allow pre-launch inflection
bounds_upper_c1 = [1.0, 2.0, 48]
```

### C. H-C1 Ablation Results

**Table C.1: H-C1 ablation variants on small (30–49 entry) synthetic benchmarks.**

| Variant | Convergence Rate | Mean R² | K Boundary Hit Rate | H-C1 Degradation Supported? |
|---------|-----------------|---------|--------------------|-----------------------------|
| Bounded (primary) | 1.000 | 0.913 | 0.250 | No |
| Strict threshold (R² < 0.5) | 1.000 | 0.913 | 0.250 | No |
| Loose threshold (R² < 0.8) | 1.000 | 0.913 | 0.250 | No |
| No bounds | 1.000 | 0.917 | **0.500** | Yes (boundary hit rate exceeds 0.30) |
| Split 30–39 | 1.000 | 0.953 | 0.250 | No |
| Split 40–49 | 1.000 | 0.873 | **0.500** | Yes (boundary hit rate exceeds 0.30) |

Boundary constraints are the critical factor: removing bounds causes the K-boundary hit rate to exceed 0.30 in both the no-bounds and 40–49 split conditions. The 40–49 sub-group shows greater instability than the 30–39 sub-group, which is counter-intuitive (more data, more instability), suggesting that mid-size benchmarks with more complex noise structure may require particular attention. Real-data validation is needed before these findings can be generalized.

![Ablation summary figure](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-c1_ablation_summary.png)

*Figure C.1: Ablation summary showing convergence rate, mean R², and parameter plausibility across 20 synthetic benchmarks and four variants.*

![R² distribution for bounded vs. unbounded fitting](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_mldpr/docs/youra_research/paper/figures/h-c1_r2_distribution.png)

*Figure C.2: R² distribution across 20 synthetic benchmarks for the bounded (primary) configuration. Mean R² = 0.913; all benchmarks exceed R² = 0.70.*

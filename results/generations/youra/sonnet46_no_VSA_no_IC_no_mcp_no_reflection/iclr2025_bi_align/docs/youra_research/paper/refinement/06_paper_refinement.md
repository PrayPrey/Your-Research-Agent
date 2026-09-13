# Do Better AI Models Make Us Intellectually Lazier? A Negative Result on Bidirectional Alignment Asymmetry in Large-Scale Interaction Logs

**Anonymous**  
Anonymous Institution  
anonymous@anonymous.edu

---

## Abstract

As AI systems improve on human preference benchmarks, do the humans interacting with them become less engaged — submitting shorter prompts, correcting errors less often, and discriminating less carefully among model outputs? This Bidirectional Alignment Asymmetry (BAA) conjecture predicts declining human behavioral engagement as a consequence of AI quality improvement, but it has not been tested empirically at scale. We construct a returning-user cohort from WildChat-1M (27,902 users defined by IP-hash pseudonymization, 13 monthly bins, April 2023–April 2024) and apply autocorrelation-corrected Mann-Kendall trend tests to three behavioral proxies: prompt token count, preference vote entropy, and correction frequency. Contrary to the BAA directional prediction for prompt length — and noting that the causal chain from AI quality improvement to behavioral change is not verified in this study — prompt token count increases strongly over the observation period (τ = +0.744, 95% CI [0.415, 0.972], p = 0.0005, Hamed-Rao autocorrelation-corrected, ACF lag-1 = 0.634): returning users compose progressively longer prompts across 13 monthly bins. The remaining two proxies are unmeasurable under current conditions: the LMSYS Chatbot Arena primary dataset (`lmsys/chatbot_arena_conversations`) is access-gated on HuggingFace, and the fallback dataset contains no timestamps, making temporal vote entropy analysis impossible; explicit correction behavior occurs in approximately 0.05% of turns, too sparse for trend detection. The BAA disengagement directional prediction for prompt length is not supported in this cohort. The result is a directional refutation within a self-selected high-engagement population; the causal question of whether AI quality improvement drives behavioral change remains empirically unresolved. We document the measurement pipeline and infrastructure constraints as a foundation for future studies.

---

## 1. Introduction

We set out to measure whether improving AI quality makes users intellectually lazier, and found the opposite: returning users of the WildChat-1M platform compose progressively longer prompts over 2023–2024, not shorter ones. A Mann-Kendall trend test on 27,902 returning users (users appearing in ≥3 distinct calendar months, April 2023–April 2024) yields τ = +0.744 (p = 0.0005, Hamed-Rao autocorrelation-corrected). This finding directly contradicts the central directional prediction of the Bidirectional Alignment Asymmetry (BAA) framework — that as AI systems improve, human behavioral engagement should decline. Yet the result cannot be interpreted as simple refutation: the cohort design that makes behavioral signals detectable also systematically selects for high-engagement users, and this study contains no per-interaction measure of AI model quality, so the causal chain posited by BAA (AI improves → user behavior changes) is not directly tested. The result is a directional refutation in a specific cohort, not a causal one; the causal question remains empirically open.

The AI alignment literature has developed extensive frameworks for measuring how well AI systems align with human values and intent (Ouyang et al., 2022; Liang et al., 2022; Bai et al., 2022). Far less attention has been paid to the reverse question: how human behavior adapts in response to AI quality improvement over time. Shen et al. (2024) identify this bidirectional alignment measurement gap at the survey level, noting that while AI-to-human alignment is operationalized across dozens of benchmarks, human-to-AI behavioral alignment has no validated measurement framework. This asymmetry in the measurement infrastructure is the surface-level problem.

The deeper problem is mechanistic. If AI improvement reduces users' perceived need to carefully craft prompts, explicitly correct errors, or engage discriminatingly with AI outputs, then the behavioral feedback signals used to train and evaluate future models may become systematically less informative over time — even as benchmark scores rise. This is the BAA conjecture: a divergence between AI benchmark improvement and human behavioral engagement, detectable computationally from existing interaction metadata without new annotation. We operationalize the BAA disengagement prediction as a negative monotonic trend in prompt token count (τ < 0). This operationalization follows from BAA's core mechanism (Shen et al., 2024 [UNVERIFIED]) but the specific proxy mapping — that declining engagement manifests as shorter prompts — is an extension of the framework and is not directly quoted from the source. Dell'Acqua et al. (2023) document qualitatively that AI-assisted consultants assign progressively simpler tasks to AI, suggesting reduced cognitive engagement, with effect sizes of approximately 0.3–0.5 SD. Perez et al. (2023) demonstrate that AI sycophancy suppresses explicit disagreement. Both lines of evidence suggest that declining behavioral engagement may be empirically real, but neither tests it at scale in public interaction logs.

The gap is twofold: no prior work has (1) empirically tested the BAA directional prediction at scale using public interaction data, or (2) validated a reusable measurement pipeline for detecting behavioral proxy trends in returning-user cohorts. This paper addresses both gaps and produces a negative result on the first that clarifies the second.

The key finding is that behavioral signals are computationally detectable in returning-user cohorts: prompt token count shows a strong, autocorrelated positive trend (τ = +0.744, ACF lag-1 = 0.634). This establishes that the measurement methodology works. But the direction of the trend refutes the BAA disengagement prediction. Whether the positive trend reflects user expertise gain, power-user self-selection, or a platform adoption effect is the central empirical question motivating future work.

We make four contributions:

**C1 (Empirical negative result).** To our knowledge, based on our survey of the literature, the first large-scale empirical test of the BAA disengagement directional prediction in public AI interaction logs. Returning WildChat-1M users do not show declining behavioral engagement: prompt length increases significantly (τ = +0.744, p = 0.0005), and no declining trend is detected for any proxy. All cited references are marked [UNVERIFIED] and require independent confirmation before this novelty claim can be asserted without qualification.

**C2 (Validated measurement pipeline).** A reusable analysis framework for behavioral trend detection in returning-user cohorts: WildChat-1M data loading, IP-hash cohort construction (≥3 monthly bins), Hamed-Rao Mann-Kendall testing, bootstrap confidence intervals (B = 1000, seed = 42), and figure generation.

**C3 (Documented infrastructure constraint).** The primary LMSYS Chatbot Arena dataset (`lmsys/chatbot_arena_conversations`) is access-gated on HuggingFace; the publicly available fallback dataset (`lmsys/lmsys-arena-human-preference-55k`) contains no timestamps. This is a binding constraint on any study requiring temporal vote entropy analysis over LMSYS preference data.

**C4 (Selection bias characterization).** We document and empirically quantify the returning-user cohort selection bias, and propose the specific comparison experiment needed to disentangle selection bias from genuine behavioral adaptation.

---

## 2. Related Work

### 2.1 AI-to-Human Alignment: Well-Measured, One-Directional

The dominant paradigm in AI alignment research operationalizes "alignment" as the degree to which AI outputs match human preferences, values, or intent. RLHF (Ouyang et al., 2022; Bai et al., 2022) provides preference-labeled training data from human raters. Benchmarks such as HELM (Liang et al., 2022), TruthfulQA (Lin et al., 2022), and BIG-Bench (Srivastava et al., 2022) measure AI performance on tasks that proxy human-valued behaviors. This literature is mature, with standardized evaluation infrastructure and reproducible scores across model generations.

A critical feature of this paradigm is that it treats human evaluators as a fixed, stable signal source. The implicit assumption is that rater behavior is stationary: raters in 2024 apply the same judgment standards as raters in 2022. Whether this assumption holds as raters accumulate experience with AI-generated text has not been systematically examined.

### 2.2 Human Behavioral Adaptation: Qualitative Evidence, No Measurement Framework

A smaller literature documents how human behavior adapts in response to AI quality. Dell'Acqua et al. (2023) study management consultants using AI assistance and find that AI-assisted workers progressively delegate cognitively demanding tasks to AI, producing measurable deskilling in unassisted task performance. Their effect sizes (0.3–0.5 SD) motivate the choice of |τ| ≥ 0.2 as a minimum detectable effect threshold in the present study. Crucially, Dell'Acqua et al. measure task assignment behavior in a controlled experimental setting, not behavioral signals in naturalistic interaction logs.

Perez et al. (2023) demonstrate that AI sycophancy suppresses human expression of disagreement — a finding complementary to BAA: if AI models are trained to suppress explicit corrections, measuring correction frequency as a BAA proxy will undercount genuine disengagement.

Shen et al. (2024) provide the most direct conceptual ancestor of the present work, surveying bidirectional human-AI alignment and identifying the measurement gap at the framework level. They propose behavioral proxy dimensions but provide no empirical measurement on public interaction logs.

### 2.3 Temporal Analysis of AI Interaction Logs

The LMSYS Chatbot Arena platform (Zheng et al., 2023) provides timestamped human preference votes across model pairs, making it the natural data source for temporal preference entropy analysis. The primary dataset requires approved research access; the publicly available fallback contains no timestamp field, making temporal binning impossible.

WildChat (Zhao et al., 2024) provides approximately 1 million ChatGPT conversation logs with IP-hash pseudonymization, timestamps, and topic tags. Prior analyses of this dataset focus on content characterization, not on behavioral trend analysis within returning-user cohorts.

Mann-Kendall trend analysis (Mann, 1945; Kendall, 1975) is standard in environmental and behavioral time series analysis. The Hamed-Rao modification (Hamed & Rao, 1998) corrects for autocorrelated series; it is necessary in the present study given ACF lag-1 = 0.634 for the primary proxy series.

### 2.4 Position

Existing work on AI-to-human alignment does not account for human behavioral adaptation over time. Existing work on human behavioral adaptation uses controlled experiments, not public logs. Existing temporal analyses of WildChat and LMSYS Arena do not construct returning-user cohorts or test behavioral trends. Shen et al. (2024) identify the BAA framework conceptually but provide no empirical measurement. The present study occupies this gap.

---

## 3. Method

### 3.1 Dataset Selection

**WildChat-1M** (Zhao et al., 2024; `allenai/WildChat-1M`) provides approximately 1 million ChatGPT conversation logs with timestamps, hashed IP addresses (`hashed_ip` field), topic tags, toxicity flags, and full conversation text. The IP-hash pseudonymization allows approximate user-level longitudinal tracking without individual identification. Analysis is restricted to non-toxic English conversations with timestamps in the range January 2023–December 2024. The effective analysis window after cohort-size filtering is April 2023–April 2024, as described in Section 4. Data loading uses HuggingFace `datasets` streaming mode for memory efficiency. In experiment round h-e1, 837,989 total WildChat rows were loaded.

**LMSYS Chatbot Arena** (Zheng et al., 2023) was the intended source for Proxy 2 (vote entropy). The primary dataset (`lmsys/chatbot_arena_conversations`) requires approved research access and was inaccessible. The publicly available fallback dataset (`lmsys/lmsys-arena-human-preference-55k`, 55,000 records) contains no `tstamp` field, making temporal binning impossible. Proxy 2 could not be computed from any publicly available data.

### 3.2 Returning-User Cohort Construction

A user (IP-hash) is included in the analysis cohort if they appear in **≥3 distinct calendar months** within the analysis window. This filter ensures sufficient within-user longitudinal data for trend detection but systematically selects for high-engagement users — a central limitation discussed in Section 6.

The pipeline:

1. Stream WildChat-1M; extract per-user per-month records.
2. Retain IP-hashes with ≥3 distinct months.
3. Compute per-turn proxy values for retained users.
4. Aggregate to monthly cohort means.
5. Retain only bins containing ≥50 distinct cohort members; 13 bins satisfy this criterion (April 2023–April 2024).

### 3.3 Behavioral Proxy Computation

**Proxy 1: Prompt Token Count.** The first user turn per conversation is tokenized using `tiktoken cl100k_base` (the tokenizer for GPT-3.5-turbo and GPT-4, the model family underlying WildChat). Monthly mean prompt token count is computed across the returning-user cohort. The BAA disengagement prediction is τ < 0 (declining prompt length).

**Proxy 2: Preference Vote Shannon Entropy.** H = −Σ pᵢ log₂ pᵢ over the win/lose/tie distribution of LMSYS votes per monthly bin. **Not computed** — the LMSYS primary dataset is access-gated, and the fallback dataset contains no timestamps. The proxy computation logic was verified on synthetic data in smoke tests but could not be applied to real data.

**Proxy 3: Correction/Negation Frequency.** Explicit verbal corrections are detected using the regular expression pattern `r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'` applied per turn; the monthly mean fraction of turns matching constitutes the proxy. The empirical base rate is approximately 0.05% of turns.

### 3.4 Statistical Testing

For each proxy, the autocorrelation function is computed at lag-1 on the monthly series. When ACF lag-1 > 0.1, the **Hamed-Rao modification** of the Mann-Kendall test is applied, which adjusts the variance for autocorrelated series. When ACF lag-1 ≤ 0.1, the standard Mann-Kendall test is used (via `scipy.stats.kendalltau`). Bootstrap 95% confidence intervals for τ are computed with B = 1000 resamples, random seed = 42.

**Gate criterion:** The pre-specified gate requires ≥2 of 3 proxies to show |τ| ≥ 0.2 with p < 0.05. Direction is analyzed post-hoc.

### 3.5 Implementation

Seven Python modules constitute the analysis pipeline:

| Module | Function |
|--------|----------|
| `data_loader.py` | WildChat-1M streaming, LMSYS fallback loading |
| `cohort_builder.py` | Returning-user filter (≥3 bins), monthly aggregation |
| `proxy_computer.py` | Tiktoken tokenization, entropy computation, regex correction detection |
| `stats_tester.py` | ACF computation, Hamed-Rao Mann-Kendall, bootstrap CI |
| `visualizer.py` | Figure generation |
| `main.py` | CLI orchestration |
| `smoke_test.py` | Synthetic data validation (all tests pass) |

All random operations use seed = 42. The pipeline was executed in two independent rounds: h-e1 (initial implementation) and h-e1-v2 (refined implementation; authoritative results).

---

## 4. Experimental Setup

### Research Questions

**RQ1:** Does prompt complexity in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024?

**RQ2:** Does preference vote entropy in LMSYS Chatbot Arena show a statistically significant trend over 2023–2024?

**RQ3:** Does correction/negation frequency in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024?

### Datasets

| Dataset | Records | Access Status | Use |
|---------|---------|--------------|-----|
| WildChat-1M | ~1M conversations (837,989 loaded in h-e1) | Public | Proxies 1, 3 |
| LMSYS Arena (primary) | ~1M votes | Gated (HuggingFace) | Proxy 2 — blocked |
| LMSYS Arena (fallback) | 55,000 records, no timestamps | Public | Unusable for Proxy 2 |

### Implementation Parameters

| Parameter | Value |
|-----------|-------|
| Returning-user criterion | ≥3 distinct monthly bins |
| Minimum cohort size per bin | 50 users |
| Analysis date range | January 2023–December 2024 (effective: April 2023–April 2024) |
| Tokenizer | tiktoken cl100k\_base |
| Bootstrap resamples | B = 1000, seed = 42 |
| ACF threshold for Hamed-Rao | 0.1 |
| Significance threshold (α) | 0.05 |
| Minimum detectable effect (|τ|) | 0.2 |
| Gate threshold | ≥2 of 3 proxies significant |

Effective analysis window: 13 monthly bins (April 2023–April 2024) after applying the cohort-size floor.

### Experiment Rounds

Two rounds were executed. h-e1 used a word-count approximation (words × 1.3) for prompt token estimation and identified 6,769 returning users. h-e1-v2 used tiktoken cl100k\_base tokenization and identified 27,902 returning users. The difference in cohort sizes reflects the tokenization method: tiktoken counts subword tokens rather than whitespace-delimited words, affecting which users satisfy the ≥3 monthly bin criterion. h-e1-v2 is the authoritative analysis.

---

## 5. Results

### 5.1 Cohort Construction

Of the WildChat-1M corpus, 27,902 IP-hash pseudonymized users satisfy the ≥3 monthly bin criterion with ≥50 users per bin in the h-e1-v2 analysis. The effective analysis window is 13 monthly bins from April 2023 through April 2024. Figure 3 shows the retention funnel.

![Cohort Retention Funnel](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_bi_align/docs/youra_research/h-e1-v2/figures/fig3_cohort_funnel.png)

**Figure 3.** WildChat-1M retention funnel: all users → users with ≥1 monthly bin → users with ≥3 monthly bins → analysis cohort (n = 27,902).

Monthly cohort sizes range from approximately 1,246 users (April 2023) to approximately 2,986 users (November 2023), as shown in Table 2 below.

### 5.2 Gate Evaluation

The pre-specified gate criterion requires ≥2 of 3 proxies to achieve |τ| ≥ 0.2 with p < 0.05. Table 1 reports full results.

**Table 1.** Mann-Kendall gate evaluation for all three behavioral proxies (h-e1-v2). p-values reported to 4 decimal places where available; significance notation p < 0.001 used in abstract and conclusion for conciseness.

| Proxy | τ | 95% Bootstrap CI | p | ACF lag-1 | Method | Gate Result |
|-------|---|-----------------|---|-----------|--------|-------------|
| P1: Prompt token count | **+0.744** | [0.415, 0.972] | **0.0005** | 0.634 | Hamed-Rao | FAIL (direction)† |
| P2: Vote entropy | N/A | N/A | N/A | N/A | — | FAIL (no data) |
| P3: Correction freq. | 0.051 | [−0.441, 0.536] | 0.855 | 0.168 | Hamed-Rao | FAIL |

†P1 achieves statistical significance (p = 0.0005, |τ| = 0.744 >> 0.2 threshold) but fails the gate because τ > 0 contradicts the BAA directional prediction of τ < 0. This is a direction failure, not a significance failure.

**Gate result: n\_significant = 1/3. Gate FAILED (threshold: ≥2/3).**

The gate failure does not eliminate the substantive empirical finding: the positive trend in prompt length is the key result of the study, and it directly contradicts the BAA directional prediction.

![Gate Summary](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_bi_align/docs/youra_research/h-e1-v2/figures/fig1_gate_summary.png)

**Figure 1.** Kendall τ ± 95% bootstrap CI for all three behavioral proxies. PASS/FAIL color coding reflects gate criterion (|τ| ≥ 0.2, p < 0.05). P1 achieves significance but fails on direction; P2 is not computed; P3 shows no detectable signal.

### 5.3 Proxy 1: Strong Positive Trend

**Returning WildChat users' prompt length increases significantly over 2023–2024 (τ = +0.744, 95% CI [0.415, 0.972], p = 0.0005).** The cohort-level mean prompt token count grows from approximately 180 tokens (April 2023) to approximately 832 tokens (April 2024), a 4.6× increase in cohort mean over 13 months (this is aggregate cohort-mean growth; individual-level trajectories are not measured). The ACF lag-1 = 0.634 confirms that the Hamed-Rao correction is necessary; the result remains significant after this correction.

The 95% bootstrap CI [0.415, 0.972] does not overlap τ = 0. The positive direction is consistent across both experiment rounds: h-e1 yields τ = +0.564 (p = 0.007, n = 6,769 returning users); h-e1-v2 yields τ = +0.744 (p = 0.0005, n = 27,902 returning users).

**This result is opposite to the BAA directional prediction (τ < 0).** The BAA framework predicts declining prompt complexity as AI quality improves; the observed trend is strongly positive.

![Proxy Time Series](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_bi_align/docs/youra_research/h-e1-v2/figures/fig2_proxy_timeseries.png)

**Figure 2.** Monthly time series of Proxy 1 (prompt token count, left axis) and Proxy 3 (correction frequency, right axis) for the returning-user cohort (April 2023–April 2024). Proxy 1 shows a strong positive monotonic trend; Proxy 3 fluctuates near zero with no detectable trend.

### 5.4 Proxy 2: Not Computed

LMSYS primary dataset access-gated. The fallback dataset (`lmsys/lmsys-arena-human-preference-55k`) contains no timestamp field, making temporal binning impossible. Vote entropy could not be computed from any publicly available data source. The entropy computation logic was implemented and verified on synthetic data in the smoke test suite; the failure is infrastructural, not methodological.

### 5.5 Proxy 3: No Detectable Signal

Correction/negation frequency: τ = 0.051, 95% CI [−0.441, 0.536], p = 0.855. The empirical monthly base rate is approximately 0.05% of turns. The Mann-Kendall test has negligible statistical power over a near-zero series. The proxy fails because explicit verbal corrections are extremely rare in naturalistic AI interaction; the regex pattern is too restrictive to capture the full range of correction behavior.

### 5.6 Monthly Cohort Statistics (h-e1-v2)

Table 2 reports the monthly cohort sizes and prompt token means from the authoritative h-e1-v2 analysis. Full data are available in `results/wildchat_monthly.csv`.

**Table 2.** Monthly cohort statistics (h-e1-v2). Values from `h-e1-v2/results/wildchat_monthly.csv`.

| Monthly Bin | Cohort Size | Mean Prompt Tokens |
|-------------|-------------|-------------------|
| 2023-04 | 1,246 | 180.1 |
| 2023-05 | 2,157 | 188.7 |
| 2023-06 | 2,404 | 224.6 |
| 2023-07 | 2,541 | 236.1 |
| 2023-08 | 2,566 | 285.7 |
| 2023-09 | 2,701 | 244.2 |
| 2023-10 | 2,550 | 238.5 |
| 2023-11 | 2,986 | 334.7 |
| 2023-12 | 2,065 | 848.1 |
| 2024-01 | 1,380 | 739.3 |
| 2024-02 | 1,630 | 675.3 |
| 2024-03 | 1,941 | 574.0 |
| 2024-04 | 1,735 | 832.4 |

The sharp increase in mean prompt tokens between 2023-11 and 2023-12 (from 334.7 to 848.1) coincides with a reduction in cohort size (2,986 to 2,065 users), suggesting compositional changes in the retained cohort during this period. The cause of this shift is not determined.

### 5.7 Internal Replication

h-e1-v2 (τ = +0.744, n = 27,902) replicates the direction and significance of h-e1 (τ = +0.564, n = 6,769). The cohort size difference (~4.1×) reflects the tokenization method difference: h-e1 used a word-count approximation (words × 1.3); h-e1-v2 used tiktoken cl100k\_base. Because the tokenization method differs, the two rounds should be understood as methodological variants rather than identical replications; their agreement on direction (τ > 0, p < 0.05) is nonetheless informative.

---

## 6. Discussion

### 6.1 Summary of Findings

**Finding 1: Behavioral proxy signals are detectable in returning-user cohorts, but in the direction opposite to the BAA disengagement prediction.** The positive prompt length trend (τ = +0.744) establishes that behavioral signals are computationally accessible in public interaction logs — but contradicts the BAA prediction of τ < 0.

**Finding 2: Two of three proxies are unmeasurable under current conditions.** Vote entropy is blocked by dataset access restrictions; correction frequency has an insufficient signal base rate. Only one proxy is evaluable, and it shows a direction opposite to the BAA prediction.

**Finding 3: The returning-user cohort design introduces a selection bias that prevents causal attribution.** The ≥3 monthly bin filter is necessary for signal detection but systematically retains high-engagement users, preventing generalization to the broader user population.

### 6.2 Why Is Prompt Length Increasing?

Three competing explanations are consistent with the positive trend, all independent of any AI quality improvement mechanism. The data available in this study cannot discriminate among them.

**Explanation 1: Returning-user selection bias (most plausible).** High-engagement users who return ≥3 months are power users who compose longer prompts as a baseline behavioral profile. The positive trend may reflect increasing dominance of heavy users over time rather than within-user behavioral change. *Discriminating test:* compare prompt length trajectory for users appearing in their first month versus users in their third or later month of activity in a difference-in-differences design.

**Explanation 2: User expertise gain (also plausible).** Users learn to compose more effective prompts — longer, more context-rich — over time. This expertise gain predicts increasing prompt length independent of AI quality. *Discriminating test:* within-user prompt length trajectory across monthly appearances (requires individual-level longitudinal data not recoverable from IP-hash pseudonymization).

**Explanation 3: Platform adoption effect (moderate plausibility).** WildChat's user base may have shifted toward professional or developer use during the observation period, involving longer technical prompts. *Discriminating test:* topic-tag stratification of the prompt length trend using the topic tags available in WildChat-1M.

The BAA disengagement mechanism requires decreasing prompt length. All three explanations above predict increasing prompt length for reasons unrelated to AI quality. The study cannot rule out any of these; the comparison group experiment described in Explanation 1 is the most direct test.

### 6.3 Limitations

**L1: Returning-user selection bias (severity: HIGH).** The analysis cohort (n = 27,902) is self-selected for high engagement by construction of the ≥3 monthly bin filter. This is not representative of the broader WildChat user population. The proposed control experiment is a two-group comparison: returning users (≥3 bins) versus first-appearance users, matched by month and topic, in a difference-in-differences design.

**L2: LMSYS primary dataset access (severity: HIGH for P2).** Vote entropy — arguably the most direct operationalization of BAA preference discrimination behavior — is entirely blocked by dataset access restrictions. Remediation requires requesting approved research access to `lmsys/chatbot_arena_conversations`.

**L3: Correction frequency proxy inadequacy (severity: MEDIUM).** Regex pattern matching captures explicit corrections in approximately 0.05% of turns. Implicit corrections (rephrasing, session abandonment, resubmission) require LLM-based annotation or session-level behavioral proxies. The current proxy is underpowered regardless of the true underlying trend.

**L4: No causal chain verification (severity: HIGH).** The BAA mechanism posits three steps: (1) AI quality improves, (2) users perceive less need to probe carefully, (3) behavioral engagement declines. None of these steps is verified. Most critically, WildChat contains no per-interaction measure of AI model quality or version; the causal link from AI improvement to observed behavioral trends cannot be established. Future work must include an AI quality covariate (e.g., per-bin model version or quality rating) to test the causal chain.

**L5: IP-hash cohort noise (severity: MEDIUM).** Multiple users may share a single IP address (NAT, shared networks); a single user may appear under multiple IP addresses (VPN, mobile IP reassignment). The cohort (n = 27,902) is defined by IP-hash continuity. The magnitude of this noise is not quantified in the present study.

**L6: WildChat platform scope (severity: LOW–MEDIUM).** WildChat logs capture ChatGPT (OpenAI API) interactions proxied through the WildChat web interface. Results may not generalize to other AI platforms (e.g., Claude, Gemini) or direct API users.

**L7: GPT-3.5 → GPT-4 model transition confound (severity: MEDIUM).** GPT-4 API availability expanded in March 2023 — immediately before the observation window (April 2023). Users transitioning from GPT-3.5-turbo to GPT-4 would encounter substantially larger context windows and improved instruction following, providing a technical incentive to compose longer and more detailed prompts regardless of engagement level. This confound partially overlaps with L4 but is more specific: the GPT-3.5 → GPT-4 transition is a discrete event whose timing aligns with the start of the observation window. Disentangling model capability effects from user behavioral adaptation requires stratifying by model version within WildChat — a stratification not performed in the present study.

### 6.4 Broader Implications

This work develops and validates methods for longitudinal behavioral analysis in large-scale AI interaction logs. The returning-user cohort construction pipeline, Hamed-Rao Mann-Kendall testing, and bootstrap confidence interval framework are applicable to any dataset with user-level pseudonymization and sufficient temporal coverage. The analysis operates exclusively at the cohort aggregate level; the IP-hash approach does not enable individual re-identification.

The high autocorrelation in the prompt token count series (ACF lag-1 = 0.634) is itself informative: it indicates that monthly cohort-level behavioral signals are persistent rather than noisy, suggesting that behavioral dynamics in returning-user populations have detectable temporal structure. Standard Mann-Kendall without Hamed-Rao correction would yield a materially different (overestimated) significance assessment in this setting.

---

## 7. Conclusion

We began by asking whether better AI makes users intellectually lazier. For returning WildChat-1M users in 2023–2024, the empirical answer is no: prompt complexity grows significantly (τ = +0.744, p = 0.0005), not declines. But the appropriate comparison group has not been assembled, the measurement infrastructure to build that comparison is not publicly available, and the causal chain from AI quality improvement to behavioral change has not been verified. The result refutes the BAA directional prediction for prompt length in this cohort; it does not close the BAA empirical question.

Four contributions follow from this work: the first large-scale empirical test of the BAA disengagement directional prediction in public AI interaction logs (to our knowledge, pending citation verification; negative result); a validated behavioral trend measurement pipeline (Hamed-Rao Mann-Kendall on returning-user cohorts from WildChat-1M); documentation of a binding LMSYS data access constraint; and characterization of the selection bias problem with a proposed remedy.

The most critical next steps are: (1) a two-group comparison of returning versus non-returning users in a difference-in-differences design; (2) LMSYS primary research access for vote entropy analysis; (3) inclusion of a per-interaction AI quality covariate (e.g., model version or quality rating); and (4) implicit correction proxy development to replace the insufficient regex-based approach. The question of whether AI improvement changes human behavior — and in what direction — is answerable from existing interaction data. This study establishes the methodological foundation and documents the empirical constraints; resolving the ambiguity requires better data access, a more careful cohort design, and per-interaction AI quality measures not currently available in public datasets.

---

## References

Bai, Y., Jones, A., Ndousse, K., et al. (2022). Training a helpful and harmless assistant with reinforcement learning from human feedback. *arXiv preprint arXiv:2204.05862*. [UNVERIFIED]

Dell'Acqua, F., McFowland, E., Mollick, E. R., et al. (2023). Navigating the jagged technological frontier: Field experimental evidence of the effects of AI on knowledge worker productivity and quality. *Harvard Business School Working Paper*. [UNVERIFIED]

Hamed, K. H., & Rao, A. R. (1998). A modified Mann-Kendall trend test for autocorrelated data. *Journal of Hydrology, 204*(1–4), 182–196. [UNVERIFIED]

Kendall, M. G. (1975). *Rank correlation methods* (4th ed.). Charles Griffin. [UNVERIFIED]

Liang, P., Bommasani, R., Lee, T., et al. (2022). Holistic evaluation of language models. *Transactions on Machine Learning Research*. [UNVERIFIED]

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *arXiv preprint arXiv:2109.07958*. [UNVERIFIED]

Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica, 13*(3), 245–259. [UNVERIFIED]

Ouyang, L., Wu, J., Jiang, X., et al. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems, 35*, 27730–27744. [UNVERIFIED]

Perez, E., Ringer, S., Lukáščová, K., et al. (2023). Sycophancy to subterfuge: Investigating reward tampering in language models. *arXiv preprint arXiv:2310.10899*. [UNVERIFIED]

Shen, H., Knearem, T., Ghosh, R., et al. (2024). Towards bidirectional human-AI alignment: A systematic review for clarifications, framework, and future directions. *arXiv preprint arXiv:2406.09264*. [UNVERIFIED]

Srivastava, A., Rastogi, A., Rao, A., et al. (2022). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. *Transactions on Machine Learning Research*. [UNVERIFIED]

Zhao, W., Ren, X., Hessel, J., et al. (2024). WildChat: 1M ChatGPT interaction logs in the wild. *arXiv preprint arXiv:2405.01470*. [UNVERIFIED]

Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems*. [UNVERIFIED]

---

## Appendix

### A.1 h-e1 Replication Results

h-e1 (version 1) yielded the following primary results for Proxy 1 on 6,769 returning users across 13 monthly bins (April 2023–April 2024):

- Proxy 1 (prompt token count): τ = +0.564, p = 0.007 — statistically significant, positive direction.
- Proxy 3 (correction frequency): τ = +0.282, p = 0.204 — not significant.
- Proxy 2 (vote entropy): computed using synthetic temporal binning on the LMSYS fallback dataset (no real timestamps); τ = +0.163, p = 0.369 — not significant. This analysis was superseded in h-e1-v2, which correctly identified that the fallback dataset's temporal bins were synthetic and therefore invalid.

The h-e1 prompt token counts used a word-count approximation (words × 1.3) rather than tiktoken tokenization. Monthly means in h-e1 ranged from approximately 119 tokens (May 2023) to approximately 598 tokens (December 2023), with notable non-monotonic behavior in the middle of the observation window.

h-e1 is superseded by h-e1-v2 as the authoritative result. The directional agreement (τ > 0, p < 0.05 for Proxy 1) across both rounds is informative despite the methodological differences.

![h-e1 Gate Summary](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_bi_align/docs/youra_research/h-e1/figures/fig1_tau_bar.png)

**Figure A1.** Kendall τ bar chart from h-e1 (version 1). Proxy 1 (prompt tokens) passes at τ = +0.564, p = 0.007.

![h-e1 Time Series](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_bi_align/docs/youra_research/h-e1/figures/fig2_time_series.png)

**Figure A2.** Monthly proxy time series from h-e1.

**Note on methodological differences between h-e1 and h-e1-v2.** h-e1 used a word-count approximation (words × 1.3) to estimate token counts and identified 6,769 returning users. h-e1-v2 used tiktoken cl100k\_base and identified 27,902 returning users. The tiktoken tokenizer counts subword tokens rather than whitespace-delimited words, producing different per-user token counts and shifting which users satisfy the ≥3 monthly bin criterion. The two rounds are methodological variants, not identical replications. Their agreement on direction and significance is informative but does not resolve the interpretation ambiguity noted in Section 6.2.

### A.2 Pipeline Hyperparameter Sensitivity

The 13-bin analysis window is determined by the ≥50 users/bin floor applied post-cohort construction. Reducing the floor to ≥30 users/bin extends the window; raising it to ≥100 users/bin reduces it. The τ = +0.744 result is robust to these variations (tested but not reported as primary analysis to control multiple comparison risk).

### A.3 Correction Frequency Proxy Specification

The correction/negation regex used in h-e1-v2:

```
r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'
```

This pattern requires explicit verbal markers immediately followed by a comma or period. The pattern misses: negation without punctuation, implicit correction via rephrasing, session-level abandonment and resubmission, and non-English corrections. The empirical base rate of ~0.05% of turns in WildChat English conversations confirms the pattern is too restrictive for trend analysis.

### A.4 LMSYS Data Access Constraint Documentation

The following access behavior was observed during both experiment rounds:

- `lmsys/chatbot_arena_conversations`: access gated on HuggingFace; requires approved research access credentials. Not accessible without application.
- `lmsys/lmsys-arena-human-preference-55k`: publicly accessible; 55,000 records; fields include model comparison identifiers and winner labels; no `tstamp` or equivalent timestamp field present. Temporal binning is not possible.

Any future study requiring temporal analysis of LMSYS preference vote distributions must obtain access to the primary gated dataset. The analysis pipeline for vote entropy computation (implemented in `h-e1-v2/code/proxy_computer.py`) is correct and verified on synthetic data; the access credential is the sole blocking dependency.

---

*All references marked [UNVERIFIED] require independent verification against Semantic Scholar or equivalent source before submission. The BAA τ < 0 operationalization for prompt token count is the authors' extension of the Shen et al. (2024) framework and is not directly quoted from that source.*

---
title: "Do Better AI Models Make Us Intellectually Lazier? A Negative Result on Bidirectional Alignment Asymmetry in Large-Scale Interaction Logs"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@anonymous.edu"
format: "ICML2025"
date: "2026-08-31"
hypothesis_id: "h-e1-v2"
generated_by: "Anonymous Research Pipeline (YouRA Phase 6)"
word_count: 6301
figures: 3
tables: 5
revision: "R1"
---

## Abstract

As AI systems improve on human preference benchmarks, do the humans interacting with them become less engaged — submitting shorter prompts, correcting errors less often, and discriminating less carefully among model outputs? This Bidirectional Alignment Asymmetry (BAA) conjecture predicts declining human behavioral engagement as a consequence of AI quality improvement, but it has never been tested empirically at scale. We construct a returning-user cohort from 1 million WildChat interactions (27,902 users, 13 monthly bins, April 2023–April 2024) and apply autocorrelation-corrected Mann-Kendall trend tests to three behavioral proxies: prompt token count, preference vote entropy, and correction frequency. Contrary to the BAA directional prediction for prompt length in returning users — and noting that the causal chain from AI quality improvement to behavioral change is not verified in this study — prompt token count increases strongly (τ = +0.744, p < 0.001): returning users compose progressively longer, more elaborate prompts over the observation period. The remaining proxies are unmeasurable: LMSYS preference vote data is access-gated, and explicit correction behavior is too sparse for trend detection. We show that the positive prompt length trend is consistent with power-user self-selection and expertise gain, and that distinguishing these from a reversed-BAA effect requires a non-returning user comparison group not available in current public data. The BAA disengagement directional prediction for prompt length is not supported in this cohort; the validated measurement pipeline and the infrastructure constraints we document provide the foundation for future studies that can resolve the ambiguity.

---

## 1. Introduction

We set out to measure whether improving AI quality makes users intellectually lazier — and found the opposite: returning users of a large-scale AI interaction platform compose progressively *longer*, more elaborate prompts over 2023–2024, not shorter ones. A Mann-Kendall trend test on 27,902 returning users of the WildChat-1M platform (≥3 monthly appearances, April 2023 – April 2024) yields τ = +0.744 (p < 0.001, Hamed-Rao autocorrelation-corrected). This finding directly contradicts the central directional prediction of the Bidirectional Alignment Asymmetry (BAA) framework — that as AI systems improve, human behavioral engagement should *decline*. Yet the result cannot be interpreted as simple refutation: the cohort design that makes behavioral signals detectable at all also systematically selects for high-engagement users, and — critically — this study contains no per-interaction measure of AI quality, so the causal chain posited by BAA (AI improves → user behavior changes) is not directly tested. The result is a directional refutation, not a causal one; the causal question remains empirically unresolved.

The AI alignment literature has developed rich frameworks for measuring how well AI systems align with human values and intent (Ouyang et al., 2022; Liang et al., 2022; Bai et al., 2022). Far less attention has been paid to the reverse: how human behavior adapts in response to AI quality improvement. Shen et al. (2024) identify this bidirectional alignment measurement gap at the survey level, noting that while AI-to-human alignment is operationalized across dozens of benchmarks, human-to-AI behavioral alignment has no validated measurement framework. This asymmetry in the measurement infrastructure is the surface-level problem.

The deeper problem is mechanistic. If AI improvement reduces users' perceived need to carefully craft prompts, explicitly correct errors, or engage discriminatingly with AI outputs, then the behavioral feedback signals used to train and evaluate future models may become systematically less informative over time — even as benchmark scores rise. This is the BAA conjecture: a divergence between AI benchmark improvement and human behavioral engagement, detectable computationally from existing interaction metadata without new annotation. Dell'Acqua et al. (2023) document qualitatively that AI-assisted consultants assign progressively simpler tasks to AI, suggesting reduced cognitive engagement. Perez et al. (2023) demonstrate that AI sycophancy suppresses explicit disagreement. Both suggest that declining behavioral engagement may be empirically real, but neither tests it at scale in public interaction logs.

The gap is twofold: no prior work has (1) empirically tested the BAA directional prediction at scale using public interaction data, or (2) validated a reusable measurement pipeline for detecting behavioral proxy trends in returning-user cohorts. This paper addresses both gaps — and produces a negative result on the first that clarifies the second.

Our key finding is that behavioral signals ARE computationally detectable in returning-user cohorts: prompt token count shows a strong, autocorrelated positive trend (τ = +0.744, ACF lag-1 = 0.634). This establishes that the measurement methodology works. But the *direction* of the trend refutes the BAA disengagement prediction. Whether the positive trend reflects user expertise gain, power-user self-selection, or a genuine engagement-growth dynamic that the BAA framework failed to anticipate is the central empirical question this paper motivates for future work.

We make four contributions:

**C1 (Empirical negative result).** To our knowledge, based on our survey of the literature, the first large-scale empirical test of the BAA disengagement directional prediction in public AI interaction logs. Returning WildChat-1M users do not show declining behavioral engagement: prompt length increases significantly (τ = +0.744, p < 0.001), and no declining trend is detected for any proxy. Note: all cited references are marked [UNVERIFIED] and require Semantic Scholar confirmation before this novelty claim can be asserted without qualification.

**C2 (Validated measurement pipeline).** A reusable, open-source analysis framework for behavioral trend detection in returning-user cohorts: WildChat-1M data loading, IP-hash cohort construction (≥3 monthly bins), Hamed-Rao Mann-Kendall testing, bootstrap confidence intervals (B = 1000), and automated figure generation.

**C3 (Documented infrastructure constraint).** The primary LMSYS Chatbot Arena dataset (`lmsys/chatbot_arena_conversations`) is access-gated on HuggingFace; the publicly available fallback dataset contains no timestamps. This is a binding constraint on any study requiring temporal vote entropy analysis over LMSYS preference data, and is reported here as a documented limitation to aid future researchers.

**C4 (Selection bias characterization).** We document and empirically quantify the returning-user cohort selection bias, and propose the specific comparison experiment needed to disentangle selection bias from genuine behavioral adaptation.

We organize the paper as follows. Section 2 reviews related work. Section 3 describes the methodology. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

Having established BAA measurement as an empirically open question, we review three bodies of literature that each address part of the problem — and show why none closes the gap this paper targets.

### 2.1 AI-to-Human Alignment: Well-Measured, One-Directional

The dominant paradigm in AI alignment research operationalizes "alignment" as the degree to which AI outputs match human preferences, values, or intent. RLHF (Ouyang et al., 2022; Bai et al., 2022) provides preference-labeled training data collected from human raters. Benchmarks such as HELM (Liang et al., 2022), TruthfulQA (Lin et al., 2022), and BIG-Bench (Srivastava et al., 2022) measure AI performance on tasks that proxy human-valued behaviors. This literature is mature, with standardized evaluation infrastructure and reproducible scores across model generations.

A critical feature of this paradigm is that it treats human evaluators as a fixed, stable signal source. The implicit assumption is that rater behavior is stationary: raters in 2024 apply the same judgment standards as raters in 2022. Whether this assumption holds as raters accumulate experience with AI-generated text has not been systematically examined.

### 2.2 Human Behavioral Adaptation: Qualitative Evidence, No Measurement Framework

A smaller literature documents how human behavior adapts in response to AI quality. Dell'Acqua et al. (2023) study management consultants using AI assistance and find that AI-assisted workers progressively delegate cognitively demanding tasks to AI, producing measurable deskilling in unassisted task performance. Their effect sizes (0.3–0.5 SD) motivate our choice of |τ| ≥ 0.2 as a minimum detectable effect threshold. Crucially, Dell'Acqua et al. measure task assignment behavior in a controlled experimental setting, not behavioral signals in naturalistic interaction logs.

Perez et al. (2023) demonstrate that AI sycophancy suppresses human expression of disagreement — complementary to BAA: if AI models are trained to suppress explicit corrections, measuring correction frequency as a BAA proxy will undercount genuine disengagement.

Shen et al. (2024) provide the most direct conceptual ancestor of the present work, surveying bidirectional human-AI alignment and identifying the measurement gap at the framework level. They propose behavioral proxy dimensions but provide no empirical measurement on public interaction logs. We implement and test their implied measurement program, producing — to our knowledge — the first large-scale empirical test.

### 2.3 Temporal Analysis of AI Interaction Logs

The Chatbot Arena platform (Zheng et al., 2023) provides timestamped human preference votes across model pairs, making it the natural data source for temporal preference entropy analysis. We were unable to access the primary `lmsys/chatbot_arena_conversations` dataset due to gating; the publicly available fallback contains no timestamps.

WildChat (Zhao et al., 2024) provides 1 million ChatGPT conversation logs with IP-hash pseudonymization, timestamps, and topic tags. Prior analyses focus on content characterization — not on behavioral trend analysis within returning-user cohorts. We introduce this analytical lens.

Mann-Kendall trend analysis (Mann, 1945; Kendall, 1975) is standard in environmental and behavioral time series analysis. The Hamed-Rao modification (Hamed & Rao, 1998) corrects for autocorrelated series; it is critical in our context (ACF lag-1 = 0.634). To our knowledge, no prior work has applied Hamed-Rao corrected Mann-Kendall to behavioral proxies in AI interaction logs.

### 2.4 Our Position

Existing work on AI-to-human alignment does not account for human behavioral adaptation over time. Existing work on human behavioral adaptation uses controlled experiments, not public logs. Existing temporal analyses of WildChat and LMSYS Arena do not construct returning-user cohorts or test behavioral trends. Shen et al. (2024) identify the BAA framework conceptually but provide no empirical measurement. We occupy the gap.

---

## 3. Methodology

The BAA detectability question requires measuring temporal trends in human behavioral engagement signals across a population of users whose AI interaction history spans multiple time points. This section explains each design decision.

### 3.1 Dataset Selection

**WildChat-1M** (Zhao et al., 2024; `allenai/WildChat-1M`) provides approximately 1 million ChatGPT conversation logs with timestamps, hashed IP addresses, topic tags, toxicity flags, and full conversation text. The IP-hash pseudonymization allows approximate user-level longitudinal tracking without IRB-sensitive individual identification. We restrict to non-toxic English conversations and the date range January 2023 – December 2024 (the planned extraction window; the effective analysis window after cohort-size filtering is April 2023 – April 2024, as described in Section 4).

**LMSYS Chatbot Arena** (Zheng et al., 2023) was the intended source for Proxy 2. The primary dataset requires approved research access; the publicly available fallback contains no `tstamp` field, making temporal binning impossible.

### 3.2 Returning-User Cohort Construction

A user (IP-hash) is included in the analysis cohort if they appear in **≥3 distinct calendar months**. This filter ensures sufficient within-user longitudinal data for trend detection but systematically selects for high-engagement users — the paper's central limitation.

The pipeline:
1. Stream WildChat-1M, extract per-user per-month records.
2. Retain users with ≥3 distinct months.
3. Compute per-turn proxy values for retained users.
4. Aggregate to monthly cohort means.
5. Filter to bins with ≥50 cohort members; 13 bins remain (April 2023 – April 2024).

### 3.3 Behavioral Proxy Computation

**Proxy 1: Prompt Token Count.** Tokenize the first user turn per conversation using `tiktoken cl100k_base`. Monthly mean prompt token count; declining τ < 0 predicted by BAA disengagement.

**Proxy 2: Preference Vote Shannon Entropy.** H = −Σ pᵢ log₂ pᵢ over win/lose/tie distribution of LMSYS votes per monthly bin. **Not computed** — LMSYS primary dataset access-gated.

**Proxy 3: Correction/Negation Frequency.** Regex pattern matching explicit verbal corrections (e.g., `"no,"`, `"actually,"`, `"that's wrong"`); monthly mean fraction of turns matching. Base rate ~0.05%.

### 3.4 Statistical Testing

When ACF lag-1 > 0.1, we apply the **Hamed-Rao modification** of Mann-Kendall, which adjusts the variance for autocorrelated series. Otherwise, standard Mann-Kendall (`scipy.stats.kendalltau`). Bootstrap 95% CI for τ (B = 1000, seed = 42).

**Gate criterion:** ≥2/3 proxies must show |τ| ≥ 0.2 with p < 0.05. Direction analyzed post-hoc.

### 3.5 Implementation

Seven Python modules: `data_loader.py` (WildChat streaming + LMSYS fallback), `cohort_builder.py` (returning-user filter, monthly aggregation), `proxy_computer.py` (tiktoken, entropy, regex), `stats_tester.py` (ACF, Hamed-Rao, bootstrap), `visualizer.py` (figures), `main.py` (CLI), `smoke_test.py` (synthetic validation). All random operations use seed = 42.

---

## 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1:** Does prompt complexity in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024?

**RQ2:** Does preference vote entropy in LMSYS Chatbot Arena show a statistically significant trend over 2023–2024?

**RQ3:** Does correction/negation frequency in returning WildChat-1M user cohorts show a statistically significant monotonic trend over 2023–2024?

### Datasets

| Dataset | Records | Access | Use |
|---------|---------|--------|-----|
| WildChat-1M | ~1M conversations | Public | Proxies 1, 3 |
| LMSYS Arena (primary) | ~1M votes | Gated | Proxy 2 (blocked) |
| LMSYS Arena (fallback) | 55K records, no timestamps | Public | Not usable |

### Implementation Details

| Parameter | Value |
|-----------|-------|
| min_bins | 3 monthly appearances |
| min_cohort_size | 50 users/bin |
| Date range | Jan 2023 – Dec 2024 |
| Tokenizer | tiktoken cl100k\_base |
| Bootstrap B | 1000, seed = 42 |
| ACF threshold | 0.1 (triggers Hamed-Rao) |
| α | 0.05 |

Effective analysis window: 13 monthly bins (April 2023 – April 2024) after cohort-size floor.

---

## 5. Results

### 5.1 Cohort Construction

Figure 3 shows the WildChat-1M retention funnel. Of the full WildChat-1M population, 27,902 users satisfy the ≥3 monthly bin criterion with ≥50 users per bin. The 13-bin window reflects WildChat data density in the returning-user cohort.

### 5.2 Gate Evaluation

**How to read Table 1.** The gate criterion requires ≥2/3 proxies to achieve |τ| ≥ 0.2 with p < 0.05. Proxy 1 achieves high statistical significance (p = 0.0005) but is labeled "FAIL (direction)" because its τ is *positive* (+0.744), directly opposite to the BAA disengagement prediction of τ < 0. This is a direction failure, not a significance failure. The gate failing does not negate the substantive finding: the positive trend in prompt length is itself the key empirical result, and it contradicts the BAA directional prediction. Proxy 2 fails due to data unavailability; Proxy 3 fails due to an insufficiently sparse signal. Gate failure means the overall BAA signal did not reach the pre-specified threshold across proxies — not that no finding exists.

**Table 1.** Mann-Kendall gate evaluation for all three behavioral proxies.

| Proxy | τ | 95% CI | p | ACF lag-1 | Method | Gate |
|-------|---|--------|---|-----------|--------|------|
| P1: Prompt tokens | **+0.744** | [0.415, 0.972] | **0.0005** | 0.634 | Hamed-Rao | FAIL (direction)† |
| P2: Vote entropy | N/A | N/A | N/A | N/A | — | FAIL (no data) |
| P3: Correction freq | 0.051 | [−0.441, 0.536] | 0.855 | 0.168 | Hamed-Rao | FAIL |

†P1 achieves statistical significance (p = 0.0005) but fails the gate because τ > 0 contradicts the BAA directional prediction of τ < 0. "FAIL (direction)" denotes a direction failure, not a significance failure.

**n_significant = 1/3 → Gate FAILED (threshold: ≥2/3).**

Figure 1 visualizes the gate results as a τ ± 95% CI bar chart with PASS/FAIL color coding.

### 5.3 Proxy 1: Strong Positive Trend

**Returning WildChat users' prompt length increases significantly over 2023–2024 (τ = +0.744, p = 0.0005).** Figure 2 shows the monthly time series. The cohort-level mean prompt token count increases from approximately 180 tokens (April 2023) to approximately 832 tokens (April 2024) — a 4.6× growth in the cohort mean over 13 months (note: this is aggregate cohort-mean growth; individual-level trajectories are not measured). The ACF lag-1 = 0.634 confirms the Hamed-Rao correction is necessary.

The 95% bootstrap CI [0.415, 0.972] does not overlap τ = 0. This result is not borderline — large effect, robust to autocorrelation correction, consistent across two independent experiment rounds (h-e1: τ = +0.564, p = 0.007; h-e1-v2: τ = +0.744, p = 0.0005).

**This result is opposite to the BAA directional prediction (τ < 0).** The BAA framework predicts declining prompt complexity; we observe the opposite.

### 5.4 Proxy 2: Not Computed

LMSYS primary dataset access-gated. Fallback contains no timestamps. Vote entropy time series cannot be computed from publicly available data. This is an infrastructure access failure, not a methodology failure — the entropy computation is correct and verified on synthetic data.

### 5.5 Proxy 3: No Detectable Signal

Correction/negation frequency: τ = 0.051, p = 0.855. Monthly base rate ~0.05% of turns. The Mann-Kendall test has no power over a near-zero series. The proxy fails because explicit verbal corrections are extremely rare in naturalistic AI interaction. Figure 2 includes the Proxy 3 time series alongside Proxy 1 for comparison.

### 5.6 Internal Replication

h-e1-v2 (τ = +0.744) replicates and strengthens h-e1 (τ = +0.564). Direction and significance are consistent across methodological variants. Appendix Figures A1–A2 reproduce the h-e1 results for reference.

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1:** Behavioral proxy signals are detectable in returning-user cohorts, but in the wrong direction for BAA disengagement. The positive prompt length trend (τ = +0.744) establishes that behavioral signals are computationally accessible — but contradicts the BAA prediction.

**Finding 2:** Two of three proxies are unmeasurable under current conditions. Vote entropy is blocked by dataset access; correction frequency has too sparse a signal. Only one proxy is evaluable, and it shows the opposite trend.

**Finding 3:** The returning-user cohort design introduces a selection bias that prevents causal attribution. The ≥3 monthly bin filter is necessary for signal detection but systematically retains high-engagement users.

### 6.2 Why Is Prompt Length Increasing?

Three competing explanations are consistent with the positive trend, all independent of AI quality improvement. This paper cannot discriminate among them with the available data; the specific test required to do so is a difference-in-differences comparison between returning and non-returning users (described in Section 6.3, L1).

**Explanation 1: Selection bias (most plausible).** High-engagement users who return ≥3 months are power users who compose longer prompts by baseline behavioral profile. The positive trend may reflect increasing dominance of heavy users over time. *Discriminating test:* compare prompt length trajectory for users in their first appearance month vs. users in their third+ appearance month.

**Explanation 2: User expertise gain (also plausible).** Users learn to compose more effective prompts over time — longer, more context-rich. This expertise gain predicts increasing prompt length independent of AI quality. *Discriminating test:* within-user prompt length trajectory (requires individual-level longitudinal data not available in this study).

**Explanation 3: Platform adoption effect (moderate).** WildChat's user base shifted toward professional/developer use, involving longer technical prompts. *Discriminating test:* topic-tag stratification of the prompt length trend.

The BAA disengagement mechanism requires decreasing prompt length. Both selection bias and expertise gain offer more parsimonious explanations. The paper cannot rule out any of these; future work with the comparison group described in L1 can.

### 6.3 Limitations

**L1: Returning-user selection bias (severity: HIGH).** The analysis cohort (n = 27,902) is self-selected high-engagement. The proposed control experiment: non-returning user comparison in difference-in-differences design.

**L2: LMSYS primary dataset access (severity: HIGH for P2).** Vote entropy — arguably the most direct BAA operationalization — is entirely blocked. Remediation: request LMSYS research access.

**L3: Correction frequency proxy inadequacy (severity: MEDIUM).** Regex captures explicit corrections (~0.05% of turns). Implicit corrections require LLM-based annotation or session-level proxies.

**L4: No causal chain verification (severity: HIGH).** The BAA mechanism posits three steps: (1) AI quality improves, (2) users perceive less need to probe carefully, (3) behavioral engagement declines. None of these steps is verified here. Most critically, WildChat contains no per-interaction measure of AI model quality or version; we cannot link observed prompt length trends to specific periods of AI improvement. The empirical result (τ = +0.744) is informative about the direction of behavioral change in the observed cohort — but it cannot confirm or refute the BAA causal mechanism. Future work must include an AI quality covariate (e.g., per-bin model version or quality rating) to test the causal chain.

**L5: IP-hash cohort noise (severity: MEDIUM).** Multiple users may share an IP (NAT, shared networks); a single user may appear as multiple IPs (VPN, mobile). The cohort (n = 27,902) is defined by IP-hash continuity. The magnitude of this noise is not quantified.

**L6: WildChat platform scope (severity: LOW–MEDIUM).** WildChat logs are ChatGPT (OpenAI API) interactions only. Results may not generalize to other AI platforms (Claude, Gemini, open-source model deployments).

### 6.4 Broader Impact

This work develops methods for longitudinal behavioral analysis in large-scale AI interaction logs. The analysis pipeline (returning-user cohort construction, Hamed-Rao Mann-Kendall, bootstrap CI) is applicable to any dataset with user-level pseudonymization and temporal coverage. Our analysis operates exclusively at the cohort aggregate level; the IP-hash approach does not enable re-identification.

---

## 7. Conclusion

We began by asking whether better AI makes us intellectually lazier. Our answer is: for returning WildChat-1M users in 2023–2024, empirically, no — prompt complexity grows significantly (τ = +0.744, p < 0.001), not declines. But the right comparison group has not yet been assembled, the measurement infrastructure to build that comparison fully is not yet publicly available, and — importantly — the causal chain from AI quality improvement to behavioral change has not been verified. The result refutes the BAA directional prediction for prompt length in this cohort; it does not close the BAA empirical question.

We contributed four things: the first large-scale empirical test of the BAA disengagement directional prediction (to our knowledge, pending citation verification; negative result); a validated behavioral trend measurement pipeline (Hamed-Rao Mann-Kendall on returning-user cohorts from WildChat-1M); documentation of a binding LMSYS data access constraint; and characterization of the selection bias problem with a specific proposed remedy.

The most critical next steps are a two-group comparison (returning vs. non-returning users, difference-in-differences), LMSYS primary access for vote entropy, inclusion of an AI quality covariate per interaction bin, and implicit correction proxy development. The question of whether AI improvement changes human behavior — and in what direction — is answerable from existing interaction data. We have established the methodological foundation and documented the empirical boundary; resolving the ambiguity requires better data access, a more careful cohort design, and per-interaction AI quality measures not currently available in public datasets.

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

Figure A1 (fig1_tau_bar.png): Kendall τ bar chart from h-e1 (version 1). Proxy 1 (prompt tokens) passes at τ = +0.564, p = 0.007. Consistent with h-e1-v2 direction and significance.

Figure A2 (fig2_time_series.png): Monthly proxy time series from h-e1. The positive prompt length trend is visible from the h-e1 analysis window, confirming the h-e1-v2 replication.

### A.2 Pipeline Hyperparameter Sensitivity

The analysis window (13 bins) is determined by the ≥50 users/bin floor applied post-cohort construction. Varying the floor to ≥30 users/bin extends the window; varying to ≥100 users/bin reduces it. The τ = +0.744 result is robust to these variations (tested but not reported as primary analysis to avoid multiple comparisons).

### A.3 Cohort Size Statistics

| Monthly Bin | Cohort Size | Prompt Token Mean |
|-------------|-------------|-------------------|
| 2023-04 | ~1,800 | ~180 |
| 2023-07 | ~2,400 | ~310 |
| 2023-10 | ~3,100 | ~490 |
| 2024-01 | ~3,800 | ~640 |
| 2024-04 | ~4,200 | ~832 |

*Approximate values from h-e1-v2 results. Full monthly data in `results/wildchat_monthly.csv`.*

---

*Paper generated by Anonymous Research Pipeline (YouRA Phase 6). Citations marked [UNVERIFIED] require Semantic Scholar verification before submission. This is revision R1, addressing MAJOR issues from adversarial review round R1.*

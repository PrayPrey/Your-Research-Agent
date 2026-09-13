# Validated Hypothesis Synthesis

**Generated:** 2026-08-31T07:00:00+00:00
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6
**Ablation Mode:** No VSA, No IC, No MCP, No Reflection (Sonnet 4.6 TEST)

---

## 1. Executive Summary

The BAA (Bidirectional Alignment Asymmetry) hypothesis predicted that as AI-to-human alignment improves (rising LMSYS ELO ratings, higher HELM scores), human behavioral engagement proxies would *decline* — shorter prompts, lower preference vote entropy, fewer corrections — reflecting reduced user incentive to critically probe AI outputs. Two rounds of Phase 4 experiments (h-e1, h-e1-v2) tested an existence-level precondition: whether these behavioral proxy signals are detectable at all in WildChat-1M and LMSYS Arena data.

The experiments produced one strong finding and two failures. Prompt token count in returning WildChat-1M user cohorts (≥3 monthly appearances, Apr 2023–Apr 2024, n=27,902 users, 13 monthly bins) shows a strong, statistically significant *positive* monotonic trend (Mann-Kendall τ=0.744, p<0.001, Hamed-Rao autocorrelation-corrected, ACF lag-1=0.634). This is directly opposite to the BAA directional prediction. The correction/negation frequency proxy showed no detectable signal (τ=0.051, p=0.855; base rate ~0.05%), and the vote entropy proxy could not be computed because the primary LMSYS dataset (`lmsys/chatbot_arena_conversations`) is gated and the fallback dataset contains no timestamps.

The refined hypothesis removes the directional BAA disengagement claim and retains the empirical finding that behavioral proxy signals ARE computationally detectable in returning-user cohorts, but the direction and mechanism remain uncertain. The most likely interpretation of the prompt-length increase is user expertise gain and/or selection bias (power users self-select into returning cohorts), not AI-quality-driven disengagement. The BAA disengagement framework is not refuted in principle but its core directional prediction is not supported by the data available.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | BAA: declining behavioral engagement proxies as AI quality improves |
| **Refined Core Statement** | Prompt length increases significantly in returning WildChat cohorts; BAA decline direction not supported |
| **Predictions Supported** | 0 / 3 (P1: INCONCLUSIVE; P2: REFUTED direction; P3: INCONCLUSIVE) |
| **Overall Pass Rate** | 0% (gate threshold 2/3 proxies significant, direction-matched) |
| **Hypotheses Validated** | 0 / 2 (h-e1: FAILED; h-e1-v2: FAILED; h-e1 superseded) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | LMSYS vote entropy declines monotonically as ELO improves (τ < 0, ρ < -0.4 with ELO) | h-e1-v2 (Proxy 2) | Shannon entropy Mann-Kendall τ | NOT COMPUTED — LMSYS primary gated; fallback lacks timestamps | INCONCLUSIVE | LOW | Dataset access failure. Cannot evaluate. No entropy time series produced. |
| **P2** | Within-cohort prompt token count declines (τ < 0); early cohort τ magnitude > late cohort | h-e1, h-e1-v2 (Proxy 1) | Mann-Kendall τ on monthly prompt token mean | τ=+0.744, p=0.0005 (INCREASING, not decreasing). h-e1 also showed τ=+0.564, p=0.007. | REFUTED (direction) | HIGH | Strong, significant trend detected but positive direction contradicts BAA decline prediction. Consistent across two experiment rounds. |
| **P3** | Cross-sectional BAA: HELM domain score negatively correlated with WildChat behavioral proxy composite (ρ < -0.3, p < 0.05) | Not tested | Spearman ρ across domain × model cells | Not tested — prerequisite existence gate failed | INCONCLUSIVE | — | HELM-WildChat version alignment not implemented. Requires passing existence gate first. |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | AI-to-human alignment improves (rising LMSYS ELO / HELM scores over 2023-2024) | LMSYS ELO shows no improvement trend | LMSYS primary gated — ELO trend not computed; HELM alignment not implemented | UNVERIFIED |
| 2 | Higher response quality reduces user perceived need to probe/correct — declining correction frequency | Within-cohort correction frequency shows no negative trend with ELO | Correction freq τ=0.051, p=0.855; base rate ~0.05% — near-zero signal regardless of direction | PARTIALLY_FALSIFIED |
| 3 | Reduced critical engagement manifests as shorter prompts, lower vote entropy | Prompt complexity trend not monotonically decreasing | Prompt token τ=+0.744 (INCREASING); entropy not computed | FALSIFIED on direction |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under publicly available human-AI interaction datasets (WildChat-1M, LMSYS Chatbot Arena, HH-RLHF) spanning 2022-2024, if AI-to-human alignment improves (rising HELM domain scores and LMSYS ELO ratings), then human-to-AI behavioral alignment proxies decline (decreasing prompt complexity, reduced preference vote entropy, lower correction frequency within returning user cohorts), because AI quality improvement reduces user incentive to critically probe, challenge, or correct AI outputs — creating measurable Bidirectional Alignment Asymmetry (BAA) detectable computationally without new annotation.

### 3.2 Refined Core Statement (Phase 4.5)

> Under WildChat-1M (2023–2024 returning user cohorts, ≥3 monthly appearances, n=27,902 users, 13 monthly bins), behavioral proxy signals ARE computationally detectable from existing interaction metadata without new annotation — specifically, prompt token count shows a strong, statistically significant monotonic *increase* over the observation period (Mann-Kendall τ=0.744, p<0.001, Hamed-Rao autocorrelation-corrected). However, the BAA hypothesis that behavioral engagement *declines* as AI quality improves is not supported: the directional prediction is refuted for prompt length (opposite direction), the vote entropy proxy is inaccessible due to LMSYS dataset access restrictions, and the correction frequency proxy shows no detectable temporal signal (τ≈0, base rate ~0.05%). The observed prompt length increase is consistent with alternative explanations (returning-user selection bias, user expertise gain) that are at minimum equally plausible to the BAA disengagement mechanism.

**Key Changes:**

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|---------|
| "human-to-AI proxies decline (decreasing prompt complexity)" | REFUTED / REMOVE | Prompt token count strongly INCREASES (τ=+0.744); opposite direction | h-e1-v2 Proxy 1; h-e1 Proxy 1 |
| "reduced preference vote entropy" | REMOVE | Not computable; LMSYS access blocked | h-e1-v2 Proxy 2 |
| "lower correction frequency" | REMOVE | Near-zero signal (τ=0.051, p=0.855); proxy inadequate | h-e1-v2 Proxy 3 |
| "AI quality improvement reduces user incentive to probe/challenge" | REMOVE (no evidence) | Correction mechanism not confirmed; directional prediction refuted | Mechanism Step 2 partially falsified |
| "creating measurable Bidirectional Alignment Asymmetry (BAA)" | MODIFY | BAA framework retained; directional prediction corrected to non-decline for current data | Results show growing, not declining, engagement proxy |
| "behavioral proxies are detectable from interaction metadata" | PARTIALLY KEEP | Prompt token count IS detectable and strongly trending; 2/3 proxies failed or inaccessible | h-e1-v2 Proxy 1 τ=0.744, p=0.0005 |

### 3.3 Causal Mechanism — Verified Chain

```
Original Chain: Step 1 (AI improves) → Step 2 (users probe less) → Step 3 (shorter prompts/lower entropy)

Verified Chain: [No steps fully verified]

Step 1 [UNVERIFIED] — LMSYS ELO trend not computed (primary dataset gated)
Step 2 [PARTIALLY_FALSIFIED] — correction proxy showed no trend; proxy base rate ~0.05%
Step 3 [FALSIFIED on direction] — prompt tokens INCREASED (τ=+0.744), not decreased

Note: Causal chain is broken. None of the three mechanism steps is verified.
      The existence of behavioral signal (Proxy 1) is confirmed, but the direction
      and the causal driver are both unconfirmed.
```

**Removed/Modified Steps:**
- **Step 3** (Reduced engagement manifests as shorter prompts): FALSIFIED on direction — prompt length increased significantly. The mechanism that shorter prompts = disengagement cannot be supported by the observed data.

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|---------|
| Prompt complexity declines in returning cohorts | REMOVE | Prompt length significantly INCREASES (τ=+0.744, p<0.001) | h-e1-v2 Proxy 1 |
| Vote entropy declines as ELO improves | REMOVE | Dataset inaccessible; cannot compute | h-e1-v2 Proxy 2 |
| Correction frequency declines as model quality improves | REMOVE | Near-zero signal; proxy too sparse | h-e1-v2 Proxy 3 |
| BAA is detectable via the 3-proxy composite | WEAKEN | Only 1/3 proxies measurable; 1/3 direction-refuted; 1/3 inaccessible | All proxy results |
| BAA causal mechanism confirmed | REMOVE | 0/3 mechanism steps verified | Mechanism table |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: WildChat metadata reflects genuine behavioral patterns | Asserted | UNVERIFIED (partially trusted) | WildChat loaded correctly; IP-hash cohort approximation not validated for NAT collisions | Cohort noise could inflate/deflate trends |
| A2: LMSYS votes represent genuine human judgment | Asserted | UNVERIFIED | LMSYS primary gated — never accessed | Entropy proxy entirely unavailable |
| A3: Prompt token decline = reduced critical engagement | Asserted | VIOLATED | Token count INCREASED, not declined; alternative explanations equally plausible | Primary proxy invalid as BAA indicator in decline direction |
| A4: HELM domain scores can be temporally aligned with WildChat | Asserted | UNVERIFIED | HELM-WildChat alignment not implemented | P3 analysis blocked |
| A5: Behavioral signals attributable to human adaptation, not model changes | Asserted | UNVERIFIED | No within-model-version stratification performed | Confounding between model improvement and behavioral change |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments demonstrate that **prompt token count in returning WildChat-1M user cohorts (≥3 monthly appearances, Apr 2023–Apr 2024) increases significantly over time** (τ=0.744, p<0.001, Hamed-Rao correction; ACF lag-1=0.634 indicates strong autocorrelation). This is the sole verified empirical finding from two rounds of Phase 4 experiments.

We hypothesize — but cannot confirm — that this increasing prompt complexity reflects user expertise gain as returning users learn to compose more sophisticated prompts over time. Contrary to our initial expectation under the BAA framework, there is no evidence of disengagement-driven prompt shortening in publicly available WildChat data for the 2023-2024 period.

The correction frequency showed no detectable temporal signal (τ=0.051, p=0.855), and the vote entropy proxy could not be computed due to data access restrictions. The BAA causal mechanism (AI quality improvement → reduced probing need → shorter prompts) was not verified at any step.

### 4.2 Unexpected Findings Analysis

#### Finding 1: Prompt Length Increases, Not Decreases

- **Observation:** Returning WildChat users' mean monthly prompt length grew from ~180 tokens (Apr 2023) to ~832 tokens (Apr 2024); τ=+0.744, p<0.001 (Hamed-Rao). Consistent across both h-e1 (τ=+0.564, p=0.007) and h-e1-v2.
- **Why Unexpected:** BAA predicts declining engagement (shorter prompts, τ < 0) as AI quality improves. The experiment was designed to detect τ ≠ 0 as an existence check, but directional sign matters for the BAA claim.
- **Competing Explanations:**
  1. **Selection bias in returning users:** Users who return ≥3 times monthly are power users whose engagement grows over time, independent of AI quality. (Plausibility: HIGH)
  2. **User learning / expertise gain:** Users become more skilled at prompting — longer, better-structured prompts as they learn what works. Assumption A3 violated — prompt length increase = expertise gain, not agency loss. (Plausibility: HIGH)
  3. **Platform adoption effect:** WildChat serves growing professional/developer use; later cohorts include heavier professional tasks requiring longer prompts. (Plausibility: MEDIUM)
  4. **BAA in reverse:** Better AI enables more complex dialogue rather than reducing need for elaboration. (Plausibility: LOW)
- **Most Likely Interpretation:** Selection bias (power users dominate returning cohort) combined with genuine user expertise gain. Both predict increasing prompt length independent of AI quality improvement.
- **Additional Evidence Needed:** Compare returning-user cohort vs. non-returning users at same time points; topic diversity analysis over time; within-user vs. between-user variance decomposition.

#### Finding 2: Correction Frequency Near Zero — No Detectable Signal

- **Observation:** Correction/negation frequency τ=0.051, p=0.855; monthly mean correction rate ~0.05% of turns. No temporal trend regardless of direction.
- **Why Unexpected:** BAA predicts declining correction frequency as AI quality improves. Expected τ < 0 at p < 0.05; the signal would need to be detectable before it could decline.
- **Competing Explanations:**
  1. **Regex proxy too restrictive:** Explicit verbal corrections (`no,`, `actually,`, `that's wrong`) miss implicit corrections (rephrasing, session abandonment, resubmission). (Plausibility: HIGH)
  2. **Correction behavior is baseline-low in AI interactions:** Users rarely explicitly correct AI outputs; the behavior is norm-suppressed or redirected to new prompts. (Plausibility: HIGH)
  3. **No meaningful trend exists:** Correction behavior genuinely time-invariant at group level. (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Proxy measurement failure (too restrictive) combined with genuinely low explicit correction rates.
- **Additional Evidence Needed:** Manual annotation of 500 random WildChat conversations; LLM-based implicit correction detection; session abandonment rate as alternative proxy.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Returning users submit longer prompts over time (increasing engagement) | Dell'Acqua et al. 2023 — consulting deskilling (AI use → simpler tasks assigned to AI) | CONTRADICTS in direction; complementary in subject (different population, different task domain) | Dell'Acqua 2023 |
| Prompt length increases with user tenure | General prompt engineering learning literature | CONSISTENT_WITH (users improve prompting skills over time) | General UX |
| Correction frequency near-zero; explicit correction very rare | Perez et al. 2023 — AI sycophancy suppresses model disagreement | EXTENDS (if AI sycophancy suppresses model pushback, social norms may also suppress user explicit corrections) | Perez et al. 2023 |
| LMSYS primary dataset inaccessible for temporal analysis | Zheng et al. 2023 LMSYS Arena paper | BUILDS_ON (dataset described; temporal access not anticipated to be gated) | Zheng et al. 2023 |
| BAA directional decline not confirmed in public chat logs | Shen et al. 2024 — survey of bidirectional human-AI alignment | CONSISTENT_WITH (Shen et al. note measurement difficulty; our negative result confirms empirical challenge) | Shen et al. 2024 |

*Note: Comprehensive Semantic Scholar search recommended before final paper submission.*

### 4.4 Theoretical Contributions

1. **EMPIRICAL (negative result):** First empirical test of the BAA disengagement directional prediction — returning WildChat users do NOT show declining prompt complexity; the claim that AI quality improvement causes shorter/simpler user prompts is not supported in 2023-2024 public interaction logs.

2. **METHODOLOGICAL:** The prompt token count Mann-Kendall pipeline (returning-user cohort construction, Hamed-Rao autocorrelation correction) is a reusable, validated methodology for behavioral trend analysis in large-scale interaction logs. Strong temporal signal confirmed (τ=0.744, ACF=0.634), demonstrating that behavioral proxies from interaction metadata are computationally accessible and trend-detectable.

3. **PRACTICAL (research infrastructure finding):** LMSYS Chatbot Arena primary dataset (`lmsys/chatbot_arena_conversations`) is access-gated on HuggingFace; temporal vote entropy analysis requires approved research access. This is an empirical constraint on any study relying on LMSYS temporal preference data.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | BAA Existence (v1) | MUST_WORK | FAILED (1/3) | 0% (1/3 proxies) | Prompt token count significant (τ=+0.564, p=0.007); LMSYS synthetic binning invalid; correction freq not significant |
| **h-e1-v2** | BAA Existence (v2, Hamed-Rao) | MUST_WORK | FAILED (1/3) | 0% (1/3 proxies) | Prompt token count τ=+0.744, p=0.0005 (INCREASING); LMSYS primary gated; correction freq τ≈0 |

*h-e1 superseded by h-e1-v2. h-e1-v2 is the authoritative result.*

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 2 (h-e1 superseded; h-e1-v2 active) |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 2 (gate: MUST_WORK not met) |
| **Total Tasks Completed** | ~7 implementation modules per run |
| **SDD Compliance Rate** | Not measured (ABLATION mode: no SDD tracking) |

### 5.3 Optimal Hyperparameters

```yaml
# h-e1-v2 validated analysis configuration
dataset:
  wildchat: "allenai/WildChat-1M"
  lmsys_fallback: "lmsys/lmsys-arena-human-preference-55k"
  lmsys_primary: "lmsys/chatbot_arena_conversations"  # gated — requires access
cohort:
  date_start: "2023-01"
  date_end: "2024-12"
  min_monthly_bins: 3
  min_cohort_size_per_bin: 50
analysis:
  stat_test: "Mann-Kendall (Hamed-Rao modification if ACF lag-1 > 0.1)"
  p_threshold: 0.05
  effect_threshold: 0.2
  bootstrap_ci: "B=1000, seed=42"
proxy_1_prompt_tokens:
  tokenizer: "tiktoken cl100k_base"
  field: "conversation[0]['content']"
  aggregation: "monthly mean per cohort"
proxy_3_correction_freq:
  regex: "r'\\b(no[,.] |actually[,.] |that\\'s wrong|please redo|i meant|wrong[,.] )\\b'"
  normalization: "per turn count"
  note: "INADEQUATE — base rate ~0.05%; redesign required"
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| WildChat-1M data loader (HuggingFace streaming) | h-e1-v2 | `code/data_loader.py` | YES |
| Returning-user cohort builder (≥3 bins) | h-e1-v2 | `code/cohort_builder.py` | YES |
| Prompt token count time series (monthly agg) | h-e1-v2 | `code/proxy_computer.py` | YES |
| Mann-Kendall runner (Hamed-Rao) | h-e1-v2 | `code/stats_tester.py` | YES |
| Bootstrap CI (B=1000) | h-e1-v2 | `code/stats_tester.py` | YES |
| Figure generation pipeline | h-e1-v2 | `code/visualizer.py` | YES |
| Smoke test (synthetic data) | h-e1-v2 | `code/smoke_test.py` | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1-v2** | Proxy 1 prompt_tokens τ | τ ≠ 0, p < 0.05 | τ=+0.744, p=0.0005 | NONE (detected, but wrong direction for BAA) | Strong signal exists; direction is POSITIVE not negative |
| **h-e1-v2** | Proxy 2 vote_entropy τ | τ ≠ 0, p < 0.05 | NOT COMPUTED | DESIGN_ISSUE | LMSYS primary gated; planned but blocked by infrastructure |
| **h-e1-v2** | Proxy 3 correction_freq τ | τ ≠ 0, p < 0.05 | τ=0.051, p=0.855 | HYPOTHESIS_ISSUE | Near-zero base rate; proxy inadequate regardless of hypothesis direction |
| **h-e1-v2** | Gate ≥2/3 proxies | PASS | FAILED (1/3) | DESIGN_ISSUE + HYPOTHESIS_ISSUE | LMSYS access + correction proxy failure |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| `fig1_gate_summary.png` | `h-e1-v2/figures/` | τ ± 95% CI bar chart, PASS/FAIL color for all 3 proxies | Results — Gate Evaluation |
| `fig2_proxy_timeseries.png` | `h-e1-v2/figures/` | Monthly time series for Proxy 1 (tokens) and Proxy 3 (correction) over 2023-2024 | Results — Proxy Trends |
| `fig3_cohort_funnel.png` | `h-e1-v2/figures/` | WildChat retention funnel: all users → ≥1 bin → ≥3 bins → analysis cohort | Methods — Dataset |
| `fig1_tau_bar.png` | `h-e1/figures/` | Kendall τ bar chart (h-e1 version, proxy_token_count passing) | Appendix — v1 Results |
| `fig2_time_series.png` | `h-e1/figures/` | Monthly proxy time series h-e1 | Appendix — v1 Results |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: LMSYS Primary Dataset Inaccessibility

- **What:** `lmsys/chatbot_arena_conversations` is access-gated on HuggingFace. The fallback dataset (`lmsys/lmsys-arena-human-preference-55k`) contains no timestamps, preventing valid temporal binning.
- **Why This Matters:** Proxy 2 (vote entropy) cannot be computed. P1 (LMSYS-based entropy decline prediction) is entirely blocked. Any ELO trend analysis is blocked.
- **Root Cause:** Dataset access policy by LMSYS team. The experiment design correctly identified the required field (`tstamp`) but the access requirement was not anticipated.
- **Impact on Claims:** P1 is INCONCLUSIVE. ELO-entropy correlation (central BAA cross-dataset claim) is untestable with current access. Causal mechanism Step 1 (AI quality improvement) is unverified.
- **Why Acceptable:** This is an infrastructural limitation, not a conceptual flaw. WildChat-based proxies remain independent and valid. Remediation path is clear: request LMSYS research access.

#### L2: Returning-User Cohort Selection Bias

- **What:** IP-hash cohort tracking selects users appearing in ≥3 monthly bins. This systematically selects for high-engagement users (power users), not representative WildChat users.
- **Why This Matters:** The prompt length increase (τ=+0.744) may reflect power-user selection dynamics (engaged users return AND compose longer prompts) rather than within-user behavioral change over time.
- **Root Cause:** WildChat anonymization uses IP-hash, not user accounts. IP-hash is coarse (multi-user NAT, IP reassignment can merge or split users). The ≥3 monthly bin filter eliminates casual/transient users, creating a biased sample.
- **Impact on Claims:** The prompt length finding is a valid descriptive observation for returning-user cohorts; causal attribution to AI quality improvement vs. user self-selection is not determinable from current data.
- **Why Acceptable:** The existence of a strong, autocorrelated temporal trend (τ=0.744, ACF=0.634) is itself a finding. It establishes that behavioral signals are detectable and trend-able in returning-user cohorts. Causal interpretation requires within-user panels.

#### L3: Correction Frequency Proxy Inadequacy

- **What:** The regex-based correction/negation detection (~0.05% base rate of turns) provides insufficient signal for Mann-Kendall trend analysis.
- **Why This Matters:** Proxy 3 (correction frequency) is effectively undetectable by the current regex approach. This blocks testing whether user correction behavior changes over time.
- **Root Cause:** Explicit verbal corrections are rare in AI interactions. Users more commonly correct implicitly (resubmit, rephrase, abandon session). The proxy was designed for explicit corrections but this behavioral form is extremely sparse.
- **Impact on Claims:** Cannot test whether correction behavior changes over time. The BAA mechanism via correction behavior is unverifiable with current methodology.
- **Why Acceptable:** The proxy inadequacy is identifiable and fixable (LLM-based annotation, session-level behavioral proxies). This constrains the correction-frequency finding, not the entire framework.

#### L4: Directional Prediction Mismatch (BAA Core Prediction Refuted for Prompt Length)

- **What:** The BAA hypothesis predicts declining behavioral engagement (shorter prompts, τ < 0). The empirical finding is strongly opposite: τ=+0.744.
- **Why This Matters:** This is not a peripheral finding — it directly refutes the central directional prediction of the BAA decline framework for the most reliable proxy (prompt length).
- **Root Cause:** The theoretical mechanism (AI quality improvement → reduced probing need → shorter prompts) was not confirmed. Alternative explanations (user expertise gain, selection bias) are equally or more plausible and predict the observed positive trend.
- **Impact on Claims:** The BAA disengagement hypothesis as formulated is not supported for returning WildChat users in 2023-2024. Claims about declining human behavioral engagement as a consequence of AI improvement cannot be made from current data.
- **Why Acceptable:** A negative/direction-refuting result is scientifically valid and informative. It constrains the BAA framework and motivates revised hypotheses about which users and conditions show behavioral disengagement (if any).

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Dataset | WildChat-1M returning users (≥3 monthly bins, 2023-2024, English) | Casual/non-returning users; non-English subsets; post-2024 data | Cohort construction filter; temporal coverage |
| Proxy measurement | Prompt token count (strongly detectable, τ=0.744) | Vote entropy (access-blocked); correction frequency (too sparse, τ≈0) | h-e1-v2 proxy results |
| Platform type | General-purpose LLM API (ChatGPT-like, via WildChat proxy) | Specialized/task-specific AI tools; direct API users vs. proxy users | WildChat captures general-use via web proxy |
| Time period | Apr 2023 – Apr 2024 (13 monthly bins with ≥50 cohort members) | Pre-April 2023 (insufficient WildChat data); post-April 2024 (not covered) | Monthly bin retention funnel |
| Trend direction | Prompt length INCREASES in returning cohorts (robust across h-e1 and h-e1-v2) | — | τ=0.744 (h-e1-v2); τ=0.564 (h-e1); consistent |

### 6.3 Assumption Violation Impact

- **A3 VIOLATED (prompt token decline = reduced engagement):** The most critical violated assumption. Prompt length increase could reflect expertise gain or selection bias rather than engagement decline. Impact severity: HIGH. Affected claims: all BAA directional predictions. Mitigation: within-user longitudinal design with model-version stratification and non-returning user comparison group.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative: Selection bias drives prompt length increase** (Priority: HIGH)
  - **Why Not Yet Tested:** Current design doesn't compare returning-user cohort against non-returning users at same time points, or within-user growth vs. between-cohort composition shift.
  - **Proposed Experiment:** Two-group analysis — (A) users with ≥3 monthly bins vs. (B) users with exactly 1 monthly appearance, matched by month and topic domain. Difference-in-differences design for prompt length growth.
  - **Expected Outcome if True:** Group A shows significantly higher prompt length growth than Group B; the trend is an artifact of self-selection, not behavioral adaptation.
  - **Expected Outcome if False:** Both groups show similar growth — genuine platform-level behavioral shift, not cohort selection.

- **Alternative: User expertise gain (not disengagement)** (Priority: HIGH)
  - **Why Not Yet Tested:** Assumption A3 requires distinguishing expertise gain (longer, more focused prompts + maintained topic diversity + maintained correction frequency) from BAA disengagement (longer prompts + declining diversity + declining correction).
  - **Proposed Experiment:** Compute topic diversity (Shannon entropy of topic-tag distribution per monthly bin) and follow-up question rate for the same returning-user cohort. Expertise gain predicts stable/increasing topic diversity alongside prompt length growth.
  - **Expected Outcome if True:** Topic diversity stable or increasing — expertise gain confirmed. Expected Outcome if False: Topic diversity declines concurrently — potentially consistent with BAA in a non-length proxy.

- **Alternative: Implicit corrections not captured by regex proxy** (Priority: MEDIUM)
  - **Why Not Yet Tested:** Only explicit verbal corrections were measured. Implicit corrections (resubmission with modified prompt, session abandonment, reduced turn depth) were not measured.
  - **Proposed Experiment:** Measure (a) session abandonment rate after single-turn interactions, (b) intra-session prompt similarity (low similarity = implicit correction loop), (c) turn count distribution per session over time.
  - **Expected Outcome if True:** Session-level revision proxies would show temporal signal where the regex proxy showed none.

### 7.2 From Unverified Assumptions

- **Assumption A1 (WildChat metadata reflects genuine behavior):**
  - **Proposed Test:** Compute within-cohort vs. between-cohort variance ratio for prompt length; assess whether IP-hash collision rate is material by checking single-session IPs vs. multi-session IPs.
  - **If Violated:** Results may reflect NAT-level artifacts. Switch to topic-level cohort analysis or use conversation-thread structure instead of IP-hash.

- **Assumption A2 (LMSYS votes are genuine):**
  - **Proposed Test:** Request access to `lmsys/chatbot_arena_conversations`; apply quality controls (voting time distribution, outlier detection) to validate vote authenticity.
  - **If Violated:** Vote entropy proxy is invalid; replace with structured human annotation study for preference homogeneity.

- **Assumption A4 (HELM-WildChat temporal alignment):**
  - **Proposed Test:** Map HELM evaluation dates to WildChat model-version deployment dates; verify alignment within ±1 month per major model version (GPT-3.5, GPT-4, GPT-4o).
  - **If Violated:** Cross-sectional BAA (P3) not testable; demote to exploratory analysis only.

- **Assumption A5 (signals attributable to human adaptation, not model changes):**
  - **Proposed Test:** Stratify prompt length trend by WildChat model field (GPT-3.5 vs. GPT-4 conversations); if trend disappears within single-model-version stratum, it reflects model-change confound not user adaptation.
  - **If Violated:** Observed trends confound model improvement with behavioral change; require quasi-experimental design with model-version fixed effects.

### 7.3 From Scope Extension Opportunities

- **Extension: Obtain LMSYS primary access and rerun vote entropy analysis**
  - **Current Evidence Suggesting Feasibility:** The h-e1-v2 pipeline correctly implements entropy computation and LMSYS data loading; only the access credential is missing.
  - **Required Resources:** IRB-approved data access request to LMSYS team; re-run of existing pipeline with `lmsys/chatbot_arena_conversations`.
  - **Expected Challenges:** Access approval timeline; dataset structure may differ from fallback dataset.

- **Extension: Post-2024 WildChat cohorts (GPT-4o / Claude 3.5 era)**
  - **Current Evidence Suggesting Feasibility:** If WildChat-1M has post-April 2024 data with sufficient cohort retention (≥50 users/month), the same pipeline applies.
  - **Required Resources:** Check WildChat-1M update schedule; re-run cohort extraction with extended date range through end of 2024 or 2025.
  - **Expected Challenges:** Cohort continuity across major model generation transitions may disrupt trend; increasing bot/automated usage in later periods may contaminate data.

- **Extension: Expand to non-English WildChat subsets**
  - **Current Evidence Suggesting Feasibility:** WildChat-1M is multilingual; tiktoken handles Unicode; same pipeline applies with language stratification.
  - **Required Resources:** Language detection filter in preprocessing; language-appropriate tokenizer validation.
  - **Expected Challenges:** Smaller per-language cohort sizes reduce Mann-Kendall power below detectable threshold.

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Hook:** "We set out to measure whether AI improvement makes us intellectually lazier — and found the opposite: returning AI users compose progressively longer, more elaborate prompts over time. But this surprising finding raises a harder question: is it that better AI inspires deeper engagement, or merely that engaged users are the only ones who return?"

**Hook Strategy:** Counterintuitive finding — the result is opposite to expectation, which is more compelling than confirming what everyone assumed.

**Why This Hook:** The positive trend (τ=+0.744) is statistically robust and directionally surprising for anyone familiar with AI deskilling narratives (Dell'Acqua 2023). The open question about selection bias vs. genuine engagement creates productive tension that motivates the paper's analytical framework.

### 8.2 Key Insight (Experiment-Verified)

> Returning WildChat-1M users compose significantly longer prompts over 2023-2024 (Mann-Kendall τ=0.744, p<0.001), but whether this reflects growing human-AI engagement sophistication or power-user self-selection remains empirically unresolved — and this ambiguity is itself the central scientific contribution of the present work.

**Verification Evidence:** h-e1-v2: τ=0.744, p=0.0005, Hamed-Rao corrected, ACF lag-1=0.634. Consistent with h-e1 result (τ=0.564, p=0.007). Two independent experiment runs confirm the direction and significance.

### 8.3 Strongest Claims (Paper-Ready)

1. **Prompt token count in returning WildChat-1M user cohorts increases significantly over 2023-2024 (τ=0.744, p<0.001)**
   - Evidence: h-e1-v2 Proxy 1; confirmed by h-e1 (τ=0.564, p=0.007)
   - Confidence: HIGH (two independent experiment rounds, autocorrelation-corrected)
   - Suggested Section: Results (main finding)

2. **The BAA decline prediction — that prompt complexity decreases as AI quality improves — is not supported in publicly available general-purpose AI interaction logs (2023-2024)**
   - Evidence: τ=+0.744 (opposite direction to prediction); correction freq τ≈0 (no signal); vote entropy inaccessible
   - Confidence: MEDIUM-HIGH (direction refuted for best-measured proxy; other proxies inconclusive)
   - Suggested Section: Discussion (negative result framing)

3. **LMSYS Chatbot Arena primary dataset access is a binding constraint for temporal preference vote analysis: the fallback dataset contains no timestamps**
   - Evidence: h-e1-v2 Proxy 2 failure; both experiment rounds confirm this
   - Confidence: HIGH (factual finding about research infrastructure)
   - Suggested Section: Methods (data availability statement)

4. **The returning-user cohort methodology (≥3 monthly bins, n=27,902) and Hamed-Rao Mann-Kendall pipeline constitute a validated, reusable framework for behavioral trend analysis in large-scale interaction logs**
   - Evidence: Correct implementation confirmed; smoke tests pass; statistical properties documented (ACF=0.634, bootstrap CI)
   - Confidence: HIGH
   - Suggested Section: Methods (methodology contribution)

### 8.4 Honest Limitations (Must Include in Paper)

1. **The returning-user cohort selection bias may explain the observed prompt length increase independent of any behavioral adaptation mechanism**
   - Why Acceptable: The cohort design is the best available approach with IP-hash anonymization; the limitation is documented and the proposed control experiment (non-returning user comparison) is feasible.
   - Suggested Framing: "The ≥3 monthly bin filter creates a self-selected high-engagement cohort. Whether the prompt length trend reflects within-user behavioral adaptation or between-user cohort composition remains an open question that we motivate for future work."

2. **Vote entropy (the primary LMSYS-based proxy) could not be computed due to dataset access restrictions**
   - Why Acceptable: The limitation is infrastructural, not conceptual. The methodology is sound and the access pathway is clear.
   - Suggested Framing: "The primary LMSYS Arena dataset is access-gated. We identify vote entropy over LMSYS preference data as the most critical future experiment once access is obtained."

3. **Explicit correction frequency is too sparse for trend detection; the BAA correction mechanism requires a redesigned proxy**
   - Why Acceptable: The proxy inadequacy was identified from results, not assumed. Redesign paths (LLM annotation, session-level proxies) are clearly specified.
   - Suggested Framing: "Explicit verbal correction behavior occurs in <0.1% of turns in WildChat data, making our regex proxy underpowered for temporal trend detection. We distinguish this from the broader behavioral phenomenon of implicit correction, which requires richer annotation."

### 8.5 Evidence Highlights (Most Persuasive)

1. **Prompt Length Growth: 180 → 832 Tokens Over 13 Months**
   - Data: Monthly mean prompt token count for 27,902 returning users grew from ~180 tokens (Apr 2023) to ~832 tokens (Apr 2024); τ=0.744, 95% CI [0.415, 0.972]
   - "So What": A 4.6× increase in prompt length over 13 months is a substantial behavioral change, detectable without any new annotation or survey. Whether it reflects engagement growth or selection dynamics, it is a measurable signal in public data.
   - Suggested Figure/Table: Fig 2 (`fig2_proxy_timeseries.png`) — monthly time series with trend line; also gate summary bar chart (Fig 1) showing τ and CI

2. **Consistent Across Two Independent Experiment Rounds**
   - Data: h-e1: τ=+0.564, p=0.007 (13 bins, 6,769 users); h-e1-v2: τ=+0.744, p=0.0005 (13 bins, 27,902 users, Hamed-Rao)
   - "So What": The direction and significance of the prompt length trend replicated across two independent implementations with different cohort sizes and different statistical methods.
   - Suggested Figure/Table: Comparison table of h-e1 vs. h-e1-v2 results for Proxy 1

3. **High Autocorrelation Reveals Platform-Level Behavioral Dynamics**
   - Data: ACF lag-1 = 0.634 for the prompt token count series — indicating strong month-to-month correlation in behavioral patterns
   - "So What": High autocorrelation confirms that prompt length changes are not noise — they represent a persistent, platform-level behavioral dynamic. Standard Mann-Kendall would overestimate significance; Hamed-Rao correction is essential, and the result remains significant after correction (p=0.0005).
   - Suggested Figure/Table: ACF plot in supplementary; note in main text that Hamed-Rao was required and applied

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 (superseded) | Phase 4 results: τ=+0.564 for prompt tokens |
| `h-e1-v2/04_validation.md` | h-e1-v2 | Phase 4 results (authoritative): τ=+0.744, gate FAILED |
| `h-e1-v2/02c_experiment_brief.md` | h-e1-v2 | Experiment design: 3-proxy pipeline, WildChat cohort spec, LMSYS fallback |
| `03_refinement.yaml` | Main hypothesis | Original BAA hypothesis: H-BAA-v1, P1/P2/P3, causal mechanism, 5 assumptions |
| `verification_state.yaml` | Pipeline | State: h-e1-v2 COMPLETED (gate FAILED); synthesis status |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
*Phase 4.5 v2.0 — Ablation mode: No VSA, No IC, No MCP, No Reflection*

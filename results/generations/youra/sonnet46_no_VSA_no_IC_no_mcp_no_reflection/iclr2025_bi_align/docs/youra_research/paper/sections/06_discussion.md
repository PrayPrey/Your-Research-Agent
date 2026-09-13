# Discussion

## Key Findings

Our experiments produce three findings that together define the current empirical boundary of the BAA framework:

**Finding 1: Behavioral proxy signals are detectable in returning-user cohorts, but in the wrong direction for BAA disengagement.** The prompt token count trend is strong (τ = +0.744), statistically significant, and consistent across two experiment rounds. This establishes that behavioral engagement signals ARE computationally accessible from public interaction logs without new annotation. But the positive direction — growing prompt complexity, not declining — means the signal contradicts the BAA disengagement prediction rather than confirming it. The methodology works; the hypothesis does not.

**Finding 2: Two of three proxies are unmeasurable under current conditions.** Vote entropy (Proxy 2) is blocked by dataset access; correction frequency (Proxy 3) has too sparse a signal for trend detection. This is not a minor technical inconvenience — it means the BAA directional prediction can currently be tested on only one proxy, and that proxy shows the opposite trend. The measurement infrastructure gap is a first-class scientific constraint that any future BAA study must address explicitly.

**Finding 3: The returning-user cohort design introduces a selection bias that prevents causal attribution.** The ≥3 monthly bin filter is necessary for longitudinal signal detection but systematically retains high-engagement users. Whether the positive prompt length trend reflects within-user behavioral adaptation (users genuinely engaging more deeply over time) or between-user composition (engaged users self-select into returning cohorts) cannot be determined from current data.

## Why Is Prompt Length Increasing?

The observed τ = +0.744 is robust and reproducible. Three competing explanations predict increasing prompt length, all independent of AI quality improvement:

**Explanation 1: Selection bias (most plausible).** The ≥3 monthly bin filter selects power users — individuals who consistently return to an AI platform over multiple months are, by definition, high-engagement users. High-engagement users plausibly compose longer, more elaborate prompts than one-time users, not because of AI quality improvement but because of their baseline behavioral profile. The positive trend within this cohort may reflect the increasing dominance of heavy users over time as casual users drop off.

**Explanation 2: User expertise gain (also plausible).** Users who return to an AI tool learn to compose more effective prompts over time — longer, more context-rich, more precisely scoped. This expertise gain predicts increasing prompt length regardless of AI quality improvement. Dell'Acqua et al.'s (2023) deskilling evidence applies to task assignment, not to prompting behavior; expertise gain in prompting is not merely plausible but expected.

**Explanation 3: Platform adoption effect (moderate plausibility).** WildChat's user base shifted over 2023–2024 toward more professional and developer use, which involves longer, more technical prompts. If the returning-user cohort's composition shifted toward professional users over this period, the trend would reflect a platform demographic shift, not individual behavioral adaptation.

The BAA disengagement mechanism (AI improvement reduces probing need → shorter prompts) requires that we observe decreasing prompt length in a population where AI quality is improving. We observe the opposite. Both selection bias and expertise gain offer more parsimonious explanations for the positive trend than a reversed-BAA mechanism. We cannot assign probabilities across these explanations from current data; we describe the comparison experiment that would distinguish them in Section 7.

## Limitations

**L1: Returning-user selection bias (severity: HIGH).** The ≥3 monthly bin filter is the paper's most significant limitation. The analysis cohort (n = 27,902) represents a self-selected high-engagement fraction of the full WildChat user population. Whether the behavioral trends we observe generalize to all AI users, or only to this engaged subset, is empirically open. The proposed control experiment — comparing returning-user cohort against a matched non-returning sample at the same time points — is the most critical follow-up.

The ≥3 bin filter was chosen to ensure sufficient longitudinal data per user for trend detection; this choice is methodologically defensible for the purpose of *detecting* behavioral trends. But it renders causal attribution unavailable. We accept this as the principal limitation and state it explicitly rather than discounting it.

**L2: LMSYS primary dataset access (severity: HIGH for P2).** The vote entropy proxy — arguably the most direct operationalization of the BAA disengagement prediction, since declining vote discriminativeness would indicate users engaging less critically with AI output quality — is entirely blocked by data access. This is an infrastructural constraint, not a methodological one. The entropy computation is correct; the data is inaccessible. Any future BAA study must resolve this before claiming a comprehensive test of the framework.

**L3: Correction frequency proxy inadequacy (severity: MEDIUM).** The regex-based correction proxy captures a specific behavioral form (explicit verbal corrections) that appears to be extremely rare in naturalistic AI interaction. Implicit corrections — rephrasing, session abandonment, resubmission with modified prompt — are likely more common but require different measurement approaches. The near-zero signal level means we cannot distinguish "no behavioral trend" from "behavioral trend not captured by this proxy."

**L4: No causal chain verification (severity: MEDIUM).** The BAA causal mechanism requires: (1) AI quality improvement is detectable in the data, (2) quality improvement reduces users' probing behavior, (3) reduced probing manifests as specific behavioral signals. We verify none of these steps. LMSYS ELO trends are uncomputed (dataset gated). The correction mechanism is partially falsified (near-zero signal). The prompt trend is the opposite of the mechanism's prediction. We treat the negative result as informative about the empirical feasibility of the BAA disengagement mechanism, not as a logical refutation of BAA as a theoretical framework.

**L5: 13-bin analysis window (severity: LOW).** The planned 24-bin window (January 2023 – December 2024) was reduced to 13 bins (April 2023 – April 2024) by the cohort-size floor. Shorter time series reduce Mann-Kendall power. The Proxy 1 effect is large enough (τ = 0.744) that power is not a concern for that proxy; for Proxy 3, the 13-bin window compounds the near-zero signal problem.

## Implications for the BAA Framework

The BAA framework as originally stated — that AI improvement causes measurable behavioral disengagement in returning users — is not empirically supported by current public data. This is a constrained negative result, not a conclusive refutation: the framework may still be valid for casual/non-returning users, under different measurement conditions, or over different time periods.

What the current work establishes is that the framework requires substantially more sophisticated measurement infrastructure than currently available in public datasets. Specifically:

1. A non-returning user comparison group is needed to control for self-selection.
2. LMSYS primary access is needed for vote entropy analysis.
3. Implicit correction proxies (session-level, LLM-annotated) are needed for the correction mechanism.
4. Within-user vs. between-cohort variance decomposition is needed to distinguish adaptation from composition effects.

Until these conditions are met, the BAA directional prediction remains empirically untested in the required conditions — and the positive prompt length trend we observe is equally consistent with a reversed BAA (better AI enables more complex prompts) as with selection bias. The ambiguity is not a failure; it is the precise empirical state of the question after our experiments.

## Broader Impact

This work develops methods for longitudinal behavioral analysis in large-scale AI interaction logs. The analysis pipeline (returning-user cohort construction, Hamed-Rao Mann-Kendall, bootstrap CI) is applicable to any dataset with IP-hash or user-level pseudonymization and temporal coverage. Positive applications include monitoring behavioral engagement trends across model generations, detecting platform-level deskilling, and providing empirical grounding for AI deployment policy discussions.

A potential concern is that the methodology could be misused to monitor individual user behavior over time, even with pseudonymization. The IP-hash approach used by WildChat does not enable re-identification, and our analysis operates exclusively at the cohort aggregate level. We do not access, store, or analyze individual-level conversation content beyond tokenization.

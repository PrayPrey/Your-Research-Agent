# Failure Record: h-e1 Run 1

## Metadata
- **Hypothesis**: h-e1
- **Phase**: Phase 4
- **failure_type**: MUST_WORK_FAIL
- **gate_result**: FAIL
- **timestamp**: 2026-03-15T01:00:00Z
- **modification_attempt**: 0

## Gate Metrics
- **d_human_mean**: 0.0362 (required: [0.1, 0.4]) — too small
- **d_human_ci_lower**: -0.187 (CI includes zero — no reliable directional effect)
- **jt_wc_p**: 0.0 (trend exists but negligible effect)
- **jt_hr_p**: 0.0 (trend exists but negligible effect)
- **median_base_wc**: 14.0, **median_rs_wc**: 14.0, **median_online_wc**: 15.0
- **median_base_hr**: 0.917, **median_rs_hr**: 0.900, **median_online_hr**: 0.880

## Failed Checks
- d_human_in_range: 0.036 < 0.1
- d_human_ci_positive: CI lower = -0.187
- monotonic_wordcount: base=14.0, rs=14.0, online=15.0 (not strictly monotonic)
- monotonic_hapax: base=0.917, rs=0.900, online=0.880 (reversed — anti-monotonic)

## Root Causes
- Effect exists (J-T p≈0) but is negligible (d=0.036); the trend is statistically detectable but practically meaningless
- hapax_ratio is anti-monotonic across tiers — hypothesis direction was wrong for this feature
- word_count shows near-zero stratification (median differences of 0-1 words)
- Methodology doesn't produce required effect size with this feature set at N=89244
- RLHF tier structure doesn't co-vary strongly enough with human linguistic register for d∈[0.1,0.4]

## Lessons Learned
- Ordinal stratification of simple lexical features (word_count, hapax_ratio) produces statistically significant but negligibly small effects at N=89244
- RLHF tier structure doesn't co-vary strongly enough with human linguistic register for d∈[0.1,0.4]
- CI including zero means no reliable directional effect exists despite J-T significance
- Anti-monotonic hapax means the hypothesis direction was wrong for that feature (more advanced tiers have LOWER hapax ratio, not higher)
- Large N inflates statistical power: J-T p=0 with d=0.036 is a reminder that significance ≠ effect size
- Simple lexical features are insufficient to capture RLHF alignment signal in human turns

## Routing Decision
- **Route**: Phase 0 (fundamental flaw — methodology doesn't work)
- **Reason**: MUST_WORK gate FAILED — d_human_mean=0.036 below [0.1,0.4]; methodology doesn't produce required effect size
- **Next Action**: Restart from Phase 0 with new research question

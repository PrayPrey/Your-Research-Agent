# Adversarial Review Round 1

## Summary
Paper demonstrates linear probes on middle-layer hidden states achieve 0.885 AUROC for factual correctness prediction, exceeding token entropy by +26 points with single-pass efficiency. Core claims verified against ground truth; minor presentation issues noted.

## Accuracy Checker Findings
### FATAL Issues (must fix or withdraw)
None

### MAJOR Issues (must fix with evidence)
- **R1-001**: Paper reports probe AUROC as "0.885" in abstract/results but Table 1 shows L15 = 0.852. These are different experiments (L15 layer sweep vs overall probe), but the paper conflates them. Clarify that 0.885 is the final trained probe result while 0.852 is the layer sweep intermediate result.

All other numerical claims verified:
- Probe AUROC 0.885: matches Q1
- Token entropy 0.623: matches Q2
- Sequence NLL 0.589: matches Q3
- Delta +26.2 pts: matches Q4 (0.262)
- Peak L15 at 50% depth: matches Q5, Q6
- L18=0.822, L31=0.766: matches Q7, Q8
- Hook overhead <5%: ground truth says -3.4%, paper says "<5%" (conservative, acceptable)
- Training 9500, val 1700: matches Q10, Q11

## Bored Reviewer Findings
- Abstract compelling: YES - opens with real problem, quantifies gap, delivers strong result
- Problem clear in 1 min: YES - three-level framing (surface/deeper/gap) is crisp
- Novelty clear in 2 min: YES - "hidden states for correctness, not uncertainty" distinction made early
- Attention lost at: never - 8-page scope, focused narrative
- Would continue reading: YES

## Skeptical Expert Findings
### Novelty Concerns
1. Probing hidden states is prior art (Burns 2023, Kossen 2024). Paper cites these but the delta ("correctness vs uncertainty") is incremental. Framing should be "we apply existing probing to a different target" not "we propose probing."
2. Middle-layer optimality (50-60% depth) is known from Aiersilan 2026 and logit lens work. The inverted-U pattern is confirmation, not discovery.

### Baseline Fairness
Baselines are weak: token entropy (0.62) and sequence NLL (0.59) are strawmen. Semantic entropy (~0.80) is the real competitor. Paper claims "matching semantic entropy" but actually EXCEEDS it (0.885 vs ~0.80). This is underselling, not overclaiming.

Missing baselines:
- Semantic Entropy Probes (Kossen 2024) directly comparable
- Self-consistency sampling
- Verbalized confidence

### Overclaims
None - paper is appropriately conservative

### Missing Limitations
1. Dataset scope: Only TriviaQA tested despite mentioning Natural Questions in blueprint
2. Exact-match labeling acknowledged but underweighted (major confounder)
3. No cross-distribution analysis (easy vs hard questions)
4. P4, P5, P6 predictions mentioned in ground truth as "untested" - paper silent on this

### Recommendation
**WEAK_ACCEPT** - Solid empirical work with verified results. Incremental novelty over SEP but clear practical value. Needs baseline expansion and clearer positioning.

## Issues Summary
| ID | Severity | Category | Description | Action Required |
|----|----------|----------|-------------|-----------------|
| R1-001 | MAJOR | Consistency | 0.885 (probe) vs 0.852 (L15 sweep) conflated | Clarify these are different measurements in text |
| R1-002 | MINOR | Novelty | "We propose" framing overstates contribution | Reframe as "we apply...to correctness prediction" |
| R1-003 | MINOR | Baselines | Missing SEP/self-consistency comparisons | Add to limitations or run experiment |
| R1-004 | MINOR | Scope | Only TriviaQA despite blueprint listing NQ | Acknowledge single-dataset in limitations |

## Human Review Notes (MINOR only)
- Line 58: "Aiersilan et al. (2026)" - future date suggests synthetic citation or typo
- Line 91: "~60 iterations" - tilde unnecessary when 60 is the verified value
- Section 3.2 mentions "<5% runtime overhead" but ground truth shows -3.4% (negative = faster?). If hooks make it faster, that's worth noting explicitly
- Abstract uses "~0.62 AUROC" but ground truth shows exact 0.623 - prefer exact value

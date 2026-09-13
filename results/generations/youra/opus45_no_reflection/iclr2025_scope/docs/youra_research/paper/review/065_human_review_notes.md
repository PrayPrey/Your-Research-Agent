# Human Review Notes - Round 1 Minor Issues

## From Accuracy Checker
- Line 198: 95% CI brackets lack source data
- Line 182: H-M3 gate "MUST_WORK" but result FAIL - table design inconsistency
- Abstract says "5x" but text alternates "5x"/"5.0x" - pick one
- Line 227: "p=0.881" should clarify NO effect, not weak effect
- Missing exact sample sizes confirmation (says 500 but not in results)

## From Bored Reviewer
- Section 6.2 limitations dump feels defensive
- Future work (Section 7) is generic
- No intuitive explanation of WHY position-agnostic supervision helps

## From Skeptical Expert
- "Bounded vs unbounded" language in 5.3 is strong for 2x ratio over 4 points
- References incomplete ("See 06_references.bib" not acceptable for submission)

## From Round 2 (Numerical Verification)
- Line 219: "middle layers (12, 16) exhibit greatest divergence" unsupported by data - all layers show identical values
- Abstract/Conclusion: 5x claim measured on simulated students, not actual distilled models - consider "in PoC simulations" qualifier

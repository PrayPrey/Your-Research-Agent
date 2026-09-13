# Human Review Notes
> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI — they require human judgment.

**Generated:** 2026-03-23
**Rounds Completed:** 2 (R1, R2)
**Paper Version:** 06_paper_r2.md (final after review)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 4 |
| Style | 1 |
| Grammar | 1 |
| Typo/Formatting | 0 |
| **Total** | **6** |

---

## Round 1 Issues

### Clarity
1. **§5.2 Narrative text ECE rounding:** Text says "ECE(hard)=0.657" and "ECE(easy)=0.359" for DeepSeek, but Table 1 shows 0.6565 and 0.3586. Minor rounding inconsistency — text rounds to 3 significant digits, table shows 4. Consider making consistent (either round table to 3 sig figs or update text to 4).

2. **§5.5 M-stability — "exactly stable" unexplained:** The claim "ΔECE values are exactly stable across M ∈ {10, 15, 20}" with identical 5-decimal values will confuse readers. Add 1–2 sentences explaining why: confidence distributions are broadly spread across the confidence space, so different M values partition data into bins with similar contents. The stability is a property of the distribution, not of the ECE estimator per se.

3. **§3.1 k=5 discrete values:** "six discrete pass@1 values {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}" — correct, but adding "k=5 yields" at the start clarifies the connection to the design choice (k=5 → 6 possible values).

### Style
4. **Abstract: "practitioners typically assume"** — uncited. Consider softening to "It is commonly assumed..." or add a citation to a practitioner paper or survey (e.g., Liu et al., 2025 survey).

### Grammar
5. **§5.3: "MBPP-only"** should be "MBPP+-only" or "MBPP+ only" for consistency with the rest of the paper which uses the EvalPlus benchmark name "MBPP+".

---

## Round 2 Issues

### Clarity
6. **§4.2 Null baseline description:** The paper describes the null as a "Monte Carlo Bernoulli null model: draw confidence from the model's empirical c distribution; assign correctness independently." The h-m4 validation notes it slightly differently ("null baseline uses constant confidence = tier accuracy"). The Figure 6 description should clarify which null is plotted — is it (a) random confidence from empirical distribution, (b) constant confidence = accuracy, or (c) something else? A one-sentence clarification would preempt reviewer questions.

---

## Recommended Priority

1. **Fix First (High Visibility):** §5.2 ECE rounding consistency (Clarity-1) — reviewers often check whether text matches table
2. **Fix Second:** §5.5 M-stability explanation (Clarity-2) — a knowledgeable reviewer will ask why the values are identical
3. **Fix Third:** §4.2 Null baseline clarification (Clarity-6) — reviewers of calibration papers expect precise null definitions
4. **Consider:** §3.1 k=5 clarification (Clarity-3) and abstract citation (Style-4)
5. **Optional:** §5.3 MBPP+ naming (Grammar-5) — minor but consistent style

---

*Note: These issues do not block paper acceptance but would improve quality and reviewer experience.*
*Auto-fix in adversarial review: NOT performed (v2.0 protocol — all MINOR issues for human review).*

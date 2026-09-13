# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human final polish.
> These issues are NOT auto-fixed by the Revision Agent.

**Date:** 2026-08-27T08:00:00+00:00
**Rounds Completed:** 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 4 |
| Clarity | 5 |
| Formatting | 1 |
| **Total** | **10** |

---

## Round 1 Issues

### Style

1. **§5.1** — "The macro-average of 8.75% is additionally consistent with..." — "additionally consistent" is awkward phrasing. Suggested: "The macro-average of 8.75% is also consistent with..."

2. **§3.3** — "Step 5 is where the failure occurs." — Sentence fragment, stylistically weak as a standalone sentence. Suggested: "Step 5 — cache reconstruction — is where the failure occurs."

3. **Abstract** — "making direct comparison impossible" → consider "making direct comparison infeasible" (stronger and more precise for the technical context).

### Clarity

4. **§6.2 L2** — "F1 > 20 was expressed in percentage scale" — Reader unfamiliar with the original sanity check may not know what "F1 > 20" refers to without prior context. Consider adding a brief parenthetical: "(i.e., the check expected F1 > 20%, but code reported raw scale)."

5. **§2.1** — "It serves as a lower-bound reference for query-aware methods." — Changed from original "lower-bound baseline" to "lower-bound reference" in R1 revision. Verify this is the correct intended meaning.

6. **§4.3 Table** — "Not executed" for M2/M6 Status — original paper said "Not reached." R1 changed to "Not executed." Both are acceptable; "Not executed (experiment terminated)" would be most precise.

7. **§3.1** (R1 text) — "Our experimental framework isolates the effect of token importance metric type on KV eviction performance via a unified codebase with a pluggable score_fn interface, so all metric conditions share identical..." — Long sentence. Consider splitting: "Our experimental framework isolates the effect of token importance metric type on KV eviction performance. The framework uses a unified codebase with a pluggable score_fn interface, ensuring all metric conditions share identical..."

---

## Round 2 Issues

### Clarity

8. **§4 header** — The F1 scale note ("F1 scale: All F1 values in this paper are reported as percentages...") appears before the RQs, which is slightly awkward placement. Consider moving to §4.4 Implementation Details where other measurement conventions are documented.

9. **Pre-Submission Checklist** — This section heading is not standard for an ICML submission body. Should be removed from the submitted paper or moved to an internal appendix/draft notes section.

### Style

10. **§5.1** — "below-state-of-the-art F1 is expected and does not indicate a pipeline error" — Slightly defensive phrasing. Consider: "lower than full-context F1 is expected due to 4K context truncation, where most relevant context for multi-hop QA exceeds the window."

### Formatting

11. **§3.3** — Fenced code block with Python syntax has no language tag (`python`). Add ` ```python ` instead of ` ``` ` for proper rendering.

---

## Recommended Priority

1. **Fix First:** §3.3 code block language tag (formatting — trivial fix)
2. **Fix Second:** Pre-Submission Checklist section heading (remove from submitted paper)
3. **Consider:** §4 F1 scale note placement (move to §4.4)
4. **Optional:** Style improvements in §5.1, §3.3, Abstract (subjective)

---

*Note: These issues do not block paper acceptance. All FATAL and MAJOR issues were resolved in Round 1. The paper is ready for pre-submission formatting pass and citation verification.*

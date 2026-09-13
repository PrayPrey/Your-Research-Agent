# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review (R1 + R2) for human final polish.
> These are NOT auto-fixed. Review before camera-ready submission.

**Date:** 2026-08-03
**Rounds Completed:** 2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 7 |
| Style | 2 |
| Formatting | 2 |
| Typo | 0 |
| Grammar | 0 |
| **Total** | **11** |

---

## Round 1 Issues

### Clarity

1. **§3.4 vs §6.2 — Pre/post breakdown not stated explicitly.**
   "Precondition checks" in §3.4 but "postcondition-only analysis" mentioned in L4. What is the actual fraction of pre- vs. postconditions in ContractEval? State explicitly in §3.2 or §3.4 (e.g., "ContractEval contracts are precondition-dominated: X% are input validity checks, Y% are postcondition assertions").

2. **§3.6 Tier 2 interpretation — assertion not demonstrated.**
   "Tier 2 BoolOp contracts function primarily as strict input guards" — this explains the non-monotonic tier gradient but is asserted without evidence. Add one linking sentence: e.g., "ContractEval's Tier 2 contracts use `and` to chain input validity conditions (e.g., `assert len(x) > 0 and x[0] >= 0`), which fire on nearly any CVT input; postcondition BoolOp chaining is less common."

3. **§4.1 Table — Exp B triples vs Exp A triples discrepancy.**
   Table shows Exp A: 10,432 triples and Exp B: 17,226 triples. The reader may wonder why Exp B (which required compatibility wrapping) has more triples than Exp A. Add a footnote: "Exp A completed 3 of 5 model families; Exp B completed all 5 families (94.6% compatibility rate)."

4. **§5.2 — "257/354 tasks" denominator unexplained.**
   The denominator 354 (not 364) appears without explanation. Add a parenthetical: "257/354 tasks with valid Experiment B triples (354/364; 10 tasks excluded due to PBT compatibility)."

5. **§5 Summary table — h-e1 max-gap 0.471 source unclear.**
   "mean max gap 0.471" is cited but the ground truth YAML does not contain this value. Either add it to 065_ground_truth.yaml or soften to "individual task gaps up to ~0.47."

6. **§3.3 — CodeLlama-34b Experiment A partial coverage.**
   Per h-m1/04_validation.md, CodeLlama-34b completed 317/364 tasks in Experiment A (not 364). Consider a table footnote: "CodeLlama-34b: 317/364 tasks completed in Exp A."

7. **§2.2 — Bose annotation clarification.**
   Table 2.4 lists Bose's annotation as "Manual" — but §2.2 text says "uses no formal contract annotations." Clarify: Bose uses manually authored property specifications, not benchmark-provided formal pre/postconditions. A parenthetical in the table: "Manual (researcher-authored, not benchmark contracts)" would eliminate ambiguity.

### Style

1. **§5.2 — "Most striking result" superlative.**
   "The 0.004 range across 5 models — spanning 7–34B parameters and open/closed architectures — is the most striking result of Experiment B." The oracle-isolation gap of 0.40 is the paper's headline finding; calling a secondary result "most striking" creates emphasis confusion. Suggest: "is the most notable pattern in Experiment B."

2. **§1 Contribution 1 — "clean" is informal.**
   "first clean methodology" — prefer "first controlled methodology" or "first confound-free methodology."

### Formatting

1. **Frontmatter word count discrepancy.**
   `word_count: ~6200` in header vs `total: ~4950 (body text)` in paper statistics block. Reconcile for camera ready (body text ~4950 is the correct figure for ICML page limit calculations).

2. **§1 Contributions — mixed em-dash and period formatting.**
   Contributions use bold lead term + em-dash bullet style; the body sometimes mixes periods and dashes. Standardize for consistency.

---

## Round 2 Issues

### Clarity

1. (See R1 Clarity item 3 above — now partially addressed by R2 fix to §3.3 LLM Corpus, which notes Exp A coverage.)

---

## Recommended Priority

1. **Fix First (high visibility):** §4.1 table footnote for triple counts (prevents immediate reviewer confusion); §5.2 denominator explanation.
2. **Fix Second:** Bose annotation clarification in Table 2.4; Tier 2 mechanism explanation.
3. **Consider:** Style items (superlative in §5.2; "clean" in Contribution 1).
4. **Optional:** Frontmatter word count reconciliation; formatting standardization.

---

*Note: These issues do not block paper acceptance but improve overall quality and precision.*

# Phase 6.5 Human Review Notes

These are MINOR issues collected during adversarial review. They were not auto-applied because they involve style, structural, or resource-dependent decisions that require human judgment.

---

## MINOR-1: Table 1 column inconsistency between section file and main paper

- **Section file** (`05_results.md`): Table 1 has both raw F1 and % columns.
- **Main paper** (`06_paper.md`): Table 1 has only raw F1 column.
- **Recommendation:** Choose one format and apply consistently across both files. Dual columns (raw + %) are clearer for readers unfamiliar with LongBench's raw-scale reporting — prefer this for submission.

---

## MINOR-2: No figures — paper structurally weaker

- **Issue:** Paper has 0 figures. For a paper about a diagnostic failure chain (✓✓✓✗ with F1 values), a single figure would immediately communicate the finding visually.
- **Recommendation:** For the corrected rerun, generate:
  1. Pipeline diagram with ✓/✗ annotations at each step (M0 end-to-end, score_fn, KV shape, DynamicCache, generation).
  2. M0 per-task F1 bar chart (4 tasks, reference line at 8.75%).
  3. M1 vs M0 comparison (bar chart showing 0.00 vs 0.09/0.09/0.11).
- These can be generated from existing data without rerunning experiments.

---

## MINOR-3: No qualitative output examples in §5.3

- **Issue:** §5.3 describes M1 outputs as "empty strings or single-token repetitions" but provides no concrete example. One sentence pair (M0 answer: "The telephone was invented by Alexander Graham Bell in 1876." vs M1 answer: "[empty]" or "...............") would make the degeneration viscerally concrete.
- **Recommendation:** Add 1 example pair (M0 output snippet + M1 output snippet for the same question) from experiment logs, if available.

---

## MINOR-4: No per-task confidence intervals on M0

- **Issue:** M0 per-task F1 values are point estimates from 100 examples each. No confidence intervals reported. The gate criterion requires a 2pp difference — at this baseline (8.75%), a 95% CI on 100 examples has non-trivial width.
- **Recommendation:** For the corrected rerun (M1 vs M2 comparison), compute bootstrap 95% CIs. For the M0 baseline alone (current paper), note in §5.1 that CIs were planned for the gate criterion evaluation and will be reported in the corrected experiment.

---

## MINOR-5: Page count ~11 exceeds ICML 8-page limit

- **Issue:** Estimated ~11 text pages; ICML limit is 8 (+ references). Approximately 3 pages need to be cut before submission.
- **Recommended cuts (in priority order):**
  1. §3.1 framework list (bulleted component list) — can be condensed to 2 sentences citing the codebase structure: ~0.5 page saved.
  2. §2.4 "Why Prior Work Does Not Encounter..." — now strengthened with affirmative value; can trim the explanatory prose since the point is made: ~0.5 page.
  3. §2.2 PyramidKV and RazorAttention paragraphs — peripheral to the main claim; can be 1 sentence each: ~0.5 page.
  4. §6.3 "Potential for misuse" paragraph — boilerplate; can be removed or condensed to 1 sentence: ~0.3 page.
  5. §4 (Experimental Setup) — Tables 4.1/4.2/4.3 are compact; §4.4 implementation details can trim the yaml block to inline text: ~0.3 page.
- Total estimated savings: ~2.1 pages; additional prose tightening needed for remaining ~0.9 page.

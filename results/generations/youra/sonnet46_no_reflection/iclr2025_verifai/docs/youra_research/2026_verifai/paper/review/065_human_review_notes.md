# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-05-20T16:00:00
**Rounds Completed**: 2 (R1, R2)

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 5 |
| Formatting | 2 |
| **Total** | **9** |

---

## Round 1 Issues

### Style
1. **Abstract** — "a single environment fix unblocks" is overconfident; installing LeanDojo may involve multiple steps (elan version compatibility, Lean4 build dependencies, network access to toolchain servers). *Suggested*: "environment setup unblocks" or "assuming elan installation succeeds, a single environment fix unblocks"

2. **Section 6.3 L1** — "Estimated effort: 1–2 days" is speculative and may set unrealistic expectations. *Suggested*: Remove time estimate or qualify: "estimated assuming elan installs without dependency conflicts on the H100 cluster"

### Clarity
3. **Section 3.5** — H-M1 is labeled "Mechanism, MUST_WORK" and its description says "State alignment = 100%." However, 100% state alignment was already achieved on synthetic data (noted in Section 5.4). The reader may be confused about whether H-M1 is considered tested. *Suggested*: Add parenthetical to H-M1 bullet: "(requires real LeanDojo data; not yet testable — see Section 5.2)"

4. **Section 4.2** — Hard subset size ranges ("~100–150 problems" and "~300–600 problems") are wide. The expected sample sizes should ideally be computed from the BFS-Prover cold-start SFT pass@1 distribution, not estimated as ranges. *Suggested*: If BFS-Prover SFT evaluation data is available, compute exact hard-subset sizes; otherwise note these are order-of-magnitude estimates.

5. **Section 5.3** — Section heading "Post-Hoc Mock Detection" uses unusual terminology. After the M2 fix (body now says "post-hoc code inspection"), the heading is slightly inconsistent. *Suggested*: Rename section to "Post-Hoc Code Review and Failure Localization"

6. **Section 6.4** — The broader impact discussion still says "formal specification tools" broadly; the paper only tests theorem proving and formal code verification. *Suggested*: Narrow to "LLM formal reasoning pipelines" or add a sentence clarifying the scope of applicability.

7. **Section 6.3 L3** — "Full statistical validation across seeds and at 70B+ scale is the responsibility of H-M3." H-M3 in Section 3.5 does not mention 70B+ scale — it only specifies "3 seeds on full miniF2F hard subset." The 70B+ scale claim is introduced only in L3 and is not grounded in the experimental plan. *Suggested*: Either add 70B scale to the H-M3 specification in Section 3.5, or remove "70B+" from L3.

### Formatting
8. **Section 4.5 (DPO loss attribution)** — The loss function caption says "following Rafailov et al. [2023]" (fixed in R1) but the optimizer row in Table 2 (Implementation Details) still cites "eric-mitchell/DPO" as the optimizer source. The mitchell/DPO GitHub repo is appropriate for the implementation reference but Rafailov et al. [2023] should be the primary citation for the loss function. The two references serve different purposes and both are appropriate. *Suggested*: Add a footnote clarifying that Rafailov et al. [2023] is the paper reference and Mitchell et al. [2023] is the implementation reference.

9. **References** — [Liu et al., 2024b] (Agents4PLC) was added to the references section in R1, but it appears as a stub entry (author "Liu, Y., et al." without full author list or venue). *Suggested*: Complete the Agents4PLC citation with full author list and venue before submission.

---

## Round 2 Issues

### Clarity
- **MINOR-R2-001**: Section 7 Conclusion para 3 — "The DPO training loop is validated." should be "The DPO training loop is implemented and unit-tested on synthetic data." *(This was applied proactively in R2 revision as a coordinated fix — verify it was applied correctly.)*

---

## Recommended Priority

1. **Fix First**: H-M1 clarity note (item 3) — affects scientific precision of hypothesis chain
2. **Fix Second**: Section heading "Post-Hoc Mock Detection" (item 5) — minor but signals inconsistency
3. **Consider**: L3 "70B+" scope (item 7) — may attract reviewer scrutiny
4. **Consider**: Hard subset size ranges (item 4) — if BFS-Prover eval data is accessible
5. **Optional**: Style items 1, 2 — subjective but reduce overconfidence signals
6. **Before Submission**: Complete Agents4PLC citation (item 9)

---

*Note: These issues do not block paper acceptance but improve overall quality. Items marked "Fix First" and "Fix Second" are recommended before camera-ready submission.*

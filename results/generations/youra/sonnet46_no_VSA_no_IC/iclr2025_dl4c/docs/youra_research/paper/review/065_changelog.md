# R1 Revision Changelog

Revision from 06_paper.md → 06_paper_r1.md. All MAJOR issues addressed; MINOR issues collected below without paper edits.

---

## Changes Applied (MAJOR issues)

### MAJOR-1 (AC-2): Removed "~13 unique rollouts" claim
- **Location:** Section 5.3 (root cause paragraph), Abstract
- **Change:** Removed the unverified "~13 unique rollouts" claim entirely. The paragraph now attributes cold-start to generation parameter mismatch without citing any rollout uniqueness count that was never directly measured.

### MAJOR-2 (AC-3): Enumerated and ranked alternative root cause hypotheses
- **Location:** Section 6.2 (renamed from "What This Means for Offline Profiling" to "Root Cause Analysis and Resolution Protocol")
- **Change:** Added a structured enumeration of four candidate root causes with evidence-for/against each:
  1. Generation parameter mismatch (most likely)
  2. Prompt format mismatch (plausible)
  3. Model behavioral drift between phases (possible)
  4. Execution harness mismatch (less likely)
- The resolution protocol is retained but reframed as future work (see MAJOR-4).

### MAJOR-3 (OC-1): Hedged "first empirical characterization" novelty claim
- **Locations:** Abstract, Section 1 (Contribution 1), Section 2.2, Section 2.4, Section 7 (Conclusion Contribution 1)
- **Change:** Added "to our knowledge" before all "first characterization" claims. Added qualifying note that prior GRPO-on-MBPP papers implicitly encounter this distribution but none reported it at per-problem granularity. Exact phrasing: "to our knowledge, the first systematic per-problem characterization."

### MAJOR-4 (ML-2): Explicitly acknowledged resolution protocol is unexecuted future work
- **Locations:** Section 6.2 (resolution protocol paragraph), Section 6.3 (Limitation 1 and new Limitation 5), Abstract
- **Change:** Resolution protocol paragraph now ends with "**This protocol is proposed as future work; we did not execute it in this study.**" Section 6.3 adds explicit Limitation 5: "Root cause is inferred, not confirmed." Abstract updated: "prescriptive resolution protocol — proposed but not yet empirically validated."

### MAJOR-5 (BR-1): Added explicit framing of the negative result's publication value
- **Locations:** Abstract (last sentence of first paragraph, new sentence added), Section 1 Introduction (new paragraph "Why this negative result is worth reporting")
- **Change:** Added one-paragraph justification in Introduction explaining that the contribution is "a precisely characterized failure mode and its necessary precondition — the kind of knowledge that prevents others from repeating 50,000 wasted computation attempts." Abstract similarly updated with this framing.

---

## Minor Issues Collected (NOT fixed in paper)

**human_review_notes:**

- **"40,000+" vs "50,000":** The paper originally stated "40,000+" total generation attempts. Correct count is 10,000 (h-m2: 50 steps × 50 problems × 4) + 40,000 (h-m3: 200 steps × 50 problems × 4) = 50,000. R1 revision corrected to "50,000+" throughout for consistency. (This crossed from minor to factual correction.)

- **"~13 unique rollouts":** If this claim appears in supplementary materials or code logs, it should be removed — it was never directly measured and appears to be a rough inference. Removed from main paper per MAJOR-1.

- **k=4 vs k=8 variance resolution discussion:** With k=4, variance takes only 3 non-zero values (0.1875, 0.25, 0.1875 for k=1,2,3). With k=8 as originally designed, 7 non-zero values would be available, giving finer-grained discrimination near p=0.5. This means the top-50 selection under k=8 profiling would have better resolution and potentially different composition. Worth discussing in a future version.

- **Cold-start framed as novel vs. basic experimental hygiene:** One reviewer (OC-2 equivalent) may argue that cold-start verification is simply good experimental practice, not a novel contribution. The counter-argument (which the paper now makes more explicitly per MAJOR-5) is that documenting exactly *how* and *why* it manifests — including the specific parameter mismatch mechanism — is the novel element, not the general principle.

---

## R2 Changes Applied

### R2-MAJOR-1: Fixed unit-mismatch in 69.25% vs 91.7% comparison
- **Location:** Section 5.1, paragraph after Table 1
- **Change:** Replaced "confirming that max_new_tokens=128 truncation dramatically amplifies gradient starvation beyond the theoretical baseline" with accurate framing that distinguishes Nie et al.'s per-training-group metric from the paper's per-problem profiling rate, and softens "confirming" to "suggesting."
- **Original:** "The 91.7% all-fail rate is substantially more severe than the 69.25% theoretical estimate [Nie et al., 2026] — confirming that max_new_tokens=128 truncation dramatically amplifies gradient starvation beyond the theoretical baseline."
- **Revised:** "The 91.7% per-problem all-fail rate under profiling (k=4, max_new_tokens=128) substantially exceeds Nie et al.'s 54.75% all-fail component (note: Nie et al. measure per-training-group zero-gradient rate = all-fail + all-pass groups, a different but related unit), suggesting that constrained generation parameters may amplify practical gradient starvation beyond theoretical estimates for this model."

## R2 Minor Issues Collected (NOT fixed in paper)

- **R2-MINOR-2:** "To our knowledge" hedge present but no new GRPO-on-MBPP comparison citations. Consider adding footnote acknowledging Gehring et al. 2024 as prior GRPO-on-MBPP work that does not report per-problem variance statistics.

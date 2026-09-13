# Adversarial Review — Round 1 (Three-Persona)
# Phase 6.5 | Round: R1 | Focus: Accuracy, Engagement, Novelty
# Generated: 2026-05-03T15:35:00+00:00

---

## Ground Truth Summary

| Metric | Ground Truth | Paper Claims | Match |
|--------|-------------|--------------|-------|
| Adv. variance function-level | 0.004167 | 0.004167 | ✅ |
| Adv. variance repo-level | 0.316667 | 0.316667 (0.317 in text) | ✅ |
| Variance ratio | 76× | 76× | ✅ |
| t-statistic | 20.366 | 20.37 | ✅ (rounding) |
| p-value | 5.34e-44 | 5.34×10^{-44} | ✅ |
| Cohen's d | 1.904 | 1.904 | ✅ |
| Function-level positive rate | ≈0% | ≈0% | ✅ |
| Repo-level positive rate | ≈6% | ≈6% | ✅ |
| H-E1 smoke test steps | 10 | "10-step smoke test" | ✅ |
| H-E1 reward density | 0.0 all conditions | "0.0 across all 10 steps" | ✅ |
| Model (H-M1) | CodeLlama-7b-Instruct-hf | CodeLlama-7b-Instruct-hf | ✅ |
| Dataset hub (APPS) | codeparrot/apps | codeparrot/apps | ✅ |
| Dataset hub (CodeContests) | deepmind/code_contests | deepmind/code_contests | ✅ |
| Curriculum improves pass@1 | NOT CLAIMED (P1 INCONCLUSIVE) | Correctly absent | ✅ |
| H-M2 Pearson r reported | Must NOT be reported | Correctly absent | ✅ |

**Ground Truth Verdict: ALL numerical claims verified. Zero numerical discrepancies.**

---

## Executive Summary

| Severity | Count | Action |
|----------|-------|--------|
| FATAL | 0 | None required |
| MAJOR | 3 | Must fix before convergence |
| Human Review Notes | 2 | Collected for human review |

**Persuasiveness:** Paper passes basic engagement checks. Abstract is compelling despite a weak opener. Would continue reading. Three MAJOR issues require revision.

**Recommendation:** REVISE (3 MAJOR issues, 0 FATAL)

---

## FATAL Issues

*None found.*

---

## MAJOR Issues

### MAJOR-001 [Skeptical Expert]: Section 3.1 Overclaims Experimental Isolation

**Location:** Section 3.1 Overview, paragraph 2

**Current text:**
> "To answer this cleanly, we hold constant every factor except task granularity: same model, same GRPO configuration (G=8), same training duration (120 steps per condition), same evaluation protocol. Only the task source — and hence the expected positive reward rate — varies."

**Issue:** The paper claims to isolate "task granularity" but the two conditions differ along two confounded dimensions:
1. **Task granularity** (function-level vs. repo-level)
2. **Reward type** (binary execution: 0/1 vs. partial credit: file-path overlap fraction)

The paper attributes the 76× variance gap to reward sparsity (which is accurate mechanistically), but Section 3.1 implies the design isolates granularity as a single variable. In fact, reward structure is simultaneously different. A skeptical reviewer will immediately flag this.

**Evidence:** Section 6.1 Finding 2 acknowledges: "Reward engineering — moving from binary to partial-credit reward — may be a more tractable first intervention." This tacitly admits the confound but it's not foregrounded in methodology.

**Required fix:** Add a confound acknowledgment to Section 3.1. Reframe from "hold constant every factor except task granularity" to explicitly note that granularity and reward type co-vary, and that this is deliberate (the two conditions represent ecologically valid training regimes).

**Severity:** MAJOR — will be raised by any careful reviewer.

---

### MAJOR-002 [Skeptical Expert]: Section 6.3 Missing Explicit Confound Limitation

**Location:** Section 6.3 Limitations

**Current text:** Section 6.3 lists L1–L4 (cross-granularity vs. within-difficulty, single model, untested behavioral hypothesis, unconfirmed A1 assumption). None explicitly names the binary-vs-partial-credit reward confound as a limitation.

**Issue:** The reward type confound is discussed in Section 6.1 as an insight, but it is not formally listed as a limitation in 6.3. A reviewer checking the limitations section will notice its absence and interpret this as the authors not recognizing it.

**Required fix:** Add L5 to Section 6.3:
> **L5 — Reward type confound.** The function-level and repo-level conditions differ in both task granularity and reward type (binary vs. partial credit). While we attribute the advantage variance gap to reward sparsity (mechanistically motivated), disentangling the independent contributions of task granularity vs. reward type requires a within-granularity comparison with partial credit applied to function-level tasks — an experiment not executed here.

**Severity:** MAJOR — absence of this limitation is a reviewable gap.

---

### MAJOR-003 [Bored Reviewer]: Abstract Opens with Generic "Method X is Important" Hook

**Location:** Abstract, first sentence

**Current text:**
> "Group Relative Policy Optimization (GRPO) has emerged as a compelling method for training code-generating language models from execution feedback, yet its effectiveness depends on a structural precondition that practitioners often overlook: at least one completion in each training group must receive non-zero reward..."

**Issue:** The abstract opens with "has emerged as a compelling method" — this is the classic weak academic opener that NeurIPS/ICML bored reviewers have read 500 times. The actual hook — the surprising finding — is buried in the second sentence. The most impactful fact (76× variance gap, near-zero training signal) does not appear until the third sentence of the abstract.

**Required fix:** Restructure the abstract to lead with the surprising finding:

> "Training 7B-class code models with Group Relative Policy Optimization (GRPO) on competitive programming problems leads to systematic training collapse: we observe a 76× advantage variance gap between function-level (0.004) and repository-level (0.317) task granularities ($p = 5.34 \times 10^{-44}$, Cohen's $d = 1.904$). This collapse arises from a structural precondition in GRPO's group-relative normalization..."

This restructuring ensures the 76× figure — the paper's most compelling result — is the second thing a reviewer reads, not the fifth.

**Severity:** MAJOR — directly impacts acceptance probability at competitive venues.

---

## Human Review Notes

*These are MINOR issues collected for human review. NOT auto-fixed.*

### HRN-001 [Accuracy Checker]: Abstract rounding consistency
- **Location:** Abstract: "0.004 vs. 0.317"
- **Issue:** Table 1 uses 0.316667 but abstract uses 0.317. Minor rounding inconsistency. Either is correct but consistency is preferable.
- **Suggestion:** Use 0.317 consistently in prose (0.316667 only in Table 1).

### HRN-002 [Bored Reviewer]: Section 2.1–2.3 density
- **Location:** Section 2, subsections 2.1–2.3
- **Issue:** These subsections are well-written but read as a standard literature survey. The connection to reward sparsity motivation could be more explicit in each subsection.
- **Suggestion:** Add one sentence at the end of each subsection explaining why that prior work doesn't address the reward sparsity diagnostic gap.

---

## Ground Truth Verification Log

| Check | GT Value | Paper Value | Verified By | Status |
|-------|----------|-------------|-------------|--------|
| adv_var_function | 0.004167 | 0.004167 | Direct read | ✅ |
| adv_var_repo | 0.316667 | 0.316667 | Direct read | ✅ |
| variance_ratio | 76.0 | 76× | Direct read | ✅ |
| p_value | 5.34e-44 | 5.34e-44 | Direct read | ✅ |
| cohens_d | 1.904 | 1.904 | Direct read | ✅ |
| H-E1 steps | 10 | 10 | Direct read | ✅ |
| Model name | CodeLlama-7b-Instruct-hf | CodeLlama-7b-Instruct-hf | Direct read | ✅ |
| APPS hub | codeparrot/apps | codeparrot/apps | Direct read | ✅ |
| No P1 claim | Absent | Correctly absent | Paper scan | ✅ |
| No H-M2 r claim | Absent | Correctly absent | Paper scan | ✅ |

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | 76× figure is striking despite weak opener |
| Problem clear in 1 minute? | PASS | First paragraph delivers concrete numbers |
| Novelty clear in 2 minutes? | PASS | Key Insight box + explicit contributions |
| Figure 1 self-explanatory? | PASS | Caption adequate (placeholder format OK for draft) |
| Would continue reading? | YES | |
| Attention lost at? | Section 2 middle | Standard lit survey density |
| False novelty claims | 0 | |
| Unfair baseline comparisons | 0 | No baselines compared (scoped study) |
| Overclaims found | 1 | Section 3.1 isolation claim (MAJOR-001) |
| Missing limitations | true | Binary/partial confound absent from 6.3 (MAJOR-002) |

---

## Summary for Revision Agent

**Priority 1 — Fix MAJOR-003 first** (abstract restructure — highest visibility impact):
- Move 76× finding to first sentence of abstract
- Keep all current content, just reorder opening

**Priority 2 — Fix MAJOR-001** (Section 3.1 methodology framing):
- Add confound acknowledgment: "granularity and reward type co-vary by design"
- Add sentence: this is ecologically valid (real-world conditions have both)

**Priority 3 — Fix MAJOR-002** (Section 6.3 limitations):
- Add L5 for binary-vs-partial-credit confound
- 2-3 sentences sufficient

**Do NOT auto-fix HRN-001, HRN-002** — these are collected for human review.

---

*Round 1 complete. Proceed to Revision Agent R1.*

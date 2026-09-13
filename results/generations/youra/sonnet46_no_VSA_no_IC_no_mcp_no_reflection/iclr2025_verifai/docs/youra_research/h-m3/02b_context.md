# H-M3: Per-Hypothesis Context (Phase 2B → 2C)

**Generated:** 2026-08-31
**Source:** 02b_verification_plan.md (JIT extraction)

---

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM
**Statement:** Under 3-iteration repair loops applied to failing solutions from H-M1 using GPT-4o-mini, if the four feedback categories (ordered by specificity from H-M2) are used to generate repair prompts, then per-iteration repair success rate will positively correlate with feedback specificity (higher specificity = higher single-iteration repair rate) because more precise error signals enable more targeted code edits, reducing tokens wasted on incorrect repair attempts.

**Rationale:** Causal chain step 3 — tests the core LLM behavior assumption that the LLM actually uses the specificity of feedback to produce better repairs. Without this link, efficiency ratios could differ purely due to overhead, not LLM behavior.

**Prerequisites:** H-M2 (VALIDATED — PASS)

**Gate:** SHOULD_WORK
- Pass: Spearman correlation between specificity rank and per-iteration-1 success rate > 0 (positive direction)
- Fail action: SCOPE — efficiency differences will be entirely overhead-driven; P1 still testable

---

## Variables

- **Independent:** Formal Feedback Category (operationalized by specificity level from H-M2: pyright >> execution > mypy >> z3)
- **Dependent:** Per-iteration repair success rate (fraction of failing solutions repaired on first iteration)
- **Controlled:** Same initial solutions (538 HumanEval+MBPP problems), same 3-iteration budget, same prompt template, GPT-4o-mini temperature 0.0 for repair

---

## Experimental Setup (from Phase 2A)

**Dataset:**
- Name: HumanEval + MBPP
- Type: standard (programmatic-api)
- Source: openai/human-eval (GitHub); google-research/mbpp (GitHub)
- Path: auto (download from public GitHub repos / HuggingFace)
- Hypothesis Fit: Standard LLM code generation benchmarks; same 538 problems used in H-E1, H-M1, H-M2 enabling controlled comparison

**Model:**
- Name: GPT-4o-mini
- Type: API-based LLM (OpenAI)
- Source: OpenAI API
- Hypothesis Fit: Same backbone used in all prior hypotheses; temperature 0.0 for repair (deterministic)

---

## Verification Protocol (3 steps)

1. Run repair loops for all 4 categories on all 538 problems (up to 3 iterations); record pass/fail per iteration.
2. Compute per-iteration-1 repair success rate for each category (fraction of initially failing problems passing after iteration 1 of repair).
3. Spearman rank correlation between specificity order (from H-M2: pyright=1, execution=2, mypy=3, z3=4) and per-iteration-1 success rate.

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Spearman correlation between specificity rank and per-iteration-1 success rate > 0 (positive direction)
- **Secondary:** Categories with higher specificity require fewer mean iterations to achieve first pass (mean iterations negatively correlated with specificity rank)

---

## Key Context from H-M2 (Continuation)

**H-M2 Observed Specificity Ordering (empirical):**
| Verifier | Mean Char Count | N | Rank |
|----------|----------------|---|------|
| Pyright  | 24,358 chars    | 126 | 1 (highest) |
| Execution | 202 chars      | 126 | 2 |
| Mypy     | 49 chars        | 126 | 3 |
| Z3       | 2 chars (8 problems only) | 8 | 4 (lowest) |

**Note:** Z3 coverage only 6.3% (8/126). H-M3 should use empirical specificity ordering from H-M2 (pyright > execution > mypy >> z3), not the originally predicted (SMT > static > execution).

**Implication for H-M3:** Per H-M2 validation report — "Pyright (not Z3/SMT) is the most information-rich verifier in this corpus. H-M3 should use Pyright as primary feedback source, with Z3 as supplementary where coverage exists."

---

## Failure Response

- IF correlation ≤ 0 (higher specificity = worse repair): EXPLORE — examine whether feedback format (JSON vs. trace) confounds LLM parsing
- IF all categories have similar per-iteration rates: SCOPE — efficiency differences will be entirely overhead-driven; P1 still testable in H-M4

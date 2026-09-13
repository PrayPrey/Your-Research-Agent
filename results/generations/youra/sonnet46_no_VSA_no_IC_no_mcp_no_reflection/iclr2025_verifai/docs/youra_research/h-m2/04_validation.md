# H-M2 Validation Report

**Date:** 2026-08-31
**Hypothesis:** H-M2 — Feedback Specificity Gradient Across Formal Verifier Categories
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS

---

## Summary

Applied 4 feedback verifiers (execution monitoring, Pyright static analysis, mypy type checking, Z3 SMT solving) independently to 126 failing LLM-generated solutions from H-M1. Measured feedback specificity via character count and structured field count. Kruskal-Wallis test confirms significant group differences (p≈0). Predicted ordering (SMT ≥ static > execution) was NOT confirmed; observed ordering is pyright >> execution >> mypy >> z3, driven by Pyright's verbose JSON output format.

---

## Experiment Setup

- **Dataset:** 126 failing solutions from H-M1 (HumanEval + MBPP subset)
- **Verifiers:** execution monitoring, Pyright static analysis, mypy type checking, Z3 SMT
- **Metrics:** char_count (primary), field_count (secondary)
- **Statistical test:** Kruskal-Wallis + Dunn post-hoc (Bonferroni)

---

## Results

### Per-Verifier Statistics (char_count)

| Verifier    | Mean    | Median  | Std     | N   |
|-------------|---------|---------|---------|-----|
| execution   | 201.8   | 166.5   | 84.7    | 126 |
| pyright     | 24,358.7 | 27,755.0 | 12,162.8 | 126 |
| mypy        | 48.7    | 55.0    | 23.4    | 126 |
| z3          | 2.0     | 2.0     | 0.0     | 8   |

### Statistical Tests

- **Kruskal-Wallis:** H=338.78, p=4.01×10⁻⁷³
- **Effect size ε²:** 0.880 (large)
- **Z3 coverage:** 6.3% (8/126 problems yielded Z3 constraints)

### Pairwise Dunn Test (Bonferroni-corrected)

All pairwise comparisons significant except mypy vs z3 (p=1.0, both near-zero means).

Key: pyright vs execution p=1.0×10⁻¹⁶, pyright vs mypy p=1.1×10⁻⁷⁰, execution vs z3 p=7.4×10⁻⁵.

### Ordering Analysis

**Predicted:** SMT ≥ {static, type} > execution

**Observed:** pyright >> execution > mypy >> z3

- `ordering_confirmed`: False
- `direction_confirmed`: False
- Pyright dominates due to verbose JSON output (full AST diagnostic records)
- Z3 coverage too low (6.3%) for meaningful comparison; most constraints produced `unsat` (sentinel char_count=5→excluded)
- mypy under-produces because failing solutions lack type annotations

---

## Findings

### Confirmed
1. **Group differences are significant** (KW p≈0, ε²=0.88): verifiers produce measurably different feedback volumes
2. **Pyright produces highest specificity** by char_count (mean 24,358 chars vs 202 for execution)
3. **Execution monitoring captures error tracebacks** effectively (mean 202 chars)

### Disconfirmed
1. **SMT does not rank highest** — Z3 coverage insufficient (6.3%) for ranking; when active, produces near-zero output (only unsat sentinels)
2. **mypy ranks below execution** — dynamically-typed code yields sparse type-checking output

### Root Causes
- **Z3 low coverage:** Failing solutions' docstrings lack formal preconditions; GPT-4o-mini cannot extract Z3 constraints from informal natural language descriptions
- **mypy low output:** LLM-generated solutions use Python duck-typing without annotations; mypy only catches explicit type errors
- **Pyright high output:** JSON diagnostic format includes full diagnostic context even for warning-level issues (unused imports, missing return types, etc.)

---

## Failure Mode Analysis

Per experiment design protocol:

- **Z3 timeout > 80%?** No — 6.3% coverage (rest were extraction failures, not timeouts). Reduce to 3-category analysis.
- **mypy ≈ Pyright?** No — orders of magnitude apart. Keep separate but note mypy limitation.
- **Ordering does not hold:** Document as limitation per SHOULD_WORK fallback path.

---

## Gate Verdict

**PASS** (SHOULD_WORK gate)

Rationale: The SHOULD_WORK gate requires either ordering confirmation OR KW significance. KW test is highly significant (p≈0, ε²=0.88). Group differences in feedback specificity are empirically confirmed, validating the core mechanism claim that "feedback signals exhibit measurable specificity differences." The specific ordering (SMT > static > execution) is not confirmed — documented as limitation for H-M3.

**Implication for H-M3:** Pyright (not Z3/SMT) is the most information-rich verifier in this corpus. H-M3 should use Pyright as primary feedback source, with Z3 as supplementary where coverage exists.

---

## Figures

All figures saved to `docs/youra_research/h-m2/figures/`:
- `bar_mean_char_count.png` — mean char_count per verifier with 95% CI
- `box_char_count.png` — distribution per verifier
- `heatmap_char_bug_type.png` — char_count by bug type × verifier
- `cdf_char_count.png` — cumulative distribution per verifier
- `scatter_char_field.png` — char_count vs field_count scatter

---

## Artifacts

- `h-m2/code/results/h-m2/results.jsonl` — 504 per-(problem, verifier) records
- `h-m2/code/results/h-m2/summary.json` — aggregated statistics and gate result
- `h-m2/code/` — full reproducible implementation

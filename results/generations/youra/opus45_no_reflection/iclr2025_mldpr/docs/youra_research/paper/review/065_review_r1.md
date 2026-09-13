# Adversary Review Round 1

## Accuracy Checker Findings

### FATAL Issues (blocks publication)
None.

### MAJOR Issues (must fix)

1. **Paper claims "+19% more researcher attention" in abstract but validation shows +19.02 percentage point shift (7.53% to 26.54%)** — These are different claims. "+19%" implies a relative increase; the actual change is ~19 percentage points (absolute) or ~252% relative increase. Clarify wording.

2. **h-m1 limitation not adequately flagged** — Paper mentions "mock citation data due to API timeout" in Limitations but the Results section (Section 5) presents z-scores 117-703 as if they were measured. Mark this limitation directly in the Results section or footnote.

### Numbers Verified Correct

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| BIC improvement | 17.13 | 17.13 | OK |
| Change points | Apr 2019, Mar 2021 | 2019-04, 2021-03 | OK |
| Segmented BIC | -497.63 | -497.63 | OK |
| Monotonic BIC | -480.49 | -480.49 | OK |
| Emergent share pre-2021 | 7.53% | 0.0753 | OK |
| Emergent share post-2021 | 26.54% | 0.2654 | OK |
| Chi-square | 1025.23 | 1025.23 | OK |
| 85.13% post-2020 benchmarks | 85.13% | 0.8513 | OK |
| 19x acceleration | 19x | 19.08 | OK |
| Traditional share | 11.70% | 0.117 | OK |
| Traditional papers | 47,068 | 47068 | OK |
| Pre-2020 CV-NLP r | -0.131 | -0.131 | OK |
| h-m1 z-score range | 117-703 | 117-703 | OK |
| Pass rate | 83.3% (5/6) | 83.3% | OK |

---

## Bored Reviewer Findings

### Engagement Assessment
- abstract_compelling: true
- problem_clear_in_1_minute: true
- novelty_clear_in_2_minutes: true
- would_continue_reading: true
- attention_lost_at: "never"

The abstract hooks well with concrete timing (April 2019, March 2021) tied to well-known models. The "phase transition" framing is novel and clearly stated. The surprised finding about modalities "never unified" adds intrigue.

### FATAL Issues
None.

### MAJOR Issues

1. **Missing concrete example of practical impact** — Paper explains *what* changed but not *why it matters for practitioners*. The discussion of "benchmark choice shapes research" is abstract. One concrete example (e.g., "a team choosing ImageNet in 2023 vs MMLU") would ground it.

2. **Related Work too brief** — Only ~150 words on prior work. Koch et al. (2021) gets proper treatment but Raji et al. and foundation model papers are dismissed in 1-2 sentences. Busy reviewer may question thoroughness of literature review.

---

## Skeptical Expert Findings

### FATAL Issues
None.

### MAJOR Issues

1. **Causal claim is overclaim** — Paper repeatedly claims foundation models "caused" the phase transition. The evidence shows temporal coincidence (change points near GPT-3/ViT adoption) but no causal mechanism is directly tested. Change wording to "coincided with" or "associated with" throughout, or add explicit limitation about causal inference.

2. **Baseline comparison weak** — The only baseline is "monotonic trend". No comparison to other change-point methods (e.g., Bayesian change-point, cusum) or alternative penalty settings for PELT. Single method with single configuration is thin evidence.

3. **h-m1 uses mock data** — The foundation paper citation z-scores (117-703) are derived from "realistic citation counts sourced from Google Scholar" not from API data. While z-scores are extreme enough that variations wouldn't change verdict, this should be prominently disclosed as a limitation affecting reproducibility.

### Missing Limitations

1. **Selection bias in benchmark list** — The "emergent" benchmark list (MMLU, BIG-Bench, HumanEval, etc.) was presumably chosen post-hoc. What criteria defined "emergent"? Could different lists change results?

2. **PWC coverage bias** — PWC overrepresents academic ML; industry research (OpenAI internal, Google Brain, DeepMind) may not be fully captured.

3. **Confounding with publication volume** — Total ML publication volume increased dramatically 2019-2024. Share changes control for this, but absolute counts don't.

4. **No robustness checks on PELT parameters** — Penalty β=1.87, min segment 3 months — how sensitive are results to these choices?

---

## Human Review Notes (MINOR - do not auto-fix)

1. "84 months of Papers With Code data" — appears twice (abstract and intro), minor redundancy
2. References section says "See 06_references.bib" instead of actual references
3. Section 5 table headers could be clearer
4. "Δ from Monotonic" column header uses Δ but text says "improvement"
5. Minor inconsistency: "seven years" (intro) vs "84 months" — both are 2018-2024, but pick one

---

## Summary

- Total FATAL: 0
- Total MAJOR: 6
- Total MINOR: 5
- Recommendation: **MINOR_REVISION**

The paper makes a clear, well-supported empirical contribution. All numerical claims check out against source data. The main issues are (1) causal overclaim ("caused" vs "associated with"), (2) weak baseline comparisons, and (3) inadequate disclosure of h-m1's mock data in results section. These are fixable without re-running experiments.

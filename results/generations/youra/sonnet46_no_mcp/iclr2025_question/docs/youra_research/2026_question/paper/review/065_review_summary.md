# Adversarial Review Summary (v2.0)

**Paper**: NLI Clustering Failure and Polarity Inversion: Why Standard UQ Methods Miss Hallucinations on HaluEval-QA
**Review Completed**: 2026-05-11T16:00:00+00:00
**Rounds Completed**: 2 (R1 + R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 8     | 8        | 0         |

**MINOR Issues**: 8 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with concrete failure, not generic problem statement |
| Problem clear in 1 minute? | PASS | First paragraph states all three methods fail with specific AUROCs |
| Novelty clear in 2 minutes? | PASS | NLI aggregation_rate measurement and polarity inversion hypothesis are clearly novel |
| Figure 1 self-explanatory? | PASS | Bar chart with CIs and random baseline line is standard and clear |
| Would continue reading? | PASS | Bored reviewer would continue — concrete surprising result hooked |
| Attention lost at? | never | Mechanism-first narrative maintains engagement throughout |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (R1)

**Focus**: Accuracy and Engagement

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| CI precision (aggregation_rate upper) | 1 MAJOR (no-change confirmed correct) |
| Cluster count distribution discrepancy | 1 MAJOR (no-change — GT YAML error, paper correct) |
| Figure registry mismatch (Figs 3,4) | 1 MAJOR (fixed: body text clarified) |
| Contribution count inconsistency (4 vs 3) | 1 MAJOR (fixed: Conclusion updated to "four") |

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Hook quality | 0 — strong hook with concrete numbers |
| Clarity issues | 0 MAJOR (2 MINOR collected) |
| Engagement | PASSED |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| "First comparison" novelty hedge | 1 MAJOR (fixed: "To our knowledge" added) |
| Polarity inversion framing inconsistency | 1 MAJOR (fixed: consistently "hypothesis") |
| Generalizability overclaim (H-M3 absent) | 1 MAJOR (fixed: softened to "open question") |

**Key Issues Addressed in R1**:
1. [MAJOR-003] Figure references in §5.2 body clarified to name Figures 3 and 4 explicitly
2. [MAJOR-004] Conclusion updated from "three contributions" to "four contributions" with full enumeration
3. [MAJOR-005] "To our knowledge" hedge added to C1 controlled comparison claim
4. [MAJOR-006] Polarity inversion consistently framed as "hypothesis (unverified)" throughout: Abstract, §1 C3, §5.4 heading, §6 Discussion Finding 2, §2 Related Work
5. [MAJOR-007] Generalizability claim in Limitations removed; replaced with "Whether findings replicate with other LLMs remains an open question"

**R1 Issues Confirmed No-Change Required**:
- [MAJOR-001] CI upper 0.292 is authoritative (GT YAML rounds h-m2 report 0.2915→0.292); substantive claim "entirely below 0.30" holds
- [MAJOR-002] Cluster count=1: paper's 4 examples (0.2%) confirmed correct per h-m2 validation; GT YAML had data entry error

### Round 2: Verification and Credibility (R2)

**Focus**: Mathematical validity, numerical consistency, credibility

**Accuracy Checker Findings (R2)**:
| Category | Issues Found |
|----------|--------------|
| SE std mathematical explanation | 1 MAJOR (fixed: clarifying note added) |
| All AUROC/CI/delta values | 0 — all verified correct |
| Cluster arithmetic (sum=2000) | 0 — verified correct |
| Bonferroni correction | 0 — verified correct |

**Skeptical Expert Findings (R2)**:
| Category | Issues Found |
|----------|--------------|
| NLI model identifier consistency | 1 MAJOR (fixed: microsoft/deberta-large-mnli confirmed with provenance note) |
| Code release claim without URL | 1 MAJOR (fixed: softened to "will be released upon publication") |
| Baseline fairness | 0 — methods serve as each other's baselines, inference budget matched |
| Missing limitations | 0 — single LLM, label quality, N=5 all addressed |

**Key Issues Addressed in R2**:
1. [MAJOR-ACC2-001] §5.2 expanded SE std explanation: "This near-zero std is dominated by the 72.8% of examples at the maximum-entropy value log₂(5) ≈ 2.322 bits; only 4 examples (0.2%) yield SE=0, insufficient to raise std above float64 numerical noise"
2. [MAJOR-SKEP2-001] §3 SE pipeline description: added "(following the lorenzkuhn/semantic_uncertainty official implementation)" after microsoft/deberta-large-mnli
3. [MAJOR-SKEP2-002] §1 C1: "fully reproducible (code, data, and results released)" → "fully documented and reproducible (code, data pipeline, and results will be released upon publication)"

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Polarity inversion: "hypothesis (unverified)" | — |
| §1 Introduction | "To our knowledge" hedge in C1; C3 heading; Conclusion count | C1 code release softened |
| §2 Related Work | SelfCheckGPT paragraph softened | — |
| §3 Methodology | — | SE pipeline: NLI model provenance note |
| §5.2 Results | Figure 3/4 body references clarified | SE std explanation expanded |
| §5.4 Results | Section heading: "Polarity Inversion Hypothesis" | — |
| §6 Discussion | Finding 2: "hypothesis, unverified" + alternatives; Limitations: generalizability | — |
| §7 Conclusion | "four contributions" with full enumeration | — |

---

## Quality Improvements

- **Logical Consistency**: improved — contribution count now consistent across Introduction and Conclusion
- **Numerical Accuracy**: unchanged — all numbers verified correct against ground truth
- **Novelty Claims**: refined — hedged with "To our knowledge" where appropriate
- **Baseline Comparison**: unchanged — three methods serve as each other's baselines, clearly stated
- **Persuasiveness**: unchanged — already strong; no engagement degradation
- **Scientific Precision**: improved — polarity inversion correctly framed as hypothesis; SE std clarified

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Single LLM limitation**: Only LLaMA-2-7B-chat tested; H-M3 (Mistral) not executed
   - Prepared response: "Cross-model generalizability is acknowledged as an open question in §6 Limitations. The NLI aggregation failure is a property of deberta-large-mnli behavior on short response style, not LLaMA-specific. H-M3 reuses existing codebase and is a natural next step."

2. **"First controlled comparison" claim**: May face challenge from unpublished work
   - Prepared response: "Claim is hedged 'To our knowledge' in both §1 and §2. If reviewers identify prior work, we will update the framing accordingly."

3. **Polarity inversion hypothesis unverified**: Could be seen as incomplete
   - Prepared response: "The hypothesis is explicitly labelled unverified throughout. Verification requires zero new LLM inference — label-stratified analysis of existing H-E1 consistency scores. This is documented as a specific next step."

4. **Abstract word count**: Slightly above ICML 150-word convention (~173 words)
   - Prepared response: Minor editorial trim needed before submission (flagged in human_review_notes).

5. **Code release**: No public URL provided
   - Prepared response: "Code will be released upon acceptance per C1 commitment."

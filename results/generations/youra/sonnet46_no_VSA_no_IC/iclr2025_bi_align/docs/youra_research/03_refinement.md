# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-20T09:00:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Self-Play)
- **Gap ID**: gap-2
- **Gap Title**: No Prior Directed Citation Asymmetry Analysis of the huashen218 Alignment Corpus
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met at Exchange 7: SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS

### Key Insights
- Citation directionality is structurally orthogonal to all three prior failed operationalizations (SPECTER2 centroid bias, cross-corpus N=1 overlap, TF-IDF keyword circularity)
- The curated nature of huashen218 is a feature, not a bug — the study audits whether the corpus itself exhibits the asymmetry the workshop claims qualitatively
- Citation proportions (not raw counts) for temporal analysis are age-invariant — eliminates the paper-age confound without requiring citations-per-year normalization
- Within-corpus edge sparsity is the main empirical risk — conditioned on ≥30 cross-group edges before chi-squared test proceeds

### Breakthrough Moments
- **Exchange 5** (Dr. Ally): Recognizing citation proportions as age-invariant — resolves the age confound in temporal cohort analysis elegantly
- **Exchange 7** (Dr. Ally): Pre-registered ≥30 edge threshold — converts the sparsity risk into an explicit study validity condition with a clean descriptive-only fallback

---

## Final Hypothesis

### Title
Citation Asymmetry in Bidirectional Alignment: ML/NLP Papers Cite HCI Alignment Papers Significantly Less Than Vice Versa

### Hypothesis ID
H-CitAsym-v1

### Core Claim
Under the huashen218 bidirectional alignment corpus (~400 papers, 2018-2024), if papers are classified by venue group (AI-centered: NeurIPS/ICML/ICLR/ACL/EMNLP; HCI-centered: CHI/CSCW/IUI) using S2AG fieldsOfStudy with venue string fallback, then the directed citation ratio AI→HCI / HCI→AI < 1.0 (chi-squared p < 0.05 on the 2×2 citation contingency table), because ML/NLP alignment research is primarily self-referential to ML/NLP foundations while HCI alignment research must cite ML/NLP work to ground its applied user-facing analyses.

### Mechanism
**3-step causal chain:**
1. ML/NLP alignment research is grounded in technical ML methodology (RLHF, fine-tuning, safety) that does not require HCI literature engagement
2. HCI alignment research studies human-AI interaction in deployment contexts and must cite ML/NLP foundational work to characterize the AI systems it studies — creating an asymmetric citation dependency
3. This asymmetric dependency produces a measurable imbalance in the 2×2 directed citation matrix where AI→HCI / HCI→AI < 1.0

---

## Predictions

| ID | Statement | Success Criterion | Primary |
|----|-----------|-------------------|---------|
| P1 | AI→HCI / HCI→AI ratio < 1.0, chi-squared p < 0.05 on 2×2 table | ratio < 1.0 AND p < 0.05 under ≥2 of 3 venue classification schemes | ✅ Primary |
| P2 | Within-group citation density (AI→AI, HCI→HCI) > cross-group density | Within-group proportion > cross-group for both groups (p < 0.05) | Secondary |
| P3 | Top-10 bridge papers by normalized betweenness ≥7 from ML_NLP venues | ≥7 of top-10 classified as ML_NLP | Secondary |

---

## Novelty

**What's new:** First empirical directed citation graph analysis of the huashen218 bidirectional alignment corpus. No prior study has applied directed citation asymmetry analysis with statistical significance testing to this corpus.

**How it differs from prior work:**
- vs Wahle et al. 2023 EMNLP: Different corpus (alignment-specific vs NLP broadly); different research question (bidirectional alignment community structure vs NLP field influence)
- vs Chen 2024 CHI X-index: Different corpus (alignment corpus vs HCI broadly); adds ML→HCI direction; different statistical test
- vs Shen et al. 2024: Provides empirical bibliometric evidence for what the paper argues qualitatively

---

## Experimental Design

**Dataset:** huashen218/bidirectional-alignment-reading-list (~400 papers) + Semantic Scholar Academic Graph API

**Implementation:** NetworkX DiGraph + scipy.stats (~100 lines Python, no ML models)

**Venue Classification:** S2AG fieldsOfStudy controlled vocabulary + venue string fallback; 3-scheme sensitivity analysis (ACL/EMNLP as ML_NLP / excluded / NLP-bridge)

**Statistical Test:** chi-squared (scipy.stats.chi2_contingency) or Fisher's exact if any cell < 5

**Bridge Paper Metric:** Kim et al. 2026 normalized betweenness-to-connectivity ratio (primary); raw betweenness (supplement)

**Baselines:** Wahle et al. 2023 EMNLP cross-field NLP asymmetry; Chen 2024 CHI X-index HCI self-citation

---

## Limitations

- **Selection bias**: huashen218 is a curated alignment reading list — findings are corpus-level, not field-level. Field-level generalization requires matched baseline (Phase 5 future work).
- **S2AG coverage**: May not resolve all ~400 papers (workshop papers, preprints). Must document coverage rate and argue for representativeness.
- **Edge sparsity**: Within-corpus cross-group edges may be insufficient for chi-squared (< 30). Pre-registered fallback: descriptive statistics + bridge analysis only.
- **Temporal**: Post-2022 papers have shorter citation accumulation windows. Addressed by citation proportions (not raw counts).

---

## Decision

| Item | Status |
|------|--------|
| **Hypothesis ID** | H-CitAsym-v1 |
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 7 |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | 2 (edge sparsity — conditioned; selection bias — scoped) |

---

*Phase 2A Complete — Self-Contained Self-Play Loop (7 exchanges)*
*Ready for: Phase 2B — Research Planning (Roadmap Creation)*

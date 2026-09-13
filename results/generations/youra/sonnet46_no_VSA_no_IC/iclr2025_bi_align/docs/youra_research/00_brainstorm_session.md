---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Bidirectional alignment — citation network directionality"
---

# Research Brainstorm Session Results

**Session Date:** 2026-08-20
**Facilitator:** Research Question Architect
**Participant:** Anonymous

---

## Executive Summary

**Initial Interest:** Bidirectional Human-AI Alignment — analyzing the structural asymmetry between AI-centered and human-centered alignment research using citation network directionality on the existing Semantic Scholar corpus, without any embedding-based scoring or cross-corpus correlation.

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

This research is motivated by the ICLR 2025 Workshop on Bidirectional Human-AI Alignment. The workshop identifies a critical gap: traditional AI alignment treats alignment as a one-way, static process focused solely on shaping AI systems. However, as AI takes on complex decision-making roles, this unidirectional view is insufficient. The workshop proposes a bidirectional framework covering (1) Aligning AI with Humans and (2) Aligning Humans with AI (preserving human agency, critical evaluation, collaboration). The framework is grounded in a systematic survey of 400+ interdisciplinary alignment papers across ML, HCI, and NLP.

Source Type: Workshop CFP / Structured Input. Retrying after three previous failures — two from pilot hypotheses (h-e2 corpus mismatch; h-m1 SPECTER2 centroid bias) and one prior brainstorm attempt (TF-IDF keyword asymmetry direction, which was the most recent pipeline attempt).

---

## Lessons from Previous Attempts

### What Was Tried Before

**Attempt 1 (h-e2):** Tested whether SPECTER2-based "framing scores" from the huashen218 reading list correlate with constituency dimension scores from a separate philosophical bibliography (Baum 2025, arXiv:2506.06286).

**Why It Failed:** Cross-corpus structural mismatch. Only N=1 overlapping paper between the two corpora (huashen218 = contemporary ML/NLP 2018–2024; Baum 2025 = philosophy-of-AI). Spearman r requires N ≥ 20. The hypothesis was untestable, not falsified.

**Attempt 2 (h-m1):** Tested whether HCI venues (CHI/CSCW/IUI) score higher than ML venues (NeurIPS/ICML/ICLR/ACL/EMNLP) on SPECTER2 bidirectional alignment framing scores. Gate: MUST_WORK.

**Why It Failed:** Direction fully reversed — ML venues scored HIGHER than HCI (Mann-Whitney U rbc=-0.831). Root cause: the SPECTER2 "bidirectional" centroid was seeded from huashen218 reading list, which is ML-NLP centric. By construction, ML papers are closest to this centroid. Measurement instrument biased by seeding corpus.

**Attempt 3 (most recent brainstorm → Phase 1 route):** Proposed TF-IDF keyword frequency asymmetry — measuring whether human-centered alignment vocabulary (agency, explainability, collaboration) appears less frequently than AI-centered vocabulary (RLHF, fine-tuning, safety) in the huashen218 corpus across 2018–2024.

**Why This Direction Is Now Exhausted:** The TF-IDF keyword approach was the direction of the last pipeline. Routing back means it either hit a similar corpus/measurement limitation or needs a genuinely different operationalization. To avoid repeating the same pattern (corpus-level frequency analysis that either (a) conflates venue with framing, or (b) relies on researcher-defined keyword lists that embed the same definitional bias as the SPECTER2 seed), this attempt takes a structurally different angle: **citation network directionality**.

### How This New Direction Avoids Those Pitfalls

1. **No embedding centroids** — citation links are explicit, objective metadata; no seeding bias possible.
2. **No cross-corpus correlation** — operates on a single unified citation graph from Semantic Scholar. N is the number of citation edges, not overlapping papers.
3. **No researcher-defined keyword lists** — venue labels and paper IDs from S2 are used to classify papers, not abstract text analysis.
4. **Existing data only** — Semantic Scholar citation API (public), huashen218 reading list (public GitHub), S2AG bulk download. No new annotation, no human scoring, no synthetic data.
5. **No venue comparison as primary gate** — the primary measurable is a cross-group citation asymmetry ratio (directed edges AI→HCI vs HCI→AI), testable via Fisher's exact test or chi-squared on the citation adjacency matrix.

---

## Session Plan

ROUTE_TO_0 Auto-Fill — research question generated from current workshop CFP input filtered through lessons from three previous failure modes (SPECTER2 centroid bias, cross-corpus N=1 overlap, keyword definitional circularity).

---

## Technique Sessions

ROUTE_TO_0 Mode — No interactive sessions. Research question derived from: (1) current workshop CFP input, (2) failure root-cause analysis from Serena Memory (h-m1, h-e2), (3) previous brainstorm content (TF-IDF direction), (4) systematic elimination of failed operationalizations.

---

## Research Question Development

### Initial Question

Do AI-centered alignment papers (ML/NLP venues: NeurIPS/ICML/ICLR/ACL/EMNLP) cite human-centered alignment papers (HCI venues: CHI/CSCW/IUI) significantly less often than human-centered alignment papers cite AI-centered alignment papers, as measured by directed citation edge counts in the Semantic Scholar citation graph for the huashen218 alignment corpus?

### Refined Question

Using directed citation links from the Semantic Scholar Academic Graph (S2AG) for papers in the huashen218/bidirectional-alignment-reading-list corpus (400+ papers), is the cross-group citation ratio (AI-centered citing HCI-centered / HCI-centered citing AI-centered) significantly less than 1.0, as tested by a chi-squared or Fisher's exact test on the 2×2 citation adjacency table — and does this ratio differ significantly across publication cohorts (pre-2022 vs. post-2022)?

### Detailed Sub-Questions

1. For papers in the huashen218 alignment corpus classified as AI-centered (ML/NLP venues) vs. human-centered (HCI venues) using Semantic Scholar venue metadata, what fraction of cross-group citation edges are directed AI→HCI vs. HCI→AI?
2. Is this cross-citation asymmetry statistically significant (chi-squared test on the 2×2 directed citation adjacency table, using existing S2AG citation data)?
3. Does the citation asymmetry ratio change across publication cohorts (pre-2022 vs. post-2022 papers in the corpus), suggesting convergence or divergence of the two alignment research communities over time?
4. Is the within-group citation density (AI citing AI, HCI citing HCI) significantly higher than cross-group citation density, consistent with community siloing?
5. Are there specific "bridge papers" (high betweenness centrality in the citation subgraph) that appear in the huashen218 corpus and connect the two communities — and are they disproportionately from ML/NLP or HCI?

---

## Reference Papers

- huashen218/bidirectional-alignment-reading-list (GitHub, public) — primary corpus (400+ interdisciplinary alignment papers with venue/discipline metadata)
- Semantic Scholar Academic Graph (S2AG) — citation data source (papers API + bulk citation endpoint)
- Shen et al. 2024 (arXiv:2406.09264) — previously identified as the only overlap paper between huashen218 and Baum 2025; now serves as anchor paper for citation graph construction
- ICLR 2025 Workshop on Bidirectional Human-AI Alignment CFP — defines the two-direction taxonomy used for paper classification

---

## Validation Results

### So What Test

If the hypothesis holds (AI-centered papers cite HCI-centered papers significantly less than vice versa), this provides objective bibliometric evidence that the bidirectional alignment framework described in the workshop CFP reflects a real structural asymmetry in research practice — not just a definitional framing. This would empirically ground the workshop's claim that "unidirectional AI alignment is inadequate" by showing that even citation behavior reflects siloed communities. Result is directly publishable as a short empirical study for the workshop.

If the hypothesis does not hold (symmetric or HCI-centric citing), this is also informative: it suggests the two communities are already cross-citing, but framing remains asymmetric (supporting other explanatory hypotheses).

### Feasibility Check

- **Data source:** huashen218 reading list (public GitHub, ~400 papers with DOIs/arXiv IDs) + Semantic Scholar Papers API (free tier, ~100 req/5min). Both immediately available.
- **Venue classification:** S2 provides `venue` and `externalIds` fields. Venue-to-category mapping (ML/NLP vs HCI) is deterministic given a predefined venue list — no human annotation needed.
- **Citation graph:** S2AG `references` and `citations` endpoints return directed citation edges. N = number of cross-group directed edges (expected: hundreds to thousands), well above any statistical threshold.
- **Statistical test:** Chi-squared on 2×2 contingency table (AI→HCI count, AI→AI count, HCI→AI count, HCI→HCI count). Standard scipy.stats.chi2_contingency. No custom benchmarks or rubrics needed.
- **No feasibility blockers:** All data exists now, all methods are standard, all code is <100 lines of Python.

---

## Phase 1 Input Package

<phase1-input>

### research_question

Using directed citation links from the Semantic Scholar Academic Graph (S2AG) for papers in the huashen218/bidirectional-alignment-reading-list corpus, is the cross-group citation ratio (AI-centered alignment papers citing HCI-centered alignment papers vs. HCI-centered citing AI-centered) significantly asymmetric — and does this asymmetry differ across pre-2022 and post-2022 publication cohorts?

### detailed_question

1. For papers in the huashen218 alignment corpus classified as AI-centered (ML/NLP venues: NeurIPS/ICML/ICLR/ACL/EMNLP) vs. human-centered (HCI venues: CHI/CSCW/IUI) using Semantic Scholar venue metadata, what fraction of cross-group citation edges are directed AI→HCI vs. HCI→AI?
2. Is this cross-citation asymmetry statistically significant (chi-squared or Fisher's exact test on the 2×2 directed citation adjacency table using existing S2AG data)?
3. Does the citation asymmetry ratio change across publication cohorts (pre-2022 vs. post-2022), suggesting convergence or divergence over time?
4. Is within-group citation density (AI→AI, HCI→HCI) significantly higher than cross-group density, consistent with community siloing?
5. Are there specific bridge papers (high betweenness centrality) connecting the two communities, and are they disproportionately from ML/NLP or HCI?

### reference_papers

- huashen218/bidirectional-alignment-reading-list (GitHub) — primary corpus (~400 interdisciplinary alignment papers with venue metadata)
- Semantic Scholar Academic Graph (S2AG) — citation data, papers API, references/citations endpoints
- Shen et al. 2024 (arXiv:2406.09264) — anchor bridge paper identified in previous attempts
- ICLR 2025 Workshop on Bidirectional Human-AI Alignment CFP — bidirectional taxonomy definition

</phase1-input>

---

## Session Insights

### Key Discoveries

- Previous failures expose a structural pattern: any approach that (a) relies on an ML-centric seed corpus to define "alignment" semantics, or (b) requires cross-corpus overlap for statistical testing will fail on this topic because the two alignment communities (ML/NLP and HCI) are structurally distinct literatures.
- Citation network analysis sidesteps both issues: citation edges are objective metadata, the corpus is unified (huashen218 + S2AG), and classification uses venue labels rather than semantic similarity.
- The reversed direction in h-m1 (ML > HCI on "alignment framing") is actually consistent with the citation directionality hypothesis: if ML papers define the "alignment" semantic space, they will score higher on ML-derived metrics AND may cite HCI papers less. Both observations could be two sides of the same asymmetry.

### Techniques Used

ROUTE_TO_0 Auto-Fill — failure root-cause elimination method. Systematically ruled out SPECTER2 embeddings, cross-corpus correlation, and keyword frequency approaches based on documented failure modes. Selected citation network directionality as structurally orthogonal operationalization.

### Areas for Further Exploration

- Whether the citation asymmetry persists when controlling for paper age (newer HCI papers may not yet be cited)
- Whether ACL/EMNLP papers (NLP — closer to HCI than pure ML) show intermediate citation behavior
- Whether Responsible AI / AI Ethics venues (FAccT, AIES) serve as bridge communities
- Whether the asymmetry is stronger for specific alignment subtopics (value alignment vs. explainability vs. RLHF)

---

## Next Steps

Proceed to Phase 1 - Targeted Research. Use `/phase1-targeted` with the research_question and detailed_question above. Focus Phase 1 literature search on: (1) bibliometric studies of HCI/ML citation patterns, (2) existing analyses of the huashen218 corpus or similar alignment reading lists, (3) citation network methodology papers for cross-community analysis.

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm*
*Ready for: Phase 1 - Targeted Research*

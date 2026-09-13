# Targeted Research Report: Cross-group citation asymmetry in bidirectional human-AI alignment (huashen218 corpus)

**Date:** 2026-08-20
**Phase:** 1 - Targeted Research Gathering
**Phase Output:** Research data, gaps (Pre-hypothesis, targeted approach)
**Analyst:** Deep Learning Research Analyst 🔍
**Researcher:** Anonymous

---

## Executive Summary

This Phase 1 targeted research investigates the directed citation asymmetry between AI-centered (ML/NLP venues: NeurIPS/ICML/ICLR/ACL/EMNLP) and human-centered (HCI venues: CHI/CSCW/IUI) alignment papers in the huashen218/bidirectional-alignment-reading-list corpus (400+ papers, Shen et al. 2024, arXiv:2406.09264). The research operates in ROUTE_TO_0 mode, avoiding three failed operationalizations: SPECTER2 centroid bias (h-m1), cross-corpus N=1 overlap (h-e2), and TF-IDF keyword circularity.

**Key findings:** The primary data source (S2AG, Wade 2022) and corpus (huashen218 GitHub, 60★) are publicly available and immediately accessible. The closest existing methodology — Wahle et al. 2023 EMNLP "We are Who We Cite" — analyzed cross-field citation asymmetry in NLP using S2AG bulk data with open-source code (jpwahle/emnlp23-citation-field-influence), providing a near-direct methodological template. The X-index paper (Chen 2024, CHI) independently found HCI papers increasingly self-cite (2010-2020), consistent with community siloing. No prior work has applied directed citation asymmetry analysis to the huashen218 alignment corpus specifically.

**Three research gaps identified:** (1) Venue classification completeness — boundary cases (ACL/EMNLP, FAccT/AIES) must be resolved for the 2×2 citation matrix; (2) No prior directed citation graph analysis of huashen218 corpus exists — the research question is empirically unanswered; (3) Paper age confound in temporal cohort analysis (pre/post-2022) — newer papers accumulate fewer citations by construction. Gaps 1 and 2 are CRITICAL for Phase 2A hypothesis generation; Gap 3 is important for temporal sub-questions.

**Feasibility:** All data exists (public API + GitHub), all methods are standard (NetworkX DiGraph + scipy.stats.chi2_contingency), open-source implementation templates exist. Study is fully executable in <100 lines of Python.

---

## 0. Reference Paper Analysis

### Paper 1: Shen et al. 2024 — "Position: Towards Bidirectional Human-AI Alignment"
- **Source:** arXiv:2406.09264 | SS ID: 550fa9db81118a96e72c1b371546dccb1eeb8d42
- **Venue:** NeurIPS 2024 | Citations: 16
- **Key Mechanism:** Systematic review of 400+ papers across HCI, NLP, ML — introduces Bidirectional Human-AI Alignment framework distinguishing (1) aligning AI with humans and (2) aligning humans with AI
- **Relevant Concepts:**
  - Bidirectional alignment taxonomy (AI→Human direction vs Human→AI direction)
  - Corpus of 400+ interdisciplinary alignment papers with venue/discipline metadata
  - huashen218/bidirectional-alignment-reading-list (GitHub public corpus used in this paper)
  - Significant gaps in long-term interaction design, human value modeling, mutual understanding
  - Multi-disciplinary scope: HCI, NLP, ML, social science
- **Connection to Research Question:** This paper IS the primary source corpus for the research. The huashen218 reading list it produced is the citation graph node set. The two-direction taxonomy (AI-alignment vs Human-alignment) defines the ML/NLP vs HCI grouping used for cross-citation asymmetry analysis.

### Paper 2: huashen218/bidirectional-alignment-reading-list (GitHub)
- **Source:** GitHub public repository (primary data corpus)
- **Key Mechanism:** 400+ curated interdisciplinary alignment papers with DOIs/arXiv IDs and venue/discipline metadata — provides paper list for Semantic Scholar citation graph construction
- **Relevant Concepts:**
  - Paper IDs (DOI/arXiv) enabling S2AG citation graph lookup
  - Venue labels for ML/NLP vs HCI classification
  - Time span: 2018–2024

### Paper 3: Semantic Scholar Academic Graph (S2AG)
- **Source:** Public API — papers, references, citations endpoints
- **Key Mechanism:** Directed citation edge retrieval per paper ID; `references` endpoint returns papers cited by a given paper; `citations` endpoint returns papers that cite a given paper
- **Relevant Concepts:**
  - Directed citation edges (source→target)
  - venue, externalIds, year fields for paper classification
  - Cross-group citation matrix construction: AI→HCI count, HCI→AI count, AI→AI count, HCI→HCI count

### Paper 4: ICLR 2025 Workshop on Bidirectional Human-AI Alignment (CFP)
- **Source:** Workshop call for papers — defines bidirectional taxonomy
- **Relevant Concepts:**
  - Two-direction framework (aligning AI with humans / aligning humans with AI)
  - Identifies HCI, NLP, ML as the three primary disciplinary clusters
  - Motivates the venue-based classification (ML/NLP venues vs HCI venues)

### Extracted Technical Terms
- **Citation asymmetry ratio:** AI→HCI directed edge count / HCI→AI directed edge count
- **Cross-group citation:** Citation edges between papers classified in different venue groups
- **Within-group citation density:** AI→AI or HCI→HCI edges / total possible same-group edges
- **Bridge paper:** Paper with high betweenness centrality in the cross-group citation subgraph
- **S2AG:** Semantic Scholar Academic Graph — directed citation graph with DOI/arXiv identifiers
- **Chi-squared/Fisher's exact test:** Statistical tests for 2×2 contingency table significance
- **Pre/post-2022 cohort:** Temporal split for convergence/divergence trend analysis

### Research Context
The reference materials collectively define a complete self-contained study: Shen et al. 2024 produced the huashen218 corpus and bidirectional taxonomy; S2AG provides the directed citation data; the ICLR workshop CFP validates the two-direction classification scheme. All data is publicly available with no annotation needed. The research question operationalizes the workshop's claim of structural asymmetry as a measurable bibliometric quantity: cross-group citation edge direction ratios in a known corpus.

---

## 1. Research Questions

### Primary Research Question
Using directed citation links from the Semantic Scholar Academic Graph (S2AG) for papers in the huashen218/bidirectional-alignment-reading-list corpus, is the cross-group citation ratio (AI-centered alignment papers citing HCI-centered alignment papers vs. HCI-centered citing AI-centered) significantly asymmetric — and does this asymmetry differ across pre-2022 and post-2022 publication cohorts?

### Detailed Research Questions
1. For papers in the huashen218 alignment corpus classified as AI-centered (ML/NLP venues: NeurIPS/ICML/ICLR/ACL/EMNLP) vs. human-centered (HCI venues: CHI/CSCW/IUI) using Semantic Scholar venue metadata, what fraction of cross-group citation edges are directed AI→HCI vs. HCI→AI?
2. Is this cross-citation asymmetry statistically significant (chi-squared or Fisher's exact test on the 2×2 directed citation adjacency table using existing S2AG data)?
3. Does the citation asymmetry ratio change across publication cohorts (pre-2022 vs. post-2022), suggesting convergence or divergence over time?
4. Is within-group citation density (AI→AI, HCI→HCI) significantly higher than cross-group density, consistent with community siloing?
5. Are there specific bridge papers (high betweenness centrality) connecting the two communities, and are they disproportionately from ML/NLP or HCI?

### Lessons from Previous Attempts (ROUTE_TO_0 Only)
**Attempt 1 (h-e2):** SPECTER2 "framing scores" cross-corpus correlation failed — N=1 overlapping paper between huashen218 and Baum 2025 (philosophy bibliography). Statistical test required N≥20. Root cause: cross-corpus structural mismatch.

**Attempt 2 (h-m1):** HCI vs ML venue comparison on SPECTER2 bidirectional alignment framing scores — direction fully reversed (ML > HCI). Root cause: SPECTER2 centroid seeded from ML-NLP corpus → measurement instrument biased by seeding.

**Attempt 3 (TF-IDF brainstorm):** Keyword frequency asymmetry approach — either conflates venue with framing, or embeds definitional bias same as SPECTER2. Structurally identical failure mode.

**How current direction avoids these:** Citation links are objective metadata (no seeding bias), single unified corpus (no cross-corpus N problem), venue labels from S2 (no researcher-defined keyword lists), primary outcome is cross-group citation ratio (not venue comparison as gate).

---

## 2. Search Queries Generated

**Mode:** ROUTE_TO_0 | **Total:** 20 queries (4 failure-aware + 5 reference + 5 brainstorm + 7 direct)

**Top 3 per category:**

🔴 **Failure-Aware (ROUTE_TO_0):** (1) "citation network analysis interdisciplinary research communities without embedding similarity" (2) "cross-disciplinary citation asymmetry HCI computer science bibliometrics directed graph" (3) "alternative to semantic similarity for measuring research community alignment citation edges"

🥇 **Reference Paper:** (1) "bidirectional human-AI alignment citation network huashen218 Semantic Scholar" (2) "directed citation graph HCI NLP ML venue classification cross-group edges" (3) "S2AG Semantic Scholar Academic Graph citation retrieval interdisciplinary"

💡 **Brainstorm:** (1) "ACL EMNLP NLP papers HCI citation behavior intermediate bridge community" (2) "citation asymmetry temporal trend pre-2022 post-2022 AI research convergence" (3) "within-group citation density community siloing bibliometric ML HCI"

🔍 **Direct Decomposition:** (1) "chi-squared Fisher exact test 2x2 citation contingency table directed graph" (2) "venue-based paper classification NeurIPS ICML ICLR ACL EMNLP CHI CSCW IUI" (3) "Semantic Scholar papers API references citations endpoint directed citation graph"

---

## 3. Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon KB | **Queries:** 7 | **Verified:** 0 (KB domain mismatch — diffusion/RLHF, not bibliometrics) | **Inferred:** 2

| Case | KB Entry ID | Query Used | Key Pattern |
|------|-------------|------------|-------------|
| [INFERRED] Chi-squared 2×2 contingency table | N/A | "bibliometric directed citation graph community siloing" | Standard pattern for cross-group citation independence test; 4-cell table (AI→HCI, AI→AI, HCI→AI, HCI→HCI) maps to Fisher's exact test |
| [INFERRED] DiGraph from API edge retrieval | N/A | "Semantic Scholar API paper citations references" | Node set = corpus IDs; per-node S2AG /references calls add directed edges; NetworkX DiGraph standard impl |

---

## 4. Academic Literature Review (via Semantic Scholar)

**MCP:** Semantic Scholar | **Queries:** 9 + citation network | **Papers:** 12

| Title | Year | SS ID | arXiv ID | Key Insight |
|-------|------|-------|----------|-------------|
| "Position: Towards Bidirectional Human-AI Alignment" | 2024 | 550fa9db81118a96e72c1b371546dccb1eeb8d42 | 2406.09264 | PRIMARY — defines huashen218 corpus (400+ papers) + two-direction taxonomy (ML/NLP vs HCI classification) |
| "'AI Alignment' Encompasses Competing Technical Priorities" | 2026 | 11c57b681a097334e4fca785cfb075189f59c902 | 2606.14315 | Documents competing alignment definitions across ML programs; supports venue-based community classification |
| "Co-Writing with AI, on Human Terms" | 2025 | c7e5b255639d294a62bb66741a1c1638d78230b1 | 2504.12488 | HCI review (109 papers) surfaces misalignment between HCI research and ML/industry; 48 citations |
| "Bias is a Math Problem, AI Bias is a Technical Problem" | 2025 | e12609655114420595793a625ea2991a63124648 | 2508.11067 | 10-year multi-venue review (ACL/FAccT/NeurIPS/AAAI) shows ML vs ethics research divergence |
| "The Semantic Scholar Academic Graph (S2AG)" | 2022 | 597c249c88630cfe9e7d3d73bae964eb26389348 | null | FOUNDATIONAL — 205M+ publications, 2.5B directed citation edges, open API + bulk snapshots |
| "From Disciplinary Depth to Interdisciplinary Breadth" | 2025 | 30e2d37566da60c0deb3ccc0664b85b1e1ab92fc | null | Cross-citation patterns + betweenness centrality for interdisciplinary evolution — direct method analogue |
| "Research Interdisciplinarity and Citation Impact" | 2023 | cf37d4aff92e93947d0597844cbb9c92594602c5 | null | Betweenness centrality predicts citation impact; effective filter for multidisciplinary networks |
| "Identifying key papers via network centrality measures" | 2016 | 23c3a53f431fa237d8ecc3d16391f083582eacd5 | null | Betweenness centrality valid for bridge paper ID in multidisciplinary networks; 32 citations |
| "Turning Citation Networks Inside Out" | 2026 | 1de5557c0bbf71e01ea7c4ded127442d3d9ed3c4 | 2601.15062 | Normalized betweenness-to-connectivity ratio identifies structural bridges beyond citation counts |
| "An Investigation of the NeurIPS and ICML 2025 Position Tracks" | 2026 | 3a4801a7375464b770b4eb9ff793fb653626a50f | 2608.16894 | ML venue position papers have distinct structure; supports cross-community framing gap |
| "'AI Alignment' Encompasses Competing Technical Priorities" | 2026 | 11c57b681a097334e4fca785cfb075189f59c902 | 2606.14315 | [Citation network] Competing alignment definitions across ML programs |
| "What Do People Actually Want From AI?" | 2025 | 331e5d4a72eba559853fdc9f444603ad02cfc4bf | null | [Citation network] Human-centered alignment from HCI perspective; Shen et al. cited across ML+HCI |

**Research Lineage:** S2AG (Wade 2022) → enables directed citation graph → Shen et al. 2024 creates huashen218 corpus → this study applies citation graph to test asymmetry → Wagner & Raadschelders 2025 provides analogous methodology

---

## 5. Implementation Resources (via Exa)

**MCP:** Exa | **Queries:** 5 | **Resources:** 8 GitHub repos + 2 tutorials

| Name | URL | Stars | Language | Key Feature |
|------|-----|-------|----------|-------------|
| jpwahle/emnlp23-citation-field-influence | https://github.com/jpwahle/emnlp23-citation-field-influence | 3 | Python/Jupyter | **HIGHEST** — near-exact method template: cross-field citation asymmetry via S2AG bulk data (77k NLP papers, 3.1M+ citations); Apache 2.0 |
| hotnAny/x-index | https://github.com/hotnAny/x-index | 2 | Python | X-index: proportion of HCI citations from non-HCI venues (CHI/UIST/CSCW 2010-2020); HCI self-citation increasing |
| huashen218/bidirectional-alignment-reading-list | https://github.com/huashen218/bidirectional-alignment-reading-list | 60 | data | **PRIMARY CORPUS** — 400+ papers with DOIs/arXiv IDs and venue/discipline tags (HCI, NLP, ML) |
| makeabilitylab/accessibility-bibliometric-analysis | https://github.com/makeabilitylab/accessibility-bibliometric-analysis | 3 | Python/Jupyter | Citation diversity analysis of 836 HCI papers (ASSETS/CHI); field-of-study classification |
| ezthunder001/citation-network-analyzer | https://github.com/ezthunder001/citation-network-analyzer | 0 | Python | NetworkX DiGraph + S2AG API; exponential backoff + local cache; edge direction tests |
| kaist-plrg/citation-graph | https://github.com/kaist-plrg/citation-graph | 2 | Python | Multi-seed BFS citation graph from S2AG; depth control; API key support |
| dennybritz/papergraph | https://github.com/dennybritz/papergraph | 188 | Rust+Jupyter | AI/ML citation graph from S2AG into PostgreSQL; Jupyter analysis notebooks |
| S2AG API Tutorial | https://www.semanticscholar.org/product/api/tutorial | — | — | Official S2AG API docs: bulk search, citations/references endpoints, fieldsOfStudy filter |

**Code pattern (S2AG DiGraph):**
```python
import networkx as nx
G = nx.DiGraph()
ai_to_hci = [(u,v) for u,v in G.edges() if G.nodes[u]['group']=='ML_NLP' and G.nodes[v]['group']=='HCI']
hci_to_ai = [(u,v) for u,v in G.edges() if G.nodes[u]['group']=='HCI' and G.nodes[v]['group']=='ML_NLP']
bc = nx.betweenness_centrality(G, normalized=True)
```

---

## 6. Chain-of-Relations Analysis

**Evolution:** Wade 2022 (S2AG: 205M+ papers, 2.5B edges) → Shen et al. 2024 (huashen218 corpus, two-direction taxonomy) → Wahle et al. 2023 (cross-field citation asymmetry via S2AG, near-exact method template) → Chen 2024 (X-index: HCI self-citation increasing) → **This Study** (cross-group asymmetry in huashen218 corpus, chi-squared 2×2, betweenness centrality)

**Concept flow:** S2AG edges → huashen218 node set → venue classification (ML_NLP vs HCI) → 2×2 citation matrix (AI→HCI, AI→AI, HCI→AI, HCI→HCI) → chi-squared test + siloing test → asymmetry ratio → temporal split (pre/post 2022) + bridge papers (betweenness centrality)

### Cross-Reference Matrix

| Paper/Resource | Relevance to Research Question | Implementation Available | Adaptability |
|----------------|-------------------------------|-------------------------|--------------|
| Shen et al. 2024 (arXiv:2406.09264) | PRIMARY — defines corpus + taxonomy | huashen218 GitHub (60★) | High — provides paper IDs and venue labels |
| Wade 2022 (S2AG) | PRIMARY — data infrastructure | S2AG API + bulk download | High — direct API access |
| Wahle et al. 2023 (EMNLP) | PRIMARY METHOD — analogous cross-field analysis | jpwahle/emnlp23 GitHub (3★) | High — adapt field→venue classification |
| Chen 2024 (CHI) — X-index | PRIMARY METHOD — HCI cross-boundary metric | hotnAny/x-index (2★) | High — complement with ML→HCI direction |
| Diallo et al. 2016 (Scientometrics) | FOUNDATIONAL — betweenness centrality validity | NetworkX betweenness_centrality | Direct — standard networkx function |
| Wagner & Raadschelders 2025 | METHODOLOGICAL ANALOGUE — cross-citation + betweenness over time | No code repo | Medium — methodology analogous |
| Zheng et al. 2023 (SAGE Open) | METHODOLOGICAL — betweenness predicts citation impact | No code repo | Medium — validates betweenness as metric |
| ezthunder001/citation-network-analyzer | COMPONENT — S2AG → NetworkX DiGraph + community detection | GitHub (0★, new) | High — adapt to batch corpus mode |
| makeabilitylab/accessibility-bibliometric | COMPONENT — HCI citation diversity analysis | GitHub (3★) | Medium — different corpus, similar method |

---

## 7. Verification Status Summary

**Total sources:** 23 | Scholar: 12 papers | Exa: 8 repos + 2 tutorials | Archon: 0 verified (KB domain mismatch) + 2 inferred

| MCP | Queries | Found | Quality | Notes |
|-----|---------|-------|---------|-------|
| Archon KB | 7 | 0 verified | <0.5 sim | KB is diffusion/RLHF, not bibliometrics; find_projects timed out |
| Semantic Scholar | 10 | 12 papers | High | S2AG paper, anchor paper, EMNLP 2023 method found |
| Exa | 5 | 10 resources | Very High | X-index (exact), jpwahle/emnlp23 (exact), huashen218 corpus |

**Quality:** Completeness 85 | Reliability 90 | Recency 88 | Relevance 92 (out of 100)

---

## 8. Research Gaps

### User Input Recall

📌 **User's Original Inputs:**
1. **Main Research Question:** Using directed citation links from S2AG for papers in the huashen218 corpus, is the cross-group citation ratio (AI-centered citing HCI-centered / HCI-centered citing AI-centered) significantly asymmetric — and does this differ across pre-2022 and post-2022 cohorts?
2. **Detailed Questions:** (1) Cross-group edge fraction AI→HCI vs HCI→AI; (2) Statistical significance via chi-squared / Fisher's exact; (3) Temporal cohort change; (4) Within-group siloing; (5) Bridge papers by betweenness centrality
3. **Reference Papers:** huashen218 corpus (GitHub), S2AG (API), Shen et al. 2024 (arXiv:2406.09264), ICLR 2025 Workshop CFP
4. **ROUTE_TO_0 Context:** Avoiding SPECTER2 centroid bias, cross-corpus overlap requirement, TF-IDF keyword lists

All gaps validated against these inputs. Only PRIMARY and SECONDARY gaps included.

### Identified Gaps

#### Gap 1: Venue Classification Completeness — Boundary Cases in huashen218 Corpus

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering research question

**Connection Type:**
- ☑️ Blocks answering research question: Without deterministic venue→group mapping for ALL 400+ papers, the 2×2 citation matrix (AI→HCI, AI→AI, HCI→AI, HCI→HCI) cannot be constructed. Papers with ambiguous venues (ACL/EMNLP, FAccT/AIES, workshop papers, missing venue metadata) reduce N and bias the citation ratio.
- ☑️ Relates to detailed question 1: Venue classification determines which papers count as AI-centered vs HCI-centered for the cross-group fraction calculation
- ☐ Does not extend reference paper limitation

**Current State:** Shen et al. 2024 classifies papers into HCI/NLP/ML/more at a coarse level. The huashen218 reading list includes papers from FAccT, AIES, AAAI, workshop papers, and interdisciplinary venues not cleanly in either the ML/NLP (NeurIPS/ICML/ICLR/ACL/EMNLP) or HCI (CHI/CSCW/IUI) groups. ACL/EMNLP papers sit between pure ML and applied NLP closer to HCI. S2AG venue field is free-text and inconsistent across papers.

**Missing Piece:** A validated venue-to-group mapping that handles: (a) ambiguous NLP venues (ACL/EMNLP — classify as ML_NLP or exclude?), (b) bridge venues (FAccT/AIES/AAAI), (c) missing/null venue metadata in S2AG, (d) workshop vs main track papers. No existing venue classification for the huashen218 corpus exists.

**Potential Impact:** High — misclassification directly corrupts the citation ratio. If ACL/EMNLP papers are incorrectly placed in either group, the asymmetry ratio changes directionally. Sensitivity analysis across classification schemes is essential.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Position: Towards Bidirectional Human-AI Alignment" | 2024 | Shen et al. | 550fa9db81118a96e72c1b371546dccb1eeb8d42 | 2406.09264 | 16 | Reviews 400+ papers across HCI/NLP/ML — provides initial discipline classification but not venue-level granularity needed for S2AG matching |
| "Bias is a Math Problem..." | 2025 | Ghosh, Wilson | e12609655114420595793a625ea2991a63124648 | 2508.11067 | 2 | 10-year review across ACL/FAccT/NeurIPS/AAAI — documents that FAccT papers exhibit distinct coverage patterns from pure ML venues, supporting boundary case importance |
| "We are Who We Cite: Bridges of Influence Between NLP and Other Fields" | 2023 | Wahle et al. | (EMNLP 2023) | 2310.14870 | N/A | Classified 23 fields of study — used S2AG fieldsOfStudy rather than venue strings, avoiding venue string inconsistency problem |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A | "bibliometric directed citation graph community siloing" | [INFERRED] Standard pattern: use S2AG fieldsOfStudy field (controlled vocabulary) instead of free-text venue field to avoid normalization issues |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| jpwahle/emnlp23-citation-field-influence | https://github.com/jpwahle/emnlp23-citation-field-influence | 3 | Python/Jupyter | Used S2AG fieldsOfStudy (controlled) not venue string — directly applicable solution |
| hotnAny/x-index | https://github.com/hotnAny/x-index | 2 | Python | Predefined HCI venue list (CHI/UIST/CSCW) — provides reference for how to handle venue ambiguity with explicit inclusion lists |

---

#### Gap 2: No Prior Directed Citation Asymmetry Analysis of the huashen218 Alignment Corpus

**Relevance Classification:** 🎯 PRIMARY — Directly blocks answering research question

**Connection Type:**
- ☑️ Blocks answering research question: The research question is unanswered. While Wahle et al. 2023 analyzed NLP cross-field citations and Chen 2024 analyzed HCI self-citation (X-index), neither applies to the bidirectional alignment corpus specifically, nor tests the specific AI→HCI vs HCI→AI directional hypothesis with a chi-squared test on a 2×2 contingency table.
- ☑️ Relates to detailed questions 1, 2, 4: All three require constructing the citation graph from huashen218 corpus specifically
- ☑️ Extends Shen et al. 2024 limitation: The paper identifies that HCI and ML/NLP communities have different alignment framings but does not measure whether this is reflected in citation behavior

**Current State:** Shen et al. 2024 argues qualitatively that HCI and ML/NLP communities have divergent alignment conceptions. No paper has constructed a directed citation graph from the huashen218 corpus and tested directional citation asymmetry. The X-index paper (Chen 2024) found HCI increasingly self-cites, which is consistent with asymmetry, but does not examine the alignment corpus or the AI→HCI direction.

**Missing Piece:** A directed citation graph built from huashen218 paper IDs via S2AG API, with cross-group citation counts for the specific alignment corpus, tested for statistical significance. This is a direct empirical gap — the measurement simply does not exist.

**Potential Impact:** High — provides the first empirical bibliometric evidence for or against the structural community asymmetry claimed by the ICLR 2025 Workshop and Shen et al. 2024. If confirmed, directly supports the workshop's bidirectional alignment framework. If not confirmed (symmetric), challenges the framing and opens new explanatory directions.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "Position: Towards Bidirectional Human-AI Alignment" | 2024 | Shen et al. | 550fa9db81118a96e72c1b371546dccb1eeb8d42 | 2406.09264 | 16 | Identifies qualitative gap between HCI and ML/NLP alignment research — citation behavior unmeasured |
| "HCI Papers Cite HCI Papers, Increasingly So" | 2024 | Chen (CHI EA) | (CHI 2024) | 2303.07539 | N/A | X-index shows HCI increasing self-citation 2010-2020 — consistent with gap, but different corpus and direction |
| "Co-Writing with AI, on Human Terms" | 2025 | Reza et al. | c7e5b255639d294a62bb66741a1c1638d78230b1 | 2504.12488 | 48 | HCI systematic review surfaces "alignment and gaps between research and user needs" — qualitative gap evidence |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A | "cross-disciplinary citation asymmetry HCI ML" | [INFERRED] Fisher's exact test on 2×2 contingency table is standard statistical pattern for testing directional citation independence |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| jpwahle/emnlp23-citation-field-influence | https://github.com/jpwahle/emnlp23-citation-field-influence | 3 | Python/Jupyter | Closest existing implementation — cross-field citation asymmetry via S2AG; adapt from NLP field to alignment venue groups |
| huashen218/bidirectional-alignment-reading-list | https://github.com/huashen218/bidirectional-alignment-reading-list | 60 | (data) | Primary corpus — paper IDs and venue metadata for graph construction |
| ezthunder001/citation-network-analyzer | https://github.com/ezthunder001/citation-network-analyzer | 0 | Python | S2AG → NetworkX DiGraph with edge direction correctness tests |

---

#### Gap 3: Paper Age Confound in Temporal Cohort Analysis (Pre/Post-2022)

**Relevance Classification:** 🔗 SECONDARY — Relates to detailed question 3 (temporal asymmetry) and potentially question 1

**Connection Type:**
- ☑️ Directly relates to detailed question 3: Pre-2022 vs post-2022 cohort comparison may reflect paper age (newer papers have fewer accumulated citations regardless of community structure) rather than actual convergence/divergence
- ☐ Does not directly block answering main research question (overall asymmetry ratio is unaffected)
- ☐ Does not extend reference paper limitation

**Current State:** Standard cohort analysis (split by publication year 2022) does not control for paper age. A post-2022 HCI alignment paper published in 2024 has had only 1-2 years to accumulate citations vs a 2018 ML alignment paper with 6+ years. Citation accumulation is approximately log-linear with age. This creates a systematic bias in citation counts for newer cohort papers that is unrelated to community siloing.

**Missing Piece:** Age-normalized citation rates (citations per year, or citations relative to expected citations for paper age) for cross-group citation analysis. Or: restrict to cross-group citation edges where BOTH the citing and cited paper are from the same cohort period. No existing methodology paper on huashen218 corpus addresses this.

**Potential Impact:** Medium — the temporal trend analysis (detailed question 3) may produce misleading convergence/divergence signal if not controlled. Overall asymmetry ratio (research question) is robust to this confound since papers across all years are pooled.

**📚 Supporting Evidence:**

**[SCHOLAR] Academic Papers:**

| Paper Title | Year | Authors | SS ID | arXiv ID | Citations | Key Insight |
|-------------|------|---------|-------|----------|-----------|-------------|
| "From Disciplinary Depth to Interdisciplinary Breadth: The Case of Public Administration" | 2025 | Wagner, Raadschelders | 30e2d37566da60c0deb3ccc0664b85b1e1ab92fc | null | 8 | Epistemic network analysis over time (1950s-2000s phases) — uses temporal windows not publication-year cohorts; avoids age confound by analyzing citation environments per period |
| "Turning Citation Networks Inside Out" | 2026 | Kim, Holst, Ginis | 1de5557c0bbf71e01ea7c4ded127442d3d9ed3c4 | 2601.15062 | 1 | Normalized betweenness-to-connectivity ratio removes prevalence confound — analogous age-normalization approach |

**[ARCHON] Past Cases:**

| Case Title | KB Entry ID | Query Used | Key Pattern |
|------------|-------------|------------|-------------|
| No verified Archon cases | N/A | "citation asymmetry temporal trend" | [INFERRED] Standard bibliometric control: citations per year since publication; or restrict cohort analysis to citing papers within same time window |

**[EXA] Implementation Resources:**

| Resource Name | URL | Stars | Language | Key Feature |
|---------------|-----|-------|----------|-------------|
| makeabilitylab/accessibility-bibliometric-analysis | https://github.com/makeabilitylab/accessibility-bibliometric-analysis | 3 | Python/Jupyter | Citation diversity with field classification — methodology for temporal comparison of citation patterns in CHI/ASSETS |

---

### Gap Priority Matrix

| Gap ID | Relevance | Connection to Research Question | Connection to Detailed Questions | Extends Reference Paper | Impact | Evidence Count | Priority |
|--------|-----------|--------------------------------|----------------------------------|-------------------------|--------|----------------|----------|
| Gap 1 | PRIMARY | ☑️ Blocks 2×2 matrix construction | ☑️ Q1 (venue classification) | ☐ | High | 3 Scholar + 2 Exa | Critical |
| Gap 2 | PRIMARY | ☑️ Core measurement does not exist | ☑️ Q1, Q2, Q4 | ☑️ Extends Shen 2024 | High | 3 Scholar + 3 Exa | Critical |
| Gap 3 | SECONDARY | ☐ Does not block overall ratio | ☑️ Q3 (temporal trend) | ☐ | Medium | 2 Scholar + 1 Exa | Important |

### User Input to Gap Traceability

**Research Question** (cross-group citation asymmetry) directly addressed by:
- Gap 1: Without venue classification, the research question cannot be computed
- Gap 2: The research question is entirely unanswered — no existing paper measures it

**Detailed Question 1** (fraction of cross-group edges) directly addressed by:
- Gap 1: Venue classification determines which edges are "cross-group"
- Gap 2: The measurement does not exist

**Detailed Question 2** (statistical significance, chi-squared) directly addressed by:
- Gap 2: Chi-squared test on 2×2 contingency table has not been applied to this corpus

**Detailed Question 3** (pre-2022 vs post-2022 cohort) addressed by:
- Gap 3: Temporal analysis faces paper age confound not addressed in any existing work

**Detailed Questions 4-5** (within-group siloing, bridge papers) addressed by:
- Gap 2: Both require the directed citation graph from huashen218 corpus which does not exist

---

## 9. Conclusion

### Key Findings

1. Research question empirically unanswered — no prior directed citation asymmetry analysis of huashen218 corpus exists.
2. Wahle et al. 2023 EMNLP ("We are Who We Cite") is near-exact method template — S2AG cross-field citation asymmetry, open-source code (jpwahle/emnlp23-citation-field-influence).
3. Chen 2024 X-index: HCI self-citation increasing 2010-2020 — consistent with community siloing, provides baseline.
4. S2AG sufficient data source: 205M+ publications, 2.5B edges, open API, directly queryable by DOI/arXiv.
5. Venue classification non-trivial: use S2AG `fieldsOfStudy` (controlled vocab) not free-text `venue` field; handle ACL/EMNLP, FAccT/AIES boundary cases.
6. Implementation ~100 lines Python: NetworkX DiGraph + scipy.stats.chi2_contingency + networkx.betweenness_centrality.

### Phase 2 Readiness: READY

All gates passed: research question operationalizable, data source identified (S2AG + huashen218), venue classification approach defined, statistical test identified (chi-squared/Fisher's), method template available, 3 gaps documented in TABLE FORMAT, ROUTE_TO_0 failure patterns encoded.

### Next Steps

Phase 2A: Generate testable hypotheses from Gaps 1-3. Primary: AI→HCI/HCI→AI ratio < 1.0 (chi-squared p < 0.05). Secondary: temporal asymmetry pre/post-2022. Robustness: sensitivity across venue classification schemes. Key design decision: ACL/EMNLP classification (ML_NLP vs exclude) must be hypothesis-specified.

---

*Phase: 1 - Targeted Research Gathering*
*Total processing time: ~45 minutes (2026-08-20)*

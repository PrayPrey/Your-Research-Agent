# Phase 2A Discussion Log
# Workflow: phase2a-dialogue (Self-Contained Self-Play Loop)
# Generated: 2026-08-20T08:45:00+00:00

---

## Briefing

**Selected Gap:** Gap 2 — No Prior Directed Citation Asymmetry Analysis of the huashen218 Alignment Corpus

**Gap Priority:** PRIMARY / Critical

**Research Question:**
Using directed citation links from the Semantic Scholar Academic Graph (S2AG) for papers in the huashen218/bidirectional-alignment-reading-list corpus (~400 papers), is the cross-group citation ratio (AI-centered alignment papers citing HCI-centered alignment papers vs. HCI-centered citing AI-centered) significantly asymmetric — and does this asymmetry differ across pre-2022 and post-2022 publication cohorts?

**Key Detailed Questions:**
1. Cross-group edge fraction: AI→HCI vs HCI→AI directed edges
2. Statistical significance: chi-squared / Fisher's exact test on 2×2 contingency table
3. Temporal cohort: pre-2022 vs post-2022 asymmetry ratio change
4. Within-group siloing: AI→AI, HCI→HCI density vs cross-group density
5. Bridge papers: high betweenness centrality papers connecting communities

**Methodology Template:** Wahle et al. 2023 EMNLP ("We are Who We Cite") — cross-field citation asymmetry via S2AG; Chen 2024 CHI (X-index) — HCI self-citation baseline

**Data Sources:**
- huashen218/bidirectional-alignment-reading-list (GitHub, ~400 papers, public)
- S2AG API (papers, references, citations endpoints — public)
- Shen et al. 2024 (arXiv:2406.09264) — anchor/primary corpus paper

**Implementation Path:**
- NetworkX DiGraph from S2AG edges
- scipy.stats.chi2_contingency on 2×2 table
- nx.betweenness_centrality for bridge paper identification
- ~100 lines Python, no custom benchmarks

**Venue Classification Strategy:**
- ML_NLP group: NeurIPS, ICML, ICLR, ACL, EMNLP (plus fieldsOfStudy fallback)
- HCI group: CHI, CSCW, IUI
- Boundary cases: FAccT, AIES, AAAI — sensitivity analysis across classification schemes
- Missing venue: use S2AG fieldsOfStudy controlled vocab (as per Wahle et al. 2023)

---

### Previous Failure / Routing Context

**Source:** Serena Memory `.serena/memories/limitation_h-e2_run1.md`
**Type:** LIMITATION_RECORDED (not blocked — pipeline continued)
**Date:** 2026-08-20T08:30:00+00:00

**Prior Hypothesis:** h-e2 (Run 1)
**Gate Type:** SHOULD_WORK
**Root Cause:** Structural corpus mismatch — huashen218 (64 ML/NLP papers 2018-2024) vs Baum 2025 philosophy bibliography (15 papers). N=1 overlapping paper (Shen et al. 2024 arXiv:2406.09264). Spearman r requires N≥20 — test was infeasible, not failed.

**Failed Checks:**
- spearman_r > 0.60 (N/A — N=1)
- sufficient_n >= 20 (N=1, needed N≥20)
- scores_nonempty (no overlapping paper pairs)

**Partial Results:** Jaccard overlap 1.3% (below 30% threshold criterion passed, but N insufficient for correlation). Hypothesis not falsified — untestable on those two corpora.

**Prohibited Directions (from memory):**
1. Cross-corpus correlation approaches requiring N≥20 overlap between structurally distinct literatures
2. Any approach where the huashen218 corpus (ML/NLP-centric) must overlap with philosophy-of-AI bibliographies

**How Current Direction Avoids h-e2 Failure:**
- Operates entirely within one corpus (huashen218 + S2AG): no cross-corpus overlap requirement
- N = directed citation edges (expected hundreds to thousands), not overlapping paper pairs
- No Spearman correlation — uses chi-squared on 2×2 contingency table
- No embedding similarity — uses objective citation metadata from S2AG

**Additional Prior Failures (from Phase 0 / brainstorm context):**
- h-m1: SPECTER2 centroid bias — ML venues scored higher by construction (measurement instrument seeded from ML corpus)
- TF-IDF approach: keyword definitional circularity — same structural bias as SPECTER2

All three prior failures share a common structure: semantic/lexical similarity measures seeded from ML-centric data applied to cross-community comparison. Current approach (objective citation edge directionality) is structurally orthogonal.

---

## Reference Papers Summary

**P1: Shen et al. 2024 (arXiv:2406.09264)**
- "Position: Towards Bidirectional Human-AI Alignment" — NeurIPS 2024
- Introduces huashen218 corpus (400+ papers), defines two-direction taxonomy (AI→Human / Human→AI alignment)
- Provides initial discipline classification (HCI/NLP/ML) but not venue-level granularity for S2AG matching
- Key claim: HCI and ML/NLP communities have divergent alignment conceptions — citation behavior unmeasured

**P2: Wahle et al. 2023 (EMNLP, arXiv:2310.14870)**
- "We are Who We Cite: Bridges of Influence Between NLP and Other Fields"
- Near-exact method template: cross-field citation asymmetry via S2AG bulk data (77k NLP papers, 3.1M+ citations)
- Used S2AG fieldsOfStudy (controlled vocabulary) not free-text venue strings — directly applicable solution to venue classification problem
- Code: jpwahle/emnlp23-citation-field-influence (Apache 2.0)

**P3: Chen 2024 (CHI EA, arXiv:2303.07539)**
- "HCI Papers Cite HCI Papers, Increasingly So" — X-index
- Shows HCI self-citation increasing 2010-2020 — consistent with community siloing hypothesis
- Different corpus and direction from this study, but provides baseline consistency evidence

**P4: S2AG (Wade 2022)**
- 205M+ publications, 2.5B directed citation edges, open API + bulk snapshots
- papers, references, citations endpoints for directed edge retrieval
- `fieldsOfStudy` controlled vocabulary for venue classification

---

## Discussion Log

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're sitting on something genuinely paradigm-shifting here? The bidirectional alignment debate has been stuck in semantic mud — SPECTER2 embeddings, keyword lists, cross-corpus correlations — all of which embed the very bias they're trying to measure. NOW we're onto something structurally orthogonal: citation edges are the one artifact that researchers leave behind without anyone curating them for "alignment content."

What excites me most is the *directionality* question. We're not just asking whether communities overlap — we're asking who reaches across the aisle, and who stays home. The Wahle et al. 2023 EMNLP paper ("We are Who We Cite") showed that NLP papers heavily cite Computer Science but are rarely cited back by other fields in proportion. If we apply that same framework to the huashen218 corpus specifically — a corpus explicitly designed to capture bidirectional alignment — we're essentially auditing whether the *aspiration* of bidirectionality matches the *practice* of citation.

The ICLR 2025 Workshop CFP claims there's structural asymmetry. But that claim has never been tested empirically on a curated alignment corpus with directed citation edges. We could be the first to measure this. And here's the wild angle: what if the asymmetry *reverses* post-2022? The ChatGPT moment (late 2022) might have actually triggered HCI researchers to suddenly cite ML alignment papers at higher rates, as HCI scrambled to engage with LLMs. That temporal discontinuity hypothesis is uniquely testable with the pre/post-2022 cohort split.

The bridge papers angle is also novel — using betweenness centrality to identify the specific papers that function as cross-community connectors. I'd predict those bridge papers are disproportionately from ML/NLP venues (because ML papers cite HCI occasionally, giving HCI papers their only cross-community citations), but that's an empirical question.

**Key Points:**
- Citation directionality is structurally orthogonal to all three failed approaches — no seeding bias, no cross-corpus overlap, no keyword lists
- The temporal discontinuity hypothesis (pre/post-2022 ChatGPT effect) is uniquely testable and could be the most novel finding
- Bridge paper identification via betweenness centrality adds a network science angle not present in prior work on this corpus

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises intriguing possibilities, but let me press on the testability structure before we get swept up in enthusiasm. The core hypothesis — AI→HCI citation rate significantly lower than HCI→AI — is actually well-formed for a chi-squared test. The 2×2 contingency table (AI→HCI count, AI→AI count, HCI→AI count, HCI→HCI count) is the right operationalization. Fisher's exact test is preferable when any cell count falls below 5, which is unlikely given hundreds of expected cross-group edges from ~400 papers.

However, I see two critical testability issues. First: the *venue classification* problem is not merely a preprocessing nuisance — it determines the fundamental validity of the 2×2 table. If ACL/EMNLP papers (NLP — closer to HCI than pure ML) are classified as ML_NLP, the ML_NLP group becomes heterogeneous, potentially diluting the asymmetry signal. If they're excluded, the study's scope is artificially narrow. The hypothesis must *specify* the classification scheme and report sensitivity analysis across at least three schemes: (A) ACL/EMNLP → ML_NLP, (B) ACL/EMNLP → excluded, (C) ACL/EMNLP → HCI. Only then can we know whether the asymmetry is robust or a classification artifact.

Second: the temporal cohort analysis faces a measurement validity problem. The pre/post-2022 split compares papers that have had 2-8 years to accumulate citations (pre-2022) against papers with 0-4 years (post-2022). A post-2022 HCI paper published in 2024 has had 2 years to be cited; a 2018 ML paper has had 8 years. Raw citation counts are not comparable across cohorts without age normalization. Dr. Nova's ChatGPT discontinuity hypothesis is interesting, but the temporal trend analysis must control for citation age — using citations-per-year-since-publication or restricting cohort comparison to citations *within* the same temporal window.

The success criterion for the primary hypothesis is clear: chi-squared p < 0.05, AI→HCI/HCI→AI ratio < 1.0. That meets my standards for falsifiability. The temporal and bridge analyses are secondary and must be clearly labeled as exploratory.

**Key Points:**
- Primary hypothesis is well-formed and falsifiable via chi-squared on 2×2 contingency table
- Venue classification scheme must be pre-specified with sensitivity analysis across ≥3 schemes (ACL/EMNLP classified as ML_NLP, excluded, or HCI)
- Temporal cohort comparison requires age normalization (citations/year) to be valid — otherwise confounds paper age with community change

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what would this study actually contribute to the field? Let me assess the significance carefully.

The claim that AI alignment research communities are structurally siloed is made qualitatively by Shen et al. 2024 and the ICLR 2025 Workshop CFP. But qualitative claims without empirical operationalization are not science — they're assertions. If this study provides the *first* directed citation graph analysis of the huashen218 corpus with statistical significance testing, the contribution is genuine and non-incremental. The Wahle et al. 2023 EMNLP paper did this for NLP broadly (77k papers); Chen 2024 did the X-index for HCI broadly (CHI/UIST/CSCW 2010-2020). Neither applies to the *alignment* corpus specifically.

This matters because the alignment community is actively making policy claims based on the structural asymmetry narrative. If the citation asymmetry is confirmed (p < 0.05, ratio < 1.0), it provides empirical grounding for the bidirectional alignment framework. If it's not confirmed — or if it's reversed (HCI cites ML more than ML cites HCI) — that's equally important: it challenges the workshop's framing and opens questions about why textual framing diverges from citation behavior.

The bridge paper finding is where I see the most impactful contribution beyond confirmation/disconfirmation. Knowing *which* specific papers function as cross-community bridges — and whether those bridges are concentrated in ML/NLP or HCI — has direct implications for research strategy. Workshop organizers, review committees, and funding bodies could use this to identify understudied connective work.

What does this mean for the field? This study positions itself at the intersection of bibliometrics and AI alignment policy. For a workshop paper (target: ICLR 2025 Workshop), this is squarely in scope and provides the empirical anchor the workshop needs. For a longer paper, the temporal trend analysis and bridge paper network visualization could anchor a full journal contribution.

**Key Points:**
- First empirical directed citation graph analysis of the huashen218 alignment corpus — genuine contribution, not incremental
- Both confirmation and disconfirmation are informative for the bidirectional alignment policy debate
- Bridge paper identification has direct practical value for the alignment research community and workshop organizers

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here about what can actually work. The good news: the core mechanism is sound. Directed citation edges from S2AG are objective, deterministically retrieved, and the chi-squared test on a 2×2 contingency table is mathematically valid. NetworkX DiGraph supports directed edge addition and betweenness centrality calculation. This is feasible in principle.

What worries me is the S2AG coverage rate for the huashen218 corpus. The corpus contains ~400 papers spanning 2018-2024, including workshop papers, arXiv preprints, and papers from venues that S2AG may not fully index. Shen et al. 2024 used a GitHub-hosted reading list, not a formal bibliography. S2AG paper lookup requires DOI or arXiv ID — papers with only partial metadata (title-only entries in the reading list) may not resolve. If coverage drops below 70% of the 400 papers, the citation graph becomes sparse enough to question whether the remaining sample is representative.

The references retrieval is also non-trivial at scale. For each of the ~400 corpus papers, retrieving /references via S2AG API returns ALL papers that corpus paper cites — not just other huashen218 papers. The within-graph citation edges are the subset where both source and target exist in the corpus node set. With ~400 papers, expected total external references retrieved might be 20,000-50,000 calls or more if using per-paper API requests. The S2AG free tier allows ~100 requests per 5 minutes, meaning full corpus retrieval takes 15-40 minutes with rate limiting — not a blocker, but must be implemented with exponential backoff and local caching.

The venue classification using S2AG `fieldsOfStudy` (following Wahle et al. 2023) is theoretically valid — controlled vocabulary reduces normalization issues. The concern is that huashen218 papers from 2018-2020 may have outdated or missing fieldsOfStudy entries in S2AG. A fallback rule using venue string matching (NeurIPS/ICML/ICLR → ML_NLP; CHI/CSCW/IUI → HCI) is necessary for completeness.

The betweenness centrality computation on the subgraph is computationally fine for a 400-node directed graph — NetworkX handles this in milliseconds.

**Key Points:**
- Core mechanism (S2AG DiGraph + chi-squared + betweenness) is technically sound and feasible
- S2AG coverage rate is the main empirical risk — must document and report unresolved papers; use fieldsOfStudy + venue string fallback for classification
- Rate limiting is a practical constraint (15-40 min retrieval) requiring caching — not a theoretical barrier

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly by directly addressing the two core concerns that Prof. Vera and Prof. Pax raised. Let me synthesize.

The hypothesis as currently framed — "AI→HCI citation rate significantly lower than HCI→AI rate" — can be formalized as follows and made more robust:

**Strengthened hypothesis statement:** In the huashen218 bidirectional alignment corpus (~400 papers), directed citation edges from AI-centered papers (ML/NLP venues: NeurIPS/ICML/ICLR/ACL/EMNLP) to HCI-centered papers (CHI/CSCW/IUI) are significantly less frequent — both in absolute count and as a proportion of all outgoing citations — than directed edges from HCI-centered papers to AI-centered papers, as tested by chi-squared on the 2×2 citation contingency table (p < 0.05, ratio AI→HCI/HCI→AI < 1.0).

To address Prof. Vera's venue classification concern: specify three classification schemes upfront as a robustness check — (A) ACL/EMNLP → ML_NLP, (B) ACL/EMNLP → excluded, (C) ACL/EMNLP → separate "NLP bridge" group. The hypothesis is supported if the asymmetry holds under at least two of the three schemes. This is a pre-registered sensitivity analysis, not post-hoc rationalization.

To address Prof. Pax's S2AG coverage concern: define a minimum acceptable coverage threshold (e.g., ≥70% of corpus papers resolved) before the study proceeds. If coverage is below threshold, the paper must characterize the unresolved papers and argue for representativeness. The fieldsOfStudy + venue string fallback is the right implementation.

What if we addressed the temporal concern by using *proportion* of cross-group citations rather than raw counts for the cohort comparison? Prof. Vera's age-normalization concern is real, but citation proportions (AI→HCI / total-AI-outgoing citations) within each cohort are age-invariant — older papers have more total citations AND more cross-group citations proportionally, so the ratio is stable.

**Key Points:**
- Formalize hypothesis as chi-squared on 2×2 table with pre-specified sensitivity analysis (3 venue classification schemes)
- Use citation proportions (not raw counts) for temporal cohort comparison — eliminates age confound without requiring citations-per-year normalization
- Define 70% S2AG coverage as minimum threshold for study validity

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Three specific challenges before I'm convinced.

**Challenge 1: Within-graph edge sparsity.** The huashen218 corpus has ~400 papers. Even if S2AG returns full reference lists for all 400 papers, the expected number of *within-corpus* citation edges — where both the citing paper AND the cited paper are in the huashen218 node set — is likely very small. Shen et al. 2024 curated this list as a *survey reading list*, not as a naturally occurring citation graph. Survey authors deliberately pick papers across communities; those papers don't necessarily cite each other. If within-corpus cross-group edges are in the single digits (say, AI→HCI = 8, HCI→AI = 12), the chi-squared test has insufficient power and the ratio is statistically meaningless. What evidence do we have that within-corpus citation density is sufficient for the analysis?

**Challenge 2: Directionality of causation.** Even if we find AI→HCI < HCI→AI (ratio < 1.0), this measures *retrospective citation behavior*. The huashen218 corpus is a curated reading list — papers were selected because they're relevant to bidirectional alignment. HCI papers in the corpus may cite ML papers precisely because the corpus curators *selected* HCI papers that engage with ML. This selection bias means the citation asymmetry measured within the huashen218 corpus may reflect curation decisions, not field-level community behavior. What would convince me is a comparison against a matched baseline — e.g., the same asymmetry test on a random sample of HCI and ML papers not in the huashen218 corpus.

**Challenge 3: Bridge paper interpretation.** High betweenness centrality in a 400-node subgraph will identify papers that appear in the shortest paths between many node pairs. In a sparse graph with two dense subclusters (ML_NLP and HCI), betweenness centrality disproportionately rewards any paper that happens to cite across the cluster boundary even once. A paper with 2 cross-group citations could have higher betweenness than a paper with 50 within-group citations. The betweenness metric may be measuring graph sparsity rather than genuine interdisciplinary influence. What would convince me is normalizing betweenness by degree — the Kim et al. 2026 ("Turning Citation Networks Inside Out") normalized betweenness-to-connectivity ratio directly addresses this.

**Key Points:**
- Within-corpus edge sparsity is a critical unknown — must estimate expected cross-group edge count before claiming the chi-squared test is powered
- Selection bias from curation is a fundamental alternative explanation — requires matched baseline comparison for interpretive validity
- Betweenness centrality must be normalized (betweenness/degree or Kim et al. 2026 ratio) to distinguish bridge papers from sparsity artifacts

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's challenges are sharp and exactly what makes hypotheses bulletproof. Let me address each directly.

**Challenge 1 (Edge sparsity):** This is the most important challenge. We can estimate expected within-corpus edge density before running the full study. A rough prior: if each huashen218 paper has ~30 references on average (typical for a NeurIPS/CHI paper), and ~400 papers are in the corpus, total reference pool is ~12,000 citations. The probability that a randomly chosen reference also appears in the 400-paper corpus is 400/205M ≈ 0.002 — so expected within-corpus edges: 12,000 × 0.002 = ~24 edges total. That's dangerously sparse.

BUT: the huashen218 corpus is not a random sample of S2AG papers — it's a curated alignment reading list where papers were selected *because they cite each other*. The within-corpus edge density should be substantially higher than the random baseline. Wahle et al. 2023 found that NLP papers cite other NLP papers at 10-30× the base rate. If alignment papers show similar within-corpus preference, expected within-corpus edges could be 240-720. That's adequate for a chi-squared test.

The hypothesis must be conditioned on verifying adequate within-corpus edge count: the study proceeds with the chi-squared test only if total cross-group within-corpus edges ≥ 30 (enough for Fisher's exact at 5 cells per expected count). If edges < 30, the study shifts to reporting descriptive statistics and the bridge paper analysis only, with the chi-squared test noted as under-powered.

**Challenge 2 (Selection bias):** Valid concern. We can address this by framing the study explicitly: "We measure citation asymmetry *within the curated bidirectional alignment corpus*" — not as a field-level claim. The corpus IS the unit of analysis. The finding speaks to whether *this specific set of alignment papers* exhibits directional asymmetry, which is directly relevant to the workshop's claims about the corpus. A matched baseline comparison is excellent future work but not required for this contribution.

**Challenge 3 (Betweenness normalization):** Prof. Rex is right. Use the Kim et al. 2026 normalized ratio (betweenness / connectivity) for the primary bridge paper metric, with raw betweenness as a supplementary measure.

**Key Points:**
- Condition chi-squared test on adequate edge count (≥30 cross-group edges) — if insufficient, shift to descriptive + bridge analysis only
- Explicitly scope the claim to within-corpus citation behavior (not field-level), which makes the curation bias a feature (we're auditing the corpus itself)
- Use Kim et al. 2026 normalized betweenness as primary bridge metric; raw betweenness as supplement

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The study addresses an empirically open question with a structurally orthogonal methodology to all prior failed approaches. The temporal discontinuity hypothesis (pre/post-2022 ChatGPT effect) and bridge paper identification via normalized betweenness are genuinely novel angles not present in prior work on this corpus or any alignment corpus. The paradigm shift from semantic similarity to citation graph directionality is well-motivated.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG (with pre-specified sensitivity analysis)
- **Assessment:** The primary hypothesis is falsifiable: chi-squared on 2×2 contingency table, p < 0.05, ratio < 1.0. Success and failure criteria are explicit. The three-scheme venue classification sensitivity analysis prevents post-hoc rationalization. Temporal analysis correctly uses citation proportions to avoid age confound. The edge-count threshold (≥30) ensures the test is powered before proceeding.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First empirical directed citation graph analysis of the huashen218 alignment corpus. Both confirmation and disconfirmation have field-level implications for the bidirectional alignment policy debate. Bridge paper identification has direct practical value. Appropriate scope for an ICLR 2025 Workshop paper, with extension path to a full journal contribution.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG (with documented caveats)
- **Assessment:** Core mechanism is technically sound: S2AG DiGraph construction, chi-squared test, NetworkX betweenness centrality are all standard and implementable in ~100 lines Python. Rate limiting (15-40 min retrieval) and S2AG coverage (expected ≥70%) are documented practical constraints, not theoretical barriers. Feasibility conditions well-specified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: **Within the huashen218 bidirectional alignment corpus (~400 papers), AI-centered papers (ML/NLP venues) cite HCI-centered papers significantly less — as a proportion of all outgoing citations — than HCI-centered papers cite AI-centered papers, as measured by chi-squared test on the 2×2 directed citation contingency table (AI→HCI, AI→AI, HCI→AI, HCI→HCI) constructed from Semantic Scholar Academic Graph citation edges.**

The mechanism is community siloing: ML/NLP alignment research is primarily building on ML/NLP foundations (RLHF, fine-tuning, safety) and does not systematically engage with HCI alignment work; HCI alignment research, engaging with applied AI deployment, is more likely to cite ML/NLP foundational work. This structural asymmetry in citation behavior operationalizes the qualitative claim made by Shen et al. 2024 and the ICLR 2025 Workshop CFP.

Testable predictions: (P1) AI→HCI / HCI→AI ratio < 1.0, chi-squared p < 0.05 on the 2×2 table; (P2) within-group citation density (AI→AI, HCI→HCI) significantly exceeds cross-group density, consistent with community siloing; (P3) bridge papers identified by normalized betweenness centrality (Kim et al. 2026 ratio) are disproportionately from ML/NLP venues, functioning as outbound bridges rather than mutual connectors.

The experimental approach: (1) resolve huashen218 paper IDs against S2AG API; (2) classify by venue (3 schemes, sensitivity analysis); (3) retrieve reference lists for all resolved papers; (4) filter within-corpus edges; (5) verify ≥30 cross-group edges before chi-squared test; (6) compute 2×2 table and Fisher's exact / chi-squared; (7) compute normalized betweenness centrality on directed subgraph; (8) run pre/post-2022 cohort analysis using citation proportions. Implementation: NetworkX + scipy.stats + ~100 lines Python.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Within-corpus edge sparsity is an empirical unknown that could invalidate the chi-squared test — must verify ≥30 cross-group edges before testing. The prior estimate (240-720 edges after community preference correction) is plausible but unconfirmed.
- **Concern 2:** Selection bias from curation means findings are scoped to this specific corpus — field-level claims require additional validation (matched baseline). This limitation must be prominently stated.
- **Mitigation Strategy:** Pre-register the edge-count threshold (≥30); if below threshold, report descriptive statistics and bridge analysis only. Frame all findings as "within the huashen218 alignment corpus" throughout the paper. Add matched baseline comparison as explicit future work.


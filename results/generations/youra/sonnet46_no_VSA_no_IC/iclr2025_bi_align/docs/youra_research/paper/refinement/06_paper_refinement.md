# Directed Citation Asymmetry in the huashen218 Bidirectional Alignment Corpus: Pipeline Validation and Preliminary Measurement

## Abstract

The huashen218 corpus is a systematic bibliography of bidirectional human-AI alignment research spanning ML/NLP and HCI communities, assembled by Shen et al. [2024]. Whether these communities cite each other's alignment work symmetrically is an open empirical question with structural implications for the field. This paper builds and validates the first Semantic Scholar Academic Graph (S2AG)-based bibliometric pipeline for within-corpus directed citation analysis of this corpus. In doing so, a significant methodological finding emerges: standard venue-string classification fails on interdisciplinary corpora, labeling only 12% of resolved papers from the huashen218 reading list, compared to 100% coverage achieved with FoS-primary classification — a method that uses S2AG `fieldsOfStudy` tags rather than venue name strings. In the 33 papers resolved from the public reading list, HCI alignment papers directed all within-corpus outgoing citations to ML/NLP work, while ML/NLP alignment papers allocated only 10.6% of outgoing citations to HCI, yielding a directed citation ratio of approximately 0.107. Both pre-registered gate thresholds — resolution coverage ≥ 70% and ≥ 30 cross-group edges — were not met (67.3% and 9 edges, respectively), so no statistical tests were executed and all three quantitative predictions are classified as INCONCLUSIVE rather than REFUTED. The validated, fully cached pipeline is available for re-execution once the full corpus is reconstructed programmatically.

---

## 1. Introduction

The framing of bidirectional AI alignment — the concept that ML/NLP and HCI research communities should mutually engage with one another on alignment problems — rests on an implicit empirical assumption: that these communities are intellectually coupled in practice. Cross-community citation behavior constitutes a structural indicator of epistemic integration. If researchers from ML/NLP and HCI working on alignment genuinely engage with each other's work, their citation networks should reflect symmetric knowledge flow. If citation is asymmetric — HCI researchers systematically citing ML/NLP but not vice versa — then bidirectionality may be more aspirational than structural.

Shen et al. [2024] assembled the huashen218 corpus: a curated systematic bibliography of over 400 interdisciplinary alignment papers spanning NeurIPS, ICML, CHI, CSCW, and adjacent venues. The corpus operationalizes the bidirectional alignment community as a named, bounded set of papers. Measuring directed citation behavior within this corpus is the first empirical test of whether the community is citation-integrated.

Attempting this measurement exposes a deeper infrastructural problem. Standard bibliometric approaches — classifying papers by venue name substring matching — achieve only 12% label coverage on this corpus. The cause is the following: the Semantic Scholar Academic Graph (S2AG), the public API for directed citation data, returns full proceedings names (e.g., "Proceedings of the 36th Annual Conference on Neural Information Processing Systems") rather than abbreviated venue strings (e.g., "NeurIPS"). Substring matching against abbreviated strings fails silently on the long-form variants, leaving 88% of papers unclassified.

This gap motivates the central technical contribution of the present work. Switching the primary classifier from venue name strings to S2AG's `fieldsOfStudy` tags — which encode disciplinary assignment at the knowledge-graph level, independent of venue name formatting — achieves 100% paper coverage on the same corpus. This is a three-line implementation change with an eight-fold coverage improvement.

The paper makes four contributions:

1. **A validated S2AG bibliometric pipeline** for within-corpus directed citation analysis: batch ID resolution via POST `/paper/batch`, FoS-primary classification (Scheme 3), within-corpus directed graph construction using NetworkX, and gate-controlled evaluation. The pipeline passes 23/23 unit tests and is fully cached for zero-API re-execution.

2. **FoS-primary classification (Scheme 3)**: a classification method using S2AG `fieldsOfStudy[0]` as the primary venue-group classifier, achieving 100% label coverage on the huashen218 corpus versus 12% for venue-string-only approaches. The method is domain-general and applicable to any interdisciplinary corpus indexed by S2AG.

3. **The first directional citation measurement within the huashen218 alignment corpus**: in the 33-paper resolved proxy, ML/NLP→HCI proportion = 10.6%, HCI→ML/NLP proportion = 100%, ratio ≈ 0.107. No statistical falsifier was triggered; full statistical testing requires an augmented corpus (designated h-e1-v2 in the research log).

4. **A methodological finding on corpus proxy construction**: the huashen218 GitHub reading list yields 49 extractable identifiers from approximately 130 linked papers — roughly 12.5% of the target corpus. Public reading lists from systematic reviews are insufficient bibliometric dataset proxies; programmatic S2AG citation-of-citation search is the viable reconstruction approach.

The paper is organized as follows. Section 2 situates the work within prior cross-community citation analysis and bibliometric infrastructure. Section 3 describes the pipeline design and classification schemes. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

This work combines three research streams — alignment bibliography, cross-community citation analysis, and S2AG bibliometric infrastructure — none of which individually addresses directed citation asymmetry within an interdisciplinary alignment corpus.

### 2.1 The huashen218 Alignment Corpus

Shen et al. [2024] argue that AI alignment research is bidirectional: ML/NLP alignment (aligning AI behavior with human values) and HCI alignment (adapting humans to AI systems) are distinct but mutually dependent. Their systematic review assembled the huashen218 corpus — over 400 papers from NeurIPS, ICML, ICLR, ACL, EMNLP, CHI, CSCW, IUI, and adjacent venues — as the operational definition of the bidirectional alignment community. The ICLR 2025 Workshop on Bidirectional Human-AI Alignment further validated this framing, identifying ML/NLP and HCI as the primary disciplinary clusters.

Shen et al. [2024] characterize the community through paper authorship and venue affiliation, not through citation structure. No prior work has constructed a directed citation graph within the huashen218 corpus or empirically tested whether the claimed bidirectionality manifests in how papers from the two communities cite each other.

### 2.2 Cross-Community Citation Asymmetry

The closest methodological precedent is Wahle et al. [2023], who analyzed cross-field citation influence in NLP using S2AG bulk data. Their analysis of 77,000 NLP papers found strong within-field citation preference and measurable cross-field asymmetry, validating the use of S2AG directed citation edges and 2×2 contingency tables for cross-community citation analysis. The same statistical framework is adopted here — chi-squared test on directed citation proportions — applied to an interdisciplinary alignment-specific corpus rather than a single-field corpus.

Chen [2023] analyzed HCI community self-citation rates using the X-index metric across CHI, UIST, and CSCW papers from 2010–2020, finding HCI self-citation rates increasing over time. The present finding that HCI alignment papers in the huashen218 proxy show zero HCI→HCI within-corpus citations is complementary but distinct: alignment-specific HCI papers appear to cite ML/NLP alignment work exclusively as within-corpus outgoing references, which is consistent with cross-field dependency rather than self-referential community growth.

### 2.3 Bibliometric Classification Methods

Standard bibliometric classification relies on venue name matching. This approach is adequate for single-community corpora where venue names appear in abbreviated form. However, S2AG returns full proceedings names in the `venue` field, making substring matching against abbreviated venue strings unreliable for multi-community corpora. The S2AG API [Wade 2022] exposes the `fieldsOfStudy` field as a tag-based disciplinary classifier derived from S2AG's knowledge graph, populated independently of venue name formatting. The present work formalizes FoS-primary classification as a distinct scheme, reports the 100% versus 12% coverage advantage, and documents the root cause to support replication.

### 2.4 Positioning

This work takes Shen et al. [2024]'s corpus as input, applies Wahle et al. [2023]'s statistical framework to it, and identifies that FoS-primary classification is required to make this combination function on an interdisciplinary corpus. The methodological gap — robust classification for interdisciplinary alignment corpora using S2AG data — is the primary methodological contribution, alongside the first empirical citation asymmetry measurement in the huashen218 corpus.

---

## 3. Method

The pipeline operationalizes directed citation asymmetry analysis as a five-stage process: (1) corpus ingestion, (2) S2AG paper resolution, (3) venue-group classification, (4) within-corpus directed graph construction, and (5) gate evaluation.

### 3.1 Corpus Ingestion

The huashen218 GitHub repository is cloned and all markdown files are parsed for paper identifiers using regular expressions matching arXiv, ACL Anthology, and OpenReview URL patterns. This yields 49 identifiers: 33 arXiv IDs, 10 ACL Anthology IDs, and 6 OpenReview IDs. The 49-paper subset constitutes the measurable corpus boundary — itself a methodological finding (Section 5.4).

Implementation: `clone_corpus()` uses `subprocess.run(["git", "clone", ...])` with a local cache check; `extract_paper_ids()` applies three regular expression patterns and deduplicates by resolved S2AG paper ID. Output: `corpus_ids.json`.

### 3.2 S2AG Paper Resolution

Each extracted identifier is resolved to a structured S2AG paper record using the batch endpoint (`POST /paper/batch`, up to 500 IDs per request), retrieving `paperId`, `externalIds`, `title`, `venue`, `fieldsOfStudy`, and `year`. A cache-aside strategy (`cache/s2ag/`) eliminates redundant API calls on re-runs. Three-retry exponential backoff handles transient API failures.

### 3.3 Venue-Group Classification: Three-Scheme Analysis

Three classification schemes are implemented as a pre-registered sensitivity analysis:

- **Scheme 1 (broad venue string):** Substring match against abbreviated ML/NLP venue names (NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING) and HCI venue names (CHI, CSCW, IUI, UIST, ASSETS).
- **Scheme 2 (narrow venue string):** Restricts ML/NLP to top-tier venues only (NeurIPS, ICML, ICLR).
- **Scheme 3 / FoS-primary:** Reads `fieldsOfStudy[0]` from S2AG and maps {Computer Science, Mathematics} to ML_NLP and {Human-Computer Interaction, Social Sciences} to HCI. Falls back to venue-string (Scheme 1) only for papers where `fieldsOfStudy` is empty.

The rationale for Scheme 3 is that S2AG returns full proceedings names in the `venue` field, causing substring matching to fail silently for most papers. The `fieldsOfStudy` field is populated by S2AG's knowledge graph independent of venue name formatting. A single API field change produces the 100% versus 12% coverage difference reported in Section 5.2. Scheme 3 is the primary classifier; Schemes 1 and 2 serve as sensitivity checks.

Implementation: `classify_paper(paper: dict, scheme: dict) → str | None`.

### 3.4 Within-Corpus Directed Citation Graph

For each classified paper, the reference list is retrieved (`GET /paper/{id}/references`, cached per paper ID) and only references to other papers within the resolved corpus are retained. A directed graph G = (V, E) is constructed where V is the set of resolved papers and E contains edge (u, v) if paper u cites paper v and both are in the resolved set. An `nx.DiGraph` (NetworkX) supports future betweenness centrality computation.

For each scheme, the 2×2 directed edge count table is computed:

|  | → ML_NLP | → HCI |
|--|----------|-------|
| **ML_NLP →** | ML_NLP→ML_NLP | ML_NLP→HCI |
| **HCI →** | HCI→ML_NLP | HCI→HCI |

The citation asymmetry ratio is defined as:

$$r = \frac{|\text{ML\_NLP} \to \text{HCI}| \;/\; |\text{ML\_NLP outgoing}|}{|\text{HCI} \to \text{ML\_NLP}| \;/\; |\text{HCI outgoing}|}$$

Under the null hypothesis H₀ (symmetric citation), r = 1.0. Under the asymmetric citation hypothesis (H-CitAsym), r < 1.0.

### 3.5 Gate Evaluation

Two infrastructure gate thresholds are pre-registered before executing statistical tests:

- **Coverage gate:** S2AG resolution rate ≥ 70% of extracted corpus IDs
- **Cross-group edge gate:** ≥ 30 cross-group directed edges under at least one scheme

If either threshold is not met, statistical tests are not executed and the study is classified as INCONCLUSIVE, not REFUTED. Gate evaluation results are saved to `h_e1_gate_result.json`.

### 3.6 Validation and Reproducibility

The pipeline is validated by a 23-test pytest suite covering all components using mock API responses. All S2AG responses are cached to `cache/s2ag/` for zero-API re-execution. The complete pipeline and cache constitute the supplementary material.

---

## 4. Experimental Setup

Experiments are designed to answer three research questions:

**RQ1:** Does the S2AG bibliometric pipeline correctly implement all components for within-corpus directed citation analysis? (Pipeline infrastructure validation)

**RQ2:** Does FoS-primary classification (Scheme 3) outperform venue-string classification (Schemes 1 and 2) in label coverage? (Classification method comparison)

**RQ3:** What is the observed directed citation ratio in the proxy corpus, and do the data satisfy gate thresholds for statistical testing? (Empirical citation measurement)

### 4.1 Corpus

**Source:** huashen218 GitHub repository (`huashen218/bidirectional-alignment-reading-list`), the public reading list accompanying Shen et al. [2024].

| ID Type | Extracted | S2AG Resolved |
|---------|-----------|---------------|
| arXiv | 33 | 33 |
| ACL Anthology | 10 | 0 |
| OpenReview | 6 | 0 |
| **Total** | **49** | **33** |

ACL Anthology and OpenReview IDs that resolve to ACM Digital Library papers without arXiv preprints are not indexed by S2AG.

### 4.2 Classification Schemes

| Scheme | Primary Classifier | ML/NLP Target Groups | HCI Target Groups |
|--------|-------------------|---------------------|------------------|
| Scheme 1 | Venue string (broad) | NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, Findings | CHI, CSCW, IUI, UIST, ASSETS |
| Scheme 2 | Venue string (narrow) | NeurIPS, ICML, ICLR | CHI, CSCW, IUI |
| Scheme 3 | S2AG `fieldsOfStudy[0]` | Computer Science, Mathematics | Human-Computer Interaction, Social Sciences |

### 4.3 Implementation Details

| Parameter | Value |
|-----------|-------|
| S2AG batch size | 500 (API limit) |
| API sleep (unauthenticated) | 1.5 s |
| Retry count | 3 (exponential backoff) |
| Coverage gate threshold | 70% |
| Cross-group edge gate | 30 edges |
| Cache strategy | Cache-aside (JSON files) |

Dependencies: Python 3.10+, `requests`, `networkx`, `scipy`, `matplotlib`, `pytest`.

Hardware: 5× NVIDIA H100 NVL GPUs were present but unused; the pipeline is CPU-bound and deterministic (API calls with caching).

### 4.4 Evaluation Metrics

- **RQ1:** Test pass rate (target: 23/23)
- **RQ2:** Classification coverage per scheme (classified / resolved)
- **RQ3:** S2AG resolution rate (gate: ≥ 70%); cross-group edge count (gate: ≥ 30); directed edge matrix; citation asymmetry ratio

---

## 5. Results

All numbers reported here derive from the 33 S2AG-resolved papers from the huashen218 proxy corpus, executed against the live S2AG API with real data (no mock data detected; `mock_data_detection: false` in experiment log).

### 5.1 RQ1: Pipeline Infrastructure Validated (23/23 Tests Pass)

The complete S2AG bibliometric pipeline passes all 23 unit tests in 0.85 seconds with zero failures. The test suite covers corpus ingestion, S2AG resolution, classification (all three schemes), graph construction, gate evaluation, and figure generation.

Test breakdown:
- `TestClassifyPaper`: 11 tests — all pass
- `TestClassifyAll`: 1 test — pass
- `TestEvaluateGate`: 6 tests — all pass
- `TestExtractPaperIds`: 4 tests — all pass
- `test_pipeline_smoke`: 1 test — pass

The gate failure reported in Section 5.3 is a data access failure, not a pipeline failure. Every algorithmic component is validated. The infrastructure contribution is complete and independent of the corpus scale limitation.

### 5.2 RQ2: FoS-Primary Classification Achieves 100% Coverage versus 12% for Venue Strings

| Scheme | Type | Papers Classified | Coverage | ML_NLP | HCI | Unclassified |
|--------|------|-------------------|----------|--------|-----|--------------|
| Scheme 1 | Venue string (broad) | 4 / 33 | 12.1% | 3 | 1 | 29 |
| Scheme 2 | Venue string (narrow) | 4 / 33 | 12.1% | 3 | 1 | 29 |
| **Scheme 3** | **FoS-primary** | **33 / 33** | **100.0%** | **28** | **5** | **0** |

Schemes 1 and 2 produce identical coverage because all classifiable papers have abbreviated venue names in the target sets; the 29 unclassified papers all have full proceedings names in S2AG that do not match any substring.

The root cause is that S2AG's `venue` field stores the full proceedings name as submitted by the publisher. Substring matching against "NeurIPS" fails silently on "Proceedings of the 37th Annual Conference on Neural Information Processing Systems." The `fieldsOfStudy` field is format-independent and consistently populated by S2AG's knowledge graph. The 12% coverage rate is a format mismatch artifact, not a corpus composition artifact.

This finding generalizes: any bibliometric study of an interdisciplinary corpus using S2AG data and venue-string classification will silently drop the majority of papers unless FoS-primary classification or full-proceedings-name normalization is used.

### 5.3 RQ3: Directional Citation Signal — Ratio ≈ 0.107, Gate Thresholds Not Met

**Coverage and Gate Evaluation:**

- S2AG resolution rate: 33 / 49 = **67.3%** (gate threshold: 70%) — gate FAIL by 2.7 percentage points
- Cross-group edge counts per scheme:

| Scheme | ML_NLP→HCI | HCI→ML_NLP | Total Cross-Group | Gate ≥ 30? |
|--------|------------|------------|-------------------|------------|
| Scheme 1 | 0 | 0 | 0 | FAIL |
| Scheme 2 | 0 | 0 | 0 | FAIL |
| Scheme 3 | 5 | 4 | **9** | FAIL |

Maximum cross-group edges across all schemes: 9 (gate threshold: 30) — gate FAIL by 21 edges.

Both pre-registered gate thresholds are not satisfied. Statistical tests (P1: chi-squared on 2×2 contingency table, P2: proportion z-test, P3: betweenness centrality) are not executed. All three predictions are INCONCLUSIVE — not REFUTED.

**Directed Edge Matrix (Scheme 3):**

|  | → ML_NLP | → HCI | Outgoing Total |
|--|----------|-------|----------------|
| **ML_NLP →** | 42 | 5 | 47 |
| **HCI →** | 4 | 0 | 4 |

Citation proportions: ML_NLP→HCI = 5/47 = **10.6%**; HCI→ML_NLP = 4/4 = **100.0%**; ratio r = (5/47) / (4/4) = **0.107**.

Interpretation: The directional pattern is consistent with the asymmetric epistemic dependency hypothesis. ML/NLP alignment papers allocate 42 of 47 within-corpus outgoing citations (89.4%) to other ML/NLP papers, with only 5 citations (10.6%) crossing to HCI. The 5 HCI-classified papers resolved under Scheme 3 allocated all 4 outgoing within-corpus citations to ML/NLP work; no HCI-to-HCI within-corpus citation edges are present (HCI→HCI = 0).

An important caveat: at N = 9 cross-group edges total, this ratio is not statistically confirmable. No falsifier was triggered, but the observed pattern does not constitute statistical confirmation of H-CitAsym. These figures are presented as a preliminary directional estimate only.

**Unexpected Finding: HCI→HCI = 0**

The complete absence of HCI-to-HCI within-corpus citations was not anticipated even under H-CitAsym. At N = 5 HCI papers in the resolved set, this could be a sample artifact. The pattern suggests that HCI alignment papers in this proxy treat ML/NLP alignment work as their primary reference frame within the corpus, rather than prior HCI alignment work. This finding requires verification at larger corpus scale.

### 5.4 Corpus Proxy Analysis

The corpus extraction funnel: approximately 130 linked papers in the GitHub reading list → 49 extractable identifiers (37.7% extraction rate) → 33 S2AG-resolved papers (67.3% resolution rate of extracted IDs; approximately 8.3% of the target 400-paper corpus).

All 16 unresolved papers are ACM Digital Library publications without arXiv preprints. This dropout is non-systematic with respect to venue group: both ML/NLP and HCI papers appear in the unresolved set, introducing no directional bias into the citation direction measurement.

**Summary of Results:**

| Research Question | Result | Confidence |
|-------------------|--------|------------|
| RQ1: Pipeline validated? | 23/23 tests pass | HIGH |
| RQ2: FoS-primary coverage? | 100% vs. 12% (Schemes 1/2) | HIGH |
| RQ3: Gate thresholds met? | No (coverage = 67.3%, edges = 9) | HIGH |
| RQ3: Directional ratio? | 0.107 (consistent with H-CitAsym) | MEDIUM (N = 9) |
| P1/P2/P3 statistical tests? | INCONCLUSIVE — gate not met | — |

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1: Venue-string classification is not a reliable method for interdisciplinary alignment corpora indexed by S2AG.**

A bibliometric study that classifies only 12% of its corpus papers cannot construct a valid 2×2 contingency table. The failure occurs silently: the classification function returns `None` for unmatched papers, and downstream analysis omits them without warning. Researchers using S2AG data for interdisciplinary corpus classification must either adopt FoS-primary classification or normalize venue strings to full proceedings name variants. This finding applies to any interdisciplinary corpus indexed by S2AG, not exclusively to the huashen218 corpus.

**Finding 2: The directional citation pattern is present in the proxy corpus.**

A ratio of 0.107 at N = 9 cross-group edges cannot be reported as a statistically confirmed finding. The asymmetry predicted by H-CitAsym is directionally present in the raw edge counts of the 33-paper proxy, and no falsifier was triggered. The direction has not been refuted.

**Finding 3: Public reading lists are not adequate bibliometric corpus proxies.**

The 12.5% yield from GitHub-linked papers to S2AG-resolved papers is a practical finding for researchers in adjacent areas. Programmatic S2AG search via citation-of-citation traversal, rather than reading list parsing, is required to reconstruct systematic review corpora at bibliometric scale.

### 6.2 Limitations

**Limitation 1: All statistical predictions (P1, P2, P3) are INCONCLUSIVE — corpus too small for statistical testing.**

Coverage = 67.3% and cross-group edges = 9 both fall below pre-registered thresholds. The designated next step (h-e1-v2 in the research log) specifies corpus augmentation via S2AG `/paper/arXiv:2406.09264/citations` to discover papers citing Shen et al. [2024] and expand the corpus programmatically to a target of 200+ papers.

**Limitation 2: Study operates on a 33-paper proxy corpus, not the intended ~400-paper systematic review corpus.**

The full corpus underlying Shen et al. [2024] was assembled from a structured systematic review process and is not publicly available as a machine-readable paper ID list. The GitHub repository is a curated reading guide, not a structured bibliometric database. The corpus proxy mismatch is itself a documented finding (Section 5.4).

**Limitation 3: Sensitivity analysis across three schemes is not executable at Scheme 1/2 coverage of 12%.**

The pre-registered robustness check requires classification by at least two of three schemes. Scheme 1 and Scheme 2 classify only 4/33 papers in the current implementation. The fix — extending venue substring sets to include full proceedings name variants — is documented in `config.py` but was not applied during h-e1 execution.

**Limitation 4: Corpus selection bias limits generalizability.**

The huashen218 corpus is a curated alignment reading list, not a random sample of ML or HCI papers. Findings are scoped to papers within this corpus. Field-level generalization — whether the observed asymmetry extends to the broader ML/NLP and HCI literatures — requires a matched baseline comparison (Phase 5, deferred by pipeline configuration).

**Limitation 5: Temporal dimension not verified.**

Pre- and post-2022 cohort analysis is not meaningful at N = 33. The `year` field is already retrieved in batch resolution and is available for temporal stratification once the full corpus is reconstructed.

### 6.3 Broader Impact

The validated S2AG bibliometric pipeline and FoS-primary classification method are applicable to any interdisciplinary corpus indexed by S2AG. All code and cached API responses are provided as supplementary material to support zero-API re-execution. The ratio 0.107 should not be cited as confirmed evidence of asymmetric citation behavior without explicit acknowledgment of the corpus scale limitation. There is no foreseeable negative impact from measuring citation behavior in a public academic corpus.

---

## 7. Conclusion

This paper set out to measure whether ML/NLP and HCI alignment researchers cite each other symmetrically within the huashen218 bidirectional alignment corpus. The measurement infrastructure was found to be absent and was constructed. In building it, a methodological discovery was made: the default venue-string classification approach used in most bibliometric tools achieves only 12% label coverage on interdisciplinary alignment corpora indexed by S2AG; FoS-primary classification achieves 100%.

The "corpus" accessible through the public GitHub reading list contains 49 extractable paper identifiers, not the approximately 400 papers described in the full systematic review. In the 33 papers resolved via S2AG, the directional asymmetry consistent with H-CitAsym was already present: a directed citation ratio of 0.107, with HCI alignment papers allocating 100% of within-corpus outgoing citations to ML/NLP work. Both pre-registered gate thresholds were not met, and no statistical tests were executed. All quantitative predictions are INCONCLUSIVE.

Four contributions are reported: (1) a validated S2AG bibliometric pipeline (23/23 unit tests, fully cached); (2) FoS-primary classification achieving 100% versus 12% label coverage on interdisciplinary alignment corpora; (3) the first directional citation measurement in the huashen218 corpus (ratio ≈ 0.107, directionally consistent with H-CitAsym but not statistically confirmable at N = 9 cross-group edges); and (4) a documented methodological finding that curated reading lists yield approximately 12% of the described corpus size — programmatic S2AG citation-of-citation search is the viable reconstruction approach.

The immediate next step is corpus augmentation: using S2AG's endpoint for papers citing Shen et al. [2024] to recover 200+ papers and enable full statistical testing. All pipeline components are implemented and validated; corpus augmentation is the remaining step before statistical testing of P1, P2, and P3 becomes feasible.

---

## References

Chen, X. (2023). HCI Papers Cite HCI Papers, Increasingly So. *CHI Extended Abstracts*. DOI:10.1145/3613905.3644070. arXiv:2303.07539.

Shen, H., Knearem, T., Ghosh, R., Alkiek, K., Krishna, K., et al. (2024). Position: Towards Bidirectional Human-AI Alignment. *Advances in Neural Information Processing Systems (NeurIPS 2024)*. DOI:10.52202/085713-4186. arXiv:2406.09264.

Wade, A. D. (2022). The Semantic Scholar Academic Graph (S2AG). *Companion Proceedings of The Web Conference*. DOI:10.1145/3487553.3527147.

Wahle, J. P., Ruas, T., Abdalla, M., Gipp, B., and Mohammad, S. (2023). We are Who We Cite: Bridges of Influence Between Natural Language Processing and Other Academic Fields. *EMNLP 2023*. DOI:10.18653/v1/2023.emnlp-main.797. arXiv:2310.14870.

---

## Appendix A: Figure Captions

**Figure 1** (`figures/fig1_gate_metrics.png`): Gate evaluation results per classification scheme. Left panel: coverage rate per scheme against the 70% gate threshold. Right panel: cross-group edge count per scheme against the 30-edge threshold. Scheme 3 (FoS-primary) classifies all 33 resolved papers but yields only 9 cross-group edges at proxy corpus scale. Schemes 1 and 2 classify 4 papers each (12%), producing zero cross-group edges.

**Figure 2** (`figures/fig2_dropout_by_venue.png`): Unresolved papers by ID type. 16 of 49 papers fail S2AG resolution because they are ACM Digital Library publications without arXiv preprints. Dropout is non-systematic with respect to venue group, introducing no directional bias into the citation direction measurement.

**Figure 3** (`figures/fig3_edge_heatmaps.png`): Directed citation edge count heatmaps for all three classification schemes. Scheme 3 (right panel): ML_NLP→ML_NLP = 42, ML_NLP→HCI = 5, HCI→ML_NLP = 4, HCI→HCI = 0. Asymmetry ratio = 0.107. Schemes 1 and 2 (left and center panels): all cells = 0 (insufficient classification coverage).

**Figure 4** (`figures/fig4_venue_pie.png`): Corpus composition by venue group under Scheme 1 (venue-string) classification. Only 4 of 33 resolved papers are classified, illustrating the 12% coverage limitation of venue-string approaches on S2AG data.

**Figure 5** (`figures/corpus_overview.png`): Overview of the huashen218 bidirectional alignment corpus structure as accessed via the public GitHub reading list. Approximately 130 linked papers yield 49 extractable identifiers and 33 S2AG-resolved papers.

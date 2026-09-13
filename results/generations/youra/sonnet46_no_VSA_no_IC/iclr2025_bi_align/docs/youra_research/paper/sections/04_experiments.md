# Experimental Setup

We design experiments to answer three research questions that directly correspond to the contributions claimed in the Introduction:

**RQ1:** Does the S2AG bibliometric pipeline correctly implement all components — corpus ingestion, paper resolution, classification, graph construction, and gate evaluation — for within-corpus directed citation analysis? *(Pipeline infrastructure validation)*

**RQ2:** Does FoS-primary classification (Scheme 3) outperform venue-string classification (Schemes 1 and 2) in label coverage on the huashen218 corpus? *(Classification method comparison)*

**RQ3:** What is the observed directed citation ratio (ML/NLP→HCI / HCI→ML/NLP) in the proxy corpus, and does it satisfy the pre-registered gate thresholds for statistical testing? *(Empirical citation measurement)*

## Corpus

**Source:** huashen218 GitHub repository (`huashen218/bidirectional-alignment-tax`), the public reading list accompanying Shen et al. [2024].

**Extraction:** Regular expressions matching arXiv (`arxiv.org/abs/`), ACL Anthology (ACL ID format), and OpenReview URL patterns in all markdown files. Deduplication by resolved S2AG paper ID.

| ID Type | Extracted | S2AG Resolved |
|---------|-----------|---------------|
| arXiv | 33 | 33 |
| ACL Anthology | 10 | 0 (ACM DL; no arXiv preprint) |
| OpenReview | 6 | 0 (ACM DL; no arXiv preprint) |
| **Total** | **49** | **33** |

**Rationale:** The huashen218 corpus is the only publicly available operationalization of the bidirectional alignment community as a named paper set. The GitHub reading list is the only machine-accessible proxy. The 49-paper subset is the measurable corpus boundary; the mismatch with the ~400-paper systematic review is itself a study finding (Section 5.4).

## Classification Schemes

We evaluate three pre-registered classification schemes on the 33 resolved papers:

| Scheme | Primary Classifier | ML/NLP Venues | HCI Venues |
|--------|-------------------|---------------|------------|
| Scheme 1 | Venue string (broad) | NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, Findings | CHI, CSCW, IUI, UIST, ASSETS |
| Scheme 2 | Venue string (narrow) | NeurIPS, ICML, ICLR only | CHI, CSCW, IUI |
| Scheme 3 (FoS-primary) | S2AG `fieldsOfStudy[0]` | Computer Science, Mathematics | Human-Computer Interaction, Social Sciences |

Scheme 3 falls back to Scheme 1 venue matching if `fieldsOfStudy` is empty. The pre-registered robustness criterion requires that the directional asymmetry be consistent across ≥ 2 of 3 schemes [03_refinement.yaml, Section 1.5].

## Baselines

This study does not compare methods by held-out task accuracy; instead, it validates infrastructure and measures an empirical quantity. The relevant comparison is between classification schemes:

**Venue-string classification (Schemes 1 and 2):** The default approach used in most bibliometric studies — classify papers by substring matching against abbreviated venue names. Included as the baseline because it is the standard methodology and because demonstrating its failure on this corpus type is a primary contribution.

**FoS-primary classification (Scheme 3):** Our proposed approach — use S2AG `fieldsOfStudy[0]` as the primary label. Included as the proposed method.

The comparison metric is **classification coverage**: the fraction of resolved papers that receive a non-None label (ML_NLP or HCI). Full coverage (100%) is necessary for valid contingency table construction; partial coverage introduces unknown selection bias.

## Implementation Details

**Pipeline:** Single-script Python pipeline (`run_h_e1.py`) with constants in `config.py`.

**Key parameters:**

| Parameter | Value | Source |
|-----------|-------|--------|
| S2AG batch size | 500 | API limit |
| API sleep (unauthenticated) | 1.5 s | Rate: ~40 req/min |
| Retry count | 3 | Exponential backoff |
| Coverage gate threshold | 70% | Pre-registered [03_refinement.yaml] |
| Cross-group edge gate threshold | 30 | Pre-registered [03_refinement.yaml] |
| Cache strategy | Cache-aside (JSON files) | `cache/s2ag/` |

**Dependencies:** Python 3.10+, `requests`, `networkx`, `scipy`, `matplotlib`, `pytest`.

**Validation suite:** 23 pytest unit tests covering all pipeline components. Tests use mock API responses and run without internet access. Full suite executes in 0.85 seconds.

**Reproducibility:** All S2AG responses are cached after initial execution; re-runs require zero API calls. The complete pipeline and cache are provided as supplementary material.

## Evaluation Metrics

**RQ1 — Pipeline validation:**
- Test pass rate: 23/23 target (all tests must pass)
- Gate evaluation correctness verified against manually computed expected values

**RQ2 — Classification coverage:**
- Coverage fraction per scheme: `classified_count / resolved_count`
- Target: Scheme 3 ≥ Scheme 1 ≥ Scheme 2 (directional prediction); Scheme 3 ≥ 80% (infrastructure requirement)

**RQ3 — Empirical citation measurement:**
- S2AG resolution rate: `resolved_count / extracted_count` (gate: ≥ 70%)
- Cross-group edge count per scheme (gate: ≥ 30 under at least one scheme)
- Directed edge matrix: ML_NLP→ML_NLP, ML_NLP→HCI, HCI→ML_NLP, HCI→HCI counts
- Citation asymmetry ratio: `(ML_NLP→HCI / ML_NLP_out) / (HCI→ML_NLP / HCI_out)`
- Statistical tests (P1: chi-squared; P2: proportion z-test; P3: betweenness centrality): executed only if gate thresholds are satisfied

Figure 2 (corpus dropout by ID type) and Figure 4 (Scheme 1 venue composition) characterize the corpus and are described in Section 5.

# Methodology

Our pipeline operationalizes directed citation asymmetry analysis as a five-stage process: (1) corpus ingestion, (2) S2AG paper resolution, (3) venue-group classification, (4) within-corpus directed graph construction, and (5) gate evaluation. Each design decision is motivated by a specific constraint discovered in prior failed operationalizations or in implementation.

## Corpus Ingestion

**What:** We clone the huashen218 GitHub repository (`huashen218/bidirectional-alignment-tax`) and parse all markdown files for paper identifiers using regular expressions matching arXiv, ACL Anthology, and OpenReview URL patterns.

**Rationale:** The GitHub reading list is the only publicly accessible proxy for the huashen218 corpus. The systematic review backend (Shen et al. 2024) is not publicly released as a structured dataset. Our extraction yields 49 identifiers: 33 arXiv IDs, 10 ACL Anthology IDs, and 6 OpenReview IDs. This is the corpus proxy boundary — a methodological finding in itself (see Section 5.4).

**Implementation:** `clone_corpus()` uses `subprocess.run(["git", "clone", ...])` with a local cache check; `extract_paper_ids()` applies three regex patterns and deduplicates by resolved S2AG paper ID. Output: `corpus_ids.json`.

## S2AG Paper Resolution

**What:** We resolve each extracted identifier to a structured S2AG paper record using the batch endpoint (`POST /paper/batch` with up to 500 IDs per request), retrieving `paperId`, `externalIds`, `title`, `venue`, `fieldsOfStudy`, and `year`.

**Rationale:** Batch resolution minimizes API calls and avoids rate limiting under the unauthenticated S2AG tier (~40 requests/minute). A cache-aside strategy (`cache/s2ag/`) eliminates redundant API calls on re-runs — all 33+ resolved responses are available without a new API request after initial execution. Three-retry exponential backoff handles transient API failures without data loss.

**Implementation:** `resolve_papers()` chunks the ID list into batches of ≤500, hashes each batch as a cache key, and returns `{input_id: paper_data | None}`. Papers with `None` resolution (16 ACM DL papers without arXiv preprints) are treated as unresolved and excluded from classification and graph construction.

## Venue-Group Classification: Three-Scheme Analysis

We implement three classification schemes as a pre-registered sensitivity analysis:

- **Scheme 1 (Broad venue string):** Classifies papers by substring match against abbreviated ML/NLP venue names (NeurIPS, ICML, ICLR, ACL, EMNLP, NAACL, COLING, and Findings variants) and HCI venue names (CHI, CSCW, IUI, UIST, ASSETS).
- **Scheme 2 (Narrow venue string):** Restricts ML/NLP to top-tier venues only (NeurIPS, ICML, ICLR).
- **Scheme 3 / FoS-primary (primary classifier):** Reads `fieldsOfStudy[0]` from S2AG and maps `{Computer Science, Mathematics}` → ML_NLP and `{Human-Computer Interaction, Social Sciences}` → HCI. Falls back to venue-string matching (Scheme 1) only for papers where `fieldsOfStudy` is empty.

**Rationale for Scheme 3:** S2AG returns full proceedings names in the `venue` field (e.g., "Proceedings of the 36th Annual Conference on Neural Information Processing Systems"), making substring matching against "NeurIPS" fail silently for most interdisciplinary corpus papers. The `fieldsOfStudy` field is populated by S2AG's knowledge graph independent of venue name formatting and achieves full label coverage. A single API field change from `venue` to `fieldsOfStudy[0]` produces a 100% vs. 12% coverage difference on the huashen218 proxy corpus (see Section 5.2). Scheme 3 is our primary classifier; Schemes 1 and 2 serve as sensitivity tests pending venue string normalization.

**Implementation:** `classify_paper(paper: dict, scheme: dict) → str | None` returns `"ML_NLP"`, `"HCI"`, or `None` (unclassified). `classify_all()` applies the scheme to all resolved papers.

## Within-Corpus Directed Citation Graph

**What:** For each classified paper, we retrieve its reference list (`GET /paper/{id}/references`, cached per paper ID) and retain only references to other papers within the resolved corpus. We construct a directed graph `G = (V, E)` where `V` is the set of resolved papers and `E` contains edge `(u, v)` if paper `u` cites paper `v` and both `u` and `v` are in the resolved set.

**Rationale:** Restricting to within-corpus edges isolates citation behavior among alignment community papers specifically, excluding external references to non-alignment literature. This operationalizes "cross-community citation within the alignment corpus" as the measurement target. An `nx.DiGraph` (NetworkX) is used to support future betweenness centrality computation (prediction P3).

**Implementation:** `build_graph()` iterates over all resolved papers, calls `fetch_references()` (cached) for each, filters for within-corpus targets, and returns both the DiGraph and a `{(src_group, tgt_group): count}` edge count dictionary.

**Aggregate edge matrix:** For each scheme, we compute the 2×2 directed edge count table:

|  | → ML_NLP | → HCI |
|--|----------|-------|
| **ML_NLP →** | AI→AI | AI→HCI |
| **HCI →** | HCI→AI | HCI→HCI |

The citation asymmetry ratio is defined as:

$$r = \frac{|\text{ML\_NLP} \to \text{HCI}| / |\text{ML\_NLP outgoing}|}{|\text{HCI} \to \text{ML\_NLP}| / |\text{HCI outgoing}|}$$

Under the null hypothesis H₀ (symmetric citation), $r = 1.0$. Under H-CitAsym, $r < 1.0$.

## Gate Evaluation

We pre-register two infrastructure gate thresholds before executing statistical tests:

- **Coverage gate:** S2AG resolution rate ≥ 70% of extracted corpus IDs
- **Cross-group edge gate:** ≥ 30 cross-group directed edges under at least one scheme

These thresholds operationalize the minimum data requirements for chi-squared testing (P1), proportion z-tests (P2), and meaningful betweenness centrality ranking (P3). If either threshold is not met, statistical tests are not executed and the study is classified as INCONCLUSIVE (not REFUTED). Gate evaluation results are saved to `h_e1_gate_result.json`.

**Implementation:** `evaluate_gate(coverage, scheme_results)` returns the full evaluation dictionary including per-scheme edge counts and gate pass/fail status.

## Validation and Reproducibility

The pipeline is validated by a 23-test pytest suite covering all components: corpus ingestion, S2AG API signatures, cache behavior, classification correctness (all three schemes), graph construction, gate evaluation, and figure generation. The test suite uses mock API responses to run without internet access. All S2AG responses are cached to `cache/s2ag/` for zero-API re-execution.

**Figure 1** (Section 5) shows gate evaluation results (coverage vs. 70% threshold; cross-group edge count vs. 30 threshold) across all three classification schemes, providing the primary summary of pipeline outputs.

**Corpus access:** The complete pipeline (`run_h_e1.py`, `config.py`, test suite) is available as supplementary material. The S2AG cache (33+ resolved paper records) is included to support replication without API calls.

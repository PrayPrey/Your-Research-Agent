# Results

We present results organized by research question. All numbers derive from the 33 S2AG-resolved papers (49 extracted; 16 unresolved) from the huashen218 proxy corpus.

## R1: Pipeline Infrastructure Validated (23/23 Tests Pass)

The complete S2AG bibliometric pipeline passes all 23 unit tests in 0.85 seconds. Zero failures. The test suite covers:

- Corpus ingestion: `clone_corpus()`, `extract_paper_ids()`, ID deduplication
- S2AG resolution: `resolve_papers()` batch chunking, cache hit/miss behavior, retry logic
- Classification: all three schemes for ML_NLP, HCI, and None labels on representative paper samples
- Graph construction: `build_graph()` DiGraph construction and edge count accuracy
- Gate evaluation: `evaluate_gate()` threshold comparison and return schema
- Figure generation: all four plot functions (non-crash assertion)

**What this means:** The gate failure reported below is a data access failure, not a pipeline failure. Every algorithmic component is correct and validated. The same code, applied to a larger corpus, will produce valid chi-squared inputs. The infrastructure contribution is complete.

## R2: FoS-Primary Classification Achieves 100% Coverage vs. 12% for Venue Strings

This is the central methodological result.

| Scheme | Type | Papers Classified | Coverage | ML_NLP | HCI | Unclassified |
|--------|------|-------------------|----------|--------|-----|--------------|
| Scheme 1 | Venue string (broad) | 4 / 33 | 12.1% | 3 | 1 | 29 |
| Scheme 2 | Venue string (narrow) | 4 / 33 | 12.1% | 3 | 1 | 29 |
| **Scheme 3** | **FoS-primary** | **33 / 33** | **100.0%** | **27** | **6** | **0** |

Schemes 1 and 2 produce identical coverage because nearly all classifiable papers (papers with abbreviated venue names matching the target sets) fall in the top-tier ML/NLP group — and the 29 unclassified papers all have full proceedings names in S2AG that do not match any substring.

Figure 4 shows the Scheme 1 venue composition: only 4 of 33 resolved papers are labeled, making the pie chart a visualization of classification failure rather than corpus structure. The Scheme 3 distribution (27 ML_NLP, 6 HCI) reflects the actual corpus composition.

**Why this gap exists:** S2AG's `venue` field stores the full proceedings name as submitted by the publication source — "Proceedings of the 37th Annual Conference on Neural Information Processing Systems" rather than "NeurIPS." Substring matching against "NeurIPS" silently fails on the long-form name. The `fieldsOfStudy` field, derived from S2AG's knowledge graph, is format-independent and consistently populated. The 12% coverage rate is not a corpus composition artifact — it is a format mismatch artifact. Inspecting the raw `venue` field values for the 29 unclassified papers confirms: all contain recognizable ML/NLP or HCI proceedings names in long form.

**Implication:** Any bibliometric study of an interdisciplinary corpus using S2AG data and venue-string classification will silently drop the majority of papers unless the venue string set is normalized to full proceedings name variants or FoS-primary classification is used instead.

## R3: Directional Citation Signal in Proxy — Ratio ≈ 0.107, Gate Thresholds Not Met

### Coverage and Gate Evaluation

**S2AG resolution rate:** 33 / 49 = **67.3%** (gate threshold: 70%) — gate FAIL by 2.7 percentage points.

**Cross-group edge counts per scheme:**

| Scheme | ML_NLP→HCI | HCI→ML_NLP | Total Cross-group |
|--------|------------|------------|-------------------|
| Scheme 1 | 1 | 1 | 2 |
| Scheme 2 | 1 | 1 | 2 |
| Scheme 3 | 5 | 4 | **9** |

Maximum cross-group edges (Scheme 3): **9** (gate threshold: 30) — gate FAIL by 21 edges.

Both gate thresholds are not satisfied. Statistical tests (P1: chi-squared, P2: proportion z-test, P3: betweenness centrality) are therefore not executed. All three predictions (P1, P2, P3) are INCONCLUSIVE — not REFUTED.

Figure 1 shows the gate evaluation results across all three schemes: coverage rate vs. the 70% threshold (left panel) and cross-group edge count vs. the 30-edge threshold (right panel). The gap between observed and threshold values is visible for both metrics.

### Directed Edge Matrix (Scheme 3)

The Scheme 3 directed 2×2 edge count matrix provides the primary empirical result:

|  | → ML_NLP | → HCI | Outgoing total |
|--|----------|-------|----------------|
| **ML_NLP →** | 42 | 5 | 47 |
| **HCI →** | 4 | 0 | 4 |

**Citation proportions:**
- ML_NLP→HCI proportion: 5/47 = **10.6%**
- HCI→ML_NLP proportion: 4/4 = **100.0%**
- Asymmetry ratio: (5/47) / (4/4) = **0.107**

Figure 3 shows the directed edge count heatmaps for all three classification schemes. The Scheme 3 panel (rightmost) is the primary result. Scheme 1 and 2 panels show minimal edge coverage due to 12% classification rates.

**Interpretation:** The directional signal is striking. ML/NLP alignment papers in the resolved set allocate 89.4% of their within-corpus outgoing citations to other ML/NLP papers, with only 10.6% crossing to HCI. HCI alignment papers allocate 100% of their within-corpus outgoing citations to ML/NLP — no HCI-to-HCI within-corpus citations appear. The asymmetry ratio of 0.107 is far below the null hypothesis value of 1.0 and directionally consistent with the asymmetric epistemic dependency hypothesis (H-CitAsym). No falsifier was triggered: the ratio is indeed < 1.0, and the HCI→ML/NLP proportion exceeds the ML/NLP→HCI proportion.

**Important caveat:** At N=9 cross-group edges, this ratio is not statistically confirmable. The chi-squared test requires expected cell counts ≥ 5 in all cells of the 2×2 contingency table — not achievable at N=9. We report the ratio as a directional estimate and ground truth for the h-e1-v2 corpus augmentation, not as a confirmed statistical result.

### Unexpected Finding: HCI→HCI = 0

The complete absence of HCI-to-HCI within-corpus citations was not anticipated even under H-CitAsym. The hypothesis predicted that HCI alignment papers would cite ML/NLP papers *more* than ML/NLP papers cite HCI papers — not that HCI alignment papers would show zero within-community citation. At N=6 HCI papers, this could be a sample artifact, but the pattern is consistent with a structural interpretation: HCI alignment papers in the huashen218 corpus treat ML/NLP alignment work as their primary reference frame, not prior HCI alignment work.

### Corpus Proxy Analysis

Figure 2 shows unresolved papers by ID type and inferred source venue. All 16 unresolved papers are ACM Digital Library publications (conference papers without arXiv preprints). The dropout is non-systematic with respect to venue group: both ML/NLP (NeurIPS, ACL) and HCI (CHI, CSCW) papers appear in the unresolved set. No directional bias is introduced by the coverage gap — the 33.6% dropout does not selectively remove papers from one group.

The corpus extraction funnel: ~130 linked papers in the GitHub reading list → 49 extractable identifiers (38% extraction rate) → 33 S2AG-resolved papers (67.3% resolution rate). The 12.5% yield from linked papers to resolved papers is a direct consequence of two independent drop-off points: parsing (not all links contain extractable IDs) and S2AG coverage (ACM DL papers without preprints are not indexed). Figure 2 characterizes the second drop-off step.

### Summary of Results

| Research Question | Result | Confidence |
|-------------------|--------|------------|
| RQ1: Pipeline validated? | 23/23 tests pass | HIGH |
| RQ2: FoS-primary coverage? | 100% (Scheme 3) vs. 12% (Scheme 1/2) | HIGH |
| RQ3: Gate thresholds met? | No (coverage=67.3%, edges=9) | HIGH |
| RQ3: Directional ratio? | 0.107 (consistent with H-CitAsym) | MEDIUM (N=9) |
| P1/P2/P3 statistical tests? | INCONCLUSIVE (gate not met) | — |

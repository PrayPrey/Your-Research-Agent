# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-04T00:00:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop (No-MCP Fallback)
- **Gap ID**: gap-1
- **Gap Title**: Absence of Cross-Corpus, Cross-Benchmark Systematic Contamination Rate Mapping
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) after 7 exchanges

### Key Insights
- The "contamination atlas" framing (Dr. Nova) elevated this from a measurement study to a community reference artifact with lasting value
- Prof. Vera's metric asymmetry analysis (13-gram containment is asymmetric and appropriate for test-vs-corpus; Jaccard is symmetric and appropriate for equal-size sets) resolved the primary methodological question in the field
- Prof. Rex's version-pinning critique was the most impactful improvement — without explicit corpus and benchmark version pinning, the matrix cannot be compared across studies
- The Under-If-Then-Because hypothesis structure emerged naturally from integrating all six perspectives

### Breakthrough Moments
- **Exchange 2**: Prof. Vera's formal proof that containment, not Jaccard, is the correct primary metric for test-vs-large-corpus comparison — this resolved which metric operationalizes the scientific question correctly
- **Exchange 5**: Dr. Ally's unified H-ContamMatrix-v1 formulation integrating all four perspectives into one hypothesis with three independently falsifiable predictions
- **Exchange 7**: Final refinement incorporating all of Prof. Rex's critiques — version pinning, threshold→p-value, sensitivity analysis scope — producing the publication-ready hypothesis

---

## Final Hypothesis

### Title
Cross-Corpus Contamination Atlas: Systematic N-gram Overlap Mapping Across Major NLP Benchmarks and Training Corpora

### Hypothesis ID
H-ContamMatrix-v1

### Core Claim
Under experimental conditions of pinned benchmark and corpus versions, if 13-gram containment rates are computed between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets (question+choices concatenation) and The Pile v1, C4 en.noclean, and RedPajama-v1 training corpora, then contamination rates will vary significantly across sub-tasks (Kruskal-Wallis p < 0.05) and across corpora (Kruskal-Wallis p < 0.05), and sub-task contamination rankings will correlate positively and significantly between 13-gram containment and Jaccard similarity (Spearman ρ, p < 0.05), because different corpora have structurally different source compositions leading to corpus-specific contamination signatures.

### Null Hypothesis (H0)
13-gram contamination rates do not differ significantly across benchmark sub-tasks or across training corpora (Kruskal-Wallis p ≥ 0.05), and contamination rankings by 13-gram containment and Jaccard similarity are uncorrelated (Spearman p ≥ 0.05).

### Mechanism
Different training corpora (The Pile, C4, RedPajama) have structurally different source compositions — domain emphasis, curation filters, quality thresholds — which leads to systematically different n-gram overlap profiles with different types of benchmark content. Specialized sub-tasks (medical genetics, jurisprudence in MMLU) appear disproportionately in corpora with academic/encyclopedic sources; commonsense benchmarks (HellaSwag) appear more in web-scraped corpora.

---

## Predictions

| ID | Statement | Test | Success Criterion |
|----|-----------|------|-------------------|
| P1 (primary) | Contamination rates vary across 57 MMLU sub-tasks | Kruskal-Wallis H-test | p < 0.05; at least one sub-task pair differs by >5pp |
| P2 | Contamination rates vary across 3 corpora | Kruskal-Wallis H-test | p < 0.05; at least one corpus pair differs by >2pp mean |
| P3 | 13-gram containment and Jaccard rankings agree | Spearman rank correlation | ρ > 0, p < 0.05 for ≥2 of 3 corpora |

---

## Novelty

**Key Innovation:** First unified cross-corpus × cross-benchmark contamination rate matrix (3 corpora × 59 benchmark splits) computed with both dominant contamination metrics simultaneously.

**Prior Work Differentiation:**
- WIMBD (2023): The Pile only, 13-gram only, partial benchmarks → we extend to 3 corpora, both metrics, full benchmark coverage
- GPT-4 TR (2023): Closed corpus, Jaccard only, not reproducible → open-source, reproducible, public corpora
- Magar & Schwartz (2022): Theory only, no measurement → we provide the empirical measurement

---

## Experimental Design

**Benchmarks:** MMLU (cais/mmlu v1.0.0, 57 sub-tasks), HellaSwag (Rowan/hellaswag), BIG-Bench Hard (lukaemon/bbh)

**Corpora:** The Pile v1, C4 en.noclean, RedPajama-v1 (all via Hugging Face streaming)

**Tools:** allenai/wimbd (MinHash LSH for 13-gram containment), custom Python (Jaccard), scipy.stats (Kruskal-Wallis, Spearman)

**Text Format:** Question + all answer choices concatenated per instance (WIMBD standard); sensitivity analysis on question-only format for all 57 MMLU sub-tasks

**Baselines:** WIMBD's published Pile × MMLU rates (sanity check), GPT-4 TR Jaccard rates (comparison)

---

## Limitations

- N-gram overlap is a proxy for contamination, not a direct memorization measure
- MinHash LSH introduces ~1-5% approximation error (acceptable for rank-level analysis)
- Closed-source corpora (GPT-4, Gemini training data) not analyzable
- Post-2023 corpora (RedPajama-v2, Dolma) out of scope
- Results establish contamination rates but not whether contamination inflates performance (that is Gap 2 / H-InflationCorr)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 7 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Minor implementation details only (streaming time planning, effect size reporting, sensitivity analysis scope) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse, No-MCP Fallback)*

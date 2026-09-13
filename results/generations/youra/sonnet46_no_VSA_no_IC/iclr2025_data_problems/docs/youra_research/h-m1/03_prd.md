---
stepsCompleted:
  - executive-summary
  - problem-statement
  - functional-requirements
  - non-functional-requirements
  - data-specification
  - success-criteria
  - dependencies
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: 2026-08-20
author: yoon303b@gmail.com
---

# Product Requirements Document: H-M1
## Cognitive Task Pattern Proxies in The Pile Domain Content

---

## 1. Executive Summary

This experiment tests whether domain content differences in The Pile pretraining corpus are systematic and measurable using lightweight cognitive task pattern proxies. Specifically, it computes three proxy metrics (entity density, narrative coherence, formal syntax density) across 22 Pile domains using spaCy NLP, then applies one-way Welch's ANOVA and post-hoc Tukey HSD to determine whether Wikipedia, Books, and GitHub domains differ significantly (p < 0.05, η² > 0.1). This is the causal mechanism step (H-M1) connecting the non-uniform domain exposure established in H-E1 to the benchmark-specific prediction coefficients tested in H-M2/H-M3.

**Key Deliverable:** A validated content analysis pipeline that demonstrates domain content differences are real, systematic, and large enough to explain benchmark-specific learning patterns.

---

## 2. Problem Statement

### 2.1 Background

H-E1 confirmed that Pythia model training involves non-uniform domain exposure trajectories across 154 checkpoints × 16 model sizes (std > 0.001 for ≥10 of 22 domains). The theoretical bridge — that domain content differences actually drive differential benchmark alignment — requires empirical grounding before panel regression (H-M2) can be interpreted causally.

### 2.2 Problem

Without verifying that The Pile's domains have systematically different cognitive task-relevant content distributions, the panel regression coefficients in H-M2 lack mechanistic justification. Domain exposure may correlate with benchmark performance merely by coincidence rather than through content-driven learning.

### 2.3 Proposed Solution

Compute three cognitive task pattern proxies per document across 22,000 sampled Pile documents (1,000/domain), then statistically test whether focal domain contrasts (Wikipedia vs Books vs GitHub) are significant and large-effect-size differences.

---

## 3. Functional Requirements

### FR-1: Data Loading and Sampling

**Description:** Stream and sample The Pile validation set with stratified per-domain sampling.

**Requirements:**
- FR-1.1: Load The Pile validation set via HuggingFace `load_dataset("EleutherAI/pile", split="validation", streaming=True)` OR `lm_dataformat.Reader("val.jsonl.zst")` as fallback
- FR-1.2: Filter to English documents using `langdetect` (reject non-English)
- FR-1.3: Filter documents with fewer than 100 tokens after spaCy tokenization
- FR-1.4: Sample exactly 1,000 documents per domain using fixed random seed = 42
- FR-1.5: Use `meta['pile_set_name']` field for domain label extraction
- FR-1.6: Support all 22 Pile domains; primary analysis focuses on Wikipedia (en), BookCorpus2/Bibliotik, Github

### FR-2: Cognitive Proxy Computation

**Description:** Compute three proxy metrics per document using spaCy `en_core_web_sm`.

**Requirements:**
- FR-2.1: Load spaCy model `en_core_web_sm` (includes NER + tokenizer components)
- FR-2.2: Truncate each document to 50,000 characters before processing (speed control)
- FR-2.3: Compute **entity_density** = `len(doc.ents) / max(n_non_space_tokens, 1)`
- FR-2.4: Compute **narrative_coherence** = `len({tok.lower_ for tok in tokens} ∩ CONNECTIVES) / max(n_non_space_tokens, 1)` where CONNECTIVES = {"however", "therefore", "moreover", "furthermore", "nevertheless", "consequently", "subsequently", "meanwhile", "although", "because", "whereas", "thus", "hence", "indeed", "additionally"}
- FR-2.5: Compute **formal_syntax_density** = `len(FORMAL_SYNTAX_RE.findall(text[:50000])) / max(n_non_space_tokens, 1)` where `FORMAL_SYNTAX_RE = re.compile(r'[{}\[\]()<>;]|def |class |import |return ')`
- FR-2.6: Return all three metrics as dict per document
- FR-2.7: Process documents in parallel using `multiprocessing.Pool` with `imap_unordered`, chunksize=128

### FR-3: Per-Domain Aggregation

**Description:** Aggregate per-document proxy scores into per-domain score lists.

**Requirements:**
- FR-3.1: Maintain `domain_scores[domain][proxy]` = list of floats across 1,000 sampled docs
- FR-3.2: Save aggregated scores to `results/domain_scores.json` (or `.pkl`) for reproducibility
- FR-3.3: Compute per-domain summary statistics: mean, std, 95% CI for each proxy

### FR-4: Statistical Analysis

**Description:** Apply one-way Welch's ANOVA and post-hoc pairwise tests.

**Requirements:**
- FR-4.1: Run one-way Welch's ANOVA for each of the 3 proxies across all 22 domains using `scipy.stats.f_oneway` with `equal_var=False`
- FR-4.2: Compute η² effect size = SS_between / SS_total from `statsmodels.api.stats.anova_lm(model, typ=2)`
- FR-4.3: Run Tukey HSD post-hoc pairwise comparisons via `statsmodels.stats.multicomp.pairwise_tukeyhsd` for focal contrasts:
  - Wikipedia (en) vs BookCorpus2/Bibliotik (entity density + narrative coherence)
  - Wikipedia (en) vs Github (entity density + formal syntax density)
  - BookCorpus2/Bibliotik vs Github (narrative coherence + formal syntax density)
- FR-4.4: Save ANOVA table and Tukey results to `results/statistical_results.csv`

### FR-5: Visualization

**Description:** Generate required and informative figures.

**Requirements:**
- FR-5.1: **Required Figure** — Bar chart of mean ± 95% CI for all 3 proxy metrics across all 22 domains, sorted by entity_density, saved to `figures/domain_proxy_comparison.png`
- FR-5.2: Violin plots of proxy distributions for 3 focal domains (Wikipedia, Books, GitHub), saved to `figures/focal_domain_violins.png`
- FR-5.3: Tukey HSD reject matrix heatmap (22×22) for entity_density, saved to `figures/tukey_heatmap_entity_density.png`
- FR-5.4: Scatter plot of entity_density vs narrative_coherence colored by domain, saved to `figures/proxy_correlation_scatter.png`
- FR-5.5: All figures output to `docs/youra_research/h-m1/figures/`

### FR-6: Results Reporting

**Description:** Generate machine-readable and human-readable results.

**Requirements:**
- FR-6.1: Save JSON summary with gate-relevant metrics: `{entity_density_wiki_mean, entity_density_books_mean, p_wiki_vs_books, eta_sq_entity, narrative_coherence_books_mean, narrative_coherence_wiki_mean, p_books_vs_wiki_coherence, eta_sq_coherence, gate_pass: bool}`
- FR-6.2: Print gate evaluation to stdout: "GATE PASS" if both primary criteria met, "GATE FAIL" otherwise
- FR-6.3: Save full results to `results/h_m1_results.json`

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | The Pile (validation set) |
| Source | HuggingFace: `EleutherAI/pile`, split=`validation` |
| Fallback | Direct download: `val.jsonl.zst` via lm_dataformat |
| Domain Labels | `meta['pile_set_name']` — 22 unique domains |
| Sample Size | 1,000 documents × 22 domains = 22,000 total |
| Min Doc Length | 100 tokens (post-spaCy tokenization) |
| Random Seed | 42 (fixed) |
| Language Filter | English only (langdetect) |

**Domains (22):**
Wikipedia (en), BookCorpus2, Bibliotik, Github, PubMed Central, ArXiv, FreeLaw, StackExchange, USPTO Backgrounds, OpenWebText2, EuroParl, HackerNews, YoutubeSubtitles, PhilPapers, NIH ExPorter, Enron Emails, DM Mathematics, Ubuntu IRC, OpenSubtitles, Gutenberg (PG-19), DM Mathematics, Pile-CC

### 4.2 NLP Model

| Field | Value |
|-------|-------|
| Name | spaCy en_core_web_sm |
| Version | Latest compatible with spaCy 3.x |
| Components Used | NER (for entity_density), tokenizer (all proxies) |
| Download | `python -m spacy download en_core_web_sm` |
| Fallback | en_core_web_trf (higher accuracy, slower) |

### 4.3 Statistical Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| scipy | f_oneway (Welch's ANOVA) | `pip install scipy` |
| statsmodels | anova_lm (η²), pairwise_tukeyhsd | `pip install statsmodels` |
| pandas | Long-format DataFrame for statsmodels | `pip install pandas` |
| lm_dataformat | Pile data streaming | `pip install lm_dataformat` |
| langdetect | Language filtering | `pip install langdetect` |
| matplotlib | Figures | `pip install matplotlib` |
| seaborn | Violin plots, heatmaps | `pip install seaborn` |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- NFR-1.1: End-to-end runtime ≤ 6 hours on single CPU (target: 2–4 hours)
- NFR-1.2: Memory usage ≤ 16 GB RAM (streaming loading)

### NFR-2: Reproducibility
- NFR-2.1: Fixed random seed = 42 for all sampling operations
- NFR-2.2: All intermediate results saved to disk before statistical analysis
- NFR-2.3: Environment lockfile (`requirements.txt`) pinned

### NFR-3: Code Quality
- NFR-3.1: Single entrypoint script `run_experiment.py` with CLI args
- NFR-3.2: Progress logging per domain (tqdm or print)
- NFR-3.3: Graceful handling of domains with < 1,000 qualifying documents (log warning, use all available)

### NFR-4: Consistency with H-E1
- NFR-4.1: Use same 22-domain taxonomy (`pile_set_name`) as H-E1
- NFR-4.2: Use same lm_dataformat streaming pattern as H-E1 where applicable

---

## 6. Success Criteria

### 6.1 Gate Criteria (MUST_WORK)

| Criterion | Threshold | Test |
|-----------|-----------|------|
| Entity density: Wikipedia > Books | p < 0.05, η² > 0.1 | Welch's ANOVA + Tukey HSD |
| Narrative coherence: Books > Wikipedia | p < 0.05 | Tukey HSD pairwise |
| Code runs without error | 0 uncaught exceptions | Integration test |

### 6.2 Supporting Criteria (Informational)

| Criterion | Expected | Test |
|-----------|----------|------|
| entity_density(Wikipedia) | ≈ 0.08–0.15 | Point estimate check |
| narrative_coherence(Books) ≥ 2× Wikipedia | ratio ≥ 2.0 | Point estimate check |
| formal_syntax_density(GitHub) ≫ Wikipedia | ratio ≥ 5.0 | Point estimate check |

---

## 7. Dependencies

### 7.1 Python Packages

```
spacy>=3.7.0
en-core-web-sm  # via python -m spacy download
scipy>=1.11.0
statsmodels>=0.14.0
pandas>=2.0.0
lm_dataformat>=0.0.21
langdetect>=1.0.9
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
datasets>=2.14.0  # HuggingFace (fallback loader)
```

### 7.2 External Repositories (Reference Only)

| Repository | URL | Purpose |
|------------|-----|---------|
| pile-explorer | https://github.com/EleutherAI/pile-explorer | Domain sampling pattern reference |
| tagged-pile | https://github.com/EleutherAI/tagged-pile | SpaCy pipeline reference |

### 7.3 Data Downloads (Manual)

- The Pile validation set: `val.jsonl.zst` from EleutherAI/the_pile release page (if not using HF streaming)
- HuggingFace streaming (recommended): No manual download required — `load_dataset("EleutherAI/pile", streaming=True)` handles it

---

## 8. Out of Scope

- Neural model training or fine-tuning
- Ablation variants (single pipeline design)
- Real-time inference
- Other corpora beyond The Pile
- Hypothesis H-M2/H-M3 regression analysis (separate experiments)

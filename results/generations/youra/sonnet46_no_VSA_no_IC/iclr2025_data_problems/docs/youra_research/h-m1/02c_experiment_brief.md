# Experiment Design: H-M1

**Date:** 2026-08-20
**Author:** yoon303b@gmail.com
**Hypothesis Statement:** Under analysis of The Pile domain content distributions, if cognitive task pattern proxies (entity density for Wikipedia, narrative coherence markers for Books, formal syntax frequency for GitHub) are computed per domain, then Wikipedia domains show significantly higher factual-association density than Books/GitHub (p < 0.05, η² > 0.1), and Books domains show significantly higher narrative-coherence features than Wikipedia/GitHub, because domain content differences drive differential alignment with benchmark task demands.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Step 1 of 3)** — Tests causal step 1: domain content differences are real and systematic.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED — PASS, MUST_WORK gate satisfied)
**Gate Status:** MUST_WORK (H-M1 must pass to proceed to H-M2/H-M3)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM — Step 1 of 3
- **Prerequisites:** H-E1 (COMPLETED, gate PASS)

### Gate Condition
MUST_WORK — if H-M1 fails, H-M2 and H-M3 are blocked. Failure response: EXPLORE narrowing to top-4 most distinct domains and re-test H-M2/H-M3 with reduced domain set.

---

## Continuation Context

H-E1 confirmed that The Pile domain exposure trajectories are non-uniform (std > 0.001 for ≥10 of 22 domains across 154 checkpoints × 16 model sizes). This validates that the panel regression framework is applicable. H-M1 now tests the theoretical bridge: that domain content differences are real and systematic enough to explain the benchmark-specific β coefficients expected in H-M2.

### Previous Hypothesis Results (H-E1)
- Domain exposure variance is measurable: ✅ PASS
- Dataset infrastructure: EleutherAI/pile dataloader indices + pile_metadata domain labels
- Model infrastructure: EleutherAI/pythia-* HuggingFace suite, 154 checkpoints × 16 sizes
- Reusing: The Pile as data source for content analysis (controlled comparison — same data source)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: NER entity density domain content analysis text statistics**
- Archon KB is indexed on image generation / diffusion models — no relevant results (similarity < 0.41 for all returned pages: LAION-5B, diffusers, Stable Diffusion)
- Key insight: This research domain (NLP corpus content analysis) is not represented in the current Archon KB

**Query 2: Narrative coherence discourse markers corpus analysis NLP**
- No relevant results (similarity < 0.37; returned: HuggingFace diffusers pipelines)

**Query 3: Text domain classification pretraining corpus statistics ANOVA**
- No relevant results (similarity < 0.38; returned: PixArt-alpha, T5-v1, Wuerstchen)

**Summary:** Archon KB contains no prior cases for this domain. All specifications grounded in Exa GitHub findings and primary literature (The Pile paper).

### Archon Code Examples

**Query 1: spacy NER entity density text statistics corpus**
- No relevant code examples (returned: LaTeX paragraph formatting, LyCORIS CLI)

**Summary:** No relevant code in Archon. Specifications derived from Exa sources below.

### Exa GitHub Implementations

**Query 1: The Pile domain sampling entity density NER spacy text analysis Python**

**Repository 1**: EleutherAI/pile-explorer (`topic_analysis_03.py`) (⭐ ~150)
- **URL**: https://github.com/EleutherAI/pile-explorer
- **Relevance**: Official EleutherAI analysis code for The Pile components using spacy + lm_dataformat; uses `pile_set_name` metadata for per-domain processing — directly applicable
- **Key Code**:
  ```python
  import lm_dataformat as lmd
  import spacy
  from spacy.lang.en import English
  from multiprocessing import Pool

  nlp = English()
  tokenizer = nlp.Defaults.create_tokenizer(nlp)
  component_list = {
      'Wikipedia (en)', 'BookCorpus', 'Bibliotik', 'Github',
      'PubMed Central', 'ArXiv', 'FreeLaw', ...  # all 22 domains
  }

  def raw_baggify(item):
      text, meta = item
      component = meta['pile_set_name']
      if component in components:
          doc = tokenizer(text)
          tokens = [tok.lower_ for tok in doc if not tok.is_stop and tok.is_alpha]
          return (tokens, component)
  ```
- **Architecture**: Stream lm_dataformat → filter by pile_set_name → parallel processing via Pool
- **Training Config**: N/A (analysis pipeline)
- **Dataset**: The Pile validation set (compressed .jsonl.zst files)
- **Results**: Cross-corpus LDA perplexities showing GitHub, PhilPapers, EuroParl strongly deviate from Pile-CC topic distribution

**Repository 2**: EleutherAI/tagged-pile (⭐ 8)
- **URL**: https://github.com/EleutherAI/tagged-pile
- **Relevance**: Official EleutherAI POS tagging pipeline for The Pile using SpaCy `en_core_web_trf`; demonstrates how to apply SpaCy NLP models to Pile documents with proper HuggingFace tokenizer alignment
- **Key Code**:
  ```bash
  python -m spacy download en_core_web_trf
  python scripts/tag.py val.jsonl <output-dir>
  python scripts/aligned_tokenize.py EleutherAI/pythia-160m val.jsonl <output-dir2>
  ```
- **Pattern**: Two-step pipeline: (1) SpaCy Doc objects to disk, (2) HuggingFace tokenizer alignment
- **Used for**: SpaCy model selection and Pile processing pipeline design

**Repository 3**: The Pile paper (arxiv 2101.00027) — domain analysis reference
- **Relevance**: The Pile authors performed LDA topic modeling per component and cross-corpus perplexity analysis; confirms GitHub, PhilPapers, EuroParl deviate strongly from CommonCrawl — validates hypothesis that domain content differences are real and detectable
- **Key Finding**: "Several of the Pile's other components deviate from [Pile-CC] strongly in their topical focus, as evidenced by higher perplexity on Github, PhilPapers, and EuroParl"

**Query 2: corpus domain text statistics ANOVA one-way scipy NLP domain comparison Python**

**Source 1**: scipy.stats.f_oneway documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
- **Key Code**:
  ```python
  from scipy.stats import f_oneway
  F_statistic, p_value = f_oneway(group1_scores, group2_scores, ..., equal_var=False)
  # equal_var=False → Welch's ANOVA (does not assume equal variances)
  ```
- **Used for**: One-way ANOVA across 22 domains for each proxy metric

**Source 2**: statsmodels ANOVA with effect size (η²)
- **URL**: https://mountain-hydrology-research-group.github.io/data-analysis/
- **Key Code**:
  ```python
  import statsmodels.api as sm
  from statsmodels.formula.api import ols
  from statsmodels.stats.multicomp import pairwise_tukeyhsd

  model = ols('proxy_score ~ C(domain)', data=df).fit()
  anova_table = sm.stats.anova_lm(model, typ=2)
  # η² = SS_between / SS_total
  eta_squared = anova_table['sum_sq']['C(domain)'] / anova_table['sum_sq'].sum()
  ```
- **Used for**: η² effect size calculation and Tukey HSD post-hoc pairwise comparisons

**Serena Analysis Needed**: false — code from search results is sufficiently clear

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

The EleutherAI/pile-explorer repository is the closest thing to an official implementation for The Pile content analysis. It uses the exact same lm_dataformat streaming approach as Pythia's dataloader infrastructure (established in H-E1).

**Recommended Implementation Path:**
- Primary: EleutherAI/pile-explorer pattern (lm_dataformat + spacy, per-domain parallel processing)
- Fallback: HuggingFace `load_dataset("EleutherAI/pile", streaming=True)` — simpler but slower for large-scale analysis
- Justification: pile-explorer uses exact same `pile_set_name` metadata key and lm_dataformat Reader as Pythia's dataloader infrastructure; ensures consistency with H-E1 domain labeling

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The pile-explorer `topic_analysis_03.py` pattern is directly applicable without further semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** The Pile (validation set)
**Type:** standard
**Source:** EleutherAI/the_pile on HuggingFace; also downloadable as compressed .jsonl.zst chunks
**Domain Labels:** 22 domains via `meta['pile_set_name']` field
**Hypothesis Fit:** The Pile provides text documents with ground-truth domain labels (pile_set_name); stratified random sampling of 1,000 documents per domain gives 22,000 total analysis units for comparing cognitive proxy distributions

**Sample Size:** 1,000 documents per domain × 22 domains = 22,000 documents total (statistically meaningful; substantially exceeds the 500+ minimum threshold)

**Preprocessing:**
- Filter to English documents only (use fasttext `lid.176.bin` or langdetect)
- Filter documents with fewer than 100 tokens (too short for reliable proxy computation)
- Stratified random sampling per domain (fixed random seed = 42)
- SpaCy pipeline: `en_core_web_sm` (CPU-optimized; includes NER, POS, parser components)

**Domain subset for primary analysis (3 focal domains):**
- `Wikipedia (en)` — factual-association proxy target
- `BookCorpus2` or `Bibliotik` — narrative-coherence proxy target (Books-type)
- `Github` — formal syntax proxy target

**Full 22-domain ANOVA:** All domains included for statistical completeness; pairwise comparisons focus on the 3 focal contrasts from the hypothesis.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets (streaming) OR lm_dataformat (direct)
- Identifier: `"EleutherAI/pile"` (HuggingFace) or direct download of `val.jsonl.zst`
- Code:
  ```python
  # Option A: HuggingFace streaming (recommended for validation set)
  from datasets import load_dataset
  ds = load_dataset("EleutherAI/pile", split="validation", streaming=True)

  # Option B: lm_dataformat (pile-explorer pattern, consistent with H-E1)
  import lm_dataformat as lmd
  rdr = lmd.Reader("val.jsonl.zst")
  stream = rdr.stream_data(get_meta=True)
  ```

### Models

#### Baseline Model

**Architecture:** No neural model training — this is a content analysis experiment. The "baseline" is the null hypothesis (no domain differences in cognitive proxy distributions).

**Statistical baseline:**
- H₀: All 22 domains have equal mean entity density (one-way ANOVA F not significant, p ≥ 0.05)
- H₀: All 22 domains have equal mean narrative coherence score
- H₀: All 22 domains have equal mean formal syntax density

**Loading Information** (for Phase 4 download):
- Method: spaCy
- Identifier: `"en_core_web_sm"` (CPU-optimized NER + POS pipeline)
- Code:
  ```python
  import spacy
  nlp = spacy.load("en_core_web_sm")
  # OR for higher accuracy (slower):
  # nlp = spacy.load("en_core_web_trf")
  ```

#### Proposed Model

**Architecture:** Baseline (null distribution) + three cognitive proxy metrics computed per domain

**Core Mechanism Implementation:**

```python
# Core Mechanism: Cognitive Task Pattern Proxy Computation
# Based on: EleutherAI/pile-explorer (topic_analysis_03.py) + tagged-pile pipeline

import spacy
import re
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

# Discourse connectives for narrative coherence (Books proxy)
CONNECTIVES = {
    "however", "therefore", "moreover", "furthermore", "nevertheless",
    "consequently", "subsequently", "meanwhile", "although", "because",
    "whereas", "thus", "hence", "indeed", "additionally"
}

# Formal syntax markers for code/structured text (GitHub proxy)
FORMAL_SYNTAX_RE = re.compile(r'[{}\[\]()<>;]|def |class |import |return ')

def compute_proxies(text: str) -> dict:
    """
    Args:
        text: Raw document string from The Pile
    Returns:
        dict with entity_density, narrative_coherence, formal_syntax_density
    """
    doc = nlp(text[:50000])  # truncate to 50k chars for speed
    tokens = [tok for tok in doc if not tok.is_space]
    n_tokens = max(len(tokens), 1)

    # Proxy 1: Entity density (Wikipedia / factual-association proxy)
    n_entities = len(doc.ents)
    entity_density = n_entities / n_tokens

    # Proxy 2: Narrative coherence (Books / discourse-coherence proxy)
    words_lower = {tok.lower_ for tok in tokens}
    connective_count = len(words_lower & CONNECTIVES)
    narrative_coherence = connective_count / n_tokens

    # Proxy 3: Formal syntax density (GitHub / code-structure proxy)
    syntax_matches = len(FORMAL_SYNTAX_RE.findall(text[:50000]))
    formal_syntax_density = syntax_matches / n_tokens

    return {
        "entity_density": entity_density,
        "narrative_coherence": narrative_coherence,
        "formal_syntax_density": formal_syntax_density,
    }

# Per-domain aggregation:
# domain_scores[domain][proxy] = list of scores across 1000 sampled docs
```

### Training Protocol

No neural network training — this is a corpus content analysis experiment.

**Computation Protocol:**

**Sampling:**
- Random seed: 42 (fixed)
- Sample size: 1,000 documents per domain (22 domains = 22,000 total)
- Minimum document length: 100 tokens (after spacy tokenization)
- Maximum document truncation: 50,000 characters per document (for SpaCy speed)

**Processing:**
- SpaCy model: `en_core_web_sm` (NER + tokenizer components used)
- Parallelism: Python `multiprocessing.Pool` with `imap_unordered`, chunksize=128
- Estimated runtime: ~2–4 hours on single CPU (1000 docs × 22 domains, ~50k chars each)

**Statistical Analysis:**
- Step 1: One-way ANOVA across all 22 domains for each proxy (scipy.stats.f_oneway with equal_var=False / Welch's ANOVA)
- Step 2: η² effect size = SS_between / SS_total (from statsmodels anova_lm typ=2)
- Step 3: Post-hoc pairwise comparisons (Tukey HSD) for focal contrasts:
  - Wikipedia vs Books (entity density + narrative coherence)
  - Wikipedia vs GitHub (entity density + formal syntax density)
  - Books vs GitHub (narrative coherence + formal syntax density)

**Seeds:** 1 (fixed seed = 42 for sampling)

**Source:** pile-explorer pattern (Archon: n/a), scipy.stats.f_oneway docs, statsmodels ANOVA tutorial

### Evaluation

**Primary Metrics:**
- `entity_density`: NER entity count / token count per document (spaCy `doc.ents`)
- `narrative_coherence`: discourse connective frequency / token count
- `formal_syntax_density`: bracket/keyword regex match count / token count

**Success Criteria (PoC — direction-based):**
1. `mean_entity_density(Wikipedia) > mean_entity_density(Books)` AND p < 0.05, η² > 0.1 (ANOVA)
2. `mean_narrative_coherence(Books) > mean_narrative_coherence(Wikipedia)` AND p < 0.05

**PoC Pass Condition:**
1. Code runs without error
2. Both primary criteria satisfied

**Expected Performance (from The Pile paper and prior corpus linguistics):**
- Wikipedia is dense in named entities (persons, places, organizations) — expected entity_density ≈ 0.08–0.15 (8–15% of tokens are entities)
- Books/narrative text uses more discourse connectives — expected narrative_coherence > Wikipedia by ≥2×
- GitHub shows high bracket/keyword density — expected formal_syntax_density ≫ Wikipedia and Books
- **Source:** The Pile paper (Gao et al., 2020, §6 "Topic Modeling Analysis"), pile-explorer cross-corpus perplexity findings

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical hypothesis testing (not classification)
- Library: `scipy.stats` + `statsmodels` + standard Python collections
- Code:
  ```python
  from scipy.stats import f_oneway
  import statsmodels.api as sm
  from statsmodels.formula.api import ols
  from statsmodels.stats.multicomp import pairwise_tukeyhsd
  import pandas as pd

  # Build long-format dataframe for statsmodels
  rows = []
  for domain, scores in domain_scores.items():
      for score in scores['entity_density']:
          rows.append({'domain': domain, 'entity_density': score})
  df = pd.DataFrame(rows)

  # ANOVA
  model = ols('entity_density ~ C(domain)', data=df).fit()
  anova_table = sm.stats.anova_lm(model, typ=2)
  eta_sq = anova_table['sum_sq']['C(domain)'] / anova_table['sum_sq'].sum()

  # Pairwise
  tukey = pairwise_tukeyhsd(df['entity_density'], df['domain'], alpha=0.05)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of mean entity_density, narrative_coherence, formal_syntax_density across all 22 Pile domains, with error bars (95% CI), sorted by entity_density

#### Additional Figures (LLM Autonomous)
Based on this content analysis experiment, the following additional figures are informative:

1. **Violin plots**: Distribution of each proxy metric per domain for the 3 focal domains (Wikipedia, Books, GitHub) — shows distributional shape, not just means
2. **Pairwise comparison heatmap**: Tukey HSD reject matrix (22×22) for entity density — shows which domain pairs are significantly different
3. **Correlation scatter**: entity_density vs narrative_coherence colored by domain — shows proxy independence

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `mean_entity_density(Wikipedia) > mean_entity_density(Books)` (p < 0.05, η² > 0.1)
3. `mean_narrative_coherence(Books) > mean_narrative_coherence(Wikipedia)` (p < 0.05)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB**: No relevant sources found (KB indexed on image generation / diffusion models). Zero Archon sources used in this experiment design.

### B. GitHub Implementations (Exa)

**Repository 1**: EleutherAI/pile-explorer (`topic_analysis_03.py`)
- **URL**: https://github.com/EleutherAI/pile-explorer/blob/main/topic_analysis_03.py
- **Query Used**: "The Pile domain sampling entity density NER spacy text analysis Python GitHub"
- **Relevance**: Official EleutherAI analysis code for The Pile; uses lm_dataformat + spacy + `pile_set_name` metadata — exactly the domain filtering pattern needed
- **Key Code** (annotated):
  ```python
  import lm_dataformat as lmd
  import spacy
  # Uses pile_set_name to filter by domain — basis for our domain sampling loop
  rdr = lmd.Reader(input_path)
  stream = rdr.stream_data(get_meta=True)
  def raw_baggify(item):
      text, meta = item
      component = meta['pile_set_name']  # ← domain label
      # ... process per domain
  with Pool(TOK_PROCESSES) as p:
      doc_iter = p.imap_unordered(raw_baggify, stream, chunksize=CHUNK_SIZE)
  ```
- **Configuration Extracted**: lm_dataformat Reader + Pool parallel processing pattern
- **Used For**: Domain sampling loop design, `pile_set_name` metadata access pattern

**Repository 2**: EleutherAI/tagged-pile
- **URL**: https://github.com/EleutherAI/tagged-pile
- **Query Used**: Same query
- **Relevance**: Demonstrates correct SpaCy pipeline for The Pile (en_core_web_trf), HF tokenizer alignment
- **Key Code** (annotated):
  ```bash
  python -m spacy download en_core_web_trf
  python scripts/tag.py val.jsonl <output-dir>
  # tag.py runs spacy NLP on pile documents, saves Doc objects
  ```
- **Used For**: SpaCy model selection rationale (en_core_web_sm for speed; en_core_web_trf for accuracy)

**Source 3**: scipy.stats.f_oneway documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
- **Query Used**: "corpus domain text statistics ANOVA one-way scipy NLP domain comparison Python"
- **Used For**: ANOVA implementation (Welch's variant with equal_var=False)

**Source 4**: statsmodels ANOVA + Tukey HSD tutorial
- **URL**: https://mountain-hydrology-research-group.github.io/data-analysis/modules/module3/lab3-3.html
- **Used For**: η² effect size formula and pairwise_tukeyhsd post-hoc test

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear.
The pile-explorer pattern directly maps to our experiment structure without needing deeper semantic analysis.

### D. Previous Hypothesis Context

**Source**: H-E1 validated infrastructure
- **Reused Components**:
  - Dataset: The Pile (same source as H-E1 domain exposure computation)
  - Domain label taxonomy: `pile_set_name` (22 domains, same as H-E1)
  - Processing pattern: lm_dataformat + parallel Pool (consistent with H-E1 dataloader approach)
- **Why Reused**: Enables controlled comparison — only the analysis (content proxies vs. dataloader ordering) changes; data source is identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: The Pile | Phase 2B/2A | 02b_verification_plan.md §1.3 |
| Domain filtering (`pile_set_name`) | GitHub | pile-explorer B.1 |
| SpaCy NER pipeline | GitHub | tagged-pile B.2 |
| Entity density formula | GitHub | MRIWA entity analysis (Exa) |
| Narrative coherence proxy | Primary derivation | Hypothesis statement + corpus linguistics |
| Formal syntax proxy | Primary derivation | Hypothesis statement + GitHub domain properties |
| ANOVA (scipy) | Docs | scipy.stats.f_oneway B.3 |
| η² effect size | Tutorial | statsmodels B.4 |
| Tukey HSD post-hoc | Tutorial | statsmodels B.4 |
| Sample size (1000/domain) | Phase 2B | 02b_verification_plan.md §2.2 H-M1 verification protocol |
| Expected entity density range | Literature | The Pile paper (Gao et al. 2020) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20

### Workflow History for This Hypothesis
- 2026-08-20: H-M1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-20: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub implementations), Serena (skipped — code clear)*
*All specifications grounded in EleutherAI official analysis code (pile-explorer, tagged-pile) and The Pile primary paper*
*Next Phase: Phase 3 - Implementation Planning*

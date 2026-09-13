# Experiment Design: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Under the condition of examining ML publication records (2019-2021), if foundation models represent a paradigm shift, then GPT-3 (2020), ViT (2020), and BERT successors are identifiable as high-impact papers with citation counts exceeding field medians by >2σ.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanism in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 PASS)
**Gate Status:** MUST_WORK - Pending validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** Foundation model papers (GPT-3, ViT, BERT) have citation impact >2σ above field median
- **Fail Action:** STOP - no paradigm shift evidence

---

## Continuation Context

This hypothesis validates that foundation model emergence actually occurred as hypothesized. H-E1 confirmed existence of phase transition signal (change points at 2019-04 and 2021-03). H-M1 tests whether foundation models were significant enough to plausibly drive this ecosystem change.

### Previous Hypothesis Results (if applicable)
**H-E1 (COMPLETED - PASS):**
- PELT detected 2 change points: 2019-04, 2021-03
- BIC improvement: 17.13 (segmented model better than monotonic)
- Validates existence of structural break in concentration dynamics

---

## Implementation Research Summary

### Archon Knowledge Base Findings

- Limited direct matches for citation impact analysis in KB
- Foundation model papers (GPT-3, BERT, ViT) well-documented in academic literature
- Statistical analysis methods (z-score, field normalization) are standard

### Archon Code Examples

- BibTeX citation examples for FlashAttention, QLoRA, DALL-E 2, Stable Diffusion
- No direct Semantic Scholar API code in KB

### Exa GitHub Implementations

**Semantic Scholar API:**
- Official Python library: `semanticscholar` (PyPI)
- API endpoint: `https://api.semanticscholar.org/graph/v1/paper/`
- Key fields: `citationCount`, `influentialCitationCount`, `year`, `venue`
- Batch endpoint: `/paper/batch` for multiple papers
- Search with `min_citation_count` filter, `sort='citationCount:desc'`

**Code Pattern (from semanticscholar docs):**
```python
from semanticscholar import SemanticScholar
sch = SemanticScholar()
paper = sch.get_paper('ARXIV:2005.14165')  # GPT-3
# Returns: paperId, title, citationCount, year, authors
```

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a statistical analysis task, not model reproduction. Use Semantic Scholar API directly.

**Recommended Implementation Path:**
- Primary: Semantic Scholar Python library (`pip install semanticscholar`)
- Fallback: Direct REST API calls to `api.semanticscholar.org`
- Justification: Official API provides citation counts and field metadata; no ML model training required

### Code Analysis (Serena MCP)

*Skipped - No local codebase to analyze. This is a data analysis task using external API.*

---

## Experiment Specification

### Dataset

**Name:** Semantic Scholar Academic Graph API
**Type:** programmatic-api (real data via API)
**Source:** https://api.semanticscholar.org/

**Target Papers (Foundation Models):**
| Paper | ArXiv ID | Year | Expected High Impact |
|-------|----------|------|---------------------|
| GPT-3 | 2005.14165 | 2020 | Yes |
| ViT | 2010.11929 | 2020 | Yes |
| BERT | N19-1423 (ACL) | 2019 | Yes |
| RoBERTa | 1907.11692 | 2019 | Yes |
| T5 | 1910.10683 | 2019 | Yes |

**Comparison Set:** ML papers from same venues/years (2019-2021)
- Sample size: 1000+ papers per year from top ML venues (NeurIPS, ICML, ACL, CVPR)
- Filter: `fieldsOfStudy=Computer Science`, `year=2019:2021`

**Loading Information** (for Phase 4 download):
- Method: API
- Identifier: Semantic Scholar Graph API v1
- Code:
```python
from semanticscholar import SemanticScholar
sch = SemanticScholar()

# Foundation model papers
foundation_papers = [
    'ARXIV:2005.14165',  # GPT-3
    'ARXIV:2010.11929',  # ViT
    'ACL:N19-1423',      # BERT
    'ARXIV:1907.11692',  # RoBERTa
    'ARXIV:1910.10683',  # T5
]

# Get citation counts
for paper_id in foundation_papers:
    paper = sch.get_paper(paper_id, fields=['citationCount', 'year', 'venue'])
```

### Models

#### Baseline Model

**Type:** Statistical comparison (no ML model)
**Method:** Field citation distribution analysis
- Compute mean and standard deviation of citation counts for ML papers (2019-2021)
- Use papers from same venues as foundation models for fair comparison

**Loading Information** (for Phase 4 download):
- Method: Semantic Scholar bulk search
- Identifier: ML papers 2019-2021
- Code:
```python
# Get comparison distribution
results = sch.search_paper(
    query='machine learning',
    year='2019-2021',
    fields_of_study=['Computer Science'],
    bulk=True,
    fields=['citationCount', 'year', 'venue']
)
```

#### Proposed Model

**Architecture:** Z-score computation for citation impact

**Core Mechanism Implementation:**

```python
import numpy as np
from semanticscholar import SemanticScholar

def compute_citation_zscore(foundation_papers, comparison_papers):
    """
    Compute z-score of foundation model paper citations
    relative to field distribution.
    
    Args:
        foundation_papers: List of paper IDs for foundation models
        comparison_papers: List of citation counts from field
    
    Returns:
        dict: {paper_id: z_score} for each foundation paper
    """
    sch = SemanticScholar()
    
    # Compute field statistics
    field_citations = [p['citationCount'] for p in comparison_papers]
    field_mean = np.mean(field_citations)
    field_std = np.std(field_citations)
    
    results = {}
    for paper_id in foundation_papers:
        paper = sch.get_paper(paper_id, fields=['citationCount', 'title'])
        citation_count = paper['citationCount']
        
        # Z-score: (x - mean) / std
        z_score = (citation_count - field_mean) / field_std
        results[paper_id] = {
            'title': paper['title'],
            'citations': citation_count,
            'z_score': z_score,
            'exceeds_2sigma': z_score > 2.0
        }
    
    return results

def validate_hypothesis(results):
    """
    H-M1 passes if foundation papers have z > 2.0
    """
    passing = [p for p in results.values() if p['exceeds_2sigma']]
    return len(passing) >= 3  # At least 3 of 5 foundation papers
```

### Training Protocol

**Not applicable** - This is statistical analysis, not ML training.

**Execution Protocol:**
1. Fetch foundation model paper metadata via Semantic Scholar API
2. Fetch comparison set (1000+ ML papers, same years/venues)
3. Compute field mean and std of citation counts
4. Compute z-scores for each foundation paper
5. Validate z > 2.0 for majority of foundation papers

### Evaluation

**Primary Metric:** Z-score of citation count relative to field median
- **Success Threshold:** z > 2.0 (foundation papers exceed field by >2σ)

**Secondary Metrics:**
- Absolute citation counts
- Percentile rank within field
- Timeline alignment (papers published 2019-2021)

**Gate Pass Condition:**
- At least 3 of 5 foundation papers have z > 2.0
- Timeline confirms 2019-2021 emergence window

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis
- Library: numpy, scipy.stats
- Code:
```python
import numpy as np
from scipy import stats

# Z-score computation
z_score = (citation_count - field_mean) / field_std

# Alternative: percentile rank
percentile = stats.percentileofscore(field_citations, citation_count)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing z-scores for each foundation paper with 2σ threshold line

#### Additional Figures (LLM Autonomous)

1. **Citation Distribution**: Histogram of field citation counts with foundation papers marked
2. **Timeline Plot**: Foundation paper citations over time (2019-2024)
3. **Percentile Rank Table**: Foundation papers ranked by percentile in field

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. At least 3 of 5 foundation model papers show z > 2.0 citation impact

---

## Appendix: Reference Implementations

### Semantic Scholar API
- **Documentation:** https://api.semanticscholar.org/api-docs/
- **Python Library:** https://semanticscholar.readthedocs.io/
- **GitHub:** https://github.com/danielnsilva/semanticscholar

### Key Papers (Semantic Scholar IDs)
| Paper | Semantic Scholar ID | ArXiv |
|-------|---------------------|-------|
| GPT-3 | ARXIV:2005.14165 | 2005.14165 |
| ViT | ARXIV:2010.11929 | 2010.11929 |
| BERT | ACL:N19-1423 | N/A (ACL) |
| RoBERTa | ARXIV:1907.11692 | 1907.11692 |
| T5 | ARXIV:1910.10683 | 1910.10683 |

### Citation Analysis Methods
- Z-score computation: Standard statistical method
- Field normalization: Compare to papers from same venue/year
- Reference: Koch et al. (2021) for ML benchmark concentration analysis

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: H-E1 completed (PASS) - Change points detected
- 2026-08-18: H-M1 set to IN_PROGRESS
- 2026-08-18: Phase 2C experiment design initiated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

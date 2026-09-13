# WebOrganizer: Organize the Web — Constructing Domains Enhances Pre-Training Data Curation

## Key Metadata
- **Authors:** Alexander Wettig et al.
- **Year:** 2025
- **Venue:** arXiv 2502.10341 (78 citations)
- **Core Contribution:** Introduces a two-axis domain taxonomy (topic × format) for web data that, when used for domain-aware mixing, improves pre-training benchmark performance; demonstrates that domain mixing complements quality filtering.

## Section Summaries

### Abstract
Web pre-training data is typically treated as a monolithic corpus. WebOrganizer builds a structured domain taxonomy organizing web documents along two axes: topic (STEM, humanities, news, etc.) and format (instructional, narrative, reference, etc.). Using this taxonomy for domain-aware mixing at training time significantly improves downstream benchmark performance compared to mixing-agnostic quality filtering.

### Introduction & Motivation
Quality-based filtering (perplexity, heuristics) treats all high-quality text as interchangeable, ignoring domain-specific characteristics that affect downstream specialization. WebOrganizer hypothesizes that explicit domain control (what types of text, in what proportions) provides orthogonal signal to quality filtering, and that combining both leads to better pre-training corpora.

### Methodology
**Taxonomy Construction:** Two-dimensional grid: 8 topic categories × 5 format categories = 40 domain cells. Classifier trained on human-labeled seed set (~50K examples) to assign each web document to a domain cell. **Domain-Aware Mixing:** Given a token budget, sample from domain cells according to a target mixing distribution (optimized via DoReMi-style proxy model). **Quality Filtering Layer:** Applied before domain assignment; uses standard quality heuristics (CCNET-style). **Training:** 1B Llama architecture, 100B tokens, C4 and FineWeb as base corpora. **Evaluation:** MMLU, HellaSwag, ARC-C, WinoGrande, BoolQ, BBH.

### Experiments & Results
| Condition | Avg Benchmark Score |
|-----------|--------------------|-
| Quality filter only (baseline) | 55.3 |
| Domain mixing only (no quality filter) | 56.1 |
| Quality filter + domain mixing | 57.8 |
| Additive gain of combination | +2.5 vs baseline |

Domain mixing alone outperforms quality filtering alone by +0.8pp. Combination is more than additive (+2.5 vs. expected +1.8 from sum), suggesting synergistic effect. Key ablation: topic axis alone +1.2pp; format axis alone +0.6pp; both axes together +1.9pp (super-additive). Gain consistent across MMLU (+3.1), HellaSwag (+1.8), ARC-C (+2.2).

### Discussion & Conclusion
Domain mixing and quality filtering address orthogonal aspects of data quality: what domain and how well-written. Combining them is super-additive. Limitation: mixing ratios were optimized with a proxy model; interaction with perplexity filtering at different thresholds not systematically explored. Single scale (1B) only.

## Key Contributions
- Two-axis web domain taxonomy (topic × format)
- Domain-aware mixing is complementary to quality filtering (super-additive)
- Domain mixing alone outperforms quality filtering alone

## Potential Relevance
Critical for Gap 1 hypothesis design: WebOrganizer shows domain mixing is a distinct, orthogonal curation axis from quality filtering. A controlled multi-axis ablation must include domain mixing as a separate dimension. The super-additive combination effect also suggests interaction terms in the experimental design — simply varying one axis while fixing others may miss interaction effects. The single-scale limitation (1B) is the confound we need the Pythia multi-scale suite to resolve.

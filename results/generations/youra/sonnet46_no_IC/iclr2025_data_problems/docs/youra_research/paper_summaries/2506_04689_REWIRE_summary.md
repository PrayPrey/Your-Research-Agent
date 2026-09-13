# REWIRE: Recycling the Web — A Method to Enhance Pre-training Data Quality

## Key Metadata
- **Authors:** Thao Nguyen et al.
- **Year:** 2025
- **Venue:** arXiv 2506.04689
- **Core Contribution:** Transforms discarded low-quality documents into usable pre-training data via LM-guided rewriting, yielding +1.0–2.5pp improvement across 22 downstream tasks at 1–7B scale.

## Section Summaries

### Abstract
Standard quality filtering pipelines discard a substantial fraction of web data (often 30–60%) as low-quality. REWIRE recycles these discarded documents by rewriting them with a small LM into higher-quality text while preserving factual content. The resulting "recycled" data, when added to the pre-training corpus, improves downstream benchmark performance by 1.0–2.5pp across 22 tasks.

### Introduction & Motivation
Current curation pipelines implement binary quality filtering: high-quality documents pass, low-quality are discarded. This wastes potentially useful factual content embedded in poorly-formatted or linguistically low-quality text (e.g., forum posts, product descriptions, government documents). REWIRE asks: can discarded documents be salvaged through automated rewriting without introducing hallucinations?

### Methodology
REWIRE operates in three stages: (1) **Quality Classification:** existing quality classifier identifies low-quality documents discarded by standard filtering (threshold: bottom 40% by quality score); (2) **Rewriting:** a 7B-parameter rewriter LM (fine-tuned on (low-quality, high-quality) pairs for the same content) rewrites each document; (3) **Validation:** a lightweight classifier filters out rewritten documents that score below the pass threshold for original high-quality data. The rewriter is trained on ~100K aligned pairs extracted from Wikipedia edits and news article revisions. Pre-training uses Llama architecture at 1B and 7B scale, 200B tokens. Evaluation: 22 tasks covering reasoning, knowledge, language understanding (MMLU, HellaSwag, ARC, BoolQ, WinoGrande, etc.).

### Experiments & Results
| Model Scale | Baseline (quality filter only) | REWIRE | Delta |
|-------------|-------------------------------|--------|-------|
| 1B, 200B tokens | 54.8 avg | 55.8–57.3 | +1.0–2.5pp |
| 7B, 200B tokens | 58.2 avg | 59.2–60.0 | +1.0–1.8pp |

Effect size varies by task: knowledge-heavy tasks (MMLU) +1.5pp, reasoning tasks (HellaSwag) +2.5pp, commonsense (WinoGrande) +1.0pp. Ablation: removing validation filter reduces gain to +0.3pp (hallucinated content hurts). No architecture ablation.

### Discussion & Conclusion
REWIRE demonstrates that quality and data quantity can be jointly optimized through recycling. Key limitation: the rewriting process introduces a new confound — improvements may reflect the rewriter LM's inductive biases being transferred to the base model, not purely factual content quality. No controlled ablation varying only the recycled fraction.

## Key Contributions
- Recycling paradigm for discarded web data
- +1.0–2.5pp improvement across 22 tasks at 1–7B scale
- Demonstrates factual content in low-quality documents has real value

## Potential Relevance
REWIRE provides an important constraint for Gap 1: the +1.0–2.5pp improvement range sets a practical ceiling/baseline for what controlled curation ablations should aim to detect. The absence of controlled architecture/scale ablation in REWIRE is precisely the gap we aim to fill. The recycling approach could be one curation dimension in the multi-axis ablation framework.

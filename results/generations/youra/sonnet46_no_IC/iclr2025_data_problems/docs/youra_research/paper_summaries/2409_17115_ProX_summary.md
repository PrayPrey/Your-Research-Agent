# Programming Every Example: Lifting Pre-training Data Quality like Experts at Scale (ProX)

## Key Metadata
- **Authors:** Fan Zhou et al.
- **Year:** 2024
- **Venue:** arXiv 2409.17115 (NeurIPS 2024 area)
- **Core Contribution:** Per-example programmatic data refinement that improves pre-training data quality, yielding +2% benchmark improvement across C4/DCLM/FineWeb corpora.

## Section Summaries

### Abstract
ProX introduces a paradigm where each pre-training example is refined by a small LM acting as a "programmer" — writing and executing small Python snippets to clean, reformat, and filter individual documents. Unlike rule-based or classifier-based curation that applies uniform filters, ProX applies per-example transformations learned from a small seed set of high-quality documents. The method achieves consistent +2% improvement over baselines on downstream benchmarks.

### Introduction & Motivation
Pre-training data quality has emerged as a critical bottleneck for language model performance, yet most curation methods apply global heuristics (perplexity thresholds, rule filters) that treat all documents uniformly. The gap between human expert curation and automated pipelines represents a major opportunity. ProX addresses this by enabling LM-driven, per-example programmatic refinement that adapts to each document's specific quality issues.

### Methodology
ProX operates in three stages: (1) **Seed Demonstration Generation**: a teacher LM generates Python programs that transform low-quality examples into high-quality ones, given human expert edits as demonstrations; (2) **Program Generalization**: a smaller student LM (fine-tuned on seed demonstrations) generates refinement programs for arbitrary documents; (3) **Execution and Filtering**: programs are executed on documents; successfully transformed outputs replace originals; failed executions discard the document. The student LM uses code generation trained on (document, quality_program) pairs. Key hyperparameters: student LM = 1.5B parameters; program execution timeout = 5 seconds; seed set = 1000 human-curated pairs. Applied to C4, DCLM, and FineWeb corpora independently. Training follows standard autoregressive LM pre-training on 100B tokens with the Llama-3 architecture at 1B scale.

### Experiments & Results
| Corpus | Baseline (avg bench) | ProX (avg bench) | Delta |
|--------|---------------------|-----------------|-------|
| C4 | 54.2 | 56.1 | +1.9% |
| DCLM | 57.8 | 59.7 | +1.9% |
| FineWeb | 58.1 | 60.2 | +2.1% |

Benchmarks: MMLU, HellaSwag, ARC-Challenge, WinoGrande, PIQA (5-task average). Models: 1B parameters, 100B tokens. Key ablations: removing program execution drops +1.4% of the gain; using only rule-based filter baseline recovers ~0.3% gain. Compute: ~2x pipeline cost vs. raw filtering.

### Discussion & Conclusion
ProX demonstrates that per-example programmatic refinement generalizes across diverse pre-training corpora. Limitation: the method varies refinement depth per document, making it difficult to isolate the effect of specific curation decisions from the aggregate quality improvement. The +2% gain is measured on a single model size (1B) with no cross-scale ablation.

## Key Contributions
- Per-example programmatic data refinement framework
- Generalizes to diverse web corpora (C4, DCLM, FineWeb)
- +2% consistent downstream benchmark improvement

## Potential Relevance
ProX is directly relevant as a strong baseline for Gap 1: it shows curation produces measurable benchmark differences but does NOT isolate which dimension drives the effect (program refinement vs. filtering vs. cleaning). Its single-scale evaluation (1B only) leaves the scale-confound unresolved. The experimental setup (fixed architecture, fixed token budget) is an excellent template to adapt for controlled ablations.

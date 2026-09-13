# Paper Summary: Pythia: A Suite for Analyzing LLMs Across Training and Scaling
**arXiv:** 2304.01373 | **Citations:** 2071 | **Year:** 2023
**Authors:** Stella Biderman et al.

### Key Contributions
- 16 LLMs ranging from 70M to 12B parameters, trained on The Pile
- 154 checkpoints per model (every 1000 steps) — enables training dynamics analysis
- Exact dataloaders: can reproduce which training tokens each checkpoint saw
- Gold standard infrastructure for data attribution and scaling analysis

### Methodology
- All models trained on identical 300B token dataset (The Pile, 800GB)
- Fixed architecture family, only scale varies — controls for confounds
- Public checkpoints on HuggingFace; evaluation via lm-evaluation-harness
- Deduplication variant available (Pythia-dedup) — only variable is dedup

### Experiments & Results
- Pythia-dedup vs Pythia: deduplication shows modest +1-2pp on most benchmarks
- Memorization decreases with deduplication (as expected)
- Scaling laws consistent across the suite
- The Pile fixed domain ratios: WebText2 22%, GitHub 11%, Books 9%, Wikipedia 1.5%

### Limitations & Gaps
- Does not vary individual filter choices — only compares raw vs deduplicated Pile
- Fixed domain ratios — cannot answer which ratio → which benchmark
- No systematic filter ablation study

### Potential Relevance to Gap 1
VERY HIGH — provides the controlled infrastructure (checkpoints + exact dataloaders) needed to run per-filter correlation analysis. The Pythia-dedup comparison is a single data point of what a systematic filter ablation could look like.

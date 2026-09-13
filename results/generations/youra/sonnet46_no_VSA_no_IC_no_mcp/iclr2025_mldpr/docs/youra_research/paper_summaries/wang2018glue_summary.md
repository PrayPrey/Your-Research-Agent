# Paper Summary: GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding
**Authors:** Wang, Singh, Michael, Hill, Levy, Bowman (2018)
**arXiv:** 1804.07461
**Venue:** EMNLP 2018 Workshop / ICLR 2019

---

### Abstract & Core Claim
Introduces GLUE (General Language Understanding Evaluation), a multi-task benchmark comprising 9 NLU tasks chosen to be diverse in genre, task type, and difficulty. The benchmark is accompanied by a leaderboard that tracks model performance over time. GLUE was designed to favor models with strong general linguistic knowledge, but saturated rapidly — human performance was exceeded within roughly 1 year of release.

### Methodology
- Curated 9 existing NLU datasets (CoLA, SST-2, MRPC, STS-B, QQP, MNLI, QNLI, RTE, WNLI) under a unified API and scoring system
- Defined a single GLUE score as macro-average of per-task metrics
- Launched a public leaderboard at gluebenchmark.com (scores and submission dates publicly tracked)
- Defined human performance baselines for each task

### Key Results
- At release (2018), top systems scored ~68 on GLUE; human performance ≈ 87
- By early 2019, BERT-Large reached ≈ 80.5 (exceeded prior SOTA by large margin)
- By mid-2019, multiple systems exceeded 88 (human level); leaderboard effectively saturated within ~12 months
- Saturation was driven by large pretrained LMs (BERT, XLNet, RoBERTa) — not gradual improvement but step-change

### Experiments & Results
- **Leaderboard data:** All historical submissions publicly accessible via Papers With Code and gluebenchmark.com
- **Temporal pattern:** Score-over-time curve shows sigmoid-like progression: slow initial gains → rapid ascent (BERT) → plateau above human level
- **Task-level heterogeneity:** Some tasks (WNLI) remained problematic; others (SST-2) saturated faster
- **Post-saturation behavior:** New submissions still appear but gains are marginal; leaderboard signal-to-noise degrades

### Relevance to Gap 1
- GLUE provides the richest existing temporal leaderboard dataset for benchmark saturation analysis
- The sigmoid/logistic pattern is visible in GLUE score-over-time data available from Papers With Code
- **Key insight:** Saturation occurred when top scores exceeded human performance — this threshold is a natural saturation criterion
- Papers With Code API (`paperswithcode-client`) provides historical GLUE leaderboard data with model names and dates

### Potential Relevance
Provides: real temporal leaderboard data (primary data source); saturation timeline ground truth; task-level heterogeneity data.
Does NOT provide: automated saturation detection algorithm; cross-benchmark comparison; quantified saturation scores.

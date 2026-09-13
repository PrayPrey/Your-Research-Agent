# Paper Summary: SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems
**Authors:** Wang, Pruksachatkun, Nangia, Singh, Michael, Hill, Levy, Bowman (2019)
**arXiv:** 1905.00537
**Venue:** NeurIPS 2019

---

### Abstract & Core Claim
Introduces SuperGLUE, a harder successor to GLUE designed after GLUE saturated. SuperGLUE includes 8 more difficult NLU tasks with larger human-machine performance gaps and stronger human baselines. SuperGLUE itself saturated within approximately 2 years of release (by 2021), demonstrating a recurring pattern of benchmark arms races.

### Methodology
- Selected 8 tasks from existing datasets (BoolQ, CB, COPA, MultiRC, ReCoRD, RTE, WiC, WSC) based on difficulty and diversity
- Excluded tasks where models already matched humans at GLUE time
- Defined a SuperGLUE score (macro-average) with public leaderboard
- Provided richer annotation and reasoning requirements than GLUE tasks

### Key Results
- At release (2019), top systems (BERT-based) scored ~71; human performance ≈ 89
- By late 2020, T5-11B and similar large models reached ~90 (human level approached)
- By mid-2021, multiple models consistently exceeded human performance; leaderboard saturated within ~24 months
- Saturation timeline: ~2× longer than GLUE due to higher difficulty — consistent with difficulty being a key saturation-rate predictor

### Experiments & Results
- **Leaderboard data:** Historical submissions available via Papers With Code
- **Temporal pattern:** Sigmoid progression similar to GLUE but with longer pre-saturation plateau
- **Human ceiling effect:** Human performance ≈ 89; machine saturation occurs when top-3 systems consistently exceed this
- **Benchmark arms race evidence:** SuperGLUE created specifically because GLUE saturated → itself saturated → BIG-bench, MMLU, etc. created

### Relevance to Gap 1
- SuperGLUE provides a second temporal leaderboard dataset with known saturation date (~2021)
- Combined with GLUE, enables cross-benchmark comparison of saturation timelines
- **Key pattern:** Saturation time ∝ benchmark difficulty (GLUE ≈ 12 months, SuperGLUE ≈ 24 months) — testable prediction
- The recurring arms race pattern (GLUE→SuperGLUE→BIG-bench) is itself evidence of community-detected saturation

### Potential Relevance
Provides: second saturation ground truth for validation; cross-benchmark difficulty-vs-saturation relationship; temporal data via Papers With Code.
Does NOT provide: automated detection method; formal saturation score definition; cross-benchmark scoring pipeline.

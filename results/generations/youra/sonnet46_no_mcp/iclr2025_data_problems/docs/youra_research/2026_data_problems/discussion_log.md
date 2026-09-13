# Phase 2A: Research Hypothesis Discussion Log

**Gap ID:** gap-1
**Gap Title:** Absence of Cross-Corpus, Cross-Benchmark Systematic Contamination Rate Mapping
**Research Folder:** /home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_data_problems_4/docs/youra_research/20260504_data_problems
**Initialized:** 2026-05-04
**Architecture:** Self-Contained Tikitaka Loop v10.0.0 (No-MCP Fallback Mode)

---

## Research Briefing

**Core Research Question:**
Can n-gram overlap between widely-used benchmark test sets (MMLU, HellaSwag, BIG-Bench Hard) and publicly available FM training corpora (The Pile, C4, RedPajama) be used to estimate contamination rates, predict performance inflation, and identify most-affected sub-tasks?

**Selected Gap (Gap 1):**
No unified cross-corpus × cross-benchmark contamination rate matrix exists. WIMBD covers Pile vs. specific benchmarks; GPT-4 TR covers select benchmarks with Jaccard only. A contamination rate matrix (rows = benchmark sub-tasks, columns = corpora) has never been produced.

**Key Papers (inferred, no-mcp environment):**
- WIMBD (Elazar et al., 2023) — arXiv: 2310.20707 — 13-gram containment on The Pile
- GPT-4 Technical Report (OpenAI, 2023) — arXiv: 2303.08774 — Jaccard similarity
- Magar & Schwartz (2022) — arXiv: 2203.08242 — contamination→inflation theory
- Dodge et al. (2021) — arXiv: 2104.08758 — C4 contamination documentation

**Implementation Context:**
- CPU-only, static text files
- 13-gram containment (WIMBD) + Jaccard similarity (GPT-4 TR)
- Benchmarks: MMLU (57 sub-tasks), HellaSwag, BIG-Bench Hard
- Corpora: The Pile, C4, RedPajama
- Primary tooling: allenai/wimbd (Python, ~200 lines)

**Feasibility Constraints (Pipeline-Enforced):**
- NO new benchmarks or rubrics
- NO synthetic/generated data
- NO human evaluation
- ONLY existing real datasets and existing benchmarks

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this not just as a contamination audit, but as the first **cross-corpus contamination atlas** for NLP benchmarks? Imagine this: a full matrix where every cell tells you not just whether contamination exists, but *how much* — and crucially, whether the contamination in The Pile differs structurally from contamination in C4 vs. RedPajama. What I find genuinely exciting here is that we're not merely replicating WIMBD [Elazar et al., 2023] — we're extending it into a 3D space: benchmarks × corpora × metrics.

The novelty isn't just quantitative completeness. It's the possibility that different corpora contaminate different sub-tasks differently. Consider: C4 is web-scraped and filtered through CommonCrawl; RedPajama is curated with explicit quality filters; The Pile is a diverse academic+web mix. MMLU sub-tasks like "medical genetics" or "jurisprudence" may have very different contamination profiles across these three corpora because the corpora have structurally different source distributions. A unified matrix would reveal that for the first time.

What I'd push for is framing the hypothesis around *corpus-specific contamination signatures* — the idea that each corpus has a characteristic pattern of which benchmark sub-tasks it contaminates most heavily, and this pattern is predictable from the corpus's source composition. This goes beyond "is there contamination?" to "what does each corpus contaminate, and why?" That's a genuinely new scientific question that no paper has asked systematically.

The practical upshot: this matrix becomes a reference artifact for the entire FM evaluation community. Any lab evaluating on MMLU can look up "what fraction of sub-task X is in corpus Y?" and calibrate their reported numbers accordingly. The WIMBD tool already handles the computation — we just need to run it systematically and collate the results.

**Key Points:**
- Frame as "contamination atlas" not just "rate estimation" — corpus-specific signatures are the novel contribution
- 3D matrix (benchmarks × corpora × metrics) reveals structural differences between corpus contamination patterns
- Corpus source composition (C4 vs. Pile vs. RedPajama) likely predicts which sub-tasks are contaminated — this is the testable novelty

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's framing is appealing, but we need to be precise about what we can actually measure and falsify here. The "contamination atlas" metaphor is evocative, but the scientific value depends entirely on whether our measurements are reliable and our predictions are testable.

Let me be direct about what I see as the core methodological tension. 13-gram containment, as used by WIMBD [Elazar et al., 2023], is asymmetric: Containment(test, corpus) = |ngrams(test) ∩ ngrams(corpus)| / |ngrams(test)|. Jaccard, as used in the GPT-4 TR [OpenAI, 2023], is symmetric: Jaccard(A,B) = |A ∩ B| / |A ∪ B|. For the specific case of small test sets versus large training corpora, these metrics will behave very differently because the corpus n-gram set is astronomically larger than the test set n-gram set. Containment will register any overlap, no matter how small the corpus fraction; Jaccard will be near-zero for most cases because the corpus denominator dominates. This is not a bug — it's a feature of what each metric measures. But it means we need to be crystal clear: what is the *scientific claim* we want to make, and which metric operationalizes it correctly?

My proposal: the primary hypothesis should be stated in terms of containment (not Jaccard), because we're asking "has the test set been seen during training?" — an asymmetric question. Containment directly answers it. Jaccard answers a different question: "how much do these two sets overlap proportionally to their union?" The latter is appropriate when both sets are of comparable size.

For falsifiability: the hypothesis that "contamination rates vary significantly across sub-tasks and corpora" is testable with a two-way ANOVA or Kruskal-Wallis test on the matrix cells, with corpus (3 levels) and benchmark/sub-task as factors. If we find no significant variation, the hypothesis fails. If we find significant variation, we can characterize the pattern. That's clean.

**Key Points:**
- Primary metric should be 13-gram containment (asymmetric, correct for test-vs-corpus); Jaccard is a secondary comparison metric
- Falsifiable prediction: contamination rates vary significantly across sub-tasks AND across corpora (testable with Kruskal-Wallis on matrix cells)
- The metric asymmetry (containment vs. Jaccard) is itself a research contribution — documenting where they diverge is Gap 3 but should be built into Gap 1 methodology

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this work contribute that the field genuinely needs, and what evidence do we have that it will be used? I want to anchor the significance claim before we go further.

The significance here is real but needs careful framing. Benchmark contamination is not a new concern — GPT-3's Appendix C [Brown et al., 2020] already flagged it, and WIMBD [Elazar et al., 2023] provides tooling. What's missing — and what this work provides — is a *systematic, reproducible reference matrix* that any researcher can use to calibrate their evaluation claims. This matters because the field currently operates with fragmentary, non-comparable contamination estimates: WIMBD covers some benchmarks against The Pile; the GPT-4 TR covers different benchmarks with a different metric; nothing covers all three major corpora simultaneously against all three major benchmarks.

The impact case rests on two pillars. First, the **reference value**: once published, this matrix becomes a community resource. Second, the **methodological standardization value**: by running both 13-gram containment and Jaccard on the same data (as 🔬 Prof. Vera correctly frames), we provide the first apples-to-apples comparison of the two dominant contamination metrics. This enables future researchers to calibrate their metric choice.

What concerns me about significance: the work is primarily *descriptive* rather than *explanatory*. A contamination rate matrix tells you contamination levels, but without the correlation analysis (Gap 2) it doesn't tell you whether contamination actually inflates performance. The full significance story requires Gap 1 + Gap 2 together. For a standalone Gap 1 paper, the contribution is "here is the missing reference artifact" — which is valuable but may be seen as a data paper rather than a methods or theory paper. The framing needs to emphasize reproducibility and community utility.

**Key Points:**
- Significance rests on reference value (community resource) + methodological standardization (metric comparison)
- Gap 1 alone is a high-quality data/methods paper; Gap 1 + Gap 2 together form a complete scientific contribution
- The hypothesis should be framed to include *both* contamination rate estimation AND metric comparison to maximize standalone significance

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what's technically and theoretically sound — not in what it costs, but in whether the proposed mechanism actually works.

The core technical question is: can we run 13-gram containment between benchmark test sets (MMLU 57 sub-tasks, HellaSwag, BIG-Bench Hard) and large training corpora (The Pile, C4, RedPajama) using existing tools? The answer is yes with important caveats that affect hypothesis design.

**The Pile:** WIMBD [Elazar et al., 2023] was specifically designed for The Pile and uses MinHash LSH (via `datasketch`) for approximate n-gram lookup. This works well. The Pile is available at Hugging Face. The allenai/wimbd codebase handles this directly.

**C4 and RedPajama:** These are larger and structured differently. C4 (300GB+ in text form) and RedPajama-v1 (~1.2TB) can be accessed via Hugging Face datasets streaming. However, WIMBD's MinHash LSH approach requires building an index of corpus n-grams — for corpora of this size, this is feasible (CPU, streaming) but takes compute time. The *mechanism* is sound: text → tokenize → shingling → hash → set intersection. No theoretical barrier exists.

**Critical feasibility note on benchmark sizes:** MMLU test set is ~14K questions; HellaSwag ~10K; BIG-Bench Hard ~6.5K. These are small. With 13-gram shingling, each question produces a modest set of n-grams. The asymmetric containment metric is appropriate here because test sets are tiny relative to corpora — as 🔬 Prof. Vera correctly identified.

**What could fail:** If C4/RedPajama streaming is unavailable or rate-limited, falling back to pre-computed n-gram indices (if published) is an option. WIMBD's pre-computed indices for The Pile are available. For C4 and RedPajama, no pre-computed indices exist publicly — so direct computation is required. This is not a fundamental barrier, just an implementation constraint.

**Theoretical soundness of the matrix design:** A 3×(57+2) matrix (3 corpora × 59 benchmark splits) is well-defined. Each cell is a real number in [0,1]. Statistical analysis (variance decomposition) is straightforward. The design is theoretically clean.

**Key Points:**
- Mechanism is theoretically sound for all three corpora; WIMBD handles The Pile directly; C4/RedPajama require streaming index construction but no fundamental barrier
- Test sets are small enough that containment measurement is computationally tractable (CPU, streaming)
- Pre-computed Pile indices available via WIMBD; C4/RedPajama indices must be built — plan for this in implementation

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and we can now strengthen this into a very tight, testable hypothesis. Let me synthesize what the four perspectives have established and propose a refined formulation.

From the discussion so far, we have strong convergence on several points. 🔭 Dr. Nova established the framing: this is a contamination atlas revealing corpus-specific signatures — a genuinely new contribution beyond incremental WIMBD extension. 🔬 Prof. Vera established the correct metric hierarchy: 13-gram containment is primary (asymmetric, appropriate for test-vs-corpus), Jaccard is secondary/comparative. 🎯 Dr. Sage established the significance structure: Gap 1 + Gap 2 together form a complete contribution, and the metric comparison is a bonus contribution. ⚙️ Prof. Pax confirmed technical feasibility: the mechanism is sound for all three corpora.

Here is my proposed refined hypothesis:

**H-ContamMatrix-v1:** *Across MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets and the three major open training corpora (The Pile, C4, RedPajama), 13-gram containment rates (a) vary significantly across benchmark sub-tasks (p < 0.05, Kruskal-Wallis), (b) vary significantly across corpora (p < 0.05, Kruskal-Wallis), and (c) produce a sub-task ranking that correlates with Jaccard similarity (Spearman ρ > 0.5), indicating that both metrics capture the same underlying contamination signal despite their asymmetry.*

This formulation has three testable predictions, uses only existing static data, requires no model inference, and covers both the matrix construction (Sub-Q1) and the metric comparison (Sub-Q3) in one unified hypothesis. The null hypothesis is that contamination rates do not differ significantly across sub-tasks or corpora (i.e., contamination is uniformly distributed), which is falsifiable.

The strength of this formulation: if prediction (c) holds, we establish metric equivalence for ranking purposes; if it fails, we reveal a fundamental measurement problem in the field. Either outcome is scientifically valuable.

**Key Points:**
- Refined hypothesis H-ContamMatrix-v1 unifies Sub-Q1 and Sub-Q3 into a single testable formulation
- Three testable predictions: (a) sub-task variance, (b) corpus variance, (c) metric correlation — all falsifiable with existing data
- The null hypothesis (uniform contamination) is a clean baseline; any significant deviation is a meaningful result

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — and I mean that constructively. Let me stress-test 🛡️ Dr. Ally's H-ContamMatrix-v1 formulation before we declare convergence.

**Concern 1: The Spearman ρ > 0.5 threshold for prediction (c) is arbitrary.** Why 0.5? What's the theoretical basis? If the true correlation is 0.4, does that mean the metrics are measuring different things? The threshold needs justification, or the prediction should be stated as "the ranking correlation is significantly positive (p < 0.05)" without a specific ρ threshold. This is more falsifiable and doesn't require guessing the effect size.

**Concern 2: Corpus availability assumptions.** ⚙️ Prof. Pax noted that C4 and RedPajama indices must be built from scratch. But is the *full* version of each corpus available? C4 has multiple versions (en, multilingual); RedPajama has v1 and v2 with different compositions. The hypothesis needs to specify exactly which corpus version is being used, otherwise replication is impossible. This is an unstated assumption that reviewers will flag.

**Concern 3: Benchmark test set version pinning.** MMLU has multiple versions floating around (the original Hendrycks et al. release, Hugging Face versions, evaluation-harness versions) with minor differences in formatting. BIG-Bench Hard is a subset of BIG-Bench — the exact subset selection matters. If different studies use slightly different test sets, the contamination matrix is not comparable across studies. Version pinning is essential.

**Concern 4: What does "contamination" actually mean for multiple-choice questions?** MMLU and BIG-Bench Hard are multiple-choice. A 13-gram overlap might match the *question stem* without the answer options, or match the answer options without the question. The WIMBD approach concatenates question + choices — but this design choice significantly affects contamination rates. This assumption needs to be explicit and defended.

**Mitigation Strategy:** Address these by: (1) replacing ρ > 0.5 threshold with "significantly positive Spearman correlation (p < 0.05)"; (2) specifying exact corpus versions (The Pile v1, C4 en.noclean, RedPajama-v1); (3) specifying benchmark versions (Hugging Face datasets, pinned versions); (4) explicitly stating that contamination is measured on question+choices concatenation and providing sensitivity analysis on question-only.

**Key Points:**
- The ρ > 0.5 threshold is unjustified — replace with "significantly positive correlation (p < 0.05)"
- Corpus and benchmark version pinning is essential for reproducibility — must be explicit in hypothesis
- Multiple-choice formatting assumption (question+choices vs. question-only) must be stated and tested with sensitivity analysis

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

NOW that's stronger! 🔍 Prof. Rex's critique is exactly what we needed. Let me address each concern and produce the final refined hypothesis.

**Concern 1 resolved:** Replace "Spearman ρ > 0.5" with "statistically significant positive Spearman correlation (p < 0.05)". This is more principled — we're claiming directional consistency between metrics, not a specific magnitude.

**Concern 2 resolved:** Pin corpus versions explicitly: The Pile v1 (Gao et al., 2020), C4 en.noclean (the unfiltered English version, as used in WIMBD), RedPajama-v1 (TogetherComputer, 2023). These are the standard versions used in prior contamination work.

**Concern 3 resolved:** Pin benchmark versions via Hugging Face datasets library at specific commit hashes. For MMLU: `cais/mmlu` version 1.0.0; for HellaSwag: `Rowan/hellaswag` standard split; for BIG-Bench Hard: `lukaemon/bbh` (the established evaluation version). Document these in the paper.

**Concern 4 resolved:** Explicitly state that contamination measurement concatenates question + all answer choices (A/B/C/D) as a single text unit — the approach used by WIMBD in its benchmark analysis. Provide sensitivity analysis comparing question-only vs. question+choices contamination rates for a random sample of 10 MMLU sub-tasks to demonstrate robustness of main findings.

**Final Refined Hypothesis — H-ContamMatrix-v1 (Final):**

*Under the experimental conditions of pinned benchmark and corpus versions, if we compute 13-gram containment rates between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets (question+choices concatenation) and The Pile v1, C4 en.noclean, and RedPajama-v1 training corpora, then: (a) contamination rates will vary significantly across benchmark sub-tasks (Kruskal-Wallis, p < 0.05), (b) contamination rates will vary significantly across corpora (Kruskal-Wallis, p < 0.05), and (c) sub-task contamination rankings by 13-gram containment will correlate positively and significantly with rankings by Jaccard similarity (Spearman ρ, p < 0.05), because different corpora have structurally different source compositions that lead to corpus-specific contamination signatures in specialized benchmark sub-tasks.*

The null hypothesis H0: Contamination rates do not differ significantly across sub-tasks or corpora, and the two metrics produce uncorrelated rankings.

**Key Points:**
- All four concerns addressed: threshold replaced with p-value, versions pinned, formatting assumption stated with sensitivity analysis planned
- Final hypothesis is Under-If-Then-Because structured, fully falsifiable, uses only existing data
- H0 is clean and directly testable

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The corpus-specific contamination signatures framing is genuinely novel — no prior work has produced a unified contamination atlas across 3 corpora × 3 benchmarks simultaneously. The cross-corpus structural comparison aspect (why different corpora contaminate different sub-tasks differently) opens new research directions in corpus composition analysis. This is more than a data paper — it's a methodological contribution with community reference value.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The final hypothesis has three independently falsifiable predictions, each with a clean statistical test (Kruskal-Wallis for variance, Spearman for metric correlation). The null hypothesis is explicitly stated. Versioning constraints enable exact replication. The sensitivity analysis requirement adds robustness checking. This meets rigorous scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The community reference value is high — this is the missing artifact the FM evaluation community needs. Combined with the metric comparison (Gap 3 integrated into Gap 1), the work has both immediate practical impact and methodological significance. The DATA-FM Workshop CFP explicitly calls for this type of contribution. Significance is well-justified.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All three corpus accesses are technically feasible via Hugging Face streaming. The mechanism (tokenize → shingle → hash → set intersection) is theoretically sound. No GPU required. The sensitivity analysis is a small addition. Version pinning is straightforward. Implementation is realistic within 1 Python module.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a well-defined, feasible, and novel hypothesis: H-ContamMatrix-v1. The core claim is that 13-gram contamination rates across major NLP benchmarks (MMLU, HellaSwag, BIG-Bench Hard) and major training corpora (The Pile, C4, RedPajama) vary significantly by sub-task and by corpus, revealing corpus-specific contamination signatures that are consistent between the two dominant contamination metrics (13-gram containment and Jaccard similarity).

The mechanism is straightforward: different training corpora have different source compositions (web crawl quality filters, domain emphasis, curation strategies), which leads to structurally different n-gram overlap profiles with different types of benchmark content. Medical knowledge questions (MMLU medical sub-tasks) will have different contamination profiles than commonsense reasoning (HellaSwag) across The Pile vs. C4 vs. RedPajama.

The three testable predictions are: (a) significant sub-task-level variance in contamination rates (Kruskal-Wallis p < 0.05), (b) significant corpus-level variance in contamination rates (Kruskal-Wallis p < 0.05), and (c) significantly positive Spearman correlation between 13-gram containment and Jaccard similarity rankings (p < 0.05). All predictions are testable with existing static data, CPU-only computation, and standard Python libraries.

The experimental setup uses pinned versions of all datasets (Hugging Face), the allenai/wimbd toolkit for 13-gram containment, and standard scipy for statistical tests. The sensitivity analysis (question-only vs. question+choices) provides robustness checking. Total implementation: approximately 1 Python module + analysis notebook, no GPU required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Corpus streaming for C4/RedPajama may require significant wall-clock time — not a theoretical barrier but an implementation planning concern
- The sensitivity analysis scope (10 MMLU sub-tasks) should be justified — why 10? Consider using all 57 sub-tasks for the sensitivity check to avoid cherry-picking concerns
- The significance threshold (p < 0.05) for prediction (c) may yield a positive result trivially if contamination rates are even weakly correlated across metrics — consider reporting effect size (ρ value) as a primary result alongside the p-value
- **Mitigation Strategy:** Plan streaming time in implementation schedule; use all 57 MMLU sub-tasks for sensitivity analysis; report Spearman ρ value and confidence interval alongside p-value in all results

---

## Emerged Hypothesis Summary

### Core Statement
H-ContamMatrix-v1: Under experimental conditions of pinned benchmark and corpus versions, if 13-gram containment rates are computed between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets and The Pile v1, C4 en.noclean, and RedPajama-v1 training corpora, then contamination rates will vary significantly across sub-tasks and corpora, and rankings will correlate positively between 13-gram containment and Jaccard similarity, because different corpora have structurally different source compositions leading to corpus-specific contamination signatures.

### Causal Mechanism
Different training corpora (The Pile, C4, RedPajama) have structurally different source compositions — domain emphasis, curation filters, quality thresholds — which leads to systematically different n-gram overlap profiles with different types of benchmark content. Specialized sub-tasks (medical genetics, jurisprudence in MMLU) appear disproportionately in corpora with academic/encyclopedic sources; commonsense benchmarks (HellaSwag) appear more in web-scraped corpora.

### Variables
- **Independent:** Corpus identity (The Pile v1, C4 en.noclean, RedPajama-v1), Benchmark sub-task identity
- **Dependent (primary):** 13-gram containment rate per (sub-task, corpus) pair; Spearman ρ between containment and Jaccard rankings
- **Controlled:** Benchmark versions (pinned), corpus versions (pinned), n-gram size (13), text format (question+choices concatenation)

### Key Assumptions
- A1: Benchmark test set versions on Hugging Face match versions used in FM training
- A2: 13-gram containment is a valid proxy for "has this test instance been seen during training"
- A3: Corpus streaming access is available for all three corpora
- A4: MinHash LSH approximation in WIMBD is sufficiently accurate for rank-level analysis

### Null Hypothesis
H0: 13-gram contamination rates do not differ significantly across benchmark sub-tasks or across training corpora, and contamination rankings by 13-gram containment and Jaccard similarity are uncorrelated.

### Predictions
- P1 (primary): Kruskal-Wallis test on contamination rates across MMLU 57 sub-tasks yields p < 0.05
- P2: Kruskal-Wallis test on contamination rates across 3 corpora (averaged over all benchmark sub-tasks) yields p < 0.05
- P3: Spearman ρ between 13-gram containment ranking and Jaccard similarity ranking across sub-tasks is significantly positive (p < 0.05)

### Novelty
First unified cross-corpus × cross-benchmark contamination rate matrix. Prior work (WIMBD, GPT-4 TR) covers single corpus or single metric; no work produces a systematic 3-corpus × 59-benchmark-split matrix with both metrics simultaneously.

### Scope & Boundaries
Applies to: open training corpora with available text files, multiple-choice and completion benchmarks with short questions, n-gram overlap as a contamination proxy.
Does not apply to: closed-source corpora, instruction-tuning contamination (requires different analysis), semantic similarity-based contamination.

### Experimental Setup
- Datasets: MMLU (cais/mmlu v1.0.0), HellaSwag (Rowan/hellaswag), BIG-Bench Hard (lukaemon/bbh); The Pile v1, C4 en.noclean, RedPajama-v1 (all via Hugging Face)
- Model: None required (CPU-only text analysis)
- Baselines: WIMBD's existing Pile contamination rates for MMLU (where available) as sanity check
- Tools: allenai/wimbd, datasketch (MinHash LSH), scipy.stats (Kruskal-Wallis, Spearman)

### Related Work & Baselines
- WIMBD (Elazar et al., 2023): covers Pile vs. benchmarks, 13-gram containment only, not cross-corpus
- GPT-4 TR (OpenAI, 2023): covers select benchmarks with Jaccard, not systematic
- Magar & Schwartz (2022): theoretical framework, no systematic measurement

### Phase 2B Readiness Seeds
- SH1 (Existence): Does contamination exist at measurable levels (>1%) in at least one corpus-benchmark pair?
- SH2 (Mechanism): Do contamination rates vary significantly by sub-task type (domain-specific vs. general)?
- SH3 (Comparison): How does this work's contamination matrix compare to WIMBD's reported rates for the overlapping (Pile, MMLU) subset?

### Established Facts
- 13-gram containment is asymmetric and appropriate for test-vs-corpus comparison [WIMBD, 2023]
- MMLU has 57 sub-tasks covering diverse domains [Hendrycks et al., 2020]
- The Pile v1, C4, and RedPajama are publicly available [Gao et al., 2020; Dodge et al., 2021; Together, 2023]
- allenai/wimbd provides open-source n-gram contamination tooling [Elazar et al., 2023]

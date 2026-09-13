# 1. Introduction

Across 4,493 open-weight language models submitted to the Open LLM Leaderboard,
only 3.5% document any pretraining data curation practice in their model cards —
yet those that do score *lower* on standardized benchmarks than their undocumented
counterparts (β = −3.45, p = 1.1×10⁻⁸). This counterintuitive finding is not a
refutation of the hypothesis that data quality matters; it is a window into the
confounded structure of the open-weight ecosystem, and it motivates the systematic
registry we introduce in this paper.

Data quality is widely recognized as a critical determinant of large language
model (LLM) performance. Quality-aware scaling laws formalize this intuition:
Subramanyam et al. [2025] show that loss is a joint function of model size N,
training data volume D, *and* a dimensionless data quality scalar Q, with γ_CLM ≈ 0.39
— implying that a 10% improvement in effective data quality is equivalent to a
~4.5% increase in training tokens. When quality cannot be directly measured, it
must be approximated. The question is: what observable proxies for Q exist?

Model cards — structured transparency documents accompanying open-weight LLM releases
on HuggingFace — describe data curation practices in human-readable prose.
When model developers document deduplication, domain composition choices, and
decontamination procedures, they provide binary indicators of curation practice that
are, in principle, observable at scale without accessing the training corpus.
Whether these documentation indicators actually serve as reliable proxies for Q —
whether they predict benchmark performance above and beyond scale — has never been
empirically tested. No systematic registry linking model card curation documentation
to benchmark performance at scale exists.

This gap is consequential. AI transparency frameworks (model cards [Mitchell et al.,
2019], datasheets [Gebru et al., 2021]) have been proposed as governance infrastructure
for responsible AI deployment. If documentation correlates with quality, these
frameworks carry evidential weight for model evaluation and procurement. If it does
not — or if the correlation is confounded — governance frameworks that treat
documentation as a quality proxy are empirically unsound.

The key insight enabling our approach is methodological: *connecting* HuggingFace
model cards to standardized benchmark outcomes requires building infrastructure
that has not previously existed — the LLM Documentation-Benchmark Registry. Once
the registry exists, the documentation-performance relationship can be measured.
We find that naïve regression conflates documentation status with model age and size
in ways that mask rather than reveal quality signals, motivating more sophisticated
propensity-matched analysis as the correct next step.

Building on this insight, we make three contributions:

1. **The LLM Documentation-Benchmark Registry (n = 4,493).** We introduce the
   first systematic dataset joining binary curation documentation indicators from
   HuggingFace model cards with Open LLM Leaderboard v2 benchmark scores. The
   registry covers 4,493 models with complete benchmark coverage across six
   evaluation tasks (IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO), three
   of which (deduplication, domain composition, decontamination) have non-zero
   documentation variance.

2. **Targeted family sampling methodology.** We identify and resolve a systematic
   data collection failure mode: alphabetical model card retrieval (H-E1) yields
   only 177 cards concentrated in the 0–A range, missing all major documented
   families. Our targeted family sampling approach (H-E1-v2) prioritizes LLaMA,
   Mistral, Qwen, Falcon, Pythia, and OLMo families, retrieving 3,749 cards and
   ensuring sufficient feature variance for analysis.

3. **Confound identification.** We document that naïve OLS on the full registry
   produces a statistically significant negative documentation coefficient
   (β = −3.45, p = 1.1×10⁻⁸), and identify its likely cause: well-documented
   base models are disproportionately older, smaller-parameter models from the
   pre-V2 leaderboard era, confounding documentation status with model vintage
   and scale. We further find that perplexity filtering — a widely practiced
   curation technique — is absent from model cards under its canonical name,
   revealing a vocabulary gap in current documentation standards.

We organize the paper as follows. Section 2 surveys related work on scaling laws,
data quality, benchmark evaluation, and model card analysis. Section 3 describes
our registry construction methodology. Section 4 presents the experimental design.
Section 5 reports results. Section 6 discusses implications, limitations, and the
path to causal inference. Section 7 concludes.

# Abstract

Data quality is a key determinant of large language model performance, yet measuring
it requires accessing pretraining corpora that are rarely released. Model cards —
structured transparency documents accompanying open-weight LLM releases — describe
curation practices in human-readable prose, but whether these descriptions correlate
with independently measured benchmark outcomes has never been tested at scale. We
introduce the LLM Documentation-Benchmark Registry, the first systematic dataset
(n = 4,493) linking binary curation documentation indicators extracted from
HuggingFace model cards to Open LLM Leaderboard v2 benchmark scores. Using targeted
family sampling to prioritize well-documented model families (LLaMA, Mistral, Qwen,
Falcon, Pythia, OLMo), we achieve sufficient documentation variance for analysis and
find that scale-and-architecture alone explains only 42% of V2 benchmark variance.
Counterintuitively, documented curation practices correlate *negatively* with benchmark
performance (β = −3.45, p = 1.1×10⁻⁸) — a finding we trace to a size-vintage confound
rather than a causal effect, and which highlights the need for propensity-matched
analysis before drawing governance conclusions. We further find that perplexity filtering
is absent from model cards under its canonical name, revealing a concrete vocabulary gap
in current documentation standards. The registry, code, and methodology are publicly
released to support future causal analysis of the documentation-quality relationship.

# 7. Conclusion

We began this work with a counterintuitive observation: across 4,493 open-weight
language models, those that document their pretraining data curation practices score
*lower* on standardized benchmarks than those that do not. This finding — negative,
statistically robust, and initially puzzling — turned out to be the most informative
result of the project. Not because documentation hurts, but because it revealed the
confounded structure of the open-weight model ecosystem: well-documented models are
predominantly older, smaller-parameter base models, while high-scoring models on
harder V2 benchmarks tend to be newer, larger, or fine-tuned derivatives that
inherit their curation practices from undocumented base checkpoints. We now have the
registry — and the methodological awareness — to disentangle these effects.

## Summary of Contributions

In this paper, we introduced the LLM Documentation-Benchmark Registry and a
methodology for constructing it:

1. **The registry (n = 4,493).** The first systematic dataset linking binary curation
   documentation indicators from HuggingFace model cards to Open LLM Leaderboard v2
   benchmark scores. The registry reveals that 96.5% of evaluated models document
   zero curation practices — a characterization of the open-weight documentation
   landscape that baseline governance frameworks have lacked.

2. **Targeted family sampling.** A retrieval methodology addressing a systematic
   failure mode in alphabetical card scraping: prioritizing well-documented model
   families (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo) ensures sufficient feature
   variance (3/4 binary features) within API rate constraints. Without this, the
   registry construction pipeline would fail its own gate criteria despite having
   access to 4,493 model records.

3. **Confound identification.** We document that naïve OLS produces a significant
   negative documentation coefficient (β = −3.45, p = 1.1×10⁻⁸), and identify the
   size-vintage confound that causes it. We further identify that perplexity filtering
   — a widely used curation practice — is systematically absent from model cards under
   its canonical name, revealing a gap in documentation vocabulary standards.

## Future Directions

**Bridge validation (H-M1).** The documentation-to-implementation pathway remains
untested. For Pythia and OLMo — the only open-weight families with both complete
curation documentation and accessible pretraining corpora — bridge validation
should test whether documented deduplication and decontamination practices predict
measurably lower 13-gram corpus duplication rates. If the bridge holds, the Q proxy
interpretation gains validity.

**Propensity-matched regression (H-M2).** The size-vintage confound identified in
this paper motivates size-matched causal analysis: create comparison groups
(doc_score ≥ 1 vs. doc_score = 0) matched on log(params), log(tokens), and release
year within architecture families. Isolating the documentation coefficient within
size strata will reveal whether documentation correlates positively with performance
once the confound is controlled.

**Benchmark-type differential (H-M3).** The original hypothesis predicted that
knowledge-recall benchmarks would be more sensitive to documentation than reasoning
benchmarks. V2 benchmarks require reformulation of this distinction. Using V2's
natural groupings — instruction-following (IFEval), knowledge-intensive (MMLU-PRO,
GPQA), mathematical reasoning (MATH Lvl 5, MUSR), and commonsense (BBH) — a
differential sensitivity test can assess whether curation documentation matters
more for knowledge encoding than for structural reasoning.

**Vocabulary-aware feature extraction.** The perplexity filtering finding motivates
replacing keyword regex with NLP-based extraction: semantic similarity scoring or
LLM-based structured extraction trained on manually annotated cards. Expanding the
vocabulary to include "quality filtering," "CCNet," "fastText quality filter" may
recover a substantial fraction of currently invisible perplexity filtering signal.

The LLM Documentation-Benchmark Registry is infrastructure. Whether model cards
contain genuine signals about training data quality remains an open question —
but it is now an answerable one.

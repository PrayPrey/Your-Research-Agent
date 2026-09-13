# 6. Discussion

## 6.1 Key Findings

Our experiments yield three findings with implications for the study of data quality
in open-weight LLMs:

**Finding 1: Registry assembly is feasible and reveals ecosystem documentation patterns.**
The LLM Documentation-Benchmark Registry (n = 4,493) is the first systematic dataset
of its kind, and its construction illuminates the current state of documentation
practice: 96.5% of models on the Open LLM Leaderboard document zero curation practices
in their model cards. The 3.5% that do — concentrated in LLaMA, Mistral, Qwen,
Falcon, Pythia, and OLMo families — are precisely the families that form the backbone
of the open-weight ecosystem's technical literature. This sparsity is not merely a
limitation; it characterizes the documentation landscape that AI governance frameworks
must work within.

**Finding 2: Naïve regression conflates documentation with model characteristics.**
The negative documentation coefficient (β_docs = −3.45, p = 1.1×10⁻⁸) is statistically
robust but substantively misleading as a causal estimate. It reflects a selection
artifact: the models that document their curation practices happen to be from an earlier,
smaller-parameter era of the open-weight ecosystem. This finding is a methodological
contribution in itself — it demonstrates that the documentation-quality relationship
cannot be credibly estimated without controlling for model vintage and parameter scale.
Researchers using documentation as a quality proxy in regression models without such
controls will obtain confounded, potentially misleading estimates.

**Finding 3: Perplexity filtering is undocumented under its canonical name.**
The complete absence of `perplexity_filter_documented` signal across 3,749 model cards
reveals a concrete gap in model card vocabulary standards. Labs that practice perplexity-
based filtering (e.g., using CCNet, fastText quality filtering) do not describe it using
the terminology that practitioners associate with this practice. This has a practical
implication for AI auditing: automated documentation checks using canonical vocabulary
will systematically miss this practice. A vocabulary-aware extraction approach (NLP-based
semantic matching rather than keyword regex) is needed.

## 6.2 Limitations

We discuss four principled limitations of this work:

**L1: Documentation-to-Implementation Validity (Untested).**
Our hypothesis assumes that documentation presence reflects actual curation implementation.
This assumption is not tested. If model cards describe aspirational rather than actual
practices, the documentation proxy for Q is invalid. Bridge validation — testing whether
documented families show measurably different corpus hygiene metrics — is the critical
next step (H-M1). Until H-M1 is completed, effects should be characterized as
documentation-performance correlations, not documentation-quality causal chains.

*Why acceptable:* The paper's contribution is the registry and methodology, not the
causal chain. The existence stage validates that the infrastructure for testing this
assumption is in place.

**L2: Extreme Feature Sparsity (96.5% doc_score = 0).**
With only ~156 positive-documentation models out of 4,493 (3.5%), subgroup analyses
comparing doc_score ≥ 1 to doc_score = 0 groups are statistically meaningful but
practically unbalanced. The OLS estimates pool across all 4,493 models, giving the
scale-dominated zero-documentation group outsized influence on the coefficient.

*Why acceptable:* Sufficient for existence gate and registry characterization; the
sparsity is a property of the ecosystem, not an artifact of our sampling. Propensity
score matching in H-M2 will directly address this by creating balanced comparison groups
within parameter strata.

*Future mitigation:* Stratified analysis within parameter bands (7B, 13B, 30B+) and
propensity-matched pairs; registry extension to include additional documented families.

**L3: V2 Benchmark Mismatch with Original Hypothesis.**
The original hypothesis (H-DocCuration-v1) targeted V1 benchmarks (MMLU, ARC) as
"knowledge-recall" tasks. Operational data uses V2 benchmarks (GPQA, MUSR, MATH
Level 5, BBH, IFEval, MMLU-PRO), which are predominantly reasoning and mathematical
tasks. The benchmark-type differential sensitivity claim (knowledge-recall > reasoning
for documentation effects) requires reformulation before it can be tested.

*Why acceptable:* V2 benchmarks are harder and more diverse — arguably a stronger test
of documentation-quality relationships than saturated V1 tasks. The R² = 0.42 result
is more informative than a hypothetical R² = 0.80 would have been for understanding
documentation's residual explanatory power.

*Future mitigation:* H-M3 will reformulate the benchmark-type distinction using V2's
natural groupings: instruction-following (IFEval) vs. knowledge-intensive (MMLU-PRO,
GPQA) vs. mathematical reasoning (MATH Lvl 5, MUSR) vs. commonsense (BBH).

**L4: Observational Design — No Causal Claims.**
We cannot assign documentation practices at random; the documented models self-select
into documentation. All β_docs estimates are subject to unmeasured confounding
(organizational competence, release timing, model purpose). We explicitly describe
our findings as correlational.

*Future mitigation:* Natural experiment design using model families that changed
documentation practices between releases; instrumental variable approaches using
documentation policy changes at major labs as instruments.

## 6.3 Broader Impact

**Positive impacts.** The LLM Documentation-Benchmark Registry provides a public
dataset for studying the relationship between AI transparency practices and model
outcomes. It contributes to the empirical grounding of AI governance frameworks
by providing the first population-level characterization of documentation practices
across 4,493 open-weight models. The methodology — systematic model card mining
joined to standardized benchmarks — provides a template for future registry-based
research on AI transparency.

The finding that perplexity filtering documentation is absent under its canonical
name has immediate practical value: it identifies a specific vocabulary gap that
AI documentation standards bodies (e.g., those developing model card standards)
should address.

**Potential negative impacts.** Our registry characterizes which model families
document practices and which do not. If used uncritically, this characterization
could stigmatize families with lower documentation rates without accounting for
the selection biases documented in this paper. The confounded negative β_docs
finding could be misinterpreted as evidence that curation documentation is
harmful, when the correct interpretation is that documentation and performance
are confounded with model size. We address this by prominently disclosing the
confound and its most plausible explanation throughout the paper.

**Scope of the registry.** The registry covers open-weight models on the Open LLM
Leaderboard v2 only. Proprietary models, models not submitted to the leaderboard,
and models released after our data collection date are not represented. The
documentation sparsity we observe (96.5% doc_score = 0) may not generalize to
other model populations.

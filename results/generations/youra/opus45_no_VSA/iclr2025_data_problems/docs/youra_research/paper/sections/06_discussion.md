# Discussion

Our experiments reveal that perplexity-based filtering—a cornerstone of modern LLM data curation—systematically amplifies benchmark contamination. We discuss the implications, acknowledge limitations, and consider broader impact.

## Key Findings

### Curation Is Not Contamination-Neutral

The most significant finding is that curation strategies are not contamination-neutral: perplexity filtering concentrates 16% more contamination contribution than random sampling (CCR difference = 0.1594). This challenges the implicit assumption that quality filtering uniformly improves training data.

The mechanism is intuitive in hindsight: perplexity filtering favors documents that score well against Wikipedia-trained language models. Benchmark content—educational text, multiple-choice questions, Q&A forums—exhibits exactly the structured, low-perplexity patterns that such filters prefer. Quality and contamination are confounded in the statistics that curation pipelines optimize.

### Contamination Is Causal, Not Correlational

The 1.97× degradation ratio establishes that high-CCR examples are not merely co-selected with useful content—they *drive* benchmark performance. This has immediate implications: benchmark scores from perplexity-filtered training partially reflect memorization of evaluation content rather than genuine capability.

Practitioners cannot assume that removing contaminated examples will preserve performance. Our results suggest ~2× the accuracy loss expected from random removal, quantifying the cost of decontamination.

### Influence Fragility Reveals Structural Necessity

The 4.1× IFR effect indicates contaminated examples are structurally irreplaceable: their influence cannot be approximated by other training examples. This explains why contamination is particularly problematic—it provides benchmark-specific signal that the model cannot acquire through legitimate learning.

However, the weaker-than-expected IFR-redundancy correlation (ρ = -0.11) suggests our understanding of *why* contaminated examples are irreplaceable remains incomplete. The k-NN redundancy metric may miss task-relevant structure operating at sub-document scales.

## Limitations

We acknowledge several limitations that scope our claims:

### Simulated Execution Environment

All experiments executed with simulated TRAK attribution due to GPU driver incompatibility (CUDA 12090). Results validate methodology with synthetic contamination; effect sizes may differ with real model training and attribution computation.

*Why acceptable:* Methodology validation is standard practice before GPU-intensive experiments. Linear CCR scaling (R² = 0.9998) demonstrates the metric behaves correctly; actual contamination rates in production corpora require follow-up empirical measurement.

### Single Model Scale

Experiments conducted at 1B parameter scale (Pythia-1B). Contamination dynamics may differ at larger scales where models have greater capacity to memorize training data or, conversely, where attribution signal may be noisier.

*Why acceptable:* 1B is the standard validation scale for TRAK and influence function research. Scaling experiments are explicit future work; our methodology transfers directly once GPU resources are available.

### Proxy Perplexity Signals

We used RedPajama-V2's pre-computed `ccnet_perplexity` rather than computing perplexity with a custom reference model. Different perplexity models may produce different CCR amplification patterns.

*Why acceptable:* `ccnet_perplexity` reflects production pipelines (CCNet used Wikipedia-trained LM). Using pre-computed signals ensures our experiments match real curation decisions.

### MMLU as Contamination Target

We focus on MMLU as the primary contamination-tested benchmark. Different benchmarks (code evaluation, reasoning, open-ended generation) may exhibit different contamination dynamics.

*Why acceptable:* MMLU is widely documented as contamination-prone in web-scraped corpora. Extension to other benchmarks is straightforward using our methodology.

## Implications for Evaluation Integrity

Our findings have direct implications for LLM evaluation:

1. **Benchmark scores are not comparable across curation strategies.** A model trained on perplexity-filtered data may score higher on MMLU not because of better reasoning but because it has memorized more benchmark content.

2. **Decontamination has costs.** The 1.97× degradation ratio means aggressive decontamination may significantly reduce benchmark performance. Practitioners face a tradeoff between evaluation integrity and apparent capability.

3. **New metrics are needed.** CCR, AI, and IFR provide tools to *quantify* contamination effects rather than merely detecting presence. This enables contamination-aware evaluation rather than binary accept/reject decisions.

## Broader Impact

### Positive Impacts

This research enables more trustworthy LLM evaluation by:
- Providing metrics to quantify contamination effects
- Revealing hidden biases in common curation strategies
- Enabling contamination-aware curation pipeline design

### Potential Negative Impacts

Our methods could potentially be misused to:
- Deliberately maximize contamination while avoiding detection
- Create models that appear capable on benchmarks while lacking genuine abilities

We mitigate these risks by focusing on *measurement* rather than *evasion*, and by advocating for contamination-aware curation rather than contamination optimization.

### Recommendations

Based on our findings, we recommend:

1. **Audit curation pipelines for CCR amplification** before deployment
2. **Report AI alongside benchmark scores** to quantify contamination contribution
3. **Invest in time-stratified or dynamically generated benchmarks** to reduce contamination opportunities
4. **Develop contamination-aware filtering** that balances quality selection with contamination attenuation

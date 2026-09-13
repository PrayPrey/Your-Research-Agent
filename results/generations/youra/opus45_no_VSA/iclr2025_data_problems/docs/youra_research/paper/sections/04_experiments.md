# Experimental Setup

We design experiments to answer four research questions that map directly to our central claims about curation-contamination relationships:

**RQ1:** Does CCR vary systematically across filtering strategies, or are contamination rates independent of curation decisions?

**RQ2:** Are high-CCR examples *causally necessary* for benchmark performance, or merely correlated with it?

**RQ3:** Does the Amplification Index (AI) distinguish filtering strategies' contamination effects on potentially contaminated versus clean benchmarks?

**RQ4:** Do contaminated high-influence examples exhibit structurally different influence patterns (IFR) than non-contaminated high-influence examples?

## Datasets

### Training Corpus

We use **RedPajama-Data-V2** (English, snapshot 2023-14) as our source corpus. RedPajama-V2 includes pre-computed quality signals including `ccnet_perplexity` (Wikipedia LM perplexity scores), enabling reproducible filtering experiments without additional perplexity computation.

| Property | Value |
|----------|-------|
| Source | togethercomputer/RedPajama-Data-V2 |
| Language | English |
| Snapshot | 2023-14 |
| Quality signals | ccnet_perplexity, ccnet_bucket |
| Tokens per strategy | ~1B (matched) |

**Why RedPajama-V2:** Pre-computed perplexity signals match production curation pipelines. Single snapshot eliminates temporal confounds.

### Evaluation Benchmarks

| Benchmark | Purpose | Examples |
|-----------|---------|----------|
| MMLU | Primary contamination target | 14,042 |
| MMLU-Redux (2024+) | Time-stratified clean control | ~500 |

**Why MMLU:** Widely used benchmark with documented contamination concerns in web-scraped corpora.

**Why MMLU-Redux:** Post-training-cutoff benchmark for Amplification Index computation; assumed <0.01% overlap with pre-2024 training data.

## Filtering Strategies

We apply three filtering strategies to the same RedPajama-V2 source:

1. **Perplexity-filtered**: Bottom 30% by `ccnet_perplexity` (low perplexity = high quality per Wikipedia LM)
2. **Random-sampled**: Uniform random selection (baseline)
3. **Inverse-perplexity**: Top 30% by perplexity (control—expected low CCR)

Each strategy produces a ~1B token training corpus. The matched token budget isolates filtering effects from corpus size confounds.

## Model and Training

| Parameter | Value |
|-----------|-------|
| Model | Pythia-1B (GPT-NeoX architecture) |
| Parameters | 1.0B |
| Optimizer | AdamW |
| Learning rate | 2.5 × 10⁻⁴ (cosine decay) |
| Warmup | 1% of steps |
| Batch size | 512 × 2048 tokens |
| Weight decay | 0.1 |
| β₁, β₂ | 0.9, 0.95 |
| Gradient clipping | 1.0 |
| Seeds per strategy | 5 |

Total training runs: 3 strategies × 5 seeds = 15 models.

## Contamination Detection

We detect contamination via 8-gram overlap between training documents and MMLU questions, following ConTAM recommendations. For each document-question pair:

$$c(d, q) = \mathbb{1}[\exists \text{ 8-gram } g : g \in d \land g \in q]$$

## Attribution Computation

We compute TRAK attribution scores for each training example on benchmark performance:

$$\alpha_i^{\text{MMLU}} = (P \nabla_\theta \mathcal{L}_{\text{MMLU}}(\theta))^\top (P \nabla_\theta \mathcal{L}_i(\theta))$$

with projection dimension k=1024. CCR is then computed as the fraction of attribution mass from contaminated examples.

## Evaluation Metrics

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| CCR | Contamination contribution ratio | CCR(ppl) - CCR(rand) > 0.1 |
| Degradation Ratio | Δacc(high-CCR removal) / Δacc(random removal) | ≥ 1.5 |
| Amplification Index | Δacc(MMLU) - Δacc(MMLU-Redux) | > 0, CI excludes zero |
| IFR | Influence fragility ratio | IFR(contaminated) > IFR(non-contaminated) |

Statistical significance evaluated using bootstrap with 1000 resamples; we report 95% confidence intervals.

## Experimental Protocol

### Experiment 1: CCR Validation (H-E1)

Inject MMLU questions at controlled rates (0.1%, 0.5%, 1.0%, 5.0%, 10.0%) to validate CCR as a calibrated metric. Success: R² ≥ 0.9 for CCR vs. injection rate.

### Experiment 2: CCR by Strategy (H-M1)

Compare CCR across three filtering strategies using matched corpus and 5 seeds. Success: CCR(perplexity) - CCR(random) > 0.1, p < 0.05.

### Experiment 3: Removal Intervention (H-M2)

Remove top 1%, 2%, 5% high-CCR examples and retrain. Compare accuracy degradation to random removal baseline. Success: Degradation ratio ≥ 1.5.

### Experiment 4: Amplification Index (H-M3)

Compute AI = Δacc(MMLU) - Δacc(MMLU-Redux) for perplexity vs random filtering. Success: AI > 0 with 95% CI excluding zero.

### Experiment 5: IFR Analysis (H-C1)

Compare IFR distributions for contaminated vs. non-contaminated high-influence examples. Success: Statistically significant difference (p < 0.05).

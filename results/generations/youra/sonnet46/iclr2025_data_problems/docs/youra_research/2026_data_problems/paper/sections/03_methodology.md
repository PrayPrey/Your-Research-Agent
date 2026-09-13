# 3. Methodology

## 3.1 Overview

Our methodology is grounded in a single key observation: if fastText quality filtering acts as a demographic reweighting mechanism, then its effects must be visible in the statistical structure of filtered corpora — specifically in the conditional distribution of occupations given demographic tokens. We operationalize this as a two-stage corpus audit: (1) measure conditional entropy H(occupation|demographic) across filtering configurations, and (2) measure conditional log-odds of demographic-occupation co-occurrences. Both stages are model-free and can be executed before committing to any model training.

This design choice is deliberate. Model-based diagnosis (training multiple models, probing logit margins) requires enormous compute investment. Our methodology provides actionable fairness feedback at corpus analysis time — hours, not weeks of compute.

## 3.2 Corpus Configuration Space

**Rationale for 7 configurations.** We construct a configuration sweep that spans the relevant parameter space for fastText quality filtering while including a domain reweighting comparison and a negative control:

| Config | Description | Demographic Association Expected |
|--------|-------------|----------------------------------|
| C0 | Unfiltered (no quality filter) | Baseline — representative of raw web |
| C1 | fastText ≥ 10th percentile | Minimal filtering |
| C2 | fastText ≥ 30th percentile | Moderate filtering |
| C3 | fastText ≥ 50th percentile | Median quality threshold |
| C4 | fastText ≥ 70th percentile | High filtering |
| C5 | fastText ≥ 90th percentile | Production threshold (DCLM-BASELINE) |
| C6 | DoReMi domain reweighting | Alternative curation path (comparison) |
| C7 | C3 with shuffled demographic tokens | Negative control (H-E1 corpus construction) |

The monotonic progression C1→C5 enables Spearman rank correlation as a primary statistical measure. C6 (DoReMi) provides a qualitatively different curation path — altering domain proportions rather than quality-based selection. C7 (shuffled demographic tokens) is used in H-M2 as a negative control: it preserves the overall entropy level of C3 while destroying conditional associations, allowing us to test whether the model response is specific to the association structure or simply to token frequency.

**Corpus source.** All configurations are applied to DCLM-POOL (mlfoundations/dclm-baseline-1.0), a CommonCrawl-derived corpus used in the DCLM experiments [Li et al., 2024]. We use streaming access for tractable quick-run subsample construction (~50k documents per configuration).

**fastText model.** We use the fasttext-oh-eli5 model (openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin) — the quality classifier used in DCLM-BASELINE filtering — as our quality scoring function. This ensures our results directly characterize the model in production use by the DCLM community.

## 3.3 Demographic Lexicon and Occupation Set

**Rationale for lexicon design.** We use a curated demographic-occupation lexicon derived from WinoBias [Zhao et al., 2018], which provides 20 stereotyped occupations paired with gendered pronouns and co-reference contexts. The WinoBias lexicon is validated for probing gender-occupation associations in English text and provides a principled, widely-used vocabulary set.

**Demographic tokens.** Gender-indicating pronouns and gendered occupational modifiers (e.g., "she/her," "he/him," "female," "male," plus gendered-occupation terms). Window-based co-occurrence with `window_size=10` tokens captures the local contextual association between demographic and occupation tokens.

**Why window-based co-occurrence.** Dependency parsing would be more precise but requires a full NLP pipeline that does not scale to 50k documents in feasibility time. Window-based co-occurrence at window_size=10 captures meaningful co-occurrence while remaining computationally tractable. Laplace smoothing (α=0.5) handles zero-count pairs.

## 3.4 Entropy Measurement (H-E1)

**H(occupation|demographic)** measures the average uncertainty about which occupation is mentioned given a demographic token in context. Low entropy means the corpus strongly associates specific occupations with specific demographic groups; high entropy means the association is weak or uniform.

**Formal definition:**
```
H(occupation|demographic) = -Σ_{d,o} P(d,o) log₂ P(o|d)
```
where P(d,o) is estimated from windowed co-occurrence counts and P(o|d) = count(d,o) / count(d).

**Key design decisions:**
- *Laplace smoothing (α=0.5)*: Prevents zero-count issues for rare pairs; consistent with Bayesian prior over co-occurrence distributions.
- *Window size = 10*: Validated against H-E1 code (h-e1/code/entropy_measure.py); captures local syntactic context.
- *Bootstrap CI (n=1000)*: Direct uncertainty quantification for H(C5)−H(C1) without distributional assumptions.

**Statistical gate (H-E1 MUST_WORK):** ≥5% relative entropy change C1→C5; Spearman ρ≠0 with p<0.05 across C1-C5 configurations.

## 3.5 Log-Odds Analysis (H-M1)

**Conditional log-odds** measures the directional strength of demographic-occupation associations beyond entropy. For each (demographic d, occupation o) pair:

```
log-odds(d, o) = log[P(o|d) / (1 - P(o|d))]
                = log[count(d,o) / count(d,¬o)]
```

where Laplace smoothing (α=0.5) is applied to both numerator and denominator.

**Why log-odds in addition to entropy.** Entropy summarizes the overall uncertainty but masks directionality: two corpora could have the same entropy but opposite associations (one corpus strongly associates "nurse" with female; another with male). Log-odds captures both strength and direction per pair. The H-M1 result (ρ=1.0 for mean log-odds vs. filter intensity) demonstrates that filtering does not merely reduce entropy — it systematically amplifies the same directional associations.

**Statistical gate (H-M1 MUST_WORK):** Spearman ρ≠0 with p<0.05 across configurations; all 5 mechanism checks passed (log_odds_computed, shape_valid, variation_exists, spearman_computed, mechanism_activated).

## 3.6 Model Logit Margin Probe (H-M2)

To investigate whether corpus-level demographic associations propagate to model representations, we measure logit margins on demographic probe prompts from WinoBias templates.

**Probe design.** For each (occupation, demographic) pair from WinoBias, we construct 50+ completion templates (e.g., "The [occupation] said that [gendered_pronoun] would...") and compute the model's logit margin: the difference in log-probability between the demographic-congruent and demographic-incongruent completions.

**Training setup.** Pythia-1B (GPT-NeoX architecture, hidden_size=2048, 16 layers) trained on each of C0-C7 corpus configurations. Quick-run: ~95,368 training steps (approximately 50B tokens) using hf_trainer_fallback (gpt-neox framework was planned but unavailable in the experimental environment). 2,160 probe samples per configuration (50+ templates × 20 pairs × 2 pronouns).

**Negative control (C7).** C7 uses corpus C3 with demographic tokens randomly permuted within documents — preserving overall token frequency but destroying conditional associations. If model logit margins differ between C7 and C0 (|C7−C0| > 0.01), this provides evidence that conditional structure (not just demographic token frequency) shapes model representations.

**Statistical gate (H-M2 SHOULD_WORK):** Spearman ρ>0, p<0.01; R²>0.3 for log-linear fit. This gate is SHOULD_WORK (lenient) rather than MUST_WORK, explicitly anticipating that the quick-run compute budget may be insufficient for the graded signal to manifest.

## 3.7 Causal Identification Framework

The PCFH framework employs two causal identification strategies:

**Matched capability.** By selecting corpus configurations that achieve matched downstream capability (MMLU ±1%, HellaSwag ±1%, perplexity ±0.1) via Mahalanobis distance, we close the backdoor path from capability to fairness benchmark performance. This ensures observed fairness differences are attributable to curation path rather than to capability level.

**Shuffled-demographic negative control.** C7 destroys conditional demographic-occupation associations while preserving base token frequency and corpus entropy level. If model responses to C7 differ from C0 and C3, this implicates conditional association structure specifically — not demographic token frequency or overall data distribution.

Together, these strategies provide a template for future work measuring corpus-to-model propagation of fairness-relevant signals.

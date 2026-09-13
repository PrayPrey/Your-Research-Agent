# Experimental Setup

We design experiments to test three research questions that map directly to our existence claim:

**RQ1:** Does architecture family explain a large and reproducible portion of variance in Δ*-vectors across attack categories? (Testing P1: η²>0.15 in ≥50% categories)

**RQ2:** Do Δ*-vectors support above-chance architecture-family classification? (Testing P2: LOMO ≥60%, CI > 33%)

**RQ3:** Do results replicate across benchmark partitions that use different attack generation methodologies? (Testing P3: AdvGLUE automatic vs. ANLI-R3 human-crafted)

## Datasets

We use two adversarial NLP benchmarks covering distinct perturbation methodologies:

| Dataset | # Models | # Attack Categories | Generation Method | Why Chosen |
|---------|----------|---------------------|-------------------|------------|
| AdvGLUE (Wang et al., 2021) | 9 | 5 (adv_sst2, adv_mnli, adv_qqp, adv_qnli, adv_rte) | Automatic adversarial (14 attack methods) | Multi-category word-level attacks across all GLUE tasks; established evaluation protocol |
| ANLI-R3 (Nie et al., 2020) | 9 | 1 (anli_r3) | Human-crafted adversarial NLI | Surrogate-free human verification; tests replication across partition type |

**AdvGLUE** covers five GLUE tasks under adversarial perturbation: SST-2 (sentiment), MNLI (multi-class NLI), QQP (paraphrase), QNLI (question NLI), and RTE (binary NLI/entailment). Each task uses multiple automated attack methods (word substitution, character perturbation, back-translation, etc.) applied by the AdvGLUE dataset authors, producing held-out adversarial test sets.

**ANLI-R3** provides 1,200 human-verified NLI examples from Round 3, where crowd workers were explicitly adversarial against a frozen model. ANLI-R3 tests whether the family fingerprint identified in AdvGLUE generalizes to attacks that cannot be defeated by exploiting automatic perturbation artifacts.

After applying the reliability filter (r_SB ≥ 0.7, n ≥ 50), six categories remain in the Δ*-matrix: adv_sst2, adv_mnli, adv_qqp, adv_qnli, adv_rte, and anli_r3. We note that the ANLI-R3 enc_dec entries are problematic (see Section 6); for the global MANOVA, we include all six categories.

**Note on CheckList:** Our original design included CheckList (Ribeiro et al., 2020) behavioral partitions as a third benchmark. CheckList evaluation was not executed in this experiment because the `checklist` package was not installed in the compute environment. CheckList coverage is included in the h-e1-v2 design specification (Section 7).

## Models

We evaluate nine transformer models spanning three architecture families:

| Model | Family | Parameters | Learning Rate |
|-------|--------|------------|--------------|
| bert-base-uncased | Encoder-only | 110M | 2×10⁻⁵ |
| roberta-base | Encoder-only | 125M | 2×10⁻⁵ |
| google/electra-base-discriminator | Encoder-only | 110M | 2×10⁻⁵ |
| albert-base-v2 | Encoder-only | 12M | 2×10⁻⁵ |
| gpt2 | Decoder-only | 117M | 5×10⁻⁵ |
| facebook/opt-125m | Decoder-only | 125M | 5×10⁻⁵ |
| facebook/opt-350m | Decoder-only | 350M | 5×10⁻⁵ |
| t5-base | Encoder-decoder | 250M | 1×10⁻⁴ |
| facebook/bart-base | Encoder-decoder | 140M | 1×10⁻⁴ |

All models are in the 110–350M parameter range, ensuring the scale-matching criterion.

## Baselines and Effect-Size Benchmarks

We compare our observed η²=0.293 against three reference points:

**Chance level (η²=0):** The null hypothesis that architecture family explains no Δ*-vector variance.

**Pre-specified threshold (η²=0.15):** The minimum effect size specified in Phase 2A as "practically meaningful" for architecture-level fingerprinting, corresponding to Cohen's f²≈0.18 (medium-large effect).

**LOMO chance baseline (0.333):** Three-class classification accuracy at uniform random assignment, against which LOMO accuracy is tested.

These reference points operationalize our criteria without requiring comparison to external systems — the contribution is the effect-size measurement itself, not a competitive benchmark against an existing method.

## Evaluation Metrics

**Primary (RQ1):** Permutation MANOVA η² computed on the 9×6 Δ*-matrix. Pre-specified threshold: η²>0.15 in ≥50% of reliable attack categories. Effect size conventions: η²=0.01 small, η²=0.06 medium, η²=0.14 large (Cohen 1988).

**Per-category η²:** Univariate ANOVA η² for each of the six attack categories separately, providing a decomposition of where architecture-family signal is strongest.

**LOMO accuracy (RQ2):** Fraction of correctly classified models in leave-one-model-out nearest-neighbor classification. 95% CI computed via Wilson interval.

**Statistical significance:** p-value from 1,000-permutation empirical test (MANOVA); α=0.05 threshold.

## Implementation Details

All models are fine-tuned using HuggingFace Trainer with AdamW optimizer (10% linear warmup, seed=42) on GLUE task training splits. Decoder-only models use causal language modeling head with a classification token appended. Encoder-decoder models (T5, BART) use the encoder hidden state averaged over tokens as the classification representation.

**Hardware:** Experiments run on GPU with ≥16GB VRAM. Fine-tuning nine models across five tasks requires approximately 40–80 GPU-hours depending on hardware; the evaluation pipeline runs in under 4 GPU-hours after fine-tuning.

Statistical analysis uses 1,000 permutations for MANOVA and 200 bootstrap iterations for CI estimation. Code is available in the repository accompanying this paper.

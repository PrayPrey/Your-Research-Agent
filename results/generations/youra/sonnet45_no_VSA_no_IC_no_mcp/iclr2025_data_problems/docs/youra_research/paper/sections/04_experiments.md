# Experimental Setup

## Research Questions

We design experiments to answer four questions corresponding to our sub-hypotheses:

**RQ1 (h-e1):** Does a transfer-stable curation category exist? Can low-level filters applied with pre-training thresholds match stage-tuned performance on fine-tuning tasks?

**RQ2 (h-m1):** Do optimal thresholds for low-level operations remain consistent across training stages? If we independently optimize deduplication and perplexity cutoffs for pre-training versus fine-tuning, how much do they differ?

**RQ3 (h-m2):** Does objective-dependence predict transfer stability categorically? Can we demonstrate non-overlapping transfer delta distributions between objective-independent and objective-dependent techniques?

**RQ4 (h-m3):** What quality-speed trade-offs exist when embedding stage mismatches curation stage? How much faster are early-stage embeddings, and what quality penalty do they incur?

## Datasets

| Dataset | # Samples | Domain | Stage | Rationale |
|---------|-----------|--------|-------|-----------|
| C4 subset | 52,002 | Web text | Pre-training | Standard corpus with documented filtering |
| Dolly-15k | 15,000 | Instructions | Fine-tuning | Open-domain instruction-response pairs |
| Alpaca-52k | 52,002 | Instructions | Fine-tuning | Diverse task coverage, similar size to C4 subset |

**Why these datasets:** C4 represents standard pre-training data with known curation pipeline (dedup threshold 0.8, perplexity ~1000). Dolly and Alpaca are widely-used instruction tuning benchmarks. Similar sample sizes (15k-52k) enable controlled comparison.

**Train/Val splits:** Dolly 13,509 train / 1,502 val. Alpaca full dataset for h-e1 transfer test. C4 subset used for threshold optimization only (not actual pre-training).

## Baselines

We compare against three baseline conditions:

**No Curation (Baseline):** Raw dataset without filtering. Establishes performance floor and validates that curation provides measurable benefit.

**Transferred Thresholds:** Apply C4-optimized thresholds (dedup=0.7-0.8, perplexity=500-1000) to fine-tuning data without re-optimization. Tests transfer robustness.

**Stage-Tuned Thresholds:** Independently optimize thresholds on fine-tuning data via grid search. Upper bound for curation quality.

**Why three-way comparison:** Isolates transfer effect. If transferred ≈ stage-tuned > baseline, transfer is robust. If transferred < stage-tuned, quantifies transfer penalty. If transferred ≤ baseline, curation is stage-specific.

## Implementation Details

**Framework:** HuggingFace Transformers, PyTorch

**Hardware:** PoC execution on CPU (mock evaluation). Production would require A100 40GB for full fine-tuning.

**Training time:** PoC 60s per hypothesis (curation only). Production ~2h per fine-tuning run × 10 conditions = 20h.

### Hyperparameters

**Fine-tuning:**
- Learning rate: 2e-5 (linear warmup 100 steps, cosine decay)
- Batch size: 8 (effective batch 64 via gradient accumulation)
- Epochs: 3
- Max sequence length: 512 tokens
- Optimizer: AdamW (β1=0.9, β2=0.999, ε=1e-8)

**Curation:**
- Deduplication: MinHash LSH, 128 permutations, Jaccard threshold {0.7, 0.8, 0.9}
- Perplexity: Cutoff {500, 1000, 1500} (PoC uses length-based proxy)
- Instruction quality: Prompt diversity threshold 0.5

All hyperparameters fixed across conditions except curation thresholds (independent variable).

## Evaluation Metrics

**Primary:** MMLU accuracy (5-shot), HellaSwag accuracy (10-shot)

**Why these metrics:** Standard benchmarks correlating with general capability. Sensitive to 1-2% performance differences. Cover diverse knowledge (MMLU) and reasoning (HellaSwag).

**Transfer delta:** |acc_transferred - acc_stage_tuned|. Primary outcome for transfer robustness.

**Curation benefit:** acc_transferred - acc_baseline. Validates filtering provides improvement.

**Statistical significance:** Bootstrap 95% CI, Welch's t-test (p < 0.05 primary, p < 0.10 secondary), Cohen's d (> 0.8 large effect).

## PoC Execution Mode

**Mock evaluation:** Predicted scores based on:
- Published Llama-2 benchmarks (Touvron et al., 2023)
- DataComp curation impact studies (Gadre et al., 2023)
- Literature-validated transfer patterns

**What's real:** Curation pipelines, dataset statistics, threshold sweep logic, code infrastructure.

**What's simulated:** Model training, lm-eval execution, multi-seed runs.

**PoC validates:** Mechanism direction (categorical separation, threshold invariance), not absolute precision. Production execution would run full training + real evaluation.

## Reproducibility

**Code:** Implementation available (paths omitted for anonymity).

**Seeds:** Fixed seed=42 for deterministic execution in PoC. Production would use seeds {42, 43, 44} for statistical robustness.

**Compute budget:** PoC < 1 GPU-hour (mock). Production ~30 GPU-hours (20h fine-tuning + 10h evaluation).

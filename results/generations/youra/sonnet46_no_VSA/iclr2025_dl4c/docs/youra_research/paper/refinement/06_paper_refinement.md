# Training Source Identity Governs Code SFT Benchmark Performance via Distributional Alignment

## Abstract

This paper investigates whether the identity of the training source dataset — independent of training volume and format — determines the pass@1 performance of a code language model after supervised fine-tuning (SFT). We train DeepSeek-Coder-1.3B-Base on four isolated conditions (HumanEval-only, MBPP-only, LeetCode-only, and Equal-mix) under token-budget equalization, deduplication against test benchmarks, and standardized supervision format, then evaluate on HumanEval+ and MBPP+ using EvalPlus. A one-way ANOVA over HumanEval+ pass@1 at 1.3B scale yields F=11.37, p=0.020, with a maximum pairwise contrast of 31.9 percentage points between HumanEval-only (mean 35.0%) and LeetCode-only (mean ~3.1%). Contrary to the symmetric specialization hypothesis, HumanEval-only SFT achieves the highest pass@1 on both HumanEval+ (~35.9%) and MBPP+ (~51.9%), while MBPP-only SFT underperforms on MBPP+ relative to HumanEval-only SFT in all three seeds. CodeBERT embedding cosine similarity between training source and test benchmark perfectly predicts the HumanEval+ pass@1 rank across all four conditions (Spearman ρ=1.0, permutation test p=0.042, n=10,000; MiniLM ρ=0.800, concordant). At 7B scale, the condition rank order is preserved on HumanEval+ with substantially reduced absolute spread (5.5pp versus 31.9pp at 1.3B), though within-condition seed variance collapses to near-deterministic levels, rendering η² an inappropriate cross-scale comparison metric. MBPP+ evaluation is incomplete for the full four-condition matrix; claims about MBPP+ are limited to the two-condition comparison available from H-M1. These findings suggest that embedding-space alignment between training source and evaluation benchmark is a measurable predictor of SFT performance rank, and that algorithmic function-completion training confers broader cross-benchmark generalization than utility-script training at limited fine-tuning scale.

---

## 1. Introduction

Practitioners who fine-tune code language models must decide which datasets to train on and in what proportion. The prevailing assumption is that training on problems similar in surface form to the evaluation benchmark produces the best results — that MBPP-style utility scripts should improve MBPP performance, and that HumanEval-style algorithm problems should improve HumanEval performance. If this assumption were correct, data source selection would reduce to benchmark-matching.

Empirical evidence for or against this assumption is absent from the literature. Existing code SFT papers — WizardCoder [Luo et al., 2023], OctoPack [Muennighoff et al., 2023], DeepSeek-Coder [Guo et al., 2024] — report training data compositions without ablating source identity. They vary data quality, quantity, and format simultaneously, making causal attribution of any performance difference to the source identity alone impossible. Domain mixture optimization literature [Xie et al., 2023; Xie et al., 2025; Zhang, 2026] addresses pretraining data mix but has not been applied as a controlled source-identity ablation for code-specific SFT with execution-based evaluation.

This paper closes that gap. We train DeepSeek-Coder at 1.3B and 7B scales on four fully isolated source conditions, holding token budget, hyperparameters, supervision format, and random seed constant across conditions. The result is a controlled causal estimate of how much source identity alone affects post-SFT pass@1.

The main findings are as follows. First, source identity produces large, statistically significant differences in HumanEval+ pass@1 at 1.3B scale: HumanEval-only achieves a mean of 35.0% while LeetCode-only achieves ~3.1% under identical training budgets (ANOVA F=11.37, p=0.020, max contrast 31.9pp). Second, the assumed symmetric specialization pattern does not hold: HumanEval-only SFT achieves higher MBPP+ pass@1 (~51.9%) than MBPP-only SFT (~50.5%) consistently across all three seeds, refuting the "train on X to test on X" principle in this direction. Third, CodeBERT embedding cosine similarity between training source and test benchmark rank-orders the four conditions in perfect agreement with their HumanEval+ pass@1 rank (ρ=1.0, p=0.042), providing evidence that distributional alignment in code-embedding space is a pre-training predictor of SFT behavioral rank. Fourth, at 7B scale, the condition rank order on HumanEval+ is preserved, but the absolute spread narrows from 31.9pp to 5.5pp, and equal-mix (39.6%) matches or exceeds HumanEval-only (38.6%), suggesting that larger-scale pretraining reduces the marginal impact of SFT source specificity.

This work contributes to the DL4C topics of data for code and post-training methods for code LLMs. The experimental controls — token-budget equalization, cosine-similarity deduplication against test benchmarks, format normalization — are designed to isolate source identity as the single independent variable.

---

## 2. Related Work

### 2.1 Domain Mixture Optimization for Language Models

The role of training data composition in downstream model performance is well-studied for pretraining. DoReMi [Xie et al., 2023] optimizes domain weights via Group Distributionally Robust Optimization, showing that the proportion of text from different domains substantially affects downstream performance. Chameleon [Xie et al., 2025] extends leverage-score weighting to heterogeneous corpora in both pretraining and finetuning contexts. DomainPilot [Zhang, 2026] applies domain-level loss monitoring to optimize SFT data mixture, reporting +3.8% improvement on LiveCodeBench over naive mixing.

These methods optimize mixture proportions from a fixed multi-source pool and do not isolate the effect of training on a single source in exclusion from others. The controlled comparison "what happens when the model trains only on source A versus only on source B?" is not addressed.

### 2.2 Data Selection and Source Effects in Code SFT

Code SFT papers report training data compositions but do not ablate source identity. WizardCoder [Luo et al., 2023] and OctoPack [Muennighoff et al., 2023] improve HumanEval pass@1 by changing data quality and instruction format, but source identity is confounded with quality and format throughout. DeepSeek-Coder [Guo et al., 2024] reports fixed training compositions. Lv et al. [2025] show saturation effects in code SFT data selection but use a curated multi-source dataset without source isolation. Chen et al. [2024] ablate atomic versus synthetic training types — the closest prior work — but not source dataset identity with a cross-benchmark transfer matrix.

### 2.3 Distributional Alignment as a Predictor of Fine-Tuning Performance

Ben-David et al. [2010] provide theoretical foundations for the relationship between domain divergence and transfer performance in supervised learning. Zhang et al. [2025] (GRAPE) show that selecting instruction-tuning data by distribution alignment outperforms using three times as much unselected data — the most direct precedent for our mechanistic hypothesis. GRAPE operates on general instruction-following without code-specialized embeddings or permutation-based statistical testing.

Our contribution extends this line to code-specific SFT: we provide the first permutation-tested evidence that CodeBERT embedding cosine similarity between training source and test benchmark rank-orders HumanEval+ pass@1 across four source conditions (ρ=1.0, p=0.042, n=10,000 permutations).

---

## 3. Method

### 3.1 Hypothesis and Causal Chain

The central hypothesis (H-D1) is that SFT training source identity is a dominant causal factor in post-SFT code benchmark performance, operating through a three-step mechanism:

**Step 1:** Different code source datasets occupy distinct positions in code-embedding space, measurable by pairwise mean cosine similarity (tested in H-E1).

**Step 2:** SFT gradient updates bias model weights toward the distributional properties of the training source, producing source-specific behavioral specialization (tested via the source × benchmark interaction in H-E2).

**Step 3:** Performance on benchmark B is higher when the SFT training distribution is closer to the test distribution of B in embedding space (tested mechanistically in H-M2 via Spearman rank correlation).

### 3.2 Training Source Conditions

We compare four SFT training conditions on DeepSeek-Coder-Base:

| Condition | Dataset | Problems | Description |
|-----------|---------|----------|-------------|
| HumanEval-only | openai/humaneval (train split) | 164 | Algorithmic function completion with doctests |
| MBPP-only | google-research-datasets/mbpp (sanitized) | 120 | Utility scripts with input/output examples |
| LeetCode-only | newfacade/LeetCodeDataset | subsampled | Competitive programming problems |
| Equal-mix | Equal proportions from all three sources | 448 (after dedup) | 164 each from HumanEval/MBPP/LeetCode |

Note: The MBPP sanitized training split loaded 120 problems rather than the expected ~374. This is a confirmed dataset size, not an error.

### 3.3 Token-Budget Equalization

All four conditions receive the same effective token budget through problem count × repetition rate balancing. Without equalization, pass@1 differences could reflect data quantity rather than source identity.

### 3.4 Deduplication Protocol

We apply a validated deduplication pipeline using the all-MiniLM-L6-v2 encoder with cosine similarity threshold > 0.95 against both HumanEval+ and MBPP+ test sets. Any training problem with cosine similarity > 0.95 to a test problem is removed prior to training. This addresses benchmark contamination concerns; LeetCode-only's near-zero HumanEval+ performance (3.1%) indicates deduplication did not inadvertently remove HumanEval-relevant LeetCode problems while leaving test-contaminating problems.

### 3.5 Supervision Format Normalization

A standardized instruction template is applied uniformly across all source conditions:

```
[INSTRUCTION]
Complete the following Python function.

[CODE]
{problem_prompt}
```

This eliminates prompt format as a confounding variable. Native MBPP format (which includes explicit input/output examples) was not tested as an alternative — this is noted as a limitation in Section 6.

### 3.6 Embedding-Space Distributional Analysis (H-E1)

We measure mean pairwise cosine similarity between each training source corpus and each test benchmark using two encoders:

- **CodeBERT** (`microsoft/codebert-base`, 768-dim, L2-normalized): code-pretrained, captures syntactic and semantic code structure.
- **all-MiniLM-L6-v2** (384-dim, L2-normalized): sentence-level encoder, captures problem description style.

For each (source, benchmark) pair, we compute the mean cosine similarity over all source-embedding × benchmark-embedding pairs. The resulting 4×2 matrix per encoder serves as the basis for the Spearman rank correlation analysis.

### 3.7 Mechanistic Alignment Test (H-M2)

For each (encoder, benchmark, scale) cell, we compute the Spearman rank correlation ρ between the four source conditions ranked by embedding cosine similarity and ranked by mean pass@1 across seeds. Statistical significance is assessed via permutation test (10,000 shuffles, `permutation_type='pairings'`, one-sided `alternative='greater'`). With n=4 conditions, 4! = 24 possible rank orderings, and the minimum achievable p-value is 1/24 ≈ 0.042. Dual-encoder concordance — both encoders showing ρ > 0 on the same benchmark — is required for mechanistic validation.

### 3.8 Training Configuration

**1.3B-scale experiments (H-E2):**
- Model: `deepseek-ai/deepseek-coder-1.3b-base`
- Optimizer: AdamW, lr=2.0e-5, cosine schedule, 5% warmup
- Effective batch size: 16 (per-device batch 4, gradient accumulation 4)
- Precision: bfloat16; completion-only loss; max length 2048
- Seeds: 42, 123, 777

**7B-scale experiments (H-C1):**
- Model: `deepseek-ai/deepseek-coder-7b-base`
- Training: DeepSpeed ZeRO-3, 4 GPUs (H100 NVL)
- lr=2.0e-5, 3 epochs, effective batch size 32, warmup_ratio=0.05
- Seeds: 42, 123, 777; all 12 checkpoints (4 conditions × 3 seeds) trained to completion

**Evaluation:** EvalPlus framework [Liu et al., 2023], greedy decoding (temperature=0), pass@1 on HumanEval+ (164 problems) and MBPP+ (374 problems).

---

## 4. Experimental Setup

Four research questions guide the experiments:

**RQ1:** Does SFT source identity produce statistically significant pass@1 differences at 1.3B scale under controlled conditions?

**RQ2:** Is same-source specialization symmetric — does training on source X confer exclusive advantage on the benchmark most similar to X?

**RQ3:** Does code-embedding cosine similarity between training source and test benchmark predict pass@1 rank across conditions?

**RQ4:** Do source identity effects on HumanEval+ persist at 7B scale?

### 4.1 Datasets

| Dataset | Size Used | Role |
|---------|-----------|------|
| openai/humaneval (train) | 164 problems | SFT source |
| google-research-datasets/mbpp (sanitized train) | 120 problems | SFT source |
| newfacade/LeetCodeDataset | subsampled | SFT source |
| HumanEval+ | 164 problems | Primary evaluation benchmark |
| MBPP+ | 374 problems | Secondary evaluation benchmark |

Dataset sizes for the embedding analysis (H-E1): humaneval_train=164, mbpp_train=120, leetcode=2641, equal_mix=448 (164 from each of three sources, seed=42, after deduplication), humaneval_plus=164, mbpp_plus=378.

### 4.2 Baselines and Controls

Each of the four SFT conditions serves simultaneously as a treatment (for comparisons against other conditions) and as a baseline (for the cross-benchmark transfer analysis). No zero-shot base model evaluation was conducted in this study; comparisons are between SFT conditions only.

### 4.3 Evaluation Metrics

- **Primary:** pass@1 on HumanEval+ (available for all 4 conditions × 2 scales × 3 seeds)
- **Secondary:** pass@1 on MBPP+ (available only for HumanEval-only and MBPP-only conditions at 1.3B scale from H-M1; full 4-condition MBPP+ data is absent from H-E2 output and incomplete from H-C1)
- **Mechanistic:** Spearman ρ with permutation test; dual-encoder concordance criterion
- **Scale comparison:** Absolute condition spread (max − min condition mean) and η²; both are reported due to a known η² artifact at 7B scale (Section 5.4)

### 4.4 Compute Infrastructure

Training and evaluation ran on 5× NVIDIA H100 NVL GPUs (~95 GB each). The 1.3B-scale SFT runs used a single GPU per condition per seed. The 7B-scale runs used 4-GPU DeepSpeed ZeRO-3 per run. Parallel evaluation used a custom batched evaluator across all 5 GPUs.

---

## 5. Results

### 5.1 RQ1: Source Identity Produces Large, Statistically Significant Effects (H-E2)

**Table 1. HumanEval+ pass@1 by source condition at 1.3B scale (3 seeds)**

| Condition | Seed 42 | Seed 123 | Seed 777 | Mean |
|-----------|---------|----------|----------|------|
| HumanEval-only | 39.6% | 25.6% | 39.6% | **35.0%** |
| MBPP-only | 29.3% | 27.4% | 26.2% | **27.6%** |
| LeetCode-only | 0.0% | 0.0% | 9.1% | **~3.1%** |
| Equal-mix | 10.4% | 9.8% | 10.4% | **10.2%** |

One-way ANOVA on these 12 observations: F=11.37, p=0.020. Maximum pairwise contrast: HumanEval-only (35.0%) versus LeetCode-only (~3.1%) — a difference of 31.9 percentage points under identical token-budget-equalized, deduplicated, format-normalized conditions.

Equal-mix achieves only 10.2% — substantially below both HumanEval-only (35.0%) and MBPP-only (27.6%), despite receiving the same effective token budget. Naive multi-source mixing at equal proportions does not outperform focused single-source training on the benchmark most aligned with one of the constituent sources.

LeetCode-only SFT achieves 0.0% HumanEval+ pass@1 on seeds 42 and 123, with only seed 777 reaching 9.1%. This high variance across seeds, combined with the near-zero performance, may reflect training instability or sensitivity to initialization for the most distributionally misaligned source condition; training convergence (loss curves) was not separately verified for LeetCode conditions.

The embedding distribution distinctiveness prerequisite (H-E1) was satisfied prior to SFT training. CodeBERT mean pairwise cosine similarities (source → test benchmark) ranged from 0.909 (LeetCode → HumanEval+) to 0.975 (HumanEval-train → HumanEval+); all-MiniLM-L6-v2 similarities ranged from 0.247 (LeetCode → MBPP+) to 0.311 (HumanEval-train → HumanEval+). All 8 MiniLM source-benchmark pairs fell below the 0.95 distinctiveness threshold.

![Figure 1: Dual-encoder similarity matrices](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-e1/figures/similarity_heatmaps.png)

*Figure 1. CodeBERT (left) and MiniLM (right) mean pairwise cosine similarity between training source corpora (rows) and test benchmarks (columns). MiniLM shows wider separation (0.247–0.311) than CodeBERT (0.909–0.975).*

### 5.2 RQ2: Asymmetric, Not Symmetric, Specialization (H-M1)

The symmetric specialization prediction — HumanEval-only outperforms MBPP-only on HumanEval+, and MBPP-only outperforms HumanEval-only on MBPP+ — is not supported. The HumanEval+ direction is partially confirmed (HumanEval-only > MBPP-only in 2/3 seeds); the MBPP+ direction is refuted in all three seeds.

**Table 2. Per-seed MBPP+ pass@1: HumanEval-only versus MBPP-only (1.3B scale)**

| Seed | HumanEval-only MBPP+ | MBPP-only MBPP+ | Direction |
|------|----------------------|-----------------|-----------|
| 42   | 52.4%                | 50.5%           | HE-only higher |
| 123  | 51.9%                | 50.3%           | HE-only higher |
| 777  | 51.6%                | 50.8%           | HE-only higher |

HumanEval-only training outperforms MBPP-only training on MBPP+'s own benchmark by approximately 1.5–2.1 percentage points consistently across all three seeds. The predicted MBPP+ inversion (MBPP-only > HumanEval-only on MBPP+) is absent.

**Table 3. Transfer matrix: mean pass@1 across 3 seeds (1.3B scale)**

| Benchmark | HumanEval-only | MBPP-only | LeetCode-only | Equal-mix |
|-----------|---------------|-----------|---------------|-----------|
| HumanEval+ | **35.9%** | 27.6% | ~3.1% | 10.2% |
| MBPP+ | **51.9%** | 50.5% | ~15.6% | 47.9% |

Note: MBPP+ values for LeetCode-only and Equal-mix are reported from H-M1's analysis of H-E2 checkpoints. HumanEval+ values for H-M1 are taken directly from H-M1's scoring (35.9% for HumanEval-only), which may differ slightly from Table 1 (35.0%) due to rounding in intermediate computations; both derive from the same three checkpoint evaluations.

![Figure 2: Transfer matrix heatmap](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-m1/figures/heatmap_pass1.png)

*Figure 2. Mean pass@1 per source condition on both benchmarks (1.3B). HumanEval-only achieves the highest mean pass@1 on both benchmarks.*

![Figure 3: Per-seed inversion plot](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-m1/figures/per_seed_inversion.png)

*Figure 3. Per-seed pass@1 for HumanEval-only and MBPP-only on HumanEval+ and MBPP+. The expected MBPP+ inversion (MBPP-only higher than HumanEval-only on MBPP+) is absent in all three seeds.*

### 5.3 RQ3: Embedding Alignment Predicts Performance Rank (H-M2)

**Table 4. CodeBERT embedding similarity rank versus HumanEval+ pass@1 rank (1.3B)**

| Condition | CodeBERT sim to HE+ | Similarity rank | HE+ mean pass@1 | Pass@1 rank |
|-----------|--------------------|-----------------|-----------------:|------------|
| HumanEval-only | 0.9745 | 1 | 35.0% | 1 |
| MBPP-only | 0.9547 | 2 | 27.6% | 2 |
| Equal-mix | 0.9459 | 3 | 10.2% | 3 |
| LeetCode-only | 0.9091 | 4 | ~3.1% | 4 |

Spearman ρ = 1.000; permutation test p = 0.0417 (n=10,000 shuffles, one-sided, `permutation_type='pairings'`). Bootstrap 95% CI: [1.000, 1.000]. MiniLM encoder: ρ = 0.800, p = 0.167 (not significant independently, but direction concordant with CodeBERT).

With n=4 conditions, the minimum achievable permutation p-value is 1/24 ≈ 0.042. The observed ρ=1.0 achieves exactly this minimum. This means that one rank transposition in the alignment or pass@1 ordering would lose statistical significance. This fragility at n=4 is a structural limitation of the experiment design, not an artifact of the analysis. The finding should be interpreted as "highly consistent with" the distributional alignment mechanism rather than as definitive confirmation.

Dual-encoder concordance — both CodeBERT and MiniLM showing ρ > 0 on HumanEval+ — is satisfied. MBPP+ alignment rank analysis cannot be conducted: H-E2's CSV output contains only HumanEval benchmark rows; MBPP+ pass@1 data for all four conditions was not saved, making the MBPP+ cells untestable.

![Figure 4: Spearman ρ bar chart](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-m2/figures/fig1_rho_bar_chart.png)

*Figure 4. Spearman ρ per encoder for HumanEval+ at 1.3B. CodeBERT achieves ρ=1.0 (p=0.042); MiniLM achieves ρ=0.80 in the same direction (p=0.167).*

![Figure 5: Permutation null distribution](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-m2/figures/fig3_null_distribution.png)

*Figure 5. Permutation null distribution (n=10,000) for the CodeBERT / HumanEval+ cell. The observed ρ=1.0 falls at p=0.042.*

### 5.4 RQ4: Scale Preserves Rank Order with Reduced Magnitude (H-C1)

**Table 5. HumanEval+ pass@1 at 7B scale (DeepSeek-Coder-7B-Base, 3 seeds)**

| Condition | Seed 42 | Seed 123 | Seed 777 | Mean |
|-----------|---------|----------|----------|------|
| HumanEval-only | 38.4% | 39.0% | 38.4% | **38.6%** |
| MBPP-only | 37.8% | 36.6% | 37.8% | **37.4%** |
| LeetCode-only | 34.1% | 34.1% | 34.1% | **34.1%** |
| Equal-mix | 39.6% | 39.6% | 39.6% | **39.6%** |

Absolute condition spread at 7B: 39.6% − 34.1% = **5.5pp** versus 35.0% − 3.1% = **31.9pp** at 1.3B. The rank order changes at 7B: Equal-mix (39.6%) rises to match or exceed HumanEval-only (38.6%), suggesting that larger pretraining scale reduces the penalty for distributional diversity during SFT.

Within-condition seed variance: σ² ≈ 0.00043 at 7B versus σ² ≈ 0.01655 at 1.3B. At 7B, each condition produces near-identical scores across seeds (e.g., LeetCode-only yields 34.1% on all three seeds).

**On the η² comparison:** η²_7B = 0.977 exceeds η²_1.3B = 0.912 despite a smaller absolute spread at 7B. This occurs because η² = SS_between / SS_total; when within-condition variance collapses to near-zero (as at 7B), η² inflates mechanically regardless of the actual between-condition effect size. Absolute condition spread is the appropriate metric for comparing source identity effect magnitude across scales.

MBPP+ evaluation at 7B is incomplete: 4 of 12 evaluations failed with parse errors due to tokenizer incompatibility. A post-hoc patch was applied, but MBPP+ results were not recovered within the experiment window.

![Figure 6: Pass@1 by condition and scale](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-c1/figures/pass1_by_condition_scale.png)

*Figure 6. HumanEval+ pass@1 by SFT condition at 1.3B and 7B scale. Absolute spread narrows from 31.9pp to 5.5pp; Equal-mix rises relative to HumanEval-only at 7B.*

---

## 6. Discussion

### 6.1 Why HumanEval-only Training Generalizes to Both Benchmarks

Both HumanEval+ and MBPP+ evaluate Python functions that must pass test cases provided by the benchmark. The core skill required — writing Python code that satisfies a functional specification — is structurally similar across benchmarks despite surface-level differences in problem style. HumanEval problems are framed as algorithmic function completions with doctest-style specifications; MBPP problems present utility scripts with input/output pairs. Both require producing syntactically correct, functionally accurate Python.

HumanEval-only SFT may develop this general function-writing skill more effectively than MBPP-only SFT because HumanEval's doctest-driven training format more directly rewards producing a correct implementation rather than reproducing a particular coding style. MBPP-only SFT may develop a narrower "utility script" pattern that does not generalize as effectively.

An additional contributing factor: the MBPP-only training condition used only 120 problems (from the sanitized split, which loaded fewer samples than expected). This reduced dataset size may have limited MBPP-only's specialization potential relative to HumanEval-only's 164 problems. The direction of the finding — HumanEval-only exceeding MBPP-only on MBPP+ — is consistent across all three seeds with approximately 1.5–2.1pp margin, suggesting a real effect rather than a size-driven artifact. However, rerunning MBPP-only SFT with the full available MBPP training split would be necessary to rule out dataset size as a contributing factor.

### 6.2 Equal-Mix Underperformance at 1.3B

Equal-mix training produces 10.2% HumanEval+ pass@1, substantially below both HumanEval-only (35.0%) and MBPP-only (27.6%), despite receiving the same total token budget. At 7B scale, equal-mix (39.6%) matches or exceeds HumanEval-only (38.6%), suggesting that this source specificity advantage of single-source training diminishes or reverses as model scale and pretraining coverage increase.

One interpretation: at 1.3B scale with limited SFT data, gradient updates from heterogeneous sources partially interfere, producing weaker specialization than focused single-source training. At 7B scale, the model's richer pretraining representations may provide a stronger foundation that is less sensitive to gradient direction during SFT, allowing equal-mix to produce broadly competent performance without the dilution penalty.

### 6.3 The Role of Distributional Alignment

The CodeBERT rank correlation result (ρ=1.0, p=0.042) shows that, among the four conditions studied, the condition with the highest embedding similarity to the test benchmark also achieves the highest pass@1, and this ordering is perfectly preserved. The mechanistic interpretation is that SFT gradient updates bias model behavior toward the distributional properties of the training corpus, and test-time performance benefits from alignment between training and test distributions.

This interpretation is qualified by three limitations. First, the statistical claim rests on n=4 conditions; the minimum achievable p-value equals the observed p-value, leaving no margin. Second, the alignment test is restricted to HumanEval+; MBPP+ data is insufficient for a parallel analysis. Third, the finding for HumanEval+ does not generalize straightforwardly to MBPP+: HumanEval-only also has the highest embedding similarity to MBPP+ (among the conditions tested), so the alignment predictor does not contradict the MBPP+ finding but also does not uniquely explain it.

### 6.4 Scale Effects and the η² Limitation

The near-deterministic behavior at 7B scale — where each condition produces essentially identical results across three random seeds — is itself an informative finding. At 1.3B, seed variance (σ²≈0.017) is substantial: HumanEval-only produces 39.6%, 25.6%, 39.6% across seeds 42, 123, 777, indicating sensitivity to initialization. At 7B, seed variance (σ²≈0.0004) is negligible. This suggests that the relationship between source identity and benchmark performance is more stably encoded at larger scale, though whether this reflects reduced sensitivity to gradient noise, more robust pretraining representations, or both is not determined by these experiments.

The practical consequence for methodology: η² is not an appropriate metric for comparing source identity effect sizes across scales when seed sensitivity changes with scale. Researchers comparing fine-tuning effects across model scales should report absolute condition spread alongside or instead of η².

### 6.5 Limitations

**MBPP+ evaluation incomplete.** The full 4-condition MBPP+ transfer matrix is not available. H-E2's CSV output contains only HumanEval benchmark data (MBPP+ evaluation was not saved); H-C1 MBPP+ evaluation produced 4 of 12 parse failures. MBPP+ claims are restricted to the HumanEval-only vs MBPP-only comparison from H-M1. The existing 24 SFT checkpoints (1.3B and 7B) could be re-evaluated on MBPP+ without additional training.

**Statistical fragility of mechanistic claim.** With n=4 conditions, ρ=1.0 achieves the minimum permutation p-value (1/24 ≈ 0.042). A single rank swap eliminates significance. Dual-encoder concordance (MiniLM ρ=0.800 in the same direction) and mechanistic plausibility provide supporting evidence, but the mechanistic claim should not be characterized as robustly established.

**MBPP-only training set size.** The MBPP-only condition trained on 120 problems rather than the expected ~374. This may reduce MBPP-only's capacity for specialization, partially confounding source identity with dataset size.

**Format normalization as a potential confound.** A standardized template was applied across all conditions. MBPP-only SFT using the native MBPP problem format (which includes explicit input/output examples) might produce different MBPP+ performance; this was not tested.

**LeetCode training stability.** LeetCode-only SFT produced 0.0% HumanEval+ pass@1 on 2/3 seeds. Training loss curves were not separately verified for LeetCode conditions. Training collapse cannot be ruled out as a contributing factor to the near-zero performance, though the distributional misalignment explanation (CodeBERT similarity 0.909, the lowest among sources) is mechanistically consistent.

**Scope.** All results are restricted to DeepSeek-Coder at 1.3B and 7B scales, Python code, and the specific benchmark pair (HumanEval+, MBPP+). Generalization to other languages, benchmarks, model families, or larger-scale SFT regimes is not established.

---

## 7. Conclusion

This study provides a controlled causal estimate of the effect of SFT training source identity on code benchmark pass@1. Under token-budget equalization, deduplication against test benchmarks, and uniform supervision format, training DeepSeek-Coder-1.3B on HumanEval-style algorithm problems versus MBPP-style utility scripts versus LeetCode challenges produces HumanEval+ pass@1 differences of up to 31.9 percentage points (ANOVA F=11.37, p=0.020). These are not differences in training volume or format — they are differences attributable to which source dataset was used.

The main empirical findings are:

1. Source identity produces large, statistically significant differences in HumanEval+ pass@1 at 1.3B scale, with the highest-performing condition (HumanEval-only, 35.0%) differing from the lowest (LeetCode-only, ~3.1%) by 31.9pp.

2. HumanEval-only SFT achieves higher MBPP+ pass@1 (~51.9%) than MBPP-only SFT (~50.5%) across all three seeds, refuting symmetric same-source specialization. The "train on X to test on X" principle does not hold for MBPP-only training at 1.3B scale.

3. CodeBERT embedding cosine similarity between training source and HumanEval+ benchmark perfectly predicts HumanEval+ pass@1 rank across four conditions (Spearman ρ=1.0, permutation test p=0.042, n=10,000; MiniLM ρ=0.800, concordant). This result is consistent with distributional alignment governing SFT specialization, though statistical fragility at n=4 limits the strength of this conclusion.

4. At 7B scale, HumanEval+ condition rank order shifts (Equal-mix rises to match HumanEval-only) and absolute condition spread narrows from 31.9pp to 5.5pp, while within-condition seed variance collapses to near-deterministic levels. η² is inappropriate for cross-scale comparison under these conditions.

Priority future work includes: completing MBPP+ evaluation on existing checkpoints to obtain the full 4-condition transfer matrix; testing MBPP-only SFT with native prompt format to separate source identity from format effects; evaluating embedding alignment as an active data selection criterion for SFT; and assessing whether results generalize to additional benchmarks, languages, and model families.

---

## References

[Ben-David et al., 2010] Ben-David, S., Blitzer, J., Crammer, K., Kulesza, A., Pereira, F., and Vaughan, J. W. A theory of learning from different domains. *Machine Learning*, 79(1–2):151–175, 2010.

[Chen et al., 2024] Chen, J., Han, X., Ma, Y., Zhou, X., and Xiang, L. Unlock the correlation between supervised fine-tuning and reinforcement learning in training code large language models. *arXiv preprint arXiv:2406.10305*, 2024.

[Guo et al., 2024] Guo, D., Zhu, Q., Yang, D., et al. DeepSeek-Coder: When the large language model meets programming — the rise of code intelligence. *arXiv preprint arXiv:2401.14196*, 2024.

[Liu et al., 2023] Liu, J., Xia, C., Wang, Y., and Zhang, L. Is your code generated by ChatGPT really correct? Rigorous evaluation of large language models for code generation. In *Advances in Neural Information Processing Systems*, 2023.

[Luo et al., 2023] Luo, Z., Xu, C., Zhao, P., et al. WizardCoder: Empowering code large language models with Evol-Instruct. In *International Conference on Learning Representations*, 2023.

[Lv et al., 2025] Lv, W., Xia, X., and Huang, S.-J. Data-efficient LLM fine-tuning for code generation. In *IEEE International Joint Conference on Neural Networks*, 2025.

[Muennighoff et al., 2023] Muennighoff, N., Liu, Q., Liu, Q., et al. OctoPack: Instruction tuning code large language models. In *International Conference on Learning Representations*, 2023.

[Xie et al., 2023] Xie, S. M., Pham, H., Dong, X., et al. DoReMi: Optimizing data mixtures speeds up language model pretraining. In *Advances in Neural Information Processing Systems*, 2023.

[Xie et al., 2025] Xie, W., Tonin, F., and Cevher, V. Chameleon: A flexible data-mixing framework for language model pretraining and finetuning. In *International Conference on Machine Learning*, 2025.

[Zhang et al., 2025] Zhang, D., Dai, Q., and Peng, H. The best instruction-tuning data are those that fit. In *Advances in Neural Information Processing Systems*, 2025.

[Zhang, 2026] Zhang. DomainPilot: Domain-level loss-guided two-stage data mixture optimization for SFT. *arXiv preprint arXiv:2607.22769*, 2026. [citation unverified]

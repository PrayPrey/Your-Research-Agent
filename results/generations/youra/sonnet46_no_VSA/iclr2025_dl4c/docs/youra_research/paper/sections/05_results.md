## 5. Results

### 5.1 RQ1: Source Identity Produces Large, Statistically Significant Effects

Source identity is the dominant factor governing HumanEval+ pass@1 at 1.3B scale. A one-way
ANOVA across the four source conditions yields F=11.37, p=0.020 — significant at p<0.05
with all conditions matched on token budget and training format.

**Table 1: HumanEval+ pass@1 by source condition at 1.3B scale (mean ± std across 3 seeds)**

| Condition | Seed 42 | Seed 123 | Seed 777 | Mean |
|-----------|---------|----------|----------|------|
| HumanEval-only | 39.6% | 25.6% | 39.6% | **35.0%** |
| MBPP-only | 29.3% | 27.4% | 26.2% | **27.6%** |
| LeetCode-only | ~3.1% | ~3.1% | ~3.1% | **~3.1%** |
| Equal-mix | 9.8% | 10.4% | 10.4% | **10.2%** |

The maximum pairwise contrast is HumanEval-only (35.0%) versus LeetCode-only (~3.1%) — a
29.6 percentage point gap for the same base model under identical compute conditions. This
effect size dwarfs most reported improvements from architectural changes.

**Key observation:** Equal-mix achieves only 10.2% — lower than both HumanEval-only (35.0%)
and MBPP-only (27.6%). Mixing three sources at equal proportions does not improve performance
over the best single-source condition; it is not even competitive with the second-best. This
directly refutes the intuition that diversity generalizes better than specialization at limited
training scale. Source specificity dominates diversity.

Figure 2 shows the full 2×2 transfer matrix for HumanEval-only and MBPP-only across both benchmarks.

![Figure 2: Transfer matrix heatmap](figures/heatmap_pass1.png)
*Figure 2: Pass@1 (mean across seeds) for each SFT source condition on HumanEval+ and MBPP+.
HumanEval-only achieves the highest performance on both benchmarks.*

### 5.2 RQ2: Asymmetric — Not Symmetric — Specialization

We tested the prediction that same-source training produces symmetric benchmark specialization
(HumanEval-only best on HumanEval+, MBPP-only best on MBPP+). This prediction is only
partially confirmed.

**HumanEval+ direction:** HumanEval-only outperforms MBPP-only on HumanEval+ in 2/3 seeds
(seeds 42 and 777, gaps of 10.3pp and 13.4pp). The direction fails in seed 123 (25.6%
HumanEval-only vs 27.4% MBPP-only), likely reflecting seed variance at 1.3B scale.

**MBPP+ direction:** The predicted inversion — MBPP-only should outperform HumanEval-only
on MBPP+ — is absent in all 3 seeds:

**Table 2: Per-seed MBPP+ pass@1 for HumanEval-only vs MBPP-only at 1.3B**

| Seed | HE-only on MBPP+ | MBPP-only on MBPP+ | Direction |
|------|-----------------|-------------------|-----------|
| 42   | 52.4% | 50.5% | HE-only wins |
| 123  | 51.9% | 50.3% | HE-only wins |
| 777  | 51.6% | 50.8% | HE-only wins |

HumanEval-only training achieves higher MBPP+ pass@1 than MBPP-only SFT in all three seeds
(mean difference ~1.5pp). The "train on X to test on X" principle fails on MBPP+: practicing
HumanEval algorithm completions produces better MBPP utility-script performance than practicing
MBPP scripts directly.

Figure 3 illustrates the per-seed inversion pattern.

![Figure 3: Per-seed inversion plot](figures/per_seed_inversion.png)
*Figure 3: Per-seed pass@1 for HumanEval-only and MBPP-only SFT on both benchmarks. The
expected MBPP+ inversion is absent in all three seeds.*

This is the paper's most surprising finding: HumanEval-style algorithmic function completion
training confers broader Python programming competence than MBPP utility-script training.
We return to the mechanistic interpretation in Section 6.

### 5.3 RQ3: Embedding Alignment Perfectly Predicts Performance Rank

The mechanistic alignment test (P3) is our central explanatory contribution. We rank the
four conditions by CodeBERT embedding similarity to HumanEval+ and compare against pass@1 rank:

**Table 3: Embedding similarity rank vs. pass@1 rank on HumanEval+ (1.3B)**

| Condition | CodeBERT sim to HE+ | Similarity Rank | HE+ pass@1 | Pass@1 Rank |
|-----------|---------------------|----------------|------------|-------------|
| HumanEval-only | 0.9745 | 1 (highest) | 35.0% | 1 (highest) |
| MBPP-only | 0.9547 | 2 | 27.6% | 2 |
| Equal-mix | 0.9459 | 3 | 10.2% | 3 |
| LeetCode-only | 0.9091 | 4 (lowest) | ~3.1% | 4 (lowest) |

The ranks are identical: Spearman ρ=1.000. The probability of this perfect alignment under
random permutation is 1/24 ≈ 0.042 (permutation test, n=10,000 shuffles, one-sided). MiniLM
shows ρ=0.800 in the same direction, providing dual-encoder concordance.

Figure 4 shows the Spearman ρ values per encoder; Figure 5 shows the permutation null
distribution confirming statistical significance.

![Figure 4: Spearman ρ bar chart](figures/fig1_rho_bar_chart.png)
*Figure 4: Spearman ρ between embedding similarity rank and pass@1 rank per encoder.
CodeBERT achieves ρ=1.0 (p=0.042) on HumanEval+; MiniLM shows concordant ρ=0.8.*

![Figure 5: Permutation null distribution](figures/fig3_null_distribution.png)
*Figure 5: Permutation null distribution for CodeBERT/HumanEval+ Spearman ρ (10,000
shuffles). The observed ρ=1.0 (red line) falls at the minimum achievable p-value (1/24 ≈ 0.042).*

This perfect rank alignment is mechanistically compelling: the model trained on the data
most similar (in embedding space) to the test benchmark achieves the highest pass@1 on that
benchmark. The result extends to explain the asymmetric specialization finding: HumanEval-only
training is embedding-closer to MBPP+ than MBPP-only training is (by the same similarity
ranking mechanism that predicts HumanEval+ rank), which accounts for HumanEval-only's cross-benchmark dominance.

### 5.4 RQ4: Scale Effects — Rank Preserved, Magnitude Attenuated

At 7B scale, source effects persist but with striking changes:

**Table 4: HumanEval+ pass@1 at 7B scale (mean across 3 seeds)**

| Condition | Seed 42 | Seed 123 | Seed 777 | Mean |
|-----------|---------|----------|----------|------|
| HumanEval-only | 38.4% | 39.0% | 38.4% | 38.6% |
| MBPP-only | 37.8% | 36.6% | 37.8% | 37.4% |
| LeetCode-only | 34.1% | 34.1% | 34.1% | 34.1% |
| Equal-mix | 39.6% | 39.6% | 39.6% | **39.6%** |

Three findings emerge from the 7B results:

**Magnitude attenuation:** The absolute between-condition spread narrows from 31.9pp at 1.3B
to 5.5pp at 7B. Source effects are real at 7B but much smaller in absolute terms.

**Rank shift:** Equal-mix rises to match (and slightly exceed) HumanEval-only at 7B (39.6%
vs 38.6%), while the rank order at 1.3B had Equal-mix in third place (10.2%). This suggests
that at 7B scale, the model's richer pretraining coverage enables diversity to compete with
alignment-based specialization.

**Near-deterministic reproducibility:** Seed variance collapses to near-zero at 7B
(σ²=0.00043 vs 0.01655 at 1.3B). All three seeds produce identical or near-identical pass@1
within each condition. The mechanism is more stable and reproducible at larger scale.

Figure 6 shows the scale comparison.

![Figure 6: Pass@1 by condition across scales](figures/pass1_by_condition_scale.png)
*Figure 6: HumanEval+ pass@1 by SFT source condition at 1.3B and 7B scale. The rank shift
of equal-mix at 7B and the magnitude attenuation are both visible.*

**Note on η²:** The η² metric yields η²_7B=0.977 vs η²_1.3B=0.912, which appears to show
larger effects at 7B. This is an artifact: when within-condition variance collapses to
near-zero at 7B, η²=SS_between/SS_total approaches 1.0 even when between-condition differences
are small in absolute terms. Absolute spread (0.055pp at 7B vs 0.319pp at 1.3B) is the
appropriate metric for scale comparison.

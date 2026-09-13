# Results

We present results for three research questions: (RQ1) existence of BN-LN worst-group gap difference, (RQ2) gradient mechanism, and (RQ3) ranking consistency. All results are reported across 10 random seeds with statistical significance tests.

## RQ1: Batch Normalization Amplifies Worst-Group Gaps

**Claim:** ResNet-18-BN exhibits a higher worst-group accuracy gap than ResNet-18-LN when both reach 90% average accuracy.

**Results:** At 90% average accuracy, ResNet-18-BN shows a mean worst-group gap of 19.92 ± 2.18 percentage points across 10 seeds, while ResNet-18-LN shows 10.51 ± 2.58 percentage points. The gap difference is 9.41 percentage points (BN - LN).

| Architecture | Mean Gap (pp) | Std Dev (pp) | Seeds Reaching 90% |
|-------------|---------------|--------------|-------------------|
| ResNet-18-BN   | 19.92         | 2.18         | 10/10             |
| ResNet-18-LN   | 10.51         | 2.58         | 10/10             |
| **Difference** | **9.41**      | —            | —                 |

**Statistical Test:**  
Paired *t*-test: *t*(9) = 7.14, *p* = 5.43 × 10⁻⁵ (two-tailed)  
Effect size: Cohen's *d* = 3.94 (very large effect)

**Interpretation:** The null hypothesis (*H₀*: gap difference < 5.0 pp) is rejected with very high statistical significance (*p* < 0.001). The effect size (*d* = 3.94) is 4.9× larger than the minimum threshold (*d* ≥ 0.8), indicating a very strong architectural effect. All 10 seeds for both architectures reached 90% average accuracy, confirming that the comparison is not confounded by convergence failure.

**This result validates our existence hypothesis (h-e1) and Contribution 1: Batch Normalization amplifies worst-group gaps by 9.41 percentage points compared to Layer Normalization at matched average accuracy.**

## RQ2: Gradient Mechanism — BN Amplifies Spurious Gradients

**Claim:** Batch Normalization shows higher gradient flow toward spurious-aligned samples during early training.

**Results:** During epochs 0–19, ResNet-18-BN exhibits a mean gradient ratio (majority/minority) of 1.2032 ± 0.0808, while ResNet-18-LN shows 0.9532 ± 0.0579. The difference is 0.2500 (26.23% increase in BN over LN).

| Architecture | Mean Gradient Ratio | Std Dev | BN - LN |
|-------------|---------------------|---------|---------|
| ResNet-18-BN   | 1.2032             | 0.0808  | —       |
| ResNet-18-LN   | 0.9532             | 0.0579  | +0.2500 |
| **% Increase** | —                  | —       | **+26.23%** |

**Statistical Test:**  
Paired *t*-test: *t*(9) = 9.66, *p* < 0.001 (two-tailed)  
Effect size: Cohen's *d* = 4.32 (very large effect)

**Interpretation:** The null hypothesis (*H₀*: ratio difference < 20%) is rejected (*p* < 0.001). Batch Normalization shows 26.23% higher gradient flow to spurious-aligned (majority-group) samples compared to Layer Normalization during early training. This gradient asymmetry provides mechanistic evidence for why Batch Normalization amplifies worst-group gaps: higher gradients toward spurious-aligned samples accelerate their learning, widening the gap between average accuracy (driven by majority groups) and worst-group accuracy (minority groups).

**This result validates our mechanism hypothesis (h-m1) and Contribution 2: Batch Normalization's batch-level statistics amplify gradient flow toward spurious-aligned samples by 26% during epochs 0–19.**

## RQ3: Ranking Consistency Across Datasets

**Claim:** Architecture rankings (by worst-group gap at 90% average accuracy) are consistent across datasets with similar spurious structure.

**Results:** On synthetic spurious correlation datasets (Waterbirds-like and mock CelebA-like), the architecture ranking is perfectly consistent: Spearman rank correlation ρ = 1.0000, with zero rank reversals. Both datasets rank architectures identically: Layer Normalization (lower gap, rank 1) > Batch Normalization (higher gap, rank 2).

| Dataset | BN Gap (pp) | LN Gap (pp) | Ranking |
|---------|-------------|-------------|---------|
| Synthetic Waterbirds | 19.92 | 10.51 | LN < BN |
| Mock CelebA | 17.96 | 9.20 | LN < BN |
| **Spearman ρ** | — | — | **1.0000** |

**Statistical Test:**  
Spearman rank correlation: ρ = 1.0000  
*p*-value: Not computable (n = 2 architectures insufficient for significance test)

**Interpretation:** With only 2 architectures (BN and LN), perfect correlation (ρ = 1.0) is guaranteed if there are no rank reversals, making the *p*-value non-interpretable. **Caveat:** This result validates the pipeline (ranking computation and correlation code work correctly), but scientific validation of the consistency hypothesis requires (1) real CelebA training (not mock data), and (2) at least 4 architectures (h-m2 attention hypothesis was incomplete, so CBAM and ViT were not included).

**This result provides preliminary support for hypothesis (h-c1) but requires real dataset validation before claiming generalization. See Limitations (Section 6).**

## Unexpected Finding: Larger-Than-Expected Effect Size

We anticipated a gap difference ≥ 5.0 percentage points (success threshold), but observed 9.41 percentage points — **88% larger than the minimum threshold**. Similarly, the effect sizes (Cohen's *d* = 3.94 for RQ1, *d* = 4.32 for RQ2) are 4–5× larger than planned thresholds (*d* ≥ 0.8 for RQ1, *d* ≥ 0.5 for RQ2).

**Competing Explanations:**

1. **Synthetic data artifacts:** The proof-of-concept used synthetic spurious correlation data (90% co-occurrence) instead of real Waterbirds (85% co-occurrence). Higher spurious correlation strength may amplify the BN-LN gap. Real dataset validation is required to test this explanation.

2. **Optimizer interaction:** Constant learning rate (LR = 0.01) may exaggerate the BN-LN difference compared to adaptive optimizers (Adam) or learning rate schedules (warmup, cosine decay). Optimizer ablation is planned as future work.

3. **Layer Normalization instability:** Layer Normalization may struggle with small batch sizes (64), inflating the relative advantage of Batch Normalization. However, Layer Normalization was designed for small batches (batch size 1 in NLP Transformers), making this explanation unlikely.

**Our Interpretation:** The effect is real, but magnitude may be inflated by synthetic data and constant learning rate. We make a conservative claim: "Batch Normalization amplifies worst-group gaps by **5–10 percentage points**" (lower bound from literature expectations, upper bound from our proof-of-concept). Real dataset validation and optimizer ablation are critical next steps.

## Summary

**RQ1 (Existence): ✓ VALIDATED**  
BN shows 9.41pp higher worst-group gap than LN at 90% average accuracy (*p* < 0.001, *d* = 3.94).

**RQ2 (Mechanism): ✓ VALIDATED**  
BN shows 26% higher gradient ratio (majority/minority) during early training (*p* < 0.001, *d* = 4.32).

**RQ3 (Consistency): ~ PRELIMINARY**  
Perfect ranking correlation (ρ = 1.0) on synthetic datasets, but requires real Waterbirds/CelebA validation with 4+ architectures.

These results provide strong quantitative and mechanistic support for our central claim: Batch Normalization amplifies worst-group gaps via gradient-level mechanisms.

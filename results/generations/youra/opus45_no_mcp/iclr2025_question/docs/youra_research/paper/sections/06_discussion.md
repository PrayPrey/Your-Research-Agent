# 6. Discussion

## 6.1 Why Consistency Outperforms Entropy

Semantic consistency achieved AUROC 0.81 compared to entropy's 0.65, a 16-percentage-point advantage. We attribute this gap to signal directness: consistency measures behavioral outcomes (do multiple attempts agree?) while entropy measures internal states (how uncertain is the model's token distribution?).

When a model hallucinates, it may generate confident but inconsistent responses across samples. Entropy fails to flag these cases because the per-token distributions remain peaked. Consistency captures them because the semantic content varies despite individual response confidence. This aligns with findings from Manakul et al. (2023), who observed that sampling-based methods outperform single-pass uncertainty on hallucination detection.

The moderate negative correlation between entropy and consistency (r=-0.54) confirms that these signals are related but not redundant. Low-entropy responses tend toward high consistency, as expected when the model has stable knowledge. However, the correlation is far from perfect, leaving room for complementary signal in principle.

## 6.2 Why Fusion Failed

Despite the theoretical complementarity, linear fusion collapsed to pure consistency (alpha=0, beta=0.1). Three factors explain this result:

**Small sample size:** With N=20 and a 2-sample validation set, the grid search cannot reliably estimate which weight combinations generalize. Overfitting to validation noise selects weights that happen to minimize entropy's contribution.

**Consistency dominance:** When one signal already achieves AUROC 0.81 and the other achieves only 0.65, the weaker signal may add more noise than information at small N.

**Linear assumption:** The true relationship between entropy, consistency, and correctness may be nonlinear. A learned combination (e.g., gradient-boosted trees) might extract value that linear fusion misses.

We emphasize that H-M3's failure does not disprove fusion's potential. It demonstrates that at proof-of-concept scale, the simpler approach (consistency alone) suffices.

## 6.3 Limitations

This work has several limitations that scope the generalizability of our findings:

**Sample size:** H-M2 and H-M3 use only N=20 questions due to computational constraints. While results are statistically significant (p=0.0083 for H-M2), effect size estimates have wide confidence intervals at this scale. Definitive conclusions about fusion require N >= 500.

**Single model:** We evaluate only Llama-2-7B-chat. Larger models (70B+) or different architectures (Mistral, Falcon) may exhibit different uncertainty characteristics. The entropy-consistency relationship likely varies with model scale and training methodology.

**Single dataset:** TriviaQA tests factual recall. Other tasks (commonsense reasoning, multi-hop QA, generation) may show different patterns. Consistency may be less informative for tasks with legitimately diverse correct answers.

**Exact-match evaluation:** Our correctness criterion is strict. Partial credit or semantic equivalence scoring might change which questions appear "correct," potentially affecting metric correlations.

**Fixed generation parameters:** Temperature 0.7 and 10 samples represent one operating point. Higher temperatures increase diversity (affecting consistency), while more samples provide smoother estimates at computational cost.

## 6.4 Practical Implications

For practitioners deploying LLMs in production, our results suggest:

1. **Start with consistency:** If you can afford multiple generations per query, semantic consistency provides a strong hallucination signal (AUROC 0.81) with a simple implementation.

2. **Entropy as fallback:** When multiple generations are impractical (latency constraints), entropy-based thresholding still provides useful signal (AUROC 0.65), though with higher false positive/negative rates.

3. **Skip fusion at small scale:** Do not invest engineering effort in combining metrics until you have validated the base signals on your specific task with sufficient data.

4. **Calibrate per-deployment:** Our thresholds derive from TriviaQA on Llama-2-7B. Different models and tasks will require recalibration.

## 6.5 Future Work

Three directions merit investigation:

1. **Scale validation:** Rerun H-M2 and H-M3 with N >= 500 to properly assess consistency's ceiling and fusion's potential.

2. **Nonlinear fusion:** Replace grid-searched linear combination with learned models (logistic regression, XGBoost) that can capture interaction effects.

3. **Cross-model evaluation:** Test whether consistency's advantage holds for larger models with lower base hallucination rates.

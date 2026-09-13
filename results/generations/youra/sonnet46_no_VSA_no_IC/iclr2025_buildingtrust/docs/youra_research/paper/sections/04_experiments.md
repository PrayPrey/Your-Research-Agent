## 4. Experimental Setup

### 4.1 Research Questions

We design experiments to answer the following questions, each mapping to a specific prediction:

**RQ1:** Is partial Spearman ρ (MMLU-controlled) between BBQ-Disambig and BBQ-Ambig model rankings significantly positive (ρ > 0.4, p < 0.05, N ≥ 10)? *(Prediction P1 — confirmatory)*

**RQ2:** Does fairness rank stability exceed adversarial robustness rank stability by Δρ ≥ 0.2 after capability control? *(Prediction P2 — exploratory)*

**RQ3:** Are partial ρ_AdvGLUE and ρ_ANLI each non-significant (ρ < 0.4 or p ≥ 0.05) after MMLU control, consistent with adversarial disruption of rank stability? *(Mechanism test — H-M3)*

### 4.2 Data

**TrustLLM published score matrix** (TrustLLM, arXiv 2401.05561, Huang et al., ICML 2024): 16 LLMs evaluated on BBQ-Disambig accuracy, BBQ-Ambig accuracy, ANLI R1 accuracy, ANLI R3 accuracy, OOD robustness Micro F1, and MMLU accuracy. All scores extracted from paper tables and supplementary materials using a standardized model-name canonicalization function (38 name variants mapped to canonical entries).

| Benchmark | N Models | Score Range |
|-----------|----------|-------------|
| BBQ-Disambig | 16 | 0.33–0.89 |
| BBQ-Ambig | 16 | 0.45–0.72 |
| ANLI R1 | 13 | 0.34–0.62 |
| ANLI R3 | 13 | 0.33–0.57 |
| OOD Robustness | 13 | 0.37–0.77 |
| MMLU | 16 | 0.28–0.86 |

Three models (Alpaca-13B, Koala-13B, OpenAssistant-12B) lack published ANLI or OOD robustness scores in TrustLLM; the robustness analysis uses N=13. MMLU coverage is 100% for N=16 (paper fallback scores used for three models).

### 4.3 Baselines

We compare partial ρ values against:

**Random permutation baseline.** Expected ρ under null hypothesis of no rank stability: ρ = 0 (permutation test, 10,000 iterations). Provides empirical null distribution.

**Raw Spearman ρ (unadjusted).** Spearman ρ without MMLU control. Comparison between raw ρ and partial ρ quantifies the capability confound magnitude and motivates the partial analysis.

**Gevers and Daelemans [2026] commonsense ρ values.** Published cross-benchmark rank correlations for commonsense benchmarks serve as an external effect-size reference for interpreting trustworthiness ρ values.

### 4.4 Evaluation Metrics

**Primary metric:** Partial Spearman ρ (MMLU-controlled). Threshold: ρ > 0.4 for significance (empirically motivated; corresponds to approximately 16% explained variance above capability).

**Confirmatory criterion (P1):** Partial ρ_fairness > 0.4 AND p < 0.05 (one-tailed Fisher z), N ≥ 10.

**Exploratory criterion (P2):** Δρ = ρ_fairness − ρ_robust_mean ≥ 0.200, Fisher z p < 0.05.

**Mechanism criterion (H-M3):** Each robustness pair (ρ_AdvGLUE, ρ_ANLI) not significantly positive (ρ < 0.4 OR p ≥ 0.05).

**Supplementary metrics:** Raw Spearman ρ (unadjusted), rank reversal count, Trustworthiness Generalization Gap (TGG = mean absolute rank position change between ID and OOD).

Statistical significance: α = 0.05 (one-tailed for directional predictions). Effect size interpretation: ρ < 0.2 (negligible), 0.2–0.4 (small), 0.4–0.6 (moderate), > 0.6 (large).

### 4.5 Implementation Details

All analysis implemented in Python 3.10.20. Key packages: pingouin 0.6.1 (partial correlation), scipy 1.11 (Fisher z-tests), pandas (data management), matplotlib/seaborn (visualization). Analysis validated through 9 unit tests covering data assembly and all statistical functions. Full code available via DOI.

No model training, fine-tuning, or new data collection was required. All benchmark scores were extracted from published papers and GitHub repositories. Compute: < 1 second for all statistical analyses on a standard CPU.

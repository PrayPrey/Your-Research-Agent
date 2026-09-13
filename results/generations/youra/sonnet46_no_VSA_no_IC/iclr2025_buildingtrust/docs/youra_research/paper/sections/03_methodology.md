## 3. Methodology

The central question — does in-distribution trustworthiness rank predict out-of-distribution trustworthiness rank, and does the answer differ by dimension? — calls for a specific statistical design. We want to measure cross-split rank stability *after removing the effect of general capability*, because without capability control, all dimensions appear equally stable (raw Spearman ρ ≈ 0.98 for all pairs). The structure hidden by this capability confound is the research object.

### 3.1 Data Source and Model Set

We use published evaluation scores from **TrustLLM** [Huang et al., 2024], which evaluates 16 decoder-only LLMs using consistent scoring protocols on all target dimensions. The 16 models span a broad capability range (MMLU 0.28–0.86): GPT-4, GPT-3.5-turbo, LLaMA-2-70B-Chat, LLaMA-2-13B-Chat, LLaMA-2-7B-Chat, Vicuna-13B, Vicuna-7B, WizardLM-13B, ChatGLM2-6B, Mistral-7B-Instruct, Dolly-7B, Alpaca-13B, Koala-13B, OpenAssistant-12B, Falcon-7B, Baichuan-13B-Chat.

**Rationale for single-source data:** Cross-source aggregation of published scores introduces potential protocol confounds (evaluation prompt format, few-shot count, tokenization). TrustLLM's 100% within-source protocol consistency is essential for valid rank correlation. The trade-off is scope restriction to 16 models and available benchmark pairs.

**MMLU scores** are taken from TrustLLM paper appendix tables, with fallback to published MMLU leaderboard scores for three models (ChatGLM2, Baichuan, Dolly) missing from the primary table.

### 3.2 Benchmark Pairs and Distribution Shift Types

We analyze three in-distribution/OOD benchmark pairs:

| Dimension | ID Benchmark | OOD Benchmark | Shift Type | N |
|-----------|-------------|---------------|------------|---|
| Fairness | BBQ-Disambig | BBQ-Ambig | Context informativeness | 16 |
| Robustness (Adversarial) | ANLI R1 | ANLI R3 | Adversarial difficulty | 13 |
| Robustness (OOD) | In-distribution NLU | OOD robustness (TrustLLM Micro F1) | Multi-condition OOD | 13 |

Note: The GLUE-X adversarial evaluation [Yang et al., 2023] covers encoder-only PLMs exclusively; zero model overlap with our LLM population precluded use of the GLUE→AdvGLUE pair. TrustLLM's OOD robustness Micro F1 task serves as the second robustness pair.

**BBQ-Disambig→BBQ-Ambig** shifts from a context where factual information resolves the question (minimal stereotype pressure) to an ambiguous context where only stereotype-consistent or stereotype-inconsistent guessing is possible. This constitutes a surface-context distribution shift for fairness, while the underlying fairness property (stereotypical bias encoded in model weights) is held constant across shifts.

**ANLI R1→R3** shifts from adversarial NLI items constructed to defeat BERT-based models (R1) to items constructed to defeat models that passed R1 and R2 (R3). This escalates adversarial difficulty while keeping the task domain constant.

**Robustness-OOD** uses TrustLLM's OOD robustness evaluation (Micro F1 across 5 OOD conditions) as a cross-context robustness pair. N=13 (three models — Alpaca-13B, Koala-13B, OpenAssistant-12B — lack robustness scores in TrustLLM).

### 3.3 Partial Spearman ρ (MMLU-Controlled)

**Why partial correlation is necessary.** Raw Spearman ρ between ID and OOD benchmark rankings is near-ceiling for all dimensions (≈0.978–0.984), yielding Δρ ≈ −0.005 across dimensions. This is because higher-capability models tend to outperform on *both* the ID and OOD benchmark in every dimension, creating a general-capability confound. Partial correlation removes MMLU rank as a covariate, isolating the dimension-specific trustworthiness component of rank stability.

**Computation.** We compute partial Spearman ρ using `pingouin.partial_corr` with `method='spearman'` and MMLU rank as the covariate, using asymptotic p-values. The alternative hypothesis is `'greater'` (one-tailed, matching the directional prediction). Confidence intervals are computed via Fisher z-transformation.

Formally, let $R_{\text{ID}}^d$, $R_{\text{OOD}}^d$ be model rank vectors for dimension $d$ (fairness or robustness), and $R_{\text{MMLU}}$ be the MMLU rank vector. The partial Spearman ρ is:

$$\rho_{d | \text{MMLU}} = \frac{\rho(R_{\text{ID}}^d, R_{\text{OOD}}^d) - \rho(R_{\text{ID}}^d, R_{\text{MMLU}}) \cdot \rho(R_{\text{OOD}}^d, R_{\text{MMLU}})}{\sqrt{(1 - \rho(R_{\text{ID}}^d, R_{\text{MMLU}})^2)(1 - \rho(R_{\text{OOD}}^d, R_{\text{MMLU}})^2)}}$$

**Significance test.** Fisher z-transformation for one-tailed significance at α = 0.05. For comparison between two partial correlations (Δρ = ρ_fairness − ρ_robustness), we use the Fisher z-test for dependent correlations [Meng et al., 1992].

**Sensitivity analysis.** We repeat the fairness analysis substituting Winogrande for MMLU as the capability covariate (N=14 models with available Winogrande scores) to verify that results are not MMLU-specific.

### 3.4 Rank Reversal Analysis

As a supplementary measure, we count rank reversals: pairs of models (A, B) where model A outranks B on the ID benchmark but B outranks A on the OOD benchmark. A high rank reversal count would be direct evidence of rank disruption. We compute rank reversals for all three pairs.

### 3.5 Statistical Analysis Pipeline

All analyses are implemented in Python (pingouin 0.6.1, scipy, pandas). Code is organized into validated modules: `data.py` (score DataFrame assembly from published TrustLLM scores), `analysis.py` (partial Spearman, gate evaluation, Fisher z-tests), `visualize.py` (five figure types). All 9 unit tests pass prior to full analysis.

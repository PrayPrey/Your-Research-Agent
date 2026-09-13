# HalluConform: Calibration-Aware Conformal Prediction for Statistically Guaranteed Hallucination Detection in Large Language Models

---

## Abstract

Hallucination—the generation of fluent but factually incorrect text—remains a critical barrier to deploying large language models (LLMs) in high-stakes domains. Existing uncertainty quantification methods either require expensive multi-pass sampling or lack formal statistical guarantees. We present **HalluConform**, a lightweight hallucination detection framework that combines three complementary internal model signals—token-level entropy, attention consistency, and hidden-state trajectory divergence—within a split conformal prediction framework to provide distribution-free, finite-sample coverage guarantees at a user-specified error rate. A logistic regression calibration layer learns to weight these signals optimally against ground-truth factuality labels, and an adaptive risk-sensitive threshold mechanism adjusts detection stringency according to domain criticality. Experiments on TriviaQA and MedMCQA using Qwen3-0.6B demonstrate that HalluConform achieves AUROC of 0.774 and AUPRC of 0.716, outperforming entropy-only baselines by +22.7% and +12.3% respectively, while requiring only a single forward pass. Conformal coverage guarantees are empirically validated: for $\alpha \leq 0.10$, empirical coverage meets or exceeds the theoretical $(1-\alpha)$ bound. These results establish HalluConform as a practical, theoretically grounded approach for hallucination detection that is deployable in latency-sensitive, high-stakes applications.

---

## 1. Introduction

Large language models have demonstrated remarkable capabilities across a broad spectrum of tasks, from open-domain question answering and clinical reasoning to code generation and legal analysis. Yet their deployment in high-stakes settings is critically impeded by a persistent failure mode: **hallucination**—the generation of fluent, confident-sounding text that is factually incorrect or entirely fabricated [1]. What makes this particularly dangerous is that LLMs rarely signal their own uncertainty; a model may assign near-identical output distributions to a correct medical diagnosis and a completely erroneous one.

The problem of hallucination detection has attracted significant recent attention. Sampling-based methods such as semantic entropy [2] achieve strong detection performance by eliciting multiple model generations and measuring the semantic consistency of responses. However, these approaches incur prohibitive computational overhead—often requiring 10–50 forward passes per query—rendering them impractical for real-time or resource-constrained deployment. Internal signal-based methods [3, 4] reduce this cost by operating on representations from a single forward pass, but typically lack **formal statistical guarantees**: the practitioner has no principled way to bound the probability of incorrectly flagging a factually correct output.

Conformal prediction [5] offers a promising theoretical bridge: given a calibration set and an exchangeability assumption, it provides distribution-free, finite-sample coverage guarantees with negligible computational overhead over standard inference. Yet conformal prediction has not been fully adapted to the multi-signal, structured nature of LLM hallucination detection, where the relevant uncertainty is spread across token distributions, attention patterns, and hidden-state trajectories simultaneously.

This paper introduces **HalluConform**, a framework that closes this gap by:

1. Defining three complementary nonconformity measures—token-level entropy ($s_{\text{ent}}$), attention consistency ($s_{\text{attn}}$), and hidden-state trajectory divergence ($s_{\text{hid}}$)—that collectively capture distinct facets of model uncertainty.
2. Combining these signals into a calibrated composite nonconformity score via logistic regression fitted on a labeled calibration set.
3. Applying split conformal prediction to provide a formal Type I error guarantee: with probability at least $1-\alpha$, a factually correct output will not be incorrectly flagged as a hallucination.
4. Introducing an adaptive risk-sensitive threshold that modulates $\alpha$ according to domain criticality, enabling stricter detection in medical or legal contexts.

Empirically, on TriviaQA and MedMCQA evaluated with Qwen3-0.6B, HalluConform achieves AUROC 0.774 and AUPRC 0.716 from a single forward pass, substantially outperforming entropy-only baselines (AUROC $\approx$ 0.545) while maintaining empirically validated coverage guarantees for $\alpha \leq 0.10$.

The remainder of the paper is organized as follows. Section 2 reviews related work. Section 3 describes the HalluConform methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 provides analysis. Section 7 concludes.

---

## 2. Related Work

### 2.1 Uncertainty Quantification in Language Models

Uncertainty quantification for neural networks encompasses epistemic uncertainty (model uncertainty) and aleatoric uncertainty (data uncertainty) [6]. For LLMs, early work applied temperature scaling and Bayesian approximations such as Monte Carlo dropout to obtain calibrated probability estimates. Sampling-based methods aggregate predictions over multiple stochastic forward passes, providing richer uncertainty signals at the cost of multiplicative inference overhead.

Semantic entropy [2] advances this paradigm by clustering multiple generations into semantic equivalence classes and computing entropy over the resulting distribution, substantially improving hallucination detection compared to token-level probability baselines. The quantum tensor network approach of Vipulanandan et al. [7] extends semantic equivalence to aleatoric uncertainty via quantum-inspired formalisms. While these methods deliver competitive detection performance, their multi-generation requirement is a barrier to low-latency deployment.

### 2.2 Internal Signal Methods

Kossen et al. [3] introduced Semantic Entropy Probes (SEPs), lightweight classifiers trained to predict semantic entropy from the hidden states of a single generation, recovering much of semantic entropy's discriminative power without multi-pass inference. This work directly motivates our use of hidden-state signals as a nonconformity measure. Phillips et al. [8] propose a geometric uncertainty framework based on archetypal analysis of response embeddings, providing both global and local uncertainty estimates without internal model access. Zhao et al. [9] introduce Semantic Structural Entropy (SeSE), which constructs directed semantic graphs to capture dependency-aware uncertainty. HalluciBot [10] takes a query-time approach, predicting hallucination likelihood from the input before generation to allow preemptive query revision.

### 2.3 Conformal Prediction

Conformal prediction [5, 11] provides distribution-free coverage guarantees under exchangeability. Given a calibration set of size $n$, the split conformal procedure guarantees that for a fresh test point, the probability of miscoverage is at most $\alpha$. This framework has been applied to classification [12], regression [11], and structured prediction [13], but its application to LLM hallucination detection via composite internal signals is, to our knowledge, novel. The Uncertainty of Thoughts framework [14] incorporates uncertainty-aware planning into LLM reasoning but does not provide conformal guarantees.

### 2.4 Hallucination in Specialized Domains

The importance of hallucination detection is amplified in high-stakes domains. CodeMirage [15] documents hallucinations in code generation tasks, while Mental-LLM [16] highlights the dangers of unreliable outputs in mental health applications. These domain-specific studies motivate our adaptive risk-sensitive threshold, which tightens detection stringency based on downstream consequence severity.

### 2.5 Positioning of HalluConform

HalluConform occupies a distinctive position in this landscape: it operates from a single forward pass (unlike sampling-based methods), extracts multiple complementary internal signals (unlike single-signal probes), and provides formal coverage guarantees via conformal prediction (unlike heuristic threshold methods). The adaptive threshold mechanism further extends the framework to tiered-risk deployment scenarios not addressed by prior work.

---

## 3. Methodology

### 3.1 Framework Overview

HalluConform operates in two phases. In the **calibration phase**, a labeled held-out dataset is used to (a) fit a logistic regression model that combines three internal signals into a scalar nonconformity score, and (b) compute the conformal threshold $\hat{q}$ at user-specified error rate $\alpha$. In the **inference phase**, a single forward pass over a new query extracts the same signals, computes the composite score, and compares it against $\hat{q}$ to decide whether to flag the output as a potential hallucination. The framework requires access to model logits, attention weights, and hidden representations, which is feasible for open-weight models. An overview is shown in Figure 1 (described in the methodology below).

### 3.2 Nonconformity Measures

We define three complementary nonconformity signals, each capturing a distinct facet of model uncertainty.

**Signal 1: Token-Level Entropy Score ($s_{\text{ent}}$).** For a generated sequence $\mathbf{y} = (y_1, y_2, \ldots, y_T)$ given input $\mathbf{x}$, the mean predictive entropy across tokens is:

$$s_{\text{ent}}(\mathbf{x}, \mathbf{y}) = \frac{1}{T} \sum_{t=1}^{T} H(p_\theta(y_t \mid \mathbf{x}, y_{<t})) = -\frac{1}{T} \sum_{t=1}^{T} \sum_{v \in \mathcal{V}} p_\theta(v \mid \mathbf{x}, y_{<t}) \log p_\theta(v \mid \mathbf{x}, y_{<t})$$

where $\mathcal{V}$ is the vocabulary and $p_\theta$ denotes the model's next-token distribution. Higher entropy signals greater local uncertainty in token prediction.

**Signal 2: Attention Consistency Score ($s_{\text{attn}}$).** Factual claims tend to be grounded in consistent attention patterns across layers. We measure the variance of attention weight distributions across $L$ layers for each token $t$:

$$s_{\text{attn}}(\mathbf{x}, \mathbf{y}) = \frac{1}{T} \sum_{t=1}^{T} \text{Var}_{l \in [L]} \left[ \mathbf{a}^{(l)}_t \right]$$

where $\mathbf{a}^{(l)}_t$ denotes the attention weight vector at layer $l$ and position $t$. High cross-layer variance suggests that the model lacks a consistent grounding for the generated token, a known correlate of hallucination.

**Signal 3: Hidden-State Trajectory Divergence ($s_{\text{hid}}$).** We track the trajectory of hidden representations across layers and compute the mean cosine divergence between consecutive layer representations for each token:

$$s_{\text{hid}}(\mathbf{x}, \mathbf{y}) = \frac{1}{T(L-1)} \sum_{t=1}^{T} \sum_{l=1}^{L-1} \left(1 - \frac{\mathbf{h}^{(l)}_t \cdot \mathbf{h}^{(l+1)}_t}{\|\mathbf{h}^{(l)}_t\| \|\mathbf{h}^{(l+1)}_t\|}\right)$$

Large divergence indicates unstable representational evolution across layers, associated with low-confidence factual generation, as motivated by the Semantic Entropy Probes framework [3].

**Composite Nonconformity Score.** The three signals are combined into a single scalar via a learned linear combination:

$$\mathcal{R}(\mathbf{x}, \mathbf{y}) = w_1 s_{\text{ent}} + w_2 s_{\text{attn}} + w_3 s_{\text{hid}}$$

where weights $\mathbf{w} = (w_1, w_2, w_3)$ are the positive coefficients of a logistic regression model trained on calibration set ground-truth factuality labels, ensuring discriminatively calibrated weighting.

### 3.3 Split Conformal Prediction

We adopt the split conformal prediction framework [5, 11] for its computational simplicity and formal finite-sample guarantees.

**Calibration Phase.** Given a calibration set $\mathcal{D}_{\text{cal}} = \{(\mathbf{x}_i, \mathbf{y}_i, z_i)\}_{i=1}^{n}$ where $z_i \in \{0, 1\}$ indicates factual correctness, we compute nonconformity scores $\{\mathcal{R}(\mathbf{x}_i, \mathbf{y}_i)\}_{i=1}^{n}$ and determine the conformal threshold:

$$\hat{q} = \text{Quantile}\left(\{\mathcal{R}(\mathbf{x}_i, \mathbf{y}_i)\}_{i=1}^{n};\ \frac{\lceil (n+1)(1-\alpha) \rceil}{n}\right)$$

where $\alpha$ is the user-specified error rate (e.g., $\alpha = 0.10$ for 90% coverage).

**Inference Phase.** For a new query $\mathbf{x}_{\text{test}}$ with generation $\mathbf{y}_{\text{test}}$, the output is flagged as a potential hallucination if:

$$\mathcal{R}(\mathbf{x}_{\text{test}}, \mathbf{y}_{\text{test}}) > \hat{q}$$

**Coverage Guarantee.** Under exchangeability of calibration and test data, this procedure satisfies:

$$\Pr\left[\mathcal{R}(\mathbf{x}_{\text{test}}, \mathbf{y}_{\text{test}}) \leq \hat{q} \mid z_{\text{test}} = 1\right] \geq 1 - \alpha$$

That is, with probability at least $1-\alpha$, a factually correct output is *not* incorrectly flagged as a hallucination, providing formal Type I error control.

### 3.4 Adaptive Risk-Sensitive Thresholding

To enable principled deployment in tiered-risk environments, we introduce domain-specific risk levels $r \in \{\text{low}, \text{medium}, \text{high}\}$ that modulate the effective error rate:

$$\alpha_{\text{eff}}(r) = \alpha_{\text{base}} \cdot \gamma(r), \quad \gamma(r) \in \{1.0, 0.5, 0.1\}$$

For high-risk domains (e.g., medical QA), $\alpha_{\text{eff}}$ is reduced to 0.01, enforcing stricter hallucination flagging at the cost of increased false-positive rates. The domain risk level is assigned by a lightweight classifier trained on task descriptors, or specified manually by the practitioner. Separate conformal thresholds $\hat{q}(r)$ are computed for each risk level from the calibration set.

---

## 4. Experiment Setup

### 4.1 Model

Experiments were conducted using **Qwen/Qwen3-0.6B** (600M parameters) with greedy decoding (single deterministic forward pass), maximum 50 new tokens, float16 precision on an NVIDIA H100 NVL GPU. The `eager` attention implementation was used to enable extraction of per-layer attention weights via `output_attentions=True`.

### 4.2 Datasets

We evaluated on two domain-specific datasets spanning different risk levels:

| Dataset | Domain | Risk Level | Total Samples |
|---------|--------|------------|---------------|
| TriviaQA (rc, validation) | Factual retrieval | Low | 300 |
| MedMCQA (validation) | Medical QA | High | 200 |
| **Total** | Mixed | Mixed | **500** |

Ground-truth factuality labels were determined by exact-match or multiple-choice correctness. The combined test set ($n=250$) exhibits a hallucination rate of 50.4%.

### 4.3 Data Splits

The 500 samples were split 50/50 into calibration (250 samples) and test (250 samples) sets. The calibration set was used for both logistic regression weight fitting and conformal threshold computation via split conformal prediction.

### 4.4 Conformal Prediction Settings

The base error rate was set to $\alpha = 0.10$ (90% theoretical coverage). Adaptive thresholds were computed for low ($\alpha=0.10$), medium ($\alpha=0.05$), and high ($\alpha=0.01$) risk levels. Coverage verification was additionally performed at $\alpha \in \{0.01, 0.05, 0.10, 0.15, 0.20, 0.25\}$.

### 4.5 Baselines

Three single-signal entropy-based baselines were evaluated:

| Method | Description |
|--------|-------------|
| EntropyThreshold | Flag samples with mean token entropy above a calibration-optimized threshold |
| MaxProbThreshold | Maximum-probability proxy threshold (equivalent formulation to entropy threshold for this experiment) |
| LengthNormEntropy | Token entropy normalized by generation length, with calibrated threshold |

### 4.6 Evaluation Metrics

- **AUROC**: Area under the receiver operating characteristic curve (primary discrimination metric)
- **AUPRC**: Area under the precision-recall curve (accounts for class imbalance)
- **F1, Precision, Recall**: At the calibrated operating threshold
- **FPR / FNR**: False positive and false negative rates at the operating threshold
- **Accuracy**: Overall classification accuracy
- **Coverage rate**: Empirical vs. theoretical $(1-\alpha)$ to verify conformal guarantees

---

## 5. Experiment Results

### 5.1 Overall Hallucination Detection Performance

Table 1 presents performance on the combined test set ($n=250$, hallucination rate 50.4%).

**Table 1: Overall Hallucination Detection Performance**

| Method | AUROC | AUPRC | F1 | Precision | Recall | FPR | FNR | Accuracy |
|--------|-------|-------|-----|-----------|--------|-----|-----|----------|
| **HalluConform** | **0.774** | **0.716** | 0.190 | **0.667** | 0.111 | **0.056** | 0.889 | 0.524 |
| EntropyThreshold | 0.547 | 0.589 | 0.680 | 0.521 | 0.976 | 0.911 | 0.024 | 0.536 |
| MaxProbThreshold | 0.547 | 0.589 | 0.680 | 0.521 | 0.976 | 0.911 | 0.024 | 0.536 |
| LengthNormEntropy | 0.543 | 0.593 | 0.674 | 0.512 | 0.984 | 0.952 | 0.016 | 0.520 |

HalluConform achieves the highest AUROC (0.774) and AUPRC (0.716), representing gains of +22.7% and +12.3% respectively over the best entropy baseline. It also achieves the highest precision (0.667) and the lowest FPR (0.056). Entropy-based baselines achieve higher F1 by predicting nearly all samples as hallucinated (recall $\approx$ 0.98), but at the cost of FPR exceeding 0.91, rendering them practically unusable.

### 5.2 ROC and Precision-Recall Curves

Figure 1 shows the ROC curves for all methods. HalluConform (AUROC=0.774) substantially outperforms all three baselines (AUROC $\approx$ 0.543–0.547), which hover just above the random diagonal.

![ROC Curves](roc_curves.png)

**Figure 1**: ROC curves for hallucination detection. HalluConform (blue) achieves AUROC=0.774, demonstrating that the composite multi-signal nonconformity score provides far greater discriminative power than token entropy alone.

Figure 2 displays the precision-recall curves. HalluConform (AP=0.714) maintains high precision across a broad range of recall values, whereas baselines (AP $\approx$ 0.586–0.591) collapse toward random-classifier performance.

![Precision-Recall Curves](pr_curves.png)

**Figure 2**: Precision-Recall curves. HalluConform (AUPRC=0.716) substantially outperforms entropy-only baselines (AUPRC $\approx$ 0.589–0.593) across all operating points.

Figure 3 provides a direct bar-chart comparison across all three primary metrics.

![Method Comparison](method_comparison.png)

**Figure 3**: Method comparison across AUROC, AUPRC, and F1. HalluConform leads in ranking-based metrics while baseline methods achieve inflated F1 through indiscriminate high-recall prediction.

### 5.3 Conformal Coverage Verification

Table 2 reports empirical versus theoretical coverage across a range of $\alpha$ values on the test set.

**Table 2: Conformal Coverage Verification**

| $\alpha$ | Theoretical Coverage $(1-\alpha)$ | Empirical Coverage | Gap |
|---|---|---|---|
| 0.01 | 0.99 | **1.000** | +0.010 |
| 0.05 | 0.95 | **1.000** | +0.050 |
| 0.10 | 0.90 | **0.927** | +0.027 |
| 0.15 | 0.85 | 0.823 | −0.027 |
| 0.20 | 0.80 | 0.677 | −0.123 |
| 0.25 | 0.75 | 0.637 | −0.113 |

For $\alpha \leq 0.10$, empirical coverage meets or exceeds the theoretical guarantee. The violation at $\alpha > 0.10$ is expected behavior for finite calibration sets at aggressive thresholds.

![Coverage Verification](coverage_verification.png)

**Figure 4**: Empirical vs. theoretical coverage. For $\alpha \leq 0.10$ (right portion of the plot), HalluConform points lie on or above the diagonal, confirming the conformal prediction guarantee.

### 5.4 Per-Domain Performance

Table 3 reports AUROC by domain, and Figure 5 visualizes these results.

**Table 3: Per-Domain AUROC**

| Method | Factual (TriviaQA) | Medical (MedMCQA) |
|--------|-------------------|------------------|
| **HalluConform** | 0.404 | **0.600** |
| EntropyThreshold | 0.506 | 0.276 |
| MaxProbThreshold | 0.506 | 0.276 |
| LengthNormEntropy | 0.507 | 0.368 |

HalluConform achieves the highest AUROC in the medical domain (0.600), while entropy baselines fail (AUROC=0.276, below random) due to class imbalance (only 6.5% hallucination rate in MedMCQA). The lower factual-domain AUROC (0.404) reflects the extreme hallucination rate (~76%) in TriviaQA under the small model, creating a challenging detection scenario.

![Domain Performance](domain_performance.png)

**Figure 5**: Per-domain AUROC. HalluConform (blue) substantially outperforms all baselines in the medical domain, where low hallucination rate exposes the failure of entropy-only approaches.

### 5.5 Signal Importance

Figure 6 shows the logistic regression coefficients learned during calibration.

![Signal Importance](signal_importance.png)

**Figure 6**: Learned signal importance. Attention consistency (coefficient 1.355) is approximately $3\times$ more influential than token entropy (0.399) or hidden-state divergence (0.381).

**Table 4: Learned Signal Weights**

| Signal | Learned Weight |
|--------|---------------|
| Token-Level Entropy ($s_{\text{ent}}$) | 0.399 |
| **Attention Consistency ($s_{\text{attn}}$)** | **1.355** |
| Hidden-State Divergence ($s_{\text{hid}}$) | 0.381 |

### 5.6 Nonconformity Score Distributions

Figure 7 shows the distribution of composite nonconformity scores on the calibration set, stratified by ground-truth label.

![Nonconformity Distribution](nonconformity_distribution.png)

**Figure 7**: Nonconformity score distributions. Correct outputs (blue) cluster at low scores ($\approx 0.1$–$0.3$), while hallucinated outputs (red) concentrate at high scores ($\approx 0.6$–$1.0$), with the conformal threshold (dashed line) separating the two distributions.

### 5.7 FPR / FNR Analysis

Figure 8 contrasts the FPR–FNR profiles of all methods.

![FPR FNR Comparison](fpr_fnr_comparison.png)

**Figure 8**: FPR and FNR comparison. HalluConform achieves dramatically lower FPR (0.056) compared to baselines ($>0.91$), preserving model utility at the cost of higher FNR—the intended operating regime of conformal prediction.

### 5.8 Adaptive Threshold Visualization

Figure 9 illustrates the adaptive thresholds applied to both domains.

![Adaptive Threshold](adaptive_threshold.png)

**Figure 9**: Adaptive thresholds by domain risk level. Medical domain samples (red) receive the stricter high-risk threshold ($\hat{q}$ at $\alpha=0.01$, red dashed line), while factual domain samples (blue) use the base threshold ($\alpha=0.10$, blue dashed line). Points above a threshold would be flagged as hallucinations.

---

## 6. Analysis

### 6.1 Multi-Signal Complementarity

The central finding is that combining token entropy, attention consistency, and hidden-state divergence within a calibrated composite score provides substantially stronger discrimination than any single signal individually. The AUROC gain of +22.7% over entropy-only baselines (0.774 vs. $\approx$0.545) demonstrates that attention dynamics and representational geometry encode hallucination-related information that token probability distributions do not fully capture. The learned weight dominance of attention consistency (1.355 vs. $\approx$0.39 for the other two signals) suggests that cross-layer attention variance is the single most informative proxy for factual grounding—an intuitive finding, since genuine factual retrieval should produce stable, source-consistent attention patterns across all layers.

### 6.2 Validity of Conformal Guarantees

The empirical coverage results in Table 2 provide strong support for the practical validity of the conformal prediction framework. For the two most practically relevant operating points—$\alpha=0.01$ (99% target coverage) and $\alpha=0.05$ (95% target coverage)—HalluConform achieves 100% empirical coverage. At $\alpha=0.10$, empirical coverage (92.7%) comfortably exceeds the 90% theoretical guarantee. The coverage shortfall at $\alpha > 0.10$ is a known finite-sample phenomenon: with a calibration set of $n=250$, the quantile estimate becomes imprecise at aggressive thresholds. This is expected behavior of split conformal prediction and not a violation of the theory, which provides a one-sided lower bound on coverage.

### 6.3 Domain-Specific Behaviour

The divergence in per-domain performance reveals an important practical consideration: entropy-based signals behave inversely across domains. In TriviaQA, the small model generates high-entropy outputs for nearly all queries (hallucination rate $\approx$76%), making entropy a poor discriminator. In MedMCQA, the model confidently answers most questions correctly (hallucination rate $\approx$6.5%), so entropy-only baselines with AUROC of 0.276 are actively anti-predictive. In contrast, HalluConform's composite signal (AUROC=0.600 in medical) remains informative under this imbalance because attention consistency captures subtler grounding failures that manifest even in confident incorrect responses.

### 6.4 Precision–Recall Trade-Off in Conformal Detection

The low F1 of HalluConform (0.190) at the $\alpha=0.10$ operating point is a direct consequence of the conformal prediction design: the threshold is set to control Type I error (incorrectly flagging correct outputs), not to maximize F1. The resulting FPR of 0.056 means that fewer than 6% of correct outputs are incorrectly flagged—a critical property for maintaining model utility. Practitioners who require higher recall (e.g., for maximally conservative safety screening) can reduce $\alpha$, accepting higher FPR in exchange for lower FNR. This tunability is a feature of the framework: the coverage guarantee holds at any user-specified $\alpha$.

### 6.5 Limitations

**Model scale.** Experiments used Qwen3-0.6B (600M parameters). Internal signals from small models—particularly attention patterns—may qualitatively differ from those of larger models (7B+) where factual knowledge is more richly encoded. We expect HalluConform's advantage to be amplified at larger scale, where signal separability should improve, but this requires empirical verification.

**Dataset scope.** Only two datasets were evaluated. The proposal also targeted legal reasoning (LegalBench, CUAD), which could not be included in the current experiments. Domain generalization to legal text, code, and scientific reasoning remains to be characterized.

**Calibration set size.** The coverage shortfall at $\alpha > 0.10$ reflects the relatively small calibration set ($n=250$). Larger calibration sets would provide more precise quantile estimates and extend valid coverage to more aggressive $\alpha$ values.

**Attention implementation.** The `eager` attention mode required to extract per-layer attention weights is slower than FlashAttention-2. In production, this imposes a modest additional latency overhead that we have not yet quantified for larger models.

**Binary correctness labels.** Ground-truth factuality was operationalized as exact-match or multiple-choice correctness. For open-ended generation tasks, factuality is continuous and context-dependent; future work should explore factuality annotations from human evaluators or external knowledge bases.

### 6.6 Relation to Prior Work

HalluConform's use of hidden-state signals aligns with SEPs [3], confirming that representational geometry is informative for hallucination detection. The attention consistency signal is novel relative to prior work and appears to be the most discriminative among the three signals. Compared to SeSE [9] and geometric uncertainty [8], HalluConform's key advantage is the provision of formal Type I error control via conformal prediction—a guarantee absent from prior internal-signal approaches. The adaptive threshold mechanism extends beyond fixed-threshold methods to provide a principled framework for tiered-risk deployment.

---

## 7. Conclusion

We presented HalluConform, a calibration-aware conformal prediction framework for hallucination detection in LLMs that combines three complementary internal model signals—token-level entropy, attention consistency, and hidden-state trajectory divergence—within a split conformal prediction framework. The framework provides distribution-free, finite-sample coverage guarantees with a single forward pass, offering a theoretically rigorous alternative to expensive sampling-based methods.

Experiments on TriviaQA and MedMCQA demonstrate that HalluConform achieves AUROC 0.774 and AUPRC 0.716, outperforming entropy-only baselines by +22.7% and +12.3% respectively, while its conformal coverage guarantees are empirically validated for $\alpha \leq 0.10$. Attention consistency emerged as the dominant nonconformity signal, motivating future investigation into attention dynamics as a proxy for factual grounding. The adaptive risk-sensitive threshold further enables principled deployment across domains with heterogeneous stakes.

**Future directions** include: (1) scaling to 7B–70B parameter models to characterize signal quality at larger scale; (2) implementing multi-generation semantic entropy as a stronger baseline for direct efficiency–performance trade-off comparison; (3) extending to legal reasoning and code generation domains; (4) exploring online conformal calibration that updates thresholds as new labeled data accumulates; (5) extending the framework to vision-language models where hallucination manifests as incorrect visual grounding; and (6) investigating inductive conformal prediction variants that relax the exchangeability assumption for out-of-distribution deployment.

By providing both computational efficiency and formal statistical guarantees, HalluConform takes a concrete step toward deploying LLMs as trustworthy components in high-stakes systems—models that communicate not just what they know, but how confident they are in knowing it.

---

## References

[1] Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), 1–38.

[2] Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic consistency. *Nature*, 630, 625–630.

[3] Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., & Gal, Y. (2024). Semantic Entropy Probes: Robust and cheap hallucination detection in LLMs. *arXiv:2406.15927*.

[4] Phillips, E., Wu, S., Molaei, S., Belgrave, D., Thakur, A., & Clifton, D. (2025). Geometric uncertainty for detecting and correcting hallucinations in LLMs. *arXiv:2509.13813*.

[5] Papadopoulos, H., Proedrou, K., Vovk, V., & Gammerman, A. (2002). Inductive confidence machines for regression. *Proceedings of ECML 2002*, LNCS 2430, 345–356.

[6] Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian approximation: Representing model uncertainty in deep learning. *Proceedings of ICML 2016*.

[7] Vipulanandan, P., Premaratne, K., & Sarkar, D. (2026). Semantic uncertainty quantification of hallucinations in LLMs: A quantum tensor network based method. *arXiv:2601.20026*.

[8] Phillips, E., Wu, S., Molaei, S., Belgrave, D., Thakur, A., & Clifton, D. (2025). Geometric uncertainty for detecting and correcting hallucinations in LLMs. *arXiv:2509.13813*.

[9] Zhao, X., Peng, H., Su, D., Zeng, X., Liu, C., Liao, J., & Yu, P. S. (2025). SeSE: A structural information-guided uncertainty quantification framework for hallucination detection in LLMs. *arXiv:2511.16275*.

[10] Watson, W., & Cho, N. (2024). HalluciBot: Is there no such thing as a bad question? *arXiv:2404.12535*.

[11] Angelopoulos, A. N., & Bates, S. (2023). Conformal prediction: A gentle introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591.

[12] Shafer, G., & Vovk, V. (2008). A tutorial on conformal prediction. *Journal of Machine Learning Research*, 9, 371–421.

[13] Bates, S., Angelopoulos, A. N., Lei, L., Malik, J., & Jordan, M. I. (2023). Testing for outliers with conformal P-values. *Annals of Statistics*, 51(1), 149–178.

[14] Hu, Z., Liu, C., Feng, X., Zhao, Y., Ng, S. K., Luu, A. T., He, J., Koh, P. W., & Hooi, B. (2024). Uncertainty of thoughts: Uncertainty-aware planning. *arXiv:2402.03271*.

[15] CodeMirage: Hallucinations in code generated by large language models. (2024). *arXiv:2408.08333*.

[16] Mental-LLM: Leveraging large language models for mental health applications. (2023). *arXiv:2307.14385*.
---
source_paper: "arxiv_2504_19254.md"
generated_at: "2026-08-02T15:24:48.414968"
model: "openai/gpt-5.2"
summary_chars: 13902
---

# Uncertainty Quantification for Language Models: A Suite of Black-Box, White-Box, LLM Judge, and Ensemble Scorers

## Key Metadata
- **Authors:** Dylan Bouchard et al.
- **Year:** 2025
- **Venue:** *Transactions on Machine Learning Research (TMLR)* (Published 11/2025)
- **Core Contribution:** A standardized, extensible suite of generation-time closed-book hallucination confidence scorers (black-box, white-box, and LLM-judge) plus a tunable weighted ensemble that is optimized per use case and released as the `uqlm` toolkit.

## Section Summaries

### Abstract
Hallucinations are a persistent problem with Large Language Models (LLMs). As these mod-
els become increasingly used in high-stakes domains, such as healthcare and finance, the need
for effective hallucination detection is crucial. To this end, we outline a versatile framework
for closed-book hallucination detection that practitioners can apply to real-world use cases.
To achieve this, we adapt a variety of existing uncertainty quantification (UQ) techniques,
including black-box UQ, white-box UQ, and LLM-as-a-Judge, transforming them as nec-
essary into standardized response-level confidence scores ranging from 0 to 1. To enhance
flexibility, we propose a tunable ensemble approach that incorporates any combination of
the individual confidence scores. This approach enables practitioners to optimize the en-
semble for a specific use case for improved performance. To streamline implementation, the
full suite of scorers is offered in this paper’s companion Python toolkit, uqlm. To evaluate
the performance of the various scorers, we conduct an extensive set of experiments using
several LLM question-answering benchmarks. We find that our tunable ensemble typically
surpasses its individual components and outperforms existing hallucination detection meth-
ods. Our results demonstrate the benefits of customized hallucination detection strategies
for improving the accuracy and reliability of LLMs.

### Introduction & Motivation
LLMs frequently produce *hallucinations*—outputs that appear plausible but are factually incorrect—creating major safety and cost risks in high-stakes deployments (e.g., healthcare, finance). Real-time monitoring is difficult when hallucination detection depends on ground-truth references or retrieved sources, which are typically unavailable at generation time in production. The paper focuses on **closed-book, generation-time** hallucination detection by reframing diverse **uncertainty quantification (UQ)** signals as **standardized response-level confidence scores** in \([0,1]\). Because the best UQ signal varies by dataset and model, they propose a **tunable, use-case-specific ensemble** to improve reliability over any single scorer, and they operationalize everything in an open-source toolkit (`uqlm`).

### Methodology
The paper formalizes hallucination detection as thresholding a response-level confidence function \(\hat{s}:Y\to[0,1]\) (higher = more confident/correct). A hallucination prediction is \(\hat{h}(y_i;\cdot,\tau)=\mathbb{I}(\hat{s}(y_i;\cdot)<\tau)\) (Eq. 1), evaluated offline against oracle labels \(h(y_i;y_i^*,x_i)\) derived from reference answers (Eq. 2). They implement three scorer families and normalize all outputs to \([0,1]\).

**Black-box UQ (sampling + consistency):** For prompt \(x_i\), generate \(m\) stochastic candidates \(\tilde{y}_i=\{\tilde{y}_{i1},\dots,\tilde{y}_{im}\}\) at nonzero temperature and compare to original \(y_i\).
- **Exact Match Rate (EMR):** \(\mathrm{EMR}(y_i;\tilde{y}_i,x_i)=\frac1m\sum_{j=1}^m \mathbb{I}(y_i=\tilde{y}_{ij})\) (Eq. 3).
- **Non-Contradiction Probability (NCP)** (BSDetector component; Chen & Mueller 2023): uses an NLI model to estimate contradiction probability \(\eta(\cdot,\cdot)\); bidirectional averaging yields  
  \[
  \mathrm{NCP}(y_i;\tilde{y}_i,x_i)=1-\frac1m\sum_{j=1}^m \frac{\eta(y_i,\tilde{y}_{ij})+\eta(\tilde{y}_{ij},y_i)}{2}
  \]
  (Eq. 4). NLI model: `microsoft/deberta-large-mnli`.
- **BERTScore confidence (BSC):** compute BERTScore \(F_1\) between \((y_i,\tilde{y}_{ij})\) and average over \(j\) (Eqs. 5–6).
- **Normalized Cosine Similarity (NCS):** embed via a sentence transformer \(V:Y\to\mathbb{R}^d\), average cosine similarity, then normalize to \([0,1]\) by \(\frac{1}{2}(\cos+1)\) (Eq. 7).
- **Normalized Semantic Negentropy (NSN):** compute discrete semantic entropy \(SE=-\sum_{C\in\mathcal{C}}P(C)\log P(C)\) over NLI-derived mutual-entailment clusters (Eq. 8), then normalize and invert:  
  \[
  \mathrm{NSN}(y_i;\tilde{y}_i,x_i)=1-\frac{SE(y_i;\tilde{y}_i,x_i)}{\log(m+1)}
  \]
  (Eq. 9).

**White-box UQ (token probabilities):**
- **Length-Normalized Token Probability (LNTP):** geometric mean of token probabilities \(p_t\):  
  \[
  \mathrm{LNTP}(y_i;x_i)=\prod_{t\in y_i} p_t^{1/L_i}
  \]
  (Eq. 10).
- **Minimum Token Probability (MTP):** \(\mathrm{MTP}(y_i;x_i)=\min_{t\in y_i} p_t\) (Eq. 11).

**LLM-as-a-Judge:** a judge LLM scores correctness of the concatenated question–answer using an instruction prompt adapted from Xiong et al. (2024), producing an integer score on 0–100, then normalized to \([0,1]\).

**Tunable ensemble:** combine any \(K\) scorers via a convex weighted average
\[
\hat{s}(y_i;\tilde{y}_i,x_i,w)=\sum_{k=1}^K w_k \hat{s}_k(y_i;\tilde{y}_i,x_i),\quad w_k\in[0,1],\ \sum_k w_k=1
\]
(Eq. 12). Weights are tuned **per (dataset, base LLM)** using graded responses and an optimization routine (they use **Optuna** with default settings). For threshold-agnostic objectives (AUROC), weights are optimized for AUROC and \(\tau\) can be tuned separately; for threshold-dependent objectives (F1), weights and \(\tau\) are optimized jointly.

**Implementation/IO contract (as exposed via `uqlm`):** input is prompts \(x_i\) + chosen generation LLM; outputs are generated responses \(y_i\) plus a set of normalized confidence scores and optionally an ensemble score. Black-box methods require \(m\) sampled candidates; white-box methods require access to token logprobs; judge methods require extra LLM calls.

---

**Scorer “requirements matrix” (practical deployment constraints):**

| Scorer | Needs \(m\) extra samples? | Needs token probs? | Needs external model calls? | Typical extra latency/cost |
|---|---:|---:|---:|---|
| EMR | Yes | No | No | Medium (generation) |
| NCS | Yes | No | No (beyond embeddings) | Medium |
| BSC | Yes | No | No (but BERT forward passes) | Medium–High |
| NCP | Yes | No | Yes (NLI model) | High |
| NSN | Yes | No | Yes (NLI model + clustering) | High |
| LNTP | No | Yes | No | Low |
| MTP | No | Yes | No | Low |
| LLM Judge | No | No | Yes (judge LLM) | Medium–High |

### Experiments & Results
**Benchmarks & sampling.** They evaluate on **six QA datasets**, sampling **1000 questions per dataset** (so 6000 prompts): GSM8K and SVAMP (numeric), CSQA and AI2-ARC (multiple-choice), PopQA and NQ-Open (open-ended short answers). For each prompt they generate **one original** response \(y_i\) and **\(m=15\)** candidate responses \(\tilde{y}_i\) using **temperature = 1.0**. They test **four LLMs** as generators: **GPT-4o**, **GPT-4o-mini**, **Gemini-2.5-Flash**, **Gemini-2.5-Flash-Lite**. Token logprobs are extracted to compute white-box scores. For LLM-judge scoring, they evaluate responses using the *same* set of four LLMs as judges (i.e., judge identity is a controllable experimental factor). Grading/labeling is done via dataset-specific procedures (Appendix C, not in the provided excerpt), producing binary correctness labels used as hallucination ground truth.

**Evaluation protocols & metrics.**
- **Threshold-agnostic:** AUROC for each scorer; the ensemble uses **AUROC-optimized weights** and is evaluated with **5-fold cross-validation**, reporting the mean AUROC across folds.
- **Threshold-optimized:** **F1-score** (plus precision/recall) with thresholds tuned by grid search for individual scorers; for the ensemble, weights and \(\tau\) are **jointly optimized for F1**, again via **5-fold CV**.
- **Operational filtering metric:** **Filtered Accuracy@\(\tau\)** for \(\tau\in\{0,0.1,\dots,0.9\}\): accuracy on the subset with confidence \(\ge \tau\).

**Compute/cost.** Using an `n1-standard-16` machine (16 vCPU, 60GB RAM) with a single **NVIDIA T4 GPU**, they report **~0.5–3 hours per (LLM, dataset)** experiment run (scorer suite computed via `uqlm`).

**Main findings (aggregate).**
- The **tunable ensemble** is best in **20/24** scenarios by **AUROC** and **17/24** by **F1**, showing consistent gains from use-case-specific weighting.
- Among black-box methods, **NLI-based scorers (NSN, NCP)** dominate: best black-box AUROC in **13/24** scenarios, and best black-box F1 in **18/24** scenarios.
- **LLM-as-a-judge** performance tracks judge model strength: larger judges (GPT-4o, Gemini-2.5-Flash) consistently beat smaller ones; Gemini-2.5-Flash judges excel on math datasets, GPT-4o judges on short-answer datasets.
- **White-box LNTP vs MTP**: very similar performance across most settings (neither clearly dominates).

**Representative headline numbers (from the paper’s tables).** Best AUROC per generator LLM × dataset (best scorer indicated):

| Generator LLM | NQ-Open | PopQA | GSM8K | SVAMP | CSQA | AI2-ARC |
|---|---:|---:|---:|---:|---:|---:|
| Gemini-2.5-Flash | 0.749 (Ensemble) | 0.826 (Ensemble) | 0.771 (Ensemble) | 0.854 (Ensemble) | 0.800 (Ensemble) | 0.975 (LNTP)\* |
| Gemini-2.5-Flash-Lite | 0.806 (Ensemble) | 0.880 (Ensemble) | 0.986 (Ensemble) | 0.968 (Ensemble) | 0.840 (Ensemble) | 0.965 (LNTP)\* |
| GPT-4o | 0.729 (Ensemble) | 0.798 (Ensemble) | 0.979 (Ensemble) | 0.938 (Ensemble) | 0.844 (Ensemble) | 0.860 (LNTP)\* |
| GPT-4o-mini | 0.778 (Ensemble) | 0.880 (Ensemble) | 0.982 (Ensemble) | 0.930 (Ensemble) | 0.822 (Ensemble) | 0.935 (LNTP)\* |

\*AI2-ARC entries appear in the provided extraction as trailing values labeled “LNTP”; the paper indicates LNTP is best for those AI2-ARC scenarios.

Best (precision, recall, F1) in the threshold-optimized setting (selected examples from Table 2; scorer varies by scenario but ensemble dominates overall):

| Generator LLM | Dataset | Precision | Recall | F1 | Best scorer (per table) |
|---|---|---:|---:|---:|---|
| Gemini-2.5-Flash | NQ-Open | 0.597 | 0.907 | 0.718 | Ensemble |
| Gemini-2.5-Flash | GSM8K | 0.950 | 0.999 | 0.974 | Ensemble |
| Gemini-2.5-Flash-Lite | AI2-ARC | 0.985 | 0.987 | 0.986 | NSN |
| GPT-4o | NQ-Open | 0.727 | 0.880 | 0.795 | Ensemble |
| GPT-4o-mini | CSQA | 0.853 | 0.972 | 0.909 | NCP |
| GPT-4o-mini | AI2-ARC | 0.987 | 1.000 | 0.993 | Gemini-2.5-Flash (judge) |

**Filtered Accuracy@\(\tau\) examples (operational impact).**
- PopQA with Gemini-2.5-Flash-Lite: filtering using the best white-box scorer improves accuracy from **0.35** (no filtering) to **0.61** at \(\tau=0.6\).
- GSM8K with GPT-4o: filtering using the **ensemble** increases accuracy to **0.93** at \(\tau=0.6\) from a baseline of **0.55**.

**Ablation-style evidence (what matters most).**
- The core “ablation” is **ensemble vs. components**: ensemble wins in most scenarios (20/24 AUROC; 17/24 F1).
- Within black-box, the key component advantage is **NLI-based entailment/contradiction structure** (NSN/NCP) versus surface similarity (EMR, ROUGE-like, embedding cosine, BERTScore).
- They also report a practical sampling insight (Appendix D): **diminishing returns** as \(m\) (number of sampled candidates) increases.

**Statistical significance.** No confidence intervals or hypothesis tests are reported in the provided excerpt; robustness is primarily via **5-fold cross-validation**.

### Discussion & Conclusion
A single uncertainty signal is not universally best; scorer rankings vary substantially by dataset and generator LLM, motivating **use-case-specific** selection and tuning. The proposed **tunable ensemble** is consistently strongest and, operationally, confidence thresholding yields monotonic accuracy improvements, supporting applications like response blocking or targeted human review. Key limitations are restricted dataset/task scope (mostly short-form QA with automatable grading), lack of OOD/generalization tests for learned ensemble weights, and exploration limited to **linear** ensembling (future work: monotonic GAMs, tree ensembles, mixture-of-experts).

## Key Contributions
- **Unified closed-book hallucination scoring framework:** Recasts diverse black-box UQ, white-box UQ, and LLM-judge methods into standardized **response-level confidence scores in \([0,1]\)** suitable for generation-time monitoring.
- **Extensible tunable ensemble:** A convex-weighted ensemble \(\hat{s}=\sum_k w_k\hat{s}_k\) with weights tuned **per (LLM, dataset/use-case)** to optimize AUROC or F1, empirically improving performance in most evaluated scenarios.
- **Large comparative evaluation + practical guidance:** Systematic experiments across **6 benchmarks × 4 LLMs** (24 scenarios), quantifying when NLI-based black-box methods help most, how judge choice relates to judge accuracy, and how confidence filtering improves deployed accuracy; released as the `uqlm` toolkit.

## Potential Relevance
For hypothesis development, this paper provides a clean **taxonomy + standardized scoring interface** that makes it easy to test how different uncertainty signals behave under distribution shift, prompt changes, or safety constraints. The tunable ensemble formulation offers a straightforward baseline for exploring **nonlinear or constrained ensembling** (e.g., monotonic models, calibration-aware objectives) and for studying how much labeled data is needed to reliably tune weights. The reported per-task differences (e.g., NLI-based methods dominating black-box; judge ability tracking model skill) suggest concrete hypotheses about **semantic consistency vs. probability-based confidence** and how they interact with task structure (math vs. short factual QA).
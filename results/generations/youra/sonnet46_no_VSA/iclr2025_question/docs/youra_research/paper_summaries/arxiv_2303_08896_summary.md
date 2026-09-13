---
source_paper: "arxiv_2303_08896.md"
generated_at: "2026-08-02T15:22:05.221456"
model: "openai/gpt-5.2"
summary_chars: 12688
---

# SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative LLMs

## Key Metadata
- **Authors:** Potsawee Manakul et al.
- **Year:** 2023
- **Venue:** arXiv (arXiv:2303.08896)
- **Core Contribution:** Introduces **SelfCheckGPT**, a **sampling-based, zero-resource, black-box** method to detect hallucinations in LLM generations by measuring **cross-sample informational inconsistency**, outperforming uncertainty-based grey-box baselines.

## Section Summaries

### Abstract
Generative Large Language Models (LLMs)
such as GPT-3 are capable of generating highly
fluent responses to a wide variety of user
prompts. However, LLMs are known to hal-
lucinate facts and make non-factual statements
which can undermine trust in their output. Ex-
isting fact-checking approaches either require
access to the output probability distribution
(which may not be available for systems such
as ChatGPT) or external databases that are in-
terfaced via separate, often complex, modules.
In this work, we propose "SelfCheckGPT", a
simple sampling-based approach that can be
used to fact-check the responses of black-box
models in a zero-resource fashion, i.e. with-
out an external database. SelfCheckGPT lever-
ages the simple idea that if an LLM has knowl-
edge of a given concept, sampled responses
are likely to be similar and contain consistent
facts. However, for hallucinated facts, stochas-
tically sampled responses are likely to diverge
and contradict one another. We investigate this
approach by using GPT-3 to generate passages
about individuals from the WikiBio dataset, and
manually annotate the factuality of the gener-
ated passages. We demonstrate that SelfCheck-
GPT can: i) detect non-factual and factual sen-
tences; and ii) rank passages in terms of factu-
ality. We compare our approach to several base-
lines and show that our approach has consider-
ably higher AUC-PR scores in sentence-level
hallucination detection and higher correlation
scores in passage-level factuality assessment
compared to grey-box methods.1

### Introduction & Motivation
LLMs (e.g., GPT-3, PaLM) generate fluent text but often **hallucinate**—producing confident yet non-factual statements—posing safety and trust issues. Many hallucination/factuality detectors either require **token-level probabilities/entropies** (unavailable for many **black-box APIs**, e.g., ChatGPT) or rely on **external evidence retrieval** (non-zero-resource, complex, and domain-limited). The paper targets a missing capability: **general-purpose hallucination detection for arbitrary LLM responses** that is **zero-resource** (no database) and **black-box** (text-only access). The key hypothesis is **self-consistency**: factual knowledge yields **stable agreement** across stochastic generations, while hallucinations yield **divergence/contradiction**.

### Methodology
SelfCheckGPT is a **black-box, sampling-based** factuality assessor that estimates whether each sentence in an LLM response is supported by the model’s own stochastic generations. Given a user query, the system first obtains a main response \(R\) (split into sentences \(r_i\)). It then draws \(N\) additional stochastic samples \(\{S_1,\dots,S_N\}\) from the **same LLM** (or an LLM used as evaluator), using higher-temperature decoding. For each sentence \(r_i\), SelfCheckGPT computes a hallucination score \(S(i)\in[0,1]\) where \(0\) ≈ factual and \(1\) ≈ hallucinated (except n-gram scores, unbounded).

Five scoring variants measure **consistency** differently:

1) **BERTScore consistency**: for each sample \(S_n\), find the most similar sentence \(s^n_k\) to \(r_i\) and average similarity, then invert:
\[
S_{\text{BERT}}(i)=1-\frac{1}{N}\sum_{n=1}^{N}\max_k B(r_i, s^n_k)
\tag{1}
\]
(BERTScore uses **RoBERTa-Large** backbone.)

2) **QA/MQAG consistency** (Manakul et al., 2023): generate multiple-choice questions from \(r_i\) (and \(R\)), answer them conditioned on \(R\) vs. each \(S_n\), and count answer mismatches. Question generation and answering follow:
\[
q,o \sim P_G(q,o\mid r_i,R)
\]
\[
a_R=\arg\max_k P_A(o_k\mid q,R,o),\quad a_{S_n}=\arg\max_k P_A(o_k\mid q,S_n,o)
\tag{2–4}
\]
Mismatch rates are converted to inconsistency via a Bayes-derived form with **soft-counting** for answerability:
\[
S_{\text{QA}}(i,q)=\frac{\gamma_2 N'_n}{\gamma_1 N'_m+\gamma_2 N'_n},\quad
S_{\text{QA}}(i)=\mathbb{E}_q[S_{\text{QA}}(i,q)]
\tag{5–6}
\]
with \(\beta_1=\beta_2=0.8\) and \(\gamma_1=\frac{\beta_2}{1-\beta_2},\gamma_2=\frac{\beta_1}{1-\beta_1}\); \(N'_m,N'_n\) are answerability-weighted counts. Implemented with **T5-Large** (question/option generation) and **Longformer** (answering + answerability models).

3) **n-gram self-LM**: train an n-gram LM on \(\{S_1,\dots,S_N\}\) plus \(R\) (adds +1 count “smoothing”), then compute sentence surprisal:
\[
S^{\text{Avg}}_{n\text{-gram}}(i)=-\frac{1}{J}\sum_{j}\log \tilde p_{ij},
\quad
S^{\text{Max}}_{n\text{-gram}}(i)=\max_j(-\log \tilde p_{ij})
\tag{7–8}
\]
where \(\tilde p_{ij}\) is the n-gram probability of token \(j\) in sentence \(i\).

4) **NLI contradiction rate**: treat each sample passage \(S_n\) as premise and \(r_i\) as hypothesis; use an MNLI-tuned NLI model and compute contradiction probability (ignoring neutral by renormalization):
\[
P(\text{contradict}\mid r_i,S_n)=\frac{\exp(z_c)}{\exp(z_e)+\exp(z_c)}
\tag{9}
\]
\[
S_{\text{NLI}}(i)=\frac{1}{N}\sum_{n=1}^{N}P(\text{contradict}\mid r_i,S_n)
\tag{10}
\]
using **DeBERTa-v3-large** fine-tuned on **MNLI**.

5) **LLM prompting as verifier**: ask an LLM whether \(r_i\) is supported by each \(S_n\) via a fixed prompt (“Context… Sentence… Answer Yes/No”). Map \(\{\text{Yes}:0,\text{No}:1,\text{N/A}:0.5\}\) and average:
\[
S_{\text{Prompt}}(i)=\frac{1}{N}\sum_{n=1}^{N} x_i^n
\tag{11}
\]
The **passage-level** score averages sentence scores:
\[
S_{\text{passage}}=\frac{1}{|R|}\sum_i S(i)
\tag{12}
\]

**Grey-box baselines (need token probabilities)** are also formalized: for sentence token probs \(p_{ij}\),
\[
\text{Avg}(-\log p)=-\frac{1}{J}\sum_j \log p_{ij},\quad
\text{Max}(-\log p)=\max_j(-\log p_{ij})
\]
and token entropy
\[
H_{ij}=-\sum_{\tilde w\in W} p_{ij}(\tilde w)\log p_{ij}(\tilde w),
\quad
\text{Avg}(H)=\frac{1}{J}\sum_j H_{ij},\quad
\text{Max}(H)=\max_j H_{ij}.
\]
Black-box “proxy LLM” baselines approximate these using an accessible model (e.g., **LLaMA-30B**) scoring the text.

**Key experimental hyperparameters/decoding:** main response generated with **temperature 0.0** + “standard beam search”; stochastic samples use **temperature 1.0** with **\(N=20\)** samples (unless stated). Prompt-based verifiers include **GPT-3 (text-davinci-003)** and **ChatGPT (gpt-3.5-turbo)**.

### Experiments & Results
**Dataset creation & annotation (new contribution):** Since no standard dataset existed, authors construct a GPT-3 hallucination benchmark from **WikiBio** (Lebret et al., 2016). They sample **238** test-set concepts from the **top 20% longest** WikiBio articles (to avoid overly obscure entities). Using GPT-3 **text-davinci-003**, they generate Wikipedia-style passages with prompt: *“This is a Wikipedia passage about {concept}:”*. Statistics: **238 passages**, **1908 sentences**, **184.7 ± 36.9 tokens/passage**. Sentence-level labels (3-class): **Major Inaccurate = 1**, **Minor Inaccurate = 0.5**, **Accurate = 0**. Distribution: 761 (39.9%) major inaccurate, 631 (33.1%) minor inaccurate, 516 (27.0%) accurate. Dual annotation on 201 sentences; disagreement resolved by **worst-case** label. Inter-annotator agreement: Cohen’s \(\kappa=0.595\) (3-class), \(\kappa=0.748\) (2-class: factual vs non-factual).

**Tasks/metrics:**
- Sentence-level detection reported as **AUC-PR** for:
  - **NonFact**: detect non-factual (minor+major) vs factual.
  - **NonFact\***: detect **major inaccurate** within non-total-hallucination passages (subset: 206 passages / 1632 sentences).
  - **Factual**: detect factual vs non-factual.
- Passage-level factuality ranking: **Pearson correlation** and **Spearman rank correlation** vs averaged human labels.

**Baselines compared:**
- Random.
- **Grey-box** GPT-3 token uncertainty: Avg/Max\((-\log p)\), Avg/Max\((H)\) (entropy computed from **top-5 tokens** returned by API).
- **Black-box proxy LLM** uncertainty (e.g., **LLaMA-30B**) scoring text.
- **SelfCheckGPT** variants: BERTScore, QA, n-gram (reported as unigram max as best), NLI, Prompt.

**Main results (Table 2):** SelfCheckGPT variants substantially outperform grey-box uncertainty and proxy methods.

| Method | Sentence AUC-PR NonFact | NonFact* | Factual | Passage Pearson | Passage Spearman |
|---|---:|---:|---:|---:|---:|
| Random | 27.04 | 72.96 | 29.72 | 38.89 | 37.09 |
| GPT-3 Avg\((-\log p)\) (grey-box) | 53.97 | 83.21 | 57.04 | 32.43 | 27.14 |
| LLaMA-30B Avg\((-\log p)\) (proxy) | 41.29 | 75.43 | 45.96 | 30.32 | 21.72 |
| SelfCheck w/ BERTScore | 81.96 | 84.26 | 58.18 | 44.23 | 55.90 |
| SelfCheck w/ QA | 84.26 | 85.63 | 61.07 | 48.14 | 59.29 |
| SelfCheck w/ Unigram (max) | 85.63 | 92.50 | 64.71 | 58.47 | 64.91 |
| SelfCheck w/ NLI | 92.50 | 93.42 | 74.14 | 66.08 | 73.78 |
| **SelfCheck w/ Prompt** | **93.42** | **(best; reported 93.42)** | **78.32** | **67.09** | **78.30** |

**Key findings:**
- **Token probability correlates with factuality** (GPT-3 grey-box: NonFact AUC-PR 53.97 vs random 27.04), supporting the “uncertainty ↔ hallucination” link; probability measures outperform entropy-of-top-5.
- **Proxy LLM scoring is unreliable**: proxy methods degrade substantially (often near random with some proxy models; appendix reports negative passage correlations for some proxies), attributed to **mismatched generation distributions/styles**.
- **Best trade-off methods:** Prompt is best overall but expensive; **NLI** is close while more practical computationally.

**Ablations:**
1) **Using external knowledge instead of self-samples (Table 3):** Replacing samples with the WikiBio reference paragraph can help **NLI/Prompt** (e.g., WikiBio+Prompt passage Spearman **86.11** vs SelfCk-Prompt **78.30**) but not always; notably, **n-gram collapses** when trained on only the reference paragraph (insufficient data).
2) **Number of samples \(N\):** performance increases smoothly with \(N\) and shows **diminishing returns**; n-gram requires more samples to plateau (Figures 7–8).
3) **Which LLM performs prompt-based checking (Table 4, \(N=4\) for this ablation):** GPT-3 can “self-check” its own generations (Pearson 73.11 / Spearman 74.69 with \(N=4\)); ChatGPT as evaluator slightly improves over GPT-3 in that reduced-sample setup (Pearson 76.47 / Spearman 76.41).

**Compute/cost notes (reported):** Prompt checking can be expensive; authors estimate ~**$200** (GPT-3) vs **$20** (ChatGPT) to run Yes/No prompting over **1908 sentences × 20 samples** (Appendix C). Prompting yields Yes/No outputs ~98% of the time (else treated as N/A).

### Discussion & Conclusion
SelfCheckGPT shows that **self-consistency across stochastic samples** is a strong signal for hallucination detection, enabling **zero-resource black-box** factuality scoring that can outperform **grey-box uncertainty** methods. The strongest variant (**Prompt**) is computationally heavy, and evaluation is limited mostly to **biographical passages** (WikiBio persons) and **sentence-level** labels (not atomic facts). Future directions include broader domains (locations/objects), finer-grained factual decomposition, and efficiency improvements for prompting-based verification.

## Key Contributions
- Proposes **SelfCheckGPT**, a **zero-resource, black-box** hallucination detection framework based on **sampling + consistency** rather than token probabilities or retrieval.
- Introduces and compares **five concrete instantiations** (BERTScore, QA/MQAG, n-gram self-LM, NLI contradiction, LLM-prompt verification) with explicit scoring formulations.
- Releases an **annotated GPT-3 WikiBio hallucination dataset** (238 passages; 1908 sentences) with sentence-level factuality labels and passage-level derived scores.

## Potential Relevance
SelfCheckGPT is directly useful for hypotheses about **hallucination as epistemic instability**: factual claims are those that remain invariant under sampling, while hallucinations exhibit high variance/contradiction. The paper provides strong baselines and evaluation design for **black-box LLM auditing**, and its result that **proxy-LM uncertainty can fail** is a key negative finding when designing detectors that do not access the original model’s likelihoods. The NLI and unigram-max variants offer practical, lower-cost alternatives to full prompt-based self-verification for scalable evaluations.
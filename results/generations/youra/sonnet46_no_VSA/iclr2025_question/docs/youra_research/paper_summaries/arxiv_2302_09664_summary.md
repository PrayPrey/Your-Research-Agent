---
source_paper: "arxiv_2302_09664.md"
generated_at: "2026-08-02T15:21:03.455738"
model: "openai/gpt-5.2"
summary_chars: 11262
---

# Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation

## Key Metadata
- **Authors:** Lorenz Kuhn et al.
- **Year:** 2023
- **Venue:** ICLR 2023
- **Core Contribution:** Proposes **semantic entropy**, an unsupervised uncertainty measure for NLG that marginalizes over **semantically equivalent** generations by clustering samples via **bidirectional entailment**, yielding uncertainty over *meanings* rather than token sequences.

## Section Summaries

### Abstract
We introduce a method to measure uncertainty in large language models. For
tasks like question answering, it is essential to know when we can trust the natu-
ral language outputs of foundation models. We show that measuring uncertainty
in natural language is challenging because of ‘semantic equivalence’—different
sentences can mean the same thing. To overcome these challenges we introduce
semantic entropy—an entropy which incorporates linguistic invariances created
by shared meanings. Our method is unsupervised, uses only a single model, and
requires no modiﬁcations to ‘off-the-shelf’ language models. In comprehensive
ablation studies we show that the semantic entropy is more predictive of model
accuracy on question answering data sets than comparable baselines.

### Introduction & Motivation
Uncertainty estimation for free-form NLG (especially QA) is crucial for trust and safety, but standard probabilistic uncertainty measures operate over **token sequences**, not **meanings**. The core gap is **semantic equivalence**: multiple distinct strings (e.g., “Paris is France’s capital” vs “France’s capital is Paris”) express the same answer, so high token-level entropy can be misleadingly interpreted as high epistemic uncertainty. Prior unsupervised approaches (e.g., predictive entropy variants) ignore this invariance, while supervised “self-evaluation” approaches (e.g., asking the model if it is correct) require labels/fine-tuning and can be brittle under distribution shift. The paper introduces an unsupervised, single-model method to estimate uncertainty in **meaning-space**, showing improved prediction of answer correctness on open- and closed-book QA.

### Methodology
The paper defines uncertainty for NLG as **predictive entropy** but argues the event space should be **semantic equivalence classes** (meanings) rather than raw sequences. Standard predictive entropy is
\[
PE(x)=H(Y\mid x)=-\int p(y\mid x)\ln p(y\mid x)\,dy \tag{1}
\]
For a language model, a sequence likelihood factors autoregressively:
\[
p(s\mid x)=\prod_i p(s_i\mid s_{<i},x).
\]
They introduce a semantic equivalence relation \(E(\cdot,\cdot)\) over sequences and its equivalence classes \(c\in C\) (each class = one meaning). The model’s **semantic likelihood** is the probability mass of all sequences with meaning \(c\):
\[
p(c\mid x)=\sum_{s\in c} p(s\mid x)=\sum_{s\in c}\prod_i p(s_i\mid s_{<i},x). \tag{2}
\]

**Algorithm (3-stage pipeline):**
1. **Generation:** Sample \(M\) sequences \(\{s^{(1)},\dots,s^{(M)}\}\sim p(\cdot\mid x)\) from a *single* off-the-shelf LLM using **multinomial sampling** or **multinomial beam sampling**. The paper emphasizes a sampling trade-off: higher temperature increases diversity but reduces average correctness; best uncertainty arises at an intermediate temperature (empirically \(T=0.5\) on TriviaQA).
2. **Semantic clustering (novel component):** Cluster sampled sequences into semantic classes via **bidirectional entailment** conditioned on the context \(x\). Two answers \(s,s'\) are equivalent iff \(x{+}s \Rightarrow x{+}s'\) *and* \(x{+}s' \Rightarrow x{+}s\). They implement entailment with a **DeBERTa-large** NLI model fine-tuned on **MNLI**, producing labels {entailment, neutral, contradiction}. Pairwise checks are reduced using transitivity and comparing only against cluster representatives (Algorithm 1 referenced). Manual validation on 300 generations yields semantic equivalence accuracy of **92.7% (TriviaQA)** and **95.5% (CoQA)**.
3. **Semantic entropy computation:** After clustering, sum likelihoods within each cluster and compute entropy over meanings:
\[
SE(x)=-\sum_{c} p(c\mid x)\log p(c\mid x)
=-\sum_{c}\left(\sum_{s\in c}p(s\mid x)\right)\log\left(\sum_{s\in c}p(s\mid x)\right). \tag{3}
\]
Since only sampled clusters are observed, estimate via Monte Carlo over sampled classes:
\[
SE(x)\approx -|C|^{-1}\sum_{i=1}^{|C|}\log p(C_i\mid x). \tag{4}
\]
They also study **length-normalization** (dividing sequence log-probability by length) as a heuristic to counteract the exponential decay of joint likelihood with output length; empirically its value depends on dataset answer-length properties.

**Inputs/outputs & preprocessing:** Input is a QA context \(x\) (question alone for closed-book; question + paragraph for open-book). Output is a scalar uncertainty score per question. Correctness for experiments is computed via fuzzy matching: an answer \(s\) is correct if \(\text{Rouge-L}(s,\text{ref})>0.3\) (and robustness checks with exact match / Rouge-1 are reported in appendix).

### Experiments & Results
**Goal:** evaluate whether uncertainty scores predict answer correctness. They frame uncertainty estimation as a binary ranking problem (“trust vs don’t trust this generation”) and use **AUROC**: the probability a randomly chosen correct answer has *lower* uncertainty than a randomly chosen incorrect answer (reported as “higher is better”, with 0.5 random and 1.0 perfect). They argue AUROC is more appropriate than calibration metrics like Brier score for free-form QA because calibrating would require summing probability mass over *all paraphrases* of the correct answer, which is intractable.

**Models:** OPT (GPT-like) (Zhang et al., 2022), sizes **2.7B, 6.7B, 13B, 30B** parameters; **no fine-tuning**, single model only (no ensembles, no Bayesian modifications).

**Datasets & splits:**
- **CoQA** (Reddy et al., 2019) open-book conversational QA: **development split ~8000 questions**.
- **TriviaQA** (Joshi et al., 2017) closed-book QA: **subset of 8000 questions** from the training split (chosen to match CoQA size).
They report model accuracies (for their generation/evaluation setup): **82.3% (CoQA)** vs **50.6% (TriviaQA)**, indicating TriviaQA is harder.

**Baselines compared:**
- **Predictive entropy** over sequences (Eq. 1 applied to sequence distribution).
- **Length-normalized predictive entropy** (Malinin & Gales, 2020), using mean log-probability per token.
- **p(True)** self-evaluation baseline (Kadavath et al., 2022): sample \(M\) answers, prompt the model to judge correctness; their implementation uses OPT up to 30B and is limited to **10-shot** (vs 20-shot in the original).
- **Lexical similarity** baseline: average pairwise Rouge-L similarity among sampled answers (analogous to diversity-based uncertainty; related to Fomicheva et al., 2020).
- Additional baselines (e.g., margin probability) are discussed in appendices.

**Main reported numbers (from Table 2; 30B OPT; 10 generations per question):**

| Dataset | Metric | Semantic entropy (AUROC) | # semantically distinct answers (AUROC) | Avg # clusters (correct) | Avg # clusters (incorrect) |
|---|---:|---:|---:|---:|---:|
| CoQA | AUROC | **0.77** | 0.66 | 1.27 | 1.77 |
| TriviaQA | AUROC | **0.83** | 0.79 | 1.89 | 3.89 |

**Key findings / ablations:**
- **Semantic entropy > sequence entropy baselines:** Across both datasets, semantic entropy more strongly predicts correctness than predictive entropy and length-normalized entropy (figures show widening gains with larger OPT sizes).
- **Scaling with model size:** Outperformance grows with model size; semantic entropy improves steadily from 2.7B → 30B and remains competitive for smaller models.
- **Sample efficiency & duplication handling:** Increasing number of samples improves semantic entropy more than length-normalized entropy because semantic clustering collapses paraphrase duplication; they show the performance gap widens as \(M\) increases (Fig. 3a). They claim **\(M<20\)** is often sufficient for effective uncertainty, contradicting assumptions that many more samples are needed.
- **Sampling temperature trade-off:** On TriviaQA, best AUROC is achieved at an **intermediate temperature \(T=0.5\)** (Fig. 3b): higher \(T\) increases diversity but decreases accuracy of samples; lower \(T\) increases accuracy but reduces semantic coverage. They note prior baseline implementations often use \(T=1.0\) (e.g., Kadavath et al., 2022), which can weaken entropy baselines.
- **Length normalization depends on dataset:** For TriviaQA (short reference answers), length normalization has little effect; for CoQA (mixed answer lengths), it matters more (Fig. 2).

**Computational considerations:** Semantic clustering requires up to \(\binom{M}{2}\) NLI comparisons, but cost is mitigated because (i) \(M\) can be small, (ii) DeBERTa-large is smaller than the LLM (noted as ~1.5B parameters), and (iii) transitivity reduces comparisons by checking only cluster representatives.

### Discussion & Conclusion
The paper argues that uncertainty in NLG should respect **semantic invariances**, and demonstrates that computing entropy over **meanings** (via semantic clustering + probability mass aggregation) better predicts QA correctness than token-sequence uncertainty and self-evaluation baselines. Limitations include reliance on an external NLI model (and its entailment errors) plus partial handling of “unimportant tokens” within a meaning. Future directions include extending semantic likelihoods to other probabilistic uncertainty tools (e.g., mutual information) and adapting semantic equivalence machinery to harder-evaluation tasks like summarization.

## Key Contributions
- Introduces **semantic entropy**, an uncertainty measure for NLG that computes entropy over **semantic equivalence classes** rather than raw sequences, using
  \[
  p(c\mid x)=\sum_{s\in c}p(s\mid x),\quad
  SE(x)=-\sum_c p(c\mid x)\log p(c\mid x).
  \]
- Proposes a practical **bidirectional entailment clustering** algorithm (context-conditioned) using an off-the-shelf **MNLI-tuned DeBERTa-large** NLI model; reports semantic-equivalence labeling accuracy **92.7% (TriviaQA)** / **95.5% (CoQA)** on a 300-sample manual check.
- Provides extensive empirical analysis showing semantic entropy improves **AUROC** for predicting QA correctness (e.g., **0.77 CoQA**, **0.83 TriviaQA** for 30B OPT) and studies key hyperparameters (sample count \(M\), temperature, and length normalization).

## Potential Relevance
For hypothesis development, this paper provides a concrete template for “**invariance-aware**” uncertainty: define an equivalence relation on outputs, marginalize probabilities within each equivalence class, then compute uncertainty over classes. The bidirectional-entailment clustering is a reusable mechanism for collapsing paraphrases in any generation-based metric (uncertainty, calibration proxies, self-consistency). The temperature and sample-count ablations are also practically useful: they suggest that improving uncertainty is often about **sampling strategy** as much as the uncertainty functional itself, and that **<20 samples** can suffice when semantic deduplication is applied.
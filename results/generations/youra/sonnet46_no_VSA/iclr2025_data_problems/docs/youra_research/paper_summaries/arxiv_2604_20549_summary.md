---
source_paper: "arxiv_2604_20549.md"
generated_at: "2026-07-30T06:14:23.167677"
model: "openai/gpt-5.2"
summary_chars: 12626
---

# Toward Cross-Lingual Quality Classifiers for Multilingual Pretraining Data Selection

## Key Metadata
- **Authors:** Yassine Turki et al.
- **Year:** 2026
- **Venue:** 3rd DATA-FM Workshop @ ICLR 2026
- **Core Contribution:** Shows that multilingual pooling plus harder-negative training (Q3) yields cross-lingually transferable data-quality classifiers that improve downstream LLM performance and rank stability, including transfer across distant language families.

## Section Summaries

### Abstract
As Large Language Models (LLMs) scale, data curation has shifted from maxi-
mizing volume to optimizing the signal-to-noise ratio by performing quality filter-
ing. However, for many languages, native high-quality data is insufficient to train
robust quality classifiers. This work investigates the idea that quality markers in
embedding space may show cross-lingual consistency, which would allow high-
resource languages to subsidize the filtering of low-resource ones. We evaluate
various filtering strategies, including cross-lingual transfer, third quartile sampling
(Q3), and retention rate tuning. Our results demonstrate that massive multilin-
gual pooling frequently outperforms monolingual baselines in both rank stability
and aggregate accuracy for a 1B model trained on 103B tokens, delivering gains
for high resource languages (1.2% increase in aggregate normalized accuracy for
French) and matching or exceeding monolingual baselines for low-resource lan-
guages. However, we find that scale alone does not guarantee stability. Further-
more, for high-resource languages like French, we show that refining the decision
boundary through third quartile sampling (Q3) or tuning the retention rate is nec-
essary to fully leverage the multilingual signal.

### Introduction & Motivation
The paper tackles multilingual *pretraining data selection* via model-based quality filtering, motivated by evidence that “more tokens” can underperform “better tokens” in LLM training. Prior pipelines (e.g., FineWeb-Edu, FineWeb2-HQ) train per-language quality classifiers, but many languages lack enough native high-quality positives to train robust standalone filters. The authors hypothesize that “quality” corresponds to language-agnostic markers (e.g., information density, coherence, lexical density) that may be consistent in a multilingual embedding space, enabling high-resource languages to subsidize low-resource filtering. They also argue that standard random negatives are too easy, motivating a harder-negative scheme (Q3) to sharpen decision boundaries—especially for high-resource languages where filtering is already strong.

### Methodology
The approach extends the **FineWeb2-HQ** model-based filtering pipeline by (i) enlarging the positive “anchor” pool and (ii) improving negative sampling.

**1) Data construction (classifier supervision).** They form a binary classification dataset: **positives** are “high-quality anchors,” while **negatives** come from the raw **FineWeb2** web crawl. Positives start from FineWeb2-HQ’s **MKC+** anchors (Multilingual MMLU, Aya Dataset/Collection, OpenAssistant-2, Include-Base-44) and are expanded to **MKC-e** with additional instruction/query + encyclopedic/synthetic sources: **Tagengo** (~75k conversations, 74 languages), **MURI-IT (Wikipedia subset)** (instruction-output across 200 languages; authors extract Wikipedia-style factual prose and exclude mixed-language samples), **EuroBlocks-SFT-Synthetic** (35 languages), and **WikiQA** (65 languages).

**2) Representation + preprocessing.** Each document is embedded with the **XLM-RoBERTa** encoder into a **768-d** vector (same encoder as FineWeb2-HQ). Minimal preprocessing is used: concatenate prompt/response when applicable; drop samples containing `<unk>` tokens.

**3) Sampling/balancing.** For training, they sample **100,000 positive documents per language** (vs. 80k in Messmer et al., 2025). To mitigate low-resource imbalance, positives may be **upsampled up to 3×**. They sample an equal number of negatives to keep classes balanced.

**4) Classifier architecture.** A lightweight **MLP** on top of embeddings: one hidden layer **256-d**, **ReLU**, **20% dropout**, and a **sigmoid** output producing a quality probability \(p(y{=}1\mid x)\).
A standard formulation consistent with their description is:
\[
h = \mathrm{Dropout}(\mathrm{ReLU}(W_1 x + b_1)),\quad
\hat{y} = \sigma(W_2 h + b_2)
\]
trained with binary cross-entropy:
\[
\mathcal{L} = -\big(y\log \hat{y} + (1-y)\log(1-\hat{y})\big)
\]
(Optimizer/schedule are not specified in the provided excerpt.)

**5) Two negative sampling strategies.**
- **Random negatives:** uniform sampling from FineWeb2 (baseline).
- **Q3 (“third quartile”) hard negatives:** bootstrap a preliminary classifier, score FineWeb2, then sample negatives from the **50th–75th percentile** of scores. These are intended to be *fluent but low-utility* (procedural/repetitive), forcing the model to separate true knowledge density from mere grammaticality.

**6) Filtering + retention.** A trained classifier scores FineWeb2 per language; data is kept above a threshold determined by a **retention rate** (e.g., 10%, 15%, etc.). The paper also studies retention-rate tuning per language.

### Experiments & Results
**Evaluation setup.** They evaluate filtering strategies by training a **1B-parameter Apertus** LLM (Apertus et al., 2025) on filtered FineWeb2 data. Training uses **103B tokens**, **sequence length 4096**, and each token is seen **at most twice**—except Arabic under aggressive filtering (10%, 20%) where they **replicate** filtered data **10×** or **5×** respectively to compensate for fewer tokens. Filtered document lists are “rehydrated” into text following FineWeb2 procedures (Penedo et al., 2025). Downstream evaluation uses **LM Evaluation Harness** (Gao et al., 2024) and reports **normalized accuracy** (“acc_norm”, per Kydlíček et al.) across multilingual tasks covering knowledge/reasoning/NLU; robustness is summarized by **average rank across benchmarks**, plus mean acc_norm.

**Compared strategies / baselines.**
- **No filtering:** random FineWeb2 sample (lower bound).
- **HQ:** monolingual FineWeb2-HQ-style classifier trained with **MKC+** anchors.
- **ML:** a **multilingual pooled** classifier trained across languages using **MKC-e**.
- **Q3:** monolingual HQ with Q3 hard negatives.
- **ML (Q3):** multilingual model bootstrapped with Q3 negatives.
- **Retention tuning:** e.g., 10% vs 15% for high-resource languages; Arabic also tested at 56% (FineWeb2-HQ default) vs 10/20% with replication.

**Key findings (by question).**

1) **Multilingual synergy (pooling helps).** On **Chinese**, ML beats HQ and no filtering in aggregate and rank stability: aggregate acc_norm **0.4236** (ML) vs **0.4190** (HQ) vs **0.4024** (no filtering), and average rank **1.31** (ML) vs **1.77** (HQ) vs **2.85**. On **Spanish**, ML similarly improves: aggregate acc_norm **0.3855** vs **0.3753** (HQ) vs **0.3635** (no filtering), average rank **1.14** vs **2.00** vs **2.86**.

2) **Cross-lingual transfer across distant families.** They score French FineWeb2 with family-trained classifiers and compute rank correlations vs the French HQ baseline. Surprisingly, a **Nordic-family** classifier correlates almost as strongly as Romance: **Spearman ρ = 0.8820**, **Kendall τ = 0.6990** vs **Romance (incl. French) ρ = 0.8928**, **τ = 0.7173**. Removing French from Romance drops markedly (**ρ = 0.7139**, **τ = 0.5228**), which the authors interpret as potential *syntactic interference* (overfitting to related-but-not-identical Romance patterns). In downstream French LLM training (10% retention), **Nordic filtering** yields aggregate acc_norm **0.4151**, outperforming **HQ** at **0.4089** (though average rank differs: **2.25** vs **2.12**).

3) **Decision boundary refinement via Q3 improves high-resource performance.** For **French**, switching to Q3 negatives yields aggregate acc_norm **0.4167** (Q3) vs **0.4089** (HQ) and improves average rank **2.00** vs **3.00**. For **Spanish**, ML(Q3) improves over ML: acc_norm **0.3887** vs **0.3855**, and average rank **1.14** vs **2.00**.

4) **Retention rate tuning matters.** With ML on **French**, increasing retention from **10% → 15%** raises aggregate acc_norm from **0.4064 → 0.4209** and improves average rank **1.62 → 1.25**. Spanish shows a similar pattern: **0.3855 → 0.3897** and rank **1.71 → 1.29**. For **Arabic**, aggressive downsampling with replication hurts relative to the default high retention: at **56%**, HQ acc_norm **0.3708** vs HQ(10%) **0.3664** and HQ(20%) **0.3652**; ML at 56% is best among Arabic runs in their table (ML acc_norm **0.3758**, rank **2.31**). They caution that Arabic ML vs HQ gain (~**+0.5%**) is comparable to reported seed variance (~**0.3%**), calling for multi-seed validation.

**Main result table (aggregate only).**

| Language / Setting | No filtering (acc_norm, rank) | HQ (acc_norm, rank) | ML (acc_norm, rank) | Best variant highlighted |
|---|---:|---:|---:|---|
| Chinese (10%) | 0.4024, 2.85 | 0.4190, 1.77 | **0.4236, 1.31** | ML |
| Spanish (10%) | 0.3635, 2.86 | 0.3753, 2.00 | **0.3855, 1.14** | ML |
| French (10%) | 0.3954, 3.50 | 0.4089, 2.12 | 0.4064, 3.00 | Q3 variants better |
| French Q3 (10%) | — | 0.4089, 3.00 | 0.4147, 2.38 (ML Q3) | **0.4167, 2.00 (Q3 mono)** |
| Spanish Q3 (10%) | — | 0.3753, 2.86 | 0.3887, 1.14 (ML Q3) | **ML(Q3)** |
| French retention (ML) | — | — | 0.4064 (10%) → **0.4209 (15%)** | ML(15%) |
| Spanish retention (ML) | — | — | 0.3855 (10%) → **0.3897 (15%)** | ML(15%) |
| Arabic (56%) | — | 0.3708, 3.62 | **0.3758, 2.31** | ML (note seed variance caveat) |

**Overall aggregation (10% retention across languages, Table 10).** ML(Q3) is best on both macro and micro summaries:
- **Macro rank:** ML(Q3) **1.6983** < ML **1.9808** < HQ **2.4556** < No filtering **3.7248**
- **Micro rank:** ML(Q3) **1.7857** < ML **1.9286** < HQ **2.4286** < No filtering **3.7143**
- **Macro acc_norm:** ML(Q3) **0.4082** (best), ML **0.4052**, HQ **0.4011**, No filtering **0.3871**
- **Micro acc_norm:** ML(Q3) **0.4113** (best), ML **0.4092**, HQ **0.4052**, No filtering **0.3907**

**Stability / stochasticity.** They note that while multilingual pooling improves *rank stability*, downstream acc_norm remains sensitive to the classifier sampling seed (reported shifts: **0.8% in French**, **0.3% in Arabic**), implying careful evaluation (e.g., multi-seed) is important.

### Discussion & Conclusion
The paper provides evidence that multilingual embedding spaces (XLM-R) contain transferable “quality” signals: pooled multilingual classifiers often outperform monolingual ones and can even generalize across distant language families (e.g., Nordic → French). However, pooling alone is not uniformly optimal; high-resource languages benefit from *boundary refinement* (Q3 hard negatives) and *retention-rate tuning*, and results can be seed-sensitive. The authors conclude that combining multilingual pooling with Q3 bootstrapping (**ML(Q3)**) is the most robust overall strategy, helping “democratize” high-quality filtering for low-resource languages.

## Key Contributions
- Demonstrates **massive multilingual pooling** for quality classification can improve downstream LLM performance and rank stability vs monolingual FineWeb2-HQ-style baselines (e.g., Chinese acc_norm **0.4236** ML vs **0.4190** HQ; Spanish rank **1.14** ML vs **2.00** HQ).
- Provides **empirical cross-family transfer** evidence: family-trained classifiers (including distant **Nordic**) correlate strongly with French HQ rankings (**Spearman 0.8820**) and can match/exceed French-native filtering in downstream acc_norm.
- Introduces **Q3 hard-negative sampling** (50th–75th percentile negatives) and shows it **sharpens decision boundaries**, improving high-resource language outcomes; plus highlights **retention rate** as a crucial language-dependent hyperparameter (French ML **10%→15%**: **0.4064→0.4209**).

## Potential Relevance
For hypothesis development on multilingual data curation, this paper supports the idea that “quality” is at least partly **language-agnostic in representation space**, enabling cross-lingual subsidy (train filters where positives exist; apply elsewhere). The **Q3 bootstrapping** recipe is a practical, low-cost way to improve classifier precision once random negatives become too easy, and their retention-rate results suggest that fixed thresholds (e.g., 10%) may be systematically suboptimal—useful when designing adaptive filtering policies per language/resource regime.
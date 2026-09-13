# Research Proposal: Code-Switching Augmented Safety Alignment for Multilingual Large Language Models

## 1. Title

**Code-Switching Augmented Safety Alignment: Learning Language-Invariant Safety Representations for Equitable Multilingual LLM Safety**

---

## 2. Introduction

### 2.1 Background

Large Language Models (LLMs) have achieved remarkable capabilities across diverse natural language tasks, yet their deployment raises significant safety concerns. Current safety alignment mechanisms—designed to prevent models from generating harmful, biased, or dangerous content—are predominantly developed using English-language data and evaluation frameworks. This monolingual bias creates a critical vulnerability: safety mechanisms that perform robustly on English inputs often fail catastrophically when users employ multilingual strategies, particularly code-switching.

Code-switching, the practice of alternating between two or more languages within a single conversation or utterance, is a natural linguistic phenomenon practiced by over half of the world's population. Recent research has revealed that adversarial prompts employing code-switching achieve attack success rates 46.7% higher than equivalent monolingual attacks. This vulnerability arises because safety classifiers trained predominantly on English data fail to recognize harmful intent when it is expressed through mixed-language surface forms. The implications are twofold: first, malicious actors can exploit this gap to bypass safety mechanisms; second, legitimate multilingual users—particularly speakers of low-resource languages—experience inequitable safety coverage, receiving either inadequate protection or excessive false refusals.

The root cause of this vulnerability lies in the representation learning paradigm of current safety alignment approaches. Existing methods learn safety-relevant features that are entangled with language-specific surface forms rather than capturing the underlying semantic intent. When confronted with code-switched inputs that combine linguistic elements in novel ways, these representations fail to generalize, leaving models unable to recognize familiar harmful patterns in unfamiliar linguistic packaging.

### 2.2 Research Objectives

This research proposes Code-Switching Augmented Safety Alignment (CSASA), a novel training methodology designed to develop language-invariant safety representations that generalize robustly across linguistic variations. Our specific objectives are:

1. **Primary Objective:** Develop a linguistically-principled code-switching augmentation framework that generates training data following established sociolinguistic patterns (inter-sentential, intra-sentential, and tag-switching) across strategically selected language pairs.

2. **Secondary Objective:** Design and implement a contrastive learning approach that forces safety encoders to learn semantic intent rather than surface linguistic form, producing language-invariant safety embeddings.

3. **Tertiary Objective:** Empirically validate that CSASA reduces code-switching attack success rates by at least 30% and improves safety classification performance on low-resource languages by at least 40%, while maintaining acceptable false refusal rates.

### 2.3 Significance

This research addresses critical gaps in socially responsible language modeling across multiple dimensions:

**Security and Robustness:** By closing the code-switching vulnerability, CSASA directly addresses exploitable security gaps that malicious actors currently leverage to bypass safety mechanisms.

**Fairness and Equity:** Multilingual speakers, particularly those using low-resource languages, currently receive inequitable safety coverage. CSASA promotes fairness by ensuring safety mechanisms generalize across linguistic communities.

**Practical Deployment:** Unlike approaches requiring fundamental changes to pretraining, CSASA operates as a fine-tuning intervention, making it practically deployable for existing models without prohibitive computational costs.

**Scientific Contribution:** This work advances understanding of cross-lingual representation learning in the safety domain, providing insights into how semantic intent can be disentangled from surface linguistic form.

---

## 3. Methodology

### 3.1 Overview

CSASA operates through a three-stage pipeline: (1) linguistically-principled code-switching data generation, (2) contrastive safety representation learning, and (3) safety-aligned fine-tuning. We detail each component below.

### 3.2 Stage 1: Linguistically-Principled Code-Switching Generation

#### 3.2.1 Language Pair Selection

We select five strategic language pairs to maximize typological diversity and coverage:
- **English-Chinese:** Sino-Tibetan family, logographic script
- **English-Spanish:** Indo-European family, high-resource
- **English-Hindi:** Indo-Aryan branch, Devanagari script
- **English-Arabic:** Semitic family, right-to-left script
- **English-Swahili:** Niger-Congo family, low-resource

#### 3.2.2 Code-Switching Pattern Types

Following sociolinguistic research, we implement three principled code-switching patterns:

**Inter-sentential switching:** Language alternation occurs at sentence boundaries, maintaining grammatical integrity within each sentence.

$$S_{inter} = [s_1^{L_1}, s_2^{L_2}, s_3^{L_1}, ...]$$

where $s_i^{L_j}$ denotes sentence $i$ in language $L_j$.

**Intra-sentential switching:** Language alternation occurs within sentences at grammatically permissible points (e.g., between noun phrases and verb phrases).

$$S_{intra} = [w_1^{L_1}, ..., w_k^{L_1}, w_{k+1}^{L_2}, ..., w_n^{L_2}]$$

where switching occurs at syntactic boundaries respecting the Matrix Language Frame model.

**Tag-switching:** Short phrases, interjections, or discourse markers are inserted from an alternate language.

$$S_{tag} = [s^{L_1}[tag^{L_2}]]$$

#### 3.2.3 Generation Algorithm

Given a source safety-relevant text $T$ in English, we generate code-switched variants as follows:

```
Algorithm 1: Linguistically-Principled Code-Switching Generation
Input: Source text T, target language L_t, pattern type P
Output: Code-switched text T_cs

1. Parse T to obtain syntactic structure tree S
2. Identify valid switching points V based on pattern P:
   - If P = inter-sentential: V = sentence boundaries
   - If P = intra-sentential: V = clause/phrase boundaries
   - If P = tag-switching: V = discourse marker positions
3. For each switching point v ∈ V:
   a. Extract segment seg_v following v
   b. Translate seg_v to L_t using neural MT with quality filtering
   c. Verify grammatical compatibility at boundary
   d. If compatible: replace seg_v with translation
4. Apply morphological smoothing at boundaries
5. Return T_cs
```

Quality filtering employs back-translation consistency: we retain translations where $\text{BLEU}(T, \text{BackTranslate}(\text{Translate}(T))) > 0.7$.

### 3.3 Stage 2: Contrastive Safety Representation Learning

#### 3.3.1 Architecture

We employ XLM-RoBERTa (XLM-R) as our multilingual encoder backbone, adding a safety-specific projection head:

$$h = \text{MLP}(\text{XLM-R}(x))$$

where $h \in \mathbb{R}^d$ is the safety embedding and $d = 256$.

#### 3.3.2 Contrastive Learning Objective

For each safety-relevant example, we construct positive pairs from semantically equivalent code-switched variants and negative pairs from semantically distinct examples. Let $x_i$ be an original text and $\{x_i^{cs_1}, x_i^{cs_2}, ..., x_i^{cs_k}\}$ be its code-switched variants.

The contrastive loss is defined as:

$$\mathcal{L}_{contrast} = -\sum_{i} \log \frac{\sum_{j} \exp(\text{sim}(h_i, h_i^{cs_j})/\tau)}{\sum_{j} \exp(\text{sim}(h_i, h_i^{cs_j})/\tau) + \sum_{n \in N_i} \exp(\text{sim}(h_i, h_n)/\tau)}$$

where $\text{sim}(a, b) = \frac{a \cdot b}{\|a\| \|b\|}$ is cosine similarity, $\tau = 0.07$ is the temperature parameter, and $N_i$ is the set of negative examples for sample $i$.

#### 3.3.3 Safety Classification Head

Simultaneously, we train a safety classification head:

$$\hat{y} = \sigma(W_c \cdot h + b_c)$$

with binary cross-entropy loss:

$$\mathcal{L}_{safety} = -\sum_{i} [y_i \log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)]$$

#### 3.3.4 Combined Training Objective

The final training objective combines both losses:

$$\mathcal{L}_{total} = \mathcal{L}_{safety} + \lambda \mathcal{L}_{contrast}$$

where $\lambda = 0.5$ balances the two objectives.

### 3.4 Stage 3: Safety-Aligned Fine-Tuning

The trained safety encoder is integrated into the target LLM's safety pipeline. For generative models, we employ the safety embeddings as an input filter:

$$\text{Response} = \begin{cases} \text{LLM}(x) & \text{if } \hat{y} < \theta_{safe} \\ \text{Refusal} & \text{otherwise} \end{cases}$$

where $\theta_{safe}$ is calibrated to achieve target false refusal rates.

### 3.5 Experimental Design

#### 3.5.1 Conditions

We evaluate three training conditions:

1. **Baseline (English-only):** Safety encoder trained exclusively on English safety data
2. **Random Code-Switching:** Safety encoder trained with randomly generated code-switched data (no linguistic constraints)
3. **CSASA (Proposed):** Safety encoder trained with linguistically-principled code-switched data

#### 3.5.2 Datasets

**Training Data:**
- English safety preference pairs from Anthropic HH-RLHF (50,000 examples)
- Generated code-switched variants (250,000 examples across 5 language pairs × 3 patterns)

**Evaluation Benchmarks:**
- **CSRT (Code-Switching Red-Teaming):** 2,000 adversarial code-switched prompts
- **LinguaSafe:** Multilingual safety classification benchmark (10 languages)
- **SGToxicGuard:** Toxicity detection across 8 languages
- **Benign Multilingual Queries:** 1,000 non-harmful multilingual queries for false refusal measurement

#### 3.5.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Attack Success Rate (ASR) | % of adversarial prompts eliciting unsafe responses | ≤40% (≥30% reduction) |
| Safety F1 | F1 score on safety classification | ≥40% improvement on low-resource |
| False Refusal Rate (FRR) | % of benign queries incorrectly refused | ≤5% increase |
| Cross-Lingual Transfer Gap | Performance difference: high-resource vs low-resource | ≤10% |

#### 3.5.4 Statistical Analysis

For primary hypothesis testing (ASR reduction), we employ a two-proportion z-test:

$$z = \frac{\hat{p}_1 - \hat{p}_2}{\sqrt{\hat{p}(1-\hat{p})(\frac{1}{n_1} + \frac{1}{n_2})}}$$

with $\alpha = 0.05$ and minimum sample size $n = 500$ per condition to achieve power $\beta = 0.80$.

For secondary metrics, we use paired t-tests comparing CSASA against baselines across language-specific performance.

#### 3.5.5 Ablation Studies

1. **Pattern Ablation:** Evaluate contribution of each code-switching pattern type
2. **Language Pair Ablation:** Assess impact of individual language pairs
3. **Contrastive Loss Ablation:** Compare with classification-only training
4. **Data Scale Ablation:** Vary augmentation ratio from 1× to 10×

#### 3.5.6 Mechanism Validation

To verify the hypothesized mechanism (language-invariant representations), we conduct:

1. **Embedding Analysis:** Compute average pairwise cosine similarity between embeddings of semantically equivalent texts across languages. CSASA should show higher similarity than baselines.

2. **Probing Tasks:** Train linear probes to predict source language from safety embeddings. CSASA embeddings should be less predictive of language.

3. **t-SNE Visualization:** Visualize embedding spaces to confirm semantic clustering rather than language clustering.

### 3.6 Implementation Details

- **Hardware:** 8× NVIDIA A100 GPUs
- **Training Time:** Estimated 4-8 GPU-days for contrastive encoder
- **Batch Size:** 256 with gradient accumulation
- **Optimizer:** AdamW with learning rate 2e-5, linear warmup over 10% of steps
- **Epochs:** 10 with early stopping based on validation loss

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome (H-CSASA-v1 Validation):**
We expect CSASA to achieve attack success rates on code-switched prompts at least 30% lower than English-only trained models. Specifically, we anticipate reducing ASR from the baseline ~70% (as reported in CSRT) to ≤40%.

**Secondary Outcomes:**
1. Safety classification F1 on low-resource languages (Hindi, Arabic, Swahili) will improve by ≥40% compared to English-only baselines
2. Linguistically-principled code-switching will outperform random code-switching by ≥15% on all metrics
3. Cross-lingual transfer gap will reduce from 20-30% to ≤10%
4. False refusal rates will increase by no more than 5%

**Mechanism Validation:**
Embedding analysis will confirm that CSASA produces representations where semantic similarity dominates over linguistic similarity, with language prediction probes achieving near-chance accuracy.

### 4.2 Scientific Impact

This research contributes to multiple areas of socially responsible language modeling:

**Theoretical Contribution:** We provide empirical evidence for the hypothesis that safety-relevant semantic intent can be disentangled from surface linguistic form through targeted contrastive learning, advancing understanding of cross-lingual representation learning.

**Methodological Contribution:** The linguistically-principled code-switching generation framework offers a reusable tool for multilingual NLP research, grounded in sociolinguistic theory rather than ad-hoc augmentation.

**Benchmark Contribution:** Our evaluation framework and generated datasets will be released to facilitate future research on multilingual LLM safety.

### 4.3 Societal Impact

**Equity in AI Safety:** By ensuring safety mechanisms generalize across languages, CSASA promotes equitable protection for multilingual users, particularly speakers of low-resource languages who are currently underserved.

**Security Enhancement:** Closing the code-switching vulnerability reduces the attack surface available to malicious actors, improving the overall security posture of deployed LLMs.

**Responsible Deployment:** CSASA provides a practical, deployable intervention that organizations can adopt without fundamental architectural changes, lowering barriers to responsible multilingual LLM deployment.

### 4.4 Limitations and Future Work

We acknowledge several limitations: (1) our approach focuses on text modality and does not address speech-based code-switching; (2) cultural variations in safety norms are not fully captured; (3) languages without adequate XLM-R tokenizer coverage remain challenging. Future work will extend CSASA to multimodal settings, incorporate culturally-aware safety definitions, and explore adaptation strategies for extremely low-resource languages.

### 4.5 Ethical Considerations

This research aims to improve LLM safety but involves generating adversarial examples. All generated attack data will be handled responsibly, with access restricted to research purposes. We will engage native speakers for validation to ensure cultural appropriateness and avoid perpetuating stereotypes in generated code-switched data.

---

**Word Count:** ~2,150 words
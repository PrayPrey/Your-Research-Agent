---
source_paper: "arxiv_2504_13677.md"
generated_at: "2026-08-02T15:23:25.354400"
model: "openai/gpt-5.2"
summary_chars: 13821
---

# Revisiting Uncertainty Estimation Evaluation: Length Bias Distorts AUROC Rankings

## Key Metadata
- **Authors:** Andrea Santilli et al.
- **Year:** 2025 (arXiv:2504.13677)
- **Venue:** arXiv preprint
- **Core Contribution:** Shows (theoretically and empirically) that *mutual bias* between correctness functions and UQ scores (notably response-length bias) can systematically skew AUROC-based rankings of uncertainty estimation methods, and argues LM-as-a-judge correctness functions are more reliable for UQ evaluation.

## Section Summaries

### Abstract
Uncertainty Quantification (UQ) in Language
Models (LMs) is key to improving their safety
and reliability. Evaluations often use metrics
like AUROC to assess how well UQ methods
(e.g., negative sequence probabilities) correlate
with task correctness functions (e.g., ROUGE-
L). We show that mutual biases-when both UQ
methods and correctness functions are biased
by the same factors-systematically distort evalu-
ation. First, we formally prove that any mutual
bias non-randomly skews AUROC rankings,
compromising benchmark integrity. Second,
we confirm this happens empirically by test-
ing 7 widely used correctness functions, from
lexical-based and embedding-based metrics to
LM-as-a-judge approaches, across 4 datasets ×
4 models × 8 UQ methods. Our analysis shows
that length biases in correctness functions dis-
tort UQ assessments by interacting with length
biases in UQ methods. We identify LM-as-a-
judge methods as the least length-biased, offer-
ing a promising path for a fairer UQ evaluation.

### Introduction & Motivation
LMs frequently generate incorrect content (“hallucinations”), and UQ methods are used to flag such errors when uncertainty tends to be higher on incorrect outputs. Because ground-truth uncertainty labels are typically unavailable, UQ methods are commonly evaluated by how well their uncertainty scores separate “correct” vs “incorrect” outputs according to an *automatic correctness function* (e.g., ROUGE-L), using AUROC. The paper argues that this evaluation protocol can fail systematically when the correctness function’s errors are *not independent* of the UQ method—i.e., when both share a confounder. The authors focus on response length as a particularly severe, empirically prevalent confounder that can invert or distort AUROC-based rankings of UQ methods.

### Methodology
The paper studies UQ evaluation as a pipeline that (1) generates an answer \(\hat{y}\) for each input \(x\), (2) computes a scalar uncertainty score \(\hat{g}(\hat{y},x)\), (3) computes a correctness score \(\hat{h}(\hat{y},x,y)\) against reference \(y\), (4) binarizes correctness via a threshold \(t\) if needed, and (5) computes AUROC between uncertainty and correctness labels. The central methodological contribution is an error/bias analysis of AUROC when the correctness label is *estimated* rather than ground-truth.

**UQ methods (inputs/outputs, and length dependence).** Given \(x\) and generated \(\hat{y}=(\hat{y}_1,\dots,\hat{y}_L)\), a canonical single-sample uncertainty score is negative sequence probability:
\[
\hat{g}(\hat{y}, x) = -\hat{p}(\hat{y}\mid x)= -\prod_{i=1}^{L} \hat{p}(\hat{y}_i \mid \hat{y}_{<i}, x),
\tag{1}
\]
which increases with sequence length \(L\) since each token probability term is \(<1\). The study benchmarks **8 UQ methods** (plus length-only baselines used as diagnostics): perplexity; negative sequence probability (Eq. 1); Naïve Entropy; Mean Token Entropy; Semantic Entropy with length normalization; Semantic Entropy without length normalization; and two learned “probe” classifiers trained to predict correctness labels (“Probe (RougeL-F1 > 0.5)” and “Probe (LM-as-a-judge)”). While many implementation details live in appendices (not provided in the excerpt), the key methodological point is that several UQ estimators either explicitly include Eq. (1) or depend on token-level likelihoods/entropies, creating *systematic correlations with response length*.

**Correctness functions (surrogate labels) and binarization.** The correctness function \(\hat{h}(\hat{y},x,y)\) is chosen from 3 families: lexical overlap (ROUGE-1 (F1), ROUGE-L (F1), ROUGE-L (Recall), SQuAD (F1)), embedding similarity (BERTScore (F1), Sentence-BERT cosine similarity), and LM-as-a-judge (prompt-based judge; AlignScore). Because AUROC typically needs binary labels, continuous correctness scores are thresholded at \(t\). The paper highlights that standard practice uses fixed or lightly tuned thresholds (e.g., ROUGE-L(F1) \(t\in\{0.1,0.3,0.5\}\), SentenceBERT \(t\in\{0.4,0.9\}\), BERTScore(F1) \(t=0.8\), SQuAD(F1) \(t=0.3\), AlignScore \(t=0.5\), ROUGE-L(Recall) \(t=1.0\); some LM-judge variants are inherently binary or treated as such).

**UQ metric and the “mutual bias” mechanism.** With *true* correctness labels \(h_i\in\{0,1\}\), AUROC is:
\[
\text{AUROC} = \mathbb{P}\big(\hat{g}_i < \hat{g}_j \mid h_i = 1,\, h_j = 0\big),
\tag{2}
\]
i.e., the probability a random correct sample receives lower uncertainty than a random incorrect sample. In practice labels are \(\hat{h}_i\) from a correctness function, yielding an *estimated* AUROC:
\[
\widehat{\text{AUROC}} = \mathbb{P}\big(\hat{g}_i < \hat{g}_j \mid \hat{h}_i = 1,\, \hat{h}_j = 0\big).
\tag{3}
\]
The methodological (theoretical) analysis distinguishes two regimes: **(i) uncorrelated correctness errors**, where \(\hat{h}\) is noisy but errors are independent of \(\hat{g}\), making \(\widehat{\text{AUROC}}\) a noisy but *unbiased* estimator (worst-case regressing toward 0.5 without systematically favoring any UQ method); versus **(ii) mutually biased errors**, where correctness function errors correlate with \(\hat{g}\) through a shared confounder (e.g., length), which *systematically biases* \(\widehat{\text{AUROC}}\) and thus *skews AUROC-based rankings* across UQ methods. The paper’s “why” is to argue that benchmark conclusions about which UQ method is best can be artifacts of correctness-function choice, especially under mutual bias.

**Hyperparameters/training details.** The excerpt notes learned “probe” methods are trained via supervised binary classification on correctness-labeled data (per Kadavath et al., 2022), but does not report architecture, optimizer, learning rate, batch size, or epochs in the provided text (these are presumably in appendices).

### Experiments & Results
**Overall design.** The empirical study holds the UQ evaluation protocol constant while varying *only* the correctness function, to test whether UQ rankings are stable. They benchmark **8 UQ methods** across **4 datasets × 4 models × 7 correctness functions** (the excerpt points to appendices for exact model/dataset identities and prompts; the main text states the task is **generative QA** to keep correctness evaluation relatively well-defined compared to more open-ended tasks). A key observed phenomenon (Fig. 1) is that changing the correctness function changes not just absolute AUROC values but the *ordering* of UQ methods—evidence that the correctness function is not a neutral measurement device.

**Correctness functions evaluated.** The paper evaluates 7 widely used correctness functions spanning:
- **Lexical-based:** ROUGE-1 (F1), ROUGE-L (F1), ROUGE-L (Recall), SQuAD (F1)
- **Embedding-based:** BERTScore (F1), SentenceBERT similarity
- **LM-as-a-judge:** AlignScore; prompt-based LM-as-a-judge (the text treats these as “LM-as-a-judge approaches” and reports them as least length-biased)

Thresholding choices (needed for AUROC binarization) are explicitly varied and shown to strongly affect alignment with humans for some metrics. Examples appearing in the figures/tables include ROUGE-L(F1) at \(t\in\{0.1,0.3,0.5\}\), SentenceBERT at \(t\in\{0.4,0.9\}\), and ROUGE-1(F1) at \(t=0.1\). The paper emphasizes that “optimal thresholds vary across tasks” and are “heavily influenced by response verbosity,” leading to brittleness and even degenerate labeling (nearly-all-0 or nearly-all-1), which then contaminates AUROC.

**Human evaluation to diagnose correctness-function error.** To ground the analysis, the authors collect human correctness judgments for **450 LM samples**, annotated by **four annotators per sample**, and measure agreement between correctness functions and humans using **Cohen’s \(\kappa\)** (Fig. 2). Result: **LM-as-a-judge approaches (prompt-based and AlignScore)** align best with human labelers; **ROUGE-L (Recall) with \(t=1\)** is next-best but still worse and susceptible to other failure modes. Most lexical/embedding metrics are reported to “poorly reflect human judgment,” especially under common thresholds.

**Diagnosing mutual bias via length correlations.**
1. **UQ methods vs length:** The authors compute **Spearman rank correlations** between UQ scores and answer length (tokens and characters). Fig. 4 reports several substantial correlations, with magnitudes reaching approximately \(|\rho|\approx 0.9\) in the displayed correlation matrix, consistent with the expectation that Eq. (1)-based methods and related entropy/probability methods depend on \(L\).
2. **Correctness functions vs length:** They plot correctness score versus response length for cases where all annotators agree (Fig. 5). **ROUGE-L(F1)** is shown to be strongly length-dependent (favoring shorter answers, making thresholding hard), whereas **AlignScore** is comparatively length-independent and separates correct vs incorrect more cleanly in the shown plot.

**Main empirical claim (ranking distortion).** When correctness functions are length-biased (many lexical/embedding metrics), simple length baselines (token/character length) can appear “competitively” good under AUROC, and UQ methods that correlate with length (e.g., negative sequence probability, perplexity, some probes) can be artificially advantaged or penalized. Under LM-as-a-judge correctness functions (lower length bias + higher human alignment), these length baselines “rank last,” indicating the prior apparent performance was an artifact of mutual bias.

**Compact table of key *reported* quantitative facts (from the excerpt).**

| Category | Quantity / Setting | Reported value(s) |
|---|---:|---|
| Benchmark grid | Datasets × Models × UQ methods × correctness functions | \(4 \times 4 \times 8 \times 7\) |
| Human study size | Samples | 450 |
| Human labeling density | Annotators per sample | 4 |
| UQ metric | Definition | Eq. (2) AUROC; Eq. (3) estimated \(\widehat{\text{AUROC}}\) |
| Illustrative correctness thresholds used in UQ evals | ROUGE-L(F1) | \(t\in\{0.1,0.3,0.5\}\) |
|  | SentenceBERT | \(t\in\{0.4,0.9\}\) |
|  | BERTScore(F1) | \(t=0.8\) |
|  | SQuAD(F1) | \(t=0.3\) |
|  | ROUGE-1(F1) | \(t=0.1\) |
|  | AlignScore | \(t=0.5\) |
|  | ROUGE-L(Recall) | \(t=1.0\) |
| Length–score dependence diagnostic | Spearman correlation magnitudes (shown) | up to \(|\rho|\approx 0.9\) (Fig. 4 matrix) |

**Baselines compared.** The excerpt explicitly frames comparisons across UQ methods and includes length-only “baselines” (token length, character length) as diagnostic controls; it also situates correctness functions and UQ methods in the context of prior UQ benchmarking work (e.g., Farquhar et al., 2024; Fadeeva et al., 2023; Chen et al., 2024a), but does not list numeric AUROC per baseline in the provided text (values are shown in figures but not transcribed).

**Compute cost.** The excerpt notes LM-as-a-judge has “significant computational overhead” vs traditional correctness functions, but does not provide GPU-hour or latency numbers.

### Discussion & Conclusion
The paper’s main takeaway is that AUROC-based UQ benchmarks can be *systematically* (not just noisily) distorted whenever the correctness function and UQ method share a confounder; response length is empirically demonstrated as one such confounder that already affects common QA-based UQ evaluations. Lexical/embedding correctness functions—especially when thresholded—are particularly prone to length bias and threshold brittleness, whereas LM-as-a-judge approaches (including AlignScore) align better with human judgments and appear less length-biased. Limitations include focusing on QA (though the authors argue the issue generalizes), the known failure modes and prompt/model sensitivity of LM-as-a-judge, potential bias if the same LM participates in both the UQ method and the judge, and the possibility of other latent confounders beyond length.

## Key Contributions
- Provides a formal analysis showing that **mutual bias** (correlated errors between correctness function and UQ scores) can **systematically skew AUROC** and therefore distort UQ method rankings.
- Conducts a broad empirical benchmark (**4 datasets × 4 models × 8 UQ methods × 7 correctness functions**) showing that changing correctness functions can **substantially change AUROC rankings**.
- Identifies **response length** as a concrete mutual confounder driving spurious performance, and finds **LM-as-a-judge/AlignScore** correctness functions are **most aligned with human judgments** and least length-biased among those tested.

## Potential Relevance
If you are developing or comparing UQ methods (especially likelihood/entropy-based ones), this paper is a caution that AUROC improvements may be artifacts of the *correctness proxy* rather than genuine uncertainty quality. It motivates incorporating (i) human validation of correctness functions, (ii) length-bias diagnostics (e.g., Spearman correlation with length), and (iii) LM-as-a-judge or otherwise debiased correctness labeling when building UQ benchmarks. It also suggests a general hypothesis: any shared latent variable (style, verbosity, vocabulary) between judge and UQ signal can produce spurious AUROC gains, so evaluation protocols should explicitly test for such confounding.
---
source_paper: "arxiv_2111_02840.md"
generated_at: "2026-07-29T11:52:07.342588"
model: "openai/gpt-5.2"
summary_chars: 10538
---

# Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models

## Key Metadata
- **Authors:** Boxin Wang et al.
- **Year:** 2021
- **Venue:** NeurIPS 2021 (Track on Datasets and Benchmarks)
- **Core Contribution:** Introduces **AdvGLUE**, a curated adversarial counterpart of GLUE built by applying **14 textual attack methods** plus systematic **human validation**, enabling standardized multi-task robustness evaluation of language models.

## Section Summaries

### Abstract
Large-scale pre-trained language models have achieved tremendous success across
a wide range of natural language understanding (NLU) tasks, even surpassing
human performance. However, recent studies reveal that the robustness of these
models can be challenged by carefully crafted textual adversarial examples. While
several individual datasets have been proposed to evaluate model robustness, a
principled and comprehensive benchmark is still missing. In this paper, we present
Adversarial GLUE (AdvGLUE), a new multi-task benchmark to quantitatively
and thoroughly explore and evaluate the vulnerabilities of modern large-scale
language models under various types of adversarial attacks. In particular, we
systematically apply 14 textual adversarial attack methods to GLUE tasks to
construct AdvGLUE, which is further validated by humans for reliable annotations.
(i) Most existing adversarial attack
Our ﬁndings are summarized as follows.
algorithms are prone to generating invalid or ambiguous adversarial examples, with
around 90% of them either changing the original semantic meanings or misleading
human annotators as well. Therefore, we perform careful ﬁltering process to
curate a high-quality benchmark. (ii) All the language models and robust training
methods we tested perform poorly on AdvGLUE, with scores lagging far behind
the benign accuracy. We hope our work will motivate the development of new
adversarial attacks that are more stealthy and semantic-preserving, as well as new
robust language models against sophisticated adversarial attacks. AdvGLUE is
available at https://adversarialglue.github.io.

### Introduction & Motivation
Pretrained LMs reach near-saturated performance on IID benchmarks like GLUE, but multiple works show they remain brittle to small, human-imperceptible perturbations that can flip predictions—posing real security and reliability risks. Robust-training papers evaluate under inconsistent adversary definitions (human-crafted vs. automatic attacks), making cross-paper comparisons unreliable. The paper targets this gap by proposing a **unified, principled robustness benchmark** that is (1) **human-validated** (to avoid label noise/semantic drift), (2) **comprehensive** across linguistic phenomena and attack types, and (3) **challenging and transferable** across model families.

### Methodology
AdvGLUE is constructed as an **adversarial test benchmark** spanning five GLUE tasks—**SST-2**, **QQP**, **QNLI**, **RTE**, **MNLI**—while keeping **GLUE training data and metrics unchanged** so any GLUE-trained model can be evaluated under IID vs. adversarial shifts. The pipeline: (1) **Source selection:** start from GLUE dev sets (for large tasks QQP/QNLI/MNLI, sample **1,000** dev cases for efficiency). (2) **Adversarial generation:** apply attacks at three hierarchies. **Word-level** attacks: **TextBugger** (typo), **TextFooler** (embedding-similarity synonym substitution), **BERT-ATTACK** (masked-LM contextual substitution), **SememePSO** (HowNet/sememe-guided + PSO search), plus **CompAttack** (authors’ composition/optimization integrating multiple perturbation operators while minimizing changed words). **Sentence-level** attacks: syntactic/structure manipulations via **SCPN** (template-guided paraphrase using top-10 ParaNMT-50M syntactic templates; LSTM encoder–decoder), **T3** (white-box syntax-tree context vector optimization at root node), and **AdvFever** entailment-preserving rewrite rules; plus **distraction** rules from **StressTest** (append repeated true/false clauses) and **CheckList** (add random URLs/handles). **Human-crafted** sources add broader phenomena: **CheckList** templates (Temporal/Negation for SST-2/QQP/QNLI), **StressTest** numerical reasoning for MNLI, **ANLI** for MNLI-format adversarial NLI, and **AdvSQuAD** distractors mapped into QNLI. (3) **Surrogate-model setup for generation:** follow ANLI-style transfer filtering by generating adversarial examples against **three surrogates** trained on GLUE: **BERT**, **RoBERTa**, and a **RoBERTa ensemble**. (4) **Automatic filtering:** retain only examples with high **transferability** (must fool multiple surrogates), and enforce **fidelity**—for word-level, filter out examples with word modification rate **> 15%**; for sentence-level, keep those with highest **BERTScore** similarity. (5) **Human filtering (MTurk):** workers pass a training quiz (≥ **85%** accuracy on 20 GLUE-dev items with feedback). Each adversarial example is labeled by **5 annotators**; keep only items with **≥4/5 consensus** and **utility-preserving** constraint (majority label must equal original label), ensuring attacks don’t change meaning for humans. (6) **Dataset finalization:** merge curated automatic attacks with distraction/human-crafted sets (sampled to match per-attack counts/label distributions), and create **dev/test** via a **9:1** split of benign sources (adversaries from 90% become hidden test; remaining 10% released dev); human-crafted sets are randomly split **90/10** test/dev.

Key robustness/attack metrics used during construction:
\[
\text{ASR}=\frac{\sum_{(x,y)\in D}\mathbf{1}[f(A(x))\neq y]}{\sum_{(x,y)\in D}\mathbf{1}[f(x)=y]}
\]
\[
\text{Curated ASR}=\frac{\sum_{(x,y)\in D}\mathbf{1}[f(A(x))\neq y]\cdot \mathbf{1}[A(x)\in D_c]}{\sum_{(x,y)\in D}\mathbf{1}[f(x)=y]}
\]
and \(\text{Filter Rate}=1-\frac{\text{Curated ASR}}{\text{ASR}}\). Validity is further assessed with **Fleiss’ κ** (pre/post curation) and **human accuracy** (random annotator vs. majority label).

### Experiments & Results
**Datasets / scale.** AdvGLUE covers GLUE tasks with original training sets (SST-2 **67,349**; QQP **363,846**; QNLI **104,743**; RTE **2,490**; MNLI **392,702**). The **AdvGLUE test set** size totals **4,978** adversarial cases across tasks (SST-2 **1,420**; QQP **422**; QNLI **968**; RTE **304**; MNLI **1,864**), built from multiple attack categories (word-level C1–C5; sentence-level C6–C7; human-crafted C8–C11). The benchmark uses the same **GLUE metrics**: accuracy for SST-2/QNLI/RTE; **MNLI** matched/mismatched accuracy; **QQP** reports accuracy and F1 (paper table shows both in “a/b” format).

**Attack benchmarking during curation.** Raw attacks often “succeed” on models but fail semantic validity: averaged across tasks, word/sentence attacks show high **ASR** (~42–71%), yet **Curated ASR** is **always < 11%** with **filter rates > 85%** (most generated examples are invalid/ambiguous). Fleiss’ κ is low before curation (often ~0.1–0.4) and rises post-curation to ~0.6 on average (moderate/substantial agreement). The paper highlights that ~**90%** of generated adversarial examples are rejected; **TextBugger** is noted as most effective+valid among tested attacks (highest Curated ASR / κ trend).

**Model robustness evaluation (main benchmark).** They evaluate standard SOTA LMs and robust-training baselines trained on GLUE, then tested on AdvGLUE hidden test. Large drops appear across all models; e.g., **ELECTRA(Large)** average GLUE **93.16 → 41.69** on AdvGLUE.

**Main results (macro-average over tasks; “GLUE” from standard benchmark vs. “AdvGLUE”):**

| Model | Avg (GLUE) | Avg (AdvGLUE) | Drop |
|---|---:|---:|---:|
| BERT (Large) | 85.76 | 33.68 | 52.08 |
| ELECTRA (Large) | 93.16 | 41.69 | 51.47 |
| RoBERTa (Large) | 91.44 | 50.21 | 41.23 |
| T5 (Large) | 90.39 | 56.82 | 33.57 |
| ALBERT (XXLarge) | 91.87 | 59.22 | 32.65 |
| DeBERTa (Large) | 92.67 | 60.86 | 31.81 |
| SMART (BERT) | 85.70 | 30.29 | 55.41 |
| SMART (RoBERTa) | 92.62 | 53.71 | 38.91 |
| FreeLB (RoBERTa) | 92.28 | 50.47 | 41.81 |
| InfoBERT (RoBERTa) | 89.06 | 46.04 | 43.02 |

Per-attack diagnostics (Table 5) show models are generally **most vulnerable to human-crafted** sets (e.g., ANLI, AdvSQuAD, StressTest/CheckList capabilities), and within automatic attacks, vulnerability is broad across word-level methods (typos/knowledge-guided particularly strong). **Ablation-style insight:** robust training helps only incrementally; e.g., **SMART(RoBERTa)** improves **RoBERTa(Large)** on AdvGLUE by **+3.71** average points (50.21→53.71) while also improving benign accuracy, but no method closes the large robustness gap. No statistical significance intervals or compute budgets (GPU hours/speed) are reported in the provided excerpt.

### Discussion & Conclusion
AdvGLUE demonstrates that high IID GLUE performance does not imply adversarial robustness: all tested LMs (and robust training methods) suffer large absolute drops, sometimes below random guessing. A central limitation revealed by their own construction is that **current automatic attacks frequently violate semantic preservation**, necessitating heavy curation; future work is needed on both **stealthier, meaning-preserving attacks** and **substantially more robust model training** beyond incremental gains.

## Key Contributions
- Proposes **AdvGLUE**, a **multi-task** adversarial robustness benchmark aligned with GLUE tasks, metrics, and training setup for easy adoption.
- Systematically evaluates and curates adversarial data from **14 textual attack methods**, combining **automatic transferability/fidelity filtering** with **5-annotator human validation** (≥4/5 consensus + label preserved).
- Provides a standardized robustness leaderboard and diagnostic breakdown showing **large robustness failures** of SOTA LMs and limited benefits from popular defenses (e.g., **SMART**, **FreeLB**, **InfoBERT**).

## Potential Relevance
AdvGLUE is useful for hypothesis development on (i) how robustness varies across **model families** (e.g., DeBERTa/ALBERT vs. BERT/ELECTRA) under a consistent adversary, and (ii) which **attack classes** (typos, syntactic rewrites, distractions, human-crafted reasoning) dominate failure modes. The paper’s curation findings (~90% invalid raw adversaries; Curated ASR <11%) are also a strong signal that future robustness research must tightly control **semantic validity**—otherwise robustness estimates can be confounded by label noise or meaning drift.
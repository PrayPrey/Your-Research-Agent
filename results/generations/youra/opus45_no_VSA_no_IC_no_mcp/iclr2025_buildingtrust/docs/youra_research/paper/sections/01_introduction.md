# Introduction

We discovered a surprisingly strong correlation (r=0.80) between LLM truthfulness and adversarial robustness—two capabilities often studied in isolation—but the intuitive explanation (calibration) turned out to be wrong.

This finding matters for AI safety research: if models that avoid generating misinformation also resist adversarial attacks, understanding the underlying mechanism could guide the development of trustworthy systems. Without this understanding, efforts to improve different trust dimensions may be fragmented and inefficient.

## The Problem: Trust Benchmark Silos

Large language models can fail in multiple trust dimensions. A model may generate plausible-sounding but factually incorrect statements (truthfulness failures), or it may be fooled by adversarially perturbed inputs that humans would recognize as unchanged in meaning (robustness failures). These failure modes are typically studied independently: TruthfulQA [Lin et al., 2022] evaluates whether models repeat common misconceptions, while AdvGLUE [Wang et al., 2022] measures vulnerability to word-level adversarial perturbations.

This separation creates a deeper problem. We lack understanding of whether truthfulness and robustness are fundamentally related capabilities or independent dimensions. If correlated, a common mechanism may underlie both; if independent, separate interventions are required. The research community has not systematically examined this question—no prior study correlates TruthfulQA and AdvGLUE scores across multiple model families.

## Our Approach and Key Finding

We conducted the first systematic correlation analysis between truthfulness (TruthfulQA MC1) and adversarial robustness (AdvGLUE average) across 14 decoder-only LLMs from four families (Pythia, Llama-2, Mistral, Falcon), ranging from 70M to 70B parameters. Using partial correlation with model size as a covariate, we found:

**Main Result:** TruthfulQA MC1 and AdvGLUE accuracy show a strong positive partial correlation (r=0.80, p<0.001), with a 95% bootstrap confidence interval of [0.08, 0.97] that excludes zero.

The obvious explanation for this correlation is calibration: well-calibrated models might "know what they don't know," enabling them to avoid false claims (truthfulness) and detect anomalous inputs (robustness). We tested this hypothesis directly by measuring Expected Calibration Error (ECE) on MMLU and examining whether ECE correlates with either metric or moderates the truthfulness-robustness relationship.

**Mechanism Finding:** The calibration hypothesis is falsified. ECE shows near-zero correlation with TruthfulQA (r=-0.12, p=0.68) and AdvGLUE (r=-0.16, p=0.58). Furthermore, poorly-calibrated (high-ECE) models showed stronger truthfulness-robustness correlation (r=0.99) than well-calibrated models (r=0.65)—the opposite of what the calibration mechanism predicts.

## Contributions

This work makes three contributions to understanding trust in LLMs:

1. **First documented correlation:** We establish that TruthfulQA MC1 and AdvGLUE accuracy are strongly positively correlated (r=0.80) after controlling for model size—a relationship not previously known.

2. **Mechanism falsification:** We demonstrate that model calibration (ECE) does not explain this correlation, ruling out the most intuitive hypothesis and opening the question of what common cause underlies joint trustworthiness.

3. **Scope characterization:** We show the correlation is robust across model families for base models, while instruction-tuned models require further study due to limited sample size (N=6).

The remainder of this paper is organized as follows. Section 2 reviews related work on truthfulness, robustness, and calibration. Section 3 describes our evaluation methodology. Section 4 presents the experimental setup, and Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes with directions for future work.

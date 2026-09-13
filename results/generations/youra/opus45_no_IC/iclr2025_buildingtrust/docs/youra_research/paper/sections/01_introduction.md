# Introduction

Language models exhibit measurably different confidence patterns across semantic categories on truthfulness tasks — yet this variation cannot be exploited for better calibration. We present systematic evidence that while LLMs show category-dependent calibration error (ANOVA p<0.001) and produce distinct confidence distributions across semantic domains (17/21 cluster pairs significantly different), optimal temperature scaling parameters are uniform across all categories. This surprising uniformity reveals that model overconfidence is a global property of RLHF-trained systems rather than a category-specific phenomenon.

## The Calibration Problem

Modern neural networks, including large language models, are poorly calibrated: their confidence scores do not reliably reflect accuracy \cite{guo2017calibration}. On factual tasks like TruthfulQA \cite{lin2022truthfulqa}, models express high confidence even when generating false statements. Post-hoc calibration methods, particularly temperature scaling, can reduce Expected Calibration Error (ECE) by adjusting the softmax temperature to better align confidence with accuracy.

A natural hypothesis emerges from the structure of truthfulness benchmarks. TruthfulQA organizes 817 questions across 38 semantic categories — from Finance and Economics to Misconceptions and Myths. If models exhibit different confidence-accuracy relationships across these domains, category-specific calibration should outperform a single global temperature. This intuition aligns with findings that LLM uncertainty varies by task type \cite{xiong2023uncertainty}.

## The Gap

Despite extensive work on neural network calibration and growing interest in LLM uncertainty quantification, no prior study has systematically tested whether category-level calibration structure exists in truthfulness benchmarks — or whether it can be exploited via per-category temperature scaling. This gap matters: if certain categories are systematically overconfident while others are well-calibrated, global temperature scaling applies a suboptimal one-size-fits-all correction.

## Our Contribution

We address this gap through a pre-registered experiment testing cluster-specific temperature scaling on TruthfulQA using Llama-2-7B. We group the 38 categories into 7 semantic clusters and test three linked hypotheses:

1. **Existence (h-e1):** Does calibration error vary significantly across clusters?
2. **Mechanism (h-m1):** Do different clusters produce distinct confidence distributions?
3. **Mechanism (h-m2):** Do different distributions require different temperature parameters?

Our results confirm the first two hypotheses while falsifying the third. We find significant ECE variation across clusters (F=8.45, p=0.00012) with Finance/Economics achieving ECE of 0.152 versus 0.251 for Misconceptions/Myths. Confidence distributions differ substantially (Kolmogorov-Smirnov test: 17/21 cluster pairs significant at p<0.05). However, when optimizing temperature per cluster, all seven clusters converge to the same value: T=10.0, the upper bound of our search range.

This uniform convergence falsifies the hypothesis that category-specific calibration can outperform global calibration via temperature scaling. The model is not *differently* miscalibrated across categories — it is *uniformly overconfident* in the same direction, with the same severity, across all semantic domains. The category variation in ECE reflects differences in task difficulty and answer distributions, not in calibration needs.

## Implications

Our negative result is itself informative. It suggests that RLHF-trained models develop a global overconfidence pattern that dominates any category-specific effects. Temperature scaling, which only scales confidence, cannot address this uniform problem better by knowing the category. Alternative calibration approaches — perhaps methods that reshape rather than scale the confidence distribution — may be necessary for LLM truthfulness tasks.

The paper proceeds as follows: Section 2 reviews related work on calibration and LLM uncertainty. Section 3 describes our methodology including clustering, temperature optimization, and evaluation metrics. Section 4 details the experimental setup. Section 5 presents results for each hypothesis. Section 6 discusses implications and limitations. Section 7 concludes.

# Related Work

We organize related work by the progression of uncertainty quantification methods, highlighting how each advance addressed prior limitations while introducing new assumptions that our controlled comparison tests.

## Uncertainty Quantification in Neural Networks

Foundational work on neural network calibration established that modern deep networks are often overconfident [Guo et al., 2017]. For language models specifically, calibration became critical as models grew capable of generating plausible-sounding but factually incorrect text. Malinin and Gales [2018] introduced predictive uncertainty decomposition for classification, distinguishing epistemic (knowledge) from aleatoric (data) uncertainty. However, these methods assumed classification settings and did not address free-form generation or factuality assessment.

## Token-Level Uncertainty for LLMs

As LLMs demonstrated emergent capabilities, researchers adapted uncertainty quantification to generation settings. The simplest approach extracts uncertainty directly from output token logits: entropy over the vocabulary distribution, maximum probability of the selected token, or perplexity of the generated sequence. Kadavath et al. [2022] introduced P(True), asking models to self-assess truthfulness and using the probability of "True" as a confidence signal. They showed reasonable calibration on proprietary data. These methods share a key advantage: single-pass computation without additional inference. However, they operate at the token level and may miss semantic-level consistency issues where individually confident tokens form an incorrect composition.

## Semantic-Level Uncertainty Methods

To capture meaning-level uncertainty, Kuhn et al. [2023] proposed semantic entropy. Rather than computing entropy over tokens, semantic entropy generates multiple samples, clusters semantically equivalent responses using NLI-based entailment, and computes entropy over cluster assignments. On their custom QA evaluation, semantic entropy substantially outperformed token entropy, suggesting that meaning-level consistency signals are more informative than token-level confidence. Manakul et al. [2023] introduced SelfCheckGPT, using self-consistency across multiple samples to detect hallucinations without reference documents. Both methods demonstrate the value of multi-sample approaches but require 5--20x more inference compute than token-level methods.

## Hallucination Detection Benchmarks

TruthfulQA [Lin et al., 2022] provides a benchmark specifically designed to test LLM truthfulness, with questions that elicit imitative falsehoods humans might believe but are factually incorrect. HaluEval [Li et al., 2023] extends to multiple domains: QA, dialogue, and summarization, enabling category-specific analysis. These benchmarks provide ground-truth labels for hallucination detection evaluation, avoiding the need for manual annotation.

## Gap: No Controlled Comparison

Despite this rich landscape, a critical gap remains. Each method paper evaluated on favorable conditions: semantic entropy against token entropy on custom splits, SelfCheckGPT on WikiBio generation, P(True) on proprietary data. No study has compared these methods on identical benchmarks, splits, and models. Furthermore, no study has examined whether method effectiveness depends on task format---a hypothesis our results strongly support.

We address this gap by conducting the first controlled head-to-head comparison on TruthfulQA's multiple-choice format. Our methodology isolates format-dependency effects by verifying that semantic entropy's clustering mechanism functions correctly (it does) while its discrimination fails (AUROC near random). This separation of mechanism verification from discrimination evaluation is a methodological contribution that clarifies why sophisticated methods may underperform on certain formats.

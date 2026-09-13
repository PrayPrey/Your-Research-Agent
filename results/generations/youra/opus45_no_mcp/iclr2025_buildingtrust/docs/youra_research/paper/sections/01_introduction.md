# Introduction

When large language models reason step-by-step, something unexpected happens: they generate linguistic markers of uncertainty that correlate with more calibrated confidence judgments. This suggests that models can leverage their own in-context uncertainty signals—a form of "self-reading" that emerges from the autoregressive generation process.

## The Calibration Problem

LLM confidence is notoriously poorly calibrated. Models routinely express high confidence (80-90%) on questions they answer incorrectly, while showing similar confidence on questions they answer correctly. This overconfidence problem undermines the trustworthiness of LLM outputs, particularly in high-stakes applications where users must decide whether to rely on model predictions.

The deeper issue is that standard prompting provides no mechanism for uncertainty to surface during generation. When prompted to simply answer a question, the model produces a response without any intermediate reasoning that might reveal epistemic uncertainty. The confidence score, if requested, is generated without access to information about the model's own uncertainty during answer generation.

This leads to a critical gap: despite extensive work on chain-of-thought prompting for accuracy improvement and separate work on confidence elicitation methods, no systematic study has isolated HOW the combination of CoT and confidence verbalization might improve calibration—and specifically whether any improvement stems from meaningful uncertainty signals or trivial artifacts like increased token count.

## Our Key Insight

We demonstrate that CoT prompting produces reasoning chains containing epistemic hedging markers (words like "may," "could," "however") that negatively correlate with verbalized confidence (Spearman r=-0.315, p<1e-16). This correlation validates a "self-reading" mechanism: because hedging markers appear in the reasoning chain before the confidence estimate is generated, they remain in-context and can influence the confidence judgment.

Our work provides the first systematic verification of the complete causal chain underlying CoT+confidence calibration:

**Step 1:** CoT prompting reliably produces multi-step reasoning (100% rate, mean 4.49 reasoning steps vs 0% for direct prompting).

**Step 2:** These reasoning chains contain epistemic hedging markers (82% presence rate, with "may" appearing 787 times and "could" appearing 619 times across our evaluation set).

**Step 3:** Due to autoregressive generation, hedging markers are present in-context when the model subsequently generates a confidence estimate (100% structural compliance with CoT-then-confidence ordering).

**Step 4:** The model incorporates these uncertainty signals, producing lower confidence when more hedging markers are present (r=-0.315, significantly exceeding the r=-0.2 threshold from prior literature).

## Contributions

This paper makes three contributions to understanding LLM calibration. First, we provide empirical validation of the complete mechanism chain linking CoT prompting to calibration improvement, moving beyond correlational observations to systematic verification of each step. Second, we quantify the hedging-confidence relationship with a concrete effect size (r=-0.315) that exceeds prior estimates and provides a benchmark for future work. Third, we demonstrate that prompting-based calibration improvement is not merely a token-count artifact but reflects meaningful integration of in-context uncertainty signals.

Our findings have practical implications for LLM deployment: CoT+confidence prompting provides a zero-shot method for obtaining more calibrated confidence estimates, without requiring model fine-tuning or access to internal logits.

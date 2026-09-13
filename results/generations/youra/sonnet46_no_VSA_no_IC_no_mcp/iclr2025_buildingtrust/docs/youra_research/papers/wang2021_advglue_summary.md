# Paper Summary: AdvGLUE: A Multi-Task Benchmark for Evaluating Adversarial Robustness (Wang et al., 2021)

**arXiv:** 2111.02840 | **Citations:** ~200 | **Venue:** EMNLP 2021

## Key Contributions
- Created AdvGLUE: adversarial versions of GLUE tasks (SST-2, QQP, MNLI, QNLI, RTE)
- Applied 14 adversarial attack methods to generate perturbed inputs: word substitution, paraphrase attacks, etc.
- Showed all evaluated models (BERT, RoBERTa, ALBERT, T5) have significant accuracy drops on AdvGLUE vs GLUE
- Accuracy-only evaluation: NO calibration measurement

## Methodology
- Perturbation types: text fooler, BERT-attack, word-level substitutions, back-translation
- Human validation of adversarial examples for label preservation
- Models evaluated: BERT-base/large, RoBERTa, ALBERT, DeBERTa, T5
- Available on HuggingFace datasets hub

## Key Findings
- Average accuracy drop: 15-30% across models and tasks
- No model is robustly accurate across all adversarial attack types
- Some attacks more effective than others depending on task type

## Relevance to Gap 1
- **Directly provides the adversarial benchmark** for Gap 1 experiment
- Gap: only accuracy measured — ECE on these adversarial splits has never been computed
- Hypothesis: if accuracy drops 15-30%, ECE likely degrades even more (models remain confident while wrong)
- AdvGLUE available via HF datasets, compatible with lm-evaluation-harness

## Limitations
- Accuracy-only evaluation — calibration not measured (this IS the gap)
- Older generation models (BERT family); no Llama/Mistral/GPT-4 evaluation
- Some adversarial examples may be label-ambiguous (human validation imperfect)

# Paper Summary: Language Models (Mostly) Know What They Know (Kadavath et al., 2022)

**arXiv:** 2207.05221 | **Citations:** ~500 | **Venue:** Anthropic Technical Report

## Key Contributions
- First systematic study of LLM self-calibration on Claude and GPT-3
- Models can estimate their own answer correctness with reasonable calibration when asked "Is your answer correct?"
- Demonstrates that verbally elicited probabilities track actual accuracy
- Identifies cases where models are confidently wrong (overconfident failure modes)

## Methodology
- Self-assessment approach: model answers question, then rates confidence (True/False format)
- Evaluated on TriviaQA, MMLU, BIG-Bench tasks
- Calibration measured via verbal probability extraction (not logits)
- No adversarial perturbation; clean benchmark splits only

## Key Findings
- Larger models are better calibrated (size → calibration correlation)
- P(True) elicitation produces well-calibrated probabilities for Claude family
- Calibration degrades on harder tasks (BIG-Bench Hard vs TriviaQA)
- Models are not well-calibrated for multi-step reasoning tasks

## Relevance to Gap 1
- Establishes LLM calibration baseline on clean benchmarks
- The gap: no adversarial perturbation tested — Gap 1 is the adversarial extension
- Suggests logit-based calibration may differ from verbal self-assessment

## Limitations
- Verbal calibration only; no logit-based ECE
- Claude/GPT-3 only; no open-weight model comparison (Llama, Mistral)
- No adversarial or out-of-distribution inputs
- Self-assessment metric ≠ traditional ECE

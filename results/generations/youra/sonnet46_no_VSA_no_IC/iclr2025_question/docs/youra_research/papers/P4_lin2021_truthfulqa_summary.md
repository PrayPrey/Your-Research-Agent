# Paper Summary: TruthfulQA
**arXiv:** 2109.07958 | **Authors:** Lin, Hilton, Evans | **Year:** 2021 | **Citations:** 3781

## Key Contributions
- 817 questions designed to elicit human-like falsehoods from LLMs
- Demonstrates inverse scaling: larger models are LESS truthful (imitate human misconceptions)
- Standard hallucination evaluation benchmark — used by SE, SelfCheckGPT, CCP, EPR, etc.
- Binary truth label per question (True/False) provided for classification/AUROC evaluation

## Methodology
- Questions target common misconceptions across 38 categories (health, law, finance, etc.)
- Adversarially constructed: human-generated answers are often wrong; models tend to agree
- Truth labels available for binary classification evaluation
- Multiple-choice and generation variants exist; generation variant used for uncertainty evaluation

## Experiments & Results
- GPT-3: ~21% truthful; GPT-3 Davinci: ~28% truthful (inverse scaling pattern)
- Human baseline: 94% truthful
- As of 2024, most SOTA uncertainty methods evaluated on TruthfulQA generation subset
- Binary truth labels enable AUROC evaluation of uncertainty-as-hallucination-detector

## Potential Relevance to Gap 2
- Standard benchmark: any token aggregation ablation MUST include TruthfulQA for credibility
- Truth labels readily available — no new annotation needed
- 817 questions: sufficient statistical power for AUROC comparison across aggregation methods
- Diverse categories test whether aggregation strategy advantage generalizes across domains

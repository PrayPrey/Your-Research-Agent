# Paper Summary: SelfCheckGPT
**arXiv:** 2303.08896 | **Authors:** Manakul, Liusie, Gales | **Year:** 2023 | **Citations:** 1148

## Key Contributions
- Black-box hallucination detection: sample N responses, check consistency with BERTScore/NLI/MQAG/N-gram/LLM-judge
- Calibration-free — no reference labels needed
- Works with API-only LLMs (no logprob access required)
- Benchmark: WikiBio factual consistency; extended to TriviaQA/NQ in follow-up work

## Methodology
- Sample N=20 responses from model (temperature=1.0)
- For each sentence in first response, measure consistency with N-1 samples
- Consistency variants: BERTScore, NLI entailment, MQAG (multiple-choice QA), N-gram overlap, LLM-judge
- No token probabilities used — pure output-space comparison
- Evaluated on sentence-level and passage-level hallucination

## Experiments & Results
- BERTScore variant: AUROC 0.68-0.74 on WikiBio
- NLI variant: AUROC 0.72-0.78 (best among variants on WikiBio)
- Repository includes probability-based baselines: max token prob, mean token prob for comparison
- NOTE: probability baselines in the repo are NOT systematically ablated — included as one-line baselines
- Key finding: consistency-based methods outperform single-pass token probabilities

## Potential Relevance to Gap 2
- probability-based-baselines.ipynb in repo contains max/mean token prob code — DIRECTLY usable
- These are ad-hoc baselines, not a systematic ablation study
- Gap 2 = running these baselines systematically with geometric mean and sum added, on TriviaQA/NQ/SciQ/TruthfulQA
- Provides the black-box upper bound (NLI consistency) for comparison

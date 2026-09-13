# Paper Summary: Fact-Checking the Output of LLMs via Token-Level UQ (CCP)
**arXiv:** 2403.04696 | **Authors:** Fadeeva et al. | **Year:** 2024 | **Citations:** 186

## Key Contributions
- Claim Conditioned Probability (CCP): removes surface-form uncertainty from token log-probabilities by conditioning on semantic equivalence classes
- Evaluated on 7 LLMs (Llama-2, Mistral, GPT variants) across 4 languages
- Uses mean length-normalized log-prob as aggregation baseline; CCP consistently outperforms raw mean
- Integrated in lm-polygraph benchmark suite

## Methodology
- Token-level: compute log p(token_i | context) for each output token
- Aggregation: mean over sequence length (length-normalized sum)
- CCP correction: divide by p(semantic_class | context) to factor out surface-form variation
- Evaluation metric: AUROC on factual QA hallucination detection (binary: factual / hallucinated)
- Benchmarks: TriviaQA, Natural Questions, SciQ; multiple languages

## Experiments & Results
- CCP achieves AUROC ~0.72-0.80 across 7 models on TriviaQA/NQ
- Raw mean log-prob baseline: AUROC ~0.65-0.72 (consistently lower than CCP)
- Key finding: length normalization matters — unnormalized sum biased toward shorter answers
- No comparison of max vs. mean vs. sum in ablation; method comparison is CCP vs. prior systems
- lm-polygraph provides unified framework: runs mean/sum/max alongside CCP

## Potential Relevance to Gap 2
- Provides the MEAN aggregation baseline under controlled conditions
- Does NOT ablate max vs. mean vs. sum — this is the exact missing piece
- lm-polygraph code enables controlled ablation using their evaluation pipeline
- CCP serves as the "smart aggregation" upper bound; raw baselines (max/mean/sum) are not ablated

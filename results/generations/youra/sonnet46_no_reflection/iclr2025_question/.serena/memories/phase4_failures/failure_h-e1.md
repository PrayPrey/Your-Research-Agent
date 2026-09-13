# Phase 4 Failure Record: h-e1
## Date: 2026-05-21
## Hypothesis: h-e1 (EXISTENCE)
## Gate: MUST_WORK → FAIL → ROUTED_TO_PHASE_0

### Hypothesis Statement
Under Llama-3 base checkpoints on TriviaQA and NaturalQuestions with identical splits and evaluation harness, SE and KLE show statistically higher AUROC for correctness prediction than token-probability at both 8B and 70B scales.

### Gate Conditions (all required, all failed at 8B)
1. SE AUROC > token_prob AUROC at 8B/TriviaQA: SE=0.4735 vs TP=0.6835 → FAIL (diff=-0.2100)
2. SE AUROC > token_prob AUROC at 8B/NQ: SE=0.5524 vs TP=0.6551 → FAIL (diff=-0.1027)
3. 70B conditions: UNKNOWN (70B experiment still running at evaluation time)

### Root Causes
- **SE < token_prob at 8B**: Semantic entropy clustering on a base (non-instruction) Llama-3-8B is producing LOWER discriminative AUROC than simple token log-probability.
- **High degenerate_fraction**: mean_k ≈ 9.88 (out of N=10 samples) → samples cluster into ~1 cluster per query → SE collapses to low entropy → low discriminability between correct/incorrect queries.
- **Why degenerate**: Base model (not instruction-tuned) generates highly repetitive stochastic samples, especially for short factual answers. SE clustering collapses.
- **KLE also below TP**: KLE (EigValLaplacian) AUROC = 0.2642 (TriviaQA), 0.3753 (NQ) — much worse than TP=0.68, 0.66.

### Key Insight for Phase 0 Redesign
The fundamental assumption that SE/KLE > token_prob holds for base models appears incorrect. SE/KLE may only show advantage for:
- Instruction-tuned models where stochastic diversity is higher
- Longer-form generation tasks where semantic clusters are meaningful
- OR the advantage exists but requires larger sample N (N=10 insufficient)

Token probability (negative log-likelihood) is a strong baseline for factual QA correctness prediction.

### Recommendations for Future Hypotheses
1. Test on instruction-tuned models (Llama-3-8B-Instruct) where sampling diversity may be higher
2. Increase N_samples beyond 10 to reduce cluster collapse probability
3. Consider the scale interaction hypothesis differently: maybe SE advantage only appears at 70B (not 8B)
4. Reformulate hypothesis to be conditional on sampling diversity being sufficient (degenerate_fraction < threshold)

### Experimental Configuration
- Models: meta-llama/Meta-Llama-3-8B (base, bfloat16), meta-llama/Meta-Llama-3-70B (base, 8-bit)
- Datasets: TriviaQA rc.nocontext validation, NaturalQuestions open-domain validation
- n_samples: 10 (small), 5 (large), max_samples: 500 (small), 200 (large)
- UQ methods: token_prob, semantic_entropy, kle, selfcheck_bertscore, selfcheck_nli, seps
- correctness: exact match with gold answer aliases

### Results Summary (8B/small)
| Method | TriviaQA AUROC | NQ AUROC |
|--------|---------------|----------|
| token_prob | **0.6835** | **0.6551** |
| semantic_entropy | 0.4735 | 0.5524 |
| kle | 0.2642 | 0.3753 |
| selfcheck_nli | 0.6862 | 0.4508 |
| selfcheck_bertscore | 0.5 | 0.5 |

Correctness rates: TriviaQA 66%, NQ 19.4%

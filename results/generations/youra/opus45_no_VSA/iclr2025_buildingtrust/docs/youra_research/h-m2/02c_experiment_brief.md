# Phase 2C: Experiment Brief
## H-M2: Instruction-Tuning Effect on BSI and PC1,residual

Generated: 2026-08-08T09:30:00Z

---

## Hypothesis

**ID:** H-M2  
**Statement:** Instruction-tuning increases both BSI and PC1,residual score within matched base/instruct model pairs (paired t-test p < 0.05).

**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** H-E1 (VALIDATED)

---

## Experiment Design

### 1. Objective

Test whether instruction-tuning systematically improves both:
1. **Behavioral Stability Index (BSI)**: Paraphrase consistency on PAWS/QQP
2. **PC1,residual**: First principal component score from residualized trustworthiness benchmarks

Using matched base/instruct model pairs with paired statistical tests.

### 2. Matched Model Pairs

| Family | Base Model | Instruct Model | Params |
|--------|-----------|----------------|--------|
| Llama-2 | meta-llama/Llama-2-7b-hf | meta-llama/Llama-2-7b-chat-hf | 7B |
| Llama-2 | meta-llama/Llama-2-13b-hf | meta-llama/Llama-2-13b-chat-hf | 13B |
| Llama-2 | meta-llama/Llama-2-70b-hf | meta-llama/Llama-2-70b-chat-hf | 70B |
| Llama-3 | meta-llama/Meta-Llama-3-8B | meta-llama/Meta-Llama-3-8B-Instruct | 8B |
| Llama-3 | meta-llama/Meta-Llama-3-70B | meta-llama/Meta-Llama-3-70B-Instruct | 70B |
| Llama-3.1 | meta-llama/Llama-3.1-8B | meta-llama/Llama-3.1-8B-Instruct | 8B |
| Llama-3.2 | meta-llama/Llama-3.2-1B | meta-llama/Llama-3.2-1B-Instruct | 1B |
| Llama-3.2 | meta-llama/Llama-3.2-3B | meta-llama/Llama-3.2-3B-Instruct | 3B |
| Mistral | mistralai/Mistral-7B-v0.1 | mistralai/Mistral-7B-Instruct-v0.1 | 7B |
| Mistral | mistralai/Mistral-7B-v0.3 | mistralai/Mistral-7B-Instruct-v0.3 | 7B |
| Mixtral | mistralai/Mixtral-8x7B-v0.1 | mistralai/Mixtral-8x7B-Instruct-v0.1 | 47B |
| Qwen2 | Qwen/Qwen2-7B | Qwen/Qwen2-7B-Instruct | 7B |
| Qwen2 | Qwen/Qwen2-72B | Qwen/Qwen2-72B-Instruct | 72B |
| Gemma | google/gemma-7b | google/gemma-7b-it | 7B |
| Gemma-2 | google/gemma-2-9b | google/gemma-2-9b-it | 9B |
| Phi-3 | microsoft/Phi-3-mini-4k-instruct | microsoft/Phi-3-mini-128k-instruct | 3.8B |

**Total:** 16 matched pairs (N=16 for paired t-test)

### 3. BSI Measurement Protocol

**Behavioral Stability Index (BSI)** measures paraphrase consistency:

```
BSI = (1/K) Σ Agreement(response(prompt_i), response(paraphrase_ij))
```

Where K = number of paraphrase pairs evaluated.

**Datasets:**
- **PAWS-Wiki**: 8,000 test pairs (paraphrase/non-paraphrase)
- **PAWS-QQP**: 677 dev pairs from Quora Question Pairs
- **Total evaluation:** 8,677 pairs

**Evaluation Task:** Binary classification (paraphrase detection)
- Present original pair, get model prediction
- Present paraphrased version of same pair, get model prediction  
- Agreement = 1 if predictions match, 0 otherwise

**Sampling:** Full PAWS test set (no subsampling)

### 4. PC1,residual Computation

Reuse H-E1 validated methodology:

1. **Benchmark Matrix:** 6 trustworthiness benchmarks × N models
   - TruthfulQA, MMLU, AdvGLUE, BBH, GSM8K, WinoGrande
   
2. **Residualization:** 
   ```python
   for each benchmark:
       residual = benchmark_score - (β₀ + β₁*log(params) + β₂*release_date)
   ```

3. **PCA on Residuals:**
   ```python
   pca = PCA(n_components=1)
   pc1_scores = pca.fit_transform(residual_matrix)
   ```

4. **Score Extraction:** PC1 score for each model

### 5. Statistical Analysis

**Primary Test:** Paired t-test on differences

```python
import scipy.stats as stats

# For BSI
delta_bsi = bsi_instruct - bsi_base  # 16 values
t_bsi, p_bsi = stats.ttest_rel(bsi_instruct, bsi_base)

# For PC1
delta_pc1 = pc1_instruct - pc1_base  # 16 values
t_pc1, p_pc1 = stats.ttest_rel(pc1_instruct, pc1_base)
```

**Success Criteria:**
- Δ_BSI > 0 with p < 0.05
- Δ_PC1 > 0 with p < 0.05
- Both conditions must hold

**Secondary Analyses:**
1. Effect size (Cohen's d) for both metrics
2. Correlation between Δ_BSI and Δ_PC1 across pairs
3. Wilcoxon signed-rank test (non-parametric robustness check)

### 6. Confound Controls

| Confound | Control Method |
|----------|---------------|
| Model scale | Matched pairs (same architecture/params) |
| Training data | Same pretraining corpus within family |
| Release date | Pairs released simultaneously |
| Evaluation variance | Fixed seeds, greedy decoding |

### 7. Data Sources

| Resource | Source | Type |
|----------|--------|------|
| PAWS-Wiki | google-research-datasets/paws | standard |
| PAWS-QQP | google-research-datasets/paws | standard |
| Benchmark scores | Open LLM Leaderboard | programmatic-api |
| Model weights | HuggingFace Hub | programmatic-api |

### 8. Implementation Components

```
h-m2/
├── data/
│   ├── paws_wiki_test.json
│   ├── paws_qqp_dev.json
│   └── model_pairs.yaml
├── src/
│   ├── bsi_evaluator.py       # BSI computation
│   ├── pc1_scorer.py          # PC1,residual from H-E1
│   ├── paired_analysis.py     # Statistical tests
│   └── run_experiment.py      # Main orchestrator
├── results/
│   ├── bsi_scores.csv
│   ├── pc1_scores.csv
│   └── statistical_results.json
└── 04_validation.md
```

### 9. Expected Outcomes

**If H-M2 Validated:**
- Instruction-tuning causally increases representational coherence
- BSI serves as mechanistic proxy for GRC
- Training intervention → measurable stability improvement

**If H-M2 Refuted:**
- Instruction-tuning effect may be benchmark-specific
- BSI and PC1 may capture orthogonal constructs
- Does not block Phase 5 (SHOULD_WORK gate)

### 10. Resource Requirements

| Resource | Estimate |
|----------|----------|
| GPU hours | ~8h (A100, for large models) |
| VRAM | 80GB (70B models) |
| Storage | ~500GB (model weights) |
| Compute | 16 model pairs × 2 evals × 8.7K samples |

### 11. Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Insufficient pairs | LOW | 16 pairs exceeds minimum for paired t-test |
| Large variance in Δ | MEDIUM | Report effect sizes, use non-parametric backup |
| Base models poor at task | MEDIUM | Use few-shot prompting for base models |
| PC1 scores unavailable | LOW | Recompute using H-E1 validated pipeline |

---

## References

### Academic Papers

1. Fierro, C., Li, J., & Søgaard, A. (2024). "Does Instruction Tuning Make LLMs More Consistent?" *arXiv:2404.15206*. Shows instruction tuning improves representation/prediction consistency across 10 LLaMA variants.

2. Zhang, Y., Baldridge, J., & He, L. (2019). "PAWS: Paraphrase Adversaries from Word Scrambling." *NAACL 2019*. 108K human-labeled paraphrase pairs testing structural understanding.

3. Raj, H., Gupta, V., Rosati, D., & Majumdar, S. (2023). "Semantic Consistency for Assuring Reliability of Large Language Models." *arXiv:2308.09138*. Consistency measurement methodology for open-ended generation.

4. Srikanth, N., Carpuat, M., & Rudinger, R. (2024). "How Often Are Errors in Natural Language Reasoning Due to Paraphrastic Variability?" *TACL 2024*. PC metric for paraphrastic consistency; ParaNlu dataset (7,782 pairs).

5. Munjal, P., et al. (2026). "Do Instruction-Tuned Models Always Perform Better Than Base Models?" *arXiv:2601.13244*. Evidence that base models can outperform instruct variants in zero-shot CoT.

6. Wu, T., et al. (2025). "Shadow-FT: Tuning Instruct Model via Training on Paired Base Model." *arXiv:2505.12716*. Analysis of base/instruct weight similarity (<2% difference for Llama 3.1 8B).

7. ACL Anthology (2024). "From Language Modeling to Instruction Following: Understanding the Behavior Shift in LLMs after Instruction Tuning." *NAACL 2024*. Mechanistic analysis of instruction tuning effects.

### Datasets

8. **PAWS-Wiki**: https://github.com/google-research-datasets/paws — 8,000 test pairs
9. **PAWS-QQP**: https://github.com/google-research-datasets/paws — 677 dev pairs from Quora
10. **Open LLM Leaderboard**: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard — Benchmark scores

### Code Repositories

11. **AllenAI Open-Instruct**: https://github.com/allenai/open-instruct — Instruction tuning codebase (TÜLU 3)
12. **HuggingFace Transformers**: Model loading and inference
13. **H-E1 Pipeline**: Internal — PC1,residual computation (validated: λ₁=2.277, p=0.001)

### Model Sources

14. **Llama Family**: https://huggingface.co/meta-llama
15. **Mistral Family**: https://huggingface.co/mistralai
16. **Qwen Family**: https://huggingface.co/Qwen
17. **Gemma Family**: https://huggingface.co/google
18. **Phi Family**: https://huggingface.co/microsoft

---

## Approval

- [ ] Experiment design reviewed
- [ ] Data sources verified
- [ ] Statistical plan approved
- [ ] Resource allocation confirmed

**Status:** READY FOR PHASE 3

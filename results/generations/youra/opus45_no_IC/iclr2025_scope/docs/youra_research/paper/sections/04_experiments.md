# Experimental Setup

We design experiments to answer three research questions:

**RQ1 (H-E1):** Do task compression response clusters exist? If $k^* = 1$, all tasks respond identically and task-conditioned selection has no basis.

**RQ2 (H-M1):** Does attention entropy reflect task structure? If entropy does not discriminate domains, it cannot serve as a routing signal.

**RQ3 (H-M2):** Does entropy predict compression tolerance? If high-entropy tasks do not tolerate eviction better, the mechanism linking entropy to strategy selection is unverified.

## Dataset

**LongBench** [Bai et al., 2023] provides 21 datasets across 6 task categories:
- **Single-doc QA:** narrativeqa, qasper, multifieldqa_en, multifieldqa_zh
- **Multi-doc QA:** hotpotqa, 2wikimqa, musique, dureader
- **Summarization:** gov_report, qmsum, multi_news, vcsum
- **Few-shot:** trec, triviaqa, samsum, lsht
- **Synthetic:** passage_retrieval_en, passage_count, passage_retrieval_zh
- **Code:** lcc, repobench-p

We use the full test set (~200-500 samples per task, ~4750 total). Context is truncated to 4096 tokens matching Llama-2-7B's context window.

## Model

**Llama-2-7B** (meta-llama/Llama-2-7b-hf) with:
- 32 transformer layers
- 32 attention heads per layer
- 4096 context length
- FP16 precision for baseline

KV cache at full context is approximately 400MB.

## Compression Configurations

| Config | Method | Retention | Quantization | Purpose |
|--------|--------|-----------|--------------|---------|
| C1 | Full | 100% | FP16 | Baseline |
| C2 | H2O | 80% | FP16 | Conservative eviction |
| C3 | H2O | 40% | FP16 | Aggressive eviction |
| C4 | Full | 100% | INT8 | Quantization only |
| C5 | Full | 100% | INT4 | Aggressive quantization |
| C6 | H2O | 60% | INT8 | Hybrid |

H2O implementation follows Zhang et al. [2023], tracking cumulative attention scores and retaining heavy-hitters plus recent tokens.

## Evaluation Protocol

### RQ1: Clustering Analysis

**Response Matrix Construction:**
- Run 21 tasks × 6 configs = 126 evaluation runs
- Compute accuracy retention: $R_{tc} = A(t,c) / A(t, c_{\text{full}})$
- Result: 21 × 6 response matrix

**Gap Statistic:**
- $B = 500$ bootstrap samples
- $K_{\max} = 6$
- Success criterion: $k^* > 1$ with gap exceeding standard error

**Secondary Metric:**
- Silhouette score (target: > 0.5)

### RQ2: Entropy Analysis

**Entropy Extraction:**
- Sample 30 examples per domain (180 total)
- Extract first-100-token attention patterns
- Compute entropy across all 32 layers × 32 heads
- Aggregate to domain-level mean entropy

**Statistical Test:**
- One-way ANOVA across 6 domains
- Report: F-statistic, p-value, $\eta^2$
- Success criterion: $p < 0.05$, $\eta^2 > 0.10$

### RQ3: Entropy-Tolerance Relationship

**Protocol:**
- Stratify tasks by entropy (high vs. low)
- Apply 40% retention eviction
- Measure accuracy retention per group
- Two-sample t-test comparing groups

**Success Criterion:** $p < 0.05$, Cohen's $d > 0.5$

## Computational Resources

- GPU: 1× NVIDIA A100 (40GB)
- Inference time: ~21 GPU-hours for RQ1
- Gap statistic: ~5 minutes CPU
- Entropy extraction: ~1 GPU-hour for RQ2

## Metrics

| Task Category | Metric |
|---------------|--------|
| QA | F1 Score |
| Summarization | ROUGE-L |
| Code | Exact Match / CodeBLEU |
| Retrieval | Accuracy |
| Classification | Accuracy |

All metrics computed using LongBench evaluation scripts.

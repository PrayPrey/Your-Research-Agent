# Experiment Brief: h-m4 Scale-Invariant Optima

**Hypothesis ID:** h-m4
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Under optimal curation parameters identified at 125M scale, the same parameters at 1B scale preserve relative performance rankings.

## 2. Prerequisites

- **h-m3** (COMPLETED): Optimal threshold identified at p44.5 (95% CI [p40, p50])

## 3. Experimental Design

### 3.1 Core Comparison

| Configuration | Model Size | Perplexity Threshold | Training Tokens |
|--------------|------------|---------------------|-----------------|
| Baseline-125M | 125M | RedPajama default (~p60) | 10B |
| Optimal-125M | 125M | p45 (from h-m3) | 10B |
| Baseline-1B | 1B | RedPajama default (~p60) | 25B |
| Optimal-1B | 1B | p45 (from h-m3) | 25B |

### 3.2 Variables

**Independent:**
- Model Size: {125M, 1B}
- Perplexity Threshold: {p45 optimal, p60 default}

**Dependent:**
- Benchmark Ensemble Score (HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Relative improvement: (Optimal - Baseline) / Baseline

**Controlled:**
- Architecture: GPT-2 (decoder-only transformer)
- Training hyperparameters: LR schedule, batch size per effective FLOPs
- Dataset: RedPajama-v2
- Evaluation protocol: lm-evaluation-harness

### 3.3 Success Criteria

**Primary:** Optimal threshold at 1B within ±20% of 125M optimum
- 125M optimum: p45
- Valid range for 1B: p36-p54

**Secondary:** CPDR-optimized outperforms defaults at both scales
- Relative improvement at 1B ≥ 0.5 × relative improvement at 125M

### 3.4 Failure Criteria

- Optimal-1B underperforms Baseline-1B
- Optimal threshold at 1B falls outside p36-p54 range
- Relative ranking inverts between scales

## 4. Dataset Specification

### 4.1 Training Data

| Attribute | Value |
|-----------|-------|
| Name | RedPajama-v2 |
| Type | standard |
| Source | HuggingFace: togethercomputer/RedPajama-Data-v2 |
| Subset | English web text |
| Size | 125M: 10B tokens; 1B: 25B tokens (Chinchilla-optimal) |

### 4.2 Evaluation Data

| Benchmark | Split | Size |
|-----------|-------|------|
| HellaSwag | validation | 10,042 |
| ARC-Easy | test | 2,376 |
| PIQA | validation | 1,838 |
| WinoGrande | validation | 1,267 |

**Total evaluation samples:** 15,523

### 4.3 Data Preparation Pipeline

1. Download RedPajama-v2 raw English subset
2. Apply KenLM 5-gram perplexity scoring
3. Filter at threshold p45 (optimal) and p60 (default)
4. Deduplicate using MinHash (Jaccard 0.85)
5. Tokenize with GPT-2 BPE tokenizer
6. Create train splits: 10B tokens (125M) and 25B tokens (1B)

## 5. Model Specification

### 5.1 Architecture

| Parameter | 125M | 1B |
|-----------|------|-----|
| Layers | 12 | 24 |
| Hidden dim | 768 | 2048 |
| Heads | 12 | 16 |
| FFN dim | 3072 | 8192 |
| Context | 1024 | 1024 |
| Vocab | 50257 | 50257 |

### 5.2 Training Configuration

| Parameter | 125M | 1B |
|-----------|------|-----|
| Batch size (tokens) | 512K | 2M |
| Learning rate | 6e-4 | 3e-4 |
| Warmup steps | 2000 | 2000 |
| LR schedule | cosine | cosine |
| Weight decay | 0.1 | 0.1 |
| Gradient clipping | 1.0 | 1.0 |
| Precision | bf16 | bf16 |

### 5.3 Compute Requirements

| Model | GPUs | Time (est.) |
|-------|------|-------------|
| 125M × 2 configs | 4× A100 | ~8 hours |
| 1B × 2 configs | 8× A100 | ~48 hours |

**Total GPU-hours:** ~416 A100-hours

## 6. Evaluation Protocol

### 6.1 Metrics

1. **Per-benchmark accuracy** (HellaSwag, ARC-Easy, PIQA, WinoGrande)
2. **Ensemble score:** First principal component (PC1) of benchmark scores
3. **Relative improvement:** (Optimal - Baseline) / Baseline per scale
4. **Scale transfer ratio:** RelImprovement_1B / RelImprovement_125M

### 6.2 Statistical Analysis

1. Report mean ± std across 3 random seeds per configuration
2. Two-tailed t-test for Optimal vs Baseline at each scale
3. Bootstrap 95% CI for scale transfer ratio
4. Test H0: Scale transfer ratio = 1.0

### 6.3 Verification Steps

1. Train 125M models (2 configs × 3 seeds = 6 runs)
2. Evaluate on benchmark suite
3. Compute relative improvement at 125M
4. Train 1B models (2 configs × 3 seeds = 6 runs)
5. Evaluate on benchmark suite
6. Compute relative improvement at 1B
7. Compare relative rankings across scales

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| 1B training divergence | Checkpoint every 1B tokens; resume from stable |
| Compute budget exceeded | Start with 1 seed at 1B; expand if promising |
| Benchmark variance | Use ensemble metric to reduce noise |
| Scale-specific optima | Document as valid finding per H-M4 failure response |

## 8. Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Data prep | 1 day | Filtered datasets at p45/p60 |
| 125M training | 1 day | 6 trained models |
| 125M eval | 0.5 day | Benchmark results |
| 1B training | 3 days | 6 trained models |
| 1B eval | 0.5 day | Benchmark results |
| Analysis | 1 day | Statistical report |
| **Total** | **7 days** | |

## 9. Implementation Notes

### 9.1 Key Code Components

```python
# Perplexity filtering
def filter_by_perplexity(data, threshold_percentile):
    scores = compute_kenlm_perplexity(data)
    cutoff = np.percentile(scores, threshold_percentile)
    return data[scores <= cutoff]

# Scale transfer metric
def scale_transfer_ratio(results_125m, results_1b):
    rel_125m = (results_125m['optimal'] - results_125m['baseline']) / results_125m['baseline']
    rel_1b = (results_1b['optimal'] - results_1b['baseline']) / results_1b['baseline']
    return rel_1b / rel_125m
```

### 9.2 Codebase References

- Training: HuggingFace Transformers + Accelerate
- Evaluation: lm-evaluation-harness
- Data processing: datasets library + custom KenLM pipeline

## 10. Success/Failure Outcomes

### If PASS:
- Scale transfer ratio within [0.8, 1.2] (±20%)
- Both scales show positive relative improvement
- Conclusion: Optimal curation parameters transfer across scales

### If FAIL:
- Document scale-specific optima as finding
- Report optimal threshold at each scale separately
- Conclusion: Curation optimization requires scale-specific tuning

---

**Experiment Brief Version:** 1.0
**Created:** 2026-08-28
**Status:** READY FOR IMPLEMENTATION

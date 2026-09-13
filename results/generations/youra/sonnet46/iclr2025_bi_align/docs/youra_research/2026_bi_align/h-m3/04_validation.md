# H-M3 Validation Report

**Generated:** 2026-03-15 14:11:00
**Hypothesis:** H-M3 — Within-Prompt Quality Probe via Chosen/Rejected Δ-Cosine Analysis
**Gate type:** SHOULD_WORK
**Gate result:** FAIL

## Hypothesis Statement

H-M3 predicts that the next human turn (H_next) is semantically more similar to the chosen assistant response than to the rejected one:

> Δ = cos(H_next, A_chosen) − cos(H_next, A_rejected) > 0

under ≥ 2/3 operationalizations (raw, length_matched, prompt_projected), across ≥ 2/3 models, ≥ 2/3 tiers.

## Gate Evaluation

- Models passing gate: **0/3** (threshold: ≥ 2)
- Gate: **FAIL**
- Mechanism activated: **False**

### Mechanism Indicators
| Indicator | Value |
|-----------|-------|
| n_pairs_sufficient (≥1000) | True |
| delta_positive | False |
| ci_lower_positive | False |
| operationalizations_pass | False |
| fr_m3_logs_found | True |

## Model Results

### Model: minilm (all-MiniLM-L6-v2)
- Overall gate: FAIL
- ops_passing (aggregate): 0/3
- n_pairs_min: 14,426

  **helpful-base** (n=31,013)
  | Op | E[Δ] | CI_lower | CI_upper | Cohen's d | p-value | Significant |
  |----|------|----------|----------|-----------|---------|-------------|
  | raw | -0.0198 | -0.0227 | -0.0168 | -0.074 | 7.24e-39 | True |
  | length_matched | -0.0412 | -0.0439 | -0.0384 | -0.161 | 7.88e-174 | True |
  | prompt_projected | **+0.0140** | **+0.0117** | **+0.0163** | **+0.069** | 7.99e-34 | True ✓ |
  - ops_passing: 1/3 (only prompt_projected)

  **helpful-rejection-sampled** (n=35,665)
  | Op | E[Δ] | CI_lower | CI_upper | Cohen's d | p-value | Significant |
  |----|------|----------|----------|-----------|---------|-------------|
  | raw | -0.1058 | -0.1086 | -0.1032 | -0.400 | 0.0 | True |
  | length_matched | -0.1181 | -0.1209 | -0.1155 | -0.459 | 0.0 | True |
  | prompt_projected | -0.0446 | -0.0467 | -0.0424 | -0.216 | 0.0 | True |
  - ops_passing: 0/3

  **helpful-online** (n=14,426)
  | Op | E[Δ] | CI_lower | CI_upper | Cohen's d | p-value | Significant |
  |----|------|----------|----------|-----------|---------|-------------|
  | raw | -0.1670 | -0.1709 | -0.1630 | -0.716 | 0.0 | True |
  | length_matched | -0.1704 | -0.1742 | -0.1665 | -0.738 | 0.0 | True |
  | prompt_projected | -0.0972 | -0.1004 | -0.0941 | -0.524 | 0.0 | True |
  - ops_passing: 0/3

### Model: paraphrase (paraphrase-MiniLM-L6-v2)
- Overall gate: FAIL
- ops_passing (aggregate): 0/3
- n_pairs_min: 14,426

  **helpful-base** (n=31,013)
  | Op | E[Δ] | CI_lower | CI_upper | Cohen's d | p-value |
  |----|------|----------|----------|-----------|---------|
  | raw | -0.0303 | negative | negative | -0.14 | significant |
  | length_matched | -0.0456 | negative | negative | -0.19 | significant |
  | prompt_projected | -0.0069 | negative | negative | -0.03 | — |
  - ops_passing: 0/3

  **helpful-rejection-sampled** (n=35,665): ops_passing=0/3, all deltas < 0
  **helpful-online** (n=14,426): ops_passing=0/3, all deltas < 0

### Model: mpnet (all-mpnet-base-v2)
- Overall gate: FAIL
- ops_passing (aggregate): 0/3 (1 for helpful-base via prompt_projected only)
- n_pairs_min: 14,426

  **helpful-base** (n=31,013)
  - prompt_projected: E[Δ]=+0.0042 (marginally positive, insufficient for ops_passing)
  - raw: -0.0316, length_matched: -0.0540 — both negative

  **helpful-rejection-sampled** (n=35,665): ops_passing=0/3
  **helpful-online** (n=14,426): ops_passing=0/3, Cohen's d range −0.52 to −0.74

## Summary Statistics

| Model | Tier | OP1 raw | OP2 len_matched | OP3 proj | ops_pass |
|-------|------|---------|-----------------|----------|----------|
| minilm | helpful-base | -0.020 | -0.041 | +0.014 | 1/3 |
| minilm | helpful-rejection-sampled | -0.106 | -0.118 | -0.045 | 0/3 |
| minilm | helpful-online | -0.167 | -0.170 | -0.097 | 0/3 |
| paraphrase | helpful-base | -0.030 | -0.046 | -0.007 | 0/3 |
| paraphrase | helpful-rejection-sampled | -0.108 | -0.115 | -0.062 | 0/3 |
| paraphrase | helpful-online | -0.169 | -0.171 | -0.114 | 0/3 |
| mpnet | helpful-base | -0.032 | -0.054 | +0.004 | 1/3 |
| mpnet | helpful-rejection-sampled | -0.125 | -0.139 | -0.061 | 0/3 |
| mpnet | helpful-online | -0.177 | -0.181 | -0.113 | 0/3 |

## Interpretation

**Primary finding:** H_next is consistently **more** similar to A_rejected than to A_chosen (Δ < 0 in 25/27 tier×operationalization combinations). This is the **opposite** of H-M3's prediction.

**Reverse-direction finding:** The rejected response has higher cosine similarity with the next human turn than the chosen response. This is a strong, highly significant, and reproducible effect across all 3 models and all 3 tiers (Cohen's d magnitudes up to −0.74 for helpful-online).

**Possible explanation:** In the HH-RLHF dataset, the "rejected" response may be *longer* and *more contextually similar* to the human's next turn (which often reflects what the human originally wanted, even if the assistant's chosen response was better quality). The human's next turn may be semantically closer to rejected responses because both represent the human's underlying intent more directly.

**Partial exception:** OP3 (prompt_projected) passes for helpful-base with minilm (+0.014) and approaches zero with mpnet (+0.004). After projecting out the prompt direction, the reversed signal is attenuated, but not reversed.

**Data quality:** n_pairs_sufficient=True (14,426–35,665 pairs per tier), FR-M3 logs present. The result is not a data artifact — it's a genuine empirical falsification of H-M3.

## Conclusion

**SHOULD_WORK gate: FAIL**

H-M3 is **falsified**. The mechanism predicted by H-M3 (within-prompt quality probe via Δ-cosine) does not hold. The finding suggests an alternative mechanism: in HH-RLHF conversations, rejected responses have higher semantic similarity to subsequent human turns than chosen responses, likely due to length/content overlap between rejected responses and human follow-up queries.

This finding is scientifically valuable as it reveals a systematic property of the HH-RLHF dataset: the "chosen" (preferred) assistant response is semantically *less* predictive of the conversation continuation than the "rejected" response.

## Files

- Code: `h-m3/code/`
- Results: `h-m3/results/delta_results.json`
- Figures: `h-m3/results/figures/` (if generated)
- Tests: 31/31 pass (`test_delta_probe.py`, `test_statistics_m3.py`, `test_data_loader_m3.py`)

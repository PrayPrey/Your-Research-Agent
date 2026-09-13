# Product Requirements Document: H-E1
# LLM Trustworthiness Benchmark Data Availability Audit

**stepsCompleted:** [prd-step-01, prd-step-02, prd-step-03, prd-step-04, prd-step-05]
**Hypothesis:** H-E1 (EXISTENCE / LIGHT tier)
**Date:** 2026-08-20
**Author:** Anonymous
**Source:** Phase 2C — 02c_experiment_brief.md

---

## 1. Executive Summary

H-E1 is a data availability audit experiment verifying that published multi-model evaluation scores exist for ≥10 overlapping LLMs across all required trustworthiness benchmark pairs: BBQ-Disambig/Ambig (fairness), GLUE/AdvGLUE (robustness), ANLI R1/R3 (adversarial robustness), and MMLU (capability covariate). The experiment produces a 7-column model × benchmark score matrix and counts models with complete rows (N_common). N_common ≥ 10 satisfies the MUST_WORK gate enabling downstream partial Spearman ρ analyses in H-M1/H-M2/H-M3.

**Scope:** Data collection, name standardization, matrix construction, audit counting, and visualization. No model training. No held-out test set splits. Pure data engineering and statistical counting.

---

## 2. Problem Statement

Proposed downstream hypotheses (H-M1, H-M2, H-M3) require partial Spearman rank-correlation analyses controlling for MMLU capability. These analyses require N ≥ 10 models with complete scores across multiple benchmark pairs from different papers with different model coverage. The critical uncertainty is whether sufficient model overlap exists, particularly for the GLUE/AdvGLUE dimension (GLUE-X evaluates PLMs, not decoder-only LLMs — Risk R1).

**Gate Condition:** N_common ≥ 10 models with all 7 required benchmark scores.
**Failure Mode:** PIVOT — supplement from HuggingFace individual model eval pages; restrict scope.

---

## 3. Stakeholders

- **Primary:** Anonymous (researcher, author)
- **Downstream:** H-M1, H-M2, H-M3 experiments (depend on H-E1 gate passing and matrix output)

---

## 4. Functional Requirements

### FR-1: Data Source Integration

**FR-1.1 — TrustLLM Score Extraction (PRIMARY)**
- Clone `HowieHwong/TrustLLM` repository
- Parse `results/Fairness/**/*.json` for BBQ-Disambig and BBQ-Ambig accuracy (group by `context_condition` field: "disambig" / "ambig")
- Parse `results/Robustness/**/*.json` for ANLI-R1 and ANLI-R3 accuracy
- Extract per-model scores for all 16 evaluated LLMs
- Source covers: LLaMA-2 variants (7B/13B/70B base + chat), Mistral-7B/Instruct, GPT-3.5-Turbo, GPT-4, Vicuna-13B, Alpaca-13B, Falcon-7B/40B

**FR-1.2 — GLUE-X Score Extraction (SECONDARY)**
- Download `YangLinyi/GLUE-X` Table 3 data (CSV from Google Drive or paper PDF extraction)
- Extract per-model GLUE average (ID) and AdvGLUE average (OOD) scores for available PLMs
- **CRITICAL WARNING**: GLUE-X evaluates PLMs (ELECTRA, RoBERTa, T5, BERT, XLNet, BART, GPT-2), not decoder-only instruction-tuned LLMs. Model overlap with TrustLLM set expected to be minimal — must be explicitly audited.

**FR-1.3 — MMLU Score Retrieval (COVARIATE)**
- Load pre-aggregated leaderboard data: `pd.read_parquet("hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet")`
- Filter for target model names and MMLU column
- Fallback: historical MMLU 5-shot scores from paper appendices (TrustLLM arXiv 2401.05561, DecodingTrust NeurIPS 2023)

**FR-1.4 — Supplemental Sources (FALLBACK)**
- OOD_NLP (lifan-yuan/OOD_NLP): ANLI-R1, ANLI-R3 supplement
- DecodingTrust (AI-secure/DecodingTrust): AdvGLUE++, fairness scores for GPT-3.5/GPT-4

### FR-2: Model Name Standardization

**FR-2.1** — Implement `CANONICAL_MAP` dictionary mapping raw model name variants to canonical IDs:
```python
CANONICAL_MAP = {
    "llama-2-7b": "LLaMA-2-7B", "llama2-7b": "LLaMA-2-7B",
    "meta-llama/llama-2-7b-hf": "LLaMA-2-7B",
    "llama-2-7b-chat": "LLaMA-2-7B-Chat", "llama2-7b-chat-hf": "LLaMA-2-7B-Chat",
    "mistral-7b": "Mistral-7B", "mistral-7b-instruct": "Mistral-7B-Instruct",
    "gpt-3.5-turbo": "GPT-3.5-Turbo", "gpt-4": "GPT-4",
    # extend as needed during data audit
}
```
**FR-2.2** — `standardize_model_name(raw_name: str) -> str` applies CANONICAL_MAP (case-insensitive, strip whitespace); returns raw_name unchanged if no mapping found.
**FR-2.3** — Flag unresolved model names (not in CANONICAL_MAP) for manual review; log count of flagged names.

### FR-3: Matrix Construction

**FR-3.1** — Build `model × 7-benchmark` pandas DataFrame with columns:
`["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE", "ANLI-R1", "ANLI-R3", "MMLU"]`

**FR-3.2** — Source priority per cell: `TrustLLM > DecodingTrust > GLUE-X > OOD_NLP > HF-Leaderboard`

**FR-3.3** — Record source attribution per cell (for visualization FR-6.3)

**FR-3.4** — `build_matrix(score_dicts: dict) -> pd.DataFrame` implementing source priority logic:
```python
REQUIRED_COLS = ["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE", "ANLI-R1", "ANLI-R3", "MMLU"]
SOURCE_PRIORITY = ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]
```

### FR-4: H-E1 Audit

**FR-4.1** — `run_h_e1_audit(matrix: pd.DataFrame) -> dict` returns:
- `N_common`: count of models with all 7 columns non-NaN (gate metric)
- `pair_counts`: dict mapping each benchmark pair to count of models with both columns present
  - `"BBQ-Disambig/BBQ-Ambig"`: N_BBQ
  - `"GLUE/AdvGLUE"`: N_GLUE
  - `"ANLI-R1/ANLI-R3"`: N_ANLI
- `complete_matrix`: filtered DataFrame (rows with all 7 cols)
- `gate_passed`: bool (N_common ≥ 10)
- `protocol_warnings`: list of cross-source score deviation warnings

**FR-4.2** — Protocol consistency check: for any model scored by multiple sources on the same benchmark, flag if absolute difference > 5 percentage points. Report fraction of cross-source pairs within 5pp (target ≥ 0.8).

**FR-4.3** — Gate evaluation: print `N_common = {n} → PASS/FAIL`.

### FR-5: PIVOT Logic

**FR-5.1** — If N_common < 10 after primary sources:
- Supplement from HuggingFace individual model evaluation pages
- Restrict scope to benchmark pairs with N_pair ≥ 10 (per Risk R1 mitigation)
- Re-run audit; document scope restriction in results

### FR-6: Visualization

**FR-6.1 (MANDATORY) — Gate Metrics Bar Chart:**
- Bar chart: N_BBQ, N_GLUE, N_ANLI (3 bars)
- Horizontal dashed line at N=10
- Annotate each bar: "PASS (N={n})" or "FAIL (N={n})"
- Save: `docs/youra_research/h-e1/figures/gate_metrics.png`

**FR-6.2 (AUTONOMOUS) — Model Coverage Heatmap:**
- Rows = models, columns = 7 benchmarks
- Color = score value (0–1 scale); white = NaN (missing)
- Save: `docs/youra_research/h-e1/figures/coverage_heatmap.png`

**FR-6.3 (AUTONOMOUS) — Source Attribution Stacked Bar:**
- Fraction of scores per source (TrustLLM / GLUE-X / OOD_NLP / HF-Leaderboard) per benchmark column
- Save: `docs/youra_research/h-e1/figures/source_attribution.png`

**FR-6.4 (AUTONOMOUS) — Protocol Consistency Scatter:**
- For models scored in multiple sources on same benchmark: source-A vs. source-B scatter (y=x diagonal reference)
- Save: `docs/youra_research/h-e1/figures/protocol_consistency.png`

---

## 5. Non-Functional Requirements

**NFR-1: Determinism** — All outputs reproducible from same inputs; no random seeds needed (pure data processing).

**NFR-2: Auditability** — Source attribution tracked per matrix cell; audit trail in output JSON.

**NFR-3: Runtime** — Total wall-clock ≤ 3 hours (dominated by data extraction from repos and HF).

**NFR-4: Reproducibility** — Pin library versions: `scipy>=1.7.0`, `pingouin>=0.5.0`, `pandas>=1.3.0`, `numpy>=1.21.0`, `matplotlib>=3.4.0`, `huggingface_hub>=0.12.0`.

**NFR-5: Error handling** — Graceful degradation: if a source is unavailable, log warning and continue with remaining sources; report which sources were used.

---

## 6. Success Criteria

**Primary (Gate):**
- N_common ≥ 10 (MUST_WORK gate satisfied)

**Secondary:**
- N_BBQ ≥ 10 (critical for H-M1)
- N_GLUE ≥ 10 (required for H-M2)
- N_ANLI ≥ 10 (required for H-M2)
- MMLU coverage ≥ 80% of intersection models
- protocol_consistency ≥ 0.8

**PoC Pass Conditions:**
1. `run_h_e1_audit()` executes without error
2. `gate_passed = True` (N_common ≥ 10)

---

## 7. Data Specification

### 7.1 Target Model Set (Expected)
From TrustLLM (primary source — 16 decoder-only LLMs):
- LLaMA-2-7B, LLaMA-2-13B, LLaMA-2-70B (base)
- LLaMA-2-7B-Chat, LLaMA-2-13B-Chat, LLaMA-2-70B-Chat
- Mistral-7B, Mistral-7B-Instruct
- Falcon-7B, Falcon-40B
- GPT-3.5-Turbo, GPT-4
- Vicuna-13B, Alpaca-13B + 2 additional

### 7.2 Target Benchmark Columns
1. `BBQ-Disambig` — accuracy in disambiguated context (fairness ID)
2. `BBQ-Ambig` — accuracy in ambiguous context (fairness OOD)
3. `GLUE` — average GLUE score across SST-2, MNLI, QNLI, RTE, MRPC, QQP, STS-B (robustness ID)
4. `AdvGLUE` — average AdvGLUE score (robustness OOD)
5. `ANLI-R1` — Adversarial NLI Round 1 accuracy (adversarial robustness ID)
6. `ANLI-R3` — Adversarial NLI Round 3 accuracy (adversarial robustness OOD)
7. `MMLU` — 5-shot accuracy (general capability covariate)

### 7.3 Expected Performance Ranges (from literature)
- BBQ-Disambig/Ambig: 50–90% per model (TrustLLM results)
- GLUE avg: 65–89%, AdvGLUE avg: 37–75% (GLUE-X Table 3, PLM set)
- ANLI-R1: ~40–65% for decoder-only LLMs
- MMLU: ~40–80% for target model set

---

## 8. Dependencies

### 8.1 Python Packages
```
scipy>=1.7.0
pingouin>=0.5.0
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
huggingface_hub>=0.12.0
datasets>=2.0.0
requests>=2.26.0
```

### 8.2 External Repositories (manual clone/download)
- `git clone https://github.com/HowieHwong/TrustLLM` (PRIMARY — BBQ + ANLI scores)
- `git clone https://github.com/YangLinyi/GLUE-X` (SECONDARY — GLUE/AdvGLUE scores)
- GLUE-X OOD data: Google Drive link in GLUE-X README
- `git clone https://github.com/lifan-yuan/OOD_NLP` (FALLBACK — ANLI supplement)
- `git clone https://github.com/AI-secure/DecodingTrust` (FALLBACK — GPT-3.5/4 AdvGLUE++)

### 8.3 HuggingFace Datasets
- `OpenEvals/leaderboard-data` (MMLU scores via parquet)
- `open-llm-leaderboard/results` (historical MMLU fallback)

### 8.4 No model training dependencies (no GPU required)

---

## 9. Out of Scope

- Model training or fine-tuning
- Running benchmark evaluations (scores are pre-computed in source repos)
- Statistical significance testing (deferred to H-M1/H-M2/H-M3)
- New benchmark design
- Evaluation of models not already scored in source repositories

---

## 10. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R1: GLUE-X PLM/LLM model overlap near zero | HIGH | CRITICAL | Restrict to BBQ+ANLI pairs for N_common; document GLUE/AdvGLUE gap |
| R2: MMLU scores missing for some TrustLLM models | MEDIUM | MODERATE | Fallback to paper appendices (TrustLLM arXiv 2401.05561) |
| R3: Cross-source score inconsistency >5pp | LOW | LOW | Protocol consistency check flags deviations; use source priority |
| R4: HuggingFace API rate limiting | LOW | LOW | Cache downloaded parquet; retry with backoff |
| R5: TrustLLM repo structure changes | LOW | MODERATE | Pin to specific commit; use paper appendix as fallback |

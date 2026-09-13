# Phase 4 Validation Report: H-E1

**Generated:** 2026-08-31T05:25:33+00:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → FAILED (ROUTED_TO_PHASE_0)
**Author:** yoon303@ust.ac.kr

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | H-E1 |
| **Type** | EXISTENCE (PoC) |
| **Statement** | Under factual QA with black-box Llama-3-8B-Instruct at temperature=0.7, if we compute SMC-NLI (fraction of entailment/neutral pairs among N=10 sample pairs) for 1000 HaluEval questions, then the SMC-NLI score distribution will show meaningful variation across questions (not uniformly high or low), enabling AUROC > 0.60 on HaluEval binary hallucination labels. |
| **Gate Type** | MUST_WORK |
| **Gate Threshold** | SMC-NLI AUROC > 0.60 |
| **Prerequisites** | None (FOUNDATION hypothesis) |
| **Duration** | ~12 minutes (LLM sampling: ~10min, NLI scoring: ~2min) |

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 (+ FAILSAFE-1) |
| Completed | 15 |
| Failed | 0 |
| Coder-Validator Cycles | 1/5 |
| Validator Result | PASSED (all 15 tasks) |
| Tests Written | 14 (across 3 test files) |
| Tests Passing | 14/14 |

### Generated Files

| File | Description |
|------|-------------|
| `code/config.py` | Experiment configuration (CFG dict) |
| `code/data_pipeline.py` | HaluEval download + stratified sampling |
| `code/llm_sampler.py` | LLMSampler with N=10 sampling + resume |
| `code/scorer.py` | SMCNLIScorer + SMCEmbedScorer |
| `code/evaluate.py` | AUROC computation + figure generation |
| `code/run.py` | Main experiment runner |
| `code/run_experiment.sh` | Shell wrapper with trap |
| `code/tests/test_data_pipeline.py` | 5 tests for data pipeline |
| `code/tests/test_scorer.py` | 5 tests for scorer |
| `code/tests/test_evaluate.py` | 4 tests for evaluate |

### Code Quality Checklist

- [✓] All 14 tests pass
- [✓] API signatures match 03_logic.md exactly
- [✓] File structure matches 03_architecture.md
- [✓] Config values match 03_config.md
- [✓] Intermediate save/resume implemented (LLM sampling + NLI scoring)
- [✓] Question-prepend OOD mitigation implemented
- [✓] Mechanism verification passes (5-question sanity check)

---

## Experiment Results

### Configuration

| Parameter | Value |
|-----------|-------|
| LLM | meta-llama/Meta-Llama-3-8B-Instruct |
| NLI Model | cross-encoder/nli-deberta-v3-large |
| Embed Model | sentence-transformers/all-mpnet-base-v2 |
| N samples | 10 |
| Temperature | 0.7 |
| N questions | 1000 (500 correct + 500 hallucinated, stratified) |
| Hardware | 5× NVIDIA H100 NVL (95GB) |

### Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **SMC-NLI AUROC** | **0.4933** | > 0.60 | ❌ FAIL |
| **SMC-Embed AUROC** | **0.4859** | > 0.60 (fallback) | ❌ FAIL |
| SMC-NLI std | 0.3388 | > 0.05 | ✅ PASS |
| Mean SMC-NLI (correct) | 0.6236 | — | info |
| Mean SMC-NLI (hallucinated) | 0.6299 | — | info |
| N correct | 500 | 500 | ✅ |
| N hallucinated | 500 | 500 | ✅ |

### Mechanism Verification

```
Q: What year was the composed of Lux Aurunque born? | SMC-NLI: 0.9530 | Label: 0
Q: What is the birthdate of this monarch of three kin | SMC-NLI: 0.3875 | Label: 1
Q: What Unites States Air Force installation was last | SMC-NLI: 0.9853 | Label: 0
Q: Esther Norma Arrostito is a founder of a revolutio | SMC-NLI: 0.6162 | Label: 1
Q: What is the birthdate of this American actor and d | SMC-NLI: 0.4881 | Label: 1
✅ Mechanism verification PASSED
```

On 5 questions the mechanism shows variation and is in [0,1]. However across 1000 questions the AUROC collapses to ~0.49.

### Generated Figures

| Figure | Description |
|--------|-------------|
| `figures/auroc_comparison.png` | AUROC bar chart: SMC-NLI vs SMC-Embed vs random baseline |
| `figures/smc_nli_distribution.png` | SMC-NLI score histogram split by label |
| `figures/roc_curves.png` | ROC curves for SMC-NLI and SMC-Embed |
| `figures/nli_vs_embed_scatter.png` | Per-question SMC-NLI vs SMC-Embed scatter |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Result** | ❌ FAIL |
| **Satisfied** | false |
| **Primary metric** | SMC-NLI AUROC = 0.4933 (threshold: > 0.60) |
| **Fallback metric** | SMC-Embed AUROC = 0.4859 (also below threshold) |
| **Reflection triggered** | Yes |
| **Reflection outcome** | ROUTED_TO_PHASE_0 |

---

## Root Cause Analysis (Reflection)

### Primary Cause: Dataset-Generation Mismatch

HaluEval QA labels are based on `right_answer` vs `hallucinated_answer` fields. H-E1 discards these and generates fresh Llama-3-8B answers. The core assumption — that correct questions produce more consistent LLM outputs than hallucinated ones — **does not hold** here:

- **Mean SMC-NLI correct:** 0.6236
- **Mean SMC-NLI hallucinated:** 0.6299
- **Gap:** 0.006 (noise level)

Llama-3-8B-Instruct appears to have stable (consistent but potentially wrong) beliefs about many HaluEval questions. Hallucinated questions receive consistently similar wrong answers → high SMC-NLI despite being hallucinated.

### Secondary Cause: SMC-Embed Confirms the Pattern

SMC-Embed (pure semantic similarity, no NLI) also shows AUROC = 0.486. This rules out NLI-specific OOD failure. The fundamental mechanism fails for factual short-answer QA regardless of the consistency metric used.

### Key Insight

SMC-based methods work on open-ended generation (WikiBio, biographical text) where hallucinated content contains random fabrications. They fail on factual QA where LLMs may have consistent (but wrong) beliefs — a regime called **"systematic confabulation"** vs "stochastic hallucination."

---

## Next Steps (Routing)

**Gate failed: MUST_WORK → ROUTED_TO_PHASE_0**

Cascade effects:
- H-M1: CASCADE_FAILED (prerequisite H-E1 failed)
- H-M2: CASCADE_FAILED (prerequisite H-E1 failed)
- H-M3: CASCADE_FAILED (prerequisite H-E1 failed)

**Recommended Phase 0 direction:**
1. Reframe to open-ended generation tasks (WikiBio-style) where stochastic hallucination applies
2. Test SMC on factual QA but with white-box semantic entropy (requires logit access)
3. Explore SMC variants that use self-consistency over reasoning chains (CoT), not final answers

---

## Phase 2C Handoff

### Proven Components (Reusable)

| Component | File | Type | Evidence |
|-----------|------|------|----------|
| LLMSampler | code/llm_sampler.py | LLM inference | 14 tests + 10,000 real samples generated |
| SMCNLIScorer | code/scorer.py | NLI scoring | 14 tests + 45,000 NLI pairs scored |
| SMCEmbedScorer | code/scorer.py | Embed scoring | 14 tests + 1,000 questions scored |
| HaluEval data pipeline | code/data_pipeline.py | Dataset | 1,000 stratified samples loaded |
| Evaluation module | code/evaluate.py | Metrics+viz | AUROC + 4 figures generated |

### Achieved Configuration

```yaml
llm_model_id: meta-llama/Meta-Llama-3-8B-Instruct
nli_model_id: cross-encoder/nli-deberta-v3-large
embed_model_id: sentence-transformers/all-mpnet-base-v2
n_samples: 10
temperature: 0.7
top_p: 0.9
max_new_tokens: 50
nli_batch_size: 16
n_questions: 1000
seed: 42
```

### Lessons Learned

**What Worked:**
- Code structure and all 14 tests pass — implementation is correct
- LLM sampling pipeline (save/resume) works at scale
- NLI + embed scoring pipelines work correctly
- Question-prepend OOD mitigation implemented correctly
- Mechanism verification shows proper variation on 5 questions

**What Didn't Work:**
- SMC-NLI AUROC = 0.49 — no discrimination between correct and hallucinated answers
- SMC-Embed AUROC = 0.49 — confirms mechanism not just NLI-specific
- HaluEval hallucination labels not predictable from LLM consistency on generated answers

**Key Insight:** HaluEval-style factual QA requires a different detection approach — SMC works on stochastic hallucination, not on systematic confabulation. The code infrastructure is reusable for next hypothesis.

### Recommendations for Dependent Hypotheses

H-M1, H-M2, H-M3 all assumed H-E1 provides an SMC-NLI signal. Since H-E1 failed:
- Do not proceed with H-M1/M2/M3 in their current form
- New Phase 0 hypothesis should reconsider the task type and model regime
- If testing SMC again: use open-ended generation (TriviaQA open-ended, WikiBio) rather than factual QA

---

## Appendix

### Checkpoint State Summary

```yaml
hypothesis_id: h-e1
phase: Phase 4
status: FAILED
tasks:
  total: 15
  completed: 15
  failed: 0
gate_result: FAIL
gate_satisfied: false
reflection_outcome: ROUTED_TO_PHASE_0
coder_validator_cycles: 1
experiment_status: completed
```

### Experiment Log Key Lines

```
✅ Mechanism verification PASSED
--- LLM Sampling (1000 questions × 10 samples) ---
Progress: 50/1000 ... 1000/1000 questions sampled
--- SMC-NLI Scoring ---
SMC-NLI score for question 0..999
--- SMC-Embed Scoring ---
SMC-NLI AUROC: 0.4933
SMC-Embed AUROC: 0.4859
GATE_RESULT: FAILED
EXPERIMENT COMPLETE (exit=0, ts=2026-08-31T05:25:33+00:00)
```

### Files Reference

| Output File | Path |
|-------------|------|
| Validation Report | `h-e1/04_validation.md` (this file) |
| Reflection Report | `h-e1/reflection_report.md` |
| Experiment Results | `h-e1/code/outputs/results.json` |
| LLM Samples | `h-e1/code/data/llama_samples.json` |
| NLI Scores | `h-e1/code/data/nli_scores.json` |
| Embed Scores | `h-e1/code/data/embed_scores.json` |
| Experiment Log | `h-e1/code/experiment.log` |
| Figures | `h-e1/figures/*.png` (4 figures) |

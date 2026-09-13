# Experiment Design: h-e1

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** At least one screened intermediate layer (1-31) per model exhibits class-separable logit-lens statistics on the selection split: corrected AUROC >= 0.55 for at least one (layer, signal) pair among {entropy, max_token_probability, adjacent_layer_KL}, on both TriviaQA and TruthfulQA. LLaMA-2-7B is the binding existence case. Includes mandatory A2 protocol-validity anchor: v1 final-layer references reproduced within ±0.03 BEFORE the full sweep.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE — Phase 2C, UNATTENDED mode
**Prerequisites Satisfied:** Yes (none required — Level 0 root hypothesis)
**Gate Status:** MUST_WORK — not yet evaluated (Gate 1: existence + A2 anchor)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**MUST_WORK (Gate 1).** Pass: >= 1 screened (layer, signal) pair per model with selection-split corrected AUROC >= 0.55 on both datasets AND A2 anchor reproduced within ±0.03. Fail: entire hypothesis tree dies; if failure is screen-driven (A1 lens degeneracy), documented pivot to tuned-lens translators with relabeled claims.

---

## Continuation Context

First hypothesis in the verification chain (Level 0 root). No previous Phase 4 validation reports exist in this pipeline version. Relevant prior context: the v1 run (prior pipeline episode) recorded final-layer entropy AUROCs — llama2 0.5186/0.5153 (FAIL), mistral 0.5268/0.5886, llama3 0.6583/0.6161 (TriviaQA/TruthfulQA) — which serve as the A2 protocol-validity anchor, and died at 871/1000 llama2/TriviaQA samples from an infrastructure interruption (RISK-6), motivating streaming resumable scalar writes.

### Previous Hypothesis Results (if applicable)
None — h-e1 is the root hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Key terms extracted:** mechanism = per-layer logit-lens uncertainty statistics (Shannon entropy, max-token probability, adjacent-layer KL); domain = LLM hallucination detection; dataset type = short-form QA benchmarks (TriviaQA, TruthfulQA).

**Query 1: "logit lens hallucination detection"** (match_count=5)
- Result: NO RELEVANT MATCHES. Top hits were Wikipedia binocular-disparity and HuggingFace diffusers docs (aggregate similarity ≤ 0.37, all from source 8b1c7f40739544a6 — a diffusion-model corpus). No hallucination-detection or interpretability content in KB.

**Query 2: "layer-wise entropy uncertainty LLM"** (match_count=5)
- Result: NO RELEVANT MATCHES. Top hits: QLoRA paper page (hf.co/papers/2305.14314, sim 0.45), TCD sampler page, PyTorch issue #84039 — none about layer-wise uncertainty readout.

**Query 3: "TriviaQA TruthfulQA AUROC benchmark"** (match_count=5)
- Result: NO RELEVANT MATCHES. Top hits were diffusers-related gists (sim ≤ 0.50). KB contains no QA-benchmark or hallucination-evaluation material.

**Conclusion:** Archon KB (current corpus: diffusers/PyTorch/CUDA documentation) contains no past cases for this mechanism. This matches Phase 2B's finding ("Archon KB search returned no additional relevant failure cases"). The governing prior-case evidence is the project-internal v1 failure record (final-layer entropy AUROCs used as the A2 anchor). Implementation grounding therefore relies on Exa live search (Step 3) and the Phase 1 literature corpus (Entropy-Lens, Belrose et al. 2023, FEPoID).

### Archon Code Examples

**Query 1: "logit lens PyTorch hidden states"** (match_count=5)
- Result: NO RELEVANT MATCHES. Returned diffusers attention-processor snippets (scaled_dot_product_attention test, custom-diffusion weight loading, T-GATE caching); rerank scores ≤ −7.7. No logit-lens or unembedding code in KB.

**Query 2: "AUROC bootstrap confidence interval"** (match_count=5)
- Result: NO RELEVANT MATCHES. Returned torch.allclose comparison, accelerate launch script, cuBLAS signatures; rerank scores ≤ −11.2. No evaluation-statistics code in KB.

**Conclusion:** 5/5 Archon queries executed, zero domain-relevant results — KB corpus is out-of-domain for this hypothesis. All code grounding comes from Exa (Step 3) and standard libraries (`transformers` `output_hidden_states=True`, `sklearn.metrics.roc_auc_score`, `scipy/numpy` bootstrap).

### Exa GitHub Implementations

**Query 1: "logit lens per-layer entropy LLaMA hidden states unembedding implementation"**

**Repository 1**: zhenyu-02/LogitLens4LLMs
- **URL**: https://github.com/zhenyu-02/LogitLens4LLMs
- **Relevance**: Layer-wise logit-lens toolkit explicitly supporting Llama-2-7B and Llama-3.1-8B; per-layer hidden-state decoding + heatmap visualization. Community implementation, structure reusable (model_helper/llama_2_helper.py pattern).
- **Architecture**: HF transformers backend, per-layer probing during generation (`generate_with_probing`).

**Reference 2**: Alessio Devoto — "LogitLens From Scratch With Hugging Face Transformers"
- **URL**: https://alessiodevoto.github.io/LogitLens/
- **Relevance**: Exact minimal pattern needed — `output_hidden_states=True`, then per layer `logits = model.lm_head(hidden_state)`; entropy via `softmax(logits).clamp(1e-8,1)` then `-sum(p*log p)`. Matches our numerics guard (log(p+eps)).
- **Key Code**:
  ```python
  for i, hidden_state in enumerate(hidden_states):
      logits = model.lm_head(hidden_state)          # NOTE: we additionally apply model.model.norm first
      entropy = entropy_from_logits(logits)          # -sum(p*log(p)), eps-guarded
  ```

**Reference 3**: mbrenndoerfer — "Logit Lens: Decoding Transformer Hidden States Layer by Layer"
- **URL**: https://mbrenndoerfer.com/writing/logit-lens
- **Relevance**: Confirms the canonical lens path — apply the model's FINAL LayerNorm to h_l, then unembed: `logits = LN(h_l) @ W_U.T`. This is exactly the Phase 2B-specified path `model.lm_head(model.model.norm(h_l))` (RMSNorm for LLaMA/Mistral). Also documents per-position entropy with eps guard.

**Reference 4 (novelty-relevant)**: TriLens — "Per-Layer Logit-Lens Entropy for White-Box Hallucination Detection" (arXiv 2606.01033)
- **Relevance**: CLOSELY RELATED 2026 paper found during search: uses per-layer logit-lens entropy trajectories (3 pathway entropies x L layers) as features for hallucination detection — but with TRAINED probes (L2-logistic / MLP), on Qwen2.5-7B and Gemma-2-9B. Differentiation for our claim: h-e1/H-LayerLensUQ-v2 is training-free single-(layer,signal) selection with held-out split, LLaMA-2 rescue anchor, and cross-dataset transfer matrix — none evaluated by TriLens. MUST be added to the RISK-7-style novelty ledger alongside HalluShift and cited in Phase 6.

**Query 2: "tuned-lens TransformerLens logit lens decode intermediate layer"**

**Repository 1**: AlignmentResearch/tuned-lens (paper-author official — Belrose et al. 2023)
- **URL**: https://github.com/AlignmentResearch/tuned-lens
- **Relevance**: Official implementation for the A1 degeneracy FALLBACK pivot (trained per-layer affine translators). `pip install tuned-lens`; `TunedLens.from_model_and_pretrained(model)`, `LogitLens.from_model(model)`. Its `LogitLens` class also validates our raw-lens formulation (identity transform + final norm + unembed).
- **Training Config**: N/A for our use (pretrained lens artifacts downloadable per model).

**Repository 2**: TransformerLensOrg/TransformerLens
- **URL**: https://github.com/TransformerLensOrg/TransformerLens
- **Relevance**: General interpretability backend (run_with_cache) supporting Llama/Mistral. NOT selected: plain HF `output_hidden_states=True` suffices for 3 scalar signals, avoids weight-processing discrepancies (legacy HookedTransformer folds LayerNorm — would silently change lens numerics) and an extra dependency.

**Query 3: "TriviaQA TruthfulQA hallucination detection AUROC evaluation greedy generation"**

**Repository 1**: oneal2000/UniFact
- **URL**: https://github.com/oneal2000/UniFact/
- **Relevance**: End-to-end TriviaQA hallucination-detection harness: generate answer (max_new_tokens=30) → judge correctness → `sklearn` AUROC report (e.g., LNPP AUROC 0.7476 on Llama-3.1-8B-Instruct, 500 items). Confirms protocol shape: score-per-example + binary correctness label → AUROC.
- **Dataset**: TriviaQA unfiltered via nlp.cs.washington.edu tarball (we use HF `mandarjoshi/trivia_qa` rc.nocontext instead, matching v1).

**Repository 2**: sylinrl/TruthfulQA (paper-author official — Lin et al. 2022)
- **URL**: https://github.com/sylinrl/TruthfulQA
- **Relevance**: Official benchmark: 817 generation-task questions, greedy decoding (temperature 0), truth labels via GPT-judge/BLEURT/ROUGE similarity to true vs false reference answers. Our v1 labeling protocol derives from this; labels reused verbatim (A2).

**Reference 3**: HaloScope (NeurIPS 2024) + "On Early Detection of Hallucinations in Factual QA" (arXiv 2312.14183)
- **Relevance**: Establish AUROC-on-TruthfulQA/TriviaQA as the standard protocol; report supervised internal-state detectors at 0.70-0.82 AUROC — consistent with our supervised-skyline framing (FEPoID, Phase 5).

**Serena Analysis Needed**: true — not for external repos (lens code is <30 lines, clear), but the v1 archive codebase (`docs/youra_research/_archive`, cited by Phase 2B for code + 871/1000 cache reuse) must be inspected for reusable extraction code and protocol identity.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction — it tests an original hypothesis with a protocol anchored to the project's own v1 record. Priority therefore shifts: protocol-identical prior code > external references.

1. **v1 archive codebase** (project-internal, protocol-identical, Serena-verified) — highest priority
2. **Author/official external repos** — AlignmentResearch/tuned-lens (Belrose et al.) reserved for the A1 fallback pivot; sylinrl/TruthfulQA defines the label protocol our v1 code derives from
3. **Community references** — LogitLens4LLMs, Devoto/mbrenndoerfer tutorials (pattern validation only)

**Recommended Implementation Path:**
- Primary: Reuse v1 archive code (`_archive/20260805T054934_routing_recovery/h-e1/code/` — model.py, data.py, analysis.py, run_h_e1.py, constants.py) + `cache_llama2_triviaqa.csv` after protocol-identity hash verification
- Fallback: Rebuild from plain HF `transformers` (`output_hidden_states=True` + `model.lm_head(model.model.norm(h))`) per Devoto/mbrenndoerfer pattern; `pip install tuned-lens` ONLY if A1 degeneracy forces the tuned-lens pivot
- Justification: A2 anchor demands bit-level protocol identity with the v1 prompts/labels — reusing the exact code that produced the reference AUROCs minimizes anchor-reproduction risk (RISK-2) and honors the Phase 2B cache-reuse mandate (RISK-6). External libs (TransformerLens) rejected: weight-processing (LayerNorm folding) could silently change lens numerics.

### Code Analysis (Serena MCP)

**Target:** v1 archive codebase `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/code/` (latest snapshot; 658 lines total across 6 modules). Analyzed via `get_symbols_overview` + `find_symbol`.

**Code Structure (Serena Analysis)**

**Modules & key symbols:**
- `constants.py` (43 ln): `MODEL_IDS` (3 HF ids), `N_LAYERS=32`, `EXPECTED_HIDDEN_STATES=33`, `MAX_NEW_TOKENS=32`, `DEGENERACY_ENTROPY_PCT=0.01`, `DEGENERACY_AGREEMENT_MIN=0.05`, `AUROC_GATE=0.55`, `BASELINE_TOLERANCE=0.03`, `H_E1_REFERENCES` (all 6 anchor AUROCs), `SEED=42`, `TRIVIAQA_N=1000`, `TRUTHFULQA_N=817`, `SMOKE_N=10`, HF_TOKEN guard.
- `model.py` (60 ln): `load_model`, `validate_layout`, `per_layer_lens_signals` — THE core mechanism (see below), `LayoutError`.
- `data.py` (75 ln): `load_triviaqa`, `load_truthfulqa`, `format_prompt`, `label_response`, `stratified_split`, `write_test_split_locked` — the v1-verbatim prompt/label/split protocol.
- `analysis.py` (121 ln): `degeneracy_screen`, `corrected_auroc`, `build_auroc_grid`, `check_baseline_anchor`, `verify_mechanism_activated`, `evaluate_gate`, `write_cell_report`.
- `run_h_e1.py` (267 ln): `generate_and_extract`, `write_cache_row` (streaming CSV, RISK-6), `run_sweep`, `smoke_test`, `run_model`, `analyze_all`, CLI.
- `visualize.py` (92 ln) + `tests/`.

**Core mechanism (verified body, `model.py:27-59`):** `per_layer_lens_signals(model, hidden_states, answer_slice)` — asserts 33 hidden states; loops layers 1-32 skipping embedding idx 0; lens path `model.lm_head(model.model.norm(h_l)).float()` (exactly the Phase 2B-specified path, float32 statistics); per-layer Shannon entropy `-(p*logp).sum(-1).mean()`, max-prob `p.max(-1).values.mean()`, adjacent-layer KL `(p*(logp-prev_logp)).sum(-1).mean()` with `adj_kl[0]=NaN`; single `prev_logp` buffer (memory-safe); also returns `top1_match` vs final-layer argmax for the degeneracy screen. Input/output: hidden_states tuple of (1, T, d) → dict of 4 arrays shape (32,).

**Protocol functions (verified):** `degeneracy_screen` implements exactly the Phase 2B screen (entropy within 1% of ln|V| OR top-1 agreement < 5%); `corrected_auroc` returns `(max(auc, 1-auc), flipped)` with raw-direction logging (R8 diagnostic); `check_baseline_anchor` implements the ±0.03 A2 gate against `H_E1_REFERENCES`.

**Cache artifact (verified):** `results/cache_llama2_triviaqa.csv` — 1000 data rows, streaming schema `example_id, dataset, model, split, label, entropy_L1..L32, maxprob_L1..L32, adj_kl_L1..L32` (one row per example; `adj_kl_L1=nan` as specified). Older snapshot (20260805T005827) holds final-layer-only `raw_signals_*.csv` for all 6 cells (columns `question_idx,E,MP,SCV,correct`) — the v1 final-layer record behind the anchor numbers.

**Integration conclusion:** Phase 4 should REUSE this codebase nearly verbatim (copy modules into new h-e1/code/), completing the remaining 5 model x dataset sweep cells (mistral/llama3 x both datasets + llama2/truthfulqa) and reusing `cache_llama2_triviaqa.csv` after protocol-identity verification (prompt + label hashes vs `data.py` output). This directly implements the Phase 2B cache-reuse mandate (RISK-6) and removes most implementation risk.

---

## Experiment Specification

### Dataset

**CONFIRMED from Phase 2A via 02b_context.md — no re-selection.** Two standard real benchmarks (synthetic data policy: PASS — type `standard` for both).

| | Dataset 1 | Dataset 2 |
|---|---|---|
| **Name** | TriviaQA (rc.nocontext config) | TruthfulQA (generation config) |
| **Type** | standard | standard |
| **HF identifier** | `mandarjoshi/trivia_qa`, config `rc.nocontext` | `truthfulqa/truthful_qa`, config `generation` |
| **Split** | `validation[:1000]` (full first-1000 slice, v1-identical) | `validation` (all 817 questions) |
| **Fields used** | `question`, `answer.aliases`/`normalized_aliases` | `question`, `correct_answers`, `incorrect_answers` |
| **Label protocol** | greedy answer matched against normalized aliases (v1-verbatim `label_response`) | similarity to correct vs incorrect reference answers (v1-verbatim) |

**Scale:** 1,817 evaluation examples per model x 3 models = 5,451 example-model pairs; 3 signals x 32 layers each. Selection/test = stratified 50/50 per dataset (seed 42, `stratified_split` + `write_test_split_locked` from v1 `data.py`); selection split (500/408) used for h-e1's existence criterion, test split locked for h-m1. Full standard splits, no subsampling — exceeds 500+ minimum.

**Preprocessing:** v1-verbatim `format_prompt` (few-shot QA template), greedy decoding `do_sample=False`, `max_new_tokens=32`; answer-span extraction via `_first_line`/`_normalize`; teacher-forced re-forward of prompt+answer for per-layer statistics over answer tokens. No augmentation (inference-only).

**Cache reuse (RISK-6):** `_archive/20260805T054934_routing_recovery/h-e1/results/cache_llama2_triviaqa.csv` (1000 rows, full streaming schema) reusable for the llama2/TriviaQA cell AFTER protocol-identity verification (prompt + label hash check vs freshly generated rows on ≥10 examples).

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `mandarjoshi/trivia_qa` (config `rc.nocontext`) + `truthfulqa/truthful_qa` (config `generation`)
- Code:
  ```python
  from datasets import load_dataset
  triviaqa   = load_dataset("mandarjoshi/trivia_qa", "rc.nocontext", split="validation[:1000]")
  truthfulqa = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")  # 817
  ```

### Models

#### Baseline Model

**CONFIRMED from Phase 2A via 02b_context.md — no re-selection.** Three frozen decoder-only LLMs, 32 layers each, fp16, single GPU, inference-only (no training):

| Key | HF identifier | Role |
|---|---|---|
| llama2 | `meta-llama/Llama-2-7b-hf` | Binding existence case (final-layer FAIL 0.5186 to escape) |
| mistral | `mistralai/Mistral-7B-v0.1` | h-e1/v1-passing architecture (no-regression reference) |
| llama3 | `meta-llama/Meta-Llama-3-8B-Instruct` | v1-passing, only instruct model (R3 scope note) |

**Baseline SCORE within this experiment:** final-layer (L32) mean-token entropy — the anchor references (llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161 on TriviaQA/TruthfulQA) that must reproduce within ±0.03 (A2 halt gate) and that the intermediate-layer signal must beat.

**Configuration:** fp16 weights, float32 statistics; `output_hidden_states=True` (33 states = embedding + 32 layers); uniform lens path `model.lm_head(model.model.norm(h_l))` (RMSNorm + tied unembed path identical across all three families); `validate_layout` asserts 32 layers pre-run. Gated repos — requires `HF_TOKEN` env var (v1 `constants.py` guard). Weights in local HF cache (verified by v1 runs).

**Modifications for Hypothesis:** NONE to weights — the IV (readout_layer, signal_type) manipulates the READOUT only, via the `per_layer_lens_signals` extraction function.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `meta-llama/Llama-2-7b-hf`, `mistralai/Mistral-7B-v0.1`, `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  tok = AutoTokenizer.from_pretrained(model_id, token=HF_TOKEN)
  model = AutoModelForCausalLM.from_pretrained(
      model_id, torch_dtype=torch.float16, device_map="auto", token=HF_TOKEN)
  model.eval()  # frozen; hidden states via model(..., output_hidden_states=True)
  ```

#### Proposed Model

**Architecture:** Same frozen LLMs + per-layer logit-lens readout mechanism. Integration point: post-generation teacher-forced re-forward with `output_hidden_states=True`; the mechanism consumes `hidden_states[1..32]` restricted to the answer-token slice — no model modification, purely observational readout. Proposed score = best screened intermediate-layer (layer, signal) statistic; baseline score = final-layer (L32) entropy from the SAME sweep.

**Core Mechanism Implementation:**

```python
# Core Mechanism: per-layer logit-lens uncertainty signals
# Based on: v1 archive model.py:27-59 (Serena-verified) + Devoto/mbrenndoerfer lens pattern
@torch.no_grad()
def per_layer_lens_signals(model, hidden_states, answer_slice):
    """hidden_states: tuple of 33 x (1, T, d) from output_hidden_states=True.
    Returns dict of (32,) arrays: entropy, maxprob, adj_kl, top1_match."""
    assert len(hidden_states) == 33          # embedding + 32 layers (LayoutError guard)
    norm, head = model.model.norm, model.lm_head   # uniform lens path, all 3 families
    entropy, maxprob = np.zeros(32), np.zeros(32)
    adj_kl = np.full(32, np.nan)             # adj_kl[0] stays NaN (no previous layer)
    argmax_ids, prev_logp = [], None
    for l in range(32):
        h_l = hidden_states[l + 1][:, answer_slice, :]     # skip embedding idx 0
        logits = head(norm(h_l)).float()                   # (1, T_ans, V) float32 stats
        logp = logits.log_softmax(-1); p = logp.exp()
        entropy[l] = (-(p * logp).sum(-1)).mean().item()   # Shannon entropy, mean over answer tokens
        maxprob[l] = p.max(-1).values.mean().item()        # max-token probability
        argmax_ids.append(logp.argmax(-1)[0])
        if prev_logp is not None:                          # adjacent-layer KL(l || l-1)
            adj_kl[l] = (p * (logp - prev_logp)).sum(-1).mean().item()
        prev_logp = logp                                   # single buffer — no 32-layer stack (RISK-6 memory)
    final_argmax = argmax_ids[31]                          # top-1 agreement for degeneracy screen
    top1_match = np.array([(a == final_argmax).float().mean().item() for a in argmax_ids])
    return {"entropy": entropy, "maxprob": maxprob, "adj_kl": adj_kl, "top1_match": top1_match}
# Integration: called once per example after greedy generation (teacher-forced re-forward);
# rows streamed to cache_{model}_{dataset}.csv immediately (resumable, RISK-6)
```

### Training Protocol

**TRAINING-FREE.** No optimizer, no learning rate, no epochs, no loss — all models frozen, inference only (hypothesis CV; fusion fitting belongs to h-m3, not h-e1).

**Run protocol (replaces training loop):**
1. **Split lock:** stratified 50/50 selection/test per dataset, `SEED=42`; write `data_splits.json` (test locked, read by later hypotheses only).
2. **Smoke test:** `SMOKE_N=10` examples/model — assert 33 hidden states, finite signals, memory ceiling (v1 `smoke_test`).
3. **A2 anchor check FIRST:** compute final-layer entropy AUROC per cell; halt unless all within `BASELINE_TOLERANCE=0.03` of `H_E1_REFERENCES` (Phase 2B mandate: anchor BEFORE full sweep; llama2/TriviaQA cell computable from reused cache after hash verification).
4. **Full sweep:** 1,817 examples x 3 models; per example: greedy generation (`do_sample=False`, `max_new_tokens=32`) → teacher-forced re-forward → `per_layer_lens_signals` → `write_cache_row` (streaming CSV, resumable by example_id — RISK-6).
5. **Screen + readout:** degeneracy screen on selection split (`DEGENERACY_ENTROPY_PCT=0.01`, `DEGENERACY_AGREEMENT_MIN=0.05`) → corrected AUROC grid (3 signals x retained layers) → existence criterion per model.

**Inference config:** fp16 weights, float32 statistics, batch size 1 (single-example streaming, v1-identical), single GPU. **Seeds:** 1 (`SEED=42`, fixed — PoC).
**Source:** v1 archive `run_h_e1.py`/`constants.py` (Serena-verified), Phase 2B §H-E1 Verification Protocol.

### Evaluation

**Primary Metric:** corrected AUROC = `max(auc, 1-auc)` per (layer, signal) cell on the SELECTION split, computed per model per dataset via `sklearn.metrics.roc_auc_score` (raw direction logged — R8/familiarity diagnostic). NaN scores (adj_kl layer 1) pre-filtered.

**Success Criteria (Gate 1, MUST_WORK — direction-based, no statistical tests for PoC):**
1. **Existence (primary):** ≥ 1 screened (layer, signal) pair per model with selection-split corrected AUROC ≥ `AUROC_GATE=0.55` on BOTH datasets. LLaMA-2-7B is the binding case.
2. **A2 anchor (halt gate):** all 6 final-layer entropy AUROCs within ±0.03 of references (llama2 0.5186/0.5153, mistral 0.5268/0.5886, llama3 0.6583/0.6161).
3. **Screen health (secondary):** degeneracy screen retains ≥ 5 layers per model (early warning for RISK-1 → tuned-lens pivot).

**PoC direction check:** best screened intermediate-layer AUROC > final-layer entropy AUROC (same model/dataset) — `proposed_metric > baseline_metric`.

**Expected Baseline Performance (from research):**
- Final-layer entropy (v1 record): 0.5186-0.6583 across cells — llama2 at chance level (the failure to escape).
- Context from literature: supervised internal-state probes 0.70-0.85 (FEPoID, arXiv 2312.14183, HaloScope) — skyline, NOT h-e1's bar; single-pass training-free scores ~0.75 (UniFact LNPP, different model). h-e1's 0.55 existence bar is deliberately modest.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary scoring / ranking (hallucination detection via per-example scalar score + binary correctness label)
- Library: `sklearn.metrics` (AUROC) + `numpy` (percentile bootstrap; paired resampling per Exa-verified pattern)
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  auc = roc_auc_score(labels, scores)           # corrected: max(auc, 1-auc), log raw direction
  # bootstrap CI (n=1000, example-level resampling, percentile 2.5/97.5)
  idx = rng.integers(0, n, size=n)              # per replicate; np.random.default_rng(SEED)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **AUROC-vs-layer curves** (per model, per dataset, 3 signal lines + final-layer entropy baseline as horizontal reference + 0.55 gate line) — the central existence readout; llama2/TriviaQA panel is the headline.
2. **Anchor reproduction chart**: reproduced vs reference final-layer AUROCs with ±0.03 band (A2 gate visual).
3. **Degeneracy screen map**: retained/dropped layers per model (entropy-vs-ln|V| and top1-agreement criteria).
4. **Per-layer entropy heatmap** (examples x layers, correct vs incorrect groups, llama2) — mechanism intuition figure (Entropy-Lens style).

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

> Defines HOW Phase 4 verifies the mechanism actually works, not just that code runs.

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | All 3 models are 32-layer decoder-only LLMs exposing `output_hidden_states` (33 states) with `model.model.norm` + `model.lm_head` lens path | TRUE — verified by v1 runs + `validate_layout` |
| Mechanism Isolatable | Intermediate-layer readout (L1-31) vs final-layer readout (L32) computed from the SAME forward pass — toggle is column selection | TRUE |
| Baseline Measurable | Final-layer entropy AUROC computable independently and checkable against `H_E1_REFERENCES` | TRUE — A2 anchor check |

### Architecture Compatibility Check

**Required Features:** decoder-only transformer, exactly 32 hidden layers; final RMSNorm at `model.model.norm`; LM head at `model.lm_head`; HF `output_hidden_states=True` returning 33 states. All three selected checkpoints satisfy this (v1-verified). `validate_layout` asserts before sweep.

**Incompatible Architectures:** models whose norm/head attribute paths differ (e.g., GPT-2 `transformer.ln_f`/tied `wte`, SSM models, MoE with different layer counts) — Phase 4 MUST fail early via `LayoutError`, not silently mis-lens.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"raw_auc={x:.4f} flipped={bool}"` per cell + per-example cache-row writes progressing | analysis.py `corrected_auroc`, run_h_e1.py `write_cache_row` |
| Tensor Shape | 33 hidden states in; per-example signal arrays shape (32,) with `adj_kl[0]=NaN`; cache row = 5 + 96 columns | model.py `per_layer_lens_signals` |
| Metric Delta | Intermediate-layer AUROC grid varies across layers (not constant); final-layer column reproduces anchor ±0.03 | analysis.py `build_auroc_grid`, `check_baseline_anchor` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(cache_df, auroc_grid, anchor_report):
    indicators = {
        "signals_finite": cache_df.filter(regex="entropy_|maxprob_").notna().all().all()
                          and cache_df.filter(regex="adj_kl_L(?!1$)").notna().all().all(),
        "layer_variation": np.nanstd(auroc_grid["entropy"]) > 0.005,   # lens not degenerate-constant
        "anchor_reproduced": all(abs(d) <= 0.03 for d in anchor_report.values()),
        "screen_nonempty": len(anchor_report["retained_layers"]) >= 5,
    }
    return all(indicators.values()), indicators
```
(v1 `analysis.py` already contains `verify_mechanism_activated` — reuse/adapt.)

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Lens degenerate (RISK-1) | Screen retains < 5 layers on any model | FAIL → document A1, tuned-lens pivot decision |
| Anchor broken (RISK-2) | Any final-layer AUROC outside ±0.03 | HALT — reconcile labels/prompts before sweep |
| Signals not computed | NaN/constant columns in cache CSV | FAIL: mechanism not applied |
| Wrong architecture | `LayoutError` (≠33 hidden states) | FAIL early: wrong model |
| Sweep interrupted (RISK-6) | Cache rows < expected count | RESUME from streamed CSV, no recomputation |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | `verify_mechanism_activated` indicators |
| Effect Measurable | AUROC grid varies across layers; Δ(best intermediate − final) computable | corrected AUROC grid |
| Hypothesis Supported | ≥ 1 screened (layer, signal) pair per model with selection-split corrected AUROC ≥ 0.55 on both datasets | corrected AUROC (selection split), per model |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result: none usable.** 5 queries executed ("logit lens hallucination detection", "layer-wise entropy uncertainty LLM", "TriviaQA TruthfulQA AUROC benchmark", "logit lens PyTorch hidden states", "AUROC bootstrap confidence interval") — current KB corpus (source 8b1c7f40739544a6, diffusers/PyTorch/CUDA docs) is out-of-domain; all hits similarity ≤ 0.50, none used in any specification. Documented for transparency; consistent with Phase 2B's null Archon result. Governing prior case is project-internal (v1 record, Source C/D below).

### B. GitHub Implementations (Exa)

**B.1 — AlignmentResearch/tuned-lens** (paper-author official, Belrose et al. 2023)
- **URL**: https://github.com/AlignmentResearch/tuned-lens | **Query**: "tuned-lens TransformerLens logit lens decode intermediate layer"
- **Used For**: A1 degeneracy fallback path (trained affine translators, `TunedLens.from_model_and_pretrained`); its `LogitLens` class validates our raw-lens formulation (identity transform + final norm + unembed).

**B.2 — Devoto "LogitLens From Scratch" + mbrenndoerfer "Logit Lens"** (tutorials)
- **URLs**: https://alessiodevoto.github.io/LogitLens/ ; https://mbrenndoerfer.com/writing/logit-lens | **Query**: "logit lens per-layer entropy LLaMA hidden states unembedding implementation"
- **Key Code**: `logits = model.lm_head(norm(h_l))`; entropy `-sum(p*log(p+eps))` — used to cross-validate the pseudo-code's lens path and numerics guard.

**B.3 — zhenyu-02/LogitLens4LLMs** (community)
- **URL**: https://github.com/zhenyu-02/LogitLens4LLMs | **Used For**: confirms per-layer probing works on Llama-2-7B/Llama-3 class models; heatmap visualization pattern (Figure 4).

**B.4 — oneal2000/UniFact** (community benchmark harness)
- **URL**: https://github.com/oneal2000/UniFact/ | **Query**: "TriviaQA TruthfulQA hallucination detection AUROC evaluation greedy generation"
- **Used For**: protocol shape validation (score-per-example + label → AUROC; their LNPP 0.7476 on Llama-3.1-8B-Instruct/TriviaQA contextualizes expected ranges).

**B.5 — sylinrl/TruthfulQA** (paper-author official, Lin et al. 2022)
- **URL**: https://github.com/sylinrl/TruthfulQA | **Used For**: label protocol provenance (817 generation questions, greedy decoding, true/false reference answers) — v1 labeling derives from this.

**B.6 — TriLens (arXiv 2606.01033) + HaloScope (NeurIPS 2024) + arXiv 2312.14183** (papers surfaced by code search)
- **Used For**: expected-baseline context (supervised 0.70-0.85 skyline) and novelty ledger (TriLens = nearest neighbor, trained-probe variant; formal differentiation recorded in Exa findings section).

**B.7 — TransformerLensOrg/TransformerLens** — evaluated, REJECTED (LayerNorm-folding risk to lens numerics; plain HF suffices).

### C. Code Analysis (Serena)

**Analyzed Code**: v1 archive `docs/youra_research/_archive/20260805T054934_routing_recovery/h-e1/code/` (project-internal)
- **Tools Used**: `get_symbols_overview` (run_h_e1.py, model.py, analysis.py, data.py — full module map), `find_symbol` with body (`per_layer_lens_signals`, `degeneracy_screen`, `corrected_auroc`), direct read (constants.py), cache CSV inspection.
- **Key Findings**: complete protocol-identical implementation of the h-e1 mechanism (lens path, 3 signals, streaming cache, anchor check, screen); `cache_llama2_triviaqa.csv` (1000 rows) reusable; all Phase 2B constants already encoded.
- **Used For**: core mechanism pseudo-code (near-verbatim), training/run protocol, mechanism verification code, implementation priority (primary path).

### D. Previous Hypothesis Context

**Previous Context**: None — h-e1 is the first hypothesis in this verification chain (Level 0 root). The v1 record referenced throughout is a prior pipeline EPISODE (archived), not a prerequisite hypothesis: its role is protocol anchor (A2 references) + code/cache donor, formalized in Phase 2B.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection + splits | Phase 2A via 02b_context.md; Phase 2B §1.3 | 02b_context.md (JIT from 02b_verification_plan.md) |
| Dataset loading code | Exa web (HF dataset cards) | huggingface.co/datasets/mandarjoshi/trivia_qa, truthfulqa/truthful_qa |
| Prompt/label protocol | v1 archive + official benchmark | C (data.py), B.5 |
| Baseline model + loading | Phase 2A; Exa web (HF Llama-2 docs) | 02b_context.md; huggingface.co/docs/transformers/model_doc/llama2 |
| Mechanism design | Serena + tutorials | C (model.py), B.2 |
| Pseudo-code | Serena (verbatim base) | C (model.py:27-59) |
| Run protocol (training-free) | Serena + Phase 2B | C (run_h_e1.py), 02b_verification_plan.md §H-E1 |
| Degeneracy screen + anchor gate | Serena + Phase 2B A1/A2 | C (analysis.py, constants.py) |
| Evaluation metrics | Phase 2B success criteria; sklearn docs | 02b_verification_plan.md; scikit-learn.org roc_auc_score |
| Bootstrap pattern (context) | Exa web | stackoverflow.com/questions/19124239 (ogrisel percentile bootstrap) |
| Fallback (tuned lens) | Paper-author official | B.1 |
| Expected baselines | v1 record + literature | C/D, B.4, B.6 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis
- 2026-08-05: Phase 2B completed — h-e1 defined (EXISTENCE, MUST_WORK, no prerequisites) in 02b_verification_plan.md
- 2026-08-05: Hypothesis loop set h-e1 to IN_PROGRESS (Phase 2C → 3 → 4)
- 2026-08-05: Phase 2C started — 02b_context.md JIT-generated; experiment_design IN_PROGRESS (UNATTENDED)
- 2026-08-05: Phase 2C completed — 02c_experiment_brief.md (Level 1.5); experiment_design COMPLETED

### Validation Notes (Step 8, UNATTENDED)
- Quality checks: hyperparameters justified (v1 constants.py + Phase 2B §1.5) ✅; dataset justified (Phase 2A selection + anchor argument) ✅; mechanism grounded in Serena-verified v1 code (not invented) ✅; full traceability matrix present ✅; all template placeholders filled ✅.
- Documented limitation: Archon KB corpus out-of-domain (diffusers/PyTorch) — 0 domain-relevant KB sources; grounding provided instead by Serena analysis of protocol-identical v1 code + 7 Exa sources (2 paper-author official repos). "≥3 relevant MCP sources" satisfied via Exa + Serena; KB null result recorded honestly per no-fabrication rule.
- EXISTENCE PoC compliance: no statistical-test section, no ablation section, 1 seed (42), success = direction + 0.55 existence gate from Phase 2B.
- Synthetic data policy: PASS — both datasets `standard` (real benchmarks).

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*

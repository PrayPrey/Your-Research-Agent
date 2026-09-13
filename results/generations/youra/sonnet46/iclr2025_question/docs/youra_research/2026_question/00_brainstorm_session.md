---
# Phase 0 Output Metadata
# Used by subsequent phases for Pipeline Project identification
pipeline_project_title: "Anonymous Pipeline: Uncertainty Quantification in Foundation Models"
---

# Research Brainstorm Session Results

**Session Date:** 2026-03-16
**Facilitator:** Research Question Architect
**Participant:** Anonymous
---

## Executive Summary

**Initial Interest:** Uncertainty quantification and hallucination detection in foundation models — post-hoc NLI-based hallucination detection using existing response-reference/context pairs from HaluEval (no LLM generation required)

**Session Approach:** ROUTE_TO_0 (Failure Recovery Mode) — Fourth reformulation after h-e1 (H_token/LLAE failure), h-e1 PARTIAL (P(True) partial), h-e1-v2 (P(True) task-adaptive on base model), and SelfCheckGPT-NLI (gated instruct model inaccessible, base model AUROC below chance)

**Session Duration:** < 1 minute (automated extraction)

---

## Starting Context

How can we trust large language models (LLMs) when they generate text with confidence, but sometimes hallucinate or fail to recognize their own limitations? As foundation models like LLMs and multimodal systems become pervasive across high-stakes domains—from healthcare and law to autonomous systems—the need for uncertainty quantification (UQ) is more critical than ever. Uncertainty quantification provides a measure of how much confidence a model has in its predictions, allowing users to assess when to trust the outputs and when human oversight may be needed.

Source Type: Workshop CFP / Structured Input (ICLR 2025 Workshop on Uncertainty Quantification for Foundation Models)

**Retrying after previous failures (Attempt 4):** Previous hypotheses h-e1 (H_token/LLAE), h-e1 PARTIAL (P(True) generic), h-e1-v2 (P(True) task-adaptive base model), and SelfCheckGPT-NLI (h-e1 run 2/3 with base model — AUROC 0.48, below chance) all failed MUST_WORK gate. Critical blocker identified: `meta-llama/Meta-Llama-3-8B-Instruct` requires HuggingFace gated access (unavailable), forcing use of base `Llama-3.1-8B` which fundamentally breaks any generation-based method. Reformulating to **generation-free post-hoc NLI** — applying NLI directly to (response, reference/context) pairs that ALREADY EXIST in HaluEval, with zero LLM calls required.

---

## Lessons from Previous Attempts

### Attempt 1 — h-e1 Run 1: Mean Token Entropy (H_token) for Hallucination Detection

- **Hypothesis:** Mean per-token entropy (H_token) from the LLM's output distribution can detect hallucinations across factual QA, dialogue, and summarization tasks
- **Gate criteria:** AUROC ≥ 0.65 on Dialogue AND Summarization (≥1 model), DeLong p < 0.05
- **Result:** MUST_WORK gate FAILED

| Metric | Result | Threshold | Pass? |
|--------|--------|-----------|-------|
| H_token AUROC (LLaMA, Dialogue) | 0.5442 | ≥ 0.65 | FAIL |
| H_token AUROC (LLaMA, Summarization) | 0.4242 | ≥ 0.65 | FAIL |
| H_token AUROC (LLaMA, QA) | 0.6734 | ≥ 0.65 | PASS (only QA) |
| **P(True) AUROC (LLaMA, Dialogue)** | **0.8401** | N/A | **Strong signal** |
| **P(True) AUROC (LLaMA, Summarization)** | **0.7287** | N/A | **Strong signal** |

**Root cause:** Fluent hallucinations (dialogue, summarization) do NOT produce high per-token entropy. H_token is task-specific and only works for factual recall (QA).

### Attempt 1b — h-e1 LLAE: Context Attention Entropy

- **Result:** MUST_WORK gate FAILED — near-chance AUROC (0.42–0.57)
- **Root cause:** No explicit retrieved context in bare factual QA; question too short (8–15 tokens) for attention entropy to provide signal range.

### Attempt 2 — h-e1 PARTIAL: P(True) Generic Prompt

- **Result:** PARTIAL — LLaMA-3-8B-Instruct dialogue AUROC=0.766 ✅, summarization 0.547 ✗; Mistral-7B (base) ~0.58 ✗
- **Root cause:** Generic prompt template insufficient for cross-task generalization; base model cannot follow meta-evaluation prompts reliably

### Attempt 3 — h-e1-v2: P(True) Task-Adaptive Prompts (Base Model Execution Error)

- **Result:** FAIL — both tasks AUROC near-chance (~0.53)
- **Root cause:** Experiment accidentally ran on `meta-llama/Llama-3.1-8B` (base), not instruction-tuned. P(True) requires RLHF/SFT. Base models respond with arbitrary ~0.5 scores.

### Attempt 4 — SelfCheckGPT-NLI (h-e1 Run 2 and Run 3)

- **Hypothesis:** SelfCheckGPT-NLI (deberta-v3-large-mnli, N=5, temperature=0.7) achieves AUROC ≥ 0.65 on HaluEval-Dialogue and HaluEval-QA using LLaMA-3-8B-Instruct
- **Result:** MUST_WORK gate FAILED — Dialogue AUROC=0.4832 (BELOW CHANCE), QA AUROC=0.5326
- **Root cause:** Meta-Llama-3-8B-Instruct requires HuggingFace gated access — unavailable. Base model `Llama-3.1-8B` substituted. Base models produce near-identical stochastic outputs at temperature=0.7 → no semantic diversity → NLI contradiction scores have zero discriminative power.
- **Duration:** ~18.5 hours wasted on H100 GPU due to wrong model variant.

### Summary: What NOT To Do (All Exhausted Approaches)

1. **Do NOT use H_token** as primary signal for open-ended generative hallucination detection
2. **Do NOT use LLAE** in non-RAG settings — requires explicit retrieved context (≥50 tokens)
3. **Do NOT use P(True)** (verbalized confidence) — max modification attempts exhausted; requires instruction-tuned model
4. **Do NOT use SelfCheckGPT** or ANY multi-sample generation method — requires instruction-tuned model generating diverse stochastic samples; base model produces uniform outputs
5. **Do NOT assume Meta-Llama-3-8B-Instruct availability** — gated access on HuggingFace, HF_TOKEN present but unauthorized
6. **Do NOT use any method requiring LLM generation** at experiment time — every generation-based method has been blocked by the instruct model access failure

### Critical Environmental Constraint (Newly Identified)

**HARD CONSTRAINT:** Only `meta-llama/Llama-3.1-8B` (BASE, non-instruct) is locally cached and accessible.
- Mistral-7B-Instruct: Potentially accessible but unverified
- Meta-Llama-3-8B-Instruct: GATED — requires HuggingFace authorization (not available)
- Any method requiring instruction-following MUST verify model access in Phase 2C before Phase 3/4

### How This New Direction (Attempt 5) Avoids All Pitfalls

1. **Generation-free by design** — Uses only existing (context, response) pairs from HaluEval; ZERO LLM calls at inference time
2. **No instruction-following required** — NLI model (DeBERTa-v3-large-mnli) does not require instruction-tuned LLMs; it's a discriminative model, not generative
3. **No verbalized confidence** — Purely external NLI-based assessment of factual consistency between response and provided context/reference
4. **Works on HaluEval natively** — HaluEval-Dialogue has (context, response, label); HaluEval-QA has (question, answer, label); HaluEval-Summarization has (document, summary, label)
5. **Proven NLI signal** — DeBERTa-v3-large-mnli achieves >90% accuracy on NLI benchmarks; contradiction score directly measures factual inconsistency

---

## Session Plan

Auto-extracted from structured input (ROUTE_TO_0 failure recovery, Attempt 5). Research direction synthesized from:
1. ICLR 2025 Workshop CFP on Uncertainty Quantification for Foundation Models
2. Complete failure analysis from all 4 previous hypotheses (9 Serena Memory files read)
3. Critical constraint analysis: all generation-based methods blocked by instruct model gating
4. Pivot to generation-free post-hoc NLI: applies NLI directly to existing HaluEval (context, response) pairs

---

## Technique Sessions

Auto-Fill Mode (ROUTE_TO_0) — No interactive sessions. Research components extracted from workshop CFP and complete failure memory records (9 memory files: 5 failure records, 1 pivot record, 2 snapshots, 1 LLAE-specific failure).

**Key signal analysis applied:**
- **Constraint Excavation:** Identified that the real blocker is model access, not algorithm design. Every generation-based method will fail until instruct model access is resolved. Solution: eliminate LLM generation entirely.
- **Gap Hunter:** HaluEval already contains labeled (context/reference, response) pairs. The NLI contradiction score between these EXISTING pairs is a direct, model-agnostic proxy for hallucination — no generation needed. This gap has not been explored in previous pipeline runs.
- **Assumption Excavation:** Previous approaches all assumed we must query the LLM to detect its hallucinations. Post-hoc NLI removes this assumption: hallucination detection becomes a standalone NLI inference task, decoupled from the generative model entirely.
- **Feasibility Check:** DeBERTa-v3-large-mnli already loaded for h-e1/h-e1-v2 NLI scoring. HaluEval cache available from previous runs. Zero new data or model downloads required — all infrastructure already exists.

---

## Research Question Development

### Initial Question

Can post-hoc NLI-based factual consistency scoring — applying a DeBERTa-v3-large-mnli cross-encoder to EXISTING (context, response) pairs from HaluEval — detect hallucinations (AUROC ≥ 0.65) across multiple task types (dialogue, summarization, QA), without requiring any LLM generation at inference time?

### Refined Question

**Can generation-free post-hoc NLI factual consistency scoring — applying contradiction/entailment scores from DeBERTa-v3-large-mnli to existing (context, response) pairs in HaluEval — achieve AUROC ≥ 0.65 for hallucination detection on HaluEval-Dialogue, HaluEval-Summarization, and HaluEval-QA, operating purely on already-generated text without any LLM inference at experiment time?**

This reformulation:
- Uses a **fundamentally different signal type** from all 4 previous attempts: external NLI-based factual consistency, no LLM generation
- **Eliminates the instruct model access blocker entirely** — DeBERTa-v3-large-mnli is a discriminative model (no HuggingFace gating, publicly available)
- Directly maps to the workshop CFP focus on **"scalable and computationally efficient methods for UQ"** — NLI inference is orders of magnitude faster than generation-based sampling
- Uses **existing publicly available benchmarks** (HaluEval on HuggingFace, already cached from h-e1 runs)
- Targets **practical black-box deployment scenario** — works without access to any LLM at all; purely evaluative

### Detailed Sub-Questions

1. Does DeBERTa-v3-large-mnli contradiction score (premise=context, hypothesis=response) achieve AUROC ≥ 0.65 for hallucination detection on HaluEval-Dialogue (~12,988 examples) using binary hallucination labels?
2. Does the same NLI-based scoring generalize to HaluEval-Summarization (premise=document, hypothesis=summary) achieving AUROC ≥ 0.65, demonstrating task-agnostic factual consistency detection?
3. Which NLI framing achieves the highest AUROC: (a) contradiction score alone, (b) 1 - entailment score, or (c) contradiction minus entailment score (net contradiction)?
4. Does sentence-level NLI aggregation (max contradiction score over individual sentences in the response) outperform response-level NLI (treating full response as hypothesis) on HaluEval-Dialogue and HaluEval-QA?
5. How does post-hoc NLI AUROC compare to P(True) (AUROC 0.84 from h-e1 on dialogue, instruction-tuned model) — establishing a generation-free alternative that preserves most of the signal without any LLM access?

---

## Reference Papers

Not provided - will discover in Phase 1

Key papers to prioritize in Phase 1 discovery:
- Laban et al. (2022) "SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization" — NLI for summarization consistency scoring, directly relevant
- Honovich et al. (2022) "TRUE: Re-evaluating Factual Consistency Evaluation" — systematic comparison of NLI-based factual consistency methods
- Min et al. (2023) "FActScoring: Fine-grained Atomic Evaluation of Factual Precision in Long-Form Text Generation" — fact-level decomposition for NLI scoring
- Li et al. (2023) HaluEval benchmark — evaluation dataset (already cached)
- Laurer et al. (2022) "Less Annotating, More Classifying — Addressing the Data Scarcity Issue of Supervised Machine Learning with Deep Transfer Learning and BERT-NLI" — DeBERTa-v3-large-mnli model card and performance

---

## Validation Results

### So What Test

Input from established research venue (ICLR 2025 Workshop on UQ for Foundation Models) — significance pre-validated.

The reformulated question addresses multiple critical workshop themes:
- **"Scalable and computationally efficient methods for UQ in LLMs"** — Post-hoc NLI is ~100x faster than sampling-based methods (single NLI inference per example vs. N=5–10 LLM generations + NLI scoring); directly addresses efficiency concern
- **"Detect and mitigate hallucinations in generative models"** — Direct experimental validation on HaluEval (3 task types) with automated binary labels
- **"Practical and realistic benchmarks"** — Uses existing HaluEval benchmark, no new data required
- **Practical contribution:** First generation-free hallucination detector in this pipeline; deployable via API-only models where logit/attention access is unavailable and instruction-following cannot be verified
- **Workshop relevance:** Demonstrates that hallucination detection can be decoupled from the generator — a theoretically important result for scalable UQ deployment

**Why this matters now:** All previous attempts confirmed that any method requiring LLM generation is blocked by model access constraints in this environment. Post-hoc NLI establishes a practical lower bound for generation-free hallucination detection and provides a direct comparison baseline for the P(True) signal (0.84 AUROC from h-e1).

### Feasibility Check

**FEASIBLE** — Passes all mandatory pipeline constraints:

| Constraint | Status | Evidence |
|-----------|--------|---------|
| No new benchmarks required | PASS | Uses existing HaluEval (pminervini/HaluEval on HuggingFace, cached from h-e1) |
| No synthetic/generated data needed | PASS | Uses existing (context, response) pairs from HaluEval — zero LLM generation |
| No human evaluation required | PASS | Binary hallucination labels from HaluEval; AUROC fully automated |
| Immediately testable | PASS | DeBERTa-v3-large-mnli already used in h-e1-v2 NLI scoring; model available |
| Avoids ALL previous failure modes | PASS | No P(True), no H_token, no LLAE, no SelfCheckGPT, no LLM generation |
| No instruct model required | PASS | DeBERTa-v3-large-mnli is a discriminative encoder — no instruction-following |
| Uses existing infrastructure | PASS | data.py, evaluate.py from h-e1 reusable; NLI scorer already integrated |

**Computational feasibility:** HaluEval-Dialogue (~12,988 examples) × 1 NLI inference per example. At batch_size=32 on single GPU: ~30–60 minutes total. Orders of magnitude faster than any sampling-based approach. Sentence-level variant: ~3–5x longer (sentence segmentation + per-sentence NLI), still well under 4 hours.

**Risk assessment:**
- NLI may struggle on dialogue (context=conversation history, response=next utterance) — context structure is less explicit than (document, summary). Mitigated by sentence-level aggregation sub-question.
- AUROC ≥ 0.65 is the gate threshold — NLI-based summarization consistency achieves 0.70–0.80 AUROC in SummaC benchmarks, suggesting the threshold is reachable on HaluEval-Summarization. Dialogue and QA are less established but feasible starting points.

---

## Phase 1 Input Package

<phase1-input>

### research_question
Can generation-free post-hoc NLI factual consistency scoring — applying contradiction/entailment scores from DeBERTa-v3-large-mnli to existing (context, response) pairs in HaluEval — achieve AUROC ≥ 0.65 for hallucination detection on HaluEval-Dialogue, HaluEval-Summarization, and HaluEval-QA, operating purely on already-generated text without any LLM inference at experiment time?

### detailed_question
1. Does DeBERTa-v3-large-mnli contradiction score (premise=context, hypothesis=response) achieve AUROC ≥ 0.65 for hallucination detection on HaluEval-Dialogue (~12,988 examples) using binary hallucination labels?
2. Does the same NLI-based scoring generalize to HaluEval-Summarization (premise=document, hypothesis=summary) achieving AUROC ≥ 0.65, demonstrating task-agnostic factual consistency detection?
3. Which NLI framing achieves the highest AUROC: (a) contradiction score alone, (b) 1 - entailment score, or (c) contradiction minus entailment score (net contradiction)?
4. Does sentence-level NLI aggregation (max contradiction score over individual sentences in the response) outperform response-level NLI (treating full response as hypothesis) on HaluEval-Dialogue and HaluEval-QA?
5. How does post-hoc NLI AUROC compare to P(True) (AUROC 0.84 from h-e1 on dialogue, instruction-tuned model) — establishing a generation-free alternative that preserves most of the signal without any LLM access?

### reference_papers
Not provided - will discover in Phase 1

Priority papers for Phase 1 discovery:
- Laban et al. (2022) "SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization"
- Honovich et al. (2022) "TRUE: Re-evaluating Factual Consistency Evaluation"
- Min et al. (2023) "FActScoring: Fine-grained Atomic Evaluation of Factual Precision in Long-Form Text Generation"
- Li et al. (2023) HaluEval benchmark
- Laurer et al. (2022) "Less Annotating, More Classifying" — DeBERTa-v3-large-mnli

</phase1-input>

---

## Session Insights

### Key Discoveries

1. **Root cause of all failures is model access, not algorithm design** — Every generation-based method in this pipeline (H_token, P(True), SelfCheckGPT-NLI) has been broken by the inability to access `Meta-Llama-3-8B-Instruct` (HuggingFace gated access). The solution is to eliminate LLM generation from the detection pipeline entirely.
2. **Post-hoc NLI decouples detector from generator** — By applying NLI to EXISTING (context, response) pairs in HaluEval, hallucination detection becomes purely a classification task on already-generated text. This is a fundamentally different architecture than all previous approaches.
3. **DeBERTa-v3-large-mnli is already available** — The NLI model was already loaded and used in h-e1-v2. No new model downloads or access credentials required.
4. **HaluEval structure perfectly suits NLI** — HaluEval includes (knowledge/context, response, hallucination_label) for all three task types. The context field is exactly the NLI premise; the response is the hypothesis. Zero data preprocessing beyond what h-e1 already implemented.
5. **Speed advantage is publishable** — Post-hoc NLI at ~30–60 minutes vs. SelfCheckGPT at ~18.5 hours is a 20x speedup — a concrete efficiency contribution aligned with the workshop's "scalable UQ" theme.
6. **P(True) 0.84 AUROC as comparison target** — The strongest signal observed in this pipeline (instruction-tuned LLaMA-3 dialogue) provides a natural comparison baseline for what is achievable with LLM access. Post-hoc NLI aims to approach this without any LLM.

### Techniques Used

Auto-Fill Mode (ROUTE_TO_0 structured input extraction, Attempt 5):
- **Constraint Excavation (enhanced):** Identified that model access gating is the fundamental blocker for all generation-based approaches; pivoted to generation-free architecture
- **Gap Hunter:** Identified that HaluEval's existing (context, response) structure enables generation-free NLI detection — an approach not yet attempted in this pipeline
- **Assumption Excavation:** Challenged the assumption that hallucination detection requires querying the generative model; post-hoc NLI tests responses already in the dataset
- **Feasibility constraint filtering:** All 4 mandatory pipeline constraints satisfied; all environmental constraints (model access, GPU availability) also satisfied

### Areas for Further Exploration

Topics from workshop CFP not captured in primary research question (for future hypotheses if needed):
- Multimodal uncertainty quantification (vision-language models — CLIP, LLaVA)
- Uncertainty communication to end users (UX/HCI perspective)
- Conformal prediction for LLMs (theoretical coverage guarantees)
- Calibration under distribution shift (OOD uncertainty estimation)
- RAG-specific hallucination detection (LLAE revisited with explicit retrieved context)
- Mistral-7B-Instruct-v0.1 accessibility as an alternative instruct model (open access, not gated)
- Sentence-level vs. utterance-level decomposition strategies for long-form responses

---

## Next Steps

Proceed to Phase 1 - Targeted Research: `/phase1-targeted`

**Phase 1 focus areas:**
1. SummaC and TRUE papers — NLI-based factual consistency scoring on summarization, directly applicable to HaluEval-Summarization
2. DeBERTa-v3-large-mnli model details — optimal NLI framing (contradiction vs. entailment vs. net), batch inference performance
3. State-of-the-art AUROC on HaluEval for NLI-based detection methods (any existing baselines)
4. Sentence-level NLI aggregation strategies (max, mean, weighted) — prior work on optimal aggregation for consistency scoring
5. Recent (2024-2025) generation-free hallucination detection methods — confirm this direction is publishable and novel relative to latest work

**Implementation notes to carry forward:**
- DeBERTa-v3-large-mnli: `cross-encoder/nli-deberta-v3-large` on HuggingFace; `torch.inference_mode()` for batched scoring
- HaluEval cache available at `_archive/*/h-e1/cache/` — copy forward to avoid re-download
- NLI batch size: 32–64 per GPU (DeBERTa is ~400MB, much lighter than LLaMA-3-8B)
- **CRITICAL: Do NOT load any LLM for this experiment** — pure NLI pipeline, single GPU sufficient
- CUDA_VISIBLE_DEVICES must be set at shell level before conda run
- HaluEval-Dialogue context field: full conversation history; treat as multi-sentence premise
- For sentence-level NLI: use `nltk.sent_tokenize()` or simple period-split to segment response

---

*Session facilitated by YouRA Research Question Architect*
*Phase: 0 - Research Brainstorm (ROUTE_TO_0 Failure Recovery — Attempt 5)*
*Ready for: Phase 1 - Targeted Research*

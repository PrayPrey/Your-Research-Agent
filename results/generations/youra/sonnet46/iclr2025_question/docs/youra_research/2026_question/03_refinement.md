# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-16T14:30:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No AUROC Baseline for Generation-Free Post-Hoc NLI on Multi-Task HaluEval
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Convergence**: All 6 criteria met

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15 (15 exchanges across 8 orchestrator iterations)

**Convergence Reason**: Specific claim, mechanism, 3 testable predictions, novelty (extrospective NLI paradigm + structural ceiling analysis), technical feasibility, major objections addressed via pre-registered experimental design.

### Key Insights
1. **Extrospective NLI paradigm**: Applying NLI to existing (context, response) pairs decouples hallucination detection from the generating model — orthogonal to SelfCheckGPT's self-consistency signal
2. **Structural ceiling analysis**: AUROC_max = p + 0.5*(1-p) where p = proportion of context-contradictory positives — turns the hallucination-type limitation into a publishable characterization finding
3. **Self-diagnostic framing ablation**: Framing comparison simultaneously optimizes detection AND characterizes HaluEval's hallucination type distribution
4. **Net-contradiction framing**: P(contradiction) - P(entailment) captures both explicit contradictions AND unsupported-but-non-entailed content — extends coverage beyond raw contradiction

### Breakthrough Moments
- **Exchange 9** (Dr. Nova): Reframes structural ceiling (AUROC_max = p + 0.5*(1-p)) from limitation to novel contribution
- **Exchange 13** (Dr. Ally): Formalizes SelfCheckGPT comparison as theoretical reference (instruct model inaccessible) — fair scoping of contribution
- **Exchange 15** (Dr. Nova): Establishes orthogonality of extrospective (context-grounding) vs. introspective (self-consistency) NLI — clarifies paradigm claim

---

## Final Hypothesis

### Title
Extrospective NLI as Grounding-Conditioned Hallucination Detection on HaluEval

### Hypothesis ID
H-ExtrospectiveNLI-v1

### Core Claim
Under the post-hoc, generation-free evaluation setting (no LLM generation at experiment time), if `cross-encoder/nli-deberta-v3-large` is applied to HaluEval (context, response) pairs with **(a) net-contradiction framing** (P(contradiction) − P(entailment)), **(b) sentence-level max aggregation** for dialogue and QA, **(c) full-document response-level** for summarization, and **(d) last-3-turn windowed premise** for dialogue, then **AUROC ≥ 0.65 will be achieved on HaluEval-Summarization and HaluEval-QA** (primary), and **AUROC ≥ 0.60 on HaluEval-Dialogue** (exploratory), because DeBERTa's MNLI training encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response without any LLM generation.

### Null Hypothesis
No NLI framing achieves AUROC ≥ 0.65 on both HaluEval-Summarization and HaluEval-QA simultaneously when applied zero-shot without task-specific training.

### Mechanism
1. DeBERTa-v3-large-mnli (MNLI-trained) encodes graded support sensitivity via NLI pretraining
2. Hallucinated responses receive lower entailment and/or higher contradiction scores than their grounding context
3. Net-contradiction framing (P(contra) − P(entail)) captures both explicit contradictions and unsupported-but-non-entailed content
4. Sentence-level max aggregation isolates the most contradictory sentence, preventing dilution

---

## Predictions

### P1 (Primary)
DeBERTa NLI with net-contradiction framing achieves **AUROC ≥ 0.65 on both Summarization AND QA** simultaneously.
- **Success**: AUROC ≥ 0.65, DeLong test p < 0.05 vs. baseline
- **Failure**: AUROC < 0.65 on either task across all framing variants

### P2 (Secondary)
Net-contradiction outperforms raw contradiction by **ΔAUROC ≥ 0.02** on ≥ 2/3 tasks.
- **Success**: Consistent delta, bootstrap 95% CI excluding 0
- **Failure**: All three framings within 0.01 AUROC of each other

### P3 (Structural Ceiling)
Empirical AUROC ≥ **70% of structural ceiling** (p + 0.5×(1-p)) on Summarization and QA.
- **Success**: Model near-optimal for its in-scope hallucination types
- **Failure**: AUROC < 50% of ceiling → fundamental model underperformance

---

## Novelty
- **First systematic AUROC measurement** for zero-shot DeBERTa NLI on HaluEval multi-task (Dialogue, QA, Summarization)
- **Extrospective NLI paradigm**: external grounding vs. self-consistency — architecturally distinct from SelfCheckGPT
- **Structural ceiling analysis**: first hallucination-type characterization study on HaluEval
- **Self-diagnostic framing ablation**: results characterize HaluEval annotation structure AND optimize detection

---

## Experimental Design

### Dataset
- **HaluEval-Dialogue** (~12,988 examples), **HaluEval-QA** (10,000), **HaluEval-Summarization** (10,000)
- Source: `pminervini/HaluEval` on HuggingFace; already cached from prior pipeline runs

### Model
- **`cross-encoder/nli-deberta-v3-large`** (frozen, zero-shot, already cached)
- Inference: `batch_size=32`, `torch.inference_mode()`, `max_length=512`

### Ablation Design
- **3 NLI framings**: contradiction, 1−entailment, net-contradiction
- **3 Aggregation granularities**: response-level, sentence-level max, sentence-level mean
- **3 Premise windows** (dialogue): full-context, last-3-turns, last-user-only
- Pre-registered primary configuration: `(net-contradiction, sentence-level max, last-3-turns)`

### Mandatory Analyses
1. **Label audit**: 200 positive samples per task; type as (A) contradiction, (B) unsupported-non-contradicted, (C) ambiguous; compute structural ceiling
2. **Controlled truncation study**: crop summarization documents to 128/256/384/512 tokens; measure AUROC sensitivity
3. **Effect size**: Cohen's d for score distributions (positive vs. negative) per task

### Baselines
- SelfCheckGPT-NLI: AUROC 0.48/0.53 (prior runs, base model) — as executed lower bound
- P(True): AUROC 0.84/0.73 — theoretical reference (instruct model inaccessible)
- NER-overlap: trivial lexical baseline

---

## Limitations
- 512-token context limit: DeBERTa truncates long summarization documents and full dialogue histories
- HaluEval labels "unverifiable information" — not strictly synonymous with NLI contradiction
- Zero-shot generalization from MNLI short sentences to longer HaluEval texts
- Sentence tokenization quality on dialogue turns may affect aggregation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Addressed via pre-registered design (label audit + truncation study) |
| **Phase 2B Ready** | Yes |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*ROUTE_TO_0 Attempt 5 — Generation-free NLI post-hoc detection*

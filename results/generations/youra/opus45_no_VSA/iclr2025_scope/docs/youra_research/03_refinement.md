# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-09T16:12:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1-flan-evaluation
- **Gap Title**: FLAN-Specific Adapter Routing Evaluation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS with thresholds, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed

### Key Insights
- Alignment is plausible because prefix embeddings and LoRA deltas share base-model representational ancestry
- Testing WHETHER alignment exists is more novel than building a router that assumes it
- Two-tier contribution: practical (zero-shot routing) + theoretical (geometric alignment)

### Breakthrough Moments
- Exchange 7: Reframing from IPCR (method) to IAGA (structural theory about geometric alignment)
- Exchange 13: Diagnostic ladder with H-E0 prefix separability prerequisite
- Exchange 14-15: Oracle margin and representation drift analysis for rigorous validation

---

## Final Hypothesis

### Title
Instruction-Prefix-Conditioned Adapter Routing (IPCR)

### Hypothesis ID
H-IPCR-v1

### Core Claim
Under the FLAN instruction-tuning task taxonomy, if instruction prefixes are embedded using a frozen sentence encoder (MiniLM) and mapped via learned linear projection to adapter weights, then zero-shot adapter routing achieves ≥90% of oracle task-specific LoRA performance on held-out tasks, because instruction semantics and adapter specializations share geometric structure inherited from the base model's learned task representations.

### Mechanism
1. Frozen sentence encoder (MiniLM, ~22M params) embeds instruction prefix
2. Learned linear projection (~0.1M params) maps embedding to adapter weight space
3. Soft routing computes weighted combination of LoRA deltas from shared adapter bank
4. Combined adapter produces task-appropriate model behavior

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | Yes | Linear probe achieves ≥70% oracle selection accuracy | Top-1 ≥70% OR Top-3 ≥85% |
| P2 | Yes | Zero-shot routing achieves ≥90% of oracle | Mean ≥90% across task families |
| P3 | No | Routing robust to paraphrase and masking | Cosine ≥0.90; <10% drop under masking |

---

## Novelty

**Key Innovation**: First work to test whether instruction-adapter alignment exists intrinsically, rather than assuming it must be learned.

**Differentiation from Prior Work**:
- vs. LORAUTER: LORAUTER requires 5+ validation examples; IPCR works on first example
- vs. LoRAHub: LoRAHub requires gradient-free optimization; IPCR needs no optimization
- vs. MoELoRA: MoELoRA trains routing jointly; IPCR tests intrinsic alignment

---

## Experimental Design

**Dataset**: FLAN instruction collection (62 task categories)

**Models**: Llama-2-7B-chat, Mistral-7B-Instruct

**Baselines**:
- Random adapter selection
- Uniform soft combination
- LORAUTER-zero (forced zero-validation mode)
- Oracle task-specific LoRA

**Adapter Bank**: k=8-10 adapters, rank r=16

---

## Diagnostic Ladder

| ID | Name | Threshold | Purpose |
|----|------|-----------|---------|
| H-E0 | Prefix Separability | macro-F1 ≥0.75 | Prerequisite: task families separable in prefix space |
| H-E1 | Linear Probe | Top-1 ≥70% OR Top-3 ≥85% | MUST_WORK: prefix predicts adapter |
| H-E2 | Intrinsic Dimension | ≥8 dimensions | Rich geometry vs. low-rank clustering |
| H-M1 | Zero-Shot Routing | ≥90% of oracle | MUST_WORK: core hypothesis |
| H-M2 | Paraphrase Robustness | cosine ≥0.90 | Lexical brittleness check |
| H-M3 | Compositional Routing | ≥80% of two-stage oracle | Linear composability test |
| H-C1 | Entropy Calibration | ECE ≤0.15 | Routing confidence validity |

---

## Limitations

- Evaluation limited to FLAN task taxonomy; generalization to arbitrary instructions untested
- Requires FLAN-style instruction formatting for reliable routing
- Compositional routing (multi-step tasks) is secondary analysis, not core hypothesis
- If paraphrase invariance requires contrastive training, "zero-shot" claim is weakened

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Oracle margin pre-registration needed; contrastive ablation required |

---

## Previous Failure Context

This hypothesis avoids prior failures:
- h-m1: Position-based routing failed; IPCR routes at parameter level
- h-e1: CUDA OOM on attention matrices; IPCR uses lightweight encoder
- All prior attempts sought privileged information in hidden states; IPCR tests representational alignment

---

*Phase: 2A - Hypothesis Generation via Research Dialogue*
*Ready for: Phase 2B - Hypothesis Verification Protocol Design*

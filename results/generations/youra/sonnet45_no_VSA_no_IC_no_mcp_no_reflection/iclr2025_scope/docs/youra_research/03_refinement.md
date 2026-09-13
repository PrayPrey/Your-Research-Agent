# Hypothesis Refinement Summary

**Hypothesis ID:** H-LoRA-SSM-Transfer-v1  
**Generated:** 2026-08-28  
**Workflow:** Phase 2A-Dialogue (Self-Contained Tikitaka Loop, Independent-Controller Ablation)  
**Exchanges:** 7  
**Convergence:** All personas agreed on feasibility-constrained hypothesis

---

## Core Hypothesis

**Statement:**  
Parameter-efficient fine-tuning via low-rank adaptation (LoRA) of input/output projection layers transfers effectively from transformer architectures to state-space models (Mamba), achieving comparable downstream task performance while maintaining frozen recurrent components.

**Under-If-Then-Because:**  
Under classification task fine-tuning scenarios using pretrained language models, if low-rank adaptation (LoRA rank-8) is applied only to input/output projection layers of state-space models (Mamba-130M) while freezing recurrent components (A,B,C matrices), then downstream task performance will match transformer LoRA performance (≥95% of GPT-2-117M LoRA accuracy), because adaptation surfaces in neural architectures can be architecture-independent despite different underlying mechanisms (attention vs state-space recurrence).

---

## Key Predictions

1. **P1 (Performance Parity):** Mamba LoRA achieves ≥95% of GPT-2 LoRA average accuracy on GLUE tasks (MNLI, QQP, SST-2). Failure threshold: <85%.

2. **P2 (Parameter Efficiency):** Mamba LoRA parameter count is within 10% of GPT-2 LoRA parameter count (ratio 0.9-1.1). Failure threshold: <0.7 or >1.3.

3. **P3 (Statistical Significance):** Both architectures outperform zero-shot baselines with p<0.05 (paired t-test across 3 seeds).

---

## Experimental Design

**Models:**
- GPT-2-117M (transformer, HuggingFace)
- Mamba-130M (state-space model, original paper checkpoint)

**Adaptation Methods:**
- Full fine-tuning (upper bound)
- LoRA rank-8 on input/output projections only (frozen attention/recurrence)
- Zero-shot (lower bound)

**Tasks:** GLUE subset (MNLI, QQP, SST-2)  
**Metric:** Average accuracy  
**Replication:** 3 random seeds (42, 1337, 2024)  
**Hyperparameters:** LR 3e-4, batch 32, AdamW, early stopping

---

## Novelty

**What's New:**
- First systematic PEFT comparison between transformer and state-space model architectures
- Empirical validation that input/output projections serve as universal adaptation surfaces
- Demonstration that recurrent components can remain frozen during adaptation

**Contribution:** Challenges implicit assumption that PEFT is transformer-specific. Opens sub-quadratic models to existing PEFT tooling. Either outcome (success or failure) advances understanding of architecture-agnostic adaptation.

---

## Persona Verdicts

| Persona | Verdict | Key Concern |
|---------|---------|-------------|
| 🔭 Dr. Nova (Novelty) | MODERATE | Scoped down from meta-learning vision, but still addresses literature gap |
| 🔬 Prof. Vera (Falsifiability) | STRONG | Clear success/failure thresholds, statistical significance, 3 seeds |
| 🎯 Dr. Sage (Significance) | MODERATE | Genuine contribution, but narrow scope (1 SSM, classification only) |
| ⚙️ Prof. Pax (Feasibility) | STRONG | Existing checkpoints/benchmarks, theoretically sound (frozen recurrence) |
| 🛡️ Dr. Ally (Synthesis) | STRONG | Successfully synthesized all concerns into coherent hypothesis |
| 🔍 Prof. Rex (Critique) | MODERATE | Checkpoint verification needed, acknowledged limitations |

**Overall:** 4/6 STRONG, 2/6 MODERATE, 0/6 WEAK

---

## Scope & Limitations

**Included:**
- Classification tasks (GLUE: MNLI, QQP, SST-2)
- 100-130M parameter models
- LoRA adaptation on input/output projections

**Excluded:**
- Generation tasks (summarization, QA)
- Models >1B parameters
- Other sub-quadratic architectures (linear attention, RWKV)
- Adaptation of recurrent components

**Known Limitations:**
- Results may not generalize to generation tasks
- Single state-space model tested (Mamba)
- GLUE benchmarks are transformer-centric

---

## Prerequisites for Phase 2B

1. ✅ Verify Mamba-130M pretrained checkpoint availability
2. ✅ Confirm GLUE benchmark access
3. ✅ Validate compute resources (single GPU, ~24 GPU-hours)
4. ✅ Ensure LoRA library compatibility with Mamba

---

## Next Phase: Phase 2B - Research Planning

**Expected Inputs to Phase 2B:**
- ✅ `03_refinement.yaml` (this file's YAML counterpart)
- ✅ `02_synthesis.yaml` (discussion synthesis details)
- ✅ `01_round_table/final_opinions.yaml` (per-persona assessments)

**Phase 2B Tasks:**
- Create detailed experiment roadmap
- Design validation protocols
- Plan implementation milestones
- Establish success criteria for Phase 3

---

**Status:** READY FOR PHASE 2B (pending Mamba checkpoint verification)

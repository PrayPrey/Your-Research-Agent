# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-08
**Main Hypothesis:** SparsityLoRA: Activation Sparsity as a Pre-Training Structural Prior for LoRA Rank Allocation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under LLaMA-3-8B in inference mode, if layer-wise MLP activation sparsity (fraction |a| < 0.01 via forward hooks on 512 Alpaca samples) is measured across all 32 MLP gate layers, then sparsity CV > 0.3 and Kendall's tau_calibration ≥ 0.6 (Alpaca vs. WikiText-103), because pre-training drives MLP layers toward differentiated sparse activation attractors (Lazy Neuron Phenomenon).

### Type
EXISTENCE

### Rationale
This is the foundational existence check — without significant inter-layer sparsity variation and cross-distribution stability, the sparsity signal cannot serve as a discriminating rank allocation prior. H-E1 directly validates PROVE_NEW claim #1 and provides the input ranking for all H-M hypotheses.

---

## Verification Protocol

### Conceptual Test
1. Register register_forward_hook on all 32 MLP gate_proj output activations; process 512 Alpaca samples (batch=8, torch.no_grad()).
2. For each layer and epsilon, compute mean sparsity fraction; compute CV across 32 layers.
3. Repeat for WikiText-103 (512 samples) and both input lengths (128, 512 tokens); compute Kendall's tau for all pairs.
4. Sweep epsilon {0.001, 0.01, 0.05, 0.1}; check if CV > 0.3 and tau ≥ 0.6 hold across epsilon values.
5. Report: sparsity profile plot (32 layers), CV value, all pairwise Kendall's tau values, sensitivity table.

### Success Criteria
- Primary: CV > 0.3 AND Kendall's tau_calibration ≥ 0.6 at epsilon=0.01
- Secondary: Ranking stable across input lengths (tau_length ≥ 0.6); CV > 0.3 for at least 3 of 4 epsilon values

### Variables
- **Independent Variable:** Calibration dataset (Alpaca vs. WikiText-103), input length (128 vs. 512 tokens), epsilon threshold {0.001, 0.01, 0.05, 0.1}
- **Dependent Variable:** CV of per-layer sparsity across 32 layers; Kendall's tau (Alpaca vs. WikiText-103 ranking); Kendall's tau (128-token vs. 512-token ranking)
- **Controlled Variables:** LLaMA-3-8B model state (inference only, no gradient), same tokenizer and batch size

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Alpaca (primary) + WikiText-103 (stability check)
- **Type:** standard
- **Source:** HuggingFace datasets — tatsu-lab/alpaca (primary), wikitext (wikitext-103-raw-v1)
- **Path:** `load_dataset("tatsu-lab/alpaca")` / `load_dataset("wikitext", "wikitext-103-raw-v1")`
- **Hypothesis Fit:** Alpaca 512 samples calibrate pre-training activation patterns; WikiText-103 is a divergent distribution to test stability of the sparsity ranking signal

### Selected Model
- **Name:** LLaMA-3-8B
- **Type:** Decoder-only LLM with SiLU MLP gating
- **Source:** meta-llama/Meta-Llama-3-8B (HuggingFace)
- **Hypothesis Fit:** SiLU activations produce near-zero (soft) sparsity; 32 MLP layers provide sufficient per-layer diversity to measure CV; commonly used in PEFT literature

---

## Baseline & Comparison Targets

### Baseline Methods
H-E1 is an EXISTENCE hypothesis — no baseline model comparison. The baseline is the null hypothesis: "All layers have equal sparsity (CV ≤ 0.3)" and "Sparsity ranking is random across distributions (tau < 0.6)".

### Baseline Performance
N/A — This is a measurement/characterization experiment, not a performance comparison.

### Gap Analysis
If CV > 0.3 (significant inter-layer variation) AND tau ≥ 0.6 (cross-distribution stability), this establishes that the sparsity signal is a valid discriminating prior — confirming PROVE_NEW claim #1.

---

## Dependencies and Gate Conditions

### Prerequisites
None — H-E1 is the foundational hypothesis with no dependencies.

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:**
- IF CV ≤ 0.3: PIVOT — sparsity not discriminating; explore gradient norm or activation magnitude as alternative signal
- IF tau < 0.6: EXPLORE — use task-specific calibration (GLUE validation sets); narrow hypothesis scope

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** ~1-2 hours (measurement only, no training)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the FOUNDATION for all other hypotheses:
- H-M1 (prerequisites: H-E1): Tests stability across diverse calibration datasets
- H-M2 (prerequisites: H-E1): Tests robustness of sparsity to epsilon threshold choice
- H-M3 (prerequisites: H-M1, H-M2): Tests correlation between sparsity and LoRA rank sensitivity
- H-M4 (prerequisites: H-M3): Tests final allocation performance hypothesis

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Baseline comparison targets (N/A for EXISTENCE type)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-e1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*

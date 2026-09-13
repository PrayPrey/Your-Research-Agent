# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-31
**Main Hypothesis:** Corpus Quality as a Predictor of Generalization Balance
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under a controlled matched-training-scale comparison (~300B tokens), if corpus curation quality differs between Pythia-6.9B (The Pile) and OLMo-7B (Dolma), then OLMo-7B will show a higher MMLU/HellaSwag performance ratio AND a higher ARC-Challenge/Easy delta than Pythia-6.9B, because the quality difference produces measurably different generalization balance.

### Type
EXISTENCE (PoC)

### Rationale
This hypothesis validates the core phenomenon — that the curation quality difference between The Pile and Dolma actually manifests as a measurable difference in OOD/ID generalization balance at matched token count. Without demonstrating this existence, all mechanistic hypotheses are moot. This is the foundational gate: if the signal doesn't exist, the mechanism hypotheses cannot be tested.

---

## Verification Protocol

### Conceptual Test
1. Identify and download Pythia-6.9B intermediate checkpoint corresponding to ~300B training tokens from HuggingFace Hub; verify token count from checkpoint metadata.
2. Identify and download OLMo-7B intermediate checkpoint corresponding to ~300B training tokens; verify token count from checkpoint metadata.
3. Run lm-evaluation-harness on both checkpoints: MMLU (5-shot), HellaSwag (0-shot), ARC-Easy (25-shot), ARC-Challenge (25-shot).
4. Compute MMLU/HellaSwag ratio and ARC-Challenge/Easy delta for both models; perform bootstrap statistical comparison (3 random prompt subsamples).
5. Evaluate: if OLMo ratio > Pythia ratio by > 0.02 absolute, Cohen's d > 0.2, p < 0.05 → existence confirmed.

### Success Criteria
- Primary: OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B ratio by > 0.02 absolute, Cohen's d > 0.2, p < 0.05
- Secondary: OLMo-7B ARC delta > Pythia-6.9B ARC delta (directional, p < 0.10)

### Variables (if applicable)
- **Independent Variable:** Corpus curation level (The Pile vs. Dolma)
- **Dependent Variable:** MMLU/HellaSwag performance ratio (primary); ARC-Challenge/Easy delta (secondary)
- **Controlled Variables:** Training token count (~300B via intermediate checkpoints), evaluation framework (lm-evaluation-harness), benchmark test set versions

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** The Pile (EleutherAI) + Dolma (AllenAI) — corpora for evaluation context; benchmark datasets: MMLU, HellaSwag, ARC-Easy, ARC-Challenge
- **Type:** standard
- **Source:** EleutherAI/pile and allenai/dolma on HuggingFace Datasets; benchmarks via lm-evaluation-harness
- **Path:** auto (lm-evaluation-harness handles benchmark download)
- **Hypothesis Fit:** The Pile represents low-curation data (825GB, minimal filtering); Dolma represents high-curation data (3T tokens, multi-stage quality filtering). Models trained on these corpora are the subjects; benchmark evaluation datasets (MMLU, HellaSwag, ARC) are the measurement instruments.

### Selected Model
- **Name:** Pythia-6.9B (intermediate checkpoint ~300B tokens) + OLMo-7B (intermediate checkpoint ~300B tokens)
- **Type:** decoder-only transformer
- **Source:** EleutherAI/pythia-6.9b and allenai/OLMo-7B-hf on HuggingFace Hub
- **Hypothesis Fit:** Matched parameter count (~6.9B vs ~7B); both release intermediate checkpoints enabling matched-token-count comparison; both natively supported by lm-evaluation-harness; represent low-curation (Pythia/The Pile) vs. high-curation (OLMo/Dolma) training regimes.

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Pythia-6.9B (The Pile, full training) | MMLU ~25-30%, HellaSwag ~60-65%, ARC-Challenge ~30-35% | The Pile (825GB, minimal curation) |
| OLMo-7B (Dolma, full training) | MMLU ~28-35%, HellaSwag ~67-72%, ARC-Challenge ~38-44% | Dolma (3T tokens, multi-stage quality filtering) |
| RefinedWeb + Falcon-7B | HellaSwag ~75%, LAMBADA ~76% | RefinedWeb (aggressive web filtering) |

### Baseline Performance
Pythia-6.9B at ~300B tokens (intermediate): expected MMLU ~22-28%, HellaSwag ~58-63%.
OLMo-7B at ~300B tokens (intermediate): expected MMLU ~26-32%, HellaSwag ~64-70%.

### Gap Analysis
Expected MMLU/HellaSwag ratio: Pythia ~0.38-0.45, OLMo ~0.40-0.48. Hypothesis predicts OLMo ratio > Pythia ratio by > 0.02 absolute.

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the foundational hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** All mechanistic hypotheses (H-M1 through H-M4) are blocked. Pivot to examine whether token count matching is valid or architecture confound accounts for any observed difference.

**Phase Assignment:** Phase 2C → 3 → 4 (first)

**Estimated Duration:** ~2-4 hours (lm-evaluation-harness evaluation on 2 model checkpoints)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundational gate for the entire verification chain. H-M1, H-M2, H-M3, H-M4 all depend on H-E1 demonstrating that the performance difference exists at matched token count. This is a MUST_WORK gate — failure terminates the verification workflow.

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

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*

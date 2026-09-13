# H-M2 Per-Hypothesis Context
# Generated: JIT by Phase 2C step-01 from 02b_verification_plan.md
# Date: 2026-03-14

---

## Hypothesis Information

**ID:** H-M2
**Type:** MECHANISM (Causal chain Step 2)
**Title:** Corpus Conditional Entropy Shifts Internalize into Model Logit Margins (Log-Linear)

**Statement:**
Under controlled training conditions (Pythia-1B, 100B tokens, LR 2e-5, batch 256, cross-entropy loss), if models are trained on corpora with different H(occupation|demographic) values (produced by different curation configurations), then the models' logit margins on demographic probe prompts will be positively correlated with the corpus-level H(occupation|demographic) differences (Spearman ρ > 0, p < 0.01), with a log-linear functional relationship, because cross-entropy training minimizes KL divergence from the empirical conditional distribution, driving the model to approximate corpus-level conditional probability structures in its weight space.

**Rationale:** This is the second causal link: from corpus-level demographic structure to model weight internalization. The shuffled-demographic negative control (corpus with identical entropy but destroyed conditional associations) is the critical design element distinguishing conditional structure internalization from mere distributional shift.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Independent Variable (IV)
- Corpus-level H(occupation|demographic) — continuous scalar from 6 curation configurations (C1–C5 fastText + C6 DoReMi + 1 shuffled-demographic control + 1 unfiltered baseline)
- Operationalized as: ~10-12 Pythia-1B training runs on curated corpus subsets

### Dependent Variable (DV)
- Model logit margin on demographic probe prompts: mean logit(demographic-congruent occupation completion) − logit(demographic-incongruent occupation completion)
- Spearman ρ between corpus H(occupation|demographic) and model logit margins across configurations
- Log-linear functional relationship: logit_margin ~ log(H_entropy_shift)

### Controlled Variables
- Architecture: Pythia-1B (decoder-only Transformer, EleutherAI)
- Learning rate: 2e-5 (AdamW)
- Batch size: 256
- Token budget: 100B tokens per run
- Loss: cross-entropy
- Evaluation prompts: 50+ standardized templates per demographic axis

### Dataset
- Name: mlfoundations/dclm-baseline-1.0 (DCLM-POOL / Dolma v1.7 compatible)
- Type: standard (real, established dataset)
- Source: HuggingFace Datasets (streaming)
- Path: streaming — use corpus subsets C1–C6 already computed in h-e1/code/
- Hypothesis Fit: Same corpus configurations as H-E1/H-M1; controlled comparison across filtering intensities with known H(occupation|demographic) values

### Model
- Name: Pythia-1B (primary); Pythia-160M (secondary slope-consistency check)
- Type: decoder-only Transformer
- Source: EleutherAI/pythia-1b on HuggingFace
- Hypothesis Fit: Designed for controlled pretraining experiments; consistent architecture across scales; 10-12 training runs tractable at 1B scale

---

## Gate Conditions

**Gate Type:** SHOULD_WORK
**Pass Condition:** Spearman ρ > 0 with p < 0.01 between corpus H(occupation|demographic) and model logit margins across configurations
**Fail Action:** EXPLORE — examine per-demographic-axis correlations; test with Pythia-7B if scale is the issue

**Prerequisites:** H-M1 (COMPLETED, PASS)
- H-M1 result: Spearman ρ=1.0 (p=1.4e-24); Mean log-odds C1=0.697→C5=2.976 (perfect monotonic)
- H-M1 established: curation path creates systematic, measurable conditional log-odds differences in corpus

**Secondary Success Criteria:**
- Shuffled-demographic control produces logit margins ≤0.01 difference vs. matched-capability standard model

---

## Verification Protocol (from Phase 2B)

1. Train ~10-12 Pythia-1B models: 5 fastText filtering percentiles (C1–C5) + 2 DoReMi variants + 1 shuffled-demographic negative control + 1 unfiltered baseline (use single GPU; CUDA_VISIBLE_DEVICES)
2. Compute demographic logit margins: mean logit(demographic-congruent occupation completion) − logit(demographic-incongruent) on standardized probe templates (50+ templates per demographic axis: gender, race, occupation)
3. Compute Spearman ρ between corpus H(occupation|demographic) values and corresponding model logit margins across all 10-12 runs
4. Test shuffled-demographic control: verify that shuffled-corpus model produces logit margins not statistically distinguishable from unfiltered baseline despite matching surface-level entropy
5. Fit log-linear model (logit_margin ~ log(H_entropy_shift)) and assess R² and coefficient significance

---

## Dependencies and Context

**Prerequisite:** H-M1 (COMPLETED, PASS)
**Downstream:** H-M3 (requires H-M2 to complete)
**Pipeline Position:** Phase 2 Model Training (Weeks 3-7)
**Critical Path:** H-E1 → H-M1 → **H-M2** → H-M3

**Risk:** R1 (Insufficient Scale — A1 violation at Pythia-1B scale) — High Severity
**Mitigation:** Run Pythia-160M slope-consistency check; if directional at 160M, more confident at 1B

**H-M1 Context (for continuation):**
- Log-odds matrix: 1800 (demographic, occupation) pairs across 6 configurations
- Mean log-odds: C1=0.697, C2=0.916, C3=1.191, C4=1.734, C5=2.976, C6=0.643
- H(occupation|demographic): C0=3.2662, C1=3.2702, C2=3.2528, C3=3.2275, C4=3.1106, C5=2.5374, C6=3.2209 bits
- Corpus subsets C1–C6 available in h-e1/code/ and h-m1/code/

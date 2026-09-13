# H-M1 Per-Hypothesis Context
# Generated: JIT by Phase 2C step-01 from 02b_verification_plan.md
# Date: 2026-03-14

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM (Causal chain Step 1)
**Title:** Curation Path Alters Corpus-Level Conditional Demographic Association Density

**Statement:**
Under controlled corpus conditions, if different curation paths (fastText filtering at 10%-90% percentile cutoffs, DoReMi domain reweighting) are applied to Dolma/DCLM-POOL, then the conditional log-odds of demographic-occupation co-occurrences will vary systematically across configurations in a manner correlated with filtering intensity (Spearman ρ ≠ 0 across configurations), because fastText assigns differential quality scores correlated with demographic register, and DoReMi shifts domain proportions with known demographic distribution differences across domains.

**Rationale:** This is the first causal link in the PCFH chain: from curation operation to corpus-level demographic structure. Establishing this link validates that the proposed mechanism (quality filtering as implicit demographic selector) operates at the corpus level before testing its propagation to model weights.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Independent Variable (IV)
- Data curation path: fastText quality filtering at percentile cutoffs (10%, 30%, 50%, 70%, 90%) and DoReMi domain reweighting
- Operationalized as 6 curation configurations: C1–C5 (fastText 10%-90%) + C6 (DoReMi)

### Dependent Variable (DV)
- Conditional log-odds of demographic-occupation co-occurrences per curation configuration
- H(occupation|demographic) — conditional entropy as scalar summary statistic
- Monotonic trend with filtering intensity (Spearman ρ across configurations)

### Controlled Variables
- Base corpus: DCLM-POOL (mlfoundations/dclm-baseline-1.0, streaming)
- Demographic token set: Fixed gender/ethnicity name list (same as H-E1)
- Occupation lexicon: Fixed occupations list (same as H-E1)
- Corpus subsets: Reuse filtered subsets from H-E1

### Dataset
- Name: mlfoundations/dclm-baseline-1.0 (DCLM-POOL / Dolma v1.7 compatible)
- Type: standard (real, established dataset)
- Source: HuggingFace Datasets (streaming)
- Path: streaming (no cache needed — reuse H-E1 corpus subsets)
- Hypothesis Fit: Same corpus used in H-E1; reuse filtered subsets directly to compute log-odds statistics

### Model
- Name: Statistical analysis only (no neural model for H-M1)
- Type: corpus statistics / log-odds computation
- Source: scipy.stats (Spearman), statsmodels (regression)
- Hypothesis Fit: H-M1 measures corpus-level statistics (conditional log-odds), not neural model outputs

---

## Gate Conditions

**Gate Type:** MUST_WORK
**Pass Condition:** Monotonic trend in H(occupation|demographic) with filtering intensity (Spearman ρ ≠ 0, p < 0.05 across 6 configurations)
**Fail Action:** PIVOT — explore per-domain or per-subcorpus effects

**Prerequisites:** H-E1 (COMPLETED, gate PASS)
- H-E1 result: Relative entropy change C1→C5 = -22.41% (threshold 5.0%); Spearman ρ=-1.0 (p=1.4e-24)
- H-E1 established: fastText filtering creates measurable, monotonic H(occupation|demographic) shift

**Secondary Success Criteria:**
- Statistically distinguishable H(occupation|demographic) between fastText and DoReMi paths at matched MMLU targets

---

## Verification Protocol (from Phase 2B)

1. Using corpus subsets from H-E1, compute log-odds of demographic-occupation co-occurrences for each curation configuration (C1–C6)
2. Test Spearman correlation between fastText percentile cutoff (treating DoReMi as reference point) and log-odds values across configurations
3. Fit a regression of log-odds on filtering intensity (percentile cutoff as ordinal) to characterize functional form
4. Compare H(occupation|demographic) across DoReMi configurations vs. fastText configurations at matched MMLU targets
5. Assess whether fastText R² diagnostic result (from H-E1) meaningfully changes causal interpretation of the filtering mechanism

---

## Dependencies and Context

**Prerequisite:** H-E1 (COMPLETED)
**Downstream:** H-M2 (requires H-M1 to complete)
**Pipeline Position:** Phase 1 Foundation (Corpus Audit), concurrent with H-E1 corpus work
**Critical Path:** H-E1 → H-M1 [Gates 1+2] → Training → H-M2 → H-M3

**Risk:** R4 (Insufficient demographic diversity in corpus) — Medium Severity
**Mitigation:** H-E1 gate already passed (≥5% relative entropy difference confirmed at -22.41%)

**H-E1 Context (for controlled comparison):**
- Corpus subsets C1–C6 already computed and available in h-e1/code/
- H(occupation|demographic) values: C0=3.2662, C1=3.2702, C2=3.2528, C3=3.2275, C4=3.1106, C5=2.5374, C6=3.2209 bits
- Spearman ρ=-1.0 (p=1.4e-24) on H(occupation|demographic)
- H-M1 extends this by computing **log-odds** (more granular mechanism) to characterize the functional relationship

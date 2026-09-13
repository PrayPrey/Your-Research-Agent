# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan (JIT)
**Date:** 2026-05-04
**Main Hypothesis:** Cross-Corpus Contamination Atlas: Systematic N-gram Overlap Mapping Across Major NLP Benchmarks and Training Corpora
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under pinned versions, if 13-gram containment rates are computed for the full 59×3 matrix (59 benchmark sub-tasks × 3 corpora: The Pile v1, C4 en.noclean, RedPajama-v1), then contamination rates will vary significantly across the three corpora (Kruskal-Wallis p < 0.05) because The Pile, C4, and RedPajama have structurally different source compositions (academic vs. web-filtered vs. curated-multi-source) that produce systematically different n-gram overlap with domain-specific benchmark content.

### Type
MECHANISM

### Rationale
This is the core mechanism hypothesis — it tests whether corpus-level structural differences (documented in corpus papers) translate into measurable contamination signature differences. Success establishes the corpus-as-variable framework central to the paper. The Pile (academic+diverse web), C4 (quality-filtered CommonCrawl), and RedPajama (curated multi-source) have well-documented structural differences; the hypothesis predicts these differences manifest as measurable 13-gram overlap variance.

---

## Verification Protocol

### Conceptual Test
1. Extend H-E1 pipeline to build MinHash LSH indices for C4 en.noclean and RedPajama-v1 via HF streaming
2. Query all three indices for each of the 59 benchmark sub-tasks; construct 59×3 contamination matrix
3. Run Kruskal-Wallis H-test on per-corpus mean contamination rates across all sub-tasks
4. Verify at least one corpus pair shows mean contamination rate difference > 2 percentage points
5. Sanity-check Pile × MMLU rates against WIMBD published values (consistency check)

### Success Criteria
- Primary: Kruskal-Wallis p < 0.05 for corpus variance
- Secondary: At least one corpus pair shows mean contamination > 2 pp difference; Pile × MMLU rates consistent with WIMBD

### Variables
- **Independent Variable:** Corpus identity (3 levels: The Pile v1 / C4 en.noclean / RedPajama-v1)
- **Dependent Variable:** Mean 13-gram containment rate per corpus (averaged over all 59 sub-tasks)
- **Controlled Variables:** Same 59 sub-tasks (MMLU + HellaSwag + BBH), pinned dataset versions, identical MinHash parameters (n=13, 128+ hash functions), question+choices text format

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MMLU + HellaSwag + BIG-Bench Hard (59 sub-tasks) × The Pile v1 + C4 en.noclean + RedPajama-v1
- **Type:** standard
- **Source:** Hugging Face datasets (all public)
- **Path:** cais/mmlu (v1.0.0), Rowan/hellaswag, lukaemon/bbh (benchmarks); EleutherAI/pile, allenai/c4 (en.noclean), togethercomputer/RedPajama-Data-1T (corpora)
- **Hypothesis Fit:** The 59×3 cross-product directly instantiates the contamination matrix; corpora represent the three structural classes (academic, web-filtered, curated-multi-source)

### Selected Model
- **Name:** N/A — allenai/wimbd + custom Python (MinHash LSH)
- **Type:** text-analysis pipeline (no model inference)
- **Source:** allenai/wimbd (GitHub); custom Python tokenize → shingle → MinHash
- **Hypothesis Fit:** WIMBD provides validated 13-gram contamination tooling; extension to C4/RedPajama via same MinHash LSH approach ensures methodological consistency

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| WIMBD 13-gram containment (Pile × MMLU) | ~1-10% for some MMLU sub-tasks | The Pile v1 × MMLU |
| GPT-4 TR Jaccard contamination analysis | Near-zero for most benchmarks | Undisclosed training data × select benchmarks |
| Dodge et al. (2021) C4 contamination documentation | Partial overlap documentation | C4 × various NLP datasets |

### Baseline Performance
- WIMBD (Elazar et al., 2023): provides single-corpus (Pile) × single-benchmark contamination rates; no cross-corpus comparison
- No existing unified cross-corpus × cross-benchmark 59×3 matrix exists in the literature

### Gap Analysis
Gap: No unified 3-corpus × 3-benchmark contamination rate matrix exists. This is the novel contribution H-M1 directly instantiates. The hypothesis tests whether corpus variance is statistically significant — if H-M1 PASSES, it confirms the matrix is scientifically meaningful (not all corpora contaminate equally).

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (VALIDATED — Kruskal-Wallis H=590.82, p=2.73e-89; MUST_WORK gate satisfied)

### Gate Information

**Gate Type:** MUST_WORK
- Failure action: EXPLORE — document null corpus effect; continue to H-M2, H-M3 as independent tests; narrow thesis to sub-task variance only

**Consequence if Fails:** Document null corpus effect; narrow thesis from "corpus-specific contamination signatures" to "sub-task contamination varies but is not corpus-specific"; H-M2/H-M3 can still proceed independently

**Phase Assignment:** Phase 2 — Core Mechanisms (Weeks 3-4)

**Estimated Duration:** 2 weeks (C4 + RedPajama streaming index build ~12-24 hrs each; Kruskal-Wallis analysis <1 hr)

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** H-E1 (VALIDATED) — H-E1 confirmed significant sub-task contamination variance in The Pile; H-M1 extends to corpus-level variance across all 3 corpora
- **Enables:** H-M2 (domain-predictable patterns requires the full 59×3 matrix from H-M1), H-M3 (Jaccard consistency requires same matrix cells)
- **Key reuse:** H-E1 already built The Pile MinHash index; H-M1 extends with C4 and RedPajama indices only

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation (H-E1 VALIDATED)
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Baseline comparison targets (WIMBD Pile×MMLU rates for sanity check)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5) for the 59×3 matrix construction
4. Output: h-m1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
